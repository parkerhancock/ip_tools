"""Async API for the UKIPO Manual of Patent Practice (MoPP) without MCP wiring."""

from .api import (  # noqa: F401
    USAGE_RESOURCE_URI,
    SearchInput,
    SectionInput,
    UpGuidelinesClient,
    UpGuidelinesSearchResponse,
    UpGuidelinesSection,
    UpGuidelinesVersion,
    get_client,
    get_section,
    get_usage_resource,
    list_versions,
    search,
)
from .corpus import CorpusUnavailable

__all__ = [
    "UpGuidelinesClient",
    "UpGuidelinesSearchResponse",
    "UpGuidelinesSection",
    "UpGuidelinesVersion",
    "SearchInput",
    "SectionInput",
    "CorpusUnavailable",
    "search",
    "get_section",
    "list_versions",
    "get_client",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]
