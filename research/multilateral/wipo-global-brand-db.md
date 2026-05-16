# WIPO Global Brand Database — multilateral

**Layer:** multilateral
**System:** Aggregated international + national trademark / appellation-of-origin search
**Operator:** World Intellectual Property Organization (WIPO)
**Rights covered:** trademark, appellation_of_origin (Article 6ter emblems also reachable separately)
**Coverage:** Madrid International Register + Article 6ter + ~75 national TM offices' contributed records
**Working languages:** English + WIPO official languages
**Connector status:** **skipped for live search** (ToS prohibits automation; public API restricted to "collaborating IP Offices"); future partner API monitored
**Last verified:** 2026-05-16
**Manifest entry:** not listed in `coverage/sources.yaml`

**Detail surveys:**
- [`connectors/wipo.md`](../connectors/wipo.md) — 2026-05 detail survey
- [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) — 2026-05-16 grounded discovery (PATENTSCOPE + Brand DB + Design DB)

**Higher / sibling layers carrying overlapping data:**
- **WIPO Madrid System direct** — for Madrid IRs specifically; the Brand DB also includes Madrid plus national TMs.
- **EUIPO TMview** — federated national-TM search hosted by EUIPO (search frontend over national registers). Different aggregator with different scope.
- **National TM registers** (where APIs exist) — USPTO TM Search, EUIPO EUTMs, IP Australia TMs.

---

## §1 Mission

The Global Brand Database is WIPO's flagship public trademark search,
unifying Madrid IRs + Article 6ter state emblems + contributed records
from ~75 national TM offices into one search interface. Conceptually
this is the trademark sibling of PATENTSCOPE — and from a coverage
perspective, the right multilateral aggregator to substitute for many
national TM connectors at once.

The catch matches PATENTSCOPE's: the public Global Brand DB has a web
UI but no public API for general use; the one API endpoint in WIPO's
catalog is explicitly restricted to "collaborating IP Offices" (not
commercial third parties); and the public UI has been hardened with
CAPTCHAs that block automated access.

## §2 What's unique here (not covered by higher layers)

- **Madrid IRs in a unified search** — search Madrid IRs alongside national TMs without per-office plumbing.
- **Article 6ter state emblems / IGO marks** — also reachable via the Article 6ter Express API separately ([`wipo-patentscope.md`](wipo-patentscope.md) §3).
- **National TMs from offices that don't have their own public API** — the long-tail value.

## §3 Programmatic surfaces

### Public Global Brand DB web UI

| Field | Value |
|---|---|
| Endpoint | `https://branddb.wipo.int/` |
| Auth | none for casual UI use |
| Format | HTML |
| Rate limit | UI throttle + AltCha proof-of-work CAPTCHA on every page load (observed 2026-05-16) |
| Cap | 180 results downloadable per query |
| ToS posture | **Explicit prohibition on automated queries** (same identical language as PATENTSCOPE ToS) |
| Verdict (zero-infra proxy) | 🔴 **Red** — ToS prohibits the access pattern; CAPTCHA enforces it |
| Primary source | [Global Brand Database Terms of Use](https://branddb.wipo.int/en/quicksearch/about/terms) |

### `idAPI 188` — restricted to collaborating offices

The one Brand DB API in WIPO's official catalog is gated to IP offices
that have signed collaboration agreements with WIPO. Not available to
commercial third parties.

| Field | Value |
|---|---|
| Endpoint | listed in [WIPO API Catalog](https://apicatalog.wipo.int/) as idAPI 188 |
| Auth | IP-office collaboration agreement required |
| Verdict | 🔴 Red — eligibility-gated; not available to us |
| Primary source | [WIPO API Catalog](https://apicatalog.wipo.int/) — search for "Brand Database" |

### Undocumented `public-api.branddb.wipo.int`

An AWS API Gateway endpoint at this URL responds with "Missing
Authentication Token" — the standard AWS error for an authenticated
endpoint hit without credentials. This **strongly suggests WIPO is
building a partner API program** that hasn't been announced yet.

| Field | Value |
|---|---|
| Endpoint | `https://public-api.branddb.wipo.int/` (undocumented; AWS API Gateway) |
| Status | Endpoint exists; auth required; no public documentation |
| Verdict | ⏳ Watch — no current path, but signals future opening |
| Primary source | Observed 2026-05-16 — [waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) §"Surprises" |

## §4 Fee schedule

Madrid System filing fees (the source of most Brand DB records) live
with the Madrid System, not Brand DB.

**Madrid System fees:** [WIPO — Madrid System fees](https://www.wipo.int/en/web/madrid-system/fees)
**Fee Calculator:** [WIPO Madrid Fee Calculator](https://www.wipo.int/madrid/feescalculator/)

Brand DB *access fees:* no fee for the public UI; no documented paid
tier (unlike PATENTSCOPE's SOAP/SFTP products). Access is gated by
eligibility (collaborating IP offices), not payment.

## §5 Connector strategy

### What we cover today

- No Brand DB access. Madrid IRs are reachable transitively when a national TM connector includes them in its scope (e.g., EUIPO returns Madrid-IR-designating-EU TMs in its search results).

### What we should NOT add (and why)

- **Public UI scraping** — ToS prohibits; CAPTCHA enforces. Even if technically bypassed, it's a contract violation.
- **idAPI 188 connector** — restricted to collaborating IP offices; we are not eligible.

### What to monitor

- **`public-api.branddb.wipo.int`** — undocumented endpoint suggests WIPO is building a partner program. **Highest-leverage watch item** for trademark coverage. If WIPO opens a commercial partner tier, this becomes the trademark analogue of EPO INPADOC.
- **TMview API** — EUIPO operates TMview as a federated frontend over national TM registers. If TMview gains a public API, it could be the practical TM aggregator. Currently HTML-only; not API-accessible. See [`COVERAGE_STRATEGY.md`](../COVERAGE_STRATEGY.md) §8 (open questions) for the TMview research target.

### Next steps

1. Quarterly recheck of [WIPO API Catalog](https://apicatalog.wipo.int/) for new Brand DB tier announcements.
2. Quarterly recheck of `public-api.branddb.wipo.int` for documentation publication.
3. Consider direct outreach to `apiteam@wipo.int` (or equivalent) for partner-tier inquiry if a paying customer needs Madrid + national TM aggregation badly.

## §6 Open questions

- **`public-api.branddb.wipo.int` partner program** — what's the eligibility model? When does it open?
- **idAPI 188 eligibility expansion** — will WIPO extend Brand DB API access beyond collaborating IP offices?
- **TMview API roadmap** — does EUIPO plan to expose TMview programmatically?

## §7 References

Primary sources only.

**System overview:**
- [WIPO Global Brand Database](https://branddb.wipo.int/)
- [WIPO API Catalog](https://apicatalog.wipo.int/)

**ToS:**
- [Global Brand Database Terms of Use](https://branddb.wipo.int/en/quicksearch/about/terms) — automation prohibition

**Madrid System (the source of most Brand DB records):**
- [Madrid System main](https://www.wipo.int/en/web/madrid-system)
- [Madrid System Members](https://www.wipo.int/en/web/madrid-system/members/index) — 116 members / 132 countries
- [Madrid System fees](https://www.wipo.int/en/web/madrid-system/fees)

**Article 6ter (sibling dataset):**
- [Article 6ter Express](https://www.wipo.int/en/web/6ter)

**Detail survey + wave:**
- [`connectors/wipo.md`](../connectors/wipo.md)
- [`waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md`](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Confirmed the original "Tier 1 hard skip" verdict and grounded the primary-source citations. **Flagged undocumented `public-api.branddb.wipo.int` endpoint as the highest-leverage trademark-coverage watch item.** | [waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md](../waves/2026-05-16-registered-ip-discovery/wipo-global-databases.md) |
