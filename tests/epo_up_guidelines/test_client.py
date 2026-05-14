"""Tests for UP Guidelines client.

UP Guidelines use a flat ``N.M.P`` numbering matching slug
``section_N_M_P`` — different from the EPC/PCT Guidelines'
Part/Chapter/Section hierarchy.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patent_client_agents.epo_up_guidelines import UpGuidelinesClient
from patent_client_agents.epo_up_guidelines.client import _citation_to_slug
from patent_client_agents.epo_up_guidelines.corpus.schema import DDL, SCHEMA_VERSION


@pytest.fixture(scope="session")
def up_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("up-corpus") / "up.db"
    conn = sqlite3.connect(out)
    try:
        conn.executescript(DDL)
        for key, val in (
            ("schema_version", str(SCHEMA_VERSION)),
            ("source", "fixture"),
            ("snapshot_date", datetime.now(UTC).strftime("%Y-%m-%d")),
            ("up_guidelines_year", "2026"),
        ):
            conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, val))
        conn.executemany(
            "INSERT INTO sections (href, section_number, title, breadcrumb, chapter, html, text) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "section_2_1",
                    "2.1",
                    "Eligibility (requirements under Rule 5(2) UPR)",
                    None,
                    "2",
                    "<div><h1>Eligibility</h1><p>For unitary effect.</p></div>",
                    "2.1 Eligibility requirements under Rule 5(2) UPR for unitary effect.",
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return out


@pytest.fixture(autouse=True)
def _set_corpus(up_corpus_path, monkeypatch):
    monkeypatch.setenv("UP_GUIDELINES_CORPUS_PATH", str(up_corpus_path))


class TestCitationToSlug:
    @pytest.mark.parametrize(
        "citation,expected",
        [
            ("1.2.1", "section_1_2_1"),
            ("1-2-1", "section_1_2_1"),
            ("1 2 1", "section_1_2_1"),
            ("Section 1.2.1", "section_1_2_1"),
            ("§ 1.2.1", "section_1_2_1"),
            ("2.1", "section_2_1"),
        ],
    )
    def test_decoder(self, citation: str, expected: str) -> None:
        assert _citation_to_slug(citation) == expected


class TestUpGuidelines:
    @pytest.mark.parametrize("citation", ["2.1", "Section 2.1", "§ 2.1", "section_2_1"])
    async def test_citation_forms(self, citation: str) -> None:
        async with UpGuidelinesClient() as c:
            sec = await c.get_section(citation)
        assert sec.href == "section_2_1"

    async def test_search(self) -> None:
        async with UpGuidelinesClient() as c:
            r = await c.search("unitary effect")
        assert r.hits
        assert r.hits[0].result_url.startswith("https://www.epo.org/en/legal/guidelines-up/")
        # UP URLs don't have .html suffix
        assert not r.hits[0].result_url.endswith(".html")
