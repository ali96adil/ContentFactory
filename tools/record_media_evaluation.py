#!/usr/bin/env python3
"""Append local, reproducible media metadata to an evaluation CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "recorded_utc", "kind", "language", "candidate", "asset", "sha256",
    "bytes", "duration_s", "sample_rate", "channels", "width", "height",
    "frame_rate", "generation_s", "source_url", "license", "gender_metadata",
    "clarity_1_5", "naturalness_1_5", "motion_1_5", "notes",
]
ROOT = Path(__file__).resolve().parents[1]


def asset_reference(asset: Path) -> tuple[Path, str]:
    """Resolve an asset and return a repository-relative, portable reference."""
    resolved = asset.resolve()
    if not resolved.is_file():
        raise ValueError(f"asset does not exist: {resolved}")
    try:
        relative = resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("asset must be inside the repository to avoid recording a private absolute path") from exc
    return resolved, relative.as_posix()


def append_row(output: Path, row: dict[str, object]) -> None:
    """Append one record only when an existing CSV has the expected schema."""
    if output.is_symlink():
        raise ValueError("output must not be a symbolic link")
    output.parent.mkdir(parents=True, exist_ok=True)
    new_file = not output.exists()
    if not new_file:
        with output.open(newline="", encoding="utf-8") as stream:
            header = next(csv.reader(stream), None)
        if header != FIELDS:
            raise ValueError("output CSV header does not match the media evaluation schema")
    with output.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def probe(path: Path) -> dict[str, object]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise SystemExit("ffprobe is required and was not found in PATH")
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,sample_rate,channels,width,height,r_frame_rate",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    return {
        "duration_s": data.get("format", {}).get("duration", ""),
        "sample_rate": audio.get("sample_rate", ""),
        "channels": audio.get("channels", ""),
        "width": video.get("width", ""),
        "height": video.get("height", ""),
        "frame_rate": video.get("r_frame_rate", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("audio", "motion"), required=True)
    parser.add_argument("--language", required=True, help="ar, en, or bilingual")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--asset", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--generation-seconds", default="")
    parser.add_argument("--gender-metadata", default="unspecified")
    parser.add_argument("--notes", default="")
    parser.add_argument("--output", type=Path, default=Path("docs/evaluation-results.csv"))
    args = parser.parse_args()

    try:
        asset, asset_name = asset_reference(args.asset)
    except ValueError as exc:
        parser.error(str(exc))
    digest_state = hashlib.sha256()
    with asset.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest_state.update(chunk)
    digest = digest_state.hexdigest()
    row = {
        "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": args.kind,
        "language": args.language,
        "candidate": args.candidate,
        "asset": asset_name,
        "sha256": digest,
        "bytes": asset.stat().st_size,
        **probe(asset),
        "generation_s": args.generation_seconds,
        "source_url": args.source_url,
        "license": args.license,
        "gender_metadata": args.gender_metadata,
        "clarity_1_5": "",
        "naturalness_1_5": "",
        "motion_1_5": "",
        "notes": args.notes,
    }
    try:
        append_row(args.output, row)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(row, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
