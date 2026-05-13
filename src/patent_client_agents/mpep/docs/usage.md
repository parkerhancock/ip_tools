# MPEP Usage

The MPEP client reads from a **local SQLite/FTS5 snapshot** of the MPEP
— it does not call USPTO at runtime. USPTO's eMPEP `/search` endpoint
has been intermittently broken since 2026-05-13 and is not part of the
library's request path. Section retrieval and full-text search both go
through the local corpus.

## First-time setup

The wheel ships the builder, not the corpus. Build the snapshot once
into the default cache path:

```bash
patent-client-agents-build-mpep-corpus \
    --output ~/.cache/patent_client_agents/mpep.db
```

The crawl takes ~4 minutes against live USPTO and yields ~3,000
sections across all 29 MPEP chapters (~50MB SQLite). Re-run periodically
to pick up USPTO revisions.

For cloud deploys, build the corpus into the container image and set
`MPEP_CORPUS_PATH` in the runtime env to point at it; the file does not
have to live in `~/.cache`.

## Search

* `MpepClient.search(query, syntax="adj", sort="relevance",
  per_page=10, page=1)` runs a FTS5 MATCH query.
* `syntax="adj"` (default) and `syntax="exact"` quote the query as a
  phrase. `syntax="and"` is FTS5's space-separated default. `syntax="or"`
  joins tokens with `OR`.
* `sort="relevance"` orders by FTS5 BM25 rank; `sort="outline"` orders
  by `section_number` ascending.
* `per_page` ≤ 100; `page` is 1-based; the response sets `has_more`
  when more rows remain.
* `include_index`, `include_notes`, `include_form_paragraphs`, and
  `snippet` are accepted for API parity but no longer affect the
  query — all body text is indexed together in the corpus.

## Section retrieval

* `MpepClient.get_section(section)` accepts either a section number
  (`"2106"`, `"2106.04(a)"`, `"706.03(a)(1)"`) or an internal href
  (`"d0e197244.html"`, `"ch2100_d29a1b_13a9e_2dc.html"`). Section
  numbers are resolved via the `section_number` index.
* The returned `MpepSection.html` is the cleaned outerHTML of the
  smallest section-id-bearing block that contains the heading. `.text`
  is the same content with whitespace collapsed.
* `highlight_query` is accepted for API parity but no longer fetches a
  separate highlighted view — search results already carry FTS5
  `<mark>`-wrapped snippets.

## Versions

`MpepClient.list_versions()` returns a single-entry list reflecting the
loaded snapshot (`label = "current (snapshot YYYY-MM-DD)"`,
`value = "current"`, `current = True`). The corpus is a point-in-time
freeze; passing a non-`"current"` version is a no-op.

## Cache-miss behavior

If neither `MPEP_CORPUS_PATH` nor `~/.cache/patent_client_agents/mpep.db`
exists, the first call raises
`patent_client_agents.mpep.corpus.CorpusUnavailable` with the build
command in the message — no silent fallback to live HTTP.
