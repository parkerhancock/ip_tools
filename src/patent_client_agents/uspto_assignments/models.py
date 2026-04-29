"""Pydantic models for USPTO Assignment Center API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Assignor(BaseModel):
    """An assignor (party transferring rights) in an assignment."""

    assignor_name: str = Field(alias="assignorName")
    execution_date: str | None = Field(default=None, alias="executionDate")


class Property(BaseModel):
    """A patent property referenced in an assignment."""

    sequence_number: int | None = Field(default=None, alias="sequenceNumber")
    application_number: str | None = Field(default=None, alias="applicationNumber")
    filing_date: str | None = Field(default=None, alias="fillingDate")  # Note: API typo
    patent_number: str | None = Field(default=None, alias="patentNumber")
    publication_number: str | None = Field(default=None, alias="publicationNumber")
    publication_date: str | None = Field(default=None, alias="publicationDate")
    pct_number: str | None = Field(default=None, alias="pctNumber")
    international_registration_number: str | None = Field(
        default=None, alias="internationalRegistrationNumber"
    )
    international_publication_date: str | None = Field(
        default=None, alias="internationalPublicationDate"
    )
    invention_title: str | None = Field(default=None, alias="inventionTitle")
    inventors: str | None = None
    issue_date: str | None = Field(default=None, alias="issueDate")


class AssignmentRecord(BaseModel):
    """A single assignment record from the USPTO Assignment Center."""

    reel_number: int = Field(alias="reelNumber")
    frame_number: int = Field(alias="frameNumber")
    assignor_execution_date: str | None = Field(default=None, alias="assignorExecutionDate")
    correspondent_name: str | None = Field(default=None, alias="correspondentName")
    assignors: list[Assignor] = Field(default_factory=list)
    assignees: list[str] = Field(default_factory=list)
    # NOTE: The ``exportPublicPatentData`` endpoint that backs ``search_*`` does
    # not include conveyance text in its response, so this field is always
    # ``None`` for records returned by those methods. Use
    # ``AssignmentCenterClient.get_application_assignments()`` if you need the
    # conveyance type (e.g. "ASSIGNMENT", "CHANGE OF NAME", "SECURITY AGREEMENT").
    conveyance_text: str | None = Field(default=None, alias="conveyanceText")
    number_of_properties: int = Field(default=0, alias="noOfProperties")
    properties: list[Property] = Field(default_factory=list)

    @property
    def reel_frame(self) -> str:
        """Return reel/frame as a formatted string."""
        return f"{self.reel_number}/{self.frame_number}"


class SearchCriterion(BaseModel):
    """A search criterion echoed back in the response."""

    property: str
    search_by: str = Field(alias="searchBy")


class AssignmentSearchResponse(BaseModel):
    """Response from the Assignment Center search API."""

    search_criteria: list[SearchCriterion] = Field(default_factory=list, alias="searchCriteria")
    data: list[AssignmentRecord] = Field(default_factory=list)

    @property
    def count(self) -> int:
        """Number of records in this response."""
        return len(self.data)


class AssignmentDetail(BaseModel):
    """A single assignment recordation as returned by the search/patent endpoint.

    This is a richer per-recordation shape than ``AssignmentRecord``: it
    includes ``conveyance`` (e.g. "ASSIGNMENT OF ASSIGNOR'S INTEREST",
    "CHANGE OF NAME", "SECURITY AGREEMENT"), recordation/receipt/mail dates,
    and a link to the cover-sheet image. Returned by
    ``AssignmentCenterClient.get_application_assignments()``.
    """

    model_config = {"extra": "allow"}

    reel_number: int = Field(alias="reelNumber")
    frame_number: int = Field(alias="frameNumber")
    conveyance: str | None = None
    conveyance_code: int | None = Field(default=None, alias="conveyanceCode")
    recordation_date: str | None = Field(default=None, alias="recordationDate")
    receipt_date: str | None = Field(default=None, alias="receiptDate")
    mail_date: str | None = Field(default=None, alias="mailDate")
    page_count: int | None = Field(default=None, alias="pageCount")
    image_url: str | None = Field(default=None, alias="imageURL")
    assignors: list[Assignor] = Field(default_factory=list)
    assignees: list[Any] = Field(default_factory=list)
    correspondent: Any | None = None
    documents: list[Any] = Field(default_factory=list)

    @property
    def reel_frame(self) -> str:
        """Return reel/frame as a formatted string."""
        return f"{self.reel_number}/{self.frame_number}"


class ApplicationAssignmentBundle(BaseModel):
    """Per-application assignment bundle returned by ``search/patent``.

    Wraps the ``data`` object: a single ``properties`` block describing the
    application/patent and an ``assignment`` array of every recordation that
    has been made against it.
    """

    model_config = {"extra": "allow"}

    properties: dict[str, Any] | None = None
    assignment: list[AssignmentDetail] = Field(default_factory=list)
    no_of_assignments: int = Field(default=0, alias="noOfAssignments")


__all__ = [
    "Assignor",
    "Property",
    "AssignmentRecord",
    "SearchCriterion",
    "AssignmentSearchResponse",
    "AssignmentDetail",
    "ApplicationAssignmentBundle",
]
