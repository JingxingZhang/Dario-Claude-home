"""《关键词》像素 MV 第二版（原唱：林俊杰）—— 新流程：先写故事（故事.md），重复歌词不重复画面，液态玻璃层。
角色见 cast.py，故事见 故事.md，分镜见 分镜说明.md，精读见 歌词精读.md。
"""
import math, os, sys
SKILL = os.environ.get('PIXMV_SKILL', '')
sys.path.insert(0, os.path.join(SKILL, 'lib'))
ROOT = os.environ.get('PIXMV_PROJECT', os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *            # draw_text, text_w, dither_grad, draw_sky, draw_water, seg, ease, hsh, lerpc …
from charkit import *           # pixmap, put, recolor, eyes, mouth, palette_strip —— 设计角色用
from props2 import *            # ptext, sfx, stamp, sys_msg, cursor, toggle, face …（像素综艺元素与道具）
from glassui import *           # 液态玻璃组件；同名覆盖 props2 的 say / OS / popup / meter（参数兼容）
from chars import heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, curtains, R
from engine import Song, MV
import huazi as Z

song = Song(ROOT)
rms, pump, beat_phase, L = song.rms, song.pump, song.beat_phase, song.L

# ======================= ① 视觉方案（见 分镜说明.md）=======================
# 曲风：抒情流行慢板 / BPM≈68 → 一句一镜、小幅动作；花字小回弹、慢逐字
# 配色跟着故事的一年走：秋（银杏金 + 纸米白）→ 冬（雪白 + 灰蓝 + 路灯暖橘）→ 第二年秋（更暖的金）；围巾红只属于“你”
PALETTE = {'paper': (244, 236, 216), 'gold': (246, 196, 62), 'scarf': (226, 74, 70), 'snow': (226, 234, 246), 'winter': (150, 170, 200), 'ink': (30, 32, 60)}
LYRIC_BASE = dict(pop=1.08, stagger=0.09, float_amp=3)
TITLE_STYLE = dict(pal='yel', size=230, angle=-3, deco=('note', 'star'))

# ======================= ② 角色（cast.py：从零绘制，随故事换装）=======================
sys.path.insert(0, ROOT)
from cast import me, you, ME_PAL, YOU_PAL, LEAF_PAL, LEAF_PRESSED, GOLD, GOLD_D, SCARF, INK
from cast import leaf as _leaf_px


def leaf(img, cx, cy, expr='happy', scale=2, ang=0.0, pal=None, sign=None):
    """小杏；举牌用玻璃小牌"""
    _leaf_px(img, cx, cy, expr, scale, ang, pal, None)
    if sign:
        gsign(cx, cy, sign, scale)


def CAST_SHEET(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(244, 236, 216))
    for y in range(26, 180, 10):
        d.line([(0, y), (320, y)], fill=(226, 216, 196))
    d.line([(10, 0), (10, 180)], fill=(236, 170, 160))
    draw_text(img, 16, 2, '《关键词》第二版·角色随故事的一年', INK)
    k = int(t * 4) % 2
    cols = [('autumn', '秋', GOLD_D), ('winter', '冬', (90, 110, 150)), ('year2', '第二年秋', (190, 120, 30))]
    for j, (o, lab, c) in enumerate(cols):
        x0 = 30 + j * 100
        draw_text(img, x0 - 10, 16, lab, c)
        me(img, x0, 90, 'walk1' if k else 'walk2', ['smile', 'blush', 'happy'][j], 2, 1, outfit=o)
        you(img, x0 + 34, 90, 'idle' if j != 1 else 'call', ['smile', 'happy', 'blush'][j], 2, -1, outfit=o)
        leaf(img, x0 + 64, 76, ['happy', 'sleep', 'heart'][j], 1, pal=LEAF_PRESSED if o == 'winter' else None)
    draw_text(img, 16, 94, '我的表情', INK)
    for i, e in enumerate(['smile', 'shock', 'blush', 'stuck', 'heart', 'zip']):
        me(img, 34 + i * 30, 140, 'desk', e, 2, 1)
    labs = ['笑', '惊', '脸红', '词穷', '心动', '拉链']
    for i, l in enumerate(labs):
        draw_text(img, 34 + i * 30 - text_w(l) // 2, 142, l, (120, 100, 90))
    draw_text(img, 212, 94, '笔记本', INK)
    for i, (c, lab) in enumerate([((58, 82, 140), '第一本'), (SCARF, '第二本')]):
        x = 216 + i * 46
        R(ImageDraw.Draw(img), x, 106, 30, 38, c); ImageDraw.Draw(img).rectangle([x, 106, x + 29, 143], outline=INK)
        R(ImageDraw.Draw(img), x + 4, 112, 22, 4, PALETTE['paper'])
        draw_text(img, x + 15 - text_w(lab) // 2, 146, lab, (120, 100, 90))
    palette_strip(img, 16, 160, [PALETTE['gold'], PALETTE['paper'], PALETTE['snow'], PALETTE['winter'], SCARF, PALETTE['ink']])
    draw_text(img, 82, 158, '秋金 纸 雪 冬蓝 围巾红 墨', (120, 100, 90))


# ======================= ③ 场景（绘制函数可以复用；镜头函数每个只用一次）=======================
from chars import person, qmark
import cover as COV
PAPER = (244, 236, 216)
RULE = (196, 208, 226)
CHALK = (232, 238, 226)
NAVY = (58, 82, 140)
LAND_T = L(6) + 2.2          # 第 7 句“喊我名字”时落地：之前“我”都微微飘着


def glow(img, cx, cy, r, col, k=0.35):
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:img.height, 0:img.width]
    m = np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) * k
    b = np.tile(BAYER, (img.height // 4 + 1, img.width // 4 + 1))[:img.height, :img.width]
    m = np.floor(m * 6 + b - 0.5).clip(0, 6) / 6
    a = a * (1 - m[..., None]) + np.array(col, float) * m[..., None]
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)))


def leaf_cols(season):
    if season == 'year2':
        return lerpc(GOLD, (255, 170, 70), 0.22), lerpc(GOLD_D, (200, 110, 40), 0.2)
    if season == 'summer':
        return (110, 176, 90), (76, 136, 70)
    if season == 'spring':
        return (170, 220, 120), (120, 180, 90)
    return GOLD, GOLD_D


def tree(img, x, ground, season='autumn', k=1.0, snow=0.0):
    """银杏树：秋 / 第二年秋 = 金色树冠；冬 = 只剩枝丫和积雪；春 = 枝头新芽；夏 = 绿树冠。k 为树冠大小"""
    d = ImageDraw.Draw(img)
    th = 36
    R(d, x - 3, ground - th, 6, th, (110, 76, 52)); R(d, x - 3, ground - th, 2, th, (140, 100, 70))
    cy = ground - th - 10
    if season in ('winter', 'spring') or k < 0.6:
        for a_, ln in ((-0.9, 22), (-0.4, 26), (0.3, 24), (0.85, 20), (-0.1, 18)):
            ex, ey = x + int(math.sin(a_) * ln), ground - th - int(math.cos(a_) * ln)
            d.line([(x, ground - th + 4), (ex, ey)], fill=(100, 70, 50), width=2)
            if season == 'winter' or snow > 0:
                d.line([(ex - 2, ey - 1), (ex + 2, ey - 1)], fill=(246, 250, 255), width=1)
            if season == 'spring':
                for j in range(3):
                    d.point((ex + j - 1, ey + j), fill=(150, 210, 110))
        if season == 'winter':
            R(d, x - 4, ground - th - 1, 8, 2, (246, 250, 255))
        if season in ('winter', 'spring'):
            return
    g, gd = leaf_cols(season)
    blobs = [(0, 0, 17), (-15, 7, 12), (15, 7, 12), (-7, -11, 11), (9, -10, 11)]
    for ox, oy, r in blobs:
        rr = max(1, int(r * k))
        disc(d, x + ox, cy + oy + 2, rr, gd)
    for ox, oy, r in blobs:
        rr = max(1, int(r * k) - 1)
        disc(d, x + ox, cy + oy, rr, g)
    for i in range(int(18 * k)):
        px, py = x + int((hsh(i, x, 1) - 0.5) * 40 * k), cy + int((hsh(i, x, 2) - 0.6) * 26 * k)
        d.point((px, py), fill=lerpc(g, WHITE, 0.4))


def street_lamp(img, x, ground, on):
    d = ImageDraw.Draw(img)
    R(d, x - 1, ground - 58, 3, 58, (60, 56, 70)); R(d, x - 5, ground - 62, 11, 5, (60, 56, 70))
    R(d, x - 3, ground - 57, 7, 3, (255, 236, 170) if on else (120, 120, 130))
    if on:
        glow(img, x, ground - 55, 34, (255, 214, 140), 0.35)


def snowfall(img, t, n=50, k=1.0, top=0, bot=H):
    d = ImageDraw.Draw(img)
    for i in range(int(n * k)):
        ph = (t * (0.08 + hsh(i, 31) * 0.06) + hsh(i, 32)) % 1
        x = int((hsh(i, 33) * 340 + math.sin(t * 0.8 + i) * 8) % 340) - 10
        y = int(top - 4 + ph * (bot - top + 8))
        d.point((x, y), fill=(250, 252, 255))
        if hsh(i, 34) > 0.7:
            d.point((x + 1, y), fill=(230, 236, 248))


def sky(img, t, season, tod, hz):
    if season == 'winter':
        if tod > 0.9:
            img.paste(Image.fromarray(dither_grad(hz, W, (22, 28, 56), (64, 74, 116))), (0, 0))
        else:
            img.paste(Image.fromarray(dither_grad(hz, W, (126, 148, 186), (214, 224, 238))), (0, 0))
    else:
        draw_sky(img, tod, hz=hz, sun=tod < 0.9, stars=0.8 if tod > 0.9 else 0, t=t)


def avenue(img, t, season='autumn', scroll=0.0, tod=0.45, ground=104, lamps=None, fall=1.0, k=1.0):
    """银杏大道：远处一排小树 + 近景大树 + 地面；季节决定树冠、地面和飘落物"""
    sky(img, t, season, tod, ground)
    d = ImageDraw.Draw(img)
    g, gd = leaf_cols(season)
    top, bot = (np.asarray(img)[0, 0], np.asarray(img)[ground - 1, 0])
    bot = tuple(int(v) for v in bot)
    winter = season == 'winter'
    for i in range(16):
        x = int((i * 26 - scroll * 0.3) % 416) - 48
        if winter:
            d.line([(x, ground - 2), (x, ground - 16)], fill=lerpc((100, 80, 70), bot, 0.5))
            d.line([(x, ground - 10), (x - 5, ground - 18)], fill=lerpc((100, 80, 70), bot, 0.5))
            d.line([(x, ground - 12), (x + 5, ground - 19)], fill=lerpc((100, 80, 70), bot, 0.5))
        else:
            disc(d, x, ground - 12, max(2, int(11 * k)), lerpc(g, bot, 0.45)); R(d, x - 1, ground - 4, 2, 4, lerpc((110, 76, 52), bot, 0.4))
    if winter:
        path = (226, 232, 242) if tod < 0.9 else (120, 130, 160)
    elif season == 'year2':
        path = (232, 214, 184)
    else:
        path = (226, 212, 188)
    R(d, 0, ground, W, H - ground, path)
    R(d, 0, ground, W, 2, lerpc(path, (120, 110, 100), 0.35))
    for i in range(70):
        x = int((hsh(i, 11) * 420 - scroll) % 420) - 50
        y = ground + 3 + int(hsh(i, 12) * (H - ground - 4))
        if winter:
            d.point((x, y), fill=lerpc(path, (170, 180, 200), 0.6))
        elif k > 0.3 or season != 'autumn':
            d.rectangle([x, y, x + 2, y + 1], fill=g if hsh(i, 13) > 0.3 else gd)
    for i in range(4):
        x = int((i * 110 + 40 - scroll) % 440) - 60
        tree(img, x, ground + 2, season, k)
        if lamps is not None and i % 2 == 1:
            street_lamp(img, x + 55, ground + 2, lamps)
    if winter:
        snowfall(img, t, 60 * fall, 1.0, 0, H)
    elif fall:
        for i in range(int(14 * fall)):
            ph = (t * 0.16 + hsh(i, 7)) % 1
            x = int((hsh(i, 8) * 360 - scroll * 0.8 + math.sin(t * 1.4 + i) * 12) % 360) - 20
            y = int(-6 + ph * (ground + 16))
            d.rectangle([x, y, x + 2, y + 1] if int(t * 4 + i) % 2 else [x, y, x + 1, y + 2], fill=g if i % 2 else gd)


def shadow(img, x, y, w=12, faint=False):
    a = np.asarray(img).copy()
    y0, y1 = max(0, y - 1), min(img.height, y + 2)
    x0, x1 = max(0, x - w), min(img.width, x + w)
    a[y0:y1, x0:x1] = (a[y0:y1, x0:x1] * (0.85 if faint else 0.7)).astype(np.uint8)
    img.paste(Image.fromarray(a))


def me_on(img, t, x, y, pose='idle', expr='smile', face_dir=1, outfit='autumn', force=None):
    """站着的我：第 7 句之前飘离地面 3 像素，影子发虚"""
    fl = (t < LAND_T) if force is None else force
    bob = -3 - int(round(math.sin(t * 2.2))) if fl else 0
    shadow(img, x, y, 9 if fl else 12, fl)
    return me(img, x, y, pose, expr, 2, face_dir, None, bob, outfit)


def you_on(img, t, x, y, pose='idle', expr='smile', face_dir=1, outfit='autumn'):
    shadow(img, x, y, 12)
    return you(img, x, y, pose, expr, 2, face_dir, None, 0, outfit)


def you_sit(img, x, y, expr, face_dir, outfit='autumn'):
    """坐着 / 桌子后的你：只画上半身"""
    from cast import YOU_HEAD, YOU_BODY, _join, _face, YOU_EYE, YOU_MOUTH, YOU_OUTFIT
    body = '\n'.join(YOU_BODY['idle'].strip('\n').split('\n')[:7])
    p = dict(YOU_PAL); p.update(YOU_OUTFIT.get(outfit, {}))
    spr = pixmap(_join(YOU_HEAD, body), p)
    w, h = put(img, spr, x, y, 2, face_dir)
    x0, y0 = int(x - w // 2), int(y - h)
    ww = spr.width
    if face_dir > 0:
        _face(img, x0, y0, 2, YOU_EYE, YOU_MOUTH, expr)
    else:
        _face(img, x0, y0, 2, (ww - 2 - YOU_EYE[0] - YOU_EYE[2], YOU_EYE[1], YOU_EYE[2]), (ww - 2 - YOU_MOUTH[0] - 3, YOU_MOUTH[1]), expr)


def room(img, t, tod=1.0, season='autumn', desk=True, lamp=True, wx=14):
    night = tod > 0.9
    top, bot = ((44, 46, 88), (28, 30, 58)) if night else ((236, 224, 204), (210, 196, 176))
    img.paste(Image.fromarray(dither_grad(H, W, top, bot)), (0, 0))
    d = ImageDraw.Draw(img)
    win = Image.new('RGB', (W, H))
    sky(win, t, season, tod, 78)
    if season == 'winter':
        snowfall(win, t, 40, 1.0, 0, 78)
    img.paste(win.crop((wx, 10, wx + 86, 78)), (wx, 10))
    d.line([(wx, 30), (wx + 50, 44), (wx + 86, 40)], fill=(70, 50, 44), width=2)
    if season == 'winter':
        d.line([(wx + 4, 29), (wx + 46, 41)], fill=(240, 246, 255))
    else:
        g, gd = leaf_cols(season)
        if night:
            g, gd = lerpc(g, (60, 60, 100), 0.35), lerpc(gd, (40, 40, 80), 0.35)
        for i in range(14):
            px, py = wx + 4 + int(hsh(i, 21) * 70), 26 + int(hsh(i, 22) * 26)
            d.rectangle([px, py, px + 3, py + 2], fill=g if i % 3 else gd)
    if night and season != 'winter':
        moon(img, wx + 66, 22, 7, 'sleep' if t < 10 else 'happy')
    fr = (120, 90, 66) if night else (176, 136, 96)
    d.rectangle([wx - 2, 8, wx + 87, 79], outline=fr, width=3)
    R(d, wx + 42, 10, 2, 68, fr); R(d, wx, 43, 86, 2, fr)
    R(d, wx - 6, 79, 98, 4, lerpc(fr, WHITE, 0.15))
    if season == 'winter':
        R(d, wx - 6, 77, 98, 2, (246, 250, 255))
    if lamp:
        lx = 286
        R(d, lx - 1, 70, 3, 30, (70, 64, 80)); R(d, lx - 8, 98, 17, 3, (70, 64, 80))
        d.polygon([(lx - 10, 70), (lx + 10, 70), (lx + 6, 60), (lx - 6, 60)], fill=(230, 150, 80))
        if night:
            glow(img, lx, 80, 90, (255, 214, 140), 0.32)
    if desk:
        d = ImageDraw.Draw(img)
        R(d, 0, 100, W, 80, (140, 92, 60)); R(d, 0, 100, W, 3, (176, 124, 84)); R(d, 0, 103, W, 1, (100, 64, 44))
    gcard(t, None, wx + 43, 44, 43, 34, r=18, refr=0.7, mag=0.03, tint=(190, 210, 255), tint_a=0.06, shadow=0.0)


def notebook_open(img, cx, y, w=56, write=0.0, tint=None):
    d = ImageDraw.Draw(img)
    pc = tint or PAPER
    d.polygon([(cx - w // 2, y + 12), (cx - w // 2 + 4, y), (cx - 1, y + 1), (cx - 1, y + 13)], fill=pc, outline=INK)
    d.polygon([(cx + 1, y + 1), (cx + w // 2 - 4, y), (cx + w // 2, y + 12), (cx + 1, y + 13)], fill=pc, outline=INK)
    for i in range(int(write * 6)):
        yy = y + 3 + (i % 3) * 3
        xx = cx - w // 2 + 7 if i < 3 else cx + 4
        d.line([(xx, yy), (xx + 16, yy)], fill=(90, 90, 120))


def book(img, x, y, w, h, col, label=None, lab_col=WHITE):
    d = ImageDraw.Draw(img)
    R(d, x + 2, y + 2, w, h, (80, 56, 40))
    R(d, x, y, w, h, col); d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK)
    R(d, x + 3, y + h - 4, w - 6, 2, PAPER)
    if label:
        draw_text(img, x + w // 2 - text_w(label) // 2, y + h // 2 - 7, label, lab_col)


def page(img, tint=None, holes=True, rules=True):
    pc = tint or PAPER
    img.paste(Image.fromarray(dither_grad(H, W, lerpc(pc, WHITE, 0.3), pc, 4)), (0, 0))
    d = ImageDraw.Draw(img)
    if rules:
        for y in range(22, H, 14):
            d.line([(0, y), (W, y)], fill=lerpc(RULE, pc, 0.2))
    d.line([(34, 0), (34, H)], fill=(236, 156, 146))
    if holes:
        for y in range(10, H, 18):
            disc(d, 12, y, 3, lerpc(pc, INK, 0.6))


def board(img, t, chalk_lines=()):
    img.paste(Image.fromarray(dither_grad(H, W, (222, 206, 178), (200, 182, 152), 5)), (0, 0))
    d = ImageDraw.Draw(img)
    R(d, 18, 4, 284, 92, (150, 104, 64))
    img.paste(Image.fromarray(dither_grad(84, 276, (46, 86, 70), (36, 70, 58), 4)), (22, 8))
    d = ImageDraw.Draw(img)
    for i in range(30):
        d.point((24 + int(hsh(i, 41) * 270), 10 + int(hsh(i, 42) * 80)), fill=(70, 110, 92))
    R(d, 16, 96, 288, 4, (176, 128, 84))
    R(d, 0, 104, W, 76, (176, 140, 104))
    for x in range(0, W, 40):
        d.line([(x, 104), (x, H)], fill=(150, 116, 84))
    for (x, y, s, col, sc) in chalk_lines:
        draw_text(img, x, y, s, col, sc)


def nametag(img, t, cx, cy, who='me', born=None, glowk=0.0):
    """名字牌：只画小头像（不编真实名字），外面一张玻璃卡"""
    if born is not None and t < born:
        return
    if glowk > 0:
        glow(img, cx, cy, 26, (255, 236, 160), 0.5 * glowk)
    d = ImageDraw.Draw(img)
    R(d, cx - 9, cy - 8, 18, 16, (255, 246, 236))
    from cast import ME_HEAD, YOU_HEAD
    spr = pixmap(ME_HEAD if who == 'me' else YOU_HEAD, ME_PAL if who == 'me' else YOU_PAL)
    put(img, spr, cx, cy + 8, 1)
    gcard(t, born, cx, cy, 11, 10, r=26, tint=(255, 190, 180) if who == 'you' else (255, 236, 170), tint_a=0.14 + 0.1 * glowk, refr=0.8, mag=0.02)


def falling_leaf(img, t, born, x0, y0, x1, y1, dur, expr='happy', scale=2, pal=None):
    k = clamp((t - born) / dur)
    if k >= 1:
        leaf(img, x1, y1, expr, scale, pal=pal)
        return x1, y1
    x = lerp(x0, x1, ease(k)) + math.sin(k * 9) * 14 * (1 - k)
    y = lerp(y0, y1, k)
    leaf(img, x, y, expr, scale, ang=math.sin(k * 11) * 40, pal=pal)
    return x, y


def mini_leaf(img, x, y, col, col2):
    put(img, pixmap('''
.yy.yy.
yyyyyyy
.yyyyy.
..yyy..
...t...
''', {'y': col, 't': col2}), int(x), int(y) + 3, 2, 1)


def staff_lines(img, y0, k, col, x0=16, x1=304, gap=12):
    d = ImageDraw.Draw(img)
    for i in range(5):
        y = y0 + i * gap
        d.line([(x0, y), (x0 + int((x1 - x0) * k), y)], fill=col)


def station(img, t, door_open=1.0):
    """冬天的小站：雨棚、柱子、站台、右侧一节列车"""
    img.paste(Image.fromarray(dither_grad(104, W, (126, 148, 186), (214, 224, 238))), (0, 0))
    d = ImageDraw.Draw(img)
    for i in range(8):
        x = i * 46 - 10
        d.line([(x, 104), (x + 6, 80)], fill=(150, 160, 186))
    R(d, 0, 0, W, 12, (90, 96, 120)); R(d, 0, 12, W, 2, (240, 246, 255))
    for x in (40, 150):
        R(d, x, 14, 4, 90, (110, 116, 140))
    R(d, 0, 104, W, 76, (176, 182, 198)); R(d, 0, 108, W, 2, (230, 200, 90))
    # 列车
    R(d, 196, 30, 124, 74, (214, 218, 226)); R(d, 196, 30, 124, 4, (170, 176, 190))
    R(d, 196, 88, 124, 4, (70, 140, 160))
    for wx in (206, 270):
        R(d, wx, 42, 40, 28, (40, 52, 84)); d.rectangle([wx, 42, wx + 39, 69], outline=(150, 156, 170))
    dw = int(18 * door_open)
    R(d, 250 - 1, 40, 20, 50, (150, 156, 170))
    R(d, 250, 41, 18, 48, (60, 70, 100))
    if dw < 18:
        R(d, 250, 41, 18 - dw, 48, (200, 204, 214))
    snowfall(img, t, 40, 1.0, 0, 104)


# ======================= ④ 镜头（按故事顺序，每个只用一次）=======================
# ---------------- 前奏：深秋夜，空白的本子 ----------------
def s_title(img, t, lt, v):
    """前奏：空白笔记本“关于____”，小杏从窗外飘进来落在本子上"""
    room(img, t, 1.0, 'autumn')
    bubbles(t, 5, 1, 110, 320, 10, 96, 3, 7, 5.0)
    awake = lt > 10.0
    me(img, 250, 100, 'desk', 'shock' if 10.0 < lt < 10.9 else ('smile' if awake else 'stuck'), 2)
    notebook_open(img, 250, 94)
    d = ImageDraw.Draw(img)
    tap = 3 if beat_phase(t) < 0.12 and lt < 9.6 else 0
    R(d, 268, 86 - tap, 2, 9, (250, 206, 70)); R(d, 268, 95 - tap, 2, 1, INK)
    if lt < 2.0:
        leaf(img, 54, 34, 'sleep', 1)
    elif lt < 8.0:
        falling_leaf(img, lt, 2.0, 54, 34, 244, 90, 6.0, 'sleep', 1)
    elif lt < 12.0:
        leaf(img, 244, 90, 'sleep' if lt < 10 else 'happy', 1)
        if 10.0 < lt < 11.5:
            sfx(img, 236, 70, '！', t, t - lt + 10.0, 1.5, 'yel', 1)
        if lt < 10:
            draw_text(img, 254, 76 - int((lt * 0.8) % 1 * 6), 'z', (220, 220, 255), outline=INK)
    else:
        k = ease(seg(lt, 12.0, 12.8))
        leaf(img, lerp(244, 266, k), lerp(90, 72, k) - math.sin(k * math.pi) * 14, 'happy', 1)
    if lt > 10.2:
        gchip(t, t - lt + 10.2, 150, 30, '关于 ______', TXT, 44)


# ---------------- 主歌一：秋 ----------------
def s_mirror(img, t, lt, v):
    """第1句：和自己对话——镜子里的我竖起大拇指"""
    img.paste(Image.fromarray(dither_grad(H, W, (236, 226, 236), (212, 200, 214), 5)), (0, 0))
    d = ImageDraw.Draw(img)
    R(d, 0, 104, W, 76, (196, 170, 150)); R(d, 0, 104, W, 2, (170, 140, 120))
    cx, cy, r = 110, 54, 44
    disc(d, cx, cy, r + 4, (170, 130, 90)); disc(d, cx, cy, r, (200, 226, 236))
    mirror = Image.new('RGB', (W, H), (200, 226, 236))
    me(mirror, cx + 4, cy + 52, 'give' if lt > 0.8 else 'idle', 'happy' if lt > 0.8 else 'smile', 2, 1)
    mk = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mk).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(mirror, (0, 0), mk)
    gcard(t, None, cx, cy, r, r, r=r * 6, refr=0.9, mag=0.04, tint=(200, 235, 255), tint_a=0.08)
    d = ImageDraw.Draw(img)
    R(d, cx + 18, cy - 46, 40, 22, (255, 232, 120)); d.rectangle([cx + 18, cy - 46, cx + 57, cy - 25], outline=GOLD_D)
    draw_text(img, cx + 20, cy - 44, '好好', INK); draw_text(img, cx + 20, cy - 33, '爱自己', INK)
    me_on(img, t, 214, 118, 'idle', 'smile' if lt < 1.4 else 'blush', -1)
    leaf(img, cx - 34, cy - 40, 'happy', 1)
    if lt > 1.0:
        sfx(img, 60, 22, '赞！', t, t - lt + 1.0, 1.8, 'yel', 1)


def s_wordlist(img, t, lt, v):
    """第2句：便利贴被贴进本子的“词表”，归到【说词】一栏；小杏将信将疑"""
    page(img)
    d = ImageDraw.Draw(img)
    draw_text(img, 44, 8, '词表', INK, 2)
    cols = ['说词', '形容词', '语助词', '关键词']
    for i, c in enumerate(cols):
        x = 44 + i * 64
        draw_text(img, x, 38, c, (120, 120, 150))
        d.line([(x, 52), (x + 56, 52)], fill=(150, 150, 180))
    k = ease(seg(lt, 0.1, 0.8))
    nx, ny = int(lerp(220, 44, k)), int(lerp(-30, 58, k))
    R(d, nx + 2, ny + 2, 56, 30, (220, 180, 90)); R(d, nx, ny, 56, 30, (255, 232, 120))
    draw_text(img, nx + 3, ny + 3, '好好爱自己', INK); draw_text(img, nx + 3, ny + 16, '就有人会爱你', INK)
    if lt > 0.9:
        gtag(t, t - lt + 0.9, 72, 104, '说词', 'cyan')
    leaf(img, 270, 96, 'side' if lt > 1.0 else 'happy', 2, sign='真的假的？' if lt > 1.0 else None)


def s_meet(img, t, lt, v):
    """第3句（初遇）：风吹走一页纸，红围巾的你捡起来递还；我掐脸——真实度 100%"""
    avenue(img, t, 'autumn', 60 + lt * 6)
    d = ImageDraw.Draw(img)
    pk = ease(seg(lt, 0.0, 0.9))
    if lt < 1.0:
        px, py = lerp(140, 196, pk), 70 - math.sin(pk * math.pi) * 30
        R(d, int(px), int(py), 10, 8, WHITE); d.rectangle([int(px), int(py), int(px) + 9, int(py) + 7], outline=INK)
    you_on(img, t, 206, 120, 'call' if lt > 1.0 else 'idle', 'smile' if lt < 1.4 else 'happy', -1)
    if lt > 1.0:
        gk = ease(seg(lt, 1.0, 1.6))
        px = lerp(196, 166, gk)
        R(d, int(px), 84, 10, 8, WHITE); d.rectangle([int(px), 84, int(px) + 9, 91], outline=INK)
    me_on(img, t, 140, 120, 'hold' if lt < 1.8 else 'scratch', 'shock' if lt < 1.0 else ('blush' if lt < 2.0 else 'heart'))
    if lt > 1.8:
        sfx(img, 116, 50, '痛！', t, t - lt + 1.9, 0.8, 'red', 1)
    if lt > 1.6:
        meter(img, 8, 6, '真实度', ease(seg(lt, 1.7, 2.7)), (255, 110, 120), 60)
    if lt > 2.2:
        for i in range(3):
            heart(img, 150 + i * 9, 50 - int((lt * 12 + i * 5) % 14), 1)


def s_dict(img, t, lt, v):
    """第4句：想写下那天的你，翻遍字典——查无此词"""
    room(img, t, 1.0, 'autumn')
    me(img, 160, 100, 'desk', 'stuck' if lt > 1.0 else 'shock', 2)
    d = ImageDraw.Draw(img)
    R(d, 126, 92, 68, 16, (150, 60, 50)); R(d, 128, 90, 64, 14, (248, 240, 222)); R(d, 159, 90, 2, 14, (200, 190, 170))
    if lt < 1.4:
        fl = (lt * 6) % 1
        x = int(160 + math.cos(fl * math.pi) * 30)
        d.line([(160, 104), (x, 90 - int(math.sin(fl * math.pi) * 10))], fill=WHITE, width=2)
        sfx(img, 210, 74, '哗哗', t, t - lt, 1.4, 'white', 1)
    for i in range(min(9, int(lt * 4))):
        x, y = 70 + int(hsh(i, 51) * 30) - (i % 3) * 14, 98 - (i // 3) * 6
        disc(d, x, y, 4, WHITE); d.point((x - 1, y), fill=(180, 180, 190))
    leaf(img, 236, 94, 'shock' if lt > 1.0 else 'happy', 1)
    popup(img, 178, 6, '词典', '查无此词', ('确定',), 0, lt > 2.0, w=132, born=t - lt + 1.0)


def bench(img, t, season='autumn'):
    avenue(img, t, season, 300, fall=0.7)


def bench_front(img):
    d = ImageDraw.Draw(img)
    for y in (96, 103):
        R(d, 98, y, 124, 4, (150, 96, 60)); R(d, 98, y, 124, 1, (186, 128, 84))
    R(d, 104, 107, 3, 14, (70, 60, 60)); R(d, 214, 107, 3, 14, (70, 60, 60))
    R(d, 96, 110, 128, 4, (130, 82, 52))


def s_zip(img, t, lt, v):
    """第5句：长椅并坐，我拉链嘴，激情水位越过警戒线"""
    bench(img, t)
    me(img, 136, 106, 'desk', 'zip', 2)
    you_sit(img, 186, 106, 'smile', 1)
    bench_front(img)
    d = ImageDraw.Draw(img)
    x0, y0, hgt = 268, 14, 80
    R(d, x0, y0, 16, hgt, (226, 230, 244))
    lv = ease(seg(lt, 0.2, 2.8)) * 1.04
    wy = y0 + hgt - int(hgt * min(1, lv))
    R(d, x0, wy, 16, y0 + hgt - wy, (250, 110, 140))
    for i in range(0, 16, 4):
        d.point((x0 + i + int(t * 8) % 4, wy), fill=WHITE)
    wl = y0 + 18
    d.line([(x0 - 4, wl), (x0 + 20, wl)], fill=(230, 40, 60))
    gcard(t, None, x0 + 8, y0 + hgt / 2, 10, hgt / 2 + 2, r=60, refr=1.2, mag=0.06, tint_a=0.06)
    draw_text(img, x0 - 40, wl - 6, '警戒线', (230, 40, 60), outline=WHITE)
    if lv > 0.78:
        sfx(img, 240, 8, '要溢出了', t, t - lt + 2.3, 9, 'red', 1)
    leaf(img, 112, 82, 'side', 1, sign='嘘')


def s_particles(img, t, lt, v):
    """第6句：你问“你常来这儿？”，我只剩语助词"""
    bench(img, t)
    me(img, 136, 106, 'desk', 'stuck', 2)
    you_sit(img, 186, 106, 'smile', -1)
    bench_front(img)
    say(img, 176, 30, '你常来这儿？', t, t - lt, tail='l')
    for (b, s, x, y) in [(0.6, '啊…', 70, 22), (1.0, '嗯…', 30, 48), (1.4, '呢', 100, 6), (1.8, '吧', 118, 44)]:
        say(img, x, y, s, t, t - lt + b, tail='r')
    gtag(t, t - lt + 1.2, 262, 100, '语助词', 'yel')
    leaf(img, 236, 70, 'sleep', 1)


def s_callname(img, t, lt, v):
    """第7句（转折）：你走出几步回头喊我名字，我“咚”地落地——踏实"""
    avenue(img, t, 'autumn', 520 + min(lt, 1.5) * 10)
    land = 2.2
    you_on(img, t, 222, 120, 'call', 'happy', -1)
    nametag(img, t, 205, 37, 'me', born=t - lt + 0.3)
    glens(t, 220, 54, 2 * spring(lt - 0.5), 1.0, 0.1)
    if lt < land:
        me_on(img, t, 110, 120, 'idle', 'shock' if lt > 0.6 else 'smile', 1, force=True)
    else:
        me_on(img, t, 110, 120, 'idle', 'blush' if lt > land + 0.6 else 'shock', 1, force=False)
        dk = clamp((lt - land) / 0.25)
        if dk < 1:
            d = ImageDraw.Draw(img)
            for i in range(4):
                d.rectangle([110 - 16 - i * 3 - int(dk * 6), 116 - i, 110 - 14 - i * 3 - int(dk * 6), 117 - i], fill=WHITE)
                d.rectangle([110 + 14 + i * 3 + int(dk * 6), 116 - i, 110 + 16 + i * 3 + int(dk * 6), 117 - i], fill=WHITE)
        sfx(img, 76, 92, '咚', t, t - lt + land, 1.2, 'yel', 1)
        stamp(img, 52, 30, '踏实', t, t - lt + land + 0.3, GOLD_D)
    if lt < 1.8:
        falling_leaf(img, lt, 0.2, 140, 0, 122, 72, 1.6, 'happy', 1)
    else:
        leaf(img, 122, 72, 'heart' if lt > land else 'happy', 1)


# ---------------- 副歌一：秋（第一章）----------------
NOTES1 = [(48, 84), (78, 72), (108, 66), (138, 60), (168, 54), (198, 66), (228, 48), (258, 60)]


def s_staff_autumn(img, t, lt, v):
    """第8句：秋天地面，风画出五线谱，新落的银杏叶落成音符；两人的影子走过"""
    base = (226, 212, 188)
    img.paste(Image.fromarray(dither_grad(H, W, lerpc(base, WHITE, 0.2), base, 5)), (0, 0))
    d = ImageDraw.Draw(img)
    for i in range(40):
        x, y = int(hsh(i, 61) * W), int(hsh(i, 62) * H)
        d.rectangle([x, y, x + 1, y], fill=lerpc(base, INK, 0.12))
    staff_lines(img, 36, ease(seg(lt, 0.0, 1.2)), lerpc(base, INK, 0.45))
    # 两人的影子从画面上缘走过
    sx = lerp(-60, 360, seg(lt, 0, 6.5))
    sh = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(sh)
    for ox in (0, 26):          # 夕阳拉长的两道人影：脚在上缘，影子斜向右下
        fx = sx + ox
        sd.polygon([(fx, 0), (fx + 8, 0), (fx + 30, 26), (fx + 20, 26)], fill=255)
        sd.ellipse([fx + 18, 22, fx + 32, 32], fill=255)
    m = np.asarray(sh) > 0
    a = np.asarray(img).copy()
    a[m] = (a[m] * 0.8).astype(np.uint8)
    img.paste(Image.fromarray(a))
    g, gd = leaf_cols('autumn')
    for i, (x, y) in enumerate(NOTES1):
        born = 1.0 + i * 0.55
        if i == len(NOTES1) - 1:
            falling_leaf(img, lt, born, x - 20, -14, x, y, 1.0, 'happy' if lt < born + 1.6 else 'heart', 1)
            continue
        k = clamp((lt - born) / 0.9)
        if k <= 0:
            continue
        mini_leaf(img, lerp(x - 14, x, k) + math.sin(k * 8) * 6 * (1 - k), lerp(-10, y, k), g, gd)
        if k >= 1:
            gdrop(t, t - lt + born + 0.9, x, y, 8)


def s_chapter1(img, t, lt, v):
    """第9句：日历十月一页页飞走变成落叶，本子写下“第一章”"""
    page(img)
    g, gd = leaf_cols('autumn')
    n = int(seg(lt, 0.2, 2.4) * 3)
    flip = (lt * 1.8) % 1 if lt < 2.4 else 0
    calendar_face(img, 44, 18, ['10月', '10月', '11月', '11月'][min(3, n)], 'shock' if lt < 2.4 else 'happy', flip if lt < 2.4 else 0)
    d = ImageDraw.Draw(img)
    for i in range(n * 3):
        k = (lt - 0.3 - i * 0.2) * 0.6
        if k > 0:
            x = 90 + int(k * 110) + int(math.sin(k * 6 + i) * 8)
            y = 30 + int(k * 40) + i * 3
            if x < W:
                d.rectangle([x, y, x + 3, y + 2], fill=g if i % 2 else gd)
    m = int(seg(lt, 2.4, 3.6) * 3 + 0.999)
    if m > 0:
        ptext(img, 222, 46, '第一章'[:m], 3, INK, None, PAPER, PAPER, shadow=False)
        d = ImageDraw.Draw(img)
        d.line([(170, 70), (274, 70)], fill=SCARF if lt > 3.8 else (160, 160, 180), width=2)
    leaf(img, 286, 96, 'happy', 1)


def s_photo(img, t, lt, v):
    """第10句（第一次·1）：银杏树下的第一张合照，照片滑进本子标“1.”"""
    avenue(img, t, 'autumn', 900)
    me_on(img, t, 144, 120, 'cheer' if lt > 0.5 else 'idle', 'happy', 1, force=False)
    you_on(img, t, 176, 120, 'call', 'happy', -1)
    leaf(img, 200, 70, 'happy', 1)
    d = ImageDraw.Draw(img)
    if 0.5 < lt < 0.75:
        a = np.asarray(img).astype(float); a = a * 0.3 + 255 * 0.7
        img.paste(Image.fromarray(a.astype(np.uint8)))
        sfx(img, 160, 30, '咔嚓', t, t - lt + 0.5, 1.0, 'white', 1)
    if lt > 0.8:
        k = ease(seg(lt, 0.8, 1.8))
        px, py = int(lerp(150, 250, k)), int(lerp(40, 20, k))
        R(d, px + 2, py + 2, 44, 50, (120, 100, 90)); R(d, px, py, 44, 50, WHITE)
        R(d, px + 3, py + 3, 38, 34, (200, 222, 236))
        R(d, px + 3, py + 29, 38, 8, (226, 212, 188))
        me(img, px + 15, py + 36, 'idle', 'happy', 1, 1); you(img, px + 28, py + 36, 'idle', 'happy', 1, -1)
        gtag(t, t - lt + 1.9, px + 22, py + 60, '1.', 'pink', 46)


def s_generous1(img, t, lt, v):
    """第11句（慷慨又自私·1）：外套和热饮都给你【慷慨】；张开手臂挡住路人的目光【自私】"""
    avenue(img, t, 'autumn', 760)
    selfish = lt > 3.0
    if not selfish:
        you_on(img, t, 196, 120, 'idle', 'blush' if lt > 1.0 else 'smile', -1)
        me_on(img, t, 150, 120, 'give', 'smile', 1, force=False)
        cup_face(img, 176, 80, 'happy', steam=t)
        gtag(t, t - lt + 0.5, 70, 26, '慷慨', 'yel')
    else:
        for side, x0 in ((-1, 30), (1, 290)):
            person(img, x0 + int(math.sin(lt * 2) * 3), 120, 'boy' if side < 0 else 'girl', -side, 'heart', 'down', t, 1)
        you_on(img, t, 196, 120, 'idle', 'happy', -1)
        me_on(img, t, 160, 120, 'cheer', 'think', 1, force=False)
        gtag(t, t - lt + 3.1, 70, 26, '自私', 'pink')
        sfx(img, 160, 46, '不许看', t, t - lt + 3.3, 99, 'pink', 1)
    leaf(img, 120, 66, 'side' if not selfish else 'happy', 1)


def scribble(img, rows, skip_x=None, col=(120, 120, 150), y0=30, step=14):
    d = ImageDraw.Draw(img)
    for r in range(rows):
        y = y0 + r * step
        x = 44
        while x < 296:
            w = 6 + int(hsh(r, x) * 18)
            if not (skip_x and r == skip_x[0] and skip_x[1] <= x <= skip_x[2]):
                d.line([(x, y), (min(296, x + w), y)], fill=col, width=2)
            x += w + 5


def s_keyword1(img, t, lt, v):
    """第12句（关键词·1）：秋夜，自己偷偷发现——搜索框打出“你”，荧光笔扫过，满页只有“你”亮起"""
    page(img)
    glow(img, 300, 0, 160, (255, 214, 140), 0.18)
    tx, ty = 150, 51
    scribble(img, 6, (2, 140, 172))
    hl = seg(lt, 1.2, 2.2)
    if hl > 0:
        hx = int(44 + 252 * hl)
        a = np.asarray(img).copy()
        a[ty - 2:ty + 14, 44:hx] = (a[ty - 2:ty + 14, 44:hx] * 0.6 + np.array((255, 226, 90)) * 0.4).astype(np.uint8)
        img.paste(Image.fromarray(a))
        d = ImageDraw.Draw(img)
        R(d, hx - 2, ty - 6, 6, 22, GOLD); R(d, hx - 2, ty + 14, 6, 4, INK)
        leaf(img, hx + 1, ty - 14, 'happy', 1)
    draw_text(img, tx, ty, '你', SCARF if hl >= 0.45 else (120, 120, 150))
    if hl >= 0.45:
        ptext(img, tx + 5, ty + 6, '你', 2, SCARF, None, WHITE, INK)
    gsearch(t, t - lt, 170, 13, 128, '你', '结果：全部相关', t - lt + 0.3)


# ---------------- 间奏：秋 → 冬 ----------------
def s_seasons(img, t, lt, v):
    """间奏：两人在银杏大道慢慢走，叶子落光、初雪落下；走过一棵大树后换上冬装"""
    p = seg(lt, 1.0, 6.5)
    season = 'autumn' if p < 0.8 else 'winter'
    avenue(img, t, season, 1100 + lt * 18, tod=0.45 if season == 'autumn' else 0.5, fall=1.0 + 1.5 * p if season == 'autumn' else 0.8, k=max(0.25, 1 - p))
    f = int(lt * 4) % 2
    o = 'autumn' if lt < 4.6 else 'winter'
    me_on(img, t, 140, 120, 'walk1' if f else 'walk2', 'smile', 1, o, force=False)
    you_on(img, t, 176, 120, 'walk2' if f else 'walk1', 'smile', 1, o)
    if 3.8 < lt < 5.4:          # 前景的大树干扫过，借它换装
        x = int(lerp(360, -60, seg(lt, 3.8, 5.4)))
        d = ImageDraw.Draw(img)
        R(d, x, 0, 34, H, (96, 66, 46)); R(d, x + 4, 0, 6, H, (124, 88, 62))
    bubbles(t, 3, 4, 0, 320, 0, 100, 3, 6, 5.0)
    if lt < 5.0:
        k = seg(lt, 2.0, 5.0)
        falling_leaf(img, k * 3, 0, 60, 10, 160, 80, 3, 'happy', 1)


def s_press(img, t, lt, v):
    """间奏后半：冬夜书桌，窗外落雪；我戴毛线帽写字，小杏被压平成书签在本子里打盹"""
    room(img, t, 1.0, 'winter')
    me(img, 160, 100, 'desk', 'think', 2, 1, outfit='winter')
    notebook_open(img, 160, 94, write=min(1, lt / 4))
    d = ImageDraw.Draw(img)
    px = 168 + int(math.sin(lt * 6) * 8)
    d.line([(px, 98), (px + 6, 86)], fill=(250, 206, 70), width=2)
    leaf(img, 140, 98, 'sleep', 1, pal=LEAF_PRESSED)
    draw_text(img, 148, 82 - int((lt * 0.8) % 1 * 6), 'z', (220, 220, 255), outline=INK)
    bubbles(t, 3, 5, 120, 320, 10, 90, 3, 6, 4.0)


# ---------------- 主歌二：冬 ----------------
def s_board_q(img, t, lt, v):
    """第13句：想正式告白——语法教室（我脑子里）：黑板“爱 = ？”"""
    board(img, t, [(120, 22, '爱 = ？', CHALK, 3)])
    me_on(img, t, 248, 124, 'scratch', 'stuck', -1, 'winter', force=False)
    _teacher(img, 58, 112, 'happy', None)
    if lt > 0.6:
        qmark(img, 262, 46)
    if lt > 1.4:
        qmark(img, 236, 40)


def _teacher(img, x, y, expr, sign):
    leaf(img, x, y, expr, 2, sign=sign, pal=LEAF_PRESSED)
    d = ImageDraw.Draw(img)
    cy = y - 4
    d.rectangle([x - 6, cy - 2, x - 2, cy + 2], outline=INK); d.rectangle([x + 2, cy - 2, x + 6, cy + 2], outline=INK)
    d.line([(x - 2, cy), (x + 2, cy)], fill=INK)


def s_board_ab(img, t, lt, v):
    """第14句：A. 动词 B. 名词——玻璃选择框在两个答案之间来回流动"""
    board(img, t, [(120, 14, '爱 = ？', CHALK, 2), (60, 46, 'A. 动词', CHALK, 2), (180, 46, 'B. 名词', CHALK, 2)])
    pick = int(lt * 2.2) % 2
    xa, xb = 96, 216
    since = (lt * 2.2 - int(lt * 2.2)) / 2.2
    cur, prv = (xa, xb) if pick == 0 else (xb, xa)
    if lt < 1 / 2.2:
        prv = cur
    gmove(t, t - since, (prv, 60, 44), (cur, 60, 44))
    me_on(img, t, 250, 124, 'give', 'stuck', -1, 'winter', force=False)
    _teacher(img, 58, 112, 'side', 'A？' if pick == 0 else 'B？')


def s_rehearse(img, t, lt, v):
    """第15句：冬夜房间里对着小杏排练告白，捧着一颗心"""
    room(img, t, 1.0, 'winter', desk=False)
    d = ImageDraw.Draw(img)
    R(d, 0, 104, W, 76, (110, 80, 70)); R(d, 0, 104, W, 2, (140, 100, 84))
    me_on(img, t, 196, 122, 'hold', 'blush', -1, 'winter', force=False)
    heart(img, 196, 92, 2)
    if int(lt * 3) % 2:
        sfx(img, 222, 60, '扑通', t, t - lt, 99, 'pink', 1, jitter=0)
    leaf(img, 112, 110, 'happy', 2, sign='我……喜欢……', pal=LEAF_PRESSED)


def s_forget(img, t, lt, v):
    """第16句：雪中街角，你一出现，我就忘词——提词卡变成空白"""
    avenue(img, t, 'winter', 1400, tod=0.5)
    k = ease(seg(lt, 0, 0.5))
    you_on(img, t, int(lerp(330, 220, k)), 120, 'idle', 'smile', -1, 'winter')
    me_on(img, t, 130, 120, 'hold', 'stuck' if lt > 0.4 else 'blush', 1, 'winter', force=False)
    if lt > 0.4:
        gcard(t, t - lt + 0.4, 100, 34, 16, 12, r=24, tint_a=0.2)
        sfx(img, 100, 14, '忘词了！', t, t - lt + 0.5, 99, 'cyan', 1)
    leaf(img, 70, 110, 'shock', 2, sign=' ' if lt > 0.4 else '我……喜欢……', pal=LEAF_PRESSED)


def s_station_split(img, t, lt, v):
    """第17句：寒假暂别。分屏：左边你拖着行李来到站台和我会合，右边你登上列车；中间站台大钟摆"""
    a = Image.new('RGB', (W, H)); b = Image.new('RGB', (W, H))
    station(a, t, 1.0); station(b, t, 1.0)
    img.paste(a.crop((0, 0, 158, H)), (0, 0)); img.paste(b.crop((162, 0, W, H)), (162, 0))
    k = ease(seg(lt, 0.2, 1.6))
    me_on(img, t, 40, 122, 'idle', 'smile', 1, 'winter', force=False)
    you_on(img, t, int(lerp(150, 80, k)), 122, 'walk1' if k < 1 and int(lt * 4) % 2 else 'idle', 'happy', -1, 'winter')
    d = ImageDraw.Draw(img)
    sx = int(lerp(150, 80, k)) + 16
    R(d, sx, 104, 12, 16, (90, 110, 150)); R(d, sx + 4, 100, 4, 4, INK)
    k2 = ease(seg(lt, 0.6, 2.6))
    you_on(img, t, int(lerp(220, 258, k2)), 122, 'call', 'smile', 1, 'winter')
    gcard(t, None, 160, 60, 4, 64, r=24, refr=1.4, mag=0.0, tint=(200, 220, 255), tint_a=0.08)
    ang = math.sin(lt * 3.6) * 0.5
    ex, ey = 160 + int(math.sin(ang) * 26), 14 + int(math.cos(ang) * 26)
    d.line([(160, 14), (ex, ey)], fill=(90, 80, 90), width=2)
    disc(d, ex, ey, 5, (230, 200, 90))
    leaf(img, 160, 66, 'laugh' if int(lt / 0.75) % 2 == 0 else 'sad', 2, pal=LEAF_PRESSED)


def s_platform(img, t, lt, v):
    """第18句：你在车门口挥手“我先走啦~”，底下浮出潜台词“等我回来”；我笑着点头"""
    station(img, t, 1.0)
    you_on(img, t, 259, 120, 'call', 'happy', -1, 'winter')
    me_on(img, t, 150, 122 - (1 if int(lt * 3) % 2 else 0), 'idle', 'smile' if lt < 1.0 else 'happy', 1, 'winter', force=False)
    say(img, 176, 30, '我先走啦~', t, t - lt + 0.1, tail='r')
    gchip(t, t - lt + 0.8, 222, 58, '潜台词：等我回来', (250, 246, 255), 38, (40, 36, 70), 0.42)
    leaf(img, 100, 112, 'happy', 2, sign='我懂' if lt > 1.2 else None, pal=LEAF_PRESSED)


def s_trainwindow(img, t, lt, v):
    """第19句（改动句：心中）：车窗起雾，你在雾上画一颗心，里面写着我的名字"""
    img.paste(Image.fromarray(dither_grad(H, W, (206, 212, 222), (176, 182, 196), 5)), (0, 0))
    d = ImageDraw.Draw(img)
    R(d, 0, 96, W, 6, (70, 140, 160))
    x0, y0, x1, y1 = 56, 10, 264, 92
    inside = Image.fromarray(dither_grad(y1 - y0, x1 - x0, (60, 70, 110), (110, 100, 120), 5))
    img.paste(inside, (x0, y0))
    for i in range(6):
        R(d, x0 + 10 + i * 34, y0 + 52, 26, 30, (90, 80, 100))
    you_sit(img, 214, 92, 'blush' if lt > 2.0 else 'smile', -1, 'winter')
    clear = np.asarray(img).copy()
    a = np.asarray(img).astype(float)
    fog = np.zeros((H, W), bool); fog[y0:y1, x0:x1] = True
    hk = ease(seg(lt, 0.3, 1.6))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    from glass import sdf_heart as _sh
    hmask = (_sh(xx - 140, yy - 52, 34 * max(0.05, hk)) < 0) & fog
    a[fog] = a[fog] * 0.45 + np.array((236, 240, 248)) * 0.55
    a[hmask] = clear[hmask]
    img.paste(Image.fromarray(a.astype(np.uint8)))
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - 3, y0 - 3, x1 + 2, y1 + 2], outline=(150, 156, 170), width=3)
    if hk > 0.9:
        nametag(img, t, 140, 50, 'me', born=t - lt + 1.6, glowk=0.4 + 0.4 * math.sin(lt * 4) ** 2)
    gheart(t, t - lt + 0.3, 140, 52, 22, tint=(255, 180, 200), tint_a=0.10, refr=1.0)
    stamp(img, 292, 28, '踏实', t, t - lt + 2.2, GOLD_D)
    leaf(img, 26, 40, 'heart', 1, pal=LEAF_PRESSED)
    snowfall(img, t, 30, 1.0, 0, H)


# ---------------- 副歌二：冬（第二章）----------------
NOTES2 = [(70, 80), (100, 68), (130, 74), (160, 62), (190, 56), (220, 68), (250, 50)]


def s_staff_winter(img, t, lt, v):
    """第20句：冬夜书桌，把压平的银杏叶一片片摆上本子里的五线谱，写一首歌给你"""
    page(img, (238, 232, 220), rules=False)
    glow(img, 310, 0, 170, (255, 214, 140), 0.22)
    staff_lines(img, 44, 1.0, (120, 120, 150), 40, 300, 10)
    draw_text(img, 44, 10, '给你的歌（草稿）', (110, 100, 130))
    g, gd = (238, 218, 156), (208, 184, 116)
    for i, (x, y) in enumerate(NOTES2):
        born = 0.4 + i * 0.6
        k = clamp((lt - born) / 0.6)
        if k <= 0:
            continue
        mini_leaf(img, lerp(320, x, ease(k)), lerp(150, y, ease(k)), g, gd)
        if k >= 1:
            gdrop(t, t - lt + born + 0.6, x, y, 7)
    if lt > 4.6:
        falling_leaf(img, lt, 4.6, 320, 150, 280, 60, 0.8, 'happy' if lt > 5.6 else 'sleep', 1, pal=LEAF_PRESSED)
    snowfall(img, t, 12, 1.0, 0, 30)


def s_chapter2(img, t, lt, v):
    """第21句：异地的日子——视频通话里你在笑，日历一天天划掉，本子写下“第二章”"""
    room(img, t, 1.0, 'winter')
    me(img, 110, 100, 'desk', 'happy', 2, 1, outfit='winter')
    d = ImageDraw.Draw(img)
    # 手机里的视频（像素画面在下，玻璃卡在上）
    R(d, 186, 22, 60, 64, (40, 44, 70))
    you_sit(img, 216, 84, 'happy', -1, 'winter')
    gcard(t, t - lt + 0.2, 216, 54, 32, 34, r=36, refr=0.8, mag=0.02, tint=(200, 220, 255), tint_a=0.06)
    # 日历一天天划掉
    R(d, 260, 30, 50, 46, WHITE); R(d, 260, 30, 50, 9, (120, 150, 200))
    n = int(seg(lt, 0.6, 3.6) * 9)
    for i in range(12):
        cx, cy = 264 + (i % 4) * 11, 42 + (i // 4) * 11
        draw_text(img, cx, cy, str(20 + i)[-1], (90, 90, 110))
        if i < n:
            d.line([(cx - 1, cy + 1), (cx + 7, cy + 9)], fill=SCARF); d.line([(cx + 7, cy + 1), (cx - 1, cy + 9)], fill=SCARF)
    if lt > 2.0:
        gchip(t, t - lt + 2.0, 285, 88, f'还有 {max(1, 12 - n)} 天', TXT, 36)
    notebook_open(img, 110, 96, write=1.0)
    if lt > 3.8:
        gchip(t, t - lt + 3.8, 110, 30, '第二章', TXT, 52)
    leaf(img, 150, 98, 'happy', 1, pal=LEAF_PRESSED)


def s_missyou(img, t, lt, v):
    """第22句（第一次·2）：第一次打出“想你”，按下发送——已送达——回来一颗心"""
    img.paste(Image.fromarray(dither_grad(H, W, (40, 44, 80), (24, 28, 52))), (0, 0))
    snowfall(img, t, 30, 1.0, 0, H)
    d = ImageDraw.Draw(img)
    R(d, 104, 2, 112, 118, (30, 30, 46)); d.rectangle([104, 2, 215, 119], outline=(120, 120, 150))
    img.paste(Image.fromarray(dither_grad(110, 104, (232, 238, 248), (214, 222, 238), 4)), (108, 6))
    R(d, 108, 6, 104, 12, (210, 216, 232)); draw_text(img, 140, 6, '你', (90, 90, 110))
    typed = '想你'[:int(seg(lt, 0.2, 1.0) * 2 + 0.999)]
    sent = lt > 1.5
    if not sent:
        R(d, 112, 100, 96, 14, WHITE)
        draw_text(img, 116, 101, typed, INK)
        if int(lt * 3) % 2:
            R(d, 116 + text_w(typed), 102, 1, 10, (40, 120, 255))
        if lt > 1.1:
            sfx(img, 190, 92, '……', t, t - lt + 1.1, 0.5, 'white', 1)
    else:
        gchip(t, t - lt + 1.5, 182, 40, '想你', SCARF, 50, (255, 220, 225), 0.16)
        gchip(t, t - lt + 1.9, 186, 56, '已送达', (120, 120, 150), 30)
        if lt > 2.3:
            gchip(t, t - lt + 2.3, 136, 76, '♥', SCARF, 50)
    leaf(img, 70, 100, 'side' if lt < 2.3 else 'heart', 2, pal=LEAF_PRESSED)


def s_return(img, t, lt, v):
    """第23句（慷慨又自私·2）：你回来了。把手套给你【慷慨】，再把你的手揣进我的口袋【自私】"""
    station(img, t, 1.0)
    selfish = lt > 3.0
    me_on(img, t, 140, 122, 'give' if not selfish else 'idle', 'smile' if not selfish else 'blush', 1, 'winter', force=False)
    you_on(img, t, 176 if not selfish else 168, 122, 'idle', 'blush' if lt > 1.0 else 'happy', -1, 'winter')
    d = ImageDraw.Draw(img)
    if not selfish:
        for gx in (162, 168):
            R(d, gx, 84, 5, 7, (240, 230, 210)); d.rectangle([gx, 84, gx + 4, 90], outline=INK)
        gtag(t, t - lt + 0.5, 70, 26, '慷慨', 'yel')
    else:
        R(d, 146, 96, 10, 8, (78, 90, 120)); d.rectangle([146, 96, 155, 103], outline=INK)
        heart(img, 151, 84, 1)
        gtag(t, t - lt + 3.1, 70, 26, '自私', 'pink')
        sfx(img, 151, 66, '揣兜', t, t - lt + 3.2, 99, 'pink', 1)
    leaf(img, 151, 102 if selfish else 110, 'happy', 1, pal=LEAF_PRESSED)


def s_keyword2(img, t, lt, v):
    """第24句（关键词·2）：雪夜路灯下，当面把本子翻给你看——那一页只有一个大字“你”"""
    avenue(img, t, 'winter', 1700, tod=1.0, lamps=True, fall=0.6)
    you_on(img, t, 214, 120, 'idle', 'blush' if lt > 1.2 else 'smile', -1, 'winter')
    me_on(img, t, 120, 120, 'give', 'blush', 1, 'winter', force=False)
    d = ImageDraw.Draw(img)
    k = ease(seg(lt, 0.2, 0.9))
    w = int(56 * k)
    if w > 4:
        R(d, 160 - w // 2, 40, w, 40, PAPER); d.rectangle([160 - w // 2, 40, 160 + w // 2, 79], outline=INK)
        d.line([(160, 40), (160, 79)], fill=(180, 170, 150))
        if k >= 1:
            ptext(img, 176, 60, '你', 2, SCARF, None, WHITE, INK)
    if lt > 1.0:
        glens(t, 176, 60, 13 * spring(lt - 1.0), 1.2, 0.25)
    leaf(img, 132, 36, 'happy', 1, pal=LEAF_PRESSED)


def s_walkhome(img, t, lt, v):
    """副歌二后的过门：雪夜路灯下送你回家，挥手"""
    avenue(img, t, 'winter', 1900, tod=1.0, lamps=True)
    k = ease(seg(lt, 0.3, 2.8))
    you_on(img, t, int(lerp(220, 300, k)), 120, 'call', 'happy', 1, 'winter')
    me_on(img, t, 120, 120, 'give', 'smile', 1, 'winter', force=False)
    leaf(img, 145, 58, 'happy', 1, pal=LEAF_PRESSED)


# ---------------- 桥段：答案 ----------------
ACRO = '你是我的关键词'


def s_acrostic(img, t, lt, v):
    """第25句：你在台灯下读那首歌，发现每行第一个字竖着读是“你是我的关键词”"""
    if lt < 1.3:
        room(img, t, 1.0, 'winter')
        you_sit(img, 160, 100, 'smile' if lt < 0.9 else 'shock', 1, 'winter')
        notebook_open(img, 160, 94, write=1.0)
        return
    page(img, (230, 222, 206))
    glow(img, 300, 0, 160, (255, 214, 140), 0.25)
    d = ImageDraw.Draw(img)
    on = int(seg(lt, 1.5, 4.6) * 7.999)
    for i, ch in enumerate(ACRO):
        y = 9 + i * 14
        lit = i < on
        if lit:
            R(d, 40, y - 1, 14, 14, (255, 226, 90))
        draw_text(img, 41, y, ch, SCARF if lit else (90, 90, 120))
        x = 60
        while x < 290:
            w = 8 + int(hsh(i, x, 5) * 20)
            d.line([(x, y + 6), (min(290, x + w), y + 6)], fill=(110, 110, 140), width=2)
            x += w + 6
    if on > 0:
        leaf(img, 26, 15 + (on - 1) * 14, 'happy', 1, pal=LEAF_PRESSED)
        step = (lt - 1.5) / (3.1 / 7.999) - (on - 1)
        hh = ((on - 1) * 14 + 14 * clamp(spring(step / 2))) / 2 + 2
        gcard(t, None, 47.5, 7 + hh, 9, hh, r=48, refr=1.3, mag=0.12, tint=(255, 230, 150), tint_a=0.10)
    if lt > 4.8:
        gtag(t, t - lt + 4.8, 200, 104, '藏头', 'pink')


def s_answer(img, t, lt, v):
    """第26句（答案）：语法教室，玻璃选择框从 B 流到“C. 专有名词”，盖章“对”；你的名字牌下画上专名号"""
    dim = (150, 170, 160)
    board(img, t, [(120, 12, '爱 = ？', CHALK, 2), (40, 36, 'A. 动词', dim, 1), (40, 52, 'B. 名词', dim, 1)])
    m = int(seg(lt, 0.1, 0.9) * 7.999)
    if m > 0:
        draw_text(img, 112, 40, 'C. 专有名词'[:m], (255, 230, 120), 2)
    gmove(t, t - lt + 0.6, (64, 58, 26), (172, 52, 64))
    if lt > 1.0:
        stamp(img, 270, 44, '对', t, t - lt + 1.0, (60, 170, 90), 99, 2)
    if lt > 1.5:
        nametag(img, t, 160, 76, 'you', born=t - lt + 1.5, glowk=0.3)
        wk = seg(lt, 1.6, 2.2)
        d = ImageDraw.Draw(img)
        d.line([(146, 89), (146 + int(28 * wk), 89)], fill=CHALK, width=2)
        if wk >= 1:
            draw_text(img, 182, 82, '←专名号', CHALK)
    me_on(img, t, 266, 124, 'cheer' if lt > 1.0 else 'idle', 'happy' if lt > 1.0 else 'shock', -1, 'winter', force=False)
    _teacher(img, 50, 112, 'happy', 'C！' if lt > 1.0 else None)


def s_timeskip(img, t, lt, v):
    """过门（时间跳跃）：同一棵银杏树，雪 → 春芽 → 夏绿 → 秋黄，一年过去"""
    stages = [('winter', '冬'), ('spring', '春'), ('summer', '夏'), ('year2', '秋')]
    i = min(3, int(lt / 0.7))
    s, lab = stages[i]
    tod = 0.45
    sky(img, t, s if s == 'winter' else 'autumn', tod, 120)
    d = ImageDraw.Draw(img)
    R(d, 0, 120, W, 60, (226, 232, 242) if s == 'winter' else ((170, 200, 120) if s in ('spring', 'summer') else (232, 214, 184)))
    tree(img, 160, 122, s, 1.0)
    if s == 'winter':
        snowfall(img, t, 40)
    gchip(t, t - lt + i * 0.7, 160, 24, lab, TXT, 56)
    leaf(img, 196, 90, 'happy', 1, pal=LEAF_PRESSED if s == 'winter' else None)


# ---------------- 最后一遍副歌：第二年秋 ----------------
def s_staff_heart(img, t, lt, v):
    """第27句（落叶·3）：第二年秋天，两人蹲在树下，落叶围着两人的影子落成一颗心"""
    base = (232, 214, 184)
    img.paste(Image.fromarray(dither_grad(H, W, lerpc(base, WHITE, 0.25), base, 5)), (0, 0))
    a = np.asarray(img).copy()
    for cx in (140, 180):
        a[44:84, cx - 9:cx + 9] = (a[44:84, cx - 9:cx + 9] * 0.8).astype(np.uint8)
    img.paste(Image.fromarray(a))
    g, gd = leaf_cols('year2')
    pts = []
    for i in range(18):
        th = i / 18 * 2 * math.pi
        hx = 16 * math.sin(th) ** 3
        hy = -(13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th))
        pts.append((160 + hx * 4.2, 62 + hy * 3.4))
    for i, (x, y) in enumerate(pts):
        born = 0.4 + i * 0.25
        k = clamp((lt - born) / 0.7)
        if k <= 0:
            continue
        mini_leaf(img, lerp(x + 20, x, k) + math.sin(k * 8) * 5 * (1 - k), lerp(-10, y, k), g, gd)
        if k >= 1:
            gdrop(t, t - lt + born + 0.7, x, y, 7)
    if lt > 5.0:
        leaf(img, 160, 104, 'heart', 1)
    me(img, 140, 84, 'desk', 'happy', 2, 1, outfit='year2')
    you_sit(img, 180, 84, 'happy', -1)


def s_notebook2(img, t, lt, v):
    """第28句（改动句：才正要开始）：第一本写满了，两人一起翻开红色封面的第二本——第 1 页"""
    avenue(img, t, 'year2', 2300 + lt * 10, tod=0.6)
    f = int(lt * 4) % 2
    me_on(img, t, 130, 120, 'idle', 'happy', 1, 'year2', force=False)
    you_on(img, t, 196, 120, 'idle', 'happy', -1)
    book(img, 70, 86, 22, 30, NAVY)
    d = ImageDraw.Draw(img)
    for i in range(6):
        d.line([(72, 88 + i * 4), (90, 88 + i * 4)], fill=PAPER)
    k = ease(seg(lt, 0.4, 1.4))
    if k < 1:
        book(img, 150, 74, 20, 26, SCARF)
    else:
        notebook_open(img, 163, 74, 44, 0.0)
    if lt > 1.5:
        gchip(t, t - lt + 1.5, 164, 34, '第二本 · 第 1 页', TXT, 44)
    leaf(img, 163, 66, 'happy', 1) if lt > 2.2 else leaf(img, 250, 40, 'happy', 1)


def s_anniv(img, t, lt, v):
    """第29句（第一次·3）：一周年，小蛋糕插着“1”字蜡烛，两人一起吹"""
    room(img, t, 0.62, 'year2')
    me(img, 110, 100, 'desk', 'happy', 2, 1, outfit='year2')
    you_sit(img, 210, 100, 'happy', -1)
    d = ImageDraw.Draw(img)
    R(d, 138, 98, 44, 4, WHITE)
    R(d, 142, 82, 36, 16, (250, 236, 220)); R(d, 142, 82, 36, 4, (240, 160, 180))
    for x in (146, 156, 166, 174):
        disc(d, x, 81, 2, (240, 150, 170))
    R(d, 158, 66, 4, 14, WHITE); R(d, 156, 66, 4, 3, WHITE)
    out = lt > 1.6
    if not out:
        fl = int(t * 10) % 2
        R(d, 159, 60 - fl, 2, 5, (255, 200, 80)); d.point((160, 59 - fl), fill=(255, 250, 200))
    else:
        for i in range(3):
            y = 60 - int((lt - 1.6) * 12) - i * 4
            if y > 30:
                d.point((160 + (i % 2), y), fill=(200, 200, 210))
        sfx(img, 160, 40, '呼——', t, t - lt + 1.6, 1.0, 'white', 1)
    gtag(t, t - lt + 2.0, 160, 18, '第 1 年', 'pink')
    if lt < 1.6:
        leaf(img, 200, 60, 'happy', 1)
    else:
        leaf(img, 200 + int((lt - 1.6) * 30) % 60, 50, 'happy', 1, ang=(lt * 360) % 360)


def s_give(img, t, lt, v):
    """第30句（改动句：爱一个人爱得）：把写满的第一本送给你【慷慨】，封面写着“只给你”【自私】"""
    avenue(img, t, 'year2', 2500, tod=0.62)
    give = lt > 2.8
    me_on(img, t, 140, 120, 'give' if not give else 'idle', 'smile' if not give else 'blush', 1, 'year2', force=False)
    you_on(img, t, 196, 120, 'idle', 'smile' if not give else 'happy', -1)
    nx, ny = (166, 80) if not give else (196, 90)
    book(img, nx - 7, ny - 9, 14, 18, NAVY)
    gtag(t, t - lt + 0.4, 60, 30, '慷慨', 'yel')
    if give:
        book(img, 210, 8, 96, 60, NAVY)
        ptext(img, 258, 36, '只给你', 2, WHITE, None, SCARF, INK)
        gtag(t, t - lt + 3.0, 60, 52, '自私', 'pink')
    leaf(img, 112, 64, 'blush', 1)


def s_keyword3(img, t, lt, v):
    """第31句（关键词·3，角色互换）：你在旧本子的最后一页，用红笔写下我的名字作为回应"""
    page(img, (240, 228, 206))
    draw_text(img, 44, 34, '最后一页', (140, 130, 120))
    d = ImageDraw.Draw(img)
    pk = seg(lt, 0.4, 1.6)
    if pk > 0:
        n = int(pk * 40)
        for i in range(n):
            a = i / 40 * 2 * math.pi
            d.point((160 + int(math.cos(a) * 20), 70 + int(math.sin(a) * 16)), fill=SCARF)
        px, py = 160 + int(math.cos(pk * 2 * math.pi) * 20), 70 + int(math.sin(pk * 2 * math.pi) * 16)
        d.line([(px, py), (px + 10, py - 14)], fill=SCARF, width=3)
    if lt > 1.6:
        nametag(img, t, 160, 70, 'me', born=t - lt + 1.6, glowk=0.4)
    gsearch(t, t - lt + 2.2, 170, 13, 128, '你', '结果：互相', t - lt + 2.4)
    if lt > 2.8:
        nametag(img, t, 230, 70, 'you', born=t - lt + 2.8)
        gchip(t, t - lt + 3.0, 196, 98, '互相', SCARF, 44, (255, 210, 215), 0.16)
    leaf(img, 100, 70, 'heart', 1)


# ---------------- 尾奏与片尾 ----------------
def s_outro(img, t, lt, v):
    """尾奏：第二年秋天的银杏大道，两人牵手走远；小杏回头挥手，跳进第二本"""
    avenue(img, t, 'year2', 2700 + lt * 6, tod=0.66)
    f = int(lt * 4) % 2
    k = seg(lt, 3.0, 15.0)
    x = int(lerp(140, 360, k))
    me_on(img, t, x, 120, 'walk1' if f else 'walk2', 'happy', 1, 'year2', force=False)
    you_on(img, t, x + 30, 120, 'walk2' if f else 'walk1', 'happy', 1)
    bubbles(t, 5, 3, 0, 320, 0, 100, 3, 7, 5.0)
    if lt < 9:
        leaf(img, 80, 40 + math.sin(lt * 2) * 4, 'happy', 2)
        if lt > 4:
            say(img, 96, 22, '下一本见~', t, t - lt + 4, tail='l')
    else:
        falling_leaf(img, lt, 9, 80, 40, x + 15, 90, 1.5, 'happy', 1)


def s_end(img, t, lt, v):
    """片尾：晨光书桌，两本笔记本叠在一起，小杏夹在红色那本里当书签"""
    room(img, t, 0.14, 'year2', desk=True, lamp=True, wx=220)
    book(img, 14, 80, 74, 24, NAVY, '只给你')
    book(img, 20, 62, 66, 20, SCARF, '第二本')
    leaf(img, 74, 58, 'happy', 1)
    if lt > 1.0:
        gsign(40, 44, '谢谢收看', 2)


# ======================= ⑤ 镜头表（每个镜头函数只用一次）=======================
I = L
SHOTS = [
    (0.0, s_title, None),
    # 主歌一（秋）
    (I(0), s_mirror, None), (I(1), s_wordlist, None), (I(2), s_meet, None), (I(3), s_dict, None),
    (I(4), s_zip, None), (I(5), s_particles, None), (I(6), s_callname, None),
    # 副歌一（秋 · 第一章）
    (I(7), s_staff_autumn, None), (I(8), s_chapter1, None), (I(9), s_photo, None), (I(10), s_generous1, None), (I(11), s_keyword1, None),
    # 间奏（秋 → 冬）
    (68.2, s_seasons, None), (76.4, s_press, None),
    # 主歌二（冬）
    (I(12), s_board_q, None), (I(13), s_board_ab, None), (I(14), s_rehearse, None), (I(15), s_forget, None),
    (I(16), s_station_split, None), (I(17), s_platform, None), (I(18), s_trainwindow, None),
    # 副歌二（冬 · 第二章）
    (I(19), s_staff_winter, None), (I(20), s_chapter2, None), (I(21), s_missyou, None), (I(22), s_return, None), (I(23), s_keyword2, None),
    (134.9, s_walkhome, None),
    # 桥段（答案）
    (I(24), s_acrostic, None), (I(25), s_answer, None),
    (147.3, s_timeskip, None),
    # 最后一遍副歌（第二年秋）
    (I(26), s_staff_heart, None), (I(27), s_notebook2, None), (I(28), s_anniv, None), (I(29), s_give, None), (I(30), s_keyword3, None),
    (179.8, s_outro, None),
    (song.p['end_start'], s_end, None),
]
SHOTS.sort(key=lambda s: s[0])
ALLOW_REPEAT = {}
SECTIONS = [L(0) + 0.12, L(7) + 0.12, 68.2, L(12) + 0.12, L(19) + 0.12, L(24) + 0.12, L(26) + 0.12, 179.8, song.p['end_start']]

# ======================= ⑥ 歌词花字 =======================
CFG = {
    '好好爱自己/就有人会爱你': dict(pal='white', kw=['爱自己', '爱你'], kwpal=['yel', 'pink'], size=100, angle=-2),
    '这乐观的说词': dict(pal='whiteb', kw=['说词'], kwpal='yel', angle=2),
    '幸福的样子/我感觉好真实': dict(pal='white', kw=['真实'], kwpal='pink', size=100, angle=-2),
    '找不到形容词': dict(pal='whiteb', kw=['形容词'], kwpal='yel', angle=2, deco=('q',)),
    '沉默在掩饰/快泛滥的激情': dict(pal='white', kw=['泛滥', '激情'], kwpal=['cyan', 'pink'], size=100, angle=-2),
    '只剩下语助词': dict(pal='whiteb', kw=['语助词'], kwpal='yel', angle=2, deco=('sweat',)),
    '有一种踏实/当你口中喊我名字': dict(pal='white', kw=['踏实', '名字'], kwpal=['yel', 'pink'], size=96, angle=-2),
    '落叶的位置/谱出一首诗': dict(pal='whiteb', kw=['落叶', '诗'], kwpal=['yel', 'yel'], size=100, angle=2, deco=('note',)),
    '时间在消逝/我们的故事开始': dict(pal='white', kw=['故事开始'], kwpal='pink', size=96, angle=-2),
    '这是第一次': dict(pal='whiteb', kw=['第一次'], kwpal='pink', size=130, angle=2, deco=('star',)),
    '让我见识爱情/可以慷慨又自私': dict(pal='white', kw=['慷慨', '自私'], kwpal=['yel', 'pink'], size=96, angle=-2),
    '你是我的关键词': dict(pal='whiteb', kw=['你', '关键词'], kwpal=['pink', 'yel'], size=130, kwscale=1.4, angle=2, deco=('star', 'note')),
    '我不太确定/爱最好的方式': dict(pal='whiteb', kw=['爱'], kwpal='pink', size=100, angle=-2, deco=('q',)),
    '是动词或名词': dict(pal='white', kw=['动词', '名词'], kwpal=['yel', 'yel'], angle=2),
    '很想告诉你/最赤裸的感情': dict(pal='whiteb', kw=['赤裸'], kwpal='pink', size=100, angle=-2),
    '却又忘词': dict(pal='white', kw=['忘词'], kwpal='yel', size=140, angle=3, deco=('sweat',)),
    '聚散总有时/而哭笑也有时': dict(pal='whiteb', kw=['聚散', '哭笑'], kwpal=['cyan', 'cyan'], size=100, angle=-2),
    '我不怕潜台词': dict(pal='white', kw=['潜台词'], kwpal='yel', angle=2),
    '有一种踏实/是你心中有我名字': dict(pal='whiteb', kw=['心中', '名字'], kwpal=['pink', 'pink'], kwscale=1.45, size=96, angle=-2),
    '你藏在歌词/代表的意思': dict(pal='white', kw=['歌词'], kwpal='yel', size=100, angle=-2),
    '是专有名词': dict(pal='whiteb', kw=['专有名词'], kwpal='yel', size=140, angle=2, deco=('star', 'bang')),
    '我们的故事/才正要开始': dict(pal='white', kw=['才正要开始'], kwpal='pink', kwscale=1.4, size=100, angle=-2),
    '爱一个人爱得/如此慷慨又自私': dict(pal='white', kw=['爱一个人爱得', '自私'], kwpal=['pink', 'yel'], size=96, angle=-2),
}
# 冬天的副歌（第 20–24 句）：换成蓝描边底色，和秋天区分；最后一遍“你是我的关键词”再放大
for i in range(19, 24):
    c = dict(CFG[song.lines[i][2]]); c['pal'] = 'whiteb' if c['pal'] == 'white' else 'white'; CFG[i] = c
CFG[30] = dict(CFG['你是我的关键词'], size=150, kwscale=1.5)

MVX = MV(song, SHOTS, CFG, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE, sections=SECTIONS)
frame = MVX.frame
DUR = song.dur

# ======================= ⑦ 封面 =======================
COVER_T = L(18) + 2.6          # 车窗雾上画的心，里面是我的名字


def COVER_3X4(img, t):
    """竖版：第二年秋天的银杏树下，落叶围成心，两人在心里；上方玻璃搜索框“你”"""
    sc = Image.new('RGB', (W, H))
    avenue(sc, t, 'year2', 2380, tod=0.6)
    img.paste(COV.portrait_from(sc, 70, 60))
    d = ImageDraw.Draw(img)
    g, gd = leaf_cols('year2')
    for i in range(22):
        th = i / 22 * 2 * math.pi
        hx = 16 * math.sin(th) ** 3
        hy = -(13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th))
        mini_leaf(img, 90 + hx * 3.6 - 7, 132 + hy * 2.9 - 6, g, gd)
    me(img, 74, 190, 'idle', 'heart', 2, 1, outfit='year2')
    you(img, 108, 190, 'idle', 'blush', 2, -1)
    _leaf_px(img, 150, 128, 'heart', 2)
    gsearch(t, None, 90, 72, 74, '你', '结果：全部相关', t - 9)
