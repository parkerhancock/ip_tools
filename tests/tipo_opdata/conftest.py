"""Pytest fixtures for the TIPO OpenData connector tests.

Provides:
- ``tipo_client`` — an async-context :class:`TipoClient` for tests that
  want a live or replayed client. Resolves the ``tk`` from
  ``TIPO_API_KEY`` (set by the root conftest as a placeholder); for
  cassette recording, set ``TIPO_API_KEY`` to a real ``tk`` UUID
  before running pytest.

VCR cassettes scrub the ``tk`` query parameter via the root conftest's
``filter_query_parameters`` config — see ``tests/conftest.py``.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest_asyncio

from patent_client_agents.tipo_opdata import TipoClient


@pytest_asyncio.fixture
async def tipo_client() -> AsyncIterator[TipoClient]:
    """Yield a context-managed TIPO client (uses ``TIPO_API_KEY``)."""
    tk = os.environ.get("TIPO_API_KEY", "test_tipo_tk")
    async with TipoClient(tk=tk) as client:
        yield client
