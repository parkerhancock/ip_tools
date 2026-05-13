"""EUIPO MCP tools — Trademark Search + Design Search.

Read-only access to the EUIPO Trademark and Design (RCD) registers via
OAuth 2.0 client_credentials. Env-gated: tools register only when
``EUIPO_CLIENT_ID`` and ``EUIPO_CLIENT_SECRET`` are both set. Same
client + subscription works for both products.

Set ``EUIPO_ENV=sandbox`` to point at the sandbox host (no identity-
document approval required, but the dataset is a frozen historical
snapshot + synthetic test rows). Production access requires emailing
ID documents to ``docs.apiplatform@euipo.europa.eu``.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from law_tools_core.mcp.conditional import conditional_tool
from patent_client_agents.euipo_designs import (
    GetDesignInput,
    SearchDesignsInput,
    get_design,
    search_designs,
)
from patent_client_agents.euipo_trademarks import (
    GetTrademarkInput,
    SearchTrademarksInput,
    get_trademark,
    search_trademarks,
)

euipo_mcp = FastMCP("EUIPO")

_EUIPO_REQUIRED_ENV: list[str] = ["EUIPO_CLIENT_ID", "EUIPO_CLIENT_SECRET"]


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


# ---------------------------------------------------------------------------
# Trademarks
# ---------------------------------------------------------------------------


@conditional_tool(euipo_mcp, requires_env=_EUIPO_REQUIRED_ENV, annotations=READ_ONLY)
async def search_euipo_trademarks(
    query: Annotated[
        str | None,
        (
            "RSQL filter expression. Examples: "
            "'wordMarkSpecification.verbalElement==*Apple* and status==REGISTERED' "
            "or 'applicationDate>=2024-01-01 and niceClasses=all=(25,28)'. "
            "Omit for an unfiltered listing of the full register."
        ),
    ] = None,
    page: Annotated[int, "0-indexed page number"] = 0,
    size: Annotated[int, "Page size, 10..100"] = 25,
    sort: Annotated[
        str | None,
        "Sort spec, e.g. 'applicationDate:desc' or 'applicationNumber:asc'",
    ] = None,
    fields: Annotated[
        str | None,
        "EBNF field selector to trim the payload, e.g. '!(goodsAndServices)'",
    ] = None,
) -> dict:
    """Search EUTMs (EU Trade Marks + IRs designating the EU) using RSQL.

    Returns a paginated envelope ``{trademarks, totalElements, totalPages, size, page}``.
    Each item carries application number, status, mark feature/kind/basis,
    Nice classes, applicants/representatives, and key dates.

    The EUIPO RSQL DSL supports ``==`` (exact), ``=in=`` / ``=out=`` (set
    membership), ``=all=`` (all-of), wildcards with ``*``, and boolean
    ``and`` / ``or`` / ``not`` operators. Field paths are dotted, e.g.
    ``wordMarkSpecification.verbalElement``, ``applicants.name``.
    """
    params = SearchTrademarksInput(query=query, page=page, size=size, sort=sort, fields=fields)
    return _dump(await search_trademarks(params))  # type: ignore[return-value]


@conditional_tool(euipo_mcp, requires_env=_EUIPO_REQUIRED_ENV, annotations=READ_ONLY)
async def get_euipo_trademark(
    application_number: Annotated[
        str,
        (
            "EUTM application number, zero-padded 9-digit string "
            "(e.g. '000274084') or 'W########[A]' for international "
            "registrations designating the EU"
        ),
    ],
) -> dict:
    """Fetch the full record for a single EUTM by application number.

    Returns ~40 fields including prosecution history, oppositions,
    cancellations, appeals, records, decisions, and goods-and-services
    classifications. Media (image / sound / video / 3D model) is returned
    by separate endpoints — not exposed here in v1.
    """
    params = GetTrademarkInput(application_number=application_number)
    return _dump(await get_trademark(params))  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Designs (RCDs)
# ---------------------------------------------------------------------------


@conditional_tool(euipo_mcp, requires_env=_EUIPO_REQUIRED_ENV, annotations=READ_ONLY)
async def search_euipo_designs(
    query: Annotated[
        str | None,
        (
            "RSQL filter expression. Examples: "
            "'applicationDate>=2024-01-01 and locarnoClasses=in=(14.03,14.04)' "
            "or 'status==REGISTERED_AND_FULLY_PUBLISHED'. "
            "Omit for an unfiltered listing of the full register."
        ),
    ] = None,
    page: Annotated[int, "0-indexed page number"] = 0,
    size: Annotated[int, "Page size, 10..100"] = 25,
    sort: Annotated[str | None, "Sort spec, e.g. 'applicationDate:desc'"] = None,
    fields: Annotated[str | None, "EBNF field selector"] = None,
) -> dict:
    """Search Registered Community Designs (RCDs) using RSQL.

    Returns ``{designs, totalElements, totalPages, size, page}``. Each
    item carries design number, application number, status, Locarno
    classes, applicants/representatives, and key dates.

    A multi-design application produces one entry per indexed design
    (e.g. ``099037115-0001``, ``099037115-0002``, …).
    """
    params = SearchDesignsInput(query=query, page=page, size=size, sort=sort, fields=fields)
    return _dump(await search_designs(params))  # type: ignore[return-value]


@conditional_tool(euipo_mcp, requires_env=_EUIPO_REQUIRED_ENV, annotations=READ_ONLY)
async def get_euipo_design(
    design_number: Annotated[
        str,
        "RCD design number, e.g. '099037115-0001' (9 digits + dash + 4 digits)",
    ],
) -> dict:
    """Fetch the full record for a single RCD by design number.

    Returns prosecution history, product indications (multilingual),
    views (image angles), Locarno classification, priorities, and
    decisions. Media (view images / 3D model) is returned by separate
    endpoints — not exposed here in v1.
    """
    params = GetDesignInput(design_number=design_number)
    return _dump(await get_design(params))  # type: ignore[return-value]


__all__ = ["euipo_mcp"]
