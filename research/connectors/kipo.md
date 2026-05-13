# KIPO Connector Survey

One-page scoping survey for adding Korean IP data sources to `patent-client-agents`.
Korea is an IP5 office; KIPO offers an unusually well-developed REST API surface
(KIPRIS Plus) compared to JPO. The catch is that registration is built around
Korean residents — most foreign developers report a manual workaround.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Free tier | English | Bulk |
|---|---|---|---|---|---|---|---|
| 1 | KIPRIS Plus API | `plus.kipris.or.kr` | ServiceKey | XML (some JSON) | 1,000 calls/mo | Partial | Yes (paid) |
| 2 | KIPO Patent Register | via KIPRIS Plus | ServiceKey | XML | Same | Bib only | No |
| 3 | KIPO Trademark Register | via KIPRIS Plus | ServiceKey | XML | Same | Partial | Bulletins |
| 4 | KIPO Design Register | via KIPRIS Plus | ServiceKey | XML | Same | Limited | No |
| 5 | IPTAB decisions | KIPRIS search UI | None (UI) / KIPRIS Plus | XML/HTML/PDF | Same | KO only | No |
| 6 | KIPO bulk data | `plus.kipris.or.kr` data products | Member login + per-product purchase | XML/CSV | Some free products | Partial | Yes |
| 7 | Patent Court / Supreme Court | `scourt.go.kr` (KR), `library.scourt.go.kr/eng` | None (UI) | HTML/PDF | Free, no API | EN summaries only | No |
| 8 | K-PION | KIPO B2B portal | Letter-of-request → account | Web UI + PDF | Free for IP offices | KO+EN MT | No |
| 9 | KSVS plant varieties | `seed.go.kr/seed_eng` | None | HTML | Free | Yes | No |
| 10 | GI registry | KIPO TM (collective marks) + NAQS (ag) | Via KIPRIS Plus | XML | Same | Partial | No |
| 11 | Patent Act | `law.go.kr/eng`, `elaw.klri.re.kr` | None | HTML/PDF | Free | Reference EN | n/a |
| 12 | Trademark Act | same | None | HTML/PDF | Free | Reference EN | n/a |
| 13 | Design Protection Act | same | None | HTML/PDF | Free | Reference EN | n/a |
| 14 | UCPA (trade secrets) | same | None | HTML/PDF | Free | Reference EN | n/a |
| 15 | KIPO Examination Guidelines | `kipo.go.kr/en` | None | PDF | Free | EN PDF (older) | n/a |

## Per-asset detail

### 1. KIPRIS Plus API
Endpoint base `https://plus.kipris.or.kr/openapi/rest/...`. ~46 OpenAPI services
as of December 2019; ~126 open-data products today across patents, utility
models, designs, trademarks, applicants, citations, legal status, bulletins.
Auth is a single `ServiceKey` query-parameter. Free tier is **1,000 calls/month
per service** — adequate for prototyping but tight for production. Responses
are XML (some products JSON). English UI exists but many endpoint description
pages are Korean only; titles and bibliography come back with English fields
when available. ToS forbids redistribution of the Authentication Key and
asserts copyright of the data products to the Korea Institute of Patent
Information (KIPI). Commercial redistribution requires a separate license.

### 2-4. Patent / Trademark / Design registers
There is no separate "PAIR-equivalent" — register data is exposed through
KIPRIS Plus endpoints (`getBibliographyDetailInfoSearch`,
`patentRegisterInfoSearch`, `applicantNumberSearch`, etc.). Trademark coverage
includes English goods/services per Nice classification. Design register has
images but limited English bibliographic data.

### 5. IPTAB decisions
IPTAB handles inter partes and ex parte trials for patents, utility models,
designs, and trademarks. Decisions are published through KIPRIS after
confidentiality redaction. There is a KIPRIS Plus endpoint for trial info
(`trialInfoSearch`) but full decision text retrieval is largely UI-driven and
Korean-only.

### 6. KIPO bulk data
The KIPRIS Plus portal sells dataset products (weekly gazette XML, full-text
collections, citation tables, English-Korean corpora). Some open-data products
are free; large historical pulls are paid and require a contract. Best
candidate is the weekly gazette and the English-Korean Corpus of US Patents
(useful for translation alignment).

### 7. Patent Court of Korea / Supreme Court
The Korean judiciary publishes case law at `scourt.go.kr`. The English
sub-site (`library.scourt.go.kr/eng`) carries selected Supreme Court (2000–),
Constitutional Court (1998–), appellate (2004–), and Patent Court (1998–)
decisions in English. The IP High Court publishes "Leading Case Summaries"
PDFs annually. No API — scrape only. There is no entity literally called
"KIPSA" in this space (likely user typo for KIPRIS or KIPI).

### 8. K-PION
Not a public API — a Korean-to-English machine-translation portal KIPO offers
to **partner IP offices** under a Letter of Request signed by the office's
international-affairs director. Provides file-wrapper bibliographic data,
transaction histories, and publication documents. Not available to private
developers.

### 9. KSVS — Korea Seed & Variety Service
Operates the Korean Plant Variety Protection system under MAFRA at
`seed.go.kr/seed_eng`. Public web UI for variety search, application status,
DUS test results. No published API. Low priority — small corpus, mostly
domestic interest.

### 10. Korean GI registry
Korea protects GIs as **collective marks under the Trademark Act** (KIPO)
rather than a stand-alone GI registry. For agricultural GIs, NAQS (National
Agricultural Products Quality Management Service, under MAFRA) maintains a
parallel registration system. KIPO GIs are reachable through the KIPRIS Plus
trademark endpoints; NAQS data has no public API.

### 11-14. Statutory texts (Patent Act, Trademark Act, Design Protection Act, UCPA)
All available in reference English translations from three sources:
- `law.go.kr/eng` — National Legal Information Center, most up-to-date
- `elaw.klri.re.kr/eng_service/` — Korea Legislation Research Institute
- `kipo.go.kr/en/...` — KIPO's curated downloads (PDF, sometimes lagging)

Translations are explicitly non-authoritative; Korean text controls. UCPA
contains Korea's primary trade-secret provisions.

### 15. KIPO Examination Guidelines
Patent Examination Guidelines (most recent EN: January 2021),
older procedure guides (2010), and various TM/design updates (e.g., virtual
goods 2022) hosted on `kipo.go.kr/en`. Korean originals are kept current;
English PDFs lag and are very large. WIPO Lex mirrors some.

## Existing Python clients

- `nuri428/mcp_kipris` — MCP server exposing KIPRIS Plus patent endpoints
- `Tech-curator/korean-patent-mcp` (also surfaces as `khreat/korean-patent-mcp`) — MCP server, Korean docs
- `seheeopark/kipris` and `kipris_rcode` — **R** packages, not Python
- No mature, async-first Python client with broad endpoint coverage. Gap is real.

## Recommended v1 scope

1. **KIPRIS Plus — patent module first.** Wrap the highest-value endpoints
   (`patUtiliSearch`, `applicantNumberSearch`, `getBibliographyDetailInfoSearch`,
   `legalStatusInfoSearch`, `claimInfoSearch`). Mirrors the USPTO ODP shape
   we already have. ServiceKey via env var `KIPRIS_PLUS_SERVICE_KEY`.
2. **KIPRIS Plus — trademark module.** Lower marginal cost once XML auth/retry
   is built. Goods/services classes come in English, so the agent UX is
   immediately useful.
3. **Statute fetcher for `law.go.kr/eng`** — small scraper that returns
   structured Patent/Trademark/Design/UCPA text, parallel to our MPEP/TMEP
   modules. Cheap, no auth, high value for agents writing Korean memos.

## Skip list (v1)

- **K-PION** — not available to private developers without an inter-office MoU.
- **KSVS plant varieties** — niche, no API, scrape-only.
- **NAQS GI registry** — no API; KIPO collective marks cover the agent use case.
- **IPTAB full text decisions** — KO-only and behind the KIPRIS UI; revisit if
  a customer asks.
- **Patent Court decision corpus** — scrape-only, English coverage is
  curated-summary not full-text; defer until we build a court-decisions module.
- **Examination Guidelines** — large static PDFs; ship as raw downloads if
  needed rather than building a search tool.

## Open questions

1. **ServiceKey for non-Korean developers.** Registration requires identity
   verification "through a professional institution"; the standard Korean
   path uses i-PIN or Korean mobile-carrier verification, which foreigners
   cannot complete. Reported workarounds: (a) email `kiprisplus@kipi.or.kr`
   for a manual foreign-applicant account, (b) use the WIPO INSPIRE-listed
   contact channel, (c) partner with a Korean entity. Need to confirm which
   path actually works today and what turnaround looks like.
2. **Paid-tier pricing.** Free is 1,000 calls/month per service; the next
   tier's exact pricing is not published in English and appears to be
   per-product quote. Need to ask KIPI directly before promising production
   throughput.
3. **Redistribution.** ToS Articles 19-21 restrict redistribution of "Service
   Information" — unclear whether caching responses on a CoWork allowlist
   server constitutes redistribution. Need legal read before building a
   download_url surface like we did for USPTO bulk.
4. **English coverage gaps.** Trademark goods/services localize well, but
   patent specifications come back as Korean text only; English abstracts
   (KPA) are a separate paid product. Confirm whether KPA is in the free
   tier or only in a paid bundle.
5. **IPTAB structured access.** `trialInfoSearch` returns trial metadata, but
   full decision PDFs/HTML may require a separate endpoint or fall back to
   the KIPRIS web UI. Worth a one-day spike before committing to the
   patent-only v1 scope.

## Sources

- [KIPRIS Plus — Service Introduction](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300024)
- [KIPRIS Plus — API list](https://plus.kipris.or.kr/eng/data/service/List.do?subTab=SC001&menuNo=300100)
- [KIPRIS Plus — Terms of Use](https://plus.kipris.or.kr/eng/main/contents.do?menuNo=300030)
- [KIPRIS Plus — Service Fee](https://plus.kipris.or.kr/eng/use/paymentMmg.do?menuNo=310105)
- [WIPO INSPIRE — KIPRIS profile](https://inspire.wipo.int/kipris)
- [KIPO — Patent Examination Guidelines (Jan 2021)](https://www.kipo.go.kr/upload/en/download/Patent_Examination_Guidelines_2021.pdf)
- [KIPO — K-PION overview](https://www.kipo.go.kr/en/HtmlApp?c=50200&catmenu=ek02_05_03)
- [KIPO — IPTAB overview PDF](https://www.kipo.go.kr/upload/en/download/Intellectual%20Property%20Trial%20And%20Appeal%20Board_2018.pdf)
- [Korea Seed & Variety Service (EN)](https://www.seed.go.kr/seed_eng/index.do)
- [Korean Patent Act (KLRI EN translation)](https://elaw.klri.re.kr/eng_service/lawView.do?lang=ENG&hseq=59876)
- [UCPA (KIPO EN PDF)](https://www.kipo.go.kr/upload/en/download/UnfairAct.pdf)
- [Trademark Act (KLRI EN)](https://elaw.klri.re.kr/eng_service/lawView.do?hseq=60480&lang=ENG)
- [nuri428/mcp_kipris (GitHub)](https://github.com/nuri428/mcp_kipris)
- [seheeopark/kipris_rcode (R, GitHub)](https://github.com/seheeopark/kipris_rcode)
- [Korean Patent MCP — Glama listing](https://glama.ai/mcp/servers/@Tech-curator/korean-patent-mcp)
- [WIPO patent-judicial guide — Republic of Korea](https://www.wipo.int/patent-judicial-guide/en/full-guide/republic-of-korea)
- [Supreme Court of Korea — Leading IP High Court summaries PDF](https://file.scourt.go.kr/dcboard/1747184898044_100818.pdf)
