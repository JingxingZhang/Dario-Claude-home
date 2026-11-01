// 第11集《城门关着》分镜。镜头按歌词切（L(n).start 是第 n 句开口的时间）。
// 主歌：版画画面；副歌：大字排版 + 右侧画框。每个 sh.el(...) 是一块印好的版。
const F = BH.film();
const S = F.song, L = S.line, B = S.beatPeriod, P = BH.PAL;
const pre = (n, d = 0.3) => L(n).start - d;
const at = (sh, t) => Math.max(0, t - sh.t0);                       // 绝对秒 → 镜头内秒
const charT = (n, ch, k = 0) => L(n).chars.filter((c) => c.c === ch)[k].s;
const TYPE = [110, 210, 860, 660], FRAME = [1040, 200, 780, 640], FBOX = [1000, 160, 860, 740];

// ================= 本章自画的东西（照场景库的写法：剪影 → knock → 墨版 → 刻白线 → 朱版一样 → 网点阴影）=================
const GATE_NAMES = ['抚州', '宫步', '士步', '桥步', '章江', '新城', '琉璃', '澹台'];

// 一整面城墙 + 八个门（门关着时填朱色）
function longWall(o, top, bot, opt = {}) {
  const k = o.ink, x0 = opt.x0 ?? -20, x1 = opt.x1 ?? 1940, n = opt.n ?? 8, w = (x1 - x0) / n;
  const wall = new Path2D(); wall.rect(x0, top, x1 - x0, bot - top); o.knock(wall);
  for (let x = x0; x < x1; x += 58) { k.fillRect(x, top - 30, 36, 30); o.knockRect(x, top - 30, 36, 30); }
  o.blueT.fillStyle = BH.tone(0.28); o.blueT.fill(wall);
  k.lineWidth = 6; k.strokeRect(x0, top, x1 - x0, bot - top);
  k.lineWidth = 1.6;
  for (let y = top + 30, r = 0; y < bot; y += 30, r++) {
    k.beginPath(); k.moveTo(x0, y); k.lineTo(x1, y); k.stroke();
    for (let x = x0 + (r % 2) * 45; x < x1; x += 90) { k.beginPath(); k.moveTo(x, y); k.lineTo(x, y + 30); k.stroke(); }
  }
  const dw = opt.doorW ?? 112, dh = opt.doorH ?? (bot - top) * 0.62;
  for (let i = 0; i < n; i++) {
    const cx = x0 + w * (i + 0.5), d = new Path2D(), ay = bot - dh + dw / 2;
    d.moveTo(cx - dw / 2, bot); d.lineTo(cx - dw / 2, ay); d.arc(cx, ay, dw / 2, Math.PI, 0); d.lineTo(cx + dw / 2, bot); d.closePath();
    BH.erase(k, (c) => c.fill(d)); BH.erase(o.blueT, (c) => c.fill(d));
    if (opt.open && opt.open.includes(i)) { k.fill(d); BH.erase(k, (c) => { c.fillRect(cx - dw / 2 + 10, ay, dw - 20, bot - ay); }); }
    else {
      o.red.fill(d); k.lineWidth = 5; k.stroke(d); k.lineWidth = 3; k.beginPath(); k.moveTo(cx, ay - dw / 2); k.lineTo(cx, bot); k.stroke();
      for (let r = 0; r < 4; r++) for (const sx of [-26, 26]) { k.beginPath(); k.arc(cx + sx, ay + 18 + r * ((bot - ay - 30) / 4), 4.5, 0, 7); k.fill(); }
    }
    if (opt.names) {
      const ny = ay - dw / 2 - 22, sz = opt.nameSize || 34;
      BH.erase(k, (c) => c.fillRect(cx - sz * 1.2, ny - sz * 0.95, sz * 2.4, sz * 1.25)); BH.erase(o.blueT, (c) => c.fillRect(cx - sz * 1.2, ny - sz * 0.95, sz * 2.4, sz * 1.25));
      k.lineWidth = 2.5; k.strokeRect(cx - sz * 1.2, ny - sz * 0.95, sz * 2.4, sz * 1.25);
      BH.text(k, opt.names[i], cx, ny, { size: sz });
    }
  }
}

// 单个门洞（近景）：rect 墙，门心 cx，门宽 dw，门顶 top；state: 'closed' | 'open'
function bigGate(o, rect, cx, dw, state = 'closed', opt = {}) {
  const [x0, y0, w, h] = rect, bot = y0 + h, k = o.ink;
  const d = BH.archWall(o, rect, [cx, opt.archY ?? y0 + h * 0.42, dw], opt.seed || 33);
  if (state === 'closed') {
    const half = new Path2D(); half.addPath(d); o.knock(half); BH.erase(o.blue, (c) => c.fill(half)); BH.erase(o.blueT, (c) => c.fill(half)); o.red.fill(half); k.lineWidth = 7; k.stroke(half);
    k.lineWidth = 5; k.beginPath(); k.moveTo(cx, (opt.archY ?? y0 + h * 0.42) - dw / 2); k.lineTo(cx, bot); k.stroke();
    for (let r = 0; r < 6; r++) for (const sx of [-dw * 0.3, -dw * 0.15, dw * 0.15, dw * 0.3]) { k.beginPath(); k.arc(cx + sx, (opt.archY ?? y0 + h * 0.42) + r * (h * 0.09) - dw * 0.15, 6, 0, 7); k.fill(); }
    k.fillRect(cx - dw * 0.42, bot - h * 0.36, dw * 0.84, 16);                         // 门闩
  }
  return d;
}

// 竹盾（像簸箕）：一排举盾的人
function shields(o, x0, x1, y, s = 1, seed = 3) {
  BH.crowd(o, x0, x1, y - 20 * s, s * 1.1, seed);
  const r = BH.rng(seed + 7), k = o.ink;
  for (let x = x0 + 20; x < x1; x += (62 + r() * 18) * s) {
    const cx = x, cy = y - 70 * s - r() * 10 * s, rw = 46 * s, rh = 58 * s, p = new Path2D();
    p.moveTo(cx - rw, cy - rh * 0.2); p.quadraticCurveTo(cx - rw * 1.05, cy + rh, cx, cy + rh * 1.05); p.quadraticCurveTo(cx + rw * 1.05, cy + rh, cx + rw, cy - rh * 0.2); p.quadraticCurveTo(cx, cy - rh * 0.45, cx - rw, cy - rh * 0.2); p.closePath();
    o.knock(p); o.inkT.fillStyle = BH.tone(0.35); o.inkT.fill(p); k.lineWidth = 4; k.stroke(p);
    k.save(); k.clip(p); k.lineWidth = 2; for (let i = -6; i <= 6; i++) { k.beginPath(); k.moveTo(cx + i * 8 * s, cy - rh); k.lineTo(cx + i * 6 * s, cy + rh * 1.1); k.stroke(); } k.restore();
  }
}

// 水关：墙 + 拱 + 铁栅（门心 cx，水线 wy）
function waterGate(o, cx, wy, dw, opt = {}) {
  const k = o.ink, top = opt.top ?? 170, rect = [-20, top, 1960, wy - top];
  const ay = wy - dw * 0.55, d = new Path2D();
  d.moveTo(cx - dw / 2, wy); d.lineTo(cx - dw / 2, ay); d.arc(cx, ay, dw / 2, Math.PI, 0); d.lineTo(cx + dw / 2, wy); d.closePath();
  const wall = new Path2D(); wall.rect(...rect); o.knock(wall); k.fill(wall);
  BH.carve(k, 0, 0, 1, false, (c) => { c.lineWidth = 3; for (let y = top + 30, r = 0; y < wy; y += 56, r++) { c.beginPath(); c.moveTo(-20, y); c.lineTo(1940, y); c.stroke(); for (let x = (r % 2) * 70; x < 1940; x += 140) { c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 56); c.stroke(); } } });
  BH.erase(k, (c) => c.fill(d)); o.blueT.fillStyle = BH.tone(0.85); o.blueT.fill(d);         // 拱里黑
  k.lineWidth = 8; k.stroke(d);
  for (let x = cx - dw / 2 + 30; x < cx + dw / 2 - 10; x += 44) k.fillRect(x - 6, ay - dw / 2, 12, wy - ay + dw / 2);
  for (const yy of [ay - 40, ay + 90, wy - 60]) k.fillRect(cx - dw / 2, yy, dw, 12);
  return d;
}

// 一支长槊（从 (x0,y0) 刺向 (x1,y1)）；hot 为烧红的铁钩
function spear(o, x0, y0, x1, y1, hot = false) {
  const k = o.ink, a = Math.atan2(y1 - y0, x1 - x0), L2 = 46;
  k.lineWidth = 8; k.lineCap = 'round'; k.beginPath(); k.moveTo(x0, y0); k.lineTo(x1, y1); k.stroke();
  const head = new Path2D(); head.moveTo(x1, y1);
  head.lineTo(x1 + Math.cos(a) * L2 + Math.cos(a + 1.6) * 10, y1 + Math.sin(a) * L2 + Math.sin(a + 1.6) * 10);
  head.lineTo(x1 + Math.cos(a) * L2 * 1.5, y1 + Math.sin(a) * L2 * 1.5);
  head.lineTo(x1 + Math.cos(a) * L2 + Math.cos(a - 1.6) * 10, y1 + Math.sin(a) * L2 + Math.sin(a - 1.6) * 10); head.closePath();
  o.knock(head); (hot ? o.red : k).fill(head); k.lineWidth = 2.5; k.stroke(head);
  if (hot) {   // 铁钩：一个弯钩 + 热气
    const hx = x1 + Math.cos(a) * 20, hy = y1 + Math.sin(a) * 20;
    o.red.lineWidth = 9; o.red.lineCap = 'round'; o.red.beginPath(); o.red.moveTo(hx, hy); o.red.quadraticCurveTo(hx + Math.cos(a + 1.5) * 40, hy + Math.sin(a + 1.5) * 40, hx + Math.cos(a + 2.6) * 30, hy + Math.sin(a + 2.6) * 30); o.red.stroke();
    o.redT.fillStyle = BH.tone(0.4); o.redT.beginPath(); o.redT.arc(x1 + Math.cos(a) * 30, y1 + Math.sin(a) * 30, 60, 0, 7); o.redT.fill();
  }
}

// 骑电动车的人（朝右）：x 车中心，y 地线
function ebike(o, x, y, s = 1, light = true) {
  const k = o.ink, w1 = [x - 70 * s, y - 32 * s], w2 = [x + 78 * s, y - 32 * s], R = 32 * s;
  if (light) {   // 车灯照出一束光：把夜色挖掉
    const cone = new Path2D(); cone.moveTo(x + 96 * s, y - 96 * s); cone.lineTo(x + 900 * s, y - 210 * s); cone.lineTo(x + 900 * s, y + 10 * s); cone.closePath();
    BH.erase(o.blueT, (c) => c.fill(cone)); BH.erase(o.blue, (c) => c.fill(cone));
    o.redT.fillStyle = BH.tone(0.18); o.redT.fill(cone);
  }
  const body = new Path2D();
  for (const [wx, wy] of [w1, w2]) { body.moveTo(wx + R, wy); body.arc(wx, wy, R, 0, 7); }
  body.moveTo(x - 90 * s, y - 52 * s); body.lineTo(x + 40 * s, y - 56 * s); body.lineTo(x + 70 * s, y - 120 * s); body.lineTo(x + 92 * s, y - 120 * s); body.lineTo(x + 70 * s, y - 40 * s); body.lineTo(x - 90 * s, y - 34 * s); body.closePath();
  // 人：坐姿，背箱
  body.moveTo(x - 30 * s, y - 60 * s); body.quadraticCurveTo(x - 40 * s, y - 150 * s, x - 6 * s, y - 182 * s); body.lineTo(x + 30 * s, y - 176 * s); body.quadraticCurveTo(x + 60 * s, y - 150 * s, x + 76 * s, y - 120 * s); body.lineTo(x + 60 * s, y - 112 * s); body.quadraticCurveTo(x + 30 * s, y - 128 * s, x + 18 * s, y - 120 * s); body.lineTo(x + 22 * s, y - 60 * s); body.closePath();
  body.moveTo(x + 22 * s, y - 200 * s); body.arc(x + 6 * s, y - 206 * s, 24 * s, 0, 7);
  const box = new Path2D(); box.rect(x - 112 * s, y - 168 * s, 74 * s, 74 * s);
  o.knock(body); o.knock(box); k.fill(body); o.red.fill(box); k.lineWidth = 3; k.stroke(box);
  BH.erase(k, (c) => { for (const [wx, wy] of [w1, w2]) { c.beginPath(); c.arc(wx, wy, R * 0.55, 0, 7); c.fill(); } });
  BH.carve(k, 0, 0, 1, false, (c) => { c.lineWidth = 3; c.beginPath(); c.arc(x + 6 * s, y - 206 * s, 26 * s, Math.PI * 1.05, Math.PI * 1.9); c.stroke(); for (const [wx, wy] of [w1, w2]) for (let i = 0; i < 6; i++) { c.beginPath(); c.moveTo(wx, wy); c.lineTo(wx + Math.cos(i) * R * 0.9, wy + Math.sin(i) * R * 0.9); c.stroke(); } });
  k.fillStyle = P.paper; k.beginPath(); k.arc(x + 92 * s, y - 104 * s, 9 * s, 0, 7); k.fill(); k.fillStyle = P.ink;
}

// 高架桥：桥面 y0，桥墩
function overpass(o, y0, seed = 1) {
  const k = o.ink, deck = new Path2D(); deck.rect(-20, y0, 1960, 46); o.knock(deck); k.fill(deck);
  k.lineWidth = 3; k.beginPath(); k.moveTo(-20, y0 - 34); k.lineTo(1940, y0 - 34); k.stroke();
  for (let x = -20; x < 1940; x += 26) { k.beginPath(); k.moveTo(x, y0 - 34); k.lineTo(x, y0); k.stroke(); }
  for (const px of [260, 900, 1540]) { const p = new Path2D(); p.rect(px - 40, y0 + 46, 80, 1080 - y0); o.knock(p); o.inkT.fillStyle = BH.tone(0.7); o.inkT.fill(p); k.lineWidth = 4; k.stroke(p); }
  BH.carve(k, 0, 0, 1, false, (c) => { c.lineWidth = 2; for (let x = 40; x < 1940; x += 160) { c.beginPath(); c.moveTo(x, y0 + 12); c.lineTo(x + 80, y0 + 12); c.stroke(); } });
}

// 夜里的楼群（远景剪影 + 窗）
function skyline(o, base, seed = 5) {
  const r = BH.rng(seed), k = o.ink;
  for (let x = -40; x < 1960;) {
    const w = 90 + r() * 120, h = 160 + r() * 330, p = new Path2D(); p.rect(x, base - h, w, h);
    o.knock(p); o.inkT.fillStyle = BH.tone(0.55); o.inkT.fill(p); k.lineWidth = 3; k.stroke(p);
    for (let wy = base - h + 24; wy < base - 20; wy += 34) for (let wx = x + 16; wx < x + w - 20; wx += 30) if (r() < 0.22) { o.red.fillRect(wx, wy, 14, 18); }
    x += w + 10;
  }
}

// 手机（屏幕留白），返回屏幕矩形
function phone(o, x, y, w, h) {
  const k = o.ink, p = new Path2D(); p.roundRect ? p.roundRect(x, y, w, h, 40) : p.rect(x, y, w, h);
  o.knock(p); k.fill(p);
  const sc = [x + 24, y + 70, w - 48, h - 140]; BH.erase(k, (c) => c.fillRect(...sc));
  k.fillStyle = P.paper; k.beginPath(); k.arc(x + w / 2, y + h - 36, 16, 0, 7); k.fill(); k.fillStyle = P.ink;
  k.lineWidth = 2; k.strokeRect(...sc);
  // 手：从下面托着
  const hand = new Path2D(); hand.moveTo(x - 60, y + h + 200); hand.quadraticCurveTo(x - 50, y + h - 120, x + 10, y + h - 180); hand.lineTo(x + 30, y + h - 40); hand.quadraticCurveTo(x + w * 0.6, y + h + 30, x + w + 40, y + h - 60); hand.lineTo(x + w + 90, y + h + 200); hand.closePath();
  o.knock(hand); k.fill(hand); BH.carve(k, 0, 0, 1, false, (c) => { c.lineWidth = 3; c.beginPath(); c.moveTo(x - 20, y + h - 100); c.quadraticCurveTo(x - 10, y + h, x + 40, y + h + 60); c.stroke(); });
  return sc;
}
function bubble(o, x, y, text, right = false) {
  const k = o.ink, sz = 54, w = [...text].length * sz + 60, h = sz + 44, bx = right ? x - w : x, p = new Path2D(); p.rect(bx, y, w, h);
  if (right) { o.red.fill(p); BH.erase(o.red, (c) => BH.text(c, text, bx + w / 2, y + sz + 12, { size: sz, color: '#000' })); }
  else { k.lineWidth = 4; k.stroke(p); BH.text(k, text, bx + w / 2, y + sz + 12, { size: sz }); }
  k.lineWidth = 4; k.strokeRect(bx, y, w, h);
}

// 十七个“正”字 = 八十五天
function tally(o, rect) {
  const [x, y, w, h] = rect, cols = 6, rows = 3, cw = w / cols, rh = h / rows;
  for (let i = 0; i < 17; i++) { const c = i % cols, r = (i / cols) | 0; BH.text(o.ink, '正', x + cw * (c + 0.5), y + rh * (r + 0.78), { size: Math.min(cw, rh) * 0.82 }); }
  BH.text(o.red, '八十五', x + cw * 5.5, y + rh * 2.62, { size: Math.min(cw, rh) * 0.3, color: P.red });
}

// ================= 主题栏 =================
F.topic(0, '四月，江水涨到城下');
F.topic(pre(1), '八个门，两千人');
F.topic(pre(7, 0.25), '城门关着');
F.topic(pre(9), '铁钩先烧红了');
F.topic(pre(17, 0.25), '城门关着');
F.topic(L(19).end + 0.6, '马上就到');
F.topic(pre(24), '一条小船出了水关');
F.topic(pre(32, 0.25), '城门开着');
F.topic(L(35).end + 0.6, '守了八十五天');
F.topic(S.duration - 3.2, '头功给谁');

// ================= 前奏：第 0 帧就是封面 =================
F.shot('title', 0, (sh) => {
  sh.el({ depth: 0.2 }, (o) => { BH.sky(o, 0, 640, 111); BH.sun(o, 420, 330, 110); });
  sh.el({ depth: 0.5, box: [900, 330, 1020, 420] }, (o) => BH.city(o, 1450, 700, 940, 1.0));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.8, box: [0, 640, 1920, 440] }, (o) => { BH.waves(o, 680, 1080, 56, 13, 0.36, 1.3, ph); BH.crests(o, 690, 19, 230, 44, ph); }));
  sh.cycle(w, { period: B / 2 });
  sh.el({ depth: 1, box: [360, 170, 1200, 380] }, (o) => BH.titleCard(o, { title: F.vars.songTitle || '城门关着', sub: '一三六三 · 洪都', rect: [420, 190, 1080, 330] }));
  sh.push(1.06, { fy: 560 });
  F.kickBeats(1, 6, { every: 4, amt: 4 });
});
F.shot('approach', S.snap(6.2), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 600, 112));
  sh.el({ depth: 0.35, box: [1100, 330, 820, 360] }, (o) => BH.city(o, 1600, 640, 800, 0.8));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.8, box: [0, 600, 1920, 480] }, (o) => BH.waves(o, 620, 1080, 50, 14, 0.38, 1.25, ph)));
  sh.cycle(w, { period: B / 2 });
  [[260, 760, 0.62], [-120, 700, 0.42], [620, 690, 0.36]].forEach(([x, y, s], i) =>
    sh.el({ box: [x - 470 * s - 20, y - 520 * s, 980 * s + 40, 640 * s], depth: 0.6 + s * 0.5 }, (o) => BH.tower(o, x, y, s, { phase: i % 2 })).bob({ amp: 4, phase: i }).drift({ x: 260 }));
  sh.push(1.05, { fx: 1400, fy: 560 });
});

// ================= 主歌1 =================
F.shot('gates', pre(1), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 520, 121));
  sh.el({ box: [-20, 330, 1960, 560], depth: 0.8 }, (o) => longWall(o, 400, 880, { names: GATE_NAMES, nameSize: 30 }));
  sh.el({ box: [880, 120, 200, 300], depth: 0.8 }, (o) => BH.profile(o, 980, 372, 0.6, { robe: 'red' }));
  sh.el({ box: [0, 860, 1920, 220], depth: 0.9 }, (o) => BH.ground(o, 880, 1080, 122));
  sh.push(1.08, { fy: 520 });
}, { transition: 'paper' });

F.shot('flood', pre(2), (sh) => {
  sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 560, 131); BH.birds(o, [200, 200, 900, 200], 6, 132); });
  sh.el({ box: [-20, 300, 1960, 500], depth: 0.5 }, (o) => longWall(o, 380, 760, { n: 5, doorW: 100 }));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 620, 1920, 460] }, (o) => { BH.waves(o, 650, 1080, 52, 15, 0.4, 1.25, ph); BH.crests(o, 660, 21, 200, 50, ph); }));
  sh.cycle(w, { period: B / 2 });
  sh.el({ box: [1010, 190, 560, 170], depth: 1 }, (o) => BH.text(o.red, '一三六三', 1290, 320, { size: 110, color: P.red, spacing: 16 })).set({ alpha: 0 }, 0).from({ alpha: 0, y: 30 }, { at: at(sh, L(2).start), dur: 0.5 });
  sh.push(1.05, { fy: 700 });
});

F.shot('ship', pre(3), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 640, 141));
  const w = [0, 1].map((ph) => sh.el({ depth: 0.8, box: [0, 660, 1920, 420] }, (o) => BH.waves(o, 690, 1080, 44, 16, 0.4, 1.2, ph)));
  sh.cycle(w, { period: B / 2 });
  sh.el({ box: [180, 160, 1560, 720], depth: 1 }, (o) => BH.tower(o, 960, 820, 1.45));
  sh.camSet({ zoom: 1 }).camTo({ zoom: 1.32, fx: 900, fy: 700 }, { at: at(sh, L(4).start) - 0.2, dur: 2.4 });
  sh.kick(at(sh, charT(4, '铁')), 9);
}, { res: 1.35 });

F.shot('army', pre(5), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 520, 151));
  sh.el({ depth: 0.4, box: [-60, 300, 2040, 340] }, (o) => { for (let i = 0; i < 6; i++) BH.tower(o, 120 + i * 340, 600, 0.3, { phase: i % 2 }); });
  sh.el({ depth: 0.6, box: [0, 580, 1920, 140] }, (o) => BH.waves(o, 600, 700, 22, 17, 0.4, 1.1));
  sh.el({ depth: 0.9, box: [-40, 560, 2000, 340] }, (o) => { BH.ground(o, 860, 1080, 152); BH.crowd(o, -20, 1940, 870, 1.25, 153, { flags: 6, flagChar: '汉' }); });
  sh.el({ box: [1180, 170, 680, 150], depth: 1 }, (o) => BH.text(o.ink, '号称六十万', 1520, 280, { size: 96, spacing: 8 })).from({ alpha: 0 }, { at: 0.1, dur: 0.4 });
  sh.camSet({ zoom: 1.04, fx: 900 }).camTo({ fx: 1060 }, { dur: 'shot', ease: 'none' });
});

F.shot('run', pre(6), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 560, 161));
  sh.el({ box: [-20, 400, 1960, 520], depth: 0.8 }, (o) => longWall(o, 470, 880, { names: GATE_NAMES, nameSize: 30 }));
  const runner = sh.el({ box: [60, 120, 260, 360], depth: 0.8 }, (o) => BH.profile(o, 190, 440, 0.7, { robe: 'red' }));
  runner.bob({ amp: 8, period: B / 2 }).to({ x: 1000 }, { at: 0.1, dur: 'shot', ease: 'none' });
  sh.el({ box: [1480, 200, 420, 160], depth: 1 }, (o) => { BH.text(o.red, '两千人', 1690, 300, { size: 88, color: P.red }); }).set({ alpha: 0 }, 0).from({ alpha: 0, scale: 1.3 }, { at: at(sh, charT(6, '两')), dur: 0.3 });
});

// ================= 副歌 1 =================
F.shot('R1a', pre(7, 0.25), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 400, 171); bigGate(p, [1040, 300, 780, 540], 1430, 340, 'closed', { archY: 520 }); }));
  sh.type(7, { box: TYPE, color: (r) => (r === 1 ? 'red' : 'ink') });
  sh.push(1.04);
}, { transition: 'split' });
F.shot('R1b', pre(8, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => {
    BH.sky(p, 200, 560, 181); BH.sun(p, 1700, 560, 70);
    longWall(p, 520, 840, { x0: 1040, x1: 1820, n: 1, doorW: 1 });
    BH.erase(p.ink, (c) => { c.beginPath(); c.moveTo(1300, 520); c.lineTo(1340, 640); c.lineTo(1420, 600); c.lineTo(1480, 680); c.lineTo(1540, 520); c.fill(); });
    BH.erase(p.blueT, (c) => { c.beginPath(); c.moveTo(1300, 520); c.lineTo(1340, 640); c.lineTo(1420, 600); c.lineTo(1480, 680); c.lineTo(1540, 520); c.fill(); });
    BH.sentry(p, 1240, 520, 0.4); BH.robed(p, 1600, 520, 0.36);
    p.red.fillRect(1380, 560, 40, 24); p.ink.lineWidth = 3; p.ink.strokeRect(1380, 560, 40, 24);
  }));
  sh.type(8, { box: TYPE, rows: ['墙塌了', '天亮前', '又砌上'], color: (r) => (r === 2 ? 'red' : 'ink') });
});

// ================= 主歌2 =================
F.shot('shields', pre(9), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 420, 191));
  sh.el({ box: [-20, 200, 1960, 560], depth: 0.5 }, (o) => bigGate(o, [-20, 220, 1960, 520], 1500, 260, 'closed', { archY: 470 }));
  sh.el({ box: [0, 700, 1920, 380], depth: 0.9 }, (o) => BH.ground(o, 740, 1080, 192));
  sh.el({ box: [200, 170, 1500, 400], depth: 0.7 }, (o) => BH.arrows(o, [300, 180, 1300, 360], 14, 193)).to({ y: 120 }, { dur: 'shot', ease: 'none' });
  const sw = sh.el({ box: [-80, 640, 1500, 260], depth: 1 }, (o) => shields(o, -60, 1300, 880, 1.25, 194));
  sw.from({ x: -220 }, { at: 0, dur: 'shot', ease: 'none' }).bob({ amp: 4, period: B / 2 });
  sh.el({ box: [1500, 180, 380, 160], depth: 1 }, (o) => { BH.text(o.ink, '抚州门', 1690, 290, { size: 80 }); });
}, { transition: 'paper' });

F.shot('breach', pre(10), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 520, 201));
  sh.el({ box: [-20, 260, 1960, 640], depth: 0.6 }, (o) => {
    longWall(o, 320, 880, { n: 3, doorW: 1 });
    const gap = (c) => { c.beginPath(); c.moveTo(620, 280); c.lineTo(700, 520); c.lineTo(820, 470); c.lineTo(900, 880); c.lineTo(1260, 880); c.lineTo(1300, 560); c.lineTo(1380, 600); c.lineTo(1420, 280); c.fill(); };
    BH.erase(o.ink, gap); BH.erase(o.blueT, gap); BH.erase(o.mask, gap);
    for (let i = 0; i < 14; i++) { const r = BH.rng(202 + i); o.ink.fillRect(880 + r() * 420, 820 + r() * 50, 30 + r() * 30, 18 + r() * 14); }
  });
  sh.el({ box: [740, 360, 620, 520], depth: 0.75 }, (o) => { BH.sentry(o, 920, 870, 0.95); BH.sentry(o, 1100, 870, 0.95); });
  const sm = [0, 1].map((ph) => sh.el({ box: [800, 180, 520, 520], depth: 0.8 }, (o) => { BH.smoke(o, 1060, 600, 1.1, 203, ph); BH.fire(o, 1010, 640, 90, 120, ph); BH.fire(o, 1150, 640, 80, 110, ph, 7); }));
  sh.cycle(sm, { period: B / 2 });
  sm.forEach((e) => e.set({ alpha: 0 }, 0).set({ alpha: 1 }, at(sh, charT(10, '火'))));
  F.shake(charT(10, '铳'), 14, 0.5); sh.kick(at(sh, charT(10, '铳')), 12);
  sh.push(1.06, { fy: 620 });
});

F.shot('xincheng', pre(11), (sh) => {
  sh.el({ depth: 0.2 }, (o) => BH.sky(o, 120, 900, 211));
  sh.el({ box: [-20, 140, 1960, 780], depth: 0.6 }, (o) => { BH.archWall(o, [-20, 140, 1960, 760], [960, 470, 460]); BH.doors(o, 960, 400, 900, 460); BH.text(o.ink, '新城门', 960, 230, { size: 72 }); });
  sh.el({ box: [0, 880, 1920, 200], depth: 0.9 }, (o) => BH.ground(o, 900, 1080, 212));
  const men = [[960, 0.9, 0], [860, 0.8, 1], [1060, 0.8, 2]].map(([x, s, i]) => sh.el({ box: [x - 140, 420, 280, 480], depth: 1 }, (o) => BH.sentry(o, x, 890, s)));
  men.forEach((e, i) => e.set({ alpha: 0 }, 0).from({ scale: 0.55, y: -80, alpha: 0 }, { at: at(sh, L(12).start) - 0.4 + i * 0.25, dur: 1.4 }).bob({ amp: 6, period: B / 2, phase: i }));
  sh.camSet({ zoom: 1 }).camTo({ zoom: 1.18, fy: 640 }, { at: at(sh, L(12).start), dur: 2.6 });
}, { res: 1.2 });

F.shot('watergate', pre(13), (sh) => {
  sh.el({ box: [-20, 150, 1960, 640], depth: 0.5 }, (o) => waterGate(o, 1180, 760, 560));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => BH.waves(o, 760, 1080, 40, 22, 0.4, 1.2, ph)));
  sh.cycle(w, { period: B / 2 });
  sh.el({ box: [100, 560, 760, 360], depth: 1 }, (o) => { BH.boat(o, 420, 860, 1.25); BH.sentry(o, 560, 800, 0.62, { flip: true }); BH.sentry(o, 420, 800, 0.58, { flip: true }); });
  const sp = [0, 1].map((k) => sh.el({ box: [560, 300, 900, 520], depth: 0.8 }, (o) => { for (let i = 0; i < 3; i++) spear(o, 1060 + i * 90, 560 + i * 30, 760 - i * 40 - k * 80, 640 + i * 40 + k * 20); }));
  sh.cycle(sp, { period: B });
  sh.push(1.06, { fx: 900, fy: 620 });
});

F.shot('hot', pre(14), (sh) => {
  sh.el({ box: [-20, 150, 1960, 640], depth: 0.5 }, (o) => waterGate(o, 1180, 760, 560));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => BH.waves(o, 760, 1080, 40, 22, 0.4, 1.2, ph)));
  sh.cycle(w, { period: B / 2 });
  const sp = [0, 1, 2].map((ph) => sh.el({ box: [520, 260, 1000, 580], depth: 0.85 }, (o) => {
    for (let i = 0; i < 3; i++) spear(o, 1060 + i * 90, 560 + i * 30, 780 - i * 40, 640 + i * 40, true);
    BH.fire(o, 760, 660, 70, 90 + ph * 10, ph, 31);
  }));
  sh.cycle(sp, { period: B / 3 });
  sh.camSet({ zoom: 1.05 }).camTo({ zoom: 1.25, fx: 820, fy: 640 }, { at: 0.2, dur: 'shot' });
  sh.kick(at(sh, charT(14, '烧')), 10);
}, { res: 1.28 });

F.shot('arrow', pre(15), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 640, 231));
  sh.el({ box: [720, 300, 1200, 600], depth: 0.6 }, (o) => { BH.city(o, 1320, 880, 1000, 1.25); BH.text(o.ink, '宫步门', 1320, 840, { size: 54 }); });
  sh.el({ box: [1000, 340, 200, 300], depth: 0.6 }, (o) => BH.sentry(o, 1080, 600, 0.55, { flip: true }));
  const ar = sh.el({ box: [80, 420, 420, 80], depth: 0.8 }, (o) => { const k = o.ink; k.lineWidth = 5; k.beginPath(); k.moveTo(100, 470); k.lineTo(470, 450); k.stroke(); o.red.beginPath(); o.red.moveTo(490, 449); o.red.lineTo(460, 438); o.red.lineTo(462, 462); o.red.fill(); k.lineWidth = 3; for (const d of [0, 14]) { k.beginPath(); k.moveTo(100 + d, 470); k.lineTo(84 + d, 452); k.moveTo(100 + d, 470); k.lineTo(86 + d, 488); k.stroke(); } });
  const tHit = charT(15, '箭') - sh.t0;
  ar.set({ alpha: 0 }, 0).set({ alpha: 1 }, Math.max(0, tHit - 1.0)).to({ x: 560, y: 90 }, { at: Math.max(0, tHit - 1.0), dur: 1.0, ease: 'power1.in' });
  sh.kick(tHit, 12); F.shake(sh.t0 + tHit, 10, 0.35);
  sh.push(1.06, { fx: 1100, fy: 560 });
});

F.shot('book16', pre(16), (sh) => {
  sh.el({ box: [300, 130, 1320, 760] }, (o) => BH.bookPage(o, {
    center: '明史纪事本末卷三', seal: '洪都',
    cols: [{ text: '德胜巡城' }, { text: '至宫步门' }, { text: '箭深入六寸', size: 104, color: 'red' }, { text: '命也', size: 130 }],
    pic: (p, r) => { BH.sky(p, r[1], 600, 241); BH.city(p, r[0] + r[2] / 2, r[1] + r[3] - 30, 560, 0.55); },
  }));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.1, fy: 500 }, { at: 0.4, dur: 2.4 });
  sh.kick(at(sh, charT(16, '六')), 9);
}, { res: 1.25 });

// ================= 副歌 2 =================
F.shot('R2a', pre(17, 0.25), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.nightSky(p, 840, 251, [1680, 290, 46]); bigGate(p, [1040, 330, 780, 510], 1430, 320, 'closed', { archY: 540 }); }));
  sh.type(17, { box: TYPE, color: (r) => (r === 1 ? 'red' : 'ink') });
}, { transition: 'split' });
F.shot('R2b', pre(18, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => {
    BH.sky(p, 200, 560, 261);
    longWall(p, 470, 840, { x0: 1040, x1: 1820, n: 1, doorW: 1 });
    const k = p.ink; for (let i = 0; i < 12; i++) { const x = 1250 + i * 26; p.knockRect(x - 7, 560, 14, 280); k.fillRect(x - 7, 560, 14, 280); }
    k.fillRect(1240, 600, 330, 10); k.fillRect(1240, 760, 330, 10);
    BH.robed(p, 1660, 840, 0.4); BH.sentry(p, 1150, 840, 0.42);
  }));
  sh.type(18, { box: TYPE, rows: ['墙塌了', '天亮前', '又砌上'], color: (r) => (r === 2 ? 'red' : 'ink') });
});
F.shot('R2c', pre(19, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.nightSky(p, 840, 271, [1270, 300, 60]); bigGate(p, [1040, 360, 780, 480], 1430, 300, 'closed', { archY: 560 }); BH.lantern(p, 1240, 470, 0.5, true); }));
  sh.type(19, { box: TYPE, color: (r) => (r === 1 ? 'red' : 'ink') });
  sh.push(1.05);
});

// ================= 间奏：夜里的城 =================
F.shot('night', L(19).end + 0.6, (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.nightSky(o, 900, 281, [1500, 260, 70]));
  sh.el({ box: [-20, 330, 1960, 580], depth: 0.6 }, (o) => longWall(o, 440, 880, { n: 6, doorW: 110 }));
  [260, 760, 1260, 1700].forEach((x, i) => sh.el({ box: [x - 70, 250, 140, 200], depth: 0.6 }, (o) => BH.lantern(o, x, 360, 0.6, true)).sway({ deg: 3, phase: i }));
  sh.el({ box: [400, 160, 1200, 280], depth: 0.6 }, (o) => { for (const x of [520, 1020, 1480]) BH.sentry(o, x, 410, 0.5); });
  sh.push(1.08, { fy: 520 });
}, { transition: 'paper' });

// ================= 桥段（古今并置）=================
F.shot('ebike', pre(20), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.nightSky(o, 1080, 291, [300, 220, 54]));
  sh.el({ depth: 0.3, box: [-40, 200, 2000, 520] }, (o) => skyline(o, 700, 292));
  sh.el({ depth: 0.7, box: [-20, 640, 1960, 440] }, (o) => overpass(o, 700, 293));
  const rider = sh.el({ box: [0, 300, 1300, 420], depth: 0.9 }, (o) => ebike(o, 360, 700, 1.4, true));
  rider.bob({ amp: 3, period: B / 2 }).from({ x: -360 }, { at: 0, dur: 'shot', ease: 'none' });
  sh.kick(at(sh, L(21).start), 6);
}, { transition: 'wipe' });

F.shot('phone', pre(22), (sh) => {
  sh.el({ depth: 0.1 }, (o) => { BH.nightSky(o, 1080, 301); skyline(o, 900, 302); });
  sh.el({ box: [520, 120, 900, 960], depth: 0.8 }, (o) => phone(o, 700, 160, 520, 760));
  const q = sh.el({ box: [740, 280, 440, 140], depth: 0.8 }, (o) => bubble(o, 760, 300, '到哪儿了'));
  q.set({ alpha: 0 }, 0).set({ alpha: 1 }, at(sh, charT(22, '到'))).from({ scale: 0.7 }, { at: at(sh, charT(22, '到')), dur: 0.25, ease: 'back.out(2)' });
  const a = sh.el({ box: [740, 470, 440, 140], depth: 0.8 }, (o) => bubble(o, 1160, 490, '马上就到', true));
  a.set({ alpha: 0 }, 0).set({ alpha: 1 }, at(sh, L(23).start + 0.3)).from({ scale: 0.7 }, { at: at(sh, L(23).start + 0.3), dur: 0.25, ease: 'back.out(2)' });
  const a2 = sh.el({ box: [740, 640, 440, 140], depth: 0.8 }, (o) => bubble(o, 1160, 660, '马上就到', true));
  a2.set({ alpha: 0 }, 0).set({ alpha: 1 }, at(sh, charT(23, '马', 1))).from({ scale: 0.7 }, { at: at(sh, charT(23, '马', 1)), dur: 0.25, ease: 'back.out(2)' });
  sh.push(1.05, { fy: 500 });
});

// ================= 主歌3：张子明 =================
F.shot('boat', pre(24), (sh) => {
  sh.el({ box: [-20, 0, 1960, 760], depth: 0.4 }, (o) => { BH.nightSky(o, 760, 311, [1650, 200, 50]); waterGate(o, 900, 740, 520, { top: 300 }); });
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => { o.blueT.fillStyle = BH.tone(0.45); o.blueT.fillRect(0, 740, 1920, 340); BH.waves(o, 740, 1080, 34, 23, 0.38, 1.2, ph); }));
  sh.cycle(w, { period: B / 2 });
  const bt = sh.el({ box: [600, 560, 600, 330], depth: 1 }, (o) => BH.boat(o, 900, 860, 1.4));
  bt.bob({ amp: 4 }).to({ x: -640, y: 20, scale: 1.15 }, { at: 0.2, dur: 'shot', ease: 'none' });
}, { transition: 'wipe' });

F.shot('walk', pre(25), (sh) => {
  const night = sh.el({ depth: 0.15 }, (o) => BH.nightSky(o, 760, 321, [1500, 230, 60]));
  const day = sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 760, 322); BH.sun(o, 1500, 260, 90); });
  const tDay = at(sh, charT(25, '白'));
  day.set({ alpha: 0 }, 0).set({ alpha: 1 }, tDay); night.set({ alpha: 1 }, 0).set({ alpha: 0 }, tDay);
  sh.el({ depth: 0.4, box: [-60, 420, 2040, 360] }, (o) => BH.mount(o, -60, 2000, 760, 260, 323, 0.6));
  sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 324));
  const man = sh.el({ box: [200, 380, 300, 520], depth: 0.9 }, (o) => BH.profile(o, 340, 870, 0.95));
  man.bob({ amp: 6, period: B / 2 }).to({ x: 520 }, { at: 0, dur: tDay, ease: 'none' }).to({ alpha: 0 }, { at: tDay, dur: 0.1 });
  const lying = sh.el({ box: [700, 700, 700, 200], depth: 0.95 }, (o) => {
    const k = o.ink, p = new Path2D(); p.ellipse(1040, 850, 200, 34, 0, 0, 7); p.moveTo(1270, 840); p.arc(1250, 838, 26, 0, 7); o.knock(p); k.fill(p);
    BH.reeds(o, 720, 1380, 880, 325);
  });
  lying.set({ alpha: 0 }, 0).set({ alpha: 1 }, tDay);
});

F.shot('arrive', pre(26), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 600, 331));
  sh.el({ depth: 0.5, box: [700, 300, 1100, 460] }, (o) => { BH.city(o, 1250, 740, 1000, 0.95); BH.text(o.ink, '应天', 1250, 400, { size: 80 }); });
  sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => BH.ground(o, 740, 1080, 332));
  const man = sh.el({ box: [180, 560, 200, 340], depth: 0.9 }, (o) => BH.profile(o, 280, 880, 0.6));
  man.bob({ amp: 5, period: B / 2 }).to({ x: 760, scale: 0.8 }, { at: 0, dur: 'shot', ease: 'none' });
  sh.el({ box: [140, 180, 420, 160], depth: 1 }, (o) => BH.text(o.red, '半个月', 350, 290, { size: 96, color: P.red })).set({ alpha: 0 }, 0).from({ alpha: 0 }, { at: at(sh, charT(26, '半')), dur: 0.3 });
  sh.push(1.06, { fx: 1100, fy: 560 });
});

F.shot('book27', pre(27), (sh) => {
  sh.el({ box: [300, 130, 1320, 760] }, (o) => BH.bookPage(o, {
    center: '明史卷一百三十三', seal: '应天',
    cols: [{ text: '太祖谓子明' }, { text: '归语而帅' }, { text: '坚守一月', size: 124, color: 'red' }, { text: '吾自取之', size: 124 }],
    pic: (p, r) => { BH.sky(p, r[1], 620, 341); BH.throne(p, r[0] + r[2] / 2, r[1] + r[3] - 30, 0.75, { sitter: 0.36 }); },
  }));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.1, fy: 500 }, { at: 0.5, dur: 2.6 });
  sh.kick(at(sh, charT(27, '一')), 8);
}, { res: 1.26 });

F.shot('seized', pre(28), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 620, 351));
  sh.el({ depth: 0.45, box: [900, 280, 1040, 460] }, (o) => BH.tower(o, 1500, 690, 0.62));
  sh.el({ depth: 0.7, box: [0, 660, 1920, 140] }, (o) => BH.waves(o, 680, 760, 24, 352, 0.4, 1.1));
  sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => { BH.ground(o, 760, 1080, 353); BH.reeds(o, 1200, 1900, 880, 354); BH.text(o.ink, '湖口', 1700, 330, { size: 72 }); });
  sh.el({ box: [340, 360, 760, 540], depth: 1 }, (o) => { BH.sentry(o, 520, 880, 1.0); BH.robed(o, 720, 880, 0.95); BH.sentry(o, 920, 880, 1.0, { flip: true }); });
  sh.push(1.08, { fx: 720, fy: 620 });
  sh.kick(at(sh, charT(28, '抓')), 9);
});

F.shot('below', pre(29), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 300, 361));
  sh.el({ box: [-20, 140, 1960, 640], depth: 0.4 }, (o) => { longWall(o, 230, 760, { n: 3, doorW: 180 }); for (let x = 60; x < 1900; x += 80) BH.sentry(o, x, 210, 0.3); });
  sh.el({ depth: 0.8, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 362));
  sh.el({ box: [-40, 520, 2000, 380], depth: 0.95 }, (o) => BH.crowd(o, -20, 1940, 880, 1.6, 363));
  sh.el({ box: [860, 420, 200, 480], depth: 0.95 }, (o) => BH.robed(o, 960, 880, 1.0));
  sh.push(1.07, { fy: 560 });
});

F.shot('shout', pre(30), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 520, 371));
  sh.el({ box: [-20, 140, 1960, 600], depth: 0.4 }, (o) => longWall(o, 200, 700, { n: 2, doorW: 200 }));
  sh.el({ depth: 0.8, box: [0, 700, 1920, 380] }, (o) => BH.ground(o, 720, 1080, 372));
  sh.el({ box: [460, 300, 320, 600], depth: 0.95 }, (o) => BH.profile(o, 620, 885, 1.3, { flip: true }));
  ['救', '且', '至'].forEach((ch, i) => {
    const e = sh.el({ box: [870, 160 + i * 220, 260, 240], depth: 1 }, (o) => { BH.erase(o.blueT, (c) => c.fillRect(890, 190 + i * 220, 220, 210)); BH.text(o.red, ch, 1000, 360 + i * 220, { size: 200, color: P.red }); });
    const t = at(sh, charT(30, ['救', '要', '到'][i]));
    e.set({ alpha: 0 }, 0).set({ alpha: 1 }, t).from({ scale: 1.4 }, { at: t, dur: 0.22, ease: 'back.out(2.2)' });
    sh.kick(t, 9);
  });
  sh.el({ box: [1460, 760, 420, 80], depth: 1 }, (o) => BH.text(o.ink, '《明史》', 1680, 820, { size: 40, weight: '600' })).from({ alpha: 0 }, { at: 0.6, dur: 0.4 });
});

F.shot('spears', pre(31), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 640, 381));
  sh.el({ box: [-20, 140, 1960, 640], depth: 0.4 }, (o) => longWall(o, 230, 760, { n: 3, doorW: 180 }));
  sh.el({ depth: 0.8, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 382));
  const fall = sh.el({ box: [200, 160, 1520, 740], depth: 0.95 }, (o) => {
    for (let i = 0; i < 9; i++) { const x0 = 260 + i * 170, y0 = 180; spear(o, x0, y0, 900 + (i - 4) * 18, 800 - Math.abs(i - 4) * 14); }
  });
  const tDrop = at(sh, charT(31, '落'));
  fall.set({ alpha: 0 }, 0).from({ y: -420, alpha: 0 }, { at: tDrop - 0.5, dur: 0.5, ease: 'power3.in' });
  F.shake(sh.t0 + tDrop, 16, 0.6); sh.kick(tDrop, 14);
  sh.el({ box: [800, 820, 320, 70], depth: 1 }, (o) => BH.shadow(o, 960, 860, 140, 18, 0.55));
});

// ================= 最后的副歌：朱色大字 =================
F.shot('F1', pre(32, 0.25), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 840, 391); BH.sun(p, 1430, 560, 90); BH.archWall(p, [1040, 300, 780, 540], [1430, 540, 300]); BH.doors(p, 1430, 500, 840, 300); }));
  sh.type(32, { box: TYPE, color: 'red' });
  sh.push(1.04);
}, { transition: 'split' });
F.shot('F2', pre(33, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => tally(p, [1080, 240, 700, 560])));
  sh.type(33, { box: TYPE, rows: ['一座城', '守了', '八十五天'], color: 'red', scale: [0.8, 0.8, 1] });
});
F.shot('F3', pre(34, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 560, 401); for (let i = 0; i < 4; i++) BH.tower(p, 1100 + i * 190, 600 + i * 50, 0.18 + i * 0.05, { phase: i % 2 }); BH.waves(p, 600, 840, 26, 402, 0.4, 1.2); }));
  sh.type(34, { box: TYPE, color: 'red' });
});
F.shot('F4', pre(35, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => {
    BH.sky(p, 200, 700, 411);
    const d = BH.archWall(p, [1040, 200, 780, 640], [1430, 470, 420]);
    BH.ground(p, 700, 840, 412); BH.waves(p, 760, 840, 20, 413, 0.3, 1.1);
  }));
  sh.type(35, { box: TYPE, rows: ['喊话的', '那个人', '没有进来'], color: 'red' });
  sh.push(1.05);
});

// ================= 尾奏 =================
F.shot('dawn', L(35).end + 0.6, (sh) => {
  sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 620, 421); BH.sun(o, 1500, 520, 130); });
  sh.el({ box: [-20, 300, 1960, 440], depth: 0.5 }, (o) => longWall(o, 400, 700, { names: GATE_NAMES, nameSize: 26, doorW: 96, open: [0, 1, 2, 3, 4, 5, 6, 7] }));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.85, box: [0, 680, 1920, 400] }, (o) => BH.waves(o, 700, 1080, 30, 422, 0.3, 1.2, ph)));
  sh.cycle(w, { period: B });
  sh.push(1.06, { fy: 560 });
}, { transition: 'paper' });

F.shot('card', S.snap(147.5), (sh) => {
  sh.el({ box: [240, 170, 1440, 700] }, (o) => BH.card(o, {
    ep: F.vars.epNo, series: F.vars.series, title: '洪都守了八十五天', kind: 'timeline', src: '据《明史》《明史纪事本末》',
    items: [{ a: '四月', b: '号称六十万' }, { a: '五月', b: '薛显开门突击' }, { a: '六月', b: '水关烧红铁钩' }, { a: '七月', b: '援军到 围解' }],
  }));
  sh.push(1.03);
}, { transition: 'paper' });

F.shot('quiet', S.snap(158.5), (sh) => {
  sh.el({ box: [-20, 0, 1960, 760], depth: 0.4 }, (o) => { BH.nightSky(o, 760, 431, [480, 210, 56]); waterGate(o, 1250, 740, 520, { top: 320 }); });
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => { o.blueT.fillStyle = BH.tone(0.45); o.blueT.fillRect(0, 740, 1920, 340); BH.waves(o, 740, 1080, 34, 432, 0.3, 1.2, ph); }));
  sh.cycle(w, { period: B });
  sh.el({ box: [180, 640, 440, 240], depth: 1 }, (o) => { BH.boat(o, 400, 860, 0.9); BH.lantern(o, 330, 770, 0.4, true); }).bob({ amp: 3, period: B * 2 }).drift({ x: 380 });
  sh.push(1.06, { fy: 600 });
}, { transition: 'paper' });

F.shot('quiet2', S.snap(167.6), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.nightSky(o, 900, 441, [1500, 240, 60]));
  sh.el({ box: [-20, 330, 1960, 580], depth: 0.6 }, (o) => longWall(o, 440, 880, { n: 6, doorW: 110, open: [0, 1, 2, 3, 4, 5] }));
  [260, 960, 1660].forEach((x, i) => sh.el({ box: [x - 70, 250, 140, 200], depth: 0.6 }, (o) => BH.lantern(o, x, 360, 0.6, true)).sway({ deg: 3, phase: i }));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.15, fy: 560 }, { dur: 'shot' });
}, { res: 1.16 });

// ================= 片尾卡 =================
F.shot('end', S.duration - 3.2, (sh) => {
  sh.el({ box: [240, 180, 1440, 680] }, (o) => BH.endCard(o, { question: '洪都守住了，头功给谁？', options: ['朱文正', '邓愈', '张子明'], next: `下一集 · ${F.vars.nextTitle || '康郎山下 两支船队'}` }));
}, { transition: 'cut', subs: false });

F.finish();
