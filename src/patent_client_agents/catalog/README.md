# patent-client-agents Catalog

Two layers of documentation, matching the two layers of the library:

- **[sources/](sources/)** — per-source Python client reference. One file per
  upstream service (USPTO ODP, Google Patents, EPO OPS, …). Documents the
  raw clients, methods, response models, and rate limits. Read this when
  you want the granular capabilities of a single backend.
- **[intents/](intents/)** — MCP tool reference, grouped by what you want to
  do rather than by backend. Documents the ~40 tools exposed over MCP,
  including the cross-source fused tools (`get_patent_claims`,
  `download_patent_pdf`) that cascade across multiple backends. Read this
  when you're wiring an agent or choosing which tool to call.

Cross-source fusion lives in `patent_client_agents.unified`. The MCP tools
are thin wrappers over that module, so Python consumers can import the same
fused helpers directly:

```python
from patent_client_agents import get_patent_claims, download_patent_pdf  # fused
from patent_client_agents.google_patents import GooglePatentsClient       # raw
```

See `intents/claims.md` and `intents/downloads.md` for the shape of each
fused API.
