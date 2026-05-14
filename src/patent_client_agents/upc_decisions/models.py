"""Pydantic models for the UPC decisions and orders feed."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpcDecision(BaseModel):
    """A single row from the UPC decisions-and-orders index."""

    case_id: str = Field(
        description=(
            "Canonical UPC case identifier — UPC_CFI_<n>/<yyyy>, "
            "UPC_CoA_<n>/<yyyy>, or ACT_<n>/<yyyy>. Normalized to "
            "underscore-separated form regardless of how it appears in "
            "the source row (the index inconsistently uses hyphens, "
            "underscores, and 7-digit zero-padded variants)."
        )
    )
    raw_references: list[str] = Field(
        default_factory=list,
        description=(
            "All case-identifier strings as they appear in the row. "
            "Some rows list two references (e.g. a registry number AND a "
            "related case number) — both are preserved here verbatim."
        ),
    )
    detail_url: str = Field(
        description=(
            "Per-decision detail page (https://www.unifiedpatentcourt.org/en/node/<id>). "
            "Note: these pages sit behind Cloudflare's interactive "
            "challenge — the index row already carries the structured "
            "fields, so callers rarely need to follow this link."
        )
    )
    court: str = Field(
        description=(
            "Division name as displayed, e.g. 'Düsseldorf (DE) Local Division', "
            "'Luxembourg (LU)', 'Stockholm (SE) - Seat of the Regional Division'."
        )
    )
    type_of_action: str = Field(
        description=(
            "Case type, e.g. 'Application for provisional measures', "
            "'Infringement Action', 'Generic Order', 'Request for a "
            "discretionary review (RoP 220.3)'."
        )
    )
    parties: list[str] = Field(
        default_factory=list,
        description=(
            "Parties split on 'v.'-style separators. The first entry is "
            "the claimant/applicant side, the second the respondent side. "
            "Multi-party sides remain as single strings — splitting "
            "further is unreliable across the index's inconsistent formatting."
        ),
    )
    pdf_urls: list[str] = Field(
        default_factory=list,
        description=(
            "All PDF document URLs attached to this row. Most rows have "
            "one PDF/A order/decision; some bundle redactions or "
            "translations as additional attachments."
        ),
    )


class UpcDecisionSearchResponse(BaseModel):
    page: int
    total_pages: int = Field(
        description=(
            "Total page count parsed from the pager. Subject to "
            "drift as new decisions are added daily."
        )
    )
    hits: list[UpcDecision]


class UpcDivision(BaseModel):
    """A division ID surfaced by the UI's filter dropdown."""

    id: str = Field(description="Numeric ID used as the division filter value.")
    name: str


class UpcLanguage(BaseModel):
    """A procedural-language option from the UI's filter dropdown."""

    id: str = Field(description="Numeric ID used as the proceedings_lang filter value.")
    name: str
