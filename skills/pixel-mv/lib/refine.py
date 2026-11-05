"""角色精修渲染管线（迭代二画风的人物部分）：让字符画小人更圆润、有体积、五官更细。

    字符画 → Scale2x 放大（斜边自动变圆润，原生 2 倍细节，不产生新颜色）
           → 体积光影（左上受光 1px 高光带、右下暗带）
           → 彩色描边（取相邻颜色的深色，不用死黑；底边更深）
           → 高清五官（画在画布像素上：2×3 眼睛带眼神光、细嘴、点状腮红）

用法（在项目的角色函数里）：
    from refine import render_char, refined_sprite, EXPR
    render_char(img, art, pal, x, y, face_dir, eye=(5, 5, 4), mth=(6, 8), expr='smile')
      art/pal：和 charkit.pixmap 一样的字符画和调色表（五官位置留空）
      eye=(x, y, gap)：左眼在字符画里的列、行，和两眼间距；mth=(x, y)：嘴左端的列、行
      x, y：脚底中点（原生画布坐标），face_dir：1 朝右、-1 朝左
    refined_sprite(art, pal) -> RGBA 精灵（没有五官的物件、宠物用，比如一片会演戏的叶子）
精修后的角色比原来 scale=2 的大小一样（原生字符画 1 格 = 画布 2 像素），可以直接替换。
配色建议：低饱和、干净，不用纯黑（见 references/visual-design.md 的“迭代二画风”）。
"""
import numpy as _np
from functools import lru_cache as _lru
from PIL import Image, ImageDraw
from charkit import pixmap

FACE_INK = (48, 38, 60)
# 表情：(眼, 嘴, 腮红)。眼：dot 圆点 / wide 睁大 / closed 笑眯 / line 一字 / heart 心心眼 / sad 下垂；
# 嘴：smile flat grin o sad smirk wave zip
EXPR = {
    'normal': ('dot', 'flat', False), 'smile': ('dot', 'smile', False), 'happy': ('closed', 'grin', False),
    'blush': ('closed', 'smile', True), 'shock': ('wide', 'o', False), 'stuck': ('line', 'wave', False),
    'think': ('dot', 'smirk', False), 'sad': ('sad', 'sad', False), 'heart': ('heart', 'smile', True),
    'zip': ('dot', 'zip', True),
}


def _pack(a):
    a = a.astype(_np.uint32)
    return (a[..., 0] << 24) | (a[..., 1] << 16) | (a[..., 2] << 8) | a[..., 3]


def scale2x(a):
    """经典 Scale2x（EPX）：把像素画放大两倍，斜线自动变平滑，不产生新颜色"""
    p = _pack(a)
    P = _np.pad(p, 1, mode='edge')
    A, B, C, D = P[:-2, 1:-1], P[1:-1, 2:], P[1:-1, :-2], P[2:, 1:-1]
    h, w = p.shape
    out = _np.zeros((h * 2, w * 2, 4), _np.uint8)
    idx = {}
    for key, cond, src in (('e0', (C == A) & (C != D) & (A != B), 'C'), ('e1', (A == B) & (A != C) & (B != D), 'B'),
                           ('e2', (D == C) & (D != B) & (C != A), 'C'), ('e3', (B == D) & (B != A) & (D != C), 'B')):
        idx[key] = (cond, src)
    Pa = _np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    nb = {'B': Pa[1:-1, 2:], 'C': Pa[1:-1, :-2]}
    for k, (oy, ox) in (('e0', (0, 0)), ('e1', (0, 1)), ('e2', (1, 0)), ('e3', (1, 1))):
        cond, src = idx[k]
        out[oy::2, ox::2] = _np.where(cond[..., None], nb[src], a)
    return out


def _lt(c, k):
    return c + (255 - c) * k


def refine_rgba(a, light=0.12, dark=0.13, outline=0.55):
    """在已放大的 RGBA 数组上加体积光影和彩色描边，返回新数组（四周各多 1px 描边）"""
    a = _np.pad(a, ((1, 1), (1, 1), (0, 0)))
    m = a[..., 3] > 0
    rgb = a[..., :3].astype(float)
    up = _np.zeros_like(m); up[1:] = m[:-1]
    lf = _np.zeros_like(m); lf[:, 1:] = m[:, :-1]
    dn = _np.zeros_like(m); dn[:-1] = m[1:]
    rt = _np.zeros_like(m); rt[:, :-1] = m[:, 1:]
    dn2 = _np.zeros_like(m); dn2[:-2] = m[2:]
    rt2 = _np.zeros_like(m); rt2[:, :-2] = m[:, 2:]
    hi = m & (~up | ~lf)
    sh = m & (~dn | ~rt | ~dn2) & ~hi
    rgb[hi] = _lt(rgb[hi], light)
    rgb[sh] = rgb[sh] * (1 - dark)
    # 彩色描边：取相邻像素颜色的深色
    o = _np.zeros_like(rgb); got = _np.zeros_like(m)
    for dy, dx, k in ((-1, 0, outline + 0.12), (1, 0, outline - 0.05), (0, -1, outline), (0, 1, outline)):
        src_m = _np.roll(m, (dy, dx), (0, 1)); src_c = _np.roll(rgb, (dy, dx), (0, 1))
        sel = ~m & src_m & ~got
        o[sel] = src_c[sel] * (1 - k) + _np.array(FACE_INK) * k * 0.5
        got |= sel
    out = _np.zeros_like(a)
    out[..., :3] = _np.where(m[..., None], rgb, o).clip(0, 255)
    out[..., 3] = _np.where(m | got, 255, 0)
    return out.astype(_np.uint8)


@_lru(maxsize=256)
def _refined(art, pal_items):
    pal = dict(pal_items)
    base = pixmap(art, pal, outline=None)
    return Image.fromarray(refine_rgba(scale2x(_np.asarray(base))), 'RGBA')


def _px(d, x, y, c):
    d.point((int(x), int(y)), fill=c)


def face_hd(img, ex, ey, gap, mx, my, expr, skin=(252, 222, 198)):
    """高清五官（画在画布像素上，比角色的像素细一倍）：ex,ey 左眼左上角；gap 两眼间距（画布像素）；mx,my 嘴中心"""
    e, m, bl = EXPR[expr]
    d = ImageDraw.Draw(img)
    INKc, W_ = FACE_INK, (255, 255, 255)
    for k, x in enumerate((ex, ex + gap)):
        if e in ('dot', 'wide'):
            hgt = 3 if e == 'dot' else 4
            d.rectangle([x, ey, x + 1, ey + hgt - 1], fill=INKc)
            if e == 'wide':
                d.rectangle([x - 1, ey + 1, x + 2, ey + 2], fill=INKc)
            _px(d, x + (1 if k == 0 else 0), ey, W_)
        elif e == 'closed':
            _px(d, x - 1, ey + 2, INKc); _px(d, x, ey + 1, INKc); _px(d, x + 1, ey + 1, INKc); _px(d, x + 2, ey + 2, INKc)
        elif e == 'line':
            d.line([(x - 1, ey + 2), (x + 2, ey + 2)], fill=INKc)
        elif e == 'heart':
            pk = (236, 80, 110)
            for yy, row in enumerate(('X.X', 'XXX', '.X.')):
                for xx, ch in enumerate(row):
                    if ch == 'X':
                        _px(d, x - 1 + xx + (0 if k == 0 else 0), ey + yy, pk)
            _px(d, x - 1, ey, (255, 200, 210))
        elif e == 'sad':
            d.rectangle([x, ey + 1, x + 1, ey + 2], fill=INKc)
            _px(d, x + (-1 if k == 0 else 2), ey - 1, INKc); _px(d, x + (0 if k == 0 else 1), ey - 1, INKc)
    mc = (150, 70, 84)
    pts = {'smile': [(-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)], 'flat': [(-1, 1), (0, 1), (1, 1)],
           'sad': [(-2, 1), (-1, 0), (0, 0), (1, 0), (2, 1)], 'smirk': [(-1, 1), (0, 1), (1, 1), (2, 0)],
           'wave': [(-2, 1), (-1, 0), (0, 1), (1, 0), (2, 1)]}
    if m == 'grin':
        d.rectangle([mx - 2, my, mx + 2, my + 2], fill=mc); d.rectangle([mx - 1, my + 2, mx + 1, my + 2], fill=(240, 120, 130))
        d.line([(mx - 2, my), (mx + 2, my)], fill=(255, 255, 255))
    elif m == 'o':
        d.rectangle([mx - 1, my, mx, my + 2], fill=mc)
    elif m == 'zip':
        for i in range(-3, 4):
            _px(d, mx + i, my + 1, (200, 200, 214) if i % 2 else INKc)
    else:
        for (dx, dy) in pts.get(m, pts['smile']):
            _px(d, mx + dx, my + dy, mc)
    if bl:
        bc = tuple(int(skin[i] * 0.45 + (246, 140, 150)[i] * 0.55) for i in range(3))
        for bx in (ex - 3, ex + gap + 2):
            d.rectangle([bx, my - 2, bx + 2, my - 2], fill=bc); _px(d, bx + 1, my - 1, bc)


def render_char(img, art, pal, x, y, face_dir, eye, mth, expr, bob=0, who=None):
    """迭代版角色渲染：x,y 脚底中点"""
    spr = _refined(art, tuple(sorted(pal.items())))
    if face_dir < 0:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    w, h = spr.size
    x0, y0 = int(round(x - w // 2)), int(round(y + bob - h))
    img.paste(spr, (x0, y0), spr)
    aw = (w - 2) // 2
    if face_dir > 0:
        ex, gx, mxn = eye[0], eye[2], mth[0] + 2
    else:
        ex, gx, mxn = aw - 1 - eye[0] - eye[2], eye[2], aw - 1 - mth[0] - 1
    face_hd(img, x0 + 1 + ex * 2, y0 + 1 + eye[1] * 2 + 2, gx * 2, x0 + 1 + mxn * 2, y0 + 1 + mth[1] * 2 + 2, expr, pal.get('s', (252, 222, 198)))
    return x0, y0, w, h




def refined_sprite(art, pal):
    """没有五官的物件、宠物：精修后的 RGBA 精灵"""
    return _refined(art, tuple(sorted(pal.items())))
