"""Async API for the IPO India statutes corpus (MCP-free).

Usage
-----
Preferred: use the client as a context manager for proper resource cleanup::

    async with IpoInStatutesClient() as client:
        section = await client.get_section_by_citation("Section 3(d) Patents Act")
        hits = await client.search("compulsory licensing", statute_name="Patents Act")

One-shot convenience functions (create and close the client automatically)::

    section = await get_section_by_citation("Section 3(d) Patents Act")
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import IpoInStatutesClient, parse_citation
from .corpus import CorpusUnavailable
from .models import (
    IpoInCorpusMeta,
    IpoInSearchHit,
    IpoInSearchResponse,
    IpoInSection,
)
from .resources import USAGE_RESOURCE_URI, get_usage_resource

__all__ = [
    "IpoInStatutesClient",
    "CorpusUnavailable",
    "IpoInSection",
    "IpoInSearchHit",
    "IpoInSearchResponse",
    "IpoInCorpusMeta",
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
    statute_name: str | None = Field(
        default=None,
        description=(
            "Optional filter: 'Patents Act', 'Patent Rules', 'Designs Act', "
            "'Trade Marks Act', or 'Copyright Act'. Case-insensitive; aliases "
            "like 'patents act 1970' are accepted."
        ),
    )
    syntax: str = Field(default="and", description="'and', 'or', 'adj', or 'exact'")
    sort: str = Field(default="relevance", description="'relevance' (BM25) or 'outline'")
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SectionInput(BaseModel):
    section_number: str = Field(
        description=(
            "Section / rule number, e.g. '3(d)', '25(2)', '107A', '71'. "
            "Pass ``citation`` instead to use the free-text form."
        ),
    )
    statute_name: str | None = Field(
        default=None,
        description=(
            "Optional discriminator when the section number exists in "
            "more than one Act (e.g. §13 exists in both the Copyright Act "
            "and the Trade Marks Act)."
        ),
    )


def get_client() -> IpoInStatutesClient:
    return IpoInStatutesClient()


async def search(params: StatuteSearchInput) -> IpoInSearchResponse:
    async with IpoInStatutesClient() as client:
        return await client.search(
            params.query,
            statute_name=params.statute_name,
            syntax=params.syntax,
            sort=params.sort,
            per_page=params.per_page,
            page=params.page,
        )


async def get_section(params: SectionInput | str) -> IpoInSection:
    if isinstance(params, str):
        params = SectionInput(section_number=params)
    async with IpoInStatutesClient() as client:
        return await client.get_section(params.section_number, statute_name=params.statute_name)


async def get_section_by_citation(citation: str) -> IpoInSection:
    async with IpoInStatutesClient() as client:
        return await client.get_section_by_citation(citation)


async def list_statutes() -> list[str]:
    async with IpoInStatutesClient() as client:
        return await client.list_statutes()
