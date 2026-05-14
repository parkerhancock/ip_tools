"""Tests for the UPC statutes corpus.

Builds a tiny in-memory corpus from inline fixtures rather than
hitting unifiedpatentcourt.org or unpacking real PDFs. The schema +
FTS5 wiring is what we want pinned; PDF text extraction is a separate
concern covered by the build CLI smoke test.
"""

from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path

import pytest

from patent_client_agents.upc_statutes import UpcStatutesClient
from patent_client_agents.upc_statutes.client import _translate_fts_query
from patent_client_agents.upc_statutes.corpus import CorpusUnavailable
from patent_client_agents.upc_statutes.corpus.schema import DDL, SCHEMA_VERSION

# Trimmed fixtures — just enough text to exercise FTS5 ranking and the
# instrument/language filter.
FIXTURES = [
    {
        "instrument": "upca",
        "language": "en",
        "short_name": "UPCA",
        "title": "Agreement on a Unified Patent Court",
        "source_url": "https://example.com/upca-en.pdf",
        "source_version": None,
        "pdf_pages": 44,
        "text": (
            "Article 33 Competence of the divisions of the Court of "
            "First Instance. Actions referred to in Article 32(1)(a) "
            "shall be brought before the local division. An opt-out "
            "under Article 83 removes UPC jurisdiction over a "
            "traditional European patent during the transitional period."
        ),
    },
    {
        "instrument": "rop",
        "language": "en",
        "short_name": "RoP",
        "title": "Consolidated Rules of Procedure of the Unified Patent Court",
        "source_url": "https://example.com/rop-en.pdf",
        "source_version": None,
        "pdf_pages": 143,
        "text": (
            "Rule 5 — Lodging of an Application to opt out and "
            "withdrawal of an opt-out. The proprietor may apply to opt "
            "out a European patent from the exclusive competence of "
            "the Court before expiry of the transitional period."
        ),
    },
    {
        "instrument": "fees",
        "language": "en",
        "short_name": "Fees",
        "title": "Consolidated Table of Court Fees and Recoverable Costs",
        "source_url": "https://example.com/fees-en.pdf",
        "source_version": None,
        "pdf_pages": 8,
        "text": (
            "Fixed fees apply to infringement actions, counterclaims "
            "for revocation, and applications for provisional measures. "
            "Recoverable costs are capped by the value-based ceiling."
        ),
    },
    {
        "instrument": "upca",
        "language": "fr",
        "short_name": "UPCA",
        "title": "Accord relatif à une juridiction unifiée du brevet",
        "source_url": "https://example.com/upca-fr.pdf",
        "source_version": None,
        "pdf_pages": 44,
        "text": (
            "Article 33 Compétence des divisions du tribunal de "
            "première instance. Les actions visées à l'article 32(1)(a) "
            "sont engagées devant la division locale."
        ),
    },
]


def _seed_corpus(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(DDL)
        for row in FIXTURES:
            conn.execute(
                """
                INSERT INTO instruments
                    (instrument, language, short_name, title,
                     source_url, source_version, pdf_pages, text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["instrument"],
                    row["language"],
                    row["short_name"],
                    row["title"],
                    row["source_url"],
                    row["source_version"],
                    row["pdf_pages"],
                    row["text"],
                ),
            )
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("snapshot_date", "2026-05-13"),
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("instrument_count", str(len(FIXTURES))),
        )
        conn.execute("INSERT INTO instruments_fts(instruments_fts) VALUES ('optimize')")
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def corpus_path(tmp_path: Path) -> Path:
    db = tmp_path / "upc_statutes.db"
    _seed_corpus(db)
    return db


def _run(coro):
    return asyncio.run(coro)


def test_translate_fts_query_quotes_hyphenated_terms():
    # Bare token: pass through.
    assert _translate_fts_query("opt", "and") == "opt"
    # Hyphenated: quoted as a phrase so FTS5 doesn't interpret the dash.
    assert _translate_fts_query("opt-out", "and") == '"opt-out"'
    # Multi-token AND: each token independently quoted as needed.
    assert _translate_fts_query("Article 33", "and") == "Article 33"
    assert _translate_fts_query("opt-out withdrawal", "and") == '"opt-out" withdrawal'
    # Exact: whole thing wrapped as a single phrase.
    assert _translate_fts_query("Article 33", "exact") == '"Article 33"'
    # OR-mode preserves the operator.
    assert _translate_fts_query("opt withdrawal", "or") == "opt OR withdrawal"


def test_list_instruments(corpus_path: Path):
    async def go():
        async with UpcStatutesClient(corpus_path=corpus_path) as c:
            return await c.list_instruments(language="en")

    instruments = _run(go())
    assert {i.instrument for i in instruments} == {"upca", "rop", "fees"}
    assert all(i.language == "en" for i in instruments)


def test_get_instrument_resolves_aliases(corpus_path: Path):
    async def go():
        async with UpcStatutesClient(corpus_path=corpus_path) as c:
            # Alias for UPCA Annex I resolves to the UPCA row.
            return await c.get_instrument(instrument="Rules of Procedure", language="en")

    rop = _run(go())
    assert rop is not None
    assert rop.short_name == "RoP"
    assert "opt out" in rop.text.lower()


def test_search_finds_hyphenated_term(corpus_path: Path):
    async def go():
        async with UpcStatutesClient(corpus_path=corpus_path) as c:
            return await c.search("opt-out", instrument="rop", language="en")

    response = _run(go())
    assert len(response.hits) == 1
    assert response.hits[0].instrument == "rop"
    assert "<mark>" in response.hits[0].snippet


def test_search_scoped_by_instrument(corpus_path: Path):
    async def go():
        async with UpcStatutesClient(corpus_path=corpus_path) as c:
            return await c.search("Article 33", instrument="upca", language="en")

    response = _run(go())
    assert all(h.instrument == "upca" for h in response.hits)
    assert response.hits[0].language == "en"


def test_search_filters_by_language(corpus_path: Path):
    async def go():
        async with UpcStatutesClient(corpus_path=corpus_path) as c:
            return await c.search("Article", language="fr")

    response = _run(go())
    assert response.hits
    assert all(h.language == "fr" for h in response.hits)


def test_missing_corpus_raises_with_install_hint(tmp_path: Path):
    missing = tmp_path / "absent.db"

    async def go():
        async with UpcStatutesClient(corpus_path=missing) as c:
            await c.list_instruments()

    with pytest.raises(CorpusUnavailable, match="build-upc-statutes-corpus"):
        _run(go())


def test_meta_round_trip(corpus_path: Path):
    async def go():
        async with UpcStatutesClient(corpus_path=corpus_path) as c:
            return await c.meta()

    meta = _run(go())
    assert meta.schema_version == SCHEMA_VERSION
    assert meta.instrument_count == len(FIXTURES)
    assert meta.snapshot_date == "2026-05-13"
