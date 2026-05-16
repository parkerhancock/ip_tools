"""SQLite schema for the DPMA Germany IP statutes corpus.

Bundles the core German IP statutes — Patentgesetz (PatG),
Markengesetz (MarkenG), Gebrauchsmustergesetz (GebrMG),
Designgesetz (DesignG), Urheberrechtsgesetz (UrhG), and
Geschäftsgeheimnisgesetz (GeschGehG) — section-by-section into one
searchable database. Each row is one section (§) of one Act,
discriminated by ``statute``.

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
    rowid    INTEGER PRIMARY KEY,
    statute  TEXT NOT NULL,
    section  TEXT NOT NULL,
    title    TEXT,
    text     TEXT NOT NULL,
    UNIQUE(statute, section)
);

CREATE INDEX IF NOT EXISTS idx_sections_statute ON sections(statute);
CREATE INDEX IF NOT EXISTS idx_sections_section ON sections(section);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    statute,
    section,
    title,
    text,
    content='sections',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, statute, section, title, text)
    VALUES (new.rowid, new.statute, new.section, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, statute, section, title, text)
    VALUES ('delete', old.rowid, old.statute, old.section, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    INSERT INTO sections_fts(sections_fts, rowid, statute, section, title, text)
    VALUES ('delete', old.rowid, old.statute, old.section, old.title, old.text);
    INSERT INTO sections_fts(rowid, statute, section, title, text)
    VALUES (new.rowid, new.statute, new.section, new.title, new.text);
END;
"""


META_KEYS = {
    "schema_version": "SQLite schema version (int)",
    "snapshot_date": "ISO-8601 date the corpus was built",
    "source_version": "Optional vendor revision tag (rarely set for DPMA)",
    "section_count": "Total rows in sections (int, for sanity checks)",
}


# Canonical statute keys recognised by the corpus and client.
# All inputs lower-cased before lookup. Values are the canonical
# short-name used in the seed (PatG / MarkenG / GebrMG / DesignG /
# UrhG / GeschGehG).
STATUTE_KEYS: dict[str, str] = {
    "patg": "PatG",
    "patentgesetz": "PatG",
    "patent act": "PatG",
    "markeng": "MarkenG",
    "markengesetz": "MarkenG",
    "trade mark act": "MarkenG",
    "trademark act": "MarkenG",
    "gebrmg": "GebrMG",
    "gebrauchsmustergesetz": "GebrMG",
    "utility model act": "GebrMG",
    "designg": "DesignG",
    "designgesetz": "DesignG",
    "design act": "DesignG",
    "urhg": "UrhG",
    "urheberrechtsgesetz": "UrhG",
    "copyright act": "UrhG",
    "geschgehg": "GeschGehG",
    "geschäftsgeheimnisgesetz": "GeschGehG",
    "geschaeftsgeheimnisgesetz": "GeschGehG",
    "trade secrets act": "GeschGehG",
}
