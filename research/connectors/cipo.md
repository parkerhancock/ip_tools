# CIPO Connector Survey

Scoping survey for adding CIPO data sources to `patent-client-agents`. Canada
is a common neighbor for US practitioners (USMCA filings, common-priority
families) and CIPO is mid-modernization (Next Generation Patents / MyCIPO
Patents, Decisia for adjudicative bodies). **Headline finding: CIPO has no
public REST/JSON API for live record search.** Programmatic access today is
bulk XML/CSV through ISED IP Horizons plus HTML scraping. CanLII is the saving
grace for case law and statutes.

## Cross-asset comparison

| # | Asset | Endpoint | Auth | Format | Bulk | EN/FR | Live API? |
|---|---|---|---|---|---|---|---|
| 1 | Canadian Patents Database (CPD) | `ised-isde.canada.ca/cipo/patent-search` (was `brevets-patents.ic.gc.ca`) | None | HTML (scrape) | No live; bulk via #4 | Both | No |
| 2 | Canadian Trademarks Database | `ised-isde.canada.ca/cipo/trademark-search` | None | HTML (scrape) | Yes via #4 | Both | No |
| 3 | Industrial Designs Database | `ic.gc.ca/app/opic-cipo/id/` | None | HTML (scrape) | Yes via #4 | Both | No |
| 4 | IP Horizons (Open Data) | `ised-isde.canada.ca/.../ip-horizons-download-intellectual-property-data` | None | XML (ST.36/weekly), CSV/TXT (quarterly), PNG | **Yes** | Both | No |
| 5 | MyCIPO Patents (client portal) | `mycipo.opic-cipo.gc.ca` | GCKey/Sign-In Partner | Web UI; internal ST.96 XML | No (account-scoped) | Both | No public API |
| 6 | Practice Notices | `ised-isde.canada.ca/.../patent-notices-and-archived-web-content` | None | HTML, PDF | RSS/email only | Both | No |
| 7 | TMOB decisions | `decisions.opic-cipo.gc.ca/tmob-comc/en/` (Decisia) | None for read | HTML, PDF, RSS | RSS feed | Both | Decisia API (license) |
| 8 | Commissioner of Patents / PAB decisions | `decisions.opic-cipo.gc.ca/pab-cab/en/` (Decisia) | None for read | HTML, PDF, RSS | RSS feed | Both | Decisia API (license) |
| 9 | Patent Act P-4 | `laws-lois.justice.gc.ca/eng/acts/p-4/` | None | HTML, PDF, XML | Yes | Both | No (file URLs) |
| 10 | Trademarks Act T-13 | `laws-lois.justice.gc.ca/eng/acts/t-13/` | None | HTML, PDF, XML | Yes | Both | No |
| 11 | Industrial Design Act I-9 | `laws-lois.justice.gc.ca/eng/acts/i-9/` | None | HTML, PDF, XML | Yes | Both | No |
| 12 | Copyright Act C-42 | `laws-lois.justice.gc.ca/eng/acts/c-42/` | None | HTML, PDF, XML | Yes | Both | No |
| 13 | Plant Breeders' Rights Act | `laws-lois.justice.gc.ca/eng/acts/p-14.6/` (registry at CFIA) | None | HTML/PDF, journal | No | Both | No |
| 14 | Trade secrets (no statute) | n/a — common law / Quebec CCQ | n/a | n/a | n/a | n/a | n/a |
| 15 | MOPOP | `manuels-manuals.opic-cipo.gc.ca/w/ic/MOPOP-en` + S3 mirror | None | HTML, PDF | Single HTML file | Both | No |
| 16 | Trademarks Examination Manual | `manuels-manuals.opic-cipo.gc.ca/w/ic/TM-en` + S3 mirror | None | HTML, PDF | Single HTML file | Both | No |
| 17 | Industrial Design Office Practice (IDOP) | `manuels-manuals.opic-cipo.gc.ca/w/ic/IDOP-en` + S3 mirror | None | HTML, PDF | Single HTML file | Both | No |
| 18 | Federal Court / FCA / SCC | `decisions.fct-cf.gc.ca`, `decisions.fca-caf.gc.ca`, `decisions.scc-csc.ca` | None | HTML, PDF, RSS | RSS per court | Both | No (CanLII covers) |
| 19 | CanLII | `api.canlii.org/v1/` | API key (free, by request) | **JSON** | Yes (paged) | Both | **Yes — REST** |

## Per-asset detail

### 1. Canadian Patents Database (CPD)
~2.63M documents over 157 years. Search UI moved from `brevets-patents.ic.gc.ca`
into ISED during the 2024 NGP migration; legacy host still redirects. No
documented REST API — scrape-only. Detail pages keyed by application or patent
number expose images and full-text. Anything cached pre-2024 should be re-verified
(the migration changed several record numbers).

### 2. Canadian Trademarks Database
~1.4M marks back to 1865; active + post-1979 inactive/abandoned. Updated every
Wednesday. The `ised-isde.canada.ca/cipo/trademark-search/{appno}` detail URLs
are stable and scrape-friendly. Bulk via IP Horizons.

### 3. Industrial Designs Database
Live UI at `ic.gc.ca/app/opic-cipo/id/`. Last content update May 2026. EN/FR
bilingual term expansion built in. No API; scrape `?appNm=` keys. Bulk via
IP Horizons.

### 4. IP Horizons — the only real "API" surface
The single most useful CIPO product. Three packages:
- **Patent XML (ST.36)** — weekly; replaced Administrative-Status + Bib/Full-text
  on 2022-05-05. Combines bib + status + claims + spec into one ST.36 file.
- **Trademark XML + PNG** — weekly; 5-60 MB; adds/updates/deletes + index TXT.
- **Researcher datasets** — quarterly CSV/TXT for patents and trademarks.
  Also on `open.canada.ca` (dataset `4bf74760-7ae7-4c83-ace8-b84a3b9aea8d`).

No auth, no documented rate limits, free. Licensed under CIPO's "Terms and
conditions for use of Canadian Intellectual Property Data" — worldwide,
royalty-free, revocable; attribution required; commercial use and sub-licensing
permitted; modified records must be flagged.

### 5. MyCIPO Patents / NGP — *no public API*
Launched 2024-07-17. Salesforce on AWS, RedHat/Java stack, ST.96 XML internally,
integrates with WIPO PCT APIs. Client-facing only — GCKey/Sign-In Partner,
scoped to your own portfolio. CIPO hinted at future programmatic data exchange
at WIPO CWS-12 (ST.96 service transactions) but no public B2B endpoint catalogue
exists as of May 2026. Track this.

### 6. Practice Notices
HTML listing under `patent-notices-and-archived-web-content` (and parallel
trademarks/designs pages). Individual notices are HTML or PDF. RSS/email
subscription via Canada.ca's notices-and-updates pipeline. No API. Example:
2026-03-24 patentable-subject-matter update.

### 7-8. TMOB and Patent Appeal Board — Decisia
Both moved to Lexum's **Decisia** (TMOB earlier; ~800 bilingual PAB decisions
back to 1970 migrated by 2020-06-30; new ones within 24h). Free HTML/PDF + RSS.
Fielded search (application number, patent number, member). Decisia exposes a
**JSON API** (`decisia-demo-api.lexum.com`) but the key is Lexum-issued and
designed for the publishing org, not third-party readers. Practical path:
RSS-poll + scrape. URLs: `decisions.opic-cipo.gc.ca/{tmob-comc|pab-cab}/{en|fr}/item/{id}/index.do`.

### 9-13. Statutes (Justice Laws Website)
Patent Act P-4, Trademarks Act T-13 (legacy hyphen lives on in filenames),
Industrial Design Act I-9, Copyright Act C-42, Plant Breeders' Rights Act
P-14.6. Stable HTML, PDF, and **XML** URLs on `laws-lois.justice.gc.ca`,
refreshed ~weekly. No API; fetch and cache. CanLII (#19) carries identical
text plus point-in-time history and is JSON-addressable — prefer CanLII.
Patent Act current to 2026-03-17, amended 2025-01-01. CETA-era trademark
amendments landed 2019 (Madrid accession, single-class → Nice).

### 14. Trade secrets
No federal statute. Common-law breach of confidence (Lac Minerals v. Corona,
1989 SCC) in common-law provinces; Quebec runs on CCQ arts. 1457/1472.
Criminal Code s.391 (theft of trade secrets) added 2020. Nothing to wrap.

### 15-17. Practice manuals (MOPOP, TEM, IDOP)
All three on `manuels-manuals.opic-cipo.gc.ca` as wiki-style pages, with a
**single concatenated HTML mirror** at
`s3.ca-central-1.amazonaws.com/manuels-manuals-opic-cipo/{MOPOP_English,TEM_En,IDOP-en}.html` —
one GET pulls the whole manual. PDF mirrors exist. IDOP last updated 2025-11-12.
Parallels our MPEP ingestion.

### 18. Federal Court / FCA / Supreme Court
Decisions on lexum-powered sites with RSS (`decisions.fct-cf.gc.ca/fc-cf/decisions/en/rss.do`).
All identical content also in CanLII. Hit CanLII; treat court sites as
canonical fallback.

### 19. CanLII — the workhorse
`api.canlii.org/v1/` with a free API key (request via
`canlii.org/en/feedback/feedback.html` with scope statement). **JSON.**
Endpoints: databases, case browse/search, case metadata, citing/cited,
legislation browse/search, legislation metadata. Covers every Canadian court
and tribunal that agreed (FCA, FC, SCC, TMOB, PAB) plus all federal +
provincial statutes with consolidated point-in-time text. Rate limits not
published numerically; docs warn against high-volume scraping — keys revocable.

### 20. Madrid Protocol accession (2019-06-17)
International registrations designating Canada flow WIPO → CIPO into the
regular Trademarks Database keyed by 6-digit Madrid IRN. No separate endpoint.

### 21. Bilingual requirement
Every public output in EN + FR. Decisia and manuals expose `?lang=eng|fra` (or
`/en/`, `/fr/` path segments). Plan `lang` as a constructor argument; default
`en` with `fr` round-trip.

## Existing Python libraries

- **`canliicalls`** (PyPI), **`pycanlii`** (github.com/unhaltable/pycanlii) —
  sync, thin; useful references but neither matches our `BaseAsyncClient`.
- No mature OSS Python client for CPD / Trademarks DB / Industrial Designs DB.
  Third-party scrapers exist (Browse AI templates) but nothing production-grade.
- University of Toronto Map & Data Library distributes a CIPO Patent
  PostgreSQL Database derived from ST.36 bulk XML — confirms bulk-feed-to-DB
  is the standard ingestion pattern.

## Recommended v1 scope

1. **CanLII REST client** (`law_tools_core.canlii`). Async, free API key, JSON.
   Lights up Patent Act + Trademarks Act statutes, FC/FCA/SCC rulings, TMOB
   and PAB decisions in one client. Highest leverage per line.
2. **CIPO IP Horizons bulk client** (`cipo_bulkdata`). Mirror of `uspto_bulkdata`:
   list products, fetch a weekly XML/CSV drop, expose ST.36 parsing helpers.
   Covers patents + trademarks + designs at the bib level.
3. **CIPO practice manuals ingest** (`cipo_manuals`). Single-GET against the
   three S3 HTML mirrors (MOPOP / TEM / IDOP) with section extraction —
   mirrors our MPEP module almost exactly.

## Skip list

- **MyCIPO Patents** — account-scoped, no public API. Revisit post-NGP.
- **Decisia API** — Lexum-licensed for publishing tribunals, not readers.
  Use public Decisia HTML + RSS; let CanLII be the JSON path.
- **Live CPD / Trademarks / Designs scrapers (v1)** — viable but brittle
  mid-NGP. Defer until bulk + CanLII prove insufficient.
- **Plant Breeders' Rights registry** — niche; ~500 grants/year.
- **Trade secrets** — no statute or registry.

## Open questions

- Does the NGP roadmap include a public bibliographic REST API? CIPO's
  WIPO CWS-12 deck describes ST.96 service transactions for internal use —
  any becoming public?
- Are CPD detail pages stable post-2024 migration? DLA Piper's 2025-07
  retrospective flagged residual data-quality issues — sample randomly
  against bulk before committing.
- Does CanLII's TOS permit caching detail JSON and re-exposing via our MCP
  tool? Confirm with their feedback channel before scaling key usage.
- IP Horizons weekly drops include a "deleted" index — confirm whether our
  cache needs tombstones or whether re-applying weekly snapshots suffices.

## Compare / contrast with peer offices

- **vs USPTO ODP** — ODP is keyed REST/JSON with documented rate limits.
  CIPO is the opposite: no live API; bulk XML or scrape. CIPO's analogue
  is USPTO BDSS, not ODP.
- **vs EUIPO** — EUIPO has OAuth2 client-credentials with JSON endpoints.
  CIPO has neither auth nor JSON — one developer-tier below EUIPO.
- **vs KIPRIS Plus** — KIPRIS Plus offers ServiceKey-keyed XML with 1,000
  calls/mo free tier. CIPO has no live equivalent; parity is in bulk
  (CIPO IP Horizons free; KIPO bulk paid).
- **vs CNIPA** — both scrape live search; CIPO publishes ST.36 bulk weekly,
  whereas CNIPA's bulk is behind a partner agreement.
- **vs CanLII** — CanLII is the standout: free, keyed JSON REST covering
  every Canadian court + statute + many tribunals. More developer-friendly
  than half the patent offices on this list. Lead with it.

## References

- IP Horizons: `ised-isde.canada.ca/.../ip-horizons-download-intellectual-property-data`
- Patent XML ST.36: `.../patent-data-bibliographic-and-full-text-xml`
- CIPO data terms: `.../terms-and-conditions-use-canadian-intellectual-property-data`
- CPD: `ic.gc.ca/opic-cipo/cpd/eng/introduction.html`
- TM DB: `ised-isde.canada.ca/cipo/trademark-search/srch`
- Designs DB: `ic.gc.ca/app/opic-cipo/id/bscSrch.do?lang=eng`
- Decisia (PAB): `.../new-web-application-decisions-commissioner-patents-decisia`
- TMOB decisions: `.../trademarks-opposition-board/decisions-registrar-trademarks-...`
- Patent Act P-4: `laws-lois.justice.gc.ca/eng/acts/p-4/`
- MOPOP mirror: `s3.ca-central-1.amazonaws.com/manuels-manuals-opic-cipo/MOPOP_English.html`
- TEM: `manuels-manuals.opic-cipo.gc.ca/w/ic/TM-en`
- IDOP mirror: `manuels-manuals-opic-cipo.s3.ca-central-1.amazonaws.com/IDOP-en.html`
- CanLII API: `github.com/canlii/API_documentation/blob/master/EN.md`
- Federal Court RSS: `decisions.fct-cf.gc.ca/fc-cf/decisions/en/rss.do`
- OGL Canada 2.0: `open.canada.ca/en/open-government-licence-canada`
- NGP overview: `ised-isde.canada.ca/.../patents/next-generation-patents`
- CIPO WIPO CWS-12 (ST.96): `wipo.int/edocs/mdocs/cws/en/cws_12/cws_12_8b_cipo.pdf`
