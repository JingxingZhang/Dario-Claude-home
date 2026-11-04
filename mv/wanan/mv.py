"""《晚安》（原唱：颜人中；词曲：陈志杰）像素 MV —— 镜头脚本。

主题：暧昧——比朋友更进一步、又还不是恋人。“我”（男生）和“你”（女生）每晚聊到很晚、用一句晚安收尾；
她忽近忽远，“我”越陷越深。贯穿道具是关系进度条「朋友——●——恋人」，滑块总卡在中间的「暧昧区」。
窗外戴睡帽的弯月是旁观者兼起哄担当。副歌一上头，副歌二热情褪色，副歌三天快亮；
结尾贴原词「多情的人始终难堪」：难堪还是“我”的，但这次“我”把手机扣下，先对月亮说了晚安。
"""
import math, os, sys
from functools import lru_cache
SKILL = os.environ.get('PIXMV_SKILL', '')
sys.path.insert(0, os.path.join(SKILL, 'lib'))
ROOT = os.environ.get('PIXMV_PROJECT', os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *
from charkit import *
from props2 import *
from chars import heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, R, qmark, paste
from engine import Song, MV
import huazi as Z

song = Song(ROOT)
rms, pump, beat_phase, L = song.rms, song.pump, song.beat_phase, song.L

# ======================= ① 视觉方案 =======================
# 曲风：中慢板 R&B 情歌（≈54 BPM 半拍感 / 检测 108.5），主歌克制、副歌三层推高，最后一遍副歌能量最大。
#   → 一句一镜，主歌慢推慢移；副歌每句 2–3 个动作点踩在重点词上；花字回弹小、逐字偏慢。
# 世界：现代城市的深夜——卧室窗边、手机屏幕、楼下街口（“窗挡住月色”“长夜”“不舍夜晚”“晚安”）。
# 配色：主色午夜靛蓝（夜）、强调色月光奶黄（月色 + 等待的心）、暗色墨紫；“你”的专属色是酒红（暧昧）。
#   第二遍副歌（v is True）：热情褪色 → 冷青灰；最后一遍（v == 'dawn'）：天快亮 → 靛蓝渐变到晨粉。
PAL_SETS = {
    False: dict(sky0=(18, 18, 52), sky1=(58, 52, 122), moon=(255, 230, 150), glow=(255, 214, 120), wall=(40, 38, 84),
                wall2=(56, 52, 108), ink=(14, 12, 30), you=(150, 48, 88), scr=(130, 226, 255), hot=(255, 120, 160)),
    True: dict(sky0=(14, 26, 36), sky1=(48, 82, 98), moon=(214, 230, 232), glow=(170, 210, 220), wall=(32, 48, 60),
               wall2=(44, 64, 78), ink=(10, 16, 22), you=(108, 70, 96), scr=(150, 220, 230), hot=(150, 200, 220)),
    'dawn': dict(sky0=(46, 40, 104), sky1=(250, 160, 160), moon=(255, 236, 190), glow=(255, 200, 150), wall=(70, 56, 110),
                 wall2=(96, 74, 132), ink=(26, 18, 44), you=(150, 48, 88), scr=(160, 230, 255), hot=(255, 140, 150)),
}
PALETTE = {k: PAL_SETS[False][k] for k in ('sky0', 'sky1', 'moon', 'you', 'ink')}


def P(v):
    return PAL_SETS['dawn'] if v == 'dawn' else PAL_SETS[True] if v is True else PAL_SETS[False]


LYRIC_BASE = dict(pop=1.12, stagger=0.08, float_amp=3)
TITLE_STYLE = dict(pal='yel', size=240, angle=-3, deco=('star', 'heart'))

# ======================= ② 角色设计 =======================
# 比例 ≈3 头身：R&B 流行的日常感，同时让 1 像素的五官在 320×180 里看得清表情。
# 我：乱翘的呆毛 + 挂在脖子上的靛蓝耳机 + 月光奶黄的宽松毛衣（“月色”和等待的颜色）。
LEAD_HEAD = '''
.......hh.......
......hh........
...hhhhhhhhhh...
..hhhhhhhhhhhh..
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.hhhshhhhhshhhh.
.hhsssssssssshh.
.hssssssssssssh.
.hssssssssssssh.
..ssssssssssss..
...ssssssssss...
....ssssssss....
'''
LEAD_TORSO = {
    'idle': '''
......ssss......
...ewwwwwwwwe...
..wwwwwwwwwwww..
.wwwwwwwwwwwwww.
.wwdwwwwwwwwdww.
.wwdwwwwwwwwdww.
.wwdwwwwwwwwdww.
.wwdwwwwwwwwdww.
.ssdwwwwwwwwdss.
...dddddddddd...
''',
    'phone': '''
......ssss......
...ewwwwwwwwe...
..wwwwwwwwwwww..
.wwwwwwwwwwwwww.
.wwwwwwwwwwwwww.
.wwwddsggsddwww.
.wwwddsggsddwww.
.wwwwwwwwwwwwww.
..wwwwwwwwwwww..
...dddddddddd...
''',
    'wave': '''
......ssss.....s
...ewwwwwwwwe.ws
..wwwwwwwwwwwww.
.wwwwwwwwwwwww..
.wwdwwwwwwwwd...
.wwdwwwwwwwwd...
.wwdwwwwwwwwd...
.wwdwwwwwwwwd...
.ssdwwwwwwwwd...
...dddddddddd...
''',
    'heart': '''
......ssss......
...ewwwwwwwwe...
..wwwwwwwwwwww..
.wwwwwwwwwwwwww.
.wwwwwrrwwrrwww.
.wwwwrrrrrrrrww.
.wwwwwrrrrrrwww.
.wwwwwwrrrrwwww.
.wwwwwwwrrwwwww.
...dddddddddd...
''',
}
LEAD_LEGS = {
    'stand': '''
....pppppppp....
....pppppppp....
....ppp..ppp....
....ppp..ppp....
....ppp..ppp....
....ppp..ppp....
....ppp..ppp....
....ppp..ppp....
...bbbb..bbbb...
''',
    'walk': '''
....pppppppp....
....pppppppp....
...ppp...ppp....
...ppp....ppp...
..ppp.....ppp...
..ppp......ppp..
..ppp......ppp..
..ppp......ppp..
.bbbb......bbbb.
''',
}
LEAD_PAL = {'h': (44, 34, 54), 's': (250, 214, 186), 'w': (250, 230, 168), 'd': (214, 184, 118), 'e': (86, 96, 176),
            'p': (62, 66, 112), 'b': (236, 236, 244), 'g': (150, 230, 255), 'r': (240, 80, 120)}

# 你（女生）：过肩长发 + 斜刘海遮住半边眉眼（“眼神逃避”）+ 一缕紫色挑染 + 酒红长大衣 + 短靴 + 永远亮着的手机。
YOU_HEAD = '''
.....hhhhhh.....
...hhhhhhhhhh...
..hhhhhhhhhhhh..
.hhhhhhhhhhhhhh.
.hhvhhhhhhhhhhh.
.hhvhhhhhhhhhhh.
.hhhvhhhhhssshh.
.hhhvhhsssssssh.
.hhsssssssssssh.
.hhsssssssssssh.
.hhsssssssssshh.
.hhhssssssssshh.
.hhh.sssssss.hh.
'''
YOU_TORSO = {
    'idle': '''
.hh...ssss...hh.
.hhcccciiiccchh.
.hhcccciicccchh.
.hccccciiccccch.
.ccdccciicccdcc.
.ccdccciicccdcc.
.ccdccciicccdcc.
.ccdccciicccdcc.
.ssdccciicccdss.
..cccccccccccc..
..cccccccccccc..
..ccccc..ccccc..
...cccc..cccc...
''',
    'phone': '''
.hh...ssss...hh.
.hhcccciiiccchh.
.hhcccciicccchh.
.hccccciiccccch.
.ccdccciicccdcc.
.ccdccciiccsgg..
.ccdccciiccsgg..
.ccdccciicccccc.
.ssdccciicccccc.
..cccccccccccc..
..cccccccccccc..
..ccccc..ccccc..
...cccc..cccc...
''',
}
YOU_LEGS = {
    'stand': '''
....ll....ll....
....ll....ll....
....bb....bb....
...bbb...bbb....
''',
    'walk': '''
...ll......ll...
..ll........ll..
..bb........bb..
.bbb.......bbb..
''',
}
YOU_PAL = {'h': (36, 26, 44), 'v': (150, 92, 190), 's': (248, 214, 194), 'c': (150, 48, 88), 'd': (108, 30, 64),
           'i': (30, 26, 40), 'l': (40, 34, 54), 'b': (22, 18, 30), 'g': (150, 236, 255)}

# 贯穿配角：戴睡帽的弯月（“窗挡住月色”）。全片旁观、吐槽，最后自己摘帽落下、换太阳上班。
MOON_ART = '''
...........oo.
....nnnnnnnoo.
..nnnnnnnnn...
.nnnnnnnnn....
.bbbbbbbb.....
.mmmmmmm......
mmmmmmmm......
mmmmmmm.......
mmmmmmm.......
mmmmmmm.......
mmmmmmm.......
mmmmmmmm......
.mmmmmmmm.....
.mmmmmmmmm....
..mmmmmmmmmm..
....mmmmmmmm..
'''
MOON_PAL = {'m': (255, 230, 150), 'n': (120, 128, 220), 'b': (245, 245, 255), 'o': (245, 245, 255)}

INK_C = (34, 24, 44)
WHITE_C = (255, 255, 255)
PINK_C = (240, 70, 110)
BLUSH_C = (255, 140, 160)
TEAR_C = (120, 200, 255)

# 表情：在精灵坐标里点像素（未放大，含 pixmap 的 1 像素描边偏移在 _face_px 里加）
LEAD_FACES = {
    'neutral': [(5, 8), (5, 9), (10, 8), (10, 9), (7, 11), (8, 11)],
    'happy': [(4, 9), (5, 8), (6, 9), (9, 9), (10, 8), (11, 9), (6, 11), (7, 12), (8, 12), (9, 11)],
    'heart': [(4, 8, PINK_C), (6, 8, PINK_C), (4, 9, PINK_C), (5, 9, PINK_C), (6, 9, PINK_C), (5, 10, PINK_C),
              (9, 8, PINK_C), (11, 8, PINK_C), (9, 9, PINK_C), (10, 9, PINK_C), (11, 9, PINK_C), (10, 10, PINK_C),
              (7, 11), (8, 11), (7, 12, (230, 70, 90)), (8, 12, (230, 70, 90))],
    'shock': [(5, 8), (5, 9), (10, 8), (10, 9), (4, 7), (11, 7), (7, 11), (8, 11), (7, 12), (8, 12)],
    'sad': [(5, 9), (10, 9), (4, 8), (11, 8), (6, 12), (7, 11), (8, 11), (9, 12)],
    'closed': [(4, 9), (5, 9), (10, 9), (11, 9), (7, 11), (8, 11)],
    'blush': [(5, 8), (5, 9), (10, 8), (10, 9), (3, 10, BLUSH_C), (4, 10, BLUSH_C), (11, 10, BLUSH_C), (12, 10, BLUSH_C),
              (6, 12), (7, 11), (8, 12), (9, 11)],
    'cry': [(4, 9), (5, 9), (10, 9), (11, 9), (5, 10, TEAR_C), (5, 11, TEAR_C), (10, 10, TEAR_C), (10, 11, TEAR_C),
            (6, 12), (7, 11), (8, 11), (9, 12)],
    'awk': [(4, 8), (5, 9), (4, 10), (11, 8), (10, 9), (11, 10), (3, 10, BLUSH_C), (12, 10, BLUSH_C), (6, 12), (7, 11), (8, 12), (9, 11)],
    'calm': [(4, 9), (5, 9), (10, 9), (11, 9), (6, 11), (7, 12), (8, 12), (9, 11), (3, 10, BLUSH_C), (12, 10, BLUSH_C)],
}
LIP_C = (214, 80, 110)
YOU_FACES = {
    'smile': [(4, 8), (5, 8), (5, 9), (10, 8), (11, 8), (10, 9), (6, 11, LIP_C), (7, 12, LIP_C), (8, 12, LIP_C), (9, 11, LIP_C)],
    'side': [(4, 8), (4, 9), (5, 9, WHITE_C), (9, 9), (10, 9, WHITE_C), (11, 8), (7, 12, LIP_C), (8, 12, LIP_C), (12, 6, TEAR_C), (12, 7, TEAR_C)],
    'wink': [(4, 9), (5, 9), (6, 9), (10, 8), (11, 8), (10, 9), (7, 12, LIP_C), (8, 12, LIP_C), (9, 11, LIP_C), (11, 10, BLUSH_C), (12, 10, BLUSH_C)],
    'bored': [(4, 8), (5, 8), (6, 8), (5, 9), (9, 8), (10, 8), (11, 8), (10, 9), (7, 12, LIP_C), (8, 12, LIP_C)],
    'awk': [(4, 8), (5, 9), (10, 9), (11, 8), (6, 12, LIP_C), (7, 11, LIP_C), (8, 12, LIP_C), (9, 11, LIP_C), (3, 10, BLUSH_C), (4, 10, BLUSH_C), (11, 10, BLUSH_C), (12, 10, BLUSH_C), (13, 7, TEAR_C), (13, 8, TEAR_C)],
}
MOON_FACES = {
    'sleep': [(3, 8), (4, 8), (5, 8), (5, 11)],
    'happy': [(3, 8), (4, 7), (5, 8), (4, 11), (5, 12), (6, 11), (2, 9, BLUSH_C)],
    'shock': [(4, 7), (5, 7), (4, 8), (5, 8), (5, 11), (5, 12), (6, 11), (6, 12)],
    'side': [(3, 7), (4, 7), (5, 7), (5, 8), (4, 12), (5, 12), (6, 12)],
    'sad': [(4, 8), (3, 7), (4, 12), (5, 11), (6, 12), (5, 9, TEAR_C), (5, 10, TEAR_C)],
    'smirk': [(4, 7), (4, 8), (3, 12), (4, 12), (5, 12), (6, 11)],
    'blush': [(3, 8), (4, 7), (5, 8), (5, 11), (2, 9, BLUSH_C), (3, 9, BLUSH_C), (6, 9, BLUSH_C)],
    'yawn': [(3, 8), (4, 8), (5, 8), (4, 10), (5, 10), (4, 11), (5, 11), (4, 12), (5, 12)],
}


def _with_face(spr, pts, dy=0):
    spr = spr.copy()
    px = spr.load()
    for p in pts:
        x, y = p[0] + 1, p[1] + 1 + dy
        c = p[2] if len(p) > 2 else INK_C
        if 0 <= x < spr.width and 0 <= y < spr.height:
            px[x, y] = (*c, 255)
    return spr


@lru_cache(maxsize=256)
def lead_spr(pose='idle', legs='stand', expr='neutral', pal_key=None):
    pal = dict(LEAD_PAL)
    if pal_key == 'fade':
        pal = {k: lerpc(v, (120, 130, 140), 0.55) for k, v in pal.items()}
    art = LEAD_HEAD.strip('\n') + '\n' + LEAD_TORSO[pose].strip('\n') + '\n' + LEAD_LEGS[legs].strip('\n')
    return _with_face(pixmap(art, pal), LEAD_FACES[expr])


@lru_cache(maxsize=256)
def you_spr(pose='idle', legs='stand', expr='smile', pal_key=None):
    pal = dict(YOU_PAL)
    if pal_key == 'fade':
        pal = {k: lerpc(v, (120, 130, 140), 0.55) for k, v in pal.items()}
    art = YOU_HEAD.strip('\n') + '\n' + YOU_TORSO[pose].strip('\n') + '\n' + YOU_LEGS[legs].strip('\n')
    return _with_face(pixmap(art, pal), YOU_FACES[expr])


@lru_cache(maxsize=64)
def moon_spr(expr='happy', col=(255, 230, 150), cap=True):
    pal = dict(MOON_PAL, m=col)
    art = MOON_ART
    if not cap:
        art = '\n'.join(r if i >= 5 else r.replace('n', '.').replace('o', '.').replace('b', '.') for i, r in enumerate(MOON_ART.strip('\n').split('\n')))
        art = art.replace('.mmmmmmm......', '.mmmmmmm......', 1)
    return _with_face(pixmap(art, pal), MOON_FACES[expr])


def lead(img, x, y, pose='idle', expr='neutral', face=1, scale=2, walk=False, t=0.0, bob=False, fade=False):
    legs = 'walk' if walk and int(t * 6) % 2 else 'stand'
    dy = -1 if (bob and int(t * 4) % 2) else 0
    put(img, lead_spr(pose, legs, expr, 'fade' if fade else None), x, y + dy, scale, face)


def you(img, x, y, pose='idle', expr='smile', face=-1, scale=2, walk=False, t=0.0, fade=False):
    legs = 'walk' if walk and int(t * 6) % 2 else 'stand'
    put(img, you_spr(pose, legs, expr, 'fade' if fade else None), x, y, scale, face)


def moonc(img, cx, cy, expr='happy', scale=2, v=False, cap=True, face=1):
    col = P(v)['moon']
    put(img, moon_spr(expr, col, cap), cx, cy, scale, face, anchor='center')


def lead_head(img, x, y, expr, scale=2):
    spr = lead_spr('idle', 'stand', expr).crop((0, 0, 18, 15))
    put(img, spr, x, y, scale, 1, anchor='topleft')


def you_head(img, x, y, expr, scale=2):
    spr = you_spr('idle', 'stand', expr).crop((0, 0, 18, 15))
    put(img, spr, x, y, scale, 1, anchor='topleft')


CAST = {'me': '我（男生）', 'you': '你（女生）', 'moon': '睡帽弯月'}


def CAST_SHEET(img, t):
    d = ImageDraw.Draw(img)
    img.paste(Image.fromarray(dither_grad(H, W, (30, 28, 70), (62, 56, 120))), (0, 0))
    draw_text(img, 6, 3, '《晚安》角色设定', (255, 230, 150), outline=INK_C)
    # 我
    draw_text(img, 6, 18, '我（他）', WHITE, outline=INK_C)
    ph = int(t * 2) % 2
    lead(img, 22, 92, 'idle', 'neutral')
    lead(img, 56, 92, 'phone', 'blush')
    lead(img, 90, 92, 'heart' if ph else 'wave', 'heart' if ph else 'happy', walk=True, t=t)
    for i, e in enumerate(['neutral', 'happy', 'heart', 'shock', 'sad', 'closed', 'blush', 'cry', 'awk', 'calm']):
        lead_head(img, 112 + (i % 5) * 41, 20 + (i // 5) * 36, e, 2)
    # 你
    draw_text(img, 6, 98, '你（她）', WHITE, outline=INK_C)
    you(img, 22, 176, 'idle', 'smile', 1)
    you(img, 56, 176, 'phone', 'bored', 1, walk=True, t=t)
    for i, e in enumerate(['smile', 'side', 'wink', 'bored', 'awk']):
        you_head(img, 80 + (i % 3) * 38, 102 + (i // 3) * 38, e, 2)
    # 月亮
    draw_text(img, 196, 98, '睡帽弯月', (255, 230, 150), outline=INK_C)
    for i, e in enumerate(['sleep', 'happy', 'side', 'shock', 'sad', 'yawn']):
        moonc(img, 214 + (i % 3) * 38, 127 + (i // 3) * 35, e, 2)
    # 三套配色：夜 / 褪色（第二遍副歌）/ 天亮（最后一遍）
    draw_text(img, 140, 3, '配色', WHITE, outline=INK_C)
    for j, (k, lab) in enumerate([(False, '夜'), (True, '褪色'), ('dawn', '天亮')]):
        p = PAL_SETS[k]
        palette_strip(img, 170 + j * 50, 6, [p['sky0'], p['sky1'], p['moon'], p['you']], 6)


# ======================= ③ 场景工具 =======================
CREAM = (255, 230, 150)
AMB = (214, 130, 214)        # 暧昧区：两人颜色混出来的粉紫
WINE = (150, 48, 88)
CYANC = (130, 220, 240)


def fill_grad(img, c0, c1, y0=0, y1=H, x0=0, w=W):
    img.paste(Image.fromarray(dither_grad(y1 - y0, w, c0, c1)), (x0, y0))


def stars(img, t, n=40, x0=0, y0=0, w=W, h=100, k=1.0, seed=0):
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = x0 + int(hsh(seed, i, 1) * w); y = y0 + int(hsh(seed, i, 2) * h)
        tw = 0.5 + 0.5 * math.sin(t * 1.6 + hsh(seed, i, 3) * 6.28)
        if tw * k > 0.25:
            c = lerpc((110, 110, 160), (255, 250, 220), min(1, tw * k))
            d.point((x, y), fill=c)
            if hsh(seed, i, 4) > 0.86 and tw > 0.75:
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    d.point((x + ox, y + oy), fill=lerpc(c, (60, 60, 110), 0.4))


def skyline(img, v, ground=130, seed=0, col=None, lit=0.22, x0=0, w=W, hmin=30, hmax=90):
    p = P(v); d = ImageDraw.Draw(img)
    col = col or lerpc(p['ink'], p['sky1'], 0.28)
    x, i = x0 - 6, 0
    while x < x0 + w:
        bw = 16 + int(hsh(seed, i, 1) * 24)
        bh = hmin + int(hsh(seed, i, 2) * (hmax - hmin))
        R(d, x, ground - bh, bw, bh + 4, col)
        R(d, x, ground - bh, bw, 1, lerpc(col, p['sky1'], 0.35))
        for wy in range(ground - bh + 4, ground - 3, 6):
            for wx in range(x + 3, x + bw - 3, 5):
                if hsh(seed, i, wx - x, wy) < lit:
                    R(d, wx, wy, 2, 3, p['glow'])
        x += bw + 2; i += 1


def night(img, t, v, y1=H, stars_k=1.0):
    p = P(v)
    fill_grad(img, p['sky0'], p['sky1'], 0, y1)
    stars(img, t, 46, h=min(y1, 110), k=stars_k * (0.5 if v == 'dawn' else 1.0))


def fade_img(img, k, x0=0, x1=W):
    """褪色：x0..x1 区域往灰色靠"""
    if k <= 0:
        return
    a = np.asarray(img).astype(float)
    g = a.mean(2, keepdims=True) * 0.9 + 12
    a[:, x0:x1] = a[:, x0:x1] * (1 - k) + g[:, x0:x1] * k
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0))


def tint_img(img, col, k):
    a = np.asarray(img).astype(float)
    a = a * (1 - k) + np.array(col, float) * k
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0))


def glow(img, cx, cy, r, col, k=0.35):
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    m = np.clip(1 - dd, 0, 1) * k
    m = np.where(np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < m * 2.2, m, m * 0.4)
    a = a * (1 - m[..., None]) + np.array(col, float) * m[..., None]
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0))


def text_c(img, cx, y, s, col, outline=INK_C):
    draw_text(img, cx - text_w(s) // 2, y, s, col, outline=outline)


def rel_bar(img, cx, y, pos, v=False, w=130, alpha=1.0, label=True):
    """关系进度条：朋友 ——●—— 恋人，中间的暧昧区"""
    if alpha <= 0:
        return
    base = img.copy() if alpha < 1 else None
    d = ImageDraw.Draw(img)
    x0, x1 = cx - w // 2, cx + w // 2
    lw = text_w('朋友')
    R(d, x0 - lw - 8, y - 3, w + 2 * lw + 16, 15, (24, 20, 44))
    d.rectangle([x0 - lw - 8, y - 3, x1 + lw + 8, y + 11], outline=(250, 248, 240))
    draw_text(img, x0 - lw - 5, y - 1, '朋友', (190, 220, 255))
    draw_text(img, x1 + 4, y - 1, '恋人', (255, 160, 190))
    R(d, x0, y + 3, w, 3, (90, 86, 120))
    a0, a1 = x0 + int(w * 0.36), x0 + int(w * 0.64)
    amb = AMB if v is not True else (150, 160, 190)
    R(d, a0, y + 2, a1 - a0, 5, amb)
    kx = x0 + int(w * clamp(pos))
    heart(img, kx, y + 3, 1, (255, 90, 140) if v is not True else (180, 200, 220))
    if label:
        s = '暧昧区'
        draw_text(img, (a0 + a1) // 2 - text_w(s) // 2, y + 12, s, amb, outline=INK_C)
    if base is not None:
        img.paste(Image.blend(base, img, alpha))


def lead_bed(img, x, bed_y, expr='neutral', pose='phone', blanket=(120, 92, 150), fade=False, scr=None):
    """坐在床上、被子盖到腰：x 为身体中线，bed_y 为被子上沿"""
    spr = lead_spr(pose, 'stand', expr, 'fade' if fade else None).crop((0, 0, 18, 24))
    big = spr.resize((36, 48), Image.NEAREST)
    img.paste(big, (int(x - 18), int(bed_y - 44)), big)
    d = ImageDraw.Draw(img)
    R(d, x - 30, bed_y, 300 - (x - 30), 14, INK_C)
    R(d, x - 29, bed_y + 1, 300 - (x - 29), 12, blanket)
    R(d, x - 29, bed_y + 1, 300 - (x - 29), 2, light(blanket, 0.3))
    for k in range(x - 10, 300, 22):
        R(d, k, bed_y + 4, 1, 8, shade(blanket, 0.25))
    if scr and pose == 'phone':
        glow(img, x, bed_y - 6, 26, scr, 0.22)


def lead_sleep(img, x, y, expr='calm', blanket=(150, 110, 170)):
    """躺着睡：头侧枕在枕头上，被子鼓成一团。x,y 为枕头左上角"""
    d = ImageDraw.Draw(img)
    R(d, x - 1, y - 1, 34, 14, INK_C); R(d, x, y, 32, 12, (250, 250, 255))
    head = lead_spr('idle', 'stand', expr).crop((0, 0, 18, 15)).transpose(Image.ROTATE_270)
    head = head.resize((head.width * 2, head.height * 2), Image.NEAREST)
    img.paste(head, (x + 2, y - 20), head)
    R(d, x + 30, y - 6, 300 - (x + 30), 22, INK_C)
    R(d, x + 31, y - 5, 300 - (x + 31), 20, blanket)
    d.ellipse([x + 40, y - 14, x + 110, y + 6], fill=blanket, outline=INK_C)
    R(d, x + 41, y - 4, 69, 8, blanket)
    R(d, x + 31, y - 5, 300 - (x + 31), 2, light(blanket, 0.3))


def phone_small(img, x, y, v, lit=True, buzz=False, t=0.0):
    d = ImageDraw.Draw(img)
    jx = int(math.sin(t * 50)) if buzz else 0
    R(d, x + jx - 1, y - 1, 10, 15, INK_C)
    R(d, x + jx, y, 8, 13, P(v)['scr'] if lit else (40, 40, 60))
    if lit:
        R(d, x + jx + 1, y + 2, 6, 1, (255, 255, 255)); R(d, x + jx + 1, y + 5, 4, 1, (255, 255, 255))


def bedroom(img, t, v, curtain=0.0, moon_expr='side', lamp_on=False, bed=True, win_x=26, moon_y=None, moon_cap=True, dim=0.0, stand=True):
    """我的卧室：左边窗（月亮在窗里），右边床"""
    p = P(v); d = ImageDraw.Draw(img)
    fill_grad(img, p['wall'], lerpc(p['wall'], p['ink'], 0.6))
    # 墙纸竖纹
    for x in range(0, W, 16):
        R(d, x, 0, 1, 132, lerpc(p['wall'], p['wall2'], 0.5))
    wx, wy, ww, wh = win_x, 12, 104, 76
    win = Image.new('RGB', (ww, wh))
    win.paste(Image.fromarray(dither_grad(wh, ww, p['sky0'], p['sky1'])), (0, 0))
    stars(win, t, 16, w=ww, h=wh - 20, seed=3, k=0.5 if v == 'dawn' else 1)
    skyline(win, v, wh, seed=5, w=ww, hmin=10, hmax=34, lit=0.25)
    my = moon_y if moon_y is not None else 26
    moonc(win, 70, my, moon_expr, 2, v, moon_cap)
    img.paste(win, (wx, wy))
    fr = (70, 56, 90) if v is not True else (60, 70, 80)
    d.rectangle([wx - 3, wy - 3, wx + ww + 2, wy + wh + 2], outline=fr, width=3)
    R(d, wx + ww // 2 - 1, wy, 2, wh, fr); R(d, wx, wy + wh // 2 - 1, ww, 2, fr)
    R(d, wx - 6, wy + wh + 3, ww + 12, 4, lerpc(fr, (255, 255, 255), 0.15))
    # 窗帘
    cw = int((ww // 2 + 8) * clamp(curtain))
    ccol = (96, 70, 130) if v is not True else (70, 86, 100)
    R(d, wx - 10, wy - 8, ww + 20, 3, (50, 40, 60))
    for side in (0, 1):
        x0 = wx - 8 if side == 0 else wx + ww + 8 - cw - 10
        wcur = cw + 10
        R(d, x0, wy - 5, wcur, wh + 16, ccol)
        for k in range(x0 + 3, x0 + wcur - 1, 5):
            R(d, k, wy - 5, 1, wh + 16, lerpc(ccol, (20, 16, 30), 0.35))
    # 地板
    R(d, 0, 132, W, H - 132, lerpc(p['wall'], (60, 40, 40), 0.5))
    R(d, 0, 132, W, 1, lerpc(p['wall'], (255, 255, 255), 0.2))
    if bed:
        bc = (120, 92, 150) if v is not True else (90, 104, 116)
        R(d, 168, 104, 146, 28, (70, 50, 70)); R(d, 168, 98, 6, 34, (70, 50, 70)); R(d, 308, 108, 6, 24, (70, 50, 70))
        R(d, 174, 100, 134, 10, (236, 232, 244)); R(d, 176, 92, 26, 10, (250, 250, 255))
        R(d, 174, 108, 134, 6, bc)
    # 床头柜 + 闹钟
    if stand:
        R(d, 140, 112, 22, 20, (90, 64, 80)); R(d, 140, 112, 22, 2, (120, 90, 100))
        R(d, 141, 100, 20, 13, INK_C); R(d, 142, 101, 18, 11, (30, 30, 40))
        draw_text(img, 143, 100, '0558' if v == 'dawn' else '0047', (255, 90, 90) if v is not True else (150, 210, 220))
    if lamp_on:
        R(d, 147, 88, 8, 6, (255, 220, 150)); R(d, 150, 94, 2, 8, (90, 80, 90))
        glow(img, 151, 92, 70, (255, 214, 140), 0.32)
    if dim:
        tint_img(img, (8, 6, 20), dim)


def street(img, t, v, ground=130, lamp_x=None, sign=None, seed=11):
    p = P(v); d = ImageDraw.Draw(img)
    night(img, t, v, ground)
    skyline(img, v, ground, seed=seed, hmin=30, hmax=80)
    R(d, 0, ground, W, H - ground, lerpc(p['ink'], p['wall'], 0.4))
    R(d, 0, ground, W, 2, lerpc(p['wall2'], (255, 255, 255), 0.15))
    for x in range(0, W, 24):
        R(d, x, ground + 10, 12, 1, lerpc(p['wall'], (255, 255, 255), 0.1))
    if lamp_x is not None:
        lamp(img, lamp_x, ground, 'happy', True, 78)


def neon(img, x, y, s, col, on=True):
    d = ImageDraw.Draw(img)
    w = text_w(s, 2) + 10
    R(d, x - 2, y - 2, w + 4, 30, (20, 14, 30))
    d.rectangle([x - 2, y - 2, x + w + 1, y + 27], outline=col if on else (60, 50, 70), width=1)
    draw_text(img, x + 5, y + 2, s, col if on else lerpc(col, (20, 14, 30), 0.7), scale=2, outline=(40, 20, 50) if on else None)
    if on:
        glow(img, x + w // 2, y + 12, 40, col, 0.18)


def thought(img, cx, cy, rx, ry, col=(250, 248, 240)):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=INK_C)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)


def heart_glow(img, cx, cy, k, col=(255, 110, 150), t=0.0):
    glow(img, cx, cy, 10 + 4 * k, col, 0.25)
    heart(img, cx, cy, k, col)


def photo(img, x, y, kind, t):
    """回忆相片（棕色）"""
    d = ImageDraw.Draw(img)
    R(d, x - 1, y - 1, 38, 34, INK_C); R(d, x, y, 36, 32, (246, 238, 220))
    R(d, x + 3, y + 3, 30, 22, (150, 116, 82))
    S = (230, 200, 160); Kd = (90, 64, 44)
    if kind == 'rope':
        R(d, x + 5, y + 14, 26, 1, S)
        heart(img, x + 18, y + 13, 1, (250, 214, 170))
        R(d, x + 5, y + 10, 3, 8, Kd); R(d, x + 28, y + 10, 3, 8, Kd)
    elif kind == 'bridge':
        R(d, x + 3, y + 18, 11, 3, Kd); R(d, x + 22, y + 18, 11, 3, Kd)
        R(d, x + 9, y + 11, 2, 7, S); R(d, x + 26, y + 11, 2, 7, S)
    elif kind == 'chat':
        R(d, x + 5, y + 6, 14, 5, S); R(d, x + 15, y + 13, 14, 5, (230, 170, 150)); R(d, x + 5, y + 20, 10, 3, S)
    elif kind == 'moon':
        disc(d, x + 18, y + 13, 6, S); disc(d, x + 21, y + 11, 5, (150, 116, 82))
    draw_text(img, x + 3, y + 25, '', Kd)


def phone_ui(img, x, y, w, h, v, msgs, t, title='她', typing=None, scroll=0, input_txt=None, cursor_on=True):
    """大手机聊天界面。msgs: [(side 'l'/'r', text)]，从下往上排"""
    p = P(v); d = ImageDraw.Draw(img)
    R(d, x - 2, y - 2, w + 4, h + 4, INK_C)
    R(d, x, y, w, h, (44, 42, 60))
    sx, sy, sw, sh = x + 3, y + 8, w - 6, h - 14
    scr = Image.new('RGB', (sw, sh), (30, 28, 50) if v is not True else (30, 40, 48))
    ds = ImageDraw.Draw(scr)
    bottom = sh - (20 if input_txt is not None else 4)
    yy = bottom + scroll
    for side, s in reversed(msgs):
        bw = text_w(s) + 8
        yy -= 17
        if yy < 15:
            break
        if side == 'l':
            bx, bg, fg = 4, (p['you'] if v is not True else (100, 80, 100)), (255, 255, 255)
        else:
            bx, bg, fg = sw - bw - 4, (CREAM if v is not True else (200, 210, 214)), INK_C
        ds.rectangle([bx, yy, bx + bw - 1, yy + 14], fill=bg)
        draw_text(scr, bx + 4, yy + 1, s, fg)
    ds = ImageDraw.Draw(scr)
    R(ds, 0, 0, sw, 14, (60, 56, 96) if v is not True else (50, 66, 76))
    draw_text(scr, sw // 2 - text_w(title) // 2, 1, title, (255, 255, 255))
    if typing:
        R(ds, 0, 14, sw, 13, (40, 36, 66))
        draw_text(scr, 3, 14, typing, (190, 190, 220))
    if input_txt is not None:
        R(ds, 2, sh - 18, sw - 4, 16, (60, 58, 84))
        s = input_txt + ('▌' if cursor_on else '')
        draw_text(scr, 5, sh - 16, s, (255, 255, 255))
    img.paste(scr, (sx, sy))
    R(d, x + w // 2 - 6, y + 3, 12, 2, (90, 90, 110))


def cal_page(img, x, y, label, col=(240, 80, 110)):
    d = ImageDraw.Draw(img)
    R(d, x - 1, y - 1, 46, 40, INK_C); R(d, x, y, 44, 38, (250, 248, 240)); R(d, x, y, 44, 10, col)
    for i in (9, 33):
        R(d, x + i, y - 4, 2, 6, (150, 150, 170))
    draw_text(img, x + 22 - text_w(label) // 2, y + 16, label, INK_C)


def my_clapper(img, x, y, n, snap):
    d = ImageDraw.Draw(img)
    R(d, x, y + 8, 64, 30, INK_C); R(d, x + 1, y + 9, 62, 28, (40, 40, 50))
    draw_text(img, x + 4, y + 10, '烂桥段', WHITE)
    draw_text(img, x + 4, y + 23, f'第{n}次', (255, 140, 140))
    lift = 0 if snap else 6
    for i in range(8):
        c = WHITE if i % 2 else INK_C
        x0 = x + i * 8
        d.polygon([(x0, y + 8 - lift * (i / 8)), (x0 + 8, y + 8 - lift * ((i + 1) / 8)), (x0 + 8, y + 2 - lift * ((i + 1) / 8)), (x0, y + 2 - lift * (i / 8))], fill=c)


def big_clock(img, cx, cy, r, ang_m, ang_h):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=INK_C)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 246, 232))
    for i in range(12):
        a = i / 12 * 6.283
        d.point((cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2)), fill=INK_C)
    d.line([(cx, cy), (cx + math.sin(ang_h) * (r - 7), cy - math.cos(ang_h) * (r - 7))], fill=INK_C, width=2)
    d.line([(cx, cy), (cx + math.sin(ang_m) * (r - 3), cy - math.cos(ang_m) * (r - 3))], fill=(230, 60, 80), width=1)


def zzz(img, x, y, t):
    for i in range(3):
        ph = (t * 0.5 + i / 3) % 1
        draw_text(img, x + int(ph * 14), y - int(ph * 22), 'z' if i % 2 else 'Z', (220, 220, 255), outline=INK_C)


# ======================= ④ 镜头 =======================
def s_title(img, t, lt, v):
    """前奏：两栋楼各亮一扇窗，弯月在中间打哈欠"""
    p = P(v); d = ImageDraw.Draw(img)
    night(img, t, v)
    skyline(img, v, 160, seed=21, hmin=20, hmax=60, lit=0.12)
    for bx, bw, bh, side in ((14, 70, 120, 1), (236, 72, 110, -1)):
        col = lerpc(p['ink'], p['sky1'], 0.18)
        R(d, bx, H - bh, bw, bh, col)
        for wy in range(H - bh + 8, H, 12):
            for wx in range(bx + 6, bx + bw - 8, 12):
                R(d, wx, wy, 6, 7, lerpc(col, (0, 0, 0), 0.3))
        wx, wy = (bx + 30, H - bh + 32)
        R(d, wx - 1, wy - 1, 18, 20, INK_C)
        R(d, wx, wy, 16, 18, (255, 214, 140) if side > 0 else (255, 170, 190))
        # 窗里的人影 + 手机光
        R(d, wx + 5, wy + 6, 6, 12, (60, 40, 60)); R(d, wx + 6, wy + 3, 4, 4, (60, 40, 60))
        R(d, wx + (10 if side > 0 else 3), wy + 9, 3, 4, P(v)['scr'])
        glow(img, wx + 8, wy + 9, 30, (255, 220, 160) if side > 0 else (255, 160, 200), 0.18)
    my = 26 + int(math.sin(lt * 0.8) * 2)
    moonc(img, 160, my, 'yawn' if (lt % 4) < 1.4 else 'sleep', 2, v)
    if (lt % 4) >= 1.4:
        zzz(img, 172, my - 6, t)


def s_intro(img, t, lt, v):
    """左右分屏：她在她的房间打字，我在床上等；关系进度条第一次出现"""
    p = P(v); d = ImageDraw.Draw(img)
    # 左：她的房间
    left = Image.new('RGB', (W, H))
    fill_grad(left, lerpc(p['wall'], WINE, 0.25), lerpc(p['ink'], WINE, 0.15))
    dl = ImageDraw.Draw(left)
    R(dl, 18, 18, 60, 50, INK_C)
    sub = Image.fromarray(dither_grad(48, 58, p['sky0'], p['sky1']))
    stars(sub, t, 8, w=58, h=30, seed=7)
    skyline(sub, v, 48, seed=8, w=58, hmin=8, hmax=22)
    left.paste(sub, (19, 19))
    R(dl, 0, 132, 160, 48, lerpc(p['ink'], WINE, 0.25))
    R(dl, 96, 106, 50, 26, (110, 50, 80)); R(dl, 96, 98, 50, 10, (130, 60, 96)); R(dl, 92, 100, 6, 32, (90, 40, 66))
    you(left, 120, 132, 'phone', 'wink' if 3.0 < lt < 5.0 else 'smile', -1, 2, t=t)
    glow(left, 108, 98, 26, p['scr'], 0.22)
    img.paste(left.crop((0, 0, 158, H)), (0, 0))
    # 右：我的房间
    right = Image.new('RGB', (W, H))
    bedroom(right, t, v, 0.0, 'smirk', win_x=180, stand=False)
    lead_bed(right, 240, 106, 'blush' if lt > 1.2 else 'neutral', 'phone', scr=p['scr'])
    img.paste(right.crop((162, 0, 320, H)), (162, 0))
    R(d, 158, 0, 4, H, INK_C)
    # 正在输入…交替
    if 0.4 < lt < 3.0 or 6.0 < lt < 7.6:
        say(img, 60, 50, '对方正在输入…', tail='r')
    if 3.2 < lt < 5.8 or 7.8 < lt:
        say(img, 196, 34, '对方正在输入…', tail='l')
    if lt > 4.4:
        k = seg(lt, 4.4, 5.0)
        pos = lerp(0.1, 0.5, ease(seg(lt, 4.6, 6.4)))
        rel_bar(img, 160, 6, pos, v, 120, k)


def s_window(img, t, lt, v):
    """窗挡住月色贪恋的交集"""
    cur = ease(seg(lt, 0.4, 1.8)) * 0.78
    mexpr = 'happy' if lt < 1.0 else 'shock'
    bedroom(img, t, v, cur, mexpr)
    lead(img, 140, 132, 'phone' if lt > 2.0 else 'idle', 'blush' if lt > 2.0 else 'neutral', -1, 2)
    if lt > 1.9:
        # 月亮从窗帘缝里挤出半张脸
        moonc(img, 78 + int(math.sin(lt * 3) * 1), 40, 'side', 2, v)
    # 文氏图：我的夜 ∩ 你的夜
    k = ease(seg(lt, 0.8, 2.6))
    cx, cy, r = 236, 50, 22
    sep = int(lerp(40, 16, k))
    yy, xx = np.mgrid[0:H, 0:W]
    m1 = (xx - (cx - sep)) ** 2 + (yy - cy) ** 2 < r * r
    m2 = (xx - (cx + sep)) ** 2 + (yy - cy) ** 2 < r * r
    a = np.asarray(img).astype(float)
    for m, c in ((m1 & ~m2, CREAM), (m2 & ~m1, (190, 70, 120)), (m1 & m2, AMB)):
        a[m] = a[m] * 0.35 + np.array(c, float) * 0.65
    e1 = m1 ^ np.roll(m1, 1, 0) | m1 ^ np.roll(m1, 1, 1)
    e2 = m2 ^ np.roll(m2, 1, 0) | m2 ^ np.roll(m2, 1, 1)
    a[e1 | e2] = (250, 248, 240)
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0))
    draw_text(img, cx - sep - 22, cy - 6, '我的夜', INK_C)
    draw_text(img, cx + sep + 2, cy - 6, '你的夜', (255, 255, 255), outline=INK_C)
    if lt > 2.6:
        sfx(img, cx, cy + 32, '交集', t, t - lt + 2.6, 99, 'pink', 1)


def s_bubbles(img, t, lt, v):
    """在浮语虚词中交映：气泡从手机里飘起来，窗玻璃上映出倒影"""
    p = P(v)
    bedroom(img, t, v, 0.35, 'side')
    lead_bed(img, 200, 106, 'happy', 'phone', scr=p['scr'])
    words = [('l', '哈哈'), ('r', '嗯嗯'), ('l', '你呢'), ('r', '在干嘛'), ('l', '早点睡'), ('r', '嘿嘿'), ('l', '还没睡?'), ('r', '你先睡')]
    d = ImageDraw.Draw(img)
    for i, (side, s) in enumerate(words):
        born = i * 0.5
        ph = (lt - born) / 2.6
        if 0 <= ph <= 1:
            x = 200 + (-34 if side == 'l' else 22) + int(math.sin(ph * 6 + i) * 6)
            y = int(58 - ph * 54)
            bw = text_w(s) + 6
            bg = p['you'] if side == 'l' else CREAM
            fg = (255, 255, 255) if side == 'l' else INK_C
            R(d, x - 1, y - 1, bw + 2, 14, INK_C); R(d, x, y, bw, 12, bg)
            draw_text(img, x + 3, y, s, fg)
            # 窗上的倒影（淡、左右错开）
            if ph < 0.8:
                rx = 32 + (i % 4) * 22
                ry = 24 + (i % 2) * 22 + int(ph * 16)
                draw_text(img, rx, ry, s, lerpc(bg, p['sky1'], 0.72))


def s_longnight(img, t, lt, v):
    """忙碌的身影慢慢的长夜：左边她快进，右边我在等"""
    p = P(v); d = ImageDraw.Draw(img)
    left = Image.new('RGB', (W, H))
    street(left, t * 4, v, 130, seed=31)
    sp = (lt * 80) % 190 - 16
    for k in range(3, 0, -1):
        you(left, int(sp - k * 14), 130, 'phone', 'bored', 1, 2, walk=True, t=t * 2 + k, fade=True)
    you(left, int(sp), 130, 'phone', 'bored', 1, 2, walk=True, t=t * 2)
    for i in range(6):
        y = 70 + i * 9
        R(ImageDraw.Draw(left), int((sp - 40 - i * 7) % 160), y, 12, 1, (255, 255, 255))
    img.paste(left.crop((0, 0, 158, H)), (0, 0))
    right = Image.new('RGB', (W, H))
    bedroom(right, t, v, 0.4, 'yawn', win_x=180, stand=False)
    lead_bed(right, 214, 106, 'closed' if int(lt * 1.2) % 3 == 1 else 'neutral', 'phone', scr=p['scr'])
    big_clock(right, 250, 38, 16, lt * 0.15, 0.05 + lt * 0.012)
    img.paste(right.crop((162, 0, 320, H)), (162, 0))
    R(d, 158, 0, 4, H, INK_C)
    text_c(img, 79, 8, '忙碌中 ×4 倍速', (255, 230, 150))
    pct = 0.03 + seg(lt, 0, 4.5) * 0.01
    R(d, 172, 8, 70, 13, INK_C)
    R(d, 173, 9, int(68 * pct) + 1, 11, (255, 120, 160))
    draw_text(img, 174, 9, '长夜加载中…', (255, 255, 255))
    draw_text(img, 246, 9, f'{int(pct * 100)}%', (255, 230, 150), outline=INK_C)


def s_drop(img, t, lt, v):
    """去匆匆地留下感情：她匆匆跑过，掉下一颗心，我捡起来"""
    street(img, t, v, 130, lamp_x=150)
    d = ImageDraw.Draw(img)
    rx = lerp(330, -40, seg(lt, 0.2, 2.2))
    if lt < 2.3:
        you(img, int(rx), 130, 'idle', 'wink' if lt < 1.2 else 'smile', -1, 2, walk=True, t=t * 2)
        for i in range(5):
            R(d, int(rx + 22 + i * 3), 80 + i * 8, 14 + i * 2, 1, (255, 255, 255))
        if 0.6 < lt < 1.8:
            say(img, int(rx) - 30, 52, '先走啦~', tail='r')
    # 心掉落
    hx = 170
    if lt > 1.1:
        fall = seg(lt, 1.1, 1.6)
        hy = int(lerp(90, 122, ease(fall)))
        if lt > 1.6:
            hy = 122 - int(abs(math.sin((lt - 1.6) * 8)) * 6 * max(0, 1 - (lt - 1.6) * 1.5))
        mx = lerp(60, hx - 18, ease(seg(lt, 2.0, 3.0)))
        if lt < 3.1:
            heart_glow(img, hx, hy, 2, (255, 120, 160))
            lead(img, int(mx), 130, 'idle', 'shock' if lt < 2.0 else 'neutral', 1, 2, walk=2.0 < lt < 3.0, t=t)
        else:
            lead(img, int(mx), 130, 'heart', 'blush', 1, 2)
            glow(img, int(mx), 98, 24, (255, 120, 160), 0.2)
        if lt > 3.1:
            sfx(img, int(mx), 36, '获得：感情×1', t, t - lt + 3.1, 99, 'pink', 1)
    else:
        lead(img, 60, 130, 'idle', 'neutral', 1, 2)
    moonc(img, 290, 24, 'happy' if lt > 3 else 'shock', 2, v)
    if lt > 3.3:
        say(img, 232, 40, '哦~', tail='r')


def s_flustered(img, t, lt, v):
    """声色太慌张你眼神逃避"""
    street(img, t, v, 132, seed=41)
    on = not (int(t * 7) % 4 == 0 or (lt > 1.5 and int(t * 11) % 3 == 0))
    neon(img, 128, 8, '声色', (255, 110, 190) if v is not True else (150, 210, 230), on)
    dart = int(lt * 2.5) % 2
    lead(img, 116, 132, 'wave' if int(lt * 3) % 2 else 'idle', 'blush' if lt > 1.2 else 'shock', 1, 2)
    you(img, 204, 132, 'idle', 'side' if dart else 'awk', -1 if dart else 1, 2)
    # 视线箭头
    ax = 178 if dart else 230
    draw_text(img, ax, 54, '←' if dart else '→', (255, 230, 120), outline=INK_C)
    sweat(img, 220, 66, 1)
    # 头顶冒蒸汽
    for i, hx in enumerate((116, 204)):
        ph = (t * 1.2 + i * 0.5) % 1
        disc(ImageDraw.Draw(img), hx + int(math.sin(ph * 6) * 3), 58 - int(ph * 16), 2 + int(ph * 2), (240, 240, 250))
    if lt > 0.8:
        sys_msg(img, 160, 44, '目光闪躲中…', (180, 70, 130))


def s_charmed(img, t, lt, v):
    """却如此地令人着迷：催眠螺旋 + 着迷值"""
    yy, xx = np.mgrid[0:H, 0:W]
    ang = np.arctan2(yy - 84, xx - 160)
    rr = np.sqrt((xx - 160) ** 2 + (yy - 84) ** 2)
    sp = ((ang * 3 + rr * 0.12 - lt * 3.0) % 6.283) < 3.14
    c1, c2 = ((240, 140, 210), (150, 80, 180)) if v is not True else ((150, 190, 210), (80, 110, 140))
    if v == 'dawn':
        c1, c2 = (255, 170, 180), (200, 110, 170)
    a = np.where(sp[..., None], np.array(c1), np.array(c2)).astype(np.uint8)
    img.paste(Image.fromarray(a), (0, 0))
    by = int(abs(math.sin(lt * 3.4)) * 3)
    lead(img, 160, 134 - by, 'heart', 'heart', 1, 2)
    for i in range(6):
        aa = i / 6 * 6.283 + lt * 1.5
        heart(img, int(160 + math.cos(aa) * 42), int(82 + math.sin(aa) * 26), 1, (255, 80, 130))
    mv_ = 0.4 + ease(seg(lt, 0.2, 2.4)) * 0.59
    meter(img, 8, 10, '上头值', mv_, (255, 70, 130), 66, blink=lt > 2.4)
    rel_bar(img, 236, 8, lerp(0.5, 0.62, ease(seg(lt, 2.0, 3.2))), v, 70, label=False)
    moonc(img, 290, 70, 'blush', 2, v)
    if lt > 1.4:
        sfx(img, 268, 98, '起哄~', t, t - lt + 1.4, 99, 'yel', 1)


def s_fog(img, t, lt, v):
    """为何总留恋这种暧昧的迷离：起雾的路，两头的路牌，看不清的中间"""
    p = P(v)
    street(img, t, v, 132, seed=51)
    d = ImageDraw.Draw(img)
    # 路牌
    R(d, 159, 40, 3, 92, (90, 80, 100))
    d.polygon([(110, 44), (154, 44), (154, 56), (110, 56), (104, 50)], fill=(170, 200, 240), outline=INK_C)
    draw_text(img, 120, 44, '朋友', INK_C)
    d.polygon([(166, 44), (210, 44), (216, 50), (210, 56), (166, 56)], fill=(255, 160, 190), outline=INK_C)
    draw_text(img, 176, 44, '恋人', INK_C)
    sw = int(math.sin(lt * 2) * 2)
    R(d, 143 + sw, 64, 36, 16, INK_C); R(d, 144 + sw, 65, 34, 14, AMB if v is not True else (150, 160, 190))
    draw_text(img, 148 + sw, 66, '暧昧', (255, 255, 255))
    d.line([(150, 58), (148 + sw, 64)], fill=(200, 200, 210)); d.line([(172, 58), (174 + sw, 64)], fill=(200, 200, 210))
    # 我在雾里打转
    wx = 90 + int(math.sin(lt * 0.9) * 40)
    fdir = 1 if math.cos(lt * 0.9) > 0 else -1
    reach = 5.4 < lt < 6.6
    lead(img, wx, 132, 'wave' if reach else 'idle', 'sad' if lt > 6.6 else 'neutral', fdir, 2, walk=not reach, t=t)
    if lt > 0.5:
        for i in range(3):
            if lt > 0.5 + i * 0.4:
                qmark(img, wx - 14 + i * 12, 50 - (i % 2) * 6)
    # 她的剪影在雾里时隐时现
    if 2.8 < lt < 6.4:
        al = seg(lt, 2.8, 3.8) * (1 - seg(lt, 5.6, 6.4))
        sil = you_spr('idle', 'stand', 'smile').copy()
        arr = np.array(sil)
        arr[..., :3] = (arr[..., :3] * 0.3 + np.array(AMB) * 0.7).astype(np.uint8)
        arr[..., 3] = (arr[..., 3] * al * 0.8).astype(np.uint8)
        put(img, Image.fromarray(arr), 240, 132, 2, -1)
    # 雾
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    fog = 0.35 + 0.25 * np.sin(xx * 0.04 + lt * 0.7 + np.sin(yy * 0.08)) * np.cos(yy * 0.05 - lt * 0.4)
    fog = np.clip(fog, 0, 0.7)
    fogc = np.array((200, 160, 220) if v is not True else (170, 190, 200), float)
    m = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < fog
    a[m] = a[m] * 0.55 + fogc * 0.45
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0))
    # 弯月举手电
    moonc(img, 36, 22, 'side', 2, v)
    if lt > 1.0:
        spotlight(img, 46, 30, 132, 26, (255, 250, 200), 0.18)
    if lt > 6.6:
        sfx(img, 240, 60, '散了…', t, t - lt + 6.6, 99, 'cyan', 1)


def s_tug(img, t, lt, v):
    """曾经多少个牵肠拉扯不舍夜晚：屋顶上拉绳，日历狂翻"""
    p = P(v); d = ImageDraw.Draw(img)
    night(img, t, v, 140)
    skyline(img, v, 150, seed=61, hmin=10, hmax=50, lit=0.3)
    R(d, 0, 132, W, 48, lerpc(p['ink'], p['wall'], 0.6)); R(d, 0, 132, W, 2, lerpc(p['wall2'], (255, 255, 255), 0.2))
    sw = math.sin(lt * 3.2) * 6
    lx, yx = 92 + int(sw * 0.3), 236 + int(sw * 0.3)
    lead(img, lx, 132, 'wave', 'happy', 1, 2)
    you(img, yx, 132, 'phone', 'smile', -1, 2)
    hy = 98
    kx = 164 + int(sw)
    d.line([(lx + 14, hy), (kx, hy + 2), (yx - 14, hy)], fill=(240, 220, 180), width=2)
    heart_glow(img, kx, hy, 2, (255, 110, 150) if v is not True else (170, 200, 220))
    n = 1 + int(98 * ease(seg(lt, 0.3, 3.4)))
    cal_page(img, 8, 10, f'第{n}夜')
    hh = 3 + int(lt * 0.3)
    s = f'聊天时长 0{hh}:{int(12 + lt * 7) % 60:02d}:{int(lt * 37) % 60:02d}'
    draw_text(img, 196, 12, s, CREAM, outline=INK_C)
    moonc(img, 164, 36, 'happy', 2, v)
    if lt > 0.3:
        sfx(img, 164, 62, '哔——', t, t - lt + 0.3, 1.2, 'white', 1)


def s_fade(img, t, lt, v):
    """到现在热情褪成陌路的感叹"""
    street(img, t, v, 130, seed=71)
    d = ImageDraw.Draw(img)
    # 陌路路牌
    R(d, 284, 50, 3, 80, (100, 100, 110))
    R(d, 262, 42, 48, 18, INK_C); R(d, 263, 43, 46, 16, (90, 150, 190))
    draw_text(img, 274, 45, '陌路', (255, 255, 255))
    yx = lerp(300, 20, seg(lt, 0.2, 3.4))
    turn = lt > 2.2
    lead(img, 140, 130, 'idle', 'sad' if turn else 'neutral', -1 if turn else 1, 2)
    you(img, int(yx), 130, 'phone', 'bored' if abs(yx - 140) > 20 else 'smile', -1, 2, walk=True, t=t)
    if 1.0 < lt < 1.9:
        say(img, 150, 48, '嗨…', tail='l')
    # 温度计
    k = ease(seg(lt, 0.6, 3.0))
    R(d, 10, 10, 12, 74, INK_C); R(d, 12, 12, 8, 66, (240, 240, 250))
    lvl = int(lerp(60, 6, k))
    col = lerpc((255, 80, 110), (110, 200, 240), k)
    R(d, 13, 76 - lvl, 6, lvl, col)
    disc(d, 16, 84, 7, INK_C); disc(d, 16, 84, 5, col)
    draw_text(img, 26, 10, 'HOT', (255, 110, 120), outline=INK_C)
    draw_text(img, 26, 64, 'COLD', (140, 220, 255), outline=INK_C)
    if lt > 3.2:
        sfx(img, 120, 52, '唉——', t, t - lt + 3.2, 99, 'cyan', 1)
    sweep = int(W * ease(seg(lt, 2.0, 4.6)))
    fade_img(img, 0.75, 0, sweep)


def s_tangle(img, t, lt, v):
    """何必拿真心与寂寞去纠缠"""
    bedroom(img, t, v, 0.6, 'sad', bed=True, dim=0.25)
    tint_img(img, (60, 110, 150), 0.18)
    d = ImageDraw.Draw(img)
    lead(img, 120, 132, 'phone', 'sad' if lt < 4 else 'cry', 1, 2)
    heart_glow(img, 120, 96, 2, (255, 120, 160))
    # 寂寞毛线鬼
    gx = int(lerp(330, 240, ease(seg(lt, 0.3, 2.0)))) + int(math.sin(lt * 2) * 3)
    gy = 66 + int(math.sin(lt * 1.5) * 4)
    disc(d, gx, gy, 19, INK_C); disc(d, gx, gy, 18, (150, 150, 165))
    R(d, gx - 18, gy, 37, 22, (150, 150, 165))
    for i in range(5):
        disc(d, gx - 14 + i * 7, gy + 22, 4, (150, 150, 165))
    R(d, gx - 7, gy - 4, 3, 4, INK_C); R(d, gx + 4, gy - 4, 3, 4, INK_C)
    draw_text(img, gx - 12, gy + 4, '寂寞', (60, 60, 80))
    # 越缠越乱的线
    n = int(seg(lt, 1.2, 6.0) * 90)
    pts = []
    for i in range(n):
        a = i * 0.37
        rr = 12 + 10 * math.sin(i * 0.21)
        pts.append((120 + math.cos(a) * (rr + 6), 100 + math.sin(a * 1.3) * (rr + 14)))
    if lt > 1.2:
        pts = [(gx - 18, gy + 10)] + pts
    for a_, b_ in zip(pts, pts[1:]):
        d.line([a_, b_], fill=(185, 185, 200), width=1)
    if lt > 3.4:
        OS(img, 6, 20, '何必呢', t, t - lt + 3.4)


def s_chatlog(img, t, lt, v):
    """几人份的畅谈道三两句晚安：聊天记录长到翻不到头"""
    bedroom(img, t, v, 0.5, 'happy', bed=False, dim=0.35)
    hist = [('l', '然后呢然后呢'), ('r', '哈哈哈哈'), ('l', '你也喜欢这首?'), ('r', '单曲循环中'), ('l', '明天吃什么'),
            ('r', '随便都行'), ('l', '你好会聊'), ('r', '跟你才这样'), ('l', '哈哈'), ('r', '真的'), ('l', '困了吗'), ('r', '还好你呢')]
    msgs = [hist[i % len(hist)] for i in range(24)]
    ends = []
    if lt > 2.2:
        ends.append(('l', '晚安'))
    if lt > 2.9:
        ends.append(('l', '真的睡啦'))
    if lt > 3.5:
        ends.append(('l', '晚安安'))
    scroll = int(max(0, 1 - seg(lt, 0, 2.0)) * 260)
    phone_ui(img, 36, 6, 116, 124, v, msgs + ends, t, '她', scroll=scroll)
    d = ImageDraw.Draw(img)
    # 滚动条
    R(d, 155, 14, 3, 112, (60, 60, 80))
    sy = int(lerp(14, 116, 1 - seg(lt, 0, 2.0)))
    R(d, 155, sy, 3, 10, CREAM)
    draw_text(img, 162, 8, f'聊天记录 {int(1 + 998 * seg(lt, 0, 2.0))}/999', CREAM, outline=INK_C)
    lead(img, 238, 132, 'phone', 'blush' if lt > 2.2 else 'happy', -1, 2)
    moonc(img, 296, 30, 'happy', 2, v)
    cnt = (lt > 2.2) + (lt > 2.9) + (lt > 3.5)
    if cnt:
        say(img, 214, 44, ['', '一句', '两句', '三句~'][cnt], tail='r')


def s_daydream(img, t, lt, v):
    """惹多情的遐想却轻易地走散"""
    p = P(v)
    street(img, t, v, 130, seed=81)
    d = ImageDraw.Draw(img)
    # 路口指示
    R(d, 158, 70, 3, 60, (100, 96, 110))
    d.polygon([(130, 72), (158, 72), (158, 82), (130, 82), (126, 77)], fill=(200, 200, 210), outline=INK_C)
    d.polygon([(161, 84), (190, 84), (194, 89), (190, 94), (161, 94)], fill=(200, 200, 210), outline=INK_C)
    if lt < 2.3:
        lead(img, 120, 130, 'idle', 'blush', 1, 2)
        k = ease(seg(lt, 0.1, 0.6))
        if k > 0:
            for i, (bx, by, br) in enumerate(((134, 70, 2), (142, 60, 3))):
                disc(d, bx, by, br + 1, INK_C); disc(d, bx, by, br, (250, 248, 240))
            thought(img, 210, 40, int(56 * k), int(30 * k))
            if k >= 1:
                moonc(img, 238, 26, 'happy', 1, v)
                lead(img, 196, 66, 'idle', 'happy', 1, 1)
                you(img, 212, 66, 'idle', 'smile', -1, 1)
                heart(img, 204, 30, 1, (255, 90, 140))
                d.line([(201, 50), (207, 50)], fill=(250, 214, 186))
    else:
        if lt < 2.8:
            ph = seg(lt, 2.3, 2.8)
            for i in range(10):
                a = i / 10 * 6.283
                disc(d, int(210 + math.cos(a) * (20 + ph * 40)), int(40 + math.sin(a) * (12 + ph * 24)), 2, (250, 248, 240))
        sfx(img, 210, 40, '啵！', t, t - lt + 2.3, 0.8, 'white', 2)
        mx = lerp(130, 30, ease(seg(lt, 2.7, 5.0)))
        yx = lerp(190, 300, ease(seg(lt, 2.7, 5.0)))
        lead(img, int(mx), 130, 'idle', 'sad', -1, 2, walk=lt < 5.0, t=t)
        you(img, int(yx), 130, 'phone', 'bored', 1, 2, walk=lt < 5.0, t=t)
        if lt > 3.2:
            sys_msg(img, 160, 18, '对方已下线', (120, 120, 140))
    moonc(img, 296, 22, 'side' if lt > 2.3 else 'happy', 2, v)
    if lt > 3.6:
        say(img, 240, 36, '啧', tail='r')


def s_vane(img, t, lt, v):
    """情意绵绵总与见异思迁为难：长长的毛线 vs 乱转的心情风向标"""
    p = P(v); d = ImageDraw.Draw(img)
    fill_grad(img, lerpc(p['sky0'], WINE, 0.2), p['ink'])
    spotlight(img, 90, 0, 132, 34, (255, 240, 200), 0.22)
    spotlight(img, 236, 0, 132, 34, (255, 200, 230), 0.22)
    R(d, 0, 132, W, 48, (70, 40, 60)); R(d, 0, 132, W, 2, (130, 80, 110))
    for x in range(0, W, 20):
        R(d, x, 0, 10, 6, (150, 40, 70)); R(d, x + 10, 0, 10, 4, (120, 30, 60))
    # 毛线团 + 绵绵的长线
    lead(img, 86, 132, 'phone', 'blush' if lt < 5 else 'sad', 1, 2)
    disc(d, 100, 98, 7, INK_C); disc(d, 100, 98, 6, (255, 150, 180))
    for k in range(-4, 5, 2):
        d.arc([94, 92 + k, 106, 104 + k], 200, 340, fill=(220, 100, 140))
    reach = ease(seg(lt, 0.3, 3.0))
    pts = []
    for i in range(40):
        f = i / 39 * reach
        x = 104 + f * 116
        y = 128 + math.sin(f * 14 + lt * 3) * 3
        pts.append((x, y))
    for a_, b_ in zip(pts, pts[1:]):
        d.line([a_, b_], fill=(255, 150, 180), width=1)
    you(img, 236, 132, 'idle', 'side' if int(lt * 1.6) % 2 else 'smile', -1, 2)
    # 风向标
    R(d, 235, 30, 2, 28, (200, 200, 210))
    labels = ['靠近', '后退', '晴', '阴', '在乎', '算了']
    idx = int(lt * 1.6) % len(labels)
    ang = math.sin(lt * 5.3) * 1.2 + math.sin(lt * 2.1) * 2
    ex, ey = 236 + math.cos(ang) * 16, 30 + math.sin(ang) * 4
    d.line([(236, 30), (ex, ey)], fill=(255, 230, 120), width=2)
    d.polygon([(ex, ey - 3), (ex + 4 * math.copysign(1, math.cos(ang)), ey), (ex, ey + 3)], fill=(255, 230, 120))
    s = labels[idx]
    R(d, 236 - text_w(s) // 2 - 3, 8, text_w(s) + 6, 14, INK_C)
    draw_text(img, 236 - text_w(s) // 2, 9, s, (255, 230, 120))
    if lt > 2.2:
        sfx(img, 160, 34, '心思说变就变', t, t - lt + 2.2, 99, 'purp', 1)
    if lt > 4.6:
        OS(img, 6, 10, '又变了', t, t - lt + 4.6)


def s_ko(img, t, lt, v):
    """总是不能抵抗你信手的晚安：防线 HP 被打到 0"""
    p = P(v); d = ImageDraw.Draw(img)
    left = Image.new('RGB', (W, H))
    fill_grad(left, lerpc(p['wall'], WINE, 0.25), lerpc(p['ink'], WINE, 0.15))
    dl = ImageDraw.Draw(left)
    R(dl, 0, 132, 160, 48, lerpc(p['ink'], WINE, 0.25))
    R(dl, 30, 106, 90, 26, (110, 50, 80)); R(dl, 30, 98, 90, 10, (130, 60, 96))
    you(left, 80, 132, 'phone', 'bored', 1, 2)
    if 0.8 < lt < 2.0:
        say(left, 20, 40, '晚安~', tail='r')
    img.paste(left.crop((0, 0, 158, H)), (0, 0))
    right = Image.new('RGB', (W, H))
    bedroom(right, t, v, 0.6, 'side', win_x=180, bed=False, stand=False)
    ko = lt > 2.6
    lead(right, 236, 132, 'phone' if ko else 'idle', 'blush' if ko else 'neutral', -1, 2)
    if ko:
        phone_small(right, 228, 96, v, True)
        glow(right, 232, 100, 26, p['scr'], 0.25)
    img.paste(right.crop((162, 0, 320, H)), (162, 0))
    R(d, 158, 0, 4, H, INK_C)
    # 飞过去的晚安
    if 1.6 < lt < 2.4:
        f = seg(lt, 1.6, 2.4)
        x = int(lerp(90, 230, f)); y = int(60 - math.sin(f * 3.14) * 30)
        R(d, x - 1, y - 1, 30, 14, INK_C); R(d, x, y, 28, 12, CREAM)
        draw_text(img, x + 2, y, '晚安', INK_C)
    if lt < 1.8:
        say(img, 176, 28, '今天不先回了', tail='l')
    hp = 1.0 - ease(seg(lt, 1.9, 2.6))
    meter(img, 176, 10, '防线', hp, (110, 220, 140) if hp > 0.3 else (255, 80, 90), 70)
    if ko:
        stamp(img, 232, 44, 'K.O.', t, t - lt + 2.6, (230, 40, 60), scale=1)
        sfx(img, 280, 90, '秒回!', t, t - lt + 3.0, 99, 'pink', 1)
    moonc(img, 140, 24, 'side' if lt < 2.6 else 'shock', 2, v)


def s_bridge(img, t, lt, v):
    """执迷与你忽远忽近烂桥段：断掉的桥 + 场记板"""
    p = P(v); d = ImageDraw.Draw(img)
    night(img, t, v, 150)
    R(d, 0, 124, W, 56, lerpc(p['sky0'], (20, 30, 60), 0.5))
    for i in range(24):
        x = int(hsh(i, 9) * W); y = 128 + int(hsh(i, 10) * 40)
        R(d, x + int(math.sin(t * 1.5 + i) * 3), y, 6, 1, lerpc(p['moon'], p['sky0'], 0.4))
    bc = (110, 80, 70) if v is not True else (90, 96, 104)
    # 左段 + 右段桥面（中间断开）
    R(d, 0, 118, 150, 6, bc); R(d, 186, 118, 134, 6, bc)
    for x in range(6, 150, 18):
        R(d, x, 124, 4, 56, lerpc(bc, (0, 0, 0), 0.3))
    for x in range(196, 320, 18):
        R(d, x, 124, 4, 56, lerpc(bc, (0, 0, 0), 0.3))
    R(d, 0, 104, 150, 2, bc); R(d, 186, 104, 134, 2, bc)
    for x in range(0, 150, 10):
        R(d, x, 104, 2, 14, bc)
    for x in range(186, 320, 10):
        R(d, x, 104, 2, 14, bc)
    # 断口碎片
    for i in range(4):
        R(d, 150 + i * 2, 124 + i * 5, 4, 3, bc); R(d, 182 - i * 2, 124 + i * 6, 4, 3, bc)
    lead(img, 128, 118, 'wave' if int(lt) % 2 else 'idle', 'sad' if lt > 3 else 'neutral', 1, 2)
    near = int(lt / 0.75) % 2 == 0
    if near:
        you(img, 214, 118, 'idle', 'smile', -1, 2)
    else:
        you(img, 288, 112, 'idle', 'side', -1, 1)
    n = 1 + int(lt / 0.75)
    snap = (lt % 0.75) < 0.12
    my_clapper(img, 8, 8, n, snap)
    if snap and lt > 0.1:
        sfx(img, 40, 56, '咔!', t, t - (lt % 0.75), 0.4, 'yel', 1)
    moonc(img, 170, 28, 'smirk', 2, v)
    megaphone(img, 182, 32, t, 1)
    rel_bar(img, 254, 8, 0.5 + 0.13 * math.sin(lt * 4.2), v, 50, label=False)


MAZE_PATH = [(18, 104), (18, 80), (66, 80), (66, 104), (114, 104), (114, 56), (42, 56), (42, 20), (90, 20), (90, 36), (138, 36),
             (138, 20), (186, 20), (186, 84), (162, 84), (162, 104), (208, 104)]


def _along(path, f):
    seglens = [math.dist(a, b) for a, b in zip(path, path[1:])]
    tot = sum(seglens); s = f * tot
    for (a, b), l in zip(zip(path, path[1:]), seglens):
        if s <= l:
            k = s / l if l else 0
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        s -= l
    return path[-1]


def maze(img, v, f, t):
    p = P(v); d = ImageDraw.Draw(img)
    R(d, 6, 8, 214, 110, lerpc(p['ink'], p['wall'], 0.5))
    wall = lerpc(p['wall2'], (255, 255, 255), 0.15)
    # 墙：网格砖
    for y in range(8, 118, 8):
        for x in range(6 + (y // 8 % 2) * 6, 220, 12):
            R(d, x, y, 11, 7, wall)
    # 走廊（含几条死路）
    corr = (24, 20, 40)
    stubs = [[(66, 80), (66, 64)], [(114, 104), (150, 104)], [(42, 20), (20, 20), (20, 44)], [(186, 84), (208, 84), (208, 60)], [(90, 36), (90, 56)]]
    for path in [MAZE_PATH] + stubs:
        for a, b in zip(path, path[1:]):
            x0, x1 = sorted((a[0], b[0])); y0, y1 = sorted((a[1], b[1]))
            R(d, x0 - 5, y0 - 5, x1 - x0 + 11, y1 - y0 + 11, corr)
    # 走过的路：奶黄虚线
    n = 120
    for i in range(int(n * f)):
        x, y = _along(MAZE_PATH, i / n)
        if i % 2 == 0:
            d.point((int(x), int(y)), fill=CREAM)
    x, y = _along(MAZE_PATH, f)
    R(d, int(x) - 6, int(y) - 4, 13, 9, INK_C); R(d, int(x) - 5, int(y) - 3, 11, 7, (250, 248, 240))
    d.line([(int(x) - 5, int(y) - 3), (int(x), int(y) + 1), (int(x) + 5, int(y) - 3)], fill=(240, 90, 120))


def s_maze(img, t, lt, v):
    """迂回一句晚安，多情人却自找难堪"""
    p = P(v); d = ImageDraw.Draw(img)
    fill_grad(img, p['sky0'], p['ink'])
    f = ease(seg(lt, 0.0, 3.4))
    maze(img, v, f, t)
    if lt < 3.4:
        sfx(img, 266, 20, '迂回中…', t, t - lt + 0.3, 3.1, 'yel', 1)
    got = lt > 3.5
    shame = lt > 4.8
    lead(img, 266, 132, 'phone' if got and not shame else 'idle', 'awk' if shame else ('happy' if got else 'neutral'), -1, 2)
    if got and not shame:
        heart(img, 266, 50, 1, (255, 90, 140)); heart(img, 280, 42, 1, (255, 90, 140))
    if shame:
        # 抱着枕头埋脸
        R(d, 251, 62, 30, 20, INK_C); R(d, 252, 63, 28, 18, (200, 186, 236)); R(d, 252, 63, 28, 2, (230, 222, 250))
        R(d, 265, 64, 1, 16, (170, 150, 214))
        sfx(img, 292, 58, '///', t, t - lt + 4.9, 99, 'pink', 1)
        stamp(img, 262, 30, '自找难堪', t, t - lt + 4.8, (220, 50, 70), scale=1)
    if got:
        sfx(img, 266, 102 - 50, '叮！', t, t - lt + 3.5, 0.8, 'yel', 1)
    moonc(img, 300, 100, 'side' if shame else 'happy', 2, v)
    if lt > 5.6:
        say(img, 230, 86, '唉~', tail='r')


def s_balcony(img, t, lt, v):
    """间奏：阳台吹风看月亮，回忆相片飘过，弯月陪坐"""
    p = P(v); d = ImageDraw.Draw(img)
    night(img, t, v, 140)
    skyline(img, v, 140, seed=91, hmin=26, hmax=70, lit=0.3)
    # 月亮从楼后升起后坐到栏杆上
    mx = int(lerp(250, 222, ease(seg(lt, 4.0, 6.0))))
    my = int(lerp(110, 30, ease(seg(lt, 0.4, 3.6))))
    if lt > 6.0:
        my = int(lerp(30, 88, ease(seg(lt, 6.0, 7.5))))
    mexpr = 'happy' if lt < 11 else ('yawn' if lt < 13 else ('side' if lt < 16 else 'sad'))
    moonc(img, mx, my, mexpr, 2, v)
    # 阳台
    R(d, 0, 104, W, 4, (200, 200, 214))
    for x in range(4, W, 10):
        R(d, x, 108, 2, 24, (170, 170, 190))
    R(d, 0, 132, W, 48, lerpc(p['ink'], p['wall'], 0.5))
    shake = lt > 13.6 and lt < 15
    fdir = (1 if int(lt * 6) % 2 else -1) if shake else 1
    ex = 'neutral' if lt < 16 else 'sad'
    lead(img, 150, 132, 'idle', ex, fdir, 2)
    # 回忆相片
    for i, kind in enumerate(['rope', 'chat', 'bridge', 'moon']):
        born = 1.0 + i * 2.6
        ph = (lt - born) / 7.0
        if 0 <= ph <= 1:
            x = int(lerp(330, -40, ph)); y = 14 + int(math.sin(ph * 6 + i) * 6) + (i % 2) * 8
            photo(img, x, y, kind, t)
    if 11.2 < lt < 14.6:
        say(img, 176, 60, '该睡了~', tail='r')
    if lt > 15.2:
        phone_small(img, 166, 86, v, True)
        sys_msg(img, 160, 40, '0 条新消息', (110, 110, 130))


def s_typing(img, t, lt, v):
    """桥段：打出晚安又删掉，重复三次，最后把手机扣下"""
    p = P(v); d = ImageDraw.Draw(img)
    bedroom(img, t, v, 0.7, 'side', bed=False, lamp_on=True, dim=0.3)
    # 输入循环：每轮 4 秒：0-1.2 打字，1.2-2.4 停，2.4-3.2 退格
    cyc = lt % 4.4
    rnd = int(lt // 4.4)
    full = '晚安'
    if rnd >= 3:
        txt = ''
    elif cyc < 1.2:
        txt = full[:int(cyc / 0.5) + 1] if cyc > 0.2 else ''
    elif cyc < 2.6:
        txt = full
    elif cyc < 3.4:
        txt = full[:max(0, 2 - int((cyc - 2.6) / 0.35) - 1)]
    else:
        txt = ''
    flipped = lt > 13.6
    if not flipped:
        phone_ui(img, 176, 8, 110, 120, v, [('l', '晚安'), ('r', '晚安'), ('l', '今天好累'), ('r', '早点休息')], t, '她',
                 input_txt=txt, cursor_on=int(t * 3) % 2 == 0)
        if rnd < 3 and 2.6 < cyc < 3.4:
            sfx(img, 300, 110, '删', t, t - cyc + 2.6, 0.8, 'red', 1)
    else:
        R(d, 176, 124, 120, 5, (110, 80, 90)); R(d, 182, 129, 4, 3, (90, 64, 74)); R(d, 286, 129, 4, 3, (90, 64, 74))
        R(d, 206, 119, 56, 5, INK_C); R(d, 207, 120, 54, 3, (60, 58, 84))
        if lt < 14.6:
            sfx(img, 232, 96, '扣', t, t - lt + 13.6, 1.0, 'white', 2)
    ex = 'neutral' if lt < 4.4 else ('sad' if lt < 13.6 else 'closed')
    lead(img, 120, 132, 'phone' if not flipped else 'idle', ex, 1, 2)
    if lt > 15.0:
        sfx(img, 88, 36, '咚咚', t, t - lt + 15.0, 1.2, 'white', 1)
    if lt > 15.6:
        say(img, 92, 50, '睡吧', tail='l')
    n = min(3, rnd + (1 if cyc > 3.2 else 0))
    if n:
        draw_text(img, 8, 8, f'删除 ×{n}', (255, 140, 150), outline=INK_C)


def s_final(img, t, lt, v):
    """最后一句（改写结局，贴原词）：难堪还是我的，但这次我先跟月亮说晚安"""
    p = P(v); d = ImageDraw.Draw(img)
    if lt < 2.4:
        fill_grad(img, p['sky0'], p['ink'])
        maze(img, v, ease(seg(lt, 0.0, 2.3)), t)
        lead(img, 266, 132, 'idle', 'neutral', -1, 2)
        moonc(img, 300, 100, 'happy', 2, v)
        return
    cur = 0.7 * (1 - ease(seg(lt, 5.2, 6.2)))
    mexpr = 'side' if lt < 6.2 else ('blush' if lt > 7.2 else 'happy')
    bedroom(img, t, v, cur, mexpr)
    flipped = lt > 4.6
    awk = lt < 4.6
    lead(img, 150, 132, 'phone' if not flipped else 'wave' if 6.2 < lt < 7.6 else 'idle',
         'awk' if awk else ('calm' if lt > 6.2 else 'closed'), -1, 2)
    if not flipped:
        phone_small(img, 142, 96, v, True)
        glow(img, 146, 100, 24, p['scr'], 0.25)
        say(img, 176, 30, '晚安', tail='l', bg=CREAM)
    else:
        R(d, 140, 110, 16, 3, INK_C)
        if lt < 5.4:
            sfx(img, 150, 92, '扣', t, t - lt + 4.6, 0.8, 'white', 1)
    if lt > 3.0:
        stamp(img, 250, 64, '始终难堪', t, t - lt + 3.0, (210, 60, 80), dur=2.6, scale=1)
    if lt > 6.3:
        say(img, 104, 36, '晚安', t, t - lt + 6.3, tail='l', bg=CREAM)
    if lt > 7.3:
        say(img, 30, 96, '晚安~', t, t - lt + 7.3, tail='r', bg=(255, 220, 236))
    if lt > 8.0:
        stamp(img, 250, 64, '晚安', t, t - lt + 8.0, (230, 160, 60), scale=2)


def s_outro(img, t, lt, v):
    """尾奏：天亮，我睡着了；弯月摘下睡帽落下，太阳上班"""
    dawn = ease(seg(lt, 2.0, 10.0))
    vv = 'dawn'
    my = int(lerp(26, 110, ease(seg(lt, 5.0, 9.5))))
    bedroom(img, t, vv, 0.0, 'happy' if lt < 5 else 'sleep', moon_y=my, moon_cap=lt < 3.6)
    d = ImageDraw.Draw(img)
    if lt > 6.5:
        # 太阳从窗里升起（画在窗内区域）
        sy = int(lerp(100, 40, ease(seg(lt, 6.5, 11.0))))
        win = img.crop((26, 12, 130, 88))
        sun(win, 30, sy - 12, 9, 'happy', t)
        img.paste(win, (26, 12))
    tint_img(img, (255, 200, 170), dawn * 0.18)
    lead_sleep(img, 178, 92, 'calm')
    zzz(img, 200, 64, t)
    if 3.0 < lt < 4.6:
        say(img, 30, 92, '下班啦~', tail='r')
    rel_bar(img, 160, 6, 0.5, False, 120, 1 - seg(lt, 3.0, 5.0))


def s_end(img, t, lt, v):
    p = P('dawn'); d = ImageDraw.Draw(img)
    fill_grad(img, (24, 20, 52), (60, 50, 100))
    stars(img, t, 40, h=170)
    moonc(img, 286, 40, 'blush', 3, False)
    R(d, 250, 74, 54, 22, INK_C); R(d, 251, 75, 52, 20, (250, 236, 200))
    draw_text(img, 263, 78, '晚安', INK_C)
    R(d, 276, 64, 2, 10, (200, 170, 120))


# ======================= ⑤ 镜头表 =======================
CHORUS = [s_tug, s_fade, s_tangle, s_chatlog, s_daydream, s_vane, s_ko, s_bridge, s_maze]   # L7..L15
SHOTS = [(0.0, s_title, False), (9.6, s_intro, False),
         (L(0), s_window, False), (L(1), s_bubbles, False), (L(2), s_longnight, False), (L(3), s_drop, False),
         (L(4), s_flustered, False), (L(5), s_charmed, False), (L(6), s_fog, False)]
SHOTS += [(L(7 + i), fn, False) for i, fn in enumerate(CHORUS)]
SHOTS += [(106.3, s_balcony, False),
          (L(16), s_flustered, 'replay'), (L(17), s_charmed, 'replay'), (L(18), s_fog, 'replay')]
SHOTS += [(L(19 + i), fn, True) for i, fn in enumerate(CHORUS)]
SHOTS += [(195.4, s_typing, False)]
def _dawnify(fn):
    def g(img, t, lt, v):
        fn(img, t, lt, v)
        tint_img(img, (255, 170, 170), 0.04 + 0.10 * seg(t, 214.0, 258.0))
    g.__name__ = fn.__name__ + '_dawn'
    return g


SHOTS += [(L(28 + i), _dawnify(fn), 'dawn') for i, fn in enumerate(CHORUS[3:])]
SHOTS += [(L(34), s_final, 'dawn'), (258.9, s_outro, 'dawn'), (song.p['end_start'], s_end, False)]
SHOTS.sort(key=lambda s: s[0])

# 回放段弹幕（镜头内秒）
DANMU = {
    s_flustered: [(0.2, '又来了', WHITE), (1.0, '两个人都在慌', (255, 180, 210)), (2.2, '这不就是暧昧', (255, 230, 120))],
    s_charmed: [(0.3, '着迷值爆表', (255, 180, 210)), (1.4, '月亮都看不下去', (255, 230, 120)), (2.6, '先别回!!', WHITE)],
    s_fog: [(0.4, '朋友还是恋人?', WHITE), (2.0, '雾好大', (180, 220, 255)), (4.0, '回了，还秒回', (255, 230, 120)), (6.0, '清醒一点!!', WHITE)],
}

# ======================= ⑥ 花字 =======================
CFG = {
    '窗挡住月色贪恋的交集': dict(pal='white', kw=['月色', '交集'], kwpal=['yel', 'pink'], size=104, angle=-2, deco=('star',)),
    '在浮语虚词中交映': dict(pal='whiteb', kw=['浮语虚词'], kwpal='purp', size=108, angle=2, deco=('note',)),
    '忙碌的身影慢慢的长夜': dict(pal='white', kw=['长夜'], kwpal='cyan', size=104, angle=-2, deco=('star',)),
    '去匆匆地留下感情': dict(pal='yel', kw=['感情'], kwpal='pink', size=108, angle=3, deco=('heart',)),
    '声色太慌张你眼神逃避': dict(pal='white', kw=['慌张', '逃避'], kwpal=['red', 'purp'], size=100, angle=-3, deco=('sweat', 'bang')),
    '却如此地令人着迷': dict(pal='pink', kw=['着迷'], kwpal='yel', kwscale=1.45, size=110, angle=3, deco=('heart', 'heart2')),
    '为何总留恋这种/暧昧的迷离': dict(pal='white', kw=['暧昧'], kwpal='pink', kwscale=1.4, size=100, angle=-2, deco=('q', 'heart')),
    '曾经多少个/牵肠拉扯不舍夜晚': dict(pal='yel', kw=['牵肠拉扯'], kwpal='pink', size=98, angle=2, deco=('heart', 'star')),
    '到现在热情/褪成陌路的感叹': dict(pal='white', kw=['热情', '陌路'], kwpal=['red', 'cyan'], size=100, angle=-3, deco=('crack',)),
    '何必拿真心/与寂寞去纠缠': dict(pal='cyan', kw=['真心', '寂寞'], kwpal=['pink', 'white'], size=100, angle=2, deco=('drop',)),
    '几人份的畅谈/道三两句晚安': dict(pal='white', kw=['晚安'], kwpal='yel', kwscale=1.45, size=100, angle=-2, deco=('star', 'heart')),
    '惹多情的遐想/却轻易地走散': dict(pal='pink', kw=['走散'], kwpal='cyan', kwscale=1.35, size=100, angle=3, deco=('q', 'x')),
    '情意绵绵总与/见异思迁为难': dict(pal='white', kw=['情意绵绵', '见异思迁'], kwpal=['pink', 'purp'], size=98, angle=-2, deco=('wave',)),
    '总是不能抵抗/你信手的晚安': dict(pal='yel', kw=['不能抵抗', '晚安'], kwpal=['red', 'whiteb'], size=100, angle=2, deco=('bang', 'heart')),
    '执迷与你/忽远忽近烂桥段': dict(pal='white', kw=['忽远忽近', '烂桥段'], kwpal=['cyan', 'purp'], size=100, angle=-3, deco=('crack', 'star')),
    '迂回一句晚安/多情人却自找难堪': dict(pal='white', kw=['晚安', '自找难堪'], kwpal=['yel', 'red'], size=96, angle=2, deco=('sweat', 'heart')),
    '迂回一句晚安/多情的人始终难堪': dict(pal='yel', kw=['晚安', '始终难堪'], kwpal=['whiteb', 'red'], size=96, angle=-2, deco=('heart', 'star', 'drop')),
}

MVX = MV(song, SHOTS, CFG, danmu=DANMU, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE)
frame = MVX.frame
DUR = song.dur
