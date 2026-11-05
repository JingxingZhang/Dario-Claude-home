"""像素人物与道具（原生分辨率 320×180 上绘制）。人物：女主（第一人称“我”）与男主“你”。"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *

K = (34, 24, 44)          # 描边
PINK = (255, 120, 170)
PINK_L = (255, 186, 214)
HEART = (240, 60, 100)
HEART_D = (170, 30, 70)
BLUSH = (255, 140, 160)
CYAN = (90, 220, 255)
NEON_P = (255, 80, 200)
NEON_B = (80, 200, 255)
NEON_Y = (255, 230, 90)
GLASS = (150, 190, 230)

PAL = {
    # 每个角色一套“外观”：配色 + 发型 + 衣着。按歌词需要随时新增（见 make_look）。
    'girl': dict(hair=(96, 48, 74), hair_d=(66, 30, 52), skin=(255, 216, 188), cloth=(250, 118, 150), cloth_d=(200, 78, 118),
                 legs=(62, 52, 84), shoe=(44, 30, 44), hair_style='long', body='dress', clip=(255, 120, 160), blush=True),
    'boy': dict(hair=(46, 46, 68), hair_d=(28, 28, 46), skin=(250, 206, 176), cloth=(88, 140, 232), cloth_d=(58, 98, 184),
                legs=(60, 64, 100), shoe=(236, 236, 240), hair_style='short', body='hoodie'),
}


def make_look(name, base='boy', **kw):
    """新建角色外观并注册，例如 make_look('grandpa', 'boy', hair_style='bald', hair=(220,220,220), beard=True, body='shirt')。
    发型 hair_style：long 长发 / short 短发 / bob 短发齐耳 / ponytail 马尾 / bun 丸子头 / bald 光头（可配 beard）
    衣着 body：dress 裙子 / hoodie 帽衫 / shirt 衬衫 / suit 西装（领带）/ uniform 校服（领结）"""
    d = dict(PAL[base]); d.update(kw); PAL[name] = d
    return name


def R(d, x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def outline_rgba(im, col=K):
    a = np.array(im)
    m = a[:, :, 3] > 0
    dil = m.copy()
    dil[1:] |= m[:-1]; dil[:-1] |= m[1:]; dil[:, 1:] |= m[:, :-1]; dil[:, :-1] |= m[:, 1:]
    edge = dil & ~m
    a[edge] = (*col, 255)
    return Image.fromarray(a, 'RGBA')


def paste(img, spr, x, y):
    img.paste(spr, (int(round(x)), int(round(y))), spr)


def scaled(spr, k):
    return spr if k == 1 else spr.resize((spr.width * k, spr.height * k), Image.NEAREST)


def ellipse_fill(d, cx, cy, rx, ry, col):
    for yy in range(-ry, ry + 1):
        dx = int(rx * math.sqrt(max(0.0, 1 - (yy / (ry + 0.5)) ** 2)) + 0.3)
        d.line([(cx - dx, cy + yy), (cx + dx, cy + yy)], fill=col)


# ---------------- 人物 ----------------
def _arm(d, sx, sy, hx, hy, cloth, skin):
    d.line([(sx, sy), (hx, hy)], fill=cloth, width=2)
    R(d, hx - 1, hy - 1, 2, 2, skin)


def person(img, x, y, who='girl', face=1, expr='smile', arm='down', t=0.0, scale=2, walk=False,
           umbrella=None, glasses=False, kneel=False, horns=False, mask=False, breathe=0.0):
    """通用 Q 版小人（脚手架）：只用于快速试画、路人群演。主角和重要角色请按歌用 charkit 从零设计。
    x,y：脚底中点（原生坐标）。face=1 朝右，-1 朝左。"""
    p = PAL[who] if isinstance(who, str) else who
    hs, body = p.get('hair_style', 'short'), p.get('body', 'hoodie')
    im = Image.new('RGBA', (30, 42), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = 15
    ky = 5 if kneel else 0          # 跪下时整个上身下移
    by = -int(round(breathe))       # 呼吸起伏
    # 后发
    if hs == 'long':
        R(d, 6, 7 + ky + by, 18, 21, p['hair_d'])
        R(d, 7, 27 + ky + by, 16, 2, p['hair_d'])
    elif hs == 'bob':
        R(d, 6, 7 + ky + by, 18, 12, p['hair_d'])
    elif hs == 'ponytail':
        R(d, 4, 6 + ky + by, 5, 16, p['hair_d']); R(d, 3, 10 + ky + by, 3, 8, p['hair_d'])
    # 腿
    ph = (int(t * 7) % 2) if walk else 0
    if kneel:
        R(d, 10, 33, 6, 4, p['legs']); R(d, 15, 37, 7, 3, p['legs']); R(d, 8, 37, 4, 3, p['shoe'])
        R(d, 21, 38, 3, 2, p['shoe'])
    else:
        lx = (-1 if ph else 1)
        if body == 'dress':
            R(d, 12 + lx, 31, 2, 8, p['legs']); R(d, 16 - lx, 31, 2, 8, p['legs'])
        else:
            R(d, 11 + lx, 30, 3, 9, p['legs']); R(d, 16 - lx, 30, 3, 9, p['legs'])
        R(d, 11 + lx, 39, 4, 2, p['shoe']); R(d, 16 - lx, 39, 4, 2, p['shoe'])
    # 身体
    if body == 'dress':
        R(d, 11, 21 + ky + by, 9, 5, p['cloth'])
        for i in range(7):
            R(d, 10 - i // 3, 26 + i + ky + by, 11 + 2 * (i // 3), 1, p['cloth'] if i < 5 else p['cloth_d'])
        R(d, 11, 25 + ky + by, 9, 1, p['cloth_d'])
    else:
        R(d, 10, 21 + ky + by, 11, 10, p['cloth'])
        R(d, 10, 29 + ky + by, 11, 2, p['cloth_d'])
        if body == 'hoodie':
            R(d, 14, 22 + ky + by, 3, 4, p['cloth_d'])  # 帽衫拉绳
        elif body == 'shirt':
            R(d, 13, 21 + ky + by, 5, 2, (250, 250, 250)); R(d, 15, 23 + ky + by, 1, 6, p['cloth_d'])
        elif body == 'suit':
            R(d, 13, 21 + ky + by, 5, 6, (250, 250, 250)); R(d, 15, 22 + ky + by, 1, 6, p.get('tie', (200, 40, 60)))
        elif body == 'uniform':
            R(d, 12, 21 + ky + by, 7, 3, (250, 250, 250)); R(d, 14, 23 + ky + by, 3, 2, p.get('tie', (200, 40, 60)))
    # 头
    hy = 12 + ky + by
    ellipse_fill(d, cx, hy, 8, 8, p['skin'])
    # 前发
    if hs in ('long', 'bob', 'ponytail', 'bun'):
        R(d, 7, hy - 9, 17, 6, p['hair'])
        R(d, 6, hy - 5, 4, 14 if hs == 'long' else 8, p['hair'])
        for i in range(0, 14, 3):
            R(d, 9 + i, hy - 3, 2, 2, p['hair'])
        R(d, 21, hy - 6, 3, 6, p['hair'])
        if hs == 'bun':
            ellipse_fill(d, 15, hy - 11, 4, 3, p['hair'])
        if p.get('clip'):
            R(d, 20, hy - 10, 3, 2, p['clip'])  # 发卡
    elif hs == 'short':
        R(d, 7, hy - 9, 17, 6, p['hair'])
        R(d, 6, hy - 6, 3, 7, p['hair'])
        for i in range(4):
            R(d, 8 + i * 4, hy - 11 + (i % 2), 3, 2, p['hair'])
        R(d, 20, hy - 4, 3, 3, p['hair'])
    elif hs == 'bald':
        R(d, 6, hy - 3, 3, 5, p['hair']); R(d, 22, hy - 3, 2, 4, p['hair'])
    if p.get('beard'):
        R(d, 12, hy + 4, 10, 4, p['hair']); R(d, 14, hy + 8, 6, 2, p['hair'])
    # 脸（朝右：五官偏右）
    ex1, ex2, ey = 13, 18, hy
    if glasses:
        R(d, 11, ey - 1, 11, 3, K); R(d, 12, ey - 1, 2, 1, (120, 120, 160))
    elif expr == 'wink':
        R(d, ex1, ey, 1, 2, K); R(d, ex2 - 1, ey + 1, 3, 1, K)
    elif expr in ('closed', 'happy'):
        d.point((ex1 - 1, ey + 1), fill=K); d.point((ex1, ey), fill=K); d.point((ex1 + 1, ey + 1), fill=K)
        d.point((ex2 - 1, ey + 1), fill=K); d.point((ex2, ey), fill=K); d.point((ex2 + 1, ey + 1), fill=K)
    elif expr == 'heart':
        for ex in (ex1, ex2):
            R(d, ex - 1, ey - 1, 1, 1, HEART); R(d, ex + 1, ey - 1, 1, 1, HEART); R(d, ex - 1, ey, 3, 1, HEART); d.point((ex, ey + 1), fill=HEART)
    elif expr == 'surprised':
        R(d, ex1, ey - 1, 1, 3, K); R(d, ex2, ey - 1, 1, 3, K)
    elif expr == 'side':  # 斜眼
        R(d, ex1 - 1, ey + 1, 3, 1, K); R(d, ex2 - 1, ey + 1, 3, 1, K); d.point((ex1 + 1, ey + 2), fill=K); d.point((ex2 + 1, ey + 2), fill=K)
    else:
        R(d, ex1, ey, 1, 2, K); R(d, ex2, ey, 1, 2, K)
    if expr in ('angry', 'pout'):
        d.point((ex1 - 1, ey - 2), fill=K); d.point((ex1, ey - 1), fill=K); d.point((ex2 + 1, ey - 2), fill=K); d.point((ex2, ey - 1), fill=K)
    if expr == 'sad':
        d.point((ex1 + 1, ey - 2), fill=K); d.point((ex1, ey - 1), fill=K); d.point((ex2 - 1, ey - 2), fill=K); d.point((ex2, ey - 1), fill=K)
    # 嘴
    my = hy + 4
    if expr in ('smile', 'wink', 'happy', 'heart'):
        d.point((15, my), fill=K); R(d, 16, my + 1, 2, 1, K); d.point((18, my), fill=K)
    elif expr == 'smirk':
        R(d, 15, my + 1, 2, 1, K); d.point((17, my), fill=K); d.point((18, my - 1), fill=K)
    elif expr == 'surprised':
        R(d, 16, my, 2, 2, K)
    elif expr == 'sad':
        R(d, 16, my, 2, 1, K); d.point((15, my + 1), fill=K); d.point((18, my + 1), fill=K)
    elif expr in ('pout', 'angry'):
        R(d, 15, my + 1, 3, 1, K)
    elif expr == 'side':
        R(d, 16, my + 1, 2, 1, K)
    else:
        R(d, 16, my + 1, 2, 1, K)
    if expr in ('smile', 'blush', 'heart', 'happy', 'wink', 'shy') or p.get('blush') and expr != 'sad':
        R(d, 11, hy + 2, 2, 1, BLUSH); R(d, 20, hy + 2, 2, 1, BLUSH)
    if expr in ('blush', 'shy'):
        R(d, 10, hy + 2, 4, 2, BLUSH); R(d, 19, hy + 2, 4, 2, BLUSH)
    # 手臂
    cl, sk = p['cloth_d'], p['skin']
    sy = 22 + ky + by
    L, Rr = (10, sy), (20, sy)
    wav = math.sin(t * 12) * 2
    hands = {
        'down': ((9, 29 + ky), (21, 29 + ky)),
        'wave': ((9, 29 + ky), (24, int(9 + wav) + ky)),
        'point': ((9, 29 + ky), (27, 21 + ky)),
        'phone': ((9, 29 + ky), (18, hy + 3)),
        'heart': ((13, 2 + ky), (17, 2 + ky)),
        'shrug': ((3, 18 + ky), (27, 18 + ky)),
        'cover': ((12, hy + 3), (19, hy + 3)),
        'hold': ((22, 24 + ky), (24, 26 + ky)),
        'ear': ((9, 29 + ky), (22, hy - 1)),
        'fist': ((9, 29 + ky), (24, 13 + ky)),
        'umbrella': ((9, 29 + ky), (20, 24 + ky)),
        'chest': ((15, 24 + ky), (17, 25 + ky)),
    }[arm]
    if arm == 'heart':  # 比心：手肘外撑，绕过脸
        d.line([L, (4, 12 + ky)], fill=cl, width=2); _arm(d, 4, 12 + ky, 12, 2 + ky, cl, sk)
        d.line([Rr, (26, 12 + ky)], fill=cl, width=2); _arm(d, 26, 12 + ky, 18, 2 + ky, cl, sk)
    else:
        _arm(d, L[0], L[1], hands[0][0], hands[0][1], cl, sk)
        _arm(d, Rr[0], Rr[1], hands[1][0], hands[1][1], cl, sk)
    if arm == 'phone':
        R(d, 19, hy - 2, 3, 5, K); R(d, 20, hy - 1, 1, 3, CYAN)
    if horns:
        for hx in (9, 20):
            R(d, hx, hy - 12, 2, 3, (220, 40, 60)); d.point((hx + (0 if hx < 15 else 1), hy - 13), fill=(220, 40, 60))
    if mask:
        R(d, 10, hy - 4, 13, 8, (250, 250, 250)); R(d, 13, hy - 1, 2, 2, K); R(d, 18, hy - 1, 2, 2, K)
        R(d, 15, hy + 2, 3, 1, (220, 60, 80))
    im = outline_rgba(im)
    if umbrella:
        um = Image.new('RGBA', (30, 42), (0, 0, 0, 0))
        ud = ImageDraw.Draw(um)
        ellipse_fill(ud, 15, 3 + ky, 13, 6, umbrella)
        R(ud, 2, 3 + ky, 27, 7, (0, 0, 0, 0))
        for i in range(3, 28, 6):
            d2 = lerpc(umbrella, (255, 255, 255), 0.3)
            ud.line([(i, 0 + ky), (i, 3 + ky)], fill=d2)
        R(ud, 15, 3 + ky, 1, 22, K)
        um = outline_rgba(um)
        um.paste(im, (0, 0), im)
        im = um
    if face < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = scaled(im, scale)
    paste(img, im, x - 15 * scale, y - 41 * scale)


# ---------------- 小道具 ----------------
HEART_PAT = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...']


@lru_cache(None)
def heart_sprite(k=1, col=HEART, broken=False, outline=True):
    im = Image.new('RGBA', (9, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y, row in enumerate(HEART_PAT):
        for x, c in enumerate(row):
            if c == 'X':
                d.point((x + 1, y + 1), fill=col)
    d.point((2, 2), fill=(255, 220, 230))
    if broken:
        for (x, y) in ((4, 1), (5, 2), (4, 3), (5, 4), (4, 5)):
            d.point((x, y), fill=(0, 0, 0, 0))
    if outline:
        im = outline_rgba(im)
    return scaled(im, k)


def heart(img, cx, cy, k=1, col=HEART, broken=False):
    s = heart_sprite(k, col, broken)
    paste(img, s, cx - s.width // 2, cy - s.height // 2)


def sparkle(img, x, y, r=3, col=(255, 250, 200)):
    d = ImageDraw.Draw(img)
    d.line([(x - r, y), (x + r, y)], fill=col); d.line([(x, y - r), (x, y + r)], fill=col)
    if r > 2:
        d.point((x - 1, y - 1), fill=col); d.point((x + 1, y + 1), fill=col); d.point((x - 1, y + 1), fill=col); d.point((x + 1, y - 1), fill=col)


def sweat(img, x, y, k=1):
    d = ImageDraw.Draw(img)
    pts = [(1, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (1, 3)]
    for (a, b) in pts:
        R(d, x + a * k, y + b * k, k, k, (120, 200, 255))
    R(d, x + k, y + k, k, k, (230, 250, 255))


def vein(img, x, y):
    d = ImageDraw.Draw(img)
    for (a, b) in ((0, 1), (1, 0), (3, 0), (4, 1), (0, 3), (1, 4), (4, 3), (3, 4)):
        R(d, x + a, y + b, 1, 1, (240, 50, 60))


def bang(img, x, y, n=2, col=(255, 70, 90)):
    d = ImageDraw.Draw(img)
    for i in range(n):
        R(d, x + i * 4, y, 2, 6, col); R(d, x + i * 4, y + 7, 2, 2, col)


def qmark(img, x, y, col=(255, 230, 90)):
    draw_text(img, x, y, '?', col, outline=K)


def concentration(img, cx, cy, t, col=(255, 255, 255), n=40, r0=60):
    """集中线"""
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = i / n * 6.283 + hsh(i, int(t * 12)) * 0.08
        rr = r0 + hsh(i, 3, int(t * 12)) * 30
        d.line([(cx + math.cos(a) * rr, cy + math.sin(a) * rr), (cx + math.cos(a) * 400, cy + math.sin(a) * 400)], fill=col)


def burst(img, t, c1, c2, cx=160, cy=90, n=16):
    """放射背景（综艺感）"""
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, c1)
    rot = t * 0.25
    for i in range(n):
        a0 = rot + i * 2 * math.pi / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + math.cos(a0) * 400, cy + math.sin(a0) * 400), (cx + math.cos(a1) * 400, cy + math.sin(a1) * 400)], fill=c2)


def dots_bg(img, t, c1, c2, step=14):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, c1)
    off = int(t * 6) % step
    for y in range(-step, H + step, step):
        for x in range(-step, W + step, step):
            xx = x + off + (step // 2 if (y // step) % 2 else 0)
            R(d, xx, y + off, 3, 3, c2)


def phone_big(img, x, y, w=70, h=120, lit=True):
    d = ImageDraw.Draw(img)
    R(d, x, y, w, h, K)
    R(d, x + 2, y + 2, w - 4, h - 4, (30, 30, 46))
    if lit:
        R(d, x + 4, y + 10, w - 8, h - 20, (236, 240, 248))
        R(d, x + 4, y + 10, w - 8, 10, (120, 170, 250))
    R(d, x + w // 2 - 6, y + 4, 12, 2, (70, 70, 90))


def chat_bubble(img, x, y, w, h, col, right=False):
    d = ImageDraw.Draw(img)
    R(d, x + 1, y, w - 2, h, col); R(d, x, y + 1, w, h - 2, col)
    if right:
        R(d, x + w - 2, y + h - 3, 3, 2, col)
    else:
        R(d, x - 1, y + h - 3, 3, 2, col)


def calendar(img, x, y, label, col=(240, 70, 80), flip=0.0):
    d = ImageDraw.Draw(img)
    R(d, x, y, 44, 44, K)
    R(d, x + 1, y + 1, 42, 42, (250, 250, 245))
    R(d, x + 1, y + 1, 42, 11, col)
    for i in (10, 32):
        R(d, x + i, y - 3, 2, 6, (120, 120, 140))
    draw_text(img, x + 22 - text_w(label) // 2, y + 18, label, K)
    if flip > 0:
        hh = int(31 * (1 - flip))
        R(d, x + 1, y + 12, 42, hh, (230, 230, 225))


def rose(img, x, y):
    d = ImageDraw.Draw(img)
    R(d, x + 2, y + 5, 1, 12, (60, 150, 70)); R(d, x + 3, y + 10, 3, 2, (60, 150, 70))
    R(d, x, y, 5, 5, (230, 40, 60)); R(d, x + 1, y + 1, 3, 2, (255, 90, 110)); R(d, x + 1, y - 1, 3, 1, (230, 40, 60))


def trash(img, x, y):
    d = ImageDraw.Draw(img)
    R(d, x - 1, y - 3, 22, 3, (120, 130, 140))
    R(d, x, y, 20, 24, (150, 160, 170))
    for i in range(4, 20, 5):
        R(d, x + i, y + 3, 1, 18, (110, 120, 130))
    R(d, x + 7, y - 5, 6, 2, (120, 130, 140))


def magnifier(img, x, y, r=8):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r, x + r, y + r], outline=K, width=2)
    d.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], fill=(200, 230, 255))
    d.line([(x + r - 1, y + r - 1), (x + r + 7, y + r + 7)], fill=(120, 80, 50), width=3)


def clock(img, cx, cy, r, t):
    d = ImageDraw.Draw(img)
    sh = int(math.sin(t * 40) * 2)
    cx += sh
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=K)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 250, 235))
    for i in range(12):
        a = i / 12 * 6.283
        d.point((cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2)), fill=K)
    a = t * 4
    d.line([(cx, cy), (cx + math.cos(a) * (r - 4), cy + math.sin(a) * (r - 4))], fill=(230, 50, 60), width=1)
    d.line([(cx, cy), (cx, cy - r + 6)], fill=K, width=2)
    for bx in (-r + 2, r - 6):
        d.ellipse([cx + bx, cy - r - 6, cx + bx + 6, cy - r], fill=(230, 60, 70))


def envelope(img, x, y, open_k=0.0):
    d = ImageDraw.Draw(img)
    R(d, x, y, 30, 20, K)
    R(d, x + 1, y + 1, 28, 18, (255, 245, 230))
    if open_k > 0:
        lift = int(open_k * 14)
        R(d, x + 4, y - lift + 2, 22, 14, (255, 255, 255))
        heart(img, x + 15, y - lift + 8, 1)
    d.line([(x + 1, y + 1), (x + 15, y + 11), (x + 29, y + 1)], fill=(220, 180, 170))
    heart(img, x + 15, y + 12, 1)


def sign_board(img, x, y, w, h, t):
    d = ImageDraw.Draw(img)
    R(d, x + w // 2 - 1, y + h, 3, 30, (130, 90, 60))
    R(d, x, y, w, h, K)
    R(d, x + 2, y + 2, w - 4, h - 4, (255, 236, 244))
    heart(img, x + w // 2, y + h // 2, 3 if int(t * 2.5) % 2 else 2)


def curtains(img, k, t):
    """舞台幕布：k=0 全开，1 全关"""
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, 14, (150, 20, 40))
    for i in range(0, W, 8):
        R(d, i, 12, 6, 4, (190, 140, 40))
    wid = int(30 + k * 132)
    for side in (0, 1):
        for i in range(wid):
            xx = i if side == 0 else W - 1 - i
            c = (170, 24, 46) if (i // 5) % 2 else (130, 16, 36)
            d.line([(xx, 14), (xx, H)], fill=c)


def spotlight(img, cx, top, bot, r, col=(255, 250, 200), k=0.35):
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    frac = np.clip((yy - top) / max(1, bot - top), 0, 1)
    half = 8 + frac * r
    m = (np.abs(xx - cx) < half) & (yy >= top) & (yy <= bot + 6)
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    m &= bay < 0.75
    a[m] = a[m] * (1 - k) + np.array(col) * k
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))


def big_button(img, cx, cy, pressed, label='离开'):
    d = ImageDraw.Draw(img)
    R(d, cx - 26, cy + 6, 52, 14, (70, 70, 90))
    R(d, cx - 24, cy + 4, 48, 6, K)
    hgt = 4 if pressed else 10
    ellipse_fill(d, cx, cy + 4 - hgt, 20, 6, (230, 50, 70))
    R(d, cx - 20, cy + 4 - hgt, 41, hgt, (180, 30, 50))
    ellipse_fill(d, cx, cy - hgt, 20, 6, (255, 80, 100))
    draw_text(img, cx - text_w(label) // 2, cy - hgt - 6, label, (255, 255, 255))


def scooter(img, x, y, t):
    d = ImageDraw.Draw(img)
    for wx in (x + 6, x + 44):
        d.ellipse([wx - 6, y - 6, wx + 6, y + 6], fill=K)
        d.ellipse([wx - 3, y - 3, wx + 3, y + 3], fill=(150, 150, 170))
        a = t * 20
        d.point((wx + math.cos(a) * 2, y + math.sin(a) * 2), fill=(240, 240, 240))
    R(d, x + 4, y - 10, 44, 6, (250, 200, 70))
    R(d, x + 10, y - 14, 30, 4, (250, 200, 70))
    R(d, x + 44, y - 30, 3, 22, (90, 90, 110))
    R(d, x + 40, y - 32, 10, 3, K)
    R(d, x + 48, y - 26, 4, 3, NEON_Y)


def dial(img, cx, cy, r, ang):
    """情绪表盘：ang 0..1（0 难过 → 1 心动）"""
    d = ImageDraw.Draw(img)
    cols = [(110, 130, 220), (150, 200, 120), (255, 200, 80), (255, 100, 150)]
    for i, c in enumerate(cols):
        a0, a1 = 180 + i * 45, 180 + (i + 1) * 45
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=c, outline=K)
    d.pieslice([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14], 180, 360, fill=(250, 246, 236))
    faces = ['sad', 'meh', 'happy', 'love']
    for i, f in enumerate(faces):
        a = math.radians(180 + 22.5 + i * 45)
        fx, fy = cx + math.cos(a) * (r - 7), cy + math.sin(a) * (r - 7)
        if f == 'love':
            heart(img, int(fx), int(fy), 1)
        else:
            R(d, int(fx) - 2, int(fy) - 1, 1, 1, K); R(d, int(fx) + 2, int(fy) - 1, 1, 1, K)
            if f == 'sad':
                R(d, int(fx) - 1, int(fy) + 2, 3, 1, K)
            elif f == 'happy':
                d.point((fx - 2, fy + 1), fill=K); R(d, int(fx) - 1, int(fy) + 2, 3, 1, K); d.point((fx + 2, fy + 1), fill=K)
            else:
                R(d, int(fx) - 1, int(fy) + 2, 3, 1, K)
    a = math.radians(180 + ang * 180)
    d.line([(cx, cy), (cx + math.cos(a) * (r - 16), cy + math.sin(a) * (r - 16))], fill=K, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=K)
    R(d, cx - r - 2, cy, 2 * r + 5, 3, K)


def wave_line(img, y0, t, amp, col, x0=0, x1=W, speed=1.0, beat=0.0):
    d = ImageDraw.Draw(img)
    prev = None
    for x in range(x0, x1):
        ph = (x - t * 60 * speed) / 26
        v = math.sin(ph) * amp * (0.6 + 0.4 * math.sin(ph * 0.37))
        if beat > 0:
            q = ((x - t * 60 * speed) % 80) / 80
            v += (-math.exp(-((q - 0.5) * 18) ** 2) * amp * 2.2 + math.exp(-((q - 0.56) * 22) ** 2) * amp * 1.2) * beat
        pt = (x, int(y0 + v))
        if prev:
            d.line([prev, pt], fill=col, width=2)
        prev = pt
