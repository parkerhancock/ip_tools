# Sprint 1 Plan

Foundations + 3 connectors. ~10 working days. All in `patent-client-agents`.

## Scope decisions (locked)

- Home for new modules: **inside `patent-client-agents`** (PCA becomes the "all IP data" wheel)
- Naming: **lowercase office name** (`ip_australia`, `canlii`, `wipo_lex`) — matches `uspto_odp`, `epo_ops`, `google_patents`
- Extraction timing: **build first, extract second** — ship `wipo_lex` as a standalone client; extract `StaticLawCorpus` after we have 3 concrete examples (mpep, tmep, wipo_lex)
- Stretches out of scope: EUIPO, PISTE/Légifrance/Judilibre — sprint 2 anchors

## Foundation: `OAuth2ClientCredentialsClient`

**Where:** `src/law_tools_core/oauth2_client.py`
**Why first:** validates the abstraction three times in sprint 1+2 (IP Australia → EUIPO → PISTE).

```python
class OAuth2ClientCredentialsClient(BaseAsyncClient):
    """BaseAsyncClient + OAuth2 client_credentials token management."""

    TOKEN_URL: str = ""           # subclass override
    DEFAULT_SCOPE: str | None = None

    def __init__(self, *, client_id, client_secret, sandbox=False, **kwargs):
        ...

    async def _get_token(self) -> str:
        # Cached token w/ expiry-aware refresh; re-fetches on 401
        ...

    async def _request(self, method, path, **kwargs):
        # Wraps super()._request to inject Authorization: Bearer <token>
        # On 401, re-fetch token once, retry once.
        ...
```

**Acceptance criteria:**
- [ ] Token cached in-memory with `expires_at` minus 30s safety margin
- [ ] Sandbox vs prod via constructor flag (each subclass declares both URLs)
- [ ] On HTTP 401: refresh token once, retry the request once, then raise `AuthenticationError`
- [ ] Test with httpx `MockTransport` (no real OAuth round-trip; just verify header injection + refresh-on-401)
- [ ] Existing `BaseAsyncClient` retry/cache behavior preserved

---

## Connector 1: `ip_australia` (biggest single win)

**Why first:** four IP rights from one OAuth stack; weekly CC-BY bulk dumps; cleanest validation of `OAuth2ClientCredentialsClient`. Survey: `research/connectors/ip_australia.md`.

### Module layout

```
src/patent_client_agents/ip_australia/
  __init__.py                # re-exports api.py
  api.py                     # Pydantic inputs + module-level async fns
  client.py                  # IpAustraliaPatentsClient, IpAustraliaTrademarksClient,
                             #   IpAustraliaDesignsClient — all subclass OAuth2ClientCredentialsClient
  bulk.py                    # IpRapidLoader — weekly CSV ZIP from data.gov.au
  models.py                  # Pydantic response models per right type
  transformers.py            # JSON → models (light; IP Australia returns clean JSON)
  resources.py               # MCP usage doc URI
  docs/usage.md
  py.typed
```

### API surface (api.py)

```python
# Patents
async def search_au_patents(params: AuPatentSearchInput) -> AuPatentSearchResponse: ...
async def get_au_patent(number: str) -> AuPatent: ...

# Trade marks
async def search_au_trademarks(params: AuTrademarkSearchInput) -> AuTrademarkSearchResponse: ...
async def get_au_trademark(number: str) -> AuTrademark: ...

# Designs
async def search_au_designs(params: AuDesignSearchInput) -> AuDesignSearchResponse: ...
async def get_au_design(number: str) -> AuDesign: ...

# Bulk
async def load_ip_rapid(asof: date | None = None, kind: Literal["patents","tm","designs","pbr"]) -> Path: ...
```

### Endpoints

| Endpoint | Base URL |
|---|---|
| Patents | `production.api.ipaustralia.gov.au/public/australian-patent-search-api/v1/` |
| Trade marks | `production.api.ipaustralia.gov.au/public/australian-trade-mark-search-api/v1/` |
| Designs | `production.api.ipaustralia.gov.au/public/australian-design-search-api/v1/` |
| Token | `portal.api.ipaustralia.gov.au` |
| Bulk | `data.gov.au/data/dataset/iprapid` (CKAN — no auth) |

### Env vars

`IP_AUSTRALIA_CLIENT_ID`, `IP_AUSTRALIA_CLIENT_SECRET` (plus `IP_AUSTRALIA_SANDBOX=1` for `test.api.ipaustralia.gov.au`).

### MCP wrapper

`src/patent_client_agents/mcp/tools/ip_australia.py` — 6 tools:
- `search_au_patents`, `get_au_patent`
- `search_au_trademarks`, `get_au_trademark`
- `search_au_designs`, `get_au_design`

Env-gate the entire `ip_australia_mcp` if either credential var is missing (same pattern as JPO).

### Tests

`tests/ip_australia/` mirrors src layout; VCR cassettes for OAuth token exchange + each endpoint.

### Acceptance

- [ ] All 6 endpoints return Pydantic models that match real production responses
- [ ] IP RAPID loader downloads + extracts the weekly ZIP into a configurable cache dir
- [ ] OAuth token refresh-on-401 verified
- [ ] CATALOG.md updated with the new row
- [ ] `src/patent_client_agents/catalog/sources/ip-australia.md` written

---

## Connector 2: `canlii` (highest leverage per LOC)

**Why second:** validates the simple-API-key pattern; lights up CA courts + statutes + tribunals in one client. Independent of OAuth work, can run in parallel.

### Module layout

```
src/patent_client_agents/canlii/
  __init__.py
  api.py                     # Pydantic inputs + async fns
  client.py                  # CanLIIClient(BaseAsyncClient) — API key as query param
  models.py                  # Case, Legislation, Citation, Database, etc.
  resources.py
  docs/usage.md
  py.typed
```

### API surface (api.py)

```python
async def list_databases() -> list[Database]: ...
async def browse_cases(database_id: str, year: int | None = None) -> list[CaseRef]: ...
async def search_cases(query: str, jurisdiction: str | None = None, ...) -> CaseSearchResponse: ...
async def get_case(database_id: str, case_id: str) -> Case: ...
async def get_case_citations(database_id: str, case_id: str) -> CitationGraph: ...

async def list_legislation(jurisdiction: str) -> list[LegislationRef]: ...
async def get_legislation(jurisdiction: str, statute_id: str, *, at: date | None = None) -> Legislation: ...
```

### Endpoint

`api.canlii.org/v1/` — JSON, API key as `?api_key=...`. Free key by request.

### Env var

`CANLII_API_KEY` — env-gate MCP registration (no key → no `canlii_mcp` mount).

### MCP wrapper

`src/patent_client_agents/mcp/tools/canlii.py` — 6 tools mirroring the API surface.

### Tests

`tests/canlii/` with VCR cassettes. Test the IP-relevant slice: Patent Act + Trademarks Act fetches, FC/FCA IP cases, TMOB + PAB browse.

### Acceptance

- [ ] All 7 endpoints return Pydantic models
- [ ] Point-in-time legislation queries work
- [ ] Citation graph endpoint surfaces citing + cited cases
- [ ] CATALOG.md + per-source catalog doc

### Open ToS question to resolve before scaling

CanLII docs warn against high-volume scraping; keys revocable. Confirm with their feedback channel that our cache-and-serve pattern (CoWork allowlist) is permitted **before** the connector ships publicly. Until cleared, ship as `private_only` (env-gated).

---

## Connector 3: `wipo_lex` (statute backbone)

**Why third:** unlocks substantive-law coverage for ~200 jurisdictions; the rest of Tier 1/2/3 statute fetchers become opportunistic on top of this.

### Module layout

```
src/patent_client_agents/wipo_lex/
  __init__.py
  api.py                     # Pydantic inputs + async fns
  client.py                  # WipoLexClient(BaseAsyncClient) — polite scrape
  models.py                  # LegislationEntry, Treaty, Decision, Jurisdiction
  transformers.py            # HTML/PDF → models
  resources.py
  docs/usage.md
  py.typed
```

### API surface (api.py)

```python
async def list_jurisdictions() -> list[Jurisdiction]: ...
async def list_legislation(jurisdiction: str, *, ip_type: IpType | None = None) -> list[LegislationEntry]: ...
async def get_legislation(legislation_id: str) -> Legislation: ...           # includes PDF bytes
async def list_treaties(*, party: str | None = None) -> list[Treaty]: ...
async def list_decisions(jurisdiction: str) -> list[Decision]: ...
async def search(query: str, *, ip_type: IpType | None = None, jurisdiction: str | None = None) -> WipoLexSearchResponse: ...
```

### Endpoint

`wipo.int/wipolex/en/main/legislation` — HTML pages with PDF/DOC attachments. No API.

### Rate-limit hygiene

- Polite User-Agent identifying patent-client-agents + contact URL
- Default to 1 RPS (configurable via constructor)
- Cache aggressively (WIPO Lex content updates rarely)
- Confirm WIPO Lex licensing posture for bibliographic metadata layer (open question from Tier 1 survey)

### MCP wrapper

`src/patent_client_agents/mcp/tools/wipo_lex.py` — 5-6 tools. No env-gate; public.

### Tests

`tests/wipo_lex/` with VCR. Cover top 10 jurisdictions, all 5 endpoints.

### Acceptance

- [ ] Listing works for all 200+ jurisdictions
- [ ] Per-legislation fetch returns metadata + linked PDF bytes
- [ ] Search across all IP types works
- [ ] CATALOG.md + per-source catalog doc
- [ ] Polite-scrape settings documented

---

## Cross-cutting work

- **CATALOG.md** — three new rows in "Active sources"
- **per-source catalog docs** — `catalog/sources/ip-australia.md`, `canlii.md`, `wipo-lex.md`
- **MCP server instructions** — extend the `instructions=` string in `mcp/server.py` to mention the new sources
- **mcp/__init__.py** — `ip_mcp.mount(ip_australia_mcp)` etc.
- **README.md** — bump module list
- **CHANGELOG.md** — release notes for the version bump
- **`unified.py`** — *no fused helpers yet*; cascade opportunities to consider in sprint 2:
  - `get_patent_claims` → could cascade to IP Australia for AU patents
  - `get_statute(jurisdiction, citation)` → cascade `wipo_lex` → national statute fetchers once they exist

## Day-by-day sequencing

Tracks run in parallel where independent. Day numbers assume one focused person.

| Day | Track A (OAuth) | Track B (CanLII — no shared dep) | Track C (WIPO Lex) |
|---|---|---|---|
| 1 | `OAuth2ClientCredentialsClient` base + tests | `canlii/client.py` + Pydantic models | `wipo_lex/client.py` + polite-scrape skeleton |
| 2 | `ip_australia/client.py` (patents endpoint only) | `canlii/api.py` cases endpoints | `wipo_lex/transformers.py` (jurisdiction list) |
| 3 | TM + Design endpoints + models | Legislation + citations endpoints | Per-legislation fetch + PDF download |
| 4 | IP RAPID bulk loader | MCP wrapper + 6 tools + tests | Search endpoint |
| 5 | MCP wrapper + 6 tools | CATALOG.md + catalog/sources/canlii.md | MCP wrapper + 5 tools |
| 6 | Tests + cassettes | (buffer / start ToS escalation) | Tests + cassettes |
| 7 | CATALOG.md + catalog doc | — | CATALOG.md + catalog doc |
| 8 | Integration: env-gate MCP, run `uv run pytest` end-to-end | — | — |
| 9 | Release prep — version bump, CHANGELOG, README | — | — |
| 10 | Buffer (catch up; or sprint-2 prep for EUIPO) | — | — |

In practice one person runs all three tracks serialized — call it 10 working days end to end.

## Risks

1. **IP Australia OAuth quotas not documented in numbers** — only the 429 contract. Register a sandbox app early to get real numbers before sprint ends.
2. **CanLII ToS for cache-and-serve** — ship private-only until cleared. Don't let this block code; ship code, gate exposure.
3. **WIPO Lex etiquette / licensing** — open question from Tier 1. Default to conservative 1 RPS, attribute aggressively. Confirm before scaling.
4. **OAuth abstraction over-engineering** — risk that the base class accommodates EUIPO/PISTE quirks we haven't seen yet. **Mitigation:** build minimal for IP Australia first, refactor when EUIPO/PISTE land in sprint 2. Resist designing for hypotheticals.
5. **Cassette recording drift** — re-recording cassettes against live APIs requires real credentials. Document the auth-header redaction setup before recording.

## Definition of done

- [ ] All 3 connectors importable: `from patent_client_agents.ip_australia import ...`
- [ ] All MCP tools registered + listed by `fastmcp list-tools`
- [ ] `uv run pytest` green (cassettes replay clean)
- [ ] `uv run ruff check src/ tests/` clean
- [ ] CATALOG.md updated, three new catalog/sources/ docs
- [ ] CHANGELOG.md entry for the version bump
- [ ] README module list extended
- [ ] At least one fused helper opportunity identified for sprint 2 (don't ship one yet)

## What we deliberately do NOT do in sprint 1

- Extract `StaticLawCorpus` — wait until we have wipo_lex + mpep + tmep as 3 concrete examples
- Build `StructuredCaseLawClient` — wait until judilibre + Find Case Law + CELLAR force the abstraction
- Wire `unified.py` fusions — wait for clear cascade opportunities (sprint 2)
- Add EUIPO, PISTE, or any sprint-2 connector — focus
- Touch `mpep`/`tmep` for refactoring — they work; leave them alone until extraction makes sense
