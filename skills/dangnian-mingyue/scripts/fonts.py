#!/usr/bin/env python3
"""准备字体：从官方源下载思源宋体（Noto Serif SC，版画画面的主字体）、霞鹜文楷、思源黑体（Noto Sans SC），按 GB2312 做子集，转成 WOFF，放进缓存目录。
setup.sh 会调用它；已经做好的会跳过。new_chapter.sh 从缓存目录把字体拷进每个章节。

  python3 fonts.py [缓存目录=~/.cache/ming-fonts]

产物：NotoSerifSC-600/900.woff、LXGWWenKai-500.woff、NotoSansSC-500/700/900.woff、OFL.txt（三种字体的 SIL OFL 1.1 许可全文）。
子集只含 GB2312 的 6763 个汉字 + ASCII + 常用中文标点，只用于网页渲染视频画面。
缺字（GB2312 以外的生僻字，如“蹚、璘、懽”）会显示成方块，写完讲稿跑 check_glyphs.py。
"""
import os, sys, shutil, subprocess, tempfile, urllib.request

OUT = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/.cache/ming-fonts')
NEED = ['NotoSerifSC-600.woff', 'NotoSerifSC-900.woff', 'LXGWWenKai-500.woff', 'NotoSansSC-500.woff', 'NotoSansSC-700.woff', 'NotoSansSC-900.woff', 'OFL.txt']
SRC = {
    'wenkai': ['https://github.com/lxgw/LxgwWenKai/releases/latest/download/LXGWWenKai-Medium.ttf'],
    'noto': ['https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf',
             'https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf'],
    'serif': ['https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf',
              'https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf'],
    'ofl_serif': ['https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifsc/OFL.txt',
                  'https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notoserifsc/OFL.txt'],
    'ofl_wenkai': ['https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/OFL.txt',
                   'https://cdn.jsdelivr.net/gh/lxgw/LxgwWenKai@main/OFL.txt'],
    'ofl_noto': ['https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt',
                 'https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosanssc/OFL.txt'],
}

if all(os.path.exists(os.path.join(OUT, f)) for f in NEED):
    print(f'✓ 字体已就绪：{OUT}'); sys.exit(0)
os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp(prefix='ming-fonts-')


def fetch(key, name):
    dst = os.path.join(tmp, name)
    for url in SRC[key]:
        try:
            print(f'  下载 {url}', flush=True)
            with urllib.request.urlopen(url, timeout=120) as r, open(dst, 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b)
            if os.path.getsize(dst) > 1000: return dst
        except Exception as e:
            print(f'  失败：{e}', flush=True)
    sys.exit(f'✗ 下载不到 {name}：检查网络（需要能访问 github.com / raw.githubusercontent.com 或 cdn.jsdelivr.net）')


chars = set()
for b1 in range(0xA1, 0xF8):
    for b2 in range(0xA1, 0xFF):
        try: chars.add(bytes([b1, b2]).decode('gb2312'))
        except UnicodeDecodeError: pass
chars |= {chr(c) for c in range(0x20, 0x7F)}
chars |= set('·—–…“”‘’《》〈〉「」『』【】〔〕（）！？，。；：、～￥％＋－×÷→←↑↓↔⇄✓✕○●◆■□△▲①②③④⑤⑥⑦⑧⑨⑩　©®°±')
txt = os.path.join(tmp, 'chars.txt'); open(txt, 'w', encoding='utf-8').write(''.join(sorted(chars)))


def subset(src, dst):
    subprocess.run([sys.executable, '-m', 'fontTools.subset', src, f'--text-file={txt}', '--flavor=woff', "--layout-features=*",
                    f'--output-file={os.path.join(OUT, dst)}'], check=True)
    print(f'  ✓ {dst}  {os.path.getsize(os.path.join(OUT, dst)) / 1e6:.1f} MB', flush=True)


wk = fetch('wenkai', 'LXGWWenKai-Medium.ttf')
subset(wk, 'LXGWWenKai-500.woff')
vf = fetch('noto', 'NotoSansSC-VF.ttf')
for w in (500, 700, 900):
    inst = os.path.join(tmp, f'noto{w}.ttf')
    subprocess.run([sys.executable, '-m', 'fontTools.varLib.instancer', '-q', vf, f'wght={w}', '-o', inst], check=True)
    subset(inst, f'NotoSansSC-{w}.woff')
sf = fetch('serif', 'NotoSerifSC-VF.ttf')
for w in (600, 900):
    inst = os.path.join(tmp, f'serif{w}.ttf')
    subprocess.run([sys.executable, '-m', 'fontTools.varLib.instancer', '-q', sf, f'wght={w}', '-o', inst], check=True)
    subset(inst, f'NotoSerifSC-{w}.woff')
ofl = '=== 思源宋体 Noto Serif SC ===\n' + open(fetch('ofl_serif', 'ofl0.txt'), encoding='utf-8').read() + '\n\n=== 霞鹜文楷 LXGW WenKai ===\n' + open(fetch('ofl_wenkai', 'ofl1.txt'), encoding='utf-8').read() + \
      '\n\n=== 思源黑体 Noto Sans SC ===\n' + open(fetch('ofl_noto', 'ofl2.txt'), encoding='utf-8').read()
open(os.path.join(OUT, 'OFL.txt'), 'w', encoding='utf-8').write(ofl)
shutil.rmtree(tmp, ignore_errors=True)
print(f'✓ 字体已就绪：{OUT}')
