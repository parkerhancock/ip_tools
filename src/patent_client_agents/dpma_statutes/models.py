"""Pydantic models for the DPMA Germany IP statutes corpus."""

from __future__ import annotations

from pydantic import BaseModel


class DpmaSection(BaseModel):
    """One section (§) of a German IP statute."""

    statute: str
    section: str
    title: str | None = None
    text: str


class DpmaSearchHit(BaseModel):
    """Single FTS hit from a DPMA statutes search."""

    statute: str
    section: str
    title: str | None = None
    snippet: str
    rank: float | None = None


class DpmaSearchResult(BaseModel):
    """Paginated search response."""

    query: str
    statute: str | None = None
    hits: list[DpmaSearchHit]
    page: int
    per_page: int
    has_more: bool


class DpmaCorpusMeta(BaseModel):
    """Corpus freshness metadata."""

    schema_version: int
    snapshot_date: str | None = None
    source_version: str | None = None
    section_count: int = 0


__all__ = [
    "DpmaSection",
    "DpmaSearchHit",
    "DpmaSearchResult",
    "DpmaCorpusMeta",
]
