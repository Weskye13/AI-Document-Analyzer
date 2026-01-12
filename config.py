"""
AI Document Analyzer - Configuration
=====================================

Central configuration for the document analyzer system.
Handles credentials, paths, and document type definitions.

Author: Law Office of Joshua E. Bardavid
Version: 2.1.0
Date: January 2026

DESIGN PRINCIPLES:
- Everything requires approval - no automatic updates
- Family members are full contacts - can be searched, linked, or created
- History is structured data - address, employment, education as reviewable records
- Approval window is fully editable - user can modify any field before applying

INFOTEMS API DEPENDENCY:
========================
This project depends EXCLUSIVELY on the InfoTems Hybrid Client located at:
    ..\New Official Infotems API\infotems_hybrid_client.py

That client is the SINGLE SOURCE OF TRUTH for:
- All InfoTems API endpoints and methods
- Field names and data structures  
- Authentication and connection handling
- CRUD operations (create, read, update, delete)

NO direct API calls to InfoTems are permitted elsewhere in this project.
All InfoTems operations MUST go through the InfotemsHybridClient class.

Available methods include:
- Contact: get_contact, search_contacts, create_contact, update_contact
- Biographic: get_contact_biography, create_contact_biographic, update_contact_biographic
- Notes: create_note, search_notes
- Search: search_by_anumber, global_search

See infotems_hybrid_client.py for complete method documentation.
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

SCRIPT_DIR = Path(__file__).parent

INFOTEMS_API_PATHS = [
    r'W:\Work\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API',
    r'C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API',
]

CLIENT_FOLDER_BASES = [
    r'W:\Work\Dropbox\Law Office of Joshua E. Bardavid\Clients',
    r'C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Clients',
]

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

INFOTEMS_API_PATH = get_first_existing_path(INFOTEMS_API_PATHS)
CLIENT_FOLDER_BASE = get_first_existing_path(CLIENT_FOLDER_BASES)
METADATA_PATH = get_first_existing_path(METADATA_PATHS)

if INFOTEMS_API_PATH:
    sys.path.insert(0, INFOTEMS_API_PATH)

# ============================================================================
# CREDENTIALS
# ============================================================================

INFOTEMS_USERNAME = os.getenv('INFOTEMS_USERNAME')
INFOTEMS_PASSWORD = os.getenv('INFOTEMS_PASSWORD')
INFOTEMS_API_KEY = os.getenv('INFOTEMS_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# ============================================================================
# AI MODEL SETTINGS
# ============================================================================

AI_CONFIG = {
    'model': 'claude-sonnet-4-20250514',
    'max_tokens': 8192,  # Increased for comprehensive extraction
    'temperature': 0.0,
}

# ============================================================================
# FAMILY MEMBER RELATIONSHIPS
# ============================================================================

FAMILY_RELATIONSHIPS = {
    'spouse': {
        'display_name': 'Spouse',
        'can_include_in_application': True,
        'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth', 
                   'city_of_birth', 'state_of_birth', 'country_of_birth',
                   'citizenship', 'gender', 'a_number', 'ssn', 'ethnicity', 'race',
                   'current_address', 'immigration_status', 'date_of_entry',
                   'date_of_marriage', 'place_of_marriage', 'include_in_application',
                   'resides_with_applicant'],
    },
    'child': {
        'display_name': 'Child',
        'can_include_in_application': True,
        'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth',
                   'city_of_birth', 'state_of_birth', 'country_of_birth',
                   'citizenship', 'gender', 'a_number', 'ssn', 'ethnicity', 'race',
                   'current_address', 'immigration_status', 'date_of_entry',
                   'include_in_application', 'resides_with_applicant'],
    },
    'father': {
        'display_name': 'Father',
        'can_include_in_application': False,
        'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth',
                   'city_of_birth', 'state_of_birth', 'country_of_birth',
                   'citizenship', 'current_city', 'current_country',
                   'is_deceased', 'date_of_death', 'us_legal_status'],
    },
    'mother': {
        'display_name': 'Mother',
        'can_include_in_application': False,
        'fields': ['first_name', 'middle_name', 'last_name', 'maiden_name',
                   'date_of_birth', 'city_of_birth', 'state_of_birth', 
                   'country_of_birth', 'citizenship', 'current_city', 
                   'current_country', 'is_deceased', 'date_of_death', 
                   'us_legal_status'],
    },
    'sibling': {
        'display_name': 'Sibling',
        'can_include_in_application': False,
        'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth',
                   'city_of_birth', 'country_of_birth', 'current_city',
                   'current_country', 'us_legal_status'],
    },
    'prior_spouse': {
        'display_name': 'Prior Spouse',
        'can_include_in_application': False,
        'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth',
                   'date_of_marriage', 'date_marriage_ended', 
                   'how_marriage_ended', 'place_marriage_ended'],
    },
}

# ============================================================================
# HISTORY RECORD TYPES
# ============================================================================

HISTORY_TYPES = {
    'address': {
        'display_name': 'Address History',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'address_line1', 'label': 'Street Address', 'required': True},
            {'key': 'address_line2', 'label': 'Apt/Suite/Floor'},
            {'key': 'city', 'label': 'City', 'required': True},
            {'key': 'state', 'label': 'State/Province'},
            {'key': 'zip_code', 'label': 'ZIP/Postal Code'},
            {'key': 'country', 'label': 'Country', 'required': True},
            {'key': 'from_date', 'label': 'From Date', 'type': 'date', 'required': True},
            {'key': 'to_date', 'label': 'To Date', 'type': 'date'},  # None = Present
            {'key': 'is_current', 'label': 'Current Address', 'type': 'bool'},
            {'key': 'is_mailing', 'label': 'Mailing Address', 'type': 'bool'},
            {'key': 'is_foreign', 'label': 'Foreign Address', 'type': 'bool'},
        ]
    },
    'employment': {
        'display_name': 'Employment History',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'employer_name', 'label': 'Employer Name', 'required': True},
            {'key': 'occupation', 'label': 'Job Title/Occupation', 'required': True},
            {'key': 'address_line1', 'label': 'Street Address'},
            {'key': 'city', 'label': 'City'},
            {'key': 'state', 'label': 'State/Province'},
            {'key': 'zip_code', 'label': 'ZIP/Postal Code'},
            {'key': 'country', 'label': 'Country'},
            {'key': 'from_date', 'label': 'From Date', 'type': 'date', 'required': True},
            {'key': 'to_date', 'label': 'To Date', 'type': 'date'},  # None = Present
            {'key': 'is_current', 'label': 'Current Employment', 'type': 'bool'},
        ]
    },
    'education': {
        'display_name': 'Education History',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'school_name', 'label': 'School Name', 'required': True},
            {'key': 'school_type', 'label': 'School Type', 'options': [
                'Primary/Grade School', 'Middle School', 'High School',
                'University', 'Trade School', 'Advanced Degree', 'Other'
            ]},
            {'key': 'address_line1', 'label': 'Street Address'},
            {'key': 'city', 'label': 'City'},
            {'key': 'state', 'label': 'State/Province'},
            {'key': 'country', 'label': 'Country'},
            {'key': 'from_date', 'label': 'From Date', 'type': 'date'},
            {'key': 'to_date', 'label': 'To Date', 'type': 'date'},
        ]
    },
    'travel': {
        'display_name': 'Travel History',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'departure_date', 'label': 'Date Left US', 'type': 'date', 'required': True},
            {'key': 'return_date', 'label': 'Date Returned', 'type': 'date', 'required': True},
            {'key': 'countries_visited', 'label': 'Countries Visited'},
            {'key': 'purpose', 'label': 'Purpose of Trip'},
        ]
    },
    'prior_entry': {
        'display_name': 'Prior US Entry',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'date_of_entry', 'label': 'Date of Entry', 'type': 'date', 'required': True},
            {'key': 'port_of_entry', 'label': 'Port of Entry'},
            {'key': 'state_of_entry', 'label': 'State of Entry'},
            {'key': 'status_at_entry', 'label': 'Status at Entry'},
            {'key': 'manner_of_entry', 'label': 'Manner of Entry'},
        ]
    },
    'criminal': {
        'display_name': 'Arrest/Criminal History',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'date_of_arrest', 'label': 'Date of Arrest', 'type': 'date', 'required': True},
            {'key': 'place_of_arrest', 'label': 'Place of Arrest', 'required': True},
            {'key': 'charges', 'label': 'Charges', 'required': True},
            {'key': 'outcome', 'label': 'Outcome'},
            {'key': 'punishment', 'label': 'Punishment/Fine'},
        ]
    },
    'prior_application': {
        'display_name': 'Prior Immigration Applications',
        'note_category': 'Case Status',
        'fields': [
            {'key': 'application_type', 'label': 'Application Type', 'required': True},
            {'key': 'date_filed', 'label': 'Date Filed', 'type': 'date'},
            {'key': 'location', 'label': 'Where Filed'},
            {'key': 'status', 'label': 'Status/Outcome'},
            {'key': 'receipt_number', 'label': 'Receipt Number'},
        ]
    },
}

# ============================================================================
# QUESTIONNAIRE DEFINITIONS
# ============================================================================

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
        'fields': {
            'primary': [
                # Personal Info - maps to Contact
                {'key': 'last_name', 'label': 'Last (family) name', 'infotems_field': 'LastName'},
                {'key': 'first_name', 'label': 'First (given) name', 'infotems_field': 'FirstName'},
                {'key': 'middle_name', 'label': 'Middle name', 'infotems_field': 'MiddleName'},
                # Biographic
                {'key': 'date_of_birth', 'label': 'Date of birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
                {'key': 'country_of_birth', 'label': 'Country of birth', 'infotems_field': 'BirthCountry', 'biographic': True},
                # Address - maps to Contact
                {'key': 'address_line1', 'label': 'Street Address', 'infotems_field': 'AddressLine1'},
                {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
                {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
                {'key': 'zip_code', 'label': 'Zip', 'infotems_field': 'PostalZipCode'},
                # Contact
                {'key': 'phone', 'label': 'Phone number(s)', 'infotems_field': 'CellPhone'},
                {'key': 'email', 'label': 'Email address', 'infotems_field': 'EmailPersonal'},
                # Immigration - Biographic
                {'key': 'a_number', 'label': 'Alien number', 'infotems_field': 'AlienNumber', 'biographic': True},
                {'key': 'immigration_status', 'label': 'Current immigration status', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
                {'key': 'date_of_entry', 'label': 'Date of entry into the United States', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
                {'key': 'native_language', 'label': 'Primary/Best language', 'infotems_field': 'NativeLanguage', 'biographic': True},
            ],
            'family_members': [],  # Consult questionnaire doesn't collect detailed family info
            'history': {
                'prior_entry': ['manner_of_entry', 'family_members_entered'],
                'criminal': ['criminal_history'],
                'prior_application': ['prior_applications'],
            },
            'other': [
                {'key': 'ice_encounters', 'label': 'ICE/DHS encounters'},
                {'key': 'prior_removals', 'label': 'Prior entries/removals'},
                {'key': 'harm_in_country', 'label': 'Harmed in country'},
                {'key': 'fear_in_country', 'label': 'Fear of harm'},
                {'key': 'prior_asylum', 'label': 'Prior asylum application'},
                {'key': 'us_relatives', 'label': 'US relatives'},
                {'key': 'removal_proceedings', 'label': 'Removal proceedings info'},
                {'key': 'referral_source', 'label': 'How did you hear about us'},
                {'key': 'additional_info', 'label': 'Additional information'},
            ],
        }
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
        'fields': {
            'primary': [
                # Section 1: Personal and Contact Info
                {'key': 'a_number', 'label': 'A-Number', 'infotems_field': 'AlienNumber', 'biographic': True},
                {'key': 'ssn', 'label': 'U.S. Social Security Number', 'infotems_field': 'SSN', 'biographic': True},
                {'key': 'last_name', 'label': 'Last (Family) Name', 'infotems_field': 'LastName'},
                {'key': 'first_name', 'label': 'First (Given) Name', 'infotems_field': 'FirstName'},
                {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
                {'key': 'other_names', 'label': 'Other names used'},
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
                {'key': 'citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
                {'key': 'ethnicity', 'label': 'Ethnicity'},
                {'key': 'race', 'label': 'Race'},
                {'key': 'religion', 'label': 'Religion'},
                {'key': 'height', 'label': 'Height'},
                {'key': 'weight', 'label': 'Weight'},
                {'key': 'eye_color', 'label': 'Eye Color'},
                {'key': 'hair_color', 'label': 'Hair Color'},
                {'key': 'native_language', 'label': 'Best/first language', 'infotems_field': 'NativeLanguage', 'biographic': True},
                {'key': 'english_fluent', 'label': 'English fluency'},
                {'key': 'other_languages', 'label': 'Other languages'},
                {'key': 'passport_country', 'label': 'Passport issuing country'},
                {'key': 'passport_number', 'label': 'Passport number'},
                {'key': 'passport_issue_date', 'label': 'Passport issue date', 'type': 'date'},
                {'key': 'passport_expiry_date', 'label': 'Passport expiry date', 'type': 'date'},
                # Section 3: Travel History - Last Entry
                {'key': 'immigration_status_at_entry', 'label': 'Immigration status at last entry', 'infotems_field': 'CurrentImmigrationStatus', 'biographic': True},
                {'key': 'date_of_entry', 'label': 'Date of Entry', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
                {'key': 'port_of_entry', 'label': 'Place or Port-of-Entry'},
                {'key': 'state_of_entry', 'label': 'State of Entry'},
                # Section 4: Family Information - Marital Status
                {'key': 'marital_status', 'label': 'Relationship status', 'infotems_field': 'MaritalStatus', 'biographic': True},
                # Employment (current only maps to Contact)
                {'key': 'employer', 'label': 'Current Employer', 'infotems_field': 'Employer'},
                {'key': 'occupation', 'label': 'Job title', 'infotems_field': 'Occupation'},
            ],
            'family_members': [
                {
                    'relationship': 'spouse',
                    'section_label': 'Spouse Information',
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'gender',
                        'date_of_birth', 'city_of_birth', 'state_of_birth', 'country_of_birth',
                        'citizenship', 'ethnicity', 'race', 'resides_with_applicant',
                        'current_city', 'current_country', 'immigration_status', 'date_of_entry',
                        'port_of_entry', 'include_in_application'
                    ],
                },
                {
                    'relationship': 'child',
                    'section_label': 'Children Information',
                    'multiple': True,
                    'max_count': 4,
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'gender',
                        'date_of_birth', 'city_of_birth', 'state_of_birth', 'country_of_birth',
                        'citizenship', 'ethnicity', 'race', 'resides_with_applicant',
                        'current_city', 'current_country', 'immigration_status', 'date_of_entry',
                        'port_of_entry', 'include_in_application'
                    ],
                },
                {
                    'relationship': 'father',
                    'section_label': 'Father Information',
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'date_of_birth',
                        'city_of_birth', 'state_of_birth', 'country_of_birth', 'citizenship',
                        'is_deceased', 'date_of_death', 'current_city', 'current_country',
                        'us_legal_status'
                    ],
                },
                {
                    'relationship': 'mother',
                    'section_label': 'Mother Information',
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'date_of_birth',
                        'city_of_birth', 'state_of_birth', 'country_of_birth', 'citizenship',
                        'is_deceased', 'date_of_death', 'current_city', 'current_country',
                        'us_legal_status'
                    ],
                },
            ],
            'history': {
                'address': {
                    'section_label': 'Address History',
                    'include_foreign': True,
                },
                'employment': {
                    'section_label': 'Employment History (5 years)',
                },
                'education': {
                    'section_label': 'Education History',
                },
                'prior_entry': {
                    'section_label': 'Prior US Entries',
                },
                'criminal': {
                    'section_label': 'Arrest/Criminal History',
                },
            },
            'other': [
                {'key': 'removal_proceedings', 'label': 'Prior removal proceedings'},
                {'key': 'false_info_given', 'label': 'False information given to US officials'},
                {'key': 'military_training', 'label': 'Military/weapons training'},
                {'key': 'asylum_statement', 'label': 'Statement (reasons for fleeing)'},
            ],
        }
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
        'fields': {
            'primary': [
                {'key': 'last_name', 'label': 'Family Name (Last Name)', 'infotems_field': 'LastName'},
                {'key': 'first_name', 'label': 'Given Name (First Name)', 'infotems_field': 'FirstName'},
                {'key': 'middle_name', 'label': 'Middle Name', 'infotems_field': 'MiddleName'},
                {'key': 'other_names', 'label': 'Other names used'},
                {'key': 'gender', 'label': 'Gender', 'infotems_field': 'Gender', 'biographic': True},
                {'key': 'date_of_birth', 'label': 'Date of Birth', 'infotems_field': 'BirthDate', 'biographic': True, 'type': 'date'},
                {'key': 'country_of_birth', 'label': 'Country of Birth', 'infotems_field': 'BirthCountry', 'biographic': True},
                {'key': 'citizenship', 'label': 'Country of Citizenship', 'infotems_field': 'Citizenship1Country', 'biographic': True},
                {'key': 'date_became_lpr', 'label': 'Date became LPR', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
                {'key': 'marital_status', 'label': 'Marital Status', 'infotems_field': 'MaritalStatus', 'biographic': True},
                {'key': 'num_marriages', 'label': 'Number of marriages'},
                {'key': 'employer', 'label': 'Current Employer/School', 'infotems_field': 'Employer'},
                {'key': 'occupation', 'label': 'Occupation', 'infotems_field': 'Occupation'},
            ],
            'family_members': [
                {
                    'relationship': 'spouse',
                    'section_label': 'Current Spouse Information',
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'date_of_birth',
                        'date_of_marriage', 'a_number', 'us_legal_status'
                    ],
                },
                {
                    'relationship': 'prior_spouse',
                    'section_label': 'Prior Spouse Information',
                    'multiple': True,
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'date_of_birth',
                        'date_of_marriage', 'date_marriage_ended', 'a_number', 'us_legal_status'
                    ],
                },
                {
                    'relationship': 'child',
                    'section_label': 'Children Information',
                    'multiple': True,
                    'fields': [
                        'first_name', 'last_name', 'date_of_birth', 'country_of_birth',
                        'a_number', 'us_legal_status'
                    ],
                },
            ],
            'history': {
                'employment': {'section_label': 'Employment/School History (5 years)'},
                'travel': {'section_label': 'Travel History (5 years)'},
                'criminal': {'section_label': 'Arrest/Criminal History'},
            },
            'other': [
                {'key': 'claimed_us_citizen', 'label': 'Ever claimed US citizenship'},
                {'key': 'voted_in_us', 'label': 'Ever voted in US elections'},
                {'key': 'tax_issues', 'label': 'Tax filing issues'},
                {'key': 'child_support_issues', 'label': 'Child support issues'},
            ],
        }
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
        'fields': {
            'primary': [
                {'key': 'last_name', 'label': 'Family name', 'infotems_field': 'LastName'},
                {'key': 'first_name', 'label': 'Given name', 'infotems_field': 'FirstName'},
                {'key': 'middle_name', 'label': 'Middle name', 'infotems_field': 'MiddleName'},
                {'key': 'maiden_name', 'label': 'Maiden name'},
                {'key': 'nickname', 'label': 'Nickname'},
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
                {'key': 'ethnicity', 'label': 'Ethnicity'},
                {'key': 'race', 'label': 'Race'},
                {'key': 'height', 'label': 'Height'},
                {'key': 'weight', 'label': 'Weight'},
                {'key': 'eye_color', 'label': 'Eye Color'},
                {'key': 'hair_color', 'label': 'Hair Color'},
                {'key': 'marital_status', 'label': 'Marital Status', 'infotems_field': 'MaritalStatus', 'biographic': True},
                {'key': 'date_of_marriage', 'label': 'Date of Marriage', 'type': 'date'},
                {'key': 'place_of_marriage', 'label': 'Place of Marriage'},
                {'key': 'employer', 'label': 'Current Employer', 'infotems_field': 'Employer'},
                {'key': 'occupation', 'label': 'Occupation', 'infotems_field': 'Occupation'},
                {'key': 'address_line1', 'label': 'Street Address', 'infotems_field': 'AddressLine1'},
                {'key': 'city', 'label': 'City', 'infotems_field': 'City'},
                {'key': 'state', 'label': 'State', 'infotems_field': 'State'},
                {'key': 'zip_code', 'label': 'ZIP Code', 'infotems_field': 'PostalZipCode'},
            ],
            'family_members': [
                {
                    'relationship': 'father',
                    'section_label': 'Father Information',
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'date_of_birth',
                        'city_of_birth', 'country_of_birth', 'is_deceased', 'date_of_death',
                        'current_city', 'current_country'
                    ],
                },
                {
                    'relationship': 'mother',
                    'section_label': 'Mother Information',
                    'fields': [
                        'first_name', 'middle_name', 'last_name', 'maiden_name',
                        'date_of_birth', 'city_of_birth', 'country_of_birth',
                        'is_deceased', 'date_of_death', 'current_city', 'current_country'
                    ],
                },
                {
                    'relationship': 'prior_spouse',
                    'section_label': 'Prior Spouse Information',
                    'multiple': True,
                    'fields': [
                        'first_name', 'last_name', 'date_of_birth',
                        'date_of_marriage', 'place_of_marriage',
                        'date_marriage_ended', 'place_marriage_ended'
                    ],
                },
            ],
            'history': {
                'address': {'section_label': 'Address History (5 years)'},
                'employment': {'section_label': 'Employment History (5 years)'},
            },
            'other': [
                {'key': 'is_usc', 'label': 'Is U.S. Citizen'},
                {'key': 'naturalization_info', 'label': 'Naturalization info'},
                {'key': 'is_lpr', 'label': 'Is Permanent Resident'},
                {'key': 'lpr_info', 'label': 'LPR info'},
                {'key': 'petition_relationship', 'label': 'Relationship to beneficiary'},
                {'key': 'prior_petitions', 'label': 'Prior petitions filed'},
                {'key': 'income', 'label': 'Current income'},
                {'key': 'tax_returns', 'label': 'Tax return info'},
                {'key': 'household_size', 'label': 'Household size'},
            ],
        }
    },

    # Additional questionnaires follow same pattern...
    # (i130_beneficiary, adjustment, ds260, waiver_601a, parole_in_place, 
    #  green_card_renewal, foia, sij)
}

# ============================================================================
# DOCUMENT TYPES (NON-QUESTIONNAIRE - AI ANALYSIS REQUIRED)
# ============================================================================

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
            {'key': 'passport_number', 'label': 'Passport Number'},
            {'key': 'issue_date', 'label': 'Issue Date', 'type': 'date'},
            {'key': 'expiration_date', 'label': 'Expiration Date', 'type': 'date'},
            {'key': 'issuing_country', 'label': 'Issuing Country'},
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
            {'key': 'uscis_number', 'label': 'USCIS Number'},
            {'key': 'category', 'label': 'Category'},
            {'key': 'card_expires', 'label': 'Card Expires', 'type': 'date'},
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
            {'key': 'uscis_number', 'label': 'USCIS Number'},
            {'key': 'category', 'label': 'Category'},
            {'key': 'resident_since', 'label': 'Resident Since', 'type': 'date'},
            {'key': 'card_expires', 'label': 'Card Expires', 'type': 'date'},
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
            {'key': 'father_name', 'label': 'Father\'s Name'},
            {'key': 'mother_name', 'label': 'Mother\'s Name'},
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
            {'key': 'id_number', 'label': 'ID Number'},
            {'key': 'issue_date', 'label': 'Issue Date', 'type': 'date'},
            {'key': 'expiration_date', 'label': 'Expiration Date', 'type': 'date'},
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
            {'key': 'passport_number', 'label': 'Passport Number'},
            {'key': 'date_of_entry', 'label': 'Date of Entry', 'infotems_field': 'DateOfEntryToUsa', 'biographic': True, 'type': 'date'},
            {'key': 'class_of_admission', 'label': 'Class of Admission'},
            {'key': 'admit_until', 'label': 'Admit Until Date', 'type': 'date'},
            {'key': 'i94_number', 'label': 'I-94 Number'},
        ]
    },
}

# ============================================================================
# FIELD MAPPINGS
# ============================================================================

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
    'window_size': '1600x1000',
    'log_font': ('Consolas', 9),
    'header_font': ('Arial', 14, 'bold'),
    'tabs': [
        'Primary Contact',
        'Family Members',
        'Address History',
        'Employment History',
        'Education History',
        'Other Information',
    ],
}

CHANGE_COLORS = {
    'new': '#4CAF50',       # Green
    'modified': '#FF9800',  # Orange
    'removed': '#F44336',   # Red
    'unchanged': '#9E9E9E', # Gray
    'linked': '#2196F3',    # Blue - linked to existing contact
    'create': '#9C27B0',    # Purple - will create new contact
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_document_types():
    """Get combined dict of questionnaires and other document types."""
    all_types = {}
    all_types.update(QUESTIONNAIRE_TYPES)
    all_types.update(DOCUMENT_TYPES)
    return all_types

def detect_questionnaire_type(text: str) -> str:
    """Detect questionnaire type from document text."""
    text_lower = text.lower()
    for qtype, config in QUESTIONNAIRE_TYPES.items():
        for pattern in config.get('detection_patterns', []):
            if pattern.lower() in text_lower:
                return qtype
    return None

def get_family_member_fields(relationship: str) -> list:
    """Get field definitions for a family member relationship type."""
    return FAMILY_RELATIONSHIPS.get(relationship, {}).get('fields', [])

def get_history_fields(history_type: str) -> list:
    """Get field definitions for a history record type."""
    return HISTORY_TYPES.get(history_type, {}).get('fields', [])

def is_biographic_field(field_name: str) -> bool:
    """Check if a field belongs to ContactBiographic."""
    return field_name in BIOGRAPHIC_FIELDS

def is_contact_field(field_name: str) -> bool:
    """Check if a field belongs to Contact."""
    return field_name in CONTACT_FIELDS
