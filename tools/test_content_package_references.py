#!/usr/bin/env python3
"""Check that package claims resolve through unique, well-formed source IDs."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "lab" / "fixtures" / "content-package-demo-TEST_ONLY.json"
SPEC = importlib.util.spec_from_file_location(
    "render_content_package", ROOT / "tools" / "render_content_package.py"
)
assert SPEC is not None and SPEC.loader is not None
RENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER)


def expect_rejected(package: dict[str, object], message: str) -> None:
    try:
        RENDER.validate_package(package, FIXTURE, "all", 1)
    except RENDER.PackageError as exc:
        assert message in str(exc), str(exc)
    else:
        raise AssertionError(f"invalid package was accepted: {message}")


def main() -> None:
    base = json.loads(FIXTURE.read_text(encoding="utf-8"))
    duplicate_sources = copy.deepcopy(base)
    duplicate_sources["sources"] = [
        {"source_id": "same", "url": "https://example.test/a"},
        {"source_id": "same", "url": "https://example.test/b"},
    ]
    expect_rejected(duplicate_sources, "source_id must be unique")

    missing_claim_id = copy.deepcopy(base)
    missing_claim_id["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    missing_claim_id["fact_base"]["claims"] = [{
        "review_status": "approved", "source_ids": ["s1"]
    }]
    expect_rejected(missing_claim_id, "claim_id")

    malformed_reference = copy.deepcopy(base)
    malformed_reference["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    malformed_reference["fact_base"]["claims"] = [{
        "claim_id": "c1", "review_status": "approved", "source_ids": [{"id": "s1"}]
    }]
    expect_rejected(malformed_reference, "must reference existing sources")

    duplicate_claims = copy.deepcopy(base)
    duplicate_claims["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    claim = {"claim_id": "c1", "review_status": "approved", "source_ids": ["s1"]}
    duplicate_claims["fact_base"]["claims"] = [claim, copy.deepcopy(claim)]
    expect_rejected(duplicate_claims, "claim_id must be unique")
    print("PASS: duplicate source/claim IDs, missing claim IDs, and malformed references reject")


if __name__ == "__main__":
    main()
