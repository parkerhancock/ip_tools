"""Pydantic models for the Australian Trade Mark Search API.

Field shapes are inferred from the public description page at
``descriptions.api.gov.au/ipaustralia/trademark-search/`` and from the
ATMOSS UI; the upstream does not publish a Swagger spec. ``extra="allow"``
keeps parsing forward-compatible with fields the upstream may add.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_BASE_CONFIG: ConfigDict = ConfigDict(populate_by_name=True, extra="allow")


class TrademarkSearchHit(BaseModel):
    """Lean row from ``POST /search/quick`` on the trade marks API.

    Each hit carries the Australian trade mark number (``serial_number``)
    plus the bibliographic fields IP Australia surfaces in its
    quick-search list view.
    """

    serial_number: str | None = Field(default=None, alias="serialNumber")
    word_mark: str | None = Field(default=None, alias="wordMark")
    status: str | None = None
    mark_type: str | None = Field(default=None, alias="markType")
    application_date: str | None = Field(default=None, alias="applicationDate")
    registration_date: str | None = Field(default=None, alias="registrationDate")
    nice_classes: list[Any] = Field(default_factory=list, alias="niceClasses")
    owners: list[Any] = Field(default_factory=list)

    model_config = _BASE_CONFIG


class TrademarkSearchResult(BaseModel):
    """Envelope returned by ``POST /search/quick`` on the trade marks API."""

    results: list[TrademarkSearchHit] = Field(default_factory=list)
    total: int | None = None

    model_config = _BASE_CONFIG


class Trademark(BaseModel):
    """Full Australian trade mark record from ``GET /trade-mark/{id}``."""

    serial_number: str | None = Field(default=None, alias="serialNumber")
    word_mark: str | None = Field(default=None, alias="wordMark")
    status: str | None = None
    mark_type: str | None = Field(default=None, alias="markType")
    application_date: str | None = Field(default=None, alias="applicationDate")
    registration_date: str | None = Field(default=None, alias="registrationDate")
    renewal_date: str | None = Field(default=None, alias="renewalDate")
    expiry_date: str | None = Field(default=None, alias="expiryDate")
    nice_classes: list[Any] = Field(default_factory=list, alias="niceClasses")
    owners: list[Any] = Field(default_factory=list)
    goods_and_services: list[Any] = Field(default_factory=list, alias="goodsAndServices")
    representatives: list[Any] = Field(default_factory=list)

    model_config = _BASE_CONFIG


__all__ = [
    "Trademark",
    "TrademarkSearchHit",
    "TrademarkSearchResult",
]
