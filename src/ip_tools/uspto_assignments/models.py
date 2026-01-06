"""Models for USPTO Patent Assignment API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AssignmentParty(BaseModel):
    """An assignor or assignee in an assignment transaction."""

    name: str
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postcode: str | None = None


class AssignmentRecord(BaseModel):
    """A USPTO assignment document record.

    Contains information about a recorded assignment including parties,
    conveyance details, and associated patents/applications.
    """

    reel_number: str | None = None
    frame_number: str | None = None
    conveyance_text: str | None = None
    recorded_date: datetime | None = None
    execution_date: datetime | None = None
    assignors: list[AssignmentParty] = Field(default_factory=list)
    assignees: list[AssignmentParty] = Field(default_factory=list)
    patent_numbers: list[str] = Field(default_factory=list)
    application_numbers: list[str] = Field(default_factory=list)


__all__ = [
    "AssignmentParty",
    "AssignmentRecord",
]
