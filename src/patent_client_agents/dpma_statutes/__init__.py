"""DPMA Germany IP statutes connector (MCP-free public surface).

The six core German IP Acts — PatG, MarkenG, GebrMG, DesignG, UrhG,
GeschGehG — bundled into one SQLite/FTS5 corpus discriminated by
``statute``. Static corpus (``category=substantive_law``,
``transport=mcp_local``, ``update_strategy=scheduled_recrawl``,
cadence ``annual``).
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from typing import TypedDict

from .api import (
    USAGE_RESOURCE_URI,
    DpmaCorpusMeta,
    DpmaSearchHit,
    DpmaSearchResult,
    DpmaSection,
    DpmaStatutesClient,
    SectionInput,
    StatuteSearchInput,
    get_client,
    get_section,
    get_section_by_citation,
    get_usage_resource,
    list_statutes,
    parse_citation,
    search,
)
from .corpus import CorpusDB, CorpusUnavailable

__all__ = [
    "DpmaStatutesClient",
    "CorpusUnavailable",
    "CorpusStatus",
    "DpmaSection",
    "DpmaSearchHit",
    "DpmaSearchResult",
    "DpmaCorpusMeta",
    "StatuteSearchInput",
    "SectionInput",
    "get_client",
    "search",
    "get_section",
    "get_section_by_citation",
    "list_statutes",
    "parse_citation",
    "get_corpus_status",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


_logger = logging.getLogger(__name__)


class CorpusStatus(TypedDict):
    """Return shape for :func:`get_corpus_status`.

    ``corpus_synced_at`` is the UTC datetime the bundled corpus was last
    refreshed from upstream (parsed from the corpus
    ``meta.snapshot_date``). ``corpus_version`` is a free-text version
    label; when no ``meta.source_version`` is stamped we fall back to a
    ``snapshot-<date>`` label. When the corpus is unbundled or
    unreadable both fields fall back to ``corpus_version="unknown"`` /
    ``corpus_synced_at=None`` — we never fabricate values.
    """

    corpus_synced_at: datetime | None
    corpus_version: str


def get_corpus_status() -> CorpusStatus:
    """Return DPMA statutes corpus freshness metadata for the validator and Provenance helper.

    Reads ``meta.snapshot_date`` and ``meta.source_version`` from the
    bundled SQLite corpus
    (:mod:`patent_client_agents.dpma_statutes.corpus.schema`). Does
    not require a live upstream call — this is the callable used by
    ``scripts/build_coverage.py`` and the MCP tool layer to stamp
    ``Provenance.corpus_synced_at`` / ``Provenance.corpus_version``
    (CONNECTOR_STANDARDS.md §4, §5.9).
    """
    try:
        with CorpusDB.open() as db:
            meta = db.meta()
    except CorpusUnavailable as exc:
        _logger.debug("DPMA statutes corpus unavailable for get_corpus_status: %s", exc)
        return CorpusStatus(corpus_synced_at=None, corpus_version="unknown")
    except Exception as exc:  # pragma: no cover — defensive; never crash the caller
        _logger.warning(
            "DPMA statutes get_corpus_status: unexpected error reading corpus meta: %r",
            exc,
        )
        return CorpusStatus(corpus_synced_at=None, corpus_version="unknown")

    snapshot_raw = meta.get("snapshot_date")
    explicit_version = meta.get("source_version")
    if explicit_version:
        version = explicit_version
    elif snapshot_raw:
        version = f"snapshot-{snapshot_raw}"
    else:
        version = "unknown"
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
        _logger.debug(
            "DPMA statutes get_corpus_status: snapshot_date %r is not ISO date",
            value,
        )
        return None
    return datetime(
        parsed_date.year,
        parsed_date.month,
        parsed_date.day,
        tzinfo=UTC,
    )
