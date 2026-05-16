# UKIPO (United Kingdom Intellectual Property Office) — API discovery

**Date:** 2026-05-16
**Scope:** UK patents, UK trade marks (GB + IR-UK), UK registered designs
**Question:** Does UKIPO expose a live, queryable REST/JSON/XML/Atom API we can proxy at runtime, with zero offline corpus on our side?

Verdict per right is split — see §10 and the executive summary.

---

## 1. Endpoint

### Patents — **One IPO Search** (HTML only; no JSON API yet)

The legacy **IPSUM** Atom/XML patent status feed was retired on **22 January 2025** and replaced by **One IPO Search**.

- Public search UI: <https://www.gov.uk/search-for-patent> (a redirect/alias to the live service)
- Service host: `https://www.search-for-intellectual-property.service.gov.uk/`
  - Detail records observed at `https://www.search-for-intellectual-property.service.gov.uk/{APPLICATION_NUMBER}` (e.g. `/GB1418215.8`, `/EP3756048` — example URLs visible in IPO's own canonical search-result listings).
- Journal subpath: `https://www.search-for-intellectual-property.service.gov.uk/journal`
- Cabinet-Office-level page describing the service and its API roadmap: [New IPO patents services detailed guide — GOV.UK](https://www.gov.uk/government/publications/one-ipo-patents-service-details/one-ipo-patents-service-details).
- Programme/launch background: [One IPO Transformation Programme](https://www.gov.uk/government/publications/one-ipo-transformation-programme/one-ipo-transformation-programme); [Introducing the One IPO roadmap (blog, 19 Feb 2026)](https://ipo.blog.gov.uk/2026/02/19/introducing-the-one-ipo-roadmap/); [Introducing the One IPO Roadmap (news)](https://www.gov.uk/government/news/introducing-the-one-ipo-roadmap).

**Is IPSUM still operational?** No. IPSUM was retired 22 Jan 2025. The legacy URL `https://www.ipo.gov.uk/p-ipsum.htm` now redirects to or signposts the new service. See the IPO blog and the [eeNews summary of the UK IPO revamp](https://www.eenewseurope.com/en/uk-patent-office-revamps-search-tool-plans-api/) (third-party, used only for date corroboration).

**Is there a JSON/XML API for patents today?** No. The "New IPO patents services detailed guide" lists three APIs as *under development* but not yet released: a **View rights portfolio API**, a **Renewals API**, and an **IP register API** — "the exact timeline for releasing APIs is still to be confirmed" ([source](https://www.gov.uk/government/publications/one-ipo-patents-service-details/one-ipo-patents-service-details)). The launch-day service on **31 March 2026** ([launch news](https://www.gov.uk/government/news/one-ipo-patents-service-what-to-expect-ahead-of-public-launch)) shipped without a public search API.

### Trade marks — **HTML search only**

- Public search UI: <https://www.gov.uk/search-for-trademark>
- Underlying app: `https://trademarks.ipo.gov.uk/ipo-tmtext` (search form at `/ipo-tmtext/start`, results at `/ipo-tmtext/page/Results`).
- Journal: <https://www.gov.uk/check-trade-marks-journal>; weekly XML bulk dumps via [Trade Marks Journal — data.gov.uk](https://www.data.gov.uk/dataset/fc8a832f-b5e2-4c03-9ae4-10a5e74b467c/ipo-tmj).
- Bulk dataset publications: [IPO trade mark dataset](https://www.gov.uk/government/publications/ipo-trade-mark-dataset); [IPO: Trade mark data release](https://www.gov.uk/government/publications/ipo-trade-mark-data-release); [Open data explained: Domestic UK Applications](https://www.gov.uk/government/publications/ipo-trade-mark-data-release/ipo-data-explained-2016); [Open Data explained: International Registrations](https://www.gov.uk/government/publications/ipo-trade-mark-data-release/open-data-explained-international).

No public live API. The [FOI 2016/489 response](https://assets.publishing.service.gov.uk/media/5a8006f140f0b62305b88baf/foi-2016-489-trade-mark-database-access.pdf) explicitly states the IPO "does not at present provide an API" for bulk trade mark retrieval, and the One IPO roadmap confirms a new trade marks digital service (including new search) is *only entering design phase* in 2026-27 ([IPO blog: roadmap](https://ipo.blog.gov.uk/2026/02/19/introducing-the-one-ipo-roadmap/); [IPO Corporate Plan 2026 to 2027](https://www.gov.uk/government/publications/intellectual-property-office-corporate-plan-2026-to-2027/intellectual-property-office-corporate-plan-2026-to-2027)).

### Registered designs — **HTML lookup by number/owner only**

- Public search UI: <https://www.gov.uk/search-registered-design> (alias) → <https://www.registered-design.service.gov.uk/find>
- Apply path: <https://www.registered-design.service.gov.uk/Apply/...>

The find tool supports lookup by design number or owner name only. For broader image/keyword search, IPO points users to the EUIPO's **Designview** tool. There is no UKIPO designs API; the One IPO roadmap places integrated trade mark + design search in a later transformation phase (post-2026-27 patents launch) — see [One IPO Transformation Programme](https://www.gov.uk/government/publications/one-ipo-transformation-programme/one-ipo-transformation-programme) and the [IPO Corporate Plan 2026 to 2027](https://www.gov.uk/government/publications/intellectual-property-office-corporate-plan-2026-to-2027/intellectual-property-office-corporate-plan-2026-to-2027).

---

## 2. Auth

- **Patents (One IPO Search HTML)** — no authentication required to use the public search UI. The future One IPO APIs (View rights portfolio, Renewals, IP register) will require an **IPO account with MFA** (the One IPO account model — text/authenticator MFA, 10-minute idle logout) per the [New IPO patents services detailed guide](https://www.gov.uk/government/publications/one-ipo-patents-service-details/one-ipo-patents-service-details). No public API tier is documented yet.
- **Trade marks** — public HTML search, no auth.
- **Registered designs** — public HTML find tool, no auth.
- **IPSUM** historically required no key; that is now moot (retired).

No primary source documents an API key, OAuth flow, or developer registration portal for UKIPO IP-register search as of 2026-05-16.

---

## 3. Query language

### Patents (One IPO Search)
Per the IPO description and operator commentary, the HTML form supports searches by:

- Application number, publication number
- Applicant/proprietor name
- Inventor name
- Representative (agent)
- Keywords (title/abstract)
- Classification (IPC/CPC)
- Status
- Date ranges on filing/publication/grant
- Licences-of-right flag

Source for the field list: [New IPO patents services detailed guide](https://www.gov.uk/government/publications/one-ipo-patents-service-details/one-ipo-patents-service-details). The advanced query syntax (boolean operators, wildcards) is not formally documented in a primary-source spec — no primary source found for an operator grammar reference.

### Trade marks
Only the HTML form on `trademarks.ipo.gov.uk/ipo-tmtext`. Supports phonetic/wordmark search, owner/representative, status, Nice class. No documented query DSL — **no primary source found** for a structured query API.

### Registered designs
Lookup by design number or owner name only ([Find a registered design](https://www.gov.uk/search-registered-design)). No structured query DSL.

---

## 4. Pagination

- **One IPO Search**: paginated HTML results. **No primary source found** specifying a hard per-page or total-results cap.
- **Trade marks (ipo-tmtext)**: paginated HTML. **No primary source found** documenting a programmatic pagination contract.
- **Designs**: returns a single-record or short list view. **No primary source found** for pagination semantics.

There is no documented Atom paging, cursor token, or `offset/limit` query parameter exposed as a stable API for any of the three rights.

---

## 5. Response shape

No primary source provides a documented JSON or Atom response schema for any of the three rights as of 2026-05-16. The public surface is HTML. IPSUM's historical Atom feed (now retired) is no longer a usable contract.

For trade marks, the closest thing to a documented record schema is the **weekly bulk XML dump** of the Trade Marks Journal ([data.gov.uk: ipo-tmj](https://www.data.gov.uk/dataset/fc8a832f-b5e2-4c03-9ae4-10a5e74b467c/ipo-tmj)) and the [trade mark dataset column dictionary](https://www.gov.uk/government/publications/ipo-trade-mark-data-release/ipo-data-explained-2016) — but those are **bulk artefacts**, not a live per-query response. The constraint of this discovery brief is "no bulk corpora," so those don't count.

**No primary source found** for a sample search-hit JSON/XML payload from a live query API on patents, trade marks, or designs.

---

## 6. Coverage scope

- **Patents** — One IPO Search covers UK patents and supplementary protection certificates (SPCs). It handled ~200,000 searches in its first 12 months according to IPO public communications ([eeNews summary referencing IPO figures](https://www.eenewseurope.com/en/uk-patent-office-revamps-search-tool-plans-api/) — used for the volume figure only). The detailed scope (earliest year covered) is **not stated** in the primary IPO publications I located — **no primary source found** for an exact date range.
- **Trade marks** — The UK trade marks register dates to 1876 (the trade marks dataset includes records from then), per the [IPO blog "UK Trade Mark Register at 150" (29 Jan 2026)](https://ipo.blog.gov.uk/2026/01/29/the-uk-trade-mark-register-at-150-what-next/). The live search at `trademarks.ipo.gov.uk` covers GB applications/registrations and the UK part of International Registrations (IR-UK) — see [Open Data explained: International Registrations](https://www.gov.uk/government/publications/ipo-trade-mark-data-release/open-data-explained-international).
- **Designs** — Registered UK designs (and pre-Brexit re-registered EU designs since the end of the transition period). No primary source for exact record counts on the live tool.

---

## 7. Rate limits / quotas

**No primary source found** for published rate limits, throttles, or per-IP quotas on One IPO Search, `trademarks.ipo.gov.uk/ipo-tmtext`, or `registered-design.service.gov.uk/find`. None of these is presented as an API; they are public-facing web services. Any automated scraping would be governed by `robots.txt` and general terms of use rather than a published quota.

---

## 8. Terms of service / licence

- Crown-copyright UK government data is published under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
- The IPO trade mark **bulk dataset** is explicitly OGL v3.0: see [IPO trade mark dataset](https://www.gov.uk/government/publications/ipo-trade-mark-dataset).
- The [Directions for the use of the One IPO Digital Services](https://www.gov.uk/government/publications/directions-for-the-use-of-the-one-ipo-digital-services/directions-for-the-use-of-the-one-ipo-digital-services) and the [Guidance and notes on the Directions](https://www.gov.uk/government/publications/directions-for-the-use-of-the-one-ipo-digital-services/guidance-and-notes-on-directions-for-the-use-of-the-one-ipo-digital-services) govern use of the digital services. **No primary source found** explicitly permitting automated/proxy scraping of `search-for-intellectual-property.service.gov.uk`, `trademarks.ipo.gov.uk`, or `registered-design.service.gov.uk` for production proxy traffic.

In short: the *bulk data* is OGL v3.0 and unambiguously reusable; the *live HTML services* have no documented permission for programmatic proxying.

---

## 9. Operational notes

- **IPSUM retired 22 January 2025.** Replaced by One IPO Search (HTML). Anyone with an IPSUM Atom integration has a broken pipeline today.
- **One IPO Patents Service public launch: 31 March 2026.** All UK patent applications must use One IPO from 1 April 2026; eOLF is being decommissioned. Source: [One IPO Patents Service: what to expect ahead of public launch](https://www.gov.uk/government/news/one-ipo-patents-service-what-to-expect-ahead-of-public-launch).
- **APIs are roadmap, not ship.** The IPO has publicly committed to three patent APIs (View rights portfolio, Renewals, IP register) and to AI-assisted search + a public bulk-data API on One IPO Search. **No release date is published.** They are inviting software vendors to email `transformation@ipo.gov.uk` for involvement ([What's changing — our future patent services, 16 Sept 2025](https://ipo.blog.gov.uk/2025/09/16/whats-changing-our-future-patent-services/)).
- **Trade marks transformation hasn't started.** Phase 2 of One IPO (trade marks digital service) is in the **design phase** during 2026-27 ([IPO Corporate Plan 2026 to 2027](https://www.gov.uk/government/publications/intellectual-property-office-corporate-plan-2026-to-2027/intellectual-property-office-corporate-plan-2026-to-2027); [Introducing the One IPO roadmap](https://ipo.blog.gov.uk/2026/02/19/introducing-the-one-ipo-roadmap/)). A new trade marks search tool is committed but unscheduled.
- **Designs transformation is even further out**, after trade marks and the IPO tribunal ([Transformation II: spotlight on trade marks, designs and tribunals](https://ipo.blog.gov.uk/2023/10/10/transformation-ii-spotlight-on-trade-marks-designs-and-tribunals/)).
- **Cumulative integrated search across patents + TMs + designs + APIs**: stated by IPO as a 2026 deliverable — but as of 2026-05-16 not yet shipped.

---

## 10. Verdict (per right)

| Right | Live API today? | Verdict |
|---|---|---|
| **Patents** | No public REST/JSON/Atom API. One IPO Search is HTML; IPSUM retired Jan 2025; APIs are in active development but unscheduled. | **RED** |
| **Trade marks** | No API. Only HTML search at `trademarks.ipo.gov.uk` and weekly bulk XML dumps (excluded by the brief's no-corpus rule). | **RED** |
| **Registered designs** | No API. HTML lookup by number/owner only; IPO redirects broader searches to Designview. | **RED** |

All three rights are **RED** against the "zero-infra live proxy" constraint. The brief explicitly says a red verdict is just as useful as a green one — this is a definitive no-go for a zero-infrastructure UKIPO proxy in 2026-05.

---

## Executive summary

**Recommendation: RED across the board for UKIPO live-API proxying.** Patents, trade marks, and registered designs each lack a public, documented, queryable REST/JSON/XML/Atom API. The legacy IPSUM Atom feed — the one historical surface that would have qualified — was retired on **22 January 2025** in favour of One IPO Search, which is currently HTML-only. The IPO has publicly committed to three patent APIs (View rights portfolio, Renewals, IP register) plus a bulk-data API on One IPO Search, but as of the One IPO Patents Service public launch on **31 March 2026** none of these is generally available; rollout is "to be confirmed." Trade marks transformation is only entering design phase in 2026-27, and designs come after that. The biggest operational risk is **the IPSUM retirement is already a year in the rear-view mirror with no replacement API yet**, so any "we'll just wait for the new API" plan has an indeterminate runway. Bridging via the OGL-v3.0 weekly Trade Marks Journal XML or other bulk dumps is available but violates the no-corpus constraint. **Revisit when the IPO publishes a developer portal URL or OpenAPI spec — not before.**
