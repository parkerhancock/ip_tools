# Rospatent / Russia IP Data Source Survey

Tier-3 survey for `patent-client-agents`. Russia is a top-10 filing
jurisdiction by raw volume but, post-February 2022, sits inside an adverse
compliance, infrastructure, and reciprocity environment that makes it
materially different from the CNIPA decision (which is hard but not legally
fraught). **Verdict up front: skip the live Russian sources at v1, ship a thin
static-law + EPO-OPS-RU shape, and revisit when the sanctions environment
changes.**

## TL;DR feasibility matrix

| # | Asset | URL | Auth | Outside-RU feasibility | Sanctions-clean? |
|---|-------|-----|------|------------------------|------------------|
| 1 | FIPS public search | `new.fips.ru/en/` | Account on heavy use | Functional but intermittent | Reading: OK |
| 2 | Rospatent open data + open APIs | `online.rospatent.gov.ru/open-data` | Free reg.; RU phone in practice | Brittle — RU-mobile / Gosuslugi gate | Reading: OK |
| 3 | searchplatform.rospatent.gov.ru | `searchplatform.rospatent.gov.ru/` | Free reg. | Unstable from US/EU IPs | Reading: OK |
| 4 | Civil Code Part 4 (statute) | WIPO Lex 22106 / 12785 | None | Easy — use WIPO Lex | Clean |
| 5 | Decree 299 (2022) text | `pravo.gov.ru` + mirrors | None | Easy — secondary mirrors | Clean |
| 6 | IP Court (`ipc.arbitr.ru`) | `ipc.arbitr.ru`, `kad.arbitr.ru` | None for index | RU-only, anti-bot | Reading: OK |
| 7 | EAPO / EAPATIS | `eapo.org`, EAPATIS | Free guest | Functional | USPTO/EPO terminated engagement |
| 8 | EPO OPS RU coverage | already wrapped | EPO key | Reduced — biblio mostly OK, legal-status patchy | Clean |

---

## 1. FIPS / Rospatent public search (`new.fips.ru`)

FIPS (the Federal Institute of Industrial Property under Rospatent) runs the
public databases for inventions, utility models, industrial designs,
trademarks, appellations of origin, and Madrid extensions to RU. Search UI is
HTML/JS form posts — no documented REST contract. EN labels exist on `/en/`,
but record content is Russian unless an EN abstract field exists. Anonymous
lookups work for low volume; sustained access needs an account. No maintained
Python client; stale GitHub scrapers break on the JS form.

## 2. Rospatent open data + open APIs

There is an official surface at `online.rospatent.gov.ru/open-data` and an
"open API" page, plus a modern SPA front-end at
`searchplatform.rospatent.gov.ru`. In practice: registration flows through
Gosuslugi (the Russian government identity service) and need a Russian phone
number; docs are Russian-only; schema drift; portals go intermittently
inaccessible from Western IP ranges. Not buildable from a US/EU codebase
without a specialty integration partner.

## 3. Russian Patent Law — Civil Code Part 4 (the one thing worth shipping)

The only cleanly accessible, licensable RU IP asset from outside Russia.
Federal Law No. 230-FZ (18 Dec 2006), in force 2008-01-01, Part 4 of the
Civil Code: 9 chapters / 326 articles (1225–1551) covering copyright,
neighboring rights, patents (inventions, utility models, industrial designs),
trademarks, GIs, trade secrets, plant varieties, IC topographies,
licensing/assignment.

- **Best EN source:** WIPO Lex 22106 (consolidated through 29 Jun 2023), with
  earlier consolidations at 21655 and 21301. Authoritative WIPO translation;
  PDF + HTML.
- **Backup:** JPO hosts an EN PDF (`jpo.go.jp/e/system/laws/gaikoku/document/index/russia-e_minpou_no4.pdf`).
- **Ship pattern:** mirror into the planned `StaticLawCorpus` base alongside
  DE/UK/BR/IN/CN. ~1 day, no live RU dependency.

## 4. Decree 299 (2022) — compulsory use without compensation

The signature post-2022 RU IP-policy instrument. Decree of the Government of
the RF No. 299 of 6 Mar 2022 amends the methodology under **Article 1360 of
the Civil Code** (state-interest compulsory licensing). For patent holders
connected to states on Russia's "unfriendly countries" list (48 jurisdictions
including US, UK, EU, AU, CA, JP, KR, CH, SG), the compensation rate for
unauthorized use of inventions, utility models, and industrial designs is set
to **0% of proceeds**. Operates only when the RU government issues a separate
order designating specific patents — as of early 2026 only a handful of such
orders are in the open record, and tracking is incomplete. Widely viewed as
facially incompatible with **TRIPS Article 31** ("adequate remuneration" for
compulsory licensing); no WTO dispute has been adjudicated.

**Connector implication:** Decree 299 is *substantive policy*, not a data
source. There is no Decree-299 register to scrape. The right product
treatment is to surface the decree text in the static-law module and treat it
as an annotation/risk-flag concept for any future RU portfolio view. **Do not
promise users a "Decree 299 patent list"** — there is no canonical one.

Related: **Decree 430 (20 May 2024)** — RU persons need a Government
Commission approval to *acquire* IP rights from unfriendly-state persons.
One-way valve on RU IP transactions. Same static-law treatment.

## 5. IP Court of the Russian Federation (Суд по интеллектуальным правам)

Specialized IP court inside the arbitrazh (commercial-court) system since
3 Jul 2013. First-instance court for Rospatent appeals (revocation,
invalidation, examination decisions); cassation court for IP infringement
tried in lower commercial courts.

- **URL:** `https://ipc.arbitr.ru/` (Russian only); cases also surface in
  general arbitrazh case-management at `kad.arbitr.ru`.
- **API:** None official. Russian commercial scrapers (parser-api.com,
  api-cloud.ru, damia.ru) sell access to kad.arbitr.ru, not IP-Court-specific.
  Open-source scrapers (`newpointer/autokad`, `kontragentio/api`) target
  kad.arbitr.ru internal endpoints; unmaintained.
- **Volume:** ~3,000–4,000 IP cases/year through the IP Court; RU-language PDFs.

Reaching this from a US/EU stack means scraping an anti-bot RU site or paying
a RU aggregator. Not sane for v1.

## 6. Sanctions context — the load-bearing analysis

What flips Rospatent from "Tier-3 brittle integration" (CNIPA-shaped) to
**wait-or-skip**:

**OFAC (US).** Russian Harmful Foreign Activities Sanctions Regs (31 CFR
Part 587) broadly prohibit dealings with sanctioned RU persons. **General
License 31 (5 May 2022)** explicitly authorizes filing, prosecuting,
maintaining, and defending patents/TMs/copyrights in either direction —
including with Rospatent and EAPO. GL 31 covers IP *transactions*; reading
public Rospatent data and citing it is well inside the GL 31 perimeter.

**EU (Reg. 833/2014, 14th package, in force 25 Jun 2024).** Article 5s
prohibits EU IP offices from *accepting new filings* from RU persons. A
filing-side block, not a data-access block — EU practitioners can still read
RU registers. From Dec 2024, EU persons must include a "no-use-in-Russia" IP
clause in license/transfer agreements for items on the Common High Priority
Items List.

**USPTO (22 Mar 2022).** Terminated all engagement with Rospatent, EAPO, and
Belarus IP office. GPPH with Rospatent terminated (Federal Register 4 Apr
2022); PCT applicants warned away from Rospatent as ISA/IPEA. No MoU activity.

**EPO.** Suspended cooperation with Rospatent and EAPO; on 10 Jul 2024
refused unitary-effect requests from Russian applicants. INPADOC RU
bibliographic coverage continues; **RU legal-status events were partial even
pre-2022** per EPO/CAS coverage docs.

**WIPO.** Has *not* formally suspended Russia from PCT, Madrid, or Hague.
WIPO Russia office activities were reduced and politically contested but
remain technically operating — Ukraine has pushed for full suspension; WIPO
has resisted citing multilateral-treaty obligations.

**Russia-side hostility.** Decree 299 (0% compensation); Decree 430 (acquisition
gate); broken SWIFT payment rails forcing maintenance via RU counsel paying in
rubles; many Western firms have withdrawn from RU practice entirely.

**Compliance net for this library.** Reading public RU/FIPS/EAPO data:
permitted. Caching and re-exposing through our MCP tool: permitted (same
posture as EPO OPS RU coverage). The law lets us build this. The economics
don't justify it — small US/EU user base for live RU register reads, declining
data quality, brittle integration, and a state that has explicitly abrogated
reciprocity. **CNIPA is hard but not hostile** (CN courts still pay Western
patentees, IP5 cooperation continues). RU is both hard *and* hostile.

## 7. Eurasian Patent Office (EAPO)

Regional patent org headquartered in Moscow under the 1994 Eurasian Patent
Convention. Member states (8): Armenia, Azerbaijan, Belarus, Kazakhstan,
Kyrgyzstan, Russia, Tajikistan, Turkmenistan. Separate legal entity from
Rospatent but operationally entwined. Issues single Eurasian patents; recently
extended to industrial designs.

- **Data assets:** EAPATIS (~90M docs incl. PCT minimum docs); Eurasian
  Publication Server; Eurasian Patent Register; Eurasian Pharmaceutical
  Register.
- **Access:** Guest mode free for EA-numbered docs and CISPATENT (EN
  abstracts); paid for full search. No documented REST API.
- **Sanctions status:** USPTO termination explicitly covers EAPO. OFAC has not
  designated EAPO institutionally. EPO suspended cooperation. EU 14th-package
  filing-block applies to RU/BY applicants but EAPO itself remains operational.
- **Inspire entries:** `inspire.wipo.int/eurasian-patent-information-system-eapatis`,
  `inspire.wipo.int/eurasian-patent-register`.

**Treatment:** same as Rospatent — read-only utility, low practitioner demand,
better served via EPO OPS biblio fallback.

---

## v1 scope — **SKIP** (with a small static-law carve-out)

| Rank | Module | Source | Why |
|---|---|---|---|
| 1 | `ru_statutes` (part of unified static-law base) | WIPO Lex 22106 (Civil Code Part 4) + Decree 299 + Decree 430 | One day; same `StaticLawCorpus` pattern as DE/UK/BR/IN/CN. Solves ~80% of agent use cases for RU patent law. |
| 2 | RU coverage via existing `epo_ops` | INPADOC | Already free, already wrapped. Add a `get_ru_biblio` recipe; document the legal-status gap. |

That's the entire v1 scope. **Do not build:** a FIPS scraper, a Rospatent
open-API client, a `searchplatform.rospatent.gov.ru` wrapper, an EAPATIS
client, an IP Court / arbitrazh scraper, or any Decree-299 patent-list
tracker.

## Skip list

- **FIPS / new.fips.ru scraping** — JS form, undocumented contract, RU-mobile
  gate on registration, intermittent reachability. EPO OPS gives us biblio.
- **Rospatent open API portal / searchplatform** — Gosuslugi-gated;
  Russian-only docs; schema drift.
- **EAPATIS scraping** — guest mode is weak; full mode paid + RU-side contract;
  USPTO terminated cooperation.
- **IP Court / `ipc.arbitr.ru` / `kad.arbitr.ru` scrapers** — RU-language,
  anti-bot, no clean API, third-party scrapers are RU vendors.
- **Decree-299-affected-patent registry** — does not exist as a canonical list.
- **Rospatent / EAPO bulk data contracts** — RU counterparty, ruble payment,
  sanctions due diligence we don't want to own.
- **Russian commercial aggregators (PatentInfo, Yandex Patents)** — small
  market, RU docs, ruble billing, secondary-sanctions risk.

## Open questions (only relevant if/when we revisit)

1. Does the OFAC/EU posture loosen? Trigger for re-survey.
2. Is there a reliable secondary tracker for which specific patents the RU
   government has designated under Decree 299? (Lidings, Gorodissky,
   pravo.gov.ru decree gazette mirror.)
3. EAPO industrial-design extension (since 2021) — what's covered in EPO OPS
   / Hague Express?
4. RU legal-status backfill — INPADOC RU legal-status was incomplete even
   pre-2022. Document the gap; don't promise filings/lapse alerting based on it.
5. Rospatent open API — does it ever publish EN docs and drop the Gosuslugi
   gate? Watch quarterly.

## Comparison with CNIPA

| Dimension | CNIPA | Rospatent |
|---|---|---|
| **Volume & demand** | World's #1 filer; every US practice cares | ~#8–10 globally pre-2022; Western demand collapsed post-2022 |
| **Reciprocity** | Hard but good-faith; CN enforces foreign patents and pays damages | Decree 299 sets foreign-patentee compensation to 0% on invoked patents |
| **Sanctions exposure** | None (some export-control on tech transfers, not on data) | OFAC GL 31 needed for filing/prosecution; payment rails broken; USPTO/EPO terminated engagement |
| **Buildable workaround** | EPO OPS + Patentscope cover ~95% of practical CN biblio | EPO OPS RU biblio + static Civil Code Part 4 cover ~90% of what an agent needs |
| **Verdict** | Build the EPO-OPS-extension + static-law shape; skip live PSS/SBJ | Build *only* the same shape (static-law + EPO-OPS-RU recipes); skip everything live |

The asymmetry is the verdict: for CN the *workaround* is the v1 ship. For RU,
**the workaround is the whole product** — no live-source upside to add.

## Sources

- [Rospatent EN](https://rospatent.gov.ru/en) · [FIPS EN](https://www.fips.ru/en/) · [new.fips.ru EN databases](https://new.fips.ru/en/informational-resources/information-retrieval-system/databases.php) · [Rospatent open data](https://online.rospatent.gov.ru/open-data) · [Rospatent open APIs](https://online.rospatent.gov.ru/open-data/open-api) · [searchplatform.rospatent.gov.ru](https://searchplatform.rospatent.gov.ru/) · [WIPO Inspire — RU patent base](https://inspire.wipo.int/russian-patent-base)
- Civil Code Part 4: [WIPO Lex 22106 (2023)](https://www.wipo.int/wipolex/en/legislation/details/22106) · [21655](https://www.wipo.int/wipolex/en/legislation/details/21655) · [21301](https://www.wipo.int/wipolex/en/legislation/details/21301) · [12785 (Parts 1–4)](https://www.wipo.int/wipolex/en/legislation/details/12785) · [JPO mirror](https://www.jpo.go.jp/e/system/laws/gaikoku/document/index/russia-e_minpou_no4.pdf)
- Decree 299 / Article 1360: [Morgan Lewis](https://www.morganlewis.com/pubs/2022/04/russian-decree-undermines-value-of-certain-patents-uspto-cuts-all-ties-with-russian-patent-office) · [IP Law Watch](https://www.iplawwatch.com/2022/03/28/the-kremlins-intellectual-property-cold-war-legalizing-patent-theft-with-decree-299/) · [Baker McKenzie](https://sanctionsnews.bakermckenzie.com/russia-adopts-zero-compensation-to-patent-owners-from-unfriendly-countries/) · [Gorodissky](https://www.gorodissky.com/publications/articles/russia-does-not-abolish-intellectual-property-rights/) · [William Fry](https://www.williamfry.com/knowledge/russia-issues-decree-providing-for-0-compensation-for-the-unauthorised-use-of-certain-ip-rights-emanating-from-unfriendly-countries/)
- USPTO / PCT / PPH: [USPTO statement](https://www.uspto.gov/about-us/news-updates/uspto-statement-engagement-russia-and-eurasian-patent-organization) · [USPTO update](https://www.uspto.gov/about-us/news-updates/update-interactions-rospatent) · [Fed. Reg. GPPH termination](https://www.federalregister.gov/documents/2022/04/04/2022-06885/termination-of-global-patent-prosecution-highway-with-rospatent) · [Finnegan](https://www.finnegan.com/en/insights/blogs/prosecution-first/for-the-uspto-russia-is-no-longer-a-stop-on-the-pph.html) · [AIPLA Russia resources](https://www.aipla.org/advocacy/international/other-international/current-resources-for-practice-with-russia)
- OFAC GL 31 / Decree 430: [Wilson Sonsini](https://www.wsgr.com/en/insights/russia-sanctions-update-intellectual-property-general-license-and-a-prohibition-on-the-provision-of-some-services.html) · [Thompson Hine](https://www.thompsonhinesmartrade.com/2022/05/ofac-issues-general-license-related-to-patents-trademarks-and-copyrights-in-russia/) · [Cleary — Decree 430](https://www.clearygottlieb.com/news-and-insights/publication-listing/new-russian-decree-imposes-restrictions-on-transfer-of-ip-rights) · [Hogan Lovells](https://www.hoganlovells.com/en/publications/at-the-crossroads-of-ip-and-russia-sanctions-what-ip-rights-holders-need-to-know)
- EU 14th package: [Gleiss Lutz](https://www.gleisslutz.com/en/news-events/know-how/foreign-trade-law-update-14th-package-eu-sanctions-against-russia) · [Skadden](https://www.skadden.com/insights/publications/2024/07/eus-14th-sanctions-package) · [Austrian Patent Office](https://www.patentamt.at/en/all-news/news-detail/artikel/sanktionspaket-der-eu-gegen-russland)
- EPO posture: [Lexology — EPO refuses RU](https://www.lexology.com/library/detail.aspx?g=b61bed70-a24e-4561-9bc9-cef2a58b549c) · [OlarteMoure — unitary effect](https://olartemoure.com/en/epo-will-reject-unitary-effect-requests-from-russian-applications/) · [INPADOC country coverage](https://cas-stnext.zendesk.com/hc/en-us/articles/30921938483085-INPADOCDB-and-INPAFAMDB-Country-Coverage) · [INPADOC legal status](https://cas-stnext.zendesk.com/hc/en-us/articles/30922098616333-INPADOCDB-and-INPAFAMDB-Legal-Status)
- WIPO Russia: [WIPO Office in Russia](https://www.wipo.int/about-wipo/en/offices/russia/) · [WIPO joint statement RU/UA](https://www.wipo.int/pressroom/en/global_ip_services_joint_statement.html) · [INTA RU/UA](https://www.inta.org/resources/the-status-of-intellectual-property-in-russia-and-ukraine/) · [Managing IP — sanctions toothless](https://www.managingip.com/article/2a5d0zxo7uj1lvmz9m6m8/ip-sanctions-toothless-as-russia-filings-so-low-data)
- IP Court / arbitrazh: [WIPO Magazine — IP Court](https://www.wipo.int/wipo_magazine/en/2014/01/article_0006.html) · [Lexology — RU IP](https://www.lexology.com/library/detail.aspx?g=d0c4cf87-35a7-46a2-9d22-e1e653291dd7) · [Parser-API kad.arbitr.ru](https://www.parser-api.com/kad-arbitr-ru) · [autokad (GitHub)](https://github.com/newpointer/autokad)
- EAPO: [EAPO EN](https://www.eapo.org/en/) · [Inspire EAPATIS](https://inspire.wipo.int/eurasian-patent-information-system-eapatis) · [Inspire EA Register](https://inspire.wipo.int/eurasian-patent-register) · [WIPO Magazine — EAPO expansion](https://www.wipo.int/wipo_magazine/en/2019/01/article_0004.html)
