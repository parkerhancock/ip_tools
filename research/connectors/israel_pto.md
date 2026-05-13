# Israel Patent Office (ILPO) Data Source Survey

Connector-scoping survey for `patent-client-agents`. Israel sits in the same
"small population, outsized IP footprint" cohort as IPOS and DPMA: roughly
~8,000 patent applications/year, but disproportionate weight in pharma
(Teva), semiconductors, defense electronics, cyber, and software. ILPO is a
single unit inside the Ministry of Justice running patents, designs,
trademarks, and appellations of origin/GIs; plant breeders' rights sit
separately at the Ministry of Agriculture's Plant Variety Council. Israel
is a PCT contracting state, a Madrid Protocol member (since 2010), a Hague
Agreement member (since 2020), and **an appointed ISA/IPEA since
2012-06-01** — placing ILPO in the club of ~16 offices that examine PCT
applications for the world. Legal-publishing infrastructure (Nevo, Takdin)
is well developed but commercial. English coverage of statute and the
public IP registers is good; English coverage of case law is shallow.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Bulk? | English | Feasibility |
|---|-------|-----|------|--------|-------|---------|-------------|
| 1 | ILPO Patents Search (file inspection) | `israelpatents.justice.gov.il` | None + reCAPTCHA + CSRF | Angular SPA → undocumented JSON | Per-record PDFs | Yes | Hard — modern SPA, Glassbox session capture, no documented contract |
| 2 | Trademarks Search | `trademarks.justice.gov.il` | None | ASP.NET MVC + Kendo UI | No | Yes | Medium — legacy ASP.NET, no API; data.gov.il is the proper path |
| 3 | Designs Search | `designsearch.justice.gov.il` | None | ASP.NET MVC + Kendo UI | No | Yes | Medium — ~25k registered designs; 2-year blackout after registration |
| 4 | data.gov.il Trademark dataset | `data.gov.il/dataset/...` | Free CKAN key | CSV/JSON via CKAN | Yes (weekly) | Hebrew + EN fields | **Easy — best on-ramp** |
| 5 | data.gov.il (other IP datasets) | `data.gov.il` via CKAN | Free | CSV/JSON | Yes | Mixed | Easy if datasets exist; coverage TBD |
| 6 | Patents Journal / Gazette | `israelpatents.justice.gov.il/...patents-journal` | None | HTML + per-record PDF | Per-issue | Yes | Tractable — monthly cadence, predictable structure |
| 7 | Patents Law 5727-1967 | WIPO Lex `15167` + `gov.il` | None | PDF/HTML | Yes (static) | Authoritative EN translation | **Easy** |
| 8 | Trade Marks Ordinance 5732-1972 | WIPO Lex `8200` / `15198` + `gov.il` | None | PDF | Yes (static) | EN authorized translation | **Easy** |
| 9 | Designs Law 5777-2017 | WIPO Lex `19434` | None | HTML/PDF | Yes (static) | EN | **Easy** |
| 10 | Commercial Torts Law 5759-1999 (trade secrets) | WIPO Lex `2375` | None | PDF/HTML | Yes (static) | EN | **Easy** |
| 11 | Plant Breeders' Rights Law 5733-1973 | WIPO Lex `9524` + UPOV | None | PDF | Yes (static) | EN | **Easy** |
| 12 | Copyright Act 5768-2007 | WIPO Lex `11509` | None | PDF | Yes (static) | EN | **Easy** |
| 13 | Appellations of Origin / GIs Law 5725-1965 | WIPO Lex `2373` | None | PDF | Yes (static) | EN | **Easy** |
| 14 | Patents Regs (Office Practice) 5728-1968 | WIPO Lex `19117` + JPO mirror | None | PDF | Yes (static) | EN | **Easy** |
| 15 | ILPO Patent Examination Guidelines | `gov.il/he/Departments/DynamicCollectors/work-procedure-db` | None | PDF (HE + partial EN) | Per-procedure | Partial | Medium — Hebrew-primary, EN appendices |
| 16 | TM Examination Guidelines | gov.il / ILPO TM department pages | None | PDF | Yes (static) | Partial | Medium |
| 17 | Design Examination Guidelines | gov.il / ILPO Designs department | None | PDF | Yes (static) | Partial | Medium |
| 18 | Supreme Court (Elyon) decisions | `supreme.court.gov.il` | None | HTML/PDF | No | Hebrew-primary; thin EN | Hard — Hebrew RTL, limited EN |
| 19 | Versa (Cardozo) Supreme Court translations | `versa.cardozo.yu.edu` | None | HTML | No (curated) | EN | Easy — but ~3-figure case count, IP slice smaller |
| 20 | Tel Aviv District Court (Economic Dept) | `court.gov.il` | None | HTML/PDF | No | HE only | Hard — Hebrew, weak public docket |
| 21 | Nevo | `nevo.co.il` | Subscription | HTML/PDF | No | HE primary | Hard — paywalled, scrape-hostile |
| 22 | Takdin | `takdin.co.il` | Subscription | HTML/PDF | No | HE primary | Hard — paywalled |
| 23 | PCT (IL as ISA/IPEA) | WIPO PATENTSCOPE + PCT eGuide | None | XML/JSON via WIPO | Yes via PCT bulk | EN | Already covered through `wipo_patentscope_bulk` plan |

## 1. ILPO Patents Search (`israelpatents.justice.gov.il`)

Flagship search and file-inspection portal. Modern stack — Angular SPA
served with hashed JS chunks (`main-OYASZJHU.js`, `chunk-GTWEZD3I.js`, …)
that hydrate a runtime `webApiAddress` from a server-side config endpoint.
Backend uses CSRF tokens, reCAPTCHA gates, and **Glassbox session capture**
(`isGlassboxOn`/`glassboxApplicationId`) — explicit anti-automation
telemetry. No published OpenAPI; no robots.txt allow-list; no documented
JSON contract. URL patterns observed:

- `/<lang>/search?AP_0_option=Any&AP_0_0=<appno>` — query string driven
- `/<lang>/patent-extract/<id>` — per-patent landing page
- `/<lang>/patents-journal` — gazette section
- WIPO INSPIRE reports coverage **2011→present** for events; biblio extends
  earlier via legacy data.

**Coverage:** All Israeli national patent applications + PCT national-phase
entries to IL; legal events; PDF dossier copies of selected file-wrapper
documents.

**Bulk:** None published. **Auth:** None visible, but session-bound CSRF +
reCAPTCHA + Glassbox = aggressive scraping triggers throttling. **English:**
First-class — site has full EN locale (`/en/...`).

**Python clients:** None. Searches for "Israel patent" Python clients on
GitHub return zero results.

**Recommendation:** Defer direct scraping. EPO OPS already covers IL
biblio + INPADOC legal events for the practical agent use case. Revisit
only if a paying customer needs IL file-wrapper PDFs.

## 2. Trademarks Search (`trademarks.justice.gov.il`)

Legacy ASP.NET MVC 5 + Kendo UI portal (jQuery, jqueryval, kendo bundles
visible in source). EN locale available (`?lang=en`). No documented API.
Covers all Israeli national TMs + Madrid extensions designating IL.

**The proper on-ramp is `data.gov.il`, not the live portal.** ILPO
publishes its TM register to data.gov.il (dataset 240) **weekly** with
applications + registrations data — Hebrew + English fields, CKAN-hosted.
This is the cleanest IL IP feed: free, structured, refreshed on a
predictable cadence, and explicitly licensed for research.

## 3. Designs Search (`designsearch.justice.gov.il`)

Same ASP.NET MVC + Kendo UI stack as the TM portal. Hebrew default with
EN. Searchable by proprietor, number, title, Locarno class, filing date,
priority. **~25,000 records** as of last public count (registered +
expired). EN labels for major fields; design titles often Hebrew-only.

**Coverage caveat:** New Designs Law (5777-2017, in force 2018-08-07)
introduced a **2-year blackout period** post-registration during which
designs are not public. Search hides those. Pre-2018 records sit under
the old Patents and Designs Ordinance (1924/1968).

## 4–5. data.gov.il (CKAN open-data portal)

Israel's national open data portal, CKAN-based, free API key. The
Ministry of Justice publishes the trademark register here weekly. CKAN's
standard `package_show`/`resource_show`/`datastore_search` endpoints
apply. **This is the only confirmed structured-data feed from ILPO** and
should be the spine of any IL connector.

Open question: Does ILPO publish a parallel **patents** or **designs**
dataset on data.gov.il, or is TM the only one? Worth a discovery sweep
via `package_search?q=patents` and `package_search?q=מדגמים` (designs).
If patents exist, IL becomes one of the higher-leverage non-IP5 targets;
if not, IL is statute-heavy by default.

## 6. Patents Journal (Gazette)

Monthly publication, Hebrew + English, sectioned by event type (publications,
oppositions, grants, lapsed, restored, PCT events). Browse-only via the
Angular SPA — same anti-automation surface as asset #1. Per-issue PDFs of
"Full Publications" are downloadable from within the SPA. **Coverage from
2011-present** per WIPO INSPIRE.

The journal is the canonical record of **opposition decisions and
Commissioner decisions** — Israel runs pre-grant opposition, not
post-grant, and Commissioner decisions are reported in the journal rather
than as a separate dataset. Mirrors the IPO India pattern (asset 5/22 in
that survey) but at one-tenth the data volume.

## 7–14. Substantive law — static document mirror

Israel's statute landscape is, **by a wide margin, the easiest part of
this connector**. All headline IP statutes have authoritative English
translations on WIPO Lex prepared by ILPO/Ministry of Justice and
reproduced with permission. They mirror cleanly into the planned
`StaticLawCorpus` shape from the `_index.md` cross-cutting plan.

| Statute | WIPO Lex ID | Status |
|---------|-------------|--------|
| Patents Law 5727-1967 | `15167` (consolidated 2014) + `2364` (original) | EN translation by ILPO; HE controls |
| Patents Regulations (Office Practice) 5728-1968 | `19117` (amended through 2019-01-16) | EN; key for procedure |
| Trade Marks Ordinance (New Version) 5732-1972 | `8200` (current) + `15198` (2010 baseline) | EN authorized translation; HE controls |
| Designs Law 5777-2017 | `19434` | In force 2018-08-07; replaced old Patents and Designs Ordinance |
| Commercial Torts Law 5759-1999 | `2375` | **Trade secrets statute** (Arts. 6-9) + unregistered TMs + injunctive relief; statutory damages up to NIS 100k without proof |
| Plant Breeders' Rights Law 5733-1973 | `9524` (WIPO Lex) + UPOV mirror | EN; UPOV 1991 Act member since 1998 |
| Copyright Act 5768-2007 | `11509` | EN; in force 2008-05-25; replaced UK-era 1911 Copyright Act |
| Appellations of Origin / GIs Law 5725-1965 | `2373` (amended through 2000) | EN; administered by ILPO |

Israel's Commercial Torts Law (#10) is **the unusual feature** flagged in
the scoping brief: a discrete statute combining trade-secret protection,
unregistered-mark protection, and preliminary remedies (Anton Piller-style
seizures, asset freezes) — distinct from the US/UK/CA common-law breach-of-
confidence baseline and the patchwork EU member states had pre-Directive
2016/943. Worth a dedicated row in the Tier 1+2 trade-secrets table in
`_index.md`.

## 15–17. ILPO Examination Guidelines (patents, TM, designs)

Published on the unified `gov.il` portal as a **work-procedures database**
(`work-procedure-db`) under the ILPO department pages. Mostly Hebrew with
selected EN translations of high-impact procedures (PCT national phase,
modified examination, computer-implemented inventions, antibody claims,
polymorphs). Less unified than MPEP/TMEP; closer to the DPMA pattern of
multiple per-topic circulars. Format is PDF.

**Feasibility:** Mirror-once is tractable for the EN-available subset.
Full Hebrew corpus is a translation problem rather than a scraping
problem — defer until clear demand.

## 18–20. Courts

Israeli courts function on a three-tier model: Magistrate, District,
Supreme. IP first-instance jurisdiction is **District Court**, with the
**Tel Aviv District Court Economic Department** (established 2010 under
the Courts Law amendment) hearing the bulk of patent and TM litigation.
Patent oppositions go to the Commissioner first, then to District Court.
The **Supreme Court** (Beit HaMishpat HaElyon) sits as the final IP
appellate court — there is no specialized IP court of appeals (unlike CAFC
or the UPC).

The judiciary's public portal at `supreme.court.gov.il` and `court.gov.il`
publishes selected decisions in Hebrew; English translations exist only
for high-profile cases. There is no documented API. Hebrew RTL parsing
adds friction over and above the access problem.

The **Versa project at Cardozo Law School** (`versa.cardozo.yu.edu`)
hosts ~700 curated English translations of Israeli Supreme Court
decisions across all subject areas, with topic-tag pages for `trademarks`,
`copyright`, `intellectual property`. It is the only practical EN entry
point to Israeli Supreme Court IP case law. Static HTML; trivial to
mirror; coverage is curated rather than comprehensive.

## 21–22. Nevo and Takdin

Israel's two major commercial legal-research databases. **Nevo Publishing
Ltd.** has published all court decisions since 1997; **Takdin** hosts
~600k cases plus statutes with a limited English Supreme Court subset.
Both are subscription, both are scrape-hostile, both are how Israeli
attorneys actually access case law. Pricing is per-seat law-firm pricing
(roughly comparable to Lexis/Westlaw national-edition pricing — i.e., not
on our budget for v1).

## 23. PCT — Israel as ISA/IPEA

Since **2012-06-01**, ILPO acts as an International Searching Authority
and International Preliminary Examining Authority for PCT applicants
from Israel, the US (limited), Georgia, Ukraine, and a few smaller
jurisdictions. ISA fees are reduced 70% for inventors / academic
institutions, 90% for students/pensioners. This matters for IL agent
work because **ILPO-issued international search reports (ISRs) and
written opinions appear in WIPO PATENTSCOPE under the standard PCT
event flow** — they're not in a separate IL feed. Coverage rides on
the existing Tier 1 `wipo_patentscope_bulk` plan.

## Recommended v1 scope

ILPO maps cleanly onto the same play as IPO India and INPI Brazil: **lean
on static law mirroring + one well-defined live feed; skip the brittle
SPA/ASP.NET register scrapes**.

1. **`israel_statutes`** — Patents Law + Patent Regs + TM Ordinance +
   Designs Law + Commercial Torts Law + Plant Breeders' Rights Law +
   Copyright Act + Appellations of Origin Law, mirrored once from WIPO
   Lex into the planned `StaticLawCorpus` shape. Highest ROI: 8 statutes,
   all in authoritative EN, zero auth, no CAPTCHA. The Commercial Torts
   Law slots into the trade-secrets row of `_index.md` (statutory trade
   secrets — a feature, not a hack, in Israeli law).
2. **`israel_data_gov_il`** — thin CKAN wrapper around the data.gov.il
   ILPO trademark dataset (weekly refresh). Confirm whether a patents or
   designs dataset exists alongside; if so, fold them in. Builds on
   existing `httpx + hishel` scaffolding.
3. **`israel_examination_guidelines`** (stretch) — mirror the EN subset
   of ILPO work-procedures from `gov.il/he/Departments/DynamicCollectors/
   work-procedure-db`. Format = PDFs; structure is per-procedure, not
   chapter-by-chapter like MPEP. Acceptable as a flat searchable index.
4. **`versa_supreme_court`** (stretch) — Cardozo Versa scrape for the EN
   Supreme Court IP slice. Small (~700 total cases, IP slice smaller),
   static HTML, public-mission project. Doubles as **a precedent for any
   future Versa/Cardozo-style curated-translation source** in other
   jurisdictions.
5. **Wire IL into existing `epo_ops`** — confirm that `get_il_biblio`
   and `get_il_legal_events` work the way `get_cn_biblio` is planned to;
   if so, IL biblio coverage rides for free on the EPO OPS backbone we
   already have built. No new module needed.

## Skip list

- **ILPO Patents Search SPA (live scrape)** — modern Angular SPA with
  reCAPTCHA + Glassbox + CSRF + runtime-configured webApiAddress; no
  documented JSON contract. Hostile-to-automation telemetry stack.
  Coverage of biblio is duplicated by EPO OPS INPADOC; file-wrapper PDFs
  are the only unique value, and demand is too thin to justify the build.
- **Trademarks register scrape** — when data.gov.il publishes the
  register weekly with structured Hebrew + EN fields, scraping the live
  ASP.NET/Kendo portal is dominated.
- **Designs register scrape** — small dataset (~25k), 2-year blackout
  reduces utility further, no API. Hague Express (planned in Tier 1)
  picks up the post-2020 Hague-routed slice.
- **Patents Journal as a separate ingest** — covered by EPO OPS legal
  events for most agent use cases; would otherwise require monthly PDF
  extraction inside the SPA-gated portal.
- **Nevo / Takdin** — subscription, scrape-hostile, no negotiated
  data feed at our budget.
- **Tel Aviv District Court direct scrape** — Hebrew RTL, no public
  docket API, fragmented across `court.gov.il` subsystems.
- **Supreme Court Hebrew corpus** — same Hebrew problem; defer to Versa
  EN curation.

## Open questions

1. **data.gov.il IP dataset inventory.** Does ILPO publish patents and/or
   designs alongside the confirmed TM dataset? Run `package_search` against
   `data.gov.il` API for `patents`, `מדגמים`, `סימני מסחר` to enumerate.
2. **data.gov.il TM dataset field schema.** Hebrew + EN parallel fields,
   or Hebrew-primary with translated subset? Affects whether the connector
   exposes EN-only or bilingual.
3. **EPO OPS IL coverage depth.** Confirm INPADOC legal-event timeliness
   for IL (typical lag vs. live ILPO register). Likely 2-6 weeks, but
   worth measuring before claiming biblio coverage.
4. **Versa Cardozo licensing.** Public-mission translation project — confirm
   redistribution under our CoWork cache-and-serve model is permitted.
5. **ILPO examination guidelines EN coverage ratio.** What fraction of
   work-procedures are translated to EN? If <20%, the mirror is a stub;
   if >50%, it's worth a proper MPEP-shape index.
6. **Israeli Hague designations.** Post-2020, IL is a Hague member. Are
   IL design designations in the Hague Express feed surfaced through the
   planned `wipo_hague_express` Tier 1 module? Confirm before deciding
   whether `israel_designs` needs anything beyond the statute mirror.
7. **Commercial Torts Law placement.** Trade secrets in `_index.md`'s
   sweep is currently statute-grouped by jurisdiction. Israel's Commercial
   Torts Law combines trade secrets **plus** unregistered TMs **plus**
   procedural remedies — should it sit in the trade-secrets row, the TM
   row, or both?

## Comparison with KIPRIS, IPOS, DPMA

| Dimension | ILPO | KIPRIS (KR) | IPOS (SG) | DPMA (DE) |
|---|---|---|---|---|
| Modern REST API for register | **No** — Angular SPA + undocumented JSON | Yes — KIPRIS Plus (XML over ServiceKey) | Partial — IPOS Open Dossier + SG IP Online | DPMAconnectPlus (paid, €200 + contract) |
| Bulk data feed | data.gov.il TM weekly (free CKAN) | KIPRIS Plus 46 services × 126 products | IPOS Open Dossier docs API | Paid backfile XML only |
| English statute corpus | **Excellent** — 8 authoritative WIPO Lex translations | Excellent — law.go.kr/eng | Excellent — Singapore Statutes Online | Good — gesetze-im-internet.de + DPMA Language Service |
| Examination guidelines (EN) | Partial — per-procedure PDFs | Yes — KIPO patent / TM examination guidelines EN | Yes — IPOS examination guidelines fully EN | Partial — DPMA circulars, EN selectively |
| Case law access | Versa (curated ~700) + paywalled Nevo/Takdin | Patent Court of Korea + KIPRIS decisions EN | Singapore Judiciary website (free, EN, indexed) | rechtsprechung-im-internet.de XML + Zenodo BPatG |
| Trade-secrets statute | **Yes — Commercial Torts Law 5759-1999** | Yes — UCPA | No (common-law equity) | Yes — GeschGehG 2019 |
| PCT ISA/IPEA status | **Yes (since 2012)** | Yes | No | Yes (via EPO) |
| Anti-automation friction | High (reCAPTCHA + Glassbox + CSRF on register) | Low–medium (ServiceKey gating, foreign-dev path unclear) | Low | Medium (contract paperwork, not technical) |
| **v1 cost** | **Low — statute mirror + CKAN wrapper covers 80%** | Medium — ServiceKey ToS unclear | Medium — multiple APIs to wire | High — paid contract |
| **v1 ceiling** | Medium — register scrape is the gap, EPO OPS narrows it | High — KIPRIS Plus covers nearly everything | High — IPOS API + EN courts | Medium — utility models the unique slice |

**Verdict:** Israel is closer to **IPOS** in statute and English coverage,
closer to **IPO India** in live-register accessibility (modern SPA in
IL's case vs. CAPTCHA-ASP.NET in IN's case — different stacks, same
"scrape-only" outcome), and closer to **DPMA** in structural complexity
(separate trade-secrets statute, fragmented court system, commercial
legal-research market). The right v1 is **statute-heavy, register-light**:
ship the 8-statute mirror + CKAN TM feed + EPO OPS IL helpers in one
sprint, and skip the SPA scrape entirely.

## Sources

- ILPO portals: [About ILPO (gov.il)](https://www.gov.il/en/departments/ilpo) · [Patents Search](https://israelpatents.justice.gov.il/) · [Trademarks Search](https://trademarks.justice.gov.il/) · [Designs Search](https://designsearch.justice.gov.il/) · [TM Online Services](https://www.gov.il/en/departments/general/tm-online-services) · [Ministry of Justice — Search Databases](https://www.justice.gov.il/En/Units/ILPO/Departments/Patents/Guides/Pages/SearchDatabases.aspx)
- WIPO INSPIRE IL register page: [`inspire.wipo.int/system/files/juri/il.pdf`](https://inspire.wipo.int/system/files/juri/il.pdf)
- Statutes (WIPO Lex): [Patents Law 5727-1967](https://www.wipo.int/wipolex/en/legislation/details/15167) ([PDF](https://www.wipo.int/edocs/lexdocs/laws/en/il/il040en.pdf)) · [Patents Regs 5728-1968](https://www.wipo.int/wipolex/en/legislation/details/19117) · [Trade Marks Ordinance 5732-1972 (current)](https://www.wipo.int/wipolex/en/legislation/details/8200) · [TM Ordinance 2010 baseline](https://www.wipo.int/wipolex/en/legislation/details/15198) · [Designs Law 5777-2017](https://www.wipo.int/wipolex/en/legislation/details/19434) · [Commercial Torts Law 5759-1999](https://www.wipo.int/wipolex/en/legislation/details/2375) ([PDF](https://wipolex-res.wipo.int/edocs/lexdocs/laws/en/il/il012en.pdf)) · [Plant Breeders' Rights Law 5733-1973](https://www.wipo.int/wipolex/en/legislation/details/9524) · [Copyright Act 5768-2007](https://www.wipo.int/wipolex/en/legislation/details/11509) · [Appellations of Origin / GIs 5725-1965](https://www.wipo.int/wipolex/en/legislation/details/2373)
- Mirrors of statutes for redundancy: [TM Ordinance on gov.il (PDF)](https://www.gov.il/BlobFolder/legalinfo/tm-law/en/New%20Trade%20Marks%20Ordinance-Israel.pdf) · [JPO mirror of Patent Regs](https://www.jpo.go.jp/e/system/laws/gaikoku/document/index/israel-e_tokkyo_kisoku.pdf) · [JPO mirror of Patents Law](https://www.jpo.go.jp/e/system/laws/gaikoku/document/index/israel-e_tokkyo.pdf) · [UPOV mirror of PBR Law](https://www.upov.int/export/sites/upov/members/en/npvlaws/israel/israel1997.pdf)
- Examination guidelines hub: [gov.il work-procedures DB](https://www.gov.il/he/Departments/DynamicCollectors/work-procedure-db?skip=0) · [Modified Examination Procedures (PDF, 2024)](https://rcip.co.il/wp-content/uploads/2009/02/Modified-Examination-Procedures-at-the-Israel-Patent-Office-2024-2.pdf) · [Patent Examination Guidelines summary (IP-TA)](https://ip-ta.com/en/new-examination-guidelines-for-the-israel-patent-office-2021/) · [The Patent Prosecution Review 2026 — Israel](https://www.iam-media.com/review/the-patent-prosecution-review/2026/article/israel-essential-updates-national-prosecution-processes)
- PCT as ISA/IPEA: [PCT eGuide IL](https://pctlegal.wipo.int/eGuide/view-doc.xhtml?doc-code=IL&doc-lang=en) · [USPTO notice on ILPO ISA/IPEA](https://www.uspto.gov/sites/default/files/patents/law/notices/ilpo_isa-ipea.pdf) · [Glazberg briefing on ILPO as ISA](https://www.ga-adv.com/israel-patent-office-serves-isa) · [ISA / IPEA Agreements (WIPO)](https://www.wipo.int/en/web/pct-system/access/isa_ipea_agreements)
- Open data: [data.gov.il portal](https://www.gov.il/en/departments/data_gov_il/govil-landing-page) · [Trademark dataset 240](http://www.data.gov.il/dataset/240) · [data.gov.il CKAN extensions on GitHub](https://github.com/gov-il/datagovil-ckanext) · [Awesome-MCP data.gov.il](https://mcpservers.org/servers/DavidOsherProceed/data-gov-il-mcp)
- Courts and case law: [Supreme Court of Israel](https://supreme.court.gov.il/sites/en/Pages/home.aspx) · [Versa — Cardozo Israeli Supreme Court Project (IP topic)](https://versa.cardozo.yu.edu/topics/intellectual-property) · [Versa Trademarks](https://versa.cardozo.yu.edu/topics/trademarks) · [Globalex — Israeli legal research](https://www.nyulawglobal.org/globalex/Israel1.html) · [Bluebook T2.22 Israel](https://www.legalbluebook.com/bluebook/v21/tables/t2-foreign-jurisdictions/t2-22-israel) · [Tel Aviv University Israeli Legal Databases guide](https://en-lawlib.tau.ac.il/israeli_databases) · [Takdin Princeton libguide](https://libguides.princeton.edu/az/takdin-israel-law-database)
- Trade secrets background: [Lexology — Protection of trade secrets in Israel](https://www.lexology.com/library/detail.aspx?g=359aa4ae-b630-4c43-8021-032e9f32c537) · [DWO — Trade Secrets Law in Israel](https://dwo.co.il/introduction-to-trade-secrets-law-in-israel/) · [Reinhold Cohn — Trade Secrets](https://rcip.co.il/service/trade-secrets/)
- Practice background: [Pearl Cohen — Israel Patent Office](https://www.pearlcohen.com/practice/israel-patent-office/) · [IPAA — Patent Office](https://www.ipaa.org.il/il-patent-office/) · [Reinhold Cohn — Israel IP Laws](https://rcip.co.il/useful-information/israel-ip-laws/) · [Chambers — Trade Marks & Copyright 2025 Israel](https://practiceguides.chambers.com/practice-guides/trade-marks-copyright-2025/israel) · [Library of Congress — Israel: New Law Regulating Designs](https://www.loc.gov/item/global-legal-monitor/2017-10-05/israel-new-law-regulating-designs)
- Wikipedia: [Israel Patent Office](https://en.wikipedia.org/wiki/Israel_Patent_Office) · [Supreme Court of Israel](https://en.wikipedia.org/wiki/Supreme_Court_of_Israel) · [Judiciary of Israel](https://en.wikipedia.org/wiki/Judiciary_of_Israel)
