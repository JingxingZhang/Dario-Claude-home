"""《{歌名}》互动表情包（1:1）：内容按这首歌定制——用 MV 里的主角、贯穿配角/物件、标志性道具。
套路：画面里有一个“操作”（点按钮 / 拉杆 / 盖章…），CLICK 秒之前是“操作前”，之后出结果（弹出 叮！、冒心、道具变化）。
运行：PIXMV_SKILL=<skill> python3 stickers/xxx.py"""
import math, os, sys
SKILL = os.environ.get('PIXMV_SKILL', '')
sys.path.insert(0, os.path.join(SKILL, 'lib'))
HERE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image
from pixlib import *
from chars import *
from props2 import *
from sticker import Sticker, ui_button, cursor_to, gift_box, ticket, N, LOOP, CLICK


def pixel(t):
    img = Image.new('RGB', (N, N), (255, 190, 220))
    burst(img, t * 0.5, (255, 176, 214), (255, 212, 232), cx=90, cy=100, n=14)
    lt = t % LOOP
    done = lt >= CLICK
    gift_box(img, 90, 102, t, label='原视频', open_k=ease(seg(lt, CLICK + 0.1, CLICK + 0.4)))
    ui_button(img, 90, 146, '+ 关注', '已关注', done, abs(lt - CLICK) < 0.1)
    cursor_to(img, lt, 150, 176, 100, 148)
    sfx(img, 34, 92, '叮！' if done else '快！', lt, CLICK if done else 0.0, 9, 'yel' if done else 'red', 2)
    cat(img, 30, 178, t, 'up', 'happy' if done else 'normal', 1, 2, sign=None if done else '点这里→', hearts=done)
    person(img, 152, 178, 'girl', -1, 'wink', 'wave', t, 2)
    return img


if __name__ == '__main__':
    Sticker(pixel, '关注我/原视频送你', kw=['原视频'], pill='关注后私信发你').export(os.path.join(HERE, '..', 'stickers'), '关注领原视频')
