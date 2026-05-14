"""Corpus-backed client for the UPC statutes."""

from __future__ import annotations

import os
import re
from typing import Any

from .corpus.db import CorpusDB, CorpusUnavailable
from .models import (
    UpcCorpusMeta,
    UpcInstrument,
    UpcInstrumentText,
    UpcStatuteSearchHit,
    UpcStatuteSearchResponse,
)

INSTRUMENT_ALIASES: dict[str, str] = {
    # short-name → canonical key
    "upca": "upca",
    "agreement": "upca",
    "statute": "upca",  # Statute is Annex I to UPCA — same source PDF
    "annex i": "upca",
    "rop": "rop",
    "rules": "rop",
    "rules of procedure": "rop",
    "fees": "fees",
    "court fees": "fees",
    "table of court fees": "fees",
    "coc": "coc",
    "code of conduct": "coc",
}


def _resolve_instrument(name: str | None) -> str | None:
    if name is None:
        return None
    key = name.strip().lower()
    return INSTRUMENT_ALIASES.get(key, key)


def _translate_fts_query(query: str, syntax: str) -> str:
    """Translate a user-facing query into an FTS5 MATCH expression.

    FTS5 treats ``-``, ``:``, and other punctuation as syntactic
    operators (``-token`` is "exclude", ``col:term`` is column-filter,
    etc.). To keep the user-facing surface simple, every token that
    contains a non-word character is wrapped as a quoted phrase so it
    matches literally.
    """
    cleaned = query.strip()
    if not cleaned:
        return ""
    if syntax in ("adj", "exact"):
        escaped = cleaned.replace('"', '""')
        return f'"{escaped}"'
    tokens = [t for t in re.split(r"\s+", cleaned) if t]
    quoted = [_quote_if_needed(t) for t in tokens]
    if syntax == "or":
        return " OR ".join(quoted)
    return " ".join(quoted)


_BARE_TOKEN_RE = re.compile(r"^\w+$", re.UNICODE)


def _quote_if_needed(token: str) -> str:
    if _BARE_TOKEN_RE.match(token):
        return token
    return '"' + token.replace('"', '""') + '"'


class UpcStatutesClient:
    """Read-only client over the UPC statutes SQLite corpus.

    The corpus is opened lazily so callers can construct a client in
    environments where the database hasn't been materialized yet — the
    first method call raises :class:`CorpusUnavailable` with a hint at
    how to build it.
    """

    def __init__(
        self,
        *,
        corpus_path: str | os.PathLike[str] | None = None,
    ) -> None:
        self._corpus_path = corpus_path
        self._db: CorpusDB | None = None

    async def __aenter__(self) -> UpcStatutesClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        if self._db is not None:
            self._db.close()
            self._db = None

    def _open(self) -> CorpusDB:
        if self._db is None:
            self._db = CorpusDB.open(self._corpus_path)
        return self._db

    async def list_instruments(self, *, language: str | None = None) -> list[UpcInstrument]:
        db = self._open()
        rows = db.list_instruments(language=language)
        return [
            UpcInstrument(
                instrument=row.instrument,
                short_name=row.short_name,
                title=row.title,
                language=row.language,
                source_url=row.source_url,
                source_version=row.source_version,
                pdf_pages=row.pdf_pages,
            )
            for row in rows
        ]

    async def get_instrument(
        self, *, instrument: str, language: str = "en"
    ) -> UpcInstrumentText | None:
        db = self._open()
        canonical = _resolve_instrument(instrument)
        if canonical is None:
            return None
        row = db.get_instrument(instrument=canonical, language=language)
        if row is None:
            return None
        return UpcInstrumentText(
            instrument=row.instrument,
            short_name=row.short_name,
            title=row.title,
            language=row.language,
            source_url=row.source_url,
            source_version=row.source_version,
            pdf_pages=row.pdf_pages,
            text=row.text,
        )

    async def search(
        self,
        query: str,
        *,
        instrument: str | None = None,
        language: str | None = "en",
        syntax: str = "and",
        sort: str = "relevance",
        per_page: int = 10,
        page: int = 1,
    ) -> UpcStatuteSearchResponse:
        db = self._open()
        fts_query = _translate_fts_query(query, syntax)
        if not fts_query:
            return UpcStatuteSearchResponse(
                query=query, hits=[], page=page, per_page=per_page, has_more=False
            )
        offset = max(0, (page - 1) * per_page)
        rows = db.search(
            fts_query,
            instrument=_resolve_instrument(instrument),
            language=language,
            limit=per_page + 1,
            offset=offset,
            sort=sort,
        )
        has_more = len(rows) > per_page
        rows = rows[:per_page]
        hits = [
            UpcStatuteSearchHit(
                instrument=r.instrument,
                short_name=r.short_name,
                language=r.language,
                snippet=r.snippet,
                rank=r.rank,
            )
            for r in rows
        ]
        return UpcStatuteSearchResponse(
            query=query, hits=hits, page=page, per_page=per_page, has_more=has_more
        )

    async def meta(self) -> UpcCorpusMeta:
        db = self._open()
        meta = db.meta()
        return UpcCorpusMeta(
            schema_version=int(meta.get("schema_version", 0)),
            snapshot_date=meta.get("snapshot_date"),
            instrument_count=int(meta.get("instrument_count", 0)),
        )


__all__ = ["UpcStatutesClient", "CorpusUnavailable"]


def __getattr__(name: str) -> Any:  # pragma: no cover — debug-only export
    if name == "INSTRUMENT_ALIASES":
        return INSTRUMENT_ALIASES
    raise AttributeError(name)
