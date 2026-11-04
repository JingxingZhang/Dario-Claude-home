#!/usr/bin/env python3
"""从带硬字幕的歌词视频里切出每一行字幕的起止时间，并导出截图拼图，供 Claude 看图读字。
  python3 lyrics_ocr.py 视频.mp4 输出目录 [--band 0.10,0.45] [--xband 0,1] [--color white|bright] [--fps 10]
输出：
  segs.json            每行 [开始秒, 结束秒]
  lines_1.png …        每行一张截图（左上角标着时间），每张拼图 18 行
  band.png             自动选中的字幕区域（红框），先看一眼确认选对了
  lyrics_skeleton.txt  “开始 | 结束 | ？？？”，把 ？？？ 换成读出的歌词即成 lyrics.txt
--band 不给时自动找：字幕所在的横条是“白色文字出现、消失最频繁”的那一段。"""
import argparse, json, os, subprocess
import numpy as np
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--band', default=None, help='字幕所在纵向范围（占画面高度的比例），如 0.10,0.45')
ap.add_argument('--xband', default='0,1', help='横向范围比例')
ap.add_argument('--color', default='white', choices=['white', 'bright'])
ap.add_argument('--fps', type=int, default=10)
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)

probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', A.video],
                                  capture_output=True, check=True).stdout)['streams'][0]
SW = 320; SH = int(round(probe['height'] * SW / probe['width'] / 2) * 2)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', A.video, '-vf', f'fps={A.fps},scale={SW}:{SH},format=rgb24', '-f', 'rawvideo', '-'],
                     capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
x0, x1 = [int(float(v) * SW) for v in A.xband.split(',')]


def textmask(a):
    a = a.astype(int)
    mx, mn = a.max(-1), a.min(-1)
    return (mn > 200) & (mx - mn < 40) if A.color == 'white' else (mx > 225)


if A.band:
    y0, y1 = [int(float(v) * SH) for v in A.band.split(',')]
else:  # 自动：按行统计文字像素随时间的变化量，取变化最多的一段（高度约 18% 画面）
    step = max(1, len(fr) // 600)
    ms = np.stack([textmask(f[:, x0:x1]) for f in fr[::step]])
    score = ms.std(0).sum(1)
    hh = max(8, int(SH * 0.18))
    cs = np.convolve(score, np.ones(hh), 'valid')
    y0 = int(cs.argmax()); y1 = y0 + hh
    pad = int(SH * 0.03); y0 = max(0, y0 - pad); y1 = min(SH, y1 + pad)
prev = Image.fromarray(fr[len(fr) // 2]).resize((SW * 2, SH * 2))
ImageDraw.Draw(prev).rectangle([x0 * 2, y0 * 2, x1 * 2 - 1, y1 * 2 - 1], outline=(255, 0, 0), width=3)
prev.save(os.path.join(A.out, 'band.png'))

band = np.stack([textmask(f[y0:y1, x0:x1]) for f in fr])
cnt = band.reshape(len(band), -1).sum(1)
thr = max(30, band.shape[1] * band.shape[2] * 0.004)
segs, cur = [], None
for i, c in enumerate(cnt):
    on = c > thr
    if on and cur is None:
        cur = [i, i]
    elif on:
        diff = (band[i] ^ band[i - 1]).sum()
        if diff > 0.5 * max(band[i].sum(), band[i - 1].sum()):
            segs.append(cur); cur = [i, i]
        else:
            cur[1] = i
    elif cur is not None:
        segs.append(cur); cur = None
if cur:
    segs.append(cur)
segs = [s for s in segs if s[1] - s[0] >= 3]
times = [[round(s[0] / A.fps, 2), round((s[1] + 1) / A.fps, 2)] for s in segs]
json.dump(times, open(os.path.join(A.out, 'segs.json'), 'w'))

tiles = []
for (s, (a, b)) in zip(segs, times):
    m = (s[0] + s[1]) // 2
    im = Image.fromarray(fr[m][y0:y1, x0:x1]).resize(((x1 - x0) * 3 // 2 * 2, (y1 - y0) * 3 // 2 * 2))
    ImageDraw.Draw(im).text((4, 2), f'{a:.1f}-{b:.1f}', fill=(255, 0, 255))
    tiles.append(im)
per = 18
for k in range(0, len(tiles), per):
    sub = tiles[k:k + per]
    tw, th = sub[0].size
    sh = Image.new('RGB', (tw * 3, th * ((len(sub) + 2) // 3)))
    for i, im in enumerate(sub):
        sh.paste(im, ((i % 3) * tw, (i // 3) * th))
    sh.save(os.path.join(A.out, f'lines_{k // per + 1}.png'))
with open(os.path.join(A.out, 'lyrics_skeleton.txt'), 'w', encoding='utf-8') as f:
    f.write('# 开始秒 | 结束秒 | 歌词（/ 表示花字换行）——时间读自原视频字幕，把 ？？？ 换成拼图里读出的歌词\n')
    for i, (a, b) in enumerate(times):
        nxt = times[i + 1][0] if i + 1 < len(times) else b + 3
        f.write(f'{a:.1f} | {max(b, min(nxt - 0.1, b + 0.6)):.1f} | ？？？\n')
print(f'✓ 字幕区域 y {y0}-{y1}/{SH}（见 band.png）  切出 {len(times)} 行  拼图 {(len(tiles) + per - 1) // per} 张 → {A.out}')
