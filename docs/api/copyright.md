# US Copyright Office

Read-only access to the [Copyright Public Records System](https://publicrecords.copyright.gov/) — the US Copyright Office's search index over registrations (post‑1978 + digitized card catalog) and recorded documents (transfers, assignments, licenses). The connector wraps the undocumented JSON API behind the web UI; no authentication required.

## Auth

None. The Copyright Office publishes the records search index for free. The server *does* reject HTTP/1.1 requests with a 500 — the client uses HTTP/2 automatically (BaseAsyncClient's `HTTP2 = True`).

## Quick Start

```python
from patent_client_agents.copyright import CopyrightClient

async with CopyrightClient() as client:
    response = await client.search("Mickey Mouse")
    for record in response.records:
        print(record.copyright_number_for_display, record.title_of_work)

    # Lookup by registration or by name
    by_title = await client.search_by_title("The Great Gatsby")
    by_name = await client.search_by_name("F. Scott Fitzgerald Estate")
```

## Functions

| Method | Description |
|---|---|
| `search(query, field, page, page_size, sort_order)` | Search across all fields (`field="keyword"`), titles, or claimant names |
| `search_by_title(title, page, page_size)` | Convenience wrapper for `field="title"` |
| `search_by_name(name, page, page_size)` | Convenience wrapper for `field="name"` (claimant) |
| `get_record(public_records_id)` | Lookup a single record by its public records ID |

## Response Shape

`SearchResponse` carries:

- `metadata` — `took_ms`, `hit_count`, `query`, etc.
- `histogram` — facet counts for `type_of_record`, `type_of_work`, `registration_class`, `registration_status`, `system_of_origin`, `recordation_item_type`
- `records` — list of `CopyrightRecord` with title(s), registration number(s), claimants, dates, work type, etc.

Records originating in `voyager` are post‑1978; `card_catalog` records are the digitized pre‑1978 backfile. Some fields (e.g. SR‑prefix sound recordings) arrive as scalars instead of arrays — the model coerces those to one‑element lists rather than rejecting the row.

## Examples

```python
# Sort the most-recent registrations for a claimant
recent = await client.search("Disney", field="name", sort_order="desc", page_size=25)

# Pull a specific record
detail = await client.get_record("voyager_67890")
print(detail.registration_status, detail.first_published_date)
```

## Stability Notes

- The API is undocumented (no service contract). Response shape has been stable through the migration to `publicrecords.copyright.gov` (the legacy `cocatalog.loc.gov` web UI is the same backend).
- Detail pages return through the search index — there is no dedicated detail endpoint, so `get_record` searches by ID and filters.
- HTTP/2 is non-negotiable: the server returns 500 on HTTP/1.1.

## MCP Tool Surface

Two tools register unconditionally (no env gate — Copyright Office is public):
`search_copyright`, `get_copyright_record`.
