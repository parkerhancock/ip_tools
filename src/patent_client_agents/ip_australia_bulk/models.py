"""Pydantic models for the IP RAPID bulk data catalog.

IP RAPID is IP Australia's weekly bulk dump of the full registered IP
register (patents + trade marks + designs + plant breeder's rights).
Distributed via the data.gov.au CKAN catalog under a Creative Commons
licence — no auth.

The catalog is fetched via the data.gov.au CKAN ``package_show`` API
(``data.gov.au/data/api/3/action/package_show?id=iprapid``); the
returned ``resources`` list carries the per-file metadata we surface
through :class:`BulkResource`.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_BASE_CONFIG: ConfigDict = ConfigDict(populate_by_name=True, extra="allow")


class BulkResource(BaseModel):
    """One downloadable resource within the IP RAPID dataset.

    Mirrors the CKAN ``resource`` shape, projected to the fields a
    consumer needs to identify and fetch the file (id, name, mimetype,
    size, download URL, last-modified timestamp).
    """

    id: str
    name: str | None = None
    description: str | None = None
    format: str | None = None
    mimetype: str | None = None
    size: int | None = None
    url: str | None = None
    last_modified: str | None = Field(default=None, alias="last_modified")

    model_config = _BASE_CONFIG


class BulkDataset(BaseModel):
    """The IP RAPID package as reported by data.gov.au CKAN.

    ``resources`` is the list of downloadable files (data zip + data
    dictionary PDF, as of 2026-05-16).
    """

    id: str
    name: str
    title: str | None = None
    notes: str | None = None
    license_id: str | None = None
    license_title: str | None = None
    metadata_modified: str | None = None
    organization: dict[str, Any] | None = None
    resources: list[BulkResource] = Field(default_factory=list)

    model_config = _BASE_CONFIG


__all__ = ["BulkDataset", "BulkResource"]
