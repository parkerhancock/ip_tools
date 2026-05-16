# CIPO (Canada) — Patents, Trademarks, Industrial Designs API Discovery

**Date:** 2026-05-16
**Scope:** Determine whether the Canadian Intellectual Property Office (CIPO)
exposes a public, queryable REST/JSON/XML API that we can proxy at runtime,
zero infrastructure on our side. Bulk dumps and HTML-only surfaces are a
**red** verdict.

**TL;DR:** **Red across the board.** CIPO publishes one tiny REST API (the
[TM Goods and Services Manual](https://api.ised-isde.canada.ca/en/docs?api=cipo-gsm)) —
a Nice-classification helper, not a search of trademark records. Patents,
trademarks, and industrial designs are reachable **only** as (a) interactive
HTML/JSP search portals, or (b) IP Horizons bulk SFTP/HTTP archives (weekly
XML, quarterly CSV/TXT). No query-and-fetch JSON API exists for any of the
three rights.

---

## 1. Endpoint

The full inventory of CIPO-facing public APIs is the
[ISED API Catalogue homepage](https://api.ised-isde.canada.ca/en). As of
2026-05-16 it lists exactly three APIs across the whole department —
Federal Corporations, **TM Goods and Services Manual**, and Measurement
Canada ORA. There is no `cipo-patents`, no `cipo-trademarks`, no
`cipo-designs` API in the catalogue.

### Patents

- **Public search surface:** [Canadian Patents Database (CPD)](https://www.ic.gc.ca/opic-cipo/cpd/eng/introduction.html),
  also reachable at `https://brevets-patents.ic.gc.ca/opic-cipo/cpd/eng/...`.
- **Form action targets** (HTML, server-rendered): `/opic-cipo/cpd/eng/search/basic.html`,
  `/opic-cipo/cpd/eng/search/boolean.html`,
  `/opic-cipo/cpd/eng/search/number.html` — see
  [search menu](https://www.ic.gc.ca/opic-cipo/cpd/eng/searchMenu.html).
- **Per-patent permalink:** `https://brevets-patents.ic.gc.ca/opic-cipo/cpd/eng/patent/<number>/summary.html`
  (example: [CA 2604999](https://brevets-patents.ic.gc.ca/opic-cipo/cpd/eng/patent/2604999/summary.html)).
- **No documented REST/JSON endpoint.** No primary source found.
- **Bulk-only alternative:** [IP Horizons patent data](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/patent-data-and-images) —
  ST.96 XML weekly, CSV/TXT quarterly, SFTP or HTTPS.

### Trademarks

- **Public search surface:** [Canadian Trademarks Database](https://ised-isde.canada.ca/cipo/trademark-search/srch).
  (The legacy `www.ic.gc.ca` Trademarks search has been migrated under
  `ised-isde.canada.ca/cipo/trademark-search/`.)
- **Internal AJAX target observed in the page's JavaScript** — the search UI
  POSTs JSON to `/cipo/trademark-search/srch` with a `JSESSIONID`-bearing
  URL. This is **not** documented in the ISED API Catalogue and is **not** a
  contracted public API. Source: the served JS at
  `/cipo/trademark-search/js/search_sgl.js;jsessionid=...` contains:
  ```js
  $.ajax({
    url: fetchUrlContextPath() + "/srch",
    contentType: "application/json",
    dataType: "json",
    type: "POST",
    data,
    ...
  });
  ```
  No publication of a schema, no auth contract, no rate-limit
  documentation. Treat as an internal browser-only endpoint.
- **Documented API:** Only the
  [TM Goods and Services Manual API](https://api.ised-isde.canada.ca/en/docs?api=cipo-gsm) —
  base path `https://apigateway-passerelledapi.ised-isde.canada.ca/cipo-gsm/v1/`,
  endpoints `GET /classes`, `GET /search`, `GET /terms/{id}`. This is the
  Nice-classification term lookup used when drafting an application; it does
  **not** search any trademark records.
- **Bulk-only alternative:** [Trademarks data: applications and registrations (XML, PNG)](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademark-data-applications-and-registrations-xml-png) —
  ST.96 XML weekly + historical, PNG images. Plus
  [researcher CSV/TXT](https://open.canada.ca/data/en/dataset/4bf74760-7ae7-4c83-ace8-b84a3b9aea8d)
  on open.canada.ca, updated quarterly (`"frequency": "P3M"`).

### Industrial Designs

- **Public search surface:** [Canadian Industrial Designs Database — basic search](https://www.ic.gc.ca/app/opic-cipo/id/bscSrch.do?lang=eng) —
  Java/JSP servlet (`.do` endpoint), HTML response only.
- **No documented REST/JSON endpoint.** No primary source found.
- **Bulk-only alternative:** [Industrial design data and images (XML, PNG)](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/industrial-design-data-and-images-applications-and-registrations-xml-png) —
  weekly XML/PNG plus historical, and
  [researcher CSV/TXT](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/industrial-design-researcher-dataset-registrations-and-assignments-csv-and-txt)
  updated quarterly.

---

## 2. Auth

| Surface | Auth model |
|---|---|
| Canadian Patents Database HTML | None — anonymous browser session |
| Canadian Trademarks Database HTML | None — anonymous browser session (JSESSIONID cookie) |
| Canadian Industrial Designs Database HTML | None — anonymous browser session (JSESSIONID) |
| TM Goods and Services Manual REST | API key (`User Key`) required |
| IP Horizons HTTPS download | None for public files |
| IP Horizons SFTP automated download | Free account — [register here](https://form.simplesurvey.com/f/s.aspx?s=59f3b3a4-2fb5-49a4-b064-645a5e3a752d&ds=SFTP); see [SFTP guide](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/automating-file-transfers-ip-horizons-local-drives-using-secure-file-transfer-protocols-sftp) |

For the GSM API specifically, the ISED API Catalogue requires you to
[log in](https://api.ised-isde.canada.ca/login?lang=en) and subscribe to the
**Public Plan**, which is free and assigns a User Key automatically. Approval
not required for the public plan. The "CIPO Internal Plan" (no limits)
requires approval and is for internal government use only. Source:
[GSM API documentation page](https://api.ised-isde.canada.ca/en/docs?api=cipo-gsm).

---

## 3. Query Language

- **Patents (CPD HTML):** Boolean form supports field-typed criteria
  ([Boolean Search](https://www.ic.gc.ca/opic-cipo/cpd/eng/search/boolean.html))
  across inventor, owner, title, abstract, claims, IPC, language of filing,
  PCT, licence availability — with `AND/OR/NOT` and date-range filters.
  Output is rendered HTML hit-lists, not JSON. Source:
  [Help — General Information](https://brevets.ic.gc.ca/opic-cipo/cpd/eng/help/content/help_general_information.html).
- **Trademarks (HTML):** Multi-field form (mark text, applicant, agent,
  Vienna codes, Nice classes, status) — Boolean operators `AND/OR/NOT`
  required in CAPS. Source: the served search page at
  [trademark-search/srch](https://ised-isde.canada.ca/cipo/trademark-search/srch).
- **Industrial Designs (HTML):** Fields documented as classification code,
  classification text, client reference number, court order number,
  description, finished article, interested parties, international
  registration number, national application/registration number, proprietor.
  Source: search-help index linked from
  [Search intellectual property databases](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/search-intellectual-property-databases).
- **GSM API:** `GET /search?q=<term>&lang=en|fr` — keyword search over the
  pre-approved goods/services term list, plus `GET /classes` and
  `GET /terms/{id}` for browsing.

No CQL, no OData, no field-operator query language is exposed
programmatically for any of the three IP rights.

---

## 4. Pagination

- **HTML hit-lists** (CPD, TM, Industrial Designs): pagination is
  HTML-anchored — there is no documented cursor or page-size parameter we
  could rely on. Hit-lists are reported in the docs to cap at a few hundred
  results per query (CPD help page states searches return "a hit list" of
  matching patents; no exposed paging contract).
- **GSM API:** OpenAPI spec at
  [cipo-gsm-en.json](https://api.ised-isde.canada.ca/swagger/spec/cipo-gsm-en.json)
  defines the endpoints but the relevant pagination is via `limit`/`offset`
  query params on `/search` per the embedded spec; **note**: the
  docs page warns "some searches may result in a large dataset, which can
  cause issues using the testing functionality on this website" — i.e. no
  hard ceiling enforced server-side beyond rate limits below.
- No primary source found for hit caps on the patents, TM, or ID HTML
  search surfaces.

---

## 5. Response Shape

- **Patents, Trademarks, Industrial Designs HTML:** server-rendered HTML.
  Detail pages like
  [CA 2604999 summary](https://brevets-patents.ic.gc.ca/opic-cipo/cpd/eng/patent/2604999/summary.html)
  contain bibliographic tables in HTML — no JSON, no Atom, no machine-
  readable envelope. Scraping is the only path.
- **TM Goods and Services Manual API:** JSON. Sample shape per the OpenAPI
  spec (description block):
  ```
  GET https://apigateway-passerelledapi.ised-isde.canada.ca/cipo-gsm/v1/classes
  → list of Nice classes
  GET .../cipo-gsm/v1/search?q=software
  → list of pre-approved goods/services terms with class numbers
  GET .../cipo-gsm/v1/terms/{id}
  → single term detail
  ```
- **IP Horizons bulk:** XML (WIPO **ST.96** standard for trademarks and
  industrial designs and patents; **ST.36** also offered for patents) and
  CSV/TXT for researcher datasets. Source:
  [IP Horizons landing page](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/canadian-intellectual-property-statistics/ip-horizons-download-intellectual-property-data).

---

## 6. Coverage Scope

| Right | Coverage | Source |
|---|---|---|
| Patents | 1869 → present; "157 years" / **2,630,000+** patent documents | [CPD Introduction](https://www.ic.gc.ca/opic-cipo/cpd/eng/introduction.html) |
| Trademarks | 140+ years; **1.2 million+** Canadian trademarks | CIPO Trademarks landing pages and the [Trademarks Database introduction](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/introduction-canadian-trademarks-database/) |
| Industrial Designs | All Canadian industrial designs filed and registered, dating back to **1861** | [Industrial designs](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/industrial-designs) and CIPO IP-databases search-help |
| IP Horizons patent bulk (open.canada.ca version) | "patent documents from 1869 to February 28, 2022" on the open.canada.ca snapshot; the **live** IP Horizons feed updates weekly (ST.96) since **August 20, 2024** ("Detailed view of recently granted and issued patents: weekly updates") | [CKAN package_show](https://open.canada.ca/data/api/3/action/package_show?id=fe1dfbb9-0fc3-42ca-b2a9-6ca4c05dbac9); [IP Horizons](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/canadian-intellectual-property-statistics/ip-horizons-download-intellectual-property-data) |

---

## 7. Rate Limits / Quotas

- **TM Goods and Services Manual API — Public Plan:** 25,000 hits per day,
  20 hits per minute. Source:
  [GSM API documentation page](https://api.ised-isde.canada.ca/en/docs?api=cipo-gsm)
  (Subscription Plans → Public Plan).
- **CPD / TM / Industrial Designs HTML:** No primary source found
  documenting per-IP or per-day quotas. Servers run behind WET-BOEW with
  JSESSIONID and chatbot integration; CIPO's standard terms apply.

---

## 8. Terms of Service

- **Data licence (IP Horizons + open.canada.ca CIPO datasets):**
  [Open Government Licence – Canada (OGL-Canada v2.0)](https://open.canada.ca/en/open-government-licence-canada).
  Worldwide, royalty-free, perpetual, non-exclusive licence — including
  commercial use; permits copy, modify, publish, translate, adapt,
  distribute, with attribution. Both the patent CKAN package
  (`"license_id": "ca-ogl-lgo"`) and trademark CKAN package
  (`"license_id": "ca-ogl-lgo"`) confirm OGL-Canada via the CKAN
  `package_show` API.
- **Programmatic / proxy use:** OGL-Canada does **not** restrict mode of
  access — but it governs **the data**, not the search HTML interfaces.
  Scraping CPD/TM/ID HTML is governed by Canada.ca general
  [Terms and conditions](https://www.canada.ca/en/transparency/terms.html);
  no primary source found that specifically permits or forbids automated
  scraping at high volume, and "you must not use the Information in a way
  that suggests any official status" still applies.
- **GSM API:** governed by the ISED API Catalogue subscription terms shown
  at sign-up; the OGL-Canada also applies to the underlying data.

---

## 9. Operational Notes

- **Bilingual:** Every CIPO surface is dual English/French — search UIs,
  documentation, and API specs. The GSM API parameterizes by `?lang=en|fr`,
  and the CKAN dataset metadata is fully bilingual.
- **NGP migration (active):** CIPO launched the
  [Next Generation Patents (NGP) initiative in 2024](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/patents/mycipo-patents-what-expect)
  — modernizing 1990s-era systems. The page warns: "During the period
  following NGP go-live, CIPO was unable to process client responses
  within internal grace dates… you might observe irregularities in the
  status information of certain applications or patents." This is the
  biggest active surface-change risk: status data on the public surfaces
  is acknowledged to be partially stale during the rollout. Also note IP
  Horizons changed the patents weekly feed format on **August 20, 2024**
  (now ST.96 XML), per the IP Horizons page.
- **No documented IP allowlists / geofencing** for the public HTML
  surfaces or the GSM API; the IP Horizons SFTP host
  (`iphorizonspi.opic-cipo.ca`) requires whitelisted account creation but
  not IP whitelisting per the [SFTP guide](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/automating-file-transfers-ip-horizons-local-drives-using-secure-file-transfer-protocols-sftp).
- **Recent UI moves:** the Trademarks search moved from
  `www.ic.gc.ca/app/opic-cipo/...` to
  `ised-isde.canada.ca/cipo/trademark-search/srch`. The patents DB is still
  served from `www.ic.gc.ca` and the patents-permalink form from
  `brevets-patents.ic.gc.ca` — both currently 200-OK and active. The
  industrial designs search is still on the legacy `www.ic.gc.ca/app`
  servlet (`bscSrch.do`).
- **No primary source found** for downtime patterns or SLO targets.

---

## 10. Verdict

| Right | Verdict | One-sentence reason |
|---|---|---|
| **Patents** | 🔴 **Red** | No documented REST/JSON API; only HTML CPD search and weekly ST.96 bulk via IP Horizons. |
| **Trademarks** | 🔴 **Red** | The only published REST API is the Nice-class GSM helper, which doesn't search trademark records; actual record search is HTML-only with an undocumented internal `/srch` POST endpoint. |
| **Industrial Designs** | 🔴 **Red** | Pure legacy JSP HTML servlet (`bscSrch.do`); only ST.96 weekly bulk and CSV/TXT quarterly are available. |

---

## Executive Summary

CIPO **does not publish a queryable REST/JSON API for any of patents,
trademarks, or industrial designs.** The only public REST API in the
[ISED API Catalogue](https://api.ised-isde.canada.ca/en) that touches CIPO
is the [Trademarks Goods and Services Manual API](https://api.ised-isde.canada.ca/en/docs?api=cipo-gsm)
— a Nice-classification helper for application drafters, not a search of
trademark records. Live data is reachable only via (a) the HTML search
portals — [CPD](https://www.ic.gc.ca/opic-cipo/cpd/eng/introduction.html),
[Trademarks](https://ised-isde.canada.ca/cipo/trademark-search/srch), and
the legacy [Industrial Designs](https://www.ic.gc.ca/app/opic-cipo/id/bscSrch.do?lang=eng)
servlet — or (b) IP Horizons bulk archives (ST.96 XML weekly, CSV/TXT
quarterly), which violate our zero-infra constraint. Recommended verdict:
**🔴 Red across patents, trademarks, and industrial designs** for a
zero-infrastructure proxy connector. The biggest operational risk if we
were forced to scrape HTML anyway is the active **Next Generation Patents
(NGP)** modernization — CIPO has publicly acknowledged status-data
irregularities and is changing both URLs and back-end formats (the
weekly patents bulk feed switched to ST.96 XML on 2024-08-20). Any
HTML-scrape we built today would be a moving target through the NGP
rollout. The only zero-infra avenue that meets our bar is the **GSM API**
— useful for trademark-application drafting workflows, but it is not a
substitute for live patent/TM/design record search.
