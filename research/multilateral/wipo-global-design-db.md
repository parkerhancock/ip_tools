# WIPO Global Design Database — multilateral

**Layer:** multilateral
**System:** Aggregated international + national industrial design search
**Operator:** World Intellectual Property Organization (WIPO)
**Rights covered:** industrial_design
**Coverage:** Hague International Register + national design records from ~30 contributing offices
**Working languages:** English + WIPO official languages
**Connector status:** **skipped for live search** (ToS prohibits automation; no public search API; only Hague Web Services for filing-side IP offices)
**Last verified:** 2026-05-16
**Manifest entry:** not listed in `coverage/sources.yaml`

**Detail surveys:**
- [`connectors/wipo.md`](../connectors/wipo.md) — 2026-05 detail survey
- [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) — 2026-05-16 grounded discovery

**Higher / sibling layers carrying overlapping data:**
- **WIPO Hague System direct** — for Hague IRs specifically; the Design DB also includes national contributions.
- **EUIPO REUD search** — for EU-level designs (formerly RCDs); EU is a Hague member, so Hague-EU designations also visible here.
- **DesignView** (likely EUIPO-hosted, design analogue of TMview) — federated frontend over national design registers; not yet investigated.
- **National design registers** (where APIs exist) — IP Australia Designs, JPO designs.

---

## §1 Mission

The Global Design Database is WIPO's flagship public design search,
unifying Hague IRs with ~30 contributing national design offices. It's
the smallest of the three WIPO databases by contributing-office count
because the Hague System has fewer members than Madrid (79 contracting
parties vs. 116) and national design contribution is less common.

For agents working on industrial designs internationally, this is the
conceptual aggregator. But like its siblings, the public web UI ToS
prohibits automated queries, and there's no public search API at all —
only Hague Web Services, which is a filing-side back-end for IP offices,
not a search surface.

## §2 What's unique here (not covered by higher layers)

- **Hague IRs in a unified search** — Hague IRs are reachable via WIPO Madrid-equivalent processes but the Global Design DB is the consumer-facing search.
- **National designs from offices that don't have their own public API.**
- **Hague-specific bibliographic detail** that doesn't always flow up to national designations.

## §3 Programmatic surfaces

### Public Global Design DB web UI

| Field | Value |
|---|---|
| Endpoint | `https://designdb.wipo.int/` |
| Auth | none for casual UI use |
| Format | HTML |
| Cap | **100 results downloadable per query** |
| Rate limit | UI throttle; the **FAQ openly states a 24-hour IP block** for "robot" behaviour |
| ToS posture | Same identical "no automated queries" language as PATENTSCOPE + Brand DB |
| Verdict (zero-infra proxy) | 🔴 **Red** — ToS prohibits; 24-hour IP block enforces |
| Primary sources | [Global Design Database Terms of Use](https://www3.wipo.int/designdb/en/help/terms.jsp) · WIPO API Catalog |

### Hague Web Services — filing-side back-end (IP offices only)

WIPO's catalog ships **Hague Web Services**, but inspection of the
documentation shows this is a **filing back-end for IP offices** (used
for transmitting Hague designations from national offices to WIPO),
**not a public search surface**.

| Field | Value |
|---|---|
| Endpoint | listed in [WIPO API Catalog](https://apicatalog.wipo.int/) |
| Auth | IP-office credentials only |
| Format | SOAP / structured filing payloads |
| Verdict | 🔴 Red — wrong shape for our use case (filing, not search; office-only auth) |

### Hague Express

Public search front-end for Hague IRs specifically. Polite scrape is
possible per the 2026-05 connector survey at `connectors/wipo.md`.
Limited to Hague IRs (not the broader Global Design DB aggregation).

| Field | Value |
|---|---|
| Endpoint | `https://www.wipo.int/hague/en/express/` |
| Auth | none |
| Format | HTML |
| ToS posture | Subject to WIPO general ToS |
| Verdict | 🟡 Yellow — polite scrape conceivable; smaller scope (Hague IRs only); see [BACKLOG Tier 1 Rank 14](../BACKLOG.md) for `wipo_hague_express` |

## §4 Fee schedule

Hague System filing fees (the source of most Design DB records) live
with the Hague System, not Design DB.

**Hague System fees:** [WIPO — Hague System fees](https://www.wipo.int/en/web/hague-system/fees)
**Fee Calculator:** [WIPO Hague Fee Calculator](https://www.wipo.int/hague/feescalculator/)

Design DB *access fees:* no fee for the public UI; no documented paid
tier. Access is gated by lack of available programmatic surface, not by
payment.

## §5 Connector strategy

### What we cover today

- No Design DB access. EU-level designs reachable via [`patent_client_agents.euipo_designs`](../regional/euipo.md). Other Hague IRs reachable only through individual national connectors where they exist (IP Australia, JPO).

### What we should NOT add (and why)

- **Public UI scraping** — ToS prohibits; 24-hour IP block enforces. The FAQ language is unusually direct about enforcement.
- **Hague Web Services** — wrong shape (filing back-end, not search); office-only auth.

### What we *could* consider

- **`wipo_hague_express`** — polite scrape of Hague Express, limited to Hague IRs (not the full Global Design DB aggregation). [BACKLOG Tier 1 Rank 14]. Smaller scope; could be useful for international-design workflows. Verdict from the original Tier 1 survey was "trivial; also covers other Hague-system designs."

### What to monitor

- **DesignView API** — EUIPO operates DesignView as a federated frontend over national design registers (analogous to TMview). If DesignView gains a public API, it could be the practical design aggregator we want. Currently HTML-only; not API-accessible. See [`COVERAGE_STRATEGY.md`](../COVERAGE_STRATEGY.md) §8 (open questions).
- **WIPO partner API program** — same general pattern as the Brand DB; if WIPO opens a partner tier for Design DB, we'd want in.

### Next steps

1. Quarterly recheck of [WIPO API Catalog](https://apicatalog.wipo.int/) for new Design DB tier announcements.
2. Investigate DesignView (likely EUIPO-hosted) for any public API path. See coverage-strategy open questions.
3. Consider `wipo_hague_express` if a paying customer needs Hague-specific design search.

## §6 Open questions

- **WIPO partner API for designs** — symmetric to the Brand DB question; no observed `public-api.designdb.wipo.int` endpoint yet.
- **DesignView API availability** — needs discovery research; on the [COVERAGE_STRATEGY](../COVERAGE_STRATEGY.md) open-questions list.
- **Hague Express scraping etiquette** — what's the polite rate?

## §7 References

Primary sources only.

**System overview:**
- [WIPO Global Design Database](https://designdb.wipo.int/)
- [WIPO API Catalog](https://apicatalog.wipo.int/)

**ToS:**
- [Global Design Database Terms of Use](https://www3.wipo.int/designdb/en/help/terms.jsp) — automation prohibition; 24-hour IP-block FAQ

**Hague System (the source of most Design DB records):**
- [Hague System main](https://www.wipo.int/en/web/hague-system)
- [Hague System Members](https://www.wipo.int/web/hague-system/members) — 79 contracting parties / 96 countries
- [Hague System fees](https://www.wipo.int/en/web/hague-system/fees)
- [Hague Express search](https://www.wipo.int/hague/en/express/)

**Detail survey + wave:**
- [`connectors/wipo.md`](../connectors/wipo.md)
- [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Confirmed the original "Tier 1 hard skip" verdict and grounded primary-source citations. Flagged the FAQ's 24-hour-IP-block language as enforcement detail not previously documented. | [waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) |
