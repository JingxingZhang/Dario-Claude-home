"""《{歌名}》像素 MV —— 这支片子专属的镜头脚本。

这里只有“骨架”，没有任何默认角色或默认画面：角色、配角、场景、配色、节奏都要按这首歌的曲风和歌词从零设计。
顺序：① 视觉方案（曲风 → 配色、节奏、花字基调）② 角色设计（CAST + CAST_SHEET）③ 镜头函数 ④ SHOTS ⑤ CFG ⑥ MV(...)
写法要点见 references/：visual-design.md（曲风到视觉）、storyboard-guide.md（逐句分镜）、library-api.md（工具速查）。
  - 镜头函数 fn(img, t, lt, v)：在 320×180 的 img 上画；动作一律按 lt（本镜头开始后的秒）编排。
  - v：False 普通 / 'replay' 回放（引擎自动褪色+扫描线+弹幕+标签）/ True 第二套配色（自己读 v is True 换色）。
  - 画面里的像素字、道具放在 y < 120，底部留给歌词花字和署名。
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


# ======================= ③ 镜头 =======================
def s_title(img, t, lt, v):
    """片头标题卡背后的画面（歌名和原唱由引擎叠加）——按歌设计，这里只是占位"""
    img.paste(Image.fromarray(dither_grad(H, W, PALETTE['bg'], PALETTE['ink'])), (0, 0))
    actor(img, 'lead', 160, 150)


def s_placeholder(img, t, lt, v, i=0):
    """还没设计的句子：保证流程能跑通；交付前必须全部替换"""
    img.paste(Image.fromarray(dither_grad(H, W, PALETTE['bg'], PALETTE['ink'])), (0, 0))
    actor(img, 'lead', 160, 130)
    ptext(img, 160, 30, f'第{i + 1}句 待设计', 1, (255, 230, 120))


def s_end(img, t, lt, v):
    img.paste(Image.fromarray(dither_grad(H, W, PALETTE['ink'], PALETTE['bg'])), (0, 0))


def _ph(i):
    return lambda img, t, lt, v: s_placeholder(img, t, lt, v, i)


# ======================= ④ 镜头表：(开始秒, 镜头函数, 变体) =======================
SHOTS = [(0.0, s_title, False)]
SHOTS += [(L(i), _ph(i), False) for i in range(len(song.lines))]
SHOTS += [(song.p['end_start'], s_end, False)]
SHOTS.sort(key=lambda s: s[0])

# 回放段弹幕：{镜头函数: [(镜头内秒, 文字, 颜色)]}
DANMU = {}

# ======================= ⑤ 每句歌词花字（键可用句序号或歌词原文）=======================
# pal 底色 / kw 重点词 / kwpal 重点词配色（可为列表）/ kwscale / size / cx cy / angle / deco 贴纸 / pop stagger shake …
CFG = {}

MVX = MV(song, SHOTS, CFG, danmu=DANMU, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE)
frame = MVX.frame
DUR = song.dur
