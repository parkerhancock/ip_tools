"""Smoke tests for the TIPO module-level helpers.

Each helper opens a context-managed ``TipoClient`` and delegates to
the matching client method. We mock ``TipoClient`` so these tests are
pure delegation contract checks — separate from the client-level
request/response tests in :mod:`test_client`.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

import patent_client_agents.tipo_opdata.api as api


@pytest.fixture
def mock_client(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patch ``TipoClient`` with an async-context AsyncMock and return the inner mock."""
    inner = AsyncMock()

    class _MockCtx:
        async def __aenter__(self) -> AsyncMock:
            return inner

        async def __aexit__(self, *exc: Any) -> None:
            return None

    def _factory(*args: Any, **kwargs: Any) -> _MockCtx:
        return _MockCtx()

    monkeypatch.setattr(api, "TipoClient", _factory)
    return inner


# ──────────────────────────────────────────────────────────────────────
# Patent helpers
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_tipo_patents_delegates(mock_client: AsyncMock) -> None:
    mock_client.search_patent_appl = AsyncMock(return_value=["x"])
    out = await api.search_tipo_patents(q="TSMC", applclass=1, top=10)
    assert out == ["x"]
    mock_client.search_patent_appl.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_delegates(mock_client: AsyncMock) -> None:
    mock_client.search_patent_appl = AsyncMock(return_value=["x"])
    out = await api.get_tipo_patent("112100001")
    assert out == ["x"]
    mock_client.search_patent_appl.assert_awaited_once_with(appl_no="112100001", top=100, skip=0)


@pytest.mark.asyncio
async def test_get_tipo_patent_publication_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_pub = AsyncMock(return_value=["p"])
    out = await api.get_tipo_patent_publication("A1")
    assert out == ["p"]
    mock_client.get_patent_pub.assert_awaited_once_with(appl_no="A1", top=100, skip=0)


@pytest.mark.asyncio
async def test_get_tipo_patent_rights_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_rights = AsyncMock(return_value=["r"])
    out = await api.get_tipo_patent_rights("A1")
    assert out == ["r"]
    mock_client.get_patent_rights.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_priority_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_priority = AsyncMock(return_value=[])
    await api.get_tipo_patent_priority("A1")
    mock_client.get_patent_priority.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_annuity_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_annuity = AsyncMock(return_value=[])
    await api.get_tipo_patent_annuity("A1")
    mock_client.get_patent_annuity.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_twins_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_twins = AsyncMock(return_value=[])
    await api.get_tipo_patent_twins("A1")
    mock_client.get_patent_twins.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_alteration_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_alteration = AsyncMock(return_value=[])
    await api.get_tipo_patent_alteration("A1")
    mock_client.get_patent_alteration.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_change_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_change = AsyncMock(return_value=[])
    await api.get_tipo_patent_change("A1")
    mock_client.get_patent_change.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_patent_divide_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_patent_divide = AsyncMock(return_value=[])
    await api.get_tipo_patent_divide("A1")
    mock_client.get_patent_divide.assert_awaited_once()


# ──────────────────────────────────────────────────────────────────────
# Trademark helpers
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_tipo_trademarks_delegates(mock_client: AsyncMock) -> None:
    mock_client.search_tmark_appl = AsyncMock(return_value=["t"])
    out = await api.search_tipo_trademarks(q="WAVE", tmark_class=9, top=20)
    assert out == ["t"]
    mock_client.search_tmark_appl.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_trademark_delegates(mock_client: AsyncMock) -> None:
    mock_client.search_tmark_appl = AsyncMock(return_value=[])
    await api.get_tipo_trademark("T1")
    mock_client.search_tmark_appl.assert_awaited_once_with(appl_no="T1", top=100, skip=0)


@pytest.mark.asyncio
async def test_get_tipo_trademark_rights_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_tmark_rights = AsyncMock(return_value=[])
    await api.get_tipo_trademark_rights("T1")
    mock_client.get_tmark_rights.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_trademark_priority_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_tmark_priority = AsyncMock(return_value=[])
    await api.get_tipo_trademark_priority("T1")
    mock_client.get_tmark_priority.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_trademark_image_urls_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_tmark_pics = AsyncMock(return_value=[])
    await api.get_tipo_trademark_image_urls("T1")
    mock_client.get_tmark_pics.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_trademark_change_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_tmark_change = AsyncMock(return_value=[])
    await api.get_tipo_trademark_change("T1")
    mock_client.get_tmark_change.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tipo_trademark_divide_delegates(mock_client: AsyncMock) -> None:
    mock_client.get_tmark_divide = AsyncMock(return_value=[])
    await api.get_tipo_trademark_divide("T1")
    mock_client.get_tmark_divide.assert_awaited_once()


# ──────────────────────────────────────────────────────────────────────
# resources.py — usage resource scaffolding
# ──────────────────────────────────────────────────────────────────────


def test_usage_resource_uri_is_namespaced() -> None:
    from patent_client_agents.tipo_opdata.resources import USAGE_RESOURCE_URI

    assert USAGE_RESOURCE_URI.startswith("pca://tipo_opdata/")


def test_get_usage_resource_returns_text() -> None:
    from patent_client_agents.tipo_opdata.resources import get_usage_resource

    body = get_usage_resource()
    assert isinstance(body, str)
    assert "TIPO" in body
