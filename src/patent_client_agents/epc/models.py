from __future__ import annotations

from pydantic import BaseModel, Field


class EpcSearchHit(BaseModel):
    title: str
    href: str
    path: list[str] = Field(default_factory=list)
    result_url: str


class EpcSearchResponse(BaseModel):
    hits: list[EpcSearchHit]
    page: int
    per_page: int
    has_more: bool


class EpcSection(BaseModel):
    href: str
    html: str
    text: str
    version: str
    title: str | None = None


class EpcVersion(BaseModel):
    label: str
    value: str
    current: bool = False
