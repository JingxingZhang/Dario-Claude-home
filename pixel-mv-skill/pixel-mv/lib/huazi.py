"""综艺花字：1920×1080 高清层。粗圆体（站酷庆科黄油体）+ 多层描边 + 渐变填充 + 高光 + 投影，逐字弹跳入场，重点词放大换色，配贴纸。"""
import json, math, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pixlib import clamp, ease, hsh

FW, FH = 1920, 1080
FONT_DIR = os.environ.get('HUAFONT', os.path.expanduser('~/.cache/huafont'))

PALS = {  # (渐变上, 渐变下, 内描边, 外描边, 投影)
    'pink': ((255, 206, 232), (255, 72, 156), (255, 255, 255), (126, 14, 82), (52, 0, 36)),
    'yel': ((255, 252, 180), (255, 168, 30), (255, 255, 255), (150, 58, 0), (60, 20, 0)),
    'cyan': ((200, 252, 255), (36, 166, 255), (255, 255, 255), (8, 48, 132), (0, 16, 56)),
    'red': ((255, 186, 160), (238, 40, 56), (255, 255, 255), (110, 0, 22), (46, 0, 10)),
    'purp': ((240, 214, 255), (146, 84, 255), (255, 255, 255), (58, 16, 124), (24, 0, 56)),
    'green': ((226, 255, 176), (64, 206, 92), (255, 255, 255), (14, 88, 34), (0, 36, 12)),
    'white': ((255, 255, 255), (236, 240, 255), (255, 92, 160), (60, 10, 60), (20, 0, 30)),
    'whiteb': ((255, 255, 255), (236, 240, 255), (40, 150, 255), (10, 30, 90), (0, 10, 40)),
}


_maps = {}
_fonts = {}


def font(ch, size, fam='zcool-qingke-huangyou'):
    if fam not in _maps:
        _maps[fam] = json.load(open(os.path.join(FONT_DIR, fam + '.json')))
    f = _maps[fam].get(str(ord(ch)))
    if f is None:
        f = _maps[fam].get(str(ord('?')))
    key = (f, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(f, size)
    return _fonts[key]


def grad(w, h, c1, c2, y0, y1):
    col = Image.new('RGB', (1, h))
    for y in range(h):
        k = clamp((y - y0) / max(1, (y1 - y0)))
        col.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3)))
    return col.resize((w, h))


@lru_cache(maxsize=4096)
def char_sprite(ch, size, pal, angle=0.0, fam=None):
    """返回 (底层 RGBA：投影+描边, 面层 RGBA：渐变填充+高光, 字宽)。两层同尺寸，字以图中心为锚。"""
    if fam is None:
        fam = 'zcool-kuaile' if ord(ch) < 128 else 'zcool-qingke-huangyou'
    f = font(ch, size, fam)
    adv = f.getlength(ch)
    c1, c2, mid, out, shd = PALS[pal]
    s1, s2 = max(3, int(size * 0.075)), max(5, int(size * 0.15))
    pad = s2 + int(size * 0.12)
    w, h = int(adv) + 2 * pad, int(size * 1.25) + 2 * pad
    ox, oy = pad, pad
    def mask(stroke):
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).text((ox, oy), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255, anchor='la')
        return m
    mf, mm, mo = mask(0), mask(s1), mask(s2)
    back = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dx, dy = int(size * 0.05) + 2, int(size * 0.07) + 2
    sh = Image.new('L', (w, h), 0); sh.paste(mo, (dx, dy))
    back.paste((*shd, 230), (0, 0), sh)
    back.paste((*out, 255), (0, 0), mo)
    back.paste((*mid, 255), (0, 0), mm)
    front = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    bb = mf.getbbox() or (0, 0, w, h)
    g = grad(w, h, c1, c2, bb[1], bb[3])
    front.paste(g, (0, 0), mf)
    gl = Image.new('L', (w, h), 0)
    ImageDraw.Draw(gl).rectangle([0, 0, w, bb[1] + (bb[3] - bb[1]) * 0.4], fill=80)
    gl = Image.composite(gl, Image.new('L', (w, h), 0), mf)
    front.paste((255, 255, 255, 255), (0, 0), gl)
    if angle:
        back = back.rotate(angle, resample=Image.BICUBIC, expand=True)
        front = front.rotate(angle, resample=Image.BICUBIC, expand=True)
    return back, front, adv


# ---------------- 贴纸 ----------------
def _star(d, cx, cy, r, col, out=(60, 30, 0), w=4):
    pts = []
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=col, outline=out, width=w)


def _heart(d, cx, cy, r, col, out=(120, 0, 50), w=5):
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * r / 16, cy + y * r / 16))
    d.polygon(pts, fill=col, outline=out, width=w)
    d.ellipse([cx - r * 0.55, cy - r * 0.55, cx - r * 0.25, cy - r * 0.25], fill=(255, 255, 255))


@lru_cache(None)
def sticker(kind, size=90):
    s = size
    im = Image.new('RGBA', (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s
    if kind == 'heart':
        _heart(d, c, c, s * 0.8, (255, 90, 150), w=max(3, s // 14))
    elif kind == 'heart2':
        _heart(d, c, c, s * 0.8, (255, 60, 80), w=max(3, s // 14))
    elif kind == 'star':
        _star(d, c, c, s * 0.9, (255, 236, 90), w=max(3, s // 14))
    elif kind == 'bang':
        for i, x in enumerate((c - s * 0.35, c + s * 0.25)):
            d.rounded_rectangle([x - s * 0.13, c - s * 0.85, x + s * 0.13, c + s * 0.25], radius=s * 0.1, fill=(255, 60, 80), outline=(90, 0, 20), width=s // 12)
            d.ellipse([x - s * 0.14, c + s * 0.45, x + s * 0.14, c + s * 0.73], fill=(255, 60, 80), outline=(90, 0, 20), width=s // 12)
    elif kind == 'q':
        f = font('?', int(s * 1.5))
        d.text((c, c), '?', font=f, fill=(255, 236, 90), stroke_width=s // 10, stroke_fill=(90, 50, 0), anchor='mm')
    elif kind == 'sweat':
        pts = [(c, c - s * 0.8)]
        for i in range(25):
            a = math.pi * i / 24
            pts.append((c + math.cos(a) * s * 0.45, c + s * 0.2 + math.sin(a) * s * 0.45))
        d.polygon(pts, fill=(130, 210, 255), outline=(10, 60, 130), width=s // 12)
        d.ellipse([c - s * 0.2, c + s * 0.05, c - s * 0.02, c + s * 0.3], fill=(240, 252, 255))
    elif kind == 'x':
        for a in (45, -45):
            r = Image.new('RGBA', (s * 2, s * 2), (0, 0, 0, 0))
            rd = ImageDraw.Draw(r)
            rd.rounded_rectangle([c - s * 0.85, c - s * 0.16, c + s * 0.85, c + s * 0.16], radius=s * 0.12, fill=(255, 50, 70), outline=(90, 0, 20), width=s // 12)
            r = r.rotate(a, resample=Image.BICUBIC)
            im.alpha_composite(r)
    elif kind == 'note':
        d.ellipse([c - s * 0.55, c + s * 0.15, c - s * 0.05, c + s * 0.6], fill=(120, 230, 255), outline=(10, 50, 120), width=s // 12)
        d.rectangle([c - s * 0.14, c - s * 0.7, c - s * 0.02, c + s * 0.4], fill=(10, 50, 120))
        d.polygon([(c - s * 0.08, c - s * 0.75), (c + s * 0.5, c - s * 0.5), (c + s * 0.5, c - s * 0.25), (c - s * 0.08, c - s * 0.45)], fill=(10, 50, 120))
    elif kind == 'crack':
        pts = [(c - s * 0.2, c - s * 0.9), (c + s * 0.35, c - s * 0.9), (c + s * 0.05, c - s * 0.15), (c + s * 0.45, c - s * 0.15),
               (c - s * 0.3, c + s * 0.9), (c - s * 0.05, c + s * 0.05), (c - s * 0.45, c + s * 0.05)]
        d.polygon(pts, fill=(255, 230, 60), outline=(100, 50, 0), width=s // 12)
    elif kind == 'drop':
        pts = [(c, c - s * 0.7)]
        for i in range(25):
            a = math.pi * i / 24
            pts.append((c + math.cos(a) * s * 0.35, c + s * 0.15 + math.sin(a) * s * 0.35))
        d.polygon(pts, fill=(170, 220, 255), outline=(30, 80, 160), width=s // 14)
    elif kind == 'horn':
        for x in (c - s * 0.5, c + s * 0.5):
            d.polygon([(x - s * 0.25, c + s * 0.4), (x + s * 0.25, c + s * 0.4), (x + (s * 0.15 if x > c else -s * 0.15), c - s * 0.6)], fill=(230, 40, 70), outline=(80, 0, 20), width=s // 12)
    elif kind == 'wave':
        for k in range(2):
            pts = [(c - s * 0.85 + i * s * 0.1, c - s * 0.25 + k * s * 0.45 + math.sin(i * 0.8) * s * 0.14) for i in range(18)]
            d.line(pts, fill=(130, 230, 255), width=s // 6, joint='curve')
    return im


def draw_sticker(base, kind, x, y, size, t, born, seed=0):
    p = clamp((t - born) / 0.25)
    if p <= 0:
        return
    sc = (p * 1.3 if p < 0.6 else 1.3 - (p - 0.6) * 0.75) if p < 1 else 1.0 + 0.06 * math.sin(t * 6 + seed)
    im = sticker(kind, size)
    ang = math.sin(t * 3 + seed) * 10
    w = max(1, int(im.width * sc))
    im2 = im.resize((w, w), Image.BICUBIC).rotate(ang, resample=Image.BICUBIC)
    base.paste(im2, (int(x - w / 2), int(y - w / 2)), im2)


# ---------------- 一句花字 ----------------
class Line:
    def __init__(self, t0, t1, text, pal='white', kw=None, kwpal='pink', size=120, cx=960, cy=830, angle=0.0, deco=(), kwscale=1.3, stagger=0.05,
                 pop=1.28, float_amp=5, shake=0, beat_kick=0.08):
        """动效随曲风调：pop 入场回弹（抒情 1.08、默认 1.28、燃 1.45），stagger 逐字间隔（快歌 0.03、慢歌 0.09），
        float_amp 漂浮幅度，shake 抖动像素（摇滚/说唱 4–8），beat_kick 重点词随鼓点放大比例。"""
        self.t0, self.t1, self.text = t0, t1, text
        self.pal, self.kw, self.kwpal, self.size = pal, kw or [], kwpal, size
        self.cx, self.cy, self.angle, self.deco = cx, cy, angle, deco
        self.kwscale, self.stagger = kwscale, stagger
        self.pop, self.float_amp, self.shake, self.beat_kick = pop, float_amp, shake, beat_kick
        self._layout()

    def _layout(self):
        rows = self.text.split('/')
        items = []
        hit = set()
        for k in self.kw:
            pos = self.text.replace('/', '').find(k)
            if pos >= 0:
                hit.update(range(pos, pos + len(k)))
        gi = 0
        rh = []
        lay = []
        for r, row in enumerate(rows):
            xs = []
            x = 0
            maxs = 0
            for ch in row:
                iskw = gi in hit
                sz = int(self.size * (self.kwscale if iskw else 1.0))
                pal = self.kwpal if iskw else self.pal
                if ch == ' ':
                    adv = self.size * 0.32
                    xs.append((None, x, sz, pal, iskw, gi))
                else:
                    _, _, adv = char_sprite(ch, sz, pal, 0.0)
                    adv = adv * 1.0 + sz * 0.04
                    xs.append((ch, x + adv / 2, sz, pal, iskw, gi))
                x += adv
                maxs = max(maxs, sz)
                gi += 1
            lay.append((xs, x, maxs))
        total_h = sum(m * 1.08 for _, _, m in lay)
        y = -total_h / 2
        ca, sa = math.cos(math.radians(-self.angle)), math.sin(math.radians(-self.angle))
        for xs, wrow, maxs in lay:
            yc = y + maxs * 0.54
            for ch, xc, sz, pal, iskw, g in xs:
                if ch is None:
                    continue
                lx = xc - wrow / 2
                ly = yc + (maxs - sz) * 0.35
                items.append(dict(ch=ch, x=self.cx + lx * ca - ly * sa, y=self.cy + lx * sa + ly * ca, size=sz, pal=pal, kw=iskw, i=g))
            y += maxs * 1.08
        self.items = items
        self.n = gi
        xs_ = [it['x'] for it in items]; ys_ = [it['y'] for it in items]
        self.bbox = (min(xs_) - self.size * 0.6, min(ys_) - self.size * 0.7, max(xs_) + self.size * 0.6, max(ys_) + self.size * 0.6)

    def draw(self, base, t, beat_phase=0.0):
        if t < self.t0 - 0.05 or t > self.t1 + 0.05:
            return
        out = clamp((t - (self.t1 - 0.2)) / 0.2)
        todo = []
        for it in self.items:
            born = self.t0 + it['i'] * self.stagger
            p = (t - born) / 0.24
            if p <= 0:
                continue
            if p < 0.55:
                sc = ease(p / 0.55) * self.pop
            elif p < 1:
                sc = self.pop - (self.pop - 1) * ease((p - 0.55) / 0.45)
            else:
                sc = 1.0
                if it['kw']:
                    sc += self.beat_kick * math.exp(-beat_phase * 6)
            sc *= 1 - ease(out)
            if sc <= 0.02:
                continue
            back, front, _ = char_sprite(it['ch'], it['size'], it['pal'], round(self.angle))
            fl = math.sin(t * 2.4 + it['i'] * 0.7) * self.float_amp
            if self.shake:
                fl += (hsh(int(t * 24), it['i']) - 0.5) * 2 * self.shake
            dy = -(1 - clamp(p)) * it['size'] * 0.35 + fl - out * 40
            if abs(sc - 1) > 0.01:
                sz = (max(1, int(back.width * sc)), max(1, int(back.height * sc)))
                back, front = back.resize(sz, Image.BICUBIC), front.resize(sz, Image.BICUBIC)
            pos = (int(it['x'] - back.width / 2), int(it['y'] - back.height / 2 + dy))
            todo.append((back, front, pos))
        for back, _, pos in todo:
            base.paste(back, pos, back)
        for _, front, pos in todo:
            base.paste(front, pos, front)
        # 贴纸
        if out < 1:
            x0, y0, x1, y1 = self.bbox
            spots = [(x1 + 20, y0 + 10), (x0 - 20, y1 - 30), (x1 - 10, y1 + 10), (x0 + 10, y0 - 10)]
            for k, kind in enumerate(self.deco):
                sx, sy = spots[k % len(spots)]
                if kind == 'horn' and self.kw:
                    kwit = [it for it in self.items if it['kw']]
                    sx, sy = kwit[0]['x'], kwit[0]['y'] - kwit[0]['size'] * 0.85
                sx = min(FW - 70, max(70, sx)); sy = min(FH - 120, max(70, sy))
                if out > 0:
                    continue
                draw_sticker(base, kind, sx, sy, 70 if kind != 'horn' else 60, t, self.t0 + 0.25 + k * 0.12, seed=k)


def pill(base, cx, cy, text, size=60, fg=(255, 255, 255), bg=(40, 20, 60), edge=(255, 110, 170), fam='zcool-kuaile', alpha=1.0):
    f = font(text[0], size, fam)
    w = sum(font(c, size, fam).getlength(c) for c in text)
    pw, ph = int(w + size * 1.0), int(size * 1.5)
    im = Image.new('RGBA', (pw + 12, ph + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, pw + 6, ph + 6], radius=ph // 2, fill=(*bg, 235), outline=edge, width=max(4, size // 10))
    x = 6 + size * 0.5
    for c in text:
        fc = font(c, size, fam)
        d.text((x, 6 + ph / 2), c, font=fc, fill=fg, anchor='lm')
        x += fc.getlength(c)
    if alpha < 1:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im.putalpha(a)
    base.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


@lru_cache(None)
def signature(text='@张景行', size=46):
    f0 = font(text[1], size, 'zcool-kuaile')
    w = int(sum(font(c, size, 'zcool-kuaile').getlength(c) for c in text)) + 40
    im = Image.new('RGBA', (w, size + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 20
    for c in text:
        fc = font(c, size, 'zcool-kuaile')
        d.text((x, 15), c, font=fc, fill=(255, 255, 255), stroke_width=5, stroke_fill=(40, 20, 60), anchor='la')
        x += fc.getlength(c)
    return im
