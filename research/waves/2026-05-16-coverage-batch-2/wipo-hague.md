# WIPO Hague System — API discovery for a zero-infra proxy connector

Research date: 2026-05-16
Entity: `WO/WIPO/Hague` (multilateral, industrial designs)
Scope: Determine whether the **Hague System itself** — distinct from the
broader Global Design Database — exposes any public, queryable
REST/JSON/XML API surface we could call live from our connector with no
hosted index, no bulk corpus, and no offline mirroring. Specifically
asked to probe **Hague Express** at
[`https://www.wipo.int/hague/en/express/`](https://www.wipo.int/hague/en/express/)
and the **eHague** portal, the **International Designs Bulletin**, and
the **Hague System Fee Calculator**.

Sibling waves: the 2026-05-16 Global Design Database investigation
([`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../2026-05-16-registered-ip-discovery/wipo-global-databases.md))
already established that the WIPO Global Design Database is ToS-blocked
and that **Hague Web Services (HWS)** — the only WIPO-catalog API in the
design domain — is an IP-office-only filing back-end, not a search API.
This wave looks one level deeper at the **Hague system surfaces directly**.

The headline up front: **RED**. WIPO does not expose a public, third-party-
callable REST/JSON search API for Hague IRs. The Hague Express UI is the
only free public search surface, and `wipo.int/robots.txt` (verified
2026-05-16 via `curl`) explicitly disallows machine access to its query
paths — `/designdb/*?`, `/designdb/*/jsp`, `/designdb/jsp`. The
International Designs Bulletin offers a per-issue XML download, but it is
scoped to IP offices that perform substantive review and violates our
"no offline corpus" rule. **Hague Web Services**, **eHague**, and the
fee calculator are all filer-side (or IP-office-side) workflow surfaces,
not search.

---

## 1. Endpoint

The Hague System has three categories of programmatic-or-near-programmatic
surfaces. None of them is a public, third-party-callable search API.

### 1.1 Hague Express (the actual IR search UI)

Hague Express — confusingly — refers to two coexisting pages:

- The marketing entry point at
  [`https://www.wipo.int/en/web/hague-system/design_search`](https://www.wipo.int/en/web/hague-system/design_search)
  ("Hague Express Database — Search International Designs", verified
  2026-05-16, HTTP 200, served by Liferay).
- The actual application at
  [`https://designdb.wipo.int/designdb/hague/en/`](https://designdb.wipo.int/designdb/hague/en/)
  (canonical app entry; verified 2026-05-16, HTTP 200; the same JSF/JSP
  pipeline that powers the Global Design Database with the `collection=Hague`
  filter applied; help at
  [`/designdb/hague/en/designdb-help.jsp`](https://designdb.wipo.int/designdb/hague/en/designdb-help.jsp)).

The Hague Express search UI is **a stateful JSP/JavaScript application**.
The compiled bundle (`designdb-all.16015.min.js`, fetched 2026-05-16,
1.37 MB) references the internal backend paths `showData`, `/branddb/`,
`/designdb/`, `/search`, `apiEvents`, and `XMLHttpRequest` — i.e. there
is an internal AJAX search API behind the UI, but:

1. It is **not documented as a public API anywhere on wipo.int**.
2. The internal search path is explicitly blocked by
   [`wipo.int/robots.txt`](https://www.wipo.int/robots.txt) which on 2026-05-16
   contains these lines:

   ```
   Disallow: /designdb/jsp
   Disallow: /designdb/*/showData.jsp
   Disallow: /designdb/*/jsp
   Disallow: /designdb/*?
   ```

3. Probing `https://designdb.wipo.int/designdb/search?q=*&collection=Hague&start=0&rows=1`
   on 2026-05-16 returned **HTTP 404** with an HTML body — the public
   search endpoint shape is not callable directly.

4. The Global Design Database (which Hague Express is the Hague-only
   filtered view of) is explicitly ToS-blocked for automated queries —
   see §1.7 / §1.8 of
   [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../2026-05-16-registered-ip-discovery/wipo-global-databases.md).

There is **no documented JSON/XML/Atom programmatic surface** for Hague
Express. The "Express" name in WIPO usage refers to the weekly-refresh
cadence of the underlying International Register data, not to a
machine-friendly API.

### 1.2 Individual IR detail (Hague Express record view)

The Hague Express UI surfaces individual IRs at URLs of the form
`https://designdb.wipo.int/designdb/showData.jsp?ID=HAGUE.<IR-number>&...`,
but these are explicitly listed in robots.txt under
`Disallow: /designdb/*/showData.jsp`, are HTML-only (no JSON
representation in `Accept: application/json` content negotiation —
verified by `curl` 2026-05-16; the server returns the same HTML), and
inherit the Global Design Database ToS (§2.1 forbids automated queries).

### 1.3 International Designs Bulletin

[`https://www.wipo.int/en/web/hague-system/bulletin/notes`](https://www.wipo.int/en/web/hague-system/bulletin/notes)
and
[`https://www.wipo.int/en/web/hague-system/bulletin/help`](https://www.wipo.int/en/web/hague-system/bulletin/help)
describe the official publication of the Hague System, published weekly
on Fridays at noon CET (per [the 2024 redesign news item](https://www.wipo.int/en/web/hague-system/w/news/2024/browsing-and-searching-the-international-designs-bulletin-is-easier-than-ever)).

The Bulletin includes a **per-issue XML download** in the
[ST.96 v4.0 XML standard](https://www.wipo.int/standards/en/st96/v4-0/),
explicitly intended for "intellectual property offices of Hague System
contracting parties that perform substantive review of international
registrations" (per the WIPO news item linked above). It is not framed as
a third-party API. Each weekly issue ships as an XML bundle, not as a
query endpoint — using it to answer a per-user query would require
ingesting every issue and indexing locally, which violates our
zero-infra constraint.

### 1.4 eHague (filer portal)

[`https://hague.wipo.int/`](https://hague.wipo.int/) is the **filer-facing
portal**: filing applications, paying renewals, downloading workbench
documents (per the
[2022 "Download Documents Directly from your Workbench" news](https://www.wipo.int/en/web/hague-system/w/news/2022/news_0021)
and the
[eHague filing tutorial](https://www.wipo.int/en/web/hague-system/ehague-filing-tutorial)).
It requires a WIPO account, is scoped to the filer's own portfolio, and
has no public search surface.

### 1.5 Hague Web Services (HWS)

WIPO API Catalog entry idAPI 158 (probed 2026-05-16 at
[`https://apicatalog.wipo.int/api/apis/all`](https://apicatalog.wipo.int/api/apis/all)):

> "**Hague Web Services (HWS)** — HWS are a secure, highly-available,
> reliable, HTTPS/REST API-based protocol for exchanging data with the
> Hague System. They can be used for sending or receiving data."
> Spec URL: [`https://www3.wipo.int/confluence/x/IACaTw`](https://www3.wipo.int/confluence/x/IACaTw)
> (WIPO Confluence — IP-office-only access).

The October 2021 HWS overview PDF
([`https://confluence.wipo.int/confluence/download/attachments/1335492640/Hague%20Web%20Services_e-2.pdf`](https://confluence.wipo.int/confluence/download/attachments/1335492640/Hague%20Web%20Services_e-2.pdf))
and the 2022 [HWS bidirectional-exchange presentation](https://www.wipo.int/edocs/mdocs/hague/en/wipo_it_id_ge_22/wipo_it_id_ge_22_presentation.pdf)
confirm HWS is a **machine-to-machine bidirectional data exchange** for
**participating IP offices** — sending decisions, receiving applications,
querying processing status, retrieving Bulletins, retrieving confidential
copies (Examining IP Offices only). Authentication uses **Financial-grade
API Security Profile 1.0** asymmetric-key signatures.

HWS is **not a search API** and is **not available to third parties**.
The catalog tag for HWS matches the same restricted-subscription axis as
the GBD Image-related API ("Usage restricted to collaborating IP
Offices").

### 1.6 Hague System Fee Calculator

[`https://www.wipo.int/en/web/hague-system/fees/calculator`](https://www.wipo.int/en/web/hague-system/fees/calculator)
is a **web UI only** (verified 2026-05-16, HTTP 200, 141 KB Liferay page
with embedded JavaScript widget). No documented JSON endpoint, no
machine-readable fee CSV, and the underlying state of the calculator
appears to be client-side JS reading static fee tables from the page.
The schedule itself is on
[`/fees/sched`](https://www.wipo.int/en/web/hague-system/fees/sched) as
HTML (see §4 below for the snapshot).

## 2. Auth

| Surface | Auth |
|---|---|
| Hague Express UI (`designdb.wipo.int`) | None for human use; explicitly off-limits to bots per ToS + robots.txt |
| International Designs Bulletin XML | None to download a weekly issue; but intended audience is IP offices doing substantive review |
| eHague filer portal | WIPO account (filer-specific, scoped to own portfolio) |
| Hague Web Services (HWS) | Asymmetric-key signature, FAPI 1.0 — **partner IP offices only** |
| Fee calculator / fee schedule | None (public HTML pages) |

No free-tier developer key for any search-style surface.

## 3. Query language

There is no documented machine query language for Hague IRs. The Hague
Express UI supports search by IR number, holder name, designation
contracting party, Locarno class, status, date ranges, and product
indication (per the
[Hague Express Help](https://designdb.wipo.int/designdb/hague/en/designdb-help.jsp)
page) — but only via the human-facing JSP form.

The International Designs Bulletin browse UI at
[`/bulletin/browse-by-bulletin`](https://www.wipo.int/en/web/hague-system/bulletin/browse-by-bulletin)
(redirected to from [`/bulletin`](https://www.wipo.int/en/web/hague-system/bulletin)
in some link paths) supports advanced search criteria, search by IR
number, and archive browse 2004–2011, per
[the 2024 redesign news](https://www.wipo.int/en/web/hague-system/w/news/2024/browsing-and-searching-the-international-designs-bulletin-is-easier-than-ever).
Still UI-only.

## 4. Pagination

UI-only. The Hague Express UI inherits the Global Design Database
**100-records-per-query download cap** documented at
[`https://www.wipo.int/en/web/global-design-database/faqs_designdb`](https://www.wipo.int/en/web/global-design-database/faqs_designdb)
("Only up to 100 results can be downloaded"). No documented cursor or
offset pagination machine surface.

## 5. Response shape

- **Hague Express UI:** HTML (and report exports as PDF / Excel via
  human-click). The internal AJAX surface returns HTML-snippets keyed on
  JSF view state; it is not a JSON API in any usable sense.
- **International Designs Bulletin:** ST.96 v4.0 XML per weekly issue
  (download), plus HTML browse UI. No per-IR query JSON.
- **HWS:** REST/JSON payloads in ST.96 — but partner-only.
- **Fee schedule:** HTML tables on
  [`/fees/sched`](https://www.wipo.int/en/web/hague-system/fees/sched);
  no JSON.

## 6. Coverage scope

The Hague System administers international design registrations under
the 1934 (terminated), 1960, and 1999 Acts of the Hague Agreement.

- **Members:** 80 contracting parties covering 97 countries as of late
  2024 (per the
  [Hague System main page](https://www.wipo.int/en/web/hague-system));
  82 / 99 per
  [Hague Yearly Review 2025 Executive Summary](https://www.wipo.int/web-publications/hague-yearly-review-2025-executive-summary/en/hague-yearly-review-2025-executive-summary.html);
  Saudi Arabia accession announced 2025
  ([news](https://www.wipo.int/en/web/hague-system/w/news/2025/saudi-arabia-joins-the-hague-system)).
  The task input cites "79 / 96" which appears slightly stale; current
  WIPO primary sources give 80–82 members and 97–99 countries.
- **Backfile depth:** Hague Express includes bibliographic data and
  reproductions for **published international registrations with a
  registration date from January 3, 1985** onward (per the
  [Hague Express info-kit page](https://www.wipo.int/hague-system-information-kit/en/index.html)
  and the [Design DB FAQ](https://www.wipo.int/en/web/global-design-database/faqs_designdb)).
  Pre-1999 records are best-effort.
- **Refresh cadence:** Weekly (with the Bulletin), per
  [the 2024 redesign news](https://www.wipo.int/en/web/hague-system/w/news/2024/browsing-and-searching-the-international-designs-bulletin-is-easier-than-ever).
- **Designations:** Each IR can designate any of the contracting parties;
  Hague Express surfaces all designations + their per-country legal
  status as supplied by national offices.

The Hague System annual filing volume is in the low five-figures of IRs
per year (see [Hague Yearly Review 2025](https://www.wipo.int/web-publications/hague-yearly-review-2025-executive-summary/en/hague-yearly-review-2025-executive-summary.html)),
so the total population is on the order of low hundreds of thousands of
IRs across the full backfile — small relative to PATENTSCOPE or the
Madrid system.

## 7. Rate limits / quotas

The Global Design Database — which Hague Express is a filtered view of —
applies the same boilerplate WIPO database ToS as PATENTSCOPE and the
Brand DB, with a documented **10-search-actions-per-minute-per-IP**
threshold (per
[Global Design Database Terms of Use](https://www.wipo.int/en/web/global-design-database/terms_and_conditions)
§2.1) and a documented **24-hour IP-block enforcement** (per the
[Design DB FAQ](https://www.wipo.int/en/web/global-design-database/faqs_designdb):
"our robot detection mechanism might mistake you for a robot and block
your IP address for 24 hours at most").

## 8. Terms of service

The Hague Express UI inherits the **Global Design Database Terms of Use
(November 2022)** at
[`https://www.wipo.int/en/web/global-design-database/terms_and_conditions`](https://www.wipo.int/en/web/global-design-database/terms_and_conditions),
which §2.1 forbids:

> "use the service excessively to the detriment of other Users (for that
> matter, **more than 10 search related actions per minute from a single
> IP address can be considered excessive**); **perform automated queries**;"

§2.2 forbids redistributing data without WIPO permission; §2.4 reserves
the right to block abusive use.

The Hague Express info-kit page (see §6 above) and the Design DB FAQ
both reaffirm: "our terms of use specifically disallow any kind of bulk
or automatic downloading of data from our system."

Additionally, `wipo.int/robots.txt` (verified 2026-05-16) **explicitly
disallows machine access to the Hague Express query and detail paths**:

```
Disallow: /designdb/jsp
Disallow: /designdb/*/showData.jsp
Disallow: /designdb/*/jsp
Disallow: /designdb/*?
```

Proxying user Hague queries live from our connector would violate both
the ToS (§2.1, automated-queries clause) and the robots.txt machine-
access prohibition on the query path.

## 9. Operational notes

- The Hague Express data backing is the same Solr-style index that backs
  the Global Design Database. There is no Hague-specific public API
  separable from the Global Design Database surface — Hague Express is
  a `collection=Hague` filter on top of the same UI.
- The **International Designs Bulletin XML feed** is the closest thing
  to a structured data surface, but it is per-issue weekly XML
  (not query) and is scoped to IP offices doing substantive review. It
  would require a hosted index on our side to answer per-IR queries —
  violating the zero-infra constraint.
- **HWS** is a real REST/JSON API and the protocol is documented at
  ST.96 v4.0 fidelity — but it is partner-only and is workflow (filing /
  decision / status notification), not search.
- **eHague** as a partial workaround: if a user has filed Hague IRs
  themselves, they can read their own portfolio through the eHague
  workbench — but only as the filer.
- **Cloud Run / data-center egress** is unusually likely to trip WIPO's
  robot detection given the documented IP-block enforcement and our
  prior observations of WAF-style filtering on adjacent WIPO hosts (see
  [`feedback_cloud_run_egress.md`](../../../feedback_cloud_run_egress.md)).
- WIPO's roadmap (per the [API Catalog for IP launch news](https://www.wipo.int/en/web/standards/w/news/2024/news_0001))
  is to publish OpenAPI specs in the
  [WIPO API Catalog](https://apicatalog.wipo.int/) as IP institutions
  register them. A future Hague search API is therefore conceivable, but
  not currently catalogued — re-check the API Catalog quarterly.

## 10. Verdict

**RED.** No public REST/JSON search API for the Hague System exists.

- Hague Express UI is the only free public search surface, and ToS
  + robots.txt **explicitly prohibit** automated queries against it.
- HWS is partner-only and is filing-side, not search.
- eHague is filer-portal scope.
- The International Designs Bulletin XML is a bulk per-issue download
  scoped to IP offices doing substantive review — violates zero-infra.
- The Fee Calculator is HTML-only with no documented machine surface.

There is no path under the stated constraints. Connector strategy: do
**not** plan to proxy Hague System queries live. Cover Hague-related
needs via (a) the **WIPO Lex** corpus for the Hague Agreement statute
text itself (where a tractable connector exists), and (b) national
design connectors for designs that have been nationalized through Hague
(IP Australia Designs, EUIPO, USPTO design patents, etc.). Re-check the
WIPO API Catalog at
[`https://apicatalog.wipo.int/`](https://apicatalog.wipo.int/) quarterly
for a potential future "Hague Search API" listing — as of 2026-05-16
the only Hague entry is HWS (filing, partner-only).
