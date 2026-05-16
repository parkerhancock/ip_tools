"""Tests for the module-level async API and Pydantic Input models."""

from __future__ import annotations

import pytest

from patent_client_agents.dpma_statutes import (
    USAGE_RESOURCE_URI,
    SectionInput,
    StatuteSearchInput,
    get_client,
    get_section,
    get_section_by_citation,
    get_usage_resource,
    list_statutes,
    search,
)


@pytest.fixture(autouse=True)
def _set_corpus(dpma_statutes_corpus_path, monkeypatch):
    monkeypatch.setenv("DPMA_STATUTES_CORPUS_PATH", str(dpma_statutes_corpus_path))


async def test_search_oneshot() -> None:
    r = await search(StatuteSearchInput(query="Patent"))
    assert r.hits


async def test_search_with_statute_filter() -> None:
    r = await search(StatuteSearchInput(query="Markenschutz", statute="MarkenG"))
    for hit in r.hits:
        assert hit.statute == "MarkenG"


async def test_get_section_oneshot_input_model() -> None:
    sec = await get_section(SectionInput(section="139", statute="PatG"))
    assert sec.section == "139"
    assert sec.statute == "PatG"


async def test_get_section_oneshot_string() -> None:
    # Section 139 is unique to PatG in the seed
    sec = await get_section("139")
    assert sec.section == "139"
    assert sec.statute == "PatG"


async def test_get_section_by_citation_oneshot() -> None:
    sec = await get_section_by_citation("§ 139 PatG")
    assert sec.title is not None
    assert "Unterlassung" in sec.title


async def test_list_statutes_oneshot() -> None:
    statutes = await list_statutes()
    # Seed covers all six bundled Acts
    assert {"PatG", "MarkenG", "GebrMG", "DesignG", "UrhG", "GeschGehG"} <= set(statutes)


def test_usage_resource() -> None:
    assert USAGE_RESOURCE_URI.startswith("resource://")
    body = get_usage_resource()
    assert "PatG" in body
    assert "§ 139 PatG" in body
    assert "GeschGehG" in body


def test_get_client_returns_client() -> None:
    client = get_client()
    assert client.__class__.__name__ == "DpmaStatutesClient"
