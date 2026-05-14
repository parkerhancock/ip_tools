from __future__ import annotations

from pydantic import BaseModel, Field


class PctGuidelinesSearchHit(BaseModel):
    title: str
    href: str
    path: list[str] = Field(default_factory=list)
    result_url: str


class PctGuidelinesSearchResponse(BaseModel):
    hits: list[PctGuidelinesSearchHit]
    page: int
    per_page: int
    has_more: bool


class PctGuidelinesSection(BaseModel):
    href: str
    html: str
    text: str
    version: str
    title: str | None = None


class PctGuidelinesVersion(BaseModel):
    label: str
    value: str
    current: bool = False
