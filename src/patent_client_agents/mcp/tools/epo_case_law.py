"""EPO Case Law of the Boards of Appeal MCP tools.

Corpus-backed search + per-section retrieval against a SQLite/FTS5
snapshot of the EPO Boards of Appeal "white book" — the canonical
compilation of case law referenced constantly in European patent
prosecution and opposition.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.epo_case_law import SearchInput, get_section, search

epo_case_law_mcp = FastMCP("EPO Case Law")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


@epo_case_law_mcp.tool(annotations=READ_ONLY)
async def search_epo_case_law(
    query: Annotated[str, "Search query against the EPO Case Law of the Boards of Appeal"],
) -> dict:
    """Search the EPO Case Law of the Boards of Appeal ("white book").

    Returns matching Case Law sections with relevance-ranked
    snippets. Covers Parts I-VII of the canonical compilation —
    the reference for how EPC Articles have been interpreted by
    the Boards of Appeal.
    """
    result = await search(SearchInput(query=query))
    return _dump(result)  # type: ignore[return-value]


@epo_case_law_mcp.tool(annotations=READ_ONLY)
async def get_epo_case_law_section(
    section: Annotated[
        str,
        (
            "Case Law section identifier. Accepts canonical citations "
            "like 'I.A.1' / 'I-A-1' / 'I A 1', URL slugs like "
            "'clr_i_a_1', or full epo.org URLs."
        ),
    ],
) -> dict:
    """Get a specific Case Law section by citation.

    Returns the full text of the requested section. Case Law is
    published at www.epo.org/en/legal/case-law/<year>/ with one
    HTML page per leaf section (``clr_i_a_1.html`` etc.).
    """
    result = await get_section(section)
    return _dump(result)  # type: ignore[return-value]
