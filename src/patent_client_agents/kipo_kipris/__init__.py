"""Async KIPO KIPRIS Plus connector (Korean Intellectual Property Office).

Built in 4 chunks: (1) scaffold from the JPO package, (2) XML row models
(this commit) for ``patUtliInfoSearchService`` /
``trademarkInfoSearchService`` / ``designInfoSearchService``, (3)
``KiprisClient`` + module-level helpers + MCP tool surface, (4) tests.
See ``research/specs/kr-kipo-connector-spec.md`` for the full contract.

Auth is BYOK per ToS §11: a single per-user ``serviceKey`` exposed via
the ``KIPO_KIPRIS_API_KEY`` environment variable.

The ``KiprisClient`` re-export is deferred until chunk 3 rewrites
``client.py`` — chunk 2's ``client.py`` still carries the JPO scaffold
contents and would fail to import the now-removed JPO model names from
``.models``.
"""

from .models import DesignRow, PatentUtilityRow, TrademarkRow

__all__ = [
    "PatentUtilityRow",
    "TrademarkRow",
    "DesignRow",
]
