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


# ======================= ③ 场景与镜头（按 故事.md 的剧情顺序）=======================
# 场景函数（画背景）可以多次调用；镜头函数（某一句、某个剧情节拍）每个只用一次。
def bg_placeholder(img, t, k=0.0):
    img.paste(Image.fromarray(dither_grad(H, W, lerpc(PALETTE['bg'], PALETTE['accent'], k * 0.3), PALETTE['ink'])), (0, 0))


def s_title(img, t, lt, v):
    """片头标题卡背后的画面（歌名和原唱由引擎叠加）：故事的开场状态"""
    bg_placeholder(img, t)
    actor(img, 'lead', 160, 150)
    bubbles(t, 4, 1, 0, 320, 0, 110)                     # 玻璃水滴氛围（可删）


def s_placeholder(img, t, lt, v, i=0):
    """还没设计的句子：保证流程能跑通；交付前必须全部替换"""
    bg_placeholder(img, t, i / max(1, len(song.lines)))
    actor(img, 'lead', 160, 130)
    gchip(t, t - lt + 0.2, 160, 30, f'第{i + 1}句 · 剧情节拍待设计', size=44)


def s_end(img, t, lt, v):
    """片尾：故事的结局状态（引擎叠加歌名、原唱、谢谢收看）"""
    bg_placeholder(img, t, 1.0)


def _ph(i):
    return lambda img, t, lt, v: s_placeholder(img, t, lt, v, i)


# ======================= ④ 镜头表：(开始秒, 镜头函数, 参数 v) =======================
# 每个镜头函数只出现一次（sweep.py 会检查）。确需首尾呼应的同一函数，写进 ALLOW_REPEAT 并说明理由。
SHOTS = [(0.0, s_title, None)]
SHOTS += [(L(i), _ph(i), None) for i in range(len(song.lines))]
SHOTS += [(song.p['end_start'], s_end, None)]
SHOTS.sort(key=lambda s: s[0])
ALLOW_REPEAT = {}

# 段落切换时刻：每处有一颗大玻璃透镜横扫画面（主歌、副歌、间奏、桥段、尾奏的起点）
SECTIONS = []

# ======================= ⑤ 每句歌词花字（键用句序号；重复的歌词可以按剧情换配色和重点词）=======================
# pal 底色 / kw 重点词 / kwpal 重点词配色（可为列表）/ kwscale / size / cx cy / angle / deco 贴纸 / pop stagger shake …
CFG = {}

MVX = MV(song, SHOTS, CFG, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE, sections=SECTIONS)
frame = MVX.frame
DUR = song.dur

# ======================= ⑦ 封面（scripts/cover.py 导出）=======================
COVER_T = None          # 16:9 封面取哪一秒：全片最有戏、最能代表故事的一帧


def COVER_3X4(img, t):
    """3:4 竖版封面的像素层（180×240）：标题、原唱、标签、署名由 cover.py 自动加。
    构图：上方 0–55 行留给标题，主画面 55–195 行，底部 195–240 行留给原唱和署名。
    可以用 cover.portrait_from(横版场景) 把一张 320×180 场景裁成竖版，再摆角色；也可以登记玻璃（g* 组件）。"""
    img.paste(Image.fromarray(dither_grad(240, 180, PALETTE['bg'], PALETTE['ink'])), (0, 0))
    actor(img, 'lead', 90, 190)
