#!/usr/bin/env python3
"""生成 歌词分镜稿.md：逐句时间、段落、歌词、所在镜头、主题栏（先跑 check.js 写出 out/shots.json）。
  python3 -I lyrics_md.py <章节目录>"""
import sys, os, json
root = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
f = os.path.join(root, 'out', 'shots.json')
if not os.path.exists(f): sys.exit('✗ 没有 out/shots.json：先跑 node scripts/check.js <章节目录>')
d = json.load(open(f, encoding='utf-8')); shots, song = d['shots'], d['song']
ts = lambda t: f'{int(t // 60)}:{t % 60:04.1f}'
def topic(t):
    cur = ''
    for x in song.get('topics', []):
        if x['t'] <= t + 1e-6: cur = x['text']
    return cur
def shot_of(a, b): return '、'.join(s['name'] for s in shots if s['t0'] < b and s['t1'] > a)
out = [f'# 歌词分镜稿 · {os.path.basename(os.path.abspath(root))}', '', f"歌长 {ts(song['duration'])}；{len(song['lines'])} 句；{len(shots)} 个镜头。时间为成片时间。", '',
       '## 段落', '', '| 段落 | 时间 | 主题栏 |', '|---|---|---|']
for s in song['sections']: out.append(f"| {s['label']} | {ts(s['start'])}–{ts(s['end'])} | {topic(s['start'] + 0.05)} |")
out += ['', '## 逐句', '', '| 句 | 时间 | 段落 | 歌词 | 镜头 |', '|---|---|---|---|---|']
for i, l in enumerate(song['lines']):
    out.append(f"| {i + 1} | {ts(l['start'])} | {'**' if l['chorus'] else ''}{l.get('tag') or ''}{'**' if l['chorus'] else ''} | {l['text']} | {shot_of(l['start'], l['end'])} |")
out += ['', '## 镜头表', '', '| 镜头 | 时间 | 转场 | 大字 |', '|---|---|---|---|']
for s in shots: out.append(f"| {s['name']} | {ts(s['t0'])}–{ts(s['t1'])} | {s['trans']} | {s['type']} |")
open(os.path.join(root, '歌词分镜稿.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n'); print('歌词分镜稿.md', len(song['lines']), '句', len(shots), '镜')
