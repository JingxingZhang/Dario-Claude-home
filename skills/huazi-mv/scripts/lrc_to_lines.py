#!/usr/bin/env python3
"""LRC 歌词 → lines.json（config.py 里 LINES 的起点）。
用法：python lrc_to_lines.py <歌词.lrc> <输出 lines.json> [--offset 0.0]
每句的结束时间 = 下一句开始前 0.2 秒（最长 6 秒）。之后在 config.py 里补 style / sec / acc 等字段。"""
import argparse, json, re
ap = argparse.ArgumentParser(); ap.add_argument('lrc'); ap.add_argument('out'); ap.add_argument('--offset', type=float, default=0.0)
a = ap.parse_args()
rows = []
for raw in open(a.lrc, encoding='utf-8-sig'):
    stamps = re.findall(r'\[(\d+):(\d+(?:\.\d+)?)\]', raw)
    text = re.sub(r'\[[^\]]*\]', '', raw).strip()
    if not stamps or not text: continue
    if re.match(r'^(作词|作曲|编曲|制作|词|曲|by|Lyrics|Composer)\s*[:：]', text, re.I): continue
    for m, s in stamps:
        rows.append((int(m) * 60 + float(s) + a.offset, text))
rows.sort()
out = []
for k, (t0, text) in enumerate(rows):
    t1 = min(rows[k + 1][0] - 0.2, t0 + 6.0) if k + 1 < len(rows) else t0 + 4.0
    out.append(dict(t0=round(t0, 2), t1=round(t1, 2), text=text))
json.dump(out, open(a.out, 'w'), ensure_ascii=False, indent=1)
print(f'✓ {len(out)} 句 → {a.out}')
