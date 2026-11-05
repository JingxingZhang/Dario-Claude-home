"""像素 MV 底层库：Fusion Pixel 12px 像素字、调色、抖动渐变、天空与水面、文字绘制。
原生画布 320×180，成片按最近邻放大 6 倍到 1920×1080。"""
import json, math, os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 320, 180
SCALE = 6
FPS = 30
ROOT = os.environ.get('PIXMV_PROJECT', os.getcwd())
FONT_DIR = os.environ.get('PIXFONT', os.path.expanduser('~/.cache/pixfont'))

# ---------------- 调色 ----------------
INK = (18, 16, 30)
INK2 = (38, 34, 58)
PAPER = (240, 232, 210)
WHITE = (250, 248, 240)
GRAY = (128, 124, 142)
GRAY_D = (78, 74, 96)
GOLD = (255, 210, 84)
GOLD_D = (190, 140, 50)
RED = (206, 44, 52)
RED_L = (238, 92, 72)
RED_D = (126, 26, 40)
LACQ = (178, 34, 44)
BROWN = (120, 78, 48)
BROWN_D = (78, 48, 34)
BROWN_L = (164, 116, 70)
SAND = (214, 184, 120)
SAND_D = (170, 138, 84)
BLUE = (60, 96, 170)
BLUE_D = (34, 52, 104)
TEAL = (64, 140, 150)
REED = (176, 170, 82)
REED_D = (120, 116, 52)
SMOKE = (92, 86, 100)
SMOKE_L = (140, 134, 146)
ORANGE = (250, 140, 40)
YEL = (255, 236, 120)
SKIN = (226, 176, 130)

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0


def lerp(a, b, k):
    return a + (b - a) * k


def lerpc(c1, c2, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(round(lerp(c1[i], c2[i], k))) for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def seg(t, a, b):
    """t 在 [a,b] 内的进度 0..1"""
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def hsh(*v):
    """确定性伪随机 0..1"""
    x = 0
    for i in v:
        x = (x * 1000003 + int(i * 7919) + 12345) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0x5BD1E995) & 0xFFFFFFFF
    x ^= x >> 15
    return (x & 0xFFFFFF) / float(0x1000000)


# ---------------- 天空 / 水面 ----------------
# tod：0 拂晓 · 0.15 早晨 · 0.45 正午 · 0.7 午后 · 0.85 日晡（傍晚）· 1 夜
SKY_KEYS = [
    (0.00, (44, 40, 96), (236, 146, 112)),
    (0.15, (74, 112, 184), (206, 214, 214)),
    (0.45, (58, 118, 200), (172, 214, 236)),
    (0.70, (84, 100, 172), (238, 196, 142)),
    (0.85, (62, 38, 92), (252, 122, 62)),
    (1.00, (10, 12, 32), (44, 42, 84)),
]


def sky_colors(tod):
    tod = clamp(tod)
    for (a, ta, ba), (b, tb, bb) in zip(SKY_KEYS, SKY_KEYS[1:]):
        if a <= tod <= b:
            k = (tod - a) / (b - a)
            return lerpc(ta, tb, k), lerpc(ba, bb, k)
    return SKY_KEYS[-1][1], SKY_KEYS[-1][2]


def dither_grad(h, w, c_top, c_bot, levels=7):
    """竖向渐变 + 4×4 Bayer 抖动，量化成 levels 档"""
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    q = v * (levels - 1)
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    idx = np.floor(q + bay - 0.5 + 0.5).clip(0, levels - 1) / (levels - 1)
    ct, cb = np.array(c_top, float), np.array(c_bot, float)
    return (ct[None, None, :] + (cb - ct)[None, None, :] * idx[:, :, None]).astype(np.uint8)


def sun_pos(tod, hz):
    """太阳沿弧线从东（右）升到西（左）落"""
    a = clamp((tod - 0.0) / 0.92)
    x = lerp(286, 34, a)
    y = hz - 6 - math.sin(a * math.pi) * (hz - 34)
    return int(x), int(y)


def draw_sky(img, tod, hz=104, sun=True, stars=0.0, t=0.0):
    top, bot = sky_colors(tod)
    arr = dither_grad(hz, W, top, bot)
    img.paste(Image.fromarray(arr, 'RGB'), (0, 0))
    d = ImageDraw.Draw(img)
    if stars > 0:
        for i in range(60):
            if hsh(i, 3) < stars:
                x, y = int(hsh(i, 1) * W), int(hsh(i, 2) * hz * 0.8)
                if hsh(i, int(t * 3)) > 0.15:
                    d.point((x, y), fill=(220, 220, 240))
    if sun and tod < 0.97:
        sx, sy = sun_pos(tod, hz)
        if tod > 0.75:
            col, core = (255, 140, 60), (255, 200, 120)
        elif tod < 0.08:
            col, core = (255, 170, 110), (255, 220, 170)
        else:
            col, core = (255, 230, 150), (255, 250, 220)
        disc(d, sx, sy, 9, col)
        disc(d, sx, sy, 7, core)
    return top, bot


def disc(d, cx, cy, r, col):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)) + 0.3)
        d.line([(cx - dx, cy + dy), (cx + dx, cy + dy)], fill=col)


def draw_water(img, t, tod, hz=104, red=0.0, choppy=0.3, y1=H):
    top, bot = sky_colors(tod)
    wt = lerpc(lerpc(bot, (30, 60, 90), 0.55), (150, 30, 40), red)
    wb = lerpc(lerpc(top, (10, 20, 40), 0.6), (80, 10, 20), red)
    arr = dither_grad(y1 - hz, W, wt, wb, levels=6)
    img.paste(Image.fromarray(arr, 'RGB'), (0, hz))
    d = ImageDraw.Draw(img)
    hl = lerpc(lerpc(bot, WHITE, 0.4), (255, 120, 90), red)
    n = int(70 + choppy * 90)
    for i in range(n):
        yy = hz + 2 + int((hsh(i, 9) ** 1.6) * (y1 - hz - 3))
        depth = (yy - hz) / max(1, (y1 - hz))
        spd = 3 + depth * 10
        ln = 2 + int(depth * 8 * (0.5 + hsh(i, 4)))
        x = (hsh(i, 5) * (W + 40) + t * spd * (1 if i % 2 else -1)) % (W + 40) - 20
        if (int(t * 2 + i) % 7) != 0:
            d.line([(int(x), yy), (int(x) + ln, yy)], fill=hl if depth > 0.15 else lerpc(hl, wt, 0.4))
    return wt


def sepia(img, k=1.0):
    a = np.asarray(img).astype(float)
    lum = (a[:, :, 0] * 0.3 + a[:, :, 1] * 0.59 + a[:, :, 2] * 0.11) / 255
    lv = np.floor(lum * 5 + np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] * 0.9) / 5
    lv = lv.clip(0, 1)
    dark, light = np.array([46, 30, 24.]), np.array([242, 214, 160.])
    s = dark[None, None] + (light - dark)[None, None] * lv[:, :, None]
    out = a * (1 - k) + s * k
    return Image.fromarray(out.astype(np.uint8), 'RGB')


def tint(img, col, k):
    a = np.asarray(img).astype(float)
    out = a * (1 - k) + np.array(col, float)[None, None] * k
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGB')


# ---------------- 字体 ----------------
_cmap = None
_fonts = {}
_glyphs = {}


def _font_for(ch):
    global _cmap
    if _cmap is None:
        _cmap = json.load(open(os.path.join(FONT_DIR, 'map12.json')))
    f = _cmap.get(str(ord(ch)))
    if f is None:
        raise KeyError('像素字体缺字：' + ch)
    if not os.path.isabs(f):
        f = os.path.join(FONT_DIR, f)
    if f not in _fonts:
        _fonts[f] = ImageFont.truetype(f, 12)
    return _fonts[f]


def glyph(ch):
    """返回 (mask ndarray bool, advance)"""
    if ch in _glyphs:
        return _glyphs[ch]
    if ch == ' ':
        g = (np.zeros((12, 6), bool), 6)
    else:
        f = _font_for(ch)
        adv = int(round(f.getlength(ch)))
        im = Image.new('L', (max(adv, 12), 12), 0)
        dr = ImageDraw.Draw(im)
        dr.fontmode = '1'
        dr.text((0, 0), ch, font=f, fill=255)
        m = np.asarray(im) > 127
        g = (m[:, :adv], adv)
    _glyphs[ch] = g
    return g


def text_w(s, scale=1, gap=0):
    return sum(glyph(c)[1] + gap for c in s) * scale - (gap * scale if s else 0)


def blit_mask(arr, m, x, y, col, scale=1):
    if scale != 1:
        m = m.repeat(scale, 0).repeat(scale, 1)
    h, w = m.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(arr.shape[1], x + w), min(arr.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = m[y0 - y:y1 - y, x0 - x:x1 - x]
    arr[y0:y1, x0:x1][sub] = col


def draw_text(img, x, y, s, col, scale=1, shadow=None, gap=0, colors=None, outline=None):
    """在 PIL 图上画像素字；colors 可逐字给颜色；返回宽度"""
    x, y = int(round(x)), int(round(y))
    arr = np.array(img)
    cx = x
    for i, ch in enumerate(s):
        m, adv = glyph(ch)
        c = colors[i] if colors else col
        if outline is not None:
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                blit_mask(arr, m, cx + ox * scale, y + oy * scale, outline, scale)
        if shadow is not None:
            blit_mask(arr, m, cx + scale, y + scale, shadow, scale)
        if c is not None:
            blit_mask(arr, m, cx, y, c, scale)
        cx += (adv + gap) * scale
    img.paste(Image.fromarray(arr, 'RGB'), (0, 0))
    return cx - x


def draw_vtext(img, x, y, s, col, shadow=None):
    for i, ch in enumerate(s):
        draw_text(img, x, y + i * 13, ch, col, shadow=shadow)
