# IP Australia — Connector Survey

One-page scoping survey for adding Australian IP coverage to `patent-client-agents`. IP
Australia administers all four IP rights from one agency (patents, trade marks, designs,
plant breeder's rights), publishes signed REST APIs for live search, and dumps the same
registry to data.gov.au as bulk longitudinal datasets. The open-data culture here is the
strongest of any jurisdiction we have surveyed.

## Cross-asset comparison

| Asset | URL | Auth | Format | Bulk? | Notes |
|---|---|---|---|---|---|
| **AusPat (Patents API)** | `production.api.ipaustralia.gov.au/public/australian-patent-search-api/v1/` | OAuth 2.0 (client_credentials) | JSON | via IPGOD/IP RAPID | quick search + get-by-number; UI at pericles.ipaustralia.gov.au |
| **Trade Marks API** | `production.api.ipaustralia.gov.au/public/australian-trade-mark-search-api/v1/` | OAuth 2.0 | JSON | via IPGOD/IP RAPID | quick search + get-by-number + `updated-since` |
| **Designs API** | `production.api.ipaustralia.gov.au/public/australian-design-search-api/v1/` | OAuth 2.0 | JSON | via IPGOD/IP RAPID | filter by Locarno class, status, `updated-since` |
| **Plant Breeder's Rights DB** | `pericles.ipaustralia.gov.au/pbr_db/` and `ipsearch.ipaustralia.gov.au` | none | HTML scrape | via IPGOD/IP RAPID | no documented REST API |
| **IP RAPID** (successor to IPGOD) | `data.gov.au/data/dataset/iprapid` | none | CSV (zipped) | YES (weekly) | IP Refreshed Automated Product for Information and Data; weekly refresh |
| **IPGOD** (annual, legacy) | `data.gov.au/data/dataset/intellectual-property-government-open-data-*` | none | CSV (zipped) | YES (annual) | ~40 tables, 100+ yrs back; CC-BY 2.5 AU |
| **IPLORD** | `data.gov.au/data/dataset/intellectual-property-longitudinal-research-data-2020` | none | CSV | YES (annual) | applicant-centric 20-yr panel, 360k AU + 250k intl applicants |
| **eServices** | `services.ipaustralia.gov.au` | login | HTML/forms | no | filing only; no public read API beyond the search APIs above |
| **Patent Examiner's Manual** | `manuals.ipaustralia.gov.au/patents/Patent_Examiners_Manual.htm` | none | HTML | no | Australian MPEP equivalent |
| **Trade Marks Manual** | `manuals.ipaustralia.gov.au/trademark` | none | HTML | no | parallel structure |
| **Legislation** | `legislation.gov.au` + `austlii.edu.au` | none | HTML/PDF/XML | partial | Federal Register of Legislation is canonical |
| **APO Hearings & Federal Court** | `austlii.edu.au` (`/au/cases/cth/APO/`, `/au/cases/cth/FCA/`) | none | HTML | partial (SINO CGI) | from 1981 onward |

## Per-asset notes

### 1. AusPat / Australian Patent Search API
Live search backed by the same dataset that powers the UI at
`pericles.ipaustralia.gov.au/ols/auspat/quickSearch.do`. Two REST endpoints:
`POST /search/quick` (list of patent numbers or basic details) and `GET /{number}`
(everything publicly available). Bibliographic coverage back to 1904; full text varies.
OAuth 2.0 client_credentials grant against the External Token API. Free to call.

### 2. Australian Trade Mark Search API (ex-ATMOSS)
Same shape as patents API. `POST /search/quick` takes `type`, `status`, `query`, and
`updated-since` — the last one is the key differentiator vs USPTO TSDR and makes
incremental sync trivial. OpenAPI description published at
`descriptions.api.gov.au/ipaustralia/trademark-search/iptms.html`. The
`atmoss.com.au` site is a third-party gateway, not IP Australia.

### 3. Australian Designs Search API
Same auth and shape; supports filter by Locarno classification, status, image, and
`updated-since`. Australia is one of the only common-law jurisdictions with both a clean
designs REST API and a longitudinal designs dataset (IPGOD includes designs tables).

### 4. Plant Breeder's Rights database
PBR is administered by IP Australia (unlike UK where it sits with DEFRA, CN where it's
MARA). No documented REST API; UI at `pericles.ipaustralia.gov.au/pbr_db/` and
`ipsearch.ipaustralia.gov.au`. Reliable PBR access today is via the IPGOD/IP RAPID PBR
tables, not live. v2 candidate at best.

### 5–6. IP RAPID and IPGOD (the crown jewel)
**IPGOD** (Intellectual Property Government Open Data) is ~40 CSV tables covering
patents, trade marks, designs, and PBR over ~100 years, with derived applicant
information. Released under **Creative Commons Attribution 2.5 Australia**. The 2019
release standardised dates to ISO `yyyy-mm-dd`, indicator columns to boolean, UTF-8 with
`\` escape — clean, parquet-friendly schema. Annual cadence (2018, 2019, 2020, 2021, …).

**IP RAPID** ("IP Refreshed Automated Product for Information and Data") is the new
successor, **refreshed weekly** rather than annually, at
`data.gov.au/data/dataset/iprapid`. Same underlying registry, same license, same
schema lineage. This is closer to a registry mirror than to USPTO weekly bulk dumps —
it's the entire registry every week, not deltas.

### 7. IPLORD
Applicant-centric panel of 360k AU and 250k international applicants over 20 years.
Built around applicants rather than applications — useful for portfolio scoring and
M&A diligence but not for live-status queries. CSV on data.gov.au, CC-BY.

### 8. eServices
Filing portal. No documented public read API; the live REST APIs in §1–§3 are the
intended read channel. Skip.

### 9. API platform — `portal.api.ipaustralia.gov.au`
Salesforce Community-style portal listing **6 APIs** in the catalog. OAuth 2.0
client_credentials. Free to call (per-action fees only for filings). Sandbox at
`test.api.ipaustralia.gov.au`, production at `production.api.ipaustralia.gov.au`.
Documented also on Anypoint Exchange (`anypoint.mulesoft.com/exchange/portals/ip-australia-3/`)
and via OpenAPI at `descriptions.api.gov.au/ipaustralia/...`. Published rate limits not
disclosed publicly; the standard ATO/api.gov.au pattern is per-client throttling.

### Substantive law
- `legislation.gov.au` is canonical — Patents Act 1990, Trade Marks Act 1995, Designs
  Act 2003, Copyright Act 1968, Plant Breeder's Rights Act 1994, plus their Regulations.
- `austlii.edu.au` mirrors the same Acts (consolidated, hyperlinked) and is more
  scrape-friendly. SINO CGI API at `austlii.edu.au/techlib/webdev/cgiapi.html` exposes
  search over the whole AustLII collection.
- Trade secrets: no statute. Common law breach of confidence (UK/Canada lineage).
- Examiner manuals at `manuals.ipaustralia.gov.au` — patents and trade marks each have
  a full online manual; chunkable for MPEP-style RAG.

### Tribunals and courts
- **APO hearings** from 1981 onward on AustLII at `/au/cases/cth/APO/`. HTML.
- **Trade marks hearings** at `/au/cases/cth/ATMO/`.
- **Federal Court of Australia** (`/au/cases/cth/FCA/`) and **High Court**
  (`/au/cases/cth/HCA/`) handle appeals and infringement.
- **AAT** handles PBR objections — relevant but small caseload.
- JADE (`jade.io`) is the commercial alternative, free for read but no documented API.

### Existing Python clients
Searched PyPI and GitHub — **no first-party or community Python client** for the IP
Australia APIs (no `pyauspat`, no `atmoss-client`, etc.). `dylanhogg/legaldata` and
`gitlab.com/legalinformatics/austlii-scraper` cover AustLII generically. Academic
IPGOD work is mostly R/Stata. We would be the first credible async Python wrapper.

## Recommended v1 scope

1. **IP RAPID bulk loader** — download the weekly zip from data.gov.au, normalise to
   parquet, expose patents/trade marks/designs/PBR as queryable tables. This is the
   single biggest leverage point: one connector covers all four IP rights with weekly
   freshness and zero auth. Same pattern as our USPTO bulk-data wrapper.
2. **Australian Trade Mark Search API** — OAuth client_credentials, `quick` + `get` +
   `updated-since`. The cleanest live API and the highest-volume right type. Pairs with
   our USPTO TSDR / EUIPO trade marks coverage.
3. **Australian Patent Search API** — same shape, same auth handshake reused.

The Designs API is a fast follow once the OAuth scaffolding from §2 lands.

## Skip list

- **eServices** — filing only, no read API beyond what §1–§3 already cover.
- **PBR live database** — no REST surface; serve via IP RAPID instead.
- **IPLORD** — niche, applicant-centric; defer until a portfolio-scoring use case asks
  for it.
- **JADE.io** — no documented API; AustLII is the open path.

## Open questions

- IP RAPID file layout — is it the same ~40 IPGOD tables, or a leaner registry slice?
  (Need to fetch the dataset page; data dictionary not yet inspected.)
- Published API rate limits — the portal mentions OAuth but not numeric caps. Will need
  to confirm via the developer portal terms or by empirical testing in the sandbox.
- Whether the patent search API returns full claim/specification text or only biblio.
  AusPat UI surfaces partial full text; the API likely does too but should be verified
  against a known publication.
- Whether the trade marks API exposes goods/services class details and image URLs in
  the `get` payload, or only number-level metadata.
- AustLII APO scraping etiquette — confirm `robots.txt` and acceptable crawl delay.

## Cross-jurisdiction compare

- **vs USPTO ODP** — IP Australia's live APIs are *simpler* (two endpoints per right
  type vs ODP's deep tree) but *narrower* (no PTAB-equivalent live tribunal data — that
  lives on AustLII). OAuth client_credentials maps cleanly to our existing ODP API-key
  pattern.
- **vs EUIPO OAuth** — same OAuth 2.0 client_credentials flow, same sandbox/production
  split. EUIPO requires manual approval per app; IP Australia's portal looks
  self-service. EUIPO publishes Open Data CSV dumps; **IP Australia publishes more, more
  often, with cleaner schemas**.
- **vs KIPRIS** — KIPRIS is XML+API-key with a Korean-only filing UI. IP Australia is
  JSON+OAuth with English documentation and OpenAPI descriptions on the same portal as
  the ATO. Substantially friendlier.
- **IPGOD/IP RAPID positioning** — *much* closer to **USPTO bulk** (whole-registry
  dumps, CSV, no auth, CC-licensed) than to EUIPO Open Data (curated slices). The
  weekly cadence on IP RAPID is actually *better* than USPTO's bulk PEDS, which lags by
  weeks.

**Bottom line:** IP Australia has the cleanest small-jurisdiction IP data stack we've
surveyed — OAuth 2.0 REST APIs with OpenAPI specs, weekly bulk dumps under CC-BY, all
four IP rights from one agency, English documentation, no per-call fees, and no prior
Python competitor. This should be one of the *easiest* connectors on the roadmap.
