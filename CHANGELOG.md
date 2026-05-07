# Changelog

All notable changes to `patent-client-agents` are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.7.0] — 2026-05-07

### Added

- **Env-gated MCP tool registration** via
  `law_tools_core.mcp.conditional_tool` and the parallel
  `register_source_if_configured` helper. Tools registered with
  `@conditional_tool(mcp, requires_env=[...])` only appear in
  `tool/list` when every named env var is set and non-empty;
  otherwise the function is still callable from Python but no
  MCP-side registration happens. Decorator-time gate (no per-call
  overhead); restart the process to pick up env changes.
- All 12 JPO MCP tools (`get_jpo_progress`, `get_jpo_progress_simple`,
  `get_jpo_priority_info`, `get_jpo_registration_info`,
  `get_jpo_number_reference`, `get_jpo_jplatpat_url`,
  `get_jpo_applicant_by_code`, `get_jpo_applicant_by_name`,
  `get_jpo_documents`, `get_jpo_patent_divisional_info`,
  `get_jpo_patent_cited_documents`,
  `get_jpo_pct_national_phase_number`) now auto-register only when
  both `JPO_API_USERNAME` and `JPO_API_PASSWORD` are set. The
  `jpo/documents` download fetcher uses
  `register_source_if_configured` for the same env gate (defense
  in depth).
- The hosted public deploy at `mcp.patentclient.com` intentionally
  does NOT carry these keys per JPO TOS; private deploys (e.g.
  law-tools on `bb-law-mcp-prod`) flip JPO on by mounting the
  secrets in their own Cloud Run env.

### Changed

- This is a behavior change for any deployment that previously
  saw `get_jpo_*` tools advertised without JPO credentials in
  the env. The tools were already non-functional in that case
  (every call failed at OAuth2 password-grant time); now they
  no longer appear in `tool/list`.

## [0.6.6] — 2026-05-05

### Fixed

- **Default cache HTTP client no longer impersonates Chrome.**
  `build_cached_http_client` was injecting a Chrome 127 `User-Agent`
  and `Accept-Language: en-US,en;q=0.9` for every `BaseAsyncClient`
  subclass. Combined with httpx's Python TLS fingerprint, that
  triggered Akamai (and similar) bot-management WAFs to 403 hard on
  USITC EDIS, federalregister.gov, and consumerfinance.gov. The
  default UA is now httpx's native `python-httpx/<ver>` string, which
  those WAFs allow as a known programmatic consumer. Callers that
  need a specific UA (e.g. SEC EDGAR's email-contact mandate) still
  override via `headers=`. Two regression tests guard against the
  Chrome UA sneaking back in.

## [0.6.5] — 2026-05-04

### Added

- `make_auth(client_storage=...)` accepts an `AsyncKeyValue` and
  threads it through to FastMCP's `GoogleProvider`. Hosted MCP
  deployments need this — FastMCP's default `FileTreeStore` is
  per-container and silently breaks Dynamic Client Registration when
  containers cycle or scale horizontally.

### Changed

- `epo_ops.fetch_fulltext` now raises a clean `ValueError` for the
  "no full-text indexed" case instead of bubbling EPO's raw 404 with
  its opaque log-path hint.

## [0.6.4] — 2026-05-04

### Fixed

- `make_auth` static verifier now claims full-URL Google scopes,
  matching what the Google Identity API actually issues.

## [0.6.3] — 2026-05-04

### Fixed

- `make_auth` static verifier now claims Google scopes on the
  `MultiAuth` path (previously only set on the single-provider path).

## [0.6.2] — 2026-05-04

### Added

- `make_auth` accepts env-driven issuer / redirect URLs so hosted
  deployments can configure them without code changes.

## [0.6.1] — 2026-04-30

### Added

- `LAW_TOOLS_CORE_LOG_TO_STDOUT` attaches a `StreamHandler(sys.stdout)`
  to the tool-call logger. Right for Cloud Run / container
  deployments where the filesystem is ephemeral and stdout is
  captured by Cloud Logging. Existing `LAW_TOOLS_CORE_LOG_DIR` file
  sink still works; either, both, or neither can be set.

## [0.6.0] — 2026-04-30

### Changed (breaking)

- **`uspto_assignments`: consolidated search surface onto
  `/search/patent`.** Replaces `search_by_assignee`, `search_by_assignor`,
  `search_by_patent`, `search_by_application`, `search_by_reel_frame`,
  `search`, `search_all`, and `get_application_assignments` with a
  single `search()` method that returns `SearchResults`. Callers must
  migrate to the new method.

### Added

- **`google_patents`: estimated expiration date.** When Google Patents
  returns an empty `expiration_date`, the client now estimates it as
  `priority_date + 20 years` and exposes a new `expiration_estimated:
  bool` field on the result so callers can distinguish authoritative
  vs estimated values.

[0.6.6]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.6
[0.6.5]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.5
[0.6.4]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.4
[0.6.3]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.3
[0.6.2]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.2
[0.6.1]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.1
[0.6.0]: https://github.com/parkerhancock/patent-client-agents/releases/tag/v0.6.0
