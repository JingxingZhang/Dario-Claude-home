"""角色设计工具：每首歌的主角、配角都在项目里从零设计，不套现成形象。

最常用的是 pixmap：用字符画逐像素画精灵，一个字符一个像素，配一张调色表。
    BODY = '''
    ....hhhh....
    ...hhhhhh...
    ...hssssh...
    ...sKsKss...
    ....ssss....
    ...cccccc...
    ..cccccccc..
    ...cc..cc...
    ...LL..LL...
    '''
    PAL = {'h': (40,30,30), 's': (250,210,180), 'K': (20,16,30), 'c': (90,160,120), 'L': (60,60,90)}
    spr = pixmap(BODY, PAL)                         # RGBA 精灵，自动描边
    put(img, spr, x, y, scale=3, face=-1)           # x,y 为脚底中点，face=-1 朝左
多帧动画：准备几张字符画（站、走 1、走 2、挥手……），按 lt 选帧，例如 frames[int(lt*8) % 2]。
表情：五官先在字符画里留空，再用 eyes()/mouth() 叠上去；或者为每个表情各画一张头部字符画，和身体拼起来。
人物比例按歌定：2 头身 Q 版（可爱、搞笑）、3 头身（日常）、5–6 头身（抒情、成熟）、非人（动物、物件、一团光）都可以。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from pixlib import lerpc, WHITE

K = (34, 24, 44)


def _parse(art):
    rows = [r.rstrip() for r in art.strip('\n').split('\n')]
    ind = min(len(r) - len(r.lstrip()) for r in rows if r.strip())
    rows = [r[ind:] for r in rows]
    w = max(len(r) for r in rows)
    return [r.ljust(w, '.') for r in rows]


def pixmap(art, pal, outline=K, shade=None):
    """字符画 → RGBA 精灵。'.' 和空格是透明；outline=None 不描边；shade=(字符, 比例) 可自动生成暗面色"""
    return _pixmap(art, tuple(sorted(pal.items())), outline)


@lru_cache(maxsize=512)
def _pixmap(art, pal_items, outline):
    pal = dict(pal_items)
    rows = _parse(art)
    h, w = len(rows), len(rows[0])
    a = np.zeros((h + 2, w + 2, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in '. ':
                continue
            col = pal.get(c)
            if col is None:
                raise KeyError(f'调色表里没有字符 {c!r}')
            a[y + 1, x + 1] = (*col[:3], col[3] if len(col) > 3 else 255)
    if outline is not None:
        m = a[:, :, 3] > 0
        d = m.copy()
        d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
        a[d & ~m] = (*outline, 255)
    return Image.fromarray(a, 'RGBA')


def put(img, spr, x, y, scale=1, face=1, anchor='feet'):
    """把精灵贴到画布：anchor='feet' 时 x,y 为脚底中点；'center' 为中心；'topleft' 为左上角"""
    if face < 0:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1:
        spr = spr.resize((spr.width * scale, spr.height * scale), Image.NEAREST)
    if anchor == 'feet':
        x, y = x - spr.width // 2, y - spr.height
    elif anchor == 'center':
        x, y = x - spr.width // 2, y - spr.height // 2
    img.paste(spr, (int(round(x)), int(round(y))), spr)
    return spr.width, spr.height


def recolor(art_pal, **over):
    """复制一份调色表并替换部分颜色（同一角色换季、换装，随故事时间线换色时用）"""
    p = dict(art_pal); p.update(over); return p


def shade(col, k=0.3):
    return lerpc(col, K, k)


def light(col, k=0.3):
    return lerpc(col, WHITE, k)


def eyes(img, x, y, kind='dot', gap=4, col=K, scale=1):
    """在 (x,y) 起画一双眼睛（左眼左上角），gap 为两眼间距（原生像素，未放大前）。
    kind：dot 圆点 / tall 竖条 / closed ^^ / line 一字 / wide 大眼 / heart 心形 / x 晕 / sad 下垂 / angry 斜眉"""
    d = ImageDraw.Draw(img)
    s = scale
    def px(a, b, c=col):
        d.rectangle([x + a * s, y + b * s, x + a * s + s - 1, y + b * s + s - 1], fill=c)
    for ox in (0, gap):
        if kind == 'dot':
            px(ox, 0)
        elif kind == 'tall':
            px(ox, 0); px(ox, 1)
        elif kind == 'closed':
            px(ox - 1, 1); px(ox, 0); px(ox + 1, 1)
        elif kind == 'line':
            px(ox - 1, 1); px(ox, 1); px(ox + 1, 1)
        elif kind == 'wide':
            px(ox, 0); px(ox + 1, 0); px(ox, 1); px(ox + 1, 1); px(ox, 0, WHITE)
        elif kind == 'heart':
            px(ox - 1, 0, (240, 60, 100)); px(ox + 1, 0, (240, 60, 100)); px(ox - 1, 1, (240, 60, 100)); px(ox, 1, (240, 60, 100)); px(ox + 1, 1, (240, 60, 100)); px(ox, 2, (240, 60, 100))
        elif kind == 'x':
            px(ox - 1, -1); px(ox + 1, 1); px(ox, 0); px(ox + 1, -1); px(ox - 1, 1)
        elif kind == 'sad':
            px(ox, 1); px(ox + (1 if ox == 0 else -1), -1)
        elif kind == 'angry':
            px(ox, 1); px(ox + (-1 if ox == 0 else 1), -1); px(ox, 0)


def mouth(img, x, y, kind='smile', col=K, scale=1):
    """嘴：smile 微笑 / grin 大笑（带红） / o 惊讶 / flat 一字 / sad 撇嘴 / smirk 坏笑 / wave 波浪（委屈）"""
    d = ImageDraw.Draw(img)
    s = scale
    def px(a, b, c=col):
        d.rectangle([x + a * s, y + b * s, x + a * s + s - 1, y + b * s + s - 1], fill=c)
    pts = {
        'smile': [(0, 0), (1, 1), (2, 1), (3, 0)],
        'grin': [(0, 0), (1, 0), (2, 0), (3, 0), (1, 1), (2, 1)],
        'o': [(1, 0), (2, 0), (1, 1), (2, 1)],
        'flat': [(0, 0), (1, 0), (2, 0), (3, 0)],
        'sad': [(0, 1), (1, 0), (2, 0), (3, 1)],
        'smirk': [(0, 1), (1, 1), (2, 1), (3, 0)],
        'wave': [(0, 1), (1, 0), (2, 1), (3, 0)],
    }[kind]
    for a, b in pts:
        px(a, b)
    if kind == 'grin':
        px(1, 1, (230, 70, 90)); px(2, 1, (230, 70, 90))


def palette_strip(img, x, y, cols, size=8):
    """设定图上的配色条"""
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cols):
        d.rectangle([x + i * (size + 2), y, x + i * (size + 2) + size - 1, y + size - 1], fill=c, outline=K)
