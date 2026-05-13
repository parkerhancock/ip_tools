# ARIPO Connector Survey

One-page survey of the African Regional Intellectual Property Organization (ARIPO)
for `patent-client-agents`. Scope: the four ARIPO protocols (patents/designs/utility
models, trademarks, plant varieties, traditional knowledge), the eService portal,
the Regional IP Database, the ARIPO JOURNAL, and how ARIPO surfaces through WIPO
Lex, Patentscope, and EPO OPS INPADOC. **Triage verdict up front: thin.** ARIPO's
digital surface is small, anti-automation in the one place it matters (the Regional
IP Database), and most data already passes through Patentscope + WIPO Lex + EPO OPS
INPADOC, all of which we already wrap or have planned. This is a 1-2 day "recipes
on existing connectors + static law" play, not a new module sprint.

## Cross-asset comparison

| # | Asset | Endpoint | Auth | Format | Bulk? | License |
|---|-------|----------|------|--------|-------|---------|
| 1 | ARIPO eService — IP Digital Library (search) | `eservice.aripo.org/pdl/` | None (cookies; JSESSIONID) | HTML (server-rendered Struts on Tomcat 7.0.47) | No | Site ToS |
| 2 | ARIPO eService — ARIPO JOURNAL | `eservice.aripo.org/ppb/pjd/PPBJournalViewList.do` | None | HTML index + per-issue PDF | PDFs only | Site ToS |
| 3 | ARIPO Regional IP Database (WIPO Publish) | `regionalip.aripo.org/` | None | HTML | No | `robots.txt: Disallow: /` — anti-automation |
| 4 | ARIPO eService — eFiling / payments | `eservice.aripo.org/pes/...` | Account | HTML | n/a | Account holders only |
| 5 | ARIPO website static (protocols, news, member states) | `www.aripo.org/` | None | HTML + PDF | n/a | Site ToS; free reuse with attribution typical |
| 6 | WIPO Lex — ARIPO profile (protocols + national laws) | `wipo.int/wipolex/.../profile/ARIPO` | None | HTML + PDF | Yes (Lex bulk planned in T1) | Free reuse |
| 7 | WIPO Patentscope — ARIPO (AP) collection | `patentscope.wipo.int/` | None for UI | HTML/JSON XHR (no docs) | Patentscope SFTP (CHF 400/yr; PCT only — not AP) | Free for UI use |
| 8 | EPO OPS — ARIPO (AP) biblio + INPADOC legal events | `ops.epo.org/3.2/...` | OAuth 2.0 | JSON/XML | Within OPS plan | EPO OPS ToU |

---

## 1. ARIPO eService — IP Digital Library (Patent / Design / UM register search)

- **Endpoint:** `https://eservice.aripo.org/pdl/pqs/quickSearchScreen.do` (quick) and `/pdl/pah/advancedSearchScreen.do` (advanced). UI for the patent register; the platform is the IPDL component WIPO/KIPO co-funded for ARIPO in the mid-2010s.
- **Auth:** None for search; a JSESSIONID cookie is set on first GET. No CAPTCHA was observed on the search forms when probed.
- **Stack:** Apache Tomcat 7.0.47 (released 2013; EOL since 2021) running a Struts-style app — `.do` action URLs, server-rendered HTML, no JSON API surface. The PDF download links carry an HMAC-style `key=` parameter scoped to the session.
- **Coverage:** ARIPO (AP) patents + industrial designs + utility models under the Harare Protocol. Per WIPO INSPIRE: searchable by PCT application/publication number, applicant/inventor name, and priority data; legal-status surfaced (e.g., "Withdrawal" for `AP/P/2000/001992`). Member-state national IP rights tab exists but INSPIRE notes it "is currently loading and a search gives no results."
- **Rate limits / bulk:** No documented limits, no bulk export. No published API.
- **ToS:** Site ToS only; no documented data-reuse policy. `robots.txt` returns 404 (path-level not configured).
- **PyPI:** None.
- **Verdict:** Scrapeable but fragile — Tomcat 7 + Struts + session-keyed download links are a classic brittle-form-app target. Better surfaced via EPO OPS INPADOC + Patentscope (items 7-8) for biblio, with ARIPO direct used only for the legal-status field that INPADOC sometimes lags on.

## 2. ARIPO JOURNAL (monthly gazette)

- **Endpoint:** `https://eservice.aripo.org/ppb/pjd/PPBJournalViewList.do` (index) → per-issue `PPBJournalPdfDownload.do?key=<hmac>&journalSeq=<n>`.
- **Auth:** None.
- **Format:** Monthly PDF, English. Each issue exposes multiple PDF section downloads (different `key=` per section, same `journalSeq=`). Per WIPO INSPIRE, current coverage is **2015 to present**.
- **Bulk:** No archive ZIP; iterate `journalSeq` (observed value `1548` in May 2026 — roughly consistent with ~130 issues since 2015 if numbering is sequential).
- **Plus:** A `PPBPublicationServerList.do` page lets you filter by legal status (filed / pending grant / granted / abandoned / assigned). And `PPBMemberStateJournalViewList.do` exposes **member-state journals** — INSPIRE notes coverage is currently partial (Kenya, Mozambique, Rwanda, São Tomé and Príncipe, Tanzania only).
- **ToS:** Site ToS.
- **Verdict:** The single highest-value asset on the ARIPO domain. ~130 monthly PDFs (~10-50 MB each estimate) totalling sub-10 GB lifetime is a one-shot mirror + parse problem. Section-split PDFs help — patent grants, design registrations, TM publications, etc. each get separate PDFs. This is the only place to get the **canonical ARIPO publication record**.

## 3. ARIPO Regional IP Database (`regionalip.aripo.org`)

- **Endpoint:** `http://regionalip.aripo.org/`. Launched 2018; WIPO Publish platform; data extracted from IPAS instances in member states.
- **Coverage (per ARIPO/WIPO):** patents, industrial designs, utility models, copyright, plant varieties, **trademarks**, across ARIPO + ~12-13 contributing member states (ARIPO, Botswana, Gambia, Ghana, Kenya, Malawi, Mozambique, Namibia, Rwanda, Tanzania, Uganda, Zambia, Zimbabwe).
- **Auth:** None for UI.
- **`robots.txt`:** **`User-agent: * / Disallow: / / Crawl-delay: 600`**. This is an unambiguous "do not crawl" signal — ARIPO explicitly disallows automated access.
- **Bulk:** None.
- **ToS:** Implied by robots.txt disallow.
- **PyPI:** None.
- **Verdict:** **Hard skip for v1.** Even though this is the only ARIPO-side surface for trademarks (Banjul Protocol) and the only consolidated cross-member-state view, the `robots.txt` makes a CoWork-cached fetch model legally/ethically untenable without an explicit ARIPO data-sharing agreement. Use Patentscope (item 7) and the eService PDF journals (item 2) for the patent/design/UM data instead.

## 4. eFiling / payments

Out of scope — write-path, account-gated. Confirmed live (`/pes/pog/gog/PESNewOnlineFilingScreen.do`) but no research-tool need.

## 5. ARIPO website static content

- **Endpoint:** `https://www.aripo.org/`. Pages of interest: `/member-states`, `/resources/protocols`, `/ip-services/{patents,trademarks,industrial-designs,plant-variety-protection,traditional-knowledge}`, `/publications/{annual-reports,copyright-publications}`, `/notices`.
- **Format:** Plain HTML + WP-style PDF uploads under `/wp-content/uploads/`.
- **Auth:** None.
- **ToS:** Site ToS.
- **Verdict:** Trivially scrapeable. Real value is the **protocols PDFs** (Harare, Banjul, Arusha, Swakopmund, Lusaka) and member-state status pages — both of which are also in WIPO Lex (item 6). Don't build a separate scraper.

## 6. WIPO Lex — ARIPO profile

- **Endpoint:** `https://www.wipo.int/wipolex/en/treaties/members/profile/ARIPO`; individual treaty pages e.g. `/treaties/details/204` (Harare), `/treaties/details/203` (Banjul), `/treaties/details/971` (Arusha), plus a Swakopmund entry.
- **Coverage:** All ARIPO protocols + implementing regulations + member-state IP statutes (cross-link from each member-state profile). Harare and Banjul Protocols were both amended 25 November 2022 ("10th Amendments") — current text is the as-amended version. Mauritius deposited its Harare Protocol accession 27 May 2025 (effective 27 August 2025).
- **Auth/format/bulk:** As planned in the Tier 1 `wipo_lex` module — free polite scrape, HTML + PDF, ~50k docs covering ~200 jurisdictions including ARIPO.
- **Verdict:** **This is the right home for all ARIPO substantive law.** Building `wipo_lex` (already #4 on the combined leaderboard) covers ARIPO protocols + the 22 member-state statutes for free — no per-office statute fetcher needed.

## 7. WIPO Patentscope — ARIPO (AP) collection

- **Endpoint:** `https://patentscope.wipo.int/` UI; AP is one of ~60 collections. Search by AP application number, INID fields, etc.
- **Auth:** None for UI; account (free) needed to download up to 10,000 records (Excel).
- **Bulk:** PCT SFTP (CHF 400/yr, already on the Tier 1 roadmap as `wipo_patentscope_bulk`) covers **PCT only** — the AP regional collection is **not** included in the SFTP feed.
- **API:** No public REST. SOAP "WIPO PATENTSCOPE Web Service" exists at CHF ~2,600/yr but is already on the Tier 1 skip list (poor stack fit; SOAP).
- **Verdict:** Use Patentscope's UI / search XHR for AP biblio + full text if/when needed; budget-priced bulk path does not include AP.

## 8. EPO OPS — ARIPO (AP) coverage

- **Endpoint:** Existing `epo_ops` module. INPADOC backend covers AP biblio and legal-status events.
- **Format:** JSON / XML via OPS.
- **Auth:** Existing OAuth 2.0 setup.
- **Coverage:** AP biblio (DOCDB) + AP legal events (INPADOC legal status file, ~100 jurisdictions, 470M events as of Oct 2024). Full text for AP is **not** in OPS — for that, fall back to ARIPO JOURNAL PDFs (item 2) or Patentscope (item 7).
- **Verdict:** **Already-built backbone.** ARIPO patent/design/UM biblio and legal events are reachable today via `epo_ops` with zero new code; only need a small `get_ap_biblio(ap_number)` / `get_ap_legal_events(ap_number)` recipe pair, mirroring the planned `cn_via_epo_ops` helpers.

---

## Protocols summary (substantive law context, all sourced via `wipo_lex`)

- **Lusaka Agreement (1976)** — establishes ARIPO itself; signed 9 Dec 1976.
- **Harare Protocol (1982, in force 1984)** — patents, utility models, industrial designs. Amended through Nov 2022 (10th amendments). In force in 22 - 2 = **20** members (Mauritius and Somalia not yet party per WIPO INSPIRE; Mauritius accession effective 27 Aug 2025 brings it to 21 — confirm post-effective-date).
- **Banjul Protocol (1993)** — trademarks. Amended through Nov 2022. 13 contracting states (Cape Verde was 13th, effective 14 Oct 2022).
- **Arusha Protocol (2015, in force 24 Nov 2024)** — plant varieties (UPOV-style PBR). Currently 4 contracting states: Cabo Verde, Ghana, Rwanda, São Tomé and Príncipe.
- **Swakopmund Protocol (2010)** — traditional knowledge and expressions of folklore. In force.

## Member states (22, confirmed May 2026)

Botswana, Cabo Verde, Eswatini, The Gambia, Ghana, Kenya, Lesotho, Liberia, Malawi,
Mauritius, Mozambique, Namibia, Rwanda, São Tomé and Príncipe, **Seychelles**
(member since 1 Jan 2022 — was missing from the prompt's list), Sierra Leone,
Somalia, Sudan, Tanzania, Uganda, Zambia, Zimbabwe.

**The prompt's list contained "South Africa" — that is incorrect; South Africa is
an observer, not a member.** Correct count is 22 if South Africa is replaced with
Seychelles.

---

## Recommended v1 scope

**Not a standalone module.** Treat ARIPO as a thin overlay on existing/planned
infrastructure:

1. **`epo_ops` recipes for AP** — `get_ap_biblio`, `get_ap_legal_events`, `get_ap_family`. Same shape as the planned `cn_via_epo_ops` helpers. ~0.5 days.
2. **`wipo_lex` ARIPO subset** — when the Tier 1 `wipo_lex` module ships, ARIPO protocols (Lusaka / Harare / Banjul / Arusha / Swakopmund) and member-state national IP statutes come for free. No extra code; just verify the ARIPO profile parses cleanly. ~0 days marginal.
3. **`aripo_journal` static mirror (optional)** — one-shot fetch + monthly cron over `PPBJournalViewList.do` → `PPBJournalPdfDownload.do`. Section-PDFs already split by IP-right type. Pair with a thin PDF text extractor to expose journal contents as a searchable corpus. ~1-2 days. Build only if a customer asks for canonical ARIPO publication records (versus INPADOC biblio).

Total marginal effort if all three: ~2-3 days. Compare to the 1-2 weeks for a
proper office connector (cf. `ip_australia`, `kipo_kipris_patents`).

## Skip list

- **`regionalip.aripo.org` (Regional IP Database)** — `robots.txt: Disallow: /`. Without an ARIPO data-sharing agreement, automated access is off-limits. Revisit only if ARIPO publishes an API or relaxes robots.
- **ARIPO eService Tomcat scrape (`/pdl/...`)** — fragile Tomcat 7 / Struts stack with session-keyed download URLs. Same biblio is in EPO OPS INPADOC; legal-status delta is not worth the maintenance burden.
- **ARIPO trademarks (Banjul)** — no clean digital path. Regional IP DB is the only consolidated view and is robots-disallowed. Member-state national TM registers are mostly not API-accessible either (Tier 3 problem for individual offices).
- **ARIPO plant varieties (Arusha)** — Protocol just entered force Nov 2024; only 4 contracting states; trivially small initial corpus. Wait for digital surface to emerge.
- **ARIPO traditional knowledge (Swakopmund)** — by design, this is not a public-register regime in the same way patents/TMs are; access controls reflect that. Not a database problem.
- **Patentscope SOAP for AP** — Tier 1 skip already.
- **Member-state national IP offices direct** — Tier 3 (and most have far worse digital infra than ARIPO itself; defer until specific customer demand surfaces).

## Open questions

1. **Mauritius Harare status post-27 Aug 2025** — INSPIRE PDF still flags Mauritius as not-a-Harare-member; confirm WIPO Lex and ARIPO website reflect the effective accession.
2. **AP collection in EPO OPS — full-text coverage?** OPS gives biblio and INPADOC events; spot-check whether AP full text (description/claims) is retrievable, or whether you must fall back to ARIPO JOURNAL PDFs.
3. **ARIPO JOURNAL section taxonomy** — multiple `key=` PDFs per `journalSeq`; need to map section codes to IP-right types (patent grants vs. designs vs. UM vs. TM events) before parsing.
4. **Regional IP Database robots policy** — is it crawler-blanket or intended to block search-engine indexing only? Worth an email to `mail@aripo.org` before final skip.
5. **Banjul (TM) digital path** — if a customer needs ARIPO TM data, the only options are Regional IP DB (robots-disallowed) or filing-agent commercial aggregators (Adams & Adams, Spoor & Fisher, Inventa, Bowmans publish updates but don't expose data). Confirm there's no API behind the eService TM module before declaring TM unreachable.
6. **JOURNAL coverage gap 2015-pre** — INSPIRE says 2015 to present; pre-2015 ARIPO publications must be reconstructed from EPO OPS INPADOC. Quantify what's missed.

## Compare with EUIPO and WIPO Lex

- **EUIPO (regional org pattern):** EUIPO publishes a proper OAuth 2.0 + OpenAPI 3 developer portal (`dev.euipo.europa.eu`), free Open Data XML bulk, an in-house Boards of Appeal case-law search, and serves as the canonical register for ~3.7M EUTMs + ~1.7M RCDs. ARIPO is two decades and several engineering generations behind — Tomcat 7 + Struts forms versus EUIPO's OAuth/JSON, robots-disallowed regional DB versus EUIPO's daily XML dumps, ~130 PDF gazettes since 2015 versus EUIPO's structured event streams. Treating ARIPO as "EUIPO for Africa" is the wrong mental model; it's closer to **a 1990s-era patent office that happens to be regional**.
- **WIPO Lex (substantive law backbone):** All ARIPO protocols + the 22 member-state IP statutes are mirrored in WIPO Lex with English translations and amendment histories. Once the Tier 1 `wipo_lex` module ships, **ARIPO substantive-law coverage is a side-effect** — no per-office statute fetcher needed. This is the same leverage WIPO Lex provides for the rest of Tier 3.

---

## Sources

- [ARIPO Member States](https://www.aripo.org/member-states)
- [ARIPO Protocols overview](https://www.aripo.org/resources/protocols)
- [WIPO Lex — ARIPO member profile](https://www.wipo.int/wipolex/en/treaties/members/profile/ARIPO)
- [WIPO Lex — Harare Protocol (treaty 204)](https://www.wipo.int/wipolex/en/treaties/details/204)
- [WIPO Lex — Banjul Protocol (treaty 203)](https://www.wipo.int/wipolex/en/treaties/details/203)
- [WIPO Lex — Arusha Protocol (treaty 971)](https://www.wipo.int/wipolex/en/treaties/details/971)
- [WIPO INSPIRE — ARIPO database report](https://inspire.wipo.int/system/files/juri/ARIPO.pdf)
- [ARIPO eService — Quick Search](https://eservice.aripo.org/pdl/pqs/quickSearchScreen.do)
- [ARIPO eService — Advanced Search](https://eservice.aripo.org/pdl/pah/advancedSearchScreen.do)
- [ARIPO eService — JOURNAL list](https://eservice.aripo.org/ppb/pjd/PPBJournalViewList.do)
- [ARIPO eService — Publication Server (legal-status filter)](https://eservice.aripo.org/ppb/ppr/PPBPublicationServerList.do)
- [ARIPO eService — Member-State Journals](https://eservice.aripo.org/ppb/pjd/PPBMemberStateJournalViewList.do)
- [ARIPO Regional IP Database (robots.txt: Disallow: /)](http://regionalip.aripo.org/)
- [ARIPO Online Tools and Services (WIPO presentation)](https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_dar_19/wipo_ip_dar_19_t_4.pdf)
- [Arusha Protocol entry into force (24 Nov 2024)](https://www.aripo.org/news/The+Arusha+Protocol+for+the+Protection+of+New+Varieties+of+Plants+Officially+Comes+into+Force-1732618853)
- [Harare/Banjul 10th Amendments commentary (Inventa)](https://inventa.com/ip-news-insights/opinion/aripos-harare-protocol-10th-amendments-changes-and-implications)
- [Mauritius Harare Protocol accession (Aug 2025)](https://www.aripo.org/)
- [Patentscope — National Collections coverage](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)
- [EU IP Helpdesk — ARIPO Country Fiche](https://intellectual-property-helpdesk.ec.europa.eu/system/files/2022-12/Africa_IP-Country-Fiche_ARIPO.pdf)
- [CarIPI — An Overview of ARIPO (2024)](https://internationalipcooperation.eu/sites/default/files/caripi-docs/2024/CarIPI_An_Overview_of_ARIPO.pdf)
