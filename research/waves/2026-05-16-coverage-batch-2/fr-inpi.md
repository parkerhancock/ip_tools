# INPI France (FR) — Patents, Trademarks, Designs API Discovery

**Date:** 2026-05-16
**Scope:** Determine whether the Institut National de la Propriété Industrielle
(INPI France) exposes a public, queryable REST/JSON/XML API that we can proxy
at runtime, zero infrastructure on our side. Bulk dumps and HTML-only
surfaces are a **red** verdict.

**TL;DR:** **Yellow.** INPI France runs a real REST API stack at
`api-gateway.inpi.fr` (the "API PI" — `brevets` / `marques` / `dessins`)
covering FR patents 1902+, EP/WO designating FR, FR trademarks, and FR
designs. The technical surface is JSON/XML over POST with documented query
syntax and a Swagger spec ([`data.inpi.fr/content/editorial/swagger-pi`](https://data.inpi.fr/content/editorial/swagger-pi)).
BUT: (1) auth is **a logged-in INPI Data account + XSRF/CSRF token + access
token/refresh token flow**, NOT PISTE OAuth2 client_credentials — the
[2026-05 connector survey](../../connectors/inpi_france.md) was wrong on that
point; PISTE only fronts Légifrance, Judilibre, and the *gov-to-gov* API
Entreprise channel, not the public INPI Data APIs; (2) hard caps of
**10,000 requests/day, 10 GB/day, 10 requests/minute, 10,000 results per
search, position parameter capped at 500** mean the API is sized for bulk
sync, not high-volume live proxy traffic; (3) the [INPI reuse licence](https://data.inpi.fr/content/editorial/licences_reutilisation_donnees_inpi)
permits redistribution under attribution but the **CGU explicitly forbids
"any obstruction that would prevent or limit third parties' access to the
Service"** — a high-volume proxy is in tension with that clause. Patents
**duplicate EPO OPS** (FR national-route patents are also there). Real gap
plugs are **FR national TMs** and **FR designs (ST.86 XML)**, but the
quota math says this should be a **per-user BYOK** connector, not a
zero-infra hosted proxy.

---

## 1. Endpoint

INPI France exposes three layered surfaces:

### 1.1 INPI Data PI APIs (the real REST surface)

Base host: `https://api-gateway.inpi.fr/services/apidiffusion/api/`

Documented endpoints from [INPI Doc Technique API PI v1.0](https://www.inpi.fr/sites/default/files/Inpi_doc_tech_API_PI_v1.0_0.pdf)
and [Swagger PI](https://data.inpi.fr/content/editorial/swagger-pi):

| Right | Path | Method |
|---|---|---|
| Patents | `/brevets/search` | POST |
| Patents (notice) | `/brevets/{pubn}` | GET |
| Patents (image) | `/brevets/{pubn}/imageCouverture` etc. | GET |
| Trademarks | `/marques/search` | POST |
| Trademarks (notice) | `/marques/{numNat}` | GET |
| Designs | `/dessins/search` | POST |
| Designs (notice/image) | `/dessins/{numNat}` and image endpoints | GET |

Auth and access activation: [`Accès aux API - Propriété industrielle`](https://data.inpi.fr/content/editorial/apis_pi).

### 1.2 PISTE (gouvernmental OAuth gateway)

`https://piste.gouv.fr/` — **does NOT host the INPI PI APIs** (despite the
[2026-05 connector survey](../../connectors/inpi_france.md) implying it might).
PISTE fronts **Légifrance, Judilibre, DataPass, Chorus Pro, API Entreprise**
and similar central-state APIs. INPI participates in PISTE only via
**API Entreprise** ([`api.gouv.fr/producteurs/inpi`](https://api.gouv.fr/producteurs/inpi)),
which is **a gov-to-gov channel restricted to French public-sector users**
(prefectures, tax authorities, etc.) — not open to private SaaS proxies.

### 1.3 data.inpi.fr web UI + SFTP bulk

[`data.inpi.fr`](https://data.inpi.fr/) — HTML search portal + SFTP delivery
of weekly stock and daily delta packages. Out of scope for a zero-infra
proxy.

---

## 2. Auth

The INPI Data PI APIs are **not OAuth2-based**. The flow is:

1. Sign up at [`data.inpi.fr/login`](https://data.inpi.fr/login) — free,
   email-validated account.
2. In *Mon espace client* → *Accès APIs PI*, subscribe to one or more
   feeds (Brevets, Marques, Dessins) and accept the
   [INPI reuse licence](https://data.inpi.fr/content/editorial/licences_reutilisation_donnees_inpi).
3. Receive an activation link → create an API-specific password at
   `api-gateway.inpi.fr`.
4. Per-call flow (per the [technical doc PDF](https://www.inpi.fr/sites/default/files/Inpi_doc_tech_API_PI_v1.0_0.pdf)):
   - `GET /token` to receive an **XSRF-TOKEN** in a cookie + header.
   - `POST /login` with credentials + the XSRF token to receive an
     **access token** (JWT-shaped) and a **refresh token**.
   - Use the access token on subsequent search/notice requests.

This is a **session-bearer-token model**, not OAuth2 client_credentials.
There is no signed-app-client / scope-grant flow; it's "a logged-in human
account, scriptable."

**Foreign-developer accessibility:** Account creation requires email +
name; no SIREN, French address, or French ID is documented as
mandatory. No primary source found stating foreign developers are
restricted — but no primary source confirms they aren't, either. The INPI
documentation is French-only; the [INPI English access page](https://www.inpi.fr/en/resources/intellectual-property/access-to-API-and-FTP)
exists but is thin and points back to the same `data.inpi.fr` flow.

---

## 3. Query Language

POST body JSON. From the [technical doc PDF](https://www.inpi.fr/sites/default/files/Inpi_doc_tech_API_PI_v1.0_0.pdf):

```json
{
  "Collections": "FR,EP,WO,CCP",
  "Query": "TIT:(téléphone AND mobile) AND IPRC:H04W*",
  "Fields": "PUBN,NAT,TIT,PUBD,DEPN,DEPD,IPRC,INV,DEM",
  "position": 0,
  "size": 100
}
```

- **Query syntax** is **SolR Lucene** — supports field-scoped terms
  (`TIT:`, `IPRC:`, `INV:`, `PUBD:[2020-01-01 TO 2025-12-31]`),
  Boolean operators, wildcards, fuzzy match.
- **Fields** are INID-coded (`PUBN` publication number, `TIT` title,
  `IPRC` IPC, `INV` inventor, `DEM` applicant, etc.).
- Comparable surface for `marques/search` (Vienna codes, Nice classes,
  applicant) and `dessins/search` (Locarno class, designer, applicant).

This is **the cleanest query surface of any national IP office on our
roadmap** — better than UKIPO's IPSUM (no query language), DPMA's
DPMAconnectPlus (Boolean only, paid), or CIPO (HTML only).

---

## 4. Pagination

From the [technical doc PDF](https://www.inpi.fr/sites/default/files/Inpi_doc_tech_API_PI_v1.0_0.pdf):

| Field | Behavior |
|---|---|
| `position` | Offset into result set. Default 0, **max 500**. |
| `size` | Page size. Default 10, max published in Swagger. |
| Total cap | A single query cannot return more than **10,000 results**, per [INPI Data API conditions](https://data.inpi.fr/content/editorial/apis_pi). |

**Implication:** Deep pagination beyond 500 offset is not possible — you
must split the query (date facet) to walk the full corpus. Standard
ElasticSearch / SolR deep-pagination limit pattern.

---

## 5. Response Shape

- **Search responses:** JSON envelope `{"total": N, "results": [{...}]}`,
  each result a bibliographic document.
- **Notice responses:** XML by default (WIPO ST.36 for patents,
  ST.66 for trademarks, **ST.86 v1.0** for designs); JSON also supported
  per the [INPI access page](https://data.inpi.fr/content/editorial/apis_pi).
- **Image responses:** PDF (cover sheet) or PNG/TIFF.
- **CSV** is offered on the FTP/SFTP side, not on the live API.

Source: [Accès aux API - Propriété industrielle](https://data.inpi.fr/content/editorial/apis_pi)
("Les données peuvent être téléchargées en XML, JSON, CSV, ou PDF depuis
les APIs ou depuis les serveurs FTP / SFTP. Le nouveau format est basé
sur JSON.").

---

## 6. Coverage Scope

Coverage windows per [Accès aux API - Propriété industrielle](https://data.inpi.fr/content/editorial/apis_pi)
and the [WIPO INSPIRE DATA INPI Portal entry](https://inspire.wipo.int/data-inpi-portal-patent-database):

| Right | Coverage |
|---|---|
| **Patents (FR)** | French patent applications & **certificats d'utilité** published since **1902** |
| **Patents (EP)** | EP applications/publications designating FR since **1978** |
| **Patents (WO)** | PCT applications since **1978** |
| **Patents (CCP)** | Supplementary Protection Certificates since **1993** |
| **Trademarks** | FR national TMs + EUTM-FR + Madrid IRs designating FR; BOPI bulletin in bulk |
| **Designs** | FR national designs since **1910**; international designs (Hague) since **1985** |

**PIBD jurisprudence migration:** the older [`pibd.inpi.fr`](https://pibd.inpi.fr/)
case-law surface was [frozen on 11 March 2026](https://pibd.inpi.fr/) ("La
base de jurisprudence fait actuellement l'objet d'une refonte importante
pour enrichir ses données. Depuis le 11 mars, celle-ci n'est plus mise à
jour et sera prochainement à retrouver sous une interface mise à jour sur
DataINPI."). The replacement on `data.inpi.fr` has no published API
schema yet; treat case-law access as **a separate problem** (we route to
Judilibre + Légifrance for FR IP case law in any event).

**Important duplication note:** FR patent biblio is **already covered by
EPO OPS** with country code `FR` (national-route filings + EP designations).
The marginal increment from INPI's API for patents is:
- Pre-1978 FR patents (1902-1977) not in INPADOC — **niche** but real.
- Live legal-status events not yet mirrored to INPADOC (typically <2-week lag).
- **Certificats d'utilité** — FR utility certificate, low volume (<1000/yr),
  partially in INPADOC but not always at full fidelity.

The genuine gaps are **FR national trademarks** (~190k active, not in EUIPO)
and **FR national designs** (not in EUIPO RCD).

---

## 7. Rate Limits / Quotas

Published in [Accès aux API - Propriété industrielle](https://data.inpi.fr/content/editorial/apis_pi)
and the [INPI reuse licence](https://data.inpi.fr/content/editorial/licences_reutilisation_donnees_inpi):

| Limit | Value |
|---|---|
| Daily requests per technical account | **10,000** |
| Daily volume per technical account | **10 GB** |
| Per-minute throughput | **10 requests/min** (regulated extraction threshold) |
| Per-query result cap | **10,000 results** |
| Per-query pagination depth | offset ≤ **500** |
| Annual extraction cap | **10% of annual flow** triggers "regulated" status |

The **10 requests/minute** is the operational bottleneck for a hosted
proxy. Across 1000 active users that's a ~6-second median wait per
request — unworkable for an interactive agent UX without per-user keys.

---

## 8. Terms of Service

Three layered documents apply:

1. **[Conditions générales d'utilisation - Data INPI](https://data.inpi.fr/content/editorial/cgu)**
   — service-level CGU. Key clause for us: *"L'utilisateur s'engage à ne
   pas faire obstacle au fonctionnement du Service ou à en faire un usage
   frauduleux. Toute entrave qui aurait pour effet d'empêcher ou de
   limiter l'accès des tiers au Service ou l'utilisation par eux-mêmes
   est interdite, sous peine de voir l'utilisateur privé d'accès aux
   services sans préavis."* (Translation: "The user undertakes not to
   obstruct the operation of the Service or make fraudulent use of it.
   Any obstruction that would prevent or limit third parties' access to
   the Service or its use by them is prohibited.")

   A high-throughput proxy that bottlenecks on the 10 req/min cap on a
   shared technical account *plausibly* meets that "limit third parties'
   access" criterion. Risk: account suspension without notice.

2. **[INPI reuse licence](https://data.inpi.fr/content/editorial/licences_reutilisation_donnees_inpi)**
   — content licence; an approved Etalab Open Licence 2.0 variant. **Permits
   redistribution** including for commercial purposes, with attribution and
   integrity-of-source preservation. Not the bottleneck.

3. **[INPI Licence des données RNE 2024](https://www.inpi.fr/sites/default/files/Licence%20donn%C3%A9es%20RNE_2024_0.pdf)**
   — only applies to RNE company data, not PI rights. Not relevant for
   patent/TM/design coverage.

**Bottom line on ToS:** The reuse licence is generous; the CGU's
anti-obstruction clause is the live risk for hosted-proxy use. Per-user
BYOK avoids the issue entirely (each user runs against their own quota).

---

## 9. Operational Notes

- **French-language primary.** The technical docs, CGU, error messages,
  and Swagger UI are French-only. The [English API access page](https://www.inpi.fr/en/resources/intellectual-property/access-to-API-and-FTP)
  exists but is a stub that points back to `data.inpi.fr` for actual
  account management.
- **Schema standards.** Designs use **WIPO ST.86 v1.0** XML — same as
  EUIPO RCD bulk, so a shared parser amortizes. Patents use **ST.36**;
  trademarks **ST.66**.
- **Update cadence:**
  - Patents & trademarks: **weekly (Friday)**.
  - Designs: **bi-weekly**.
  - RNE companies: **daily** (out of scope for PI rights).
- **PIBD migration.** As of **2026-03-11**, the old jurisprudence base
  stopped being updated. The replacement on `data.inpi.fr` has no
  documented API yet. For FR IP case law we should route to **Judilibre**
  (Cour de cassation API) and **Légifrance** (already shipped as
  `FR/Legifrance/IP`).
- **No IP allowlisting / geofencing** is documented for `api-gateway.inpi.fr`.
- **WIPO INSPIRE** lists the [DATA INPI Portal as a tier-1 patent
  database](https://inspire.wipo.int/data-inpi-portal-patent-database) —
  i.e. INPI's data is recognized as authoritative for FR rights.

---

## 10. Verdict

| Right | Verdict | One-sentence reason |
|---|---|---|
| **Patents** | 🟡 **Yellow** — defer | Real REST API exists, but FR patent biblio is already in EPO OPS via INPADOC; the marginal coverage (pre-1978, certificats d'utilité, live legal status) doesn't justify the 10 req/min bottleneck for a hosted proxy. Revisit as BYOK. |
| **Trademarks** | 🟡 **Yellow** — BYOK candidate | This is a real gap: ~190k active FR national TMs not in EUIPO. The API is clean. But quota constraints (10/min) and ToS anti-obstruction clause make it a **per-user BYOK** connector, not a zero-infra proxy. |
| **Designs** | 🟡 **Yellow** — BYOK candidate | Same as TMs — FR national designs are a gap vs. EUIPO RCD, the ST.86 XML is standard, but the 10/min cap precludes a shared-key hosted proxy. |

**Overall:** **🟡 Yellow.** Unlike CIPO (🔴 across the board because no
REST API exists), INPI France has a perfectly serviceable REST API — the
blocker is the **session-based auth + per-account quota + CGU anti-
obstruction clause**, which together push this connector into the
**BYOK pattern** (à la JPO J-PlatPat or DPMA per-user contracts) rather
than a hosted proxy. The strategic answer is:

1. **Patents:** Skip — EPO OPS via [`patent_client_agents.epo_ops`](../../src/patent_client_agents/epo_ops/)
   covers FR national-route + EP designations sufficiently for an agent UX.
2. **FR national TMs and designs:** Build a **BYOK** `inpi_pi` connector
   that accepts user-provided INPI Data credentials and proxies on
   their behalf. This is the only zero-infra-on-our-side path that respects
   both the CGU and the quota math.
3. **FR statutes:** Already shipped as `FR/Legifrance/IP` via the
   [`patent_client_agents.legifrance`](../../src/patent_client_agents/) bundle
   (PISTE OAuth — that part of the survey *was* correct, just for
   Légifrance, not INPI PI).
4. **FR IP case law:** Pursue Judilibre via PISTE (separate workstream) —
   not gated on INPI's PIBD migration.

---

## Drift vs. `connectors/inpi_france.md` (2026-05 survey)

| Claim in older survey | Status now |
|---|---|
| "PISTE OAuth2 single client lights up Légifrance + Judilibre + INPI PI" | **Wrong on INPI PI.** PISTE fronts Légifrance + Judilibre + API Entreprise. The INPI Data PI APIs are on a separate `api-gateway.inpi.fr` host with session-token auth, not PISTE OAuth. |
| "Quota: 10,000 requests/day and 10 GB/day per technical account" | **Confirmed, plus 10 req/min throughput cap and 10,000-result query cap not mentioned in the survey.** |
| "PIBD migration to data.inpi.fr 'later in the summer' 2026" | **Already in progress** — frozen 2026-03-11, replacement timeline still vague. |
| "INPI reuse licence is approved Etalab variant" | Confirmed. |
| "FR national TMs not in EUIPO (~190k active)" | Confirmed — primary gap-plug rationale. |
| "INPI directives in PDF" | Confirmed — separate static-corpus opportunity. |

---

## Executive Summary

INPI France runs a **legitimate REST API** on `api-gateway.inpi.fr`
covering FR patents 1902+, EP/WO designating FR, FR trademarks, and FR
designs — JSON envelopes, SolR Lucene query syntax, ST.36/ST.66/ST.86
XML responses, and free-after-registration access. The technical surface
is the cleanest of any national IP office we've surveyed (better than
UKIPO's IPSUM, DPMA's contract-gated DPMAconnectPlus, CIPO's HTML-only).
What blocks a zero-infra hosted proxy is the combination of (1) **session-
bearer-token auth bound to a personal Data INPI account** (not PISTE OAuth
client_credentials — the [2026-05 survey](../../connectors/inpi_france.md)
was confused on this point; PISTE fronts Légifrance/Judilibre, not INPI
PI), (2) **10 requests/minute throughput** + 10,000 daily request cap on
the account, (3) [CGU anti-obstruction clause](https://data.inpi.fr/content/editorial/cgu)
that puts a high-volume shared-account proxy on shaky legal ground. The
right shape for this connector is **per-user BYOK** (à la JPO J-PlatPat).
The genuine coverage gaps are **FR national TMs and FR national designs**;
FR patents are already in EPO OPS via INPADOC. Recommended verdict:
**🟡 Yellow** — defer hosted-proxy build, queue BYOK design.
