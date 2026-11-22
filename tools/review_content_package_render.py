#!/usr/bin/env python3
"""Run technical QA and create a standalone TEST_ONLY contact sheet for a rendered package."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab"
EVIDENCE = LAB / "evidence"
LANGUAGES = {"ar": "Arabic White", "en": "English"}
AMBIGUOUS = re.compile(r"(^|[-_.])(final|production|publish|approved|release)([-_.]|$)", re.I)


def command(args: list[str]) -> str:
    result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"not a valid PNG header: {path.name}")
    return struct.unpack(">II", header[16:24])


def ffprobe(path: Path) -> dict:
    return json.loads(command(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def image_uri(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def add_tile(parts: list[str], x: int, y: int, w: int, h: int, uri: str, label: str, font: int = 22) -> None:
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#142628" stroke="#527f7b"/>')
    parts.append(f'<image x="{x + 8}" y="{y + 8}" width="{w - 16}" height="{h - 48}" href="{uri}" preserveAspectRatio="xMidYMid meet"/>')
    parts.append(f'<text x="{x + w // 2}" y="{y + h - 14}" text-anchor="middle" fill="#f6edda" font-family="Geeza Pro,Arial,sans-serif" font-size="{font}">{esc(label)}</text>')


def run(args: argparse.Namespace) -> dict:
    artifacts = args.artifacts.resolve()
    output = args.output.resolve()
    if not artifacts.is_relative_to(EVIDENCE.resolve()) or "TEST_ONLY" not in str(artifacts):
        raise ValueError("artifacts must be under a TEST_ONLY path inside lab/evidence/")
    if not artifacts.is_dir():
        raise FileNotFoundError(f"artifact directory not found: {artifacts}")
    if not output.is_relative_to(EVIDENCE.resolve()) or output == EVIDENCE.resolve() or "TEST_ONLY" not in output.name:
        raise ValueError("output must be a new TEST_ONLY directory under lab/evidence/")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite review directory: {output}")

    files = sorted(p for p in artifacts.iterdir() if p.is_file())
    if not files or any(AMBIGUOUS.search(path.name) for path in files):
        raise ValueError("empty artifact directory or production-ambiguous filename")
    report_path = artifacts / "render-report.json"
    result_path = artifacts / "renderer-result.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    renderer_result = json.loads(result_path.read_text(encoding="utf-8"))
    if report.get("mode") != "TEST_ONLY_LOCAL_PREVIEW" or report.get("external_publication_enabled") is not False or report.get("external_publication_approved") is not False or report.get("audio_present") is not False:
        raise ValueError("render report TEST_ONLY/audio/publication gates failed")

    media = [path for path in files if path.suffix.lower() in {".mp4", ".png", ".jpg", ".jpeg"}]
    if any("TEST_ONLY" not in path.name for path in media):
        raise ValueError("media filename missing TEST_ONLY marker")
    shorts = {lang: artifacts / f"short-{lang}-TEST_ONLY.mp4" for lang in LANGUAGES}
    carousels = {lang: sorted(artifacts.glob(f"carousel-{lang}-*-TEST_ONLY.png")) for lang in LANGUAGES}
    storyboards = {lang: sorted(artifacts.glob(f"youtube-long-storyboard-{lang}-*-TEST_ONLY.png")) for lang in LANGUAGES}
    checks: list[dict] = []
    video_info: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="content-package-contact-TEST_ONLY-") as temp_name:
        temp = Path(temp_name)
        thumbs: dict[str, Path] = {}
        for lang, path in shorts.items():
            if not path.is_file():
                raise FileNotFoundError(f"missing Short: {path.name}")
            info = ffprobe(path)
            streams = info.get("streams", [])
            video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
            audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
            if video is None or video.get("codec_name") != "h264" or (video.get("width"), video.get("height")) != (1080, 1920):
                raise ValueError(f"Short dimensions/codec check failed: {path.name}")
            fps = video.get("avg_frame_rate")
            duration = float(info["format"]["duration"])
            frames = int(video.get("nb_frames", "0"))
            if fps != "24/1" or abs(duration - 5.0) > 0.05 or frames != 120:
                raise ValueError(f"Short duration/fps/frame count check failed: {path.name}")
            if audio_streams:
                raise ValueError(f"unexpected audio stream: {path.name}")
            command(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
            video_info[lang] = {"duration_seconds": duration, "width": video["width"], "height": video["height"], "fps": fps, "frames": frames, "codec": video["codec_name"], "audio_streams": len(audio_streams), "bytes": path.stat().st_size}
            checks.append({"check": f"short_{lang}_metadata_and_decode", "status": "PASS"})
            sample_times = (0.5, 2.4, 4.0, 4.8)
            hashes = set()
            for index, seconds in enumerate(sample_times, 1):
                thumb = temp / f"short-{lang}-{index}.jpg"
                command(["ffmpeg", "-v", "error", "-y", "-ss", str(seconds), "-i", str(path), "-frames:v", "1", "-vf", "scale=210:374:force_original_aspect_ratio=decrease", "-q:v", "5", str(thumb)])
                digest = hashlib.sha256(thumb.read_bytes()).hexdigest()
                hashes.add(digest)
                thumbs[f"short-{lang}-{index}"] = thumb
            if len(hashes) < 2:
                raise ValueError(f"sampled frames show no visual change in {path.name}")
            video_info[lang]["sampled_unique_frames"] = len(hashes)
        checks.append({"check": "shorts_show_temporal_visual_change", "status": "PASS"})

        for lang in LANGUAGES:
            if len(carousels[lang]) != 5 or len(storyboards[lang]) != 6:
                raise ValueError(f"unexpected number of {lang} carousel/storyboard images")
            for path in carousels[lang]:
                if png_dimensions(path) != (1080, 1350):
                    raise ValueError(f"carousel dimensions check failed: {path.name}")
                thumb = temp / f"{path.stem}.jpg"
                command(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-frames:v", "1", "-vf", "scale=236:295:force_original_aspect_ratio=decrease", "-q:v", "5", str(thumb)])
                thumbs[path.stem] = thumb
            for path in storyboards[lang]:
                if png_dimensions(path) != (1920, 1080):
                    raise ValueError(f"storyboard dimensions check failed: {path.name}")
                thumb = temp / f"{path.stem}.jpg"
                command(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-frames:v", "1", "-vf", "scale=280:158:force_original_aspect_ratio=decrease", "-q:v", "5", str(thumb)])
                thumbs[path.stem] = thumb
        checks.append({"check": "all_carousel_and_storyboard_png_dimensions", "status": "PASS"})

        for item in renderer_result:
            file_path = artifacts / item["path"]
            if not file_path.is_file() or "TEST_ONLY" not in item["path"]:
                raise ValueError(f"renderer manifest path missing or unmarked: {item.get('path')}")
        if any("TEST_ONLY" not in path.name for path in media):
            raise ValueError("unmarked rendered media filename")
        checks.extend([
            {"check": "manifest_paths_exist_and_media_names_marked_TEST_ONLY", "status": "PASS"},
            {"check": "filenames_not_production_ambiguous", "status": "PASS"},
            {"check": "publication_disabled_and_audio_absent", "status": "PASS"},
        ])

        width = 1800
        y = 150
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="1" viewBox="0 0 {width} 1">']
        svg.append('<rect width="100%" height="100%" fill="#0e1c1e"/>')
        svg.append(f'<text x="56" y="72" fill="#78e4c3" font-family="Geeza Pro,Arial,sans-serif" font-size="40">Content package review • TEST_ONLY</text>')
        svg.append('<text x="56" y="118" fill="#b6ceca" font-family="Arial,sans-serif" font-size="22">Sampled silent Short frames • Carousel slides • YouTube storyboard panels</text>')
        sections = []
        for lang in LANGUAGES:
            language_label = "العربية البيضاء" if lang == "ar" else "English"
            sections.append((f"Short • {language_label}", [thumbs[f"short-{lang}-{i}"] for i in range(1, 5)], 4, 400, 430, ["0.5s", "2.4s", "4.0s", "4.8s"]))
        for lang in LANGUAGES:
            language_label = "العربية البيضاء" if lang == "ar" else "English"
            sections.append((f"Carousel • {language_label}", [thumbs[path.stem] for path in carousels[lang]], 5, 320, 315, [f"Slide {index:02d}" for index in range(1, 6)]))
        for lang in LANGUAGES:
            language_label = "العربية البيضاء" if lang == "ar" else "English"
            sections.append((f"YouTube storyboard • {language_label}", [thumbs[path.stem] for path in storyboards[lang]], 6, 270, 190, [f"Panel {index:02d}" for index in range(1, 7)]))
        for title, paths, columns, cell_w, cell_h, labels in sections:
            y += 36
            svg.append(f'<text x="56" y="{y}" fill="#f6edda" font-family="Geeza Pro,Arial,sans-serif" font-size="28">{esc(title)}</text>')
            y += 16
            gap = (width - 112 - columns * cell_w) // max(1, columns - 1) if columns > 1 else 0
            row_h = cell_h + 18
            for i, (thumb, label) in enumerate(zip(paths, labels)):
                x = 56 + i * (cell_w + gap)
                add_tile(svg, x, y, cell_w, row_h, image_uri(thumb), label, 16 if cell_w < 300 else 19)
            y += row_h + 8
        svg[0] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y + 40}" viewBox="0 0 {width} {y + 40}">'
        svg.append('</svg>')
        output.mkdir(parents=True)
        svg_path = temp / "contact-sheet.svg"
        svg_path.write_text("\n".join(svg), encoding="utf-8")
        preview = output / "content-package-contact-sheet-TEST_ONLY.png"
        command(["rsvg-convert", "--format", "png", "--output", str(preview), str(svg_path)])

    review_rows = [
        "| معيار المراجعة البشرية | الحالة | ملاحظات المستخدم |",
        "|---|---|---|",
        *[f"| {name} | بانتظار مراجعة المستخدم | |" for name in ("وضوح النص على شاشة الهاتف", "حجم النص وتوزيعه", "سلامة اتجاه العربية والتشكيل", "التباين", "قص النص والعناصر", "توازن النص مع الصورة", "عدم هيمنة الأيقونة على المشاهد", "تنسيق الخط بين اللغتين", "تنوع الحركة", "سلاسة الحركة بالتشغيل المتصل", "الإيقاع", "الذوق البصري", "تماسك تسلسل Carousel", "وضوح Storyboard", "جودة الترجمة")],
    ]
    (output / "human-review-TEST_ONLY.md").write_text(
        "# قائمة مراجعة بشرية — TEST_ONLY\n\nلم تُسجّل درجة جودة بشرية آلياً. اكتب الملاحظات بعد مشاهدة المعاينة ومراجعة النصين.\n\n"
        + "\n".join(review_rows) + "\n\nالجودة والحقوق والصوت والتصدير والنشر تبقى غير معتمدة.\n",
        encoding="utf-8",
    )
    result = {
        "mode": "TEST_ONLY_TECHNICAL_QA",
        "source_artifact_dir": str(artifacts.relative_to(ROOT)),
        "preview": preview.name,
        "preview_dimensions": list(png_dimensions(preview)),
        "artifact_file_count": len(files),
        "video_details": video_info,
        "checks": checks,
        "human_review_status": "PENDING_USER_REVIEW",
        "publication_enabled": False,
        "audio_added": False,
    }
    (output / "technical-checks-TEST_ONLY.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
