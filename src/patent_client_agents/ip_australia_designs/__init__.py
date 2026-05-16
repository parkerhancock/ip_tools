"""Async client for the Australian Designs Search API (IP Australia).

Two endpoints: ``POST /search/quick`` (filterable by Locarno
classification, status, and ``changedSinceDate``) and
``GET /design/{ipRightIdentifier}`` for one full record. OAuth 2.0
client_credentials, free to call.
"""

from .client import IpAustraliaDesignsClient
from .models import Design, DesignSearchHit, DesignSearchResult

__all__ = [
    "Design",
    "DesignSearchHit",
    "DesignSearchResult",
    "IpAustraliaDesignsClient",
]
