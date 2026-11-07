import os, sys
os.environ["CHALK_W"] = "1080"; os.environ["CHALK_H"] = "2200"
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import render as R

FONTS = [("演示夏行楷（当前）·行楷", "fonts/YanShiXiaXingKai.ttf"),
         ("鸿雷行书简体·行书", "fonts/cands/鸿雷行书简体.otf"),
         ("云峰静龙行书·行书", "fonts/cands/云峰静龙行书.ttf"),
         ("王强书法体·行楷", "fonts/cands/王强书法体.ttf"),
         ("沐瑶软笔手写体·软笔", "fonts/cands/沐瑶软笔手写体.ttf"),
         ("清松手写体7·飘逸·行楷", "fonts/cands/清松手寫體7：飄逸.ttf"),
         ("演示秋鸿楷·楷偏行", "fonts/cands/演示秋鸿楷.ttf"),
         ("演示春风楷·楷偏行", "fonts/cands/演示春风楷.ttf"),
         ("钟齐志莽行书·行书", "fonts/ZhiMangXing-Regular.ttf"),
         ("龙藏体·行书", "fonts/LongCang-Regular.ttf")]
SAMPLE = "为什么天空是蓝色？"
SAMPLE2 = "波长越短，散射越强"
need = set("".join(open("lines.txt", encoding="utf-8").read().split()) +
           "为什么天空是蓝色太阳光七色混合蓝光波长短红光散射强度倍白天日落光路短四处满天沿途散尽夕阳橙红波长越短散射越强nm0123456789")
need -= set("，。；：？！、 ")

def ink(fn, size=100):
    f = ImageFont.truetype(fn, size); hs, ws = [], []
    for c in "天光为么空":
        im = Image.new("L", (300, 300)); ImageDraw.Draw(im).text((50, 150), c, font=f, fill=255, anchor="lm")
        ys, xs = np.nonzero(np.asarray(im) > 40); hs.append(np.ptp(ys) if len(ys) else 0); ws.append(np.ptp(xs) if len(xs) else 0)
    return np.mean(hs) / size, np.mean(ws) / size, f.getlength("蓝") / size

R.BOARD = R.make_board()
img = R.BOARD.copy()
label = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 30)
rows = []
ROW = 205
for k, (name, fn) in enumerate(FONTS):
    cm = TTFont(fn, fontNumber=0).getBestCmap()
    miss = sorted(c for c in need if ord(c) not in cm)
    hr, wr, adv = ink(fn)
    R.FONT = os.path.join(R.HERE, fn); R.CMAP = set(cm)
    R.FONT_SCALE = 0.80 / hr                       # normalise ink height
    R.TRACK = min(1.0, (wr * 1.30) / adv)
    y = 150 + k * ROW
    for txt, x, sz in ((SAMPLE, 70, 74), (SAMPLE2, 70, 60)):
        e = R.text_element(txt, x, y + (0 if sz == 74 else 92), sz, R.WHITE if sz == 74 else R.YELLOW, 0, 1)
        h, w = e.alpha.shape
        w = min(w, R.W - e.x0); a = e.alpha[:, :w]
        sl = img[e.y0:e.y0 + h, e.x0:e.x0 + w]; sl += a[..., None] * (e.color - sl)
    rows.append((k, name, y, miss))
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(im)
for k, name, y, miss in rows:
    tag = f"{k + 1}. {name}"
    d.text((70, y - 70), tag, font=label, fill=(170, 210, 190))
    if miss: d.text((R.W - 60, y - 70), "缺字", font=label, fill=(255, 150, 140), anchor="ra")
    d.line([(60, y + 140), (R.W - 60, y + 140)], fill=(80, 100, 90), width=1)
    print(name, "missing", len(miss), "".join(miss[:20]))
im.save(sys.argv[1])
