#!/usr/bin/env python3
"""Regression tests for privacy-safe media evaluation recording."""

from __future__ import annotations

import csv
from pathlib import Path
import tempfile

from record_media_evaluation import FIELDS, ROOT, append_row, asset_reference


def sample_row() -> dict[str, object]:
    return {field: "" for field in FIELDS}


def main() -> None:
    evidence = ROOT / "lab" / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="record-media-evaluation-TEST_ONLY-", dir=evidence) as asset_dir:
        asset = Path(asset_dir) / "asset-TEST_ONLY.bin"
        asset.write_bytes(b"TEST_ONLY")
        with tempfile.TemporaryDirectory(prefix="record-media-evaluation-") as temp_name:
            temp = Path(temp_name)
            resolved, reference = asset_reference(asset)
            assert resolved == asset.resolve()
            assert reference.endswith("/asset-TEST_ONLY.bin")

            row = sample_row()
            row["asset"] = reference
            output = temp / "results.csv"
            append_row(output, row)
            with output.open(newline="", encoding="utf-8") as stream:
                records = list(csv.DictReader(stream))
            assert len(records) == 1 and records[0]["asset"] == reference

            invalid = temp / "invalid.csv"
            invalid.write_text("wrong,header\nkeep,this\n", encoding="utf-8")
            original = invalid.read_bytes()
            try:
                append_row(invalid, row)
            except ValueError as exc:
                assert "header" in str(exc)
            else:
                raise AssertionError("mismatched CSV schema was accepted")
            assert invalid.read_bytes() == original

            outside = temp / "outside.bin"
            outside.write_bytes(b"private")
            try:
                asset_reference(outside)
            except ValueError as exc:
                assert "inside the repository" in str(exc)
            else:
                raise AssertionError("external asset path was accepted")

            link = temp / "output-link.csv"
            link.symlink_to(output)
            try:
                append_row(link, row)
            except ValueError as exc:
                assert "symbolic link" in str(exc)
            else:
                raise AssertionError("symbolic-link output was accepted")

    print("PASS: asset references stay repository-relative; invalid schemas and symlink outputs are rejected without changing files")


if __name__ == "__main__":
    main()
