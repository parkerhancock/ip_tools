"""Async API for USITC services.

Usage
-----
Preferred: use clients as context managers for proper resource cleanup::

    async with EdisClient() as client:
        investigations = await client.list_investigations()
        documents = await client.list_documents(investigation_number="337-TA-1234")

    async with DataWebClient() as client:
        report = await client.run_report(query)

One-shot convenience functions (create and close client automatically)::

    investigations = await edis_search_investigations()

Legacy: passing client= parameter (deprecated, will be removed in v1.0)::

    client = get_edis_client()
    investigations = await edis_search_investigations(client=client)
    await client.close()  # Manual cleanup required
"""

from __future__ import annotations

import warnings
from typing import Any

from .client import DataWebClient, EdisClient, HtsClient, IdsClient
from .models import (
    DataWebReport,
    DownloadedAttachment,
    EdisAttachment,
    EdisDocument,
    EdisInvestigation,
    HtsExportResponse,
    HtsSearchResult,
    IdsInvestigation,
    SavedQuerySummary,
)
from .resources import (
    DATAWEB_GUIDE_RESOURCE_URI,
    EDIS_TOKEN_RESOURCE_URI,
    HTS_RESOURCE_URI,
    IDS_RESOURCE_URI,
    get_dataweb_resource,
    get_edis_resource,
    get_hts_resource,
    get_ids_resource,
)

__all__ = [
    "EdisClient",
    "DataWebClient",
    "IdsClient",
    "HtsClient",
    "EdisInvestigation",
    "EdisDocument",
    "EdisAttachment",
    "DownloadedAttachment",
    "DataWebReport",
    "SavedQuerySummary",
    "IdsInvestigation",
    "HtsSearchResult",
    "HtsExportResponse",
    "get_edis_client",
    "get_dataweb_client",
    "get_ids_client",
    "get_hts_client",
    "edis_search_investigations",
    "edis_list_documents",
    "edis_list_attachments",
    "edis_download_attachment",
    "dataweb_run_report",
    "dataweb_list_saved_queries",
    "ids_list_investigations",
    "hts_search",
    "hts_export_range",
    "EDIS_TOKEN_RESOURCE_URI",
    "DATAWEB_GUIDE_RESOURCE_URI",
    "IDS_RESOURCE_URI",
    "HTS_RESOURCE_URI",
    "get_edis_resource",
    "get_dataweb_resource",
    "get_ids_resource",
    "get_hts_resource",
]


def get_edis_client() -> EdisClient:
    """Create an EdisClient. Prefer using as context manager."""
    return EdisClient()


def get_dataweb_client() -> DataWebClient:
    """Create a DataWebClient. Prefer using as context manager."""
    return DataWebClient()


def get_ids_client() -> IdsClient:
    """Create an IdsClient. Prefer using as context manager."""
    return IdsClient()


def get_hts_client() -> HtsClient:
    """Create an HtsClient. Prefer using as context manager."""
    return HtsClient()


def _warn_edis_deprecated() -> None:
    warnings.warn(
        "Passing client= is deprecated and will be removed in v1.0. "
        "Use 'async with EdisClient() as client:' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def _warn_dataweb_deprecated() -> None:
    warnings.warn(
        "Passing client= is deprecated and will be removed in v1.0. "
        "Use 'async with DataWebClient() as client:' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def _warn_ids_deprecated() -> None:
    warnings.warn(
        "Passing client= is deprecated and will be removed in v1.0. "
        "Use 'async with IdsClient() as client:' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def _warn_hts_deprecated() -> None:
    warnings.warn(
        "Passing client= is deprecated and will be removed in v1.0. "
        "Use 'async with HtsClient() as client:' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


async def edis_search_investigations(
    investigation_number: str | None = None,
    investigation_phase: str | None = None,
    investigation_type: str | None = None,
    investigation_status: str | None = None,
    page_number: int = 1,
    *,
    client: EdisClient | None = None,
) -> list[EdisInvestigation]:
    """Search EDIS investigations.

    The investigation_number and investigation_phase are passed as path segments
    (per EDIS API spec). Other filters are query parameters.

    If no client is provided, creates one internally and closes it after the request.
    """
    kwargs: dict[str, Any] = {
        "investigationType": investigation_type,
        "investigationStatus": investigation_status,
        "pageNumber": page_number,
    }

    if client is not None:
        _warn_edis_deprecated()
        return await client.list_investigations(
            investigation_number=investigation_number,
            investigation_phase=investigation_phase,
            **kwargs,
        )

    async with EdisClient() as cl:
        return await cl.list_investigations(
            investigation_number=investigation_number,
            investigation_phase=investigation_phase,
            **kwargs,
        )


async def edis_list_documents(
    investigation_number: str | None = None,
    document_type: str | None = None,
    page_number: int = 1,
    *,
    client: EdisClient | None = None,
) -> list[EdisDocument]:
    """List EDIS documents.

    If no client is provided, creates one internally and closes it after the request.
    """
    kwargs = {
        "investigationNumber": investigation_number,
        "documentType": document_type,
        "pageNumber": page_number,
    }

    if client is not None:
        _warn_edis_deprecated()
        return await client.list_documents(**kwargs)

    async with EdisClient() as cl:
        return await cl.list_documents(**kwargs)


async def edis_list_attachments(
    document_id: int,
    *,
    client: EdisClient | None = None,
) -> list[EdisAttachment]:
    """List attachments for an EDIS document.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_edis_deprecated()
        return await client.list_attachments(document_id)

    async with EdisClient() as cl:
        return await cl.list_attachments(document_id)


async def edis_download_attachment(
    document_id: int,
    attachment_id: int,
    *,
    client: EdisClient | None = None,
) -> DownloadedAttachment:
    """Download an EDIS attachment.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_edis_deprecated()
        return await client.download_attachment(
            document_id=document_id,
            attachment_id=attachment_id,
        )

    async with EdisClient() as cl:
        return await cl.download_attachment(
            document_id=document_id,
            attachment_id=attachment_id,
        )


async def dataweb_run_report(
    query: dict[str, Any],
    *,
    client: DataWebClient | None = None,
) -> DataWebReport:
    """Run a DataWeb report.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_dataweb_deprecated()
        return await client.run_report(query)

    async with DataWebClient() as cl:
        return await cl.run_report(query)


async def dataweb_list_saved_queries(
    *,
    client: DataWebClient | None = None,
) -> list[SavedQuerySummary]:
    """List saved DataWeb queries.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_dataweb_deprecated()
        return await client.list_saved_queries()

    async with DataWebClient() as cl:
        return await cl.list_saved_queries()


async def ids_list_investigations(
    *,
    client: IdsClient | None = None,
) -> list[IdsInvestigation]:
    """List IDS investigations.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_ids_deprecated()
        return await client.list_investigations()

    async with IdsClient() as cl:
        return await cl.list_investigations()


async def hts_search(
    keyword: str,
    *,
    client: HtsClient | None = None,
) -> list[HtsSearchResult]:
    """Search HTS codes.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_hts_deprecated()
        return await client.search(keyword)

    async with HtsClient() as cl:
        return await cl.search(keyword)


async def hts_export_range(
    from_code: str,
    to_code: str,
    format_: str = "JSON",
    styles: bool = True,
    *,
    client: HtsClient | None = None,
) -> HtsExportResponse:
    """Export HTS codes in a range.

    If no client is provided, creates one internally and closes it after the request.
    """
    if client is not None:
        _warn_hts_deprecated()
        return await client.export_range(from_code, to_code, format_, styles)

    async with HtsClient() as cl:
        return await cl.export_range(from_code, to_code, format_, styles)
