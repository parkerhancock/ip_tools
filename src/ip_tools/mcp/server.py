"""Standalone ip-tools MCP server entry point.

Run via the ``ip-tools-mcp`` console script (installed by the
``[mcp]`` extra), or directly::

    python -m ip_tools.mcp.server
    fastmcp run ip_tools.mcp.server:mcp

Stdio is the default transport. Pass ``--transport http`` (or use
``fastmcp run``) for HTTP mode.
"""

from __future__ import annotations

from law_tools_core.mcp.server_factory import build_server

from . import ip_mcp

mcp = build_server(
    name="ip-tools",
    instructions=(
        "Patent and IP data connectors: USPTO (ODP, PPUBS, Assignments, "
        "Office Actions, PTAB, Petitions, Bulk Data), EPO OPS, Google "
        "Patents, CPC, and the MPEP."
    ),
)
mcp.mount(ip_mcp)


def main() -> None:
    """Entry point for the ``ip-tools-mcp`` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
