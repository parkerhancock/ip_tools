"""USPTO Open Data Portal MCP tools."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlparse

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from law_tools_core.mcp.downloads import register_source
from patent_client_agents.uspto_odp import PtabTrialsClient, UsptoOdpClient

uspto_mcp = FastMCP("USPTO")


# USPTO ODP URL fields that require API key auth — must be stripped from responses
_AUTH_URL_FIELDS = {"fileDownloadURI", "downloadURI", "downloadUrl", "fileLocationURI"}


def _dump(obj: object) -> object:
    """Serialize a Pydantic model and strip auth-required URLs."""
    if hasattr(obj, "model_dump"):
        data = obj.model_dump()  # type: ignore[union-attr]
        _strip_auth_urls(data)
        return data
    return obj


def _strip_auth_urls(data: object) -> None:
    """Recursively remove auth-required URL fields from nested dicts/lists."""
    if isinstance(data, dict):
        for key in _AUTH_URL_FIELDS & data.keys():
            del data[key]
        for v in data.values():
            _strip_auth_urls(v)
    elif isinstance(data, list):
        for item in data:
            _strip_auth_urls(item)


# ---------------------------------------------------------------------------
# Download fetchers
# ---------------------------------------------------------------------------


async def _fetch_application_document(path: str) -> tuple[bytes, str]:
    """Fetch a USPTO prosecution document. Path: ``{app_number}/documents/{doc_id}``."""
    parts = path.split("/")
    if len(parts) == 3 and parts[1] == "documents":
        app_number, doc_id = parts[0], parts[2]
    elif len(parts) == 2:
        app_number, doc_id = parts[0], parts[1]
    else:
        raise ValueError(f"Expected {{app}}/documents/{{doc_id}}, got: {path}")
    async with UsptoOdpClient() as client:
        pdf_bytes = await client.download_document(app_number, doc_id)
        return pdf_bytes, f"{app_number}_{doc_id}.pdf"


async def _fetch_ptab_document(path: str) -> tuple[bytes, str]:
    """Fetch a PTAB trial document PDF. Path: ``{document_identifier}``.

    Gets document metadata first to find fileDownloadURI, then fetches the
    PDF from that path.
    """
    doc_id = path.strip("/")
    async with PtabTrialsClient() as client:
        response = await client.get_document(doc_id)
        download_uri = None
        bag = getattr(response, "patentTrialDocumentDataBag", None) or []
        for entry in bag:
            dd = getattr(entry, "documentData", None)
            if dd and getattr(dd, "fileDownloadURI", None):
                download_uri = dd.fileDownloadURI
                break
            if getattr(entry, "fileDownloadURI", None):
                download_uri = entry.fileDownloadURI
                break
        if not download_uri:
            raise ValueError(f"No fileDownloadURI found for PTAB document {doc_id}")
        uri_path = urlparse(str(download_uri)).path
        pdf_bytes = await client.download_document_pdf(uri_path)
        return pdf_bytes, f"ptab_{doc_id}.pdf"


register_source("uspto/applications", _fetch_application_document, "application/pdf")
register_source("ptab/documents", _fetch_ptab_document, "application/pdf")


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------


@uspto_mcp.tool(annotations=READ_ONLY)
async def search_applications(
    query: Annotated[
        str,
        "Lucene-style query. Searchable fields include: "
        "applicationMetaData.inventionTitle, applicationMetaData.patentNumber, "
        "applicationMetaData.publicationNumber, applicationMetaData.filingDate, "
        "applicationMetaData.grantDate, applicationMetaData.cpcClassificationBag, "
        "applicationMetaData.examinerName, applicationMetaData.applicationTypeCategory "
        "(UTILITY/DESIGN/PLANT/REAEX). "
        "Example: 'applicationMetaData.inventionTitle:\"blockchain authentication\"'",
    ],
    limit: Annotated[int, "Maximum number of results to return"] = 25,
    offset: Annotated[int, "Result offset for pagination"] = 0,
) -> dict:
    """Search USPTO patent applications by metadata fields (title, CPC, dates, status).

    NOTE: This searches application metadata only — not claims or specification
    text. For full-text patent search (within claims, description, abstract),
    use search_patent_publications instead.
    """
    async with UsptoOdpClient() as client:
        result = await client.search_applications(query=query, limit=limit, offset=offset)
        return _dump(result)  # type: ignore[return-value]


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_application(
    application_number: Annotated[
        str,
        "USPTO application number (8+ digits). Examples: '16123456', '17654321'. "
        "NOT a patent number (like '10123456B2') or publication number "
        "(like 'US20230012345A1'). If you have a patent number, use "
        "get_patent_family to find the application number first.",
    ],
) -> dict:
    """Get application metadata: status, filing/grant dates, examiner, CPC, and title.

    Does NOT return patent text (claims, spec, abstract). For patent text,
    use get_patent_publication. For prosecution documents, use
    list_file_history.
    """
    async with UsptoOdpClient() as client:
        result = await client.get_application(application_number)
        return _dump(result)  # type: ignore[return-value]


@uspto_mcp.tool(annotations=READ_ONLY)
async def list_file_history(
    application_number: Annotated[
        str,
        "USPTO application number (8+ digits). Examples: '16123456'. "
        "NOT a patent number or publication number.",
    ],
) -> dict:
    """List prosecution file-history documents for an application.

    Returns each document with its identifier, code, description, date,
    direction (incoming/outgoing/internal), page count, and available
    formats (XML, PDF, MS_WORD). Pass the ``document_identifier`` to
    ``get_file_history_item`` to fetch the content.

    Key document codes: CLM (claims as filed/amended), SPEC (specification),
    ABST (abstract), CTFR/CTNF (office actions), REM (applicant remarks),
    NOA (notice of allowance), CTRS (restriction requirement), IDS
    (information disclosure statement).
    """
    async with UsptoOdpClient() as client:
        response = await client.get_documents(application_number)

    documents: list[dict[str, object]] = []
    for raw in response.model_dump().get("documents", []):
        formats = [
            opt.get("mimeTypeIdentifier")
            for opt in (raw.get("downloadOptionBag") or [])
            if opt.get("mimeTypeIdentifier")
        ]
        documents.append(
            {
                "document_identifier": raw.get("documentIdentifier"),
                "code": raw.get("documentCode"),
                "description": raw.get("documentCodeDescriptionText"),
                "date": raw.get("officialDate") or raw.get("documentDate"),
                "direction": raw.get("directionCategory"),
                "page_count": raw.get("pageCount"),
                "formats": formats,
            }
        )
    return {"application_number": application_number, "documents": documents}


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_file_history_item(
    application_number: Annotated[
        str,
        "USPTO application number (8+ digits). Examples: '16123456'.",
    ],
    document_identifier: Annotated[
        str,
        "Document identifier from list_file_history (e.g. 'IGBCPFXCPXXIFW3').",
    ],
    format: Annotated[
        str,
        "Content format. 'auto' (default): readable structured text — XML "
        "parsed when available, else PDF text layer, else Tesseract OCR for "
        "image-only PDFs. 'xml': raw ST.96 XML (raises if XML was not filed "
        "for this document). For PDFs of one or more documents, use "
        "``download_file_history`` instead (it handles n=1 as a raw PDF).",
    ] = "auto",
) -> dict:
    """Get the text content of a file-history document.

    Returns readable text regardless of how USPTO filed the document —
    agents do not need to pre-check format availability. Focused on
    *content* (structured text or XML); for PDF bytes, call
    ``download_file_history`` (with ``item_ids=[document_identifier]``
    for a single document, or a list for bulk).

    Call ``list_file_history`` first to discover valid
    ``document_identifier`` values for an application.
    """
    from law_tools_core.exceptions import NotFoundError, ValidationError
    from law_tools_core.filenames import file_history_item as _fh_name
    from patent_client_agents.uspto_odp.clients.applications import ApplicationsClient

    if format == "pdf":
        raise ValidationError(
            "format='pdf' was removed from get_file_history_item — use "
            "download_file_history(application_number, item_ids=[document_identifier]) "
            "to get a PDF download_url."
        )

    async with ApplicationsClient() as client:
        try:
            result = await client.get_document_content(
                application_number, document_identifier, format=format
            )
            if result.get("format") == "xml":
                result["filename"] = _fh_name(
                    application_number=application_number,
                    document_code=None,
                    mail_date=None,
                    document_identifier=document_identifier,
                    extension="xml",
                )
            return result
        except NotFoundError:
            response = await client.get_documents(application_number)
            sample = [
                {
                    "document_identifier": d.documentIdentifier,
                    "code": d.documentCode,
                    "description": d.documentCodeDescriptionText,
                }
                for d in response.documents[:20]
            ]
            raise NotFoundError(
                f"Document {document_identifier!r} not found in application "
                f"{application_number}. First {len(sample)} available documents: "
                f"{sample}. Use list_file_history for the complete list."
            ) from None


_FILE_HISTORY_BULK_CAP = 50


def _parse_iso_date(value: str | None, *, field_name: str):
    """Parse ``YYYY-MM-DD`` to a ``date`` or return ``None``. Raises ``ValidationError`` on bad input."""
    if not value:
        return None
    from datetime import date as _date

    from law_tools_core.exceptions import ValidationError

    try:
        return _date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be ISO date YYYY-MM-DD; got {value!r}") from exc


@uspto_mcp.tool(annotations=READ_ONLY)
async def download_file_history(
    application_number: Annotated[
        str,
        "USPTO application number (8+ digits). Examples: '16123456'.",
    ],
    item_ids: Annotated[
        list[str] | None,
        "Specific document_identifier values from list_file_history. "
        "None means 'all documents matching the other filters'.",
    ] = None,
    document_codes: Annotated[
        list[str] | None,
        "Filter to USPTO document type codes (e.g. ['CTNF', 'IDS', 'NOA']). "
        "See list_file_history for available codes in this application.",
    ] = None,
    after: Annotated[
        str | None,
        "Include only documents on or after this date (ISO YYYY-MM-DD).",
    ] = None,
    before: Annotated[
        str | None,
        "Include only documents on or before this date (ISO YYYY-MM-DD).",
    ] = None,
) -> dict:
    """Bulk-download file-history documents for a USPTO application.

    Returns a single zip of matching PDFs (or the raw PDF if exactly one
    matches) plus a manifest. Cap: 50 documents per call. Filters AND
    together; if more than 50 documents match, the call refuses and
    asks you to narrow.

    Use ``list_file_history`` to discover document_identifier values and
    document codes for an application.
    """
    from datetime import date as _date

    from law_tools_core.exceptions import ValidationError
    from law_tools_core.filenames import file_history_item as _fh_name
    from law_tools_core.mcp.downloads import BulkItem, download_bulk_response, fetch_with_cache

    after_d = _parse_iso_date(after, field_name="after")
    before_d = _parse_iso_date(before, field_name="before")

    async with UsptoOdpClient() as client:
        response = await client.get_documents(application_number)

    raw_docs = response.model_dump().get("documents") or []
    item_id_set = set(item_ids) if item_ids else None
    doc_code_set = set(document_codes) if document_codes else None

    matched: list[dict[str, object]] = []
    for raw in raw_docs:
        doc_id = raw.get("documentIdentifier")
        if not doc_id:
            continue
        if item_id_set is not None and doc_id not in item_id_set:
            continue
        code = raw.get("documentCode")
        if doc_code_set is not None and code not in doc_code_set:
            continue
        date_str = raw.get("officialDate") or raw.get("documentDate")
        if after_d or before_d:
            doc_d: _date | None
            try:
                doc_d = _date.fromisoformat((date_str or "")[:10]) if date_str else None
            except ValueError:
                doc_d = None
            if after_d and (doc_d is None or doc_d < after_d):
                continue
            if before_d and (doc_d is None or doc_d > before_d):
                continue
        matched.append(
            {
                "document_identifier": doc_id,
                "code": code,
                "date": date_str,
                "description": raw.get("documentCodeDescriptionText"),
                "direction": raw.get("directionCategory"),
                "page_count": raw.get("pageCount"),
            }
        )

    if not matched:
        raise ValidationError(
            f"No file-history documents in application {application_number} "
            f"match the given filters."
        )
    if len(matched) > _FILE_HISTORY_BULK_CAP:
        raise ValidationError(
            f"File history for {application_number} has {len(matched)} documents "
            f"matching the filters; max {_FILE_HISTORY_BULK_CAP} per call. "
            f"Narrow with item_ids, document_codes, after, or before — or page "
            f"manually using list_file_history."
        )

    bulk_items = [
        BulkItem(
            item_id=str(d["document_identifier"]),
            resource_path=(
                f"uspto/applications/{application_number}/documents/{d['document_identifier']}"
            ),
            metadata={
                "document_code": d.get("code"),
                "document_date": d.get("date"),
                "description": d.get("description"),
                "direction": d.get("direction"),
                "page_count": d.get("page_count"),
            },
        )
        for d in matched
    ]

    async def _fetcher(item: BulkItem) -> tuple[bytes, str]:
        # Reuse the registered uspto/applications fetcher via cache. Rename the
        # file with the human-friendly file_history_item convention so the zip
        # entry is self-describing without consulting the manifest.
        content, _ = await fetch_with_cache(item.resource_path)
        nice_name = _fh_name(
            application_number=application_number,
            document_code=str(item.metadata.get("document_code"))
            if item.metadata.get("document_code")
            else None,
            mail_date=str(item.metadata.get("document_date"))[:10]
            if item.metadata.get("document_date")
            else None,
            document_identifier=item.item_id,
            extension="pdf",
        )
        return content, nice_name

    return await download_bulk_response(
        bulk_items,
        _fetcher,
        container_label=f"{application_number}_file_history",
        container_metadata={
            "container": application_number,
            "application_number": application_number,
        },
        content_type_single="application/pdf",
    )


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_patent_family(
    identifier: Annotated[
        str,
        "The number to look up. Format depends on identifier_type.",
    ],
    identifier_type: Annotated[
        str,
        "Type of identifier: 'application' (e.g. '16123456'), "
        "'patent' (e.g. '10123456' or 'US10123456B2'), or "
        "'publication' (e.g. 'US20230012345A1'). "
        "Default: 'patent'.",
    ] = "patent",
) -> dict:
    """Get patent family relationships (continuations, divisionals, CIPs).

    Also useful for resolving a patent number to its application number.
    The response includes all family members with their application numbers,
    patent numbers, and relationship types.
    """
    async with UsptoOdpClient() as client:
        result = await client.get_family(identifier, identifier_type=identifier_type)
        return _dump(result)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_patent_assignment(
    application_number: Annotated[
        str,
        "USPTO application number (8+ digits). Examples: '16123456', '17654321'. "
        "NOT a patent number or publication number.",
    ],
) -> dict:
    """Get assignment and ownership transfer history for a patent application."""
    async with UsptoOdpClient() as client:
        result = await client.get_assignment(application_number)
        return _dump(result)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# PTAB (trials, appeals, interferences)
# ---------------------------------------------------------------------------


_PTAB_SEARCH_METHOD = {
    "proceeding": "search_trial_proceedings",
    "trial_decision": "search_trial_decisions",
    "trial_document": "search_trial_documents",
    "appeal_decision": "search_appeal_decisions",
    "interference_decision": "search_interference_decisions",
}

_PTAB_GET_METHOD = {
    "proceeding": ("get_trial_proceeding", "trial_number"),
    "trial_decision": ("get_trial_decision", "document_identifier"),
    "trial_document": ("get_trial_document", "document_identifier"),
    "appeal_decision": ("get_appeal_decision", "document_identifier"),
    "interference_decision": ("get_interference_decision", "document_identifier"),
}


@uspto_mcp.tool(annotations=READ_ONLY)
async def search_ptab(
    type: Annotated[
        str,
        "What to search. 'proceeding' — AIA trial proceedings (IPR/PGR/CBM/DER). "
        "'trial_decision' — decisions issued in AIA trials. "
        "'trial_document' — documents filed in AIA trials. "
        "'appeal_decision' — ex parte appeal decisions (different legal vehicle from "
        "AIA trials). 'interference_decision' — pre-AIA interference decisions.",
    ],
    query: Annotated[str, "Search query"],
    limit: Annotated[int, "Maximum number of results"] = 25,
    offset: Annotated[int, "Result offset for pagination"] = 0,
) -> dict:
    """Search PTAB records across trials, appeals, and interferences.

    Appeals and interferences are legally distinct tribunals from AIA
    trials — pick ``type`` deliberately. For trial-bound searches, use
    ``proceeding`` / ``trial_decision`` / ``trial_document``.
    """
    key = type.strip().lower()
    method_name = _PTAB_SEARCH_METHOD.get(key)
    if method_name is None:
        from law_tools_core.exceptions import ValidationError

        raise ValidationError(f"type must be one of {sorted(_PTAB_SEARCH_METHOD)}; got {type!r}")
    async with UsptoOdpClient() as client:
        method = getattr(client, method_name)
        result = await method(query=query, limit=limit, offset=offset)
        return _dump(result)  # type: ignore[return-value]


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_ptab(
    type: Annotated[
        str,
        "Record type to fetch. 'proceeding' — takes a trial number (e.g. "
        "'IPR2024-00001'). 'trial_decision' / 'trial_document' / "
        "'appeal_decision' / 'interference_decision' — take a document identifier "
        "from the corresponding search.",
    ],
    identifier: Annotated[
        str,
        "Trial number for 'proceeding'; document identifier for all other types.",
    ],
) -> dict:
    """Fetch a single PTAB record (proceeding, decision, or document) by identifier."""
    key = type.strip().lower()
    if key not in _PTAB_GET_METHOD:
        from law_tools_core.exceptions import ValidationError

        raise ValidationError(f"type must be one of {sorted(_PTAB_GET_METHOD)}; got {type!r}")
    method_name, _id_kind = _PTAB_GET_METHOD[key]
    async with UsptoOdpClient() as client:
        method = getattr(client, method_name)
        result = await method(identifier)
        return _dump(result)  # type: ignore[return-value]


@uspto_mcp.tool(annotations=READ_ONLY)
async def list_ptab_children(
    parent_type: Annotated[
        str,
        "What the ``parent_identifier`` refers to. 'trial' — an AIA trial number "
        "(e.g. 'IPR2024-00001'); lists decisions and/or documents. 'application' — "
        "a USPTO application number; lists ex parte appeal decisions for it. "
        "'interference' — an interference number; lists decisions.",
    ],
    parent_identifier: Annotated[str, "Trial number, application number, or interference number"],
    include: Annotated[
        str,
        "For parent_type='trial' only: 'decisions' (default), 'documents', or 'both'. "
        "Appeals and interferences only return decisions.",
    ] = "decisions",
) -> dict:
    """List PTAB children (decisions, documents) attached to a parent record.

    Use ``download_ptab_document`` to retrieve the PDF of any trial document.
    """
    from law_tools_core.exceptions import ValidationError

    pt = parent_type.strip().lower()
    inc = include.strip().lower()
    async with UsptoOdpClient() as client:
        if pt == "trial":
            if inc not in ("decisions", "documents", "both"):
                raise ValidationError(
                    f"include must be 'decisions', 'documents', or 'both' for trials; got {include!r}"
                )
            out: dict[str, object] = {"trial_number": parent_identifier}
            if inc in ("decisions", "both"):
                decisions = await client.get_trial_decisions_by_trial(parent_identifier)
                out["decisions"] = _dump(decisions)
            if inc in ("documents", "both"):
                documents = await client.get_trial_documents_by_trial(parent_identifier)
                out["documents"] = _dump(documents)
            return out
        if pt == "application":
            if inc not in ("decisions",):
                raise ValidationError("parent_type='application' only supports include='decisions'")
            result = await client.get_appeal_decisions_by_number(parent_identifier)
            return {"application_number": parent_identifier, "decisions": _dump(result)}
        if pt == "interference":
            if inc not in ("decisions",):
                raise ValidationError(
                    "parent_type='interference' only supports include='decisions'"
                )
            result = await client.get_interference_decisions_by_number(parent_identifier)
            return {"interference_number": parent_identifier, "decisions": _dump(result)}
        raise ValidationError(
            f"parent_type must be 'trial', 'application', or 'interference'; got {parent_type!r}"
        )


# ---------------------------------------------------------------------------
# PTAB bulk downloads (container-scoped)
# ---------------------------------------------------------------------------
#
# Single-document PTAB downloads were removed in favor of the container-bulk
# tools below. The ``ptab/documents/{id}`` fetcher registration above (see
# ``_fetch_ptab_document``) stays so any signed URLs minted before the
# removal still resolve from cache, and so the bulk tool's ``fetch_with_cache``
# path keeps working.


_PTAB_TRIAL_DOCUMENTS_CAP = 100
_PTAB_TRIAL_DECISIONS_CAP = 50
_PTAB_APPEAL_DECISIONS_CAP = 50
_PTAB_INTERFERENCE_DECISIONS_CAP = 50


def _ptab_parse_date(value: str | None, *, field_name: str):
    if not value:
        return None
    from datetime import date as _date

    from law_tools_core.exceptions import ValidationError

    try:
        return _date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be ISO date YYYY-MM-DD; got {value!r}") from exc


async def _ptab_download_pdf(file_download_uri: str) -> bytes:
    """Download a PTAB PDF given a ``fileDownloadURI`` from any list/get response."""
    async with PtabTrialsClient() as client:
        uri_path = urlparse(str(file_download_uri)).path
        return await client.download_document_pdf(uri_path)


async def _run_ptab_bulk(
    *,
    candidates: list[dict],
    container_label: str,
    container_metadata: dict,
    cap: int,
    container_kind: str,
) -> dict:
    """Shared bulk-download pipeline for the 4 PTAB tools.

    Each candidate dict must carry: ``item_id``, ``resource_path``,
    ``file_download_uri``, ``filename``, and any extra metadata for the
    manifest. Filtering (by item_ids / date) is done by the caller before
    this runs.
    """
    from law_tools_core.exceptions import ValidationError
    from law_tools_core.mcp.downloads import BulkItem, download_bulk_response, fetch_with_cache

    if not candidates:
        raise ValidationError(
            f"No PTAB {container_kind} match the given filters for {container_label!r}."
        )
    if len(candidates) > cap:
        raise ValidationError(
            f"PTAB {container_kind} for {container_label!r} has {len(candidates)} items "
            f"matching the filters; max {cap} per call. Narrow with item_ids or "
            f"date filters (after/before)."
        )

    # Fetch-internal hints (URI + target filename) live in a side dict keyed
    # by item_id so they don't pollute the BulkItem.metadata surfaced in the
    # manifest, and so they can't shadow kwargs like ``filename`` when the
    # n=1 short-circuit splats metadata into ``download_response``.
    _fetch_plan: dict[str, tuple[str, str]] = {}
    bulk_items = []
    _INTERNAL_KEYS = {"resource_path", "item_id", "filename", "file_download_uri"}
    for cand in candidates:
        manifest_metadata = {k: v for k, v in cand.items() if k not in _INTERNAL_KEYS}
        bulk_items.append(
            BulkItem(
                item_id=cand["item_id"],
                resource_path=cand["resource_path"],
                metadata=manifest_metadata,
            )
        )
        _fetch_plan[cand["item_id"]] = (cand["file_download_uri"], cand["filename"])

    async def _fetcher(item: BulkItem) -> tuple[bytes, str]:
        uri, filename = _fetch_plan[item.item_id]

        async def _inline() -> tuple[bytes, str]:
            return await _ptab_download_pdf(uri), filename

        return await fetch_with_cache(item.resource_path, fetcher=_inline)

    return await download_bulk_response(
        bulk_items,
        _fetcher,
        container_label=container_label,
        container_metadata=container_metadata,
        content_type_single="application/pdf",
    )


def _extract_trial_bag_entry(entry) -> dict | None:
    """Pull (doc_id, URI, metadata) out of a PtabTrialDocument or PtabTrialDecision entry."""
    dd = getattr(entry, "documentData", None)
    if not dd:
        return None
    doc_id = getattr(dd, "documentIdentifier", None)
    uri = getattr(dd, "fileDownloadURI", None) or getattr(dd, "downloadURI", None)
    if not doc_id or not uri:
        return None
    filing_date = getattr(dd, "documentFilingDate", None)
    decision = getattr(entry, "decisionData", None)
    if decision is not None and not filing_date:
        filing_date = getattr(decision, "decisionIssueDate", None)
    return {
        "item_id": str(doc_id),
        "file_download_uri": str(uri),
        "document_filing_date": filing_date,
        "document_title": getattr(dd, "documentTitleText", None)
        or getattr(dd, "documentName", None),
        "document_type": getattr(dd, "documentTypeDescriptionText", None),
        "document_number": getattr(dd, "documentNumber", None),
        "filing_party_category": getattr(dd, "filingPartyCategory", None),
        "decision_type": getattr(decision, "decisionTypeCategory", None) if decision else None,
    }


def _filter_by_date(
    candidates: list[dict],
    *,
    date_key: str,
    after,
    before,
) -> list[dict]:
    """Keep only candidates whose ``date_key`` value is within [after, before]."""
    if after is None and before is None:
        return candidates
    from datetime import date as _date

    out = []
    for c in candidates:
        raw = c.get(date_key)
        parsed: _date | None
        try:
            parsed = _date.fromisoformat((raw or "")[:10]) if raw else None
        except ValueError:
            parsed = None
        if after and (parsed is None or parsed < after):
            continue
        if before and (parsed is None or parsed > before):
            continue
        out.append(c)
    return out


@uspto_mcp.tool(annotations=READ_ONLY)
async def download_ptab_trial_documents(
    trial_number: Annotated[
        str,
        "AIA trial number (e.g. 'IPR2024-00001', 'PGR2023-00012', 'CBM2019-00001'). "
        "Every document filed by the parties in this trial is a candidate.",
    ],
    item_ids: Annotated[
        list[str] | None,
        "Specific document_identifier values from list_ptab_children(parent_type='trial', "
        "include='documents'). None means 'all documents matching the other filters'.",
    ] = None,
    after: Annotated[
        str | None,
        "Include only documents filed on or after this date (ISO YYYY-MM-DD).",
    ] = None,
    before: Annotated[
        str | None,
        "Include only documents filed on or before this date (ISO YYYY-MM-DD).",
    ] = None,
) -> dict:
    """Bulk-download party filings for one AIA trial as a single zip.

    Fetches everything the parties filed in the trial — petitions,
    responses, motions, replies, exhibits, depositions, notices — all of
    it. Cap: 100 documents per call. Big IPRs with many exhibits may
    need narrowing via ``item_ids`` (use ``list_ptab_children`` to
    enumerate) or date filters.

    For board-issued papers (institution decisions, FWDs, orders), use
    ``download_ptab_trial_decisions`` instead.
    """
    after_d = _ptab_parse_date(after, field_name="after")
    before_d = _ptab_parse_date(before, field_name="before")

    async with UsptoOdpClient() as client:
        response = await client.get_trial_documents_by_trial(trial_number)
    bag = getattr(response, "patentTrialDocumentDataBag", None) or []

    id_set = set(item_ids) if item_ids else None
    candidates: list[dict] = []
    for entry in bag:
        extracted = _extract_trial_bag_entry(entry)
        if extracted is None:
            continue
        if id_set and extracted["item_id"] not in id_set:
            continue
        extracted["resource_path"] = f"ptab/documents/{extracted['item_id']}"
        extracted["filename"] = _ptab_document_filename(
            proceeding_number=trial_number,
            entry=extracted,
        )
        candidates.append(extracted)

    candidates = _filter_by_date(
        candidates, date_key="document_filing_date", after=after_d, before=before_d
    )

    return await _run_ptab_bulk(
        candidates=candidates,
        container_label=f"{trial_number}_trial_documents",
        container_metadata={"container": trial_number, "trial_number": trial_number},
        cap=_PTAB_TRIAL_DOCUMENTS_CAP,
        container_kind="trial documents",
    )


@uspto_mcp.tool(annotations=READ_ONLY)
async def download_ptab_trial_decisions(
    trial_number: Annotated[
        str,
        "AIA trial number (e.g. 'IPR2024-00001'). Every decision issued "
        "by the board in this trial is a candidate.",
    ],
    item_ids: Annotated[list[str] | None, "Specific document_identifier values."] = None,
    after: Annotated[str | None, "Only decisions issued on or after (ISO YYYY-MM-DD)."] = None,
    before: Annotated[str | None, "Only decisions issued on or before (ISO YYYY-MM-DD)."] = None,
) -> dict:
    """Bulk-download board decisions for one AIA trial as a single zip.

    Institution decisions, scheduling orders, FWDs, board orders — papers
    issued by the board itself. Cap: 50 per call. For party filings
    (petitions, responses, exhibits) use ``download_ptab_trial_documents``.
    """
    after_d = _ptab_parse_date(after, field_name="after")
    before_d = _ptab_parse_date(before, field_name="before")

    async with UsptoOdpClient() as client:
        response = await client.get_trial_decisions_by_trial(trial_number)
    bag = getattr(response, "patentTrialDocumentDataBag", None) or []

    id_set = set(item_ids) if item_ids else None
    candidates: list[dict] = []
    for entry in bag:
        extracted = _extract_trial_bag_entry(entry)
        if extracted is None:
            continue
        if id_set and extracted["item_id"] not in id_set:
            continue
        extracted["resource_path"] = f"ptab/trial-decisions/{extracted['item_id']}"
        extracted["filename"] = _ptab_document_filename(
            proceeding_number=trial_number,
            entry=extracted,
            fallback_code=extracted.get("decision_type"),
        )
        candidates.append(extracted)

    candidates = _filter_by_date(
        candidates, date_key="document_filing_date", after=after_d, before=before_d
    )

    return await _run_ptab_bulk(
        candidates=candidates,
        container_label=f"{trial_number}_trial_decisions",
        container_metadata={"container": trial_number, "trial_number": trial_number},
        cap=_PTAB_TRIAL_DECISIONS_CAP,
        container_kind="trial decisions",
    )


@uspto_mcp.tool(annotations=READ_ONLY)
async def download_ptab_appeal_decisions(
    application_number: Annotated[
        str,
        "USPTO application number (8+ digits; appeals attach to applications, not trial "
        "numbers). Examples: '16123456'. Every ex parte appeal decision issued for this "
        "application is a candidate.",
    ],
    item_ids: Annotated[list[str] | None, "Specific document_identifier values."] = None,
    after: Annotated[str | None, "Only decisions issued on or after (ISO YYYY-MM-DD)."] = None,
    before: Annotated[str | None, "Only decisions issued on or before (ISO YYYY-MM-DD)."] = None,
) -> dict:
    """Bulk-download ex parte appeal decisions for one USPTO application.

    Appeals are a distinct vehicle from AIA trials. Cap: 50 per call.
    Use ``list_ptab_children(parent_type='application')`` to preview
    what's available.
    """
    after_d = _ptab_parse_date(after, field_name="after")
    before_d = _ptab_parse_date(before, field_name="before")

    async with UsptoOdpClient() as client:
        response = await client.get_appeal_decisions_by_number(application_number)
    bag = getattr(response, "patentAppealDataBag", None) or []

    id_set = set(item_ids) if item_ids else None
    candidates: list[dict] = []
    for entry in bag:
        dd = getattr(entry, "documentData", None)
        if not dd:
            continue
        doc_id = getattr(dd, "documentIdentifier", None)
        uri = getattr(dd, "fileDownloadURI", None) or getattr(dd, "downloadURI", None)
        if not doc_id or not uri:
            continue
        if id_set and doc_id not in id_set:
            continue
        decision = getattr(entry, "decisionData", None)
        candidates.append(
            {
                "item_id": str(doc_id),
                "file_download_uri": str(uri),
                "document_filing_date": getattr(dd, "documentFilingDate", None),
                "decision_issue_date": getattr(decision, "decisionIssueDate", None)
                if decision
                else None,
                "decision_type": getattr(decision, "decisionTypeCategory", None)
                if decision
                else None,
                "appeal_outcome": getattr(decision, "appealOutcomeCategory", None)
                if decision
                else None,
                "document_type": getattr(dd, "documentTypeDescriptionText", None),
                "document_name": getattr(dd, "documentName", None),
                "resource_path": f"ptab/appeal-decisions/{doc_id}",
                "filename": _ptab_decision_filename(
                    container=application_number,
                    doc_id=str(doc_id),
                    code=getattr(decision, "decisionTypeCategory", None) if decision else None,
                    date=getattr(decision, "decisionIssueDate", None)
                    if decision
                    else getattr(dd, "documentFilingDate", None),
                ),
            }
        )

    candidates = _filter_by_date(
        candidates, date_key="decision_issue_date", after=after_d, before=before_d
    )

    return await _run_ptab_bulk(
        candidates=candidates,
        container_label=f"{application_number}_appeal_decisions",
        container_metadata={
            "container": application_number,
            "application_number": application_number,
        },
        cap=_PTAB_APPEAL_DECISIONS_CAP,
        container_kind="appeal decisions",
    )


@uspto_mcp.tool(annotations=READ_ONLY)
async def download_ptab_interference_decisions(
    interference_number: Annotated[
        str,
        "Pre-AIA interference number. Every decision issued in this interference is a candidate.",
    ],
    item_ids: Annotated[list[str] | None, "Specific document_identifier values."] = None,
    after: Annotated[str | None, "Only decisions issued on or after (ISO YYYY-MM-DD)."] = None,
    before: Annotated[str | None, "Only decisions issued on or before (ISO YYYY-MM-DD)."] = None,
) -> dict:
    """Bulk-download decisions for one pre-AIA interference.

    Interferences are a legacy tribunal distinct from AIA trials and
    appeals. Cap: 50 per call.
    """
    after_d = _ptab_parse_date(after, field_name="after")
    before_d = _ptab_parse_date(before, field_name="before")

    async with UsptoOdpClient() as client:
        response = await client.get_interference_decisions_by_number(interference_number)
    bag = getattr(response, "patentInterferenceDataBag", None) or []

    id_set = set(item_ids) if item_ids else None
    candidates: list[dict] = []
    for entry in bag:
        dd = getattr(entry, "decisionDocumentData", None) or getattr(entry, "documentData", None)
        if not dd:
            continue
        doc_id = getattr(dd, "documentIdentifier", None)
        uri = getattr(dd, "fileDownloadURI", None)
        if not doc_id or not uri:
            continue
        if id_set and doc_id not in id_set:
            continue
        candidates.append(
            {
                "item_id": str(doc_id),
                "file_download_uri": str(uri),
                "decision_issue_date": getattr(dd, "decisionIssueDate", None),
                "decision_type": getattr(dd, "decisionTypeCategory", None),
                "interference_outcome": getattr(dd, "interferenceOutcomeCategory", None),
                "document_title": getattr(dd, "documentTitleText", None)
                or getattr(dd, "documentName", None),
                "resource_path": f"ptab/interference-decisions/{doc_id}",
                "filename": _ptab_decision_filename(
                    container=interference_number,
                    doc_id=str(doc_id),
                    code=getattr(dd, "decisionTypeCategory", None),
                    date=getattr(dd, "decisionIssueDate", None),
                ),
            }
        )

    candidates = _filter_by_date(
        candidates, date_key="decision_issue_date", after=after_d, before=before_d
    )

    return await _run_ptab_bulk(
        candidates=candidates,
        container_label=f"{interference_number}_interference_decisions",
        container_metadata={
            "container": interference_number,
            "interference_number": interference_number,
        },
        cap=_PTAB_INTERFERENCE_DECISIONS_CAP,
        container_kind="interference decisions",
    )


def _ptab_document_filename(
    *,
    proceeding_number: str,
    entry: dict,
    fallback_code: str | None = None,
) -> str:
    """Build a filename for a PTAB trial doc/decision via the shared ptab_document helper."""
    from law_tools_core.filenames import ptab_document as _ptab_name

    return _ptab_name(
        proceeding_number=proceeding_number,
        filing_date=entry.get("document_filing_date"),
        document_code=entry.get("document_type") or fallback_code,
        document_identifier=entry["item_id"],
    )


def _ptab_decision_filename(
    *,
    container: str,
    doc_id: str,
    code: str | None,
    date: str | None,
) -> str:
    """Build a filename for an appeal/interference decision."""
    from law_tools_core.filenames import ptab_document as _ptab_name

    return _ptab_name(
        proceeding_number=container,
        filing_date=date,
        document_code=code,
        document_identifier=doc_id,
    )


# ---------------------------------------------------------------------------
# Petitions
# ---------------------------------------------------------------------------


@uspto_mcp.tool(annotations=READ_ONLY)
async def search_petitions(
    query: Annotated[str, "Search query for petition decisions"],
    limit: Annotated[int, "Maximum number of results"] = 25,
    offset: Annotated[int, "Result offset for pagination"] = 0,
) -> dict:
    """Search USPTO petition decisions."""
    async with UsptoOdpClient() as client:
        result = await client.search_petitions(q=query, limit=limit, offset=offset)
        return _dump(result)  # type: ignore[return-value]


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_petition(
    petition_id: Annotated[str, "Petition decision record identifier"],
) -> dict:
    """Get details for a specific petition decision."""
    async with UsptoOdpClient() as client:
        result = await client.get_petition(petition_id)
        return _dump(result)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Bulk Data
# ---------------------------------------------------------------------------


@uspto_mcp.tool(annotations=READ_ONLY)
async def search_bulk_datasets(
    query: Annotated[str, "Search query for bulk data products"],
) -> dict:
    """Search available USPTO bulk data products."""
    async with UsptoOdpClient() as client:
        result = await client.search_bulk_datasets(query=query)
        return _dump(result)  # type: ignore[return-value]


@uspto_mcp.tool(annotations=READ_ONLY)
async def get_bulk_dataset(
    product_id: Annotated[str, "Bulk data product identifier"],
) -> dict:
    """Get details and file listing for a specific bulk data product."""
    async with UsptoOdpClient() as client:
        result = await client.get_bulk_dataset_product(product_id)
        return _dump(result)  # type: ignore[return-value]
