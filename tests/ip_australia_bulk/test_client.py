"""Client-level smoke tests for the IP RAPID bulk catalog client."""

from __future__ import annotations

from patent_client_agents.ip_australia_bulk import CKAN_HOST, IpAustraliaBulkClient


def test_default_base_url_is_data_gov_au() -> None:
    client = IpAustraliaBulkClient()
    assert client.base_url == CKAN_HOST
    # No auth (data.gov.au CKAN is public).
    assert client._client.auth is None  # type: ignore[attr-defined]
