# Regional IP offices

Multi-state offices where a single filing grants protection across a defined
region. Sits between the multilateral layer and national offices.

## Synopses in this folder

| Office | Region | Rights | Synopsis |
|---|---|---|---|
| **EPO** | 38 EPC states + PCT national-phase | Patents + INPADOC backbone | [epo.md](epo.md) |
| **EUIPO** | 27 EU states | EU Trade Marks (EUTM) + Registered EU Designs (REUD, ex-RCD) + TMview / DesignView federations | [euipo.md](euipo.md) |
| **UPC** | ~17 EU states for Unitary Patents | UP decisions, UP Court decisions | [upc.md](upc.md) |
| **EAPO** | Eurasian (8 states) | Patents | [eapo.md](eapo.md) — *not yet written; see [connectors/](../connectors/) and BACKLOG* |
| **ARIPO** | African regional (22 states) | Patents + utility models + designs + TMs + plant varieties | [aripo.md](aripo.md) — *deferred per BACKLOG skip verdict; coverage via EPO OPS AP code* |
| **OAPI** | Francophone African (17 states) | Patents + designs + TMs + GIs | [oapi.md](oapi.md) — *deferred per BACKLOG skip verdict; coverage via EPO OPS OA code* |
| **GCC Patent Office** | Gulf (6 states) | Patents (legacy register only) | [gcc-patent.md](gcc-patent.md) — *closed for new applications since 2021-01-06* |

## Layer-level note

EPO is the **single highest-leverage office in the registered-IP catalog** because INPADOC
gives biblio + family + legal-events coverage for ~100 patent offices worldwide,
substituting for national patent register connectors at many jurisdictions. EUIPO is
the only registered-IP office for EU-level marks and designs.

National-level rights still require national connectors — regional offices do **not**
substitute for national TM/design coverage outside the EU level. EUIPO's TMview is a
search frontend over national TM registers, not a unified register.

For details see [`../COVERAGE_STRATEGY.md`](../COVERAGE_STRATEGY.md) §3 and §6.
