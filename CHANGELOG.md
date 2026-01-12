# Changelog

All notable changes to the AI Document Analyzer project.

---

## [2.4.0] - 2026-01-11

### Added - Enhanced Multi-Pass Extraction (Ralph Brainstormer Pattern)

Inspired by the "Debate & Consensus" workflow from ralph-brainstormer, this release adds a sophisticated multi-pass extraction system for significantly higher accuracy.

**New Files:**
- `enhanced_extractor.py` - Multi-pass extraction engine
- `extraction_validator.py` - Validation layer for logical consistency

**6 New Improvements:**

1. **Self-Critique Pass** - AI reviews its own extraction for errors
   - Checks for swapped values, OCR errors, format issues
   - Returns corrections with explanations
   
2. **Confidence-Based Re-Extraction** - Low-confidence fields get retried
   - Fields below 70% confidence are re-extracted with focused prompts
   - Only updates if confidence improves

3. **Cross-Validation Extraction** - Multiple prompt strategies find consensus
   - STRUCTURED: Direct JSON schema extraction
   - NARRATIVE: Describe document then extract
   - Merges best results from each strategy

4. **Validation Layer** - Logical consistency checks before comparison
   - Date consistency (DOB vs entry date vs marriage date)
   - A-number format validation
   - Required fields by document type
   - Name field validation (swapped names, all caps)
   - Low confidence flagging

5. **Iterative Improvement Loop** - Refine until quality threshold met
   - Maximum 3 iterations
   - Continues until validation errors resolved
   - Feeds errors back for targeted fixes

6. **Family Member Verification** - Two-pass extraction for family data
   - Verifies each family member exists in document
   - Extracts additional fields (DOB, citizenship, A-number)
   - Removes false positives

**Usage:**

```bash
# Enhanced mode (default)
python main.py document.pdf

# Basic single-pass mode
python main.py document.pdf --basic
```

**Metrics Tracking:**
- Iterations count
- Total API calls
- Strategies used
- Validation errors (initial vs final)
- Low confidence fields (initial vs final)
- Critique corrections made

---

## [2.3.0] - 2026-01-11

### Changed - History Records Now Proper InfoTems Records

**MAJOR**: History records are now saved as proper structured InfoTems records instead of notes.

| History Type | Old Method | New Method |
|--------------|------------|------------|
| Address | Note | `create_address()` |
| Employment | Note | `create_employment()` |
| Education | Note | `create_education()` |
| Travel | Note | `create_travel_history()` |

### Added

- `HistoryAction.SAVE_AS_RECORDS` - New default action for supported history types
- `HistorySet.supports_records` - Property to check if history type supports proper records
- `_apply_history_records()` - Routes history to appropriate API methods
- `_create_address_record()` - Creates Address records in InfoTems
- `_create_employment_record()` - Creates Employment records in InfoTems
- `_create_education_record()` - Creates Education records in InfoTems
- `_create_travel_record()` - Creates TravelHistory records in InfoTems
- `_create_history_note()` - Fallback for unsupported history types
- `_build_biographic_fields()` - Maps questionnaire data to ContactBiographic fields

### Enhanced - Family Member Creation

Family members now get full biographic data when created:

| Field | InfoTems Location |
|-------|-------------------|
| date_of_birth | ContactBiographic.BirthDate |
| city_of_birth | ContactBiographic.BirthCity |
| state_of_birth | ContactBiographic.BirthState |
| country_of_birth | ContactBiographic.BirthCountry |
| citizenship | ContactBiographic.Citizenship1Country |
| gender | ContactBiographic.Gender |
| a_number | ContactBiographic.AlienNumber |
| ssn | ContactBiographic.SSN |
| ethnicity | ContactBiographic.Ethnicity |
| race | ContactBiographic.Race |
| immigration_status | ContactBiographic.CurrentImmigrationStatus |
| date_of_entry | ContactBiographic.DateOfLastEntryToUSA |

### Enhanced - Relationship Fields

Complete mapping of relationship fields:

| Field | InfoTems Field | Status |
|-------|----------------|--------|
| place_marriage_ended | EndCity/State/Country | ✅ Added |
| resides_with_applicant | AreHouseholdMembers | ✅ Added (derived) |
| is_step | IsStep | ✅ Added |
| is_adopted | IsRelatedContactAdopted | ✅ Added |

---

## [2.2.0] - 2026-01-11

### Added - Full Family Member Relationship Linking

- `add_contact_relative()` integration for CREATE_NEW and LINK_EXISTING actions
- `search_contact_relationships()` for checking existing links
- `_build_relationship_kwargs()` maps questionnaire data to relationship fields
- `get_contact_relatives()` helper method

### Relationship Fields Supported

- Marriage dates (start_date, end_date)
- Marriage locations (start_city/state/country)
- Immigration flags:
  - are_filing_immigration_benefit_together
  - does_related_contact_reside_with_primary_contact
  - will_related_contact_accompany
  - will_related_contact_immigrate_later
- Prior spouse auto-marks as estranged

---

## [2.1.0] - 2026-01-11

### Changed - Hub/Spoke Architecture

- Established InfoTems Hybrid Client as SOLE source of truth for all API operations
- Added explicit dependency documentation in config.py header
- Updated class docstrings with available client methods
- Created TEST_HANDOFF.md for testing documentation

### Documentation

- DEPENDENCIES.md created
- All API operations documented with explicit method names

---

## [2.0.0] - 2026-01-10

### Added

- Family member search/link/create workflow
- History records: address, employment, education as structured data
- 6-tab approval GUI with full editability
- All changes require approval before applying
- 12 questionnaire types supported

### Questionnaires Supported

1. Consult
2. 589 Asylum
3. N-400 Citizenship
4. I-130 Petitioner
5. I-130 Beneficiary
6. I-485 Adjustment
7. DS-260 Immigrant Visa
8. I-601A Waiver
9. I-131F Parole
10. I-90 Green Card Renewal
11. FOIA Request
12. SIJ Special Immigrant Juvenile

---

## [1.0.0] - 2026-01-09

### Initial Release

- AI-powered document extraction using Claude Vision
- InfoTems comparison and update
- Basic approval workflow
- Support for PDF and image files

---

*Maintained by Law Office of Joshua E. Bardavid*
