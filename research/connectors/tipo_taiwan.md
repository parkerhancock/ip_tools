# TIPO (Taiwan) Connector Survey

One-page scoping survey for Taiwan Intellectual Property Office sources.
Taiwan is large by filings (semiconductors, electronics, biotech) but small by
treaty integration: **not a WIPO member** (PRC objects to ROC membership),
therefore **not in the PCT, Madrid, Hague, or UPOV**. WIPO Lex carries Taiwan's
statutes under "Taiwan Province of China" — politically charged but
functionally usable. No INPADOC bridge: TW patents do *not* appear in EPO OPS
family data the way CN/KR/JP do.

The good news: TIPO has invested in open data. A real REST API exists with a
published OpenAPI/OAS spec, and a free Open Data download portal mirrors the
USPTO/EUIPO/CIPO bulk pattern. The Intellectual Property and Commercial Court
(IPCC) has a public decisions portal but no machine API.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Free tier | English | Bulk |
|---|---|---|---|---|---|---|---|
| 1 | TWPAT patent search (UI) | `twpat.tipo.gov.tw`, `twpat1.tipo.gov.tw` | None (UI / anti-proxy) | HTML/PDF | Free | Partial (TWPAT-ENG) | No |
| 2 | TWPAT-simple / TWPAT6 | `twpat-simple.tipo.gov.tw`, `twpat6.tipo.gov.tw` | None (UI) | HTML | Free | Partial | No |
| 3 | GPSS (Global Patent Search) | `gpss.tipo.gov.tw` | Free account | HTML/PDF | Free | EN UI | No |
| 4 | TIPO REST API (OpenData) | `tiponet.tipo.gov.tw/Gazette/OpenData/...` | apiKey | JSON | Free (undocumented quota) | Bib fields EN | Adjacent |
| 5 | TIPO Open Data downloads | `cloud.tipo.gov.tw/S220/opdata` | None | ZIP / XML / CSV | Free | Bib fields EN | **Yes** |
| 6 | Trademark search (text + image) | `cloud.tipo.gov.tw/S282/...` | None (UI) | HTML/PNG | Free | EN UI | No |
| 7 | Design search | via TWPAT / cloud.tipo.gov.tw | None | HTML/PDF | Free | Partial | Via #5 |
| 8 | data.gov.tw datasets | `data.gov.tw/en/datasets/...` | None | CSV / JSON | Free | Dataset-level EN | Yes (mirrors #5) |
| 9 | IP & Commercial Court decisions | `ipc.judicial.gov.tw`, `judgment.judicial.gov.tw` | None (UI) | HTML/PDF | Free | EN summaries only | No |
| 10 | Judicial Yuan law search (法學資料檢索) | `lawsearch.judicial.gov.tw` | None (UI) | HTML | Free | KO/ZH | No |
| 11 | Supreme Court IP rulings | via `judgment.judicial.gov.tw` | None | HTML/PDF | Free | EN curated only | No |
| 12 | Patent Act | `law.moj.gov.tw/ENG/.../J0070007` | None | HTML/PDF | Free | Reference EN | n/a |
| 13 | Trademark Act | `law.moj.gov.tw/ENG/.../J0070001` | None | HTML/PDF | Free | Reference EN | n/a |
| 14 | Copyright Act | `law.moj.gov.tw/ENG/.../J0070017` | None | HTML/PDF | Free | Reference EN | n/a |
| 15 | Trade Secrets Act | `law.moj.gov.tw/ENG/.../J0080028` | None | HTML/PDF | Free | Reference EN | n/a |
| 16 | Integrated Circuit Layout Protection Act | `law.moj.gov.tw/ENG/.../J0070027` | None | HTML/PDF | Free | Reference EN | n/a |
| 17 | Plant Variety and Plant Seed Act | `law.moj.gov.tw/ENG/.../M0030024` | None | HTML/PDF | Free | Reference EN | n/a |
| 18 | Patent / Trademark / Design Examination Guidelines | `tipo.gov.tw/en/...` | None | PDF | Free | Partial EN | n/a |
| 19 | Regulations for Patent Linkage of Drugs | `law.moj.gov.tw/ENG/.../L0030103` | None | HTML/PDF | Free | Reference EN | n/a |
| 20 | WIPO Lex (Taiwan Province of China) | `wipo.int/wipolex/.../members/profile/TW` | None | HTML | Free | EN | n/a |

## Per-asset detail

### 1-3. Patent search UIs (TWPAT family + GPSS)
Three browser-only front-ends. **TWPAT** (`twpat.tipo.gov.tw/tipotwoc/tipotwekm`)
is the primary register, ASP-style with an anti-proxy session-cookie gate
("TTS_AntiProxy"); legal-status counterpart at `twpat1.tipo.gov.tw/twpatc/twpatengkm`.
**TWPAT-simple** / **TWPAT6** are post-2022 simplified front-ends over the same
data. **GPSS** (`gpss.tipo.gov.tw`, launched 2018) aggregates IP5 + TIPO + 105
foreign offices; free account; useful as a *foreign* patent search from inside
Taiwan, but the TW portion overlaps TWPAT. All three are session + JS +
anti-proxy stacks in the CNIPA-hostile family; route around via the API (#4)
and bulk (#5) rather than scrape.

### 4. TIPO REST API (OpenData)
Base URL pattern: `https://tiponet.tipo.gov.tw/Gazette/OpenData/OD/OD05.aspx?QryDS=API00/...`.
OAS spec published at `DownLoadFiles/OpenData_API.json`. Auth is `apiKey`
header (per the `publicapi.dev` listing); free tier exists but the rate-limit
numerics are not documented in English. Coverage is bibliographic — patents,
trademarks, priority claims, registration numbers — *not* full-text/claims/
figures. Closest TIPO equivalent to USPTO ODP.

### 5. TIPO Open Data downloads
`cloud.tipo.gov.tw/S220/opdata` is the bulk-data portal: weekly patent / TM /
design gazettes, classification tables, applicant tables, historical biblio
dumps. ZIP-packed XML/CSV; no auth; no per-call fee. Cleanest TIPO asset and
the right anchor for v1 — same pattern as `uspto_bulkdata`, `euipo_bulkdata`,
`cipo_bulkdata`, `inpi_rpi`.

### 6. Trademark search (cloud.tipo.gov.tw/S282)
Launched March 2024 with AI image-based search at S282WV1; text search at
`OS0101.jsp`. UI-only; no documented API. Register data is reachable through
the bulk feed; skip the scrape.

### 7. Design search
Taiwan treats designs as a *category of patent* (invention, utility model,
design) under one Patent Act. Search is via the same TWPAT/cloud.tipo.gov.tw
stack; bulk design data ships through #5.

### 8. data.gov.tw
CKAN-style central portal; TIPO publishes IPC classification tables (22312),
trademark priority info (35466), TM agency listings (59717). Mirrors/
summarizes the cloud.tipo.gov.tw products; useful as a discovery layer.

### 9-11. Court decisions
The **Intellectual Property and Commercial Court** (智慧財產及商業法院, IPCC),
created 2008-07-01 (expanded to commercial cases 2021), handles civil/
criminal/administrative IP cases at first and second instance; appeals go to
the Supreme Court / Supreme Administrative Court. Decision text is published
in Chinese only at `judgment.judicial.gov.tw` and `ipc.judicial.gov.tw`. The
Judicial Yuan's 法學資料檢索系統 (`lawsearch.judicial.gov.tw`) is the master full-
text search. **No machine API.** EN coverage is limited to curated highlights
on the IPCC EN site. No Taiwan equivalent of CanLII, BAILII, or Find Case
Law (UK). Commercial **Lawsnote (七法)** has better search UX but is paywalled
and non-redistributable.

### 12-17. Statutory law (one-stop on law.moj.gov.tw/ENG)
All Taiwan IP statutes are mirrored in EN translation:
- **Patent Act** (`J0070007`) — covers invention, utility model, and design
  patents in one statute; 2022 version + 2024 Patent Linkage amendments to Art. 60-1
- **Trademark Act** (`J0070001`) — current 2023; procedural-examination
  guidelines amended effective 2025-12-01
- **Copyright Act** (`J0070017`) — 2022; TIPO is the competent agency
- **Trade Secrets Act** (`J0080028`) — Taiwan was **the second jurisdiction in
  the world (after Sweden) to enact a stand-alone trade-secrets statute**
  (1996). Criminal penalties added 2013; foreign-protection + secrecy-order
  reforms 2019; National Security Act "core key technology" overlay 2022; a
  2024-2025 draft amendment is pending in the legislature, raising criminal
  exposure to NT$10M / 5 years (NT$50M for cross-border violations). Real
  Trade Secrets *Act* (not unfair-competition tucked-in like CN AUCL or KR
  UCPA).
- **Integrated Circuit Layout Protection Act** (`J0070027`) — 1996; sui generis
  IC topography protection, registered through TIPO
- **Plant Variety and Plant Seed Act** (`M0030024`) — administered by the
  Council of Agriculture / Agriculture and Food Agency, **not TIPO**; Taiwan is
  not a UPOV member but the act is UPOV-1991 shaped

Translations are explicitly non-authoritative; Chinese text controls. Same
shape as `law.go.kr/eng` (KR) — small, static, MPEP-pattern fetcher.

### 18. Examination Guidelines
Published on `tipo.gov.tw/en/`. EN coverage is partial and lags Chinese
originals (2025-12-01 TM procedural revisions are announced in EN but the
full guideline PDF is Chinese-first). Static PDF; MPEP-pattern fetcher
applies but with smaller EN surface than KIPO or JPO.

### 19. Patent Linkage system (2019)
Implemented 2019-08-20 via amendments to the Pharmaceutical Affairs Act and
the new Article 60-1 of the Patent Act. Implementation rules ("**Regulations
for the Patent Linkage of Drugs**", `L0030103`) are published in EN. The
linkage *register* (NDA-patent submissions, Paragraph IV declarations) is
maintained by the **Taiwan Food & Drug Administration (TFDA)**, not TIPO —
notable jurisdictional split. No public API.

### 20. WIPO Lex Taiwan profile
WIPO Lex maintains a profile under "Taiwan Province of China"
(`wipolex/en/members/profile/TW`) covering the core statutes. This is the
**only WIPO-administered IP resource Taiwan appears in**: no PCT, no INPADOC,
no Madrid, no Hague, no UPOV. Politically charged labeling, functionally
usable as a fallback mirror.

## Existing Python clients

- **No Python client for TIPO patent or trademark data was found.** The
  `publicapi.dev/tipo-api` listing exists but lists no SDKs.
- `g0v/laweasyread` — community wrapper for Taiwan general legal data;
  scoped to statutes, not IP-specific.
- No `mcp_tipo`-style server exists; the connector space is open.

## Recommended v1 scope

1. **`tipo_bulkdata`** — wrap `cloud.tipo.gov.tw/S220/opdata` weekly gazette
   + applicant/IPC tables. No auth, ZIP+XML, stable schema. Mirrors
   `uspto_bulkdata` / `euipo_bulkdata` / `cipo_bulkdata` / `inpi_rpi`.
   **Highest-leverage TIPO asset by a wide margin.**
2. **`tipo_api`** — wrap `tiponet.tipo.gov.tw/Gazette/OpenData` with
   `TIPO_API_KEY` env var. Reference the bundled OAS at
   `DownLoadFiles/OpenData_API.json`. Biblio-only.
3. **`tw_statutes`** — `StaticLawCorpus` fetcher for the seven IP statutes
   on `law.moj.gov.tw/ENG` (Patent / TM / Copyright / **Trade Secrets** / IC
   Layout / Patent Linkage Regs / Plant Variety). ~1 day. Trade Secrets Act
   is the standout — most jurisdictions don't have a stand-alone statute.
4. **`tipo_guidelines`** (stretch) — static-PDF fetcher for Examination
   Guidelines (EN coverage partial).

## Skip list (v1)

- **TWPAT / TWPAT-simple / TWPAT6 scraping** — JS + anti-proxy + session
  cookies; brittle, ToS-grey. Route via #4/#5.
- **GPSS** — account-gated; TW portion overlaps #5; foreign coverage already
  via EPO OPS / Google Patents / USPTO ODP.
- **cloud.tipo.gov.tw S282 (TM image search)** — UI-only; back-end not exposed.
- **judgment.judicial.gov.tw / IPCC scraping** — no API; CN-only; Lawsnote
  paywalled and non-redistributable. Defer.
- **TFDA Patent Linkage register** — TFDA infrastructure, niche pharma; out of
  PCA scope for v1.
- **PCT / Madrid / Hague / UPOV bridges** — Taiwan is in *none*; document
  the gap, don't wrap.

## Open questions

1. **API quota numerics.** Free-tier limits and paid path are not documented
   in English. Register a key and measure empirically before launch.
2. **OAS spec completeness.** Coverage of `OpenData_API.json` relative to
   TWPAT (claims, full text, figures, file-history) is unknown — likely
   biblio-only. Confirm before scoping `tipo_api` v1.
3. **Bulk ToS for cache-and-serve.** Free-to-use, but explicit redistribution
   terms for our CoWork allowlist (`download_url` exposure) need a read.
   Same question as KIPRIS Plus.
4. **English bibliographic coverage.** TM goods/services localize via Nice;
   patent specs are almost certainly Chinese-only. Confirm before promising
   EN-only agent workflows.
5. **WIPO Lex "Taiwan Province of China" labeling.** Functionally useful;
   politically sensitive. Decide whether to remap the jurisdiction string to
   "Taiwan" in client-facing output.
6. **Trade Secrets Act amendment status.** Pin current version; watch the
   2024-2025 draft amendment. EN translation typically lags Chinese
   promulgation by months.
7. **Open court-decision substrate.** Check `g0v` projects and Judicial Yuan
   "open court data" initiatives — if a Lawsnote-equivalent open feed exists,
   it flips #9-11 from skip to in-scope.

## Cross-jurisdiction comparison

| Office | Auth | API style | Bulk | Notes |
|---|---|---|---|---|
| **TIPO** | apiKey | REST JSON + OAS | Free ZIP/XML | Closest to USPTO ODP pattern; no court API; no WIPO bridges |
| KIPRIS Plus | ServiceKey (query) | XML over REST | Paid+free | Foreigner-dev friction; richer catalog |
| EUIPO | OAuth 2.0 | JSON / OpenAPI 3 | Free XML | Modernest stack surveyed |
| IP Australia | OAuth 2.0 | JSON | CC-BY weekly | Cleanest connector on the roadmap |
| CNIPA | scrape / paid | HTML + JS + CAPTCHA | Contract-only | Hostile; route via EPO OPS |

TIPO sits between KIPO and IP Australia: real REST API and clean bulk feed
(better than CNIPA, much better than IPO India), but a closed court
substrate (worse than CanLII or Find Case Law). The Trade Secrets Act is
the most distinctive piece of substantive TW IP law and is the strongest
reason to ship `tw_statutes` even if the live connectors slip.

## Sources

- [TIPO — API Service announcement](https://www.tipo.gov.tw/en/cp-282-600217-88d54-2.html)
- [TIPO Patent & Trademark Open Data Downloads](https://cloud.tipo.gov.tw/S220/opdata)
- [TIPO OpenData API portal](https://tiponet.tipo.gov.tw/Gazette/OpenData/OD/OD05.aspx?QryDS=API00)
- [TIPO API — publicapi.dev](https://publicapi.dev/tipo-api)
- [TWPAT patent search](https://twpat.tipo.gov.tw/tipotwoc/tipotwekm)
- [TWPAT-ENG legal status](https://twpat1.tipo.gov.tw/twpatc/twpatengkm)
- [TIPO Trademark Search S282 (text + image)](https://cloud.tipo.gov.tw/S282/S282WV1/?lang=en)
- [GPSS Global Patent Search System](https://gpss.tipo.gov.tw/gpsskmc/accserver)
- [TIPO Laws & Regulations index](https://www.tipo.gov.tw/en/lp-275-2.html)
- [Patent Act (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=J0070007)
- [Trademark Act (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=J0070001)
- [Copyright Act (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=J0070017)
- [Trade Secrets Act (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=J0080028)
- [Integrated Circuit Layout Protection Act (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=J0070027)
- [Plant Variety and Plant Seed Act (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=M0030024)
- [Regulations for the Patent Linkage of Drugs (MOJ EN)](https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=L0030103)
- [Executive Yuan — Trade Secrets Act draft amendment](https://english.ey.gov.tw/Page/61BF20C3E89B856/c67fcefe-ab33-4343-8216-24120806da8c)
- [Article 60-1 patent linkage — Lee, Tsai & Partners](https://www.leetsai.com/patent/addition-of-article-60-1-to-the-patent-law-of-taiwan-to-improve-the-patent-linkage-system)
- [Intellectual Property and Commercial Court (EN)](https://ipc.judicial.gov.tw/en/mp-092.html)
- [Judicial Yuan Legal Data Retrieval System](https://lawsearch.judicial.gov.tw/)
- [Harvard — Taiwan Legal Research Guide](https://guides.library.harvard.edu/c.php?g=368710&p=2491432)
- [Globalex — Taiwan Legal Research](https://www.nyulawglobal.org/globalex/taiwan.html)
- [WIPO Lex — Taiwan Province of China profile](https://www.wipo.int/wipolex/en/members/profile/TW)
- [data.gov.tw — TM priority dataset](https://data.gov.tw/en/datasets/35466)
- [data.gov.tw — IPC dataset](https://data.gov.tw/en/datasets/22312)
- [TIPO GPSS launch (2018)](https://www.tipo.gov.tw/en/cp-282-658513-9e2ec-2.html)
- [TM Procedural Examination Guidelines (2025-12-01)](https://en.unionpatent.com.tw/taiwan-trademark-procedural-examination-guidelines-revised-and-implemented-from-december-1-2025)
- [ICLG Patents 2026 — Taiwan](https://iclg.com/practice-areas/patents-laws-and-regulations/taiwan)
- [Wikipedia — TIPO](https://en.wikipedia.org/wiki/Taiwan_Intellectual_Property_Office)
