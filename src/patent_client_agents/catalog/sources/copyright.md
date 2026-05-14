# US Copyright Office

Read-only access to the US Copyright Office's Copyright Public Records System (CPRS). Search and lookup over registrations (post‑1978 + digitized card catalog) and recorded documents (transfers, assignments, licenses). The connector wraps the undocumented JSON API behind `publicrecords.copyright.gov`.

## Source

| | |
|---|---|
| Module | `patent_client_agents.copyright` |
| Client | `CopyrightClient` |
| Base URL | `https://api.publicrecords.copyright.gov/search_service_external` |
| Auth | None (public) |
| Rate limits | Not published; client uses BaseAsyncClient SQLite cache |
| Status | Active |

## Authentication

None. The Copyright Office publishes its records search for free. Note: HTTP/2 is required — the server returns HTTP 500 on HTTP/1.1. `CopyrightClient` sets `HTTP2 = True` automatically.

## API Endpoints

The connector wraps a single search endpoint and reuses it for "detail" lookups by ID.

| Path | Method | Coverage |
|---|---|---|
| `/simple_search_dsl` | GET | Search across all fields, title, or claimant name; returns metadata + histogram facets + records |

## Library API

```python
from patent_client_agents.copyright import CopyrightClient

async with CopyrightClient() as client:
    response = await client.search("Mickey Mouse")
    for record in response.records:
        print(record.copyright_number_for_display, record.title_of_work)

    by_title = await client.search_by_title("The Great Gatsby")
    detail = await client.get_record("voyager_12345")
```

### Methods

| Method | Description |
|---|---|
| `search(query, field, page, page_size, sort_order)` | Search across all fields (`field="keyword"`), titles, or claimant names |
| `search_by_title(title, page, page_size)` | Convenience wrapper for `field="title"` |
| `search_by_name(name, page, page_size)` | Convenience wrapper for `field="name"` (claimant) |
| `get_record(public_records_id)` | Look up a single record by its public records ID (filtered search) |

## MCP Tools

| Tool | Description |
|---|---|
| `search_copyright` | Search registrations and recorded documents |
| `get_copyright_record` | Fetch a single record by its public records ID |

Both register unconditionally; no env gate.
