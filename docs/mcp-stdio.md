# Running `patent-client-agents` as a stdio MCP server

The `[mcp]` extra ships a ready-to-run stdio MCP server that exposes
all patent and IP tools to any MCP-speaking client — Claude Code,
Claude Desktop, Cursor, Cline, CoWork, or a homegrown fastmcp Client.

## Install

```bash
pip install 'patent-client-agents[mcp]'
```

This installs the runtime (`fastmcp`, `starlette`) and adds the
`patent-client-agents-mcp` console script.

## Run

```bash
patent-client-agents-mcp                  # default: stdio transport, no auth
```

`patent-client-agents-mcp` is a thin wrapper around `patent_client_agents.mcp.server:mcp` that
runs via fastmcp. You can also invoke it directly:

```bash
python -m patent_client_agents.mcp.server
fastmcp run patent_client_agents.mcp.server:mcp
```

## Claude Code configuration

Add one of the following blocks to your MCP config (`.mcp.json` at the
project root or `~/.claude.json` for user-scope):

```json
{
  "mcpServers": {
    "patent-client-agents": {
      "command": "patent-client-agents-mcp"
    }
  }
}
```

If you prefer to invoke a specific venv or Python interpreter:

```json
{
  "mcpServers": {
    "patent-client-agents": {
      "command": "/path/to/.venv/bin/patent-client-agents-mcp",
      "env": {
        "USPTO_ODP_API_KEY": "…",
        "EPO_OPS_API_KEY": "…",
        "EPO_OPS_API_SECRET": "…"
      }
    }
  }
}
```

The server starts with no authentication in stdio mode. Any env vars
set in the `env` block are available to the connectors — USPTO ODP,
EPO OPS, and JPO all consume credentials from env (see each connector's
`CATALOG.md` entry).

## Tools exposed

The server mounts `ip_mcp`, which composes 15 sub-servers (always-on
plus env-gated):

| Sub-server | Tools | Download path (HTTPS + `pca://`) |
|---|---:|---|
| `Patents` (Google Patents) | 7 | `patents/{publication_number}` |
| `USPTO` (ODP — applications, PTAB, petitions, bulk) | 18 | `uspto/applications/{app}/documents/{doc}`, `ptab/documents/{document_identifier}` |
| `Publications` (PPUBS) | 3 | `publications/{publication_number}` |
| `International` (EPO OPS, CPC; + 12 JPO when `JPO_API_USERNAME` and `JPO_API_PASSWORD` are set) | 10 / 22 | `epo/patents/{publication_number}`, `jpo/documents/{ip_type}/{app}/{doc_kind}` |
| `OfficeActions` (USPTO OA rejections/citations/text) | 1 | — |
| `PatentAssignments` (USPTO Assignment Center) | 1 | — |
| `Trademarks` (TESS search — needs `[tmsearch]` extra or `PCA_WAF_TOKEN_*`; TSDR — needs `USPTO_TSDR_API_KEY`; TMEP; Trademark Assignments) | 9 | — |
| `MPEP` | 2 | — |
| `CAFC` (Federal Circuit opinions + patent classifier) | 3 | `cafc/opinions/{appeal_number}` |
| `Copyright` (US Copyright Office — registrations + recorded documents) | 2 | — |
| `USITC` (EDIS Section 337 — needs `USITC_EDIS_TOKEN` for downloads; DataWeb — needs `USITC_DATAWEB_TOKEN`; HTS; IDS) | 8 | `usitc/documents/{doc_id}/attachments/{att_id}` |
| `UPC` (Unified Patent Court decisions feed + UPCA/RoP/Fees corpus) | 7 | — |
| `CanLII` (env-gated on `CANLII_API_KEY`) | 0 / 9 | — |
| `WIPO Lex` | 2 | — |
| `EUIPO` (env-gated on `EUIPO_CLIENT_ID` + `EUIPO_CLIENT_SECRET`) | 0 / 4 | — |
| **Total** | **73 default; +12 JPO / +9 CanLII / +4 EUIPO with credentials** | |

## Downloads — two transports

Tools that return bytes (PDFs, file-history docs, JPO bundles, etc.)
ride **two transports out of one fetch**:

1. An HMAC-signed `download_url` (HTTPS) when
   `LAW_TOOLS_CORE_PUBLIC_URL` is set on a remote HTTP deployment.
2. A `pca://...` MCP resource URI served via `resources/read` over
   the existing MCP session.

Tool responses include both: structured content carries
`download_url`, `resource_uri`, `filename`, `content_type`,
`size_bytes` (and `expires_at` on rotating URLs); content blocks
carry a `ResourceLink` pointing at the same `pca://` URI.

**Why two paths.** Hosted sandboxes like Claude CoWork allowlist
the MCP server but block outbound HTTP to arbitrary hosts — a
curl against `mcp.patentclient.com/downloads/...` fails even
though the tool call that minted the URL succeeded. The
`resources/read` path rides the session the client is already
holding, so the bytes flow without ever touching the network gate.
URL-comfortable clients (Claude Desktop, Cursor, homegrown
clients) keep fetching `download_url` directly and ignore the
resource link.

The resource templates are advertised via
`resources/templates/list`:

```
pca://patents/{publication_number}
pca://publications/{publication_number}
pca://epo/patents/{publication_number}
pca://uspto/applications/{application_number}/documents/{document_identifier}
pca://ptab/documents/{document_identifier}
pca://cafc/opinions/{appeal_number}
pca://usitc/documents/{document_id}/attachments/{attachment_id}
pca://jpo/documents/{ip_type}/{application_number}/{doc_kind}     # env-gated
```

The path after `pca://` matches the HTTPS download path
one-for-one — `pca://patents/US12345678B2` and
`/downloads/patents/US12345678B2` resolve the same cached bytes.

**Bulk downloads.** Bulk tools (e.g. `download_file_history`,
`download_ptab_trial_documents`) return one `ResourceLink` per
successfully fetched item alongside a zip URL. The structured
manifest carries per-item `resource_uri` + `download_url`, so
resource-aware clients can pull per-doc through MCP and avoid
JSON-RPC message caps that bite on large archives. Bulk zip
resources themselves are HTTP-only — use the per-doc URIs over
MCP, or the zip `download_url` over HTTPS.

In stdio mode without `LAW_TOOLS_CORE_PUBLIC_URL`, tools write
bytes to a tempfile and return `file_path` instead. The
`resource_uri` field is still set so MCP clients that resolve it
locally see the same path.

## Verifying

A one-off smoke test against the running server:

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def main():
    async with Client(StdioTransport(command="patent-client-agents-mcp", args=[])) as c:
        tools = await c.list_tools()
        print(len(tools), "tools")
        result = await c.call_tool("get_mpep_section", {"section": "2106"})
        print(result.data.get("title") if result.data else None)

asyncio.run(main())
```

Expect 73 tools by default. Counts scale with env-gated connectors:
+12 JPO when `JPO_API_USERNAME` + `JPO_API_PASSWORD` are set, +9 CanLII
when `CANLII_API_KEY` is set, +4 EUIPO when `EUIPO_CLIENT_ID` +
`EUIPO_CLIENT_SECRET` are set. Title should be
`2106 … Patent Subject Matter Eligibility`.

## Not installed?

If `patent-client-agents-mcp` is on PATH but startup fails with
`ModuleNotFoundError: No module named 'fastmcp'`, you installed
`patent-client-agents` without the `[mcp]` extra. Re-install with
`pip install 'patent-client-agents[mcp]'`.
