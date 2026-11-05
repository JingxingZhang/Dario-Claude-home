"""液态玻璃（Liquid Glass 风格）高清渲染层：在 1920×1080 成帧上画会折射背景的玻璃。

做法（numpy + PIL，不依赖 GPU）：
  1. 用有向距离场（SDF）描述玻璃形状：圆角矩形 / 胶囊 / 圆 / 心形，可任意组合；
  2. 透镜折射：边缘一圈“斜面”把外侧背景压缩折进来（越靠边越强），中间轻微放大；
     R、G、B 三个通道折射量略有差别，边缘出现一点色散；
  3. 轻微毛玻璃模糊 + 着色 + 提亮；
  4. 镜面高光：沿边缘 2–3 像素的亮线，亮度随法线与光源方向的夹角变化，光源随时间缓慢转动，
     所以高光会沿着曲边“游走”；
  5. 柔和投影；
  6. 弹簧动画 spring()：出现时先横向、再纵向回弹，像一滴液体被拉开。
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import huazi as Z

FW, FH = 1920, 1080


def spring(dt, response=0.42, damping=0.78):
    """0→1 的阻尼弹簧（Apple 式参数：response 为周期秒数，damping 为阻尼比）。
    起步速度为 0（不会“跳”一下），过冲约 8%，约 0.5 秒稳定。"""
    if dt <= 0:
        return 0.0
    w = 2 * math.pi / response
    z = damping
    wd = w * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w * dt) * (math.cos(wd * dt) + z * w / wd * math.sin(wd * dt))


def ease_out(k):
    k = min(1.0, max(0.0, k))
    return 1 - (1 - k) ** 3


def ease_in(k):
    k = min(1.0, max(0.0, k))
    return k * k * k


def sdf_rrect(px, py, hw, hh, r):
    r = min(r, hw, hh)
    qx = np.abs(px) - (hw - r)
    qy = np.abs(py) - (hh - r)
    ox, oy = np.maximum(qx, 0), np.maximum(qy, 0)
    return np.sqrt(ox * ox + oy * oy) + np.minimum(np.maximum(qx, qy), 0) - r


def sdf_circle(px, py, r):
    return np.sqrt(px * px + py * py) - r


def sdf_ellipse(px, py, a, b):
    """椭圆（近似距离场），用于移动中被拉长的透镜"""
    return (np.sqrt((px / a) ** 2 + (py / b) ** 2) - 1) * min(a, b)


def sdf_union(*ds, k=18.0):
    """几块玻璃“融在一起”：平滑并集（k 越大，接缝越圆润，像两滴水相连）"""
    d = ds[0]
    for e in ds[1:]:
        h = np.clip(0.5 + 0.5 * (e - d) / k, 0, 1)
        d = e * (1 - h) + d * h - k * h * (1 - h)
    return d


def sdf_heart(px, py, s):
    """心形（Inigo Quilez 的心形距离场），s 为整体尺寸"""
    x = np.abs(px / s)
    y = -py / s + 0.55
    a = np.sqrt((x - 0.25) ** 2 + (y - 0.75) ** 2) - math.sqrt(2) / 4
    m = np.maximum(x + y, 0) * 0.5
    b = np.sqrt(np.minimum(x ** 2 + (y - 1) ** 2, (x - m) ** 2 + (y - m) ** 2)) * np.sign(x - y)
    return np.where(y + x > 1, a, b) * s


def glass(big, cx, cy, hw, hh, sdf=None, t=0.0, tint=(255, 255, 255), tint_a=0.10, bezel=None, refr=1.0,
          mag=0.05, blur=1.2, shadow=0.22, alpha=1.0, spec=1.0, lift=10, light=None, edge=1.0):
    """在 big（PIL RGB, 1920×1080）上画一块液态玻璃。cx,cy 中心；hw,hh 半宽半高；sdf(px,py)->距离（默认胶囊）"""
    if hw < 3 or hh < 3 or alpha <= 0.01:
        return 200.0
    if sdf is None:
        r = min(hw, hh)
        sdf = lambda px, py: sdf_rrect(px, py, hw, hh, r)
    bz = bezel or max(6.0, min(34.0, min(hw, hh) * 0.5))
    pad = int(bz * 1.1 + 26)
    BW, BH = big.size
    x0, x1 = int(max(0, cx - hw - pad)), int(min(BW, cx + hw + pad))
    y0, y1 = int(max(0, cy - hh - pad)), int(min(BH, cy + hh + pad + 14))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return 200.0
    crop = big.crop((x0, y0, x1, y1))
    reg = np.asarray(crop).astype(np.float32)
    src = np.asarray(crop.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else crop).astype(np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    px, py = xx - cx, yy - cy
    d = sdf(px, py)
    if shadow > 0:
        ds = sdf(px, py - 12)
        sh = (np.clip(1 - np.maximum(ds, 0) / 26, 0, 1) ** 2) * shadow * alpha
        sh = np.where(d > 0, sh, 0)
        reg *= (1 - sh[..., None])
    lum = 200.0
    if (d < 1).any():
        gy, gx = np.gradient(d)
        nl = np.sqrt(gx * gx + gy * gy) + 1e-6
        nx, ny = gx / nl, gy / nl
        depth = np.maximum(-d, 0)
        e = np.clip(1 - depth / bz, 0, 1)
        off = refr * bz * 0.95 * e ** 2.4
        sc = 1 - mag
        Hh, Ww = src.shape[:2]

        def samp(k, ch):
            sx = np.clip(np.rint(cx + px * sc + nx * off * k - x0), 0, Ww - 1).astype(np.int32)
            sy = np.clip(np.rint(cy + py * sc + ny * off * k - y0), 0, Hh - 1).astype(np.int32)
            return src[sy, sx, ch]
        col = np.stack([samp(1.12, 0), samp(1.0, 1), samp(0.88, 2)], -1)
        col = col * (1 - tint_a) + np.array(tint, np.float32) * tint_a
        col = col * 0.97 + lift
        col += (e ** 3)[..., None] * 16
        a = (light if light is not None else 2.35 + math.sin(t * 0.7) * 0.6)
        lx, ly = math.cos(a), math.sin(a)
        rim = np.clip(1 - depth / 2.6, 0, 1)
        dot = nx * lx + ny * ly
        s1 = np.clip(dot, 0, 1) ** 3
        s2 = np.clip(-dot, 0, 1) ** 3
        sp = rim * (0.28 + 0.95 * s1 + 0.45 * s2) * 255 * spec
        sp += (e ** 5) * s1 * 40 * spec
        col += sp[..., None]
        lum = float(col[d < -2].mean()) if (d < -2).any() else 200.0
        cov = np.clip(0.5 - d, 0, 1) * alpha
        reg = reg * (1 - cov[..., None]) + col * cov[..., None]
        hair = np.clip(1 - np.abs(d - 0.8) / 1.3, 0, 1) * 0.16 * alpha * edge
        reg *= (1 - hair[..., None])
    big.paste(Image.fromarray(np.clip(reg, 0, 255).astype(np.uint8)), (x0, y0))
    return lum


def ink(col, lum):
    """玻璃底亮就用原色字，底暗就换成浅色字（htext 会自动给浅色字加深色细描边）"""
    if lum >= 120:
        return col
    return tuple(int(c + (255 - c) * 0.82) for c in col)


# ---------------- 高清文字 ----------------
FAM = 'zcool-kuaile'


def tw(s, size, fam=FAM):
    return sum(Z.font(c, size, fam).getlength(c) for c in s) if s else 0


def htext(big, x, y, s, size, col, fam=FAM, anchor='c', alpha=1.0, stroke=0, stroke_col=(255, 255, 255)):
    """高清文字；anchor='c' 时 (x,y) 为中心，'l' 时 x 为左端、y 为垂直中心"""
    if not s or alpha <= 0.01:
        return
    if stroke == 0 and sum(col) > 600:          # 浅色字：加一圈深色细描边，保证在玻璃上看得清
        stroke, stroke_col = max(2, size // 18), (40, 32, 60)
    w = tw(s, size, fam)
    xx = x - w / 2 if anchor == 'c' else x
    lay = Image.new('RGBA', big.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for c in s:
        f = Z.font(c, size, fam)
        d.text((xx, y), c, font=f, fill=(*col, 255), anchor='lm', stroke_width=stroke, stroke_fill=(*stroke_col, 255))
        xx += f.getlength(c)
    if alpha < 1:
        a = np.asarray(lay).copy()
        a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
        lay = Image.fromarray(a)
    big.paste(lay, (0, 0), lay)


# ---------------- 整帧后期：柔光 + 暗角 ----------------
_VIG = None


def post(big, bloom=0.22, vig=0.14):
    global _VIG
    if big.size != (FW, FH):        # 非 16:9 画布（封面等）：只做柔光，暗角现算
        a = np.asarray(big).astype(np.float32)
        BW, BH = big.size
        small = big.resize((BW // 4, BH // 4), Image.BILINEAR)
        s = np.asarray(small).astype(np.float32)
        b = np.clip((s.mean(2, keepdims=True) - 175) / 80, 0, 1) * s
        bi = Image.fromarray(b.astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)).resize((BW, BH), Image.BILINEAR)
        a += np.asarray(bi).astype(np.float32) * bloom
        yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
        r = np.hypot((xx - BW / 2) / (BW / 2), (yy - BH / 2) / (BH / 2))
        a *= (1 - vig + vig * (1 - np.clip(r - 0.75, 0, 1) ** 1.5))[..., None]
        big.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        return
    a = np.asarray(big).astype(np.float32)
    if bloom > 0:
        small = big.resize((480, 270), Image.BILINEAR)
        s = np.asarray(small).astype(np.float32)
        lum = s.mean(2, keepdims=True)
        b = np.clip((lum - 175) / 80, 0, 1) * s
        bi = Image.fromarray(b.astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)).resize((FW, FH), Image.BILINEAR)
        a += np.asarray(bi).astype(np.float32) * bloom
    if vig > 0:
        if _VIG is None:
            yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
            r = np.hypot((xx - FW / 2) / (FW / 2), (yy - FH / 2) / (FH / 2))
            _VIG = (1 - np.clip(r - 0.75, 0, 1) ** 1.5)[..., None]
        a = a * (1 - vig + vig * _VIG)
    big.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
