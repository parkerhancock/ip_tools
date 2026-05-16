"""Tests for the module-level async API."""

from __future__ import annotations

import pytest

from patent_client_agents.ipo_in_mppp import (
    USAGE_RESOURCE_URI,
    MpppSearchInput,
    MpppSectionInput,
    get_client,
    get_section,
    get_usage_resource,
    search,
)


@pytest.fixture(autouse=True)
def _set_corpus(ipo_in_mppp_corpus_path, monkeypatch):
    monkeypatch.setenv("IPO_IN_MPPP_CORPUS_PATH", str(ipo_in_mppp_corpus_path))


async def test_search_oneshot() -> None:
    r = await search(MpppSearchInput(query="first examination report"))
    assert r.hits


async def test_get_section_string() -> None:
    sec = await get_section("04.05.01")
    assert sec.section_number == "04.05.01"


async def test_get_section_input_model() -> None:
    sec = await get_section(MpppSectionInput(section_reference="Chapter 04.05.01"))
    assert sec.section_number == "04.05.01"


def test_get_client() -> None:
    c = get_client()
    assert c.__class__.__name__ == "MpppClient"


def test_usage_resource() -> None:
    assert USAGE_RESOURCE_URI.startswith("resource://")
    body = get_usage_resource()
    assert "MPPP" in body
    assert "Chapter" in body
