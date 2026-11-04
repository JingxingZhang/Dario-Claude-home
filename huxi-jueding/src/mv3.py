"""《呼吸决定》像素 MV 第二版：画面里也是“综艺”——像素花字（拟声词、印章、OS、系统消息、弹窗、数值条、弹幕），
橘猫配角吐槽，月亮/路灯/垃圾桶/闹钟/日历/手机/心/楼房都有表情。底部歌词仍是高清综艺花字。
所有镜头的动作都按“这句歌词开唱后第几秒（lt）”编排，第二遍主歌/副歌直接复用。"""
import math
import numpy as np
from PIL import Image, ImageDraw
from pixlib import *
from chars import person, heart, sparkle, sweat, vein, qmark, concentration, burst, dots_bg, rose, envelope, magnifier, scooter, \
    curtains, spotlight, wave_line, chat_bubble, PINK, HEART, CYAN, NEON_P, NEON_B, NEON_Y, K, R, paste, scaled
from props2 import *
import mv2
from mv2 import street, room, rain, rms, pump, beat_phase, LS, HZ, TITLE, END, DUR
import huazi as Z


def sky_moon(img, expr='happy', blush=False, v2=False):
    moon(img, 262, 24, 10, expr, (255, 214, 232) if v2 else (250, 240, 200), blush)


def neon_sign(img, x, y, s, col, t, flick=False, scale=1):
    on = not flick or int(t * 6) % 3 != 0
    spr = ptext_sprite(s, scale, col if on else lerpc(col, K, 0.6), None, lerpc(col, WHITE, 0.6) if on else (60, 50, 70), K, False)
    d = ImageDraw.Draw(img)
    R(d, x - 3, y - 2, spr.width + 6, spr.height + 4, (20, 14, 30))
    d.rectangle([x - 3, y - 2, x + spr.width + 2, y + spr.height + 1], outline=col if on else (60, 50, 70))
    paste(img, spr, x, y)


def letterbox(img, k=1.0, label=None):
    d = ImageDraw.Draw(img)
    h = int(16 * k)
    R(d, 0, 0, W, h, K); R(d, 0, H - h, W, h, K)
    if label and k >= 1:
        ptext(img, W - 30, 22, label, 1, (255, 230, 120), None, WHITE, K)


# ======================= 镜头 =======================
def s_title(img, t, lt, v):
    room(img, t)
    sky_moon_in_window(img, 'sleep')
    person(img, 200, 132, 'girl', -1, 'closed', 'down', t, 2, breathe=math.sin(t * 2))
    d = ImageDraw.Draw(img); R(d, 0, 128, W, 8, (96, 58, 40)); R(d, 0, 128, W, 1, (140, 90, 60))
    cat(img, 100, 129, t, 'sleep', face_dir=1, scale=2)
    for i in range(3):
        ph = (t * 0.5 + i / 3) % 1
        draw_text(img, 112 + int(ph * 14), 100 - int(ph * 24), 'z' if i % 2 else 'Z', (220, 220, 255), outline=K)


def sky_moon_in_window(img, expr):
    moon(img, 262, 34, 9, expr)


def s_phone(img, t, lt, v):
    room(img, t)
    sky_moon_in_window(img, 'smirk' if lt > 6 else 'sleep')
    buzz = 2.5 <= lt < 3.7
    pick = lt >= 3.7
    ex = 'surprised' if 2.5 <= lt < 4.5 else ('happy' if lt >= 6 else 'closed' if lt < 2.5 else 'side')
    person(img, 200, 132, 'girl', -1, ex, 'phone' if pick else 'down', t, 2)
    d = ImageDraw.Draw(img); R(d, 0, 128, W, 8, (96, 58, 40)); R(d, 0, 128, W, 1, (140, 90, 60))
    if not pick:
        jx = int(math.sin(t * 60) * 1) if buzz else 0
        R(d, 168 + jx, 122, 10, 6, K); R(d, 169 + jx, 123, 8, 4, CYAN if buzz else (60, 60, 80))
    if buzz:
        sfx(img, 172, 104, '嗡嗡', t, 9.5 + 2.5, 1.2, 'cyan', 1, jitter=1)
    if 3.0 <= lt < 6.5:
        say(img, 140, 76, '新消息 ♥', t, 9.5 + 3.0, tail='r', bg=(255, 220, 236))
    if 4.6 <= lt < 8.0:
        OS(img, 196, 40, '又是他？', t, 9.5 + 4.6)
    cexpr = 'shock' if 2.6 <= lt < 5 else ('side' if lt >= 6.5 else 'normal')
    cat(img, 100, 129, t, 'sit' if lt >= 2.6 else 'sleep', cexpr, 1, 2)
    if lt >= 2.6:
        sfx(img, 92, 70, '?!', t, 9.5 + 2.6, 1.0, 'yel', 1)
    if lt >= 6.6:
        sfx(img, 80, 74, '啧', t, 9.5 + 6.6, 1.5, 'purp', 1)


def s_walk(img, t, lt, v):
    stop = 7.3
    scroll = min(lt, stop) * 40 + 600
    street(img, t, False, scroll=scroll, rain_k=0.9)
    sky_moon(img, 'happy' if lt < 6 else 'shock')
    stamp(img, 50, 30, '第一天', t, 19.3, (240, 90, 150))
    walking = lt < stop
    if lt >= 5.5:
        bx = lerp(360, 236, ease(seg(lt, 5.5, 7.8)))
        lamp(img, int(bx) + 18, 128, 'shock' if lt < 8.4 else 'smirk', True, 76)
        neon_sign(img, int(bx) - 30, 6, 'HI', NEON_B, t, flick=True, scale=2)
        person(img, int(bx), 126, 'boy', -1, 'smirk', 'down', t, 2, walk=lt < 7.8)
        if lt > 8.0:
            sfx(img, int(bx) - 22, 48, '叮~', t, 19 + 8.0, 1.6, 'yel', 1)
    person(img, 120, 126, 'girl', 1, 'smile', 'umbrella', t, 2, walk=walking, umbrella=PINK)
    cat(img, 84, 127, t, 'walk' if walking else 'sit', 'side' if lt > 8 else 'normal', 1, 1)


def s_hi(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=1060, rain_k=0.6)
    sky_moon(img, 'happy', v2=v2)
    neon_sign(img, 196, 30, 'HI', NEON_B if lt < 0.9 else NEON_Y, t, flick=lt < 0.9, scale=2)
    lamp(img, 268, 128, 'blush' if lt > 1.0 else 'happy', True, 76)
    person(img, 104, 126, 'girl', 1, 'happy', 'wave', t, 2, umbrella=PINK)
    person(img, 214, 126, 'boy', -1, 'surprised' if lt < 1.0 else 'blush', 'down', t, 2)
    if lt > 0.1:
        say(img, 126, 44, '嗨~', tail='l')
    sfx(img, 236, 50, '叮！', t, t - lt + 0.9, 1.6, 'yel', 2)
    cat(img, 70, 127, t, 'sit', 'happy', 1, 1)
    if lt > 1.5:
        say(img, 40, 96, '喵？', tail='r')


def s_bad(img, t, lt, v):
    v2 = v is True
    burst(img, t, (70, 20, 90) if not v2 else (100, 20, 80), (110, 40, 140) if not v2 else (160, 40, 120))
    wk = int(beat_phase(t) < 0.25)
    person(img, 214, 150, 'boy', -1, 'wink' if wk else 'smirk', 'fist', t, 3, horns=lt > 1.0)
    if lt > 1.0:
        d = ImageDraw.Draw(img)
        d.line([(236, 126), (250, 120), (252, 112)], fill=(220, 40, 60), width=2)  # 小恶魔尾巴
        R(d, 250, 108, 5, 4, (220, 40, 60))
    meter(img, 8, 30, '渣男指数', ease(seg(lt, 0.3, 2.4)) * 0.99, (255, 70, 110), 64, blink=lt > 2.4)
    if lt > 2.5:
        sfx(img, 60, 56, '警报！', t, t - lt + 2.5, 9, 'red', 1, jitter=1)
    person(img, 60, 150, 'girl', 1, 'pout', 'down', t, 2)
    if int(t * 3) % 2:
        vein(img, 72, 64)
    cat(img, 128, 150, t, 'hiss', 'angry', 1, 2)
    sfx(img, 128, 92, '哈——！', t, t - lt + 1.8, 2.0, 'red', 1, jitter=1)
    if lt > 3.4:
        OS(img, 6, 98, '坏透了', t, t - lt + 3.4)


def s_twodays(img, t, lt, v):
    dots_bg(img, t, (255, 220, 236) if v is not True else (250, 200, 240), (255, 196, 220))
    flip = seg(lt, 1.3, 1.6)
    calendar_face(img, 12, 26, 'DAY 2' if flip >= 1 else 'DAY 1', 'shock' if flip >= 1 else 'happy', flip if flip < 1 else 0)
    sfx(img, 60, 30, '啪', t, t - lt + 1.6, 1.0, 'red', 2)
    meter(img, 110, 8, '恋爱进度', ease(seg(lt, 1.7, 2.6)), (255, 90, 160), 70)
    if lt > 2.6:
        sfx(img, 290, 14, '!?', t, t - lt + 2.6, 9, 'yel', 1, jitter=1)
    k = 2 + ease(seg(lt, 1.7, 3.6)) * 3
    kk = max(2, int(round(k + pump(t))))
    hx, hy = 200, 58
    d = ImageDraw.Draw(img)
    d.line([(236, 106), (hx, hy + 4 * kk)], fill=WHITE)
    heart_face(img, hx, hy, kk, 'heart' if kk >= 4 else 'happy')
    person(img, 240, 150, 'boy', -1, 'smile', 'point', t, 2)
    person(img, 92, 150, 'girl', 1, 'surprised', 'down', t, 2)
    cat(img, 40, 150, t, 'sit', 'shock', 1, 2)
    sweat(img, 30, 92, 2)
    if lt > 3.0:
        say(img, 8, 76, '这么快？', tail='l')


def s_truelove(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=1060, rain_k=0.4)
    sky_moon(img, 'side', v2=v2)
    spotlight(img, 214, 0, 130, 50)
    person(img, 214, 128, 'boy', -1, 'smile', 'hold', t, 2, kneel=True)
    rose(img, 184, 86)
    for i in range(4):
        if int(t * 6 + i) % 3:
            sparkle(img, 180 + int(hsh(i, 4) * 60), 50 + int(hsh(i, 5) * 30), 2)
    # 测谎仪
    meter(img, 8, 30, '测谎仪', 0.1 + 0.85 * abs(math.sin(lt * 9)) if lt < 1.3 else 0.97, (255, 60, 60), 56, show_pct=False)
    if lt > 0.6:
        sfx(img, 150, 30, '滴滴滴', t, t - lt + 0.6, 0.8, 'red', 1, jitter=1)
    if lt > 1.3:
        stamp(img, 150, 32, '假', t, t - lt + 1.3, (230, 40, 60), scale=2)
    person(img, 92, 128, 'girl', 1, 'side', 'down', t, 2)
    OS(img, 6, 52, '信你才怪', t, t - lt + 0.3)
    cat(img, 52, 128, t, 'up', 'side', 1, 1, sign='?')


def s_hi2(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=1060, rain_k=0.4)
    sky_moon(img, 'blush' if lt > 2.2 else 'happy', blush=lt > 2.2, v2=v2)
    p = seg(lt, 1.0, 2.2)
    person(img, 100, 128, 'girl', 1, 'wink', 'wave', t, 2)
    person(img, 222, 128, 'boy', -1, 'blush' if p >= 1 else 'surprised', 'cover' if p >= 1 else 'down', t, 2)
    say(img, 50, 44, '嗨~ ♥', tail='l') if lt > 0.15 else None
    if 0 < p < 1:
        heart_face(img, int(lerp(124, 214, p)), int(70 - math.sin(p * math.pi) * 40), 2, 'happy')
    if p >= 1:
        sfx(img, 262, 44, '扑通', t, t - lt + 2.2 + int((lt - 2.2) / 0.8) * 0.8, 0.5, 'pink', 1)
        for i in range(5):
            a = i / 5 * 6.283 + t
            r = 14 + (lt - 2.2) * 16
            if r < 50:
                heart(img, int(222 + math.cos(a) * r), int(64 + math.sin(a) * r), 1)
    cat(img, 160, 128, t, 'sit', 'cover' if lt > 2.4 else 'normal', -1, 1)
    if lt > 3.0:
        say(img, 140, 86, '没眼看', tail='l')
    letterbox(img, ease(seg(lt, 0, 0.3)), '特写')


def s_chat(img, t, lt, v):
    dots_bg(img, t, (230, 236, 255), (210, 220, 250))
    phone_face(img, 116, 8, 88, 132, 'shock' if lt > 4.2 else 'happy')
    chat_bubble(img, 148, 30, 50, 15, (255, 160, 200), right=True)
    draw_text(img, 151, 32, '在恋爱吗', K)
    if lt < 3.0:
        if lt > 0.8:
            draw_text(img, 122, 50, '对方正在输入…', (90, 100, 140))
    else:
        chat_bubble(img, 122, 50, 48, 15, (220, 224, 236))
        draw_text(img, 125, 52, '没有呀~', K)
    if lt > 4.2:
        d = ImageDraw.Draw(img)
        y = 76 + int((1 - seg(lt, 4.2, 4.4)) * 10)
        R(d, 118, y, 84, 26, (40, 40, 60)); R(d, 119, y + 1, 82, 24, (255, 236, 244))
        heart(img, 126, y + 7, 1)
        draw_text(img, 133, y + 1, '小美：', (230, 60, 110))
        draw_text(img, 133, y + 12, '宝贝晚安♥', K)
        sfx(img, 236, 70, '叮！', t, t - lt + 4.2, 1.2, 'yel', 2)
    if lt > 4.8:
        stamp(img, 236, 40, '翻车', t, t - lt + 4.8, (230, 40, 60))
    person(img, 56, 150, 'girl', 1, 'side' if lt > 4.2 else 'smile', 'phone', t, 2)
    cat(img, 262, 150, t, 'sit', 'shock' if lt > 4.2 else 'normal', -1, 2)
    if lt > 4.4:
        sfx(img, 262, 90, '!!', t, t - lt + 4.4, 9, 'red', 1)


def s_dump(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=1300, rain_k=0.4)
    sky_moon(img, 'side', v2=v2)
    throw = 1.6
    eat = 2.4
    trash_face(img, 270, 104, 'laugh' if lt > eat else 'happy', lid=1.0 if 2.0 < lt < eat + 0.3 else 0)
    labels = ['A', 'B', 'C']
    for i in range(3):
        a = t * 5 + i * 2.1
        if i == 0 and lt >= throw:
            p = seg(lt, throw, eat)
            if p < 1:
                x, y = int(lerp(176, 280, p)), int(40 - math.sin(p * math.pi) * 30 + p * 56)
                heart_face(img, x, y, 2, 'shock')
            continue
        x, y = int(176 + math.cos(a) * 18), int(44 + math.sin(a) * 10)
        heart_face(img, x, y, 2, 'happy')
        draw_text(img, x - 3, y - 18, labels[i], WHITE, outline=K)
    if lt > eat:
        sfx(img, 282, 84, '嗝~', t, t - lt + eat, 1.6, 'green', 1)
        ptext(img, 220, 30, '前任+1', 1, (210, 255, 170), (70, 200, 90), WHITE, K)
    person(img, 176, 128, 'boy', -1, 'smirk', 'heart', t, 2)
    person(img, 70, 128, 'girl', 1, 'side', 'down', t, 2)
    cat(img, 112, 128, t, 'up', 'side', -1, 1, sign='渣')


def s_search(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=1500, rain_k=0.4)
    sky_moon(img, 'laugh', v2=v2)
    sfx(img, 236, 24, '噗', t, t - lt + 0.9, 1.4, 'yel', 1)
    look = math.sin(lt * 2.4)
    person(img, 120, 128, 'boy', -1, 'sad', 'point', t, 2)
    magnifier(img, int(78 + look * 20), 70)
    say(img, 60, 36, '唉~真爱好难找', tail='r')
    person(img, 200, 128, 'girl', -1, 'pout', 'hold', t, 2)
    heart_face(img, 178, 84, 2, 'happy')
    cat(img, 250, 128, t, 'up', 'normal', -1, 1, sign='在这↓')


def s_now(img, t, lt, v):
    burst(img, t, (255, 230, 120), (255, 200, 80))
    concentration(img, 240, 90, t, (255, 255, 255))
    clock_face(img, 160, 46, 18, t, 'scream')
    sfx(img, 90, 40, '啪！', t, t - lt + 0.1, 1.0, 'red', 2, slam=True)
    for i, s in enumerate(('3', '2', '1')):
        if 0.8 + i * 0.6 <= lt < 1.4 + i * 0.6:
            ptext(img, 220, 30, s, 3, (255, 250, 200), (255, 150, 40), WHITE, K)
    if lt > 2.6:
        sfx(img, 222, 34, 'NOW!', t, t - lt + 2.6, 9, 'red', 2, jitter=1)
    person(img, 70, 150, 'girl', 1, 'angry', 'point', t, 2)
    jump = int(abs(math.sin(lt * 10)) * 4) if lt < 0.6 else 0
    person(img, 250, 150 - jump, 'boy', -1, 'surprised', 'down', t, 2)
    sweat(img, 268, 74, 2)
    if lt < 0.8:
        sfx(img, 280, 60, '吓', t, t - lt + 0.1, 0.7, 'cyan', 1)
    cat(img, 128, 150, t, 'sit', 'shock', 1, 1)


def s_confess(img, t, lt, v):
    interrogation(img, t)
    stamp(img, 160, 22, '坦白局', t, t - lt + 0.2, (230, 40, 60))
    items = ['1.劈腿', '2.已读不回', '3.删聊天记录', '4.同时约三个']
    k = seg(lt, 0.9, 4.2)
    scroll_list(img, 8, 34, items, k, t)
    n = int(len(items) * k + 0.999) if k > 0 else 0
    if 0 < n:
        sfx(img, 112, 40 + (n - 1) * 14, '叮', t, t - lt + 0.9 + (n - 1) * 3.3 / 4, 0.5, 'yel', 1)
    person(img, 160, 126, 'boy', 1, 'sad', 'hold', t, 2)
    for i in range(3):
        ph = (t * 1.5 + i / 3) % 1
        sweat(img, 140 + i * 18, int(46 + ph * 20), 1)
    sfx(img, 196, 44, '汗', t, t - lt + 0.5, 9, 'cyan', 1, jitter=1)
    person(img, 262, 126, 'girl', -1, 'angry', 'point', t, 2)
    cat(img, 226, 128, t, 'sit', 'angry', -1, 1, hat='police')


def s_letter(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=1900, rain_k=0.3)
    sky_moon(img, 'happy', v2=v2)
    op = seg(lt, 2.1, 2.6)
    meter(img, 96, 26, '表白加载中', ease(seg(lt, 0.3, 2.0)), (120, 220, 255), 56)
    person(img, 96, 128, 'girl', 1, 'smile' if op > 0.5 else 'side', 'ear', t, 2)
    person(img, 220, 128, 'boy', -1, 'blush', 'hold', t, 2)
    envelope(img, 172, 82, op)
    if op >= 1:
        sfx(img, 188, 54, '啵~', t, t - lt + 2.6, 1.2, 'pink', 1)
        heart_face(img, 186, int(64 - (lt - 2.6) * 10), 2, 'heart')
    say(img, 30, 52, '说吧 我听着', tail='l') if lt > 0.3 else None
    cat(img, 136, 128, t, 'up', 'happy', 1, 1, sign='准')


def s_likeme(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=2100, ground=140, rain_k=0.2)
    sky_moon(img, 'blush', True, v2=v2)
    d = ImageDraw.Draw(img)
    big_heart_building(img, 140, t, seg(lt, 0.8, 2.8))
    R(d, 0, 130, W, 20, (90, 90, 110)); R(d, 0, 130, W, 2, (130, 130, 150))
    for x in range(0, W, 24):
        R(d, x, 126, 4, 4, (90, 90, 110))
    person(img, 70, 132, 'boy', 1, 'happy', 'point', t, 2)
    megaphone(img, 88, 86, t, 1)
    if lt > 0.4:
        sfx(img, 176, 72, '我是真的喜欢你!!', t, t - lt + 0.4, 9, 'pink', 1, jitter=1)
    for i, tb in enumerate((2.3, 2.9, 3.5)):
        firework(img, 100 + i * 60, 30 + (i % 2) * 10, lt, tb, [NEON_Y, NEON_P, NEON_B][i])
    person(img, 256, 132, 'girl', -1, 'shy', 'cover', t, 2)
    draw_text(img, 268, 56, '///', BLUSH if False else (255, 140, 160), outline=K)
    cat(img, 214, 132, t, 'sit', 'heart', -1, 1, hearts=True)


def s_dream(img, t, lt, v):
    burst(img, t, (255, 170, 210), (255, 206, 230))
    d = ImageDraw.Draw(img)
    for i in range(18):
        x = (hsh(i, 1) * W + t * 14) % W
        y = (hsh(i, 2) * H + t * 24) % H
        R(d, int(x), int(y), 3, 2, (255, 240, 246))
    person(img, 130, 160, 'girl', 1, 'heart', 'heart', t, 3, breathe=math.sin(t * 3))
    # 幻想泡泡：电影票、冰淇淋、摩天轮
    bubble_box(img, 196, 18, 110, 46, WHITE, K, 'think')
    R(d, 204, 30, 22, 14, (255, 200, 80)); draw_text(img, 206, 31, '票', K)
    R(d, 238, 28, 10, 10, (255, 170, 200)); d.polygon([(237, 38), (249, 38), (243, 52)], fill=(220, 170, 110))
    ferris(img, 282, 38, 12, t)
    toggle(img, 200, 74, '恋爱模式', lt > 1.5)
    if lt > 1.5:
        sfx(img, 290, 98, 'ON!', t, t - lt + 1.5, 9, 'green', 1)
    cat(img, 40, 160, t, 'roll', 'happy', 1, 2, hearts=True)


def s_dial(img, t, lt, v):
    v2 = v is True
    dots_bg(img, t, (40, 50, 110) if not v2 else (90, 30, 100), (60, 72, 140) if not v2 else (120, 50, 130))
    lever = clamp(1 - abs(lt - 0.5) / 0.3) if lt < 0.8 else 0
    slot_machine(img, 92, 26, lt, (1.6, 2.1, 2.6), ('heart', 'heart', 'heart'), lever)
    cat(img, 236, 112, t, 'up', 'happy' if lt > 2.6 else 'normal', -1, 2)
    if lt > 2.7:
        sfx(img, 152, 16, 'JACKPOT!', t, t - lt + 2.7, 9, 'yel', 1, jitter=1)
        for i in range(8):
            ph = (lt - 2.7 + i * 0.13) % 1
            heart(img, int(110 + i * 12 + math.sin(t * 4 + i) * 3), int(100 + ph * 30), 1)
    person(img, 40, 150, 'girl', 1, 'heart' if lt > 2.6 else 'surprised', 'down', t, 2)
    person(img, 284, 150, 'boy', -1, 'blush' if lt > 2.6 else 'surprised', 'down', t, 2)


def s_breath(img, t, lt, v):
    v2 = v is True
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (16, 14, 40) if not v2 else (40, 12, 50))
    wave_line(img, 36, t, 3 + rms(t) * 10, CYAN, beat=1.0)
    bpm = int(75 + 45 * ease(seg(lt, 0.3, 2.6)))
    ptext(img, 40, 62, f'BPM {bpm}', 1, (200, 250, 255), (50, 170, 255), WHITE, K)
    br = math.sin(t * 2.4) * 1.5
    person(img, 128, 140, 'girl', 1, 'closed', 'down', t, 2, breathe=br)
    person(img, 192, 140, 'boy', -1, 'closed', 'down', t, 2, breathe=br)
    heart_face(img, 160, 66, 2 + int(pump(t) > 0.35), 'blush')
    sfx(img, 108, 56, '呼~', t, t - lt + 0.3, 1.0, 'cyan', 1)
    sfx(img, 214, 56, '吸~', t, t - lt + 1.3, 1.0, 'cyan', 1)
    sfx(img, 108, 56, '呼~', t, t - lt + 2.3, 1.0, 'cyan', 1)
    moon(img, 296, 84, 9, 'blush', blush=True)


def s_ride(img, t, lt, v):
    v2 = v is True
    seg_i = min(2, int(lt / 0.9))
    d = ImageDraw.Draw(img)
    if seg_i == 0:
        street(img, t, v2, scroll=t * 160, rain_k=0)
        ferris(img, 250, 54, 34, t)
        tag = '游乐园'
    elif seg_i == 1:
        R(d, 0, 0, W, 110, (120, 200, 250))
        sun(img, 60, 34, 12, 'happy', t)
        wave_sea(img, t, 96)
        R(d, 0, 118, W, 62, (240, 220, 160))
        tag = '海边'
    else:
        R(d, 0, 0, W, H, (150, 200, 250))
        mountains(img, t * 200, 128)
        R(d, 0, 128, W, 52, (110, 170, 90))
        tag = '山里'
    R(d, 0, 128, W, 8, (70, 70, 90))
    for x in range(int(-t * 400) % 30 - 30, W, 30):
        R(d, x, 131, 14, 2, WHITE)
    sub = Image.new('RGBA', (110, 70), (0, 0, 0, 0))
    person(sub, 44, 54, 'girl', 1, 'happy', 'wave', t, 1)
    person(sub, 60, 54, 'boy', 1, 'happy', 'point', t, 1)
    scooter(sub, 20, 60, t)
    cat(sub, 76, 52, t, 'sit', 'happy', 1, 1, hat='goggle')
    paste(img, scaled(sub, 2), 70, 10 + int(math.sin(t * 9)))
    ptext(img, 40, 28, tag, 1, (255, 255, 255), (220, 230, 255), WHITE, K)
    sfx(img, 280, 24, 'GO!', t, t - lt + 0.1, 9, 'green', 2)


def s_nofeel(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=2300, rain_k=0.4)
    sky_moon(img, 'side', v2=v2)
    off = lt > 1.2
    toggle(img, 110, 26, '感情', not off)
    if off:
        sfx(img, 196, 32, '咔', t, t - lt + 1.2, 0.8, 'white', 1)
    p = seg(lt, 1.8, 2.6)
    closed = lt > 2.8
    safe_box(img, 180, 80, closed, lt > 3.2)
    if not closed:
        heart_face(img, int(lerp(150, 202, p)), int(lerp(84, 100, p)), 2, 'sad')
    if lt > 3.2:
        stamp(img, 202, 70, '封存', t, t - lt + 3.2, (120, 120, 140))
    person(img, 84, 128, 'girl', 1, 'smile', 'shrug', t, 2)
    person(img, 272, 128, 'boy', -1, 'surprised', 'down', t, 2)
    cat(img, 136, 128, t, 'sleep', 'normal', 1, 1)
    if lt > 2.0:
        say(img, 100, 86, '无所谓~', tail='l')


def s_cool(img, t, lt, v):
    v2 = v is True
    runway(img, t, v2)
    b = int(pump(t, 2))
    gx = lerp(110, 200, seg(lt, 0, 4.3))
    person(img, int(gx), 136 - b, 'girl', 1, 'smile', 'down', t, 2, walk=True, glasses=True)
    cat(img, int(gx) - 34, 136 - b, t, 'walk', 'normal', 1, 1, glasses=True)
    person(img, 290, 136, 'boy', -1, 'surprised', 'down', t, 2)
    sfx(img, 290, 52, '???', t, t - lt + 0.8, 9, 'purp', 1, jitter=1)
    for i, bt in enumerate((0.3, 1.1, 1.9, 2.7, 3.5)):
        sfx(img, 60 + (i % 3) * 30, 30 + (i % 2) * 14, 'COOL', t, t - lt + bt, 0.6, 'cyan', 1)
    if lt > 2.0:
        ptext(img, 160, 22, '做自己', 2, (255, 250, 180), (255, 160, 40), WHITE, K)
    # 闪光灯
    if int(t * 8) % 5 == 0:
        sparkle(img, 30 + int(hsh(int(t * 8), 1) * 60), 60, 4, WHITE)


def s_stage(img, t, lt, v):
    d = ImageDraw.Draw(img)
    R(d, 0, 0, W, H, (24, 14, 30))
    R(d, 0, 128, W, 22, (110, 70, 50)); R(d, 0, 128, W, 2, (160, 110, 70))
    spotlight(img, 170, 14, 128, 46)
    drop = seg(lt, 1.7, 2.2)
    # 纸板月亮道具
    if drop <= 0:
        R(d, 206, 70, 2, 40, (130, 90, 60))
        moon(img, 207, 60, 10, 'smirk')
    person(img, 170, 128, 'boy', -1, 'surprised' if drop > 0 else 'smile', 'hold' if drop <= 0 else 'down', t, 2, mask=drop <= 0)
    if drop > 0:
        mx, my = 150 - int(drop * 20), int(48 + drop * 76)
        R(d, mx, my, 13, 8, (250, 250, 250)); R(d, mx + 3, my + 3, 2, 2, K); R(d, mx + 8, my + 3, 2, 2, K)
        sfx(img, 128, 110, '啪嗒', t, t - lt + 2.1, 1.0, 'white', 1)
        sweat(img, 188, 50, 2)
    clapper(img, 240, 30, t, lt > 0.6)
    if lt > 0.6:
        sfx(img, 264, 20, '卡！', t, t - lt + 0.6, 1.4, 'red', 2, slam=True)
    curtains(img, ease(seg(lt, 2.8, 3.9)), t)
    if lt > 3.5:
        ptext(img, 160, 70, '谢幕', 2, (255, 240, 200), (240, 190, 90), WHITE, K)
    person(img, 40, 176, 'girl', 1, 'side', 'down', t, 2)
    cat(img, 84, 176, t, 'sit', 'side', 1, 1)
    score_card(img, 52, 100, '0')
    score_card(img, 90, 118, '0')


def s_blame(img, t, lt, v):
    v2 = v is True
    burst(img, t, (40, 30, 70) if not v2 else (70, 20, 70), (60, 44, 96) if not v2 else (100, 30, 90))
    person(img, 70, 148, 'boy', 1, 'angry', 'point', t, 2)
    say(img, 30, 40, '都怪你！', tail='l')
    p = seg(lt, 0.6, 1.0)
    dodge = 16 if lt > 0.9 else 0
    if 0 < p < 1 or lt < 1.3:
        ax = int(lerp(100, 260, p))
        d = ImageDraw.Draw(img)
        R(d, ax - 30, 98, 30, 4, (240, 60, 80)); d.polygon([(ax, 92), (ax + 10, 100), (ax, 108)], fill=(240, 60, 80))
    person(img, 250 + dodge, 148, 'girl', -1, 'side', 'down', t, 2)
    if lt > 0.9:
        sfx(img, 236, 60, '闪', t, t - lt + 0.9, 0.8, 'cyan', 2)
    crack = lt > 1.5
    heart_face(img, 160, 58, 4, 'sad' if crack else 'shock', broken=crack)
    if crack:
        sfx(img, 196, 30, '咔嚓', t, t - lt + 1.5, 1.4, 'yel', 2, jitter=1)
    cat(img, 160, 148, t, 'sit', 'side', 1, 1)
    if lt > 2.0:
        say(img, 150, 100, '关我啥事', tail='l')


def s_decide(img, t, lt, v):
    v2 = v is True
    street(img, t, v2, scroll=2600, rain_k=0.5)
    sky_moon(img, 'shock' if lt > 1.4 else 'side', v2=v2)
    pressed = lt > 1.4
    popup(img, 84, 20, '系统提示', '确定离开吗？', ('是', '否'), sel=0, pressed=pressed)
    cx_ = int(lerp(220, 118, ease(seg(lt, 0.2, 0.9))))
    cy_ = int(lerp(100, 64, ease(seg(lt, 0.2, 0.9))))
    cursor(img, cx_, cy_)
    if pressed:
        sfx(img, 236, 22, '叮咚', t, t - lt + 1.4, 1.2, 'yel', 1)
        sys_msg(img, 160, 86, '已确认：你选的')
    person(img, 236, 128, 'boy', -1, 'sad' if pressed else 'pout', 'point', t, 2)
    person(img, 70, 128, 'girl', 1, 'side', 'down', t, 2)
    OS(img, 6, 100, '你选的哦', t, t - lt + 1.8)
    cat(img, 120, 128, t, 'sit', 'normal', 1, 1)


def s_words(img, t, lt, v):
    dots_bg(img, t, (250, 230, 240), (240, 210, 226))
    person(img, 120, 168, 'girl', 1, 'closed', 'chest', t, 3)
    words = ['嗨', '深爱', '真爱', '喜欢你', '离开']
    n = 0
    for i, w in enumerate(words):
        p = (lt * 0.9 - i * 0.6)
        if p >= 1:
            n += 1
        if 0 < p < 1:
            x = lerp(300, 128, ease(p)); y = lerp(30 + i * 16, 104, ease(p))
            tw = text_w(w) + 8
            bubble_box(img, int(x) - tw // 2, int(y), tw, 15, WHITE, K, 'r')
            draw_text(img, int(x) - tw // 2 + 4, int(y) + 2, w, K)
    heart_face(img, 121, 104, 2 + min(2, n // 2), 'blush')
    meter(img, 180, 128 - 108, '记住了', n / 5, (255, 100, 160), 50, show_pct=False)
    if n >= 5:
        sfx(img, 250, 46, '已保存', t, t - lt + 0.6 * 4 + 1.1, 9, 'green', 1)
    cat(img, 250, 168, t, 'sit', 'heart', -1, 2)


def s_leave(img, t, lt, v):
    final = v is True
    street(img, t, final, scroll=2900, rain_k=1.0)
    sky_moon(img, 'sad', v2=final)
    bx = lerp(190, 360, ease(seg(lt, 0.4, 5.0)))
    lamp(img, 280, 128, 'sad', int(t * 3) % 4 != 0, 76)
    person(img, int(bx), 128, 'boy', 1, 'closed', 'down', t, 2, walk=bx < 359)
    if lt > 1.5:
        sys_msg(img, 160, 30, '—— 对方已离开 ——')
    if not final:
        person(img, 90, 128, 'girl', 1, 'sad', 'umbrella', t, 2, umbrella=PINK)
        cat(img, 56, 128, t, 'sit', 'normal', 1, 1)
        if lt > 3.0:
            say(img, 30, 86, '喵…', tail='l')
    else:
        turn = lt >= 3.3
        if not turn:
            person(img, 90, 128, 'girl', 1, 'sad', 'umbrella', t, 2, umbrella=PINK)
            cat(img, 56, 128, t, 'sit', 'normal', 1, 1)
        else:
            gx = lerp(90, -40, ease(seg(lt, 4.0, 6.7)))
            person(img, int(gx), 128, 'girl', -1, 'smile', 'down', t, 2, walk=True)
            cat(img, int(gx) + 30, 128, t, 'walk', 'happy', -1, 1)
            stamp(img, 214, 74, '清醒', t, t - lt + 3.4, (60, 160, 90))


def s_interlude(img, t, lt, v):
    fog = clamp(seg(lt, 11.4, 13.4)) * (1 - seg(lt, 20.4, 22))
    room(img, t, fog=fog)
    sky_moon_in_window(img, 'happy' if lt > 18 else 'sad')
    d = ImageDraw.Draw(img)
    stamp(img, 62, 26, '回忆杀', t, t - lt + 0.8, (240, 90, 150), dur=4)
    caps = [('DAY1', 'heart'), ('嗨', 'hi'), ('坦白局', 'list'), ('喜欢你', 'heart'), ('离开', 'door')]
    for i, (cap, ic) in enumerate(caps):
        p = (lt - 2.5 - i * 1.6) / 6
        if 0 < p < 1:
            x = int(lerp(300, 10, p)); y = int(40 + math.sin(p * 6 + i) * 12 + i * 5)
            R(d, x - 1, y - 1, 34, 40, K); R(d, x, y, 32, 38, (250, 250, 245)); R(d, x + 2, y + 2, 28, 22, (90, 80, 130))
            if ic == 'heart':
                heart(img, x + 16, y + 13, 1)
            elif ic == 'hi':
                draw_text(img, x + 9, y + 6, 'HI', NEON_B)
            elif ic == 'list':
                for k in range(3):
                    R(d, x + 6, y + 6 + k * 5, 18, 2, (250, 236, 200))
            else:
                R(d, x + 10, y + 5, 12, 18, (140, 100, 70)); d.point((x + 19, y + 14), fill=NEON_Y)
            draw_text(img, x + 16 - text_w(cap) // 2, y + 25, cap, K)
    ex = 'sad' if lt < 13.4 else ('closed' if lt < 19.4 else 'smile')
    arm = 'point' if 14.6 < lt < 18.9 else 'down'
    person(img, 200, 132, 'girl', -1, ex, arm, t, 2, breathe=math.sin(t * 2))
    R(d, 0, 128, W, 8, (96, 58, 40)); R(d, 0, 128, W, 1, (140, 90, 60))
    if 11.4 < lt < 14.4:
        ph = (t * 0.9) % 1
        disc(d, 168 - int(ph * 10), 76, int(2 + ph * 6), (220, 226, 240))
        sfx(img, 150, 60, '哈~', t, t - lt + 11.6, 1.4, 'white', 1)
    hp = seg(lt, 14.6, 18.6)
    if hp > 0 and fog > 0.2:
        pts = []
        for i in range(60):
            a = i / 59 * 2 * math.pi
            pts.append((150 + 16 * math.sin(a) ** 3 * 1.3, 52 - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * 1.3))
        n = int(hp * 60)
        for a_, b_ in zip(pts[:n], pts[1:n + 1]):
            d.line([a_, b_], fill=(255, 150, 190), width=3)
    # 猫咪走过来蹭她
    cx_ = int(lerp(-20, 160, ease(seg(lt, 9.0, 12.0))))
    cat(img, cx_, 129, t, 'walk' if lt < 12 else 'sit', 'happy' if lt > 15 else 'normal', 1, 2, hearts=lt > 15)
    if lt > 19.4:
        sfx(img, 230, 70, '♥', t, t - lt + 19.4, 9, 'pink', 2)


def s_outro(img, t, lt, v):
    rk = 1 - seg(lt, 2, 11)
    dawn = seg(lt, 9, 16)
    street(img, t, False, scroll=t * 30 if lt < 15 else (211 + 15) * 30, rain_k=rk)
    if dawn > 0:
        a = np.asarray(img).astype(float)
        top = np.array([255, 170, 150.]); bot = np.array([255, 220, 160.])
        g = np.linspace(0, 1, 110)[:, None, None]
        sky = top * (1 - g) + bot * g
        a[:110] = a[:110] * (1 - dawn * 0.75) + sky * dawn * 0.75
        img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
        sun(img, 60, int(90 - dawn * 50), 11, 'happy', t)
        rainbow(img, 240, 122, 58, seg(lt, 12, 15))
    else:
        sky_moon(img, 'sleep')
    lamp(img, 290, 128, 'happy', dawn < 0.5, 76)
    um = PINK if lt < 10 else None
    walking = lt < 15
    arm = 'umbrella' if um else ('wave' if 13 < lt < 18 else 'down')
    ex = 'closed' if lt < 10 else 'happy'
    person(img, 150, 128, 'girl', 1, ex, arm, t, 2, walk=walking, umbrella=um, breathe=math.sin(t * 1.6) * 1.5)
    cat(img, 112, 128, t, 'walk' if walking else 'sit', 'happy', 1, 1, hearts=lt > 15)
    if lt > 11:
        sfx(img, 176, 30, '雨停了', t, t - lt + 11, 5, 'cyan', 2)
    if lt > 16:
        sfx(img, 190, 60, '呼~', t, t - lt + 16, 3, 'white', 1)


def s_end(img, t, lt, v):
    room(img, t)
    a = np.asarray(img).astype(float) * 0.45
    img.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    cat(img, 264, 140, t, 'up', 'happy', -1, 2, sign='谢谢收看')


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

# 回放段的弹幕（相对镜头开始的秒数）
DANMU = {
    s_now: [(0.2, '前方高能', (255, 230, 120)), (0.9, '姐姐好飒', WHITE), (1.8, '闹钟：我好难', (150, 220, 255))],
    s_confess: [(0.3, '坦白从宽!', WHITE), (1.2, '同时约三个??', (255, 150, 150)), (2.4, '渣男实锤', (255, 230, 120)), (3.3, '警猫上岗', (150, 220, 255))],
    s_letter: [(0.2, '先别心软', WHITE), (1.3, '猫猫:准了', (255, 230, 120))],
    s_likeme: [(0.3, '整栋楼都在比心', (255, 180, 210)), (1.5, '哈哈哈哈哈', WHITE), (2.6, '月亮都脸红了', (255, 230, 120))],
    s_dream: [(0.4, '恋爱脑上线', (255, 180, 210)), (1.6, '清醒一点!!', WHITE)],
}


def shot_at(t):
    cur = 0
    for i, s in enumerate(SHOTS):
        if t >= s[0]:
            cur = i
    return cur


def compose(t, i):
    t0, fn, v = SHOTS[i]
    img = Image.new('RGB', (W, H), INK)
    fn(img, t, t - t0, v)
    if v == 'replay':
        a = np.asarray(img).astype(float)
        g = a.mean(2, keepdims=True)
        a = a * 0.55 + g * 0.45
        a[:, :, 2] = a[:, :, 2] * 1.08 + 8
        a[::3] *= 0.85
        img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
        danmaku(img, t - t0, DANMU.get(fn, []), y0=30, rows=3, speed=90)
    return img


def frame(t):
    i = shot_at(t)
    img = compose(t, i)
    t0 = SHOTS[i][0]
    if i > 0 and t - t0 < 0.16:
        prev = compose(t, i - 1)
        k = (t - t0) / 0.16
        m = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < k
        img = Image.fromarray(np.where(m[:, :, None], np.asarray(img), np.asarray(prev)).astype(np.uint8))
    big = img.resize((Z.FW, Z.FH), Image.NEAREST)
    mv2.overlay_hi(big, t, 0 if SHOTS[i][2] != 'replay' else _replay_idx())
    return big


def _replay_idx():
    return next(k for k, s in enumerate(mv2.SHOTS) if s[2] == 'replay')
