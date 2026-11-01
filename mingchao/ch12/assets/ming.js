// 大明开局 —— 系列组件库（每章沿用；抖音 9:16，1080×1920）
// 一切都是时间的函数：随机数用 MR.random(seed)，图像在加载时一次性画好，动画全部挂在同一条 GSAP 时间线上。
(function () {
  const M = (window.Ming = {});
  const NS = 'http://www.w3.org/2000/svg';
  M.W = 1080; M.H = 1920;
  // 内容安全区（抖音界面盖不到的地方）：x 60–920、y 360–1240，水平中心 490；右侧按钮列 x>940 只放装饰
  M.SAFE = { x: 60, y: 360, w: 860, h: 880, cx: 490, bottom: 1240 };
  M.C = {
    paper: '#efe6d2', paper2: '#e4d6b8', ink: '#15110d', ink2: '#4a4038', wash: '#8c8172', wash2: '#b9ad98',
    red: '#c23a2c', red2: '#8e241e', gold: '#b88a2e', gold2: '#d6b462', night: '#1b1d22',
  };

  // ---------- DOM ----------
  M.el = function (tag, cls, parent, html, style) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (style) Object.assign(e.style, style);
    if (parent) parent.appendChild(e);
    return e;
  };
  // 绝对定位的块：M.box(parent, 'cls', x, y, html, {w,h,...style})
  M.box = function (parent, cls, x, y, html, st) {
    const s = Object.assign({ position: 'absolute', left: x + 'px', top: y + 'px' }, st || {});
    if (s.w != null) { s.width = s.w + 'px'; delete s.w; }
    if (s.h != null) { s.height = s.h + 'px'; delete s.h; }
    return M.el('div', cls, parent, html, s);
  };
  // 一张 SVG：M.svg(parent, x, y, w, h, inner, viewBox?)
  M.svg = function (parent, x, y, w, h, inner, vb, cls) {
    const s = document.createElementNS(NS, 'svg');
    s.setAttribute('width', w); s.setAttribute('height', h);
    s.setAttribute('viewBox', vb || `0 0 ${w} ${h}`);
    s.setAttribute('class', 'svg ' + (cls || ''));
    s.style.position = 'absolute'; s.style.left = x + 'px'; s.style.top = y + 'px';
    s.innerHTML = inner || '';
    if (parent) parent.appendChild(s);
    return s;
  };
  M.q = (root, sel) => root.querySelector(sel);
  M.qa = (root, sel) => [...root.querySelectorAll(sel)];

  // ---------- 旁白时间（读 #cues，即 MR.words()）----------
  // lines: [{id, text}]，按讲解稿顺序；字幕块 chunks: [{line, a, b, text}]（a、b 为该行“发音字”下标）
  const SPEECH = /[㐀-鿿A-Za-z0-9]/;
  const speechOf = (s) => [...s].filter((c) => SPEECH.test(c)).join('');
  M.voice = function (lines) {
    const words = MR.words();
    const ch = [];
    for (const w of words) {
      const cs = [...w.word].filter((c) => SPEECH.test(c));
      cs.forEach((c, k) => ch.push({ c, s: w.start + ((w.end - w.start) * k) / cs.length, e: w.start + ((w.end - w.start) * (k + 1)) / cs.length }));
    }
    const at = {};
    let i = 0;
    for (const l of lines) {
      const sp = speechOf(l.text);
      if (ch.slice(i, i + sp.length).map((x) => x.c).join('') !== sp)
        throw new Error(`Ming.voice: 第 ${l.id} 句与 #cues（旁白逐词时间）对不上：${sp.slice(0, 12)}… vs ${ch.slice(i, i + 12).map((x) => x.c).join('')}`);
      at[l.id] = { i0: i, sp };
      i += sp.length;
    }
    // T(行号) = 该句开始；T(行号, '词', 第几次, 'end') = 说到这个词的时刻
    const T = function (id, needle, nth, edge) {
      const L = at[id];
      if (!L) throw new Error('Ming.T: 没有第 ' + id + ' 句');
      if (needle == null) return ch[L.i0].s;
      const nd = speechOf(String(needle));
      let k = -1, from = 0;
      for (let n = 0; n < (nth || 1); n++) { k = L.sp.indexOf(nd, from); if (k < 0) break; from = k + 1; }
      if (k < 0) throw new Error(`Ming.T: 第 ${id} 句里没有「${needle}」`);
      return edge === 'end' ? ch[L.i0 + k + nd.length - 1].e : ch[L.i0 + k].s;
    };
    T.end = (id) => { const L = at[id]; return ch[L.i0 + L.sp.length - 1].e; };
    T.char = (id, k, edge) => { const L = at[id]; const x = ch[L.i0 + Math.min(k, L.sp.length - 1)]; return edge === 'end' ? x.e : x.s; };
    T.last = () => ch[ch.length - 1].e;
    return T;
  };

  // 字幕：每块在说出第一个字时出现，最后一个字说完后多留一会儿，下一块出现前收起
  M.subtitles = function (tl, T, chunks, parent) {
    const times = chunks.map((c) => ({ c, s: T.char(c.line, c.a), e: T.char(c.line, c.b - 1, 'end') }));
    times.forEach((x, k) => {
      const next = times[k + 1];
      const end = Math.min(next ? next.s - 0.04 : x.e + 1.2, x.e + 0.7);
      const el = M.el('div', 'sub', parent, x.c.text.replace(/\n/g, '<br>'));
      el.setAttribute('data-id', 'sub-' + k);
      tl.fromTo(el, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.14, ease: 'power2.out', immediateRender: false }, Math.max(0, x.s - 0.06));
      tl.fromTo(el, { opacity: 1 }, { opacity: 0, duration: 0.1, ease: 'none', immediateRender: false }, Math.max(x.s + 0.1, end - 0.1));
    });
    return times;
  };

  // ---------- 纸纹（固定层，加载时画一次）----------
  M.paper = function (canvas, seed) {
    const W = (canvas.width = M.W), H = (canvas.height = canvas.dataset.h ? +canvas.dataset.h : M.H);
    const g = canvas.getContext('2d'), r = MR.random(seed || 3);
    g.fillStyle = M.C.paper; g.fillRect(0, 0, W, H);
    // 大块的明暗起伏
    for (let i = 0; i < 26; i++) {
      const x = r() * W, y = r() * H, rad = 200 + r() * 420;
      const gr = g.createRadialGradient(x, y, 0, x, y, rad);
      const dark = r() < 0.5;
      gr.addColorStop(0, dark ? 'rgba(150,120,80,0.07)' : 'rgba(255,250,238,0.10)');
      gr.addColorStop(1, 'rgba(0,0,0,0)');
      g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    // 纤维
    g.lineCap = 'round';
    for (let i = 0; i < 900; i++) {
      const x = r() * W, y = r() * H, len = 8 + r() * 46, a = r() * Math.PI;
      g.strokeStyle = r() < 0.6 ? `rgba(120,95,60,${0.05 + r() * 0.08})` : `rgba(255,252,242,${0.12 + r() * 0.15})`;
      g.lineWidth = 0.6 + r() * 1.1;
      g.beginPath(); g.moveTo(x, y);
      g.quadraticCurveTo(x + Math.cos(a) * len * 0.5 + (r() - 0.5) * 8, y + Math.sin(a) * len * 0.5 + (r() - 0.5) * 8, x + Math.cos(a) * len, y + Math.sin(a) * len);
      g.stroke();
    }
    // 细颗粒
    const img = g.getImageData(0, 0, W, H), d = img.data;
    for (let p = 0; p < d.length; p += 4) { const n = (r() - 0.5) * 14; d[p] += n; d[p + 1] += n; d[p + 2] += n * 0.9; }
    g.putImageData(img, 0, 0);
    // 四角压暗
    const v = g.createRadialGradient(W / 2, H * 0.45, H * 0.35, W / 2, H * 0.45, H * 0.85);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(80,55,25,0.20)');
    g.fillStyle = v; g.fillRect(0, 0, W, H);
  };

  // ---------- 墨晕图（canvas → dataURL，按参数缓存）----------
  const inkCache = {};
  M.ink = function (o) {
    o = Object.assign({ size: 800, seed: 1, color: '31,26,21', n: 60, spread: 0.28, alpha: 0.5, rim: 0.35, soft: 0.6 }, o || {});
    const key = JSON.stringify(o);
    if (inkCache[key]) return inkCache[key];
    const c = document.createElement('canvas');
    const S = (c.width = c.height = o.size), g = c.getContext('2d'), r = MR.random(o.seed);
    let x = S / 2, y = S / 2;
    for (let i = 0; i < o.n; i++) {
      const rad = S * (0.06 + r() * 0.16) * (1 - (i / o.n) * 0.4);
      x += (r() - 0.5) * S * o.spread * 0.5; y += (r() - 0.5) * S * o.spread * 0.5;
      x = Math.min(S * 0.75, Math.max(S * 0.25, x)); y = Math.min(S * 0.75, Math.max(S * 0.25, y));
      const gr = g.createRadialGradient(x, y, rad * (1 - o.soft), x, y, rad);
      const a = o.alpha * (0.5 + r() * 0.5);
      gr.addColorStop(0, `rgba(${o.color},${a})`);
      gr.addColorStop(0.85, `rgba(${o.color},${a * 0.8})`);
      gr.addColorStop(1, `rgba(${o.color},0)`);
      g.fillStyle = gr; g.beginPath(); g.arc(x, y, rad, 0, Math.PI * 2); g.fill();
      if (o.rim > 0) { // 湿边：边缘一圈略深
        g.strokeStyle = `rgba(${o.color},${o.rim * a * 0.5})`; g.lineWidth = 2 + r() * 3;
        g.beginPath(); g.arc(x, y, rad * 0.93, 0, Math.PI * 2); g.stroke();
      }
    }
    return (inkCache[key] = c.toDataURL('image/png'));
  };
  // 一整片铺满的墨（转场用）：中心实、边缘碎
  M.inkFlood = function (seed, color) {
    return M.ink({ size: 1200, seed, color: color || '31,26,21', n: 140, spread: 0.5, alpha: 0.95, rim: 0.4, soft: 0.35 });
  };

  // ---------- 远山（SVG 字符串）----------
  M.mountains = function (w, h, seed, o) {
    o = Object.assign({ layers: 3, color: '#1f1a15', top: 0.25, amp: 0.3 }, o || {});
    const r = MR.random(seed);
    let out = '<defs>';
    for (let l = 0; l < o.layers; l++)
      out += `<linearGradient id="mg${seed}_${l}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${o.color}" stop-opacity="${0.16 + l * 0.12}"/><stop offset="1" stop-color="${o.color}" stop-opacity="0"/></linearGradient>`;
    out += '</defs>';
    for (let l = 0; l < o.layers; l++) {
      const base = h * (o.top + l * 0.16), pts = [];
      const n = 7 + Math.floor(r() * 4);
      for (let i = 0; i <= n; i++) pts.push([(i / n) * w, base + (r() - 0.6) * h * o.amp * (1 - l * 0.2)]);
      let d = `M0,${h} L0,${pts[0][1]}`;
      for (let i = 1; i < pts.length; i++) {
        const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
        d += ` Q${(x0 + x1) / 2 + (r() - 0.5) * 40},${Math.min(y0, y1) - r() * h * 0.08} ${x1},${y1}`;
      }
      d += ` L${w},${h} Z`;
      out += `<path d="${d}" fill="url(#mg${seed}_${l})"/>`;
    }
    return out;
  };

  // ---------- 印章 ----------
  let grain = null;
  M.grain = function () { // 斑驳的遮罩（印泥不匀）
    if (grain) return grain;
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d'), r = MR.random(11);
    g.fillStyle = '#000'; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(0,0,0,${r()})`; g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.arc(r() * 256, r() * 256, 0.5 + r() * 2.6, 0, 7); g.fill(); }
    return (grain = c.toDataURL());
  };
  // M.seal(parent, '壹', {x, y, size, zhu, rot})
  M.seal = function (parent, text, o) {
    o = Object.assign({ x: 0, y: 0, size: 120, zhu: false, rot: -4, row: false }, o || {});
    const chars = [...text];
    if (o.row) { // 横排长条章（短语用）
      const fs = o.size * 0.62;
      return M.box(parent, 'seal' + (o.zhu ? ' zhu' : ''), o.x, o.y, `<span style="font-size:${fs}px;white-space:nowrap;letter-spacing:${fs * 0.08}px">${text}</span>`, {
        h: o.size, padding: `0 ${o.size * 0.28}px`, boxSizing: 'border-box', rotate: o.rot + 'deg',
        maskImage: `url(${M.grain()})`, webkitMaskImage: `url(${M.grain()})`, maskSize: '180px', webkitMaskSize: '180px' });
    }
    const cols = chars.length >= 3 ? 2 : 1, rows = Math.ceil(chars.length / cols);
    const fs = (o.size * 0.78) / Math.max(rows, cols);
    // 印文从右往左竖读
    const order = [];
    for (let c = cols - 1; c >= 0; c--) for (let rr = 0; rr < rows; rr++) order.push([rr, c]);
    const cells = new Array(rows * cols).fill('');
    chars.forEach((ch, k) => { const [rr, c] = order[k]; cells[rr * cols + c] = ch; });
    const html = cells.map((ch) => `<span style="font-size:${fs}px">${ch}</span>`).join('');
    const e = M.box(parent, 'seal' + (o.zhu ? ' zhu' : ''), o.x, o.y, html, {
      w: o.size, h: o.size * (chars.length === 2 && cols === 1 ? 1.6 : 1), gridTemplateColumns: `repeat(${cols}, 1fr)`,
      padding: o.size * 0.08 + 'px', boxSizing: 'border-box', rotate: o.rot + 'deg',
      maskImage: `url(${M.grain()})`, webkitMaskImage: `url(${M.grain()})`, maskSize: '180px', webkitMaskSize: '180px',
    });
    return e;
  };

  // ---------- 逐字书写 ----------
  M.chars = function (el, text) {
    el.innerHTML = [...text].map((c) => (c === '\n' ? '<br>' : `<span class="ch">${c === ' ' ? '&nbsp;' : c}</span>`)).join('');
    return M.qa(el, '.ch');
  };
  // 笔画感：每个字从上到下（竖写）或从左到右被“写”出来，伴随轻微收缩
  M.write = function (tl, spans, t, o) {
    o = Object.assign({ dur: 0.38, stagger: 0.16, dir: 'down' }, o || {});
    const from = o.dir === 'down' ? 'inset(0% 0% 100% 0%)' : 'inset(0% 100% 0% 0%)';
    spans.forEach((s, k) => {
      gsap.set(s, { clipPath: from, scale: 1.08, opacity: 0.2 });
      tl.fromTo(s, { clipPath: from, scale: 1.08, opacity: 0.2 }, { clipPath: 'inset(-10% -10% -10% -10%)', scale: 1, opacity: 1, duration: o.dur, ease: 'power2.out', immediateRender: false }, t + k * o.stagger);
    });
    return t + (spans.length - 1) * o.stagger + o.dur;
  };

  // ---------- 补间小工具（都用 fromTo + immediateRender:false，跳帧也对）----------
  M.bind = function (tl) {
    const fx = {};
    // 出现：fx.in(el, t, {from}, {to}, dur, ease)
    fx.in = (el, t, from, to, dur, ease) => {
      gsap.set(el, from);
      tl.fromTo(el, from, Object.assign({ duration: dur == null ? 0.6 : dur, ease: ease || 'expo.out', immediateRender: false }, to), Math.max(0, t));
      return t;
    };
    fx.to = (el, t, from, to, dur, ease) => {
      tl.fromTo(el, from, Object.assign({ duration: dur == null ? 0.5 : dur, ease: ease || 'power2.inOut', immediateRender: false }, to), Math.max(0, t));
      return t;
    };
    fx.pop = (el, t, dur, bounce) => fx.in(el, t, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1 }, dur || 0.5, MR.spring(bounce == null ? 0.18 : bounce));
    fx.fade = (el, t, dur) => fx.in(el, t, { opacity: 0 }, { opacity: 1 }, dur || 0.5, 'power1.out');
    fx.rise = (el, t, dist, dur) => fx.in(el, t, { opacity: 0, y: dist == null ? 40 : dist }, { opacity: 1, y: 0 }, dur || 0.7);
    fx.drop = (el, t, dist, dur) => fx.in(el, t, { opacity: 0, y: -(dist == null ? 60 : dist) }, { opacity: 1, y: 0 }, dur || 0.55, MR.spring(0.12));
    fx.out = (el, t, dur) => fx.to(el, t, { opacity: 1 }, { opacity: 0 }, dur || 0.3, 'power2.in');
    // 印章落下：从大到小砸下来，落点 = t
    fx.stamp = (el, t, gain) => {
      gsap.set(el, { scale: 2.2, opacity: 0 });
      tl.fromTo(el, { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: 'power4.in', immediateRender: false }, Math.max(0, t - 0.22));
      MR.sfx('stamp', Math.max(0, t), { gain: gain || 0.7 });
      return t;
    };
    // SVG 描边画出：path 需带 pathLength="1"
    fx.draw = (el, t, dur, ease) => {
      const els = el.length != null && !el.tagName ? [...el] : [el];
      els.forEach((e) => { gsap.set(e, { strokeDasharray: 1, strokeDashoffset: 1 }); });
      tl.fromTo(els, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: dur || 1, ease: ease || 'power2.inOut', immediateRender: false }, Math.max(0, t));
      return t;
    };
    // 计数：把 el 的文字从 a 计到 b
    fx.count = (el, t, a, b, dur, fmt) => {
      const o = { v: a };
      const f = fmt || ((v) => String(Math.round(v)));
      el.textContent = f(a);
      tl.fromTo(o, { v: a }, { v: b, duration: dur || 1.2, ease: 'expo.out', immediateRender: false, onUpdate: () => { el.textContent = f(o.v); } }, Math.max(0, t));
      return t;
    };
    return fx;
  };

  // ---------- 平滑曲线 ----------
  M.smooth = function (pts, closed) {
    if (pts.length < 3) return 'M' + pts.map((p) => p.join(',')).join(' L');
    const P = closed ? [pts[pts.length - 1], ...pts, pts[0], pts[1]] : [pts[0], ...pts, pts[pts.length - 1]];
    let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
    for (let i = 1; i < P.length - 2; i++) {
      const p0 = P[i - 1], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
    }
    return d + (closed ? ' Z' : '');
  };

  // ---------- 地图投影 ----------
  // M.proj({lon0, lon1, lat0, lat1, w, h}) → ([lon,lat]) => [x,y]
  M.proj = function (o) {
    const k = (lon, lat) => [((lon - o.lon0) / (o.lon1 - o.lon0)) * o.w, ((o.lat1 - lat) / (o.lat1 - o.lat0)) * o.h];
    k.path = (pts, closed) => M.smooth(pts.map((p) => k(p[0], p[1])), closed);
    return k;
  };
  // 地理数据（经纬度，示意精度）
  M.geo = {
    // 1344 年前后的黄河（1194 年起夺淮入海）
    huangheLower: [[112.6, 34.9], [113.6, 34.95], [114.35, 34.85], [115.0, 34.78], [115.6, 34.78], [116.4, 34.55], [117.2, 34.28], [117.9, 33.95], [118.6, 33.75], [119.1, 33.55], [119.8, 33.75], [120.3, 34.0]],
    huaihe: [[113.4, 32.4], [114.4, 32.42], [115.3, 32.55], [116.2, 32.5], [116.8, 32.62], [117.4, 32.92], [117.9, 32.95], [118.5, 33.08], [119.1, 33.5]],
    changjiang: [[115.6, 29.8], [116.4, 29.95], [117.0, 30.5], [117.8, 31.0], [118.4, 31.4], [118.8, 32.05], [119.4, 32.2], [120.3, 32.0], [121.0, 31.7], [121.8, 31.35]],
    coastEast: [[119.0, 36.0], [119.3, 35.5], [119.45, 35.0], [119.9, 34.6], [120.3, 34.15], [120.7, 33.3], [120.9, 32.6], [121.4, 32.05], [121.9, 31.3], [121.9, 30.6]],
    // 全国示意
    coast: [[124.2, 40.0], [122.2, 40.5], [121.2, 40.8], [119.6, 39.9], [118.2, 39.1], [117.7, 38.5], [118.6, 37.5], [119.3, 37.1], [120.7, 37.8], [122.5, 37.4], [121.0, 36.6], [120.3, 36.0], [119.3, 35.1], [120.3, 34.3], [120.9, 32.6], [121.9, 31.2], [121.9, 30.0], [121.5, 28.5], [120.3, 27.2], [119.5, 25.6], [118.0, 24.4], [116.5, 23.0], [114.2, 22.3], [111.0, 21.5], [110.2, 20.4], [109.6, 21.6], [108.1, 21.5]],
    huanghe: [[96.5, 35.0], [100.0, 36.0], [103.8, 36.1], [105.5, 37.5], [106.5, 39.5], [108.0, 40.8], [110.5, 40.6], [111.2, 39.4], [110.5, 37.0], [110.4, 35.0], [111.5, 34.8], [113.5, 34.9], [114.4, 34.85], [117.2, 34.3], [119.1, 33.6], [120.3, 34.0]],
    yangtze: [[97.0, 33.0], [100.0, 28.0], [102.0, 26.5], [104.5, 28.8], [106.5, 29.6], [108.4, 30.8], [110.4, 31.0], [111.3, 30.7], [112.5, 29.5], [114.3, 30.6], [116.0, 29.8], [117.0, 30.5], [118.8, 32.05], [120.3, 32.0], [121.8, 31.4]],
    city: {
      haozhou: [117.56, 32.87], yingzhou: [115.82, 32.9], xuzhou: [117.18, 34.27], kaifeng: [114.35, 34.8], jiqing: [118.78, 32.05],
      caozhou: [115.48, 35.24], baimao: [115.62, 34.86], jining: [116.59, 35.41], dongping: [116.3, 35.92], shanzhou: [116.08, 34.8],
      huanglinggang: [115.05, 34.8], dadu: [116.4, 39.9], shangdu: [116.18, 42.36], huaian: [119.1, 33.55], shouzhou: [116.78, 32.57],
    },
  };

  // ---------- 剪影（返回 SVG 片段，fill/stroke 都用 currentColor）----------
  const P2 = (p) => p[0].toFixed(1) + ',' + p[1].toFixed(1);
  const POSES = {
    //        头        颈        髋         膝1        脚1       膝2        脚2        肘1       手1       肘2       手2
    stand: { hd: [50, 26], n: [50, 44], p: [50, 108], k1: [45, 154], f1: [43, 200], k2: [55, 154], f2: [57, 200], e1: [37, 78], h1: [35, 110], e2: [63, 78], h2: [65, 110] },
    walk: { hd: [52, 26], n: [51, 44], p: [49, 108], k1: [40, 152], f1: [30, 198], k2: [58, 154], f2: [66, 199], e1: [42, 78], h1: [36, 104], e2: [60, 78], h2: [70, 100] },
    run: { hd: [64, 30], n: [59, 46], p: [47, 106], k1: [72, 136], f1: [66, 176], k2: [36, 148], f2: [16, 182], e1: [74, 72], h1: [88, 88], e2: [40, 72], h2: [28, 90] },
    bend: { hd: [80, 60], n: [70, 68], p: [40, 110], k1: [50, 155], f1: [50, 200], k2: [32, 156], f2: [24, 200], e1: [78, 92], h1: [88, 110], e2: [64, 96], h2: [78, 118] },
    ride: { hd: [50, 26], n: [50, 44], p: [46, 100], k1: [66, 108], f1: [62, 150], k2: [60, 110], f2: [56, 150], e1: [62, 70], h1: [76, 72], e2: [46, 74], h2: [66, 80] },
    reach: { hd: [52, 26], n: [51, 44], p: [49, 108], k1: [44, 154], f1: [42, 200], k2: [56, 154], f2: [58, 200], e1: [66, 64], h1: [86, 56], e2: [40, 78], h2: [36, 108] },
    sitread: { hd: [56, 30], n: [52, 46], p: [46, 100], k1: [66, 108], f1: [62, 150], k2: [60, 110], f2: [56, 150], e1: [66, 70], h1: [80, 60], e2: [60, 74], h2: [78, 66] },
  };
  M.person = function (o) {
    o = Object.assign({ pose: 'stand', hat: 'jin', robe: 34, w: 1, child: false, female: false, prop: null }, o || {});
    const P = POSES[o.pose];
    const L = o.child ? 9 : 11.5, A = o.child ? 7 : 9;
    const n = P.n, p = P.p;
    const dx = p[0] - n[0], dy = p[1] - n[1], len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len, px = -uy, py = ux;
    const sh = 15, hp = 15, hem = o.female ? 70 : o.robe;
    const q = (b, s, u) => [b[0] + px * s + ux * (u || 0), b[1] + py * s + uy * (u || 0)];
    const torso = [q(n, sh, 2), q(p, hp + 2), q(p, hp + 7, hem), q(p, -hp - 7, hem), q(p, -hp - 2), q(n, -sh, 2)];
    let s = '';
    // 腿
    const leg = (k, f) => `<path d="M${P2(p)} L${P2(k)} L${P2(f)}" fill="none" stroke="currentColor" stroke-width="${L}" stroke-linecap="round" stroke-linejoin="round"/>`;
    if (!o.female) s += leg(P.k1, P.f1) + leg(P.k2, P.f2);
    else s += `<path d="M${P2([P.f1[0] - 4, 200])} L${P2([P.f2[0] + 4, 200])}" stroke="currentColor" stroke-width="10" stroke-linecap="round"/>`;
    // 身子（袍子）
    s += `<path d="M${torso.map(P2).join(' L')} Z" fill="currentColor" stroke="currentColor" stroke-width="5" stroke-linejoin="round"/>`;
    // 胳膊
    const arm = (e, h, side) => `<path d="M${P2(q(n, side * (sh - 3), 5))} L${P2(e)} L${P2(h)}" fill="none" stroke="currentColor" stroke-width="${A}" stroke-linecap="round" stroke-linejoin="round"/>`;
    s += arm(P.e1, P.h1, 1) + arm(P.e2, P.h2, -1);
    // 脖子和头
    const hd = P.hd, hr = o.child ? 12.5 : 12.5;
    s += `<path d="M${P2(n)} L${P2([hd[0], hd[1] + 6])}" stroke="currentColor" stroke-width="9" stroke-linecap="round"/>`;
    s += `<circle cx="${hd[0]}" cy="${hd[1]}" r="${hr}" fill="currentColor"/>`;
    // 帽子 / 发式
    const [hx, hy] = hd;
    if (o.hat === 'li') s += `<path d="M${hx - 36},${hy - 2} L${hx - 6},${hy - 27} Q${hx},${hy - 31} ${hx + 6},${hy - 27} L${hx + 36},${hy - 2} Q${hx + 36},${hy + 2} ${hx + 30},${hy + 1} Q${hx},${hy - 8} ${hx - 30},${hy + 1} Q${hx - 36},${hy + 2} ${hx - 36},${hy - 2} Z" fill="currentColor"/>`;
    else if (o.hat === 'jin') s += `<circle cx="${hx - 2}" cy="${hy - 12}" r="6" fill="currentColor"/>`;
    else if (o.hat === 'futou') s += `<path d="M${hx - 12},${hy - 4} Q${hx - 12},${hy - 22} ${hx},${hy - 22} Q${hx + 12},${hy - 22} ${hx + 12},${hy - 4} Z" fill="currentColor"/><path d="M${hx - 50},${hy - 9} L${hx + 50},${hy - 9}" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>`;
    else if (o.hat === 'bun') s += `<circle cx="${hx + 1}" cy="${hy - 14}" r="8" fill="currentColor"/><path d="M${hx - 9},${hy - 6} Q${hx - 16},${hy + 10} ${hx - 10},${hy + 18}" stroke="currentColor" stroke-width="5" fill="none"/>`;
    else if (o.hat === 'kids') s += `<circle cx="${hx - 9}" cy="${hy - 10}" r="5" fill="currentColor"/><circle cx="${hx + 9}" cy="${hy - 10}" r="5" fill="currentColor"/>`;
    // 道具
    if (o.prop === 'hoe') s += `<path d="M${P2(P.h1)} L${P.h1[0] + 26},${P.h1[1] + 70}" stroke="currentColor" stroke-width="5" stroke-linecap="round"/><path d="M${P.h1[0] + 18},${P.h1[1] + 70} L${P.h1[0] + 44},${P.h1[1] + 62} L${P.h1[0] + 40},${P.h1[1] + 78} Z" fill="currentColor"/>`;
    if (o.prop === 'bucket') s += `<path d="M${P.h1[0]},${P.h1[1]} L${P.h1[0]},${P.h1[1] + 10}" stroke="currentColor" stroke-width="3"/><path d="M${P.h1[0] - 13},${P.h1[1] + 10} L${P.h1[0] + 13},${P.h1[1] + 10} L${P.h1[0] + 10},${P.h1[1] + 36} L${P.h1[0] - 10},${P.h1[1] + 36} Z" fill="currentColor"/>`;
    if (o.prop === 'flute') s += `<path d="M${hx + 6},${hy + 6} L${hx + 46},${hy + 22}" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>`;
    if (o.prop === 'stick') s += `<path d="M${P2(P.h1)} L${P.h1[0] + 50},${P.h1[1] - 40}" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>`;
    if (o.prop === 'book') s += `<path d="M${P.h1[0] - 4},${P.h1[1] - 16} l26,-6 l4,22 l-26,6 Z" fill="currentColor"/>`;
    return `<g>${s}</g>`;
  };

  // 正面坐着的皇帝（冕旒）：box 120×200
  M.emperor = function (o) {
    o = Object.assign({ child: false }, o || {});
    let s = '';
    s += `<path d="M30,52 Q60,40 90,52 L104,150 Q60,166 16,150 Z" fill="currentColor"/>`;   // 袍
    s += `<path d="M30,56 Q14,90 10,128 L30,132 Q34,96 42,70 Z" fill="currentColor"/><path d="M90,56 Q106,90 110,128 L90,132 Q86,96 78,70 Z" fill="currentColor"/>`; // 袖
    s += `<path d="M22,150 L98,150 L92,196 L28,196 Z" fill="currentColor"/>`;    // 下摆
    s += `<path d="M52,100 L68,100 L66,122 L54,122 Z" fill="var(--paper)" opacity=".55"/>`; // 笏
    s += `<circle cx="60" cy="30" r="15" fill="currentColor"/>`;
    s += `<rect x="34" y="8" width="52" height="6" rx="2" fill="currentColor"/>`;  // 冕板
    for (let i = 0; i < 6; i++) s += `<path d="M${38 + i * 8.8},14 L${38 + i * 8.8},26" stroke="currentColor" stroke-width="2"/><circle cx="${38 + i * 8.8}" cy="27" r="2" fill="currentColor"/>`;
    s += `<rect x="54" y="0" width="12" height="10" fill="currentColor"/>`;
    return `<g>${s}</g>`;
  };

  // 龙椅（正面）：box 360×400
  M.throne = function () {
    return `<g>
      <path d="M40,60 Q30,10 70,22 Q100,34 120,30 L240,30 Q260,34 290,22 Q330,10 320,60 L312,250 L48,250 Z" fill="url(#gold)"/>
      <path d="M86,70 L274,70 L266,236 L94,236 Z" fill="none" stroke="#7a5a1e" stroke-width="5" opacity=".6"/>
      <circle cx="180" cy="150" r="46" fill="none" stroke="#7a5a1e" stroke-width="5" opacity=".55"/>
      <path d="M150,150 Q180,110 210,150 Q180,190 150,150 Z" fill="#7a5a1e" opacity=".45"/>
      <path d="M8,200 Q4,180 30,182 L56,186 L56,300 L14,300 Z" fill="url(#gold)"/>
      <path d="M352,200 Q356,180 330,182 L304,186 L304,300 L346,300 Z" fill="url(#gold)"/>
      <path d="M20,262 L340,262 L350,300 L10,300 Z" fill="url(#gold)"/>
      <path d="M24,300 L336,300 L324,330 L36,330 Z" fill="#8a6524"/>
      <path d="M44,330 L70,330 L66,396 L40,396 Z M290,330 L316,330 L320,396 L294,396 Z" fill="#8a6524"/>
      <path d="M0,396 L360,396" stroke="#8a6524" stroke-width="6"/>
    </g>`;
  };
  M.goldDefs = '<defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2c172"/><stop offset=".55" stop-color="#b8903f"/><stop offset="1" stop-color="#8a6524"/></linearGradient></defs>';

  // 水牛（侧面，朝右）：box 400×230；rider 为骑在背上的人
  M.buffalo = function (o) {
    o = Object.assign({ rider: null, book: false, horns: true }, o || {});
    let s = '';
    s += `<path d="M72,118 C58,130 54,152 58,180 L63,181 C64,158 68,140 78,126 Z" fill="currentColor"/>`; // 尾
    s += `<path d="M70,120 C62,92 82,70 122,64 C172,56 240,58 290,66 C318,70 334,84 342,100 C352,104 364,110 372,120 C384,132 388,148 382,162 C376,172 362,174 352,168 C342,162 334,152 326,148 C322,162 318,172 316,180 L314,222 L300,224 L297,188 C290,190 282,190 276,188 L274,222 L260,224 L257,186 C230,190 190,192 160,188 L156,222 L142,224 L139,184 C132,182 124,180 118,178 L114,220 L100,222 L97,170 C85,162 75,148 70,120 Z" fill="currentColor"/>`;
    if (o.horns) { // 水牛标志性的弯角：向后上方扫成新月
      s += `<path d="M350,108 C326,104 300,92 286,72 C278,58 284,44 296,40 C292,56 302,76 330,90 C342,96 356,98 364,100 Z" fill="currentColor"/>`;
      s += `<path d="M362,104 C352,88 352,68 366,52 C372,46 380,48 380,54 C368,66 370,84 378,100 Z" fill="currentColor" opacity=".6"/>`;
    }
    s += `<path d="M340,104 L326,98 L332,112 Z" fill="currentColor"/>`;  // 耳
    s += `<circle cx="358" cy="124" r="3.2" fill="var(--paper)" opacity=".7"/>`; // 眼
    if (o.book) s += `<path d="M318,50 l22,-14 l14,22 l-22,14 Z" fill="currentColor"/><path d="M322,50 l18,-11" stroke="var(--paper)" stroke-width="2" opacity=".6"/><path d="M332,58 L334,64" stroke="currentColor" stroke-width="2"/>`;
    if (o.rider) { const k = o.riderScale || 0.92; s += `<g transform="translate(${170 - 50 * k},${62 - 100 * k}) scale(${k})">${o.rider}</g>`; }
    return `<g>${s}</g>`;
  };

  // 茅草屋：box 320×250
  M.hut = function (o) {
    o = Object.assign({ glow: false }, o || {});
    let s = '';
    s += `<path d="M48,120 L272,120 L272,236 L48,236 Z" fill="currentColor"/>`;
    s += `<path d="M138,160 L182,160 L182,236 L138,236 Z" fill="var(--paper)" opacity=".25" class="door"/>`;
    s += `<path d="M76,150 L118,150 L118,186 L76,186 Z" fill="var(--paper)" opacity=".25" class="win"/>`;
    s += `<path d="M206,150 L248,150 L248,186 L206,186 Z" fill="var(--paper)" opacity=".25" class="win"/>`;
    s += `<path d="M8,132 Q90,60 160,26 Q230,60 312,132 Q240,124 160,124 Q80,124 8,132 Z" fill="currentColor"/>`;
    const r = MR.random(5);
    for (let i = 0; i < 22; i++) { const x = 16 + i * 13.5; s += `<path d="M${x},${130 - Math.abs(x - 160) * 0.05} l${(r() - 0.5) * 6},${10 + r() * 9}" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>`; }
    s += `<path d="M150,30 L170,30 L168,16 L152,18 Z" fill="currentColor"/>`;
    s += `<path d="M10,238 L310,238" stroke="currentColor" stroke-width="6" stroke-linecap="round"/>`;
    return `<g>${s}</g>`;
  };

  // 骆驼（侧面朝右）：box 420×340；腿单独成组便于抖动
  M.camel = function () {
    // 腿：大腿 + 小腿，膝盖处略折
    const leg = (x, y) => `M${x},${y} L${x + 4},${y + 62} L${x - 2},${y + 124}`;
    const legs = `<g class="legs"><path d="${leg(118, 206)} ${leg(150, 210)} ${leg(290, 204)} ${leg(320, 198)}" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/></g>`;
    return `<g>${legs}
      <path d="M80,190 C76,150 104,140 128,128 C150,82 186,86 196,128 C214,140 226,140 240,128 C258,84 296,86 306,130 C326,138 340,150 352,132 C362,112 360,80 366,60 C370,44 394,40 404,56 C410,66 404,74 396,74 C388,80 384,100 384,124 C384,160 362,190 330,206 C300,222 140,226 108,214 C92,208 82,200 80,190 Z" fill="currentColor"/>
      <path d="M82,186 C68,196 64,214 68,236" stroke="currentColor" stroke-width="7" fill="none" stroke-linecap="round"/>
      <path d="M150,96 Q120,150 132,196 Q166,212 196,196 Q206,150 186,96 Z" fill="#6b5f52"/>
      <path d="M262,96 Q238,150 250,196 Q282,210 310,196 Q318,150 300,96 Z" fill="#6b5f52"/>
      <path d="M136,150 L198,150 M248,150 L314,150" stroke="var(--paper)" stroke-width="3" opacity=".5"/>
      <path d="M168,92 Q220,60 280,92" stroke="#6b5f52" stroke-width="10" fill="none"/>
    </g>`;
  };

  // 独眼石人（正面）：box 260×420
  M.stoneMan = function () {
    return `<g>
      <path d="M78,20 Q130,4 182,20 L190,122 Q130,138 70,122 Z" fill="#5c564d"/>
      <circle class="eye" cx="130" cy="72" r="17" fill="var(--cinnabar)"/>
      <path d="M100,104 L160,104" stroke="#2d2924" stroke-width="5" stroke-linecap="round"/>
      <path d="M40,140 Q130,118 220,140 L232,392 Q130,410 28,392 Z" fill="#5c564d"/>
      <path d="M40,150 Q24,250 32,330 L56,330 Q56,250 70,170 Z M220,150 Q236,250 228,330 L204,330 Q204,250 190,170 Z" fill="#4c463e"/>
      <path d="M96,40 l18,30 l-10,22 M196,210 l-30,40 l10,36 l-22,30 M70,260 l26,26 l-6,30" stroke="#2d2924" stroke-width="3" fill="none" opacity=".7"/>
      <path d="M20,396 L240,396" stroke="#3a352f" stroke-width="8" stroke-linecap="round"/>
    </g>`;
  };

  // 饭碗：box 160×110
  M.bowl = function (o) {
    o = Object.assign({ rice: true }, o || {});
    return `<g>${o.rice ? '<path d="M24,40 Q80,0 136,40 Z" fill="var(--paper)" stroke="currentColor" stroke-width="4"/>' : ''}
      <path d="M10,40 L150,40 Q146,92 80,96 Q14,92 10,40 Z" fill="currentColor"/>
      <path d="M56,96 L104,96 L100,108 L60,108 Z" fill="currentColor"/>
      <path d="M22,54 Q80,62 138,54" stroke="var(--paper)" stroke-width="3" opacity=".35" fill="none"/></g>`;
  };
  // 方孔铜钱：box 100×100
  M.coin = function () {
    return `<g><circle cx="50" cy="50" r="46" fill="#b8903f" stroke="#7a5a1e" stroke-width="4"/><circle cx="50" cy="50" r="36" fill="none" stroke="#7a5a1e" stroke-width="2" opacity=".6"/><rect x="38" y="38" width="24" height="24" fill="var(--paper)" stroke="#7a5a1e" stroke-width="3"/></g>`;
  };
  // 羊：box 120×90
  M.sheep = function () {
    return `<g><path d="M20,40 Q16,18 40,18 Q52,6 66,16 Q86,8 94,26 Q110,30 104,48 Q106,64 86,62 L30,62 Q12,60 20,40 Z" fill="var(--paper)" stroke="currentColor" stroke-width="4"/>
      <path d="M98,30 Q116,28 116,42 Q114,52 102,50 Z" fill="currentColor"/>
      <path d="M36,62 L34,86 M48,62 L48,86 M76,62 L76,86 M88,62 L90,86" stroke="currentColor" stroke-width="6" stroke-linecap="round"/></g>`;
  };
  // 书：box 120×150；官帽：box 160×90；名牌：box 100×160
  M.iconBook = function () { return `<g><path d="M10,10 L100,10 Q112,10 112,22 L112,140 L22,140 Q10,140 10,128 Z" fill="currentColor"/><path d="M22,128 L112,128" stroke="var(--paper)" stroke-width="3" opacity=".5"/><rect x="34" y="28" width="22" height="80" fill="var(--paper)" opacity=".85"/><path d="M40,44 L50,44 M40,62 L50,62 M40,80 L50,80" stroke="currentColor" stroke-width="3"/></g>`; };
  M.iconHat = function () { return `<g><path d="M48,74 Q46,20 80,18 Q114,20 112,74 Z" fill="currentColor"/><path d="M40,74 L120,74 L116,86 L44,86 Z" fill="currentColor"/><path d="M2,52 L158,52" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><circle cx="2" cy="52" r="6" fill="currentColor"/><circle cx="158" cy="52" r="6" fill="currentColor"/></g>`; };
  M.iconTag = function () { return `<g><path d="M50,4 L50,26" stroke="currentColor" stroke-width="4"/><path d="M20,26 L80,26 L80,140 L50,156 L20,140 Z" fill="currentColor"/><circle cx="50" cy="40" r="6" fill="var(--paper)"/><path d="M38,64 L62,64 M38,90 L62,90 M38,116 L62,116" stroke="var(--paper)" stroke-width="5" opacity=".35" stroke-dasharray="4 6"/></g>`; };

  // 一圈虚线框 + 打叉（朱砂）
  M.cross = function (w, h) {
    return `<path pathLength="1" d="M${w * 0.12},${h * 0.12} L${w * 0.88},${h * 0.88}" stroke="var(--cinnabar)" stroke-width="16" stroke-linecap="round" fill="none"/><path pathLength="1" d="M${w * 0.88},${h * 0.12} L${w * 0.12},${h * 0.88}" stroke="var(--cinnabar)" stroke-width="16" stroke-linecap="round" fill="none"/>`;
  };
  M.check = function (w, h) {
    return `<path pathLength="1" d="M${w * 0.15},${h * 0.55} L${w * 0.42},${h * 0.8} L${w * 0.88},${h * 0.2}" stroke="var(--ink)" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
  };

  // ---------- 镜头 ----------
  // 世界里的格子（每格一屏 1080×1920），镜头在格子间推拉
  M.stage = function (world) {
    const st = { panels: {} };
    st.panel = (id, gx, gy) => {
      const p = M.el('div', 'panel', world);
      p.id = 'p-' + id; p.setAttribute('data-id', 'shot-' + id);
      p.style.left = gx * 1240 + 'px'; p.style.top = gy * 2080 + 'px';
      st.panels[id] = { el: p, x: gx * 1240, y: gy * 2080 };
      return p;
    };
    // 可见窗口：只在需要时显示，渲染更快
    st.show = (tl, id, t0, t1) => {
      const el = st.panels[id].el;
      tl.set(el, { visibility: 'visible' }, Math.max(0, t0));
      if (t1 != null) tl.set(el, { visibility: 'hidden' }, t1);
    };
    // 某格内的世界坐标
    st.at = (id, x, y) => [st.panels[id].x + x, st.panels[id].y + y];
    return st;
  };
})();

// =====================================================================
// 扩展：后续章节常用的剪影与地理数据（和尚、寺庙、骑马将领、士兵、城墙、楼船、宫殿；明初城市与湖泊）
// =====================================================================
(function () {
  const M = window.Ming;
  // 人物的补充：头盔（kui）、光头（bald）、道具 spear / flag / beads；袈裟用 o.monk
  const person0 = M.person;
  M.person = function (o) {
    o = Object.assign({}, o || {});
    const hat = o.hat, prop = o.prop;
    if (hat === 'kui' || hat === 'bald') o.hat = 'none';
    if (['spear', 'flag', 'beads'].includes(prop)) o.prop = null;
    if (o.monk) { o.robe = Math.max(o.robe || 0, 62); }
    let s = person0(o).replace(/^<g>|<\/g>$/g, '');
    const P = { stand: [50, 26, 35, 110], walk: [52, 26, 36, 104], run: [64, 30, 88, 88], bend: [80, 60, 88, 110], ride: [50, 26, 76, 72], reach: [52, 26, 86, 56], sitread: [56, 30, 80, 60] }[o.pose || 'stand'];
    const [hx, hy, ax, ay] = P;
    if (hat === 'kui') s += `<path d="M${hx - 15},${hy - 2} Q${hx - 15},${hy - 22} ${hx},${hy - 23} Q${hx + 15},${hy - 22} ${hx + 15},${hy - 2} L${hx + 18},${hy + 2} L${hx - 18},${hy + 2} Z" fill="currentColor"/><path d="M${hx},${hy - 22} Q${hx + 4},${hy - 40} ${hx - 6},${hy - 50}" stroke="var(--cinnabar)" stroke-width="4" fill="none" stroke-linecap="round"/>`;
    if (o.monk) s += `<path d="M${hx - 12},${hy + 22} L${hx + 14},${hy + 92}" stroke="var(--cinnabar)" stroke-width="7" opacity=".85"/>`;
    if (prop === 'spear') s += `<path d="M${ax},${ay + 60} L${ax + 6},${ay - 90}" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M${ax + 6},${ay - 90} l-6,-4 l6,-22 l6,22 Z" fill="currentColor"/>`;
    if (prop === 'flag') s += `<path d="M${ax},${ay + 60} L${ax + 4},${ay - 110}" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M${ax + 4},${ay - 110} L${ax + 60},${ay - 96} L${ax + 4},${ay - 78} Z" fill="var(--cinnabar)"/>`;
    if (prop === 'beads') s += `<circle cx="${ax}" cy="${ay - 4}" r="9" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="2 3"/>`;
    return `<g>${s}</g>`;
  };
  // 和尚：光头、长袍、袈裟带、念珠
  M.monk = (o) => M.person(Object.assign({ pose: 'stand', hat: 'bald', monk: true, prop: 'beads' }, o || {}));
  // 士兵：头盔、长枪
  M.soldier = (o) => M.person(Object.assign({ pose: 'stand', hat: 'kui', robe: 26, prop: 'spear' }, o || {}));

  // 马（侧面朝右）：box 420×300；rider 为骑手（M.person({pose:'ride'})），flag 为马上的旗
  M.horse = function (o) {
    o = Object.assign({ rider: null, riderScale: 0.95 }, o || {});
    let s = '';
    s += `<path d="M98,130 C70,140 58,182 66,232 C78,200 86,172 102,152 Z" fill="currentColor"/>`;
    s += `<path d="M300,190 L306,240 L300,286 M318,184 L332,236 L340,284 M128,190 L120,240 L128,286 M150,192 L162,242 L154,286" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
    s += `<path d="M95,140 C95,105 130,92 175,95 L285,92 C305,90 318,80 330,62 C340,44 355,30 372,24 L380,10 L386,26 C398,32 410,46 414,60 C416,70 408,74 398,70 C390,66 380,64 372,70 C362,90 352,112 340,128 C332,150 326,170 318,186 C300,196 270,198 240,196 L170,196 C140,196 112,190 100,176 C94,166 94,152 95,140 Z" fill="currentColor"/>`;
    s += `<path d="M330,62 C320,70 312,84 300,92 L310,96 C322,86 330,76 338,66 Z" fill="currentColor" opacity=".7"/>`;
    s += `<circle cx="392" cy="44" r="3" fill="var(--paper)" opacity=".7"/>`;
    s += `<path d="M180,96 Q205,86 232,96 L228,112 Q205,104 184,112 Z" fill="var(--cinnabar)" opacity=".8"/>`;
    if (o.rider) { const k = o.riderScale; s += `<g transform="translate(${205 - 46 * k},${96 - 100 * k}) scale(${k})">${o.rider}</g>`; }
    return `<g>${s}</g>`;
  };
  // 将领骑马
  M.general = (o) => M.horse({ rider: M.person(Object.assign({ pose: 'ride', hat: 'kui', prop: 'flag' }, o || {})) });

  // 寺庙：box 400×300
  M.temple = function () {
    return `<g>
      <path d="M20,290 L380,290 L370,268 L30,268 Z" fill="currentColor"/>
      <rect x="70" y="150" width="260" height="118" fill="currentColor"/>
      <rect x="170" y="190" width="60" height="78" fill="var(--paper)" opacity=".28"/>
      <rect x="92" y="180" width="44" height="50" fill="var(--paper)" opacity=".2"/><rect x="264" y="180" width="44" height="50" fill="var(--paper)" opacity=".2"/>
      <path d="M0,160 Q40,150 60,128 L340,128 Q360,150 400,160 Q380,150 200,146 Q20,150 0,160 Z" fill="currentColor"/>
      <path d="M50,128 Q90,110 120,82 L280,82 Q310,110 350,128 Z" fill="currentColor"/>
      <path d="M100,82 Q140,64 160,40 L240,40 Q260,64 300,82 Z" fill="currentColor"/>
      <rect x="168" y="96" width="64" height="24" fill="var(--cinnabar)"/>
      <path d="M200,40 L200,18" stroke="currentColor" stroke-width="6"/><circle cx="200" cy="14" r="6" fill="currentColor"/>
    </g>`;
  };
  // 宫殿（重檐）：box 520×320
  M.palace = function () {
    return `<g>
      <path d="M0,320 L520,320 L500,290 L20,290 Z" fill="currentColor"/>
      <path d="M200,320 L320,320 L300,290 L220,290 Z" fill="var(--paper)" opacity=".18"/>
      <rect x="60" y="170" width="400" height="120" fill="currentColor"/>
      ${[0, 1, 2, 3, 4].map((i) => `<rect x="${84 + i * 76}" y="196" width="40" height="94" fill="var(--paper)" opacity=".16"/>`).join('')}
      <path d="M10,178 Q60,170 80,140 L440,140 Q460,170 510,178 Q470,168 260,164 Q50,168 10,178 Z" fill="currentColor"/>
      <path d="M70,140 Q120,120 150,92 L370,92 Q400,120 450,140 Z" fill="currentColor"/>
      <path d="M40,96 Q100,86 130,56 L390,56 Q420,86 480,96 Q440,88 260,86 Q80,88 40,96 Z" fill="currentColor"/>
      <path d="M140,56 Q190,36 220,10 L300,10 Q330,36 380,56 Z" fill="currentColor"/>
      <rect x="226" y="104" width="68" height="24" fill="var(--gold)"/>
    </g>`;
  };
  // 城墙与城楼：box 600×260
  M.cityWall = function () {
    let crenel = '';
    for (let x = 0; x < 600; x += 30) crenel += `<rect x="${x}" y="110" width="18" height="16" fill="currentColor"/>`;
    return `<g>${crenel}
      <rect x="0" y="126" width="600" height="134" fill="currentColor"/>
      <path d="M260,260 L260,196 Q300,160 340,196 L340,260 Z" fill="var(--paper)" opacity=".28"/>
      <rect x="220" y="70" width="160" height="56" fill="currentColor"/>
      <path d="M200,76 Q240,64 256,40 L344,40 Q360,64 400,76 Z" fill="currentColor"/>
      <path d="M232,40 Q262,26 276,8 L324,8 Q338,26 368,40 Z" fill="currentColor"/>
      ${[0, 1, 2].map((i) => `<rect x="${240 + i * 46}" y="84" width="26" height="30" fill="var(--paper)" opacity=".2"/>`).join('')}
      <path d="M0,200 L600,200" stroke="var(--paper)" stroke-width="2" opacity=".12"/>
    </g>`;
  };
  // 楼船（战船）：box 420×260
  M.warship = function () {
    return `<g>
      <path d="M10,180 L410,180 Q396,230 340,240 L80,240 Q30,230 10,180 Z" fill="currentColor"/>
      <rect x="110" y="120" width="200" height="60" fill="currentColor"/>
      <rect x="150" y="76" width="120" height="44" fill="currentColor"/>
      <path d="M100,124 Q210,104 320,124 Z M140,80 Q210,62 280,80 Z" fill="currentColor"/>
      ${[0, 1, 2, 3, 4, 5].map((i) => `<rect x="${124 + i * 30}" y="136" width="16" height="18" fill="var(--paper)" opacity=".22"/>`).join('')}
      <path d="M210,76 L210,8" stroke="currentColor" stroke-width="5"/><path d="M210,10 L262,22 L210,36 Z" fill="var(--cinnabar)"/>
      <path d="M40,200 L380,200" stroke="var(--paper)" stroke-width="2" opacity=".2"/>
      <path d="M0,246 Q60,236 120,246 T240,246 T360,246 T480,246" stroke="currentColor" stroke-width="3" fill="none" opacity=".5"/>
    </g>`;
  };
  // 小火苗（起义、战火）：box 52×64
  M.flame = (color) => `<path d="M26,4 C40,22 48,34 46,46 C44,58 34,64 26,64 C16,64 6,58 6,46 C6,34 14,26 20,14 C22,26 26,28 30,26 C32,20 30,12 26,4 Z" fill="${color || 'var(--cinnabar)'}"/>`;

  // 地理：明初常用城市（经纬度，示意精度）与湖泊
  Object.assign(M.geo.city, {
    yingtian: [118.78, 32.05], chuzhou: [118.31, 32.3], hezhou: [118.35, 31.72], taiping: [118.49, 31.56], caishi: [118.45, 31.67],
    zhenjiang: [119.45, 32.2], changzhou: [119.97, 31.81], pingjiang: [120.62, 31.3], hangzhou: [120.16, 30.27], shaoxing: [120.58, 30.0],
    hongdu: [115.86, 28.68], jiangzhou: [116.0, 29.71], anqing: [117.06, 30.53], chizhou: [117.49, 30.66], wuchang: [114.31, 30.55],
    hanyang: [114.27, 30.55], luzhou: [117.27, 31.86], yangzhou: [119.41, 32.39], gaoyou: [119.46, 32.78], taizhou: [119.92, 32.46],
    xiangyang: [112.14, 32.04], jiangling: [112.19, 30.35], changsha: [112.94, 28.23], huizhou: [118.33, 29.87], beiping: [116.4, 39.9],
    huangjuesi: [117.5, 32.93],
  });
  M.geo.lake = {
    poyang: [[116.0, 29.6], [116.2, 29.75], [116.35, 29.5], [116.55, 29.35], [116.75, 29.0], [116.6, 28.75], [116.25, 28.8], [116.05, 29.0], [115.95, 29.3]],
    taihu: [[119.9, 31.2], [120.05, 31.45], [120.4, 31.5], [120.6, 31.25], [120.4, 30.95], [120.05, 30.95]],
    dongting: [[112.3, 29.0], [112.6, 29.4], [113.0, 29.4], [113.1, 29.1], [112.8, 28.85], [112.4, 28.8]],
  };
  // 城市中文名（地图标注用）
  M.geo.name = {
    haozhou: '濠州', yingzhou: '颍州', xuzhou: '徐州', kaifeng: '汴梁', jiqing: '集庆', yingtian: '应天', caozhou: '曹州', baimao: '白茅堤',
    jining: '济宁', dongping: '东平', shanzhou: '单州', huanglinggang: '黄陵冈', dadu: '大都', shangdu: '上都', huaian: '淮安', shouzhou: '寿州',
    chuzhou: '滁州', hezhou: '和州', taiping: '太平', caishi: '采石', zhenjiang: '镇江', changzhou: '常州', pingjiang: '平江', hangzhou: '杭州',
    shaoxing: '绍兴', hongdu: '洪都', jiangzhou: '江州', anqing: '安庆', chizhou: '池州', wuchang: '武昌', hanyang: '汉阳', luzhou: '庐州',
    yangzhou: '扬州', gaoyou: '高邮', taizhou: '泰州', xiangyang: '襄阳', jiangling: '江陵', changsha: '长沙', huizhou: '徽州', beiping: '北平',
    huangjuesi: '皇觉寺',
  };
})();
