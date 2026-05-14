"""SQLite schema for the UPC statutes corpus.

The corpus stores one row per (instrument, language) pair — full
plain-text of each legal instrument, with an FTS5 virtual table
indexing the searchable fields. The "external content" pattern keeps
the inverted index slim while the canonical row lives in
``instruments``.

Per-Article / per-Rule section extraction is deferred to a v2 schema
revision — the PDFs are well-structured enough that we can split UPCA
articles and RoP rules from the TOC, but the parser needs to be tuned
per instrument and that work isn't in scope for v0.11.0.
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

CREATE TABLE IF NOT EXISTS instruments (
    rowid          INTEGER PRIMARY KEY,
    instrument     TEXT NOT NULL,
    language       TEXT NOT NULL,
    short_name     TEXT NOT NULL,
    title          TEXT NOT NULL,
    source_url     TEXT NOT NULL,
    source_version TEXT,
    pdf_pages      INTEGER,
    text           TEXT NOT NULL,
    UNIQUE(instrument, language)
);

CREATE INDEX IF NOT EXISTS idx_instruments_short_name
    ON instruments(short_name);
CREATE INDEX IF NOT EXISTS idx_instruments_language
    ON instruments(language);

CREATE VIRTUAL TABLE IF NOT EXISTS instruments_fts USING fts5(
    short_name,
    title,
    text,
    content='instruments',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS instruments_ai AFTER INSERT ON instruments BEGIN
    INSERT INTO instruments_fts(rowid, short_name, title, text)
    VALUES (new.rowid, new.short_name, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS instruments_ad AFTER DELETE ON instruments BEGIN
    INSERT INTO instruments_fts(instruments_fts, rowid, short_name, title, text)
    VALUES ('delete', old.rowid, old.short_name, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS instruments_au AFTER UPDATE ON instruments BEGIN
    INSERT INTO instruments_fts(instruments_fts, rowid, short_name, title, text)
    VALUES ('delete', old.rowid, old.short_name, old.title, old.text);
    INSERT INTO instruments_fts(rowid, short_name, title, text)
    VALUES (new.rowid, new.short_name, new.title, new.text);
END;
"""


META_KEYS = {
    "schema_version": "SQLite schema version (int)",
    "snapshot_date": "ISO-8601 date the corpus was built",
    "instrument_count": "Number of (instrument, language) rows",
}
