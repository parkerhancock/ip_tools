"""Static metadata + citation parsing for the Légifrance IP connector.

Two canonical statute identifiers — ``CPI`` (Code de la propriété
intellectuelle, the IP code covering patents / trademarks / designs /
copyright) and ``Code de commerce`` (the commercial code; the L.151
family carries the trade-secret regime). The parser here is the
single source of truth that maps practitioner-shaped citation strings
(``L. 611-10 CPI``, ``Art. L. 151-1 Code de commerce``) into the
``(statute, section)`` tuple the corpus stores. Keep it permissive on
input formatting and strict on the output canonicalization — agents
should be able to paste literal French citations and get a hit.
"""

from __future__ import annotations

import re

STATUTES: tuple[str, ...] = ("CPI", "Code de commerce")
"""Closed vocabulary for the ``statute`` column (and statute filter)."""


# Accept the practitioner-facing shapes the brief calls out:
#   "L. 611-10 CPI"
#   "Art. L. 611-10 CPI"
#   "L611-10 CPI"
#   "L. 151-1 Code de commerce"
#
# We strip a leading "Art." (with or without trailing dot/space), then
# parse "L<digits>-<digits>" (dot or hyphen tolerated between L and
# digits), then match the trailing statute name.
_CITATION_RE = re.compile(
    r"""
    ^\s*
    (?:art(?:icle)?\.?\s+)?         # optional "Art." or "Article "
    (?:L\.?\s*)                     # required "L" prefix (book/livre)
    (?P<num>\d+[-\.]\d+(?:[-\.]\d+)?)  # "611-10", "151-1", "611.10"
    \s+
    (?P<statute>CPI|code\s+de\s+commerce)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


class CitationParseError(ValueError):
    """Raised when a citation string doesn't match any accepted form."""


def parse_citation(citation: str) -> tuple[str, str]:
    """Parse a Légifrance IP citation into ``(statute, section)``.

    Accepted forms (case-insensitive, leading "Art."/``Article``
    optional)::

        "L. 611-10 CPI"          -> ("CPI", "L611-10")
        "Art. L. 611-10 CPI"     -> ("CPI", "L611-10")
        "L611-10 CPI"            -> ("CPI", "L611-10")
        "L. 151-1 Code de commerce" -> ("Code de commerce", "L151-1")

    The returned ``section`` is canonical: capital ``L`` with no dot,
    hyphenated digits (``L611-10``), matching the seed schema.
    """
    match = _CITATION_RE.match(citation)
    if not match:
        raise CitationParseError(
            f"could not parse citation {citation!r}; expected forms like "
            "'L. 611-10 CPI' or 'Art. L. 151-1 Code de commerce'"
        )
    num = match.group("num").replace(".", "-")
    raw_statute = match.group("statute").strip().lower()
    if raw_statute == "cpi":
        statute = "CPI"
    else:
        # Normalize internal whitespace so "Code  de  commerce" still works.
        statute = "Code de commerce"
    return statute, f"L{num}"


__all__ = ["STATUTES", "CitationParseError", "parse_citation"]
