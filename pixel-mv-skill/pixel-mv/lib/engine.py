"""像素综艺 MV 引擎：读项目数据（project.json / lyrics.txt / audio.json），管理镜头表、歌词花字、片头片尾、回放效果、署名，输出 1920×1080 帧。

项目里的 mv.py 只需要：写镜头函数 fn(img, t, lt, v) → 组镜头表 SHOTS → 写每句花字配置 CFG → mv = MV(ROOT, SHOTS, CFG, ...) → frame = mv.frame
  - img：320×180 原生画布；t：全片秒；lt：本镜头开始后的秒（所有动作都按 lt 编排，重复段直接复用）
  - v：False 普通 / 'replay' 回放（褪色+扫描线+弹幕+“回放”标签）/ True 第二套配色（场景自己读 v is True 换色）
"""
import json, math, os
import numpy as np
from PIL import Image
from pixlib import W, H, INK, BAYER, seg
import huazi as Z


class Song:
    def __init__(self, root):
        self.root = root
        self.p = json.load(open(os.path.join(root, 'project.json'), encoding='utf-8'))
        self.lines = []
        for raw in open(os.path.join(root, 'tools', 'lyrics.txt'), encoding='utf-8'):
            if raw.startswith('#') or not raw.strip():
                continue
            a, b, s = [x.strip() for x in raw.split('|', 2)]
            self.lines.append((float(a), float(b), s))
        self.LS = [a for a, b, s in self.lines]
        au = json.load(open(os.path.join(root, 'tools', 'audio.json')))
        self.beats = np.array(au['beats'])
        self.rms_ = au['rms']
        self.dur = float(self.p.get('duration') or au['dur'])

    def rms(self, t):
        i = int(t * 30)
        return self.rms_[i] if 0 <= i < len(self.rms_) else 0.0

    def beat_phase(self, t):
        i = np.searchsorted(self.beats, t) - 1
        return t - self.beats[i] if i >= 0 else 9.0

    def pump(self, t, k=1.0):
        return math.exp(-self.beat_phase(t) * 7) * k

    def L(self, i, pre=0.12):
        """第 i 句（从 0 数）开唱前 pre 秒，用作镜头开始时刻"""
        return self.LS[i] - pre


DEFAULT_STYLE = dict(pal='white', kwpal='pink')  # 其余默认见 huazi.Line：size=120, cy=830


def build_lyrics(song, cfg, base=None):
    """cfg：列表（按句序）或 dict（键为句序号，或直接用歌词原文——重复的句子自动共用一套样式），每项是 Z.Line 的参数；kw 可配 kwpal 为列表实现多组重点词各自换色。"""
    out = []
    for i, (a, b, s) in enumerate(song.lines):
        c = dict(DEFAULT_STYLE)
        c.update(base or {})
        c.update((cfg[i] if isinstance(cfg, list) else (cfg.get(i) or cfg.get(s, {}))) or {})
        nxt = song.lines[i + 1][0] if i + 1 < len(song.lines) else b + 2
        b = min(b, nxt - 0.05)
        kw = c.pop('kw', None)
        kwpal = c.pop('kwpal', 'pink')
        L = Z.Line(a, b, s, kw=kw, kwpal=kwpal if isinstance(kwpal, str) else kwpal[0], **c)
        if kw and not isinstance(kwpal, str):
            flat = s.replace('/', '')
            for w, p in zip(kw, kwpal):
                pos = flat.find(w)
                for it in L.items:
                    if pos <= it['i'] < pos + len(w):
                        it['pal'] = p
        out.append(L)
    return out


class MV:
    def __init__(self, song, shots, cfg, danmu=None, title_style=None, replay_label='回放 REPLAY', tag='像素 MV', lyric_base=None):
        """lyric_base：全曲歌词花字的基调（按曲风定），如 dict(pop=1.08, stagger=0.09, float_amp=3) 抒情、dict(pop=1.45, stagger=0.03, shake=5) 燃。
        title_style：片头片尾歌名的样式（pal/size/angle/deco/pop…）。"""
        self.song = song
        self.shots = shots
        self.lyrics = build_lyrics(song, cfg, lyric_base)
        self.danmu = danmu or {}
        p = song.p
        self.title_end = float(p.get('title_end', 9.6))
        self.end_start = float(p.get('end_start', song.dur - 10))
        ts = dict(pal='pink', size=230, cx=960, cy=400, angle=-3, deco=('heart', 'star', 'note'))
        ts.update(title_style or {})
        self.TITLE = Z.Line(-2.0, self.title_end - 0.4, p['title'], stagger=0.0, **ts)
        te = dict(ts); te['size'] = int(ts['size'] * 0.87)
        self.END = Z.Line(self.end_start + 0.1, song.dur + 1, p['title'], stagger=0.08, **te)
        self.artist_line = '原唱 · ' + p['artist'] if p.get('artist') else None
        self.tag = p.get('tag', tag)
        self.signature = p.get('signature', '')
        self.replay_label = replay_label

    def shot_at(self, t):
        cur = 0
        for i, s in enumerate(self.shots):
            if t >= s[0]:
                cur = i
        return cur

    def compose(self, t, i):
        from props2 import danmaku
        t0, fn, v = self.shots[i]
        img = Image.new('RGB', (W, H), INK)
        fn(img, t, t - t0, v)
        if v == 'replay':
            a = np.asarray(img).astype(float)
            g = a.mean(2, keepdims=True)
            a = a * 0.55 + g * 0.45
            a[:, :, 2] = a[:, :, 2] * 1.08 + 8
            a[::3] *= 0.85
            img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
            danmaku(img, t - t0, self.danmu.get(fn, []), y0=30, rows=3, speed=90)
        return img

    def frame(self, t):
        i = self.shot_at(t)
        img = self.compose(t, i)
        t0 = self.shots[i][0]
        if i > 0 and t - t0 < 0.16:  # 像素抖动溶解转场
            prev = self.compose(t, i - 1)
            k = (t - t0) / 0.16
            m = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W] < k
            img = Image.fromarray(np.where(m[:, :, None], np.asarray(img), np.asarray(prev)).astype(np.uint8))
        big = img.resize((Z.FW, Z.FH), Image.NEAREST)
        self.overlay(big, t, i)
        return big

    def overlay(self, big, t, i):
        bp = self.song.beat_phase(t)
        te = self.title_end
        if t < te:  # 片头：歌名 + 原唱
            out = seg(t, te - 0.6, te)
            self.TITLE.draw(big, t if t < te - 0.6 else te - 0.6 + out * 0.2, bp)
            if out < 1:
                if self.artist_line:
                    Z.pill(big, 960, 640, self.artist_line, 64, alpha=1 - out)
                if self.tag:
                    Z.pill(big, 960, 760, self.tag, 44, bg=(255, 110, 170), edge=(255, 255, 255), alpha=1 - out)
        if t >= self.end_start:  # 片尾
            k = seg(t, self.end_start, self.end_start + 0.7)
            self.END.draw(big, t, bp)
            if k > 0:
                if self.artist_line:
                    Z.pill(big, 960, 620, self.artist_line, 64, alpha=k)
                Z.pill(big, 960, 740, (self.tag + ' · ' if self.tag else '') + '谢谢收看', 44, bg=(255, 110, 170), edge=(255, 255, 255), alpha=k)
        if self.shots[i][2] == 'replay' and self.replay_label:
            Z.pill(big, 230, 80, self.replay_label, 46, bg=(200, 30, 50), edge=(255, 255, 255))
        for L_ in self.lyrics:
            if L_.t0 - 0.1 <= t <= L_.t1 + 0.1:
                L_.draw(big, t, bp)
        if self.signature:
            s = Z.signature(self.signature)
            big.paste(s, (960 - s.width // 2, Z.FH - s.height - 6), s)
        dur = self.song.dur
        if t > dur - 1.2:
            a = np.asarray(big).astype(float) * (1 - seg(t, dur - 1.2, dur - 0.1))
            big.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
