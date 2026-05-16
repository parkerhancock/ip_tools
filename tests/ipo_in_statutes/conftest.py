"""Shared fixtures for IPO India statutes tests.

Builds an on-disk corpus from the bundled seed JSONL so the read path
is exercised end-to-end without any network calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from patent_client_agents.ipo_in_statutes.corpus.build import build_corpus


@pytest.fixture(scope="session")
def ipo_in_statutes_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a session-scoped corpus from the packaged seed."""
    out = tmp_path_factory.mktemp("ipo-in-statutes-corpus") / "ipo_in_statutes.db"
    build_corpus(out)
    return out


@pytest.fixture
def ipo_in_statutes_corpus_env(
    monkeypatch: pytest.MonkeyPatch,
    ipo_in_statutes_corpus_path: Path,
) -> Path:
    """Point IPO_IN_STATUTES_CORPUS_PATH at the fixture corpus."""
    monkeypatch.setenv("IPO_IN_STATUTES_CORPUS_PATH", str(ipo_in_statutes_corpus_path))
    return ipo_in_statutes_corpus_path
