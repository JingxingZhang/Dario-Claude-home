#!/usr/bin/env python3
"""导关键帧拼图：python3 still.py 项目目录 输出.png 秒,秒,… [--cols 3] [--full]
--full：额外把每帧按 1920×1080 原尺寸存到 输出同名目录（做封面用）。"""
import argparse, os
from PIL import Image, ImageDraw
from _load import load

ap = argparse.ArgumentParser()
ap.add_argument('project'); ap.add_argument('out'); ap.add_argument('times')
ap.add_argument('--cols', type=int, default=3); ap.add_argument('--full', action='store_true')
A = ap.parse_args()
mv = load(A.project)
ts = [float(x) for x in A.times.split(',') if x.strip()]
tw, th = 640, 360
rows = (len(ts) + A.cols - 1) // A.cols
sheet = Image.new('RGB', (A.cols * (tw + 4), rows * (th + 4)), 'white')
for i, t in enumerate(ts):
    big = mv.frame(t)
    if A.full:
        od = os.path.splitext(A.out)[0]; os.makedirs(od, exist_ok=True); big.save(os.path.join(od, f'{t:.2f}.png'))
    im = big.resize((tw, th), Image.BILINEAR)
    ImageDraw.Draw(im).text((4, 4), f'{t:.1f}', fill=(255, 0, 255))
    sheet.paste(im, ((i % A.cols) * (tw + 4), (i // A.cols) * (th + 4)))
sheet.save(A.out)
print('✓', A.out)
