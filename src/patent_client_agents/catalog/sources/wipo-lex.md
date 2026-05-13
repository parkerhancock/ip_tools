# WIPO Lex

Free, public, no-auth access to WIPO's global IP statute, treaty, and judgment database. ~50,000 legal documents across ~200 jurisdictions, curated by WIPO and translated into the six UN languages. Sprint-1 scope is the **legislation** collection (search + detail). Treaties and judgments use the same URL/HTML shape and are planned follow-ups.

## Source

| | |
|---|---|
| Module | `patent_client_agents.wipo_lex` |
| Client | `WipoLexClient` |
| Base URL | `https://www.wipo.int` |
| Auth | None (public) |
| Rate limits | Not published; client defaults to a polite User-Agent and caches aggressively |
| Status | Active |

## Authentication

None. WIPO Lex is a public service. The client identifies itself with a descriptive User-Agent (`patent-client-agents-wipolex/<version>`) and depends on the shared `BaseAsyncClient` SQLite cache for repeat-fetch friendliness.

## API Endpoints

WIPO Lex does not publish a documented JSON API. The client wraps two stable server-rendered HTML surfaces:

| Path | Method | Coverage |
|---|---|---|
| `/wipolex/en/legislation/results` | GET | Search results list (parses anchor pattern `/legislation/details/{ID}`) |
| `/wipolex/en/legislation/details/{id}` | GET | Per-legislation metadata (OpenGraph + `<meta name>` tags + file attachments) |

Treaties and judgments use the same shape at `/wipolex/en/treaties/{results,details}` and `/wipolex/en/judgments/{results,details}` — planned for a follow-up sprint.

## Library API

```python
from patent_client_agents.wipo_lex import (
    GetLegislationInput,
    SearchLegislationInput,
    SubjectMatter,
    TypeOfText,
    get_legislation,
    search_legislation,
)

# Canadian patent statutes
hits = await search_legislation(
    SearchLegislationInput(
        country_codes=["CA"],
        subject_matter=[SubjectMatter.PATENTS],
        type_of_text=[TypeOfText.MAIN_IP_LAWS],
    )
)

# Per-legislation detail + downloadable PDFs
detail = await get_legislation("23293")  # Canadian Patent Act
for f in detail.files:
    print(f.label, f.url, f.mime_type)
```

### Methods

| Method | Description |
|---|---|
| `search_legislation(country_codes, subject_matter, type_of_text, keywords, start_date, end_date, include_historical)` | Search the legislation collection; returns hits with `legislation_id` + display title |
| `get_legislation(legislation_id)` | Per-entry metadata: title, jurisdiction, summary, canonical URL, file attachments |

### Filter codes

`SubjectMatter` enum (full list in `patent_client_agents.wipo_lex.SubjectMatter`):
1=Patents, 2=Utility Models, 3=Designs, 4=Trademarks, 5=GIs, 6=Trade Names, 7=IC Layouts, 8=Competition, 9=Trade Secrets, 10=PVP, 11=Copyright, 12=Enforcement, 13=ADR, 14=Domain Names, 15=Genetic Resources, 16=Cultural Expressions, 17=Technology Transfer, 18=Traditional Knowledge, 19=IP Regulatory Body, 20=Other, 21=Industrial Property.

`TypeOfText` enum: 205=Main IP Laws, 207=Implementing Rules, 210=IP-related Laws, 213=Framework Laws, 214=Other, 215=National IP Strategy.

## MCP Tools

| Tool | Description |
|---|---|
| `search_wipo_lex_legislation` | Search legislation across jurisdictions by subject / type / keywords / date |
| `get_wipo_lex_legislation` | Per-legislation metadata + PDF/DOC attachment links |

Both tools register unconditionally (no env gate — WIPO Lex is public).

## Related Docs

- Survey: [research/connectors/wipo.md](../../../../research/connectors/wipo.md)
- API discovery (HTML parsing notes): [research/connectors/wipo_lex_api_discovery.md](../../../../research/connectors/wipo_lex_api_discovery.md)
