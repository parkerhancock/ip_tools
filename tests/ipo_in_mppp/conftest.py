"""Shared fixtures for IPO India MPPP tests.

Builds an on-disk corpus from the bundled seed JSONL.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from patent_client_agents.ipo_in_mppp.corpus.build import build_corpus


@pytest.fixture(scope="session")
def ipo_in_mppp_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("ipo-in-mppp-corpus") / "ipo_in_mppp.db"
    build_corpus(out)
    return out


@pytest.fixture
def ipo_in_mppp_corpus_env(
    monkeypatch: pytest.MonkeyPatch,
    ipo_in_mppp_corpus_path: Path,
) -> Path:
    monkeypatch.setenv("IPO_IN_MPPP_CORPUS_PATH", str(ipo_in_mppp_corpus_path))
    return ipo_in_mppp_corpus_path
