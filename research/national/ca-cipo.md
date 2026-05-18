# CIPO Canada (CA) — national

**Layer:** national
**Jurisdiction:** CA (WIPO ST.3: CA)
**Issuing body:** Canadian Intellectual Property Office (an agency of Innovation, Science and Economic Development Canada — ISED)
**Rights administered:** patent, trademark, industrial_design, copyright (registers), trade_secret (statute-only, common law)
**Working languages:** English + French (bilingual)
**Connector status:** **skipped for live registers** (zero REST APIs across all rights); CanLII covers case law
**Last verified:** 2026-05-16
**Manifest entry:** [`coverage/sources.yaml` `CA/CanLII`](../../coverage/sources.yaml) (CanLII cases — `patent_client_agents.canlii`)

**Detail surveys:**
- [`connectors/cipo.md`](../connectors/cipo.md) — 2026-05 detail survey (211 lines)
- [`waves/2026-05-16-registered-ip-discovery/cipo-canada.md`](../waves/2026-05-16-registered-ip-discovery/cipo-canada.md) — 2026-05-16 grounded discovery (zero REST APIs)

**Higher layers covering this office transitively:**
- **EPO INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — CA patent biblio + family
- **WIPO Madrid** — international TMs designating CA (Canada acceded 2019-06-17, post-Madrid 1989)
- **WIPO Hague** — international designs designating CA (Canada acceded 2018-11-05)
- **CanLII** — Canadian IP case law (Federal Court / FCA / Supreme Court of Canada + TMOB + PAB)

---

## §1 Mission

CIPO is the Canadian IP office. Canada is in the IP5+ peripheral tier
— modest filing volumes by global standards, but a top-tier IP system
with sophisticated case law (the Federal Court is the primary IP venue;
the TMOB and Patent Appeal Board handle administrative tribunals). CIPO
is mid-modernization under the "Next Generation Patents" (NGP)
programme, but as of 2026-05-16, no programmatic search APIs exist for
any of the three registered rights.

For Canadian IP work, the recommended path is EPO INPADOC for patent
biblio/family + CanLII for case law and statutes. National-only TM and
design data has no proxyable substitute.

## §2 What's unique here
- **CA patent prosecution status** in real time (vs. INPADOC's lag)
- **CA file wrappers** (national-only direct filings)
- **National-only CA trademarks** (pre-Madrid-accession 2019; post-accession non-Madrid filings)
- **National-only CA designs** (pre-Hague-accession 2018; post-accession non-Hague filings)
- **CIPO Patent Appeal Board (PAB) and Trademarks Opposition Board (TMOB) decisions** — covered transitively via CanLII; CIPO Decisia is the upstream source

## §3 Programmatic surfaces

### ISED API Catalogue

The entire Innovation, Science and Economic Development Canada (ISED)
department lists **three APIs total** across `api.ised-isde.canada.ca`.
The only CIPO entry is the TM Goods & Services Manual — a Nice-class
classification helper, **not a record search**.

| Field | Value |
|---|---|
| Endpoint | `api.ised-isde.canada.ca` |
| CIPO APIs available | TM Goods & Services Manual only |
| Verdict | 🔴 Red — no patent/TM/design search API exists |
| Primary source | [`waves/2026-05-16-registered-ip-discovery/cipo-canada.md`](../waves/2026-05-16-registered-ip-discovery/cipo-canada.md) |

### Canadian Patents Database (CPD) — HTML only

Public web search at `ised-isde.canada.ca/cipo/patent-search`. No REST.
Wayback / scraping is the only programmatic path and it's brittle.

| Field | Value |
|---|---|
| Endpoint | `ised-isde.canada.ca/cipo/patent-search` (HTML) |
| Auth | none |
| Format | HTML |
| Verdict | 🔴 Red |

### Canadian Trademarks Database — HTML + undocumented POST

The only "API" surface is an undocumented internal `/srch` POST endpoint
backing the HTML search UI. Subject to UI redesigns.

| Field | Value |
|---|---|
| Endpoint | `ised-isde.canada.ca/cipo/trademark-search` (HTML); undocumented internal `/srch` POST |
| Auth | none |
| Verdict | 🔴 Red — undocumented, unsupported, brittle |

### Industrial Designs Database — legacy JSP

Pure legacy JSP servlet (`bscSrch.do`). HTML-only.

| Field | Value |
|---|---|
| Verdict | 🔴 Red |

### IP Horizons bulk

Weekly ST.36 XML for patents, weekly TM XML+PNG, quarterly research CSV.
Open Government Licence — Canada (OGL). Bulk-shaped; doesn't fit our
zero-infra constraint but legally clean if we ever pivot to bulk
ingestion.

| Field | Value |
|---|---|
| Endpoint | CIPO IP Horizons bulk delivery |
| Auth | none |
| Format | ST.36 XML / TM XML+PNG / CSV |
| ToS | Open Government Licence — Canada |
| Verdict | 🔴 Red (bulk-shaped, not proxy-shaped) |

## §4 Fees

**Official schedule:** [CIPO — Fees (ised-isde.canada.ca)](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/fees)
**Statutory basis:** Patent Rules, Trademarks Regulations, Industrial Design Regulations (under the respective Acts)

Headline figures **pending dedicated fee research**. CIPO fees are in CAD.
Canada has entity-size tiers ("standard" vs. "small entity"; small entity
=≤50 employees + non-controlled by larger entity); fee reductions of
50% historically though specifics vary by category.

## §5 Connector strategy

### What we cover today

- [`patent_client_agents.canlii`](../../src/patent_client_agents/canlii/) (and via `tools/law-tools/`) — Canadian Federal Court / FCA / SCC IP rulings + TMOB + PAB decisions + Patent Act + Trademarks Act + provincial statutes; manifest entry `CA/CanLII`.
- CA patent biblio + family via [`patent_client_agents.epo_ops`](../regional/epo.md) (transitive).

### What we should NOT add (and why)

- **Live CIPO patent / TM / design register scrapers** — no stable surface; CIPO is mid-NGP migration; HTML subdomains have already migrated once (from `ic.gc.ca` to `ised-isde.canada.ca/cipo` in 2024). Scrapers will be moving targets.
- **Direct integration with the undocumented `/srch` POST** — unsupported and unsigned.

### What we *should* consider

- **`cipo_bulkdata`** — IP Horizons ST.36 weekly XML + TM XML+PNG + quarterly research CSV via Shape-E catalog connector. This is bulk, not proxy, but legally clean (Open Government Licence — Canada) and well-shaped. See [`BACKLOG.md`](../BACKLOG.md) Tier 2 Rank 3.
- **`cipo_manuals`** — MOPOP / TEM / IDOP single-HTML S3 mirrors via `StaticLawCorpus` pattern. Same shape as MPEP/TMEP. See BACKLOG Tier 2 Rank 4.

### Next steps

1. **Quarterly recheck** of [api.ised-isde.canada.ca](https://api.ised-isde.canada.ca/) for any new CIPO API additions to the catalog.
2. **Watch list:** CIPO NGP roadmap — public bibliographic REST API on the horizon, or staying ST.96-internal? Monitor CIPO WIPO CWS contributions.
3. **Substantive law / manuals expansion**: `cipo_manuals` is a clean next step regardless of register modernization — adds value, no register-modernization dependency.

## §6 Open questions

- **NGP API roadmap** — will CIPO ship a public REST search API as part of NGP, or stay with the bulk + HTML model? No published timeline.
- **CanLII redistribution ToS** — does CanLII permit caching detail JSON and re-exposing via our MCP tool? Confirm before scaling key usage. (Listed in BACKLOG Tier 1 open questions.)
- **TMOB / PAB Decisia coverage in CanLII** — does CanLII have full coverage, or are there gaps requiring Decisia fallback?

## §7 References

Primary sources only.

**ISED / CIPO landing:**
- [CIPO landing (ised-isde.canada.ca)](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en)
- [ISED API Catalogue](https://api.ised-isde.canada.ca/)

**Search UIs (HTML only):**
- [Canadian Patents Database](https://ised-isde.canada.ca/cipo/patent-search)
- [Canadian Trademarks Database](https://ised-isde.canada.ca/cipo/trademark-search)
- [Industrial Designs Database](https://www.ic.gc.ca/app/opic-cipo/dsgn/srch.do?lang=eng)

**Bulk + open data:**
- [CIPO IP Horizons bulk](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/open-data-and-statistics)
- [open.canada.ca — Open Government Licence](https://open.canada.ca/en/open-government-licence-canada)

**Fees:**
- [CIPO fees](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/fees)

**Case law:**
- [CanLII](https://www.canlii.org/) — case law + statutes
- [TMOB / PAB Decisia](https://decisia.lexum.com/cipo/decisions/en/nav.do) — upstream of CanLII

**Detail survey + wave:**
- [`connectors/cipo.md`](../connectors/cipo.md) — full 211-line detail survey
- [`waves/2026-05-16-registered-ip-discovery/cipo-canada.md`](../waves/2026-05-16-registered-ip-discovery/cipo-canada.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Reconciled the original "Tier 2 CanLII + bulk + manuals" framing — confirmed **zero REST search APIs across all three rights**; the only CIPO entry in the entire ISED API Catalogue is the TM Goods & Services Manual (classification helper, not record search). | [waves/2026-05-16-registered-ip-discovery/cipo-canada.md](../waves/2026-05-16-registered-ip-discovery/cipo-canada.md) |
