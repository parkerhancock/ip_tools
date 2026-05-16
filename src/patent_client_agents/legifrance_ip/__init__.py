"""Légifrance IP statutes — CPI + Code de commerce L.151 trade secrets.

Static-law corpus served from a local SQLite/FTS5 snapshot built by
``patent-client-agents-build-legifrance-ip-corpus`` from the bundled
``data/seed.jsonl``. Runtime never calls Légifrance.

CONNECTOR_STANDARDS.md classification: ``category=substantive_law``,
``transport=mcp_local``, ``update_strategy=scheduled_recrawl``,
``update_cadence=annual``. See ``coverage/sources.yaml`` row
``FR/Legifrance/IP``.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from typing import TypedDict

from .api import LegifranceIpClient, get_section, search
from .client import LegifranceIpClient as _LegifranceIpClient  # re-export alias
from .corpus import CorpusDB, CorpusUnavailable
from .models import LegifranceSearchHit, LegifranceSearchResult, LegifranceSection
from .resources import STATUTES, CitationParseError, parse_citation

__all__ = [
    "CitationParseError",
    "CorpusDB",
    "CorpusStatus",
    "CorpusUnavailable",
    "LegifranceIpClient",
    "LegifranceSearchHit",
    "LegifranceSearchResult",
    "LegifranceSection",
    "STATUTES",
    "get_corpus_status",
    "get_section",
    "parse_citation",
    "search",
]


_logger = logging.getLogger(__name__)
_ = _LegifranceIpClient  # silence "unused import" — kept for symmetry with other connectors


class CorpusStatus(TypedDict):
    """Return shape for :func:`get_corpus_status`.

    ``corpus_synced_at`` is the UTC datetime the bundled corpus was last
    refreshed (parsed from the corpus ``meta.snapshot_date``).
    ``corpus_version`` mirrors the seed version label recorded in
    ``meta.source_version`` — for the bundled seed that is ``"seed v1"``.
    When the corpus is unbundled or unreadable the version falls back to
    ``"unknown"`` and the sync timestamp to ``None`` — we never fabricate
    values.
    """

    corpus_synced_at: datetime | None
    corpus_version: str


def get_corpus_status() -> CorpusStatus:
    """Return Légifrance IP corpus freshness metadata.

    Reads ``meta.source_version`` and ``meta.snapshot_date`` from the
    bundled SQLite corpus. Does not require a live upstream call — this
    is the callable ``scripts/build_coverage.py`` uses to detect drift,
    and the Légifrance IP MCP tools use to stamp
    ``Provenance.corpus_synced_at`` / ``Provenance.corpus_version`` on
    every response (CONNECTOR_STANDARDS.md §4, §5.9).

    Returns:
        A :class:`CorpusStatus` mapping with keys ``corpus_synced_at``
        (UTC ``datetime`` or ``None``) and ``corpus_version`` (string).
    """
    try:
        with CorpusDB.open() as db:
            meta = db.meta()
    except CorpusUnavailable as exc:
        _logger.debug("Légifrance IP corpus unavailable for get_corpus_status: %s", exc)
        return CorpusStatus(corpus_synced_at=None, corpus_version="unknown")
    except Exception as exc:  # pragma: no cover — defensive; never crash the caller
        _logger.warning(
            "Légifrance IP get_corpus_status: unexpected error reading corpus meta: %r",
            exc,
        )
        return CorpusStatus(corpus_synced_at=None, corpus_version="unknown")

    version = meta.get("source_version") or "unknown"
    snapshot_raw = meta.get("snapshot_date")
    return CorpusStatus(
        corpus_synced_at=_parse_snapshot_date(snapshot_raw),
        corpus_version=version,
    )


def _parse_snapshot_date(value: str | None) -> datetime | None:
    """Parse ``meta.snapshot_date`` (ISO YYYY-MM-DD) into a UTC datetime."""
    if not value:
        return None
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        _logger.debug("Légifrance IP get_corpus_status: snapshot_date %r is not ISO date", value)
        return None
    return datetime(
        parsed_date.year,
        parsed_date.month,
        parsed_date.day,
        tzinfo=UTC,
    )
