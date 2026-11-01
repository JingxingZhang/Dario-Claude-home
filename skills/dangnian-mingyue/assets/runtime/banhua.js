// 当年明月 · 版画套色 MV 引擎（BH）
// 画面 = 纸 + 靛版 + 朱版 + 墨版，三版正片叠底、轻微错版；每个“元素”只印一次（半调网点 + 印刷质感），之后逐帧只做变换与合成。
// 约定（scripts/lib/film.js、render.js、still.js、check.js 只认这些）：
//   window.__timelines.film = { duration(), time(t, suppress) }   time() 同步画好那一帧
//   window.__mr.ready()      字体就绪（mr.js 提供）
//   window.__bh.report(t)    这一刻的镜头、元素外框、主题栏、字幕（check.js 用）
//   window.__bh.shots()      镜头表（lyrics_md.py 用）
// 一切确定：随机数有种子；动画写在 GSAP 时间线上，逐帧 seek。
(function () {
  // 画布尺寸读 <html data-w data-h>（封面 3:4 用 1080×1440）；默认 16:9 1920×1080
  const W = Number(document.documentElement.getAttribute('data-w')) || 1920, H = Number(document.documentElement.getAttribute('data-h')) || 1080;
  const BH = (window.BH = window.BH || {});
  BH.W = W; BH.H = H;
  const PAL = (BH.PAL = { paper: '#ece2ca', ink: '#1f1b1c', red: '#c63b2b', blue: '#2c5b82' });
  const PLATES = ['blue', 'red', 'ink'];

  // ====================== 印刷工具 ======================
  BH.rng = function (seed) {
    let a = (Number(seed) || 1) >>> 0;
    const f = () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    f.range = (lo, hi) => lo + (hi - lo) * f();
    return f;
  };
  BH.noise = function (seed) {
    const r = BH.rng(seed), P = new Uint8Array(512), V = new Float32Array(256);
    for (let i = 0; i < 256; i++) { P[i] = i; V[i] = r(); }
    for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); const t = P[i]; P[i] = P[j]; P[j] = t; }
    for (let i = 0; i < 256; i++) P[i + 256] = P[i];
    const s = (t) => t * t * (3 - 2 * t);
    const n2 = (x, y) => {
      const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, X = xi & 255, Y = yi & 255;
      const a = V[P[P[X] + Y]], b = V[P[P[X + 1] + Y]], c = V[P[P[X] + Y + 1]], d = V[P[P[X + 1] + Y + 1]], u = s(xf), v = s(yf);
      return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
    };
    n2.fbm = (x, y, oct = 4) => { let t = 0, amp = 0.5, f = 1, n = 0; for (let i = 0; i < oct; i++) { t += amp * n2(x * f, y * f); n += amp; amp *= 0.5; f *= 2; } return t / n; };
    return n2;
  };
  BH.canvas = (w = W, h = H) => { const c = document.createElement('canvas'); c.width = Math.max(1, Math.ceil(w)); c.height = Math.max(1, Math.ceil(h)); return c; };
  BH.noiseImage = function (seed, w, h, scale, oct, colorFn) {
    w = Math.max(1, Math.ceil(w)); h = Math.max(1, Math.ceil(h));
    const c = BH.canvas(w, h), x = c.getContext('2d'), im = x.createImageData(w, h), n = BH.noise(seed);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      const col = colorFn(n.fbm(i * scale, j * scale, oct), i, j), k = (j * w + i) * 4;
      im.data[k] = col[0]; im.data[k + 1] = col[1]; im.data[k + 2] = col[2]; im.data[k + 3] = col[3];
    }
    x.putImageData(im, 0, 0); return c;
  };
  // 元素画布带一个“基准变换”（把屏幕坐标映射到元素画布）；需要回到屏幕坐标时用它，而不是单位矩阵
  BH.base = (ctx) => ctx.__base || new DOMMatrix();
  BH.at = function (ctx, x, y, s, fn, flip = false, rot = 0) { ctx.save(); ctx.translate(x, y); if (rot) ctx.rotate(rot); ctx.scale(flip ? -s : s, s); fn(ctx); ctx.restore(); };

  BH.paper = function (ctx, o = {}) {
    const { base = PAL.paper, seed = 1, fibers = 1800, blotchAmt = 0.22 } = o;
    ctx.fillStyle = base; ctx.fillRect(0, 0, W, H);
    const b = BH.noiseImage(seed, 240, 135, 0.03, 5, (v) => [0, 0, 0, Math.max(0, v - 0.45) * 255 * blotchAmt * 2]);
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(b, 0, 0, W, H);
    const b2 = BH.noiseImage(seed + 7, 480, 270, 0.08, 3, (v) => [255, 255, 255, Math.max(0, v - 0.55) * 255 * 0.5]);
    ctx.globalCompositeOperation = 'screen'; ctx.drawImage(b2, 0, 0, W, H); ctx.restore();
    const r = BH.rng(seed + 3); ctx.save(); ctx.lineCap = 'round';
    for (let i = 0; i < fibers; i++) {
      const x = r() * W, y = r() * H, len = 6 + r() * 30, a = r() * Math.PI * 2;
      ctx.strokeStyle = `rgba(90,70,40,${0.04 + r() * 0.08})`; ctx.lineWidth = 0.6 + r() * 0.9;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.quadraticCurveTo(x + Math.cos(a + 0.6) * len * 0.5, y + Math.sin(a + 0.6) * len * 0.5, x + Math.cos(a) * len, y + Math.sin(a) * len); ctx.stroke();
    }
    for (let i = 0; i < 500; i++) { ctx.fillStyle = `rgba(120,90,50,${0.05 + r() * 0.12})`; ctx.beginPath(); ctx.arc(r() * W, r() * H, 0.5 + r() * 1.6, 0, 7); ctx.fill(); }
    ctx.restore();
  };
  BH.grainTile = function (seed, amt = 0.07) {
    const c = BH.canvas(512, 512), x = c.getContext('2d'), im = x.createImageData(512, 512), r = BH.rng(seed);
    for (let i = 0; i < im.data.length; i += 4) { const v = r() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255 * amt; }
    x.putImageData(im, 0, 0); return c;
  };
  // 半调网点：dens 画布的 alpha → 点，画进 ctx（都按设备像素算；res 是元素的分辨率倍数）
  BH.halftone = function (ctx, dens, o = {}) {
    const res = o.res || 1, cell = (o.cell || 9) * res, angle = o.angle == null ? 15 : o.angle, maxR = (o.maxR || 0.62) * cell, minA = o.minA || 0.02;
    const w = dens.width, h = dens.height, d = dens.getContext('2d').getImageData(0, 0, w, h).data;
    const a = (angle * Math.PI) / 180, ux = Math.cos(a) * cell, uy = Math.sin(a) * cell, vx = -uy, vy = ux;
    const R = Math.ceil(Math.hypot(w, h) / cell) + 2;
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = o.color || '#000'; ctx.beginPath();
    let any = false;
    for (let i = -R; i <= R; i++) for (let j = -R; j <= R; j++) {
      const x = w / 2 + i * ux + j * vx, y = h / 2 + i * uy + j * vy;
      if (x < -cell || y < -cell || x > w + cell || y > h + cell) continue;
      const xi = Math.min(w - 1, Math.max(0, x | 0)), yi = Math.min(h - 1, Math.max(0, y | 0)), al = d[(yi * w + xi) * 4 + 3] / 255;
      if (al < minA) continue;
      const r = maxR * Math.sqrt(al); ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, Math.PI * 2); any = true;
    }
    if (any) ctx.fill(); ctx.restore();
  };
  // 印刷质感：墨层上啃出空隙、毛边（按设备像素）
  BH.inkify = function (cv, o = {}) {
    const { seed = 5, voids = 0.3, edge = 0.5, fine = 0.4 } = o;
    const w = cv.width, h = cv.height, x = cv.getContext('2d'), im = x.getImageData(0, 0, w, h), d = im.data;
    let any = false; for (let k = 3; k < d.length; k += 64) if (d[k]) { any = true; break; }
    if (!any) { for (let k = 3; k < d.length; k += 4) if (d[k]) { any = true; break; } }
    if (!any) return false;
    const bw = Math.ceil(w / 4), bh = Math.ceil(h / 4);
    const bd = BH.noiseImage(seed, bw, bh, 0.09, 4, (v) => [0, 0, 0, v * 255]).getContext('2d').getImageData(0, 0, bw, bh).data;
    const r = BH.rng(seed + 1);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      const k = (j * w + i) * 4, a = d[k + 3]; if (!a) continue;
      const nb = bd[((j >> 2) * bw + (i >> 2)) * 4 + 3] / 255, nf = r();
      let m = 1 - voids * Math.max(0, nb - 0.55) * 4 - fine * (nf < 0.06 ? 0.8 : 0);
      const af = a / 255; if (af < 0.98) m *= nf * edge + (1 - edge) > 1 - af ? 1.15 : 0.2;
      d[k + 3] = Math.max(0, Math.min(255, a * m));
    }
    x.putImageData(im, 0, 0); return true;
  };
  // 在 path 内画平行排线（路径走当前变换；线走元素的屏幕坐标）
  BH.hatch = function (ctx, path, o = {}) {
    const { angle = 45, gap = 10, width = 2, color = PAL.ink, rect = [0, 0, W, H], wobble = 0, seed = 2 } = o;
    ctx.save(); ctx.clip(path); ctx.setTransform(BH.base(ctx)); ctx.strokeStyle = color; ctx.lineCap = 'round';
    const a = (angle * Math.PI) / 180, cx = rect[0] + rect[2] / 2, cy = rect[1] + rect[3] / 2, R = Math.hypot(rect[2], rect[3]) / 2 + 10, r = BH.rng(seed);
    for (let t = -R; t <= R; t += gap) {
      ctx.lineWidth = width * (0.8 + r() * 0.4);
      const px = cx + Math.cos(a + Math.PI / 2) * t, py = cy + Math.sin(a + Math.PI / 2) * t; ctx.beginPath();
      for (let s = 0; s <= 8; s++) { const u = -R + (2 * R * s) / 8, wv = wobble ? (r() - 0.5) * wobble : 0;
        const x = px + Math.cos(a) * u + Math.cos(a + Math.PI / 2) * wv, y = py + Math.sin(a) * u + Math.sin(a + Math.PI / 2) * wv; s ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
      ctx.stroke();
    }
    ctx.restore();
  };
  BH.ridge = function (x0, x1, base, peak, seed, rough = 1, step = 8) {
    const n = BH.noise(seed), pts = [];
    for (let x = x0; x <= x1 + step; x += step) {
      const u = (x - x0) / (x1 - x0), env = Math.sin(Math.min(1, Math.max(0, u)) * Math.PI) ** 0.7;
      pts.push([x, base - peak * env * (0.55 + 0.6 * n.fbm(x * 0.0035, seed * 0.1, 3) + 0.2 * rough * (n(x * 0.03, 3) - 0.5))]);
    }
    return pts;
  };
  BH.ridgePath = (pts, base) => { const p = new Path2D(); p.moveTo(pts[0][0], base); for (const q of pts) p.lineTo(q[0], q[1]); p.lineTo(pts[pts.length - 1][0], base); p.closePath(); return p; };
  BH.polyline = (ctx, pts) => { ctx.beginPath(); pts.forEach((q, i) => (i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]))); };
  BH.torn = function (x, y, w, h, seed, jag = 7) {
    const r = BH.rng(seed), p = new Path2D(), pts = [];
    const edge = (x0, y0, x1, y1) => { const n = Math.max(4, (Math.hypot(x1 - x0, y1 - y0) / 9) | 0); for (let i = 0; i < n; i++) { const t = i / n; pts.push([x0 + (x1 - x0) * t + (r() - 0.5) * jag, y0 + (y1 - y0) * t + (r() - 0.5) * jag]); } };
    edge(x, y, x + w, y); edge(x + w, y, x + w, y + h); edge(x + w, y + h, x, y + h); edge(x, y + h, x, y);
    pts.forEach((q, i) => (i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1]))); p.closePath(); return p;
  };
  BH.roof = function (cx, y, hw, h, lift = 22) {
    const p = new Path2D();
    p.moveTo(cx - hw - lift * 1.6, y - lift); p.quadraticCurveTo(cx - hw - lift * 0.3, y + 4, cx - hw, y + 2); p.lineTo(cx + hw, y + 2);
    p.quadraticCurveTo(cx + hw + lift * 0.3, y + 4, cx + hw + lift * 1.6, y - lift); p.quadraticCurveTo(cx + hw * 0.62, y - h * 0.3, cx + hw * 0.5, y - h);
    p.lineTo(cx - hw * 0.5, y - h); p.quadraticCurveTo(cx - hw * 0.62, y - h * 0.3, cx - hw - lift * 1.6, y - lift); p.closePath(); return p;
  };
  BH.font = (fam, size, weight = '') => `${weight} ${size}px ${fam}`.trim();
  BH.text = function (ctx, s, x, y, o = {}) {
    const { fam = 'Serif', size = 54, weight = '900', color = PAL.ink, align = 'center', spacing = 0, stroke = null, strokeW = 0 } = o;
    ctx.save(); ctx.font = BH.font(fam, size, weight); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    const chars = [...s], ws = chars.map((c) => ctx.measureText(c).width), total = ws.reduce((a, b) => a + b, 0) + spacing * (chars.length - 1);
    let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
    chars.forEach((c, i) => { if (stroke) { ctx.lineJoin = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = strokeW; ctx.strokeText(c, cx, y); } ctx.fillStyle = color; ctx.fillText(c, cx, y); cx += ws[i] + spacing; });
    ctx.restore(); return total;
  };
  BH.vtext = function (ctx, s, x, y, o = {}) {
    const { fam = 'Serif', size = 48, weight = '900', color = PAL.ink, gap = 6 } = o;
    ctx.save(); ctx.font = BH.font(fam, size, weight); ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    [...s].forEach((c, i) => { if ('，。、'.includes(c)) ctx.fillText(c, x + size * 0.35, y + i * (size + gap) - size * 0.45); else ctx.fillText(c, x, y + i * (size + gap)); });
    ctx.restore(); return [...s].length * (size + gap);
  };
  BH.seal = function (ctx, x, y, size, chars, o = {}) {
    const { color = PAL.red, fam = 'Serif', weight = '900', seed = 4, rot = 0 } = o;
    const c = BH.canvas(size + 8, size + 8), x2 = c.getContext('2d');
    x2.fillStyle = color; x2.fillRect(4, 4, size, size); x2.globalCompositeOperation = 'destination-out';
    x2.strokeStyle = '#000'; x2.lineWidth = size * 0.03; x2.strokeRect(4 + size * 0.07, 4 + size * 0.07, size * 0.86, size * 0.86);
    const n = chars.length, cols = n > 2 ? 2 : 1, rows = Math.ceil(n / cols), cs = (size * 0.78) / Math.max(rows, cols);
    x2.font = BH.font(fam, cs * 0.95, weight); x2.textAlign = 'center'; x2.textBaseline = 'middle'; x2.fillStyle = '#000';
    [...chars].forEach((ch, i) => { const col = Math.floor(i / rows), row = i % rows;
      const cx = 4 + size - size * 0.11 - cs * (col + 0.5) - (cols === 1 ? (size * 0.78 - cs) / 2 : 0), cy = 4 + size * 0.11 + cs * (row + 0.5) + (rows === 1 ? (size * 0.78 - cs) / 2 : 0);
      x2.fillText(ch, cx, cy); });
    const r = BH.rng(seed); for (let i = 0; i < size * 1.2; i++) { x2.beginPath(); x2.arc(4 + r() * size, 4 + r() * size, r() * size * 0.018 + 0.4, 0, 7); x2.fill(); }
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.globalAlpha = 0.92; ctx.drawImage(c, -size / 2 - 4, -size / 2 - 4); ctx.restore();
  };

  // ====================== 歌曲数据 ======================
  BH.song = function () {
    const node = document.getElementById('song');
    const s = node ? JSON.parse(node.textContent) : null;
    if (!s || !s.duration) throw new Error('index.html 里没有歌曲数据（#song）：先跑 scripts/song_sync.py');
    s.lines = s.lines || []; s.sections = s.sections || []; s.beats = s.beats || [];
    s.line = (n) => { const l = s.lines[n - 1]; if (!l) throw new Error(`没有第 ${n} 句歌词（共 ${s.lines.length} 句）`); return l; };
    s.sec = (k) => { const x = typeof k === 'number' ? s.sections[k - 1] : s.sections.find((q) => q.label === k || q.tag === k); if (!x) throw new Error('没有段落：' + k); return x; };
    s.beatPeriod = s.bpm ? 60 / s.bpm : 0.8;
    s.snap = (t) => { if (!s.beats.length) return t; let b = s.beats[0]; for (const x of s.beats) if (Math.abs(x - t) < Math.abs(b - t)) b = x; return b; };
    s.beatAfter = (t) => s.beats.find((x) => x >= t - 1e-6) ?? t;
    s.beatBefore = (t) => { let b = null; for (const x of s.beats) if (x <= t + 1e-6) b = x; return b ?? t; };
    s.beatsIn = (a, b) => s.beats.filter((x) => x >= a && x < b);
    s.at = (t) => s.lines.find((l) => t >= l.start && t < l.end) || null;
    return s;
  };

  // ====================== 影片 ======================
  BH.film = function (opts = {}) {
    const V = window.MR && MR.vars ? MR.vars() : {};
    const song = BH.song();
    const tl = gsap.timeline({ paused: true });
    tl.set({}, {}, song.duration);
    const root = document.getElementById('film');
    const stage = document.getElementById('stage') || (() => { const c = BH.canvas(); c.id = 'stage'; root.appendChild(c); return c; })();
    const ctx = stage.getContext('2d');
    const fp = {}; for (const p of PLATES) { const c = BH.canvas(); fp[p] = { c, x: c.getContext('2d') }; }
    const color = { blue: PAL.blue, red: PAL.red, ink: PAL.ink };
    let paperC = null; const grains = [];
    const F = { tl, song, vars: V, shots: [], topics: [], kicks: [], shakes: [], opts, subsOn: true };
    let finished = false;

    // ---------- 元素 ----------
    let elSeq = 0;
    function makeEl(sh, o, draw) {
      if (typeof o === 'function') { draw = o; o = {}; }
      const el = {
        id: ++elSeq, shot: sh, name: o.name || `${sh.name}#${sh.els.length + 1}`, box: o.box || [0, 0, W, H], res: o.res || sh.res, depth: o.depth == null ? 1 : o.depth,
        knock: o.knock !== false, kind: o.kind || 'pic', draw, seed: o.seed || elSeq * 7 + 3, from: o.from || 0, until: o.until == null ? null : o.until,
        origin: o.origin || null, bg: o.bg, p: { x: 0, y: 0, scale: 1, rot: 0, alpha: 1 }, procs: [], cv: null, bbox: null, visible: null, text: o.text || null,
        tone: o.tone || {},
      };
      const rel = (at) => sh.t0 + (at || 0);
      const dur = (d) => (d === 'shot' ? sh.t1 - sh.t0 : d == null ? 0.6 : d);
      el.set = (vars, at = 0) => { tl.set(el.p, vars, rel(at)); return el; };
      el.to = (vars, t = {}) => { tl.to(el.p, Object.assign({}, vars, { duration: dur(t.dur), ease: t.ease || 'power2.inOut', immediateRender: false }), rel(t.at)); return el; };
      el.from = (vars, t = {}) => { const end = {}; for (const k of Object.keys(vars)) end[k] = el.p[k];
        tl.fromTo(el.p, Object.assign({}, vars), Object.assign(end, { duration: dur(t.dur), ease: t.ease || 'power2.out', immediateRender: false }), rel(t.at));
        if (!t.at) Object.assign(el.p, vars); return el; };
      // 程序化运动（按时间算，逐帧确定）
      el.bob = (o2 = {}) => { el.procs.push({ k: 'y', amp: o2.amp ?? 4, period: o2.period ?? song.beatPeriod, phase: o2.phase || 0 }); return el; };
      el.sway = (o2 = {}) => { el.procs.push({ k: 'rot', amp: o2.deg ?? 1.5, period: o2.period ?? song.beatPeriod * 2, phase: o2.phase || 0 }); return el; };
      el.drift = (o2 = {}) => { el.procs.push({ k: 'drift', x: o2.x || 0, y: o2.y || 0 }); return el; };
      el.pulse = (o2 = {}) => { el.procs.push({ k: 'pulse', amt: o2.amt ?? 0.03, beats: o2.beats || song.beatsIn(sh.t0, sh.t1) }); return el; };
      sh.els.push(el);
      return el;
    }

    function prerender(el) {
      const [bx, by, bw, bh] = el.box, r = el.res, cw = Math.ceil(bw * r), ch = Math.ceil(bh * r);
      const t0 = performance.now();
      const mk = () => { const c = BH.canvas(cw, ch), x = c.getContext('2d'), m = new DOMMatrix().scale(r).translate(-bx, -by); x.setTransform(m); x.__base = m; return [c, x]; };
      const pl = {}; for (const k of ['ink', 'red', 'blue', 'inkT', 'redT', 'blueT', 'mask']) { const [c, x] = mk(); pl[k] = { c, x }; }
      pl.ink.x.fillStyle = pl.ink.x.strokeStyle = PAL.ink; pl.red.x.fillStyle = pl.red.x.strokeStyle = PAL.red; pl.blue.x.fillStyle = pl.blue.x.strokeStyle = PAL.blue;
      for (const k of ['inkT', 'redT', 'blueT', 'mask']) pl[k].x.fillStyle = pl[k].x.strokeStyle = '#000';
      const o = { ink: pl.ink.x, red: pl.red.x, blue: pl.blue.x, inkT: pl.inkT.x, redT: pl.redT.x, blueT: pl.blueT.x, mask: pl.mask.x, box: el.box, res: r, seed: el.seed,
        knock: (path) => { pl.mask.x.fill(path); }, knockRect: (x, y, w, h) => { pl.mask.x.fillRect(x, y, w, h); } };
      el.draw(o);
      const tn = el.tone;
      BH.halftone(pl.blue.x, pl.blueT.c, { res: r, cell: tn.blueCell || 9, angle: 15, color: PAL.blue });
      BH.halftone(pl.red.x, pl.redT.c, { res: r, cell: tn.redCell || 8, angle: 75, color: PAL.red });
      BH.halftone(pl.ink.x, pl.inkT.c, { res: r, cell: tn.inkCell || 7, angle: 45, color: PAL.ink });
      const s = el.seed;
      BH.inkify(pl.blue.c, { seed: s + 1, voids: tn.voids ?? 0.3, fine: 0.45 });
      BH.inkify(pl.red.c, { seed: s + 2, voids: tn.voids ?? 0.35, fine: 0.45 });
      BH.inkify(pl.ink.c, { seed: s + 3, voids: tn.inkVoids ?? 0.16, fine: 0.3 });
      const m = pl.mask.x; m.save(); m.setTransform(1, 0, 0, 1, 0, 0); for (const k of PLATES) m.drawImage(pl[k].c, 0, 0); m.restore();
      for (const k of ['inkT', 'redT', 'blueT']) { pl[k].c.width = pl[k].c.height = 1; }
      el.cv = { blue: pl.blue.c, red: pl.red.c, ink: pl.ink.c, mask: pl.mask.c, w: cw, h: ch };
      el.ms = performance.now() - t0;
    }
    function release(el) { if (!el.cv) return; for (const k of ['blue', 'red', 'ink', 'mask']) { el.cv[k].width = el.cv[k].height = 1; } el.cv = null; }
    function contentBox(el) {
      if (el.bbox) return el.bbox;
      if (!el.cv) prerender(el);
      const { w, h } = el.cv, d = el.cv.mask.getContext('2d').getImageData(0, 0, w, h).data;
      let x0 = w, y0 = h, x1 = -1, y1 = -1;
      for (let j = 0; j < h; j += 3) for (let i = 0; i < w; i += 3) if (d[(j * w + i) * 4 + 3] > 40) { if (i < x0) x0 = i; if (i > x1) x1 = i; if (j < y0) y0 = j; if (j > y1) y1 = j; }
      const [bx, by] = el.box, r = el.res;
      el.bbox = x1 < 0 ? null : [bx + x0 / r, by + y0 / r, bx + (x1 + 3) / r, by + (y1 + 3) / r];
      return el.bbox;
    }

    // ---------- 镜头 ----------
    F.shot = function (name, from, build, o = {}) {
      if (finished) throw new Error('F.shot 要写在 F.finish() 之前');
      F.shots.push({ name, from: Number(from), build, o });
      return F;
    };
    function buildShots() {
      F.shots.sort((a, b) => a.from - b.from);
      if (!F.shots.length) throw new Error('没有镜头：至少要一个 F.shot');
      if (F.shots[0].from > 0.001) throw new Error(`第一个镜头要从 0 秒开始（现在从 ${F.shots[0].from}s）：第 0 帧就是封面`);
      F.shots.forEach((s, i) => {
        s.t0 = s.from; s.t1 = i + 1 < F.shots.length ? F.shots[i + 1].from : song.duration;
        s.trans = s.o.transition || (i === 0 ? 'none' : 'cut'); s.transDur = s.o.transDur || { wipe: 0.55, paper: 0.5, split: 0.5, cut: 0, none: 0 }[s.trans] || 0;
        s.res = s.o.res || 1.12; s.els = []; s.cycles = []; s.cam = { zoom: 1, fx: W / 2, fy: H / 2, rot: 0 }; s.subs = s.o.subs !== false; s.idx = i;
        s.dur = s.t1 - s.t0;
        const sh = s;
        sh.el = (o2, draw) => makeEl(sh, o2, draw);
        sh.beats = () => song.beatsIn(sh.t0, sh.t1);
        sh.camSet = (vars) => { Object.assign(sh.cam, vars); return sh; };
        sh.camTo = (vars, t = {}) => { tl.to(sh.cam, Object.assign({}, vars, { duration: t.dur === 'shot' || t.dur == null ? sh.t1 - sh.t0 - (t.at || 0) : t.dur, ease: t.ease || 'sine.inOut', immediateRender: false }), sh.t0 + (t.at || 0)); return sh; };
        sh.push = (zoom = 1.12, o3 = {}) => { const from = Object.assign({}, sh.cam); tl.fromTo(sh.cam, from, Object.assign({ zoom, fx: o3.fx ?? sh.cam.fx, fy: o3.fy ?? sh.cam.fy, duration: sh.t1 - sh.t0, ease: o3.ease || 'none', immediateRender: false }), sh.t0); return sh; };
        sh.cycle = (els, o3 = {}) => { const period = o3.period || song.beatPeriod / 2; els.forEach((e, k) => { e.visible = (t) => Math.floor((t - sh.t0) / period) % els.length === k; }); return sh; };
        sh.type = (lineOrText, o3 = {}) => typeset(sh, lineOrText, o3);
        sh.kick = (at, amt) => { F.kick(sh.t0 + at, amt); return sh; };
        if (s.trans === 'split') F.kick(s.t0, 24);
        s.build(sh, song);
      });
    }

    // ---------- 副歌大字（借拼贴排版：一字一印，按唱到的时间砸下来）----------
    function typeset(sh, src, o) {
      let text, chars;
      if (typeof src === 'number') { const l = song.line(src); text = l.display || l.text; chars = l.chars || null; }
      else if (src && src.text) { text = src.display || src.text; chars = src.chars || null; }
      else { text = String(src); chars = null; }
      // 行：按空格分短语；短语超过 maxPerRow（默认 4）字再均分成几行——大字要大
      const per = o.maxPerRow || 4;
      const rows = o.rows || text.split(/[\s　]+/).filter(Boolean).flatMap((ph) => { const cs = [...ph], n = Math.ceil(cs.length / per), k = Math.ceil(cs.length / n), out = []; for (let i = 0; i < cs.length; i += k) out.push(cs.slice(i, i + k).join('')); return out; });
      const box = o.box || [110, 200, 900, 680];
      const scales = o.scale ? rows.map((_, i) => o.scale[i] ?? o.scale[o.scale.length - 1]) : rows.map(() => 1);
      const gap = o.gap || 0.12;
      const maxLen = Math.max(...rows.map((r, i) => [...r].length * scales[i]));
      const sumH = rows.reduce((a, r, i) => a + scales[i] * (1 + gap), 0);
      const size = Math.min(o.size || 300, box[2] / maxLen / 0.98, box[3] / sumH);
      const totalH = rows.reduce((a, r, i) => a + size * scales[i] * (1 + gap), 0);
      let y = box[1] + (o.valign === 'top' ? 0 : (box[3] - totalH) / 2);
      // 字的时间：给了逐字时间就用；否则按镜头起点均匀排
      const flat = [...text].filter((c) => !/[\s　]/.test(c));
      let times = flat.map((_, i) => sh.t0 + 0.15 + i * 0.12);
      if (chars) { const tc = chars.filter((c) => !/[\s　]/.test(c.c)); if (tc.length === flat.length) times = tc.map((c) => c.s); }
      const colorOf = o.color || ((ri, ci, gi) => (ri === rows.length - 1 ? 'red' : 'ink'));
      const out = []; let gi = 0;
      rows.forEach((row, ri) => {
        const sz = size * scales[ri], cs = [...row];
        y += sz * (1 + gap) * 0.88;
        let x = o.align === 'center' ? box[0] + (box[2] - cs.length * sz * 0.98) / 2 : box[0];
        cs.forEach((c, ci) => {
          const col = typeof colorOf === 'function' ? colorOf(ri, ci, gi) : colorOf;
          const cx = x, cy = y, g = gi;
          const el = makeEl(sh, { name: `${sh.name}:字${gi + 1}`, box: [cx - sz * 0.05, cy - sz * 0.98, sz * 1.1, sz * 1.25], kind: 'type', text: c, res: o.res || 1.05, depth: o.depth ?? 0.6, seed: 900 + gi * 13 + sh.idx * 101 },
            (p) => { const plate = col === 'tone' ? p.inkT : p[col]; BH.text(plate, c, cx, cy, { size: sz, color: col === 'tone' ? 'rgba(0,0,0,0.55)' : PAL[col] || PAL.ink, align: 'left' }); });
          const at = Math.max(0, times[g] - sh.t0 - (o.lead ?? 0.04));
          if (o.mode === 'all') { /* 整句从镜头开始就在 */ }
          else { el.set({ alpha: 0 }, 0); el.set({ alpha: 1 }, at); el.from({ scale: o.slam ?? 1.35 }, { at, dur: 0.22, ease: 'back.out(2.2)' }); }
          if (o.kick !== false && ci === 0 && o.mode !== 'all') F.kick(sh.t0 + at, o.kickAmt ?? 7);
          el.origin = [cx + sz * 0.5, cy - sz * 0.38];
          out.push(el); x += sz * 0.98; gi++;
        });
      });
      return out;
    }

    // ---------- 节拍错版、震屏、主题栏 ----------
    F.kick = (t, amt = 8) => { F.kicks.push({ t, amt, dir: BH.rng(Math.round(t * 1000) + 1)() * Math.PI * 2 }); return F; };
    F.kickBeats = (from, to, o = {}) => { const every = o.every || 2; song.beatsIn(from, to).forEach((b, i) => { if (i % every === 0) F.kick(b, o.amt ?? 5); }); return F; };
    F.shake = (t, amt = 10, dur = 0.4) => { F.shakes.push({ t, amt, dur }); return F; };
    F.topic = (t, text) => { F.topics.push({ t, text }); F.topics.sort((a, b) => a.t - b.t); return F; };
    F.subs = (on) => { F.subsOn = on !== false; return F; };

    function reg(t) {
      const step = Math.floor(t * 6), r = BH.rng(step * 31 + 7);
      const o = { blue: [4 + (r() - 0.5) * 2.4, -3 + (r() - 0.5) * 2.4], red: [-3 + (r() - 0.5) * 2.4, 4 + (r() - 0.5) * 2.4], ink: [(r() - 0.5) * 0.8, (r() - 0.5) * 0.8] };
      for (const k of F.kicks) { const d = t - k.t; if (d < 0 || d > 0.9) continue; const e = k.amt * Math.exp(-d * 7) * Math.cos(d * 18);
        o.blue[0] += Math.cos(k.dir) * e; o.blue[1] += Math.sin(k.dir) * e; o.red[0] -= Math.cos(k.dir) * e; o.red[1] -= Math.sin(k.dir) * e; }
      return o;
    }
    function shake(t) { let x = 0, y = 0; for (const s of F.shakes) { const d = t - s.t; if (d < 0 || d > s.dur) continue; const e = s.amt * (1 - d / s.dur); const r = BH.rng(Math.floor(t * 30) + 3); x += (r() - 0.5) * 2 * e; y += (r() - 0.5) * 2 * e; } return [x, y]; }

    // ---------- 合成 ----------
    function procVal(el, t) {
      let dx = 0, dy = 0, dr = 0, ds = 0; const sh = el.shot, u = (t - sh.t0) / Math.max(0.001, sh.t1 - sh.t0);
      for (const p of el.procs) {
        if (p.k === 'y') dy += p.amp * Math.sin((2 * Math.PI * (t - sh.t0)) / p.period + p.phase);
        else if (p.k === 'rot') dr += p.amp * Math.sin((2 * Math.PI * (t - sh.t0)) / p.period + p.phase);
        else if (p.k === 'drift') { dx += p.x * u; dy += p.y * u; }
        else if (p.k === 'pulse') { for (const b of p.beats) { const d = t - b; if (d >= 0 && d < 0.35) ds += p.amt * (1 - d / 0.35); } }
      }
      return [dx, dy, dr, ds];
    }
    function matrix(el, t) {
      const sh = el.shot, c = sh.cam, d = el.depth, z = 1 + (c.zoom - 1) * d;
      const cx = W / 2 + (c.fx - W / 2) * d, cy = H / 2 + (c.fy - H / 2) * d;
      const [dx, dy, dr, ds] = procVal(el, t);
      const [bx, by, bw, bh] = el.box, o = el.origin || [bx + bw / 2, by + bh / 2];
      return new DOMMatrix().translate(W / 2, H / 2).scale(z).rotate((c.rot || 0) * d).translate(-cx, -cy)
        .translate(o[0] + el.p.x + dx, o[1] + el.p.y + dy).rotate(el.p.rot + dr).scale(el.p.scale + ds).translate(-o[0], -o[1])
        .translate(bx, by).scale(1 / el.res);
    }
    function visibleEls(sh, t) {
      return sh.els.filter((el) => {
        if (t < sh.t0 + el.from) return false; if (el.until != null && t >= sh.t0 + el.until) return false;
        if (el.visible && !el.visible(t)) return false; return el.p.alpha > 0.001;
      });
    }
    function activeShots(t) {
      const out = [];
      F.shots.forEach((s, i) => {
        if (t >= s.t0 && t < s.t1) out.push({ s, role: 'main' });
        else if (i + 1 < F.shots.length && t >= s.t1 && t < s.t1 + F.shots[i + 1].transDur && F.shots[i + 1].trans === 'wipe') out.push({ s, role: 'under' });
      });
      if (!out.length && t >= song.duration - 1e-3 && F.shots.length) out.push({ s: F.shots[F.shots.length - 1], role: 'main' });
      out.sort((a, b) => (a.role === 'under' ? -1 : 1));
      return out;
    }
    function wipePath(s, t) {
      const u = Math.min(1, (t - s.t0) / s.transDur), e = 1 - Math.pow(1 - u, 3), X = -120 + (W + 240) * e, r = BH.rng(s.idx * 17 + 5), p = new Path2D();
      p.moveTo(-10, -10); for (let y = -10; y <= H + 40; y += 36) p.lineTo(X + (r() - 0.5) * 70 + Math.sin(y * 0.02) * 30, y); p.lineTo(-10, H + 40); p.closePath(); return p;
    }
    function compose(t) {
      if (!paperC) { paperC = BH.canvas(); BH.paper(paperC.getContext('2d'), { seed: (V.paperSeed || 13) }); for (let i = 0; i < 3; i++) grains.push(BH.grainTile(51 + i, 0.07)); }
      for (const p of PLATES) { fp[p].x.setTransform(1, 0, 0, 1, 0, 0); fp[p].x.globalCompositeOperation = 'source-over'; fp[p].x.globalAlpha = 1; fp[p].x.clearRect(0, 0, W, H); }
      const act = activeShots(t);
      // 缓存：只留当前与下一个镜头
      const keep = new Set(); act.forEach((a) => keep.add(a.s)); const nx = F.shots.find((s) => s.t0 > t); if (nx) keep.add(nx);
      for (const s of F.shots) if (!keep.has(s)) s.els.forEach(release);
      for (const a of act) {
        const s = a.s, wiping = a.role === 'main' && s.trans === 'wipe' && t < s.t0 + s.transDur;
        let clip = null;
        if (wiping) { clip = wipePath(s, t); for (const p of PLATES) { const x = fp[p].x; x.save(); x.globalCompositeOperation = 'destination-out'; x.fill(clip); x.restore(); } }
        for (const el of visibleEls(s, t)) {
          if (!el.cv) prerender(el);
          const M = matrix(el, t);
          for (const p of PLATES) {
            const x = fp[p].x; x.save();
            if (clip) { x.setTransform(1, 0, 0, 1, 0, 0); x.clip(clip); }
            x.setTransform(M); x.globalAlpha = Math.min(1, el.p.alpha);
            if (el.knock) { x.globalCompositeOperation = 'destination-out'; x.drawImage(el.cv.mask, 0, 0); }
            x.globalCompositeOperation = 'source-over'; x.drawImage(el.cv[p], 0, 0); x.restore();
          }
        }
      }
      const [sx, sy] = shake(t), o = reg(t);
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; ctx.drawImage(paperC, 0, 0);
      ctx.save(); ctx.translate(sx, sy); ctx.globalCompositeOperation = 'multiply';
      ctx.globalAlpha = 0.92; ctx.drawImage(fp.blue.c, o.blue[0], o.blue[1]); ctx.globalAlpha = 0.95; ctx.drawImage(fp.red.c, o.red[0], o.red[1]); ctx.globalAlpha = 1; ctx.drawImage(fp.ink.c, o.ink[0], o.ink[1]);
      ctx.restore();
      // 纸闪转场
      for (const a of act) { const s = a.s; if (a.role === 'main' && s.trans === 'paper' && t < s.t0 + s.transDur / 2) { ctx.save(); ctx.globalAlpha = 1 - (t - s.t0) / (s.transDur / 2); ctx.drawImage(paperC, 0, 0); ctx.restore(); } }
      const nxt = F.shots.find((s) => s.trans === 'paper' && t >= s.t0 - s.transDur / 2 && t < s.t0);
      if (nxt) { ctx.save(); ctx.globalAlpha = 1 - (nxt.t0 - t) / (nxt.transDur / 2); ctx.drawImage(paperC, 0, 0); ctx.restore(); }
      ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.fillStyle = ctx.createPattern(grains[Math.floor(t * 6) % 3], 'repeat'); ctx.fillRect(0, 0, W, H); ctx.restore();
      hud(t, act);
    }

    // ---------- 版面：主题栏、署名、字幕 ----------
    const HUD = (F.HUD = { topic: [60, 40, 850, 96], sign: [1600, 0, 320, 170], subs: [0, 905, W, 175] });
    function topicAt(t) { let s = null; for (const x of F.topics) if (x.t <= t + 1e-6) s = x; return s; }
    function lineAt(t) {
      let cur = null;
      for (const l of song.lines) { const until = l.end + 0.5; if (t >= l.start - 0.25 && t < until) cur = l; }
      return cur;
    }
    function hud(t, act) {
      if (opts.cover) { if (V.signature) { BH.text(ctx, V.signature, W - 104, 104, { weight: '600', size: 40, align: 'right', stroke: PAL.paper, strokeW: 8 }); BH.seal(ctx, W - 64, 88, 48, V.sealText || '景行', { seed: 7 }); } return; }
      const series = `${V.series || '大明开局'} · 第${V.epNo || '01'}集${V.songTitle ? '《' + V.songTitle + '》' : ''}`;
      const tp = topicAt(t);
      if (tp && tp.text) {
        ctx.save(); ctx.font = BH.font('Serif', 46, '900'); const tw = [...tp.text].reduce((a, c) => a + ctx.measureText(c).width + 4, 0); ctx.restore();
        const bw = Math.min(850, tw + 70);
        ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = PAL.red; ctx.fillRect(60, 40, bw, 96); ctx.restore();
        BH.text(ctx, tp.text, 60 + bw / 2, 106, { size: 46, color: PAL.paper, spacing: 4 });
      }
      BH.text(ctx, series, 64, 172, { fam: 'Serif', weight: '600', size: 24, align: 'left', stroke: PAL.paper, strokeW: 6 });
      if (V.signature) { BH.text(ctx, V.signature, 1800, 104, { weight: '600', size: 36, align: 'right', stroke: PAL.paper, strokeW: 8 }); BH.seal(ctx, 1836, 90, 44, V.sealText || '景行', { seed: 7 }); }
      const main = act.find((a) => a.role === 'main');
      const showSubs = F.subsOn && (!main || main.s.subs);
      const l = showSubs ? lineAt(t) : null;
      if (l) {
        ctx.save(); ctx.globalAlpha = 0.9; ctx.fillStyle = PAL.paper; ctx.fillRect(0, 905, W, 175); ctx.restore();
        ctx.fillStyle = PAL.ink; ctx.fillRect(0, 905, W, 5); ctx.fillRect(0, 914, W, 1.5);
        const txt = l.display || l.text, cs = [...txt], size = Math.min(58, 1560 / Math.max(1, cs.length));
        ctx.save(); ctx.font = BH.font('Serif', size, '900'); const ws = cs.map((c) => ctx.measureText(c).width + 6); const tot = ws.reduce((a, b) => a + b, 0);
        let x = 960 - tot / 2; const times = (l.chars && l.chars.length === cs.length) ? l.chars : null;
        cs.forEach((c, i) => {
          const sung = times ? (times[i].s == null ? t >= l.start : t >= times[i].s) : t >= l.start + (i / cs.length) * (l.end - l.start);
          ctx.fillStyle = sung ? (l.chorus ? PAL.red : PAL.ink) : 'rgba(31,27,28,0.36)'; ctx.fillText(c, x, 1012); x += ws[i];
        });
        ctx.restore();
      }
    }

    // ---------- 收尾：注册时间线 ----------
    F.finish = function () {
      buildShots(); finished = true;
      let last = -1;
      const film = { duration: () => song.duration, time: (x, s) => { if (x === undefined) return tl.time(); tl.time(Math.min(x, song.duration), s); compose(Math.min(x, song.duration)); last = x; return film; } };
      window.__timelines = Object.assign(window.__timelines || {}, { film });
      window.__bh = {
        shots: () => F.shots.map((s) => ({ name: s.name, t0: s.t0, t1: s.t1, trans: s.trans, els: s.els.length, type: s.els.filter((e) => e.kind === 'type').map((e) => e.text).join('') })),
        report: (t) => {
          film.time(t, true);
          const act = activeShots(t);
          const els = [];
          for (const a of act) for (const el of visibleEls(a.s, t)) {
            const b = contentBox(el); if (!b) continue; const M = matrix(el, t), r = el.res, bx = el.box[0], by = el.box[1];
            const pts = [[b[0], b[1]], [b[2], b[1]], [b[0], b[3]], [b[2], b[3]]].map(([x, y]) => M.transformPoint(new DOMPoint((x - bx) * r, (y - by) * r)));
            els.push({ shot: a.s.name, name: el.name, kind: el.kind, text: el.text, alpha: el.p.alpha, bg: el.bg === true || (b[2] - b[0]) * (b[3] - b[1]) > W * H * 0.45 || (b[2] - b[0]) > W * 0.6 || el.depth < 0.5,
              bbox: [Math.min(...pts.map((p) => p.x)), Math.min(...pts.map((p) => p.y)), Math.max(...pts.map((p) => p.x)), Math.max(...pts.map((p) => p.y))], ms: el.ms || 0 });
          }
          const l = lineAt(t), tp = topicAt(t);
          return { t, shots: act.map((a) => a.s.name), els, topic: tp ? tp.text : null, sub: l ? (l.display || l.text) : null, hud: HUD, duration: song.duration };
        },
        song: () => ({ duration: song.duration, lines: song.lines.map((l) => ({ start: l.start, end: l.end, text: l.display || l.text, chorus: !!l.chorus, tag: l.tag })), sections: song.sections, topics: F.topics }),
      };
      return F;
    };
    return F;
  };
})();
