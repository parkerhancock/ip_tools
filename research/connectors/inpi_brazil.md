# INPI Brazil & Brazilian IP Data Source Survey

Connector-scoping survey for `patent-client-agents`. Brazil's INPI is the largest IP office in Latin America (≈30k patent filings, ≈300k trademark filings per year). The good news: INPI publishes a real, scriptable bulk feed (the RPI XML weekly) plus dados.gov.br datasets. The bad news: the live search UI (`busca.inpi.gov.br/pePI/`) is a 1990s ASP-style portal with a CAPTCHA and Portuguese-only labels, and there is no public REST API for any of it. Brazil's open-data culture sits between mature (EU/AU) and developing (IN/CN): more open than CNIPA, less mature than USPTO ODP.

## Cross-asset comparison

| # | Asset | URL | Auth | Format | Bulk? | Outside-Brazil feasibility |
|---|-------|-----|------|--------|-------|----------------------------|
| 1 | Busca de Patentes (pePI) | busca.inpi.gov.br/pePI/ | Free login + CAPTCHA | HTML scrape | No (use #5) | Hard — CAPTCHA, JS forms |
| 2 | Busca de Marcas (pePI) | busca.inpi.gov.br/pePI/ | Free login + CAPTCHA | HTML scrape | No (use #5) | Hard — same |
| 3 | Busca de Desenhos Industriais | busca.inpi.gov.br/pePI/ | Free login + CAPTCHA | HTML scrape | No (use #5) | Hard — same |
| 4 | INPI Open Data on dados.gov.br | dados.gov.br + gov.br/inpi/.../dados-abertos | None | CSV / XML / ZIP | Yes (annual + weekly) | **Easy** |
| 5 | Revista da Propriedade Industrial (RPI) | revistas.inpi.gov.br | None | PDF + ZIP+TXT + ZIP+XML | Yes (weekly, since 2017-01-31) | **Easy** |
| 6 | GI Registry | manualdeig.inpi.gov.br + RPI IG section | None for browse | HTML / PDF | Yes (via RPI) | Easy — small dataset |
| 7 | Topography of Integrated Circuits | gov.br/inpi/.../topografias | Filing requires login | HTML / PDF | Yes (via RPI) | Easy — very small dataset |
| 8 | Cultivar Registry (SNPC, MAPA) | sistemas.agricultura.gov.br/snpc/cultivarweb | None for browse | HTML + spreadsheet | Yes (spreadsheet refresh) | Easy |
| 9–16 | Statutes, guidelines, resoluções | planalto.gov.br, gov.br/inpi, WIPO Lex | None | HTML / PDF | Yes (static) | Easy |
| 17 | INPI administrative appeal decisions | Published in RPI | None | PDF blocks in RPI | Via RPI | Easy — RPI XML |
| 18 | Federal Justice (Justiça Federal, TRF2) | jusbrasil, lexml, court portals | None | HTML | Mostly no | Medium — fragmented |
| 19 | STJ / STF IP rulings | scon.stj.jus.br, jurisprudencia.stf.jus.br | None | HTML / search API-ish | Yes (search endpoints exist) | Medium |

## 1–3. pePI live search (Busca de Patentes / Marcas / Desenhos)

One servlet-based portal (`busca.inpi.gov.br/pePI/servlet/...Controller`) backs patents, trademarks, and industrial designs, switching on a `tipoRecurso` parameter.

- **URL:** `https://busca.inpi.gov.br/pePI/`. **Auth:** Free e-INPI account + CAPTCHA on session start (anonymous browse allowed but throttled).
- **Rate limits:** Undocumented; aggressive scraping triggers session resets and IP throttling.
- **Format:** Server-rendered HTML, ASP/JSP-era forms, JSESSIONID cookies, Portuguese-only labels.
- **Coverage:** Patents 1976-, trademarks 1991-, designs 1970s- (older records partial).
- **Bulk:** None — INPI explicitly routes bulk consumers to RPI (#5) and dados.gov.br (#4).
- **ToS:** Public-record data; commercial reuse permitted under Decreto 8.777/2016, but the live UI ToS prohibits automated scraping.
- **Python:** No maintained library. `ampla-api` (Java/Spring), Apify "INPI Trademark Checker" (commercial), Infosimples (commercial) — nothing on PyPI is current.

Read: don't wrap pePI. Wrap RPI + dados.gov.br and reconstruct the same data with proper joins.

## 4. INPI Open Data on dados.gov.br

The real story. INPI publishes on the Brazilian Open Data Portal (`dados.gov.br`) under Decreto 8.777/2016's open license, covering Patents, Trademarks, Industrial Designs, Computer Programs, and Technology Transfer Contracts.

- **URLs:** `dados.gov.br/organization/6fddb467-7b6c-4691-9ec1-2fb35229bf56` (INPI org); `gov.br/inpi/pt-br/acesso-a-informacao/dados-abertos` (INPI side).
- **Auth:** None. **Rate limits:** None enforced; static ZIPs on a CDN.
- **Format:** CSV + XML inside ZIPs. Annual patent biblio cuts (`bw-p-2019`, `bw-p-2020`, …), ~50–500 MB per ZIP. Inventor/applicant/agent + IPC + dispatch history.
- **Coverage:** Annual bibliographic for the five tracks; weekly companion is the RPI feed.
- **ToS:** Open license (free reuse, attribution INPI / Decreto 8.777/2016).
- **Python:** No INPI-specific library; `httpx` + `polars/pandas` is sufficient. The CKAN-style `dados.gov.br` API exposes dataset listings as JSON.

This is the spine of any Brazil connector.

## 5. Revista da Propriedade Industrial (RPI)

The weekly official bulletin. Every administrative act — filings, office actions, allowances, registrations, oppositions, appeals, GI grants, IC topography registrations, tech-contract registrations — publishes here. Issue #2879 dropped 2026-03-10; cadence is one issue per Tuesday.

- **URL:** `https://revistas.inpi.gov.br/rpi/`. PDFs at `revistas.inpi.gov.br/pdf/{Section}{Number}.pdf`; ZIP+TXT at `revistas.inpi.gov.br/txt/P{Number}.zip`; ZIP+XML at `revistas.inpi.gov.br/xml/{nomeArquivoEscritorio}` (filename resolved from a JSON manifest).
- **Auth:** None. **Rate limits:** None practical.
- **Format:** PDF (per section), ZIP+TXT, ZIP+XML. Eight sections: Comunicados, Contratos de Tecnologia, Desenhos Industriais, Indicações Geográficas, Marcas, Patentes, Programas de Computador, Topografia de Circuitos Integrados.
- **Coverage:** 2017-01-31 → present, all eight sections. Pre-2017 is PDF-only legacy.
- **Bulk:** Yes — every issue archived; dados.gov.br hosts the manifest. Encoded with INID + INPI dispatch codes (documented at "Códigos e Abreviações"). Schema docs at `gov.br/inpi/pt-br/backup/servicos/arquivos/rpi_xml_marcas_versao_103.pdf` and analogous for patents/designs; INPI publishes layout version bumps.
- **ToS:** Open license. **Python:** None purpose-built; Brazilian legal scrapers (`escavador`, `jusbrasil`) ingest RPI but don't expose it.

**This is the asset to wrap first.** Closest Brazilian analogue to USPTO PAIR + USPTO Trademark Daily XML, rolled into one.

## 6. GI Registry (Indicações Geográficas)

INPI administers Brazilian GIs under LPI Title IV (Arts. 176–182), distinguishing Indicação de Procedência (IP) from Denominação de Origem (DO). ~120 granted/pending as of 2025 (cachaça, Vale dos Vinhedos, cafés do Cerrado Mineiro). Browse via `servicos.busca.inpi.gov.br`; acts publish in the RPI IG section; manual at `manualdeig.inpi.gov.br`. No standalone API — derive from RPI XML, no separate scraper.

## 7. Topography of Integrated Circuits

Brazilian sui generis IC layout protection under **Lei nº 11.484/2007** (also instituted PADIS/PATVD semiconductor incentives). 10-year term from filing or first exploitation. Very low volume (<100 filings/year). Browse at `gov.br/inpi/pt-br/servicos/topografias-de-circuitos-integrados`; acts publish in the RPI "Topografia" section. Niche; derive from RPI XML.

## 8. Cultivar Registry / Plant Variety Rights — SNPC (not INPI)

Brazilian PVP is **outside INPI**: the SNPC (Serviço Nacional de Proteção de Cultivares), inside MAPA, administers Lei 9.456/1997 + Decreto 2.366/1997. Two registries — RNC (commerce admission) and SNPC protection (sui generis IP right, UPOV 1978).

- **URLs:** `sistemas.agricultura.gov.br/snpc/cultivarweb/cultivares_registradas.php` (RNC); `.../cultivares_protegidas.php` (PVP). **Auth:** None.
- **Format:** HTML forms + downloadable spreadsheet (quarterly; last refresh 2026-04-04). Spreadsheet is the bulk channel.
- **Coverage:** RNC ~50k+ varietal entries; PVP registry ~5k granted. **Python:** None.

Easy connector — functionally parallel to MARA PVP (China) and USDA PVP Office.

## 9–16. Substantive law sources

Brazil's IP statutes are unusually consolidated: **one master law (LPI 9.279/1996) covers patents, utility models, designs, marks, GIs, and trade-secret/unfair-competition**. Most jurisdictions split these. For our static-law module pattern this is a feature — one mirrored corpus, articulated by Title, gets you 80% of the IP-law surface.

| # | Law / source | Best URL | Notes |
|---|--------------|----------|-------|
| 9 | LPI — Lei 9.279/1996 | `planalto.gov.br/ccivil_03/leis/l9279.htm` + WIPO Lex (EN) | Patents (Title I), Designs (Title II), Marks (Title III), GIs (Title IV), Trade secrets / unfair competition (Title V, Art. 195) |
| 10 | Software Law — Lei 9.609/1998 | `planalto.gov.br/ccivil_03/leis/l9609.htm` | Copyright-equivalent; INPI keeps the registry |
| 11 | Copyright Law — Lei 9.610/1998 | `planalto.gov.br/ccivil_03/leis/l9610.htm` | Administered outside INPI (FBN, EBC) |
| 12 | PVP Law — Lei 9.456/1997 + Decreto 2.366/1997 | `planalto.gov.br/ccivil_03/leis/l9456.htm` | Administered by SNPC/MAPA |
| 13 | IC Topographies — Lei 11.484/2007 | `planalto.gov.br/ccivil_03/_ato2007-2010/2007/lei/l11484.htm` | Administered by INPI |
| 14 | Trade Secrets | LPI Art. 195 — no separate statute | Article-level mirror sufficient |
| 15 | Diretrizes de Exame | `gov.br/inpi/pt-br/assuntos/patentes/consultas-publicas/` | Bloco I (Res. 124/2013, republicada Portaria DIRPA 16/2024); Bloco II (Res. 169/2016); Manual de Marcas; Manual de IGs |
| 16 | Resoluções / Portarias | RPI Comunicados + `gov.br/inpi/pt-br/backup/centrais-de-conteudo/legislacao` | Recent: Portaria DIRPA 14/2024 (form/content); Portaria PR 48/2024 (PPH V); Portaria MDIC 110/2025 (fees); Portaria DIRPA 02/2026 (macroprocess) |

**Authoritative URLs:** `planalto.gov.br` is the official federal-law repository; `lexml.gov.br` is a federated metadata catalog; WIPO Lex carries solid EN translations of LPI / 9.456 / 11.484 / Bloco I & II with modest lag. **PT-only:** Manual de Marcas, Manual de IGs, and most Portarias. INPI's English portal (`gov.br/inpi/en`) is thin marketing, not regulatory.

## 17. INPI administrative appeal decisions

Brazil's INPI handles recurso/administrative-nullity internally; decisions publish in the RPI under per-section dispatch codes (no PTAB-style portal, no JSON feed, no search UI beyond pePI). Access path: parse RPI XML and filter by dispatch code.

## 18. Federal Justice (Justiça Federal)

Patent **nullity** is exclusively federal (INPI is a mandatory party); patent **infringement** sits in state courts unless joined with nullity. The **TRF2** (Rio de Janeiro / Espírito Santo) houses Brazil's specialized IP bench — five trial-level IP-and-pension courts + two specialized appellate panels; most life-sciences/pharma IP funnels through it. Each TRF runs its own e-process portal (`eproc.trf2.jus.br` etc.); public consultation works without OAB digital cert for non-sealed cases; no unified federal docket API. HTML + PDF; bulk only via commercial aggregators (`jusbrasil.com.br`, `escavador.com`).

## 19. STJ / STF IP rulings

- **STJ:** Jurisprudence search at `scon.stj.jus.br/SCON/`. HTML search; URL parameters are stable but undocumented. Landmark 2024 ruling allowed state infringement courts to decide patent nullity incidentally without federal referral.
- **STF:** `jurisprudencia.stf.jus.br` — constitutional IP matters are rare but notable (2021 ADI 5529 struck down LPI Art. 40 sole-paragraph patent-term extension).
- HTML + PDF acórdãos; no official bulk dump.

## Existing Brazilian-developer landscape

Active but commercial-leaning: **infosimples** (paid REST for INPI marks/patents), **Apify "INPI Trademark Checker"** (commercial scraper-as-a-service), **Signa** (commercial TM + EN translation), **ampla-api** (GitHub Java/Spring, demo-quality). No maintained PyPI package targets INPI as of May 2026. Same pattern as CNIPA — open data exists, scraping monetizers keep their code closed.

## Recommended v1 scope

Ship what's open, scriptable, and won't break on the next CAPTCHA refresh.

1. **`inpi_rpi`** — RPI weekly bulletin: list issues, fetch manifest, download ZIP+XML by section, parse INID/dispatch codes into Pydantic models. Load-bearing.
2. **`inpi_opendata`** — dados.gov.br annual biblio dumps for patents/trademarks/designs. Thin CKAN wrapper + ZIP+CSV reader. Pairs with RPI for current vs. historical.
3. **`brazil_law`** — static mirror of LPI 9.279, Lei 9.609, Lei 9.610, Lei 9.456, Lei 11.484, Bloco I + Bloco II, Manual de Marcas. Articulated by Title/Article like MPEP/TMEP. LPI's unified-statute design fits the static module pattern unusually well — one corpus replaces 4–5 statute mirrors.

Optional v2: **`snpc_cultivar`** (RNC + PVP spreadsheet, separate org), **STJ jurisprudence** (HTML scrape of `scon.stj.jus.br` for doctrine).

## Skip list

- **pePI scraping** — CAPTCHA + ToS-hostile + brittle; RPI XML + dados.gov.br reconstruct the same data.
- **e-INPI filing flows** — out of scope for a read-only library.
- **TRF/PJe court dockets** — fragmented per region, no API, sealed-record handling; use commercial aggregators if needed.
- **Commercial aggregators (Jusbrasil, Escavador, Signa, Infosimples)** — optional credentialed plugins, not core.
- **Standalone trade-secrets statute** — doesn't exist; cite LPI Art. 195.

## Open questions

1. **RPI XML schema versioning** — INPI bumps layouts (`...versao_103.pdf`) periodically. Pin and migrate, or auto-detect?
2. **dados.gov.br vs. RPI overlap** — annual biblio dumps recap weekly RPI. Both, or RPI-only with year-aggregation?
3. **Portuguese MT** — keep records in PT and rely on caller-side translation, or ship optional EN MT for title/abstract like the CNIPA strategy?
4. **STJ search stability** — `scon.stj.jus.br` works today but isn't a documented API. How fragile?
5. **Examination Guidelines lag** — Bloco II is from 2016; DIRPA 02/2026 modifies practice. Annotate the EN translation with a PT-only diff?
6. **Programas de Computador registry** — administrative, not a patent. Separate model, or fold into RPI parsing?

## Compare / contrast: INPI Brazil vs. CNIPA vs. USPTO ODP

| Dimension | INPI Brazil | CNIPA | USPTO ODP |
|-----------|-------------|-------|-----------|
| Bulk data | **RPI XML weekly + dados.gov.br annual** | Contract-only, Chinese entity required | Comprehensive ODP + bulk |
| Public REST API | None documented | None documented | Yes, OpenAPI'd, keyed |
| CAPTCHA on live search | Yes (pePI) | Yes (PSS + SBJ) | No |
| Language | PT-only UI; EN translations for statutes | CN-only; EN lags | English-native |
| Open license | Decreto 8.777/2016 — explicit | Restricted | Public domain |
| Court records | Fragmented federal portals | wenshu closed since 2021 | PACER (paid) |
| Existing Python lib | None on PyPI | None solid | `patent_client`, ODP SDKs |

**Open-data maturity:** INPI Brazil sits between mature (USPTO/EU/AU) and developing (IN/CN). The RPI XML feed — weekly, structured, open-licensed, stable schema — puts Brazil ahead of CNIPA and roughly on par with IPO India. What's missing is the documented REST API on top. For a connector library this is fine: bulk-XML + static law mirror is a cleaner integration target than a flaky JS-rendered search portal.

## Sources

- INPI: [INPI portal PT](https://www.gov.br/inpi/pt-br) · [INPI portal EN](https://www.gov.br/inpi/en) · [pePI](https://busca.inpi.gov.br/pePI/) · [Plataforma de Serviços](https://servicos.busca.inpi.gov.br/) · [Dados Abertos](https://www.gov.br/inpi/pt-br/acesso-a-informacao/dados-abertos) · [INPI Open Data announcement](https://www.gov.br/inpi/pt-br/central-de-conteudo/noticias/inpi-disponibiliza-dados-abertos-sobre-cinco-servicos)
- RPI: [Revista RPI](https://revistas.inpi.gov.br/rpi/) · [RPI Marcas XML schema manual](https://www.gov.br/inpi/pt-br/backup/servicos/arquivos/rpi_xml_marcas_versao_103.pdf)
- Dados.gov.br: [INPI org page](https://dados.gov.br/organization/6fddb467-7b6c-4691-9ec1-2fb35229bf56) · [RPI dataset](https://dados.gov.br/dataset/revista-da-propriedade-industrial-rpi) · [RPI de Patentes resource](https://dados.gov.br/lt/dataset/7aa82f39-45c1-4f8c-a06f-9a3caff26bfc/resource/4288c07c-f9bd-45d7-8fc0-56b4fc1f5c82) · [Pedidos de Patentes 2020](https://dados.gov.br/dataset/bw-p-2020)
- Statutes (Planalto): [Lei 9.279/1996 — LPI](https://www.planalto.gov.br/ccivil_03/leis/l9279.htm) · [Lei 9.456/1997 — PVP](https://www.planalto.gov.br/ccivil_03/leis/l9456.htm) · [Decreto 2.366/1997](https://www.planalto.gov.br/ccivil_03/decreto/1997/d2366.htm) · [Lei 11.484/2007](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2007/lei/l11484.htm)
- Guidelines & manuals: [Diretrizes Bloco I PDF](https://www.gov.br/inpi/pt-br/assuntos/patentes/consultas-publicas/arquivos/diretriz_de_exame_de_patente_retificado_original_1.pdf) · [WIPO Lex Bloco I](https://www.wipo.int/wipolex/en/legislation/details/16926) · [WIPO Lex Bloco II](https://www.wipo.int/wipolex/en/legislation/details/16927) · [Manual de Marcas](https://manualdemarcas.inpi.gov.br/) · [Manual de IGs](https://manualdeig.inpi.gov.br/projects/manual-de-indicacoes-geograficas/wiki)
- GIs / IC topography: [INPI IG guia básico](https://www.gov.br/inpi/pt-br/servicos/indicacoes-geograficas/guia-basico) · [INPI Topografia legislação](https://www.gov.br/inpi/pt-br/servicos/topografias-de-circuitos-integrados/legislacao-topografia-de-circuitos-integrados)
- SNPC / cultivars: [CultivarWeb RNC](https://sistemas.agricultura.gov.br/snpc/cultivarweb/cultivares_registradas.php) · [CultivarWeb PVP](https://sistemas.agricultura.gov.br/snpc/cultivarweb/cultivares_protegidas.php) · [MAPA cultivares registradas](https://www.gov.br/agricultura/pt-br/acesso-a-informacao/acoes-e-programas/cartas-de-servico/defesa-agropecuaria-sementes-e-mudas/informacoes-sobre-cultivares-registradas)
- Courts: [WIPO Patent Judicial Guide — Brazil](https://www.wipo.int/patent-judicial-guide/en/full-guide/brazil/3.3) · [IPWatchdog on STJ 2024 invalidity ruling](https://ipwatchdog.com/2024/10/29/brazils-superior-court-justice-rules-infringement-courts-can-hear-invalidity-arguments/) · [Lexology — Brazilian patent specialization](https://www.lexology.com/library/detail.aspx?g=ff316cb9-527a-4144-b2f9-11768f19d6ab) · [Chambers Patent Litigation 2025 Brazil](https://practiceguides.chambers.com/practice-guides/patent-litigation-2025/brazil/trends-and-developments)
- Practice notices: [Kasznar Leonardos — Portarias 2024](https://www.kasznarleonardos.com/atualizacao-importante-novas-regras-publicadas-pelo-instituto-nacional-de-propriedade-industrial-inpi/) · [Simões IP — Portaria DIRPA 14/2024](https://www.simoes-ip.com/o-inpi-estabelece-novas-normas-gerais-quanto-a-forma-e-ao-conteudo-dos-pedidos-de-patentes-e-certificados-de-adicao/) · [Montaury — Portaria MDIC 110/2025 fees](https://montaury.com.br/pt/atualizacoes-na-tabela-de-taxas-do-inpi-novas-portarias-publicadas) · [IDS — PPH Phase V](https://ids.org.br/noticia/inpi-publica-portaria-inpi-pr-no-48-2024-que-institui-a-fase-v-do-projeto-piloto-pph/)
- Commercial / context: [Signa INPI Brazil](https://signa.so/offices/inpi-brazil) · [Apify INPI Trademark Checker](https://apify.com/cloway/inpi-trademark-checker/api) · [MarketBlast Brazilian Patent Search Guide](https://marketblast.com/patents_&_trademarks/how_to_do_a_brazilian_patent_search/) · [WIPO ATR PI Brazil 2024](https://confluence.wipo.int/confluence/spaces/ATR/pages/1640667784/CWS+ATR+PI+2024+BR)
