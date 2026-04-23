# PTAB (trials, appeals, interferences)

Unified surface over USPTO ODP's PTAB endpoints. 15 original tools
collapsed to 4 via type discriminators on search, get, and list-by-parent
shapes.

## Tribunal types

The `type` discriminator surfaces legally distinct tribunals — don't treat
them interchangeably:

- **`proceeding`** — AIA trial proceedings (IPR, PGR, CBM, DER). Identified
  by trial number like `IPR2024-00001`.
- **`trial_decision`** — decisions issued in an AIA trial. Identified by
  document identifier.
- **`trial_document`** — documents filed in an AIA trial (petitions,
  responses, orders, etc.). Identified by document identifier.
- **`appeal_decision`** — ex parte appeal decisions (Board decisions on
  examiner rejections). Legally different from AIA trials; keyed by
  application number for listing, document identifier for single lookup.
- **`interference_decision`** — pre-AIA interference decisions. Legacy
  proceedings; keyed by interference number for listing, document
  identifier for single lookup.

## MCP tools

### `search_ptab(type, query, limit, offset)`

Search any of the five types by query. Returns a list of matching records
in that type's shape.

```python
# AIA trials mentioning "machine learning":
search_ptab(type="proceeding", query="machine learning")

# Ex parte appeals by a specific applicant:
search_ptab(type="appeal_decision", query="applicant:\"Anthropic PBC\"")
```

### `get_ptab(type, identifier)`

Fetch a single PTAB record by identifier.

- `type="proceeding"` → `identifier` is a trial number (`IPR2024-00001`).
- All other types → `identifier` is a document identifier from the
  corresponding `search_ptab` response.

```python
get_ptab(type="proceeding", identifier="IPR2024-00001")
get_ptab(type="trial_decision", identifier="document-id-here")
```

### `list_ptab_children(parent_type, parent_identifier, include)`

List decisions or documents attached to a parent record.

| `parent_type` | `parent_identifier` | valid `include` |
|---|---|---|
| `trial` | Trial number (`IPR2024-00001`) | `decisions`, `documents`, `both` |
| `application` | USPTO application number | `decisions` only (appeals) |
| `interference` | Interference number | `decisions` only |

```python
# All decisions + documents in an AIA trial:
list_ptab_children(parent_type="trial", parent_identifier="IPR2024-00001", include="both")

# Appeals for a specific application:
list_ptab_children(parent_type="application", parent_identifier="16123456")
```

### `download_ptab_document(document_identifier)`

Stays separate from the unified PDF download — PTAB documents are a
different document class (trial filings) with their own identifier space
and download path.

## Python API (raw)

Source-specific methods on `UsptoOdpClient` remain for direct Python use:

```python
from patent_client_agents.uspto_odp import UsptoOdpClient

async with UsptoOdpClient() as client:
    # Search
    proceedings = await client.search_trial_proceedings(query="...")
    decisions = await client.search_trial_decisions(query="...")
    documents = await client.search_trial_documents(query="...")
    appeals = await client.search_appeal_decisions(query="...")
    interferences = await client.search_interference_decisions(query="...")

    # Lookup
    proceeding = await client.get_trial_proceeding(trial_number)
    decision = await client.get_trial_decision(document_identifier)
    # (... similar getters for appeal_decision, interference_decision, trial_document)

    # List by parent
    trial_decisions = await client.get_trial_decisions_by_trial(trial_number)
    trial_documents = await client.get_trial_documents_by_trial(trial_number)
    application_appeals = await client.get_appeal_decisions_by_number(application_number)
    interference_decisions = await client.get_interference_decisions_by_number(interference_number)
```

No library-level fusion — the MCP discriminators dispatch directly to these
client methods. Python consumers already have the granular API.
