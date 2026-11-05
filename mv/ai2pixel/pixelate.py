"""把 AI 生成的插画转成 64-bit 档像素画（原生 960×540，最多 160 色，放大 2 倍到 1920×1080）。
  python3 pixelate.py 输入.png 输出.png [--palette 共用调色板.png] [--colors 160] [--crop center|top]
做法：
  1. 裁成 16:9；
  2. 边缘保留的缩小：先轻微锐化，再用 BOX 缩到 960×540（比双线性更干净，不会糊）；
  3. 轻度色阶分离（让皮肤、头发、衣服的明暗变成几级清楚的色阶，去掉 AI 图那种连续的“喷枪感”）；
  4. 统一调色板：用 --palette 指定一张共用调色板，全片所有镜头颜色一致；不指定就从这张图里取 160 色；
  5. 4×4 有序抖动（规整的像素点阵，不用随机噪点）；
  6. 主要轮廓加深一档描边（像素画的边线感）；
  7. 最近邻放大 2 倍。"""
import argparse
import numpy as np
from PIL import Image, ImageFilter, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--palette', default=None); ap.add_argument('--colors', type=int, default=160)
ap.add_argument('--crop', default='center'); ap.add_argument('--w', type=int, default=960)
A = ap.parse_args()
W, H = A.w, A.w * 9 // 16

im = Image.open(A.src).convert('RGB')
sw, sh = im.size
if sw / sh > 16 / 9:
    nw = int(sh * 16 / 9); x0 = (sw - nw) // 2; im = im.crop((x0, 0, x0 + nw, sh))
else:
    nh = int(sw * 9 / 16); y0 = (sh - nh) // 2 if A.crop == 'center' else 0; im = im.crop((0, y0, sw, y0 + nh))
im = im.filter(ImageFilter.UnsharpMask(2, 80, 2))
small = im.resize((W, H), Image.BOX)
a = np.asarray(small).astype(np.float32)
# 色阶分离：每通道压到 24 级，保留色相
a = np.round(a / 255 * 23) / 23 * 255
# 有序抖动
bay = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5
bay = np.tile(bay, (H // 4 + 1, W // 4 + 1))[:H, :W][..., None]
a = np.clip(a + bay * 7, 0, 255).astype(np.uint8)
src = Image.fromarray(a)
if A.palette:
    pal = Image.open(A.palette).convert('RGB').quantize(A.colors, method=Image.Quantize.MEDIANCUT)
    q = src.quantize(palette=pal, dither=Image.Dither.NONE)
else:
    q = src.quantize(A.colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
out = np.asarray(q.convert('RGB')).astype(np.float32)
# 轮廓：亮度跳变大的地方，暗的一侧再压暗一档
lum = out.mean(2)
gy = np.abs(np.diff(lum, axis=0, prepend=lum[:1])); gx = np.abs(np.diff(lum, axis=1, prepend=lum[:, :1]))
edge = (np.maximum(gx, gy) > 60) & (lum < np.roll(lum, 1, 0) + 1)
out[edge] *= 0.82
res = Image.fromarray(out.clip(0, 255).astype(np.uint8)).resize((1920, 1080), Image.NEAREST)
res.save(A.dst)
print('✓', A.dst, f'{W}×{H}', len(set(np.asarray(q).ravel().tolist())), '色')
