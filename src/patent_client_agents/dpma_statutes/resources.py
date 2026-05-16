"""Resource helpers for the DPMA Germany statutes connector."""

from __future__ import annotations

USAGE_RESOURCE_URI = "resource://dpma_statutes/usage"


def get_usage_resource() -> str:
    """Return a one-page usage cheat-sheet for the DPMA statutes tools."""
    return (
        "DPMA Germany — bundled IP statutes corpus covering:\n"
        "  • PatG       — Patentgesetz (Patent Act)\n"
        "  • MarkenG    — Markengesetz (Trade Mark Act)\n"
        "  • GebrMG     — Gebrauchsmustergesetz (Utility Model Act)\n"
        "  • DesignG    — Designgesetz (Design Act)\n"
        "  • UrhG       — Urheberrechtsgesetz (Copyright Act)\n"
        "  • GeschGehG  — Geschäftsgeheimnisgesetz (Trade Secrets Act)\n\n"
        "Citation forms accepted by `get_dpma_section`:\n"
        "  • '§ 1 PatG'       — patentable inventions\n"
        "  • '§ 139 PatG'     — injunction & damages\n"
        "  • '§ 14 MarkenG'   — exclusive trade-mark rights\n"
        "  • '§ 1 GebrMG'     — utility-model subject matter\n"
        "  • '§ 5 GeschGehG'  — bare 'Section'/'s.' shorthand accepted too\n\n"
        "Use `search_dpma_statutes(query, statute=...)` to full-text\n"
        "search across one Act or all six.\n"
    )


__all__ = ["USAGE_RESOURCE_URI", "get_usage_resource"]
