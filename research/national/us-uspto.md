# USPTO United States (US) — national

**Layer:** national
**Jurisdiction:** US (WIPO ST.3: US)
**Issuing body:** United States Patent and Trademark Office (an agency of the Department of Commerce)
**Rights administered:** patent, trademark, design_patent (designs are handled as design patents in the US — different mechanism than other jurisdictions)
**Working languages:** English
**Connector status:** **active** (deepest connector in the catalog)
**Last verified:** 2026-05-16
**Manifest entries:**
- `US/USPTO/ODP/Applications` — `patent_client_agents.uspto_odp`
- `US/USPTO/ODP/PTAB` — same module
- `US/USPTO/ODP/Petitions` — same module
- `US/USPTO/PPUBS` — `patent_client_agents.uspto_publications`
- `US/USPTO/Assignments/Patents` — `patent_client_agents.uspto_assignments`
- `US/USPTO/OfficeActions` — `patent_client_agents.uspto_office_actions`
- `US/USPTO/BulkData` — `patent_client_agents.uspto_bulkdata`
- `US/USPTO/TSDR` — `patent_client_agents.uspto_tsdr`
- `US/USPTO/TMSearch` — `patent_client_agents.uspto_tmsearch`
- `US/USPTO/Assignments/Trademarks` — `patent_client_agents.uspto_trademark_assignments`
- `US/USPTO/MPEP` — `patent_client_agents.mpep` (substantive law)
- `US/USPTO/TMEP` — `patent_client_agents.tmep` (substantive law)

**Detail surveys:**
- Substantial existing knowledge across the connector codebase + [`MIGRATION_PLAYBOOK.md`](../../MIGRATION_PLAYBOOK.md) rows 1-8 (USPTO migrations)
- USPTO Applications migration is the canonical template for the playbook (row 1, ✅ done)

**Higher / sibling layers carrying overlapping data:**
- **EPO INPADOC** — US patent biblio is in DOCDB, but USPTO ODP is **the authoritative real-time source** for US patents and adds prosecution depth INPADOC doesn't carry.
- **Google Patents** — covers US patents transitively; useful for prior-art search across foreign patents that USPTO doesn't issue.
- **WIPO PATENTSCOPE** — for PCT applications filed at USPTO as receiving office.

---

## §1 Mission

USPTO is the largest patent office in the world by application volume
and the source-of-record for US patents, trademarks, and design patents.
US is unusually open about data access — the agency operates under a
statutory open-data mandate that makes USPTO the cleanest API surface
of any major IP office globally. This is why USPTO is our deepest
connector by far: ~10 distinct services covering applications, PPUBS,
Assignments, OAs, PTAB, Petitions, TSDR, TM Search, TM Assignments,
Bulk Data, plus substantive-law layers (MPEP, TMEP, CAFC opinions, USITC).

If you only proxied one office's data, you'd proxy USPTO.

## §2 What's unique here (not covered by higher layers)

- **Full prosecution file wrappers** (file history, IDS, transactions) via ODP and bulk
- **Real-time application status** (vs. INPADOC's lag of weeks-to-months)
- **Office actions full text** with structured rejection codes
- **PTAB proceedings** (IPR, PGR, CBM, Interference, Appeal decisions)
- **Petitions** (revival, extensions, etc.)
- **Patent + trademark assignment history** with structured reel/frame
- **TSDR** (Trademark Status and Document Retrieval) — TM file history, opposition records
- **TM Search** (the modernized USPTO TM search)
- **Design patent register** (US handles industrial designs as a class of patent, not as a separate right)

## §3 Programmatic surfaces

### USPTO Open Data Portal (ODP)

| Field | Value |
|---|---|
| Endpoint | `https://api.uspto.gov/` |
| Auth | API key (free; obtained via developer.uspto.gov) |
| Format | JSON |
| ToS posture | Permissive; explicit open-data policy |
| Verdict | 🟢 Green — operational |
| Primary source | [USPTO Open Data Portal](https://developer.uspto.gov/) |

Covers applications, PTAB, Petitions in one API.

### PPUBS (Patent Public Search)

| Field | Value |
|---|---|
| Endpoint | `https://ppubs.uspto.gov/dirsearch-public/` |
| Auth | none (cookie-based session for advanced features) |
| Format | JSON |
| Verdict | 🟢 Green — operational via [`patent_client_agents.uspto_publications`](../../src/patent_client_agents/uspto_publications/) |

### USPTO Bulk Data products

| Field | Value |
|---|---|
| Endpoint | `https://developer.uspto.gov/data` |
| Auth | API key for catalog browsing |
| Format | various — XML, PDF, CSV per product |
| Verdict | 🟢 Green for catalog navigation; bulk delivery is bulk-shaped (not used for live proxy) |

### TSDR (Trademark Status & Document Retrieval)

| Field | Value |
|---|---|
| Endpoint | `https://tsdrapi.uspto.gov/ts/` |
| Auth | TSDR_API_KEY (free; signup via TSDR portal) |
| Format | JSON / XML / ZIP per request |
| Verdict | 🟢 Green |

### TM Search (modernized TM register)

| Field | Value |
|---|---|
| Endpoint | `https://tmsearch.uspto.gov/` |
| Auth | varies (some endpoints public, some session-based) |
| Verdict | 🟢 Green — operational via [`patent_client_agents.uspto_tmsearch`](../../src/patent_client_agents/uspto_tmsearch/) |
| Note | Egress filtering concern: TESS (predecessor) was blocked from Cloud Run egress per [`memory/project_cloud_run_egress.md`](../../../../.claude/projects/-Users-parkerhancock-Projects-parker-monorepo-tools-patent-client-agents/memory/project_cloud_run_egress.md). TM Search may have similar filtering — verify per deployment. |

## §4 Fee schedule

**Detail file:** [`fee-schedules/us-uspto-fees.md`](../fee-schedules/us-uspto-fees.md)
**Official schedule:** [USPTO Fee Schedule](https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule)
**Consolidated PDF:** [USPTO-fee-schedule_current.pdf (eff. 2025-01-19, rev. 2026-05-01)](https://www.uspto.gov/sites/default/files/documents/USPTO-fee-schedule_current.pdf)
**Statutory basis:** 35 USC + 37 CFR Part 1 (patents) / 37 CFR Part 2 (trademarks); USPTO fee-setting authority under §10 of the Patent Act (sunsets 2026-09-16 — see notes below)

### Patent fees (current — large entity baseline)

| Category | Amount (USD) | Notes |
|---|---|---|
| Filing (basic) | 320 | Plus search + examination fees |
| Search | 700 | |
| Examination | 800 | |
| Issue | 1,290 | |
| Maintenance yr 3.5 | 2,000 | |
| Maintenance yr 7.5 | 3,760 | |
| Maintenance yr 11.5 | 7,700 | |
| RCE (1st) | 1,500 | |
| RCE (2nd+) | 2,000 | |
| Appeal forwarding | 2,560 | |

**Entity-size tiers:**
- **Small entity (≤500 employees)** — **60%** off most fees (up from 50% pre-UAIA, late 2022)
- **Micro entity** — **80%** off most fees (up from 75% pre-UAIA)

### Trademark fees (current)

**Major change 2025-01-18:** TEAS Plus / TEAS Standard tiers **abolished**.
Single base fee + surcharges replaces the old two-tier model.

| Category | Amount (USD) | Notes |
|---|---|---|
| Application (1 class) | 350 | Single base fee |
| Free-text ID surcharge | 200 / class | |
| Missing info surcharge | 100 / class | |
| Oversized ID surcharge | 200 / class | |
| Statement of use | 100 / class | |
| Renewal (every 10 yr) | 425 / class | |

### Notes

- **Director's §10 fee-setting authority sunsets 2026-09-16** — further fee adjustments require legislation or rulemaking before this date.
- **USPTO is the most fee-litigated office in the world** — recent rulemakings include 89 FR 91898 (FY25 Patent), 89 FR 91062 (FY25 Trademark).
- Any cost model relying on the **pre-UAIA discount tiers (50% / 75%)** or the **TEAS Plus/Standard structure** is stale.

## §5 Connector strategy

### What we cover today

The full USPTO catalog. ~10 distinct connector modules (see manifest entries above). USPTO is the only office where we ship near-complete coverage across applications + publications + assignments + office actions + PTAB + petitions + TM search + TSDR + bulk data catalog + substantive-law layers (MPEP, TMEP).

### What we should improve

- **MIGRATION_PLAYBOOK rows 4-8 pending** — Google Patents, USPTO PTAB, Office Actions, Petitions, Assignments still need the §5.9 envelope sweep. Highest-value local cleanup ahead of new connectors. See [`MIGRATION_PLAYBOOK.md`](../../MIGRATION_PLAYBOOK.md).
- **TBMP** (Trademark Trial and Appeal Board Manual) — `BACKLOG.md` US Gap Analysis identifies this as a small new module. Mirrors MPEP/TMEP shape.
- **Design Patent Examiner Guidelines** — no formal "MPEP for designs"; consider adding as a small module or extending MPEP to surface design-specific chapters.

### What we should NOT add

- **Pre-grant publications scraping outside PPUBS** — PPUBS already covers this; alternative scrapers are redundant.
- **Bulk-only ingestion** — runs against the zero-infra constraint; ODP + PPUBS + TSDR cover the live-search needs.

### Next steps

1. Knock out MIGRATION_PLAYBOOK rows 4-8 (envelope sweep on existing tools). Highest-leverage local cleanup.
2. Update fee logic anywhere it references TEAS Plus/Standard or pre-UAIA (50%/75%) discount tiers — both are stale as of 2025-01-18.
3. Ship TBMP (~1 day per BACKLOG estimate).
4. Watch for USPTO Director §10 sunset (2026-09-16) — fee rulemaking cadence may shift.

## §6 Open questions

- **What happens after §10 sunset?** Will Congress reauthorize, or does fee-adjustment revert to formal rulemaking only?
- **Are there post-grant proceedings beyond IPR/PGR/CBM that we don't expose?** Worth reviewing PTAB tool scope.
- **TM Search Cloud Run egress** — confirmed problematic for TESS predecessor; verify TM Search per deployment.

## §7 References

Primary sources only.

**APIs:**
- [USPTO Open Data Portal](https://developer.uspto.gov/) — ODP / PPUBS / TSDR / TM Search developer docs
- [TSDR API](https://tsdrapi.uspto.gov/)
- [USPTO Patent Center](https://patentcenter.uspto.gov/) — application detail UI

**Fees:**
- [USPTO Fee Schedule](https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule)
- [FY2025 Patent Fee Rule (89 FR 91898)](https://www.federalregister.gov/documents/2024/11/20/2024-26821/setting-and-adjusting-patent-fees-during-fiscal-year-2025)
- [FY2025 Trademark Fee Rule (89 FR 91062)](https://www.federalregister.gov/documents/2024/11/18/2024-26644/setting-and-adjusting-trademark-fees-during-fiscal-year-2025)

**Statutory:**
- [35 USC](https://uscode.house.gov/browse/prelim@title35) — patents
- [37 CFR](https://www.ecfr.gov/current/title-37) — patent + trademark regulations

**Detail in this repo:**
- [`MIGRATION_PLAYBOOK.md`](../../MIGRATION_PLAYBOOK.md) — rows 1-8 for USPTO migrations
- [`fee-schedules/us-uspto-fees.md`](../fee-schedules/us-uspto-fees.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. **Reconciled TEAS Plus/Standard abolition (2025-01-18) and UAIA discount-tier shift (small 50%→60%, micro 75%→80%, late 2022).** Both invalidate older fee logic in the codebase if it exists. | [fee-schedules/us-uspto-fees.md](../fee-schedules/us-uspto-fees.md) |
