"""Async one-shot API for the Légifrance IP corpus.

Both ``search()`` and ``get_section()`` are module-level coroutines
that open a :class:`LegifranceIpClient` for the duration of the call
and close it afterwards. Prefer the context-manager form
(``async with LegifranceIpClient() as client: ...``) when fanning
multiple calls; these helpers exist for the common single-call
shape.
"""

from __future__ import annotations

from .client import LegifranceIpClient
from .models import LegifranceSearchResult, LegifranceSection

__all__ = ["search", "get_section", "LegifranceIpClient"]


async def search(
    query: str,
    *,
    statute: str | None = None,
    per_page: int = 10,
    page: int = 1,
) -> LegifranceSearchResult:
    """Search the Légifrance IP corpus.

    Args:
        query: Free-text query in French (or English fallback). FTS5
            treats multi-token queries as AND with diacritic-folded
            matching, so ``brevetabilite`` will hit ``brevetabilité``.
        statute: Optional filter — ``'CPI'`` or ``'Code de commerce'``.
        per_page: Maximum hits to return (1-100).
        page: 1-indexed page number.
    """
    async with LegifranceIpClient() as client:
        return await client.search(query, statute=statute, per_page=per_page, page=page)


async def get_section(citation: str) -> LegifranceSection:
    """Resolve a French statutory citation to a corpus row.

    Accepts the practitioner-facing shapes ``"L. 611-10 CPI"``,
    ``"Art. L. 611-10 CPI"``, ``"L611-10 CPI"``, and ``"L. 151-1 Code de
    commerce"`` — see :func:`patent_client_agents.legifrance_ip.resources.parse_citation`
    for the full grammar.
    """
    async with LegifranceIpClient() as client:
        return await client.get_section(citation)
