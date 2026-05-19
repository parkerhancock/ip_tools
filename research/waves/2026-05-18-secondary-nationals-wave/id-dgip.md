# DGIP Indonesia (ID) — Patents, Utility Models, Trademarks, Designs, Copyright API Discovery

**Date:** 2026-05-18
**Scope:** Determine whether the Direktorat Jenderal Kekayaan
Intelektual (DGIP / DJKI — Directorate General of Intellectual
Property under the Ministry of Law of the Republic of Indonesia)
exposes a public, queryable REST/JSON/XML API that we can proxy at
runtime, zero infrastructure on our side. Bulk dumps and HTML-only
surfaces would be a **red** verdict; per-user BYOK with personal
credentials would be yellow; undocumented-but-unauthenticated JSON
that mirrors the SE/PRV or FI/PRH pattern would be green.

**TL;DR:** **Red — no public API.** DGIP's consumer register surface
is [`pdki-indonesia.dgip.go.id`](https://pdki-indonesia.dgip.go.id/)
("Pangkalan Data Kekayaan Intelektual" — the Intellectual Property
Database). The hostname is **hard-walled behind an Imperva /
Incapsula (Distil Networks) bot-management challenge** at the
TLS-edge — every probe in this discovery returned a 200/403 with a
~200–1,000-byte HTML iframe redirecting to
`/_Incapsula_Resource?...` regardless of User-Agent, Accept-Language,
Sec-Fetch-* headers, or path. The same wall covers every transaction
subdomain probed (`merek.`, `paten.`, `desainindustri.`, `hakcipta.`,
`ig.`, `dtlst.`, `rd.`, `ekii.`, `dashboardmonitoring.dgip.go.id`,
each returning a 403 with the same Incapsula iframe). The
`pdki-indonesia` host additionally proxies through Alibaba Cloud ESA,
adding a second bot layer in front of the application. There is
**no documented REST/JSON/XML API**, **no developer portal**, **no
`/api/`, `/v1/`, `/_next/data/`, `/graphql` or equivalent path
reachable** (all return the same Incapsula challenge HTML), and
**zero entries for Indonesia in the [WIPO IP API Catalog](https://apicatalog.wipo.int/)**
(probed 2026-05-18: 179 total APIs across DPMA, EPO, EUIPO, IP
Australia, JPO, MOIP KOREA, QAZ, UPRP, USPTO, WIPO — zero from
DGIP/DJKI). Indonesia's open-data portal
[`data.go.id`](https://data.go.id/) has **no DGIP datasets** —
searches for "DJKI" and "kekayaan intelektual" return only
municipal/provincial aggregate counts (e.g. "Jumlah HKI di
Kabupaten Majalengka"), not register data. Bulk gazettes ("Berita
Resmi Paten / Merek / Desain Industri / Indikasi Geografis / Hak
Cipta / Lisensi Paten / Madrid Protokol") are published as HTML
+ PDF catalogs on [`dgip.go.id/berita-resmi/...`](https://dgip.go.id/),
not as machine-readable feeds. ID patents are already reachable
transitively via **WIPO PATENTSCOPE** (Indonesia national
collection: **193,561 records**, biblio 1987-12-02 → 2025-12-08,
latest update 2026-01-22 — confirmed against the
[PATENTSCOPE Data Coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf))
and via the **EPO OPS / INPADOC** layer (Indonesia is a PCT
contracting state since 1997 and a Paris Convention member);
international TM filings designating ID via **WIPO Madrid Monitor**
(ID acceded to the Madrid Protocol 2017-10-02, in force 2018-01-02
— [WIPO Madrid notification 217](https://www.wipo.int/wipolex/en/treaties/notifications/details/treaty_madridp-gp_217)).
**Indonesia is not currently a Hague System member** (it was the
first Asian Hague member in 1950 but withdrew in 2010; a draft
Presidential Regulation for re-accession was submitted to the
Indonesian Parliament 2024-08-06 but has not been ratified as of
2026-05). The genuine national-only gaps — **ID utility models
("paten sederhana" under [UU No. 13 Tahun 2016](https://peraturan.bpk.go.id/Home/Details/37536)
as amended by [UU No. 65 Tahun 2024](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024)),
ID-only national TMs, ID-only national designs, all ID copyright
and trade-secret records, ID geographical indications, and full
prosecution detail (file history, examiner notes, opposition
proceedings)** — have **no programmatic surface we can proxy**.

**Verdict: 🔴 Red.** Bot-walled HTML SPA, no documented API, no
open-data feed, zero WIPO Catalog presence, no third-party wrapper
on GitHub/PyPI/GitLab (confirmed via web search 2026-05-18).
Substantive law is reachable cleanly via primary-source statute
hosts — [`peraturan.bpk.go.id`](https://peraturan.bpk.go.id/) and
[`jdih.dgip.go.id`](https://jdih.dgip.go.id/) — which is a **green**
adjunct corpus if we want to ship ID substantive-law coverage,
mirroring the `ipo_in_statutes` / `dpma_statutes` / `legifrance_ip`
pattern. The register-side proxy story is closed for the
foreseeable future.

---

## 1. Endpoint

DGIP's surface is sharded across institutional, register, transaction,
and ancillary hosts. Each was probed 2026-05-18.

| Surface | Host | Right(s) | Shape | Probe result |
|---|---|---|---|---|
| DGIP institutional | [`dgip.go.id`](https://dgip.go.id/) | content + gazettes | classic PHP/CMS HTML | 200 OK, 75 KB; gazette index links visible |
| PDKI register search | [`pdki-indonesia.dgip.go.id`](https://pdki-indonesia.dgip.go.id/) | patent / utility model / TM / design / copyright / GI | SPA, Alibaba Cloud ESA + Imperva | 200 OK with 212-byte Incapsula iframe, no application HTML reachable to anonymous curl |
| `/search?type=trademark` | same | TM | (same) | 200 OK with 1,048-byte Incapsula iframe |
| `/api`, `/api/v1`, `/api/search/trademarks`, `/_next/data` | same | — | (same) | All return 200 OK with the 1,047–1,055-byte Incapsula iframe — indistinguishable response shape, suggesting catch-all wildcard at the WAF/CDN edge |
| Trademark e-filing | [`merek.dgip.go.id`](https://merek.dgip.go.id/) | TM filing | (Incapsula-walled HTML) | 403 Forbidden, 884-byte Incapsula iframe |
| Patent e-filing | [`paten.dgip.go.id`](https://paten.dgip.go.id/) | patent filing | (same) | 403, 885-byte Incapsula iframe |
| Design e-filing | [`desainindustri.dgip.go.id`](https://desainindustri.dgip.go.id/) | design filing | (same) | 403, 884-byte Incapsula iframe |
| Copyright e-filing | [`hakcipta.dgip.go.id`](https://hakcipta.dgip.go.id/) | copyright filing | (same) | 403, 884-byte Incapsula iframe |
| GI e-filing | [`ig.dgip.go.id`](https://ig.dgip.go.id/) | geographical indication filing | (same) | 403, 885-byte Incapsula iframe |
| IC layout-design e-filing | [`dtlst.dgip.go.id`](https://dtlst.dgip.go.id/) | "Desain Tata Letak Sirkuit Terpadu" | (same) | 403, 884-byte Incapsula iframe |
| Trade secret recordal | [`rd.dgip.go.id`](https://rd.dgip.go.id/) | "Rahasia Dagang" — trade-secret licence recordal | (same) | 403, 884-byte Incapsula iframe |
| e-KII unified portal | [`ekii.dgip.go.id`](https://ekii.dgip.go.id/) | unified filing front door | (same) | 403, 884-byte Incapsula iframe |
| Performance dashboard | [`dashboardmonitoring.dgip.go.id`](https://dashboardmonitoring.dgip.go.id/) | aggregated stats | HTML | 403, 884-byte Incapsula iframe |
| Legal-information portal | [`jdih.dgip.go.id`](https://jdih.dgip.go.id/) | DGIP statutes catalogue | HTML | TLS handshake failed on direct probe; reachable via search-engine cache |
| Patent registry (operational) | [`sipaten.dgip.go.id`](https://sipaten.dgip.go.id/) | internal patent system | (no public surface) | TLS handshake failed on direct probe |
| English face | [`en.dgip.go.id`](https://en.dgip.go.id/) | English content | — | TLS handshake failed on direct probe |
| IP marketplace | [`marketplace.dgip.go.id`](https://marketplace.dgip.go.id/) | TM/patent transfer listings | HTML | not probed (not in scope) |
| Traditional knowledge | [`kik.dgip.go.id`](https://kik.dgip.go.id/) / [`kikomunal-indonesia.dgip.go.id`](https://kikomunal-indonesia.dgip.go.id/) | traditional knowledge | HTML | not probed (Kekayaan Intelektual Komunal — communal IP, niche) |

The Incapsula iframe pattern is consistent: every reachable host
returns a `<script src="/_Incapsula_Resource?SWJIYLWA=..."></script>`
+ iframe wrapper that bounces the browser through a JS challenge.
The PDKI host additionally injects a second script tag
(`/mite-Tyrants-to-leasure-an-Old-not-shout-Conumbe`), which is the
Distil/Incapsula behavioral-fingerprinting layer. Solving the
challenge programmatically would require running the JS in a
headless browser; that is a per-user runtime cost, not a zero-infra
proxy. Even with a headless solver, the resulting requests are not
documented as a "public API" surface — they are SPA-internal calls
intended for browser consumption, with no published versioning or
ToS.

---

## 2. Auth

There is **no API to authenticate against.** PDKI search itself is
described as anonymous-public in DGIP's own usage guide
([PDKI usage tutorial PDF, ekii.dgip.go.id](https://ekii.dgip.go.id/uploads/files/lessons87/61f97429e8056f85533a98f4cbc1fa79.pdf)) —
"users do not need to log in" — but this refers to the HTML browser
UI, not to a programmatic interface. The filing portals
(`merek.`, `paten.`, etc.) sit behind the same Incapsula wall plus an
application-level login for filing accounts; that's a transactional
identity gate, not a search surface.

No primary source advertises:

- An API key or OAuth client-credentials flow.
- A developer registration portal under `dgip.go.id` or
  `pdki-indonesia.dgip.go.id`.
- A paid-data agreement equivalent to DPMA's *DPMAconnectPlus* or
  KIPO's *KIPRIS Plus*.
- Any developer-friendly accommodation.

Confirmed by absence: the [WIPO IP API Catalog](https://apicatalog.wipo.int/)
lists 179 office APIs as of 2026-05-18. Probe payload
`GET https://apicatalog.wipo.int/api/apis?size=300` returned 0 hits
filtered against `indonesia`, `dgip`, `dirjenki`, `djki`, `kekayaan`,
or country code `id`. The catalog providers are exactly DPMA, EPO,
EUIPO, IP Australia, JPO, MOIP KOREA, QAZ, UPRP, USPTO, and WIPO —
the same closed list returned on the AT/OPA probe.

---

## 3. Query Language

**Not applicable.** PDKI is a browser SPA whose URL grammar
(`/search?type=trademark&keyword=DID2020047323&page=1`) implies
client-side state but does not document a query DSL. Even if the
Incapsula wall could be cleared, the SPA's internal fetch calls are
unversioned, undocumented, and intended for in-browser use only.
There is no Lucene grammar (as INPI France offers), no Boolean
field grammar (as DPMA's `Expertenrecherche` offers), no published
JSON schema, no GraphQL schema introspection endpoint reachable.

---

## 4. Pagination

**Not applicable.** No reachable API.

---

## 5. Response Shape

**Not applicable.** No reachable API.

---

## 6. Coverage Scope

### What DGIP would expose if it had an API

Indonesia's substantive IP system covers seven rights, all
administered by DGIP under the Ministry of Law:

- **Invention patents** ("paten") — 20-year term, [UU No. 13 Tahun 2016](https://peraturan.bpk.go.id/Home/Details/37536) as amended by [UU No. 65 Tahun 2024](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024) (third amendment, signed 2024-10-28).
- **Simple patents** ("paten sederhana") — a **distinct ID-specific subtype**, 10-year term, lower inventiveness threshold; covers new products and processes that are industrially applicable but do not meet full inventive-step requirements. This is the rights-class most analogous to a German Gebrauchsmuster or Chinese utility model, but it is administered as a patent subtype under the same law, not a separate register.
- **Trademarks and Geographical Indications** — [UU No. 20 Tahun 2016](https://peraturan.bpk.go.id/Details/37595/uu-no-20-tahun-2016).
- **Industrial Designs** — [UU No. 31 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44893/uu-no-31-tahun-2000).
- **Copyright** — [UU No. 28 Tahun 2014](https://peraturan.bpk.go.id/Details/38690/uu-no-28-tahun-2014). Registration is optional/declarative, not constitutive.
- **Trade Secrets** — [UU No. 30 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44896). No public register; only licence-recordal events go through DGIP at [`rd.dgip.go.id`](https://rd.dgip.go.id/).
- **Layout-Designs of Integrated Circuits** — [UU No. 32 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44897). Niche register.
- **Plant Variety Protection** — [UU No. 29 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44894). Administered separately by the Ministry of Agriculture's PVT office (not DGIP), but treated together in the WIPO Lex profile for Indonesia.

### What's reachable transitively

- **PATENTSCOPE Indonesia national collection** — **193,561 records**, biblio data 1987-12-02 → 2025-12-08, abstracts 1991-04-18 → 2025-12-08, latest update 2026-01-22. Confirmed against the [PATENTSCOPE Data Coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf). No chemical-data indexing, no document images, no OCR. Includes both `paten` and `paten sederhana` filings (the source data does not distinguish in the PATENTSCOPE columns; the application-type field carries the subtype). About **~5 months of recency drift** between latest biblio (2026-01-22) and end-of-coverage range (2025-12-08) — newer filings are in the system but not yet harvested into PATENTSCOPE.
- **EPO OPS / INPADOC** — Indonesia is a Paris Convention member and PCT contracting state since 1997-09-05 ([WIPO PCT contracting states](https://www.wipo.int/pct/en/pct_contracting_states.html)). INPADOC coverage includes ID national filings and ID-designated PCT national-phase entries at biblio + family + legal-events fidelity. Reachable via `patent_client_agents.epo_ops`.
- **ASEAN IP Register** ([`asean-ipregister.wipo.net`](https://asean-ipregister.wipo.net/) / [`ip-register.aseanip.org`](https://ip-register.aseanip.org/)) — relaunched 2023 from the older "ASEAN PATENTSCOPE" (2017). Covers 9 ASEAN members including Indonesia. **Built on WIPO's wopublish platform** (an Apache Wicket / Java Server stack — jsessionid + IBehaviorListener URLs in the probe output, classic Wicket signature). Browser-only — no documented REST API, returns server-rendered HTML on each interaction. Notable detail: per the [ASEAN-IPR public rollout announcement](https://www.aseanip.org/home/2023/03/03/public-rollout-of-asean-patentscope-service), **Indonesia hosts the regional database server itself** — i.e. ID is the data backbone for the ASEAN cross-office register.
- **WIPO Madrid Monitor** — ID joined Madrid Protocol 2017-10-02, in force 2018-01-02 ([WIPO Madrid notification 217](https://www.wipo.int/wipolex/en/treaties/notifications/details/treaty_madridp-gp_217)). International TM IRs designating ID are reachable at WIPO; ID-only national TMs are not.
- **WIPO Hague** — Indonesia is **NOT** currently a Hague member. It was the first Asian member in 1950 but withdrew in 2010. A draft Presidential Regulation for re-accession was submitted to the Indonesian Parliament 2024-08-06; not yet ratified. International design IRs designating ID are **not** available via Hague today.
- **WIPO Global Brand Database** and **Global Design Database** — neither carries ID-only national collections; only the Madrid / Hague international slices.
- **WIPO Lex** — primary-source IP statutes for ID at [`https://www.wipo.int/wipolex/en/profile.jsp?code=ID`](https://www.wipo.int/wipolex/en/profile.jsp?code=ID). Catalogs the seven IP laws above plus the WTO ratification act ([UU No. 7 Tahun 1994](https://peraturan.bpk.go.id/)).

### What's not reachable anywhere outside DGIP

- **ID-only national trademarks** (i.e. TMs filed directly with DGIP, not via Madrid) — locked behind PDKI.
- **ID-only national industrial designs** (no Hague IR alternative because ID is not a Hague member) — locked behind PDKI.
- **Full prosecution detail** — file history, examiner notes, office actions, opposition proceedings, appeals (Komisi Banding Paten) — locked.
- **Copyright records** — declarative recordal at DGIP; no third-party register.
- **Trade-secret licence recordals** — only DGIP records these.
- **Geographical Indications** — ID register only.
- **Communal IP** ("Kekayaan Intelektual Komunal" — traditional knowledge, traditional cultural expressions, communal-IP variants) at [`kik.dgip.go.id`](https://kik.dgip.go.id/) — ID-specific category, no international equivalent.
- **DGIP performance / annual-report data** at [`dashboardmonitoring.dgip.go.id`](https://dashboardmonitoring.dgip.go.id/) — Incapsula-walled.

---

## 7. Rate Limits / Quotas

**Not applicable** to any reachable surface — no API to rate-limit.
The Incapsula WAF presumably imposes per-IP request limits as a
bot-defense mechanism, but those are not "API throttles" in any
agent-usable sense.

---

## 8. Terms of Service

DGIP does not publish a website terms-of-use page comparable to
JPO's TaaS conditions or KIPO's KIPRIS Plus contract. The
ministerial parent (Kementerian Hukum R.I. — Ministry of Law) sits
under Indonesian government licensing norms but does not publish a
machine-readable open-data licence. The closest signal is:

- **Indonesia's Open Government Data Platform** at
  [`data.go.id`](https://data.go.id/), operated by the Ministry of
  Communication and Informatics, defaults to *Creative Commons
  Attribution* for most datasets. **DGIP does not publish to
  `data.go.id`.** Searches for "DJKI" return 3 hits on the literal
  search-results page (no DGIP-sourced datasets); searches for
  "kekayaan intelektual" return only municipal/provincial aggregate
  HKI counts (Kab. Majalengka, Kab. Ogan Komering Ilir, Kota
  Sukabumi, Provinsi Jawa Tengah), not DGIP register data.
- **DGIP's own gazettes** at [`dgip.go.id/berita-resmi/...`](https://dgip.go.id/) — Berita Resmi Paten (BRP), Berita Resmi Merek (BRM), Berita Resmi Desain Industri (BRDI), Berita Resmi Indikasi Geografis (BRIG), Berita Resmi Lisensi Paten, Berita Resmi Madrid Protokol — are published as PDF + HTML index pages. There is no explicit licence; these are statutory publications under the relevant IP laws (e.g. [UU No. 13 Tahun 2016](https://peraturan.bpk.go.id/Home/Details/37536) § 49 for patent gazettes).

The Indonesian Public Information Disclosure Act
([UU No. 14 Tahun 2008](https://peraturan.bpk.go.id/Home/Details/39068),
"Keterbukaan Informasi Publik") creates a general public-information
duty for government bodies, with carve-outs for trade secrets,
personal data, and ongoing investigations. The Act provides
substantive cover for re-using statutory publications (gazettes,
court decisions, laws) but does not create a specific machine-readable
right to register data. Any production proxy would need to confirm
posture via DGIP's PPID (Pejabat Pengelola Informasi dan Dokumentasi)
at [`ppid.dgip.go.id`](http://ppid.dgip.go.id/).

---

## 9. Operational Notes

**Bot defense is the wall.** PDKI runs Alibaba Cloud ESA at the CDN layer, Imperva/Incapsula at the WAF layer, and a Distil Networks behavioral-fingerprinting script in-page. Every probe variant (Safari and Chrome User-Agents with realistic Sec-Fetch headers; different Accept-Language; multiple paths) returned the same Incapsula JS-challenge iframe. Defeat paths: (a) headless-browser per request — per-user runtime cost, brittle to challenge upgrades; (b) CAPTCHA-solving service contract — out of scope; (c) private allowlist agreement with DGIP — no documented path. None satisfy zero-infra-proxy.

**No SOAP / WSDL legacy.** DGIP does not appear to publish a legacy SOAP service. Probes for `wsdl`, `soap`, `services.dgip.go.id`, `ws.dgip.go.id` returned no DNS resolution.

**ASEAN IP Register is the consolation prize, but it's a non-API surface.** [`asean-ipregister.wipo.net`](https://asean-ipregister.wipo.net/) / [`ip-register.aseanip.org`](https://ip-register.aseanip.org/) runs on WIPO's wopublish (Apache Wicket) platform — `jsessionid` cookies + IBehaviorListener URLs + server-rendered POST-driven interactions. No REST endpoint, no JSON, no documented schema; scraping wopublish is worse than scraping PDKI because every page state requires session binding. WIPO's [INSPIRE jurisdiction profile for Indonesia](https://inspire.wipo.int/system/files/juri/id.pdf) describes ID's role in ASEAN PATENTSCOPE but does not point to a programmatic endpoint.

**Statute corpus is the only clean lift.** Indonesian IP law is reachable at two primary-source hosts:
- [`peraturan.bpk.go.id`](https://peraturan.bpk.go.id/) — BPK JDIH (Supreme Audit Agency legal-info system); slug URLs of shape `/Home/Details/{id}` and `/Details/{id}/uu-no-{n}-tahun-{yyyy}`. Anonymous-curl probe returned 403 (Cloudflare interstitial), but the URLs are canonical and the laws are public-domain government work.
- [`jdih.dgip.go.id`](http://jdih.dgip.go.id/) — DGIP's own JDIH catalog of IP-specific regulations. TLS handshake failed on direct probe; reachable via search-engine cache.

**Third-party wrapper search returned zero.** A targeted web search
(`"pdki-indonesia.dgip.go.id" API site:github.com OR site:gitlab.com
OR site:pypi.org`) returned 0 hits for DGIP/PDKI wrappers. Existing
Indonesian government-data wrappers (PDDIKTI for higher education,
unrelated to IP) are popular on GitHub, which suggests the
developer community has *tried* to wrap DGIP and given up — or
DGIP's bot wall is recent enough that no one has bothered.

**The DJKI roadmap mentions digitalization, not openness.** DGIP's
[2024 reflection article](https://www.dgip.go.id/artikel/detail-artikel-berita/djki-refleksi-2024-strategi-dan-inovasi-menuju-layanan-kekayaan-intelektual-lebih-modern?kategori=liputan-humas)
describes 2024-2025 priorities around "Roadmap Pengembangan
Kekayaan Intelektual Nasional" coordinated with BAPPENAS (national
development planning agency) plus an ASEAN IP Rights Action Plan
2026-2030. None of the public-facing statements mention API
provision, open-data publication, or developer access. The
direction is "digital filing modernization" + "PDKI search
quality improvements" (image search, phonetic search, AI assist) —
all of which are end-user features that strengthen the bot wall
rather than open the data.

**Imperva is hard to bypass legally.** Even if a headless solver
worked technically, Imperva's terms of service prohibit
"circumvention of access controls" — and Indonesia's
[UU No. 19 Tahun 2016](https://peraturan.bpk.go.id/Details/37589/uu-no-19-tahun-2016)
(Information and Electronic Transactions Law, "UU ITE") creates
criminal penalties for unauthorized access to government computer
systems. Operating a hosted scraper that defeats the bot wall is
not just rate-limit-risky; it crosses into a posture this repo does
not want to inhabit.

---

## 10. Verdict

**🔴 Red — no public API, no path to one.**

**What kills it:** no documented REST/JSON/XML on any `dgip.go.id` host; Imperva/Incapsula + Alibaba Cloud ESA on every reachable subdomain; 0 entries for Indonesia in the [WIPO IP API Catalog](https://apicatalog.wipo.int/) (179 total, 10 office providers, none Indonesian); no DGIP datasets on [`data.go.id`](https://data.go.id/); no third-party wrapper on GitHub/PyPI/GitLab; DJKI's 2024-2026 roadmap describes UI/filing modernization, not API provision; [UU ITE](https://peraturan.bpk.go.id/Details/37589/uu-no-19-tahun-2016) raises the legal floor on scraper-bypass beyond mere ToS risk.

**What's still missing for ID coverage:** ID-only national TMs (no Madrid IR alternative), ID-only national designs (no Hague IR because ID withdrew 1950→2010), ID copyright + trade-secret + GI registers, full prosecution detail (file history, opposition, Komisi Banding Paten), and `paten sederhana` subtype-filtered prosecution (the subtype appears in PATENTSCOPE under the application-type field but full subtype-filtered detail is DGIP-only).

**What's still green-adjacent:** substantive Indonesian IP law (Patents Act + 2024 third amendment, Merek+GI Act, Designs Act, Copyright Act, Trade Secret Act, DTLST Act, PVP Act, UU ITE, Public Information Disclosure Act) is reachable cleanly at [`peraturan.bpk.go.id`](https://peraturan.bpk.go.id/) and [`jdih.dgip.go.id`](http://jdih.dgip.go.id/) — a `StaticLawCorpus` candidate mirroring `ipo_in_statutes` / `dpma_statutes` / `legifrance_ip` / `tw_trade_secrets`.

**Operational path:**

1. Close the register-side proxy story for ID. Mark `coverage/sources.yaml` register-side as `skipped` with blocker `no_public_api + bot_walled`. Reachable transitively via PATENTSCOPE (~193K records, monthly lag), INPADOC (biblio + family + legal events), Madrid Monitor (TM IRs designating ID), and the ASEAN IP Register (browser-only).
2. Queue a `legifrance_ip`-shape `id_statutes` connector covering the eight to ten primary IP acts at `peraturan.bpk.go.id` slug URLs.
3. Re-evaluate 2027-Q1 for: Hague System ratification (currently before Parliament; ASEAN IPR Action Plan 2026-2030 lists it as a target); any DGIP open-data announcement tied to the BAPPENAS roadmap; DPMA-style paid-API equivalent.
4. Send no contact emails. No surface to negotiate against.

**Strategic memory:** Indonesia hosts the ASEAN IP Register regional server itself but provides *no* API to its own register data. ID delivers data to other ASEAN offices via WIPO's wopublish, then locks its own front door. The path forward for ID coverage runs through (a) higher-layer transitive coverage, (b) substantive-law static corpus, and (c) a 2027-Q1 recheck. The register-side gap is real but narrow; the substantive-law shipment is genuinely useful for prosecution arguments and litigation work and is the only proxy-shippable layer.
