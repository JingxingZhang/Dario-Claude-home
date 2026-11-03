"""渲染成片：4 进程并行出 1920×1080 帧 → H.264；音轨直接取用户上传视频里的原曲（不重编码）。
  python3 render2.py --audio 原视频.mp4 [--from 秒 --to 秒] [--out 文件.mp4]"""
import argparse, math, os, subprocess, tempfile, time
from multiprocessing import Process
import mv2
from pixlib import ROOT, FPS

ap = argparse.ArgumentParser()
ap.add_argument('--audio', required=True)
ap.add_argument('--from', dest='t0', type=float, default=0)
ap.add_argument('--to', dest='t1', type=float, default=mv2.DUR)
ap.add_argument('--out', default=os.path.join(ROOT, 'out', '呼吸决定-像素MV.mp4'))
ap.add_argument('--workers', type=int, default=4)
A = ap.parse_args()


def work(i, f0, f1, path):
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    t = time.time()
    for k in range(f0, f1):
        ff.stdin.write(mv2.frame(k / FPS).tobytes())
        if i == 0 and (k - f0) % 200 == 0:
            print(f'  worker0 {k - f0}/{f1 - f0}  {time.time() - t:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()
    assert ff.returncode == 0


if __name__ == '__main__':
    os.makedirs(os.path.dirname(A.out), exist_ok=True)
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
        pr.join(); assert pr.exitcode == 0, 'worker failed'
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-ss', f'{A.t0:.3f}', '-t', f'{A.t1 - A.t0:.3f}', '-i', A.audio,
                    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', A.out], check=True)
    print('done', A.out, f'{os.path.getsize(A.out)/1e6:.1f} MB')
