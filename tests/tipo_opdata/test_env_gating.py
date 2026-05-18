"""Tests for env-gated TIPO MCP tool registration.

Verifies that ``patent_client_agents.mcp.tools.tipo_opdata`` registers
the 14 TIPO tools only when ``TIPO_API_KEY`` is set.

Test strategy: each test ``importlib.reload``s the tipo_opdata module
under a controlled env, then inspects a fresh ``FastMCP`` instance to
see what got registered. We rebind ``tipo_opdata_mcp`` on the module
to a fresh server before reload so each ``@conditional_tool`` decorator
runs against an empty surface — that way the assertions are about
what *this reload* would have registered.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any, cast

import pytest
from fastmcp import FastMCP

# Names the chunk-3 surface registers — all 14 MCP tools.
EXPECTED_TIPO_TOOLS = {
    "search_tipo_patents",
    "get_tipo_patent",
    "get_tipo_patent_publication",
    "get_tipo_patent_rights",
    "get_tipo_patent_priority",
    "get_tipo_patent_annuity",
    "get_tipo_patent_twins",
    "get_tipo_patent_events",
    "search_tipo_trademarks",
    "get_tipo_trademark",
    "get_tipo_trademark_rights",
    "get_tipo_trademark_priority",
    "get_tipo_trademark_image_urls",
    "get_tipo_trademark_events",
}


def _reload_tipo_with_fresh_mcp() -> ModuleType:
    """Reload the tipo_opdata tool module under a fresh FastMCP."""
    import patent_client_agents.mcp.tools.tipo_opdata as tipo

    tipo.tipo_opdata_mcp = FastMCP("TIPO Taiwan — OpenData")
    return importlib.reload(tipo)


async def _list_tool_names(tipo_mod: ModuleType) -> set[str]:
    """Return the set of registered tool names on the fresh FastMCP."""
    mcp = cast("Any", tipo_mod).tipo_opdata_mcp
    tools = await mcp.list_tools()
    return {t.name for t in tools}


@pytest.fixture
def fresh_state(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    """Restore the conftest-managed env after each test by reloading once more."""
    yield
    # Reload one more time under the conftest's set env so subsequent
    # tests see the registered tools.
    _reload_tipo_with_fresh_mcp()


class TestTipoEnvGating:
    @pytest.mark.asyncio
    async def test_no_tools_registered_when_env_unset(
        self, monkeypatch: pytest.MonkeyPatch, fresh_state: None
    ) -> None:
        """With TIPO_API_KEY unset, zero TIPO tools register."""
        monkeypatch.delenv("TIPO_API_KEY", raising=False)

        tipo = _reload_tipo_with_fresh_mcp()

        names = await _list_tool_names(tipo)
        assert names & EXPECTED_TIPO_TOOLS == set()

    @pytest.mark.asyncio
    async def test_no_tools_registered_when_env_empty_string(
        self, monkeypatch: pytest.MonkeyPatch, fresh_state: None
    ) -> None:
        """Empty-string TIPO_API_KEY is treated as absent."""
        monkeypatch.setenv("TIPO_API_KEY", "")

        tipo = _reload_tipo_with_fresh_mcp()

        names = await _list_tool_names(tipo)
        assert names & EXPECTED_TIPO_TOOLS == set()

    @pytest.mark.asyncio
    async def test_all_tools_registered_when_env_set(
        self, monkeypatch: pytest.MonkeyPatch, fresh_state: None
    ) -> None:
        """With TIPO_API_KEY set, every TIPO tool registers."""
        monkeypatch.setenv("TIPO_API_KEY", "some-tk")

        tipo = _reload_tipo_with_fresh_mcp()

        names = await _list_tool_names(tipo)
        assert EXPECTED_TIPO_TOOLS <= names, f"missing tools: {EXPECTED_TIPO_TOOLS - names}"
