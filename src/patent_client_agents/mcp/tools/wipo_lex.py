"""WIPO Lex MCP tools.

Public-no-auth surface — these tools always register (no env gate).
Covers the **legislation** collection only; treaties and judgments
share the WIPO Lex URL shape and can be added as parallel tools.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from law_tools_core.mcp.annotations import READ_ONLY
from patent_client_agents.wipo_lex import (
    GetLegislationInput,
    SearchLegislationInput,
    SubjectMatter,
    TypeOfText,
    get_legislation,
    search_legislation,
)

wipo_lex_mcp = FastMCP("WIPO Lex")


def _dump(obj: object) -> object:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[union-attr]
    return obj


@wipo_lex_mcp.tool(annotations=READ_ONLY)
async def search_wipo_lex_legislation(
    country_codes: Annotated[
        list[str] | None,
        "ISO 3166-1 alpha-2 codes (['CA', 'US']) or regional org codes ('EU')",
    ] = None,
    subject_matter: Annotated[
        list[int] | None,
        "SubjectMatter codes: 1=Patents, 2=Utility Models, 3=Designs, 4=Trademarks, "
        "5=GIs, 9=Trade Secrets, 10=PVP, 11=Copyright, 12=Enforcement",
    ] = None,
    type_of_text: Annotated[
        list[int] | None,
        "TypeOfText codes: 205=Main IP Laws, 207=Implementing Rules, "
        "210=IP-related Laws, 213=Framework Laws, 214=Other, 215=National IP Strategy",
    ] = None,
    keywords: Annotated[str | None, "Free-text search over title + notes"] = None,
    start_date: Annotated[str | None, "Lower bound YYYY-MM-DD"] = None,
    end_date: Annotated[str | None, "Upper bound YYYY-MM-DD"] = None,
    include_historical: Annotated[bool, "Include superseded texts"] = False,
) -> dict:
    """Search WIPO Lex for IP legislation across ~200 jurisdictions.

    Returns a list of ``{legislation_id, title, url}`` hits. Use
    ``get_wipo_lex_legislation`` with a hit's ``legislation_id`` to get the
    full metadata + downloadable PDF/DOC links.

    Examples:
      * Canadian patent law: country_codes=["CA"], subject_matter=[1]
      * Trade secrets statutes globally: subject_matter=[9]
      * UK IP enforcement: country_codes=["GB"], subject_matter=[12]
    """
    params = SearchLegislationInput(
        country_codes=country_codes,
        subject_matter=[SubjectMatter(c) for c in subject_matter] if subject_matter else None,
        type_of_text=[TypeOfText(c) for c in type_of_text] if type_of_text else None,
        keywords=keywords,
        start_date=start_date,
        end_date=end_date,
        include_historical=include_historical,
    )
    return _dump(await search_legislation(params))  # type: ignore[return-value]


@wipo_lex_mcp.tool(annotations=READ_ONLY)
async def get_wipo_lex_legislation(
    legislation_id: Annotated[
        str, "WIPO Lex internal ID (e.g. '23293' for the Canadian Patent Act)"
    ],
) -> dict:
    """Fetch full metadata + downloadable PDF/DOC links for a single WIPO Lex entry.

    Returns title, jurisdiction, summary line, canonical URL, and a list of
    file attachments (typically EN/FR/multilingual PDFs and a Word version).
    """
    return _dump(await get_legislation(GetLegislationInput(legislation_id=legislation_id)))  # type: ignore[return-value]


__all__ = ["wipo_lex_mcp"]
