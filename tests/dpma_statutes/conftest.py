"""Shared fixtures for DPMA Germany statutes tests.

Builds an on-disk corpus from the bundled seed JSONL so the read path
is exercised end-to-end without any network calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from patent_client_agents.dpma_statutes.corpus.build import build_corpus


@pytest.fixture(scope="session")
def dpma_statutes_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a session-scoped corpus from the packaged seed."""
    out = tmp_path_factory.mktemp("dpma-statutes-corpus") / "dpma_statutes.db"
    build_corpus(out)
    return out


@pytest.fixture
def dpma_statutes_corpus_env(
    monkeypatch: pytest.MonkeyPatch,
    dpma_statutes_corpus_path: Path,
) -> Path:
    """Point DPMA_STATUTES_CORPUS_PATH at the fixture corpus."""
    monkeypatch.setenv("DPMA_STATUTES_CORPUS_PATH", str(dpma_statutes_corpus_path))
    return dpma_statutes_corpus_path
