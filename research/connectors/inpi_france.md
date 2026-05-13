# INPI France — Connector Survey

Survey of French IP data sources for `patent-client-agents`. Status: 2026-05.

France is a paradox for an IP connector: most "French patents" are EP-routed and
already visible through `epo_ops`, most French trademarks are EUTM-routed (we
get them through the planned `euipo_trademarks`), and most French designs are
RCDs. But the **INPI Data portal (`data.inpi.fr`)** is a real bulk-data asset
backed by French open-data law, plus France ships an unusually clean public
case-law stack (Judilibre + Légifrance via PISTE). The marginal value over
EPO+EUIPO sits in three places: (1) FR-only national filings (utility
certificates, FR-only patents, national TMs/designs), (2) primary-law access
to the **Code de la propriété intellectuelle (CPI)**, (3) **Tribunal
judiciaire de Paris 3e chambre** decisions for IP litigation intelligence.

## Cross-asset matrix

| # | Asset | Auth | Format | Freshness | License | Python? |
|---|---|---|---|---|---|---|
| 1 | **data.inpi.fr** portal (search UI) | Registration | HTML | Live | Etalab-style | n/a |
| 2 | **API PI Brevets** (FR/EP patents) | Account + user/pass via "Mes accès API/SFTP" | XML/JSON/PDF (notice, image, search) | Weekly (Fri) | INPI reuse licence (approved Etalab variant) | None tracked |
| 3 | **API PI Marques** (TM) | Same | XML/JSON, BOPI bulletin, search, image | Weekly (Fri) | Same | None tracked |
| 4 | **API PI Dessins & Modèles** | Same | XML per WIPO **ST.86 v1.0** + image | Bi-monthly | Same | None tracked |
| 5 | **INPI FTP/SFTP** (PI bulk) | Form request → creds | Weekly/stock ZIPs (XML+images); annual stock | Weekly + ≥1×/yr stock | Same | None tracked |
| 6 | **API RNE** (ex-RNCS — businesses) | Account creds | JSON / PDF (actes, bilans since 1993/2017) | **Daily** | Same | `etalab/rncs_worker_api_entreprise` (legacy RNCS), `pappers_api` (3rd-party paid) |
| 7 | **INPI jurisprudence DB** (PIBD) | None (public) | HTML; migrating into data.inpi.fr "summer" | 15-day cadence | INPI reuse licence | None tracked |
| 8 | **INPI Directives** (examen brevets/marques/D&M) | None | PDF | Ad-hoc (last bumps Jan/Apr 2026) | Open access | None |
| 9 | **Légifrance API** (CPI, Code commerce L.151) | PISTE OAuth2 client_credentials | JSON | Live | Open Licence 2.0 | **`pylegifrance`** (Pydantic), `legipy` (CLI), `dila-api-client` |
| 10 | **Judilibre API** (Cass + CA + TJ civil) | PISTE OAuth2 client_credentials | JSON | Live, with `/transactionalhistory` delta feed | Open Licence 2.0 | Same `dila-api-client`-family |
| 11 | **INAO** (FR GIs — wine/spirits/agri) | None | HTML / PDF / shapefiles | Annual | Etalab | None tracked |

PISTE is the **single OAuth2 broker** for both Légifrance and Judilibre — one
client implementation lights up both.

## Asset notes

### 1–5: `data.inpi.fr` and the INPI APIs

The INPI Data portal is a **real bulk channel**, not a polite-scrape situation.
WIPO INSPIRE catalogs it as a first-class patent database. Access pattern:

- Free registration → "Mes accès API / SFTP" panel → accept the INPI reuse
  licence → receive technical credentials (basic auth user/pass, not OAuth).
- **Quota**: 10,000 requests/day and 10 GB/day per technical account
  (documented).
- **Formats**: XML / JSON / CSV / PDF over HTTPS; ZIP+XML over FTP/SFTP.
- **Coverage**:
  - Patents: FR + EP designations + PCT national phase + CCPs. Notice in XML;
    search endpoint; "image" (face page + claims/description) endpoint.
  - Trademarks: FR + EUTM + International (Madrid) designations of FR;
    BOPI weekly bulletin as bulk artifact.
  - Designs & Models: WIPO **ST.86 v1.0** XML — same standard used by EUIPO RCD
    bulk, so a shared parser amortizes.
- **Updates**: weekly Friday for patents & TMs; bi-monthly for D&M; daily for
  RNE (companies).
- **Stock vs. flow**: an annual full stock (a.k.a. "backlog") is published at
  least once per year via SFTP for D&M (confirmed) — same shape as for
  patents/TMs. Pattern matches USPTO bulk + EUIPO Open Data.

This is comparable in seriousness to **EUIPO Open Data**, slightly behind
**USPTO bulk** (which is genuinely open without registration), but ahead of
**DPMA backfile** (which is paid and contractual). The Pydantic-friendly JSON
option is what separates it from the older ST.36-only feeds.

### 6: RNE (ex-RNCS)

The Registre National des Entreprises replaced the RNCS on **2023-01-01**
(PACTE law). Daily JSON+PDF feed of all French legal entities, including
"actes" and "bilans" since 1993/2017. **Useful for assignee normalization** —
turning "Société Générale" / "SG" / "Banque SG" into a canonical SIREN. Also
the foundation of the popular commercial `pappers_api` (free tier: 10k
companies + 1k documents/month). The 2026 decree adds a CSRD-OTI reporting
field; minor schema change.

For our purposes RNE is an **adjacency** rather than a core IP asset: it
unlocks accurate assignee resolution, but only on the French side.

### 7: PIBD jurisprudence

Free, public, no auth. Covers FR national judicial decisions on patents (1823;
full text 1997+), trademarks (1904; full text 1997+), designs (1994+), GIs;
plus INPI Director General decisions on TM oppositions (2004+), nullity/
revocation (2020+), patent oppositions (2020+). The site explicitly announced
migration into `data.inpi.fr` "later in the summer" of 2026 under a new
interface — **timing-sensitive scraper risk**. Recommend waiting for the
migration.

### 8: INPI Directives

Three separate PDF manuals — Patents (Apr 2022), Trademark opposition
(Jan 2026), Designs registration (Jan 2026), plus a Patent post-grant
procedures volume (Apr 2025). Plain PDF, no auth, perfect fit for the
`StaticLawCorpus` base. Cheap, but in French only — agent value depends on the
caller speaking French or accepting MT.

### 9–10: Légifrance + Judilibre (PISTE)

This is the **clean** part of the French stack:

- **PISTE** = `piste.gouv.fr`, the DILA's API gateway. **OAuth2
  client_credentials**, free after registration. Same KeyId works for
  Légifrance and Judilibre.
- **Légifrance**: full-text REST search over the Codes (incl. **CPI**
  LEGITEXT000006069414 covering copyright L.111-1+, patents L.611-1+, TMs
  L.711-1+, designs L.511-1+, GIs L.722-1+), and the **Code de commerce
  L.151-1 to L.154-1** (trade secrets — note: trade secrets are in
  Code de commerce, NOT in CPI; Law 2018-670 transposed EU Dir 2016/943
  there). Stable since 2023-04-04.
- **Judilibre**: Cour de cassation since 2021, CA civil/social/commercial
  (incl. **Cour d'appel de Paris pôle 5 ch. 1/2** — the IP appellate
  division) since March 2022, lower courts on civil/commercial since
  **2024-12-31** (newly available — covers **Tribunal judiciaire de Paris
  3e chambre**, the exclusive-national-jurisdiction IP trial chamber).
  Has a `/transactionalhistory` delta endpoint — meaningfully better than
  USPTO/CourtListener polling.

**Python competitors exist**: `pylegifrance` (Pydantic, alpha), `legipy`,
`dila-api-client`. None are async-first or aimed at agent use; clean
green-field opportunity to wrap PISTE properly once for both APIs.

### 11: INAO + EU GI transfer

INAO (Institut national de l'origine et de la qualité) keeps the FR GI list
(AOP/AOC/IGP) but **no real API** — HTML product search, shapefiles, annual
PDFs. Per **Reg. 2024/1143** (in force 2024-05-13), artisanal/industrial IGPs
are now exclusively EUIPO-managed (covered by EUIPO GIview, in our planned
`euipo_*` stack); agricultural/wine/spirits GIs stay with the European
Commission. This means INAO scraping is **strictly lower-value than the
EUIPO + EC route** for cross-border use cases; only a domestic FR analysis
needs INAO-specific data (e.g., delimitation maps).

## Compare with what we already have

| Dimension | INPI France | DPMA (Tier 2) | EUIPO (Tier 1) | USPTO ODP |
|---|---|---|---|---|
| Free public API | **Yes** (registered) | **No** (DPMAconnect+ is €200 paid) | Yes (OAuth) | Yes (key) |
| Bulk feed | XML/JSON via SFTP + APIs, weekly | Paid only | Open Data Platform daily XML | Public bulk |
| TM coverage | FR + EUTM-FR + Madrid-FR | DE + EUTM-DE | All EUTM | n/a |
| Design standard | **ST.86 v1.0** XML | Not exposed | ST.86 / OD | n/a |
| Court data | Judilibre (Cass + CA + TJ civil from 2024) | rechtsprechung-im-internet + Zenodo BPatG | EUIPO eSearch (no API) + CELLAR | CAFC/CourtListener (own modules) |
| Statutory law | PISTE → CPI + Code commerce L.151 | gesetze-im-internet.de | EUR-Lex CELLAR | govinfo / legal_statutes |
| Utility-rights gap vs. EPO | **Certificats d'utilité** exist but small (~hundreds/yr) | **Gebrauchsmuster** large (~10k+/yr) | n/a | n/a |
| Filing-language barrier | French only | German only | EN available | EN |

**Does INPI France add value beyond EPO + EUIPO for FR rights?**

- **Patents**: marginal. EPO OPS already covers FR-published applications (via
  national-route equivalents) and all EP designations. The genuine increment
  is (a) **certificats d'utilité** (FR utility certificate — small volume,
  unlike German Gebrauchsmuster), (b) FR-only legal-status events not in
  INPADOC, (c) primary INPI register opposition decisions (from 2020+).
- **Trademarks**: small. National FR TM register only — EUTMs are EUIPO. But
  ~190k FR national TMs are active and not in EUIPO. Worth wrapping if
  shipping a "complete EU TM clearance" agent.
- **Designs**: small same as TMs — FR national designs only; ~99% of
  cross-border designs are RCDs.
- **Case law**: **large**. TJ Paris 3e chambre is *the* French IP trial court,
  exclusive national jurisdiction for patents/EUTMs/designs/GIs. Judilibre
  unlocks it cleanly. This is the **highest-leverage piece** of the FR stack.
- **Statutes**: **large**. CPI + Code de commerce L.151 via PISTE is the only
  authoritative path to FR primary law; gives FR coverage for the
  `StaticLawCorpus` base with no scraping.

## v1 scope (recommended build order, by leverage)

1. **`piste_dila`** — shared PISTE OAuth2 client_credentials adapter,
   `OAuth2ClientCredentialsClient` base extended (already on the roadmap
   for EUIPO + IP Australia). Powers both #2 and #3.
2. **`legifrance`** — CPI, Code de commerce L.151 (trade secrets), point-in-
   time versioning. Hooks into `StaticLawCorpus` shape so the agent can cite
   articles uniformly with MPEP/MoPP/LPI.
3. **`judilibre`** — Cour de cassation IP cases + Cour d'appel de Paris pôle
   5 + Tribunal judiciaire de Paris 3e chambre. Uses `/transactionalhistory`
   for incremental sync. Fits `StructuredCaseLawClient` base alongside Find
   Case Law (UK) and CELLAR (EU).
4. **`inpi_bulk`** — INPI SFTP for D&M ST.86 + patents/TM weekly XML. Reuse
   the WIPO-standards parser bundle. Skip the live JSON API in v1 — bulk
   covers the corpus and avoids per-call quota juggling.
5. **`inpi_directives`** — three PDF manuals into `StaticLawCorpus`. Half-day
   each.

**Defer to v2**: the INPI live PI APIs (#2–4). Bulk SFTP gives the corpus;
live API only matters for "what changed in the last week" use cases that the
weekly stock already answers.

## Skip list (do not build)

- **INPI API live PI (v1)** — bulk covers the corpus; live calls waste the
  10k/day quota and add a second auth path. Revisit if a near-real-time
  use case appears.
- **INPI jurisprudence DB scraping** — explicit migration to data.inpi.fr
  announced for summer 2026; scraper would be obsoleted in months. Wait.
- **RNE direct wrapper for IP work** — assignee normalization is the only
  IP-adjacent use; the third-party `pappers_api` already covers it. If we
  ever need first-party, wrap then.
- **INAO scraping** — Reg. 2024/1143 moved industrial/artisanal GIs to EUIPO;
  agri/wine GIs go via EC eAmbrosia. No standalone INAO data is more
  authoritative than the EUIPO/EC route except delimitation shapefiles, which
  are out of scope for patent agents.
- **Court d'appel de Paris pre-2022 IP appeals** — Judilibre starts at
  2022-03; for older decisions, fall back to Légifrance "jurisprudence
  judiciaire" segment (still PISTE).

## Open questions

1. **INPI reuse licence ≠ Etalab 2.0 verbatim.** The INPI reuse licence is
   "approved Etalab variant" but has its own text. Confirm it permits
   CoWork cache-and-serve (the recurring license question on
   ServiceKey-style auth).
2. **INPI API quota semantics.** 10k requests + 10 GB/day — per-account or
   per-key? Is the SFTP bulk on the same quota?
3. **PISTE rate limits.** Documented limits for Légifrance/Judilibre per
   sandbox/prod KeyId — search hits don't pin numbers; need to register a
   sandbox app or check Swagger.
4. **Judilibre TJ Paris coverage depth.** "Lower courts civil since
   2024-12-31" — how much of TJ Paris 3e chambre is *retrospectively*
   indexed? If only forward-looking, the 1823-2024 patent decisions remain
   PIBD-only until the migration completes.
5. **PIBD migration target schema.** Will the post-migration data.inpi.fr
   jurisprudence module expose an API/JSON, or only an HTML interface?
6. **INPI D&M ST.86 dialect.** Confirm INPI's ST.86 matches EUIPO's exactly
   so the parser is reusable verbatim (vs. variant fields).
7. **Certificats d'utilité (FR utility certificate) coverage in EPO OPS.**
   Are they exposed via INPADOC legal-status or do we need INPI? Empirical
   test needed.
8. **Language strategy.** All INPI directives and most PIBD case law are
   French-only. Bundle MT, surface raw FR + EN abstract, or accept FR-only?

## Summary verdict

The headline is **the French stack is roughly DPMA-quality data on EUIPO-
quality infrastructure**: a real bulk channel, a clean OAuth gateway shared
across two APIs (PISTE), and free-after-registration access — better access
hygiene than DPMA, comparable freshness to USPTO bulk, but with a smaller
incremental corpus once EPO + EUIPO are already covered. The two compelling
modules are **`judilibre` (TJ Paris + CA Paris + Cass for IP)** and
**`legifrance` (CPI + Code commerce L.151)**, both riding on a single PISTE
OAuth client — these turn France from "covered by EPO + EUIPO" into "covered
end-to-end including primary law and litigation intelligence."

Sources:
- [Accueil - Data INPI](https://data.inpi.fr/)
- [Accès aux API - Propriété industrielle](https://data.inpi.fr/content/editorial/apis_pi)
- [Accès aux API et FTP | INPI](https://www.inpi.fr/ressources/propriete-intellectuelle/acces-aux-api-et-ftp)
- [INPI API PI technical doc PDF](https://www.inpi.fr/sites/default/files/Inpi_doc_tech_API_PI_v1.0_0.pdf)
- [Catalogue API publiques - api.gouv.fr](https://api.gouv.fr/producteurs/inpi)
- [DATA INPI Portal — WIPO INSPIRE](https://inspire.wipo.int/data-inpi-portal-patent-database)
- [Doc tech Dessins & Modèles (ST.86)](https://www.inpi.fr/sites/default/files/doctech_dmfr_v1_3_.pdf)
- [Licences de réutilisation des données de l'INPI](https://data.inpi.fr/content/editorial/licences_reutilisation_donnees_inpi)
- [Etalab Open Licence 2.0 (SPDX)](https://spdx.org/licenses/etalab-2.0.html)
- [Accès au serveur SFTP - Entreprises](https://data.inpi.fr/content/editorial/Serveur_ftp_entreprises)
- [Registre national des entreprises (RNE) | INPI](https://www.inpi.fr/ressources/formalites-dentreprises/registre-national-entreprises)
- [API Entreprise — RNE actes et bilans](https://entreprise.api.gouv.fr/catalogue/inpi/rne/actes_bilans)
- [PIBD | INPI](https://pibd.inpi.fr/)
- [Base de jurisprudence en propriété industrielle](https://www.inpi.fr/ressources/propriete-intellectuelle/consulter-base-de-jurisprudence-en-propriete-industrielle)
- [Directives | INPI](https://www.inpi.fr/directives)
- [Code de la propriété intellectuelle - Légifrance](https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069414/)
- [Open data et API - Légifrance](https://www.legifrance.gouv.fr/contenu/pied-de-page/open-data-et-api)
- [API Légifrance — data.gouv.fr](https://www.data.gouv.fr/dataservices/legifrance)
- [PISTE — DILA registration](https://piste.gouv.fr/registration)
- [pylegifrance](https://pylegifrance.github.io/pylegifrance/)
- [judilibre-search (Cour de cassation)](https://github.com/Cour-de-cassation/judilibre-search)
- [Données ouvertes et API — Judilibre](https://www.courdecassation.fr/acces-rapide-judilibre/donnees-ouvertes-open-data-et-api)
- [3e chambre — Propriété intellectuelle — TJ Paris](https://www.tribunal-de-paris.justice.fr/75/3rd-chamber-intellectual-property)
- [Code de commerce L.151-1 à L.154-1 (secret des affaires)](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000005634379/LEGISCTA000037266547/)
- [Loi 2018-670 du 30 juillet 2018 — secret des affaires](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000037262111)
- [INAO — Geographical data](https://www.inao.gouv.fr/en/geographic-data)
- [Pappers API documentation](https://www.pappers.fr/api/documentation)
