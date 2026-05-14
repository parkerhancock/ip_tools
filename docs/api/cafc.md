# Federal Circuit (CAFC)

Read-only access to opinions from the [US Court of Appeals for the Federal Circuit](https://www.cafc.uscourts.gov/) — the court that hears virtually every appeal in a US patent case, plus ITC §337, government‑contract, veterans, and trademark TTAB appeals. The connector wraps the court's WordPress DataTables API behind the opinions page, classifies each opinion as patent‑related by keyword scoring, and exposes PDF download through the shared `pca://cafc/...` resource channel.

## Auth

None. The CAFC opinions page is public. The client scrapes the WordPress nonce from the page on first request and feeds it back to the DataTables AJAX endpoint; no user account required.

## Quick Start

```python
from datetime import date
from patent_client_agents.cafc import CAFCClient

async with CAFCClient() as client:
    # Patent appeals from PTAB, district court, ITC, and Court of Federal Claims
    opinions = await client.search(
        date_from=date(2025, 1, 1),
        origins=["PTO", "DCT", "ITC", "CFC"],
        max_results=50,
    )
    for op in opinions:
        print(op.release_date, op.appeal_number, op.case_name)

    # Or the convenience method for the same patent-origin filter
    patent_opinions = await client.search_patent_opinions(date_from=date(2025, 1, 1))

    # Last 30 days, all origins
    recent = await client.recent(days=30)
```

## Functions

| Method | Description |
|---|---|
| `search(query, date_from, date_to, origins, max_results)` | Free-text + date + origin filter against the upstream DataTables search |
| `search_patent_opinions(date_from, date_to, max_results)` | Pre-filtered to origins `PTO`, `DCT`, `ITC`, `CFC` |
| `recent(days)` | Convenience: last *N* days, all origins |
| `download_pdf(opinion, output_path)` | Fetch the opinion PDF bytes; optionally write to disk |

## Origin codes

| Code | Meaning | Patent-relevant? |
|---|---|---|
| `PTO` | USPTO / PTAB appeals | Yes |
| `DCT` | District court appeals | Yes (patent infringement) |
| `ITC` | US International Trade Commission §337 | Yes |
| `CFC` | Court of Federal Claims | Yes (gov-contract patent claims) |
| `CAVC` | Court of Appeals for Veterans Claims | No |
| `MSPB` | Merit Systems Protection Board | No |

The `is_patent_case` flag on each `CAFCOpinion` is computed independently by a keyword classifier (`PatentClassifier`), not just by origin — so unusual origins that *do* mention patents still get flagged.

## Patent classifier

`PatentClassifier` weighs keyword categories (strong indicators like "patent", "USPTO", "PTAB"; statute references like `35 U.S.C. § 103`; technical terms like "infringement", "claim construction") to produce `(is_patent, confidence, matched_keywords)`. False positives like "patient care" and "patent leather" are filtered. Default threshold is 0.5.

```python
from patent_client_agents.cafc import PatentClassifier

classifier = PatentClassifier()
is_patent, confidence, keywords = classifier.classify(
    "Apple Inc. v. Vidal, Director of the USPTO"
)
# is_patent=True, confidence~=0.9, keywords includes "uspto" and "vidal"
```

## Stability Notes

- The DataTables API is undocumented; the URL shape, column ordering, and nonce mechanism have been stable for years but are not contractual.
- The client's `_init_session()` extracts the WordPress nonce by regex from the opinions HTML page; if the WordPress theme is restyled and removes the `wdtNonceFrontendServerSide_1` hidden input, the regex would need updating.
- CAFC's edge (CloudFront + WordPress) blocks plain Python user agents on the AJAX endpoint with a 403. The client sends a regular desktop Chrome User-Agent to pass.
- PDF URLs are absolute against the WordPress origin; opinions older than ~2010 occasionally redirect.

## MCP Tool Surface

| Tool | Description |
|---|---|
| `search_cafc_opinions` | Free-text search + optional `patent_only` filter |
| `search_cafc_patent_opinions` | Pre-filtered to patent-origin (PTO/DCT/ITC/CFC) |
| `download_cafc_pdf` | Fetch an opinion PDF by appeal number; returns a signed `download_url` |
