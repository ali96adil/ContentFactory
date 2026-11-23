#!/usr/bin/env python3
"""Exercise local metrics ledger idempotency, conflicts, and path boundaries."""
from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory

from analyze_platform_metrics import compare, load_ledger_rows

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "lab" / "evidence"
FIXTURE = ROOT / "lab" / "fixtures" / "platform-metrics-TEST_ONLY.csv"
SPEC = importlib.util.spec_from_file_location(
    "import_platform_metrics", ROOT / "tools" / "import_platform_metrics.py"
)
assert SPEC is not None and SPEC.loader is not None
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def read_fixture() -> tuple[list[str], list[dict[str, str]]]:
    with FIXTURE.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames is not None
        return reader.fieldnames, list(reader)


def write_rows(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="metrics-ledger-TEST_ONLY-", dir=EVIDENCE) as temp_name:
        temp = Path(temp_name)
        database = temp / "metrics.sqlite3"
        headers, original = read_fixture()

        first = IMPORTER.import_csv(FIXTURE, database)
        second = IMPORTER.import_csv(FIXTURE, database)
        assert first["source_row_count"] == 26 and first["inserted_rows"] == 26
        assert first["ledger_row_count"] == 26 and first["source_data_origin"] == "TEST_ONLY"
        assert second["inserted_rows"] == 0 and second["duplicate_rows"] == 26
        assert second["ledger_row_count"] == 26
        ledger_rows = load_ledger_rows(database)
        analysis = compare(ledger_rows)
        assert len(ledger_rows) == 26 and analysis["mode"] == "TEST_ONLY_SYNTHETIC"
        assert analysis["publish_allowed"] is False
        cli = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "analyze_platform_metrics.py"),
             "--ledger", str(database)],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
        cli_result = json.loads(cli.stdout)
        assert cli_result["mode"] == "TEST_ONLY_SYNTHETIC"
        assert cli_result["export_allowed"] is False and cli_result["publish_allowed"] is False

        equivalent_time = [dict(row) for row in original]
        equivalent_time[0]["observed_at"] = "2026-11-01T15:00:00+03:00"
        equivalent_path = temp / "equivalent-time-TEST_ONLY.csv"
        write_rows(equivalent_path, headers, equivalent_time)
        normalized = IMPORTER.import_csv(equivalent_path, database)
        assert normalized["inserted_rows"] == 0 and normalized["duplicate_rows"] == 26

        concurrent_database = temp / "concurrent.sqlite3"
        with ThreadPoolExecutor(max_workers=2) as pool:
            concurrent_results = list(pool.map(
                lambda _: IMPORTER.import_csv(FIXTURE, concurrent_database), range(2)
            ))
        assert sum(result["inserted_rows"] for result in concurrent_results) == 26
        assert sum(result["duplicate_rows"] for result in concurrent_results) == 26
        assert all(result["ledger_row_count"] == 26 for result in concurrent_results)

        tampered_database = temp / "tampered.sqlite3"
        IMPORTER.import_csv(FIXTURE, tampered_database)
        with sqlite3.connect(tampered_database) as connection:
            connection.execute("UPDATE metric_snapshots SET content_sha256='invalid'")
        try:
            load_ledger_rows(tampered_database)
        except ValueError as exc:
            assert "integrity check" in str(exc)
        else:
            raise AssertionError("tampered metrics ledger was accepted")

        conflicting = [dict(row) for row in original]
        extra = dict(conflicting[0], post_id="new-post-rollback", topic_id="new-topic")
        conflicting.insert(0, extra)
        conflicting[1]["impressions"] = "10001"
        conflict_path = temp / "conflict-TEST_ONLY.csv"
        write_rows(conflict_path, headers, conflicting)
        try:
            IMPORTER.import_csv(conflict_path, database)
        except IMPORTER.ImportError as exc:
            assert "conflicting values" in str(exc)
        else:
            raise AssertionError("conflicting historical snapshot was accepted")
        with sqlite3.connect(database) as connection:
            count = connection.execute("SELECT COUNT(*) FROM metric_snapshots").fetchone()[0]
        assert count == 26, "failed batch must roll back newly inserted rows"

        naive = [dict(row) for row in original]
        naive[0]["observed_at"] = "2026-11-01T12:00:00"
        naive_path = temp / "naive-time-TEST_ONLY.csv"
        write_rows(naive_path, headers, naive)
        try:
            IMPORTER.import_csv(naive_path, database)
        except IMPORTER.ImportError as exc:
            assert "UTC offset" in str(exc)
        else:
            raise AssertionError("naive timestamp was accepted")

        try:
            IMPORTER.import_csv(FIXTURE, ROOT / "unsafe-test-ledger.sqlite3")
        except IMPORTER.ImportError as exc:
            assert "under lab/imports" in str(exc)
        else:
            raise AssertionError("database outside ignored local data paths was accepted")

        empty_path = temp / "empty-TEST_ONLY.csv"
        write_rows(empty_path, headers, [])
        try:
            IMPORTER.import_csv(empty_path, database)
        except IMPORTER.ImportError as exc:
            assert "at least one data row" in str(exc)
        else:
            raise AssertionError("empty CSV was accepted")

        linked_database = temp / "linked.sqlite3"
        linked_database.symlink_to(database)
        try:
            IMPORTER.import_csv(FIXTURE, linked_database)
        except IMPORTER.ImportError as exc:
            assert "symbolic link" in str(exc)
        else:
            raise AssertionError("symlink database path was accepted")

    print("PASS: metrics imports are idempotent and concurrency-safe; UTC aliases dedupe; conflicts roll back; unsafe inputs/DB paths reject")


if __name__ == "__main__":
    main()
