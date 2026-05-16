"""Pydantic models for the Taiwan Trade Secrets Act corpus."""

from __future__ import annotations

from pydantic import BaseModel


class TwTradeSecretsSection(BaseModel):
    """One Article of the Taiwan Trade Secrets Act.

    ``section`` is the article number as it appears in the statute
    (e.g. ``"2"``, ``"13"``, ``"13-1"`` for sub-numbered articles
    inserted by amendment).
    """

    section: str
    title: str | None = None
    text: str


class TwTradeSecretsSearchHit(BaseModel):
    """One BM25-ranked hit from a corpus full-text search."""

    section: str
    title: str | None = None
    snippet: str
    rank: float | None = None


class TwTradeSecretsSearchResult(BaseModel):
    """Paged search response."""

    query: str
    hits: list[TwTradeSecretsSearchHit]
    page: int
    per_page: int
    has_more: bool


class TwTradeSecretsCorpusMeta(BaseModel):
    """Vendor-style metadata about the bundled corpus snapshot."""

    schema_version: int
    snapshot_date: str | None = None
    source_version: str | None = None
    section_count: int = 0
