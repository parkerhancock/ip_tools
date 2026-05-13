# UKIPO Connector Survey

One-page survey of UKIPO and adjacent UK IP data sources for `patent-client-agents`. Scope: patents (Ipsum / One IPO Search), trade marks, registered designs, examination manuals, hearings, courts, statutory law, post-Brexit divergence, and UK plant variety rights. UK is an EPO member state (EPC ≠ EU), so prosecution-level patent data is *also* reachable via the existing `epo_ops` module; this survey focuses on UK-domestic register and tribunal data.

## Cross-asset comparison

| # | Asset | Endpoint | Auth | Format | Bulk? | License |
|---|-------|----------|------|--------|-------|---------|
| 1 | Ipsum / One IPO Search (patents) | `gov.uk/search-for-patent` (live); `ipo.gov.uk/p-ipsum.htm` (legacy, retiring Jan 2025) | None on UI; **no public API yet** (roadmap H2-2025/26) | HTML + PDF documents; future JSON | No (UI only) | OGL v3.0 |
| 2 | Find a trade mark | `trademarks.ipo.gov.uk/ipo-tmtext` | None | HTML | No public API | OGL v3.0 |
| 3 | Find a registered design | `registered-design.service.gov.uk/find/` | None | HTML + image binaries | No | OGL v3.0 |
| 4 | UKIPO Trade Mark dataset (FOI bulk + Trade Marks Journal) | `gov.uk/government/publications/ipo-trade-mark-dataset`; `data.gov.uk/dataset/.../ipo-tmj` | None (request bulk via IPO email) | XML (TMJ weekly), CSV/XML (FOI dumps) | Partial | OGL v3.0 |
| 5 | UKIPO Patent dataset | `gov.uk/government/publications/ipo-patent-data` | None | CSV/Excel snapshots | Periodic | OGL v3.0 |
| 6 | Manual of Patent Practice (MoPP) | `gov.uk/guidance/manual-of-patent-practice-mopp` | None | HTML (sectioned), PDF mirror | Yes (full PDF) | OGL v3.0 |
| 7 | Manual of Trade Marks Practice | `gov.uk/guidance/trade-marks-manual` | None | HTML | Yes | OGL v3.0 |
| 8 | Designs Examination Guide | No standalone manual; uses Designs Practice Notice + RDA 1949 | None | HTML/PDF | n/a | OGL v3.0 |
| 9 | UKIPO Hearings (patent + TM + design decisions) | `ipo.gov.uk/p-challenge-decision-results.htm`, `ipo.gov.uk/t-challenge-decision-results.htm` | None | HTML index → PDF decisions | No bulk; scrape | OGL v3.0 |
| 10 | Find Case Law (Patents Court, IPEC, Court of Appeal, UKSC) | `caselaw.nationalarchives.gov.uk` + `api.caselaw.nationalarchives.gov.uk` | None for public API; **license required for bulk** | LegalDocML XML + HTML + Atom feed | Yes via license | OGL v3.0 (public); separate computational-use licence for bulk |
| 11 | BAILII (Patents Court / IPEC / CoA / UKSC) | `bailii.org/ew/cases/EWHC/Patents/`, `.../IPEC/` | None | HTML (raw judgments) | No official bulk | OGL v3.0 (Crown copyright) but BAILII ToS restricts automated scraping |
| 12 | legislation.gov.uk — Patents Act 1977, TMA 1994, RDA 1949, CDPA 1988, Trade Secrets Regs 2018, secondary rules | `legislation.gov.uk/.../data.xml` or `/data.akn` | None | CLML XML, Akoma Ntoso XML, HTML, PDF, RDF | Yes | OGL v3.0 |
| 13 | UK Plant Breeders' Rights (APHA) | `gov.uk/guidance/plant-breeders-rights`; UPOV PLUTO/PRISMA bridge | None on gov.uk; UPOV side requires registration | HTML (no JSON API) | UPOV PLUTO bulk | OGL v3.0 (UK side) |

---

## 1. Ipsum / One IPO Search (UK patent file inspection)

Legacy Ipsum (`ipo.gov.uk/p-ipsum.htm`) is being decommissioned; the live service is **One IPO Search** at `https://www.gov.uk/search-for-patent` (also reachable at `search-for-intellectual-property.service.gov.uk/`), launched Jan 2025. UI only, no auth. **No public REST API yet** — the One IPO Patents Service overview confirms three APIs are in development ("View rights portfolio", "Renewals", "IP register") rolling out H2-2025 / 2026, but no OpenAPI spec or developer portal sign-up is live. Output: HTML for register data + PDFs for file-history documents (application, claims, search opinions, correspondence). Coverage: all UK patents and applications + SPCs. No bulk. OGL v3.0. No maintained Python client.

## 2. UK Trade Marks register

Search UIs at `trademarks.ipo.gov.uk/ipo-tmtext` (word) and `/ipo-tmcase` (case file). **No public API.** A 2016 FOI response stated the IPO "does not at present provide an API for bulk data retrieval of the trade mark database"; the One IPO programme has not yet superseded that. HTML only on the UI; structured TM data ships via the weekly Trade Marks Journal (asset 4). Coverage: full UK register + ~1.4M "comparable UK" marks created 1 Jan 2021 from EUTMs, plus IRs designating UK. No PyPI client.

## 3. UK Registered Designs

`registered-design.service.gov.uk/find/` ("Find a registered design"). **No public API.** UI search is constrained to design number or owner name; richer search (Locarno class, product indication) is pushed to EUIPO DesignView, which also has no documented API. HTML + image binaries. Coverage includes ~700k comparable UK designs created from RCDs on 1 Jan 2021. No bulk, no PyPI client.

## 4. UKIPO Trade Marks Journal + bulk TM dataset

Weekly journal at `ipo.gov.uk/t-tmj.htm`; data.gov.uk record at `data.gov.uk/dataset/fc8a832f-b5e2-4c03-9ae4-10a5e74b467c/ipo-tmj`; bulk-dump request procedure at `gov.uk/government/publications/trade-mark-database-access` and `.../ipo-trade-mark-dataset`. Journal published each Friday in PDF *and* XML — covers weekly acceptances pending registration. The widely-circulated 2016 FOI dump shipped CSV/XML for the full register up to Feb 2015; more current full-register dumps are on-request via the IPO. OGL v3.0. No PyPI client.

## 5. UKIPO Patent Dataset (statistical snapshots)

`gov.uk/government/publications/ipo-patent-data` and the annual *Facts and Figures*. CSV/Excel snapshots of applications/grants/SPCs — aggregate statistical view, not a structured register feed. Current as of June 2025 release. OGL v3.0.

## 6. Manual of Patent Practice (MoPP)

`gov.uk/guidance/manual-of-patent-practice-mopp` — per-section HTML keyed to PA 1977 section number; consolidated PDF mirror at `ipo.gov.uk/downloads/practice-manual.pdf`. Covers PA 1977 + relevant CDPA 1988 provisions + SPC chapter. Updated quarterly (last update 2 Jan 2026 — sections 14, 20, SPC). OGL v3.0. **Fit:** mirrors `mpep`/`tmep` almost verbatim.

## 7. Manual of Trade Marks Practice

`gov.uk/guidance/trade-marks-manual` + `/the-examination-guide` + Tribunal section. HTML, organised Parts A–D (Introduction, alphabetical examination practice, notifications, overcoming objections). OGL v3.0. **Fit:** direct sibling of `tmep`.

## 8. Designs Examination Guide

UKIPO does **not** publish a single Designs Manual analogous to MoPP or the TM Manual. Designs examination is governed by the RDA 1949, the Registered Designs Rules 2006, and *ad hoc* practice notices under `gov.uk/government/collections/intellectual-property-designs`. The FOI-released internal "Designs Practice Manual" sits at `assets.publishing.service.gov.uk/media/.../foi-2016-480.pdf`. Treat as a small static corpus alongside the statutory layer — not worth its own module.

## 9. UKIPO Hearings — patent, TM, and design decisions

Decision indices at `ipo.gov.uk/p-challenge-decision-results.htm` (patents) and `/t-challenge-decision-results.htm` (TMs); design decisions follow the same pattern. HTML index pages filterable by hearing type + year, linking to per-decision PDFs. UK is not federal, so UKIPO tribunal decisions are the inter partes equivalent of PTAB/TTAB. Decisions are first published via the British Library and republished here, then by reporters (RPC, FSR). No bulk feed; scrape index + GET PDFs. OGL v3.0. No PyPI client.

## 10. Find Case Law — Patents Court, IPEC, CoA, UKSC

Web: `caselaw.nationalarchives.gov.uk/`. Public API: `api.caselaw.nationalarchives.gov.uk/` with Swagger docs. Atom feed at `caselaw.nationalarchives.gov.uk/atom.xml`. No auth for the public API; **transactional bulk / computational-use licence** required for systematic re-use beyond OGL terms — both R&D (1-year) and business (5-year) licences are issued by `caselawlicence@nationalarchives.gov.uk`. Judgments delivered as **LegalDocML XML** at `/{uri}/data.xml` plus HTML. Parser open-sourced at `github.com/nationalarchives/tna-judgments-parser`. Coverage: Patents Court (`EWHC/Patents`), IPEC (`EWHC/IPEC`, from 1 Oct 2013), CoA Civil, UKSC. Bulk export uses a MarkLogic export script for licensees. National Archives ships `ds-find-caselaw-docs` and `ds-caselaw-privileged-api` repos but no PyPI client.

## 11. BAILII — alternative free case-law source

`bailii.org/databases.html`; IP courts at `/ew/cases/EWHC/Patents/` and `/ew/cases/EWHC/IPEC/`. HTML only (raw judgments, no headnotes), no API, no bulk. BAILII's ToS is explicit that it serves humans, not pipelines. Judgments themselves are Crown Copyright (OGL) but BAILII's added value is restricted. Use Find Case Law as the canonical structured source; BAILII is a fallback for older judgments.

## 12. legislation.gov.uk — statutory law

`legislation.gov.uk/{ukpga|uksi|...}/{year}/{number}/data.xml` (CLML), `/data.akn` (Akoma Ntoso), `/data.feed` (Atom), `/data.rdf` (RDF). CLML schema at `legislation.gov.uk/schema/legislation.xsd`; XSLTs for CLML→HTML5/AKN open-sourced at `github.com/legislation`. Supports **point-in-time** queries via `/{date}/data.xml`. Coverage of every required statute and SI:

- **Patents Act 1977** — `ukpga/1977/37`
- **Trade Marks Act 1994** — `ukpga/1994/26` (UKIPO also publishes a consolidated Aug-2024 PDF)
- **Registered Designs Act 1949** — `ukpga/Geo6/12-13-14/88` (UKIPO Aug-2024 PDF)
- **Copyright, Designs and Patents Act 1988** — `ukpga/1988/48` (Part III = unregistered design right)
- **Trade Secrets (Enforcement, etc.) Regulations 2018** — `uksi/2018/597`
- **Patents Rules 2007** — `uksi/2007/3291`; **Trade Marks Rules 2008** — `uksi/2008/1797`; **Registered Designs Rules 2006** — `uksi/2006/1975`
- **Intellectual Property (Unjustified Threats) Act 2017** — `ukpga/2017/14`
- **Intellectual Property Act 2014** — `ukpga/2014/18`

OGL v3.0. No dedicated PyPI client; httpx + lxml wrapper is sufficient.

## 13. UK Plant Breeders' Rights (APHA / DEFRA)

`gov.uk/guidance/plant-breeders-rights`; applications go through UPOV PRISMA; register search via UPOV PLUTO. No JSON API. Post-Brexit UK PVR domestic register has run via APHA since 1 Jan 2021; retained EU rights (CPVO grants effective 31 Dec 2020) co-exist for their remaining lifespan. CPVO is no longer UK-applicable. OGL v3.0 (UK side). Niche.

## Post-Brexit divergence (notes, not a data source)

UK left **EUIPO scope** on 1 Jan 2021 — EUIPO data is no longer authoritative for UK rights; ~1.4M comparable UK marks and ~700k re-registered UK designs were created on that date with UK numbers but inherited EU filing/priority dates. UK **remains an EPC contracting state** (EPC ≠ EU), so EP(UK) patents continue to flow through `epo_ops`; the UK-national PA 1977 / SPC route remains via UKIPO. **Comparable UK mark non-use clock** expired 1 Jan 2026 — UK-only use now required, relevant to TM-status models. The **Unjustified Threats Act 2017** aligned threats law across patents/TMs/designs (litigation-tooling concern, not register data). **CPVO** no longer covers UK; PVR is APHA-only.

---

## Recommended v1 scope

1. **`ukipo_mopp`** — Manual of Patent Practice. Static HTML scrape with quarterly refresh; mirrors `mpep`/`tmep` exactly. ~1 day. Highest leverage — agents query examination practice constantly.
2. **`ukipo_tm_manual`** — Manual of Trade Marks Practice + Tribunal section. Same pattern, another ~1 day. Pairs with #1 to give a complete UK examination corpus.
3. **`uk_statutes`** — Thin client over `legislation.gov.uk` returning CLML/AKN XML for PA 1977, TMA 1994, RDA 1949, CDPA 1988, Trade Secrets Regs 2018, Patents/TM/Designs Rules, Unjustified Threats Act 2017, IP Act 2014. ~2 days for the generic CLML fetcher + curated catalogue. Natural home for **point-in-time** queries (a feature the existing `legal_statutes` USC fetcher can't match).
4. **`uk_caselaw` (stretch)** — Find Case Law public API + Atom feed for Patents Court / IPEC / CoA / UKSC. LegalDocML XML is well-specified. ~3–4 days; gated on whether to apply for the computational-use licence (free, 1-year R&D form).

Total v1: ~1 sprint for assets 1–3; defer 4 to a second pass.

## Skip list

- **Ipsum / One IPO Search scraping** — wait for the One IPO REST API (H2-2025/2026). A brittle scraper now will be obsoleted in 12 months and adds little over `epo_ops`/INPADOC for UK patents.
- **UK TM and design register scraping** — no API, no bulk beyond TMJ XML; heavy overlap with already-skipped EUIPO TMview/DesignView. Re-evaluate when One IPO TM/Design APIs ship.
- **BAILII** — ToS-hostile to scraping; use Find Case Law.
- **UKIPO Hearings scraping** — small dataset, PDF-only, low automation leverage; fetch ad-hoc.
- **Designs Examination Guide** — no consolidated manual; ride along with RDA/RDR statutes.
- **UK PVR** — niche; UPOV PLUTO already covers it.

## Open questions

1. **One IPO API release date and shape** — OAuth-gated or open? Will the OpenAPI spec ship before GA? Contact `information@ipo.gov.uk`.
2. **Trade Marks Journal XML schema** — is the weekly XML stable and documented? Could be a cheap `ukipo_tmj` delta-feed wrapper.
3. **Find Case Law licensing** — does the free R&D computational-use licence permit caching under CoWork's allowlist model? If not, transactional licence may be needed.
4. **TM bulk dataset cadence** — 2016 FOI dump is stale; is there a refresh schedule now, or still FOI-only?
5. **Comparable UK mark/design enrichment** — do UKIPO records expose parent EUTM/RCD numbers cleanly, or must the link be rebuilt from EUIPO data?

## Compare/contrast with existing patterns

- **vs. EUIPO** — opposite. EUIPO has a modern OAuth 2.0 / OIDC developer portal with OpenAPI and quota plans; UKIPO has *no* production developer API for registers. One IPO is moving in EUIPO's direction but isn't there yet — expect a similar OAuth shape when it ships.
- **vs. USPTO ODP** — USPTO ODP is REST/JSON + API key. UKIPO has no equivalent; today the UK ecosystem looks like **pre-2022 USPTO** (manuals + scrape + bulk-data product catalogue). The MoPP/TM Manual wrappers will look almost identical to the existing `mpep`/`tmep` modules.
- **vs. KIPRIS Plus** — KIPRIS uses ServiceKey (single API key in query string) over XML. UKIPO has no key-gated API; the closest architectural analog is `legislation.gov.uk`'s clean URI scheme (CLML XML at `/data.xml`), which is more like **EUR-Lex CELLAR** than KIPRIS.
- **Pattern summary:** UKIPO v1 = **static-corpus fetching** (manuals, statutes) + optional **structured-XML legal-document ingestion** (CLML, LegalDocML). No auth, no quotas, OGL v3.0 throughout. Closest existing patterns: `mpep`/`tmep` for the manuals, EUR-Lex CELLAR (see EUIPO survey) for the statutory layer.
