"""WIPO Lex connector — global IP statute, treaty, and judgment database.

Sprint-1 scope is the **legislation** collection only (search + detail).
Treaties and judgments share the same URL/HTML shape and can be added
later without churning the public API.
"""

from .api import (  # noqa: F401
    USAGE_RESOURCE_URI,
    GetLegislationInput,
    LegislationDetail,
    LegislationSearchHit,
    LegislationSearchResponse,
    SearchLegislationInput,
    SubjectMatter,
    TypeOfText,
    WipoLexClient,
    WipoLexCollection,
    WipoLexFileLink,
    get_client,
    get_legislation,
    get_usage_resource,
    search_legislation,
)

__all__ = [
    "WipoLexClient",
    "SearchLegislationInput",
    "GetLegislationInput",
    "search_legislation",
    "get_legislation",
    "get_client",
    "LegislationDetail",
    "LegislationSearchHit",
    "LegislationSearchResponse",
    "SubjectMatter",
    "TypeOfText",
    "WipoLexCollection",
    "WipoLexFileLink",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]
