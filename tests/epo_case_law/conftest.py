"""Shared fixtures for EPO Case Law tests."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patent_client_agents.epo_case_law.corpus.schema import DDL, SCHEMA_VERSION


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
def caselaw_corpus_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("caselaw-corpus") / "caselaw.db"
    rows = [
        _row(
            "clr_i_a",
            "I.A",
            "A. Patentable inventions",
            "Part I",
            "General principles concerning patentability under Article 52 EPC.",
        ),
        _row(
            "clr_i_a_1",
            "I.A.1",
            "1. Novelty",
            "Part I",
            "Novelty is assessed under Article 54 EPC; see G 1/03.",
        ),
        _row(
            "clr_i_d_3",
            "I.D.3",
            "3. Inventive step",
            "Part I",
            "The problem-and-solution approach is the standard method.",
        ),
        _row(
            "clr_foreword",
            "Foreword",
            "Foreword",
            "Foreword",
            "Foreword to the 10th edition of the Case Law of the Boards of Appeal.",
        ),
    ]
    conn = sqlite3.connect(out)
    try:
        conn.executescript(DDL)
        for key, val in (
            ("schema_version", str(SCHEMA_VERSION)),
            ("source", "fixture"),
            ("snapshot_date", datetime.now(UTC).strftime("%Y-%m-%d")),
            ("caselaw_year", "2022"),
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
