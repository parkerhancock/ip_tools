"""Async API for the Taiwan Trade Secrets Act corpus (MCP-free).

Usage
-----
Preferred: use the client as a context manager for proper resource cleanup::

    async with TwTradeSecretsClient() as client:
        section = await client.get_section_by_citation("Art. 13-1 Trade Secrets Act")
        hits = await client.search("damages")

One-shot convenience functions (create and close the client automatically)::

    section = await get_section_by_citation("Art. 13-1 Trade Secrets Act")
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import TwTradeSecretsClient, parse_citation
from .corpus import CorpusUnavailable
from .models import (
    TwTradeSecretsCorpusMeta,
    TwTradeSecretsSearchHit,
    TwTradeSecretsSearchResult,
    TwTradeSecretsSection,
)
from .resources import USAGE_RESOURCE_URI, get_usage_resource

__all__ = [
    "TwTradeSecretsClient",
    "CorpusUnavailable",
    "TwTradeSecretsSection",
    "TwTradeSecretsSearchHit",
    "TwTradeSecretsSearchResult",
    "TwTradeSecretsCorpusMeta",
    "SearchInput",
    "SectionInput",
    "get_client",
    "search",
    "get_section",
    "get_section_by_citation",
    "parse_citation",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


class SearchInput(BaseModel):
    """Input for full-text search across the bundled Trade Secrets Act."""

    query: str
    syntax: str = Field(default="and", description="'and', 'or', 'adj', or 'exact'")
    sort: str = Field(default="relevance", description="'relevance' (BM25) or 'outline'")
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SectionInput(BaseModel):
    """Input for fetching a specific Article."""

    section: str = Field(
        description=(
            "Article number, e.g. '2', '13', '13-1'. Citation forms like "
            "'Art. 2 Trade Secrets Act' are also accepted."
        ),
    )


def get_client() -> TwTradeSecretsClient:
    """Create a :class:`TwTradeSecretsClient`.

    Prefer using the client as a context manager::

        async with TwTradeSecretsClient() as client:
            ...
    """
    return TwTradeSecretsClient()


async def search(params: SearchInput) -> TwTradeSecretsSearchResult:
    async with TwTradeSecretsClient() as client:
        return await client.search(
            params.query,
            syntax=params.syntax,
            sort=params.sort,
            per_page=params.per_page,
            page=params.page,
        )


async def get_section(params: SectionInput | str) -> TwTradeSecretsSection:
    if isinstance(params, str):
        params = SectionInput(section=params)
    async with TwTradeSecretsClient() as client:
        return await client.get_section(params.section)


async def get_section_by_citation(citation: str) -> TwTradeSecretsSection:
    async with TwTradeSecretsClient() as client:
        return await client.get_section_by_citation(citation)
