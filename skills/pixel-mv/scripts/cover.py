#!/usr/bin/env python3
"""导出交付封面（3:4 竖版，1080×1440）：python3 cover.py 项目目录 [--t 秒] [--also-16x9]
  cover/封面.png：调用 mv.py 里的 COVER_3X4(img, t) 在 180×240 竖版画布上单独构图，再自动加标题、原唱、标签、署名；
                  没写 COVER_3X4 时，自动从第 --t 秒（默认 COVER_T）的原生画面裁出竖版来用（建议还是专门构图）。
  --also-16x9：额外导出 cover/封面_16x9.png（成片第 --t 秒的一帧），平台需要横版封面时再用。"""
import argparse, os
from _load import load

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--t', type=float, default=None)
ap.add_argument('--also-16x9', dest='also', action='store_true')
A = ap.parse_args()
mv = load(A.project)
os.makedirs(os.path.join(A.project, 'cover'), exist_ok=True)
t = A.t if A.t is not None else getattr(mv, 'COVER_T', None)
if t is None:
    raise SystemExit('✗ 给 --t 秒，或在 mv.py 里写 COVER_T = 秒（选全片最有戏、最能代表故事的一刻）')
from cover import build_3x4, portrait_from
pj = mv.song.p
if hasattr(mv, 'COVER_3X4'):
    draw = mv.COVER_3X4
else:
    print('！mv.py 里没有 COVER_3X4(img, t)：先从原生画面裁一个竖版应急；正式交付建议专门构图')
    i = mv.MVX.shot_at(t)
    native = mv.MVX.compose(t, i)

    def draw(img, tt):
        img.paste(portrait_from(native, 70, 60))
big = build_3x4(draw, t, pj['title'], pj.get('artist', ''), (pj.get('tag') or '像素 MV'), pj.get('signature', ''),
                getattr(mv, 'TITLE_STYLE', None))
p = os.path.join(A.project, 'cover', '封面.png')
big.save(p); print('✓', p, big.size)
if A.also:
    p2 = os.path.join(A.project, 'cover', '封面_16x9.png')
    mv.frame(t).save(p2); print('✓', p2)
