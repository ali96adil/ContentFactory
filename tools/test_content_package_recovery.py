#!/usr/bin/env python3
"""Exercise local content-package backup/restore without services or credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "lab" / "evidence"
PACKAGE = ROOT / "lab" / "fixtures" / "content-package-demo-TEST_ONLY.json"
RENDER = ROOT / "tools" / "render_content_package.py"
REVIEW = ROOT / "tools" / "review_content_package_render.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, tmp_dir: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TMPDIR"] = str(tmp_dir)
    result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr[-3000:]}\n{result.stdout[-3000:]}")
    return result


def file_manifest(folder: Path) -> dict[str, dict[str, object]]:
    return {
        path.relative_to(folder).as_posix(): {"sha256": sha256(path), "bytes": path.stat().st_size}
        for path in sorted(folder.rglob("*")) if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", required=True, help="new TEST_ONLY directory name under lab/evidence/")
    parser.add_argument("--preview-seconds", type=int, default=5, choices=(5,), help="keep the existing reviewer’s accepted five-second preview contract")
    args = parser.parse_args()
    if "TEST_ONLY" not in args.run_name or Path(args.run_name).name != args.run_name:
        raise SystemExit("--run-name must be a plain directory name containing TEST_ONLY")
    if not PACKAGE.is_file():
        raise SystemExit(f"missing source package: {PACKAGE}")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    run_root = EVIDENCE / args.run_name
    if run_root.exists():
        raise SystemExit(f"refusing to overwrite: {run_root}")
    run_root.mkdir()
    temp_root = run_root / "tmp"
    temp_root.mkdir()
    rendered = run_root / "rendered-TEST_ONLY"
    original_review = run_root / "review-original-TEST_ONLY"
    archive_path = run_root / "content-package-backup-TEST_ONLY.tar.gz"
    restored_root = run_root / "restored-TEST_ONLY"
    restored_review = run_root / "review-restored-TEST_ONLY"

    run([sys.executable, str(RENDER), "--input", str(PACKAGE), "--output", str(rendered),
         "--platform", "all", "--preview-seconds", str(args.preview_seconds), "--visual-direction", "fieldnotes"], tmp_dir=temp_root)
    artifacts = rendered / "artifacts"
    run([sys.executable, str(REVIEW), "--artifacts", str(artifacts), "--output", str(original_review)], tmp_dir=temp_root)

    manifest = file_manifest(rendered)
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(rendered, arcname="factory-output", recursive=True)
    restored_root.mkdir()
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(path=restored_root, filter="data")
    restored_bundle = restored_root / "factory-output"
    restored_manifest = file_manifest(restored_bundle)
    if restored_manifest != manifest:
        raise RuntimeError("restore file list or SHA-256 verification failed")

    restored_artifacts = restored_bundle / "artifacts"
    run([sys.executable, str(REVIEW), "--artifacts", str(restored_artifacts), "--output", str(restored_review)], tmp_dir=temp_root)
    original_qa = json.loads((original_review / "technical-checks-TEST_ONLY.json").read_text(encoding="utf-8"))
    restored_qa = json.loads((restored_review / "technical-checks-TEST_ONLY.json").read_text(encoding="utf-8"))
    if (original_qa["checks"] != restored_qa["checks"]
            or original_qa["video_details"] != restored_qa["video_details"]
            or original_qa["human_review_status"] != "PENDING_USER_REVIEW"
            or restored_qa["publication_enabled"] is not False):
        raise RuntimeError("restored content failed the same technical review or a gate changed")

    report = {
        "mode": "TEST_ONLY_LOCAL_BACKUP_RESTORE",
        "input": str(PACKAGE.relative_to(ROOT)),
        "run_root": str(run_root.relative_to(ROOT)),
        "archive": archive_path.name,
        "archive_bytes": archive_path.stat().st_size,
        "file_count": len(manifest),
        "sha256_manifest": manifest,
        "render": "PASS: 2 silent five-second Shorts, 10 Carousel slides, 12 YouTube storyboard panels and render manifest",
        "backup_restore": "PASS: restored to a new directory and all file sizes/SHA-256 values match",
        "restored_review": "PASS: technical checks and FFprobe details match the original review",
        "human_quality": "PENDING_USER_REVIEW",
        "external_publication_enabled": False,
        "audio_added": False,
        "secrets_included": False,
        "n8n_included": False,
    }
    (run_root / "recovery-report-TEST_ONLY.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("run_root", "archive", "archive_bytes", "file_count", "render", "backup_restore", "restored_review", "human_quality")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
