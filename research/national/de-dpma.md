# DPMA Germany (DE) — national

**Layer:** national
**Jurisdiction:** DE (WIPO ST.3: DE)
**Issuing body:** Deutsches Patent- und Markenamt (German Patent and Trade Mark Office)
**Rights administered:** patent, utility_model, trademark, design, copyright (registers; copyright is largely automatic in DE)
**Working languages:** German (primary); English (partial — some service pages, fee schedules)
**Connector status:** **skipped for live registers** (contract §3.2 prohibits proxy use); statutes shipped
**Last verified:** 2026-05-16
**Manifest entry:** [`coverage/sources.yaml` `DE/DPMA/Statutes`](../../coverage/sources.yaml) (statutes only — `patent_client_agents.dpma_statutes`)

**Detail surveys:**
- [`connectors/dpma.md`](../connectors/dpma.md) — 2026-05 detail survey (211 lines; covers DPMAregister UI, DEPATISnet, DPMAconnectPlus REST, backfile, BPatG/BGH case law, gesetze-im-internet)
- [`waves/2026-05-16-registered-ip-discovery/dpma-germany.md`](../waves/2026-05-16-registered-ip-discovery/dpma-germany.md) — 2026-05-16 grounded API discovery

**Higher layers covering this office transitively:**
- **EPO INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — DE patent biblio + family; this is the recommended substitute for DPMA patent register data.
- **EUIPO** (via [`regional/euipo.md`](../regional/euipo.md)) — only for EU-level marks (EUTMs designating DE); pure DE national TMs are NOT covered.
- **WIPO Madrid / Hague** — Madrid IRs designating DE / Hague IRs designating DE; national-only filings are NOT covered.

---

## §1 Mission

DPMA is the largest national IP office in Europe and the home office for
the Bundespatentgericht (BPatG) and the Unified Patent Court's Munich
Central Division (mechanical engineering). Germany is strategic for any
European IP work — but the German federal data-access policy treats
register data as a paid product with strict redistribution terms.

For agents working on German patents, EPO OPS via INPADOC substitutes
for biblio/family at the regional layer. National-only filings at the
TM and design level — and German utility models (Gebrauchsmuster), a
distinctive German right type not in EP — remain DPMA-exclusive but
are not proxyable under the current contract terms.

## §2 What's unique here
- **German utility models (Gebrauchsmuster, GebrMG)** — a registered right distinct from patents; not covered by EP filings; only path is DPMA.
- **National-only DE trademarks** — those filed directly with DPMA, not via Madrid IR or EUTM.
- **National-only DE designs** — those filed directly with DPMA, not via Hague IR or RCD/REUD.
- **Real-time DPMA file history** — DPMAregister UI has live file inspection; EPO OPS doesn't carry it.
- **DPMA-specific procedural events** — opposition, nullity, BPatG appeal status.

## §3 Programmatic surfaces

### DPMAconnectPlus REST API

| Field | Value |
|---|---|
| Endpoint | `https://dpmaconnect.dpma.de/dpmaws/rest-services/` (separate services per right) |
| Auth | HTTP Basic (username + password); paper contract required |
| Format | XML on ST.36 (patents) / ST.66 (TMs) / ST.87 (designs) extension schemas |
| Cost | One-time access fee + provision costs (see contract page) |
| Rate limit | No published per-second / per-day numbers; contract §2.13 disclaims uninterrupted access |
| ToS posture | **§3.2 explicitly prohibits passing data to third parties** — proxy-as-a-service is barred |
| Verdict (zero-infra proxy) | 🔴 **Red** — clean technical surface, but contract terms preclude our model |
| Primary sources | [DPMAconnectPlus overview (EN)](https://www.dpma.de/english/search/data_supply_services/dpmaconnect/index.html) · [Interface spec (DE PDF)](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf) · [Standard contract terms (DE PDF)](https://www.dpma.de/docs/recherche/dienste/dpmaconnectplusvertragsbedingungen.pdf) |

The API is technically attractive — structured `Expertenrecherche` query
syntax (Boolean + 50+ INID-coded fields like `INH=` (proprietor),
`AT=` (application), `IC=` (IPC class), `WAKZ=` (PCT family)), production-grade
XSDs — but every blocker is on the legal side: §3.2 of the standard
contract bars third-party redistribution; §2.1 requires a registered,
non-dynamic IP (fights cloud egress); 1,000-hit-per-query cap with no
documented pagination; signed paper contract by Munich postal mail.

### DPMAregister web UI

| Field | Value |
|---|---|
| Endpoint | `register.dpma.de` |
| Auth | none (CAPTCHA on some endpoints) |
| Format | HTML, CSV/XLSX export (≤cap), PDF for in-register file inspection |
| ToS posture | UI use only; scraping not encouraged |
| Verdict | 🔴 Red — UI scraping is brittle and against the spirit of the access policy |

### DEPATISnet (patent search UI)

| Field | Value |
|---|---|
| Endpoint | `depatisnet.dpma.de` |
| Auth | none |
| Format | HTML, CSV/XLSX (≤100 rows), PDF/TIFF |
| ToS posture | Public UI; scraping not formally addressed |
| Verdict | 🔴 Red — overlaps EPO OPS DE coverage; brittle |

### DPMA backfile bulk

| Field | Value |
|---|---|
| Endpoint | Contract-gated bulk delivery (DPMA datenabgabe) |
| Cost | Paid provision per package |
| Format | WIPO ST.36 patents, ST.86 designs, images |
| Verdict | 🔴 Red — bulk doesn't fit our zero-infra constraint |

## §4 Fees

DPMA publishes separate fee schedules for patents, utility models,
designs, and trademarks. Statutory basis is the **Patentkostengesetz
(PatKostG)** — German Patent Costs Act. DPMAconnectPlus (the bulk API
contract) has its own separate access fee.

- **Official schedule (EN):** [DPMA — Fees and Costs (English)](https://www.dpma.de/english/services/fees/index.html)
- **Official schedule (DE):** [DPMA — Gebühren](https://www.dpma.de/service/gebuehren/index.html)
- **Statutory basis:** [Patentkostengesetz (PatKostG)](https://www.gesetze-im-internet.de/patkostg/) — full text at gesetze-im-internet.de.


## §5 Connector strategy

### What we cover today

- [`patent_client_agents.dpma_statutes`](../../src/patent_client_agents/dpma_statutes/) — bundled SQLite/FTS5 corpus of the six core German IP Acts (PatG, MarkenG, GebrMG, DesignG, UrhG, GeschGehG); manifest entry `DE/DPMA/Statutes`.
- DE patent biblio + family via [`patent_client_agents.epo_ops`](../regional/epo.md) (transitive).

### What we should NOT add (and why)

- **DPMAconnectPlus proxy** — contract §3.2 prohibits passing data to third parties. Even paying the contract fee and signing the paper contract doesn't unlock a proxy model. The "buy access and proxy it" path is foreclosed by the legal terms, not by cost.
- **DEPATISnet scrape** — brittle, UI-only, and redundant with EPO OPS DE coverage at the biblio/family layer.
- **DPMAregister live scrape** — same; CAPTCHA-gated and unsupported as a programmatic interface.

### What we *could* add later

- **`dpma_caselaw`** — BPatG decisions via rechtsprechung-im-internet.de XML feed + BGH via the RiI daily feed. Substantive law / case law layer, no register proxy. See [`connectors/dpma.md`](../connectors/dpma.md) §7 for the asset details.
- **Per-user DPMAconnectPlus access** — if a specific end user has their own signed DPMA contract, a connector could accept their credentials via env and proxy on their behalf. This is the JPO/KIPO BYOK pattern adapted to DPMA. Operationally hostile (paper contract, fixed IP requirement) but legally viable. Low priority pending user demand.

### Next steps

1. Monitor for DPMAregister modernization — the current platform predates the EPO OPS / EUIPO OAuth surfaces and may eventually get a friendlier replacement. No timeline published.
2. Watch BPatG case-law coverage as a substantive-law expansion target — that's redistribution-clean and adds real value for DE IP litigation work.

## §6 Open questions

- **Does paying the contract fee + signing the standard contract unlock any path other than the §3.2-restricted one?** Primary source says the standard contract is what's offered; bespoke terms would require direct negotiation.
- **Are there exceptions for academic / research use?** §3.2's language is categorical; no carve-out in the public-facing contract.
- **DPMAregister modernization timeline.** No primary source found.

## §7 References

Primary sources only.

**Service overviews:**
- [DPMAconnectPlus overview (EN)](https://www.dpma.de/english/search/data_supply_services/dpmaconnect/index.html)
- [DPMA Search & Information Products (EN)](https://www.dpma.de/english/search/data_supply_services/index.html)

**Technical specs:**
- [Interface spec — DPMAconnectPlus (DE PDF)](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf)
- [Legacy DPMAconnect SOAP API spec (DE PDF)](https://www.dpma.de/docs/recherche/dienste/dpmaconnectapibeschreibung.pdf)

**Legal terms:**
- [Standard contract terms — DPMAconnectPlus (DE PDF)](https://www.dpma.de/docs/recherche/dienste/dpmaconnectplusvertragsbedingungen.pdf) — §3.2 (no third-party data transfer)

**Fees:**
- [DPMA fees (EN)](https://www.dpma.de/english/services/fees/index.html)
- Patentkostengesetz (PatKostG) — statutory basis

**Detail survey + wave:**
- [`connectors/dpma.md`](../connectors/dpma.md) — full 211-line asset survey
- [`waves/2026-05-16-registered-ip-discovery/dpma-germany.md`](../waves/2026-05-16-registered-ip-discovery/dpma-germany.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Reconciled the original "Tier 2 paid+contract" framing — the actual blocker is **contract §3.2 (no third-party redistribution)**, not the EUR 200 cost. | [waves/2026-05-16-registered-ip-discovery/dpma-germany.md](../waves/2026-05-16-registered-ip-discovery/dpma-germany.md) |
