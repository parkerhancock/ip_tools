# IMPI Mexico (MX) — Patents, Trademarks, Designs API Discovery

**Date:** 2026-05-18
**Scope:** Determine whether the **Instituto Mexicano de la
Propiedad Industrial** (IMPI, the Mexican Institute of Industrial
Property) exposes a public, queryable REST/JSON/XML API that we can
proxy at runtime, with zero infrastructure on our side. Bulk dumps
and HTML-only surfaces would be a **red** verdict; per-user BYOK is
**yellow**; undocumented-but-unauthenticated stable JSON is
**green**. Mexico is a [USMCA party (Chapter 20 — IP)](https://ustr.gov/trade-agreements/free-trade-agreements/united-states-mexico-canada-agreement/agreement-between)
but IMPI maintains its own national register entirely — USMCA is a
substantive-law harmonization vehicle, not a data-sharing
arrangement.

**TL;DR — Verdict: 🔴 red.** IMPI publishes **no documented
REST/JSON API**, **no entry in the [WIPO IP API Catalog](https://apicatalog.wipo.int/)**
(probed 2026-05-18 — 0 IMPI entries among 179 total across 10 IPOs:
DPMA, EPO, EUIPO, IP Australia, JPO, MOIP KOREA, QAZ, UPRP, USPTO,
WIPO), and **no analogue to OEPM's WSDL bundle or SE/PRV's
reverse-engineerable JSON layer**. There IS a Vue.js SPA at
[`marcia.impi.gob.mx/marcas/search`](https://marcia.impi.gob.mx/marcas/search)
with a backend JSON API at `/marcas/search/internal/*` that
responds to JSON calls with session + CSRF tokens, but **the
practical-use barrier is structural** — every other IMPI
infrastructure surface (`siga.impi.gob.mx`, `vidoc.impi.gob.mx`,
`datosabiertos.impi.gob.mx`, `acervomarcas.impi.gob.mx:8181`,
`patenteslibres.impi.gob.mx`, `eservicios.impi.gob.mx`,
`pase.impi.gob.mx`) resolves to a single Telmex IP block at
`187.130.250.0/24` and **times out completely from US-egress IPs**.
Only the Akamai-fronted `www.gob.mx/impi` and the separately-
hosted `marcia.impi.gob.mx` are reachable from our network.

**Material consequence:** even if we wrote a connector against the
MARCia JSON endpoints, the *companion* surfaces — patent files
(VIDOC), classification (ClasNiza), the Gaceta (SIGA), the
electronic prosecution portal (PASE), the bulk open-data catalog
(datosabiertos) — would all need a Mexican-IP egress proxy or
residential exit node to function. Per [MEMORY:
project_cloud_run_egress.md], Mexican government infrastructure
filters cloud-egress IPs even harder than USPTO TESS or
unifiedpatentcourt.org, and that filter is **whole-subdomain-block
DROP, not 403**. This is the structural blocker.

**Material distinguishers vs. the wave so far:**
- **vs. SE/PRV (green undocumented):** PRV ships its register data on
  modern hosts that respond globally with permissive licenses
  (CC0 1.0 / CC BY 4.0). IMPI's register surfaces are on Telmex
  infrastructure that geo-filters non-MX egress; no published
  reuse license outside the open-data portal (which itself is
  unreachable from US).
- **vs. ES/OEPM (yellow BYOK):** OEPM publishes a documented
  catalogue of five SOAP web services with a per-applicant access
  form, technical manuals, and an Aviso legal permitting
  commercial reuse with attribution. IMPI has none of that — no
  catalogued web services, no access form for non-residents, no
  published API ToS, no WSDLs.
- **vs. CN/CNIPA (red, structural foreign-developer block):** Both
  red, but for different reasons. CNIPA's red is that account
  signup requires a Chinese mobile number; the infrastructure
  technically responds. IMPI's red is that the infrastructure
  itself **does not respond** to non-MX egress. There's no
  account to apply for.
- **vs. AT/ÖPA (red, personal-use Impressum):** Both red but at
  different layers. ÖPA *responds* with HTML, refuses commercial
  reuse via Impressum. IMPI *doesn't respond at all* to most
  egress IPs.

The infrastructure barrier is decisive: **a zero-infra proxy
posture against IMPI is not feasible.** Coverage of MX has to flow
through EPO INPADOC (transitively, for granted MX patents) +
Google Patents (transitively, for MX trademarks and designs that
reach it), with a documented gap on national-only file histories,
electronic prosecution events, the Gaceta, and substantive
register status events.

---

## 1. Endpoint inventory

### 1.1 Public-facing IMPI infrastructure (the surface map)

| Host | Purpose | Stack | Reachable from US? |
|---|---|---|---|
| `www.gob.mx/impi` | Institutional landing | Akamai-fronted | ✅ (returns 404 on `/impi` GET, valid Akamai response — endpoint not the issue) |
| `marcia.impi.gob.mx` | Trademark search (MARCia) | Vue.js SPA + Spring backend | ✅ (responds 200) |
| `siga.impi.gob.mx` | Gazette + patent search (SIGA) | JSF stack at `/newSIGA/content/common/principal.jsf` | ❌ (timeout — `187.130.250.132`) |
| `vidoc.impi.gob.mx` | Document viewer | Web app | ❌ (timeout — `187.130.250.x`) |
| `acervomarcas.impi.gob.mx:8181` | Legacy Marcanet (`/marcanet/`, `/UCMServlet`) | servlet on port 8181 | ❌ (timeout) |
| `datosabiertos.impi.gob.mx` | IMPI open-data portal | SharePoint `.aspx` | ❌ (timeout — `187.130.250.144`) |
| `patenteslibres.impi.gob.mx` | Public-domain patent browser | Web app | ❌ (timeout) |
| `eservicios.impi.gob.mx` | Electronic-services portal (PASE entry) | Web app | ❌ (timeout) |
| `pase.impi.gob.mx` | Electronic prosecution (patents/utility models/designs) | API surface (search hit `pase.impi.gob.mx/api/guide/getGuide`) | ❌ (timeout) |
| `clasniza.impi.gob.mx` | Nice classification tool | Web app | ❌ (timeout) |
| `historico.datos.gob.mx` / `www.datos.gob.mx` | Mexico federal open-data portal | CKAN-style | ✅ (Akamai/nginx — responds) |

**Key infrastructure observation.** All `*.impi.gob.mx` hosts
except `marcia.impi.gob.mx` resolve to addresses in the Telmex
`187.130.250.0/24` block and **silently drop** (TCP SYN unanswered
— `Connection timed out after 15011 milliseconds`) from US
egress. This is not a WAF 403 / not a Cloudflare challenge / not a
geofence with a "this content is not available in your country"
page — it's a packet-level drop, indicating either ISP-level ACL
or a deliberate non-MX-egress block on the IMPI Telmex circuit.
The block is **subdomain-wide**, not per-app.

`marcia.impi.gob.mx` is the only IMPI subdomain hosted on
different infrastructure (likely a tmv.io / tmvapi.com CDN edge —
the MARCia CSP allows `*.tmvapi.com`, `*.tmv.io`, `*.tmv.cloud`
for `img-src`, and the image CDN base is at
`https://prod.impi.static.tmv.io/lm/tmimage_trim96/MX/`). That's
why MARCia survives and everything else doesn't.

### 1.2 MARCia (`marcia.impi.gob.mx`) — the only reachable surface

The MARCia trademark search SPA is a Vue.js application served at
[`marcia.impi.gob.mx/marcas/search`](https://marcia.impi.gob.mx/marcas/search).
Per third-party comparison sources (e.g.
[easylex.com](https://easylex.com/blog/marcia-vs-marcanet),
[concretalegal.com](https://concretalegal.com/blog/marcanet-vs-marcia/)),
**MARCia updates daily**, while the legacy Marcanet
(`acervomarcas.impi.gob.mx:8181/marcanet/`) updates every 15–30
days. MARCia was introduced [mid-May 2020 per IMPI's "Marcia.
Búsqueda de marcas" gob.mx page](https://www.gob.mx/impi/acciones-y-programas/marcia-265449).

**Stack:**
- Vue.js SPA, code-split at `static/js/app.91d47144.js` (~1.46 MB).
- Spring Boot backend — JSESSIONID cookie, signed `SESSIONTOKEN`
  JWT (`HS512`, jti + sub claims) issued on first GET to
  `/marcas/search`, XSRF token in `XSRF-TOKEN` cookie + `_csrf`
  meta tag, validated on POSTs via `X-XSRF-TOKEN` header.
- CSP: `connect-src 'self'` — the SPA can only call back to
  `marcia.impi.gob.mx`. Image CDN at `*.tmv.io`/`*.tmvapi.com`
  for trademark images.
- Hardcoded SPA constant: `lastIndexingDate: '02 Feb 2020'` —
  this is a default fallback string baked into the bundle's
  `window.VARS` object, **not** the actual data currency. Third
  parties confirm daily indexing.

**API surface extracted from the SPA bundle.** All paths are
relative to `baseUrl = '/marcas'` and use POST with JSON content
type `application/json;charset=UTF-8`:

| Path | Purpose | Notes |
|---|---|---|
| `/marcas/security/session/exists` | session existence check | returned **500** on direct probe — needs full session context |
| `/marcas/security/session/login` | establish authenticated session | unknown if regular user can hit it; the SPA uses anonymous sessions |
| `/marcas/security/session/save` | persist preferences | |
| `/marcas/security/session/preferences` | get user preferences | |
| `/marcas/security/session/delete` | logout | |
| `/marcas/search/internal/counts` | overall corpus size | **200** on probe — returned `{"records": 0, "extracts": 0}` for fresh anonymous session (no search registered) |
| `/marcas/search/internal/record` | POST — register a search query, returns `searchId` | needs query payload — opaque structure (rejected our `{title:"NIKE"}` attempt with 500) |
| `/marcas/search/internal/record/combination` | combine two searches with op | takes `{left, right, op}` |
| `/marcas/search/internal/result` | POST `{searchId, pageSize, pageNumber, filters, sort}` — fetch paginated results | requires prior searchId from `/record` POST |
| `/marcas/search/internal/result/count` | POST query — returns count without fetching results | needs same opaque query shape |
| `/marcas/search/internal/records` | GET — list active searches | |
| `/marcas/search/internal/extract` | GET — extract a single record by id | params `p=` (rightId), `s=` (sessionId), `o=` (annotation) |
| `/marcas/search/internal/extract/bulk` | POST — bulk extract | |
| `/marcas/search/internal/image/upload/bulk` | POST — image search input | reverse image search; trademark imagery via tmv.io CDN |
| `/marcas/search/internal/view/` | GET — record view | |

**Probe results (2026-05-18):**
1. `GET /marcas/search/quick` → 200, returns the Vue.js SPA HTML
   shell. The path is a Vue Router *client-side* route, not the API.
2. `POST /marcas/search/quick` (with session + XSRF) → **200, but
   returns SPA HTML** — the Spring backend treats anything not
   under `/marcas/search/internal/` as an SPA route.
3. `GET /marcas/search/internal/counts` (with session) → **200,
   JSON** `{"records": 0, "extracts": 0}`. Confirms the JSON API
   is reachable.
4. `POST /marcas/search/internal/result/count` with payload
   `{"trademarkText":"NIKE"}` → **500**. The accepted payload
   shape is opaque without further bundle extraction.
5. `POST /marcas/search/internal/result/count` with structured
   payload (`{query:{title, classes, codes, ...}, images:[]}`) →
   **500**. Schema is more nuanced than the SPA's `defaultQuery()`
   alone reveals.
6. `GET /marcas/search/internal/extract?p=RM202401000000&s=test`
   → **500** (no session-registered search to extract from).

**The MARCia API is reachable from our egress, accepts JSON, and
returns JSON.** It's the closest IMPI gets to a green-undocumented
surface. The blockers are: (a) opaque payload schema requiring
deep bundle extraction and live-call replay; (b) Spring-managed
session state with XSRF tokens; (c) no rate-limit headers, no
published ToS, no canonical documentation; (d) **everything else
on `*.impi.gob.mx` is unreachable**, so this is at most 25% of
the IP-office surface area.

### 1.3 datos.gob.mx — Mexico's federal open-data portal

| Field | Value |
|---|---|
| Endpoint | [`www.datos.gob.mx/organization/?q=impi`](https://www.datos.gob.mx/organization/?q=impi) |
| Auth | none |
| Format | HTML index pages; CSV + XML at the dataset link layer (per third-party search results — datasets in CSV/XML formats) |
| Reachable from US? | ✅ (Akamai-fronted nginx) |
| Rating | 🔴 **Red** — federal open-data portal hosts IMPI's *statistical* datasets ("Información estadística de invenciones, signos distintivos y protección a la propiedad intelectual"), not register-level data. The full register lives on the unreachable `datosabiertos.impi.gob.mx`. |

The federal portal is reachable but exposes only IMPI's
aggregated statistics dataset (per the [historico.datos.gob.mx
listing](https://historico.datos.gob.mx/busca/dataset/informacion-estadistica-de-invenciones-signos-distintivos-y-proteccion-a-la-propiedad-intelectu)),
not the full register. The full register data lives behind the
geo-blocked `datosabiertos.impi.gob.mx` SharePoint portal.

### 1.4 dof.gob.mx — Diario Oficial de la Federación (substantive law)

| Field | Value |
|---|---|
| Endpoint | [`www.dof.gob.mx/`](https://www.dof.gob.mx/) |
| Auth | none |
| Format | HTML (server: Apache PHP); per-note `nota_detalle.php?codigo=N&fecha=DD/MM/YYYY` |
| Reachable from US? | ✅ (responds 200, sets `DOF_WEB` session cookie) |
| Rating | 🟡 **Yellow informational** — the authoritative substantive-law publication for Mexico, including IMPI fee schedule updates, the LFPPI publication (codigo=5596010, 2020-07-01), and ongoing reform notices |

DOF is the canonical primary source for Mexican federal law and
the publication of record for IMPI fee-schedule updates. Not a
patent-register surface, but the right citation target for
substantive law and fee references.

### 1.5 Diputados — Mexican substantive law

| Endpoint | [`www.diputados.gob.mx/LeyesBiblio/ref/lfppi.htm`](https://www.diputados.gob.mx/LeyesBiblio/ref/lfppi.htm) |
|---|---|
| Auth | none |
| Reachable | ✅ (nginx 200) |
| Rating | 🟡 informational — canonical statutory references |

The Mexican Chamber of Deputies hosts the canonical consolidated
version of the **Ley Federal de Protección a la Propiedad
Industrial (LFPPI)**, [published in the DOF on 2020-07-01, in
force from 2021-11-05](https://www.dof.gob.mx/nota_detalle.php?codigo=5596010&fecha=01%2F07%2F2020).
The LFPPI replaced the 1991 *Ley de la Propiedad Industrial* and
harmonized Mexican substantive law with [USMCA Chapter 20 IP
commitments](https://ustr.gov/trade-agreements/free-trade-agreements/united-states-mexico-canada-agreement/agreement-between).
PDF text and reform history are at
[`diputados.gob.mx/LeyesBiblio/ref/lfppi.htm`](https://www.diputados.gob.mx/LeyesBiblio/ref/lfppi.htm)
and the IMPI-hosted version (also blocked from US egress) at
[`gob.mx/impi/documentos/ley-federal-de-proteccion-a-la-propiedad-industrial-274304`](https://www.gob.mx/impi/documentos/ley-federal-de-proteccion-a-la-propiedad-industrial-274304).

### 1.6 WIPO IP API Catalog — IMPI not listed

| Endpoint | [`https://apicatalog.wipo.int/`](https://apicatalog.wipo.int/) |
|---|---|
| Backing API | `https://apicatalog.wipo.int/api/apis?start=0&size=500` |
| IMPI / MX result | **0 entries** as of 2026-05-18 — full result inventory by org: DPMA (1), EPO (6), EUIPO (10), IP Australia (5), JPO (40), MOIP KOREA (90), QAZ (1), UPRP (3), USPTO (19), WIPO (4); 179 total across 10 IPOs |
| Rating | informational — confirms IMPI does not publish any cataloged API in WIPO's canonical inventory |

The 10 IPOs WIPO indexes do not include IMPI. By contrast, the
neighbouring Latin American absences from the WIPO catalog (INPI
Brazil, INAPI Chile, SIC Colombia, INDAUTOR/INDECOPI Peru,
DNDA/INPI Argentina) confirm a Latin America-wide pattern: only
QAZ (Kazakhstan, Latin-American in name but Asia in geography)
appears outside the EU + AU + JP + KR + US core.

### 1.7 EPO INPADOC + Google Patents — transitive coverage

| Surface | Coverage of MX |
|---|---|
| EPO INPADOC | MX granted patents are part of INPADOC's worldwide legal-status coverage per [Espacenet INPADOC help](https://worldwide.espacenet.com/help?locale=en_ep&method=handleHelpTopic&topic=legalstatusqh) and the [IFI CLAIMS legal-status reference](https://www.ificlaims.com/docs/legal-status.htm). Coverage depth: biblio + family + legal events at INPADOC's lag (typically 4-12 weeks). |
| Google Patents | MX patents and TMs flow into Google Patents' worldwide index (no formal partnership; web crawl of `siga.impi.gob.mx` historical snapshots + WIPO Patentscope re-ingestion) |
| Patentscope (WIPO) | MX is a [PCT contracting state since 1995-01-01](https://www.wipo.int/pct/en/pct_contracting_states.html); PCT national-phase entries from MX appear, but pure-national MX filings (estimated 21,265/year per [IMPI 2025 stats](https://www.gob.mx/impi/prensa/presenta-impi-en-2025-record-historico-en-patentes-concedidas-a-mexicanos-y-registra-aumento-en-registros-marcarios)) are not necessarily in Patentscope unless WIPO ingests bulk from IMPI. |

**Practical coverage assessment.** For an MX patent of commercial
scale (granted, family-claiming), EPO INPADOC covers it. For an
MX national-only utility model or industrial design, INPADOC
coverage is thinner; Google Patents fills some of it. The
national-only file history, prosecution events, oppositions,
declarations of nullity, and fee-status updates are not on any
external surface — only on the (unreachable) IMPI register.

## 2. Authentication architecture

There is no documented authentication architecture. The MARCia
backend uses anonymous Spring Boot session cookies (JSESSIONID +
HS512-signed SESSIONTOKEN JWT + XSRF-TOKEN), which a connector
can replicate by GETting `/marcas/search` to mint a session, then
threading the cookies + XSRF header on every POST. There is no
API key, no OAuth, no signup form. PASE
(`pase.impi.gob.mx/api/guide/getGuide` per a web-search hit) is
the electronic prosecution portal and likely requires a [FIEL
(Firma Electrónica Avanzada) certificate](https://www.gob.mx/sat/acciones-y-programas/firma-electronica-fiel)
issued by SAT (the Mexican tax authority) to Mexican
nationals/residents only — a structural foreign-developer block
similar to CN/CNIPA's CN-mobile signup requirement. Empirical
confirmation impossible without MX egress.

## 3. License and terms of service

There is no published API terms of service for any IMPI surface.
The federal open-data portal at
[`datos.gob.mx/libre-uso-mx`](https://datos.gob.mx/libre-uso-mx)
publishes a "Libre Uso MX" license that is permissive (commercial
+ non-commercial reuse with attribution), and this license
nominally covers IMPI datasets indexed on the federal portal. But
the in-scope datasets there are *aggregated statistics*, not
register data — the register data lives on the unreachable
`datosabiertos.impi.gob.mx`, where the applicable Aviso legal /
Términos y condiciones is unverifiable from US egress.

Mexico's federal *Ley General de Transparencia y Acceso a la
Información Pública* (LGTAIP, [published in DOF
2015-05-04](https://www.dof.gob.mx/nota_detalle.php?codigo=5391143&fecha=04%2F05%2F2015))
provides general statutory cover for register-data reuse, but
unlike EU/Spain's PSI Directive transposition, there is no
specific Mexican open-government-data act applying to IP register
data by default. Each agency publishes its own Plan Anual de
Apertura, and IMPI's plan is on the (unreachable)
`datosabiertos.impi.gob.mx`.

## 4. Substantive law

Mexico's substantive IP framework is:

- **Ley Federal de Protección a la Propiedad Industrial (LFPPI)** —
  [DOF 2020-07-01, in force 2021-11-05](https://www.dof.gob.mx/nota_detalle.php?codigo=5596010&fecha=01%2F07%2F2020),
  consolidated at [diputados.gob.mx](https://www.diputados.gob.mx/LeyesBiblio/ref/lfppi.htm).
  Covers patents, utility models, industrial designs, integrated-
  circuit layouts, trademarks, distinctive signs, denominations
  of origin (DO), geographic indications (GI), and trade secrets.
- **Ley Federal del Derecho de Autor** — separate copyright statute,
  administered by [INDAUTOR](https://www.indautor.gob.mx/) (not
  IMPI).
- **Ley Federal de Variedades Vegetales** — plant varieties,
  administered by [SNICS-SADER](https://www.gob.mx/snics) (not
  IMPI).
- **Reglamento de la LFPPI** — implementing regulations.

USMCA Chapter 20 (IP) is the international harmonization driver
but does not create a data-sharing arrangement between USPTO and
IMPI beyond ongoing [USPTO-IMPI cooperation programs
(uspto.gov)](https://www.uspto.gov/learning-and-resources/pursuing-international-ip-protection/mexico)
and a Patent Prosecution Highway pilot.

## 5. Fees

Out of scope for the wave file (link-only policy enforced in the
synopsis §4). IMPI's fee schedule is in MXN (Mexican peso) and
published in the DOF annually via the *Acuerdo* on tarifas — most
recently per the Diario Oficial publication track.

## 6. Cross-jurisdiction context

- **WIPO Madrid Protocol designating MX:** Mexico [acceded
  effective 2013-02-19 (WIPO Madrid news, 2025 update)](https://www.wipo.int/en/web/madrid-system/w/news/2025/madrid-system-mexico-now-providing-trademark-registration-certificates).
  Madrid IRs designating MX flow through WIPO Madrid Monitor
  (transitively covered).
- **Hague System (industrial designs):** Mexico [acceded
  effective 2020-06-06](https://www.wipo.int/hague/en/members/). Hague
  IRs designating MX flow through Hague Express (transitively
  covered).
- **PCT:** [Mexico is a contracting state since 1995-01-01](https://www.wipo.int/pct/en/pct_contracting_states.html);
  PCT national-phase entries appear in INPADOC.
- **Patent Prosecution Highway:** [USPTO-IMPI PPH pilot](https://www.uspto.gov/patents/basics/international-protection/patent-prosecution-highway/patent-prosecution-3)
  — accelerated examination using USPTO work products. Useful
  context for prosecution timeline modeling; not a data surface.
- **EPO-IMPI strategic cooperation:** Per [Uhthoff (Mexico law
  firm) summary](https://uhthoff.com.mx/en/mexican-institute-of-industrial-property-impi-and-european-patent-office-epo-strategic-cooperation-enhancing-patent-prosecution-strategies-in-mexico-in-terms-of-pharmaceutical-patents/),
  IMPI and EPO have a cooperation MOU for pharma-patent
  prosecution. Useful for INPADOC currency expectations.

## 7. Comparison to wave peers

| Office | Verdict | Why |
|---|---|---|
| SE/PRV | 🟢 green | Modern hosts, undocumented JSON, CC0/CC BY 4.0, reachable globally |
| FI/PRH | 🟢 green | Same shape as PRV — undocumented JSON, reachable, permissive license |
| ES/OEPM | 🟡 yellow_byok | Documented SOAP, per-applicant free credentials, permissive Aviso legal |
| IT/UIBM | 🟡 yellow_byok | Limited API + BYOK pattern |
| NL/RVO | 🔴 red | Struts2 only, no API |
| AT/ÖPA | 🔴 red | HTML only + personal-use Impressum |
| CH/IPI | 🔴 red | Limited surfaces |
| NZ/IPONZ | 🔴 red | HTML only |
| **MX/IMPI** | **🔴 red** | **Infrastructure-level geo-block on most subdomains; no documented API; not in WIPO catalog** |

IMPI is the *only* office in the wave where the blocker is at the
infrastructure layer rather than the ToS or auth layer. Even
CN/CNIPA's structural foreign-developer block is account-layer
(signup requires CN mobile), not network-layer (the servers
respond to non-CN egress).

## 8. What would unblock this

Three theoretical paths, none viable under the zero-infra constraint:

1. **Mexican-IP egress proxy** — rent a Mexican datacenter or
   residential exit node (Telmex / TotalPlay / Megacable) and route
   IMPI traffic through it. Violates the zero-infra constraint;
   also introduces a paid intermediary; also vulnerable to IMPI
   recognizing and blocking residential-proxy ranges.
2. **Mexico-hosted cooperation partner** — a Mexican IP firm with
   register access who wraps IMPI surfaces as a paid API. Several
   exist commercially (`mxmarks.com`, `bonamark.com`,
   `marcaria.com`); wrapping them violates the upstream-guarantee
   norm and adds a paid intermediary.
3. **IMPI publishes a proper API** — IMPI's "paperless and
   e-office" trajectory (per [Lexology 2020 article on IMPI
   becoming paperless](https://www.lexology.com/library/detail.aspx?g=2fb8e12b-f0a6-44e0-836b-960191f8197d))
   suggests this is in IMPI's long-term roadmap, but no public
   timeline. Worth monitoring [gob.mx/impi/prensa](https://www.gob.mx/impi/prensa)
   announcements quarterly.

## 9. Recommendation

**Skip the connector.** Coverage of MX flows through:
- **EPO INPADOC** (via `patent_client_agents.epo_ops`) — granted MX
  patents at biblio + family + legal-events fidelity.
- **Google Patents** (via `patent_client_agents.google_patents`) — MX
  patents and TMs that the crawl picks up.
- **WIPO Madrid Monitor / Hague Express** (transitively via planned
  WIPO connectors) — Madrid IRs designating MX, Hague IRs
  designating MX.
- **PCT (Patentscope, transitively via EPO OPS)** — PCT national-
  phase entries into MX.

Document the gap explicitly: **MX national-only file histories,
electronic prosecution events, the Gaceta, opposition / nullity
proceedings, and the open-data register catalog are not covered
and cannot be covered without Mexican egress**. This is a
structural exclusion, not a "haven't gotten to it yet" exclusion.

If the unblocking path ever opens (IMPI publishes an API; or a
non-paid MX cooperation arrangement materializes), reopen this
file; the MARCia JSON layer is the connector starting point.

## 10. Open questions

- **Cloud Run / Cloudflare Workers egress test** — empirically
  confirm the geo-block surface from production-style egress (the
  curl from this analysis was from a US residential IP). The
  block is likely identical or stricter.
- **MARCia data currency** — third parties say "daily indexing"
  but the SPA bundle's `lastIndexingDate: '02 Feb 2020'` deserves
  empirical confirmation by registering a search via the JSON API
  (after extracting the payload schema from the bundle) and
  checking whether RM2025xxxxxxx-level records return.
- **PASE FIEL requirement** — unverified that PASE requires a SAT-
  issued FIEL certificate; this is the consistent practice for
  Mexican gov electronic services but the public PASE landing
  page (unreachable from US) would be the canonical answer.
- **Madrid IR ingestion in MARCia** — if MARCia surfaces both
  national and Madrid IRs (likely, given IMPI is the receiving
  office for Madrid in MX), the discriminator field is unknown.
- **Patentscope MX coverage depth** — whether WIPO ingests bulk
  MX patent data into Patentscope, or only via PCT national-phase
  entries. INPADOC is the more reliable transitive layer.
- **IMPI WIPO ST.36 / ST.66 / ST.86 compliance** — whether
  IMPI's bulk distributions on `datosabiertos.impi.gob.mx` ship
  in WIPO-standard XML (as OEPM does) or proprietary formats.
  Unverifiable from US egress.
- **`pase.impi.gob.mx/api/guide/getGuide`** — the only `api`-
  pathed IMPI URL that surfaces in third-party web search. Likely
  a published-help endpoint, not a substantive data API.
- **acervomarcas Marcanet legacy** — port 8181 servlet,
  unreachable. Even if reachable, third parties confirm 15-30 day
  data lag and MARCia is the canonical replacement.
