"""封面：3:4（180×240 → 1080×1440）、16:9（第 0 帧）、知识卡单帧。"""
import os
from PIL import Image, ImageDraw
import mv
from pixlib import *
from sprites import *

OUT = os.path.join(ROOT, 'cover'); os.makedirs(OUT, exist_ok=True)
CW, CH = 180, 240
t = 176.0
img = Image.new('RGB', (CW, CH), INK)
draw_sky(img, 0.85, 150, t=t)
draw_water(img, t, 0.85, 150, red=0.7, choppy=0.8, y1=CH)
for i in range(2):
    x, y = 60 + i * 60, 90 + i * 6
    paste(img, tower_ship(100, True, True), x, y)
    fire(img, x + 8, y + 58, 84, 40, t, seed=i + 3)
    smoke(img, x + 50, y + 10, t, seed=i + 3, k=1.1, top=0)
mv.wind_streaks(img, t, 0.6)
mv.zhu_boat(img, t, 6, 150, 2, wind=1.0, face=1)
d = ImageDraw.Draw(img)
# 红签
R(d, 6, 6, text_w('大明开局 · 第12集') + 8, 16, RED)
draw_text(img, 10, 8, '大明开局 · 第12集', PAPER)
# 钩子两行
draw_text(img, 10, 38, '风来了', WHITE, scale=2, outline=INK, shadow=INK)
draw_text(img, 10, 66, '他没等到', GOLD, scale=2, outline=INK, shadow=INK)
# 歌名
draw_text(img, CW - 10 - text_w('等风来', 3), 92, '等风来', RED_L, scale=3, outline=INK, shadow=INK)
draw_text(img, CW - 10 - text_w('1363 · 鄱阳湖'), 132, '1363 · 鄱阳湖', PAPER, outline=INK)
# 署名（右上角）
x = CW - 6 - text_w('@张景行')
draw_text(img, x, 4, '@张景行', WHITE, outline=INK)
R(d, CW - 6 - 28, 18, 28, 13, RED)
draw_text(img, CW - 6 - 26, 18, '景行', PAPER)
img.resize((CW * 6, CH * 6), Image.NEAREST).save(os.path.join(OUT, 'cover-3x4.png'))
mv.frame(0).resize((1920, 1080), Image.NEAREST).save(os.path.join(OUT, 'cover-16x9.png'))
mv.frame(100.0).resize((1920, 1080), Image.NEAREST).save(os.path.join(OUT, '知识卡.png'))
print('ok')
