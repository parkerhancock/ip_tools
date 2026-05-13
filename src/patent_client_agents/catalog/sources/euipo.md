# EUIPO

Read-only access to the European Union Intellectual Property Office's Trademark Search and Design Search APIs. Covers all ~2.3M EU trademarks (EUTMs + international registrations designating the EU, 1996 onward) and all ~1.5M Registered Community Designs (RCDs, since April 2003). One OAuth2 app is shared across both products; querying uses RSQL (URI-friendly FIQL variant). Sandbox and production environments are toggled via `EUIPO_ENV`; sandbox auto-approves on subscription but carries a frozen historical snapshot + synthetic test rows — fine for shape testing, useless for "is this mark live today" work. Production access requires emailing identity documents to EUIPO.

## Source

| | |
|---|---|
| Module | `patent_client_agents.euipo_trademarks` + `patent_client_agents.euipo_designs` |
| Client | `EuipoTrademarksClient`, `EuipoDesignsClient` |
| Base URL | `https://api.euipo.europa.eu/{trademark,design}-search` (prod) / `https://api-sandbox.euipo.europa.eu/...` (sandbox) |
| Auth | OAuth2 client_credentials — `EUIPO_CLIENT_ID` + `EUIPO_CLIENT_SECRET` |
| Rate limits | 25,000 calls/day per app on the Default Plan (visible at subscription time) |
| Status | Active |

## Authentication

Two-step setup:

1. **Register an App.** Sign up at <https://dev.euipo.europa.eu> (production) and/or <https://dev-sandbox.euipo.europa.eu> (sandbox — separate auth realm). Each portal lets you create an "App" that gives you a `client_id` (shown as "API Key" in the UI, sent in `X-IBM-Client-Id`) and a `client_secret`.
2. **Subscribe.** From the App's Subscriptions tab, subscribe to the "Trademark Search" and/or "Design Search" products on the Default Plan. Sandbox subscriptions activate immediately; **production subscriptions require sending identity documents to `docs.apiplatform@euipo.europa.eu`** (passport copy for natural persons, plus company register excerpt for legal persons).

Set `EUIPO_CLIENT_ID` and `EUIPO_CLIENT_SECRET` in the environment, or pass them to the client constructor. Both clients also accept a pre-built `auth=` handler so callers can plug in the 3-legged `authorizationCode` flow if they ever need the user-delegated scopes (the library defaults to `clientCredentials` with scope `uid`, which empirically returns the full register — not the misleading "partial read access under certain conditions" suggested by the spec).

Every request carries both `Authorization: Bearer <token>` and `X-IBM-Client-Id: <client_id>`; the library handles both automatically.

## Rate Limits

The Default Plan grants 25,000 calls per day across all subscribed products on a given App. Over-quota requests return HTTP 429. There is no documented burst limit, but the `BaseAsyncClient` retry layer handles transient 429s with exponential backoff. Higher-quota plans exist but are not self-service — contact `apiplatform@euipo.europa.eu`.

Access tokens are valid for 7,200 seconds (2 hours) and are cached in-memory by `OAuth2ClientCredentialsAuth`. The library refreshes automatically on 401 from the resource endpoint, so callers never see token expiry directly.

## API Endpoints

### Trademark Search (v1.0.0 prod / v1.1.0 sandbox — identical operation signatures)

| Path | Method | Coverage |
|---|---|---|
| `/trademarks` | GET | RSQL search across all EUTMs |
| `/trademarks/{applicationNumber}` | GET | Full record (~40 fields) |
| `/trademarks/{applicationNumber}/image` | GET | Mark image (figurative / 3D / colour / position / pattern) |
| `/trademarks/{applicationNumber}/image/thumbnail` | GET | Thumbnail |
| `/trademarks/{applicationNumber}/sound` | GET | Sound mark audio |
| `/trademarks/{applicationNumber}/video` | GET | Multimedia / motion mark video |
| `/trademarks/{applicationNumber}/model` | GET | 3D shape mark model |

### Design Search (v1.0.0)

| Path | Method | Coverage |
|---|---|---|
| `/designs` | GET | RSQL search across all RCDs |
| `/designs/{designNumber}` | GET | Full record |
| `/designs/{designNumber}/views/{order}` | GET | Image of a single view (1-indexed angle) |
| `/designs/{designNumber}/views/{order}/thumbnail` | GET | Thumbnail of a view |
| `/designs/{designNumber}/model` | GET | 3D model bytes |

## Query Language (RSQL)

The `query` parameter accepts RSQL expressions:

```
applicationDate>=2024-01-01 and ((markFeature==FIGURATIVE and niceClasses=all=(25,26))
                                  or (markFeature==WORD and niceClasses=out=(40)))
```

Operators: `==` exact, `!=` not-equal, `=in=` set membership, `=out=` set non-membership, `=all=` all-of, `=any=` any-of, `<` `>` `<=` `>=` for ordered fields. Strings support `*` wildcards. Field paths are dotted (`wordMarkSpecification.verbalElement`, `applicants.name`). Page size is 10..100 (the spec's `size=3` examples are wrong — EUIPO rejects `size<10`).

## Library API

```python
from patent_client_agents.euipo_trademarks import (
    EuipoTrademarksClient,
    SearchTrademarksInput,
    search_trademarks,
    get_trademark,
    GetTrademarkInput,
)

# One-shot
page = await search_trademarks(SearchTrademarksInput(
    query="wordMarkSpecification.verbalElement==*Apple* and status==REGISTERED",
    size=25,
    sort="applicationDate:desc",
))
print(f"{page.total_elements} matches across {page.total_pages} pages")

# Batch — one client, one token, one cache
async with EuipoTrademarksClient(environment="sandbox") as cl:
    for tm in page.trademarks:
        full = await cl.get_trademark(tm.application_number)
        for gns in full.goods_and_services:
            print(gns.class_number, gns.terms_in("en"))
```

```python
from patent_client_agents.euipo_designs import (
    EuipoDesignsClient,
    SearchDesignsInput,
    search_designs,
)

# RCDs filed in Locarno classes 14 (recording equipment) since 2024-01-01
page = await search_designs(SearchDesignsInput(
    query="applicationDate>=2024-01-01 and locarnoClasses=in=(14.01,14.02,14.03)",
    sort="applicationDate:desc",
))
```

### Methods

#### `EuipoTrademarksClient`

| Method | Description |
|---|---|
| `search(query, page, size, sort, fields)` | RSQL search — returns `TrademarkSearchResult` |
| `get_trademark(application_number)` | Full record — returns `Trademark` |
| `get_image(application_number)` | Mark image bytes |
| `get_image_thumbnail(application_number)` | Thumbnail bytes |
| `get_sound(application_number)` | Sound mark audio bytes |
| `get_video(application_number)` | Multimedia/motion mark video bytes |
| `get_model(application_number)` | 3D shape model bytes |

#### `EuipoDesignsClient`

| Method | Description |
|---|---|
| `search(query, page, size, sort, fields)` | RSQL search — returns `DesignSearchResult` |
| `get_design(design_number)` | Full record — returns `Design` |
| `get_view(design_number, order)` | View image bytes |
| `get_view_thumbnail(design_number, order)` | View thumbnail bytes |
| `get_model(design_number)` | 3D model bytes |

## MCP Tools

| Tool | Description |
|---|---|
| `search_euipo_trademarks` | RSQL search across the EUTM register |
| `get_euipo_trademark` | Full record by application number |
| `search_euipo_designs` | RSQL search across the RCD register |
| `get_euipo_design` | Full record by design number |

All tools env-gate on `EUIPO_CLIENT_ID` + `EUIPO_CLIENT_SECRET` — they are absent from `tool/list` on deployments that don't carry both. Media endpoints (image/sound/video/3D model) are exposed only via the library API in v1.

## Related Docs

- Survey: [research/connectors/euipo.md](../../../../research/connectors/euipo.md) — full scope including bulk data, GIs, EU statutory law via CELLAR
- Live findings: [research/euipo_api_authoritative.md](../../../../research/euipo_api_authoritative.md) — auth URLs, scope behavior, sandbox-vs-prod data freshness
