"""Tests for ``law_tools_core.mcp.conditional``.

Verifies the env-gate semantics for ``conditional_tool`` and the
parallel ``register_source_if_configured`` helper.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from law_tools_core.mcp import conditional_tool, downloads, register_source_if_configured
from law_tools_core.mcp.annotations import READ_ONLY


@pytest.fixture(autouse=True)
def _reset_sources():
    """Clear the source registry between tests so they don't leak state."""
    saved = dict(downloads._SOURCES)
    downloads._SOURCES.clear()
    yield
    downloads._SOURCES.clear()
    downloads._SOURCES.update(saved)


@pytest.fixture
def fresh_mcp() -> FastMCP:
    """A new FastMCP instance with no tools registered."""
    return FastMCP("test-server")


# ---------------------------------------------------------------------------
# conditional_tool
# ---------------------------------------------------------------------------


class TestConditionalTool:
    @pytest.mark.asyncio
    async def test_env_present_registers(
        self, fresh_mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.setenv("MY_PASS", "secret")

        @conditional_tool(fresh_mcp, requires_env=["MY_USER", "MY_PASS"])
        async def gated_tool() -> dict:
            return {"ok": True}

        tool_names = {t.name for t in await fresh_mcp.list_tools()}
        assert "gated_tool" in tool_names
        # Function still callable directly.
        assert await gated_tool() == {"ok": True}

    @pytest.mark.asyncio
    async def test_env_absent_does_not_register(
        self, fresh_mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MY_USER", raising=False)
        monkeypatch.delenv("MY_PASS", raising=False)

        @conditional_tool(fresh_mcp, requires_env=["MY_USER", "MY_PASS"])
        async def gated_tool() -> dict:
            return {"ok": True}

        tool_names = {t.name for t in await fresh_mcp.list_tools()}
        assert "gated_tool" not in tool_names
        # The Python function is still callable from skill / library code.
        assert await gated_tool() == {"ok": True}

    @pytest.mark.asyncio
    async def test_env_partial_does_not_register(
        self, fresh_mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Only one of the two required vars is set — must be treated as absent.
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.delenv("MY_PASS", raising=False)

        @conditional_tool(fresh_mcp, requires_env=["MY_USER", "MY_PASS"])
        async def gated_tool() -> dict:
            return {"ok": True}

        tool_names = {t.name for t in await fresh_mcp.list_tools()}
        assert "gated_tool" not in tool_names

    @pytest.mark.asyncio
    async def test_env_empty_string_treated_as_absent(
        self, fresh_mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # An env var set to "" is a frequent footgun in shell scripts;
        # treat it the same as unset.
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.setenv("MY_PASS", "")

        @conditional_tool(fresh_mcp, requires_env=["MY_USER", "MY_PASS"])
        async def gated_tool() -> dict:
            return {"ok": True}

        tool_names = {t.name for t in await fresh_mcp.list_tools()}
        assert "gated_tool" not in tool_names

    @pytest.mark.asyncio
    async def test_forwards_tool_kwargs(
        self, fresh_mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.setenv("MY_PASS", "secret")

        @conditional_tool(
            fresh_mcp,
            requires_env=["MY_USER", "MY_PASS"],
            annotations=READ_ONLY,
        )
        async def gated_tool() -> dict:
            return {"ok": True}

        tools = {t.name: t for t in await fresh_mcp.list_tools()}
        assert "gated_tool" in tools
        registered = tools["gated_tool"]
        # FastMCP normalizes annotations into a ToolAnnotations object;
        # readOnlyHint=True should round-trip through.
        assert getattr(registered.annotations, "readOnlyHint", None) is True


# ---------------------------------------------------------------------------
# register_source_if_configured
# ---------------------------------------------------------------------------


async def _dummy_fetcher(path: str) -> tuple[bytes, str]:
    return b"content", "file.zip"


class TestRegisterSourceIfConfigured:
    def test_env_present_registers_source(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.setenv("MY_PASS", "secret")

        register_source_if_configured(
            "test/source",
            _dummy_fetcher,
            "application/zip",
            requires_env=["MY_USER", "MY_PASS"],
        )

        assert "test/source" in downloads._SOURCES
        assert downloads._SOURCES["test/source"].mime_type == "application/zip"

    def test_env_absent_skips_registration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MY_USER", raising=False)
        monkeypatch.delenv("MY_PASS", raising=False)

        register_source_if_configured(
            "test/source",
            _dummy_fetcher,
            "application/zip",
            requires_env=["MY_USER", "MY_PASS"],
        )

        assert "test/source" not in downloads._SOURCES

    def test_env_partial_skips_registration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.delenv("MY_PASS", raising=False)

        register_source_if_configured(
            "test/source",
            _dummy_fetcher,
            "application/zip",
            requires_env=["MY_USER", "MY_PASS"],
        )

        assert "test/source" not in downloads._SOURCES

    def test_env_empty_string_skips_registration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_USER", "alice")
        monkeypatch.setenv("MY_PASS", "")

        register_source_if_configured(
            "test/source",
            _dummy_fetcher,
            "application/zip",
            requires_env=["MY_USER", "MY_PASS"],
        )

        assert "test/source" not in downloads._SOURCES
