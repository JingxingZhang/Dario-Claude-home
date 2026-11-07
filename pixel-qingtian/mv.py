"""《晴天》像素 MV —— 这支片子专属的镜头脚本（原唱：周杰伦）。

故事：长大后的“我”背着吉他在阴雨天回到母校，循着秋千边的小黄花回想学生时代的她；
第二遍副歌真的放晴，“我”放走夹在笔记本里的压花，在阳光下的秋千上弹完吉他 solo。
详见 故事.md / 歌词精读.md / 分镜说明.md。
"""
import math, os, sys
SKILL = os.environ.get('PIXMV_SKILL', '')
sys.path.insert(0, os.path.join(SKILL, 'lib'))
ROOT = os.environ.get('PIXMV_PROJECT', os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *
from charkit import *
from props2 import *
from refine import render_char, refined_sprite
import style as ST
from chars import heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, curtains, R
from engine import Song, MV
import huazi as Z

song = Song(ROOT)
rms, pump, beat_phase, L = song.rms, song.pump, song.beat_phase, song.L

# ======================= ① 视觉方案 =======================
# 曲风：抒情流行摇滚 / 68.5 BPM / 木吉他前奏 + 乐队，副歌放开，尾奏电吉他 solo
#   → 一句一镜、慢推慢移；副歌加大动作和天气；花字小回弹、慢逐字（pop≈1.12, stagger≈0.08）
# 世界：一所普通的中学校园（秋千、走廊、教室、校门、操场、体育馆屋檐），2000 年代初的校服
# 配色随故事时间线变：
#   现在·阴天（灰蓝）→ 回忆·童年（奶油暖黄）→ 回忆·高中午后（暖金）→ 现在·下雨（冷灰蓝）
#   → 回忆·风雨校门（深青）→ 回忆·毕业（橙色黄昏）→ 间奏·雨小（雾灰）→ 现在·雨停（淡青）
#   → 现在·最后一场大雨（深蓝）→ 放晴（晴空蓝 + 小黄花黄）→ 尾奏·午后阳光（暖白）
# 主色：校服白 + 藏青；强调色：小黄花黄（贯穿全片唯一的高饱和色）；暗色：雨天的深青灰
PALETTE = {'navy': (44, 58, 92), 'shirt': (240, 240, 232), 'flower': (255, 206, 40),
           'rain': (70, 92, 112), 'sky': (120, 186, 236), 'warm': (250, 214, 150)}
LYRIC_BASE = dict(pop=1.12, stagger=0.08, float_amp=3)
TITLE_STYLE = dict(pal='yel', size=230, angle=-2, deco=('star', 'note'))

# ======================= ② 角色设计（字符画，迭代二精修） =======================
SKIN = (252, 222, 198)
HAIR = (46, 38, 44)
# —— 长大后的“我”：深橄榄色夹克 + 牛仔裤 + 背上的吉他包（辨识点：吉他包）
ADULT_PAL = {'h': HAIR, 's': SKIN, 'j': (84, 98, 80), 'w': (236, 236, 228), 'p': (70, 88, 128),
             'k': (60, 50, 50), 'g': (40, 36, 44), 'G': (70, 64, 74)}
ADULT_IDLE = '''
......hhhh....
.....hhhhhh...
....hhhhhhhh..
....hssssssh..
....ssssssss..
....ssssssss..
.....ssssss...
gg....ssss....
gGgjjjjwwjjj..
gGgjjjjjwjjjj.
gGgjjjjjjjjjj.
gGgjjjjjjjjjj.
gGgsjjjjjjjjs.
gGg.jjjjjjjj..
gGg.pppppppp..
gGg.ppp..ppp..
gGg.ppp..ppp..
.g..ppp..ppp..
....ppp..ppp..
....kkk..kkk..
'''
ADULT_WAVE = '''
......hhhh..ss
.....hhhhhh.ss
....hhhhhhhhjj
....hssssssjj.
....sssssssj..
....ssssssj...
.....ssssss...
gg....ssss....
gGgjjjjwwjj...
gGgjjjjjwjj...
gGgjjjjjjjj...
gGgjjjjjjjj...
gGgsjjjjjjj...
gGg.jjjjjjjj..
gGg.pppppppp..
gGg.ppp..ppp..
gGg.ppp..ppp..
.g..ppp..ppp..
....ppp..ppp..
....kkk..kkk..
'''
# 坐在秋千上弹吉他（尾奏）：b 琴身 B 面板 o 音孔 d 琴颈
ADULT_PLAY = '''
....hhhh.........
...hhhhhh........
..hhhhhhhh.......
..hssssssh.......
..ssssssss.......
..ssssssss.......
...ssssss........
....ssss.........
..jjjwwjjj.......
.jjjjjwjjjj......
.jjjjjjjjjj......
.jjbbbbjjjsdddddd
.jbBBBBbsddddd...
.bBBBoBBb........
.bBBBBBBb........
..bbbbbbpppp.....
...pppppppppp....
..........ppp....
..........ppp....
..........kkk....
'''
GUITAR_PAL = {'b': (150, 84, 40), 'B': (214, 150, 80), 'o': (50, 30, 20), 'd': (96, 60, 34)}

# —— 学生时代的“我”：白衬衫 + 藏青长裤，头发更短更乱
TEEN_PAL = {'h': (34, 30, 40), 's': SKIN, 'w': (244, 244, 236), 'n': (52, 64, 104), 'k': (50, 44, 48), 'c': (200, 200, 196)}
TEEN_IDLE = '''
.....hhhh....
...hhhhhhh...
...hhhhhhhh..
...hssssssh..
...ssssssss..
...ssssssss..
....ssssss...
.....ssss....
...wwwcwwww..
..wwwwwwwwww.
..wwwwwwwwww.
..swwwwwwwws.
..s.wwwwww.s.
....nnnnnn...
....nnn.nnn..
....nnn.nnn..
....nnn.nnn..
....nnn.nnn..
....kkk.kkk..
'''
TEEN_RUN = '''
......hhhh...
....hhhhhhh..
...hhhhhhhhh.
....hssssssh.
....ssssssss.
....ssssssss.
.....ssssss..
......ssss...
..swwwcwwww..
...wwwwwwwwss
...wwwwwwwww.
...wwwwwwww..
....wwwwww...
....nnnnnnn..
...nnn...nnn.
..nnn.....nn.
.nnn......nn.
kkk.......kk.
..........kk.
'''
TEEN_REACH = '''
.....hhhh.......
...hhhhhhh......
...hhhhhhhh.....
...hssssssh.....
...ssssssss.....
...ssssssss.....
....ssssss......
.....ssss.......
...wwwcwwwwwwwss
..wwwwwwwwwwwwss
..wwwwwwwww.....
..swwwwwwww.....
..s.wwwwww......
....nnnnnn......
....nnn.nnn.....
....nnn.nnn.....
....nnn.nnn.....
....nnn.nnn.....
....kkk.kkk.....
'''
# —— 学生时代的“你”：马尾 + 白衬衫 + 藏青百褶裙，发卡上别着小黄花（y）
GIRL_PAL = {'h': (58, 40, 40), 's': SKIN, 'w': (246, 246, 240), 'n': (52, 64, 104), 'o': (240, 240, 236),
            'k': (70, 46, 46), 'y': (255, 206, 40), 'c': (220, 120, 120)}
GIRL_IDLE = '''
.....hhhhy...
....hhhhhyy..
...hhhhhhhhhh
...hhssssshhh
...hssssssshh
...hssssssshh
....ssssss.h.
.....ssss....
...wwwccwww..
..wwwwwwwwww.
..wwwwwwwwww.
..swwwwwwwws.
..s.nnnnnn.s.
...nnnnnnnn..
...nnnnnnnn..
.....ss.ss...
.....oo.oo...
.....oo.oo...
.....kk.kk...
'''
GIRL_WAVE = '''
.....hhhhy..ss
....hhhhhyy.ss
...hhhhhhhhhww
...hhssssshhw.
...hssssssshw.
...hsssssssh..
....ssssss.h..
.....ssss.....
...wwwccwww...
..wwwwwwwww...
..wwwwwwwww...
..swwwwwwww...
..s.nnnnnn....
...nnnnnnnn...
...nnnnnnnn...
.....ss.ss....
.....oo.oo....
.....oo.oo....
.....kk.kk....
'''
# —— 小时候的“我”：天蓝 T 恤 + 短裤，坐在秋千上
KID_PAL = {'h': (40, 34, 40), 's': SKIN, 't': (120, 186, 236), 'p': (230, 160, 70), 'k': (200, 70, 70)}
KID_SIT = '''
...hhhh...
..hhhhhh..
..hssssh..
..ssssss..
..ssssss..
...ssss...
..tttttt..
.sttttttts
.sttttttts
..pppppp..
..pppppppp
.......ss.
.......kk.
'''

CAST = {
    'adult': dict(name='我·现在', art={'idle': ADULT_IDLE, 'wave': ADULT_WAVE, 'play': ADULT_PLAY},
                  pal={**ADULT_PAL, **GUITAR_PAL}, eye=(5, 4, 3), mth=(5, 6)),
    'teen': dict(name='我·高中', art={'idle': TEEN_IDLE, 'run': TEEN_RUN, 'reach': TEEN_REACH},
                 pal=TEEN_PAL, eye=(4, 4, 3), mth=(4, 6)),
    'girl': dict(name='你·高中', art={'idle': GIRL_IDLE, 'wave': GIRL_WAVE},
                 pal=GIRL_PAL, eye=(5, 4, 3), mth=(5, 6)),
    'kid': dict(name='我·童年', art={'idle': KID_SIT}, pal=KID_PAL, eye=(3, 3, 2), mth=(3, 4)),
}
# 坐姿精灵的五官位置和站姿不同
POSE_FACE = {('adult', 'play'): ((3, 4, 3), (3, 6)), ('adult', 'wave'): ((5, 4, 3), (5, 6)),
             ('teen', 'run'): ((5, 4, 3), (5, 6)), ('girl', 'wave'): ((5, 4, 3), (5, 6))}


def actor(img, who, x, y, pose='idle', face=1, expr='smile', bob=0, ghost=0.0):
    """画一个角色：x,y 脚底中点。ghost>0 时画成半透明的回忆残影。"""
    c = CAST[who]
    art = c['art'].get(pose) or c['art']['idle']
    eye, mth = POSE_FACE.get((who, pose), (c['eye'], c['mth']))
    if ghost <= 0:
        return render_char(img, art, c['pal'], x, y, face, eye, mth, expr, bob)
    tmp = img.copy()
    render_char(tmp, art, c['pal'], x, y, face, eye, mth, expr, bob)
    img.paste(Image.blend(img, tmp, max(0.0, 1 - ghost)))


# —— 贯穿物件：小黄花（花苞 → 盛开 → 少一片 → 压花）
FLOWER_Y = (255, 206, 40)
FLOWER_D = (214, 150, 20)
FLOWER_C = (176, 96, 20)
STEM = (96, 140, 70)


def flower(img, x, y, bloom=1.0, petals=5, lost=(), stem=14, k=1.0, sway=0.0):
    """秋千边的小黄花：x,y 为花茎底部；bloom 0 = 花苞，1 = 盛开；lost = 掉了的花瓣序号"""
    d = ImageDraw.Draw(img)
    tx, ty = x + sway, y - stem
    for i in range(stem):
        yy = y - i
        xx = x + sway * i / max(1, stem)
        d.point((int(xx), int(yy)), fill=STEM)
    d.point((int(x - 1), int(y - stem // 2)), fill=STEM); d.point((int(x - 2), int(y - stem // 2 - 1)), fill=STEM)
    d.point((int(x + 1), int(y - stem // 3)), fill=STEM); d.point((int(x + 2), int(y - stem // 3 - 1)), fill=STEM)
    if bloom < 0.15:
        d.rectangle([tx - 1, ty - 2, tx + 1, ty], fill=FLOWER_D)
        d.point((int(tx), int(ty - 3)), fill=FLOWER_Y)
        return
    r = 1.5 + 2.5 * bloom * k
    for i in range(petals):
        if i in lost:
            continue
        a = -math.pi / 2 + i * 2 * math.pi / petals
        px, py = tx + math.cos(a) * r, ty + math.sin(a) * r
        d.ellipse([px - 1.6 * k, py - 1.6 * k, px + 1.6 * k, py + 1.6 * k], fill=FLOWER_Y)
        d.point((int(px), int(py - 1)), fill=(255, 236, 140))
    d.rectangle([tx - 1, ty - 1, tx + 1, ty + 1], fill=FLOWER_C)


def pressed_flower(img, x, y, k=1.0):
    """夹在笔记本里的压花（扁平、颜色褪一点）"""
    d = ImageDraw.Draw(img)
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5 + 0.3
        px, py = x + math.cos(a) * 3 * k, y + math.sin(a) * 2.2 * k
        d.ellipse([px - 1.5 * k, py - 1.1 * k, px + 1.5 * k, py + 1.1 * k], fill=(236, 196, 80))
    d.point((int(x), int(y)), fill=(150, 96, 40))
    d.line([x, y + 1, x - 2, y + 8], fill=(120, 140, 80))


def notebook(img, x, y, open_k=1.0, with_flower=True):
    """旧笔记本（打开时左页夹着压花，右页有字迹线）"""
    d = ImageDraw.Draw(img)
    if open_k < 0.5:
        d.rectangle([x, y, x + 16, y + 20], fill=(60, 96, 140), outline=(30, 40, 60))
        d.rectangle([x + 3, y + 4, x + 13, y + 7], fill=(236, 230, 210))
        return
    d.rectangle([x - 2, y, x + 34, y + 22], fill=(60, 96, 140))
    d.rectangle([x, y + 1, x + 15, y + 20], fill=(246, 240, 222))
    d.rectangle([x + 17, y + 1, x + 32, y + 20], fill=(246, 240, 222))
    d.line([x + 16, y + 1, x + 16, y + 20], fill=(200, 190, 170))
    for i in range(5):
        d.line([x + 19, y + 4 + i * 3, x + 30, y + 4 + i * 3], fill=(170, 170, 190))
    if with_flower:
        pressed_flower(img, x + 7, y + 9)


def swing(img, x, top, seat_y, ang=0.0, col=(120, 110, 100)):
    """旧秋千：x 为横梁中点；ang 为摆角（弧度）；返回坐板中心坐标"""
    d = ImageDraw.Draw(img)
    d.line([x - 26, top, x + 26, top], fill=(90, 80, 74), width=2)
    d.line([x - 24, top, x - 30, seat_y + 18], fill=(90, 80, 74), width=2)
    d.line([x + 24, top, x + 30, seat_y + 18], fill=(90, 80, 74), width=2)
    L_ = seat_y - top
    sx, sy = x + math.sin(ang) * L_, top + math.cos(ang) * L_
    for dx in (-7, 7):
        d.line([x + dx, top, sx + dx, sy], fill=col)
    d.rectangle([sx - 9, sy, sx + 9, sy + 1], fill=(150, 100, 60))
    return sx, sy


def CAST_SHEET(img, t):
    """角色设定图"""
    img.paste(Image.fromarray(dither_grad(180, 320, (246, 240, 226), (226, 232, 240))), (0, 0))
    draw_text(img, 6, 4, '《晴天》像素 MV · 角色设定', INK)
    bob = int(round(math.sin(t * 2 * math.pi) * 0.6))
    row = 74
    for who, pose, ex, x in [('adult', 'idle', 'smile', 22), ('adult', 'wave', 'happy', 50), ('adult', 'play', 'smile', 82),
                             ('teen', 'idle', 'normal', 124), ('teen', 'run', 'happy', 150), ('teen', 'reach', 'think', 178),
                             ('girl', 'idle', 'smile', 216), ('girl', 'wave', 'happy', 242)]:
        actor(img, who, x, row, pose, 1, ex, bob)
    sx, sy = swing(img, 290, 22, 60, 0.18 * math.sin(t * 6.28))
    actor(img, 'kid', sx, sy + 3, 'idle', 1, 'happy')
    for name, x in (('我·现在', 52), ('我·高中', 150), ('你·高中', 229), ('我·童年', 290)):
        draw_text(img, x - text_w(name) // 2, row + 4, name, INK)
    draw_text(img, 6, 96, '表情', INK)
    for i, ex in enumerate(('normal', 'smile', 'happy', 'think', 'sad', 'shock')):
        actor(img, 'adult', 20 + i * 22, 158, 'idle', 1, ex)
    for i, ex in enumerate(('smile', 'happy', 'blush', 'sad')):
        actor(img, 'girl', 160 + i * 20, 158, 'idle', 1, ex)
    draw_text(img, 238, 96, '小黄花', INK)
    flower(img, 244, 150, 0.0, stem=12)
    flower(img, 258, 150, 1.0, stem=14, sway=math.sin(t * 6.28))
    flower(img, 274, 150, 1.0, lost=(2,), stem=14)
    notebook(img, 282, 128, 1.0)
    for lab, x in (('花苞', 244), ('盛开', 258), ('少一片', 274)):
        pass
    draw_text(img, 238, 154, '花苞→盛开→少一片→压花', INK) if False else None
    palette_strip(img, 6, 170, list(PALETTE.values()), 7)


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
    actor(img, 'adult', 160, 150)


def s_placeholder(img, t, lt, v, i=0):
    """还没设计的句子：保证流程能跑通；交付前必须全部替换"""
    bg_placeholder(img, t, i / max(1, len(song.lines)))
    actor(img, 'adult', 160, 130)
    ptext(img, 160, 30, f'第{i + 1}句', 1)


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


# ======================= ⑤ 每句歌词花字（键用句序号；重复的歌词可以按剧情换配色和重点词）=======================
# pal 底色 / kw 重点词 / kwpal 重点词配色（可为列表）/ kwscale / size / cx cy / angle / deco 贴纸 / pop stagger shake …
CFG = {}

MVX = MV(song, SHOTS, CFG, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE, glass=False)
frame = MVX.frame
DUR = song.dur

# ======================= ⑦ 封面（scripts/cover.py 导出）=======================
COVER_T = None          # 封面表现故事的哪一刻（全片秒）


def COVER_3X4(img, t):
    """交付封面（3:4 竖版，1080×1440）的像素层（180×240）：标题、原唱、标签、署名由 cover.py 自动加。
    构图：上方 0–55 行留给标题，主画面 55–195 行，底部 195–240 行留给原唱和署名。
    可以用 cover.portrait_from(横版场景) 把一张 320×180 场景裁成竖版，再摆角色；也可以登记玻璃（g* 组件）。"""
    img.paste(Image.fromarray(dither_grad(240, 180, PALETTE['bg'], PALETTE['ink'])), (0, 0))
    actor(img, 'adult', 90, 190)
