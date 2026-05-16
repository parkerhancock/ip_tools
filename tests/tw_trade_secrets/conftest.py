"""Shared fixtures for Taiwan Trade Secrets Act tests.

Builds an on-disk corpus from the bundled seed JSONL so the read path
is exercised end-to-end without any network calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from patent_client_agents.tw_trade_secrets.corpus.build import build_corpus


@pytest.fixture(scope="session")
def tw_trade_secrets_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a session-scoped corpus from the packaged seed."""
    out = tmp_path_factory.mktemp("tw-trade-secrets-corpus") / "tw_trade_secrets.db"
    build_corpus(out)
    return out


@pytest.fixture
def tw_trade_secrets_corpus_env(
    monkeypatch: pytest.MonkeyPatch,
    tw_trade_secrets_corpus_path: Path,
) -> Path:
    """Point TW_TRADE_SECRETS_CORPUS_PATH at the fixture corpus."""
    monkeypatch.setenv("TW_TRADE_SECRETS_CORPUS_PATH", str(tw_trade_secrets_corpus_path))
    return tw_trade_secrets_corpus_path
