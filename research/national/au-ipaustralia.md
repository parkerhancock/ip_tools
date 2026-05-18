# IP Australia (AU) — national

**Layer:** national
**Jurisdiction:** AU (WIPO ST.3: AU)
**Issuing body:** IP Australia (an executive agency under the Australian Department of Industry, Science and Resources)
**Rights administered:** patent (standard + innovation), trademark, registered_design, plant_breeders_rights
**Working languages:** English
**Connector status:** **active** (cleanest BYOK pattern in the catalog)
**Last verified:** 2026-05-16
**Manifest entries:**
- [`AU/IPAustralia/Patents`](../../coverage/sources.yaml) — `patent_client_agents.ip_australia_patents`
- [`AU/IPAustralia/Trademarks`](../../coverage/sources.yaml) — `patent_client_agents.ip_australia_trademarks`
- [`AU/IPAustralia/Designs`](../../coverage/sources.yaml) — `patent_client_agents.ip_australia_designs`
- [`AU/IPAustralia/Bulk`](../../coverage/sources.yaml) — `patent_client_agents.ip_australia_bulk` (IP RAPID catalog)

**Detail surveys:**
- [`connectors/ip_australia.md`](../connectors/ip_australia.md) — 2026-05 detail survey (192 lines)
- [`connectors/ip_australia_endpoints.md`](../connectors/ip_australia_endpoints.md) — full endpoint inventory (334 lines)

**Higher / sibling layers carrying overlapping data:**
- **EPO INPADOC** — AU patent biblio + family
- **WIPO Madrid** — international TMs designating AU (AU is a Madrid member since 2001)
- **WIPO Hague** — international designs designating AU (AU is a Hague member since 2022)

---

## §1 Mission

IP Australia is widely regarded as one of the cleanest national IP office
data surfaces globally — modern OAuth 2.0 REST APIs across all four IP
rights from one agency, plus a CC-BY 4.0 bulk catalog (IP RAPID) on
data.gov.au, all under a single agency umbrella. The BACKLOG's original
verdict called it "**likely the easiest connector on the entire roadmap**" —
which proved correct, and the resulting `ip_australia_*` packages
are now the canonical template for BYOK national-office connectors in
this codebase.

Our KIPO BYOK design (and any future national-office BYOK work) should
mirror this pattern.

## §2 What's unique here
- **AU patent prosecution status** in real time
- **AU file wrappers**
- **National-only AU trademarks** — not in Madrid IRs
- **National-only AU registered designs** — not in Hague IRs (pre-2022 designs and post-2022 non-Hague filings)
- **Plant Breeder's Rights** — AU operates a PBR register; this right type isn't covered by EP/EUIPO/INPADOC
- **AU innovation patents** — though innovation patents were closed for new filings 2021-08-26 (legacy register remains active)
- **AU IP RAPID bulk data** — weekly tables across all four rights, CC-BY 4.0

## §3 Programmatic surfaces

### IP Australia Patent Search API

| Field | Value |
|---|---|
| Endpoint | `https://api.business.gov.au/ip-australia/patent-search/v1/` |
| Auth | OAuth2 client credentials — `IPAUSTRALIA_CLIENT_ID` + `IPAUSTRALIA_CLIENT_SECRET` |
| Format | JSON (OpenAPI 3 spec published) |
| Rate limit | Default API gateway throttle; published in developer portal |
| ToS posture | Permissive — supports programmatic / proxy use with proper credentials |
| Verdict (zero-infra proxy) | 🟢 **Green** — operational |
| Primary source | [IP Australia API developer page](https://www.ipaustralia.gov.au/about-us/working-with-us/digital-and-data/ip-australia-application-programming-interfaces-apis) |

### IP Australia Trade Mark Search API

Same OAuth infrastructure, separate scope. Endpoint pattern:
`https://api.business.gov.au/ip-australia/trade-mark-search/v1/`.

### IP Australia Design Search API

Same pattern: `https://api.business.gov.au/ip-australia/design-search/v1/`.

### IP RAPID bulk catalog

| Field | Value |
|---|---|
| Endpoint | `https://data.gov.au/data/dataset/ip-rapid` |
| Auth | none |
| Format | CSV / parquet (weekly tables across all four rights) |
| License | **CC-BY 4.0 International** (corrected from the older "CC-BY 2.5 AU" research) |
| Verdict | 🟢 Green for Shape E catalog connector (`ip_australia_bulk`); bulk shape, but legally clean |

### AustLII for APO hearings + Federal Court IP

| Field | Value |
|---|---|
| Endpoint | AustLII SINO CGI |
| Auth | none |
| Verdict | 🟡 Yellow — niche; case-law layer; deferred per BACKLOG until tribunal coverage demand emerges |

## §4 Fees

IP Australia publishes separate fee schedules for patents, trade marks,
and designs (charged in AUD).

- **Patents:** [IPA — Patents timeframes and fees](https://www.ipaustralia.gov.au/patents/timeframes-and-fees) (filing, examination, acceptance, annuities yrs 4–20, excess-claim fees)
- **Trade marks:** [IPA — Trade marks timeframes and fees](https://www.ipaustralia.gov.au/trade-marks/timeframes-and-fees) (application per class with picklist vs free-text tiers, renewal)
- **Designs:** [IPA — Designs timeframes and fees](https://www.ipaustralia.gov.au/designs/timeframes-and-fees) (filing, registration, renewal)
- **Renewal tables:** [Renewals year-by-year](https://www.ipaustralia.gov.au/manage-my-ip/how-to-renew-my-ip-right)
- **Statutory basis:** [Patent Regulations 1991 — Schedule 7 (Fees)](http://classic.austlii.edu.au/au/legis/cth/consol_reg/pr1991218/sch7.html)

*(frozen at the date written; consult the official URLs above for current figures).*

## §5 Connector strategy

### What we cover today

- Three OAuth-keyed register connectors (patents/TMs/designs) — env-gated on `IPAUSTRALIA_CLIENT_ID` + `IPAUSTRALIA_CLIENT_SECRET`
- One bulk-catalog connector (IP RAPID) — no auth required
- All four rights, complete coverage modulo the AustLII case-law deferral

### What we *might* improve later

- **AustLII case-law layer** (`au_austlii`) — APO hearings + Federal Court IP. BACKLOG Tier 2 stretch. Defer until tribunal coverage demand emerges.
- **PBR-specific tools** — Plant Breeder's Rights is a distinct right type carried by IP Australia. Currently treated as out-of-scope for the registered-IP search shape; might warrant its own tool if user demand emerges.

### What we should NOT add

- Nothing — IP Australia is in good shape. The cleanest national-office surface we operate.

### Template value

**IP Australia is the canonical BYOK template** for the rest of the
codebase. The pattern:
1. Env-gated tool registration (tools only mount when both `*_CLIENT_ID` and `*_CLIENT_SECRET` are set)
2. OAuth2 client-credentials flow with token caching
3. Per-right modular packages sharing a common `ip_australia_common` scaffold
4. Manifest entries one per right
5. The same pattern applies to: EUIPO (existing), JPO (existing), KIPO (planned)

## §6 Open questions

- **IP RAPID schema stability** — confirmed CC-BY 4.0 International (corrected from older CC-BY 2.5 AU); data dictionary not yet inspected programmatically.
- **PBR-specific endpoint scope** — does the existing API surface include PBR, or is it a separate (potentially undocumented) endpoint?
- **Future Hague-system integration** — AU joined Hague in 2022; how do designations flow through the AU design register?

## §7 References

Primary sources only.

**APIs:**
- [IP Australia developer page](https://www.ipaustralia.gov.au/about-us/working-with-us/digital-and-data/ip-australia-application-programming-interfaces-apis)
- [api.business.gov.au — IP Australia APIs](https://api.business.gov.au/) — gateway

**Fees:**
- [Patent timeframes and fees](https://www.ipaustralia.gov.au/patents/timeframes-and-fees)
- [Trade mark timeframes and fees](https://www.ipaustralia.gov.au/trade-marks/timeframes-and-fees)
- [Design timeframes and fees](https://www.ipaustralia.gov.au/designs/timeframes-and-fees)
- [Renewals](https://www.ipaustralia.gov.au/manage-my-ip/how-to-renew-my-ip-right)
- [Patent Regulations 1991 Schedule 7 (AustLII)](http://classic.austlii.edu.au/au/legis/cth/consol_reg/pr1991218/sch7.html)

**Bulk + open data:**
- [IP RAPID on data.gov.au](https://data.gov.au/data/dataset/ip-rapid)

**Detail surveys + fee research:**
- [`connectors/ip_australia.md`](../connectors/ip_australia.md) — main detail survey
- [`connectors/ip_australia_endpoints.md`](../connectors/ip_australia_endpoints.md) — endpoint inventory

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis. Confirmed IP RAPID licence is **CC-BY 4.0 International** (corrected from older CC-BY 2.5 AU). Noted the 2024 patent fee-structure shifts (excess-claim fees timing and renewal curve restructure); current figures are on the official schedule. | — |
