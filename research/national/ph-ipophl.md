# IPOPHL Philippines (PH) — national

**Layer:** national
**Jurisdiction:** PH (WIPO ST.3: PH)
**Issuing body:** Intellectual Property Office of the Philippines (IPOPHL), attached agency of the Department of Trade and Industry; created under Republic Act 8293 (Intellectual Property Code of the Philippines)
**Rights administered:** patent, utility_model, industrial_design, trademark, geographical_indication, copyright (voluntary register); plant_variety is administered by the Bureau of Plant Industry under DA-NSIC, not IPOPHL
**Working languages:** English (primary, authoritative for all examination, decisions, and the WIPO Publish UI); Filipino is co-official under the 1987 Constitution
**Connector status:** **register-side: skipped** (no API + PH register is materially covered by upstream tools we already ship); **statutes-side: planned** (small `ph_statutes` static corpus for RA 8293 + IRRs + IPOPHL Memorandum Circulars)
**Last verified:** 2026-05-18
**Manifest entry:** not yet listed in `coverage/sources.yaml`

**Detail surveys:**
- [`waves/2026-05-18-secondary-nationals-wave/ph-ipophl.md`](../waves/2026-05-18-secondary-nationals-wave/ph-ipophl.md) — 2026-05-18 grounded research

**Higher layers covering this office transitively (the unusual part of the PH story):**
- **WIPO PATENTSCOPE** — full PH national patent collection (incl. published utility models); per the [data-coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) row 60: coverage **30.12.1899 → 17.11.2025**, **twice-monthly** refresh, last loaded **22.01.2026**. Materially current — ~3-month lag.
- **EPO INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — PH patents biblio + family + legal events through the standard EPO OPS country path; same `patent_client_agents.epo_ops` we ship today.
- **EUIPO TMview** ([tmdn.org/tmview](https://www.tmdn.org/tmview/)) — PH joined 2013 contributing ~325k TMs at launch; currently the canonical regional aggregator. IPOPHL itself is the **Country Lead** operating ASEAN TMview / ASEAN DesignView / ASEAN TMclass on EUIPO's TMDN infrastructure per the [IPOPHL handover announcement](https://www.ipophil.gov.ph/news/the-ipophl-takes-over-management-of-asean-it-tools-on-intellectual-property/).
- **ASEAN TMview / ASEAN DesignView** — regional consolidated, operated by IPOPHL on behalf of ASEAN. Discoverable via [aseanip.org](https://www.aseanip.org/) and the [ASEAN IP Register at `ip-register.aseanip.org`](https://ip-register.aseanip.org/wopublish-search/public/home).
- **WIPO Global Brand Database** ([`branddb.wipo.int/branddb/ph/en/`](https://branddb.wipo.int/branddb/ph/en/)) — mirrored since 2013 per the [coverage page](https://branddb.wipo.int/en/coverage).
- **WIPO Madrid Monitor** — international TMs designating PH (PH joined Madrid Protocol 25 Jul 2012).
- **WIPO Hague** — **does NOT designate PH** (PH is not a Hague contracting state).

---

## §1 Mission

IPOPHL is the Philippines' single national IP authority — patents,
utility models, industrial designs, trademarks, geographical
indications, and the voluntary copyright register — established
under Republic Act 8293 ([IP Code of the Philippines, 1997](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html)).
For agents, the operationally interesting fact is that IPOPHL is
**not just a national office** — it is the **regional Country Lead**
for the ASEAN IT tools (ASEAN TMview, ASEAN DesignView, ASEAN
TMclass), meaning IPOPHL operates EUIPO-style regional infrastructure
for the other ASEAN members. PH's national register is materially
visible upstream: PATENTSCOPE refreshes the PH national patent
collection twice a month, EUIPO TMDN ingests the PH TM register at
the ASEAN TMview cadence, and WIPO Global Brand Database mirrors
the same TM stream. The genuine national-only gap is **PH copyright
voluntary register entries, IPOPHL Bureau of Legal Affairs (BLA)
decisions, and pure-PH prosecution file history** — all of which
sit behind an Incapsula WAF on [`onlineservices.ipophil.gov.ph`](https://onlineservices.ipophil.gov.ph/)
and have no programmatic substrate. See [§3](#3-programmatic-surfaces).

## §2 What's unique here

- **PH utility models** — separate registration under RA 8293 §§
  108-114 with a 7-year non-renewable term and no substantive novelty
  examination; per the [IPOPHL UM overview](https://www.ipophil.gov.ph/services/utility-model/).
  Indexed in IPOPHL WIPO Publish and flowing into PATENTSCOPE's PH
  national collection via WIPO ST.6 data exchange.
- **PH-national-only trademarks** — Madrid IRs designating PH are
  visible via WIPO Madrid Monitor; pure PH-only TMs flow to TMview
  and Global Brand Database via the ASEAN TMview pipeline operated
  by IPOPHL itself.
- **PH-national-only industrial designs** — PH is **not** a Hague
  contracting state, so there is **no** higher-layer international-
  designation feed for PH designs; pure-PH designs live in IPOPHL +
  ASEAN DesignView (EUIPO-hosted regional view) only.
- **IP Code (Republic Act 8293) and IPOPHL Memorandum Circulars** —
  primary substantive law and the running secondary-rule layer.
  English-authoritative; freely mirrored on
  [lawphil.net](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html)
  and IPOPHL's own [administrative-issuances tree](https://www.ipophil.gov.ph/administrative-issuances/).
- **IPOPHL Bureau of Legal Affairs (BLA) decisions** — first-instance
  administrative IP-dispute body (oppositions, cancellations, inter
  partes). Notices and publications live at the
  [BLA Publication portal](https://onlineservices.ipophil.gov.ph/blapublication/) —
  WAF-walled, not reproduced by any higher layer.
- **Voluntary PH copyright register** — PH copyright is automatic
  under Berne, but IPOPHL operates a voluntary register at
  [Copyright Search](https://onlineservices.ipophil.gov.ph/CopyrightSearch/);
  not exposed by any higher layer.
- **ASEAN IT-tools operatorship** — IPOPHL operates the ASEAN regional
  feeds for the other 8 ASEAN states; meaning if we ever wanted ASEAN
  regional coverage at one stroke, the operational party is IPOPHL.

## §3 Programmatic surfaces

### WIPO Publish at IPOPHL — patents / utility models / industrial designs / trademarks

| Field | Value |
|---|---|
| Endpoint | [`https://wipopublish.ipophil.gov.ph/wopublish-search/public/`](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home) (`/patents`, `/trademarks`, `/designs`, `/detail/{module}?id=`) |
| Auth | None (anonymous public read) |
| Format | HTML (Apache Wicket SSR over internal Solr core; no JSON envelope exposed) |
| Rate limit | Not published (IIS reverse proxy; no Incapsula on this host) |
| ToS posture | WIPO global technical-assistance terms govern the **software**; IPOPHL has no published reuse-licence statement for the **data** |
| Rating (zero-infra proxy) | 🔴 **Red** — HTML-only SSR with Wicket pagination; no JSON/XML response; covered transitively by PATENTSCOPE + EUIPO TMview + WIPO Global Brand DB |
| Primary source | [WIPO Publish home (IPOPHL)](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home) · [IPOPHL deployment news (17 Sep 2018)](https://www.ipophil.gov.ph/news/ipophl-deploys-new-patent-search-tool/) |

Solr-style `?query=*:*` and `?query=OFCO:PH` parameters do resolve
through to the underlying Solr — making this technically scrapable —
but the response is server-rendered Wicket HTML and pagination uses
component-coordinate URLs that re-resolve per session. Buckets per
probe 2026-05-18 (US egress): **patents 82,327**, **trademarks
791,043**, **designs 24,141**. Not a viable substrate for a hosted
proxy.

### IPOPHL e-services suite (filings + copyright register + BLA)

| Field | Value |
|---|---|
| Endpoint | [`https://onlineservices.ipophil.gov.ph/`](https://onlineservices.ipophil.gov.ph/) → eTMfile, eInventionFile, eUMFile, eIDFile, eCorr 2.0, eDocFile, CopyrightSearch, blapublication, blanotices, copyrightdomain |
| Auth | IPOPHL applicant account (eCorr 2.0, email-bootstrapped); DragonPay for fee payment |
| Format | Classic ASP / WebForms HTML behind **Incapsula WAF** (returns 403 to non-browser user agents without JS challenge) |
| Rate limit | Not published |
| ToS posture | Designed for filing workflows; no API contract |
| Rating (zero-infra proxy) | 🔴 **Red** — Incapsula WAF on every probed path; filing-side, not search-side |
| Primary source | [IPOPHL eServices entry](https://onlineservices.ipophil.gov.ph/) · [Online Filing](https://www.ipophil.gov.ph/online-filing/) · [eTMfile FAQ](https://www.ipophil.gov.ph/help-and-support/trademark/etmfile-for-trademarks-faqs/) |

Hard skip. Even if the WAF were unblocked, this is the filing layer,
not a documented read interface.

### WIPO IP API Catalog (confirm-by-absence)

| Field | Value |
|---|---|
| Endpoint | [`https://apicatalog.wipo.int/api/apis`](https://apicatalog.wipo.int/api/apis) |
| Probe | `GET /api/apis?size=300` 2026-05-18 → 179 APIs across 10 unique IPOs (DPMA, EPO, EUIPO, IP Australia, JPO, MOIP KOREA, QAZ, UPRP, USPTO, WIPO); **zero entries for IPOPHL / Philippines / PH** |
| Rating | informational |
| Primary source | [WIPO API Catalog](https://apicatalog.wipo.int/) |

The canonical inventory of office APIs does not list IPOPHL. This
confirms by absence that no WIPO-registered IPOPHL API exists today.

### data.gov.ph (Open Data Philippines)

| Field | Value |
|---|---|
| Endpoint | [`https://data.gov.ph/`](https://data.gov.ph/) |
| Auth | n/a (Angular SPA shell only at probe; no SSR; no IPOPHL datasets discovered) |
| Format | n/a |
| Rating (zero-infra proxy) | 🔴 **Red** — no IPOPHL data on the PH national open-data portal |
| Primary source | [Open Data Philippines](https://data.gov.ph/) |

Materially different posture from `data.gov.sg` (which at least
publishes lodgement-date-walk JSON for SG TMs/designs). No PH open-
data equivalent surfaces IPOPHL register data.

### Philippine substantive-law mirror

| Field | Value |
|---|---|
| Endpoint | [`https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html`](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html) (RA 8293 IP Code); [`https://www.ipophil.gov.ph/administrative-issuances/`](https://www.ipophil.gov.ph/administrative-issuances/) (IPOPHL Memorandum Circulars + IRRs) |
| Auth | None |
| Format | HTML / PDF; predictable URLs |
| Rating (zero-infra proxy) | 🟢 **Green** — clean static corpus, same pattern as `ipo_in_statutes` / `dpma_statutes` / `legifrance_ip` / `tw_trade_secrets` |
| Primary source | [LawPhil RA 8293 page](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html) · [IPOPHL administrative issuances](https://www.ipophil.gov.ph/administrative-issuances/) |

Canonical, free, English-authoritative. LawPhil (Arellano Law
Foundation) is non-government but is the most reliable free statute
mirror in PH practice. IPOPHL's own `administrative-issuances` tree
carries the Memorandum Circulars and IRRs. The
[Official Gazette](https://www.officialgazette.gov.ph/) is the
government-authoritative source for Republic Acts but returns 403 to
non-browser user agents — corpus build should use LawPhil + IPOPHL.

## §4 Fees

IPOPHL charges in **Philippine peso (PHP)** across patents (filing,
search, substantive examination, grant, annuities yrs 5-20), utility
models (filing/grant/renewal), industrial designs (filing/renewal),
trademarks (filing/registration/renewal per class), geographical
indications, and copyright voluntary-register fees — plus IPOPHL
Bureau of Legal Affairs filing fees for opposition, cancellation,
and inter partes proceedings. Fee schedules are set by IPOPHL
Memorandum Circulars under the authority delegated by RA 8293.

- **Official schedule:** [IPOPHL Schedule of Fees](https://www.ipophil.gov.ph/services/schedule-of-fees/) — landing page with per-right tables:
  - [Trademark-related fees](https://www.ipophil.gov.ph/services/schedule-of-fees/trademark-related-fees/)
  - [Utility Model & Industrial Design fees](https://www.ipophil.gov.ph/services/schedule-of-fees/utility-model-industrial-design/)
  - [General and Other Fees](https://www.ipophil.gov.ph/services/schedule-of-fees/general-and-other-fees/)
- **Statutory basis:** [Republic Act 8293 (IP Code, 1997)](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html) and IPOPHL Implementing Rules & Regulations published via [Administrative Issuances](https://www.ipophil.gov.ph/administrative-issuances/).
- **Rate adjustment notices:** [IPOPHL Memorandum Circulars (Administrative Issuances)](https://www.ipophil.gov.ph/administrative-issuances/) — MC 2017-002 et seq. set fee structures; MC 2023-002 (per public references) updated portions of the fee schedule.

Notable discount programs *(named only — specific amounts and dates
live on the official schedule)*:

- **Small Entity discount** — RA 8293 § 7.3 authorises IPOPHL to set
  reduced fees for small entities (typically MSMEs); operationalised
  through the fee schedule.
- **ASPEC (ASEAN Patent Examination Co-operation)** — accelerated
  examination programme operated by IPOPHL as Country Lead; fee
  posture per [ASPEC programme overview](https://www.ipophil.gov.ph/asean-patent-cooperation-aspec/).
- **PPH (Patent Prosecution Highway)** — fee posture varies per
  bilateral partner.

## §5 Connector strategy

### What we cover today

PH register-side coverage today is **entirely transitive** via
existing connectors:

- [`patent_client_agents.epo_ops`](../regional/epo.md) — PH patents
  biblio + family + legal events through INPADOC.
- (transitively, via tools that ship today) WIPO PATENTSCOPE search
  — but we do not currently ship a `wipo_patentscope` connector;
  this is queued in [`BACKLOG.md`](../BACKLOG.md).
- (transitively, via tools that ship today) EUIPO TMview /
  Global Brand Database — also not directly wired into our connector
  set; the EUIPO surface is wired through
  [`regional/euipo.md`](../regional/euipo.md) for EUTM specifically
  and would need a TMview-direct wrapper for ASEAN/PH TMs.

### What we should add

**Revival recommendation: ship `ph_statutes` as a static-law corpus.**

- **Module name candidate:** `ph_statutes` (mirroring `ipo_in_statutes`,
  `dpma_statutes`, `legifrance_ip`, `tw_trade_secrets`).
- **Scope:** Republic Act 8293 (Intellectual Property Code, 1997) and
  amendments (RA 9150 Layout-Designs of Integrated Circuits, RA 9502
  Cheaper Medicines Act amendments, RA 10372 copyright amendments),
  plus the running stream of IPOPHL Memorandum Circulars carried at
  [`/administrative-issuances/`](https://www.ipophil.gov.ph/administrative-issuances/).
  Each fetched once from its LawPhil or IPOPHL URL.
- **Why ship rather than skip:** the substantive-law layer is the only
  **green** PH surface, the primary sources are stable (RA 8293 has
  been the IP Code since 1997-06-06), and the static-corpus pattern
  is well-trodden (five sibling corpora already shipped or proposed).
  Closing it means we lose PH agent capability for filings,
  prosecution arguments, BLA disputes, and SG SICC + PH RTC cross-
  border work for no engineering saving.
- **Cross-reference:** queue in [`BACKLOG.md`](../BACKLOG.md) as
  `PH/IPOPHL/Statutes`; coverage/sources.yaml entry per the manifest
  naming convention used by `FR/Legifrance/IP`.

### What we should NOT add

- **Register-side hosted proxy at any layer.** No usable JSON/XML REST
  exists: WIPO Publish at IPOPHL is HTML-only with Wicket pagination
  (same brittleness as AT's see.ip Next.js Server Actions and DPMA
  WebForms); IPOPHL e-services are uniformly Incapsula-WAF-walled;
  the WIPO IP API Catalog has zero IPOPHL entries; `data.gov.ph` has
  no IPOPHL datasets. **PATENTSCOPE + EUIPO TMview + WIPO Global
  Brand Database collectively cover the read side**; we should wire
  to those upstream surfaces, not build a hosted PH scrape.
- **Copyright register or BLA-decisions scrape.** WAF-walled,
  brittle, and the data is operationally narrow. Defer until a
  paying customer asks.
- **IPOPHL filing-side (eTMfile, eInventionFile, eUMFile, eIDFile).**
  Filing-side scope; not contemplated for unaffiliated SaaS
  redistribution; foreign-filer accessible but identity-bound to an
  IPOPHL eCorr 2.0 account.
- **ASEAN Register direct scrape at `ip-register.aseanip.org`.**
  Same WIPO Publish stack; IPOPHL operates it; same HTML-only
  posture; same proxy posture.
- **`data.gov.ph` wrapper.** No IPOPHL datasets discovered; no
  utility today.

### Next steps

1. **Cut a `ph_statutes` static-corpus PR** using `tw_trade_secrets`
   as the smallest sibling exemplar, then walk `dpma_statutes` for
   the multi-act case. Primary URLs: LawPhil for RA 8293, IPOPHL's
   administrative-issuances tree for Memorandum Circulars.
2. **Defer PATENTSCOPE connector decision** to the PATENTSCOPE
   research thread — this is where PH patents and UMs become
   queryable in our stack.
3. **Defer EUIPO TMview / ASEAN TMview wrapper** to the TMview
   research thread; PH TMs become queryable via that wrapper.
4. **Monitor IPOPHL news for a developer programme.** None has been
   announced; PH is not on the WIPO API Catalog trajectory; watch
   [`www.ipophil.gov.ph/news/`](https://www.ipophil.gov.ph/news/).

## §6 Open questions

- **PH plant-variety register at DA-NSIC** — administered by Bureau
  of Plant Industry, not IPOPHL. Out of IPOPHL scope, but a PVP
  agent might want it. Action: defer to a separate PH-PVP wave.
- **ASEAN TMview / EUIPO TMDN coverage freshness for PH** — primary-
  source-confirmed cadence beyond the qualitative "PH is up-to-date"
  claim from EU IP cooperation pages. Action: probe TMDN coverage
  metadata directly.
- **PATENTSCOPE PH backfile completeness** — coverage table says
  30.12.1899 → 17.11.2025; spot-check whether early-20th-century PH
  patents are actually present or whether the date range is a
  metadata default. Action: sample query against PATENTSCOPE.
- **WIPO Publish JSON export at IPOPHL** — some WIPO Publish
  deployments expose `?download=CSV` or similar; not observed on
  IPOPHL's instance. Action: full request-path enumeration with a
  cookied browser session before any future scrape decision.
- **PH Hague accession trajectory** — IPOPHL has stated interest in
  joining Hague (per news statements); accession would activate the
  WIPO Hague substitution layer for PH designs. Action: monitor
  IPOPHL news.
- **IPOPHL administrative-issuances feed freshness** — is there an
  RSS/Atom feed on the `/administrative-issuances/` tree, or only
  the WordPress page list? Action: probe `?feed=rss2` and
  `/wp-json/wp/v2/` per WordPress conventions before corpus build.

## §7 References

Primary sources only — IPOPHL, WIPO, EUIPO/TMDN, LawPhil, Official
Gazette.

**IPOPHL portals + service docs:**
- [Home — IPOPHL](https://www.ipophil.gov.ph/)
- [Services index](https://www.ipophil.gov.ph/services/)
- [Patent](https://www.ipophil.gov.ph/patent/) · [Utility Model](https://www.ipophil.gov.ph/services/utility-model/) · [Industrial Design](https://www.ipophil.gov.ph/services/industrial-design/) · [Trademark](https://www.ipophil.gov.ph/trademark/)
- [Trademark Online Tools](https://www.ipophil.gov.ph/trademark/trademark-online-tools/)
- [Online Filing](https://www.ipophil.gov.ph/online-filing/)
- [IPOPHL eServices](https://onlineservices.ipophil.gov.ph/) (Incapsula-walled)
- [Patent Search and Analytics](https://www.ipophil.gov.ph/services/patent-search-analytics/)
- [Administrative Issuances](https://www.ipophil.gov.ph/administrative-issuances/)
- [Schedule of Fees](https://www.ipophil.gov.ph/services/schedule-of-fees/)
- [News](https://www.ipophil.gov.ph/news/)
- [Privacy Policy](https://www.ipophil.gov.ph/privacy-policy/)
- [IPOPHL deploys new patent search tool (17 Sep 2018)](https://www.ipophil.gov.ph/news/ipophl-deploys-new-patent-search-tool/)
- [IPOPHL takes over management of ASEAN IT tools](https://www.ipophil.gov.ph/news/the-ipophl-takes-over-management-of-asean-it-tools-on-intellectual-property/)
- [ASEAN Patent Cooperation (ASPEC)](https://www.ipophil.gov.ph/asean-patent-cooperation-aspec/)

**WIPO Publish (IPOPHL national):**
- [WIPO Publish home](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home)
- [Patents](https://wipopublish.ipophil.gov.ph/wopublish-search/public/patents) · [Trademarks](https://wipopublish.ipophil.gov.ph/wopublish-search/public/trademarks) · [Designs](https://wipopublish.ipophil.gov.ph/wopublish-search/public/designs)
- [About page](https://wipopublish.ipophil.gov.ph/wopublish-search/public/about)

**ASEAN regional surfaces (IPOPHL is Country Lead):**
- [ASEAN IP Portal](https://www.aseanip.org/)
- [ASEAN IP Register](https://ip-register.aseanip.org/wopublish-search/public/home) (WIPO Publish)

**WIPO transitive coverage:**
- [PATENTSCOPE](https://patentscope.wipo.int/search/en/search.jsf) · [Data coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)
- [Global Brand Database — PH](https://branddb.wipo.int/branddb/ph/en/) · [Coverage page](https://branddb.wipo.int/en/coverage)
- [Madrid Monitor](https://www.wipo.int/madrid/monitor/) · [Hague Express](https://www.wipo.int/designdb/hague/)
- [WIPO IP API Catalog](https://apicatalog.wipo.int/) — confirm-by-absence
- [WIPO INSPIRE Philippines jurisdiction note](https://inspire.wipo.int/system/files/juri/ph.pdf)

**EUIPO transitive coverage:**
- [TMview](https://www.tmdn.org/tmview/) · [Philippines joins TMview (TMDN news)](https://www.tmdn.org/network/-/philippines-joins-tmview) · [DesignView](https://www.tmdn.org/network/web/csc/offices-summary)

**Substantive law:**
- [LawPhil RA 8293 (IP Code)](https://lawphil.net/statutes/repacts/ra1997/ra_8293_1997.html)
- [Official Gazette RA 8293](https://www.officialgazette.gov.ph/1997/06/06/republic-act-no-8293/) (government-authoritative; 403 to bot egress)
- [IPOPHL WipoLex profile](https://www.wipo.int/wipolex/en/text/480286)

**Wave file:**
- [`waves/2026-05-18-secondary-nationals-wave/ph-ipophl.md`](../waves/2026-05-18-secondary-nationals-wave/ph-ipophl.md) — 2026-05-18 grounded research with full endpoint probes, ToS analysis, and bucket counts

---

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-18 | Initial synopsis. Register-side **🔴 red** — no usable JSON/XML REST: WIPO Publish at [`wipopublish.ipophil.gov.ph`](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home) is Apache Wicket SSR HTML over an internal Solr core (Solr-style `?query=OFCO:PH` works but pagination is Wicket-coordinate, no JSON envelope); [`onlineservices.ipophil.gov.ph`](https://onlineservices.ipophil.gov.ph/) is uniformly Incapsula-WAF-walled (403 to bots); [WIPO IP API Catalog](https://apicatalog.wipo.int/) has **zero** IPOPHL entries (179 APIs across 10 unique IPOs); `data.gov.ph` has no IPOPHL datasets. PH register is materially covered transitively — PATENTSCOPE PH national collection refreshes twice/month with ~3-month lag (per [data-coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) row 60: 30.12.1899 → 17.11.2025, last loaded 22.01.2026); EUIPO TMview ingests the PH TM register and IPOPHL itself is the regional Country Lead operating ASEAN TMview on EUIPO's TMDN infrastructure; WIPO Global Brand Database mirrors the PH TM stream since 2013. **Surprise:** IPOPHL is the regional operator of the ASEAN IT tools for the other ASEAN states. Statutes-side **🟢 green** — RA 8293 + IPOPHL Memorandum Circulars are static-corpus material; recommend `ph_statutes` PR under current `StaticLawCorpus` standards. | [waves/2026-05-18-secondary-nationals-wave/ph-ipophl.md](../waves/2026-05-18-secondary-nationals-wave/ph-ipophl.md) · [WIPO Publish IPOPHL](https://wipopublish.ipophil.gov.ph/wopublish-search/public/home) · [PATENTSCOPE data coverage](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) · [WIPO IP API Catalog](https://apicatalog.wipo.int/) |
