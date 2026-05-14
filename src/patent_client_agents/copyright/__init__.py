"""US Copyright Office public records search.

Queries the undocumented JSON API at api.publicrecords.copyright.gov.
Searches registrations and recorded documents (transfers, assignments).
No authentication required. Requires HTTP/2.
"""

from patent_client_agents.copyright.client import CopyrightClient, CopyrightError
from patent_client_agents.copyright.models import (
    CopyrightRecord,
    Histogram,
    SearchMetadata,
    SearchResponse,
)

__all__ = [
    "CopyrightClient",
    "CopyrightError",
    "CopyrightRecord",
    "Histogram",
    "SearchMetadata",
    "SearchResponse",
]
