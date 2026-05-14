"""UPC MCP tools — decisions/orders feed + statutes corpus.

Two surfaces:

* **Decisions** scrape the public listing at
  ``unifiedpatentcourt.org/.../decisions-and-orders``. The listing
  itself isn't auth-gated, but per-decision detail pages are Cloudflare-
  challenged — these tools deliberately stay on the listing and the
  direct PDF URLs.
* **Statutes** read from a pre-built SQLite/FTS5 corpus produced by
  ``patent-client-agents-build-upc-statutes-corpus``. If the corpus
  isn't materialized at runtime, the tool surfaces a clear
  :class:`CorpusUnavailable` message with the build command.

Neither surface requires credentials, so the tools are unconditionally
registered.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.upc_decisions import (
    DecisionLookupInput,
    DecisionSearchInput,
    get_decision,
    list_divisions,
    list_languages,
    search_decisions,
)
from patent_client_agents.upc_statutes import (
    InstrumentInput,
    StatuteSearchInput,
    get_instrument,
    list_instruments,
    search,
)

upc_mcp = FastMCP("UPC")


def _dump(obj: object) -> object:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    if isinstance(obj, list):
        return [_dump(item) for item in obj]
    return obj


# ---------------------------------------------------------------------------
# Decisions and Orders
# ---------------------------------------------------------------------------


@upc_mcp.tool(annotations=READ_ONLY)
async def search_upc_decisions(
    page: Annotated[int, "0-indexed page number, default 0 (most recent)"] = 0,
    judgement_type: Annotated[
        str | None,
        "Filter to 'order' or 'decision'; omit for both",
    ] = None,
    court_type: Annotated[
        str | None,
        (
            "Court-type ID: '1' = Court of Appeal, '2' = Central CFI, "
            "'3' = Local CFI, '4' = Regional CFI. Omit for all."
        ),
    ] = None,
    division: Annotated[
        str | None,
        "Specific division ID — use list_upc_divisions to discover",
    ] = None,
    proceedings_lang: Annotated[
        str | None,
        "Procedural-language ID — use list_upc_languages to discover",
    ] = None,
) -> dict:
    """Search the UPC decisions-and-orders index.

    Returns a page of decisions with canonical case IDs
    (``UPC_CFI_<n>/<yyyy>``, ``UPC_CoA_<n>/<yyyy>``, or
    ``ACT_<n>/<yyyy>``), court, type of action, parties, and direct
    URLs to the PDF/A document(s). Pagination via the ``page`` arg;
    total page count is reported in the response.
    """
    params = DecisionSearchInput(
        page=page,
        judgement_type=judgement_type,
        court_type=court_type,
        division=division,
        proceedings_lang=proceedings_lang,
    )
    return _dump(await search_decisions(params))  # type: ignore[return-value]


@upc_mcp.tool(annotations=READ_ONLY)
async def get_upc_decision(
    case_id: Annotated[
        str,
        (
            "Canonical UPC case identifier. Examples: 'UPC_CFI_1747/2025', "
            "'UPC_CoA_335/2023', 'ACT_551054/2023'. Hyphenated variants "
            "like 'UPC-CFI-478/2025' are accepted and normalized."
        ),
    ],
) -> dict:
    """Look up a single UPC decision by its case identifier.

    Walks the listing pages until a match is found; returns ``None`` if
    no matching row exists.
    """
    params = DecisionLookupInput(case_id=case_id)
    return _dump(await get_decision(params))  # type: ignore[return-value]


@upc_mcp.tool(annotations=READ_ONLY)
async def list_upc_divisions() -> list[dict]:
    """List the UPC division filter options.

    Returns the dropdown values used by the
    :func:`search_upc_decisions` ``division`` argument. The list
    includes Central / Local / Regional Divisions and the Court of
    Appeal seat.
    """
    return _dump(await list_divisions())  # type: ignore[return-value]


@upc_mcp.tool(annotations=READ_ONLY)
async def list_upc_languages() -> list[dict]:
    """List the UPC procedural-language filter options.

    Returns the dropdown values used by the
    :func:`search_upc_decisions` ``proceedings_lang`` argument
    (English, French, German, plus minority procedural languages used
    by specific Local Divisions).
    """
    return _dump(await list_languages())  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Statutes
# ---------------------------------------------------------------------------


@upc_mcp.tool(annotations=READ_ONLY)
async def search_upc_statutes(
    query: Annotated[str, "Search query against the UPC statutes corpus"],
    instrument: Annotated[
        str | None,
        (
            "Optional instrument key — 'upca', 'rop', 'fees', or 'coc'. "
            "Use 'statute' as an alias for the UPCA Annex I portion. "
            "Omit to search across all instruments."
        ),
    ] = None,
    language: Annotated[
        str,
        "ISO 639-1: 'en' (default), 'fr', or 'de'",
    ] = "en",
    per_page: Annotated[int, "Hits per page, 1..100"] = 10,
    page: Annotated[int, "1-indexed page number"] = 1,
) -> dict:
    """Search the UPC statutes corpus (UPCA, RoP, Fees, CoC).

    Returns ranked snippets with ``<mark>...</mark>`` highlights around
    matched terms. Use this for citation lookups like ``"Article 33"``
    or topical searches like ``"opt-out withdrawal"``.
    """
    params = StatuteSearchInput(
        query=query,
        instrument=instrument,
        language=language,
        per_page=per_page,
        page=page,
    )
    return _dump(await search(params))  # type: ignore[return-value]


@upc_mcp.tool(annotations=READ_ONLY)
async def get_upc_section(
    instrument: Annotated[
        str,
        "Instrument key: 'upca', 'rop', 'fees', or 'coc'",
    ],
    language: Annotated[str, "'en' (default), 'fr', or 'de'"] = "en",
) -> dict:
    """Fetch the full plain text of a UPC legal instrument.

    Note: section-level (per-Article, per-Rule) retrieval is not yet
    available. For now, pair this tool with
    :func:`search_upc_statutes` to locate a specific provision and
    quote the snippet.
    """
    params = InstrumentInput(instrument=instrument, language=language)
    return _dump(await get_instrument(params))  # type: ignore[return-value]


@upc_mcp.tool(annotations=READ_ONLY)
async def list_upc_instruments(
    language: Annotated[
        str | None,
        "Filter to a single language; omit for all",
    ] = None,
) -> list[dict]:
    """List instruments available in the UPC statutes corpus.

    Each entry carries the instrument key, short name, title, language,
    source PDF URL, and page count.
    """
    return _dump(await list_instruments(language=language))  # type: ignore[return-value]


__all__ = ["upc_mcp"]
