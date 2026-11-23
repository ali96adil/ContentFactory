#!/usr/bin/env python3
"""Regression checks for the local, non-publishing metrics analyzer."""

from __future__ import annotations

import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
