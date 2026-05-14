"""Async API for the UPC statutes corpus (MCP-free)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import UpcStatutesClient
from .corpus import CorpusUnavailable
from .models import (
    UpcCorpusMeta,
    UpcInstrument,
    UpcInstrumentText,
    UpcStatuteSearchHit,
    UpcStatuteSearchResponse,
)
from .resources import USAGE_RESOURCE_URI, get_usage_resource

__all__ = [
    "UpcStatutesClient",
    "CorpusUnavailable",
    "UpcInstrument",
    "UpcInstrumentText",
    "UpcCorpusMeta",
    "UpcStatuteSearchHit",
    "UpcStatuteSearchResponse",
    "StatuteSearchInput",
    "InstrumentInput",
    "get_client",
    "search",
    "get_instrument",
    "list_instruments",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]


class StatuteSearchInput(BaseModel):
    query: str
    instrument: str | None = Field(
        default=None,
        description=(
            "Optional instrument key — 'upca', 'rop', 'fees', 'coc', "
            "or 'statute' (alias for the UPCA Annex I portion). "
            "Aliases like 'rules of procedure' are accepted."
        ),
    )
    language: str | None = Field(
        default="en",
        description="ISO 639-1 code: 'en', 'fr', or 'de'. Pass None to search all languages.",
    )
    syntax: str = Field(default="and", description="'and', 'or', 'adj', or 'exact'")
    sort: str = Field(default="relevance", description="'relevance' (BM25) or 'instrument'")
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class InstrumentInput(BaseModel):
    instrument: str = Field(
        description="Instrument key or alias — 'upca', 'rop', 'fees', 'coc', 'statute'."
    )
    language: str = Field(default="en")


def get_client() -> UpcStatutesClient:
    return UpcStatutesClient()


async def search(params: StatuteSearchInput) -> UpcStatuteSearchResponse:
    async with UpcStatutesClient() as client:
        return await client.search(
            params.query,
            instrument=params.instrument,
            language=params.language,
            syntax=params.syntax,
            sort=params.sort,
            per_page=params.per_page,
            page=params.page,
        )


async def get_instrument(params: InstrumentInput | str) -> UpcInstrumentText | None:
    if isinstance(params, str):
        params = InstrumentInput(instrument=params)
    async with UpcStatutesClient() as client:
        return await client.get_instrument(instrument=params.instrument, language=params.language)


async def list_instruments(language: str | None = None) -> list[UpcInstrument]:
    async with UpcStatutesClient() as client:
        return await client.list_instruments(language=language)
