"""Resource helpers for the Taiwan Trade Secrets Act connector."""

from __future__ import annotations

USAGE_RESOURCE_URI = "resource://tw_trade_secrets/usage"


def get_usage_resource() -> str:
    """Return a one-page usage cheat-sheet for the TW Trade Secrets tools.

    Inline (rather than reading a packaged .md file) so the wheel
    layout stays minimal — the statute is short enough that the
    indirection isn't worth it.
    """
    return (
        "Taiwan Trade Secrets Act (營業秘密法) — bundled English translation.\n\n"
        "Coverage: Articles 1, 2, 3, 10, 11, 13, 13-1 (legislative\n"
        "purpose, definition, employee-derived ownership, acts of\n"
        "misappropriation, injunction + damages, treble damages,\n"
        "criminal liability).\n\n"
        "Citation forms accepted by `get_tw_trade_secrets_section`:\n"
        "  • 'Art. 2 Trade Secrets Act'\n"
        "  • 'Section 13 Trade Secrets Act'\n"
        "  • 'Art. 13-1' (sub-numbered articles inserted by amendment)\n"
        "  • '13' (bare article number)\n\n"
        "Use `search_tw_trade_secrets(query)` to full-text search the\n"
        "Act.\n"
    )


__all__ = ["USAGE_RESOURCE_URI", "get_usage_resource"]
