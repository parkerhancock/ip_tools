"""Shared fixtures for Légifrance IP statutes tests.

Builds an on-disk corpus from the bundled seed JSONL so the read path
is exercised end-to-end without any network calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from patent_client_agents.legifrance_ip.corpus.build import build_corpus


@pytest.fixture(scope="session")
def legifrance_ip_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a session-scoped corpus from the packaged seed."""
    out = tmp_path_factory.mktemp("legifrance-ip-corpus") / "legifrance_ip.db"
    build_corpus(out)
    return out


@pytest.fixture
def legifrance_ip_corpus_env(
    monkeypatch: pytest.MonkeyPatch,
    legifrance_ip_corpus_path: Path,
) -> Path:
    """Point LEGIFRANCE_IP_CORPUS_PATH at the fixture corpus."""
    monkeypatch.setenv("LEGIFRANCE_IP_CORPUS_PATH", str(legifrance_ip_corpus_path))
    return legifrance_ip_corpus_path
