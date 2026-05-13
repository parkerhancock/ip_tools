# MPEP

Access the Manual of Patent Examining Procedure (MPEP) for searching
and retrieving patent examination guidance.

## First-time setup

`MpepClient` reads from a local SQLite/FTS5 corpus, **not** live USPTO.
The wheel ships the builder; build the snapshot once before the first
call:

```bash
patent-client-agents-build-mpep-corpus \
    --output ~/.cache/patent_client_agents/mpep.db
```

The crawl takes ~4 minutes and produces ~3,000 sections across all 29
MPEP chapters (~50MB). Re-run periodically to pick up USPTO revisions.

The runtime locates the corpus via:

1. `MPEP_CORPUS_PATH` env var (explicit; used in cloud deploys).
2. `~/.cache/patent_client_agents/mpep.db` (local-dev default).

If neither exists, the first call raises `CorpusUnavailable` with the
build command in the message — no silent fallback to live HTTP.

## Quick Start

```python
from patent_client_agents.mpep import MpepClient

async with MpepClient() as client:
    # Search MPEP
    results = await client.search("obviousness")

    # Get specific section
    section = await client.get_section("2141")

    # List available versions (single-entry; reflects the loaded snapshot)
    versions = await client.list_versions()
```

## Functions

| Function | Description |
|----------|-------------|
| `search()` | Search MPEP content (FTS5 BM25 by default) |
| `get_section()` | Get a specific MPEP section |
| `list_versions()` | Return the loaded snapshot's version label |

## Common Sections

| Section | Topic |
|---------|-------|
| 2100 | Patentability |
| 2106 | Patent Subject Matter Eligibility |
| 2111 | Claim Interpretation |
| 2141 | Obviousness |
| 2163 | Written Description |
| 2164 | Enablement |
| 2173 | Definiteness |

## Usage Pattern

```python
from patent_client_agents.mpep import (
    MpepClient,
    search,
    get_section,
)

# Context manager (recommended)
async with MpepClient() as client:
    results = await client.search("Alice test")

# One-shot convenience functions
results = await search(query="obviousness prima facie")
section = await get_section(section_id="2141.02")
```

## Cloud deploys

For containerized deployments, run the builder during image build and
set `MPEP_CORPUS_PATH` in the runtime env:

```dockerfile
RUN patent-client-agents-build-mpep-corpus --output /app/data/mpep.db
ENV MPEP_CORPUS_PATH=/app/data/mpep.db
```

The published wheel stays small (no corpus bundled); refresh becomes
"rebuild + redeploy".
