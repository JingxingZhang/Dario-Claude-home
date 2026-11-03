"""渲染成片：4 进程并行画帧（320×180）→ ffmpeg 最近邻放大到 1920×1080 → H.264。
  python3 render.py [--from 秒 --to 秒] [--out 文件.mp4] [--song mp3]
有 --song 时：响度归一到 -14 LUFS 后配进去；没有就出无声版（之后用 mux.sh 配歌）。"""
import argparse, math, os, subprocess, sys, tempfile, time
from multiprocessing import Process
import mv
from pixlib import W, H, SCALE, FPS

ap = argparse.ArgumentParser()
ap.add_argument('--from', dest='t0', type=float, default=0)
ap.add_argument('--to', dest='t1', type=float, default=mv.DUR)
ap.add_argument('--out', default=None)
ap.add_argument('--song', default=None)
ap.add_argument('--workers', type=int, default=4)
ap.add_argument('--crf', type=int, default=16)
A = ap.parse_args()
OUTDIR = os.path.join(mv.ROOT if hasattr(mv, 'ROOT') else '..', 'out')
from pixlib import ROOT
OUTDIR = os.path.join(ROOT, 'out'); os.makedirs(OUTDIR, exist_ok=True)


def work(i, f0, f1, path):
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-vf', f'scale={W*SCALE}:{H*SCALE}:flags=neighbor', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(A.crf),
                           '-pix_fmt', 'yuv420p', '-tune', 'animation', path], stdin=subprocess.PIPE)
    t = time.time()
    for k in range(f0, f1):
        ff.stdin.write(mv.frame(k / FPS).tobytes())
        if i == 0 and (k - f0) % 300 == 0:
            print(f'  worker0 {k - f0}/{f1 - f0}  {time.time() - t:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()
    assert ff.returncode == 0


if __name__ == '__main__':
    F0, F1 = int(round(A.t0 * FPS)), int(math.ceil(A.t1 * FPS))
    tmp = tempfile.mkdtemp()
    per = math.ceil((F1 - F0) / A.workers)
    ps, segs = [], []
    for i in range(A.workers):
        a, b = F0 + i * per, min(F1, F0 + (i + 1) * per)
        if a >= b: break
        p = os.path.join(tmp, f'seg{i}.mp4'); segs.append(p)
        pr = Process(target=work, args=(i, a, b, p)); pr.start(); ps.append(pr)
    for pr in ps:
        pr.join(); assert pr.exitcode == 0
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    out = A.out or os.path.join(OUTDIR, 'ep12-dengfenglai-pixel' + ('' if A.song else '-silent') + '.mp4')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst]
    if A.song:
        cmd += ['-ss', f'{A.t0:.3f}', '-i', A.song, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest']
    else:
        cmd += ['-c', 'copy']
    cmd += ['-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    print('done', out, f'{os.path.getsize(out)/1e6:.1f} MB')
