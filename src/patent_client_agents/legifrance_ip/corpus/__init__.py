"""Static Légifrance IP corpus — a frozen, queryable SQLite snapshot.

The runtime never calls Légifrance; it reads from a SQLite/FTS5 database
produced by ``patent-client-agents-build-legifrance-ip-corpus`` from the
bundled ``data/seed.jsonl``. Deployments materialize it via the build
CLI; the runtime locates it through:

1. ``LEGIFRANCE_IP_CORPUS_PATH`` environment variable (explicit path)
2. ``~/.cache/patent_client_agents/legifrance_ip.db`` (local-dev default)
3. ``CorpusUnavailable`` is raised with build instructions otherwise.
"""

from __future__ import annotations

from .db import CorpusDB, CorpusUnavailable, default_corpus_path

__all__ = ["CorpusDB", "CorpusUnavailable", "default_corpus_path"]
