# KIPO Korea (KR) — national

**Layer:** national
**Jurisdiction:** KR (WIPO ST.3: KR)
**Issuing body:** Korean Intellectual Property Office (특허청 / Korean: T'eukheoch'eong)
**Rights administered:** patent, utility_model, trademark, design
**Working languages:** Korean (primary); English (partial — KIPRIS English UI, KPA machine-translated abstracts)
**Connector status:** planned (BYOK architecture)
**Last verified:** 2026-05-16
**Manifest entry:** not yet listed in `coverage/sources.yaml`

**Detail surveys:**
- [`connectors/kipo.md`](../connectors/kipo.md) — 2026-05 asset-by-asset survey (182 lines; 15 assets including KIPRIS Plus API, IPTAB, K-PION, KSVS, plant varieties, GI registry, Patent Act statutes)
- [`waves/2026-05-16-registered-ip-discovery/kipo-kipris-plus.md`](../waves/2026-05-16-registered-ip-discovery/kipo-kipris-plus.md) — 2026-05-16 grounded discovery on KIPRIS Plus API

**Higher layers covering this office transitively:**
- **EPO INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — KR patent biblio + family; legal events coverage depends on whether KR is in INPADOC's ~50-office legal-events subset (verify per query)
- **WIPO PATENTSCOPE** — PCT applications filed at KIPO as receiving office; PCT applications designating KR as their national-phase target
- **WIPO Madrid** — international TMs designating KR (KR is a Madrid member); national-only KR TMs are NOT in Madrid
- **WIPO Hague** — international designs designating KR (KR joined the Hague System 2014-07-01); national-only KR designs are NOT in Hague

---

## §1 Mission

KIPO is one of the IP5 offices — the five largest patent offices that
collectively handle ~80% of global patent applications (USPTO, EPO, JPO,
KIPO, CNIPA). KIPO administers all four traditional Korean registered IP
rights from one agency, and the underlying online search system
(KIPRIS) is operated by a sister agency (Korea Institute of Patent
Information, KIPI). Korea is a top global jurisdiction for utility model
filings — a distinct right type from patents that KIPO administers
alongside its patent register.

For agents working on Korean prior art, ownership, prosecution, or
post-grant review, KIPO is the authoritative source. EPO INPADOC
substitutes for KR patent biblio + family at the regional layer, but
prosecution depth, native-language full text, utility models, and
trademark/design data are only available directly from KIPO.

## §2 What's unique here
- **Korean-language full text** of patents and utility models (EPO OPS full text covers ~30 collections; KR patent full text typically lives in KIPRIS only).
- **Real-time KR patent prosecution status** (vs. INPADOC's lag).
- **Utility models** — Korea is a major UM jurisdiction; UMs are a distinct right not covered by EP-only systems.
- **National-only KR trademarks** — Madrid IRs designating KR are visible via Madrid, but pure KR-only filings live only in KIPO.
- **National KR designs not filed via Hague** — pre-2014 designs and post-2014 national-only filings live only in KIPO.
- **IPTAB decisions** (Korean Intellectual Property Trial and Appeal Board) — Korea's post-grant tribunal; analogous to USPTO PTAB.
- **Machine-translated English abstracts (KPA)** — a separate KIPRIS Plus dataset for non-Korean readers.

## §3 Programmatic surfaces

### KIPRIS Plus REST API

| Field | Value |
|---|---|
| Endpoint | `http://kipo-api.kipi.or.kr/openapi/service/{patUtliInfoSearchService,trademarkInfoSearchService,designInfoSearchService}/{getWordSearch,getAdvancedSearch,…}` |
| Auth | Per-user API key (one key per member account) — passed as `serviceKey` query parameter |
| Format | **XML only** (no JSON variant on the English portal) |
| Rate limit | Two tiers (Development — free quota; Operation — paid, "carefully reviewed and approved on a limited basis"). See the KIPRIS Plus terms for the current quota and price. |
| ToS posture | **Per-user only** — §11 forbids sharing Authentication Keys with others |
| Verdict (zero-infra proxy) | 🟡 **Yellow** — BYOK architecture viable; shared-key proxy is ToS-prohibited |
| Primary sources | [Service Introduction (EN)](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024) · [Terms of use (EN) §11](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030) · [Patent-Utility doc page (EN)](https://plus.kipris.or.kr/eng/data/clas/DBII_000000000000001/view.do?menuNo=310000) |

The API itself is technically excellent: REST with `getWordSearch` (free-text)
and `getAdvancedSearch` (structured) operations for each right; ~46 OpenAPI
services per the 2019 KIPRIS leaflet ([PDF](https://plus.kipris.or.kr/sampledata/KIPRISPlus%20leaflet.pdf));
1948-onward backfile per [WIPO Inspire](https://inspire.wipo.int/kipris).
The blocker is purely contractual — ToS §11 forbids one-key-many-users.

### `data.go.kr` mirror

The same KIPRIS endpoints are also listed on Korea's national open data
portal `data.go.kr` with English UI:

- [Trademark Information Search Service (service 15043964)](https://www.data.go.kr/en/data/15043964/openapi.do)
- [Design Information Search Service (service 15043970)](https://www.data.go.kr/en/data/15043970/openapi.do)
- [Patent-Utility Service (service 15065437)](https://www.data.go.kr/data/15065437/openapi.do)

Alternate registration path if KIPRIS Plus signup blocks on Korean
identity verification (i-PIN / KR mobile carrier). Whether `data.go.kr`
registration succeeds without a Korean phone is **not confirmed by
primary source** ([wave research §2](../waves/2026-05-16-registered-ip-discovery/kipo-kipris-plus.md)).

### KIPRIS web UI scraping

Not recommended — the public KIPRIS UI is anti-scrape-protected and the
API path above is the supported method. Verdict: 🔴 red.

### K-PION (B2B office portal)

Inter-office only (not available to private developers per the existing
detail survey [`connectors/kipo.md`](../connectors/kipo.md)). Verdict: 🔴 red.

## §4 Fees

KIPO charges in KRW across patent, utility model, design, and trade
mark — filing, search, examination, grant, and renewal categories,
with discount tiers for small entities and individual applicants.
KIPRIS Plus API access has its own separate fee structure (development
tier vs. operation tier).

- **KIPO fee landing (EN):** [KIPO main portal](https://www.kipo.go.kr/en/MainApp) — navigate via the service portal.
- **KIPRIS Plus access fees (Korean):** [KIPRIS Plus fee notice](https://plus.kipris.or.kr/portal/main/contents.do?menuNo=210168)
- **KIPRIS Plus EN service introduction:** [KIPRIS Plus service introduction](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024)


## §5 Connector strategy

### What we cover today

Nothing yet — KIPO is not in `coverage/sources.yaml` as of 2026-05-16.
KR patent biblio + family is currently accessed transitively via
[`patent_client_agents.epo_ops`](../regional/epo.md).

### What we should add

**Connector: `patent_client_agents.kipo_kipris` (planned, BYOK)** — see
[`BACKLOG.md`](../BACKLOG.md) original entry "Tier 1 Rank 9-10".
Reconciled architecture: env-gated per-user keys, mirroring the JPO /
EUIPO / IP Australia pattern.

**Tools to surface (initial scope):**
- `search_kipo_patents(query, ...)` — KIPRIS Plus patent-utility word/advanced search
- `get_kipo_patent(application_or_publication_number)` — bibliographic + drawing access
- `search_kipo_trademarks(query, ...)` — trademark word/advanced search
- `get_kipo_trademark(application_or_registration_number)` — bibliographic + Vienna-class lookup
- `search_kipo_designs(query, ...)` — design word/advanced search
- `get_kipo_design(application_or_registration_number)` — bibliographic + drawing access

**Auth model:**
- Env var: `KIPO_KIPRIS_API_KEY` — supplied per deployment / per end user
- Tool registration gated on env var presence (CONNECTOR_STANDARDS.md §7.x pattern, already used for JPO_API_USERNAME/PASSWORD and IPAUSTRALIA_CLIENT_ID/SECRET)
- On the hosted demo (mcp.patentclient.com) the KIPO tools simply don't register without a key — honest and ToS-clean

### What we should NOT add

- **Shared-key hosted proxy** — ToS §11 explicitly prohibits sharing keys with others; doing this would be a contract violation.
- **KIPRIS UI scrape** — brittle and against KIPO's data-access policy; the API is the supported path.
- **K-PION** — inter-office only.

### Next steps

1. Verify foreign-developer signup path: register at KIPRIS Plus EN portal and `data.go.kr` to confirm whether Korean phone / i-PIN is mandatory. Cite `kiprisplus@kipi.or.kr` as the documented manual workaround.
2. Once a working `serviceKey` is obtained, smoke-test `patUtliInfoSearchService/getWordSearch`, `trademarkInfoSearchService/getWordSearch`, `designInfoSearchService/getWordSearch` to confirm the XML response shape.
3. Design `patent_client_agents.kipo_kipris` package per the JPO connector pattern (`patent_client_agents.jpo` is the closest existing template — BYOK + XML response parsing).

## §6 Open questions

- **Foreign-developer signup path.** Does `data.go.kr` registration succeed without a Korean phone? Primary source ambiguous ([Terms of use §5](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030)).
- **Operation-tier approval criteria.** What does "carefully reviewed and approved on a limited basis" mean in practice? Lead time? Conditions?
- **Redistribution beyond per-user proxy.** Does serving KIPRIS data via our MCP tool (even with BYOK) trigger ToS §11's redistribution language? Legal review recommended before any cache-and-serve pattern.
- **JSON variant.** Is JSON output available on operation tier or only XML?
- **Total document count.** No primary-source quote for current totals — relevant for capacity planning.

## §7 References

Primary sources only.

**Portals + docs:**
- [KIPRIS Plus EN portal](https://plus.kipris.or.kr/eng/main.do)
- [KIPRIS Plus EN service catalog](https://plus.kipris.or.kr/eng/data/service/List.do?subTab=SC001&menuNo=300100)
- [KIPRIS Plus EN registration](https://plus.kipris.or.kr/eng/member/joinView.do?menuNo=300028)
- [KIPO English homepage](https://www.kipo.go.kr/en/)
- [KIPRIS English homepage](http://eng.kipris.or.kr/enghome/kipris/kipris.jsp)

**Terms + service introduction:**
- [Service Introduction (EN)](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024) — "11 types of data through API"
- [Terms of Use (EN)](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030) — §5 (membership), §11 (Authentication Keys, no sharing)

**API documentation:**
- [Patent-Utility Model Publications doc (EN)](https://plus.kipris.or.kr/eng/data/clas/DBII_000000000000001/view.do?menuNo=310000)
- [REST OpenAPI utilization guide (KR)](https://plus.kipris.or.kr/portal/bbs/view.do?nttId=132&bbsId=B0000001&menuNo=200015)
- [data.go.kr — Trademark Information Search Service (EN)](https://www.data.go.kr/en/data/15043964/openapi.do)
- [data.go.kr — Design Information Search Service (EN)](https://www.data.go.kr/en/data/15043970/openapi.do)
- [data.go.kr — Patent-Utility Service](https://www.data.go.kr/data/15065437/openapi.do)
- [KIPRIS Plus 2019 leaflet (PDF)](https://plus.kipris.or.kr/sampledata/KIPRISPlus%20leaflet.pdf)

**WIPO context:**
- [WIPO Inspire — KIPRIS profile](https://inspire.wipo.int/kipris) — 1948-onward backfile confirmation

**Detail survey (older, pre-2026-05-16):**
- [`connectors/kipo.md`](../connectors/kipo.md) — full 15-asset survey

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-16 | Initial synopsis | Distilled from [`connectors/kipo.md`](../connectors/kipo.md) + [`waves/2026-05-16-registered-ip-discovery/kipo-kipris-plus.md`](../waves/2026-05-16-registered-ip-discovery/kipo-kipris-plus.md). Reconciled BYOK architecture as required by ToS §11. |
