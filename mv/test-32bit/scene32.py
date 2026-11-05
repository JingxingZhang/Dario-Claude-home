"""32-bit 像素风景测试图：全部用代码凭空绘制（没有任何图片素材、没有 AI 生成）。
原生 480×270（每个像素放大 4 倍到 1920×1080），全图统一到一套 64 色调色板。
  python3 scene32.py            → sunset_32bit.png（静帧）
  python3 scene32.py --video    → sunset_32bit.mp4（6 秒动态：云飘、水波、阳光碎金、窗灯）"""
import math, sys, subprocess, os
import numpy as np
from PIL import Image

W, H = 480, 270
HZ = 172                      # 地平线（水岸线）
SUN = (318, 160, 25)          # 太阳：x, y, 半径
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5
BAY = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]


def lerp(a, b, k):
    return a + (b - a) * k


def ramp(stops, v):
    """多段颜色渐变：stops = [(位置, (r,g,b)), ...]，v 为 0..1 数组"""
    v = np.clip(v, 0, 1)
    out = np.zeros(v.shape + (3,))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (v >= p0) & (v <= p1)
        k = ((v - p0) / (p1 - p0))[m][:, None]
        out[m] = np.array(c0) + (np.array(c1) - np.array(c0)) * k
    return out


# ---------------- 噪声 ----------------
_G = rng.random((512, 512))


def vnoise(x, y):
    xi, yi = np.floor(x).astype(int), np.floor(y).astype(int)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    g = lambda a, b: _G[(b) % 512, (a) % 512]
    return lerp(lerp(g(xi, yi), g(xi + 1, yi), u), lerp(g(xi, yi + 1), g(xi + 1, yi + 1), u), v)


def fbm(x, y, oct=4):
    s, a, f, n = 0, 0.5, 1.0, 0
    for _ in range(oct):
        s += a * vnoise(x * f, y * f); n += a; a *= 0.5; f *= 2.03
    return s / n


YY, XX = np.mgrid[0:H, 0:W].astype(float)


def draw(t=0.0):
    img = np.zeros((H, W, 3))
    # 1. 天空：靛紫 → 紫 → 品红 → 珊瑚 → 橙 → 地平线金
    v = YY / HZ
    sky = ramp([(0, (34, 26, 84)), (0.28, (84, 50, 136)), (0.52, (176, 80, 150)), (0.7, (240, 118, 112)),
                (0.86, (255, 166, 98)), (1.0, (255, 214, 146))], v)
    dsun = np.hypot((XX - SUN[0]) / 1.6, YY - SUN[1])
    glow = np.clip(1 - dsun / 170, 0, 1) ** 2
    sky = sky + (np.array((255, 214, 150)) - sky) * glow[..., None] * 0.55
    img[:] = sky
    # 星星（只在最上面）
    st = rng.random((H, W)) > 0.9965
    tw = (np.sin(t * 3 + XX * 0.7) > -0.3)
    m = st & (YY < 50) & tw
    img[m] = (230, 220, 255)
    # 2. 云：横向拉长的分层积云，底部被夕阳照亮、顶部偏紫
    for layer, (y0, y1, sx, sy, thr, sp) in enumerate(((22, 70, 90, 12, 0.56, 3.0), (60, 118, 70, 9, 0.53, 5.0), (105, 150, 55, 7, 0.55, 8.0))):
        band = (YY >= y0) & (YY < y1)
        nx = (XX + t * sp + layer * 300) / sx
        ny = YY / sy + layer * 17
        d = fbm(nx, ny)
        fade = np.clip(np.minimum(YY - y0, y1 - YY) / 10, 0, 1)
        dd = d * fade
        cm = band & (dd > thr)
        below = np.roll(dd, -2, 0) < dd       # 下沿（被照亮）
        above = np.roll(dd, 3, 0) < thr       # 上沿
        near = np.clip(1 - np.abs(XX - SUN[0]) / 260, 0, 1)
        hy = (YY - 20) / (HZ - 20)
        base = ramp([(0, (96, 62, 150)), (0.5, (196, 98, 160)), (1, (250, 140, 128))], hy * 0.8 + near * 0.3)
        lit = ramp([(0, (236, 140, 170)), (1, (255, 204, 150))], np.clip(near * 1.2 + hy * 0.4, 0, 1))
        core = base * 0.82 + np.array((40, 20, 70)) * 0.18
        col = np.where((cm & below & ~above)[..., None], lit, np.where((cm & above)[..., None], base * 0.92 + 18, core))
        edge = cm & (dd < thr + 0.025)
        col = np.where(edge[..., None], lerp(col, lit, 0.5), col)
        img[cm] = col[cm]
    # 3. 太阳 + 横穿太阳的细云带
    ds = np.hypot(XX - SUN[0], YY - SUN[1])
    sm = ds < SUN[2]
    sc = ramp([(0, (255, 250, 222)), (0.7, (255, 226, 160)), (1, (255, 186, 110))], ds / SUN[2])
    img[sm] = sc[sm]
    for k, yb in enumerate((150, 156, 163, 169)):
        stripe = sm & (np.abs(YY - yb - math.sin(t + k) * 0.6) < 0.9 + k * 0.3)
        img[stripe] = lerp(img[stripe], np.array((250, 150, 120)), 0.55)
    # 4. 远山（左），两层，空气透视
    for i, (base_y, amp, col, sc_) in enumerate(((150, 26, (128, 84, 160), 60), (160, 18, (96, 64, 138), 34))):
        hgt = base_y - amp * fbm(XX[0] / sc_ + i * 9, np.full(W, 3.0 + i), 3) - (XX[0] * 0.06) * 0
        hgt = hgt + np.clip((XX[0] - 230) / 40, 0, 4) * 8           # 右侧降下去，让位给城市
        mm = (YY >= hgt[None, :]) & (YY < HZ)
        shade = np.clip((YY - hgt[None, :]) / 30, 0, 1)
        c = np.array(col) * (1 - shade[..., None] * 0.15)
        rim = (YY - hgt[None, :] < 1.2) & mm
        img[mm] = c[mm]
        img[rim] = lerp(img[rim], np.array((255, 170, 140)), 0.45)
        if i == 1:      # 山脚零星灯火
            lights = mm & (YY > HZ - 6) & (rng.random((H, W)) > 0.985) & (XX < 230)
            img[lights] = (255, 214, 140)
    # 5. 城市天际线（右），逆光剪影 + 亮灯的窗 + 朝太阳一侧的轮廓光
    x = 236
    i = 0
    rr = np.random.default_rng(11)
    while x < W:
        bw = int(rr.integers(8, 22)); bh = int(rr.integers(18, 64))
        if 286 < x + bw and x < 350:          # 给太阳留出缺口：中间只有几栋矮楼
            bh = int(rr.integers(6, 12))
        top = HZ - bh
        body = (XX >= x) & (XX < x + bw) & (YY >= top) & (YY < HZ)
        g = np.clip((YY - top) / bh, 0, 1)
        bc = ramp([(0, (78, 56, 120)), (1, (42, 32, 80))], g)
        img[body] = bc[body]
        side = (XX == x + bw - 1) if x + bw / 2 < SUN[0] else (XX == x)
        img[body & side] = lerp(img[body & side], np.array((255, 160, 120)), 0.5)
        img[body & (YY == top)] = lerp(img[body & (YY == top)], np.array((255, 180, 140)), 0.5)
        for wy in range(top + 3, HZ - 2, 4):
            for wx in range(x + 2, x + bw - 2, 3):
                on = rr.random() < 0.38
                blink = math.sin(t * 2 + wx * 1.7 + wy) > -0.9
                if on and blink:
                    img[wy:wy + 2, wx:wx + 1] = (255, 206, 128) if rr.random() < 0.8 else (190, 210, 255)
        x += bw + int(rr.integers(0, 3))
        i += 1
    # 电视塔（通用造型）
    tx = 446
    tower = (np.abs(XX - tx) <= 1) & (YY > 70) & (YY < HZ)
    img[tower] = (52, 38, 90)
    pod = (np.abs(XX - tx) <= 4) & (np.abs(YY - 104) <= 3)
    img[pod] = (60, 44, 100); img[(np.abs(XX - tx) <= 4) & (YY == 104)] = (255, 200, 140)
    img[(np.abs(XX - tx) <= 0) & (YY > 50) & (YY <= 70)] = (70, 52, 110)
    if int(t * 2) % 2 == 0:
        img[49:51, tx:tx + 1] = (255, 90, 90)
    # 6. 水面：倒影（带水平波动）+ 碎金光柱 + 波纹高光
    above = img[:HZ].copy()
    for y in range(HZ, H):
        dy = y - HZ
        ry = max(0, HZ - 1 - int(dy * 0.92))
        amp = 0.6 + dy * 0.05
        off = (np.sin(XX[0] * 0.08 + y * 0.9 - t * 2.4) * amp + np.sin(XX[0] * 0.21 - y * 0.5 + t * 1.7) * amp * 0.5).astype(int)
        src = np.clip(np.arange(W) + off, 0, W - 1)
        row = above[ry, src]
        k = 0.62 - dy * 0.0015
        img[y] = row * k + np.array((44, 30, 96)) * (1 - k)
    wv = (YY >= HZ)
    lines = wv & (np.sin(XX * 0.12 + YY * 1.7 - t * 3) > 0.93) & (np.sin(YY * 0.9) > 0)
    img[lines] = lerp(img[lines], np.array((200, 150, 220)), 0.35)
    col_w = 10 + (YY - HZ) * 0.5
    glit = wv & (np.abs(XX - SUN[0] - np.sin(YY * 0.7 + t) * 2) < col_w) & \
        (fbm(XX / 3 + t * 0.8, YY * 1.3, 2) > 0.55 + (np.abs(XX - SUN[0]) / np.maximum(col_w + 1, 1)) * 0.22)
    img[glit] = lerp(img[glit], np.array((255, 236, 176)), 0.85)
    img[(YY == HZ)] = lerp(img[(YY == HZ)], np.array((255, 196, 150)), 0.4)
    # 7. 前景：河边栏杆（右下）、银杏树枝剪影（左上），边缘带夕阳轮廓光
    rail_y = 232
    rail = (XX > 250) & ((np.abs(YY - rail_y) < 1.5) | (np.abs(YY - (rail_y + 14)) < 1))
    posts = (XX > 250) & (YY > rail_y) & (YY < H) & (((XX - 254) % 46) < 3)
    img[rail | posts] = (36, 26, 64)
    img[(XX > 250) & (YY == rail_y - 1)] = (232, 140, 130)
    deck = (XX > 236) & (YY > 252)
    img[deck] = ramp([(0, (70, 50, 100)), (1, (50, 36, 82))], (YY - 252) / 18)[deck]
    img[(XX > 236) & (YY == 252)] = (210, 130, 140)
    # 银杏树枝：一根弯曲的主枝 + 几根小枝 + 成簇的扇形叶团（剪影，下沿和右沿带夕阳轮廓光）
    br = np.zeros((H, W), bool)
    def seg_line(x0, y0, x1, y1, w):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        m = np.zeros((H, W), bool)
        for k in range(n):
            px, py = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
            m |= (np.abs(XX - px) <= w) & (np.abs(YY - py) <= w)
        return m
    sway = math.sin(t * 0.9) * 1.2
    pts = [(-4, 4), (40, 14), (86, 22), (128, 34 + sway)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        br |= seg_line(x0, y0, x1, y1, 1.6)
    twigs = [((40, 14), (52, 34)), ((86, 22), (96, 44)), ((70, 19), (64, 40)), ((110, 28), (124, 50))]
    for (a0, b0) in twigs:
        br |= seg_line(a0[0], a0[1], b0[0], b0[1] + sway, 0.8)
    clumps = [(8, 10, 9), (24, 22, 8), (34, 6, 7), (52, 38, 8), (58, 16, 7), (66, 42, 7), (80, 10, 6), (96, 46, 7),
              (102, 26, 6), (118, 40, 6), (124, 54, 6), (132, 32, 5), (14, 30, 6), (44, 28, 5)]
    for (cx, cy, r) in clumps:
        cy = cy + sway * (cx / 130)
        d_ = np.hypot(XX - cx, (YY - cy) * 1.25)
        ang = np.arctan2(YY - cy, XX - cx)
        fan = r * (0.86 + 0.14 * np.cos(ang * 5))           # 扇形叶缘
        br |= d_ < fan
    img[br] = (40, 30, 58)
    lit = br & ~np.roll(br, -1, 0)                             # 下沿
    lit2 = br & ~np.roll(br, -1, 1)                            # 右沿
    img[lit | lit2] = (226, 128, 92)
    inner = br & ~np.roll(br, -2, 0) & ~lit
    img[inner] = (120, 66, 70)
    for (cx, cy, r) in clumps[::2]:
        hl = br & (np.hypot(XX - cx - r * 0.3, YY - cy - r * 0.4) < r * 0.35)
        img[hl] = (70, 46, 74)
    # 8. 飞鸟
    for bi in range(4):
        bx = int((120 + bi * 26 + t * 9) % 520) - 20
        by = int(62 + bi * 6 + math.sin(t * 2 + bi) * 2)
        flap = int(t * 6 + bi) % 2
        for dx, dy_ in ((-2, -flap), (-1, 0), (0, 1 - flap), (1, 0), (2, -flap)):
            if 0 <= bx + dx < W and 0 <= by + dy_ < H:
                img[by + dy_, bx + dx] = (46, 30, 70)
    return img


def quantize(img, pal=None, colors=64):
    a = np.clip(img + BAY[..., None] * 10, 0, 255).astype(np.uint8)
    im = Image.fromarray(a)
    if pal is None:
        q = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        return q, q
    return im.quantize(palette=pal, dither=Image.Dither.NONE), pal


if __name__ == '__main__':
    q, pal = quantize(draw(0.0))
    big = q.convert('RGB').resize((W * 4, H * 4), Image.NEAREST)
    big.save(os.path.join(OUT, 'sunset_32bit.png'))
    q.convert('RGB').save(os.path.join(OUT, 'sunset_32bit_native.png'))
    print('✓ 静帧', len(set(q.getdata())), '色')
    if '--video' in sys.argv:
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                               '-vf', 'scale=1920:1080:flags=neighbor', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p',
                               os.path.join(OUT, 'sunset_32bit.mp4')], stdin=subprocess.PIPE)
        for f in range(180):
            fr, _ = quantize(draw(f / 30), pal)
            ff.stdin.write(np.asarray(fr.convert('RGB')).tobytes())
        ff.stdin.close(); ff.wait()
        print('✓ 动态')
