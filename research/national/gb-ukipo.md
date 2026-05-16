# UKIPO United Kingdom (GB) — national

**Layer:** national
**Jurisdiction:** GB (WIPO ST.3: GB)
**Issuing body:** UK Intellectual Property Office (an executive agency of the Department for Business and Trade)
**Rights administered:** patent, trademark, registered_design
**Working languages:** English
**Connector status:** **skipped for live registers** (no public API as of 2026-05-16); UKIPO MoPP shipped (substantive law)
**Last verified:** 2026-05-16
**Manifest entry:** [`coverage/sources.yaml` `GB/UKIPO/MoPP`](../../coverage/sources.yaml) (statutes/manual only — `patent_client_agents.ukipo_mopp`)

**Detail surveys:**
- [`connectors/ukipo.md`](../connectors/ukipo.md) — 2026-05 detail survey (125 lines)
- [`waves/2026-05-16-registered-ip-discovery/ukipo-uk.md`](../waves/2026-05-16-registered-ip-discovery/ukipo-uk.md) — 2026-05-16 grounded discovery (IPSUM retirement + One IPO status)

**Higher layers covering this office transitively:**
- **EPO INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — GB patent biblio + family (GB granted via EP designation OR via direct national filing)
- **WIPO Madrid** — international TMs designating GB (UK is a Madrid member); national-only GB TMs are NOT in Madrid
- **WIPO Hague** — international designs designating GB; national-only designs NOT in Hague

---

## §1 Mission

UKIPO is the UK national IP office, separate from the EPO (UK is not in
the unitary patent system but UK granted patents are common via EP
designation pre-Brexit and increasingly via direct national filings
post-Brexit). UKIPO is currently in the middle of a multi-year platform
modernization called "One IPO Transformation" — the old IPSUM Atom feed
was retired and the replacement REST APIs have not been published with
a release timeline.

For agents working on UK IP, EPO INPADOC substitutes for patent biblio +
family. National-only GB TMs and registered designs are gaps with no
proxyable substitute under our zero-infra constraint until the One IPO
APIs ship.

## §2 What's unique here (not covered by higher layers)

- **National-only GB trademarks** — not designated in Madrid IRs
- **National-only GB registered designs** — not designated in Hague IRs
- **UK Patent Office decisions** (Comptroller, Hearing Officer rulings)
- **UK file wrappers** (post-Brexit direct national filings)
- **UK IPEC / Patents Court rulings** — case law layer (covered via `find_case_law` if licensed)
- **UK Manual of Patent Practice (MoPP)** — substantive-law layer (already shipped)

## §3 Programmatic surfaces

### IPSUM Atom feed — **retired 2025-01-22**

Historically the closest UKIPO had to a patent API. Atom-format status
feed. Retired without a direct replacement.

| Field | Value |
|---|---|
| Status | **Retired 2025-01-22** |
| Verdict | 🔴 Red (no longer operational) |
| Primary source | [gov.uk announcement](https://www.gov.uk/government/news) (per the wave research) |

### One IPO Patents Service — launched 2026-03-31 *without an API*

The modernized successor surface. Public launch was 2026-03-31, but
launched **without a public search API**. UKIPO has explicitly stated
"exact timeline for releasing APIs is still to be confirmed."

| Field | Value |
|---|---|
| Status | HTML public UI live; **no public API** |
| Verdict | 🔴 Red (no API surface) |
| Primary source | [`waves/2026-05-16-registered-ip-discovery/ukipo-uk.md`](../waves/2026-05-16-registered-ip-discovery/ukipo-uk.md) |

### One IPO Trade Marks Service — *just entering design phase 2026-27*

Per the wave research, the trade marks track of the One IPO programme is
**just entering design phase in 2026-27**. The current TM surface is
HTML-only at `trademarks.ipo.gov.uk/ipo-tmtext` plus weekly bulk XML on
`data.gov.uk`.

| Field | Value |
|---|---|
| Status | HTML search + weekly bulk XML |
| Verdict | 🔴 Red — no live API; bulk is Shape-E catalog-only |

### One IPO Designs Service — *queued behind trade marks*

Designs phase comes after trade marks in the One IPO transformation
sequence. HTML lookup only at `registered-design.service.gov.uk/find`.

| Field | Value |
|---|---|
| Status | HTML lookup only |
| Verdict | 🔴 Red |

### Weekly bulk XML on data.gov.uk

For trade marks: `data.gov.uk` weekly TMJ XML. Shape-E catalog-only;
doesn't meet our zero-infra constraint.

| Field | Value |
|---|---|
| Endpoint | `data.gov.uk` |
| Auth | none |
| Format | XML weekly |
| ToS | Open Government Licence v3.0 |
| Verdict | 🔴 Red for proxy (bulk-shaped); could be Shape-E catalog connector if user demand justifies it |

## §4 Fee schedule

**Detail file:** *no fee-schedules/gb-ukipo-fees.md yet — queued for future research*
**Official schedule:** [UKIPO fees (gov.uk)](https://www.gov.uk/topic/intellectual-property/fees)
**Statutory basis:** Patents (Fees) Rules 2007 + amendments; Trade Marks (Fees) Rules 2008; Registered Designs Rules 2006

Headline figures **pending dedicated fee research**. UKIPO fees are paid
in GBP. UK left the EU patent + design system (Brexit), so post-2020
filing fees apply only to UK-specific national filings.

## §5 Connector strategy

### What we cover today

- [`patent_client_agents.ukipo_mopp`](../../src/patent_client_agents/ukipo_mopp/) — UK Manual of Patent Practice substantive-law corpus; manifest entry `GB/UKIPO/MoPP`.
- GB patent biblio + family via [`patent_client_agents.epo_ops`](../regional/epo.md) (transitive).

### What we should NOT add (and why)

- **Live UKIPO register scraping** — no stable surface; One IPO is replacing UI/UX iteratively. Any scraper built today gets obsoleted as the transformation rolls out.
- **IPSUM scraper** — retired; nothing to scrape.
- **TM/design HTML scraping** — same brittle pattern; bulk XML is a cleaner fallback but doesn't fit zero-infra.

### What we *should* add when available

- **One IPO Patents Service API** — when announced and published. Worth a discovery pass within 30 days of announcement.
- **One IPO Trade Marks Service API** — same; later in the rollout (2026-27 design phase + however long to ship).
- **UK case law via Find Case Law** — Patents Court / IPEC / Court of Appeal / UKSC. See [`connectors/ukipo.md`](../connectors/ukipo.md) and BACKLOG row 18. Gated on the free R&D computational-use licence.

### Next steps

1. **Quarterly recheck** of [gov.uk/government/organisations/intellectual-property-office](https://www.gov.uk/government/organisations/intellectual-property-office) for One IPO API announcements.
2. **Watch list:** [`BACKLOG.md`](../BACKLOG.md) quarterly watch list — already includes UKIPO One IPO.
3. **Substantive law expansion:** UK statutes (Patents Act 1977, Trade Marks Act 1994, Registered Designs Act 1949, CDPA 1988, Trade Secrets Regs 2018) via legislation.gov.uk CLML/AKN is a viable next step (BACKLOG Tier 2 Rank 10). Would round out UK substantive-law coverage with point-in-time queries (a feature USC fetchers can't match).

## §6 Open questions

- **One IPO API release date** — explicitly TBD per primary source. Recheck quarterly.
- **Find Case Law licensing** — does the free R&D computational-use licence permit our cache-and-serve model via MCP?
- **Designs phase timeline** — sequence is TMs → designs, but TMs hasn't shipped APIs yet; designs is 2+ years out at minimum.

## §7 References

Primary sources only.

**Service surfaces:**
- [UKIPO landing (gov.uk)](https://www.gov.uk/government/organisations/intellectual-property-office)
- [One IPO Patents search](https://www.search.ipo.gov.uk/) (HTML; no API)
- [UK Trade Marks search](https://trademarks.ipo.gov.uk/ipo-tmtext) (HTML)
- [UK Registered Designs search](https://www.registered-design.service.gov.uk/find)

**Bulk:**
- [data.gov.uk — Trade Marks Journal weekly XML](https://www.data.gov.uk/)

**Legal basis:**
- [legislation.gov.uk — Patents Act 1977](https://www.legislation.gov.uk/ukpga/1977/37)
- [legislation.gov.uk — Trade Marks Act 1994](https://www.legislation.gov.uk/ukpga/1994/26)
- [legislation.gov.uk — Registered Designs Act 1949](https://www.legislation.gov.uk/ukpga/1949/88)

**Fees:**
- [gov.uk — IP fees](https://www.gov.uk/topic/intellectual-property/fees)

**Detail survey + wave:**
- [`connectors/ukipo.md`](../connectors/ukipo.md) — full detail survey
- [`waves/2026-05-16-registered-ip-discovery/ukipo-uk.md`](../waves/2026-05-16-registered-ip-discovery/ukipo-uk.md)

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Reconciled the original "Tier 2; APIs coming H2-2025/2026" framing — **IPSUM retired 2025-01-22; One IPO Patents Service launched 2026-03-31 without an API; trade marks track just entering design phase 2026-27**. | [waves/2026-05-16-registered-ip-discovery/ukipo-uk.md](../waves/2026-05-16-registered-ip-discovery/ukipo-uk.md) |
