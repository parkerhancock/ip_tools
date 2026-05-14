"""SQLite/FTS5 corpus subpackage for the UPC statutes."""

from .db import (
    CorpusDB,
    CorpusHit,
    CorpusInstrument,
    CorpusUnavailable,
    default_corpus_path,
)

__all__ = [
    "CorpusDB",
    "CorpusUnavailable",
    "CorpusInstrument",
    "CorpusHit",
    "default_corpus_path",
]
