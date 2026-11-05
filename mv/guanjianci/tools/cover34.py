"""3:4 竖版封面（1080×1440）：原生 180×240 像素画 ×6 放大，再叠液态玻璃与花字标题。
  python3 tools/cover34.py   （需要 PIXMV_SKILL 指向 skill 目录；输出 cover/封面_3x4.png）"""
import os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.environ['PIXMV_SKILL']
sys.path.insert(0, os.path.join(SK, 'lib')); sys.path.insert(0, ROOT)
os.environ['PIXMV_PROJECT'] = ROOT
import numpy as np
from PIL import Image, ImageDraw
import mv as M
from pixlib import dither_grad, sky_colors, lerpc, hsh
import huazi as Z
from glass import glass, htext, tw, post, sdf_heart, ink

CW, CH, S = 180, 240, 6
t = 105.8
# ---------- 像素层 ----------
scene = Image.new('RGB', (320, 180))
M.avenue(scene, t, 0.42, 1700)
cv = Image.new('RGB', (CW, CH))
top, bot = sky_colors(0.42)
cv.paste(Image.fromarray(dither_grad(70, CW, lerpc(top, (40, 60, 140), 0.25), top, 6)), (0, 0))
cv.paste(scene.crop((70, 0, 250, 180)), (0, 60))
d = ImageDraw.Draw(cv)
ground = 60 + 104
R = lambda x, y, w, h, c: d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)
R(0, 240 - 16, CW, 16, lerpc((226, 212, 188), (200, 180, 150), 0.3))
for i in range(40):                      # 天上加飘落的银杏叶
    x, y = int(hsh(i, 91) * CW), int(hsh(i, 92) * 150)
    R(x, y, 3 if i % 2 else 2, 2 if i % 2 else 3, M.GOLD if i % 3 else M.GOLD_D)
M.CUR[0] = t
M.me(cv, 58, 192, 'idle', 'heart', 2, 1)
M.you(cv, 124, 192, 'idle', 'blush', 2, -1)
for x, w in ((58, 12), (124, 12)):
    a = np.asarray(cv).copy(); a[191:194, x - w:x + w] = (a[191:194, x - w:x + w] * 0.7).astype(np.uint8); cv = Image.fromarray(a)
M._leaf_px(cv, 152, 144, 'heart', 2)
M.nametag.__globals__['GL'].clear()
# 名字牌头像（像素），玻璃心之后画
from cast import ME_HEAD
from charkit import pixmap, put
dd = ImageDraw.Draw(cv)
dd.rectangle([82, 116, 98, 132], fill=(255, 246, 236))
put(cv, pixmap(ME_HEAD, M.ME_PAL), 90, 131, 1)

big = cv.resize((CW * S, CH * S), Image.NEAREST)
post(big, 0.22, 0.12)
# ---------- 液态玻璃层 ----------
glass(big, 540, 744, 210, 210, lambda px, py: sdf_heart(px, py, 330), t=1.0, tint=(255, 120, 150), tint_a=0.2, refr=1.3, mag=0.08)
glass(big, 540, 746, 66, 60, t=1.0, tint=(255, 236, 170), tint_a=0.2, refr=0.8, mag=0.02)
for (x, y, r) in ((150, 560, 34), (930, 520, 26), (880, 660, 18), (200, 700, 16), (980, 900, 30)):
    glass(big, x, y, r, r, t=1.0, refr=1.3, mag=0.18, shadow=0.08)
# 标题
L = Z.Line(-2, 99, '关键词', pal='yel', size=250, cx=540, cy=200, angle=-3, deco=('note', 'star'), stagger=0.0, pop=1.08)
# 玻璃底板托住标题
glass(big, 540, 210, 420, 150, t=1.2, tint_a=0.10, refr=1.0, mag=0.03)
L.draw(big, 3.0, 0.5)
# 搜索框：输入“你”
X, Y, HW = 540, 420, 400
lum = glass(big, X, Y, HW, 56, t=1.0, tint_a=0.16)
x0 = X - HW + 44
dd = ImageDraw.Draw(big)
dd.ellipse([x0, Y - 20, x0 + 30, Y + 10], outline=(110, 100, 140), width=5)
dd.line([(x0 + 26, Y + 6), (x0 + 40, Y + 20)], fill=(110, 100, 140), width=6)
htext(big, x0 + 66, Y + 2, '你', 50, M.SCARF, anchor='l')
dd.rounded_rectangle([x0 + 66 + tw('你', 50) + 6, Y - 26, x0 + 66 + tw('你', 50) + 10, Y + 26], 2, fill=(40, 120, 255))
res = '结果：全部相关'
htext(big, X + HW - 44 - tw(res, 38), Y + 2, res, 38, ink((110, 100, 130), lum), anchor='l')
# 原唱 / 标签
def chip(cx, cy, s, size, col, tint, ta):
    w = tw(s, size) + size * 1.3
    l = glass(big, cx, cy, w / 2, size * 0.78, t=1.0, tint=tint, tint_a=ta)
    htext(big, cx, cy + 2, s, size, ink(col, l))
chip(540, 1240, '原唱 · 林俊杰', 56, (40, 32, 56), (255, 255, 255), 0.18)
chip(540, 1336, '像素 MV · 液态玻璃版', 40, (222, 60, 84), (255, 180, 200), 0.2)
sg = Z.signature('@张景行')
glass(big, 540, 1440 - sg.height / 2 - 8, sg.width / 2 - 6, sg.height / 2 - 8, t=1.0, tint_a=0.14, shadow=0.1)
big.paste(sg, (540 - sg.width // 2, 1440 - sg.height - 8), sg)
out = os.path.join(ROOT, 'cover', '封面_3x4.png')
big.save(out)
print('✓', out, big.size)
