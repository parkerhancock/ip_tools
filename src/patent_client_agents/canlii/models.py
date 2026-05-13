"""Pydantic models for the CanLII REST API.

Field names mirror the upstream JSON (camelCase). Optional fields are
``None`` where the API may omit them.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["en", "fr"]
"""Output language code accepted by CanLII."""


class LegislationType(StrEnum):
    STATUTE = "STATUTE"
    REGULATION = "REGULATION"
    ANNUAL_STATUTE = "ANNUAL_STATUTE"


class CaseDatabase(BaseModel):
    """A CanLII court / tribunal database (one per court)."""

    database_id: str = Field(alias="databaseId")
    jurisdiction: str
    name: str

    model_config = {"populate_by_name": True}


class CaseId(BaseModel):
    """CanLII case identifier, scoped by language."""

    en: str | None = None
    fr: str | None = None


class CaseRef(BaseModel):
    """Lightweight case reference returned by browse/citator endpoints."""

    database_id: str = Field(alias="databaseId")
    case_id: CaseId = Field(alias="caseId")
    title: str
    citation: str

    model_config = {"populate_by_name": True}


class CaseMetadata(BaseModel):
    """Full metadata for a single case."""

    database_id: str = Field(alias="databaseId")
    case_id: str = Field(alias="caseId")
    url: str
    title: str
    citation: str
    language: Language
    docket_number: str | None = Field(default=None, alias="docketNumber")
    decision_date: date | None = Field(default=None, alias="decisionDate")
    keywords: str | None = None
    concatenated_id: str | None = Field(default=None, alias="concatenatedId")

    model_config = {"populate_by_name": True}


class CaseList(BaseModel):
    """Paginated case list from caseBrowse."""

    cases: list[CaseRef]


class CitedCasesResponse(BaseModel):
    cited_cases: list[CaseRef] = Field(alias="citedCases")

    model_config = {"populate_by_name": True}


class CitingCasesResponse(BaseModel):
    citing_cases: list[CaseRef] = Field(alias="citingCases")

    model_config = {"populate_by_name": True}


class CitedLegislationRef(BaseModel):
    """A legislation reference returned by the citator."""

    database_id: str = Field(alias="databaseId")
    legislation_id: str = Field(alias="legislationId")
    title: str
    citation: str | None = None
    type: LegislationType | None = None

    model_config = {"populate_by_name": True}


class CitedLegislationsResponse(BaseModel):
    cited_legislations: list[CitedLegislationRef] = Field(alias="citedLegislations")

    model_config = {"populate_by_name": True}


class LegislationDatabase(BaseModel):
    """A CanLII legislation database (statutes or regulations, scoped by jurisdiction)."""

    database_id: str = Field(alias="databaseId")
    type: LegislationType
    jurisdiction: str
    name: str

    model_config = {"populate_by_name": True}


class LegislationRef(BaseModel):
    """A legislation reference returned by browse."""

    database_id: str = Field(alias="databaseId")
    legislation_id: str = Field(alias="legislationId")
    title: str
    citation: str
    type: LegislationType

    model_config = {"populate_by_name": True}


class LegislationList(BaseModel):
    legislations: list[LegislationRef]


class LegislationPart(BaseModel):
    """A part (chapter / division) of a statute or regulation."""

    part_id: str = Field(alias="partId")
    part_name: str = Field(alias="partName")

    model_config = {"populate_by_name": True}


class LegislationMetadata(BaseModel):
    """Full metadata for a single statute or regulation."""

    legislation_id: str = Field(alias="legislationId")
    url: str
    title: str
    citation: str
    type: LegislationType
    language: Language
    date_scheme: str | None = Field(default=None, alias="dateScheme")
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    repealed: str | None = None
    content: list[LegislationPart] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class CaseDatabaseList(BaseModel):
    case_databases: list[CaseDatabase] = Field(alias="caseDatabases")

    model_config = {"populate_by_name": True}


class LegislationDatabaseList(BaseModel):
    legislation_databases: list[LegislationDatabase] = Field(alias="legislationDatabases")

    model_config = {"populate_by_name": True}


__all__ = [
    "Language",
    "LegislationType",
    "CaseDatabase",
    "CaseDatabaseList",
    "CaseId",
    "CaseList",
    "CaseMetadata",
    "CaseRef",
    "CitedCasesResponse",
    "CitedLegislationRef",
    "CitedLegislationsResponse",
    "CitingCasesResponse",
    "LegislationDatabase",
    "LegislationDatabaseList",
    "LegislationList",
    "LegislationMetadata",
    "LegislationPart",
    "LegislationRef",
]
