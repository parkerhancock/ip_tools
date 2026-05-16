"""Resource helpers for the IPO India statutes connector."""

from __future__ import annotations

USAGE_RESOURCE_URI = "resource://ipo_in_statutes/usage"


def get_usage_resource() -> str:
    """Return a one-page usage cheat-sheet for the IPO India statutes tools.

    Inline (rather than reading a packaged .md file) so the wheel
    layout stays minimal — the upstream MPEP equivalents read a
    bundled file via importlib.resources, but the static text below
    is short enough that the indirection isn't worth it.
    """
    return (
        "IPO India statutes — bundled corpus covering:\n"
        "  • Patents Act, 1970 (with amendments through 2024)\n"
        "  • Patent Rules, 2003 (with 2024 amendments)\n"
        "  • Designs Act, 2000\n"
        "  • Trade Marks Act, 1999\n"
        "  • Copyright Act, 1957 (last amended 2012)\n\n"
        "Citation forms accepted by `get_ipo_in_section`:\n"
        "  • 'Section 3(d) Patents Act' — the famous Indian §3(d) bar\n"
        "  • 'Section 25(2) Patents Act' — post-grant opposition\n"
        "  • 'Rule 71 Patent Rules'      — examination deadline\n"
        "  • 'S. 84'                     — bare number; resolves\n"
        "                                  uniquely when possible\n\n"
        "Use `search_ipo_in_statutes(query, statute=...)` to full-text\n"
        "search across one Act or all four.\n"
    )


__all__ = ["USAGE_RESOURCE_URI", "get_usage_resource"]
