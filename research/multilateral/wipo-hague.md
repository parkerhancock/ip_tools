# WIPO Hague System (WO/WIPO/Hague)

**Layer:** multilateral
**Jurisdiction:** WO (international system)
**Issuing body:** World Intellectual Property Organization (WIPO) — International Bureau
**Rights administered:** industrial_design
**Working languages:** English, French, Spanish ([source](https://www.wipo.int/en/web/hague-system))
**Connector status:** skipped (no public search API; ToS + robots.txt prohibit automation)
**Last verified:** 2026-05-16
**Manifest entry:** not listed in `coverage/sources.yaml`

**Detail surveys:**
- [`connectors/wipo.md`](../connectors/wipo.md) — 2026-05 WIPO cross-asset survey (Hague Express row + HWS reference)
- [`waves/2026-05-16-coverage-batch-2/wipo-hague.md`](../waves/2026-05-16-coverage-batch-2/wipo-hague.md) — 2026-05-16 grounded API discovery for the Hague System itself

**Sibling layers covering overlapping data:**
- [`multilateral/wipo-global-design-db.md`](./wipo-global-design-db.md) — Global Design Database (Hague + ~30 national/regional collections aggregated)
- Future national design connectors (EUIPO, IP Australia Designs, USPTO design patents, JPO, KIPO) — Hague designations land in the same national registers via the Hague filing workflow

---

## §1 Mission

The Hague System is WIPO's centralized filing pathway for **international
industrial design registrations**. Filed via a single international
application under the 1960 and/or 1999 Acts of the Hague Agreement, an
international registration ("IR") can designate **80 contracting parties
covering 97 countries** (as of late 2024; growing — Saudi Arabia
[acceded in 2025](https://www.wipo.int/en/web/hague-system/w/news/2025/saudi-arabia-joins-the-hague-system),
with 82 members / 99 countries cited in the
[Hague Yearly Review 2025](https://www.wipo.int/web-publications/hague-yearly-review-2025-executive-summary/en/hague-yearly-review-2025-executive-summary.html)).
Each designation is then examined according to the law of the designated
contracting party. Agents care about Hague because it is the single
point of truth for an IR's bibliographic data, designations, and per-
country legal-status history before those events propagate (with lag)
into national design registers.

## §2 What's unique here

Hague-only data not reliably available from any higher layer:

- **The IR record itself** — IR number, registration date under 1960 vs
  1999 Acts, basic application identifiers — is canonical at WIPO and is
  the join key into per-country national-design files (see
  [Hague Guide: International Registration](https://www.wipo.int/en/web/hague-system/guide/registration)).
- **All-designations-from-one-filing** — Hague is the only place where
  every contracting-party designation of a single IR is visible together,
  before national propagation.
- **Legal-status changes from designated offices** — refusals,
  protections, invalidations are notified to WIPO and surfaced in the
  Hague Express UI and the International Designs Bulletin
  ([source](https://www.wipo.int/en/web/hague-system/bulletin/notes)).
- **The International Designs Bulletin** — weekly Friday-noon-CET
  publication that is the **legal-effect publication** for Hague IRs
  ([source](https://www.wipo.int/en/web/hague-system/bulletin/help)).
- **Reduced fees for LDC applicants** under the Hague Agreement —
  10% of the standard amounts, only knowable from WIPO's schedule
  ([source](https://www.wipo.int/en/web/hague-system/fees/sched)).

## §3 Programmatic surfaces

### Hague Express (public IR search UI)

| Field | Value |
|---|---|
| Endpoint | [`https://designdb.wipo.int/designdb/hague/en/`](https://designdb.wipo.int/designdb/hague/en/) — application entry; marketing page at [`/en/web/hague-system/design_search`](https://www.wipo.int/en/web/hague-system/design_search) |
| Auth | None for human use |
| Format | HTML JSP UI; AJAX returns HTML view-state fragments — no documented JSON |
| Rate limit | 10 search actions / minute / IP threshold ([GDD ToS §2.1](https://www.wipo.int/en/web/global-design-database/terms_and_conditions)); 24-hour IP block on robot detection ([GDD FAQ](https://www.wipo.int/en/web/global-design-database/faqs_designdb)) |
| ToS posture | Automated queries explicitly prohibited; robots.txt disallows `/designdb/*?` and `/designdb/*/jsp` paths ([source](https://www.wipo.int/robots.txt)) |
| Verdict (zero-infra proxy) | 🔴 red |
| Primary source | [Hague Express Help](https://designdb.wipo.int/designdb/hague/en/designdb-help.jsp) |

Inherits the Global Design Database stack; no Hague-specific public API.

### International Designs Bulletin (XML download)

| Field | Value |
|---|---|
| Endpoint | [`https://www.wipo.int/en/web/hague-system/bulletin/notes`](https://www.wipo.int/en/web/hague-system/bulletin/notes) (info), per-issue XML linked from [browse-by-bulletin](https://www.wipo.int/en/web/hague-system/bulletin/browse-by-bulletin) |
| Auth | None to download |
| Format | ST.96 v4.0 XML ([standard](https://www.wipo.int/standards/en/st96/v4-0/)) |
| Rate limit | Not documented as a programmatic feed |
| ToS posture | Intended for IP offices doing substantive review of IRs ([source](https://www.wipo.int/en/web/hague-system/w/news/2024/browsing-and-searching-the-international-designs-bulletin-is-easier-than-ever)) |
| Verdict (zero-infra proxy) | 🔴 red — bulk per-issue, not query; using it for per-user queries requires a hosted index |
| Primary source | [Bulletin help](https://www.wipo.int/en/web/hague-system/bulletin/help) |

ST.96-modeled XML, structurally clean — but bulk-only, which violates
our zero-infra rule.

### Hague Web Services (HWS) — partner-only

| Field | Value |
|---|---|
| Endpoint | Spec at [`https://www3.wipo.int/confluence/x/IACaTw`](https://www3.wipo.int/confluence/x/IACaTw) (IP-office-only Confluence); overview PDF at [`confluence.wipo.int/.../Hague Web Services_e-2.pdf`](https://confluence.wipo.int/confluence/download/attachments/1335492640/Hague%20Web%20Services_e-2.pdf?api=v2) |
| Auth | Asymmetric-key signature, [FAPI 1.0](https://openid.net/specs/openid-financial-api-part-1-1_0.html); partner IP offices only |
| Format | HTTPS REST/JSON; ST.96 payloads |
| Rate limit | Not public |
| ToS posture | Partner agreement; **not** available to third parties |
| Verdict (zero-infra proxy) | 🔴 red — not a search API; filing/exchange workflow only |
| Primary source | [WIPO API Catalog idAPI 158](https://apicatalog.wipo.int/) (entry "Hague Web Services (HWS)") |

The only Hague API in WIPO's catalog. Not for us.

### eHague (filer workbench)

| Field | Value |
|---|---|
| Endpoint | [`https://hague.wipo.int/`](https://hague.wipo.int/) |
| Auth | WIPO account (filer-scoped) |
| Format | Web UI |
| ToS posture | Filer-only; scoped to own portfolio |
| Verdict (zero-infra proxy) | 🔴 red — no public search surface |
| Primary source | [eHague filing tutorial](https://www.wipo.int/en/web/hague-system/ehague-filing-tutorial) |

Useful only for filers reading their own portfolio.

### Fee Calculator + Fee Schedule

| Field | Value |
|---|---|
| Endpoint | [`https://www.wipo.int/en/web/hague-system/fees/calculator`](https://www.wipo.int/en/web/hague-system/fees/calculator) (UI); [`/fees/sched`](https://www.wipo.int/en/web/hague-system/fees/sched) (HTML table); [`/fees/individ-fee`](https://www.wipo.int/en/web/hague-system/fees/individ-fee) (individual designation fees) |
| Auth | None |
| Format | HTML only; client-side JS reads static fee tables |
| ToS posture | Public information |
| Verdict (zero-infra proxy) | 🟡 yellow — usable by scraping the HTML schedule for fee snapshots, but no JSON API |
| Primary source | [Fee schedule page](https://www.wipo.int/en/web/hague-system/fees/sched) |

The fee schedule is HTML and stable — a tractable scrape target *if* we
ever decide to surface Hague fees, but not a search surface.

## §4 Fee schedule (snapshot 2026-05-16)

**Detail file:** none yet — fees inline below.
**Official schedule:** [Hague System Schedule of Fees](https://www.wipo.int/en/web/hague-system/fees/sched)
**Fee calculator:** [Hague System Fee Calculator](https://www.wipo.int/en/web/hague-system/fees/calculator)
**Effective date:** 2025-01-01 (per page title "Schedule of Fees (as in force on January 1, 2025)")
**Currency:** Swiss francs (CHF) only — all Hague fees ([source](https://www.wipo.int/en/web/paying-for-ip-services/hague-system-fees))

| Category | Amount (CHF) | Notes |
|---|---|---|
| Basic fee — one design | 397 | International application |
| Basic fee — each additional design | 50 | Same international application (raised from 19 effective 2024-01-01) |
| Publication — per reproduction | 17 | |
| Publication — each extra page of reproductions | 150 | After the first |
| Standard designation fee — level one, one design | 42 | Plus 2 CHF per additional design |
| Standard designation fee — level two, one design | 60 | Plus 20 CHF per additional design |
| Standard designation fee — level three, one design | 90 | Plus 50 CHF per additional design |
| Individual designation fees | varies | Per contracting party — see [`/fees/individ-fee`](https://www.wipo.int/en/web/hague-system/fees/individ-fee) |
| LDC applicant reduction | × 10% | Reduced to 10% of standard for applicants whose sole entitlement is connection with an LDC |

USD conversion intentionally omitted — Hague fees are paid only in CHF.

## §5 Connector strategy

### What we cover today

Nothing for Hague. WIPO Lex (statute text) covers the **Hague Agreement
text** itself but not Hague IRs. National connectors (IP Australia
Designs, etc.) cover Hague-designated designs after national
propagation.

### What we should add (if anything)

**Nothing for live search.** The strategic memory:

- No public Hague search API exists.
- The Hague Express UI is ToS-blocked and robots.txt-blocked.
- The Bulletin XML feed is bulk-per-issue and violates the zero-infra
  rule.
- HWS is partner-only.

Mild yellow opportunity: **Hague fee snapshot scrape** of
[`/fees/sched`](https://www.wipo.int/en/web/hague-system/fees/sched) and
[`/fees/individ-fee`](https://www.wipo.int/en/web/hague-system/fees/individ-fee).
The pages are stable HTML with structured tables (confirmed 2026-05-16
by `curl` + `grep` against the live pages). This would be a tiny static
corpus refresher, not a live API. Low priority.

### What we should NOT add

- Live Hague Express search proxy — explicitly prohibited by ToS §2.1
  ([Global Design Database Terms of Use](https://www.wipo.int/en/web/global-design-database/terms_and_conditions))
  and `robots.txt` (`Disallow: /designdb/*?`,
  [source](https://www.wipo.int/robots.txt)).
- International Designs Bulletin XML mirror — violates zero-infra
  ("we will NOT host a search index").
- HWS integration — partner-only, not available to us.

### Next steps

- Quarterly re-check of the [WIPO API Catalog](https://apicatalog.wipo.int/)
  for a potential future public Hague search API.
- Optionally schedule a small Hague fee-snapshot scrape (yellow,
  low-priority) if downstream users ask for "what does a Hague filing
  cost in country X."
- Continue to direct Hague-related queries to WIPO's UI as a deep-link
  destination, not as a proxied surface.

## §6 Open questions

- Is there a private Hague search API for the **WIPO IP Portal**'s
  authenticated users at [`https://ipportal.wipo.int/`](https://ipportal.wipo.int/)
  beyond the eHague workbench? — No primary source found.
- Will the WIPO API Catalog ever list a **third-party-callable** Hague
  search API? — No public roadmap. The [WIPO API Day 2023 program](https://www.wipo.int/en/web/cws/wipo-api-day-program)
  mentioned API catalogue expansion in general but no Hague search
  commitment.
- Could Hague IR data be reached through the **EUIPO DesignView** /
  federated design search? — Not yet investigated; tracked in the next
  wave.
- Are the per-country **individual designation fees** scrape-friendly as
  a structured table? — Pages exist at
  [`/fees/individ-fee`](https://www.wipo.int/en/web/hague-system/fees/individ-fee);
  not yet shape-validated.

## §7 References

- [Hague System main page](https://www.wipo.int/en/web/hague-system)
- [How does the Hague System work?](https://www.wipo.int/en/web/hague-system/how_hague_works)
- [Hague Guide for Users — International Registration](https://www.wipo.int/en/web/hague-system/guide/registration)
- [Hague Express search UI (marketing page)](https://www.wipo.int/en/web/hague-system/design_search)
- [Hague Express application entry](https://designdb.wipo.int/designdb/hague/en/)
- [Hague Express Help](https://designdb.wipo.int/designdb/hague/en/designdb-help.jsp)
- [International Designs Bulletin — notes](https://www.wipo.int/en/web/hague-system/bulletin/notes)
- [International Designs Bulletin — help](https://www.wipo.int/en/web/hague-system/bulletin/help)
- [2024 Bulletin redesign news (XML download mention)](https://www.wipo.int/en/web/hague-system/w/news/2024/browsing-and-searching-the-international-designs-bulletin-is-easier-than-ever)
- [eHague portal](https://hague.wipo.int/)
- [Hague System Fee Calculator](https://www.wipo.int/en/web/hague-system/fees/calculator)
- [Hague System Schedule of Fees — Jan 1, 2025](https://www.wipo.int/en/web/hague-system/fees/sched)
- [Individual Designation Fees](https://www.wipo.int/en/web/hague-system/fees/individ-fee)
- [Paying Hague System Fees](https://www.wipo.int/en/web/paying-for-ip-services/hague-system-fees)
- [Global Design Database Terms of Use (Nov 2022)](https://www.wipo.int/en/web/global-design-database/terms_and_conditions)
- [Global Design Database FAQs (IP-block enforcement)](https://www.wipo.int/en/web/global-design-database/faqs_designdb)
- [wipo.int robots.txt](https://www.wipo.int/robots.txt)
- [WIPO API Catalog](https://apicatalog.wipo.int/) — HWS entry idAPI 158
- [Hague Web Services overview PDF (2021)](https://confluence.wipo.int/confluence/download/attachments/1335492640/Hague%20Web%20Services_e-2.pdf?api=v2)
- [HWS bidirectional-exchange presentation (2022)](https://www.wipo.int/edocs/mdocs/hague/en/wipo_it_id_ge_22/wipo_it_id_ge_22_presentation.pdf)
- [ST.96 v4.0 XML standard](https://www.wipo.int/standards/en/st96/v4-0/)
- [Hague Yearly Review 2025 — Executive Summary](https://www.wipo.int/web-publications/hague-yearly-review-2025-executive-summary/en/hague-yearly-review-2025-executive-summary.html)
- [Saudi Arabia joins the Hague System (2025)](https://www.wipo.int/en/web/hague-system/w/news/2025/saudi-arabia-joins-the-hague-system)

---

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis | Distilled from `connectors/wipo.md` + `waves/2026-05-16-coverage-batch-2/wipo-hague.md` + live `curl` verification of `wipo.int/robots.txt`, `designdb.wipo.int/designdb/hague/en/`, `apicatalog.wipo.int/api/apis/all`, and `/en/web/hague-system/fees/sched` |
