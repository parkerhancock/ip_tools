"""USITC MCP tools (EDIS investigations + documents, DataWeb, HTS, IDS).

Section 337 patent investigations are the IP-relevant slice; HTS and IDS
listings round out the ITC's public surface. EDIS uses
``USITC_EDIS_TOKEN``; DataWeb uses ``USITC_DATAWEB_TOKEN``; HTS and IDS
require no auth.
"""

from __future__ import annotations

import asyncio
import base64
from datetime import date as _date
from pathlib import PurePosixPath
from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.exceptions import ValidationError
from law_tools_core.filenames import usitc_attachment as _usitc_name
from law_tools_core.mcp import (
    BulkItem,
    download_bulk_response,
    download_response,
    fetch_with_cache,
    register_source,
)
from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.usitc import (
    DataWebClient,
    EdisClient,
    EdisDocument,
    HtsClient,
    IdsClient,
)
from patent_client_agents.usitc.client import build_dataweb_query

usitc_mcp = FastMCP("USITC")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


def _parse_iso_date(value: str | None, *, field_name: str) -> _date | None:
    if not value:
        return None
    try:
        return _date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be ISO date YYYY-MM-DD; got {value!r}") from exc


# ---------------------------------------------------------------------------
# Download fetcher (registered on import)
# ---------------------------------------------------------------------------


async def _fetch_usitc_attachment(path: str) -> tuple[bytes, str]:
    """Fetch a USITC EDIS attachment.

    Path format: ``{document_id}/attachments/{attachment_id}`` (remainder
    after stripping the ``usitc/documents/`` prefix).
    """
    parts = path.split("/")
    if len(parts) == 3 and parts[1] == "attachments":
        document_id, attachment_id = int(parts[0]), int(parts[2])
    elif len(parts) == 2:
        document_id, attachment_id = int(parts[0]), int(parts[1])
    else:
        raise ValueError(f"Expected {{doc_id}}/attachments/{{att_id}}, got: {path}")

    async with EdisClient() as client:
        result = await client.download_attachment(document_id, attachment_id)
        content = base64.b64decode(result.content_base64)
        filename = result.filename or f"usitc_{document_id}_{attachment_id}.pdf"
        return content, filename


register_source("usitc/documents", _fetch_usitc_attachment, "application/pdf")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clean_edis_document(doc: object) -> dict:
    """Dump an EdisDocument and remove upstream URLs that require EDIS auth."""
    item = _dump(doc)
    # attachment_list_uri points to edis.usitc.gov and requires a token —
    # agents should use list_usitc_attachments(document_id=...) instead
    if isinstance(item, dict):
        item.pop("attachment_list_uri", None)
    return item  # type: ignore[return-value]


def _parse_edis_date(date_str: str | None) -> str | None:
    """Extract YYYY-MM-DD from EDIS date strings.

    Handles both '2005-01-25 00:00:00.0' and '2024/05/16 00:00:00' formats.
    """
    if not date_str:
        return None
    if len(date_str) < 10:
        return None
    return date_str[:10].replace("/", "-")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@usitc_mcp.tool(annotations=READ_ONLY)
async def search_usitc_investigations(
    investigation_number: Annotated[
        str | None,
        "Investigation number (e.g. '337-1234'). "
        "Used as path segment per EDIS API — use EDIS format without 'TA-' prefix.",
    ] = None,
    phase: Annotated[
        str | None, "Phase filter (e.g. 'Violation', 'Preliminary', 'Final', 'Review2')"
    ] = None,
    investigation_type: Annotated[
        str | None,
        "Type filter (e.g. 'Sec 337', 'Import Injury', "
        "'Industry and Economic Analysis', 'Tariff Affairs & Trade Agreements')",
    ] = None,
    status: Annotated[
        str | None, "Status filter: 'PreInstitution', 'Active', 'Inactive', or 'Cancelled'"
    ] = None,
) -> dict:
    """Search USITC investigations via EDIS.

    Filter by investigation number (path lookup), phase, type, or status.
    Returns investigation number, title, phase, status, type, and docket number.
    """
    kwargs: dict = {}
    if investigation_type:
        kwargs["investigationType"] = investigation_type
    if status:
        kwargs["investigationStatus"] = status

    async with EdisClient() as client:
        result = await client.list_investigations(
            investigation_number=investigation_number,
            investigation_phase=phase,
            **kwargs,
        )
        return {"results": [_dump(r) for r in result]}


@usitc_mcp.tool(annotations=READ_ONLY)
async def search_usitc_documents(
    investigation_number: Annotated[
        str | None,
        "Investigation number in EDIS format (e.g. '337-1234'). Partial numbers allowed.",
    ] = None,
    investigation_phase: Annotated[
        str | None, "Phase filter (e.g. 'Violation', 'Final', 'Review2')"
    ] = None,
    document_type: Annotated[
        str | None,
        "Document type (e.g. 'Motion', 'Order', 'Notice', 'Brief Filed With ALJ'). "
        "Must be complete string — partial matches not allowed.",
    ] = None,
    firm_org: Annotated[
        str | None,
        "Firm/organization name. Each word is treated as an OR search.",
    ] = None,
    security_level: Annotated[
        str | None, "Security level filter: 'Public', 'Confidential', or 'Limited'"
    ] = None,
    date_from: Annotated[
        str | None,
        "Filter documents on or after this date (YYYY-MM-DD). "
        "Triggers server-side pagination through all results.",
    ] = None,
    date_to: Annotated[
        str | None,
        "Filter documents on or before this date (YYYY-MM-DD). "
        "Triggers server-side pagination through all results.",
    ] = None,
    page_number: Annotated[
        int,
        "Page number (100 results per page). "
        "If 'has_more' is true in the response, increment to get the next page.",
    ] = 1,
) -> dict:
    """Search USITC EDIS documents.

    Returns document ID, type, title, security level, filing party, date,
    firm, and investigation context. Use investigation_number to scope to
    a specific investigation.

    Returns up to 100 results per page. Check 'has_more' in the response
    and increment page_number to paginate. Works with or without date
    filters.

    When date_from or date_to is set, the server fetches all matching
    documents from EDIS (up to 3000) and filters by document_date, then
    returns the requested page of filtered results.
    """
    kwargs: dict = {}
    if investigation_number:
        kwargs["investigationNumber"] = investigation_number
    if investigation_phase:
        kwargs["investigationPhase"] = investigation_phase
    if document_type:
        kwargs["documentType"] = document_type
    if firm_org:
        kwargs["firmOrg"] = firm_org
    if security_level:
        kwargs["securityLevel"] = security_level

    use_date_filter = date_from is not None or date_to is not None
    page_size = 100

    if not use_date_filter:
        kwargs["pageNumber"] = page_number
        async with EdisClient() as client:
            result = await client.list_documents(**kwargs)
            return {
                "results": [_clean_edis_document(r) for r in result],
                "page": page_number,
                "has_more": len(result) >= page_size,
            }

    # Server-side: fetch all pages from EDIS, filter by date, then paginate
    max_pages = 30
    all_docs: list = []
    async with EdisClient() as client:
        for api_page in range(1, max_pages + 1):
            kwargs["pageNumber"] = api_page
            batch = await client.list_documents(**kwargs)
            if not batch:
                break
            all_docs.extend(batch)

    filtered = []
    for doc in all_docs:
        doc_date = _parse_edis_date(doc.document_date)
        if doc_date is None:
            continue
        if date_from and doc_date < date_from:
            continue
        if date_to and doc_date > date_to:
            continue
        filtered.append(doc)

    start = (page_number - 1) * page_size
    page_results = filtered[start : start + page_size]

    return {
        "results": [_clean_edis_document(r) for r in page_results],
        "page": page_number,
        "has_more": start + page_size < len(filtered),
        "total_matched": len(filtered),
    }


@usitc_mcp.tool(annotations=READ_ONLY)
async def search_hts_tariffs(
    query: Annotated[str, "Keyword to search HTS tariff codes"],
) -> dict:
    """Search USITC Harmonized Tariff Schedule by keyword."""
    async with HtsClient() as client:
        results = await client.search(keyword=query)
        return {"results": [_dump(r) for r in results]}


@usitc_mcp.tool(annotations=READ_ONLY)
async def run_dataweb_report(
    trade_type: Annotated[
        str,
        "Trade type: 'Import', 'Export', 'GenImp', 'TotExp', 'Balance', 'ForeignExp', 'ImpExp'",
    ] = "Import",
    classification: Annotated[
        str,
        "Classification system: 'HTS', 'SITC', 'NAIC', 'SIC', 'QUICK', 'EXPERT'",
    ] = "HTS",
    years: Annotated[
        str,
        "Comma-separated years, e.g. '2023,2024'. Defaults to '2024'.",
    ] = "2024",
    data_metrics: Annotated[
        str,
        "Comma-separated metrics: 'CONS_CUSTOMS_VALUE', 'CONS_FIR_UNIT_QUANT', 'CONS_QUANTITY_2'. "
        "Defaults to 'CONS_CUSTOMS_VALUE'.",
    ] = "CONS_CUSTOMS_VALUE",
    commodities: Annotated[
        str | None,
        "Comma-separated commodity codes to filter (e.g. '8542,8541'). None = all commodities.",
    ] = None,
    granularity: Annotated[
        str,
        "HTS digit level: '2', '4', '6', '8', '10'. Default '2'.",
    ] = "2",
    aggregate_countries: Annotated[
        bool,
        "If true, aggregate all countries. If false, break out by country.",
    ] = True,
    aggregate_commodities: Annotated[
        bool,
        "If true, aggregate commodities. If false, break out by commodity code.",
    ] = True,
    scale: Annotated[
        str,
        "Value scale: '1' (actual dollars), '1000' (thousands), '1000000' (millions).",
    ] = "1",
    timeline: Annotated[
        str,
        "Time aggregation: 'Annual' or 'Monthly'.",
    ] = "Annual",
) -> dict:
    """Run a USITC DataWeb trade data report.

    Query US import/export trade statistics by commodity, country, and time period.
    Returns tabular data with column headers and row values.
    Requires USITC_DATAWEB_TOKEN environment variable.
    """
    year_list = [y.strip() for y in years.split(",")]
    metric_list = [m.strip() for m in data_metrics.split(",")]
    commodity_list = [c.strip() for c in commodities.split(",")] if commodities else None

    query = build_dataweb_query(
        trade_type=trade_type,
        classification=classification,
        years=year_list,
        timeline=timeline,
        data_metrics=metric_list,
        scale=scale,
        commodities=commodity_list,
        granularity=granularity,
        aggregate_countries=aggregate_countries,
        aggregate_commodities=aggregate_commodities,
    )

    async with DataWebClient() as client:
        result = await client.run_report(query)
        return _dump(result)  # type: ignore[return-value]


@usitc_mcp.tool(annotations=READ_ONLY)
async def list_usitc_attachments(
    document_id: Annotated[int, "EDIS document ID to list attachments for"],
) -> dict:
    """List attachments for a USITC EDIS document.

    Use download_usitc_attachment to download a specific attachment.
    """
    async with EdisClient() as client:
        results = await client.list_attachments(document_id)
        items = []
        for att in results:
            item = _dump(att)
            if isinstance(item, dict):
                item.pop("download_uri", None)
            items.append(item)
        return {"results": items}


_USITC_BULK_CAP = 25
_USITC_PAGE_LIMIT = 50  # safety: don't walk more than 50 pages of doc listings


@usitc_mcp.tool(annotations=READ_ONLY)
async def download_usitc_investigation_documents(
    investigation_number: Annotated[
        str,
        "USITC EDIS investigation number (e.g. '337-TA-1234'). Every "
        "attachment for every document in this investigation is a candidate.",
    ],
    item_ids: Annotated[
        list[str] | None,
        "Specific items keyed as '{document_id}/attachments/{attachment_id}' "
        "(matches the canonical EDIS path). None means 'all attachments matching "
        "the other filters'.",
    ] = None,
    document_types: Annotated[
        list[str] | None,
        "Filter to these EDIS document types (e.g. ['Motion', 'Order', "
        "'Brief Filed With ALJ']). Must match exactly.",
    ] = None,
    after: Annotated[
        str | None,
        "Include only documents officially received on or after this date (ISO YYYY-MM-DD).",
    ] = None,
    before: Annotated[
        str | None,
        "Include only documents officially received on or before this date (ISO YYYY-MM-DD).",
    ] = None,
) -> dict:
    """Bulk-download USITC EDIS attachments for one investigation.

    Two-level enumeration: pages through every document in the investigation,
    then lists each document's attachments. Cap: 25 attachments per call
    (USITC PDFs are routinely huge — exhibits often hundreds of MB each).

    The cap applies to *attachments*, not documents — a single EDIS
    document can carry multiple PDFs. Narrow with ``item_ids``,
    ``document_types``, or date range to fit under the cap. Use
    ``search_usitc_documents`` and ``list_usitc_attachments`` to preview.
    """
    after_d = _parse_iso_date(after, field_name="after")
    before_d = _parse_iso_date(before, field_name="before")
    type_set = set(document_types) if document_types else None
    id_set = set(item_ids) if item_ids else None

    # Fast path: when the caller already knows the exact attachments,
    # skip the full per-investigation page walk (~60s for 337-1380's
    # 600 docs against a slow EDIS day) and just hand the explicit IDs
    # straight to the bulk-download fetcher.
    if id_set:
        bulk_items_fast: list[BulkItem] = []
        for item in id_set:
            try:
                doc_part, _attachments_kw, att_part = item.split("/", 2)
                doc_id = int(doc_part)
                att_id = int(att_part)
            except (ValueError, AttributeError):
                raise ValidationError(
                    f"item_ids entries must look like '<doc_id>/attachments/<att_id>'; got {item!r}"
                ) from None
            bulk_items_fast.append(
                BulkItem(
                    item_id=item,
                    resource_path=f"usitc/documents/{item}",
                    metadata={
                        "document_id": doc_id,
                        "attachment_id": att_id,
                        "investigation_number": investigation_number,
                    },
                )
            )
        if len(bulk_items_fast) > _USITC_BULK_CAP:
            raise ValidationError(
                f"item_ids has {len(bulk_items_fast)} entries; max {_USITC_BULK_CAP} per call."
            )

        async def _fetcher_fast(item: BulkItem) -> tuple[bytes, str]:
            return await fetch_with_cache(item.resource_path)

        return await download_bulk_response(
            bulk_items_fast,
            _fetcher_fast,
            container_label=f"{investigation_number}_documents",
            container_metadata={
                "container": investigation_number,
                "investigation_number": investigation_number,
            },
            content_type_single="application/pdf",
        )

    # 1. Page through documents for the investigation. EDIS doesn't return a
    # total count — walk pages in parallel batches and stop at the first
    # empty page.
    documents: list[EdisDocument] = []
    async with EdisClient() as client:
        page_batch = 8
        page = 1
        while page <= _USITC_PAGE_LIMIT:
            stop = min(page + page_batch, _USITC_PAGE_LIMIT + 1)
            batches = await asyncio.gather(
                *(
                    client.list_documents(investigationNumber=investigation_number, pageNumber=p)
                    for p in range(page, stop)
                )
            )
            empty_seen = False
            for b in batches:
                if not b:
                    empty_seen = True
                    break
                documents.extend(b)
            if empty_seen:
                break
            page = stop

        # 2. Filter docs by type/date BEFORE listing attachments — every
        # attachment-list call is a separate HTTP round trip.
        def _doc_passes(doc: EdisDocument) -> bool:
            if type_set and doc.document_type not in type_set:
                return False
            doc_date = _parse_edis_date(doc.official_received_date or doc.document_date)
            if after_d or before_d:
                try:
                    parsed = _date.fromisoformat(doc_date) if doc_date else None
                except ValueError:
                    parsed = None
                if after_d and (parsed is None or parsed < after_d):
                    return False
                if before_d and (parsed is None or parsed > before_d):
                    return False
            return True

        filtered_docs = [d for d in documents if _doc_passes(d)]

        # 3. Concurrent attachment listing — 20 in flight is enough to
        # absorb EDIS latency without tripping rate limits in practice.
        sem = asyncio.Semaphore(20)

        async def _list(doc):
            async with sem:
                atts = await client.list_attachments(doc.id)
                return doc, atts

        listings = await asyncio.gather(*(_list(d) for d in filtered_docs))

        candidates: list[dict] = []
        for doc, attachments in listings:
            doc_date = _parse_edis_date(doc.official_received_date or doc.document_date)
            for att in attachments:
                item_id = f"{doc.id}/attachments/{att.id}"
                if id_set and item_id not in id_set:
                    continue
                candidates.append(
                    {
                        "item_id": item_id,
                        "document_id": doc.id,
                        "attachment_id": att.id,
                        "document_type": doc.document_type,
                        "document_title": doc.title,
                        "document_date": doc_date,
                        "firm_organization": doc.firm_organization,
                        "filed_by": doc.filed_by,
                        "attachment_title": att.title,
                        "page_count": att.page_count,
                        "file_size": att.file_size,
                        "original_file_name": att.original_file_name,
                    }
                )

    if not candidates:
        raise ValidationError(
            f"No USITC attachments in investigation {investigation_number} match the given filters."
        )
    if len(candidates) > _USITC_BULK_CAP:
        raise ValidationError(
            f"Investigation {investigation_number} has {len(candidates)} attachments "
            f"matching the filters; max {_USITC_BULK_CAP} per call. Narrow with "
            f"item_ids, document_types, or date range — or paginate manually with "
            f"list_usitc_attachments."
        )

    bulk_items = [
        BulkItem(
            item_id=c["item_id"],
            resource_path=f"usitc/documents/{c['item_id']}",
            metadata={k: v for k, v in c.items() if k != "item_id"},
        )
        for c in candidates
    ]

    async def _fetcher(item: BulkItem) -> tuple[bytes, str]:
        return await fetch_with_cache(item.resource_path)

    return await download_bulk_response(
        bulk_items,
        _fetcher,
        container_label=f"{investigation_number}_documents",
        container_metadata={
            "container": investigation_number,
            "investigation_number": investigation_number,
        },
        content_type_single="application/pdf",
    )


@usitc_mcp.tool(annotations=READ_ONLY)
async def download_usitc_attachment(
    document_id: Annotated[int, "EDIS document ID"],
    attachment_id: Annotated[int, "EDIS attachment ID"],
) -> dict:
    """Download a USITC EDIS attachment.

    Returns a signed `download_url` (or `file_path` in local stdio mode) plus
    `filename`, `content_type`, `size_bytes`, `document_id`, `attachment_id`.
    """
    async with EdisClient() as client:
        result = await client.download_attachment(document_id, attachment_id)
        ext = (PurePosixPath(result.filename or "").suffix.lstrip(".") or "pdf").lower()
        filename = _usitc_name(
            document_id=document_id,
            attachment_id=attachment_id,
            extension=ext,
        )
        content = base64.b64decode(result.content_base64)
        return await download_response(
            f"usitc/documents/{document_id}/attachments/{attachment_id}",
            content,
            filename=filename,
            content_type=result.content_type or "application/pdf",
            document_id=document_id,
            attachment_id=attachment_id,
        )


@usitc_mcp.tool(annotations=READ_ONLY)
async def list_ids_investigations(
    limit: Annotated[
        int, "Max records to return (default 200; 4000+ exist, full payload exceeds MCP budget)"
    ] = 200,
    offset: Annotated[int, "Records to skip for pagination"] = 0,
    investigation_number_contains: Annotated[
        str | None, "Filter to investigations whose number contains this substring (e.g. '337-1')"
    ] = None,
    title_contains: Annotated[
        str | None,
        "Filter to investigations whose title contains this substring (case-insensitive)",
    ] = None,
    include_parties: Annotated[
        bool,
        "Include participants/staff arrays. Off by default — they're ~85% of payload size.",
    ] = False,
) -> dict:
    """List USITC IDS (Intellectual Property) investigations.

    Upstream returns ~4000 records in a single 11 MB payload. By default
    the tool drops ``participants``/``staff_contacts`` (the bulk of that
    payload) and returns the first ``limit`` records. ``total`` reports
    the unfiltered upstream size so callers can paginate or refine.
    """
    async with IdsClient() as client:
        results = await client.list_investigations()

    if investigation_number_contains:
        needle = investigation_number_contains
        results = [r for r in results if needle in (r.investigation_number or "")]
    if title_contains:
        needle = title_contains.lower()
        results = [r for r in results if needle in (r.title or "").lower()]

    total = len(results)
    page = results[offset : offset + limit]

    exclude = None if include_parties else {"participants", "staff_contacts"}
    items = [r.model_dump(exclude=exclude) for r in page]
    return {"results": items, "total": total, "offset": offset, "limit": limit}
