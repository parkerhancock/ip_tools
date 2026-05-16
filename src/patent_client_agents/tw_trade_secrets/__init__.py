"""Taiwan Trade Secrets Act connector (MCP-free public surface).

The Taiwan Trade Secrets Act (營業秘密法) in its official English
translation, bundled into one SQLite/FTS5 corpus. Static corpus
(``category=substantive_law``, ``transport=mcp_local``,
``update_strategy=scheduled_recrawl``, cadence ``irregular``). The TIPO
live REST API and bulk-data tracks are out of scope for this connector
— see the follow-up PR plan in CHANGELOG.md.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from typing import TypedDict

from .api import (
    USAGE_RESOURCE_URI,
    SearchInput,
    SectionInput,
    TwTradeSecretsClient,
    TwTradeSecretsCorpusMeta,
    TwTradeSecretsSearchHit,
    TwTradeSecretsSearchResult,
    TwTradeSecretsSection,
    get_client,
    get_section,
    get_section_by_citation,
    get_usage_resource,
    parse_citation,
    search,
)
from .corpus import CorpusDB, CorpusUnavailable

__all__ = [
    "TwTradeSecretsClient",
    "CorpusUnavailable",
    "CorpusStatus",
    "TwTradeSecretsSection",
    "TwTradeSecretsSearchHit",
    "TwTradeSecretsSearchResult",
    "TwTradeSecretsCorpusMeta",
    "SearchInput",
    "SectionInput",
    "get_client",
    "search",
    "get_section",
    "get_section_by_citation",
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
    label: Taiwan's statutes are published on law.moj.gov.tw without a
    discrete vendor revision tag, so when no ``meta.source_version`` is
    stamped we fall back to a ``snapshot-<date>`` label. When the
    corpus is unbundled or unreadable both fields fall back to
    ``corpus_version="unknown"`` / ``corpus_synced_at=None`` — we never
    fabricate values.
    """

    corpus_synced_at: datetime | None
    corpus_version: str


def get_corpus_status() -> CorpusStatus:
    """Return TW Trade Secrets corpus freshness metadata.

    Reads ``meta.snapshot_date`` and ``meta.source_version`` from the
    bundled SQLite corpus
    (:mod:`patent_client_agents.tw_trade_secrets.corpus.schema`). Does
    not require a live upstream call — this is the callable used by
    ``scripts/build_coverage.py`` and the MCP tool layer to stamp
    ``Provenance.corpus_synced_at`` / ``Provenance.corpus_version``
    (CONNECTOR_STANDARDS.md §4, §5.9).

    The corpus is located via ``TW_TRADE_SECRETS_CORPUS_PATH`` or the
    local-dev default at
    ``~/.cache/patent_client_agents/tw_trade_secrets.db``. If the file
    is missing, unreadable, or the schema is unexpected, returns
    ``corpus_version="unknown"`` and ``corpus_synced_at=None`` —
    callers can still surface a Provenance object, just without
    freshness info.
    """
    try:
        with CorpusDB.open() as db:
            meta = db.meta()
    except CorpusUnavailable as exc:
        _logger.debug("TW Trade Secrets corpus unavailable for get_corpus_status: %s", exc)
        return CorpusStatus(corpus_synced_at=None, corpus_version="unknown")
    except Exception as exc:  # pragma: no cover — defensive; never crash the caller
        _logger.warning(
            "TW Trade Secrets get_corpus_status: unexpected error reading corpus meta: %r",
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
            "TW Trade Secrets get_corpus_status: snapshot_date %r is not ISO date",
            value,
        )
        return None
    return datetime(
        parsed_date.year,
        parsed_date.month,
        parsed_date.day,
        tzinfo=UTC,
    )
