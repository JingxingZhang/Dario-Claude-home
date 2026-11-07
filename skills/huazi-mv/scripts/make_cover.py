#!/usr/bin/env python3
"""3:4 竖版封面（1080×1440）：歌名大花字 + 一句高潮歌词 + 原唱标签 + 底部标签，背景用这首歌的配色和母题。
用法：python make_cover.py <项目目录> <输出.png>
读 config.py 里的 COVER（都可省略）：
  COVER = dict(palette='clear', scheme='clear', line='等到放晴的那天', kw=['放晴'], kw_scheme='kw_sun',
               flowers=True, icon='sun', label='综艺花字 MV')"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
proj, out = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], proj]
import numpy as np, skia
import engine as R
import huazi as hz
CW, CH = 1080, 1440
R.W, R.H = CW, CH
cv = dict(palette='clear', scheme='clear', line=None, kw=[], kw_scheme='kw_sun', flowers=False, icon='sun', label='综艺花字 MV')
cv.update(getattr(R.CFG, 'COVER', {}) or {})
T = R.make_textures()
s = skia.Surface(CW, CH); c = s.getCanvas()
top, bot, ink, acc = R.PALETTES[cv['palette']]
p = skia.Paint(); p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, CH)], [R.CI(top), R.CI(bot)]))
c.drawRect(skia.Rect.MakeWH(CW, CH), p)
warm = R.hx('#FFF6DD'); sx, sy = 870, 120
g = skia.Paint(); g.setBlendMode(skia.BlendMode.kScreen)
g.setShader(skia.GradientShader.MakeRadial(skia.Point(sx, sy), 900, [R.CI(warm, .55), R.CI(warm, .18), R.CI(warm, 0)], [0, .35, 1]))
c.drawRect(skia.Rect.MakeWH(CW, CH), g)
for k, img in enumerate(T['clouds'][:4]):
    cp = skia.Paint(); cp.setColorFilter(skia.ColorFilters.Blend(R.CI((1, 1, 1)), skia.BlendMode.kSrcIn)); cp.setAlphaf(.3)
    c.drawImage(img, [-300, 420, -150, 500][k], [120, 40, 720, 820][k], skia.SamplingOptions(skia.FilterMode.kLinear), cp)
rng = np.random.default_rng(3)
if cv['flowers']:
    stem = R.mixc(ink, R.hx('#6E7B4A'), .6)
    for y0, s0, n in ((1250, .55, 16), (1360, .8, 13)):
        for i in range(n):
            x = (i + rng.uniform(.1, .9)) / n * (CW + 80) - 40
            R.draw_flower(c, x, y0 + rng.uniform(-20, 30), s0 * rng.uniform(.8, 1.2), 1.0, R.FLOWER_COL, R.FLOWER_CEN, 1,
                          rot=rng.uniform(-15, 15), stem=rng.uniform(60, 140), stemcol=stem)
    R.draw_flower(c, 540, 1060, 2.2, 1.0, R.FLOWER_COL, R.FLOWER_CEN, 1, rot=6, stem=260, stemcol=stem)
    for i in range(26):
        c.save(); c.translate(rng.uniform(40, CW - 40), rng.uniform(640, 1180)); c.rotate(rng.uniform(0, 360)); c.scale(.5, .5 * rng.uniform(.5, 1))
        c.drawPath(R.petal_path(1), R.paint(R.FLOWER_COL, .9)); c.restore()
title = R.CFG.TITLE
n = len(title); size = min(300, 900 / max(1, n) * 1.05); step = size * 1.08
for k, ch in enumerate(title):
    hz.draw_glyph(c, ch, 540 + (k - (n - 1) / 2) * step, 330 + (k % 2) * 24, R.F('kl', size), hz.SCH[cv['scheme']], 1, rot=(k % 2 * 2 - 1) * 5)
for (x, y, r, col) in ((210, 180, 46, hz._hx('#FFC21A')), (880, 230, 34, (1, 1, 1)), (900, 470, 24, hz._hx('#FFC21A')), (170, 470, 20, (1, 1, 1))):
    hz.star4(c, x, y, r, col, 1, 12)
if cv['icon'] == 'sun':
    hz.sun_icon(c, 870, 120, 48, 1, 12)
yl = 640
if cv['line']:
    line = cv['line']; sb = R.F('sb', min(84, 900 / len(line)))
    ws = [sb.measureText(ch) for ch in line]; tot = sum(ws) + 10 * (len(line) - 1); x = 540 - tot / 2
    km = [False] * len(line)
    for w in cv['kw']:
        k = line.find(w)
        if k >= 0:
            for j in range(k, k + len(w)): km[j] = True
    for i, ch in enumerate(line):
        sch = hz.SCH[cv['kw_scheme']] if km[i] else hz.SCH[cv['scheme']]
        hz.draw_glyph(c, ch, x + ws[i] / 2, yl + 8 * math.sin(i * 1.3), sb, sch, 1, sc=1.14 if km[i] else 1, rot=(i % 2 * 2 - 1) * 3)
        x += ws[i] + 10
if getattr(R.CFG, 'ARTIST', None):
    hz.tag(c, R.CFG.ARTIST, 540, yl + 150, R.F('kl', 56), hz.SCH[cv['scheme']]['tag'], 1, rot=-5)
if cv['label']:
    hz.tag(c, cv['label'], 540, 1395, R.F('kl', 40), hz.SCH[cv['scheme']]['outer'], 1, rot=0)
gp = skia.Paint(); gp.setBlendMode(skia.BlendMode.kOverlay); gp.setAlphaf(.05)
c.drawImageRect(T['grain'][0], skia.Rect.MakeWH(CW, CH), skia.SamplingOptions(), gp)
s.makeImageSnapshot().save(out)
print('✓', out)
