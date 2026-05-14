# UPC statutes — usage

Corpus-backed access to the canonical legal documents of the Unified Patent
Court: the UPC Agreement (UPCA), its Annex I (Statute of the UPC), the
consolidated Rules of Procedure (RoP), the consolidated Table of Court Fees and
Recoverable Costs, and the Code of Conduct for Representatives. Each instrument
is mirrored in English, French, and German.

## When to use which tool

- **`get_upc_section`** — fetch the full plain text of a named instrument.
  Use when you need to read or quote a whole document, or when downstream code
  will do its own slicing by article/rule number.
- **`search_upc_statutes`** — FTS5 search across all instruments (or a single
  one). Use for questions like "what does the RoP say about opt-out", "find
  Article 33", "which instrument covers court-fee reimbursement".

## Instrument keys

| Key | Short name | Coverage |
| --- | --- | --- |
| `upca` | UPCA | UPC Agreement + Statute (Annex I) |
| `rop` | RoP | Consolidated Rules of Procedure (18th draft + amendments) |
| `fees` | Fees | Consolidated Table of Court Fees and Recoverable Costs |
| `coc` | CoC | Code of Conduct for Representatives (when added) |

`statute` is accepted as an alias for the UPCA Annex I portion — the source
PDF is the same, so the tool returns the UPCA instrument.

## Limits

- Section-level (per-Article, per-Rule) retrieval is **not** yet supported.
  For now, "give me Article 33" is best phrased as
  `search_upc_statutes(query="Article 33", instrument="upca")`. Structured
  section extraction is on the v0.12.0 roadmap.
- The corpus is a snapshot, not a live feed. Re-run
  `patent-client-agents-build-upc-statutes-corpus` when UPC publishes a new
  consolidated revision (typically alongside Administrative Committee
  decisions amending the RoP).
