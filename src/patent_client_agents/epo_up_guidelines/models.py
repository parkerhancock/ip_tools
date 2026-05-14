from __future__ import annotations

from pydantic import BaseModel, Field


class UpGuidelinesSearchHit(BaseModel):
    title: str
    href: str
    path: list[str] = Field(default_factory=list)
    result_url: str


class UpGuidelinesSearchResponse(BaseModel):
    hits: list[UpGuidelinesSearchHit]
    page: int
    per_page: int
    has_more: bool


class UpGuidelinesSection(BaseModel):
    href: str
    html: str
    text: str
    version: str
    title: str | None = None


class UpGuidelinesVersion(BaseModel):
    label: str
    value: str
    current: bool = False
