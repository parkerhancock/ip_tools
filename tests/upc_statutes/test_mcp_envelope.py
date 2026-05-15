"""Envelope-shape tests for the migrated UPC statutes MCP tools.

Verifies CONNECTOR_STANDARDS.md §5.9 (envelope shape + Provenance, with
``corpus_version`` set for the ``mcp_local`` substantive-law corpus per
§4), §5.4 (list-accepting fetches), and §5.8 (vocab ``list_*``
enumerators returning ``ListEnvelope``).

Mocks the upstream UPC statutes client / API at the boundary so tests
don't require the SQLite corpus to be materialized.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from law_tools_core.envelope import ListEnvelope, Provenance
from law_tools_core.exceptions import ValidationError
from patent_client_agents.mcp.tools.upc import (
    get_upc_section,
    list_upc_instruments,
    search_upc_statutes,
)
from patent_client_agents.upc_statutes.models import (
    UpcInstrument,
    UpcInstrumentText,
    UpcStatuteSearchHit,
    UpcStatuteSearchResponse,
)


def _make_hit(
    instrument: str = "upca", *, snippet: str = "<mark>Article 33</mark> ..."
) -> UpcStatuteSearchHit:
    return UpcStatuteSearchHit(
        instrument=instrument,
        short_name="UPCA",
        language="en",
        snippet=snippet,
        rank=-1.5,
    )


def _make_instrument(
    instrument: str = "upca",
    *,
    short_name: str = "UPCA",
    title: str = "Agreement on a Unified Patent Court",
    language: str = "en",
    pages: int | None = 33,
) -> UpcInstrument:
    return UpcInstrument(
        instrument=instrument,
        short_name=short_name,
        title=title,
        language=language,
        source_url=f"https://example/{instrument}.pdf",
        source_version=None,
        pdf_pages=pages,
    )


def _make_instrument_text(instrument: str = "upca") -> UpcInstrumentText:
    base = _make_instrument(instrument)
    return UpcInstrumentText(
        **base.model_dump(),
        text=f"Full text of {instrument}...",
    )


# ──────────────────────────────────────────────────────────────────────
# search_upc_statutes — §5.9 envelope + corpus_version provenance
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_upc_statutes_returns_list_envelope_with_corpus_version():
    response = UpcStatuteSearchResponse(
        query="Article 33",
        hits=[_make_hit("upca"), _make_hit("rop")],
        page=1,
        per_page=10,
        has_more=False,
    )
    with patch("patent_client_agents.mcp.tools.upc.search") as mock_search:
        mock_search.return_value = response

        result = await search_upc_statutes(query="Article 33")

    assert isinstance(result, ListEnvelope)
    assert isinstance(result.provenance, Provenance)
    assert result.provenance.source_name == "Unified Patent Court"
    # mcp_local substantive-law corpus → corpus_version is stamped
    # (stub value per CONNECTOR_STANDARDS.md §8).
    assert result.provenance.corpus_version == "unknown — needs verification"
    assert len(result.items) == 2
    assert "Article 33" in result.summary
    assert result.more_available is False


@pytest.mark.asyncio
async def test_search_upc_statutes_more_available_when_has_more():
    response = UpcStatuteSearchResponse(
        query="opt-out",
        hits=[_make_hit("rop")],
        page=1,
        per_page=10,
        has_more=True,
    )
    with patch("patent_client_agents.mcp.tools.upc.search") as mock_search:
        mock_search.return_value = response

        result = await search_upc_statutes(query="opt-out")

    assert result.more_available is True


# ──────────────────────────────────────────────────────────────────────
# get_upc_section — §5.4 list-accepting, ListEnvelope shape
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_upc_section_single_returns_list_envelope():
    text = _make_instrument_text("upca")
    with patch("patent_client_agents.mcp.tools.upc.UpcStatutesClient") as mock_cls:
        mock_client = mock_cls.return_value.__aenter__.return_value
        mock_client.get_instrument = AsyncMock(return_value=text)

        result = await get_upc_section(instrument="upca")

    assert isinstance(result, ListEnvelope)
    assert len(result.items) == 1
    assert result.items[0]["instrument"] == "upca"
    assert "UPCA" in result.summary
    # corpus_* provenance is set for the mcp_local statutes corpus
    assert result.provenance.corpus_version == "unknown — needs verification"


@pytest.mark.asyncio
async def test_get_upc_section_list_preserves_order():
    keys = ["upca", "rop", "fees"]
    texts = [_make_instrument_text(k) for k in keys]
    with patch("patent_client_agents.mcp.tools.upc.UpcStatutesClient") as mock_cls:
        mock_client = mock_cls.return_value.__aenter__.return_value
        mock_client.get_instrument = AsyncMock(side_effect=texts)

        result = await get_upc_section(instrument=keys)

    assert [r["instrument"] for r in result.items] == keys
    assert "3 of 3" in result.summary


@pytest.mark.asyncio
async def test_get_upc_section_empty_list_raises():
    with pytest.raises(ValidationError, match="at least one"):
        await get_upc_section(instrument=[])


# ──────────────────────────────────────────────────────────────────────
# list_upc_instruments — §5.8 vocab enumerator
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_upc_instruments_returns_list_envelope():
    instruments = [_make_instrument("upca"), _make_instrument("rop", short_name="RoP")]
    with patch("patent_client_agents.mcp.tools.upc.list_instruments") as mock_list:
        mock_list.return_value = instruments

        result = await list_upc_instruments()

    assert isinstance(result, ListEnvelope)
    assert result.provenance.source_name == "Unified Patent Court"
    # mcp_local → corpus_version is stamped
    assert result.provenance.corpus_version == "unknown — needs verification"
    assert len(result.items) == 2
    assert "2 entries" in result.summary
