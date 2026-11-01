#!/usr/bin/env python3
"""检查歌词、分镜、封面里用到的字，项目字体里有没有（缺字会显示成方块）。
  python3 -I check_glyphs.py <章节目录>"""
import sys, os, re, glob
from fontTools.ttLib import TTFont
root = sys.argv[1]
txt = ''
for f in glob.glob(os.path.join(root, 'tools', 'lyrics*.txt')) + [os.path.join(root, 'assets', 'chapter.js'), os.path.join(root, 'cover', 'cover.html'), os.path.join(root, 'index.html')]:
    if os.path.exists(f): txt += open(f, encoding='utf-8').read()
chars = set(c for c in txt if ord(c) > 0x2e80)
bad = False
for f in sorted(glob.glob(os.path.join(root, 'assets', 'fonts', '*.woff'))):
    if not re.search(r'NotoSerifSC-(600|900)', f): continue
    cmap = TTFont(f).getBestCmap()
    miss = sorted(c for c in chars if ord(c) not in cmap)
    if miss: bad = True
    print(os.path.basename(f), '缺字：' + ''.join(miss) if miss else '齐全')
sys.exit(1 if bad else 0)
