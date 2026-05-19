# DIP Thailand (TH) — Patents, Petty Patents, Trademarks, Designs, Copyright, GI API Discovery

**Date:** 2026-05-18
**Scope:** Determine whether the Department of Intellectual Property
(DIP / กรมทรัพย์สินทางปัญญา, under the Ministry of Commerce, Royal
Thai Government) exposes a public, queryable REST/JSON/XML API we can
proxy at runtime with zero infrastructure on our side. Bulk dumps and
HTML-only surfaces would be **red**; per-user BYOK with a paper-
contract registration would be **yellow**; undocumented-but-
unauthenticated JSON would be **green**.

**TL;DR:** **Yellow — a real REST/JSON API exists, but it's a BYOK
contract surface.** DIP runs a documented "Data Exchange / ระบบ
แลกเปลี่ยนข้อมูล" platform at
[`api.ipthailand.go.th/data-exchange/`](https://api.ipthailand.go.th/data-exchange/view/home.aspx)
cataloguing **21 published REST APIs** across **all six DIP rights**
(invention patents, design patents, petty patents / utility models,
trademarks, copyright, geographical indications) plus statistics. The
API surface is unambiguous: per-API rows expose `API_NAME_ENG`,
`API_URL`, `API_METHOD` (mostly POST, one GET), version, last-updated
date, and a documented request/response schema served from the same
ASP.NET WebForms portal (`DIP_DESCRIPTION_Detail_LookupView.aspx`).
Authentication is **Bearer-token** issued after a two-step approval:
(a) register at
[`api.ipthailand.go.th/data-exchange/Register.aspx`](https://api.ipthailand.go.th/data-exchange/Register.aspx)
and (b) post a paper request letter to DIP's Information and
Communication Technology Center within 30 days; on approval, DIP
emails a token. That's the same paper-contract pattern as **DPMA's
DPMAconnectPlus** and **KIPO's KIPRIS Plus** — yellow against our
zero-infra constraint because the credential is per-org and the
contract is offline-bound. Consumer search hosts
(`patentsearch.ipthailand.go.th`, `tmsearch.ipthailand.go.th`,
`search.ipthailand.go.th`, `exchange.ipthailand.go.th`) are **Cloudflare
Turnstile-challenged** or **Incapsula-walled**; institutional
`ipthailand.go.th` is Incapsula. Thailand has **zero entries in the
[WIPO IP API Catalog](https://apicatalog.wipo.int/)** (probed 179
APIs across 10 IPOs, no TH). Transitive coverage: **WIPO PATENTSCOPE
TH national collection — 191,367 records**, biblio + abstracts
13.08.1980 → 08.12.2025, last loaded 22.01.2026 (per the
[Data Coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)
row 76); **EUIPO TMview** carries DIP's >960k Thai trademarks since
the DIP integration milestone; **ASEAN TMview / ASEAN DesignView**
on EUIPO TMDN aggregates TH together with the other 8 ASEAN states
(PH-operated as Country Lead, per our [PH synopsis](../../national/ph-ipophl.md)
§3); **WIPO Madrid Monitor** covers IRs designating TH since
TH's accession 2017-11-07. **WIPO Hague does NOT cover TH** —
accession is in legislative pipeline (Patent Act amendments approved
by Parliament 2022-11-29; cabinet IP Work Plan 2025-08-26) but not
yet ratified as of 2026-05.

**Verdict: 🟡 Yellow.** A genuine REST/JSON surface exists with a
formal contract path. Worth a connector in **planned/BYOK** mode
(per-deployment-org token), mirroring the DPMA/KIPO pattern. The
substantive-law layer (Patent Act B.E. 2522, Trademark Act B.E. 2534,
Copyright Act B.E. 2537, etc.) is reachable cleanly at
[`www.ocs.go.th`](https://www.ocs.go.th/) (the new krisdika.go.th
host, redirected since the OCS rebrand) and via WIPO Lex —
a **green** static-corpus adjunct.

---

## 1. Endpoint

DIP's surface is sharded across institutional, register-search,
filing, and data-exchange hosts. Each was probed 2026-05-18 from US
egress.

| Surface | Host | Right(s) | Stack | Probe |
|---|---|---|---|---|
| Institutional | [`www.ipthailand.go.th`](https://www.ipthailand.go.th/) | content + statutes PDFs | Static HTML behind Incapsula | 200 OK, 212-byte Incapsula `/_Incapsula_Resource?...` iframe |
| Patent register search | [`patentsearch.ipthailand.go.th`](https://patentsearch.ipthailand.go.th/) | patent, design, petty patent | Cloudflare Turnstile + ASP.NET WebForms (`DIPSearch/PatentSearch/SearchComplex.aspx`, `SearchIPC.aspx`) | 403 with 5.5 KB Cloudflare "Just a moment..." challenge HTML |
| Trademark register search | [`tmsearch.ipthailand.go.th`](https://tmsearch.ipthailand.go.th/) | trademark | Same Cloudflare + WebForms | 403 / 5.5 KB challenge |
| TM image search | [`search-tm.ipthailand.go.th`](https://search-tm.ipthailand.go.th/portal) | trademark | Cloudflare-walled | 403 / 5.5 KB challenge |
| Unified DIP search | [`search.ipthailand.go.th`](https://search.ipthailand.go.th/) | unified | Incapsula | 200 / 212-byte iframe |
| **Data Exchange catalogue + portal** | [`api.ipthailand.go.th/data-exchange/`](https://api.ipthailand.go.th/data-exchange/view/home.aspx) | patent / design / petty patent / TM / copyright / music-copyright / GI / statistics | **ASP.NET behind Cloudflare cf-cache-status=DYNAMIC** (catalogue is reachable to bot egress) | 200 OK, 84,715-byte HTML cataloguing 21 published APIs |
| Data Exchange register | [`api.ipthailand.go.th/data-exchange/Register.aspx`](https://api.ipthailand.go.th/data-exchange/Register.aspx) | self-service registration | ASP.NET WebForms | 404 to anonymous bot UA (form requires session bootstrap) |
| Data Exchange logged-in search | [`api.ipthailand.go.th/data-exchange/loginsearch.aspx`](https://api.ipthailand.go.th/data-exchange/loginsearch.aspx) | per-token API query UI | ASP.NET WebForms | Auth-walled |
| E-Exchange documentation | [`exchange.ipthailand.go.th/manual`](https://exchange.ipthailand.go.th/manual) | user manual | Cloudflare-walled to bot UA | 403 / 5.5 KB challenge |
| DIP e-Service (filings) | [`eservice.ipthailand.go.th`](https://eservice.ipthailand.go.th/login) | filings | Angular SPA | 200 / Angular shell |
| DIP SSO | [`sso.ipthailand.go.th`](https://sso.ipthailand.go.th/) | identity / DIP CA | Cloudflare-walled | 403 / 5.5 KB challenge |
| Service portal | [`portal.ipthailand.go.th`](https://portal.ipthailand.go.th/) | identity portal | Cloudflare-walled | 403 / 5.5 KB challenge |
| Statutes mirror (formerly krisdika) | [`www.ocs.go.th`](https://www.ocs.go.th/) | Office of the Council of State law portal | Apache 2.4 / PHP 7.3 / HTML | 200 / 165 KB clean HTML (no WAF) |

The actual API base URL for each of the 21 published APIs is **not
api.ipthailand.go.th itself** — the catalogue's per-row `API_URL`
field carries the operational base for each API, served by the
catalogue's `getformbody` / `GetField` endpoints. Probe of
`/api/Search/V_API_TM2` against `api.ipthailand.go.th` returns 404
(ARR/3.0 / ASP.NET); the live operational hosts are
catalogue-resolved per API at request time. This is the same shape
as DPMA's `DPMAconnectPlus` portal-then-host indirection.

The 21 catalogued APIs (extracted from the home page DOM, 2026-05-18):

| Code | Service (TH) | View ID | Method |
|---|---|---|---|
| A0001 | บริการข้อมูลลิขสิทธิ์ (Copyright data service) | `V_API_CPR` | POST |
| A0002 | บริการข้อมูลลิขสิทธิ์เพลง (Music-copyright data service) | `V_API_CPRSONG` | POST |
| A0003 | บริการข้อมูลสิ่งบ่งชี้ทางภูมิศาสตร์ (GI data service) | `V_API_GI` | POST |
| A0005 | บริการข้อมูลสิทธิบัตรออกแบบ (Design patent data service) | `PATENT_TYPE2_2021` | POST |
| A0006 | บริการข้อมูลอนุสิทธิบัตร (Petty-patent / utility-model service) | `PATENT_TYPE3_2021` | POST |
| A0007 | บริการข้อมูลเครื่องหมายการค้า (Trademark data service) | `V_API_TM2` | POST |
| A0013 | บริการข้อมูลสถิติยื่นรับจดทะเบียนของเครื่องหมายการค้า (TM filing/registration statistics) | `V_REQ_REG` | POST |
| A0015 | ค้นหาข้อมูลคำขอเครื่องหมายการค้า (TM application search) | — | GET |
| A0019 | บริการข้อมูลสิทธิบัตรการประดิษฐ์ (Invention-patent data service) | `PATENT_TYPE1_2021` | POST |
| A0021 | บริการสถิติยื่นคำขออนุสิทธิบัตรตามจังหวัด (Petty-patent stats by province) | `V_PTPETTY_REQUEST_PROVINCE` | POST |
| A0022 | บริการ สถิติการจดแจ้งลิขสิทธิ์ จำแนกตามจังหวัด (Copyright recordal stats by province) | `V2_CPR_AREA_REQUEST` | POST |
| A0023 | บริการ สถิติการยื่นขอเครื่องหมายการค้า จำแนกตามจังหวัด (TM-filing stats by province) | `V2_TRADEMARK_REQUEST_AREA` | POST |
| A0024 | บริการ สถิติรับจดทะเบียนสิทธิบัตรการประดิษฐ์ จำแนกตามจังหวัด (Invention-patent grants by province) | `V_PT_REGISTER_PROVINCE` | POST |
| A0025 | บริการ สถิติรับจดทะเบียนสิทธิบัตรการประดิษฐ์ จำแนกตามสัญชาติ (Invention-patent grants by nationality) | `V_PT_REGISTER_NATION` | POST |
| A0026 | บริการ สถิติยื่นจดทะเบียนสิทธิบัตรการประดิษฐ์ จำแนกตามจังหวัด (Invention-patent filings by province) | `V_PT_REGISTER_PROVINCE` | POST |
| A0027 | บริการ สถิติยื่นจดทะเบียนสิทธิบัตรการประดิษฐ์ จำแนกตามสัญชาติ (Invention-patent filings by nationality) | `V_PT_REGISTER_NATION` | POST |
| A0028 | บริการ สถิติรับจดทะเบียนสิทธิบัตรการออกแบบ จำแนกตามจังหวัด (Design-patent grants by province) | `V_PTDESIGN_REGISTER_PROVINCE` | POST |
| A0029 | บริการ สถิติรับจดทะเบียนสิทธิบัตรการออกแบบ จำแนกตามสัญชาติ (Design-patent grants by nationality) | `V_PTDESIGN_REGISTER_NATION` | POST |
| A0030 | บริการ สถิติยื่นจดทะเบียนสิทธิบัตรการออกแบบ จำแนกตามจังหวัด (Design-patent filings by province) | `V_PTDESIGN_REQUEST_PROVINCE` | POST |
| A0031 | บริการ สถิติยื่นจดทะเบียนสิทธิบัตรการออกแบบ จำแนกตามสัญชาติ (Design-patent filings by nationality) | `V_PTDESIGN_REQUEST_NATION` | POST |
| A0034 | บริการข้อมูลสิทธิบัตรประดิษฐ์ ออกแบบ อนุสิทธิบัตร (Unified patent chatbot service) | `API_PATENT_CHATBOT` | POST |

Coverage class: 6 register-data APIs (A0001/A0002/A0003/A0005/A0006/
A0007/A0019/A0034), 1 TM-application search (A0015), 1 unified
patent chatbot (A0034 overlaps A0005/A0006/A0019 — likely the
LLM-grounding feed), 12 statistical APIs (A0013/A0021–A0031). Most-
recent update flag observed: A0006/A0007 last refreshed
**25 October 2024 (พ.ศ. 2567)**; A0034 (chatbot) refreshed
**13 July 2023**; A0019/A0005 refreshed **3 March 2023**. The
register-data services are the live operational layer; the
statistical services are aggregate counts useful for landscape work
but not per-record retrieval.

---

## 2. Auth

**Bearer-token, paper-contract, BYOK.** Verbatim from the catalogue
home page text (translated):
> "Contacting to request API service can be registered via the
> system by clicking the Register button. Send a written letter
> expressing intent to use the API service to the Department of
> Intellectual Property" (paraphrased from
> [`api.ipthailand.go.th/data-exchange/view/home.aspx`](https://api.ipthailand.go.th/data-exchange/view/home.aspx)).

Web-search-resolved manual content
([`exchange.ipthailand.go.th/manual`](https://exchange.ipthailand.go.th/manual),
Google-indexed because the host is bot-walled to direct curl):
> "After registration, users must submit a request letter through
> mail to the Information and Communication Technology Center at
> the Department of Intellectual Property within 30 days. Once the
> department receives and approves the API usage request, they will
> notify the applicant via email, and users can then access the
> system to view the Token key details. The API uses Bearer token
> authentication in the header format, such as `Bearer {tokenkey}`."

Procedurally:
1. Online registration at
   [`Register.aspx`](https://api.ipthailand.go.th/data-exchange/Register.aspx).
2. Mail a request letter to DIP's Information and Communication
   Technology Center (ศูนย์เทคโนโลยีสารสนเทศและการสื่อสาร) at
   563 Nonthaburi 1 Rd, Bang Krasor, Mueang Nonthaburi 11000,
   Thailand. Hotline 1368.
3. Approval and token-issuance via email.
4. Token used as `Authorization: Bearer {tokenkey}` on each
   request; request bodies are JSON.

Foreign-developer accessibility: no published prohibition on
foreign applicants; the registration form is in Thai but DIP's IP
Information Centre handles English correspondence (as in PCT/Madrid
work). No DIP precedent for hosted-SaaS redistribution agreements —
this is per-org credentialling, identical posture to **DPMA
DPMAconnectPlus** and **KIPO KIPRIS Plus**.

Catalogue confirms also a probable internal-only IDA / JWT layer:
`DIP_DESCRIPTION_Detail_LookupView.aspx/GetData` accepts an
integer `idapi` and returns the per-API metadata blob (request
schema, response schema, parameters). Anonymous probe of `GetData`
with the view-name string returns:
`{"Message":"Conversion failed when converting the varchar value
'V_API_TM2' to data type int.", "ExceptionType":"System.ArgumentException"}` —
the route is open but expects the numeric primary key, which is
not exposed on the home-page DOM (only the integer A-codes A0001–
A0034 are visible; the internal `idapi` is a different sequence).

---

## 3. Query Language

Per-API. The catalogue serves a per-API JSON schema via
`getformbody` / `GetField` calls (visible in the home-page DOM).
Each register-data API publishes a **request body schema** ($
parameter fields) and a **response body schema** ($ field names,
data types, Thai + English labels) that the catalogue UI renders.
Public schema introspection requires a valid `idapi` numeric.
Reasonable inference from the public catalogue + standard ASP.NET
WebForms pattern: structured-field POST bodies (e.g. for `V_API_TM2`:
trademark application number / registration number / class /
applicant name / status / date range), JSON-in / JSON-out, no
documented free-text or Lucene grammar.

No GraphQL, no SPARQL, no SDMX. No OData. No `$filter` operator.

---

## 4. Pagination

Not specified in the public catalogue. Per-API pagination scheme is
discoverable only post-token. The catalogue lists `API_REQUEST` and
`API_RESPONSE` schemas inside `DIP_DESCRIPTION_Detail_LookupView.aspx`
but those bodies are only fetchable with the numeric `idapi`.

---

## 5. Response Shape

Documented as JSON, served from ASP.NET WebForms. Sample-record
inspection blocked by the same numeric-key gate. The catalogue UI
includes a "preview" rendering element (`#formexampleapi` in the
home-page JS), implying each API has a documented example response
body the portal renders for authenticated users.

---

## 6. Coverage Scope

### What DIP would expose via the published APIs (per-right)

DIP administers the full TH IP system under the Ministry of
Commerce:

- **Invention patents** ("สิทธิบัตรการประดิษฐ์") — 20-year term under
  the [Patent Act B.E. 2522 (1979)](https://www.wipo.int/wipolex/en/legislation/details/3807),
  amended by Act (No. 2) B.E. 2535 (1992) and Act (No. 3)
  B.E. 2542 (1999). Draft amendments approved by Parliament
  2022-11-29 (Hague-accession enabler).
- **Design patents** ("สิทธิบัตรการออกแบบผลิตภัณฑ์") — 10-year term,
  same Patent Act.
- **Petty patents / utility models** ("อนุสิทธิบัตร") — 6-year initial
  term + 2×2-year renewals, lower inventiveness threshold; closest
  analogue to a German Gebrauchsmuster. Specifically catalogued
  under A0006 in the Data Exchange API.
- **Trademarks** ("เครื่องหมายการค้า") —
  [Trademark Act B.E. 2534 (1991)](https://www.wipo.int/wipolex/en/legislation/details/3812)
  as amended through 2016 Madrid-Protocol enablement.
- **Geographical Indications** ("สิ่งบ่งชี้ทางภูมิศาสตร์") —
  [GI Act B.E. 2546 (2003)](https://www.wipo.int/wipolex/en/legislation/details/3833).
- **Copyright** ("ลิขสิทธิ์") —
  [Copyright Act B.E. 2537 (1994)](https://www.wipo.int/wipolex/en/legislation/details/3839)
  as amended. Voluntary recordal at DIP; rights arise on creation
  under Berne.
- **Music copyright** ("ลิขสิทธิ์เพลง") — subset of copyright with a
  dedicated API (A0002) reflecting DIP's distinct music-rights
  business process.
- **Trade Secrets** ("ความลับทางการค้า") —
  [Trade Secrets Act B.E. 2545 (2002)](https://www.wipo.int/wipolex/en/legislation/details/3835).
  No public register; not catalogued in Data Exchange.
- **Layout-Designs of Integrated Circuits** ("แบบผังภูมิของวงจรรวม") —
  Act B.E. 2543 (2000). Niche; not catalogued in Data Exchange.
- **Plant Variety Protection** — administered by **Department of
  Agriculture** under MOAC, not DIP. Out of DIP scope.

### What's reachable transitively (already shipped or queued)

- **WIPO PATENTSCOPE Thailand national collection** — **191,367
  records**, biblio + abstracts 13.08.1980 → 08.12.2025, latest
  load 22.01.2026 (per
  [Data Coverage table row 76](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)).
  Materially current (~6-week lag). No chemical data, no document
  images, no OCR. Covers both invention patents and design patents;
  petty-patent coverage in PATENTSCOPE depends on whether DIP shares
  petty-patent data with WIPO (the PATENTSCOPE document type
  distinguishes IPC-coded inventions from non-IPC-coded utility
  models — TH petty patents may or may not appear depending on the
  WIPO data-exchange profile).
- **EPO OPS / INPADOC** — TH is a PCT contracting state since
  2009-09-24 (`patent_client_agents.epo_ops` already ships).
  INPADOC carries TH national filings and PCT national-phase entries
  at biblio + family + legal-events fidelity.
- **EUIPO TMview** — DIP joined TMview with >960k Thai trademarks
  per the [Thailand-joins-TMview announcement](https://www.tmdn.org/network/-/thailand-joins-tmview).
  TH TMs are also visible via **ASEAN TMview** (EUIPO TMDN, PH-
  operated as ASEAN Country Lead — see [PH synopsis](../../national/ph-ipophl.md) §3).
- **EUIPO ASEAN DesignView** — TH industrial designs aggregated
  with the other 8 ASEAN states. Same EUIPO TMDN stack.
- **WIPO Madrid Monitor** — international TM IRs designating TH
  since accession 2017-11-07
  ([WIPO Madrid news, Aug 2017](https://www.wipo.int/en/web/madrid-system/w/news/2017/news_0015)).
  TH was the 99th Madrid member.
- **WIPO Hague System** — **does NOT currently designate TH.** Draft
  Patent Act amendments enabling Hague accession were approved by
  the Thai Parliament 2022-11-29 and reaffirmed in the
  National IP Policy Committee's IP Work Plan 2025-08-26
  ([Tilleke summary](https://www.tilleke.com/insights/thailands-progress-toward-joining-hague-agreement/19/));
  ratification pending as of 2026-05.
- **WIPO Global Brand Database** — carries the Madrid IR slice
  designating TH but does not currently mirror the TH national-only
  TM collection.
- **WIPO Lex Thailand profile** —
  [`https://www.wipo.int/wipolex/en/profile.jsp?code=TH`](https://www.wipo.int/wipolex/en/profile.jsp?code=TH) —
  catalogues all primary TH IP statutes in English.

### What's not reachable anywhere outside DIP (true national-only gap)

- **TH-only national trademarks** — pre-2017-11-07 TH national-only
  TMs (no Madrid IR alternative) and post-2017 TH-only TMs filed
  directly with DIP rather than via Madrid. Reachable via the Data
  Exchange API A0007 (BYOK) or via EUIPO TMview (free, aggregator).
- **TH petty patents / utility models** ("อนุสิทธิบัตร") — A0006 is
  the direct surface; PATENTSCOPE coverage is dependent on WIPO's
  data-exchange profile.
- **TH-only national industrial designs** (no Hague IR because TH
  isn't a Hague member yet) — reachable via the Data Exchange API
  A0005 or via EUIPO ASEAN DesignView.
- **TH copyright voluntary recordals** ("การจดแจ้งลิขสิทธิ์") — A0001;
  music-copyright recordals — A0002. No higher-layer mirror.
- **TH geographical indications** — A0003. No higher-layer mirror
  beyond the EU-Thailand GI bilateral protocols.
- **Full prosecution detail** (file history, examiner reasoning,
  office actions, opposition proceedings, Patent Board / Trademark
  Board decisions) — not in the Data Exchange catalogue. Reachable
  only through DIP's filing-side portals
  (`eservice.ipthailand.go.th`, `bis.ipthailand.go.th`,
  `patentsearch.ipthailand.go.th`), which are
  Cloudflare/Incapsula-walled.

---

## 7. Rate Limits / Quotas

**No published rate limits in the catalogue.** Per-API throttles
likely exist post-token; comparison hosts (DPMA DPMAconnectPlus,
KIPO KIPRIS Plus) publish per-second/per-day envelopes only inside
the signed-in portal. Cloudflare cf-cache-status=DYNAMIC on
api.ipthailand.go.th implies CDN-edge rate-shaping but not API-key
throttling.

---

## 8. Terms of Service

No public ToS page reachable to bot egress at
`ipthailand.go.th/terms` or similar. The Data Exchange home page
text references the registration-and-letter contract as the
governing instrument; the contract terms are bilateral between DIP
and the issued-org credential holder, not published. Comparable
DPMA / KIPO contracts limit redistribution to "applicant own use"
and prohibit unaffiliated SaaS redistribution.

The **Royal Thai Government Open Data Master Plan** publishes via
[`data.go.th`](https://data.go.th/) under default Creative Commons
Attribution. DIP **publishes 12 datasets** to `data.go.th`
(confirmed via the Google-indexed listing —
[`data.go.th/en/dataset/dip0001`](https://data.go.th/en/dataset/dip0001)
is "ข้อมูลสิทธิบัตรค้นหาตามเลขทะเบียน" / "patent search by registration
number"). The portal itself is **Cloudflare-walled** to anonymous
bot egress (403 / "Access Denied" HTML at probe 2026-05-18), but
the Google-indexed dataset cards confirm the slugs
(`dip0001` … presumably through `dip0012`-shaped). Whether these
are bulk CSV/XML dumps or pointer-to-API entries was not
empirically resolvable from US egress; the
[`gdcatalog.go.th`](https://gdcatalog.go.th/) federated catalogue
([`/dataset/gdpublish-dip-010101`](https://gdcatalog.go.th/dataset/gdpublish-dip-010101)
for "สถิติการรับจดทะเบียนเครื่องหมายการค้า") suggests CKAN-shape
statistical aggregates rather than per-record register dumps.

Thailand's **Computer Crime Act B.E. 2550 (2007) as amended B.E.
2560 (2017)** creates criminal penalties for unauthorised access
to computer systems — comparable to Indonesia's UU ITE. Operating
a hosted scraper that defeats DIP's Cloudflare/Incapsula walls is
not just ToS-risky; the legal floor is higher than ordinary
TOSE.

---

## 9. Operational Notes

**Dual bot-defense.** Two distinct WAF stacks across the
`ipthailand.go.th` family:
- **Incapsula** (Imperva) on `www.ipthailand.go.th`,
  `search.ipthailand.go.th` — 212-byte iframe redirect to
  `/_Incapsula_Resource?SWJIYLWA=...`.
- **Cloudflare Turnstile** ("Just a moment...") on
  `patentsearch.`, `tmsearch.`, `search-tm.`, `exchange.`, `sso.`,
  `portal.ipthailand.go.th` — 5.5 KB challenge HTML referencing
  `challenges.cloudflare.com`.
- **api.ipthailand.go.th** is exceptionally **Cloudflare-served
  but not Turnstile-challenged** (cf-cache-status=DYNAMIC, no
  challenge HTML); this is the documented, intentionally crawlable
  Data Exchange catalogue path. Probe of `/api/Search/...` returns
  404 ASP.NET (ARR/3.0), confirming that operational API hosts are
  per-API and not at `api.ipthailand.go.th` root.

**ASP.NET WebForms underneath.** The Data Exchange catalogue is
ASP.NET WebForms (`x-powered-by: ASP.NET`, IIS/ARR 3.0). Patent
and TM search hosts are also `.aspx`-extension WebForms behind
the Cloudflare layer. This is consistent with TH government IT
procurement norms (heavy ASP.NET / SQL Server stack).

**Third-party wrapper search returned zero.** A targeted web
search (`site:github.com OR site:pypi.org "api.ipthailand.go.th"`)
returned no published Python/JS wrappers. The Data Exchange
catalogue has been live since at least 2023 (oldest API
last-update dates 2022-08-04); the absence of wrappers reflects
the per-org contracted credential gating rather than the API
being unknown.

**TM5 / ID5 / TM5+ membership.** Thailand is **not** a member of
the TM5 (USPTO/EUIPO/JPO/KIPO/CNIPA) or ID5 partner-office networks,
which is why there is no direct EUIPO IP-Office REST mirror of the
DIP TM file. EUIPO TMDN's ASEAN TMview is the proxy.

**Statute corpus is clean.** The Office of the Council of State
(formerly Krisdika) at [`www.ocs.go.th`](https://www.ocs.go.th/) is
Apache 2.4 / PHP 7.3 with **no WAF**; clean PHP-rendered HTML
catalogue of Thai statutes. The
[`librarian/elaw/elaw_external/`](https://www.ocs.go.th/) sub-tree
serves canonical PDFs of all IP acts.
**WIPO Lex Thailand profile**
([`wipo.int/wipolex/en/profile.jsp?code=TH`](https://www.wipo.int/wipolex/en/profile.jsp?code=TH))
provides English-authoritative versions of each Act — Patent Act,
Trademark Act, Copyright Act, GI Act, Trade Secrets Act, ICLD Act,
PVP Act. Also mirrored at
[`www.ipthailand.go.th/images/...Act.pdf`](https://www.ipthailand.go.th/images/633/Patent-Act-Edit.pdf)
when the Incapsula host is rendered through a browser.

**Hague accession pipeline.** Patent Act amendments enabling Hague
accession approved by Parliament 2022-11-29; National IP Policy
Committee's IP Work Plan adopted 2025-08-26 names Hague accession
as a target. As of 2026-05-18 not yet ratified. Once ratified,
international design IRs designating TH become reachable via
WIPO Hague Express — closing the design-coverage gap automatically.

---

## 10. Verdict

**🟡 Yellow — real REST API, BYOK contract surface.**

**What makes it yellow:** DIP's Data Exchange platform at
[`api.ipthailand.go.th/data-exchange/`](https://api.ipthailand.go.th/data-exchange/view/home.aspx)
is a documented, catalogued, JSON-REST surface covering all six
operational DIP rights plus statistics. Bearer-token auth, paper-
contract registration, per-org credential. Identical posture to
**DPMA DPMAconnectPlus** and **KIPO KIPRIS Plus** — connector
shippable as **planned/BYOK** with credentials supplied per
deployment org.

**What would push it red:** if redistribution restrictions in the
DIP contract turn out to be DPMA-strict (applicant-own-use only,
no SaaS redistribution). Cannot be verified without executing the
registration → letter → token flow. **Action: confirm via
DIP IT Center correspondence before committing to a connector
spec.**

**What would push it green:** a self-service token (no paper
letter) or a documented hosted-SaaS clause. Neither is signalled
in the home-page documentation.

**Surprise:** Thailand is the **first ASEAN IP office in our
survey with a documented, register-level REST API surface**.
PH (WIPO Publish HTML), ID (Incapsula-walled SPA), MY (HTML)
have nothing equivalent. DIP's 21-API catalogue is meaningful
infrastructure investment, even with the paper-contract gate.
Worth treating as a planned BYOK connector at the same priority
tier as DPMA and KIPO.

**Statutes:** **🟢 green** — Patent Act B.E. 2522, Trademark Act
B.E. 2534, Copyright Act B.E. 2537, GI Act B.E. 2546, Trade
Secrets Act B.E. 2545, Computer Crime Act B.E. 2550 — all reachable
clean at [`www.ocs.go.th`](https://www.ocs.go.th/) +
[WIPO Lex TH profile](https://www.wipo.int/wipolex/en/profile.jsp?code=TH) +
[`ipthailand.go.th/images/`](https://www.ipthailand.go.th/) statute
PDFs. Static-corpus shippable per the
`ipo_in_statutes` / `dpma_statutes` / `legifrance_ip` /
`tw_trade_secrets` pattern.

**Operational path:**

1. **Defer DIP register-side connector to BYOK planning.** Queue
   in `BACKLOG.md` as `TH/DIP/DataExchange` with `planned/BYOK`
   status. Spec a `th_dip_data_exchange` module that takes a
   `DIP_DATA_EXCHANGE_TOKEN` env var and a configurable per-API
   base URL (since the catalogue resolves the operational host
   per API at request time).
2. **Ship `th_statutes` static-corpus connector** mirroring
   `dpma_statutes`. Scope: 7 Acts (Patent, Trademark, Copyright,
   GI, Trade Secrets, ICLD, PVP if PVP is in scope) +
   ministerial regulations + DIP notifications. Primary URLs:
   WIPO Lex first (English-authoritative), ipthailand.go.th
   statute PDFs second, ocs.go.th third.
3. **Use existing transitive coverage today.** PATENTSCOPE
   (191,367 TH records, monthly lag) + INPADOC (biblio + family
   + legal events via `patent_client_agents.epo_ops`) + EUIPO
   TMview (>960k TH TMs) + ASEAN TMview/DesignView (PH-operated
   regional surface) + Madrid Monitor (post-2017-11-07 IR
   designations) gives effective TH coverage at 0 incremental
   engineering cost.
4. **Send a DIP IT Center inquiry** to validate (a) the contract
   redistribution clauses, (b) the per-API operational base URLs,
   (c) the per-API rate limits, and (d) whether foreign-developer
   credentials are issued without TH legal representation.
5. **Re-evaluate 2027-Q1** after TH Hague ratification (would
   close the design-coverage gap automatically via WIPO Hague
   Express) and after the DIP IP Work Plan 2026-2030 deliverables
   land.

**Strategic memory:** Thailand is the ASEAN exception — a real
register-level REST API exists, mediated by a paper contract. The
right posture is BYOK planned, not skipped. The substantive-law
layer is greenfield-clean and should be shipped on the standard
`StaticLawCorpus` pattern. Consumer-facing search hosts
(`patentsearch.`, `tmsearch.`, `search.`) are correctly off-limits
— Cloudflare/Incapsula-walled, no scrape posture worth taking
when the Data Exchange API is the documented path.
