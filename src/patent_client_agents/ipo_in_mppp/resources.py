"""Resource helpers for the IPO India MPPP connector."""

from __future__ import annotations

USAGE_RESOURCE_URI = "resource://ipo_in_mppp/usage"


def get_usage_resource() -> str:
    """Return a one-page usage cheat-sheet for the IPO India MPPP tools."""
    return (
        "IPO India MPPP — Manual of Patent Practice & Procedure (v3.0, 2019)\n"
        "Internal examination manual published by the Office of the Controller\n"
        "General of Patents, Designs and Trade Marks; the IPO India equivalent\n"
        "of the USPTO MPEP / UKIPO MoPP / EPO Guidelines.\n\n"
        "Citation form accepted by `get_ipo_in_mppp_section`:\n"
        "  • '04.05.01'                  — bare dotted number\n"
        "  • 'Chapter 04.05.01'          — informal citation\n"
        "  • 'MPPP Chapter 04.05.01'     — fully-qualified citation\n\n"
        "Use `search_ipo_in_mppp(query)` to full-text search across the manual.\n"
        "Sections are organised hierarchically (Chapter → Section → Subsection).\n"
    )


__all__ = ["USAGE_RESOURCE_URI", "get_usage_resource"]
