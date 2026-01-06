"""Core module tests for ip_tools."""

from __future__ import annotations

import pytest

from ip_tools.core.base_client import BaseAsyncClient
from ip_tools.core.exceptions import IpToolsError


class TestIpToolsError:
    """Tests for IpToolsError exception."""

    def test_can_raise_ip_tools_error(self) -> None:
        """Verify IpToolsError can be raised and caught."""
        with pytest.raises(IpToolsError):
            raise IpToolsError("test error")

    def test_error_message_preserved(self) -> None:
        """Verify error message is preserved."""
        try:
            raise IpToolsError("custom message")
        except IpToolsError as e:
            assert str(e) == "custom message"


class TestBaseAsyncClient:
    """Tests for BaseAsyncClient."""

    def test_can_instantiate(self) -> None:
        """Verify BaseAsyncClient can be instantiated."""
        client = BaseAsyncClient(base_url="https://example.com")
        assert client.base_url == "https://example.com"

    def test_default_values(self) -> None:
        """Verify default attribute values."""
        client = BaseAsyncClient()
        assert client.base_url == ""
        assert client._max_retries == 4
        assert client._owns_client is True

    def test_base_url_trailing_slash_stripped(self) -> None:
        """Verify trailing slash is stripped from base_url."""
        client = BaseAsyncClient(base_url="https://example.com/")
        assert client.base_url == "https://example.com"
