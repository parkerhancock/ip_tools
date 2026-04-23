# Patent PDF Download (cross-source)

Download a patent or publication PDF with worldwide coverage via a cascade
across three backends.

## Cascade order

1. **Google Patents** — preferred. PDFs are already OCR'ed (text extraction
   works directly; no post-processing needed).
2. **USPTO PPUBS** — US patents and published applications. Assembled from
   image pages; **not OCR'ed**.
3. **EPO OPS** — worldwide fallback. Assembled from image pages across all
   EPO-covered jurisdictions; **not OCR'ed**.

The cascade advances only on "not found" signals from a source
(`NotFoundError`, `FileNotFoundError`, missing-PDF `ValueError`). Hard
errors — auth failures, transient 5xx, rate limits — **surface
immediately** rather than being masked by silent fallback, so you don't
retry a legitimate failure against two more backends.

PPUBS cleanly 404s for non-US numbers (via its publication-number resolver),
so the cascade runs unconditionally regardless of country — no US/non-US
branching in the caller.

## Why not ODP?

USPTO ODP exposes PDFs only through the **prosecution document** endpoint,
which requires multi-step resolution (resolve patent → application number →
list file history → find grant document → download). There is no single-call
`number → PDF` surface. ODP's strength in this domain (prosecution
documents) is already exposed via `get_file_history_item`.

## Python API

```python
from patent_client_agents import download_patent_pdf

pdf = await download_patent_pdf("US10000000B2")
# PatentPdf(pdf_bytes=b"...", source="google_patents", filename="US10000000B2.pdf",
#           patent_number="US10000000B2", patent_title=None)

pdf.pdf_bytes      # raw bytes
pdf.source         # "google_patents" | "ppubs" | "epo"
pdf.filename       # suggested filename
```

`PatentPdf` is a frozen dataclass — stable for logging, serialization, and
pattern matching.

## MCP tool

```
download_patent_pdf(patent_number) -> dict
```

Returns the standard download response (`download_url` or `file_path`,
`filename`, `content_type`, `size_bytes`) plus a `source` field indicating
which backend served the bytes. Agents can check `source` to decide whether
OCR is needed before text extraction.

## Not included

- `download_ptab_document` — stays separate. Different document class
  (trial filings, not patent PDFs) with its own identifier space.
- File-history documents — use `get_file_history_item(format="pdf")`
  instead; that tool returns a signed download URL for the specific
  prosecution document, not a patent PDF.
