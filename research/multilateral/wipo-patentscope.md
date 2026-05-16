# WIPO PATENTSCOPE — multilateral

**Layer:** multilateral
**System:** Patent Cooperation Treaty (PCT) + national patent collections aggregated by WIPO
**Operator:** World Intellectual Property Organization (WIPO)
**Rights covered:** patent (and where applicable utility model)
**Coverage:** PCT international applications + national/regional collections from ~70 contributing offices
**Working languages:** English + WIPO official languages
**Connector status:** **skipped for live search** (ToS prohibits automated queries); future partner API monitored
**Last verified:** 2026-05-16
**Manifest entry:** not listed in `coverage/sources.yaml` for PATENTSCOPE specifically; PCT-related patents reachable transitively via EPO INPADOC

**Detail surveys:**
- [`connectors/wipo.md`](../connectors/wipo.md) — 2026-05 detail survey (150 lines)
- [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) — 2026-05-16 grounded discovery (all three WIPO public DBs)

**Higher / sibling layers carrying overlapping data:**
- **EPO INPADOC** — DOCDB carries biblio for ~100 offices including most major PATENTSCOPE contributors. For agents needing patent biblio, INPADOC is the recommended path.
- **National offices' direct registers** (where APIs exist) — USPTO ODP, EPO OPS, JPO, etc.

---

## §1 Mission

PATENTSCOPE is WIPO's flagship public patent search system, covering
PCT applications and a growing set of national collections through
bilateral contribution agreements. It's the closest thing to a unified
global patent database, with strong multilingual coverage and machine
translation. For agents wanting "search across all jurisdictions
without per-office plumbing," PATENTSCOPE is the conceptual fit.

The catch: WIPO's public-facing PATENTSCOPE is consumed via the web UI,
not via an API. The only programmatic surface is a paid bulk product
over SFTP, and the public web UI's ToS explicitly prohibits automated
queries.

## §2 What's unique here (not covered by higher layers)

- **PCT application data not yet entered into national phase** — PCT international applications are visible via PATENTSCOPE before they hit any national office's register.
- **WIPO's machine-translated abstracts** in WIPO-supported languages.
- **Cross-jurisdictional unified search UI** — one query across ~70 collections (this is the part WIPO won't let us proxy).

## §3 Programmatic surfaces

### Public PATENTSCOPE web UI

| Field | Value |
|---|---|
| Endpoint | `https://patentscope.wipo.int/search/en/` |
| Auth | none |
| Format | HTML |
| ToS posture | **§2.1 explicitly forbids automated queries.** >10 actions/min from a single IP flagged as excessive. |
| Verdict (zero-infra proxy) | 🔴 **Red** — ToS prohibits the access pattern |
| Primary sources | [PATENTSCOPE Terms of Use (Oct 2025)](https://patentscope.wipo.int/search/en/help/terms_conditions.jsf) — §2.1 prohibition; [PCT Data Products and Services](https://www.wipo.int/en/web/patentscope/data/index) |

### Paid PCT Data SFTP feed

| Field | Value |
|---|---|
| Endpoint | SFTP delivery (post-contract) |
| Auth | Account + paid contract |
| Format | XML (ST.36 + WIPO publication schemas) |
| Cost | **CHF 400 – 2,000 / year** per the PCT Data Products page; CHF 400 for the most basic weekly subset |
| ToS posture | Bulk redistribution explicitly addressed in contract; review required |
| Verdict | 🟡 Yellow — bulk-shaped (not live API), but cleanest WIPO data deal if budget exists |
| Primary source | [PCT Data Products and Services](https://www.wipo.int/en/web/patentscope/data/index) |

### Paid SOAP search API

| Field | Value |
|---|---|
| Endpoint | SOAP envelope (WSDL on request) |
| Auth | Account + paid contract |
| Cost | **~CHF 2,600 / year** |
| ToS posture | Search-style access; subject to ToS |
| Verdict | 🔴 Red — paid + SOAP + poor stack fit; SFTP bulk gives most of the data more cheaply |
| Primary source | [PCT Data Products and Services](https://www.wipo.int/en/web/patentscope/data/index) |

### Article 6ter Express API

| Field | Value |
|---|---|
| Endpoint | WIPO Article 6ter Express |
| Auth | none |
| Format | REST/JSON |
| Verdict | 🟢 Green for the narrow dataset it covers (state emblems / IGO marks) |
| Primary source | [WIPO Article 6ter Express](https://www.wipo.int/en/web/6ter) |

Note: Article 6ter is a small but clean dataset — not patent search. Useful
for trademark conflict analysis (state emblems can't be registered as
trademarks).

## §4 Fee schedule (PCT system, not PATENTSCOPE API access)

**Detail file:** *no fee-schedules/wipo-pct-fees.md yet — queued*
**Official PCT fee schedule:** [WIPO — PCT fees](https://www.wipo.int/en/web/pct-system/fees)
**Statutory basis:** PCT Regulations (Rule 96) + Schedule of Fees

PCT applications carry international fees (transmittal, search, examination,
international filing, supplementary search) plus national-phase entry
fees at each designated office. The international fees are paid at the
receiving Office (USPTO, EPO, JPO, KIPO, CNIPA, IB) and forwarded to
WIPO + the International Searching Authority.

PATENTSCOPE *access fees* (separate from PCT filing fees) are documented
on the [PCT Data Products page](https://www.wipo.int/en/web/patentscope/data/index): CHF 400 / yr (SFTP weekly subset) to CHF 2,600 / yr (SOAP search).

## §5 Connector strategy

### What we cover today

- PCT international applications via INPADOC (transitively, through [`patent_client_agents.epo_ops`](../regional/epo.md))
- Google Patents as a transitive aggregator for PCT publication metadata ([`patent_client_agents.google_patents`](../../src/patent_client_agents/google_patents/))

### What we should NOT add (and why)

- **PATENTSCOPE public-UI scraping** — ToS §2.1 explicitly forbids automated queries; >10 actions/min flagged excessive. Doing this would be a contract violation regardless of technical feasibility.
- **Paid SOAP search proxy** — SOAP + CHF 2,600/yr + paid-only model that we'd need to re-contract for each end user. Poor stack fit; redundant with INPADOC for most use cases.

### What we *could* consider

- **`wipo_pct_bulk`** — paid SFTP feed at CHF 400/yr for weekly PCT XML. Bulk-shaped, but legally clean and at the cheap end of WIPO's data products. [`BACKLOG.md`](../BACKLOG.md) Tier 1 Rank 7 lists this as `wipo_patentscope_bulk`. Doesn't meet zero-infra constraint by definition (bulk), but is a reasonable budget option if user demand for PCT-specific freshness justifies it.
- **`wipo_article6ter`** — free REST/JSON for state emblems / IGO marks. Small but clean; [BACKLOG Tier 1 Rank 8].

### What to monitor

- **WIPO partner API program** — undocumented endpoint observed at `public-api.branddb.wipo.int` (AWS API Gateway responding "Missing Authentication Token") suggests WIPO is building partner program. Recheck quarterly at [WIPO API Catalog](https://apicatalog.wipo.int/).

### Next steps

1. Quarterly recheck of [WIPO API Catalog](https://apicatalog.wipo.int/) for new public endpoints.
2. Consider `wipo_pct_bulk` if budget for CHF 400/yr exists AND user demand for PCT-specific freshness emerges.
3. `wipo_article6ter` is a low-effort win for trademark workflows that need state-emblem screening.

## §6 Open questions

- **WIPO partner API release date** — observed signals but no announcement.
- **PCT SFTP feed scope** — does it include reassignments / legal-status updates, or only publication-week snapshots? Contact `patentscope@wipo.int`.
- **WIPO Lex licensing for systematic mirroring of bibliographic metadata** — statutes themselves are public-domain but WIPO's metadata layer ToS is separately addressed.

## §7 References

Primary sources only.

**System overview:**
- [WIPO PCT](https://www.wipo.int/en/web/pct-system)
- [PATENTSCOPE search](https://patentscope.wipo.int/search/en/)
- [WIPO API Catalog](https://apicatalog.wipo.int/)

**ToS:**
- [PATENTSCOPE Terms of Use](https://patentscope.wipo.int/search/en/help/terms_conditions.jsf) — §2.1 (no automated queries)

**Data products:**
- [PCT Data Products and Services](https://www.wipo.int/en/web/patentscope/data/index)
- [Article 6ter Express](https://www.wipo.int/en/web/6ter)

**Detail survey + wave:**
- [`connectors/wipo.md`](../connectors/wipo.md)
- [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Confirmed the original "Tier 1 hard skip" verdict for public PATENTSCOPE; grounded primary-source citations for ToS §2.1 prohibition and paid SFTP / SOAP pricing. | [waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) |
