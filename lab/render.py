import concurrent.futures
import json
import pathlib
import resource
import subprocess
import tempfile
import time

ROOT = pathlib.Path("renders")
OUT = pathlib.Path("evidence")
records = []
for engine in ("librsvg", "inkscape"):
    for locale in ("ar", "en"):
        source = ROOT / locale / "short"
        target = OUT / f"{engine}-{locale}-TEST_ONLY.mp4"
        start = time.monotonic()
        with tempfile.TemporaryDirectory(dir=OUT) as temp:
            directory = pathlib.Path(temp)
            if engine == "inkscape":
                def render_svg(path):
                    subprocess.run(
                        ["inkscape", str(path), f"--export-filename={directory / path.with_suffix('.png').name}"],
                        check=True, capture_output=True, timeout=15,
                    )
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                    list(pool.map(render_svg, sorted(source.glob("*.svg"))))
                sequence = directory / "frame-%03d.png"
            else:
                sequence = source / "frame-%03d.svg"
            staged = directory / target.name
            subprocess.run(
                ["ffmpeg","-v","error","-y","-threads","2","-framerate","24","-i",str(sequence),
                 "-an","-c:v","libx264","-threads","2","-preset","fast","-pix_fmt","yuv420p",str(staged)],
                check=True, timeout=100,
            )
            staged.replace(target)
        metadata = subprocess.check_output(
            ["ffprobe","-v","error","-show_entries","stream=width,height,nb_frames,r_frame_rate:format=duration",
             "-of","json",str(target)], text=True,
        )
        data = json.loads(metadata)
        stream = data["streams"][0]
        assert (stream["width"], stream["height"], stream["nb_frames"], stream["r_frame_rate"]) == (1080,1920,"96","24/1")
        records.append({"file":target.name,"elapsed_s":round(time.monotonic()-start,2),
                        "bytes":target.stat().st_size,**data})
        (OUT/"motion-metrics.json").write_text(json.dumps(records,indent=2))
for locale in ("ar","en"):
    for fmt in ("carousel","landscape"):
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(ROOT/locale/fmt/"frame-000.svg"),
                        "-frames:v","1",str(OUT/f"librsvg-{locale}-{fmt}.png")],check=True,timeout=15)
