#!/usr/bin/env python3
"""从带硬字幕的歌词视频里找出每段字幕的起止时间，并拼成对照图，供人工（Claude 看图）识读。
用法：python sub_detect.py <视频> <输出目录> [--band 0.70,0.86] [--thresh 128]
--band：字幕所在的高度范围（占画面高度的比例）。不确定时先不传，脚本会自动找“文字最多变化”的横条，并输出 band.png 供检查。
输出：segments.json（[{i, t0, t1}]）、sheet_0.png、sheet_1.png …（每张 28 段，左边是序号和时间）"""
import argparse, json, os
import cv2, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--band', default=None); ap.add_argument('--thresh', type=int, default=128)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cap = cv2.VideoCapture(a.video); fps = cap.get(5) or 30; Hh = int(cap.get(4)); Ww = int(cap.get(3))
frames = []; i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if i % max(1, int(round(fps / 10))) == 0:
        frames.append((i / fps, (cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) > a.thresh).astype(np.uint8)))
    i += 1
if a.band:
    y0, y1 = [int(float(v) * Hh) for v in a.band.split(',')]
else:   # 自动：逐行统计相邻采样之间的变化量，取变化最集中的一条带
    var = np.zeros(Hh)
    for (_, p), (_, q) in zip(frames, frames[1:]): var += np.abs(p.astype(int) - q.astype(int)).sum(1)
    k = np.convolve(var, np.ones(max(8, Hh // 12)), 'same'); c = int(k.argmax()); h = max(40, Hh // 9)
    y0, y1 = max(0, c - h // 2), min(Hh, c + h // 2)
    print(f'自动选择字幕带：第 {y0}–{y1} 行（{y0/Hh:.2f}–{y1/Hh:.2f}），请看 band.png 确认')
cap = cv2.VideoCapture(a.video); cap.set(1, int(len(frames) / 2 * fps / 10)); ok, f = cap.read()
if ok:
    cv2.rectangle(f, (0, y0), (Ww - 1, y1), (0, 0, 255), 3); cv2.imwrite(os.path.join(a.out, 'band.png'), f)
segs, cur = [], None
for t, b in frames:
    band = b[y0:y1]; s = int(band.sum())
    if s < 20:
        if cur: segs.append(cur); cur = None
        continue
    if cur is None or np.abs(band.astype(int) - cur['b'].astype(int)).sum() > 0.15 * max(s, int(cur['b'].sum())):
        if cur: segs.append(cur)
        cur = dict(t0=t, t1=t, b=band)
    else:
        cur['t1'] = t
if cur: segs.append(cur)
segs = [s for s in segs if s['t1'] - s['t0'] >= 0.25]
json.dump([dict(i=k, t0=round(s['t0'], 2), t1=round(s['t1'] + 0.1, 2)) for k, s in enumerate(segs)],
          open(os.path.join(a.out, 'segments.json'), 'w'), ensure_ascii=False, indent=0)
tiles = []
for k, s in enumerate(segs):
    b = s['b'] * 255
    cols = np.where(b.max(0) > 0)[0]
    if len(cols): b = b[:, max(0, cols[0] - 10):cols[-1] + 10]
    b = cv2.resize(b, (min(900, b.shape[1]), b.shape[0]))
    lab = np.zeros((b.shape[0], 190), np.uint8)
    cv2.putText(lab, f"{k} {s['t0']:.1f}-{s['t1']:.1f}", (2, b.shape[0] // 2 + 6), cv2.FONT_HERSHEY_SIMPLEX, .55, 255, 1)
    row = np.zeros((b.shape[0], 1090), np.uint8); row[:, :190] = lab; row[:, 190:190 + b.shape[1]] = b
    tiles.append(row)
for p in range(0, len(tiles), 28):
    cv2.imwrite(os.path.join(a.out, f'sheet_{p // 28}.png'), 255 - np.vstack(tiles[p:p + 28]))
print(f'✓ {len(segs)} 段字幕 → {a.out}/segments.json，对照图 sheet_*.png')
