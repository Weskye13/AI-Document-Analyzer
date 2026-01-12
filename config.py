"""
AI Document Analyzer - Configuration
=====================================

Central configuration for the document analyzer system.
Handles credentials, paths, and document type definitions.

Author: Law Office of Joshua E. Bardavid
Version: 1.0.0
Date: January 2026
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# PATHS
# ============================================================================

# Script directory
SCRIPT_DIR = Path(__file__).parent

# InfoTems API paths (try multiple locations)
INFOTEMS_API_PATHS = [
    r'W:\Work\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API',
    r'C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API',
]

# Client folders base paths
CLIENT_FOLDER_BASES = [
    r'W:\Work\Dropbox\Law Office of Joshua E. Bardavid\Clients',
    r'C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Clients',
]

# Metadata file paths
METADATA_PATHS = [
    r'W:\Work\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\File MetaData\unified_client_metadata.json',
    r'C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\File MetaData\unified_client_metadata.json',
]

def get_first_existing_path(paths):
    """Return first path that exists from a list."""
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0] if paths else None

# Active paths
INFOTEMS_API_PATH = get_first_existing_path(INFOTEMS_API_PATHS)
CLIENT_FOLDER_BASE = get_first_existing_path(CLIENT_FOLDER_BASES)
METADATA_PATH = get_first_existing_path(METADATA_PATHS)

# Add InfoTems API to path
if INFOTEMS_API_PATH:
    sys.path.insert(0, INFOTEMS_API_PATH)

# ============================================================================
# CREDENTIALS
# ============================================================================

# InfoTems credentials
INFOTEMS_USERNAME = os.getenv('INFOTEMS_USERNAME')
INFOTEMS_PASSWORD = os.getenv('INFOTEMS_PASSWORD')
INFOTEMS_API_KEY = os.getenv('INFOTEMS_API_KEY')

# Anthropic API key
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# ============================================================================
# AI MODEL SETTINGS
# ============================================================================

AI_CONFIG = {
    'model': 'claude-sonnet-4-20250514',  # Best balance of speed and accuracy
    'max_tokens': 4096,
    'temperature': 0.0,  # Deterministic for data extraction
}

# ============================================================================
# DOCUMENT TYPE DEFINITIONS
# ============================================================================

# Document types and their expected extractable fields
DOCUMENT_TYPES = {
    'questionnaire': {
        'display_name': 'Client Questionnaire',
        'description': 'Immigration questionnaire with biographical data',
        'fields': [
            # Personal Info
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'place_of_birth', 'label': 'Place of Birth', 'infotems_field': 'BirthCity'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry'},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender'},
            {'key': 'marital_status', 'label': 'Marital Status', 'infotems_field': 'MaritalStatus'},
            {'key': 'nationality', 'label': 'Nationality/Citizenship', 'infotems_field': 'Citizenship1Country'},
            
            # Contact Info
            {'key': 'cell_phone', 'label': 'Cell Phone', 'infotems_field': 'CellPhone'},
            {'key': 'home_phone', 'label': 'Home Phone', 'infotems_field': 'HomePhone'},
            {'key': 'email', 'label': 'Email', 'infotems_field': 'EmailPersonal'},
            
            # Address
            {'key': 'address_line1', 'label': 'Address Line 1', 'infotems_field': 'AddressLine1'},
            {'key': 'address_line2', 'label': 'Address Line 2', 'infotems_field': 'AddressLine2'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            
            # Immigration Info
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'date_of_entry', 'label': 'Date of Entry to US', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'immigration_status', 'label': 'Immigration Status', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
            {'key': 'native_language', 'label': 'Native Language', 'infotems_field': 'NativeLanguage', 'biographic': True},
            
            # Employment
            {'key': 'employer', 'label': 'Employer', 'infotems_field': 'Employer'},
            {'key': 'occupation', 'label': 'Occupation', 'infotems_field': 'Occupation'},
        ]
    },
    
    'passport': {
        'display_name': 'Passport',
        'description': 'Foreign passport document',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'place_of_birth', 'label': 'Place of Birth', 'infotems_field': 'BirthCity'},
            {'key': 'nationality', 'label': 'Nationality', 'infotems_field': 'Citizenship1Country'},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender'},
            {'key': 'passport_number', 'label': 'Passport Number', 'document_field': True},
            {'key': 'issue_date', 'label': 'Issue Date', 'document_field': True, 'type': 'date'},
            {'key': 'expiration_date', 'label': 'Expiration Date', 'document_field': True, 'type': 'date'},
            {'key': 'issuing_country', 'label': 'Issuing Country', 'document_field': True},
        ]
    },
    
    'ead_card': {
        'display_name': 'Employment Authorization Document',
        'description': 'EAD/Work Permit card',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry'},
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'uscis_number', 'label': 'USCIS Number', 'document_field': True},
            {'key': 'category', 'label': 'Category', 'document_field': True},
            {'key': 'card_expires', 'label': 'Card Expires', 'document_field': True, 'type': 'date'},
        ]
    },
    
    'green_card': {
        'display_name': 'Permanent Resident Card',
        'description': 'Green Card / PR Card',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry'},
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'uscis_number', 'label': 'USCIS Number', 'document_field': True},
            {'key': 'category', 'label': 'Category', 'document_field': True},
            {'key': 'resident_since', 'label': 'Resident Since', 'document_field': True, 'type': 'date'},
            {'key': 'card_expires', 'label': 'Card Expires', 'document_field': True, 'type': 'date'},
        ]
    },
    
    'birth_certificate': {
        'display_name': 'Birth Certificate',
        'description': 'Foreign or US birth certificate',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'place_of_birth', 'label': 'Place of Birth', 'infotems_field': 'BirthCity'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry'},
            {'key': 'father_name', 'label': 'Father\'s Name', 'document_field': True},
            {'key': 'mother_name', 'label': 'Mother\'s Name', 'document_field': True},
        ]
    },
    
    'id_card': {
        'display_name': 'ID Card',
        'description': 'State ID, Driver\'s License, or foreign ID',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'address_line1', 'label': 'Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'id_number', 'label': 'ID Number', 'document_field': True},
            {'key': 'issue_date', 'label': 'Issue Date', 'document_field': True, 'type': 'date'},
            {'key': 'expiration_date', 'label': 'Expiration Date', 'document_field': True, 'type': 'date'},
        ]
    },
    
    'i94': {
        'display_name': 'I-94 Arrival/Departure Record',
        'description': 'USCIS I-94 form',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'type': 'date'},
            {'key': 'country_of_citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country'},
            {'key': 'passport_number', 'label': 'Passport Number', 'document_field': True},
            {'key': 'date_of_entry', 'label': 'Date of Entry', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'class_of_admission', 'label': 'Class of Admission', 'document_field': True},
            {'key': 'admit_until', 'label': 'Admit Until Date', 'document_field': True, 'type': 'date'},
            {'key': 'i94_number', 'label': 'I-94 Number', 'document_field': True},
        ]
    },
}

# ============================================================================
# FIELD MAPPINGS FOR UPDATES
# ============================================================================

# Fields that go in Contact vs ContactBiographic
CONTACT_FIELDS = [
    'FirstName', 'MiddleName', 'LastName', 'Suffix',
    'CellPhone', 'HomePhone', 'WorkPhone', 'EmailPersonal', 'EmailWork',
    'AddressLine1', 'AddressLine2', 'City', 'State', 'PostalZipCode',
    'Employer', 'Occupation',
]

BIOGRAPHIC_FIELDS = [
    'AlienNumber', 'BirthDate', 'BirthCity', 'BirthState', 'BirthCountry',
    'Gender', 'MaritalStatus', 'NativeLanguage',
    'Citizenship1Country', 'Citizenship2Country',
    'CurrentImmigrationStatus', 'DateOfEntryToUsa',
    'SSN',
]

# ============================================================================
# UI SETTINGS
# ============================================================================

UI_CONFIG = {
    'window_title': 'AI Document Analyzer',
    'window_size': '1400x900',
    'log_font': ('Consolas', 9),
    'header_font': ('Arial', 14, 'bold'),
}

# Change indicator colors
CHANGE_COLORS = {
    'new': '#4CAF50',       # Green - new value being added
    'modified': '#FF9800',  # Orange - value being changed
    'removed': '#F44336',   # Red - value being removed
    'unchanged': '#9E9E9E', # Gray - no change
}
