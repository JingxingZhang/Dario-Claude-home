// 大明开局 · 第12集 · 鄱阳湖（原书第十二章《鄱阳湖！决死战！》）· 雾山画风 · 16:9 · 60 fps
(() => {
const F = Ming.film();
const { T, fx, C, M, V, tl } = F;
const W = Wushan, box = F.box, fig = F.fig;
const WD = 1920, HT = 1080;
const sfx = (n, t, o) => MR.sfx(n, Math.max(0, t), o);
const pop = (el, t, from) => fx.in(el, t, Object.assign({ opacity: 0, scale: 1.25, y: 20 }, from || {}), { opacity: 1, scale: 1, y: 0 }, 0.45, 'expo.out');
const out = (el, t, d) => fx.to(el, t, { opacity: 1 }, { opacity: 0 }, d || 0.35, 'power2.in');
const kwo = (o) => Object.assign({ back: false, x: 360, w: 1200, y: 380, size: 180, color: '#f2b84b' }, o || {});
const fA = W.fbm(1), fB = W.fbm(2), fC = W.fbm(3), fD = W.fbm(4);
const card = (p, x, y, w, idx, text) => box(p, '', x, y, `<span class="ws-num" style="font-size:60px;margin-right:16px">${idx}</span><span class="ws-label" style="font-size:52px">${text}</span>`,
  { w, h: 124, background: 'rgba(8,10,16,.82)', border: '3px solid #b88a2e', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box' });
const note = (p, x, y, text, at, o) => { const e = box(p, (o && o.cls) || 'ws-label', x, y, text, Object.assign({ fontSize: '42px', color: '#ffe0a0' }, (o && o.st) || {})); fx.fade(e, at, 0.35); return e; };

// ---------- 画法 ----------
const ship = (g, x, wl, s, t, o) => {
  o = o || {};
  g.save(); g.translate(x, wl); g.rotate(o.tilt || 0); g.scale(s * (o.facing || 1), s);
  g.fillStyle = o.col || '#06080c';
  g.beginPath(); g.moveTo(-260, -40); g.lineTo(240, -40); g.quadraticCurveTo(300, -60, 320, -110); g.lineTo(290, -40); g.quadraticCurveTo(250, 20, 180, 24); g.lineTo(-200, 24); g.quadraticCurveTo(-260, 10, -280, -60); g.closePath(); g.fill();
  g.fillRect(-200, -120, 340, 82); g.fillRect(-160, -200, 260, 82); g.fillRect(-110, -270, 160, 72);
  [[-220, -120, 380], [-180, -200, 300], [-130, -270, 200]].forEach(([a, y, w]) => { g.beginPath(); g.moveTo(a, y); g.lineTo(a + w, y); g.lineTo(a + w - 20, y - 18); g.lineTo(a + 20, y - 18); g.closePath(); g.fill(); });
  if (o.lit) { g.fillStyle = `rgba(255,160,80,${o.lit})`; for (let r = 0; r < 3; r++) for (let i = 0; i < 6 - r * 2; i++) g.fillRect(-180 + r * 40 + i * 52, -100 - r * 80, 18, 20); }
  g.strokeStyle = o.col || '#06080c'; g.lineWidth = 6; g.beginPath(); g.moveTo(-30, -290); g.lineTo(-30, -400); g.stroke();
  const wind = o.wind || 0;
  g.fillStyle = o.flag || '#7a1a12'; g.beginPath(); g.moveTo(-30, -400); for (let i = 0; i <= 8; i++) g.lineTo(-30 + i * 14 * (1 - 2 * wind), -400 + Math.sin(t * 5 + i * 0.7) * 6); g.lineTo(-30 + 112 * (1 - 2 * wind), -350); for (let i = 8; i >= 0; i--) g.lineTo(-30 + i * 14 * (1 - 2 * wind), -350 + Math.sin(t * 5 + i * 0.7) * 6); g.closePath(); g.fill();
  if (o.rim) { g.strokeStyle = o.rim; g.lineWidth = 3; g.beginPath(); g.moveTo(-200, -120); g.lineTo(140, -120); g.moveTo(-160, -200); g.lineTo(100, -200); g.moveTo(-260, -40); g.lineTo(240, -40); g.stroke(); }
  if (o.burn) { for (let i = 0; i < 4; i++) W.flame(g, -180 + i * 110, -130 - (i % 2) * 70, 1.4 * o.burn, t, 70 + i); }
  g.restore();
};
// 小战船（朱军）：x, 水线, 比例, facing
const boat = (g, x, wl, s, t, o) => {
  o = o || {};
  g.save(); g.translate(x, wl + Math.sin(t * 2.2 + x * 0.01) * 3); g.rotate(o.tilt || 0); g.scale(s * (o.facing || 1), s);
  g.fillStyle = o.col || '#0a0c10';
  g.beginPath(); g.moveTo(-120, -20); g.lineTo(110, -20); g.quadraticCurveTo(150, -30, 160, -60); g.lineTo(140, -10); g.quadraticCurveTo(110, 16, 70, 18); g.lineTo(-90, 18); g.quadraticCurveTo(-120, 8, -130, -30); g.closePath(); g.fill();
  g.fillRect(-60, -60, 90, 40);
  g.strokeStyle = o.col || '#0a0c10'; g.lineWidth = 5; g.beginPath(); g.moveTo(0, -60); g.lineTo(0, -170); g.stroke();
  g.fillStyle = o.sail || '#d8c8a0'; g.beginPath(); g.moveTo(4, -165); g.lineTo(4, -70); g.lineTo(70 * (o.windK == null ? 1 : o.windK), -90); g.closePath(); g.fill();
  if (o.rim) { g.strokeStyle = o.rim; g.lineWidth = 2.5; g.beginPath(); g.moveTo(-120, -20); g.lineTo(110, -20); g.stroke(); }
  if (o.fire) W.flame(g, 0, -40, 1.2 * o.fire, t, 90 + Math.round(x));
  g.restore();
};
const water = (g, y, t, top, bot, glint) => {
  const wg = g.createLinearGradient(0, y, 0, HT); wg.addColorStop(0, top); wg.addColorStop(1, bot); g.fillStyle = wg; g.fillRect(0, y, WD, HT - y);
  g.strokeStyle = glint || 'rgba(170,215,240,.18)'; g.lineWidth = 2;
  for (let i = 0; i < 26; i++) { const yy = y + 10 + i * i * 0.9, x = ((i * 337 + t * (20 + i * 3)) % (WD + 300)) - 150; g.beginPath(); g.moveTo(x, yy); g.lineTo(x + 80 + i * 4, yy); g.stroke(); }
};
const daySky = (g, t, red) => {
  W.sky(g, WD, HT, W.mix('#3a5a7a', '#3a0a08', red), W.mix('#9ab0b8', '#a8301a', red), W.mix('#e8d8b0', '#f2903a', red), 0.6);
  W.orb(g, 1500, 240, 80, W.mix('#fff6dc', '#ffd0a0', red), 'rgba(255,230,170,.35)', 400);
  W.range(g, WD, HT, { f: fA, y: 560, amp: 140, shift: t * 8, top: W.mix('#5a6e78', '#4a1a14', red), bot: W.mix('#7a8a88', '#6a2a1a', red) });
  W.mist(g, WD, t, { y: 580, h: 70, alpha: 0.35, color: 'rgba(255,250,235,.5)', seed: 4, speed: 12 });
};
const lake = (g, t, red, y) => water(g, y || 640, t, W.mix('#3a5a68', '#8a1a10', red), W.mix('#0e1a22', '#2a0604', red), red > 0.5 ? 'rgba(255,180,120,.25)' : 'rgba(230,240,245,.22)');
const fleet = (g, t, red, x0, n, wl, s, o) => { for (let i = 0; i < n; i++) ship(g, x0 + i * 330 * s, (wl || 720) + (i % 2) * 14, s, t + i, Object.assign({ lit: 0.3, rim: 'rgba(230,240,250,.25)' }, o || {})); };

// ===================== A 首帧钩子：巨舰如山 · 小船仰攻 · 一支流箭 · 东北风 =====================
{
  const t1 = T(6) + 0.2;
  const p = F.shot('open', 0, 0, 0, t1);
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p), fg = W.canvas(p, WD, HT);
  const red0 = T(5, '东北风') - 0.2;
  const men = [0, 1].map(() => Rig.human(sv, { look: Rig.LOOK.soldier, ground: 40 }));
  W.clock(tl, 0, t1 + 0.6, (t) => {
    const red = W.smooth(W.clamp((t - red0) / 1.6, 0, 1));
    g.clearRect(0, 0, WD, HT);
    daySky(g, t, red);
    lake(g, t, red, 600);
    for (let i = 0; i < 6; i++) ship(g, 180 + i * 330, 690 + (i % 2) * 18, 0.95, t + i, { lit: 0.2, rim: 'rgba(240,240,250,.25)', burn: red * (i % 2 ? 0.8 : 0.5) });
    // 链着的大船（铁链线）
    g.strokeStyle = 'rgba(10,10,12,.9)'; g.lineWidth = 6; g.beginPath(); for (let i = 0; i < 6; i++) { const x = 180 + i * 330; if (i) g.quadraticCurveTo(x - 165, 720, x - 60, 690); else g.moveTo(x + 60, 690); } g.stroke();
    if (red > 0) { g.fillStyle = `rgba(200,40,10,${0.18 * red})`; g.fillRect(0, 0, WD, HT); W.speedLines(g, WD, HT, t, { n: 30, speed: 2400, alpha: 0.18 * red, seed: 3, color: 'rgba(255,220,180,.6)' }); }
    // 前景小船 + 仰头的兵
    fg.clearRect(0, 0, WD, HT);
    boat(fg, 1180, 960, 2.0, t, { col: '#05070a', rim: 'rgba(240,230,210,.4)' });
    const pp = Rig.stand(t);
    men.forEach((r, i) => { const a = Object.assign({}, pp.angles, { head: -24, torso: -6 }); r.set({ x: 1060 + i * 170, y: 920 - 172 * 1.05 + pp.bob, groundY: 920, s: 1.05, facing: -1, angles: a, worldAngles: pp.worldAngles }, red > 0.4 ? W.LIGHT.fire : W.LIGHT.day); });
  });
  // 首帧文字
  const yr = box(p, 'ws-num', 130, 190, '1363', { fontSize: '140px' });
  const yl = box(p, 'ws-label', 140, 400, '鄱阳湖 · 七月', { fontSize: '50px' });
  const big = box(p, 'ws-title', 130, 470, '船楼高十余丈', { fontSize: '104px', color: '#f2efe6' });
  fx.to([yr, yl, big], T(3) - 0.2, { opacity: 1 }, { opacity: 0 }, 0.3);
  const src = box(p, 'ws-tag', 140, 200, '联巨舟为阵，望之如山 ——《明史》', { fontSize: '44px' });
  pop(src, T(2, '像山') - 0.4); out(src, T(3) - 0.15);
  const yang = box(p, 'ws-label', 140, 210, '仰攻不利', { fontSize: '72px' });
  fx.rise(yang, T(3, '仰着') - 0.1, 14, 0.35); out(yang, T(4) - 0.15);
  // 一支流箭
  const arrowAt = T(4, '流箭') - 0.3;
  const ar = F.svg(p, 0, 0, WD, HT, `<path d="M0,0 L120,-10" stroke="#06070a" stroke-width="6" stroke-linecap="round"/><path d="M120,-10 l-20,-10 l4,18 z" fill="#06070a"/>`, `0 0 ${WD} ${HT}`);
  tl.fromTo(ar, { x: 1900, y: 260, opacity: 1 }, { x: 300, y: 420, duration: 0.5, ease: 'power2.in', immediateRender: false }, arrowAt);
  gsap.set(ar, { opacity: 0 }); tl.set(ar, { opacity: 1 }, arrowAt); tl.set(ar, { opacity: 0 }, arrowAt + 0.55);
  sfx('whip', arrowAt, { gain: 0.6 });
  const dead = box(p, 'ws-label', 140, 210, '陈友谅 · 中流矢死', { fontSize: '60px', color: '#ff8a5a' });
  fx.rise(dead, T(4, '死在') - 0.1, 14, 0.35); out(dead, T(5) - 0.15);
  F.kw('东北风', T(5, '东北风'), kwo({ x: 140, w: 800, y: 210, size: 170, color: '#f2efe6', until: T(6) - 0.2 }));
  sfx('whoosh', T(5, '东北风'), { gain: 0.6, dur: 1.4 }); sfx('riser', T(5, '红了') - 0.6, { gain: 0.4, dur: 1.2 });
  F.scene('open', 0);
}

// ===================== B 开战：分船十一队 · 火炮焚舟 · 杀伤略相当 =====================
F.topic(T(6) - 0.05, '分船十一队');
{
  const t0 = T(6) - 0.05, t1 = T(9) + 1.0;
  const p = F.shot('day1', 1, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const gun = T(7, '火炮') - 0.1;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const b = W.smooth(W.clamp((t - gun) / 1.0, 0, 1));
    g.clearRect(0, 0, WD, HT);
    daySky(g, t, 0.15 * b);
    lake(g, t, 0, 560);
    for (let i = 0; i < 4; i++) ship(g, 1100 + i * 230, 640 + i * 30, 0.6, t + i, { facing: -1, lit: 0.2, burn: b * (i % 2 ? 0.9 : 0.6) });
    // 十一队小船（三角箭头阵）
    for (let r = 0; r < 11; r++) { const y = 660 + r * 22, x = 120 + ((t - t0) * 70) % 60 + (r % 2) * 40; for (let c = 0; c < 3; c++) boat(g, x + c * 120 + r * 18, y, 0.32, t + r + c, { col: '#0a0c10' }); }
    if (b > 0 && b < 1) { for (let i = 0; i < 6; i++) { const x = 700 + i * 70, y = 620 - Math.sin(i) * 40; g.fillStyle = `rgba(255,230,160,${(1 - b)})`; g.beginPath(); g.arc(x, y, 18 * (1 - b) + 4, 0, 6.28); g.fill(); } }
    if (b > 0) W.smoke(g, 1300, 500, t, { seed: 13, n: 12, alpha: 0.45 * b, scale: 2.2, color: 'rgba(60,50,50,.6)', rise: 400, drift: 120 });
  });
  const c11 = box(p, 'ws-num', 140, 200, '11队', { fontSize: '150px' });
  fx.rise(c11, T(6, '十一') - 0.15, 18, 0.35);
  const fs = box(p, 'ws-label', 150, 380, '太祖分军十一队以御之', { fontSize: '44px' });
  fx.fade(fs, T(6, '十一') + 0.3, 0.3);
  fx.to([c11, fs], T(7) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  const xd = box(p, 'ws-tag', 140, 200, '前锋 · 徐达', { fontSize: '54px' }); pop(xd, T(7, '徐达') - 0.15);
  const yt = box(p, 'ws-tag', 140, 310, '俞通海 · 火炮焚其舟数十', { fontSize: '50px' }); pop(yt, gun - 0.1);
  W.flash(tl, gun + 0.15, '#fff2d0', 0.55, 0.4); W.shake(tl, gun + 0.15, 0.5, 14); sfx('impact', gun + 0.15, { gain: 0.7 }); sfx('subdrop', gun + 0.2, { gain: 0.5, dur: 1.0 });
  fx.to([xd, yt], T(8) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  const xs = box(p, 'ws-title', 140, 220, '杀伤略相当', { fontSize: '100px' }); fx.rise(xs, T(8) - 0.05, 16, 0.4);
  F.scene('day1', T(6));
}

// ===================== C 张定边直冲 · 座船搁浅 · 常遇春一箭 =====================
F.topic(T(9) - 0.05, '张定边');
{
  const t0 = T(9) - 0.2, t1 = T(17) + 0.2;
  const p = F.shot('dingbian', 2, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.45, dur: 0.6 });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p), fg = W.canvas(p, WD, HT);
  const stuck = T(10, '卡在') - 0.2, shoot = T(12, '射中') - 0.1, surge = T(13, '水涌') - 0.3, free = T(14) - 0.1, stuck2 = T(15, '卡在') - 0.2, bump = T(16, '撞') - 0.4;
  const zhang = Rig.human(sv, { look: Rig.LOOK.general, ground: 0 }), chang = Rig.human(sv, { look: Rig.LOOK.general, ground: 0 }), zhu = Rig.human(sv, { look: Rig.LOOK.commander, ground: 0 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const ap = W.clamp((t - t0) / (shoot - t0), 0, 1), hit = t > shoot;
    const sg = W.smooth(W.clamp((t - surge) / 0.8, 0, 1)), fr = W.smooth(W.clamp((t - free) / 1.0, 0, 1));
    const s2 = W.smooth(W.clamp((t - stuck2) / 0.6, 0, 1)), bk = W.smooth(W.clamp((t - bump) / 0.6, 0, 1));
    g.clearRect(0, 0, WD, HT);
    daySky(g, t, 0.1);
    lake(g, t, 0, 600);
    // 沙洲
    g.fillStyle = '#6a5a3e'; g.beginPath(); g.ellipse(420, 820, 380, 46, 0, 0, 6.28); g.fill();
    // 朱元璋座船（左，搁浅倾斜 → 脱身）
    const zt = t > stuck ? -0.08 * (1 - fr) : 0, zx = 420 - fr * 260;
    boat(g, zx, 800 - 8 * (1 - fr), 1.25, t, { tilt: zt, sail: '#e8e0c8', rim: 'rgba(255,255,255,.4)' });
    // 张定边的船（右 → 左逼近，越来越大）
    const zs = 0.45 + 0.35 * W.smooth(ap), zxp = W.lerp(1650, 1050, W.smooth(ap)) + (hit ? (t - shoot) * 80 : 0);
    ship(g, zxp, 760, zs, t, { facing: -1, lit: 0.2, flag: '#5a1a12' });
    if (ap > 0 && ap < 1) W.speedLines(g, WD, HT, t, { n: 24, speed: 2600, alpha: 0.22, seed: 5, color: 'rgba(255,255,255,.6)' });
    // 水涌
    if (sg > 0 && sg < 1) { g.fillStyle = `rgba(230,245,250,${0.6 * (1 - sg)})`; g.beginPath(); g.ellipse(560, 800, 240 * sg + 40, 40 * sg + 6, 0, 0, 6.28); g.fill(); }
    // 常遇春的船（右下前景 → 搁浅 → 破船撞出）
    const cx = 1500 - bk * 120, ct = s2 > 0 ? 0.07 * s2 * (1 - bk) : 0;
    boat(fg, cx, 990, 1.5, t, { facing: -1, tilt: ct, col: '#05070a', rim: 'rgba(255,240,220,.4)' }), fg; // 画在前景
    // 破船
    if (t > bump - 1.6) { const k = W.clamp((t - (bump - 1.6)) / 1.6, 0, 1); boat(fg, W.lerp(1950, 1700, k), 1000, 1.0, t, { tilt: 0.3, sail: '#5a4a3a', col: '#100a08' }); }
    // 人物
    const pa = Rig.stand(t);
    zhang.set({ x: zxp - 190 * zs, y: 760 - 40 * zs - 172 * zs * 1.4 + pa.bob, groundY: 760 - 40 * zs, s: zs * 1.4, facing: -1, angles: hit ? Object.assign({}, pa.angles, { torso: 18, head: 10 }) : pa.angles, worldAngles: pa.worldAngles }, W.LIGHT.day);
    const pz = Rig.stand(t + 1);
    zhu.set({ x: zx - 30, y: 780 - 60 * 1.25 - 172 * 0.9 + pz.bob, groundY: 780 - 60 * 1.25, s: 0.9, facing: 1, angles: pz.angles, worldAngles: pz.worldAngles }, W.LIGHT.day);
    const pc = t > shoot - 1.2 && t < shoot + 0.8 ? Rig.address(t) : Rig.stand(t + 2);
    chang.set({ x: cx + 20, y: 990 - 60 * 1.5 - 172 * 0.95 + pc.bob, groundY: 990 - 60 * 1.5, s: 0.95, facing: -1, angles: pc.angles, worldAngles: pc.worldAngles }, W.LIGHT.day);
  });
  // fg 在 sv 之后建，要让常遇春在船上：把 sv 移到最上层
  p.appendChild(sv);
  const zd = box(p, 'ws-tag', 1240, 200, '陈友谅骁将 · 张定边', { fontSize: '50px' }); pop(zd, T(9, '张定边') - 0.15);
  const ff = box(p, 'ws-label', 1250, 300, '直犯太祖舟', { fontSize: '50px' }); fx.fade(ff, T(9, '直冲') - 0.1, 0.3);
  fx.to([zd, ff], T(10) - 0.1, { opacity: 1 }, { opacity: 0 }, 0.3);
  const jj = box(p, 'ws-title', 140, 200, '舟胶于沙', { fontSize: '96px', color: '#e5482b' }); fx.rise(jj, stuck, 14, 0.35); W.shake(tl, stuck + 0.2, 0.4, 10); sfx('thud', stuck + 0.2, { gain: 0.6 });
  out(jj, T(11) - 0.1);
  const near = box(p, 'ws-label', 140, 210, '越来越近', { fontSize: '64px' }); fx.fade(near, T(11) - 0.05, 0.3); out(near, T(12) - 0.1);
  sfx('riser', T(11) - 0.2, { gain: 0.45, dur: 1.4 });
  const cy = box(p, 'ws-tag', 1240, 200, '常遇春', { fontSize: '56px' }); pop(cy, T(12, '常遇春') - 0.15);
  const arr = F.svg(p, 0, 0, WD, HT, `<path d="M0,0 L-110,-6" stroke="#06070a" stroke-width="6" stroke-linecap="round"/>`, `0 0 ${WD} ${HT}`);
  gsap.set(arr, { opacity: 0 }); tl.set(arr, { opacity: 1 }, shoot - 0.35); tl.fromTo(arr, { x: 1450, y: 760 }, { x: 1150, y: 520, duration: 0.35, ease: 'none', immediateRender: false }, shoot - 0.35); tl.set(arr, { opacity: 0 }, shoot);
  W.flash(tl, shoot, '#fff6e0', 0.5, 0.35); sfx('whip', shoot - 0.35, { gain: 0.6 }); sfx('hit', shoot, { gain: 0.7 });
  const sz = box(p, 'ws-title', 140, 200, '射中定边', { fontSize: '96px' }); fx.rise(sz, shoot + 0.05, 14, 0.35);
  fx.to([cy, sz], T(13) - 0.1, { opacity: 1 }, { opacity: 0 }, 0.3);
  const ss = box(p, 'ws-label', 140, 210, '舟骤进，水涌，太祖舟乃得脱', { fontSize: '50px' }); fx.fade(ss, T(13) + 0.1, 0.3); out(ss, T(15) - 0.15);
  sfx('slide', surge, { gain: 0.5, dur: 1.0 });
  const c2 = box(p, 'ws-label', 140, 210, '遇春舟复胶于浅', { fontSize: '56px' }); fx.fade(c2, T(15) + 0.1, 0.3); out(c2, T(16) - 0.1);
  const c3 = box(p, 'ws-label', 140, 210, '有败舟顺流下，触遇春舟乃脱', { fontSize: '52px', color: '#ffe0a0' }); fx.fade(c3, T(16) + 0.2, 0.3);
  sfx('thud', bump + 0.6, { gain: 0.5 });
  const src = box(p, 'ws-label', 150, 300, '——《明史·常遇春传》', { fontSize: '36px', color: '#fff3df' }); fx.fade(src, T(16) + 0.8, 0.3);
  F.scene('dingbian', T(9));
}

// ===================== D 第二天：巨舰尽出 · 斩退缩者 · 丁普郎 =====================
F.topic(T(17) - 0.05, '第二天');
{
  const t0 = T(17) - 0.05, t1 = T(25) + 0.2;
  const p = F.shot('day2', 3, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const ding0 = T(21) - 0.2, dead = T(23) - 0.1;
  const zhu = Rig.human(sv, { look: Rig.LOOK.commander, ground: 0 }), ding = Rig.human(sv, { look: Rig.LOOK.general, ground: 0 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const dk = t > ding0 ? 1 : 0, dd = W.smooth(W.clamp((t - dead) / 1.0, 0, 1));
    g.clearRect(0, 0, WD, HT);
    const sun = W.clamp((t - ding0) / (t1 - ding0), 0, 1);
    W.sky(g, WD, HT, '#4a5a72', W.mix('#a8b0b0', '#c89060', dk * sun), W.mix('#e8d8b0', '#f0b060', dk * sun), 0.6);
    W.orb(g, 400 + sun * 1100 * dk, 260 - Math.sin(sun * 3.14) * 80 * dk, 70, '#fff6dc', 'rgba(255,230,170,.35)', 360);
    lake(g, t, 0, 560);
    fleet(g, t, 0, 520, 5, 700, 0.95, { facing: -1 });
    boat(g, 300, 900, 1.6, t, { sail: '#e8e0c8', rim: 'rgba(255,255,255,.4)' });
    const pa = dk ? Rig.stand(t) : Rig.address(t);
    const who = dk ? ding : zhu, other = dk ? zhu : ding;
    who.set({ x: 290, y: 900 - 60 * 1.6 - 172 * 1.15 + pa.bob, groundY: 900 - 60 * 1.6, s: 1.15, facing: 1, angles: dd > 0 ? Object.assign({}, pa.angles, { head: 0 }) : pa.angles, worldAngles: pa.worldAngles }, dk ? W.lightMix(W.LIGHT.day, W.LIGHT.fire, dd) : W.LIGHT.day);
    other.set({ x: -500, y: 0, groundY: 0, s: 0.01, angles: pa.angles }, W.LIGHT.day);
    if (dd > 0) { g.fillStyle = `rgba(10,4,4,${0.35 * dd})`; g.fillRect(0, 0, WD, HT); }
  });
  const all = box(p, 'ws-tag', 560, 200, '友谅悉巨舰出战', { fontSize: '54px' }); pop(all, T(17) + 0.1);
  const pa1 = box(p, 'ws-title', 560, 310, '有怖色', { fontSize: '110px' }); fx.rise(pa1, T(18, '怕色') - 0.2, 14, 0.4);
  fx.to([all, pa1], T(19) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  const mh = box(p, 'ws-label', 560, 210, '太祖亲麾之，不前', { fontSize: '56px' }); fx.fade(mh, T(19) + 0.05, 0.3);
  const zh = box(p, 'ws-title', 560, 310, '斩退缩者十余人', { fontSize: '86px', color: '#e5482b' }); fx.rise(zh, T(20, '杀了') - 0.1, 14, 0.4); sfx('impact', T(20, '杀了'), { gain: 0.6 });
  fx.to([mh, zh], ding0 - 0.1, { opacity: 1 }, { opacity: 0 }, 0.3);
  const dp = box(p, 'ws-tag', 560, 200, '丁普郎 · 原陈友谅部将', { fontSize: '52px' }); pop(dp, T(21, '丁普郎') - 0.1);
  const cs = box(p, 'ws-label', 560, 310, '自辰至午，身被十余创', { fontSize: '56px' }); fx.fade(cs, T(22) + 0.1, 0.3);
  const sd = box(p, 'ws-title', 560, 400, '首脱犹直立', { fontSize: '96px', color: '#f2efe6' }); fx.rise(sd, T(23) - 0.05, 14, 0.4);
  const sh = box(p, 'ws-title', 560, 530, '敌惊为神', { fontSize: '96px', color: '#f2b84b' }); fx.rise(sh, T(24, '神') - 0.3, 14, 0.4);
  sfx('subdrop', T(23), { gain: 0.5, dur: 1.4 });
  const src = box(p, 'ws-label', 570, 680, '——《明史·赵德胜传》附丁普郎', { fontSize: '36px', color: '#fff3df' }); fx.fade(src, T(24) + 0.4, 0.3);
  F.scene('day2', T(17));
}

// ===================== E 东北风 · 七舟火攻 · 湖水尽赤 =====================
F.topic(T(25) - 0.05, '东北风');
{
  const t0 = T(25) - 0.05, t1 = T(33) + 1.0;
  const p = F.shot('fire', 4, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const wind = T(25, '东北风') - 0.2, go = T(27) - 0.3, hit = T(28, '撞向') + 0.2, redAt = T(30) - 0.2, dim = T(32) - 0.3;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const w = W.smooth(W.clamp((t - wind) / 0.6, 0, 1)), m = W.clamp((t - go) / (hit - go), 0, 1), b = W.smooth(W.clamp((t - hit) / 1.6, 0, 1));
    const red = W.smooth(W.clamp((t - redAt) / 0.8, 0, 1)) * (1 - 0.5 * W.smooth(W.clamp((t - dim) / 2, 0, 1)));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#4a3a4a', '#2a0604', Math.max(b, red)), W.mix('#c08060', '#a01a0a', Math.max(b, red)), W.mix('#f0c080', '#f06a2a', Math.max(b, red)), 0.6);
    W.orb(g, 1650, 520, 90, '#ffd8a0', 'rgba(255,170,90,.45)', 520);
    W.range(g, WD, HT, { f: fB, y: 580, amp: 120, shift: t * 10, top: '#4a2026', bot: '#7a3a2e' });
    lake(g, t, Math.max(red, b * 0.6), 620);
    for (let i = 0; i < 5; i++) ship(g, 1000 + i * 210, 700 + (i % 2) * 20, 0.7, t + i, { facing: -1, lit: 0.2, wind: w, burn: b * (0.6 + 0.4 * (i % 2)) });
    if (w > 0) W.speedLines(g, WD, HT, t, { n: 40, speed: 2000, alpha: 0.2 * w, seed: 9, color: 'rgba(255,255,255,.6)' });
    for (let i = 0; i < 7; i++) { const x = W.lerp(100 + i * 50, 980 + (i % 3) * 60, m), y = 760 + (i % 4) * 30; if (m < 1) boat(g, x, y, 0.5, t + i, { windK: w ? 1.2 : 0.6, fire: t > go ? 0.6 : 0, col: '#0a0605' }); }
    if (b > 0) { W.smoke(g, 1300, 560, t, { seed: 41, n: 16, alpha: 0.55 * b, scale: 3.2, color: 'rgba(40,20,20,.65)', rise: 600, drift: 260 }); W.embers(g, t, { n: Math.round(220 * b), x0: 900, x1: 1900, y: 720, speed: 160, seed: 43 }); }
    if (red > 0) { g.fillStyle = `rgba(190,30,10,${0.35 * red})`; g.fillRect(0, 0, WD, HT); }
  });
  F.kw('东北风', T(25, '东北风'), kwo({ x: 140, w: 800, y: 200, size: 170, color: '#f2efe6', until: T(26) - 0.1 }));
  sfx('whoosh', wind, { gain: 0.7, dur: 1.8 });
  const sev = box(p, 'ws-num', 140, 200, '七舟', { fontSize: '140px' }); fx.rise(sev, T(26, '七条') - 0.2, 16, 0.35);
  const fy = box(p, 'ws-label', 150, 370, '实火药芦苇中', { fontSize: '50px' }); fx.fade(fy, T(27) - 0.05, 0.3);
  fx.to([sev, fy], hit - 0.2, { opacity: 1 }, { opacity: 0 }, 0.3);
  W.flash(tl, hit, '#fff0c0', 0.7, 0.5); W.shake(tl, hit, 0.9, 24); sfx('impact', hit, { gain: 0.9 }); sfx('subdrop', hit + 0.05, { gain: 0.8, dur: 1.8 });
  const fl = box(p, 'ws-title', 140, 210, '风烈火炽，烟焰涨天', { fontSize: '84px' }); fx.rise(fl, T(29) - 0.05, 14, 0.35); out(fl, T(30) - 0.15);
  F.kw('湖水尽赤', T(30, '全红'), kwo({ x: 360, w: 1200, y: 300, size: 190, color: '#ff8a5a', until: T(31) - 0.1 }));
  const n2k = box(p, 'ws-label', 140, 220, '斩首二千余级，焚溺死者无算', { fontSize: '56px' }); fx.fade(n2k, T(31) + 0.1, 0.3);
  const src = box(p, 'ws-label', 150, 310, '——《明史·太祖本纪》', { fontSize: '38px', color: '#fff3df' }); fx.fade(src, T(31) + 0.6, 0.3);
  fx.to([n2k, src], T(32) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  const fu = box(p, 'ws-tag', 140, 210, '辛卯，复战，友谅复大败', { fontSize: '52px' }); pop(fu, T(32) + 0.05);
  F.scene('fire', T(25));
}

// ===================== F 两道命令（冷知识并置）· 站队题 =====================
F.topic(T(33) - 0.1, '两道命令');
{
  const t0 = T(33) - 0.2, t1 = T(39) + 0.2;
  const p = F.shot('orders', 5, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.6 });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const chen = Rig.human(sv, { look: Rig.LOOK.general, ground: 60 }), zhu = Rig.human(sv, { look: Rig.LOOK.commander, ground: 60 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    // 左：冷夜（陈）；右：暖光（朱）
    g.save(); g.beginPath(); g.rect(0, 0, 960, HT); g.clip();
    W.sky(g, WD, HT, '#05060c', '#1a1428', '#2a1a28', 0.6); lake(g, t, 0.15, 640); ship(g, 480, 720, 0.8, t, { facing: 1, lit: 0.4 });
    g.restore();
    g.save(); g.beginPath(); g.rect(960, 0, 960, HT); g.clip();
    W.sky(g, WD, HT, '#3a2140', '#c4712f', '#f7d48c', 0.6); lake(g, t, 0, 640); boat(g, 1440, 760, 1.2, t, { sail: '#e8e0c8' });
    g.restore();
    g.fillStyle = '#06070a'; g.fillRect(956, 0, 8, HT);
    const pa = Rig.address(t), pb = Rig.stand(t);
    chen.set({ x: 640, y: 860 - 172 * 1.2 + pa.bob, groundY: 860, s: 1.2, facing: -1, angles: pa.angles, worldAngles: pa.worldAngles }, W.LIGHT.moon);
    zhu.set({ x: 1300, y: 860 - 172 * 1.2 + pb.bob, groundY: 860, s: 1.2, facing: 1, angles: pb.angles, worldAngles: pb.worldAngles }, W.LIGHT.dawn);
  });
  const sw = box(p, 'ws-label', 140, 200, '敛舟自守，不敢更战', { fontSize: '50px' }); fx.fade(sw, T(33) + 0.1, 0.3); out(sw, T(34) - 0.1);
  const jw = box(p, 'ws-tag', 140, 200, '左、右二金吾将军皆降', { fontSize: '50px' }); pop(jw, T(34) - 0.05); out(jw, T(35) - 0.15);
  const L = box(p, 'ws-title', 140, 200, '尽杀所获将士', { fontSize: '76px', color: '#ff8a5a' }); fx.rise(L, T(35, '全杀') - 0.3, 14, 0.4);
  const Ls = box(p, 'ws-label', 150, 300, '陈友谅', { fontSize: '46px' }); fx.fade(Ls, T(35) + 0.1, 0.3);
  const R = box(p, 'ws-title', 1100, 200, '悉还所俘', { fontSize: '76px', color: '#ffe0a0' }); fx.rise(R, T(36, '放了') - 0.3, 14, 0.4);
  const R2 = box(p, 'ws-label', 1110, 300, '伤者傅以善药 · 朱元璋', { fontSize: '46px' }); fx.fade(R2, T(36, '敷上') - 0.2, 0.3);
  F.kw('还俘', T(36, '放了') + 0.4, kwo({ x: 1100, w: 600, y: 380, size: 140, until: T(37) - 0.1 }));
  const src = box(p, 'ws-label', 0, 470, '——《明史·太祖本纪》', { w: WD, textAlign: 'center', fontSize: '36px', color: '#fff3df' }); fx.fade(src, T(36) + 1.0, 0.3);
  fx.to([L, Ls, R, R2, src], T(37) - 0.2, { opacity: 1 }, { opacity: 0.0 }, 0.3);
  // 站队题
  const opts = [['①', '船太大', T(37, '船太大')], ['②', '风不对', T(37, '风不对')], ['③', '人心散了', T(37, '人心')]];
  opts.forEach(([i, txt, at], k) => { const c = card(p, 170 + k * 540, 300, 500, i, txt); fx.in(c, at - 0.15, { opacity: 0, y: 30 }, { opacity: 1, y: 0 }, 0.35, 'expo.out'); sfx('pop', at, { gain: 0.4 }); });
  const qq = box(p, 'ws-title', 0, 180, '陈友谅输在哪一样？', { w: WD, textAlign: 'center', fontSize: '84px', color: '#f2b84b' });
  fx.rise(qq, T(38) - 0.1, 16, 0.4); sfx('ding', T(38, '哪一样'), { gain: 0.45 });
  F.scene('orders', T(33));
}

// ===================== G 湖口：粮尽突围 · 中流矢死 · 陈理降 =====================
F.topic(T(39) - 0.05, '湖口');
{
  const t0 = T(39) - 0.05, t1 = T(46) + 0.2;
  const p = F.shot('hukou', 6, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const cyc0 = T(39), cyc1 = T(40) - 0.1, run = T(41) - 0.2, meet = T(42) - 0.1, shot = T(43, '射中') - 0.35, fall = T(43, '死了') - 0.3, flee = T(44) - 0.1, gate = T(45) - 0.2;
  const chen = Rig.human(sv, { look: Rig.LOOK.general, ground: 0 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const cy = t > cyc0 && t < cyc1 ? 0.5 + 0.5 * Math.sin((t - cyc0) * 3.4) : 0.3;
    const r = W.clamp((t - run) / 3.2, 0, 1), d = W.smooth(W.clamp((t - fall) / 0.6, 0, 1)), gk = W.smooth(W.clamp((t - gate) / 0.8, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#0a0e18', '#4a6a8a', cy), W.mix('#1a2a3a', '#a0b0b0', cy), W.mix('#2a3a44', '#e0d0a8', cy), 0.6);
    if (t > cyc0 && t < cyc1) { const a = (t - cyc0) * 3.4; W.orb(g, 960 + Math.cos(a) * 700, 560 - Math.sin(a) * 340, 54, '#fff6dc', 'rgba(255,240,200,.3)', 240); }
    W.range(g, WD, HT, { f: fC, y: 560, amp: 180, shift: t * 10, top: '#1a2a34', bot: '#2a3a44' });
    // 湖口：两岸山夹住的水道
    lake(g, t, 0, 620);
    g.fillStyle = '#0a1016'; g.beginPath(); g.moveTo(1200, 620); g.lineTo(1500, 600); g.lineTo(1920, 640); g.lineTo(1920, 1080); g.lineTo(1380, 1080); g.closePath(); g.fill();
    if (gk === 0) {
      // 陈友谅的一百条船冲向湖口（右上）
      for (let i = 0; i < 14; i++) { const x = W.lerp(200 + (i % 7) * 110, 900 + (i % 7) * 70, r), y = 700 + Math.floor(i / 7) * 60; ship(g, x, y, 0.28, t + i, { facing: 1, lit: 0.2 }); }
      // 朱元璋的船守在上游（右），顺流迎上
      const m = W.clamp((t - meet) / 1.2, 0, 1);
      for (let i = 0; i < 8; i++) boat(g, W.lerp(1700, 1250, m) + (i % 4) * 60, 680 + Math.floor(i / 4) * 70, 0.42, t + i, { facing: -1, sail: '#e8e0c8' });
      // 陈友谅旗舰
      if (t > meet) ship(g, 980, 800, 0.7, t, { facing: 1, lit: 0.3, flag: '#7a1a12', rim: 'rgba(230,240,250,.3)' });
    } else {
      // 武昌城门打开
      g.fillStyle = '#0b0d12'; g.fillRect(400, 380, 1120, 480); g.fillStyle = `rgba(255,220,150,${0.85 * gk})`; g.fillRect(860, 600, 200, 260);
      g.fillStyle = '#1e0e0a'; g.fillRect(860 - 100 * gk, 600, 100, 260); g.fillRect(960 + 100 * gk, 600, 100, 260);
    }
    sv.style.opacity = t > meet && gk === 0 ? 1 - d * 0.9 : 0;
    const pa = Rig.address(t);
    chen.set({ x: 1000, y: 800 - 270 * 0.7 - 172 * 1.0 + pa.bob + d * 60, groundY: 800 - 270 * 0.7, s: 1.0, facing: 1, angles: d > 0 ? Object.assign({}, pa.angles, { torso: -40 * d, head: -20 * d }) : pa.angles, worldAngles: pa.worldAngles }, W.LIGHT.moon);
  });
  const hd = box(p, 'ws-label', 140, 200, '相持 · 将近一月', { fontSize: '56px' }); fx.fade(hd, T(39) + 0.1, 0.3); out(hd, T(40) - 0.1);
  const sj = box(p, 'ws-tag', 140, 200, '八月 · 友谅食尽', { fontSize: '54px' }); pop(sj, T(40) + 0.05); out(sj, T(41) - 0.1);
  const bai = box(p, 'ws-label', 140, 200, '以百艘突围 ——《明史·常遇春传》', { fontSize: '48px' }); fx.fade(bai, T(41) + 0.05, 0.3); out(bai, T(42) - 0.1);
  const sl = box(p, 'ws-label', 140, 200, '太祖命扼上流，顺流搏战', { fontSize: '52px' }); fx.fade(sl, T(42) + 0.05, 0.3); out(sl, shot - 0.1);
  const ar = F.svg(p, 0, 0, WD, HT, `<path d="M0,0 L-110,-14" stroke="#06070a" stroke-width="6" stroke-linecap="round"/>`, `0 0 ${WD} ${HT}`);
  gsap.set(ar, { opacity: 0 }); tl.set(ar, { opacity: 1 }, shot); tl.fromTo(ar, { x: 1800, y: 300 }, { x: 1060, y: 410, duration: 0.35, ease: 'none', immediateRender: false }, shot); tl.set(ar, { opacity: 0 }, shot + 0.36);
  W.flash(tl, shot + 0.35, '#ffffff', 0.5, 0.35); sfx('whip', shot, { gain: 0.6 }); sfx('hit', shot + 0.35, { gain: 0.7 }); sfx('subdrop', fall + 0.3, { gain: 0.7, dur: 1.6 });
  const zs = box(p, 'ws-title', 140, 200, '中流矢死', { fontSize: '110px', color: '#e5482b' }); fx.rise(zs, T(43, '死了') - 0.1, 14, 0.4);
  out(zs, flee - 0.15);
  const zd = box(p, 'ws-label', 140, 200, '张定边以其子理奔武昌', { fontSize: '54px' }); fx.fade(zd, flee + 0.05, 0.3); out(zd, gate - 0.1);
  const xj = box(p, 'ws-tag', 140, 200, '1364年二月 · 陈理降', { fontSize: '54px' }); pop(xj, T(45) + 0.1); sfx('slide', gate, { gain: 0.5 });
  F.scene('hukou', T(39));
}

// ===================== H 知识卡：鄱阳湖一仗 =====================
F.topic(T(46) - 0.1, '鄱阳湖一仗');
{
  const t0 = T(46) - 0.1, t1 = T(48) + 0.2;
  const p = F.shot('card', 7, 0, t0, t1, { enter: 'cut' });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.3, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#05070c', '#0e1724', '#1c2a38', 0.6);
    W.mist(g, WD, t, { y: 760, h: 120, alpha: 0.3, color: 'rgba(170,200,220,.4)', seed: 91, speed: 10 });
    W.embers(g, t, { n: 30, x0: 0, x1: WD, y: 900, speed: 30, seed: 93, alpha: 0.4 });
  });
  const panel = box(p, '', 260, 180, '', { w: 1400, h: 680, background: 'rgba(8,10,16,.88)', border: '4px solid #b88a2e', borderRadius: '16px', boxShadow: '0 0 60px rgba(242,184,75,.2)' });
  const corner = box(p, 'ws-tag', 290, 200, '大明开局 · 第12集', { fontSize: '36px' });
  const title = box(p, 'ws-title', 260, 270, '鄱阳湖一仗', { w: 1400, textAlign: 'center', fontSize: '84px' });
  const axis = box(p, '', 360, 530, '', { w: 1200, h: 6, background: '#b88a2e' });
  const nodes = [['开战', '分船十一队', '张定边直犯太祖舟'], ['火攻', '东北风 · 七舟', '湖水尽赤'], ['两道命令', '陈：尽杀所俘', '朱：悉还所俘'], ['湖口', '八月 · 粮尽突围', '陈友谅中流矢死']];
  const ats = [T(46, '开战'), T(46, '火攻'), T(46, '两道'), T(46, '湖口')];
  nodes.forEach(([y, a, b], i) => {
    const x = 360 + i * 400;
    const dot = box(p, '', x - 18, 515, '', { w: 36, h: 36, borderRadius: '50%', background: i === 3 ? '#e5482b' : '#f2b84b', border: '4px solid #06070a' });
    const n = box(p, 'ws-num', x - 180, 420, y, { w: 360, textAlign: 'center', fontSize: '66px' });
    const l1 = box(p, 'ws-label', x - 190, 580, a, { w: 380, textAlign: 'center', fontSize: '44px' });
    const l2 = box(p, 'ws-label', x - 190, 646, b, { w: 380, textAlign: 'center', fontSize: '34px', color: '#d9c7a4' });
    [dot, n, l1, l2].forEach((e, k) => fx.in(e, ats[i] - 0.15 + k * 0.05, { opacity: 0, y: 16 }, { opacity: 1, y: 0 }, 0.35, 'expo.out'));
    sfx('tick', ats[i], { gain: 0.45 });
  });
  const src = box(p, 'ws-label', 260, 770, '据《明史》太祖本纪、常遇春传、赵德胜传', { w: 1400, textAlign: 'center', fontSize: '34px', color: '#a89a80' });
  [panel, corner, title, axis, src].forEach((e, k) => fx.in(e, t0 + k * 0.05, { opacity: 0, scale: 0.98 }, { opacity: 1, scale: 1 }, 0.35, 'power2.out'));
  sfx('paper', t0 + 0.05, { gain: 0.5 });
  F.scene('card', T(46));
}

// ===================== I 下一集：张士诚 =====================
F.topic(T(48) - 0.05, '下一集 · 张士诚');
{
  const t0 = T(48) - 0.05, t1 = T(51) + 1.0;
  const p = F.shot('next', 8, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const zs = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 0 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#1a2230', '#5a6a78', '#b8b0a0', 0.6);
    W.range(g, WD, HT, { f: fD, y: 620, amp: 80, shift: t * 6, top: '#3a4a54', bot: '#5a6a70' });
    water(g, 660, t, '#4a5a64', '#141c22', 'rgba(240,240,240,.22)');
    // 盐船：船上堆着盐袋
    const x = 700 + (t - t0) * 30;
    boat(g, x, 820, 1.7, t, { sail: '#d8d0c0' });
    g.fillStyle = '#e8e4da'; for (let i = 0; i < 5; i++) { g.beginPath(); g.ellipse(x - 120 + i * 48, 770 - (i % 2) * 14, 30, 18, 0, 0, 6.28); g.fill(); }
    const pa = Rig.stand(t);
    zs.set({ x: x + 110, y: 820 - 20 * 1.7 - 172 * 0.95 + pa.bob, groundY: 820 - 20 * 1.7, s: 0.95, facing: 1, angles: pa.angles, worldAngles: pa.worldAngles }, W.LIGHT.day);
  });
  const lb = box(p, 'ws-tag', 140, 200, '下一集 · 张士诚', { fontSize: '54px' }); pop(lb, T(48) + 0.1);
  const yw = box(p, 'ws-label', 150, 310, '以操舟运盐为业 ——《明史·张士诚传》', { fontSize: '44px' }); fx.fade(yw, T(48, '卖盐') - 0.1, 0.3);
  const q = box(p, 'ws-title', 140, 400, '他最后怎么死的？', { fontSize: '80px', color: '#ffe0a0' }); fx.rise(q, T(49) - 0.05, 14, 0.4);
  const cm = box(p, 'ws-label', 150, 520, '评论里先写出来罢', { fontSize: '56px' }); fx.fade(cm, T(50) - 0.05, 0.3);
  fx.to([lb, yw, q, cm], T(51) - 0.3, { opacity: 1 }, { opacity: 0 }, 0.3);
  F.scene('next', T(48));
}

// ===================== J 收尾：湖水红了，又清了 =====================
F.topic(T(51) - 0.1, '湖水又清了');
{
  const t0 = T(51) - 0.2, end = T.last() + 1.0 + V.endHold;
  const p = F.shot('end', 9, 0, t0, null, { dur: 0.9 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.7 });
  const g = W.canvas(p, WD, HT);
  const clear = T(52) - 0.2;
  W.clock(tl, t0 - 0.6, end + 0.1, (t) => {
    const red = 1 - W.smooth(W.clamp((t - clear) / 1.8, 0, 1));
    g.clearRect(0, 0, WD, HT);
    daySky(g, t, red * 0.8);
    lake(g, t, red, 600);
    for (let i = 0; i < 3; i++) ship(g, 300 + i * 600, 720, 0.7, t + i, { col: W.mix('#06080c', '#2a2a2e', 1 - red), lit: 0, burn: red * 0.4 });
    W.mist(g, WD, t, { y: 760, h: 90, alpha: 0.35 + 0.2 * (1 - red), color: 'rgba(240,245,245,.5)', seed: 8, speed: 16 });
  });
  const l1 = box(p, 'ws-title', 0, 200, '湖水尽赤', { w: WD, textAlign: 'center', fontSize: '110px', color: '#ff8a5a' });
  fx.rise(l1, T(51, '红') - 0.3, 18, 0.45);
  const l2 = box(p, 'ws-title', 0, 340, '后来，又清了', { w: WD, textAlign: 'center', fontSize: '80px' });
  fx.fade(l2, T(52) - 0.05, 0.6);
  fx.to(l1, T(52), { opacity: 1 }, { opacity: 0.25 }, 1.2);
  const nx = box(p, 'ws-tag', 1240, 640, '下一集 · 张士诚', { fontSize: '50px' });
  pop(nx, T.end(52) + 0.3); sfx('chime', T.end(52) + 0.3, { gain: 0.5 });
  F.scene('end', T(51));
}

F.finish();
})();
