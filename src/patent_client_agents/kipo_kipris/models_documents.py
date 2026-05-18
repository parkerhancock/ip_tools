"""Stub module — KIPRIS Plus has no document-bundle endpoint in v1.

The JPO connector this package was scaffolded from has document-bundle
ZIP/HTM parsing; KIPRIS Plus has no analogous endpoint in the v1 tool
surface (full-text and legal-events are v2 deferrals — see
``research/specs/kr-kipo-connector-spec.md`` §3). This module exists
only to keep import paths from the scaffold step from breaking until
chunk 3 cleans them up.

Chunk 3 may delete this file entirely if no caller references it.
"""

from __future__ import annotations

# Re-export the row models so any straggler import like
# ``from patent_client_agents.kipo_kipris.models_documents import PatentUtilityRow``
# keeps working until chunk 3 rewires the package __init__.
from .models import DesignRow, PatentUtilityRow, TrademarkRow

__all__ = [
    "PatentUtilityRow",
    "TrademarkRow",
    "DesignRow",
]
