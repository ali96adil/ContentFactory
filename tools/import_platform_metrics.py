#!/usr/bin/env python3
"""Idempotently import authorized local metrics CSV rows into a private SQLite ledger."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

from analyze_platform_metrics import load_rows

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab"
ALLOWED_INPUT_ROOTS = (LAB / "imports", LAB / "fixtures", LAB / "evidence")
ALLOWED_DB_ROOTS = (LAB / "imports", LAB / "evidence")
NUMERIC_FIELDS = (
    "age_hours", "impressions", "views", "avg_watch_seconds",
    "duration_seconds", "saves", "shares", "external_cost_usd",
)
IDENTITY_FIELDS = ("platform", "account_id", "post_id", "observed_at")
SCHEMA_VERSION = "1"


class ImportError(ValueError):
    """Raised when a CSV cannot be safely added to the local ledger."""


def contained(path: Path, roots: tuple[Path, ...]) -> bool:
    return any(path.is_relative_to(root.resolve()) for root in roots)


def canonical_row(source: dict[str, str], row_number: int) -> dict[str, str]:
    row = {key: value.strip() for key, value in source.items()}
    for field in ("account_id", "topic_id", "post_id", "language", "format", "observed_at"):
        if not row[field]:
            raise ImportError(f"row {row_number}: {field} must not be empty")
    try:
        observed = datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ImportError(f"row {row_number}: observed_at must be an ISO 8601 date/time") from exc
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ImportError(f"row {row_number}: observed_at must include a UTC offset")
    row["observed_at"] = observed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    for field in NUMERIC_FIELDS:
        try:
            value = Decimal(row[field])
        except InvalidOperation as exc:
            raise ImportError(f"row {row_number}: {field} must be numeric") from exc
        if not value.is_finite():
            raise ImportError(f"row {row_number}: {field} must be finite")
        row[field] = format(value.normalize(), "f")
    return row


def prepare_database(path: Path, source: Path) -> Path:
    if path.suffix.lower() != ".sqlite3":
        raise ImportError("database filename must end in .sqlite3")
    resolved = path.resolve()
    if not contained(resolved, ALLOWED_DB_ROOTS):
        raise ImportError("database must be under lab/imports/ or lab/evidence/")
    if resolved == source or path.is_symlink():
        raise ImportError("database must not be the input file or a symbolic link")
    return resolved


def import_csv(source_path: Path, database_path: Path) -> dict[str, object]:
    source = source_path.resolve()
    if not source.is_file() or not contained(source, ALLOWED_INPUT_ROOTS):
        raise ImportError("input CSV must be a file under lab/imports/, lab/fixtures/, or lab/evidence/")
    rows = load_rows(source)
    if not rows:
        raise ImportError("input CSV must contain at least one data row")
    normalized = [canonical_row(row, index) for index, row in enumerate(rows, start=2)]
    database = prepare_database(database_path, source)
    database.parent.mkdir(parents=True, exist_ok=True)

    inserted = duplicates = 0
    with sqlite3.connect(database, timeout=10, isolation_level=None) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=10000")
        connection.execute("""CREATE TABLE IF NOT EXISTS ledger_meta (
            name TEXT PRIMARY KEY, value TEXT NOT NULL
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS metric_snapshots (
            row_key TEXT PRIMARY KEY,
            content_sha256 TEXT NOT NULL,
            row_json TEXT NOT NULL,
            imported_at_utc TEXT NOT NULL
        )""")
        version = connection.execute(
            "SELECT value FROM ledger_meta WHERE name='schema_version'"
        ).fetchone()
        if version is None:
            connection.execute(
                "INSERT INTO ledger_meta(name,value) VALUES('schema_version',?)",
                (SCHEMA_VERSION,),
            )
        elif version[0] != SCHEMA_VERSION:
            raise ImportError(f"unsupported ledger schema version: {version[0]}")

        connection.execute("BEGIN IMMEDIATE")
        try:
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            for row in normalized:
                identity = json.dumps(
                    [row[field] for field in IDENTITY_FIELDS], ensure_ascii=False,
                    separators=(",", ":"),
                )
                row_key = hashlib.sha256(identity.encode("utf-8")).hexdigest()
                row_json = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                digest = hashlib.sha256(row_json.encode("utf-8")).hexdigest()
                previous = connection.execute(
                    "SELECT content_sha256 FROM metric_snapshots WHERE row_key=?", (row_key,)
                ).fetchone()
                if previous is not None:
                    if previous[0] != digest:
                        raise ImportError("conflicting values for an existing platform post snapshot")
                    duplicates += 1
                    continue
                connection.execute(
                    "INSERT INTO metric_snapshots(row_key,content_sha256,row_json,imported_at_utc) VALUES(?,?,?,?)",
                    (row_key, digest, row_json, now),
                )
                inserted += 1
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        total = connection.execute("SELECT COUNT(*) FROM metric_snapshots").fetchone()[0]

    return {
        "mode": "LOCAL_METRICS_IMPORT",
        "source_row_count": len(normalized),
        "inserted_rows": inserted,
        "duplicate_rows": duplicates,
        "ledger_row_count": total,
        "source_data_origin": "TEST_ONLY" if any(
            "synthetic" in row["data_origin"].lower() or "test_only" in row["data_origin"].lower()
            for row in normalized
        ) else "manual",
        "publishing_enabled": False,
        "external_api_calls": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="authorized local CSV; TEST_ONLY fixtures only test this importer")
    parser.add_argument("--database", type=Path, required=True, help="ignored SQLite file under lab/imports/ or lab/evidence/")
    args = parser.parse_args()
    try:
        print(json.dumps(import_csv(args.input, args.database), ensure_ascii=False, indent=2))
        return 0
    except (OSError, sqlite3.Error, ImportError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
