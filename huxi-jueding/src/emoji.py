"""1:1 表情包「关注后私信发原视频」：像素画（180×180，放大 6 倍到 1080）+ 高清综艺花字。
输出：emoji/关注领原视频.png（1080×1080 静态）、emoji/关注领原视频.gif（480×480 动图，2.4 秒循环）。"""
import math, os
from PIL import Image, ImageDraw
from pixlib import *
from chars import person, heart, sparkle, burst, K, R, PINK, NEON_Y
from props2 import cat, sfx, ptext, cursor, heart_face, face
import huazi as Z

N = 180          # 原生边长
S = 6            # 放大倍数 → 1080
OUT = os.path.join(ROOT, 'emoji')
LOOP = 2.4


def gift(img, cx, cy, t, open_k=0.0):
    d = ImageDraw.Draw(img)
    w, h = 64, 40
    x, y = cx - w // 2, cy - h // 2
    hop = int(abs(math.sin(t * math.pi * 2 / 0.8)) * 3) if open_k == 0 else 0
    R(d, x - 1, y - 1, w + 2, h + 2, K); R(d, x, y, w, h, (240, 80, 120))
    R(d, x + w // 2 - 4, y, 8, h, (255, 214, 90))
    # 盖子
    ly = y - 9 - hop - int(open_k * 14)
    R(d, x - 4, ly - 1, w + 10, 11, K); R(d, x - 3, ly, w + 8, 9, (255, 110, 150)); R(d, x + w // 2 - 4, ly, 8, 9, (255, 214, 90))
    # 蝴蝶结
    for s in (-1, 1):
        d.polygon([(cx, ly - 1), (cx + s * 12, ly - 8), (cx + s * 12, ly + 2)], fill=(255, 214, 90), outline=K)
    R(d, cx - 2, ly - 4, 5, 5, (255, 180, 40))
    # 标签
    lw = text_w('原视频') + 8
    R(d, cx - lw // 2 - 1, cy - 2, lw + 2, 16, K); R(d, cx - lw // 2, cy - 1, lw, 14, (255, 250, 240))
    draw_text(img, cx - lw // 2 + 4, cy, '原视频', (230, 50, 90))


def follow_btn(img, cx, cy, done, press):
    d = ImageDraw.Draw(img)
    w, h = 62, 20
    x, y = cx - w // 2, cy - h // 2 + (1 if press else 0)
    R(d, x + 1, y + h, w - 2, 2 if not press else 1, K)
    col = (150, 150, 165) if done else (250, 60, 90)
    R(d, x + 1, y - 1, w - 2, h + 2, K); R(d, x - 1, y + 1, w + 2, h - 2, K)
    R(d, x + 1, y, w - 2, h, col); R(d, x, y + 1, w, h - 2, col)
    R(d, x + 2, y + 1, w - 4, 2, lerpc(col, WHITE, 0.4))
    s = '已关注' if done else '+ 关注'
    draw_text(img, cx - text_w(s) // 2, y + 4, s, WHITE)


def pixel_layer(t):
    img = Image.new('RGB', (N, N), (255, 190, 220))
    burst(img, t * 0.5, (255, 176, 214), (255, 212, 232), cx=90, cy=100, n=14)
    lt = t % LOOP
    click = 0.9
    done = lt >= click
    gift(img, 90, 102, t, open_k=ease(seg(lt, click + 0.1, click + 0.4)))
    if done:
        for i in range(6):
            a = -math.pi / 2 + (i - 2.5) * 0.35
            r = 10 + (lt - click) * 40
            if r < 60:
                heart(img, int(90 + math.cos(a) * r), int(78 + math.sin(a) * r), 1)
    follow_btn(img, 90, 146, done, abs(lt - click) < 0.1)
    # 鼠标：移到按钮上点一下
    cx_ = int(lerp(150, 100, ease(seg(lt, 0.1, 0.75))))
    cy_ = int(lerp(176, 148, ease(seg(lt, 0.1, 0.75))))
    cursor(img, cx_, cy_)
    if done:
        sfx(img, 34, 92, '叮！', lt, click, 9, 'yel', 2)
    else:
        sfx(img, 34, 92, '快！', lt, 0.0, 9, 'red', 2)
    bob = int(abs(math.sin(t * math.pi / 0.6)) * 2)
    cat(img, 30, 178 - bob, t, 'up', 'happy' if done else 'normal', 1, 2, sign='点这里→' if not done else None, hearts=done)
    person(img, 152, 178, 'girl', -1, 'wink', 'wave', t, 2)
    for i in range(4):
        if int(t * 5 + i) % 2:
            sparkle(img, int(20 + hsh(i, 1) * 140), int(60 + hsh(i, 2) * 50), 2)
    return img


TEXT = Z.Line(-5, 99, '关注我/原视频送你', pal='yel', kw=['原视频'], kwpal='pink', kwscale=1.25, size=138, cx=540, cy=200, angle=-4,
              deco=('heart', 'star', 'bang'))


def frame(t, size=1080):
    base = pixel_layer(t).resize((N * S, N * S), Image.NEAREST)
    TEXT.draw(base, 10.0 + (t % LOOP), beat_phase=(t % 0.6))
    Z.pill(base, 540, 1018, '关注后私信发你 · @张景行', 50, bg=(60, 20, 70), edge=(255, 255, 255))
    return base if size == 1080 else base.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    frame(0.6).save(os.path.join(OUT, '关注领原视频.png'))
    frames = [frame(i / 10, 480).convert('P', palette=Image.ADAPTIVE, colors=128) for i in range(int(LOOP * 10))]
    frames[0].save(os.path.join(OUT, '关注领原视频.gif'), save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=2)
    frame(1.6).save(os.path.join(OUT, '关注领原视频-已关注.png'))
    for f in os.listdir(OUT):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
