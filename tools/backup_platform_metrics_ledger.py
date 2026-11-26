#!/usr/bin/env python3
"""Create and restore verified local backups of the private metrics SQLite ledger."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile

from analyze_platform_metrics import load_ledger_rows

ROOT = Path(__file__).resolve().parents[1]
IMPORTS = ROOT / "lab" / "imports"
EVIDENCE = ROOT / "lab" / "evidence"


class BackupError(ValueError):
    """Raised when a backup or restore would violate the local safety contract."""


def rows_digest(rows: list[dict[str, str]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_paths(source: Path, destination: Path, operation: str) -> tuple[Path, Path]:
    if source.is_symlink():
        raise BackupError("source database must not be a symbolic link")
    if destination.is_symlink():
        raise BackupError("destination database must not be a symbolic link")
    source = source.resolve()
    destination = destination.resolve()
    allowed_destinations = (EVIDENCE,) if operation == "backup" else (EVIDENCE, IMPORTS)
    if not any(source.is_relative_to(root.resolve()) for root in (EVIDENCE, IMPORTS)):
        raise BackupError("source database must be under lab/imports/ or lab/evidence/")
    if not any(destination.is_relative_to(root.resolve()) for root in allowed_destinations):
        raise BackupError("backup destination must be under lab/evidence/" if operation == "backup"
                          else "restore destination must be under lab/imports/ or lab/evidence/")
    if source == destination or destination.suffix.lower() != ".sqlite3":
        raise BackupError("source and destination must differ; destination must end in .sqlite3")
    if not source.is_file():
        raise FileNotFoundError(f"source ledger not found: {source}")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing database: {destination}")
    return source, destination


def copy_ledger(source_path: Path, destination_path: Path, operation: str) -> dict[str, object]:
    if operation not in {"backup", "restore"}:
        raise BackupError("operation must be backup or restore")
    source, destination = validate_paths(source_path, destination_path, operation)
    source_rows = load_ledger_rows(source)
    expected_digest = rows_digest(source_rows)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".partial.sqlite3", dir=destination.parent
    )
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        os.chmod(temporary, 0o600)
        with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as source_db:
            with sqlite3.connect(temporary) as destination_db:
                source_db.backup(destination_db)
        copied_rows = load_ledger_rows(temporary)
        if rows_digest(copied_rows) != expected_digest:
            raise BackupError("backup verification failed: restored row digest differs")
        # Hard-link creation is atomic and fails instead of replacing a concurrently-created destination.
        os.link(temporary, destination)
        temporary.unlink()
    finally:
        temporary.unlink(missing_ok=True)

    digest = hashlib.sha256()
    with destination.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "mode": "LOCAL_METRICS_LEDGER_BACKUP" if operation == "backup" else "LOCAL_METRICS_LEDGER_RESTORE",
        "row_count": len(copied_rows),
        "content_sha256": expected_digest,
        "database_sha256": digest.hexdigest(),
        "database_bytes": destination.stat().st_size,
        "destination": str(destination.relative_to(ROOT)),
        "external_api_calls": False,
        "publishing_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("backup", "restore"))
    parser.add_argument("source", type=Path, help="existing valid local metrics ledger")
    parser.add_argument("--destination", type=Path, required=True, help="new .sqlite3 path in an ignored local folder")
    args = parser.parse_args()
    try:
        print(json.dumps(copy_ledger(args.source, args.destination, args.operation), ensure_ascii=False, indent=2))
        return 0
    except (OSError, sqlite3.Error, BackupError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
