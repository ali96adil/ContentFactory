"""macOS adapter: render package SVG frames through librsvg, then encode with FFmpeg."""
import json
import pathlib
import subprocess
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
RENDERS = ROOT / "renders"
records = []

for locale in ("ar", "en"):
    source = RENDERS / locale / "short"
    target = EVIDENCE / f"librsvg-{locale}-TEST_ONLY.mp4"
    start = time.monotonic()
    with tempfile.TemporaryDirectory(dir=EVIDENCE) as temp:
        temp = pathlib.Path(temp)
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
