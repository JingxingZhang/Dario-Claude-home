#!/usr/bin/env python3
"""把“参考音频”上的歌词时间迁移到“目标音频”（例如：从歌词视频的音轨迁移到无损原版）。
用法：python align_lines.py <参考音频/视频> <目标音频> <lines.json（时间在参考音频上）> <输出 lines_aligned.json>
做法：两边各算 chroma（每 0.1 秒一帧），用每句在参考里的片段，到目标里滑动找最相似的位置。
  - 相似度 ≥ 0.99 = 同一段录音；0.93–0.99 = 旋律相同、演唱或伴奏不同；更低 = 不可靠，标出来人工确认。
  - 两个音源结构不同（剪辑版、拼接版、现场版）时，同一句可能对应多个位置，输出里列出前三个候选。
结果里每句带 conf 和 candidates，并按“相邻句时间顺序”做一致性检查。"""
import json, sys
import numpy as np, librosa
ref_path, tgt_path, lines_path, out_path = sys.argv[1:5]
sr, hop = 22050, 2205
def chroma(p):
    y, _ = librosa.load(p, sr=sr)
    c = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    return c / (np.linalg.norm(c, axis=0, keepdims=True) + 1e-9)
cr, ct = chroma(ref_path), chroma(tgt_path)
lines = json.load(open(lines_path))
def sims(T):
    L = T.shape[1]
    return np.array([(T * ct[:, k:k + L]).sum() / L for k in range(ct.shape[1] - L)])
prev = -1e9; out = []
for l in lines:
    a, b = int(l['t0'] * 10), int(max(l['t1'], l['t0'] + 1.5) * 10)
    s = sims(cr[:, a:b]); cands = []
    s2 = s.copy()
    for _ in range(3):
        k = int(s2.argmax()); cands.append((round(k / 10, 2), round(float(s2[k]), 3))); s2[max(0, k - 40):k + 40] = -1
    # 选第一个在上一句之后、且相似度不比最好的差 0.01 以上的候选
    best = max(cands, key=lambda c: c[1])
    pick = next((c for c in sorted(cands) if c[0] > prev - 0.5 and c[1] >= best[1] - 0.01), best)
    d = pick[0] - l['t0']
    m = dict(l); m['t0'] = round(l['t0'] + d, 2); m['t1'] = round(l['t1'] + d, 2)
    if 'seg' in m: m['seg'] = [(n, round(x + d, 2), round(y + d, 2)) for n, x, y in m['seg']]
    m['conf'] = pick[1]; m['candidates'] = cands
    m['order_ok'] = m['t0'] > prev - 0.5
    out.append(m); prev = max(prev, m['t0'])
json.dump(out, open(out_path, 'w'), ensure_ascii=False, indent=1)
for m in out:
    flag = '' if m['conf'] >= 0.95 else '  ← 置信度低，请人工确认'
    if not m['order_ok']: flag += '  ← 时间倒退：两个音源结构不同（拼接/剪辑版），看 candidates 手工重排'
    print(f"{m['t0']:7.2f}  {m['conf']:.3f}  {m['text']}{flag}")
print(f'✓ {out_path}')
