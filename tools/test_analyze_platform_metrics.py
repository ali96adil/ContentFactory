#!/usr/bin/env python3
"""Regression checks for the local, non-publishing metrics analyzer."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from analyze_platform_metrics import compare, load_rows, number


ROOT = Path(__file__).resolve().parents[1]


class AnalyzePlatformMetricsTests(unittest.TestCase):
    def test_synthetic_fixture_never_authorizes_action(self) -> None:
        result = compare(load_rows(ROOT / "lab/fixtures/platform-metrics-TEST_ONLY.csv"))

        self.assertEqual(result["mode"], "TEST_ONLY_SYNTHETIC")
        self.assertFalse(result["scale_eligible"])
        self.assertFalse(result["export_allowed"])
        self.assertFalse(result["publish_allowed"])
        self.assertTrue(result["decisions"])
        self.assertEqual(
            {row["recommendation"] for row in result["decisions"]},
            {"test_only_no_action"},
        )

    def test_numeric_fields_reject_invalid_or_non_finite_values(self) -> None:
        for value in ("", "not-a-number", "NaN", "Infinity", "-Infinity", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                number({"metric": value}, "metric")

    def test_numeric_fields_accept_zero_and_finite_values(self) -> None:
        self.assertEqual(number({"metric": "0"}, "metric"), 0)
        self.assertEqual(number({"metric": "12.5"}, "metric"), 12.5)

    def test_import_requires_known_data_provenance(self) -> None:
        source = ROOT / "lab/fixtures/platform-metrics-TEST_ONLY.csv"
        with source.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            headers = reader.fieldnames
            rows = list(reader)
        rows[0]["data_origin"] = ""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "unknown-origin.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "data_origin"):
                load_rows(path)

    def test_import_rejects_short_or_overlong_rows(self) -> None:
        source = ROOT / "lab/fixtures/platform-metrics-TEST_ONLY.csv"
        with source.open(encoding="utf-8") as stream:
            lines = stream.readlines()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.csv"
            path.write_text("".join(lines[:2]).rstrip("\n") + ",extra\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "more values"):
                load_rows(path)

            short_row = lines[1].rstrip("\n").rsplit(",", 1)[0]
            path.write_text(lines[0] + short_row + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fewer values"):
                load_rows(path)


if __name__ == "__main__":
    unittest.main()
