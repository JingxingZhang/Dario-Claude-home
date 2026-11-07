#!/usr/bin/env python3
"""把成片按字节切成 ≤19 MB 的小块（下载页单个文件上限 20 MB），并核对拼回去和原片逐字节一致。
用法：python split_upload.py <成片.mp4> <输出目录> [--prefix v1]
输出：<prefix>_0.mp4、<prefix>_1.mp4 …，以及 manifest.json（总字节数、各块文件名）。"""
import argparse, hashlib, json, os
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('out'); ap.add_argument('--prefix', default='part')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
CH = 19 * 1024 * 1024
data = open(a.video, 'rb').read(); names = []
for k in range(0, len(data), CH):
    n = f'{a.prefix}_{k // CH}.mp4'; open(os.path.join(a.out, n), 'wb').write(data[k:k + CH]); names.append(n)
joined = b''.join(open(os.path.join(a.out, n), 'rb').read() for n in names)
assert hashlib.sha256(joined).digest() == hashlib.sha256(data).digest(), '拼合校验失败'
json.dump(dict(total=len(data), parts=names), open(os.path.join(a.out, 'manifest.json'), 'w'), indent=1)
print(f'✓ {len(names)} 块，共 {len(data)} 字节，拼合校验通过 → {a.out}')
