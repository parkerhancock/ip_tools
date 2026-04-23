# Patent Claims (cross-source)

Retrieve structured patent claims with **nested limitation depth**, spanning
full worldwide + historical coverage.

## Why fused

Two backends have structured claim data:

- **USPTO ODP grant XML** — authoritative for US patents granted since
  ~2000; preserves the claim element tree exactly as filed.
- **Google Patents HTML** — worldwide coverage including pre-2000 US
  patents and non-US jurisdictions, with nested `<claim-text>` divs that
  encode the same limitation tree as ODP.

PPUBS also exposes claims but its parser currently collapses multi-claim
documents into a single merged claim (see memory tech-debt note). It is
**not** used as a claims source.

**Empirical result (2026-04-23):** on US10000000B2, ODP and Google produce
identical limitation counts (20/20 claims) and identical depth sequences
per claim (e.g. claim 9: `[0, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1]`). This gave us
confidence that a canonical normalized shape can be fed by either source
without information loss.

## Canonical shape

Every claim, from either source, comes back in this shape:

```python
{
    "claim_number": int,
    "limitations": [
        {"text": str, "depth": int},
        ...
    ],
    "claim_text": str,                         # rebuilt from limitations
    "claim_type": "independent" | "dependent",
    "depends_on": int | None,                  # parent claim number
}
```

`claim_text` is **derived** from `limitations` using a single formatter
(`f"{N}. " + "\n".join("    "*depth + text)`) — so both sources produce
byte-identical output. Do not rely on source-specific `claim_text` quirks;
use `limitations` for structured analysis.

### Depth semantics

- `depth=0` → claim **preamble** (e.g. "A method comprising:").
- `depth=1` → top-level requirements (sibling elements of the claim body).
- `depth=2+` → sub-requirements nested **within** a parent limitation.

For infringement claim-charting, a depth-2 sub-limitation only applies
within its depth-1 parent — don't map it as an independent requirement.

## Python API

```python
from patent_client_agents import get_patent_claims

claims = await get_patent_claims("US10000000B2")
# [{"claim_number": 1, "limitations": [{"text": "...", "depth": 0}, ...], ...}, ...]

# Only independent claims:
independents = [c for c in claims if c["depends_on"] is None]

# Infringement-chart-style mapping:
limitation_map = {c["claim_number"]: c["limitations"] for c in claims}
```

Helpers are also exported if you need to normalize your own claim data:

```python
from patent_client_agents import (
    build_canonical_claim,
    odp_limitations_from_text,
    google_limitations_from_html,
)
```

## MCP tool

```
get_patent_claims(patent_number, view="full" | "independent_only" | "limitations") -> dict
```

- `view="full"` (default) — `{"patent_number": ..., "claims": [...]}` with the full canonical list.
- `view="independent_only"` — same shape, filtered to claims where `depends_on is None`.
- `view="limitations"` — compact `{"patent_number": ..., "limitations_by_claim": {N: [...]}}`.

## Coverage & failure modes

- US patents post-~2000 → ODP path, always. Fast and authoritative.
- US patents pre-2000, non-US patents → ODP raises `NotFoundError` /
  `ValidationError`; the tool transparently falls through to Google.
- `NotFoundError` only raises when **both** sources lack the patent.
