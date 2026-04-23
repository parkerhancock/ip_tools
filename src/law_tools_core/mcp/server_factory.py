"""FastMCP server factory.

``build_server()`` returns a ``FastMCP`` instance with standard
middleware wired (friendly errors, bearer auth, tool-call logging) and
standard custom routes mounted (``/downloads/{path}``,
``/oauth/token``). Consumers then ``mcp.mount(sub_mcp)`` their
domain-specific tool servers and call ``mcp.run()``.

Both ``ip-tools`` and ``law-tools`` MCP servers sit on top of this.
"""

from __future__ import annotations

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import _env
from .downloads import handle_download
from .middleware import BearerTokenAuth, FriendlyErrors, ToolCallLogger


def build_server(name: str, instructions: str) -> FastMCP:
    """Build a FastMCP server with all standard middleware and routes.

    Args:
        name: Server name (shows up in MCP client UI).
        instructions: One-paragraph description passed to ``FastMCP(...)``.
    """
    mcp = FastMCP(name, instructions=instructions)

    # Outer-to-inner: FriendlyErrors wraps ToolCallLogger so the JSONL
    # log sees the raw exception type, not the remapped ToolError.
    mcp.add_middleware(BearerTokenAuth())
    mcp.add_middleware(FriendlyErrors())
    mcp.add_middleware(ToolCallLogger())

    @mcp.custom_route("/downloads/{path:path}", methods=["GET"])
    async def _downloads_route(request: Request):  # noqa: ANN202
        """Serve HMAC-signed document downloads."""
        return await handle_download(request)

    @mcp.custom_route("/oauth/token", methods=["POST"])
    async def _oauth_token(request: Request) -> JSONResponse:
        """OAuth2 client-credentials grant.

        Validates ``client_secret`` against ``LAW_TOOLS_CORE_API_KEY``
        and returns it as an access token. Lets OAuth2-only clients
        (e.g. CoWork) authenticate against the MCP server.
        """
        token = _env.get("API_KEY", "")
        if not token:
            return JSONResponse({"error": "server_error"}, status_code=500)

        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            data = dict(await request.form())
        else:
            data = await request.json()

        if data.get("grant_type") != "client_credentials":
            return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)

        if data.get("client_secret") != token:
            return JSONResponse({"error": "invalid_client"}, status_code=401)

        return JSONResponse({"access_token": token, "token_type": "bearer"})

    return mcp
