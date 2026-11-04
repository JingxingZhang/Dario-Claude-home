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

# ======================= ① 视觉方案（按曲风和歌词定，写清理由）=======================
# 曲风：{例：慢板抒情 / 72 BPM / 钢琴+弦乐}  → 节奏：一句一镜、慢推慢移；花字：小回弹、慢逐字
# 主色：{例：雾蓝 + 暖橘路灯}  理由：{歌词里的“冬夜”“等你回家”}
PALETTE = {'bg': (40, 48, 80), 'accent': (255, 170, 90), 'ink': (24, 20, 34)}
LYRIC_BASE = dict(pop=1.28, stagger=0.05, float_amp=5)      # 按曲风改：抒情 pop≈1.08 stagger≈0.09；燃 pop≈1.45 stagger≈0.03 shake≈5
TITLE_STYLE = dict(pal='pink', size=230, angle=-3, deco=('heart', 'star'))

# ======================= ② 角色设计（从零画，别套现成形象）=======================
# 主角是谁由歌词决定：人数、年龄、时代、职业、是不是人（可以是动物、物件、一团光）。
# 用字符画逐像素画：一个字符一个像素，配调色表；不同动作各画一张，表情用 eyes()/mouth() 叠加。
# 下面这个灰色剪影只是占位，正式制作前必须换成按歌设计的角色。
PLACEHOLDER = '''
....kkkk....
...kkkkkk...
...kkkkkk...
....kkkk....
...kkkkkk...
..kkkkkkkk..
..kkkkkkkk..
...kk..kk...
...kk..kk...
'''
CAST = {
    'lead': dict(name='主角（待设计）', art={'idle': PLACEHOLDER}, pal={'k': (150, 150, 165)}),
}


def actor(img, who, x, y, pose='idle', scale=3, face=1, expr=None, lt=0.0):
    """画一个角色：x,y 脚底中点。expr 可在这里按设计叠加眼睛嘴巴。"""
    c = CAST[who]
    art = c['art'].get(pose) or c['art']['idle']
    put(img, pixmap(art, c['pal']), x, y, scale, face)


def CAST_SHEET(img, t):
    """角色设定图：分镜检查点时连同分镜一起发给用户确认。画出每个角色的主要动作/表情、配角或贯穿物件、配色条。"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(236, 232, 244))
    draw_text(img, 8, 6, '角色设定（待设计）', K)
    for i, (k, c) in enumerate(CAST.items()):
        actor(img, k, 50 + i * 70, 140, 'idle', 3)
        draw_text(img, 50 + i * 70 - text_w(c['name']) // 2, 146, c['name'], K)
    palette_strip(img, 8, 166, list(PALETTE.values()))


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
