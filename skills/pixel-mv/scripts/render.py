#!/usr/bin/env python3
"""渲染成片：并行出帧 → H.264 → 配原曲 → 体积不超过上限（默认 100 MB）。
  python3 render.py 项目目录 [--from 秒 --to 秒] [--draft] [--max-mb 100] [--workers 4] [--fps 30|60] [--out 文件.mp4]
--fps 60：动效（玻璃弹簧、托盘变形、透镜）更顺滑，渲染时间约翻倍。
音轨取 project.json 里的 audio（原曲 mp3/mp4/wav）。先按 CRF 18 + 码率封顶编码；万一仍超限，自动两遍编码压到上限的 94%。"""
import argparse, json, math, os, subprocess, sys, tempfile, time
from multiprocessing import Process

ap = argparse.ArgumentParser()
ap.add_argument('project'); ap.add_argument('--from', dest='t0', type=float, default=0); ap.add_argument('--to', dest='t1', type=float, default=None)
ap.add_argument('--draft', action='store_true'); ap.add_argument('--max-mb', type=float, default=100); ap.add_argument('--workers', type=int, default=4)
ap.add_argument('--out', default=None); ap.add_argument('--fps', type=int, default=30)
A = ap.parse_args()
PROJ = os.path.abspath(A.project)
pj = json.load(open(os.path.join(PROJ, 'project.json'), encoding='utf-8'))
FPS = A.fps


def work(i, f0, f1, path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _load import load
    mv = load(PROJ)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12' if not A.draft else '24', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    t = time.time()
    for k in range(f0, f1):
        ff.stdin.write(mv.frame(k / FPS).tobytes())
        if i == 0 and (k - f0) % 300 == 0:
            print(f'  帧 {k - f0}/{f1 - f0}（{time.time() - t:.0f}s）', flush=True)
    ff.stdin.close(); ff.wait()
    assert ff.returncode == 0


def size_mb(p):
    return os.path.getsize(p) / 1e6


if __name__ == '__main__':
    dur = float(pj['duration'])
    t1 = min(dur, A.t1 if A.t1 is not None else dur)
    F0, F1 = int(round(A.t0 * FPS)), int(math.ceil(t1 * FPS))
    os.makedirs(os.path.join(PROJ, 'out'), exist_ok=True)
    if A.out:
        out = os.path.abspath(A.out)
    else:
        base = os.path.join(PROJ, 'out', pj['title'] + ('-小样' if A.draft or A.t0 > 0 or t1 < dur else '') + '-像素MV')
        v = 1
        while os.path.exists(f'{base}-v{v}.mp4'):
            v += 1
        out = f'{base}-v{v}.mp4'
    tmp = tempfile.mkdtemp()
    per = math.ceil((F1 - F0) / A.workers)
    ps, segs = [], []
    t_start = time.time()
    for i in range(A.workers):
        a, b = F0 + i * per, min(F1, F0 + (i + 1) * per)
        if a >= b:
            break
        p = os.path.join(tmp, f'seg{i}.mp4'); segs.append(p)
        pr = Process(target=work, args=(i, a, b, p)); pr.start(); ps.append(pr)
    for pr in ps:
        pr.join()
        if pr.exitcode != 0:
            raise SystemExit('✗ 有进程出错：先跑 scripts/sweep.py 找报错的帧')
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    video = os.path.join(tmp, 'video.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    D = t1 - A.t0
    cap_kbps = int((A.max_mb * 1e6 * 0.94 * 8 / D - 192000) / 1000)
    audio = ['-ss', f'{A.t0:.3f}', '-t', f'{D:.3f}', '-i', pj['audio']]
    amap = ['-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest']
    common = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', str(FPS), '-movflags', '+faststart']
    preset = 'veryfast' if A.draft else 'slow'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, *audio, *amap, *common, '-preset', preset, '-crf', '24' if A.draft else '18',
                    '-maxrate', f'{cap_kbps}k', '-bufsize', f'{cap_kbps * 2}k', out], check=True)
    if size_mb(out) > A.max_mb:
        br = int(cap_kbps * 0.94)
        print(f'  {size_mb(out):.1f} MB 超过 {A.max_mb} MB，改两遍编码（{br} kbps）…')
        pl = os.path.join(tmp, 'x264')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-map', '0:v:0', *common, '-preset', preset, '-b:v', f'{br}k', '-pass', '1', '-passlogfile', pl, '-an', '-f', 'null', '/dev/null'], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, *audio, *amap, *common, '-preset', preset, '-b:v', f'{br}k', '-pass', '2', '-passlogfile', pl, out], check=True)
    pr_ = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', out], capture_output=True, text=True).stdout)
    got = float(pr_['format']['duration'])
    ok = size_mb(out) <= A.max_mb and abs(got - D) < 0.2
    print(f'{"✓" if ok else "✗"} {out}\n  {got:.2f}s（应为 {D:.2f}s）  {size_mb(out):.1f} MB（上限 {A.max_mb:.0f}）  用时 {time.time() - t_start:.0f}s')
    raise SystemExit(0 if ok else 1)
