"""Data models for US Copyright Office public records."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


def _coerce_to_list(v: Any) -> list[str]:
    """Wrap a single scalar value into a one-element list.

    The Copyright Office Public Records API returns scalar strings for
    fields that are *typically* multi-valued (registration_number,
    title_of_work, claimant, etc.) when a record happens to have only
    one value — e.g. early SR-prefix sound-recording registrations.
    Without this coercer the model rejects those rows with
    ``Input should be a valid list``.
    """
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v else []
    return v


class Claimant(BaseModel):
    """A copyright claimant."""

    claimant_full_name: str = ""


class CopyrightNumber(BaseModel):
    """A formatted copyright registration number."""

    copyright_number: str = ""


class CopyrightRecord(BaseModel):
    """A copyright registration or recorded document from the Copyright Office."""

    public_records_id: str = ""
    title_of_work: list[str] = Field(default_factory=list)
    registration_number: list[str] = Field(default_factory=list)
    copyright_number_for_display: str = ""
    type_of_record: str = ""  # "registration" or "recordation"
    registration_status: str = ""  # "published", "unpublished"
    registration_class: list[str] = Field(default_factory=list)

    # People
    claimant: list[str] = Field(default_factory=list)
    claimants: list[Claimant] = Field(default_factory=list)
    publisher_name: list[str] = Field(default_factory=list)

    # Work classification
    type_of_work: str | None = None
    all_type_of_work: list[str] = Field(default_factory=list)
    system_of_origin: str = ""  # "voyager" (post-1978) or "card_catalog"

    # Dates
    application_date: list[str] = Field(default_factory=list)
    first_published_date: list[str] = Field(default_factory=list)
    fee_date: list[str] = Field(default_factory=list)
    deposit_received_date: list[str] = Field(default_factory=list)
    representative_date: str = ""

    # Card catalog images (LOC tile server)
    link_to_image_url: list[str] = Field(default_factory=list)

    # Relevance score from search
    score: float = 0.0

    _coerce = field_validator(
        "title_of_work",
        "registration_number",
        "registration_class",
        "claimant",
        "publisher_name",
        "all_type_of_work",
        "application_date",
        "first_published_date",
        "fee_date",
        "deposit_received_date",
        "link_to_image_url",
        mode="before",
    )(classmethod(lambda cls, v: _coerce_to_list(v)))


class SearchMetadata(BaseModel):
    """Metadata from a copyright search response."""

    took_ms: int = 0
    hit_count: int = 0
    hit_count_relation: str = "eq"
    max_score: float = 0.0
    query: str = ""
    fields: str = ""


class Histogram(BaseModel):
    """Facet counts from a search response."""

    type_of_record: dict[str, int] = Field(default_factory=dict)
    type_of_work: dict[str, int] = Field(default_factory=dict)
    registration_class: dict[str, int] = Field(default_factory=dict)
    registration_status: dict[str, int] = Field(default_factory=dict)
    system_of_origin: dict[str, int] = Field(default_factory=dict)
    recordation_item_type: dict[str, int] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response from a copyright search."""

    metadata: SearchMetadata = Field(default_factory=SearchMetadata)
    histogram: Histogram = Field(default_factory=Histogram)
    records: list[CopyrightRecord] = Field(default_factory=list)
