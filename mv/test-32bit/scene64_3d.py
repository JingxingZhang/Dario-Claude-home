"""N64 年代风格（低多边形 3D）测试图：同一个晚霞湖边场景，全部用代码绘制，没有图片素材、没有 AI 生成。
自写的简易 3D 渲染器（numpy）：三角形光栅化 + 深度缓冲 + 透视校正贴图 + 双线性（模糊）贴图过滤 + 距离雾
+ 镜像倒影 + 16 位色（5-5-5）抖动 + 柔和放大。这些都是那个年代主机画面的标志特征。
  python3 scene64_3d.py           → sunset_64bit_3d.png
  python3 scene64_3d.py --video   → sunset_64bit_3d.mp4（6 秒：镜头缓慢横移、云飘、水波、灯闪）"""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageFilter

W, H = 384, 216                     # 内部分辨率（宽屏），最后柔和放大到 1080p
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(3)
WATER_Y = -0.5
FOG = np.array((246, 150, 120.0))
SUN_DIR = np.array([0.18, 0.06, 1.0]); SUN_DIR /= np.linalg.norm(SUN_DIR)


# ---------------- 贴图（都很小，靠双线性过滤放大，N64 式的柔和模糊）----------------
def tex_windows(seed):
    r = np.random.default_rng(seed)
    t = np.zeros((32, 16, 3)); t[:] = (54, 40, 92)
    for y in range(2, 32, 4):
        for x in range(1, 16, 3):
            if r.random() < 0.4:
                t[y:y + 2, x:x + 2] = (255, 200, 120) if r.random() < 0.85 else (180, 200, 255)
            else:
                t[y:y + 2, x:x + 2] = (40, 30, 70)
    return t


def tex_noise(n, c0, c1, seed, scale=1.0):
    r = np.random.default_rng(seed)
    g = r.random((n // 4 + 2, n // 4 + 2))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
    v = np.asarray(im).astype(float) / 255
    return np.array(c0) + (np.array(c1) - np.array(c0)) * v[..., None]


TEX = {
    'win1': tex_windows(1), 'win2': tex_windows(2), 'win3': tex_windows(3),
    'stone': tex_noise(16, (150, 112, 132), (186, 140, 150), 4),
    'leaf': tex_noise(16, (200, 120, 40), (255, 196, 70), 5),
    'rock': tex_noise(16, (90, 64, 130), (120, 84, 150), 6),
    'plain': np.ones((2, 2, 3)) * 255,
}
CLOUD = tex_noise(64, (0, 0, 0), (1, 1, 1), 9)[..., 0]
WAVE = tex_noise(32, (0, 0, 0), (1, 1, 1), 11)[..., 0]


def bilinear(tex, u, v):
    h, w = tex.shape[:2]
    u = u * w - 0.5; v = v * h - 0.5
    x0 = np.floor(u).astype(int); y0 = np.floor(v).astype(int)
    fx = (u - x0)[..., None]; fy = (v - y0)[..., None]
    x0 %= w; y0 %= h; x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    t = tex if tex.ndim == 3 else tex[..., None]
    c = (t[y0, x0] * (1 - fx) + t[y0, x1] * fx) * (1 - fy) + (t[y1, x0] * (1 - fx) + t[y1, x1] * fx) * fy
    return c if tex.ndim == 3 else c[..., 0]


# ---------------- 几何 ----------------
TRIS = []          # (3 个顶点, 3 个 uv, 颜色, 贴图名, 是否受光)


def quad(p0, p1, p2, p3, col, tex='plain', uv=((0, 0), (1, 0), (1, 1), (0, 1)), lit=True):
    TRIS.append(((p0, p1, p2), (uv[0], uv[1], uv[2]), col, tex, lit))
    TRIS.append(((p0, p2, p3), (uv[0], uv[2], uv[3]), col, tex, lit))


def box(x0, y0, z0, x1, y1, z1, col, tex='plain', tu=1.0, tv=1.0, front_tex=None):
    P = lambda x, y, z: np.array((x, y, z), float)
    a, b, c, d = P(x0, y0, z0), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0)
    e, f, g, h = P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)
    ft = front_tex or tex
    uvf = ((0, tv), (tu, tv), (tu, 0), (0, 0))
    quad(a, b, c, d, col, ft, uvf)                 # 前（朝镜头）
    quad(f, e, h, g, col, tex, uvf)                # 后
    quad(e, a, d, h, col, ft, uvf)                 # 左
    quad(b, f, g, c, col, ft, uvf)                 # 右
    quad(d, c, g, h, col, tex)                     # 顶


def build():
    TRIS.clear()
    # 岸边平台 + 侧面
    quad(np.array((-9, 0, -2.0)), np.array((9, 0, -2.0)), np.array((9, 0, 3.6)), np.array((-9, 0, 3.6)),
         (200, 160, 170), 'stone', ((0, 0), (12, 0), (12, 4), (0, 4)))
    quad(np.array((-9, 0, 3.6)), np.array((9, 0, 3.6)), np.array((9, WATER_Y - 0.3, 3.6)), np.array((-9, WATER_Y - 0.3, 3.6)), (120, 90, 120), 'stone',
         ((0, 0), (12, 0), (12, 0.5), (0, 0.5)))
    # 栏杆
    for x in np.arange(-8, 8.1, 2.0):
        box(x - 0.05, 0, 3.3, x + 0.05, 1.0, 3.4, (60, 46, 80))
    box(-8, 0.95, 3.3, 8, 1.05, 3.4, (70, 54, 92))
    box(-8, 0.5, 3.32, 8, 0.56, 3.38, (70, 54, 92))
    # 路灯
    for x in (-5.5, 5.5):
        box(x - 0.05, 0, 2.9, x + 0.05, 2.8, 3.0, (56, 44, 78))
        box(x - 0.18, 2.8, 2.82, x + 0.18, 2.95, 3.08, (255, 230, 170), lit=False) if False else box(x - 0.18, 2.8, 2.82, x + 0.18, 2.95, 3.08, (255, 230, 170))
    # 两个人（背影）：我（藏青毛衣）和你（米白外套 + 红围巾）
    def person(x, body, scarf=None, hair=(52, 40, 52), h=1.0):
        box(x - 0.13, 0, 2.55, x - 0.02, 0.62 * h, 2.7, (70, 66, 82))
        box(x + 0.02, 0, 2.55, x + 0.13, 0.62 * h, 2.7, (70, 66, 82))
        box(x - 0.22, 0.6 * h, 2.5, x + 0.22, 1.22 * h, 2.75, body)
        if scarf:
            box(x - 0.2, 1.12 * h, 2.48, x + 0.2, 1.26 * h, 2.77, scarf)
            box(x + 0.05, 0.85 * h, 2.47, x + 0.15, 1.15 * h, 2.5, scarf)
        box(x - 0.15, 1.24 * h, 2.52, x + 0.15, 1.54 * h, 2.74, (240, 200, 176))
        box(x - 0.17, 1.33 * h, 2.5, x + 0.17, 1.58 * h, 2.76, hair)
    person(-0.45, (66, 92, 150))
    person(0.25, (236, 226, 208), (226, 74, 70), (110, 70, 58), 0.94)
    # 银杏树（左前景）：树干 + 低多边形树冠
    box(-6.15, 0, 6.0, -5.85, 3.2, 6.3, (110, 80, 66))
    cx, cy, cz = -6.0, 4.3, 6.2
    ico = [(0, 1.6, 0), (1.9, 0.4, 0), (0.6, 0.4, 1.7), (-1.6, 0.4, 1.0), (-1.6, 0.4, -1.0), (0.6, 0.4, -1.7), (1.4, -1.1, 0.9), (-0.3, -1.2, 1.4),
           (-1.6, -1.0, 0), (-0.3, -1.2, -1.4), (1.4, -1.1, -0.9), (0, -1.7, 0)]
    V = [np.array((cx + a * 1.5, cy + b, cz + c * 1.2)) for a, b, c in ico]
    F = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5), (0, 5, 1), (1, 6, 2), (2, 7, 3), (3, 8, 4), (4, 9, 5), (5, 10, 1),
         (2, 6, 7), (3, 7, 8), (4, 8, 9), (5, 9, 10), (1, 10, 6), (11, 7, 6), (11, 8, 7), (11, 9, 8), (11, 10, 9), (11, 6, 10)]
    for f in F:
        TRIS.append(((V[f[0]], V[f[1]], V[f[2]]), ((0, 0), (1, 0), (0.5, 1)), (255, 255, 255), 'leaf', True))
    # 对岸城市（右）
    r = np.random.default_rng(21)
    x = 6.0
    while x < 70:
        w = r.uniform(3, 7); h = r.uniform(5, 22); z0 = r.uniform(78, 92)
        if 20 < x < 34:
            h = r.uniform(2, 4)
        box(x, WATER_Y, z0, x + w, h, z0 + w, (255, 255, 255), 'win%d' % r.integers(1, 4), w / 3, h / 4)
        x += w + r.uniform(0.3, 2)
    box(58, WATER_Y, 96, 59, 46, 97, (86, 64, 120))                          # 电视塔
    box(56.8, 30, 94.8, 60.2, 33, 98.2, (96, 72, 132))
    # 左边远山（低多边形山脊）
    ridge = [(-160, 0), (-120, 14), (-90, 9), (-60, 18), (-30, 11), (0, 15), (20, 6), (34, 0)]
    for (x0, h0), (x1, h1) in zip(ridge, ridge[1:]):
        a, b = np.array((x0, WATER_Y, 140.0)), np.array((x1, WATER_Y, 140.0))
        c, d = np.array((x1, h1, 140.0)), np.array((x0, h0, 140.0))
        quad(a, b, c, d, (255, 255, 255), 'rock', ((0, 1), (4, 1), (4, 0), (0, 0)))


# ---------------- 相机与光栅化 ----------------
def camera(t):
    yaw = math.radians(-6 + math.sin(t * 0.5) * 1.5)
    pitch = math.radians(-4)
    pos = np.array((0.2 + math.sin(t * 0.5) * 0.15, 1.75, -1.6))
    cy_, sy_ = math.cos(yaw), math.sin(yaw); cp, sp = math.cos(pitch), math.sin(pitch)
    Ry = np.array(((cy_, 0, -sy_), (0, 1, 0), (sy_, 0, cy_)))
    Rx = np.array(((1, 0, 0), (0, cp, sp), (0, -sp, cp)))
    return pos, Rx @ Ry


F_ = H / 2 / math.tan(math.radians(30))


def project(p, pos, R):
    c = R @ (p - pos)
    return c


YY, XX = np.mgrid[0:H, 0:W].astype(float)


def raster(img, zb, tris, pos, R, light_on=True, mirror=False, t=0.0):
    for (verts, uvs, col, tex, lit) in tris:
        if mirror:
            verts = [np.array((v[0], 2 * WATER_Y - v[1], v[2])) for v in verts]
        cs = [project(v, pos, R) for v in verts]
        if min(c[2] for c in cs) < 0.15:
            continue
        sx = [W / 2 + F_ * c[0] / c[2] for c in cs]
        sy = [H / 2 - F_ * c[1] / c[2] for c in cs]
        x0, x1 = max(0, int(min(sx))), min(W - 1, int(max(sx)) + 1)
        y0, y1 = max(0, int(min(sy))), min(H - 1, int(max(sy)) + 1)
        if x0 > x1 or y0 > y1:
            continue
        px = XX[y0:y1 + 1, x0:x1 + 1] + 0.5; py = YY[y0:y1 + 1, x0:x1 + 1] + 0.5
        (ax, bx, cx), (ay, by, cy) = sx, sy
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            continue
        w0 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
        w1 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not m.any():
            continue
        iz = [1 / c[2] for c in cs]
        izp = w0 * iz[0] + w1 * iz[1] + w2 * iz[2]
        z = 1 / izp
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m &= z < sub
        if not m.any():
            continue
        u = (w0 * uvs[0][0] * iz[0] + w1 * uvs[1][0] * iz[1] + w2 * uvs[2][0] * iz[2]) * z
        v = (w0 * uvs[0][1] * iz[0] + w1 * uvs[1][1] * iz[1] + w2 * uvs[2][1] * iz[2]) * z
        tc = bilinear(TEX[tex], u, v) * (np.array(col) / 255)
        n = np.cross(verts[1] - verts[0], verts[2] - verts[0]); n = n / (np.linalg.norm(n) + 1e-9)
        if mirror:
            n = -n
        if lit:
            amb = np.array((0.5, 0.42, 0.62))
            dif = max(0.0, float(np.dot(n, -SUN_DIR))) * 0.5 + max(0.0, float(n[1])) * 0.35
            rim = max(0.0, float(np.dot(n, np.array((0.3, 0.2, 0.9))))) * 0.35
            tc = tc * (amb + dif) + np.array((255, 170, 120)) * rim * 0.4
        fog = np.clip((z - 10) / 240, 0, 0.6)[..., None]
        tc = tc * (1 - fog) + FOG * fog
        blk = img[y0:y1 + 1, x0:x1 + 1]
        blk[m] = tc[m]
        sub[m] = z[m]


def sky_and_water(pos, R, t):
    dx = (XX + 0.5 - W / 2) / F_; dy = -(YY + 0.5 - H / 2) / F_
    d = np.stack([dx, dy, np.ones_like(dx)], -1) @ R          # 相机坐标 → 世界方向
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    el = d[..., 1]
    def skycol(e):
        stops = [(-0.05, (255, 206, 150)), (0.05, (252, 158, 110)), (0.16, (214, 98, 140)), (0.32, (120, 64, 150)), (0.6, (44, 30, 92))]
        out = np.zeros(e.shape + (3,))
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            k = np.clip((e - p0) / (p1 - p0), 0, 1)[..., None]
            sel = (e >= p0)[..., None]
            out = np.where(sel, np.array(c0) + (np.array(c1) - np.array(c0)) * k, out)
        out[e < stops[0][0]] = stops[0][1]
        return out
    img = skycol(el)
    sd = np.clip(np.sum(d * SUN_DIR, -1), -1, 1)
    glow = np.clip((sd - 0.9) / 0.1, 0, 1) ** 3
    img = img + (np.array((255, 236, 190)) - img) * glow[..., None] * 0.7
    disk = sd > 0.9985
    img[disk] = (255, 244, 210)
    up = el > 0.01
    cu = d[..., 0] / np.maximum(el, 0.01) * 0.08 + t * 0.01
    cv = d[..., 2] / np.maximum(el, 0.01) * 0.08
    cl = bilinear(CLOUD, cu, cv)
    cm = up & (cl > 0.55)
    ccol = np.array((250, 160, 150)) * 0.6 + img * 0.4
    a_ = np.clip((cl - 0.55) * 6, 0, 1)[..., None] * np.clip(el * 6, 0, 1)[..., None]
    img = np.where(cm[..., None], img * (1 - a_) + ccol * a_, img)
    zb = np.full((H, W), np.inf)
    wm = el < 0
    tt = (WATER_Y - pos[1]) / np.minimum(d[..., 1], -1e-4)
    zb[wm] = tt[wm] * (d[..., :][wm] @ (R.T @ np.array((0, 0, 1.0))) if False else 1)
    # 水面：反射天空 + 波纹 + 太阳光柱
    hx = pos[0] + d[..., 0] * tt; hz = pos[2] + d[..., 2] * tt
    wv = bilinear(WAVE, hx * 0.15 + t * 0.05, hz * 0.05 - t * 0.03)
    refl = skycol(-el + (wv - 0.5) * 0.04) * 0.62 + np.array((60, 40, 110)) * 0.38
    da = np.abs(np.arctan2(d[..., 0], d[..., 2]) - math.atan2(SUN_DIR[0], SUN_DIR[2]))
    width = 0.02 + (-el) * 0.5
    sp = np.clip(1 - da / np.maximum(width, 1e-3), 0, 1) * np.clip((wv - 0.42) * 5, 0, 1)
    refl = refl + (np.array((255, 228, 176)) - refl) * (sp ** 1.5)[..., None] * 0.85
    fogw = np.clip(tt / 160, 0, 0.7)[..., None]
    refl = refl * (1 - fogw) + FOG * fogw
    img = np.where(wm[..., None], refl, img)
    zz = np.where(wm, tt, np.inf)
    return img, zz, wm, hx, hz


def render(t=0.0):
    pos, R = camera(t)
    img, zb, wm, hx, hz = sky_and_water(pos, R, t)
    # 倒影：把场景沿水面镜像画到一张单独的图上，再按波纹扭动后叠到水面
    rimg = img.copy(); rzb = np.full((H, W), np.inf)
    raster(rimg, rzb, TRIS, pos, R, mirror=True, t=t)
    hit = np.isfinite(rzb) & wm
    off = (np.sin(YY * 0.9 + t * 3) * 1.2).astype(int)
    src_x = np.clip(XX.astype(int) + off, 0, W - 1)
    rs = rimg[YY.astype(int), src_x]
    hs = hit[YY.astype(int), src_x]
    img = np.where((hs & wm)[..., None], img * 0.45 + rs * 0.5, img)
    raster(img, zb, TRIS, pos, R, t=t)
    # 路灯光晕（N64 式的加法光斑）
    for x in (-5.5, 5.5):
        c = R @ (np.array((x, 2.87, 2.95)) - pos)
        if c[2] > 0.2:
            sx, sy = W / 2 + F_ * c[0] / c[2], H / 2 - F_ * c[1] / c[2]
            g = np.clip(1 - np.hypot(XX - sx, YY - sy) / (14 + math.sin(t * 7) * 0.5), 0, 1) ** 2
            img = img + np.array((255, 190, 120)) * g[..., None] * 0.6
    # 16 位色（每通道 5 位）+ 4×4 抖动
    bay = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5)
    bay = np.tile(bay, (H // 4 + 1, W // 4 + 1))[:H, :W][..., None]
    q = np.clip(np.floor((np.clip(img, 0, 255) + bay * 8) / 8) * 8 + 4, 0, 255).astype(np.uint8)
    im = Image.fromarray(q).resize((1920, 1080), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    return im


if __name__ == '__main__':
    build()
    render(0.0).save(os.path.join(OUT, 'sunset_64bit_3d.png'))
    print('✓ 静帧', len(TRIS), '个三角形')
    if '--video' in sys.argv:
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '30', '-i', '-',
                               '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'sunset_64bit_3d.mp4')], stdin=subprocess.PIPE)
        for f in range(180):
            ff.stdin.write(np.asarray(render(f / 30)).tobytes())
        ff.stdin.close(); ff.wait()
        print('✓ 动态')
