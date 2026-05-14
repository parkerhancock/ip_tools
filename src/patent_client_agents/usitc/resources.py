"""Resource helpers for USITC shared API."""

from __future__ import annotations

from importlib import resources

EDIS_TOKEN_RESOURCE_URI = "resource://usitc/edis-token"
DATAWEB_GUIDE_RESOURCE_URI = "resource://usitc/dataweb-api"
IDS_RESOURCE_URI = "resource://usitc/ids-feed"
HTS_RESOURCE_URI = "resource://usitc/hts-rest"


def _read_doc(name: str) -> str:
    return resources.files("law_tools.usitc.docs").joinpath(name).read_text(encoding="utf-8")


def get_edis_resource() -> str:
    return _read_doc("edis_token.md")


def get_dataweb_resource() -> str:
    return _read_doc("dataweb_api.md")


def get_ids_resource() -> str:
    return _read_doc("ids_feed.md")


def get_hts_resource() -> str:
    return _read_doc("hts_rest.md")
