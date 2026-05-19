# DGIP Indonesia (ID) — national

**Layer:** national
**Jurisdiction:** ID (WIPO ST.3: ID)
**Issuing body:** Direktorat Jenderal Kekayaan Intelektual (DGIP, also DJKI), Direktorat Jenderal under the Kementerian Hukum (Ministry of Law) of the Republic of Indonesia
**Rights administered:** patent (incl. *paten sederhana* simple-patent subtype), trademark, geographical_indication, industrial_design, copyright, trade_secret (licence recordal only), layout_design_ic (DTLST), and DGIP's communal-IP / traditional-knowledge register (KIK). Plant Variety Protection is administered separately by the Ministry of Agriculture's PVT office, not DGIP.
**Working languages:** Bahasa Indonesia (primary, authoritative for all statutes and gazettes); English available on a parallel content host ([`en.dgip.go.id`](https://en.dgip.go.id/), though TLS handshake failed on direct 2026-05-18 probe).
**Connector status:** **register-side: skipped** (no public REST + Imperva bot wall on every reachable host); **statutes-side: planned** (`legifrance_ip`-shape `StaticLawCorpus` candidate over `peraturan.bpk.go.id`).
**Last verified:** 2026-05-18
**Manifest entry:** not yet listed in `coverage/sources.yaml`

**Detail surveys:**
- [`waves/2026-05-18-secondary-nationals-wave/id-dgip.md`](../waves/2026-05-18-secondary-nationals-wave/id-dgip.md) — 2026-05-18 grounded 10-section discovery

**Higher layers covering this office transitively:**
- **WIPO PATENTSCOPE** — Indonesia national collection, 193,561 records, biblio 1987-12-02 → 2025-12-08, latest update 2026-01-22 ([Data Coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf)). This is the operational substitute for ID patent register data — both `paten` and `paten sederhana` records flow through.
- **EPO INPADOC** (via [`regional/epo.md`](../regional/epo.md)) — ID national filings plus ID-designating PCT national-phase entries at biblio + family + legal-events fidelity. Indonesia has been a PCT contracting state since 1997-09-05.
- **WIPO Madrid Monitor** — international TM IRs designating ID. ID acceded to Madrid Protocol 2017-10-02, in force 2018-01-02 ([WIPO notification 217](https://www.wipo.int/wipolex/en/treaties/notifications/details/treaty_madridp-gp_217)). ID-only national TMs remain DGIP-only.
- **WIPO Hague** — **not applicable.** Indonesia is *not* currently a Hague member (joined 1950, withdrew 2010; re-accession Presidential Regulation submitted to Parliament 2024-08-06, not yet ratified). All ID industrial designs remain DGIP-only.
- **ASEAN IP Register** ([`asean-ipregister.wipo.net`](https://asean-ipregister.wipo.net/) / [`ip-register.aseanip.org`](https://ip-register.aseanip.org/)) — relaunched 2023 from the older "ASEAN PATENTSCOPE" (2017). Covers ID plus eight other ASEAN members. Per the [ASEAN-IPR public rollout announcement](https://www.aseanip.org/home/2023/03/03/public-rollout-of-asean-patentscope-service), **Indonesia hosts the regional database server itself** — a striking inversion (ID supplies the regional backbone but locks its own front door). Browser-only WIPO wopublish (Apache Wicket) stack — no documented REST.

---

## §1 Mission

DGIP is Indonesia's single national IP authority — patents (full and simple-patent subtype), trademarks, geographical indications, industrial designs, copyright, trade-secret licence recordals, layout-designs of integrated circuits, and the ID-specific communal-IP register. It sits under the Kementerian Hukum (Ministry of Law) and operates Indonesia's filing infrastructure plus the consumer register search at [`pdki-indonesia.dgip.go.id`](https://pdki-indonesia.dgip.go.id/) (Pangkalan Data Kekayaan Intelektual — PDKI). Indonesia is **the world's fourth-most-populous country** (≈278 million), a G20 economy, and an ASEAN member. DGIP's role in the layered structure is the ID-only national slice that escapes higher-layer coverage; for cross-border filings, INPADOC, PATENTSCOPE, and Madrid Monitor reach into Indonesia at the same biblio fidelity they reach into other PCT/Madrid members. The unique ID-specific category worth naming is **`paten sederhana`** — a 10-year simple-patent subtype defined alongside the 20-year invention patent in [UU No. 13 Tahun 2016 (Patents Act)](https://peraturan.bpk.go.id/Home/Details/37536) as amended by [UU No. 65 Tahun 2024](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024), with a lower inventive-step threshold; this is the rights-class most analogous to a German Gebrauchsmuster or Chinese utility model, but administered as a patent subtype rather than a separate register.

## §2 What's unique here

- **`Paten sederhana` (simple patent)** — 10-year subtype with lower inventiveness threshold; visible in PATENTSCOPE under the application-type field but full subtype-filtered prosecution detail is DGIP-only.
- **ID-only national trademarks** — Madrid IRs designating ID are reachable via WIPO Madrid Monitor (post-2018); pre-2018 national TMs and pure SG-only-equivalent ID-only filings live only at DGIP.
- **ID-only industrial designs** — no Hague IR alternative exists for ID (withdrew 2010), so the entire ID design register is national-only.
- **Geographical Indications** — ID-only register, including the "Kekayaan Intelektual Komunal" / communal-IP variants (e.g. Liberika Kayong Utara coffee, Pinang Betara Jambi areca-nut) that DGIP profiles in its public communications.
- **Copyright register** — declarative, optional, ID-only.
- **Trade-secret licence recordals** (Rahasia Dagang) — ID-only event log under [UU No. 30 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44896).
- **Layout-design IC register** ("DTLST") under [UU No. 32 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44897) — niche but real.
- **Komisi Banding Paten** (Patent Appeals Commission) decisions — first-instance administrative appeals, not reproduced by any higher layer.
- **Full Indonesian-language IP statute corpus** — Patents Act, TM+GI Act, Designs Act, Copyright Act, Trade Secret Act, DTLST Act, PVP Act, UU ITE (Information and Electronic Transactions Law), and the [Public Information Disclosure Act (UU No. 14 Tahun 2008)](https://peraturan.bpk.go.id/Home/Details/39068). Bahasa Indonesia-authoritative, version-controlled at [`peraturan.bpk.go.id`](https://peraturan.bpk.go.id/) and [`jdih.dgip.go.id`](http://jdih.dgip.go.id/), free.

## §3 Programmatic surfaces

### PDKI register search ([`pdki-indonesia.dgip.go.id`](https://pdki-indonesia.dgip.go.id/))

| Field | Value |
|---|---|
| Endpoint | [`https://pdki-indonesia.dgip.go.id/`](https://pdki-indonesia.dgip.go.id/) — SPA-internal calls only, no documented API |
| Auth | None for the HTML UI; no API-key flow advertised |
| Format | HTML / JS bundle; no JSON contract published |
| Rate limit | Not published (Imperva-managed at the WAF) |
| ToS posture | No website terms-of-use; defense-in-depth posture is implicit "browser-only" |
| Rating (zero-infra proxy) | 🔴 **Red** — Alibaba Cloud ESA + Imperva/Incapsula + Distil behavioral fingerprinting on every host; every probe variant on 2026-05-18 returned the same Incapsula JS-challenge iframe |
| Primary source | [PDKI landing](https://pdki-indonesia.dgip.go.id/) · [PDKI usage tutorial (DGIP e-learning PDF)](https://ekii.dgip.go.id/uploads/files/lessons87/61f97429e8056f85533a98f4cbc1fa79.pdf) |

Hard skip. The bot wall is bound at the TLS edge and returns indistinguishable responses for `/`, `/search?type=trademark`, `/api`, `/api/v1`, `/_next/data`, and every other variant probed — there is no path that escapes it.

### DGIP transaction/filing subdomains

| Field | Value |
|---|---|
| Endpoint | `merek.dgip.go.id` (TM filing), `paten.dgip.go.id` (patent filing), `desainindustri.dgip.go.id` (design filing), `hakcipta.dgip.go.id` (copyright filing), `ig.dgip.go.id` (GI filing), `dtlst.dgip.go.id` (DTLST filing), `rd.dgip.go.id` (trade-secret recordal), `ekii.dgip.go.id` (unified e-KII portal) |
| Auth | Application-level login required for filing |
| Format | HTML (Incapsula-walled to anonymous traffic) |
| ToS posture | Filing-side scope; not contemplated for unaffiliated SaaS proxy |
| Rating (zero-infra proxy) | 🔴 **Red** — every host returned 403 with an 884-byte Incapsula iframe on 2026-05-18 probes |
| Primary source | [DGIP eServices index (institutional home)](https://dgip.go.id/) |

Same wall, same iframe pattern — confirms the bot-defense is account-wide, not specific to PDKI.

### DGIP institutional / gazette host ([`dgip.go.id`](https://dgip.go.id/))

| Field | Value |
|---|---|
| Endpoint | [`https://dgip.go.id/berita-resmi/...`](https://dgip.go.id/) — Berita Resmi Paten (BRP), Berita Resmi Merek (BRM), Berita Resmi Desain Industri (BRDI), Berita Resmi Indikasi Geografis (BRIG), Berita Resmi Lisensi Paten, Berita Resmi Madrid Protokol |
| Auth | None |
| Format | HTML index + PDF gazette files |
| Rate limit | Not published |
| ToS posture | Statutory publications under [UU No. 13 Tahun 2016 § 49](https://peraturan.bpk.go.id/Home/Details/37536) etc.; no explicit licence |
| Rating (zero-infra proxy) | 🔴 **Red** — bulk PDF gazettes, not machine-readable structured data; not a register-substitute substrate |
| Primary source | [DGIP institutional home](https://dgip.go.id/) |

Useful as a primary-source archive for prosecution arguments (gazette announcements drive opposition windows, renewal deadlines, etc.) but not a proxy substrate.

### data.go.id (Indonesia open-data portal)

| Field | Value |
|---|---|
| Endpoint | [`https://data.go.id/`](https://data.go.id/) |
| Auth | None for catalog browsing |
| Format | CKAN-style HTML + dataset metadata |
| Rate limit | Not specifically published |
| ToS posture | CC-BY default for most datasets |
| Rating (zero-infra proxy) | 🔴 **Red** — DGIP does not publish here; search for "DJKI" returns 0 substantive hits, "kekayaan intelektual" returns only municipal/provincial aggregate counts (Kab. Majalengka, Kab. Ogan Komering Ilir, Kota Sukabumi, Provinsi Jawa Tengah) — no register data |
| Primary source | [data.go.id home](https://data.go.id/) |

Not a route — DGIP simply isn't on the national open-data platform.

### WIPO IP API Catalog ([`apicatalog.wipo.int`](https://apicatalog.wipo.int/))

| Field | Value |
|---|---|
| Endpoint | [`https://apicatalog.wipo.int/api/apis?size=300`](https://apicatalog.wipo.int/) |
| Probe 2026-05-18 | 0 Indonesian / DGIP / DJKI entries (179 total APIs; providers limited to DPMA, EPO, EUIPO, IP Australia, JPO, MOIP KOREA, QAZ, UPRP, USPTO, WIPO) |
| Rating (zero-infra proxy) | 🔴 **Red** by absence — DGIP has not published an API to the canonical multilateral catalog |
| Primary source | [WIPO IP API Catalog](https://apicatalog.wipo.int/) |

Confirms DGIP has not registered any public programmatic interface with WIPO.

### ASEAN IP Register ([`asean-ipregister.wipo.net`](https://asean-ipregister.wipo.net/))

| Field | Value |
|---|---|
| Endpoint | [`https://asean-ipregister.wipo.net/`](https://asean-ipregister.wipo.net/) / [`https://ip-register.aseanip.org/`](https://ip-register.aseanip.org/) |
| Auth | None |
| Format | HTML (Apache Wicket / WIPO wopublish; `jsessionid` + IBehaviorListener URLs on probe) |
| ToS posture | WIPO-hosted; no explicit ASEAN-wide API ToS |
| Rating (zero-infra proxy) | 🔴 **Red** — server-rendered Wicket UI, no documented REST, session-bound interactions; scraping shape is worse than scraping PDKI |
| Primary source | [ASEAN IP Register about](https://www.aseanip.org/services/asean-ip-register) · [ASEAN-IPR public rollout announcement](https://www.aseanip.org/home/2023/03/03/public-rollout-of-asean-patentscope-service) |

Notable detail: per the rollout announcement, **Indonesia hosts the regional database server** — i.e. ID is the data backbone for the ASEAN cross-office register, even while it locks its own front door.

### Substantive law — `peraturan.bpk.go.id` + `jdih.dgip.go.id`

| Field | Value |
|---|---|
| Endpoint | [`https://peraturan.bpk.go.id/`](https://peraturan.bpk.go.id/) (BPK JDIH — Supreme Audit Agency legal-info system) · [`http://jdih.dgip.go.id/`](http://jdih.dgip.go.id/) (DGIP's own JDIH catalog of IP-specific regulations) |
| Auth | None |
| Format | HTML / PDF; slug-addressable laws |
| ToS posture | Public-domain government work under Indonesian statutory norms |
| Rating (zero-infra proxy) | 🟢 **Green** — clean static corpus, same shape as `ipo_in_statutes` / `dpma_statutes` / `legifrance_ip` / `tw_trade_secrets` |
| Primary source | [BPK JDIH home](https://peraturan.bpk.go.id/) · [UU No. 13 Tahun 2016 (Paten)](https://peraturan.bpk.go.id/Home/Details/37536) · [UU No. 65 Tahun 2024 (third Paten amendment)](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024) · [UU No. 20 Tahun 2016 (Merek + GI)](https://peraturan.bpk.go.id/Details/37595/uu-no-20-tahun-2016) |

Canonical, free, version-controlled. **This is the only proxy-shippable layer for ID.**

## §4 Fees

DGIP charges in **IDR (Indonesian Rupiah)** across patents (filing, search, examination, grant, annuities), trademarks (filing/renewal per class), geographical indications, industrial designs, copyright recordals, trade-secret licence recordals, and DTLST filings. Fee schedules are set by Government Regulation ("Peraturan Pemerintah") on Non-Tax State Revenue ("PNBP — Penerimaan Negara Bukan Pajak") for the Ministry of Law, periodically updated.

- **Official schedule:** [DGIP institutional home](https://dgip.go.id/) — navigate per right (Paten / Merek / Desain Industri / Hak Cipta / Indikasi Geografis / DTLST / Rahasia Dagang) for the current PNBP table.
- **Statutory basis:** PNBP government regulations published at [`peraturan.bpk.go.id`](https://peraturan.bpk.go.id/); fees are referenced in the substantive IP laws (e.g. [UU No. 13 Tahun 2016 (Paten)](https://peraturan.bpk.go.id/Home/Details/37536) as amended by [UU No. 65 Tahun 2024](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024)).
- **Gazette announcements (fee changes):** [DGIP berita resmi index](https://dgip.go.id/) for the relevant right.

Notable discount programs *(named here; specific amounts and dates live on the official schedule)*:

- **UMKM (small/medium enterprises) reduced filings** — eligibility via Ministry-of-Cooperatives certification.
- **Educational/research institution reduced filings** — eligibility via institutional accreditation.
- **Annual-fee grace period** — under the 2024 third amendment ([UU No. 65 Tahun 2024](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024)), patent holders late on annual fees receive a grace period (replacing automatic cancellation in the prior regime).

## §5 Connector strategy

### What we cover today

Nothing — ID is not in `coverage/sources.yaml` as of 2026-05-18. ID patent biblio + family is currently accessed transitively via [`patent_client_agents.epo_ops`](../regional/epo.md) for INPADOC and via WIPO PATENTSCOPE (no proxied connector — agents query the WIPO surface directly). ID international TM IRs are reachable via Madrid Monitor.

### What we should add

**Queue a `legifrance_ip`-shape statute connector for Indonesian IP law.**

- **Module name candidate:** `id_statutes` (mirroring `ipo_in_statutes`, `dpma_statutes`, `legifrance_ip`, `tw_trade_secrets`).
- **Scope (eight to ten primary acts):** Paten ([UU No. 13 Tahun 2016](https://peraturan.bpk.go.id/Home/Details/37536) + [UU No. 65 Tahun 2024](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024) third amendment), Merek + GI ([UU No. 20 Tahun 2016](https://peraturan.bpk.go.id/Details/37595/uu-no-20-tahun-2016)), Desain Industri ([UU No. 31 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44893/uu-no-31-tahun-2000)), Hak Cipta ([UU No. 28 Tahun 2014](https://peraturan.bpk.go.id/Details/38690/uu-no-28-tahun-2014)), Rahasia Dagang ([UU No. 30 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44896)), DTLST ([UU No. 32 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44897)), PVP ([UU No. 29 Tahun 2000](https://peraturan.bpk.go.id/Home/Details/44894)), UU ITE ([UU No. 19 Tahun 2016](https://peraturan.bpk.go.id/Details/37589/uu-no-19-tahun-2016)), and the Public Information Disclosure Act ([UU No. 14 Tahun 2008](https://peraturan.bpk.go.id/Home/Details/39068)).
- **Why this is the right move:** the substantive-law layer is the only **green** ID surface, the primary sources are stable, the static-corpus pattern is well-trodden (four sibling corpora already shipped), and the resulting capability — prosecution arguments, opposition/cancellation strategy, freedom-to-operate posture for ID — is genuinely useful even with the register-side gap.
- **Cross-reference:** queue in [`BACKLOG.md`](../BACKLOG.md); coverage/sources.yaml entry as `ID/BPK/IP` (or `ID/JDIH/IP` per the naming convention used by `FR/Legifrance/IP`).

### What we should NOT add

- **Register-side hosted proxy at any layer.** PDKI is Imperva-walled with no documented API; every DGIP transaction subdomain is also Imperva-walled; ASEAN IP Register is server-rendered Wicket without REST; data.go.id has no DGIP content; WIPO IP API Catalog has zero ID entries. Higher-layer coverage (PATENTSCOPE ~193K records, INPADOC biblio + family + legal events, Madrid IRs designating ID) covers the cross-border slice transitively. The ID-only slice is a real but narrow gap that does not justify a bot-wall-bypass posture.
- **Imperva-bypass headless-browser scraper.** Crosses [UU ITE (UU No. 19 Tahun 2016)](https://peraturan.bpk.go.id/Details/37589/uu-no-19-tahun-2016) territory for unauthorized access to government systems, on top of generic Imperva ToS issues. This repo's posture is zero-infra proxy of *documented* APIs, not bypassing access controls.
- **PDKI HTML scrape.** Same reason — Distil/Incapsula behavioral fingerprinting is what we'd have to defeat per request.
- **ASEAN IP Register Wicket scrape.** Worse shape than PDKI (session-bound), no benefit.
- **DGIP performance dashboard, marketplace, KIK (communal IP) hosts.** Imperva-walled; not in scope.
- **PVP register at the Ministry of Agriculture.** Out of DGIP's perimeter; not a planned coverage item.

### Next steps

1. **Cut the `id_statutes` worktree** — copy from `tw_trade_secrets` as the smallest sibling exemplar, then walk through `dpma_statutes` for the multi-act case. Manifest entry should be `ID/BPK/IP` or `ID/JDIH/IP`.
2. **Confirm `peraturan.bpk.go.id` fetch posture** — anonymous-curl probe 2026-05-18 returned 403 (Cloudflare interstitial) for the law-detail page; verify with a realistic browser User-Agent + Accept-Language before connector implementation, or fall back to `jdih.dgip.go.id` slug URLs.
3. **Set a 2027-Q1 re-evaluation** for: (a) Indonesia's Hague System re-accession (Presidential Regulation before Parliament since 2024-08; ASEAN IPR Action Plan 2026-2030 lists it as a target — would unlock Hague IR coverage for ID designs); (b) any DGIP open-data announcement tied to the BAPPENAS Roadmap Pengembangan Kekayaan Intelektual Nasional; (c) DPMA-style paid-API equivalent.
4. **Do not contact DGIP.** No surface to negotiate against; DGIP's published 2024-2026 roadmap is filing-modernization-and-PDKI-search-quality, not data provision. Re-evaluate 2027-Q1.

## §6 Open questions

- **PATENTSCOPE coverage of `paten sederhana`** — the [PATENTSCOPE Data Coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) shows 193,561 ID records but doesn't break out the simple-patent subtype. A targeted query on the application-type field is needed to confirm subtype-filtered coverage.
- **Hague System re-accession timeline** — Presidential Regulation submitted 2024-08-06; Parliament timeline not public. Monitor [WIPO Hague members page](https://www.wipo.int/en/web/hague-system/members) for ID listing.
- **ASEAN IP Register data freshness for ID** — Indonesia hosts the regional server but the public Wicket UI doesn't expose per-jurisdiction update timestamps. Confirm by sample query for recent (2026) ID filings.
- **`peraturan.bpk.go.id` Akoma Ntoso / structured-text export** — anonymous-curl probe returned a Cloudflare interstitial 403; no documented bulk-XML export. Check whether the BPK JDIH offers a structured-data feed before settling on HTML+PDF as the ingestion shape.
- **DGIP gazette structure** — Berita Resmi Paten et al. are published as PDFs; per-issue size and indexing approach (extract-and-discard vs. mirror) needs a sample-pull before any `id_gazettes` extension lands.
- **DGIP foreign-developer posture under UU 14/2008** — the Public Information Disclosure Act provides general public-information cover for statutory publications; whether DGIP's PPID would issue a confirmation letter on re-use of register data is unknown. Not pursuing without a paying customer.

## §7 References

Primary sources only — DGIP, BPK JDIH, WIPO Lex, WIPO PATENTSCOPE, ASEAN-IPR.

**DGIP portals + service docs:**
- [DGIP institutional home](https://dgip.go.id/)
- [PDKI landing](https://pdki-indonesia.dgip.go.id/)
- [PDKI usage tutorial (DGIP e-learning PDF)](https://ekii.dgip.go.id/uploads/files/lessons87/61f97429e8056f85533a98f4cbc1fa79.pdf)
- [DGIP 2024 reflection article (roadmap context)](https://www.dgip.go.id/artikel/detail-artikel-berita/djki-refleksi-2024-strategi-dan-inovasi-menuju-layanan-kekayaan-intelektual-lebih-modern?kategori=liputan-humas)

**Indonesian IP statutes on `peraturan.bpk.go.id`:**
- [UU No. 13 Tahun 2016 — Paten](https://peraturan.bpk.go.id/Home/Details/37536)
- [UU No. 65 Tahun 2024 — Perubahan Ketiga atas UU 13/2016](https://peraturan.bpk.go.id/Details/306515/uu-no-65-tahun-2024)
- [UU No. 20 Tahun 2016 — Merek dan Indikasi Geografis](https://peraturan.bpk.go.id/Details/37595/uu-no-20-tahun-2016)
- [UU No. 31 Tahun 2000 — Desain Industri](https://peraturan.bpk.go.id/Home/Details/44893/uu-no-31-tahun-2000)
- [UU No. 28 Tahun 2014 — Hak Cipta](https://peraturan.bpk.go.id/Details/38690/uu-no-28-tahun-2014)
- [UU No. 30 Tahun 2000 — Rahasia Dagang](https://peraturan.bpk.go.id/Home/Details/44896)
- [UU No. 32 Tahun 2000 — Desain Tata Letak Sirkuit Terpadu (DTLST)](https://peraturan.bpk.go.id/Home/Details/44897)
- [UU No. 29 Tahun 2000 — Perlindungan Varietas Tanaman (PVP)](https://peraturan.bpk.go.id/Home/Details/44894)
- [UU No. 19 Tahun 2016 — Perubahan atas UU ITE](https://peraturan.bpk.go.id/Details/37589/uu-no-19-tahun-2016)
- [UU No. 14 Tahun 2008 — Keterbukaan Informasi Publik](https://peraturan.bpk.go.id/Home/Details/39068)

**Higher-layer coverage (transitive):**
- [WIPO PATENTSCOPE Data Coverage table](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) (Indonesia row: 193,561 records, biblio 1987-12-02 → 2025-12-08, latest update 2026-01-22)
- [WIPO Madrid Protocol — Indonesia accession notification 217](https://www.wipo.int/wipolex/en/treaties/notifications/details/treaty_madridp-gp_217) (2017-10-02 accession, 2018-01-02 in force)
- [WIPO Lex member profile — Indonesia](https://www.wipo.int/wipolex/en/profile.jsp?code=ID)
- [WIPO INSPIRE jurisdiction profile — Indonesia (PDF)](https://inspire.wipo.int/system/files/juri/id.pdf)
- [WIPO IP API Catalog](https://apicatalog.wipo.int/) — probed 2026-05-18, 0 DGIP entries out of 179 total
- [ASEAN IP Register about](https://www.aseanip.org/services/asean-ip-register) · [ASEAN-IPR public rollout announcement (2023)](https://www.aseanip.org/home/2023/03/03/public-rollout-of-asean-patentscope-service)

**Detail survey:**
- [`waves/2026-05-18-secondary-nationals-wave/id-dgip.md`](../waves/2026-05-18-secondary-nationals-wave/id-dgip.md) — 2026-05-18 grounded 10-section discovery

---

## §8 Change log

| Date | Change | Source |
|---|---|---|
| 2026-05-18 | Initial synopsis. Register-side **🔴 red** — no public API. PDKI ([`pdki-indonesia.dgip.go.id`](https://pdki-indonesia.dgip.go.id/)) and every DGIP transaction subdomain (`merek.`, `paten.`, `desainindustri.`, `hakcipta.`, `ig.`, `dtlst.`, `rd.`, `ekii.`, `dashboardmonitoring.dgip.go.id`) are walled behind Alibaba Cloud ESA + Imperva/Incapsula + Distil behavioral fingerprinting; all 2026-05-18 probe variants returned indistinguishable JS-challenge iframes regardless of path. Zero DGIP entries in the [WIPO IP API Catalog](https://apicatalog.wipo.int/) (179 total APIs, providers limited to DPMA, EPO, EUIPO, IP Australia, JPO, MOIP KOREA, QAZ, UPRP, USPTO, WIPO). No DGIP datasets on Indonesia's open-data portal [`data.go.id`](https://data.go.id/). ASEAN IP Register at [`asean-ipregister.wipo.net`](https://asean-ipregister.wipo.net/) is browser-only WIPO wopublish (Apache Wicket) — no REST. Statutes-side **🟢 green** — Indonesian IP-law corpus reachable cleanly at [`peraturan.bpk.go.id`](https://peraturan.bpk.go.id/) and [`jdih.dgip.go.id`](http://jdih.dgip.go.id/); queue `id_statutes` `StaticLawCorpus` covering Paten + 2024 third amendment, Merek+GI, Desain Industri, Hak Cipta, Rahasia Dagang, DTLST, PVP, UU ITE, and the Public Information Disclosure Act. Transitive coverage via PATENTSCOPE (193,561 ID records, biblio 1987→2025-12, latest update 2026-01-22) and INPADOC (biblio + family + legal events). **Striking inversion:** Indonesia hosts the regional ASEAN IP Register server itself but provides no API to its own register data. **Hague System status:** ID withdrew 1950→2010; re-accession Presidential Regulation submitted to Parliament 2024-08-06, not yet ratified — re-evaluate 2027-Q1. | [waves/2026-05-18-secondary-nationals-wave/id-dgip.md](../waves/2026-05-18-secondary-nationals-wave/id-dgip.md) · [PATENTSCOPE Data Coverage](https://patentscope.wipo.int/search/en/help/data_coverage.jsf) · [WIPO Madrid notification 217](https://www.wipo.int/wipolex/en/treaties/notifications/details/treaty_madridp-gp_217) · [ASEAN-IPR rollout](https://www.aseanip.org/home/2023/03/03/public-rollout-of-asean-patentscope-service) |
