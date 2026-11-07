#!/usr/bin/env python3
"""音源检查：格式、采样率、位深、码率、标签（歌名 / 歌手 / 专辑），并用频谱判断是不是真无损。
用法：python probe_audio.py <音频或视频文件>
判断方法：有损编码（mp3 / aac）通常在 16–20 kHz 处一刀切；真无损的高频是平滑衰减到 Nyquist 附近的。"""
import json, subprocess, sys
import numpy as np, librosa
path = sys.argv[1]
info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', path],
                                 capture_output=True, text=True).stdout)
fmt = info['format']; a = next(s for s in info['streams'] if s['codec_type'] == 'audio')
tags = {k.lower(): v for k, v in (fmt.get('tags') or {}).items()}
print(f"文件：{path}\n时长：{float(fmt['duration']):.2f}s  编码：{a['codec_name']}  采样率：{a.get('sample_rate')} Hz  "
      f"位深：{a.get('bits_per_raw_sample') or a.get('sample_fmt')}  码率：{int(fmt.get('bit_rate', 0)) // 1000} kbps")
print('标签：' + '  '.join(f"{k}={tags[k]}" for k in ('title', 'artist', 'album', 'date') if k in tags) or '标签：无')
sr = int(a.get('sample_rate', 44100))
y, sr = librosa.load(path, sr=sr, mono=True, duration=120)
S = np.abs(librosa.stft(y, n_fft=8192, hop_length=4096)).mean(1)
f = librosa.fft_frequencies(sr=sr, n_fft=8192)
db = 20 * np.log10(S / S.max() + 1e-12)
def lvl(lo, hi): m = (f >= lo) & (f < hi); return float(db[m].mean()) if m.any() else float('nan')
edges = [(14000, 15500), (15500, 16500), (16500, 17500), (17500, 18500), (18500, 19500), (19500, 20500), (20500, 21500)]
lv = [lvl(*e) for e in edges]
for (lo, hi), v in zip(edges, lv):
    print(f'  {lo/1000:.1f}–{hi/1000:.1f} kHz  {v:6.1f} dB')
drops = [lv[i] - lv[i + 1] for i in range(len(lv) - 1)]
cut = max(drops) if drops else 0
if a['codec_name'] in ('mp3', 'aac', 'vorbis', 'opus'):
    verdict = '有损编码文件'
elif cut > 15:
    i = drops.index(cut); verdict = f'疑似有损转码：{edges[i][1]/1000:.1f} kHz 附近陡降 {cut:.0f} dB'
else:
    verdict = '高频平滑衰减，判断为真无损'
print('结论：' + verdict)
