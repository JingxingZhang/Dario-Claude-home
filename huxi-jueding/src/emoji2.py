"""1:1 表情包「感谢关注，点个推荐呗」：沿用像素 + 综艺花字风格。
输出：emoji/感谢关注求推荐.gif（480×480，2.4 秒循环，原版质量）、.png（1080 静图：点推荐前 / 已推荐）。"""
import math, os
from PIL import Image, ImageDraw
from pixlib import *
from chars import person, heart, sparkle, burst, K, R
from props2 import cat, sfx, cursor, heart_face, firework
import huazi as Z
from emoji import N, S, OUT, LOOP

NEON_Y, NEON_P, NEON_B = (255, 230, 90), (255, 80, 200), (80, 200, 255)


def star(d, cx, cy, r, col):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=col, outline=K)


def rec_btn(img, cx, cy, done, press):
    d = ImageDraw.Draw(img)
    w, h = 66, 20
    x, y = cx - w // 2, cy - h // 2 + (1 if press else 0)
    col = (255, 196, 60) if done else (250, 60, 90)
    R(d, x + 1, y + h, w - 2, 2 if not press else 1, K)
    R(d, x + 1, y - 1, w - 2, h + 2, K); R(d, x - 1, y + 1, w + 2, h - 2, K)
    R(d, x + 1, y, w - 2, h, col); R(d, x, y + 1, w, h - 2, col)
    R(d, x + 2, y + 1, w - 4, 2, lerpc(col, WHITE, 0.45))
    star(d, x + 11, y + 10, 6, WHITE if not done else (255, 120, 60))
    s = '已推荐' if done else '推荐'
    draw_text(img, x + 20 + (40 - text_w(s)) // 2, y + 4, s, WHITE if not done else K)


def pixel_layer(t):
    img = Image.new('RGB', (N, N), (255, 220, 150))
    burst(img, t * 0.5, (255, 214, 140), (255, 236, 186), cx=90, cy=100, n=14)
    lt = t % LOOP
    click = 0.9
    done = lt >= click
    # 中间一颗会害羞的大心，随节拍跳；点了推荐后变成心形眼并冒小心
    pump = 1 if (t % 0.6) < 0.15 else 0
    heart_face(img, 84, 100, 4 + pump, 'laugh' if done else 'blush')
    if done:
        for i in range(7):
            a = -math.pi / 2 + (i - 3) * 0.33
            r = 22 + (lt - click) * 36
            if r < 66:
                heart(img, int(84 + math.cos(a) * r), int(96 + math.sin(a) * r), 1)
        for i, (fx, fy, tb, c) in enumerate(((36, 70, click + 0.05, NEON_P), (140, 64, click + 0.35, NEON_B), (60, 54, click + 0.7, NEON_Y))):
            firework(img, fx, fy, lt, tb, c)
    rec_btn(img, 88, 146, done, abs(lt - click) < 0.1)
    cx_ = int(lerp(150, 100, ease(seg(lt, 0.1, 0.75))))
    cy_ = int(lerp(176, 148, ease(seg(lt, 0.1, 0.75))))
    cursor(img, cx_, cy_)
    if done:
        sfx(img, 30, 92, '叮！', lt, click, 9, 'yel', 2)
    else:
        sfx(img, 30, 92, '求！', lt, 0.0, 9, 'red', 2)
    bob = int(abs(math.sin(t * math.pi / 0.6)) * 2) + (int(abs(math.sin((lt - click) * 8)) * 4) if done and lt < click + 0.8 else 0)
    cat(img, 30, 178 - bob, t, 'up', 'heart' if done else 'normal', 1, 2, sign='谢谢！' if done else '拜托啦', hearts=False)
    person(img, 152, 178, 'girl', -1, 'happy' if done else 'wink', 'heart', t, 2)
    for i in range(4):
        if int(t * 5 + i) % 2:
            sparkle(img, int(20 + hsh(i, 1) * 140), int(60 + hsh(i, 2) * 50), 2)
    return img


TEXT = Z.Line(-5, 99, '感谢关注/点个推荐呗', pal='yel', kw=['推荐'], kwpal='pink', kwscale=1.3, size=128, cx=540, cy=200, angle=-4,
              deco=('heart', 'star', 'heart2'))


def frame(t, size=1080):
    base = pixel_layer(t).resize((N * S, N * S), Image.NEAREST)
    TEXT.draw(base, 10.0 + (t % LOOP), beat_phase=(t % 0.6))
    Z.pill(base, 540, 1018, '你最好啦，比心', 50, bg=(120, 40, 20), edge=(255, 255, 255))
    return base if size == 1080 else base.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    frame(0.6).save(os.path.join(OUT, '感谢关注求推荐.png'))
    frame(1.6).save(os.path.join(OUT, '感谢关注求推荐-已推荐.png'))
    frames = [frame(i / 10, 480).convert('P', palette=Image.ADAPTIVE, colors=128) for i in range(int(LOOP * 10))]
    frames[0].save(os.path.join(OUT, '感谢关注求推荐.gif'), save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=2)
    for f in sorted(os.listdir(OUT)):
        if f.startswith('感谢'):
            print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
