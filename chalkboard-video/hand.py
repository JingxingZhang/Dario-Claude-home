"""Illustrated right hand holding a chalk stick. make_hand() -> (RGBA PIL image, (ax, ay)) where
(ax, ay) is the chalk tip inside the image. Drawn at SS x supersampling, flat-illustration style."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SKIN = (236, 190, 156)
SKIN_D = (205, 150, 116)     # shade
LINE = (120, 74, 52)         # outline
NAIL = (246, 214, 196)
SLEEVE = (54, 74, 112)
SLEEVE_D = (38, 54, 86)
CUFF = (232, 232, 226)


def make_hand(chalk_color=(240, 240, 232), scale=1.0, SS=3, arm=1500):
    # local coordinates in 1x px, chalk tip at origin, hand toward +x +y
    ox, oy = 60, 160                      # canvas offset of the tip
    Wc, Hc = int(ox + arm + 120), int(oy + arm + 120)
    k = SS * scale
    img = Image.new("RGBA", (int(Wc * k), int(Hc * k)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(x, y):
        return ((x + ox) * k, (y + oy) * k)

    def capsule(a, b, w, fill, outline=LINE, ow=3.2):
        for col, ww in ((outline, w + 2 * ow), (fill, w)):
            if col is None: continue
            d.line([P(*a), P(*b)], fill=col, width=int(ww * k))
            for c in (a, b):
                r = ww / 2 * k
                cx, cy = P(*c)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    def poly(pts, fill, outline=LINE, ow=3.2):
        q = [P(*p) for p in pts]
        if outline is not None:
            d.line(q + [q[0]], fill=outline, width=int(2 * ow * k), joint="curve")
            for x, y in q:
                r = ow * k
                d.ellipse([x - r, y - r, x + r, y + r], fill=outline)
        d.polygon(q, fill=fill)

    def blob(cx, cy, rx, ry, fill, outline=LINE, ow=3.2):
        if outline is not None:
            x0, y0 = P(cx - rx - ow, cy - ry - ow); x1, y1 = P(cx + rx + ow, cy + ry + ow)
            d.ellipse([x0, y0, x1, y1], fill=outline)
        x0, y0 = P(cx - rx, cy - ry); x1, y1 = P(cx + rx, cy + ry)
        d.ellipse([x0, y0, x1, y1], fill=fill)

    a = np.array([0.80, -0.60]); a /= np.linalg.norm(a)   # chalk axis (tip -> back)
    n = np.array([0.60, 0.80])                            # toward the palm

    def A(s, t, shift=48):
        v = a * (s + shift) + n * t
        return (float(v[0]), float(v[1]))

    # --- forearm + sleeve (drawn first, under the hand)
    wrist = np.array(A(200, 205))
    fdir = np.array([0.62, 0.78]); fdir /= np.linalg.norm(fdir)
    fn = np.array([-fdir[1], fdir[0]])
    far = wrist + fdir * arm
    poly([tuple(wrist + fn * 62), tuple(far + fn * 95), tuple(far - fn * 95), tuple(wrist - fn * 58)], SKIN)
    cuff0 = wrist + fdir * 95
    poly([tuple(cuff0 + fn * 82), tuple(far + fn * 130), tuple(far - fn * 130), tuple(cuff0 - fn * 80)], SLEEVE, outline=SLEEVE_D)
    poly([tuple(cuff0 + fn * 84), tuple(cuff0 + fdir * 26 + fn * 86), tuple(cuff0 + fdir * 26 - fn * 82), tuple(cuff0 - fn * 82)], CUFF, outline=(170, 170, 160))

    # --- palm / back of the hand
    poly([A(95, 60), A(150, 20), A(230, 55), A(285, 150), A(265, 245), A(195, 285), A(120, 250), A(80, 160)], SKIN)
    # curled ring + little fingers (bottom side of the fist)
    blob(*A(108, 212), 34, 30, SKIN)
    blob(*A(150, 255), 30, 26, SKIN)
    capsule(A(92, 175), A(140, 210), 40, SKIN)
    # middle finger, curled under the chalk
    capsule(A(150, 110), A(62, 70), 44, SKIN)
    capsule(A(62, 70), A(42, 28), 40, SKIN)
    # chalk stick
    if chalk_color is not None:
        L, Wd = 150, 24
        c0, c1 = np.array(A(0, 0, 0)), np.array(A(L, 0, 0))
        perp = n * Wd / 2
        q = [tuple(c0 + a * 6 + perp * 0.75), tuple(c1 + perp), tuple(c1 - perp), tuple(c0 + a * 6 - perp * 0.75)]
        poly(q, chalk_color, outline=tuple(int(v * 0.72) for v in chalk_color), ow=2)
        poly([tuple(c0 + a * 7 + perp * 0.75), tuple(c0), tuple(c0 + a * 7 - perp * 0.75)], chalk_color, outline=tuple(int(v * 0.72) for v in chalk_color), ow=2)
    # index finger on top of the chalk
    capsule(A(175, 40), A(105, -12), 46, SKIN)
    capsule(A(105, -12), A(52, -24), 40, SKIN)
    blob(*A(60, -26), 13, 10, NAIL, outline=None)
    # thumb pressing from the near side
    capsule(A(120, 150), A(70, 105), 50, SKIN)
    capsule(A(70, 105), A(36, 22), 42, SKIN)
    blob(*A(38, 30), 11, 13, NAIL, outline=None)
    # knuckle creases
    for s, t in ((128, -6), (85, 82), (60, 120)):
        x, y = A(s, t)
        d.arc([*P(x - 12, y - 8), *P(x + 12, y + 8)], 200, 330, fill=SKIN_D, width=int(2.5 * k))

    img = img.resize((int(Wc * scale), int(Hc * scale)), Image.LANCZOS)
    return img, (ox * scale, oy * scale)


if __name__ == "__main__":
    im, (ax, ay) = make_hand(arm=500)
    bg = Image.new("RGBA", im.size, (34, 54, 46, 255))
    bg.alpha_composite(im)
    ImageDraw.Draw(bg).ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(255, 0, 0, 255))
    bg.convert("RGB").save("hand_test.png")
