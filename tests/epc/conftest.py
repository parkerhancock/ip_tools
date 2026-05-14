"""Shared fixtures for EPC tests."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patent_client_agents.epc.corpus.schema import DDL, SCHEMA_VERSION


def _row(
    slug: str, section_number: str | None, title: str, chapter: str | None, text: str
) -> tuple:
    return (
        slug,
        section_number,
        title,
        None,
        chapter,
        f"<div><h1>{title}</h1><p>{text}</p></div>",
        f"{title} {text}",
    )


@pytest.fixture(scope="session")
def epc_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("epc-corpus") / "epc.db"
    rows = [
        _row(
            "a54",
            "Article 54",
            "Article 54 – Novelty",
            "Article",
            "An invention is considered new if it does not form part of the state of the art.",
        ),
        _row(
            "a56",
            "Article 56",
            "Article 56 – Inventive step",
            "Article",
            "An invention involves an inventive step if it is not obvious to a person skilled in the art.",
        ),
        _row(
            "r71",
            "Rule 71",
            "Rule 71 – Examination procedure",
            "Rule",
            "Communications from the Examining Division under Article 94(3).",
        ),
    ]
    conn = sqlite3.connect(out)
    try:
        conn.executescript(DDL)
        for key, val in (
            ("schema_version", str(SCHEMA_VERSION)),
            ("source", "fixture"),
            ("snapshot_date", datetime.now(UTC).strftime("%Y-%m-%d")),
            ("epc_year", "2020"),
        ):
            conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, val))
        conn.executemany(
            "INSERT INTO sections (href, section_number, title, breadcrumb, chapter, html, text) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()
    return out
