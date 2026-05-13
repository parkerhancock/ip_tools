# CanLII

Read-only access to the [CanLII REST API](https://github.com/canlii/API_documentation/blob/master/EN.md), covering Canadian courts, tribunals, statutes, and regulations.

## IP-relevant databases

| `database_id` | Coverage |
|---|---|
| `csc-scc` | Supreme Court of Canada |
| `fca` | Federal Court of Appeal |
| `fct` | Federal Court |
| `tmob-comc` | Trade-marks Opposition Board / Commission des oppositions des marques de commerce |
| `cab-cab` | Commissioner of Patents — Patent Appeal Board decisions |
| `cas` | Federal statutes (consolidated) |
| `car` | Federal regulations |

## Authentication

Free API key via the [CanLII feedback form](https://www.canlii.org/en/feedback/feedback.html).
Set `CANLII_API_KEY` in the environment.

## Limits

- HTTPS only
- Max `result_count` = 10,000 per browse
- 10 MB response cap (surfaces as `TOO_LONG` envelope → `ApiError(413)`)

## Quick example

```python
from patent_client_agents.canlii import (
    BrowseCasesInput,
    browse_cases,
    get_case,
    GetCaseInput,
)

# Last 20 TMOB decisions
cases = await browse_cases(BrowseCasesInput(database_id="tmob-comc", result_count=20))

# Detailed view of a Federal Court IP case
case = await get_case(
    GetCaseInput(database_id="fct", case_id="2024fc12345")
)
```

## Cross-jurisdiction notes

CanLII surfaces both English and French content via the `language` parameter
(except the citator, which is English-only). Point-in-time legislation
queries use `start_date` / `end_date` on the legislation metadata, which
reflect the entry-into-force and repeal dates respectively.
