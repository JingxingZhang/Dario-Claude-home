"""9:16 chalkboard explainer with Edge-TTS (zh-CN-YunjianNeural) voice-over, subtitles and a drawing hand.
usage: python3 vertical.py OUT.mp4        (PREVIEW=1.2,5.0 python3 vertical.py  -> preview PNGs)"""
import os, sys, subprocess, re
os.environ.setdefault("CHALK_W", "1080"); os.environ.setdefault("CHALK_H", "1920")
# chalk lettering: 演示夏行楷 (Slidexiaxing, free for commercial use) — tiny ink, wide advance, so scale + tighten
os.environ.setdefault("CHALK_FONT", "fonts/YanShiXiaXingKai.ttf")
os.environ.setdefault("CHALK_FONT_SCALE", "1.22"); os.environ.setdefault("CHALK_TRACK", "0.72")
SHOW_HAND = os.environ.get("HAND") == "1"     # drawn hand is off by default (bare chalk stick instead)
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage
from multiprocessing import Pool
import render as R
from hand import make_hand

W, H, FPS = R.W, R.H, R.FPS
HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, "vo")  # fill with: python3 tts.py vo/lN.mp3 "<line N of lines.txt>" +12%
LINES = [l.strip() for l in open(os.path.join(HERE, "lines.txt"), encoding="utf-8") if l.strip()]
WHITE, YELLOW, BLUE, PINK, ORANGE = R.WHITE, R.YELLOW, R.BLUE, R.PINK, R.ORANGE
HAND_SCALE = 0.78
GAP, ERASE_GAP, INTRO, OUTRO = 0.35, 3.2, 0.5, 1.8

# ------------------------------------------------------------- narration timing
def load_words(i):
    rows = []
    for ln in open(os.path.join(VO, f"l{i}.mp3.words.tsv"), encoding="utf-8"):
        o, d, t = ln.rstrip("\n").split("\t")
        rows.append((float(o), float(d), t))
    return rows

WORDS = [load_words(i + 1) for i in range(len(LINES))]
STARTS, ENDS = [], []
t = INTRO
for i, w in enumerate(WORDS):
    span = w[-1][0] + w[-1][1] - w[0][0]
    STARTS.append(t); ENDS.append(t + span)
    t = t + span + (ERASE_GAP if i == 5 else GAP)
DUR = ENDS[-1] + OUTRO
NF = int(round(DUR * FPS))

def window(i):
    t1 = STARTS[i + 1] - 0.1 if i + 1 < len(STARTS) else ENDS[i] + 0.8
    if i == 5: t1 = ENDS[i] + 0.25
    return STARTS[i], t1

def seq(i, items):
    """items: list of (weight, factory(t0,t1)) spread across narration line i's window"""
    t0, t1 = window(i)
    tot = sum(w for w, _ in items)
    out, t = [], t0
    for w, f in items:
        d = (t1 - t0) * w / tot
        out.append(f(t, t + d - 0.06))
        t += d
    return out

# subtitles: split line at punctuation, time each phrase from word boundaries
PUNCT = "，。；：？！、,.;:?!"
def subtitle_chunks(i):
    text = LINES[i]
    phrases = [p for p in re.split(f"[{PUNCT}]", text) if p.strip()]
    words = WORDS[i]
    base = words[0][0]
    # char index (punctuation stripped) -> time
    times, k = [], 0
    for o, d, wt in words:
        for _ in wt:
            times.append(o - base)
    chunks, pos = [], 0
    for p in phrases:
        idx = min(pos, len(times) - 1)
        chunks.append([STARTS[i] + times[idx], p])
        pos += len(p)
    # merge short neighbours (<= 15 chars)
    merged = []
    for st, p in chunks:
        if merged and len(merged[-1][1]) + len(p) <= 13:
            merged[-1][1] += "，" + p
        else:
            merged.append([st, p])
    out = []
    for j, (st, p) in enumerate(merged):
        en = merged[j + 1][0] if j + 1 < len(merged) else ENDS[i] + 0.15
        out.append((st - 0.05, en, p))
    return out

# ------------------------------------------------------------- scene
def build():
    rng = R.rng
    E = []
    T = lambda *a, **k: (lambda t0, t1: R.text_element(*a, t0, t1, **k))
    S = lambda paths, col, **k: (lambda t0, t1: R.stroke_element(paths, col, t0, t1, **k))
    # 1 title
    E += seq(0, [(3, T("为什么天空是蓝色？", W / 2, 210, 92, WHITE, anchor="c", density=0.62)),
                 (1, S([R.wave_pts(160, 920, 288, 240, 4)], YELLOW, width=6))])
    # 2 sun
    sc, sr = (200, 480), 60
    rays = []
    for k in range(12):
        a = k / 12 * 2 * np.pi
        rays.append([(sc[0] + (sr + 15) * np.cos(a), sc[1] + (sr + 15) * np.sin(a)),
                     (sc[0] + (sr + 40) * np.cos(a), sc[1] + (sr + 40) * np.sin(a))])
    A = seq(1, [(1, S([R.circle_pts(*sc, sr)], YELLOW, width=8)), (1, S(rays, YELLOW, width=6)),
                (2, T("太阳光 = 七色混合", 330, 480, 54, WHITE))])
    # 3 blue / 4 red
    A += seq(2, [(2, S([R.wave_pts(90, 990, 690, 40, 20)], BLUE, width=7)),
                 (2, T("蓝光：波长短 ~450nm", W / 2, 785, 54, BLUE, anchor="c"))])
    A += seq(3, [(2, S([R.wave_pts(90, 990, 930, 115, 26)], PINK, width=7)),
                 (2, T("红光：波长长 ~700nm", W / 2, 1025, 54, PINK, anchor="c"))])
    # 5 formula / 6 ratio
    A += seq(4, [(3, T("散射强度 ∝ 1/λ^4", W / 2, 1245, 96, WHITE, anchor="c", density=0.64)),
                 (1, S([[(118, 1152), (962, 1147), (966, 1338), (114, 1342), (120, 1148)]], YELLOW, width=6))])
    A += seq(5, [(0.7, S(R.arrow_paths((540, 1372), (540, 1468)), WHITE, width=6)),
                 (2, T("蓝光散射 ≈ 红光的 5.9 倍", W / 2, 1545, 58, YELLOW, anchor="c")),
                 (1.4, T("(700÷450)^4 ≈ 5.9", W / 2, 1630, 46, WHITE, anchor="c"))])
    er = R.Eraser(160, 340, W - 160, 1690, ENDS[5] + 0.3, STARTS[6] - 0.25, bw=230, bh=120)
    for e in A: e.eraser = er
    E += A
    # 7 day panel
    GY = 960
    def person(px, gy):
        return [R.circle_pts(px, gy - 66, 15, -90, 270, 60), [(px, gy - 50), (px, gy - 22)],
                [(px - 18, gy - 40), (px, gy - 34), (px + 18, gy - 40)],
                [(px - 14, gy), (px, gy - 22), (px + 14, gy)]]
    dots = []
    while len(dots) < 60:
        px, py = rng.uniform(110, 970), rng.uniform(380, 890)
        if abs(px - 540) < 45 or (abs(px - 540) < 90 and abs(py - 450) < 85) or (px < 300 and py < 430): continue
        dots.append((px, py))
    dots.sort(key=lambda p: abs(p[0] - 540) + 0.3 * abs(p[1] - 650))
    dp = []
    for px, py in dots:
        a = rng.uniform(0, 2 * np.pi); dp.append([(px, py), (px + 7 * np.cos(a), py + 7 * np.sin(a))])
    E += seq(6, [(0.5, T("白天", 90, 385, 62, YELLOW)),
                 (0.6, S([R.circle_pts(540, 450, 44)], YELLOW, width=7)),
                 (0.6, S([[(80, GY), (1000, GY + 3)]], WHITE, width=6)),
                 (0.5, S(person(540, GY), WHITE, width=5)),
                 (0.5, S(R.arrow_paths((540, 505), (540, 860)), WHITE, width=6)),
                 (1.2, S(dp, BLUE, width=7, jitter=0.3)),
                 (1.6, T("光路短：蓝光四处散射 → 满天蓝", W / 2, 1015, 44, BLUE, anchor="c"))])
    # 8 sunset panel
    G2 = 1470
    dash = [[(x, 1085), (x + 34, 1086)] for x in range(90, 990, 56)]
    sc2 = []
    for k in range(14):
        bx = 840 - k * 42 + rng.uniform(-8, 8)
        by = G2 - 80 - rng.uniform(15, 170) * (1 - k / 18)
        sc2.append([(bx, by), (bx + 6, by - 5)])
    long = np.stack([np.linspace(860, 215, 120), G2 - 40 - 6 * np.sin(np.linspace(0, np.pi, 120))], 1)
    E += seq(7, [(0.4, S(dash, WHITE, width=4, density=0.45)),
                 (0.5, T("日落", 90, 1160, 62, ORANGE)),
                 (0.5, S([[(80, G2), (1000, G2 + 3)]], WHITE, width=6)),
                 (0.5, S([R.circle_pts(925, G2, 52, 180, 360, 80)], ORANGE, width=7)),
                 (0.5, S(person(160, G2), WHITE, width=5)),
                 (0.8, S([long, [(237, G2 - 58), (213, G2 - 40), (237, G2 - 22)]], ORANGE, width=6)),
                 (0.7, S(sc2, BLUE, width=7, jitter=0.3)),
                 (1.6, T("光路长：蓝光沿途散尽 → 夕阳橙红", W / 2, 1530, 44, ORANGE, anchor="c"))])
    # 9 conclusion
    E += seq(8, [(3, T("波长越短，散射越强", W / 2, 1655, 70, WHITE, anchor="c", density=0.64)),
                 (1, S([R.wave_pts(240, 840, 1712, 260, 3)], YELLOW, width=5))])
    return E, [er]

# ------------------------------------------------------------- hand path
REST = np.array([W + 420.0, H + 500.0])

def hand_track(E, ERS):
    pos = np.full((NF, 2), np.nan); col = [None] * NF; mode = ["chalk"] * NF
    for f in range(NF):
        t = f / FPS
        act = [e for e in E if e.t0 <= t < e.t1]
        if act:
            e = act[-1]
            pos[f] = e.tip(e.progress(t)); col[f] = tuple(e.color.astype(int))
        for er in ERS:
            if er.t0 <= t < er.t1:
                c = er.pos(er.progress(t))
                pos[f] = c - np.array([73, -55]) * HAND_SCALE + np.array([0, -28]); mode[f] = "eraser"
    # fill gaps
    f = 0
    while f < NF:
        if not np.isnan(pos[f, 0]): f += 1; continue
        g = f
        while g < NF and np.isnan(pos[g, 0]): g += 1
        P = pos[f - 1] if f > 0 else REST
        Q = pos[g] if g < NF else REST
        n = g - f
        nxt_col = col[g] if g < NF else col[f - 1]
        if n > 1.3 * FPS or g == NF or f == 0:
            m = int(0.55 * FPS)
            for k in range(n):
                if f > 0 and k < m: u = R.ease(k / m); pos[f + k] = P + (REST - P) * u
                elif g < NF and k >= n - m: u = R.ease((k - (n - m)) / m); pos[f + k] = REST + (Q - REST) * u
                else: pos[f + k] = REST
                col[f + k] = nxt_col if k > n / 2 else (col[f - 1] if f > 0 else nxt_col)
                mode[f + k] = mode[f - 1] if (f > 0 and k < n / 2) else "chalk"
        else:
            for k in range(n):
                u = R.ease((k + 1) / (n + 1))
                arc = np.array([0, -40]) * np.sin(np.pi * u)   # little lift between strokes
                pos[f + k] = P + (Q - P) * u + arc
                col[f + k] = nxt_col
        f = g
    for f in range(NF):
        if col[f] is None: col[f] = WHITE
    sm = ndimage.gaussian_filter1d(pos, 1.2, axis=0)
    er_f = np.array([m == "eraser" for m in mode])
    sm[er_f] = pos[er_f]          # eraser frames stay locked to the eraser
    return sm, col, mode

# ------------------------------------------------------------- render
G = {}

def sprite(color):
    im, (ax, ay) = make_hand(chalk_color=color, scale=HAND_SCALE, arm=2300) if color else make_hand(chalk_color=None, scale=HAND_SCALE, arm=2300)
    a = np.asarray(im, np.float32) / 255.0
    sh = ndimage.gaussian_filter(a[..., 3], 12 * HAND_SCALE) * 0.38
    return a[..., :3] * 255.0, a[..., 3], sh, (ax, ay)

def init():
    R.BOARD = R.make_board()
    R.DUR = DUR
    E, ERS = build()
    R.ELEMS, R.ERASERS = E, ERS
    al = np.zeros((H, W), np.float32)
    for e in E:
        if e.eraser is None: continue
        h, w = e.alpha.shape
        al[e.y0:e.y0 + h, e.x0:e.x0 + w] = np.maximum(al[e.y0:e.y0 + h, e.x0:e.x0 + w], e.alpha)
    R.RESIDUE = ndimage.gaussian_filter(al, (5, 14)) * 0.12
    G["track"] = hand_track(E, ERS)
    if SHOW_HAND:
        G["sprites"] = {c: sprite(c) for c in set(G["track"][1])}
        G["sprites"]["eraser"] = sprite(None)
    # subtitles
    font = ImageFont.truetype(R.SUB_FONT, 54)
    subs = []
    for i in range(len(LINES)):
        for st, en, txt in subtitle_chunks(i):
            im = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((W / 2, 55), txt, font=font, fill=(255, 255, 255, 255), anchor="mm",
                                    stroke_width=6, stroke_fill=(12, 20, 16, 235))
            a = np.asarray(im, np.float32) / 255.0
            subs.append((st, en, a[..., :3] * 255, a[..., 3]))
    G["subs"] = subs

def blit(img, rgb, a, x, y, shadow=None, sdx=0, sdy=0):
    h, w = a.shape
    for arr, ox, oy, is_sh in ((shadow, x + sdx, y + sdy, True), (a, x, y, False)):
        if arr is None: continue
        x0, y0 = max(0, ox), max(0, oy)
        x1, y1 = min(W, ox + w), min(H, oy + h)
        if x1 <= x0 or y1 <= y0: continue
        sa = arr[y0 - oy:y1 - oy, x0 - ox:x1 - ox][..., None]
        dst = img[y0:y1, x0:x1]
        if is_sh: dst *= (1 - sa)
        else: dst += sa * (rgb[y0 - oy:y1 - oy, x0 - ox:x1 - ox] - dst)

def draw_eraser(img, pos, bw=230, bh=104):
    x, y = pos
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im, "RGBA")
    dr.rounded_rectangle([x - bw / 2 + 14, y - bh / 2 + 18, x + bw / 2 + 14, y + bh / 2 + 18], 12, fill=(0, 0, 0, 80))
    dr.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], 12, fill=(150, 104, 62, 255))
    dr.rounded_rectangle([x - bw / 2 + 7, y - bh / 2 + 7, x + bw / 2 - 7, y + bh / 2 - 30], 8, fill=(178, 128, 80, 255))
    dr.rectangle([x - bw / 2 + 3, y + bh / 2 - 24, x + bw / 2 - 3, y + bh / 2 - 3], fill=(214, 214, 206, 255))
    return np.asarray(im)

def render_frame(fi):
    t = fi / FPS
    img = R.BOARD.copy()
    for er in R.ERASERS:
        ue = er.progress(t)
        if ue > 0:
            m = np.clip((ue - er.rev) * 40, 0, 1)
            img += (R.RESIDUE * m)[..., None] * (np.array([230, 232, 224]) - img)
    for e in R.ELEMS:
        u = e.progress(t)
        if u <= 0: continue
        h, w = e.alpha.shape
        a = e.alpha * np.clip((u - e.reveal) * 60 + 1, 0, 1) if u < 1 else e.alpha * (e.reveal < 5)
        if e.eraser is not None:
            ue = e.eraser.progress(t)
            if ue > 0:
                a = a * (1 - np.clip((ue - e.eraser.rev[e.y0:e.y0 + h, e.x0:e.x0 + w]) * 40, 0, 1))
        sl = img[e.y0:e.y0 + h, e.x0:e.x0 + w]
        sl += a[..., None] * (e.color - sl)
    for er in R.ERASERS:
        ue = er.progress(t)
        if 0 < ue < 1:
            img = draw_eraser(np.clip(img, 0, 255).astype(np.uint8), er.pos(ue)).astype(np.float32)
    pos, col, mode = G["track"]
    if SHOW_HAND:
        key = "eraser" if mode[fi] == "eraser" else col[fi]
        rgb, a, sh, (ax, ay) = G["sprites"][key]
        bob = np.array([np.sin(t * 7.0) * 1.5, np.cos(t * 5.0) * 1.5])
        x, y = (pos[fi] + bob - (ax, ay)).astype(int)
        blit(img, rgb, a, x, y, shadow=sh, sdx=int(26 * HAND_SCALE), sdy=int(34 * HAND_SCALE))
    else:   # comparison version: bare chalk stick, only while writing
        act = [e for e in R.ELEMS if e.t0 <= t < e.t1]
        if act:
            e = act[-1]
            img = R.chalk_stick(np.clip(img, 0, 255).astype(np.uint8), e.tip(e.progress(t)), tuple(e.color)).astype(np.float32)
    for st, en, rgb, a in G["subs"]:
        if st <= t < en:
            fade = min(1, (t - st) / 0.12, (en - t) / 0.12)
            blit(img, rgb, a * fade, 0, H - 205)
    return np.clip(img, 0, 255).astype(np.uint8).tobytes()

# ------------------------------------------------------------- audio
def decode(path, sr=48000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def make_audio(path):
    import wave
    sfx_path = path + ".sfx.wav"
    R.make_audio(sfx_path)
    with wave.open(sfx_path) as wv:
        sfx = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    SR = 48000
    voice = np.zeros(len(sfx), np.float32)
    for i in range(len(LINES)):
        v = decode(os.path.join(VO, f"l{i + 1}.mp3"))
        s0 = int((STARTS[i] - WORDS[i][0][0]) * SR)
        n = min(len(v), len(voice) - s0)
        voice[s0:s0 + n] += v[:n]
    voice = voice / max(1e-6, np.abs(voice).max()) * 0.92
    mix = voice[:, None] + sfx * 0.22
    mix = mix / max(1.0, np.abs(mix).max() / 0.97)
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
        wv.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "chalkboard_vertical.mp4")
    print(f"duration {DUR:.2f}s, {NF} frames")
    init()
    if os.environ.get("PREVIEW"):
        for ts in os.environ["PREVIEW"].split(","):
            Image.frombytes("RGB", (W, H), render_frame(int(float(ts) * FPS))).save(os.path.join(HERE, f"v_{ts}.png"))
        sys.exit()
    wav = os.path.join(HERE, "vertical_mix.wav")
    make_audio(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(NF), chunksize=4)):
            ff.stdin.write(fr)
            if k % 150 == 0: print("frame", k, flush=True)
    ff.stdin.close(); ff.wait()
    print("done", out)
