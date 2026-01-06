---
name: "ip_research"
description: "IP data research tools for patents. Use for patent searches, lookups, and citation analysis."
---

# IP Research Skill

Data connectors for intellectual property research using the ip_tools library.

## Quick Start

| Task | Example |
|------|---------|
| Fetch patent by number | `client.fetch("US10123456B2")` |
| Search patents | `client.search(query)` |
| Get citation data | `client.citations(patent_number)` |

### Library Source & Issues

**ip_tools** source: [parkerhancock/ip_tools](https://github.com/parkerhancock/ip_tools)

Report bugs, unexpected behavior, or feature requests as issues on the repository. Include the ip_tools version, minimal reproduction code, and relevant API responses if possible.

## Available Connectors

| Source | Module | Description |
|--------|--------|-------------|
| Google Patents | `ip_tools.google_patents` | Full-text search, patent documents, citations |
| USPTO ODP | `ip_tools.uspto_odp` | Open Data Portal - applications, PTAB, bulk data |
| USPTO Publications | `ip_tools.uspto_publications` | Granted patents full-text search (PPUBS) |
| USPTO Assignments | `ip_tools.uspto_assignments` | Patent ownership and assignment data |
| EPO OPS | `ip_tools.epo_ops` | European Patent Office Open Patent Services |
| JPO | `ip_tools.jpo` | Japan Patent Office (requires API credentials) |

## Common Research Tasks

### Fetch a Patent

```python
from ip_tools.google_patents import GooglePatentsClient

async with GooglePatentsClient() as client:
    patent = await client.fetch("US10123456B2")
```

### Search Patents

```python
from ip_tools.google_patents import GooglePatentsClient

async with GooglePatentsClient() as client:
    results = await client.search("machine learning neural network")
```

### Get Citations

```python
from ip_tools.google_patents import GooglePatentsClient

async with GooglePatentsClient() as client:
    citations = await client.citations("US10123456B2")
```

## Cache Management

All clients cache HTTP responses to `~/.cache/ip_tools/`. Use these APIs to manage the cache:

```python
from ip_tools.google_patents import GooglePatentsClient
from datetime import timedelta

# Set TTL (optional, default uses HTTP headers)
async with GooglePatentsClient(ttl_seconds=3600) as client:
    # Get cache statistics
    stats = await client.cache_stats()
    # stats.hit_rate, stats.entry_count, stats.size_mb

    # Clear all cached data
    await client.cache_clear()

    # Clear entries older than max_age
    await client.cache_clear_expired(max_age=timedelta(hours=1))

    # Invalidate by URL pattern (regex)
    await client.cache_invalidate(r"patents\.google\.com")
```

Disable caching entirely with `use_cache=False`:

```python
async with GooglePatentsClient(use_cache=False) as client:
    patent = await client.fetch("US10123456B2")  # Always fetches
```

## USPTO Open Data Portal (ODP)

The ODP module provides comprehensive USPTO data access. Requires `USPTO_ODP_API_KEY` environment variable.

### ODP Clients

| Client | Description |
|--------|-------------|
| `ApplicationsClient` | Patent applications, documents, family graphs |
| `BulkDataClient` | Bulk data product downloads |
| `PetitionsClient` | Petition decisions |
| `PtabTrialsClient` | IPR/PGR/CBM/DER proceedings |
| `PtabAppealsClient` | Ex parte appeals |
| `PtabInterferencesClient` | Interference decisions |

### Application Lookup

```python
from ip_tools.uspto_odp import ApplicationsClient

async with ApplicationsClient() as client:
    # Get application by number
    app = await client.get("16123456")

    # Get file wrapper documents
    docs = await client.get_documents("16123456")

    # Get assignment history
    assignments = await client.get_assignment("16123456")

    # Build patent family graph
    family = await client.get_family("16123456")
```

### Search Applications

```python
from ip_tools.uspto_odp import ApplicationsClient

async with ApplicationsClient() as client:
    results = await client.search(
        query="artificial intelligence",
        limit=25,
        sort="filingDate desc"
    )
```

### PTAB Trials (IPR/PGR)

```python
from ip_tools.uspto_odp import PtabTrialsClient

async with PtabTrialsClient() as client:
    # Search proceedings
    results = await client.search_proceedings(query="patent:US10123456")

    # Get proceeding by trial number
    proceeding = await client.get_proceeding("IPR2023-00001")

    # Get trial documents
    docs = await client.get_documents_by_trial("IPR2023-00001")

    # Get decisions
    decisions = await client.get_decisions_by_trial("IPR2023-00001")
```

### Bulk Data Downloads

```python
from ip_tools.uspto_odp import BulkDataClient

async with BulkDataClient() as client:
    # Search available products
    products = await client.search(query="grant")

    # Get product with file list
    product = await client.get_product(
        "PTGRXML",
        file_from_date="2024-01-01",
        file_to_date="2024-12-31"
    )
```

## Routing Logic

### Patent lookup
"Find patent US10123456" -> Use fetch with patent number

### Patent search
"Find patents related to X" -> Use search with keywords

### Citation analysis
"What patents cite US10123456?" -> Use citations method

### Application status
"What's the status of application 16/123,456?" -> Use ODP ApplicationsClient.get()

### PTAB proceedings
"Are there any IPRs against US10123456?" -> Use ODP PtabTrialsClient.search_proceedings()
