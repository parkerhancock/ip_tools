"""Tests for Google Patents client."""

from __future__ import annotations

import pytest

from ip_tools.google_patents.client import GooglePatentsClient, PatentData


class TestGooglePatentsImports:
    """Test that Google Patents module imports work correctly."""

    def test_import_client(self) -> None:
        """Verify GooglePatentsClient can be imported."""
        assert GooglePatentsClient is not None

    def test_import_patent_data(self) -> None:
        """Verify PatentData model can be imported."""
        assert PatentData is not None


@pytest.fixture
def google_patents_client() -> GooglePatentsClient:
    """Create a GooglePatentsClient instance for testing."""
    return GooglePatentsClient(use_cache=False)


class TestGooglePatentsClient:
    """Tests for GooglePatentsClient."""

    def test_client_instantiation(self, google_patents_client: GooglePatentsClient) -> None:
        """Verify client can be instantiated via fixture."""
        assert google_patents_client is not None
        assert google_patents_client._use_cache is False

    def test_client_default_cache(self) -> None:
        """Verify default cache setting is True."""
        client = GooglePatentsClient()
        assert client._use_cache is True
