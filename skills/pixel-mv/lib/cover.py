"""封面工具：16:9 横版直接取成片里最有戏的一帧；3:4 竖版（1080×1440）单独构图。

3:4 竖版的做法：原生 180×240 像素画 ×6 放大 → 柔光 → 项目登记的玻璃 → 标题（花字 + 玻璃底板）→
原唱 / 标签 / 署名玻璃胶囊。项目只需要在 mv.py 里写 COVER_3X4(img, t)：在 180×240 画布上画像素层，
可以顺手调用 glassui 的 g* 组件登记玻璃（坐标同样是原生坐标，×6 后正好是 1080×1440）。
构图建议：标题占上方 0–55 行，主画面 55–195 行，底部 195–240 行留给原唱、标签和署名。"""
import numpy as np
from PIL import Image
from pixlib import dither_grad, lerpc
import huazi as Z
import glassui as G
from glass import glass, htext, tw, post, ink

CW, CH, S = 180, 240, 6


def portrait_from(scene, x0=70, top=60):
    """把一张 320×180 的横版场景裁成竖版：取 x0 起 180 列，上方补 top 行天空（取场景顶行颜色向上加深）"""
    out = Image.new('RGB', (CW, CH))
    a = np.asarray(scene)
    c = tuple(int(v) for v in a[0, x0:x0 + CW].mean(0))
    out.paste(Image.fromarray(dither_grad(top + 10, CW, lerpc(c, (30, 40, 110), 0.3), c, 6)), (0, 0))
    out.paste(scene.crop((x0, 0, x0 + CW, min(180, CH - top))), (0, top))
    return out


def chip(big, cx, cy, s, size, col, tint=(255, 255, 255), ta=0.18):
    w = tw(s, size) + size * 1.3
    l = glass(big, cx, cy, w / 2, size * 0.78, t=1.0, tint=tint, tint_a=ta)
    htext(big, cx, cy + 2, s, size, ink(col, l))


def build_3x4(draw_native, t, title, artist='', tag='像素 MV', signature='', title_style=None):
    G.CUR[0] = t
    G.GL.clear()
    cv = Image.new('RGB', (CW, CH))
    draw_native(cv, t)
    items = list(G.GL); G.GL.clear()
    big = cv.resize((CW * S, CH * S), Image.NEAREST)
    post(big, 0.22, 0.12)
    for f in items:
        f(big)
    ts = dict(pal='pink', size=250, angle=-3, deco=('star', 'note'))
    ts.update(title_style or {})
    ts['size'] = min(ts.get('size', 250), int(900 / max(1, len(title)) / 1.05))
    glass(big, 540, 210, 420, 150, t=1.2, tint_a=0.10, refr=1.0, mag=0.03)
    Z.Line(-2, 99, title, cx=540, cy=200, stagger=0.0, pop=1.08, **{k: v for k, v in ts.items() if k in ('pal', 'size', 'angle', 'deco', 'kw', 'kwpal')}).draw(big, 3.0, 0.5)
    if artist:
        chip(big, 540, 1240, '原唱 · ' + artist, 56, (40, 32, 56))
    if tag:
        chip(big, 540, 1336, tag, 40, (222, 60, 84), (255, 180, 200), 0.2)
    if signature:
        sg = Z.signature(signature)
        glass(big, 540, 1440 - sg.height / 2 - 8, sg.width / 2 - 6, sg.height / 2 - 8, t=1.0, tint_a=0.14, shadow=0.1)
        big.paste(sg, (540 - sg.width // 2, 1440 - sg.height - 8), sg)
    return big
