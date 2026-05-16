"""Static DPMA Germany IP statutes corpus — a frozen, queryable SQLite snapshot.

The runtime never calls gesetze-im-internet.de; it reads from a
SQLite/FTS5 database produced by
``patent-client-agents-build-dpma-statutes-corpus``. The database is
not bundled with the wheel — deployments materialize it via the build
CLI and the runtime locates it through:

1. ``DPMA_STATUTES_CORPUS_PATH`` environment variable (explicit path)
2. ``~/.cache/patent_client_agents/dpma_statutes.db`` (local-dev default)
3. ``CorpusUnavailable`` is raised with build instructions otherwise.
"""

from __future__ import annotations

from .db import CorpusDB, CorpusUnavailable, default_corpus_path

__all__ = ["CorpusDB", "CorpusUnavailable", "default_corpus_path"]
