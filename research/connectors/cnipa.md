# CNIPA & China IP Data Source Survey

Connector-scoping survey for `patent-client-agents`. China is the largest patent/trademark office by volume but the hardest major jurisdiction to integrate. This report inventories what is accessible from outside China, what requires a commercial license, and what is now effectively closed.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Bulk? | Outside-China feasibility |
|---|-------|-----|------|--------|-------|---------------------------|
| 1 | CNIPA PSS patent search | pss-system.cnipa.gov.cn | Email login + CAPTCHA | HTML / dynamic JS | No | Hard — login, CAPTCHA, geo-fragility |
| 2 | CNIPA trademark search (SBJ) | sbj.cnipa.gov.cn / wcjs.sbj.cnipa.gov.cn | Slider-CAPTCHA, no key | HTML | No | Hard — CAPTCHA, frequent geo-block |
| 3 | CNIPA design patents (外观设计) | Same PSS portal | Same | HTML / PDF | No | Same as #1 |
| 4 | CNIPA bulk data | CNIPA "Patent Information Service" | Contract w/ China entity | XML / PDF | Yes (contracted) | Effectively no without local entity |
| 5 | PRCD invalidation decisions | cponline.cnipa.gov.cn (announcements) | None for index, CAPTCHA for full text | HTML / PDF | No | Partial — scraping feasible, brittle |
| 6 | Court decisions (SPC IP Tribunal, Beijing IP Court) | wenshu.court.gov.cn, ipc.court.gov.cn | Chinese phone # since Aug 2021 | HTML | No (intentionally restricted) | Largely closed |
| 7 | Chinese GIs | english.cnipa.gov.cn GI column + MARA AGI list | None | HTML / PDF lists | Yes (static lists) | Feasible — small static datasets |
| 8 | MARA plant variety rights | nybkjfzzx.agri.cn / cnpvp.cn | None for browse | HTML | No | Feasible — scraping |
| 9–15 | Statutes & guidelines (Patent, Implementing Regs, Examination Guidelines, Trademark, AUCL, Copyright, GI/PVP regs) | WIPO Lex, NPC Observer, China Law Translate | None | HTML / PDF | Yes (static) | Easy — static documents |

## 1. CNIPA PSS — Patent Search (pss-system.cnipa.gov.cn)

Flagship public search covering >100 jurisdictions with citations, family, legal status. Nine-language UI translates labels only — record content (titles, abstracts, claims) stays Chinese unless an MT column is opened.

- **URL:** `http://pss-system.cnipa.gov.cn/sipopublicsearch/inportal/i18n.shtml`; `cponline.cnipa.gov.cn` variant for Patent Business Processing.
- **Auth:** Free email account + CAPTCHA; mobile verification on some flows.
- **Rate limits:** Undocumented; heavy querying triggers CAPTCHA escalation and IP blocks.
- **Format:** JS-rendered HTML with AJAX pagination; no documented REST contract.
- **Coverage:** CN invention + utility model + design, 1985-09-10 to present; status, exam history, transfers.
- **Bulk:** Only via CNIPA Patent Information Service contracts requiring a Chinese counterparty.
- **ToS:** Personal/research only; commercial redistribution prohibited.
- **Python clients:** No maintained library. `github.com/CNIPA` is internal tooling, not a client. Wild-scraper repos break on each CAPTCHA refresh.

## 2. CNIPA Trademark Search (sbj.cnipa.gov.cn)

"Comprehensive Service System for Trademark Online." Public search at `wcjs.sbj.cnipa.gov.cn`. English label translations only; content Chinese.

- **URL:** `https://wcjs.sbj.cnipa.gov.cn` (search) + `https://sbj.cnipa.gov.cn` (portal). Internal endpoints: SISTM (similar-mark), SGTMI (detail).
- **Auth:** Slider-CAPTCHA every session; phone OTP on heavy use.
- **Rate limits:** Aggressive bot-detection; IP bans common after a few hundred queries.
- **Format:** HTML scrape, no JSON.
- **Coverage:** All CN TM applications/registrations; Madrid extensions by app number.
- **Bulk:** None public. Commercial monitors (CompuMark, Corsearch, MarkMonitor) license via Chinese partners.
- **Python:** None solid.

## 3. CNIPA Design Patents (外观设计)

Same PSS portal, same access model. 2020 Patent Law adds partial designs + 15-year term; China joined **Hague Agreement** 2022-05-05, so post-2022 designs are also on WIPO **Hague Express** (`https://www3.wipo.int/designdb/hague/en/`) — public, no auth, much friendlier than PSS. Pre-2022 CN-only designs remain PSS-only.

## 4. CNIPA Bulk Data

CNIPA "Patent Information Service" sells XML packs (front-file weekly + historical), but contracts require a Chinese registered entity. No USPTO-style bulk dump. **EPO OPS is the de-facto bulk CN channel** — CNIPA→EPO data exchange surfaces CN bibliographic, abstract, full-text, and INPADOC legal-events under our existing `epo_ops` client. Coverage: excellent for invention patents, weaker for utility models, weakest for designs.

## 5. PRCD — Reexamination and Invalidation Decisions

Now inside CNIPA's Reexamination and Invalidation Department (former Patent Reexamination Board). Decisions announced (公告) via `https://cponline.cnipa.gov.cn`. No PTAB-equivalent JSON feed.

- **Auth:** Index open; PDF download needs session + CAPTCHA.
- **Volume:** ~6–8k invalidation decisions/yr; ~30k+ reexamination decisions/yr.
- **Format:** Chinese-text PDF (text-layer present, OCR usually unnecessary).
- **Bulk alternative:** CIELA-Rouse, Changtsi, IPHouse compile structured datasets at enterprise pricing.

## 6. Beijing IP Court / SPC IP Tribunal

The most-degraded asset of the past five years.

- **China Judgments Online (wenshu.court.gov.cn):** Since Aug 2021 requires a **Chinese mobile number**, caps results at 600/query, removed >11M cases. Published count: 14.9M (2021) → 10.4M (2022) → 5.11M (2023). An internal-only "National Court Cases Database" now backs many categories.
- **SPC IP Tribunal (`enipc.court.gov.cn`):** Selected English summaries only, not a docket.
- **Beijing IP Court (`bjipc.gov.cn`):** Selected decisions.
- **Commercial:** OpenLaw, Wolters Kluwer CN, Westlaw China, Lexis China — all Chinese-language, enterprise.
- **Wikimedia China Judgments Online Preservation Program** mirrors pre-2021 dumps (historical only).

## 7. Geographical Indications

Post-2018 reform consolidated GI authority under CNIPA. Three tracks: (a) CNIPA collective/certification TM GIs (on TM portal); (b) CNIPA sui generis GI Products — list as PDF/HTML in the GI column of english.cnipa.gov.cn; (c) MARA Agricultural GIs — separate MoARA list. End-2020 totals: 2,391 protected GI products; 6,085 GI registrations; 9,479 logo users. Static lists, easy to mirror quarterly. EU–China GI Agreement (Nov 2021) cross-protects 100 names per side; table on DG AGRI's site.

## 8. MARA Plant Variety Rights

Two-track: MARA for agricultural crops; State Forestry and Grassland Administration for forestry/ornamental species. MARA search at `nybkjfzzx.agri.cn`; UPOV-aligned database at `cnpvp.cn`. Browse-only HTML, no API, no CAPTCHA on index. May-2025 revised Regulations on Protection of New Plant Varieties introduce essentially-derived varieties (EDV) and lengthen terms. "CNVPO" in the brief isn't the office's current self-identification — MARA PVP and SFGA PVP are the operational bodies. Easy: ~25k variety records combined, text, no auth.

## 9–15. Substantive law sources

Reliable English text exists for every statute. Ship as static, cached resources (mirror once, don't scrape per-call) — same pattern as MPEP/TMEP.

| # | Law | Best source | Notes |
|---|-----|------------|-------|
| 9 | Patent Law (4th amend., 2020/2021) | WIPO Lex `legislation/details/21027` | Official translation; in force 2021-06-01 |
| 10 | Implementing Regulations of the Patent Law | WIPO Lex + China Law Translate | 2024 revision (effective 2024-01-20) |
| 11 | Guidelines for Patent Examination 审查指南 | english.cnipa.gov.cn `transfer/patentexamination/referencematerials/` | 2024 edition in force; **2026-01-01 revision announced**. CNIPA publishes English PDFs but on a lag; firm summaries (Spruson & Ferguson, Wilson Sonsini, Hogan Lovells) are useful supplements |
| 12 | Trademark Law (2019) + Implementing Regs | WIPO Lex; AppInChina mirror | TML 2019 in force 2019-11-01 |
| 13 | Anti-Unfair Competition Law (2019, trade secrets in Arts. 9–10) | WIPO Lex `legislation/details/19557`; HongFang Law mirror | 2019 amendment shifts burden on alleged misappropriator |
| 14 | Copyright Law (2020) | WIPO Lex `legislation/details/21065` and `legislation/details/21066` | In force 2021-06-01 |
| 15 | GI Regulations + Plant Variety Regs | WIPO Lex; MARA gazette; May-2025 PVP revision | Multiple instruments — see assets 7–8 |

**Translation reliability:** WIPO Lex (authoritative, slow) > China Law Translate (community, quick + annotated) > firm summaries (context, not citation) > MOFCOM (uneven). Avoid lawinfochina.com for citation work.

## Commercial providers (the practical access path)

| Provider | CN coverage | API? | Cost signal |
|----------|------------|------|-------------|
| IncoPat (Clarivate-distributed) | Strongest CN coverage; daily updates from CNIPA | Yes — REST, enterprise contract | ~$30–80k/yr typical |
| PatSnap / 智慧芽 (Zhihuiya) | Strong CN; designs OK | Yes — REST, paid tier | Mid-five to low-six figures/yr |
| Innography | Acquired by Clarivate; analytics-focused | Limited API | Enterprise |
| CNIPR (国家知识产权局服务系统) | Free public lookup, no API | No | Free but scrape-only |
| WIPO Patentscope | Includes CN; English MT | Yes (limited REST) | Free |
| EPO OPS (already wrapped) | CN biblio + abstracts + INPADOC | Yes | Free tier sufficient |

None of IncoPat / PatSnap / Innography / CNIPR publish REST contracts publicly — NDA + contract required. For an open-source library, treat any commercial integration as an optional plugin, not core.

## Recommended v1 scope

Build only what's open, stable, and maintainable without a Chinese entity or commercial license:

1. **CN coverage via existing `epo_ops`** — add `get_cn_biblio`, `get_cn_legal_events` recipes. Lowest cost, highest value.
2. **WIPO Patentscope CN feed** — free JSON/XML, English MT; full-text where EPO lacks it.
3. **WIPO Hague Express** — post-2022 CN designs, trivial to wrap.
4. **CNIPA GI lists** (sui generis + MARA AGI) — static tables, quarterly refresh.
5. **MARA plant variety rights** — browse-only HTML, no auth, small dataset.
6. **Static law/regs corpus** — Patent Law, Implementing Regs, Examination Guidelines, Trademark Law, AUCL, Copyright Law, GI/PVP Regs. Mirror once, expose by article like MPEP.

## Skip list

- **CNIPA PSS scraping** — CAPTCHA + JS + ToS-hostile + brittle. Use EPO OPS / Patentscope.
- **CNIPA SBJ trademark scraping** — CAPTCHA + bot-blocking. License a commercial mirror if TM is required.
- **wenshu.court.gov.cn** — CN phone number since 2021-08, 600-result cap, sensitive removals. Effectively closed.
- **CNIPA bulk data contracts** — needs Chinese entity counterparty.
- **IncoPat / PatSnap / Innography APIs** — proprietary, enterprise; consider optional credentialed plugins, not core.
- **Beijing IP Court / SPC IP Tribunal full docket** — selected summaries only.

## Open questions

1. **2026 Examination Guidelines translation lag** — ship current EN edition + CN diff, or wait for official EN?
2. **CN designs pre-2022** — accept the EPO OPS gap, or build a Patentscope fallback?
3. **PRCD decisions** — Chinese-only PDFs + LLM translation pipeline acceptable?
4. **Commercial plugins** — ship optional `pca-incopat`/`pca-patsnap` (BYO key) or stay strictly open?
5. **Wenshu archive** — is the Wikimedia preservation snapshot legally clean to mirror, or external-pointer only?

## Sources

- [CNIPA PSS](http://pss-system.cnipa.gov.cn/sipopublicsearch/inportal/i18n.shtml) · [CNIPA English](https://english.cnipa.gov.cn/) · [WIPO Inspire: PSS](https://inspire.wipo.int/patent-search-and-analysis-system)
- Trademark: [borsamip guide](https://www.borsamip.com/GuidanceTrademark/1260.html) · [Yucheng IP TM guide 2025](https://yciplaw.com/china-trademark-database-search-guide-2025/)
- WIPO Lex: [Patent Law 21027](https://www.wipo.int/wipolex/en/legislation/details/21027) · [Copyright Law 21065](https://www.wipo.int/wipolex/en/legislation/details/21065) · [AUCL 19557](https://www.wipo.int/wipolex/en/legislation/details/19557)
- Examination: [CNIPA EN reference materials](https://english.cnipa.gov.cn/transfer/patentexamination/referencematerials/index.htm) · [Wilson Sonsini 2024 rules](https://www.wsgr.com/en/insights/newly-amended-chinese-implementing-rules-for-patent-law-and-guidelines-for-patent-examination-bring-significant-changes-to-patenting-strategy-in-china.html) · [China IP Law Update – 2026 Guidelines](https://www.chinaiplawupdate.com/2025/11/chinas-national-intellectual-property-administration-releases-revised-guidelines-for-patent-examination-effective-january-1-2026/) · [Hogan Lovells – 2019 TML/AUCL](https://www.hoganlovells.com/en/publications/lightning-fast-ip-reform-in-china-trademark-law-and-anti-unfair-competition-law-amended)
- Invalidation: [IPKey study](https://ipkey.eu/sites/default/files/ipkey-docs/2022/Study%20on%20Patent%20Invalidation%20System%20in%20China_EN.pdf) · [Changtsi 2023 reference](https://www.changtsi.com/news/insight/2053.html)
- Courts: [SPC IP Tribunal EN](https://enipc.court.gov.cn/en-us/index.html) · [ChinaFile – wenshu decline](https://www.chinafile.com/reporting-opinion/viewpoint/verdicts-chinas-courts-used-be-accessible-online-now-theyre-disappearing) · [RFA – judgment access limits](https://www.rfa.org/english/news/china/china-court-records-12142023132626.html) · [Wikimedia CJO Preservation](https://meta.wikimedia.org/wiki/China_Judgments_Online_Preservation_Program)
- GIs / PVR: [CNIPA GI column](https://english.cnipa.gov.cn/col/col2997/index.html) · [Wanhuida GI](https://www.wanhuida.com/Content/2024/11-27/1050122814_print.html) · [Rouse PVP 2025](https://rouse.com/insights/news/2025/key-highlights-and-practical-suggestions-on-china-s-regulations-on-the-protection-of-new-plant-varieties-2025-revision) · [USDA FAS PVP](https://www.fas.usda.gov/data/china-china-releases-plant-variety-protection-regulations-comment)
- Commercial / context: [IncoPat](https://clarivate.com/intellectual-property/patent-intelligence/incopat/) · [PatSnap pricing](https://www.patsnap.com/pricing) · [WIPO Analytics Manual Ch. 7](https://wipo-analytics.github.io/manual/databases.html) · [CNIPA-EPO PCT cooperation](https://english.cnipa.gov.cn/art/2024/10/29/art_1340_195752.html)
