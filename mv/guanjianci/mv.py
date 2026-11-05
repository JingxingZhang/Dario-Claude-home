"""《关键词》像素 MV（原唱：林俊杰）—— 镜头脚本。角色见 cast.py，分镜见 分镜说明.md，精读见 歌词精读.md。
  镜头函数 fn(img, t, lt, v)：v=False 午后 / True 黄昏（副歌二）/ 2 清晨（最后一遍副歌）。
"""
import math, os, sys
SKILL = os.environ.get('PIXMV_SKILL', '')
sys.path.insert(0, os.path.join(SKILL, 'lib'))
ROOT = os.environ.get('PIXMV_PROJECT', os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *            # draw_text, text_w, dither_grad, draw_sky, draw_water, seg, ease, hsh, lerpc …
from charkit import *           # pixmap, put, recolor, eyes, mouth, palette_strip —— 设计角色用
from props2 import *            # ptext, sfx, stamp, say, OS, sys_msg, popup, cursor, meter, toggle, danmaku, face …（综艺元素与道具）
from chars import heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, curtains, R
from engine import Song, MV
import huazi as Z

song = Song(ROOT)
rms, pump, beat_phase, L = song.rms, song.pump, song.beat_phase, song.L

# ======================= ① 视觉方案（见 分镜说明.md）=======================
# 曲风：抒情流行慢板 / BPM≈68 / 钢琴+弦乐 → 一句一镜、小幅动作；花字小回弹、慢逐字
# 主色 纸米白（笔记本=词的世界）+ 强调 银杏金（落叶/小杏）+ 点睛 围巾红（只属于“你”）+ 暗色 墨蓝（深夜书桌）
PALETTE = {'paper': (244, 236, 216), 'gold': (246, 196, 62), 'scarf': (226, 74, 70), 'ink': (30, 32, 60)}
LYRIC_BASE = dict(pop=1.08, stagger=0.09, float_amp=3)
TITLE_STYLE = dict(pal='yel', size=230, angle=-3, deco=('note', 'star'))

# ======================= ② 角色设计（cast.py：从零绘制）=======================
sys.path.insert(0, ROOT)
from cast import me, you, leaf, ME_PAL, YOU_PAL, LEAF_PAL, GOLD, GOLD_D, SCARF, INK


def CAST_SHEET(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(244, 236, 216))
    for y in range(26, 180, 10):
        d.line([(0, y), (320, y)], fill=(226, 216, 196))
    d.line([(10, 0), (10, 180)], fill=(236, 170, 160))
    draw_text(img, 16, 2, '《关键词》', INK)
    draw_text(img, 90, 2, '我：写字的人', (58, 82, 140))
    draw_text(img, 206, 2, '你：红围巾', SCARF)
    leaf(img, 300, 10 + int(math.sin(t * 6) * 2), 'happy', 1, ang=math.sin(t * 3) * 30)
    k = int(t * 4) % 2
    poses = [('idle', 'smile', '站'), ('walk1' if k else 'walk2', 'happy', '走'), ('hold', 'blush', '抱本子'),
             ('give', 'smile', '递'), ('cheer', 'happy', '欢呼'), ('scratch', 'stuck', '挠头')]
    for i, (p, e, lab) in enumerate(poses):
        x = 30 + i * 30
        me(img, x, 82, p, e)
        draw_text(img, x - text_w(lab) // 2, 84, lab, (120, 100, 90))
    exs = [('smile', '笑'), ('shock', '惊'), ('blush', '脸红'), ('stuck', '词穷'), ('heart', '心动'), ('zip', '拉链')]
    for i, (e, lab) in enumerate(exs):
        x = 30 + i * 30
        me(img, x, 138, 'desk', e)
        draw_text(img, x - text_w(lab) // 2, 140, lab, (120, 100, 90))
    for i, (p, e, lab) in enumerate([('idle', 'smile', '站'), ('walk1' if k else 'walk2', 'happy', '走'), ('call', 'blush', '喊你')]):
        x = 222 + i * 34
        you(img, x, 82, p, e)
        draw_text(img, x - text_w(lab) // 2, 84, lab, (120, 100, 90))
    draw_text(img, 206, 98, '小杏·银杏叶(贯穿)', GOLD_D)
    for i, (e, lab) in enumerate([('happy', ''), ('shock', ''), ('side', ''), ('blush', ''), ('sleep', ''), ('heart', '')]):
        leaf(img, 224 + (i % 3) * 36, 124 + (i // 3) * 28, e)
    palette_strip(img, 16, 154, list(PALETTE.values()))
    draw_text(img, 62, 152, '纸 银杏金 围巾红 墨蓝', (120, 100, 90))
    draw_text(img, 16, 167, '像素MV · @张景行', (160, 140, 120))


# ======================= ③ 场景（按这首歌现画）=======================
from chars import person, qmark
DUSK = (255, 150, 80)
PAPER = (244, 236, 216)
RULE = (196, 208, 226)
CHALK = (232, 238, 226)
LAND_T = L(6) + 2.2          # 第 7 句“喊我名字”时落地：之前的镜头里“我”都微微飘着


def tod_of(v):
    """副歌一=午后，副歌二(v=True)=黄昏，最后一遍(v=2)=第二天清晨"""
    return 0.10 if v == 2 else (0.80 if v is True else 0.45)


def glow(img, cx, cy, r, col, k=0.35):
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    m = np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) * k
    m = np.floor(m * 6 + np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] - 0.5).clip(0, 6) / 6
    a = a * (1 - m[..., None]) + np.array(col, float) * m[..., None]
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)))


def gold_of(tod):
    if tod > 0.6:
        return lerpc(GOLD, DUSK, 0.45 * clamp((tod - 0.6) / 0.25)), lerpc(GOLD_D, (190, 90, 50), 0.4 * clamp((tod - 0.6) / 0.25))
    if tod < 0.2:
        return lerpc(GOLD, (250, 214, 180), 0.25), lerpc(GOLD_D, (200, 140, 120), 0.25)
    return GOLD, GOLD_D


def tree(img, x, ground, tod, big=1.0):
    d = ImageDraw.Draw(img)
    g, gd = gold_of(tod)
    th = int(36 * big)
    R(d, x - 3, ground - th, 6, th, (110, 76, 52)); R(d, x - 3, ground - th, 2, th, (140, 100, 70))
    cy = ground - th - int(10 * big)
    blobs = [(0, 0, 17), (-15, 7, 12), (15, 7, 12), (-7, -11, 11), (9, -10, 11)]
    for ox, oy, r in blobs:
        disc(d, x + int(ox * big), cy + int(oy * big) + 2, int(r * big), gd)
    for ox, oy, r in blobs:
        disc(d, x + int(ox * big), cy + int(oy * big), int(r * big) - 1, g)
    for i in range(18):
        px, py = x + int((hsh(i, x, 1) - 0.5) * 40 * big), cy + int((hsh(i, x, 2) - 0.6) * 26 * big)
        d.point((px, py), fill=lerpc(g, WHITE, 0.4))


def street_lamp(img, x, ground, on):
    d = ImageDraw.Draw(img)
    R(d, x - 1, ground - 58, 3, 58, (60, 56, 70)); R(d, x - 5, ground - 62, 11, 5, (60, 56, 70))
    R(d, x - 3, ground - 57, 7, 3, (255, 236, 170) if on else (120, 120, 130))
    if on:
        glow(img, x, ground - 55, 34, (255, 214, 140), 0.35)


def avenue(img, t, tod=0.45, scroll=0.0, ground=104, lamps=None, fall=1.0):
    """深秋银杏大道：远处一排小树 + 近景大树 + 落叶铺地 + 飘叶"""
    draw_sky(img, tod, hz=ground, sun=tod < 0.9, stars=0.8 if tod > 0.9 else 0, t=t)
    d = ImageDraw.Draw(img)
    g, gd = gold_of(tod)
    top, bot = sky_colors(tod)
    for i in range(16):
        x = int((i * 26 - scroll * 0.3) % 416) - 48
        c = lerpc(g, bot, 0.45)
        disc(d, x, ground - 12, 11, c); R(d, x - 1, ground - 4, 2, 4, lerpc((110, 76, 52), bot, 0.4))
    path = (226, 212, 188) if 0.2 <= tod <= 0.6 else ((222, 206, 214) if tod < 0.2 else lerpc((226, 212, 188), (160, 110, 110), clamp((tod - 0.6) / 0.35)))
    R(d, 0, ground, W, H - ground, path)
    R(d, 0, ground, W, 2, lerpc(path, (120, 110, 80), 0.4))
    for i in range(70):
        x = int((hsh(i, 11) * 420 - scroll) % 420) - 50
        y = ground + 3 + int(hsh(i, 12) * (H - ground - 4))
        d.rectangle([x, y, x + 2, y + 1], fill=g if hsh(i, 13) > 0.3 else gd)
    for i in range(4):
        x = int((i * 110 + 40 - scroll) % 440) - 60
        tree(img, x, ground + 2, tod)
        if lamps is not None and i % 2 == 1:
            street_lamp(img, x + 55, ground + 2, lamps)
    if fall:
        for i in range(int(14 * fall)):
            ph = (t * 0.16 + hsh(i, 7)) % 1
            x = int((hsh(i, 8) * 360 - scroll * 0.8 + math.sin(t * 1.4 + i) * 12) % 360) - 20
            y = int(-6 + ph * (ground + 16))
            if int(t * 4 + i) % 2:
                d.rectangle([x, y, x + 2, y + 1], fill=g)
            else:
                d.rectangle([x, y, x + 1, y + 2], fill=gd)


def shadow(img, x, y, w=12, faint=False):
    d = ImageDraw.Draw(img)
    c = (0, 0, 0)
    a = np.asarray(img).copy()
    y0, y1 = max(0, y - 1), min(H, y + 2)
    x0, x1 = max(0, x - w), min(W, x + w)
    a[y0:y1, x0:x1] = (a[y0:y1, x0:x1] * (0.85 if faint else 0.7)).astype(np.uint8)
    img.paste(Image.fromarray(a))


def me_on(img, t, x, y, pose='idle', expr='smile', face_dir=1, pal=None, force=None):
    """站着的我：第 7 句之前飘离地面 3 像素，影子发虚"""
    fl = (t < LAND_T) if force is None else force
    bob = -3 - int(round(math.sin(t * 2.2))) if fl else 0
    shadow(img, x, y, 9 if fl else 12, fl)
    return me(img, x, y, pose, expr, 2, face_dir, pal, bob)


def you_on(img, t, x, y, pose='idle', expr='smile', face_dir=1):
    shadow(img, x, y, 12)
    return you(img, x, y, pose, expr, 2, face_dir)


def room(img, t, tod=1.0, desk=True, lamp=True, wx=14):
    night = tod > 0.9
    top, bot = ((44, 46, 88), (28, 30, 58)) if night else ((236, 224, 204), (210, 196, 176))
    img.paste(Image.fromarray(dither_grad(H, W, top, bot)), (0, 0))
    d = ImageDraw.Draw(img)
    win = Image.new('RGB', (W, H))
    draw_sky(win, tod, hz=78, sun=not night, stars=0.9 if night else 0, t=t)
    img.paste(win.crop((wx, 10, wx + 86, 78)), (wx, 10))
    # 窗外的银杏枝
    g, gd = gold_of(0.45 if night else tod)
    if night:
        g, gd = lerpc(GOLD, (60, 60, 100), 0.35), lerpc(GOLD_D, (40, 40, 80), 0.35)
    d.line([(wx, 30), (wx + 50, 44), (wx + 86, 40)], fill=(70, 50, 44), width=2)
    for i in range(14):
        px, py = wx + 4 + int(hsh(i, 21) * 70), 26 + int(hsh(i, 22) * 26)
        d.rectangle([px, py, px + 3, py + 2], fill=g if i % 3 else gd)
    if night:
        moon(img, wx + 66, 22, 7, 'sleep' if t < 10 else 'happy')
    fr = (120, 90, 66) if night else (176, 136, 96)
    d.rectangle([wx - 2, 8, wx + 87, 79], outline=fr, width=3)
    R(d, wx + 42, 10, 2, 68, fr); R(d, wx, 43, 86, 2, fr)
    R(d, wx - 6, 79, 98, 4, lerpc(fr, WHITE, 0.15))
    if lamp:
        lx = 286
        R(d, lx - 1, 70, 3, 30, (70, 64, 80)); R(d, lx - 8, 98, 17, 3, (70, 64, 80))
        d.polygon([(lx - 10, 70), (lx + 10, 70), (lx + 6, 60), (lx - 6, 60)], fill=(230, 120, 80))
        if night:
            glow(img, lx, 80, 90, (255, 214, 140), 0.32)
    if desk:
        R(d, 0, 100, W, 80, (140, 92, 60)); R(d, 0, 100, W, 3, (176, 124, 84)); R(d, 0, 103, W, 1, (100, 64, 44))


def notebook_open(img, cx, y, w=56, write=0.0, tint=None):
    d = ImageDraw.Draw(img)
    pc = tint or PAPER
    d.polygon([(cx - w // 2, y + 12), (cx - w // 2 + 4, y), (cx - 1, y + 1), (cx - 1, y + 13)], fill=pc, outline=INK)
    d.polygon([(cx + 1, y + 1), (cx + w // 2 - 4, y), (cx + w // 2, y + 12), (cx + 1, y + 13)], fill=pc, outline=INK)
    for i in range(int(write * 6)):
        yy = y + 3 + (i % 3) * 3
        xx = cx - w // 2 + 7 if i < 3 else cx + 4
        d.line([(xx, yy), (xx + 16, yy)], fill=(90, 90, 120))


def page(img, tint=None, holes=True):
    """笔记本内页（词的世界）"""
    pc = tint or PAPER
    img.paste(Image.fromarray(dither_grad(H, W, lerpc(pc, WHITE, 0.3), pc, 4)), (0, 0))
    d = ImageDraw.Draw(img)
    rc = lerpc(RULE, pc, 0.2)
    for y in range(22, H, 14):
        d.line([(0, y), (W, y)], fill=rc)
    d.line([(34, 0), (34, H)], fill=(236, 156, 146))
    if holes:
        for y in range(10, H, 18):
            disc(d, 12, y, 3, lerpc(pc, INK, 0.6))


def mood(img, v):
    """副歌二：夕阳从右上照进来；最后一遍：清晨的淡紫晨光"""
    if v is True:
        glow(img, 330, -20, 300, (255, 140, 80), 0.32)
    elif v == 2:
        glow(img, -10, -10, 280, (190, 180, 255), 0.25)


def page_tint(v):
    return {False: PAPER, True: (246, 222, 200), 2: (238, 232, 240)}.get(v, PAPER)


def board(img, t, chalk_lines=()):
    img.paste(Image.fromarray(dither_grad(H, W, (222, 206, 178), (200, 182, 152), 5)), (0, 0))
    d = ImageDraw.Draw(img)
    R(d, 18, 4, 284, 92, (150, 104, 64))
    img.paste(Image.fromarray(dither_grad(84, 276, (46, 86, 70), (36, 70, 58), 4)), (22, 8))
    for i in range(30):
        x, y = 24 + int(hsh(i, 41) * 270), 10 + int(hsh(i, 42) * 80)
        d.point((x, y), fill=(70, 110, 92))
    R(d, 16, 96, 288, 4, (176, 128, 84))
    R(d, 0, 104, W, 76, (176, 140, 104))
    for x in range(0, W, 40):
        d.line([(x, 104), (x, H)], fill=(150, 116, 84))
    for (x, y, s, col, sc) in chalk_lines:
        draw_text(img, x, y, s, col, sc)


def nametag(img, cx, cy, who='me', glowk=0.0, scale=1):
    """名字牌：只画小头像，不编真实名字"""
    d = ImageDraw.Draw(img)
    w, h = 22 * scale, 20 * scale
    x0, y0 = cx - w // 2, cy - h // 2
    if glowk > 0:
        glow(img, cx, cy, 26 * scale, (255, 236, 160), 0.5 * glowk)
        d = ImageDraw.Draw(img)
    R(d, x0, y0, w, h, WHITE)
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=SCARF, width=max(1, scale))
    from cast import ME_HEAD, YOU_HEAD
    spr = pixmap(ME_HEAD if who == 'me' else YOU_HEAD, ME_PAL if who == 'me' else YOU_PAL)
    put(img, spr, cx, y0 + h - 2 * scale, scale)


def tag(img, x, y, s, col, t, born):
    """语法标签【××】"""
    if t < born:
        return
    sfx(img, x, y, '【' + s + '】', t, born, 99, col, 1, jitter=0)


def falling_leaf(img, t, born, x0, y0, x1, y1, dur, expr='happy', scale=2):
    """小杏飘落：转着圈，落定后露脸"""
    k = clamp((t - born) / dur)
    if k >= 1:
        leaf(img, x1, y1, expr, scale)
        return x1, y1
    e = ease(k)
    x = lerp(x0, x1, e) + math.sin(k * 9) * 14 * (1 - k)
    y = lerp(y0, y1, k)
    leaf(img, x, y, expr, scale, ang=math.sin(k * 11) * 40)
    return x, y


# ======================= ④ 镜头 =======================
def s_title(img, t, lt, v):
    """前奏：深夜书桌，银杏叶从窗外飘进来，落在空白笔记本上"""
    room(img, t, 1.0)
    awake = lt > 10.0
    me(img, 250, 100, 'desk', 'shock' if 10.0 < lt < 10.9 else ('smile' if awake else 'stuck'), 2)
    notebook_open(img, 250, 94)
    d = ImageDraw.Draw(img)
    tap = 3 if beat_phase(t) < 0.12 and lt < 9.6 else 0
    R(d, 268, 86 - tap, 2, 9, (250, 206, 70)); R(d, 268, 95 - tap, 2, 1, INK)
    if lt < 2.0:
        leaf(img, 54, 34, 'sleep', 1)
    elif lt < 8.0:
        falling_leaf(img, lt, 2.0, 54, 34, 246, 90, 6.0, 'sleep', 1)
    elif lt < 12.0:
        leaf(img, 246, 90, 'sleep' if lt < 10 else 'happy', 1)
        if 10.0 < lt < 11.5:
            sfx(img, 236, 70, '！', t, t - lt + 10.0, 1.5, 'yel', 1)
        if lt < 10:
            draw_text(img, 254, 76 - int((lt * 0.8) % 1 * 6), 'z', (220, 220, 255), outline=INK)
    else:
        k = ease(seg(lt, 12.0, 12.8))
        leaf(img, lerp(246, 266, k), lerp(90, 72, k) - math.sin(k * math.pi) * 14, 'happy', 1)


def s_mirror(img, t, lt, v):
    """第1句：和自己对话——镜子里的我竖起大拇指"""
    img.paste(Image.fromarray(dither_grad(H, W, (236, 226, 236), (212, 200, 214), 5)), (0, 0))
    d = ImageDraw.Draw(img)
    R(d, 0, 104, W, 76, (196, 170, 150)); R(d, 0, 104, W, 2, (170, 140, 120))
    cx, cy, r = 110, 54, 44
    disc(d, cx, cy, r + 4, (170, 130, 90)); disc(d, cx, cy, r, (200, 226, 236))
    mirror = Image.new('RGB', (W, H), (200, 226, 236))
    m = ImageDraw.Draw(mirror)
    for i in range(3):
        m.line([(cx - 30 + i * 8, cy - 30), (cx - 10 + i * 8, cy - 40)], fill=(230, 244, 250))
    me(mirror, cx + 4, cy + 52, 'give' if lt > 0.8 else 'idle', 'happy' if lt > 0.8 else 'smile', 2, 1)
    mk = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mk).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(mirror, (0, 0), mk)
    # 便利贴
    R(d, cx + 18, cy - 46, 40, 22, (255, 232, 120)); d.rectangle([cx + 18, cy - 46, cx + 57, cy - 25], outline=GOLD_D)
    draw_text(img, cx + 20, cy - 44, '好好', INK); draw_text(img, cx + 20, cy - 33, '爱自己', INK)
    me_on(img, t, 214, 118, 'idle', 'smile' if lt < 1.4 else 'blush', -1)
    leaf(img, cx - 34, cy - 40, 'happy', 1)
    if lt > 1.0:
        sfx(img, 60, 22, '赞！', t, t - lt + 1.0, 1.8, 'yel', 1)


def s_note(img, t, lt, v):
    """第2句：便利贴特写，被贴上【说词】标签；小杏将信将疑"""
    img.paste(Image.fromarray(dither_grad(H, W, (236, 226, 236), (214, 202, 216), 5)), (0, 0))
    d = ImageDraw.Draw(img)
    R(d, 86, 14, 150, 92, (220, 180, 90)); R(d, 82, 10, 150, 92, (255, 232, 120))
    R(d, 82, 10, 150, 10, (250, 216, 96))
    ptext(img, 157, 42, '好好爱自己', 2, INK, None, (255, 232, 120), (255, 232, 120), shadow=False)
    ptext(img, 157, 70, '就有人会爱你', 1, INK, None, (255, 232, 120), (255, 232, 120), shadow=False)
    tag(img, 157, 94, '说词', 'cyan', t, t - lt + 0.5)
    leaf(img, 270, 92, 'side' if lt > 0.9 else 'happy', 2, sign='真的假的？' if lt > 0.9 else None)


def s_real(img, t, lt, v):
    """第3句：银杏大道，你第一次出现；我捏自己的脸——真实度 100%"""
    sc = 40 + lt * 14
    avenue(img, t, 0.45, sc)
    walk = lt < 1.7
    f = int(lt * 5) % 2
    you_on(img, t, 196, 120, ('walk1' if f else 'walk2') if walk else 'idle', 'smile' if lt < 2 else 'happy')
    me_on(img, t, 140, 120, ('walk1' if f else 'walk2') if walk else 'scratch', 'blush' if walk else ('shock' if lt < 2.4 else 'heart'))
    if lt > 1.7:
        sfx(img, 116, 50, '痛！', t, t - lt + 1.8, 0.8, 'red', 1)
    meter(img, 8, 8, '真实度', ease(seg(lt, 1.9, 2.9)), (255, 110, 120), 60)
    if lt > 2.0:
        for i in range(3):
            heart(img, 150 + i * 9, 50 - int((lt * 12 + i * 5) % 14), 1)


def s_dict(img, t, lt, v):
    """第4句：翻字典找形容词——查无此词"""
    room(img, t, 1.0)
    me(img, 160, 100, 'desk', 'stuck' if lt > 1.0 else 'shock', 2)
    d = ImageDraw.Draw(img)
    # 字典
    R(d, 126, 92, 68, 16, (150, 50, 50)); R(d, 128, 90, 64, 14, (248, 240, 222)); R(d, 159, 90, 2, 14, (200, 190, 170))
    fl = (lt * 6) % 1
    if lt < 1.4:
        x = int(160 + math.cos(fl * math.pi) * 30)
        d.line([(160, 104), (x, 90 - int(math.sin(fl * math.pi) * 10))], fill=WHITE, width=2)
        sfx(img, 210, 74, '哗哗', t, t - lt, 1.4, 'white', 1)
    n = min(9, int(lt * 4))
    for i in range(n):
        x, y = 70 + int(hsh(i, 51) * 30) - (i % 3) * 14, 98 - (i // 3) * 6
        disc(d, x, y, 4, WHITE); d.point((x - 1, y), fill=(180, 180, 190)); d.point((x + 1, y + 1), fill=(180, 180, 190))
    leaf(img, 236, 94, 'shock' if lt > 1.0 else 'happy', 1)
    if lt > 1.0:
        popup(img, 178, 6, '词典', '查无此词', ('确定',), 0, lt > 2.0, w=132)


def bench_scene(img, t, lt, v):
    avenue(img, t, 0.5, 300, fall=0.7)
    d = ImageDraw.Draw(img)
    # 长椅：靠背挡住下半身
    return d


def bench_front(img):
    d = ImageDraw.Draw(img)
    for y in (96, 103):
        R(d, 98, y, 124, 4, (150, 96, 60)); R(d, 98, y, 124, 1, (186, 128, 84))
    R(d, 104, 107, 3, 14, (70, 60, 60)); R(d, 214, 107, 3, 14, (70, 60, 60))
    R(d, 96, 110, 128, 4, (130, 82, 52))


def s_bench(img, t, lt, v):
    """第5句：长椅并坐，我拉链嘴，激情水位越过警戒线"""
    bench_scene(img, t, lt, v)
    me(img, 136, 106, 'desk', 'zip', 2)
    _you_sit(img, 186, 106, 'smile', 1)
    bench_front(img)
    d = ImageDraw.Draw(img)
    # 激情水位计
    x0, y0, hgt = 268, 14, 80
    R(d, x0 - 1, y0 - 1, 18, hgt + 2, INK); R(d, x0, y0, 16, hgt, (230, 236, 246))
    lv = ease(seg(lt, 0.2, 2.8)) * 1.04
    wy = y0 + hgt - int(hgt * min(1, lv))
    R(d, x0, wy, 16, y0 + hgt - wy, (250, 110, 140))
    for i in range(0, 16, 4):
        d.point((x0 + i + int(t * 8) % 4, wy), fill=WHITE)
    wl = y0 + 18
    d.line([(x0 - 4, wl), (x0 + 20, wl)], fill=(230, 40, 60))
    draw_text(img, x0 - 40, wl - 6, '警戒线', (230, 40, 60), outline=WHITE)
    draw_text(img, x0 - 10, y0 + hgt + 3, '激情', INK, outline=WHITE)
    if lv > 0.78:
        sfx(img, 240, 8, '要溢出了', t, t - lt + 2.3, 9, 'red', 1)
    leaf(img, 112, 82, 'side', 1, sign='嘘')


def _you_sit(img, x, y, expr, face_dir):
    from cast import YOU_HEAD, YOU_BODY, _join
    body = '\n'.join(YOU_BODY['idle'].strip('\n').split('\n')[:7])
    spr = pixmap(_join(YOU_HEAD, body), YOU_PAL)
    w, h = put(img, spr, x, y, 2, face_dir)
    from cast import _face, YOU_EYE, YOU_MOUTH
    x0, y0 = int(x - w // 2), int(y - h)
    if face_dir > 0:
        _face(img, x0, y0, 2, YOU_EYE, YOU_MOUTH, expr)
    else:
        ww = spr.width
        _face(img, x0, y0, 2, (ww - 2 - YOU_EYE[0] - YOU_EYE[2], YOU_EYE[1], YOU_EYE[2]), (ww - 2 - YOU_MOUTH[0] - 3, YOU_MOUTH[1]), expr)


def s_particles(img, t, lt, v):
    """第6句：你问“？”，我只剩语助词"""
    bench_scene(img, t, lt, v)
    me(img, 136, 106, 'desk', 'stuck', 2)
    _you_sit(img, 186, 106, 'smile', -1)
    bench_front(img)
    say(img, 196, 40, '？', tail='l')
    words = [(0.15, '啊…', 70, 22), (0.7, '嗯…', 104, 8), (1.2, '呢', 40, 46), (1.6, '吧', 136, 30)]
    for (b, s, x, y) in words:
        if lt > b:
            say(img, x, y, s, tail='r')
    tag(img, 250, 92, '语助词', 'yel', t, t - lt + 1.0)
    leaf(img, 236, 70, 'sleep', 1)
    if lt > 1.0:
        sweat(img, 160, 66, 1)


def s_name(img, t, lt, v):
    """第7句（转折）：你回头喊我名字，我“咚”地落地——踏实"""
    avenue(img, t, 0.5, 520 + min(lt, 1.5) * 10)
    land = 2.2
    fl = lt < land
    you_on(img, t, 222, 120, 'call', 'happy', -1)
    if lt > 0.3:
        bubble_box(img, 186, 22, 38, 30, WHITE, INK, 'r')
        nametag(img, 205, 37, 'me')
    if fl:
        me_on(img, t, 110, 120, 'idle', 'shock' if lt > 0.6 else 'smile', 1, force=True)
    else:
        dk = clamp((lt - land) / 0.25)
        me_on(img, t, 110, 120, 'idle', 'blush' if lt > land + 0.6 else 'shock', 1, force=False)
        if dk < 1:
            d = ImageDraw.Draw(img)
            for i in range(4):
                d.rectangle([110 - 16 - i * 3 - int(dk * 6), 116 - i, 110 - 14 - i * 3 - int(dk * 6), 117 - i], fill=(250, 248, 240))
                d.rectangle([110 + 14 + i * 3 + int(dk * 6), 116 - i, 110 + 16 + i * 3 + int(dk * 6), 117 - i], fill=(250, 248, 240))
        sfx(img, 76, 92, '咚', t, t - lt + land, 1.2, 'yel', 1)
        stamp(img, 52, 30, '踏实', t, t - lt + land + 0.3, GOLD_D)
    if lt < 1.8:
        falling_leaf(img, lt, 0.2, 140, 0, 122, 72, 1.6, 'happy', 1)
    else:
        leaf(img, 122, 72, 'heart' if lt > land else 'happy', 1)


STAFF_Y = [36, 48, 60, 72, 84]
NOTES = [(48, 84), (78, 72), (108, 66), (138, 60), (168, 54), (198, 66), (228, 48), (258, 60)]


def s_staff(img, t, lt, v):
    """第8句：风在地上画出五线谱，落叶一片片落成音符"""
    tod = tod_of(v)
    base = (226, 212, 188) if v is False else ((232, 186, 160) if v is True else (226, 216, 228))
    img.paste(Image.fromarray(dither_grad(H, W, lerpc(base, WHITE, 0.2), base, 5)), (0, 0))
    mood(img, v)
    d = ImageDraw.Draw(img)
    for i in range(40):
        x, y = int(hsh(i, 61) * W), int(hsh(i, 62) * H)
        d.rectangle([x, y, x + 1, y], fill=lerpc(base, INK, 0.12))
    g, gd = gold_of(tod)
    wk = ease(seg(lt, 0.0, 1.2))
    for y in STAFF_Y:
        d.line([(16, y), (16 + int(288 * wk), y)], fill=lerpc(base, INK, 0.45))
    if wk > 0:
        for i in range(5):
            xx = 16 + int(288 * wk) + i * 3
            d.point((min(W - 1, xx), STAFF_Y[i] - 2), fill=WHITE)
    # 高音谱号：用像素画
    clef = '''
...k.
..k.k
..k.k
..kk.
.kk..
k.k..
k.kkk
.kkk.
..k..
.kk..
'''
    put(img, pixmap(clef, {'k': lerpc(base, INK, 0.7)}, None), 26, 90, 3, 1)
    for i, (x, y) in enumerate(NOTES):
        born = 1.0 + i * 0.55
        if i == len(NOTES) - 1:
            falling_leaf(img, lt, born, x - 20, -14, x, y, 1.0, 'happy' if lt < born + 1.6 else 'heart', 1)
            if lt > born + 1.0:
                sparkle(img, x + 10, y - 10, 3)
            continue
        k = clamp((lt - born) / 0.9)
        if k <= 0:
            continue
        lx = lerp(x - 14, x, k) + math.sin(k * 8) * 6 * (1 - k)
        ly = lerp(-10, y, k)
        spr = pixmap('''
.yy.yy.
yyyyyyy
.yyyyy.
..yyy..
...t...
''', {'y': g, 't': gd})
        put(img, spr, int(lx), int(ly) + 3, 2, 1)
        if k >= 1 and lt - born - 0.9 < 0.5:
            sfx(img, x, y - 16, '♪', t, t - lt + born + 0.9, 0.5, 'yel', 1, jitter=0)
    # 远处两个人的身影（右上）
    if v is not False or lt > 2:
        draw_text(img, 250, 6, '♪ ♫', lerpc(base, INK, 0.5))


def s_chapter(img, t, lt, v):
    """第9句：日历翻走变成落叶，新的一页写上“第一章”"""
    page(img, page_tint(v))
    mood(img, v)
    g, gd = gold_of(tod_of(v))
    n = int(seg(lt, 0.2, 2.4) * 4)
    flip = (lt * 1.8) % 1 if lt < 2.4 else 0
    labels = ['10月', '11月', '12月', '1月', '2月']
    calendar_face(img, 44, 18, labels[min(4, n)], 'shock' if lt < 2.4 else 'happy', flip if lt < 2.4 else 0)
    d = ImageDraw.Draw(img)
    for i in range(n * 2):
        k = (lt - 0.3 - i * 0.25) * 0.6
        if k <= 0:
            continue
        x = 90 + int(k * 110) + int(math.sin(k * 6 + i) * 8)
        y = 30 + int(k * 40) + i * 3
        if x < W:
            d.rectangle([x, y, x + 3, y + 2], fill=g if i % 2 else gd)
    title = '第一章'
    m = int(seg(lt, 2.4, 3.6) * 3 + 0.999)
    if m > 0:
        ptext(img, 222, 46, title[:m], 3, INK, None, PAPER, PAPER, shadow=False)
        d = ImageDraw.Draw(img)
        d.line([(170, 70), (274, 70)], fill=SCARF if lt > 3.8 else (160, 160, 180), width=2)
    if 2.4 < lt < 3.8:
        px = 180 + int(seg(lt, 2.4, 3.6) * 84)
        d.line([(px, 54), (px + 8, 38)], fill=(250, 206, 70), width=3); d.point((px, 55), fill=INK)
    leaf(img, 286, 96, 'happy', 1)


def s_first(img, t, lt, v):
    """第10句：第一行写下“1.”，盖章“第1次”"""
    page(img, page_tint(v))
    mood(img, v)
    draw_text(img, 42, 26, '1.', INK, 2)
    d = ImageDraw.Draw(img)
    wk = seg(lt, 0.1, 0.9)
    d.line([(66, 40), (66 + int(200 * wk), 40)], fill=(150, 150, 170))
    stamp(img, 166, 66, '第1次', t, t - lt + 0.35, GOLD_D, 99, 3)
    if lt > 0.5:
        for i in range(6):
            a = i / 6 * 6.283 + lt
            rr = 50 + (lt - 0.5) * 20
            if rr < 80:
                sparkle(img, int(166 + math.cos(a) * rr), int(66 + math.sin(a) * rr * 0.5), 2)
    if lt < 1.2:
        leaf(img, 270, 90, 'happy', 2)
    else:
        leaf(img, 270, 86 - int(abs(math.sin(lt * 4)) * 8), 'happy', 2, ang=0)
        sfx(img, 270, 52, '耶！', t, t - lt + 1.2, 99, 'yel', 1)


def balance(img, cx, cy, sway):
    d = ImageDraw.Draw(img)
    R(d, cx - 1, cy, 3, 26, (90, 80, 90)); R(d, cx - 8, cy + 26, 17, 3, (90, 80, 90))
    a = sway
    lx, ly = cx - 34, cy + int(a * 3)
    rx, ry = cx + 34, cy - int(a * 3)
    d.line([(lx, ly), (rx, ry)], fill=(90, 80, 90), width=2)
    for x, y, s, col in ((lx, ly, '慷慨', GOLD_D), (rx, ry, '自私', SCARF)):
        d.line([(x, y), (x - 10, y + 12)], fill=(120, 110, 120)); d.line([(x, y), (x + 10, y + 12)], fill=(120, 110, 120))
        R(d, x - 13, y + 12, 27, 3, (120, 110, 120))
        draw_text(img, x - text_w(s) // 2, y + 16, s, col, outline=WHITE)
    heart(img, rx, ry + 8, 1)
    cup_face(img, lx, ly + 6, 'happy')


def s_generous(img, t, lt, v):
    """第11句：前半句把热饮外套都给你【慷慨】，后半句张开手臂挡住路人的目光【自私】"""
    tod = tod_of(v)
    avenue(img, t, tod, 760, lamps=(v is True) or None)
    selfish = lt > 3.0
    f = int(lt * 4) % 2
    if not selfish:
        you_on(img, t, 196, 120, 'idle', 'blush' if lt > 1.0 else 'smile', -1)
        me_on(img, t, 150, 120, 'give', 'smile', 1, force=False)
        cup_face(img, 176, 80, 'happy', steam=t)
        tag(img, 70, 26, '慷慨', 'yel', t, t - lt + 0.5)
    else:
        for side, x0 in ((-1, 30), (1, 290)):
            person(img, x0 + int(math.sin(lt * 2) * 3), 120, 'boy' if side < 0 else 'girl', -side, 'heart', 'down', t, 1)
        you_on(img, t, 196, 120, 'idle', 'happy', -1)
        me_on(img, t, 160, 120, 'cheer', 'think', 1, force=False)
        tag(img, 70, 26, '自私', 'pink', t, t - lt + 3.1)
        sfx(img, 160, 46, '不许看', t, t - lt + 3.3, 99, 'pink', 1)
    balance(img, 262, 10, math.sin(lt * 2.5) * (0.6 if not selfish else 0.2))
    leaf(img, 120, 66, 'side' if not selfish else 'happy', 1)


def scribble_rows(img, rows, col=(120, 120, 150), seed=0, skip=()):
    d = ImageDraw.Draw(img)
    for r in range(rows):
        y = 30 + r * 14
        x = 44
        while x < 296:
            w = 6 + int(hsh(r, x, seed) * 18)
            if (r, x) not in skip:
                d.line([(x, y), (min(296, x + w), y)], fill=col, width=2)
            x += w + 5


def searchbar(img, t, lt, q, born, res):
    d = ImageDraw.Draw(img)
    R(d, 44, 4, 252, 16, WHITE); d.rectangle([44, 4, 295, 19], outline=INK)
    from chars import magnifier
    magnifier(img, 48, 6, 4)
    n = len(q) if lt > born else 0
    draw_text(img, 64, 6, q[:n], SCARF)
    if int(lt * 2) % 2 and lt < born + 0.6:
        R(d, 64 + text_w(q[:n]), 6, 1, 11, INK)
    if lt > born + 0.6:
        draw_text(img, 291 - text_w(res), 6, res, (120, 120, 140))


def s_keyword(img, t, lt, v):
    """第12句：搜索框输入“你”，荧光笔扫过，只有“你”亮起"""
    page(img, page_tint(v))
    mood(img, v)
    final = v == 2
    hl_k = seg(lt, 1.2, 2.2)
    rows = 6
    tx, ty = 150, 30 + 2 * 14 - 7
    if not final:
        scribble_rows(img, rows, skip={(2, x) for x in range(140, 172)})
        d = ImageDraw.Draw(img)
        if hl_k > 0:
            hx = int(44 + 252 * hl_k)
            a = np.asarray(img).copy()
            a[ty - 2:ty + 14, 44:hx] = (a[ty - 2:ty + 14, 44:hx] * 0.6 + np.array((255, 226, 90)) * 0.4).astype(np.uint8)
            img.paste(Image.fromarray(a))
            d = ImageDraw.Draw(img)
            R(d, hx - 2, ty - 6, 6, 22, GOLD); R(d, hx - 2, ty + 14, 6, 4, INK)
            leaf(img, hx + 1, ty - 14, 'happy', 1)
        draw_text(img, tx, ty, '你', SCARF if hl_k >= 0.45 else (120, 120, 150), 1)
        if hl_k >= 0.45:
            ptext(img, tx + 5, ty + 6, '你', 2, SCARF, None, WHITE, INK)
            sparkle(img, tx + 16, ty - 4, 2)
    else:
        # 最后一句：整页的字一个接一个变成“你”
        nn = int(seg(lt, 0.6, 3.6) * 6 * 15)
        d = ImageDraw.Draw(img)
        for r in range(rows):
            for c in range(15):
                k = r * 15 + c
                x, y = 46 + c * 16, 24 + r * 14
                if k < nn:
                    draw_text(img, x, y, '你', SCARF)
                else:
                    d.line([(x, y + 6), (x + 11, y + 6)], fill=(120, 120, 150), width=2)
        if lt > 3.6:
            leaf(img, 160, 112, 'heart', 1)
    searchbar(img, t, lt, '你', 0.2, '结果：全部相关' if not final else '结果：全部是你')


def s_walk(img, t, lt, v):
    """间奏：两人在银杏大道慢慢走，从午后走到黄昏；小杏乘风冲浪"""
    tod = 0.45 + seg(lt, 0, 8.0) * 0.3
    avenue(img, t, tod, 900 + lt * 22)
    f = int(lt * 4) % 2
    me_on(img, t, 140, 120, 'walk1' if f else 'walk2', 'smile', 1, force=False)
    you_on(img, t, 176, 120, 'walk2' if f else 'walk1', 'smile', 1)
    x = 40 + (lt * 30) % 300
    leaf(img, x, 30 + math.sin(lt * 2) * 8, 'happy', 1, ang=math.sin(lt * 3) * 20 if int(lt) % 3 == 0 else 0)
    if 2 < lt < 4.5:
        say(img, int(x) - 6, 44, '呼~', tail='l')


def s_write(img, t, lt, v):
    """间奏后半：深夜书桌，我认真写字，小杏在台灯下打盹"""
    room(img, t, 1.0)
    me(img, 160, 100, 'desk', 'think', 2)
    notebook_open(img, 160, 94, write=min(1, lt / 4))
    d = ImageDraw.Draw(img)
    px = 168 + int(math.sin(lt * 6) * 8)
    d.line([(px, 98), (px + 6, 86)], fill=(250, 206, 70), width=2)
    if int(lt * 3) % 2:
        sfx(img, 196, 80, '沙沙', t, t - lt, 99, 'white', 1, jitter=0)
    leaf(img, 270, 94, 'sleep', 1)
    draw_text(img, 278, 76 - int((lt * 0.8) % 1 * 6), 'z', (220, 220, 255), outline=INK)


def s_board_q(img, t, lt, v):
    """第13句：语法课，黑板“爱 = ？”，我挠头"""
    board(img, t, [(120, 22, '爱 = ？', CHALK, 3)])
    me_on(img, t, 248, 124, 'scratch', 'stuck', -1, force=False)
    _teacher(img, 58, 112, 'happy', None)
    if lt > 0.6:
        qmark(img, 262, 46)
    if lt > 1.4:
        qmark(img, 236, 40)


def _teacher(img, x, y, expr, sign):
    leaf(img, x, y, expr, 2, sign=sign)
    d = ImageDraw.Draw(img)
    cy = y - 4
    d.rectangle([x - 6, cy - 2, x - 2, cy + 2], outline=INK); d.rectangle([x + 2, cy - 2, x + 6, cy + 2], outline=INK)
    d.line([(x - 2, cy), (x + 2, cy)], fill=INK)


def s_board_ab(img, t, lt, v):
    """第14句：A. 动词  B. 名词——我举着粉笔犹豫"""
    board(img, t, [(120, 14, '爱 = ？', CHALK, 2), (60, 46, 'A. 动词', CHALK, 2), (180, 46, 'B. 名词', CHALK, 2)])
    d = ImageDraw.Draw(img)
    pick = int(lt * 2.2) % 2
    x = 60 if pick == 0 else 180
    d.rectangle([x - 4, 44, x + 74, 74], outline=(255, 230, 120))
    me_on(img, t, 250, 124, 'give', 'stuck', -1, force=False)
    _teacher(img, 58, 112, 'side', 'A？' if pick == 0 else 'B？')


def s_rehearse(img, t, lt, v):
    """第15句：对着小杏排练告白，捧着一颗心"""
    room(img, t, 1.0, desk=False)
    d = ImageDraw.Draw(img)
    R(d, 0, 104, W, 76, (110, 80, 70)); R(d, 0, 104, W, 2, (140, 100, 84))
    me_on(img, t, 196, 122, 'hold', 'blush', -1, force=False)
    heart(img, 196, 92, 2)
    if int(lt * 3) % 2:
        sfx(img, 222, 60, '扑通', t, t - lt, 99, 'pink', 1, jitter=0)
    leaf(img, 112, 110, 'happy', 2, sign='我……喜欢……')


def s_forget(img, t, lt, v):
    """第16句：你一出现，提词卡一片空白——忘词"""
    avenue(img, t, 0.55, 1300)
    k = ease(seg(lt, 0, 0.5))
    you_on(img, t, int(lerp(330, 220, k)), 120, 'idle', 'smile', -1)
    me_on(img, t, 130, 120, 'hold', 'stuck' if lt > 0.4 else 'blush', 1, force=False)
    d = ImageDraw.Draw(img)
    if lt > 0.4:
        R(d, 116, 20, 28, 20, WHITE); d.rectangle([116, 20, 143, 39], outline=INK)
        sfx(img, 130, 10, '忘词了！', t, t - lt + 0.5, 99, 'cyan', 1)
    leaf(img, 70, 110, 'shock', 2, sign='　　　' if lt > 0.4 else '我……喜欢……')


def s_split(img, t, lt, v):
    """第17句：分屏——左边相聚，右边道别；中间钟摆；小杏在哭笑之间翻转"""
    a = Image.new('RGB', (W, H)); b = Image.new('RGB', (W, H))
    avenue(a, t, 0.45, 200, fall=0.5); avenue(b, t, 0.82, 260, fall=0.5)
    img.paste(a.crop((0, 0, 158, H)), (0, 0)); img.paste(b.crop((162, 0, W, H)), (162, 0))
    d = ImageDraw.Draw(img)
    R(d, 158, 0, 4, H, WHITE)
    k = ease(seg(lt, 0.2, 1.6))
    me_on(img, t, int(lerp(30, 64, k)), 120, 'walk1' if k < 1 and int(lt * 4) % 2 else 'idle', 'happy', 1, force=False)
    you_on(img, t, int(lerp(130, 96, k)), 120, 'walk2' if k < 1 and int(lt * 4) % 2 else 'idle', 'happy', -1)
    if k >= 1:
        heart(img, 80, 50, 1)
    k2 = ease(seg(lt, 0.4, 3.0))
    me_on(img, t, 200, 120, 'give', 'smile', 1, force=False)
    you_on(img, t, int(lerp(236, 300, k2)), 120, 'call', 'smile', 1)
    # 钟摆
    ang = math.sin(lt * 3.6) * 0.5
    d.line([(160, 0), (160 + int(math.sin(ang) * 30), int(math.cos(ang) * 30))], fill=(90, 80, 90), width=2)
    disc(d, 160 + int(math.sin(ang) * 30), int(math.cos(ang) * 30), 5, GOLD)
    leaf(img, 160, 62, 'laugh' if int(lt / 0.75) % 2 == 0 else 'sad', 2)


def s_subtext(img, t, lt, v):
    """第18句：“我先走啦”底下浮出潜台词“明天见”"""
    avenue(img, t, 0.7, 1500)
    you_on(img, t, 214, 120, 'call', 'happy', -1)
    me_on(img, t, 120, 120 - (1 if int(lt * 3) % 2 else 0), 'idle', 'smile' if lt < 1.0 else 'happy', 1, force=False)
    say(img, 176, 30, '我先走啦~', t, t - lt + 0.1, tail='r')
    if lt > 0.8:
        draw_text(img, 162, 50, '（潜台词：明天见）', (120, 110, 140), outline=WHITE)
    leaf(img, 64, 112, 'happy', 2, sign='我懂' if lt > 1.2 else None)


def s_heartname(img, t, lt, v):
    """第19句：心中有我名字——心形小窗里，我的名字牌在发光"""
    avenue(img, t, 0.6, 1700)
    you_on(img, t, 214, 120, 'idle', 'blush', -1)
    me_on(img, t, 120, 120, 'idle', 'heart' if lt > 1.5 else 'smile', 1, force=False)
    k = ease(seg(lt, 0.3, 1.2))
    if k > 0:
        hk = max(1, int(round(6 * k)))
        heart(img, 166, 44, hk)
        if k >= 1:
            nametag(img, 166, 46, 'me', glowk=0.5 + 0.5 * math.sin(lt * 4) ** 2)
        d = ImageDraw.Draw(img)
        d.line([(196, 82), (180, 64)], fill=WHITE)
    stamp(img, 50, 30, '踏实', t, t - lt + 2.0, GOLD_D)
    leaf(img, 270, 60, 'heart', 1)


def s_lampbye(img, t, lt, v):
    """副歌二后的过门：黄昏转夜，路灯下挥手告别"""
    tod = 0.82 + seg(lt, 0, 2.8) * 0.16
    avenue(img, t, tod, 2000, lamps=True)
    k = ease(seg(lt, 0.3, 2.8))
    you_on(img, t, int(lerp(220, 300, k)), 120, 'call', 'happy', 1)
    me_on(img, t, 120, 120, 'give', 'smile', 1, force=False)
    leaf(img, 145, 58, 'happy', 1)


ACRO = '你是我的关键词'


def s_acrostic(img, t, lt, v):
    """第25句：你藏在歌词——七行字的第一个字依次亮起，竖着读是“你是我的关键词”"""
    page(img, (220, 210, 196))
    glow(img, 300, 0, 160, (255, 214, 140), 0.25)
    d = ImageDraw.Draw(img)
    on = int(seg(lt, 0.3, 4.2) * 7.999)
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
        leaf(img, 26, 15 + (on - 1) * 14, 'happy', 1)
    if lt > 4.4:
        d.rectangle([38, 7, 56, 108], outline=SCARF, width=2)
        sfx(img, 200, 112 - 8, '藏头', t, t - lt + 4.4, 99, 'pink', 1)


def s_answer(img, t, lt, v):
    """第26句：选项 C. 专有名词（盖“对”字章）——名字牌下画上专名号"""
    dim = (150, 170, 160)
    board(img, t, [(120, 12, '爱 = ？', CHALK, 2), (40, 36, 'A. 动词', dim, 1), (40, 52, 'B. 名词', dim, 1)])
    m = int(seg(lt, 0.1, 0.9) * 7.999)
    s = 'C. 专有名词'
    if m > 0:
        draw_text(img, 112, 40, s[:m], (255, 230, 120), 2)
    d = ImageDraw.Draw(img)
    if lt > 1.0:
        stamp(img, 270, 44, '对', t, t - lt + 1.0, (60, 170, 90), 99, 2)
    if lt > 1.5:
        nametag(img, 160, 76, 'you', glowk=0.3)
        wk = seg(lt, 1.6, 2.2)
        d = ImageDraw.Draw(img)
        d.line([(146, 89), (146 + int(28 * wk), 89)], fill=CHALK, width=2)
        if wk >= 1:
            draw_text(img, 182, 82, '←专名号', CHALK)
    me_on(img, t, 266, 124, 'cheer' if lt > 1.0 else 'idle', 'happy' if lt > 1.0 else 'shock', -1, force=False)
    _teacher(img, 50, 112, 'happy', 'C！' if lt > 1.0 else None)


def s_road(img, t, lt, v):
    """第28句：清晨，长长的银杏大道——故事才正要开始；枝头冒出新芽"""
    avenue(img, t, 0.1, 2300 + lt * 16)
    f = int(lt * 4) % 2
    me_on(img, t, 180, 120, 'walk1' if f else 'walk2', 'happy', 1, force=False)
    you_on(img, t, 210, 120, 'walk2' if f else 'walk1', 'happy', 1)
    d = ImageDraw.Draw(img)
    d.line([(0, 14), (60, 22), (90, 18)], fill=(110, 76, 52), width=3)
    bk = ease(seg(lt, 2.2, 3.4))
    if bk > 0:
        r = max(1, int(4 * bk))
        disc(d, 84, 14, r, (140, 210, 110)); disc(d, 84, 14 - r // 2, max(1, r - 2), (190, 240, 150))
        if bk >= 1:
            sparkle(img, 92, 8, 2)
    leaf(img, 60, 34, 'shock' if 2.2 < lt < 3.6 else 'happy', 1)
    R(d, 220, 4, 96, 16, PAPER); d.rectangle([220, 4, 315, 19], outline=INK)
    draw_text(img, 225, 6, '第1页·未完待续', INK)


def s_give(img, t, lt, v):
    """第30句：把整本写满的笔记本送给你【慷慨】，封面写着“只给你”【自私】"""
    avenue(img, t, 0.12, 2500)
    give = lt > 2.8
    d = ImageDraw.Draw(img)
    me_on(img, t, 140, 120, 'give' if not give else 'idle', 'smile' if not give else 'blush', 1, force=False)
    you_on(img, t, 196, 120, 'idle', 'smile' if not give else 'happy', -1)
    nx, ny = (166, 80) if not give else (196, 90)
    R(d, nx - 7, ny - 9, 14, 18, (58, 82, 140)); d.rectangle([nx - 7, ny - 9, nx + 6, ny + 8], outline=INK)
    R(d, nx - 4, ny - 5, 8, 3, PAPER)
    tag(img, 60, 30, '慷慨', 'yel', t, t - lt + 0.4)
    if give:
        R(d, 210, 8, 96, 60, (58, 82, 140)); d.rectangle([210, 8, 305, 67], outline=INK)
        R(d, 216, 14, 84, 48, (52, 74, 128))
        ptext(img, 258, 38, '只给你', 2, WHITE, None, SCARF, INK)
        tag(img, 60, 50, '自私', 'pink', t, t - lt + 3.0)
    leaf(img, 112, 64, 'blush', 1)


def s_outro(img, t, lt, v):
    """尾奏：清晨，两人沿着银杏大道越走越远"""
    avenue(img, t, 0.14, 2700 + lt * 6)
    f = int(lt * 4) % 2
    k = seg(lt, 3.0, 15.0)
    x = int(lerp(140, 360, k))
    me_on(img, t, x, 120, 'walk1' if f else 'walk2', 'happy', 1, force=False)
    you_on(img, t, x + 32, 120, 'walk2' if f else 'walk1', 'happy', 1)
    lx = 80
    leaf(img, lx, 40 + math.sin(lt * 2) * 4, 'happy', 2)
    if lt > 8:
        say(img, lx + 16, 24, '故事继续~', t, t - lt + 8, tail='l')


def s_end(img, t, lt, v):
    """片尾：晨光书桌，笔记本合上，小杏夹在里面当书签"""
    room(img, t, 0.12, desk=True, lamp=True, wx=220)
    d = ImageDraw.Draw(img)
    x0, y0 = 16, 72
    R(d, x0 + 3, y0 + 3, 70, 28, (100, 64, 44))
    R(d, x0, y0, 70, 28, (58, 82, 140)); d.rectangle([x0, y0, x0 + 69, y0 + 27], outline=INK)
    R(d, x0 + 4, y0 + 24, 62, 3, PAPER)
    draw_text(img, x0 + 10, y0 + 8, '只给你', WHITE)
    leaf(img, x0 + 58, y0 - 6, 'happy', 1)
    leaf(img, 40, 40, 'happy', 2, sign='谢谢收看') if lt > 1.0 else None


# ======================= ⑤ 镜头表 =======================
I = L
SHOTS = [
    (0.0, s_title, False),
    (I(0), s_mirror, False), (I(1), s_note, False), (I(2), s_real, False), (I(3), s_dict, False),
    (I(4), s_bench, False), (I(5), s_particles, False), (I(6), s_name, False),
    # 副歌一（午后）
    (I(7), s_staff, False), (I(8), s_chapter, False), (I(9), s_first, False), (I(10), s_generous, False), (I(11), s_keyword, False),
    # 间奏
    (68.2, s_walk, False), (76.4, s_write, False),
    # 主歌二
    (I(12), s_board_q, False), (I(13), s_board_ab, False), (I(14), s_rehearse, False), (I(15), s_forget, False),
    (I(16), s_split, False), (I(17), s_subtext, False), (I(18), s_heartname, False),
    # 副歌二（黄昏）
    (I(19), s_staff, True), (I(20), s_chapter, True), (I(21), s_first, True), (I(22), s_generous, True), (I(23), s_keyword, True),
    (134.9, s_lampbye, True),
    # 桥段
    (I(24), s_acrostic, False), (I(25), s_answer, False),
    # 最后一遍副歌（清晨）
    (I(26), s_staff, 2), (I(27), s_road, 2), (I(28), s_first, 2), (I(29), s_give, 2), (I(30), s_keyword, 2),
    (179.3, s_outro, 2),
    (song.p['end_start'], s_end, 2),
]
SHOTS.sort(key=lambda s: s[0])
DANMU = {}

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
    '我不太确定/爱最好的方式': dict(pal='white', kw=['爱'], kwpal='pink', size=100, angle=-2, deco=('q',)),
    '是动词或名词': dict(pal='whiteb', kw=['动词', '名词'], kwpal=['yel', 'yel'], angle=2),
    '很想告诉你/最赤裸的感情': dict(pal='white', kw=['赤裸'], kwpal='pink', size=100, angle=-2),
    '却又忘词': dict(pal='whiteb', kw=['忘词'], kwpal='yel', size=140, angle=3, deco=('sweat',)),
    '聚散总有时/而哭笑也有时': dict(pal='white', kw=['聚散', '哭笑'], kwpal=['cyan', 'cyan'], size=100, angle=-2),
    '我不怕潜台词': dict(pal='whiteb', kw=['潜台词'], kwpal='yel', angle=2),
    '有一种踏实/是你心中有我名字': dict(pal='white', kw=['踏实', '心中', '名字'], kwpal=['yel', 'pink', 'pink'], size=96, angle=-2),
    '你藏在歌词/代表的意思': dict(pal='white', kw=['歌词'], kwpal='yel', size=100, angle=-2),
    '是专有名词': dict(pal='whiteb', kw=['专有名词'], kwpal='yel', size=140, angle=2, deco=('star', 'bang')),
    '我们的故事/才正要开始': dict(pal='white', kw=['才正要开始'], kwpal='pink', size=100, angle=-2),
    '爱一个人爱得/如此慷慨又自私': dict(pal='white', kw=['慷慨', '自私'], kwpal=['yel', 'pink'], size=96, angle=-2),
}

MVX = MV(song, SHOTS, CFG, danmu=DANMU, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE)
frame = MVX.frame
DUR = song.dur
