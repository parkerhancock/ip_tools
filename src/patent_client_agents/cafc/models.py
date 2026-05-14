"""Data models for CAFC opinions."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class CAFCOpinion(BaseModel):
    """A Federal Circuit opinion or order."""

    appeal_number: str
    release_date: date | None = None
    origin: str = ""  # PTO, DCT, ITC, CFC, etc.
    document_type: str = ""  # OPINION, ORDER, RULE 36 JUDGMENT
    case_name: str = ""
    case_name_short: str = ""
    precedential_status: str = ""  # Precedential, Nonprecedential
    file_path: str = ""  # WordPress relative path to PDF
    pdf_url: str = ""  # Full URL to PDF

    # Patent classification
    is_patent_case: bool = False
    patent_confidence: float = 0.0
    patent_keywords: list[str] = Field(default_factory=list)
