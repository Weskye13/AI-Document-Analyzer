# Questionnaire Field Mappings - Revised Design
## AI Document Analyzer - Bardavid Law

**Date:** January 12, 2026  
**Version:** 2.0 (Revised)
**Purpose:** Define comprehensive field mappings including family members and history records

---

## Design Principles

1. **Everything requires approval** - No automatic updates; all changes reviewed and editable
2. **Family members are full contacts** - Spouse, children, parents can be searched, linked, or created
3. **History is structured data** - Address, employment, education stored as reviewable records
4. **Approval window is fully editable** - User can modify any field, contact, or relationship before applying

---

## Data Model

### Primary Contact Data
Fields that update the main client's Contact and ContactBiographic records.

### Family Member Data
Each family member (spouse, children, parents) is treated as a potential separate contact:
- **Search existing contacts** by name, A-number, DOB
- **Link to existing contact** if found
- **Create new contact** if not found
- **Update existing linked contact** with new data

### History Data
Structured records that can be:
- Stored as case notes with formatted tables
- Exported for form preparation
- Reviewed and edited in approval window

---

## InfoTems Available Fields

### Contact Record Fields
| InfoTems Field | Description |
|----------------|-------------|
| `FirstName` | First/given name |
| `MiddleName` | Middle name |
| `LastName` | Last/family name |
| `Suffix` | Name suffix (Jr., III, etc.) |
| `CellPhone` | Mobile phone |
| `HomePhone` | Home phone |
| `WorkPhone` | Work phone |
| `EmailPersonal` | Personal email |
| `EmailWork` | Work email |
| `AddressLine1` | Street address line 1 |
| `AddressLine2` | Apt/Suite/Floor |
| `City` | City |
| `State` | State |
| `PostalZipCode` | ZIP code |
| `Employer` | Current employer name |
| `Occupation` | Job title/occupation |

### ContactBiographic Record Fields
| InfoTems Field | Description |
|----------------|-------------|
| `AlienNumber` | A-Number (9 digits) |
| `SSN` | Social Security Number |
| `BirthDate` | Date of birth |
| `BirthCity` | City of birth |
| `BirthState` | State/province of birth |
| `BirthCountry` | Country of birth |
| `Gender` | Male/Female |
| `MaritalStatus` | Single/Married/Divorced/Widowed |
| `NativeLanguage` | Primary language |
| `Citizenship1Country` | Country of citizenship |
| `Citizenship2Country` | Second citizenship (if any) |
| `CurrentImmigrationStatus` | Immigration status |
| `DateOfEntryToUsa` | Most recent US entry date |

---

## Family Member Structure

Each family member extracted from questionnaire:

```python
{
    'relationship': 'spouse' | 'child' | 'father' | 'mother' | 'sibling',
    'extracted_data': {
        'first_name': str,
        'middle_name': str,
        'last_name': str,
        'date_of_birth': date,
        'city_of_birth': str,
        'state_of_birth': str,
        'country_of_birth': str,
        'citizenship': str,
        'gender': str,
        'a_number': str,
        'ssn': str,
        'current_address': str,
        'immigration_status': str,
        'date_of_entry': date,
        # Relationship-specific fields
        'date_of_marriage': date,  # spouse only
        'include_in_application': bool,  # spouse/children
    },
    'matched_contact': {
        'contact_id': int | None,
        'match_confidence': float,
        'match_method': 'a_number' | 'name_dob' | 'name_only' | None,
    },
    'action': 'link_existing' | 'create_new' | 'update_existing' | 'skip',
    'fields_to_update': [...],  # if updating existing
}
```

---

## History Record Structure

### Address History
```python
{
    'type': 'address',
    'records': [
        {
            'address_line1': str,
            'address_line2': str,
            'city': str,
            'state': str,
            'zip_code': str,
            'country': str,
            'from_date': date,
            'to_date': date | 'Present',
            'is_current': bool,
            'is_mailing': bool,
            'is_foreign': bool,
        },
        ...
    ]
}
```

### Employment History
```python
{
    'type': 'employment',
    'records': [
        {
            'employer_name': str,
            'occupation': str,
            'address': str,
            'city': str,
            'state': str,
            'zip_code': str,
            'country': str,
            'from_date': date,
            'to_date': date | 'Present',
            'is_current': bool,
        },
        ...
    ]
}
```

### Education History
```python
{
    'type': 'education',
    'records': [
        {
            'school_name': str,
            'school_type': 'Primary' | 'Middle' | 'High School' | 'University' | 'Trade School' | 'Advanced Degree',
            'address': str,
            'city': str,
            'state': str,
            'country': str,
            'from_date': date,
            'to_date': date,
        },
        ...
    ]
}
```

### Travel History
```python
{
    'type': 'travel',
    'records': [
        {
            'departure_date': date,
            'return_date': date,
            'countries_visited': [str],
            'duration_days': int,
        },
        ...
    ]
}
```

### Criminal/Arrest History
```python
{
    'type': 'criminal',
    'records': [
        {
            'date_of_arrest': date,
            'place_of_arrest': str,
            'charges': str,
            'outcome': str,
            'punishment': str,
        },
        ...
    ]
}
```

---

## Approval Window Design

### Tab Structure

**Tab 1: Primary Contact**
- Side-by-side comparison: Current InfoTems ↔ Extracted Data
- Each field editable
- Checkboxes to approve/reject individual changes
- "Apply Selected Changes" button

**Tab 2: Family Members**
For each family member (spouse, children, parents):
- Extracted data display (editable)
- Search panel: "Find in InfoTems" button
  - Search by A-number (exact match)
  - Search by Name + DOB (fuzzy match)
  - Search by Name only (multiple results possible)
- Match results list with selection
- Actions:
  - "Link to Selected Contact" - associates family member
  - "Create New Contact" - creates contact with extracted data
  - "Update Linked Contact" - updates existing linked contact
  - "Skip" - don't process this family member
- If linked/created, show field comparison for updates

**Tab 3: Address History**
- Table view of all addresses extracted
- Editable inline
- Columns: Address, City, State, ZIP, Country, From, To, Current?, Mailing?
- Add/Remove row buttons
- "Save to Case Notes" button (formatted table)

**Tab 4: Employment History**
- Table view of all employment records
- Editable inline
- Columns: Employer, Title, Address, City, State, Country, From, To, Current?
- Current employment auto-populates primary contact fields
- Add/Remove row buttons
- "Save to Case Notes" button

**Tab 5: Education History**
- Table view of all education records
- Editable inline
- Columns: School, Type, City, State, Country, From, To
- Add/Remove row buttons
- "Save to Case Notes" button

**Tab 6: Other Information**
- Travel history (if applicable)
- Criminal history (if applicable)
- Prior immigration applications
- Free-text notes/comments
- All editable
- "Save to Case Notes" button

### Bottom Action Bar
- "Apply All Approved Changes" - executes all approved updates
- "Save Draft" - saves current state without applying
- "Cancel" - discard all changes
- Progress indicator showing what will be updated

---

## Workflow

### Step 1: Document Upload & Extraction
1. User uploads document (PDF, image)
2. AI identifies document type (questionnaire or other)
3. AI extracts all data with confidence scores
4. System detects questionnaire type if applicable

### Step 2: Primary Contact Matching
1. Extract A-number or name from document
2. Search InfoTems for matching contact
3. If multiple matches, present selection dialog
4. If no match, offer to create new contact
5. Load current contact data for comparison

### Step 3: Family Member Processing
For each family member found:
1. Display extracted data
2. Auto-search for existing contacts (by A-number first, then name+DOB)
3. Present matches with confidence scores
4. User selects action: Link, Create, Update, or Skip
5. If linking/updating, show field-level comparison

### Step 4: History Data Processing
1. Parse all history sections (address, employment, education, etc.)
2. Organize into structured records
3. Identify current vs. historical entries
4. Flag inconsistencies or gaps

### Step 5: Approval Window
1. Present all data in tabbed interface
2. User reviews and edits all fields
3. User approves/rejects individual changes
4. User confirms family member actions
5. User reviews history data

### Step 6: Apply Changes
Only after explicit approval:
1. Update primary contact (Contact + ContactBiographic)
2. Process family members (create/link/update as approved)
3. Save history data to case notes (formatted)
4. Log all changes made

---

## Note Format for History Data

When saving history to case notes, use structured format:

```
=== ADDRESS HISTORY ===
Updated: 01/12/2026

1. CURRENT ADDRESS
   123 Main Street, Apt 4B
   New York, NY 10001
   From: 03/2023 to Present

2. PREVIOUS ADDRESS
   456 Oak Avenue
   Brooklyn, NY 11201
   From: 01/2020 to 03/2023

3. PREVIOUS ADDRESS
   789 Pine Road
   Queens, NY 11375
   From: 06/2018 to 01/2020

=== EMPLOYMENT HISTORY ===
Updated: 01/12/2026

1. CURRENT EMPLOYER
   ABC Company
   Manager
   100 Business Blvd, New York, NY 10001
   From: 06/2021 to Present

2. PREVIOUS EMPLOYER
   XYZ Corp
   Assistant Manager
   200 Commerce St, Brooklyn, NY 11201
   From: 03/2019 to 06/2021

=== EDUCATION HISTORY ===
Updated: 01/12/2026

1. Universidad Nacional (University)
   San Salvador, El Salvador
   From: 2010 to 2014

2. Instituto Nacional (High School)
   San Salvador, El Salvador
   From: 2006 to 2010
```

---

## Implementation Priority

### Phase 1: Core Functionality
- [ ] Primary contact extraction and comparison
- [ ] Basic approval window with editable fields
- [ ] Apply changes to Contact + ContactBiographic

### Phase 2: Family Members
- [ ] Family member extraction
- [ ] Contact search functionality
- [ ] Link/Create/Update workflow
- [ ] Family member tab in approval window

### Phase 3: History Data
- [ ] Address history extraction and display
- [ ] Employment history extraction and display
- [ ] Education history extraction and display
- [ ] History tabs in approval window
- [ ] Save to case notes functionality

### Phase 4: Advanced Features
- [ ] Travel history
- [ ] Criminal history
- [ ] Prior applications tracking
- [ ] Batch processing multiple documents
- [ ] Export to form-filling tools

---

## Questionnaire Field Definitions

See `config.py` for complete field definitions for each questionnaire type.

Key changes from v1:
- Family member fields now have `family_member` attribute identifying relationship
- History fields now have `history_type` attribute (address/employment/education/travel/criminal)
- All fields remain editable in approval window regardless of mapping status
