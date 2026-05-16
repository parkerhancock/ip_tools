"""Pydantic models for the IPO India MPPP corpus."""

from __future__ import annotations

from pydantic import BaseModel


class MpppSection(BaseModel):
    section_number: str
    chapter: str | None = None
    title: str | None = None
    text: str
    source_url: str | None = None


class MpppSearchHit(BaseModel):
    section_number: str
    chapter: str | None = None
    title: str | None = None
    snippet: str
    rank: float | None = None


class MpppSearchResponse(BaseModel):
    query: str
    hits: list[MpppSearchHit]
    page: int
    per_page: int
    has_more: bool


class MpppCorpusMeta(BaseModel):
    schema_version: int
    snapshot_date: str | None = None
    source_version: str | None = None
    section_count: int = 0
