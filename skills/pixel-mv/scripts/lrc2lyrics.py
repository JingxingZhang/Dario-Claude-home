#!/usr/bin/env python3
"""把 LRC 歌词（[mm:ss.xx]歌词）转成 lyrics.txt（开始 | 结束 | 歌词）。每句结束 = 下一句开始 - 0.1 秒（最长 6 秒）。
  python3 lrc2lyrics.py 歌词.lrc 输出/lyrics.txt [--dur 歌曲总秒数]"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
dur = float(sys.argv[sys.argv.index('--dur') + 1]) if '--dur' in sys.argv else None
rows = []
for line in open(src, encoding='utf-8-sig'):
    tags = re.findall(r'\[(\d+):(\d+(?:\.\d+)?)\]', line)
    text = re.sub(r'\[[^\]]*\]', '', line).strip()
    if not tags or not text:
        continue
    for m, s in tags:
        rows.append((int(m) * 60 + float(s), text))
rows.sort()
with open(out, 'w', encoding='utf-8') as f:
    f.write('# 开始秒 | 结束秒 | 歌词（/ 表示花字换行）——由 LRC 转换\n')
    for i, (t, s) in enumerate(rows):
        nxt = rows[i + 1][0] if i + 1 < len(rows) else (dur or t + 6)
        f.write(f'{t:.2f} | {min(nxt - 0.1, t + 6):.2f} | {s}\n')
print(f'✓ {out}  {len(rows)} 句')
