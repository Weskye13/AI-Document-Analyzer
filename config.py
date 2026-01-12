"""
AI Document Analyzer - Configuration
=====================================

Central configuration for the document analyzer system.
Handles credentials, paths, and document type definitions.

Author: Law Office of Joshua E. Bardavid
Version: 2.0.0
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
# QUESTIONNAIRE DEFINITIONS (HARDCODED MAPPINGS)
# ============================================================================

# Questionnaire types with their detection patterns and field mappings
QUESTIONNAIRE_TYPES = {
    'consult_questionnaire': {
        'display_name': 'Consultation Questionnaire',
        'description': 'Initial consultation intake form',
        'detection_patterns': [
            'Pre-Consultation Questionnaire',
            'Consult Questionnaire',
            'Cuestionario de Consulta',
        ],
        'languages': ['English', 'Spanish', 'Creole'],
        'fields': [
            # Personal Info
            {'key': 'last_name', 'label': 'Last (family) name', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'First (given) name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle name', 'infotems_field': 'MiddleName'},
            {'key': 'date_of_birth', 'label': 'Date of birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            # Address
            {'key': 'address_line1', 'label': 'Street Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'Zip', 'infotems_field': 'PostalZipCode'},
            # Contact
            {'key': 'phone', 'label': 'Phone number(s)', 'infotems_field': 'CellPhone'},
            {'key': 'email', 'label': 'Email address', 'infotems_field': 'EmailPersonal'},
            # Immigration
            {'key': 'a_number', 'label': 'Alien number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'immigration_status', 'label': 'Current immigration status', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
            {'key': 'date_of_entry', 'label': 'Date of entry into the United States', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'native_language', 'label': 'Primary/Best language', 'infotems_field': 'NativeLanguage', 'biographic': True},
            # Info Only (extracted but not mapped)
            {'key': 'manner_of_entry', 'label': 'Manner of entry', 'info_only': True},
            {'key': 'family_members_entered', 'label': 'Family members entered with', 'info_only': True},
            {'key': 'ice_encounters', 'label': 'ICE/DHS encounters', 'info_only': True},
            {'key': 'prior_removals', 'label': 'Prior entries/removals', 'info_only': True},
            {'key': 'harm_in_country', 'label': 'Harmed in country', 'info_only': True},
            {'key': 'fear_in_country', 'label': 'Fear of harm', 'info_only': True},
            {'key': 'prior_asylum', 'label': 'Prior asylum application', 'info_only': True},
            {'key': 'us_relatives', 'label': 'US relatives', 'info_only': True},
            {'key': 'removal_proceedings', 'label': 'Removal proceedings info', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Criminal history', 'info_only': True},
            {'key': 'prior_applications', 'label': 'Previous immigration applications', 'info_only': True},
        ]
    },
    
    'asylum_questionnaire': {
        'display_name': 'I-589 Asylum Questionnaire',
        'description': 'Asylum application questionnaire',
        'detection_patterns': [
            'Questionnaire for Asylum',
            'Cuestionario para el asilo',
            'Form I-589',
            '589 Questionnaire',
        ],
        'languages': ['English', 'Spanish', 'French', 'Chinese', 'Russian', 'Haitian Creole'],
        'fields': [
            # Section 1: Personal and Contact Info
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'ssn', 'label': 'U.S. Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
            {'key': 'last_name', 'label': 'Last (Family) Name', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'First (Given) Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'other_names', 'label': 'Other names used', 'info_only': True},
            {'key': 'in_care_of', 'label': 'In Care Of Name', 'info_only': True},
            {'key': 'address_line1', 'label': 'Street Number and Name', 'infotems_field': 'AddressLine1'},
            {'key': 'address_line2', 'label': 'Apartment, Suite, Floor', 'infotems_field': 'AddressLine2'},
            {'key': 'city', 'label': 'City or Town', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            # Section 2: Personal Background
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'City of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'state_of_birth', 'label': 'State/Province of Birth', 'infotems_field': 'BirthState', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'citizenship', 'label': 'Country of Citizenship or Nationality', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'ethnicity', 'label': 'Ethnicity', 'info_only': True},
            {'key': 'race', 'label': 'Race', 'info_only': True},
            {'key': 'religion', 'label': 'Religion', 'info_only': True},
            {'key': 'height', 'label': 'Height', 'info_only': True},
            {'key': 'weight', 'label': 'Weight', 'info_only': True},
            {'key': 'eye_color', 'label': 'Eye Color', 'info_only': True},
            {'key': 'hair_color', 'label': 'Hair Color', 'info_only': True},
            {'key': 'native_language', 'label': 'Best/first language', 'infotems_field': 'NativeLanguage', 'biographic': True},
            {'key': 'english_fluent', 'label': 'English fluency', 'info_only': True},
            {'key': 'other_languages', 'label': 'Other languages', 'info_only': True},
            {'key': 'passport_country', 'label': 'Passport issuing country', 'info_only': True},
            {'key': 'passport_number', 'label': 'Passport number', 'info_only': True},
            {'key': 'passport_issue_date', 'label': 'Passport issue date', 'info_only': True, 'type': 'date'},
            {'key': 'passport_expiry_date', 'label': 'Passport expiry date', 'info_only': True, 'type': 'date'},
            # Section 3: Travel History
            {'key': 'immigration_status_at_entry', 'label': 'Immigration status at last entry', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
            {'key': 'date_of_entry', 'label': 'Date of Entry', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'port_of_entry', 'label': 'Place or Port-of-Entry', 'info_only': True},
            {'key': 'state_of_entry', 'label': 'State of Entry', 'info_only': True},
            {'key': 'prior_entries', 'label': 'Prior US entries', 'info_only': True},
            # Section 4: Family Information
            {'key': 'marital_status', 'label': 'Relationship status', 'infotems_field': 'MaritalStatus', 'biographic': True},
            {'key': 'spouse_info', 'label': 'Spouse information', 'info_only': True, 'family_member': 'spouse'},
            {'key': 'children_info', 'label': 'Children information', 'info_only': True, 'family_member': 'children'},
            {'key': 'father_info', 'label': 'Father information', 'info_only': True, 'family_member': 'father'},
            {'key': 'mother_info', 'label': 'Mother information', 'info_only': True, 'family_member': 'mother'},
            # Employment (current only)
            {'key': 'employer', 'label': 'Current Employer', 'infotems_field': 'Employer'},
            {'key': 'occupation', 'label': 'Job title', 'infotems_field': 'Occupation'},
            # Info Only sections
            {'key': 'address_history', 'label': 'Address history', 'info_only': True},
            {'key': 'employment_history', 'label': 'Employment history', 'info_only': True},
            {'key': 'education_history', 'label': 'Education history', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Criminal/arrest history', 'info_only': True},
            {'key': 'removal_proceedings', 'label': 'Prior removal proceedings', 'info_only': True},
            {'key': 'false_info_given', 'label': 'False information given', 'info_only': True},
            {'key': 'military_training', 'label': 'Military/weapons training', 'info_only': True},
        ]
    },
    
    'n400_questionnaire': {
        'display_name': 'N-400 Naturalization Questionnaire',
        'description': 'Citizenship application questionnaire',
        'detection_patterns': [
            'N-400 Naturalization',
            'N400 questionnaire',
            'Cuestionario N-400',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'last_name', 'label': 'Family Name (Last Name)', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'Given Name (First Name)', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'other_names', 'label': 'Other names used', 'info_only': True},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'date_became_lpr', 'label': 'Date became LPR', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'marital_status', 'label': 'Marital Status', 'infotems_field': 'MaritalStatus', 'biographic': True},
            {'key': 'num_marriages', 'label': 'Number of marriages', 'info_only': True},
            {'key': 'spouse_info', 'label': 'Current spouse information', 'info_only': True, 'family_member': 'spouse'},
            {'key': 'prior_spouse_info', 'label': 'Prior spouse information', 'info_only': True},
            {'key': 'employer', 'label': 'Current Employer/School', 'infotems_field': 'Employer'},
            {'key': 'occupation', 'label': 'Occupation', 'infotems_field': 'Occupation'},
            {'key': 'employment_history', 'label': 'Employment history', 'info_only': True},
            {'key': 'travel_history', 'label': 'Travel history (5 years)', 'info_only': True},
            {'key': 'children_info', 'label': 'Children information', 'info_only': True, 'family_member': 'children'},
            {'key': 'claimed_us_citizen', 'label': 'Claimed US citizenship', 'info_only': True},
            {'key': 'voted_in_us', 'label': 'Voted in US elections', 'info_only': True},
            {'key': 'tax_issues', 'label': 'Tax filing issues', 'info_only': True},
            {'key': 'child_support_issues', 'label': 'Child support issues', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Arrest/criminal history', 'info_only': True},
        ]
    },
    
    'i130_petitioner_questionnaire': {
        'display_name': 'I-130 Petitioner Questionnaire',
        'description': 'Family petition questionnaire for USC/LPR petitioner',
        'detection_patterns': [
            'I-130 Questionnaire for the USC/LPR Petitioner',
            'I-130 Questionnaire Petitioner',
            'USC Petitioner Questionnaire',
            'Cuestionario del Peticionario',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'last_name', 'label': 'Family name', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'Given name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle name', 'infotems_field': 'MiddleName'},
            {'key': 'maiden_name', 'label': 'Maiden name', 'info_only': True},
            {'key': 'nickname', 'label': 'Nickname', 'info_only': True},
            {'key': 'cell_phone', 'label': 'Mobile/Cell Phone', 'infotems_field': 'CellPhone'},
            {'key': 'home_phone', 'label': 'Home Phone', 'infotems_field': 'HomePhone'},
            {'key': 'work_phone', 'label': 'Work Phone', 'infotems_field': 'WorkPhone'},
            {'key': 'email', 'label': 'Email Address', 'infotems_field': 'EmailPersonal'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'Birthplace City', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'state_of_birth', 'label': 'Birthplace State', 'infotems_field': 'BirthState', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Birthplace Country', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'ssn', 'label': 'Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'ethnicity', 'label': 'Ethnicity', 'info_only': True},
            {'key': 'race', 'label': 'Race', 'info_only': True},
            {'key': 'height', 'label': 'Height', 'info_only': True},
            {'key': 'weight', 'label': 'Weight', 'info_only': True},
            {'key': 'eye_color', 'label': 'Eye Color', 'info_only': True},
            {'key': 'hair_color', 'label': 'Hair Color', 'info_only': True},
            {'key': 'marital_status', 'label': 'Marital Status', 'infotems_field': 'MaritalStatus', 'biographic': True},
            {'key': 'date_of_marriage', 'label': 'Date of Marriage', 'info_only': True, 'type': 'date'},
            {'key': 'place_of_marriage', 'label': 'Place of Marriage', 'info_only': True},
            {'key': 'prior_marriages', 'label': 'Previous marriages', 'info_only': True},
            {'key': 'father_info', 'label': 'Father information', 'info_only': True, 'family_member': 'father'},
            {'key': 'mother_info', 'label': 'Mother information', 'info_only': True, 'family_member': 'mother'},
            {'key': 'is_usc', 'label': 'Is U.S. Citizen', 'info_only': True},
            {'key': 'naturalization_info', 'label': 'Naturalization info', 'info_only': True},
            {'key': 'is_lpr', 'label': 'Is Permanent Resident', 'info_only': True},
            {'key': 'lpr_info', 'label': 'LPR info', 'info_only': True},
            {'key': 'employer', 'label': 'Current Employer', 'infotems_field': 'Employer'},
            {'key': 'occupation', 'label': 'Occupation', 'infotems_field': 'Occupation'},
            {'key': 'employment_history', 'label': 'Employment history', 'info_only': True},
            {'key': 'address_line1', 'label': 'Street Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'address_history', 'label': 'Address history', 'info_only': True},
            {'key': 'income', 'label': 'Current income', 'info_only': True},
            {'key': 'tax_returns', 'label': 'Tax return info', 'info_only': True},
            {'key': 'household_size', 'label': 'Household size', 'info_only': True},
            {'key': 'petition_relationship', 'label': 'Relationship to beneficiary', 'info_only': True},
            {'key': 'prior_petitions', 'label': 'Prior petitions filed', 'info_only': True},
        ]
    },
    
    'i130_beneficiary_questionnaire': {
        'display_name': 'I-130A Beneficiary Questionnaire',
        'description': 'Family petition questionnaire for foreign national beneficiary',
        'detection_patterns': [
            'I-130A Questionnaire for the Foreign National Beneficiary',
            'I-130A Questionnaire',
            'Beneficiary Questionnaire',
            'Cuestionario I130 para el beneficiary',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'father_info', 'label': 'Father information', 'info_only': True, 'family_member': 'father'},
            {'key': 'mother_info', 'label': 'Mother information', 'info_only': True, 'family_member': 'mother'},
            {'key': 'employer', 'label': 'Current Employer', 'infotems_field': 'Employer'},
            {'key': 'occupation', 'label': 'Occupation', 'infotems_field': 'Occupation'},
            {'key': 'employment_history', 'label': 'Employment history', 'info_only': True},
            {'key': 'address_line1', 'label': 'Current Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'address_history', 'label': 'Address history', 'info_only': True},
            {'key': 'last_foreign_address', 'label': 'Last foreign address', 'info_only': True},
            {'key': 'last_foreign_employment', 'label': 'Last foreign employment', 'info_only': True},
        ]
    },
    
    'adjustment_questionnaire': {
        'display_name': 'I-485 Adjustment Questionnaire',
        'description': 'Adjustment of Status questionnaire',
        'detection_patterns': [
            'Questionnaire for Form I-485',
            'Adjustment Questionnaire',
            'Cuestionario para el Formulario I-485',
            'Residencia Permanente',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'full_name', 'label': 'Name', 'infotems_field': None},  # Parse into components
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'other_names', 'label': 'Other names used', 'info_only': True},
            {'key': 'address_line1', 'label': 'Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'Zip Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'phone', 'label': 'Phone number', 'infotems_field': 'CellPhone'},
            {'key': 'email', 'label': 'Email address', 'infotems_field': 'EmailPersonal'},
            {'key': 'ssn', 'label': 'Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
            {'key': 'height', 'label': 'Height', 'info_only': True},
            {'key': 'weight', 'label': 'Weight', 'info_only': True},
            {'key': 'eye_color', 'label': 'Eye Color', 'info_only': True},
            {'key': 'hair_color', 'label': 'Hair Color', 'info_only': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'City of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'passport_number', 'label': 'Passport Number', 'info_only': True},
            {'key': 'arrest_history', 'label': 'Arrest history', 'info_only': True},
            {'key': 'date_of_entry', 'label': 'Date entered US', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'date_left_country', 'label': 'Date left home country', 'info_only': True, 'type': 'date'},
            {'key': 'countries_transited', 'label': 'Countries transited', 'info_only': True},
            {'key': 'prior_entries', 'label': 'Prior US entries', 'info_only': True},
            {'key': 'marital_status', 'label': 'Marital status', 'infotems_field': 'MaritalStatus', 'biographic': True},
            {'key': 'spouse_info', 'label': 'Spouse information', 'info_only': True, 'family_member': 'spouse'},
            {'key': 'children_info', 'label': 'Children information', 'info_only': True, 'family_member': 'children'},
            {'key': 'father_info', 'label': 'Father information', 'info_only': True, 'family_member': 'father'},
            {'key': 'mother_info', 'label': 'Mother information', 'info_only': True, 'family_member': 'mother'},
            {'key': 'address_history', 'label': 'Address history', 'info_only': True},
            {'key': 'employer', 'label': 'Current Employer', 'infotems_field': 'Employer'},
            {'key': 'occupation', 'label': 'Job Title/Position', 'infotems_field': 'Occupation'},
            {'key': 'employment_history', 'label': 'Employment history', 'info_only': True},
        ]
    },
    
    'ds260_questionnaire': {
        'display_name': 'DS-260 Immigrant Visa Questionnaire',
        'description': 'Immigrant Visa and Alien Registration Application questionnaire',
        'detection_patterns': [
            'DS-260',
            'DS260',
            'Immigrant Visa and Alien Registration',
            'Solicitud de Visa de Inmigrante',
        ],
        'languages': ['English', 'Spanish', 'Mandarin'],
        'fields': [
            {'key': 'full_name', 'label': 'Name Provided', 'infotems_field': None},
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'native_name', 'label': 'Full Name in Native Language', 'info_only': True},
            {'key': 'other_names', 'label': 'Other Names Used', 'info_only': True},
            {'key': 'gender', 'label': 'Sex', 'infotems_field': 'Gender', 'biographic': True},
            {'key': 'marital_status', 'label': 'Current Marital Status', 'infotems_field': 'MaritalStatus', 'biographic': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'City of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'state_of_birth', 'label': 'State/Province of Birth', 'infotems_field': 'BirthState', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'citizenship', 'label': 'Country of Nationality', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'passport_number', 'label': 'Passport Document ID', 'info_only': True},
            {'key': 'passport_country', 'label': 'Passport Issuing Country', 'info_only': True},
            {'key': 'passport_issue_date', 'label': 'Passport Issue Date', 'info_only': True, 'type': 'date'},
            {'key': 'passport_expiry_date', 'label': 'Passport Expiry Date', 'info_only': True, 'type': 'date'},
            {'key': 'other_nationality', 'label': 'Other Nationality', 'infotems_field': 'Citizenship2Country', 'biographic': True},
            {'key': 'address_line1', 'label': 'Present Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State/Province', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'Postal Zone/ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'address_history', 'label': 'Address history', 'info_only': True},
            {'key': 'cell_phone', 'label': 'Primary Phone Number', 'infotems_field': 'CellPhone'},
            {'key': 'home_phone', 'label': 'Secondary Phone Number', 'infotems_field': 'HomePhone'},
            {'key': 'work_phone', 'label': 'Work Phone Number', 'infotems_field': 'WorkPhone'},
            {'key': 'email', 'label': 'Email Address', 'infotems_field': 'EmailPersonal'},
            {'key': 'social_media', 'label': 'Social Media', 'info_only': True},
            {'key': 'father_info', 'label': 'Father information', 'info_only': True, 'family_member': 'father'},
            {'key': 'mother_info', 'label': 'Mother information', 'info_only': True, 'family_member': 'mother'},
            {'key': 'spouse_info', 'label': 'Spouse information', 'info_only': True, 'family_member': 'spouse'},
            {'key': 'prior_spouse_info', 'label': 'Prior spouse information', 'info_only': True},
            {'key': 'children_info', 'label': 'Children information', 'info_only': True, 'family_member': 'children'},
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'us_travel_history', 'label': 'US travel history', 'info_only': True},
            {'key': 'prior_visas', 'label': 'Prior US visas', 'info_only': True},
            {'key': 'visa_issues', 'label': 'Visa cancellation/revocation', 'info_only': True},
            {'key': 'occupation', 'label': 'Primary Occupation', 'infotems_field': 'Occupation'},
            {'key': 'employer', 'label': 'Present Employer or School', 'infotems_field': 'Employer'},
            {'key': 'countries_traveled', 'label': 'Countries traveled (5 years)', 'info_only': True},
            {'key': 'military_service', 'label': 'Military service', 'info_only': True},
            {'key': 'petitioner_info', 'label': 'Petitioner information', 'info_only': True},
        ]
    },
    
    'waiver_601a_questionnaire': {
        'display_name': 'I-601A Waiver Questionnaire',
        'description': 'Unlawful Presence Waiver questionnaire',
        'detection_patterns': [
            'Form I-601A Questionnaire',
            '601A Questionnaire',
            'Unlawful Presence Waiver',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'ssn', 'label': 'U.S. Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
            {'key': 'last_name', 'label': 'Last (Family) Name', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'First (Given) Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'other_names', 'label': 'Other names used', 'info_only': True},
            {'key': 'address_line1', 'label': 'Street Number and Name', 'infotems_field': 'AddressLine1'},
            {'key': 'address_line2', 'label': 'Apartment, Suite, Floor', 'infotems_field': 'AddressLine2'},
            {'key': 'city', 'label': 'City or Town', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'City of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'state_of_birth', 'label': 'State/Province of Birth', 'infotems_field': 'BirthState', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'ethnicity', 'label': 'Ethnicity', 'info_only': True},
            {'key': 'race', 'label': 'Race', 'info_only': True},
            {'key': 'height', 'label': 'Height', 'info_only': True},
            {'key': 'weight', 'label': 'Weight', 'info_only': True},
            {'key': 'eye_color', 'label': 'Eye Color', 'info_only': True},
            {'key': 'hair_color', 'label': 'Hair Color', 'info_only': True},
            {'key': 'immigration_status_at_entry', 'label': 'Immigration status at entry', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
            {'key': 'date_of_entry', 'label': 'Date of Entry', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'port_of_entry', 'label': 'Port of Entry', 'info_only': True},
            {'key': 'prior_entries', 'label': 'Prior entries', 'info_only': True},
            {'key': 'marital_status', 'label': 'Marital status', 'infotems_field': 'MaritalStatus', 'biographic': True},
            {'key': 'spouse_info', 'label': 'Spouse information', 'info_only': True, 'family_member': 'spouse'},
            {'key': 'children_info', 'label': 'Children information', 'info_only': True, 'family_member': 'children'},
            {'key': 'father_info', 'label': 'Father information', 'info_only': True, 'family_member': 'father'},
            {'key': 'mother_info', 'label': 'Mother information', 'info_only': True, 'family_member': 'mother'},
            {'key': 'removal_proceedings', 'label': 'Prior removal proceedings', 'info_only': True},
            {'key': 'false_info_given', 'label': 'False information given', 'info_only': True},
            {'key': 'military_training', 'label': 'Military/weapons training', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Arrest/criminal history', 'info_only': True},
        ]
    },
    
    'parole_in_place_questionnaire': {
        'display_name': 'I-131F Parole in Place Questionnaire',
        'description': 'Parole in Place application questionnaire',
        'detection_patterns': [
            'Form I-131F Questionnaire',
            'I-131F Questionnaire',
            'Parole in Place',
            'Formulario I134F',
        ],
        'languages': ['English', 'Spanish', 'Creole'],
        'fields': [
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'ssn', 'label': 'U.S. Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
            {'key': 'uscis_account', 'label': 'USCIS Online Account Number', 'info_only': True},
            {'key': 'last_name', 'label': 'Last (Family) Name', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'First (Given) Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'other_names', 'label': 'Other names used', 'info_only': True},
            {'key': 'address_line1', 'label': 'Street Number and Name', 'infotems_field': 'AddressLine1'},
            {'key': 'address_line2', 'label': 'Apartment, Suite, Floor', 'infotems_field': 'AddressLine2'},
            {'key': 'city', 'label': 'City or Town', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'email', 'label': 'Email address', 'infotems_field': 'EmailPersonal'},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'City of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'state_of_birth', 'label': 'State/Province of Birth', 'infotems_field': 'BirthState', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'ethnicity', 'label': 'Ethnicity', 'info_only': True},
            {'key': 'race', 'label': 'Race', 'info_only': True},
            {'key': 'height', 'label': 'Height', 'info_only': True},
            {'key': 'weight', 'label': 'Weight', 'info_only': True},
            {'key': 'eye_color', 'label': 'Eye Color', 'info_only': True},
            {'key': 'hair_color', 'label': 'Hair Color', 'info_only': True},
            {'key': 'spouse_info', 'label': 'Spouse information', 'info_only': True, 'family_member': 'spouse'},
            {'key': 'date_of_marriage', 'label': 'Date of Marriage', 'info_only': True, 'type': 'date'},
            {'key': 'children_info', 'label': 'Children information', 'info_only': True, 'family_member': 'children'},
            {'key': 'immigration_status_at_entry', 'label': 'Immigration status at entry', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
            {'key': 'date_of_entry', 'label': 'Date of Entry', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'port_of_entry', 'label': 'Port of Entry', 'info_only': True},
            {'key': 'prior_entries', 'label': 'Prior entries', 'info_only': True},
            {'key': 'removal_proceedings', 'label': 'Prior removal proceedings', 'info_only': True},
            {'key': 'false_info_given', 'label': 'False information given', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Arrest/criminal history', 'info_only': True},
            {'key': 'statement', 'label': 'Statement for parole', 'info_only': True},
        ]
    },
    
    'green_card_renewal_questionnaire': {
        'display_name': 'I-90 Green Card Renewal Questionnaire',
        'description': 'Green Card renewal/replacement questionnaire',
        'detection_patterns': [
            'I-90 Questionnaire',
            'I90 Questionnaire',
            'Green Card Renewal',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'ssn', 'label': 'U.S. Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
            {'key': 'uscis_account', 'label': 'USCIS Online Account Number', 'info_only': True},
            {'key': 'email', 'label': 'Email Address', 'infotems_field': 'EmailPersonal'},
            {'key': 'card_issue_date', 'label': 'Current Card Issue Date', 'info_only': True, 'type': 'date'},
            {'key': 'card_expiry_date', 'label': 'Current Card Expiry Date', 'info_only': True, 'type': 'date'},
            {'key': 'last_name', 'label': 'Family Name (Last Name)', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'Given Name (First Name)', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'prior_names', 'label': 'Prior names', 'info_only': True},
            {'key': 'address_line1', 'label': 'Street Number and Name', 'infotems_field': 'AddressLine1'},
            {'key': 'address_line2', 'label': 'Apt/Ste/Flr', 'infotems_field': 'AddressLine2'},
            {'key': 'city', 'label': 'City or Town', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'city_of_birth', 'label': 'City/Town/Village of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'ethnicity', 'label': 'Ethnicity', 'info_only': True},
            {'key': 'race', 'label': 'Race', 'info_only': True},
            {'key': 'height', 'label': 'Height', 'info_only': True},
            {'key': 'weight', 'label': 'Weight', 'info_only': True},
            {'key': 'eye_color', 'label': 'Eye Color', 'info_only': True},
            {'key': 'hair_color', 'label': 'Hair Color', 'info_only': True},
            {'key': 'mother_name', 'label': 'Mother\'s Name', 'info_only': True},
            {'key': 'father_name', 'label': 'Father\'s Name', 'info_only': True},
            {'key': 'place_of_first_entry', 'label': 'Place of First Entry', 'info_only': True},
            {'key': 'how_obtained_residency', 'label': 'How obtained residency', 'info_only': True},
            {'key': 'where_became_resident', 'label': 'Where became resident', 'info_only': True},
            {'key': 'class_of_admission', 'label': 'Class of admission', 'info_only': True},
            {'key': 'removal_proceedings', 'label': 'Prior removal proceedings', 'info_only': True},
            {'key': 'travel_count', 'label': 'Travel count', 'info_only': True},
            {'key': 'trips_over_6_months', 'label': 'Trips over 6 months', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Arrest/criminal history', 'info_only': True},
        ]
    },
    
    'foia_questionnaire': {
        'display_name': 'FOIA Questionnaire',
        'description': 'Freedom of Information Act request questionnaire',
        'detection_patterns': [
            'FOIA Questionnaire',
            'Cuestionario FOIA',
            'Freedom of Information',
        ],
        'languages': ['English', 'Spanish', 'Creole'],
        'fields': [
            {'key': 'last_name', 'label': 'Last (family) name', 'infotems_field': 'LastName'},
            {'key': 'first_name', 'label': 'First (given) name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle name', 'infotems_field': 'MiddleName'},
            {'key': 'date_of_birth', 'label': 'Date of birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of birth', 'infotems_field': 'BirthCountry', 'biographic': True},
            {'key': 'address_line1', 'label': 'Street Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'Zip', 'infotems_field': 'PostalZipCode'},
            {'key': 'phone', 'label': 'Phone number(s)', 'infotems_field': 'CellPhone'},
            {'key': 'email', 'label': 'Email address', 'infotems_field': 'EmailPersonal'},
            {'key': 'a_number', 'label': 'Alien number', 'infotems_field': 'AlienNumber', 'biographic': True},
            {'key': 'father_name', 'label': 'Father\'s Full Name', 'info_only': True},
            {'key': 'mother_name', 'label': 'Mother\'s Full Name', 'info_only': True},
            {'key': 'immigration_status', 'label': 'Current immigration status', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
            {'key': 'date_of_entry', 'label': 'Date of entry into US', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'manner_of_entry', 'label': 'Manner of entry', 'info_only': True},
            {'key': 'family_members_entered', 'label': 'Family members entered with', 'info_only': True},
            {'key': 'ice_encounters', 'label': 'ICE/DHS encounters', 'info_only': True},
            {'key': 'prior_removals', 'label': 'Prior entries/removals', 'info_only': True},
            {'key': 'removal_proceedings', 'label': 'Removal proceedings info', 'info_only': True},
            {'key': 'criminal_history', 'label': 'Criminal history', 'info_only': True},
            {'key': 'prior_applications', 'label': 'Previous immigration applications', 'info_only': True},
            {'key': 'receipt_numbers', 'label': 'Receipt numbers', 'info_only': True},
            {'key': 'native_language', 'label': 'Primary language', 'infotems_field': 'NativeLanguage', 'biographic': True},
        ]
    },
    
    'sij_questionnaire': {
        'display_name': 'SIJ Questionnaire',
        'description': 'Special Immigrant Juvenile Status questionnaire',
        'detection_patterns': [
            'Questionnaire for SIJ',
            'SIJ Questionnaire',
            'Cuestionario Para La Visa Juvenil',
            'Visa Especial Juvenil',
        ],
        'languages': ['English', 'Spanish'],
        'fields': [
            {'key': 'full_name', 'label': 'Full Name', 'infotems_field': None},
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'address_line1', 'label': 'Current Address', 'infotems_field': 'AddressLine1'},
            {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
            {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
            {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            {'key': 'date_started_living', 'label': 'Date started living there', 'info_only': True, 'type': 'date'},
            {'key': 'father_name', 'label': 'Father\'s name', 'info_only': True},
            {'key': 'father_birthplace', 'label': 'Father\'s birthplace', 'info_only': True},
            {'key': 'father_location', 'label': 'Father\'s current location', 'info_only': True},
            {'key': 'mother_name', 'label': 'Mother\'s name', 'info_only': True},
            {'key': 'mother_birthplace', 'label': 'Mother\'s birthplace', 'info_only': True},
            {'key': 'mother_location', 'label': 'Mother\'s current location', 'info_only': True},
            {'key': 'address_history', 'label': 'Address history (28 years)', 'info_only': True},
        ]
    },
}

# ============================================================================
# DOCUMENT TYPE DEFINITIONS (NON-QUESTIONNAIRE - AI ANALYSIS REQUIRED)
# ============================================================================

# Document types that require on-the-spot AI analysis
DOCUMENT_TYPES = {
    'passport': {
        'display_name': 'Passport',
        'description': 'Foreign passport document',
        'fields': [
            {'key': 'first_name', 'label': 'First Name', 'infotems_field': 'FirstName'},
            {'key': 'last_name', 'label': 'Last Name', 'infotems_field': 'LastName'},
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'place_of_birth', 'label': 'Place of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'nationality', 'label': 'Nationality', 'infotems_field': 'Citizenship1Country', 'biographic': True},
            {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
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
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
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
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
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
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'place_of_birth', 'label': 'Place of Birth', 'infotems_field': 'BirthCity', 'biographic': True},
            {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
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
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
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
            {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
            {'key': 'country_of_citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
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
    'info_only': '#2196F3', # Blue - info only (not mapped)
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_document_types():
    """Get combined list of questionnaires and other document types."""
    all_types = {}
    for key, value in QUESTIONNAIRE_TYPES.items():
        all_types[key] = value
    for key, value in DOCUMENT_TYPES.items():
        all_types[key] = value
    return all_types

def detect_questionnaire_type(text: str) -> str:
    """Detect questionnaire type from document text."""
    text_lower = text.lower()
    for qtype, config in QUESTIONNAIRE_TYPES.items():
        for pattern in config.get('detection_patterns', []):
            if pattern.lower() in text_lower:
                return qtype
    return None

def get_mappable_fields(doc_type: str) -> list:
    """Get fields that can be mapped to InfoTems for a document type."""
    all_types = get_all_document_types()
    if doc_type not in all_types:
        return []
    
    fields = all_types[doc_type].get('fields', [])
    return [f for f in fields if f.get('infotems_field') and not f.get('info_only')]

def get_info_only_fields(doc_type: str) -> list:
    """Get fields that are extracted but not mapped to InfoTems."""
    all_types = get_all_document_types()
    if doc_type not in all_types:
        return []
    
    fields = all_types[doc_type].get('fields', [])
    return [f for f in fields if f.get('info_only')]
