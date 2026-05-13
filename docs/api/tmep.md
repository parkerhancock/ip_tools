# TMEP

Access the Trademark Manual of Examining Procedure (TMEP) for searching
and retrieving trademark examination guidance.

## First-time setup

`TmepClient` reads from a local SQLite/FTS5 corpus, **not** live USPTO.
The wheel ships the builder; build the snapshot once before the first
call:

```bash
patent-client-agents-build-tmep-corpus \
    --output ~/.cache/patent_client_agents/tmep.db
```

The crawl takes ~2 minutes and produces ~1,750 sections across all 19
TMEP chapters (~16MB). Re-run periodically to pick up USPTO revisions.

The runtime locates the corpus via:

1. `TMEP_CORPUS_PATH` env var (explicit; used in cloud deploys).
2. `~/.cache/patent_client_agents/tmep.db` (local-dev default).

If neither exists, the first call raises `CorpusUnavailable` with the
build command in the message — no silent fallback to live HTTP.

## Quick Start

```python
from patent_client_agents.tmep import TmepClient

async with TmepClient() as client:
    # Search the TMEP
    results = await client.search("likelihood of confusion")

    # Get a specific section
    section = await client.get_section("1207.01(a)")

    # List available versions (single-entry; reflects the loaded snapshot)
    versions = await client.list_versions()
```

## Functions

| Function | Description |
|---|---|
| `search()` | Full-text search across the TMEP (FTS5 BM25 by default) |
| `get_section()` | Get a specific TMEP section by number or href |
| `list_versions()` | Return the loaded snapshot's version label |

## Common Sections

| Section | Topic |
|---|---|
| 1202 | Use of subject matter as a trademark |
| 1207 | Refusal on the basis of likelihood of confusion (§ 2(d)) |
| 1209 | Refusal on basis of descriptiveness |
| 1212 | Acquired distinctiveness (§ 2(f)) |
| 1213 | Disclaimers |
| 1402 | Identification and classification of goods/services |
| 1715 | Letter of protest |
| 904 | Specimens |

## Usage Pattern

```python
from patent_client_agents.tmep import (
    TmepClient,
    SearchInput,
    search,
    get_section,
)

# Context manager (recommended)
async with TmepClient() as client:
    results = await client.search("disclaimer")

# One-shot convenience functions
results = await search(SearchInput(query="2(d) refusal"))
section = await get_section("1207.01(a)")
```

## Cloud deploys

For containerized deployments, run the builder during image build and
set `TMEP_CORPUS_PATH` in the runtime env:

```dockerfile
RUN patent-client-agents-build-tmep-corpus --output /app/data/tmep.db
ENV TMEP_CORPUS_PATH=/app/data/tmep.db
```

The published wheel stays small (no corpus bundled); refresh becomes
"rebuild + redeploy".
