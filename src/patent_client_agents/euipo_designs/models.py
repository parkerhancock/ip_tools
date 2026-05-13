"""Pydantic models for the EUIPO Design (RCD) Search API.

Field names mirror the upstream JSON (camelCase). Models use
``extra="allow"`` so EUIPO can add new optional fields without breaking
parsing. The list endpoint returns :class:`DesignSearchResultItem`; the
detail endpoint returns the richer :class:`Design`.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

_BASE_CONFIG: ConfigDict = ConfigDict(populate_by_name=True, extra="allow")


class Status(StrEnum):
    """RCD lifecycle status."""

    RECEIVED = "RECEIVED"
    UNDER_EXAMINATION = "UNDER_EXAMINATION"
    REGISTRATION_PENDING = "REGISTRATION_PENDING"
    REGISTERED = "REGISTERED"
    REGISTERED_AND_FULLY_PUBLISHED = "REGISTERED_AND_FULLY_PUBLISHED"
    REGISTERED_AND_SUBJECT_TO_DEFERMENT = "REGISTERED_AND_SUBJECT_TO_DEFERMENT"
    LACK_OF_EFFECTS = "LACK_OF_EFFECTS"
    SURRENDERED = "SURRENDERED"
    INVALIDITY_PROCEDURE_PENDING = "INVALIDITY_PROCEDURE_PENDING"
    DESIGN_DECLARED_INVALID = "DESIGN_DECLARED_INVALID"
    EXPIRED = "EXPIRED"
    APPEALED = "APPEALED"
    APPEALABLE = "APPEALABLE"
    WITHDRAWN = "WITHDRAWN"
    REFUSED = "REFUSED"
    SPLIT = "SPLIT"


class Person(BaseModel):
    """Applicant or representative.

    ``name`` is documented as required but sandbox data sometimes
    returns Persons with only ``office`` + ``identifier``; we accept the
    looser shape to avoid bombing on real-world payloads.
    """

    office: str  # 'EM' or 'WO'
    name: str | None = None
    identifier: str | None = None

    model_config = _BASE_CONFIG


class Designer(BaseModel):
    identifier: str
    name: str | None = None

    model_config = _BASE_CONFIG


class ProductIndicationTerms(BaseModel):
    """Product description terms for one language."""

    language: str
    terms: list[str]

    model_config = _BASE_CONFIG


class View(BaseModel):
    """One angle of a design representation (e.g. front, side, top)."""

    order: int
    image_format: str = Field(alias="imageFormat")

    model_config = _BASE_CONFIG


class Model3D(BaseModel):
    """3D model attached to a design."""

    model_format: str = Field(alias="modelFormat")

    model_config = _BASE_CONFIG


class Publication(BaseModel):
    bulletin_number: str = Field(alias="bulletinNumber")
    publication_section: str = Field(alias="publicationSection")
    publication_date: date = Field(alias="publicationDate")

    model_config = _BASE_CONFIG


class DesignSearchResultItem(BaseModel):
    """Lean row returned by ``GET /designs`` (search)."""

    design_number: str = Field(alias="designNumber")
    application_date: date = Field(alias="applicationDate")
    status: Status
    applicants: list[Person]

    application_number: str | None = Field(default=None, alias="applicationNumber")
    applicant_reference: str | None = Field(default=None, alias="applicantReference")
    registration_date: date | None = Field(default=None, alias="registrationDate")
    expiry_date: date | None = Field(default=None, alias="expiryDate")
    locarno_classes: list[str] = Field(alias="locarnoClasses", default_factory=list)
    representatives: list[Person] = Field(default_factory=list)

    model_config = _BASE_CONFIG

    @property
    def is_live(self) -> bool:
        """True if the design is in any non-terminated state."""
        return self.status not in {
            Status.WITHDRAWN,
            Status.REFUSED,
            Status.LACK_OF_EFFECTS,
            Status.SURRENDERED,
            Status.DESIGN_DECLARED_INVALID,
            Status.EXPIRED,
        }

    @property
    def is_registered(self) -> bool:
        return self.status in {
            Status.REGISTERED,
            Status.REGISTERED_AND_FULLY_PUBLISHED,
            Status.REGISTERED_AND_SUBJECT_TO_DEFERMENT,
        }


class DesignSearchResult(BaseModel):
    """Envelope returned by ``GET /designs``."""

    designs: list[DesignSearchResultItem]
    total_elements: int = Field(alias="totalElements")
    total_pages: int = Field(alias="totalPages")
    size: int
    page: int

    model_config = _BASE_CONFIG


class Design(DesignSearchResultItem):
    """Full design record from ``GET /designs/{designNumber}``.

    Inherits the list-view fields and adds prosecution history + media
    metadata. Rare fields flow through via ``extra="allow"``.
    """

    application_language: str | None = Field(default=None, alias="applicationLanguage")
    second_language: str | None = Field(default=None, alias="secondLanguage")
    status_date: date | None = Field(default=None, alias="statusDate")
    effective_date: date | None = Field(default=None, alias="effectiveDate")
    publication_deferment_indicator: bool | None = Field(
        default=None, alias="publicationDefermentIndicator"
    )
    deferment_expiration_date: date | None = Field(default=None, alias="defermentExpirationDate")
    renewal_status: str | None = Field(default=None, alias="renewalStatus")

    verbal_element: str | None = Field(default=None, alias="verbalElement")
    product_indications: list[ProductIndicationTerms] = Field(
        alias="productIndications", default_factory=list
    )

    views: list[View] = Field(default_factory=list)
    model: Model3D | None = None
    publications: list[Publication] = Field(default_factory=list)
    designers: list[Designer] = Field(default_factory=list)

    model_config = _BASE_CONFIG

    def product_terms_in(self, language: str) -> list[str]:
        """Return the product terms for ``language`` (e.g. ``'en'``), or ``[]``."""
        for entry in self.product_indications:
            if entry.language == language:
                return entry.terms
        return []


__all__ = [
    "Design",
    "DesignSearchResult",
    "DesignSearchResultItem",
    "Designer",
    "Model3D",
    "Person",
    "ProductIndicationTerms",
    "Publication",
    "Status",
    "View",
]
