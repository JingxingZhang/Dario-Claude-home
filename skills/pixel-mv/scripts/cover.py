#!/usr/bin/env python3
"""导出封面：python3 cover.py 项目目录 [--t 秒]
  16:9 → cover/封面_16x9.png：取成片第 --t 秒（默认 mv.py 里的 COVER_T）的一帧，1920×1080；
  3:4  → cover/封面_3x4.png：调用 mv.py 里的 COVER_3X4(img, t) 单独构图，1080×1440（没写就跳过并提醒）。"""
import argparse, os
from _load import load

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--t', type=float, default=None)
A = ap.parse_args()
mv = load(A.project)
os.makedirs(os.path.join(A.project, 'cover'), exist_ok=True)
t = A.t if A.t is not None else getattr(mv, 'COVER_T', None)
if t is None:
    raise SystemExit('✗ 给 --t 秒，或在 mv.py 里写 COVER_T = 秒（选全片最有戏的一帧）')
p = os.path.join(A.project, 'cover', '封面_16x9.png')
mv.frame(t).save(p); print('✓', p)
if hasattr(mv, 'COVER_3X4'):
    from cover import build_3x4
    pj = mv.song.p
    big = build_3x4(mv.COVER_3X4, t, pj['title'], pj.get('artist', ''), (pj.get('tag') or '像素 MV'), pj.get('signature', ''),
                    getattr(mv, 'TITLE_STYLE', None))
    p = os.path.join(A.project, 'cover', '封面_3x4.png')
    big.save(p); print('✓', p)
else:
    print('！mv.py 里还没有 COVER_3X4(img, t)：3:4 竖版封面跳过（抖音、小红书竖版位要用）')
