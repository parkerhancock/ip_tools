"""Resource helpers for the UPC statutes corpus."""

from __future__ import annotations

from importlib import resources

USAGE_RESOURCE_URI = "resource://upc_statutes/usage"


def get_usage_resource() -> str:
    return (
        resources.files("patent_client_agents.upc_statutes.docs")
        .joinpath("usage.md")
        .read_text(encoding="utf-8")
    )
