"""Async client for the Australian Trade Mark Search API (IP Australia).

Two endpoints: ``POST /search/quick`` for filtered listings (with the
ATMOSS-style ``quickSearchType`` / ``status`` / ``changedSinceDate``
filters) and ``GET /trade-mark/{ipRightIdentifier}`` for one full
record. OAuth 2.0 client_credentials, free to call.

The ``changedSinceDate`` filter makes incremental sync against the
Australian trade marks register trivial — a feature USPTO TSDR and
EUIPO do not directly expose.
"""

from .client import IpAustraliaTrademarksClient
from .models import Trademark, TrademarkSearchHit, TrademarkSearchResult

__all__ = [
    "IpAustraliaTrademarksClient",
    "Trademark",
    "TrademarkSearchHit",
    "TrademarkSearchResult",
]
