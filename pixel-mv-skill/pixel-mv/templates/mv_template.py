"""《{歌名}》像素综艺 MV —— 镜头脚本。
结构：镜头函数 → SHOTS（镜头表）→ DANMU（回放段弹幕）→ CFG（每句歌词花字样式）→ MV(...)
写法要点（详见 references/storyboard-guide.md、library-api.md）：
  - 镜头函数 fn(img, t, lt, v)：在 320×180 的 img 上画；动作一律按 lt（本镜头开始后的秒）编排。
  - v：False 普通 / 'replay' 回放（引擎自动褪色+扫描线+弹幕+标签）/ True 第二套配色（自己读 v is True 换色）。
  - 画面里的像素字、道具放在 y < 120，底部留给歌词花字和署名。
  - 主角外观用 make_look() 按歌词定制；贯穿全片的配角（宠物或代表物件）选一个就固定用到底。
"""
import math, os, sys
SKILL = os.environ.get('PIXMV_SKILL', '')
sys.path.insert(0, os.path.join(SKILL, 'lib'))
ROOT = os.environ.get('PIXMV_PROJECT', os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *
from chars import *            # person, make_look, heart, sparkle, sweat, burst, dots_bg, concentration, spotlight, curtains …
from props2 import *           # ptext, sfx, stamp, say, OS, sys_msg, popup, cursor, meter, toggle, danmaku, cat, dog, moon, lamp, face …
from scenes_common import street, room, rain
from engine import Song, MV
import huazi as Z

song = Song(ROOT)
rms, pump, beat_phase, L = song.rms, song.pump, song.beat_phase, song.L

# ---------- 角色（按歌词定制）----------
ME = make_look('me', 'girl')          # 例：make_look('me', 'girl', hair_style='ponytail', body='uniform', cloth=(70,90,160))
YOU = make_look('you', 'boy')


# ---------- 镜头 ----------
def s_title(img, t, lt, v):
    """片头标题卡背后的画面（歌名和原唱由引擎叠加）"""
    street(img, t, scroll=t * 10, rain_k=0.3)
    person(img, 120, 128, ME, 1, 'smile', 'down', t, 2)
    cat(img, 84, 128, t, 'sit', 'normal', 1, 1)


def s_placeholder(img, t, lt, v, i=0):
    """还没设计的句子先用占位镜头，保证流程能跑通；交付前必须全部替换"""
    street(img, t, v is True, scroll=600 + i * 120, rain_k=0.4)
    person(img, 110, 128, ME, 1, 'smile', 'down', t, 2)
    person(img, 210, 128, YOU, -1, 'smile', 'down', t, 2)
    ptext(img, 160, 40, f'第{i + 1}句 待设计', 1, (255, 230, 120))


def s_end(img, t, lt, v):
    room(img, t)
    a = np.asarray(img).astype(float) * 0.45
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))


def _ph(i):
    return lambda img, t, lt, v: s_placeholder(img, t, lt, v, i)


# ---------- 镜头表：(开始秒, 镜头函数, 变体) ----------
SHOTS = [(0.0, s_title, False)]
SHOTS += [(L(i), _ph(i), False) for i in range(len(song.lines))]
SHOTS += [(song.p['end_start'], s_end, False)]
SHOTS.sort(key=lambda s: s[0])

# ---------- 回放段弹幕：{镜头函数: [(镜头内秒, 文字, 颜色)]} ----------
DANMU = {}

# ---------- 每句歌词花字：键可用句序号或歌词原文 ----------
# 参数：pal 底色 / kw 重点词列表 / kwpal 重点词配色（可为列表）/ kwscale / size / cx cy / angle / deco 贴纸
# 配色：pink yel cyan red purp green white whiteb；贴纸：heart heart2 star bang q sweat x note crack drop horn wave
CFG = {}

MVX = MV(song, SHOTS, CFG, danmu=DANMU)
frame = MVX.frame
DUR = song.dur
