"""Tests for the module-level async API and Pydantic Input models."""

from __future__ import annotations

import pytest

from patent_client_agents.ipo_in_statutes import (
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
def _set_corpus(ipo_in_statutes_corpus_path, monkeypatch):
    monkeypatch.setenv("IPO_IN_STATUTES_CORPUS_PATH", str(ipo_in_statutes_corpus_path))


async def test_search_oneshot() -> None:
    r = await search(StatuteSearchInput(query="fair dealing"))
    assert r.hits


async def test_get_section_oneshot_input_model() -> None:
    sec = await get_section(SectionInput(section_number="3(d)", statute_name="Patents Act"))
    assert sec.section_number == "3(d)"
    assert sec.statute_name == "Patents Act"


async def test_get_section_oneshot_string() -> None:
    sec = await get_section("107A")
    assert sec.section_number == "107A"


async def test_get_section_by_citation_oneshot() -> None:
    sec = await get_section_by_citation("Section 84 Patents Act")
    assert sec.title is not None
    assert "compulsory" in sec.title.lower()


async def test_list_statutes_oneshot() -> None:
    statutes = await list_statutes()
    assert len(statutes) >= 4


def test_usage_resource() -> None:
    assert USAGE_RESOURCE_URI.startswith("resource://")
    body = get_usage_resource()
    assert "Patents Act, 1970" in body
    assert "Section 3(d)" in body


def test_get_client_returns_client() -> None:
    client = get_client()
    assert client.__class__.__name__ == "IpoInStatutesClient"
