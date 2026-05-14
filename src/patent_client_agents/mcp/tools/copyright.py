"""US Copyright Office MCP tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.copyright import CopyrightClient

copyright_mcp = FastMCP("Copyright")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


@copyright_mcp.tool(annotations=READ_ONLY)
async def search_copyright(
    query: Annotated[str, "Search query (title, name, keyword, registration number)"],
    field: Annotated[
        str, "Field to search: 'keyword' (all fields), 'title', or 'name'"
    ] = "keyword",
    page: Annotated[int, "Page number (1-based)"] = 1,
    page_size: Annotated[int, "Results per page (default 10, max ~50)"] = 10,
) -> dict:
    """Search US Copyright Office registrations and recorded documents.

    Searches the Copyright Public Records System (publicrecords.copyright.gov).
    Returns registrations (post-1978 and digitized card catalog) and
    recorded documents (transfers, assignments, licenses).

    Each result includes title, claimant, registration number, dates,
    work type, and registration status.
    """
    async with CopyrightClient() as client:
        response = await client.search(query, field=field, page=page, page_size=page_size)
        return {
            "metadata": _dump(response.metadata),
            "histogram": _dump(response.histogram),
            "results": [_dump(r) for r in response.records],
        }


@copyright_mcp.tool(annotations=READ_ONLY)
async def get_copyright_record(
    public_records_id: Annotated[
        str,
        "Public records ID (e.g. 'card_catalog_CC19381945B_390000-391999.1449')",
    ],
) -> dict:
    """Get a specific copyright record by its public records ID.

    Returns the full registration or recordation record.
    """
    async with CopyrightClient() as client:
        record = await client.get_record(public_records_id)
        if record is None:
            return {"error": f"No record found for ID {public_records_id}"}
        return _dump(record)  # type: ignore[return-value]
