"""Read-side API for the Légifrance IP SQLite corpus.

The runtime never calls Légifrance — it opens an already-built ``.db``
file produced by ``patent-client-agents-build-legifrance-ip-corpus`` and
serves queries against it. Locator precedence:

1. ``LEGIFRANCE_IP_CORPUS_PATH`` env var (explicit, used in cloud deploys).
2. ``~/.cache/patent_client_agents/legifrance_ip.db`` (local-dev convenience).

Misses raise :class:`CorpusUnavailable` with a message telling the
caller how to materialize the database — never a silent fallback.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path


class CorpusUnavailable(RuntimeError):
    """Raised when the Légifrance IP corpus database cannot be located or opened."""


@dataclass(frozen=True)
class CorpusSection:
    statute: str
    section: str
    title: str | None
    text: str


@dataclass(frozen=True)
class CorpusHit:
    statute: str
    section: str
    title: str | None
    snippet: str


def default_corpus_path() -> Path:
    """Return the local-dev default location (~/.cache/...)."""
    return Path.home() / ".cache" / "patent_client_agents" / "legifrance_ip.db"


def _resolve_corpus_path(explicit: str | os.PathLike[str] | None) -> Path:
    if explicit is not None:
        return Path(explicit)
    env = os.environ.get("LEGIFRANCE_IP_CORPUS_PATH")
    if env:
        return Path(env)
    return default_corpus_path()


_INSTALL_HINT = (
    "Run `patent-client-agents-build-legifrance-ip-corpus --output "
    "~/.cache/patent_client_agents/legifrance_ip.db` to build it, or set "
    "LEGIFRANCE_IP_CORPUS_PATH to an existing corpus file."
)


class CorpusDB:
    """Thin wrapper around the corpus SQLite connection.

    Open via context manager so the underlying connection is closed
    deterministically::

        with CorpusDB.open() as corpus:
            row = corpus.get_section("CPI", "L611-10")
            hits = corpus.search("brevetabilité")
    """

    def __init__(self, conn: sqlite3.Connection, path: Path) -> None:
        self._conn = conn
        self._path = path
        conn.row_factory = sqlite3.Row

    @classmethod
    def open(
        cls,
        path: str | os.PathLike[str] | None = None,
        *,
        must_exist: bool = True,
    ) -> CorpusDB:
        resolved = _resolve_corpus_path(path)
        if must_exist and not resolved.exists():
            raise CorpusUnavailable(
                f"Légifrance IP corpus not found at {resolved}. {_INSTALL_HINT}"
            )
        try:
            conn = sqlite3.connect(f"file:{resolved}?mode=ro", uri=True)
        except sqlite3.OperationalError as exc:
            raise CorpusUnavailable(
                f"Could not open Légifrance IP corpus at {resolved}: {exc}. {_INSTALL_HINT}"
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

    def meta_get(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def get_section(
        self,
        statute: str,
        section: str,
    ) -> CorpusSection | None:
        row = self._conn.execute(
            "SELECT statute, section, title, text FROM sections WHERE statute = ? AND section = ?",
            (statute, section),
        ).fetchone()
        return _row_to_section(row) if row else None

    def search(
        self,
        query: str,
        *,
        statute: str | None = None,
        limit: int = 10,
        offset: int = 0,
        snippet_chars: int = 200,
    ) -> list[CorpusHit]:
        """Run an FTS5 query against the corpus.

        Args:
            query: An FTS5 MATCH expression (callers translate from the
                public API before calling).
            statute: Optional filter — ``CPI`` or ``Code de commerce``.
            limit: Maximum hits to return.
            offset: Pagination offset.
            snippet_chars: Approximate snippet width in characters.

        Returns:
            A list of :class:`CorpusHit` ordered by BM25 relevance.
        """
        # FTS5 snippet() expects a token count, not chars — divide chars by ~5
        # (a rough average French token length) for a sensible window.
        token_count = max(8, min(snippet_chars // 5, 64))

        if statute is None:
            sql = """
                SELECT
                    s.statute,
                    s.section,
                    s.title,
                    snippet(sections_fts, 1, '<mark>', '</mark>', '…', ?) AS snippet
                FROM sections_fts
                JOIN sections s ON s.rowid = sections_fts.rowid
                WHERE sections_fts MATCH ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            """
            params: tuple = (token_count, query, limit, offset)
        else:
            sql = """
                SELECT
                    s.statute,
                    s.section,
                    s.title,
                    snippet(sections_fts, 1, '<mark>', '</mark>', '…', ?) AS snippet
                FROM sections_fts
                JOIN sections s ON s.rowid = sections_fts.rowid
                WHERE sections_fts MATCH ? AND s.statute = ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            """
            params = (token_count, query, statute, limit, offset)

        rows = self._conn.execute(sql, params).fetchall()
        return [
            CorpusHit(
                statute=row["statute"],
                section=row["section"],
                title=row["title"],
                snippet=row["snippet"] or "",
            )
            for row in rows
        ]

    def count_for(self, query: str, *, statute: str | None = None) -> int:
        if statute is None:
            row = self._conn.execute(
                "SELECT count(*) AS n FROM sections_fts WHERE sections_fts MATCH ?",
                (query,),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT count(*) AS n FROM sections_fts "
                "JOIN sections s ON s.rowid = sections_fts.rowid "
                "WHERE sections_fts MATCH ? AND s.statute = ?",
                (query, statute),
            ).fetchone()
        return int(row["n"])


def _row_to_section(row: sqlite3.Row) -> CorpusSection:
    return CorpusSection(
        statute=row["statute"],
        section=row["section"],
        title=row["title"],
        text=row["text"],
    )


__all__ = [
    "CorpusDB",
    "CorpusUnavailable",
    "CorpusSection",
    "CorpusHit",
    "default_corpus_path",
]
