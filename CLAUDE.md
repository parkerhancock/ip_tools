# IP Tools

Async Python library for patent data from USPTO, EPO, Google Patents, and JPO.

## Development

```bash
uv sync --group dev              # Install dependencies
uv run pytest                    # Run tests (685 tests, ~7s)
uv run ruff check src/ tests/    # Lint
uv run ruff format src/ tests/   # Format
```

## Testing

Tests use `pytest-recording` (VCR.py) to replay recorded HTTP interactions. Cassettes live in `tests/<module>/cassettes/`.

```bash
uv run pytest                                          # Replay from cassettes (default)
uv run pytest --record-mode=new_episodes               # Record missing cassettes
uv run pytest --cov=ip_tools --cov-report=term-missing # Coverage report
```

Coverage: 88% excluding JPO (no credentials available). Target: keep above 85%.

When adding new API client methods, record a cassette and scrub credentials before committing:
- EPO: client_id, client_secret, access_token
- USPTO ODP: `USPTO_ODP_API_KEY`

## Architecture

```
src/ip_tools/
  core/           # Base client, caching, retry, logging, exceptions
  google_patents/  # Scrapes Google Patents (no API key needed)
  epo_ops/        # EPO Open Patent Services (needs EPO_OPS_API_KEY/SECRET)
  uspto_odp/      # USPTO Open Data Portal (needs USPTO_ODP_API_KEY)
  uspto_assignments/  # USPTO assignment records (no key needed)
  uspto_publications/ # USPTO Public Search (no key needed)
  jpo/            # Japan Patent Office (needs JPO_API_USERNAME/PASSWORD)
```

## Error Handling

Log-first pattern: exceptions include a path to `~/.cache/ip_tools/ip_tools.log` in their message. Full stacktraces go to the log file; agents see only concise messages. See `core/exceptions.py` and `core/logging.py`.

## Key Conventions

- All clients extend `core.base_client.BaseAsyncClient` and use async context managers
- HTTP caching via `hishel` (SQLite-backed), retry via `tenacity`
- Models are Pydantic v2
- The skill lives at `skills/ip_research/` and is symlinked to `~/.claude/skills/`
