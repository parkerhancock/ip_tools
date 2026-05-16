# TIPO Taiwan — Wave research (2026-05-16)

**Entity:** `TW/TIPO` — Taiwan Intellectual Property Office (智慧財產局, Ministry of Economic Affairs)
**Rights:** patent, utility model, design (one Patent Act); trademark; (separate copyright registry — out of scope here)
**Constraint under test:** zero-infrastructure proxy of a live REST API.
**Date verified:** 2026-05-16

---

## §1 Endpoint

TIPO ships a real REST OpenData API. The base URL — and the path documented in the older 2026-05 survey — has moved:

| What | Where (2026-05-16, verified) |
|---|---|
| OAS spec (Swagger 2.0) | [`GET https://cloud.tipo.gov.tw/S220/opdata/api/file/oas`](https://cloud.tipo.gov.tw/S220/opdata/api/file/oas) — 179 KB, served as `OpenData_API.json` |
| Live API base | `https://cloud.tipo.gov.tw/S220/opdataapi/api/` |
| Bulk portal SPA | [`https://cloud.tipo.gov.tw/S220/opdata`](https://cloud.tipo.gov.tw/S220/opdata) |
| New patent search UI (iPKM, replaces TWPAT) | [`https://cloud.tipo.gov.tw/S400`](https://cloud.tipo.gov.tw/S400) — launched 2024-12-18; old TWPAT scheduled offline 2025-04-25 per [TIPO News 2025-05-15](https://www.tipo.gov.tw/en/tipo2/363-22677.html) |

**Drift from older survey:** the older [`connectors/tipo_taiwan.md`](../../connectors/tipo_taiwan.md) lists the API base as `https://tiponet.tipo.gov.tw/Gazette/OpenData/OD/OD05.aspx?QryDS=API00`. That host **301-redirects to `cloud.tipo.gov.tw/S220/opdata?QryDS=API00`** today, and the legacy English news page [`tipo.gov.tw/en/cp-282-600217-88d54-2.html`](https://www.tipo.gov.tw/en/cp-282-600217-88d54-2.html) now returns "the website has been redesigned, please use https://www.tipo.gov.tw." API path/host has consolidated under cloud.tipo.gov.tw.

### 15 OAS-documented operations (all GET, biblio-only)

From parsing the live OAS at `/api/file/oas`:

**Patents (8 ops):**
- `GET /PatentAppl` — 專利申請案IPC/LOC及第1申請人國籍資訊 (filings + IPC/LOC + first-applicant nationality). `applclass` param: 1=invention, 2=utility model, 3=design.
- `GET /PatentPub` — 發明公開案 (invention publications: publication number, IPC, applicant/inventor/agent names)
- `GET /PatentRights` — 專利權狀態異動資料 (legal status events: licence/cancel/revoke/charge-expir/opposition/nullity flags)
- `GET /PatentPriority` — 專利優先權案
- `GET /PatentAnnuity` — 年費繳納紀錄 (annuity payment history)
- `GET /PatentAlteration` — 讓與紀錄 (assignment records)
- `GET /PatentDivide` — 分割案
- `GET /PatentTwins` — 一案兩請 (Taiwan one-application-two-rights cross-references; UM+invention dual-track)
- `GET /PatentChange` — 改請案

**Trademarks (6 ops):**
- `GET /TmarkAppl` — registration applications (Nice class, image URL, agent, applicant)
- `GET /TmarkRights` — rights-status events
- `GET /TmarkPriority` — priority claims
- `GET /TmarkPics` — image gallery (PNG/JPG hosted on `cloud.tipo.gov.tw/S282/...`)
- `GET /TmarkDivide` — divisional records
- `GET /TmarkChange` — assignment records

**Designs:** no dedicated operation; reachable through `/PatentAppl?applclass=3` and `/PatentRights?applclass=3` since the Patent Act covers designs.

Verified live with the public demo `tk` token `43b47d07-4795-45d9-819a-9c71c72e4105` that data.gov.tw publishes on [dataset 35466](https://data.gov.tw/en/datasets/35466) — `status: "ok"` returned with real records.

## §2 Auth

- **Mechanism:** `tk` query-string parameter (UUID-shaped per OAS field `description: "向經濟部智慧財產局申請核發，存取使用之唯一驗證碼"` — "unique authentication code issued by TIPO upon application").
- **Without `tk`:** API returns HTTP 200 with `status: "sample"`, `message: "驗證碼不通過，僅提供範例資料。驗證碼請洽智慧局申請"` ("token failed, sample data only — apply to IPO for token") and hard-caps at 25 rows. Useful for endpoint smoke-tests but not production.
- **How to register:** download the docx form at [`cloud.tipo.gov.tw/S220/opdata/api/information/file/api-register-form-docx`](https://cloud.tipo.gov.tw/S220/opdata/api/information/file/api-register-form-docx) (verified live, 22 KB Microsoft Word 2007+), fill in user/contact/software-purpose/industry, email to **`ipoid@tipo.gov.tw`**. No portal-based signup, no online OAuth flow. Form is **Traditional Chinese only**.
- **Foreign-developer accessibility:** no nationality restriction listed; form supports overseas address + English contact. No primary source confirming explicitly that foreigners receive `tk`, but data.gov.tw publishes a working `tk` that is reachable from the US (CF Cloudflare edge, no geofencing observed). Empirically the API responded normally from a US-egress proxy on 2026-05-16.

## §3 Query language

Per-endpoint structured parameters declared in the OAS. Representative subset for `/PatentAppl`:

| Param | Type | Purpose |
|---|---|---|
| `format` (required) | string | `JSON` or `XML` |
| `tk` (required) | string | auth token |
| `top` | integer | rows per page (max **6,000**, verified empirically) |
| `skip` | integer | offset |
| `orderby` | string | sort column |
| `applclass` | integer | 1=invention / 2=UM / 3=design |
| `applno` | string | application number |
| `applbdate` / `appledate` | string | filing date range |
| `ipcfull`, `ipcsection`, `ipcclass`, `ipcsubclass`, `ipcmaingroup`, `ipcgroup` | string | IPC hierarchical filter |
| `locfull`, `loclevel1`, `loclevel2` | string | Locarno (design) classification |

`/PatentPub` adds `noticeno`/`noticebdate`/`noticeedate`/`patentname`/`applnamec`/`applnamee`/`inventornamec`/`inventornamee`/`agentnamec`. `/TmarkAppl` adds `tmarkname`/`tmarkclass`/`tmarktype`/`tmarkcolor`/`goodclasscode`/`applcountry`/`agentname`.

**No free-text full-text search.** Field-only matching. No boolean operators, no proximity, no truncation — pure parameterised filter. For Chinese-language full-text patent search, the user is routed to the iPKM UI at `cloud.tipo.gov.tw/S400`.

## §4 Pagination

Standard `top` (page size) + `skip` (offset) — Microsoft OData / REST-classic shape.

- Empirically verified caps:
  - Without `tk`: `top` silently clamped to 25 regardless of requested value.
  - With `tk`: `top` honored up to **6,000**; `top=10000` returns `status: error`, `message: "此API查詢筆數上限為6,000筆，請設定參數top=6,000後再進行查詢"` ("this API has a query-row limit of 6,000; set top=6,000 or lower").
- Total-row count returned in `total-count` field — paginate by walking `skip += 6000`.
- No cursor / continuation-token model. Pure offset pagination, which means large traversals are O(n²) on the server side.

## §5 Response shape

Both JSON and XML negotiated by the `format` query param.

JSON shape (verified `/TmarkPriority?tk=…&top=2`):

```jsonc
{
  "version": "1.0",
  "status": "ok",                // or "sample" / "error"
  "message": "",
  "top": 2,
  "skip": 0,
  "order-by": "appl-no",
  "total-count": 70984,
  "tmarkpriority": {
    "-page-count": 2,
    "-create-date": "2026/05/17",
    "tmarkrightscontents": [
      {
        "-sequence": 1,
        "-tmark-right-url": "ftps://ftp.tipo.gov.tw/ftp/TmarkRights/000/TmarkRights_1_00083309.xml",
        "tmarkcontent": [{
          "appl-no": "065001166",
          "tmark-class": "1", "tmark-class-desc": "商標",
          "exam-no": "00083309",
          "tmark-name": "ＳＴＯＸＩＬ（墨色）",
          "priorities": { "priority-date": "1996/09/06", "priority-country-code": "US", … }
        }]
      }, …
    ]
  }
}
```

**Key surprise:** every list response includes a `-tmark-right-url` (or `-patent-right-url`) pointer to an **FTPS** URL (`ftps://ftp.tipo.gov.tw/...`) where the per-record full XML detail lives. So the REST surface returns biblio-summary; deeper detail is on an FTPS host. A pure HTTPS proxy would expose the biblio fields; FTPS fetches would need a separate transport. The MOJ-style ZH-translation-only Wayback story does **not** apply here — but the FTPS handoff is non-trivial.

OAS schema models 15 definitions; the largest (`TmarkAppl`) has only 8 top-level properties — confirms biblio-only scope. No `abstract`, no `claims`, no `description` text fields, no `figures`. Zero occurrences of `abstract` / `fulltext` / `claim` in the OAS spec.

## §6 Coverage scope

Empirically verified `total-count` values returned from the API on 2026-05-16:

| Operation | Total rows | Coverage |
|---|---|---|
| `/PatentAppl` | 1,451,147 | All filings (invention + UM + design combined) — backfile to **1972** (oldest filing date observed: `appl-no=06202104`, `appl-date=1972/07/26`) |
| `/PatentRights` | 916,697 | Granted-rights register, legal-status events |
| `/TmarkAppl` | 3,386,403 | Trademark filings — backfile to **1951** (oldest: `appl-no=000000001`, `appl-date=1951/02/27`, `tmark-name=林森`) |
| `/TmarkPriority` | 70,984 | TM priority claims only |

Coverage is bibliographic + rights/status only. **No full text, claims, specifications, drawings, or office-action documents are exposed through the API.** Patent figures, claims text, and prosecution file wrappers remain UI-only on iPKM (`cloud.tipo.gov.tw/S400`).

## §7 Rate limits / quotas

- **Not documented** anywhere on the portal or OAS. The English news pages, registration form, and OAS contain no rate-limit clause.
- Empirical probe (10 rapid sequential requests with the demo `tk`): all 200, p50 ≈ 0.4 s, no 429s. CF edge cache likely absorbing repeated identical queries.
- Page-size cap: **6,000 rows per request** (verified — see §4).
- No per-key or per-IP daily quota referenced in any primary source. Quotas are likely enforced at TIPO discretion case-by-case during the email-application review; the OAS treats `tk` as opaque.

## §8 Terms of service

The portal's data are released under the **Taiwan Open Government Data License v1.0** ([data.gov.tw/license](https://data.gov.tw/license)). Each TIPO dataset page on data.gov.tw (e.g. [#35466 — TM priority](https://data.gov.tw/en/datasets/35466)) cites this license.

Key clauses (verbatim from the English text on data.gov.tw/license):

> **§2.1** "The Data Providing Organization grants User a perpetual, worldwide, non-exclusive, irrevocable, royalty-free copyright license to reproduce, distribute, publicly transmit, publicly broadcast, publicly recite, publicly present, publicly perform, compile, adapt to the Open Data provided **for any purpose**, including but not limited to making all kinds of Derivative Works either as products or services."
>
> **§2.2** "User can **sublicense** the copyrights which he/she is granted through 2.1 to others."
>
> **§4.2** "The License is compatible with the **Creative Commons Attribution License 4.0 International**."
>
> **§3.2** "When User makes use of the Open Data and its Derivative Work, he/she must make an explicit notice of statement as **attribution** requested in the Exhibit … If User fails to comply with the attribution requirement, the rights granted under this License shall be deemed to have been void ab initio."

**Verdict on ToS for our use:** explicitly green for proxy-and-redistribute, provided we surface a TIPO/MOEA attribution string in our response envelope. CC-BY-4.0-compatible is unusual and unambiguous — better than UKIPO's "no clear license", better than CNIPA (no license).

## §9 Operational notes

- **Language:** Traditional Chinese (zh-Hant) for all field values that aren't structured codes. The OAS itself, registration form, news pages, and error messages are all Chinese-primary; English TIPO news pages exist but the API help text isn't translated. Field *names* in the JSON are English (`appl-no`, `tmark-name`, `priority-country-code`), but the *content* is Chinese (`tmark-name: "林森"`, `appl-country: "中華民國"`). Translation pairs are not exposed — applicant English name is a separate field (`appl-name-e`) that's often null for domestic applicants.
- **Geofencing:** none observed. CF edge in DFW served all requests; no Taiwan-residency check.
- **Network surface:** REST is HTTPS via Cloudflare. The per-record detail XMLs that responses point to are on **FTPS** (`ftps://ftp.tipo.gov.tw/`). A proxy that needs detail records must speak FTPS — not just HTTP.
- **iPKM migration (drift from older survey):** the legacy **TWPAT family is being retired**. iPKM at `cloud.tipo.gov.tw/S400` is the new patent search UI launched 2024-12-18 ([TIPO News](https://www.tipo.gov.tw/en/tipo2/363-22677.html)); old TWPAT was scheduled offline 2025-04-25. iPKM is Next.js / `_next/static/chunks` — a SPA — but no OpenData-style API on the iPKM `/S400/` path was found. The OpenData REST surface at `/S220/opdataapi/api/` is unaffected.
- **Anti-bot:** none on the API itself (no captcha, no JS challenge). The TWPAT UI had a `TTS_AntiProxy` cookie gate (per old survey), which is moot now that the UI is being retired. The bulk-portal SPA does require a captcha for some operations (`/api/captcha/uuid`, `/api/captcha/generate` referenced in the JS bundle), but those are for bulk-file feedback submission, not for `tk`-authenticated API queries.
- **Token model:** `tk` appears in the URL query string, which is non-ideal for logging hygiene but consistent with other Asian gov APIs (KIPRIS Plus `ServiceKey`, J-PlatPat).

## §10 Verdict

🟢 **GREEN** for a TIPO biblio + status proxy, with explicit scope ceilings.

**One-sentence reasoning:** TIPO ships a real Swagger 2.0–documented REST API at `cloud.tipo.gov.tw/S220/opdataapi/api/` with 15 endpoints covering patent/UM/design + trademark biblio, priority, status, annuity, and assignment data, under a CC-BY-4.0-compatible Taiwan Open Government Data License that explicitly permits sublicensing — zero infrastructure on our side beyond an HTTP client and a `TIPO_API_KEY` env var, **subject to** the constraint that the API is biblio/status-only (no full text/claims/drawings) and the auth flow is a Word-form email request to `ipoid@tipo.gov.tw` rather than a self-service portal.

**Caveats that keep this from being "perfect green":**

1. **No full text/claims/specifications/figures.** For agent workflows that need claim language or prior-art passages, the API is insufficient and the iPKM UI scrape would be required — explicit out-of-scope.
2. **`tk` provisioning is email + docx**, not self-service. First-user-on-the-team latency is days, not minutes; renewal/rotation cycle unknown. Foreign-developer success rate not documented.
3. **Detail records sit on FTPS** (`ftps://ftp.tipo.gov.tw/`), not the same HTTPS host. A pure HTTP proxy won't reach them. Acceptable to ship a biblio-only v1 and skip the detail pointer.
4. **Chinese-only field content** for everything that isn't a structured code. English bibliographic data exists in dedicated fields (`appl-name-e`, `inventor-name-e`) but is often empty for domestic applicants. An EN-only agent workflow needs upstream translation or graceful degradation.

**Verdict basis:** verified live on 2026-05-16 — OAS download, sample-mode probe without `tk`, authenticated probe with the public demo `tk` from data.gov.tw, pagination cap empirical, ToS confirmed on data.gov.tw/license.

---

## Drift summary vs. older survey ([`connectors/tipo_taiwan.md`](../../connectors/tipo_taiwan.md))

| Older claim | 2026-05-16 finding | Drift? |
|---|---|---|
| Base URL `tiponet.tipo.gov.tw/Gazette/OpenData/OD/OD05.aspx` | 301-redirects to `cloud.tipo.gov.tw/S220/opdata` — same destination, new canonical host | ✏️ correct |
| OAS at `DownLoadFiles/OpenData_API.json` | Now served at `cloud.tipo.gov.tw/S220/opdata/api/file/oas` (same JSON content, with `Content-Disposition: attachment; filename="OpenData_API.json"`) | ✏️ correct |
| Auth = `apiKey` header per publicapi.dev | Auth is `tk` query parameter, **not** an HTTP header. publicapi.dev listing was wrong. | 🔴 corrected |
| TWPAT is the main UI | TWPAT scheduled offline 2025-04-25; **iPKM at cloud.tipo.gov.tw/S400 is the replacement** as of 2024-12-18 | 🔴 corrected |
| English news page at `tipo.gov.tw/en/cp-282-600217-88d54-2.html` | Now returns 404 / "site has been redesigned" — old slug killed during 2024 redesign | 🔴 corrected |
| TIPO API "Closest equivalent to USPTO ODP" | Confirmed — biblio + status only, no full text. Slightly narrower scope than ODP (no file-history equivalent) | ✏️ confirmed |
| ToS unclear / "explicit redistribution terms … need a read" | Resolved — **Taiwan OGDL v1.0, CC-BY-4.0 compatible, sublicensing explicitly permitted** | ✅ resolved |
| Rate limits "not documented in English" | Still not documented; page-size cap of 6,000 rows discovered empirically. Daily/per-key quota still unknown. | ✏️ partial |
| publicapi.dev says "no rate limits" | Misleading — there *is* a 6,000-row-per-request cap. | 🔴 corrected |
