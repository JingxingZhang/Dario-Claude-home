"""Chalkboard-style explainer video: 为什么天空是蓝色？ (30 s, 1920x1080, 30 fps)."""
# Fonts: put MaShanZheng-Regular.ttf (Google Fonts, OFL) in ./fonts/ — e.g.
#   curl -L -o fonts/MaShanZheng-Regular.ttf https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/mashanzheng/MaShanZheng-Regular.ttf
# Deps: pip install numpy pillow scipy fonttools ; ffmpeg on PATH.
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage
from fontTools.ttLib import TTFont
from multiprocessing import Pool

W, H = int(os.environ.get("CHALK_W", 1920)), int(os.environ.get("CHALK_H", 1080))
FPS, DUR = 30, 30.0
NF = int(FPS * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts/MaShanZheng-Regular.ttf")
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CMAP = set(TTFont(FONT).getBestCmap().keys())
rng = np.random.default_rng(7)

WHITE = (238, 236, 226)
YELLOW = (246, 226, 122)
BLUE = (128, 192, 242)
PINK = (242, 134, 134)
ORANGE = (247, 168, 92)

# ---------------------------------------------------------------- board
def make_board():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([34, 54, 46], np.float32)
    lo = ndimage.gaussian_filter(rng.standard_normal((H // 8, W // 8)).astype(np.float32), 6)
    lo = np.kron(lo / (lo.std() + 1e-6), np.ones((8, 8), np.float32))[:H, :W]
    img = base[None, None, :] + lo[..., None] * 3.0
    # faint old-chalk smears
    smear = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(smear)
    for _ in range(26):
        cx, cy = rng.uniform(0, W), rng.uniform(0, H)
        for k in range(6):
            dx = rng.uniform(-260, 260)
            d.line([(cx, cy + k * 18), (cx + dx, cy + k * 18 + rng.uniform(-20, 20))],
                   fill=int(rng.uniform(20, 60)), width=int(rng.uniform(30, 70)))
    smear = np.asarray(smear.filter(ImageFilter.GaussianBlur(28)), np.float32) / 255.0
    img += smear[..., None] * np.array([40, 44, 40], np.float32) * 0.55
    # fine grain
    img += rng.standard_normal((H, W, 1)).astype(np.float32) * 2.2
    # vignette
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    img *= (1 - 0.32 * np.clip(r - 0.35, 0, 1) ** 1.4)[..., None]
    # wooden frame
    F = 26
    wood = np.array([96, 64, 38], np.float32)
    grain = ndimage.gaussian_filter1d(rng.standard_normal((H, W)).astype(np.float32), 40, axis=1)
    grain = grain / (grain.std() + 1e-6)
    frame = np.zeros((H, W), bool)
    frame[:F, :] = frame[-F:, :] = True
    frame[:, :F] = frame[:, -F:] = True
    woodimg = wood[None, None, :] * (1 + 0.10 * grain[..., None])
    img[frame] = woodimg[frame]
    # inner shadow next to the frame
    dist = np.minimum.reduce([x - F, W - F - x, y - F, H - F - y])
    sh = np.clip(1 - dist / 18.0, 0, 1) * (~frame)
    img *= (1 - 0.45 * sh)[..., None]
    return np.clip(img, 0, 255)

# chalk grain texture shared by all chalk (board tooth): mostly horizontal streaks
def make_grain():
    n = rng.random((H, W)).astype(np.float32)
    n = ndimage.gaussian_filter(n, (0.6, 2.2))
    n = (n - n.mean()) / n.std()
    return n

GRAIN = make_grain()

def chalkify(mask, x0, y0, density=0.55):
    """mask: float [0,1] crop. returns alpha with broken chalk texture."""
    h, w = mask.shape
    g = GRAIN[y0:y0 + h, x0:x0 + w]
    soft = ndimage.gaussian_filter(mask, 0.9)
    a = np.clip((soft - 0.5 + 0.38 * g * 0.5 + (density - 0.5)) * 3.2 + 0.5, 0, 1) * (soft > 0.05)
    a = a * (0.80 + 0.20 * np.clip(g, -1, 1))
    halo = ndimage.gaussian_filter(mask, 3.0) * 0.10
    return np.clip(np.maximum(a, halo), 0, 1).astype(np.float32)

# ---------------------------------------------------------------- elements
class Element:
    def __init__(self, color, t0, t1, x0, y0, mask, reveal, tip, density=0.55, eraser=None):
        self.color = np.array(color, np.float32)
        self.t0, self.t1 = t0, t1
        self.x0, self.y0 = x0, y0
        self.alpha = chalkify(mask, x0, y0, density)
        self.reveal = reveal.astype(np.float32)
        self.tip = tip
        self.eraser = eraser

    def progress(self, t):
        if t <= self.t0: return 0.0
        if t >= self.t1: return 1.0
        u = (t - self.t0) / (self.t1 - self.t0)
        return u

def ease(u):
    return u * u * (3 - 2 * u)

PAD = 12

def jitter_path(pts, amp=1.4, seed=None):
    r = np.random.default_rng(seed)
    pts = np.asarray(pts, np.float32)
    n = len(pts)
    wob = ndimage.gaussian_filter1d(r.standard_normal((n, 2)).astype(np.float32), max(1, n / 25)) * amp * 3
    return pts + wob

def densify(pts, step=2.0):
    pts = np.asarray(pts, np.float32)
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(b - a)
        k = max(1, int(L / step))
        for i in range(1, k + 1):
            out.append(a + (b - a) * i / k)
    return np.array(out)

def stroke_element(paths, color, t0, t1, width=7, density=0.55, jitter=1.2):
    """paths: list of polylines, drawn in order (pen lifts between)."""
    paths = [jitter_path(densify(p), jitter, seed=int(rng.integers(1e9))) for p in paths]
    allp = np.concatenate(paths)
    x0 = int(max(0, allp[:, 0].min() - width - PAD)); y0 = int(max(0, allp[:, 1].min() - width - PAD))
    x1 = int(min(W, allp[:, 0].max() + width + PAD)); y1 = int(min(H, allp[:, 1].max() + width + PAD))
    w, h = x1 - x0, y1 - y0
    lens = [np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)) + 1e-3 for p in paths]
    total = sum(lens)
    mask = Image.new("L", (w, h), 0)
    rev = Image.new("I", (w, h), 2 ** 30)
    dm, dr = ImageDraw.Draw(mask), ImageDraw.Draw(rev)
    SCALE = 100000
    seq = []
    acc = 0.0
    for p, L in zip(paths, lens):
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        cum = acc + np.concatenate([[0], np.cumsum(seg)])
        for i in range(len(p) - 1):
            seq.append((p[i] - (x0, y0), p[i + 1] - (x0, y0), cum[i] / total))
        acc += L
    tip_pts = np.concatenate(paths); tip_s = []
    acc = 0.0
    for p, L in zip(paths, lens):
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        tip_s.append(acc + np.concatenate([[0], np.cumsum(seg)]))
        acc += L
    tip_s = np.concatenate(tip_s) / total
    for a, b, s in reversed(seq):  # earlier segments win
        wv = width * (0.85 + 0.3 * rng.random())
        dm.line([tuple(a), tuple(b)], fill=255, width=int(round(wv)))
        dr.line([tuple(a), tuple(b)], fill=int(s * SCALE), width=int(round(wv)) + 4)
        r = wv / 2
        dm.ellipse([a[0] - r, a[1] - r, a[0] + r, a[1] + r], fill=255)
        dr.ellipse([a[0] - r - 2, a[1] - r - 2, a[0] + r + 2, a[1] + r + 2], fill=int(s * SCALE))
    mask = np.asarray(mask, np.float32) / 255.0
    rev = np.asarray(rev, np.float64)
    rev = np.where(rev >= 2 ** 30, 9.0, rev / SCALE)

    def tip(u):
        i = min(len(tip_pts) - 1, int(np.searchsorted(tip_s, u)))
        return tip_pts[i]
    return Element(color, t0, t1, x0, y0, mask, rev, tip, density)

def text_element(text, x, y, size, color, t0, t1, anchor="l", density=0.6):
    """Supports '^' prefix for a superscript char. Writes char by char, slanted wipe."""
    font = ImageFont.truetype(FONT, size)
    fb = ImageFont.truetype(FALLBACK, int(size * 0.80))
    sup = ImageFont.truetype(FALLBACK, int(size * 0.45))
    glyphs = []
    i = 0
    while i < len(text):
        c = text[i]
        if c == "^":
            glyphs.append((text[i + 1], sup, -0.42)); i += 2; continue
        f = font if ord(c) in CMAP else fb
        glyphs.append((c, f, 0.0)); i += 1
    widths = []
    for c, f, _ in glyphs:
        widths.append(f.getlength(c) if c != " " else size * 0.35)
    tw = sum(widths)
    if anchor == "c": x = x - tw / 2
    x0 = int(x - PAD); y0 = int(y - size * 0.6 - PAD)
    w = int(tw + 2 * PAD); h = int(size * 1.6 + 2 * PAD)
    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    rev = np.full((h, w), 9.0)
    n = max(1, sum(1 for c, _, _ in glyphs if c.strip()))
    k = 0
    cx = x - x0
    boxes = []
    for (c, f, dy), gw in zip(glyphs, widths):
        if c.strip():
            m = Image.new("L", (w, h), 0)
            ImageDraw.Draw(m).text((cx, (y - y0) + dy * size), c, font=f, fill=255, anchor="lm" if f is not sup else "lm")
            ma = np.asarray(m, np.float32) / 255.0
            yy, xx = np.nonzero(ma > 0.02)
            if len(xx):
                gx0, gx1 = xx.min(), xx.max() + 1
                gy0, gy1 = yy.min(), yy.max() + 1
                Y, X = np.mgrid[0:h, 0:w]
                local = ((X - gx0) + 0.35 * (Y - gy0)) / ((gx1 - gx0) + 0.35 * (gy1 - gy0) + 1e-3)
                sel = ma > 0.02
                rev[sel] = np.minimum(rev[sel], (k + np.clip(local[sel], 0, 1)) / n)
                boxes.append((k / n, (k + 1) / n, gx0 + x0, gx1 + x0, gy0 + y0, gy1 + y0))
                mask = Image.fromarray(np.maximum(np.asarray(mask), np.asarray(m)))
            k += 1
        cx += gw
    mask = np.asarray(mask, np.float32) / 255.0

    def tip(u):
        for a, b, gx0, gx1, gy0, gy1 in boxes:
            if u <= b:
                v = (u - a) / (b - a)
                v = min(max(v, 0), 1)
                return np.array([gx0 + (gx1 - gx0) * v, gy0 + (gy1 - gy0) * (0.5 + 0.4 * math.sin(v * 9))])
        a, b, gx0, gx1, gy0, gy1 = boxes[-1]
        return np.array([gx1, (gy0 + gy1) / 2])
    return Element(color, t0, t1, x0, y0, mask, rev, tip, density)

def circle_pts(cx, cy, r, a0=-100, a1=265, n=160):
    a = np.radians(np.linspace(a0, a1, n))
    rr = r * (1 + 0.015 * np.sin(a * 3))
    return np.stack([cx + rr * np.cos(a), cy + rr * np.sin(a)], 1)

def wave_pts(x0, x1, y, lam, amp):
    xs = np.arange(x0, x1, 2.0)
    return np.stack([xs, y + amp * np.sin((xs - x0) / lam * 2 * np.pi)], 1)

def arrow_paths(a, b, head=26):
    a, b = np.array(a, float), np.array(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    h1 = b - d * head + n * head * 0.6
    h2 = b - d * head - n * head * 0.6
    return [[a, b], [h1, b, h2]]

# ---------------------------------------------------------------- eraser
class Eraser:
    def __init__(self, x0, y0, x1, y1, t0, t1, bw=150, bh=70):
        self.t0, self.t1 = t0, t1
        self.box = (x0, y0, x1, y1)
        self.bw, self.bh = bw, bh
        rows = np.arange(y0 + bh * 0.4, y1 + bh * 0.4, bh * 0.85)
        pts = []
        for i, ry in enumerate(rows):
            xs = (x0, x1) if i % 2 == 0 else (x1, x0)
            pts += [(xs[0], ry), (xs[1], ry + bh * 0.25)]
        self.path = densify(pts, 6.0)
        seg = np.linalg.norm(np.diff(self.path, axis=0), axis=1)
        self.s = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()
        rev = np.full((H, W), 9.0, np.float32)
        hw, hh = int(bw * 0.5), int(bh * 0.62)
        for (px, py), sv in zip(self.path, self.s):
            xa, xb = max(0, int(px) - hw), min(W, int(px) + hw)
            ya, yb = max(0, int(py) - hh), min(H, int(py) + hh)
            r = rev[ya:yb, xa:xb]
            np.minimum(r, sv, out=r)
        self.rev = rev

    def progress(self, t):
        if t <= self.t0: return 0.0
        if t >= self.t1: return 1.0
        return (t - self.t0) / (self.t1 - self.t0)

    def pos(self, u):
        i = min(len(self.path) - 1, int(np.searchsorted(self.s, u)))
        return self.path[i]

# ---------------------------------------------------------------- script
def build():
    E = []
    # Title
    E.append(text_element("为什么天空是蓝色？", W / 2, 118, 104, WHITE, 0.4, 3.0, anchor="c", density=0.62))
    ul = wave_pts(560, 1360, 192, 260, 4)
    E.append(stroke_element([ul], YELLOW, 3.0, 3.7, width=6))

    # Scene A ------------------------------------------------ 4 → 19.5 s
    sun_c, sun_r = (250, 450), 66
    E.append(stroke_element([circle_pts(*sun_c, sun_r)], YELLOW, 4.0, 4.9, width=8))
    rays = []
    for k in range(12):
        a = k / 12 * 2 * np.pi
        r0, r1 = sun_r + 16, sun_r + 44
        rays.append([(sun_c[0] + r0 * np.cos(a), sun_c[1] + r0 * np.sin(a)),
                     (sun_c[0] + r1 * np.cos(a), sun_c[1] + r1 * np.sin(a))])
    E.append(stroke_element(rays, YELLOW, 4.9, 5.9, width=6))
    E.append(text_element("太阳光 = 七色混合", 250, 600, 46, WHITE, 6.0, 7.4, anchor="c"))

    E.append(stroke_element([wave_pts(370, 1080, 360, 42, 20)], BLUE, 7.5, 9.3, width=7))
    E.append(text_element("蓝光：波长短 ~450nm", 1110, 360, 50, BLUE, 9.3, 10.6))
    E.append(stroke_element([wave_pts(370, 1080, 520, 120, 26)], PINK, 10.7, 12.3, width=7))
    E.append(text_element("红光：波长长 ~700nm", 1110, 520, 50, PINK, 12.3, 13.6))

    E.append(text_element("散射强度 ∝ 1/λ^4", 760, 760, 92, WHITE, 13.8, 15.8, anchor="c", density=0.64))
    box = [[(400, 680), (1125, 676), (1130, 846), (396, 850), (402, 676)]]
    E.append(stroke_element(box, YELLOW, 15.9, 16.9, width=6))
    E.append(stroke_element(arrow_paths((1160, 763), (1290, 763)), WHITE, 17.0, 17.5, width=6))
    E.append(text_element("蓝光散射≈红光的 5.9 倍", 1310, 735, 48, YELLOW, 17.5, 18.8))
    E.append(text_element("(700÷450)^4 ≈ 5.9", 1310, 805, 40, WHITE, 18.0, 19.0))
    eraser = Eraser(150, 250, W - 150, 1010, 19.6, 21.6, bw=170, bh=100)
    for e in E[2:]:
        e.eraser = eraser

    # Scene B ------------------------------------------------ 21.8 → 30 s
    B = []
    GY = 800
    B.append(stroke_element([[(80, GY), (W - 80, GY + 4)]], WHITE, 21.8, 22.4, width=6))
    B.append(stroke_element([[(960, 250), (960, GY - 20)]], WHITE, 22.0, 22.4, width=4, density=0.45))
    B.append(text_element("白天", 120, 270, 56, YELLOW, 22.3, 22.9))
    B.append(text_element("日落", 1000, 270, 56, ORANGE, 22.3, 22.9))

    def person(px):
        return [circle_pts(px, GY - 66, 15, -90, 270, 60), [(px, GY - 50), (px, GY - 22)],
                [(px - 18, GY - 40), (px, GY - 34), (px + 18, GY - 40)],
                [(px - 14, GY), (px, GY - 22), (px + 14, GY)]]
    # day panel
    B.append(stroke_element([circle_pts(480, 340, 42)], YELLOW, 22.9, 23.5, width=7))
    B.append(stroke_element(person(480), WHITE, 23.5, 24.1, width=5))
    B.append(stroke_element(arrow_paths((480, 400), (480, 700)), WHITE, 24.1, 24.6, width=6))
    dots = []
    while len(dots) < 70:
        px, py = rng.uniform(120, 900), rng.uniform(300, 760)
        if abs(px - 480) < 40 or (abs(px - 480) < 80 and abs(py - 340) < 80): continue
        dots.append((px, py))
    dots.sort(key=lambda p: abs(p[0] - 480) + 0.3 * abs(p[1] - 500))
    dpaths = []
    for px, py in dots:
        a = rng.uniform(0, 2 * np.pi)
        dpaths.append([(px, py), (px + 7 * np.cos(a), py + 7 * np.sin(a))])
    B.append(stroke_element(dpaths, BLUE, 24.6, 25.9, width=7, jitter=0.3))
    B.append(text_element("光路短：蓝光四处散射 → 满天蓝", 480, 850, 40, BLUE, 25.0, 26.3, anchor="c"))
    # sunset panel
    sun2 = circle_pts(1745, GY, 50, 180, 360, 80)
    B.append(stroke_element([sun2], ORANGE, 25.6, 26.1, width=7))
    B.append(stroke_element(person(1080), WHITE, 25.9, 26.4, width=5))
    long = np.stack([np.linspace(1680, 1130, 120), GY - 40 - 6 * np.sin(np.linspace(0, np.pi, 120))], 1)
    B.append(stroke_element([long, [(1150, GY - 58), (1128, GY - 40), (1150, GY - 22)]], ORANGE, 26.4, 27.1, width=6))
    sc = []
    for k in range(16):
        bx = 1660 - k * 30 + rng.uniform(-8, 8)
        by = GY - 70 - rng.uniform(10, 160) * (1 - k / 22)
        sc.append([(bx, by), (bx + 6, by - 5)])
    B.append(stroke_element(sc, BLUE, 26.6, 27.3, width=7, jitter=0.3))
    B.append(text_element("光路长：蓝光沿途散尽 → 夕阳橙红", 1400, 850, 40, ORANGE, 26.8, 28.0, anchor="c"))
    # conclusion
    B.append(text_element("波长越短，散射越强 —— 所以天空是蓝的", W / 2, 965, 62, WHITE, 28.0, 29.4, anchor="c", density=0.64))
    B.append(stroke_element([wave_pts(560, 1360, 1012, 300, 3)], YELLOW, 29.4, 29.8, width=5))
    return E + B, [eraser]

# ---------------------------------------------------------------- render
BOARD = None
ELEMS = None
ERASERS = None
RESIDUE = None

def init():
    global BOARD, ELEMS, ERASERS, RESIDUE
    BOARD = make_board()
    ELEMS, ERASERS = build()
    # residue = blurred ghost of erased content
    acc = np.zeros((H, W, 3), np.float32)
    al = np.zeros((H, W), np.float32)
    for e in ELEMS:
        if e.eraser is None: continue
        h, w = e.alpha.shape
        al[e.y0:e.y0 + h, e.x0:e.x0 + w] = np.maximum(al[e.y0:e.y0 + h, e.x0:e.x0 + w], e.alpha)
    RESIDUE = ndimage.gaussian_filter(al, (5, 14)) * 0.12

def chalk_stick(img, pos, color, angle=-0.9):
    x, y = pos
    L, Wd = 70, 16
    d = np.array([math.cos(angle), math.sin(angle)])
    n = np.array([-d[1], d[0]])
    p = np.array([x, y]) + d * 4
    q = p + d * L
    poly = [p + n * Wd / 2, q + n * Wd / 2, q - n * Wd / 2, p - n * Wd / 2]
    shadow = [tuple(v + (10, 14)) for v in poly]
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im, "RGBA")
    dr.polygon(shadow, fill=(0, 0, 0, 70))
    c = tuple(int(min(255, v * 0.95 + 15)) for v in color)
    dr.polygon([tuple(v) for v in poly], fill=c + (255,))
    dr.line([tuple(poly[0]), tuple(poly[1])], fill=(255, 255, 255, 120), width=3)
    dr.polygon([tuple(p + n * Wd / 2), tuple(p - n * Wd / 2), tuple(p - d * 5)], fill=c + (255,))
    return np.asarray(im)

def draw_eraser(img, pos, u):
    x, y = pos
    bw, bh = 170, 74
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im, "RGBA")
    ang = math.sin(u * 40) * 3
    dr.rounded_rectangle([x - bw / 2 + 12, y - bh / 2 + 16, x + bw / 2 + 12, y + bh / 2 + 16], 10, fill=(0, 0, 0, 80))
    dr.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], 10, fill=(150, 104, 62, 255))
    dr.rounded_rectangle([x - bw / 2 + 6, y - bh / 2 + 6, x + bw / 2 - 6, y + bh / 2 - 22], 6, fill=(178, 128, 80, 255))
    dr.rectangle([x - bw / 2 + 2, y + bh / 2 - 18, x + bw / 2 - 2, y + bh / 2 - 2], fill=(214, 214, 206, 255))
    return np.asarray(im)

def render_frame(fi):
    t = fi / FPS
    img = BOARD.copy()
    # residue from eraser
    for er in ERASERS:
        ue = er.progress(t)
        if ue > 0:
            m = np.clip((ue - er.rev) * 40, 0, 1)
            img += (RESIDUE * m)[..., None] * (np.array([230, 232, 224]) - img) * 1.0
    tip = None
    for e in ELEMS:
        u = e.progress(t)
        if u <= 0: continue
        h, w = e.alpha.shape
        a = e.alpha * np.clip((u - e.reveal) * 60 + 1, 0, 1) if u < 1 else e.alpha * (e.reveal < 5)
        if e.eraser is not None:
            ue = e.eraser.progress(t)
            if ue > 0:
                a = a * (1 - np.clip((ue - e.eraser.rev[e.y0:e.y0 + h, e.x0:e.x0 + w]) * 40, 0, 1))
        sl = img[e.y0:e.y0 + h, e.x0:e.x0 + w]
        sl += a[..., None] * (e.color - sl)
        if 0 < u < 1:
            tip = (e.tip(u), e.color)
    out = np.clip(img, 0, 255).astype(np.uint8)
    for er in ERASERS:
        ue = er.progress(t)
        if 0 < ue < 1:
            out = draw_eraser(out, er.pos(ue), ue)
    if tip is not None:
        out = chalk_stick(out, tip[0], tip[1])
    return out.tobytes()

# ---------------------------------------------------------------- audio
def make_audio(path):
    SR = 48000
    N = int(SR * DUR)
    t = np.arange(N) / SR
    env = np.zeros(N, np.float32)
    er_env = np.zeros(N, np.float32)
    ELEMS_, ERS_ = ELEMS, ERASERS
    for e in ELEMS_:
        i0, i1 = int(e.t0 * SR), int(e.t1 * SR)
        seg = np.zeros(i1 - i0, np.float32)
        # strokes come in bursts: gate by a ~6 Hz on/off rhythm
        tt = np.arange(i1 - i0) / SR
        r = np.random.default_rng(i0)
        ph = r.uniform(0, 6)
        gate = 0.55 + 0.45 * np.sin(2 * np.pi * (5 + r.uniform(-1, 1)) * tt + ph)
        gate = np.clip(gate, 0, 1) ** 1.6
        fade = np.minimum(1, np.minimum(tt / 0.03, (tt[-1] - tt) / 0.05 + 1e-3))
        env[i0:i1] = np.maximum(env[i0:i1], gate * fade)
        # tap at pen-down
        k = np.arange(int(0.025 * SR))
        env[i0:i0 + len(k)] += 1.6 * np.exp(-k / (0.004 * SR))
    for er in ERS_:
        i0, i1 = int(er.t0 * SR), int(er.t1 * SR)
        tt = np.arange(i1 - i0) / SR
        er_env[i0:i1] = (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 1.6 * tt))) * np.minimum(1, tt / 0.1)
    r = np.random.default_rng(1)
    noise = r.standard_normal(N).astype(np.float32)
    F = np.fft.rfft(noise)
    f = np.fft.rfftfreq(N, 1 / SR)
    chalk = np.fft.irfft(F * np.exp(-((np.log(f + 1) - np.log(3800)) ** 2) / 0.35), N)
    rub = np.fft.irfft(F * np.exp(-((np.log(f + 1) - np.log(700)) ** 2) / 0.5), N)
    grit = np.abs(ndimage.gaussian_filter1d(r.standard_normal(N), 60)); grit /= grit.max()
    chalk = chalk / np.abs(chalk).max() * (0.4 + 0.9 * grit)
    rub = rub / np.abs(rub).max()
    room = np.fft.irfft(np.fft.rfft(r.standard_normal(N)) * np.exp(-f / 300), N)
    room = room / np.abs(room).max() * 0.015
    y = 0.22 * chalk * env + 0.28 * rub * er_env + room
    y = y / max(1e-6, np.abs(y).max()) * 0.7
    st = np.stack([y, np.roll(y, 24) * 0.96], 1)
    pcm = (st * 32767).astype(np.int16)
    import wave
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
        wv.writeframes(pcm.tobytes())

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "chalkboard_test.mp4")
    preview = os.environ.get("PREVIEW")
    init()
    if preview:
        for ts in preview.split(","):
            fi = int(float(ts) * FPS)
            Image.frombytes("RGB", (W, H), render_frame(fi)).save(os.path.join(HERE, f"prev_{ts}.png"))
        sys.exit()
    wav = os.path.join(HERE, "chalk.wav")
    make_audio(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(NF), chunksize=4)):
            ff.stdin.write(fr)
            if k % 90 == 0: print("frame", k, flush=True)
    ff.stdin.close(); ff.wait()
    print("done", out)
