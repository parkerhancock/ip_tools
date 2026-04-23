"""Shared MCP tool annotations.

These dicts are passed to ``@mcp.tool(annotations=...)`` so MCP clients
can reason about side effects without parsing docstrings.
"""

# Data retrieval tools: query external APIs and return structured data.
# They do not modify any state.
READ_ONLY = {
    "readOnlyHint": True,
    "openWorldHint": True,
}

# Download tools read from external APIs but write to local cache / tempfile.
DOWNLOAD = {
    "readOnlyHint": False,
    "openWorldHint": True,
}
