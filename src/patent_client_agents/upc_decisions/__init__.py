"""UPC decisions-and-orders connector (MCP-free public surface)."""

from .api import (
    DecisionLookupInput,
    DecisionSearchInput,
    UpcDecision,
    UpcDecisionsClient,
    UpcDecisionSearchResponse,
    UpcDivision,
    UpcLanguage,
    download_decision_pdf,
    get_client,
    get_decision,
    list_divisions,
    list_languages,
    search_decisions,
)

__all__ = [
    "UpcDecisionsClient",
    "UpcDecision",
    "UpcDecisionSearchResponse",
    "UpcDivision",
    "UpcLanguage",
    "DecisionSearchInput",
    "DecisionLookupInput",
    "get_client",
    "search_decisions",
    "get_decision",
    "download_decision_pdf",
    "list_divisions",
    "list_languages",
]
