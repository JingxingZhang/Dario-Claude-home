#!/usr/bin/env python3
"""整片渲染：分段并行出帧 → 拼接二次编码 → 配音频。
用法：python render_all.py <项目目录> <音频文件> <输出.mp4> [--workers 4] [--crf 22] [--audio aac|alac] [--fade-out 0]
  --audio aac ：AAC 320 kbps，兼容性最好（默认）
  --audio alac：无损音轨（苹果设备直接播放，部分 Windows 播放器不支持，文件更大）
  --fade-out N：音源结尾是硬切时，最后 N 秒淡出
中间文件放在 <项目目录>/render/；分段先用 crf 19 保留质量，最后统一用 --crf 二次编码。"""
import argparse, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('audio'); ap.add_argument('out')
ap.add_argument('--workers', type=int, default=4); ap.add_argument('--crf', type=int, default=22)
ap.add_argument('--audio-codec', '--audio', dest='acodec', default='aac'); ap.add_argument('--fade-out', type=float, default=0)
a = ap.parse_args()
P = os.path.abspath(a.project); R = os.path.join(P, 'render'); os.makedirs(R, exist_ok=True)
info = json.loads(subprocess.run([sys.executable, os.path.join(HERE, 'engine.py'), P, 'info'], capture_output=True, text=True).stdout.strip().splitlines()[-1])
N, total, aend = info['frames'], info['total'], info['audio_end']
print(f'共 {N} 帧（{total:.1f}s），{a.workers} 个进程并行……', flush=True)
t0 = time.time(); procs = []; parts = []
step = (N + a.workers - 1) // a.workers
for i in range(a.workers):
    s, e = i * step, min(N, (i + 1) * step)
    if s >= e: break
    path = os.path.join(R, f'part{i}.mp4'); parts.append(path)
    log = open(os.path.join(R, f'log{i}.txt'), 'w')
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, 'engine.py'), P, 'chunk', str(s), str(e), path, '19'], stdout=log, stderr=subprocess.STDOUT))
for p in procs:
    if p.wait() != 0: sys.exit('✗ 有分段渲染失败，看 render/log*.txt')
print(f'✓ 画面渲染完成（{(time.time() - t0) / 60:.1f} 分钟）', flush=True)
lst = os.path.join(R, 'list.txt')
open(lst, 'w').write(''.join(f"file '{os.path.basename(p)}'\n" for p in parts))
af = f'apad=whole_dur={total}'
if a.fade_out > 0: af = f'afade=t=out:st={aend - a.fade_out}:d={a.fade_out},' + af
acodec = ['-c:a', 'aac', '-b:a', '320k'] if a.acodec == 'aac' else ['-c:a', 'alac']
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', a.audio, '-map', '0:v', '-map', '1:a',
       '-af', af, *acodec, '-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf), '-tune', 'film', '-pix_fmt', 'yuv420p',
       '-movflags', '+faststart', '-t', str(total), a.out]
subprocess.run(cmd, check=True)
pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', a.out], capture_output=True, text=True).stdout)['format']
print(f"✓ {a.out}  {float(pr['duration']):.2f}s  {int(pr['size']) / 1e6:.1f} MB  总用时 {(time.time() - t0) / 60:.1f} 分钟")
