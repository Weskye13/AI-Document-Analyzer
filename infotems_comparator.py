"""
AI Document Analyzer - InfoTems Comparison
===========================================

Compares extracted document data with existing InfoTems records.
Generates change proposals for user approval.

Author: Law Office of Joshua E. Bardavid
Version: 1.0.0
Date: January 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict

from config import (
    DOCUMENT_TYPES, CONTACT_FIELDS, BIOGRAPHIC_FIELDS,
    INFOTEMS_USERNAME, INFOTEMS_PASSWORD, INFOTEMS_API_KEY,
    METADATA_PATH
)

# Import InfoTems client
try:
    from infotems_hybrid_client import InfotemsHybridClient
    INFOTEMS_AVAILABLE = True
except ImportError:
    INFOTEMS_AVAILABLE = False


@dataclass
class FieldChange:
    """Represents a proposed change to a single field."""
    field_key: str
    field_label: str
    current_value: Optional[str]
    new_value: Optional[str]
    confidence: float
    change_type: str  # 'new', 'modified', 'unchanged'
    infotems_field: Optional[str] = None
    is_biographic: bool = False
    approved: bool = True  # Default to approved
    
    @property
    def has_change(self) -> bool:
        """Check if this represents an actual change."""
        return self.change_type in ('new', 'modified')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ChangeSet:
    """Collection of proposed changes for a contact."""
    contact_id: Optional[int] = None
    contact_name: str = ""
    a_number: str = ""
    document_type: str = ""
    source_file: str = ""
    extraction_confidence: float = 0.0
    changes: List[FieldChange] = field(default_factory=list)
    biographic_id: Optional[int] = None
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def contact_changes(self) -> List[FieldChange]:
        """Get changes that apply to Contact record."""
        return [c for c in self.changes if not c.is_biographic and c.has_change]
    
    @property
    def biographic_changes(self) -> List[FieldChange]:
        """Get changes that apply to ContactBiographic record."""
        return [c for c in self.changes if c.is_biographic and c.has_change]
    
    @property
    def approved_changes(self) -> List[FieldChange]:
        """Get only approved changes."""
        return [c for c in self.changes if c.approved and c.has_change]
    
    @property
    def total_changes(self) -> int:
        """Count of actual changes (not unchanged)."""
        return sum(1 for c in self.changes if c.has_change)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            'contact_id': self.contact_id,
            'contact_name': self.contact_name,
            'a_number': self.a_number,
            'document_type': self.document_type,
            'source_file': self.source_file,
            'extraction_confidence': self.extraction_confidence,
            'changes': [c.to_dict() for c in self.changes],
            'biographic_id': self.biographic_id,
            'errors': self.errors,
            'created_at': self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeSet':
        """Create from dictionary."""
        changes = [FieldChange(**c) for c in data.get('changes', [])]
        return cls(
            contact_id=data.get('contact_id'),
            contact_name=data.get('contact_name', ''),
            a_number=data.get('a_number', ''),
            document_type=data.get('document_type', ''),
            source_file=data.get('source_file', ''),
            extraction_confidence=data.get('extraction_confidence', 0.0),
            changes=changes,
            biographic_id=data.get('biographic_id'),
            errors=data.get('errors', []),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )


class InfotemsComparator:
    """
    Compares extracted document data with InfoTems records.
    
    Generates change proposals that can be reviewed before applying.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize comparator with InfoTems connection.
        
        Args:
            verbose: Print status messages
        """
        self.verbose = verbose
        self.client = None
        self.metadata = {}
        
        if not INFOTEMS_AVAILABLE:
            raise ImportError("InfoTems client not available. Check INFOTEMS_API_PATH.")
        
        # Initialize InfoTems client
        self.client = InfotemsHybridClient(
            api_key=INFOTEMS_API_KEY,
            username=INFOTEMS_USERNAME,
            password=INFOTEMS_PASSWORD,
            debug=False
        )
        
        # Load metadata cache
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
    # CONTACT LOOKUP
    # ========================================================================
    
    def find_contact(self, a_number: str = None, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Find existing contact in InfoTems.
        
        Args:
            a_number: A-number to search
            name: Client name to search (fallback)
            
        Returns:
            Contact dict or None
        """
        self.log(f"🔍 Searching InfoTems...")
        
        # Try A-number search first
        if a_number:
            # Clean A-number
            a_clean = re.sub(r'[^0-9]', '', a_number)
            
            # Check metadata cache first
            if self.metadata.get('clients'):
                for a_num, data in self.metadata['clients'].items():
                    if re.sub(r'[^0-9]', '', a_num) == a_clean:
                        contact_id = data.get('client_id')
                        if contact_id:
                            self.log(f"   ✓ Found in cache: ID {contact_id}")
                            return self.client.get_contact(contact_id)
            
            # Search via API
            result = self.client.search_by_anumber(a_number)
            if result:
                self.log(f"   ✓ Found by A-number: {result.get('DisplayAs')} (ID: {result.get('Id')})")
                return result
        
        # Try name search as fallback
        if name:
            # Parse name (assuming LAST, First format)
            parts = name.split(',')
            if len(parts) >= 2:
                last_name = parts[0].strip()
                first_name = parts[1].strip().split()[0]  # First word only
                
                result = self.client.search_contacts(
                    first_name=first_name,
                    last_name=last_name,
                    per_page=5
                )
                
                if result and result.get('Data'):
                    contact = result['Data'][0]
                    self.log(f"   ✓ Found by name: {contact.get('DisplayAs')} (ID: {contact.get('Id')})")
                    return contact
        
        self.log(f"   ⚠ Contact not found")
        return None
    
    def get_contact_biographic(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """
        Get contact biographic data.
        
        Args:
            contact_id: InfoTems contact ID
            
        Returns:
            Biographic data dict or None
        """
        try:
            bio = self.client.get_contact_biography(contact_id)
            if bio:
                self.log(f"   ✓ Retrieved biographic data")
                return bio
        except Exception as e:
            self.log(f"   ⚠ Could not get biographic: {e}")
        
        return None
    
    # ========================================================================
    # COMPARISON
    # ========================================================================
    
    def compare(self, extracted_data: Dict[str, Any], source_file: str) -> ChangeSet:
        """
        Compare extracted data with InfoTems record.
        
        Args:
            extracted_data: Result from DocumentExtractor.extract_data()
            source_file: Path to source document
            
        Returns:
            ChangeSet with proposed changes
        """
        self.log(f"\n{'='*60}")
        self.log(f"📊 COMPARING DATA")
        self.log(f"{'='*60}")
        
        # Initialize change set
        change_set = ChangeSet(
            document_type=extracted_data.get('document_type', ''),
            source_file=str(source_file),
            extraction_confidence=extracted_data.get('confidence', 0.0),
        )
        
        # Get document type config
        doc_type = extracted_data.get('document_type')
        if doc_type not in DOCUMENT_TYPES:
            change_set.errors.append(f"Unknown document type: {doc_type}")
            return change_set
        
        doc_config = DOCUMENT_TYPES[doc_type]
        extracted_fields = extracted_data.get('fields', {})
        
        # Extract A-number and name for lookup
        a_number = None
        client_name = None
        
        if 'a_number' in extracted_fields:
            a_number = extracted_fields['a_number'].get('value')
            change_set.a_number = a_number or ''
        
        # Build name from extracted fields
        first = extracted_fields.get('first_name', {}).get('value', '')
        last = extracted_fields.get('last_name', {}).get('value', '')
        if last and first:
            client_name = f"{last}, {first}"
            change_set.contact_name = client_name
        
        # Find existing contact
        existing_contact = self.find_contact(a_number=a_number, name=client_name)
        
        if existing_contact:
            change_set.contact_id = existing_contact.get('Id')
            change_set.contact_name = existing_contact.get('DisplayAs', client_name)
            
            # Get biographic data
            biographic = self.get_contact_biographic(change_set.contact_id)
            if biographic:
                change_set.biographic_id = biographic.get('Id')
        else:
            self.log(f"\n   ℹ Contact not found - will create new contact")
        
        # Compare each field
        self.log(f"\n   Comparing fields...")
        
        for field_def in doc_config['fields']:
            field_key = field_def['key']
            field_label = field_def['label']
            infotems_field = field_def.get('infotems_field')
            is_biographic = field_def.get('biographic', False)
            is_document_field = field_def.get('document_field', False)
            
            # Skip document-only fields (passport number, etc.)
            if is_document_field:
                continue
            
            # Get extracted value
            extracted_info = extracted_fields.get(field_key, {})
            new_value = extracted_info.get('value')
            confidence = extracted_info.get('confidence', 0.0)
            
            # Skip if no extracted value
            if not new_value:
                continue
            
            # Get current value
            current_value = None
            if existing_contact and infotems_field:
                if is_biographic and biographic:
                    current_value = biographic.get(infotems_field)
                else:
                    current_value = existing_contact.get(infotems_field)
            
            # Normalize values for comparison
            current_norm = self._normalize_value(current_value, field_def)
            new_norm = self._normalize_value(new_value, field_def)
            
            # Determine change type
            if not current_value:
                change_type = 'new'
            elif current_norm != new_norm:
                change_type = 'modified'
            else:
                change_type = 'unchanged'
            
            # Create change record
            change = FieldChange(
                field_key=field_key,
                field_label=field_label,
                current_value=str(current_value) if current_value else None,
                new_value=str(new_value) if new_value else None,
                confidence=confidence,
                change_type=change_type,
                infotems_field=infotems_field,
                is_biographic=is_biographic,
                approved=(change_type != 'unchanged')  # Auto-approve actual changes
            )
            
            change_set.changes.append(change)
            
            # Log the comparison
            if change.has_change:
                icon = "➕" if change_type == 'new' else "📝"
                self.log(f"   {icon} {field_label}: '{current_value}' → '{new_value}'")
        
        self.log(f"\n   📋 Summary: {change_set.total_changes} changes found")
        
        return change_set
    
    def _normalize_value(self, value: Any, field_def: Dict) -> str:
        """
        Normalize value for comparison.
        
        Args:
            value: Value to normalize
            field_def: Field definition
            
        Returns:
            Normalized string value
        """
        if value is None:
            return ''
        
        value_str = str(value).strip()
        
        # Handle dates
        if field_def.get('type') == 'date':
            # Try to parse and standardize date format
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(value_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return value_str
        
        # Handle phone numbers
        if 'phone' in field_def['key'].lower():
            # Remove non-digits
            return re.sub(r'[^\d]', '', value_str)
        
        # Handle A-numbers
        if 'a_number' in field_def['key'].lower():
            return re.sub(r'[^A0-9]', '', value_str.upper())
        
        # Default: lowercase for comparison
        return value_str.lower()
    
    # ========================================================================
    # APPLY CHANGES
    # ========================================================================
    
    def apply_changes(self, change_set: ChangeSet) -> Dict[str, Any]:
        """
        Apply approved changes to InfoTems.
        
        Args:
            change_set: ChangeSet with approved changes
            
        Returns:
            Result dict with success status and details
        """
        self.log(f"\n{'='*60}")
        self.log(f"📤 APPLYING CHANGES TO INFOTEMS")
        self.log(f"{'='*60}")
        
        results = {
            'success': False,
            'contact_id': change_set.contact_id,
            'contact_updated': False,
            'biographic_updated': False,
            'contact_created': False,
            'fields_updated': [],
            'errors': []
        }
        
        approved = change_set.approved_changes
        if not approved:
            self.log("   ℹ No approved changes to apply")
            results['success'] = True
            return results
        
        # Separate contact and biographic changes
        contact_updates = {}
        biographic_updates = {}
        
        for change in approved:
            if not change.infotems_field:
                continue
            
            if change.is_biographic:
                biographic_updates[change.infotems_field] = change.new_value
            else:
                contact_updates[change.infotems_field] = change.new_value
        
        try:
            # Create new contact if needed
            if not change_set.contact_id:
                self.log("   Creating new contact...")
                
                # Need at least first and last name
                first_name = contact_updates.pop('FirstName', None)
                last_name = contact_updates.pop('LastName', None)
                
                if not first_name or not last_name:
                    results['errors'].append("Cannot create contact: First and Last name required")
                    return results
                
                new_id = self.client.create_contact(
                    first_name=first_name,
                    last_name=last_name,
                    **contact_updates
                )
                
                change_set.contact_id = new_id
                results['contact_id'] = new_id
                results['contact_created'] = True
                self.log(f"   ✓ Created contact ID: {new_id}")
                
                # Clear contact updates since they were applied during creation
                contact_updates = {}
            
            # Update contact fields
            if contact_updates and change_set.contact_id:
                self.log(f"   Updating contact {change_set.contact_id}...")
                self.client.update_contact(change_set.contact_id, contact_updates)
                results['contact_updated'] = True
                results['fields_updated'].extend(contact_updates.keys())
                self.log(f"   ✓ Updated {len(contact_updates)} contact fields")
            
            # Update biographic fields
            if biographic_updates and change_set.contact_id:
                if change_set.biographic_id:
                    self.log(f"   Updating biographic {change_set.biographic_id}...")
                    self.client.update_contact_biographic(
                        change_set.biographic_id, 
                        biographic_updates
                    )
                else:
                    self.log(f"   Creating biographic for contact {change_set.contact_id}...")
                    result = self.client.create_contact_biographic(
                        change_set.contact_id,
                        **biographic_updates
                    )
                    change_set.biographic_id = result.get('Id')
                
                results['biographic_updated'] = True
                results['fields_updated'].extend(biographic_updates.keys())
                self.log(f"   ✓ Updated {len(biographic_updates)} biographic fields")
            
            results['success'] = True
            self.log(f"\n   ✅ All changes applied successfully")
            
        except Exception as e:
            results['errors'].append(str(e))
            self.log(f"   ❌ Error applying changes: {e}")
        
        return results


# ============================================================================
# STANDALONE TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("INFOTEMS COMPARATOR - TEST MODE")
    print("="*60)
    
    try:
        comparator = InfotemsComparator(verbose=True)
        
        # Test contact lookup
        print("\n--- Testing Contact Lookup ---")
        contact = comparator.find_contact(a_number="A216207999")
        
        if contact:
            print(f"\nFound contact: {contact.get('DisplayAs')}")
            print(f"  ID: {contact.get('Id')}")
            print(f"  Email: {contact.get('EmailPersonal')}")
            print(f"  Phone: {contact.get('CellPhone')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
