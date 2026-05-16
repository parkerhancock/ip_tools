# KIPO / KIPRIS Plus — API Discovery for Zero-Infra Proxy Connector

**Date:** 2026-05-16
**Target office:** Korean Intellectual Property Office (KIPO)
**Likely API surface:** KIPRIS Plus (operated by the Korea Institute of Patent Information, KIPI) — and a mirror of the same endpoints listed on Korea's national Open Data Portal, [data.go.kr](https://www.data.go.kr/en/index.do).
**Decision frame:** can we proxy the API live from our connector with zero local index, no bulk download, no offline corpus?

---

## 1. Endpoint

KIPRIS Plus is the developer-facing arm of KIPRIS, KIPO's online IP search system. APIs are RESTful and respond in XML.

- Portal (Korean): <https://plus.kipris.or.kr/>
- Portal (English): <https://plus.kipris.or.kr/eng/main.do>
- Service catalog (English): <https://plus.kipris.or.kr/eng/data/service/List.do?subTab=SC001&menuNo=300100>
- Developer guide hub (Korean only): <https://plus.kipris.or.kr/portal/bbs/list.do?bbsId=B0000001>
- API service map (beta): <https://plus.kipris.or.kr/portal/main/contents.do?menuNo=210167>

Base API host (production REST endpoints, confirmed by data.go.kr OpenAPI listings and KIPRIS docs):

- Host: `http://kipo-api.kipi.or.kr/openapi/service/{service}/{operation}` ([reference, design search example](https://plus.kipris.or.kr/portal/bbs/view.do?nttId=132&bbsId=B0000001&menuNo=200015))

Right-by-right endpoints surfaced in primary sources:

| Right | Service path (under `kipo-api.kipi.or.kr/openapi/service/…`) | Primary source |
|---|---|---|
| Patents & utility models (publications/registrations) | `patUtliInfoSearchService` (`getWordSearch`, `getAdvancedSearch`, plus item-by-item lookups) | [KIPRIS Plus — Patent-Utility Model Publications](https://plus.kipris.or.kr/eng/data/clas/DBII_000000000000001/view.do?menuNo=310000); [data.go.kr 15065437](https://www.data.go.kr/data/15065437/openapi.do?recommendDataYn=Y) |
| Trademarks | `trademarkInfoSearchService/getWordSearch` (and `getAdvancedSearch`) | [data.go.kr 15043964 — Trademark Information Search Service (EN)](https://www.data.go.kr/en/data/15043964/openapi.do) |
| Designs | `designInfoSearchService/getWordSearch` (and `getAdvancedSearch`) | [data.go.kr 15043970 — Design Information Search Service (EN)](https://www.data.go.kr/en/data/15043970/openapi.do); [KIPRIS Plus dev guide notice](https://plus.kipris.or.kr/portal/bbs/view.do?nttId=132&bbsId=B0000001&menuNo=200015) |

KIPRIS Plus advertises "**11 types of data** through API including Public Announcements, Patents and Utility Models, Citations, English Abstracts (KPA), Procedural Data, Search Guide, Registrations, Trial Records, Foreign Patents, Machine Translations, and Classifications, providing standardized XML data applicable to all environments." ([Service Introduction, EN](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024)). An older KIPI leaflet describes the catalog as "**46 OpenAPI** as of December 2019" ([leaflet PDF](https://plus.kipris.or.kr/sampledata/KIPRISPlus%20leaflet.pdf)).

**No primary source found** for the exact full URL of the patent-utility `getAdvancedSearch` operation in plain text on the English site — the path is documented inside the developer guide PDF and the data.go.kr OpenAPI definition page, which require a logged-in account to view the OpenAPI specification block.

---

## 2. Auth

KIPRIS Plus requires a per-user authentication key on every call.

- **Mandatory key.** "Any Member wishing to use the Open API Service must obtain an Authentication Key in accordance with the procedures set by the Institute" — [Terms of use, EN, §11](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030). "Members may only obtain one Authentication Key at a time. Additionally, Members shall not provide, disclose, or share Authentication Keys with others" (same source).
- **Membership step is gated.** "A User may register as a Member by agreeing to the Terms, collection/use of personal information, and setting up an ID and Password in accordance with the procedures set by the Institute. **During this procedure, the Institute may request identity verification through a professional institution**" — [Terms of use, EN, §5](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030). Korean public-sector portals typically implement that step via i-PIN or mobile-carrier verification (KR phone number required); the ToS does not commit to an alternative for non-residents.
- **Account tiers.** Two tiers: **development** (default after signup, free up to a monthly cap) and **operation** (paid, "carefully reviewed and approved on a limited basis" — [data.go.kr 15043964](https://www.data.go.kr/en/data/15043964/openapi.do)).
- **Registration portal.** English signup page: <https://plus.kipris.or.kr/eng/member/joinView.do?menuNo=300028>. Service-application landing: <https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300026>.
- **Alternative path:** the same REST APIs are also listed on Korea's national open data portal, `data.go.kr` (e.g., [trademark service](https://www.data.go.kr/en/data/15043964/openapi.do), [design service](https://www.data.go.kr/en/data/15043970/openapi.do)). `data.go.kr` has an English-language [Join membership](https://www.data.go.kr/en/uim/mss/mberSubscribeConfirmFormView.do) form; however, primary documentation does not explicitly confirm that registration succeeds without a Korean phone or i-PIN, and the [OGD Portal Introduction (EN)](https://www.data.go.kr/en/ugs/selectPortalInfoView.do) page does not address foreign-user eligibility.
- **Approval lead time.** **No primary source found** for an SLA. The portal lists support hours as "Monday-Friday 09:00-12:00, 13:00-18:00 KST" with contact `kiprisplus@kipi.or.kr` ([Service Introduction, EN](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024)), implying human-in-the-loop review for at least the operation tier.

---

## 3. Query Language

Each service exposes two top-level search operations:

- **`getWordSearch`** — free-text search across the full document (title, abstract, claims).
- **`getAdvancedSearch`** — structured field-by-field search with boolean conjunction of fields.

Both return paginated XML.

**Patent-utility searchable fields** (per the data.go.kr OpenAPI listing and [KIPRIS Plus Patent-Utility doc page](https://plus.kipris.or.kr/eng/data/clas/DBII_000000000000001/view.do?menuNo=310000)):

> invention title, abstract, claim scope, IPC code, application number, publication number, registration number, priority claim number, international application number, international publication number, application date, publication date, announcement date, registration date, priority claim date, international application date, international publication date, applicant name, patent customer number, inventor name, agent name, agent code, registered rights holder, patent/utility administrative disposition, page number, items per page, and sort criteria.

**Trademark searchable fields** ([data.go.kr 15043964, EN](https://www.data.go.kr/en/data/15043964/openapi.do)):

> application number, application reference number, application date, publication number, publication date, registration number, registration reference number, registration date, registration gazette number, registration publication date, priority number, priority date, international registration number, international registration date, application status, product classification code, design code (Vienna), applicant name, agent name, and registrant (RG)/code.

**Design searchable fields** ([data.go.kr 15043970, EN](https://www.data.go.kr/en/data/15043970/openapi.do)): equivalent shape — application/publication/registration numbers and dates, design classification, applicant, agent, plus drawing access.

Inputs accept Korean and English where applicable (e.g., applicant name "삼성전자" vs. "Samsung Electronics"); however, the underlying records are primarily Korean. Machine-translated **English abstracts (KPA — Korean Patent Abstracts)** are offered as a separate API per the KIPRIS Plus service introduction.

CQL-style operators are **not** documented as a public input language; instead, fields are passed as separate query parameters and combined server-side (typical of Korean public-sector OpenAPI patterns: `?serviceKey=…&fieldA=…&fieldB=…&pageNo=…&numOfRows=…`).

---

## 4. Pagination

Standard Korean public-API pagination convention is `pageNo` + `numOfRows`. **No primary source found** in the English-language pages quoting the exact parameter names for KIPRIS Plus — the field reference for patent-utility search explicitly mentions "page number, items per page, and sort criteria" as request parameters ([Patent-Utility Model Publications, EN](https://plus.kipris.or.kr/eng/data/clas/DBII_000000000000001/view.do?menuNo=310000)) but does not name them. The deeper schema lives in the dev-guide PDF (`API 개발가이드`, [list](https://plus.kipris.or.kr/portal/bbs/list.do?bbsId=B0000001), [REST OPEN API utilization guide](https://plus.kipris.or.kr/portal/bbs/view.do?nttId=132&bbsId=B0000001&menuNo=200015)), which is Korean-only and requires portal navigation.

Hard cap on total accessible results: **no primary source found**.

---

## 5. Response Shape

- Format: **XML only.** "providing standardized XML data applicable to all environments" — [Service Introduction, EN](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024). No JSON variant is advertised on the English portal.
- Patent-utility hits include "bibliographic information including application number, registration date, invention title, and registration status, as well as download paths for drawings and full specifications" — [Patent-Utility Model Publications, EN](https://plus.kipris.or.kr/eng/data/clas/DBII_000000000000001/view.do?menuNo=310000).
- Design hits include "bibliographic, drawing, and summary information for the design publications and registration gazettes" — [data.go.kr 15043970, EN](https://www.data.go.kr/en/data/15043970/openapi.do).
- **No primary source found, on a publicly readable page, for a literal sample XML response.** The sample blocks live inside the developer-guide PDFs and the data.go.kr OpenAPI definition viewer, both of which require an authenticated session or are reachable only via the document download URL inside the portal.

---

## 6. Coverage Scope

- **All four KR rights:** patents, utility models, designs, trademarks — confirmed for both the in-page KIPRIS service ([KIPRIS Intro](https://www.kipris.or.kr/khome/info.do?page=intro), [KIPRIS English homepage](http://eng.kipris.or.kr/enghome/kipris/kipris.jsp)) and the KIPRIS Plus API catalog ([EN service list](https://plus.kipris.or.kr/eng/data/service/List.do?subTab=SC001&menuNo=300100)).
- **Backfile depth:** WIPO Inspire's KIPRIS profile states KIPRIS "provides bibliographic data in text format from **1948**" ([WIPO Inspire — KIPRIS](https://inspire.wipo.int/kipris)).
- **Aux datasets via API:** Citations, English Abstracts (KPA, machine-translated), Procedural Data, Trial Records, Foreign Patents, Machine Translations, and Classification lookups — [Service Introduction, EN](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024).
- Document count: **no primary source found** quoting a current total; KIPO does publish annual statistics via [KIPO English homepage](https://www.kipo.go.kr/en/) but not as a count on the KIPRIS Plus pages.

---

## 7. Rate Limits / Quotas

- **Development tier — free up to 1,000 calls / month** per the published service-fee page ([Service Fee, EN](https://plus.kipris.or.kr/eng/use/paymentMmg.do?menuNo=310105); summary echoed across the portal). That cap is global per Authentication Key, not per endpoint.
- **Operation tier — flat-rate annual service fee of approximately USD 1,783 / year** ([Service Fee, EN](https://plus.kipris.or.kr/eng/use/paymentMmg.do?menuNo=310105)). The operation tier is "carefully reviewed and approved on a limited basis. To manage system resources and ensure traffic stability" ([data.go.kr 15043964, EN](https://www.data.go.kr/en/data/15043964/openapi.do)).
- **Per-IP or per-minute throttle:** **no primary source found** for a specific RPS or daily quota number; the only governance signal is the discretionary operations-tier review.
- The platform publishes a real-time [API Status page (EN)](https://plus.kipris.or.kr/eng/main/apiStatus.do?menuNo=310128) which probes major operations every 10 minutes — useful for our own health-check loop.

---

## 8. Terms of Service

Primary source: [Terms of use, EN](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030). Notable provisions for a proxy-style integration:

- **One key per member; no sharing.** "Members shall not provide, disclose, or share Authentication Keys with others" (§11). Calling on behalf of arbitrary downstream end-users from a single key is therefore at minimum *gray area*. If we plan to expose this as a service-for-others, KIPI's expectation is one key per identifiable user/organisation.
- **Promotional use of customer identity is permitted unless objected to.** "The Institute may use User information (organization name, logo, applied or utilized products, etc.) for non-commercial promotional purposes in connection with Service dissemination and use."
- **Copyright reserved.** "The copyright of these Terms belongs to the Korea Institute of Patent Information, and any unauthorized reproduction, distribution, or transmission shall constitute an infringement of copyright and is strictly prohibited" — this clause covers the *Terms text* itself, not response payloads, but the upstream data is KIPO bulletin content.
- **Korean version controls.** "In the event of any inconsistency between the Korean version and the English version of these Terms, the Korean version shall prevail" — i.e., the English ToS is non-authoritative; a Korean-fluent reviewer should re-validate any commercial deployment.
- **No explicit prohibition on commercial use found on the EN page.** The paid operation tier presupposes commercial use is contemplated; no clause was found banning resale of response data, but **no primary source confirms** affirmative redistribution rights either.

---

## 9. Operational Notes

- **English documentation:** the portal navigation, service catalog, terms, and signup flow are bilingual. The developer-guide PDFs (`API 개발가이드`, e.g. [nttId=638](https://plus.kipris.or.kr/portal/bbs/view.do?nttId=638&bbsId=B0000001&menuNo=210149), [nttId=132](https://plus.kipris.or.kr/portal/bbs/view.do?nttId=132&bbsId=B0000001&menuNo=200015)) live under the `/portal/` (Korean) tree only; the English `/eng/` tree links to service descriptions but not the technical spec PDFs. **Expect Korean-only PDFs for the field reference and sample payloads.**
- **Response language:** record content is Korean; KPA English abstracts are an opt-in side dataset, not the default.
- **Geofencing:** **no primary source found** on the KIPRIS Plus or KIPO pages stating an IP-allowlist or country block. The portal is openly indexed and accessible from US IPs (this research was conducted from a US-routed agent). Risk per [project_cloud_run_egress.md](../../personal-knowledge-docs/) (memory note): Korean government APIs *can* filter Cloud Run egress more aggressively than residential ranges; this should be verified during the first cutover, not assumed.
- **Support hours:** Monday-Friday 09:00-12:00 and 13:00-18:00 KST, email `kiprisplus@kipi.or.kr`, phone +82-2-6915-1496 ([Service Introduction, EN](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024)). Office: KIPS Building 7F, 131 Teheran-ro, Gangnam-gu, Seoul.
- **Downtime patterns / planned changes:** no primary source found in the English portal. The notice board at <https://plus.kipris.or.kr/portal/bbs/list.do?bbsId=B0000004> carries change announcements but is Korean-only.
- **Two paths to the same APIs:** identical endpoints can also be reached via `data.go.kr` after registering there ([Trademark](https://www.data.go.kr/en/data/15043964/openapi.do), [Design](https://www.data.go.kr/en/data/15043970/openapi.do), [Patent-Utility](https://www.data.go.kr/data/15065437/openapi.do?recommendDataYn=Y), [Citations](https://www.data.go.kr/data/15057617/openapi.do), [PTAB-equivalent Trial](https://www.data.go.kr/data/15065474/openapi.do)). `data.go.kr` has an EN UI but the same KR-identity verification gates may apply.

---

## 10. Verdict

**Yellow.**

The transport story is genuinely good: REST/XML, real per-right search endpoints (`patUtliInfoSearchService`, `trademarkInfoSearchService`, `designInfoSearchService`) hosted at a stable URL (`kipo-api.kipi.or.kr/openapi/service/…`), structured field search, pagination, and 1948-onward backfile — all the building blocks of a clean live-proxy. The 1,000-call/month free tier plus ~USD 1,783/yr unlimited-ish operation tier matches USPTO/EPO pricing tolerances.

The blockers are non-technical and serious for a proxy-as-a-service: (1) the ToS expressly forbids sharing a single Authentication Key, which is exactly what "proxy with zero infra" means in practice; (2) signup's "identity verification through a professional institution" clause typically implements as Korean phone or i-PIN, with no primary-source confirmation that a US-only operator can obtain a key without engaging an in-Korea agent; (3) the canonical field reference and sample payloads are inside Korean-language PDFs behind the portal nav, so the schema work is non-trivial; and (4) the operation tier (which we'd need to scale beyond hobby usage and to be on solid commercial footing) is discretionarily reviewed by KIPI.

---

## Executive Summary

KIPRIS Plus is a real REST/XML API covering all four KR rights (patents, utility models, designs, trademarks) at `kipo-api.kipi.or.kr/openapi/service/…`, with both free-text and field-structured search, 1948-onward backfile, and a 1,000-call/month free tier rising to a flat ~USD 1,783/yr operation tier. We can technically proxy it. **However, the verdict is yellow, not green:** the Terms of Use forbid sharing one Authentication Key across users ([§11](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030)), the operation tier is "carefully reviewed and approved on a limited basis" ([data.go.kr 15043964](https://www.data.go.kr/en/data/15043964/openapi.do)), and signup may require Korean identity verification with no documented foreigner workaround. The biggest operational risk is the one-key-per-member rule colliding head-on with multi-tenant proxy usage — building a clean per-user OAuth handoff (each user brings their own KIPI key) is the safest design, but it adds account-onboarding friction in any English-only product surface and likely a Korean phone in the loop.
