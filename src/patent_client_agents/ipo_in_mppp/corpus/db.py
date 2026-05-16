"""Read-side API for the IPO India MPPP SQLite corpus.

The runtime never builds the corpus — it opens an already-built ``.db``
file produced by ``patent-client-agents-build-ipo-in-mppp-corpus``
and serves queries against it. Locator precedence:

1. ``IPO_IN_MPPP_CORPUS_PATH`` env var (explicit, for cloud deploys).
2. ``~/.cache/patent_client_agents/ipo_in_mppp.db`` (local-dev default).

Misses raise :class:`CorpusUnavailable` with a hint at how to build it.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path


class CorpusUnavailable(RuntimeError):
    """Raised when the IPO India MPPP corpus cannot be located or opened."""


@dataclass(frozen=True)
class CorpusSection:
    section_number: str
    chapter: str | None
    title: str | None
    text: str
    source_url: str | None


@dataclass(frozen=True)
class CorpusHit:
    section_number: str
    chapter: str | None
    title: str | None
    snippet: str
    rank: float | None


def default_corpus_path() -> Path:
    """Return the local-dev default location (~/.cache/...)."""
    return Path.home() / ".cache" / "patent_client_agents" / "ipo_in_mppp.db"


def _resolve_corpus_path(explicit: str | os.PathLike[str] | None) -> Path:
    if explicit is not None:
        return Path(explicit)
    env = os.environ.get("IPO_IN_MPPP_CORPUS_PATH")
    if env:
        return Path(env)
    return default_corpus_path()


_INSTALL_HINT = (
    "Run `patent-client-agents-build-ipo-in-mppp-corpus --output "
    "~/.cache/patent_client_agents/ipo_in_mppp.db` to build it, or set "
    "IPO_IN_MPPP_CORPUS_PATH to an existing corpus file."
)


class CorpusDB:
    """Thin wrapper around the IPO India MPPP corpus SQLite connection."""

    def __init__(self, conn: sqlite3.Connection, path: Path) -> None:
        self._conn = conn
        self._path = path
        conn.row_factory = sqlite3.Row

    @classmethod
    def open(
        cls, path: str | os.PathLike[str] | None = None, *, must_exist: bool = True
    ) -> CorpusDB:
        resolved = _resolve_corpus_path(path)
        if must_exist and not resolved.exists():
            raise CorpusUnavailable(
                f"IPO India MPPP corpus not found at {resolved}. {_INSTALL_HINT}"
            )
        try:
            conn = sqlite3.connect(f"file:{resolved}?mode=ro", uri=True)
        except sqlite3.OperationalError as exc:
            raise CorpusUnavailable(
                f"Could not open IPO India MPPP corpus at {resolved}: {exc}. {_INSTALL_HINT}"
            ) from exc
        return cls(conn, resolved)

    @property
    def path(self) -> Path:
        return self._path

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> CorpusDB:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def meta(self) -> dict[str, str]:
        rows = self._conn.execute("SELECT key, value FROM meta").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def get_section(self, *, section_number: str) -> CorpusSection | None:
        row = self._conn.execute(
            "SELECT * FROM sections WHERE section_number = ?",
            (section_number,),
        ).fetchone()
        return _row_to_section(row) if row else None

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        offset: int = 0,
        sort: str = "relevance",
        snippet_chars: int = 200,
    ) -> list[CorpusHit]:
        """Run an FTS5 query against the corpus.

        Args:
            query: FTS5 MATCH expression.
            limit / offset: Pagination.
            sort: ``relevance`` (BM25, default) or ``outline``
                (section_number ascending).
            snippet_chars: Approximate snippet width in characters.
        """
        order = "ORDER BY rank" if sort == "relevance" else "ORDER BY s.section_number"
        # snippet() column index 2 = text (section_number, title, text)
        sql = f"""
            SELECT
                s.section_number,
                s.chapter,
                s.title,
                snippet(sections_fts, 2, '<mark>', '</mark>', '…', ?) AS snippet,
                rank
            FROM sections_fts
            JOIN sections s ON s.rowid = sections_fts.rowid
            WHERE sections_fts MATCH ?
            {order}
            LIMIT ? OFFSET ?
        """
        token_count = max(8, min(snippet_chars // 5, 64))
        rows = self._conn.execute(sql, (token_count, query, limit, offset)).fetchall()
        return [
            CorpusHit(
                section_number=row["section_number"],
                chapter=row["chapter"],
                title=row["title"],
                snippet=row["snippet"] or "",
                rank=row["rank"],
            )
            for row in rows
        ]


def _row_to_section(row: sqlite3.Row) -> CorpusSection:
    return CorpusSection(
        section_number=row["section_number"],
        chapter=row["chapter"],
        title=row["title"],
        text=row["text"],
        source_url=row["source_url"],
    )


__all__ = [
    "CorpusDB",
    "CorpusUnavailable",
    "CorpusSection",
    "CorpusHit",
    "default_corpus_path",
]
