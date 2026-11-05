#!/usr/bin/env python3
"""全片扫一遍（不编码），尽早发现越界、除零之类的报错，并检查有没有重复使用的镜头：
  python3 sweep.py 项目目录 [--step 3]
重复镜头 = SHOTS 里同一个镜头函数出现两次以上。新流程要求重复的歌词也画新剧情，所以这算错误；
确实需要（比如片尾回到开场的同一个地方作首尾呼应，但人物状态已经变了）就在 mv.py 写 ALLOW_REPEAT = {函数名: 理由}。"""
import argparse, time, traceback
from collections import Counter
from _load import load

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--step', type=int, default=3)
A = ap.parse_args()
mv = load(A.project)
bad = 0
shots = mv.MVX.shots if hasattr(mv, 'MVX') else getattr(mv, 'SHOTS', [])
allow = getattr(mv, 'ALLOW_REPEAT', {})
cnt = Counter(getattr(s[1], '__name__', str(s[1])) for s in shots)
dups = {k: n for k, n in cnt.items() if n > 1 and k not in allow and not k.startswith('<lambda')}
for k, n in dups.items():
    print(f'✗ 镜头 {k} 用了 {n} 次：重复的歌词也要推进剧情、画新画面（见 references/story-design.md）')
replays = sum(1 for s in shots if s[2] == 'replay')
if replays:
    print(f'✗ 有 {replays} 个回放镜头（v=\'replay\'）：新流程不再用回放，重复段要画新剧情')
t0 = time.time()
for k in range(0, int(mv.DUR * 30), A.step):
    try:
        mv.frame(k / 30)
    except Exception:
        bad += 1
        if bad <= 5:
            print(f'✗ {k / 30:.2f}s'); traceback.print_exc(limit=3)
print(('✓ 无报错' if not bad else f'✗ {bad} 帧报错'), f'（{int(mv.DUR * 30) // A.step} 帧，{time.time() - t0:.0f}s）')
raise SystemExit(1 if (bad or dups or replays) else 0)
