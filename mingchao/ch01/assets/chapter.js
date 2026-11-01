// 大明开局 · 第01集 · 童年（原书第一章）· 雾山画风 · 16:9 · 60 fps
// 结构：每个镜头 = F.shot 格子 + W.canvas 背景（W.clock 逐帧画）+ 可选 Rig 骨骼角色 + DOM 文字
(() => {
const F = Ming.film();
const { T, fx, C, M, V, tl } = F;
const W = Wushan, box = F.box, fig = F.fig;
const WD = 1920, HT = 1080;
const sfx = (n, t, o) => MR.sfx(n, Math.max(0, t), o);
const pop = (el, t, from) => fx.in(el, t, Object.assign({ opacity: 0, scale: 1.25, y: 20 }, from || {}), { opacity: 1, scale: 1, y: 0 }, 0.45, 'expo.out');
const out = (el, t, d) => fx.to(el, t, { opacity: 1 }, { opacity: 0 }, d || 0.35, 'power2.in');
const dim = (el, t, to, d) => fx.to(el, t, { opacity: 1 }, { opacity: to }, d || 0.6, 'power2.inOut');
const sil = (p, x, y, w, h, inner, sc, cls, flip, color) => { const e = fig(p, x, y, w, h, inner, sc, flip, color || '#07080b'); if (cls) e.classList.add(cls); return e; };
const fA = W.fbm(1), fB = W.fbm(2), fC = W.fbm(3), fD = W.fbm(4), fE = W.fbm(5), fG = W.fbm(6);
const kwo = (o) => Object.assign({ back: false, x: 360, w: 1200, y: 380, size: 180, color: '#f2b84b' }, o || {});
// 牌位：深木底 + 金字竖排
const tablet = (p, x, y, title, num) => {
  const e = box(p, '', x, y, `<div style="font:500 34px var(--kai);color:#d9c7a4;letter-spacing:6px;writing-mode:vertical-rl;margin:0 auto 14px;height:96px">${title}</div><div class="ws-num" style="font-size:96px;writing-mode:vertical-rl;margin:0 auto;letter-spacing:8px">${num}</div>`,
    { w: 170, h: 470, background: 'linear-gradient(180deg,#3a2216,#1d100a)', border: '4px solid #8a6524', borderRadius: '18px 18px 6px 6px', boxShadow: '0 0 40px rgba(255,150,60,.25), inset 0 0 30px rgba(0,0,0,.6)', paddingTop: '26px', boxSizing: 'border-box', textAlign: 'center' });
  return e;
};
// 选项卡（站队题）
const card = (p, x, y, w, idx, text) => box(p, '', x, y, `<span class="ws-num" style="font-size:64px;margin-right:18px">${idx}</span><span class="ws-label" style="font-size:56px">${text}</span>`,
  { w, h: 130, background: 'rgba(8,10,16,.82)', border: '3px solid #b88a2e', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box' });
// 夜里的茅屋（canvas 画）：x 中心、地面 gy、比例 s；glow 0–1 为屋里红光，lamp 为油灯
const hut = (g, x, gy, s, glow, lamp, t) => {
  g.save(); g.translate(x, gy); g.scale(s, s);
  if (glow > 0.01) { const r = g.createRadialGradient(0, -110, 0, 0, -110, 520); r.addColorStop(0, `rgba(255,70,30,${0.55 * glow})`); r.addColorStop(1, 'rgba(255,70,30,0)'); g.fillStyle = r; g.fillRect(-560, -640, 1120, 700); }
  g.fillStyle = '#0a0b0e'; g.fillRect(-160, -150, 320, 150);
  const win = (wx) => { g.fillStyle = glow > 0.01 ? `rgba(255,${Math.round(90 + 60 * (1 - glow))},40,${0.35 + 0.65 * glow})` : `rgba(255,190,110,${lamp * (0.75 + 0.15 * Math.sin(t * 9))})`; g.fillRect(wx, -112, 46, 40); };
  win(-120); win(74);
  g.fillStyle = glow > 0.01 ? `rgba(255,120,60,${0.2 + 0.5 * glow})` : `rgba(255,190,110,${0.35 * lamp})`; g.fillRect(-24, -86, 48, 86);
  g.fillStyle = '#06070a'; g.beginPath(); g.moveTo(-210, -128); g.quadraticCurveTo(-90, -230, 0, -290); g.quadraticCurveTo(90, -230, 210, -128); g.quadraticCurveTo(0, -150, -210, -128); g.fill();
  g.strokeStyle = glow > 0.01 ? `rgba(255,140,80,${0.5 + 0.4 * glow})` : 'rgba(170,215,240,.55)'; g.lineWidth = 3;
  g.beginPath(); g.moveTo(-210, -128); g.quadraticCurveTo(-90, -230, 0, -290); g.quadraticCurveTo(90, -230, 210, -128); g.stroke();
  g.restore();
};
const nightBase = (g, t, k) => {
  W.sky(g, WD, HT, '#03070f', '#0e2134', '#24414f', 0.62);
  W.stars(g, WD, HT, t, 7, 140, 0.9);
  W.orb(g, 1560 - t * 2, 200, 66, '#f3f0df', 'rgba(150,200,255,.35)', 320);
  W.range(g, WD, HT, { f: fA, y: 600, amp: 260, shift: t * 12 + (k || 0), top: '#1d3446', bot: '#2a4a57', rim: 'rgba(160,210,240,.25)' });
  W.mist(g, WD, t, { y: 600, h: 90, alpha: 0.35, color: 'rgba(170,205,220,.55)', seed: 4, speed: 16 });
  W.range(g, WD, HT, { f: fB, y: 760, amp: 160, shift: t * 24 + (k || 0) * 2, top: '#101d2a', bot: '#1a3140', scale: 0.005 });
};
const ground = (g, y, col) => { g.fillStyle = col || '#05070b'; g.fillRect(0, y, WD, HT - y); };

// ===================== A 首帧钩子：1328 · 茅屋 · 重八 · 龙椅 =====================
{
  const t1 = T(5) + 0.2;
  const p = F.shot('open', 0, 0, 0, t1);
  const g = W.canvas(p, WD, HT);
  const throneAt = T(3, '龙椅') - 0.3;
  W.clock(tl, 0, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    nightBase(g, t);
    ground(g, 860);
    hut(g, 560, 862, 1.15, 0, 1, t);
    W.smoke(g, 560, 520, t, { seed: 3, n: 7, alpha: 0.35, scale: 0.8, color: 'rgba(120,130,150,.5)', rise: 300 });
    const k = W.smooth(W.clamp((t - throneAt) / 1.2, 0, 1));
    if (k > 0) { W.rays(g, 1420, 560, t, { n: 16, len: 900, color: `rgba(255,200,110,${0.18 * k})` }); }
    W.mist(g, WD, t, { y: 840, h: 70, alpha: 0.45, color: 'rgba(140,180,200,.5)', seed: 8, speed: 26 });
  });
  // 首帧文字（第 0 帧就完整）
  const yr = box(p, 'ws-num', 130, 190, '1328', { fontSize: '150px' });
  const yl = box(p, 'ws-label', 140, 400, '濠州钟离 · 一户佃农', { fontSize: '48px' });
  const name = box(p, 'ws-title', 960, 260, '重八', { fontSize: '230px', w: 720, textAlign: 'center', color: '#f2b84b' });
  tl.fromTo(name, { scale: 1 }, { scale: 1.08, duration: 0.25, yoyo: true, repeat: 1, ease: 'sine.inOut', immediateRender: false }, T(2, '重八'));
  sfx('impact', T(2, '重八'), { gain: 0.6 });
  // 四十年后 → 龙椅
  fx.to(name, T(3, '四十') - 0.25, { opacity: 1, y: 0 }, { opacity: 0, y: -40 }, 0.3);
  const th = sil(p, 1240, 420, 360, 400, M.goldDefs + M.throne(), 0.95, 'rim-fire', false, '#b88a2e');
  fx.in(th, throneAt, { opacity: 0, y: 60, scale: 0.9 }, { opacity: 1, y: 0, scale: 1 }, 0.9, 'expo.out');
  F.kw('40年', T(3, '四十'), kwo({ x: 960, w: 720, y: 240, size: 200, until: T(4) - 0.25 }));
  sfx('riser', throneAt - 0.4, { gain: 0.45, dur: 1.2 });
  // 问号
  const q = box(p, 'ws-title', 1580, 250, '？', { fontSize: '200px', color: '#e5482b', letterSpacing: '0' });
  fx.to(th, T(4) - 0.1, { opacity: 1 }, { opacity: 0.45 }, 0.5);
  fx.to(name, T(4) - 0.1, { opacity: 0, y: -40 }, { opacity: 1, y: 0 }, 0.5);
  pop(q, T(4, '怎么') - 0.1);
  sfx('pop', T(4, '怎么'), { gain: 0.5 });
  F.scene('open', 0);
}

// ===================== B 红光满室：邻居跑来救火 =====================
F.topic(T(5) - 0.05, '红光满室');
{
  const t0 = T(5) - 0.05, t1 = T(11) + 1.0;
  const p = F.shot('birth', 1, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const sv = W.svgLayer(p), fg = W.canvas(p, WD, HT);
  const GY = 880;
  const nb = [0, 1].map(() => Rig.human(sv, { look: Rig.LOOK.civilian, ground: 60 }));
  const glowOn = T(6, '红光'), runAt = T(7, '跑来') - 1.4, stopAt = T(8, '门口'), glowOff = T(8, '没有') - 0.1;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const gl = W.smooth(W.clamp((t - glowOn + 0.3) / 0.7, 0, 1)) * (1 - W.smooth(W.clamp((t - glowOff) / 0.6, 0, 1)));
    g.clearRect(0, 0, WD, HT);
    nightBase(g, t, 200);
    ground(g, GY);
    hut(g, 1260, GY + 2, 1.5, gl, 1 - gl, t);
    if (gl > 0.05) W.embers(g, t, { n: Math.round(60 * gl), x0: 1050, x1: 1470, y: 560, speed: 90, seed: 9, alpha: gl });
    // 邻居：从左边跑来，到门口停下
    const k = W.clamp((t - runAt) / Math.max(0.5, stopAt - runAt), 0, 1);
    nb.forEach((r, i) => {
      const x = W.lerp(-120 - i * 170, 880 - i * 170, W.smooth(k));
      const pp = k < 1 ? Rig.walk(t, { period: 0.42, phase: i * 0.2 }) : Rig.stand(t + i);
      const s = 1.12 - i * 0.06;
      r.set({ x, y: GY - 172 * s + pp.bob, groundY: GY, s, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, gl > 0.3 ? W.LIGHT.fire : W.LIGHT.moon);
    });
    fg.clearRect(0, 0, WD, HT);
    W.grass(fg, WD, HT, t * 30, { y: 1000, h: 90, seed: 3, color: '#04060a' });
  });
  const src = box(p, 'ws-label', 140, 200, '《明史·太祖本纪》', { fontSize: '40px', color: '#d9c7a4' });
  const qt = box(p, 'ws-title', 130, 260, '及产，红光满室', { fontSize: '96px', color: '#ffb08a' });
  fx.fade(src, T(6) - 0.1, 0.4); fx.rise(qt, glowOn - 0.1, 20, 0.5);
  W.flash(tl, glowOn, 'rgba(255,80,30,1)', 0.35, 0.6);
  sfx('subdrop', glowOn, { gain: 0.5, dur: 1.0 });
  fx.to([src, qt], T(7) - 0.2, { opacity: 1 }, { opacity: 0 }, 0.3);
  const nl = box(p, 'ws-tag', 140, 220, '邻居以为失火，跑来救', { fontSize: '52px' });
  pop(nl, T(7, '邻居') - 0.1); out(nl, T(8) + 0.4);
  sfx('whoosh', runAt + 0.3, { gain: 0.4, dur: 0.9 });
  sfx('thud', stopAt, { gain: 0.45 });
  // 一个孩子 + 一张嘴
  const kid = box(p, 'ws-title', 140, 230, '屋里，多了一个孩子', { fontSize: '76px' });
  fx.rise(kid, T(9) - 0.05, 18, 0.5); out(kid, T(10) - 0.15, 0.25);
  const bowl = sil(p, 820, 250, 160, 110, M.bowl({ rice: false }), 1.6, 'rim-fire', false, '#1a120c');
  fx.pop(bowl, T(10, '嘴') - 0.3, 0.5); sfx('ding', T(10, '嘴'), { gain: 0.4 });
  F.kw('一张嘴', T(10, '嘴'), kwo({ x: 140, w: 640, y: 260, size: 170, color: '#f2efe6', until: T(11) - 0.2 }));
  out(bowl, T(11) - 0.2);
  F.scene('birth', T(5));
}

// ===================== C 佃农朱五四（白天田地）=====================
F.topic(T(11) - 0.1, '第四个儿子');
{
  const t0 = T(11) - 0.2, t1 = T(12) + 0.2;
  const p = F.shot('field', 2, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.6 });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const GY = 860;
  const dad = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 64 });
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#6d8aa0', '#c9c2a2', '#e8d7a8', 0.55);
    W.orb(g, 1500, 240, 70, '#fff6dc', 'rgba(255,230,170,.4)', 380);
    W.range(g, WD, HT, { f: fC, y: 600, amp: 200, shift: t * 10, top: '#6f7f78', bot: '#9aa38a' });
    W.mist(g, WD, t, { y: 640, h: 80, alpha: 0.35, color: 'rgba(255,250,235,.55)', seed: 14, speed: 12 });
    ground(g, 700, '#4a3a22');
    g.strokeStyle = 'rgba(30,20,10,.45)'; g.lineWidth = 4;
    for (let i = 0; i < 9; i++) { const y = 720 + i * i * 4.5; g.beginPath(); g.moveTo(0, y); g.lineTo(WD, y + 6); g.stroke(); }
    const k = 0.45 + 0.4 * (0.5 + 0.5 * Math.sin(t * 2.6));
    const pp = Rig.bow(t, k);
    dad.set({ x: 640 + t * 6 - T(11) * 6, y: GY - 172 * 1.3 + pp.bob, groundY: GY, s: 1.3, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, W.LIGHT.day);
  });
  const nm = box(p, 'ws-tag', 980, 220, '朱五四 · 佃农', { fontSize: '62px' });
  pop(nm, T(11, '五四') - 0.15);
  const ex = box(p, 'ws-label', 990, 340, '佃农：租地主的地来种', { fontSize: '50px' });
  fx.rise(ex, T(11, '没有地') - 0.1, 14, 0.4);
  const n4 = box(p, 'ws-num', 1000, 450, '第四子', { fontSize: '120px' });
  fx.rise(n4, T(11, '第四') - 0.1, 20, 0.4);
  const s4 = box(p, 'ws-label', 1010, 600, '“生四子，太祖其季也”——《明史》', { fontSize: '36px', color: '#fff3df' });
  fx.fade(s4, T(11, '第四') + 0.3, 0.4);
  F.scene('field', T(11));
}

// ===================== D 祠堂：四代数字名 → 流传说法 → 站队题 =====================
F.topic(T(12) - 0.05, '四代人都是数');
{
  const t0 = T(12) - 0.05, t1 = T(21) + 0.2;
  const p = F.shot('names', 3, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const candles = [[200, 840], [1720, 840], [560, 860], [1360, 860]];
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    const bg = g.createLinearGradient(0, 0, 0, HT); bg.addColorStop(0, '#0d0807'); bg.addColorStop(0.6, '#24130c'); bg.addColorStop(1, '#0a0605'); g.fillStyle = bg; g.fillRect(0, 0, WD, HT);
    const glow = g.createRadialGradient(960, 620, 0, 960, 620, 900); glow.addColorStop(0, 'rgba(255,140,50,.22)'); glow.addColorStop(1, 'rgba(255,140,50,0)'); g.fillStyle = glow; g.fillRect(0, 0, WD, HT);
    g.fillStyle = '#140a06'; g.fillRect(0, 820, WD, 260);
    g.strokeStyle = 'rgba(255,190,110,.4)'; g.lineWidth = 3; g.beginPath(); g.moveTo(0, 820); g.lineTo(WD, 820); g.stroke();
    candles.forEach(([x, y], i) => { g.fillStyle = '#d8cdb0'; g.fillRect(x - 9, y - 70, 18, 70); W.flame(g, x, y - 72, 0.45, t, 40 + i); });
    W.smoke(g, 960, 300, t, { seed: 17, n: 8, alpha: 0.18, scale: 1.2, color: 'rgba(200,170,140,.4)', rise: 260, drift: 60 });
    W.embers(g, t, { n: 24, x0: 150, x1: 1770, y: 820, speed: 40, seed: 19, alpha: 0.5 });
  });
  // 四块牌位
  const names = [['高祖', '百六', T(13, '百六')], ['曾祖', '四九', T(13, '四九')], ['祖父', '初一', T(14, '初一')], ['父亲', '五四', T(14, '五四')]];
  const tabs = names.map(([a, b, at], i) => { const e = tablet(p, 520 + i * 230, 260, a, b); fx.in(e, at - 0.25, { opacity: 0, y: 80 }, { opacity: 1, y: 0 }, 0.5, MR.spring(0.16)); sfx('thud', at - 0.05, { gain: 0.45 }); return e; });
  const lab = box(p, 'ws-label', 0, 190, '朱家四代 · 据朱元璋撰碑文', { w: WD, textAlign: 'center', fontSize: '40px', color: '#d9c7a4' });
  fx.fade(lab, T(12, '名字') - 0.1, 0.4);
  F.kw('四代', T(14, '五四', 1, 'end') + 0.1, kwo({ x: 1440, w: 420, y: 580, size: 150, color: '#e5482b', rot: -6, until: T(15) + 0.3 }));
  // 名字是个数，人也就是个数：牌位暗下去
  tabs.forEach((e, i) => dim(e, T(15, '人也') + i * 0.08, 0.35, 0.8));
  sfx('subdrop', T(15, '人也'), { gain: 0.35, dur: 1.2 });
  // 流传说法 → 查无此条
  fx.to([...tabs, lab], T(16) - 0.25, { opacity: 0.35 }, { opacity: 0 }, 0.3);
  const scroll = box(p, '', 360, 230, `<div class="ws-label" style="font-size:42px;color:#d9c7a4;margin-bottom:24px">流传说法</div><div class="ws-title" style="font-size:72px;letter-spacing:6px">元朝不许百姓取名</div><div class="ws-num" style="font-size:96px;margin-top:30px">28 ＋ 26 ＝ 54</div><div class="ws-label" style="font-size:36px;color:#d9c7a4;margin-top:8px">（举例：爹娘岁数相加）</div>`,
    { w: 1200, h: 470, background: 'rgba(10,8,8,.78)', border: '3px solid #8a6524', borderRadius: '12px', textAlign: 'center', paddingTop: '34px', boxSizing: 'border-box' });
  fx.in(scroll, T(16) - 0.15, { opacity: 0, clipPath: 'inset(0 50% 0 50%)' }, { opacity: 1, clipPath: 'inset(0 0% 0 0%)' }, 0.55, 'power3.out');
  sfx('paper', T(16) - 0.1, { gain: 0.5 });
  const seal = M.seal(p, '查无此条', { x: 1290, y: 520, size: 210, zhu: true, rot: -10 });
  fx.stamp(seal, T(17, '查不到'), 0.8);
  // 常遇春家、汤和家
  fx.to([scroll, seal], T(18) - 0.25, { opacity: 1 }, { opacity: 0 }, 0.3);
  const fam = (x, who, list, at) => {
    const h = box(p, 'ws-tag', x, 220, who, { fontSize: '54px' }); pop(h, at - 0.15);
    list.forEach((n, i) => { const e = box(p, 'ws-num', x + 10, 340 + i * 130, n, { fontSize: '96px' }); fx.rise(e, at + 0.15 + i * 0.12, 18, 0.35); fx.to(e, T(19) - 0.25, { opacity: 1 }, { opacity: 0 }, 0.3); });
    fx.to(h, T(19) - 0.25, { opacity: 1 }, { opacity: 0 }, 0.3);
  };
  fam(420, '常遇春家', ['常四三', '常重五', '常六六'], T(18, '常遇春'));
  fam(1080, '汤和家', ['汤五一', '汤六一', '汤七一'], T(18, '汤和'));
  sfx('tick', T(18, '常遇春'), { gain: 0.4 }); sfx('tick', T(18, '汤和'), { gain: 0.4 });
  // 站队题：三个选项
  const opts = [['①', '爹娘岁数', T(19, '爹娘')], ['②', '出生日子', T(19, '出生')], ['③', '族里排行', T(19, '排行')]];
  opts.forEach(([i, txt, at], k) => { const c = card(p, 170 + k * 540, 470, 500, i, txt); fx.in(c, at - 0.15, { opacity: 0, y: 40 }, { opacity: 1, y: 0 }, 0.4, 'expo.out'); sfx('pop', at, { gain: 0.4 }); });
  const qq = box(p, 'ws-title', 0, 240, '“重八”是哪一种？', { w: WD, textAlign: 'center', fontSize: '100px', color: '#f2b84b' });
  fx.rise(qq, T(20) - 0.1, 20, 0.45);
  sfx('ding', T(20, '哪一种'), { gain: 0.45 });
  F.scene('names', T(12));
}
F.topic(T(19) - 0.1, '重八，是哪一种？');

// ===================== E 放牛：刘德家 · 读不起书 · 一辈子的打算 =====================
F.topic(T(21) - 0.05, '给刘家放牛');
{
  const t0 = T(21) - 0.05, t1 = T(27) + 1.0;
  const p = F.shot('ox', 4, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT);
  const GY = 860;
  const misty = T(23) - 0.2;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const m = W.smooth(W.clamp((t - misty) / 1.2, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#2a2448', '#b4573a', '#f3b25a', 0.62);
    W.orb(g, 1560, 560, 100, '#ffe2a0', 'rgba(255,170,90,.45)', 520);
    W.range(g, WD, HT, { f: fD, y: 640, amp: 220, shift: t * 16, top: '#6b3b45', bot: '#c06e4a' });
    W.mist(g, WD, t, { y: 660, h: 90, alpha: 0.4, color: 'rgba(255,210,170,.5)', seed: 23, speed: 14 });
    W.range(g, WD, HT, { f: fE, y: 790, amp: 120, shift: t * 34, top: '#3b1d24', bot: '#5a2c2c', scale: 0.005 });
    ground(g, GY, '#1a0d0c');
    if (m > 0) { g.fillStyle = `rgba(250,225,200,${0.4 * m})`; g.fillRect(0, 0, WD, HT); W.mist(g, WD, t, { y: 520, h: 260, alpha: 0.55 * m, color: 'rgba(255,240,225,.7)', seed: 29, speed: 20 }); }
  });
  // 骑牛的少年（远景剪影，便宜）
  const ox = sil(p, 0, GY - 230 * 1.25 + 8, 400, 230, M.buffalo({ rider: M.person({ pose: 'ride', child: true, hat: 'none' }) }), 1.25, 'rim-dawn', false, '#0b0607');
  tl.fromTo(ox, { x: 80 }, { x: 560, duration: t1 - t0, ease: 'none', immediateRender: false }, t0);
  tl.fromTo(ox, { y: 0 }, { y: -6, duration: 0.6, yoyo: true, repeat: Math.ceil((t1 - t0) / 1.2), ease: 'sine.inOut', immediateRender: false }, t0);
  const tg = box(p, 'ws-tag', 1100, 210, '地主 · 刘德', { fontSize: '62px' });
  pop(tg, T(21, '刘德') - 0.15);
  const dl = box(p, 'ws-label', 1110, 330, '“田主德”——《御制皇陵碑》', { fontSize: '38px', color: '#fff3df' });
  fx.fade(dl, T(21, '放牛'), 0.4);
  fx.to([tg, dl], T(22) - 0.2, { opacity: 1 }, { opacity: 0 }, 0.3);
  // 私塾窗
  const school = box(p, '', 1180, 260, `<div class="ws-label" style="font-size:44px;color:#ffe0a0">私塾</div><div style="margin-top:16px;height:200px;background:repeating-linear-gradient(90deg,#120806 0 10px,rgba(255,220,150,.75) 10px 46px);border:6px solid #120806"></div>`, { w: 360, textAlign: 'center' });
  fx.fade(school, T(22) - 0.1, 0.4);
  F.kw('学费', T(22, '学费'), kwo({ x: 1100, w: 560, y: 560, size: 150, color: '#e5482b', until: T(23) - 0.1 }));
  out(school, T(23) - 0.2);
  // 雾中的一辈子
  const wife = sil(p, 1150, 460, 100, 200, M.person({ pose: 'stand', female: true, hat: 'none' }), 2.0, null, false, '#3a2c28');
  const kids = [0, 1, 2].map((i) => sil(p, 1380 + i * 130, 580, 100, 200, M.person({ pose: 'stand', child: true, hat: 'none' }), 1.4, null, i === 1, '#3a2c28'));
  fx.fade(wife, T(24, '媳妇') - 0.2, 0.5);
  kids.forEach((e, i) => fx.fade(e, T(24, '孩子') - 0.1 + i * 0.12, 0.4));
  fx.to([wife, ...kids], T(26) - 0.2, { opacity: 1 }, { opacity: 0 }, 0.35);
  const ln = box(p, 'ws-label', 1100, 230, '一辈子，大约就是这样', { fontSize: '52px' });
  fx.fade(ln, T(24) - 0.1, 0.5); out(ln, T(26) - 0.2);
  // 刘德 · 门合上（留人钩子）

  const dL = box(p, '', 960 - 300, 170, '', { w: 300, h: 690, background: 'linear-gradient(90deg,#2a160e,#170b07)', border: '4px solid #0a0503', boxSizing: 'border-box' });
  const dR = box(p, '', 960, 170, '', { w: 300, h: 690, background: 'linear-gradient(270deg,#2a160e,#170b07)', border: '4px solid #0a0503', boxSizing: 'border-box' });
  const shut = T(26, '再去') - 0.2;
  fx.in(dL, shut, { x: -330, opacity: 0 }, { x: 0, opacity: 1 }, 0.6, 'power3.in');
  fx.in(dR, shut, { x: 330, opacity: 0 }, { x: 0, opacity: 1 }, 0.6, 'power3.in');
  sfx('thud', shut + 0.6, { gain: 0.7 }); W.shake(tl, shut + 0.6, 0.3, 8);
  const ld = box(p, 'ws-title', 0, 420, '刘德', { w: WD, textAlign: 'center', fontSize: '180px', color: '#f2b84b' });
  out(ox, shut + 0.3, 0.3);
  fx.rise(ld, T(26) - 0.05, 20, 0.5);
  F.scene('ox', T(21));
}

// ===================== F 元廷：五年五个新皇帝 =====================
F.topic(T(27) - 0.1, '五年五个新皇帝');
{
  const t0 = T(27) - 0.2, t1 = T(32) + 0.3;
  const p = F.shot('court', 5, 0, t0, t1, { dur: 0.8 });
  sfx('whoosh', t0 + 0.1, { gain: 0.45, dur: 0.6 });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#05060c', '#1a1830', '#3a2a3a', 0.65);
    W.stars(g, WD, HT, t, 11, 80, 0.6);
    W.range(g, WD, HT, { f: fG, y: 700, amp: 140, shift: t * 10, top: '#141626', bot: '#262438' });
    W.mist(g, WD, t, { y: 760, h: 70, alpha: 0.3, color: 'rgba(170,170,210,.45)', seed: 31, speed: 18 });
    ground(g, 860, '#07070c');
    W.rays(g, 960, 520, t, { n: 14, len: 800, color: 'rgba(242,184,75,.12)', spin: 0.03 });
  });
  const pal = sil(p, 700, 230, 520, 320, M.palace(), 1.0, 'rim-moon', false, '#0b0c14');
  pal.style.opacity = 0.75;
  const th = sil(p, 820, 470, 360, 400, M.goldDefs + M.throne(), 0.75, 'rim-fire', false, '#b88a2e');
  const lb = box(p, 'ws-label', 140, 200, '大都 · 元廷', { fontSize: '48px', color: '#d9c7a4' });
  fx.fade(lb, T(27) + 0.1, 0.4);
  // 五个新皇帝依次坐上又消失
  const emp = [];
  const names = ['天顺帝', '文宗', '明宗', '宁宗', '顺帝'];
  const ats = [T(28, '五个') - 0.2, T(28, '五个') + 0.05, T(28, '五个') + 0.3, T(28, '新皇帝'), T(28, '皇帝') + 0.25];
  names.forEach((n, i) => {
    const x = 210 + i * 320;
    const e = sil(p, x, 520, 120, 200, M.emperor(), 1.15, 'rim-fire', false, '#120d0c');
    const tg = box(p, 'ws-label', x - 30, 770, n, { w: 200, textAlign: 'center', fontSize: '40px', color: '#f2b84b' });
    fx.in(e, ats[i], { opacity: 0, y: 30 }, { opacity: 1, y: 0 }, 0.3, 'expo.out');
    fx.fade(tg, ats[i] + 0.1, 0.3);
    sfx('tick', ats[i], { gain: 0.4 });
    emp.push([e, tg]);
  });
  fx.to(th, T(28) - 0.2, { opacity: 1 }, { opacity: 0.35 }, 0.4);
  F.kw('5年 · 5帝', T(28, '五年'), kwo({ x: 460, w: 1000, y: 210, size: 140, until: T(29) - 0.1 }));
  const yrs = box(p, 'ws-label', 1480, 200, '1328—1333', { fontSize: '48px', color: '#fff3df' });
  fx.fade(yrs, T(28, '五年'), 0.4);
  // 一个九岁登基，一个多月被赶下台
  const fall = (k, at, rot) => { const [e, tg] = emp[k]; fx.to(e, at, { y: 0, rotation: 0, opacity: 1 }, { y: 160, rotation: rot, opacity: 0 }, 0.6, 'power2.in'); fx.to(tg, at, { opacity: 1 }, { opacity: 0.25 }, 0.4); sfx('whip', at, { gain: 0.45 }); };
  const n1 = box(p, 'ws-tag', 140, 300, '九岁（虚岁）登基 · 一月余被废', { fontSize: '46px' });
  pop(n1, T(29, '九岁') - 0.15); fall(0, T(29, '赶下'), -24); out(n1, T(30) - 0.1);
  const n2 = box(p, 'ws-tag', 140, 300, '与弟相见数日 · 暴卒', { fontSize: '46px' });
  pop(n2, T(30) - 0.05); fall(2, T(30, '死了') - 0.1, 18);
  sfx('subdrop', T(30, '死了'), { gain: 0.4, dur: 1.0 });
  const n3 = box(p, 'ws-label', 140, 390, '史家多疑为毒杀（《元史·明宗纪》）', { fontSize: '34px', color: '#d9c7a4' });
  fx.fade(n3, T(30, '死了') + 0.3, 0.4);
  fx.to([n2, n3], T(31) - 0.15, { opacity: 1 }, { opacity: 0 }, 0.3);
  F.scene('court', T(27));
}

// ===================== G 官吏收钱的名目（叶子奇《草木子》）=====================
F.topic(T(31) + 0.3, '官吏收钱的名目');
{
  const t0 = T(31, '下面') - 0.2, t1 = T(39) + 0.2;
  const p = F.shot('fees', 6, 0, t0, t1, { dur: 0.7 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.5 });
  const g = W.canvas(p, WD, HT);
  const flyAt = T(38, '勤快') - 0.3;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#0a0608', '#2a1416', '#4a2a22', 0.6);
    W.range(g, WD, HT, { f: fA, y: 600, amp: 150, shift: t * 10, top: '#1e1418', bot: '#3a2420' });
    ground(g, 820, '#0b0606');
    // 衙门大门（剪影）+ 两盏灯
    g.fillStyle = '#070405'; g.fillRect(560, 360, 800, 470);
    g.beginPath(); g.moveTo(480, 380); g.lineTo(960, 250); g.lineTo(1440, 380); g.closePath(); g.fill();
    g.strokeStyle = 'rgba(255,150,80,.55)'; g.lineWidth = 3; g.beginPath(); g.moveTo(480, 380); g.lineTo(960, 250); g.lineTo(1440, 380); g.stroke();
    [[620, 470], [1300, 470]].forEach(([x, y], i) => { g.fillStyle = `rgba(230,72,43,${0.85 + 0.1 * Math.sin(t * 5 + i)})`; g.beginPath(); g.ellipse(x, y, 34, 44, 0, 0, 6.28); g.fill(); const r = g.createRadialGradient(x, y, 0, x, y, 200); r.addColorStop(0, 'rgba(255,90,40,.3)'); r.addColorStop(1, 'rgba(255,90,40,0)'); g.fillStyle = r; g.fillRect(x - 200, y - 200, 400, 400); });
    W.mist(g, WD, t, { y: 800, h: 70, alpha: 0.35, color: 'rgba(200,150,140,.4)', seed: 37, speed: 18 });
    W.embers(g, t, { n: 30, x0: 500, x1: 1420, y: 820, speed: 50, seed: 41, alpha: 0.6 });
  });
  const hand = box(p, 'ws-title', 0, 240, '下面 · 收钱', { w: WD, textAlign: 'center', fontSize: '96px' });
  fx.rise(hand, T(31, '下面') + 0.1, 18, 0.4); out(hand, T(32) - 0.15);
  const src = box(p, 'ws-tag', 0, 200, '叶子奇《草木子》', { w: WD, textAlign: 'center', fontSize: '54px' });
  src.style.background = 'none'; src.style.color = '#f2b84b';
  fx.fade(src, T(32, '叶子奇') - 0.1, 0.4);
  // 签条
  const fees = [['拜见钱', '新官上任', T(33, '拜见')], ['追节钱', '逢年过节', T(34, '追节')], ['生日钱', '过生日', T(35, '生日钱')], ['公事钱', '打官司', T(36, '公事')], ['撒花钱', '无事白要', T(37, '撒花')]];
  const slips = fees.map(([n, why, at], i) => {
    const big = i === 4;
    const x = 130 + i * 310, y = big ? 300 : 330;
    const e = box(p, '', x, y, `<div class="ws-title" style="font-size:${big ? 84 : 66}px;writing-mode:vertical-rl;letter-spacing:10px;margin:0 auto">${n}</div><div class="ws-label" style="font-size:30px;color:#ffe0a0;margin-top:16px">${why}</div>`,
      { w: big ? 220 : 190, h: big ? 470 : 420, background: 'linear-gradient(180deg,#b52a17,#7e1a0e)', border: '3px solid #f2b84b', borderRadius: '6px', textAlign: 'center', paddingTop: '22px', boxSizing: 'border-box', boxShadow: '0 10px 30px rgba(0,0,0,.5)' });
    fx.in(e, at - 0.25, { opacity: 0, y: -120, rotation: (i % 2 ? 6 : -6) }, { opacity: 1, y: 0, rotation: (i % 2 ? 2 : -2) }, 0.4, MR.spring(0.14));
    sfx('paper', at - 0.1, { gain: 0.45 });
    return e;
  });
  fx.to(src, T(33) - 0.3, { opacity: 1 }, { opacity: 0 }, 0.3);
  const seal = M.seal(p, '无事白要', { x: 1620, y: 560, size: 170, zhu: true, rot: -12 });
  fx.stamp(seal, T(37, '撒花') + 0.35, 0.8);
    // 冷话：签条随风飘起
  slips.forEach((e, i) => fx.to(e, flyAt + i * 0.07, { y: 0, x: 0, opacity: 1 }, { y: -700, x: 160 + i * 40, rotation: 30 + i * 8, opacity: 0 }, 1.4, 'power2.in'));
  out(seal, flyAt + 0.2, 0.6);
  sfx('whoosh', flyAt + 0.2, { gain: 0.4, dur: 1.2 });
  F.scene('fees', T(31));
}

// ===================== H 伯颜请杀五姓 =====================
F.topic(T(39) - 0.05, '1337，伯颜上奏');
{
  const t0 = T(39) - 0.05, t1 = T(42) + 0.2;
  const p = F.shot('five', 7, 0, t0, t1, { enter: 'cut' });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.3, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#120405', '#3a0c0a', '#5a1a12', 0.6);
    W.smoke(g, 960, 900, t, { seed: 51, n: 12, alpha: 0.4, scale: 2.4, color: 'rgba(20,6,6,.6)', rise: 700, drift: 80 });
    ground(g, 860, '#080203');
    W.embers(g, t, { n: 50, x0: 100, x1: 1820, y: 880, speed: 70, seed: 53, alpha: 0.6 });
  });
  const yr = box(p, 'ws-label', 140, 200, '1337年 · 权臣伯颜 · 《元史·顺帝纪》', { fontSize: '44px', color: '#d9c7a4' });
  fx.fade(yr, t0 + 0.1, 0.3);
  const xs = ['张', '王', '刘', '李', '赵'];
  const ch = xs.map((c, i) => { const e = box(p, 'ws-title', 300 + i * 270, 360, c, { fontSize: '210px', letterSpacing: '0' }); fx.in(e, T(39, c) - 0.1, { opacity: 0, scale: 1.4 }, { opacity: 1, scale: 1 }, 0.25, 'power4.in'); sfx('hit', T(39, c), { gain: 0.35 }); return e; });
  const xx = F.svg(p, 260, 300, 1400, 380, M.cross(1400, 380), `0 0 1400 380`);
  fx.draw(xx.querySelectorAll('path'), T(39, '杀掉') - 0.1, 0.35);
  sfx('slide', T(39, '杀掉'), { gain: 0.5 }); W.shake(tl, T(39, '杀掉') + 0.2, 0.3, 10);
  // 皇帝没有答应：叉淡去
  out(xx, T(40, '没有'), 0.6);
  const no = box(p, 'ws-tag', 0, 690, '帝不从', { w: WD, textAlign: 'center', fontSize: '60px' });
  no.style.background = 'none'; fx.fade(no, T(40, '没有'), 0.4);
  // 朱家不在这五个姓里
  ch.forEach((e) => dim(e, T(41) - 0.1, 0.3, 0.5)); out(no, T(41) - 0.1);
  const zhu = box(p, 'ws-title', 1590, 470, '朱', { fontSize: '150px', color: '#f2b84b', letterSpacing: '0' });
  fx.in(zhu, T(41, '朱家') - 0.1, { opacity: 0, x: 60 }, { opacity: 1, x: 0 }, 0.5, 'expo.out');
  sfx('ding', T(41, '不在'), { gain: 0.35 });
  F.scene('five', T(39));
}

// ===================== I 1344：旱、蝗、饥、疫、黄河决口；十七岁 =====================
F.topic(T(42) - 0.05, '1344，淮河两岸');
{
  const t0 = T(42) - 0.05, t1 = T(48) + 1.0;
  const p = F.shot('disaster', 8, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const tLoc = T(44, '蝗虫') - 0.3, tFam = T(45) - 0.1, tFlood = T(46, '决') - 0.4, tBoy = T(47) - 0.2;
  const boy = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 56 });
  const cracks = []; { const r = MR.random(77); for (let i = 0; i < 60; i++) { const x = r() * WD, y = 800 + r() * 260; cracks.push([x, y, x + (r() - 0.5) * 160, y + (r() - 0.3) * 40]); } }
  const loc = []; { const r = MR.random(79); for (let i = 0; i < 420; i++) loc.push([r() * 2400, 200 + r() * 600, 0.6 + r() * 1.2, r() * 6.28]); }
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const fl = W.smooth(W.clamp((t - tFlood) / 1.4, 0, 1));
    const by = W.smooth(W.clamp((t - tBoy) / 0.8, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, W.mix('#8a5a1e', '#1a2430', fl), W.mix('#d89a3a', '#3a4a52', fl), W.mix('#f2cf7a', '#6a7a78', fl), 0.6);
    W.orb(g, 1450, 280, 110, W.mix('#fff4c0', '#cfd6d0', fl), `rgba(255,200,90,${0.5 * (1 - fl)})`, 600, 1 - 0.7 * fl);
    W.range(g, WD, HT, { f: fB, y: 640, amp: 180, shift: t * 10, top: W.mix('#8a5a2a', '#2a3a44', fl), bot: W.mix('#b07a3a', '#3a4c52', fl) });
    ground(g, 780, W.mix('#5a3a1a', '#1a2226', fl));
    g.strokeStyle = 'rgba(30,15,5,.75)'; g.lineWidth = 3;
    cracks.forEach(([a, b, c, d]) => { g.beginPath(); g.moveTo(a, b); g.lineTo(c, d); g.stroke(); });
    // 村子（屋顶）与炊烟：饥疫后炊烟断
    for (let i = 0; i < 6; i++) { const x = 220 + i * 280; g.fillStyle = '#1a1008'; g.beginPath(); g.moveTo(x - 90, 790); g.lineTo(x, 720); g.lineTo(x + 90, 790); g.closePath(); g.fill(); g.fillRect(x - 70, 780, 140, 40);
      if (t < tFam) W.smoke(g, x + 20, 720, t, { seed: 60 + i, n: 5, alpha: 0.3, scale: 0.5, color: 'rgba(90,80,70,.5)', rise: 200 }); }
    // 蝗群
    const lk = W.clamp((t - tLoc) / 2.2, 0, 1);
    if (lk > 0 && lk < 1) { g.fillStyle = 'rgba(30,20,8,.85)'; loc.forEach(([x, y, s, ph]) => { const xx = x - lk * 2600 + Math.sin(t * 9 + ph) * 8; if (xx > -20 && xx < WD + 20) { g.beginPath(); g.ellipse(xx, y + Math.sin(t * 7 + ph) * 10, 5 * s, 2 * s, 0.2, 0, 6.28); g.fill(); } });
      W.speedLines(g, WD, HT, t, { n: 30, speed: 2800, alpha: 0.2 * (1 - lk), seed: 8, color: 'rgba(60,40,10,.6)' }); }
    // 洪水
    if (fl > 0) { const top = 1080 - fl * 360; const wg = g.createLinearGradient(0, top, 0, HT); wg.addColorStop(0, 'rgba(120,150,150,.95)'); wg.addColorStop(1, 'rgba(30,50,60,.98)'); g.fillStyle = wg; g.beginPath(); g.moveTo(0, HT); for (let x = 0; x <= WD; x += 40) g.lineTo(x, top + Math.sin(x * 0.01 + t * 4) * 14 + Math.sin(x * 0.023 - t * 6) * 8); g.lineTo(WD, HT); g.closePath(); g.fill();
      W.mist(g, WD, t, { y: top - 20, h: 60, alpha: 0.5 * fl, color: 'rgba(220,235,235,.6)', seed: 71, speed: 80 }); }
    // 十七岁：少年站在高处
    if (by > 0) { g.fillStyle = `rgba(10,14,16,${by})`; g.beginPath(); g.moveTo(1180, 740); g.quadraticCurveTo(1400, 600, 1700, 620); g.lineTo(1760, 760); g.closePath(); g.fill(); }
    const pp = Rig.stand(t);
    boy.set({ x: 1440, y: 640 - 172 * 1.0 + pp.bob, groundY: 640, s: 1.0, facing: -1, angles: pp.angles, worldAngles: pp.worldAngles }, W.LIGHT.dawn);
    sv.style.opacity = by;
  });
  const steps = [['大旱', T(43, '大旱')], ['蝗', T(44, '蝗虫')], ['饥荒', T(45, '饥荒')], ['瘟疫', T(45, '瘟疫')]];
  const stEls = steps.map(([s, at], i) => { const e = box(p, 'ws-tag', 150 + i * 280, 210, s, { fontSize: '62px' }); pop(e, at - 0.15); sfx('hit', at, { gain: 0.4 }); return e; });
  const src = box(p, 'ws-label', 150, 330, '“旱蝗，大饥疫”——《明史·太祖本纪》', { fontSize: '38px', color: '#fff3df' });
  fx.fade(src, T(45) + 0.3, 0.4);
  fx.to([...stEls, src], tFlood - 0.1, { opacity: 1 }, { opacity: 0 }, 0.3);
  W.flash(tl, tFlood + 0.35, '#e8f4f4', 0.6, 0.5); W.shake(tl, tFlood + 0.35, 0.7, 18);
  sfx('subdrop', tFlood + 0.35, { gain: 0.8, dur: 1.6 }); sfx('whoosh', tFlood, { gain: 0.6, dur: 1.2 });
  F.kw('决口', T(46, '决') + 0.1, kwo({ x: 360, w: 1200, y: 240, size: 200, color: '#e5482b', until: T(47) - 0.2 }));
  const bm = box(p, 'ws-label', 150, 210, '五月 · 白茅堤 · 《元史·河渠志》', { fontSize: '42px', color: '#e8f4f4' });
  fx.fade(bm, T(46, '白茅') - 0.1, 0.4); out(bm, T(47) - 0.2);
  F.kw('17岁', T(47, '十七'), kwo({ x: 200, w: 800, y: 300, size: 200, color: '#f2b84b', until: T(48) - 0.1 }));
  sfx('chime', T(47, '十七'), { gain: 0.4 });
  F.scene('disaster', T(42));
}

// ===================== J 七年后：独眼石人 =====================
F.topic(T(48) - 0.1, '据载：独眼石人');
{
  const t0 = T(48) - 0.2, t1 = T(50) + 0.2;
  const p = F.shot('stone', 9, 0, t0, t1, { dur: 0.9 });
  sfx('whoosh', t0 + 0.1, { gain: 0.45, dur: 0.7 });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#05090c', '#132a2e', '#2c5d67', 0.62);
    W.orb(g, 420, 230, 54, '#e8f0e6', 'rgba(160,220,220,.3)', 260);
    W.range(g, WD, HT, { f: fC, y: 620, amp: 160, shift: t * 12, top: '#0e1e22', bot: '#1c3a40' });
    W.mist(g, WD, t, { y: 680, h: 90, alpha: 0.45, color: 'rgba(170,215,215,.5)', seed: 81, speed: 20 });
    ground(g, 820, '#1a1a14');
    g.fillStyle = '#2a2a1e'; g.beginPath(); g.ellipse(640, 840, 420, 60, 0, 0, 6.28); g.fill();
    W.mist(g, WD, t, { y: 840, h: 60, alpha: 0.4, color: 'rgba(140,180,180,.5)', seed: 83, speed: 30 });
  });
  const st = sil(p, 510, 380, 260, 420, M.stoneMan(), 1.05, 'rim-moon', false, '#5c564d');
  fx.in(st, T(48, '挖出') - 0.4, { y: 280, opacity: 0.2 }, { y: 0, opacity: 1 }, 1.2, 'power3.out');
  sfx('thud', T(48, '石人'), { gain: 0.6 }); W.shake(tl, T(48, '石人'), 0.4, 8);
  const lb = box(p, 'ws-tag', 1000, 200, '据载 · 1351年（至正十一年）', { fontSize: '46px' });
  pop(lb, T(48, '七年') - 0.1);
  const lines2 = ['石人一只眼', '挑动黄河天下反'];
  lines2.forEach((s, i) => { const e = box(p, 'ws-title', 1000, 340 + i * 160, '', { fontSize: '108px', color: i ? '#ff8a5a' : '#f2efe6', letterSpacing: '8px' }); M.write(tl, M.chars(e, s), T(49, i ? '挑动' : '石人') - 0.05, { dir: 'right', dur: 0.2, stagger: 0.07 }); sfx('draw', T(49, i ? '挑动' : '石人'), { dur: 0.6, gain: 0.35 }); });
  F.scene('stone', T(48));
}

// ===================== K 知识卡：一图看懂本集 =====================
F.topic(T(50) - 0.1, '童年的四个年份');
{
  const t0 = T(50) - 0.1, t1 = T(52) + 0.2;
  const p = F.shot('card', 10, 0, t0, t1, { enter: 'cut' });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.3, t1 + 0.6, (t) => {
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#05070c', '#0e1724', '#1c2a38', 0.6);
    W.mist(g, WD, t, { y: 760, h: 120, alpha: 0.3, color: 'rgba(170,200,220,.4)', seed: 91, speed: 10 });
    W.embers(g, t, { n: 30, x0: 0, x1: WD, y: 900, speed: 30, seed: 93, alpha: 0.4 });
  });
  const panel = box(p, '', 260, 180, '', { w: 1400, h: 680, background: 'rgba(8,10,16,.88)', border: '4px solid #b88a2e', borderRadius: '16px', boxShadow: '0 0 60px rgba(242,184,75,.2)' });
  const corner = box(p, 'ws-tag', 290, 200, '大明开局 · 第01集', { fontSize: '36px' });
  const title = box(p, 'ws-title', 260, 270, '童年的四个年份', { w: 1400, textAlign: 'center', fontSize: '84px' });
  const axis = box(p, '', 360, 530, '', { w: 1200, h: 6, background: '#b88a2e' });
  const nodes = [['1328', '生于濠州钟离', '佃农朱五四第四子'], ['1337', '伯颜请杀五姓', '帝不从'], ['1344', '旱蝗饥疫', '黄河决白茅堤'], ['1351', '独眼石人出', '“挑动黄河天下反”']];
  const els = [panel, corner, title, axis];
  nodes.forEach(([y, a, b], i) => {
    const x = 360 + i * 400;
    const dot = box(p, '', x - 18, 515, '', { w: 36, h: 36, borderRadius: '50%', background: i === 0 ? '#e5482b' : '#f2b84b', border: '4px solid #06070a' });
    const n = box(p, 'ws-num', x - 160, 410, y, { w: 320, textAlign: 'center', fontSize: '84px' });
    const l1 = box(p, 'ws-label', x - 180, 580, a, { w: 360, textAlign: 'center', fontSize: '48px' });
    const l2 = box(p, 'ws-label', x - 180, 646, b, { w: 360, textAlign: 'center', fontSize: '36px', color: '#d9c7a4' });
    const at = T(50, y.slice(2)) - 0.15;
    [dot, n, l1, l2].forEach((e, k) => fx.in(e, at + k * 0.05, { opacity: 0, y: 16 }, { opacity: 1, y: 0 }, 0.35, 'expo.out'));
    sfx('tick', at + 0.1, { gain: 0.45 });
    els.push(dot, n, l1, l2);
  });
  const src = box(p, 'ws-label', 260, 770, '据《明史·太祖本纪》《元史》· 石人事据元末记载', { w: 1400, textAlign: 'center', fontSize: '34px', color: '#a89a80' });
  els.push(src);
  // 首帧前就位的底板、标题
  [panel, corner, title, axis, src].forEach((e, k) => fx.in(e, t0 + k * 0.05, { opacity: 0, scale: 0.98 }, { opacity: 1, scale: 1 }, 0.35, 'power2.out'));
  sfx('paper', t0 + 0.05, { gain: 0.5 });
  F.scene('card', T(50));
}

// ===================== L 下一集：刘德的门 =====================
F.topic(T(52) - 0.05, '下一集 · 灾难');
{
  const t0 = T(52) - 0.05, t1 = T(56) + 1.0;
  const p = F.shot('gate', 11, 0, t0, t1, { enter: 'wipe' });
  const g = W.canvas(p, WD, HT), sv = W.svgLayer(p);
  const GY = 860;
  const boy = Rig.human(sv, { look: Rig.LOOK.civilian, ground: 60 });
  const crack = T(55) - 0.3;
  W.clock(tl, t0 - 0.6, t1 + 0.6, (t) => {
    const c = W.smooth(W.clamp((t - crack) / 1.0, 0, 1));
    g.clearRect(0, 0, WD, HT);
    W.sky(g, WD, HT, '#262a30', '#4a4e52', '#7a7a72', 0.6);
    W.mist(g, WD, t, { y: 500, h: 160, alpha: 0.35, color: 'rgba(210,210,200,.45)', seed: 97, speed: 12 });
    ground(g, GY, '#121212');
    // 刘家院墙与大门
    g.fillStyle = '#1a1612'; g.fillRect(0, 380, WD, GY - 380);
    g.fillStyle = '#0d0a08'; g.beginPath(); g.moveTo(560, 330); g.lineTo(1360, 330); g.lineTo(1420, 380); g.lineTo(500, 380); g.closePath(); g.fill();
    g.fillStyle = '#3a1c10'; g.fillRect(660, 400, 300, GY - 400); g.fillRect(960, 400, 300, GY - 400);
    g.strokeStyle = '#0a0503'; g.lineWidth = 6; g.strokeRect(660, 400, 600, GY - 400);
    g.fillStyle = '#b88a2e'; [[920, 620], [1000, 620]].forEach(([x, y]) => { g.beginPath(); g.arc(x, y, 14, 0, 6.28); g.fill(); });
    if (c > 0) { const gw = 6 + c * 22; const lg = g.createLinearGradient(960 - gw * 8, 0, 960 + gw * 8, 0); lg.addColorStop(0, 'rgba(255,220,150,0)'); lg.addColorStop(0.5, `rgba(255,220,150,${0.9 * c})`); lg.addColorStop(1, 'rgba(255,220,150,0)'); g.fillStyle = lg; g.fillRect(960 - gw * 8, 400, gw * 16, GY - 400); }
    W.mist(g, WD, t, { y: 840, h: 60, alpha: 0.35, color: 'rgba(200,200,190,.45)', seed: 99, speed: 20 });
    const pp = Rig.bow(t, 0.9);
    boy.set({ x: 960, y: GY + 120 - 172 * 1.25 + pp.bob, groundY: GY + 120, s: 1.25, facing: 1, angles: pp.angles, worldAngles: pp.worldAngles }, W.lightMix(W.LIGHT.moon, W.LIGHT.dawn, c));
  });
  const lb = box(p, 'ws-tag', 140, 200, '下一集 · 1344年 · 春', { fontSize: '50px' });
  pop(lb, T(52) + 0.1);
  const ld = box(p, 'ws-title', 1380, 420, '刘德', { fontSize: '120px', color: '#f2b84b' });
  fx.rise(ld, T(53, '刘德') - 0.1, 18, 0.4);
  const want = box(p, 'ws-label', 140, 320, '求一块埋人的地', { fontSize: '62px' });
  fx.rise(want, T(53, '一块') - 0.1, 14, 0.4);
  const no = box(p, 'ws-title', 1380, 570, '没有给', { fontSize: '84px', color: '#e5482b' });
  fx.rise(no, T(54, '没有') - 0.1, 14, 0.4); sfx('thud', T(54, '没有'), { gain: 0.5 });
  const q = box(p, 'ws-title', 140, 450, '给地的人是谁？', { fontSize: '76px', color: '#ffe0a0' });
  fx.rise(q, T(54, '给地') - 0.1, 18, 0.4);
  const src = box(p, 'ws-label', 140, 560, '据《御制皇陵碑》', { fontSize: '36px', color: '#d9c7a4' });
  fx.fade(src, T(54, '给地') + 0.4, 0.4);
  sfx('riser', crack - 0.4, { gain: 0.4, dur: 1.2 });
  fx.to([lb, ld, want, no, q, src], T(56) - 0.3, { opacity: 1 }, { opacity: 0 }, 0.3);
  F.scene('gate', T(52));
}

// ===================== M 收尾：回到茅屋 · 重八 · 一个数 =====================
F.topic(T(56) - 0.1, '一个数做的名字');
{
  const t0 = T(56) - 0.2, end = T.last() + 1.0 + V.endHold;
  const p = F.shot('end', 12, 0, t0, null, { dur: 0.9 });
  sfx('whoosh', t0 + 0.1, { gain: 0.4, dur: 0.7 });
  const g = W.canvas(p, WD, HT);
  W.clock(tl, t0 - 0.6, end + 0.1, (t) => {
    g.clearRect(0, 0, WD, HT);
    nightBase(g, t, 400);
    ground(g, 860);
    hut(g, 560, 862, 1.15, 0, 1, t);
    W.smoke(g, 560, 520, t, { seed: 3, n: 7, alpha: 0.35, scale: 0.8, color: 'rgba(120,130,150,.5)', rise: 300 });
    W.mist(g, WD, t, { y: 840, h: 70, alpha: 0.45, color: 'rgba(140,180,200,.5)', seed: 8, speed: 26 });
  });
  const name = box(p, 'ws-title', 960, 260, '重八', { fontSize: '230px', w: 720, textAlign: 'center', color: '#f2b84b' });
  fx.rise(name, T(56, '重八') - 0.2, 20, 0.5);
  sfx('impact', T(56, '重八'), { gain: 0.5 });
  const one = box(p, 'ws-label', 960, 560, '一个数', { fontSize: '72px', w: 720, textAlign: 'center' });
  fx.fade(one, T(57) - 0.05, 0.5);
  tl.fromTo(name, { letterSpacing: '14px', opacity: 1 }, { letterSpacing: '60px', opacity: 0.7, duration: 1.6, ease: 'sine.inOut', immediateRender: false }, T(57));
  const nx = box(p, 'ws-tag', 1100, 700, '下一集 · 灾难', { fontSize: '50px' });
  pop(nx, T.end(57) + 0.3);
  sfx('chime', T.end(57) + 0.3, { gain: 0.5 });
  F.scene('end', T(56));
}

F.finish();
})();
