"""USPTO Trademark MCP tools (TESS search, TMEP, TSDR, trademark assignments).

Tools backed by:

- ``patent_client_agents.uspto_tmsearch`` — TESS Elasticsearch search.
  Needs an AWS WAF token (see token_manager docs); install with the
  ``[tmsearch]`` extra to enable in-process token minting via Playwright.
- ``patent_client_agents.tmep`` — TMEP corpus search/lookup. No auth.
- ``patent_client_agents.uspto_tsdr`` — TSDR status / documents.
  Requires ``USPTO_TSDR_API_KEY``.
- ``patent_client_agents.uspto_trademark_assignments`` — Assignment Center
  records. No auth.
"""

from __future__ import annotations

import json
from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.exceptions import ValidationError
from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.tmep import SearchInput, get_section, search
from patent_client_agents.uspto_tmsearch import TmsearchClient
from patent_client_agents.uspto_trademark_assignments import TrademarkAssignmentClient
from patent_client_agents.uspto_tsdr import TsdrClient

trademarks_mcp = FastMCP("Trademarks")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


def _dump_list(items: list) -> dict:
    return {"results": [_dump(i) for i in items]}


# ---------------------------------------------------------------
# Trademark Search (TESS)
# ---------------------------------------------------------------


@trademarks_mcp.tool(annotations=READ_ONLY)
async def search_trademarks(
    query: Annotated[str, "Search query — a wordmark, owner name, or goods/services description"],
    search_by: Annotated[
        str,
        "Which field to search. 'wordmark' (default) — trademark text; 'owner' — registrant name; "
        "'goods_services' — goods/services description. The legacy 'general' alias is "
        "equivalent to 'wordmark'.",
    ] = "wordmark",
    paginate_all: Annotated[
        bool,
        "When true, auto-paginates through all matching results (wordmark/owner only). "
        "Ignored for goods_services.",
    ] = False,
    max_results: Annotated[
        int,
        "Cap on total results when paginate_all=True.",
    ] = 500,
) -> dict:
    """Search USPTO trademarks (TESS).

    Unified search across wordmarks, owners, and goods/services descriptions.
    Use ``get_trademark`` for lookup by serial or registration number.
    """
    field = search_by.strip().lower()
    if field == "general":
        field = "wordmark"
    if field not in ("wordmark", "owner", "goods_services"):
        raise ValidationError(
            f"search_by must be 'wordmark', 'owner', or 'goods_services'; got {search_by!r}"
        )

    async with TmsearchClient() as client:
        if paginate_all:
            if field == "goods_services":
                raise ValidationError(
                    "paginate_all is not supported for search_by='goods_services'"
                )
            kwargs: dict = {"max_results": max_results}
            if field == "owner":
                kwargs["owner"] = query
            else:
                kwargs["wordmark"] = query
            results = await client.search_all(**kwargs)
            return _dump_list(results)

        if field == "wordmark":
            result = await client.search(wordmark=query)
        elif field == "owner":
            result = await client.search_owner(query)
        else:  # goods_services
            result = await client.search(goods_services=query)
        return _dump(result)  # type: ignore[return-value]


@trademarks_mcp.tool(annotations=READ_ONLY)
async def get_trademark(
    serial_number: Annotated[
        str | None,
        "USPTO trademark serial number (e.g. '97123456').",
    ] = None,
    registration_number: Annotated[
        str | None,
        "USPTO trademark registration number.",
    ] = None,
) -> dict | None:
    """Get a trademark by serial or registration number. Exactly one must be set.

    Returns full trademark details: wordmark, owner, goods/services, filing
    and registration dates, status. For current status only (no full record),
    use ``get_trademark_status`` (TSDR).
    """
    if bool(serial_number) == bool(registration_number):
        raise ValidationError(
            "get_trademark requires exactly one of serial_number or registration_number"
        )

    async with TmsearchClient() as client:
        if serial_number:
            result = await client.get_by_serial(serial_number)
        else:
            assert registration_number is not None
            result = await client.get_by_registration(registration_number)
        if result is None:
            return None
        return _dump(result)  # type: ignore[return-value]


# ---------------------------------------------------------------
# TSDR (Trademark Status & Document Retrieval)
# ---------------------------------------------------------------


@trademarks_mcp.tool(annotations=READ_ONLY)
async def get_trademark_status(
    serial_number: Annotated[str, "USPTO trademark serial number"],
) -> dict:
    """Get trademark status from TSDR.

    Returns current status, filing date, registration date, mark text,
    and status description. Requires ``USPTO_TSDR_API_KEY``.
    """
    async with TsdrClient() as client:
        result = await client.get_status(serial_number)
        return _dump(result)  # type: ignore[return-value]


@trademarks_mcp.tool(annotations=READ_ONLY)
async def get_trademark_documents(
    serial_number: Annotated[str, "USPTO trademark serial number"],
) -> dict:
    """Get prosecution documents for a trademark from TSDR.

    Returns documents filed during prosecution: office actions,
    responses, registration certificates, etc. Requires
    ``USPTO_TSDR_API_KEY``.
    """
    async with TsdrClient() as client:
        docs = await client.get_documents(serial_number)
        return _dump_list(docs)


@trademarks_mcp.tool(annotations=READ_ONLY)
async def batch_trademark_status(
    serial_numbers_json: Annotated[
        str, 'JSON array of serial numbers, e.g. \'["97123456", "97654321"]\''
    ],
) -> dict:
    """Batch check trademark status for multiple marks.

    Accepts a JSON array string of serial numbers. Returns status for
    each. Requires ``USPTO_TSDR_API_KEY``.
    """
    serial_numbers = json.loads(serial_numbers_json)
    if not isinstance(serial_numbers, list):
        raise ValidationError("Expected a JSON array of strings")

    async with TsdrClient() as client:
        result = await client.batch_status(serial_numbers)
        return result


@trademarks_mcp.tool(annotations=READ_ONLY)
async def get_trademark_last_update(
    serial_number: Annotated[str, "USPTO trademark serial number"],
) -> dict:
    """Get the last-update timestamp for a trademark case.

    Returns when the trademark record was last modified at the USPTO.
    Requires ``USPTO_TSDR_API_KEY``.
    """
    async with TsdrClient() as client:
        result = await client.get_last_update(serial_number)
        return _dump(result)  # type: ignore[return-value]


# ---------------------------------------------------------------
# TMEP (Trademark Manual of Examining Procedure)
# ---------------------------------------------------------------


@trademarks_mcp.tool(annotations=READ_ONLY)
async def search_tmep(
    query: Annotated[str, "Search query for the TMEP"],
) -> dict:
    """Search the Trademark Manual of Examining Procedure.

    Returns matching TMEP sections with relevance-ranked snippets.
    Useful for finding examination guidance on trademark registration
    issues.
    """
    result = await search(SearchInput(query=query))
    return _dump(result)  # type: ignore[return-value]


@trademarks_mcp.tool(annotations=READ_ONLY)
async def get_tmep_section(
    section: Annotated[str, "TMEP section number (e.g. '1207', '1207.01(a)') or href"],
) -> dict:
    """Get a specific TMEP section by number.

    Returns the full text of the requested section from the Trademark
    Manual of Examining Procedure.
    """
    result = await get_section(section)
    return _dump(result)  # type: ignore[return-value]


# ---------------------------------------------------------------
# Trademark Assignment Center
# ---------------------------------------------------------------


_TM_ASSIGNMENT_AXES = (
    "assignee",
    "assignor",
    "serial_number",
    "registration_number",
    "reel_frame",
)


@trademarks_mcp.tool(annotations=READ_ONLY)
async def search_trademark_assignments(
    query: Annotated[
        str,
        "Value to search for (e.g. 'Apple Inc', '97123456', '9006/0093').",
    ],
    by: Annotated[
        str,
        "What kind of value `query` is. One of: assignee, assignor, "
        "serial_number, registration_number, reel_frame.",
    ],
    limit: Annotated[
        int,
        "Maximum records to return per request (max 1000).",
    ] = 100,
    start_row: Annotated[
        int,
        "1-based starting row for pagination.",
    ] = 1,
) -> dict:
    """Search USPTO trademark assignment recordations.

    Returns recordations with reel/frame, conveyance, assignors,
    assignees, and affected trademark properties. No auth required.
    """
    axis = by.strip().lower()
    if axis not in _TM_ASSIGNMENT_AXES:
        raise ValidationError(f"`by` must be one of {_TM_ASSIGNMENT_AXES}; got {by!r}")

    async with TrademarkAssignmentClient() as client:
        if axis == "assignee":
            records = await client.search_by_assignee(query, start_row=start_row, limit=limit)
        elif axis == "assignor":
            records = await client.search_by_assignor(query, start_row=start_row, limit=limit)
        elif axis == "serial_number":
            records = await client.search_by_serial(query, start_row=start_row, limit=limit)
        elif axis == "registration_number":
            records = await client.search_by_registration(query, start_row=start_row, limit=limit)
        else:  # reel_frame
            records = await client.search_by_reel_frame(query, start_row=start_row, limit=limit)

    return _dump_list(records)
