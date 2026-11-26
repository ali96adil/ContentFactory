#!/usr/bin/env python3
"""Regression tests for renderer-manifest path containment."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "review_content_package_render", ROOT / "tools" / "review_content_package_render.py"
)
assert SPEC is not None and SPEC.loader is not None
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


def rejected(artifacts: Path, records: object) -> bool:
    try:
        REVIEW.validate_renderer_manifest(artifacts, records)
    except ValueError:
        return True
    return False


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="manifest-path-TEST_ONLY-") as temp_name:
        root = Path(temp_name)
        artifacts = root / "artifacts"
        artifacts.mkdir()
        (artifacts / "short-ar-TEST_ONLY.mp4").write_bytes(b"preview")
        outside = root / "outside-TEST_ONLY.mp4"
        outside.write_bytes(b"outside")
        valid = [{"path": "short-ar-TEST_ONLY.mp4"}]
        REVIEW.validate_renderer_manifest(artifacts, valid)
        assert rejected(artifacts, [{"path": "../outside-TEST_ONLY.mp4"}])
        assert rejected(artifacts, [{"path": str(outside)}])
        assert rejected(artifacts, [{"path": "missing-TEST_ONLY.mp4"}])
        assert rejected(artifacts, [{"path": "unmarked.mp4"}])
        assert rejected(artifacts, [{"path": "short-ar-TEST_ONLY.mp4"}, {"path": "short-ar-TEST_ONLY.mp4"}])
        assert rejected(artifacts, {"path": "short-ar-TEST_ONLY.mp4"})
        link = artifacts / "linked-TEST_ONLY.mp4"
        link.symlink_to(outside)
        assert rejected(artifacts, [{"path": link.name}])
    print("PASS: renderer manifest rejects traversal, absolute/missing/unmarked/duplicate paths and symlinks")


if __name__ == "__main__":
    main()
