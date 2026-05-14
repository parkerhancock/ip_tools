"""Async API for the UPC decisions-and-orders feed (MCP-free)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .client import DEFAULT_LANGUAGE, UpcDecisionsClient
from .models import (
    UpcDecision,
    UpcDecisionSearchResponse,
    UpcDivision,
    UpcLanguage,
)

__all__ = [
    "UpcDecisionsClient",
    "UpcDecision",
    "UpcDecisionSearchResponse",
    "UpcDivision",
    "UpcLanguage",
    "DecisionSearchInput",
    "DecisionLookupInput",
    "get_client",
    "search_decisions",
    "get_decision",
    "download_decision_pdf",
    "list_divisions",
    "list_languages",
]


class DecisionSearchInput(BaseModel):
    page: int = Field(default=0, ge=0, description="0-indexed page number")
    judgement_type: str | None = Field(
        default=None,
        description="Either 'order' or 'decision'; omit to include both.",
    )
    court_type: str | None = Field(
        default=None,
        description=(
            "Court-type filter ID. '1' = Court of Appeal, "
            "'2' = Central Divisions of the CFI, "
            "'3' = Local Divisions of the CFI, "
            "'4' = Regional Divisions of the CFI."
        ),
    )
    division: str | None = Field(
        default=None,
        description="Specific division ID — use list_divisions() to discover.",
    )
    proceedings_lang: str | None = Field(
        default=None,
        description="Procedural-language filter ID — use list_languages() to discover.",
    )
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        description="UI language for the listing page ('en', 'fr', or 'de').",
    )


class DecisionLookupInput(BaseModel):
    case_id: str = Field(
        description=(
            "Canonical UPC case identifier — UPC_CFI_<n>/<yyyy>, "
            "UPC_CoA_<n>/<yyyy>, or ACT_<n>/<yyyy>. Hyphenated variants "
            "are accepted and normalized."
        )
    )
    language: str = Field(default=DEFAULT_LANGUAGE)


def get_client(language: str = DEFAULT_LANGUAGE) -> UpcDecisionsClient:
    """Construct a UPC decisions client.

    Prefer using the client as a context manager::

        async with UpcDecisionsClient() as client:
            ...
    """
    return UpcDecisionsClient(language=language)


async def search_decisions(params: DecisionSearchInput) -> UpcDecisionSearchResponse:
    async with UpcDecisionsClient(language=params.language) as client:
        return await client.search(
            page=params.page,
            judgement_type=params.judgement_type,
            court_type=params.court_type,
            division=params.division,
            proceedings_lang=params.proceedings_lang,
        )


async def get_decision(params: DecisionLookupInput | str) -> UpcDecision | None:
    if isinstance(params, str):
        params = DecisionLookupInput(case_id=params)
    async with UpcDecisionsClient(language=params.language) as client:
        return await client.get_decision(params.case_id)


async def download_decision_pdf(pdf_url: str, *, language: str = DEFAULT_LANGUAGE) -> bytes:
    async with UpcDecisionsClient(language=language) as client:
        return await client.download_pdf(pdf_url)


async def list_divisions(language: str = DEFAULT_LANGUAGE) -> list[UpcDivision]:
    async with UpcDecisionsClient(language=language) as client:
        return await client.list_divisions()


async def list_languages(language: str = DEFAULT_LANGUAGE) -> list[UpcLanguage]:
    async with UpcDecisionsClient(language=language) as client:
        return await client.list_languages()
