"""画风迭代（PIXMV_STYLE>=1）的背景：分层、柔和、有光影。由 mv.py 在 STYLE>=1 时覆盖原来的场景函数。
设计原则（参照 Apple 的视觉语言）：低饱和、干净的大色块，柔和渐变，靠层次和光影表现空间，不用死黑描边。"""
import math
import numpy as np
from PIL import Image, ImageDraw
from pixlib import W, H, BAYER, dither_grad, lerpc, hsh, disc, sun_pos, clamp, lerp
from chars import R

WHITE = (250, 248, 240)


def grad3(h, w, c0, c1, c2, mid=0.55, levels=16):
    """三段竖向渐变 + Bayer 抖动（16 档，比原来细腻）"""
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    q = np.floor(v * (levels - 1) + bay - 0.5 + 0.5).clip(0, levels - 1) / (levels - 1)
    c0, c1, c2 = (np.array(c, float) for c in (c0, c1, c2))
    k1 = np.clip(q / mid, 0, 1)[..., None]
    k2 = np.clip((q - mid) / (1 - mid), 0, 1)[..., None]
    out = np.where((q < mid)[..., None], c0 + (c1 - c0) * k1, c1 + (c2 - c1) * k2)
    return out.astype(np.uint8)


def glow_np(img, cx, cy, r, col, k=0.35, add=False):
    a = np.asarray(img).astype(float)
    hh, ww = a.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww]
    m = np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) ** 1.6 * k
    b = np.tile(BAYER, (hh // 4 + 1, ww // 4 + 1))[:hh, :ww]
    m = np.floor(m * 8 + b - 0.5).clip(0, 8) / 8
    a = a + (np.array(col, float) - a) * m[..., None] if not add else a + np.array(col, float) * m[..., None]
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)))


SKY = {
    'day': ((92, 146, 220), (152, 196, 238), (238, 228, 214)),
    'gold': ((104, 132, 206), (196, 184, 214), (252, 212, 166)),
    'dawn': ((118, 138, 204), (196, 186, 226), (250, 214, 200)),
    'winter': ((146, 168, 204), (196, 210, 232), (236, 240, 248)),
    'night': ((18, 22, 50), (34, 40, 80), (70, 72, 120)),
    'wnight': ((20, 26, 54), (40, 48, 90), (82, 92, 136)),
}


def sky_key(season, tod):
    if tod > 0.9:
        return 'wnight' if season == 'winter' else 'night'
    if season == 'winter':
        return 'winter'
    if tod < 0.2:
        return 'dawn'
    if tod > 0.55 or season == 'year2':
        return 'gold'
    return 'day'


def cloud(img, cx, cy, s, base, shade, light):
    d = ImageDraw.Draw(img)
    blobs = [(-10, 2, 6), (-3, -2, 8), (6, 0, 7), (13, 3, 5), (0, 4, 7)]
    for ox, oy, r in blobs:
        disc(d, int(cx + ox * s), int(cy + oy * s + 2), int(r * s), shade)
    for ox, oy, r in blobs:
        disc(d, int(cx + ox * s), int(cy + oy * s), int(r * s) - 1, base)
    for ox, oy, r in blobs[:3]:
        disc(d, int(cx + ox * s - 1), int(cy + oy * s - 2), max(1, int(r * s) - 4), light)


def sky(img, t, season, tod, hz):
    key = sky_key(season, tod)
    c0, c1, c2 = SKY[key]
    img.paste(Image.fromarray(grad3(hz, W, c0, c1, c2)), (0, 0))
    d = ImageDraw.Draw(img)
    night = key in ('night', 'wnight')
    if night:
        for i in range(70):
            x, y = int(hsh(i, 1) * W), int(hsh(i, 2) * hz * 0.75)
            tw_ = hsh(i, int(t * 2)) > 0.2
            d.point((x, y), fill=(230, 232, 255) if tw_ else (140, 150, 200))
            if hsh(i, 5) > 0.93:
                d.point((x + 1, y), fill=(180, 190, 240)); d.point((x - 1, y), fill=(180, 190, 240))
        if season != 'winter':
            glow_np(img, 270, 26, 30, (220, 220, 255), 0.25)
            disc(d, 270, 26, 7, (248, 244, 222)); disc(d, 273, 24, 6, c0)
        return
    if key != 'winter':
        sx, sy = sun_pos(tod, hz)
        glow_np(img, sx, sy, 70, lerpc(c2, (255, 240, 200), 0.6), 0.45)
        disc(d, sx, sy, 8, (255, 246, 220)); disc(d, sx, sy, 6, (255, 252, 240))
    base = lerpc(c2, (255, 255, 255), 0.75)
    shade = lerpc(c1, c2, 0.5)
    light = (255, 255, 255)
    for i in range(3):
        cx = (hsh(i, 41) * 360 + t * (2 + i)) % 380 - 30
        cloud(img, cx, 14 + i * 13, 0.8 + 0.25 * i, base, shade, light)


def city(img, hz, season, key):
    """远景：一排低矮的楼，被空气透视冲淡"""
    d = ImageDraw.Draw(img)
    c0, c1, c2 = SKY[key]
    col = lerpc(c2, c0, 0.28)
    win = (255, 226, 160) if key in ('night', 'wnight', 'gold') else lerpc(col, (255, 255, 255), 0.25)
    x = -4
    i = 0
    while x < W:
        w = 14 + int(hsh(i, 71) * 20)
        h = 10 + int(hsh(i, 72) * 22)
        R(d, x, hz - h, w, h, col)
        R(d, x, hz - h, w, 1, lerpc(col, (255, 255, 255), 0.15))
        for yy in range(hz - h + 3, hz - 3, 4):
            for xx in range(x + 2, x + w - 2, 4):
                if hsh(xx, yy, i) > 0.55:
                    d.point((xx, yy), fill=win)
        x += w + 1
        i += 1


LEAF_TONES = {
    'autumn': ((190, 124, 38), (226, 160, 46), (247, 201, 72), (255, 230, 136)),
    'year2': ((196, 112, 40), (232, 152, 52), (250, 190, 70), (255, 222, 130)),
    'summer': ((60, 112, 70), (86, 146, 84), (122, 178, 98), (176, 214, 132)),
}


def crown(img, x, cy, season, k=1.0, seed=0):
    d = ImageDraw.Draw(img)
    deep, sh, base, li = LEAF_TONES.get(season, LEAF_TONES['autumn'])
    pts = []
    for i in range(13):
        a = hsh(i, seed, 3) * 2 * math.pi
        rr = hsh(i, seed, 4) ** 0.6 * 16
        pts.append((x + math.cos(a) * rr * 1.25, cy + math.sin(a) * rr * 0.85, 6 + hsh(i, seed, 5) * 5))
    pts.sort(key=lambda p: p[1])
    for px, py, r in pts:
        disc(d, int(px + 2), int(py + 3), max(1, int(r * k)), deep)
    for px, py, r in pts:
        disc(d, int(px + 1), int(py + 1), max(1, int(r * k) - 1), sh)
    for px, py, r in pts:
        disc(d, int(px), int(py), max(1, int(r * k) - 2), base)
    for px, py, r in pts:
        if px < x + 4 and py < cy + 4:
            disc(d, int(px - 2), int(py - 2), max(1, int(r * k) - 5), li)
    for i in range(int(26 * k)):
        a = hsh(i, seed, 7) * 2 * math.pi
        rr = 22 * k
        fx, fy = x + math.cos(a) * rr * 1.1, cy + math.sin(a) * rr * 0.8
        d.point((int(fx), int(fy)), fill=base if i % 3 else li)
    for i in range(int(8 * k)):
        d.point((int(x - 10 + hsh(i, seed, 9) * 16), int(cy - 10 + hsh(i, seed, 10) * 12)), fill=(255, 246, 210))


def trunk(img, x, ground, th=36):
    d = ImageDraw.Draw(img)
    R(d, x - 3, ground - th, 7, th, (122, 90, 72))
    R(d, x - 3, ground - th, 2, th, (156, 120, 96))
    R(d, x + 2, ground - th, 2, th, (96, 70, 58))
    R(d, x - 5, ground - 3, 11, 3, (110, 80, 64))
    for i in range(5):
        d.point((x - 1 + (i % 2), ground - th + 6 + i * 6), fill=(100, 74, 60))


def branches(img, x, ground, th, season):
    d = ImageDraw.Draw(img)
    snow = season == 'winter'
    for a_, ln in ((-0.9, 22), (-0.45, 27), (0.0, 20), (0.35, 25), (0.85, 21)):
        ex, ey = x + int(math.sin(a_) * ln), ground - th - int(math.cos(a_) * ln)
        d.line([(x, ground - th + 4), (ex, ey)], fill=(104, 76, 62), width=2)
        for j in (0.5, 0.75):
            mx, my = x + (ex - x) * j, ground - th + 4 + (ey - ground + th - 4) * j
            d.line([(mx, my), (mx + (6 if a_ > 0 else -6), my - 5)], fill=(116, 88, 72))
        if snow:
            d.line([(ex - 3, ey - 1), (ex + 2, ey - 1)], fill=(250, 252, 255))
            d.point((ex - 1, ey - 2), fill=(250, 252, 255))
        if season == 'spring':
            for j in range(4):
                d.point((ex + j - 2, ey + (j % 2)), fill=(156, 214, 120) if j % 2 else (200, 236, 160))


def tree(img, x, ground, season='autumn', k=1.0, snow=0.0):
    th = 36
    a = np.asarray(img).copy()          # 地面上的树影（午后光从左上来，影子落向右下）
    y0, y1 = ground - 1, min(H, ground + 4)
    x0, x1 = max(0, x - 6), min(W, x + 30)
    if x1 > x0 and season not in ('spring',):
        a[y0:y1, x0:x1] = (a[y0:y1, x0:x1] * 0.86).astype(np.uint8)
        img.paste(Image.fromarray(a))
    trunk(img, x, ground, th)
    if season in ('winter', 'spring') or k < 0.6:
        branches(img, x, ground, th, season)
        if season == 'winter':
            d = ImageDraw.Draw(img)
            R(d, x - 4, ground - th - 1, 9, 2, (250, 252, 255))
        if season in ('winter', 'spring'):
            return
    crown(img, x, ground - th - 12, 'year2' if season == 'year2' else ('summer' if season == 'summer' else 'autumn'), k, seed=x // 7)


def ground_fill(img, ground, season, scroll, tod):
    d = ImageDraw.Draw(img)
    winter = season == 'winter'
    night = tod > 0.9
    if winter:
        top, bot = ((214, 224, 240), (240, 244, 252)) if not night else ((96, 106, 150), (130, 140, 180))
    elif season == 'year2':
        top, bot = (226, 204, 172), (240, 224, 198)
    else:
        top, bot = (220, 204, 178), (238, 226, 206)
    img.paste(Image.fromarray(grad3(H - ground, W, top, lerpc(top, bot, 0.5), bot, 0.4, 10)), (0, ground))
    R(d, 0, ground, W, 1, lerpc(top, (110, 96, 90), 0.35))
    R(d, 0, ground + 1, W, 1, lerpc(top, (255, 255, 255), 0.35))
    for j, y in enumerate((ground + 9, ground + 22, ground + 42)):      # 地砖的透视接缝
        d.line([(0, y), (W, y)], fill=lerpc(top, (150, 130, 120), 0.18 + 0.04 * j))
        step = 18 + j * 12
        off = int(scroll * (0.6 + j * 0.3)) % step
        for x in range(-off, W, step):
            d.line([(x, y - (8 + j * 6)), (x, y)], fill=lerpc(top, (150, 130, 120), 0.12))
    if winter:
        for i in range(60):
            x, y = int((hsh(i, 81) * 400 - scroll) % 400) - 40, ground + 2 + int(hsh(i, 82) * (H - ground - 3))
            d.point((x, y), fill=(255, 255, 255) if hsh(i, 83) > 0.5 else (196, 208, 232))
    else:
        tones = LEAF_TONES['year2' if season == 'year2' else 'autumn']
        for i in range(90):
            x = int((hsh(i, 11) * 420 - scroll) % 420) - 50
            y = ground + 3 + int(hsh(i, 12) ** 1.6 * (H - ground - 4))
            c = tones[1 + int(hsh(i, 13) * 3) % 3]
            d.point((x, y), fill=c); d.point((x + 1, y), fill=c); d.point((x, y + 1), fill=tones[0])
            if hsh(i, 14) > 0.6:
                d.point((x + 1, y - 1), fill=tones[3])


def snowfall(img, t, n=50, k=1.0, top=0, bot=H):
    d = ImageDraw.Draw(img)
    for i in range(int(n * k)):
        near = hsh(i, 35) > 0.75
        sp = (0.1 + hsh(i, 31) * 0.06) * (1.6 if near else 1)
        ph = (t * sp + hsh(i, 32)) % 1
        x = int((hsh(i, 33) * 340 + math.sin(t * 0.8 + i) * (12 if near else 6)) % 340) - 10
        y = int(top - 4 + ph * (bot - top + 8))
        if near:
            d.rectangle([x, y, x + 1, y + 1], fill=(252, 253, 255))
        else:
            d.point((x, y), fill=(236, 240, 250))


def falling_leaves(img, t, n, scroll, ground, season):
    d = ImageDraw.Draw(img)
    tones = LEAF_TONES['year2' if season == 'year2' else 'autumn']
    for i in range(int(n)):
        ph = (t * (0.13 + hsh(i, 9) * 0.06) + hsh(i, 7)) % 1
        x = int((hsh(i, 8) * 360 - scroll * 0.8 + math.sin(t * 1.4 + i) * 14) % 360) - 20
        y = int(-6 + ph * (ground + 16))
        f = int(t * 5 + i) % 3
        if f == 0:
            d.point((x, y), fill=tones[2]); d.point((x + 1, y), fill=tones[2]); d.point((x + 2, y), fill=tones[3]); d.point((x + 1, y + 1), fill=tones[1])
        elif f == 1:
            d.point((x, y), fill=tones[2]); d.point((x, y + 1), fill=tones[1]); d.point((x + 1, y), fill=tones[3])
        else:
            d.point((x, y), fill=tones[1]); d.point((x + 1, y + 1), fill=tones[2])


# =====================================================================
# 迭代二（PIXMV_STYLE=2）：高清光影层
#   背景快照（场景函数画完背景时记一张）→ 和成帧比较得到“前景遮罩”（人物、道具、像素字）
#   → 背景做轻微景深虚化，前景保持锐利 → 前景朝光一侧加暖色轮廓光 → 户外白天加柔和光束 → 按季节调色
# =====================================================================
from PIL import ImageFilter
BGSNAP = [None]
GRADE = [None]
FW, FH = 1920, 1080


def mark(img):
    if BGSNAP[0] is None:
        BGSNAP[0] = img.copy()


def _lut(gain, lift, gamma, s_curve):
    x = np.arange(256) / 255.0
    out = []
    for c in range(3):
        y = x ** gamma
        y = y + s_curve * (y - 0.5) * (1 - abs(2 * y - 1)) * 0.5
        y = lift[c] / 255 + y * (1 - lift[c] / 255)
        out.append(np.clip(y * gain[c] * 255, 0, 255).astype(np.uint8))
    return np.stack(out, 1)


LUTS = {
    'day': _lut((1.02, 1.0, 0.97), (10, 8, 18), 0.96, 0.25),
    'gold': _lut((1.05, 0.99, 0.92), (14, 8, 16), 0.95, 0.28),
    'dawn': _lut((1.02, 0.99, 1.0), (14, 10, 22), 0.95, 0.22),
    'winter': _lut((0.97, 1.0, 1.05), (10, 12, 22), 0.97, 0.2),
    'night': _lut((0.98, 0.98, 1.06), (8, 8, 22), 1.02, 0.3),
    'wnight': _lut((0.96, 0.99, 1.08), (8, 10, 26), 1.02, 0.3),
    None: _lut((1.0, 1.0, 0.99), (8, 8, 14), 0.98, 0.18),
}
_RAYS = {}


def rays(big, t, key):
    """户外白天：从左上斜射下来的几道柔和光束，缓慢摆动"""
    k = int(t * 4)
    if (key, k) not in _RAYS:
        lay = Image.new('L', (480, 270), 0)
        d = ImageDraw.Draw(lay)
        for i in range(5):
            x = 40 + i * 80 + math.sin(t * 0.3 + i) * 12
            w = 18 + i % 3 * 10
            d.polygon([(x, -10), (x + w, -10), (x + w + 160, 280), (x + 160, 280)], fill=90 - i * 10)
        lay = lay.filter(ImageFilter.GaussianBlur(14)).resize((FW, FH), Image.BILINEAR)
        _RAYS.clear()
        _RAYS[(key, k)] = np.asarray(lay).astype(np.float32) / 255
    return _RAYS[(key, k)]


def hd_pass(big, img, bgp, t, key):
    a = np.asarray(big).astype(np.float32)
    if bgp is not None:
        fg = np.any(np.asarray(img) != np.asarray(bgp), axis=2)
        fgm = Image.fromarray((fg * 255).astype(np.uint8)).resize((960, 540), Image.NEAREST).filter(ImageFilter.GaussianBlur(0.8)).resize((FW, FH), Image.BILINEAR)
        m = np.asarray(fgm).astype(np.float32)[..., None] / 255
        bgb = np.asarray(bgp.resize((960, 540), Image.NEAREST).filter(ImageFilter.GaussianBlur(1.2)).resize((FW, FH), Image.BILINEAR)).astype(np.float32)
        a = a * m + bgb * (1 - m)
        if key not in ('night', 'wnight'):        # 轮廓光：前景朝左上（受光）的一侧
            mm = m[..., 0]
            rim = np.clip(mm - np.roll(np.roll(mm, 5, 0), 5, 1), 0, 1)
            rim = np.asarray(Image.fromarray((rim * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
            lc = np.array((255, 236, 200) if key in ('day', 'gold', 'dawn') else (220, 236, 255), np.float32)
            a += rim[..., None] * lc * 0.5
        if key in ('day', 'gold', 'dawn'):
            r = rays(big, t, key)[..., None]
            col = np.array((255, 236, 196) if key != 'dawn' else (255, 220, 230), np.float32)
            a = a + (col - a) * r * 0.24
    out = np.clip(a, 0, 255).astype(np.uint8)
    lut = LUTS.get(key, LUTS[None])
    out = np.stack([lut[out[..., c], c] for c in range(3)], -1)
    big.paste(Image.fromarray(out))


# 光影层改用 skill 内置的 lib/style.py（引擎 MV(hd_light=True) 统一调用），这里只做别名，保证场景函数里的 mark / GRADE 指向同一份
import style as _LS
BGSNAP, GRADE, mark, hd_pass = _LS.BGSNAP, _LS.GRADE, _LS.mark, _LS.hd_pass
