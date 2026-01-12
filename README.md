# AI Document Analyzer

AI-powered document extraction system for immigration law practice management.

## Architecture: Hub and Spoke Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFOTEMS API HUB                                │
│                                                                         │
│   Location: ..\New Official Infotems API\infotems_hybrid_client.py     │
│                                                                         │
│   This is the SINGLE SOURCE OF TRUTH for all InfoTems operations.      │
│   ALL API calls, field names, and data structures are defined here.    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ imports
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AI DOCUMENT ANALYZER (Spoke)                       │
│                                                                         │
│   This project uses the hub client exclusively.                        │
│   NO direct InfoTems API calls are permitted in this codebase.         │
│                                                                         │
│   Components:                                                           │
│   ├── config.py              - Configuration and paths                 │
│   ├── document_extractor.py  - AI document parsing (Claude Vision)     │
│   ├── infotems_comparator.py - Compare/apply changes via hub client    │
│   ├── approval_gui.py        - User review interface                   │
│   └── main.py                - Application entry point                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Critical Dependency

**The InfoTems Hybrid Client is the ONLY authorized way to interact with InfoTems.**

Location:
```
C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API\infotems_hybrid_client.py
```

### Why This Matters

1. **Single Source of Truth**: All API endpoints, field names, and data structures are defined in one place
2. **Safe Updates**: The hub client uses PATCH operations to prevent data corruption
3. **Consistency**: All projects (Mail GUI, Full Wrapper, AI Document Analyzer) use the same client
4. **Maintainability**: API changes only need to be made in one location

### Available Methods

The hub client provides these methods (used by this project):

**Contact Operations:**
- `get_contact(contact_id)` - Get contact by ID
- `search_contacts(first_name, last_name, ...)` - Search contacts
- `search_by_anumber(a_number)` - Find by A-number
- `create_contact(first_name, last_name, **fields)` - Create new contact
- `update_contact(contact_id, fields)` - Update contact (PATCH)

**Biographic Operations:**
- `get_contact_biography(contact_id)` - Get biographic data
- `create_contact_biographic(contact_id, **fields)` - Create biographic
- `update_contact_biographic(biographic_id, fields)` - Update biographic (PATCH)

**Relationship Operations:**
- `add_contact_relative(primary_id, related_id, relationship, **kwargs)` - Link contacts as relatives
- `search_contact_relationships(primary_contact_id)` - Get linked relatives
- `update_contact_relationship(relationship_id, fields)` - Update relationship
- `delete_contact_relationship(relationship_id)` - Remove link

**History Record Operations:**
- `create_address(contact_id, line1, city, state, ...)` - Create address record
- `create_employment(contact_id, occupation, start_date, ...)` - Create employment record
- `create_education(contact_id, institution_name, ...)` - Create education record
- `create_travel_history(contact_id, arrival_date, ...)` - Create travel record

**Notes:**
- `create_note(subject, body, contact_id, category, ...)` - Create note

### Adding New InfoTems Functionality

If this project needs new InfoTems functionality:

1. **DO NOT** add API calls directly to this project
2. **DO** add the method to `infotems_hybrid_client.py` first
3. **THEN** import and use it from the hub client

## Features

- **Enhanced Multi-Pass Extraction**: Uses Claude Vision AI with self-critique, validation, and iterative refinement
- **Cross-Validation**: Multiple extraction strategies find consensus for higher accuracy
- **Validation Layer**: Catches logical errors (impossible dates, format issues) before comparison
- **Family Member Handling**: Search, link, or create contacts with full biographic data
- **History as Proper Records**: Address, employment, education, travel saved as InfoTems records
- **Approval Workflow**: All changes require user approval before applying
- **Editable Interface**: All extracted data can be modified before saving

## Installation

```bash
pip install anthropic pymupdf python-dotenv
```

## Configuration

Create `.env` file:
```
ANTHROPIC_API_KEY=your-key
INFOTEMS_USERNAME=your-username
INFOTEMS_PASSWORD=your-password
INFOTEMS_API_KEY=your-api-key
```

## Usage

```python
from document_extractor import DocumentExtractor
from infotems_comparator import InfotemsComparator
from approval_gui import ApprovalGUI

# Extract data from document
extractor = DocumentExtractor()
extracted = extractor.extract_from_file("questionnaire.pdf")

# Compare with InfoTems
comparator = InfotemsComparator()
change_set = comparator.compare(extracted, "questionnaire.pdf")

# Review and approve
gui = ApprovalGUI(change_set, comparator=comparator, on_apply=comparator.apply_changes)
result = gui.run()
```

## Version History

- **v2.4.0** - Enhanced multi-pass extraction with self-critique, validation, and iterative refinement (Ralph Brainstormer pattern)
- **v2.3.0** - History as proper InfoTems records (Address, Employment, Education, Travel), full biographic data for family members
- **v2.2.0** - Full family member relationship linking via `add_contact_relative()`
- **v2.1.0** - Hub/spoke architecture documentation, explicit InfoTems client dependency
- **v2.0.0** - Family member search/link/create, history records, comprehensive approval GUI
- **v1.0.0** - Initial release with basic extraction and comparison

## Author

Law Office of Joshua E. Bardavid
