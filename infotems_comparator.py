"""
AI Document Analyzer - InfoTems Comparison
===========================================

Compares extracted document data with existing InfoTems records.
Handles primary contact, family members, and history records.
All changes require approval before applying.

IMPORTANT: This module depends EXCLUSIVELY on the InfoTems Hybrid Client at:
C:\\Users\\Josh\\Dropbox\\Law Office of Joshua E. Bardavid\\Administrative Docs\\Scripts\\New Official Infotems API\\infotems_hybrid_client.py

ALL InfoTems API operations MUST go through that client.
NO direct API calls are permitted in this module.

Author: Law Office of Joshua E. Bardavid
Version: 2.1.0
Date: January 2026

DESIGN PRINCIPLES:
- Everything requires approval - no automatic updates
- Family members are full contacts - can be searched, linked, or created
- History is structured data - address, employment, education as reviewable records
- All data is editable in the approval window before applying
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

from config import (
    QUESTIONNAIRE_TYPES, DOCUMENT_TYPES, CONTACT_FIELDS, BIOGRAPHIC_FIELDS,
    FAMILY_RELATIONSHIPS, HISTORY_TYPES,
    INFOTEMS_USERNAME, INFOTEMS_PASSWORD, INFOTEMS_API_KEY,
    METADATA_PATH, get_all_document_types
)


# ============================================================================
# INFOTEMS CLIENT IMPORT - SINGLE SOURCE OF TRUTH
# ============================================================================
# 
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CRITICAL: The InfoTems Hybrid Client is the ONLY authorized way to      ║
# ║  interact with InfoTems. NO direct API calls are permitted here.         ║
# ║                                                                          ║
# ║  Hub Location: ..\New Official Infotems API\infotems_hybrid_client.py   ║
# ║                                                                          ║
# ║  If you need new InfoTems functionality:                                 ║
# ║  1. Add the method to infotems_hybrid_client.py FIRST                   ║
# ║  2. Then import and use it here                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

INFOTEMS_HUB_PATH = r"..\New Official Infotems API\infotems_hybrid_client.py"

try:
    from infotems_hybrid_client import InfotemsHybridClient
    INFOTEMS_AVAILABLE = True
except ImportError as e:
    INFOTEMS_AVAILABLE = False
    _IMPORT_ERROR = str(e)

def _validate_infotems_client():
    """Validate that the InfoTems hub client is available."""
    if not INFOTEMS_AVAILABLE:
        raise ImportError(
            f"\n"
            f"{'='*70}\n"
            f"INFOTEMS HUB CLIENT NOT FOUND\n"
            f"{'='*70}\n"
            f"\n"
            f"This project requires the InfoTems Hybrid Client (the hub).\n"
            f"\n"
            f"Expected location:\n"
            f"  {INFOTEMS_HUB_PATH}\n"
            f"\n"
            f"Full path:\n"
            f"  C:\\Users\\Josh\\Dropbox\\Law Office of Joshua E. Bardavid\\\n"
            f"  Administrative Docs\\Scripts\\New Official Infotems API\\\n"
            f"  infotems_hybrid_client.py\n"
            f"\n"
            f"The hub client is the SINGLE SOURCE OF TRUTH for all InfoTems\n"
            f"API operations. Ensure it exists and is in the Python path.\n"
            f"\n"
            f"Import error: {_IMPORT_ERROR if '_IMPORT_ERROR' in dir() else 'Unknown'}\n"
            f"{'='*70}\n"
        )


# ============================================================================
# ENUMS
# ============================================================================

class ChangeType(Enum):
    """Type of change to a field."""
    NEW = 'new'
    MODIFIED = 'modified'
    UNCHANGED = 'unchanged'
    REMOVED = 'removed'


class FamilyMemberAction(Enum):
    """Action to take for a family member."""
    SKIP = 'skip'                    # Do nothing
    LINK_EXISTING = 'link_existing'  # Link to existing contact (TODO: requires API method)
    CREATE_NEW = 'create_new'        # Create new contact
    UPDATE_LINKED = 'update_linked'  # Update already-linked contact


class HistoryAction(Enum):
    """Action for history records."""
    SAVE_AS_RECORDS = 'save_as_records'  # Save as proper InfoTems records (Address, Employment, Education, Travel)
    SAVE_TO_NOTES = 'save_to_notes'       # Save as formatted case note (fallback)
    SKIP = 'skip'                          # Don't save


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FieldChange:
    """Represents a proposed change to a single field."""
    field_key: str
    field_label: str
    current_value: Optional[str]
    new_value: Optional[str]
    confidence: float
    change_type: ChangeType
    infotems_field: Optional[str] = None
    is_biographic: bool = False
    approved: bool = True
    edited_value: Optional[str] = None  # User-edited value
    
    @property
    def has_change(self) -> bool:
        """Check if this represents an actual change."""
        return self.change_type in (ChangeType.NEW, ChangeType.MODIFIED)
    
    @property
    def final_value(self) -> Optional[str]:
        """Get the value to use (edited or new)."""
        return self.edited_value if self.edited_value is not None else self.new_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['change_type'] = self.change_type.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldChange':
        """Create from dictionary."""
        data = data.copy()
        data['change_type'] = ChangeType(data['change_type'])
        return cls(**data)


@dataclass
class FamilyMember:
    """Represents a family member extracted from questionnaire."""
    relationship: str  # spouse, child, father, mother, sibling, prior_spouse
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    
    # Matching
    matched_contact_id: Optional[int] = None
    matched_contact_name: Optional[str] = None
    match_confidence: float = 0.0
    match_method: Optional[str] = None  # 'a_number', 'name_dob', 'name_only'
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Action
    action: FamilyMemberAction = FamilyMemberAction.SKIP
    
    # Changes to apply (if linking/updating)
    field_changes: List[FieldChange] = field(default_factory=list)
    
    # Editing
    edited_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def display_name(self) -> str:
        """Get display name for this family member."""
        data = self.edited_data if self.edited_data else self.extracted_data
        first = data.get('first_name', '')
        last = data.get('last_name', '')
        if first and last:
            return f"{first} {last}"
        return f"Unknown {self.relationship}"
    
    @property
    def final_data(self) -> Dict[str, Any]:
        """Get final data (edited or extracted)."""
        result = self.extracted_data.copy()
        result.update(self.edited_data)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'relationship': self.relationship,
            'extracted_data': self.extracted_data,
            'confidence': self.confidence,
            'matched_contact_id': self.matched_contact_id,
            'matched_contact_name': self.matched_contact_name,
            'match_confidence': self.match_confidence,
            'match_method': self.match_method,
            'action': self.action.value,
            'field_changes': [c.to_dict() for c in self.field_changes],
            'edited_data': self.edited_data,
        }


@dataclass
class HistoryRecord:
    """A single history record (address, employment, education, etc.)."""
    record_type: str  # 'address', 'employment', 'education', 'travel', etc.
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    is_current: bool = False
    edited_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def final_data(self) -> Dict[str, Any]:
        """Get final data (edited or extracted)."""
        result = self.data.copy()
        result.update(self.edited_data)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'record_type': self.record_type,
            'data': self.data,
            'confidence': self.confidence,
            'is_current': self.is_current,
            'edited_data': self.edited_data,
        }


@dataclass
class HistorySet:
    """Collection of history records of one type."""
    history_type: str  # 'address', 'employment', 'education', 'travel', etc.
    records: List[HistoryRecord] = field(default_factory=list)
    action: HistoryAction = HistoryAction.SAVE_AS_RECORDS  # Default to proper records
    
    # History types that support proper InfoTems records
    RECORD_SUPPORTED_TYPES = {'address', 'employment', 'education', 'travel'}
    
    @property
    def supports_records(self) -> bool:
        """Check if this history type supports proper InfoTems records."""
        return self.history_type in self.RECORD_SUPPORTED_TYPES
    
    @property
    def display_name(self) -> str:
        """Get display name for this history type."""
        return HISTORY_TYPES.get(self.history_type, {}).get('display_name', self.history_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'history_type': self.history_type,
            'records': [r.to_dict() for r in self.records],
            'action': self.action.value,
        }


@dataclass 
class ChangeSet:
    """Complete set of proposed changes from document extraction."""
    # Primary contact
    contact_id: Optional[int] = None
    contact_name: str = ""
    a_number: str = ""
    biographic_id: Optional[int] = None
    
    # Document info
    document_type: str = ""
    questionnaire_type: Optional[str] = None
    source_file: str = ""
    extraction_confidence: float = 0.0
    
    # Primary contact changes
    changes: List[FieldChange] = field(default_factory=list)
    
    # Family members
    family_members: List[FamilyMember] = field(default_factory=list)
    
    # History records
    history: Dict[str, HistorySet] = field(default_factory=dict)
    
    # Other extracted info (not mapped to fields)
    other_info: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def contact_changes(self) -> List[FieldChange]:
        """Get approved changes for Contact record."""
        return [c for c in self.changes 
                if not c.is_biographic and c.has_change and c.approved]
    
    @property
    def biographic_changes(self) -> List[FieldChange]:
        """Get approved changes for ContactBiographic record."""
        return [c for c in self.changes 
                if c.is_biographic and c.has_change and c.approved]
    
    @property
    def total_primary_changes(self) -> int:
        """Count of primary contact changes."""
        return sum(1 for c in self.changes if c.has_change)
    
    @property
    def family_member_count(self) -> int:
        """Count of family members with actions."""
        return sum(1 for fm in self.family_members 
                   if fm.action != FamilyMemberAction.SKIP)
    
    @property
    def history_count(self) -> int:
        """Count of history records to save."""
        count = 0
        for hs in self.history.values():
            if hs.action in (HistoryAction.SAVE_AS_RECORDS, HistoryAction.SAVE_TO_NOTES):
                count += len(hs.records)
        return count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            'contact_id': self.contact_id,
            'contact_name': self.contact_name,
            'a_number': self.a_number,
            'biographic_id': self.biographic_id,
            'document_type': self.document_type,
            'questionnaire_type': self.questionnaire_type,
            'source_file': self.source_file,
            'extraction_confidence': self.extraction_confidence,
            'changes': [c.to_dict() for c in self.changes],
            'family_members': [fm.to_dict() for fm in self.family_members],
            'history': {k: v.to_dict() for k, v in self.history.items()},
            'other_info': self.other_info,
            'errors': self.errors,
            'created_at': self.created_at,
        }


# ============================================================================
# MAIN COMPARATOR CLASS
# ============================================================================

class InfotemsComparator:
    """
    Compares extracted document data with InfoTems records.
    Handles primary contact, family members, and history.
    
    IMPORTANT: All InfoTems operations use the InfotemsHybridClient.
    See: ..\\New Official Infotems API\\infotems_hybrid_client.py
    
    Available InfoTems client methods used by this class:
    
    CONTACTS:
    - get_contact(contact_id) -> Contact record
    - search_contacts(first_name, last_name, ...) -> Search results
    - search_by_anumber(a_number) -> Contact by A-number
    - create_contact(first_name, last_name, **fields) -> New contact ID
    - update_contact(contact_id, fields) -> Updated contact
    
    BIOGRAPHIC:
    - get_contact_biography(contact_id) -> Biographic data
    - create_contact_biographic(contact_id, **fields) -> New biographic
    - update_contact_biographic(biographic_id, fields) -> Updated biographic
    
    RELATIONSHIPS (Family Members):
    - add_contact_relative(primary_id, related_id, relationship, **kwargs) -> Link relatives
    - search_contact_relationships(primary_contact_id) -> Get linked relatives
    - update_contact_relationship(relationship_id, fields) -> Update relationship
    - delete_contact_relationship(relationship_id) -> Remove link
    
    HISTORY RECORDS (v3.0 - Proper Structured Records):
    - create_address(contact_id, line1, city, state, ...) -> Address record
    - create_employment(contact_id, occupation, start_date, ...) -> Employment record
    - create_education(contact_id, institution_name, ...) -> Education record
    - create_travel_history(contact_id, arrival_date, ...) -> Travel record
    
    NOTES (Fallback for unsupported history types):
    - create_note(subject, body, contact_id, category, ...) -> New note ID
    """
    
    def __init__(self, verbose: bool = True):
        """Initialize comparator with InfoTems connection."""
        self.verbose = verbose
        self.client = None
        self.metadata = {}
        
        if not INFOTEMS_AVAILABLE:
            raise ImportError(
                "InfoTems client not available. Ensure infotems_hybrid_client.py "
                "is in the Python path. Location: "
                "..\\New Official Infotems API\\infotems_hybrid_client.py"
            )
        
        # Initialize the ONLY authorized InfoTems client
        self.client = InfotemsHybridClient(
            api_key=INFOTEMS_API_KEY,
            username=INFOTEMS_USERNAME,
            password=INFOTEMS_PASSWORD,
            debug=False
        )
        
        self._load_metadata()
    
    def log(self, message: str):
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(f"  {message}")
    
    def _load_metadata(self):
        """Load unified client metadata for quick lookups."""
        if METADATA_PATH and Path(METADATA_PATH).exists():
            try:
                with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                self.log(f"📂 Loaded metadata: {len(self.metadata.get('clients', {}))} clients")
            except Exception as e:
                self.log(f"⚠ Could not load metadata: {e}")
    
    # ========================================================================
    # CONTACT SEARCH - Uses InfotemsHybridClient methods
    # ========================================================================
    
    def search_contacts(
        self, 
        a_number: str = None, 
        name: str = None,
        first_name: str = None,
        last_name: str = None,
        dob: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for contacts in InfoTems.
        
        Uses InfotemsHybridClient methods:
        - search_by_anumber() for A-number lookup
        - search_contacts() for name search
        - get_contact_biography() for DOB verification
        
        Returns list of matching contacts with match info.
        """
        results = []
        
        # Try A-number search (exact match) - uses client.search_by_anumber()
        if a_number:
            a_clean = re.sub(r'[^0-9]', '', a_number)
            
            # Check metadata cache first
            if self.metadata.get('clients'):
                for a_num, data in self.metadata['clients'].items():
                    if re.sub(r'[^0-9]', '', a_num) == a_clean:
                        contact_id = data.get('client_id')
                        if contact_id:
                            # Use client.get_contact() from hybrid client
                            contact = self.client.get_contact(contact_id)
                            if contact:
                                contact['_match_method'] = 'a_number'
                                contact['_match_confidence'] = 1.0
                                results.append(contact)
                                return results  # A-number is unique
            
            # API search using client.search_by_anumber()
            result = self.client.search_by_anumber(a_number)
            if result:
                result['_match_method'] = 'a_number'
                result['_match_confidence'] = 1.0
                results.append(result)
                return results
        
        # Name + DOB search using client.search_contacts()
        if (first_name or last_name) and dob:
            api_results = self.client.search_contacts(
                first_name=first_name,
                last_name=last_name,
                per_page=limit
            )
            
            if api_results and api_results.get('Data'):
                for contact in api_results['Data']:
                    # Check DOB match using client.get_contact_biography()
                    bio = self.get_contact_biographic(contact.get('Id'))
                    if bio:
                        contact_dob = bio.get('BirthDate', '')
                        if self._dates_match(contact_dob, dob):
                            contact['_match_method'] = 'name_dob'
                            contact['_match_confidence'] = 0.95
                            contact['_biographic'] = bio
                            results.append(contact)
        
        # Name-only search using client.search_contacts()
        if not results and (first_name or last_name):
            api_results = self.client.search_contacts(
                first_name=first_name,
                last_name=last_name,
                per_page=limit
            )
            
            if api_results and api_results.get('Data'):
                for contact in api_results['Data']:
                    contact['_match_method'] = 'name_only'
                    contact['_match_confidence'] = 0.6
                    results.append(contact)
        
        # Full name search (parse LAST, First)
        if not results and name:
            parts = name.split(',')
            if len(parts) >= 2:
                return self.search_contacts(
                    first_name=parts[1].strip().split()[0],
                    last_name=parts[0].strip(),
                    dob=dob,
                    limit=limit
                )
        
        return results[:limit]
    
    def find_contact(self, a_number: str = None, name: str = None) -> Optional[Dict[str, Any]]:
        """Find single best-matching contact."""
        results = self.search_contacts(a_number=a_number, name=name, limit=1)
        return results[0] if results else None
    
    def get_contact_biographic(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """
        Get contact biographic data.
        Uses client.get_contact_biography() from InfotemsHybridClient.
        """
        try:
            # Note: method is get_contact_biography (not biographic)
            return self.client.get_contact_biography(contact_id)
        except Exception:
            return None
    
    def _dates_match(self, date1: str, date2: str) -> bool:
        """Check if two dates match (handles different formats)."""
        if not date1 or not date2:
            return False
        
        def parse_date(d):
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(d.split('T')[0], fmt.split('T')[0])
                except ValueError:
                    continue
            return None
        
        d1 = parse_date(str(date1))
        d2 = parse_date(str(date2))
        
        return d1 and d2 and d1.date() == d2.date()
    
    # ========================================================================
    # COMPARISON - MAIN ENTRY POINT  
    # ========================================================================
    
    def compare(self, extracted_data: Dict[str, Any], source_file: str) -> ChangeSet:
        """
        Compare extracted data with InfoTems records.
        
        Builds complete ChangeSet including:
        - Primary contact field changes
        - Family members with search results
        - History records
        """
        self.log(f"\n{'='*60}")
        self.log(f"📊 COMPARING EXTRACTED DATA")
        self.log(f"{'='*60}")
        
        change_set = ChangeSet(
            document_type=extracted_data.get('document_type', ''),
            questionnaire_type=extracted_data.get('questionnaire_type'),
            source_file=str(source_file),
            extraction_confidence=extracted_data.get('confidence', 0.0),
        )
        
        # Get document config
        doc_type = extracted_data.get('document_type')
        all_types = get_all_document_types()
        
        if doc_type not in all_types:
            change_set.errors.append(f"Unknown document type: {doc_type}")
            return change_set
        
        doc_config = all_types[doc_type]
        
        # Extract primary contact identifier
        fields = extracted_data.get('fields', {})
        a_number = fields.get('a_number', {}).get('value')
        first_name = fields.get('first_name', {}).get('value', '')
        last_name = fields.get('last_name', {}).get('value', '')
        
        if a_number:
            change_set.a_number = a_number
        if first_name and last_name:
            change_set.contact_name = f"{last_name}, {first_name}"
        
        # Find existing contact using search methods
        existing_contact = self.find_contact(
            a_number=a_number,
            name=change_set.contact_name
        )
        
        biographic = None
        if existing_contact:
            change_set.contact_id = existing_contact.get('Id')
            change_set.contact_name = existing_contact.get('DisplayAs', change_set.contact_name)
            biographic = self.get_contact_biographic(change_set.contact_id)
            if biographic:
                change_set.biographic_id = biographic.get('Id')
            self.log(f"   ✓ Found contact: {change_set.contact_name} (ID: {change_set.contact_id})")
        else:
            self.log(f"   ℹ No existing contact found - will create new")
        
        # Compare primary fields
        self._compare_primary_fields(
            change_set, doc_config, fields, existing_contact, biographic
        )
        
        # Process family members
        family_data = extracted_data.get('family_members', [])
        if family_data:
            self._process_family_members(change_set, family_data)
        
        # Process history records
        history_data = extracted_data.get('history', {})
        if history_data:
            self._process_history(change_set, history_data)
        
        # Other info
        other = extracted_data.get('other', {})
        if other:
            change_set.other_info = other
        
        # Summary
        self.log(f"\n   📋 SUMMARY:")
        self.log(f"      Primary changes: {change_set.total_primary_changes}")
        self.log(f"      Family members: {len(change_set.family_members)}")
        self.log(f"      History records: {change_set.history_count}")
        
        return change_set
    
    def _compare_primary_fields(
        self, 
        change_set: ChangeSet,
        doc_config: Dict,
        fields: Dict[str, Any],
        existing_contact: Optional[Dict],
        biographic: Optional[Dict]
    ):
        """Compare primary contact fields."""
        self.log(f"\n   Comparing primary fields...")
        
        # Get field definitions from config
        field_defs = doc_config.get('fields', {})
        if isinstance(field_defs, dict):
            # Questionnaire format
            primary_fields = field_defs.get('primary', [])
        else:
            # Document format (list)
            primary_fields = field_defs
        
        for field_def in primary_fields:
            field_key = field_def['key']
            field_label = field_def['label']
            infotems_field = field_def.get('infotems_field')
            is_biographic = field_def.get('biographic', False)
            
            # Get extracted value
            extracted = fields.get(field_key, {})
            new_value = extracted.get('value')
            confidence = extracted.get('confidence', 0.0)
            
            if not new_value:
                continue
            
            # Get current value
            current_value = None
            if infotems_field:
                if is_biographic and biographic:
                    current_value = biographic.get(infotems_field)
                elif existing_contact:
                    current_value = existing_contact.get(infotems_field)
            
            # Determine change type
            current_norm = self._normalize_value(current_value, field_def)
            new_norm = self._normalize_value(new_value, field_def)
            
            if not current_value:
                change_type = ChangeType.NEW
            elif current_norm != new_norm:
                change_type = ChangeType.MODIFIED
            else:
                change_type = ChangeType.UNCHANGED
            
            change = FieldChange(
                field_key=field_key,
                field_label=field_label,
                current_value=str(current_value) if current_value else None,
                new_value=str(new_value) if new_value else None,
                confidence=confidence,
                change_type=change_type,
                infotems_field=infotems_field,
                is_biographic=is_biographic,
                approved=(change_type != ChangeType.UNCHANGED)
            )
            
            change_set.changes.append(change)
            
            if change.has_change:
                icon = "➕" if change_type == ChangeType.NEW else "📝"
                self.log(f"      {icon} {field_label}: '{current_value}' → '{new_value}'")
    
    def _process_family_members(self, change_set: ChangeSet, family_data: List[Dict]):
        """Process extracted family members."""
        self.log(f"\n   Processing {len(family_data)} family members...")
        
        for fm_data in family_data:
            relationship = fm_data.get('relationship', 'unknown')
            extracted = fm_data.get('data', {})
            confidence = fm_data.get('confidence', 0.0)
            
            fm = FamilyMember(
                relationship=relationship,
                extracted_data=extracted,
                confidence=confidence,
            )
            
            # Search for existing contact
            fm_a_number = extracted.get('a_number')
            fm_first = extracted.get('first_name')
            fm_last = extracted.get('last_name')
            fm_dob = extracted.get('date_of_birth')
            
            search_results = self.search_contacts(
                a_number=fm_a_number,
                first_name=fm_first,
                last_name=fm_last,
                dob=fm_dob,
                limit=5
            )
            
            fm.search_results = search_results
            
            if search_results:
                best_match = search_results[0]
                fm.matched_contact_id = best_match.get('Id')
                fm.matched_contact_name = best_match.get('DisplayAs')
                fm.match_confidence = best_match.get('_match_confidence', 0.0)
                fm.match_method = best_match.get('_match_method')
                
                # Default action based on match quality
                if fm.match_confidence >= 0.9:
                    fm.action = FamilyMemberAction.UPDATE_LINKED
                else:
                    fm.action = FamilyMemberAction.SKIP  # User must confirm
                
                self.log(f"      {relationship}: {fm.display_name} - matched to {fm.matched_contact_name}")
            else:
                self.log(f"      {relationship}: {fm.display_name} - no match found")
            
            change_set.family_members.append(fm)
    
    def _process_history(self, change_set: ChangeSet, history_data: Dict):
        """Process history records."""
        self.log(f"\n   Processing history records...")
        
        for history_type, records in history_data.items():
            if not records:
                continue
            
            history_set = HistorySet(history_type=history_type)
            
            for rec_data in records:
                record = HistoryRecord(
                    record_type=history_type,
                    data=rec_data.get('data', rec_data),
                    confidence=rec_data.get('confidence', 0.8),
                    is_current=rec_data.get('is_current', False),
                )
                history_set.records.append(record)
            
            change_set.history[history_type] = history_set
            self.log(f"      {history_set.display_name}: {len(history_set.records)} records")
    
    def _normalize_value(self, value: Any, field_def: Dict) -> str:
        """Normalize value for comparison."""
        if value is None:
            return ''
        
        value_str = str(value).strip()
        
        if field_def.get('type') == 'date':
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(value_str.split('T')[0], fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return value_str
        
        if 'phone' in field_def['key'].lower():
            return re.sub(r'[^\d]', '', value_str)
        
        if 'a_number' in field_def['key'].lower():
            return re.sub(r'[^0-9]', '', value_str)
        
        return value_str.lower()
    
    # ========================================================================
    # APPLY CHANGES - Uses InfotemsHybridClient methods
    # ========================================================================
    
    def apply_changes(self, change_set: ChangeSet) -> Dict[str, Any]:
        """
        Apply all approved changes to InfoTems.
        
        Uses InfotemsHybridClient methods:
        - create_contact() - Create new contact
        - update_contact() - Update contact fields (PATCH)
        - create_contact_biographic() - Create biographic record
        - update_contact_biographic() - Update biographic (PATCH)
        - create_note() - Create case notes for history
        
        Handles:
        - Primary contact updates/creation
        - Family member create/update (linking requires API enhancement)
        - History saved as case notes
        """
        self.log(f"\n{'='*60}")
        self.log(f"📤 APPLYING CHANGES TO INFOTEMS")
        self.log(f"{'='*60}")
        
        results = {
            'success': False,
            'primary_contact': {
                'contact_id': change_set.contact_id,
                'created': False,
                'updated': False,
                'fields': [],
            },
            'family_members': [],
            'history_notes': [],
            'errors': [],
        }
        
        try:
            # 1. Apply primary contact changes
            self._apply_primary_changes(change_set, results)
            
            # 2. Apply family member changes
            self._apply_family_changes(change_set, results)
            
            # 3. Save history as proper records (or notes as fallback)
            self._apply_history_records(change_set, results)
            
            results['success'] = True
            self.log(f"\n   ✅ All changes applied successfully")
            
        except Exception as e:
            results['errors'].append(str(e))
            self.log(f"   ❌ Error: {e}")
        
        return results
    
    def _apply_primary_changes(self, change_set: ChangeSet, results: Dict):
        """
        Apply primary contact changes.
        Uses client.create_contact(), update_contact(), 
        create_contact_biographic(), update_contact_biographic()
        """
        contact_updates = {}
        biographic_updates = {}
        
        for change in change_set.changes:
            if not change.approved or not change.has_change or not change.infotems_field:
                continue
            
            value = change.final_value
            if change.is_biographic:
                biographic_updates[change.infotems_field] = value
            else:
                contact_updates[change.infotems_field] = value
        
        if not contact_updates and not biographic_updates:
            self.log("   ℹ No primary contact changes to apply")
            return
        
        # Create new contact if needed using client.create_contact()
        if not change_set.contact_id:
            first_name = contact_updates.pop('FirstName', '')
            last_name = contact_updates.pop('LastName', '')
            
            if not first_name or not last_name:
                raise ValueError("Cannot create contact without First and Last name")
            
            # Uses InfotemsHybridClient.create_contact()
            new_id = self.client.create_contact(
                first_name=first_name,
                last_name=last_name,
                **contact_updates
            )
            change_set.contact_id = new_id
            results['primary_contact']['contact_id'] = new_id
            results['primary_contact']['created'] = True
            self.log(f"   ✓ Created contact ID: {new_id}")
            contact_updates = {}
        
        # Update contact fields using client.update_contact() (PATCH)
        if contact_updates:
            self.client.update_contact(change_set.contact_id, contact_updates)
            results['primary_contact']['updated'] = True
            results['primary_contact']['fields'].extend(contact_updates.keys())
            self.log(f"   ✓ Updated {len(contact_updates)} contact fields")
        
        # Update biographic fields
        if biographic_updates:
            if change_set.biographic_id:
                # Uses client.update_contact_biographic() (PATCH)
                self.client.update_contact_biographic(
                    change_set.biographic_id, biographic_updates
                )
            else:
                # Uses client.create_contact_biographic()
                result = self.client.create_contact_biographic(
                    change_set.contact_id, **biographic_updates
                )
                if result:
                    change_set.biographic_id = result.get('Id')
            
            results['primary_contact']['fields'].extend(biographic_updates.keys())
            self.log(f"   ✓ Updated {len(biographic_updates)} biographic fields")
    
    def _apply_family_changes(self, change_set: ChangeSet, results: Dict):
        """
        Apply family member changes.
        
        Uses InfotemsHybridClient methods:
        - create_contact() - Create new contact for family member
        - update_contact() - Update existing contact
        - add_contact_relative() - Link contacts as relatives
        - search_contact_relationships() - Check existing relationships
        
        Supports:
        - CREATE_NEW: Creates new contact AND links as relative
        - UPDATE_LINKED: Updates existing matched contact
        - LINK_EXISTING: Links existing contact as relative
        """
        # Map our relationship types to InfoTems relationship types
        RELATIONSHIP_MAP = {
            'spouse': 'Spouse',
            'child': 'Child',
            'father': 'Father',
            'mother': 'Mother',
            'sibling': 'Sibling',
            'prior_spouse': 'Spouse',  # Will set end_date
            'son': 'Son',
            'daughter': 'Daughter',
            'brother': 'Brother',
            'sister': 'Sister',
            'parent': 'Parent',
        }
        
        for fm in change_set.family_members:
            fm_result = {
                'relationship': fm.relationship,
                'name': fm.display_name,
                'action': fm.action.value,
                'contact_id': None,
                'relationship_id': None,
                'success': False,
            }
            
            try:
                if fm.action == FamilyMemberAction.SKIP:
                    fm_result['success'] = True
                    
                elif fm.action == FamilyMemberAction.CREATE_NEW:
                    data = fm.final_data
                    
                    # Create the family member contact with all available fields
                    contact_fields = {}
                    if data.get('middle_name'):
                        contact_fields['MiddleName'] = data['middle_name']
                    if data.get('maiden_name'):
                        contact_fields['MaidenName'] = data['maiden_name']
                    
                    new_id = self.client.create_contact(
                        first_name=data.get('first_name', ''),
                        last_name=data.get('last_name', ''),
                        **contact_fields
                    )
                    fm_result['contact_id'] = new_id
                    self.log(f"   ✓ Created {fm.relationship}: {fm.display_name} (ID: {new_id})")
                    
                    # Create biographic data for the family member
                    bio_fields = self._build_biographic_fields(data)
                    if bio_fields and new_id:
                        try:
                            self.client.create_contact_biographic(new_id, **bio_fields)
                            self.log(f"   ✓ Added biographic data ({len(bio_fields)} fields)")
                        except Exception as bio_err:
                            self.log(f"   ⚠ Biographic creation failed: {bio_err}")
                    
                    # Link as relative
                    if change_set.contact_id and new_id:
                        rel_type = RELATIONSHIP_MAP.get(fm.relationship, 'Other')
                        rel_kwargs = self._build_relationship_kwargs(fm, data)
                        
                        rel_result = self.client.add_contact_relative(
                            primary_contact_id=change_set.contact_id,
                            related_to_contact_id=new_id,
                            related_to_contact_is=rel_type,
                            **rel_kwargs
                        )
                        
                        if rel_result:
                            fm_result['relationship_id'] = rel_result.get('Id')
                            self.log(f"   ✓ Linked as {rel_type}")
                    
                    fm_result['success'] = True
                    
                elif fm.action == FamilyMemberAction.LINK_EXISTING:
                    # Link existing contact as relative
                    if fm.matched_contact_id and change_set.contact_id:
                        rel_type = RELATIONSHIP_MAP.get(fm.relationship, 'Other')
                        data = fm.final_data
                        rel_kwargs = self._build_relationship_kwargs(fm, data)
                        
                        rel_result = self.client.add_contact_relative(
                            primary_contact_id=change_set.contact_id,
                            related_to_contact_id=fm.matched_contact_id,
                            related_to_contact_is=rel_type,
                            **rel_kwargs
                        )
                        
                        fm_result['contact_id'] = fm.matched_contact_id
                        if rel_result:
                            fm_result['relationship_id'] = rel_result.get('Id')
                        fm_result['success'] = True
                        self.log(f"   ✓ Linked {fm.relationship}: {fm.display_name} as {rel_type}")
                    
                elif fm.action == FamilyMemberAction.UPDATE_LINKED:
                    if fm.matched_contact_id:
                        data = fm.final_data
                        updates = {}
                        
                        # Map family member fields to contact fields
                        field_map = {
                            'first_name': 'FirstName',
                            'middle_name': 'MiddleName', 
                            'last_name': 'LastName',
                        }
                        
                        for fm_key, it_key in field_map.items():
                            if data.get(fm_key):
                                updates[it_key] = data[fm_key]
                        
                        if updates:
                            self.client.update_contact(fm.matched_contact_id, updates)
                        
                        fm_result['contact_id'] = fm.matched_contact_id
                        fm_result['success'] = True
                        self.log(f"   ✓ Updated {fm.relationship}: {fm.display_name}")
                        
            except Exception as e:
                fm_result['error'] = str(e)
                results['errors'].append(f"Family member {fm.display_name}: {e}")
            
            results['family_members'].append(fm_result)
    
    def _build_relationship_kwargs(self, fm: FamilyMember, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build kwargs for add_contact_relative() from family member data.
        
        Maps extracted questionnaire fields to InfoTems relationship fields.
        """
        kwargs = {}
        
        # Marriage/relationship dates
        if data.get('date_of_marriage'):
            kwargs['start_date'] = data['date_of_marriage']
        if data.get('date_marriage_ended'):
            kwargs['end_date'] = data['date_marriage_ended']
        
        # Marriage start location
        if data.get('place_of_marriage'):
            place = data['place_of_marriage']
            parts = [p.strip() for p in place.split(',')]
            if len(parts) >= 1:
                kwargs['start_city'] = parts[0]
            if len(parts) >= 2:
                kwargs['start_state'] = parts[1]
            if len(parts) >= 3:
                kwargs['start_country'] = parts[2]
        
        # Marriage end location (divorce/death location)
        if data.get('place_marriage_ended'):
            place = data['place_marriage_ended']
            parts = [p.strip() for p in place.split(',')]
            if len(parts) >= 1:
                kwargs['end_city'] = parts[0]
            if len(parts) >= 2:
                kwargs['end_state'] = parts[1]
            if len(parts) >= 3:
                kwargs['end_country'] = parts[2]
        
        # Immigration flags
        if data.get('include_in_application') is not None:
            kwargs['are_filing_immigration_benefit_together'] = bool(data['include_in_application'])
        if data.get('resides_with_applicant') is not None:
            kwargs['does_related_contact_reside_with_primary_contact'] = bool(data['resides_with_applicant'])
            # If they reside together, they're household members
            kwargs['are_household_members'] = bool(data['resides_with_applicant'])
        if data.get('will_accompany') is not None:
            kwargs['will_related_contact_accompany'] = bool(data['will_accompany'])
        if data.get('will_immigrate_later') is not None:
            kwargs['will_related_contact_immigrate_later'] = bool(data['will_immigrate_later'])
        if data.get('is_step') is not None:
            kwargs['is_step'] = bool(data['is_step'])
        if data.get('is_adopted') is not None:
            kwargs['is_related_contact_adopted'] = bool(data['is_adopted'])
        
        # For prior spouse, mark as estranged if no end_date
        if fm.relationship == 'prior_spouse' and 'end_date' not in kwargs:
            kwargs['are_estranged'] = True
        
        return kwargs
    
    def _build_biographic_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build biographic fields for create_contact_biographic() from extracted data.
        
        Maps questionnaire fields to InfoTems ContactBiographic fields.
        """
        fields = {}
        
        # A-number
        if data.get('a_number'):
            fields['AlienNumber'] = data['a_number']
        
        # Birth information
        if data.get('date_of_birth'):
            fields['BirthDate'] = data['date_of_birth']
        if data.get('city_of_birth'):
            fields['BirthCity'] = data['city_of_birth']
        if data.get('state_of_birth'):
            fields['BirthState'] = data['state_of_birth']
        if data.get('country_of_birth'):
            fields['BirthCountry'] = data['country_of_birth']
        
        # Demographics
        if data.get('gender'):
            fields['Gender'] = data['gender']
        if data.get('citizenship'):
            fields['Citizenship1Country'] = data['citizenship']
        if data.get('ethnicity'):
            fields['Ethnicity'] = data['ethnicity']
        if data.get('race'):
            fields['Race'] = data['race']
        
        # Immigration status
        if data.get('immigration_status'):
            fields['CurrentImmigrationStatus'] = data['immigration_status']
        if data.get('date_of_entry'):
            fields['DateOfLastEntryToUSA'] = data['date_of_entry']
        
        # SSN (only if provided)
        if data.get('ssn'):
            fields['SSN'] = data['ssn']
        
        return fields
    
    def get_contact_relatives(self, contact_id: int) -> List[Dict[str, Any]]:
        """
        Get all relatives linked to a contact.
        Uses client.search_contact_relationships() from InfotemsHybridClient.
        
        Args:
            contact_id: The primary contact ID
            
        Returns:
            List of relationship records
        """
        try:
            result = self.client.search_contact_relationships(
                primary_contact_id=contact_id,
                per_page=100
            )
            return result.get('Items', []) if result else []
        except Exception:
            return []
    
    def _apply_history_records(self, change_set: ChangeSet, results: Dict):
        """
        Save history as proper InfoTems records or notes.
        
        Uses InfotemsHybridClient methods:
        - create_address() for address history
        - create_employment() for employment history  
        - create_education() for education history
        - create_travel_history() for travel/entry history
        - create_note() for unsupported history types (fallback)
        """
        if not change_set.contact_id:
            return
        
        for history_type, history_set in change_set.history.items():
            if history_set.action == HistoryAction.SKIP:
                continue
            
            if not history_set.records:
                continue
            
            # Route to appropriate handler based on action and type
            if history_set.action == HistoryAction.SAVE_AS_RECORDS and history_set.supports_records:
                self._create_history_records(change_set.contact_id, history_set, results)
            else:
                # Fallback to notes for unsupported types
                self._create_history_note(change_set.contact_id, history_set, results)
    
    def _create_history_records(self, contact_id: int, history_set: HistorySet, results: Dict):
        """Create proper InfoTems records for supported history types."""
        
        record_results = {
            'type': history_set.history_type,
            'record_count': len(history_set.records),
            'created_ids': [],
            'success': False,
        }
        
        try:
            for record in history_set.records:
                data = record.final_data
                record_id = None
                
                if history_set.history_type == 'address':
                    record_id = self._create_address_record(contact_id, data)
                elif history_set.history_type == 'employment':
                    record_id = self._create_employment_record(contact_id, data)
                elif history_set.history_type == 'education':
                    record_id = self._create_education_record(contact_id, data)
                elif history_set.history_type == 'travel':
                    record_id = self._create_travel_record(contact_id, data)
                
                if record_id:
                    record_results['created_ids'].append(record_id)
            
            record_results['success'] = len(record_results['created_ids']) > 0
            self.log(f"   ✓ Created {len(record_results['created_ids'])} {history_set.display_name} records")
            
        except Exception as e:
            record_results['error'] = str(e)
            results['errors'].append(f"History {history_set.history_type}: {e}")
        
        results['history_notes'].append(record_results)
    
    def _create_address_record(self, contact_id: int, data: Dict[str, Any]) -> Optional[int]:
        """Create an Address record in InfoTems."""
        kwargs = {'contact_id': contact_id}
        
        if data.get('street') or data.get('address_line1'):
            kwargs['line1'] = data.get('street') or data.get('address_line1')
        if data.get('apt') or data.get('address_line2'):
            kwargs['Line2'] = data.get('apt') or data.get('address_line2')
        if data.get('city'):
            kwargs['city'] = data['city']
        if data.get('state'):
            kwargs['state'] = data['state']
        if data.get('country'):
            kwargs['country'] = data['country']
        if data.get('zip') or data.get('postal_code'):
            kwargs['postal_zip_code'] = data.get('zip') or data.get('postal_code')
        if data.get('from_date'):
            kwargs['StartDate'] = data['from_date']
        if data.get('to_date'):
            kwargs['EndDate'] = data['to_date']
        
        result = self.client.create_address(**kwargs)
        return result.get('Id') if result else None
    
    def _create_employment_record(self, contact_id: int, data: Dict[str, Any]) -> Optional[int]:
        """Create an Employment record in InfoTems."""
        kwargs = {'contact_id': contact_id}
        
        if data.get('employer') or data.get('company_name'):
            # Note: Ideally we'd create/find a Company first, but for now use occupation
            kwargs['occupation'] = data.get('job_title') or data.get('position') or 'Employee'
        if data.get('job_title') or data.get('position'):
            kwargs['occupation'] = data.get('job_title') or data.get('position')
        if data.get('from_date'):
            kwargs['start_date'] = data['from_date']
        if data.get('to_date'):
            kwargs['end_date'] = data['to_date']
        
        result = self.client.create_employment(**kwargs)
        return result.get('Id') if result else None
    
    def _create_education_record(self, contact_id: int, data: Dict[str, Any]) -> Optional[int]:
        """Create an Education record in InfoTems."""
        kwargs = {'contact_id': contact_id}
        
        if data.get('school') or data.get('institution'):
            kwargs['institution_name'] = data.get('school') or data.get('institution')
        if data.get('degree') or data.get('program'):
            kwargs['program_of_study'] = data.get('degree') or data.get('program')
        if data.get('city'):
            kwargs['city'] = data['city']
        if data.get('country'):
            kwargs['country'] = data['country']
        if data.get('from_date'):
            kwargs['start_date'] = data['from_date']
        if data.get('to_date'):
            kwargs['end_date'] = data['to_date']
        
        result = self.client.create_education(**kwargs)
        return result.get('Id') if result else None
    
    def _create_travel_record(self, contact_id: int, data: Dict[str, Any]) -> Optional[int]:
        """Create a TravelHistory record in InfoTems."""
        kwargs = {'contact_id': contact_id}
        
        if data.get('arrival_date') or data.get('entry_date'):
            kwargs['arrival_date'] = data.get('arrival_date') or data.get('entry_date')
        if data.get('departure_date') or data.get('exit_date'):
            kwargs['departure_date'] = data.get('departure_date') or data.get('exit_date')
        if data.get('port_of_entry') or data.get('arrival_city'):
            kwargs['arrival_city'] = data.get('port_of_entry') or data.get('arrival_city')
        if data.get('arrival_state'):
            kwargs['arrival_state'] = data['arrival_state']
        if data.get('status_on_entry') or data.get('immigration_status'):
            kwargs['immigration_status_on_arrival'] = data.get('status_on_entry') or data.get('immigration_status')
        if data.get('countries_visited'):
            kwargs['visited_countries'] = data['countries_visited']
        
        result = self.client.create_travel_history(**kwargs)
        return result.get('Id') if result else None
    
    def _create_history_note(self, contact_id: int, history_set: HistorySet, results: Dict):
        """Fallback: Save history as a formatted note."""
        note_result = {
            'type': history_set.history_type,
            'record_count': len(history_set.records),
            'success': False,
        }
        
        try:
            content = self._format_history_note(history_set)
            category = HISTORY_TYPES.get(history_set.history_type, {}).get(
                'note_category', 'Case Status'
            )
            subject = f"{history_set.display_name} - {datetime.now().strftime('%m/%d/%Y')}"
            
            note_id = self.client.create_note(
                subject=subject,
                body=content,
                contact_id=contact_id,
                category=category
            )
            
            note_result['success'] = True
            note_result['note_id'] = note_id
            self.log(f"   ✓ Saved {history_set.display_name} as note ({len(history_set.records)} records)")
            
        except Exception as e:
            note_result['error'] = str(e)
            results['errors'].append(f"History {history_set.history_type}: {e}")
        
        results['history_notes'].append(note_result)
    
    def _format_history_note(self, history_set: HistorySet) -> str:
        """Format history records as note content."""
        lines = [
            f"=== {history_set.display_name.upper()} ===",
            f"Updated: {datetime.now().strftime('%m/%d/%Y')}",
            ""
        ]
        
        # Sort: current first, then by date descending
        records = sorted(
            history_set.records,
            key=lambda r: (not r.is_current, r.final_data.get('from_date', '0000')),
            reverse=True
        )
        
        for i, record in enumerate(records, 1):
            data = record.final_data
            
            if record.is_current:
                lines.append(f"{i}. CURRENT")
            else:
                lines.append(f"{i}. PREVIOUS")
            
            # Format based on type
            if history_set.history_type == 'address':
                addr = data.get('address_line1', '')
                if data.get('address_line2'):
                    addr += f", {data['address_line2']}"
                city = data.get('city', '')
                state = data.get('state', '')
                zip_code = data.get('zip_code', '')
                country = data.get('country', '')
                
                lines.append(f"   {addr}")
                lines.append(f"   {city}, {state} {zip_code}")
                if country and country.upper() not in ('US', 'USA', 'UNITED STATES'):
                    lines.append(f"   {country}")
                    
            elif history_set.history_type == 'employment':
                lines.append(f"   {data.get('employer_name', 'Unknown')}")
                lines.append(f"   {data.get('occupation', '')}")
                addr = data.get('address_line1', '')
                city = data.get('city', '')
                if addr or city:
                    lines.append(f"   {addr}, {city}")
                    
            elif history_set.history_type == 'education':
                lines.append(f"   {data.get('school_name', 'Unknown')} ({data.get('school_type', '')})")
                city = data.get('city', '')
                country = data.get('country', '')
                if city or country:
                    lines.append(f"   {city}, {country}")
            
            # Dates
            from_date = data.get('from_date', '')
            to_date = data.get('to_date', 'Present')
            if from_date:
                lines.append(f"   From: {from_date} to {to_date}")
            
            lines.append("")
        
        return "\n".join(lines)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("INFOTEMS COMPARATOR - TEST MODE")
    print("="*60)
    print("\nThis module depends on InfotemsHybridClient at:")
    print("..\\New Official Infotems API\\infotems_hybrid_client.py")
    print("\nAll InfoTems operations go through that client.")
    
    try:
        comparator = InfotemsComparator(verbose=True)
        
        print("\n--- Testing Contact Search ---")
        results = comparator.search_contacts(first_name="Juan", last_name="Garcia", limit=3)
        for r in results:
            print(f"  Found: {r.get('DisplayAs')} (ID: {r.get('Id')}, Method: {r.get('_match_method')})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
