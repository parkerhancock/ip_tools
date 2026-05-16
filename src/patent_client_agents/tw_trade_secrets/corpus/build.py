"""Build the Taiwan Trade Secrets Act SQLite/FTS5 corpus from a JSON seed.

The seed file ships in the repo at
``src/patent_client_agents/tw_trade_secrets/data/seed.jsonl`` and
contains one JSON object per Article of the Taiwan Trade Secrets Act
(營業秘密法), in the official English translation published by the
Laws & Regulations Database of the Republic of China
(``law.moj.gov.tw/Eng``). Each record has:

    {
        "section": "13-1",
        "title": "Criminal Liability",
        "text": "...full Article text..."
    }

Console-script entry point for
``patent-client-agents-build-tw-trade-secrets-corpus``.

The seed approach (rather than scraping law.moj.gov.tw at build time)
keeps the connector deterministic and CI-friendly — the seed is itself
the artifact under version control, and refreshing it is a deliberate
documented step. See ``CONNECTOR_STANDARDS.md`` §4 ``update_strategy =
scheduled_recrawl`` / cadence ``irregular`` for the policy.
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

# The seed file lives alongside the package source. Cloud deploys can
# override via ``--seed`` to point at a freshly recrawled JSONL.
DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed.jsonl"


def _load_seed(seed_path: Path) -> list[dict[str, str]]:
    """Read the JSON-lines seed into a list of dicts.

    Skips blank lines and ``#``-prefixed comment lines so future seed
    updates can keep inline notes. Required keys are ``section`` and
    ``text``; ``title`` is optional.
    """
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
            for key in ("section", "text"):
                if key not in row or not row[key]:
                    raise ValueError(f"{seed_path}:{lineno}: missing required key '{key}'")
            rows.append(row)
    return rows


def build_corpus(
    output_path: Path,
    *,
    seed_path: Path = DEFAULT_SEED_PATH,
    source_version: str | None = None,
) -> int:
    """Write the corpus to ``output_path`` and return the row count.

    Builds into a temp path first so a half-finished run can't corrupt
    an existing database.
    """
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
            "INSERT INTO sections (section, title, text) VALUES (?, ?, ?)",
            [(row["section"], row.get("title"), row["text"]) for row in seed_rows],
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
        description=(
            "Build the Taiwan Trade Secrets Act SQLite/FTS5 corpus from the bundled JSON seed."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home() / ".cache" / "patent_client_agents" / "tw_trade_secrets.db",
        help=(
            "Path to write the corpus to "
            "(default: ~/.cache/patent_client_agents/tw_trade_secrets.db)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=DEFAULT_SEED_PATH,
        help="JSON-lines seed file to ingest (default: bundled seed.jsonl).",
    )
    parser.add_argument(
        "--source-version",
        default=None,
        help="Optional vendor version label (rarely set for TW Trade Secrets).",
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
