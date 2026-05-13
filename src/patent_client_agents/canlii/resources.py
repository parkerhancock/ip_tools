"""Resource helpers for the CanLII shared API."""

from __future__ import annotations

from importlib import resources

USAGE_RESOURCE_URI = "resource://canlii/usage"


def get_usage_resource() -> str:
    return (
        resources.files("patent_client_agents.canlii.docs")
        .joinpath("usage.md")
        .read_text(encoding="utf-8")
    )
