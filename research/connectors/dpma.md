# DPMA (Deutsches Patent- und Markenamt) — Connector Survey

Survey of DPMA and adjacent German-IP data sources for `patent-client-agents`.
DPMA is the largest national office in Europe and the home of BPatG and the
UPC's mechanical-engineering central division — strategic even though EPO OPS
already returns DE family members.

## Cross-asset comparison

| Asset | Endpoint | Auth | Cost | Format | Bulk? | Python client? |
|---|---|---|---|---|---|---|
| DPMAregister (UI) | `register.dpma.de` | none | free | HTML, CSV, XLSX (≤cap) | no | none |
| DEPATISnet (UI) | `depatisnet.dpma.de` | none | free | HTML, CSV/XLSX (≤100 rows), PDF/TIFF | no (UI only) | none |
| DPMAconnect / **Plus** (REST) | DPMA (contract-gated) | username + password over TLS | €200 one-time + provision fees | REST JSON/XML, PDF/TIFF | yes (weekly packages) | none on PyPI; Go in `patent-dev/bulk-file-loader` |
| DPMA Backfile data | `dpma.de/.../backfile` | contract / order | paid (provision costs) | XML (WIPO ST.36 patents, ST.86 designs), images | yes | none |
| Online Akteneinsicht | `register.dpma.de` (in-register) | none (CAPTCHA gate) | free | PDF | no | none |
| BPatG decisions | `bundespatentgericht.de` + CE-BPatG (Zenodo) | none | free (non-commercial) | HTML, PDF; Zenodo dump | partial (Zenodo dataset) | none |
| BGH decisions | `bundesgerichtshof.de` + `rechtsprechung-im-internet.de` | none | free | HTML, PDF, XML on RiI | yes (RiI XML) | community scrapers |
| gesetze-im-internet.de | same | none | free | HTML, PDF, **XML** | yes (per-act `xml.zip`) | `bundestag/gesetze` (md mirror) |
| UPC CMS | `cms.unified-patent-court.org` | **OAuth2** (token, 1800s) | free for registered users | JSON | A2A API | none specific |

## 1. DPMAregister
`register.dpma.de`. Free, daily-updated, no auth, all four IP rights.
Patents since 1981-01-01, trade marks back to 1894-10. Basic / Advanced /
Expert search plus a "Monitoring" mode. Export is CSV/XLSX from the result
list, HTML/PDF "register excerpt" per record. No JSON endpoint —
programmatic access is via DPMAconnectPlus.
[DPMA | DPMAregister](https://www.dpma.de/english/search/dpmaregister/index.html);
[WIPO Inspire entry](https://inspire.wipo.int/dpmaregister).

## 2. DEPATISnet
Worldwide patent search front-end over the DEPATIS archive — **160M+
patent publications**, German docs back to 1877, plus WO/EP/US/JP/etc.
UI only, no advertised JSON API. Expert mode supports a structured query
language (`field operator term`, AND/OR/NOT, proximity ops). CSV/XLSX
export **capped at 100 rows** per query. PDFs downloadable per document.
The expert-search URL (`depatisnet.dpma.de/DepatisNet/depatisnet?action=experte`)
accepts HTTP GET with a `query=` parameter and is the de facto scrape
target.
[DEPATISnet](https://www.dpma.de/english/search/depatisnet/index.html);
[help PDF](https://depatisnet.dpma.de/prod/de/depatisnet_hilfe.pdf).

## 3. DPMAconnectPlus — the REST API
The only first-class programmatic interface. SSL/TLS REST; legal-status
+ publication data for **all four IP rights**; on-demand retrieval +
weekly bulk packages (patents/UM Thursdays, TM/design Fridays). Auth =
**username/password issued by DPMA after signing a standard data-supply
agreement** — not OAuth (unlike EUIPO and UPC). **€200 one-time connection
fee**; per-record retrieval free; bulk packages incur "provision costs".
JSON/XML metadata + PDF/TIFF documents. Spec PDFs:
[Schnittstellenbeschreibung](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf),
[API-Beschreibung](https://dpma.de/docs/recherche/dienste/dpmaconnectapibeschreibung.pdf).
No Python client on PyPI; closest prior art is a Go library
([`patent-dev/bulk-file-loader`](https://github.com/patent-dev/bulk-file-loader),
MIT, 2024+).
[DPMAconnectPlus](https://www.dpma.de/english/search/data_supply_services/dpmaconnect/index.html).

## 4. DPMA Backfile / open data
DPMA does **not** run a free open-data bucket comparable to USPTO
`data.uspto.gov` or EPO BDDS. "Backfile data" is a paid order-by-volume
service shipped as WIPO **ST.36** (patents/UM) + **ST.86** (designs) XML
plus images; ST.96 not yet implemented per DPMA's WIPO CWS status report.
Free bulk → use EPO OPS (we already wrap it) or scrape DEPATISnet.
[DPMA | Backfile data](https://www.dpma.de/english/search/data_supply_services/dpmadatenabgabe/backfile/index.html).

## 5. Online Akteneinsicht (file inspection)
Free, in-DPMAregister, **patents + utility models only** (no TM/design).
Covers grants since 2013-01-21 plus any older file requested for
inspection. Returns PDFs of application docs, OAs, replies. Gated by a
CAPTCHA-style "security question". DPMAconnectPlus exposes the DEPATIS
document archive (published specifications) but **not** prosecution
correspondence.
[Online file inspection](https://www.dpma.de/english/search/dpmaregister/file_inspection/index.html);
[file scope](https://register.dpma.de/register/htdocs/test/en/hilfe/online-akteneinsicht/welcheaktenkoennenangefordertwerden/index.html).

## 6. Utility models (Gebrauchsmuster)
There is **no separate "DPMAnutzer" portal** — utility-model records ride
inside DPMAregister, DEPATISnet, and DPMAconnectPlus alongside patents.
This matters because **Gebrauchsmuster are not in EPO OPS as a distinct
right-type**, and Germany is one of the very few major jurisdictions where
utility models are heavily used as unexamined fast-track and as a
divisional weapon during litigation. **DPMA is the only authoritative
source for the German GM corpus.**
[Utility Models](https://www.dpma.de/english/utility_models/index.html).

## 7. DEPATIS (legacy)
"DEPATIS" is the underlying archive; **DEPATISnet** is the web layer.
No separately exposed mainframe API to worry about — DPMAconnectPlus is
the canonical machine interface today.

## 8–15. Statutes, guidelines, forms

**gesetze-im-internet.de** — official BMJ/BfJ portal, free,
scrape-friendly, per-act **XML zip** + HTML + (for major acts) English
PDF translations by DPMA's Language Service. All target acts available:
PatG, MarkenG, GebrMG, DesignG (ex-GeschmMG), UrhG, GeschGehG (2019
implementation of EU Dir. 2016/943). Community Markdown mirror at
[`bundestag/gesetze`](https://github.com/bundestag/gesetze) renders the
XML daily. The earlier `tech4germany/rechtsinfo_api` is offline.

**DPMA examination guidelines / Richtlinien** (P 2796 patents, P 2733
classification, plus TM/design/utility-model search guidelines under §7
GebrMG) are PDF-only on dpma.de. English versions exist for several.
**Filing forms / Anmeldebestimmungen**: PDF-only — not a connector target.
[DPMA | Law](https://www.dpma.de/english/our_office/law/index.html).

## 16. Bundespatentgericht (BPatG)
Germany's primary invalidation / inter-partes venue + appeal court from
DPMA examiner decisions. All decisions from 2000-01-01 forward at
[bundespatentgericht.de/Decisions](https://www.bundespatentgericht.de/EN/Jurisdiction/Decisions/decisions_node.html);
full-text search; HTML + PDF; no public REST. Open dataset: **CE-BPatG
(Corpus der Entscheidungen des Bundespatentgerichts)** on
[Zenodo](https://zenodo.org/records/7767295) — largest free BPatG corpus,
refreshed 1–2× per year. Non-commercial reuse free; commercial fee-based.
Fastest path to a usable corpus without scraping the live site.

## 17–18. Bundesgerichtshof (BGH)
Supreme civil/criminal court; X. Zivilsenat hears patent appeals from
BPatG. Two access points:

- **bundesgerichtshof.de** — official DB, full-text since 2000-01-01,
  free non-commercial, HTML + PDF, RSS feeds at
  `Service/RSSFeed/Function/RSS_EN.xml`. No JSON API.
- **rechtsprechung-im-internet.de** — federal-courts portal (BMJ/BfJ),
  BGH decisions since 2010, daily updates, **structured XML** alongside
  HTML/PDF, catalogued on
  [GovData](https://www.govdata.de/suche/daten/rechtsprechung-im-internet)
  with explicit free-reuse licensing. **This is the scrape-friendly
  entry point.**

## 19. UPC (Unified Patent Court)
Out of DPMA but practically essential. CMS at
`cms.unified-patent-court.org`. **CMS public API is OAuth2** (token,
1800s lifetime — the older API-KEY auth was retired). Use cases:
programmatic opt-outs, case lookups.
[CMS Public API v1.4](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/upc-cms-public-api-documentation_v1_4.pdf);
[A2A API](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/UPC-New_CMS_A2A%20API%20Documentation_V1_4_forPublication_StartOf8July.pdf).
~883 cases filed as of 2025-05 — corpus small enough that periodic sync
is cheap.

---

## Recommended v1 scope

**Wrap, in priority order:**

1. **DEPATISnet expert-search scrape + per-doc PDF fetch.** No auth, no
   contract, immediate value. Covers Gebrauchsmuster (which EPO OPS does
   not). Implement as an HTML scraper with a typed `expert_search(query,
   format=…)` and `get_document(pub_number, format=pdf|tiff)`. Pair with
   the existing EPO OPS client for cross-validation of bibliographic data.
2. **gesetze-im-internet.de statute fetcher.** Per-act XML zip + English
   PDF, cached. Cheap, no auth, lets us answer "show me §3 PatG" or "GeschGehG
   §2 Nr. 1 definition". Models same shape as our existing MPEP/TMEP
   resources. Bonus: mirror the [`bundestag/gesetze`](https://github.com/bundestag/gesetze)
   markdown corpus for offline use.
3. **BGH / BPatG decision fetcher via `rechtsprechung-im-internet.de` XML
   + CE-BPatG Zenodo snapshot.** Combine the live RiI XML feed (fresh BGH
   decisions, daily) with the CE-BPatG Zenodo dump (deep BPatG corpus).
   Both free, both well-licensed. Gives us a real German patent-litigation
   data layer.

## Skip list

- **DPMAconnectPlus** in v1 — the €200 connection fee plus a signed standard
  agreement plus the lack of self-serve onboarding makes this a v2 decision
  contingent on user demand. The Go reference client
  [`patent-dev/bulk-file-loader`](https://github.com/patent-dev/bulk-file-loader)
  is the model to copy when we do wrap it.
- **DPMA Backfile XML** — paid, ST.36 only, redundant with EPO OPS for DE
  patent publications.
- **UPC CMS API** — important but orthogonal to DPMA; spin out as its own
  connector card.
- **DPMA examination guidelines (PDF-only)** — not structured enough to be
  worth a connector; index links in the docs.
- **DPMAnutzer** — does not exist as a separate portal.

## Open questions

- DEPATISnet ToS / rate-limit posture for automated scraping — DPMA has
  not published an explicit robots policy beyond standard `robots.txt`;
  need to confirm acceptable QPS empirically and add `User-Agent` identifying
  patent-client-agents.
- Whether the Online Akteneinsicht CAPTCHA gate is bypassable with a
  cookie-bearing session or whether we need a manual-token workflow (the
  USPTO ODP file-history flow is the precedent).
- Whether CE-BPatG ships ECLI identifiers consistently — required for
  cross-linking to BGH and (future) EU CJEU IP decisions.
- DPMAconnectPlus per-call quota — the spec PDFs do not appear to disclose
  rate limits; need to ask DPMA when (if) we sign the agreement.

## Compare/contrast with existing connectors

**vs. EPO OPS:** EPO OPS already returns DE patent publications and
INPADOC legal status/family, so for *examined* DE patents the marginal
benefit of DPMA is modest. But EPO OPS does not cover (a) Gebrauchsmuster
as a distinct right-type, (b) DE trademarks/designs, (c) prosecution file
wrappers, (d) BPatG/BGH decisions, or (e) DE statutes. DPMA + RiI +
gesetze-im-internet are the only paths. Value concentrates in **utility
models + register metadata + litigation/statute corpora**, not in
re-fetching what EPO returns.

**vs. EUIPO:** EUIPO has modern OAuth2 client-credentials + well-documented
JSON REST. DPMAconnectPlus is generationally behind: username/password,
contract-gated, weekly bulk packages over streaming. The free public
surface (DEPATISnet, register, AkE) is UI-first and must be scraped.

**vs. USPTO ODP:** USPTO ODP is API-key gated but free, JSON-native, with
self-serve onboarding — much friendlier. DPMAconnectPlus is gated by money
and paperwork; the free counterpart (DEPATISnet/register UI) is more like
PPUBS — usable but scrape-shaped.
