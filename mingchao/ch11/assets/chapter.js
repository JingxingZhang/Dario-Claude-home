// 大明开局 · 第11集 · 洪都八十五天（原书第十一章《洪都的奇迹》）· 雾山画风 · 16:9 · 60 fps
(() => {
const F = Ming.film();
const { T, fx, C, M, V, tl } = F;
const W = Wushan, box = F.box, fig = F.fig;
const WD = 1920, HT = 1080;
const sfx = (n, t, o) => MR.sfx(n, Math.max(0, t), o);
const pop = (el, t, from) => fx.in(el, t, Object.assign({ opacity: 0, scale: 1.25, y: 20 }, from || {}), { opacity: 1, scale: 1, y: 0 }, 0.45, 'expo.out');
const out = (el, t, d) => fx.to(el, t, { opacity: 1 }, { opacity: 0 }, d || 0.35, 'power2.in');
const sil = (p, x, y, w, h, inner, sc, cls, flip, color) => { const e = fig(p, x, y, w, h, inner, sc, flip, color || '#07080b'); if (cls) e.classList.add(cls); return e; };
const kwo = (o) => Object.assign({ back: false, x: 360, w: 1200, y: 380, size: 180, color: '#f2b84b' }, o || {});
const fA = W.fbm(1), fB = W.fbm(2), fC = W.fbm(3), fD = W.fbm(4), fE = W.fbm(5);
const write = (p, x, y, text, at, o) => { o = o || {}; const e = box(p, o.cls || 'ws-title', x, y, '', Object.assign({ fontSize: (o.size || 84) + 'px' }, o.st || {})); M.write(tl, M.chars(e, text), at, { dir: 'right', dur: 0.2, stagger: Math.min(0.08, (o.span || 0.9) / [...text].length) }); sfx('draw', at, { dur: 0.6, gain: 0.3 }); return e; };
const card = (p, x, y, w, idx, text) => box(p, '', x, y, `<span class="ws-num" style="font-size:64px;margin-right:18px">${idx}</span><span class="ws-label" style="font-size:56px">${text}</span>`,
  { w, h: 130, background: 'rgba(8,10,16,.82)', border: '3px solid #b88a2e', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box' });

// ---------- 画法 ----------
// 城墙：x0–x1，墙顶 top，地面 gy；breach：[缺口中心, 半宽, 深度 0–1]；patch：缺口处补砖的进度 0–1
const wall = (g, x0, x1, top, gy, o) => {
  o = o || {};
  const col = o.col || '#0b0d12', rim = o.rim || 'rgba(170,215,240,.55)';
  g.fillStyle = col; g.beginPath(); g.moveTo(x0, gy);
  const mw = 34, step = 56;
  g.lineTo(x0, top);
  for (let x = x0; x < x1; x += step) { g.lineTo(x, top - 22); g.lineTo(x + mw, top - 22); g.lineTo(x + mw, top); g.lineTo(Math.min(x1, x + step), top); }
  g.lineTo(x1, gy); g.closePath(); g.fill();
  g.strokeStyle = rim; g.lineWidth = 3; g.beginPath(); g.moveTo(x0, top); g.lineTo(x1, top); g.stroke();
  // 砖缝
  g.strokeStyle = 'rgba(255,255,255,.05)'; g.lineWidth = 2;
  for (let y = top + 30; y < gy; y += 34) { g.beginPath(); g.moveTo(x0, y); g.lineTo(x1, y); g.stroke(); }
  if (o.breach) {
    const [bx, bw, d] = o.breach, depth = (gy - top + 30) * d;
    g.save(); g.globalCompositeOperation = 'destination-out';
    g.beginPath(); g.moveTo(bx - bw, top - 24); g.lineTo(bx - bw * 0.7, top - 24 + depth * 0.7); g.lineTo(bx - bw * 0.2, top - 24 + depth); g.lineTo(bx + bw * 0.4, top - 24 + depth * 0.85); g.lineTo(bx + bw, top - 24); g.closePath(); g.fill(); g.restore();
    if (o.patch) { const ph = depth * o.patch; g.fillStyle = '#3a2a1e'; g.fillRect(bx - bw * 0.75, top - 24 + depth - ph, bw * 1.5, ph); g.strokeStyle = 'rgba(0,0,0,.4)'; for (let y = top - 24 + depth - ph; y < top - 24 + depth; y += 22) { g.beginPath(); g.moveTo(bx - bw * 0.75, y); g.lineTo(bx + bw * 0.75, y); g.stroke(); } }
  }
};
// 城楼（门楼）
const tower = (g, cx, top, s, lit, rim) => {
  g.save(); g.translate(cx, top); g.scale(s, s);
  g.fillStyle = '#080a0e'; g.fillRect(-90, -110, 180, 110);
  g.beginPath(); g.moveTo(-140, -100); g.quadraticCurveTo(0, -170, 140, -100); g.lineTo(110, -120); g.quadraticCurveTo(0, -180, -110, -120); g.closePath(); g.fill();
  g.beginPath(); g.moveTo(-120, -160); g.quadraticCurveTo(0, -225, 120, -160); g.lineTo(90, -175); g.quadraticCurveTo(0, -230, -90, -175); g.closePath(); g.fill();
  g.fillRect(-60, -170, 120, 60);
  if (lit) { g.fillStyle = `rgba(255,170,90,${lit})`; [-55, -15, 25].forEach((x) => g.fillRect(x, -80, 26, 34)); }
  g.strokeStyle = rim || 'rgba(170,215,240,.5)'; g.lineWidth = 3; g.beginPath(); g.moveTo(-140, -100); g.quadraticCurveTo(0, -170, 140, -100); g.stroke();
  g.restore();
};
// 巨舰：x 船中，wl 水线，s 比例，facing 1 朝右
const ship = (g, x, wl, s, t, o) => {
  o = o || {};
  g.save(); g.translate(x, wl); g.scale(s * (o.facing || 1), s);
  g.fillStyle = o.col || '#06080c';
  g.beginPath(); g.moveTo(-260, -40); g.lineTo(240, -40); g.quadraticCurveTo(300, -60, 320, -110); g.lineTo(290, -40); g.quadraticCurveTo(250, 20, 180, 24); g.lineTo(-200, 24); g.quadraticCurveTo(-260, 10, -280, -60); g.closePath(); g.fill();
  // 楼橹三层
  g.fillRect(-200, -120, 340, 82); g.fillRect(-160, -200, 260, 82); g.fillRect(-110, -270, 160, 72);
  [[-220, -120, 380], [-180, -200, 300], [-130, -270, 200]].forEach(([a, y, w]) => { g.beginPath(); g.moveTo(a, y); g.lineTo(a + w, y); g.lineTo(a + w - 20, y - 18); g.lineTo(a + 20, y - 18); g.closePath(); g.fill(); });
  if (o.lit) { g.fillStyle = `rgba(255,160,80,${o.lit})`; for (let r = 0; r < 3; r++) for (let i = 0; i < 6 - r * 2; i++) g.fillRect(-180 + r * 40 + i * 52, -100 - r * 80, 18, 20); }
  // 旗
  g.strokeStyle = g.fillStyle = o.col || '#06080c'; g.lineWidth = 6; g.beginPath(); g.moveTo(-30, -290); g.lineTo(-30, -400); g.stroke();
  g.fillStyle = o.flag || '#7a1a12'; g.beginPath(); g.moveTo(-30, -400); for (let i = 0; i <= 8; i++) g.lineTo(-30 + i * 14, -400 + Math.sin(t * 5 + i * 0.7) * 6); g.lineTo(82, -350); for (let i = 8; i >= 0; i--) g.lineTo(-30 + i * 14, -350 + Math.sin(t * 5 + i * 0.7) * 6); g.closePath(); g.fill();
  if (o.rim) { g.strokeStyle = o.rim; g.lineWidth = 3; g.beginPath(); g.moveTo(-200, -120); g.lineTo(140, -120); g.moveTo(-160, -200); g.lineTo(100, -200); g.stroke(); }
  g.restore();
};
// 小渔船
const skiff = (g, x, wl, s, t) => {
  g.save(); g.translate(x, wl + Math.sin(t * 2.4) * 4); g.rotate(Math.sin(t * 1.7) * 0.03); g.scale(s, s);
  g.fillStyle = '#05070a'; g.beginPath(); g.moveTo(-90, -14); g.quadraticCurveTo(0, 22, 96, -18); g.lineTo(80, 4); g.quadraticCurveTo(0, 26, -76, 4); g.closePath(); g.fill();
  g.beginPath(); g.ellipse(-10, -40, 13, 15, 0, 0, 6.28); g.fill(); g.fillRect(-26, -30, 30, 26);
  g.strokeStyle = '#05070a'; g.lineWidth = 5; g.beginPath(); g.moveTo(10, -30); g.lineTo(70, 30); g.stroke();
  g.strokeStyle = 'rgba(190,225,240,.6)'; g.lineWidth = 2; g.beginPath(); g.moveTo(-90, -14); g.quadraticCurveTo(0, 22, 96, -18); g.stroke();
  g.restore();
};
const water = (g, y, t, top, bot, glint) => {
  const wg = g.createLinearGradient(0, y, 0, HT); wg.addColorStop(0, top); wg.addColorStop(1, bot); g.fillStyle = wg; g.fillRect(0, y, WD, HT - y);
  g.strokeStyle = glint || 'rgba(170,215,240,.18)'; g.lineWidth = 2;
  for (let i = 0; i < 26; i++) { const yy = y + 10 + i * i * 0.9, x = ((i * 337 + t * (20 + i * 3)) % (WD + 300)) - 150; g.beginPath(); g.moveTo(x, yy); g.lineTo(x + 80 + i * 4, yy); g.stroke(); }
};
const nightSky = (g, t, k) => {
  W.sky(g, WD, HT, '#03070f', '#0e2134', '#24414f', 0.62);
  W.stars(g, WD, HT, t, 7, 120, 0.8);
  W.orb(g, 360, 200, 60, '#f3f0df', 'rgba(150,200,255,.35)', 300);
  W.range(g, WD, HT, { f: fA, y: 560, amp: 200, shift: t * 10 + (k || 0), top: '#1d3446', bot: '#2a4a57', rim: 'rgba(160,210,240,.2)' });
  W.mist(g, WD, t, { y: 560, h: 80, alpha: 0.35, color: 'rgba(170,205,220,.5)', seed: 4, speed: 14 });
};
const fleetLights = []; { const r = MR.random(42); for (let i = 0; i < 260; i++) fleetLights.push([r() * WD, 640 + r() * 70 + r() * r() * 80, r() * 6.28, 1 + r() * 2.2]); }
const drawLights = (g, t, x0, x1, a) => { g.globalCompositeOperation = 'lighter'; for (const [x, y, ph, s] of fleetLights) { if (x < x0 || x > x1) continue; g.globalAlpha = (a || 1) * (0.4 + 0.6 * (0.5 + 0.5 * Math.sin(t * 3 + ph))); g.fillStyle = '#ffa23f'; g.beginPath(); g.arc(x, y, s, 0, 6.28); g.fill(); } g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; };

// ===================== A 首帧钩子：号称六十万 · 楼船与城齐 · 城塌了又砌 · 城下一句话 =====================
{
  const t1 = T(7) + 0.2;
  const p = F.shot('siege', 0, 0, 0, t1);
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p), fg = W.canvas(p, WD, HT);
  const GY = 860;
  const brk = T(3, '塌了') - 0.2, walkAt = T(5) - 0.2;
  const zm = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 50 });
  const guards = [0, 1].map(() => Rig.human(sv, { look: Rig.LOOK.yuan, ground: 50 }));
  W.clock(tl, 0, t1 + 0.6, (t) => {
    const b = W.smooth(W.clamp((t - brk) / 0.6, 0, 1)), pt = W.clamp((t - brk - 0.8) / 3.5, 0, 1);
    g.clearRect(0, 0, WD, HT);
    nightSky(g, t);
    water(g, 640, t, '#0c1a26', '#04080d');
    drawLights(g, t, 0, 900);
    ship(g, 380, 700, 0.9, t, { lit: 0.7, rim: 'rgba(170,215,240,.4)' });
    ship(g, 720, 690, 0.65, t + 1, { lit: 0.5 });
    wall(g, 960, WD + 10, 470, GY, { breach: [1260, 110, 0.55 * b], patch: pt });
    tower(g, 1600, 470, 1.0, 0.8);
    g.fillStyle = '#05070a'; g.fillRect(960, GY, WD - 960, HT - GY);
    if (b > 0 && b < 1) W.smoke(g, 1260, 560, t, { seed: 5, n: 10, alpha: 0.5, scale: 1.4, color: 'rgba(120,110,100,.55)', rise: 200 });
    W.embers(g, t, { n: 40, x0: 1000, x1: 1800, y: 600, speed: 60, seed: 11, alpha: 0.6 });
    // 被押到城下的人（第 5 句起）
    const k = W.clamp((t - walkAt) / 2.2, 0, 1), on = t > walkAt - 0.1 ? 1 : 0;
    sv.style.opacity = on;
    const x = W.lerp(700, 1100, W.smooth(k));
    const pp = k < 1 ? Rig.walk(t, { period: 0.6 }) : Rig.stand(t);
    zm.set({ x, y: GY - 172 * 0.9 + pp.bob, groundY: GY, s: 0.9, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, W.LIGHT.fire);
    guards.forEach((r, i) => { const q = k < 1 ? Rig.walk(t + 0.2 * i, { period: 0.6 }) : Rig.stand(t + i); r.set({ x: x - 110 - i * 90, y: GY - 172 * 0.92 + q.bob, groundY: GY, s: 0.92, facing: 1, angles: q.angles, worldAngles: q.worldAngles }, W.LIGHT.fire); });
    fg.clearRect(0, 0, WD, HT);
    W.mist(fg, WD, t, { y: 820, h: 70, alpha: 0.35, color: 'rgba(140,180,200,.45)', seed: 8, speed: 22 });
  });
  // 首帧文字（第 0 帧就完整）
  const yr = box(p, 'ws-num', 130, 190, '1363', { fontSize: '140px' });
  const yl = box(p, 'ws-label', 140, 400, '洪都（今南昌）', { fontSize: '46px' });
  const big = box(p, 'ws-title', 130, 470, '号称六十万', { fontSize: '120px', color: '#ff8a5a' });
  fx.to([yr, yl, big], T(2) - 0.2, { opacity: 1 }, { opacity: 0 }, 0.3);
  const eq = box(p, 'ws-tag', 140, 210, '楼船高与城等 ——《明史·邓愈传》', { fontSize: '46px' });
  pop(eq, T(2) - 0.05); out(eq, T(3) - 0.15);
  W.shake(tl, brk + 0.3, 0.5, 14); sfx('subdrop', brk + 0.2, { gain: 0.6, dur: 1.2 }); sfx('thud', brk + 0.3, { gain: 0.6 });
  const s3 = box(p, 'ws-label', 140, 220, '城坏三十余丈 · 且筑且战', { fontSize: '56px', color: '#ffd9a0' });
  fx.rise(s3, T(3) + 0.3, 16, 0.4); out(s3, T(4) - 0.15);
  F.kw('85天', T(4, '八十五'), kwo({ x: 140, w: 700, y: 210, size: 220, until: T(5) - 0.2 }));
  const q = box(p, 'ws-title', 1080, 220, '他喊了一句——', { fontSize: '84px', color: '#f2efe6' });
  fx.rise(q, T(6) - 0.1, 18, 0.45);
  sfx('riser', T(6) - 0.3, { gain: 0.4, dur: 1.2 });
  F.scene('siege', 0);
}

// ===================== B 侄子朱文正：何患不富贵 · 增城浚池 =====================
F.topic(T(7) - 0.05, '守城的是侄子');
{
  const t0 = T(7) - 0.05, t1 = T(14) + 0.2;
  const p = F.shot('nephew', 1, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p), sv2 = W.svgLayer(p);
  const GY = 860, back = T(8) - 0.2, fwd = T(11) - 0.2;
  const wen = Rig.human(sv, { look: Rig.LOOK.general, ground: 66 });
  const zhu = Rig.human(sv2, { look: Rig.LOOK.commander, ground: 66 });
  const rise = T(13) - 0.1;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const warm = W.smooth(W.clamp((t - back) / 0.5, 0, 1)) * (1 - W.smooth(W.clamp((t - fwd) / 0.5, 0, 1)));
    const L = W.lightMix(W.LIGHT.dawn, W.LIGHT.fire, warm);
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#2a2448', '#2b130c', warm), W.mix('#b4573a', '#8e4223', warm), W.mix('#f3b25a', '#e0a35c', warm), 0.62);
    W.orb(g, 1580, 520, 90, '#ffe2a0', 'rgba(255,170,90,.4)', 480);
    W.range(g, WD, HT, { f: fB, y: 640, amp: 180, shift: t * 12, top: '#6b3b45', bot: '#c06e4a' });
    W.mist(g, WD, t, { y: 660, h: 80, alpha: 0.35, color: 'rgba(255,210,170,.5)', seed: 23, speed: 14 });
    // 城头：墙顶会加高，护城河会加深
    const r = W.smooth(W.clamp((t - rise) / 1.2, 0, 1));
    wall(g, -10, WD + 10, 700 - 50 * r, GY + 40, { col: '#1a0d0c', rim: 'rgba(255,200,140,.6)' });
    g.fillStyle = '#120807'; g.fillRect(0, GY, WD, HT - GY);
    g.fillStyle = `rgba(40,70,90,${0.6 + 0.3 * r})`; g.fillRect(0, 1000 - 40 * r, WD, 80 + 40 * r);
    const pa = Rig.stand(t);
    const wx = 1500;
    wen.set({ x: wx, y: 700 - 50 * r - 172 * 1.25 + pa.bob, groundY: 700 - 50 * r, s: 1.25, facing: warm > 0.5 ? -1 : 1, angles: pa.angles, worldAngles: pa.worldAngles }, L);
    const pz = Rig.address(t);
    zhu.set({ x: 1120, y: 700 - 172 * 1.3, groundY: 700, s: 1.3, facing: 1, angles: pz.angles, worldAngles: pz.worldAngles }, L);
    sv2.style.opacity = warm;
  });
  const nm = box(p, 'ws-tag', 840, 220, '大都督 · 朱文正', { fontSize: '58px' });
  pop(nm, T(7, '朱文正') - 0.15);
  const nn = box(p, 'ws-label', 850, 330, '朱元璋长兄之子', { fontSize: '44px' });
  fx.fade(nn, T(7, '侄子') - 0.1, 0.3);
  fx.to([nm, nn], back - 0.1, { opacity: 1 }, { opacity: 0 }, 0.3);
  const fb = box(p, 'ws-label', 140, 180, '早年 · 回闪', { fontSize: '40px', color: '#ffd9a0' });
  fx.fade(fb, back + 0.1, 0.3);
  const qt = write(p, 140, 250, '“叔父成大业，何患不富贵。”', T(9, '叔父') - 0.05, { size: 62, span: 1.6 });
  const src = box(p, 'ws-label', 150, 350, '——《明史·诸王传》', { fontSize: '38px', color: '#ffe0a0' });
  fx.fade(src, T(9) + 1.4, 0.4);
  const xi = box(p, 'ws-tag', 150, 430, '太祖喜其言', { fontSize: '50px' });
  pop(xi, T(10, '高兴') - 0.2); sfx('ding', T(10, '高兴'), { gain: 0.35 });
  fx.to([fb, qt, src, xi], fwd - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  // 酒杯 → 《明史》三个词
  const cup = box(p, '', 1080, 240, `<svg width="160" height="200" viewBox="0 0 160 200"><path d="M20,20 L140,20 Q136,96 80,110 Q24,96 20,20 Z" fill="#f2b84b" stroke="#06070a" stroke-width="6"/><path d="M80,110 L80,170 M40,180 L120,180" stroke="#f2b84b" stroke-width="12" stroke-linecap="round"/></svg>`, {});
  const cl = box(p, 'ws-label', 990, 460, '有书说：整日饮酒', { fontSize: '44px' });
  fx.fade(cup, T(11) - 0.05, 0.3); fx.fade(cl, T(11) + 0.1, 0.3);
  fx.to([cup, cl], T(12, '增城') - 0.3, { opacity: 1 }, { opacity: 0 }, 0.4);
  const src2 = box(p, 'ws-label', 140, 200, '我翻《明史》：', { fontSize: '48px', color: '#ffe0a0' });
  fx.fade(src2, T(12) - 0.05, 0.3);
  [['增城', T(12, '增城')], ['浚池', T(12, '浚池')], ['号令明肃', T(12, '号令')]].forEach(([w, at], i) => { const s = M.seal(p, w, { x: 140 + i * 330, y: 300, size: 130, zhu: true, rot: -6 + i * 4, row: true }); s.style.background = 'rgba(14,8,8,.85)'; fx.stamp(s, at, 0.6); });
  F.scene('nephew', T(7));
}

// ===================== C 抚州门：城坏三十余丈 · 邓愈三月不解甲 =====================
F.topic(T(14) - 0.05, '抚州门');
{
  const t0 = T(14) - 0.05, t1 = T(19) + 1.0;
  const p = F.shot('fuzhou', 2, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p), fg = W.canvas(p, WD, HT);
  const GY = 860, brk = T(16, '塌了') - 0.25, cyc = T(18) - 0.2;
  const deng = Rig.human(sv, { look: Rig.LOOK.general, ground: 60 });
  const masons = [0, 1, 2].map(() => Rig.human(sv, { look: Rig.LOOK.soldier, ground: 50 }));
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const b = W.smooth(W.clamp((t - brk) / 0.5, 0, 1)), pt = W.clamp((t - T(17)) / 3.5, 0, 1);
    const day = (t > cyc) ? 0.5 + 0.5 * Math.sin((t - cyc) * 2.4 - 1.57) : 0.15;
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#120a10', '#5a2a1e', day), W.mix('#2a1414', '#c06a3a', day), W.mix('#4a2a22', '#f3b25a', day), 0.6);
    if (t > cyc) { const a = (t - cyc) * 2.4; W.orb(g, 960 + Math.cos(a) * 760, 620 - Math.sin(a) * 380, 60, day > 0.5 ? '#ffe2a0' : '#f3f0df', 'rgba(255,200,140,.3)', 260); }
    W.range(g, WD, HT, { f: fC, y: 600, amp: 160, shift: t * 10, top: '#2a1a1e', bot: '#4a2a26' });
    W.smoke(g, 400, 640, t, { seed: 21, n: 10, alpha: 0.4, scale: 2, color: 'rgba(40,24,24,.6)', rise: 500, drift: 120 });
    W.smoke(g, 1500, 640, t, { seed: 23, n: 10, alpha: 0.4, scale: 2, color: 'rgba(40,24,24,.6)', rise: 500, drift: 120 });
    wall(g, -10, WD + 10, 520, GY, { col: '#0b0807', rim: 'rgba(255,170,100,.6)', breach: [960, 230, 0.75 * b], patch: pt * 0.85 });
    tower(g, 300, 520, 0.9, 0.6, 'rgba(255,170,100,.5)');
    g.fillStyle = '#060404'; g.fillRect(0, GY, WD, HT - GY);
    if (b > 0) { W.smoke(g, 960, 640, t - brk, { seed: 25, n: 14, alpha: 0.6 * (1 - pt * 0.6), scale: 2.2, color: 'rgba(110,90,80,.6)', rise: 260, drift: 60 }); W.embers(g, t, { n: 60, x0: 760, x1: 1160, y: 700, speed: 80, seed: 27, alpha: 0.7 }); }
    // 砌墙的人（缺口处）
    sv.style.opacity = 1;
    masons.forEach((r, i) => { const on = t > T(17) - 0.3; const pp = Rig.bow(t + i * 0.7, 0.4 + 0.4 * (0.5 + 0.5 * Math.sin(t * 3 + i))); r.set({ x: on ? 820 + i * 140 : -400, y: GY - 172 * 0.95 + pp.bob, groundY: GY, s: 0.95, facing: i % 2 ? -1 : 1, angles: pp.angles, worldAngles: pp.worldAngles }, W.LIGHT.fire); });
    const pd = Rig.stand(t);
    deng.set({ x: 1500, y: 520 - 172 * 1.15 + pd.bob, groundY: 520, s: 1.15, facing: -1, angles: pd.angles, worldAngles: pd.worldAngles }, day > 0.5 ? W.LIGHT.dawn : W.LIGHT.fire);
    fg.clearRect(0, 0, WD, HT);
    W.mist(fg, WD, t, { y: 840, h: 60, alpha: 0.3, color: 'rgba(200,160,140,.4)', seed: 29, speed: 20 });
  });
  const tg = box(p, 'ws-tag', 1240, 200, '邓愈 · 抚州门', { fontSize: '58px' });
  pop(tg, T(14, '邓愈') - 0.15);
  const ls = box(p, 'ws-label', 1250, 310, '当要冲 ——《明史·邓愈传》', { fontSize: '40px' });
  fx.fade(ls, T(14, '要紧') - 0.1, 0.3);
  fx.to([tg, ls], T(15) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  const ch = box(p, 'ws-tag', 130, 200, '陈友谅亲督战', { fontSize: '54px' });
  pop(ch, T(15) - 0.05); out(ch, T(16) - 0.1);
  W.shake(tl, brk + 0.25, 0.7, 20); W.flash(tl, brk + 0.25, 'rgba(255,200,150,1)', 0.4, 0.4);
  sfx('subdrop', brk + 0.2, { gain: 0.8, dur: 1.4 }); sfx('impact', brk + 0.25, { gain: 0.7 });
  F.kw('三十丈', T(16, '三十'), kwo({ x: 130, w: 700, y: 200, size: 170, color: '#e5482b', until: T(17) - 0.1 }));
  const zz = box(p, 'ws-title', 130, 220, '且筑且战', { fontSize: '96px' });
  fx.rise(zz, T(17) - 0.05, 18, 0.4); out(zz, T(18) - 0.15);
  const jia = box(p, 'ws-title', 130, 220, '昼夜不解甲者三月', { fontSize: '76px', color: '#ffe0a0' });
  fx.rise(jia, T(18) + 0.2, 18, 0.5);
  F.scene('fuzhou', T(14));
}

// ===================== D 新城门：薛显开门出击 =====================
F.topic(T(19) - 0.05, '薛显开门');
{
  const t0 = T(19) - 0.2, t1 = T(22) + 1.0;
  const p = F.shot('xue', 3, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.45, dur: 0.6 });
  const g = W.canvas(p, WD, HT);
  const open = T(20, '开门') - 0.2, charge = T(20, '冲出') - 0.4, fall = T(21, '死在') - 0.2;
  const riders = []; { const r = MR.random(9); for (let i = 0; i < 9; i++) riders.push([i * 150 + r() * 40, r() * 30, r() * 6.28]); }
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const o = W.smooth(W.clamp((t - open) / 0.6, 0, 1)), c = W.clamp((t - charge) / 2.6, 0, 1), f = W.smooth(W.clamp((t - fall) / 0.7, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#2a2148', '#b65439', '#f3b25a', 0.65);
    W.orb(g, 1650, 640, 90, '#ffe7b0', 'rgba(255,170,90,.45)', 520);
    W.rays(g, 1650, 640, t, { n: 14, len: 1500, color: 'rgba(255,190,120,.14)' });
    W.range(g, WD, HT, { f: fD, y: 660, amp: 160, shift: t * 14, top: '#5a2c35', bot: '#a85a42' });
    // 左侧城墙与城门
    wall(g, -10, 520, 420, 860, { col: '#0b0608', rim: 'rgba(255,200,140,.6)' });
    g.fillStyle = `rgba(255,200,130,${0.85 * o})`; g.fillRect(250, 640, 160, 220);
    g.fillStyle = '#1e0e0a'; g.fillRect(250 - 80 * o, 640, 80, 220); g.fillRect(330 + 80 * o, 640, 80, 220);
    tower(g, 330, 420, 0.8, 0.6, 'rgba(255,200,140,.6)');
    g.fillStyle = '#0b0608'; g.fillRect(0, 860, WD, 220);
    // 敌阵与帅旗
    for (let i = 0; i < 18; i++) { const x = 1150 + (i % 9) * 80, y = 860 - (i < 9 ? 0 : 20); g.fillStyle = '#120a0a'; g.fillRect(x, y - 90, 18, 90); g.beginPath(); g.arc(x + 9, y - 100, 12, 0, 6.28); g.fill(); }
    g.save(); g.translate(1450, 860); g.rotate(f * 1.3); g.strokeStyle = '#120a0a'; g.lineWidth = 8; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, -320); g.stroke();
    g.fillStyle = '#7a1a12'; g.beginPath(); g.moveTo(0, -320); for (let i = 0; i <= 8; i++) g.lineTo(i * 16, -320 + Math.sin(t * 6 + i * 0.7) * 7); g.lineTo(128, -250); for (let i = 8; i >= 0; i--) g.lineTo(i * 16, -250 + Math.sin(t * 6 + i * 0.7) * 7); g.closePath(); g.fill(); g.restore();
    if (c > 0 && c < 1) W.speedLines(g, WD, HT, t, { n: 40, speed: 3000, alpha: 0.3, seed: 7, color: 'rgba(255,230,200,.6)' });
    if (c > 0) W.smoke(g, 400 + c * 700, 860, t, { seed: 33, n: 10, alpha: 0.5 * (1 - c * 0.5), scale: 1, color: 'rgba(150,110,80,.6)', rise: 120, drift: -200 });
  });
  const tg = box(p, 'ws-tag', 640, 200, '薛显 · 章江门 新城门', { fontSize: '56px' });
  pop(tg, T(19, '薛显') - 0.15); out(tg, T(20) - 0.1);
  sfx('slide', open, { gain: 0.5 });
  // 骑兵剪影冲出
  const rs = riders.map(([x, y, ph], i) => { const e = sil(p, 0, 640 + y, 420, 300, M.general(), 0.55, 'rim-dawn', false, '#0b0608'); return [e, x, ph]; });
  rs.forEach(([e, x, ph], i) => { tl.fromTo(e, { x: 260 - x * 0.3, opacity: 0 }, { x: 260 + 700 - x * 0.6, opacity: 1, duration: 1.6, ease: 'power2.out', immediateRender: false }, charge + i * 0.06); tl.fromTo(e, { y: 0 }, { y: -10, duration: 0.18, yoyo: true, repeat: 9, ease: 'sine.inOut', immediateRender: false }, charge + i * 0.06); });
  sfx('whoosh', charge, { gain: 0.6, dur: 1.2 }); sfx('impact', charge + 1.2, { gain: 0.5 });
  const kill = box(p, 'ws-tag', 1100, 200, '斩其平章刘进昭', { fontSize: '56px' });
  pop(kill, fall - 0.1); sfx('thud', fall + 0.5, { gain: 0.6 });
  const src = box(p, 'ws-label', 1110, 310, '——《明史·薛显传》', { fontSize: '38px' });
  fx.fade(src, fall + 0.3, 0.3);
  F.scene('xue', T(19));
}

// ===================== E 赵德胜：弩中腰，镞入六寸 =====================
F.topic(T(22) - 0.05, '赵德胜');
{
  const t0 = T(22) - 0.2, t1 = T(28) + 0.2;
  const p = F.shot('zhao', 4, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.6 });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const hit = T(23, '射进') - 0.05, pull = T(24, '拔') - 0.2, die = T(27, '断了') - 0.1;
  const zhao = Rig.human(sv, { look: Rig.LOOK.general, ground: 60 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const sun = W.clamp((t - t0) / (t1 - t0), 0, 1), d = W.smooth(W.clamp((t - die) / 1.4, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#3a2140', '#0a0812', sun), W.mix('#c4512f', '#3a1a1a', sun), W.mix('#f7c46c', '#6a3a2a', sun), 0.6);
    W.orb(g, 1500, 560 + sun * 260, 120, '#e8452a', 'rgba(255,120,60,.45)', 600, 1 - sun * 0.4);
    W.range(g, WD, HT, { f: fE, y: 700, amp: 150, shift: t * 8, top: '#4a2026', bot: '#7a3a2e' });
    wall(g, -10, WD + 10, 640, 900, { col: '#0a0507', rim: 'rgba(255,170,100,.55)' });
    tower(g, 820, 640, 1.6, 0.4 * (1 - d), 'rgba(255,170,100,.55)');
    // 弩箭
    const a = W.clamp((t - hit + 0.35) / 0.35, 0, 1);
    if (a > 0 && t < pull) { g.strokeStyle = '#0a0507'; g.lineWidth = 5; const x = W.lerp(1900, 900, a), y = W.lerp(300, 470, a); g.beginPath(); g.moveTo(x, y); g.lineTo(x + 70, y - 12); g.stroke(); if (a < 1) W.speedLines(g, WD, HT, t, { n: 10, speed: 3000, alpha: 0.2, seed: 3 }); }
    if (t >= pull) { g.save(); g.translate(1010, 640); g.rotate(1.2); g.strokeStyle = '#0a0507'; g.lineWidth = 5; g.beginPath(); g.moveTo(0, 0); g.lineTo(80, 0); g.stroke(); g.restore(); }
    const L = W.lightMix(W.LIGHT.dawn, W.LIGHT.fire, sun);
    const pp = Rig.stand(t * (1 - d));
    zhao.set({ x: 900, y: 640 - 172 * 1.05 + pp.bob, groundY: 640, s: 1.05, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, L);
    sv.style.opacity = 1 - d * 0.55;
  });
  const tg = box(p, 'ws-tag', 1150, 200, '赵德胜 · 城门楼', { fontSize: '56px' });
  pop(tg, T(22, '赵德胜') - 0.15); out(tg, hit - 0.2);
  W.flash(tl, hit, 'rgba(255,230,200,1)', 0.5, 0.4); sfx('whip', hit - 0.15, { gain: 0.6 }); sfx('hit', hit, { gain: 0.6 });
  const six = box(p, 'ws-title', 1150, 220, '镞入六寸', { fontSize: '110px', color: '#e5482b' });
  fx.rise(six, T(23, '六寸') - 0.15, 18, 0.35); out(six, T(25) - 0.15);
  sfx('thud', pull + 0.3, { gain: 0.4 });
  const q1 = write(p, 1150, 220, '吾自壮岁从军，伤矢石屡矣，', T(25) + 0.05, { size: 54, span: 1.6, cls: 'ws-label' });
  const q2 = write(p, 1150, 300, '无重此者。', T(25, '没有') - 0.1, { size: 54, span: 0.5, cls: 'ws-label' });
  const q3 = write(p, 1150, 400, '丈夫死不恨，', T(26) - 0.05, { size: 64, span: 0.6 });
  const q4 = write(p, 1150, 490, '恨不能扫清中原耳。', T(26, '只恨') - 0.05, { size: 64, span: 0.9 });
  const age = box(p, 'ws-num', 1160, 620, '年三十九', { fontSize: '96px' });
  fx.rise(age, T(27, '三十九') - 0.2, 14, 0.5);
  const src = box(p, 'ws-label', 1160, 760, '——《明史·赵德胜传》', { fontSize: '38px', color: '#d9c7a4' });
  fx.fade(src, T(27) + 0.4, 0.4);
  F.scene('zhao', T(22));
}

// ===================== F 小渔船出水关：夜行昼止，半月到应天 =====================
F.topic(T(28) - 0.05, '一条小渔船');
{
  const t0 = T(28) - 0.05, t1 = T(33) + 1.0;
  const p = F.shot('boat', 5, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const slip = T(30) - 0.2, cyc = T(31) - 0.1, cold = T(32) - 0.2;
  const zm = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 50 });
  const reeds = []; { const r = MR.random(13); for (let i = 0; i < 90; i++) reeds.push([r() * WD, 800 + r() * 80, 60 + r() * 120, r() * 6.28]); }
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const s = W.clamp((t - slip) / 2.0, 0, 1), cy = t > cyc && t < cold ? 0.5 + 0.5 * Math.sin((t - cyc) * 3.2 - 1.57) : 0;
    const k = W.smooth(W.clamp((t - cold) / 0.6, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#03070f', '#2a3a52', cy), W.mix('#0e2134', '#6a8aa0', cy), W.mix('#24414f', '#c9c2a2', cy), 0.62);
    if (t > cyc && t < cold) { const a = (t - cyc) * 3.2; W.orb(g, 960 + Math.cos(a) * 700, 600 - Math.sin(a) * 360, 54, cy > 0.5 ? '#fff6dc' : '#f3f0df', 'rgba(220,230,255,.3)', 240); }
    else W.orb(g, 1560, 200, 54, '#f3f0df', 'rgba(150,200,255,.35)', 280);
    W.range(g, WD, HT, { f: fA, y: 600, amp: 160, shift: t * 10, top: '#1d3446', bot: '#2a4a57' });
    water(g, 700, t, '#0c1a26', '#04080d');
    // 水关：城墙 + 铁栅（只在出关段）
    if (t < cyc + 0.3) {
      wall(g, -10, 640, 380, 720, {});
      g.fillStyle = '#04060a'; g.fillRect(380, 560, 200, 160);
      g.strokeStyle = '#1a2a34'; g.lineWidth = 8; for (let x = 396; x < 580; x += 26) { g.beginPath(); g.moveTo(x, 560); g.lineTo(x, 730 - s * 120); g.stroke(); }
    }
    // 芦苇
    g.strokeStyle = 'rgba(5,8,12,.9)'; g.lineWidth = 3;
    reeds.forEach(([x, y, h, ph]) => { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.sin(t * 1.5 + ph) * 12, y - h * 0.6, x + Math.sin(t * 1.5 + ph) * 22, y - h); g.stroke(); });
    // 小船
    const bx = t < cyc + 0.3 ? W.lerp(480, 1000, W.smooth(s)) : (k > 0 ? W.lerp(1250, 1350, k) : 600 + ((t - cyc) * 140) % 1000);
    skiff(g, bx, 760, k > 0 ? 1.6 : 1.2, t);
    // 冷知识：左侧六十万船灯
    if (k > 0) { g.globalAlpha = k; drawLights(g, t, 0, 820, 1); ship(g, 380, 720, 0.7, t, { lit: 0.6 }); g.globalAlpha = 1; }
    const pp = Rig.stand(t);
    zm.set({ x: 640, y: 700 - 172 * 1.1 + pp.bob, groundY: 700, s: 1.1, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, W.LIGHT.moon);
    sv.style.opacity = t < slip ? 1 : 0;
  });
  const tg = box(p, 'ws-tag', 1100, 200, '千户 · 张子明', { fontSize: '56px' });
  pop(tg, T(29, '张子明') - 0.15); out(tg, cyc - 0.1);
  const iso = box(p, 'ws-label', 1100, 310, '内外隔绝', { fontSize: '52px' });
  fx.fade(iso, T(28) + 0.2, 0.3); out(iso, T(29) - 0.1);
  sfx('slide', slip, { gain: 0.4, dur: 1.4 });
  const ny = box(p, 'ws-title', 1000, 220, '夜行昼止 · 半月始达', { fontSize: '78px' });
  fx.rise(ny, T(31) + 0.1, 18, 0.4); out(ny, cold - 0.1);
  const L60 = box(p, 'ws-num', 160, 210, '60万', { fontSize: '170px', color: '#ff8a5a' });
  const Lb = box(p, 'ws-label', 170, 400, '城外 · 号称', { fontSize: '46px' });
  const Rb = box(p, 'ws-label', 1150, 400, '出城报信 · 一条小渔船', { fontSize: '46px' });
  fx.rise(L60, T(32, '六十万') - 0.2, 16, 0.4); fx.fade(Lb, T(32, '六十万'), 0.3);
  fx.fade(Rb, T(32, '小船') - 0.2, 0.3);
  F.kw('小渔船', T(32, '小船'), kwo({ x: 1080, w: 700, y: 210, size: 150, until: T(33) + 0.2 }));
  F.scene('boat', T(28));
}

// ===================== G 应天：坚守一月，吾自取之 =====================
F.topic(T(33) - 0.1, '再守一个月');
{
  const t0 = T(33) - 0.2, t1 = T(36) + 0.2;
  const p = F.shot('yingtian', 6, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.6 });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const GY = 860;
  const zhu = Rig.human(sv, { look: Rig.LOOK.commander, ground: 70 }), zm = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 60 });
  const ebb = T(34, '江水') - 0.2;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const e = W.smooth(W.clamp((t - ebb) / 2.2, 0, 1));
    g.clearRect(0, 0, WD, HT);
    const bg = g.createLinearGradient(0, 0, 0, HT); bg.addColorStop(0, '#1a0e08'); bg.addColorStop(1, '#3a2010'); g.fillStyle = bg; g.fillRect(0, 0, WD, HT);
    const gl = g.createRadialGradient(560, 520, 0, 560, 520, 900); gl.addColorStop(0, 'rgba(255,170,80,.28)'); gl.addColorStop(1, 'rgba(255,170,80,0)'); g.fillStyle = gl; g.fillRect(0, 0, WD, HT);
    // 柱子
    g.fillStyle = '#120804'; [120, 1000].forEach((x) => g.fillRect(x, 160, 60, GY - 160));
    g.fillRect(0, 140, WD, 30); g.fillStyle = '#0d0603'; g.fillRect(0, GY, WD, HT - GY);
    W.flame(g, 330, 700, 0.5, t, 3); W.flame(g, 860, 700, 0.5, t, 4);
    // 右侧：江水日涸示意（窗）
    g.save(); g.beginPath(); g.rect(1160, 220, 620, 560); g.clip();
    W.sky(g, WD, HT, '#5a6a7a', '#a0a8a0', '#d8c8a0', 0.5);
    const wl = 560 + e * 140; water(g, wl, t, '#2a4a5a', '#10202a');
    g.fillStyle = '#4a3a26'; g.fillRect(1160, 740, 620, 60);
    ship(g, 1470, wl + 10 + e * 30, 0.6, t, { col: '#0a0c10' });
    if (e > 0.6) { g.save(); g.translate(1470, 760); g.rotate(0.06 * (e - 0.6) / 0.4); g.restore(); }
    g.restore();
    g.strokeStyle = '#d0a060'; g.lineWidth = 6; g.strokeRect(1160, 220, 620, 560);
    const pa = Rig.address(t), pb = Rig.bow(t, 0.5);
    zhu.set({ x: 420, y: GY - 172 * 1.35 + pa.bob, groundY: GY, s: 1.35, facing: 1, angles: pa.angles, worldAngles: pa.worldAngles }, W.LIGHT.fire);
    zm.set({ x: 820, y: GY - 172 * 1.2 + pb.bob, groundY: GY, s: 1.2, facing: -1, angles: pb.angles, worldAngles: pb.worldAngles }, W.LIGHT.fire);
  });
  const ln = box(p, 'ws-tag', 140, 200, '应天 · 朱元璋', { fontSize: '54px' });
  pop(ln, T(33) + 0.1);
  const dry = box(p, 'ws-tag', 1240, 250, '江水日涸，巨舰将不利', { fontSize: '44px' });
  pop(dry, T(34, '江水') - 0.1);
  fx.to([ln, dry], T(35) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  const yi = box(p, 'ws-title', 140, 190, '坚守一月，吾自取之', { fontSize: '96px', color: '#ffe0a0' });
  fx.rise(yi, T(35, '再守') - 0.15, 18, 0.45); sfx('impact', T(35, '一个月'), { gain: 0.5 });
  const src = box(p, 'ws-label', 150, 310, '——《明史·赵德胜传》附张子明', { fontSize: '38px', color: '#d9c7a4' });
  fx.fade(src, T(35) + 1.2, 0.4);
  F.scene('yingtian', T(33));
}

// ===================== H 城下：劝降还是喊坚守 =====================
F.topic(T(36) - 0.05, '城下一句话');
{
  const t0 = T(36) - 0.05, t1 = T(45) + 0.2;
  const p = F.shot('shout', 7, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p), fg = W.canvas(p, WD, HT);
  const GY = 880, walk0 = T(37) - 0.1, stab = T(44, '刺死') - 0.35;
  const zm = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 60 });
  const guards = [0, 1, 2].map(() => Rig.human(sv, { look: Rig.LOOK.yuan, ground: 60 }));
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const k = W.clamp((t - walk0) / 2.4, 0, 1), d = W.smooth(W.clamp((t - stab - 0.3) / 0.9, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#03070f', '#0e1a2a', '#1e3040', 0.6);
    W.stars(g, WD, HT, t, 9, 80, 0.6);
    wall(g, 1060, WD + 10, 250, GY, {});
    tower(g, 1500, 250, 1.1, 0.7);
    // 城头火把
    for (let i = 0; i < 6; i++) W.flame(g, 1120 + i * 130, 222, 0.32 + (t > T(43) - 0.2 ? 0.15 : 0), t, 50 + i);
    g.fillStyle = '#05070a'; g.fillRect(0, GY, WD, HT - GY);
    W.mist(g, WD, t, { y: 760, h: 80, alpha: 0.3, color: 'rgba(140,170,190,.4)', seed: 61, speed: 16 });
    const x = W.lerp(200, 820, W.smooth(k));
    const pp = k < 1 ? Rig.walk(t, { period: 0.62 }) : Rig.stand(t);
    zm.set({ x, y: GY - 172 * 1.3 + pp.bob, groundY: GY, s: 1.3, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, W.LIGHT.fire);
    guards.forEach((r, i) => { const q = k < 1 ? Rig.walk(t + 0.2 * i, { period: 0.62 }) : Rig.stand(t + i); r.set({ x: x - 170 - i * 130, y: GY - 172 * 1.25 + q.bob, groundY: GY, s: 1.25, facing: 1, angles: q.angles, worldAngles: q.worldAngles }, W.LIGHT.fire); });
    sv.style.opacity = 1 - d;
    fg.clearRect(0, 0, WD, HT);
    if (t > stab) { // 长槊刺下
      const a = W.smooth(W.clamp((t - stab) / 0.3, 0, 1));
      fg.strokeStyle = '#020304'; fg.lineWidth = 9; fg.lineCap = 'round';
      [[-1, 0.9], [1, 0.8], [-0.4, 1.1], [0.6, 1.0]].forEach(([dx, s], i) => { fg.beginPath(); const tx = 820 + dx * 30, ty = 700; fg.moveTo(tx + dx * 900 * (1.4 - a * 0.4), ty - 700 * s * (1.2 - a * 0.2)); fg.lineTo(tx + dx * 120 * (1 - a), ty - 80 * (1 - a)); fg.stroke(); });
      fg.fillStyle = `rgba(0,0,0,${0.55 * d})`; fg.fillRect(0, 0, WD, HT);
    }
  });
  const hk = box(p, 'ws-tag', 140, 200, '湖口 · 被执', { fontSize: '54px' });
  pop(hk, T(36, '湖口') - 0.15); out(hk, T(37) - 0.1);
  const yu = box(p, 'ws-label', 140, 200, '令诱城中降', { fontSize: '54px' });
  fx.fade(yu, T(37) + 0.1, 0.3); out(yu, T(38) - 0.1);
  const ok = box(p, 'ws-tag', 140, 200, '佯诺', { fontSize: '60px' });
  pop(ok, T(38) - 0.05); out(ok, T(39) - 0.15);
  // 站队题
  const c1 = card(p, 1120, 300, 600, '①', '劝降 · 能活'), c2 = card(p, 1120, 460, 600, '②', '喊坚守 · 会死');
  fx.in(c1, T(39, '劝降') - 0.15, { opacity: 0, x: -30 }, { opacity: 1, x: 0 }, 0.35, 'expo.out');
  fx.in(c2, T(39, '坚守') - 0.15, { opacity: 0, x: -30 }, { opacity: 1, x: 0 }, 0.35, 'expo.out');
  sfx('pop', T(39, '劝降'), { gain: 0.4 }); sfx('pop', T(39, '坚守'), { gain: 0.4 });
  const qq = box(p, 'ws-title', 1100, 640, '换了是你，喊哪一句？', { fontSize: '64px', color: '#f2b84b' });
  fx.rise(qq, T(40) - 0.1, 16, 0.4); sfx('ding', T(40, '哪一句'), { gain: 0.45 });
  fx.to([c1, c2, qq], T(41) - 0.2, { opacity: 1 }, { opacity: 0 }, 0.3);
  // 城下大呼
  const s1 = write(p, 1120, 300, '“我张大舍。', T(42) - 0.05, { size: 80, span: 0.5 });
  const s2 = write(p, 1120, 400, '已见主上，', T(42, '已经') - 0.05, { size: 80, span: 0.5 });
  const s3 = write(p, 1120, 500, '令诸公坚守，', T(43) - 0.05, { size: 80, span: 0.6 });
  const s4 = write(p, 1120, 600, '救且至！”', T(43, '救兵') - 0.05, { size: 96, span: 0.4, st: { color: '#ff8a5a' } });
  F.kw('救兵就到', T(43, '救兵') + 0.3, kwo({ x: 1100, w: 720, y: 730, size: 100, color: '#f2b84b', until: T(44) - 0.1 }));
  W.shake(tl, T(43, '救兵'), 0.3, 8);
  fx.to([s1, s2, s3, s4], stab - 0.1, { opacity: 1 }, { opacity: 0.25 }, 0.3);
  W.flash(tl, stab + 0.25, 'rgba(180,20,10,1)', 0.55, 0.6); sfx('impact', stab + 0.25, { gain: 0.8 }); sfx('subdrop', stab + 0.3, { gain: 0.7, dur: 1.6 });
  const zan = box(p, 'ws-label', 1120, 760, '贼怒，攒槊杀之 ——《明史》', { fontSize: '42px', color: '#d9c7a4' });
  fx.fade(zan, T(44) + 1.2, 0.4);
  F.scene('shout', T(36));
}

// ===================== I 七月解围 · 十四人 · 两年后安置桐城 =====================
F.topic(T(45) - 0.05, '七月解围');
{
  const t0 = T(45) - 0.05, t1 = T(49) + 0.2;
  const p = F.shot('relief', 8, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const leave = T(46, '撤了') - 0.3, later = T(48) - 0.2;
  const sails = []; { const r = MR.random(21); for (let i = 0; i < 26; i++) sails.push([r() * 1000 - 200, 640 + r() * 120, 0.5 + r() * 0.5, r() * 6.28]); }
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const l = W.smooth(W.clamp((t - leave) / 3, 0, 1)), lt = W.smooth(W.clamp((t - later) / 0.8, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#3a2140', '#1a1c24', lt), W.mix('#c4712f', '#4a4a52', lt), W.mix('#f7d48c', '#8a8a82', lt), 0.6);
    W.orb(g, 400, 420, 100, '#fff0c8', 'rgba(255,200,120,.4)', 520, 1 - lt * 0.7);
    W.range(g, WD, HT, { f: fB, y: 600, amp: 140, shift: t * 10, top: W.mix('#7b4a50', '#3a3a40', lt), bot: W.mix('#cf8e66', '#5a5a5a', lt) });
    water(g, 650, t, W.mix('#6a5a5a', '#2a3a44', lt), '#10161c', 'rgba(255,230,200,.2)');
    // 朱元璋的帆（左，驶入）
    sails.forEach(([x, y, s, ph]) => { const xx = x + (t - t0) * 60; g.fillStyle = '#1a0e0c'; g.beginPath(); g.moveTo(xx, y); g.lineTo(xx + 60 * s, y); g.lineTo(xx + 50 * s, y + 14 * s); g.lineTo(xx + 10 * s, y + 14 * s); g.closePath(); g.fill(); g.fillStyle = '#e8d8b0'; g.beginPath(); g.moveTo(xx + 30 * s, y - 120 * s); g.lineTo(xx + 30 * s, y - 4); g.lineTo(xx + 30 * s + 70 * s * (0.8 + 0.2 * Math.sin(t + ph)), y - 30 * s); g.closePath(); g.fill(); });
    // 洪都城（右）与离开的巨舰
    wall(g, 1300, WD + 10, 480, 700, { col: '#120c0e', rim: 'rgba(255,200,150,.5)', breach: [1600, 90, 0.4], patch: 1 });
    ship(g, 1250 + l * 700, 720, 0.6, t, { facing: 1, col: '#0a0608' });
    ship(g, 1050 + l * 900, 735, 0.5, t + 1, { facing: 1, col: '#0a0608' });
  });
  const a = box(p, 'ws-tag', 140, 200, '七月 · 太祖自将来援', { fontSize: '54px' });
  pop(a, T(45) + 0.1);
  const b = box(p, 'ws-label', 150, 310, '友谅解围，逆战于鄱阳湖', { fontSize: '46px' });
  fx.fade(b, T(46, '撤了'), 0.3);
  fx.to([a, b], T(47) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  // 十四人
  const ts = [];
  for (let i = 0; i < 14; i++) { const e = box(p, '', 200 + i * 108, 300, '', { w: 70, h: 220, background: 'linear-gradient(180deg,#3a2216,#1d100a)', border: '3px solid #8a6524', borderRadius: '12px 12px 4px 4px' }); fx.in(e, T(47, '十四') - 0.6 + i * 0.05, { opacity: 0, y: 40 }, { opacity: 1, y: 0 }, 0.35, 'expo.out'); ts.push(e); }
  const n14 = box(p, 'ws-num', 0, 560, '14人', { w: WD, textAlign: 'center', fontSize: '120px' });
  fx.rise(n14, T(47, '十四') - 0.1, 16, 0.4); sfx('tick', T(47, '十四'), { gain: 0.5 });
  const nsrc = box(p, 'ws-label', 0, 710, '“先后战死者凡十四人” ——《明史》', { w: WD, textAlign: 'center', fontSize: '40px', color: '#d9c7a4' });
  fx.fade(nsrc, T(47, '十四') + 0.3, 0.3);
  fx.to([...ts, n14, nsrc], later - 0.1, { opacity: 1 }, { opacity: 0 }, 0.35);
  const y2 = box(p, 'ws-title', 140, 230, '两年后 · 1365', { fontSize: '90px' });
  fx.rise(y2, later + 0.1, 18, 0.4);
  const tc = box(p, 'ws-tag', 150, 370, '执大都督朱文正以归，安置桐城', { fontSize: '48px' });
  pop(tc, T(48, '安置') - 0.3);
  const tsrc = box(p, 'ws-label', 160, 480, '——《明史·太祖本纪》', { fontSize: '38px', color: '#d9c7a4' });
  fx.fade(tsrc, T(48, '安置') + 0.2, 0.3);
  sfx('thud', T(48, '桐城'), { gain: 0.5 });
  F.scene('relief', T(45));
}

// ===================== J 知识卡：洪都八十五天 =====================
F.topic(T(49) - 0.1, '洪都八十五天');
{
  const t0 = T(49) - 0.1, t1 = T(51) + 0.2;
  const p = F.shot('card', 9, 0, t0, t1, { enter: 'cut' });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.3, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#05070c', '#0e1724', '#1c2a38', 0.6);
    W.mist(g, WD, t, { y: 760, h: 120, alpha: 0.3, color: 'rgba(170,200,220,.4)', seed: 91, speed: 10 });
    W.embers(g, t, { n: 30, x0: 0, x1: WD, y: 900, speed: 30, seed: 93, alpha: 0.4 });
  });
  const panel = box(p, '', 260, 180, '', { w: 1400, h: 680, background: 'rgba(8,10,16,.88)', border: '4px solid #b88a2e', borderRadius: '16px', boxShadow: '0 0 60px rgba(242,184,75,.2)' });
  const corner = box(p, 'ws-tag', 290, 200, '大明开局 · 第11集', { fontSize: '36px' });
  const title = box(p, 'ws-title', 260, 270, '洪都八十五天', { w: 1400, textAlign: 'center', fontSize: '84px' });
  const axis = box(p, '', 360, 530, '', { w: 1200, h: 6, background: '#b88a2e' });
  const nodes = [['四月', '号称六十万围城', '朱文正、邓愈、赵德胜守'], ['抚州门', '城坏三十余丈', '且筑且战'], ['小渔船', '张子明出水关', '半月到应天'], ['七月', '朱元璋来援', '陈友谅解围']];
  const ats = [T(49, '四月'), T(49, '塌了'), T(49, '小船'), T(49, '七月')];
  const els = [panel, corner, title, axis];
  nodes.forEach(([y, a, b], i) => {
    const x = 360 + i * 400;
    const dot = box(p, '', x - 18, 515, '', { w: 36, h: 36, borderRadius: '50%', background: i === 3 ? '#e5482b' : '#f2b84b', border: '4px solid #06070a' });
    const n = box(p, 'ws-num', x - 170, 420, y, { w: 340, textAlign: 'center', fontSize: '70px' });
    const l1 = box(p, 'ws-label', x - 190, 580, a, { w: 380, textAlign: 'center', fontSize: '46px' });
    const l2 = box(p, 'ws-label', x - 190, 646, b, { w: 380, textAlign: 'center', fontSize: '34px', color: '#d9c7a4' });
    [dot, n, l1, l2].forEach((e, k) => fx.in(e, ats[i] - 0.15 + k * 0.05, { opacity: 0, y: 16 }, { opacity: 1, y: 0 }, 0.35, 'expo.out'));
    sfx('tick', ats[i], { gain: 0.45 });
  });
  const src = box(p, 'ws-label', 260, 770, '据《明史》太祖本纪、邓愈传、赵德胜传、诸王传', { w: 1400, textAlign: 'center', fontSize: '34px', color: '#a89a80' });
  [panel, corner, title, axis, src].forEach((e, k) => fx.in(e, t0 + k * 0.05, { opacity: 0, scale: 0.98 }, { opacity: 1, scale: 1 }, 0.35, 'power2.out'));
  sfx('paper', t0 + 0.05, { gain: 0.5 });
  F.scene('card', T(49));
}

// ===================== K 下一集：鄱阳湖 =====================
F.topic(T(51) - 0.05, '下一集 · 鄱阳湖');
{
  const t0 = T(51) - 0.05, t1 = T(54) + 1.0;
  const p = F.shot('lake', 10, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const fl = T(53) - 0.1;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#03060c', '#0a1626', '#1a2a3a', 0.6);
    W.stars(g, WD, HT, t, 17, 100, 0.6);
    W.range(g, WD, HT, { f: fC, y: 600, amp: 80, shift: t * 6, top: '#0e1a24', bot: '#16242e' });
    water(g, 620, t, '#0a1622', '#03070c');
    drawLights(g, t, 0, 820, 1);
    g.save(); g.translate(1920, 0); g.scale(-1, 1); drawLights(g, t + 2, 0, 700, 0.7); g.restore();
    ship(g, 520, 720, 0.85, t, { lit: 0.6, rim: 'rgba(170,215,240,.35)' });
    ship(g, 1450, 730, 0.55, t + 1, { lit: 0.5, facing: -1, flag: '#b0281a' });
    if (t > fl) { const a = W.clamp(1 - (t - fl) / 1.2, 0, 1); const r = g.createRadialGradient(960, 700, 0, 960, 700, 700); r.addColorStop(0, `rgba(255,120,40,${0.5 * a})`); r.addColorStop(1, 'rgba(255,120,40,0)'); g.fillStyle = r; g.fillRect(0, 0, WD, HT); }
    W.mist(g, WD, t, { y: 680, h: 80, alpha: 0.35, color: 'rgba(150,180,200,.4)', seed: 71, speed: 18 });
  });
  const lb = box(p, 'ws-tag', 140, 200, '下一集 · 鄱阳湖', { fontSize: '54px' });
  pop(lb, T(51) + 0.1);
  const cy = box(p, 'ws-label', 150, 310, '陈友谅本人，后来怎样？', { fontSize: '56px', color: '#ffe0a0' });
  fx.rise(cy, T(52, '陈友谅') - 0.1, 14, 0.4);
  const cm = box(p, 'ws-title', 150, 400, '评论里先写出来罢', { fontSize: '72px' });
  fx.rise(cm, T(53) - 0.05, 14, 0.4);
  W.flash(tl, fl + 0.2, 'rgba(255,140,60,1)', 0.3, 0.6); sfx('subdrop', fl + 0.2, { gain: 0.5, dur: 1.2 });
  fx.to([lb, cy, cm], T(54) - 0.3, { opacity: 1 }, { opacity: 0 }, 0.3);
  F.scene('lake', T(51));
}

// ===================== L 收尾：城墙塌了又补 =====================
F.topic(T(54) - 0.1, '补过的城墙');
{
  const t0 = T(54) - 0.2, end = T.last() + 1.0 + V.endHold;
  const p = F.shot('end', 11, 0, t0, null, { dur: 0.9 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.7 });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.6, end + 0.1, (t) => {
    g.clearRect(0, 0, WD, HT);
    nightSky(g, t, 300);
    water(g, 640, t, '#0c1a26', '#04080d');
    wall(g, 260, WD - 260, 380, 860, { breach: [960, 260, 0.6], patch: 1 });
    tower(g, 960, 380, 1.1, 0.6);
    g.fillStyle = '#05070a'; g.fillRect(0, 860, WD, HT - 860);
    W.mist(g, WD, t, { y: 820, h: 70, alpha: 0.4, color: 'rgba(140,180,200,.45)', seed: 8, speed: 22 });
  });
  const l1 = box(p, 'ws-title', 0, 190, '塌了又补', { w: WD, textAlign: 'center', fontSize: '110px' });
  fx.rise(l1, T(54, '塌了') - 0.2, 18, 0.45);
  const l2 = box(p, 'ws-label', 0, 760, '城坏复完者数十丈 ——《明史》', { w: WD, textAlign: 'center', fontSize: '46px', color: '#ffe0a0' });
  fx.fade(l2, T(55) - 0.05, 0.5);
  const nx = box(p, 'ws-tag', 1240, 640, '下一集 · 鄱阳湖', { fontSize: '50px' });
  pop(nx, T.end(55) + 0.3); sfx('chime', T.end(55) + 0.3, { gain: 0.5 });
  F.scene('end', T(54));
}

F.finish();
})();
