# GCC Patent Office Connector Survey

One-page survey of the GCC Patent Office (GCCPO) and the six Gulf member-state national IP offices for `patent-client-agents`. **Bottom line up front: skip GCC as a v1 target.** The unified regional grant system was abolished by the GCC Supreme Council effective 5/6 January 2021; the surviving register is a closed corpus fading toward ~2041, and the only Gulf national office with a usable public search UI (SAIP) trails the IP5 in digital maturity by a decade.

## Cross-asset comparison

| # | Asset | Endpoint | Auth | Format | Live? |
|---|-------|----------|------|--------|-------|
| 1 | GCCPO Advanced Search | `gccpo.org/CustomersService/Adv_SearchEn` | None | HTML form, EN/AR | Yes (closed register + post-2023 outsourced files) |
| 2 | GCCPO Patent Gazette | `gccpo.org/Doc/PatentGazette/Gazette/Gazette-E/{n}.pdf` | None | PDF (EN), AR mirror | Yes (~93 issues to Nov 2024) |
| 3 | WIPO Lex — GCC Patent Regulation (1992, 2014 amendment) | `wipo.int/wipolex/.../14915` | None | HTML + PDF (AR/EN) | Yes |
| 4 | SAIP IP Search (KSA) | `ipsearch.saip.gov.sa` | None | HTML, EN/AR | Yes (registered rights from ~2013, no pending apps) |
| 5 | UAE MoE patent e-services | `services.economy.ae` / `moet.gov.ae` | UAE Pass for filing | HTML form | Yes (transactional, not search) |
| 6 | UAE MoE Open Data | `moet.gov.ae/en/moe-opendata?q=patent` | None | CSV/Excel | Yes (aggregate stats only) |
| 7 | Kuwait / Qatar / Bahrain MoCI registers | n/a | n/a | n/a | **No public online search**; filings routed to GCCPO since 2023 |
| 8 | Oman MoCIIP patent search | Directorate of IP under MoCIIP | n/a | HTML (per Saba IP, 2024) | Reported live; no documented URL/API |

No PyPI client exists for any of these.

## GCCPO register and gazette

`gccpo.org` is up as of May 2026. A `.NET` web app with a 13-field advanced-search form covering application/publication number, applicant, inventor, title, IPC, priority data. No API, classic ASP.NET viewstate plumbing. Patent Gazette issues are static numbered PDFs in EN and AR — issue 93 (Nov 2024) is the most recent confirmed.

**Closure mechanics.** The GCC Supreme Council abolished the unified regional patent in 2021. Pre-2021 grants (~70k applications) remain valid in all six member states through their 20-year term — latest expiry ~2041, so the unitary corpus is a 15-year fade. The 2022 amended GCC Patent Regulations created a **regional examining authority**, not a relaunched regional grant office: Bahrain (Jan 2023), Kuwait (Jan 2023), and Qatar (Jul 2023) route filings to GCCPO for centralized examination, but resulting patents are granted at the national level and valid only in the originating country. Saudi Arabia, UAE, and Oman have not joined. There is no public discussion of restoring unitary grants — no "Doha Declaration" surfaced in 2024-2025 tracking. WIPO Magazine's Mar 2025 piece describes the new examination model, not a unitary-grant revival.

## GCC Patent Regulation (legal framework)

WIPO Lex hosts the Patent Regulation of the Cooperation Council for the Arab States of the Gulf (record id 14915, originally 22 Sept 1992; the 2014 amendment is the operative version through the 2021 sunset). The 2022 amended Regulations that established the post-2021 outsourced model do not yet appear in WIPO Lex in English — Kadasa and Gowling WLG describe them but no canonical EN text is indexed. **Drops in for free** as part of the already-planned `wipo_lex` connector — zero GCC-specific engineering needed.

## Member state national offices

**SAIP (Saudi Arabia)** — `ipsearch.saip.gov.sa`, launched late 2022, is the only GCC national office with a free public search UI. Covers registered patents + designs + TMs from ~2013 onwards; **no pending applications, no pre-2013 backfile.** EN/AR. No documented API. The 2025 SAIP fast-track grant procedures are real, but the public data layer is still a website. Of all Gulf nationals, this is the only one worth a v1 wrapper if customer demand emerges, and the shape would mirror `ipo_india`.

**UAE (MoET)** — `moet.gov.ae` handles patent registration via DIEPD. `services.economy.ae` is transactional (file/renew), not searchable. Open Data portal carries aggregate statistical CSV/Excel only — useful for landscape charts, useless for register lookup. The Jan 2025 "Patent Hive" initiative promises to cut grant time from 42 to 6 months but adds no new public data surface. **ADGM and DIFC** operate common-law commercial-court regimes that *adjudicate* IP disputes (post-2019 DIFC IP legislation) but do not maintain patent registers — registration remains federal MoET. ADGM public registers cover companies/financials only.

**Kuwait, Qatar, Bahrain** — three smallest national offices; all three route filings to GCCPO since 2023. None publishes a public online register or search UI. Practitioner intermediaries describe internal databases, not public ones. WIPO INSPIRE entries list no machine-readable feed.

**Oman (MoCIIP)** — Saba IP reported in 2024 that patent search "is now possible" via the Directorate of IP under MoCIIP; no URL, no documented API, no confirmed third-party scrape pattern. Not yet buildable.

## v1 verdict: **SKIP**

Skip GCC Patent Office and all six member-state national offices for v1. Reasons:

1. **The unified regional patent is a sunsetting asset class** (~2041 cliff).
2. **Post-2023 GCCPO files are national patents**, not regional — better consumed via national offices, none of which expose machine-readable feeds.
3. **All web fronts are ASP.NET / viewstate / form-only** — same brittle pattern as IPO India and INPI Brazil pePI. Belongs on the skip-list, not the build-list.
4. **WIPO Patentscope and EPO OPS cover the prior-art use case.** GCCPO-published applications are indexed in Patentscope; INPADOC covers PCT national-phase entries into Gulf states.
5. **WIPO Lex absorbs the statutory side for free** — no GCC-specific code.

If/when a paying customer forces the issue, **SAIP is the only national office that even has a public search UI** — start there, treat it as a small `ipo_india`-shape scrape, accept that pending applications and pre-2013 grants are out of scope.

## ARIPO / OAPI comparison

Both ARIPO and OAPI are **active** regional offices (unlike GCCPO) and rank ahead of GCC if regional-office demand surfaces:

- **ARIPO** — online register at `eservice.aripo.org/pdl/pqs/quickSearchScreen.do` (quick) and `/pah/advancedSearchScreen.do` (advanced). KIPO-built infrastructure, so similar bones to KIPRIS. Form-only HTML, no API, but more modern than GCCPO.
- **OAPI** — `oapi.int/en/`. Bangui Agreement covers 17 Francophone-African states with unitary grants. French-language, smaller register, but unitary-patent value is intact.

Both belong in Tier 3 alongside Israel / Singapore / Taiwan if regional-office demand materializes. **Both rank higher than GCCPO because they still issue unitary regional patents.**

## Open questions

1. Will SAIP publish a documented API as part of Saudi Vision 2030 open-data commitments? Re-check `ipsearch.saip.gov.sa` quarterly.
2. Does UAE MoE expand Open Data beyond aggregate stats under the 2025 "Patent Hive" initiative?
3. Are the 2022 amended GCC Patent Regulations available in authoritative EN anywhere outside law-firm summaries? Track for WIPO Lex addition.

## Decision

Drop GCC and all six Gulf national offices from the v1 buildable list. Add to watch list with quarterly check cadence; promote only on confirmed paying-customer demand. WIPO Lex absorbs the statutory layer cleanly.
