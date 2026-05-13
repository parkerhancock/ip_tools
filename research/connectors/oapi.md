# OAPI (Organisation Africaine de la Propriété Intellectuelle) Data Source Survey

Connector-scoping survey for `patent-client-agents`. OAPI is the regional IP
office for 17 mostly-Francophone African states, headquartered in Yaoundé,
Cameroon. Created by the **Bangui Agreement** (1977, revised 1999, 2015,
2024), it operates a **unitary** system — a single OAPI application/grant
takes effect simultaneously in every member state, with the "national route"
via PCT closed. Filing volume is modest (low-thousands of patents/year
across all 17 states combined).

**Verdict — skip.** No public REST API, no online register, no bulk data
feed. The "patent / TM / design databases" advertised at
`oapi.int/en/service/online-services/` are an HTML-only WIPO Publish
(Apache Wicket + Solr) instance running on a bare IPv4 endpoint
(`http://195.24.202.12:9092/wopublish-search/`) with JSESSIONID cookies, no
TLS, and no documented API. EPO OPS already covers OAPI patents under
country code `OA`; WIPO Lex carries the Bangui Agreement (the **single
unified statute** covering ten annexes — patents, utility models, TMs,
designs, trade names, GIs, copyright, unfair competition, IC topographies,
plant varieties — in one instrument). Together those cover ~90% of the
practical OAPI agent need at zero engineering cost.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Bulk? | Feasibility |
|---|-------|-----|------|--------|-------|-------------|
| 1 | OAPI Patent / TM / Design Databases (WIPO Publish) | `195.24.202.12:9092/wopublish-search/` | None | HTML (Wicket + Solr) | No | **Hard** — scrape only, brittle session state |
| 2 | BOPI — Bulletin Officiel (gazette) | `siege.oapi.int/publication/...` + `oapi.int/wp-content/uploads/` | None | PDF (FlippingBook embed) | Per-issue | Easy URLs, **hard parse** (PDF-only) |
| 3 | e-Filing system (TMs only, since 2024-06-03) | account portal | Account | Web form | No | Skip — write-only, not a search surface |
| 4 | Bangui Agreement + Annexes I-X | `oapi.int/en/legal-framework/` + WIPO Lex | None | PDF + HTML (FR/EN) | Static | **Easy** — one corpus, ten rights |
| 5 | WIPO Lex OAPI profile | `wipo.int/wipolex/en/members/profile/OAPI` | None | HTML + PDF | Static | Easy — covered by planned `wipo_lex` |
| 6 | EPO OPS / Espacenet (patents, country code `OA`) | EPO OPS API | OAuth | XML/JSON | Yes | **Free** — already covered by `epo_ops` |

## 1. WIPO Publish at `195.24.202.12:9092`

All three online "databases" (patents, TMs, designs) point to the same
backend — WIPO Publish, an Apache Solr + Apache Wicket app WIPO licenses
to smaller IP offices. Probe of `/public/patents?1` returned HTTP 200 / 864
KB of Wicket-Ajax HTML with session-bound autocomplete URLs
(`?0-1.IBehaviorListener.0-body-...`). No OpenAPI, no JSON, no bulk export.
Per WIPO INSPIRE the coverage is **2014→present, bibliographic + cover
page only, 20 patents per gazette issue**; full publications are
"available on Espacenet" (i.e., EPO OPS) rather than on OAPI itself.

Not worth wrapping — Wicket session state is hostile to scraping, ToS is
opaque, and EPO OPS already exposes the same data with an actual API.

## 2. BOPI — Bulletin Officiel de la Propriété Industrielle

The weekly-ish gazette. Predictable URL pattern observed (`HTTP 200`):

- `siege.oapi.int/publication/brevet/{year}/bopi-{n}/` — patents (`BR`)
- `siege.oapi.int/publication/marque/{year}/bopi-{n}/` — TMs (`MQ`)
- `siege.oapi.int/publication/dmi/{year}/bopi-{n}/` — designs (`DM`)
- Geographical indications live separately at `ig-oapi.org`
- Direct PDF mirrors: `oapi.int/wp-content/uploads/{year}/{mm}/BOPI_{NN}{XX}{YYYY}.pdf`
  (e.g. `BOPI_06MQ2025.pdf`)

PDF-only, no XML, no ZIP+TXT. FlippingBook embed on some issues but the
underlying PDF is fetchable. ~10-12 issues/year per right-type. No
manifest, no RSS — enumeration is by walking the WordPress year/month
archives at `oapi.int/en/category/bopi/{patents,...}/`.

The structural problem: bibliographic blocks are PDF-laid-out by OAPI
staff with no fixed schema, formatting drifts across years. Reconstructing
structured records is real work for relatively little payoff once EPO OPS
covers patents.

## 3. e-Filing system (TM only, June 2024)

OAPI launched e-filing for **trademarks only** on 2024-06-03 — covering
searches, filings, renewals, recordals, and oppositions. Patents are
explicitly out of scope for this phase. Account-scoped, hard-copy
supporting documents still required by post. Not a public read surface.

## 4. Bangui Agreement — substantive law (the one asset worth caring about)

The Bangui Agreement is a **unified statute** covering ten distinct IP
rights in one instrument — broader than Brazil's LPI 9.279/96 (which also
unifies several rights). Annexes:

| Annex | Subject |
|-------|---------|
| I | Patents |
| II | Utility models |
| III | Trademarks and service marks |
| IV | Industrial designs |
| V | Trade names |
| VI | Geographical indications |
| VII | Literary and artistic property (copyright) |
| VIII | Unfair competition |
| IX | Layout designs (topographies) of integrated circuits |
| X | New plant varieties |

**Authoritative sources:**

- `oapi.int/en/legal-framework/bangui-agreement/` — OAPI's own FR/EN pages
- `wipo.int/wipolex/en/legislation/details/20275` — 1999 revision (EN)
- `oapi.int/wp-content/uploads/2023/11/anglais.pdf` — consolidated EN PDF
- WIPO Lex carries 1977 + 1999 revision + 2015 amendments + implementing
  regulations, in FR (canonical) and EN.

**2022 revisions** (Annexes III/IV/V, in force 2022-01-02): TM definition
extended to sound and audiovisual marks, certification marks added,
multi-class filings allowed, opposition window 6mo→3mo, GI protection
extended to agricultural and artisanal products.

**2024 revisions** (Annexes I/II, applied to applications filed
2025-01-01+): automatic **substantive examination** introduced (OAPI was
formal-exam-only before), pre-grant **opposition** with 3-month window,
voluntary divisional applications, LDC members exempted from
pharmaceutical-product patent obligation. Material shift — pre-2025 OAPI
patents were essentially unexamined registrations.

The **unified-statute design makes this corpus exceptionally cheap to
mirror**: one Annex-resolved document gives an agent citation-grade access
to all ten IP rights' substantive law for the entire Francophone-African
unitary jurisdiction. Drop it onto the planned `StaticLawCorpus` base
behind `wipo_lex`; no OAPI-specific code needed.

## 5. WIPO Lex coverage

OAPI has a member profile (`wipo.int/wipolex/en/members/profile/OAPI`)
with the 1977/1999/2015 Bangui texts, the 1999 implementing regulations,
and treaty memberships. EN translations available for headline texts; FR
canonical. The 2024 Annex-I/II revision should appear after WIPO's typical
6-18mo cataloguing lag. The planned Tier 1 `wipo_lex` client subsumes this
entirely.

## 6. Member states (confirmed, 17 as of 2026)

Benin, Burkina Faso, Cameroon, Central African Republic, Chad, **Comoros**
(joined 2013, most recent accession), Republic of the Congo, Côte d'Ivoire,
Equatorial Guinea, Gabon, Guinea, Guinea-Bissau, Mali, Mauritania, Niger,
Senegal, Togo. Largely Francophone with Lusophone (Guinea-Bissau, EG also
Spanish) and Arabophone (Mauritania) outliers.

## 7. Language

**French is canonical.** English exists for the Bangui Agreement (official
translation) and for OAPI website navigation. BOPI text, circulars,
implementing regulations, guidelines, and the WIPO Publish search UI are
French-only or French-primarily. Agent surfacing OAPI content needs FR→EN
MT in the pipeline or returns French strings to users.

## v1 scope — skip

OAPI fails the standalone-feasibility gate:

1. **No API** — WIPO Publish HTML, plain HTTP, Wicket session state.
2. **No bulk feed** — BOPI is per-issue PDF only; reconstructing
   structured data requires per-year, per-issue PDF parsing.
3. **EPO OPS already covers patents** under country code `OA` at zero
   marginal cost.
4. **WIPO Lex already covers the Bangui Agreement** — the planned Tier 1
   `wipo_lex` client subsumes the entire substantive-law surface.
5. **Filing volume is small** — opportunity cost not justified.

**Right v1 posture:** one Tier-1 backlog ticket — *"OAPI via `epo_ops` +
`wipo_lex` recipes"* (`get_oapi_biblio`, `get_oapi_legal_events`, Bangui
Annex-resolved citations) — and a one-line entry in the Tier-3 watch
table. No standalone module.

## Skip list

- WIPO Publish HTML scrape (`195.24.202.12:9092`) — brittle Wicket, no
  API, data redundant with EPO OPS
- BOPI PDF parser — high engineering cost, low payoff once EPO OPS covers
  patents (TM/design/GI parse only useful in narrow specialty cases)
- e-filing system — write-only, account-scoped
- GI registry (`ig-oapi.org`) — small dataset, browse only

## Open questions

1. **EPO OPS coverage depth for `OA`** — confirm whether INPADOC tracks
   OAPI legal events (oppositions, lapses, renewals) or just publication
   biblio. Likely the latter; opposition data only lives in BOPI PDFs.
2. **2024 Annex revision in WIPO Lex** — when does the text effective
   2025-01-01 appear? Watch the OAPI Lex profile.
3. **WIPO Publish public endpoints** — WIPO ships an admin layer to IPOs;
   verify with `wipo.int/wopublish` whether any public JSON/XML endpoint
   exists for OAPI's instance (would unlock #1 without scraping).
4. **BOPI manifest** — any RSS / JSON listing beyond walking the
   WordPress year/month archives at `oapi.int/en/category/bopi/`?

## Comparison: OAPI vs. ARIPO vs. Brazil INPI

| Aspect | OAPI (FR Africa) | ARIPO (EN Africa) | INPI Brazil |
|--------|------------------|-------------------|-------------|
| Statute pattern | **Unified** (Bangui — 10 Annexes, one instrument) | **Federated** (Harare/Banjul Protocols + national laws still in force) | **Unified** (LPI 9.279/96 + a few sui generis statutes) |
| Effect of grant | Unitary — single grant covers all 17 states automatically | Designated states only — applicant picks; grant validates per state | National only |
| Online register | No | Yes (`eservice.aripo.org/pdl/pqs/`) — Quick Search portal, Korea-donor-funded | No (pePI CAPTCHA-gated) |
| Bulk data | No (BOPI PDF only) | Limited (gazette PDFs) | Yes (**RPI weekly XML + dados.gov.br annual**) |
| EPO OPS coverage | Yes (`OA`) | Yes (`AP`) | Yes (`BR`) |
| WIPO Lex coverage | Strong (FR + EN) | Strong (EN native) | Strong (PT + EN) |
| Language | French primary; EN only for treaty texts | English-native | Portuguese primary; LPI EN translation good |
| Filing volume | Low (1-3k patents/yr) | Low (1-2k patents/yr) | High (~30k patents/yr) |
| **v1 verdict** | **Skip** — go via `epo_ops` + `wipo_lex` | **Skip-with-tickle** — ARIPO has an actual portal worth a feasibility revisit | **Build** (Tier 2 #11 — `inpi_rpi` + `brazil_law`) |

The **unified-statute pattern** is a feature in all three for our
`StaticLawCorpus` shape: one mirror, one citation namespace, multiple
rights' worth of substantive law. OAPI is the cleanest example of the
pattern (ten annexes, one document) but is dramatically thinner than
Brazil on machine-readable register data. The Bangui Agreement plus EPO
OPS recipes gets a Francophone-Africa-focused agent ~90% of what it needs
— building beyond that requires PDF parsing of BOPI, which is real work
for real little payoff at current filing volumes.

**Tier 3 disposition: documented and skipped.** Revisit if (a) OAPI ships
a WIPO Publish public JSON endpoint, (b) the 2024 substantive-exam shift
drives a 5x+ filing-volume increase that justifies BOPI parsing, or (c) a
paying customer needs OAPI-specific TM/design/GI register data not served
by EPO OPS.
