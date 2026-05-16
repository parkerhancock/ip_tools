"""SQLite schema for the Légifrance IP statutes corpus.

One ``sections`` row per French statutory article. The FTS5 virtual table
indexes ``title`` + ``text`` and stays in sync via AI/AD/AU triggers —
the FTS5 "external content" pattern (rowid mirrors the canonical row in
``sections``). Tokenizer is ``unicode61 remove_diacritics 2`` so French
accented characters fold for search (``brevetabilite`` matches
``brevetabilité``) while the canonical row preserves the original
diacritics for display.
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
    rowid    INTEGER PRIMARY KEY,
    statute  TEXT NOT NULL,
    section  TEXT NOT NULL,
    title    TEXT,
    text     TEXT NOT NULL,
    UNIQUE(statute, section)
);

CREATE INDEX IF NOT EXISTS idx_sections_section ON sections(section);
CREATE INDEX IF NOT EXISTS idx_sections_statute ON sections(statute);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    title,
    text,
    content='sections',
    content_rowid='rowid',
    tokenize="unicode61 remove_diacritics 2"
);

CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, title, text)
    VALUES (new.rowid, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, title, text)
    VALUES ('delete', old.rowid, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, title, text)
    VALUES ('delete', old.rowid, old.title, old.text);
    INSERT INTO sections_fts(rowid, title, text)
    VALUES (new.rowid, new.title, new.text);
END;
"""


META_KEYS = {
    "schema_version": "SQLite schema version (int)",
    "snapshot_date": "ISO-8601 date the corpus was built",
    "source_version": "Légifrance corpus version label (e.g. 'seed v1')",
    "section_count": "Total rows in sections (int, for sanity checks)",
}
