# WIPO Lex

Read-only access to the WIPO Lex public web surface — global IP statute, treaty, and judgment database curated by WIPO for ~200 jurisdictions in six UN languages. The sprint-1 client wraps the **legislation** collection (search + detail).

## Why WIPO Lex

If your agent needs to ask "what statutes govern patent eligibility in jurisdiction X?", this is the answer key. WIPO Lex carries the canonical text for the IP laws of essentially every UN member, along with WIPO-administered treaties and many national IP judgments. Translations are WIPO-curated; the native text always controls.

## Authentication

None. Public service. The client identifies itself with a descriptive User-Agent and caches aggressively (WIPO Lex content updates rarely).

## Quick example

```python
from patent_client_agents.wipo_lex import (
    GetLegislationInput,
    SearchLegislationInput,
    SubjectMatter,
    TypeOfText,
    get_legislation,
    search_legislation,
)

# List Canadian patent statutes
results = await search_legislation(
    SearchLegislationInput(
        country_codes=["CA"],
        subject_matter=[SubjectMatter.PATENTS],
        type_of_text=[TypeOfText.MAIN_IP_LAWS],
    )
)
for hit in results.hits:
    print(hit.legislation_id, hit.title)

# Fetch detail for the Canadian Patent Act (with PDF links)
detail = await get_legislation("23293")
print(detail.title, detail.jurisdiction)
for f in detail.files:
    print(" ", f.label, "→", f.url)
```

## Scope of subject matter codes

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

Full list lives on `SubjectMatter` (`patent_client_agents.wipo_lex.SubjectMatter`).

## What's NOT in this connector yet

Sprint 1 covers **legislation** only. Treaties and judgments use the same URL shape and can be added by reusing the same transformer pattern — they're listed in the index as follow-ups, not gaps.

## Etiquette

- Default User-Agent identifies the library and points at a project URL
- Aggressive caching via the shared `BaseAsyncClient` SQLite store
- No documented numeric rate limits — be polite

## Stability notes

The connector parses two stable surfaces:

1. **`/legislation/results`** — search results page, where each hit is a stable
   `<a href="/wipolex/en/legislation/details/{ID}">{Title}</a>` anchor.
2. **`/legislation/details/{id}`** — detail page, where the canonical metadata
   travels on `<meta property="og:title|og:url">` and `<meta name="description">`
   tags plus a list of attachment links under known CSS classes.

If WIPO restyles the page, the meta layer survives; only the file-link
selector in `transformers.py` would need updating.
