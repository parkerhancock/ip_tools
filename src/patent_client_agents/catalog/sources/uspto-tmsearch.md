# USPTO Trademark Search (TESS)

Read-only access to USPTO's Trademark Electronic Search System (TESS). Searches the live trademark register by wordmark, owner, goods/services description, design code, and registration metadata. Wraps the TESS Elasticsearch backend behind `tmsearch.uspto.gov`.

## Source

| | |
|---|---|
| Module | `patent_client_agents.uspto_tmsearch` |
| Client | `TmsearchClient` |
| Base URL | `https://tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch` |
| Auth | AWS WAF `aws-waf-token` cookie (~4 day lifetime) |
| Rate limits | Not published; WAF returns 403/202 on rejection — client retries once with a force-refresh |
| Status | Active. Requires `patent-client-agents[tmsearch]` extra for in-process token minting, or BYO token via env. |

## Authentication

USPTO TESS sits behind AWS WAF. The WAF binds an `aws-waf-token` cookie to the User-Agent + TLS fingerprint that solved the challenge.js puzzle. The token lasts ~4 days.

Two paths to a valid token:

1. **In-process via Playwright** (requires `pip install 'patent-client-agents[tmsearch]'` + `playwright install chromium`). The client mints a token on first use and caches it.
2. **Bring your own** via `PCA_WAF_TOKEN_JSON` (inline JSON payload) or `PCA_WAF_TOKEN_PATH` (path to JSON file). Payload shape: `{"token": "...", "expires": <unix_ts>, "acquired": "ISO-8601"}`. Designed for Secret Manager mounts on Cloud Run.

Legacy env vars `LAW_TOOLS_WAF_TOKEN_JSON` and `WAF_TOKEN_PATH` are honored for one release as a fallback.

Default cache path: `~/.cache/patent_client_agents/waf_token.json`. The legacy `~/.law-tools/waf_token.json` is also read for one release.

`TmsearchClient.__init__` raises `ConfigurationError` if `curl_cffi` is not installed (since the WAF requires Chrome TLS impersonation on all subsequent API calls). The `[tmsearch]` extra installs both `curl_cffi` and `playwright`.

## API Endpoints

| Path | Method | Coverage |
|---|---|---|
| `/prod-stage-v1-0-0/tmsearch` | POST | Elasticsearch-style query: `{"query": ..., "size": ..., "from": ...}` |

## Library API

```python
from patent_client_agents.uspto_tmsearch import TmsearchClient

async with TmsearchClient() as client:
    results = await client.search_wordmark("APPLE", live_only=True)
    detail = await client.get_by_serial("97123456")

    # Multi-criteria
    apple_live = await client.search(
        wordmark="APPLE",
        owner="Apple Inc",
        live_only=True,
        size=100,
    )

    # Auto-paginate
    all_apple = await client.search_all(wordmark="APPLE", max_results=1000)
```

### Methods

| Method | Description |
|---|---|
| `search(...)` | Unified multi-criteria search; `status="live"`/`"dead"`/`"all"` |
| `search_wordmark(wordmark, live_only, size, from_)` | Wordmark search |
| `search_owner(owner_name, live_only, size, from_)` | Owner search |
| `search_goods_services(terms, live_only, size, from_)` | Goods/services description search |
| `get_by_serial(serial_number)` | Single-record lookup |
| `get_by_registration(registration_number)` | Single-record lookup |
| `search_all(wordmark, owner, live_only, batch_size, max_results)` | Auto-paginated wordmark/owner search |

## Token refresh (deploy)

The hosted `mcp.patentclient.com` instance refreshes tokens via a separate Cloud Run Job (`law_tools.uspto_tmsearch.refresh_job`) on a 3-day cron — Playwright on the job side, Secret Manager mount on the service side as `PCA_WAF_TOKEN_JSON`. The connector's in-process retry handles mid-request WAF rejections by force-refreshing the cached token.

## MCP Tools

| Tool | Description |
|---|---|
| `search_trademarks` | Unified search by wordmark/owner/goods+services; supports auto-pagination |
| `get_trademark` | Single-record lookup by serial or registration number |

Both live on PCA's `trademarks_mcp` sub-server alongside TSDR, TMEP, and Trademark Assignments tools.
