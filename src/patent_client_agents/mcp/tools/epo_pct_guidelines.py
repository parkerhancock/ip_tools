"""EPO PCT-EPO Guidelines MCP tools.

The Guidelines that apply when the EPO acts as ISA, IPEA, or RO under
the Patent Cooperation Treaty (PCT). Separate from the EPC Guidelines.
Corpus-backed search + per-section retrieval.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.epo_pct_guidelines import SearchInput, get_section, search

epo_pct_guidelines_mcp = FastMCP("EPO PCT-EPO Guidelines")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


@epo_pct_guidelines_mcp.tool(annotations=READ_ONLY)
async def search_epo_pct_guidelines(
    query: Annotated[str, "Search query for the PCT-EPO Guidelines"],
) -> dict:
    """Search the EPO Guidelines that apply under the PCT.

    Covers EPO's practice when acting as International Searching
    Authority, International Preliminary Examining Authority, or
    Receiving Office under the Patent Cooperation Treaty.
    """
    result = await search(SearchInput(query=query))
    return _dump(result)  # type: ignore[return-value]


@epo_pct_guidelines_mcp.tool(annotations=READ_ONLY)
async def get_epo_pct_guidelines_section(
    section: Annotated[
        str,
        (
            "PCT-EPO Guidelines section identifier. Accepts canonical "
            "citations like 'G-II, 3.1' or URL slugs like 'g_ii_3_1'."
        ),
    ],
) -> dict:
    """Get a specific PCT-EPO Guidelines section."""
    result = await get_section(section)
    return _dump(result)  # type: ignore[return-value]
