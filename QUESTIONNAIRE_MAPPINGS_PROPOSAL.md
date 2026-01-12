# Questionnaire Field Mappings Proposal
## AI Document Analyzer - Bardavid Law

**Date:** January 12, 2026  
**Purpose:** Define hardcoded field mappings for standard questionnaires to InfoTems

---

## Overview

This document proposes field mappings from the firm's standard questionnaires to InfoTems Contact and ContactBiographic records. These mappings can be hardcoded since the questionnaires are standardized forms used repeatedly.

**Important Notes:**
- User approval is still required before any updates (handwriting may be misread, data may be incorrect)
- These mappings are for the **primary client** only (spouse, children, parents are informational)
- Fields marked with `[BIOGRAPHIC]` go to ContactBiographic record
- Fields marked with `[CONTACT]` go to Contact record
- Fields marked with `[INFO ONLY]` are extracted but not mapped to InfoTems (for reference/case notes)

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

## Questionnaire Mappings

### 1. Consult Questionnaire (`consult_questionnaire`)
**Purpose:** Initial consultation intake  
**Languages:** English, Spanish, Creole

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Last (family) name | `LastName` | CONTACT |
| First (given) name | `FirstName` | CONTACT |
| Middle name | `MiddleName` | CONTACT |
| Date of birth | `BirthDate` | BIOGRAPHIC |
| Country of birth | `BirthCountry` | BIOGRAPHIC |
| Street Address | `AddressLine1` | CONTACT |
| City | `City` | CONTACT |
| State | `State` | CONTACT |
| Zip | `PostalZipCode` | CONTACT |
| Phone number(s) | `CellPhone` | CONTACT |
| Email address | `EmailPersonal` | CONTACT |
| Alien number | `AlienNumber` | BIOGRAPHIC |
| Current immigration status | `CurrentImmigrationStatus` | BIOGRAPHIC |
| Date of entry into US | `DateOfEntryToUsa` | BIOGRAPHIC |
| Primary/Best language | `NativeLanguage` | BIOGRAPHIC |
| Manner of entry | - | INFO ONLY |
| Prior entries/removals | - | INFO ONLY |
| Harm/fear in country | - | INFO ONLY |
| Criminal history | - | INFO ONLY |
| Removal proceedings info | - | INFO ONLY |

---

### 2. 589 Questionnaire - Asylum (`asylum_questionnaire`)
**Purpose:** I-589 Asylum Application  
**Languages:** English, Spanish, French, Chinese, Russian, Haitian Creole

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| A-Number | `AlienNumber` | BIOGRAPHIC |
| U.S. Social Security Number | `SSN` | BIOGRAPHIC |
| Last (Family) Name | `LastName` | CONTACT |
| First (Given) Name | `FirstName` | CONTACT |
| Middle Name | `MiddleName` | CONTACT |
| Street Number and Name | `AddressLine1` | CONTACT |
| Apartment, Suite, Floor | `AddressLine2` | CONTACT |
| City or Town | `City` | CONTACT |
| State | `State` | CONTACT |
| ZIP Code | `PostalZipCode` | CONTACT |
| Gender | `Gender` | BIOGRAPHIC |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| City of Birth | `BirthCity` | BIOGRAPHIC |
| State/Province of Birth | `BirthState` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Country of Citizenship | `Citizenship1Country` | BIOGRAPHIC |
| Ethnicity | - | INFO ONLY |
| Race | - | INFO ONLY |
| Religion | - | INFO ONLY |
| Height | - | INFO ONLY |
| Weight | - | INFO ONLY |
| Eye Color | - | INFO ONLY |
| Hair Color | - | INFO ONLY |
| Best/first language | `NativeLanguage` | BIOGRAPHIC |
| Passport country | - | INFO ONLY |
| Passport number | - | INFO ONLY |
| Passport issue date | - | INFO ONLY |
| Passport expiry date | - | INFO ONLY |
| Immigration status at entry | `CurrentImmigrationStatus` | BIOGRAPHIC |
| Date of Entry | `DateOfEntryToUsa` | BIOGRAPHIC |
| Place/Port of Entry | - | INFO ONLY |
| Relationship status | `MaritalStatus` | BIOGRAPHIC |
| **Spouse Information** | - | INFO ONLY (separate contact) |
| **Children Information** | - | INFO ONLY (separate contacts) |
| **Parents Information** | - | INFO ONLY |
| **Address History** | - | INFO ONLY |
| **Employment History** | `Employer`, `Occupation` (current only) | CONTACT |
| **Education History** | - | INFO ONLY |
| **Criminal History** | - | INFO ONLY |

---

### 3. N-400 Questionnaire - Naturalization (`n400_questionnaire`)
**Purpose:** Naturalization/Citizenship Application  
**Languages:** English, Spanish

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Family Name (Last Name) | `LastName` | CONTACT |
| Given Name (First Name) | `FirstName` | CONTACT |
| Middle Name | `MiddleName` | CONTACT |
| Other names used | - | INFO ONLY |
| Gender | `Gender` | BIOGRAPHIC |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Country of Citizenship | `Citizenship1Country` | BIOGRAPHIC |
| Date became LPR | `DateOfEntryToUsa` | BIOGRAPHIC |
| Marital Status | `MaritalStatus` | BIOGRAPHIC |
| Number of marriages | - | INFO ONLY |
| **Spouse Information** | - | INFO ONLY |
| **Employment/School History** | `Employer`, `Occupation` (current) | CONTACT |
| **Travel History** | - | INFO ONLY |
| **Children Information** | - | INFO ONLY |
| **Criminal/Arrest History** | - | INFO ONLY |
| Tax questions | - | INFO ONLY |
| Voting questions | - | INFO ONLY |

---

### 4. I-130 Questionnaire - Petitioner (`i130_petitioner_questionnaire`)
**Purpose:** Family Petition (USC/LPR Petitioner)  
**Languages:** English, Spanish

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Family name | `LastName` | CONTACT |
| Given name | `FirstName` | CONTACT |
| Middle name | `MiddleName` | CONTACT |
| Maiden name | - | INFO ONLY |
| Mobile/Cell Phone | `CellPhone` | CONTACT |
| Home Phone | `HomePhone` | CONTACT |
| Work Phone | `WorkPhone` | CONTACT |
| Email Address | `EmailPersonal` | CONTACT |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| Place of Birth (City, State, Country) | `BirthCity`, `BirthState`, `BirthCountry` | BIOGRAPHIC |
| Country of Citizenship | `Citizenship1Country` | BIOGRAPHIC |
| Social Security Number | `SSN` | BIOGRAPHIC |
| A-Number | `AlienNumber` | BIOGRAPHIC |
| Ethnicity | - | INFO ONLY |
| Race | - | INFO ONLY |
| Height | - | INFO ONLY |
| Weight | - | INFO ONLY |
| Eye Color | - | INFO ONLY |
| Hair Color | - | INFO ONLY |
| Marital Status | `MaritalStatus` | BIOGRAPHIC |
| Date of Marriage | - | INFO ONLY |
| Place of Marriage | - | INFO ONLY |
| Previous marriages | - | INFO ONLY |
| **Father Information** | - | INFO ONLY |
| **Mother Information** | - | INFO ONLY |
| Naturalization info (if USC) | - | INFO ONLY |
| LPR info (if LPR) | - | INFO ONLY |
| Current employment | `Employer`, `Occupation` | CONTACT |
| **Employment History** | - | INFO ONLY |
| **Address History** | `AddressLine1`, `City`, `State`, `PostalZipCode` (current) | CONTACT |
| Income information | - | INFO ONLY |

---

### 5. I-130A Questionnaire - Beneficiary (`i130_beneficiary_questionnaire`)
**Purpose:** Family Petition (Foreign National Beneficiary)  
**Languages:** English, Spanish

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| **Father Information** | - | INFO ONLY |
| **Mother Information** | - | INFO ONLY |
| Current Employer | `Employer` | CONTACT |
| Occupation | `Occupation` | CONTACT |
| **Employment History** | - | INFO ONLY |
| Current Address | `AddressLine1`, `City`, `State`, `PostalZipCode` | CONTACT |
| **Address History** | - | INFO ONLY |

*Note: This is supplemental - main beneficiary info usually from DS-260 or Adjustment questionnaire*

---

### 6. Adjustment Questionnaire - I-485 (`adjustment_questionnaire`)
**Purpose:** Adjustment of Status to Permanent Resident  
**Languages:** English, Spanish (bilingual form)

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Name | `FirstName`, `MiddleName`, `LastName` | CONTACT |
| Other names used | - | INFO ONLY |
| Address | `AddressLine1`, `City`, `State`, `PostalZipCode` | CONTACT |
| Phone | `CellPhone` | CONTACT |
| Email | `EmailPersonal` | CONTACT |
| Social Security Number | `SSN` | BIOGRAPHIC |
| Height | - | INFO ONLY |
| Weight | - | INFO ONLY |
| Eye Color | - | INFO ONLY |
| Hair Color | - | INFO ONLY |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| City of Birth | `BirthCity` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Passport Number | - | INFO ONLY |
| Date entered US | `DateOfEntryToUsa` | BIOGRAPHIC |
| Date left home country | - | INFO ONLY |
| Countries transited | - | INFO ONLY |
| Prior US entries | - | INFO ONLY |
| Arrest history | - | INFO ONLY |
| Marital status | `MaritalStatus` | BIOGRAPHIC |
| **Spouse Information** | - | INFO ONLY |
| **Children Information** | - | INFO ONLY |
| **Parents Information** | - | INFO ONLY |
| **Address History** | - | INFO ONLY |
| **Employment History** | `Employer`, `Occupation` (current) | CONTACT |

---

### 7. DS-260 Questionnaire (`ds260_questionnaire`)
**Purpose:** Immigrant Visa Application (Consular Processing)  
**Languages:** English, Spanish, Mandarin

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Name Provided | `FirstName`, `MiddleName`, `LastName` | CONTACT |
| Full Name in Native Language | - | INFO ONLY |
| Other Names Used | - | INFO ONLY |
| Sex | `Gender` | BIOGRAPHIC |
| Current Marital Status | `MaritalStatus` | BIOGRAPHIC |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| City of Birth | `BirthCity` | BIOGRAPHIC |
| State/Province of Birth | `BirthState` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Country of Nationality | `Citizenship1Country` | BIOGRAPHIC |
| Passport Document ID | - | INFO ONLY |
| Passport Issuing Country | - | INFO ONLY |
| Passport Issue/Expiry Dates | - | INFO ONLY |
| Other nationalities | `Citizenship2Country` | BIOGRAPHIC |
| Present Address | `AddressLine1`, `City`, `State`, `PostalZipCode` | CONTACT |
| **Address History** | - | INFO ONLY |
| Primary Phone | `CellPhone` | CONTACT |
| Secondary Phone | `HomePhone` | CONTACT |
| Work Phone | `WorkPhone` | CONTACT |
| Email Address | `EmailPersonal` | CONTACT |
| Social Media | - | INFO ONLY |
| **Father Information** | - | INFO ONLY |
| **Mother Information** | - | INFO ONLY |
| **Spouse Information** | - | INFO ONLY |
| **Previous Spouses** | - | INFO ONLY |
| **Children Information** | - | INFO ONLY |
| A-Number (if any) | `AlienNumber` | BIOGRAPHIC |
| **US Travel History** | - | INFO ONLY |
| **Visa History** | - | INFO ONLY |
| Primary Occupation | `Occupation` | CONTACT |
| Current Employer/School | `Employer` | CONTACT |
| **Countries Traveled** | - | INFO ONLY |
| **Military Service** | - | INFO ONLY |

---

### 8. 601A Questionnaire (`waiver_601a_questionnaire`)
**Purpose:** I-601A Unlawful Presence Waiver  
**Languages:** English, Spanish

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| A-Number | `AlienNumber` | BIOGRAPHIC |
| U.S. Social Security Number | `SSN` | BIOGRAPHIC |
| Last (Family) Name | `LastName` | CONTACT |
| First (Given) Name | `FirstName` | CONTACT |
| Middle Name | `MiddleName` | CONTACT |
| Other names used | - | INFO ONLY |
| Street Number and Name | `AddressLine1` | CONTACT |
| Apartment, Suite, Floor | `AddressLine2` | CONTACT |
| City or Town | `City` | CONTACT |
| State | `State` | CONTACT |
| ZIP Code | `PostalZipCode` | CONTACT |
| Gender | `Gender` | BIOGRAPHIC |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| City of Birth | `BirthCity` | BIOGRAPHIC |
| State/Province of Birth | `BirthState` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Country of Citizenship | `Citizenship1Country` | BIOGRAPHIC |
| Ethnicity | - | INFO ONLY |
| Race | - | INFO ONLY |
| Height | - | INFO ONLY |
| Weight | - | INFO ONLY |
| Eye Color | - | INFO ONLY |
| Hair Color | - | INFO ONLY |
| Immigration status at entry | `CurrentImmigrationStatus` | BIOGRAPHIC |
| Date of Entry | `DateOfEntryToUsa` | BIOGRAPHIC |
| Port of Entry | - | INFO ONLY |
| Prior entries | - | INFO ONLY |
| Relationship status | `MaritalStatus` | BIOGRAPHIC |
| **Spouse Information** | - | INFO ONLY |
| **Children Information** | - | INFO ONLY |
| **Parents Information** | - | INFO ONLY |
| **Criminal History** | - | INFO ONLY |
| Prior removal proceedings | - | INFO ONLY |

---

### 9. I-131F Questionnaire (`parole_in_place_questionnaire`)
**Purpose:** Parole in Place Application  
**Languages:** English, Spanish, Creole

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| A-Number | `AlienNumber` | BIOGRAPHIC |
| U.S. Social Security Number | `SSN` | BIOGRAPHIC |
| USCIS Online Account Number | - | INFO ONLY |
| Last (Family) Name | `LastName` | CONTACT |
| First (Given) Name | `FirstName` | CONTACT |
| Middle Name | `MiddleName` | CONTACT |
| Other names used | - | INFO ONLY |
| Street Number and Name | `AddressLine1` | CONTACT |
| Apartment, Suite, Floor | `AddressLine2` | CONTACT |
| City or Town | `City` | CONTACT |
| State | `State` | CONTACT |
| ZIP Code | `PostalZipCode` | CONTACT |
| Email address | `EmailPersonal` | CONTACT |
| Gender | `Gender` | BIOGRAPHIC |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| City of Birth | `BirthCity` | BIOGRAPHIC |
| State/Province of Birth | `BirthState` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Country of Citizenship | `Citizenship1Country` | BIOGRAPHIC |
| Ethnicity | - | INFO ONLY |
| Race | - | INFO ONLY |
| Height | - | INFO ONLY |
| Weight | - | INFO ONLY |
| Eye Color | - | INFO ONLY |
| Hair Color | - | INFO ONLY |
| **Spouse Information** (incl. SSN) | - | INFO ONLY |
| Date of Marriage | - | INFO ONLY |
| **Children Information** (incl. SSN) | - | INFO ONLY |
| Immigration status at entry | `CurrentImmigrationStatus` | BIOGRAPHIC |
| Date of Entry | `DateOfEntryToUsa` | BIOGRAPHIC |
| Port of Entry | - | INFO ONLY |
| Prior entries | - | INFO ONLY |
| Prior removal proceedings | - | INFO ONLY |
| **Criminal History** | - | INFO ONLY |

---

### 10. I-90 Questionnaire (`green_card_renewal_questionnaire`)
**Purpose:** Green Card Renewal/Replacement  
**Languages:** English, Spanish

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| A-Number | `AlienNumber` | BIOGRAPHIC |
| U.S. Social Security Number | `SSN` | BIOGRAPHIC |
| USCIS Online Account Number | - | INFO ONLY |
| Email Address | `EmailPersonal` | CONTACT |
| Current Card Issue Date | - | INFO ONLY |
| Current Card Expiry Date | - | INFO ONLY |
| Family Name (Last Name) | `LastName` | CONTACT |
| Given Name (First Name) | `FirstName` | CONTACT |
| Middle Name | `MiddleName` | CONTACT |
| Prior names | - | INFO ONLY |
| Street Number and Name | `AddressLine1` | CONTACT |
| Apt/Ste/Flr | `AddressLine2` | CONTACT |
| City or Town | `City` | CONTACT |
| State | `State` | CONTACT |
| ZIP Code | `PostalZipCode` | CONTACT |
| Country | - | INFO ONLY |
| Gender | `Gender` | BIOGRAPHIC |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| City/Town/Village of Birth | `BirthCity` | BIOGRAPHIC |
| Country of Birth | `BirthCountry` | BIOGRAPHIC |
| Ethnicity | - | INFO ONLY |
| Race | - | INFO ONLY |
| Height | - | INFO ONLY |
| Weight | - | INFO ONLY |
| Eye Color | - | INFO ONLY |
| Hair Color | - | INFO ONLY |
| Mother's Name | - | INFO ONLY |
| Father's Name | - | INFO ONLY |
| Place of First Entry | - | INFO ONLY |
| How obtained residency | - | INFO ONLY |
| Where became resident | - | INFO ONLY |
| Class of admission | - | INFO ONLY |
| Prior removal proceedings | - | INFO ONLY |
| Travel history | - | INFO ONLY |
| **Criminal History** | - | INFO ONLY |

---

### 11. FOIA Questionnaire (`foia_questionnaire`)
**Purpose:** Freedom of Information Act Request  
**Languages:** English, Spanish, Creole

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Last (family) name | `LastName` | CONTACT |
| First (given) name | `FirstName` | CONTACT |
| Middle name | `MiddleName` | CONTACT |
| Date of birth | `BirthDate` | BIOGRAPHIC |
| Country of birth | `BirthCountry` | BIOGRAPHIC |
| Street Address | `AddressLine1` | CONTACT |
| City | `City` | CONTACT |
| State | `State` | CONTACT |
| Zip | `PostalZipCode` | CONTACT |
| Phone number(s) | `CellPhone` | CONTACT |
| Email address | `EmailPersonal` | CONTACT |
| Alien number | `AlienNumber` | BIOGRAPHIC |
| Father's Full Name | - | INFO ONLY |
| Mother's Full Name | - | INFO ONLY |
| Current immigration status | `CurrentImmigrationStatus` | BIOGRAPHIC |
| Date of entry into US | `DateOfEntryToUsa` | BIOGRAPHIC |
| Manner of entry | - | INFO ONLY |
| ICE/DHS encounters | - | INFO ONLY |
| Prior entries/removals | - | INFO ONLY |
| Removal proceedings info | - | INFO ONLY |
| Criminal history | - | INFO ONLY |
| Prior immigration applications | - | INFO ONLY |
| Primary language | `NativeLanguage` | BIOGRAPHIC |

---

### 12. SIJ Questionnaire (`sij_questionnaire`)
**Purpose:** Special Immigrant Juvenile Status  
**Languages:** English, Spanish

| Questionnaire Field | InfoTems Field | Type |
|---------------------|----------------|------|
| Full Name | `FirstName`, `MiddleName`, `LastName` | CONTACT |
| Date of Birth | `BirthDate` | BIOGRAPHIC |
| Current Address | `AddressLine1`, `City`, `State`, `PostalZipCode` | CONTACT |
| Date started living there | - | INFO ONLY |
| Father's name | - | INFO ONLY |
| Father's birthplace | - | INFO ONLY |
| Father's current location | - | INFO ONLY |
| Mother's name | - | INFO ONLY |
| Mother's birthplace | - | INFO ONLY |
| Mother's current location | - | INFO ONLY |
| **Address History (28 years)** | - | INFO ONLY |

---

## Implementation Notes

### Questionnaire Detection
The AI should identify questionnaire type by:
1. Looking for header text (e.g., "Questionnaire for Asylum", "N-400", "I-130")
2. Checking for Bardavid Law letterhead/branding
3. Analyzing field structure and section names

### Multi-Language Support
The same questionnaire may be in different languages. The AI should:
1. Identify the language
2. Use language-appropriate OCR settings
3. Map fields based on structure (field order is consistent across translations)

### Data Normalization
Before comparison with InfoTems:
- **A-Numbers:** Strip "A" prefix, format as 9 digits
- **Dates:** Convert to YYYY-MM-DD format
- **Phone numbers:** Strip formatting, normalize to 10 digits
- **Names:** Proper case normalization
- **Gender:** Map to "Male" or "Female"
- **Marital Status:** Map to InfoTems values (Single, Married, Divorced, Widowed)

### Confidence Scoring
Different extraction confidence levels:
- **High (0.9+):** Clearly printed/typed text in designated field
- **Medium (0.7-0.9):** Handwritten but legible
- **Low (<0.7):** Unclear handwriting, partial text

### Family Members
Spouse, children, and parents data should be:
1. Extracted and displayed for review
2. Available as separate "Create New Contact" action
3. Not automatically merged into primary client record

### Address/Employment History
Historical data should be:
1. Extracted for reference
2. Available in a summary view
3. NOT automatically merged (only current info updates InfoTems)

---

## Approval Workflow

1. **Document Upload** → AI identifies questionnaire type
2. **Field Extraction** → AI extracts all fields with confidence scores
3. **Client Lookup** → Match to existing InfoTems contact (A-number or name)
4. **Comparison View** → Show current vs. proposed values
5. **User Review** → Approve/reject individual field changes
6. **Apply Changes** → Update InfoTems via PATCH API

---

## Next Steps

1. Review and confirm these mappings
2. Add any missing fields from questionnaires
3. Implement questionnaire-specific extraction templates
4. Add questionnaire type detection logic
5. Create family member handling workflow
