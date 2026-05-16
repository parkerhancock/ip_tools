# DPMA (Deutsches Patent- und Markenamt) — Live API Discovery

**Research date:** 2026-05-16
**Question:** Does DPMA expose a queryable REST/JSON/XML/SOAP API we can proxy at runtime, with zero on-our-side infrastructure beyond an HTTP client?
**TL;DR:** Yes, a clean REST API exists (DPMAconnectPlus). **No, we cannot proxy it under our zero-infra model.** Access requires a signed paper contract, a one-time EUR 200 connection fee, and — critically — § 3.2 of the standard contract **prohibits passing the data to third parties** (which is exactly what a proxy does). Verdict: **RED.**

---

## 1. Endpoint

DPMA runs three parallel access products. Only **DPMAconnectPlus** is a clean REST API; the legacy SOAP service (just "DPMAconnect") is being deprecated; "DPMAdatenabgabe" is the bulk-download product that DPMAconnectPlus also fronts.

**Service home:** [DPMAconnectPlus overview (English)](https://www.dpma.de/english/search/data_supply_services/dpmaconnect/index.html)
**Interface spec (PDF, German):** [Schnittstellenbeschreibung DPMAconnectPlus](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf)
**Legacy SOAP spec (PDF, German):** [DPMAconnect API-Beschreibung](https://www.dpma.de/docs/recherche/dienste/dpmaconnectapibeschreibung.pdf)

**Base URL:** `https://dpmaconnect.dpma.de/dpmaws/rest-services/`

Three sibling services, one per IP right (per the [DPMAconnectPlus interface spec](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf), pp. 2–12):

| IP right | Service path | Search endpoint | Detail endpoint |
|---|---|---|---|
| Patents + Utility Models (Gebrauchsmuster) | `DPMAregisterPatService` | `…/DPMAregisterPatService/search/<expert-query>` | `…/getRegisterInfo/<Aktenzeichen>` |
| Trade Marks | `DPMAregisterMarkeService` | `…/DPMAregisterMarkeService/search/<expert-query>` | `…/getRegisterInfo/<Aktenzeichen>` |
| Designs | `DPMAregisterGsmService` | `…/DPMAregisterGsmService/search/<expert-query>` | `…/getRegisterInfo/<Designnummer>` |

Example call from the spec:
```
https://dpmaconnect.dpma.de/dpmaws/rest-services/DPMAregisterPatService/search/<expert-query-as-URL-encoded-string>
```

There is **no public-facing patents/trademarks REST API** outside DPMAconnectPlus. DEPATISnet (`depatisnet.dpma.de`) and DPMAregister (`register.dpma.de`) are HTML applications; programmatic access funnels through DPMAconnectPlus by design — see the consolidation announcement in [Mitteilung Nr. 9/19](https://www.dpma.de/dpma/veroeffentlichungen/mitteilungen/archiv/2019/mdp_09_2019.html) which folded the prior services (DPMAconnect SOAP, DPMAdatenabgabe, DEPATISconnect) into DPMAconnectPlus effective 1 January 2020.

## 2. Authentication

**HTTP Basic** over TLS. From [Schnittstellenbeschreibung DPMAconnectPlus](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf) p. 1:

> "Die REST Web Services arbeiten mit Basic Authentifizierung. Jeder Funktion der drei Web Services müssen dafür im HTTP Header 'Authorization' der Benutzername und das Benutzerpasswort … BASE64 encodiert zusammen mit dem Authentifizierungsschema 'Basic' übergeben werden."

**How to get credentials.** Per the [DPMAconnectPlus overview](https://www.dpma.de/english/search/data_supply_services/dpmaconnect/index.html):

> "Following the conclusion of an agreement, we will create an account for you with a username and a password of your choice … A standard agreement with the DPMA which regulates users' rights and obligations, and their reasons for use of the data, must be concluded in order to access the data."

Process (from the same page and from the [standard contract PDF](https://www.dpma.de/docs/recherche/dienste/standardvertrag_dpmaconnectplus.pdf)):

1. Download the standard contract (Standardvertrag).
2. Sign **two paper copies with legally valid original signatures**.
3. Mail both copies + annexes to: *Deutsches Patent- und Markenamt, Referat 2.1.2 - Kundenservice, Datenabgabe, 80297 München, Germany.*
4. DPMA counter-signs and provisions the username/password.

**Cost:** One-time EUR 200 connection fee (§ 4.2 of the contract). Data retrieval from the register and DEPATIS itself is free; weekly bulk packages cost extra per Annex 1.

**No company-registration / VAT ID / eIDAS gate is documented** — the standard contract accepts any company ("der Firma _______, vertreten durch _______"). But:

- The contract is in **German only** (Standardvertrag DPMAconnectPlus, Stand 01.04.2020).
- It requires a **registered, non-dynamic IP address** on the receiving system (§ 2.1: *"über ein System mit registrierter und nicht dynamischer IP-Adresse herunterlädt"*) — that's awkward for cloud-deployed proxies.
- "How long does approval take?" — **no primary source found** for a published SLA; DPMA documents the postal-mail flow but does not state a turnaround time.

## 3. Query language

**Structured field queries via the DPMAregister "Expertenrecherche" syntax** — not free text. The REST `search/` function takes the same expert-query string a power user would type into the DPMAregister "Expertenrecherche" form. From [Schnittstellenbeschreibung DPMAconnectPlus](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf) p. 2:

> "Dabei muss die übergebene Expertenabfrage denselben Anforderungen genügen wie in der Auskunftsanwendung DPMAregister Maske 'Patente und Gebrauchsmuster' -> 'Expertenrecherche'."
> ("The expert query must meet the same requirements as in the DPMAregister 'Patents and Utility Models' -> 'Expert Search' form.")

**Syntax overview** (from the [DPMAregister Hilfetext PDF, V 1695/10.25](https://register.dpma.de/prod/de/register_hilfe.pdf), §§ 2.4 and 2.6):

- Boolean operators: `UND`, `ODER`, `NICHT` (German equivalents of AND, OR, NOT)
- Comparison operators: `=`, `>=`, `<=`
- Grouping: parentheses `( )`
- Date math: `j-2005` (year 2005), `M1-2005` (Jan 2005), `kw5-2013` (calendar week 5 of 2013)
- Existence: `exists INH`, `not exists INH`
- Field-scoped: `<FIELD-CODE> = "value"`

**Example expert queries** (Hilfetext p. 6):
```
INH = "Hamburg"
AT = M1-2005
SART = patent UND INH = "Deutsches Zentrum für Luft- und Raumfahrt"
   UND AT >= 1.3.2022 UND AT <= 31.5.2022
   UND (TI = Herstellung ODER TI = Verfahren)
```

**Searchable fields** (Hilfetext §§ 2.6.1–2.6.4; abbreviated — full table at the URL above). The Hilfetext provides ~50+ searchable fields per IP right, each annotated with INID code, German label, short code, applicable IP types, and basic/extended/expert mode availability:

| Code | Field | IP types | Notes |
|---|---|---|---|
| `AKZ` | Aktenzeichen (file number, all jurisdictions) | P, Z, G, T | Collective field |
| `DAKZ` | DE file number | P, Z, G, T | |
| `EAKZ` | EP file number | P, G | |
| `WAKZ` | PCT/WO file number | P, G | PCT national-phase entries |
| `INH` | Anmelder/Inhaber (applicant/owner) | P, Z, G, T | |
| `IN` | Erfinder (inventor) | P only | |
| `AT`, `DAT`, `EAT`, `WAT` | Filing dates (DE/EP/WO) | P, G | |
| `TI` | Bezeichnung/Titel | P, G, T | Title text |
| `IC`, `ICM`, `ICS` | IPC class / main / subordinate | P, Z, G | |
| `SART` | Schutzrechtsart (patent / Gebrauchsmuster / Schutzzertifikat / Topografie) | P, Z, G, T | |
| `ST` | Status | P, Z, G, T | |
| `PUB`, `PET` | Publication date / grant publication date | P, Z, G, T | |
| `PRC`, `PRNA`, `PRDA` | Priority country / number / date | P, G | |
| `WDS` | Bestimmungsstaaten WO (PCT designated states) | P, G | |
| `EDS` | Benannte Vertragsstaaten EP | P, G | |
| `CT`, `CTNP` | Citations (patent / non-patent literature) | P, G | |
| `VTR` | Vertreter (representative) | P, Z, G, T | |

Trade marks and designs have their own field sets (Hilfetext §§ 3 and 4).

## 4. Pagination

**Hard cap: 1000 hits per search for full users; 100 hits for test/demo accounts.** From [Schnittstellenbeschreibung DPMAconnectPlus](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf) p. 1:

> "Registrierten Benutzern werden maximal 1000 Treffer bei den diversen Suchfunktionen der Web Services zurückgeliefert, Benutzern mit einem Testzugang 100 Treffer."

**The spec does not document any pagination mechanism** — no `offset`, `limit`, `cursor`, `page`, or `size` parameter is listed for the `search/` function. The interface returns one XML hit-list per call (matching `PatentHitList.xsd` / `MarkenHitList.xsd` / `DesignHitList.xsd`), apparently truncated at 1000. **No primary source found** for any way to access hits 1001+ beyond narrowing the query.

## 5. Response shape

**XML only.** No JSON envelope. The REST API returns XML strings conforming to published XSDs.

- **Hit list:** `PatentHitList.xsd`, `MarkenHitList.xsd`, `DesignHitList.xsd` (schemas referenced in [Schnittstellenbeschreibung DPMAconnectPlus](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf) pp. 2, 8, 10).
- **Detail record (patents/utility models):** DPMA extension of WIPO ST.36 schema — `DE-PATGBM-RegisterExt` at <http://www.dpma.de/standards/XMLSchema/DE-PATGBM-RegisterExt>
- **Detail record (designs):** DPMA extension of WIPO ST.86 schema — `DS-XML-V1-1Ext` at <http://register.dpma.de/standards/XMLSchema/DS-XML-V1-1Ext>
- **Detail record (trade marks):** DPMA extension of WIPO ST.66 — `DE-TM-Register-V1.1.xsd` at <http://register.dpma.de/standards/XMLSchema/DE-TM-Register-V1.1.xsd>
- **Images:** `getRegisterFullImage` / `getRegisterThumbnailImage` return raw JPG.
- **Documents:** `getPatentpublikation_PDF`, `getRecherchierbarerVolltext` return PDF blobs by document ID; bulk download functions (`get<Type>_XML/_PDF/<publication-week>`) return ZIPs containing XML or PDF batches.

**Sample fragments are not included verbatim in the interface PDF** — the spec defers to the XSDs hosted on `register.dpma.de` for record structure. **No primary source found** for an inline sample hit/detail JSON or XML snippet outside the XSD files themselves.

## 6. Coverage scope

From the [DPMAregister Hilfetext](https://register.dpma.de/prod/de/register_hilfe.pdf):

- **Patents / Utility Models / SPCs / Topographies (§ 2.1):** All electronic register entries are available; substantially complete from ~1981 onward; partial coverage 1950–1981; pre-1950 entries are generally not electronic and **not available** via DPMAregister. SPCs available from 1993. Topographies only those pending or in force on 1 Feb 2012. GDR (DDR) patents available from 1981.
- **PCT (WO) national-phase entries (§ 2.1):** Indexed via `WAKZ` / `WAT` / `WDS` fields, but until the national phase is initiated, **fields such as inventor and applicant may be empty** (Hilfetext p. 4: *"Bei Anmeldungen bei der Weltorganisation für geistiges Eigentum (WO-Anmeldungen) mit deutscher Benennung werden in DPMAregister bis zur Einleitung der nationalen oder regionalen Phase nicht alle Felder mit Daten gefüllt"*).
- **EP applications (§ 2.1):** Indexed but with limited fields until grant.
- **Trade marks (§ 3.1):** German trade marks registered since **October 1894**, provided not cancelled before 1 January 1995; plus EU trade marks and WIPO IR marks designating Germany or the EU. Per [DPMA statistics](https://www.dpma.de/english/our_office/publications/statistics/index.html), DPMA received 4,473,798 patent applications cumulative through end-2024.
- **Designs (§ 4.1):** Registered designs plus DDR designs (1952–1992, digitised under DFG-Projekt 415711347).
- **Geographic Indications.**

**Document archive (DEPATIS) via DPMAconnectPlus:** Per [DEPATISnet overview](https://www.dpma.de/english/search/depatisnet/index.html), the archive holds **>160 million patent publications worldwide** (DE since 1877). The contract (§ 2.5) restricts DEPATIS retrieval through DPMAconnectPlus to **DE, DD, EP, and WO documents only** — no other offices.

## 7. Rate limits / quotas

- **Per-query cap:** 1000 hits (full account) / 100 hits (test account). Source: [Schnittstellenbeschreibung DPMAconnectPlus](https://www.dpma.de/docs/recherche/dienste/schnittstellenbeschreibungdpmaconnectplus.pdf) p. 1.
- **Bandwidth throttling:** § 2.2 of the [standard contract](https://www.dpma.de/docs/recherche/dienste/standardvertrag_dpmaconnectplus.pdf) reserves DPMA's right to cap per-recipient transfer volume *"sofern es hierfür einen triftigen Grund gibt"* (if there is good cause), particularly *"wenn das Downloadvolumen des Datenempfängers die Betriebsfähigkeit und -sicherheit der Schnittstelle so beeinträchtigt, dass hierdurch andere Datenempfänger in ihrer Nutzung behindert werden"* (if the recipient's download volume impairs the operability and security of the interface for other recipients).
- **Published per-second / per-day rate limit:** **No primary source found.** The contract is qualitative ("good cause") rather than quantitative.
- **Free-tier vs paid-tier:** There is no free tier of the REST interface itself; everyone pays EUR 200 once. Test accounts (100-hit cap) exist but the spec does not describe how to get one.

## 8. Terms of service

The [standard contract PDF (Standardvertrag DPMAconnectPlus, Stand 01.04.2020)](https://www.dpma.de/docs/recherche/dienste/standardvertrag_dpmaconnectplus.pdf) is the controlling ToS. The decisive clauses for a proxy/SaaS:

**§ 3.1 — Purpose limitation.** Data may be used only for one of four declared purposes, ticked at contract signing:

> a) Aufbau/Entwicklung/Ausbau eigener Datensammlungen zu Schutzrechten … vom Datenempfänger **intern** zur Ermittlung, Verwaltung und Überprüfung von Schutzrechten genutzt werden
> b) … vom Datenempfänger autorisierten Dritten (gegebenenfalls gegen Entgelt) zur Verfügung gestellt werden, um ihnen die Ermittlung, Verwaltung und Überprüfung von Schutzrechten zu ermöglichen
> c) Entwicklung und Vertrieb von Informationsprodukten und -dienstleistungen zu Schutzrechten
> d) Wissenschaftliche Tätigkeit

(Translation: a) internal use only; b) provision to *authorised third parties* for IP-right administration; c) developing/selling IP information products; d) scientific research.)

**§ 3.2 — Hard restrictions.** The recipient acquires a **non-exclusive, non-transferable** right of use. Specifically prohibited:

> "die vom DPMA bezogenen Daten beziehungsweise Datensätze ganz oder teilweise an Dritte weiterzugeben; eine Weitergabe im Rahmen einer Nutzung gemäß dem Zweck nach Ziffer 1 b) ist von diesem Verbot ausgenommen"
> ("passing the data, in whole or in part, to third parties; a transfer within the scope of usage purpose 1b is exempted from this prohibition")

Plus:
- No use for *gewerbliche Adressenverwertung* (commercial address-list reuse).
- No use that creates the appearance the recipient is authorised to administer IP rights legally.
- No use for rating natural persons.

**§ 5 — Confidentiality.** Recipient must protect pre-publication data, propagate corrections immediately, follow BSI security guidelines.

**§ 7.6 — DPMA termination right.** DPMA may terminate without notice if it cannot supply the data on data-protection grounds.

**Implication for our proxy model:** A patentclient.com / Cowork proxy that accepts arbitrary queries from end-users and returns DPMA data to them is a textbook violation of § 3.2 unless those end-users are themselves *authorised third parties* under purpose 1b. The bar for "authorised third party" is not defined in the contract, but the surrounding context (purpose: enable the third party to administer their own IP rights) is much narrower than a general MCP/agent audience.

## 9. Operational notes

- **Language:** Service overview is bilingual DE/EN; **all primary contractual and technical documents are German-only** — interface spec PDF, standard contract PDF, and the Hilfetext for query syntax. The DPMAregister UI has an English mode but the help PDF is German.
- **IP allowlisting:** Yes. § 2.1 of the [standard contract](https://www.dpma.de/docs/recherche/dienste/standardvertrag_dpmaconnectplus.pdf) requires the recipient to download from *"ein System mit registrierter und nicht dynamischer IP-Adresse"* — i.e., the connection IP is registered at contract signing. Cloud Run with auto-scaling would need a static egress NAT or VPC connector, and any IP change requires contract amendment. (This same constraint already bit us with USPTO TESS and unifiedpatentcourt.org — see `project_cloud_run_egress.md` in memory.)
- **Geofencing:** None documented beyond the registered-IP requirement.
- **Downtime patterns:** § 2.13 of the contract: *"Das DPMA schuldet keinen unterbrechungsfreien Zugriff / keine permanente Verfügbarkeit der Daten."* (DPMA does not owe uninterrupted access or permanent availability.) **No primary source found** for SLO/uptime targets or a status page.
- **Recent / planned changes:** The major consolidation already happened on 1 January 2020 ([Mitteilung Nr. 9/19](https://www.dpma.de/dpma/veroeffentlichungen/mitteilungen/archiv/2019/mdp_09_2019.html)) when DPMAconnect (SOAP) + DPMAdatenabgabe + DEPATISconnect were unified into DPMAconnectPlus. The legacy SOAP endpoints at `dpmaconnect.dpma.de/dpmaws/services/…` are still listed in the older [DPMAconnect API-Beschreibung PDF](https://www.dpma.de/docs/recherche/dienste/dpmaconnectapibeschreibung.pdf), but new integrators should use REST. The DPMAconnectPlus overview page itself was last updated 30 March 2026 and shows *"[updated documents coming soon]"* under "Contract" — i.e., a contract revision is in flight.

## 10. Verdict

**RED.**

Technically, the DPMAconnectPlus REST API is well-built, well-documented (in German), and field-queryable — every box on the "good API" checklist is ticked: structured Expertenrecherche query syntax, standardised XML records (ST.36/ST.66/ST.86 extensions), HTTPS+Basic auth, predictable URL pattern. If our only constraint were "is there a live API we can call," the answer would be a clean green.

But three contractual realities make it infeasible as a runtime proxy under our zero-infra model:

1. **§ 3.2 of the standard contract prohibits passing the data to third parties** except under the narrow "authorised third party for IP administration" carve-out — patentclient.com/Cowork users do not fit that template.
2. **The registered-IP requirement (§ 2.1)** clashes with elastic cloud egress; we would need a dedicated egress NAT and a contract amendment every time it changes.
3. **The signed paper contract + Munich mail + EUR 200 fee + German-only documents** means this is not a "click here, get an API key" path — it is a procurement project requiring a German-speaking signatory.

For DPMA, the realistic path is either (a) sign the contract under purpose 1c and operate as a per-customer-purchased data product, or (b) keep our existing `dpma_statutes` bundled corpus and add an EPO-OPS-fronted view for German patents (EP/DE family data flows through EPO under EPO's own much more permissive ToS).

---

## Executive summary

DPMA's **DPMAconnectPlus REST API** is the right shape — structured Expertenrecherche queries over patents, utility models, trade marks, designs, and a 160M-document DEPATIS archive, with XML responses on standard WIPO schemas — but **it is not a green-light proxy target**. The single biggest risk is § 3.2 of the standard contract, which forbids the data recipient from passing the DPMA data to third parties; that is exactly what an MCP proxy does for arbitrary users. Layered on top are a paper-contract + EUR 200 fee + Munich postal flow, a static-IP requirement that fights cloud egress, German-only contract and technical docs, and a 1000-hit-per-query cap with no documented pagination. **Verdict: RED for zero-infra proxy. Keep the existing bundled `dpma_statutes` corpus; cover German patents indirectly through EPO OPS (which we already proxy under EPO's permissive ToS).**
