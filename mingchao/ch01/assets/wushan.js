// 风格层 · 雾山：程序化的天空、山、雾、火、火星、烟、速度线、光束、逆光剪影、跑动循环、旗帜、闪白、震屏。
// 一切都是时间 t 的纯函数（W.clock 把绘制挂到 GSAP 时间线上，逐帧 seek 时重画），渲染完全确定。
(function () {
  const W = (window.Wushan = {});
  const TAU = Math.PI * 2;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const smooth = (k) => k * k * (3 - 2 * k);
  W.clamp = clamp; W.lerp = lerp; W.smooth = smooth;

  // ---------- 颜色 ----------
  const hex = (h) => { h = h.replace('#', ''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; };
  W.mix = (a, b, k, alpha) => { const A = hex(a), B = hex(b); const c = A.map((v, i) => Math.round(lerp(v, B[i], clamp(k, 0, 1)))); return alpha == null ? `rgb(${c})` : `rgba(${c},${alpha})`; };
  W.rgba = (h, a) => `rgba(${hex(h)},${a})`;

  // ---------- 噪声 ----------
  W.noise1 = (seed) => {
    const r = MR.random(seed), g = Array.from({ length: 1024 }, () => r());
    return (x) => { const i = Math.floor(x), f = x - i, a = g[((i % 1024) + 1024) % 1024], b = g[(((i + 1) % 1024) + 1024) % 1024]; return a + (b - a) * smooth(f); };
  };
  W.fbm = (seed) => { const n = [0, 1, 2, 3].map((k) => W.noise1(seed * 7 + k)); return (x) => n[0](x) * 0.55 + n[1](x * 2.13) * 0.25 + n[2](x * 4.37) * 0.13 + n[3](x * 8.91) * 0.07; };

  // ---------- 时钟：t0–t1 之间每次 seek 都调用 draw(t) ----------
  const clocks = [];
  W.clock = (tl, t0, t1, draw) => {
    clocks.push({ t0, draw });
    let cur = t0;
    const p = {};
    Object.defineProperty(p, 't', { get: () => cur, set: (v) => { cur = v; draw(v); } });
    tl.fromTo(p, { t: t0 }, { t: t1, duration: Math.max(0.001, t1 - t0), ease: 'none', immediateRender: false }, Math.max(0, t0));
  };

  // 从第 0 秒开始的时钟：GSAP 停在 0 时不会渲染从 0 开始的补间，建完镜头后手动画一次第 0 帧
  W.primeAll = () => clocks.forEach((c) => { if (c.t0 <= 0.0001) c.draw(0); });
  // F.finish() 前自动预绘第 0 帧（章节里不用再手动调用 W.primeAll）
  if (window.Ming && Ming.film) {
    const film0 = Ming.film;
    Ming.film = function (o) { const F = film0(o); const fin = F.finish; F.finish = () => { W.primeAll(); fin(); }; return F; };
  }

  // ---------- 画布 ----------
  W.canvas = (parent, w, h, x, y, z) => {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    Object.assign(c.style, { position: 'absolute', left: (x || 0) + 'px', top: (y || 0) + 'px', width: w + 'px', height: h + 'px', zIndex: z || 0 });
    parent.appendChild(c);
    return c.getContext('2d');
  };

  // 天空：三段渐变
  W.sky = (g, w, h, top, mid, bot, midAt) => {
    const gr = g.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, top); gr.addColorStop(midAt == null ? 0.55 : midAt, mid); gr.addColorStop(1, bot);
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
  };
  // 星
  W.stars = (g, w, h, t, seed, n, alpha) => {
    const r = MR.random(seed);
    for (let i = 0; i < n; i++) {
      const x = r() * w, y = r() * h * 0.55, s = 0.6 + r() * 1.8, ph = r() * TAU;
      g.globalAlpha = alpha * (0.45 + 0.55 * (0.5 + 0.5 * Math.sin(t * (1.5 + r() * 2) + ph)));
      g.fillStyle = '#e8f2ff'; g.beginPath(); g.arc(x, y, s, 0, TAU); g.fill();
    }
    g.globalAlpha = 1;
  };
  // 月 / 日：光晕 + 盘
  W.orb = (g, x, y, r, core, glow, glowR, alpha) => {
    g.globalAlpha = alpha == null ? 1 : alpha;
    const gr = g.createRadialGradient(x, y, r * 0.6, x, y, glowR);
    gr.addColorStop(0, glow); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(x, y, glowR, 0, TAU); g.fill();
    g.fillStyle = core; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();
    g.globalAlpha = 1;
  };
  // 山脊：fbm 生成，shift 是视差平移（像素），底部渐隐成雾色
  W.range = (g, w, h, o) => {
    const f = o.f, step = 6, y0 = o.y, amp = o.amp, sc = o.scale || 0.004, sh = o.shift || 0;
    g.beginPath(); g.moveTo(-10, h);
    for (let x = -10; x <= w + 10; x += step) {
      const v = f((x + sh) * sc);
      const peak = Math.pow(v, o.sharp || 1.6);
      g.lineTo(x, y0 - peak * amp);
    }
    g.lineTo(w + 10, h); g.closePath();
    const gr = g.createLinearGradient(0, y0 - amp, 0, Math.min(h, y0 + (o.fade || 260)));
    gr.addColorStop(0, o.top); gr.addColorStop(1, o.bot);
    g.fillStyle = gr; g.fill();
    if (o.rim) { g.strokeStyle = o.rim; g.lineWidth = o.rimW || 2; g.globalAlpha = o.rimA || 0.7; g.stroke(); g.globalAlpha = 1; }
  };
  // 雾带：一串大号柔光椭圆，水平流动（循环）
  W.mist = (g, w, t, o) => {
    const r = MR.random(o.seed || 3), n = o.n || 9, span = w + 900;
    for (let i = 0; i < n; i++) {
      const bx = r() * span, by = o.y + (r() - 0.5) * o.h, rx = 260 + r() * 420, ry = 50 + r() * 70, sp = (o.speed || 18) * (0.6 + r() * 0.8);
      const x = ((bx + t * sp) % span) - 450;
      g.save(); g.translate(x, by); g.scale(rx / 100, ry / 100);
      const gr = g.createRadialGradient(0, 0, 0, 0, 0, 100);
      gr.addColorStop(0, o.color); gr.addColorStop(1, 'rgba(0,0,0,0)');
      g.globalAlpha = o.alpha * (0.6 + 0.4 * r());
      g.fillStyle = gr; g.beginPath(); g.arc(0, 0, 100, 0, TAU); g.fill();
      g.restore();
    }
    g.globalAlpha = 1;
  };
  // 火星：从源区上升、左右摆，按周期循环
  W.embers = (g, t, o) => {
    const r = MR.random(o.seed || 9);
    g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < o.n; i++) {
      const x0 = lerp(o.x0, o.x1, r()), life = 1.6 + r() * 2.2, ph = r() * life, sp = (o.speed || 120) * (0.6 + r() * 0.8);
      const k = ((t + ph) % life) / life;
      const x = x0 + Math.sin((t + ph) * (1.5 + r() * 2)) * 18 + k * (o.drift || 30);
      const y = o.y - k * sp * life;
      const s = (1.2 + r() * 2.6) * (1 - k * 0.7);
      g.globalAlpha = (1 - k) * (o.alpha || 0.9);
      g.fillStyle = k < 0.3 ? '#fff1b0' : k < 0.6 ? '#ffb347' : '#ff5a24';
      g.beginPath(); g.arc(x, y, s, 0, TAU); g.fill();
    }
    g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  };
  // 火堆：三层水滴形火舌，抖动由时间决定
  W.flame = (g, x, y, s, t, seed) => {
    const n = W._fn || (W._fn = W.noise1(77));
    g.globalCompositeOperation = 'lighter';
    const glow = g.createRadialGradient(x, y - 30 * s, 0, x, y - 30 * s, 140 * s);
    glow.addColorStop(0, 'rgba(255,140,50,.45)'); glow.addColorStop(1, 'rgba(255,80,20,0)');
    g.fillStyle = glow; g.beginPath(); g.arc(x, y - 30 * s, 140 * s, 0, TAU); g.fill();
    [['#ff4a1c', 1.0], ['#ff9a2e', 0.72], ['#fff0a8', 0.42]].forEach(([c, k], i) => {
      const fl = 0.82 + 0.3 * n(t * 7 + seed * 3 + i), lean = (n(t * 3 + seed + i * 5) - 0.5) * 22 * s;
      const hh = 90 * s * k * fl, ww = 34 * s * k;
      g.fillStyle = c; g.beginPath();
      g.moveTo(x - ww, y);
      g.bezierCurveTo(x - ww * 1.1, y - hh * 0.45, x - ww * 0.2 + lean * 0.5, y - hh * 0.7, x + lean, y - hh);
      g.bezierCurveTo(x + ww * 0.3 + lean * 0.5, y - hh * 0.7, x + ww * 1.1, y - hh * 0.45, x + ww, y);
      g.closePath(); g.fill();
    });
    g.globalCompositeOperation = 'source-over';
  };
  // 烟柱：一串扩散的灰团
  W.smoke = (g, x, y, t, o) => {
    const r = MR.random(o.seed || 5), n = o.n || 10;
    for (let i = 0; i < n; i++) {
      const life = 4 + r() * 2, k = ((t + r() * life) % life) / life;
      const px = x + Math.sin(k * 3 + i) * 20 + k * (o.drift || 90), py = y - k * (o.rise || 380), rad = (30 + k * 120) * (o.scale || 1);
      const gr = g.createRadialGradient(px, py, 0, px, py, rad);
      gr.addColorStop(0, o.color || 'rgba(60,66,80,.5)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
      g.globalAlpha = (1 - k) * (o.alpha || 0.7); g.fillStyle = gr; g.beginPath(); g.arc(px, py, rad, 0, TAU); g.fill();
    }
    g.globalAlpha = 1;
  };
  // 速度线
  W.speedLines = (g, w, h, t, o) => {
    const r = MR.random(o.seed || 11);
    g.strokeStyle = o.color || 'rgba(230,240,255,.5)';
    for (let i = 0; i < o.n; i++) {
      const y = r() * h, len = 200 + r() * 600, sp = (o.speed || 2600) * (0.6 + r() * 0.8), span = w + len * 2;
      const x = span - (((r() * span) + t * sp) % span) - len;
      g.globalAlpha = (o.alpha || 0.5) * (0.3 + 0.7 * r()); g.lineWidth = 1 + r() * 3;
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + len, y); g.stroke();
    }
    g.globalAlpha = 1;
  };
  // 光束（从光源放射，缓慢旋转）
  W.rays = (g, x, y, t, o) => {
    g.save(); g.translate(x, y); g.rotate(t * (o.spin || 0.03));
    g.globalCompositeOperation = 'lighter';
    const n = o.n || 14, len = o.len || 1600;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * TAU, wdt = 0.05 + 0.04 * Math.sin(i * 1.7);
      const gr = g.createLinearGradient(0, 0, Math.cos(a) * len, Math.sin(a) * len);
      gr.addColorStop(0, o.color || 'rgba(255,200,120,.22)'); gr.addColorStop(1, 'rgba(255,200,120,0)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, len, a - wdt, a + wdt); g.closePath(); g.fill();
    }
    g.restore();
  };
  // 草叶前景条（视差最快）
  W.grass = (g, w, h, shift, o) => {
    const r = MR.random(o.seed || 21), n = o.n || 160, span = w + 200;
    g.fillStyle = o.color || '#05070a';
    g.fillRect(0, o.y, w, h - o.y);
    for (let i = 0; i < n; i++) {
      const bx = r() * span, ht = 30 + r() * (o.h || 120), lean = (r() - 0.5) * 40;
      const x = ((bx - shift) % span + span) % span - 100;
      g.beginPath(); g.moveTo(x - 6, o.y + 2); g.quadraticCurveTo(x + lean * 0.4, o.y - ht * 0.6, x + lean, o.y - ht); g.quadraticCurveTo(x + lean * 0.3 + 4, o.y - ht * 0.5, x + 6, o.y + 2); g.fill();
    }
  };
  // 营帐（剪影，帐门透出火光）
  W.tent = (g, x, y, s, lit) => {
    g.fillStyle = '#06080c'; g.beginPath(); g.moveTo(x - 70 * s, y); g.lineTo(x, y - 80 * s); g.lineTo(x + 70 * s, y); g.closePath(); g.fill();
    if (lit > 0) { g.fillStyle = `rgba(255,150,60,${lit})`; g.beginPath(); g.moveTo(x - 12 * s, y); g.lineTo(x, y - 34 * s); g.lineTo(x + 12 * s, y); g.closePath(); g.fill(); }
  };

  // ---------- 图层与光源（骨骼角色 rig.js 用）----------
  // 在镜头格里叠一层 SVG（放骨骼角色），返回 svg 元素；之后再建的 canvas 会盖在它上面（做前景草、速度线）
  W.svgLayer = (parent) => {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('width', 1920); s.setAttribute('height', 1080);
    Object.assign(s.style, { position: 'absolute', left: '0px', top: '0px', overflow: 'visible' });
    parent.appendChild(s); return s;
  };
  // 光源预设：dx, dy 是“从角色指向光源”的方向；color 是受光边颜色
  W.LIGHT = {
    moon: { dx: -0.75, dy: -0.66, color: '#bfe3ff', s: 0.4, r: 5 },
    fire: { dx: 0.7, dy: 0.5, color: '#ffb066', s: 0.38, r: 5.5 },
    dawn: { dx: 0.95, dy: -0.3, color: '#ffd38a', s: 0.38, r: 5.5 },
    day: { dx: 0.5, dy: -0.85, color: '#fff4dc', s: 0.3, r: 4 },
  };
  W.lightMix = (a, b, k) => ({ dx: lerp(a.dx, b.dx, k), dy: lerp(a.dy, b.dy, k), color: W.mixHex(a.color, b.color, k), s: lerp(a.s, b.s, k), r: lerp(a.r, b.r, k) });
  W.mixHex = (a, b, k) => { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => Math.round(lerp(v, B[i], clamp(k, 0, 1))).toString(16).padStart(2, '0')).join(''); };

  // ---------- DOM 层 ----------
  // 闪白 / 闪红
  W.flash = (tl, t, color, peak, dur) => {
    const el = document.getElementById('flash');
    tl.set(el, { background: color }, t - 0.001);
    tl.fromTo(el, { opacity: 0 }, { opacity: peak, duration: 0.05, ease: 'none', immediateRender: false }, t);
    tl.fromTo(el, { opacity: peak }, { opacity: 0, duration: dur || 0.5, ease: 'power2.out', immediateRender: false }, t + 0.05);
  };
  // 震屏：衰减的正弦抖动（作用在 #viewport 上，结束时归零）
  W.shake = (tl, t, dur, amp) => {
    const vp = document.getElementById('viewport');
    const p = {}; let k = 0;
    Object.defineProperty(p, 'k', { get: () => k, set: (v) => { k = v; const a = amp * (1 - v) * (1 - v); vp.style.transform = v >= 1 ? '' : `translate(${Math.sin(v * 61) * a}px, ${Math.cos(v * 47) * a * 0.7}px)`; } });
    tl.fromTo(p, { k: 0 }, { k: 1, duration: dur, ease: 'none', immediateRender: false }, t);
  };
  // 跑动循环：两个姿势交替 + 上下颠；返回 { el, place(t, x, y) }
  W.runner = (F, p, o) => {
    const M = Ming, box = M.box(p, o.cls || '', 0, 0, '', { w: 100 * o.sc, h: 200 * o.sc });
    const pose = (k) => F.fig(box, 0, 0, 100, 200, (o.kind === 'soldier' ? M.soldier : M.person)(Object.assign({ pose: k }, o.person || {})), o.sc, o.flip, o.color || '#05070a');
    const a = pose('run'), b = pose('walk');
    const per = o.period || 0.28, ph = o.phase || 0;
    return {
      el: box,
      place(t, x, y) {
        const k = ((t + ph) % per) / per, on = k < 0.5;
        a.style.opacity = on ? 1 : 0; b.style.opacity = on ? 0 : 1;
        const bob = Math.abs(Math.sin((t + ph) / per * Math.PI)) * 10 * o.sc;
        box.style.transform = `translate(${x}px, ${y - bob}px)`;
      },
    };
  };
  // 旗：SVG 路径随时间飘动；返回 update(t)
  W.flag = (p, x, y, o) => {
    const w = o.w || 120, h = o.h || 70, pole = o.pole || 220;
    const s = Ming.svg(p, x, y - pole, w + 20, pole + 10, `<path d="M4,0 L4,${pole}" stroke="#05070a" stroke-width="6"/><path class="fl" fill="${o.color || '#d93a22'}" stroke="#05070a" stroke-width="3"/>`);
    s.style.overflow = 'visible'; if (o.cls) s.classList.add(o.cls);
    const fl = s.querySelector('.fl'), ph = o.phase || 0;
    return (t) => {
      let d = 'M4,4';
      for (let i = 0; i <= 10; i++) { const u = i / 10; d += ` L${4 + u * w},${4 + Math.sin(t * 5 + ph - u * 4) * 10 * u}`; }
      for (let i = 10; i >= 0; i--) { const u = i / 10; d += ` L${4 + u * w},${4 + h + Math.sin(t * 5 + ph - u * 4 + 0.6) * 10 * u}`; }
      fl.setAttribute('d', d + ' Z');
    };
  };
  // 朱红笔触条（标题衬底）：毛边矩形
  W.brushBar = (p, x, y, w, h, color) => {
    const r = MR.random(Math.round(x + y)), top = [], bot = [];
    for (let i = 0; i <= 24; i++) { const u = i / 24; top.push(`${u * w},${(r() - 0.5) * h * 0.18 + (u < 0.05 || u > 0.95 ? h * 0.2 : 0)}`); bot.push(`${u * w},${h + (r() - 0.5) * h * 0.2 - (u < 0.05 || u > 0.95 ? h * 0.2 : 0)}`); }
    const s = Ming.svg(p, x, y, w, h, `<path d="M${top.join(' L')} L${bot.reverse().join(' L')} Z" fill="${color || '#c8311c'}"/>`);
    s.style.overflow = 'visible';
    return s;
  };
})();
