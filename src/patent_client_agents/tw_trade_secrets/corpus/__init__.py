"""Static Taiwan Trade Secrets Act corpus — a frozen, queryable SQLite snapshot.

The runtime never calls law.moj.gov.tw; it reads from a SQLite/FTS5
database produced by ``patent-client-agents-build-tw-trade-secrets-corpus``.
The database is not bundled with the wheel — deployments materialize it
via the build CLI and the runtime locates it through:

1. ``TW_TRADE_SECRETS_CORPUS_PATH`` environment variable (explicit path)
2. ``~/.cache/patent_client_agents/tw_trade_secrets.db`` (local-dev default)
3. ``CorpusUnavailable`` is raised with build instructions otherwise.
"""

from __future__ import annotations

from .db import CorpusDB, CorpusUnavailable, default_corpus_path

__all__ = ["CorpusDB", "CorpusUnavailable", "default_corpus_path"]
