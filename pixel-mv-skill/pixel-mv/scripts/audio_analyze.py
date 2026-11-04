#!/usr/bin/env python3
"""音频分析：逐帧音量（30 fps，归一化 0–1）、BPM、每拍时刻 → audio.json。
  python3 audio_analyze.py 歌曲(mp3/mp4/wav) 输出/audio.json"""
import json, subprocess, sys
import numpy as np

src, out = sys.argv[1], sys.argv[2]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '22050', '-f', 's16le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(float) / 32768
sr = 22050; hop = sr // 100
n = len(x) // hop
rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
win = 1024
frames = np.lib.stride_tricks.sliding_window_view(x, win)[::hop]
spec = np.abs(np.fft.rfft(frames * np.hanning(win), axis=1))
flux = np.concatenate([[0], np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(1)])
o = np.maximum(flux - np.convolve(flux, np.ones(50) / 50, 'same'), 0)
a0, a1 = int(len(o) * 0.12), int(len(o) * 0.6)   # 用歌曲中段估速度
seg = o[a0:a1] - o[a0:a1].mean()
ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
best = max(np.arange(60, 181, 0.5), key=lambda b: ac[int(round(6000 / b))] + 0.5 * ac[int(round(12000 / b))])
P = 6000 / best
ph = max(range(int(P)), key=lambda p: o[np.arange(p + a0, a1, P).astype(int)].sum())
dur = len(x) / sr
beats = [(ph + k * P) / 100 for k in range(-2000, 4000) if 0 <= (ph + k * P) / 100 < dur]
r30 = [float(rms[int(i * 100 / 30):int((i + 1) * 100 / 30)].mean() or 0) for i in range(int(dur * 30))]
mx = np.percentile(r30, 98) or 1
json.dump({'bpm': float(best), 'beats': beats, 'rms': [round(min(1, v / mx), 3) for v in r30], 'dur': dur}, open(out, 'w'))
print(f'✓ {out}  时长 {dur:.2f}s  BPM≈{best:.1f}（每拍 {P / 100:.2f}s）  {len(beats)} 拍')
