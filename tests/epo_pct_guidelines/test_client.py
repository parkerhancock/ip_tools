"""Tests for PCT-EPO Guidelines client.

PCT-EPO Guidelines use the same URL hierarchy as the EPC Guidelines
(``g_ii_3_1.html`` → ``G-II, 3.1``). Citation forms and behavior
mirror the EPC Guidelines tests exactly.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patent_client_agents.epo_pct_guidelines import PctGuidelinesClient
from patent_client_agents.epo_pct_guidelines.corpus.schema import DDL, SCHEMA_VERSION


@pytest.fixture(scope="session")
def pct_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("pct-corpus") / "pct.db"
    conn = sqlite3.connect(out)
    try:
        conn.executescript(DDL)
        for key, val in (
            ("schema_version", str(SCHEMA_VERSION)),
            ("source", "fixture"),
            ("snapshot_date", datetime.now(UTC).strftime("%Y-%m-%d")),
            ("guidelines_year", "2024"),
        ):
            conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, val))
        conn.executemany(
            "INSERT INTO sections (href, section_number, title, breadcrumb, chapter, html, text) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "g_ii_3_1",
                    "G-II, 3.1",
                    "3.1 Subject matter excluded from international search",
                    None,
                    "G",
                    "<div><h1>Excluded subject matter</h1><p>Discoveries.</p></div>",
                    "3.1 Subject matter excluded from international search. Discoveries.",
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return out


@pytest.fixture(autouse=True)
def _set_corpus(pct_corpus_path, monkeypatch):
    monkeypatch.setenv("PCT_GUIDELINES_CORPUS_PATH", str(pct_corpus_path))


class TestPctGuidelines:
    @pytest.mark.parametrize("citation", ["G-II, 3.1", "G-II 3.1", "G.II.3.1", "g_ii_3_1"])
    async def test_citation_forms(self, citation: str) -> None:
        async with PctGuidelinesClient() as c:
            sec = await c.get_section(citation)
        assert sec.href == "g_ii_3_1"

    async def test_search(self) -> None:
        async with PctGuidelinesClient() as c:
            r = await c.search("Discoveries")
        assert r.hits
        assert r.hits[0].result_url.startswith("https://www.epo.org/en/legal/guidelines-pct/")
