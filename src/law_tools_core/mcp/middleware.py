"""FastMCP middleware: friendly errors, bearer auth, and tool-call logging.

Install order matters. ``FriendlyErrors`` must sit outer of
``ToolCallLogger`` so the JSONL log records the original exception type
(e.g. ``httpx.ReadError``) rather than the remapped ``ToolError``.
"""

from __future__ import annotations

import json
import logging
import time
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from law_tools_core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    LawToolsCoreError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

from . import _env

# ---------------------------------------------------------------------------
# FriendlyErrors
# ---------------------------------------------------------------------------

_friendly_logger = logging.getLogger(__name__ + ".friendly")

RETRYABLE = "[retryable]"
NOT_RETRYABLE = "[not-retryable]"


def _friendly_message(tool_name: str, exc: BaseException) -> str | None:
    """Map an exception to a clean client-facing message, or None to pass through."""
    if isinstance(exc, (httpx.ReadError, httpx.ConnectError, httpx.RemoteProtocolError)):
        return (
            f"{RETRYABLE} Upstream service dropped the connection while "
            f"handling {tool_name}. This is usually transient — please retry."
        )
    if isinstance(exc, httpx.TimeoutException):
        return (
            f"{RETRYABLE} Upstream service timed out while handling {tool_name}. "
            f"Retry, or narrow the request if possible."
        )
    if isinstance(exc, RateLimitError):
        return f"{RETRYABLE} Rate limited by upstream: {exc}"
    if isinstance(exc, ServerError):
        return f"{RETRYABLE} Upstream server error: {exc}"
    if isinstance(exc, NotFoundError):
        return f"{NOT_RETRYABLE} Not found: {exc}"
    if isinstance(exc, AuthenticationError):
        return f"{NOT_RETRYABLE} Authentication failed for upstream service."
    if isinstance(exc, ConfigurationError):
        return f"{NOT_RETRYABLE} Server misconfiguration: {exc}"
    if isinstance(exc, LawToolsCoreError):
        return f"{NOT_RETRYABLE} {exc}"
    return None


class FriendlyErrors(Middleware):
    """Remap transport/typed errors to clean ToolError messages."""

    async def on_call_tool(self, context, call_next):  # noqa: ANN001
        tool_name = getattr(context.message, "name", "unknown_tool")
        try:
            return await call_next(context)
        except ToolError:
            raise
        except Exception as exc:
            message = _friendly_message(tool_name, exc)
            if message is None:
                raise
            _friendly_logger.warning(
                "Remapping %s from %s: %s",
                tool_name,
                type(exc).__name__,
                exc,
                exc_info=exc,
            )
            raise ToolError(message) from exc


# ---------------------------------------------------------------------------
# BearerTokenAuth
# ---------------------------------------------------------------------------


class BearerTokenAuth(Middleware):
    """Reject requests without a valid bearer token.

    Reads the expected token from ``LAW_TOOLS_CORE_API_KEY`` (or the
    legacy ``LAW_TOOLS_API_KEY`` alias). If the variable is not set,
    all requests are allowed (local/stdio mode).
    """

    def __init__(self) -> None:
        self._token = _env.get("API_KEY", "")

    async def on_call_tool(self, context: MiddlewareContext, call_next):  # noqa: ANN001
        if self._token and not self._check_auth(context):
            raise ToolError("Unauthorized: invalid or missing bearer token")
        return await call_next(context)

    def _check_auth(self, context: MiddlewareContext) -> bool:
        # FastMCP exposes transport headers via context.request
        # when running over HTTP. For stdio, headers are absent.
        request = getattr(context, "request", None)
        if request is None:
            return True  # stdio — no auth needed
        headers = getattr(request, "headers", {})
        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:] == self._token
        return False


# ---------------------------------------------------------------------------
# ToolCallLogger
# ---------------------------------------------------------------------------

_tool_logger = logging.getLogger("law_tools_core.mcp.tools")
_tool_logger.setLevel(logging.INFO)
_tool_logger.propagate = False


def _configure_tool_logger() -> None:
    """Attach a rotating file handler when LAW_TOOLS_CORE_LOG_DIR is set.

    Safe to call multiple times — a handler is added at most once.
    """
    if _tool_logger.handlers:
        return
    log_dir = _env.get("LOG_DIR")
    if not log_dir:
        return
    path = Path(log_dir)
    if not path.exists() and not log_dir:
        return
    path.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        path / "tool_calls.jsonl",
        maxBytes=50 * 1024 * 1024,  # 50 MB
        backupCount=5,
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    _tool_logger.addHandler(handler)


class ToolCallLogger(Middleware):
    """Log every tool call as a JSON line: tool name, duration, success/error."""

    def __init__(self) -> None:
        _configure_tool_logger()

    async def on_call_tool(self, context, call_next):  # noqa: ANN001
        params = context.message
        tool_name = params.name
        t0 = time.monotonic()
        error_msg = None
        error_tb = None
        try:
            result = await call_next(context)
            return result
        except Exception as exc:
            error_msg = f"{type(exc).__name__}: {exc}"
            error_tb = traceback.format_exc()
            raise
        finally:
            duration_ms = round((time.monotonic() - t0) * 1000, 1)
            record = {
                "ts": context.timestamp.isoformat(),
                "tool": tool_name,
                "duration_ms": duration_ms,
                "ok": error_msg is None,
            }
            if error_msg:
                record["error"] = error_msg
                record["traceback"] = error_tb
            _tool_logger.info(json.dumps(record, default=str))
