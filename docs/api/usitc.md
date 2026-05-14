# USITC (EDIS / DataWeb / HTS / IDS)

Access US International Trade Commission data: EDIS investigation dockets and documents (Section 337 patent enforcement), DataWeb import/export statistics, HTS tariff codes, and IDS intellectual-property investigation index. EDIS and DataWeb need free tokens; HTS and IDS are fully public.

## Auth

| Sub‑surface | Env var | How to obtain | Notes |
|---|---|---|---|
| EDIS (documents, attachments) | `USITC_EDIS_TOKEN` | Log in at [edis.usitc.gov](https://edis.usitc.gov) via Login.gov → profile menu → "API Token Generator" | JWT; ~2 weeks lifetime |
| DataWeb (trade reports) | `USITC_DATAWEB_TOKEN` | Mint at [dataweb.usitc.gov](https://dataweb.usitc.gov) under your account | |
| HTS (tariff codes) | — | None | Public |
| IDS (IP investigations) | — | None | Public |

EDIS rejects download requests without auth even for public documents. `EdisClient.require_auth()` raises a clear `AuthenticationError` with the URL to mint a token if the env var isn't set.

## Quick Start

```python
from patent_client_agents.usitc import (
    DataWebClient,
    EdisClient,
    HtsClient,
    IdsClient,
)
from patent_client_agents.usitc.client import build_dataweb_query

# 1. EDIS — Section 337 investigation
async with EdisClient() as client:
    investigations = await client.list_investigations(
        investigation_number="337-TA-1380",
    )
    documents = await client.list_documents(
        investigationNumber="337-TA-1380",
        documentType="Order",
    )
    attachments = await client.list_attachments(document_id=documents[0].id)
    pdf = await client.download_attachment(documents[0].id, attachments[0].id)

# 2. HTS lookup (public)
async with HtsClient() as client:
    results = await client.search(keyword="semiconductor")

# 3. DataWeb report (needs USITC_DATAWEB_TOKEN)
query = build_dataweb_query(
    trade_type="Import",
    classification="HTS",
    years=["2024"],
    data_metrics=["CONS_CUSTOMS_VALUE"],
    commodities=["8542"],
    granularity="6",
)
async with DataWebClient() as client:
    report = await client.run_report(query)

# 4. IDS — IP investigation index (public)
async with IdsClient() as client:
    ip_investigations = await client.list_investigations()
```

## EDIS functions

Electronic Document Information System. The patent‑relevant surface — every Section 337 (`337-TA-*`) investigation lives here.

| Method | Description |
|---|---|
| `list_investigations(investigation_number, investigation_phase, **filters)` | Investigation index with phase / type / status filters |
| `list_documents(**filters)` | Document index for an investigation (100 results per page) |
| `list_attachments(document_id)` | Per-document attachment listing |
| `download_attachment(document_id, attachment_id)` | Download a specific attachment (base64-encoded payload) |

## DataWeb functions

Tariff and trade statistics.

| Method | Description |
|---|---|
| `run_report(query)` | Execute a DataWeb query (use `build_dataweb_query` to construct one) |
| `list_saved_queries()` | List saved-query templates on the account |

## HTS functions

Harmonized Tariff Schedule lookup.

| Method | Description |
|---|---|
| `search(keyword)` | Keyword search for tariff codes |
| `export_range(start, end)` | Export a range of HTS codes |

## IDS functions

Intellectual-property investigation index.

| Method | Description |
|---|---|
| `list_investigations()` | List all IDS investigations (~4000 records in one 11 MB payload) |

## Investigation type codes

| Type | Description |
|------|-------------|
| `337` | Unfair import practices (typically patent) |
| `AD` | Antidumping |
| `CVD` | Countervailing duty |
| `201` | Safeguard |

## Stability Notes

- EDIS, DataWeb, and HTS APIs are documented but undergo periodic refactors. The connector includes a JWT expiry-decode for EDIS that surfaces `AuthenticationError` proactively (rather than letting Akamai 503 the request when the token expires).
- EDIS investigations don't return a total count in `list_documents` — pagination walks pages until the first empty response. The MCP `download_usitc_investigation_documents` tool does this in parallel batches of 8 pages.
- EDIS PDFs are routinely huge (often hundreds of MB for exhibits); the bulk-download MCP tool caps at 25 attachments per call.

## MCP Tool Surface

| Tool | Description |
|---|---|
| `search_usitc_investigations` | EDIS investigation search (number, phase, type, status filters) |
| `search_usitc_documents` | EDIS document search with optional server-side date filtering + pagination |
| `list_usitc_attachments` | Attachments for a single EDIS document |
| `download_usitc_attachment` | Download one EDIS attachment; returns signed `download_url` |
| `download_usitc_investigation_documents` | Bulk download (≤25 attachments) for an investigation with filters |
| `search_hts_tariffs` | HTS keyword search |
| `run_dataweb_report` | Run a DataWeb trade-stats report (needs `USITC_DATAWEB_TOKEN`) |
| `list_ids_investigations` | IDS investigation listing with substring filters |

EDIS attachments register the `pca://usitc/documents/{doc_id}/attachments/{att_id}` download fetcher so resource-aware MCP clients (CoWork) can stream PDFs via `resources/read`.
