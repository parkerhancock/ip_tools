"""European Patent Convention (EPC) MCP tools.

Corpus-backed search + per-section retrieval against a SQLite/FTS5
snapshot of the EPC Convention Articles + Implementing Regulations
Rules from www.epo.org.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.epc import SearchInput, get_section, search

epc_mcp = FastMCP("EPC")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


@epc_mcp.tool(annotations=READ_ONLY)
async def search_epc(
    query: Annotated[str, "Search query against EPC Articles and Rules"],
) -> dict:
    """Search the European Patent Convention + Implementing Regulations.

    Returns matching Articles and Rules with relevance-ranked snippets.
    Covers the EPC 2000 Convention (180 Articles) and the Implementing
    Regulations (~176 Rules) as published by the EPO.
    """
    result = await search(SearchInput(query=query))
    return _dump(result)  # type: ignore[return-value]


@epc_mcp.tool(annotations=READ_ONLY)
async def get_epc_section(
    section: Annotated[
        str,
        (
            "EPC section identifier. Accepts canonical citations like "
            "'Article 54' / 'Art. 54' / 'Rule 71' / 'R. 71', URL slugs "
            "like 'a54' or 'r71', or full epo.org URLs."
        ),
    ],
) -> dict:
    """Get a specific EPC Article or Rule by citation.

    Returns the full text of the requested provision. EPC content
    is published at www.epo.org/en/legal/epc/<year>/ with one HTML
    page per Article (``a<N>.html``) or Rule (``r<N>.html``).
    """
    result = await get_section(section)
    return _dump(result)  # type: ignore[return-value]
