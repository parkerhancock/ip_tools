"""Pydantic models for USPTO Trademark Search API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TrademarkSearchResult(BaseModel):
    """A single trademark from the USPTO trademark search."""

    serial_number: str = Field(alias="serialNumber")
    registration_number: str | None = Field(default=None, alias="registrationNumber")
    wordmark: str | None = None
    status_live: bool = Field(alias="alive")
    owner_name: list[str] | None = Field(default=None, alias="ownerName")
    attorney: str | None = None
    filed_date: datetime | None = Field(default=None, alias="filedDate")
    registration_date: datetime | None = Field(default=None, alias="registrationDate")
    abandon_date: datetime | None = Field(default=None, alias="abandonDate")
    cancel_date: datetime | None = Field(default=None, alias="cancelDate")
    goods_and_services: list[str] | None = Field(default=None, alias="goodsAndServices")
    drawing_code: int | None = Field(default=None, alias="drawingCode")
    drawing_code_description: str | None = Field(default=None, alias="drawingCodeDescription")
    current_basis: list[str] | None = Field(default=None, alias="currentBasis")
    international_class: list[str] | None = Field(default=None, alias="internationalClass")
    us_class: list[str] | None = Field(default=None, alias="usClass")
    design_code: list[str] | None = Field(default=None, alias="designCode")
    design_code_description: list[str] | None = Field(default=None, alias="designCodeDescription")
    mark_description: list[str] | None = Field(default=None, alias="markDescription")
    disclaimer: str | None = None
    assignment_recorded: bool = Field(default=False, alias="assignmentRecorded")

    @field_validator(
        "filed_date", "registration_date", "abandon_date", "cancel_date", mode="before"
    )
    @classmethod
    def parse_date(cls, v: str | None) -> datetime | None:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    @field_validator(
        "design_code",
        "design_code_description",
        "international_class",
        "us_class",
        "current_basis",
        "goods_and_services",
        "owner_name",
        "mark_description",
        mode="before",
    )
    @classmethod
    def ensure_list(cls, v: str | list[str] | None) -> list[str] | None:
        """Convert comma-separated strings to lists."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        # Split comma-separated string
        return [s.strip() for s in v.split(",") if s.strip()]

    @property
    def is_live(self) -> bool:
        """Whether the trademark is currently live."""
        return self.status_live

    @property
    def is_registered(self) -> bool:
        """Whether the trademark is registered."""
        return self.registration_number is not None and self.cancel_date is None

    @property
    def primary_owner(self) -> str | None:
        """Get the primary owner name."""
        if self.owner_name and len(self.owner_name) > 0:
            return self.owner_name[0]
        return None


class TrademarkSearchResponse(BaseModel):
    """Response from the USPTO trademark search API."""

    total: int = 0
    results: list[TrademarkSearchResult] = Field(default_factory=list)
    query_time_ms: int = 0

    @property
    def count(self) -> int:
        """Number of results in this response."""
        return len(self.results)


__all__ = [
    "TrademarkSearchResult",
    "TrademarkSearchResponse",
]
