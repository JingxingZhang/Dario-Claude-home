"""液态玻璃 UI 组件（Liquid Glass 风格）：镜头函数里“登记”，引擎在 1080p 高清阶段统一画。

为什么要分两步：玻璃要折射“已经画好的像素画面”，而且要在放大后的高清帧上画才有细腻的边缘高光；
所以镜头函数 fn(img, t, lt, v) 在 320×180 原生画布上画像素世界，同时调用这里的 g* 函数登记玻璃，
引擎（engine.MV.frame）放大画面后再按登记顺序画出所有玻璃，然后才叠歌词花字和署名。

坐标：除特别注明（hd=True）外，一律用原生坐标（320×180），内部 ×6 换算成高清。
born：出现时刻（全片秒，通常写 t - lt + 镜头内秒）；born=None 表示常驻、不做出现动画。
所有组件出现时都带弹簧动效（先横向、再纵向回弹，像一滴液体被拉开）。

本模块同名覆盖 props2 的 say / OS / popup / meter：先 `from props2 import *` 再 `from glassui import *`，
原来的气泡、弹窗、数值条就自动变成玻璃版，参数兼容。
"""
import math
import numpy as np
from PIL import ImageDraw
from glass import glass, spring, sdf_rrect, sdf_circle, sdf_union, sdf_heart, htext, tw, ink

GL = []           # 本帧登记的玻璃（闭包），引擎每帧清空
CUR = [0.0]       # 引擎写入的当前全片秒（给不带 t 参数的组件用）
S6 = 6
TXT = (40, 32, 56)
PALC = {'yel': (190, 124, 16), 'pink': (222, 60, 84), 'cyan': (24, 126, 186), 'red': (220, 50, 60),
        'white': (60, 50, 80), 'purp': (130, 70, 190), 'green': (40, 150, 90)}
TINTC = {'yel': (255, 214, 110), 'pink': (255, 170, 190), 'cyan': (150, 210, 255), 'red': (255, 160, 160),
         'white': (255, 255, 255), 'purp': (210, 180, 255), 'green': (170, 240, 200)}


def _cl(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def _pop(t, born, dur=99.0):
    """出现 / 消失进度：返回 (横向弹簧, 纵向弹簧, 消失系数, 已出现秒)；不在显示期返回 None"""
    if born is None:
        return 1.0, 1.0, 1.0, 9.0
    dt = t - born
    if dt < 0 or dt > dur + 0.35:
        return None
    return spring(dt), spring(dt - 0.07), 1 - _cl((dt - dur) / 0.35), dt


# ---------------- 基础组件 ----------------
def gchip(t, born, cx, cy, text, col=TXT, size=50, tint=(255, 255, 255), tint_a=0.12, dur=99.0, minw=0, hd=False, refr=1.0):
    """玻璃胶囊标签（cx,cy 为中心）。字色会按玻璃底下的亮度自动变深 / 变浅。"""
    p = _pop(t, born, dur)
    if not p:
        return
    sx, sy, out, dt = p
    w = max(minw, tw(text, size) + size * 1.2); h = size * 1.5
    X, Y = (cx, cy) if hd else (cx * S6, cy * S6)
    X = min(max(X, w / 2 + 12), 1920 - w / 2 - 12)

    def f(big):
        lum = glass(big, X, Y, w / 2 * sx * out, h / 2 * sy * out, t=t, tint=tint, tint_a=tint_a, refr=refr)
        if dt > 0.08 and out > 0.4:
            htext(big, X, Y + 2, text, size, ink(col, lum), alpha=_cl((dt - 0.08) / 0.15) * out)
    GL.append(f)


def gtag(t, born, cx, cy, text, pal='yel', size=54, dur=99.0):
    """语法 / 定性标签：按配色名着色的玻璃胶囊"""
    gchip(t, born, cx, cy, text, PALC.get(pal, TXT), size, TINTC.get(pal, (255, 255, 255)), 0.16, dur)


def gcard(t, born, cx, cy, hw, hh, r=30, tint=(255, 255, 255), tint_a=0.10, refr=1.0, mag=0.05,
          content=None, sdf=None, dur=99.0, shadow=0.22, alpha=1.0):
    """玻璃卡片 / 任意形状（cx,cy,hw,hh 原生坐标；r 为高清圆角）。
    sdf(HW, HH) -> (px,py)->距离：自定义形状；content(big, X, Y, HW, HH, lum)：在玻璃上画内容（高清坐标）。"""
    p = _pop(t, born, dur)
    if not p:
        return
    sx, sy, out, dt = p
    X, Y, HW, HH = cx * S6, cy * S6, hw * S6 * sx * out, hh * S6 * sy * out

    def f(big):
        sd = sdf(HW, HH) if sdf else (lambda px, py: sdf_rrect(px, py, HW, HH, r))
        lum = glass(big, X, Y, HW, HH, sd, t=t, tint=tint, tint_a=tint_a, refr=refr, mag=mag, shadow=shadow, alpha=alpha)
        if content and dt > 0.1 and out > 0.5:
            content(big, X, Y, HW, HH, lum)
    GL.append(f)


def gheart(t, born, cx, cy, size, tint=(255, 120, 150), tint_a=0.2, refr=1.3, mag=0.08, dur=99.0):
    """心形玻璃窗（size 为原生半宽左右）"""
    gcard(t, born, cx, cy, size, size, sdf=lambda HW, HH: (lambda px, py: sdf_heart(px, py, HW * 1.55)),
          tint=tint, tint_a=tint_a, refr=refr, mag=mag, dur=dur)


def glens(t, cx, cy, r, refr=1.2, mag=0.12, tint=(255, 255, 255), tint_a=0.04, alpha=1.0, shadow=0.12, hd=False):
    """圆形玻璃透镜 / 水滴：放在物件上会把它放大"""
    X, Y, RR = (cx, cy, r) if hd else (cx * S6, cy * S6, r * S6)
    GL.append(lambda big: glass(big, X, Y, RR, RR, t=t, refr=refr, mag=mag, tint=tint, tint_a=tint_a, alpha=alpha, shadow=shadow))


def gdrop(t, born, cx, cy, r=9, life=0.7):
    """溅起一颗玻璃水珠（物体落地、按钮按下、心跳时用）"""
    dt = t - born
    if 0 <= dt <= life:
        glens(t, cx, cy, r * spring(dt), 1.4, 0.2, alpha=1 - _cl((dt - life * 0.5) / (life * 0.5)), shadow=0.08)


def bubbles(t, n=4, seed=0, x0=0, x1=320, y0=0, y1=120, r0=4, r1=8, speed=6.0):
    """缓缓上浮的玻璃水滴（前奏、尾奏、梦境的氛围）"""
    for i in range(n):
        h = lambda k: (math.sin((i + 1) * 12.9898 + seed * 78.233 + k * 37.719) * 43758.5453) % 1
        ph = (t * speed / (y1 - y0 + 20) + h(1)) % 1
        x = x0 + h(2) * (x1 - x0) + math.sin(t * 0.9 + i * 2) * 6
        y = y1 + 10 - ph * (y1 - y0 + 20)
        a = _cl(min(ph / 0.15, (1 - ph) / 0.15))
        glens(t, x, y, r0 + h(3) * (r1 - r0), 1.3, 0.18, alpha=a, shadow=0.08)


def gmove(t, born, a, b, hh=15, tint=(255, 240, 180), tint_a=0.10, mag=0.14):
    """液态选择框：从 a=(x,y,hw) 流到 b=(x,y,hw)，移动中被拉长（选择题、切换选项、高亮某个词）"""
    if t < born:
        return
    k = spring(t - born)
    x, y = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
    hw = a[2] + (b[2] - a[2]) * k + abs(b[0] - x) * 0.35
    gcard(t, None, x, y, hw, hh, r=90, refr=1.3, mag=mag, tint=tint, tint_a=tint_a)


# ---------------- 覆盖 props2 的同名组件（参数兼容）----------------
def say(img, x, y, s, t=None, born=None, tail='l', cps=16, **kw):
    """对话气泡 → 玻璃胶囊：打字时胶囊跟着字变长；尾巴是一颗分离出来的小水滴。x,y 为左上角"""
    tt = CUR[0] if t is None else t
    if born is not None:
        if tt < born:
            return
        n = max(1, int((tt - born) * cps) + 1)
    else:
        n, born = len(s), tt - 9
    cur = s[:n]
    size = 50
    w = tw(cur, size) + size * 1.2; h = size * 1.5
    X = min(x * S6 + w / 2, 1920 - w / 2 - 12); Y = y * S6 + h / 2 + 4
    sx, sy = spring(tt - born), spring(tt - born - 0.07)
    dark = kw.get('os_', False)

    def f(big):
        lum = glass(big, X, Y, w / 2 * sx, h / 2 * sy, t=tt, tint=(40, 36, 70) if dark else (255, 255, 255), tint_a=0.4 if dark else 0.14)
        dx = -w / 2 + 26 if tail == 'l' else w / 2 - 26
        rr = 12 * spring(tt - born - 0.15)
        glass(big, X + dx, Y + h / 2 + 18, rr, rr, t=tt, shadow=0.1)
        htext(big, X, Y + 2, cur, size, ink(TXT, lum))
    GL.append(f)


def OS(img, x, y, s, t, born):
    """内心 OS：深色玻璃气泡"""
    say(img, x, y, 'OS：' + s, t, born, os_=True)


def popup(img, x, y, title, msg, btns=('确定',), sel=0, pressed=False, w=150, born=None):
    """系统弹窗 → 玻璃提示卡（标题 / 正文 / 一枚玻璃按钮）"""
    tt = CUR[0]
    hw, hh = w / 2, 30

    def content(big, X, Y, HW, HH, lum):
        htext(big, X, Y - 100, title, 38, ink((110, 100, 130), lum))
        htext(big, X, Y - 22, msg, 66, ink(TXT, lum))
        l2 = glass(big, X, Y + 92, 90 * (0.94 if pressed else 1), 34, t=tt, tint=(120, 170, 255), tint_a=0.3)
        htext(big, X, Y + 94, btns[sel if sel < len(btns) else 0], 44, ink((30, 90, 200), l2))
    gcard(tt, born, x + hw, y + hh, hw, hh, r=40, content=content, tint_a=0.22)


def meter(img, x, y, label, v, col=(255, 70, 110), w=70, show_pct=True, blink=False):
    """数值条 → 玻璃胶囊，里面是一段会涨的液体。x,y 为左上角"""
    tt = CUR[0]
    X0 = x * S6
    lw = tw(label, 46)
    Wd = lw + w * S6 * 0.9 + 190
    X, Y = X0 + Wd / 2, y * S6 + 52
    v = _cl(v)

    def f(big):
        lum = glass(big, X, Y, Wd / 2, 50, t=tt, tint_a=0.14)
        htext(big, X0 + 34, Y + 2, label, 46, ink(TXT, lum), anchor='l')
        tx0, tx1 = X0 + 50 + lw, X0 + Wd - 110
        dd = ImageDraw.Draw(big)
        dd.rounded_rectangle([tx0, Y - 12, tx1, Y + 12], 12, fill=(210, 206, 220))
        fx = tx0 + (tx1 - tx0) * v
        c = col if not (blink and int(tt * 6) % 2) else (255, 255, 255)
        if fx > tx0 + 24:
            dd.rounded_rectangle([tx0, Y - 12, fx, Y + 12], 12, fill=c)
            dd.rounded_rectangle([tx0 + 6, Y - 9, fx - 6, Y - 5], 3, fill=tuple(int(a + (255 - a) * 0.5) for a in c))
        if show_pct:
            htext(big, X0 + Wd - 66, Y + 2, f'{int(round(v * 100))}%', 42, ink(TXT, lum))
    GL.append(f)


def gsearch(t, born, cx, cy, hw, query, result='', typed_at=None, qcol=(226, 74, 70)):
    """玻璃搜索框：胶囊从中间拉开 → 打出 query → 结果淡入。cx,cy,hw 原生坐标"""
    p = _pop(t, born)
    if not p:
        return
    sx, _, _, dt = p
    X, Y, HW = cx * S6, cy * S6, hw * S6
    ta = (born if born is not None else t - 9) + 0.3 if typed_at is None else typed_at
    n = len(query) if t > ta else 0

    def f(big):
        lum = glass(big, X, Y, HW * sx, 56, t=t, tint_a=0.14)
        if sx < 0.8:
            return
        x0 = X - HW + 40
        dd = ImageDraw.Draw(big)
        g = ink((120, 110, 140), lum)
        dd.ellipse([x0, Y - 20, x0 + 30, Y + 10], outline=g, width=5)
        dd.line([(x0 + 26, Y + 6), (x0 + 40, Y + 20)], fill=g, width=6)
        htext(big, x0 + 64, Y + 2, query[:n], 46, qcol, anchor='l')
        if int(t * 2) % 2 and t < ta + 0.6:
            c = x0 + 64 + tw(query[:n], 46) + 6
            dd.rounded_rectangle([c, Y - 24, c + 4, Y + 24], 2, fill=(40, 120, 255))
        if result and t > ta + 0.6:
            htext(big, X + HW - 40 - tw(result, 36), Y + 2, result, 36, ink((110, 100, 130), lum), anchor='l', alpha=_cl((t - ta - 0.6) / 0.3))
    GL.append(f)


def gsign(cx, cy, text, scale=2):
    """配角 / 物件举的牌 → 头顶一枚玻璃小牌（cx,cy 为配角中心，原生坐标）"""
    gchip(CUR[0], None, cx, cy - 9 * scale - 6, text.strip('　 '), size=42, minw=160)
