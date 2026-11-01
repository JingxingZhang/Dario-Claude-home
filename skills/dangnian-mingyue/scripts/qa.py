#!/usr/bin/env python3
"""成片质检：时长、分辨率、体积（默认上限 100 MB）、响度、长时间静止、黑场。
  python3 -I qa.py <成片.mp4> [--max-mb 100]
有 ✗ 的项要处理；“静止 ≥ 2 秒”在 MV 里多是知识卡、片尾卡的停留，只修真正的空镜。音轨是 song_sync.py 归一到 −14 LUFS 的整首歌。"""
import json, re, subprocess, sys
args = sys.argv[1:]
if not args: sys.exit(__doc__)
f = args[0]
cap = float(args[args.index('--max-mb') + 1]) if '--max-mb' in args else 100.0
run = lambda *c: subprocess.run(c, capture_output=True, text=True)
p = json.loads(run('ffprobe', '-v', 'error', '-show_entries', 'format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate', '-of', 'json', f).stdout)
fmt = p['format']; v = next(s for s in p['streams'] if s['codec_type'] == 'video'); a = next((s for s in p['streams'] if s['codec_type'] == 'audio'), None)
D, size = float(fmt['duration']), int(fmt['size'])
bad = 0
def line(ok, msg):
    global bad
    if not ok: bad += 1
    print(('✓ ' if ok else '✗ ') + msg)
print(f'qa       {f}')
line(True, f"{v['width']}×{v['height']}  {eval(v['r_frame_rate']):.0f} fps  {v['codec_name']}  音频 {a['codec_name'] if a else '无'}  时长 {D:.2f}s（{D / 60:.1f} 分）")
line(size <= cap * 1e6, f'体积 {size / 1e6:.1f} MB（上限 {cap:.0f} MB）  码率 {int(fmt["bit_rate"]) / 1e6:.2f} Mbps')
if a:
    e = run('ffmpeg', '-hide_banner', '-nostats', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-').stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1]); tp = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)
    line(-15.5 <= I <= -13.0, f'响度 {I:.1f} LUFS（宜 −14 左右）' + (f'  真峰值 {float(tp[-1]):.1f} dBTP' if tp else ''))
else:
    line(False, '没有音轨')
e = run('ffmpeg', '-hide_banner', '-nostats', '-i', f, '-vf', 'freezedetect=n=0.002:d=2,blackdetect=d=0.5:pix_th=0.08', '-an', '-f', 'null', '-').stderr
fr = re.findall(r'freeze_start: ([\d.]+).*?freeze_end: ([\d.]+)', e.replace('\n', ' '))
bl = re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', e)
print(('· ' if fr else '✓ ') + ('静止 ≥ 2 秒：' + '、'.join(f'{float(s):.1f}–{float(t):.1f}s' for s, t in fr) if fr else '没有 ≥ 2 秒的静止'))
line(not bl, '黑场：' + ('、'.join(f'{float(s):.1f}–{float(t):.1f}s' for s, t in bl) if bl else '无'))
sys.exit(1 if bad else 0)
