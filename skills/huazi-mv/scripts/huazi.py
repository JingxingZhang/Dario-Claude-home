# -*- coding: utf-8 -*-
"""综艺花字 (variety-show caption) glyph renderer + stickers."""
import skia, math

def _hx(s): s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
def _ci(c, a=1.):
    a = max(0., min(1., a)); return skia.Color(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255), int(a * 255))

def scheme(f1, f2, outer, shadow, inner='#FFFFFF', tag=None):
    return dict(f1=_hx(f1), f2=_hx(f2), outer=_hx(outer), shadow=_hx(shadow), inner=_hx(inner), tag=_hx(tag or outer))

SCH = {
    # sections
    'memory': scheme('#FFF1A8', '#FFAE1A', '#6A3B17', '#3D1F08'),
    'mist':   scheme('#FFFFFF', '#BFE2FF', '#2D4D70', '#132539'),
    'storm':  scheme('#FFFFFF', '#A9DBFF', '#1660C9', '#04122A', tag='#1660C9'),
    'dusk':   scheme('#FFF0D0', '#FF9636', '#7E2F08', '#3E1503'),
    'night':  scheme('#FFFFFF', '#C9B8FF', '#5130B8', '#0B0624', tag='#5130B8'),
    'clear':  scheme('#FFFFFF', '#FFE266', '#1E63B8', '#0C2E5C', tag='#FF7A1A'),
    # keywords
    'kw_flower': scheme('#FFF59A', '#FFB000', '#C43E00', '#5A1A00'),
    'kw_rain':   scheme('#EFFAFF', '#4FB4FF', '#0B3E86', '#021431'),
    'kw_sun':    scheme('#FFF3A6', '#FF8A00', '#C22F00', '#4D1000'),
    'kw_love':   scheme('#FFE3EE', '#FF5C93', '#A3123F', '#40041A'),
    'kw_wind':   scheme('#F0FFFB', '#5EE6C8', '#0B6F6A', '#022B2A'),
    'kw_bye':    scheme('#F2F2FF', '#9AA8FF', '#3C3A9E', '#121038'),
}

def draw_glyph(c, ch, x, y, font, sch, a=1., sc=1., rot=0., blur=0., skew=0., glow=0.):
    """Layered: hard shadow, outer stroke, white stroke, gradient fill, gloss."""
    if a <= .004 or sc <= .01: return
    size = font.getSize()
    m = font.getMetrics(); w = font.measureText(ch)
    base = -(m.fAscent + m.fDescent) / 2
    ox = -w / 2
    c.save(); c.translate(x, y)
    if rot: c.rotate(rot)
    if sc != 1: c.scale(sc, sc)
    if skew: c.skew(skew, 0)
    mf = skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur) if blur > .4 else None
    def P(col, alpha, stroke=0.):
        p = skia.Paint(AntiAlias=True); p.setColor(_ci(col, alpha))
        if stroke:
            p.setStyle(skia.Paint.kStrokeAndFill_Style); p.setStrokeWidth(stroke)
            p.setStrokeJoin(skia.Paint.kRound_Join)
        if mf: p.setMaskFilter(mf)
        return p
    sw_o = size * .20; sw_i = size * .095
    if glow > .01:
        g = P(sch['outer'], a * glow, sw_o * 1.4); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * .22))
        c.drawString(ch, ox, base, font, g)
    # hard drop shadow
    c.drawString(ch, ox + size * .055, base + size * .075, font, P(sch['shadow'], a * .9, sw_o))
    c.drawString(ch, ox, base, font, P(sch['outer'], a, sw_o))
    c.drawString(ch, ox, base, font, P(sch['inner'], a, sw_i))
    fp = skia.Paint(AntiAlias=True)
    fp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, -size * .42), skia.Point(0, size * .42)],
                                                [_ci(sch['f1'], a), _ci(sch['f2'], a)]))
    if mf: fp.setMaskFilter(mf)
    c.drawString(ch, ox, base, font, fp)
    # gloss on the upper part
    c.save(); c.clipRect(skia.Rect.MakeLTRB(-size, -size, size, -size * .08))
    gp = skia.Paint(AntiAlias=True); gp.setColor(_ci((1, 1, 1), a * .38))
    if mf: gp.setMaskFilter(mf)
    c.drawString(ch, ox, base, font, gp)
    c.restore()
    c.restore()

def draw_string(c, s, x, y, font, sch, a=1., track=0., sc=1., rot=0., align='c'):
    ws = [font.measureText(ch) for ch in s]
    tot = sum(ws) + track * (len(s) - 1)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    cx = -tot / 2 if align == 'c' else 0
    for ch, w in zip(s, ws):
        draw_glyph(c, ch, cx + w / 2, 0, font, sch, a)
        cx += w + track
    c.restore()
    return tot

# ---------------------------------------------------------------- stickers
def star4(c, x, y, r, col, a, rot=0.):
    if a < .01 or r < .5: return
    p = skia.Path()
    for k in range(8):
        ang = math.pi / 4 * k + math.radians(rot)
        rr = r if k % 2 == 0 else r * .28
        px, py = x + rr * math.cos(ang), y + rr * math.sin(ang)
        (p.moveTo if k == 0 else p.lineTo)(px, py)
    p.close()
    sp = skia.Paint(AntiAlias=True); sp.setColor(_ci((1, 1, 1), a)); sp.setStyle(skia.Paint.kStrokeAndFill_Style)
    sp.setStrokeWidth(r * .35); sp.setStrokeJoin(skia.Paint.kRound_Join)
    c.drawPath(p, sp)
    fp = skia.Paint(AntiAlias=True); fp.setColor(_ci(col, a)); c.drawPath(p, fp)

def heart(c, x, y, r, col, a, rot=0.):
    if a < .01: return
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); p.moveTo(0, r * .9)
    p.cubicTo(-r * 1.6, -r * .1, -r * .7, -r * 1.3, 0, -r * .45)
    p.cubicTo(r * .7, -r * 1.3, r * 1.6, -r * .1, 0, r * .9); p.close()
    o = skia.Paint(AntiAlias=True); o.setColor(_ci((1, 1, 1), a)); o.setStyle(skia.Paint.kStrokeAndFill_Style); o.setStrokeWidth(r * .4)
    o.setStrokeJoin(skia.Paint.kRound_Join)
    c.drawPath(p, o); f = skia.Paint(AntiAlias=True); f.setColor(_ci(col, a)); c.drawPath(p, f)
    c.restore()

def drop(c, x, y, r, col, a, rot=0.):
    if a < .01: return
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); p.moveTo(0, -r * 1.7); p.cubicTo(r * .9, -r * .5, r, 0, r, r * .3)
    p.arcTo(skia.Rect.MakeLTRB(-r, -r * .7, r, r * 1.3), 0, 180, False); p.cubicTo(-r, 0, -r * .9, -r * .5, 0, -r * 1.7); p.close()
    o = skia.Paint(AntiAlias=True); o.setColor(_ci((1, 1, 1), a)); o.setStyle(skia.Paint.kStrokeAndFill_Style); o.setStrokeWidth(r * .45)
    c.drawPath(p, o); f = skia.Paint(AntiAlias=True); f.setColor(_ci(col, a)); c.drawPath(p, f)
    c.drawCircle(-r * .35, r * .1, r * .22, _p((1, 1, 1), a * .8))
    c.restore()

def _p(col, a, stroke=0.):
    p = skia.Paint(AntiAlias=True); p.setColor(_ci(col, a))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap)
    return p

def speed_lines(c, x, y, h, col, a, n=3, phase=0.):
    for k in range(n):
        yy = y - h / 2 + h * (k + .5) / n
        L = 60 + 30 * math.sin(phase * 6 + k * 2)
        c.drawLine(x - L, yy, x, yy, _p((1, 1, 1), a, 11))
        c.drawLine(x - L, yy, x, yy, _p(col, a, 6))

def sun_icon(c, x, y, r, a, rot=0.):
    c.save(); c.translate(x, y); c.rotate(rot)
    for k in range(10):
        c.save(); c.rotate(k * 36)
        c.drawLine(0, -r * 1.35, 0, -r * 1.85, _p((1, 1, 1), a, r * .42))
        c.drawLine(0, -r * 1.35, 0, -r * 1.85, _p(_hx('#FF9A1F'), a, r * .22))
        c.restore()
    c.drawCircle(0, 0, r * 1.1, _p((1, 1, 1), a))
    c.drawCircle(0, 0, r, _p(_hx('#FFC21A'), a))
    c.drawCircle(-r * .32, -r * .1, r * .1, _p(_hx('#5A2A00'), a)); c.drawCircle(r * .32, -r * .1, r * .1, _p(_hx('#5A2A00'), a))
    sm = skia.Path(); sm.moveTo(-r * .35, r * .25); sm.quadTo(0, r * .6, r * .35, r * .25)
    c.drawPath(sm, _p(_hx('#5A2A00'), a, r * .1))
    c.restore()

def tag(c, text, x, y, font, bg, a=1., rot=-6., sc=1., fg=(1, 1, 1)):
    """Rounded label sticker."""
    if a < .01 or sc < .01: return
    w = sum(font.measureText(ch) for ch in text) + 4 * (len(text) - 1)
    h = font.getSize() * 1.5; pad = font.getSize() * .6
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    r = skia.Rect.MakeXYWH(-w / 2 - pad, -h / 2, w + 2 * pad, h)
    c.drawRoundRect(r.makeOffset(5, 7), h / 2, h / 2, _p((0, 0, 0), .35 * a))
    c.drawRoundRect(r.makeOutset(5, 5), h / 2 + 5, h / 2 + 5, _p((1, 1, 1), a))
    c.drawRoundRect(r, h / 2, h / 2, _p(bg, a))
    m = font.getMetrics(); base = -(m.fAscent + m.fDescent) / 2
    cx = -w / 2
    for ch in text:
        c.drawString(ch, cx, base, font, _p(fg, a)); cx += font.measureText(ch) + 4
    c.restore()

def qmark(c, x, y, size, font, sch, a, rot):
    c.save(); c.translate(x, y); c.rotate(rot)
    draw_glyph(c, '？', 0, 0, font, sch, a)
    c.restore()
