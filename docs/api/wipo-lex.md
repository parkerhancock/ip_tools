# WIPO Lex

Read-only access to the [WIPO Lex](https://www.wipo.int/wipolex/) public web surface — WIPO's curated global IP statute / treaty / judgment database across ~200 jurisdictions in six UN languages. v0.9 scope is the **legislation** collection (search + per-entry detail with PDF/DOC attachment links). Treaties and judgments share the same URL shape and are planned follow-ups.

## Auth

None. WIPO Lex is a free public service. The client identifies itself with a polite User-Agent and uses the shared `BaseAsyncClient` cache so repeat fetches don't hit WIPO's CDN.

## Quick Start

```python
from patent_client_agents.wipo_lex import (
    GetLegislationInput,
    SearchLegislationInput,
    SubjectMatter,
    TypeOfText,
    WipoLexClient,
    get_legislation,
    search_legislation,
)

async with WipoLexClient() as client:
    # Canadian patent statutes
    results = await client.search_legislation(
        country_codes=["CA"],
        subject_matter=[SubjectMatter.PATENTS],
        type_of_text=[TypeOfText.MAIN_IP_LAWS],
    )
    for hit in results.hits:
        print(hit.legislation_id, hit.title)

    # Detail page with downloadable PDFs
    detail = await client.get_legislation("23293")  # Canadian Patent Act
    for f in detail.files:
        print(f.label, "→", f.url)
```

## Functions

| Function | Description |
|---|---|
| `search_legislation(country_codes, subject_matter, type_of_text, keywords, start_date, end_date, include_historical)` | Search the legislation collection |
| `get_legislation(legislation_id)` | Per-entry metadata + downloadable file links |

## Filter Codes

`SubjectMatter`:

| Code | Subject |
|---|---|
| 1 | Patents (Inventions) |
| 2 | Utility Models |
| 3 | Industrial Designs |
| 4 | Trademarks |
| 5 | Geographical Indications |
| 9 | Trade Secrets |
| 10 | Plant Variety Protection |
| 11 | Copyright |
| 12 | Enforcement |

Full list of 21 codes available on `patent_client_agents.wipo_lex.SubjectMatter`.

`TypeOfText`:

| Code | Type |
|---|---|
| 205 | Main IP Laws |
| 207 | Implementing Rules / Regulations |
| 210 | IP-related Laws |
| 213 | Framework Laws |
| 214 | Other Texts |
| 215 | National IP Strategy |

## Examples

```python
# Trade-secret statutes globally
results = await search_legislation(
    SearchLegislationInput(subject_matter=[SubjectMatter.TRADE_SECRETS])
)

# UK IP enforcement statutes
results = await search_legislation(
    SearchLegislationInput(
        country_codes=["GB"],
        subject_matter=[SubjectMatter.ENFORCEMENT],
    )
)

# Pull the 35 U.S.C. PDF
detail = await get_legislation(GetLegislationInput(legislation_id="21466"))
```

## Stability Notes

The connector wraps two stable server-rendered surfaces (WIPO Lex does not publish a JSON API):

- `/wipolex/en/legislation/results` — search results, parses each `<a href="/legislation/details/{ID}">{Title}</a>` anchor.
- `/wipolex/en/legislation/details/{id}` — detail page; canonical metadata travels on `<meta property="og:title|og:url">` and `<meta name="description">` (most stable layer WIPO exposes) plus file-attachment anchors discovered by extension substring.

If WIPO restyles the page, the meta layer survives; only the file-link selector in `transformers.py` would need updating.

## MCP Tool Surface

Two tools register unconditionally (no env gate — WIPO Lex is public):
`search_wipo_lex_legislation`, `get_wipo_lex_legislation`.
