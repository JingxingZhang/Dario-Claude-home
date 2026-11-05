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


def me(img, x, y, pose='idle', expr='smile', scale=2, face_dir=1, pal=None, bob=0):
    """我：x,y 脚底中点"""
    p = pal or ME_PAL
    if pose == 'desk':
        art = _join(ME_HEAD, ME_DESK)
    else:
        art = _join(ME_HEAD, ME_BODY[pose])
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


def you(img, x, y, pose='idle', expr='smile', scale=2, face_dir=1, pal=None, bob=0):
    p = pal or YOU_PAL
    art = _join(YOU_HEAD, YOU_BODY[pose])
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
