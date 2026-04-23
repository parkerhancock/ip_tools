"""Tests for law_tools_core/mcp/downloads.py."""

from __future__ import annotations

import os

import pytest

from law_tools_core.mcp import downloads


@pytest.fixture(autouse=True)
def _reset_sources():
    """Clear the source registry between tests so they don't leak state."""
    saved = dict(downloads._SOURCES)
    downloads._SOURCES.clear()
    yield
    downloads._SOURCES.clear()
    downloads._SOURCES.update(saved)


@pytest.fixture
def _signing_secret(monkeypatch):
    monkeypatch.setenv("LAW_TOOLS_CORE_API_KEY", "test-secret")
    yield


class TestHmac:
    def test_sign_verify_roundtrip(self, _signing_secret) -> None:
        path = "patents/US10123456B2"
        assert downloads.verify_path(path, downloads.sign_path(path))

    def test_wrong_signature_rejected(self, _signing_secret) -> None:
        assert not downloads.verify_path("patents/X", "wrongsig")

    def test_no_secret_allows_all(self, monkeypatch) -> None:
        monkeypatch.delenv("LAW_TOOLS_CORE_API_KEY", raising=False)
        monkeypatch.delenv("LAW_TOOLS_API_KEY", raising=False)
        assert downloads.verify_path("anything", "bogus")

    def test_permanent_bucket(self, _signing_secret) -> None:
        path = "patents/X"
        sig = downloads.sign_path(path, bucket="permanent")
        assert downloads.verify_path(path, sig)

    def test_legacy_env_var_alias(self, monkeypatch) -> None:
        """Legacy LAW_TOOLS_API_KEY should still work."""
        monkeypatch.delenv("LAW_TOOLS_CORE_API_KEY", raising=False)
        monkeypatch.setenv("LAW_TOOLS_API_KEY", "legacy-secret")
        path = "patents/X"
        assert downloads.verify_path(path, downloads.sign_path(path))


class TestRegistry:
    def test_register_and_match(self) -> None:
        async def fetch(_remainder: str) -> tuple[bytes, str]:
            return b"", "f.pdf"

        downloads.register_source("patents", fetch)
        match = downloads._match_source("patents/US10123456B2")
        assert match is not None
        _, remainder = match
        assert remainder == "US10123456B2"

    def test_longest_prefix_wins(self) -> None:
        async def short(_: str) -> tuple[bytes, str]:
            return b"short", "s.pdf"

        async def long(_: str) -> tuple[bytes, str]:
            return b"long", "l.pdf"

        downloads.register_source("uspto", short)
        downloads.register_source("uspto/applications", long)

        match = downloads._match_source("uspto/applications/16123456/x")
        assert match is not None
        source, _ = match
        assert source.fetch is long

    def test_unknown_path_returns_none(self) -> None:
        assert downloads._match_source("unknown/path") is None


class TestBuildDownloadUrl:
    def test_local_mode_returns_stub(self, monkeypatch) -> None:
        monkeypatch.delenv("LAW_TOOLS_CORE_PUBLIC_URL", raising=False)
        monkeypatch.delenv("LAW_TOOLS_PUBLIC_URL", raising=False)
        result = downloads.build_download_url("patents/X")
        assert "local mode" in result.lower()

    def test_remote_mode_signs_url(self, monkeypatch) -> None:
        monkeypatch.setenv("LAW_TOOLS_CORE_API_KEY", "secret")
        monkeypatch.setenv("LAW_TOOLS_CORE_PUBLIC_URL", "https://mcp.example.com")
        url = downloads.build_download_url("patents/X")
        assert url.startswith("https://mcp.example.com/downloads/patents/X?key=")

    def test_label_prepended(self, monkeypatch) -> None:
        monkeypatch.setenv("LAW_TOOLS_CORE_API_KEY", "secret")
        monkeypatch.setenv("LAW_TOOLS_CORE_PUBLIC_URL", "https://mcp.example.com")
        out = downloads.build_download_url("patents/X", label="Patent PDF")
        assert out.startswith("Patent PDF\n\nDownload:")


class TestDownloadResponse:
    def test_local_mode_writes_tempfile(self, tmp_path, monkeypatch) -> None:
        monkeypatch.delenv("LAW_TOOLS_CORE_PUBLIC_URL", raising=False)
        monkeypatch.delenv("LAW_TOOLS_PUBLIC_URL", raising=False)
        payload = downloads.download_response(
            "patents/X",
            b"bytes",
            filename="X.pdf",
            content_type="application/pdf",
        )
        assert "file_path" in payload
        assert os.path.exists(payload["file_path"])
        assert payload["size_bytes"] == 5
        assert payload["filename"] == "X.pdf"

    def test_remote_mode_returns_signed_url_and_expires_at(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setenv("LAW_TOOLS_CORE_API_KEY", "secret")
        monkeypatch.setenv("LAW_TOOLS_CORE_PUBLIC_URL", "https://mcp.example.com")
        monkeypatch.setenv("LAW_TOOLS_CORE_DOWNLOAD_CACHE", str(tmp_path))
        payload = downloads.download_response(
            "patents/X",
            b"bytes",
            filename="X.pdf",
        )
        assert payload["download_url"].startswith("https://mcp.example.com/")
        assert "expires_at" in payload
        assert "Z" in payload["expires_at"]

    def test_permanent_url_omits_expires_at(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setenv("LAW_TOOLS_CORE_API_KEY", "secret")
        monkeypatch.setenv("LAW_TOOLS_CORE_PUBLIC_URL", "https://mcp.example.com")
        monkeypatch.setenv("LAW_TOOLS_CORE_DOWNLOAD_CACHE", str(tmp_path))
        payload = downloads.download_response(
            "patents/X",
            b"bytes",
            filename="X.pdf",
            permanent=True,
        )
        assert "expires_at" not in payload
