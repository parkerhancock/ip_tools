"""USPTO Patent Assignment MCP tools.

The trademark-assignment half of the original combined ``assignments``
module lives with ``law-tools``; this file carries only the patent-side
tools backed by ``patent_client_agents.uspto_assignments``.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.exceptions import ValidationError
from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.uspto_assignments import AssignmentCenterClient

patent_assignments_mcp = FastMCP("PatentAssignments")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


def _dump_list(items: list) -> dict:
    return {"results": [_dump(i) for i in items]}


@patent_assignments_mcp.tool(annotations=READ_ONLY)
async def search_patent_assignments(
    assignee: Annotated[
        str | None,
        "Assignee name (party receiving patent rights).",
    ] = None,
    assignor: Annotated[
        str | None,
        "Assignor name (party transferring patent rights).",
    ] = None,
    patent_number: Annotated[
        str | None,
        "USPTO patent number to look up chain of title for.",
    ] = None,
    application_number: Annotated[
        str | None,
        "USPTO application number to look up recorded assignments for.",
    ] = None,
    reel_frame: Annotated[
        str | None,
        "Reel/frame identifier (e.g. '52614/446') for a specific recordation.",
    ] = None,
    paginate_all: Annotated[
        bool,
        "When true, auto-paginates through all matching results (assignee/assignor only). "
        "Ignored for patent_number, application_number, and reel_frame lookups.",
    ] = False,
) -> dict:
    """Search USPTO patent assignments. Exactly one filter must be set.

    Returns assignment records with reel/frame, recording date, conveyance
    type, assignor/assignee details, and affected properties (applications
    and patents).
    """
    filters = {
        "assignee": assignee,
        "assignor": assignor,
        "patent_number": patent_number,
        "application_number": application_number,
        "reel_frame": reel_frame,
    }
    set_filters = [k for k, v in filters.items() if v is not None]
    if len(set_filters) != 1:
        raise ValidationError(
            f"search_patent_assignments requires exactly one filter; got {set_filters or 'none'}"
        )
    selected = set_filters[0]
    value = filters[selected]
    assert value is not None

    async with AssignmentCenterClient() as client:
        if selected == "assignee":
            if paginate_all:
                records = await client.search_all(assignee_name=value)
            else:
                records = await client.search_by_assignee(value)
        elif selected == "assignor":
            if paginate_all:
                records = await client.search_all(assignor_name=value)
            else:
                records = await client.search_by_assignor(value)
        elif selected == "patent_number":
            records = await client.search_by_patent(value)
        elif selected == "application_number":
            records = await client.search_by_application(value)
        else:  # reel_frame
            records = await client.search_by_reel_frame(value)
    return _dump_list(records)
