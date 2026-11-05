"""通用场景背景：霓虹城市街（可卷动、湿地面倒影）、雨、窗边室内。v2=True 为第二套配色（紫红夜）。
需要别的场景（海边、教室、山、天台……）时，按同样写法在项目里新写，或参考 props2 里的 mountains / wave_sea / runway / interrogation。"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *
from chars import R, NEON_P, NEON_B, NEON_Y, K


@lru_cache(None)
def city_layers(v2=False, neon=None):
    """neon：招牌文字和颜色，如 (('LOVE', NEON_P), ('HI', NEON_B))，按歌词换成贴题的字"""
    """返回 (天空, 远楼, 近楼) 三层，宽 640 便于横向卷动"""
    sky = Image.new('RGB', (W, H))
    top, bot = ((44, 10, 64), (170, 50, 120)) if v2 else ((16, 14, 44), (74, 44, 112))
    sky.paste(Image.fromarray(dither_grad(H, W, top, bot, levels=8)), (0, 0))
    d = ImageDraw.Draw(sky)
    for i in range(40):
        if hsh(i, 1) < 0.7:
            d.point((int(hsh(i, 2) * W), int(hsh(i, 3) * 70)), fill=(200, 200, 230))
    disc(d, 262, 30, 10, (250, 240, 210) if not v2 else (255, 210, 230))
    disc(d, 258, 27, 9, top)
    far = Image.new('RGBA', (640, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(far)
    x = 0
    i = 0
    while x < 640:
        w = 14 + int(hsh(i, 5) * 20)
        h = 40 + int(hsh(i, 6) * 60)
        col = (40, 30, 80) if not v2 else (70, 24, 90)
        R(d, x, 130 - h, w, h + 10, col)
        for wy in range(130 - h + 4, 128, 6):
            for wx in range(x + 2, x + w - 2, 4):
                if hsh(i, wx, wy) < 0.22:
                    R(d, wx, wy, 2, 3, (250, 220, 120) if hsh(wx, wy) < 0.7 else (120, 230, 250))
        x += w + 1
        i += 1
    near = Image.new('RGBA', (640, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(near)
    x = -10
    i = 0
    neon = list(neon) if neon else [('LOVE', NEON_P), ('HI', NEON_B), ('BAR', NEON_Y), ('24H', NEON_B), ('CAFE', NEON_P)]
    while x < 640:
        w = 40 + int(hsh(i, 7) * 40)
        h = 70 + int(hsh(i, 8) * 50)
        col = (26, 20, 50) if not v2 else (44, 14, 60)
        R(d, x, 134 - h, w, h + 6, col)
        R(d, x, 134 - h, w, 2, (60, 50, 100))
        for wy in range(134 - h + 8, 128, 9):
            for wx in range(x + 4, x + w - 6, 8):
                if hsh(i, wx, wy, 3) < 0.35:
                    R(d, wx, wy, 4, 4, (255, 200, 110))
        if i % 2 == 0:
            s, c = neon[(i // 2) % len(neon)]
            tw = text_w(s)
            nx, ny = x + w // 2 - tw // 2, 134 - h + 14
            R(d, nx - 3, ny - 2, tw + 6, 15, (20, 14, 30))
            near.paste(Image.new('RGBA', (1, 1)), (0, 0))
            tmp = Image.new('RGB', (tw + 6, 15), (20, 14, 30))
            draw_text(tmp, 3, 1, s, c)
            near.paste(tmp, (nx - 3, ny - 2))
        x += w + 2
        i += 1
    return sky, far, near


def street(img, t, v2=False, scroll=0.0, ground=128, rain_k=0.8, neon=None):
    sky, far, near = city_layers(v2, tuple(neon) if neon else None)
    img.paste(sky, (0, 0))
    ofs1 = int(scroll * 0.3) % 320
    ofs2 = int(scroll * 0.7) % 320
    img.paste(far.crop((ofs1, 0, ofs1 + W, H)), (0, -2), far.crop((ofs1, 0, ofs1 + W, H)))
    nc = near.crop((ofs2, 0, ofs2 + W, H))
    img.paste(nc, (0, -6), nc)
    d = ImageDraw.Draw(img)
    # 霓虹闪
    if (int(t * 3) % 7) == 0:
        pass
    # 湿漉漉的街面 + 倒影
    R(d, 0, ground, W, H - ground, (24, 20, 40) if not v2 else (36, 14, 50))
    R(d, 0, ground, W, 2, (70, 60, 110))
    a = np.array(img)
    refl = a[ground - 40:ground][::-1]
    n = min(len(refl), H - ground - 2)
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:n, :W]
    seg_ = a[ground + 2:ground + 2 + n].astype(float)
    mix = (refl[:n].astype(float) * 0.45 + seg_ * 0.55)
    keep = bay < 0.6
    seg_[keep] = mix[keep]
    a[ground + 2:ground + 2 + n] = seg_.astype(np.uint8)
    img.paste(Image.fromarray(a), (0, 0))
    if rain_k > 0:
        rain(img, t, rain_k, ground)


def rain(img, t, k, ground=H):
    d = ImageDraw.Draw(img)
    n = int(160 * k)
    for i in range(n):
        sp = 260 + hsh(i, 2) * 120
        x = (hsh(i, 1) * (W + 60) - t * 60) % (W + 60) - 30
        y = (hsh(i, 3) * H + t * sp) % (H + 20) - 10
        d.line([(int(x), int(y)), (int(x - 2), int(y + 6))], fill=(160, 180, 230) if i % 3 else (200, 214, 250))
        if i % 5 == 0:
            ph = (t * 2 + hsh(i, 9)) % 1
            if ph < 0.25:
                sx = int(hsh(i, 8) * W)
                sy = ground + 3 + int(hsh(i, 7) * (H - ground - 6)) if ground < H else int(H - 4)
                r = int(1 + ph * 12)
                d.point((sx - r, sy), fill=(150, 170, 220)); d.point((sx + r, sy), fill=(150, 170, 220))


def room(img, t, v2=False, fog=0.0, rain_k=1.0):
    """室内窗边（向原视频的雨夜窗景致意）"""
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (44, 26, 34))
    for y in range(0, H, 4):
        R(d, 0, y, W, 1, (50, 30, 38))
    # 窗外城市
    win = Image.new('RGB', (W, H))
    street(win, t, v2, scroll=0, ground=150, rain_k=0)
    img.paste(win.crop((30, 16, 290, 128)), (30, 16))
    # 玻璃上的雨痕
    for i in range(70):
        x = 30 + int(hsh(i, 4) * 260)
        L = 3 + int(hsh(i, 5) * 8)
        y = 16 + (hsh(i, 6) * 112 + t * (8 + hsh(i, 7) * 30)) % 112
        d.line([(x, int(y)), (x, int(y) + L)], fill=(150, 170, 210))
        d.point((x, int(y) + L + 1), fill=(220, 230, 255))
    if fog > 0:
        a = np.array(img).astype(float)
        sub = a[16:128, 30:290]
        bay = np.tile(BAYER, (40, 80))[:112, :260]
        m = bay < fog * 0.6
        sub[m] = sub[m] * 0.5 + np.array([200, 205, 220]) * 0.5
        a[16:128, 30:290] = sub
        img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    # 窗框
    for x in (28, 158, 290):
        R(d, x, 14, 4, 116, (76, 46, 36))
    R(d, 28, 14, 266, 4, (76, 46, 36))
    R(d, 28, 70, 266, 3, (76, 46, 36))
    # 窗台
    R(d, 0, 128, W, 8, (96, 58, 40))
    R(d, 0, 128, W, 1, (140, 90, 60))
    R(d, 0, 136, W, H - 136, (36, 20, 28))
    # 蜡烛
    R(d, 64, 118, 5, 10, (250, 240, 220))
    fl = hsh(int(t * 12), 3)
    R(d, 65, 113 - int(fl * 2), 3, 5, (255, 200, 80))
    d.point((66, 112 - int(fl * 2)), fill=(255, 250, 200))
    R(d, 240, 120, 10, 8, (200, 90, 80)); R(d, 250, 122, 2, 4, (200, 90, 80))  # 杯子
    rain(img, t, 0.0)


