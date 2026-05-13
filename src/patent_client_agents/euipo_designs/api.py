"""Async API for EUIPO Design Search (RCD).

Same shape as :mod:`patent_client_agents.canlii.api` and
:mod:`patent_client_agents.euipo_trademarks.api`: Pydantic inputs +
module-level one-shot coroutines.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import EuipoDesignsClient, EuipoEnvironment
from .models import (
    Design,
    Designer,
    DesignSearchResult,
    DesignSearchResultItem,
    Model3D,
    Person,
    ProductIndicationTerms,
    Publication,
    Status,
    View,
)

__all__ = [
    "Design",
    "DesignSearchResult",
    "DesignSearchResultItem",
    "Designer",
    "EuipoDesignsClient",
    "EuipoEnvironment",
    "GetDesignInput",
    "GetDesignMediaInput",
    "GetDesignViewInput",
    "Model3D",
    "Person",
    "ProductIndicationTerms",
    "Publication",
    "SearchDesignsInput",
    "Status",
    "View",
    "get_client",
    "get_design",
    "get_design_model",
    "get_design_view",
    "get_design_view_thumbnail",
    "search_designs",
]


class SearchDesignsInput(BaseModel):
    query: str | None = Field(
        default=None,
        description=(
            "RSQL filter expression. Example: "
            "'applicationDate>=2024-01-01 and locarnoClasses=in=(14.03,14.04)'. "
            "Omit for an unfiltered listing of the full register."
        ),
    )
    page: int = Field(default=0, ge=0)
    size: int = Field(default=25, ge=10, le=100)
    sort: str | None = Field(default=None, description="Sort spec, e.g. 'applicationDate:desc'")
    fields: str | None = None


class GetDesignInput(BaseModel):
    design_number: str = Field(
        description="RCD design number, e.g. '099037115-0001' (9 digits + dash + 4 digits)"
    )


class GetDesignViewInput(BaseModel):
    design_number: str
    order: int = Field(ge=1, description="1-indexed view order, matches View.order")


class GetDesignMediaInput(BaseModel):
    design_number: str


def get_client() -> EuipoDesignsClient:
    """Create an :class:`EuipoDesignsClient`. Prefer the context-manager form."""
    return EuipoDesignsClient()


async def search_designs(params: SearchDesignsInput) -> DesignSearchResult:
    async with EuipoDesignsClient() as client:
        return await client.search(**params.model_dump())


async def get_design(params: GetDesignInput) -> Design:
    async with EuipoDesignsClient() as client:
        return await client.get_design(params.design_number)


async def get_design_view(params: GetDesignViewInput) -> bytes:
    async with EuipoDesignsClient() as client:
        return await client.get_view(params.design_number, params.order)


async def get_design_view_thumbnail(params: GetDesignViewInput) -> bytes:
    async with EuipoDesignsClient() as client:
        return await client.get_view_thumbnail(params.design_number, params.order)


async def get_design_model(params: GetDesignMediaInput) -> bytes:
    async with EuipoDesignsClient() as client:
        return await client.get_model(params.design_number)
