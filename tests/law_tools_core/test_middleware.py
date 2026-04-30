"""Tests for the tool-call logger configuration in law_tools_core.mcp.middleware."""

from __future__ import annotations

import importlib
import json
import logging
import sys
from logging.handlers import RotatingFileHandler

import pytest


@pytest.fixture
def fresh_middleware(monkeypatch, tmp_path):
    """Reload the middleware module with a clean logger between tests.

    The module attaches handlers to a process-level logger
    (``law_tools_core.mcp.tools``); reloading + clearing handlers before
    each test gives an isolated configuration call.
    """
    # Clear any LOG_DIR / LOG_TO_STDOUT inherited from the host environment
    for var in (
        "LAW_TOOLS_CORE_LOG_DIR",
        "LAW_TOOLS_LOG_DIR",
        "LAW_TOOLS_CORE_LOG_TO_STDOUT",
        "LAW_TOOLS_LOG_TO_STDOUT",
    ):
        monkeypatch.delenv(var, raising=False)

    from law_tools_core.mcp import middleware

    importlib.reload(middleware)
    middleware._tool_logger.handlers.clear()
    yield middleware
    middleware._tool_logger.handlers.clear()


def test_no_handlers_when_no_env(fresh_middleware) -> None:
    """With neither env var set, no handler is attached and logging is a no-op."""
    fresh_middleware._configure_tool_logger()
    assert fresh_middleware._tool_logger.handlers == []


def test_file_handler_when_log_dir_set(monkeypatch, tmp_path, fresh_middleware) -> None:
    """LAW_TOOLS_CORE_LOG_DIR attaches a rotating file handler."""
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_DIR", str(tmp_path))
    fresh_middleware._configure_tool_logger()
    handlers = fresh_middleware._tool_logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], RotatingFileHandler)
    assert str(handlers[0].baseFilename).endswith("tool_calls.jsonl")


def test_stdout_handler_when_log_to_stdout_set(monkeypatch, fresh_middleware) -> None:
    """LAW_TOOLS_CORE_LOG_TO_STDOUT=true attaches a StreamHandler to sys.stdout."""
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_TO_STDOUT", "true")
    fresh_middleware._configure_tool_logger()
    handlers = fresh_middleware._tool_logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert handlers[0].stream is sys.stdout


def test_both_handlers_when_both_set(monkeypatch, tmp_path, fresh_middleware) -> None:
    """Both env vars set → both handlers attached."""
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_TO_STDOUT", "1")
    fresh_middleware._configure_tool_logger()
    handlers = fresh_middleware._tool_logger.handlers
    assert len(handlers) == 2


def test_stdout_handler_emits_json(monkeypatch, capsys, fresh_middleware) -> None:
    """Records logged through the configured logger reach stdout as one JSON line."""
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_TO_STDOUT", "yes")
    fresh_middleware._configure_tool_logger()
    fresh_middleware._tool_logger.info(json.dumps({"tool": "test_tool", "ok": True}))
    captured = capsys.readouterr()
    assert json.loads(captured.out.strip()) == {"tool": "test_tool", "ok": True}


def test_idempotent_configure(monkeypatch, fresh_middleware) -> None:
    """Calling _configure_tool_logger twice attaches handlers only once."""
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_TO_STDOUT", "true")
    fresh_middleware._configure_tool_logger()
    fresh_middleware._configure_tool_logger()
    assert len(fresh_middleware._tool_logger.handlers) == 1


@pytest.mark.parametrize("falsy", ["false", "FALSE", "0", "no", "off", ""])
def test_log_to_stdout_falsy_values_dont_attach(monkeypatch, falsy, fresh_middleware) -> None:
    """Falsy values for LOG_TO_STDOUT do not attach a stdout handler."""
    monkeypatch.setenv("LAW_TOOLS_CORE_LOG_TO_STDOUT", falsy)
    fresh_middleware._configure_tool_logger()
    assert fresh_middleware._tool_logger.handlers == []
