# CNIPA China (CN) — national

**Layer:** national
**Jurisdiction:** CN (WIPO ST.3: CN)
**Issuing body:** China National Intellectual Property Administration (国家知识产权局)
**Rights administered:** patent, utility_model, trademark, design (plus geographical indications and integrated-circuit layout designs, administered by CNIPA but out of scope for this synopsis)
**Working languages:** Mandarin Chinese (primary; operational); English (information site only)
**Connector status:** skipped (route via higher layers; no native CNIPA connector planned)
**Last verified:** 2026-05-16
**Manifest entry:** not listed in `coverage/sources.yaml` — covered transitively via `WO/EPO` (INPADOC CN feed)

**Detail surveys:**
- [`connectors/cnipa.md`](../connectors/cnipa.md) — 2026-05 asset-by-asset survey (15 assets: PSS, SBJ, designs, bulk data, PRCD, courts, GIs, plant-variety rights, statutes)
- [`waves/2026-05-16-coverage-batch-2/cn-cnipa.md`](../waves/2026-05-16-coverage-batch-2/cn-cnipa.md) — 2026-05-16 grounded re-evaluation

**Higher layers covering this office transitively:**
- **EPO OPS / INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — CN patent biblio + abstracts + family + legal events (since 2024-12, ST.27-formatted). The single most important transitive channel.
- **WIPO Patentscope** — CN national patent collection (~3M docs; full text in CN from 1996+; English bibliographic data 1985+; full-text translation via WIPO Translate).
- **WIPO Hague Express** — CN designs filed via Hague (post 2022-05-05 only; CN joined Hague 2022-05-05).
- **WIPO Madrid Monitor / Global Brand Database** — TMs designating CN via Madrid (a *subset* of CN TMs; pure CN national filings not covered).
- **WIPO Lex** — Patent Law, Trademark Law, AUCL, Copyright Law statutes for CN.

---

## §1 Mission

CNIPA is **the world's #1 patent office by application volume** — 1.8M
patent applications filed in 2024 (per
[WIPO IPI 2025](https://www.wipo.int/web-publications/world-intellectual-property-indicators-2025-highlights/en/patents-highlights.html)),
plus 6.4M trademark applications the same year. It is one of the IP5
offices (USPTO, EPO, JPO, KIPO, CNIPA) and the dominant filer in 8
of 10 frontier technology fields tracked by WIPO. Coverage of
Chinese patents, utility models, trademarks, and designs is
strategically essential for any global prior-art, ownership, or
freedom-to-operate workflow.

For agents working on Chinese IP, the operational gap between
"strategic importance" and "programmatic accessibility" is the
largest of any major office. CNIPA's *own* systems are effectively
closed to foreign programmatic users. Practical access flows
through three higher-layer proxies (EPO OPS, WIPO Patentscope, WIPO
Hague) for as much of the data as those proxies cover.

## §2 What's unique here (only available from CNIPA, if at all)

- **CN-language full text** (description + claims) of utility
  models and pre-1996 inventions — EPO OPS and Patentscope are
  thinner here than for inventions from 1996+.
- **CN-specific procedural events** — PRCD reexamination/invalidation
  decisions, register changes, fee payments. Dec 2024 ST.27 upgrade
  aligns legal-status emissions to a WIPO standard (flows to
  INPADOC), but the most granular events remain CNIPA-only.
- **Utility models** — CN is the world's #1 UM jurisdiction; many
  CN UMs never appear in EPO INPADOC's UM subset.
- **CN-only trademarks** — the vast majority of CN TM filings are
  national-only and live only in SBJ; Madrid covers a thin slice.
- **Pre-2022 CN-only design patents** — CN joined Hague 2022-05-05;
  pre-2022 designs are CNIPA-only.

## §3 Programmatic surfaces

Every CNIPA-operated surface is 🔴 RED against the zero-infra-
proxy constraint. There is **no documented public REST/JSON/XML
API** for any of patents, utility models, trademarks, or designs.
Live probes from US egress on 2026-05-16: `412` on `pss-system`,
`cpquery`, `ggfw`, `sso`; `406` on `wcjs`; `403` on the developer-
FAQ page itself.

| Surface | Right(s) | Endpoint | Auth | Format | Verdict |
|---|---|---|---|---|---|
| Patent Search & Analysis (PSS) | patent, UM, design | [pss-system.cponline.cnipa.gov.cn](https://pss-system.cponline.cnipa.gov.cn/) | Email account + slider CAPTCHA + OTP | HTML SPA | 🔴 |
| China & multi-country exam info (cpquery) | patent legal status | [cpquery.cponline.cnipa.gov.cn](https://cpquery.cponline.cnipa.gov.cn/) | Email account + CAPTCHA | HTML SPA | 🔴 |
| Patent business processing (cponline) | filing + prosecution | [cponline.cnipa.gov.cn](https://cponline.cnipa.gov.cn/) | Login wall | HTML SPA | 🔴 |
| Trademark online search (WCJS) | trademark | [wcjs.sbj.cnipa.gov.cn](https://wcjs.sbj.cnipa.gov.cn/) | Anon. search + slider CAPTCHA; account requires CN mainland phone + real-name verification (late 2025) | HTML SPA | 🔴 |
| Trademark services portal (SBJ) | trademark | [sbj.cnipa.gov.cn](https://sbj.cnipa.gov.cn/) | Same as WCJS | HTML SPA | 🔴 |
| IP Data Resources Public Service (ipdps) | bulk catalog | [ipdps.cnipa.gov.cn](https://ipdps.cnipa.gov.cn/) | Institutional contract (Chinese entity); 45 orgs served per WIPO CWS/ATR/PI/2024/CN | Bulk XML | 🔴 |
| National IP Public Service Platform (ggfw) | unified gateway | [ggfw.cnipa.gov.cn](https://ggfw.cnipa.gov.cn/) | SSO; same CN-phone constraints | HTML SPA | 🔴 |
| Patent publication PDFs (epub) | published patents | `http://epub.cnipa.gov.cn/` | Login | PDF | 🔴 |
| Office-to-office PCT M2M API | patent | Bilateral with WIPO ([CNIPA WIPO API Day 2023](https://www.wipo.int/edocs/mdocs/cws/en/wipo_webinar_standards_api_2023_1/wipoapiday2023_day2_zhang.pdf)) | Inter-office contract | XML | 🔴 (not a public developer surface) |

Material details for the most consequential of these:

- **PSS / cpquery / sbj / ggfw** — JS SPAs behind WAFs that return
  `412 Precondition Failed` / `406 Not Acceptable` to unattested
  clients (probe 2026-05-16). Internal AJAX endpoints exist but
  are undocumented and not contractually stable.
- **`wcjs.sbj.cnipa.gov.cn`** — late-2025 account-registration
  tightening (Chinese mainland phone + real-name verification)
  forecloses account-based foreign machine access. Per [Yucheng IP
  Law 2025](https://yciplaw.com/china-trademark-database-search-guide-2025/);
  CNIPA's own English procedure page confirms foreign applicants
  must engage a recorded Chinese trademark agency
  ([art_2996_205374](https://english.cnipa.gov.cn/art/2026/3/17/art_2996_205374.html)).
- **`ipdps.cnipa.gov.cn`** — consolidated bulk-data portal (Oct
  2023 launch; 60 data types as of 2024 per [WIPO
  CWS/ATR/PI/2024/CN](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640996450/CWS+ATR+PI+2024+CN)).
  Distribution to "45 research institutions, IP service agencies,
  and enterprises on a targeted basis" — a closed list, not a
  public API.
- **December 2024 ST.27 legal-status upgrade.** CNIPA emits WIPO
  ST.27-compliant legal-status events as of Dec 2024 — surfaced
  through the cpquery UI, not as an API. This *should* improve
  what INPADOC ingests; see §5.
- **2026-01-01 XML-only filing mandate.** Patent applications must
  be filed in WIPO ST.96-style XML from Jan 1 2026 — applicant-
  facing, not searcher-facing, but indicates the internal data is
  already ST.96-shaped.

## §4 Fee schedule (snapshot 2026-05-16)

**Detail file:** *pending dedicated fee research*
**Official schedule:** [`english.cnipa.gov.cn/col/col3000/`](https://english.cnipa.gov.cn/col/col3000/index.html) (Patent Fee Schedule, in CNY)
**Effective date:** Current schedule; reduced-fee policy for SME annuities (85% discount) in effect; open-license annuity discount 15% (2024).

Indicative headline figures in CNY (from CNIPA English fee schedule, 2026-05-16 snapshot):

| Category | Amount (CNY) | Notes |
|---|---|---|
| Filing — invention patent | 900 | excludes additional fees |
| Filing — utility model | 500 | |
| Filing — design | 500 | |
| Filing — additional priority claim, each | 150 | |
| Printing fee on publication | 100 | |
| Substantive examination | 2,500 | invention only |
| Annuity yrs 1–3 | 900 | per year |
| Annuity yrs 4–6 | 1,200 | per year |
| Annuity yrs 7–9 | 2,000 | per year |
| Annuity yrs 10–12 | 4,000 | per year |
| Annuity yrs 13–15 | 6,000 | per year |
| Annuity yrs 16–20 | 8,000 | per year |
| PTA-period annuity (per year of extension) | 8,000 | post-2020 Patent Law |
| Reexamination | 1,000 | invention |
| Evaluation report (utility model / design) | 2,400 | |
| Invalidation petition | 3,000 | |

Fee reductions for individuals and SMEs run up to 85% on annuities;
open-license patents get a separate 15% reduction. TM and IC
layout-design schedules are on the same English Fees landing.

## §5 Connector strategy

### What we cover today

- **CN patent biblio + abstracts + family + legal events** —
  transitively via `patent_client_agents.epo_ops`. The December
  2024 ST.27 upgrade on CNIPA's side improves the *fidelity* of
  what flows to INPADOC.
- **CN patent statutes (Patent Law, Implementing Regs)** — via
  WIPO Lex; statutes corpus is the standard pattern (mirror once,
  expose by article).
- **PCT applications with CN as receiving office or designated
  state** — via WIPO Patentscope (Patentscope is not yet wrapped
  as a first-class connector; pending).

### What we should add (if anything)

**Nothing in the form of a direct CNIPA connector.** The verdict is
🔴 RED — no public API, hostile WAFs, mainland-phone real-name
verification on the trademark service since late 2025, bulk
products gated to Chinese registered entities.

If we want richer CN coverage beyond what EPO OPS gives:
- **Patentscope wrap** (general — applies to CN and many other
  collections at once) — would unlock CN full-text descriptions
  and claims back to 1996 with English MT. Cross-reference
  [`BACKLOG.md`](../BACKLOG.md). This is *not* a CNIPA connector;
  it's a WIPO-layer connector that improves CN coverage.
- **WIPO Hague Express wrap** for post-2022 CN designs — small,
  trivial.

### What we should NOT add

- **Direct CNIPA scraping or account-based integration** — ToS
  hostile, WAF/CAPTCHA hostile, account-creation impossible for
  foreigners on the new TM service. Strategic memory: do not
  re-evaluate.
- **CNIPA bulk-data subscription** — requires a Chinese registered
  entity counterparty; out of scope for an open-source connector.
- **Commercial proprietary feeds (IncoPat / PatSnap / Innography)**
  — enterprise NDA contracts; could be supported via an optional
  BYO-key plugin pattern in the future, not core.

### Next steps

1. Track upstream changes: re-verify the "real-name mainland-phone"
   constraint on the TM service in 6 months; if CNIPA opens a
   foreign-developer programme, re-evaluate.
2. Improve CN coverage *transitively* by scoping a Patentscope
   connector (separate workstream — Patentscope improves CN, JP,
   KR, AR, and PCT coverage simultaneously).
3. Confirm via a live INPADOC call that the December 2024 ST.27
   legal-status events actually appear in the EPO OPS CN feed
   today (not just announced by CNIPA).
4. Dedicated fee-schedule research file (`fee-schedules/cn-cnipa-fees.md`).

## §6 Open questions

- Does WIPO Patentscope's CN feed give **full-text claims and
  descriptions** where EPO OPS lacks them? Probe against a known
  utility model and a pre-2010 invention before architecting.
- How current is the ST.27 CN legal-status feed *as it surfaces in
  EPO INPADOC*? CNIPA announced Dec 2024; EPO ingestion lag is a
  separate question.
- For **CN utility models** — what fraction live in INPADOC vs.
  CNIPA-only? Quantify the unique-here gap via coverage probe.
- For **CN designs pre-2022** — any acceptable third-party mirror,
  or simply document the gap?
- Is the **WIPO Global Brand Database** mirroring any CN national
  TMs beyond Madrid designations? Assume no full national coverage
  until verified.
- Watch for post-2025 changes to the foreign-applicant TM account-
  creation rules (CNIPA English news channel).

## §7 References

Primary sources only:

- [CNIPA English homepage](https://english.cnipa.gov.cn/)
- [CNIPA patent fee schedule (EN, CNY)](https://english.cnipa.gov.cn/col/col3000/index.html)
- [CNIPA — foreign trademark applicants procedure](https://english.cnipa.gov.cn/art/2026/3/17/art_2996_205374.html)
- [CNIPA — foreign-applicant priority documents](https://english.cnipa.gov.cn/art/2026/3/17/art_3645_205365.html)
- [Patent Search & Analysis System (PSS)](https://pss-system.cponline.cnipa.gov.cn/)
- [China & multi-country patent examination info query (cpquery)](https://cpquery.cponline.cnipa.gov.cn/)
- [Patent Business Processing System (cponline)](https://cponline.cnipa.gov.cn/)
- [Trademark online search (WCJS)](https://wcjs.sbj.cnipa.gov.cn/)
- [Trademark services portal (SBJ)](https://sbj.cnipa.gov.cn/)
- [IP Data Resources Public Service System (ipdps)](https://ipdps.cnipa.gov.cn/)
- [National IP Public Service Platform (ggfw)](https://ggfw.cnipa.gov.cn/)
- [WIPO CWS/ATR/PI/2024/CN — Annual Technical Report](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640996450/CWS+ATR+PI+2024+CN)
- [WIPO CWS/ATR/TM/2024/CN — Annual Technical Report (Trademarks)](https://confluence.wipo.int/confluence/pages/viewpage.action?pageId=1640996457)
- [CNIPA WIPO API Day 2023 presentation](https://www.wipo.int/edocs/mdocs/cws/en/wipo_webinar_standards_api_2023_1/wipoapiday2023_day2_zhang.pdf)
- [WIPO API Catalog for IP](https://apicatalog.wipo.int/)
- [WIPO IPI 2025 Patent Highlights](https://www.wipo.int/web-publications/world-intellectual-property-indicators-2025-highlights/en/patents-highlights.html)
- [`connectors/cnipa.md`](../connectors/cnipa.md) — 2026-05 detail survey

---

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis; verdict RED. Material drift from older `connectors/cnipa.md`: (a) Chinese-mainland-phone real-name verification became mandatory for the trademark service account in late 2025; (b) December 2024 ST.27 legal-status upgrade improves what EPO OPS receives; (c) `ipdps.cnipa.gov.cn` added as the consolidated bulk-data portal; (d) older 917564.htm "Chinese Patent XML Data" page now 404. | Distilled from [`connectors/cnipa.md`](../connectors/cnipa.md) + [`waves/2026-05-16-coverage-batch-2/cn-cnipa.md`](../waves/2026-05-16-coverage-batch-2/cn-cnipa.md) |
