# USITC (EDIS / DataWeb / HTS / IDS)

US International Trade Commission data: EDIS investigation dockets and documents (Section 337 patent enforcement), DataWeb trade statistics, HTS Harmonized Tariff Schedule, and the IDS intellectual-property investigation index. EDIS and DataWeb need free user-minted tokens; HTS and IDS are public.

## Source

| | |
|---|---|
| Module | `patent_client_agents.usitc` |
| Client | `EdisClient`, `DataWebClient`, `HtsClient`, `IdsClient` (one per sub-surface) |
| Base URL | `https://edis.usitc.gov/data`, `https://datawebws.usitc.gov/dataweb`, `https://hts.usitc.gov/reststop`, `https://ids.usitc.gov` |
| Auth | EDIS: `USITC_EDIS_TOKEN` (JWT, ~2 wk lifetime). DataWeb: `USITC_DATAWEB_TOKEN`. HTS, IDS: none. |
| Rate limits | Not published; EDIS surfaces expired tokens as Akamai 503/403, so the client pre-decodes JWT `exp` and raises `AuthenticationError` early |
| Status | Active |

## Authentication

EDIS rejects download requests without a Bearer token even for public documents. Mint a token at [edis.usitc.gov](https://edis.usitc.gov) via Login.gov → Profile → "API Token Generator". Set `USITC_EDIS_TOKEN`.

DataWeb requires `USITC_DATAWEB_TOKEN`, minted on the DataWeb account page.

`EdisClient.require_auth()` and `DataWebClient` both surface a clear `AuthenticationError` with the mint URL when the env var is missing.

## API Endpoints

| Surface | Base URL | Coverage |
|---|---|---|
| EDIS | `https://edis.usitc.gov/data` | Investigations, documents, attachments — needs Bearer JWT |
| DataWeb | `https://datawebws.usitc.gov/dataweb` | Trade-stats query/report endpoints — needs Bearer token |
| HTS | `https://hts.usitc.gov/reststop` | Tariff code search / range export — public |
| IDS | `https://ids.usitc.gov` | IP investigation index — public |

Override any of these with `USITC_EDIS_BASE_URL` / `USITC_DATAWEB_BASE_URL` / `USITC_HTS_BASE_URL` / `USITC_IDS_BASE_URL` for staging/testing.

## Library API

```python
from patent_client_agents.usitc import (
    DataWebClient,
    EdisClient,
    HtsClient,
    IdsClient,
)
from patent_client_agents.usitc.client import build_dataweb_query

# EDIS — Section 337 enforcement
async with EdisClient() as client:
    docs = await client.list_documents(
        investigationNumber="337-TA-1380",
        documentType="Order",
    )

# HTS — public lookup
async with HtsClient() as client:
    results = await client.search(keyword="semiconductor")

# DataWeb — trade stats
async with DataWebClient() as client:
    query = build_dataweb_query(
        trade_type="Import",
        classification="HTS",
        years=["2024"],
        data_metrics=["CONS_CUSTOMS_VALUE"],
        commodities=["8542"],
        granularity="6",
    )
    report = await client.run_report(query)

# IDS — IP investigations index
async with IdsClient() as client:
    investigations = await client.list_investigations()
```

### EDIS methods

| Method | Description |
|---|---|
| `list_investigations(investigation_number, investigation_phase, **filters)` | Investigation index with type / status filters |
| `list_documents(**filters)` | Document index (100 per page) |
| `list_attachments(document_id)` | Per-document attachment listing |
| `download_attachment(document_id, attachment_id)` | Download an attachment (base64-encoded) |

### DataWeb methods

| Method | Description |
|---|---|
| `run_report(query)` | Execute a DataWeb query (compose via `build_dataweb_query`) |
| `list_saved_queries()` | Saved-query templates |

### HTS / IDS methods

| Method | Description |
|---|---|
| `HtsClient.search(keyword)` | HTS keyword search |
| `HtsClient.export_range(start, end)` | HTS code range export |
| `IdsClient.list_investigations()` | IDS IP investigation index (~4000 records in one 11 MB payload) |

## Investigation type codes

| Type | Description |
|---|---|
| `337` | Unfair import practices (typically patent) |
| `AD` | Antidumping |
| `CVD` | Countervailing duty |
| `201` | Safeguard |

## MCP Tools

| Tool | Description |
|---|---|
| `search_usitc_investigations` | EDIS investigation search |
| `search_usitc_documents` | EDIS document search; server-side date filter + pagination |
| `list_usitc_attachments` | Attachments for one EDIS document |
| `download_usitc_attachment` | Download a single attachment; returns signed `download_url` |
| `download_usitc_investigation_documents` | Bulk-download (≤25 attachments) with type/date filters |
| `search_hts_tariffs` | HTS keyword search |
| `run_dataweb_report` | DataWeb trade-stats report |
| `list_ids_investigations` | IDS investigation listing with substring filters |

EDIS attachments are addressable as `pca://usitc/documents/{doc_id}/attachments/{att_id}` for resource-aware MCP clients.
