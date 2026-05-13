# IPO India (CGPDTM) Data Source Survey

Connector-scoping survey for `patent-client-agents`. India is the world's sixth-largest patent jurisdiction by filings and a top-three trademark jurisdiction, with disproportionate weight in pharmaceuticals (Section 3(d) anti-evergreening, Section 84 compulsory licensing) and FMCG branding. It is also famously the **least machine-readable major IP jurisdiction**: nearly everything is HTML-with-CAPTCHA or PDF-only, no documented REST contracts, and bulk feeds are practically non-existent. The Controller General of Patents, Designs and Trade Marks (CGPDTM) runs patents, designs, trademarks; the GI Registry sits separately in Chennai under the same umbrella. Plant variety rights are administered by the PPV&FR Authority under MoA&FW.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Bulk? | Feasibility |
|---|-------|-----|------|--------|-------|-------------|
| 1 | InPASS — patent advanced search | iprsearch.ipindia.gov.in/PublicSearch | None + CAPTCHA | HTML scrape | No | Hard — CAPTCHA per session, ASP.NET viewstate |
| 2 | TM Public Search | tmrsearch.ipindia.gov.in/tmrpublicsearch / tmsearch.ipindia.gov.in | None + CAPTCHA | HTML scrape | No | Hard — JS-rendered, new AI image-search portal in Oracle APEX |
| 3 | Designs Public Search + E-Register | search.ipindia.gov.in/designsearch | None + CAPTCHA | HTML scrape | No | Hard — gaps for 2005/2006/2008; "not valid for legal proceedings" disclaimer |
| 4 | GI Registry public search | search.ipindia.gov.in/GIRPublic | None + CAPTCHA | HTML scrape | No | Tractable — small dataset (~700 records) |
| 5 | Patent Office Journal (weekly) | ipindia.gov.in/journal-patents.htm | None | PDF (200–500MB/issue) | Per-issue | Tractable — predictable URL pattern, but huge PDFs |
| 6 | Trade Marks Journal (weekly) | ipindia.gov.in/ipr/TMR_journal | None | PDF | Per-issue | Tractable — same pattern |
| 7 | data.gov.in patent / TM datasets | data.gov.in/resource/weekly-patent-application-published | API key (free) | CSV / JSON / XML | Yes (limited) | Easy — but coverage is shallow |
| 8 | Form 27 working statements | iprsearch.ipindia.gov.in (per-patent E-Register) | None + CAPTCHA | PDF attachments | No | Hard — buried in per-patent record; no index |
| 9–19 | Statutes / Rules / MPPP | indiacode.nic.in, ipindia.gov.in/writereaddata, WIPO Lex | None | PDF | Yes (static) | Easy — mirror once |
| 20 | Delhi HC IPD judgments | delhihighcourt.nic.in/web/judgement/fetch-data | None + CAPTCHA | HTML + PDF | No | Tractable — structured docket, free-text search |
| 21 | Supreme Court judgments | sci.gov.in, judgments.ecourts.gov.in | None | HTML + PDF | No | Tractable — covered by `legal-research` |
| 22 | Controller decisions | Published in Patent Office Journal (asset 5) | None | PDF | Per-issue | Hard — extraction problem inside journal PDFs |

## 1. InPASS — Indian Patent Advanced Search System

Flagship patent search launched February 2015. Four tabs: Patent Search, Patent E-Register, Application Status, Help. Supports wildcards, truncation, boolean operators, full-text search of granted patents and pre-grant publications.

- **URL:** `https://iprsearch.ipindia.gov.in/PublicSearch/` (historical: `ipindiaservices.gov.in/PublicSearch`)
- **Auth:** None, but every search and every E-Register/status fetch requires solving an image CAPTCHA. ASP.NET WebForms with `__VIEWSTATE`/`__EVENTVALIDATION` — session-stateful.
- **Rate limits:** No documented quota. Aggressive scraping triggers IP blocks and JCAPTCHA escalation. Site is frequently down (multi-hour outages monthly).
- **Format:** HTML scrape only. No JSON. PDF attachments for granted specifications, claims, drawings via separate links.
- **Coverage:** Indian patent applications from ~1995 forward; full-text only for post-2005 publications. Pre-2005 records have biblio only.
- **Bulk:** None.
- **ToS:** Public data; "information not valid for legal proceedings" disclaimer.
- **Python clients:** No serious maintained library on PyPI. A handful of GitHub repos exist (most archived, none with CAPTCHA-solving). Commercial services (PatSeer, Relecura, Questel Orbit) license bulk Indian data via undisclosed channels — they likely have InPASS scrapers plus journal ingest.

## 2. Trade Marks Public Search

Two coexisting portals as of 2026:

- **Legacy:** `https://tmrsearch.ipindia.gov.in/tmrpublicsearch/` (also exposed as `/eregister/`). Wordmark, Vienna code, phonetic search.
- **New DPIIT TM Search (2024–2026):** `https://tmsearch.ipindia.gov.in/ords/r/tisa/trademark_search/dpiit-public-search` — Oracle APEX app, AI-powered image search, accepts JPEG/PNG uploads for similarity.

- **Auth:** None, CAPTCHA per session. The Oracle APEX app uses APEX session tokens; the legacy app uses ASP.NET viewstate.
- **Rate limits:** Undocumented; sessions expire fast. The new APEX backend has been observed to 503 under modest load.
- **Format:** HTML; PDF for original/amended specimen sheets; PNG for marks.
- **Coverage:** All Indian TM applications/registrations + Madrid extensions designating India.
- **Bulk:** None public. Marcaria, Corsearch, CompuMark mirror via licensed scrapers / undisclosed feeds.
- **Python clients:** None usable. `legaldev.in`, `quickcompany.in`, `tmwala.com` are user-facing reskins, not libraries.

## 3. Designs Public Search

- **URL:** `https://search.ipindia.gov.in/designsearch` (search) and `https://search.ipindia.gov.in/DesignApplicationStatus/DesignEregister/index` (E-Register).
- **Auth:** None + CAPTCHA.
- **Coverage:** Search from April 1997 onward **except 2005, 2006, 2008** (gap noted on site). E-Register only for applications filed on or after **2009-04-01**.
- **Format:** HTML; design representations as low-res JPG.
- **Bulk:** None. The Hague Express on WIPO is a partial alternative for designs with WIPO designation (rare for IN).
- **Quality flag:** Site itself warns "information is dynamically retrieved and is under testing, therefore the information retrieved by this system is not valid for any legal proceedings under the Designs Act, 2000." Use only as an index, not authority.

## 4. GI Registry (Chennai)

Geographical Indications Registry, separate office in Chennai under CGPDTM. India is a strong GI jurisdiction (Darjeeling Tea, Basmati Rice contest, Kanjeevaram silk, etc.).

- **URL:** `https://search.ipindia.gov.in/GIRPublic/` (public search) + `https://ipindia.gov.in/gi.htm` (registry homepage) + `https://ipindia.gov.in/registered-gls.htm` (registered list).
- **Auth:** None + CAPTCHA on detail views.
- **Coverage:** ~605 registered GIs (Q1 2026); ~1,000 applications total. UP leads with 74, Tamil Nadu 69. Renewable 10-year terms.
- **Format:** HTML + PDF specifications. The static "registered GIs" page is a clean HTML table — easy to mirror.
- **Bulk:** Static list is effectively bulk; one HTML scrape gets the catalog.
- **Quality:** This is the easiest IPO India asset. Small dataset, mostly static, low CAPTCHA friction on the static list.

## 5–6. Patent Office Journal and Trade Marks Journal

Weekly PDF gazettes — the only **complete** official record of office activity. Every grant, every TM advertisement, every controller decision, every Form 27 acknowledgment cascades through these.

- **URL:**
  - Patent Journal: `https://ipindia.gov.in/journal-patents.htm` (current); `https://search.ipindia.gov.in/IPOJournal/Journal/Patent` (search across issues); `https://ipindia.gov.in/ipr/patent/journal_archieve/journal_YYYY/` (annual archive pages back to 2010).
  - TM Journal: `https://ipindia.gov.in/ipr/TMR_journal/index.htm`, `https://search.ipindia.gov.in/IPOJournal/Journal/Trademark`.
- **Auth:** None.
- **Format:** PDF, typically 200–500MB per weekly issue (TM journal often 3–5GB when image-heavy).
- **Coverage:** Patent Journal weekly since 2005-ish; TM Journal weekly since the 1999 Act took effect.
- **Bulk:** Per-issue direct links — scriptable. Predictable filename pattern by date / issue number.
- **Extraction:** Native PDF text layer is present (no OCR needed for patent journal). TM journal mixes text and embedded images.
- **Quality flag:** This is the canonical source for **Controller decisions** (asset 22). Decisions are not separately indexed — they live as sections inside each weekly journal.

## 7. data.gov.in (OGD Platform)

India's Open Government Data portal hosts a handful of IP datasets:

- **URL:** `https://www.data.gov.in/resource/weekly-patent-application-published` and a Patent/TM statistics dashboard launched 2024.
- **Auth:** Free API key (NIC OGD), included in URL.
- **Format:** CSV / JSON / XML via Resource API.
- **Coverage:** Shallow — weekly patent application titles, applicant names, agg statistics. Not full bibliographic data, no claims, no abstracts. Not a substitute for InPASS.
- **Bulk:** Yes, but coverage is the limiting factor, not access.
- **Use case:** Filing-trend dashboards, not record retrieval.

## 8. Form 27 — Working Statements

India is the only major jurisdiction requiring patentees to disclose commercial working. The **Patents (Amendment) Rules, 2024 (effective 2024-03-15)** changed the cadence from annual to **every three financial years** and dropped the licensee-disclosure requirement. Penalty for non-filing: fine up to INR 10 lakh under Section 122.

- **URL:** No standalone Form 27 register. Filed Form 27s appear as PDF attachments inside each patent's E-Register record on InPASS.
- **Coverage:** Mandatory for all granted Indian patents post-grant. Compliance is uneven; many patentees file nil-working statements.
- **Format:** Per-patent PDF in InPASS E-Register, behind CAPTCHA.
- **Bulk:** None. There is no Form 27 dataset, no aggregate dashboard.
- **Quality flag:** Form 27 is the most-requested-and-least-accessible IPO India data point — pharma analysts, generics manufacturers, and access-to-medicines researchers (MSF, Access IBSA) all want it. Several academic projects have hand-compiled subsets; none current or comprehensive.

## 9–19. Substantive law and procedural manuals

All available as static PDFs; mirror once, expose like MPEP/TMEP. Update cadence ranges from "never" (1957 Copyright Act core, though amended) to "every few years" (Patents Rules).

| # | Instrument | Best source | Format | Notes |
|---|-----------|-------------|--------|-------|
| 9 | Patents Act, 1970 (incorporating amendments through 2024-08-01) | `ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf`; indiacode.nic.in | PDF | Section 3(d), 84, 25(1), 8 are the headline provisions |
| 10 | Trade Marks Act, 1999 | indiacode.nic.in; WIPO Lex | PDF | |
| 11 | Designs Act, 2000 + Designs Rules, 2001 | indiacode.nic.in; WIPO Lex | PDF | |
| 12 | GI of Goods (Registration and Protection) Act, 1999 + GI Rules, 2002 | indiacode.nic.in | PDF | |
| 13 | Copyright Act, 1957 (last amended 2012) | indiacode.nic.in; copyright.gov.in | PDF | |
| 14 | PPV&FR Act, 2001 + PPV&FR Rules, 2003 | indiacode.nic.in/A2001-53.pdf; plantauthority.gov.in | PDF | Administered separately by PPV&FRA |
| 15 | Trade Secrets — **no statute**; Protection of Trade Secrets Bill, 2024 pending | 22nd Law Commission Report (2024-03); bill text on PRSIndia | PDF | Common-law breach of confidence + contract is current law |
| 16 | Patents Rules, 2003 + Patents (Amendment) Rules, 2024 + Patents (Second Amendment) Rules, 2024 | ipindia.gov.in/rules-patents.htm | PDF | Major procedural overhaul |
| 17 | Trade Marks Rules, 2017 | ipindia.gov.in | PDF | |
| 18 | Manual of Patent Office Practice and Procedure (MPPP), v3.0 (2019; updates pending) | `ipindia.gov.in/frontend/pdf/patents/Manual_for_Patent_Office_Practice_and_Procedure_.pdf`; WIPO Lex `legislation/details/7648` | PDF | India's MPEP equivalent — ~400 pages, well-structured |
| 19 | Trade Marks Manual, Designs Manual | ipindia.gov.in/IPOGuidelinesManuals/ | PDF | Less comprehensive than MPPP; section/article numbering is consistent enough to chunk MPEP-style |

## 20–22. Tribunals and courts

**IPAB abolished** by the Tribunals Reforms Act, 2021 (notified 2021-04-04 ordinance, enacted 2021-08). IP appeals now flow to High Courts.

- **Delhi HC IP Division** (asset 20): Set up 2021-07-07, IPD Rules 2022 notified 2022-02-24. Inherited ~3,000 pending IPAB matters. Original + appellate + revisional + writ jurisdiction over IP. Public docket at `https://delhihighcourt.nic.in/web/judgement/fetch-data`; case status at `https://delhihighcourt.nic.in/`. PDF judgments, structured metadata (case number, parties, date, bench). Reliable, frequently updated, comparatively scrape-friendly (no CAPTCHA on docket index; CAPTCHA on full-text fetch for some flows). The 2022-23 IPD Annual Report is published as a PDF.
- **Madras / Bombay / Calcutta High Courts:** No dedicated IPD yet (proposals tabled). IP cases are scattered through the commercial division docket on each HC's e-courts portal.
- **National e-Courts services** (`https://hcservices.ecourts.gov.in/`, `https://judgments.ecourts.gov.in/`): unified search across HCs and the Supreme Court. CAPTCHA-gated but free-text searchable. This is the right entry point for cross-HC IP search.
- **Supreme Court** (asset 21): `https://www.sci.gov.in/` and judgments.ecourts.gov.in. Already feasible via the `legal-research` skill's court connectors.
- **Controller decisions** (asset 22): No standalone publication. Decisions appear as text sections inside the weekly Patent Office Journal PDFs. Extraction is a PDF-parsing problem, not an API problem.

## Recommended v1 scope

Given that nothing here resembles a USPTO ODP-style REST API, v1 should ride on **(a) static document mirroring** and **(b) a single tightly-scoped CAPTCHA-aware HTML connector** for the highest-value live data.

1. **Static law/regs/manuals corpus** — Patents Act + Rules, TM Act + Rules, Designs Act + Rules, GI Act + Rules, Copyright Act, PPV&FR Act, MPPP. Mirror once from indiacode.nic.in + ipindia.gov.in, expose section-by-section like the existing MPEP/TMEP modules. Zero CAPTCHA, zero rate limit, full text always available. Highest ROI.
2. **Patent Office Journal + Trade Marks Journal ingest** — predictable weekly PDF URLs, no auth, no CAPTCHA. Build a scheduled fetcher + PDF text extractor. Unlocks Controller decisions (asset 22) and weekly grant/advertisement feeds. Heavy on storage but mechanically trivial.
3. **Delhi HC IP Division docket** — structured, free, reliable, growing fast. Wraps cleanly as a high-court IP case search. Provides the only post-IPAB appellate substrate. Friction: occasional CAPTCHA on full-text fetch.

Defer **InPASS** and **TM Public Search** unless we accept a CAPTCHA-solver dependency (2Captcha/Anti-Captcha) and the operational fragility that comes with ASP.NET WebForms scraping. If we ship them, position as "best-effort scrapers" with explicit quality caveats.

## Skip list

- **InPASS scraping (v1)** — CAPTCHA + ASP.NET viewstate + frequent downtime. Cross-coverage via EPO OPS / Google Patents / Patentscope is sufficient for most IN biblio needs (full-text only on InPASS, but that's a v2 problem).
- **TM Public Search scraping (v1)** — Oracle APEX + legacy ASP.NET both fragile; commercial providers exist if hard requirement.
- **Designs Public Search scraping** — small jurisdiction signal, "not valid for legal proceedings" disclaimer, gaps in coverage. Skip.
- **Form 27 bulk** — no index, no API; would require iterating CAPTCHA-gated E-Register per patent. Specialty project, not v1.
- **Controller decisions as a separate dataset** — they live inside the Patent Office Journal; ship via journal ingest, not as a separate connector.
- **Cross-HC e-courts API** — judgments.ecourts.gov.in is on the `legal-research` skill's roadmap; don't duplicate here.

## Open questions

1. **CAPTCHA strategy:** Do we ship a 2Captcha/Anti-Captcha integration as an optional dep, or do we hard-skip every CAPTCHA-gated endpoint? Affects InPASS, TM search, Designs search, GI detail views.
2. **Journal PDF storage:** Patent Office Journals run 200–500MB/week. ~50GB/yr just for patent journal. Do we ingest+strip-to-text and discard PDFs, or mirror PDFs too? Affects R2/storage cost.
3. **Form 27 academic compilation:** Is there a Research-side use case strong enough to justify a one-time hand-curated mirror (~50k post-2012 patents)? MSF, Access IBSA, generics manufacturers would all consume this.
4. **Delhi HC IPD JSON:** Their portal serves HTML; is there an ecourts.gov.in JSON API we can use instead? Worth a discovery pass.
5. **Statute update cadence:** Patents Rules amend every 1–3 years; how do we detect new amendments without manual monitoring? RSS / WIPO Lex push / scheduled diff?

## Comparison with CNIPA

IPO India is **less tractable than CNIPA** in some dimensions and **more tractable** in others:

- **More tractable than CNIPA:** No geo-fencing, no Chinese-phone-number requirement, no language barrier (English is an official IPO India language; almost all records are in English; Hindi is co-equal but rare in machine records). Statutes are freely available in authoritative English. Court decisions are public and accessible (vs. wenshu.court.gov.cn's collapsing public docket). The Delhi HC IPD is a genuinely well-structured docket — better than anything CNIPA-side. EPO OPS coverage of IN is solid (IN is a PCT receiving office; IN biblio + INPADOC events propagate cleanly).
- **Less tractable than CNIPA:** No PSS-equivalent. No bulk-data contract path at all (CNIPA at least sells XML packs to Chinese entities). Even CNIPA exposes weekly grant XML via the Patent Information Service; IPO India publishes only PDF journals. The 2024 Patents Rules removed Form 27 licensee disclosure — a regression in transparency. Site uptime is materially worse than CNIPA.
- **Same problems both share:** CAPTCHA-everywhere, no documented REST contracts, ASP.NET/Oracle-APEX legacy stacks, brittle session state, no first-party Python clients of any quality.

Net: **CNIPA's data is harder to reach but better-structured once reached; IPO India's data is easier to reach in principle but the formats are worse (PDF-only journals, no XML feeds).** The right move for IPO India v1 is to lean hard on the static document side — where IPO India is genuinely *easier* than CNIPA — and minimize the CAPTCHA-scraped surface area to one high-value asset (Delhi HC IPD).

## Sources

- IPO India portals: [ipindia.gov.in](https://ipindia.gov.in/) · [InPASS](https://iprsearch.ipindia.gov.in/PublicSearch/) · [TM Public Search (new APEX)](https://tmsearch.ipindia.gov.in/) · [TM Public Search (legacy)](https://tmrsearch.ipindia.gov.in/tmrpublicsearch/) · [Designs Search](https://search.ipindia.gov.in/designsearch) · [Designs E-Register](https://search.ipindia.gov.in/DesignApplicationStatus/DesignEregister/index) · [GI Public Search](https://search.ipindia.gov.in/GIRPublic/) · [Registered GIs list](https://ipindia.gov.in/registered-gls.htm)
- Journals: [Patent Office Journal](https://ipindia.gov.in/journal-patents.htm) · [Trade Marks Journal](https://ipindia.gov.in/ipr/TMR_journal/index.htm) · [Journal search](https://search.ipindia.gov.in/IPOJournal/Journal/Patent)
- Statutes: [India Code Patents Act 1970](https://www.indiacode.nic.in/handle/123456789/1392) · [Patents Act consolidated through 2024-08-01](https://www.ipindia.gov.in/writereaddata/Portal/IPOAct/1_113_1_The_Patents_Act__1970___incorporating_all_amendments_till_1-08-2024.pdf) · [PPV&FR Act 2001](https://www.indiacode.nic.in/bitstream/123456789/1909/1/A2001-53.pdf) · [Section 3(d)](https://ipindia.gov.in/writereaddata/portal/ev/sections/ps3.html) · [Patent Rules listing](https://ipindia.gov.in/rules-patents.htm)
- MPPP: [Manual v3.0 (2019)](https://ipindia.gov.in/frontend/pdf/patents/Manual_for_Patent_Office_Practice_and_Procedure_.pdf) · [WIPO Lex MPPP entry](https://www.wipo.int/wipolex/en/legislation/details/7648)
- Patents (Amendment) Rules 2024 + Form 27: [IPWatchdog analysis](https://ipwatchdog.com/2024/03/28/understanding-2024-amendment-indias-patents-rules-light-u-s-patent-rules/) · [Lexology — Form 27 post-2024](https://www.lexology.com/library/detail.aspx?g=ae470b5e-6c73-4063-9d46-79ac8bc02a99) · [Form 27 deep dive](https://www.lexology.com/library/detail.aspx?g=da1555b4-1c33-467a-8f6d-eb6079d9325f)
- Delhi HC IPD: [Delhi HC homepage](https://www.delhihighcourt.nic.in/) · [Latest judgments](https://delhihighcourt.nic.in/web/judgement/fetch-data) · [IPD Annual Report 2022-23](https://delhihighcourt.nic.in/files/2024-04/213033669764676f5dda169.pdf) · [IPD Rules 2022 on WIPO Lex](https://www.wipo.int/wipolex/en/legislation/details/21496) · [Managing IP — IPD game-changer](https://www.managingip.com/article/2aoxdrzghl7fpb3f1ce80/sponsored-content/game-changer-the-intellectual-property-division-of-the-high-court-of-delhi)
- IPAB abolition: [Tribunals Reforms Act 2021 — JURIST commentary](https://www.jurist.org/commentary/2021/07/parnami-raj-delhi-ip-bench/) · [Asia IP — post-IPAB landscape](https://asiaiplaw.com/section/in-depth/india-post-ipab-should-other-courts-also-have-their-own-ip-division)
- E-courts: [HC Services](https://hcservices.ecourts.gov.in/) · [Judgments portal](https://judgments.ecourts.gov.in/)
- Open data: [data.gov.in weekly patent dataset](https://www.data.gov.in/resource/weekly-patent-application-published) · [IP statistics dashboard](https://www.bananaip.com/intellepedia/ip-statistics-dashboard/)
- Trade Secrets: [Trade Secrets Bill 2024 — Intepat](https://www.intepat.com/blog/the-trade-secret-bill-2024-a-comprehensive-analysis) · [EU IP Helpdesk overview](https://intellectual-property-helpdesk.ec.europa.eu/news-events/news/overview-protection-trade-secrets-bill-2024-2024-06-06_en) · [22nd Law Commission Report](https://corporate.cyrilamarchandblogs.com/2024/05/the-22nd-law-commission-report-on-trade-secrets-call-for-a-balancing-act/)
- PPV&FR: [Plant Authority portal](https://plantauthority.gov.in/) · [Variety compendium](https://plantauthority.gov.in/compendium-varieties-registered-under-ppvfr-act-2001)
