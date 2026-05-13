"""Pydantic models for the WIPO Lex connector."""

from __future__ import annotations

from enum import IntEnum, StrEnum

from pydantic import BaseModel, Field


class SubjectMatter(IntEnum):
    """WIPO Lex ``subjectMatter`` codes — embedded in the search form dropdowns."""

    PATENTS = 1
    UTILITY_MODELS = 2
    INDUSTRIAL_DESIGNS = 3
    TRADEMARKS = 4
    GEOGRAPHICAL_INDICATIONS = 5
    TRADE_NAMES = 6
    INTEGRATED_CIRCUIT_LAYOUTS = 7
    COMPETITION = 8
    TRADE_SECRETS = 9
    PLANT_VARIETY_PROTECTION = 10
    COPYRIGHT = 11
    ENFORCEMENT = 12
    ADR = 13
    DOMAIN_NAMES = 14
    GENETIC_RESOURCES = 15
    TRADITIONAL_CULTURAL_EXPRESSIONS = 16
    TECHNOLOGY_TRANSFER = 17
    TRADITIONAL_KNOWLEDGE = 18
    IP_REGULATORY_BODY = 19
    OTHER = 20
    INDUSTRIAL_PROPERTY = 21


class TypeOfText(IntEnum):
    """WIPO Lex ``typeOfText`` codes for the legislation search."""

    MAIN_IP_LAWS = 205
    IMPLEMENTING_RULES = 207
    IP_RELATED_LAWS = 210
    FRAMEWORK_LAWS = 213
    OTHER_TEXTS = 214
    NATIONAL_IP_STRATEGY = 215


class WipoLexCollection(StrEnum):
    """The three WIPO Lex collections."""

    LEGISLATION = "legislation"
    TREATIES = "treaties"
    JUDGMENTS = "judgments"


class LegislationSearchHit(BaseModel):
    """A single legislation entry as it appears on a ``/results`` page.

    Result-page HTML carries the WIPO Lex ID and a one-line title with
    inline citation; the rest of the metadata lives on the
    ``/legislation/details/{id}`` page.
    """

    legislation_id: str = Field(description="WIPO Lex internal ID (e.g. '23293')")
    title: str = Field(description="Display title incl. inline citation")
    url: str = Field(description="Absolute URL on www.wipo.int")


class LegislationSearchResponse(BaseModel):
    """Paginated-style result set; WIPO Lex returns the full match list per query."""

    hits: list[LegislationSearchHit]
    query_url: str = Field(description="The URL that produced this result set")


class WipoLexFileLink(BaseModel):
    """A downloadable attachment on a legislation detail page (PDF/DOC/text)."""

    label: str
    url: str
    mime_type: str | None = None


class LegislationDetail(BaseModel):
    """Full metadata for a single WIPO Lex legislation entry.

    Extracted from the ``/legislation/details/{id}`` page. The bulk of the
    canonical metadata travels on OpenGraph + ``<meta name>`` tags, which
    are stable across page redesigns.
    """

    legislation_id: str
    title: str = Field(description="WIPO Lex display title (matches og:title)")
    jurisdiction: str | None = Field(
        default=None,
        description="Country / regional org name as shown in the description meta",
    )
    summary: str | None = Field(
        default=None,
        description="The full og:description string (year, assent date, type, subjects)",
    )
    url: str = Field(description="Canonical WIPO Lex URL")
    files: list[WipoLexFileLink] = Field(
        default_factory=list, description="PDF / DOC attachments linked on the page"
    )


__all__ = [
    "LegislationDetail",
    "LegislationSearchHit",
    "LegislationSearchResponse",
    "SubjectMatter",
    "TypeOfText",
    "WipoLexCollection",
    "WipoLexFileLink",
]
