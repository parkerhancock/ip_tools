"""SQLite schema for the Taiwan Trade Secrets Act corpus.

The corpus indexes a single statute — the Taiwan Trade Secrets Act
(營業秘密法) — section by section. Each row is one Article (or
sub-numbered Article like ``13-1``). There is no ``statute`` field
because the corpus only covers one statute; if we ever extend it to
sibling Acts (Fair Trade Act, Personal Data Protection Act, etc.) the
schema would need to grow a ``statute_name`` discriminator. For now,
single-statute keeps the schema and queries simple.

The FTS5 virtual table indexes title + text, using the "external
content" pattern so the canonical row lives in ``sections`` while the
inverted index stays slim. Per-section trigger pairs keep them in sync.
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
    rowid   INTEGER PRIMARY KEY,
    section TEXT UNIQUE NOT NULL,
    title   TEXT,
    text    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sections_section ON sections(section);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    section,
    title,
    text,
    content='sections',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, section, title, text)
    VALUES (new.rowid, new.section, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section, title, text)
    VALUES ('delete', old.rowid, old.section, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, section, title, text)
    VALUES ('delete', old.rowid, old.section, old.title, old.text);
    INSERT INTO sections_fts(rowid, section, title, text)
    VALUES (new.rowid, new.section, new.title, new.text);
END;
"""


META_KEYS = {
    "schema_version": "SQLite schema version (int)",
    "snapshot_date": "ISO-8601 date the corpus was built",
    "source_version": "Optional vendor revision tag (rarely set for TW Trade Secrets)",
    "section_count": "Total rows in sections (int, for sanity checks)",
}
