#!/usr/bin/env python3
"""Run the repository's complete zero-cost local/CI verification sequence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MOTION = ROOT / "lab" / "motion-canvas"


def main() -> int:
    required = ("ffmpeg", "ffprobe", "rsvg-convert", "node", "npm")
    missing = [name for name in required if shutil.which(name) is None]
    if missing:
        print("Missing verification tools: " + ", ".join(missing), file=sys.stderr)
        print("Install the free system packages listed in README.md, then retry.", file=sys.stderr)
        return 2

    run_name = "content-package-recovery-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-TEST_ONLY"
    commands = [
        ([sys.executable, "lab/test_checkpoint.py"], ROOT),
        ([sys.executable, "tools/test_analyze_platform_metrics.py"], ROOT),
        ([sys.executable, "tools/test_content_package_pipeline.py"], ROOT),
        ([sys.executable, "tools/test_review_content_package_render.py"], ROOT),
        ([sys.executable, "tools/test_content_package_recovery.py", "--run-name", run_name], ROOT),
        ([sys.executable, "-m", "py_compile",
          "tools/analyze_platform_metrics.py", "tools/test_analyze_platform_metrics.py",
          "tools/render_content_package.py", "tools/review_content_package_render.py",
          "tools/test_review_content_package_render.py",
          "tools/test_content_package_pipeline.py", "tools/test_content_package_recovery.py",
          "tools/verify_repo.py"], ROOT),
        (["node", "--check", "lab/motion.mjs"], ROOT),
        (["npm", "ci", "--legacy-peer-deps"], MOTION),
        (["npm", "run", "build"], MOTION),
    ]
    for command, cwd in commands:
        print("+ " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=cwd, check=False)
        if result.returncode:
            print(f"Verification stopped: command exited {result.returncode}.", file=sys.stderr)
            return result.returncode
    print("Repository verification: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
