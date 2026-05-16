"""Async API for the IPO India MPPP corpus (MCP-free)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import MpppClient, normalize_section_reference
from .corpus import CorpusUnavailable
from .models import MpppCorpusMeta, MpppSearchHit, MpppSearchResponse, MpppSection
from .resources import USAGE_RESOURCE_URI, get_usage_resource

__all__ = [
    "MpppClient",
    "CorpusUnavailable",
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
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


class MpppSearchInput(BaseModel):
    query: str
    syntax: str = Field(default="and", description="'and', 'or', 'adj', or 'exact'")
    sort: str = Field(default="relevance", description="'relevance' (BM25) or 'outline'")
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class MpppSectionInput(BaseModel):
    section_reference: str = Field(
        description=(
            "MPPP section reference — bare dotted number ('04.05.01') or "
            "citation form ('Chapter 04.05.01', 'MPPP Chapter 04.05.01')."
        ),
    )


def get_client() -> MpppClient:
    return MpppClient()


async def search(params: MpppSearchInput) -> MpppSearchResponse:
    async with MpppClient() as client:
        return await client.search(
            params.query,
            syntax=params.syntax,
            sort=params.sort,
            per_page=params.per_page,
            page=params.page,
        )


async def get_section(params: MpppSectionInput | str) -> MpppSection:
    if isinstance(params, str):
        params = MpppSectionInput(section_reference=params)
    async with MpppClient() as client:
        return await client.get_section(params.section_reference)
