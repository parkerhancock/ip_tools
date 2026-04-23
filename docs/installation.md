# Installing `ip-tools`

`ip-tools` ships in one wheel that covers six install modes. Pick the
one that matches how you're going to use it:

| Mode | You want to... | Section |
|---|---|---|
| Python library | Import `ip_tools` in your own async code | [§1](#1-python-library) |
| Python library + MCP runtime | Run an MCP server locally or in-process | [§2](#2-python-library-with-mcp-runtime) |
| Claude Code plugin (from GitHub) | One-command install into Claude Code | [§3](#3-claude-code-plugin-from-github) |
| Claude Code skill (dev symlink) | Edit the skill content and hot-reload | [§4](#4-claude-code-skill-dev-symlink) |
| Stdio MCP (any MCP client) | Connect Claude Desktop / Cursor / Cline / CoWork-local / custom client | [§5](#5-stdio-mcp-from-any-mcp-client) |
| Remote MCP — Cowork | Add `ip-tools` to a shared Cowork workspace | [§6](#6-remote-mcp--cowork) |
| Remote MCP — Claude Code / Desktop / others | HTTP MCP with Bearer token | [§7](#7-remote-mcp--generic-claude-code-desktop-etc) |

Skip to the section you need — they're independent.

---

## 1. Python library

Use this when you're writing async Python that calls patent APIs
directly — no MCP, no Claude Code. The bare install pulls no
MCP-runtime dependencies (`fastmcp`, `starlette`), so it stays lean.

### Install

```bash
pip install ip-tools
```

Or with `uv`:

```bash
uv add ip-tools
```

### API keys

Set via environment variables. Most connectors work without keys but
these unlock the full surface:

| Variable | Source | How to get |
|---|---|---|
| `USPTO_ODP_API_KEY` | USPTO Open Data Portal | [developer.uspto.gov](https://developer.uspto.gov/) (free) |
| `EPO_OPS_API_KEY`, `EPO_OPS_API_SECRET` | EPO Open Patent Services | [developers.epo.org](https://developers.epo.org/) (free, 4 GB/week) |
| `JPO_API_USERNAME`, `JPO_API_PASSWORD` | JPO J-PlatPat | Contact JPO (restricted) |

Google Patents, USPTO Publications, USPTO Assignments, and MPEP need
no credentials.

### Verify

```python
import asyncio
from ip_tools.google_patents import GooglePatentsClient

async def main():
    async with GooglePatentsClient() as client:
        patent = await client.get_patent_data("US10123456B2")
        print(patent.title)

asyncio.run(main())
```

Expected output: `Phase change material heat sink using additive manufacturing and method`.

---

## 2. Python library with MCP runtime

Use this when you want to run the stdio MCP server from the same venv
as other Python work — e.g. embedding `ip_mcp` in your own composed
FastMCP server, or running `ip-tools-mcp` as a subprocess from a
Python script.

### Install

```bash
pip install 'ip-tools[mcp]'
```

The `[mcp]` extra pulls `fastmcp>=3.2.3` and `starlette>=0.37` on top
of the base dependencies.

### What you get

Two new console scripts on your PATH:

- `ip-tools-mcp` — launches the stdio MCP server (63 patent tools)
- `ip-tools-skill-install` — symlinks the `ip_research` skill into `~/.claude/skills/` (see §4)

Plus the Python-importable MCP surface:

```python
from ip_tools.mcp import ip_mcp                 # pre-composed FastMCP
from ip_tools.mcp.server import mcp as ip_server  # + middleware + routes
```

Mount `ip_mcp` inside your own FastMCP server:

```python
from fastmcp import FastMCP
from ip_tools.mcp import ip_mcp

my_server = FastMCP("my-server")
my_server.mount(ip_mcp)  # + your own tools alongside
```

This is exactly how `law-tools` consumes `ip-tools` in the monorepo.

---

## 3. Claude Code plugin (from GitHub)

Use this when you use Claude Code and want the skill **and** the 63
MCP tools dropped in with one command.

### Prereq

`uv` needs to be on `PATH`. The plugin's MCP server spawns via `uvx`,
which handles the Python runtime (`fastmcp` and friends) in a managed
environment so you don't have to `pip install` anything.

```bash
# install uv if you don't have it — one-liner from astral.sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install

```bash
claude plugin add github:parkerhancock/ip_tools
```

What happens:

1. Claude Code clones the repo into `~/.claude/plugins/ip-tools/`.
2. It auto-discovers the `ip_research` skill at
   `src/ip_tools/skills/` — available to the agent immediately.
3. It registers the MCP server declared in `.claude-plugin/plugin.json`.
   On first use, `uvx` installs `ip-tools[mcp]` from the plugin clone
   into a managed environment and launches `ip-tools-mcp`. The cold
   start takes ~30 seconds; after that it's fast because uv caches
   the resolved environment.

### Update

```bash
claude plugin update ip-tools
```

Re-clones and reinstalls. The uv-managed env gets rebuilt on next
MCP launch.

### Remove

```bash
claude plugin remove ip-tools
```

### Configure API keys

API keys are read from environment. For a global Claude Code install,
export them in your shell profile:

```bash
export USPTO_ODP_API_KEY="…"
export EPO_OPS_API_KEY="…"
export EPO_OPS_API_SECRET="…"
```

Restart Claude Code so the new env reaches the MCP subprocess. Without
keys, Google Patents / PPUBS / MPEP / Assignments still work; USPTO
ODP and EPO tools will return auth errors.

### Verify

Start Claude Code, open a chat, and ask something patent-research-ish:

> "What's in MPEP section 2106?"

The `ip_research` skill surfaces in routing and Claude calls
`get_mpep_section` via the MCP server. The response is the text of
MPEP 2106 — Patent Subject Matter Eligibility.

Or, more directly — list MCP tools from within a Claude Code session:

```
/mcp
```

`ip-tools` should show up with 63 tools.

### Troubleshooting

**`uvx: command not found`** — install uv (see prereq).

**MCP server shows "failed to start" in `/mcp`** — open the logs
pane and look for the stderr output. Common causes: offline during
first install (`uvx` can't fetch packages), or a Python build error
on ancient macOS (upgrade `uv` to the latest).

**Cold start takes too long** — subsequent runs are ~1s. If every
session is 30s, something is evicting uv's cache. Check
`~/.cache/uv/` is persistent.

---

## 4. Claude Code skill (dev symlink)

Use this when you're **editing** the skill content and want
`~/.claude/skills/ip-research` to track your working tree. Native
installer copies the repo — this symlinks it, so edits are live.

### Install

```bash
pip install 'ip-tools[mcp]'
ip-tools-skill-install
```

Creates `~/.claude/skills/ip-research` as a symlink into the
pip-installed package. Idempotent — re-runs no-op when already linked.

### Point at a different target

```bash
ip-tools-skill-install --target=/path/to/other/skills/dir
```

### Replace an existing directory

```bash
ip-tools-skill-install --force
```

Backs up any existing `ip-research` dir to `ip-research.bak` and
replaces with the symlink.

### Native installer vs dev symlink

| | Native installer (§3) | Dev symlink (§4) |
|---|---|---|
| Command | `claude plugin add ...` | `ip-tools-skill-install` |
| Source | Cloned copy of the repo | Pip-installed package (symlinked) |
| Updates | `claude plugin update` (re-clones) | Picks up edits live — reinstall `ip-tools` to refresh |
| Best for | Users | Contributors editing SKILL.md or references |

---

## 5. Stdio MCP from any MCP client

Use this when you want every patent tool available as MCP tools to
your client (Claude Desktop, Cursor, Cline, CoWork-local, or a custom
fastmcp client). The server is a short-lived subprocess speaking
JSON-RPC over stdio.

### Install

```bash
pip install 'ip-tools[mcp]'
```

This gives you the `ip-tools-mcp` console script on PATH.

### Wire the MCP client

#### Claude Code

Add to `.mcp.json` at your project root (or `~/.claude.json` for
user-scope):

```json
{
  "mcpServers": {
    "ip-tools": {
      "command": "ip-tools-mcp"
    }
  }
}
```

Or add from the CLI:

```bash
claude mcp add ip-tools ip-tools-mcp
```

If you're using a venv, point at the absolute path so Claude Code
launches the right interpreter:

```json
{
  "mcpServers": {
    "ip-tools": {
      "command": "/path/to/.venv/bin/ip-tools-mcp",
      "env": {
        "USPTO_ODP_API_KEY": "…",
        "EPO_OPS_API_KEY": "…",
        "EPO_OPS_API_SECRET": "…"
      }
    }
  }
}
```

#### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "ip-tools": {
      "command": "ip-tools-mcp",
      "env": {
        "USPTO_ODP_API_KEY": "…"
      }
    }
  }
}
```

#### Cursor, Cline, and other stdio MCP clients

Same pattern — `command: "ip-tools-mcp"` plus any env vars. Consult
the client's own MCP config docs for the file location.

### Verify

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def main():
    async with Client(StdioTransport(command="ip-tools-mcp", args=[])) as c:
        tools = await c.list_tools()
        print(f"{len(tools)} tools")
        result = await c.call_tool("get_mpep_section", {"section": "2106"})
        print(result.data.get("title"))

asyncio.run(main())
```

Expect **63 tools** and title starting `2106 ... Patent Subject Matter
Eligibility`.

### Troubleshooting

**`ip-tools-mcp: command not found`** — `[mcp]` extra wasn't
installed. Rerun `pip install 'ip-tools[mcp]'`.

**`ModuleNotFoundError: No module named 'fastmcp'` at startup** — same
root cause. Something is launching a Python that doesn't have fastmcp.

**Zero tools listed** — the MCP client is likely talking to the wrong
server. Check the JSON config points at the right binary.

---

## 6. Remote MCP — Cowork

Use this when your team uses Cowork and wants `ip-tools` available as
a shared connector for the whole workspace. Requires a deployed
`ip-tools` remote MCP endpoint (see §7 for what's running on the
server side, and `deploy/DEPLOYMENT.md` for standing one up).

### Prereqs

- A deployed `ip-tools` MCP server — e.g. `https://mcp.example.com/ip_tools/`
- The `LAW_TOOLS_CORE_API_KEY` secret value set on that server
- Cowork admin access to the target workspace

### Add the connector

1. In Cowork, open **Settings → Connectors**.
2. Click **Add custom MCP**.
3. Fill in:
   - **Server URL**: `https://mcp.example.com/ip_tools/mcp`
   - **Auth type**: **OAuth2 client credentials**
   - **Client ID**: any string (`ip-tools` is a fine default — the
     server doesn't check client_id, only client_secret)
   - **Client secret**: the `LAW_TOOLS_CORE_API_KEY` value from the
     server's `.env`
   - **Token URL**: `https://mcp.example.com/ip_tools/oauth/token`
4. Save.

Cowork will immediately POST to the token URL with
`grant_type=client_credentials&client_secret=<secret>` and exchange
it for an access token. The server returns the same token back as the
`access_token` (the OAuth endpoint is a passthrough — the token
*is* the API key). Cowork caches the token and uses it as
`Authorization: Bearer <token>` on every MCP request.

### Verify

After saving, Cowork should list the connector as **Connected**. Open
any Cowork chat and ask a patent question — the `ip-tools` connector
should appear in the tool-use indicators.

### Troubleshooting

**Connection test fails with `401 invalid_client`** — the client
secret doesn't match `LAW_TOOLS_CORE_API_KEY` on the server. Re-copy
from the server `.env`, being careful not to include trailing
whitespace.

**Connection test fails with `500 server_error` on token exchange** —
`LAW_TOOLS_CORE_API_KEY` is not set on the server at all. Check the
systemd unit's `EnvironmentFile` and `sudo systemctl restart ip-tools-mcp`.

**Tools list empty after connecting** — the bearer token wasn't
forwarded. Double-check Cowork is sending it as `Authorization: Bearer
<token>`, not e.g. `Token <token>`.

---

## 7. Remote MCP — generic (Claude Code, Desktop, etc.)

Use this when you're pointing Claude Code, Claude Desktop, or any
HTTP-speaking MCP client at a deployed `ip-tools` remote MCP. No
OAuth2 round-trip — you paste the bearer token directly.

### Prereqs

Same as §6: a deployed endpoint + the `LAW_TOOLS_CORE_API_KEY` value.
For setup, see `deploy/DEPLOYMENT.md`.

### Claude Code config

`.mcp.json` in the project root, or `~/.claude.json` for user-scope:

```json
{
  "mcpServers": {
    "ip-tools": {
      "url": "https://mcp.example.com/ip_tools/mcp",
      "headers": {
        "Authorization": "Bearer <LAW_TOOLS_CORE_API_KEY value>"
      }
    }
  }
}
```

### Claude Desktop config

Same shape — `claude_desktop_config.json` accepts `url` + `headers`
for remote MCPs.

### Raw smoke-test

```bash
curl -s -X POST https://mcp.example.com/ip_tools/mcp \
  -H "Authorization: Bearer <LAW_TOOLS_CORE_API_KEY value>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a JSON response with `"serverInfo": {"name": "ip-tools", ...}`.

### Downloads

Patent PDFs (Google Patents, PPUBS, EPO, PTAB, etc.) return signed
`download_url` fields pointing at
`https://mcp.example.com/ip_tools/downloads/{path}?key=...`. URLs
rotate every 24 hours by HMAC — the tool response includes an
`expires_at` field so the client knows when to re-call.

---

## Deciding which path

```
  Are you writing Python that uses the library directly?
  ├── yes → §1 (bare) or §2 (with MCP runtime)
  └── no ↓

  Are you a Claude Code user?
  ├── yes → §3 (plugin install from GitHub)
  │         plus §5 if you want the MCP tools too
  └── no ↓

  Is your team using Cowork?
  ├── yes → §6 (Cowork remote MCP)
  └── no ↓

  Are you on Claude Desktop / Cursor / Cline / other stdio client?
  ├── local subprocess → §5 (stdio MCP)
  └── pointing at a deployed server → §7 (remote MCP)
```

## Getting help

- Issues: [github.com/parkerhancock/ip_tools/issues](https://github.com/parkerhancock/ip_tools/issues)
- Full source: [github.com/parkerhancock/ip_tools](https://github.com/parkerhancock/ip_tools)
- Deploy guide for remote MCP: `deploy/DEPLOYMENT.md`
- Per-connector API notes: `src/ip_tools/catalog/*.md`
