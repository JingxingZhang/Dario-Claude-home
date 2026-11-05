#!/usr/bin/env python3
"""下载并整理三套 OFL 字体（经 jsDelivr 的 npm 包）：
  Fusion Pixel 12px（像素字）→ ~/.cache/pixfont/map12.json + t12/*.ttf
  站酷庆科黄油体 / 站酷快乐体（花字）→ ~/.cache/huafont/<family>.json + <family>-ttf/*.ttf
已下好的跳过。用法：python3 fonts.py"""
import json, os, ssl, sys, urllib.request
from fontTools.ttLib import TTFont

CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'pixel-mv-skill/1.0'})
    for i in range(4):
        try:
            return urllib.request.urlopen(req, context=CTX, timeout=60).read()
        except Exception as e:
            if i == 3:
                raise
    return b''


def files(pkg, ver):
    d = json.loads(get(f'https://data.jsdelivr.com/v1/packages/npm/{pkg}@{ver}?structure=flat'))
    return [f['name'] for f in d['files']]


def build(dst_dir, pkg, ver, pick, map_path, ttf_dir):
    if os.path.exists(map_path):
        print('✓ 已有', map_path); return
    os.makedirs(ttf_dir, exist_ok=True)
    names = [n for n in files(pkg, ver) if pick(n)]
    m = {}
    for n in sorted(names):
        out = os.path.join(ttf_dir, os.path.basename(n).replace('.woff2', '.ttf'))
        if not os.path.exists(out):
            raw = os.path.join(ttf_dir, '_tmp.woff2')
            open(raw, 'wb').write(get(f'https://cdn.jsdelivr.net/npm/{pkg}@{ver}{n}'))
            t = TTFont(raw); t.flavor = None; t.save(out); os.remove(raw)
        for cp in TTFont(out).getBestCmap():
            m.setdefault(str(cp), out)
    json.dump(m, open(map_path, 'w'))
    print('✓', pkg, len(names), '个分片，', len(m), '个字符 →', map_path)


home = os.path.expanduser('~/.cache')
pix = os.environ.get('PIXFONT', os.path.join(home, 'pixfont'))
hua = os.environ.get('HUAFONT', os.path.join(home, 'huafont'))
build(pix, '@vp-tw/cjk-web-fonts-fusion-pixel-font', '0.0.1',
      lambda n: n.startswith('/dist/12px/monospaced/zh_hans/') and n.endswith('.woff2'),
      os.path.join(pix, 'map12.json'), os.path.join(pix, 't12'))
for fam in ('zcool-qingke-huangyou', 'zcool-kuaile'):
    build(hua, f'@fontsource/{fam}', '5.3.0', lambda n: n.endswith('-400-normal.woff2'),
          os.path.join(hua, fam + '.json'), os.path.join(hua, fam + '-ttf'))
