# PH/IPOPHL (Intellectual Property Office of the Philippines) — Wave 2026-05-18

**Question:** Does IPOPHL expose a public REST/JSON/XML API we can call
per user query at runtime? Currently `rating: tbd` in
`STATE.yaml`. Bulk dumps and HTML-only surfaces = red. BYOK with
per-user creds = yellow. Undocumented-but-unauthenticated APIs that
are stable = green.

**Verdict:** 🔴 **Red overall — but transitive coverage is unusually
deep, and IPOPHL is the **regional Country Lead** for the very tools
that already cover PH.** The only IPOPHL-hosted programmatic surface
is **WIPO Publish at [`wipopublish.ipophil.gov.ph`](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home)** —
a public, unauthenticated Apache Wicket UI over an internal Solr core,
supporting `OFCO:PH` Solr/Lucene queries against ~82k patents, ~791k
trademarks, and ~24k designs. It is HTML-only (server-side-rendered,
no JSON response envelope, no documented REST), behind an IIS reverse
proxy with `jsessionid` URL rewriting. There is **no entry for IPOPHL
in the [WIPO IP API Catalog](https://apicatalog.wipo.int/)** (179
APIs, 10 unique IPOs — DPMA, EPO, EUIPO, IP Australia, JPO, MOIP
KOREA, QAZ, UPRP, USPTO, WIPO — zero PH). The IPOPHL e-services
domain [`onlineservices.ipophil.gov.ph`](https://onlineservices.ipophil.gov.ph/)
is wholly behind an Incapsula WAF returning 403 to bot user agents.
**`data.gov.ph`** is an Angular SPA with no IPOPHL datasets. The
genuine wins are transitive — **WIPO PATENTSCOPE** carries the full
national PH patent collection (1899-11-17, refreshed twice/month);
**EUIPO TMview / ASEAN TMview** carries the PH trade-mark register
(IPOPHL is the regional Country Lead operating ASEAN TMview /
ASEAN DesignView on EUIPO infrastructure); **WIPO Global Brand
Database** carries the same PH TM data; **WIPO Hague** carries
international designs designating PH; **EPO INPADOC** carries PH
patent biblio + family + legal events. **Recommended
`connector_status: skipped` (register-side, with the strategic-memory
note that PH is *materially* covered by upstream tools we already
ship); statutes-side `planned` — RA 8293 IP Code on
[lawphil.net](https://lawphil.net/) is a small static-corpus win.**

---

## 1. Endpoint

IPOPHL's online surface splits across three hosts; **none** expose a
documented programmatic interface.

| Surface | Host | Right(s) | Shape | Bot access |
|---|---|---|---|---|
| WIPO Publish (national search) | [`wipopublish.ipophil.gov.ph`](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home) | patent, utility model, design, trademark | Apache Wicket HTML over Solr | ✅ Direct (no WAF) |
| e-Services (filings, copyright search, BLA, registries) | [`onlineservices.ipophil.gov.ph`](https://onlineservices.ipophil.gov.ph/) | filing + copyright register + BLA notices | Incapsula-WAF-walled CMS / classic ASP | 🔒 403 to bots |
| Institutional CMS | [`www.ipophil.gov.ph`](https://www.ipophil.gov.ph/) | content, fee schedules, manuals (PDFs) | WordPress 6.9.x | ✅ Direct |

Transitively-accessible PH surfaces hosted by **other offices**:

| Surface | Host | Right(s) | Coverage cited primary source |
|---|---|---|---|
| ASEAN IP Register | [`ip-register.aseanip.org`](https://ip-register.aseanip.org/wopublish-search/public/home) | regional consolidated patent + TM + design | Operated by IPOPHL on behalf of ASEAN; WIPO Publish stack |
| WIPO PATENTSCOPE national collection | [`patentscope.wipo.int`](https://patentscope.wipo.int/search/en/search.jsf) | PH patents, UMs, designs | Per [data-coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) row 60: 30.12.1899 – 17.11.2025, twice-a-month refresh |
| EUIPO TMview | [`tmdn.org/tmview`](https://www.tmdn.org/tmview/) | PH trademarks | [Philippines joins TMview (TMDN news)](https://www.tmdn.org/network/-/philippines-joins-tmview) |
| WIPO Global Brand Database | [`branddb.wipo.int/branddb/ph/en/`](https://branddb.wipo.int/branddb/ph/en/) | PH trademarks | [Coverage page](https://branddb.wipo.int/en/coverage) · [Launch news 2013](https://www.wipo.int/en/web/global-brand-database/w/news/2013/news_0003) |
| EPO INPADOC | EPO OPS | PH patents biblio + family + legal-status | Via [`patent_client_agents.epo_ops`](../../../src/patent_client_agents/epo_ops/) |
| WIPO Hague Express | [`wipo.int/designdb/hague/`](https://www.wipo.int/designdb/hague/) | International designs designating PH | PH is a Hague Agreement contracting state |
| WIPO Madrid Monitor | [`wipo.int/madrid/monitor/`](https://www.wipo.int/madrid/monitor/) | International TMs designating PH | PH joined Madrid Protocol 25 Jul 2012 |

**WIPO Publish URL conventions on `wipopublish.ipophil.gov.ph`:**

- `/wopublish-search/public/home` — landing page; renders module links.
- `/wopublish-search/public/patents?query=*:*` — patent list, Solr `*:*` for all.
- `/wopublish-search/public/patents?query=OFCO:PH` — patent list filtered to PH publishing office.
- `/wopublish-search/public/trademarks?query=OFCO:PH` — trade-mark list, PH only.
- `/wopublish-search/public/designs?query=OFCO:PH` — design list, PH only.
- `/wopublish-search/public/detail/patents?id=PH12010000340` — patent detail by publication number.
- `/wopublish-search/public/detail/trademarks?id={id}` — trade-mark detail.
- `/wopublish-search/public/detail/designs?id={id}` — design detail.
- `/wopublish-search/public/about` — about page (canonical WIPO Publish boilerplate).

The application is **Apache Wicket** (form actions like
`?0-1.IFormSubmitListener-body-advancedSearchTab-...`), `jsessionid`
in URL when cookies disabled. Internal Solr leak visible in resource
links: `http://10.10.0.125:9092/wopublish-resources/page/page1.html`
(the Solr-fronting service on the office LAN). No published JSON
endpoints, no `wt=json` exposed at the public URL.

Probes 2026-05-18 (US egress):

```
GET https://wipopublish.ipophil.gov.ph/wopublish-search/public/about
  → 200 OK, IIS 10.0, no auth, jsessionid via Set-Cookie

GET https://wipopublish.ipophil.gov.ph/wopublish-search/public/patents?query=OFCO:PH
  → 200 OK, ~356k-line HTML, "82327 results"

GET https://wipopublish.ipophil.gov.ph/wopublish-search/public/trademarks?query=OFCO:PH
  → 200 OK, "791043 results"

GET https://wipopublish.ipophil.gov.ph/wopublish-search/public/designs?query=OFCO:PH
  → 200 OK, "24141 results"

GET https://wipopublish.ipophil.gov.ph/wopublish-search/public/detail/patents?id=PH12013500907
  → 200 OK, biblio detail page (Wicket render)

GET https://onlineservices.ipophil.gov.ph/CopyrightSearch/
  → 403 Forbidden, Incapsula challenge (incident ID returned)

GET https://onlineservices.ipophil.gov.ph/blapublication/
  → 403 Forbidden, Incapsula

GET https://data.gov.ph/index/public/dataset/
  → 200 OK, but Angular SPA shell only; no SSR; no API discovered
```

---

## 2. Auth

There is **no API to authenticate against.** WIPO Publish at
[`wipopublish.ipophil.gov.ph`](https://wipopublish.ipophil.gov.ph/) is
anonymous read; the search forms accept anonymous queries. The
[`onlineservices.ipophil.gov.ph`](https://onlineservices.ipophil.gov.ph/)
suite (eTMfile, eInventionFile, eUMFile, eIDFile, eCorr 2.0, BLA
notices, Copyright registry/search) **requires the applicant's IPOPHL
account** (email-based; DragonPay payment) — not an API key. The
filing flow accepts foreign filers; this is filing-side, not search-
side, so it does not unlock biblio reads either.

The [WIPO IP API Catalog](https://apicatalog.wipo.int/) at probe
2026-05-18 (`GET /api/apis?size=300`) returned 179 APIs across
**10 unique IPOs**: DPMA, EPO, EUIPO, IP Australia, JPO, MOIP KOREA,
QAZ (Kazakhstan), UPRP (Poland), USPTO, WIPO. **Zero entries for
IPOPHL / Philippines / PH.** This is the canonical inventory of
office APIs — confirmed-by-absence.

No primary source advertises:
- An API key or OAuth client-credentials flow at any IPOPHL host.
- A developer registration portal.
- A paid-data agreement equivalent to DPMA's *DPMAconnectPlus*,
  KIPO's *KIPRIS Plus*, or IP Australia's OAuth2 OpenAPI suite.

---

## 3. Query Language

**Solr / Lucene URL parameter — undocumented but visible.** The WIPO
Publish patents/trademarks/designs endpoints accept a `query=` URL
parameter that resolves directly to the Solr query string. Observed
values:

- `query=*:*` — match all.
- `query=OFCO:PH` — restrict to records whose office-code field is `PH`.

The form submission inside the SPA also produces Wicket-style URL
parameters like `0-1.IFormSubmitListener-body-advancedSearchTab-...`
that drive server-side state — these are **not** a programmatic
contract; they are part of Wicket's component-tree-coordinate scheme
and re-resolve per session.

No published Solr field dictionary. The Apache Wicket front-end
exposes form fields named like `advancedInputWrapper:advancedInputsList:1:advancedInputSearchPanel:input`
(application number, applicant, publication date, etc.) — useful as a
hint, not as a contract.

The same `?query=OFCO:PH` mechanic also works on the regional ASEAN
Register at [`ip-register.aseanip.org/wopublish-search/public/...`](https://ip-register.aseanip.org/wopublish-search/public/home),
which IPOPHL itself operates as Country Lead for ASEAN IT tools (see
§9 below).

---

## 4. Pagination

**HTML pagination via Wicket postbacks.** The result-list pages have a
`paginatorSlideForm` Wicket form; navigation goes through the same
component-coordinate URLs. There is **no `start=`/`rows=` Solr
query parameter exposed** at the public URL — the Solr surface is
proxied through Wicket, not pass-through.

Practical implication for a hypothetical proxy: every page beyond the
first would require POSTing the prior page's Wicket form state. This
is the same brittleness as the AT see.ip Next.js Server Actions case
in [`at-opa.md`](at-opa.md) and the DPMA WebForms case.

---

## 5. Response Shape

**HTML only — no JSON / XML response document.** The list pages are
server-rendered HTML with embedded result tables. Each result links to
a detail page at `/wopublish-search/public/detail/{module}?id={pubnum}`
which is also HTML. WIPO Publish in some deployments exposes export
endpoints (CSV/XLS), but at IPOPHL's instance no export link is
visible on the public list page.

The legacy "user-selection" mechanic (`userSelectionForm` Wicket form)
lets a logged-in user mark results for download — but it is a UI
workflow, not a documented API. No primary source publishes a
JSON/XML schema for IPOPHL's WIPO Publish instance.

---

## 6. Coverage Scope

What WIPO Publish at IPOPHL indexes — by Solr-counted bucket on
`OFCO:PH` 2026-05-18:

| Module | Count (OFCO:PH) | Notes |
|---|---|---|
| Patents | **82,327** | Includes invention patents + published applications |
| Utility Models | (in patents bucket per WIPO Publish convention) | PH UMs registered without substantive examination |
| Industrial Designs | **24,141** | National designs (separate from Hague IRs) |
| Trademarks | **791,043** | All TMs published or registered |

Total across the three modules ≈ **897k records on `OFCO:PH`**.

**Higher-layer substitutes already in our stack:**

- **PH patents (biblio + family + legal events):** EPO OPS via
  [`patent_client_agents.epo_ops`](../../../src/patent_client_agents/epo_ops/).
  Philippines is a PCT contracting state and an EPC contracting party
  via the EPO partner-office network; PH national filings are covered
  in INPADOC at biblio + legal-events fidelity. Same path as the
  AT case.
- **PH patents national collection in PATENTSCOPE:** Per the
  [PATENTSCOPE data-coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)
  row 60, Philippines data is loaded with a **twice-monthly** refresh,
  coverage **30.12.1899 → 17.11.2025**, last loaded **22.01.2026**.
  This is the canonical machine-actionable PH patent surface today
  for PCT and PCT-designating-PH filings.
- **PH trademarks (TMview + ASEAN TMview):** PH joined TMview in
  2013 ([TMDN news](https://www.tmdn.org/network/-/philippines-joins-tmview))
  contributing ~325k records at launch, growing to the current 791k
  national TMs. IPOPHL itself is the **Country Lead for the ASEAN
  IT Tools** (ASEAN TMview, ASEAN DesignView, ASEAN TMclass) per the
  [IPOPHL handover announcement](https://www.ipophil.gov.ph/news/the-ipophl-takes-over-management-of-asean-it-tools-on-intellectual-property/) —
  meaning IPOPHL operates these regional EUIPO-hosted feeds for the
  other ASEAN offices too. The proxy substrate is EUIPO's TMDN
  (`tmdn.org`).
- **PH trademarks (WIPO Global Brand Database):** Mirrored since 2013
  ([WIPO news](https://www.wipo.int/en/web/global-brand-database/w/news/2013/news_0003)),
  ~300k records at launch, currently the global aggregator of choice.
  Coverage page: [`branddb.wipo.int/en/coverage`](https://branddb.wipo.int/en/coverage).
- **PH designs (ASEAN DesignView, EUIPO DesignView):** Per the same
  ASEAN-tool footprint; PH is one of 9 ASEAN states in the regional
  feed. PH is **NOT** a Hague Agreement contracting state per the
  [WIPO Hague members list](https://www.wipo.int/hague/en/members/),
  so PH-only designs sit in IPOPHL's national register + ASEAN
  DesignView; Hague IRs do not designate PH (yet — accession is
  under PH government study per IPOPHL public statements).
- **PH copyright register:** [IPOPHL Copyright Search](https://onlineservices.ipophil.gov.ph/CopyrightSearch/)
  is HTML behind Incapsula WAF — bot 403; no API; PH copyright
  registration is voluntary under RA 8293 § 191.

**Genuine national-only gaps that have no programmatic substitute:**

- **PH utility models** — a real PH right with shorter (7-year)
  term, no substantive novelty examination. Per the
  [IPOPHL utility model overview](https://www.ipophil.gov.ph/services/utility-model/).
  Indexed in WIPO Publish; not extracted into a standalone bucket.
  PATENTSCOPE national collection should capture published UMs.
- **PH copyright register entries** — PH is a Berne member so most
  copyright is automatic; the IPOPHL voluntary register is the only
  national index. WAF-walled; no API.
- **PH BLA (Bureau of Legal Affairs) decisions** — IPOPHL's quasi-
  judicial body for IP disputes (opposition, cancellation,
  inter partes). [BLA Notices Publication index](https://onlineservices.ipophil.gov.ph/blapublication/)
  is WAF-walled; not exposed by any higher layer.
- **PH plant-variety register** — administered by the Bureau of Plant
  Industry under DA-NSIC (not IPOPHL); see the [DA-NSIC PVP](https://nsic.da.gov.ph/)
  reference. Not in IPOPHL surfaces at all.
- **PH file history (prosecution document images)** — not in any
  WIPO Publish detail page observed; would live in eInventionFile /
  eDocFile behind authentication.

---

## 7. Rate Limits / Quotas

**Not published.** No primary source documents API rate limits because
no API is offered. The WIPO Publish UI is presumably subject to
ordinary anti-abuse throttling at the IIS / WAF layer. The IPOPHL
e-services Incapsula WAF immediately 403s bot user agents — a
proxy operating at scale would trip the same WAF if it ever served
data sourced from that subdomain.

---

## 8. Terms of Service

The WIPO Publish "About" page at IPOPHL points to the [**WIPO global
technical-assistance terms**](http://www.wipo.int/global_ip/en/activities/technicalassistance/termsandconditions.html)
which govern the software license between WIPO and the IP Office.
These terms govern the **software**, not the **data** in the IP
Office's instance. The data ToS is whatever IPOPHL has published.

Probes 2026-05-18 of [`www.ipophil.gov.ph`](https://www.ipophil.gov.ph/)
did not surface a top-level "data licence" or "open-data licence"
statement comparable to data.gov.sg's
[Singapore Open Data Licence](https://data.gov.sg/open-data-licence)
or the UK Open Government Licence. The IPOPHL Privacy Policy
([`/privacy-policy/`](https://www.ipophil.gov.ph/privacy-policy/) per
WordPress site map) governs personal data handling. The
public-register data itself has no published reuse licence — the
default is that public registry information is publicly accessible
under the IP Code (RA 8293), but commercial redistribution by a third
party at scale is not blessed by any primary source we located.

**Bottom line on ToS:** No documented prohibition on programmatic
read (unlike AT's Impressum, which explicitly forecloses commercial
reuse), but no explicit permission either. The absence of a published
reuse licence is itself a soft-yellow signal — building a hosted
proxy substrate without an explicit licence would carry the same
posture risk we noted for `cn-cnipa.md`.

---

## 9. Operational Notes

- **Language.** IPOPHL works in **English** as its primary language
  of administration (Filipino is co-official under the 1987 PH
  Constitution but English is the working language for IP filings,
  examination, decisions, and the WIPO Publish UI).
- **WIPO Publish deployment age.** IPOPHL launched WIPO Publish on
  **17 September 2018** per [IPOPHL news](https://www.ipophil.gov.ph/news/ipophl-deploys-new-patent-search-tool/).
  Stack is **Apache Wicket** + Solr + IIS 10 reverse proxy, with
  internal Solr at `10.10.0.125:9092` (leaked in resource URL). The
  about page identifies WIPO Publish v1.4.0b at IPOPHL; the regional
  ASEAN Register instance is similar.
- **IPOPHL is the regional ASEAN Country Lead.** Per the
  [ASEAN IT-tools handover announcement](https://www.ipophil.gov.ph/news/the-ipophl-takes-over-management-of-asean-it-tools-on-intellectual-property/),
  IPOPHL operates ASEAN TMview, ASEAN DesignView, and ASEAN TMclass
  for the other ASEAN member offices. This is operationally
  significant — IPOPHL is *the* office that feeds EUIPO TMDN for the
  ASEAN region. The regional consolidated register at
  [`ip-register.aseanip.org`](https://ip-register.aseanip.org/wopublish-search/public/home)
  uses the same WIPO Publish stack and same `OFCO:PH` Solr filter.
- **Incapsula WAF on `onlineservices.ipophil.gov.ph`.** All e-services
  (eTMfile, eInventionFile, eUMFile, eIDFile, eCorr 2.0, eDocFile,
  CopyrightSearch, blapublication, blanotices, blahearingsched,
  copyrightdomain) return **403** to common Mozilla/curl user-agent
  strings without Incapsula's JavaScript challenge — confirmed by
  probes. The institutional CMS at `www.ipophil.gov.ph` (WordPress)
  is not WAF-walled.
- **WIPO Publish at IPOPHL is not WAF-walled.** Probes from US egress
  (Texas) hit `wipopublish.ipophil.gov.ph` cleanly with default curl,
  no challenge, no geofencing detected.
- **DragonPay payment integration.** IPOPHL's online filing routes
  through [DragonPay](https://www.dragonpay.ph/) for fee collection —
  a third-party PH PSP. Not relevant for our zero-infra proxy; filing
  is out of scope.
- **No federated identity (no Singpass equivalent).** Unlike SG's
  CorpPass/Singpass gating, PH's online services use IPOPHL-issued
  accounts (eCorr 2.0) bootstrapped from email. Foreign filer access
  is documented in the [eTMfile FAQ](https://www.ipophil.gov.ph/help-and-support/trademark/etmfile-for-trademarks-faqs/).
- **PATENTSCOPE coverage is materially current.** Per [data-coverage
  table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)
  row 60: Philippines national collection refreshed **22.01.2026**,
  covering **up to 17.11.2025** — a ~3-month lag from publication.
  This is materially better than the SG data.gov.sg patent endpoint
  (frozen Aug 2018 → Oct 2020) and is comparable to PATENTSCOPE
  coverage of other ASEAN national collections.
- **WIPO Standards ATR/PI/2022/PH and ATR/ID/2023/PH and ATR/TM/2024/PH.**
  IPOPHL files Annual Technical Reports with WIPO ST.6 / ST.9 (patent
  / TM data exchange) per the [WIPO ATR series](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640671101/CWS+ATR+TM+2024+PH).
  This confirms IPOPHL participates in the WIPO standards-based data
  exchange — the data flow we exploit transitively via PATENTSCOPE.
- **PH IP Code (Republic Act 8293).** The substantive law. Mirrored
  free on [LawPhil RA 8293 page](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html)
  (Lawphil Project, Arellano Law Foundation — non-government but
  comprehensive and free). Also on the
  [Official Gazette](https://www.officialgazette.gov.ph/1997/06/06/republic-act-no-8293/)
  (but bot 403 from US egress) and at the
  [IPOPHL administrative-issuances tree](https://www.ipophil.gov.ph/administrative-issuances/).

---

## 10. Verdict

| Right | Verdict | One-sentence reason |
|---|---|---|
| **Patents** | 🔴 **Red — covered transitively** | PATENTSCOPE national collection refreshes twice/month with ~3-month lag, EPO INPADOC covers PH at biblio+family+legal-events; IPOPHL's own WIPO Publish is HTML-only with Wicket pagination — not a viable proxy substrate. |
| **Utility models** | 🔴 **Red — covered transitively** | PH UMs flow into PATENTSCOPE under the PH national collection (same WIPO ST.6 data exchange that carries patents); no separate API. |
| **Trademarks** | 🔴 **Red — covered transitively** | EUIPO TMview + WIPO Global Brand Database carry the full PH TM register (~791k records on the IPOPHL Solr side; ~325k+growth on TMview since 2013); IPOPHL itself is the regional Country Lead operating ASEAN TMview on EUIPO's TMDN infrastructure. |
| **Designs** | 🔴 **Red — covered transitively (regional only)** | ASEAN DesignView + EUIPO DesignView carry PH designs; PH is **not** a Hague contracting state so no Hague IR coverage layer; pure-PH designs live in IPOPHL WIPO Publish + ASEAN DesignView. |
| **Copyright** | 🔴 **Red — no path** | IPOPHL voluntary register is HTML behind Incapsula WAF returning 403 to bots; no API; PH copyright is automatic under Berne so register is non-authoritative anyway. |
| **Plant variety** | n/a — not IPOPHL | Administered by Bureau of Plant Industry under DA-NSIC, not IPOPHL. |
| **Substantive law (RA 8293)** | 🟢 **Green — static-corpus material** | RA 8293 + IPOPHL Implementing Rules & Memorandum Circulars are static text published on [lawphil.net](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html) and the IPOPHL administrative-issuances tree — same static-corpus shape as `ipo_in_statutes`, `dpma_statutes`, `legifrance_ip`, `tw_trade_secrets`, `sg_statutes` (proposed). |

**Overall:** **🔴 Red — `red_no_api` (register-side).** IPOPHL
publishes **no public register API** (REST, JSON, XML, SOAP, or
otherwise), is not listed in the [WIPO IP API Catalog](https://apicatalog.wipo.int/),
and its only programmatic-looking surface (WIPO Publish at
`wipopublish.ipophil.gov.ph`) is server-side-rendered HTML with
Wicket pagination — not a viable proxy substrate. **However** the
red verdict is materially softened by an unusually deep transitive
coverage stack: PATENTSCOPE national collection (twice-monthly,
~3-month lag) covers PH patents and UMs; EUIPO TMview / ASEAN
TMview / WIPO Global Brand Database all carry the PH TM register
(IPOPHL is the regional Country Lead operating ASEAN TMview on
EUIPO's TMDN); EPO INPADOC carries PH patent biblio + family +
legal events. The genuine PH-national-only gaps are PH copyright
voluntary-register entries, IPOPHL BLA decisions, and pure
prosecution file-history images — all WAF-walled, no API, no
transitive substitute. The decision is **locked**: do not build a
hosted proxy of IPOPHL surfaces; rely on PATENTSCOPE + EUIPO + WIPO
for register reads; ship a small `ph_statutes` static corpus for
RA 8293 + IRRs + Memorandum Circulars. Strategic memory: revisit
only if IPOPHL announces a developer programme (monitor
[`www.ipophil.gov.ph/news/`](https://www.ipophil.gov.ph/news/)).
