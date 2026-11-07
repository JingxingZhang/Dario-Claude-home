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
from chars import heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, curtains, R, calendar
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


# ======================= ③ 场景工具（可以多次调用） =======================
from scenes_common import rain as _rain_unused  # noqa: F401  (不用霓虹雨；本片自己画雨)
from cover import portrait_from

HZ = 100          # 户外地平线
FEET = 116        # 人物脚底
SWX, SWTOP, SWSEAT = 214, 50, 96   # 秋千：横梁中点、横梁高度、坐板高度
FLX = 246         # 秋千边小黄花的位置

# 天色：(天顶, 中段, 地平线, 调色键, 地面上, 地面下)
MOODS = {
    'overcast': ((132, 146, 164), (166, 176, 190), (202, 206, 210), None, (150, 152, 150), (176, 176, 170)),
    'child':    ((236, 200, 150), (246, 222, 176), (252, 238, 206), 'gold', (214, 196, 160), (232, 218, 190)),
    'gold':     ((206, 164, 122), (238, 196, 140), (252, 226, 180), 'gold', (206, 184, 150), (226, 208, 176)),
    'rain':     ((92, 106, 124), (120, 134, 150), (152, 162, 172), None, (108, 116, 122), (130, 138, 144)),
    'wind':     ((66, 88, 108), (96, 116, 132), (132, 146, 156), None, (100, 110, 116), (122, 130, 134)),
    'storm':    ((30, 40, 58), (48, 60, 80), (74, 86, 102), 'night', (58, 66, 74), (76, 84, 92)),
    'dusk':     ((120, 96, 150), (230, 136, 96), (250, 198, 140), 'gold', (196, 150, 118), (214, 176, 140)),
    'after':    ((166, 176, 184), (192, 198, 202), (216, 218, 216), None, (160, 164, 160), (182, 186, 180)),
    'clearing': ((146, 180, 208), (186, 206, 222), (224, 230, 226), 'dawn', (176, 182, 172), (198, 202, 190)),
    'clear':    ((84, 146, 224), (150, 196, 240), (236, 232, 214), 'day', (150, 196, 110), (176, 214, 128)),
    'warm':     ((104, 140, 210), (200, 190, 210), (252, 216, 168), 'gold', (170, 190, 110), (198, 208, 140)),
}


def mixm(a, b, k):
    """两种天色之间插值（转场用）"""
    A, B = MOODS[a], MOODS[b]
    return tuple(lerpc(x, y, k) if isinstance(x, tuple) else (y if k > 0.5 else x) for x, y in zip(A, B))


def M(m):
    return MOODS[m] if isinstance(m, str) else m


def sky(img, t, m, hz=HZ, clouds=3, sun=None, dark_clouds=False):
    c0, c1, c2, g = M(m)[:4]
    ST.set_grade(g)
    img.paste(Image.fromarray(ST.grad3(hz, W, c0, c1, c2)), (0, 0))
    d = ImageDraw.Draw(img)
    if sun is not None:
        sx, sy, k = sun
        ST.glow_np(img, sx, sy, 60, (255, 244, 210), 0.5 * k)
        d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=lerpc(c1, (255, 248, 226), k))
    base = lerpc(c2, (255, 255, 255), 0.55) if not dark_clouds else lerpc(c0, c1, 0.6)
    shade = lerpc(c1, c2, 0.4) if not dark_clouds else lerpc(c0, (20, 24, 34), 0.3)
    light = lerpc(base, (255, 255, 255), 0.4)
    for i in range(clouds):
        cx = (hsh(i, 41) * 360 + t * (2 + i)) % 380 - 30
        ST.cloud(img, cx, 12 + i * 12, 0.9 + 0.3 * i, base, shade, light)


def school(img, m, base=HZ, x0=0, x1=W, h=44, lights=False):
    """远处的教学楼：三层、一排排窗、楼顶的钟"""
    d = ImageDraw.Draw(img)
    c0, c1, c2 = M(m)[:3]
    wall = lerpc(lerpc(c2, (232, 224, 210), 0.5), c1, 0.25)
    R(d, x0, base - h, x1 - x0, h, wall)
    R(d, x0, base - h, x1 - x0, 2, lerpc(wall, (120, 110, 110), 0.4))
    win = lerpc(c1, (90, 110, 140), 0.45) if not lights else (255, 222, 150)
    for fl in range(3):
        y = base - h + 6 + fl * 13
        for x in range(x0 + 6, x1 - 8, 14):
            R(d, x, y, 8, 7, win)
            R(d, x, y, 8, 1, lerpc(win, (255, 255, 255), 0.3))
    cx = (x0 + x1) // 2
    R(d, cx - 8, base - h - 10, 16, 10, wall)
    d.ellipse([cx - 4, base - h - 8, cx + 4, base - h], fill=(244, 240, 230), outline=(110, 100, 100))


def ground(img, m, hz=HZ, wet=0.0, t=0.0, track=False):
    d = ImageDraw.Draw(img)
    top, bot = M(m)[4], M(m)[5]
    img.paste(Image.fromarray(ST.grad3(H - hz, W, top, lerpc(top, bot, 0.5), bot, 0.4, 10)), (0, hz))
    R(d, 0, hz, W, 1, lerpc(top, (80, 80, 80), 0.3))
    if track:
        R(d, 0, hz + 18, W, 12, lerpc((176, 96, 74), top, 0.35))
        for y in (hz + 21, hz + 26):
            d.line([(0, y), (W, y)], fill=(236, 230, 220))
    if wet > 0:
        for i in range(5):
            px = int(hsh(i, 61) * 280) + 10; py = hz + 8 + int(hsh(i, 62) * 50)
            w = 18 + int(hsh(i, 63) * 20)
            d.ellipse([px, py, px + w, py + 4], fill=lerpc(top, M(m)[1], 0.6 * wet))


def swing_set(img, ang=0.0, rope=(120, 110, 100)):
    return swing(img, SWX, SWTOP, SWSEAT, ang, rope)


def yard(img, t, m, ang=0.0, bloom=0.0, lost=(), wet=0.0, flower_on=True, clouds=3, sun=None, dark=False, sway=None):
    """操场边的秋千和小黄花（全片的“家”）"""
    sky(img, t, m, HZ, clouds, sun, dark)
    school(img, m, HZ - 2, 0, 170)
    ground(img, m, HZ, wet, t)
    ST.mark(img)
    sx, sy = swing_set(img, ang)
    if flower_on:
        flower(img, FLX, FEET - 2, bloom, lost=lost, stem=12, sway=math.sin(t * 2) if sway is None else sway)
    return sx, sy


def classroom(img, t, m, rain_k=0.0, fog=0.0, board_text=None, empty=False):
    """教室内：左边黑板，右边窗（窗外是这一刻的天色），一排课桌"""
    d = ImageDraw.Draw(img)
    c0, c1, c2 = M(m)[:3]
    ST.set_grade(M(m)[3])
    wall = lerpc((232, 222, 200), c2, 0.25)
    R(d, 0, 0, W, 110, wall)
    R(d, 0, 92, W, 18, lerpc(wall, (150, 170, 150), 0.35))
    img.paste(Image.fromarray(ST.grad3(70, W, lerpc(wall, (140, 120, 100), 0.3), lerpc(wall, (170, 150, 120), 0.3), (196, 172, 136), 0.5, 8)), (0, 110))
    R(d, 12, 16, 104, 46, (40, 70, 60)); R(d, 10, 14, 108, 2, (120, 90, 60)); R(d, 10, 62, 108, 3, (120, 90, 60))
    if board_text:
        draw_text(img, 18, 30, board_text, (240, 240, 230))
    wx, wy, ww, wh = 196, 14, 112, 66
    img.paste(Image.fromarray(ST.grad3(wh, ww, c0, c1, c2)), (wx, wy))
    for i in range(2):
        cx = (hsh(i, 5) * 160 + t * 3) % 150 - 20
        ST.cloud(img, wx + cx, wy + 14 + i * 14, 0.7, lerpc(c2, (255, 255, 255), 0.5), lerpc(c1, c2, 0.4), (255, 255, 255))
    if rain_k > 0:
        for i in range(int(40 * rain_k)):
            x = wx + int((hsh(i, 1) * ww - t * 20) % ww); y = wy + int((hsh(i, 3) * wh + t * 120) % wh)
            d.line([(x, y), (x - 1, min(wy + wh - 1, y + 4))], fill=lerpc(c2, (230, 236, 246), 0.6))
    if fog > 0:
        a = np.asarray(img).astype(float)
        a[wy:wy + wh, wx:wx + ww] = a[wy:wy + wh, wx:wx + ww] * (1 - fog) + np.array((222, 226, 230)) * fog
        img.paste(Image.fromarray(a.astype(np.uint8)))
        d = ImageDraw.Draw(img)
    R(d, wx - 3, wy - 3, ww + 6, 3, (226, 226, 220)); R(d, wx - 3, wy + wh, ww + 6, 4, (210, 210, 204))
    R(d, wx + ww // 2 - 1, wy, 3, wh, (226, 226, 220)); R(d, wx - 3, wy, 3, wh, (226, 226, 220)); R(d, wx + ww, wy, 3, wh, (226, 226, 220))
    ST.mark(img)


def desk(img, x, y=FEET - 10, w=30):
    d = ImageDraw.Draw(img)
    R(d, x - w // 2, y, w, 4, (176, 128, 80)); R(d, x - w // 2, y, w, 1, (210, 164, 110))
    R(d, x - w // 2 + 2, y + 4, 2, 10, (110, 90, 80)); R(d, x + w // 2 - 4, y + 4, 2, 10, (110, 90, 80))


def corridor(img, t, m, scroll=0.0, clock_ang=None):
    """走廊（侧面）：上面一排窗、下面是地砖"""
    d = ImageDraw.Draw(img)
    c0, c1, c2 = M(m)[:3]
    ST.set_grade(M(m)[3])
    wall = lerpc((226, 218, 200), c2, 0.3)
    R(d, 0, 0, W, 104, wall)
    for k in range(-1, 7):
        x = int(k * 60 - scroll % 60)
        img.paste(Image.fromarray(ST.grad3(40, 40, c0, c1, c2)), (x + 10, 18))
        R(d, x + 8, 16, 44, 2, (236, 236, 230)); R(d, x + 8, 58, 44, 3, (236, 236, 230)); R(d, x + 29, 18, 2, 40, (236, 236, 230))
        R(d, x + 56, 0, 4, 104, lerpc(wall, (150, 140, 130), 0.3))
    R(d, 0, 86, W, 18, lerpc(wall, (140, 160, 150), 0.4))
    img.paste(Image.fromarray(ST.grad3(H - 104, W, (190, 180, 168), (176, 166, 156), (160, 150, 142), 0.5, 8)), (0, 104))
    for i in range(12):
        x = int(i * 30 - scroll % 30)
        d.line([(x, 104), (x - 18, H)], fill=(150, 140, 132))
    if clock_ang is not None:
        cx, cy = 160, 8
        d.ellipse([cx - 7, cy - 6, cx + 7, cy + 8], fill=(246, 244, 236), outline=(90, 80, 80))
        d.line([(cx, cy + 1), (cx + int(5 * math.sin(clock_ang)), cy + 1 - int(5 * math.cos(clock_ang)))], fill=(40, 30, 30))
        d.line([(cx, cy + 1), (cx + int(3 * math.sin(clock_ang / 12)), cy + 1 - int(3 * math.cos(clock_ang / 12)))], fill=(40, 30, 30))
    ST.mark(img)


def gate(img, t, m, wet=0.0, dark=False):
    """校门：两根门柱 + 横梁，后面是教学楼"""
    sky(img, t, m, HZ, 3, None, dark)
    school(img, m, HZ - 2, 130, 320)
    ground(img, m, HZ, wet, t)
    d = ImageDraw.Draw(img)
    pc = lerpc((176, 168, 160), M(m)[1], 0.25)
    for x in (34, 286):
        R(d, x - 7, 30, 14, HZ - 30 + 14, pc); R(d, x - 8, 28, 16, 3, lerpc(pc, (90, 80, 80), 0.4))
    R(d, 27, 30, 266, 6, lerpc(pc, (130, 120, 110), 0.3))
    ST.mark(img)


def field(img, t, m, sun=None, dark=False, eaves=False):
    sky(img, t, m, HZ - 8, 3, sun, dark)
    school(img, m, HZ - 10, 40, 260, 34)
    ground(img, m, HZ - 8, 0.0, t, track=True)
    if eaves:
        d = ImageDraw.Draw(img)
        R(d, 0, 0, W, 16, (70, 74, 84)); R(d, 0, 16, W, 3, (50, 54, 62))
        R(d, 8, 16, 6, 104, (90, 92, 100)); R(d, 300, 16, 6, 104, (90, 92, 100))
        R(d, 0, FEET - 2, W, 6, (120, 120, 124))
    ST.mark(img)


def rain_fx(img, t, k, slant=2, col=(222, 230, 242), ground_y=FEET):
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    for i in range(int(190 * k)):
        sp = 230 + hsh(i, 2) * 120
        x = (hsh(i, 1) * (W + 60) - t * 30 * slant) % (W + 60) - 30
        y = (hsh(i, 3) * H + t * sp) % (H + 20) - 10
        L_ = 5 + int(hsh(i, 4) * 4)
        d.line([(int(x), int(y)), (int(x - slant), int(y + L_))], fill=col if i % 3 else lerpc(col, (150, 160, 180), 0.4))
        if i % 6 == 0:
            ph = (t * 2 + hsh(i, 9)) % 1
            if ph < 0.25:
                sx = int(hsh(i, 8) * W); sy = ground_y - 6 + int(hsh(i, 7) * 14)
                r = int(1 + ph * 10)
                d.point((sx - r, sy), fill=col); d.point((sx + r, sy), fill=col)


def wind_fx(img, t, k, petals=0, col=(240, 244, 250)):
    d = ImageDraw.Draw(img)
    for i in range(int(14 * k)):
        y = int(hsh(i, 21) * 110) + 4
        x = int((hsh(i, 22) * 400 + t * (260 + hsh(i, 23) * 140)) % 420) - 60
        L_ = 10 + int(hsh(i, 24) * 22)
        d.line([(x, y), (x + L_, y + 1)], fill=col)
    for i in range(int(petals)):
        x = int((hsh(i, 31) * 380 + t * (90 + hsh(i, 32) * 60)) % 380) - 30
        y = int(hsh(i, 33) * 110 + math.sin(t * 3 + i) * 8)
        petal(img, x, y, i)


def petal(img, x, y, i=0):
    d = ImageDraw.Draw(img)
    if int(i) % 2:
        d.point((x, y), fill=FLOWER_Y); d.point((x + 1, y), fill=FLOWER_Y); d.point((x, y + 1), fill=FLOWER_D)
    else:
        d.point((x, y), fill=FLOWER_Y); d.point((x, y + 1), fill=(255, 236, 140)); d.point((x + 1, y + 1), fill=FLOWER_D)


def petals_fall(img, t, n, x0=0, x1=W, top=-6, bot=FEET, speed=1.0, seed=0):
    for i in range(n):
        ph = (t * (0.18 + hsh(i, 9, seed) * 0.08) * speed + hsh(i, 7, seed)) % 1
        x = int(x0 + hsh(i, 8, seed) * (x1 - x0) + math.sin(t * 1.6 + i) * 10)
        y = int(top + ph * (bot - top))
        petal(img, x, y, i + int(t * 4))


def note(img, x, y, col=(250, 248, 240), edge=(60, 50, 70)):
    d = ImageDraw.Draw(img)
    d.ellipse([x - 3, y - 1, x + 2, y + 3], fill=edge); d.ellipse([x - 2, y, x + 1, y + 2], fill=col)
    d.line([(x + 2, y + 1), (x + 2, y - 8)], fill=edge)
    d.line([(x + 2, y - 8), (x + 5, y - 5)], fill=edge)


def beat_notes(img, t, lt, x, y, cols=((255, 206, 40), (250, 248, 240), (150, 200, 255)), rise=40, life=1.8):
    """每拍从 (x,y) 冒出一个音符往上飘"""
    for j in range(5):
        bi = np.searchsorted(song.beats, t) - 1 - j
        if bi < 0:
            break
        bt = song.beats[bi]
        dt = t - bt
        if dt > life or bt < t - lt:
            continue
        nx = x + int(math.sin(bi * 1.7) * 18 + dt * 6 * (1 if bi % 2 else -1))
        ny = int(y - dt / life * rise)
        note(img, nx, ny, cols[bi % len(cols)])


def memory(img, k=0.18, col=(255, 222, 160)):
    """回忆滤镜：暖色 + 四角暗一点"""
    img.paste(tint(img, col, k))
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    v = (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a *= (1 - 0.18 * np.clip(v - 0.5, 0, 1))[..., None]
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)))


def seated(img, who, x, seat_y, expr='smile', face=1, bob=0):
    """坐在秋千 / 椅子上：上半身照常画，腿从坐板垂下"""
    c = CAST[who]
    art = c['art']['idle'].strip('\n').split('\n')
    h = len(art) * 2 + 2
    hip = {'adult': 14, 'teen': 13, 'girl': 12}[who]
    feet = seat_y - hip * 2 + h - 1 + bob
    tmp = img.copy()
    actor(tmp, who, x, feet, 'idle', face, expr)
    img.paste(tmp.crop((0, 0, W, seat_y + 1)), (0, 0))
    d = ImageDraw.Draw(img)
    pal = c['pal']
    leg = pal.get('p') or pal.get('n')
    for dx in (-4, 1):
        if who == 'girl':
            R(d, x + dx, seat_y + 1, 3, 3, SKIN); R(d, x + dx, seat_y + 4, 3, 4, pal['o']); R(d, x + dx, seat_y + 8, 4, 2, pal['k'])
        else:
            R(d, x + dx, seat_y + 1, 3, 8, leg); R(d, x + dx, seat_y + 9, 4, 2, pal['k'])


def flower_big(img, cx, cy, scale, bloom=1.0, lost=(), stem=14, sway=0.0):
    """放大的小黄花（特写用）：先画小图再最近邻放大，保持像素颗粒"""
    tmp = Image.new('RGB', (24, 26), (255, 0, 255))
    flower(tmp, 12, 25, bloom, lost=lost, stem=stem, sway=sway)
    big = tmp.resize((24 * scale, 26 * scale), Image.NEAREST)
    m = Image.fromarray((np.any(np.asarray(big) != (255, 0, 255), axis=2) * 255).astype(np.uint8))
    img.paste(big, (int(cx - 12 * scale), int(cy - 25 * scale)), m)


def pressed_big(img, cx, cy, scale):
    tmp = Image.new('RGB', (14, 14), (255, 0, 255))
    pressed_flower(tmp, 7, 5)
    big = tmp.resize((14 * scale, 14 * scale), Image.NEAREST)
    m = Image.fromarray((np.any(np.asarray(big) != (255, 0, 255), axis=2) * 255).astype(np.uint8))
    img.paste(big, (int(cx - 7 * scale), int(cy - 5 * scale)), m)


def umbrella(img, x, top, col=(250, 214, 60), closed=False):
    d = ImageDraw.Draw(img)
    if closed:
        d.polygon([(x, top), (x - 2, top + 14), (x + 2, top + 14)], fill=col)
        d.line([(x, top + 14), (x, top + 22)], fill=(80, 70, 70))
        return
    d.pieslice([x - 14, top, x + 14, top + 16], 180, 360, fill=col)
    for k in (-7, 0, 7):
        d.line([(x, top), (x + k * 2, top + 8)], fill=lerpc(col, (0, 0, 0), 0.2))
    d.line([(x, top + 8), (x, top + 26)], fill=(80, 70, 70))


def flash(img, k, col=(255, 255, 255)):
    if k > 0:
        img.paste(tint(img, col, min(1.0, k)))


def big_book(img, t, title=None, pic='two', page_col=(246, 238, 216), flower_on=True):
    """全屏翻开的书 / 笔记本"""
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (110, 84, 70))
    R(d, 24, 8, 272, 108, (70, 96, 140))
    R(d, 28, 10, 130, 104, page_col); R(d, 162, 10, 130, 104, page_col)
    R(d, 158, 10, 4, 104, lerpc(page_col, (120, 100, 80), 0.3))
    for i in range(6):
        d.line([(172, 40 + i * 10), (280, 40 + i * 10)], fill=lerpc(page_col, (120, 120, 160), 0.35))
    if title:
        draw_text(img, 172, 20, title, (44, 58, 92))
    ST.set_grade('gold')


# ======================= ③ 镜头（按 故事.md 的剧情顺序；每个函数只用一次） =======================
def walk_bob(lt, sp=6.0):
    return int(abs(math.sin(lt * sp)) * 1.5)


# —— 前奏：阴天，长大的“我”回到母校
def s_title(img, t, lt, v):
    gate(img, t, 'overcast')
    flower(img, 300, FEET - 2, 0.0, stem=10, sway=math.sin(t * 2))
    actor(img, 'adult', 150, FEET, 'idle', 1, 'normal')
    wind_fx(img, t, 0.4)


def s_intro_walk(img, t, lt, v):
    yard(img, t, 'overcast', 0.12 * math.sin(t * 1.6))
    x = lerp(40, FLX - 20, ease(seg(lt, 0.0, 12.0)))
    pose_expr = 'normal' if lt < 13 else 'think'
    actor(img, 'adult', x, FEET, 'idle', 1, pose_expr, walk_bob(lt) if lt < 12 else 0)
    if lt > 14:
        ptext(img, FLX, FEET - 32, '?', 1)
    wind_fx(img, t, 0.3)


# —— 主歌一 A：花开，花瓣飘过童年，秋千晃回现在
def s_bloom(img, t, lt, v):
    k = seg(lt, 0.0, 2.6)
    yard(img, t, mixm('overcast', 'child', k), 0.1 * math.sin(t * 1.6), flower_on=False)
    a = np.asarray(img).astype(float)
    img.paste(Image.fromarray((a * 0.7 + np.array(M(mixm('overcast', 'child', k))[2]) * 0.3).astype(np.uint8)))
    flower_big(img, 160, 108, 4, ease(seg(lt, 0.2, 1.4)), sway=math.sin(t * 2) * 0.6)
    sfx(img, 206, 30, '叮', t, t - lt + 0.35, dur=1.6, pal='yel', scale=1)
    if lt > 1.4:
        for i in range(6):
            ph = (lt - 1.4) * 0.6 + i * 0.15
            sparkle(img, int(160 + math.cos(i * 1.05 + lt) * (24 + ph * 10)), int(66 + math.sin(i * 1.05 + lt) * 16), 2)


def s_petal_years(img, t, lt, v):
    d = ImageDraw.Draw(img)
    img.paste(Image.fromarray(ST.grad3(H, W, (246, 226, 186), (250, 236, 206), (252, 244, 226))), (0, 0))
    ST.set_grade('gold')
    panels = [(14, 'pram'), (116, 'slide'), (218, 'gate')]
    for j, (x, kind) in enumerate(panels):
        a = seg(lt, j * 0.9, j * 0.9 + 0.5)
        if a <= 0:
            continue
        y0 = 22 + int((1 - ease(a)) * 10)
        R(d, x - 2, y0 - 2, 92, 72, (120, 96, 80)); R(d, x, y0, 88, 68, (252, 240, 214))
        if kind == 'pram':
            d.pieslice([x + 24, y0 + 22, x + 56, y0 + 50], 180, 300, fill=(140, 180, 220))
            R(d, x + 24, y0 + 36, 34, 12, (140, 180, 220)); d.ellipse([x + 26, y0 + 48, x + 34, y0 + 56], fill=(60, 60, 70)); d.ellipse([x + 48, y0 + 48, x + 56, y0 + 56], fill=(60, 60, 70))
        elif kind == 'slide':
            d.line([(x + 20, y0 + 58), (x + 60, y0 + 22)], fill=(240, 120, 90), width=4)
            R(d, x + 60, y0 + 22, 3, 36, (120, 120, 140)); R(d, x + 66, y0 + 22, 3, 36, (120, 120, 140))
            for k in range(4):
                R(d, x + 60, y0 + 28 + k * 8, 9, 1, (120, 120, 140))
        else:
            R(d, x + 14, y0 + 20, 8, 40, (176, 168, 160)); R(d, x + 66, y0 + 20, 8, 40, (176, 168, 160)); R(d, x + 14, y0 + 20, 60, 5, (150, 140, 130))
        R(d, x, y0 + 60, 88, 8, (220, 200, 160))
    px = lerp(-10, 330, seg(lt, 0.2, 3.4)); py = 60 + math.sin(lt * 3) * 18
    for k in range(3):
        petal(img, int(px - k * 2), int(py + k), k)


def s_kid_swing(img, t, lt, v):
    ang = 0.45 * math.sin(lt * 2 * math.pi / 1.76)
    sx, sy = yard(img, t, 'child', ang, bloom=0.0)
    actor(img, 'kid', sx, sy + 3, 'idle', 1, 'happy')
    memory(img, 0.12)


def s_swing_grow(img, t, lt, v):
    k = seg(lt, 0, 3.6)
    m = mixm('child', 'gold', k * 2) if k < 0.5 else mixm('gold', 'overcast', (k - 0.5) * 2)
    ang = 0.42 * math.sin(lt * 2 * math.pi / 1.76) * (1 - 0.6 * k)
    sx, sy = yard(img, t, m, ang, bloom=0.0)
    who = 'kid' if lt < 1.25 else ('teen' if lt < 2.5 else 'adult')
    if who == 'kid':
        actor(img, 'kid', sx, sy + 3, 'idle', 1, 'happy')
    else:
        seated(img, who, int(sx), int(sy), 'smile' if who == 'teen' else 'normal')
    if abs(lt - 1.25) < 0.12 or abs(lt - 2.5) < 0.12:
        flash(img, 0.5)


def s_hum1(img, t, lt, v):
    sx, sy = yard(img, t, 'overcast', 0.06 * math.sin(t * 1.6), bloom=0.0, sway=pump(t) * 2)
    seated(img, 'adult', int(sx), int(sy), 'smile')
    beat_notes(img, t, lt, int(sx) + 6, int(sy) - 34)


def s_hum2(img, t, lt, v):
    k = seg(lt, 0.0, 3.2)
    sky(img, t, 'overcast', H, 3)
    d = ImageDraw.Draw(img)
    ST.mark(img)
    for i in range(10):
        nx = 40 + i * 26; ny = int(150 - seg(lt, i * 0.25, i * 0.25 + 1.8) * 130)
        if seg(lt, i * 0.25, 9) > 0:
            note(img, nx, ny, ((255, 206, 40), (250, 248, 240), (150, 200, 255))[i % 3])
    if lt > 2.7:
        sfx(img, 160, 54, '叮铃铃', t, t - lt + 2.7, dur=1.0, pal='yel', scale=1, jitter=2)
        flash(img, seg(lt, 3.0, 3.3) * 0.8, (255, 236, 190))


# —— 主歌一 B：高中午后
def s_window_sky(img, t, lt, v):
    classroom(img, t, 'gold')
    desk(img, 160); desk(img, 250)
    seated(img, 'teen', 250, FEET - 12, 'think', 1)
    desk(img, 250)
    d = ImageDraw.Draw(img)
    for i in range(4):
        d.line([(240 + i * 3, FEET - 11), (240 + i * 3, FEET - 8)], fill=(60, 50, 50))
    beat_notes(img, t, lt, 258, 74, rise=24, life=1.4)
    memory(img, 0.14)


def s_petal_hair(img, t, lt, v):
    classroom(img, t, 'gold')
    seated(img, 'girl', 150, FEET - 12, 'smile', 1)
    desk(img, 150)
    seated(img, 'teen', 214, FEET - 12, 'blush' if lt > 2.4 else 'normal', -1)
    desk(img, 214)
    if lt < 1.4:
        px, py = 300 - lt * 10, 40 + math.sin(lt * 5) * 2
    else:
        u = ease(seg(lt, 1.4, 2.6))
        px, py = lerp(286, 156, u), lerp(40, 66, u) + math.sin(lt * 4) * 4 * (1 - u)
    petal(img, int(px), int(py))
    memory(img, 0.14)


def s_skip_class(img, t, lt, v):
    corridor(img, t, 'gold', scroll=lt * 90, clock_ang=lt * 9)
    b = walk_bob(lt, 10)
    actor(img, 'girl', 150, FEET + b, 'idle', 1, 'happy')
    actor(img, 'teen', 178, FEET + (1 - b), 'run', 1, 'happy')
    if lt > 0.3:
        sys_msg(img, 160, 24, '逃课警告！', (220, 70, 80))
    memory(img, 0.12)


def s_flower_fall(img, t, lt, v):
    ang = 0.22 * math.sin(lt * 2 * math.pi / 1.76)
    sx, sy = yard(img, t, 'gold', ang, bloom=1.0)
    seated(img, 'girl', int(sx), int(sy), 'happy')
    actor(img, 'teen', int(sx) - 26, FEET, 'idle', 1, 'happy')
    petals_fall(img, t, 26)
    memory(img, 0.14)


# —— 主歌一 C：回到现在
def s_fog_window(img, t, lt, v):
    d = ImageDraw.Draw(img)
    ST.set_grade(None)
    R(d, 0, 0, W, H, (150, 156, 160))
    R(d, 0, 0, W, 8, (120, 126, 132))
    img.paste(Image.fromarray(ST.grad3(78, 190, (96, 100, 108), (120, 124, 130), (140, 142, 146))), (20, 16))
    for i in range(5):
        R(d, 30 + i * 36, 66, 26, 4, (110, 96, 84))
    a = np.asarray(img).astype(float)
    fog = 0.55 + 0.25 * seg(lt, 0, 3)
    a[16:94, 20:210] = a[16:94, 20:210] * (1 - fog) + np.array((214, 218, 222)) * fog
    img.paste(Image.fromarray(a.astype(np.uint8)))
    d = ImageDraw.Draw(img)
    R(d, 16, 12, 198, 4, (230, 230, 226)); R(d, 16, 94, 198, 5, (210, 210, 206)); R(d, 113, 16, 4, 78, (230, 230, 226))
    R(d, 16, 16, 4, 78, (230, 230, 226)); R(d, 210, 16, 4, 78, (230, 230, 226))
    R(d, 0, 99, W, H, (128, 132, 136))
    ST.mark(img)
    if lt > 1.4:
        hx, hy = 186, 52
        d.ellipse([hx - 5, hy - 4, hx + 5, hy + 6], fill=(170, 176, 182))
        for k in range(4):
            R(d, hx - 5 + k * 3, hy - 10, 2, 7, (170, 176, 182))
    actor(img, 'adult', 236, FEET, 'idle', -1, 'sad')


def s_rain_start(img, t, lt, v):
    yard(img, t, 'rain', 0.05 * math.sin(t), bloom=1.0, wet=seg(lt, 0, 1.6), dark=True)
    cloud_face(img, 70, 22, 'sad', (200, 206, 214))
    actor(img, 'adult', 150, FEET, 'idle', 1, 'think')
    rain_fx(img, t, 0.15 + 0.35 * seg(lt, 0.2, 1.6))
    sfx(img, 230, 30, '沙沙', t, t - lt + 0.3, dur=1.4, pal='cyan', scale=1)


def s_rain_bathe(img, t, lt, v):
    yard(img, t, 'rain', 0.05 * math.sin(t), bloom=1.0, wet=1.0, dark=True)
    g = 0.55 + 0.4 * abs(math.sin(lt * 2.2))
    if 1.0 < lt < 2.6:
        actor(img, 'teen', 90, FEET, 'idle', 1, 'happy', ghost=g)
        actor(img, 'girl', 112, FEET, 'idle', -1, 'happy', ghost=g)
    actor(img, 'adult', 170, FEET, 'idle', 1, 'blush' if lt > 0.8 else 'normal')
    umbrella(img, 184, FEET - 46 if lt < 0.8 else FEET - 28, (90, 110, 140), closed=lt > 0.8)
    rain_fx(img, t, 0.6)


def s_notebook(img, t, lt, v):
    field(img, t, 'rain', eaves=True, dark=True)
    rain_fx(img, t, 0.7, ground_y=FEET)
    actor(img, 'adult', 80, FEET, 'idle', 1, 'smile')
    k = ease(seg(lt, 0.4, 1.4))
    if k > 0:
        d = ImageDraw.Draw(img)
        bx, by = 120 + int((1 - k) * 20), 26
        R(d, bx - 4, by - 4, 128, 82, (40, 44, 52))
        R(d, bx, by, 120, 74, (70, 96, 140))
        R(d, bx + 4, by + 3, 54, 68, (246, 240, 222)); R(d, bx + 62, by + 3, 54, 68, (246, 240, 222))
        for i in range(6):
            d.line([(bx + 68, by + 14 + i * 9), (bx + 110, by + 14 + i * 9)], fill=(170, 170, 190))
        pressed_big(img, bx + 31, by + 26, 3)
    stamp(img, 270, 98, '还留着', t, t - lt + 3.0, col=(230, 170, 40), scale=1)


def s_ask_back(img, t, lt, v):
    gate(img, t, 'wind', dark=True)
    actor(img, 'teen', 128, FEET, 'idle', 1, 'think' if int(lt * 3) % 2 else 'normal')
    actor(img, 'girl', 176, FEET, 'idle', 1, 'normal')
    if lt > 0.4:
        say(img, 96, 54, '……', t, t - lt + 0.4, tail='l')
    memory(img, 0.08, (180, 200, 220))


def s_choice(img, t, lt, v):
    gate(img, t, 'wind', dark=True)
    actor(img, 'teen', 128, FEET, 'idle', 1, 'think')
    actor(img, 'girl', 176, FEET, 'idle', 1, 'normal')
    sel = int(lt * 1.7) % 2
    popup(img, 86, 22, '心里的问题', '你会等待还是离开？', btns=('等待', '离开'), sel=sel, pressed=False, w=150)
    memory(img, 0.08, (180, 200, 220))


# —— 副歌一（回忆）：风雨校门 → 毕业
def s_reach(img, t, lt, v):
    gate(img, t, 'wind', dark=True)
    wind_fx(img, t, 1.0, petals=6)
    tx = lerp(100, 128, ease(seg(lt, 0.5, 4.0)))
    actor(img, 'teen', tx, FEET, 'reach', 1, 'think')
    actor(img, 'girl', 182, FEET, 'idle', 1, 'normal')
    d = ImageDraw.Draw(img)
    jx = int(math.sin(t * 30) * 1)
    d.point((180 + jx, FEET - 40), fill=FLOWER_Y); d.point((181 + jx, FEET - 40), fill=FLOWER_Y)
    memory(img, 0.08, (180, 200, 220))


def s_rain_grows(img, t, lt, v):
    gate(img, t, 'wind', wet=seg(lt, 0, 2), dark=True)
    cloud_face(img, 160, 18, 'sad' if lt < 1.6 else 'scream', (150, 160, 176))
    actor(img, 'teen', 128, FEET, 'reach', 1, 'shock')
    actor(img, 'girl', 182, FEET, 'idle', 1, 'sad')
    rain_fx(img, t, 0.3 + 0.7 * seg(lt, 0, 3), slant=4)
    sfx(img, 250, 40, '哗啦', t, t - lt + 0.6, dur=1.6, pal='cyan', scale=1, jitter=2)
    memory(img, 0.06, (180, 200, 220))


def s_cant_see(img, t, lt, v):
    gate(img, t, 'storm', wet=1.0, dark=True)
    u = seg(lt, 0.2, 3.6)
    gx = lerp(182, 262, u)
    actor(img, 'girl', gx, FEET, 'idle', 1, 'sad', walk_bob(lt), ghost=u * 0.9)
    if u < 0.85:
        umbrella(img, int(gx + 4), FEET - 50, (250, 214, 60))
    actor(img, 'teen', 110, FEET, 'idle', 1, 'sad')
    rain_fx(img, t, 1.0, slant=4)


def s_distance(img, t, lt, v):
    gate(img, t, 'storm', wet=1.0, dark=True)
    actor(img, 'teen', 160, FEET, 'idle', 1, 'sad')
    rain_fx(img, t, 0.9, slant=3)
    val = 0.42 - 0.08 * ease(seg(lt, 2.6, 3.2))
    meter(img, 104, 22, '距离', val, (120, 190, 255), w=70, show_pct=False, blink=lt > 2.6)


def s_forecast(img, t, lt, v):
    gap = math.sin(seg(lt, 0.8, 2.6) * math.pi)
    classroom(img, t, mixm('rain', 'gold', gap * 0.5), rain_k=0.8 * (1 - gap))
    seated(img, 'teen', 250, FEET - 12, 'think', 1)
    desk(img, 250)
    d = ImageDraw.Draw(img)
    R(d, 116, 8, 2, 14, (110, 90, 70)); R(d, 150, 8, 2, 14, (110, 90, 70))
    R(d, 104, 20, 60, 20, (176, 128, 80)); R(d, 106, 22, 56, 16, (226, 190, 140))
    draw_text(img, 110, 25, '明天：晴？', (70, 40, 30))
    memory(img, 0.1)


def s_desk_lay(img, t, lt, v):
    classroom(img, t, 'rain', rain_k=1.0)
    d = ImageDraw.Draw(img)
    for i in range(6):
        x = 204 + i * 18; y = 16 + int((lt * (6 + i) + hsh(i, 3) * 60) % 60)
        d.line([(x, y), (x, y + 6)], fill=(214, 224, 236))
    actor(img, 'teen', 250, FEET + 10, 'idle', -1, 'sad')
    desk(img, 250, FEET - 10, 40)
    memory(img, 0.08, (190, 200, 220))


def s_storybook(img, t, lt, v):
    big_book(img, t, '从前从前……')
    actor(img, 'teen', 76, 100, 'idle', 1, 'smile')
    actor(img, 'girl', 108, 100, 'idle', -1, 'smile')
    flower(img, 256, 104, 1.0, stem=12)
    memory(img, 0.1)


def s_wind_pages(img, t, lt, v):
    corridor(img, t, 'dusk', 0)
    d = ImageDraw.Draw(img)
    for i in range(10):
        x = int((hsh(i, 3) * 300 + lt * (140 + hsh(i, 4) * 80)) % 360) - 30
        y = int(20 + hsh(i, 5) * 80 + math.sin(lt * 4 + i) * 6)
        R(d, x, y, 12, 12, (250, 248, 240)); R(d, x, y, 12, 3, (230, 70, 80))
        draw_text(img, x + 2, y + 3, str(int(hsh(i, 6) * 28) + 1), (40, 30, 30)) if False else None
    wind_fx(img, t, 1.0)
    memory(img, 0.12)


def s_far_apart(img, t, lt, v):
    u = ease(seg(lt, 0.2, 3.4))
    corridor(img, t, 'dusk', u * 60)
    actor(img, 'teen', lerp(130, 34, u), FEET, 'idle', 1, 'sad')
    actor(img, 'girl', lerp(190, 290, u), FEET, 'idle', -1, 'normal')
    wind_fx(img, t, 0.6)
    memory(img, 0.12)


def s_plus_one(img, t, lt, v):
    sx, sy = yard(img, t, 'dusk', 0.08 * math.sin(t * 1.6), bloom=1.0)
    seated(img, 'girl', int(sx), int(sy), 'smile')
    actor(img, 'teen', int(sx) + 22, FEET, 'idle', -1, 'blush')
    calendar(img, 20, 14, '+1', (240, 140, 60), flip=seg(lt, 0.8, 1.4))
    sfx(img, 90, 30, '+1天', t, t - lt + 1.2, dur=2.4, pal='yel', scale=1)
    memory(img, 0.12)


def s_grad_photo(img, t, lt, v):
    gate(img, t, 'dusk')
    actor(img, 'teen', 140, FEET, 'idle', 1, 'smile')
    actor(img, 'girl', 172, FEET, 'idle', -1, 'smile')
    if lt > 0.6:
        img.paste(sepia(img, 0.6))
        d = ImageDraw.Draw(img)
        R(d, 0, 0, W, 6, (250, 248, 240)); R(d, 0, H - 6, W, 6, (250, 248, 240)); R(d, 0, 0, 6, H, (250, 248, 240)); R(d, W - 6, 0, 6, H, (250, 248, 240))
    flash(img, max(0, 1 - abs(lt - 0.6) * 5))
    sfx(img, 250, 26, '咔嚓', t, t - lt + 0.6, dur=1.2, pal='white', scale=1)


def s_goodbye(img, t, lt, v):
    sx, sy = yard(img, t, 'dusk', 0.0, bloom=1.0)
    d = ImageDraw.Draw(img)
    u = ease(seg(lt, 1.6, 5.2))
    gx = lerp(int(sx) + 18, 330, u)
    if lt < 0.8:
        d.point((int(gx) - 1, FEET - 40), fill=FLOWER_Y)
    else:
        k = ease(seg(lt, 0.4, 0.8))
        fx, fy = lerp(gx - 1, sx, k), lerp(FEET - 40, sy - 1, k)
        d.rectangle([fx - 1, fy - 1, fx + 1, fy], fill=FLOWER_Y)
    actor(img, 'girl', gx, FEET, 'wave' if lt > 1.2 else 'idle', -1 if lt > 1.2 else -1, 'smile', walk_bob(lt) if u > 0 else 0)
    actor(img, 'teen', 120, FEET, 'idle', 1, 'sad' if lt < 3.5 else 'smile')
    memory(img, 0.14)


# —— 间奏：现在，雨小了，秋千边的花少了一片
def s_interlude(img, t, lt, v):
    lost = (2,) if lt > 6.2 else ()
    sx, sy = yard(img, t, mixm('rain', 'after', seg(lt, 0, 8)), 0.05 * math.sin(t * 1.4), bloom=1.0, lost=lost, wet=1.0)
    seated(img, 'adult', int(sx), int(sy), 'normal' if lt < 6.5 else 'sad')
    notebook(img, int(sx) + 8, int(sy) - 14, 0.0)
    rain_fx(img, t, 0.5 * (1 - seg(lt, 0, 9)))
    d = ImageDraw.Draw(img)
    if 4.6 < lt < 6.4:
        u = seg(lt, 4.6, 6.2)
        petal(img, int(FLX + 4 + u * 8), int(FEET - 16 + u * 18))
    for j in range(3):
        bi = np.searchsorted(song.beats, t) - 1 - j
        if bi < 0:
            break
        dt = t - song.beats[bi]
        if dt < 1.6 and lt > 6:
            r = int(2 + dt * 10)
            d.ellipse([FLX + 10 - r, FEET + 4 - r // 3, FLX + 10 + r, FEET + 4 + r // 3], outline=(200, 206, 210))


# —— 主歌二：现在，故地重游
def s_corridor_ghost(img, t, lt, v):
    corridor(img, t, 'clearing', lt * 6, clock_ang=1.2)
    actor(img, 'adult', lerp(60, 120, seg(lt, 0, 2.4)), FEET, 'idle', 1, 'normal', walk_bob(lt))
    u = seg(lt, 0.2, 2.0)
    if 0 < u < 1:
        gx = lerp(330, -20, u)
        actor(img, 'girl', gx, FEET, 'idle', -1, 'happy', walk_bob(lt, 10), ghost=0.55)
        actor(img, 'teen', gx + 26, FEET, 'run', -1, 'happy', walk_bob(lt, 10), ghost=0.55)


def s_petal_shoulder(img, t, lt, v):
    sky(img, t, 'clearing', HZ, 2)
    school(img, 'clearing', HZ - 2, 0, 320)
    ground(img, 'clearing', HZ, 0.6)
    ST.tree(img, 150, HZ + 4, 'summer', 1.0)
    ST.mark(img)
    actor(img, 'adult', 172, FEET, 'idle', 1, 'normal')
    u = seg(lt, 0.0, 1.2)
    px, py = lerp(150, 172, u), lerp(30, FEET - 30, u)
    petal(img, int(px + math.sin(lt * 5) * 4 * (1 - u)), int(py))


def s_enter_class(img, t, lt, v):
    classroom(img, t, 'clearing', rain_k=0.4)
    d = ImageDraw.Draw(img)
    for x in (110, 160):
        desk(img, x)
    R(d, 146, FEET - 10, 28, 1, (255, 246, 220))
    ow = int(26 * (1 - ease(seg(lt, 0, 0.8))))
    R(d, 0, 30, 30, 86, (120, 96, 76)); R(d, 2, 32, 26, 82, (90, 70, 56))
    R(d, 2, 32, max(2, ow), 82, (176, 132, 96))
    actor(img, 'adult', lerp(16, 96, ease(seg(lt, 0.5, 2.6))), FEET, 'idle', 1, 'normal' if lt < 2.8 else 'sad', walk_bob(lt) if lt < 2.6 else 0)


def s_rain_stop(img, t, lt, v):
    classroom(img, t, mixm('rain', 'clearing', seg(lt, 0, 1.6)), rain_k=0.6 * (1 - seg(lt, 0, 1.6)))
    cloud_face(img, 252, 30, 'sad' if lt < 0.9 else 'happy', (236, 240, 244))
    actor(img, 'adult', 160, FEET, 'idle', 1, 'think')
    meter(img, 26, 76, '雨停', 0.15 + 0.25 * seg(lt, 0.2, 1.6), (120, 200, 255), w=60, show_pct=False)


def s_catch_drops(img, t, lt, v):
    d = ImageDraw.Draw(img)
    ST.set_grade('dawn')
    img.paste(Image.fromarray(ST.grad3(H, W, (146, 180, 208), (190, 210, 224), (226, 232, 228))), (0, 0))
    R(d, 0, 112, W, H - 112, (200, 198, 190)); R(d, 0, 110, W, 3, (236, 234, 228))
    ST.mark(img)
    R(d, 0, 92, 170, 10, (84, 98, 80)); R(d, 170, 90, 16, 13, SKIN); R(d, 182, 88, 6, 4, SKIN)
    for i in range(3):
        st = 0.3 + i * 0.9
        u = seg(lt, st, st + 0.6)
        if 0 < u < 1:
            y = lerp(-4, 88, u)
            d.ellipse([178, y - 2, 181, y + 2], fill=(200, 220, 246))
        elif lt > st + 0.6 and lt < st + 1.0:
            for k in (-1, 1):
                d.point((179 + k * int((lt - st - 0.6) * 20), 86), fill=(200, 220, 246))


def s_take_guitar(img, t, lt, v):
    classroom(img, t, 'clearing')
    desk(img, 110)
    if lt < 2.4:
        seated(img, 'adult', 160, FEET - 12, 'normal' if lt < 1.2 else 'smile', 1)
        d = ImageDraw.Draw(img)
        op = ease(seg(lt, 0.8, 1.8))
        R(d, 182, FEET - 26, 8, 26, (40, 36, 44))
        if op > 0:
            R(d, 190, FEET - 26 + int(10 * (1 - op)), int(14 * op), 6, (150, 84, 40))
    else:
        actor(img, 'adult', 160, FEET, 'play', 1, 'smile')
    desk(img, 160)


def s_chalk(img, t, lt, v):
    classroom(img, t, 'clearing')
    txt = '等待？离开？'
    n = int(len(txt) * seg(lt, 0.1, 1.6))
    draw_text(img, 26, 34, txt[:n], (244, 244, 236))
    actor(img, 'adult', 130, FEET, 'idle', -1, 'think')


def s_erase(img, t, lt, v):
    classroom(img, t, 'clearing')
    draw_text(img, 26, 34, '等待？离开？', (244, 244, 236))
    d = ImageDraw.Draw(img)
    ex = int(lerp(14, 116, ease(seg(lt, 0.4, 3.0))))
    R(d, 12, 16, ex - 12, 46, (40, 70, 60))
    R(d, ex - 6, 32, 12, 8, (90, 70, 60)); R(d, ex - 6, 32, 12, 3, (230, 220, 200))
    for i in range(8):
        dt = (lt * 1.3 + hsh(i, 3)) % 1
        d.point((ex - 4 + int(hsh(i, 4) * 10), 42 + int(dt * 40)), fill=(230, 232, 226))
    actor(img, 'adult', 134, FEET, 'idle', -1, 'smile' if lt > 2.0 else 'normal')


# —— 副歌二（现在）：操场的风雨 → 放晴
def s_wind_guitar(img, t, lt, v):
    field(img, t, 'storm', dark=True)
    wind_fx(img, t, 1.2)
    actor(img, 'adult', 150, FEET, 'idle', 1, 'think', int(math.sin(t * 9) * 1))
    notebook(img, 160, FEET - 28, 0.0)


def s_last_rain(img, t, lt, v):
    field(img, t, 'storm', dark=True)
    cloud_face(img, 210, 18, 'scream' if lt > 1.4 else 'sad', (100, 110, 128))
    actor(img, 'adult', 150, FEET + 2, 'idle', 1, 'stuck')
    rain_fx(img, t, 1.0, slant=4)
    sfx(img, 74, 36, '哗啦', t, t - lt + 0.4, dur=1.4, pal='cyan', scale=1, jitter=2)


def s_ghost_wash(img, t, lt, v):
    field(img, t, 'storm', dark=True)
    g = 0.45 + 0.55 * seg(lt, 0.8, 2.8)
    if g < 1:
        actor(img, 'girl', 200, FEET, 'idle', -1, 'smile', ghost=g)
    actor(img, 'adult', 110, FEET, 'idle', 1, 'sad' if lt < 2.4 else 'normal')
    rain_fx(img, t, 1.0, slant=3)


def s_gym_eaves(img, t, lt, v):
    field(img, t, mixm('storm', 'rain', seg(lt, 0, 6)), dark=True, eaves=True)
    rain_fx(img, t, 0.8 - 0.4 * seg(lt, 0, 6), slant=2)
    actor(img, 'adult', 160, FEET - 2, 'play', 1, 'smile')
    beat_notes(img, t, lt, 176, 80, rise=26)
    meter(img, 96, 24, '雨停', 0.6 + 0.35 * seg(lt, 0, 5.6), (120, 200, 255), w=70, show_pct=False, blink=lt > 4.8)


def s_clear(img, t, lt, v):
    k = ease(seg(lt, 0.0, 0.9))
    m = mixm('storm', 'clear', k)
    field(img, t, m, sun=(260, 26, k))
    if k > 0.6:
        sun(img, 260, 26, 10, 'happy', t)
    for i in range(22):
        x = 8 + i * 14 + int(hsh(i, 5) * 6)
        b = ease(seg(lt, 0.5 + abs(x - 160) / 160 * 1.4, 1.2 + abs(x - 160) / 160 * 1.4))
        if b > 0:
            flower(img, x, FEET + 6 + int(hsh(i, 6) * 8), b, stem=8 + int(hsh(i, 7) * 6), sway=math.sin(t * 2 + i))
    actor(img, 'adult', 160, FEET, 'idle', 1, 'shock' if lt < 1.4 else 'happy')
    rain_fx(img, t, 0.8 * (1 - k))
    flash(img, max(0, 0.7 - lt * 0.9), (255, 250, 230))


def field_flowers(img, t, n=22, wind=0.0, lost_k=0.0):
    for i in range(n):
        x = 8 + i * 14 + int(hsh(i, 5) * 6)
        lost = tuple(j for j in range(5) if hsh(i, j, 77) < lost_k)
        flower(img, x, FEET + 6 + int(hsh(i, 6) * 8), 1.0, lost=lost, stem=8 + int(hsh(i, 7) * 6), sway=math.sin(t * 2 + i) + wind * 3)


def s_smile(img, t, lt, v):
    field(img, t, 'clear', sun=(260, 26, 1.0))
    sun(img, 260, 26, 10, 'happy', t)
    field_flowers(img, t)
    actor(img, 'adult', 160, FEET, 'wave' if 0.2 < lt < 1.1 else 'idle', 1, 'happy' if lt > 1.1 else 'normal')
    stamp(img, 72, 52, '好一点', t, t - lt + 1.6, col=(240, 170, 30), scale=1)


def s_last_page(img, t, lt, v):
    big_book(img, t, None, page_col=(250, 246, 230))
    pressed_big(img, 92, 50, 5)
    txt = '从前从前'
    n = int(len(txt) * seg(lt, 0.3, 1.8))
    draw_text(img, 174, 22, txt[:n], (44, 58, 92))
    ST.set_grade('day')


def s_wind_lift(img, t, lt, v):
    field(img, t, 'clear', sun=(260, 26, 1.0))
    sun(img, 260, 26, 10, 'happy', t)
    field_flowers(img, t, wind=1.0)
    wind_fx(img, t, 0.8, petals=8)
    actor(img, 'adult', 130, FEET, 'idle', 1, 'shock' if lt < 1.4 else 'smile')
    notebook(img, 140, FEET - 24, 1.0, with_flower=lt < 1.0)
    if lt >= 1.0:
        u = seg(lt, 1.0, 3.6)
        pressed_flower(img, int(150 + u * 60 + math.sin(lt * 3) * 6), int(FEET - 20 - u * 50), 1.2)


def s_float_away(img, t, lt, v):
    sky(img, t, 'clear', 150, 3, (280, 20, 1.0))
    school(img, 'clear', 150, 40, 300, 60)
    d = ImageDraw.Draw(img)
    R(d, 0, 150, W, 30, (150, 196, 110))
    ST.mark(img)
    u = seg(lt, 0, 3.6)
    pressed_flower(img, int(80 + u * 200), int(110 - u * 90 + math.sin(lt * 2.4) * 8), 1.4 - 0.8 * u)
    actor(img, 'adult', 40, 160, 'idle', 1, 'smile')


def s_plus_qing(img, t, lt, v):
    yard(img, t, 'clear', 0.04 * math.sin(t), bloom=1.0, sun=(280, 22, 1.0))
    field_flowers(img, t, n=12)
    actor(img, 'adult', 120, FEET, 'idle', 1, 'smile')
    x, y = 160, 40
    if lt < 2.8:
        sfx(img, x, y, '+1天', t, t - lt + 0.4, dur=2.4, pal='yel', scale=2)
    else:
        pop(img, x, y, '晴', t, t - lt + 2.8, dur=9, scale=3, c1=(255, 236, 120), c2=(255, 170, 40))
    sparkle(img, int(280 + math.sin(t * 3) * 2), 60, 2)


def s_stand(img, t, lt, v):
    field(img, t, 'clear', sun=(260, 26, 1.0))
    sun(img, 260, 26, 10, 'happy', t)
    field_flowers(img, t)
    actor(img, 'adult', 160, FEET, 'idle', 1, 'normal' if lt < 1.2 else 'smile')


def s_wave_bye(img, t, lt, v):
    field(img, t, 'clear', sun=(260, 26, 1.0))
    sun(img, 260, 26, 10, 'happy', t)
    field_flowers(img, t, lost_k=0.15 * seg(lt, 2, 5))
    actor(img, 'adult', 150, FEET, 'wave', 1, 'happy')
    tw = 2 + int(abs(math.sin(t * 4)) * 2)
    sparkle(img, 228, 36, tw, (255, 236, 150))


# —— 尾奏：阳光下的秋千，弹完 solo
def s_coda(img, t, lt, v):
    ang = 0.06 * math.sin(lt * 2 * math.pi / 1.76)
    sx, sy = yard(img, t, 'warm', ang, bloom=1.0, sun=(270, 22, 1.0), sway=pump(t) * 2)
    flower_big(img, FLX + 2, FEET + 2, 2, 1.0, sway=pump(t) * 1.5)
    actor(img, 'adult', int(sx) + 2, int(sy) + 13, 'play', 1, 'happy' if pump(t) > 0.5 else 'smile')
    beat_notes(img, t, lt, int(sx) + 20, int(sy) - 30, rise=50, life=2.2)
    petals_fall(img, t, 10, speed=0.6, seed=3)


def s_end(img, t, lt, v):
    sx, sy = yard(img, t, 'warm', 0.0, bloom=1.0, sun=(270, 22, 1.0))
    flower_big(img, FLX + 2, FEET + 2, 2, 1.0, sway=math.sin(t * 2) * 0.8)
    actor(img, 'adult', int(sx) - 30, FEET, 'idle', 1, 'smile')
    petals_fall(img, t, 8, speed=0.5, seed=5)


# ======================= ④ 镜头表 =======================
SHOTS = [
    (0.0, s_title, None), (9.6, s_intro_walk, None),
    (L(0), s_bloom, None), (L(1), s_petal_years, None), (L(2), s_kid_swing, None), (L(3), s_swing_grow, None),
    (L(4), s_hum1, None), (L(5), s_hum2, None), (L(6), s_window_sky, None), (L(7), s_petal_hair, None),
    (L(8), s_skip_class, None), (L(9), s_flower_fall, None), (L(10), s_fog_window, None), (L(11), s_rain_start, None),
    (L(12), s_rain_bathe, None), (L(13), s_notebook, None), (L(14), s_ask_back, None), (L(15), s_choice, None),
    (L(16), s_reach, None), (L(17), s_rain_grows, None), (L(18), s_cant_see, None), (L(19), s_distance, None),
    (L(20), s_forecast, None), (L(21), s_desk_lay, None), (L(22), s_storybook, None), (L(23), s_wind_pages, None),
    (L(24), s_far_apart, None), (L(25), s_plus_one, None), (L(26), s_grad_photo, None), (L(27), s_goodbye, None),
    (141.7, s_interlude, None),
    (L(28), s_corridor_ghost, None), (L(29), s_petal_shoulder, None), (L(30), s_enter_class, None), (L(31), s_rain_stop, None),
    (L(32), s_catch_drops, None), (L(33), s_take_guitar, None), (L(34), s_chalk, None), (L(35), s_erase, None),
    (L(36), s_wind_guitar, None), (L(37), s_last_rain, None), (L(38), s_ghost_wash, None), (L(39), s_gym_eaves, None),
    (L(40), s_clear, None), (L(41), s_smile, None), (L(42), s_last_page, None), (L(43), s_wind_lift, None),
    (L(44), s_float_away, None), (L(45), s_plus_qing, None), (L(46), s_stand, None), (L(47), s_wave_bye, None),
    (239.7, s_coda, None), (song.p['end_start'], s_end, None),
]
SHOTS.sort(key=lambda s: s[0])
ALLOW_REPEAT = {}

# ======================= ⑤ 每句花字 =======================
CFG = {
    0: dict(pal='white', kw=['小黄花'], kwpal='yel', deco=('star',), angle=-3),
    1: dict(pal='yel', kw=['飘着'], kwpal='white', angle=2),
    2: dict(pal='white', kw=['荡秋千'], kwpal='yel', angle=-2),
    3: dict(pal='yel', kw=['晃'], kwpal='pink', angle=3),
    4: dict(pal='white', size=96, deco=('note',), angle=-2),
    5: dict(pal='yel', size=92, deco=('note',), angle=2),
    6: dict(pal='white', kw=['前奏'], kwpal='yel', deco=('note',), angle=-3),
    7: dict(pal='yel', kw=['花瓣'], kwpal='pink', angle=2),
    8: dict(pal='white', kw=['翘课'], kwpal='pink', deco=('bang',), angle=-3),
    9: dict(pal='pink', kw=['花落'], kwpal='yel', angle=3),
    10: dict(pal='whiteb', size=100, kw=['看不见'], kwpal='cyan', angle=-2),
    11: dict(pal='cyan', kw=['下雨天'], kwpal='white', deco=('drop',), angle=2),
    12: dict(pal='whiteb', kw=['淋一遍'], kwpal='cyan', angle=-3),
    13: dict(pal='white', size=100, kw=['勇气'], kwpal='yel', angle=2),
    14: dict(pal='whiteb', kw=['再问'], kwpal='pink', angle=-2),
    15: dict(pal='white', kw=['等待', '离开'], kwpal=['cyan', 'pink'], deco=('q',), angle=3),
    16: dict(pal='whiteb', size=100, kw=['握着你手'], kwpal='pink', deco=('wave',), angle=-3),
    17: dict(pal='cyan', kw=['雨'], kwpal='white', angle=2),
    18: dict(pal='whiteb', kw=['看你不见'], kwpal='cyan', deco=('drop',), angle=-2),
    19: dict(pal='white', size=100, kw=['你身边'], kwpal='pink', angle=3),
    20: dict(pal='whiteb', kw=['放晴'], kwpal='yel', angle=-3),
    21: dict(pal='cyan', kw=['好一点'], kwpal='white', angle=2),
    22: dict(pal='white', size=100, kw=['爱你很久'], kwpal='pink', deco=('heart',), angle=-2),
    23: dict(pal='cyan', kw=['风'], kwpal='white', deco=('wave',), angle=3),
    24: dict(pal='whiteb', kw=['好远'], kwpal='cyan', angle=-3),
    25: dict(pal='yel', size=100, kw=['多爱一天'], kwpal='pink', deco=('heart',), angle=2),
    26: dict(pal='white', kw=['最后'], kwpal='pink', angle=-2),
    27: dict(pal='white', kw=['拜拜'], kwpal='cyan', angle=3),
    28: dict(pal='whiteb', kw=['翘课'], kwpal='yel', angle=-3),
    29: dict(pal='white', kw=['花落'], kwpal='yel', angle=2),
    30: dict(pal='whiteb', size=100, kw=['看不见'], kwpal='pink', angle=-2),
    31: dict(pal='cyan', kw=['消失'], kwpal='white', angle=3),
    32: dict(pal='whiteb', kw=['再淋一遍'], kwpal='cyan', deco=('drop',), angle=-3),
    33: dict(pal='white', size=100, kw=['还留着'], kwpal='yel', deco=('star',), angle=2),
    34: dict(pal='whiteb', kw=['再问'], kwpal='cyan', angle=-2),
    35: dict(pal='white', kw=['等待', '离开'], kwpal=['cyan', 'pink'], angle=3),
    36: dict(pal='whiteb', size=100, kw=['握着'], kwpal='yel', deco=('wave',), angle=-3),
    37: dict(pal='cyan', kw=['雨渐渐'], kwpal='white', angle=2),
    38: dict(pal='whiteb', kw=['看你不见'], kwpal='cyan', angle=-2),
    39: dict(pal='white', size=100, kw=['还要多久'], kwpal='cyan', angle=3),
    40: dict(pal='yel', kw=['放晴'], kwpal='white', kwscale=1.6, deco=('star', 'bang'), angle=-3, size=128),
    41: dict(pal='white', kw=['好一点'], kwpal='yel', deco=('star',), angle=2),
    42: dict(pal='yel', size=100, kw=['爱你很久'], kwpal='pink', deco=('heart',), angle=-2),
    43: dict(pal='white', kw=['风'], kwpal='cyan', deco=('wave',), angle=3),
    44: dict(pal='yel', kw=['好远'], kwpal='white', angle=-3),
    45: dict(pal='white', size=100, kw=['多爱一天'], kwpal='yel', deco=('heart',), angle=2),
    46: dict(pal='yel', kw=['最后'], kwpal='white', angle=-2),
    47: dict(pal='white', kw=['拜拜'], kwpal='yel', kwscale=1.5, deco=('star', 'wave'), angle=3),
}

MVX = MV(song, SHOTS, CFG, title_style=TITLE_STYLE, lyric_base=LYRIC_BASE, glass=False)
frame = MVX.frame
DUR = song.dur

# ======================= ⑦ 封面 =======================
COVER_T = 205.6


def COVER_3X4(img, t):
    """3:4 竖版封面：放晴那一刻的操场（裁成竖版），上方留给标题"""
    sc = Image.new('RGB', (W, H))
    field(sc, t, 'clear', sun=(226, 30, 1.0))
    sun(sc, 226, 30, 10, 'happy', t)
    field_flowers(sc, t)
    actor(sc, 'adult', 160, FEET, 'wave', 1, 'happy')
    pressed_flower(sc, 196, 58, 1.3)
    img.paste(portrait_from(sc, 70, 60), (0, 0))
