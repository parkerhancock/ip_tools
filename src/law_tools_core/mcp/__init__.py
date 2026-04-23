"""Shared MCP scaffolding for `ip-tools` and `law-tools`.

Consumers compose a FastMCP server via ``build_server()`` and register
domain-specific download fetchers via
``law_tools_core.mcp.downloads.register_source``.

Env vars (all optional; deployment-specific):
    LAW_TOOLS_CORE_API_KEY      bearer token + HMAC signing secret
    LAW_TOOLS_CORE_PUBLIC_URL   base URL for signed download links
    LAW_TOOLS_CORE_LOG_DIR      directory for tool-call JSONL logs
    LAW_TOOLS_CORE_DOWNLOAD_CACHE      on-disk cache dir for downloads
    LAW_TOOLS_CORE_DOWNLOAD_TTL_SECONDS HMAC rotation bucket (default 86400)

All variables accept a legacy ``LAW_TOOLS_*`` alias for backward
compatibility with pre-split law-tools deployments.
"""

from .annotations import DOWNLOAD, READ_ONLY
from .downloads import (
    build_download_url,
    build_download_url_or_fetch,
    download_response,
    handle_download,
    register_source,
    sign_path,
    verify_path,
)
from .middleware import BearerTokenAuth, FriendlyErrors, ToolCallLogger
from .server_factory import build_server

__all__ = [
    "BearerTokenAuth",
    "DOWNLOAD",
    "FriendlyErrors",
    "READ_ONLY",
    "ToolCallLogger",
    "build_download_url",
    "build_download_url_or_fetch",
    "build_server",
    "download_response",
    "handle_download",
    "register_source",
    "sign_path",
    "verify_path",
]
