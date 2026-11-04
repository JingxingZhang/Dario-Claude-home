"""1:1 表情包「关注后，下一首歌优先给你定制」：像素点歌机 + 综艺花字，沿用前两张的风格（蓝紫配色以便区分）。
输出：emoji/关注优先定制下一首.gif（480×480，2.4 秒循环）、.png（1080 静图：关注前 / 已关注）。"""
import math, os
from PIL import Image, ImageDraw
from pixlib import *
from chars import person, heart, sparkle, burst, K, R
from props2 import cat, sfx, cursor, ptext
import huazi as Z
from emoji import N, S, OUT, LOOP, follow_btn

NEON_Y, NEON_P, NEON_B = (255, 230, 90), (255, 80, 200), (80, 200, 255)


def jukebox(img, cx, top, t, lit):
    """复古点歌机：拱顶霓虹、滚动屏、按键、出票口"""
    d = ImageDraw.Draw(img)
    w, h = 58, 60
    x = cx - w // 2
    # 机身 + 拱顶
    d.ellipse([x - 1, top - 1, x + w, top + 40], fill=K)
    R(d, x - 1, top + 18, w + 2, h - 17, K)
    d.ellipse([x, top, x + w - 1, top + 38], fill=(110, 60, 170))
    R(d, x, top + 19, w, h - 19, (110, 60, 170))
    # 霓虹拱条（循环变色）
    cols = [NEON_P, NEON_Y, NEON_B, (120, 240, 140)]
    for k in range(3):
        c = cols[(int(t * 6) + k) % 4] if lit else lerpc(cols[k], (60, 40, 90), 0.5)
        d.arc([x + 4 + k * 4, top + 4 + k * 4, x + w - 5 - k * 4, top + 34 - k * 4], 180, 360, fill=c, width=2)
    # 屏幕：滚动“下一首：？？？”
    R(d, x + 7, top + 24, w - 14, 14, K)
    R(d, x + 8, top + 25, w - 16, 12, (20, 30, 50))
    msg = '♪ 下一首：？？？ ' * 2
    off = int(t * 24) % text_w('♪ 下一首：？？？ ')
    scr = Image.new('RGB', (w - 16, 12), (20, 30, 50))
    draw_text(scr, -off, 0, msg, (120, 255, 200))
    img.paste(scr, (x + 8, top + 25))
    # 按键
    for i in range(4):
        R(d, x + 9 + i * 11, top + 42, 8, 5, K); R(d, x + 10 + i * 11, top + 42, 6, 4, cols[i] if lit else (150, 140, 170))
    # 出票口
    R(d, x + 14, top + 52, w - 28, 3, K)
    # 音箱格栅
    for yy in range(top + 49, top + h - 1, 2):
        R(d, x + 3, yy, 8, 1, (80, 40, 130)); R(d, x + w - 11, yy, 8, 1, (80, 40, 130))


def ticket(img, x, y):
    d = ImageDraw.Draw(img)
    R(d, x - 1, y - 1, 46, 20, K)
    R(d, x, y, 44, 18, (255, 214, 80))
    R(d, x + 2, y + 2, 40, 1, (255, 240, 170))
    for yy in range(y + 2, y + 17, 3):
        d.point((x + 10, yy), fill=(200, 140, 30))
    draw_text(img, x + 1, y + 3, '★', (230, 90, 40))
    draw_text(img, x + 13, y + 3, '优先券', K)


def pixel_layer(t):
    img = Image.new('RGB', (N, N), (150, 170, 255))
    burst(img, t * 0.5, (150, 166, 255), (186, 200, 255), cx=90, cy=100, n=14)
    lt = t % LOOP
    click = 0.9
    done = lt >= click
    jukebox(img, 86, 70, t, done)
    # 关注后：出票口吐出“优先券”，飘到右上；音符往外冒
    if done:
        p = ease(seg(lt, click + 0.1, click + 0.6))
        tx, ty = int(lerp(64, 116, p)), int(lerp(120, 76, p))
        if p > 0:
            ticket(img, tx, ty)
        for i in range(5):
            ph = ((lt - click) * 0.9 + i * 0.2) % 1
            nx = int(86 + math.sin(i * 2.1 + lt * 3) * 26)
            ny = int(84 - ph * 30)
            draw_text(img, nx, ny, '♪' if i % 2 else '♫', [NEON_P, NEON_Y, NEON_B][i % 3], outline=K)
    follow_btn(img, 86, 146, done, abs(lt - click) < 0.1)
    cx_ = int(lerp(150, 96, ease(seg(lt, 0.1, 0.75))))
    cy_ = int(lerp(176, 148, ease(seg(lt, 0.1, 0.75))))
    cursor(img, cx_, cy_)
    if done:
        sfx(img, 30, 92, '叮！', lt, click, 9, 'yel', 2)
    else:
        sfx(img, 30, 92, '点！', lt, 0.0, 9, 'cyan', 2)
    bob = int(abs(math.sin(t * math.pi / 0.6)) * 2)
    cat(img, 30, 178 - bob, t, 'up', 'heart' if done else 'normal', 1, 2, sign='VIP!' if done else '点歌吗')
    person(img, 152, 178, 'girl', -1, 'happy' if done else 'wink', 'point', t, 2)
    for i in range(4):
        if int(t * 5 + i) % 2:
            sparkle(img, int(20 + hsh(i, 1) * 140), int(60 + hsh(i, 2) * 50), 2)
    return img


TEXT = Z.Line(-5, 99, '关注我/下一首你来定', pal='cyan', kw=['你来定'], kwpal='yel', kwscale=1.3, size=124, cx=540, cy=196, angle=-4,
              deco=('note', 'star', 'heart'))


def frame(t, size=1080):
    base = pixel_layer(t).resize((N * S, N * S), Image.NEAREST)
    TEXT.draw(base, 10.0 + (t % LOOP), beat_phase=(t % 0.6))
    Z.pill(base, 540, 1018, '关注后可优先定制下一首歌', 46, bg=(40, 30, 100), edge=(255, 255, 255))
    return base if size == 1080 else base.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    frame(0.6).save(os.path.join(OUT, '关注优先定制下一首.png'))
    frame(1.7).save(os.path.join(OUT, '关注优先定制下一首-已关注.png'))
    frames = [frame(i / 10, 480).convert('P', palette=Image.ADAPTIVE, colors=128) for i in range(int(LOOP * 10))]
    frames[0].save(os.path.join(OUT, '关注优先定制下一首.gif'), save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=2)
    for f in sorted(os.listdir(OUT)):
        if f.startswith('关注优先'):
            print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
