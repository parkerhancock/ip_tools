"""USPTO Office Action MCP tools.

Search office action rejections, citations, full text, and enriched citation
metadata via the USPTO ODP office action endpoints (X-API-KEY auth).
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.exceptions import ValidationError
from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.uspto_office_actions import OfficeActionClient

office_actions_mcp = FastMCP("Office Actions")


_SEARCH_DISPATCH = {
    "rejections": "search_rejections",
    "citations": "search_citations",
    "text": "search_office_action_text",
    "enriched_citations": "search_enriched_citations",
}


@office_actions_mcp.tool(annotations=READ_ONLY)
async def search_office_actions(
    criteria: Annotated[
        str,
        "Lucene query. Valid fields depend on result_type: "
        "  rejections → patentApplicationNumber, hasRej101, hasRej102, hasRej103, "
        "hasRej112, hasRejDP, legalSectionCode, nationalClass, groupArtUnitNumber, "
        "submissionDate, aliceIndicator, allowedClaimIndicator. "
        "  citations → patentApplicationNumber, referenceIdentifier, "
        "parsedReferenceIdentifier, legalSectionCode, examinerCitedReferenceIndicator, "
        "applicantCitedExaminerReferenceIndicator, groupArtUnitNumber, techCenter. "
        "  text → patentApplicationNumber, inventionTitle, submissionDate, "
        "legacyDocumentCodeIdentifier (CTNF/CTFR/NOA/…), groupArtUnitNumber, "
        "patentNumber, applicationTypeCategory. "
        "  enriched_citations → patentApplicationNumber, citedDocumentIdentifier, "
        "publicationNumber, inventorNameText, countryCode, kindCode, "
        "officeActionCategory, citationCategoryCode, officeActionDate, "
        "examinerCitedReferenceIndicator, nplIndicator, groupArtUnitNumber.",
    ],
    result_type: Annotated[
        str,
        "What to search: 'rejections' (per-claim rejection records with 101/102/103/112/"
        "DP indicators plus Alice/Bilski/Mayo/Myriad flags), 'citations' (prior-art "
        "references cited with examiner/applicant indicators), 'text' (full office-"
        "action body text with structured sections), or 'enriched_citations' (citations "
        "with inventor names, country/kind codes, and passage locations).",
    ] = "rejections",
    start: Annotated[int, "Result offset for pagination"] = 0,
    rows: Annotated[int, "Maximum results to return (max 100)"] = 25,
) -> dict:
    """Search USPTO office action data (rejections, citations, text, or enriched citations).

    All four result types share the same Lucene ``criteria`` surface but
    accept different field names — see the ``criteria`` description for
    the valid fields per type.
    """
    rt = result_type.strip().lower()
    method_name = _SEARCH_DISPATCH.get(rt)
    if method_name is None:
        raise ValidationError(
            f"result_type must be one of {sorted(_SEARCH_DISPATCH)}; got {result_type!r}"
        )
    async with OfficeActionClient() as client:
        method = getattr(client, method_name)
        result = await method(criteria, start=start, rows=rows)
        return result.model_dump()
