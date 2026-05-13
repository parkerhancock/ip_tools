"""Async API for EUIPO Trademark Search.

Mirror of :mod:`patent_client_agents.canlii.api` shape: Pydantic input
models + module-level coroutines that create and close a client per call
so one-shot use needs no context manager.

For batching, instantiate :class:`EuipoTrademarksClient` directly so
many calls share one OAuth token + cache.

Usage::

    from patent_client_agents.euipo_trademarks import (
        EuipoTrademarksClient,
        SearchTrademarksInput,
        search_trademarks,
        get_trademark,
    )

    # one-shot
    page = await search_trademarks(SearchTrademarksInput(
        query="wordMarkSpecification.verbalElement==*Apple* and status==REGISTERED",
        size=25,
    ))

    # batch — one client, one token, one cache
    async with EuipoTrademarksClient() as cl:
        for appno in interesting_marks:
            tm = await cl.get_trademark(appno)
            ...
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import EuipoEnvironment, EuipoTrademarksClient
from .models import (
    GoodsAndServicesClass,
    GoodsAndServicesTerms,
    MarkBasis,
    MarkFeature,
    MarkKind,
    Person,
    Publication,
    Status,
    Trademark,
    TrademarkSearchResult,
    TrademarkSearchResultItem,
    WordMarkSpecification,
)

__all__ = [
    "EuipoEnvironment",
    "EuipoTrademarksClient",
    "GetTrademarkInput",
    "GetTrademarkMediaInput",
    "GoodsAndServicesClass",
    "GoodsAndServicesTerms",
    "MarkBasis",
    "MarkFeature",
    "MarkKind",
    "Person",
    "Publication",
    "SearchTrademarksInput",
    "Status",
    "Trademark",
    "TrademarkSearchResult",
    "TrademarkSearchResultItem",
    "WordMarkSpecification",
    "get_client",
    "get_trademark",
    "get_trademark_image",
    "get_trademark_image_thumbnail",
    "get_trademark_model",
    "get_trademark_sound",
    "get_trademark_video",
    "search_trademarks",
]


class SearchTrademarksInput(BaseModel):
    query: str | None = Field(
        default=None,
        description=(
            "RSQL filter expression. Example: "
            "'wordMarkSpecification.verbalElement==*Apple* and status==REGISTERED'. "
            "Omit for an unfiltered listing of the full register."
        ),
    )
    page: int = Field(default=0, ge=0, description="0-indexed page number")
    size: int = Field(default=25, ge=10, le=100, description="Page size, 10..100")
    sort: str | None = Field(default=None, description="Sort spec, e.g. 'applicationDate:desc'")
    fields: str | None = Field(
        default=None,
        description="EBNF field selector, e.g. '!(goodsAndServices)' to skip heavy fields",
    )


class GetTrademarkInput(BaseModel):
    application_number: str = Field(
        description=(
            "EUTM application number, zero-padded 9-digit string "
            "(e.g. '000274084') or 'W########[A]' for international "
            "registrations designating the EU"
        )
    )


class GetTrademarkMediaInput(BaseModel):
    application_number: str


def get_client() -> EuipoTrademarksClient:
    """Create an :class:`EuipoTrademarksClient`. Prefer the context-manager form."""
    return EuipoTrademarksClient()


async def search_trademarks(params: SearchTrademarksInput) -> TrademarkSearchResult:
    async with EuipoTrademarksClient() as client:
        return await client.search(**params.model_dump())


async def get_trademark(params: GetTrademarkInput) -> Trademark:
    async with EuipoTrademarksClient() as client:
        return await client.get_trademark(params.application_number)


async def get_trademark_image(params: GetTrademarkMediaInput) -> bytes:
    async with EuipoTrademarksClient() as client:
        return await client.get_image(params.application_number)


async def get_trademark_image_thumbnail(params: GetTrademarkMediaInput) -> bytes:
    async with EuipoTrademarksClient() as client:
        return await client.get_image_thumbnail(params.application_number)


async def get_trademark_sound(params: GetTrademarkMediaInput) -> bytes:
    async with EuipoTrademarksClient() as client:
        return await client.get_sound(params.application_number)


async def get_trademark_video(params: GetTrademarkMediaInput) -> bytes:
    async with EuipoTrademarksClient() as client:
        return await client.get_video(params.application_number)


async def get_trademark_model(params: GetTrademarkMediaInput) -> bytes:
    async with EuipoTrademarksClient() as client:
        return await client.get_model(params.application_number)
