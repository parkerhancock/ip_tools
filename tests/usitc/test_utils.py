"""Tests for USITC utility functions."""

from __future__ import annotations

import pytest

from patent_client_agents.usitc.utils import (
    DATAWEB_BASE_URL,
    EDIS_BASE_URL,
    HTS_BASE_URL,
    IDS_URL,
    coerce_bool,
    get_env_token,
    normalize_params,
)


class TestGetEnvToken:
    """Tests for get_env_token function."""

    def test_returns_token_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TEST_TOKEN", "my_token_123")
        result = get_env_token("TEST_TOKEN")
        assert result == "my_token_123"

    def test_strips_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TEST_TOKEN", "  token_with_spaces  ")
        result = get_env_token("TEST_TOKEN")
        assert result == "token_with_spaces"

    def test_returns_none_for_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MISSING_TOKEN", raising=False)
        result = get_env_token("MISSING_TOKEN")
        assert result is None


class TestCoerceBool:
    """Tests for coerce_bool function."""

    def test_true_values(self) -> None:
        assert coerce_bool("true") is True
        assert coerce_bool("True") is True
        assert coerce_bool("TRUE") is True
        assert coerce_bool("1") is True
        assert coerce_bool("yes") is True

    def test_false_values(self) -> None:
        assert coerce_bool("false") is False
        assert coerce_bool("False") is False
        assert coerce_bool("FALSE") is False
        assert coerce_bool("0") is False
        assert coerce_bool("no") is False

    def test_none_values(self) -> None:
        assert coerce_bool(None) is None
        assert coerce_bool("invalid") is None
        assert coerce_bool("maybe") is None

    def test_bool_passthrough(self) -> None:
        assert coerce_bool(True) is True
        assert coerce_bool(False) is False

    def test_strips_whitespace(self) -> None:
        assert coerce_bool("  true  ") is True
        assert coerce_bool("  false  ") is False


class TestNormalizeParams:
    """Tests for normalize_params function."""

    def test_removes_none_values(self) -> None:
        result = normalize_params({"a": 1, "b": None, "c": "value"})
        assert result == {"a": 1, "c": "value"}

    def test_removes_empty_strings(self) -> None:
        result = normalize_params({"a": 1, "b": "", "c": "value"})
        assert result == {"a": 1, "c": "value"}

    def test_keeps_other_falsy_values(self) -> None:
        result = normalize_params({"a": 0, "b": False})
        assert result == {"a": 0, "b": False}

    def test_handles_empty_dict(self) -> None:
        result = normalize_params({})
        assert result == {}


class TestBaseUrls:
    """Tests for base URL constants."""

    def test_edis_base_url(self) -> None:
        assert "edis.usitc.gov" in EDIS_BASE_URL

    def test_dataweb_base_url(self) -> None:
        assert "usitc.gov" in DATAWEB_BASE_URL

    def test_ids_url(self) -> None:
        assert "ids.usitc.gov" in IDS_URL
        assert ".json" in IDS_URL

    def test_hts_base_url(self) -> None:
        assert "hts.usitc.gov" in HTS_BASE_URL
