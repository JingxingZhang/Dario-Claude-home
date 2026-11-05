"""《关键词》角色：我（写字的人）、你（红围巾）、小杏（银杏叶·贯穿配角）。全部字符画从零绘制。"""
import math
from PIL import Image, ImageDraw
from pixlib import *
from charkit import *
from props2 import face

INK = (34, 24, 44)
GOLD = (246, 196, 62)        # 银杏金
GOLD_D = (214, 150, 40)
SCARF = (226, 74, 70)        # 你的红围巾

# ---------------- 我：写字的人 · 藏青毛衣 · 耳后夹一支铅笔 ----------------
ME_PAL = {'h': (46, 38, 56), 'H': (70, 60, 82), 's': (250, 216, 186), 'S': (226, 184, 156),
          'c': (58, 82, 140), 'C': (42, 60, 108), 'w': (240, 236, 226), 'p': (250, 206, 70), 'P': (240, 150, 140),
          'L': (78, 70, 66), 'B': (44, 34, 34), 'n': (250, 246, 232), 'N': (200, 80, 70)}
ME_HEAD = '''
.....hhhhhh.....
....hhhhhhhhP...
...hhhhhhhhhhp..
...hhhHhhhhHhhp.
...hhssshhsssh..
...hsssssssssh..
...Sssssssssss..
....ssssssssS...
....ssssssssS...
.....ssssssS....
......sssS......
'''
ME_BODY = {
 'idle': '''
....wcccccccw...
...ccccwwccccc..
..cCccccccccccC.
..cCccccccccccC.
..cCccccccccccC.
..cCccccccccccC.
..sCccccccccccs.
...CCCCCCCCCCC..
....LLLLLLLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLL...LLL...
...BBBB...BBBB..
''',
 'walk1': '''
....wcccccccw...
...ccccwwccccc..
..cCccccccccccC.
.cCcccccccccccCc
.cCccccccccccc.s
.sCccccccccccc..
...ccccccccccc..
...CCCCCCCCCCC..
....LLLLLLLLL...
...LLLL...LLLL..
...LLL.....LLL..
..LLL.......LLL.
..LLL.......LLL.
.BBBB.......BBBB
................
''',
 'walk2': '''
....wcccccccw...
...ccccwwccccc..
..cCccccccccccC.
..cCccccccccccC.
..cCccccccccccC.
..sCccccccccccs.
...ccccccccccc..
...CCCCCCCCCCC..
....LLLLLLLLL...
....LLLL.LLLL...
....LLLL.LLLL...
.....LLL.LLL....
.....LLL.LLL....
....BBBB.BBBB...
................
''',
 'hold': '''
....wcccccccw...
...ccccwwccccc..
..cCccccccccccC.
..cCcnnnnnnnccC.
..cCsnnnnnnnscC.
..cCcnNNNNNnccC.
..cCcnnnnnnnccC.
...CCnnnnnnnCC..
....LLLLLLLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLL...LLL...
...BBBB...BBBB..
''',
 'give': '''
....wcccccccw...
...ccccwwcccccccc
..cCcccccccccCCCs
..cCccccccccc....
..cCccccccccc....
..cCccccccccc....
..sCccccccccc....
...CCCCCCCCCC....
....LLLLLLLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLL...LLL...
...BBBB...BBBB..
''',
 'cheer': '''
.s............s.
.cc..wccccw..cc.
..cCccwwccccCc..
...ccccccccccc..
...ccccccccccc..
...ccccccccccc..
...ccccccccccc..
...CCCCCCCCCCC..
....LLLLLLLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLL...LLL...
...BBBB...BBBB..
''',
 'scratch': '''
....wcccccccwcs.
...ccccwwccccCc.
..cCccccccccc...
..cCccccccccc...
..cCccccccccc...
..cCccccccccc...
..sCccccccccc...
...CCCCCCCCCC...
....LLLLLLLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLLL.LLLL...
....LLL...LLL...
...BBBB...BBBB..
''',
}
# 冬天：毛线帽（米白带一道灰蓝条纹）
ME_HEAD_HAT = '''
.....wwwwww.....
....wwwwwwww....
...wwwwwwwwww...
...CCCCCCCCCC...
...hhssshhsssh..
...hsssssssssh..
...Sssssssssss..
....ssssssssS...
....ssssssssS...
.....ssssssS....
......sssS......
'''
# 随故事换装：秋（藏青毛衣、黄铅笔）/ 冬（灰蓝大衣、毛线帽）/ 第二年秋（银杏色毛衣、耳后夹你的红笔）
ME_OUTFIT = {
    'autumn': {},
    'winter': {'c': (104, 118, 150), 'C': (78, 90, 120), 'w': (236, 228, 212)},
    'year2': {'c': (224, 168, 64), 'C': (186, 128, 40), 'p': (226, 74, 70), 'P': (180, 50, 50)},
}
YOU_OUTFIT = {
    'autumn': {},
    'winter': {'o': (200, 156, 112), 'O': (164, 120, 84)},
    'year2': {},
}
LEAF_PRESSED = {'y': (238, 218, 156), 'Y': (208, 184, 116), 't': (170, 140, 90)}

# 坐在书桌后：只画上半身（桌子挡住腿）
ME_DESK = '''
....wcccccccw...
...ccccwwccccc..
..cCccccccccccC.
..cCccccccccccC.
.sCccccccccccCs.
'''


def _join(head, body):
    return head.strip('\n') + '\n' + body.strip('\n')


# 眼睛在精灵里的位置（字符画坐标，未含描边）
ME_EYE = (5, 5, 4)      # x, y, gap
ME_MOUTH = (6, 8)
YOU_EYE = (5, 5, 4)
YOU_MOUTH = (6, 7)

# 表情：(眼, 嘴, 腮红)
EXPR = {
    'normal': ('dot', 'flat', False), 'smile': ('dot', 'smile', False), 'happy': ('closed', 'grin', False),
    'blush': ('closed', 'smile', True), 'shock': ('wide', 'o', False), 'stuck': ('line', 'wave', False),
    'think': ('dot', 'smirk', False), 'sad': ('sad', 'sad', False), 'heart': ('heart', 'smile', True),
    'zip': ('dot', 'zip', True),
}


def _face(img, x0, y0, sc, eye, mth, ex):
    e, m, bl = EXPR[ex]
    eyes(img, x0 + (eye[0] + 1) * sc, y0 + (eye[1] + 1) * sc, e, eye[2] * sc // sc * 1 if False else eye[2], scale=sc) if False else None
    # eyes() 的 gap 是原生像素；放大时按 scale 画
    d = ImageDraw.Draw(img)
    ex_x, ex_y = x0 + (eye[0] + 1) * sc, y0 + (eye[1] + 1) * sc
    eyes(img, ex_x, ex_y, e, eye[2], scale=sc)
    mx, my = x0 + (mth[0] + 1) * sc, y0 + (mth[1] + 1) * sc
    if m == 'zip':
        for i in range(4):
            d.rectangle([mx + i * sc, my, mx + i * sc + sc - 1, my + sc - 1], fill=(200, 200, 210) if i % 2 else INK)
    else:
        mouth(img, mx, my, m, scale=sc)
    if bl:
        c = (240, 130, 140)
        d.rectangle([ex_x - 2 * sc, my - sc, ex_x - sc - 1, my - 1], fill=c)
        d.rectangle([ex_x + (eye[2] + 2) * sc, my - sc, ex_x + (eye[2] + 3) * sc - 1, my - 1], fill=c)


def me(img, x, y, pose='idle', expr='smile', scale=2, face_dir=1, pal=None, bob=0, outfit='autumn'):
    """我：x,y 脚底中点；outfit 随故事换装"""
    p = dict(pal or ME_PAL); p.update(ME_OUTFIT.get(outfit, {}))
    head = ME_HEAD_HAT if outfit == 'winter' else ME_HEAD
    if pose == 'desk':
        art = _join(head, ME_DESK)
    else:
        art = _join(head, ME_BODY[pose])
    if STYLE >= 1 and scale == 2:
        p2 = dict(p); p2.update({k: v for k, v in SOFT['me'].items() if k not in ME_OUTFIT.get(outfit, {})})
        return render_char(img, art, p2, x, y, face_dir, ME_EYE, ME_MOUTH, expr, bob, 'me')
    spr = pixmap(art, p)
    w, h = put(img, spr, x, y + bob, scale, face_dir)
    x0, y0 = int(round(x - w // 2)), int(round(y + bob - h))
    if face_dir > 0:
        _face(img, x0, y0, scale, ME_EYE, ME_MOUTH, expr)
    else:  # 朝左时镜像五官位置
        ww = spr.width
        eye = (ww - 2 - ME_EYE[0] - ME_EYE[2], ME_EYE[1], ME_EYE[2])
        mth = (ww - 2 - ME_MOUTH[0] - 3, ME_MOUTH[1])
        _face(img, x0, y0, scale, eye, mth, expr)
    return x0, y0, w, h


# ---------------- 你：齐耳短发 · 米白长外套 · 红围巾（全片辨识点） ----------------
YOU_PAL = {'b': (92, 56, 46), 'B': (120, 76, 60), 's': (252, 222, 196), 'S': (230, 190, 164),
           'o': (238, 228, 206), 'O': (204, 190, 166), 'r': SCARF, 'R': (176, 50, 52), 'L': (64, 62, 80), 'K': (60, 40, 40)}
YOU_HEAD = '''
....bbbbbbbb....
...bbbbbbbbbb...
..bbbbBbbbbbbb..
..bbbbbbbbbbbb..
..bbsssssssbbb..
..bbsssssssbbb..
..bbsssssssSbb..
..bbsssssssSbb..
..bb.sssssS.bb..
.....sssss......
'''
YOU_BODY = {
 'idle': '''
...rrrrrrrrrr...
..rrRrrrrrrRrr..
..ooorrrrrooOo..
..oOooRrrooooOo.
..oOooRrooooooO.
..oOooRroooooOo.
..sOooooooooooOs
...OoooooooooO..
...ooooooooooo..
...ooooo.ooooo..
....LLL...LLL...
....LLL...LLL...
....LLL...LLL...
...KKKK...KKKK..
''',
 'walk1': '''
...rrrrrrrrrr...
..rrRrrrrrrRrr..
..ooorrrrrooOo..
.ooOooRrrooooOo.
.sOoooRroooooo.s
...oooRroooooo..
...ooooooooooo..
...OoooooooooO..
..oooooo.oooooo.
..ooooo...ooooo.
..LLL.......LLL.
..LLL.......LLL.
.LLL.........LLL
KKKK.........KKKK
''',
 'walk2': '''
...rrrrrrrrrr...
..rrRrrrrrrRrr..
..ooorrrrrooOo..
..oOooRrrooooOo.
..oOooRrooooooO.
..sOooRroooooOs.
...ooooooooooo..
...OoooooooooO..
...ooooooooooo..
...ooooo.ooooo..
.....LLL.LLL....
.....LLL.LLL....
.....LLL.LLL....
....KKKK.KKKK...
''',
 'call': '''
...rrrrrrrrrr.s.
..rrRrrrrrrRrro.
..ooorrrrroooo..
..oOooRrrooooo..
..oOooRroooooo..
..oOooRroooooo..
..sOoooooooooo..
...OoooooooooO..
...ooooooooooo..
...ooooo.ooooo..
....LLL...LLL...
....LLL...LLL...
....LLL...LLL...
...KKKK...KKKK..
''',
}


def you(img, x, y, pose='idle', expr='smile', scale=2, face_dir=1, pal=None, bob=0, outfit='autumn'):
    p = dict(pal or YOU_PAL); p.update(YOU_OUTFIT.get(outfit, {}))
    art = _join(YOU_HEAD, YOU_BODY[pose])
    if STYLE >= 1 and scale == 2:
        p2 = dict(p); p2.update({k: v for k, v in SOFT['you'].items() if k not in YOU_OUTFIT.get(outfit, {})})
        return render_char(img, art, p2, x, y, face_dir, YOU_EYE, YOU_MOUTH, expr, bob, 'you')
    spr = pixmap(art, p)
    w, h = put(img, spr, x, y + bob, scale, face_dir)
    x0, y0 = int(round(x - w // 2)), int(round(y + bob - h))
    if face_dir > 0:
        _face(img, x0, y0, scale, YOU_EYE, YOU_MOUTH, expr)
    else:
        ww = spr.width
        _face(img, x0, y0, scale, (ww - 2 - YOU_EYE[0] - YOU_EYE[2], YOU_EYE[1], YOU_EYE[2]), (ww - 2 - YOU_MOUTH[0] - 3, YOU_MOUTH[1]), expr)
    return x0, y0, w, h


# ---------------- 小杏：一片银杏叶（贯穿配角）----------------
LEAF = '''
.yyyyy..yyyyy.
yyyyyYyyYyyyyy
yyYyyyyyyyyYyy
.yyYyyyyyyYyy.
..yyyyyyyyyy..
...yyyyyyyy...
....yyYYyy....
.....yYYy.....
......yy......
......tt......
.......t......
'''
LEAF_PAL = {'y': GOLD, 'Y': GOLD_D, 't': (150, 110, 40)}


def leaf(img, cx, cy, expr='happy', scale=2, ang=0.0, pal=None, sign=None, arms=False):
    """小杏：cx,cy 叶片中心。ang 旋转角度（度），飘落时用。sign：举一块小牌子。"""
    if STYLE >= 1 and scale >= 2:
        spr = _refined(LEAF, tuple(sorted((pal or LEAF_PAL).items())))
        if scale > 2:
            spr = spr.resize((spr.width * scale // 2, spr.height * scale // 2), Image.NEAREST)
    else:
        spr = pixmap(LEAF, pal or LEAF_PAL)
        spr = spr.resize((spr.width * scale, spr.height * scale), Image.NEAREST)
    if ang:
        spr = spr.rotate(ang, Image.NEAREST, expand=True)
    img.paste(spr, (int(cx - spr.width // 2), int(cy - spr.height // 2)), spr)
    if not ang or abs(ang) < 1:
        face(img, int(cx), int(cy - 2 * scale), expr, max(1, scale // 2))
    if sign:
        from props2 import ptext
        d = ImageDraw.Draw(img)
        tw = text_w(sign) + 8
        sx, sy = int(cx - tw // 2), int(cy - 9 * scale - 12)
        d.line([(cx, cy - 5 * scale), (cx, sy + 12)], fill=(150, 110, 40), width=1)
        d.rectangle([sx, sy, sx + tw, sy + 12], fill=(250, 246, 232), outline=INK)
        draw_text(img, sx + 4, sy + 1, sign, INK)


# =====================================================================
# 画风迭代（PIXMV_STYLE=1/2）：角色精修渲染管线
#   字符画 → Scale2x 放大（斜边变圆润，原生 2 倍细节）→ 体积光影（左上受光 1px 高光带、右下 2px 暗带）
#   → 彩色描边（取相邻颜色的深色，不用死黑；底边更深）→ 高清五官（2×3 眼睛带眼神光、细嘴、点状腮红）
# =====================================================================
import os as _os
from functools import lru_cache as _lru
import numpy as _np
STYLE = int(_os.environ.get('PIXMV_STYLE', '2'))       # 默认迭代二画风；PIXMV_STYLE=0 可回到原版
# 迭代版的柔和配色（Apple 式：低饱和、干净、不用纯黑）
SOFT = {
    'me': {'h': (52, 46, 66), 'H': (88, 80, 104), 's': (252, 222, 198), 'S': (236, 196, 172), 'c': (72, 100, 160), 'C': (54, 78, 130),
           'w': (246, 242, 234), 'p': (250, 206, 84), 'P': (244, 160, 150), 'L': (86, 80, 84), 'B': (60, 50, 56), 'n': (252, 248, 236), 'N': (210, 96, 88)},
    'you': {'b': (110, 70, 58), 'B': (148, 98, 78), 's': (254, 226, 204), 'S': (238, 200, 176), 'o': (244, 236, 220), 'O': (214, 202, 182),
            'r': (232, 88, 84), 'R': (192, 64, 66), 'L': (78, 76, 96), 'K': (84, 60, 60)},
}
FACE_INK = (48, 38, 60)


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


def render_char(img, art, pal, x, y, face_dir, eye, mth, expr, bob=0, who='me'):
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


def you_upper(img, x, y, expr, face_dir, outfit='autumn'):
    """坐着 / 桌子后的你（只有上半身），迭代版"""
    body = '\n'.join(YOU_BODY['idle'].strip('\n').split('\n')[:7])
    p = dict(YOU_PAL); p.update(YOU_OUTFIT.get(outfit, {}))
    p.update({k: v for k, v in SOFT['you'].items() if k not in YOU_OUTFIT.get(outfit, {})})
    return render_char(img, _join(YOU_HEAD, body), p, x, y, face_dir, YOU_EYE, YOU_MOUTH, expr)


@_lru(maxsize=64)
def _leaf_refined(pal_items):
    return _refined(LEAF, pal_items)
