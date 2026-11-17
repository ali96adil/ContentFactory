"""macOS rendering adapter for existing SVG scenes and package SVG frames."""
import argparse
import json
import pathlib
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
RENDERS = ROOT / "renders"
FPS = 24


def ffprobe(path: pathlib.Path) -> dict[str, object]:
    data = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,nb_frames,r_frame_rate:format=duration,size",
         "-of", "json", str(path)], text=True,
    ))
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    return {
        "duration_seconds": float(data.get("format", {}).get("duration", 0)),
        "bytes": path.stat().st_size,
        "codec": video.get("codec_name", ""),
        "width": video.get("width", 0),
        "height": video.get("height", 0),
        "frames": int(video.get("nb_frames", 0) or 0),
        "frame_rate": video.get("r_frame_rate", ""),
        "audio_present": any(s.get("codec_type") == "audio" for s in data.get("streams", [])),
    }


def render_svg_still(source: pathlib.Path, target: pathlib.Path) -> dict[str, object]:
    if not source.is_file():
        raise FileNotFoundError(f"missing SVG input: {source}")
    if target.exists():
        raise FileExistsError(f"refusing to overwrite output: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    staged = target.with_name(f".{target.name}.partial")
    try:
        subprocess.run(["rsvg-convert", "-o", str(staged), str(source)], check=True, timeout=45)
        staged.replace(target)
    finally:
        staged.unlink(missing_ok=True)
    root = ET.parse(source).getroot()
    width = int(float(root.attrib["width"].removesuffix("px")))
    height = int(float(root.attrib["height"].removesuffix("px")))
    return {"path": target.name, "bytes": target.stat().st_size,
            "width": width, "height": height}


def render_package_svgs(svg_root: pathlib.Path, output: pathlib.Path, fps: int = FPS) -> list[dict[str, object]]:
    if not svg_root.is_dir():
        raise FileNotFoundError(f"missing package SVG directory: {svg_root}")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for locale, suffix in (("ar_white", "ar"), ("en", "en")):
        short_source = svg_root / locale / "short"
        frames = sorted(short_source.glob("frame-*.svg"))
        if not frames:
            raise FileNotFoundError(f"no short SVG frames for {locale}: {short_source}")
        target = output / f"short-{suffix}-TEST_ONLY.mp4"
        if target.exists():
            raise FileExistsError(f"refusing to overwrite output: {target}")
        with tempfile.TemporaryDirectory(prefix=f".{suffix}-frames-", dir=output) as temp_name:
            temp = pathlib.Path(temp_name)
            for index, frame in enumerate(frames):
                render_svg_still(frame, temp / f"frame-{index:05d}.png")
            staged = temp / target.name
            subprocess.run(
                ["ffmpeg", "-nostdin", "-v", "error", "-y", "-threads", "2", "-framerate", str(fps),
                 "-i", str(temp / "frame-%05d.png"), "-an", "-c:v", "libx264", "-threads", "2",
                 "-preset", "fast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(staged)],
                check=True, timeout=240,
            )
            metadata = ffprobe(staged)
            if (metadata["codec"], metadata["width"], metadata["height"], metadata["frame_rate"], metadata["audio_present"]) != ("h264", 1080, 1920, f"{fps}/1", False):
                raise RuntimeError(f"short video failed technical profile: {metadata}")
            staged.replace(target)
        records.append({"kind": "short_video", "language": locale, "path": target.name, **ffprobe(target)})

        for kind, dir_name, prefix, dimensions in (
            ("carousel_slide", "carousel", "carousel", (1080, 1350)),
            ("youtube_long_storyboard_panel", "youtube_long", "youtube-long-storyboard", (1920, 1080)),
        ):
            source_dir = svg_root / locale / dir_name
            slides = sorted(source_dir.glob("*.svg"))
            if not slides:
                raise FileNotFoundError(f"no {dir_name} SVG files for {locale}: {source_dir}")
            for index, slide in enumerate(slides, start=1):
                target = output / f"{prefix}-{suffix}-{index:02d}-TEST_ONLY.png"
                record = render_svg_still(slide, target)
                if (record["width"], record["height"]) != dimensions:
                    raise RuntimeError(f"{kind} failed dimensions: {record}")
                records.append({"kind": kind, "language": locale, "index": index, **record})
    return records


def legacy_render() -> None:
    records = []
    for locale in ("ar", "en"):
        source = RENDERS / locale / "short"
        target = EVIDENCE / f"librsvg-{locale}-TEST_ONLY.mp4"
        start = time.monotonic()
        with tempfile.TemporaryDirectory(dir=EVIDENCE) as temp_name:
            temp = pathlib.Path(temp_name)
            for frame in sorted(source.glob("frame-*.svg")):
                output = temp / frame.with_suffix(".png").name
                subprocess.run(["rsvg-convert", "-o", str(output), str(frame)], check=True, timeout=30)
            staged = temp / target.name
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-threads", "2", "-framerate", "24",
                 "-i", str(temp / "frame-%03d.png"), "-an", "-c:v", "libx264", "-threads", "2",
                 "-preset", "fast", "-pix_fmt", "yuv420p", str(staged)],
                check=True, timeout=120,
            )
            metadata = json.loads(subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries",
                 "stream=codec_name,width,height,nb_frames,r_frame_rate:format=duration,size",
                 "-of", "json", str(staged)], text=True,
            ))
            stream = metadata["streams"][0]
            assert (stream["codec_name"], stream["width"], stream["height"], stream["nb_frames"],
                    stream["r_frame_rate"]) == ("h264", 1080, 1920, "96", "24/1")
            staged.replace(target)
        records.append({"file": str(target.relative_to(ROOT)), "elapsed_s": round(time.monotonic() - start, 2),
                        "bytes": target.stat().st_size, **metadata})
    print(json.dumps(records, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-svg-dir", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path)
    parser.add_argument("--fps", type=int, default=FPS)
    args = parser.parse_args()
    if args.package_svg_dir is None and args.output_dir is None:
        legacy_render()
        return
    if args.package_svg_dir is None or args.output_dir is None:
        parser.error("--package-svg-dir and --output-dir must be used together")
    if args.fps != FPS:
        parser.error(f"only {FPS} fps is supported by this package renderer")
    if not shutil.which("rsvg-convert") or not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        parser.error("rsvg-convert, ffmpeg, and ffprobe must be available")
    records = render_package_svgs(args.package_svg_dir.resolve(), args.output_dir.resolve(), args.fps)
    result_path = args.output_dir.resolve() / "renderer-result.json"
    if result_path.exists():
        parser.error(f"refusing to overwrite renderer result: {result_path}")
    result_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
