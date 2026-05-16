"""Tests for the module-level async API and Pydantic Input models."""

from __future__ import annotations

import pytest

from patent_client_agents.tw_trade_secrets import (
    USAGE_RESOURCE_URI,
    SearchInput,
    SectionInput,
    get_client,
    get_section,
    get_section_by_citation,
    get_usage_resource,
    search,
)


@pytest.fixture(autouse=True)
def _set_corpus(tw_trade_secrets_corpus_path, monkeypatch):
    monkeypatch.setenv("TW_TRADE_SECRETS_CORPUS_PATH", str(tw_trade_secrets_corpus_path))


async def test_search_oneshot() -> None:
    r = await search(SearchInput(query="damages"))
    assert r.hits


async def test_get_section_oneshot_input_model() -> None:
    sec = await get_section(SectionInput(section="2"))
    assert sec.section == "2"
    assert "trade secret" in sec.text.lower()


async def test_get_section_oneshot_string() -> None:
    sec = await get_section("13-1")
    assert sec.section == "13-1"
    assert sec.title == "Criminal Liability"


async def test_get_section_by_citation_oneshot() -> None:
    sec = await get_section_by_citation("Art. 13-1 Trade Secrets Act")
    assert sec.section == "13-1"
    assert sec.title is not None


def test_usage_resource() -> None:
    assert USAGE_RESOURCE_URI.startswith("resource://")
    body = get_usage_resource()
    assert "Trade Secrets Act" in body
    assert "Art. 13-1" in body


def test_get_client_returns_client() -> None:
    client = get_client()
    assert client.__class__.__name__ == "TwTradeSecretsClient"
