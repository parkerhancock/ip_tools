# Unified Patent Court (UPC) — Connector Survey

Survey of UPC and adjacent Unitary-Patent data sources for `patent-client-agents`.
Status: 2026-05. Flagged out of the DPMA survey as "important but orthogonal";
this is the standalone card. The UPC went live **2023-06-01**, jointly with the
Unitary Patent. It is a supranational court with exclusive (eventually)
jurisdiction over Unitary Patents and (subject to opt-out during the
transitional period) traditional European patents in participating EU states.
It is **not** part of the CJEU/General Court system even though the Court of
Appeal sits in Luxembourg.

## Cross-asset matrix

| # | Asset | Endpoint | Auth | Cost | Format | Bulk? | Python? |
|---|---|---|---|---|---|---|---|
| 1 | **CMS Public API v1.4** | `api-prod.unified-patent-court.org/upc/public/api/v4/*` | OAuth2 bearer (1800s) | free (registration) | JSON | per-call | none |
| 2 | **CMS A2A API v2.6** | same host, A2A path | OAuth2 (replaces former X-API-KEY) | free (representative-account gated) | JSON | batch opt-out submission | none |
| 3 | **Decisions & Orders** | `unifiedpatentcourt.org/en/decisions-and-orders` | none | free | HTML index + PDF/A | no (per-decision) | none |
| 4 | **Opt-out Register** | `unifiedpatentcourt.org/en/registry/opt-out` (public list); CMS read for structured | none for UI; OAuth2 for CMS | free | HTML/CSV via UI; JSON via CMS | yes (CMS) | none |
| 5 | **Unitary Patent Register** | EPO European Patent Register + OPS Register service | EPO OPS OAuth2 (already wrapped) | free (OPS quota) | XML/JSON | yes (subsequent B8/B9 pubs) | **we already wrap via `epo_ops`** |
| 6 | **Legal texts** (UPCA, Statute, RoP, Fees, CoC) | `unifiedpatentcourt.org/en/court/legal-documents` | none | free | PDF + HTML | n/a | none |
| 7 | **Hearings calendar** | published via CMS + per-division pages | none for UI | free | HTML | no | none |
| 8 | **Third-party trackers** | Bristows / Osborne Clarke / Unified Patents / upc.law / Kluwer / CMS Law / JUVE | varies | free or paid | HTML | no | none |

PISTE/EUIPO/IP-Australia-shaped OAuth2 client_credentials — one auth pattern,
two UPC APIs.

---

## Court structure and jurisdiction

### 1. Architecture (UPCA Arts. 6–9)

Three pillars:

- **Court of First Instance** — Central / Local / Regional Divisions.
- **Court of Appeal** — single seat, **Luxembourg**. Now operating **three panels**
  (third panel stood up at the beginning of 2026), with **Klaus Grabinski (DE)**
  as President.
- **Patent Mediation and Arbitration Centre (PMAC)** — twin seats in **Ljubljana
  (SI)** and **Lisbon (PT)**; director Aleš Zalar; formal opening
  **2026-06-02**. Operates in EN/FR/DE; mandate covers UP + SPC disputes;
  positioning itself for SEP/FRAND ADR. Settlements and awards are
  UPC-confirmable for enforceability across all contracting states.

### 2. Central Division seats — Munich / Paris / **Milan**

Paris is the **main seat** (UPCA Annex II) plus thematic sections:

- **Paris** — IPC sections B, D, E, G, H (electronics, telecoms, physics,
  textiles, civil engineering) plus SPC matters where the patent is in
  IPC class A or C.
- **Munich** — IPC section F (mechanical engineering, lighting, heating,
  weapons, blasting).
- **Milan** — IPC sections A and C (human necessities including
  pharmaceuticals, chemistry, metallurgy) — minus SPC carve-out which
  goes to Paris.

**Milan startup status (confirmed):** Milan was added by Administrative
Committee decision after the original London seat was vacated post-Brexit;
**operational since 2024-07-01**. So Tier-1 life-sciences cases that would
historically have gone to London now anchor in Milan.

### 3. Local Divisions (currently 13 LDs + 1 RD)

- **Germany — 4 LDs** (Düsseldorf, Mannheim, München, Hamburg). **Düsseldorf
  stood up a second panel in March 2026** — the only LD with a second panel,
  reflecting volume.
- **France — 1 LD** (Paris).
- **Italy — 1 LD** (Milan).
- **Netherlands — 1 LD** (The Hague).
- **Belgium — 1 LD** (Brussels).
- **Austria, Denmark, Finland, Ireland (signatory, pending), Portugal, Slovenia** —
  one LD each where established.
- Bulgaria, Luxembourg, Malta — **explicitly no LD/RD**, route through
  Central Division.

### 4. Regional Division

**Nordic-Baltic Regional Division** — seat **Stockholm**, hearings in
**Tallinn (EE)**. SE/EE/LV/LT participating. Caseload has been thin
relative to expectations — ~7 lawsuits filed since 2023 (Edwards
Lifesciences v Meril Life Sciences, Ocado v Autostore, Abbott v Dexcom
are the notable ones). No other Regional Division currently planned.

### 5. Participating contracting member states (18 as of 2026-05)

AT, BE, BG, DK, EE, FI, FR, DE, IT, LV, LT, LU, MT, NL, PT, **RO**, SI, SE.

**Romania ratification:** deposited **2024-05-31**, UPCA entered into force
in RO **2024-09-01**. Practical consequence:

- UPs granted **2023-06-01 → 2024-08-30**: 17 states.
- UPs granted **2024-09-01 → present**: 18 states (RO included).
- This is "Unitary Patent generations" — relevant for any analytics
  module that maps UPs to territories.

**Signed but unratified (7):** CY, CZ, EL (Greece), HU, IE, PL, SK.
**Non-signatories (2):** ES, HR. **Outside EU/UPC:** UK (post-Brexit), CH,
NO, TR — these EP designations route through national courts as before.

---

## Data assets

### 7. UPC CMS Public API v1.4

**Base URLs**
- Prod: `https://api-prod.unified-patent-court.org/upc/public/api/v4/`
- Pre-prod: `https://api-pre-prod.unified-patent-court.org/upc/public/api/v4/`

**Auth:** OAuth2 bearer token, **1800-second lifetime**. The legacy `X-API-KEY`
auth has been retired. Token endpoint issues access tokens against a registered
developer app (registration is via the "For IT developers" / "IT for developer"
portal).

**Documentation:** [Public API v1.4 PDF](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/upc-cms-public-api-documentation_v1_4.pdf)
(Feb 2023). SWAGGER/JSON also published under the IT-for-developers section.

**Endpoints (currently confirmed accessible during the transitional new-CMS rollout):**
- Search case
- Search case types
- List of languages

These read from the **previous CMS** during the transition window. Other
endpoints (parties, decisions, hearings) were available in v1.4 but are
intermittently behind the new-CMS migration; check live before scoping
specific fields. Each tool call should expect a 401 → token refresh dance.

**Rate limits:** not publicly documented. Empirical only — start polite,
1 RPS, back off on 429.

### 8. UPC CMS A2A API (v2.6 / v1.4 split)

**Purpose:** representative law-firm channel. Distinct from the Public API.
Two doc tracks:

- `upc-cms-a2a-api-documentation_v2_6.pdf` — main A2A reference
- `UPC-New_CMS_A2A%20API%20Documentation_V1_4_forPublication_StartOf8July.pdf` —
  new-CMS rollout-period addendum

**Capabilities (vs Public):** the A2A suite **now handles every opt-out
request** — the former Public-API opt-out path has been retired. Submitter
must be a registered representative; batch or single submission via a single
call (one patent or scripted sequential calls for portfolios). Each request
returns a unique case ID or a clear error message.

**Important asymmetry:** **opt-out creation only** is over A2A — **withdrawal
of an existing opt-out must be done via the CMS Front Office (web UI)**, not
API. That's a hard product constraint, not a roadmap item.

**Auth:** OAuth2 (replaced the legacy API-KEY).

**Difference vs Public API:** A2A = write path for representatives (opt-outs,
filings), Public = read path for everyone. Both share OAuth2 infra. For a
patent-research connector, we want **Public API**; A2A is a niche we should
**not** wrap absent a clear customer (it's a regulated filing channel and
mis-use has live-case consequences).

### 9. Decisions and Orders

Public index at `unifiedpatentcourt.org/en/decisions-and-orders`. Format =
**HTML index → PDF/A per decision**. Documents are PDF/A specifically
(format mandated by the RoP for everything submitted or issued). Redaction
of personal data per GDPR is automatic before publication.

**Languages:** procedural language of the underlying case, plus any required
translations:
- Central Division: EN / FR / DE.
- Local Divisions: EN + local language (DE for German LDs, IT for Milan,
  NL for The Hague, FR for Paris, etc.). **English has emerged as the
  dominant procedural language**.
- Court of Appeal may order translations into the CoA procedural language
  when it differs from first instance.

**ECLI:** not systematically assigned to UPC decisions in the way CJEU
decisions get them. Case-ID format is `UPC_CFI_n/yyyy` for First Instance,
`UPC_CoA_n/yyyy` for Court of Appeal, `ACT_NNNNNN/yyyy` for actions in CMS.
Cross-linking to national EU databases (e.g. `eurlex_cellar`, planned
`de_caselaw`) will need a custom UPC↔ECLI normalizer rather than a clean key
join.

**Search facets on the official UI:** text search, division filter, language
filter, date range, decision type. **The UI is functional but unloved** —
third-party trackers (United Patents, upc.law, Osborne Clarke) all advertise
"better organized than the court's own registry" as a selling point.

### 10. Opt-out Register

The official opt-out list **is public**, surfaced under
`unifiedpatentcourt.org/en/registry/opt-out`. Two access paths:

- **UI** — search/browse, no auth. The Registry enters an opt-out as soon as
  practicable after receipt; corrections take effect on the date the
  correction is noted.
- **CMS Public API** — structured read of opt-out records during the
  transitional period (subject to the new-CMS rollout caveat above).

For our purposes the opt-out feed is **the most valuable structured asset**
out of the entire UPC stack — it tells us, for every traditional EP patent,
whether the UPC has jurisdiction. Pairs with `epo_ops` family lookups: given
an EP publication, the answer "is this opted out?" is a 2-step join.

### 11. Unitary Patent Register — **lives at EPO, not UPC**

Critical routing fact: the **Register for Unitary Patent Protection** is an
**integral but separate part of the European Patent Register**, administered
by the **EPO**. It records unitary effect, limitations, licences, transfers,
revocation, lapse for EP-with-unitary-effect patents.

Access for us is **already wrapped** via `epo_ops`. Specifically:

- OPS Published-data and Register services support **both UP search and
  retrieval**.
- OPS Legal and Family services support **retrieval only** (not search).
- The **C0 publication marker** plus B7000 / B920 bibliographic elements in
  subsequent publications (B8/B9) carry UP status, member-state coverage,
  and UPC opt-out information.
- The Register endpoint shape (`GetRegisterUNIP`-style) retrieves the
  **Unitary Patent Package (UPP)** with date of registration of unitary
  effect, procedural-language code, and the list of designated states.

**Implication:** the v1 UPC connector does **not** need to wrap UP register
data. Extending `epo_ops` with `get_unitary_patent_package(epo_number)`
and `get_upc_opt_out_status(epo_number)` helpers covers it.

### 12. Hearings / calendars / filings

- **Hearing schedules:** published per division on the UPC website and
  reachable via the CMS. Not structured in a way that supports cross-division
  calendar pulls out of the box.
- **Docket entries / filings:** UPC has **substantially tighter
  confidentiality** than US PACER/CourtListener. The default is that
  pleadings are **not public**; third-party access is by reasoned request
  to the Registry (RoP 262 / 262A) and is regularly contested. What's
  reliably public: decisions, orders, opt-out entries, case metadata
  (parties, division, language). **No equivalent of PACER for UPC.**

### 13. Substantive law (UPCA Annex I / Annex II / RoP / Fees / CoC)

All free, all PDF + HTML at `unifiedpatentcourt.org/en/court/legal-documents`:

- **UPC Agreement (UPCA)** — 2013 treaty establishing the court.
- **Statute of the UPC** — Annex I to UPCA.
- **Rules of Procedure (RoP)** — **18th draft** adopted by the
  Administrative Committee on **2022-07-08**, in force **2022-09-01**. The
  "18th edition" framing in the wild is correct — there were 18 drafts.
- **Rules on Court Fees and Recoverable Costs.**
- **Code of Conduct for Representatives.**
- Casalonga publishes a free **interactive cross-referenced version** at
  `upc-casalonga.eu` in EN/FR/DE — useful as a stable canonical mirror
  outside the official site.

---

## Volume and trajectory

**Filing volume (Bird & Bird's "UPC in numbers" + JUVE + IPKat 2025 wrap-up):**

- **End of 2025:** ~946 cases at Court of First Instance (per the
  six-months-of-2025 update); ~471 cumulative infringement actions; 79
  cumulative revocation actions (standalone); 228 cumulative counterclaims
  for revocation; 80 cumulative PI applications.
- **2025 alone:** 239 infringement (+54.2% YoY), 27 revocations, 83
  counterclaim-revocations, 36 PIs.
- **First-instance dispositions:** 79 infringement merits decisions (260+
  pending); 30 revocation decisions (35 pending); PI grant rate ~45%.
- **DPMA card's 883-by-May-2025 figure** was correct as of that point; the
  current number is ~50% higher.

**Notable / precedent-shaping decisions** (for any decision-corpus tooling):

- **NanoString v 10x Genomics** (UPC_CoA_335/2023) — first substantive
  CoA decision, **overturned** Munich LD's PI; CoA used broader claim
  construction and found likely invalidity for lack of inventive step.
- **Sanofi/Regeneron v Amgen** (Munich CD then UPC_CoA_528–529/2024) —
  EP 3666797 revoked at first instance 2024-07-16, **reinstated on
  appeal** in the CoA's broad-functional-antibody-claim ruling.
- Edwards Lifesciences v Meril Life Sciences (Nordic-Baltic RD,
  `ACT_459769/2023`) — flagship heart-valve fight.
- Various **Nokia / OPPO / VIVO / Xiaomi** SEP cases across Munich and
  Mannheim LDs feeding into FRAND practice.

The corpus is small but growing fast; precedent value per decision is
unusually high because there is no other source of UPC case law.

---

## Existing tooling

- **Python clients:** **none** for UPC CMS specifically. `upcdb` on PyPI
  is unrelated (it wraps `upcdatabase.org` for product barcodes).
- **Commercial / paywalled trackers:**
  - **JUVE Patent** — editorial/news, paywalled archive, no API.
  - **Bristows UPC Review** — annual PDF, free.
  - **Osborne Clarke UPC tracker** — free web index, no API.
  - **Wolters Kluwer Manual IP — UPC Case Law Tracker** — subscription, no API.
  - **CMS Law UPC Tracker (`cms.law/en/int/insight/unified-patent-court`)** —
    free aggregate stats, no API.
  - **United Patents (`united-patents.eu`)** — free decisions registry,
    advertised as "better organized than the court's own"; no API.
  - **upc.law** — search/tag/category UI, no API.
  - **ip fray** — newsletter/blog with daily roundups; no API.
  - **Unified Patents Portal — UPC Module** (2024-02 launch) — paywalled.
  - **Darts-ip (Clarivate)** — commercial; UPC coverage rolled in.
  - **Lex Machina** — UPC coverage announced 2024-2025; commercial.
  - **IPlytics (LexisNexis)** — UPC analytics for SEP/standards work,
    commercial.

**Practical:** the open-data lane is wide open. No competing free Python
client; the only practical bottleneck is the CMS Public API's transitional
state and the lack of a structured decisions feed beyond HTML+PDF.

---

## Compare with what we have

- **vs USPTO PTAB (`uspto_odp`)** — both are inter partes patent tribunals
  with similar shapes (parties, patent-in-suit, decisions, exhibits). PTAB
  is administrative (IPR/PGR/CBM) and **filings are fully public**. UPC is
  judicial (infringement / revocation / DJ / PI) and **filings are
  presumptively confidential**. Decisions are public for both. The data
  model for UPC will look more like a court docket than a tribunal docket —
  closer to `pacer`/`courtlistener` shape than to `uspto_odp`.
- **vs CJEU / General Court (planned `eurlex_cellar`)** — **The UPC is not
  the CJEU.** Even though the UPC Court of Appeal sits in Luxembourg, the
  CJEU's IP jurisdiction is EUIPO-side (appeals from BoA) and
  preliminary-reference-side. UPC and CJEU intersect only via preliminary
  references the UPC may make to the CJEU on EU law questions; otherwise
  these are parallel court systems.
- **vs national IP courts (planned `de_caselaw` / `judilibre` /
  `uk_caselaw`)** — many UPC decisions either originate from disputes that
  also have parallel national proceedings (especially DE BPatG nullity
  actions running alongside UPC infringement) or cite national IP courts
  on substantive points. **Cross-linking will matter** — design
  identifier-mapping into the connector from day one (UPC case ID ↔ EP
  publication ↔ DE BPatG file number ↔ TJ Paris RG number).
- **vs `epo_ops`** — direct overlap on the Unitary Patent Register side;
  the right pattern is to **extend `epo_ops` with UP-aware helpers**
  rather than duplicate.

---

## Recommended v1 scope

Three modules, all small. They reuse two existing abstractions
(`OAuth2ClientCredentialsClient`, `StaticLawCorpus`) and add one new one
(decisions-feed harvester for HTML+PDF/A).

1. **`upc_cms`** — Public API v1.4 client. OAuth2 client_credentials
   against `api-prod.unified-patent-court.org/upc/public/api/v4/`. Initial
   surface: `search_cases()`, `search_case_types()`, `list_languages()`,
   plus opportunistic `get_case(case_id)` and `list_opt_outs()` if those
   endpoints remain accessible through the new-CMS transition. Token
   refresh every 1800s.
2. **`upc_decisions`** — Decisions/Orders harvester. Crawl the
   `unifiedpatentcourt.org/en/decisions-and-orders` index, fetch
   per-decision PDF/A + metadata, normalize case IDs
   (`UPC_CFI_n/yyyy` / `UPC_CoA_n/yyyy` / `ACT_nnnnnn/yyyy`), index
   division/language/date/decision-type. Pairs with the `StructuredCaseLawClient`
   base once we ship it (UPC decisions are not LegalDocML/Akoma Ntoso, so
   we get a plain-text+metadata path).
3. **`upc_statutes`** — Static-law fetcher for UPCA + Statute + RoP 18th
   edition + Court-Fees Rules + Code of Conduct. EN/FR/DE parallel.
   `StaticLawCorpus`-shape, mirrors `mpep` / `tmep` / planned UK MoPP.
   Casalonga's interactive code is a useful cross-reference but the
   primary source is `unifiedpatentcourt.org/en/court/legal-documents`.

**Plus one extension** (not a new module):
- **`epo_ops` UP helpers** — `get_unitary_patent_package(ep_number)`,
  `get_upc_opt_out_status(ep_number)`. Cheap on top of existing OPS
  Register client.

**Effort:** ~4 days for `upc_statutes` + `epo_ops` helpers (mostly piping),
~3-5 days for `upc_decisions` (depends on PDF-text extraction quality and
multilingual indexing), ~5-7 days for `upc_cms` (OAuth2 boilerplate is
amortized but the new-CMS transitional weirdness needs live testing).

## Skip list

- **`upc_a2a`** — the A2A API is a regulated filing channel for
  representative law firms. Wrapping it doesn't add agent value (you can't
  agentically file opt-outs on behalf of unrelated proprietors), and the
  mis-use surface is real. **Skip unless a paying customer is a UPC
  representative.**
- **PACER-style live filings index** — RoP 262 / 262A confidentiality plus
  per-document Registry vetting kill the cost-benefit; we get decisions
  for free, filings would require manual Registry requests.
- **Commercial-tracker scraping** (United Patents / upc.law / Osborne
  Clarke / Wolters Kluwer / Bristows) — ToS-hostile, redundant given the
  CMS+decisions feed, and locks us to brittle HTML.
- **CJEU IP rulings via UPC** — wrong gateway; planned `eurlex_cellar`
  handles CJEU directly.
- **National-court cross-linking as a v1 module** — design the **identifier
  normalization** into `upc_cms` and `upc_decisions` schemas from day one,
  but the actual cross-link enrichment lives in downstream tooling, not
  this connector.

## Open questions

1. **CMS Public API endpoint coverage during new-CMS transition.** Only
   `search case / search case types / list of languages` are publicly
   guaranteed to be accessible right now. **Need a live test** of
   `get_case(id)`, parties, hearings, opt-outs, decisions endpoints
   before scoping `upc_cms` surface. Contact: the IT-for-developers
   portal on `unifiedpatentcourt.org` for sandbox credentials.
2. **OAuth2 registration process.** Documentation references a
   "developer app" registration but exact ToS for redistribution under
   the CoWork allowlist's cache-and-serve model is unstated. Need a
   legal read on §§ around redistribution/caching before exposing
   `download_url` for CMS payloads.
3. **A2A vs Public API write/read split.** Confirmed direction
   (write → A2A representatives, read → Public for everyone) but the
   **opt-out withdrawal** path being CMS-Front-Office-only is the kind
   of asymmetry that will trip up agent users — needs explicit
   surfacing in tool descriptions.
4. **Opt-out data shape and bulk export.** The opt-out list is public via
   UI; question is whether CMS exposes a paginated `list_opt_outs(since=)`
   or only single-record lookups. If bulk, this becomes the
   highest-leverage UPC feed (every EP-in-force jurisdiction-tagged).
5. **PDF/A → structured-text quality on multilingual decisions.** UPC
   decisions are PDF/A with multilingual content; OCR isn't needed but
   layout extraction quality varies. Need to spot-check 10 decisions
   from each division before committing to "structured decisions feed".
6. **Hearing-calendar accessibility.** Are they via CMS endpoint or only
   per-division HTML pages? Affects whether `upc_cms.list_hearings()`
   is a v1 feature or a v2.
7. **PMAC data surface (2026-06-02 onward).** When PMAC goes live, will
   it publish anonymized awards / consent decrees as a separate feed,
   or fold into the UPC decisions registry? Watch-list item.
8. **ECLI mapping.** UPC doesn't natively assign ECLIs; do we mint
   `ECLI:EU:UPC:yyyy:nnn`-style synthetic identifiers (risky — not
   official) or just expose the native `UPC_*/yyyy` format? Defaults
   should be native + optional ECLI sidecar.

## Compare with existing patterns

- **OAuth2 client_credentials.** Same pattern as EUIPO (Tier 1) + IP
  Australia (Tier 2) + INPI France PISTE (Tier 3). UPC CMS is the **fourth
  bench-test of the planned `OAuth2ClientCredentialsClient` base** — by
  the time we ship it, the base will be hardened. Token-lifetime
  difference is trivial (1800s here, similar elsewhere).
- **Decisions feed.** UPC decisions are PDF/A + HTML metadata, **not**
  LegalDocML/Akoma Ntoso. So they fit the **non-structured** branch of
  `StructuredCaseLawClient` — the same branch that will handle
  `cipo_decisia` and `bpatg` HTML+PDF. Identifier normalization is the
  reusable part; the parser is bespoke.
- **Static-law corpus.** UPCA + Statute + RoP + Fees + CoC are a textbook
  `StaticLawCorpus` use case — EN/FR/DE parallel, stable PDFs, MPEP-shape.
  This becomes the 12th or 13th module riding on the same base.
- **Cross-jurisdiction graph.** The cleanest precedent for the cross-link
  story is `epo_ops` ↔ `uspto_odp` via priority claims; UPC adds a
  jurisdiction layer over the EP side and forces us to design proper
  identifier-mapping primitives. This pays off for `de_caselaw` and
  `judilibre` too.

---

## Update 2026-05-13: empirical investigation of the Public API enrollment path

Findings from an investigation conducted alongside the v0.11.0 `upc_decisions`
+ `upc_statutes` ship. Read these as corrections / additions to the sections
above; the original survey predates these probes.

### 1. The current Public API spec is v5, not v1.4

The v1.4 PDF (Feb 2023) is the documentation the corporate site links from
the news posts and the IT-for-developers page, but the **authoritative
spec is now Swagger v5.3** — `info.title: "UPC CMS Public API V5"`,
`info.version: v5`, paths under `/v5/...`. The JSON is at
`/sites/default/files/upc_technical_files/swagger_v5-3.json` on
`www.unifiedpatentcourt.org` (Cloudflare-gated for unauthenticated direct
GETs; reachable via a logged-in browser session).

A canonical snapshot is staged at
`research/openapi/upc_cms_public_api_v5-3.json` for offline reference.

### 2. Endpoint surface in v5.3

Ten GET-only paths, 64 schema definitions, no `securityDefinitions` block
(auth is layered on at the gateway, not declared in the spec):

| Method + path | Purpose |
| --- | --- |
| `GET /v5/caseTypes` | Search case types |
| `GET /v5/cases` | Search cases (18 query params: number, year, type, dates, patentNumber, decisionNumber, decisionFullText, parties, representative, judge, language, paging) |
| `GET /v5/documents/{caseType}/{number}/{year}` | All documents of a specific case |
| `GET /v5/documents/download/{id}` | Download a document binary |
| `GET /v5/languages` | List of languages |
| `GET /v5/opt-out/list` | Opt-out cases for a patent number (the highest-leverage public-API asset — answers "is this EP opted out?") |
| `GET /v5/opt-out/patentStatus` | Opted Out vs Withdrawn status (paginated) |
| `GET /v5/opt-out/statusTypes` | Opt-out status taxonomy |
| `GET /v5/representatives` | Representative search |
| `GET /v5/representatives/representationEntitlements` | Entitlement taxonomy |

The spec's declared `host: "upcbe"` over `schemes: ["http"]` is an
internal export artifact, not the real public-facing URL.

### 3. The Filing UI and the Public Read API are separate systems

Verified via direct inspection of an authenticated CMS Filing session at
`cms.unifiedpatentcourt.org`:

- **Filing UI auth model**: Keycloak OAuth2 + Bearer JWT (RS256).
  Issuer: `https://cms.unifiedpatentcourt.org/iam-service-develop/realms/front-office-public`.
  Token endpoint: `…/realms/front-office-public/protocol/openid-connect/token`.
  SPA client: `frontend`. Scopes: `openid profile email`. Token type:
  Bearer. **No mTLS** anywhere in the Filing UI stack.
- **Filing UI backends** (read off the SPA's JS bundle):
  `addressbook-api`, `dtk-api`, `epct-integration-api`, `npefiling-api`,
  `user-api`. **None match the swagger v5.3 read surface** — the
  Filing UI never calls `/v5/cases`, `/v5/opt-out/list`, etc.
- A CMS Filing account therefore **does not bootstrap into Public Read
  API access**. They're separately credentialed.

### 4. The Public Read API host rejects TLS at the network layer

Both `api-prod.unified-patent-court.org` and
`api-pre-prod.unified-patent-court.org` (same GCP-resolved IP, currently
`35.227.230.26`) reject incoming TLS connections from arbitrary clients:

- HTTPS GET to `/` returns `HTTP 000` (no HTTP layer reached).
- TLSv1.2 / TLSv1.3 handshakes close with `cipher=NONE`, `0 bytes read`,
  no `ServerHello`, no `CertificateRequest`.
- This persists even when the Filing UI's valid Bearer token is attached
  from inside an authenticated browser session.

Consistent explanations: source-IP allowlist enforced before the TLS
handshake completes (e.g. Cloud Armor pre-handshake rule), and/or mTLS
where the server doesn't bother negotiating with non-allowlisted source
IPs. DigiCert/QuoVadis publishes a "UPC Authentication Certificates"
page (linked below), which is suggestive of mTLS being part of the
picture, but not dispositive.

No alternate public-facing subdomain exists: `api.*`, `cms-api.*`,
`public-api.*`, `publicapi.*` on `unifiedpatentcourt.org` all return
NXDOMAIN. The corporate `www.*` host serves docs but not the API.

### 5. The enrollment workflow is not publicly documented

Verified by reading the verbatim text of:

- `/en/registry/it-developers` — links docs + Swagger; no registration
  surface, no portal link.
- `/en/news/update-public-apis-following-launch-first-phase-new-cms-roll-out`
  — describes endpoint availability, ends with *"For questions or further
  assistance, please contact us via the website contact form."*
- `/en/news/new-cms-release-automated-opt-outs-a2a-api-update-28-july-2025`
  — describes OAuth as the auth mechanism, ends with *"For further
  assistance, please contact your usual UPC CMS support representative."*

The strings `client_id`, `client_secret`, `register an application`,
`developer portal`, `application registration`, and `API access` (as
enrollment terminology) appear on **none** of those pages.

The Filing-UI walkthrough PDF (`How to access the new CMS – APIs test
environment_30.07.pdf`) covers user-account signup only and does not
mention API client credentials.

### 6. Pending question to UPC support

The Athena contact form (`/marketplace/formcreator/front/formdisplay.php?id=1`)
is the only documented contact channel for read-API enrollment questions.
Draft message body to submit:

> Subject: Public Read API enrollment vs. Filing UI access — separate systems?
>
> I'm building a read-only integration against the CMS Public API
> (Swagger v5.3 — search cases, opt-out reads, language and
> status-type lookups). I'm trying to get clarity on the enrollment
> path, and I want to share what I've found so I can ask precisely.
>
> 1. I have a CMS Filing account at `cms.unifiedpatentcourt.org`.
>    Login works. Auth is Keycloak OAuth2 + Bearer JWT, realm
>    `front-office-public`, issuer
>    `https://cms.unifiedpatentcourt.org/iam-service-develop/realms/front-office-public`.
>    The Filing UI calls these backends only: `addressbook-api`,
>    `dtk-api`, `epct-integration-api`, `npefiling-api`, `user-api`.
>
> 2. The Swagger v5.3 spec describes a separate read surface (paths
>    `/v5/cases`, `/v5/opt-out/list`, `/v5/opt-out/patentStatus`, etc.).
>    I cannot find this surface mounted at any path under
>    `cms.unifiedpatentcourt.org`; the SPA never calls it.
>
> 3. The presumed host `api-prod.unified-patent-court.org` (and the
>    pre-prod equivalent) reject TLS handshakes from arbitrary clients
>    before any HTTP layer — even with a valid Bearer token from the
>    Filing UI session attached. The TLS handshake closes with no
>    `ServerHello` in TLSv1.2 or TLSv1.3.
>
> The Filing account does not appear to grant Public Read API access.
> My questions:
>
> 1. Is the Public Read API at `api-prod.unified-patent-court.org` a
>    separate enrollment from the Filing UI signup, or is there a
>    self-service "request API access" step inside the Filing UI?
>
> 2. If separate: what does the read-API enrollment require?
>    Specifically:
>    - A separate Keycloak client / realm (e.g. not `frontend` / not
>      `front-office-public`)?
>    - A QuoVadis or DigiCert client TLS certificate (mTLS)?
>    - A source-IP allowlist?
>    - All of the above?
>
> 3. Could you confirm or correct the public-facing base URL for the
>    read API? `https://api-prod.unified-patent-court.org/upc/public/api/v5/`
>    is the best guess based on the swagger's `host`/`basePath` and the
>    older v1.4 PDF, but the swagger's declared `host: upcbe` is clearly
>    an internal placeholder.
>
> 4. Is there a sandbox / pre-prod equivalent of the read API
>    accessible to developers before production enrollment?

### 7. Implications for the connector roadmap

- `upc_cms` (v0.12.0) is **blocked on the answer to #6** — without
  enrollment we cannot smoke-test against the real endpoints, and the
  auth model (OAuth-only vs OAuth+mTLS vs OAuth+IP-allowlist) materially
  changes the client design and the deploy surface.
- The OAuth2 scaffold itself is already battle-tested by the EUIPO
  connectors (`OAuth2ClientCredentialsAuth` in `law_tools_core.oauth2`).
  If the answer turns out to be OAuth-only, the client is mostly
  boilerplate around the staged swagger; expect ~2-3 days end-to-end.
- If mTLS is required, an additional `httpx` `cert=` plumbing layer is
  needed and the OSS distribution story changes (users have to enroll
  their own QuoVadis cert; the wheel cannot ship credentials).
- The v0.11.0 wheel covers everything we can ship from public sources
  without enrollment: decisions/orders feed + statutes corpus + (deferred)
  EPO OPS UP/opt-out helpers for the EP-side view.

---

## Sources

- [UPC CMS Public API v5.3 Swagger JSON](https://www.unifiedpatentcourt.org/sites/default/files/upc_technical_files/swagger_v5-3.json) — **current authoritative spec** (Cloudflare-gated for direct GETs; offline copy staged at `research/openapi/upc_cms_public_api_v5-3.json`)
- [UPC Public API v1.4 documentation (PDF)](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/upc-cms-public-api-documentation_v1_4.pdf) — Feb 2023; **superseded by v5.3** but still linked from the corporate site
- [How to access the new CMS – APIs test environment (PDF, 2025-07-30)](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/How%20to%20access%20the%20new%20CMS%20%E2%80%93%20APIs%20test%20environment_30.07.pdf) — covers UI account signup only, not API client credentials
- [Athena contact form (formcreator/formdisplay.php?id=1)](https://athena.unifiedpatentcourt.org/marketplace/formcreator/front/formdisplay.php?id=1) — only documented contact channel for read-API enrollment questions
- [DigiCert/QuoVadis — UPC Authentication Certificates](https://www.digicert.com/tls-ssl/unified-patent-court-certificates) — suggestive of mTLS as part of the access model, not dispositive
- [UPC A2A API v1.4 (new-CMS rollout)](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/UPC-New_CMS_A2A%20API%20Documentation_V1_4_forPublication_StartOf8July.pdf)
- [UPC A2A API v2.6 (current)](https://www.unifiedpatentcourt.org/sites/default/files/upc_documents/upc-cms-a2a-api-documentation_v2_6.pdf)
- [Update on public APIs following launch of first phase of the new CMS](https://www.unifiedpatentcourt.org/en/news/update-public-apis-following-launch-first-phase-new-cms-roll-out)
- [Automated opt-outs via A2A API — update 2025-07-28](https://www.unifiedpatentcourt.org/en/news/new-cms-release-automated-opt-outs-a2a-api-update-28-july-2025)
- [For IT developers — UPC](https://www.unifiedpatentcourt.org/en/registry/it-developers)
- [Decisions and Orders index](https://www.unifiedpatentcourt.org/en/decisions-and-orders)
- [Opt-Out registry](https://www.unifiedpatentcourt.org/en/registry/opt-out)
- [UPC legal documents (UPCA / Statute / RoP / Fees / CoC)](https://www.unifiedpatentcourt.org/en/court/legal-documents)
- [Court presentation (structure)](https://www.unifiedpatentcourt.org/en/court/presentation)
- [PMAC official site](https://www.pmac-upc.org/en/contact-us)
- [PMAC opens June 2026 — Lewis Silkin](https://www.lewissilkin.com/insights/2026/03/25/the-upcs-usp-the-patent-mediation-and-arbitration-centre-opens-in-june-2026-102mo2k)
- [UPC member states](https://www.unifiedpatentcourt.org/en/organisation/upc-member-states)
- [Romania becomes 18th UPC member — Pearl Cohen](https://www.pearlcohen.com/romania-becomes-18th-upc-member-state/)
- [UPC structure — Herbert Smith Freehills Kramer](https://www.hsfkramer.com/insights/2023-06/upc-structure-%E2%80%93-local-regional-and-central-divisions-and-court-of-appeal)
- [All UPC judges — JUVE Patent](https://www.juve-patent.com/legal-commentary/all-upc-judges-and-their-current-capacities/)
- [Nordic-Baltic RD status — JUVE Patent](https://www.juve-patent.com/people-and-business/scandinavias-upc-gambit-high-hopes-despite-sluggish-start/)
- [UPC in numbers — 32 months — Bird & Bird](https://www.twobirds.com/en/insights/2026/the-upc-in-numbers-32-months-of-action)
- [UPC 2025 cases and outcomes — IPKat](https://ipkitten.blogspot.com/2026/02/upckat-2025-upc-cases-and-outcomes-what.html)
- [UPC received 50% more infringement cases in 2025 — JUVE Patent](https://www.juve-patent.com/legal-commentary/upc-received-50-more-infringement-cases-in-2025/)
- [Bristows UPC Review 2023-2024 (PDF)](https://www.bristowsupc.com/app/uploads/2024/12/Unified-Patent-Court-Review-2023-2024.pdf)
- [NanoString v 10x Genomics CoA — IPKat](https://ipkitten.blogspot.com/2024/03/first-substantive-decision-of-upc-court.html)
- [Amgen v Sanofi CoA UPC_CoA_528-529/2024 — IPKat](https://ipkitten.blogspot.com/2025/12/upc-court-of-appeal-tackles-broad.html)
- [Casalonga UPC interactive code](https://www.upc-casalonga.eu/?id_rubrique=4&lang=en)
- [UP register in EPO patent knowledge](https://www.epo.org/en/searching-for-patents/helpful-resources/unitary-patent-information)
- [United Patents — UPC decisions registry](https://united-patents.eu/)
- [Osborne Clarke UPC decision tracker](https://www.osborneclarke.com/news/osborne-clarke-launches-upc-decision-tracker)
- [Unified Patents — UPC tracker launch](https://www.unifiedpatents.com/insights/2024/2/13/unified-patent-court-upc-now-tracked-by-unified)
- [Wolters Kluwer UPC Case Law Tracker](https://www.wolterskluwer.com/en/news/wolters-kluwer-adds-new-unified-patent-court-case-law-tracker-to-kluwer-ip-law)
