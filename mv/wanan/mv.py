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


# ======================= ③ 镜头（占位，分镜确认后再画）=======================
def s_title(img, t, lt, v):
    img.paste(Image.fromarray(dither_grad(H, W, PALETTE['sky0'], PALETTE['sky1'])), (0, 0))


def s_placeholder(img, t, lt, v, i=0):
    img.paste(Image.fromarray(dither_grad(H, W, PALETTE['sky0'], PALETTE['ink'])), (0, 0))
    ptext(img, 160, 30, f'第{i + 1}句 待设计', 1, (255, 230, 120))


def s_end(img, t, lt, v):
    img.paste(Image.fromarray(dither_grad(H, W, PALETTE['ink'], PALETTE['sky0'])), (0, 0))


def _ph(i):
    return lambda img, t, lt, v: s_placeholder(img, t, lt, v, i)


SHOTS = [(0.0, s_title, False)]
SHOTS += [(L(i), _ph(i), False) for i in range(len(song.lines))]
SHOTS += [(song.p['end_start'], s_end, False)]
SHOTS.sort(key=lambda s: s[0])
DANMU = {}
CFG = {}

MVX = MV(song, SHOTS, CFG, danmu=DANMU, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE)
frame = MVX.frame
DUR = song.dur
