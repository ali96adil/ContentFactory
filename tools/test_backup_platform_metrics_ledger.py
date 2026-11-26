#!/usr/bin/env python3
"""Verify SQLite online backup/restore without replacing existing ledgers."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from analyze_platform_metrics import load_ledger_rows

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "lab" / "evidence"
FIXTURE = ROOT / "lab" / "fixtures" / "platform-metrics-TEST_ONLY.csv"
IMPORT_SPEC = importlib.util.spec_from_file_location(
    "import_platform_metrics", ROOT / "tools" / "import_platform_metrics.py"
)
BACKUP_SPEC = importlib.util.spec_from_file_location(
    "backup_platform_metrics_ledger", ROOT / "tools" / "backup_platform_metrics_ledger.py"
)
assert IMPORT_SPEC is not None and IMPORT_SPEC.loader is not None
assert BACKUP_SPEC is not None and BACKUP_SPEC.loader is not None
IMPORTER = importlib.util.module_from_spec(IMPORT_SPEC)
IMPORT_SPEC.loader.exec_module(IMPORTER)
BACKUP = importlib.util.module_from_spec(BACKUP_SPEC)
BACKUP_SPEC.loader.exec_module(BACKUP)


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="metrics-backup-TEST_ONLY-", dir=EVIDENCE) as temp_name:
        temp = Path(temp_name)
        source = temp / "source.sqlite3"
        backup = temp / "backup.sqlite3"
        restored = temp / "restored.sqlite3"
        IMPORTER.import_csv(FIXTURE, source)
        source_rows = load_ledger_rows(source)
        source_digest = BACKUP.rows_digest(source_rows)

        backup_result = BACKUP.copy_ledger(source, backup, "backup")
        restore_result = BACKUP.copy_ledger(backup, restored, "restore")
        assert backup_result["row_count"] == restore_result["row_count"] == 26
        assert backup_result["content_sha256"] == restore_result["content_sha256"] == source_digest
        assert BACKUP.rows_digest(load_ledger_rows(restored)) == source_digest
        assert backup.stat().st_mode & 0o777 == 0o600

        backup_hash = file_sha(backup)
        try:
            BACKUP.copy_ledger(source, backup, "backup")
        except FileExistsError:
            pass
        else:
            raise AssertionError("backup overwrote an existing destination")
        assert file_sha(backup) == backup_hash

        invalid = temp / "invalid.sqlite3"
        with sqlite3.connect(invalid) as connection:
            connection.execute("CREATE TABLE not_a_ledger (value TEXT)")
        try:
            BACKUP.copy_ledger(invalid, temp / "invalid-backup.sqlite3", "backup")
        except ValueError:
            pass
        else:
            raise AssertionError("invalid source database was backed up")

    print("PASS: SQLite backup/restore preserves 26 TEST_ONLY rows and digest; existing destinations and invalid ledgers reject")


if __name__ == "__main__":
    main()
