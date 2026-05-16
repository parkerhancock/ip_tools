"""Build the IPO India MPPP SQLite/FTS5 corpus from a JSON seed.

The IPO India MPPP (Manual of Patent Practice & Procedure) v3.0 (2019)
is published as a single ~400-page PDF. Refresh requires scraping the
PDF off ipindia.gov.in and re-chunking — outside the runtime path.
The seed file at ``data/ipo_in_mppp/seed.jsonl`` is the build input.

Each record shape::

    {
        "section_number": "04.05.01",
        "chapter": "Chapter 4",
        "title": "Examination of patent applications",
        "text": "...full section text...",
        "source_url": "https://ipindia.gov.in/..."
    }

Console-script entry point for
``patent-client-agents-build-ipo-in-mppp-corpus``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

from .schema import DDL, SCHEMA_VERSION

logger = logging.getLogger(__name__)

DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed.jsonl"


def _load_seed(seed_path: Path) -> list[dict[str, str]]:
    """Read the JSON-lines seed into a list of dicts."""
    rows: list[dict[str, str]] = []
    with seed_path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{seed_path}:{lineno}: invalid JSON — {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{seed_path}:{lineno}: expected object, got {type(row).__name__}")
            for key in ("section_number", "text"):
                if key not in row or not row[key]:
                    raise ValueError(f"{seed_path}:{lineno}: missing required key '{key}'")
            rows.append(row)
    return rows


def build_corpus(
    output_path: Path,
    *,
    seed_path: Path = DEFAULT_SEED_PATH,
    source_version: str | None = "v3.0 (2019)",
) -> int:
    """Write the corpus to ``output_path`` and return the row count."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    seed_rows = _load_seed(seed_path)
    logger.info("Loaded %d seed rows from %s", len(seed_rows), seed_path)

    conn = sqlite3.connect(tmp_path)
    try:
        conn.executescript(DDL)
        snapshot = datetime.now(UTC).strftime("%Y-%m-%d")
        meta_pairs = [
            ("schema_version", str(SCHEMA_VERSION)),
            ("snapshot_date", snapshot),
            ("section_count", str(len(seed_rows))),
        ]
        if source_version:
            meta_pairs.append(("source_version", source_version))
        conn.executemany(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            meta_pairs,
        )
        conn.executemany(
            "INSERT INTO sections (section_number, chapter, title, text, source_url) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["section_number"],
                    row.get("chapter"),
                    row.get("title"),
                    row["text"],
                    row.get("source_url"),
                )
                for row in seed_rows
            ],
        )
        conn.commit()
    finally:
        conn.close()

    if output_path.exists():
        output_path.unlink()
    tmp_path.rename(output_path)
    logger.info("Wrote %d sections to %s", len(seed_rows), output_path)
    return len(seed_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the IPO India MPPP SQLite/FTS5 corpus from the bundled JSON seed."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home() / ".cache" / "patent_client_agents" / "ipo_in_mppp.db",
        help="Path to write the corpus to (default: ~/.cache/patent_client_agents/ipo_in_mppp.db)",
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=DEFAULT_SEED_PATH,
        help="JSON-lines seed file to ingest (default: bundled seed.jsonl).",
    )
    parser.add_argument(
        "--source-version",
        default="v3.0 (2019)",
        help="Vendor edition label (defaults to the v3.0 2019 publication).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable INFO logging.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        count = build_corpus(
            args.output,
            seed_path=args.seed,
            source_version=args.source_version,
        )
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 — CLI top-level boundary
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {count} sections to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
