"""CanLII MCP tools.

Read-only access to Canadian courts / tribunals / statutes / regulations
via the CanLII REST API. Env-gated: tools only register when
``CANLII_API_KEY`` is set (matches the JPO env-gating pattern).
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from law_tools_core.mcp.conditional import conditional_tool
from patent_client_agents.canlii import (
    BrowseCasesInput,
    BrowseLegislationInput,
    GetCaseInput,
    GetCitatorInput,
    GetLegislationInput,
    Language,
    browse_cases,
    browse_legislation,
    get_case,
    get_cited_cases,
    get_cited_legislations,
    get_citing_cases,
    get_legislation,
    list_case_databases,
    list_legislation_databases,
)

canlii_mcp = FastMCP("CanLII")

_CANLII_REQUIRED_ENV: list[str] = ["CANLII_API_KEY"]


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def list_canlii_case_databases(
    language: Annotated[Language, "Output language: 'en' or 'fr'"] = "en",
) -> dict:
    """List every court / tribunal database CanLII indexes.

    Returns a flat list of ``{databaseId, jurisdiction, name}``. IP-relevant
    examples: ``fct`` (Federal Court), ``fca`` (Federal Court of Appeal),
    ``csc-scc`` (Supreme Court), ``tmob-comc`` (Trade-marks Opposition Board),
    ``cab-cab`` (Commissioner of Patents — Patent Appeal Board).
    """
    return _dump(await list_case_databases(language=language))  # type: ignore[return-value]


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def list_canlii_legislation_databases(
    language: Annotated[Language, "Output language: 'en' or 'fr'"] = "en",
) -> dict:
    """List every legislation database (statutes / regulations / annual statutes).

    IP-relevant examples: ``cas`` (federal statutes — Patent Act lives here as
    ``rsc-1985-c-p-4``; Trademarks Act as ``rsc-1985-c-t-13``), ``car``
    (federal regulations).
    """
    return _dump(await list_legislation_databases(language=language))  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def browse_canlii_cases(
    database_id: Annotated[str, "CanLII database code (e.g. 'fct', 'tmob-comc')"],
    offset: Annotated[int, "Record number to start from (0 = most recent)"] = 0,
    result_count: Annotated[int, "Page size (1-10000)"] = 100,
    language: Annotated[Language, "'en' or 'fr'"] = "en",
    published_after: Annotated[
        str | None, "ISO date YYYY-MM-DD — only return docs published on/after this date"
    ] = None,
    published_before: Annotated[str | None, "ISO date YYYY-MM-DD"] = None,
    decision_date_after: Annotated[
        str | None,
        "ISO date YYYY-MM-DD — only return decisions handed down on/after this date",
    ] = None,
    decision_date_before: Annotated[str | None, "ISO date YYYY-MM-DD"] = None,
) -> dict:
    """Browse cases from a CanLII database, newest first.

    Use ``list_canlii_case_databases`` to discover ``database_id`` values. Date
    filters are optional and can be combined (e.g. ``decisionDateAfter`` +
    ``decisionDateBefore`` for a window).
    """
    params = BrowseCasesInput(
        database_id=database_id,
        offset=offset,
        result_count=result_count,
        language=language,
        published_after=published_after,
        published_before=published_before,
        decision_date_after=decision_date_after,
        decision_date_before=decision_date_before,
    )
    return _dump(await browse_cases(params))  # type: ignore[return-value]


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def get_canlii_case(
    database_id: Annotated[str, "CanLII database code"],
    case_id: Annotated[str, "CanLII case identifier (e.g. '2008scc9')"],
    language: Annotated[Language, "'en' or 'fr'"] = "en",
) -> dict:
    """Fetch full metadata for a single CanLII case (no full text — use the ``url`` field).

    Returns title, citation, docket number, decision date, keywords, and a
    canonical ``url`` that points to the CanLII landing page.
    """
    params = GetCaseInput(database_id=database_id, case_id=case_id, language=language)
    return _dump(await get_case(params))  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Citator
# ---------------------------------------------------------------------------


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def get_canlii_cited_cases(
    database_id: Annotated[str, "CanLII database code"],
    case_id: Annotated[str, "CanLII case identifier"],
) -> dict:
    """List cases that ``case_id`` cites. (CanLII citator endpoint is English-only.)"""
    params = GetCitatorInput(database_id=database_id, case_id=case_id)
    return _dump(await get_cited_cases(params))  # type: ignore[return-value]


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def get_canlii_citing_cases(
    database_id: Annotated[str, "CanLII database code"],
    case_id: Annotated[str, "CanLII case identifier"],
) -> dict:
    """List cases that cite ``case_id``. (CanLII citator endpoint is English-only.)"""
    params = GetCitatorInput(database_id=database_id, case_id=case_id)
    return _dump(await get_citing_cases(params))  # type: ignore[return-value]


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def get_canlii_cited_legislations(
    database_id: Annotated[str, "CanLII database code"],
    case_id: Annotated[str, "CanLII case identifier"],
) -> dict:
    """List legislation that ``case_id`` cites."""
    params = GetCitatorInput(database_id=database_id, case_id=case_id)
    return _dump(await get_cited_legislations(params))  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Legislation
# ---------------------------------------------------------------------------


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def browse_canlii_legislation(
    database_id: Annotated[str, "Legislation database code (e.g. 'cas', 'car')"],
    language: Annotated[Language, "'en' or 'fr'"] = "en",
) -> dict:
    """List statutes / regulations within a legislation database."""
    params = BrowseLegislationInput(database_id=database_id, language=language)
    return _dump(await browse_legislation(params))  # type: ignore[return-value]


@conditional_tool(canlii_mcp, requires_env=_CANLII_REQUIRED_ENV, annotations=READ_ONLY)
async def get_canlii_legislation(
    database_id: Annotated[str, "Legislation database code"],
    legislation_id: Annotated[
        str, "Legislation identifier (e.g. 'rsc-1985-c-p-4' for the Patent Act)"
    ],
    language: Annotated[Language, "'en' or 'fr'"] = "en",
) -> dict:
    """Fetch metadata for a statute or regulation.

    Includes ``startDate`` / ``endDate`` and ``repealed`` flags for
    point-in-time interpretation, plus a list of parts/chapters.
    """
    params = GetLegislationInput(
        database_id=database_id,
        legislation_id=legislation_id,
        language=language,
    )
    return _dump(await get_legislation(params))  # type: ignore[return-value]


__all__ = ["canlii_mcp"]
