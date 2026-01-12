# AI Document Analyzer

**Version:** 1.0.0  
**Author:** Law Office of Joshua E. Bardavid  
**Date:** January 2026

## Overview

AI-powered document analysis system that extracts data from immigration documents and updates InfoTems automatically. Uses Claude AI for intelligent OCR and data extraction, with a user approval workflow before applying changes.

## Features

- **AI-Powered Extraction**: Uses Claude Vision API for intelligent document analysis
- **Multiple Document Types**: Supports questionnaires, passports, EADs, green cards, birth certificates, IDs, and I-94s
- **InfoTems Integration**: Compares extracted data with existing records and shows differences
- **Approval Workflow**: Review all proposed changes before they're applied
- **Batch Processing**: Process multiple documents at once
- **Both GUI and CLI**: Use the graphical interface or command line

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
┌─────────────────┐
│ 3. Compare with │
│    InfoTems     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Review GUI   │
│ (Approve/Reject)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Apply Changes│
│   to InfoTems   │
└─────────────────┘
```

## Installation

### 1. Install Dependencies

```bash
cd "C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\AI Document Analyzer"
pip install -r requirements.txt
```

### 2. Configure Environment

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
4. Review proposed changes in the approval dialog
5. Click "Apply" to update InfoTems

### CLI Mode

Process a single document:
```bash
python main.py document.pdf
```

With specific document type:
```bash
python main.py questionnaire.pdf --type questionnaire
```

Apply changes without review:
```bash
python main.py passport.pdf --type passport --apply
```

## Supported Document Types

| Type | Description | Fields Extracted |
|------|-------------|------------------|
| `questionnaire` | Client questionnaires | Name, DOB, address, contact info, A-number, immigration status |
| `passport` | Foreign passports | Name, DOB, nationality, passport number, issue/expiry dates |
| `ead_card` | Employment Authorization | Name, DOB, A-number, category, expiration |
| `green_card` | Permanent Resident Card | Name, DOB, A-number, category, resident since |
| `birth_certificate` | Birth certificates | Name, DOB, place of birth, parents |
| `id_card` | Driver's license/State ID | Name, DOB, address, ID number, expiry |
| `i94` | I-94 Arrival Record | Name, DOB, entry date, class of admission |

## Architecture

```
AI Document Analyzer/
├── main.py                 # Main application and CLI entry point
├── config.py               # Configuration and field definitions
├── document_extractor.py   # AI document analysis (Claude Vision)
├── infotems_comparator.py  # InfoTems comparison and updates
├── approval_gui.py         # Review and approval GUI
├── requirements.txt        # Python dependencies
├── .env.template           # Environment variable template
└── README.md               # This file
```

### Key Components

1. **DocumentExtractor** (`document_extractor.py`)
   - Loads PDFs/images and converts to base64
   - Sends to Claude Vision API for analysis
   - Extracts structured data based on document type

2. **InfotemsComparator** (`infotems_comparator.py`)
   - Looks up existing contacts by A-number or name
   - Compares extracted data with current values
   - Generates ChangeSet with proposed modifications

3. **ChangeReviewGUI** (`approval_gui.py`)
   - Displays side-by-side comparison
   - Color-coded change indicators
   - Per-field approval checkboxes

4. **DocumentAnalyzerApp** (`main.py`)
   - Main GUI application
   - Coordinates extraction → comparison → approval → update

## InfoTems Field Mapping

Extracted data is mapped to InfoTems fields:

### Contact Fields
- FirstName, MiddleName, LastName
- CellPhone, HomePhone, EmailPersonal
- AddressLine1, AddressLine2, City, State, PostalZipCode

### Biographic Fields
- AlienNumber, BirthDate, BirthCity, BirthCountry
- Gender, MaritalStatus, NativeLanguage
- Citizenship1Country, CurrentImmigrationStatus

## Change Types

| Type | Color | Description |
|------|-------|-------------|
| **New** | Green | Field was empty, now has value |
| **Modified** | Orange | Existing value changed |
| **Unchanged** | Gray | Value matches current record |

## Dependencies

- **anthropic**: Claude AI API client
- **PyMuPDF**: PDF to image conversion
- **Pillow**: Image processing
- **requests**: HTTP client for InfoTems API
- **python-dotenv**: Environment variable management

## Integration with Full Wrapper

This script is designed to be integrated into Full Wrapper as a standalone module. Future integration points:

1. **Triggered by document upload** in the main application
2. **Embedded approval dialog** in the communication workflow
3. **Automatic client matching** using Full Wrapper's contact database
4. **Audit logging** to track all changes made

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Ensure you've created `.env` file and added your API key.

### "InfoTems connection not available"
Check INFOTEMS_USERNAME, INFOTEMS_PASSWORD, and INFOTEMS_API_KEY in `.env`.

### "Could not determine document type"
Try specifying the document type manually with `--type`.

### Poor OCR results
- Ensure document images are clear and high-resolution
- Try scanning at higher DPI
- Verify document is not upside down or rotated

## Future Enhancements

- [ ] Support for multi-page questionnaires
- [ ] Automatic language detection for foreign documents
- [ ] Translation integration for non-English documents
- [ ] Batch import from email attachments
- [ ] Integration with Full Wrapper main interface
- [ ] Document classification model for faster type detection

## License

Proprietary - Law Office of Joshua E. Bardavid
