#!/usr/bin/env python3
"""音频分析 → audio.json：时长、速度、全部节拍、主拍（较强的那一组）、每帧（30fps）低/中/高频能量与起音强度。
用法：python analyze_audio.py <音频文件> <输出 audio.json> [--half auto|yes|no]
--half：librosa 常把慢歌测成两倍速。auto = 测出的速度 > 100 BPM 时，隔一拍取一拍作为主拍。"""
import argparse, json
import numpy as np, librosa

ap = argparse.ArgumentParser(); ap.add_argument('audio'); ap.add_argument('out'); ap.add_argument('--half', default='auto')
a = ap.parse_args()
y, sr = librosa.load(a.audio, sr=22050)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
tempo = float(np.atleast_1d(tempo)[0])
hop = int(sr / 30)
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)); f = librosa.fft_frequencies(sr=sr, n_fft=2048)
def band(lo, hi):
    v = S[(f >= lo) & (f < hi)].mean(0); return v / max(np.percentile(v, 98), 1e-9)
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; rms = rms / max(np.percentile(rms, 98), 1e-9)
on = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop); on = on / max(np.percentile(on, 99), 1e-9)
n = len(rms)
half = a.half == 'yes' or (a.half == 'auto' and tempo > 100)
main = beats
if half and len(beats) > 4:
    idx = np.clip((beats * 30).astype(int), 0, n - 1)
    even, odd = on[idx[0::2]].mean(), on[idx[1::2]].mean()
    main = beats[0::2] if even >= odd else beats[1::2]
r = lambda arr: [round(float(x), 3) for x in arr[:n]]
json.dump(dict(fps=30, dur=len(y) / sr, tempo=tempo, main_tempo=tempo / 2 if half else tempo,
               beats=[round(float(b), 3) for b in beats], main_beats=[round(float(b), 3) for b in main],
               rms=r(rms), low=r(band(20, 150)), mid=r(band(150, 2000)), high=r(band(2000, 9000)), onset=r(on)),
          open(a.out, 'w'))
print(f'✓ {a.out}  时长 {len(y)/sr:.2f}s  测得 {tempo:.1f} BPM  主拍 {tempo/2 if half else tempo:.1f} BPM（{len(main)} 拍）')
