"""Pydantic models for the IPO India statutes corpus."""

from __future__ import annotations

from pydantic import BaseModel


class IpoInSection(BaseModel):
    statute_name: str
    section_number: str
    title: str | None = None
    text: str
    source_url: str | None = None


class IpoInSearchHit(BaseModel):
    statute_name: str
    section_number: str
    title: str | None = None
    snippet: str
    rank: float | None = None


class IpoInSearchResponse(BaseModel):
    query: str
    statute_name: str | None = None
    hits: list[IpoInSearchHit]
    page: int
    per_page: int
    has_more: bool


class IpoInCorpusMeta(BaseModel):
    schema_version: int
    snapshot_date: str | None = None
    source_version: str | None = None
    section_count: int = 0
