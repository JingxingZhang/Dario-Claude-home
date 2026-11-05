"""1:1 互动表情包：像素层（180×180，放大 6 倍到 1080）+ 高清综艺花字 + 底部标签。内容按每首歌的歌词定制。
用法见 templates/sticker_template.py：写 pixel(t) → Sticker(pixel, '第一行/第二行', ...) → export()。
输出：<name>.gif（480×480，2.4 秒循环）+ <name>.png（操作前静图）+ <name>-之后.png（操作后静图）。"""
import math, os
from PIL import Image, ImageDraw
from pixlib import *
from chars import K, R
import huazi as Z

N, S, LOOP = 180, 6, 2.4
CLICK = 0.9   # 默认在第 0.9 秒“点下去”，之前是操作前，之后是操作后


def ui_button(img, cx, cy, label, done_label, done, press=False, col=(250, 60, 90), done_col=(150, 150, 165), icon=None, w=62, fg_done=WHITE):
    """一枚像素按钮（关注 / 推荐 / 收藏…），icon(d, x, y) 可画左侧小图标"""
    d = ImageDraw.Draw(img)
    h = 20
    x, y = cx - w // 2, cy - h // 2 + (1 if press else 0)
    c = done_col if done else col
    R(d, x + 1, y + h, w - 2, 2 if not press else 1, K)
    R(d, x + 1, y - 1, w - 2, h + 2, K); R(d, x - 1, y + 1, w + 2, h - 2, K)
    R(d, x + 1, y, w - 2, h, c); R(d, x, y + 1, w, h - 2, c)
    R(d, x + 2, y + 1, w - 4, 2, lerpc(c, WHITE, 0.45))
    s = done_label if done else label
    ox = 0
    if icon:
        icon(d, x + 6, y + 4); ox = 8
    draw_text(img, cx - text_w(s) // 2 + ox, y + 4, s, fg_done if done else WHITE)


def cursor_to(img, lt, x0, y0, x1, y1, t0=0.1, t1=0.75):
    from props2 import cursor
    k = ease(seg(lt, t0, t1))
    cursor(img, int(lerp(x0, x1, k)), int(lerp(y0, y1, k)))


def gift_box(img, cx, cy, t, label='礼物', open_k=0.0, col=(240, 80, 120), ribbon=(255, 214, 90)):
    d = ImageDraw.Draw(img)
    w, h = 64, 40
    x, y = cx - w // 2, cy - h // 2
    hop = int(abs(math.sin(t * math.pi * 2 / 0.8)) * 3) if open_k == 0 else 0
    R(d, x - 1, y - 1, w + 2, h + 2, K); R(d, x, y, w, h, col); R(d, x + w // 2 - 4, y, 8, h, ribbon)
    ly = y - 9 - hop - int(open_k * 14)
    R(d, x - 4, ly - 1, w + 10, 11, K); R(d, x - 3, ly, w + 8, 9, lerpc(col, WHITE, 0.2)); R(d, x + w // 2 - 4, ly, 8, 9, ribbon)
    for s in (-1, 1):
        d.polygon([(cx, ly - 1), (cx + s * 12, ly - 8), (cx + s * 12, ly + 2)], fill=ribbon, outline=K)
    lw = text_w(label) + 8
    R(d, cx - lw // 2 - 1, cy - 2, lw + 2, 16, K); R(d, cx - lw // 2, cy - 1, lw, 14, (255, 250, 240))
    draw_text(img, cx - lw // 2 + 4, cy, label, (230, 50, 90))


def ticket(img, x, y, label='优先券', col=(255, 214, 80)):
    d = ImageDraw.Draw(img)
    w = text_w(label) + 18
    R(d, x - 1, y - 1, w + 2, 20, K); R(d, x, y, w, 18, col); R(d, x + 2, y + 2, w - 4, 1, lerpc(col, WHITE, 0.5))
    draw_text(img, x + 1, y + 3, '★', (230, 90, 40))
    draw_text(img, x + 13, y + 3, label, K)


class Sticker:
    def __init__(self, pixel, text, kw=None, pal='yel', kwpal='pink', pill=None, pill_bg=(60, 20, 70), size=138, deco=('heart', 'star', 'bang')):
        """pixel(t) -> 180×180 RGB 像素层；text 用 / 分两行；pill 为底部标签（表情包默认不加署名）"""
        self.pixel = pixel
        self.text = Z.Line(-5, 99, text, pal=pal, kw=kw, kwpal=kwpal, kwscale=1.25, size=size, cx=540, cy=200, angle=-4, deco=deco)
        self.pill, self.pill_bg = pill, pill_bg

    def frame(self, t, size=1080):
        base = self.pixel(t).resize((N * S, N * S), Image.NEAREST)
        self.text.draw(base, 10.0 + (t % LOOP), beat_phase=(t % 0.6))
        if self.pill:
            Z.pill(base, 540, 1018, self.pill, 48, bg=self.pill_bg, edge=(255, 255, 255))
        return base if size == 1080 else base.resize((size, size), Image.LANCZOS)

    def export(self, out_dir, name, before=0.6, after=1.7, gif_size=480, fps=10):
        os.makedirs(out_dir, exist_ok=True)
        self.frame(before).save(os.path.join(out_dir, f'{name}.png'))
        self.frame(after).save(os.path.join(out_dir, f'{name}-之后.png'))
        fr = [self.frame(i / fps, gif_size).convert('P', palette=Image.ADAPTIVE, colors=128) for i in range(int(LOOP * fps))]
        g = os.path.join(out_dir, f'{name}.gif')
        fr[0].save(g, save_all=True, append_images=fr[1:], duration=int(1000 / fps), loop=0, optimize=True, disposal=2)
        for f in (f'{name}.gif', f'{name}.png', f'{name}-之后.png'):
            print('✓', os.path.join(out_dir, f), os.path.getsize(os.path.join(out_dir, f)) // 1024, 'KB')
