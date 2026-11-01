#!/usr/bin/env python3
"""把 still.js 导出的一批 PNG 拼成接触印样（按时间排序，标注文件名）。
  python3 -I sheet.py <png目录> <输出.png> [每行几张=6] [每张宽=300]"""
import sys, glob, re, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
w = int(sys.argv[4]) if len(sys.argv) > 4 else 300
tm = lambda f: float((re.findall(r'-([\d.]+)s\.png$', f) or ['0'])[0])
files = sorted(glob.glob(os.path.join(d, '*.png')), key=tm)
if not files: sys.exit('没有 PNG')
r0 = Image.open(files[0]); h = int(w * r0.height / r0.width)
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * (h + 26)), 'white'); dr = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    x, y = (i % cols) * w, (i // cols) * (h + 26)
    sheet.paste(Image.open(f).convert('RGB').resize((w, h)), (x, y + 26)); dr.text((x + 6, y + 6), os.path.basename(f), fill='black')
sheet.save(out); print(out, len(files))
