from __future__ import annotations

from typing import Any

from pydantic import AnyHttpUrl, BaseModel, Field


class EdisInvestigation(BaseModel):
    investigation_number: str = Field(alias="investigationNumber")
    investigation_phase: str | None = Field(default=None, alias="investigationPhase")
    investigation_type: str | None = Field(default=None, alias="investigationType")
    investigation_status: str | None = Field(default=None, alias="investigationStatus")
    title: str | None = Field(default=None, alias="investigationTitle")
    docket_number: str | None = Field(default=None, alias="docketNumber")
    document_list_uri: str | None = Field(default=None, alias="documentListUri")


class EdisDocument(BaseModel):
    id: int
    document_type: str | None = Field(default=None, alias="documentType")
    title: str | None = Field(default=None, alias="documentTitle")
    security_level: str | None = Field(default=None, alias="securityLevel")
    investigation_number: str | None = Field(default=None, alias="investigationNumber")
    investigation_phase: str | None = Field(default=None, alias="investigationPhase")
    investigation_status: str | None = Field(default=None, alias="investigationStatus")
    investigation_title: str | None = Field(default=None, alias="investigationTitle")
    investigation_type: str | None = Field(default=None, alias="investigationType")
    firm_organization: str | None = Field(default=None, alias="firmOrganization")
    filed_by: str | None = Field(default=None, alias="filedBy")
    on_behalf_of: str | None = Field(default=None, alias="onBehalfOf")
    document_date: str | None = Field(default=None, alias="documentDate")
    official_received_date: str | None = Field(default=None, alias="officialReceivedDate")
    attachment_list_uri: str | None = Field(default=None, alias="attachmentListUri")
    modified_date: str | None = Field(default=None, alias="modifiedDate")


class EdisAttachment(BaseModel):
    id: int
    document_id: int = Field(alias="documentId")
    title: str | None = None
    file_size: int | None = Field(default=None, alias="fileSize")
    original_file_name: str | None = Field(default=None, alias="originalFileName")
    page_count: int | None = Field(default=None, alias="pageCount")
    create_date: str | None = Field(default=None, alias="createDate")
    last_modified_date: str | None = Field(default=None, alias="lastModifiedDate")
    download_uri: AnyHttpUrl | None = Field(default=None, alias="downloadUri")


class DownloadedAttachment(BaseModel):
    document_id: int
    attachment_id: int
    filename: str | None = None
    content_type: str | None = None
    content_base64: str


class DataWebReport(BaseModel):
    dto: dict[str, Any]
    raw: dict[str, Any]


class SavedQuerySummary(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: str | None = Field(default=None, alias="createdDate")


class IdsInvestigation(BaseModel):
    investigation_id: int = Field(alias="Investigation ID")
    investigation_number: str = Field(alias="Investigation Number")
    title: str | None = Field(default=None, alias="Full Title")
    topic: str | None = Field(default=None, alias="Topic")
    # These fields can be strings (legacy/tests) or dicts (current API)
    product_group: str | dict[str, Any] | None = Field(
        default=None, alias="Product Group Code Description"
    )
    phase: str | dict[str, Any] | None = Field(default=None, alias="Phase Number")
    investigation_status: str | dict[str, Any] | None = Field(
        default=None, alias="Investigation Status"
    )
    investigation_type: str | dict[str, Any] | None = Field(
        default=None, alias="Investigation Type"
    )
    docket_number: str | None = Field(default=None, alias="Docket Number")
    start_date: str | None = Field(default=None, alias="Start Date")
    end_date: str | None = Field(default=None, alias="Investigation End Date")
    staff_contacts: list[dict[str, Any]] | None = Field(default=None, alias="Staff")
    participants: list[dict[str, Any]] | None = Field(default=None, alias="Participants")


class HtsSearchResult(BaseModel):
    hts_number: str | None = Field(default=None, alias="htsno")
    description: str | None = Field(default=None, alias="description")
    heading: str | None = Field(default=None, alias="heading")
    chapter: str | None = Field(default=None, alias="chapter")


class HtsExportResponse(BaseModel):
    entries: list[dict[str, Any]]
    raw: list[dict[str, Any]]
