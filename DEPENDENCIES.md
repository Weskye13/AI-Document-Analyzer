# Dependencies - AI Document Analyzer

## Hub-Spoke Architecture

This project follows a **hub-spoke architecture** for InfoTems integration:

```
                    ┌─────────────────────────────────────┐
                    │         HUB (Single Source)         │
                    │                                     │
                    │   infotems_hybrid_client.py         │
                    │   Location: ../New Official         │
                    │            Infotems API/            │
                    │                                     │
                    │   - All API endpoints               │
                    │   - All field names                 │
                    │   - All data structures             │
                    │   - Authentication                  │
                    │   - Connection handling             │
                    └──────────────┬──────────────────────┘
                                   │
                                   │ (imports from)
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│    SPOKE 1    │        │    SPOKE 2    │        │    SPOKE 3    │
│               │        │               │        │               │
│ AI Document   │        │  Full Wrapper │        │   Mail GUI    │
│   Analyzer    │        │               │        │               │
│               │        │               │        │               │
│ (this project)│        │  (MCP server) │        │ (processing)  │
└───────────────┘        └───────────────┘        └───────────────┘
```

## The Golden Rule

**NEVER make direct API calls to InfoTems from spoke projects.**

All InfoTems operations MUST go through `InfotemsHybridClient`.

## InfoTems Hybrid Client Location

```
Absolute Path:
C:\Users\Josh\Dropbox\Law Office of Joshua E. Bardavid\Administrative Docs\Scripts\New Official Infotems API\infotems_hybrid_client.py

Relative to this project:
..\New Official Infotems API\infotems_hybrid_client.py
```

## How This Project Uses the Hub

### config.py
- Adds the InfoTems API path to `sys.path`
- Provides credentials from environment variables
- Does NOT make any API calls

### infotems_comparator.py
- Imports `InfotemsHybridClient` from the hub
- Creates single client instance
- All search/create/update operations go through that client
- Documents which hub methods are used

### approval_gui.py
- Receives comparator instance (which has the client)
- Passes search requests to comparator
- Does NOT directly interact with InfoTems

### main.py
- Orchestrates the workflow
- Creates comparator (which creates client)
- Does NOT directly interact with InfoTems

## Methods We Use from the Hub

| Hub Method | Used In | Purpose |
|------------|---------|---------|
| `get_contact()` | comparator | Retrieve contact by ID |
| `search_contacts()` | comparator | Search by name |
| `search_by_anumber()` | comparator | Search by A-number |
| `create_contact()` | comparator | Create new contact |
| `update_contact()` | comparator | Update contact (PATCH) |
| `get_contact_biography()` | comparator | Get biographic data |
| `create_contact_biographic()` | comparator | Create biographic |
| `update_contact_biographic()` | comparator | Update biographic (PATCH) |
| `create_note()` | comparator | Create case notes |

## Adding New Functionality

### If you need a new InfoTems operation:

1. **Check the hub** - Does `infotems_hybrid_client.py` have the method?

2. **If YES** - Import and use it:
   ```python
   # In infotems_comparator.py
   result = self.client.existing_method(params)
   ```

3. **If NO** - Add it to the hub first:
   ```python
   # In infotems_hybrid_client.py
   def new_method(self, params):
       """Document the method."""
       return self._official_request("GET", "/endpoint")
   ```
   Then use it from the spoke.

4. **NEVER** add direct API calls to this project.

## Why This Architecture?

1. **Single Source of Truth** - One place defines all InfoTems interactions
2. **Consistency** - All projects use the same field names and structures
3. **Maintainability** - API changes only need updates in one place
4. **Safe Updates** - HybridClient uses PATCH for safe partial updates
5. **Authentication** - Centralized credential and token handling

## Verification Checklist

Before committing changes, verify:

- [ ] No `requests` imports in this project (except requirements.txt)
- [ ] No `intranet.infotems.com` URLs in this project
- [ ] No direct HTTP calls to InfoTems
- [ ] All InfoTems operations go through `self.client.*` methods
- [ ] New methods needed? Added to hub first

## Related Projects Using the Same Hub

- **Full Wrapper** - Practice management application
- **Mail GUI** - Mail processing system
- **MCP Server** - Claude AI integration

All these projects import from the same `infotems_hybrid_client.py`.
