"""把一张图做成像素风 GIF：缩到 320×180 原生像素、固定调色板，加镜头漂浮、风线、飘过的小云和阳光闪烁，循环播放。
  python3 pixelize.py 输入图 输出.gif [--scale 3] [--colors 64] [--secs 2.4]"""
import argparse, math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--scale', type=int, default=3)
ap.add_argument('--colors', type=int, default=64)
ap.add_argument('--secs', type=float, default=2.4)
ap.add_argument('--fps', type=int, default=10)
A = ap.parse_args()

W, H = 320, 180
PAD = 6                      # 留边给镜头漂浮
BW, BH = W + 2 * PAD, H + 2 * PAD
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16


def hsh(*v):
    x = 0
    for i in v:
        x = (x * 1000003 + int(i * 7919) + 12345) & 0xFFFFFFFF
    x ^= x >> 13; x = (x * 0x5BD1E995) & 0xFFFFFFFF; x ^= x >> 15
    return (x & 0xFFFFFF) / float(0x1000000)


src = Image.open(A.src).convert('RGB')
# 先略微提高饱和度和对比，缩小后颜色更“像素游戏”
src = ImageEnhance.Color(src).enhance(1.15)
src = ImageEnhance.Contrast(src).enhance(1.08)
base = src.resize((BW, BH), Image.LANCZOS)
# 固定调色板（中位切分），整段动画共用，避免闪烁
pal_img = base.quantize(colors=A.colors, method=Image.MEDIANCUT, dither=Image.NONE)
PALETTE = pal_img.getpalette()[:A.colors * 3]
pal_rgb = np.array(PALETTE, float).reshape(-1, 3)


def to_pal(img):
    """有序抖动 + 映射到固定调色板"""
    a = np.asarray(img).astype(float)
    h, w = a.shape[:2]
    bay = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w][:, :, None]
    a = a + (bay - 0.5) * 18
    d = ((a[:, :, None, :] - pal_rgb[None, None]) ** 2).sum(3)
    idx = d.argmin(2).astype(np.uint8)
    p = Image.fromarray(idx, 'P'); p.putpalette(PALETTE + [0] * (768 - len(PALETTE)))
    return p


base_p = to_pal(base).convert('RGB')
N = int(A.secs * A.fps)


def cloud(d, x, y, s, col, edge):
    for (dx, dy, r) in ((0, 0, 5), (6, -3, 6), (13, 0, 5), (7, 2, 5)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=edge)
    for (dx, dy, r) in ((0, 0, 4), (6, -3, 5), (13, 0, 4), (7, 2, 4)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=col)


frames = []
for f in range(N):
    ph = f / N                        # 0..1 一个循环
    a = 2 * math.pi * ph
    # 镜头：轻轻上下浮动 + 小幅左右摆，像跟着神龙一起飞
    ox = PAD + int(round(math.sin(a) * 3))
    oy = PAD + int(round(math.sin(a * 2) * 2))
    img = base_p.crop((ox, oy, ox + W, oy + H))
    d = ImageDraw.Draw(img)
    # 阳光：左上角一圈一圈闪
    arr = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - 6, yy - 6)
    glow = np.clip(1 - r / (46 + 6 * math.sin(a * 2)), 0, 1) ** 1.6 * 0.5
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    m = bay < glow * 1.6
    arr[m] = arr[m] * 0.45 + np.array([255, 250, 225]) * 0.55
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    for i in range(6):
        ang = 0.25 + i * 0.22 + math.sin(a + i) * 0.03
        L = 30 + 10 * math.sin(a * 2 + i)
        d.line([(6, 6), (6 + math.cos(ang) * L, 6 + math.sin(ang) * L)], fill=(255, 252, 230))
    # 风线：往右飞掠（神龙朝左飞，背景向右退）
    for i in range(14):
        y = int(4 + hsh(i, 1) * 22) if i % 2 else int(150 + hsh(i, 1) * 26)  # 只在上下两条天空/云海里，不划过人物
        ln = 10 + int(hsh(i, 2) * 22)
        sp = 1 + int(hsh(i, 3) * 2)                       # 每个循环走 1~2 屏，首尾衔接
        x = int((hsh(i, 4) * (W + 80) + ph * sp * (W + 80)) % (W + 80)) - 40
        d.line([(x, y), (x + ln, y)], fill=(250, 252, 255) if i % 3 else (210, 225, 255))
    # 前景小云飘过（像素云）
    for i in range(3):
        y = int(168 + i * 5 + hsh(i, 7) * 3)
        x = int((hsh(i, 8) * (W + 120) + ph * (W + 120)) % (W + 120)) - 60
        cloud(d, x, y, 1, (250, 248, 255), (176, 186, 220))
    # 闪光点
    for i in range(10):
        if (f + i * 3) % 8 < 3:
            sx, sy = int(hsh(i, 9) * W), int(hsh(i, 10) * 90)
            rr = 2 if (f + i * 3) % 8 == 1 else 1
            d.line([(sx - rr, sy), (sx + rr, sy)], fill=(255, 255, 240)); d.line([(sx, sy - rr), (sx, sy + rr)], fill=(255, 255, 240))
    p = to_pal(img) if False else img.quantize(palette=pal_img, dither=Image.NONE)
    frames.append(p.resize((W * A.scale, H * A.scale), Image.NEAREST))

frames[0].save(A.out, save_all=True, append_images=frames[1:], duration=int(1000 / A.fps), loop=0, optimize=True, disposal=1)
print('ok', A.out, len(frames), 'frames')
