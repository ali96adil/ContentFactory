#!/usr/bin/env python3
"""Check that package claims resolve through unique, well-formed source IDs."""
from __future__ import annotations

import copy
import hashlib
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


def valid_claim(**overrides: object) -> dict[str, object]:
    claim: dict[str, object] = {
        "claim_id": "c1", "text_ar_white": "حقيقة", "text_en": "Fact",
        "claim_type": "general", "review_status": "approved",
        "reviewer_alias": "reviewer-1", "reviewed_at_utc": "2026-11-25T12:00:00Z",
        "source_ids": ["s1"], "notes": "",
    }
    claim.update(overrides)
    return claim


def valid_asset(asset_id: str) -> dict[str, object]:
    path = ROOT / "lab" / "fixtures" / "content-package-demo-TEST_ONLY.json"
    return {
        "asset_id": asset_id, "kind": "reference", "rights_status": "verified",
        "source_url": "https://example.test/source", "license_name": "Example",
        "license_url": "https://example.test/license", "path": "lab/fixtures/content-package-demo-TEST_ONLY.json",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


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
    missing_claim_id["fact_base"]["claims"] = [valid_claim(claim_id="")]
    expect_rejected(missing_claim_id, "claim_id")

    malformed_reference = copy.deepcopy(base)
    malformed_reference["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    malformed_reference["fact_base"]["claims"] = [valid_claim(source_ids=[{"id": "s1"}])]
    expect_rejected(malformed_reference, "must reference existing sources")

    duplicate_claims = copy.deepcopy(base)
    duplicate_claims["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    claim = valid_claim()
    duplicate_claims["fact_base"]["claims"] = [claim, copy.deepcopy(claim)]
    expect_rejected(duplicate_claims, "claim_id must be unique")

    missing_reviewer = copy.deepcopy(base)
    missing_reviewer["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    missing_reviewer["fact_base"]["claims"] = [valid_claim(reviewer_alias="")]
    expect_rejected(missing_reviewer, "reviewer_alias")

    non_utc_review = copy.deepcopy(base)
    non_utc_review["sources"] = [{"source_id": "s1", "url": "https://example.test/a"}]
    non_utc_review["fact_base"]["claims"] = [
        valid_claim(reviewed_at_utc="2026-11-25T15:00:00+03:00")
    ]
    expect_rejected(non_utc_review, "must use UTC")

    duplicate_assets = copy.deepcopy(base)
    duplicate_assets["assets"] = [valid_asset("same"), valid_asset("same")]
    expect_rejected(duplicate_assets, "asset_id must be unique")

    malformed_asset_digest = copy.deepcopy(base)
    malformed_asset_digest["assets"] = [valid_asset("asset-1") | {"sha256": "not-a-digest"}]
    expect_rejected(malformed_asset_digest, "64-character hexadecimal SHA-256")

    uppercase_digest = copy.deepcopy(base)
    uppercase_asset = valid_asset("asset-upper")
    uppercase_asset["sha256"] = str(uppercase_asset["sha256"]).upper()
    uppercase_digest["assets"] = [uppercase_asset]
    RENDER.validate_package(uppercase_digest, FIXTURE, "all", 1)
    print("PASS: unique IDs, required review metadata, valid source references, and asset checksum validation")


if __name__ == "__main__":
    main()
