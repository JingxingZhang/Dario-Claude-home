#!/usr/bin/env python3
"""Contact sheet of one generated clip (frames every --step seconds, timestamped),
used to choose the in-point / best take before editing.

Usage: python3 tools/review_sheet.py clips/S05.mp4 [--step 0.25] [-o out/S05_sheet.jpg]
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--step", type=float, default=0.25)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    clip = Path(a.clip)
    out = Path(a.out) if a.out else clip.with_name(clip.stem + "_sheet.jpg")
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vf",
                        f"fps=1/{a.step},scale=384:-2", f"{d}/f_%04d.jpg"], check=True)
        frames = sorted(Path(d).glob("f_*.jpg"))
        w, h = Image.open(frames[0]).size
        rows = (len(frames) + a.cols - 1) // a.cols
        sheet = Image.new("RGB", (w * a.cols, h * rows), "black")
        for i, f in enumerate(frames):
            im = Image.open(f)
            ImageDraw.Draw(im).text((6, 4), f"{i * a.step:.2f}s", fill="yellow")
            sheet.paste(im, ((i % a.cols) * w, (i // a.cols) * h))
        sheet.save(out, quality=85)
    print(out)


if __name__ == "__main__":
    main()
