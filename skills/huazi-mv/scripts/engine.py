# -*- coding: utf-8 -*-
"""综艺花字 MV 渲染引擎（skia，1920x1080@30）。

每首歌一个项目目录，里面放 config.py（歌词、段落、配色、天气、标签……）和 audio.json（analyze_audio.py 生成）。
用法：
  python engine.py <项目目录> preview <输出目录> 秒 秒 …
  python engine.py <项目目录> chunk <起始帧> <结束帧> <输出.mp4> <crf>
（整片渲染用 render_all.py，它会并行调用 chunk 再合成音频。）
"""
import skia, numpy as np, json, math, os, sys, subprocess, cv2, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import huazi as hz

W, H, FPS = 1920, 1080, 30
PROJ = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.environ.get('HZMV_PROJECT', '.')
_spec = importlib.util.spec_from_file_location('mvconfig', os.path.join(PROJ, 'config.py'))
CFG = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(CFG)
A = json.load(open(os.path.join(PROJ, 'audio.json')))
LOW = np.array(A['low']); HIGH = np.array(A['high']); ONS = np.array(A['onset'])
BEATS = np.array(A['main_beats'])
AUDIO_END = float(getattr(CFG, 'AUDIO_END', A['dur']))
TOTAL = float(getattr(CFG, 'TOTAL', AUDIO_END + 2.5))
NFRAMES = int(TOTAL * FPS)
def C(name, default=None): return getattr(CFG, name, default)
LINES = CFG.LINES
for _k, _v in (C('EXTRA_SCHEMES') or {}).items():
    hz.SCH[_k] = hz.scheme(*_v)
CHAPTERS = C('CHAPTERS', [])

def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def smooth(t): t = clamp(t); return t * t * (3 - 2 * t)
def eo3(t): t = clamp(t); return 1 - (1 - t) ** 3
def eio(t): t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def eback(t, s=1.6):
    t = clamp(t); return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2
def hx(s): s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
def mixc(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))
def lum(c): return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def C4(c, a=1.): return skia.Color4f(c[0], c[1], c[2], clamp(a))
def CI(c, a=1.): return skia.Color(int(clamp(c[0]) * 255), int(clamp(c[1]) * 255), int(clamp(c[2]) * 255), int(clamp(a) * 255))
def env(arr, t):
    i = int(t * FPS); return float(arr[i]) if 0 <= i < len(arr) else 0.
def pulse(t, decay=.22):
    i = np.searchsorted(BEATS, t) - 1
    if i < 0: return 0.
    return math.exp(-(t - BEATS[i]) / decay)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            u = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1
            if isinstance(v0, tuple): return mixc(v0, v1, u)
            return lerp(v0, v1, u)
    return keys[-1][1]

def paint(c=(0, 0, 0), a=1., stroke=None, blur=0., aa=True):
    p = skia.Paint(AntiAlias=aa)
    p.setColor4f(C4(c, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur > .25: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

# ---------------------------------------------------------------- fonts
FD = os.environ.get('HZMV_FONTS', os.path.expanduser('~/.cache/huazi-mv/fonts'))
_tf = {}
def tf_var(path, wght):
    k = (path, wght)
    if k not in _tf:
        base = skia.Typeface.MakeFromFile(path)
        if wght is None: _tf[k] = base
        else:
            Co = skia.FontArguments.VariationPosition.Coordinate
            tag = (ord('w') << 24) | (ord('g') << 16) | (ord('h') << 8) | ord('t')
            vp = skia.FontArguments.VariationPosition(skia.FontArguments.VariationPosition.Coordinates([Co(tag, wght)]))
            fa = skia.FontArguments(); fa.setVariationDesignPosition(vp)
            _tf[k] = base.makeClone(fa)
    return _tf[k]
def TF(name):
    return {
        's3': lambda: tf_var(f'{FD}/NotoSerifSC[wght].ttf', 300),
        's4': lambda: tf_var(f'{FD}/NotoSerifSC[wght].ttf', 400),
        's6': lambda: tf_var(f'{FD}/NotoSerifSC[wght].ttf', 600),
        's9': lambda: tf_var(f'{FD}/NotoSerifSC[wght].ttf', 900),
        'kl': lambda: tf_var(f'{FD}/ZCOOLKuaiLe-Regular.ttf', None),
        'sb': lambda: tf_var(f'{FD}/NotoSansSC[wght].ttf', 900),
        'ci': lambda: tf_var(f'{FD}/CormorantGaramond-Italic[wght].ttf', 500),
        'cr': lambda: tf_var(f'{FD}/CormorantGaramond[wght].ttf', 500),
    }[name]()
_fc = {}
def F(name, size):
    k = (name, round(size * 2) / 2)
    if k not in _fc:
        f = skia.Font(TF(name), k[1]); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
        f.setHinting(skia.FontHinting.kNone); _fc[k] = f
    return _fc[k]

def text_w(s, font, track=0.):
    return sum(font.measureText(ch) for ch in s) + track * max(0, len(s) - 1)

def draw_text(c, s, x, y, font, col, a, track=0., align='c', blur=0.):
    """Draw string with tracking; y is optical centre line."""
    if a <= .003: return
    m = font.getMetrics(); base = y - (m.fAscent + m.fDescent) / 2
    w = text_w(s, font, track)
    cx = x - w / 2 if align == 'c' else (x if align == 'l' else x - w)
    p = paint(col, a, blur=blur)
    for ch in s:
        c.drawString(ch, cx, base, font, p)
        cx += font.measureText(ch) + track

def glyph(c, ch, x, y, font, col, a, blur=0., rot=0., sc=1., skew=0., glow=0., glowcol=None):
    if a <= .003: return
    m = font.getMetrics(); w = font.measureText(ch)
    base = -(m.fAscent + m.fDescent) / 2
    c.save(); c.translate(x, y)
    if rot: c.rotate(rot)
    if sc != 1: c.scale(sc, sc)
    if skew: c.skew(skew, 0)
    if glow > .01:
        c.drawString(ch, -w / 2, base, font, paint(glowcol or col, a * glow, blur=font.getSize() * .16))
    c.drawString(ch, -w / 2, base, font, paint(col, a, blur=blur))
    c.restore()

# ---------------------------------------------------------------- palettes & world keys
P = lambda top, bot, ink, acc='#E8AE12': (hx(top), hx(bot), hx(ink), hx(acc))
PAPER = P('#EEE7D9', '#F7F2E8', '#2A2521')
MEMORY = P('#EDE0C8', '#F4EAD8', '#3A2D24')
MIST = P('#C4CBCE', '#DCDFDC', '#28323A')
STORM = P('#121C24', '#26343E', '#E9EEF0', '#F2BD2C')
AFTER = P('#D3DCDF', '#ECEEE8', '#2A363D')
DUSK = P('#EBC49A', '#F7E6CF', '#3B271C', '#D98E0B')
NIGHT = P('#0C1218', '#1B2730', '#EEF2F4', '#F2BD2C')
CLEAR = P('#6FB3E0', '#F5EED8', '#12304A', '#E9A90E')
PALETTES = {'paper': PAPER, 'memory': MEMORY, 'mist': MIST, 'storm': STORM, 'after': AFTER, 'dusk': DUSK,
            'night': NIGHT, 'clear': CLEAR}
for _k, _v in (C('EXTRA_PALETTES') or {}).items():
    PALETTES[_k] = P(*_v)
PAL_KEYS = [(t_, PALETTES[n_]) for t_, n_ in C('PAL_KEYS', [(0, 'paper')])] + [(1e9, None)]
PAL_KEYS[-1] = (1e9, PAL_KEYS[-2][1])
def palette(t):
    for (t0, p0), (t1, p1) in zip(PAL_KEYS, PAL_KEYS[1:]):
        if t < t1:
            u = smooth((t - t0) / (t1 - t0))
            return tuple(mixc(a, b, u) for a, b in zip(p0, p1))
    return PAL_KEYS[-1][1]

_z = [(0, 0), (1e9, 0)]
RAIN_K = C('RAIN_K', _z); WIND_K = C('WIND_K', [(0, .08), (1e9, .08)]); SUN_K = C('SUN_K', _z)
GLASS_K = C('GLASS_K', _z); CLOUD_K = C('CLOUD_K', [(0, .12), (1e9, .12)])
LIGHTNING = C('LIGHTNING', [])
FLASHES = C('FLASHES', [])
CHORUS = C('CHORUS', [])

# ---------------------------------------------------------------- precomputed textures / particles
RNG = np.random.default_rng(7)
def np_img(arr):
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType,
                                alphaType=skia.kUnpremul_AlphaType)

def make_textures():
    T = {}
    r = np.random.default_rng(11)
    # paper fibre (static, multiply)
    n = r.random((H // 2, W // 2)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 1.2) * .6 + cv2.GaussianBlur(r.random((H // 2, W // 2)).astype(np.float32), (0, 0), 6) * .4
    n = (n - n.min()) / (n.max() - n.min())
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
    a = np.zeros((H, W, 4), np.uint8); a[..., :3] = (n * 255)[..., None].astype(np.uint8); a[..., 3] = 255
    T['paper'] = np_img(a)
    # animated grain (overlay)
    T['grain'] = []
    for k in range(6):
        g = r.normal(.5, .18, (H // 2, W // 2)).clip(0, 1).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)
        a = np.zeros((H, W, 4), np.uint8); a[..., :3] = (g * 255)[..., None].astype(np.uint8); a[..., 3] = 255
        T['grain'].append(np_img(a))
    # clouds (alpha masks)
    T['clouds'] = []
    for k in range(6):
        cw, ch = 1100, 420
        m = np.zeros((ch, cw), np.float32)
        for j in range(26):
            x = r.uniform(.15, .85) * cw; y = r.uniform(.35, .7) * ch
            rad = r.uniform(50, 150) * (1 - abs(x / cw - .5))
            cv2.circle(m, (int(x), int(y)), int(rad), 1., -1)
        m = cv2.GaussianBlur(m, (0, 0), 38); m = m / max(m.max(), 1e-3)
        m = np.clip(m * 1.3, 0, 1) ** 1.3
        a = np.zeros((ch, cw, 4), np.uint8); a[..., :3] = 255; a[..., 3] = (m * 255).astype(np.uint8)
        T['clouds'].append(np_img(a))
    # glass droplets
    s = skia.Surface(W, H); c = s.getCanvas(); c.clear(skia.ColorTRANSPARENT)
    for j in range(420):
        x = r.uniform(0, W); y = r.uniform(0, H); rad = r.uniform(1.5, 8) ** 1.1
        c.drawCircle(x, y, rad, paint((1, 1, 1), .07))
        c.drawCircle(x, y + rad * .15, rad, paint((0, 0, 0), .10, stroke=max(.8, rad * .22)))
        c.drawCircle(x - rad * .3, y - rad * .35, rad * .28, paint((1, 1, 1), .55, blur=.4))
    T['glass'] = s.makeImageSnapshot()
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2)
    v = np.clip((d - .55) / .75, 0, 1) ** 1.6
    a = np.zeros((H, W, 4), np.uint8); a[..., 3] = (v * 255).astype(np.uint8)
    T['vig'] = np_img(a)
    return T

# rain streaks
NR = 620
RAIN = dict(x=RNG.uniform(-500, W + 300, NR), sp=RNG.uniform(1500, 2400, NR), ln=RNG.uniform(50, 130, NR),
            ph=RNG.uniform(0, 5000, NR), z=RNG.uniform(.25, 1., NR), ord=RNG.permutation(NR))
# dust motes
ND = 60
DUST = dict(x=RNG.uniform(0, W, ND), y=RNG.uniform(0, H, ND), r=RNG.uniform(1.2, 4.5, ND), vx=RNG.uniform(-8, 14, ND),
            vy=RNG.uniform(-14, -3, ND), ph=RNG.uniform(0, 6.28, ND))
# sliding drops on glass
NS = 16
SLIDE = dict(x=RNG.uniform(60, W - 60, NS), sp=RNG.uniform(30, 110, NS), ph=RNG.uniform(0, H, NS), r=RNG.uniform(4, 9, NS))
# field flowers for the clear sky
NF = 34
FIELD = []
for i in range(NF):
    x = (i + RNG.uniform(.1, .9)) / NF * (W + 120) - 60
    FIELD.append(dict(x=x, y=RNG.uniform(985, 1070), s=RNG.uniform(.35, .75), d=abs(x - W / 2) / W * 1.8 + RNG.uniform(0, .3),
                      ph=RNG.uniform(0, 6.28), stem=RNG.uniform(40, 120), rot=RNG.uniform(-20, 20)))

# petal emitters: (t0, t1, rate per s, region, mode)
PETAL_EMIT = C('PETAL_EMIT', [])
PETALS = []
for (a, b, rate, reg, mode) in PETAL_EMIT:
    n = int((b - a) * rate)
    for k in range(n):
        PETALS.append(dict(t=a + (b - a) * RNG.random(), reg=reg, mode=mode, u=RNG.random(), v=RNG.random(),
                           s=RNG.uniform(.6, 1.3), sp=RNG.uniform(.7, 1.3), ph=RNG.uniform(0, 6.28),
                           rs=RNG.uniform(-200, 200)))

# ---------------------------------------------------------------- scene elements
def draw_background(c, t, pal, T, S, cloud, wind):
    top, bot, ink, acc = pal
    p = skia.Paint()
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [CI(top), CI(bot)]))
    c.drawRect(skia.Rect.MakeWH(W, H), p)
    # sun / warm light
    if S > .01:
        _disc = C('SUN_DISC_FROM'); _on = _disc is not None and t > _disc
        sx, sy = W * .74, H * (.2 if _on else .12)
        warm = hx('#FFF6DD') if _on else hx('#FFE2A6')
        g = skia.Paint(); g.setBlendMode(skia.BlendMode.kScreen)
        g.setShader(skia.GradientShader.MakeRadial(skia.Point(sx, sy), 1000,
                    [CI(warm, (.55 if lum(top) > .4 else .8) * S), CI(warm, .18 * S), CI(warm, 0)], [0, .35, 1]))
        c.drawRect(skia.Rect.MakeWH(W, H), g)
        if _on and S > .3:  # god rays + sun disc
            c.save(); c.translate(sx, sy)
            for k in range(11):
                ang = k * 32.7 + t * 1.8
                c.save(); c.rotate(ang)
                path = skia.Path(); path.moveTo(0, 0); path.lineTo(2400, -70 - 40 * (k % 3)); path.lineTo(2400, 70 + 40 * (k % 2)); path.close()
                rp = paint(warm, .045 * S * (0.6 + .4 * math.sin(t * .7 + k)), blur=12); rp.setBlendMode(skia.BlendMode.kScreen)
                c.drawPath(path, rp)
                c.restore()
            c.drawCircle(0, 0, 150, paint(warm, .35 * S, blur=60))
            c.drawCircle(0, 0, 64, paint((1, .99, .95), .95 * S, blur=1.5))
            c.restore()
    # clouds
    if cloud > .01:
        bl = lum(top)
        cc = mixc(mixc(top, bot, .5), (1, 1, 1), .55 if bl > .45 else .10)
        for k, img in enumerate(T['clouds']):
            v = 14 + 9 * k
            span = W + 1400
            x = ((k * 517 + t * v * (1 + 2.5 * wind)) % span) - 1100
            y = -120 + 70 * (k % 3) + (k // 3) * 140
            cp = skia.Paint(); cp.setColorFilter(skia.ColorFilters.Blend(CI(cc), skia.BlendMode.kSrcIn))
            cp.setAlphaf(clamp(cloud * (.55 + .12 * (k % 3)) * (.85 if bl < .45 else .4)))
            c.drawImage(img, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), cp)

def draw_dust(c, t, pal, amt):
    if amt < .01: return
    top, bot, ink, acc = pal
    col = (1, .97, .88) if lum(top) > .45 else (1, 1, 1)
    for i in range(ND):
        x = (DUST['x'][i] + t * DUST['vx'][i] + 30 * math.sin(t * .3 + DUST['ph'][i])) % W
        y = (DUST['y'][i] + t * DUST['vy'][i]) % H
        tw = .5 + .5 * math.sin(t * 1.3 + DUST['ph'][i] * 3)
        c.drawCircle(x, y, DUST['r'][i] * 2.2, paint(col, amt * .22 * tw, blur=DUST['r'][i] * 1.4))

def draw_rain(c, t, pal, R, wind, near):
    if R < .01: return
    top, bot, ink, acc = pal
    dark = lum(top) < .4
    col = (.86, .92, .97) if dark else (.25, .30, .34)
    slant = .12 + .55 * wind
    n = int(NR * R)
    idx = RAIN['ord'][:n]
    nrm = 1 / math.sqrt(1 + slant * slant)
    paths = {}
    for i in idx:
        z = RAIN['z'][i]
        if (z > .62) != near: continue
        yy = (RAIN['ph'][i] + t * RAIN['sp'][i] * (.6 + .5 * z)) % (H + 300) - 150
        x = RAIN['x'][i] + yy * slant + t * 90 * wind
        x = (x + 600) % (W + 900) - 450
        L = RAIN['ln'][i] * (.5 + .7 * z)
        a = (.10 + .30 * z) * (1 if dark else .75)
        key = round(a, 2), round(.6 + 1.4 * z, 1)
        pth = paths.setdefault(key, skia.Path())
        pth.moveTo(x, yy); pth.lineTo(x - slant * L * nrm, yy - L * nrm)
    for (a, wdt), pth in paths.items():
        c.drawPath(pth, paint(col, a * min(1, .5 + R), stroke=wdt))

def draw_glass(c, t, T, G, pal):
    if G < .01: return
    gp = skia.Paint(); gp.setAlphaf(G * .9)
    c.drawImage(T['glass'], 0, 0, skia.SamplingOptions(), gp)
    for i in range(NS):
        y = (SLIDE['ph'][i] + t * SLIDE['sp'][i]) % (H + 200) - 100
        x = SLIDE['x'][i] + 6 * math.sin(y * .02 + i)
        r = SLIDE['r'][i]
        c.drawLine(x, y - 180, x, y - r, paint((1, 1, 1), .05 * G, stroke=r * .7))
        c.drawCircle(x, y, r, paint((1, 1, 1), .10 * G))
        c.drawCircle(x, y + r * .2, r, paint((0, 0, 0), .14 * G, stroke=r * .25))
        c.drawCircle(x - r * .3, y - r * .35, r * .3, paint((1, 1, 1), .6 * G))

def petal_path(s):
    p = skia.Path()
    p.moveTo(0, 0); p.cubicTo(-14 * s, -18 * s, -12 * s, -46 * s, 0, -56 * s)
    p.cubicTo(12 * s, -46 * s, 14 * s, -18 * s, 0, 0); p.close()
    return p

def draw_flower(c, x, y, s, bloom, col, center, a=1., petals=5, missing=(), rot=0., stem=0., stemcol=None, inkcol=None):
    if a < .01: return
    if stem > 1:
        sp = skia.Paint(AntiAlias=True); sp.setStyle(skia.Paint.kStroke_Style); sp.setStrokeWidth(2.2 * max(s, .5))
        sc = stemcol
        sp.setShader(skia.GradientShader.MakeLinear([skia.Point(x, y), skia.Point(x, y + stem)], [CI(sc, a * .9), CI(sc, 0)]))
        path = skia.Path(); path.moveTo(x, y); path.cubicTo(x + 6 * s, y + stem * .35, x - 10 * s, y + stem * .7, x - 4 * s, y + stem)
        c.drawPath(path, sp)
    c.save(); c.translate(x, y); c.rotate(rot)
    if bloom < .02:
        c.drawCircle(0, 0, 13 * s, paint(col, a))
        c.drawCircle(-3 * s, -4 * s, 4 * s, paint((1, 1, 1), .35 * a, blur=1.5))
    else:
        b = eback(bloom, 1.2)
        for k in range(petals):
            if k in missing: continue
            c.save(); c.rotate(k * 360 / petals + 8 * math.sin(k)); c.scale(b, b)
            pp = petal_path(s)
            c.drawPath(pp, paint(col, a))
            c.drawPath(pp, paint(mixc(col, (1, 1, 1), .35), .35 * a, stroke=1.0))
            c.restore()
        c.drawCircle(0, 0, 10 * s * (.6 + .4 * b), paint(center, a))
        for k in range(7):
            ang = k * 51.4 * math.pi / 180
            c.drawCircle(math.cos(ang) * 5 * s, math.sin(ang) * 5 * s, 1.6 * s, paint(mixc(center, (0, 0, 0), .3), a * .8))
    c.restore()

FLOWER_COL = hx('#F2C028'); FLOWER_CEN = hx('#B9770A')

E = sys.modules[__name__]

def scene_hook(c, t, pal, wind, name):
    """config.py 里可选的 scene(c, t, pal, ctx, E) / scene_over(...)：画这首歌专属的母题（小黄花、纸飞机、星星……）。
    E 是本引擎模块，里面的画图工具都能用：E.draw_flower、E.paint、E.eo3、E.pulse、E.BEATS、E.field_flowers ……"""
    fn = getattr(CFG, name, None)
    if fn:
        fn(c, t, pal, dict(wind=wind), E)


def field_flowers(c, t, start, wilt_start=None, wind=0.0, stemcol=None, col=None, cen=None):
    """底部一排花田：start 起从中间往两边依次开；wilt_start 起花瓣逐渐掉光"""
    stemcol = stemcol or (0.4, 0.48, 0.3)
    for f in FIELD:
        b = eo3((t - start - f['d'] * 1.3) / 1.1)
        if b <= 0: continue
        wilt = smooth((t - wilt_start - f['d']) / 5) if wilt_start is not None else 0
        sw = (6 + 22 * wind) * math.sin(t * 2 + f['ph'])
        x, y = f['x'] + sw * .4, f['y'] - f['stem'] * b * .2
        lost = tuple(k for k in range(5) if (k * 0.21 + f['ph'] % 1) % 1 < wilt)
        draw_flower(c, x, y, f['s'], b, col or FLOWER_COL, cen or FLOWER_CEN, 1, missing=lost, rot=sw + f['rot'],
                    stem=f['stem'], stemcol=stemcol)


def ripples(c, t, cx, cy, col, t0, t1):
    """踩主拍从 (cx, cy) 扩散的水波纹（透视椭圆）"""
    i = np.searchsorted(BEATS, t) - 1
    for j in range(3):
        if i - j < 0: break
        dt = t - BEATS[i - j]
        r = 30 + dt * 260
        aa = .35 * (1 - clamp(dt / 2.4)) * smooth((t - t0) / 1.5) * (1 - smooth((t - t1 + 1.5) / 1.5))
        c.drawOval(skia.Rect.MakeXYWH(cx - r, cy - r * .16, 2 * r, 2 * r * .32), paint(col, aa, stroke=1.3))


def beat_notes(c, t, t_from, fade=1.0):
    """跟着主拍从底部飘起的音符贴纸"""
    i = np.searchsorted(BEATS, t) - 1
    for j in range(6):
        k = i - j
        if k < 0: break
        bt = BEATS[k]
        if bt < t_from: continue
        dt = t - bt
        if dt > 2.6: continue
        x = 420 + ((k * 397) % 1080); y = 900 - dt * 210
        a = (1 - smooth((dt - 1.8) / .8)) * smooth(dt * 5) * fade
        col = hz._hx('#FF7A1A') if k % 2 else hz._hx('#1E63B8')
        c.save(); c.translate(x + 14 * math.sin(dt * 3 + k), y); c.rotate(-12 + 8 * math.sin(dt * 2 + k))
        c.drawOval(skia.Rect.MakeXYWH(-17, -12, 34, 24), paint((1, 1, 1), a))
        c.drawOval(skia.Rect.MakeXYWH(-13, -9, 26, 18), paint(col, a))
        c.drawLine(11, -2, 11, -62, paint((1, 1, 1), a, stroke=9))
        c.drawLine(11, -2, 11, -62, paint(col, a, stroke=4.5))
        fl = skia.Path(); fl.moveTo(11, -62); fl.cubicTo(30, -52, 34, -38, 24, -26)
        c.drawPath(fl, paint((1, 1, 1), a, stroke=9)); c.drawPath(fl, paint(col, a, stroke=4.5))
        c.restore()


def badges(c, t, pal):
    """BADGES：没有歌词的段落（间奏、solo）里的大号综艺标签，可带踩拍音符"""
    for b in C('BADGES', []):
        t0, t1 = b['t0'], b['t1']
        if not (t0 - .1 < t < t1 + .9): continue
        pt = clamp((t - t0 - .3) / .45); out = smooth((t - t1) / .8)
        if pt > 0:
            bp = pulse(t, .2)
            hz.tag(c, b['text'], 960, b.get('y', 330) + 6 * math.sin(t * 3), F('kl', b.get('size', 64)),
                   hz.SCH[b.get('scheme', 'kw_sun')]['outer'], min(1, pt * 3) * (1 - out),
                   rot=-5 + 3 * math.sin(t * 2.6), sc=eback(pt, 2.6) * (1 + .07 * bp))
        if b.get('notes'):
            beat_notes(c, t, t0 + .5, 1 - out)

def draw_petals(c, t, wind):
    for p in PETALS:
        dt = t - p['t']
        if dt < 0 or dt > 7: continue
        if p['mode'] == 'fall':
            if p['reg'] == 'flower': x0, y0 = 960 + (p['u'] - .5) * 60, 400
            else: x0, y0 = p['u'] * W, -40
            x = x0 + 70 * math.sin(dt * 1.6 * p['sp'] + p['ph']) + dt * 40 * wind
            y = y0 + dt * 150 * p['sp']
            a = 1 - smooth((dt - 5) / 2)
        elif p['mode'] == 'drift':
            x0, y0 = -40, p['v'] * H * .8 + 100
            x = x0 + dt * 380 * p['sp']; y = y0 - dt * 40 + 40 * math.sin(dt * 2 + p['ph'])
            a = 1 - smooth((dt - 4) / 2)
        else:  # blow from the field
            x0, y0 = p['u'] * W, 1000 + p['v'] * 60
            x = x0 + dt * (260 + 300 * wind) * p['sp']; y = y0 - dt * (90 + 60 * p['v']) + 30 * math.sin(dt * 2.5 + p['ph'])
            a = smooth(dt * 3) * (1 - smooth((dt - 4) / 2.5))
        if not (-80 < x < W + 80 and -80 < y < H + 80): continue
        c.save(); c.translate(x, y); c.rotate(p['ph'] * 57 + dt * p['rs']); c.scale(p['s'] * .55, p['s'] * .55 * (.6 + .4 * abs(math.sin(dt * 3 + p['ph']))))
        c.drawPath(petal_path(1), paint(FLOWER_COL, .92 * a))
        c.restore()

# ---------------------------------------------------------------- lyrics
def line_window(i):
    L = LINES[i]; nxt = LINES[i + 1]['t0'] if i + 1 < len(LINES) else 999
    end = min(nxt + .25, L['t1'] + L.get('hold', 1.0)) if not L.get('keep') else L['t1'] + L.get('hold', 1.0)
    end = max(end, L['t1'] + .15)
    return L['t0'] - .2, end

def char_times(L):
    s = L['text']; n = len(s)
    if 'seg' in L:
        out = []
        for cnt, a, b in L['seg']:
            out += [a + (b - a) * k / cnt for k in range(cnt)]
        return out
    dur = L['t1'] - L['t0']
    span = min(dur * .72, n * .34)
    return [L['t0'] + span * k / n for k in range(n)]

def fontspec(L):
    """字体：主歌（sec='v'）站酷快乐体，副歌（sec='c'）思源黑体 Black；行里写 font / size / track 可覆盖"""
    st = L['style']
    if st == 'vert': f, sz, tr = 'kl', 84, 0
    elif L.get('sec') == 'v': f, sz, tr = 'kl', 104, 10
    elif st == 'rainheavy': f, sz, tr = 'sb', 128, 12
    elif st == 'clear': f, sz, tr = 'sb', 150, 14
    else: f, sz, tr = 'sb', 104, 10
    return (L.get('font', f), L.get('size', sz), L.get('track', tr))

SCHEMES = C('SCHEMES', [(0, 'memory')])
def sec_scheme(t0):
    cur = SCHEMES[0][1]
    for a, name in SCHEMES:
        if t0 >= a: cur = name
    return cur

KW = C('KW', {})
def kw_schemes(L):
    s = L['text']; out = [None] * len(s)
    for w in L.get('acc', []):
        k = s.find(w)
        while k >= 0:
            for j in range(k, k + len(w)): out[j] = hz.SCH[KW.get(w, 'kw_sun')]
            k = s.find(w, k + len(w))
    return out

def accent_mask(L):
    s = L['text']; m = [False] * len(s)
    for w in L.get('acc', []):
        k = s.find(w)
        if k >= 0:
            for j in range(k, k + len(w)): m[j] = True
    return m

def english(c, L, t, y, pal, a):
    return
    if not L.get('en') or a < .01: return
    top, bot, ink, acc = pal
    u = eo3((t - L['t0'] - .35) / .9)
    draw_text(c, L['en'], 960, y + 10 * (1 - u), F('ci', 34), ink, a * u * .62, track=1.2, blur=(1 - u) * 4)

def draw_line(c, i, t, pal, ctx):
    L = LINES[i]; st = L['style']
    ws, we = line_window(i)
    if not (ws <= t <= we): return
    top, bot, ink, acc = pal
    dark = lum(top) < .4
    fname, size, track = fontspec(L)
    font = F(fname, size)
    s = L['text']; n = len(s)
    ct = char_times(L); am = accent_mask(L)
    q = smooth((t - (we - .6)) / .6)            # exit
    lineA = 1 - q
    ex_y = -16 * q
    wind = ctx['wind']; bp = ctx['bp']
    # base layout
    widths = [font.measureText(ch) for ch in s]
    total = sum(widths) + track * (n - 1)
    cy = L.get('y', 540)
    if st == 'bloom': cy = 790
    if st == 'sky': cy = 330
    if st == 'float': cy = 560 - 50 * eio((t - L['t0']) / (we - L['t0']))
    xs = []; x = 960 - total / 2
    for w in widths: xs.append(x + w / 2); x += w + track
    pos = [[xs[k], cy] for k in range(n)]
    vertical = st == 'vert'
    if vertical:
        col_x = L['col']; y0 = 196
        pos = [[col_x, y0 + k * size * 1.2 + size / 2] for k in range(n)]

    # ---- style decorations (under text)
    if st == 'swing':
        th = ctx['swing']
        c.save(); c.rotate(th, 960, -300)
        ra = lineA * eo3((t - L['t0'] + .2) / .8)
        hw = max(total / 2 + 40, 360)
        for sx in (-hw, hw):
            c.drawLine(960 + sx, -300, 960 + sx, cy + size * .62, paint(ink, .55 * ra, stroke=1.6))
        c.drawLine(960 - hw - 14, cy + size * .62, 960 + hw + 14, cy + size * .62, paint(ink, .8 * ra, stroke=3))
    if st == 'window':
        wa = lineA
        tr = eo3((t - L['t0'] + .2) / 1.0)
        fr = skia.Rect.MakeXYWH(960 - 780, 540 - 260, 1560, 520)
        wp = paint(ink, .5 * wa, stroke=2.4)
        if tr < .999:
            pe = skia.TrimPathEffect.Make(0, max(tr, .001))
            if pe is not None: wp.setPathEffect(pe)
        path = skia.Path(); path.addRect(fr); c.drawPath(path, wp)
        mp = skia.Path(); mp.moveTo(960, 280); mp.lineTo(960, 800); mp.moveTo(180, 410); mp.lineTo(1740, 410)
        c.drawPath(mp, wp)
        cy2 = 600
        for k in range(n): pos[k][1] = cy2
    if st == 'storybook':
        u = eo3((t - L['t0']) / 1.6)
        hw = total / 2 + 60
        for sgn in (-1, 1):
            x0 = 960 + sgn * hw; x1 = 960 + sgn * (hw + 220 * u)
            c.drawLine(x0, cy, x1, cy, paint(ink, .45 * lineA, stroke=1.2))
            c.save(); c.translate(x1 + sgn * 10, cy); c.rotate(45)
            c.drawRect(skia.Rect.MakeXYWH(-5, -5, 10, 10), paint(acc, lineA * u)); c.restore()
    if st == 'distance':
        u = eio((t - L['t0']) / (L['t1'] - L['t0'] + .5))
        lx = lerp(520, 905, u); rx = 1400
        ya = 800
        da = lineA * smooth((t - L['t0'] + .2) / .6)
        dp = paint(ink, .28 * da, stroke=1.2); dp.setPathEffect(skia.DashPathEffect.Make([6, 10], t * 20))
        pth = skia.Path(); pth.moveTo(lx + 16, ya); pth.lineTo(rx - 16, ya); c.drawPath(pth, dp)
        c.drawCircle(lx, ya, 9, paint(ink, da)); c.drawCircle(lx, ya, 22, paint(ink, .15 * da, blur=8))
        c.drawCircle(rx, ya, 9, paint(acc, da)); c.drawCircle(rx, ya, 26, paint(acc, .3 * da, blur=10))

    # ---- glyphs (综艺花字)
    sch_line = hz.SCH[sec_scheme(L['t0'])]
    kwm = kw_schemes(L)
    glow = .55 if dark else 0.
    sc_beat = 1 + .05 * bp * ctx['chorus']
    placed = []
    for k, ch in enumerate(s):
        if ch == ' ': continue
        pp = clamp((t - ct[k]) / .42)
        if pp <= 0: continue
        p = eo3(pp)
        a = min(1., pp * 3) * lineA
        blur = q * 4
        x, y = pos[k]
        seed = ((i * 31 + k * 17) % 11) / 10 - .5
        y += -40 * (1 - p) + ex_y + 5 * math.sin(t * 3.2 + k * .9)
        sc = eback(pp, 2.6) * (1 - .4 * q) * sc_beat
        rot = (1 - p) * seed * 60 + seed * 7
        skew = 0.
        sch = kwm[k] or sch_line
        if kwm[k]: sc *= 1.14 + .05 * math.sin(t * 6)
        if st == 'rainheavy':
            pb = clamp((t - ct[k]) / .45)
            y += -70 * (1 - eback(pb, 2.2)) if pb < 1 else 0
        if st == 'clear':
            pb = clamp((t - ct[k]) / .6)
            sc = (1 + .45 * (1 - eback(pb, 2.0))) * sc_beat * (1.14 if kwm[k] else 1)
            blur = (1 - eo3(pb)) * 2.5 + q * 4
        if st == 'wind':
            skew = -.22 * wind
            x += -30 * wind * math.sin(t * 3 + k)
        if st == 'float':
            y += 8 * math.sin(t * 1.4 + k * .7)
        if st == 'fall':
            ft = ct[-1] + .55 + .09 * k
            dt = t - ft
            if dt > 0:
                y += 240 * dt * dt + 40 * dt
                x += 34 * math.sin(dt * 2.6 + k) * dt
                rot += (1 if k % 2 else -1) * 70 * dt
                a *= 1 - smooth(dt / 1.5)
        if st == 'blurout':
            bt = clamp((t - (ct[-1] + .35)) / 1.6)
            blur += 18 * eio(bt); a *= 1 - .7 * eio(bt)
            x += 8 * eio(bt) * math.sin(k * 2.1)
        if st == 'spread':
            u = eio((t - (ct[-1] + .1)) / 2.4)
            x = 960 + (x - 960) * (1 + 1.6 * u)
            y += 26 * u * math.sin(k * 1.7)
            a *= 1 - .25 * u * (0 < k < n - 1)
        if st == 'question':
            u = eio((t - (ct[-1] + .3)) / 1.3)
            if k in L.get('up', (2, 3)): x -= 40 * u; y -= 92 * u
            if k in L.get('down', (6, 7)): x += 40 * u; y += 92 * u
            if k in L.get('dim', (4, 5)): a *= 1 - .55 * u
        if st == 'drift':
            dt = t - (ct[-1] + .9 + .16 * (n - k))
            if dt > 0:
                x += 210 * dt ** 1.45 * (.7 + .05 * k); y += -60 * dt + 18 * math.sin(dt * 2 + k)
                rot += 20 * dt * (1 if k % 2 else -.6)
                a *= 1 - smooth(dt / 2.6); blur += dt * 2
        if st == 'window':
            fog = smooth((t - (ct[-1] + .2)) / 1.5)
            blur += 14 * fog; a *= 1 - .5 * fog
        hz.draw_glyph(c, ch, x, y, font, sch, a, sc=sc, rot=rot, blur=blur, skew=skew, glow=glow)
        placed.append((k, x, y, a))

    stickers(c, i, L, t, st, placed, size, cy, lineA, kwm, sch_line, wind, ct, vertical, n)
    if st == 'swing': c.restore()
    elif vertical and L.get('seal'):
        sa = lineA * eback((t - ct[-1] - .2) / .5)
        sx, sy = L['col'], 196 + n * size * 1.2 + 40
        c.drawRoundRect(skia.Rect.MakeXYWH(sx - 26, sy - 26, 52, 52), 8, 8, paint((1, 1, 1), clamp(sa)))
        c.drawRoundRect(skia.Rect.MakeXYWH(sx - 22, sy - 22, 44, 44), 6, 6, paint(hz.SCH['kw_flower']['f2'], clamp(sa)))
        glyph(c, C('SEAL_CHAR', C('TITLE', '印')[0]), sx, sy, F('kl', 30), (1, 1, 1), clamp(sa))

def stickers(c, i, L, t, st, placed, size, cy, lineA, kwm, sch_line, wind, ct, vertical, n):
    if not placed: return
    yellow = hz._hx('#FFC21A')
    # sparkles on keywords
    kws = [pl for pl in placed if kwm[pl[0]] is not None]
    if kws and st not in ('fall', 'drift'):
        (k0, x0, y0, a0), (k1, x1, y1, a1) = kws[0], kws[-1]
        tw = .75 + .25 * math.sin(t * 7)
        e = eback(clamp((t - ct[k1] - .1) / .4), 2)
        hz.star4(c, x0 - size * .55, y0 - size * .55, 22 * e * tw, yellow, a0, t * 60)
        hz.star4(c, x1 + size * .6, y1 - size * .5, 15 * e * (1.75 - tw), (1, 1, 1), a1, -t * 50)
        hz.star4(c, x1 + size * .45, y1 + size * .55, 11 * e * tw, yellow, a1, t * 40)
    last = placed[-1]
    lx, ly = last[1], last[2]
    fx, fy = placed[0][1], placed[0][2]
    e_end = eback(clamp((t - ct[-1] - .15) / .45), 2.2)
    if st == 'question':
        for j, (qx, qy) in enumerate(((fx - size * .9, fy - 70), (lx + size * .9, ly + 40))):
            hz.qmark(c, qx, qy + 6 * math.sin(t * 5 + j), size, F('sb', 84), hz.SCH['kw_love'], lineA * e_end, (-14 if j == 0 else 12) + 8 * math.sin(t * 4 + j))
    if 'kw_love' in [hz_name(kwm[pl[0]]) for pl in placed]:
        for j in range(3):
            ph = (t * .7 + j / 3) % 1
            hz.heart(c, lx + 60 + 40 * j, ly - 40 - ph * 140, 16 + 6 * j, hz._hx('#FF5C93'), lineA * e_end * (1 - ph) ** .6, 12 * math.sin(t * 3 + j))
    if st in ('rainheavy', 'blurout') or (st == 'center' and kws and hz_name(kws[0] and kwm[kws[0][0]]) == 'kw_rain'):
        for j in range(3):
            dy = (t * 1.6 + j * .33) % 1
            hz.drop(c, lx + 80 + 34 * j, ly - 60 + dy * 120, 13 - 2 * j, hz._hx('#4FB4FF'), lineA * e_end * (1 - dy), 0)
    if st == 'wind':
        hz.speed_lines(c, fx - size * .75, fy, size * .9, hz._hx('#6EC3FF'), lineA * eo3((t - L['t0']) / .5) * min(1, .4 + wind), 4, t)
    if L.get('icon') == 'sun':
        sa = eback(clamp((t - ct[-1] - .1) / .5), 2.2)
        hz.sun_icon(c, lx + size * 1.15, ly + size * .05, 40 * sa, lineA, t * 30)
    tg = TAGS.get(i)
    if tg:
        pt = clamp((t - L['t0'] - .45) / .4)
        if pt > 0:
            if vertical: tx, ty = L['col'] - 150, 160
            elif st == 'window': tx, ty = 330, 290
            else: tx, ty = min(lx + size * .3 + 28 * len(tg), 1790 - 26 * len(tg)), ly - size * 1.0
            bg = sch_line['tag']
            hz.tag(c, tg, tx, ty + 4 * math.sin(t * 4), F('kl', 46), bg, lineA * min(1, pt * 3),
                   rot=-7 + 3 * math.sin(t * 3.3 + i), sc=eback(pt, 2.6))

TAGS = C('TAGS', {})

def hz_name(sch):
    for k, v in hz.SCH.items():
        if v is sch: return k
    return None

def draw_staff(c, t, pal, group):
    """Solfège lines on a five‑line staff."""
    top, bot, ink, acc = pal
    t0, t1, notes = group
    if not (t0 - .3 < t < t1 + .9): return
    q = smooth((t - t1) / .8); A_ = 1 - q
    u = eo3((t - t0 + .3) / 1.2)
    x0, x1 = 300, 1620; yb = 585; gap = 24
    for k in range(5):
        y = yb - k * gap
        c.drawLine(x0, y, lerp(x0, x1, u), y, paint(ink, .38 * A_, stroke=1.4))
    # treble clef glyph
    draw_text(c, '𝄞', x0 + 40, yb - 2 * gap, F('cr', 1), ink, 0)  # (font lacks glyph; keep layout minimal)
    xs = np.linspace(x0 + 90, x1 - 60, len(notes))
    prev = None
    contour = skia.Path()
    for k, (tn, syl, step) in enumerate(notes):
        p = clamp((t - tn) / .35)
        if p <= 0: break
        x = xs[k]; y = yb - step * gap / 2 + 2
        if prev is None: contour.moveTo(x, y)
        else: contour.lineTo(x, y)
        prev = (x, y)
    if prev: c.drawPath(contour, paint(acc, .55 * A_, stroke=1.6))
    for k, (tn, syl, step) in enumerate(notes):
        p = clamp((t - tn) / .35)
        if p <= 0: break
        x = xs[k]; y = yb - step * gap / 2 + 2
        e = eback(p, 2.4)
        # ledger line for D5? (within staff)
        dt = t - tn
        if dt < 1.0:
            r = 14 + dt * 60
            c.drawCircle(x, y, r, paint(acc, .5 * (1 - dt) * A_, stroke=1.2))
        c.save(); c.translate(x, y); c.rotate(-22); c.scale(e, e)
        c.drawOval(skia.Rect.MakeXYWH(-15, -10.5, 30, 21), paint(ink if k % 7 else acc, A_))
        c.restore()
        c.drawLine(x + 13 * e, y - 3, x + 13 * e, y - 3 - 74 * e, paint(ink, .9 * A_ * e, stroke=1.6))
        hz.draw_string(c, syl, x, yb + 74 + 10 * (1 - eo3(p)), F('kl', 38), hz.SCH[sec_scheme(t0)], A_ * min(1, p * 3), track=1, sc=eback(p, 2.4), rot=(k % 3 - 1) * 5)

# ---------------------------------------------------------------- HUD, title, end card
def hud(c, t, pal):
    """左上角歌名，右上角章节，底部进度条"""
    top, bot, ink, acc = pal
    vis = smooth((t - C('HUD_FROM', 15.3)) / 2) * (1 - smooth((t - (C('END_START', AUDIO_END) - .8)) / .8))
    if vis < .01 or not C('HUD', True): return
    a = .72 * vis
    title_ = C('TITLE', '')
    draw_text(c, title_, 84, 78, F('s6', 24), ink, a, track=4, align='l')
    if C('ARTIST_LATIN'):
        draw_text(c, C('ARTIST_LATIN'), 84 + text_w(title_, F('s6', 24), 4) + 18, 79, F('ci', 26), ink, a * .7, align='l')
    ch = None
    for cc in CHAPTERS:
        if t >= cc[0]: ch = cc
    if ch:
        ca = a * smooth((t - ch[0]) / 1.2)
        draw_text(c, f'{ch[1]}', 1836, 78, F('ci', 26), ink, ca * .7, align='r')
        w = text_w(ch[1], F('ci', 26))
        draw_text(c, ch[2], 1836 - w - 22, 78, F('s4', 20), ink, ca * .8, track=3, align='r')
    x0, x1, y = 84, 1836, 1006
    pr = clamp(t / AUDIO_END)
    c.drawLine(x0, y, x1, y, paint(ink, .14 * vis, stroke=1))
    c.drawLine(x0, y, lerp(x0, x1, pr), y, paint(ink, .45 * vis, stroke=1))
    for cc in CHAPTERS[1:]:
        cx = lerp(x0, x1, cc[0] / AUDIO_END)
        c.drawLine(cx, y - 4, cx, y + 4, paint(ink, .3 * vis, stroke=1))
    c.drawCircle(lerp(x0, x1, pr), y, 3.5, paint(acc, vis))


def _big_title(c, t, text, t0, cy, size, sch, a_mul=1.0, out=0.0):
    n = len(text)
    size = min(size, 1500 / max(1, n) / 1.12)
    step = size * 1.12
    for k, ch in enumerate(text):
        pp = clamp((t - (t0 + k * .5)) / .5)
        if pp <= 0: continue
        x = 960 + (k - (n - 1) / 2) * step
        hz.draw_glyph(c, ch, x, cy + 7 * math.sin(t * 2.4 + k * 1.3) - out * 40, F('kl', size), sch,
                      min(1, pp * 3) * (1 - out) * a_mul, sc=eback(pp, 2.4) * (1 - .5 * out), rot=(k % 2 * 2 - 1) * 5 + 3 * math.sin(t * 2 + k))
    return step * n


def title(c, t, pal):
    """片头：歌名大花字 + 星星 + 原唱标签 + 一行副标题（TITLE_SUB）"""
    t_out = C('TITLE_OUT', 12.6)
    if t > t_out + 2.4: return
    out = smooth((t - t_out) / 1.2)
    sch = hz.SCH[C('TITLE_SCHEME', 'memory')]
    wid = _big_title(c, t, C('TITLE', ''), C('TITLE_IN', 2.0), 625, 230, sch, 1, out)
    for j, (dx, dy, r) in enumerate(((-.5, -125, 30), (.5, -105, 22), (.55, 120, 15), (-.56, 135, 12))):
        pa = eback(clamp((t - 3.1 - j * .2) / .4), 2)
        hz.star4(c, 960 + dx * (wid + 60), 625 + dy, r * pa * (1 + .18 * math.sin(t * 5 + j)), hz._hx('#FFC21A') if j % 2 == 0 else (1, 1, 1), 1 - out, t * 40 + j * 30)
    pt = clamp((t - 4.3) / .45)
    if pt > 0 and C('ARTIST'):
        hz.tag(c, C('ARTIST'), 960, 815 - out * 30, F('kl', 42), sch['outer'], (1 - out) * min(1, pt * 3), rot=-5 + 2 * math.sin(t * 3), sc=eback(pt, 2.4))
    if C('TITLE_SUB'):
        pt2 = eo3((t - 5.4) / 1.2)
        draw_text(c, C('TITLE_SUB'), 960, 895 - out * 30, F('ci', 30), pal[2], pt2 * (1 - out) * .6, track=1.5)


def endcard(c, t, pal):
    """片尾：歌名再出现一次 + 原唱标签 + 副标题（END_SUB），可选太阳贴纸（END_ICON='sun'）"""
    t0 = C('END_START')
    if t0 is None or t < t0: return
    sch = hz.SCH[C('END_SCHEME', 'clear')]
    wid = _big_title(c, t, C('TITLE', ''), t0 + .3, 430, 200, sch)
    if C('END_ICON') == 'sun':
        sa = eback(clamp((t - t0 - 1.2) / .5), 2.2)
        hz.sun_icon(c, 960 + wid / 2 + 60, 310, 42 * sa, 1, t * 25)
    pt = clamp((t - t0 - 1.5) / .45)
    if pt > 0 and C('ARTIST'):
        hz.tag(c, C('ARTIST'), 960, 610, F('kl', 42), sch['tag'], min(1, pt * 3), rot=-5 + 2 * math.sin(t * 3), sc=eback(pt, 2.4))
    if C('END_SUB'):
        p3 = eo3((t - t0 - 2.2) / 1.2)
        draw_text(c, C('END_SUB'), 960, 680, F('ci', 30), pal[2], p3 * .65, track=1.5)

# ---------------------------------------------------------------- frame
STAFFS = []
def build_staffs():
    """SOLFEGE：哼唱 / 唱名段落画成五线谱。每项 (开始, 结束, [(t0, t1, '唱名 空格分隔', [音高步数…]), …])
    音高步数以五线谱最下面一条线（E4）为 0，向上每个线或间 +1。"""
    for t0, t1, parts in C('SOLFEGE', []):
        notes = []
        for a, b, syl, steps in parts:
            sy = syl.split(); n = len(sy)
            notes += [(a + (b - a) * k / n, sy[k], steps[k]) for k in range(n)]
        STAFFS.append((t0, t1, notes))
build_staffs()

def swing_angle(t):
    """SWINGS：[(开始, 结束)] 时间段里 swing 动效的摆角"""
    for a, b in C('SWINGS', []):
        if a <= t <= b:
            u = t - a
            amp = 7.5 * smooth(u / 1.2) * (1 - .5 * smooth((u - 4) / 4))
            return amp * math.sin(2 * math.pi * u / C('SWING_PERIOD', 1.764))
    return 0.

def render_frame(c, t, T):
    pal = palette(t)
    top, bot, ink, acc = pal
    R = keyed(t, RAIN_K); wind = keyed(t, WIND_K); S = keyed(t, SUN_K); G = keyed(t, GLASS_K); cloud = keyed(t, CLOUD_K)
    chorus = 1. if any(a <= t < b for a, b in CHORUS) else 0.
    bp = pulse(t, .22)
    ctx = dict(wind=wind, bp=bp, chorus=chorus, swing=swing_angle(t))
    c.clear(CI(top))
    c.save()
    zs = 1 + .006 * bp * chorus + .004 * env(LOW, t) * chorus
    c.translate(W / 2, H / 2); c.scale(zs, zs); c.translate(-W / 2, -H / 2)
    draw_background(c, t, pal, T, S, cloud, wind)
    draw_dust(c, t, pal, (1 - R) * (.5 + .5 * S) * (lum(top) > .45))
    scene_hook(c, t, pal, wind, 'scene')
    draw_rain(c, t, pal, R, wind, near=False)
    title(c, t, pal)
    for g in STAFFS: draw_staff(c, t, pal, g)
    for i in range(len(LINES)):
        draw_line(c, i, t, pal, ctx)
    draw_petals(c, t, wind)
    badges(c, t, pal)
    scene_hook(c, t, pal, wind, 'scene_over')
    draw_rain(c, t, pal, R, wind, near=True)
    c.restore()
    draw_glass(c, t, T, G, pal)
    # lightning & the clearing flash
    fl = 0.
    for lt in LIGHTNING:
        dt = t - lt
        if 0 <= dt < 1.2: fl = max(fl, .55 * math.exp(-dt / .12) + .25 * math.exp(-max(0, dt - .18) / .1) * (dt > .18))
    for ft in FLASHES:
        dt = t - ft
        if 0 <= dt < 2.5: fl = max(fl, .7 * math.exp(-dt / .5))
    if fl > .005:
        fp = skia.Paint(); fp.setColor4f(C4((1, .99, .96), fl)); fp.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeWH(W, H), fp)
    # paper / grain / vignette
    light = lum(top) > .45
    pp = skia.Paint(); pp.setBlendMode(skia.BlendMode.kMultiply if light else skia.BlendMode.kScreen)
    pp.setAlphaf(.07 if light else .03)
    c.drawImage(T['paper'], 0, 0, skia.SamplingOptions(), pp)
    gp = skia.Paint(); gp.setBlendMode(skia.BlendMode.kOverlay); gp.setAlphaf(.05 if light else .09)
    c.drawImage(T['grain'][int(t * 12) % 6], 0, 0, skia.SamplingOptions(), gp)
    vp = skia.Paint(); vp.setAlphaf(.28 if light else .55)
    c.drawImage(T['vig'], 0, 0, skia.SamplingOptions(), vp)
    hud(c, t, pal)
    endcard(c, t, pal)
    # global fades
    fi = 1 - smooth(t / 1.2); fo = smooth((t - (TOTAL - 1.4)) / 1.4)
    k = max(fi, fo)
    if k > .001:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), k))

# ---------------------------------------------------------------- drivers
def preview(times, out):
    T = make_textures(); s = skia.Surface(W, H); c = s.getCanvas()
    for t in times:
        render_frame(c, t, T)
        s.makeImageSnapshot().save(f'{out}/f_{t:07.2f}.png')

def chunk(a, b, path, crf):
    T = make_textures(); s = skia.Surface(W, H); c = s.getCanvas()
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
                           '-tune', 'film', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for f in range(a, b):
        render_frame(c, f / FPS, T)
        ff.stdin.write(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        if (f - a) % 300 == 0: print(path, f, flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == '__main__':
    cmd = sys.argv[2]
    if cmd == 'preview':
        out = sys.argv[3]; os.makedirs(out, exist_ok=True)
        preview([float(x) for x in sys.argv[4:]], out)
    elif cmd == 'chunk':
        chunk(int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], int(sys.argv[6]))
    elif cmd == 'info':
        print(json.dumps(dict(total=TOTAL, frames=NFRAMES, audio_end=AUDIO_END, lines=len(LINES))))
