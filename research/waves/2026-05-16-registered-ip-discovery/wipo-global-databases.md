# WIPO Global Databases — API discovery for a zero-infra proxy connector

Research date: 2026-05-16
Scope: Determine whether WIPO's three flagship global databases —
**PATENTSCOPE**, the **Global Brand Database**, and the **Global Design Database** —
expose a public, queryable REST/JSON/XML API we can call live from a Python
connector without bulk downloads, hosted indexes, or offline corpora.

Method: walked WIPO's official documentation, terms-of-use pages, FAQ pages,
the [WIPO API Catalog for Intellectual Property](https://apicatalog.wipo.int/),
the [WIPO B2B Developer Portal](https://b2b.wipo.int/catalog/all), and probed
the actual backends (`developers.branddb.wipo.int`, `public-api.branddb.wipo.int`,
`api.branddb.wipo.int`, `apicatalog.wipo.int/api/apis/all`) at runtime to
confirm what the docs say.

The headline up front: **all three databases are red**. WIPO does not publish
a free, public, programmatic search API for any of them, and the terms of use
of all three explicitly forbid automated querying. Our zero-infra constraint
cannot be satisfied for any of the three.

---

## 1. PATENTSCOPE

### 1.1 Endpoint

There is **no public REST/JSON search API for PATENTSCOPE**. The only
WIPO-published search interface is the human-facing web UI at
[`https://patentscope.wipo.int/search/en/advancedSearch.jsf`](https://patentscope.wipo.int/search/en/advancedSearch.jsf)
(a JSF / PrimeFaces app — every search is a stateful, viewstate-bound POST,
not a documented API).

The only documented programmatic surface is a **fee-based SOAP/Java client**
described on the WIPO page
[PCT Data Products and Services](https://www.wipo.int/en/web/patentscope/data/index):

> "Programmatic access via a set of Java API, based on SOAP protocol, to all
> publication documents available in the document tab of the PATENTSCOPE
> search engine. … **Price: 2000 Swiss francs per calendar year.**"
> — [wipo.int/en/web/patentscope/data/index](https://www.wipo.int/en/web/patentscope/data/index)

That product is not a search API — it returns publication documents by
identifier for batch download. There is also a smaller-scope variant (Java
SOAP) for the "Published International Application" series at CHF 600/year.

The WIPO API Catalog confirms there is no PATENTSCOPE search API published —
a probe of [`https://apicatalog.wipo.int/api/apis/all`](https://apicatalog.wipo.int/api/apis/all)
on 2026-05-16 returned 181 APIs total. The only WIPO-org entries are:

- idAPI 185 — WIPO Pearl API (terminology)
- idAPI 187 — Hague Web Services (HWS) — design filing, not search
- idAPI 188 — GBD Image-related API ("**Usage restricted to collaborating IP Offices**")
- idAPI 221 — IPCPUB (classification publication)

No PATENTSCOPE entry, no Global Brand DB search entry, no Global Design DB
search entry — primary-source confirmation from WIPO's own catalog.

### 1.2 Auth

Not applicable — no public API exists. The fee-based SOAP/Java service requires a paid subscription and authorization under WIPO's "authorized uses policy" linked from [PCT Data Products and Services](https://www.wipo.int/en/web/patentscope/data/index).

### 1.3 Query language

Free-text web UI supports CQL-style operators (`AND`, `OR`, `NOT`,
proximity, field qualifiers like `EN_TI`, `EN_AB`, `IC`, `PA`, `IN`, `PCN`,
`DP`, etc.) per the [PATENTSCOPE help](https://patentscope.wipo.int/search/en/help/fieldsHelp.jsf).
But the syntax is documented only for the web search form — not as a
machine-callable surface.

### 1.4 Pagination

UI-only pagination (server-paged JSF). No documented machine pagination.

### 1.5 Response shape

UI returns HTML; the SOAP API returns ZIP-of-TIFF + XML (per the data products page above). No JSON.

### 1.6 Coverage scope

The largest dataset in scope here, and the most painful to lose: PATENTSCOPE
covers PCT international applications plus 87+ national collections, with
weekly publication and 2024 additions including Belgium, Norway (full-text),
Malta, Monaco, GCC, and a refresh of Saudi Arabia / ARIPO / Kenya
(per the WIPO/Japio 2024 briefing
[2024e03.pdf](https://www.japio.or.jp/english/fair/files/2024/2024e03.pdf)).
The PATENTSCOPE "national collections – data coverage" page
[`/search/en/help/data_coverage.jsf`](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)
lists ~88 office rows with individual record counts (EPO 5.39M, JP 5.39M, etc.).
Third-party summaries put the total above 100 million documents; we have not
been able to confirm an exact WIPO-published total figure for 2025
(no primary source found for a single "total documents" headline number).

### 1.7 Rate limits / quotas

The [PATENTSCOPE Terms of Use (October 2025 update)](https://www.wipo.int/en/web/patentscope/data/terms_patentscope)
explicitly state in §2.1 that users are forbidden to:

> "use the service excessively to the detriment to other Users (for that matter,
> **more than 10 search related actions per minute from a single IP address
> can be considered excessive**); perform automated queries;"

That's a hard ToS prohibition on the only surface we could plausibly proxy.

### 1.8 Terms of service

[Terms of Use — PATENTSCOPE Database (last updated October 2025)](https://www.wipo.int/en/web/patentscope/data/terms_patentscope):

- §2.1 forbids "perform automated queries" and "use the service excessively"
  (more-than-10-actions/minute test).
- §2.2: "Under no circumstances may the data made available through
  PATENTSCOPE Database be sold or sublicensed by the User in any way without
  WIPO's permission."
- §2.3: "Webmasters interested in deep linking PATENTSCOPE Database from
  their website are invited to contact WIPO for authorization."
- §2.5: "WIPO reserves the right to intervene and block access … in case of
  unauthorized or abusive use of the service."

In short, proxying user queries through the JSF UI from our connector would
violate §2.1 and risk §2.5 block on our IP / Cloud Run egress.

### 1.9 Operational notes

- WIPO machine-translates titles/abstracts and OCRs claims; the ToS §4.1
  flags OCR-derived fields as error-prone.
- ToS §4.6 notes the Russian Federation national collection may contain
  data inconsistent with Ukrainian territorial integrity — a political /
  reputational caveat for any product surfacing the data.
- Per the [PCT Data Products and Services page](https://www.wipo.int/en/web/patentscope/data/index),
  the only WIPO-supported "machine" path is fee-based subscription + SFTP
  bulk + SOAP/Java, which violates our zero-infra rule.

### 1.10 Verdict

**RED.** No public REST/JSON search API. The SOAP/Java product is paid,
batch-oriented, and behind an SFTP subscription. The only public
search surface — the JSF web UI — is explicitly off-limits to "automated
queries" under WIPO's ToS, with a 10/minute IP-based threshold.

---

## 2. WIPO Global Brand Database (Trademarks)

### 2.1 Endpoint

There is **no public REST/JSON search API for the Global Brand Database**.
The public search UI lives at [`https://branddb.wipo.int/`](https://branddb.wipo.int/),
which today is gated by an **AltCha proof-of-work CAPTCHA** that issues a
session cookie before any page (including
[`/en/coverage`](https://branddb.wipo.int/en/coverage)) is served.
A fresh `curl` to either URL returns the AltCha challenge HTML and a
JavaScript handshake against
`https://api.branddb.wipo.int/captcha` + `https://api.branddb.wipo.int/dbinfo`
— i.e. there is an internal `api.branddb.wipo.int` backend, but it is not
documented and is explicitly fronted by anti-bot.

There is also a developer portal at
[`https://developers.branddb.wipo.int/`](https://developers.branddb.wipo.int/)
(Angular SPA, compiled 2025-11-06). Its JS bundle references
`https://public-api.branddb.wipo.int`. A probe of that host on 2026-05-16
returned an AWS API Gateway response: `{"message":"Missing Authentication Token"}`
(HTTP 403) — i.e. it exists, is gated, and there is no public OpenAPI doc.
The WIPO [GBD FAQ](https://www.wipo.int/en/web/global-brand-database/faqs_branddb)
makes clear that data redistribution and bulk download are not permitted; the
[WIPO API Catalog entry idAPI 188 ("GBD Image-related API")](https://apicatalog.wipo.int/)
is the only Brand DB API listed and is described as:

> "API for trademark image classification against US Design codes, Vienna 8
> and Vienna 9 classification, and for trademark image similarity search.
> **Usage restricted to collaborating IP Offices.**"

So `public-api.branddb.wipo.int` is almost certainly the IP-Office-only
image API surface, not a third-party-callable search API.

### 2.2 Auth

For the only documented Brand DB API (idAPI 188, image classification),
access is "restricted to collaborating IP Offices" — i.e. partner-only, not
a free public key. No primary source found for any free public registration
path. The web UI requires only a session cookie issued after passing the
AltCha challenge — no auth required for human use of the UI itself.

### 2.3 Query language

UI-only. The Brand DB UI supports a custom advanced search with field
qualifiers (mark text, image, applicant, holder, status, Nice class, Vienna
class, jurisdiction, dates, etc.) per
[`https://branddb.wipo.int/branddb/en/branddb-help.jsp`](https://branddb.wipo.int/branddb/en/branddb-help.jsp).
No documented machine query language.

### 2.4 Pagination

UI-only. The GBD FAQ caps **report download at 180 records** total per query
even for human use:

> "Due to our agreements with the national offices participating in the
> Global Brand Database project precluding us from redistributing data,
> **only 180 results can be downloaded**."
> — [GBD FAQ](https://www.wipo.int/en/web/global-brand-database/faqs_branddb)

### 2.5 Response shape

UI returns HTML / report PDF / report Excel. No documented JSON.

### 2.6 Coverage scope

Largest trademark dataset in the world. WIPO's January 2025 webinar
[Overview of the Global Brand Database](https://www.wipo.int/edocs/mdocs/madrid/en/wipo_webinar_branddb_2025_1/wipo_webinar_branddb_2025_1_www_641231.pdf)
and the WIPO/Japio 2025 briefing
[2025e04.pdf](https://japio.or.jp/english/fair/files/2025/2025e04.pdf)
report **70.2 million records from 87 different data sources** as of 2024,
including: international marks under the Madrid System; trademarks from
participating national/regional offices; appellations of origin and
geographical indications under the Lisbon System; 6ter emblems; WHO INNs;
and the EUIPO collection. Updated daily.

### 2.7 Rate limits / quotas

[Terms of Use — Global Brand Database (November 2022)](https://www.wipo.int/en/web/global-brand-database/terms_and_conditions) §2.1 uses
identical language to PATENTSCOPE:

> "use the service excessively to the detriment of other Users (for that
> matter, **more than 10 search related actions per minute from a single
> IP address can be considered excessive**); **perform automated queries**;"

Beyond ToS, there is an enforced robot-detection layer (AltCha CAPTCHA on
every page, plus IP blocks — see Design DB §3.9 below for the parallel
explicit "24-hour block" wording, which applies the same way here).

### 2.8 Terms of service

[Terms of Use — Global Brand Database](https://www.wipo.int/en/web/global-brand-database/terms_and_conditions):

- §2.1 forbids automated queries and excessive use.
- §2.2: data may not be sold or sublicensed without WIPO permission.
- §2.4: WIPO reserves the right to block abusive use.

The [FAQ](https://www.wipo.int/en/web/global-brand-database/faqs_branddb)
is even more direct:

> "Regarding the downloading of the Global Brand Database, our terms of use
> specifically disallow any kind of **bulk or automatic downloading of data**
> from our system."
> "As the database is a free-of-charge public service, in order to maintain
> quality of service for all, our terms of use specifically disallow
> **automatic querying**, and our terms of use also preclude automatic
> search and/or download of results."

### 2.9 Operational notes

- All `branddb.wipo.int` page loads are now gated by an AltCha
  proof-of-work CAPTCHA (observed 2026-05-16 via direct `curl`).
- The undocumented `public-api.branddb.wipo.int` is AWS API Gateway and
  rejects unauthenticated callers with `{"message":"Missing Authentication
  Token"}`.
- Data redistribution explicitly forbidden by agreement with participating
  national offices — even if we obtained API access, we would still need
  case-by-case approval to redistribute responses to our users.

### 2.10 Verdict

**RED.** No public search API exists. The one Brand DB API in WIPO's
catalog is partner-only. The web UI is explicitly off-limits to automated
querying, capped at 180 downloadable results, fronted by a real CAPTCHA, and
redistribution of responses is precluded by the underlying IP-office
agreements.

---

## 3. WIPO Global Design Database (Industrial Designs)

### 3.1 Endpoint

There is **no public REST/JSON search API for the Global Design Database**.
Public access is via the UI at
[`https://designdb.wipo.int/designdb/en/`](https://designdb.wipo.int/designdb/en/).
The only design-system API published in the WIPO catalog is
[Hague Web Services (HWS)](https://apicatalog.wipo.int/) (idAPI 187),
which the catalog description marks as a "secure HTTPS/REST API-based protocol
for **exchanging data with the Hague System**" — i.e. a filing back-end for
participating IP offices and Hague users (POST/GET for application
management, payment, legal-status, classification, and office-interaction
operations). Spec is on WIPO's internal Confluence:
[`https://www3.wipo.int/confluence/x/IACaTw`](https://www3.wipo.int/confluence/x/IACaTw).

HWS is not a search API across the Global Design Database. It is a
filing/exchange API for the Hague System workflow.

### 3.2 Auth

Hague Web Services is a partner/office-level API (the catalog tags it under
the `WIPO IPO` axis and the "subscription_type" code matches the same
restricted code as the Brand DB image API). No free public key; no
primary-source documentation found for self-serve registration. For the
Global Design Database UI itself, no auth is required — just human use.

### 3.3 Query language

UI-only. The Design DB UI supports search by Locarno class, applicant,
designation, origin, registration number, date ranges, and image
similarity (per [designdb-help.jsp](https://designdb.wipo.int/designdb/en/designdb-help.jsp)).
No documented machine query language for third parties.

### 3.4 Pagination

UI-only. The [Design DB FAQ](https://www.wipo.int/en/web/global-design-database/faqs_designdb)
caps **report download at 100 records** per query:

> "Only up to 100 results can be downloaded".

### 3.5 Response shape

UI returns HTML / report PDF / report Excel. No documented JSON.

### 3.6 Coverage scope

Per the WIPO Global Design Database public page and FAQ, the database covers
over **15 million designs** across the Hague System + ~41 participating
national/regional offices as of October 2025 (most recent addition: Croatia).
Major collections include China, EUIPO, Japan, USA; India was added in
October 2020 with ~58,000 design models. The Hague International Collection
is updated weekly.

(Primary source for the 15M figure and office count is the WIPO Global Design
Database overview page itself,
[`https://www.wipo.int/en/web/global-design-database`](https://www.wipo.int/en/web/global-design-database).)

### 3.7 Rate limits / quotas

[Terms of Use — Global Design Database](https://www.wipo.int/en/web/global-design-database/terms_and_conditions) §2.1 uses identical language:

> "use the service excessively to the detriment of other Users (for that
> matter, **more than 10 search related actions per minute from a single
> IP address can be considered excessive**); **perform automated queries**;"

Plus a direct IP-block enforcement statement in the
[Design DB FAQ](https://www.wipo.int/en/web/global-design-database/faqs_designdb):

> "If you perform a lot of searches, our **robot detection mechanism might
> mistake you for a robot and block your IP address for 24 hours at most**.
> Contact at gbd@wipo.int if you feel that this is incorrect."

### 3.8 Terms of service

[Terms of Use — Global Design Database](https://www.wipo.int/en/web/global-design-database/terms_and_conditions):

- §2.1 forbids automated queries and excessive use.
- §2.2: data may not be sold or sublicensed without WIPO permission.
- §2.4: WIPO reserves the right to block abusive use.

The [Design DB FAQ](https://www.wipo.int/en/web/global-design-database/faqs_designdb)
reiterates that "our terms of use specifically disallow any kind of bulk or
automatic downloading of data" and the redistribution agreement with
national offices precludes acquiring the database.

### 3.9 Operational notes

- Active robot-detection with 24-hour IP block (per the FAQ above).
- The Hague Express Database covers international design registrations
  governed by the 1999 and/or 1960 Acts of the Hague Agreement, with
  reproductions of designs published since 3 January 1985.
- Cloud Run / data-center egress is unusually likely to trip the
  robot-detection given our earlier observations of WAF-style filtering on
  WIPO-adjacent hosts (see `feedback_cloud_run_egress.md` in the team
  memory).

### 3.10 Verdict

**RED.** No public search API. The only design-system API in WIPO's catalog
is the Hague filing/exchange surface for IP-office partners, not a third
party search API. The UI is explicitly off-limits to automated queries
(§2.1) with a published 24-hour IP-block enforcement, capped at 100
downloadable results per query, and redistribution is precluded by
participating-office agreements.

---

## Executive summary

All three WIPO global databases fail the zero-infra constraint, and they fail
in the **same way**. WIPO ships no public, third-party-callable REST/JSON
search API for PATENTSCOPE, the Global Brand Database, or the Global Design
Database; the only WIPO-published APIs in the official catalog are Pearl
(terminology), Hague Web Services (Hague filing back-end), the GBD
image-classification API (partner-only), and IPCPUB (classification
publication). The web UIs are explicitly off-limits to "automated queries"
under identical ToS language across all three databases, with a documented
10-actions-per-minute IP threshold, and the Brand and Design DBs now layer
real anti-bot enforcement on top (AltCha CAPTCHA on every page of
`branddb.wipo.int`; a stated 24-hour IP block on `designdb.wipo.int`).
Bulk-download routes exist for PATENTSCOPE — SOAP/Java + SFTP at CHF
600–2,000/year — but they are batch products and violate the "no hosted
index" rule. Ranked least-bad to most-bad: (1) **PATENTSCOPE** at least has a
paid SOAP path we could license if we relaxed the constraint; (2) the
**Global Brand Database** has a developer portal (`developers.branddb.wipo.int`)
and a gated API host (`public-api.branddb.wipo.int`) that hint at a future
partner program, so it is worth a periodic re-check; (3) the **Global Design
Database** is the most decisively closed — only the Hague filing API exists,
and the FAQ openly threatens IP blocks. Recommendation: do **not** plan to
proxy WIPO global databases live from our connector. For trademark and
design coverage, route to the national-office connectors instead (USPTO TSDR,
EUIPO, IPO India, IP Australia, DPMA, etc.) and treat WIPO global as a
human-only deep-link destination.
