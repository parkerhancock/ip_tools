"""MCP resource exports for the KIPO KIPRIS Plus connector.

Stub: chunk 3 fills in the real usage-resource body (BYOK guidance, ToS
§11 redistribution caveats, dev-tier quota notes). For now this exposes
the URI the MCP layer will register so other modules can reference it
without circular imports.
"""

from __future__ import annotations

USAGE_RESOURCE_URI = "pca://kipo_kipris/usage"


def get_usage_resource() -> str:
    """Return the usage-resource text for the KIPRIS Plus connector.

    Stub body until chunk 3.
    """
    return "KIPRIS Plus connector — see research/specs/kr-kipo-connector-spec.md"


__all__ = ["USAGE_RESOURCE_URI", "get_usage_resource"]
