"""《{歌名}》像素 MV —— 这支片子专属的镜头脚本。

这里只有“骨架”，没有任何默认角色或默认画面：故事、角色、场景、配色、节奏都要按这首歌从零设计。
顺序：① 视觉方案 ② 角色（CAST + CAST_SHEET）③ 场景与镜头函数（按 故事.md 的剧情顺序写）④ SHOTS ⑤ CFG ⑥ MV(...) ⑦ 封面
写法要点见 references/：story-design.md（先写故事）、storyboard-guide.md（逐句分镜）、visual-design.md、
liquid-glass.md（玻璃层）、library-api.md（工具速查）。

  - 镜头函数 fn(img, t, lt, v)：在 320×180 的 img 上画像素世界；动作一律按 lt（本镜头开始后的秒）编排。
  - 一个镜头函数只用一次：重复的歌词要画剧情的下一步，不复用镜头（sweep.py 会检查）。
    想做“视觉押韵”（同一个构图、同一个地方再出现），就写一个新函数，复用场景的绘制函数，但人物状态、时间、天气、道具要变。
  - v：随便传什么给镜头函数（比如这段剧情所处的时间 'dusk'、角色状态），按需使用。
  - 画面里的像素字、道具放在 y < 120，底部留给歌词花字和署名。
  - 液态玻璃：调用 glassui 的 gchip / gtag / gcard / gheart / glens / gdrop / bubbles / gmove / gsearch / say / OS / popup / meter
    “登记”玻璃，引擎放大画面后统一画（见 references/liquid-glass.md）。玻璃是“文字和界面”那一层，像素是“世界”那一层。
    带 born 的玻璃会自动弹出、待机微浮、在镜头结束前自动退场；born=None 是窗、镜面这类结构性玻璃，不做动画。
  - 迭代二画风（默认）：角色用 refine.render_char，背景用 lib/style.py 的工具；每个户外 / 室内场景画完背景后调用 ST.mark(img)，
    引擎的高清光影层会让背景轻度虚化、人物锐利并带轮廓光，户外白天加光束，按天空调色（见 references/visual-design.md）。
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
from refine import render_char, refined_sprite   # 迭代二画风：角色精修（Scale2x + 体积光影 + 彩色描边 + 高清五官）
import style as ST              # 迭代二画风：天空、云、远景城市、树、地面、雪和落叶；ST.mark(img) 登记背景快照
from chars import heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, curtains, R
from engine import Song, MV
import huazi as Z

song = Song(ROOT)
rms, pump, beat_phase, L = song.rms, song.pump, song.beat_phase, song.L

# ======================= ① 视觉方案（按曲风、歌词和故事定，写清理由）=======================
# 曲风：{例：慢板抒情 / 72 BPM / 钢琴+弦乐}  → 节奏：一句一镜、慢推慢移；花字：小回弹、慢逐字
# 主色：{例：雾蓝 + 暖橘路灯}  理由：{歌词里的“冬夜”“等你回家”}
# 故事的时间线怎么体现在颜色上：{例：第一段秋天午后 → 第二段冬夜 → 结尾春天清晨}
PALETTE = {'bg': (40, 48, 80), 'accent': (255, 170, 90), 'ink': (24, 20, 34)}
LYRIC_BASE = dict(pop=1.28, stagger=0.05, float_amp=5)      # 按曲风改：抒情 pop≈1.08 stagger≈0.09；燃 pop≈1.45 stagger≈0.03 shake≈5
TITLE_STYLE = dict(pal='pink', size=230, angle=-3, deco=('heart', 'star'))

# ======================= ② 角色设计（从零画，别套现成形象）=======================
# 主角是谁由故事决定：人数、年龄、时代、职业、是不是人（可以是动物、物件、一团光）。
# 用字符画逐像素画：一个字符一个像素，配调色表；不同动作各画一张，表情用 eyes()/mouth() 叠加。
# 故事里角色会变（换季换装、受伤、长大、关系变化），就用 recolor() 或另画一张，体现在画面上。
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


def actor(img, who, x, y, pose='idle', scale=2, face=1, expr='smile', lt=0.0):
    """画一个角色：x,y 脚底中点。迭代二画风用 render_char（精修 + 高清五官）；
    字符画里五官留空，在 CAST 里写 eye=(列, 行, 两眼间距)、mth=(列, 行)。"""
    c = CAST[who]
    art = c['art'].get(pose) or c['art']['idle']
    if 'eye' in c:
        return render_char(img, art, c['pal'], x, y, face, c['eye'], c['mth'], expr)
    put(img, refined_sprite(art, c['pal']), x, y, 1, face)


def CAST_SHEET(img, t):
    """角色设定图：检查点时连同故事和分镜一起发给用户确认。画出每个角色的主要动作/表情、配角或贯穿物件、配色条。"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(236, 232, 244))
    draw_text(img, 8, 6, '角色设定（待设计）', K)
    for i, (k, c) in enumerate(CAST.items()):
        actor(img, k, 50 + i * 70, 140, 'idle', 3)
        draw_text(img, 50 + i * 70 - text_w(c['name']) // 2, 146, c['name'], K)
    palette_strip(img, 8, 166, list(PALETTE.values()))


# ======================= ③ 场景与镜头（按 故事.md 的剧情顺序）=======================
# 场景函数（画背景）可以多次调用；镜头函数（某一句、某个剧情节拍）每个只用一次。
def bg_placeholder(img, t, k=0.0):
    """占位背景：迭代二画风的天空 + 远景城市 + 地面。背景画完立刻 ST.mark(img)，引擎据此做景深和轮廓光"""
    ST.sky(img, t, 'autumn', 0.45 + k * 0.4, 110)
    ST.city(img, 102, 'autumn', ST.sky_key('autumn', 0.45 + k * 0.4))
    ST.ground_fill(img, 110, 'autumn', t * 4, 0.45)
    ST.mark(img)


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

MVX = MV(song, SHOTS, CFG, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE, sections=SECTIONS)   # hd_light / glass 默认开启
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
