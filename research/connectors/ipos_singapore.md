# IPOS Singapore — Connector Survey

Scoping survey for adding Singapore IP coverage to `patent-client-agents`. IPOS
administers all five SG IP rights (patents, trade marks, registered designs,
geographical indications, plant variety rights) from one English-language agency
and runs a modern web/mobile front door (**IP2SG** / **IPOS Digital Hub** / **IPOS
Go**). Two API surfaces with very different ToS profiles: the *transactional* IP2SG
APIs are CorpPass-gated to SG-resident entities, while the *open-data* tier on
data.gov.sg is shallow and partly stale. SG also hosts the **WIPO Arbitration and
Mediation Center Singapore office** at Maxwell Chambers (regional ADR hub).

## Cross-asset comparison

| Asset | URL | Auth | Format | Bulk? | Notes |
|---|---|---|---|---|---|
| **IP2SG transactional APIs** | `ip2sg.ipos.gov.sg/RPS/WC/API/APITokenRequest.aspx` | CorpPass + GIRO + manual approval | JSON/REST | no | Filings + renewals + ICGS lookups for TM/PT/DS; **SG-entity-gated**, not useful for our agent stack |
| **data.gov.sg "IPOS applications API"** | `data.gov.sg/collections/281/view` | none (anon) / API key for higher RL | JSON | partial | Lodgement-date queries; patents data **stale (Aug 2018–Oct 2020)**, TM data current to May 2025 |
| **data.gov.sg IPOS datasets** | `data.gov.sg/datasets?agencies=Intellectual+Property+Office+of+Singapore+(IPOS)` | none | CSV / JSON | YES | Trade-mark filings, "TMs by class", "TMs by country of applicant"; Open Data Licence (CC-BY-equivalent) |
| **IPOS Digital Hub — Basic / Advanced search** | `digitalhub.ipos.gov.sg/FAMN/eservice/IP4SG/MN_BasicSearch` | none for read | HTML (ASP.NET) | no | Public register front-end; replaced legacy IP2SG UI in June 2022 |
| **Trade Mark Similar Mark Search** | `digitalhub.ipos.gov.sg/FAMN/eservice/IP4SG/MN_TmSimilarMarkSearch` | none | HTML | no | Vienna + phonetic similarity tool |
| **TM Goods & Services (ICGS) search** | `digitalhub.ipos.gov.sg/FAMN/eservice/IP4SG/MN_TmIcgsSearch` | none | HTML | no | Nice-class + IPOS pre-approved terms list |
| **Patents / Designs basic search** | `ip2.sg/RPS/WP/CM/SearchSimpleP.aspx?SearchCategory=PT` (and `=DS`) | none | HTML | no | Legacy `ip2.sg` URL still alive alongside `digitalhub` |
| **IPOS Journals** | `digitalhub.ipos.gov.sg/FAMN/eservice/IP4SG/MN_Journals` | none | HTML / PDF | YES (weekly) | Patent and TM journals, similar shape to UKIPO/IPO India |
| **IPOS Go (mobile app)** | iOS / Google Play | personal CorpPass | native | no | Filing front-end; not a data source |
| **Singapore Statutes Online (SSO)** | `sso.agc.gov.sg` | none | HTML / PDF | no documented bulk | Canonical statutes incl. Patents Act, TMA 1998, RDA 2000, Copyright Act 2021, GIA 2014, PVPA 2004 |
| **IPOS Examination / Work Manuals** | `ipos.gov.sg/about-ip/patents/guides/` + `tm-guides/` | none | PDF (mostly chaptered) | no | Patent Examination Guidelines, Patents Formalities Manual, Trade Marks Work Manual, Designs Work Manual |
| **eLitigation** | `elitigation.sg` | free read | HTML (ASP.NET) | no | Free public docket access (Supreme Court + State Courts + SICC) |
| **LawNet** | `lawnet.sg` | paid subscription | HTML | no | Authoritative case law; subscription-gated, not viable for the agent stack |
| **WIPO Arbitration Center (SG)** | `wipo.int/amc/en/center/singapore/` | none | HTML | partial | UDRP decisions corpus already accessible via WIPO global feed |
| **ASEAN IP Portal — ASPEC** | `aseanip.org/services/asean-patent-examination-co-operation-(aspec)` | none | HTML / PDF | no | Form-based; metadata not exposed as data |
| **ASEAN PATENTSCOPE** | via `patentscope.wipo.int` (BN, KH, ID, MY, PH, TH, VN national collections) | none | HTML / XML | partial (SFTP CHF 400/yr) | SG itself **not** in ASEAN PATENTSCOPE (no national collection there) |

## Per-asset notes

**IP2SG transactional APIs.** Launched 1 Feb 2021 (TM filing/renewal/ICGS first,
then patents and designs). Auth: CorpPass + admin + GIRO + manual approval via
`APITokenRequest.aspx`. Designed for SG-resident filing agents; redistribution ToS
likely preclude cache-and-serve. Hard skip.

**data.gov.sg "IPOS applications API".** The open IPOS surface (collection 281).
Patent (`d_c49410cc1e293b0a7213a433ab612067`) and TM
(`d_56058f817dc3708f8b97e0876335ac66`) endpoints accept `lodgement_date=YYYY-MM-DD`
and return JSON `{"items": [...]}`. **Coverage gap**: patents frozen Aug 2018–Oct
2020; TM current to May 2025; no design or PVP endpoint. Rate limits: 10s buckets,
429 on overrun, tightened 1 Nov 2025; API keys lift limits.

**data.gov.sg curated datasets.** Statistical slices (TMs by class / country) plus
the TM register dump. **Singapore Open Data Licence** — perpetual, royalty-free,
commercial OK with attribution. Cleanest available path.

**IPOS Digital Hub (`digitalhub.ipos.gov.sg`).** Replaced legacy IP2SG UI on 2 Jun
2022. ASP.NET WebForms (`__VIEWSTATE`), no underlying REST. Legacy `ip2.sg` host
still alive for simple-search forms. Scraping is feasible but brittle and redundant
with data.gov.sg + journals.

**IPOS Go mobile.** World's first mobile TM-registration app (2019). Recent: TM
Classification Recommender (Jan 2024), Deadlines Tracker / Dashboard (Dec 2024
beta). Filing front-end, not data.

**SSO (`sso.agc.gov.sg`).** Canonical, free, version-controlled statute repo. All
SG IP statutes: Patents Act 1994 (formerly Cap. 221, renumbered in the 2020 Revised
Edition), TMA 1998, RDA 2000, Copyright Act 2021 (replaced 1987 Act on 21 Nov 2021),
GIA 2014, PVPA 2004 (technical exam with SFA), Layout-Designs of Integrated Circuits
Act 1999. HTML is heading-anchored — same shape as our IN/BR/MY statute mirrors.
No documented bulk export. **Trade secrets**: no statute; common law breach of
confidence + Cybersecurity Act 2018 (amended 2024) criminal overlay. Nothing to wrap.

**Examination / Work Manuals.** Patent Examination Guidelines (~4.3 MB PDF, chs 1–10;
Ch 10 = Examination Review, added 2022); Patents Formalities Manual; Trade Marks
Work Manual (chapterwise via circulars); Designs Work Manual; running Practice
Directions & Circulars. Free, English, PDF. Mirror once via `StaticLawCorpus`.

**eLitigation + LawNet.** **eLitigation** is the Judiciary's e-filing front-end
(Supreme Court — HC / CoA / SICC + State Courts), free public docket browse, same
WebForms generation as Digital Hub. **SICC** sits inside the General Division of
the HC and hears cross-border IP disputes. Substantive judgments live behind
**LawNet** subscription (~SGD 250/yr). **Free workaround**: SG Supreme Court
judgments since ~2000 are republished on **WorldLII / CommonLII** as `[YEAR] SGHC nn`
/ `[YEAR] SGCA nn`.

**WIPO Arbitration Center — SG Office.** Maxwell Chambers since May 2010.
Operational node for AP ADR; UDRP decisions are already on the global feed at
`wipo.int/amc/en/domains/decisions/`. No SG-specific corpus to wrap.

**ASPEC and ASEAN PATENTSCOPE.** ASPEC (2009) is the nine-office work-sharing
programme (BN/KH/ID/LA/MY/PH/SG/TH/VN; Myanmar excluded). **ASPEC+** launched 6 Apr
2026 with harmonised reports and committed timelines. No public ASPEC API or
metadata feed — request status sits inside each national prosecution file. **SG is
not in ASEAN PATENTSCOPE** (national collection not mirrored to WIPO; the seven
others are). Hard skip ASPEC for v1.

**Existing Python clients.** Nothing IPOS-specific on PyPI/GitHub. Generic
`datagovsg` clients don't include IPOS endpoints. First-mover.

## Recommended v1 scope

| Rank | Module | Source | Why |
|---|---|---|---|
| 1 | `sg_statutes` (static-law corpus) | `sso.agc.gov.sg` HTML mirror | Patents Act / TMA / RDA / Copyright Act 2021 / GIA / PVPA / Layout-Designs Act in one fetch; mirrors `mpep`/`tmep`/UK MoPP shape exactly. **Cheapest and highest-coverage Singapore module.** |
| 2 | `sg_manuals` | IPOS examination & work manuals (patents + TM + designs + formalities + circulars) | One GET per PDF, English, free; same `StaticLawCorpus` base as #1; complements `mpep`/`tmep` for SG agents. |
| 3 | `sg_datagovsg` | data.gov.sg IPOS APIs + curated datasets | Real open-data tier; covers TM register (current to 2025) + patent register (stale) under Singapore Open Data Licence; thin wrapper, no auth |
| 4 | `sg_journals` | IPOS Patent Journal + Trade Marks Journal weekly PDFs from Digital Hub | Predictable URLs; canonical source of *current* SG filings filling the data.gov.sg patent-API gap. Mirrors `in_journals` pattern. |
| 5 | `sg_caselaw` (stretch) | WorldLII / CommonLII SGHC + SGCA + SGIPOS hearings | Free; HTML; small volume; gives us SG IP judgments without LawNet. Validate ToS before committing. |

Use the **`StaticLawCorpus`** abstraction (`_index.md` §Cross-cutting) for #1, #2, #5.
Use **`OAuth2ClientCredentialsClient`** only if and when IPOS opens a real public
read API — not for #1–#5.

## Skip list

- **IP2SG transactional APIs** — CorpPass + GIRO + SG-entity gating; redistribution
  ToS incompatible with our stack.
- **IPOS Digital Hub HTML scraping** — ASP.NET `__VIEWSTATE`; brittle and redundant
  with data.gov.sg + journals.
- **LawNet** — paywall; use WorldLII/CommonLII instead.
- **IPOS Go mobile** — filing front-end, not data.
- **ASPEC metadata** — no public API; visibility comes through national records.
- **ASEAN PATENTSCOPE for SG** — SG isn't in that collection; use IPOS directly.
- **eLitigation scrape (v1)** — same WebForms brittleness as Digital Hub.
- **TM Similar Mark Search scrape** — proprietary scoring; not worth reproducing.

## Open questions

1. **data.gov.sg patent-API freshness** — stuck at Oct 2020; permanent break or
   pending republish? Email data.gov.sg feedback.
2. **API key tier numerics** — anonymous rate limits aren't published; register and
   benchmark.
3. **Designs/PVP on data.gov.sg** — placeholder in collection 281 but no live
   endpoint; confirm before scoping.
4. **WorldLII/CommonLII SGHC ToS** — AustLII-family scrape etiquette confirmed for
   `ip_australia`; revalidate for SGHC.
5. **IPOS Journals storage** — weekly PDFs; estimate size before deciding
   extract-and-discard vs. full mirror.
6. **SSO bulk export** — no documented path; ask AGC Legislation Division for
   XML/AKN dump of IP acts.
7. **ASPEC+ April 2026 metadata exchange** — any PCT-PPH-style XML feed worth
   tracking?

## Cross-jurisdiction compare

- **vs IP Australia** — natural sibling (English, multi-right, small register, modern
  front door) but IP Australia ships an **OAuth REST suite** (Patents/TM/Designs) +
  **IP RAPID weekly bulk** under CC-BY 2.5 AU. IPOS has *no* OAuth read API at the
  IPOS layer — only data.gov.sg slices and CorpPass-gated transactional APIs.
  IP Australia is materially ahead on open-API maturity; IPOS leads on mobile UX
  and manual quality.
- **vs EUIPO** — EUIPO has OAuth client_credentials over ~3.7M TMs + ~1.7M designs,
  OpenAPI, daily Open Data XML dumps. IPOS (~600k SG marks) has no equivalent.
  EUIPO is two tiers cleaner.
- **vs USPTO ODP** — ODP exposes full prosecution histories under a free API-key
  model. IPOS exposes no equivalent prosecution-history API; what's free is biblio
  only. Approximating ODP depth in SG would require Digital Hub HTML scraping
  per-case, which we're skipping.
- **vs IPO India** — both have mature legal corpora + access-hostile registries.
  IPOS is materially friendlier: no CAPTCHAs, a real open-data tier, English
  predictable journals (vs. 200–500 MB PDFs), ASP.NET-brittle (not CAPTCHA-gated).

**Bottom line:** Singapore is a clean "static law + manuals + thin open-data
wrapper" build, not the OAuth-suite story IP Australia gives. The legal corpus
(`sg_statutes` + `sg_manuals`) is the win — it lights up agent capability for SG
filings, prosecution arguments, ASEAN coordination, and SICC dispute work at minimal
engineering cost. The data.gov.sg tier is a real but small bonus once the patent-API
freshness gap is resolved. Skip CorpPass and the Digital Hub scrape until a paying
customer asks.
