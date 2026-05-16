"""SQLite schema for the IPO India statutes corpus.

The corpus bundles the four core Indian IP Acts — Patents Act 1970,
Designs Act 2000, Trade Marks Act 1999, and Copyright Act 1957 —
section-by-section into one searchable database. Each row is one
section (or rule) of one Act, discriminated by ``statute_name``.

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
    rowid          INTEGER PRIMARY KEY,
    statute_name   TEXT NOT NULL,
    section_number TEXT NOT NULL,
    title          TEXT,
    text           TEXT NOT NULL,
    source_url     TEXT,
    UNIQUE(statute_name, section_number)
);

CREATE INDEX IF NOT EXISTS idx_sections_statute
    ON sections(statute_name);
CREATE INDEX IF NOT EXISTS idx_sections_section_number
    ON sections(section_number);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    statute_name,
    section_number,
    title,
    text,
    content='sections',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, statute_name, section_number, title, text)
    VALUES (new.rowid, new.statute_name, new.section_number, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, statute_name, section_number, title, text)
    VALUES ('delete', old.rowid, old.statute_name, old.section_number, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, statute_name, section_number, title, text)
    VALUES ('delete', old.rowid, old.statute_name, old.section_number, old.title, old.text);
    INSERT INTO sections_fts(rowid, statute_name, section_number, title, text)
    VALUES (new.rowid, new.statute_name, new.section_number, new.title, new.text);
END;
"""


META_KEYS = {
    "schema_version": "SQLite schema version (int)",
    "snapshot_date": "ISO-8601 date the corpus was built",
    "source_version": "Optional vendor revision tag (rarely set for India)",
    "section_count": "Total rows in sections (int, for sanity checks)",
}


# Canonical statute keys recognised by the corpus and client.
STATUTE_KEYS: dict[str, str] = {
    # short_key → canonical statute_name
    "patents": "Patents Act",
    "patents act": "Patents Act",
    "patents act 1970": "Patents Act",
    "patent rules": "Patent Rules",
    "patents rules": "Patent Rules",
    "designs": "Designs Act",
    "designs act": "Designs Act",
    "designs act 2000": "Designs Act",
    "trade marks": "Trade Marks Act",
    "trademarks": "Trade Marks Act",
    "trade marks act": "Trade Marks Act",
    "trade marks act 1999": "Trade Marks Act",
    "copyright": "Copyright Act",
    "copyright act": "Copyright Act",
    "copyright act 1957": "Copyright Act",
}
