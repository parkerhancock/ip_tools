"""USPTO ODP client implementations."""

from .applications import ApplicationsClient
from .base import (
    PaginationModel,
    SearchPayload,
    UsptoOdpBaseClient,
)
from .bulkdata import BulkDataClient
from .petitions import PetitionsClient
from .ptab_appeals import PtabAppealsClient
from .ptab_interferences import PtabInterferencesClient
from .ptab_trials import PtabTrialsClient

__all__ = [
    # Base
    "UsptoOdpBaseClient",
    "SearchPayload",
    "PaginationModel",
    # Domain clients
    "ApplicationsClient",
    "BulkDataClient",
    "PetitionsClient",
    "PtabTrialsClient",
    "PtabAppealsClient",
    "PtabInterferencesClient",
]
