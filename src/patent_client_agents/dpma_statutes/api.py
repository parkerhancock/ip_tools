"""Async API for the DPMA Germany IP statutes corpus (MCP-free).

Usage
-----
Preferred: use the client as a context manager for proper resource cleanup::

    async with DpmaStatutesClient() as client:
        section = await client.get_section_by_citation("§ 139 PatG")
        hits = await client.search("Patentverletzung", statute="PatG")

One-shot convenience functions (create and close the client automatically)::

    section = await get_section_by_citation("§ 139 PatG")
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import DpmaStatutesClient, parse_citation
from .corpus import CorpusUnavailable
from .models import (
    DpmaCorpusMeta,
    DpmaSearchHit,
    DpmaSearchResult,
    DpmaSection,
)
from .resources import USAGE_RESOURCE_URI, get_usage_resource

__all__ = [
    "DpmaStatutesClient",
    "CorpusUnavailable",
    "DpmaSection",
    "DpmaSearchHit",
    "DpmaSearchResult",
    "DpmaCorpusMeta",
    "StatuteSearchInput",
    "SectionInput",
    "get_client",
    "search",
    "get_section",
    "get_section_by_citation",
    "list_statutes",
    "parse_citation",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


class StatuteSearchInput(BaseModel):
    query: str
    statute: str | None = Field(
        default=None,
        description=(
            "Optional filter: 'PatG', 'MarkenG', 'GebrMG', 'DesignG', "
            "'UrhG', or 'GeschGehG'. Case-insensitive; long-form aliases "
            "(Patentgesetz, Markengesetz, …) accepted."
        ),
    )
    syntax: str = Field(default="and", description="'and', 'or', 'adj', or 'exact'")
    sort: str = Field(default="relevance", description="'relevance' (BM25) or 'outline'")
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SectionInput(BaseModel):
    section: str = Field(
        description=(
            "Section number, e.g. '1', '139', '14'. Pass ``citation`` "
            "(e.g. '§ 139 PatG') via :func:`get_section_by_citation` "
            "for the free-text form."
        ),
    )
    statute: str | None = Field(
        default=None,
        description=(
            "Optional discriminator when the section number exists in "
            "more than one Act (e.g. § 1 exists in PatG, GebrMG, "
            "DesignG, UrhG, and GeschGehG)."
        ),
    )


def get_client() -> DpmaStatutesClient:
    return DpmaStatutesClient()


async def search(params: StatuteSearchInput) -> DpmaSearchResult:
    async with DpmaStatutesClient() as client:
        return await client.search(
            params.query,
            statute=params.statute,
            syntax=params.syntax,
            sort=params.sort,
            per_page=params.per_page,
            page=params.page,
        )


async def get_section(params: SectionInput | str) -> DpmaSection:
    if isinstance(params, str):
        params = SectionInput(section=params)
    async with DpmaStatutesClient() as client:
        return await client.get_section(params.section, statute=params.statute)


async def get_section_by_citation(citation: str) -> DpmaSection:
    async with DpmaStatutesClient() as client:
        return await client.get_section_by_citation(citation)


async def list_statutes() -> list[str]:
    async with DpmaStatutesClient() as client:
        return await client.list_statutes()
