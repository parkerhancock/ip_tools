"""Async API for WIPO Lex.

Mirror of the :mod:`patent_client_agents.mpep.api` shape: a Pydantic input
plus a module-level coroutine that opens + closes the client for one-shot
callers.

Usage::

    from patent_client_agents.wipo_lex import (
        SearchLegislationInput,
        SubjectMatter,
        WipoLexClient,
        get_legislation,
        search_legislation,
    )

    hits = await search_legislation(
        SearchLegislationInput(country_codes=["CA"], subject_matter=[SubjectMatter.PATENTS])
    )
    detail = await get_legislation("23293")
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import WipoLexClient
from .models import (
    LegislationDetail,
    LegislationSearchHit,
    LegislationSearchResponse,
    SubjectMatter,
    TypeOfText,
    WipoLexCollection,
    WipoLexFileLink,
)
from .resources import USAGE_RESOURCE_URI, get_usage_resource

__all__ = [
    # Client
    "WipoLexClient",
    "get_client",
    # Inputs
    "SearchLegislationInput",
    "GetLegislationInput",
    # Functions
    "search_legislation",
    "get_legislation",
    # Models
    "LegislationDetail",
    "LegislationSearchHit",
    "LegislationSearchResponse",
    "SubjectMatter",
    "TypeOfText",
    "WipoLexCollection",
    "WipoLexFileLink",
    # Resources
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


class SearchLegislationInput(BaseModel):
    country_codes: list[str] | None = Field(
        default=None,
        description="ISO 3166-1 alpha-2 country / regional org codes (e.g. ['CA', 'US', 'EU']).",
    )
    subject_matter: list[SubjectMatter] | None = Field(
        default=None, description="One or more SubjectMatter codes."
    )
    type_of_text: list[TypeOfText] | None = Field(
        default=None, description="One or more TypeOfText codes (e.g. MAIN_IP_LAWS = 205)."
    )
    keywords: str | None = Field(default=None, description="Free-text search over title + notes.")
    start_date: str | None = Field(default=None, description="Lower bound (YYYY-MM-DD).")
    end_date: str | None = Field(default=None, description="Upper bound (YYYY-MM-DD).")
    include_historical: bool = Field(
        default=False, description="Include superseded / historical texts."
    )


class GetLegislationInput(BaseModel):
    legislation_id: str = Field(description="WIPO Lex internal ID (e.g. '23293').")


def get_client() -> WipoLexClient:
    """Create a WipoLexClient. Prefer the context-manager form directly."""
    return WipoLexClient()


async def search_legislation(params: SearchLegislationInput) -> LegislationSearchResponse:
    async with WipoLexClient() as client:
        return await client.search_legislation(**params.model_dump())


async def get_legislation(params: GetLegislationInput | str | int) -> LegislationDetail:
    if not isinstance(params, GetLegislationInput):
        params = GetLegislationInput(legislation_id=str(params))
    async with WipoLexClient() as client:
        return await client.get_legislation(params.legislation_id)
