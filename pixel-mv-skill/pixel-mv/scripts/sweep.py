#!/usr/bin/env python3
"""全片扫一遍（不编码），尽早发现越界、除零之类的报错：python3 sweep.py 项目目录 [--step 3]"""
import argparse, time, traceback
from _load import load

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--step', type=int, default=3)
A = ap.parse_args()
mv = load(A.project)
t0 = time.time(); bad = 0
for k in range(0, int(mv.DUR * 30), A.step):
    try:
        mv.frame(k / 30)
    except Exception:
        bad += 1
        if bad <= 5:
            print(f'✗ {k / 30:.2f}s'); traceback.print_exc(limit=3)
print(('✓ 无报错' if not bad else f'✗ {bad} 帧报错'), f'（{int(mv.DUR * 30) // A.step} 帧，{time.time() - t0:.0f}s）')
raise SystemExit(1 if bad else 0)
