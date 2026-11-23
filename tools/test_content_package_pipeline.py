#!/usr/bin/env python3
"""Acceptance checks for the TEST_ONLY package-to-media path; all temporary outputs stay in lab/evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "lab" / "evidence"
PACKAGE = ROOT / "lab" / "fixtures" / "content-package-demo-TEST_ONLY.json"
CONVERTER = ROOT / "tools" / "render_content_package.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CONVERTER), *args], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not PACKAGE.is_file():
        raise SystemExit(f"missing acceptance input: {PACKAGE}")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="content-package-acceptance-TEST_ONLY-", dir=EVIDENCE) as temp_name:
        temp = Path(temp_name)
        missing_output = temp / "missing-file-TEST_ONLY"
        missing = run("--input", str(temp / "absent-TEST_ONLY.json"), "--output", str(missing_output))
        assert missing.returncode != 0 and not missing_output.exists()
        assert not missing_output.with_name(f".{missing_output.name}.work").exists()

        incomplete_path = temp / "incomplete-package-TEST_ONLY.json"
        incomplete = json.loads(PACKAGE.read_text(encoding="utf-8"))
        incomplete["copy"]["en"]["short_video"].pop("voiceover")
        incomplete_path.write_text(json.dumps(incomplete, ensure_ascii=False), encoding="utf-8")
        incomplete_output = temp / "incomplete-output-TEST_ONLY"
        rejected = run("--input", str(incomplete_path), "--output", str(incomplete_output))
        assert rejected.returncode != 0 and "voiceover" in rejected.stderr
        assert not incomplete_output.exists()
        assert not incomplete_output.with_name(f".{incomplete_output.name}.work").exists()

        non_finite_path = temp / "non-finite-duration-TEST_ONLY.json"
        non_finite = json.loads(PACKAGE.read_text(encoding="utf-8"))
        non_finite["copy"]["en"]["youtube_long"]["target_duration_minutes"] = float("nan")
        non_finite_path.write_text(json.dumps(non_finite, ensure_ascii=False), encoding="utf-8")
        non_finite_output = temp / "non-finite-output-TEST_ONLY"
        rejected_non_finite = run("--input", str(non_finite_path), "--output", str(non_finite_output))
        assert rejected_non_finite.returncode != 0 and "target_duration_minutes" in rejected_non_finite.stderr
        assert not non_finite_output.exists()
        assert not non_finite_output.with_name(f".{non_finite_output.name}.work").exists()

        output = temp / "resumable-run-TEST_ONLY"
        interrupted = run("--input", str(PACKAGE), "--output", str(output),
                          "--platform", "all", "--preview-seconds", "1",
                          "--visual-direction", "fieldnotes",
                          "--test-interrupt-after-svg-count", "1")
        work = output.with_name(f".{output.name}.work")
        assert interrupted.returncode == 75
        assert not output.exists() and work.is_dir()
        state = json.loads((work / "job.json").read_text(encoding="utf-8"))
        assert state["stage"] == "vector_rendering"
        assert len(list((work / "svg").rglob("*.svg"))) == 1

        wrong_direction_resume = run("--input", str(PACKAGE), "--output", str(output),
                                     "--platform", "all", "--preview-seconds", "1",
                                     "--visual-direction", "gallery", "--resume")
        assert wrong_direction_resume.returncode != 0 and "resume refused" in wrong_direction_resume.stderr
        assert work.is_dir()

        resumed = run("--input", str(PACKAGE), "--output", str(output), "--platform", "all",
                      "--preview-seconds", "1", "--visual-direction", "fieldnotes", "--resume")
        assert resumed.returncode == 0, resumed.stderr[-4000:]
        assert output.is_dir() and not work.exists()
        artifacts = output / "artifacts"
        videos = sorted(artifacts.glob("short-*-TEST_ONLY.mp4"))
        carousels = sorted(artifacts.glob("carousel-*-TEST_ONLY.png"))
        storyboards = sorted(artifacts.glob("youtube-long-storyboard-*-TEST_ONLY.md"))
        assert len(videos) == 2 and len(carousels) == 10 and len(storyboards) == 2
        report = json.loads((artifacts / "render-report.json").read_text(encoding="utf-8"))
        assert report["visual_direction"] == "fieldnotes"
        assert report["external_publication_enabled"] is False and report["external_publication_approved"] is False
        assert report["audio_present"] is False
        assert all(item["audio_present"] is False for item in report["artifacts"] if item["kind"] == "short_video")

        report_hash = sha256(artifacts / "render-report.json")
        overwrite = run("--input", str(PACKAGE), "--output", str(output), "--platform", "all",
                        "--preview-seconds", "1", "--visual-direction", "fieldnotes")
        assert overwrite.returncode != 0 and "refusing to overwrite" in overwrite.stderr
        assert sha256(artifacts / "render-report.json") == report_hash

    print("PASS: missing/incomplete/non-finite package inputs rejected; interrupted fieldnotes render resumed; changed direction rejected on resume; silent TEST_ONLY outputs rendered; overwrite refused without changing report")


if __name__ == "__main__":
    main()
