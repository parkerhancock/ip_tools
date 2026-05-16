"""Pydantic models for the Légifrance IP API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LegifranceSection(BaseModel):
    """A single French statutory article from the corpus."""

    statute: str = Field(
        description="Law collection — 'CPI' (Code de la propriété intellectuelle) "
        "or 'Code de commerce'."
    )
    section: str = Field(
        description="Article number without leading 'L.' — e.g. 'L611-10', 'L151-1'."
    )
    title: str | None = Field(default=None, description="Article heading in French.")
    text: str = Field(description="Canonical article body in French.")


class LegifranceSearchHit(BaseModel):
    """One FTS5 hit with a highlighted snippet."""

    statute: str
    section: str
    title: str | None = None
    snippet: str


class LegifranceSearchResult(BaseModel):
    """Search response — relevance-ranked hits with pagination metadata."""

    hits: list[LegifranceSearchHit]
    page: int
    per_page: int
    has_more: bool


__all__ = ["LegifranceSection", "LegifranceSearchHit", "LegifranceSearchResult"]
