#!/usr/bin/env python3
"""导出角色设定图（分镜检查点和分镜一起发给用户）：调用项目 mv.py 里的 CAST_SHEET(img, t)。
  python3 cast_sheet.py 项目目录 输出.png [--gif]   （--gif 额外导一个 2 秒循环小动图，看动作和表情变化）"""
import argparse
from PIL import Image
from _load import load

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('out'); ap.add_argument('--gif', action='store_true')
A = ap.parse_args()
mv = load(A.project)
if not hasattr(mv, 'CAST_SHEET'):
    raise SystemExit('✗ mv.py 里还没有 CAST_SHEET(img, t)：先设计角色')


def one(t):
    img = Image.new('RGB', (320, 180), (236, 232, 244))
    mv.CAST_SHEET(img, t)
    return img.resize((1920, 1080), Image.NEAREST)


one(0.5).save(A.out)
if A.gif:
    fr = [one(i / 10).resize((960, 540), Image.NEAREST).convert('P', palette=Image.ADAPTIVE, colors=128) for i in range(20)]
    g = A.out.rsplit('.', 1)[0] + '.gif'
    fr[0].save(g, save_all=True, append_images=fr[1:], duration=100, loop=0)
    print('✓', g)
print('✓', A.out)
