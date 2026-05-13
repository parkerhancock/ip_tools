"""Resource helpers for the WIPO Lex API."""

from __future__ import annotations

from importlib import resources

USAGE_RESOURCE_URI = "resource://wipo_lex/usage"


def get_usage_resource() -> str:
    return (
        resources.files("patent_client_agents.wipo_lex.docs")
        .joinpath("usage.md")
        .read_text(encoding="utf-8")
    )
