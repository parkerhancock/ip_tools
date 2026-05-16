# CNIPA China (CN/CNIPA) — wave research 2026-05-16

Re-evaluation of CNIPA's public programmatic surfaces against the
zero-infra-proxy constraint. Cross-references the 2026-05 detail
survey at [`research/connectors/cnipa.md`](../../connectors/cnipa.md);
drift notes inline.

**TL;DR:** Verdict **🔴 RED**. CNIPA exposes no public REST/JSON/XML
API to foreigners that we can proxy at runtime. Every primary
CNIPA endpoint is either (a) a JS-rendered HTML SPA behind WAF +
CAPTCHA, (b) a paid bulk-data product requiring a Chinese
counterparty, or (c) — newest blocker, December 2025 — an account
system that requires a Chinese mainland mobile number with
real-name verification, foreclosing foreign machine access
entirely. Route Chinese patents through EPO OPS (`epo_ops` already
shipped) and Patentscope. Skip CN trademarks and pre-2022 designs
unless a commercial mirror is licensed.

---

## 1. Endpoint

Primary public-facing CNIPA surfaces, grouped by right:

| # | Surface | Right(s) | URL | Tech |
|---|---------|----------|-----|------|
| 1 | Patent Search & Analysis System (PSS) | invention, utility model, design | `https://pss-system.cponline.cnipa.gov.cn/` | JS SPA, HTML, slider-CAPTCHA |
| 2 | China & Multi-country Patent Examination Info Query | patent prosecution / legal status | `https://cpquery.cponline.cnipa.gov.cn/` | JS SPA, slider-CAPTCHA |
| 3 | Patent Business Processing (cponline) | filing + post-grant | `https://cponline.cnipa.gov.cn/` | JS SPA, login wall |
| 4 | Trademark online search (商标网上检索) | trademark | `https://wcjs.sbj.cnipa.gov.cn/` | JS SPA, slider-CAPTCHA |
| 5 | Trademark services portal (sbj) | trademark | `https://sbj.cnipa.gov.cn/` | JS SPA, login wall |
| 6 | IP Data Resources Public Service System (ipdps) | bulk data product catalog | `https://ipdps.cnipa.gov.cn/` | JS SPA, contract-gated downloads |
| 7 | National IP Public Service Platform (ggfw) | unified gateway (patents/TM/IC layout/GI) | `https://ggfw.cnipa.gov.cn/` | JS SPA, WAF, SSO |
| 8 | Patent publication/announcement (epub) | published patents PDF | `http://epub.cnipa.gov.cn/` | HTML + login |
| 9 | Patent Affairs Bulletin (announcement-twice-weekly) | gazette | `https://english.cnipa.gov.cn/col/col2944/` | static HTML pages |
| 10 | Unified SSO | login plumbing | `https://sso.cnipa.gov.cn/am/` | OAuth-style endpoint, no docs |

**No documented public REST/JSON endpoint anywhere on `*.cnipa.gov.cn`.**

The closest thing to a published API surface is the inquiry page
`https://www.cnipa.gov.cn/jact/front/mailpubdetail.do?transactId=475602&sysid=6`
("如何申请对接API接口方式" — *how to apply to connect via API*), which
*itself* returns `403 Forbidden` from a US IP (probe 2026-05-16). The
companion inquiry `?transactId=459197&sysid=12` (中国及多国专利审查信息查询
系统接口 — *China & multi-country patent examination info query API*)
likewise 403s. The FAQ that would explain how to apply for API
access is itself geo-blocked.

WIPO's 2024 CNIPA Annual Technical Report (CWS/ATR/PI/2024/CN)
mentions that CNIPA built a **"National Intellectual Property
Public Service Platform"** in 2024 and *"provided standardized data
to 45 research institutions, intellectual property service
agencies, and enterprises on a targeted basis"* — a closed
distribution list, not a public API. [Source: `confluence.wipo.int`
CWS/ATR/PI/2024/CN](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640996450/CWS+ATR+PI+2024+CN).

Probe results from US egress, 2026-05-16:

```
HEAD https://pss-system.cponline.cnipa.gov.cn/        → 412 Precondition Failed (WAF JS challenge)
HEAD https://cpquery.cponline.cnipa.gov.cn/           → 412 Precondition Failed
HEAD https://wcjs.sbj.cnipa.gov.cn/                   → 406 Not Acceptable (WAF)
HEAD https://ipdps.cnipa.gov.cn/                      → 200 (SPA shell only — content behind XHR auth)
HEAD https://ggfw.cnipa.gov.cn/                       → 412 Precondition Failed
HEAD https://sso.cnipa.gov.cn/am/                     → 412 Precondition Failed
HEAD https://www.cnipa.gov.cn/jact/front/mailpubdetail.do?transactId=475602&sysid=6  → 403 Forbidden (WAF)
HEAD https://english.cnipa.gov.cn/                    → 200 (static English info pages OK)
```

## 2. Auth

Multi-layer authentication wall:

- **No API key program exists for foreign developers.** Searches and FAQs lead to a customer-service hotline (`010-62356655`); no online developer portal. [`cnipa.gov.cn` FAQ](https://www.cnipa.gov.cn/jact/front/mailpubdetail.do?transactId=475602&sysid=6) (403 from US).
- **PSS user accounts:** email registration + CAPTCHA on every login; OTP escalation on heavy query patterns.
- **Trademark services account (new CNIPA TM platform, in force 2025):** *"only a Chinese mainland mobile number that has passed real-name verification can be used for account registration, submission, and correspondence. As a result, foreign individuals or overseas companies cannot directly register and use the platform."* [Source: Yucheng IP Law, "China Trademark Database Search Guide 2025"](https://yciplaw.com/china-trademark-database-search-guide-2025/) — corroborated by CNIPA's own English-language guidance on foreign applicants requiring a recorded Chinese trademark agency: [`english.cnipa.gov.cn` art_2996_205374](https://english.cnipa.gov.cn/art/2026/3/17/art_2996_205374.html).
- **Bulk data products:** require a contract with CNIPA-recognised intermediaries (Chinese registered entity), not a US LLC. [Background: `english.cnipa.gov.cn` Products & Services index](https://english.cnipa.gov.cn/transfer/productsservices/index.htm).

Foreign-developer accessibility: **effectively zero** for the
authenticated surfaces. Anonymous HTML scraping of PSS/SBJ is
hostile-to-bots but technically possible; it violates ToS.

## 3. Query language

Each public-facing portal has its own ad-hoc HTML query form. No
documented field syntax, no operator grammar published in any
discoverable English page. PSS supports keyword + classification
(IPC/CPC) + publication-number + date-range; the actual
search-request shape lives in unpublished AJAX endpoints.

No primary source found for a queryable structured-search API.

## 4. Pagination

No documented pagination — public surfaces are HTML SPAs whose
internal AJAX call boundaries are not contractually stable. The
trademark portal `wcjs.sbj.cnipa.gov.cn` historically caps result
sets at a few hundred entries before challenging with a slider
CAPTCHA; no published number. No primary source found.

## 5. Response shape

Not applicable — no API. HTML SPAs render results client-side from
internal XHR responses (JSON-over-AJAX in places) that are not
versioned or documented and that change at CNIPA's discretion.
Patent-document XML *exists* as a product catalog (front-file weekly
XML feeds since 1985 conforming to WIPO ST.96 for newly filed
applications from 2026-01-01 onward) but is delivered via paid bulk
contracts, not API. [Source: Lexology, "CNIPA: Full Implementation
of Patent Electronic Filing in XML Format Effective from January 1,
2026"](https://www.lexology.com/library/detail.aspx?g=f4c7b612-de77-4092-89a8-848fea6ab2fb).

## 6. Coverage scope

What CNIPA's own systems theoretically cover (if access existed):

- **Invention patents** — back to 1985-09-10 (the date China's
  Patent Law took effect). ~5M+ applications cumulative; 1.8M
  filings in 2024 alone (WIPO IPI 2025). [Source: WIPO IPI 2025
  patents
  highlights](https://www.wipo.int/web-publications/world-intellectual-property-indicators-2025-highlights/en/patents-highlights.html).
- **Utility models** — China is the world's #1 UM jurisdiction by a
  large margin; this is a distinct right type that EPO INPADOC
  partially covers but with weaker depth.
- **Design patents** — back to 1985; post-2022-05-05 designs are
  also accessible via WIPO Hague Express (China joined Hague
  2022-05-05). Pre-2022 CN-only designs live only in CNIPA.
- **Trademarks** — 6.4M applications in 2024 alone; no foreign-
  accessible public API.
- **Patent legal status** — CNIPA upgraded its legal-status data
  service in December 2024 to emit WIPO ST.27-compliant events.
  This is exposed in the cpquery web UI, not as an API. [Source:
  CWS/ATR/PI/2024/CN, "real-time conversion of CNIPA's legal status
  data into legal status data that conforms to WIPO ST.27
  standards"](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640996450/CWS+ATR+PI+2024+CN).

## 7. Rate limits / quotas

Not published. Anti-bot WAFs (`412`, `406`, `403` on probe) and
client-side CAPTCHAs act as the *de facto* rate limits. Empirically
(per [Aztec Co., Ltd.'s 2024 walkthrough](https://aztec.co.jp/en/news/columns/5742)
and the older `connectors/cnipa.md` survey) heavy automated
querying produces escalating CAPTCHA + IP-level blocking within a
few hundred requests from a single egress.

## 8. Terms of service

CNIPA's English Products & Services pages (e.g.
`english.cnipa.gov.cn/transfer/productsservices/`) describe the
patent-XML and bulk products as licensed deliverables, not
free-to-redistribute. The PSS public-search system is for
personal/research use; commercial redistribution and large-scale
automated extraction are not permitted (per `connectors/cnipa.md`
2026-05 review; no English ToS hyperlink on the system page itself).

**Proxy-prohibited posture is the safe assumption** for all
non-public-information surfaces. No primary-source English ToS for
the PSS or trademark portals was located in this wave.

## 9. Operational notes

- **Language:** Mandarin Chinese throughout the operational
  systems. `english.cnipa.gov.cn` is an *information* site (news,
  fee tables, procedure overviews); the operational systems
  (`pss-system`, `wcjs`, `cpquery`, `ipdps`, `ggfw`) are
  Chinese-only with optional UI-label translation, not record
  translation.
- **Geo-fragility:** WAF challenges on every cponline subdomain
  from US egress (Cloud Run / residential alike per the older
  survey). The static English info site at `english.cnipa.gov.cn`
  responds normally; the operational systems do not.
- **December 2025 access tightening** — the trademark service
  platform now requires Chinese mainland phone + real-name
  verification for account creation, foreclosing the prior
  email-based registration path. [Source: Yucheng IP Law
  2025](https://yciplaw.com/china-trademark-database-search-guide-2025/).
- **December 2024 ST.27 upgrade** — legal-status events now
  WIPO-standard; this *should* flow into INPADOC's CN feed, making
  EPO OPS the de-facto channel for normalized CN legal status
  rather than scraping CNIPA directly. [Source:
  CWS/ATR/PI/2024/CN](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640996450/CWS+ATR+PI+2024+CN).
- **2026-01-01 XML-only filing** — patent applications must be
  submitted in WIPO ST.96-style XML starting 2026-01-01. Affects
  applicants, not searchers; relevant only as an indicator that
  CNIPA *internally* speaks ST.96 (so the future shape of any
  hypothetical foreign-facing API would likely be ST.96 XML).
  [Source: Lexology
  2026-01](https://www.lexology.com/library/detail.aspx?g=f4c7b612-de77-4092-89a8-848fea6ab2fb).
- **The `english.cnipa.gov.cn/transfer/productsservices/917564.htm`
  page referenced in older surveys ("Chinese Patent XML Data")
  returns `404 Not Found` (probe 2026-05-16).** The product
  catalog has been reshuffled into `ipdps.cnipa.gov.cn`.

## 10. Verdict — 🔴 RED

CNIPA fails the zero-infra-proxy constraint on every dimension:
no documented public REST/JSON/XML API, hostile WAFs, account
requirements that exclude foreigners (mainland phone + real-name
verification on the TM service since late 2025), bulk-data
contracts limited to Chinese registered entities, and a static
public information site that contains no programmatic surface.

**The right strategy is not to integrate CNIPA directly.** Route
Chinese patents through **EPO OPS** (already shipped as
`patent_client_agents.epo_ops`; CN biblio + abstracts + INPADOC
legal events including the new ST.27-formatted events) and
**WIPO Patentscope** (full-text descriptions + claims for CN
where EPO OPS lacks them; CN national collection added in 2013
covers ~3M docs with English bibliographic translation back to
1985 and CN full-text from 1996+). For CN designs filed via
**Hague Express** (post 2022-05-05), use the WIPO Hague feed.
For CN trademarks, the **WIPO Global Brand Database** carries
Madrid extensions designating CN but is *not* a full mirror of
the CNIPA national TM register; the practical paid alternatives
(IncoPat, PatSnap, Corsearch, CompuMark) require enterprise
contracts and are out of scope for an open connector.

---

## Drift vs. [`connectors/cnipa.md`](../../connectors/cnipa.md) (2026-05)

Older detail survey aligns with this wave's findings on the
fundamentals (no API, route via EPO OPS + Patentscope). Material
deltas to flag:

1. **TM platform real-name lockout (late 2025).** Older survey
   noted CAPTCHA + frequent geo-block. New finding: foreign
   accounts on the new trademark service platform are *structurally*
   barred — Chinese mainland phone + real-name verification is now
   required for account registration. Older survey predates this
   change. → **Synopsis §5 must note this as a hard "do-not-build"
   factor for any CN-TM connector ambition.**
2. **`english.cnipa.gov.cn/transfer/productsservices/917564.htm`
   is 404.** Older survey cited this page as the "Chinese Patent
   XML Data" product description. The product catalog has moved to
   `ipdps.cnipa.gov.cn`. → Synopsis §7 references should drop the
   404'd URL.
3. **December 2024 ST.27 legal-status upgrade** improves the
   *quality* of what EPO OPS receives. This is a *positive* drift —
   makes the "route via EPO OPS" strategy more powerful, not less.
   → Synopsis §2 should note the ST.27 alignment as a reason CN
   legal events via INPADOC are increasingly trustworthy.
4. **`ipdps.cnipa.gov.cn` exists and resolves (`200`)** — was not
   inventoried in the older survey as a distinct endpoint. It is
   the consolidated bulk-product catalog (replacing scattered
   "products & services" pages on the English site), still
   contract-gated, still no public API.

No reversals of the older survey's recommendation: **skip live
integration; route via EPO OPS + Patentscope + WIPO Hague + WIPO
Global Brand Database**.

---

## Primary sources cited above

- [`english.cnipa.gov.cn`](https://english.cnipa.gov.cn/) — CNIPA English landing page
- [`english.cnipa.gov.cn/col/col3000/index.html`](https://english.cnipa.gov.cn/col/col3000/index.html) — Patent fee schedule (English, in CNY)
- [`english.cnipa.gov.cn/art/2026/3/17/art_2996_205374.html`](https://english.cnipa.gov.cn/art/2026/3/17/art_2996_205374.html) — Foreign trademark applicants (agency required)
- [`english.cnipa.gov.cn/art/2026/3/17/art_3645_205365.html`](https://english.cnipa.gov.cn/art/2026/3/17/art_3645_205365.html) — Foreign-applicant priority documents
- [`english.cnipa.gov.cn/transfer/productsservices/index.htm`](https://english.cnipa.gov.cn/transfer/productsservices/index.htm) — Products and services overview
- [`ipdps.cnipa.gov.cn`](https://ipdps.cnipa.gov.cn/) — IP Data Resources Public Service System (Chinese)
- [`pss-system.cponline.cnipa.gov.cn`](https://pss-system.cponline.cnipa.gov.cn/) — Patent Search & Analysis System
- [`cpquery.cponline.cnipa.gov.cn`](https://cpquery.cponline.cnipa.gov.cn/) — China & multi-country examination info query
- [`wcjs.sbj.cnipa.gov.cn`](https://wcjs.sbj.cnipa.gov.cn/) — Trademark online search
- [`ggfw.cnipa.gov.cn`](https://ggfw.cnipa.gov.cn/) — National IP Public Service Platform
- [`confluence.wipo.int/CWS+ATR+PI+2024+CN`](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640996450/CWS+ATR+PI+2024+CN) — CNIPA Annual Technical Report 2024 to WIPO CWS
- [`confluence.wipo.int/CWS+ATR+TM+2024+CN`](https://confluence.wipo.int/confluence/pages/viewpage.action?pageId=1640996457) — CNIPA Annual Technical Report (Trademarks) 2024 to WIPO CWS
- [`wipo.int CNIPA PCT API service practice 2023`](https://www.wipo.int/edocs/mdocs/cws/en/wipo_webinar_standards_api_2023_1/wipoapiday2023_day2_zhang.pdf) — CNIPA's API service is for *office-to-office* PCT data exchange with WIPO, not for public developers
- [`apicatalog.wipo.int`](https://apicatalog.wipo.int/) — WIPO IP API catalog (Angular SPA; no CNIPA public-API entries discoverable in static HTML)
