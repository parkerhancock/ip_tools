"""IPO India MPPP connector (MCP-free public surface).

The Manual of Patent Practice & Procedure published by the IPO India —
the office's internal examination manual, India's counterpart to the
USPTO MPEP / UKIPO MoPP / EPO Guidelines. Static corpus
(``category=substantive_law``, ``transport=mcp_local``,
``update_strategy=scheduled_recrawl``, cadence ``irregular`` — IPO
India ships major MPPP revisions roughly every 4-5 years).
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from typing import TypedDict

from .api import (
    USAGE_RESOURCE_URI,
    MpppClient,
    MpppCorpusMeta,
    MpppSearchHit,
    MpppSearchInput,
    MpppSearchResponse,
    MpppSection,
    MpppSectionInput,
    get_client,
    get_section,
    get_usage_resource,
    normalize_section_reference,
    search,
)
from .corpus import CorpusDB, CorpusUnavailable

__all__ = [
    "MpppClient",
    "CorpusUnavailable",
    "CorpusStatus",
    "MpppSection",
    "MpppSearchHit",
    "MpppSearchResponse",
    "MpppCorpusMeta",
    "MpppSearchInput",
    "MpppSectionInput",
    "get_client",
    "search",
    "get_section",
    "normalize_section_reference",
    "get_corpus_status",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


_logger = logging.getLogger(__name__)


class CorpusStatus(TypedDict):
    """Return shape for :func:`get_corpus_status`.

    ``corpus_synced_at`` is the UTC datetime the bundled corpus was
    last refreshed from upstream (parsed from the corpus
    ``meta.snapshot_date``). ``corpus_version`` is the MPPP edition
    label as recorded in ``meta.source_version`` (e.g.
    ``"v3.0 (2019)"``); when no explicit version is stamped we surface
    the snapshot date as ``"snapshot-<date>"``. When the corpus is
    unbundled or unreadable both fields fall back to
    ``corpus_version="unknown"`` / ``corpus_synced_at=None`` — we
    never fabricate values.
    """

    corpus_synced_at: datetime | None
    corpus_version: str


def get_corpus_status() -> CorpusStatus:
    """Return IPO India MPPP corpus freshness metadata for the validator and Provenance helper.

    Reads ``meta.snapshot_date`` and ``meta.source_version`` from the
    bundled SQLite corpus
    (:mod:`patent_client_agents.ipo_in_mppp.corpus.schema`). Does not
    require a live upstream call — this is the callable used by
    ``scripts/build_coverage.py`` and the MCP tool layer to stamp
    ``Provenance.corpus_synced_at`` / ``Provenance.corpus_version``
    (CONNECTOR_STANDARDS.md §4, §5.9).

    The corpus is located via ``IPO_IN_MPPP_CORPUS_PATH`` or the
    local-dev default at
    ``~/.cache/patent_client_agents/ipo_in_mppp.db``. If the file is
    missing, unreadable, or the schema is unexpected, returns
    ``corpus_version="unknown"`` and ``corpus_synced_at=None``.
    """
    try:
        with CorpusDB.open() as db:
            meta = db.meta()
    except CorpusUnavailable as exc:
        _logger.debug("IPO India MPPP corpus unavailable for get_corpus_status: %s", exc)
        return CorpusStatus(corpus_synced_at=None, corpus_version="unknown")
    except Exception as exc:  # pragma: no cover — defensive; never crash the caller
        _logger.warning(
            "IPO India MPPP get_corpus_status: unexpected error reading corpus meta: %r",
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
            "IPO India MPPP get_corpus_status: snapshot_date %r is not ISO date",
            value,
        )
        return None
    return datetime(
        parsed_date.year,
        parsed_date.month,
        parsed_date.day,
        tzinfo=UTC,
    )
