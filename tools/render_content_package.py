#!/usr/bin/env python3
"""Validate a TEST_ONLY content package and render local previews through existing SVG/FFmpeg tools."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import resource
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab"
EVIDENCE = LAB / "evidence"
MOTION = LAB / "motion.mjs"
RENDER_MAC = LAB / "render_mac.py"
PLATFORMS = {"youtube", "tiktok", "instagram", "facebook"}
LOCALES = ("ar_white", "en")
FORMATS = ("short_video", "carousel", "youtube_long")
FPS = 24


class PackageError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_string(obj: object, path: str) -> str:
    if not isinstance(obj, str) or not obj.strip():
        raise PackageError(f"{path} must be a non-empty string")
    return obj.strip()


def validate_package(pkg: object, input_path: Path, selected_platform: str, preview_seconds: int) -> dict[str, object]:
    if not isinstance(pkg, dict):
        raise PackageError("package root must be a JSON object")
    if pkg.get("contract_version") != "content-package.v1":
        raise PackageError("contract_version must be content-package.v1")
    lifecycle = pkg.get("lifecycle")
    if not isinstance(lifecycle, dict) or lifecycle.get("test_only") is not True:
        raise PackageError("refusing package without lifecycle.test_only=true")
    if "TEST_ONLY" not in input_path.name and "TEST_ONLY" not in str(pkg.get("package_id", "")):
        raise PackageError("TEST_ONLY marker is required in input filename or package_id")
    require_string(pkg.get("package_id"), "package_id")
    require_string(pkg.get("revision"), "revision")

    topic = pkg.get("topic")
    if not isinstance(topic, dict):
        raise PackageError("topic must be an object")
    for key in ("topic_id", "audience", "viewer_need"):
        require_string(topic.get(key), f"topic.{key}")
    titles = topic.get("working_title")
    if not isinstance(titles, dict):
        raise PackageError("topic.working_title must contain ar_white and en")
    for locale in LOCALES:
        require_string(titles.get(locale), f"topic.working_title.{locale}")
    promises = topic.get("single_promise")
    if not isinstance(promises, dict):
        raise PackageError("topic.single_promise must contain ar_white and en")
    for locale in LOCALES:
        require_string(promises.get(locale), f"topic.single_promise.{locale}")

    sources = pkg.get("sources")
    fact_base = pkg.get("fact_base")
    if not isinstance(fact_base, dict):
        raise PackageError("fact_base must be an object")
    claims = fact_base.get("claims")
    assets = pkg.get("assets")
    if not isinstance(sources, list) or not isinstance(claims, list) or not isinstance(assets, list):
        raise PackageError("sources, fact_base.claims, and assets must be arrays")
    source_ids = set()
    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            raise PackageError(f"sources[{i}] must be an object")
        source_id = require_string(source.get("source_id"), f"sources[{i}].source_id")
        if source_id in source_ids:
            raise PackageError(f"sources[{i}].source_id must be unique")
        source_ids.add(source_id)
        require_string(source.get("url"), f"sources[{i}].url")
    claim_ids = set()
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            raise PackageError(f"fact_base.claims[{i}] must be an object")
        claim_id = require_string(claim.get("claim_id"), f"fact_base.claims[{i}].claim_id")
        if claim_id in claim_ids:
            raise PackageError(f"fact_base.claims[{i}].claim_id must be unique")
        claim_ids.add(claim_id)
        if claim.get("review_status") != "approved":
            raise PackageError(f"fact_base.claims[{i}] lacks approved fact review")
        for key in ("text_ar_white", "text_en", "claim_type", "reviewer_alias"):
            require_string(claim.get(key), f"fact_base.claims[{i}].{key}")
        reviewed_at = require_string(claim.get("reviewed_at_utc"),
                                     f"fact_base.claims[{i}].reviewed_at_utc")
        try:
            parsed_reviewed_at = datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise PackageError(
                f"fact_base.claims[{i}].reviewed_at_utc must be a UTC ISO-8601 timestamp"
            ) from exc
        if parsed_reviewed_at.utcoffset() != timezone.utc.utcoffset(parsed_reviewed_at):
            raise PackageError(
                f"fact_base.claims[{i}].reviewed_at_utc must use UTC"
            )
        references = claim.get("source_ids")
        if (not isinstance(references, list) or not references
                or any(not isinstance(ref, str) or not ref.strip() for ref in references)
                or not set(references).issubset(source_ids)):
            raise PackageError(f"fact_base.claims[{i}] must reference existing sources")
    asset_ids = set()
    for i, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise PackageError(f"assets[{i}] must be an object")
        asset_id = require_string(asset.get("asset_id"), f"assets[{i}].asset_id")
        if asset_id in asset_ids:
            raise PackageError(f"assets[{i}].asset_id must be unique")
        asset_ids.add(asset_id)
        if asset.get("rights_status") != "verified":
            raise PackageError(f"assets[{i}] lacks verified rights")
        for key in ("source_url", "license_name", "license_url", "sha256", "path"):
            require_string(asset.get(key), f"assets[{i}].{key}")
        if (len(asset["sha256"]) != 64
                or any(char not in "0123456789abcdefABCDEF" for char in asset["sha256"])):
            raise PackageError(f"assets[{i}].sha256 must be a 64-character hexadecimal SHA-256 digest")
        asset_path = (ROOT / asset["path"]).resolve()
        if not asset_path.is_relative_to(LAB.resolve()) or not asset_path.is_file():
            raise PackageError(f"assets[{i}].path must be an existing local file under lab/")
        if sha256(asset_path) != asset["sha256"].lower():
            raise PackageError(f"assets[{i}].sha256 does not match the local file")

    copy = pkg.get("copy")
    if not isinstance(copy, dict) or set(LOCALES) - set(copy):
        raise PackageError("copy must contain ar_white and en")
    normalized_copy = {}
    for locale in LOCALES:
        locale_copy = copy[locale]
        if not isinstance(locale_copy, dict) or set(FORMATS) - set(locale_copy):
            raise PackageError(f"copy.{locale} must include short_video, carousel, youtube_long")
        short = locale_copy["short_video"]
        if not isinstance(short, dict):
            raise PackageError(f"copy.{locale}.short_video must be an object")
        for key in ("hook", "voiceover", "caption", "call_to_action"):
            require_string(short.get(key), f"copy.{locale}.short_video.{key}")
        if not isinstance(short.get("on_screen_text"), list) or not short["on_screen_text"]:
            raise PackageError(f"copy.{locale}.short_video.on_screen_text must be a non-empty array")
        if any(not isinstance(line, str) or not line.strip() for line in short["on_screen_text"]):
            raise PackageError(f"copy.{locale}.short_video.on_screen_text entries must be non-empty strings")
        seconds = short.get("target_duration_seconds")
        if not isinstance(seconds, int) or isinstance(seconds, bool) or not 1 <= seconds <= 60:
            raise PackageError(f"copy.{locale}.short_video.target_duration_seconds must be an integer from 1 to 60")
        if preview_seconds > seconds:
            raise PackageError(f"preview duration exceeds copy.{locale}.short_video.target_duration_seconds")
        carousel = locale_copy["carousel"]
        if not isinstance(carousel, dict):
            raise PackageError(f"copy.{locale}.carousel must be an object")
        require_string(carousel.get("caption"), f"copy.{locale}.carousel.caption")
        require_string(carousel.get("call_to_action"), f"copy.{locale}.carousel.call_to_action")
        require_string(carousel.get("target_aspect_ratio"), f"copy.{locale}.carousel.target_aspect_ratio")
        slides = carousel.get("slides")
        if not isinstance(slides, list) or len(slides) < 2:
            raise PackageError(f"copy.{locale}.carousel.slides must contain at least two slides")
        for i, slide in enumerate(slides):
            if not isinstance(slide, dict):
                raise PackageError(f"copy.{locale}.carousel.slides[{i}] must be an object")
            for key in ("heading", "body", "visual_note"):
                require_string(slide.get(key), f"copy.{locale}.carousel.slides[{i}].{key}")
        long = locale_copy["youtube_long"]
        if not isinstance(long, dict):
            raise PackageError(f"copy.{locale}.youtube_long must be an object")
        for key in ("title", "opening", "ending", "description"):
            require_string(long.get(key), f"copy.{locale}.youtube_long.{key}")
        minutes = long.get("target_duration_minutes")
        try:
            valid_minutes = (isinstance(minutes, (int, float)) and not isinstance(minutes, bool)
                             and math.isfinite(float(minutes)) and minutes > 0)
        except (OverflowError, ValueError):
            valid_minutes = False
        if not valid_minutes:
            raise PackageError(f"copy.{locale}.youtube_long.target_duration_minutes must be positive")
        sections = long.get("sections")
        if not isinstance(sections, list) or len(sections) < 3:
            raise PackageError(f"copy.{locale}.youtube_long.sections must contain at least three sections")
        for i, section in enumerate(sections):
            if not isinstance(section, dict):
                raise PackageError(f"copy.{locale}.youtube_long.sections[{i}] must be an object")
            require_string(section.get("heading"), f"copy.{locale}.youtube_long.sections[{i}].heading")
            points = section.get("talking_points")
            if not isinstance(points, list) or not points or any(not isinstance(x, str) or not x.strip() for x in points):
                raise PackageError(f"copy.{locale}.youtube_long.sections[{i}].talking_points must be non-empty strings")
        normalized_copy[locale] = locale_copy

    adaptations = pkg.get("platform_adaptations")
    if not isinstance(adaptations, dict) or set(PLATFORMS) - set(adaptations):
        raise PackageError("platform_adaptations must contain YouTube, TikTok, Instagram, and Facebook")
    if selected_platform != "all" and selected_platform not in PLATFORMS:
        raise PackageError(f"unsupported platform: {selected_platform}")
    selected = PLATFORMS if selected_platform == "all" else {selected_platform}
    for platform in PLATFORMS:
        adapter = adaptations[platform]
        if not isinstance(adapter, dict) or adapter.get("publishing_enabled") is not False:
            raise PackageError(f"platform_adaptations.{platform}.publishing_enabled must be false")
        if adapter.get("account_alias", ""):
            raise PackageError("account aliases must remain empty for this no-account local test")
    release = pkg.get("release_control")
    if not isinstance(release, dict) or release.get("external_publication_enabled") is not False or release.get("external_publication_approved") is not False:
        raise PackageError("external publication must remain disabled and unapproved")
    if release.get("destination_alias", ""):
        raise PackageError("destination_alias must remain empty")
    return {
        "contract_version": pkg["contract_version"], "package_id": pkg["package_id"],
        "revision": pkg["revision"], "package_sha256": "", "test_only": True,
        "platform_selection": selected_platform, "selected_platforms": sorted(selected),
        "languages": list(LOCALES), "fps": FPS, "preview_seconds": preview_seconds,
        "topic": topic, "copy": normalized_copy,
    }


def atomic_json(path: Path, value: object) -> None:
    staged = path.with_name(f".{path.name}.partial")
    staged.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    staged.replace(path)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_storyboards(plan: dict[str, object], output: Path) -> list[dict[str, object]]:
    records = []
    for locale in LOCALES:
        long = plan["copy"][locale]["youtube_long"]
        language_name = "Arabic White" if locale == "ar_white" else "English"
        lines = [f"# {long['title']} — {language_name} — TEST_ONLY", "", f"> Status: draft storyboard only; no final episode, voice, or publication.", "", "## Opening", "", long["opening"], ""]
        for index, section in enumerate(long["sections"], start=1):
            lines.extend([f"## Scene {index:02d}: {section['heading']}", ""])
            lines.extend([f"- {point}" for point in section["talking_points"]])
            lines.append("")
        lines.extend(["## Ending", "", long["ending"], "", "## Review status", "", "Facts: blocked. Rights: blocked. Quality: pending human review. Audio: not included. Publication: disabled.", ""])
        path = output / f"youtube-long-storyboard-{locale}-TEST_ONLY.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        records.append({"kind": "youtube_long_storyboard", "language": locale, "path": path.name, "bytes": path.stat().st_size})
    return records


def update_job(job_path: Path, job: dict[str, object], stage: str) -> None:
    job["stage"] = stage
    job["updated_at_utc"] = now_utc()
    atomic_json(job_path, job)


def run(args: argparse.Namespace) -> int:
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if not input_path.is_relative_to(LAB.resolve()):
        raise PackageError("input file must be inside lab/")
    if not input_path.is_file():
        raise FileNotFoundError(f"input package not found: {input_path}")
    if not output_path.is_relative_to(EVIDENCE.resolve()) or output_path == EVIDENCE.resolve():
        raise PackageError("output directory must be a child of lab/evidence/")
    if "TEST_ONLY" not in output_path.name:
        raise PackageError("output directory name must contain TEST_ONLY")
    package = json.loads(input_path.read_text(encoding="utf-8"))
    plan = validate_package(package, input_path, args.platform, args.preview_seconds)
    plan["visual_direction"] = args.visual_direction
    source_hash = sha256(input_path)
    plan["package_sha256"] = source_hash
    plan["topic"] = package["topic"]
    plan["copy"] = package["copy"]
    work = output_path.with_name(f".{output_path.name}.work")
    job_path = work / "job.json"

    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output directory: {output_path}")
    if work.exists():
        if not args.resume:
            raise FileExistsError(f"incomplete work exists; use --resume after checking it: {work}")
        if not job_path.is_file():
            raise PackageError(f"cannot resume: missing job state file {job_path}")
        job = json.loads(job_path.read_text(encoding="utf-8"))
        if (job.get("source_sha256") != source_hash or job.get("platform_selection") != args.platform
                or job.get("preview_seconds") != args.preview_seconds
                or job.get("visual_direction", "editorial") != args.visual_direction):
            raise PackageError("resume refused: input package or platform selection changed")
    else:
        if args.resume:
            raise PackageError(f"cannot resume because no interrupted work exists: {work}")
        work.mkdir(parents=True)
        job = {
            "package_id": plan["package_id"], "source_name": input_path.name,
            "source_sha256": source_hash, "platform_selection": args.platform,
            "visual_direction": args.visual_direction, "publication_enabled": False,
            "created_at_utc": now_utc(), "stage": "initialized",
            "elapsed_seconds_accumulated": 0.0, "preview_seconds": args.preview_seconds,
        }
        atomic_json(job_path, job)
        atomic_json(work / "render-plan.json", plan)
        shutil.copy2(input_path, work / "source-package-TEST_ONLY.json")

    svg_dir = work / "svg"
    artifact_dir = work / "artifacts"
    if job.get("stage") != "vectors_ready":
        shutil.rmtree(svg_dir, ignore_errors=True)
        update_job(job_path, job, "vector_rendering")
        node = shutil.which("node")
        if not node:
            raise FileNotFoundError("node executable is required")
        command = [node, str(MOTION), "--plan", str(work / "render-plan.json"), "--output", str(svg_dir)]
        if args.test_interrupt_after_svg_count:
            command += ["--test-interrupt-after-svg-count", str(args.test_interrupt_after_svg_count)]
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode == 75 and args.test_interrupt_after_svg_count:
            job["elapsed_seconds_accumulated"] = float(job.get("elapsed_seconds_accumulated", 0)) + time.monotonic() - args.started_at
            atomic_json(job_path, job)
            print(f"SIMULATED INTERRUPTION saved for resume at {work}", file=sys.stderr)
            return 75
        if result.returncode:
            raise RuntimeError(f"SVG rendering failed with exit code {result.returncode}")
        update_job(job_path, job, "vectors_ready")

    if job.get("stage") != "media_ready":
        shutil.rmtree(artifact_dir, ignore_errors=True)
        artifact_dir.mkdir(parents=True)
        update_job(job_path, job, "media_rendering")
        markdown_records = write_storyboards(plan, artifact_dir)
        render_result = subprocess.run(
            [sys.executable, str(RENDER_MAC), "--package-svg-dir", str(svg_dir),
             "--output-dir", str(artifact_dir), "--fps", str(FPS)],
            cwd=ROOT, check=False,
        )
        if render_result.returncode:
            raise RuntimeError(f"media rendering failed with exit code {render_result.returncode}")
        renderer_records = json.loads((artifact_dir / "renderer-result.json").read_text(encoding="utf-8")) if (artifact_dir / "renderer-result.json").is_file() else []
        job["artifact_records"] = markdown_records + renderer_records
        update_job(job_path, job, "media_ready")

    if job.get("stage") != "complete":
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        records = job.get("artifact_records", [])
        report = {
            "mode": "TEST_ONLY_LOCAL_PREVIEW", "package_id": job["package_id"],
            "source_package": job["source_name"], "source_sha256": source_hash,
            "platform_selection": args.platform, "visual_direction": args.visual_direction,
            "languages": list(LOCALES), "fps": FPS,
            "preview_duration_seconds": args.preview_seconds,
            "target_duration_seconds": min(plan["copy"][locale]["short_video"]["target_duration_seconds"] for locale in LOCALES),
            "audio_present": False, "fact_gate": "BLOCKED_OR_UNREVIEWED",
            "rights_gate": "BLOCKED_OR_UNREVIEWED", "quality_gate": "PENDING_HUMAN_REVIEW",
            "external_publication_enabled": False, "external_publication_approved": False,
            "elapsed_seconds": round(float(job.get("elapsed_seconds_accumulated", 0)) + time.monotonic() - args.started_at, 3),
            "child_user_cpu_seconds": round(children.ru_utime, 3),
            "child_system_cpu_seconds": round(children.ru_stime, 3),
            "max_child_rss_mb": round(children.ru_maxrss / (1024 * 1024), 2),
            "artifacts": records,
        }
        atomic_json(artifact_dir / "render-report.json", report)
        shutil.rmtree(svg_dir, ignore_errors=True)
        update_job(job_path, job, "complete")
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output directory: {output_path}")
    work.replace(output_path)
    print(f"Rendered TEST_ONLY package to {output_path}")
    print(f"Report: {output_path / 'artifacts' / 'render-report.json'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--platform", choices=("all", *sorted(PLATFORMS)), default="all")
    parser.add_argument("--visual-direction", choices=("editorial", "spotlight", "fieldnotes", "typeplay", "gallery"), default="editorial",
                        help="TEST_ONLY visual template: editorial, spotlight, fieldnotes, typeplay, or gallery")
    parser.add_argument("--preview-seconds", type=int, default=5,
                        help="silent visual excerpt length; defaults to 5 seconds and never exceeds package target")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--test-interrupt-after-svg-count", type=int, default=0,
                        help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.started_at = time.monotonic()
    try:
        if args.test_interrupt_after_svg_count < 0:
            raise PackageError("test interrupt count must be non-negative")
        if args.preview_seconds < 1 or args.preview_seconds > 60:
            raise PackageError("--preview-seconds must be from 1 to 60")
        if args.test_interrupt_after_svg_count and args.resume:
            raise PackageError("do not combine interruption simulation and --resume")
        return run(args)
    except (OSError, ValueError, PackageError, RuntimeError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
