"""Pydantic models for the UPC statutes corpus."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpcInstrument(BaseModel):
    """A single legal instrument in the UPC corpus."""

    instrument: str = Field(
        description=(
            "Stable lowercase key — one of 'upca', 'statute', 'rop', "
            "'fees', 'coc'. 'statute' refers to the Statute of the UPC "
            "(Annex I to UPCA); 'rop' is the consolidated Rules of "
            "Procedure currently in force; 'fees' is the consolidated "
            "Table of Court Fees and Recoverable Costs; 'coc' is the "
            "Code of Conduct for Representatives."
        )
    )
    short_name: str = Field(description="Citation-ready short name, e.g. 'UPCA', 'RoP', 'Statute'.")
    title: str = Field(description="Full official title as it appears on the source.")
    language: str = Field(description="ISO 639-1 code: 'en', 'fr', or 'de'.")
    source_url: str
    source_version: str | None = Field(
        default=None,
        description=(
            "Version label or publication date as recorded by the build "
            "snapshot. Consolidated documents carry their last-amendment "
            "date here when discoverable."
        ),
    )
    pdf_pages: int | None = None


class UpcInstrumentText(UpcInstrument):
    """An instrument with its extracted plain text."""

    text: str


class UpcStatuteSearchHit(BaseModel):
    instrument: str
    short_name: str
    language: str
    snippet: str = Field(
        description=(
            "FTS5-rendered snippet with <mark>...</mark> tags around the "
            "matched terms. Token width tuned to ~200 characters."
        )
    )
    rank: float | None = Field(
        default=None,
        description="BM25 rank score (lower = more relevant) when sort='relevance'.",
    )


class UpcStatuteSearchResponse(BaseModel):
    query: str
    hits: list[UpcStatuteSearchHit]
    page: int
    per_page: int
    has_more: bool


class UpcCorpusMeta(BaseModel):
    schema_version: int
    snapshot_date: str | None = None
    instrument_count: int
