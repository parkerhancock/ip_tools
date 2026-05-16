"""SQLite schema for the IPO India MPPP (Manual of Patent Practice & Procedure) corpus.

The MPPP is published by the IPO India as a single ~400-page PDF
organised into hierarchical chapter sections (e.g. ``04.05.01``).
Each row of ``sections`` is one section node — the FTS5 virtual
table indexes title + text via the "external content" pattern so
the canonical row stays in ``sections``.
"""

from __future__ import annotations

SCHEMA_VERSION = 1

DDL = """
PRAGMA foreign_keys = OFF;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sections (
    rowid          INTEGER PRIMARY KEY,
    section_number TEXT UNIQUE NOT NULL,
    chapter        TEXT,
    title          TEXT,
    text           TEXT NOT NULL,
    source_url     TEXT
);

CREATE INDEX IF NOT EXISTS idx_sections_chapter
    ON sections(chapter);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    section_number,
    title,
    text,
    content='sections',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, section_number, title, text)
    VALUES (new.rowid, new.section_number, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section_number, title, text)
    VALUES ('delete', old.rowid, old.section_number, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section_number, title, text)
    VALUES ('delete', old.rowid, old.section_number, old.title, old.text);
    INSERT INTO sections_fts(rowid, section_number, title, text)
    VALUES (new.rowid, new.section_number, new.title, new.text);
END;
"""


META_KEYS = {
    "schema_version": "SQLite schema version (int)",
    "snapshot_date": "ISO-8601 date the corpus was built",
    "source_version": "MPPP edition label (e.g. 'v3.0 (2019)') when known",
    "section_count": "Total rows in sections (int, for sanity checks)",
}
