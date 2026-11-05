"""像素综艺素材：像素花字（拟声词/印章/OS/系统消息/弹窗/数值条/弹幕）、会“演戏”的物件（带表情的月亮、路灯、
垃圾桶、闹钟、日历、手机、心、楼房）、猫咪配角、各种场景道具。全部在原生 320×180 上画。"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *
from chars import K, R, paste, scaled, outline_rgba, ellipse_fill, heart, HEART, PINK, PINK_L, CYAN, NEON_P, NEON_B, NEON_Y, sparkle, sweat, BLUSH

# ---------------- 像素花字 ----------------
def _mask(s):
    w = max(1, text_w(s))
    m = np.zeros((12, w), bool)
    x = 0
    for ch in s:
        g, adv = glyph(ch)
        m[:, x:x + g.shape[1]] |= g
        x += adv
    return m


def _dil(m, n=1):
    for _ in range(n):
        d = m.copy()
        d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
        d[1:, 1:] |= m[:-1, :-1]; d[:-1, :-1] |= m[1:, 1:]; d[1:, :-1] |= m[:-1, 1:]; d[:-1, 1:] |= m[1:, :-1]
        m = d
    return m


@lru_cache(maxsize=2048)
def ptext_sprite(s, scale=2, c1=WHITE, c2=None, ring=WHITE, out=K, shadow=True):
    """像素花字精灵：渐变填充 + 白色内描边 + 深色外描边 + 投影"""
    m = _mask(s).repeat(scale, 0).repeat(scale, 1)
    pad = 3
    h, w = m.shape
    M = np.zeros((h + 2 * pad + 1, w + 2 * pad + 1), bool)
    M[pad:pad + h, pad:pad + w] = m
    r1 = _dil(M, 1)
    r2 = _dil(r1, 1)
    if scale == 1:  # 小字：只描一圈深色边，不加白色内描边，保证清晰
        r2 = r1
        c2 = c1
        ring = out
    a = np.zeros(M.shape + (4,), np.uint8)
    if shadow:
        sh = np.zeros_like(r2); sh[1:, 1:] = r2[:-1, :-1]
        a[sh] = (*lerpc(out, (0, 0, 0), 0.5), 255)
    a[r2] = (*out, 255)
    a[r1] = (*ring, 255)
    c2 = c2 or c1
    rows = np.arange(M.shape[0])[:, None] * np.ones((1, M.shape[1]))
    top = (rows < pad + h * 0.5)
    a[M & top] = (*c1, 255)
    a[M & ~top] = (*c2, 255)
    hi = M & ~np.roll(M, 1, 0)  # 笔画顶边提亮
    a[hi & top] = (*lerpc(c1, WHITE, 0.6), 255)
    return Image.fromarray(a, 'RGBA')


def ptext(img, x, y, s, scale=2, c1=WHITE, c2=None, ring=WHITE, out=K, anchor='c', shadow=True):
    spr = ptext_sprite(s, scale, c1, c2, ring, out, shadow)
    if anchor == 'c':
        x, y = x - spr.width // 2, y - spr.height // 2
    paste(img, spr, x, y)
    return spr.width, spr.height


def pop(img, x, y, s, t, born, dur=9.0, scale=2, c1=WHITE, c2=None, ring=WHITE, out=K, jitter=0, slam=False):
    """动态像素花字：弹出（slam=True 为盖章式从大砸下），dur 后消失"""
    dt = t - born
    if dt < 0 or dt > dur:
        return
    sc = scale
    if slam:
        if dt < 0.08:
            sc = scale + 2
        elif dt < 0.14:
            sc = scale + 1
    else:
        if dt < 0.07:
            sc = max(1, scale - 1)
        elif dt < 0.15:
            sc = scale + 1
    dy = 0 if dt > 0.2 else int(-math.sin(dt / 0.2 * math.pi) * 3)
    jx = int((hsh(int(t * 20), 1) - 0.5) * 2 * jitter) if jitter else 0
    jy = int((hsh(int(t * 20), 2) - 0.5) * 2 * jitter) if jitter else 0
    ptext(img, x + jx, y + dy + jy, s, sc, c1, c2, ring, out)


SFX_PAL = {
    'yel': ((255, 244, 120), (255, 160, 30), K), 'red': ((255, 150, 140), (230, 40, 60), K), 'pink': ((255, 200, 230), (255, 80, 160), K),
    'cyan': ((200, 250, 255), (50, 170, 255), K), 'green': ((210, 255, 170), (70, 200, 90), K), 'purp': ((230, 200, 255), (140, 90, 250), K),
    'white': (WHITE, (210, 220, 250), K),
}


def sfx(img, x, y, s, t, born, dur=1.2, pal='yel', scale=2, jitter=1, slam=False):
    c1, c2, out = SFX_PAL[pal]
    pop(img, x, y, s, t, born, dur, scale, c1, c2, WHITE, out, jitter, slam)


def stamp(img, cx, cy, s, t, born, col=(230, 40, 60), dur=99, scale=2):
    """印章：方框 + 字，从大砸下"""
    dt = t - born
    if dt < 0 or dt > dur:
        return
    sc = scale + (2 if dt < 0.07 else 1 if dt < 0.13 else 0)
    spr = ptext_sprite(s, sc, WHITE, WHITE, col, col, False)
    w, h = spr.width + 6, spr.height + 4
    box = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rectangle([0, 0, w - 1, h - 1], outline=col, width=2)
    d.rectangle([3, 3, w - 4, h - 4], fill=(*col, 255))
    box.paste(spr, (3, 2), spr)
    # 斑驳
    a = np.array(box)
    for i in range(int(w * h * 0.03)):
        xx, yy = int(hsh(i, 1, len(s)) * w), int(hsh(i, 2, len(s)) * h)
        a[yy, xx, 3] = 0
    box = Image.fromarray(a)
    box = box.rotate(-8, resample=Image.NEAREST, expand=True)
    paste(img, box, cx - box.width // 2, cy - box.height // 2)


def bubble_box(img, x, y, w, h, bg=WHITE, edge=K, tail='l'):
    d = ImageDraw.Draw(img)
    R(d, x + 1, y - 1, w - 2, h + 2, edge); R(d, x - 1, y + 1, w + 2, h - 2, edge); R(d, x, y, w, h, edge)
    R(d, x + 1, y, w - 2, h, bg); R(d, x, y + 1, w, h - 2, bg)
    if tail == 'l':
        R(d, x + 6, y + h, 4, 2, bg); R(d, x + 5, y + h, 1, 3, edge); R(d, x + 10, y + h, 1, 2, edge); R(d, x + 6, y + h + 2, 2, 1, bg); R(d, x + 6, y + h + 3, 3, 1, edge)
    elif tail == 'r':
        R(d, x + w - 10, y + h, 4, 2, bg); R(d, x + w - 6, y + h, 1, 3, edge); R(d, x + w - 11, y + h, 1, 2, edge); R(d, x + w - 8, y + h + 2, 2, 1, bg); R(d, x + w - 9, y + h + 3, 3, 1, edge)
    elif tail == 'think':
        for i, r in enumerate((2, 1)):
            disc(d, x + 8 - i * 4, y + h + 4 + i * 4, r + 1, edge); disc(d, x + 8 - i * 4, y + h + 4 + i * 4, r, bg)


def say(img, x, y, s, t=None, born=None, tail='l', bg=WHITE, fg=K, cps=16, os_=False):
    """说话 / 内心 OS 气泡（打字机效果）。x,y 为气泡左上角"""
    if born is not None:
        if t < born:
            return
        n = max(1, int((t - born) * cps) + 1)
    else:
        n = len(s)
    w = text_w(s) + 8
    if x + w > W - 2:
        x = W - 2 - w
    bubble_box(img, x, y, w, 15, (40, 30, 60) if os_ else bg, K, 'think' if os_ else tail)
    draw_text(img, x + 4, y + 2, s[:n], (255, 230, 120) if os_ else fg)


def OS(img, x, y, s, t, born):
    say(img, x, y, 'OS：' + s, t, born, os_=True)


def sys_msg(img, cx, y, s, col=(120, 120, 140)):
    w = text_w(s) + 12
    d = ImageDraw.Draw(img)
    R(d, cx - w // 2 + 2, y, w - 4, 15, col); R(d, cx - w // 2, y + 2, w, 11, col)
    draw_text(img, cx - w // 2 + 6, y + 2, s, WHITE)


def popup(img, x, y, title, msg, btns=('是', '否'), sel=0, pressed=False, w=150):
    """复古系统弹窗"""
    d = ImageDraw.Draw(img)
    h = 58
    R(d, x + 3, y + 3, w, h, (20, 16, 30))
    R(d, x, y, w, h, (200, 200, 210)); d.rectangle([x, y, x + w - 1, y + h - 1], outline=K)
    R(d, x + 1, y + 1, w - 2, 13, (40, 60, 170))
    draw_text(img, x + 4, y + 1, title, WHITE)
    R(d, x + w - 12, y + 3, 9, 9, (200, 200, 210)); draw_text(img, x + w - 11, y + 1, '×', K)
    draw_text(img, x + w // 2 - text_w(msg) // 2, y + 18, msg, K)
    bw = 40
    for i, b in enumerate(btns):
        bx = x + w // 2 - (len(btns) * (bw + 8)) // 2 + i * (bw + 8)
        by = y + 38
        dn = pressed and i == sel
        R(d, bx, by, bw, 15, K)
        R(d, bx + (1 if dn else 0), by + (1 if dn else 0), bw - 1, 14, (230, 230, 236) if not dn else (170, 170, 180))
        if i == sel:
            d.rectangle([bx + 2, by + 2, bx + bw - 3, by + 12], outline=(40, 60, 170))
        draw_text(img, bx + bw // 2 - text_w(b) // 2 + (1 if dn else 0), by + 1 + (1 if dn else 0), b, K)
    return x, y


def cursor(img, x, y):
    pat = ['X.....', 'XX....', 'XWX...', 'XWWX..', 'XWWWX.', 'XWWWWX', 'XWWXXX', 'XXWX..', '...X..']
    d = ImageDraw.Draw(img)
    for j, row in enumerate(pat):
        for i, c in enumerate(row):
            if c == 'X':
                d.point((x + i, y + j), fill=K)
            elif c == 'W':
                d.point((x + i, y + j), fill=WHITE)


def meter(img, x, y, label, v, col=(255, 70, 110), w=70, show_pct=True, blink=False):
    d = ImageDraw.Draw(img)
    lw = text_w(label)
    R(d, x - 2, y - 2, lw + w + 34, 18, (20, 16, 34))
    d.rectangle([x - 2, y - 2, x + lw + w + 31, y + 15], outline=WHITE)
    draw_text(img, x + 1, y + 1, label, WHITE)
    bx = x + lw + 5
    R(d, bx, y + 3, w, 8, (60, 56, 80))
    on = int(w * clamp(v))
    c = col if not (blink and int(hsh(int(v * 100)) * 2)) else WHITE
    for i in range(0, on, 3):
        R(d, bx + i, y + 3, 2, 8, c)
    if show_pct:
        draw_text(img, bx + w + 2, y + 1, f'{int(round(v * 100))}', (255, 230, 120))


def danmaku(img, t, items, t0=0.0, y0=18, rows=3, speed=70):
    """弹幕：items = [(出现时刻, 文字, 颜色)]"""
    for k, (ta, s, col) in enumerate(items):
        dt = t - ta
        if dt < 0:
            continue
        x = W - dt * speed
        w = text_w(s)
        if x < -w - 4:
            continue
        y = y0 + (k % rows) * 15
        draw_text(img, int(x), y, s, col, outline=K)


# ---------------- 会演戏的物件：小表情 ----------------
def face(img, cx, cy, expr='happy', k=1, col=K):
    """在物件上画一张小脸（eyes 间距 6k）"""
    d = ImageDraw.Draw(img)
    ex = 3 * k
    def eye(x, y):
        R(d, x, y, k, 2 * k, col)
    if expr in ('happy', 'smile'):
        eye(cx - ex, cy); eye(cx + ex - k + 1, cy)
        R(d, cx - k, cy + 3 * k, 2 * k + 1, k, col); d.point((cx - 2 * k, cy + 2 * k), fill=col); d.point((cx + 2 * k, cy + 2 * k), fill=col)
    elif expr == 'shock':
        R(d, cx - ex - k // 2, cy - k, 2 * k, 2 * k, col); R(d, cx + ex - k // 2, cy - k, 2 * k, 2 * k, col)
        R(d, cx - k, cy + 2 * k, 2 * k + 1, 3 * k, col)
    elif expr == 'sad':
        eye(cx - ex, cy); eye(cx + ex - k + 1, cy)
        R(d, cx - k, cy + 3 * k, 2 * k + 1, k, col); d.point((cx - 2 * k, cy + 4 * k), fill=col); d.point((cx + 2 * k, cy + 4 * k), fill=col)
        R(d, cx - ex, cy + 2 * k + 1, 1, 2, (120, 200, 255))
    elif expr == 'side':
        R(d, cx - ex - 1, cy + k, 3, 1, col); R(d, cx + ex - 1, cy + k, 3, 1, col)
        d.point((cx - ex + 1, cy + k + 1), fill=col); d.point((cx + ex + 1, cy + k + 1), fill=col)
        R(d, cx - k, cy + 3 * k, 2 * k + 1, 1, col)
    elif expr == 'sleep':
        R(d, cx - ex - 1, cy + 1, 3, 1, col); R(d, cx + ex - 1, cy + 1, 3, 1, col)
        R(d, cx, cy + 3 * k, 2, 2, col)
    elif expr == 'blush':
        d.point((cx - ex - 1, cy + 1), fill=col); d.point((cx - ex, cy), fill=col); d.point((cx - ex + 1, cy + 1), fill=col)
        d.point((cx + ex - 1, cy + 1), fill=col); d.point((cx + ex, cy), fill=col); d.point((cx + ex + 1, cy + 1), fill=col)
        R(d, cx - ex - 3, cy + 2, 2, 1, BLUSH); R(d, cx + ex + 2, cy + 2, 2, 1, BLUSH)
        R(d, cx - 1, cy + 3 * k, 3, 1, col)
    elif expr == 'smirk':
        eye(cx - ex, cy); eye(cx + ex - k + 1, cy)
        R(d, cx - k, cy + 3 * k, 2 * k, 1, col); d.point((cx + k + 1, cy + 3 * k - 1), fill=col)
    elif expr == 'scream':
        R(d, cx - ex - 1, cy - 1, 3, 1, col); R(d, cx + ex - 1, cy - 1, 3, 1, col)
        d.point((cx - ex, cy), fill=col); d.point((cx + ex, cy), fill=col)
        R(d, cx - 2 * k, cy + 2 * k, 4 * k + 1, 3 * k, col); R(d, cx - k, cy + 2 * k + 1, 2 * k + 1, 1, (230, 60, 80))
    elif expr == 'laugh':
        d.point((cx - ex - 1, cy + 1), fill=col); d.point((cx - ex, cy), fill=col); d.point((cx - ex + 1, cy + 1), fill=col)
        d.point((cx + ex - 1, cy + 1), fill=col); d.point((cx + ex, cy), fill=col); d.point((cx + ex + 1, cy + 1), fill=col)
        R(d, cx - 2 * k, cy + 2 * k, 4 * k + 1, 2 * k, col); R(d, cx - k, cy + 3 * k, 2 * k + 1, 1, (230, 60, 80))
    elif expr == 'heart':
        for x0 in (cx - ex, cx + ex):
            R(d, x0 - 1, cy - 1, 1, 1, HEART); R(d, x0 + 1, cy - 1, 1, 1, HEART); R(d, x0 - 1, cy, 3, 1, HEART); d.point((x0, cy + 1), fill=HEART)
        R(d, cx - k, cy + 3 * k, 2 * k + 1, 1, col)
    elif expr == 'dead':
        for x0 in (cx - ex, cx + ex):
            d.point((x0 - 1, cy - 1), fill=col); d.point((x0 + 1, cy + 1), fill=col); d.point((x0 + 1, cy - 1), fill=col); d.point((x0 - 1, cy + 1), fill=col); d.point((x0, cy), fill=col)
        R(d, cx - k, cy + 3 * k, 2 * k + 1, 1, col)


# ---------------- 猫咪配角 ----------------
CAT = (250, 190, 110)      # 橘猫
CAT_D = (210, 140, 70)
CAT_W = (255, 244, 230)


def cat(img, x, y, t=0.0, pose='sit', expr='normal', face_dir=1, scale=2, sign=None, glasses=False, hat=None, hearts=False):
    """橘猫：x,y 为脚底中点。pose: sit / walk / sleep / hiss / roll / up(举牌)"""
    im = Image.new('RGBA', (26, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tail = math.sin(t * 5) * 2
    if pose == 'sleep':
        ellipse_fill(d, 12, 17, 9, 4, CAT); R(d, 4, 14, 6, 6, CAT)
        R(d, 4, 11, 2, 3, CAT); R(d, 8, 11, 2, 3, CAT)
        R(d, 5, 16, 1, 1, K); R(d, 8, 16, 1, 1, K)
        for i in range(0, 14, 4):
            R(d, 10 + i, 14, 2, 1, CAT_D)
        d.line([(21, 18), (24, 15 + int(tail / 2))], fill=CAT, width=2)
    elif pose == 'roll':
        ellipse_fill(d, 13, 15, 9, 5, CAT_W); ellipse_fill(d, 13, 12, 9, 3, CAT)
        for (lx, ly) in ((6, 7), (9, 6), (17, 6), (20, 7)):
            R(d, lx + int(math.sin(t * 8 + lx) * 1), ly, 2, 4, CAT)
        R(d, 2, 13, 6, 6, CAT); R(d, 2, 19, 2, 2, CAT); R(d, 6, 19, 2, 2, CAT)
    else:
        walk = int(t * 8) % 2 if pose == 'walk' else 0
        # 身体
        ellipse_fill(d, 14, 15, 7, 5, CAT)
        R(d, 10, 14, 8, 4, CAT_W)
        for i in range(0, 10, 3):
            R(d, 14 + i // 2, 11, 1, 3, CAT_D)
        # 腿
        R(d, 9 + walk, 18, 2, 4, CAT); R(d, 13 - walk, 18, 2, 4, CAT); R(d, 16 + walk, 18, 2, 4, CAT); R(d, 19 - walk, 18, 2, 4, CAT)
        # 尾巴
        if pose == 'hiss':
            R(d, 21, 4, 2, 11, CAT); R(d, 20, 3, 4, 2, CAT_D)
        else:
            d.line([(21, 15), (24, 10 + int(tail)), (23, 6 + int(tail))], fill=CAT, width=2)
        # 头
        hx, hy = 7, 9
        ellipse_fill(d, hx, hy, 6, 5, CAT)
        R(d, hx - 6, hy - 7, 3, 4, CAT); R(d, hx + 3, hy - 7, 3, 4, CAT)
        d.point((hx - 5, hy - 5), fill=PINK); d.point((hx + 4, hy - 5), fill=PINK)
        R(d, hx - 2, hy - 4, 1, 3, CAT_D); R(d, hx + 1, hy - 4, 1, 3, CAT_D)
        R(d, hx - 3, hy + 2, 6, 3, CAT_W)
        # 表情
        if glasses:
            R(d, hx - 5, hy - 1, 11, 2, K)
        elif expr == 'side':
            R(d, hx - 4, hy, 2, 1, K); R(d, hx + 2, hy, 2, 1, K)
        elif expr == 'shock':
            R(d, hx - 4, hy - 1, 2, 2, K); R(d, hx + 2, hy - 1, 2, 2, K)
        elif expr == 'happy':
            d.point((hx - 4, hy), fill=K); d.point((hx - 3, hy - 1), fill=K); d.point((hx - 2, hy), fill=K)
            d.point((hx + 2, hy), fill=K); d.point((hx + 3, hy - 1), fill=K); d.point((hx + 4, hy), fill=K)
        elif expr == 'heart':
            for x0 in (hx - 3, hx + 3):
                d.point((x0 - 1, hy - 1), fill=HEART); d.point((x0 + 1, hy - 1), fill=HEART); R(d, x0 - 1, hy, 3, 1, HEART)
        elif expr == 'angry':
            R(d, hx - 4, hy, 2, 1, K); R(d, hx + 2, hy, 2, 1, K); d.point((hx - 4, hy - 2), fill=K); d.point((hx + 3, hy - 2), fill=K)
        elif expr == 'cover':
            R(d, hx - 5, hy - 1, 11, 3, CAT_W)
        else:
            R(d, hx - 4, hy - 1, 1, 2, K); R(d, hx + 3, hy - 1, 1, 2, K)
        d.point((hx, hy + 2), fill=PINK)
        if pose == 'hiss' or expr == 'angry':
            R(d, hx - 1, hy + 3, 3, 1, K)
        if pose == 'up':
            R(d, hx + 4, hy - 2, 2, 6, CAT)
        if hat == 'police':
            R(d, hx - 5, hy - 8, 11, 3, (40, 60, 140)); R(d, hx - 6, hy - 5, 13, 1, K); R(d, hx - 1, hy - 7, 2, 1, NEON_Y)
        elif hat == 'goggle':
            R(d, hx - 5, hy - 2, 11, 3, (90, 60, 40)); R(d, hx - 4, hy - 1, 3, 2, CYAN); R(d, hx + 1, hy - 1, 3, 2, CYAN)
    im = outline_rgba(im)
    if face_dir > 0:  # 画的时候猫头朝左；朝右时翻转
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = scaled(im, scale)
    paste(img, im, x - 13 * scale, y - 22 * scale)
    if sign:
        sw = text_w(sign) + 6
        d2 = ImageDraw.Draw(img)
        sx = x + (6 if face_dir > 0 else -6) * scale - sw // 2
        sy = y - 22 * scale - 16
        R(d2, sx + sw // 2, sy + 14, 1, 10, (130, 90, 60))
        R(d2, sx - 1, sy - 1, sw + 2, 16, K); R(d2, sx, sy, sw, 14, (255, 248, 230))
        draw_text(img, sx + 3, sy + 1, sign, K)
    if hearts:
        for i in range(2):
            ph = (t * 0.8 + i * 0.5) % 1
            heart(img, x + (i * 10 - 5), int(y - 22 * scale - ph * 16), 1)


# ---------------- 表情物件 ----------------
def moon(img, cx, cy, r=12, expr='happy', col=(250, 240, 200), blush=False):
    d = ImageDraw.Draw(img)
    disc(d, cx, cy, r + 1, K)
    disc(d, cx, cy, r, col)
    disc(d, cx - r // 3, cy - r // 3, r // 4, lerpc(col, (200, 190, 150), 0.5))
    disc(d, cx + r // 2, cy + r // 3, r // 6, lerpc(col, (200, 190, 150), 0.5))
    face(img, cx, cy - 1, expr, 1)
    if blush:
        R(d, cx - 7, cy + 2, 3, 1, BLUSH); R(d, cx + 5, cy + 2, 3, 1, BLUSH)


def sun(img, cx, cy, r=12, expr='happy', t=0.0):
    d = ImageDraw.Draw(img)
    for i in range(10):
        a = i / 10 * 6.283 + t * 0.6
        d.line([(cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3)), (cx + math.cos(a) * (r + 8), cy + math.sin(a) * (r + 8))], fill=(255, 200, 60), width=2)
    disc(d, cx, cy, r + 1, K); disc(d, cx, cy, r, (255, 220, 80))
    face(img, cx, cy - 1, expr, 1)


def lamp(img, x, ground, expr='happy', on=True, h=70):
    d = ImageDraw.Draw(img)
    R(d, x - 1, ground - h, 3, h, (60, 64, 90)); R(d, x - 4, ground - 3, 9, 3, (60, 64, 90))
    R(d, x - 1, ground - h, 14, 3, (60, 64, 90))
    R(d, x + 6, ground - h + 2, 14, 10, K); R(d, x + 7, ground - h + 3, 12, 8, (255, 230, 140) if on else (120, 120, 130))
    if on:
        a = np.asarray(img).astype(float)
        yy, xx = np.mgrid[0:H, 0:W]
        top = ground - h + 12
        m = (yy > top) & (yy < ground) & (np.abs(xx - (x + 13)) < 3 + (yy - top) * 0.45)
        m &= np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < 0.5
        a[m] = a[m] * 0.7 + np.array([255, 230, 150]) * 0.3
        img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    face(img, x + 13, ground - h + 5, expr, 1)


def trash_face(img, x, y, expr='happy', lid=0.0):
    d = ImageDraw.Draw(img)
    R(d, x - 1, y, 22, 26, K)
    R(d, x, y + 1, 20, 24, (130, 170, 140))
    for i in range(4, 20, 5):
        R(d, x + i, y + 14, 1, 10, (100, 140, 110))
    ly = y - 3 - int(lid * 6)
    R(d, x - 2, ly, 24, 4, K); R(d, x - 1, ly + 1, 22, 2, (110, 150, 120))
    face(img, x + 10, y + 6, expr, 1)


def clock_face(img, cx, cy, r, t, expr='scream', shake=True):
    d = ImageDraw.Draw(img)
    sh = int(math.sin(t * 50) * 2) if shake else 0
    cx += sh
    for bx in (-r + 1, r - 7):
        disc(d, cx + bx + 3, cy - r - 2, 4, K); disc(d, cx + bx + 3, cy - r - 2, 3, (240, 70, 80))
    disc(d, cx, cy, r + 2, K); disc(d, cx, cy, r, (255, 250, 235))
    for i in range(12):
        a = i / 12 * 6.283
        d.point((cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2)), fill=K)
    face(img, cx, cy - 2, expr, 2)
    R(d, cx - 6, cy + r + 1, 3, 4, K); R(d, cx + 4, cy + r + 1, 3, 4, K)


def calendar_face(img, x, y, label, expr='happy', flip=0.0):
    d = ImageDraw.Draw(img)
    R(d, x, y, 46, 48, K); R(d, x + 1, y + 1, 44, 46, (250, 250, 245)); R(d, x + 1, y + 1, 44, 11, (240, 70, 80))
    for i in (10, 34):
        R(d, x + i, y - 3, 2, 6, (120, 120, 140))
    draw_text(img, x + 23 - text_w(label) // 2, y + 14, label, K)
    face(img, x + 23, y + 32, expr, 1)
    if flip > 0:
        R(d, x + 1, y + 12, 44, int(35 * (1 - flip)), (225, 225, 220))
        R(d, x + 1, y + 12 + int(35 * (1 - flip)), 44, 1, (180, 180, 180))


def phone_face(img, x, y, w=60, h=104, expr=None):
    d = ImageDraw.Draw(img)
    R(d, x, y, w, h, K); R(d, x + 2, y + 2, w - 4, h - 4, (36, 36, 52))
    R(d, x + 4, y + 10, w - 8, h - 18, (238, 240, 248))
    R(d, x + 4, y + 10, w - 8, 11, (110, 160, 250))
    R(d, x + w // 2 - 6, y + 4, 12, 2, (80, 80, 100))
    if expr:
        face(img, x + w // 2, y + 5, expr, 1, (200, 200, 220))


def heart_face(img, cx, cy, k=2, expr='happy', broken=False, col=HEART):
    heart(img, cx, cy, k, col, broken)
    if k >= 2 and not broken:
        face(img, cx, cy - k // 2, expr, 1 if k < 4 else 2, K)


def building_face(img, x, ground, w, h, expr='shock', col=(46, 38, 90), win=(255, 210, 120)):
    """一栋会做表情的楼：窗户亮灯拼出眼睛和嘴"""
    d = ImageDraw.Draw(img)
    R(d, x, ground - h, w, h, col); R(d, x, ground - h, w, 2, lerpc(col, WHITE, 0.25))
    for wy in range(ground - h + 6, ground - 4, 7):
        for wx in range(x + 4, x + w - 5, 6):
            R(d, wx, wy, 3, 4, lerpc(col, K, 0.3))
    cx, cy = x + w // 2, ground - h + h // 3
    ex = w // 4
    def lit(px, py, ww, hh):
        R(d, px, py, ww, hh, win)
    if expr == 'shock':
        lit(cx - ex - 3, cy, 6, 8); lit(cx + ex - 3, cy, 6, 8); lit(cx - 4, cy + 16, 9, 10)
    elif expr == 'heart':
        for x0 in (cx - ex, cx + ex):
            lit(x0 - 4, cy, 3, 3); lit(x0 + 1, cy, 3, 3); lit(x0 - 4, cy + 3, 8, 3); lit(x0 - 2, cy + 6, 4, 2)
        lit(cx - 5, cy + 18, 11, 3)
    elif expr == 'happy':
        lit(cx - ex - 2, cy + 2, 5, 3); lit(cx + ex - 2, cy + 2, 5, 3); lit(cx - 6, cy + 16, 13, 3); lit(cx - 8, cy + 13, 3, 3); lit(cx + 6, cy + 13, 3, 3)
    elif expr == 'side':
        lit(cx - ex - 3, cy + 3, 7, 3); lit(cx + ex - 3, cy + 3, 7, 3); lit(cx - 3, cy + 17, 7, 2)
    elif expr == 'sad':
        lit(cx - ex - 2, cy + 2, 5, 3); lit(cx + ex - 2, cy + 2, 5, 3); lit(cx - 6, cy + 18, 13, 3); lit(cx - 8, cy + 21, 3, 3); lit(cx + 6, cy + 21, 3, 3)


def big_heart_building(img, ground, t, k=1.0):
    """楼群窗户亮成一颗心"""
    pts = []
    for i in range(240):
        a = i / 240 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((160 + x * 3.4, 60 + y * 3.2))
    d = ImageDraw.Draw(img)
    n = int(len(pts) * clamp(k))
    for (x, y) in pts[:n:4]:
        R(d, int(x) - 1, int(y) - 1, 3, 3, (255, 120, 170) if int(t * 4 + x) % 3 else (255, 230, 130))


# ---------------- 场景道具 ----------------
def ferris(img, cx, cy, r, t, col=(255, 140, 200)):
    d = ImageDraw.Draw(img)
    d.line([(cx, cy), (cx - r * 0.6, cy + r + 10)], fill=(180, 180, 200), width=2)
    d.line([(cx, cy), (cx + r * 0.6, cy + r + 10)], fill=(180, 180, 200), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
    for i in range(8):
        a = i / 8 * 6.283 + t * 0.4
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line([(cx, cy), (x, y)], fill=lerpc(col, WHITE, 0.4))
        R(d, int(x) - 3, int(y), 7, 6, [NEON_Y, NEON_B, PINK, (140, 230, 120)][i % 4])
        R(d, int(x) - 3, int(y), 7, 1, K)


def mountains(img, scroll=0.0, ground=128):
    d = ImageDraw.Draw(img)
    for col, base, amp, sp, f in (((140, 160, 220), 60, 26, 0.3, 0.035), ((90, 140, 120), 90, 18, 0.7, 0.06)):
        for x in range(W):
            xx = x + scroll * sp
            hgt = base - amp * (0.6 * math.sin(xx * f) + 0.4 * math.sin(xx * f * 2.3 + 1))
            d.line([(x, int(hgt)), (x, ground)], fill=col)
            if col[0] == 140 and hgt < base - amp * 0.7:
                d.point((x, int(hgt)), fill=WHITE)


def wave_sea(img, t, y0=110, col=(60, 150, 220)):
    d = ImageDraw.Draw(img)
    R(d, 0, y0, W, H - y0, col)
    for i in range(30):
        x = int((hsh(i, 1) * W + t * 20 * (1 if i % 2 else -1)) % W)
        y = y0 + 3 + int(hsh(i, 2) * (H - y0 - 6))
        R(d, x, y, 6, 1, lerpc(col, WHITE, 0.6))


def slot_machine(img, x, y, t, stops, results, lever=0.0):
    """老虎机：stops=每格停的时刻，results=停下的表情"""
    d = ImageDraw.Draw(img)
    R(d, x, y, 120, 70, K); R(d, x + 2, y + 2, 116, 66, (220, 60, 90))
    R(d, x + 6, y + 6, 108, 12, (40, 20, 40)); draw_text(img, x + 60 - text_w('情绪机') // 2, y + 6, '情绪机', NEON_Y)
    faces_ = ['sad', 'side', 'happy', 'heart']
    for i in range(3):
        bx = x + 10 + i * 35
        R(d, bx, y + 22, 30, 32, WHITE)
        if t < stops[i]:
            f = faces_[int(t * 14 + i * 3) % 4]
            off = int((t * 140) % 8)
        else:
            f = results[i]; off = 0
        if f == 'heart':
            heart_face(img, bx + 15, y + 38 + off - 4, 2, 'happy')
        else:
            disc(d, bx + 15, y + 38 + off - 4, 9, (255, 220, 80)); face(img, bx + 15, y + 36 + off - 4, f, 1)
    # 拉杆
    ly = y + 10 + int(lever * 30)
    R(d, x + 120, y + 20, 4, 30, (160, 160, 170)); d.line([(x + 124, y + 34), (x + 130, ly)], fill=(160, 160, 170), width=2)
    disc(d, x + 130, ly, 4, (240, 60, 70))


def interrogation(img, t, swing=True):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (34, 34, 44))
    for x in range(0, W, 20):
        R(d, x, 0, 1, 128, (40, 40, 52))
    R(d, 0, 128, W, H - 128, (54, 50, 60))
    ang = math.sin(t * 2.2) * 0.25 if swing else 0
    lx, ly = 160 + math.sin(ang) * 40, 40
    d.line([(160, 0), (lx, ly)], fill=(20, 20, 26), width=1)
    d.polygon([(lx - 10, ly + 8), (lx + 10, ly + 8), (lx + 5, ly), (lx - 5, ly)], fill=(70, 80, 70))
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    m = (yy > ly + 8) & (np.abs(xx - (lx + (yy - ly) * math.sin(ang))) < 6 + (yy - ly) * 0.55)
    m &= np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < 0.6
    a[m] = a[m] * 0.6 + np.array([255, 245, 190]) * 0.4
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    R(d, 110, 118, 100, 6, (110, 80, 60)); R(d, 116, 124, 4, 16, (90, 60, 50)); R(d, 200, 124, 4, 16, (90, 60, 50))


def scroll_list(img, x, y, items, k, t):
    d = ImageDraw.Draw(img)
    n = int(len(items) * k + 0.999) if k > 0 else 0
    hgt = 8 + n * 14
    R(d, x, y, 96, hgt, (250, 236, 200)); R(d, x - 3, y - 4, 102, 5, (200, 160, 100)); R(d, x - 3, y + hgt, 102, 5, (200, 160, 100))
    for i in range(n):
        draw_text(img, x + 5, y + 4 + i * 14, items[i], (120, 40, 40))


def megaphone(img, x, y, t, face_dir=1):
    d = ImageDraw.Draw(img)
    s = face_dir
    d.polygon([(x, y - 3), (x + 14 * s, y - 9), (x + 14 * s, y + 9), (x, y + 3)], fill=(240, 240, 250), outline=K)
    R(d, x - (4 if s > 0 else 0), y - 2, 4, 5, (240, 80, 90))
    for i in range(3):
        ph = (t * 3 + i / 3) % 1
        rr = 6 + ph * 22
        d.arc([x + 14 * s - rr, y - rr, x + 14 * s + rr, y + rr], -40 if s > 0 else 140, 40 if s > 0 else 220, fill=NEON_Y)


def firework(img, cx, cy, t, born, col):
    dt = t - born
    if dt < 0 or dt > 1.4:
        return
    d = ImageDraw.Draw(img)
    if dt < 0.3:
        R(d, cx, int(cy + (0.3 - dt) * 200), 1, 4, col)
        return
    p = (dt - 0.3) / 1.1
    for i in range(16):
        a = i / 16 * 6.283
        r = p * 26
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r + p * p * 8
        if hsh(i, int(t * 10)) > p * 0.6:
            R(d, int(x), int(y), 2, 2, col if i % 2 else WHITE)


def clapper(img, x, y, t, snap):
    d = ImageDraw.Draw(img)
    R(d, x, y + 8, 50, 30, K); R(d, x + 1, y + 9, 48, 28, (40, 40, 50))
    draw_text(img, x + 4, y + 11, '第38条', WHITE)
    draw_text(img, x + 4, y + 23, '演技 ×', (255, 120, 120))
    ang = 0 if snap else -0.4
    for i in range(6):
        c = WHITE if i % 2 else K
        x0 = x + i * 8.3
        d.polygon([(x0, y + 8), (x0 + 8, y + 8), (x0 + 8 + math.sin(ang) * 0, y + 2 + ang * 20 * (i / 6)), (x0, y + 2 + ang * 20 * (i / 6))], fill=c)


def score_card(img, x, y, s):
    d = ImageDraw.Draw(img)
    R(d, x + 9, y + 18, 2, 12, (130, 90, 60))
    R(d, x - 1, y - 1, 22, 20, K); R(d, x, y, 20, 18, WHITE)
    draw_text(img, x + 10 - text_w(s) // 2, y + 3, s, (230, 40, 60))


def safe_box(img, x, y, closed, locked):
    d = ImageDraw.Draw(img)
    R(d, x, y, 44, 40, K); R(d, x + 1, y + 1, 42, 38, (120, 130, 150))
    if closed:
        R(d, x + 3, y + 3, 38, 34, (150, 160, 180)); disc(d, x + 22, y + 20, 6, K); disc(d, x + 22, y + 20, 4, (200, 200, 210))
        draw_text(img, x + 22 - text_w('封存') // 2, y + 28 - 6 + 10, '', K)
    else:
        R(d, x + 3, y + 3, 38, 34, (30, 30, 40))
        R(d, x - 30, y + 2, 30, 36, (150, 160, 180)); R(d, x - 30, y + 2, 30, 36, (150, 160, 180))
    if locked:
        R(d, x + 16, y + 30, 12, 9, (240, 200, 60)); d.arc([x + 17, y + 23, x + 27, y + 33], 180, 360, fill=K, width=2)


def runway(img, t, v2=False):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (20, 14, 34) if not v2 else (40, 10, 50))
    d.polygon([(130, 70), (190, 70), (300, H), (20, H)], fill=(70, 60, 100))
    for i in range(8):
        y = 74 + i * 14
        k = (y - 70) / 110
        xl, xr = 130 - 110 * k, 190 + 110 * k
        on = (int(t * 4) + i) % 2
        R(d, int(xl) - 2, y, 3, 2, NEON_Y if on else (120, 110, 60)); R(d, int(xr), y, 3, 2, NEON_Y if on else (120, 110, 60))
    for cx in (40, 280):
        for i in range(3):
            R(d, cx - 20 + i * 14, 50, 10, 6, K)
            disc(d, cx - 15 + i * 14, 60, 2, WHITE if int(t * 6 + i + cx) % 3 else NEON_Y)


def rainbow(img, cx, cy, r, k=1.0):
    d = ImageDraw.Draw(img)
    cols = [(240, 70, 80), (255, 150, 60), (255, 230, 90), (100, 210, 110), (80, 160, 250), (150, 100, 230)]
    ang = 180 + 180 * clamp(k)
    for i, c in enumerate(cols):
        rr = r - i * 3
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, ang, fill=c, width=3)


def toggle(img, x, y, label, on):
    d = ImageDraw.Draw(img)
    lw = text_w(label)
    R(d, x - 2, y - 2, lw + 40, 18, (20, 16, 34)); d.rectangle([x - 2, y - 2, x + lw + 37, y + 15], outline=WHITE)
    draw_text(img, x + 1, y + 1, label, WHITE)
    bx = x + lw + 6
    R(d, bx, y + 2, 26, 10, (90, 220, 120) if on else (120, 120, 130))
    disc(d, bx + (20 if on else 5), y + 7, 4, WHITE)


# ---------------- 更多配角：小狗、会演戏的小物件 ----------------
DOG = (236, 236, 236)
DOG_D = (190, 170, 150)
DOG_E = (150, 110, 80)


def dog(img, x, y, t=0.0, pose='sit', expr='normal', face_dir=1, scale=2, sign=None, hearts=False, col=DOG, ear=DOG_E):
    """小狗（垂耳、摇尾巴）。pose: sit / walk / up(举牌) / jump。参数和 cat() 一致，方便互换。"""
    im = Image.new('RGBA', (26, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wag = int(math.sin(t * 14) * 2)
    walk = int(t * 8) % 2 if pose == 'walk' else 0
    jump = int(abs(math.sin(t * 8)) * 3) if pose == 'jump' else 0
    oy = -jump
    ellipse_fill(d, 15, 15 + oy, 7, 5, col)
    R(d, 11, 16 + oy, 8, 3, lerpc(col, WHITE, 0.4))
    R(d, 9 + walk, 18 + oy, 2, 4, col); R(d, 13 - walk, 18 + oy, 2, 4, col); R(d, 17 + walk, 18 + oy, 2, 4, col); R(d, 20 - walk, 18 + oy, 2, 4, col)
    d.line([(21, 13 + oy), (24, 9 + wag + oy)], fill=col, width=2)
    hx, hy = 7, 9 + oy
    ellipse_fill(d, hx, hy, 6, 5, col)
    R(d, hx - 7, hy - 3, 3, 7, ear); R(d, hx + 4, hy - 3, 3, 7, ear)       # 垂耳
    R(d, hx - 2, hy + 2, 5, 3, lerpc(col, WHITE, 0.5)); R(d, hx - 1, hy + 1, 3, 2, K)  # 鼻子
    if expr == 'happy':
        d.point((hx - 4, hy - 1), fill=K); d.point((hx - 3, hy - 2), fill=K); d.point((hx - 2, hy - 1), fill=K)
        d.point((hx + 2, hy - 1), fill=K); d.point((hx + 3, hy - 2), fill=K); d.point((hx + 4, hy - 1), fill=K)
        R(d, hx, hy + 5, 2, 2, (240, 100, 120))   # 吐舌头
    elif expr == 'shock':
        R(d, hx - 4, hy - 2, 2, 2, K); R(d, hx + 2, hy - 2, 2, 2, K)
    elif expr == 'sad':
        R(d, hx - 4, hy - 1, 2, 1, K); R(d, hx + 2, hy - 1, 2, 1, K); R(d, hx - 4, hy + 1, 1, 2, (120, 200, 255))
    elif expr == 'heart':
        for x0 in (hx - 3, hx + 3):
            d.point((x0 - 1, hy - 2), fill=HEART); d.point((x0 + 1, hy - 2), fill=HEART); R(d, x0 - 1, hy - 1, 3, 1, HEART)
    elif expr == 'side':
        R(d, hx - 4, hy - 1, 2, 1, K); R(d, hx + 2, hy - 1, 2, 1, K)
    else:
        R(d, hx - 4, hy - 2, 1, 2, K); R(d, hx + 3, hy - 2, 1, 2, K)
    if pose == 'up':
        R(d, hx + 4, hy - 1, 2, 6, col)
    im = outline_rgba(im)
    if face_dir > 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = scaled(im, scale)
    paste(img, im, x - 13 * scale, y - 22 * scale)
    if sign:
        sw = text_w(sign) + 6
        d2 = ImageDraw.Draw(img)
        sx = x + (6 if face_dir > 0 else -6) * scale - sw // 2
        sy = y - 22 * scale - 16
        R(d2, sx + sw // 2, sy + 14, 1, 10, (130, 90, 60))
        R(d2, sx - 1, sy - 1, sw + 2, 16, K); R(d2, sx, sy, sw, 14, (255, 248, 230))
        draw_text(img, sx + 3, sy + 1, sign, K)
    if hearts:
        for i in range(2):
            ph = (t * 0.8 + i * 0.5) % 1
            heart(img, x + (i * 10 - 5), int(y - 22 * scale - ph * 16), 1)


def cloud_face(img, cx, cy, expr='happy', col=(250, 250, 255), k=1.0):
    """会演戏的云朵（下雨天的配角、天气类歌曲的贯穿物件）"""
    d = ImageDraw.Draw(img)
    for (dx, dy, r) in ((-10, 2, 7), (0, -3, 9), (10, 2, 7)):
        disc(d, cx + dx, cy + dy, int(r * k) + 1, K)
    for (dx, dy, r) in ((-10, 2, 7), (0, -3, 9), (10, 2, 7)):
        disc(d, cx + dx, cy + dy, int(r * k), col)
    face(img, cx, cy - 1, expr, 1)


def star_face(img, cx, cy, r=9, expr='happy', col=(255, 226, 90)):
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.5
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=col, outline=K)
    face(img, cx, cy - 1, expr, 1)


def cup_face(img, cx, cy, expr='happy', col=(250, 246, 236), drink=(150, 90, 60), steam=0.0):
    """一杯会演戏的饮料（咖啡/奶茶），t 传给 steam 让热气飘"""
    d = ImageDraw.Draw(img)
    R(d, cx - 9, cy - 8, 18, 18, K); R(d, cx - 8, cy - 7, 16, 16, col); R(d, cx - 8, cy - 7, 16, 3, drink)
    d.arc([cx + 6, cy - 4, cx + 14, cy + 4], -90, 90, fill=K, width=2)
    face(img, cx, cy + 1, expr, 1)
    for i in range(2):
        ph = (steam * 0.7 + i * 0.5) % 1
        R(d, cx - 3 + i * 5 + int(math.sin(ph * 6) * 1), int(cy - 10 - ph * 10), 1, 3, (230, 230, 240))
