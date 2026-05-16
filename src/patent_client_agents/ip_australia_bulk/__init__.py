"""IP RAPID bulk data catalog client (data.gov.au).

Lightweight CKAN catalog + download surface for the IP RAPID weekly
snapshot. No auth — IP RAPID is published under Creative Commons.

This connector intentionally ships a minimal v1 surface (catalog +
download) per CONNECTOR_STANDARDS.md §7.2 Shape E. Full CSV ingestion
(~40 tables across patents / trade marks / designs / PBR) is deferred
to a follow-up to keep the OAuth-API rights surface independent.
"""

from .client import CKAN_HOST, IpAustraliaBulkClient
from .models import BulkDataset, BulkResource

__all__ = [
    "CKAN_HOST",
    "BulkDataset",
    "BulkResource",
    "IpAustraliaBulkClient",
]
