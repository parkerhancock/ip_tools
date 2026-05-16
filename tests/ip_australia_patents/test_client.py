"""Client-level smoke tests for the IP Australia Patents client.

We do not exercise the live API here; the tests pin the auth + host
wiring so refactors of ``ip_australia_common`` don't silently regress
the per-rights clients.
"""

from __future__ import annotations

import pytest

from law_tools_core.exceptions import ConfigurationError
from law_tools_core.oauth2 import OAuth2ClientCredentialsAuth
from patent_client_agents.ip_australia_patents import IpAustraliaPatentsClient


def test_missing_env_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IPAUSTRALIA_CLIENT_ID", raising=False)
    monkeypatch.delenv("IPAUSTRALIA_CLIENT_SECRET", raising=False)
    with pytest.raises(ConfigurationError, match="IPAUSTRALIA_CLIENT_ID"):
        IpAustraliaPatentsClient()


def test_constructor_wires_oauth_against_production_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("IPAUSTRALIA_CLIENT_ID", "test-id")
    monkeypatch.setenv("IPAUSTRALIA_CLIENT_SECRET", "test-secret")
    monkeypatch.delenv("IPAUSTRALIA_ENV", raising=False)

    client = IpAustraliaPatentsClient()
    assert client.environment == "production"
    assert client.base_url.startswith("https://production.api.ipaustralia.gov.au")
    assert client.base_url.endswith("/public/australian-patent-search-api/v1")

    # OAuth handler is wired against the External Token API on the same host.
    auth = client._client.auth  # type: ignore[attr-defined]
    assert isinstance(auth, OAuth2ClientCredentialsAuth)
    assert (
        auth._token_url  # type: ignore[attr-defined]
        == "https://production.api.ipaustralia.gov.au/public/external-token-api/v1/access_token"
    )


def test_sandbox_environment_swaps_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IPAUSTRALIA_CLIENT_ID", "test-id")
    monkeypatch.setenv("IPAUSTRALIA_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("IPAUSTRALIA_ENV", "sandbox")

    client = IpAustraliaPatentsClient()
    assert client.environment == "sandbox"
    assert client.base_url.startswith("https://test.api.ipaustralia.gov.au")
