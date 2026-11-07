import sys, math, skia, numpy as np
sys.path.insert(0, sys.argv[1])
import render_huazi_album as R
import huazi as hz
CW, CH = 1080, 1440
R.W, R.H = CW, CH
t = 252.0
T = R.make_textures()
s = skia.Surface(CW, CH); c = s.getCanvas()
pal = R.CLEAR
top, bot, ink, acc = pal
c.clear(R.CI(top))
# sky + sun + clouds
p = skia.Paint(); p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, CH)], [R.CI(top), R.CI(bot)]))
c.drawRect(skia.Rect.MakeWH(CW, CH), p)
sx, sy = 870, 120
warm = R.hx('#FFF6DD')
g = skia.Paint(); g.setBlendMode(skia.BlendMode.kScreen)
g.setShader(skia.GradientShader.MakeRadial(skia.Point(sx, sy), 900, [R.CI(warm, .6), R.CI(warm, .2), R.CI(warm, 0)], [0, .35, 1]))
c.drawRect(skia.Rect.MakeWH(CW, CH), g)
c.save(); c.translate(sx, sy)
for k in range(11):
    c.save(); c.rotate(k * 32.7 + 8)
    path = skia.Path(); path.moveTo(0, 0); path.lineTo(2000, -70 - 40 * (k % 3)); path.lineTo(2000, 70 + 40 * (k % 2)); path.close()
    rp = R.paint(warm, .05, blur=12); rp.setBlendMode(skia.BlendMode.kScreen); c.drawPath(path, rp); c.restore()
c.drawCircle(0, 0, 170, R.paint(warm, .4, blur=70))
c.restore()
for k, img in enumerate(T['clouds'][:4]):
    cp = skia.Paint(); cp.setColorFilter(skia.ColorFilters.Blend(R.CI((1, 1, 1)), skia.BlendMode.kSrcIn)); cp.setAlphaf(.35)
    c.drawImage(img, [-300, 420, -150, 500][k], [120, 40, 720, 820][k], skia.SamplingOptions(skia.FilterMode.kLinear), cp)
# flower field (two rows) + main flower
rng = np.random.default_rng(3)
stem = R.mixc(ink, R.hx('#6E7B4A'), .6)
for row, (y0, s0, n) in enumerate(((1250, .55, 16), (1360, .8, 13))):
    for i in range(n):
        x = (i + rng.uniform(.1, .9)) / n * (CW + 80) - 40
        R.draw_flower(c, x, y0 + rng.uniform(-20, 30), s0 * rng.uniform(.8, 1.2), 1.0, R.FLOWER_COL, R.FLOWER_CEN, 1,
                      rot=rng.uniform(-15, 15), stem=rng.uniform(60, 140), stemcol=stem)
R.draw_flower(c, 540, 1060, 2.2, 1.0, R.FLOWER_COL, R.FLOWER_CEN, 1, rot=6, stem=260, stemcol=stem)
# petals drifting
for i in range(26):
    x, y = rng.uniform(40, CW - 40), rng.uniform(640, 1180)
    c.save(); c.translate(x, y); c.rotate(rng.uniform(0, 360)); c.scale(.5, .5 * rng.uniform(.5, 1))
    c.drawPath(R.petal_path(1), R.paint(R.FLOWER_COL, .9)); c.restore()
# title 花字
kl = R.F('kl', 300)
for k, (ch, rot) in enumerate((('晴', -6), ('天', 5))):
    hz.draw_glyph(c, ch, 540 + (k * 2 - 1) * 165, 330 + (k * 24), kl, hz.SCH['clear'], 1, rot=rot)
for (x, y, r, col) in ((210, 180, 46, hz._hx('#FFC21A')), (880, 210, 34, (1, 1, 1)), (900, 470, 24, hz._hx('#FFC21A')), (170, 470, 20, (1, 1, 1))):
    hz.star4(c, x, y, r, col, 1, 12)
hz.sun_icon(c, 870, 120, 48, 1, 12)
# lyric line
sb = R.F('sb', 84)
line = '等到放晴的那天'
ws = [sb.measureText(ch) for ch in line]; tot = sum(ws) + 10 * 6; x = 540 - tot / 2
for i, ch in enumerate(line):
    sch = hz.SCH['kw_sun'] if ch in '放晴' else hz.SCH['clear']
    hz.draw_glyph(c, ch, x + ws[i] / 2, 640 + 8 * math.sin(i * 1.3), sb, sch, 1, sc=1.14 if ch in '放晴' else 1, rot=(i % 2 * 2 - 1) * 3)
    x += ws[i] + 10
hz.tag(c, '周杰伦', 540, 790, R.F('kl', 56), hz.SCH['clear']['tag'], 1, rot=-5)
hz.tag(c, '综艺花字 MV', 540, 1395, R.F('kl', 40), hz.SCH['clear']['outer'], 1, rot=0)
# grain + vignette (light)
gp = skia.Paint(); gp.setBlendMode(skia.BlendMode.kOverlay); gp.setAlphaf(.05)
c.drawImageRect(T['grain'][0], skia.Rect.MakeWH(CW, CH), skia.SamplingOptions(), gp)
s.makeImageSnapshot().save(sys.argv[2])
print('ok')
