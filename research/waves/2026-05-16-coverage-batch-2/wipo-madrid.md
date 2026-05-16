# WIPO Madrid System — API discovery for a zero-infra proxy connector

Research date: 2026-05-16
Entity ID: `WO/WIPO/Madrid`
Scope: Determine whether the **WIPO Madrid System** itself (Madrid
Monitor and the new eMadrid "Find and Monitor" service that is replacing
it) exposes a public, queryable REST/JSON/XML API we can call live from a
Python connector — no bulk downloads, no hosted indexes, no offline
corpora.

Sibling research:
- Brand DB / Design DB / PATENTSCOPE — see
  [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../2026-05-16-registered-ip-discovery/wipo-global-databases.md).
  The Global Brand Database aggregates Madrid IRs + national TMs and was
  found **red** (ToS-blocked, anti-automation). This wave is about the
  Madrid System on its own — Madrid Monitor, eMadrid, and any direct
  Madrid API.
- WIPO connector survey — see [`connectors/wipo.md`](../../connectors/wipo.md).
  Madrid Monitor is covered there at the cross-asset comparison level.

Headline: **Red.** WIPO does not publish a public, free, programmatic
search API for the Madrid System. Madrid Monitor exposes two
undocumented per-IR XML endpoints that are auth-free and return ST.66
data, but the
[Madrid Monitor Terms of Use (July 2025)](https://www3.wipo.int/madrid/monitor/en/terms.jsp)
explicitly forbid automated queries and bulk acquisition. The legitimate
programmatic path is the bulk XML feed via UN ICC FTP at CHF 30,000/yr.

---

## 1. Endpoint

WIPO maintains two parallel surfaces for searching Madrid international
trademark registrations:

- **Madrid Monitor (legacy, being decommissioned).**
  Public UI at
  [`https://www3.wipo.int/madrid/monitor/en/`](https://www3.wipo.int/madrid/monitor/en/).
  WIPO states on
  [Finding and Monitoring International Trademark Registrations](https://www.wipo.int/en/web/madrid-system/find-and-monitor-international-trademark-registrations):
  "We will decommission Madrid Monitor once functionality has been
  integrated into Find and Monitor in eMadrid."
- **eMadrid "Find and Monitor" (current).**
  Public UI at
  [`https://madrid.wipo.int/findmonit/quick-search`](https://madrid.wipo.int/findmonit/quick-search),
  reachable from the umbrella [eMadrid portal](https://madrid.wipo.int/).

Neither surface publishes a search API. The
[WIPO API Catalog](https://apicatalog.wipo.int/) lists 181 IP-office APIs
(probe 2026-05-16); the four `organization == "WIPO"` entries are:

| idAPI | Title | Description |
|---|---|---|
| 185 | WIPO Pearl API | terminology lookup |
| 187 | Hague Web Services (HWS) | design **filing** (partner offices only) |
| 188 | GBD Image-related API | trademark image classification — "**Usage restricted to collaborating IP Offices**" |
| 221 | IPCPUB | classification publication |

No Madrid Monitor entry, no eMadrid search entry — primary-source
confirmation from WIPO's own catalog API
(`GET https://apicatalog.wipo.int/api/apis/all`).

### Undocumented per-IR XML endpoints

Madrid Monitor exposes two undocumented per-IR endpoints that return
single-record XML over plain HTTPS, no auth, no API key — confirmed by
direct probe 2026-05-16:

- `GET https://www3.wipo.int/madrid/monitor/api/v1/data/{IRN}` →
  `text/xml` returning a `Transaction` element under
  `http://www.wipo.int/standards/XMLSchema/trademarks` with the
  `Romarin-V1-3.xsd` schema. Includes designations, classes, holder,
  expiry, application date, mark image URI, goods/services. Example:
  [`/api/v1/data/WO500000000789955`](https://www3.wipo.int/madrid/monitor/api/v1/data/WO500000000789955).
- `GET https://www.wipo.int/madrid/monitor/api/v1/tmxml/data/{IRN}` →
  same record, returned under the WO-TM-Search /
  `WO-TM-Search-TradeMark-V1-0-Final.xsd` (TM-View) schema. The URL
  shape is the one referenced from the
  [API Catalog User Guide](https://www.wipo.int/en/web/standards/ip-api-catalog/user-guide)
  family of pages but is not documented as a public API anywhere on
  wipo.int.

Both endpoints are the backend the JS UI calls. They are **not** advertised
as a developer surface, and the Madrid Monitor terms forbid programmatic
use against them (see §8 below).

### Madrid Monitor bulk XML (legitimate programmatic path)

Documented at
[`/madrid/en/monitor/download.html`](https://www.wipo.int/madrid/en/monitor/download.html):
"The full Madrid Monitor database is available in XML format for **CHF
30,000**." Daily delta `yyyymmdd.zip` files are pushed via UN
International Computing Centre (ICC) anonymous FTP — files are named by
date and contain the current state of all marks changed that day plus
mark images. Authentication is by contract (paid subscriber).

## 2. Auth

- Madrid Monitor UI / undocumented per-IR XML: **none.** Open HTTPS.
- eMadrid Find-and-Monitor UI: **none for public search**; a WIPO User
  Account is needed for the watchlist / saved-search features.
- ICC FTP bulk XML: **paid contract** (CHF 30,000/yr).
- Madrid Office Portal (MOP) and Madrid e-Filing (MeF) APIs: **partner
  IP Offices only** — internal authentication, contract-bound, not a
  public-facing API. See the September 2025 IB briefing
  [`mm_ld_wg_23_roundtable_1_ib.pdf`](https://www.wipo.int/edocs/mdocs/madrid/en/mm_ld_wg_23/mm_ld_wg_23_roundtable_1_ib.pdf).
- WIPO B2B Developer Portal ([`b2b.wipo.int`](https://b2b.wipo.int/catalog/all)):
  catalogs the WIPO Pearl API only for Madrid-adjacent work — no Madrid
  search API listed.

## 3. Query language

For Madrid Monitor / Find-and-Monitor the human UI supports the queries
described on
[Finding and Monitoring International Trademark Registrations](https://www.wipo.int/en/web/madrid-system/find-and-monitor-international-trademark-registrations):
mark name, holder name, IR number, designation, Nice class, status
(active / inactive / pending). UI export formats are PDF / CSV / XML.

The undocumented per-IR endpoint supports **only** lookup by IR number —
it is `GET /data/{IRN}`, with no search parameters. There is no
documented machine-readable search-by-holder or search-by-designation
endpoint. Probing `/api/v1/search?q=test` returned HTTP 404.

## 4. Pagination

Not applicable to the per-IR endpoint (single-record lookup). UI search
pagination is server-driven and not documented as an API.

## 5. Response shape

- Per-IR `/api/v1/data/{IRN}` → XML, WIPO ST.66 / Romarin v1.3 schema
  (`http://www.wipo.int/standards/XMLSchema/trademarks` namespace).
- Per-IR `/api/v1/tmxml/data/{IRN}` → XML, WIPO TM-View / OAMI
  `TM-Search` schema (`http://www.oami.europa.eu/TM-Search` namespace,
  pointing at WIPO's `WO-TM-Search-TradeMark-V1-0-Final.xsd`).
- Bulk ICC FTP → ST.66 ZIP per day + image binaries.

No JSON anywhere on the Madrid surface.

## 6. Coverage scope

- ~915,000+ international trademark registrations across **132 countries
  / 116 members** of the Madrid System per the
  [WIPO Madrid System overview](https://www.wipo.int/en/web/madrid-system).
- Full backfile: Madrid IR numbers from the 1890s forward; modern records
  (post-Protocol entry into force 1996) carry mark images and structured
  designation chains.
- National-phase data: the IR record carries each designated office's
  status code under Madrid (`DesignatedUnderCode` = Agreement or
  Protocol) and refusal / acceptance / final-decision events recorded
  by WIPO — but **not** the full national-office prosecution history.
  For national-office downstream prosecution, the user must go to the
  national office's TM register.

## 7. Rate limits / quotas

From the
[Madrid Monitor Terms of Use (July 2025)](https://www3.wipo.int/madrid/monitor/en/terms.jsp),
§6 "Fair Use":

> "the service is not designed for bulk downloads and therefore the
> User shall not undertake the following unfair use: more than **10
> search related actions per minute** from an IP address; and
> **automated queries**."

WIPO "reserves the right to intervene and restrict or prevent access to
the User in case of unfair use of the service."

## 8. Terms of service

Madrid Monitor Terms of Use (July 2025) — §5 "Prohibited Use":

> "perform bulk acquisition, bulk downloads or bulk storing of data or
> documents;" and
> "perform bulk copying, bulk reformatting or bulk redistribution of
> data or documents;"

And §6 (excerpted in §7 above) forbids automated queries. §5 also bars
sub-licensing the data to "another service provider host or publisher."

**This is a hard block for a zero-infra proxy.** Even though the per-IR
XML endpoints are open and unauthenticated, hitting them from a server
on behalf of arbitrary users falls within the "automated queries"
prohibition and within the §5 prohibition on making Madrid Monitor data
"accessible or sublicensed in any way to another service provider host
or publisher."

A self-hosted bulk-XML mirror (CHF 30,000/yr) **is** legitimate but
violates our zero-infra constraint (we'd be hosting a search index, not
proxying).

## 9. Operational notes

- **Languages.** Madrid filings are in English, French, or Spanish per
  Rule 6 of the
  [Common Regulations under the Madrid Protocol](https://www.wipo.int/en/web/madrid-system).
  Goods/services are translated by WIPO into the other two filing
  languages.
- **Transition risk.** Madrid Monitor is on a decommissioning timeline;
  the per-IR XML endpoints could disappear without notice as eMadrid
  Find-and-Monitor replaces them. WIPO has published no migration
  commitment for the back-end URLs.
- **Partner-only flags.** MeF (e-Filing) and MOP (Office Portal) are
  partner-IP-office-only. They are filing/document-exchange APIs, not
  search APIs — irrelevant to a third-party proxy.
- **WIPO API Standard.** WIPO has published its own
  [WIPO Standard on Web API](https://www.wipo.int/meetings/en/doc_details.jsp?doc_id=415578)
  pushing member offices toward REST/JSON. The Madrid System has not
  followed its own guidance.
- **Commercial alternatives exist** (e.g. signa.so) that license the bulk
  XML feed and resell API access. These are out-of-scope under our
  "primary source only" rule but worth noting for the strategic doc.

## 10. Verdict

**Red.** 🔴

WIPO does not publish a public, free, search-capable Madrid API. The
only auth-free machine surface is an **undocumented per-IR XML endpoint**
that supports lookup only (no search) and is explicitly covered by ToS
clauses forbidding "automated queries" and re-publication to another
service provider host. The only legitimate programmatic path is the
**CHF 30,000/yr bulk ICC FTP feed**, which violates our zero-infra
constraint by definition.

For our connector roadmap this means: we cover Madrid IRs only
**transitively** through the national/regional offices that publish a
proper TM API (USPTO TSDR, EUIPO TMView, IP Australia Trade Marks API,
etc.), or we skip Madrid until WIPO ships a public REST/JSON Madrid
search API. There is no in-between path that satisfies ToS + zero-infra.
