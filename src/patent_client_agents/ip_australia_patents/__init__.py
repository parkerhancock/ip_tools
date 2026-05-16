"""Async client for the Australian Patent Search API (IP Australia).

IP Australia's Patent Search API covers the live AusPat register
(bibliographic coverage back to 1904). Two endpoints:
``POST /search/quick`` for filtered listings and
``GET /patent/{ipRightIdentifier}`` for one full record. OAuth 2.0
client_credentials, free to call.

See :class:`IpAustraliaPatentsClient` for the auth + environment
contract; the shared scaffolding lives in
:mod:`patent_client_agents.ip_australia_common`.
"""

from .client import IpAustraliaPatentsClient
from .models import Patent, PatentSearchHit, PatentSearchResult

__all__ = [
    "IpAustraliaPatentsClient",
    "Patent",
    "PatentSearchHit",
    "PatentSearchResult",
]
