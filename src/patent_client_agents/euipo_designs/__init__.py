"""Async client for the EUIPO Design (RCD) Search API.

EUIPO's Design Search API covers all ~1.5M Registered Community Designs
since 1 April 2003. Filtered by an RSQL query DSL; pagination is
0-indexed with ``page=`` + ``size=`` (10..100). Same OAuth client as
:mod:`patent_client_agents.euipo_trademarks` — see
:class:`EuipoDesignsClient` for the environment toggle.
"""

from .api import (  # noqa: F401
    Design,
    Designer,
    DesignSearchResult,
    DesignSearchResultItem,
    EuipoDesignsClient,
    EuipoEnvironment,
    GetDesignInput,
    GetDesignMediaInput,
    GetDesignViewInput,
    Model3D,
    Person,
    ProductIndicationTerms,
    Publication,
    SearchDesignsInput,
    Status,
    View,
    get_client,
    get_design,
    get_design_model,
    get_design_view,
    get_design_view_thumbnail,
    search_designs,
)

__all__ = [
    "Design",
    "DesignSearchResult",
    "DesignSearchResultItem",
    "Designer",
    "EuipoDesignsClient",
    "EuipoEnvironment",
    "GetDesignInput",
    "GetDesignMediaInput",
    "GetDesignViewInput",
    "Model3D",
    "Person",
    "ProductIndicationTerms",
    "Publication",
    "SearchDesignsInput",
    "Status",
    "View",
    "get_client",
    "get_design",
    "get_design_model",
    "get_design_view",
    "get_design_view_thumbnail",
    "search_designs",
]
