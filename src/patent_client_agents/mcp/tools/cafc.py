"""Federal Circuit (CAFC) MCP tools.

Search opinions, classify as patent cases, and serve opinion PDFs via
the shared ``pca://cafc/...`` download channel.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.filenames import cafc_opinion as _cafc_name
from law_tools_core.mcp import download_response, register_source
from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.cafc import CAFCClient, PatentClassifier

cafc_mcp = FastMCP("CAFC")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


# ---------------------------------------------------------------------------
# Download fetcher (registered on import)
# ---------------------------------------------------------------------------


async def _fetch_cafc_opinion(path: str) -> tuple[bytes, str]:
    """Fetch a CAFC opinion PDF. Path: ``{appeal_number}``."""
    appeal_number = path.strip("/")
    async with CAFCClient() as client:
        opinions = await client.search(query=appeal_number, max_results=20)
        match = None
        for o in opinions:
            if o.appeal_number and appeal_number in o.appeal_number:
                match = o
                break
        if match is None:
            raise ValueError(f"No CAFC opinion found for {appeal_number}")
        pdf_bytes = await client.download_pdf(match)
        return pdf_bytes, f"cafc_{appeal_number}.pdf"


register_source("cafc/opinions", _fetch_cafc_opinion, "application/pdf")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@cafc_mcp.tool(annotations=READ_ONLY)
async def search_cafc_opinions(
    query: Annotated[str | None, "Search text to filter CAFC opinions"] = None,
    patent_only: Annotated[bool, "Only return patent-related opinions"] = False,
    limit: Annotated[int, "Maximum number of results"] = 25,
) -> dict:
    """Search Federal Circuit (CAFC) opinions.

    Results include pdf_url for each opinion (public URL).
    Use download_cafc_pdf to download a specific opinion.
    """
    async with CAFCClient() as client:
        # Pass query through to the upstream DataTables search field.
        # Filtering client-side over a paginated fetch effectively
        # filtered only the most recent ``limit`` rows and almost always
        # returned 0 hits — the upstream search is what actually finds
        # matches across the full corpus.
        opinions = await client.search(query=query, max_results=limit)
        if patent_only:
            classifier = PatentClassifier()
            opinions = [o for o in opinions if classifier.classify(o.case_name)[0]]
        return {"results": [_dump(o) for o in opinions]}


@cafc_mcp.tool(annotations=READ_ONLY)
async def search_cafc_patent_opinions(
    date_from: Annotated[str | None, "Start date (YYYY-MM-DD) to filter opinions"] = None,
    date_to: Annotated[str | None, "End date (YYYY-MM-DD) to filter opinions"] = None,
    max_results: Annotated[int, "Maximum number of results"] = 25,
) -> dict:
    """Search CAFC opinions specifically related to patent cases (PTO, DCT, ITC, CFC origins).

    Results include pdf_url for each opinion (public URL).
    Use download_cafc_pdf to download a specific opinion PDF.
    """
    from datetime import date as date_type

    async with CAFCClient() as client:
        kwargs: dict = {"max_results": max_results}
        if date_from:
            kwargs["date_from"] = date_type.fromisoformat(date_from)
        if date_to:
            kwargs["date_to"] = date_type.fromisoformat(date_to)
        opinions = await client.search_patent_opinions(**kwargs)
        return {"results": [_dump(o) for o in opinions]}


@cafc_mcp.tool(annotations=READ_ONLY)
async def download_cafc_pdf(
    appeal_number: Annotated[str, "CAFC appeal number (e.g. '2023-1234')"],
) -> dict:
    """Download a CAFC opinion PDF by appeal number.

    Returns a signed `download_url` (or `file_path` in local stdio mode) plus
    `filename`, `content_type`, `size_bytes`, `appeal_number`, `case_name`.
    """
    async with CAFCClient() as client:
        opinions = await client.search(query=appeal_number, max_results=20)
        match = None
        for o in opinions:
            if o.appeal_number and appeal_number in o.appeal_number:
                match = o
                break
        if match is None:
            raise ValueError(f"No CAFC opinion found for appeal number {appeal_number}")
        pdf_bytes = await client.download_pdf(match)

        native = PurePosixPath(match.file_path or "").name if match.file_path else ""
        if native.lower().endswith(".pdf"):
            filename = native
        else:
            filename = _cafc_name(
                appeal_number=match.appeal_number or appeal_number,
                opinion_type=(
                    "NONPRECEDENTIAL"
                    if (match.precedential_status or "").lower().startswith("nonpreced")
                    else match.document_type or "OPINION"
                ),
                date=(
                    f"{match.release_date.month}-{match.release_date.day}-{match.release_date.year}"
                    if match.release_date
                    else None
                ),
            )
        return await download_response(
            f"cafc/opinions/{appeal_number}",
            pdf_bytes,
            filename=filename,
            content_type="application/pdf",
            appeal_number=appeal_number,
            case_name=match.case_name,
        )
