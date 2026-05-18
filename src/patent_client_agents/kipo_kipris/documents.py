"""Stub module — KIPRIS Plus has no document-bundle ZIP parsing in v1.

The JPO ``app_doc_cont_*`` endpoints return ZIP archives that the JPO
connector unpacks here; KIPRIS Plus exposes no equivalent endpoint in
the v1 tool surface (full-text and legal-events are v2 deferrals — see
``research/specs/kr-kipo-connector-spec.md`` §3). This stub exists only
to keep import paths from the scaffold step from breaking until chunk
3 cleans them up.

Chunk 3 may delete this file entirely if no caller references it.
"""

from __future__ import annotations

__all__: list[str] = []
