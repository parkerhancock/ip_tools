# EUIPO Connector Survey

One-page survey of EUIPO and adjacent EU IP data sources for `patent-client-agents`.
Scope: trademarks (EUTM), Registered Community Designs (RCD), Boards of Appeal, guidelines, EUIPN cross-office aggregators, bulk data, GIs, CJEU IP case law, and EU statutory law. EPO (patents) is already covered and out of scope here.

## Cross-asset comparison

| # | Asset | Endpoint | Auth | Format | Bulk? | License |
|---|-------|----------|------|--------|-------|---------|
| 1 | EUTM Search API | `dev.euipo.europa.eu` (Trademark Search v1.0) | OAuth 2.0 / OIDC (client credentials or access code) | JSON (OpenAPI) | Yes (Open Data XML) | EUIPO ToU; free reuse |
| 2 | RCD Search / Filing API | `dev.euipo.europa.eu` (Design Search; Design Filing) | OAuth 2.0 / OIDC | JSON + binary images | Yes (Open Data XML) | EUIPO ToU |
| 3 | Boards of Appeal (eSearch Case Law) | `euipo.europa.eu/eSearchCLW/` | None (web UI) | HTML + PDF (no documented API) | No | EUIPO ToU |
| 4 | Examination Guidelines | `guidelines.euipo.europa.eu/` + `tunnel-web` PDFs | None | HTML + PDF (23 EU languages, 2025 ed.) | Yes (PDF) | EUIPO ToU |
| 5 | TMview / DesignView / TMclass / GIview | `tmdn.org`, `tmview.tmdn.org`, `tmclass.tmdn.org`, `gisearch.tmdn.org` | None for UI; **no public API** | HTML (JSON used internally) | No | EUIPN ToU |
| 6 | EUIPO Open Data Platform | `euipo.europa.eu/.../open-data` | Free registration | XML (full + partial datasets, daily) | Yes | Free reuse; PII anonymised |
| 7 | EUIPO Developer Portal | `dev.euipo.europa.eu` (+ `dev-sandbox`) | OAuth 2.0 client credentials | JSON | n/a | Plan-based quotas |
| 8 | CJEU / General Court IP rulings | `curia.europa.eu` + EUR-Lex (CELLAR) | None | HTML + PDF + RDF/XML | Yes (CELLAR SPARQL + REST) | CC reuse via Pub. Office |
| 9 | EU statutory law (2017/1001, 6/2002, 2016/943, 2024/1143) | EUR-Lex by CELEX | None | HTML / PDF / Formex / RDF | Yes (CELLAR) | Free reuse |
| 10 | EU GIs — GIview + eAmbrosia | `gisearch.tmdn.org` (GIview), `ec.europa.eu/agriculture/eambrosia` | None | HTML + CSV/XML export | Yes (data.europa.eu) | Free reuse |

---

## 1. EUTM Register / eSearch plus (Trademark Search API)

- **Endpoint:** `https://dev.euipo.europa.eu/product/trademark-search_100/api/trademark-search` (production); `https://dev-sandbox.euipo.europa.eu/` (sandbox). UI equivalent: `https://euipo.europa.eu/eSearch/`.
- **Auth:** OAuth 2.0 over OpenID Connect. Two flows — `accessCode` (3-legged, user consent) and `clientCredentials` (machine-to-machine). Register an app on the Developer Portal to obtain Client ID + Client Secret. Scopes are operation-level (e.g. trade-mark vs design).
- **Rate limits:** Per-subscription-plan quotas; over-quota returns HTTP 429. Specific numerics not published publicly — plans are negotiated/subscribed in the API Portal.
- **Format:** REST + JSON; OpenAPI 3 descriptor available (no official client libraries, but generators work).
- **Coverage:** All EUTMs from inception of the office (1996+); ~2 million live + dead marks. Returns full prosecution metadata, file inspection links, opposition flags.
- **Bulk:** Yes — XML dumps via Open Data Platform (item 6) for full register snapshots, plus partial datasets by category.
- **ToS:** EUIPO API Terms of Use; anonymisation of natural-person applicants/reps in bulk data.
- **PyPI:** No official Python client. Third-party Apify scraper exists (`apify-client`), and the WIPO CWS 12/7d memo notes EUIPO publishes only OpenAPI specs.

## 2. Registered Community Design (RCD)

- **Endpoint:** Design Search API (read) and Design Filing API (write) at `https://dev.euipo.europa.eu/product` (Designs section). UI equivalent: eSearch plus design tab.
- **Auth, format, limits:** Same OAuth 2.0/OIDC infrastructure and per-plan quotas as the EUTM API.
- **Coverage:** All RCDs since 1 April 2003 (~1.7M designs). Includes design representations (image binaries), Locarno classification, deferments, renewals.
- **Bulk:** Yes via Open Data Platform; image binaries are referenced by URL inside the XML.
- **PyPI:** None.

## 3. EUIPO Boards of Appeal — eSearch Case Law

- **Endpoint:** `https://euipo.europa.eu/eSearchCLW/`. Aggregates BoA decisions plus General Court / CJEU / national-court judgments interpreting EUTM/Design law.
- **Auth:** None — public web UI only.
- **API:** **No documented public REST API.** The 2025 "Enhancements to our search tool for case law" announcement confirms UI-only improvements (semantic features, filters); no developer endpoint surfaced. The internal JSON XHR endpoints behind the search page are undocumented and unstable — feasible to scrape but not contract-stable.
- **Format:** HTML results, PDF decisions.
- **Coverage:** BoA decisions back to 1996; CJ/GC layer; national-court layer (variable depth).
- **Bulk:** No formal bulk export; the Boards of Appeal occasionally publish themed PDF compilations.
- **PyPI:** None.

## 4. Guidelines for Examination (TM + Design)

- **Endpoint:** `https://guidelines.euipo.europa.eu/` (HTML, 2025 edition, 23 EU languages). Full PDFs under `https://euipo.europa.eu/tunnel-web/secure/webdav/guest/document_library/`.
- **Auth:** None.
- **Format:** HTML per chapter + downloadable PDF; structured by Part A/B/C/D/E + shared parts; tracked-changes PDF exists.
- **Bulk:** PDFs are direct downloads; HTML pages have stable per-chapter URLs (e.g. `/1803436` for the TM root).
- **ToS:** EUIPO content reuse policy.
- **PyPI:** None. Trivial to scrape and chunk for retrieval, analogous to the existing MPEP/TMEP wrappers in the library.

## 5. EUIPN Tools — TMview, DesignView, TMclass, GIview

- **Endpoints:** `https://www.tmdn.org/tmview/`, `https://www.tmdn.org/tmdsview-web/` (DesignView), `https://www.tmdn.org/tmclass/`, `https://www.tmdn.org/giview/`.
- **Auth:** None for the web UIs.
- **API:** **No public, documented developer API.** EUIPN provides UIs only; the internal JSON XHR endpoints can be called but carry no SLA. TMview alone aggregates ~100 M trademarks across 70+ offices; DesignView ~20 M designs.
- **Format:** HTML (JSON internally).
- **Bulk:** No.
- **PyPI:** None official.
- **Note:** For multi-jurisdiction TM coverage, scraping `tmdn.org` is the only realistic path — but contract drift risk is high.

## 6. EUIPO Open Data Platform

- **Endpoint:** `https://euipo.europa.eu/ohimportal/en/open-data` (renamed "Open Data Platform" in the 2024 relaunch).
- **Auth:** Free registration to download.
- **Format:** XML — full register snapshots plus partial datasets by slice (e.g. new filings, renewals, oppositions). Daily refresh.
- **Coverage:** Full EUTM + RCD register history.
- **Bulk:** Native bulk download is the purpose of the platform.
- **ToS:** Free reuse; data on natural persons (applicants/reps) anonymised; company/organisation data fully exposed.
- **PyPI:** None — but a thin downloader + XML parser is the obvious wrapper.

## 7. EUIPO Developer Portal

- **Endpoint:** `https://dev.euipo.europa.eu/` (production) and `https://dev-sandbox.euipo.europa.eu/` (sandbox with realistic test data).
- **Auth:** OAuth 2.0 / OIDC with two flows; per-app Client ID + Secret; scopes per operation.
- **Products catalogued:** Trademark Search, Design Search, Design Filing, plus newer offerings rolled out in the "Innovative new APIs" announcement (TMview-style image search, applicant lookups).
- **Quotas:** Plan-based; HTTP 429 on overage. Identical limits across sandbox and production for a given plan.
- **Format:** REST + JSON; OpenAPI 3 specs downloadable; no official SDKs.

## 8. CJEU / General Court IP Rulings

- **EUIPO surface:** Included in eSearch Case Law (item 3) and on `https://www.euipo.europa.eu/en/boards-of-appeal/publications/cjgc-case-law`.
- **Canonical source:** `https://curia.europa.eu/` (Curia search) + `https://eur-lex.europa.eu/` (EUR-Lex) for full text by CELEX/ECLI.
- **API:** EUR-Lex exposes the **CELLAR** semantic repository — both a SPARQL 1.1 endpoint and a RESTful content API over RDF/CDM-modelled documents. ECLI is the stable cross-court identifier. No auth; ~60-second query timeout; per-IP throttling (keep concurrency under ~5, back off on 429/503).
- **Format:** RDF/XML, HTML, PDF, Formex; JSON via content negotiation on the SPARQL endpoint (`application/sparql-results+json`).
- **Coverage:** Reported decisions from 2002 onward (and many earlier).
- **PyPI:** No mature Python client; the R package `eurlex` (CRAN) is the reference implementation — port-able to async Python.

## 9. EU Statutory Law (EUR-Lex)

Direct CELEX-addressed full text, in 24 languages, HTML/PDF/Formex/RDF:

- **EUTM Regulation 2017/1001** — `https://eur-lex.europa.eu/eli/reg/2017/1001` (consolidated `02017R1001`)
- **Design Regulation 6/2002** — `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02002R0006-20250501` (consolidated)
- **Trade Secrets Directive 2016/943** — CELEX `32016L0943`
- **GI Regulation 2024/1143** — CELEX `32024R1143`

Same CELLAR access model as item 8. Free reuse.

## 10. EU Geographical Indications — GIview + eAmbrosia (post-2024)

**Current state after Reg. 2024/1143 (in force May 2024):**

- **eAmbrosia** — `https://ec.europa.eu/agriculture/eambrosia/` — the canonical Union register for agricultural product, wine, and spirit-drink GIs. Maintained by DG AGRI historically; **administration is transferring to EUIPO** under Reg. 2024/1143. Filing intake moved to eAmbrosia online. Open dataset published at `https://data.europa.eu/data/datasets/eambrosia-eu-geographical-indications-register` (CSV/XML refreshes).
- **GIview** — `https://www.tmdn.org/giview/` — EUIPO's public-facing GI search aggregator (since Nov 2020). Covers EU-registered GIs, third-country GIs protected by treaty, and EU GIs protected abroad.
- **Craft & industrial GIs (new):** Reg. (EU) 2023/2411 created a separate EUIPO-administered system for non-agricultural GIs; the register sits on EUIPO infrastructure directly.
- **Auth/format/API:** UIs only, no documented developer API for either eAmbrosia or GIview. eAmbrosia ships a bulk CSV/XML dataset via data.europa.eu; GIview has no formal export. Free reuse.

---

## Recommended v1 scope

Wrap these three first; they give the highest data leverage per engineering hour and align with the existing patterns in `patent-client-agents`:

1. **EUTM Search API (`euipo_trademarks`)** — primary trademark client. OAuth 2.0 is a well-understood pattern, OpenAPI spec is published, and this is the natural EU counterpart to the existing USPTO TSDR/TMEP coverage. Highest user value.
2. **RCD Search API (`euipo_designs`)** — same auth, same SDK pattern; gives EU designs as a sibling to the trademark client. Low marginal cost once #1 is built.
3. **EUIPO Open Data Platform (`euipo_bulkdata`)** — XML bulk dumps for offline analytics and backfill. Mirrors the existing `uspto_bulkdata` module exactly.

Bonus light wrappers (one file each, no new auth model):

4. **Guidelines (`euipo_guidelines`)** — static HTML/PDF, mirrors the `mpep` and `tmep` modules. Easy retrieval-time win for the legal-research skill.
5. **EUR-Lex / CELLAR (`eurlex_cellar`)** — covers items 8 and 9 (CJEU rulings + statutory law) in one client. SPARQL + REST; no auth. Pure value-add for legal research, and useful far beyond EUIPO.

## Skip list (for v1)

- **eSearch Case Law / Boards of Appeal direct scrape** — no public API, undocumented XHR, decisions accessible via eSearch's overlap with CELLAR for the CJ/GC layer; the BoA-only delta isn't worth a scraper.
- **TMview / DesignView / TMclass / GIview HTML scrape** — no developer API, contract drift risk, and the underlying registers are reachable directly via each member office or via EUIPO Open Data for EU content. Revisit only if a customer specifically needs ex-EU multi-office TM coverage.
- **EUIPO Design Filing API** — write path; out of scope for a research-oriented library.
- **eAmbrosia / GIview wrappers** — small niche, currently mid-migration to EUIPO under Reg. 2024/1143; wait until the transfer settles and a developer API materialises. If needed sooner, ingest the data.europa.eu CSV dump directly.

## Open questions

- **EUIPO API quota numerics.** Subscription-plan limits are not published — only the 429 error contract. Need to register a sandbox app to read the real numbers, or contact `apiteam@euipo.europa.eu`.
- **OAuth flow choice.** `clientCredentials` is right for a server-side library, but EUIPO's docs imply some operations may be gated to `accessCode` (3-legged) only. Need to confirm which read operations work with pure machine-to-machine credentials.
- **Open Data XML schema stability.** The 2024 platform refresh changed slice definitions; need to confirm whether prior XSDs remain valid for historical snapshots.
- **eSearch Case Law internal endpoints.** Worth a one-day spike to see if the search XHR is stable enough to expose as an unofficial read-only client — only if customer demand for BoA decisions exists.
- **GI authority transfer timing.** Reg. 2024/1143 makes EUIPO the operator of the Union register, but eAmbrosia URL still resolves to `ec.europa.eu/agriculture`. Need to check whether the eAmbrosia URL/host will migrate to EUIPO infrastructure before building anything.
- **EUIPN/TMview licensing.** If the firm ever needs ex-EU TM coverage via TMview scraping, confirm whether EUIPN's ToU permits programmatic access — current docs are silent.

---

## Sources

- [EUIPO API Portal](https://dev.euipo.europa.eu/)
- [EUIPO API Portal — Security (OAuth/OIDC)](https://dev.euipo.europa.eu/security)
- [EUIPO API Portal — Trademark Search v1](https://dev.euipo.europa.eu/product/trademark-search_100/api/trademark-search)
- [EUIPO API Portal — FAQ (rate limits / 429)](https://dev.euipo.europa.eu/faq)
- [EUIPO Sandbox](https://dev-sandbox.euipo.europa.eu/product)
- [WIPO CWS/12/7d — EUIPO Web APIs](https://www.wipo.int/edocs/mdocs/cws/en/cws_12/cws_12_7d_euipo.pdf)
- [EUIPO eSearch plus](https://euipo.europa.eu/eSearch/)
- [EUIPO eSearch Case Law](https://euipo.europa.eu/eSearchCLW/)
- [EUIPO Boards of Appeal — Decisions](https://www.euipo.europa.eu/en/boards-of-appeal/decisions)
- [EUIPO Guidelines portal](https://guidelines.euipo.europa.eu/)
- [EUIPO 2025 Guidelines news](https://www.euipo.europa.eu/en/news/2025-euipo-examination-guidelines-now-available-in-23-official-eu-languages)
- [EUIPO Open Data Platform](https://euipo.europa.eu/ohimportal/en/open-data)
- [EUIPN — TMview / DesignView / TMclass / GIview](https://www.tmdn.org/)
- [EUIPO GI Hub](https://www.euipo.europa.eu/en/gi-hub)
- [eAmbrosia register](https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/)
- [data.europa.eu — eAmbrosia dataset](https://data.europa.eu/data/datasets/eambrosia-eu-geographical-indications-register)
- [EUR-Lex CELLAR SPARQL + REST](https://data.europa.eu/data/datasets/sparql-cellar-of-the-publications-office)
- [EUR-Lex ECLI help](https://eur-lex.europa.eu/content/help/eurlex-content/ecli.html)
- [Reg. 2017/1001 (EUTMR)](https://eur-lex.europa.eu/eli/reg/2017/1001)
- [Reg. 6/2002 (CDR consolidated)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02002R0006-20250501)
