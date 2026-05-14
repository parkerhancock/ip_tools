"""EPO Unitary Patent (UP) Guidelines MCP tools.

The Guidelines for the EPO's role in administering the Unitary Patent
(UP) regime: opt-in/opt-out, fees, renewals, the UPP register. Separate
from the EPC and PCT Guidelines; uses flat ``N.M.P`` section numbering.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.epo_up_guidelines import SearchInput, get_section, search

epo_up_guidelines_mcp = FastMCP("EPO UP Guidelines")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


@epo_up_guidelines_mcp.tool(annotations=READ_ONLY)
async def search_epo_up_guidelines(
    query: Annotated[str, "Search query for the EPO Unitary Patent Guidelines"],
) -> dict:
    """Search the EPO Unitary Patent (UP) Guidelines.

    Covers the EPO's practice for the Unitary Patent regime —
    requesting unitary effect, fees, renewals, the UPP register, and
    related procedures under the UP Regulation and Implementing
    Regulations.
    """
    result = await search(SearchInput(query=query))
    return _dump(result)  # type: ignore[return-value]


@epo_up_guidelines_mcp.tool(annotations=READ_ONLY)
async def get_epo_up_guidelines_section(
    section: Annotated[
        str,
        (
            "UP Guidelines section identifier. Accepts citations like "
            "'1.2.1' / '1-2-1' / 'Section 1.2.1', or URL slugs like "
            "'section_1_2_1'."
        ),
    ],
) -> dict:
    """Get a specific UP Guidelines section."""
    result = await get_section(section)
    return _dump(result)  # type: ignore[return-value]
