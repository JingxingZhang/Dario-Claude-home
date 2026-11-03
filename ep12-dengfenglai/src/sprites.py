"""像素精灵：楼船、小船、人物、旗、火、烟、芦苇船、祠堂。全部代码绘制。"""
import math
from functools import lru_cache
from PIL import Image, ImageDraw
from pixlib import *


def R(d, x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def paste(img, spr, x, y):
    img.paste(spr, (int(round(x)), int(round(y))), spr)


def scaled(spr, k):
    return spr.resize((spr.width * k, spr.height * k), Image.NEAREST)


# ---------- 陈友谅楼船：高数丈、丹漆、每船三重 ----------
@lru_cache(None)
def tower_ship(w=120, flags=True, burnt=False):
    hh = 78
    im = Image.new('RGBA', (w, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lac = (60, 40, 40) if burnt else LACQ
    lacd = (34, 24, 26) if burnt else RED_D
    lacl = (90, 60, 50) if burnt else RED_L
    base = hh - 16
    # 船身（梯形）
    for i in range(16):
        inset = int(i * 0.9)
        d.line([(inset, base + i), (w - 1 - inset - (i // 3), base + i)], fill=lac if i < 11 else lacd)
    R(d, 0, base, w, 2, GOLD_D)
    R(d, 2, base + 6, w - 6, 1, lacd)
    # 铁裹船舷：一排铆钉
    for x in range(4, w - 6, 6):
        d.point((x, base + 9), fill=GRAY)
    # 三重楼
    tiers = [(6, base - 15, w - 12), (14, base - 29, w - 28), (24, base - 41, w - 48)]
    for k, (x0, y0, ww) in enumerate(tiers):
        th = 14 if k < 2 else 12
        R(d, x0, y0, ww, th, lac)
        R(d, x0, y0, ww, 2, lacl)
        R(d, x0 - 2, y0 - 1, ww + 4, 2, GOLD_D)  # 檐
        for x in range(x0 + 3, x0 + ww - 4, 7):
            R(d, x, y0 + 5, 4, 5, INK)
            d.point((x + 1, y0 + 6), fill=(90, 60, 40) if not burnt else INK)
        for x in range(x0, x0 + ww, 3):
            d.point((x, y0 + th - 1), fill=lacd)
    # 桅杆与旗
    if flags:
        for mx in (w // 2 - 18, w // 2 + 14):
            R(d, mx, 0, 2, base - 40, BROWN_D)
    return im


def tower_flags(img, x, y, w, t, wind, scale=1, burnt=False):
    """楼船上的旗：x,y 为楼船左上角"""
    if burnt:
        return
    for mx in (w // 2 - 18, w // 2 + 14):
        flag(img, x + (mx + 1) * scale, y, 12 * scale, 7 * scale, wind, t + mx, (40, 30, 30), scale)


# ---------- 朱元璋这边的小船 ----------
@lru_cache(None)
def small_boat(w=34, mast=True, white_mast=False):
    hh = 34
    im = Image.new('RGBA', (w, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base = hh - 8
    for i in range(8):
        inset = i + (2 if i > 4 else 0)
        d.line([(inset, base + i), (w - 1 - inset // 2 - (3 if i < 2 else 0), base + i)], fill=BROWN if i < 5 else BROWN_D)
    d.line([(0, base), (w - 1, base)], fill=BROWN_L)
    R(d, w - 4, base - 3, 3, 3, BROWN)  # 船头
    if mast:
        R(d, w // 2, 2, 1, base - 2, WHITE if white_mast else BROWN_D)
    return im


def flag(img, x, y, fw, fh, wind, t, col, scale=1):
    """旗：wind=0 时垂着，wind=1 时向西（左）展开飘动。x,y 为杆顶"""
    d = ImageDraw.Draw(img)
    wind = clamp(wind)
    if wind < 0.05:
        # 垂旗：贴着旗杆垂下，几道褶
        R(d, x - 2 * scale, y + 1, 2 * scale, fh + 3 * scale, col)
        R(d, x - 3 * scale, y + 1 + scale * 2, scale, fh, lerpc(col, INK, 0.35))
        return
    L = int(fw * (0.25 + 0.75 * wind))
    for i in range(L):
        k = i / max(1, L)
        dy = math.sin(i * 0.55 / scale - t * 9) * (1 + 1.5 * k) * scale * wind
        droop = (1 - wind) * k * fh * 0.8
        c = col if (i // scale) % 4 else lerpc(col, INK, 0.25)
        R(d, x - i - 1, int(y + 1 + dy + droop), 1, int(fh * (1 - 0.25 * k)), c)


def person(img, x, y, kind='zhu', pose=0, t=0.0, face=1, scale=1, dark=False):
    """小人（8×14）；x,y 为脚底中点"""
    pal = {
        'zhu': ((150, 30, 40), (90, 20, 30), GOLD),       # 主将：朱红披风、金盔
        'soldier': ((90, 92, 110), (60, 60, 76), GRAY),
        'ding': (BLUE, BLUE_D, (220, 220, 230)),          # 丁普郎：蓝甲
        'enemy': ((150, 60, 50), (100, 40, 40), (60, 50, 50)),
        'chang': ((70, 110, 70), (40, 70, 40), GRAY),     # 常遇春
        'zhang': ((60, 50, 60), (34, 28, 40), (150, 140, 120)),  # 张定边
    }[kind]
    body, bd, helm = pal
    if dark:
        body = bd = helm = INK
    im = Image.new('RGBA', (12, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sk = INK if dark else SKIN
    # 头盔 + 脸
    R(d, 4, 0, 4, 2, helm)
    R(d, 3, 2, 6, 1, helm)
    R(d, 4, 3, 4, 3, sk)
    d.point((6 if face > 0 else 5, 4), fill=INK)
    # 身体
    crouch = 2 if pose == 2 else 0
    R(d, 3, 6 + crouch, 6, 5, body)
    R(d, 3, 10 + crouch, 6, 1, bd)
    # 腿
    if pose == 1:  # 走/冲
        ph = int(t * 10) % 2
        R(d, 3 + ph, 11 + crouch, 2, 5 - crouch, bd)
        R(d, 7 - ph, 11 + crouch, 2, 5 - crouch, bd)
    else:
        R(d, 4, 11 + crouch, 2, 5 - crouch, bd)
        R(d, 7, 11 + crouch, 2, 5 - crouch, bd)
    if crouch:
        im2 = Image.new('RGBA', (12, 16), (0, 0, 0, 0))
        im2.paste(im.crop((0, 0, 12, 14)), (0, 2))
        im = im2
    if face < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1:
        im = scaled(im, scale)
    paste(img, im, x - 6 * scale, y - 16 * scale)


def blade(img, x, y, ang, ln=7, col=(220, 224, 236)):
    d = ImageDraw.Draw(img)
    d.line([(x, y), (x + math.cos(ang) * ln, y - math.sin(ang) * ln)], fill=col)


def bubble(img, x, y, s, col=INK, bg=WHITE):
    """对话气泡：x,y 为尾巴尖"""
    w = text_w(s) + 6
    d = ImageDraw.Draw(img)
    bx, by = int(x - w // 2), int(y - 19)
    R(d, bx + 1, by, w - 2, 15, bg)
    R(d, bx, by + 1, w, 13, bg)
    R(d, int(x) - 1, by + 15, 3, 2, bg)
    d.point((int(x), by + 17), fill=bg)
    draw_text(img, bx + 3, by + 2, s, col)


def name_tag(img, x, y, s, col=WHITE, bg=INK):
    w = text_w(s) + 4
    d = ImageDraw.Draw(img)
    R(d, int(x - w // 2), int(y), w, 14, bg)
    draw_text(img, int(x - w // 2) + 2, int(y) + 1, s, col)


def hp_bar(img, x, y, v, w=30):
    d = ImageDraw.Draw(img)
    draw_text(img, x - 13, y - 3, 'HP', WHITE, shadow=INK)
    R(d, x, y, w + 2, 6, INK)
    col = (90, 220, 110) if v > 0.5 else GOLD if v > 0.2 else RED
    R(d, x + 1, y + 1, int(w * clamp(v)), 4, col)


# ---------- 火与烟 ----------
FIRE = [YEL, (255, 196, 60), ORANGE, (232, 80, 40), (170, 40, 40)]


def fire(img, x, y, w, hmax, t, seed=0, k=1.0):
    """一团火：x 左、y 底"""
    d = ImageDraw.Draw(img)
    for i in range(w):
        n = hsh(seed, i, int(t * 14))
        h = int(hmax * k * (0.35 + 0.65 * n) * (0.6 + 0.4 * math.sin(i / max(1, w) * math.pi)))
        for j in range(h):
            q = j / max(1, h)
            c = FIRE[min(4, int(q * 4.6 + hsh(seed, i, j, int(t * 10)) * 0.8))]
            d.point((x + i, y - j), fill=c)
    # 火星
    for i in range(int(6 * k)):
        ph = (t * 0.9 + hsh(seed, i)) % 1
        px = x + hsh(seed, i, 2) * w + math.sin(t * 3 + i) * 3
        py = y - hmax * k - ph * 30
        if hsh(seed, i, int(t * 8)) > 0.3:
            d.point((int(px), int(py)), fill=YEL if ph < 0.5 else ORANGE)


def smoke(img, x, y, t, seed=0, k=1.0, top=0, drift=-0.4):
    d = ImageDraw.Draw(img)
    n = 9
    for i in range(n):
        ph = (t * 0.22 + i / n + hsh(seed, i) * 0.1) % 1
        yy = y - ph * (y - top)
        xx = x + drift * ph * 60 + math.sin(t + i) * 2
        r = int((3 + ph * 9) * k)
        c = lerpc(SMOKE, SMOKE_L, hsh(seed, i, 7)) if ph < 0.75 else lerpc(SMOKE_L, (170, 160, 170), (ph - 0.75) * 4)
        disc(d, int(xx), int(yy), r, c)


def explosion(img, x, y, p, seed=0):
    """p 0..1"""
    if p <= 0 or p >= 1:
        return
    d = ImageDraw.Draw(img)
    r = int(4 + p * 18)
    disc(d, x, y, r, lerpc(YEL, (200, 60, 40), p))
    if p < 0.6:
        disc(d, x, y, int(r * 0.6), WHITE)
    for i in range(10):
        a = hsh(seed, i) * 6.283
        rr = r + 4 + p * 10
        d.point((int(x + math.cos(a) * rr), int(y + math.sin(a) * rr)), fill=ORANGE)


# ---------- 火船：芦苇 + 火药 ----------
def fire_boat(img, t, x, y, wind=1.0, num=None, lit=False):
    """x,y 为船身左上角（小船坐标系）"""
    b = small_boat(30, mast=True)
    paste(img, b, x, y)
    d = ImageDraw.Draw(img)
    base = y + 26
    # 芦苇捆
    for i in range(4):
        bx = x + 4 + i * 5
        R(d, bx, base - 7, 4, 7, REED)
        R(d, bx, base - 5, 4, 1, REED_D)
        for j in range(3):
            d.point((bx + j, base - 8 - (j % 2)), fill=REED)
    # 火药桶
    R(d, x + 22, base - 5, 4, 5, INK2)
    R(d, x + 22, base - 3, 4, 1, GRAY_D)
    # 帆（顺风鼓起）
    mx = x + 15
    sw = int(3 + 8 * wind)
    for j in range(13):
        bulge = int(math.sin(j / 12 * math.pi) * 3 * wind)
        R(d, mx - sw - bulge, y + 5 + j, sw + bulge, 1, PAPER if j % 4 else (210, 200, 180))
    if num is not None:
        draw_text(img, x + 11, y - 12, str(num), GOLD, outline=INK)
    if lit:
        fire(img, x + 3, base - 4, 22, 16, t, seed=x)


# ---------- 祠堂 ----------
def shrine(img, x, y, reveal=1.0, scale=1):
    """x 中心、y 底；reveal 自下而上搭起来"""
    w, h = 70, 44
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # 台基
    R(d, 4, 38, 62, 6, (150, 140, 130))
    R(d, 2, 42, 66, 2, (110, 100, 96))
    # 柱、墙
    R(d, 12, 20, 46, 18, (150, 40, 40))
    for cx in (12, 22, 46, 56):
        R(d, cx, 20, 3, 18, (110, 26, 30))
    R(d, 29, 24, 12, 14, INK)  # 门
    R(d, 30, 25, 10, 1, GOLD_D)
    # 屋顶（反宇）
    for i in range(12):
        x0 = 4 + i // 2 - (3 if i > 9 else 0)
        d.line([(x0, 8 + i), (w - 1 - x0, 8 + i)], fill=(52, 60, 70) if i % 3 else (80, 90, 100))
    R(d, 0, 18, 6, 2, (52, 60, 70))
    R(d, w - 6, 18, 6, 2, (52, 60, 70))
    d.point((0, 17), fill=(52, 60, 70)); d.point((w - 1, 17), fill=(52, 60, 70))
    R(d, 20, 6, 30, 2, (80, 90, 100))
    R(d, 31, 13, 8, 5, GOLD)  # 匾
    if reveal < 1:
        cut = int(h * (1 - reveal))
        R(d, 0, 0, w, cut, (0, 0, 0, 0))
    if scale != 1:
        im = scaled(im, scale)
    paste(img, im, x - w * scale // 2, y - h * scale)


def hill(img, cx, y, w, h, col, col2):
    d = ImageDraw.Draw(img)
    for i in range(h):
        k = i / h
        half = int(w / 2 * math.sqrt(k) * (1 + 0.04 * math.sin(i)))
        d.line([(cx - half, y - h + i), (cx + half, y - h + i)], fill=col if (i // 3) % 2 else col2)


def tablets(img, x, y, n, first_hi=True):
    """牌位一排：x 起点、y 底"""
    d = ImageDraw.Draw(img)
    for i in range(n):
        tx = x + i * 13
        hi = (i == 0 and first_hi)
        h = 40 if hi else 30
        R(d, tx, y - h, 11, h, (120, 30, 36) if hi else (92, 34, 38))
        R(d, tx - 1, y - h - 2, 13, 3, GOLD if hi else GOLD_D)
        R(d, tx - 1, y - 3, 13, 3, GOLD_D)
