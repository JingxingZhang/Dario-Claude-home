"""《呼吸决定》像素 MV：逐句分镜（原生 320×180）+ 综艺花字（1920×1080）。
人物：女主“我”（粉裙长发）、男主“你”（蓝帽衫）。frame(t) 返回 1920×1080 RGB。"""
import json, math, os
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw
from pixlib import *
from chars import *
import huazi as Z

DUR = 242.83
AU = json.load(open(os.path.join(ROOT, 'tools', 'audio.json')))
BEATS = np.array(AU['beats'])
RMS = AU['rms']


def rms(t):
    i = int(t * 30)
    return RMS[i] if 0 <= i < len(RMS) else 0.0


def beat_phase(t):
    i = np.searchsorted(BEATS, t) - 1
    return t - BEATS[i] if i >= 0 else 9.0


def pump(t, k=1.0):
    return math.exp(-beat_phase(t) * 7) * k


# ---------------- 歌词 ----------------
def load_lines():
    out = []
    for raw in open(os.path.join(ROOT, 'tools', 'lyrics.txt'), encoding='utf-8'):
        if raw.startswith('#') or not raw.strip():
            continue
        a, b, s = [x.strip() for x in raw.split('|')]
        out.append((float(a), float(b), s))
    return out


LINES = load_lines()
LS = [a for a, b, s in LINES]

CFG = {
    '嗨': dict(pal='yel', size=210, cx=560, cy=250, angle=-8, deco=('star', 'bang')),
    '怎么那么坏': dict(pal='pink', kw=['坏'], kwpal='purp', kwscale=1.5, angle=4, deco=('horn', 'bang')),
    '才两天就深爱': dict(pal='white', kw=['两天', '深爱'], kwpal=['yel', 'red'], angle=-3, deco=('heart', 'star')),
    '说得好像真爱': dict(pal='whiteb', kw=['真爱'], kwpal='pink', angle=3, deco=('q', 'star')),
    '我对你说 嗨': dict(pal='pink', kw=['嗨'], kwpal='yel', kwscale=1.6, angle=-4, deco=('heart', 'star')),
    '今天有没有恋爱': dict(pal='white', kw=['恋爱'], kwpal='pink', angle=-2, deco=('q', 'heart')),
    '是否谈了又甩': dict(pal='cyan', kw=['甩'], kwpal='red', kwscale=1.6, angle=5, deco=('bang', 'sweat')),
    '还说难遇真爱': dict(pal='purp', kw=['真爱'], kwpal='pink', angle=-3, deco=('sweat', 'q')),
    '我要你现在': dict(pal='yel', kw=['现在'], kwpal='red', kwscale=1.5, angle=-5, deco=('bang', 'star')),
    '把丑事都说出来': dict(pal='white', kw=['丑事'], kwpal='green', kwscale=1.4, angle=3, deco=('sweat', 'bang')),
    '才会听你表白': dict(pal='yel', kw=['表白'], kwpal='pink', kwscale=1.4, angle=-3, deco=('heart', 'star')),
    '听你说你是真的/喜欢我': dict(pal='white', kw=['喜欢我'], kwpal='pink', kwscale=1.45, size=105, angle=-2, deco=('heart', 'heart2', 'star')),
    '真的想谈恋爱了': dict(pal='purp', kw=['恋爱'], kwpal='pink', kwscale=1.4, angle=3, deco=('heart', 'star', 'heart2')),
    '那就让情绪决定': dict(pal='cyan', kw=['情绪'], kwpal='yel', kwscale=1.4, angle=-3, deco=('star', 'note')),
    '听呼吸频率': dict(pal='white', kw=['呼吸'], kwpal='cyan', kwscale=1.5, angle=0, deco=('wave', 'heart')),
    '跟感觉旅行': dict(pal='yel', kw=['旅行'], kwpal='green', kwscale=1.4, angle=-4, deco=('note', 'star')),
    '大不了不谈感情': dict(pal='white', kw=['不谈'], kwpal='red', kwscale=1.4, angle=3, deco=('x', 'sweat')),
    'Just do what I/suppose to do': dict(pal='cyan', size=96, angle=-3, deco=('note', 'star')),
    '你也不用再演戏': dict(pal='yel', kw=['演戏'], kwpal='purp', kwscale=1.4, angle=3, deco=('bang', 'star')),
    '怪我不爱你': dict(pal='white', kw=['不爱你'], kwpal='red', kwscale=1.35, angle=-4, deco=('crack', 'bang')),
    '是你的决定': dict(pal='cyan', kw=['你的'], kwpal='yel', kwscale=1.5, angle=4, deco=('bang', 'star')),
    '每句话在我心里': dict(pal='white', kw=['心里'], kwpal='pink', kwscale=1.4, angle=-2, deco=('heart', 'heart2')),
    '清清楚楚地/说你想离去': dict(pal='whiteb', kw=['离去'], kwpal='cyan', kwscale=1.4, size=105, angle=-2, deco=('drop', 'drop')),
}


def make_lines():
    out = []
    for i, (a, b, s) in enumerate(LINES):
        c = dict(CFG[s])
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else b + 2
        b = min(b, nxt - 0.05)
        kw = c.pop('kw', None)
        kwpal = c.pop('kwpal', 'pink')
        L = Z.Line(a, b, s, kw=kw if isinstance(kwpal, str) or not kw else kw, kwpal=kwpal if isinstance(kwpal, str) else kwpal[0], **c)
        if kw and not isinstance(kwpal, str):  # 多组重点词各自换色
            flat = s.replace('/', '')
            for w, p in zip(kw, kwpal):
                pos = flat.find(w)
                for it in L.items:
                    if pos <= it['i'] < pos + len(w):
                        it['pal'] = p
        out.append(L)
    return out


HZ = make_lines()


# ---------------- 背景 ----------------
@lru_cache(None)
def city_layers(v2=False):
    """返回 (天空, 远楼, 近楼) 三层，宽 640 便于横向卷动"""
    sky = Image.new('RGB', (W, H))
    top, bot = ((44, 10, 64), (170, 50, 120)) if v2 else ((16, 14, 44), (74, 44, 112))
    sky.paste(Image.fromarray(dither_grad(H, W, top, bot, levels=8)), (0, 0))
    d = ImageDraw.Draw(sky)
    for i in range(40):
        if hsh(i, 1) < 0.7:
            d.point((int(hsh(i, 2) * W), int(hsh(i, 3) * 70)), fill=(200, 200, 230))
    disc(d, 262, 30, 10, (250, 240, 210) if not v2 else (255, 210, 230))
    disc(d, 258, 27, 9, top)
    far = Image.new('RGBA', (640, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(far)
    x = 0
    i = 0
    while x < 640:
        w = 14 + int(hsh(i, 5) * 20)
        h = 40 + int(hsh(i, 6) * 60)
        col = (40, 30, 80) if not v2 else (70, 24, 90)
        R(d, x, 130 - h, w, h + 10, col)
        for wy in range(130 - h + 4, 128, 6):
            for wx in range(x + 2, x + w - 2, 4):
                if hsh(i, wx, wy) < 0.22:
                    R(d, wx, wy, 2, 3, (250, 220, 120) if hsh(wx, wy) < 0.7 else (120, 230, 250))
        x += w + 1
        i += 1
    near = Image.new('RGBA', (640, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(near)
    x = -10
    i = 0
    neon = [('LOVE', NEON_P), ('HI', NEON_B), ('BAR', NEON_Y), ('24H', NEON_B), ('CAFE', NEON_P)]
    while x < 640:
        w = 40 + int(hsh(i, 7) * 40)
        h = 70 + int(hsh(i, 8) * 50)
        col = (26, 20, 50) if not v2 else (44, 14, 60)
        R(d, x, 134 - h, w, h + 6, col)
        R(d, x, 134 - h, w, 2, (60, 50, 100))
        for wy in range(134 - h + 8, 128, 9):
            for wx in range(x + 4, x + w - 6, 8):
                if hsh(i, wx, wy, 3) < 0.35:
                    R(d, wx, wy, 4, 4, (255, 200, 110))
        if i % 2 == 0:
            s, c = neon[(i // 2) % len(neon)]
            tw = text_w(s)
            nx, ny = x + w // 2 - tw // 2, 134 - h + 14
            R(d, nx - 3, ny - 2, tw + 6, 15, (20, 14, 30))
            near.paste(Image.new('RGBA', (1, 1)), (0, 0))
            tmp = Image.new('RGB', (tw + 6, 15), (20, 14, 30))
            draw_text(tmp, 3, 1, s, c)
            near.paste(tmp, (nx - 3, ny - 2))
        x += w + 2
        i += 1
    return sky, far, near


def street(img, t, v2=False, scroll=0.0, ground=128, rain_k=0.8):
    sky, far, near = city_layers(v2)
    img.paste(sky, (0, 0))
    ofs1 = int(scroll * 0.3) % 320
    ofs2 = int(scroll * 0.7) % 320
    img.paste(far.crop((ofs1, 0, ofs1 + W, H)), (0, -2), far.crop((ofs1, 0, ofs1 + W, H)))
    nc = near.crop((ofs2, 0, ofs2 + W, H))
    img.paste(nc, (0, -6), nc)
    d = ImageDraw.Draw(img)
    # 霓虹闪
    if (int(t * 3) % 7) == 0:
        pass
    # 湿漉漉的街面 + 倒影
    R(d, 0, ground, W, H - ground, (24, 20, 40) if not v2 else (36, 14, 50))
    R(d, 0, ground, W, 2, (70, 60, 110))
    a = np.array(img)
    refl = a[ground - 40:ground][::-1]
    n = min(len(refl), H - ground - 2)
    bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:n, :W]
    seg_ = a[ground + 2:ground + 2 + n].astype(float)
    mix = (refl[:n].astype(float) * 0.45 + seg_ * 0.55)
    keep = bay < 0.6
    seg_[keep] = mix[keep]
    a[ground + 2:ground + 2 + n] = seg_.astype(np.uint8)
    img.paste(Image.fromarray(a), (0, 0))
    if rain_k > 0:
        rain(img, t, rain_k, ground)


def rain(img, t, k, ground=H):
    d = ImageDraw.Draw(img)
    n = int(160 * k)
    for i in range(n):
        sp = 260 + hsh(i, 2) * 120
        x = (hsh(i, 1) * (W + 60) - t * 60) % (W + 60) - 30
        y = (hsh(i, 3) * H + t * sp) % (H + 20) - 10
        d.line([(int(x), int(y)), (int(x - 2), int(y + 6))], fill=(160, 180, 230) if i % 3 else (200, 214, 250))
        if i % 5 == 0:
            ph = (t * 2 + hsh(i, 9)) % 1
            if ph < 0.25:
                sx = int(hsh(i, 8) * W)
                sy = ground + 3 + int(hsh(i, 7) * (H - ground - 6)) if ground < H else int(H - 4)
                r = int(1 + ph * 12)
                d.point((sx - r, sy), fill=(150, 170, 220)); d.point((sx + r, sy), fill=(150, 170, 220))


def room(img, t, v2=False, fog=0.0, rain_k=1.0):
    """室内窗边（向原视频的雨夜窗景致意）"""
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (44, 26, 34))
    for y in range(0, H, 4):
        R(d, 0, y, W, 1, (50, 30, 38))
    # 窗外城市
    win = Image.new('RGB', (W, H))
    street(win, t, v2, scroll=0, ground=150, rain_k=0)
    img.paste(win.crop((30, 16, 290, 128)), (30, 16))
    # 玻璃上的雨痕
    for i in range(70):
        x = 30 + int(hsh(i, 4) * 260)
        L = 3 + int(hsh(i, 5) * 8)
        y = 16 + (hsh(i, 6) * 112 + t * (8 + hsh(i, 7) * 30)) % 112
        d.line([(x, int(y)), (x, int(y) + L)], fill=(150, 170, 210))
        d.point((x, int(y) + L + 1), fill=(220, 230, 255))
    if fog > 0:
        a = np.array(img).astype(float)
        sub = a[16:128, 30:290]
        bay = np.tile(BAYER, (40, 80))[:112, :260]
        m = bay < fog * 0.6
        sub[m] = sub[m] * 0.5 + np.array([200, 205, 220]) * 0.5
        a[16:128, 30:290] = sub
        img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    # 窗框
    for x in (28, 158, 290):
        R(d, x, 14, 4, 116, (76, 46, 36))
    R(d, 28, 14, 266, 4, (76, 46, 36))
    R(d, 28, 70, 266, 3, (76, 46, 36))
    # 窗台
    R(d, 0, 128, W, 8, (96, 58, 40))
    R(d, 0, 128, W, 1, (140, 90, 60))
    R(d, 0, 136, W, H - 136, (36, 20, 28))
    # 蜡烛
    R(d, 64, 118, 5, 10, (250, 240, 220))
    fl = hsh(int(t * 12), 3)
    R(d, 65, 113 - int(fl * 2), 3, 5, (255, 200, 80))
    d.point((66, 112 - int(fl * 2)), fill=(255, 250, 200))
    R(d, 240, 120, 10, 8, (200, 90, 80)); R(d, 250, 122, 2, 4, (200, 90, 80))  # 杯子
    rain(img, t, 0.0)


def bg_burst(img, t, c1, c2):
    burst(img, t, c1, c2)


def two(img, t, gx, bx, ge='smile', be='smile', ga='down', ba='down', gy=124, by=124, gs=2, bs=2, **kw):
    person(img, gx, gy, 'girl', 1, ge, ga, t, gs, **{k[2:]: v for k, v in kw.items() if k.startswith('g_')})
    person(img, bx, by, 'boy', -1, be, ba, t, bs, **{k[2:]: v for k, v in kw.items() if k.startswith('b_')})


# ---------------- 镜头 ----------------
def s_title(img, t, lt, v2):
    room(img, t)
    person(img, 200, 132, 'girl', -1, 'closed', 'down', t, 2, breathe=math.sin(t * 2) * 1)
    R(ImageDraw.Draw(img), 0, 128, W, 8, (96, 58, 40))


def s_phone(img, t, lt, v2):
    room(img, t)
    buzz = 12.5 <= t < 15.5
    ex = 'surprised' if 12.5 <= t < 14 else ('happy' if t >= 14 else 'closed')
    person(img, 200 + (int(math.sin(t * 50)) if buzz else 0), 132, 'girl', -1, ex, 'phone' if t >= 13.2 else 'down', t, 2)
    d = ImageDraw.Draw(img)
    R(d, 0, 128, W, 8, (96, 58, 40)); R(d, 0, 128, W, 1, (140, 90, 60))
    if buzz and t < 13.2:
        R(d, 176, 122, 8, 5, K); R(d, 177, 123, 6, 3, CYAN)
        for k in (-1, 1):
            d.line([(180 + k * 7, 118), (180 + k * 9, 122)], fill=WHITE)
    if t >= 14.0:
        p = seg(t, 14.0, 14.3)
        heart(img, 170, int(82 - p * 10), 2 if int(t * 3) % 2 else 1)
    if t >= 16.5:
        sparkle(img, 150, 70, 3)


def s_walk(img, t, lt, v2):
    stop = 26.5
    scroll = min(t, stop) * 40
    street(img, t, v2, scroll=scroll, rain_k=0.9)
    walking = t < stop
    person(img, 120, 126, 'girl', 1, 'smile', 'umbrella', t, 2, walk=walking, umbrella=PINK)
    if t >= 25.0:
        bx = lerp(340, 220, ease(seg(t, 25.0, 27.5)))
        person(img, int(bx), 126, 'boy', -1, 'smile' if t > 27.5 else 'closed', 'down', t, 2, walk=t < 27.5)
        if t > 28.2:
            sparkle(img, int(bx) - 20, 50, 3)


def s_hi(img, t, lt, v2):
    street(img, t, v2, scroll=1060, rain_k=0.6)
    two(img, t, 110, 214, 'happy', 'surprised' if lt < 0.8 else 'blush', 'wave', 'down', g_umbrella=PINK)
    for i in range(3):
        if lt > 0.4 + i * 0.3:
            heart(img, 160 + i * 12, int(60 - (lt - i * 0.3) * 8) % 60 + 30, 1)


def s_bad(img, t, lt, v2):
    burst(img, t, (70, 20, 90) if not v2 else (100, 20, 80), (110, 40, 140) if not v2 else (160, 40, 120))
    wk = int(beat_phase(t) < 0.25)
    person(img, 200, 140, 'boy', -1, 'wink' if wk else 'smirk', 'fist', t, 3, horns=lt > 1.3)
    if lt > 1.3:
        for i in range(4):
            sparkle(img, 150 + int(hsh(i, 1) * 100), 30 + int(hsh(i, 2) * 50), 2 + (int(t * 4 + i) % 2), (255, 120, 200))
    person(img, 70, 140, 'girl', 1, 'pout', 'down', t, 2)
    if int(t * 3) % 2:
        vein(img, 82, 54)


def s_twodays(img, t, lt, v2):
    dots_bg(img, t, (255, 220, 236), (255, 196, 220))
    flip = seg(t, 40.4, 40.9)
    calendar(img, 18, 30, 'DAY 2' if flip >= 1 else 'DAY 1', flip=flip if flip < 1 else 0)
    k = 2 + ease(seg(t, 40.9, 43.0)) * 4
    kk = max(1, int(round(k + pump(t, 1.0))))
    heart(img, 168, 70, kk)
    person(img, 108, 140, 'girl', 1, 'surprised' if t < 41 else 'heart', 'down', t, 2)
    person(img, 236, 140, 'boy', -1, 'smile', 'heart', t, 2)


def s_truelove(img, t, lt, v2):
    street(img, t, v2, scroll=1060, rain_k=0.4)
    spotlight(img, 210, 0, 130, 50)
    person(img, 210, 128, 'boy', -1, 'smile', 'hold', t, 2, kneel=True)
    rose(img, 180, 86)
    for i in range(5):
        if int(t * 6 + i) % 3:
            sparkle(img, 170 + int(hsh(i, 4) * 70), 40 + int(hsh(i, 5) * 40), 2)
    person(img, 96, 128, 'girl', 1, 'side', 'down', t, 2)
    qmark(img, 104, 34)


def s_hi2(img, t, lt, v2):
    street(img, t, v2, scroll=1060, rain_k=0.4)
    p = seg(t, 47.2, 48.6)
    two(img, t, 100, 222, 'wink', 'blush' if p >= 1 else 'surprised', 'wave', 'cover' if p >= 1 else 'down')
    if 0 < p < 1:
        heart(img, int(lerp(120, 210, p)), int(70 - math.sin(p * math.pi) * 40), 2)
    if p >= 1:
        for i in range(6):
            a = i / 6 * 6.283 + t
            r = 16 + (t - 48.6) * 20
            if r < 70:
                heart(img, int(222 + math.cos(a) * r), int(60 + math.sin(a) * r), 1)


def s_chat(img, t, lt, v2):
    dots_bg(img, t, (230, 236, 255), (210, 220, 250))
    phone_big(img, 122, 12, 76, 134)
    d = ImageDraw.Draw(img)
    chat_bubble(img, 150, 40, 42, 18, (255, 150, 190), right=True)
    heart(img, 162, 49, 1)
    qmark(img, 172, 42, K)
    if t < 55.0:
        chat_bubble(img, 130, 66, 28, 14, (210, 214, 230))
        for i in range(3):
            on = int(t * 4) % 3 == i
            R(d, 136 + i * 7, 72 - (1 if on else 0), 3, 3, (90, 90, 110) if on else (150, 150, 170))
    else:
        chat_bubble(img, 130, 66, 40, 16, (210, 214, 230))
        heart(img, 140, 74, 1, broken=True)
        heart(img, 154, 74, 1)
        qmark(img, 162, 68, (120, 120, 140))
    person(img, 60, 150, 'girl', 1, 'smile', 'phone', t, 2)
    person(img, 262, 150, 'boy', -1, 'sweat' if False else 'surprised', 'phone', t, 2)
    sweat(img, 274, 70, 2)


def s_dump(img, t, lt, v2):
    street(img, t, v2, scroll=1300, rain_k=0.4)
    trash(img, 268, 104)
    throw = 60.4
    for i in range(3):
        a = t * 5 + i * 2.1
        if i == 0 and t >= throw:
            p = seg(t, throw, throw + 0.8)
            if p < 1:
                heart(img, int(lerp(170, 278, p)), int(40 - math.sin(p * math.pi) * 30 + p * 50), 2)
            continue
        heart(img, int(170 + math.cos(a) * 16), int(44 + math.sin(a) * 10), 2)
    if t >= throw + 0.8:
        heart(img, 278, 98, 2, broken=True)
        bang(img, 290, 78)
    person(img, 170, 128, 'boy', -1, 'smirk', 'heart', t, 2)
    person(img, 70, 128, 'girl', 1, 'surprised', 'down', t, 2)
    sweat(img, 88, 56, 2)


def s_search(img, t, lt, v2):
    street(img, t, v2, scroll=1500, rain_k=0.4)
    look = math.sin(lt * 2.4)
    person(img, 200, 128, 'boy', -1 if look < 0 else 1, 'surprised', 'point', t, 2)
    magnifier(img, int(200 + look * 46), 70)
    person(img, 120, 128, 'girl', 1, 'pout', 'hold', t, 2)
    heart(img, 146, 84, 2)
    if int(t * 2) % 2:
        sweat(img, 214, 50, 2)


def s_now(img, t, lt, v2):
    burst(img, t, (255, 230, 120), (255, 200, 80))
    concentration(img, 220, 90, t, (255, 255, 255))
    clock(img, 160, 46, 22, t)
    draw_text(img, 160 - text_w('NOW') // 2, 76, 'NOW', (230, 40, 60), outline=WHITE)
    person(img, 80, 150, 'girl', 1, 'angry', 'point', t, 2)
    person(img, 244, 150, 'boy', -1, 'surprised', 'down', t, 2)
    sweat(img, 262, 74, 2)


def s_confess(img, t, lt, v2):
    street(img, t, v2, scroll=1700, rain_k=0.3)
    d = ImageDraw.Draw(img)
    k = ease(seg(lt, 0.2, 2.6))
    hgt = int(10 + 70 * k)
    R(d, 168, 52, 50, hgt, (250, 236, 200)); R(d, 166, 50, 54, 5, (200, 160, 100)); R(d, 166, 50 + hgt, 54, 5, (200, 160, 100))
    icons = [lambda x, y: heart(img, x, y, 1, broken=True), lambda x, y: (R(d, x - 5, y - 4, 10, 8, (180, 200, 230)), d.line([(x - 5, y - 4), (x + 5, y + 4)], fill=HEART), d.line([(x + 5, y - 4), (x - 5, y + 4)], fill=HEART)),
             lambda x, y: (R(d, x - 3, y - 5, 6, 10, K), R(d, x - 2, y - 4, 4, 7, CYAN)), lambda x, y: sweat(img, x - 2, y - 3, 1)]
    for i in range(int(k * 8)):
        x, y = 180 + (i % 2) * 26, 64 + (i // 2) * 15
        icons[i % 4](x, y)
        R(d, x + 8, y - 1, 10, 2, (160, 140, 120))
    person(img, 230, 128, 'boy', -1, 'sad', 'hold', t, 2)
    sweat(img, 248, 50, 2); sweat(img, 220, 44, 1)
    person(img, 80, 128, 'girl', 1, 'side', 'down', t, 2)


def s_letter(img, t, lt, v2):
    street(img, t, v2, scroll=1900, rain_k=0.3)
    op = seg(lt, 1.6, 2.4)
    person(img, 100, 128, 'girl', 1, 'smile' if op > 0.5 else 'side', 'ear', t, 2)
    person(img, 214, 128, 'boy', -1, 'blush', 'hold', t, 2)
    envelope(img, 156, 80, op)
    if op >= 1:
        for i in range(3):
            heart(img, 150 + i * 14, int(60 - ((t * 20 + i * 7) % 30)), 1)


def s_likeme(img, t, lt, v2):
    dots_bg(img, t, (255, 226, 240), (255, 200, 225))
    sign_board(img, 170, 26, 70, 46, t)
    person(img, 206, 150, 'boy', -1, 'smile', 'heart', t, 2)
    person(img, 90, 150, 'girl', 1, 'shy', 'cover', t, 2)
    for i in range(7):
        y = (hsh(i, 2) * 160 - t * 22) % 150
        heart(img, int(20 + hsh(i, 1) * 280), int(y), 1)


def s_dream(img, t, lt, v2):
    burst(img, t, (255, 170, 210), (255, 206, 230))
    for i in range(18):
        x = (hsh(i, 1) * W + t * 14) % W
        y = (hsh(i, 2) * H + t * 24) % H
        d = ImageDraw.Draw(img)
        R(d, int(x), int(y), 3, 2, (255, 240, 246)); d.point((int(x) + 1, int(y) + 2), fill=(255, 180, 210))
    person(img, 160, 160, 'girl', 1, 'heart', 'heart', t, 3, breathe=math.sin(t * 3))
    heart(img, 160, 20, 2 + int(pump(t) > 0.4))
    for i in range(4):
        if int(t * 3 + i) % 2:
            sparkle(img, int(80 + hsh(i, 3) * 160), int(40 + hsh(i, 4) * 70), 3)


def s_dial(img, t, lt, v2):
    dots_bg(img, t, (40, 50, 110) if not v2 else (90, 30, 100), (60, 72, 140) if not v2 else (120, 50, 130))
    settle = seg(lt, 0, 2.6)
    ang = clamp(0.5 + math.sin(lt * 7) * 0.5 * (1 - settle) + settle * 0.42 * ease(settle))
    if settle >= 1:
        ang = 0.92 + 0.03 * math.sin(t * 6)
    dial(img, 160, 96, 56, ang)
    person(img, 56, 150, 'girl', 1, 'heart' if settle >= 1 else 'surprised', 'down', t, 2)
    person(img, 264, 150, 'boy', -1, 'blush' if settle >= 1 else 'surprised', 'down', t, 2)


def s_breath(img, t, lt, v2):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (16, 14, 40) if not v2 else (40, 12, 50))
    amp = 3 + rms(t) * 10
    wave_line(img, 34, t, amp, CYAN, beat=1.0)
    br = math.sin(t * 2.4) * 1.5
    person(img, 128, 140, 'girl', 1, 'closed', 'down', t, 2, breathe=br)
    person(img, 192, 140, 'boy', -1, 'closed', 'down', t, 2, breathe=br)
    heart(img, 160, 64, 2 + int(pump(t) > 0.35))
    for k in (0, 1):
        ph = (t * 0.8 + k * 0.5) % 1
        if ph < 0.6:
            x = 146 + k * 26
            disc(d, x + (6 if k == 0 else -6) * ph * 2, 66 - int(ph * 10), int(1 + ph * 3), (200, 210, 240))


def s_ride(img, t, lt, v2):
    street(img, t, v2, scroll=t * 160, rain_k=0.3)
    sub = Image.new('RGBA', (110, 70), (0, 0, 0, 0))
    person(sub, 44, 54, 'girl', 1, 'happy', 'wave', t, 1)
    person(sub, 60, 54, 'boy', 1, 'happy', 'point', t, 1)
    scooter(sub, 20, 60, t)
    sub = scaled(sub, 2)
    paste(img, sub, 60, 128 - 128 + int(math.sin(t * 9))) if False else paste(img, sub, 50, -6 + int(math.sin(t * 9)))
    d = ImageDraw.Draw(img)
    for i in range(10):
        y = int(30 + hsh(i, 1) * 100)
        x = int((hsh(i, 2) * W - t * 500) % (W + 40)) - 20
        d.line([(x, y), (x + 20 + int(hsh(i, 3) * 20), y)], fill=WHITE)
    for i in range(4):
        x = 40 - i * 14 - int((t * 30) % 14)
        heart(img, x + 30, 60 + int(math.sin(t * 5 + i) * 6), 1)


def s_nofeel(img, t, lt, v2):
    street(img, t, v2, scroll=2300, rain_k=0.4)
    person(img, 90, 128, 'girl', 1, 'smile', 'shrug', t, 2)
    person(img, 236, 128, 'boy', -1, 'surprised', 'down', t, 2)
    heart(img, 162, 70, 4)
    p = seg(t, 98.6, 98.8)
    if p > 0:
        d = ImageDraw.Draw(img)
        s = int(26 + (1 - p) * 20)
        for k in (-1, 1):
            d.line([(162 - s, 70 - s * k), (162 + s, 70 + s * k)], fill=(230, 30, 50), width=6)
            d.line([(162 - s, 70 - s * k), (162 + s, 70 + s * k)], fill=(255, 90, 100), width=2)
        sweat(img, 252, 52, 2)


def s_cool(img, t, lt, v2):
    street(img, t, v2, scroll=t * 50, rain_k=0.3)
    b = int(pump(t, 2))
    person(img, 170, 128 - b, 'girl', 1, 'smile', 'down', t, 2, walk=True, glasses=True)
    person(img, 70, 128, 'boy', 1, 'surprised', 'down', t, 2, walk=True)
    qmark(img, 66, 30)
    d = ImageDraw.Draw(img)
    for i in range(3):
        if int(t * 4 + i) % 2:
            sparkle(img, 200 + i * 18, 40 + i * 8, 2, NEON_Y)


def s_stage(img, t, lt, v2):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (24, 14, 30))
    R(d, 0, 128, W, 22, (110, 70, 50)); R(d, 0, 128, W, 2, (160, 110, 70))
    spotlight(img, 160, 14, 128, 46)
    drop = seg(t, 108.0, 108.6)
    person(img, 160, 128, 'boy', -1, 'surprised' if drop > 0 else 'smile', 'down', t, 2, mask=drop <= 0)
    if drop > 0:
        mx, my = 140 - int(drop * 20), int(48 + drop * 76)
        R(d, mx, my, 13, 8, (250, 250, 250)); R(d, mx + 3, my + 3, 2, 2, K); R(d, mx + 8, my + 3, 2, 2, K)
        sweat(img, 178, 50, 2)
    curtains(img, ease(seg(t, 109.0, 110.2)), t)
    person(img, 40, 172, 'girl', 1, 'side', 'down', t, 2)


def s_blame(img, t, lt, v2):
    burst(img, t, (40, 30, 70) if not v2 else (70, 20, 70), (60, 44, 96) if not v2 else (100, 30, 90))
    concentration(img, 160, 70, t, (90, 80, 140))
    person(img, 80, 148, 'boy', 1, 'angry', 'point', t, 2)
    person(img, 240, 148, 'girl', -1, 'side', 'down', t, 2)
    crack = t >= 111.4
    heart(img, 160, 62, 4, broken=crack)
    if crack:
        bang(img, 176, 32)


def s_decide(img, t, lt, v2):
    street(img, t, v2, scroll=2600, rain_k=0.5)
    press = t >= 114.8
    big_button(img, 160, 100, press)
    person(img, 196, 128, 'boy', -1, 'sad' if press else 'pout', 'point' if not press else 'down', t, 2)
    person(img, 76, 128, 'girl', 1, 'angry', 'point', t, 2)
    if press:
        concentration(img, 160, 92, t, (255, 255, 255), n=24, r0=36)


def s_words(img, t, lt, v2):
    dots_bg(img, t, (250, 230, 240), (240, 210, 226))
    person(img, 130, 168, 'girl', 1, 'closed', 'chest', t, 3)
    n = int(seg(lt, 0, 4.0) * 6)
    glow = 1 + n // 2
    heart(img, 131, 104, min(4, glow))
    for i in range(6):
        p = (lt * 0.9 - i * 0.55)
        if 0 < p < 1:
            x = lerp(310, 136, ease(p)); y = lerp(30 + i * 14, 102, ease(p))
            chat_bubble(img, int(x), int(y), 20, 11, WHITE)
            d = ImageDraw.Draw(img)
            for k in range(3):
                R(d, int(x) + 4 + k * 5, int(y) + 5, 2, 2, (150, 150, 170))


def s_leave(img, t, lt, v2):
    final = v2
    street(img, t, v2, scroll=2900, rain_k=1.0)
    bx = lerp(190, 360, ease(seg(lt, 0.4, 5.0)))
    person(img, int(bx), 128, 'boy', 1, 'closed', 'down', t, 2, walk=bx < 359)
    if not final:
        person(img, 90, 128, 'girl', 1, 'sad', 'umbrella', t, 2, umbrella=PINK)
    else:
        turn = lt >= 3.3
        if not turn:
            person(img, 90, 128, 'girl', 1, 'sad', 'umbrella', t, 2, umbrella=PINK)
        else:
            gx = lerp(90, -40, ease(seg(lt, 4.0, 6.7)))
            person(img, int(gx), 128, 'girl', -1, 'smile', 'down', t, 2, walk=True)
            if lt < 4.4:
                sparkle(img, 100, 40, 3)


def s_interlude(img, t, lt, v2):
    fog = clamp(seg(t, 138.0, 140.0)) * (1 - seg(t, 147.0, 148.6))
    room(img, t, fog=fog)
    d = ImageDraw.Draw(img)
    # 回忆：小相片飘过窗前
    if 129 < t < 139:
        icons = ['heart', 'cal', 'rose', 'scooter', 'heart']
        for i, ic in enumerate(icons):
            p = (t - 129 - i * 1.6) / 6
            if 0 < p < 1:
                x = int(lerp(300, 20, p)); y = int(40 + math.sin(p * 6 + i) * 14 + i * 6)
                R(d, x, y, 26, 30, (250, 250, 245)); R(d, x + 2, y + 2, 22, 20, (90, 80, 130))
                if ic == 'heart':
                    heart(img, x + 13, y + 12, 1)
                elif ic == 'cal':
                    R(d, x + 6, y + 6, 14, 12, WHITE); R(d, x + 6, y + 6, 14, 3, HEART)
                elif ic == 'rose':
                    rose(img, x + 11, y + 6)
                else:
                    R(d, x + 5, y + 14, 16, 3, NEON_Y); R(d, x + 6, y + 18, 3, 3, K); R(d, x + 17, y + 18, 3, 3, K)
    # 呵气、在雾上画心
    ex = 'sad' if t < 140 else ('closed' if t < 146 else 'smile')
    arm = 'point' if 141 < t < 145.5 else 'down'
    person(img, 200, 132, 'girl', -1, ex, arm, t, 2, breathe=math.sin(t * 2) * 1)
    R(d, 0, 128, W, 8, (96, 58, 40)); R(d, 0, 128, W, 1, (140, 90, 60))
    if 138 < t < 141:
        ph = (t * 0.9) % 1
        disc(d, 160 - int(ph * 10), 76, int(2 + ph * 6), (220, 226, 240))
    hp = seg(t, 141.2, 145.2)
    if hp > 0 and fog > 0.2:
        pts = []
        for i in range(60):
            a = i / 59 * 2 * math.pi
            pts.append((150 + 16 * math.sin(a) ** 3 * 1.3, 52 - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * 1.3))
        n = int(hp * 60)
        for a_, b_ in zip(pts[:n], pts[1:n + 1]):
            d.line([a_, b_], fill=(255, 150, 190), width=3)
    R(d, 176, 124, 8, 4, K)  # 手机（暗）


def s_outro(img, t, lt, v2):
    rk = 1 - seg(t, 213, 222)
    street(img, t, False, scroll=t * 30 if t < 226 else 226 * 30, rain_k=rk)
    if rk < 0.5:
        d = ImageDraw.Draw(img)
        for i in range(30):
            if hsh(i, 9) < (0.5 - rk) * 2 and int(t * 2 + i) % 5:
                d.point((int(hsh(i, 10) * W), int(hsh(i, 11) * 60)), fill=(255, 255, 230))
    um = PINK if t < 221 else None
    arm = 'umbrella' if um else ('wave' if 224 < t < 229 else 'down')
    ex = 'closed' if t < 221 else 'happy'
    person(img, 150, 128, 'girl', 1 if t < 226 else -1, ex, arm, t, 2, walk=t < 226, umbrella=um, breathe=math.sin(t * 1.6) * 1.5)
    if t > 224:
        ph = (t * 0.6) % 1
        disc(ImageDraw.Draw(img), 168 + int(ph * 8), 48 - int(ph * 8), int(1 + ph * 4), (220, 226, 245))


def s_end(img, t, lt, v2):
    room(img, t)
    a = np.asarray(img).astype(float) * 0.45
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))


def L(i, pre=0.12):
    return LS[i] - pre


SHOTS = [
    (0.0, s_title, False), (9.5, s_phone, False), (19.0, s_walk, False),
    (L(0), s_hi, False), (L(1), s_bad, False), (L(2), s_twodays, False), (L(3), s_truelove, False), (L(4), s_hi2, False),
    (L(5), s_chat, False), (L(6), s_dump, False), (L(7), s_search, False), (L(8), s_now, False), (L(9), s_confess, False),
    (L(10), s_letter, False), (L(11), s_likeme, False), (L(12), s_dream, False),
    (L(13), s_dial, False), (L(14), s_breath, False), (L(15), s_ride, False), (L(16), s_nofeel, False), (L(17), s_cool, False),
    (L(18), s_stage, False), (L(19), s_blame, False), (L(20), s_decide, False), (L(21), s_words, False), (L(22), s_leave, False),
    (126.6, s_interlude, False),
    (L(23), s_now, 'replay'), (L(24), s_confess, 'replay'), (L(25), s_letter, 'replay'), (L(26), s_likeme, 'replay'), (L(27), s_dream, 'replay'),
    (L(28), s_dial, True), (L(29), s_breath, True), (L(30), s_ride, True), (L(31), s_nofeel, True), (L(32), s_cool, True),
    (L(33), s_stage, True), (L(34), s_blame, True), (L(35), s_decide, True), (L(36), s_words, True), (L(37), s_leave, True),
    (211.0, s_outro, False), (232.5, s_end, False),
]

# 场景里写死的时刻（动作卡点）按第一遍的句子时间写；第二遍用同一镜头时整体平移
SHIFT = {}
for k, (t0, fn, v) in enumerate(SHOTS):
    if v in ('replay', True):
        first = next(t for (t, f, vv) in SHOTS if f is fn and vv is False)
        SHIFT[k] = t0 - first


def shot_at(t):
    cur = 0
    for i, s in enumerate(SHOTS):
        if t >= s[0]:
            cur = i
    return cur


def compose(t, i):
    t0, fn, v = SHOTS[i]
    img = Image.new('RGB', (W, H), INK)
    sh = SHIFT.get(i, 0.0)
    fn(img, t - sh, t - t0, v is True)
    if v == 'replay':
        a = np.asarray(img).astype(float)
        g = a.mean(2, keepdims=True)
        a = a * 0.45 + g * 0.55
        a[:, :, 2] = a[:, :, 2] * 1.1 + 10
        a[::3] *= 0.82
        img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    return img


def frame(t):
    i = shot_at(t)
    img = compose(t, i)
    t0 = SHOTS[i][0]
    if i > 0 and t - t0 < 0.16:  # 像素抖动溶解
        prev = compose(t, i - 1)
        k = (t - t0) / 0.16
        m = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < k
        img = Image.fromarray(np.where(m[:, :, None], np.asarray(img), np.asarray(prev)).astype(np.uint8))
    big = img.resize((Z.FW, Z.FH), Image.NEAREST)
    overlay_hi(big, t, i)
    return big


def overlay_hi(big, t, i):
    bp = beat_phase(t)
    # 片头：歌名 + 原唱
    if t < 9.6:
        out = seg(t, 9.0, 9.6)
        TITLE.draw(big, t if t < 9.0 else 9.0 + out * 0.2, bp)
        if out < 1:
            Z.pill(big, 960, 640, '原唱 · Fine乐团', 64, alpha=1 - out)
            Z.pill(big, 960, 760, '像素 MV', 44, bg=(255, 110, 170), edge=(255, 255, 255), fg=(255, 255, 255), alpha=1 - out)
    if t >= 232.5:
        k = seg(t, 232.5, 233.2)
        END.draw(big, t, bp)
        if k > 0:
            Z.pill(big, 960, 620, '原唱 · Fine乐团', 64, alpha=k)
            Z.pill(big, 960, 740, '像素 MV · 谢谢收看', 44, bg=(255, 110, 170), edge=(255, 255, 255), alpha=k)
    if SHOTS[i][2] == 'replay':
        Z.pill(big, 230, 80, '回放 REPLAY', 46, bg=(200, 30, 50), edge=(255, 255, 255))
    for L_ in HZ:
        if L_.t0 - 0.1 <= t <= L_.t1 + 0.1:
            L_.draw(big, t, bp)
    s = Z.signature()
    big.paste(s, (960 - s.width // 2, Z.FH - s.height - 6), s)
    if t > DUR - 1.2:
        a = np.asarray(big).astype(float) * (1 - seg(t, DUR - 1.2, DUR - 0.1))
        big.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))


TITLE = Z.Line(-2.0, 9.2, '呼吸决定', pal='pink', size=230, cx=960, cy=400, angle=-3, deco=('heart', 'star', 'note'), stagger=0.0)
END = Z.Line(232.6, DUR + 1, '呼吸决定', pal='pink', size=200, cx=960, cy=400, angle=-3, deco=('heart', 'star'), stagger=0.08)
