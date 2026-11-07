"""温馨治愈风综艺花字渲染：生成 RGBA 叠加帧，经管道交给 ffmpeg 合成。"""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1280, 720, 30
FD = "/tmp/claude-0/-home-user-Dario-Claude-home/ca684931-2b58-5e52-900a-18cb1b1b1c67/scratchpad/fonts/"
CUTE = FD + "ZCOOLKuaiLe-Regular.ttf"
BRUSH = FD + "MaShanZheng-Regular.ttf"

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def hexc(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)

# ---------- sprite 生成 ----------
def add_shadow(img, blur=6, off=(0, 4), color=(60, 30, 10), op=0.55, pad=20):
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * op))
    sh = Image.new("RGBA", img.size, color + (0,))
    sh.putalpha(a)
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(sh, (pad + off[0], pad + off[1]))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(layer)
    out.alpha_composite(img, (pad, pad))
    return out

def glyph(ch, style, size):
    """单字 sprite（中心对齐用），返回 (img, advance)。"""
    if style == "warm":       # 奶油渐变填充 + 白描边 + 暖棕外描边
        f = font(CUTE, size); o1, o2 = int(size * .17), int(size * .08)
        fill_top, fill_bot, inner, outer = "#fffbe8", "#ffc766", "#ffffff", "#8a4618"
    elif style == "warm2":    # 粉橘版本
        f = font(CUTE, size); o1, o2 = int(size * .17), int(size * .08)
        fill_top, fill_bot, inner, outer = "#ffffff", "#ffb3a0", "#ffffff", "#a8432e"
    elif style == "poem":     # 毛笔字：白字 + 柔光
        f = font(BRUSH, size); o1, o2 = max(3, int(size * .05)), 0
        fill_top, fill_bot, inner, outer = "#fffdf6", "#ffe9c7", None, "#3a2210"
    pad = o1 + 6
    bb = f.getbbox(ch)
    adv = f.getlength(ch)
    cw, chh = int(adv) + pad * 2, int(size * 1.25) + pad * 2
    img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    org = (pad, pad)
    d = ImageDraw.Draw(img)
    if outer:
        d.text(org, ch, font=f, fill=hexc(outer), stroke_width=o1, stroke_fill=hexc(outer))
        if inner: d.text(org, ch, font=f, fill=hexc(inner), stroke_width=o2, stroke_fill=hexc(inner))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(org, ch, font=f, fill=255)
    grad = Image.new("RGBA", img.size)
    gd = ImageDraw.Draw(grad)
    t0, t1 = hexc(fill_top), hexc(fill_bot)
    y0, y1 = pad + bb[1], pad + bb[3]
    for y in range(img.size[1]):
        k = min(max((y - y0) / max(1, y1 - y0), 0), 1)
        gd.line([(0, y), (img.size[0], y)], fill=tuple(int(t0[i] + (t1[i] - t0[i]) * k) for i in range(4)))
    img.paste(grad, (0, 0), mask)
    if style == "poem":
        img = add_shadow(img, blur=8, off=(0, 3), color=(40, 20, 5), op=0.85, pad=24)
    else:
        img = add_shadow(img, blur=5, off=(0, 5), color=(70, 30, 5), op=0.5, pad=16)
    return img, adv

def pill(text, size=30, bg="#f39a4a", fg="#ffffff", border="#ffffff"):
    f = font(CUTE, size)
    tw = int(f.getlength(text)); px, py = int(size * .7), int(size * .38)
    w, h = tw + px * 2, int(size * 1.2) + py * 2
    img = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, w + 4, h + 4], radius=h // 2, fill=hexc(bg), outline=hexc(border), width=4)
    d.text((4 + px, 4 + py - int(size * .05)), text, font=f, fill=hexc(fg))
    return add_shadow(img, blur=5, off=(0, 4), op=0.4)

def sparkle(r=22, color="#fff3b0"):
    s = r * 2 + 12
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(img); c = s / 2
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * .28
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=hexc(color), outline=hexc("#ffffff"))
    return add_shadow(img, blur=4, off=(0, 0), color=(255, 200, 80), op=0.9, pad=10)

def heart(r=22, color="#ff8f8f"):
    s = r * 3
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((s / 2 + x * r / 16, s / 2 + y * r / 16))
    d.polygon(pts, fill=hexc(color))
    d.line(pts + [pts[0]], fill=hexc("#ffffff"), width=4)
    return add_shadow(img, blur=4, off=(0, 3), op=0.4)

def sun(r=30):
    s = r * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(img); c = s / 2
    for i in range(10):
        a = 2 * math.pi * i / 10
        d.line([(c + r * 1.35 * math.cos(a), c + r * 1.35 * math.sin(a)),
                (c + r * 1.85 * math.cos(a), c + r * 1.85 * math.sin(a))], fill=hexc("#ffb43c"), width=7)
    d.ellipse([c - r, c - r, c + r, c + r], fill=hexc("#ffd35a"), outline=hexc("#ffffff"), width=5)
    # 笑脸
    d.arc([c - r * .45, c - r * .2, c + r * .45, c + r * .5], 20, 160, fill=hexc("#8a4618"), width=4)
    d.ellipse([c - r * .4, c - r * .3, c - r * .22, c - r * .1], fill=hexc("#8a4618"))
    d.ellipse([c + r * .22, c - r * .3, c + r * .4, c - r * .1], fill=hexc("#8a4618"))
    return add_shadow(img, blur=5, off=(0, 3), op=0.35)

def bubble(text, size=40):
    f = font(CUTE, size)
    tw = int(f.getlength(text)); w, h = tw + size, int(size * 1.7)
    img = Image.new("RGBA", (w + 30, h + 34), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, w + 6, h + 6], radius=h // 2, fill=hexc("#ffffff"), outline=hexc("#8a4618"), width=4)
    d.polygon([(w * .3, h + 2), (w * .22, h + 28), (w * .45, h + 2)], fill=hexc("#ffffff"))
    d.line([(w * .3, h + 6), (w * .22, h + 28), (w * .45, h + 6)], fill=hexc("#8a4618"), width=4)
    d.text((6 + size / 2, 6 + size * .3), text, font=f, fill=hexc("#8a4618"))
    return add_shadow(img, blur=4, off=(0, 3), op=0.35)

# ---------- 动画 ----------
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def back(x, s=1.3):
    x = clamp(x); x -= 1
    return x * x * ((s + 1) * x + s) + 1
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3

class Sprite:
    """一个独立元素：t0~t1 出现，pop/fade 入场，轻微漂浮，淡出。"""
    def __init__(self, img, cx, cy, t0, t1, mode="pop", rot=0, float_amp=3, spin=0, twinkle=False):
        self.img, self.cx, self.cy, self.t0, self.t1 = img, cx, cy, t0, t1
        self.mode, self.rot, self.fa, self.spin, self.tw = mode, rot, float_amp, spin, twinkle
    def draw(self, frame, t):
        if t < self.t0 or t > self.t1: return
        lt = t - self.t0
        out = clamp((self.t1 - t) / 0.4)
        if self.mode == "pop":
            sc = back(lt / 0.55); al = ease(lt / 0.3) * out
        elif self.mode == "fade":
            sc = 0.95 + 0.05 * ease(lt / 1.0); al = ease(lt / 0.9) * out
        elif self.mode == "drop":
            sc = 1; al = clamp(lt / 0.15) * out
        sc *= 1 - 0.06 * (1 - out)
        if self.tw: sc *= 1 + 0.12 * math.sin(lt * 3.5)
        dy = self.fa * math.sin(lt * 1.4 + self.cx * .01)
        if self.mode == "drop": dy += -40 * (1 - back(lt / 0.4, 1.8))
        if sc <= 0.02 or al <= 0.01: return
        im = self.img
        w, h = max(1, int(im.width * sc)), max(1, int(im.height * sc))
        if (w, h) != im.size: im = im.resize((w, h), Image.BICUBIC)
        r = self.rot + self.spin * lt
        if r: im = im.rotate(r, resample=Image.BICUBIC, expand=True)
        if al < 1:
            a = im.getchannel("A").point(lambda v: int(v * al)); im = im.copy(); im.putalpha(a)
        x, y = int(self.cx - im.width / 2), int(self.cy + dy - im.height / 2)
        frame.alpha_composite(im, (x, y)) if 0 <= x and 0 <= y and x + im.width <= W and y + im.height <= H \
            else paste_clip(frame, im, x, y)

def paste_clip(frame, im, x, y):
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(im.width, W - x), min(im.height, H - y)
    if ex <= sx or ey <= sy: return
    frame.alpha_composite(im.crop((sx, sy, ex, ey)), (x + sx, y + sy))

def line(text, style, size, x, y, t0, t1, stagger=0.12, mode="pop", align="left", rot=0):
    """逐字入场的一行花字；x 为左端（align=left）或中心。"""
    gl = [glyph(c, style, size) for c in text]
    total = sum(a for _, a in gl)
    cur = x - total / 2 if align == "center" else x
    out = []
    for i, (img, adv) in enumerate(gl):
        cx = cur + adv / 2
        if text[i] != " ":
            out.append(Sprite(img, cx, y, t0 + i * stagger, t1, mode=mode, rot=rot,
                              float_amp=2.5 if style != "poem" else 1.2))
        cur += adv
    return out

# ---------- 慢节奏剪辑结构 ----------
SPEED = 0.6                    # 画面放慢到 0.6 倍（minterpolate 补帧后的 slow.mp4）
# slow.mp4 中检测到的镜头切点
CUTS = [0, 2.7, 5.8333, 6.8667, 10.0, 11.0333, 15.2, 17.2667, 19.3667, 22.5, 23.5333, 26.6667, 33.5, 35.0333, 38.4667]
# XF[i]：镜头 i 与 i+1 之间的叠化时长；0 = 保留硬切（两段羊群连着走）
XF = [0.5, 0, 0.4, 0.3, 0.3, 0.6, 0.5, 0.5, 0.3, 0.3, 0.7, 0.4, 0.5]
N = len(CUTS) - 1
D = [CUTS[i + 1] - CUTS[i] for i in range(N)]
S = [0.0]
for i in range(N - 1):
    S.append(S[-1] + D[i] - XF[i])
DUR = S[-1] + D[-1]
FADE_IN, FADE_OUT = 0.8, 1.5

def win(i, j=None):
    """镜头 i（到 j）在成片中的完整可见区间（不含与前后镜头的叠化段）。"""
    j = i if j is None else j
    a = S[i] + (XF[i - 1] if i > 0 else FADE_IN * 0.5)
    b = S[j] + D[j] - (XF[j] if j < N - 1 else FADE_OUT * 0.6)
    return a, b

E = []
def at(i, off, j=None, early=False):
    """元素起止：可见区起点+off（early=True 则从入场叠化开始），终点顺延到下一次叠化的大半段。"""
    j = i if j is None else j
    a, b = win(i, j)
    if early and i > 0: a = S[i]
    tail = XF[j] * 0.8 if j < N - 1 else 0
    return a + off, b + tail

E.append(Sprite(pill("高原慢日子", 24, bg="#c8763a"), 1180, 44, 0.8, DUR - FADE_OUT, mode="fade", float_amp=0))

# 0 奶奶侧脸
t0, t1 = at(0, 0.2)
E += line("皱纹里", "warm", 66, 860, 190, t0, t1)
E += line("住着太阳", "warm", 66, 900, 285, t0 + 0.6, t1)
E.append(Sprite(sun(26), 1170, 175, t0 + 1.0, t1, spin=15))
# 1-2 羊群出门（两段连着）
t0, t1 = at(1, 0.2, 2)
E += line("羊羊出门上班啦", "warm2", 58, 90, 120, t0, t1, stagger=0.1)
E.append(Sprite(bubble("咩～", 34), 980, 330, t0 + 1.3, S[2] - 0.05, rot=6))
E.append(Sprite(bubble("咩咩！", 34), 330, 520, t0 + 1.9, S[2], rot=-5))
E.append(Sprite(bubble("等等我～", 34), 1000, 520, S[2] - 0.3, t1, rot=4))
# 3 倚墙的男孩
t0, t1 = at(3, 0.15)
E += line("晒暖暖的", "warm", 60, 760, 470, t0, t1)
E += line("小朋友", "warm", 60, 840, 560, t0 + 0.6, t1)
E.append(Sprite(pill("嘴角偷偷上扬中", 28, bg="#ff9c8a"), 1010, 370, t0 + 1.3, t1, rot=-4))
E.append(Sprite(sparkle(20), 740, 300, t0 + 1.5, t1, twinkle=True))
E.append(Sprite(sparkle(13), 775, 350, t0 + 1.7, t1, twinkle=True))
# 4 门帘
t0, t1 = at(4, 0.05, early=True)
E += line("风  路过", "poem", 70, 560, 80, t0, t1, stagger=0.1, mode="fade")
# 5 村里的羊群
t0, t1 = at(5, 0.15)
E += line("这里的早高峰", "warm", 56, 640, 95, t0, t1, align="center", stagger=0.1)
E += line("属于咩咩", "warm2", 64, 640, 180, t0 + 0.9, t1, align="center")
E.append(Sprite(pill("慢慢走 不着急", 28, bg="#8fb86a"), 1090, 300, t0 + 2.0, t1, rot=5))
# 6 抚摸青稞
t0, t1 = at(6, 0.1)
E += line("青稞", "poem", 82, 860, 150, t0, t1, mode="fade")
E += line("沉甸甸的", "poem", 62, 900, 245, t0 + 0.4, t1, mode="fade")
E.append(Sprite(pill("今年丰收啦", 28, bg="#e7a73a"), 245, 640, t0 + 0.8, t1, rot=-4))
# 7 溪水
t0, t1 = at(7, 0.1)
E += line("雪山的水", "poem", 64, 640, 140, t0, t1, align="center", mode="fade", stagger=0.14)
E += line("慢慢流", "poem", 64, 640, 225, t0 + 0.6, t1, align="center", mode="fade", stagger=0.14)
# 8 闭眼晒太阳的老人
t0, t1 = at(8, 0.2)
E += line("什么都不想", "warm", 58, 690, 180, t0, t1)
E += line("就很好", "warm", 66, 780, 275, t0 + 0.9, t1)
E.append(Sprite(pill("晒太阳充电中", 28, bg="#f39a4a"), 290, 90, t0 + 1.4, t1, rot=-3))
E.append(Sprite(sun(22), 470, 90, t0 + 1.6, t1, spin=18))
# 9 倒酥油茶
t0, t1 = at(9, 0.05, early=True)
E.append(Sprite(pill("酥油茶 续上！", 34, bg="#d0643c"), 260, 110, t0, t1, rot=-5))
E.append(Sprite(heart(16), 740, 420, t0 + 0.3, t1))
# 10 中年男人
t0, t1 = at(10, 0.2)
E += line("守着这片土地", "poem", 62, 780, 200, t0, t1, mode="fade", stagger=0.14)
E += line("的人", "poem", 62, 1000, 290, t0 + 1.0, t1, mode="fade")
# 11 山坡羊群全景
t0, t1 = at(11, 0.3)
E += line("日子慢慢", "poem", 96, 640, 170, t0, t1, align="center", mode="fade", stagger=0.25)
E += line("岁月长长", "poem", 96, 700, 290, t0 + 1.6, t1, align="center", mode="fade", stagger=0.25)
for k, (x, y, r) in enumerate([(380, 120, 16), (980, 160, 20), (930, 330, 12), (430, 300, 12)]):
    E.append(Sprite(sparkle(r), x, y, t0 + 3.2 + k * 0.4, t1, twinkle=True))
# 12 小羊特写
t0, t1 = at(12, 0.05, early=True)
E += line("咩？", "warm2", 110, 1010, 200, t0, t1, stagger=0.15)
E.append(Sprite(bubble("今天也很开心", 30), 1010, 380, t0 + 0.5, t1, rot=4))
# 13 男孩特写（片尾）
t0, _ = at(13, 0.2); t1 = DUR - 0.3
E += line("愿你也被阳光", "warm", 54, 1065, 470, t0, t1, align="center", stagger=0.1)
E += line("温柔以待", "warm2", 70, 1065, 565, t0 + 0.9, t1, align="center", stagger=0.14)
E.append(Sprite(heart(18), 1200, 640, t0 + 1.8, t1))
E.append(Sprite(heart(13), 1235, 600, t0 + 2.0, t1, rot=15))
E.append(Sprite(sparkle(16), 905, 400, t0 + 1.9, t1, twinkle=True))

# ---------- 合成 ----------
def base_filter():
    """slow.mp4 -> 切段 -> 叠化/硬切串联 -> 首尾淡入淡出。"""
    parts = [f"[0:v]trim={CUTS[i]}:{CUTS[i+1]},setpts=PTS-STARTPTS,fps=30,settb=AVTB,format=yuv420p[s{i}]" for i in range(N)]
    cur, acc = "s0", D[0]
    for i in range(1, N):
        out = f"c{i}"
        if XF[i - 1] == 0:
            parts.append(f"[{cur}][s{i}]concat=n=2:v=1:a=0[{out}]")
        else:
            parts.append(f"[{cur}][s{i}]xfade=transition=fade:duration={XF[i-1]}:offset={acc - XF[i-1]:.4f}[{out}]")
        acc += D[i] - XF[i - 1]; cur = out
    parts.append(f"[{cur}]fade=t=in:st=0:d={FADE_IN},fade=t=out:st={DUR - FADE_OUT:.4f}:d={FADE_OUT}[base]")
    return ";".join(parts)

def render(slow, audio_src, dst, preview_times=None):
    tempo = 23.1333 / DUR
    if preview_times:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", slow, "-filter_complex", base_filter(),
                        "-map", "[base]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "base.mp4"], check=True)
        for t in preview_times:
            fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for e in E: e.draw(fr, t)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", "base.mp4", "-frames:v", "1", "bg.png"], check=True)
            bg = Image.open("bg.png").convert("RGBA"); bg.alpha_composite(fr)
            bg.convert("RGB").save(f"prev_{t:05.2f}.jpg", quality=88)
        return
    n = int(DUR * FPS)
    fc = base_filter() + ";[base][1:v]overlay=0:0:format=auto,format=yuv420p[v]" + \
         f";[2:a]atempo={tempo:.5f},afade=t=in:st=0:d=0.5,afade=t=out:st={DUR - 2.0:.3f}:d=2.0,atrim=0:{DUR:.3f}[a]"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", slow,
                          "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", audio_src, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                          "-movflags", "+faststart", "-t", f"{DUR:.3f}", dst], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for e in E: e.draw(fr, t)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    print("done", p.returncode, "duration", round(DUR, 2), "tempo", round(tempo, 4))

if __name__ == "__main__":
    # 用法：preview slow.mp4 t1 t2 ... | render slow.mp4 原视频(取音轨) 输出.mp4
    if sys.argv[1] == "preview":
        render(sys.argv[2], None, None, [float(x) for x in sys.argv[3:]])
    else:
        render(sys.argv[2], sys.argv[3], sys.argv[4])
