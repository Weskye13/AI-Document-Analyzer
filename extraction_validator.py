"""
AI Document Analyzer - Extraction Validator
============================================

Validates extracted data for logical consistency.
Runs BEFORE InfoTems comparison to catch AI extraction errors.

Inspired by Ralph Brainstormer's "Debate & Consensus" pattern:
- Multiple validation rules act as "critics"
- Errors are flagged for re-extraction or human review

Author: Law Office of Joshua E. Bardavid
Version: 1.0.0
Date: January 2026
"""

import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    ERROR = 'error'        # Must be fixed
    WARNING = 'warning'    # Should review
    INFO = 'info'          # FYI only


@dataclass
class ValidationError:
    """Represents a validation error or warning."""
    rule_name: str
    severity: ValidationSeverity
    message: str
    field_key: Optional[str] = None
    current_value: Any = None
    suggested_value: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_name': self.rule_name,
            'severity': self.severity.value,
            'message': self.message,
            'field_key': self.field_key,
            'current_value': self.current_value,
            'suggested_value': self.suggested_value,
        }


@dataclass
class ValidationResult:
    """Result of validation run."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    
    @property
    def error_count(self) -> int:
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        return len(self.warnings)
    
    @property
    def all_issues(self) -> List[ValidationError]:
        return self.errors + self.warnings + self.info
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'info': [i.to_dict() for i in self.info],
        }


class ExtractionValidator:
    """
    Validates extracted document data for logical consistency.
    
    Acts as a "Ruthless Judge" (Ralph Brainstormer pattern) to catch:
    - Logical inconsistencies (DOB vs age, impossible dates)
    - Format errors (A-numbers, phone numbers, dates)
    - Missing required fields for document type
    - Low confidence extractions
    """
    
    # A-number pattern: 9 digits, optionally prefixed with 'A'
    A_NUMBER_PATTERN = re.compile(r'^A?(\d{8,9})$', re.IGNORECASE)
    
    # Date patterns
    DATE_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}$',           # ISO: 2024-01-15
        r'^\d{2}/\d{2}/\d{4}$',           # US: 01/15/2024
        r'^\d{2}-\d{2}-\d{4}$',           # US alt: 01-15-2024
        r'^\d{1,2}/\d{1,2}/\d{4}$',       # US loose: 1/5/2024
    ]
    
    # Phone pattern (US)
    PHONE_PATTERN = re.compile(r'^[\d\s\-\(\)\.]+$')
    
    # Required fields by document type
    REQUIRED_FIELDS = {
        'questionnaire_589': ['first_name', 'last_name', 'date_of_birth', 'country_of_birth'],
        'questionnaire_i485': ['first_name', 'last_name', 'date_of_birth', 'a_number'],
        'questionnaire_n400': ['first_name', 'last_name', 'date_of_birth', 'a_number', 'green_card_number'],
        'questionnaire_consult': ['first_name', 'last_name'],
        'passport': ['first_name', 'last_name', 'date_of_birth', 'passport_number', 'country'],
        'ead_card': ['first_name', 'last_name', 'a_number', 'category'],
        'green_card': ['first_name', 'last_name', 'a_number'],
    }
    
    # Fields that should contain dates
    DATE_FIELDS = [
        'date_of_birth', 'date_of_entry', 'date_of_marriage', 'date_marriage_ended',
        'passport_expiration', 'ead_expiration', 'green_card_expiration',
        'from_date', 'to_date', 'start_date', 'end_date',
    ]
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def log(self, message: str):
        if self.verbose:
            print(f"  [Validator] {message}")
    
    def validate(self, extracted: Dict[str, Any]) -> ValidationResult:
        """
        Run all validation rules on extracted data.
        
        Args:
            extracted: The extraction result from DocumentExtractor
            
        Returns:
            ValidationResult with all errors/warnings
        """
        result = ValidationResult(is_valid=True)
        
        doc_type = extracted.get('document_type', 'unknown')
        fields = extracted.get('fields', {})
        family_members = extracted.get('family_members', [])
        history = extracted.get('history', {})
        
        # Run all validation rules
        self._validate_required_fields(doc_type, fields, result)
        self._validate_a_number(fields, result)
        self._validate_dates(fields, result)
        self._validate_date_consistency(fields, result)
        self._validate_name_fields(fields, result)
        self._validate_confidence_scores(extracted, result)
        self._validate_family_members(family_members, result)
        self._validate_history_records(history, result)
        
        # Set overall validity
        result.is_valid = len(result.errors) == 0
        
        self.log(f"Validation complete: {result.error_count} errors, {result.warning_count} warnings")
        
        return result
    
    def _validate_required_fields(self, doc_type: str, fields: Dict, result: ValidationResult):
        """Check that required fields for document type are present."""
        required = self.REQUIRED_FIELDS.get(doc_type, [])
        
        for field_key in required:
            field_data = fields.get(field_key)
            if not field_data:
                result.warnings.append(ValidationError(
                    rule_name='required_field_missing',
                    severity=ValidationSeverity.WARNING,
                    message=f"Required field '{field_key}' not found",
                    field_key=field_key,
                ))
            elif isinstance(field_data, dict):
                value = field_data.get('value')
                if not value or str(value).strip() == '':
                    result.warnings.append(ValidationError(
                        rule_name='required_field_empty',
                        severity=ValidationSeverity.WARNING,
                        message=f"Required field '{field_key}' is empty",
                        field_key=field_key,
                    ))
    
    def _validate_a_number(self, fields: Dict, result: ValidationResult):
        """Validate A-number format."""
        a_number_field = fields.get('a_number')
        if not a_number_field:
            return
        
        value = a_number_field.get('value') if isinstance(a_number_field, dict) else a_number_field
        if not value:
            return
        
        value = str(value).strip().replace(' ', '').replace('-', '')
        
        match = self.A_NUMBER_PATTERN.match(value)
        if not match:
            result.errors.append(ValidationError(
                rule_name='invalid_a_number',
                severity=ValidationSeverity.ERROR,
                message=f"Invalid A-number format: '{value}'. Expected 8-9 digits.",
                field_key='a_number',
                current_value=value,
            ))
        else:
            # Normalize to 9 digits
            digits = match.group(1)
            if len(digits) == 8:
                result.info.append(ValidationError(
                    rule_name='a_number_format',
                    severity=ValidationSeverity.INFO,
                    message=f"A-number has 8 digits, may need leading zero",
                    field_key='a_number',
                    current_value=value,
                    suggested_value=f"A{digits.zfill(9)}",
                ))
    
    def _validate_dates(self, fields: Dict, result: ValidationResult):
        """Validate date fields have proper format."""
        for field_key in self.DATE_FIELDS:
            field_data = fields.get(field_key)
            if not field_data:
                continue
            
            value = field_data.get('value') if isinstance(field_data, dict) else field_data
            if not value:
                continue
            
            value = str(value).strip()
            
            # Check if matches any valid pattern
            is_valid = False
            for pattern in self.DATE_PATTERNS:
                if re.match(pattern, value):
                    is_valid = True
                    break
            
            if not is_valid:
                result.warnings.append(ValidationError(
                    rule_name='invalid_date_format',
                    severity=ValidationSeverity.WARNING,
                    message=f"Date field '{field_key}' has non-standard format: '{value}'",
                    field_key=field_key,
                    current_value=value,
                ))
    
    def _validate_date_consistency(self, fields: Dict, result: ValidationResult):
        """Check logical consistency between dates."""
        
        def parse_date(value) -> Optional[date]:
            """Try to parse a date value."""
            if not value:
                return None
            if isinstance(value, dict):
                value = value.get('value')
            if not value:
                return None
            value = str(value).strip()
            
            # Try different formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return None
        
        dob = parse_date(fields.get('date_of_birth'))
        entry_date = parse_date(fields.get('date_of_entry'))
        marriage_date = parse_date(fields.get('date_of_marriage'))
        today = date.today()
        
        # DOB should be in the past
        if dob and dob > today:
            result.errors.append(ValidationError(
                rule_name='future_dob',
                severity=ValidationSeverity.ERROR,
                message="Date of birth is in the future",
                field_key='date_of_birth',
                current_value=str(dob),
            ))
        
        # DOB should be reasonable (not > 120 years ago)
        if dob and (today.year - dob.year) > 120:
            result.errors.append(ValidationError(
                rule_name='unreasonable_dob',
                severity=ValidationSeverity.ERROR,
                message="Date of birth is more than 120 years ago",
                field_key='date_of_birth',
                current_value=str(dob),
            ))
        
        # Entry date should be after DOB
        if dob and entry_date and entry_date < dob:
            result.errors.append(ValidationError(
                rule_name='entry_before_birth',
                severity=ValidationSeverity.ERROR,
                message="Date of entry is before date of birth",
                field_key='date_of_entry',
                current_value=str(entry_date),
            ))
        
        # Marriage date should be after DOB (and person should be at least 14)
        if dob and marriage_date:
            if marriage_date < dob:
                result.errors.append(ValidationError(
                    rule_name='marriage_before_birth',
                    severity=ValidationSeverity.ERROR,
                    message="Marriage date is before date of birth",
                    field_key='date_of_marriage',
                    current_value=str(marriage_date),
                ))
            elif (marriage_date.year - dob.year) < 14:
                result.warnings.append(ValidationError(
                    rule_name='marriage_too_young',
                    severity=ValidationSeverity.WARNING,
                    message="Person was under 14 at marriage date",
                    field_key='date_of_marriage',
                    current_value=str(marriage_date),
                ))
    
    def _validate_name_fields(self, fields: Dict, result: ValidationResult):
        """Validate name fields for common issues."""
        name_fields = ['first_name', 'last_name', 'middle_name']
        
        for field_key in name_fields:
            field_data = fields.get(field_key)
            if not field_data:
                continue
            
            value = field_data.get('value') if isinstance(field_data, dict) else field_data
            if not value:
                continue
            
            value = str(value).strip()
            
            # Check for numbers in name
            if re.search(r'\d', value):
                result.warnings.append(ValidationError(
                    rule_name='name_contains_numbers',
                    severity=ValidationSeverity.WARNING,
                    message=f"Name field '{field_key}' contains numbers: '{value}'",
                    field_key=field_key,
                    current_value=value,
                ))
            
            # Check for all caps (might need title case)
            if value.isupper() and len(value) > 2:
                result.info.append(ValidationError(
                    rule_name='name_all_caps',
                    severity=ValidationSeverity.INFO,
                    message=f"Name field '{field_key}' is all caps",
                    field_key=field_key,
                    current_value=value,
                    suggested_value=value.title(),
                ))
            
            # Check for swapped first/last names (common OCR error)
            first = fields.get('first_name', {})
            last = fields.get('last_name', {})
            first_val = first.get('value') if isinstance(first, dict) else first
            last_val = last.get('value') if isinstance(last, dict) else last
            
            if first_val and last_val:
                # If last name is shorter than first and looks like a first name
                if len(str(last_val)) < 3 and len(str(first_val)) > 5:
                    result.info.append(ValidationError(
                        rule_name='possible_name_swap',
                        severity=ValidationSeverity.INFO,
                        message="First and last names may be swapped",
                        field_key='first_name',
                        current_value=f"{first_val} {last_val}",
                        suggested_value=f"{last_val} {first_val}",
                    ))
    
    def _validate_confidence_scores(self, extracted: Dict, result: ValidationResult):
        """Flag low confidence extractions."""
        fields = extracted.get('fields', {})
        
        low_confidence_fields = []
        for field_key, field_data in fields.items():
            if isinstance(field_data, dict):
                confidence = field_data.get('confidence', 1.0)
                if confidence < 0.7:
                    low_confidence_fields.append((field_key, confidence))
        
        if low_confidence_fields:
            for field_key, confidence in low_confidence_fields:
                result.warnings.append(ValidationError(
                    rule_name='low_confidence',
                    severity=ValidationSeverity.WARNING,
                    message=f"Low confidence ({confidence:.0%}) on field '{field_key}'",
                    field_key=field_key,
                    current_value=confidence,
                ))
    
    def _validate_family_members(self, family_members: List[Dict], result: ValidationResult):
        """Validate family member data."""
        for i, fm in enumerate(family_members):
            relationship = fm.get('relationship', 'unknown')
            data = fm.get('data', {})
            confidence = fm.get('confidence', 1.0)
            
            # Check required fields for family members
            if not data.get('first_name') and not data.get('last_name'):
                result.warnings.append(ValidationError(
                    rule_name='family_member_no_name',
                    severity=ValidationSeverity.WARNING,
                    message=f"Family member {i+1} ({relationship}) has no name",
                    field_key=f'family_members[{i}]',
                ))
            
            # Check confidence
            if confidence < 0.7:
                result.warnings.append(ValidationError(
                    rule_name='family_member_low_confidence',
                    severity=ValidationSeverity.WARNING,
                    message=f"Low confidence ({confidence:.0%}) on family member: {relationship}",
                    field_key=f'family_members[{i}]',
                    current_value=confidence,
                ))
    
    def _validate_history_records(self, history: Dict, result: ValidationResult):
        """Validate history records."""
        for history_type, records in history.items():
            if not isinstance(records, list):
                continue
            
            for i, record in enumerate(records):
                data = record.get('data', {})
                confidence = record.get('confidence', 1.0)
                
                # Check for empty records
                if not data or all(not v for v in data.values()):
                    result.info.append(ValidationError(
                        rule_name='empty_history_record',
                        severity=ValidationSeverity.INFO,
                        message=f"Empty {history_type} record at index {i}",
                        field_key=f'history.{history_type}[{i}]',
                    ))
                
                # Check confidence
                if confidence < 0.7:
                    result.warnings.append(ValidationError(
                        rule_name='history_low_confidence',
                        severity=ValidationSeverity.WARNING,
                        message=f"Low confidence ({confidence:.0%}) on {history_type} record {i+1}",
                        field_key=f'history.{history_type}[{i}]',
                        current_value=confidence,
                    ))


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXTRACTION VALIDATOR - TEST MODE")
    print("="*60)
    
    # Test with sample data
    test_data = {
        'document_type': 'questionnaire_589',
        'confidence': 0.85,
        'fields': {
            'first_name': {'value': 'JOHN', 'confidence': 0.95},
            'last_name': {'value': 'DOE', 'confidence': 0.9},
            'date_of_birth': {'value': '1990-15-01', 'confidence': 0.6},  # Invalid date
            'a_number': {'value': 'A12345678', 'confidence': 0.8},
            'date_of_entry': {'value': '1985-01-01', 'confidence': 0.7},  # Before DOB!
        },
        'family_members': [
            {'relationship': 'spouse', 'data': {'first_name': 'Jane'}, 'confidence': 0.5},
            {'relationship': 'child', 'data': {}, 'confidence': 0.9},  # No name
        ],
        'history': {
            'address': [
                {'data': {'city': 'New York'}, 'confidence': 0.4},
            ]
        }
    }
    
    validator = ExtractionValidator(verbose=True)
    result = validator.validate(test_data)
    
    print(f"\n{'='*60}")
    print(f"VALIDATION RESULT: {'PASS' if result.is_valid else 'FAIL'}")
    print(f"{'='*60}")
    print(f"Errors: {result.error_count}")
    for e in result.errors:
        print(f"  ❌ [{e.rule_name}] {e.message}")
    print(f"\nWarnings: {result.warning_count}")
    for w in result.warnings:
        print(f"  ⚠️ [{w.rule_name}] {w.message}")
    print(f"\nInfo: {len(result.info)}")
    for i in result.info:
        print(f"  ℹ️ [{i.rule_name}] {i.message}")
