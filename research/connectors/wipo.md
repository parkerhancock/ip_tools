# WIPO Connector Survey

One-page scoping survey of WIPO (and UPOV) data assets for potential inclusion
in `patent-client-agents`. Status as of 2026-05.

## Cross-asset comparison

| Asset | Type | Auth | Format | Bulk DL | Cost | Ease |
|---|---|---|---|---|---|---|
| PATENTSCOPE search web service | SOAP | Paid subscription | XML | Via SFTP (separate) | CHF 600/yr (search) + CHF 2,000/yr (Java/SOAP "Operational" API) | Hard (SOAP) |
| PATENTSCOPE bulk PCT data | SFTP push | Subscription | XML + TIFF | Yes (weekly) | CHF 400/yr (basic bibliographic), more for full text/images | Medium |
| Madrid Monitor (online) | HTML | None for UI | HTML/JSON internal | Prohibited by ToS | Free | Hard (scrape) |
| Madrid Monitor bulk XML | FTP (ICC) | Paid subscription | XML | Yes (daily diffs) | ~CHF 30,000/yr | Easy if paid |
| Hague Express | HTML | None | HTML | Manual only | Free | Medium (scrape) |
| Lisbon Express | HTML | None | HTML | Manual only | Free | Easy (small dataset) |
| Global Brand Database | HTML | None | HTML/JSON internal | **Prohibited** | Free | Hard (anti-scrape) |
| Global Design Database | HTML | None | HTML/JSON internal | **Prohibited** | Free | Hard (anti-scrape) |
| WIPO Lex | HTML + PDFs | None | HTML/PDF | Not formal | Free | Medium (scrape) |
| WIPO Standards (ST.96/ST.36) | Spec docs | None | XSD / PDF | Yes (just download XSDs) | Free | n/a (reference only) |
| UPOV PLUTO | HTML | WIPO account | HTML/JSON internal | Contributors only | Free | Hard |
| WIPO Pearl (terminology) | REST API | API key (request) | JSON | n/a | Free | Easy |
| WIPO Article 6ter | REST API | None (documented) | JSON | n/a | Free | Easy |
| WIPO API Catalog (meta) | REST/HTML | None | OAS / JSON | n/a | Free | Easy |

---

## 1. PCT / PATENTSCOPE

- **URL:** `https://patentscope.wipo.int/` (UI), web service docs at `https://www.wipo.int/en/web/patentscope/data/index`
- **Auth:** Paid annual subscription required for the web service. No public REST/JSON endpoint.
- **Protocol/format:** SOAP/XML (Java sample code). No JSON-native REST endpoint as of 2026; WIPO's roadmap mentions REST but PATENTSCOPE itself has not migrated.
- **Cost:** CHF 600/yr for search web service, CHF 2,000/yr for the "Operational" Java SOAP API that returns IASR + batch document downloads. PCT raw-data SFTP feed is a separate CHF 400/yr+ subscription.
- **Coverage:** 100M+ records across PCT applications and 70+ national/regional collections. Front-page images, full-text claims/description for XML-filed applications.
- **Bulk download:** Yes, via SFTP, weekly on publication day. Bibliographic XML + TIFF images for the publication week.
- **ToS:** Bulk scraping of the search UI is prohibited; SFTP feed has its own commercial terms. Resale of raw documents is restricted.
- **Python clients on PyPI:** None I could find with active maintenance. The notable client is the Ruby gem `cantab/patentscope`. Some users build SOAP calls with `zeep`. `wipo-ipc` exists on PyPI but appears to be a small IPC-code lookup helper, not a PATENTSCOPE client.

## 2. Madrid Monitor / Madrid System

- **URL:** `https://www3.wipo.int/madrid/monitor/en/`
- **Auth:** None for the UI. Paid subscription for bulk XML.
- **Protocol/format:** Browser UI hits an internal JSON endpoint, but ToS forbids automation. Bulk XML follows WIPO ST.66.
- **Cost:** Free UI. Full Madrid Monitor XML database **CHF ~30,000/year** via the UN International Computing Centre (ICC) FTP. Daily delta files with marks-changed snapshots plus images.
- **Coverage:** ~915,000 international trademark registrations across 132 Madrid System members.
- **Bulk download:** Yes for paying subscribers (ICC FTP, daily). No legal path for free bulk.
- **ToS:** Explicitly disallows bulk/automatic download from the web UI.
- **Python clients:** None on PyPI. Third-party aggregators (e.g., Signa.so) offer commercial APIs over Madrid data.

## 3. Hague Express

- **URL:** `https://www.wipo.int/en/web/hague-system/design_search` and `https://designdb.wipo.int/designdb/hague/en/`
- **Auth:** None.
- **Format:** HTML UI with internal JSON. Weekly update cadence.
- **Coverage:** International design registrations under the Hague Agreement (~95 members).
- **Bulk download:** None advertised; same ToS constraints as the other WIPO databases.
- **ToS:** Same anti-bulk language as Madrid Monitor and Global Brand DB.
- **Python clients:** None found.

## 4. Lisbon System / Lisbon Express

- **URL:** `https://lisbon-express.wipo.int/`
- **Auth:** None.
- **Format:** HTML; small dataset.
- **Coverage:** Appellations of origin + geographical indications registered under Lisbon Agreement + 2015 Geneva Act. Total record count is small (low thousands).
- **Bulk download:** Not formal, but the dataset is small enough that a polite scraper is feasible.
- **ToS:** Same WIPO ToS family.
- **Python clients:** None found.

## 5. Global Brand Database

- **URL:** `https://branddb.wipo.int/` (aggregator). Status page: `https://www.wipo.int/en/web/global-brand-database`
- **Auth:** None for UI.
- **Format:** HTML + internal JSON; web UI caps any single download at 180 records.
- **Coverage:** ~70M trademark records, 87 national/regional sources, daily refresh. Aggregator across e.g. USPTO TSDR, EUIPO, Madrid, JPO etc.
- **Bulk download:** **Explicitly prohibited.** WIPO cannot redistribute because of contributor-office agreements.
- **ToS:** Hard "no automated querying, no bulk." Hard to wrap legally.
- **Python clients:** None. Anti-automation features in the UI (Cloudflare-class) actively block bots.

## 6. Global Design Database

- **URL:** `https://designdb.wipo.int/designdb/en/`
- **Auth:** None.
- **Format:** HTML + internal JSON; UI caps downloads at 100 records.
- **Coverage:** Aggregator across national + Hague design registrations.
- **Bulk download:** **Explicitly prohibited.**
- **ToS:** Same as Global Brand DB.
- **Python clients:** None.

## 7. WIPO Lex

- **URL:** `https://www.wipo.int/wipolex/en/main/legislation`
- **Auth:** None.
- **Format:** HTML pages + PDF/DOC attachments. No public API and no documented SPARQL endpoint (WIPO Lex is not part of the EU CELLAR/ELI linked-data stack despite surface similarities).
- **Coverage:** ~50,000 documents from ~200 jurisdictions across three collections: IP laws/regulations, WIPO-administered treaties + IP-related treaties, IP judgments. Six UN languages.
- **Bulk download:** None advertised. The site is built for human browsing and PDF download.
- **ToS:** Public legal texts — generally redistributable (statutes/treaties are not copyrightable as a rule) but WIPO's editorial layer (bibliographic notes, cross-references) is theirs.
- **Python clients:** None found. EU has `eurlex` for EUR-Lex; nothing equivalent for WIPO Lex.

## 8. WIPO Standards (ST.96, ST.36, ST.66, ST.86)

- **URL:** `https://www.wipo.int/standards/en/`
- **Format:** XSDs, design rules, release notes (PDFs).
- **Relevance:** Reference only. ST.96 is the dominant modern IP XML schema; ST.36 (patents), ST.66 (TMs), ST.86 (designs) are legacy formats still used by ODP/EPO/Madrid bulk feeds. Worth bundling the schemas as reference data if we add XML parsers for any of the bulk feeds — not a "connector" per se.
- **Python clients:** Generic `xmlschema` works fine; no WIPO-specific package needed.

## 9. UPOV PLUTO

- **URL:** `https://pluto.upov.int/` (and `https://www.upov.int/en/find-and-explore/databases/pluto-search`)
- **Auth:** WIPO User Account required (free signup). Premium tier free for UPOV-member officials.
- **Format:** HTML UI; internal JSON. No public API.
- **Coverage:** Plant variety records from UPOV members + OECD. Used for denomination similarity searches.
- **Bulk download:** Only available to data **contributors** (the "PLUTO Contribute" workflow). No consumer-side bulk.
- **ToS:** UPOV terms; non-commercial leaning.
- **Python clients:** None.

## 10. Newer 2024-2026 WIPO APIs

- **WIPO API Catalog** (`https://apicatalog.wipo.int/`): Launched July 2024 as a meta-index of IP-office APIs (USPTO, EPO, JPO, KIPO, etc.). Crawls OpenAPI specs published by member offices. Not a data API itself — useful only as a discovery layer. Free.
- **WIPO Pearl Terminology API**: REST/JSON, API key obtained via Business Partner Portal request. Free. Niche (multilingual terminology lookup for technical translation).
- **Article 6ter Express API** (`https://6ter.wipo.int/api`): REST/JSON. State emblems and international-org marks. Niche, small dataset, but actually a documented modern endpoint — easy win if anyone needs it.
- **WIPO IP Portal** redesign (2024): UX-only refresh of the unified entry point; no new public data API behind it.
- **WIPO Standard on Web APIs**: WIPO has been publishing internal standards (REST-JSON, REST-XML, SOAP-XML interface types) telling member offices how to design APIs. This is signal that WIPO is encouraging modernization but is itself slow to migrate its own services.

---

## Recommended v1 scope

1. **PATENTSCOPE PCT raw-data SFTP feed** — at CHF 400/yr the cheapest path to weekly PCT publication data, complements our existing USPTO/EPO patent coverage. Pure XML parsing problem (ST.36 / ST.96), no scraping ethics issue. High filing volume (~280k PCT applications/yr).
2. **WIPO Lex** — free, public, redistributable legal texts. Pairs with our existing MPEP/TMEP wrappers as a global "substantive law" layer. Polite HTML scraper + PDF fetcher; volume is bounded (~50k docs). High utility for any agent doing comparative IP law questions.
3. **Article 6ter Express API** — cheap "+1" wrapper. Real REST/JSON, no auth, small dataset, documented OpenAPI. Useful for trademark conflict checks (state emblems, IGO marks) that USPTO/EUIPO don't cover. Maybe 1-2 days of work and we ship three WIPO assets instead of two.

Reasoning: filing-volume × ease-of-access. PATENTSCOPE bulk + WIPO Lex are the two assets where the legal/ToS picture is clean and the data is genuinely additive. 6ter is a freebie.

## Skip list

- **Global Brand Database** and **Global Design Database** — ToS forbids automation; anti-scrape defenses in the UI; nothing redistributable. Not worth the legal/engineering risk.
- **Madrid Monitor bulk XML** — CHF 30,000/yr is a budget conversation, not an engineering one. Skip until a paying client requires it. The free UI is also off-limits per ToS.
- **UPOV PLUTO** — niche (plant variety), no public bulk path, requires account. Revisit only on customer demand.
- **WIPO Pearl** — niche, would mostly be useful for translation workflows, not patent prosecution.
- **PATENTSCOPE SOAP search service** — at CHF 600+CHF 2,000/yr it's only marginally cheaper than commercial alternatives, and SOAP is a poor fit for our async/Pydantic stack. The bulk SFTP feed gives us most of the data at a fraction of the cost.
- **Hague Express, Lisbon Express** as standalone wrappers — low traffic, low utility unless a customer asks. Could fold into a future "international filings" module alongside Madrid.

## Open questions

- Does the **PCT SFTP feed** include reassignments / legal-status updates, or only publication-week snapshots? WIPO's data page mentions IASR (International Application Status Report) only on the paid SOAP API — confirm before scoping.
- Is there a **REST/JSON PATENTSCOPE** endpoint planned for 2026-2027? WIPO has published web-API standards but not announced a PATENTSCOPE migration date. Worth a direct email to `patentscope@wipo.int`.
- **WIPO Lex licensing**: confirm WIPO's position on systematic mirroring of the database. Statutes themselves are public-domain, but the bibliographic metadata layer may have separate ToS.
- **API Catalog crawler**: does it expose its index as a downloadable JSON/OAS list, or only as an HTML directory? Could be a useful seed for discovering all of EPO/USPTO/JPO/etc. APIs in one place.
- **Article 6ter API**: rate limits and quotas are not documented on the public docs page — needs a test call.
- Any **community-maintained Python wrappers** living outside PyPI (GitHub-only)? My searches found Ruby and JavaScript projects but no actively maintained Python ones; worth a closer look before reinventing.
