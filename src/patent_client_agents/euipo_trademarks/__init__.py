"""Async client for the EUIPO Trademark Search API.

EUIPO's Trademark Search API covers all ~2.3M EU trademarks (EUTMs +
international registrations designating the EU) since the office opened
in 1996. Filtered by an RSQL query DSL; pagination is 0-indexed with
``page=`` and ``size=`` (10..100). Both sandbox and production are
covered — see :class:`EuipoTrademarksClient` for the environment toggle.
"""

from .api import (  # noqa: F401
    EuipoEnvironment,
    EuipoTrademarksClient,
    GetTrademarkInput,
    GetTrademarkMediaInput,
    GoodsAndServicesClass,
    GoodsAndServicesTerms,
    MarkBasis,
    MarkFeature,
    MarkKind,
    Person,
    Publication,
    SearchTrademarksInput,
    Status,
    Trademark,
    TrademarkSearchResult,
    TrademarkSearchResultItem,
    WordMarkSpecification,
    get_client,
    get_trademark,
    get_trademark_image,
    get_trademark_image_thumbnail,
    get_trademark_model,
    get_trademark_sound,
    get_trademark_video,
    search_trademarks,
)

__all__ = [
    "EuipoEnvironment",
    "EuipoTrademarksClient",
    "GetTrademarkInput",
    "GetTrademarkMediaInput",
    "GoodsAndServicesClass",
    "GoodsAndServicesTerms",
    "MarkBasis",
    "MarkFeature",
    "MarkKind",
    "Person",
    "Publication",
    "SearchTrademarksInput",
    "Status",
    "Trademark",
    "TrademarkSearchResult",
    "TrademarkSearchResultItem",
    "WordMarkSpecification",
    "get_client",
    "get_trademark",
    "get_trademark_image",
    "get_trademark_image_thumbnail",
    "get_trademark_model",
    "get_trademark_sound",
    "get_trademark_video",
    "search_trademarks",
]
