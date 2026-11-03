"""《等风来》（大明开局·第12集）像素 MV：逐句分镜 + 叠层（主题栏、署名、风力表、对话框歌词、副歌大字）。
frame(t) 返回 320×180 的 PIL 图。"""
import math
from PIL import Image, ImageDraw
import numpy as np
from pixlib import *
from sprites import *

LY = load_lyrics()
DUR = 234.68
SIGN, SEAL = '@张景行', '景行'


def line_at(t):
    for L in LY:
        if L['show0'] <= t < L['show1']:
            return L
    return None


def ct(i, k):
    """第 i 句第 k 个字的开唱时间（k 按显示版字符位置，含空格）"""
    c = LY[i]['ct'][k]
    return c[0] if c else None


# ---------------- 时间轴：一天里的太阳 & 风 ----------------
TOD = [(0, 0.02), (44, 0.12), (61, 0.3), (69, 0.3), (76.5, 0.68), (93.5, 0.78),
       (110.3, 0.78), (110.4, 0.05), (119.4, 0.12), (121.7, 0.45), (128.1, 0.5),
       (137.8, 0.75), (155.5, 0.83), (172.6, 0.86), (190.4, 0.88)]


def tod_at(t):
    for (a, x), (b, y) in zip(TOD, TOD[1:]):
        if a <= t <= b:
            return lerp(x, y, seg(t, a, b))
    return TOD[-1][1]


def wind_at(t):
    if t < 158.9:
        return 0.0
    if t < 160.6:
        return ease(seg(t, 158.9, 160.6))
    if t < 190.4:
        return 1.0
    if t >= 208:
        return 0.6
    return 0.8


def bob(t, k=1.0, ph=0.0):
    return int(round(math.sin(t * 1.6 + ph) * k))


def bg(img, t, tod=None, hz=104, red=0.0, choppy=0.3, stars=0.0, sun=True):
    tod = tod_at(t) if tod is None else tod
    draw_sky(img, tod, hz, sun=sun, stars=stars, t=t)
    draw_water(img, t, tod, hz, red=red, choppy=choppy)
    return tod


def far_fleet(img, t, hz, x0=150, n=6, col=(70, 40, 50), dx=0.0):
    """地平线上一排楼船剪影"""
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = int(x0 + i * 26 + dx)
        R(d, x, hz - 6, 22, 6, col)
        R(d, x + 3, hz - 10, 15, 4, col)
        R(d, x + 6, hz - 13, 9, 3, col)
        R(d, x + 10, hz - 20, 1, 7, col)


def zhu_boat(img, t, x, y, scale=1, wind=None, white=True, face=1, pose=0, flagcol=RED):
    """朱元璋的座船（小船 + 主将 + 旗）。x,y 为船左上角"""
    wind = wind_at(t) if wind is None else wind
    b = small_boat(34, True, white)
    if scale != 1:
        b = scaled(b, scale)
    paste(img, b, x, y)
    flag(img, x + 17 * scale, y + 2 * scale, 12 * scale, 7 * scale, wind, t, flagcol, scale)
    person(img, x + 9 * scale, y + 26 * scale, 'zhu', pose, t, face, scale)


def speed_lines(img, t, y0, y1, n=14, col=WHITE, dirx=-1):
    d = ImageDraw.Draw(img)
    for i in range(n):
        y = int(y0 + hsh(i, 1) * (y1 - y0))
        ln = 10 + int(hsh(i, 2) * 30)
        x = (hsh(i, 3) * W - t * 400 * (-dirx)) % (W + 60) - 30
        d.line([(int(x), y), (int(x) + ln, y)], fill=col)


def wind_streaks(img, t, k):
    """东北风：从右上往左下的风线"""
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    for i in range(int(22 * k)):
        ph = (t * 0.9 + hsh(i, 11)) % 1
        x = W + 20 - ph * (W + 80) + hsh(i, 12) * 60
        y = 20 + hsh(i, 13) * 100 + ph * 40
        ln = 8 + int(hsh(i, 14) * 14)
        c = lerpc(WHITE, (200, 210, 230), hsh(i, 15))
        d.line([(int(x), int(y)), (int(x + ln), int(y - ln * 0.35))], fill=c)


# ---------------- 各镜头 ----------------
def s_title(img, t, lt):
    hz = 108
    bg(img, t, 0.02 + lt * 0.002, hz)
    far_fleet(img, t, hz, 176, 5, dx=-lt * 0.6)
    zhu_boat(img, t, 36, hz + 8 + bob(t), 1)
    for i, x in enumerate((96, 122)):
        b = small_boat(30, True)
        paste(img, b, x, hz + 14 + bob(t, 1, i + 1))
        flag(img, x + 16, hz + 16 + bob(t, 1, i + 1), 10, 6, 0, t, RED)
    draw_text(img, (W - text_w('大明开局 · 第12集')) // 2, 30, '大明开局 · 第12集', PAPER, outline=INK)
    tw = text_w('等风来', 4, gap=1)
    draw_text(img, (W - tw) // 2, 46, '等风来', GOLD, scale=4, shadow=RED_D, gap=1, outline=INK)


def s_fleet(img, t, lt):
    hz = 100
    bg(img, t, None, hz)
    pan = lt * 3.2
    for i in range(4):
        x = 150 + i * 70 - pan
        ship = tower_ship(96)
        paste(img, ship, x, hz - 50 + bob(t, 1, i))
        tower_flags(img, x, hz - 50 + bob(t, 1, i), 96, t, 0)
    for i in range(3):
        x = 10 + i * 40 - pan * 0.4
        zhu_boat(img, t, int(x), 116 + bob(t, 1, i), 1, white=(i == 1))


def s_wait(img, t, lt):
    hz = 112
    bg(img, t, None, hz)
    far_fleet(img, t, hz, 196, 5, dx=-lt * 0.8)
    zhu_boat(img, t, 60, 82 + bob(t, 1), 2, face=1)


def s_sunrise(img, t, lt):
    hz = 104
    bg(img, t, None, hz)
    d = ImageDraw.Draw(img)
    # 楼船连成一片，像山
    for i in range(6):
        x = 120 + i * 34 - lt * 0.5
        ship = tower_ship(80)
        paste(img, ship, x, hz - 62 + bob(t, 1, i))
    zhu_boat(img, t, 30, 108 + bob(t), 1)


def s_v1a(img, t, lt):
    hz = 132
    bg(img, t, None, hz)
    ship = scaled(tower_ship(120), 2)
    x = 120 - lt * 4
    paste(img, ship, x, hz - 140 + bob(t, 1))
    tower_flags(img, x, hz - 140 + bob(t, 1), 120, t, 0, 2)
    zhu_boat(img, t, 20, hz - 46 + bob(t, 1, 2), 2, face=1)
    if lt > 1.8:
        bubble(img, 48, 96, '……')


def s_v1b(img, t, lt):
    hz = 118
    bg(img, t, None, hz)
    w = 200
    ship = tower_ship(w)
    x, y = 60, hz - 62 + bob(t, 1)
    paste(img, ship, x, y)
    tower_flags(img, x, y, w, t, 0)
    base = 78 - 16
    tiers = [(6, base - 15, w - 12, 14), (14, base - 29, w - 28, 14), (24, base - 41, w - 48, 12)]
    d = ImageDraw.Draw(img)
    marks = [ct(1, 9), ct(1, 10), ct(1, 11)]  # 分 三 层
    if t < 52.5:
        for k in range(3):
            if marks[k] and t >= marks[k] - 0.05:
                x0, y0, ww, th = tiers[k]
                if int(t * 6) % 2 == 0 or t > marks[k] + 0.5:
                    d.rectangle([x + x0 - 1, y + y0 - 1, x + x0 + ww, y + y0 + th], outline=GOLD)
                draw_text(img, x + x0 - 16, y + y0 + 1, '一二三'[k], GOLD, outline=INK)
        if t >= ct(1, 3):  # 刷红漆
            for i in range(8):
                px = x + 10 + ((i * 23 + int(t * 30)) % (w - 20))
                d.point((px, y + base + 3), fill=WHITE)
    else:
        # 楼上人说话，楼下听不见
        person(img, x + 70, y + base - 41, 'enemy', 0, t, 1)
        person(img, x + 120, y + base + 1 - 1, 'enemy', 0, t, -1)
        if t >= 53.0:
            bubble(img, x + 72, y + base - 58, '喂——')
        if t >= 54.5:
            bubble(img, x + 120, y + base - 18, '？')


def s_v1c(img, t, lt):
    hz = 112
    bg(img, t, None, hz)
    d = ImageDraw.Draw(img)
    ships = []
    for i in range(5):
        x = 6 + i * 62 - lt * 2
        y = hz - 62 + bob(t, 1, i) - (6 if i % 2 else 0)
        paste(img, tower_ship(90), x, y)
        tower_flags(img, x, y, 90, t, 0)
        ships.append((x, y))
    # 铁索连舟
    for i in range(4):
        x1, y1 = ships[i][0] + 86, ships[i][1] + 66
        x2 = ships[i + 1][0] + 4
        for xx in range(int(x1), int(x2), 3):
            d.point((xx, int(y1 + 2 + math.sin((xx - x1) / 6) * 2)), fill=GRAY)
    # 望过去像山冈：描一道山脊
    k = seg(t, ct(3, 8), ct(3, 13) + 0.3)  # 望 … 冈
    if k > 0:
        pts = []
        for i, (x, y) in enumerate(ships):
            pts += [(x + 4, y + 40), (x + 45, y + 14 - 10 * (i % 2 == 0)), (x + 86, y + 40)]
        n = int(len(pts) * k)
        for (a, b) in zip(pts[:n], pts[1:n + 1]):
            d.line([a, b], fill=GOLD, width=1)
        if t >= ct(3, 13):
            draw_text(img, 120, 34, '像山冈', GOLD, outline=INK)


def s_v1d(img, t, lt):
    hz = 106
    bg(img, t, 0.5, hz)
    zhu_boat(img, t, 40, 74 + bob(t), 2, white=True)
    ex = lerp(330, 130, ease(seg(t, 61.6, 63.9)))
    b = scaled(small_boat(40, True), 2)
    paste(img, b, ex, 70 + bob(t, 1, 1))
    person(img, int(ex + 50), 70 + 52, 'zhang', 1, t, -1, 2)
    if t < 63.9:
        speed_lines(img, t, 70, 140, 10, PAPER, 1)
    name_tag(img, ex + 50, 78 - 14 - 22, '张定边')
    draw_text(img, 12, 32, '昨天', PAPER, outline=INK)


def s_v1e(img, t, lt):
    hz = 106
    bg(img, t, 0.5, hz)
    d = ImageDraw.Draw(img)
    # 沙洲
    for i in range(10):
        hw = 70 - i * 5
        d.line([(80 - hw, 128 + i), (80 + hw, 128 + i)], fill=SAND if i % 3 else SAND_D)
    stuck = seg(t, ct(5, 0), ct(5, 4) + 0.2)
    sh = int(math.sin(t * 40) * 2) if 64.6 < t < 66.0 else 0
    zhu_boat(img, t, 40 + sh, int(74 + stuck * 8), 2, white=True)
    # 张定边贴上来
    hit = ct(5, 12)  # 射
    hb = t >= hit
    b = scaled(small_boat(40, True), 2)
    paste(img, b, 140 + (6 if hb else 0), 70 + bob(t, 1, 1))
    zx = 190 + (int(seg(t, hit, hit + 0.4) * 10) if hb else 0)
    person(img, zx, 122, 'zhang', 0, t, -1, 2)
    name_tag(img, zx, 66, '张定边')
    # 常遇春从旁射
    paste(img, small_boat(30, True), 250, 118 + bob(t, 1, 2))
    person(img, 262, 144, 'chang', 0, t, -1, 1)
    name_tag(img, 262, 112, '常遇春')
    a0, a1 = ct(5, 8), hit  # 箭 … 射
    if a0 <= t < a1 + 0.05:
        k = seg(t, a0, a1)
        ax = lerp(254, zx + 4, k)
        ay = lerp(132, 104, k)
        d.line([(int(ax), int(ay)), (int(ax + 8), int(ay + 2))], fill=WHITE)
        d.point((int(ax), int(ay)), fill=GOLD)
    if hb:
        p = seg(t, hit, hit + 0.5)
        if p < 1:
            explosion(img, zx, 104, p, 3)
        draw_text(img, zx + 10, 82, '！', RED_L, scale=2, outline=INK)
    draw_text(img, 12, 32, '昨天', PAPER, outline=INK)


def s_pc(img, t, lt, second=False):
    hz = 108
    bg(img, t, None, hz)
    d = ImageDraw.Draw(img)
    # 云飞快：时间在过
    for i in range(5):
        cx = (hsh(i, 21) * W + lt * (18 + i * 4)) % (W + 80) - 40
        cy = 36 + i * 9
        c = lerpc(sky_colors(tod_at(t))[1], WHITE, 0.5)
        R(d, int(cx), cy, 34, 4, c)
        R(d, int(cx) + 6, cy - 3, 18, 3, c)
    if second:
        far_fleet(img, t, hz, 160, 6, dx=-lt)
    zhu_boat(img, t, 120, 78 + bob(t), 2, face=-1)
    # 影子越拉越长
    k = seg(t, LY[6 if not second else 20]['start'], LY[7 if not second else 21]['end'])
    R(d, 120 + 18, 134, int(10 + k * 70), 1, lerpc(INK, (40, 60, 90), 0.5))
    if t > (74.2 if not second else 133.3):
        bubble(img, 150, 92, '……')


def s_chorus(img, t, lt, which='C1'):
    hz = 110
    tod = bg(img, t, None, hz, choppy=0.25)
    if which == 'C2':
        far_fleet(img, t, hz, 214, 4, col=(60, 30, 44))
    zhu_boat(img, t, 214, 80 + bob(t), 2, face=-1)


def s_card(img, t, lt):
    """间奏知识卡：道具图鉴·楼船"""
    hz = 110
    bg(img, t, 0.78, hz)
    a = np.asarray(img).astype(float) * 0.35
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    d = ImageDraw.Draw(img)
    k = ease(seg(lt, 0.4, 1.2)) * (1 - ease(seg(t, 108.6, 109.6)))
    ship = tower_ship(110)
    sx = int(lerp(330, 196, k))
    paste(img, ship, sx, 52 + bob(t, 1))
    tower_flags(img, sx, 52 + bob(t, 1), 110, t, 0)
    if k <= 0.02:
        return
    x0, y0, w, h = 10, 30, 178, int(116 * k)
    if h < 12:
        return
    R(d, x0, y0, w, h, INK)
    d.rectangle([x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2], outline=PAPER)
    d.rectangle([x0 + 3, y0 + 3, x0 + w - 4, y0 + h - 4], outline=GRAY_D)
    if k < 0.95:
        return
    rows = [('道具图鉴 No.12', '楼船', GOLD),
            ('主人', '陈友谅', WHITE), ('高', '数丈', WHITE), ('外漆', '丹漆', RED_L),
            ('楼层', '每船三重', WHITE), ('船舷', '裹以铁', WHITE), ('数量', '数百艘', WHITE),
            ('特性', '上下人语声不相闻', GOLD)]
    for i, (kk, v, c) in enumerate(rows):
        yy = y0 + 8 + i * 13
        if i == 0:
            draw_text(img, x0 + 8, yy, kk, GRAY)
            draw_text(img, x0 + w - 8 - text_w(v), yy, v, c)
            R(d, x0 + 6, yy + 13, w - 12, 1, GRAY_D)
        else:
            draw_text(img, x0 + 8, yy + 2, kk, GRAY)
            draw_text(img, x0 + 46, yy + 2, v, c)
    if int(t * 2) % 2:
        draw_text(img, x0 + w - 14, y0 + h - 15, '▼', GOLD)


def s_v2a(img, t, lt):
    hz = 100
    bg(img, t, None, hz)
    for row in range(2):
        for i in range(4):
            x = 330 + i * 80 - lt * (70 + row * 30) - row * 40
            y = hz - 60 + row * 26 + bob(t, 1, i)
            paste(img, tower_ship(100 + row * 20), x, y)
            tower_flags(img, x, y, 100 + row * 20, t, 0)


def deck(img, t, hz=118):
    bg(img, t, None, hz)
    far_fleet(img, t, hz, 100, 8, col=(110, 34, 44))
    d = ImageDraw.Draw(img)
    R(d, 0, 140, W, 10, BROWN)
    R(d, 0, 140, W, 1, BROWN_L)
    for x in range(0, W, 16):
        R(d, x, 141, 1, 9, BROWN_D)


def s_v2b(img, t, lt):
    deck(img, t)
    k = seg(t, ct(13, 9), ct(13, 11))  # 缩着手
    for i in range(5):
        sh = int(math.sin(t * 30 + i) * 1) if k > 0 else 0
        person(img, 110 + i * 30 + sh, 140, 'soldier', 2 if k > 0.3 else 0, t, -1, 2)


def s_v2c(img, t, lt):
    deck(img, t)
    d = ImageDraw.Draw(img)
    # 朱元璋挥旗
    sw = math.sin(lt * 9) * 0.6
    px, py = 46, 108
    tx, ty = px + math.sin(sw) * 40, py - math.cos(sw) * 40
    person(img, 40, 140, 'zhu', 0, t, 1, 2)
    d.line([(px, py), (int(tx), int(ty))], fill=BROWN_D, width=2)
    for j in range(14):
        R(d, int(tx - 1 - j * math.cos(sw) - math.sin(sw * 2) * j * 0.3), int(ty + j * 0.2 + math.sin(t * 12 + j) * 1.5), 1, 10, RED)
    for i in range(5):
        person(img, 120 + i * 30, 140, 'soldier', 2, t, -1, 2)
    if t >= ct(14, 7):
        bubble(img, 180, 98, '……')


def s_v2d(img, t, lt):
    deck(img, t)
    d = ImageDraw.Draw(img)
    cut = ct(15, 3)  # 斩
    person(img, 40, 140, 'zhu', 0, t, 1, 2)
    for i in range(5):
        back = i in (1, 3, 4)
        if back and t >= cut:
            continue
        person(img, 120 + i * 30, 140, 'soldier', 0 if t >= cut else 2, t, -1 if not back else 1, 2)
    if cut <= t < cut + 0.08:
        R(d, 0, 0, W, H, WHITE)
    if t >= cut:
        p = seg(t, cut, cut + 0.12)
        sc = 4
        draw_text(img, 160 - 6 * sc, int(52 - (1 - p) * 10), '斩', RED, scale=sc, outline=INK)


def s_v2e(img, t, lt):
    hz = 104
    bg(img, t, None, hz)
    for i in range(3):
        x = 230 + i * 34
        paste(img, tower_ship(90), x, hz - 58 + bob(t, 1, i))
    bx = lerp(10, 150, ease(seg(t, 119.45, 121.6)))
    paste(img, scaled(small_boat(34, True), 2), bx, 70 + bob(t))
    person(img, int(bx + 34), 122, 'ding', 1, t, 1, 2)
    blade(img, int(bx + 42), 104, 0.7, 10)
    name_tag(img, bx + 34, 72, '丁普郎', GOLD)
    speed_lines(img, t, 60, 140, 12, WHITE, -1)


def s_v2f(img, t, lt):
    hz = 104
    bg(img, t, None, hz)
    for i in range(4):
        x = -20 + i * 90
        paste(img, tower_ship(100), x, hz - 58 + (i % 2) * 6)
    d = ImageDraw.Draw(img)
    R(d, 110, 132, 100, 10, BROWN_D)
    hit0, hit1 = ct(17, 0), ct(17, 5)  # 身 … 伤
    n = int(seg(t, hit0, hit1 + 0.1) * 12)
    hp = 1 - n / 12
    head = ct(17, 8)  # 头落了
    dark = t >= head + 0.15
    person(img, 160, 132, 'ding', 0, t, 1, 2, dark=dark)
    blade(img, 168, 112, 1.2, 12, INK if dark else (220, 224, 236))
    for i in range(n):
        if hsh(i, 5) > 0.2 and t < hit1 + 0.3:
            d.point((150 + int(hsh(i, 6) * 20), 106 + int(hsh(i, 7) * 22)), fill=RED_L)
    hp_bar(img, 146, 88, hp, 30)
    name_tag(img, 160, 70, '丁普郎', GOLD)
    if dark:
        draw_text(img, 196, 102, '仍直立', WHITE, outline=INK)
    if t >= ct(17, 11) - 0.2:  # 不倒
        draw_text(img, 8, 32, '《明史》：首脱犹直立', PAPER, outline=INK)


def s_v2g(img, t, lt):
    hz = 104
    bg(img, t, None, hz)
    paste(img, tower_ship(110), 196, hz - 58)
    d = ImageDraw.Draw(img)
    R(d, 40, 132, 260, 10, BROWN_D)
    person(img, 100, 132, 'ding', 0, t, 1, 2, dark=True)
    blade(img, 108, 112, 1.0, 14, INK)
    k = seg(t, ct(18, 6), ct(18, 11))
    for i in range(3):
        ex = 190 + i * 26 + k * 30
        person(img, int(ex), 132, 'enemy', 1 if k > 0 else 0, t, -1, 2)
        if t >= ct(18, 8):
            draw_text(img, int(ex) - 3, 84, '！', RED_L, outline=INK)
    if t >= ct(18, 10):
        bubble(img, 242, 82, '神！')
    draw_text(img, 8, 32, '敌惊为神', PAPER, outline=INK)


def s_v2h(img, t, lt):
    hz = 136
    bg(img, t, None, hz)
    d = ImageDraw.Draw(img)
    R(d, 159, 22, 3, 128, BROWN_D)
    flag(img, 160, 28, 30, 24, 0, t, RED, 3)
    person(img, 120, 148, 'zhu', 0, t, 1, 2)
    if t >= ct(19, 7):
        bubble(img, 120, 104, '……')


def s_br1(img, t, lt):
    hz = 108
    w = wind_at(t)
    bg(img, t, None, hz, choppy=0.3 + w * 0.7)
    zhu_boat(img, t, 112, 76 + bob(t, 1 + w), 2, face=-1)
    wind_streaks(img, t, w)
    if t >= 159.0:
        draw_text(img, 196, 44, '东北风', GOLD, scale=2, outline=INK)


def s_br2(img, t, lt):
    hz = 96
    bg(img, t, None, hz, choppy=1)
    for i in range(7):
        t0 = 160.65 + i * 0.32
        if t < t0:
            continue
        p = seg(t, t0, t0 + 0.15)
        x = 8 + i * 44
        y = 104 + (i % 2) * 14 + bob(t, 1, i) - int((1 - p) * 6)
        fire_boat(img, t, x, y, 1.0, num=i + 1)
    wind_streaks(img, t, 0.7)


def s_br3(img, t, lt):
    """敢死士撑火船顺东北风往西南（画面左）冲进楼船阵"""
    hz = 100
    bg(img, t, None, hz, choppy=1)
    for i in range(3):
        x = -36 + i * 40
        y = hz - 60 + (i % 2) * 8
        paste(img, tower_ship(100), x, y)
        tower_flags(img, x, y, 100, t, 1)
    adv = ease(seg(t, 164.9, 168.4)) * 110
    for i in range(7):
        x = 150 + (i % 4) * 42 - adv + (i // 4) * 20
        y = 100 + (i // 4) * 22 + bob(t, 1, i)
        fire_boat(img, t, int(x), y, 1.0)
    person(img, int(290 - adv), 156, 'soldier', 1, t, -1, 1)
    wind_streaks(img, t, 1)


def s_br4(img, t, lt):
    hz = 100
    p = seg(t, 168.4, 172.6)
    bg(img, t, None, hz, choppy=1, red=p * 0.35)
    for i in range(3):
        x = -40 + i * 56
        y = hz - 60 + (i % 2) * 8
        paste(img, tower_ship(100, True, p > 0.6), x, y)
        if t > 168.5 + i * 0.4:
            fire(img, x + 10, y + 58, 80, 40, t, seed=i, k=min(1, (t - 168.5 - i * 0.4) * 1.5))
            smoke(img, x + 50, y + 10, t, seed=i, k=1, top=-20)
    for i in range(7):
        x = 60 + (i % 4) * 30
        y = 108 + (i // 4) * 16
        fire_boat(img, t, x, y, 1.0, lit=True)
    for j, te in enumerate((168.5, 168.95, 169.6, 170.6, 171.2, 171.8)):
        explosion(img, 20 + j * 24, 70 + (j % 2) * 20, seg(t, te, te + 0.6), j)
    zhu_boat(img, t, 262, 108 + bob(t), 1, face=-1)
    wind_streaks(img, t, 1)


def s_fc(img, t, lt):
    hz = 104
    red = ease(seg(t, ct(31, 0), ct(31, 9)))  # 一整湖的水 都红了起来
    red = max(red, 0.35) if t < 190 else red
    bg(img, t, None, hz, red=red, choppy=0.9)
    for i in range(3):
        x = 196 + i * 44
        y = hz - 60 + (i % 2) * 8
        paste(img, tower_ship(90, True, True), x, y)
        fire(img, x + 8, y + 58, 74, 36, t, seed=i + 10)
        smoke(img, x + 45, y + 8, t, seed=i + 10, k=1, top=-10)
    wind_streaks(img, t, 0.8)
    d3 = LY[32]
    if d3['show0'] <= t < LY[33]['show0']:
        # 丁普郎站着，没等到风
        paste(img, small_boat(34, True), 226, 112)
        flag(img, 243, 114, 12, 7, 1.0, t, RED)
        person(img, 236, 138, 'ding', 0, t, -1, 1, dark=True)
        name_tag(img, 236, 98, '丁普郎', GOLD)
    elif t >= LY[33]['show0']:
        zhu_boat(img, t, 222, 104 + bob(t), 1, face=-1)


def s_v3a(img, t, lt):
    hz = 104
    bg(img, t, 1.0, hz, stars=0.8, sun=False)
    d = ImageDraw.Draw(img)
    hill(img, 40, hz, 140, 30, (24, 26, 44), (30, 32, 52))
    hill(img, 280, hz, 160, 36, (24, 26, 44), (30, 32, 52))
    for i in range(3):
        x = 60 + i * 80 + lt * 6
        paste(img, small_boat(30, True), x, hz + 10 + i * 8 + bob(t, 1, i))
    R(d, 8, 30, 98, 16, INK)
    draw_text(img, 12, 32, '八月 · 泾江口', GOLD)


def s_v3b(img, t, lt):
    hz = 104
    bg(img, t, 1.0, hz, stars=0.8, sun=False)
    d = ImageDraw.Draw(img)
    x, y = 150, hz - 60
    paste(img, tower_ship(110), x, y)
    shot = ct(35, 10)  # 穿
    if t < shot + 0.2:
        flag(img, x + 110 // 2 - 17, y, 12, 7, 0.8, t, (40, 30, 30))
    else:
        R(d, x + 110 // 2 - 22, y + 30, 6, 4, (40, 30, 30))  # 旗落
    wx, wy = x + 24 + 3 + 7, y + 78 - 16 - 41 + 5
    peek = seg(t, ct(35, 3), ct(35, 5))
    if peek > 0:
        R(d, wx, wy + 5 - int(peek * 5), 4, 4, SKIN)
        R(d, wx, wy + 5 - int(peek * 5) - 1, 4, 1, GOLD_D)
    a0 = ct(35, 7)
    if a0 <= t < shot + 0.05:
        k = seg(t, a0, shot)
        ax, ay = lerp(10, wx, k), lerp(130, wy + 2, k)
        d.line([(int(ax) - 9, int(ay) + 3), (int(ax), int(ay))], fill=WHITE)
    if shot <= t < shot + 0.1:
        R(d, 0, 0, W, H, WHITE)
    name_tag(img, x + 55, y - 18, '陈友谅')


def s_v3c(img, t, lt):
    hz = 118
    bg(img, t, 0.3, hz)
    hill(img, 160, hz, 220, 54, (70, 110, 70), (60, 98, 62))
    shrine(img, 160, hz - 44, ease(seg(t, 195.4, 196.6)), 1)
    R(ImageDraw.Draw(img), 8, 30, 98, 16, INK)
    draw_text(img, 12, 32, '第二年 · 康郎山', GOLD)


def s_v3d(img, t, lt):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (40, 22, 26))
    for y in range(0, 150, 6):
        R(d, 0, y, W, 1, (50, 28, 32))
    R(d, 0, 120, W, 30, (60, 40, 36))
    R(d, 0, 120, W, 1, (90, 60, 50))
    tablets(img, 92, 120, 12)
    draw_vtext(img, 91, 82, '丁普郎', GOLD)
    for cx in (70, 262):
        R(d, cx, 108, 4, 12, PAPER)
        fire(img, cx, 107, 4, 6, t, seed=cx)
    draw_text(img, 254, 100, '…', GRAY)
    # 冷知识
    k = seg(t, 197.6, 198.4)
    if k > 0:
        R(d, 8, 32, 200, 46, INK)
        d.rectangle([9, 33, 206, 76], outline=GOLD_D)
        draw_text(img, 14, 37, '康郎山忠臣庙 祀三十五人', WHITE)
        draw_text(img, 14, 51, '首 · 丁普郎', GOLD)
        draw_text(img, 14, 63, '——《明史》卷一三三', GRAY)


def s_out(img, t, lt):
    hz = 106
    bg(img, t, 0.84, hz, choppy=0.5)
    hill(img, 60, hz, 120, 26, (60, 40, 70), (54, 36, 64))
    shrine(img, 60, hz - 22, 1.0, 1)
    far_fleet(img, t, hz, 236, 3, col=(40, 26, 36))
    zhu_boat(img, t, int(150 - lt * 1.2), 112 + bob(t), 1, face=-1)
    wind_streaks(img, t, 0.35)


def s_end(img, t, lt):
    d = ImageDraw.Draw(img)
    bg(img, t, 0.9, 106, choppy=0.3)
    a = np.asarray(img).astype(float) * 0.3
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    R(d, 30, 30, 260, 112, INK)
    d.rectangle([31, 31, 288, 140], outline=PAPER)
    d.rectangle([33, 33, 286, 138], outline=GRAY_D)
    draw_text(img, 160 - text_w('这一仗 赢在哪？', 2) // 2, 40, '这一仗 赢在哪？', WHITE, scale=2, shadow=INK2)
    cur = int(lt / 0.9) % 2
    for i, s in enumerate(('A  一阵东北风', 'B  不退的人')):
        y = 78 + i * 18
        draw_text(img, 96, y, s, GOLD if cur == i else WHITE)
        if cur == i and int(lt * 4) % 2 == 0:
            draw_text(img, 82, y, '▶', GOLD)
    R(d, 40, 116, 240, 1, GRAY_D)
    draw_text(img, 46, 122, '下一集 · 轮到张士诚', PAPER)
    draw_text(img, 274 - text_w('合集 · 大明开局'), 122, '合集 · 大明开局', GRAY)


# ---------------- 分镜表 ----------------
def L(i):
    return LY[i]['show0']


SHOTS = [  # (开始, 函数, 主题栏, 风力表, 叙述)
    (0.0, s_title, None, False),
    (8.0, s_fleet, '湖上没有风', False),
    (21.4, s_wait, '湖上没有风', True),
    (32.6, s_sunrise, '湖上没有风', True),
    (L(0), s_v1a, '他的船像山', True),
    (L(1), s_v1b, '他的船像山', True),
    (L(3), s_v1c, '他的船像山', True),
    (L(4), s_v1d, '昨天 差一点', False),
    (L(5), s_v1e, '昨天 差一点', False),
    (L(6), s_pc, '日头往西走', True),
    (L(8), lambda i, t, lt: s_chorus(i, t, lt, 'C1'), '等一阵东北风', True),
    (93.6, s_card, '楼船上下三重', False),
    (110.35, s_v2a, '没有人肯走', True),
    (L(13), s_v2b, '没有人肯走', True),
    (L(14), s_v2c, '没有人肯走', True),
    (L(15), s_v2d, '没有人肯走', True),
    (L(16), s_v2e, '他没有倒下', True),
    (L(17), s_v2f, '他没有倒下', True),
    (L(18), s_v2g, '他没有倒下', True),
    (L(19), s_v2h, '旗一动不动', True),
    (L(20), lambda i, t, lt: s_pc(i, t, lt, True), '日头又偏西', True),
    (L(22), lambda i, t, lt: s_chorus(i, t, lt, 'C2'), '等一阵东北风', True),
    (155.4, s_br1, '风从东北来', True),
    (L(27), s_br2, '风从东北来', True),
    (L(28), s_br3, '风从东北来', True),
    (L(29), s_br4, '风从东北来', True),
    (L(30), s_fc, '湖水尽赤', True),
    (190.3, s_v3a, '一个多月以后', False),
    (L(35), s_v3b, '一个多月以后', False),
    (L(36), s_v3c, '康郎山上', False),
    (L(37), s_v3d, '康郎山上', False),
    (208.0, s_out, '风来得太晚', True),
    (228.7, s_end, None, False),
]

NARR = [  # 对话框里的叙述（没有歌词时）
    (0.0, 8.0, '至正二十三年七月 · 鄱阳湖'),
    (9.0, 15.8, '朱元璋亲自来救南昌'),
    (16.4, 23.4, '陈友谅撤围 东出鄱阳湖'),
    (24.0, 31.0, '两军遇于康郎山'),
    (31.6, 37.6, '七月己丑 天刚亮'),
    (38.2, 44.0, '湖上 一丝风也没有'),
    (94.8, 109.4, '——《明史·陈友谅传》'),
    (155.0, 156.5, '日晡'),
    (209.0, 216.0, '己丑日晡 大风起东北'),
    (216.6, 222.6, '风烈火炽 湖水尽赤'),
    (223.2, 228.4, '——《明史·太祖本纪》'),
    (229.0, 234.7, '你选哪个？评论区说说'),
]


def shot_at(t):
    cur = 0
    for i, s in enumerate(SHOTS):
        if t >= s[0]:
            cur = i
    return cur


# ---------------- 叠层 ----------------
def overlay_sign(img):
    x = W - 6 - text_w(SIGN)
    draw_text(img, x, 4, SIGN, WHITE, outline=INK)
    d = ImageDraw.Draw(img)
    sw = text_w(SEAL) + 4
    R(d, W - 6 - sw, 18, sw, 13, RED)
    draw_text(img, W - 6 - sw + 2, 18, SEAL, PAPER)


def overlay_theme(img, s):
    d = ImageDraw.Draw(img)
    w = text_w(s) + 14
    R(d, 9, 6, w, 16, INK)
    R(d, 9, 6, 4, 16, RED)
    draw_text(img, 17, 8, s, PAPER)


def overlay_wind(img, t, w):
    d = ImageDraw.Draw(img)
    x, y = 236, 34
    R(d, x, y, 78, 15, INK)
    draw_text(img, x + 3, y + 1, '风', PAPER)
    cells = 5
    on = w * cells
    for i in range(cells):
        cx = x + 18 + i * 11
        fill = i < round(on)
        col = GOLD if fill else INK2
        R(d, cx, y + 3, 9, 9, col)
        if not fill:
            blink = (w == 0 and int(t * 2) % 2 == 0 and 69 < t < 160)
            d.rectangle([cx, y + 3, cx + 8, y + 11], outline=RED if blink else GRAY_D)


def dialog_box(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 4, 151, W - 5, H - 3
    R(d, x0 + 1, y0, x1 - x0 - 1, y1 - y0 + 1, INK)
    R(d, x0, y0 + 1, x1 - x0 + 1, y1 - y0 - 1, INK)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=PAPER)


def overlay_lyric(img, t):
    Ln = line_at(t)
    if Ln is not None:
        s = Ln['text']
        hot = RED_L if chorus(Ln['sec']) else GOLD
        cols = []
        for k, c in enumerate(s):
            tc = Ln['ct'][k]
            cols.append(None if tc is None else (hot if t >= tc[0] else (150, 146, 160)))
        x = (W - text_w(s)) // 2
        draw_text(img, x, 158, s, None, colors=cols)
        if t > Ln['end'] + 0.2 and int(t * 3) % 2 == 0:
            draw_text(img, W - 18, 163, '▼', GRAY)
        return True
    for a, b, s in NARR:
        if a <= t < b:
            n = len(s) if a == 0.0 else int((t - a) * 14) + 1
            draw_text(img, (W - text_w(s)) // 2, 158, s[:n], PAPER)
            return True
    return False


BIG_HOT = set('风来红')


def overlay_big(img, t):
    Ln = line_at(t)
    if Ln is None or not chorus(Ln['sec']):
        return
    rows = Ln['text'].split(' ')
    sc = 3
    k0 = 0
    for r, row in enumerate(rows):
        x = 12
        y = 38 + r * 44
        for j, ch in enumerate(row):
            tc = Ln['ct'][k0 + j]
            if tc is not None and t >= tc[0] - 0.03:
                p = seg(t, tc[0] - 0.03, tc[0] + 0.1)
                col = RED_L if ch in BIG_HOT else WHITE
                if p < 1:
                    col = YEL
                dy = int((1 - p) * -8)
                draw_text(img, x, y + dy, ch, col, scale=sc, shadow=INK, outline=INK)
            x += 12 * sc + 2
        k0 += len(row) + 1


def compose(t, idx=None):
    i = shot_at(t) if idx is None else idx
    t0, fn, theme, hud = SHOTS[i]
    img = Image.new('RGB', (W, H), INK)
    fn(img, t, t - t0)
    return img, theme, hud


def shake_amt(t):
    if 168.4 <= t < 172.6:
        return 1
    if abs(t - ct(15, 3)) < 0.15:
        return 2
    return 0


def frame(t):
    i = shot_at(t)
    img, theme, hud = compose(t, i)
    # 镜头切换：0.2 秒像素抖动溶解
    t0 = SHOTS[i][0]
    if i > 0 and t - t0 < 0.2 and SHOTS[i][1] is not s_end:
        prev, _, _ = compose(t, i - 1)
        k = (t - t0) / 0.2
        mask = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < k
        a = np.where(mask[:, :, None], np.asarray(img), np.asarray(prev))
        img = Image.fromarray(a.astype(np.uint8), 'RGB')
    if SHOTS[i][1] in (s_v1d, s_v1e):
        img = sepia(img, 0.85)
    s = shake_amt(t)
    if s:
        a = np.roll(np.asarray(img), (int(hsh(int(t * 30), 1) * 2 * s) - s, int(hsh(int(t * 30), 2) * 2 * s) - s), (0, 1))
        img = Image.fromarray(a, 'RGB')
    overlay_big(img, t)
    if theme:
        overlay_theme(img, theme)
    if hud:
        overlay_wind(img, t, wind_at(t))
    overlay_sign(img)
    dialog_box(img)
    overlay_lyric(img, t)
    return img
