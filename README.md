# AI Document Analyzer

**Version:** 2.1.0  
**Author:** Law Office of Joshua E. Bardavid  
**Date:** January 2026

## Overview

AI-powered document analysis system that extracts data from immigration documents and updates InfoTems with user approval. Uses Claude AI for intelligent OCR and data extraction, with a comprehensive approval workflow before applying any changes.

## ⚠️ CRITICAL DEPENDENCY: InfoTems Hybrid Client

**This project depends EXCLUSIVELY on the InfoTems Hybrid Client.**

```
SINGLE SOURCE OF TRUTH FOR ALL INFOTEMS OPERATIONS:
..\New Official Infotems API\infotems_hybrid_client.py
```

### Why This Matters

- **NO direct API calls** to InfoTems are permitted in this project
- **ALL InfoTems operations** must go through `InfotemsHybridClient`
- **Field names, endpoints, and data structures** are defined in that client
- **Authentication and connection handling** is managed by that client

### InfoTems Methods Used

This project uses the following methods from `InfotemsHybridClient`:

| Method | Purpose |
|--------|---------|
| `get_contact(id)` | Retrieve contact by ID |
| `search_contacts(...)` | Search contacts by name |
| `search_by_anumber(a_num)` | Find contact by A-number |
| `create_contact(...)` | Create new contact |
| `update_contact(id, fields)` | Update contact (PATCH) |
| `get_contact_biography(id)` | Get biographic data |
| `create_contact_biographic(...)` | Create biographic record |
| `update_contact_biographic(...)` | Update biographic (PATCH) |
| `create_note(...)` | Create case notes |

### Adding New InfoTems Functionality

If you need additional InfoTems functionality:

1. **First check** if the method exists in `infotems_hybrid_client.py`
2. **If it exists**, import and use it from `InfotemsHybridClient`
3. **If it doesn't exist**, add it to `infotems_hybrid_client.py` first
4. **NEVER** make direct API calls in this project

## Features

- **AI-Powered Extraction**: Uses Claude Vision API for intelligent document analysis
- **Family Member Support**: Extract and link family members as contacts
- **History Tracking**: Address, employment, education history as structured records
- **Full Approval Workflow**: Review and edit ALL data before applying
- **InfoTems Integration**: Safe PATCH updates via the Hybrid Client

## Workflow

```
┌─────────────────┐
│ 1. Load Document│
│   (PDF/Image)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. AI Extraction│
│  (Claude Vision)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. Compare with InfoTems            │
│    (via InfotemsHybridClient ONLY)  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ 4. Review GUI   │
│ (6 Tabs - All   │
│  Editable)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 5. Apply Changes                    │
│    (via InfotemsHybridClient ONLY)  │
└─────────────────────────────────────┘
```

## Installation

### 1. Ensure InfoTems Client is Available

The InfoTems Hybrid Client must be in your Python path:

```
C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API\
```

This path is automatically added by `config.py`.

### 2. Install Dependencies

```bash
cd "C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\AI Document Analyzer"
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.template` to `.env` and fill in your credentials:

```bash
copy .env.template .env
```

Edit `.env`:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
INFOTEMS_USERNAME=your-username
INFOTEMS_PASSWORD=your-password
INFOTEMS_API_KEY=your-api-key
```

## Usage

### GUI Mode (Recommended)

```bash
python main.py
```

1. Click "Add Files" to select documents
2. Choose document type (or use Auto-detect)
3. Click "Analyze Documents"
4. Review in 6-tab approval dialog:
   - **Primary Contact**: Field-by-field comparison
   - **Family Members**: Search, link, or create
   - **Address History**: Editable table
   - **Employment History**: Editable table
   - **Education History**: Editable table
   - **Other Info**: Additional extracted data
5. Click "Apply" to update InfoTems

### CLI Mode

```bash
python main.py document.pdf --type questionnaire
```

## Supported Document Types

| Type | Description | Family Members | History |
|------|-------------|----------------|---------|
| `asylum_questionnaire` | 589 Asylum Questionnaire | ✓ | ✓ |
| `n400_questionnaire` | N-400 Naturalization | ✓ | ✓ |
| `i130_petitioner` | I-130 Petitioner | ✓ | ✓ |
| `i485_questionnaire` | I-485 Adjustment | ✓ | ✓ |
| `passport` | Foreign passports | - | - |
| `ead_card` | Employment Authorization | - | - |
| `green_card` | Permanent Resident Card | - | - |

## Architecture

```
AI Document Analyzer/
├── main.py                 # Main GUI application
├── config.py               # Configuration (paths, credentials, field defs)
├── document_extractor.py   # AI extraction (Claude Vision)
├── infotems_comparator.py  # InfoTems operations (via HybridClient)
├── approval_gui.py         # 6-tab approval interface
├── requirements.txt        # Python dependencies
└── README.md               # This file

EXTERNAL DEPENDENCY (Hub):
../New Official Infotems API/
└── infotems_hybrid_client.py  # SOLE InfoTems API interface
```

### Module Responsibilities

| Module | Responsibility | InfoTems Access |
|--------|---------------|-----------------|
| `config.py` | Paths, credentials, field definitions | None (config only) |
| `document_extractor.py` | AI document analysis | None |
| `infotems_comparator.py` | Contact search/compare/update | **Via HybridClient only** |
| `approval_gui.py` | User interface | Via comparator |
| `main.py` | Application orchestration | Via comparator |

## InfoTems Field Mapping

### Contact Fields (via HybridClient)
- FirstName, MiddleName, LastName, Suffix
- CellPhone, HomePhone, WorkPhone
- EmailPersonal, EmailWork
- AddressLine1, AddressLine2, City, State, PostalZipCode

### Biographic Fields (via HybridClient)
- AlienNumber, SSN, BirthDate
- BirthCity, BirthState, BirthCountry
- Gender, MaritalStatus, NativeLanguage
- Citizenship1Country, CurrentImmigrationStatus

## Dependencies

### Python Packages
- **anthropic**: Claude AI API client
- **PyMuPDF**: PDF to image conversion
- **Pillow**: Image processing
- **python-dotenv**: Environment variable management

### Internal Dependencies
- **InfotemsHybridClient**: `../New Official Infotems API/infotems_hybrid_client.py`
  - This is the **ONLY** authorized interface to InfoTems
  - All contact, biographic, and note operations go through this client

## Troubleshooting

### "InfoTems client not available"
Ensure the path to `infotems_hybrid_client.py` exists:
```
C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API\
```

### "ANTHROPIC_API_KEY not found"
Create `.env` file with your API key.

### "InfoTems connection failed"
Check credentials in `.env` file. The HybridClient handles authentication.

## License

Proprietary - Law Office of Joshua E. Bardavid
