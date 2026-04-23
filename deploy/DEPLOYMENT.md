# `ip-tools` Remote MCP Server Deployment

Design-only guide. The artifacts here (`ip-tools-mcp.service`,
`nginx-mcp.conf`, `env.example`) are deployment templates modelled on
the law-tools deployment at `tools/law-tools/deploy/` but stripped of
firm-specific infrastructure (GCP WIF, PACER, RECAP). They stand up a
public MCP server for the ip-tools patent surface.

## Architecture

```
clients ──HTTPS──▶  nginx (443)  ──127.0.0.1:8002──▶  fastmcp (stdio JSON-RPC via streamable-http)
                   TLS termination                      serves /mcp + /downloads/* + /oauth/token
```

- **Transport:** `streamable-http` (fastmcp 3.x) — long-lived
  bidirectional HTTP/1.1 streams. Same shape as Claude Code's remote MCP
  client expects.
- **Auth:** `Bearer` token via `Authorization` header. Token is the
  value of `LAW_TOOLS_CORE_API_KEY`.
- **OAuth2:** the server also exposes `POST /oauth/token` (client
  credentials grant) for OAuth2-only clients. See
  `law_tools_core/mcp/server_factory.py`.
- **Downloads:** search/get tools return HMAC-signed URLs at
  `/downloads/{resource_path}?key=...` with a 24-hour rotating-key
  TTL. The handler streams from an on-disk cache.

## Requirements

- Linux VM with a public IP.
- Domain with DNS A/AAAA record pointing at the VM.
- `nginx`, `certbot`, `python3.12+`, `git`.
- Free USPTO ODP and EPO OPS API keys (see `env.example`).

## Initial Setup

These steps assume a fresh Ubuntu 22.04/24.04 VM. Adapt package
managers as needed for other distros.

### 1. Create the `ip-tools` system user

```bash
sudo useradd --system --shell /usr/sbin/nologin --home /opt/ip-tools ip-tools
```

### 2. Clone and install

```bash
sudo mkdir -p /opt/ip-tools
sudo git clone https://github.com/parkerhancock/ip_tools.git /opt/ip-tools
sudo chown -R ip-tools:ip-tools /opt/ip-tools
cd /opt/ip-tools
sudo -u ip-tools python3 -m venv .venv
sudo -u ip-tools .venv/bin/pip install -e '.[mcp]'
```

### 3. Provision env file

```bash
sudo cp deploy/env.example /opt/ip-tools/.env
sudo chown ip-tools:ip-tools /opt/ip-tools/.env
sudo chmod 600 /opt/ip-tools/.env
sudo -u ip-tools nano /opt/ip-tools/.env
```

Mint the bearer token in-place:

```bash
sudo -u ip-tools bash -c 'echo "LAW_TOOLS_CORE_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")" >> /opt/ip-tools/.env'
```

### 4. Optional: provision log + cache directories

```bash
sudo mkdir -p /var/log/ip-tools /var/cache/ip-tools/downloads
sudo chown -R ip-tools:ip-tools /var/log/ip-tools /var/cache/ip-tools
```

Add the corresponding `LAW_TOOLS_CORE_LOG_DIR` and
`LAW_TOOLS_CORE_DOWNLOAD_CACHE` entries to `.env` if you provisioned
them.

### 5. Install the systemd unit

```bash
sudo cp deploy/ip-tools-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ip-tools-mcp
sudo systemctl start ip-tools-mcp
sudo systemctl status ip-tools-mcp
```

### 6. Install the nginx config + obtain a TLS cert

Replace `mcp.example.com` in `deploy/nginx-mcp.conf` with your
hostname, then:

```bash
sudo cp deploy/nginx-mcp.conf /etc/nginx/sites-available/mcp.example.com
sudo ln -s /etc/nginx/sites-available/mcp.example.com /etc/nginx/sites-enabled/
sudo certbot --nginx -d mcp.example.com
sudo nginx -t && sudo systemctl reload nginx
```

Certbot auto-installs the TLS cert lines into the nginx config and
sets up a renewal cron. Verify renewal works:

```bash
sudo certbot renew --dry-run
```

### 7. Smoke-test the endpoint

From any machine:

```bash
curl -s -X POST https://mcp.example.com/ip_tools/mcp \
  -H "Authorization: Bearer <LAW_TOOLS_CORE_API_KEY value>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a JSON response carrying `"serverInfo":{"name":"ip-tools"...}`.

## Client Configuration

### Claude Code / Desktop (`.mcp.json` or `~/.claude.json`)

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

### OAuth2-only clients

```
POST https://mcp.example.com/ip_tools/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_secret=<LAW_TOOLS_CORE_API_KEY value>
```

Response: `{"access_token": "<token>", "token_type": "bearer"}`.

## Service Management

```bash
sudo systemctl status ip-tools-mcp
sudo systemctl restart ip-tools-mcp
sudo journalctl -u ip-tools-mcp -f           # tail
sudo journalctl -u ip-tools-mcp --since today
```

## Updating env vars

```bash
sudo -u ip-tools nano /opt/ip-tools/.env
sudo systemctl restart ip-tools-mcp
```

## Deploying new code

Pull and restart. The unit runs `pip install -e .`, so pulling
refreshes the running code the next time the service is restarted:

```bash
sudo -u ip-tools bash -c 'cd /opt/ip-tools && git pull origin main'
sudo systemctl restart ip-tools-mcp
```

If dependencies changed:

```bash
sudo -u ip-tools /opt/ip-tools/.venv/bin/pip install -e '.[mcp]'
sudo systemctl restart ip-tools-mcp
```

## Co-tenanting with `law-tools`

The nginx template ships with a single `location /ip_tools/` block. If
you also run `law-tools` on the same host, add its block alongside:

```nginx
location /ip_tools/ { ... proxy_pass http://127.0.0.1:8002; ... }
location /law_tools/ { ... proxy_pass http://127.0.0.1:8001; ... }
```

Different ports, different systemd units, shared TLS cert and bearer
token (or mint separate tokens per service). The two MCP surfaces have
no import-time coupling — the law-tools unit mounts `ip_mcp` via the
`ip-tools` package dependency but runs a separate process.

## Troubleshooting

**`502 Bad Gateway` from nginx.** The fastmcp backend isn't running.
`systemctl status ip-tools-mcp` and `journalctl -u ip-tools-mcp -n 100`.

**`401 Unauthorized` on initialize.** Bearer token mismatch. Verify the
token in `/opt/ip-tools/.env` matches the client's `Authorization`
header.

**`ModuleNotFoundError: No module named 'fastmcp'`.** The venv was
installed without the `[mcp]` extra. Rerun `pip install -e '.[mcp]'`.

**Download URLs 403.** HMAC mismatch, usually because
`LAW_TOOLS_CORE_API_KEY` was rotated mid-session. The agent should
re-call the source tool to mint a fresh URL.

**Download URLs 410 Gone.** Intentional — this signals a cache miss on
a budget-tracked source (PACER/RECAP), which only applies when
co-tenanting with law-tools. Not reachable via ip-tools alone.

## Scaling notes

- Each MCP session holds an open HTTP stream. The default VM sizing
  (e2-small, 2 GB RAM) handles ~50 concurrent sessions.
- USPTO ODP caps at 60 req/min. Under load consider a backend cache
  tier — the existing hishel SQLite cache (`~/.cache/ip_tools/`)
  already handles this for single-process deployments.
- If you need more throughput, scale horizontally behind an nginx
  upstream block — fastmcp sessions are stateless (`--stateless` flag
  already set in the unit file).

## What's *not* here

This template is intentionally minimal. Deployment patterns we use at
Baker Botts but did not port to this public guide:

- GitHub Actions auto-deploy via GCP Workload Identity Federation.
- WAF token refresh (private WAF provider, specific to our edge).
- PACER spending budget ledger + RECAP inline upload (law-tools only).

If you want CI auto-deploy or any of the above, start from
`tools/law-tools/deploy/DEPLOYMENT.md` — the recipes there are
adaptable.
