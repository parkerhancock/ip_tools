"""Env var helper with LAW_TOOLS_* legacy aliases.

``LAW_TOOLS_CORE_*`` is canonical. ``LAW_TOOLS_*`` is accepted as a
fallback so pre-split law-tools deployments keep working without a
config rewrite.
"""

from __future__ import annotations

import os

_CANONICAL_PREFIX = "LAW_TOOLS_CORE_"
_LEGACY_PREFIX = "LAW_TOOLS_"


def get(name: str, default: str = "") -> str:
    """Read ``LAW_TOOLS_CORE_{name}`` with ``LAW_TOOLS_{name}`` as fallback."""
    canonical = os.environ.get(_CANONICAL_PREFIX + name)
    if canonical is not None:
        return canonical
    legacy = os.environ.get(_LEGACY_PREFIX + name)
    if legacy is not None:
        return legacy
    return default
