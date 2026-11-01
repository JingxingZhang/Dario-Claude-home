// 第11集《救兵就要到》分镜（v5 歌词）。歌讲张子明一个人，守城的经过放在前奏、间奏、尾奏的画面里。
// 主歌、导歌：版画画面；副歌：大字排版 + 右侧画框。每个 sh.el(...) 是一块印好的版。
const F = BH.film();
const S = F.song, L = S.line, B = S.beatPeriod, P = BH.PAL;
const pre = (n, d = 0.3) => L(n).start - d;
const at = (sh, t) => Math.max(0, t - sh.t0);
const charT = (n, ch, k = 0) => L(n).chars.filter((c) => c.c === ch)[k].s;
const TYPE = [110, 210, 860, 660], FRAME = [1040, 200, 780, 640], FBOX = [1000, 160, 860, 740];

// ================= 本章自画的东西 =================
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

// 十七个“正”字 = 八十五天
function tally(o, rect) {
  const [x, y, w, h] = rect, cols = 6, rows = 3, cw = w / cols, rh = h / rows;
  for (let i = 0; i < 17; i++) { const c = i % cols, r = (i / cols) | 0; BH.text(o.ink, '正', x + cw * (c + 0.5), y + rh * (r + 0.78), { size: Math.min(cw, rh) * 0.82 }); }
  BH.text(o.red, '八十五', x + cw * 5.5, y + rh * 2.62, { size: Math.min(cw, rh) * 0.3, color: P.red });
}


// 庙：台基、四柱、朱门、匾、屋顶
function temple(o, cx, base, w, plaque = '忠臣庙') {
  const k = o.ink, h = w * 0.42, top = base - h;
  const plat = new Path2D(); plat.rect(cx - w * 0.6, base - 40, w * 1.2, 40); o.knock(plat); k.fill(plat);
  const body = new Path2D(); body.rect(cx - w / 2, top, w, h - 40); o.knock(body); o.blueT.fillStyle = BH.tone(0.22); o.blueT.fill(body); k.lineWidth = 5; k.stroke(body);
  for (const fx of [-0.42, -0.16, 0.16, 0.42]) k.fillRect(cx + fx * w - 12, top, 24, h - 40);
  const door = new Path2D(); door.rect(cx - w * 0.12, top + h * 0.3, w * 0.24, h * 0.7 - 40); o.red.fill(door); k.lineWidth = 4; k.stroke(door);
  k.beginPath(); k.moveTo(cx, top + h * 0.3); k.lineTo(cx, base - 40); k.stroke();
  const roof = BH.roof(cx, top + 6, w * 0.62, h * 0.55, 30); o.knock(roof); k.fill(roof);
  BH.carve(k, 0, 0, 1, false, (c) => { c.lineWidth = 3; for (let i = 1; i < 6; i++) { c.beginPath(); c.moveTo(cx - w * 0.6 + i * 6, top - i * h * 0.08); c.lineTo(cx + w * 0.6 - i * 6, top - i * h * 0.08); c.stroke(); } });
  const pw = w * 0.3, ph = 70, py = top + 20; BH.erase(o.blueT, (c) => c.fillRect(cx - pw / 2, py, pw, ph)); k.fillStyle = P.paper; k.fillRect(cx - pw / 2, py, pw, ph); k.fillStyle = P.ink; k.lineWidth = 4; k.strokeRect(cx - pw / 2, py, pw, ph);
  BH.text(k, plaque, cx, py + ph * 0.74, { size: ph * 0.62 });
}
// 一排塑像（n 尊，第 hi 尊朱色）
function statues(o, x0, x1, base, n = 14, hi = 8) {
  const k = o.ink, gap = (x1 - x0) / n;
  k.fillRect(x0 - 20, base, x1 - x0 + 40, 18); o.knockRect(x0 - 20, base, x1 - x0 + 40, 18);
  for (let i = 0; i < n; i++) {
    const cx = x0 + gap * (i + 0.5), s = Math.min(0.42, gap / 180);
    BH.robed(o, cx, base, s, i + 1 === hi ? { robe: 'red' } : {});
  }
}

// ================= 主题栏 =================
F.topic(0, '四月，船停满了江');
F.topic(pre(1), '一个千户出了城');
F.topic(pre(9), '坚守一个月');
F.topic(pre(11, 0.25), '守住啊');
F.topic(pre(14), '回来的路上');
F.topic(pre(20), '城下');
F.topic(pre(21, 0.25), '守住啊');
F.topic(L(23).end + 0.5, '城里的八十五天');
F.topic(pre(24), '他喊的是这一句');
F.topic(pre(28), '后来');
F.topic(pre(31, 0.25), '守住了');
F.topic(L(33).end + 0.4, '守了八十五天');
F.topic(S.duration - 3.2, '头功给谁');

// ================= 前奏：第 0 帧就是封面；第二镜交代围城 =================
F.shot('title', 0, (sh) => {
  sh.el({ depth: 0.2 }, (o) => { BH.sky(o, 0, 640, 511); BH.sun(o, 420, 330, 110); });
  sh.el({ depth: 0.5, box: [900, 330, 1020, 420] }, (o) => BH.city(o, 1450, 700, 940, 1.0));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.8, box: [0, 640, 1920, 440] }, (o) => { BH.waves(o, 680, 1080, 56, 13, 0.36, 1.3, ph); BH.crests(o, 690, 19, 230, 44, ph); }));
  sh.cycle(w, { period: B / 2 });
  sh.el({ depth: 1, box: [360, 170, 1200, 380] }, (o) => BH.titleCard(o, { title: F.vars.songTitle || '救兵就要到', sub: '一三六三 · 洪都', rect: [420, 190, 1080, 330] }));
  sh.push(1.06, { fy: 560 });
  F.kickBeats(1, 6, { every: 4, amt: 4 });
});
F.shot('siege', S.snap(6.2), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 520, 512));
  sh.el({ box: [-20, 300, 1960, 420], depth: 0.45 }, (o) => longWall(o, 360, 640, { names: ['抚州', '宫步', '士步', '桥步', '章江', '新城', '琉璃', '澹台'], nameSize: 26, doorW: 92 }));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.8, box: [0, 620, 1920, 460] }, (o) => BH.waves(o, 640, 1080, 48, 14, 0.38, 1.25, ph)));
  sh.cycle(w, { period: B / 2 });
  [[200, 830, 0.5], [760, 800, 0.4], [1300, 840, 0.52], [-200, 780, 0.34]].forEach(([x, y, s], i) =>
    sh.el({ box: [x - 470 * s - 20, y - 520 * s, 980 * s + 40, 640 * s], depth: 0.6 + s * 0.6 }, (o) => BH.tower(o, x, y, s, { phase: i % 2 })).bob({ amp: 4, phase: i }).drift({ x: 160 }));
  sh.el({ box: [860, 230, 700, 150], depth: 1 }, (o) => BH.text(o.red, '号称六十万', 1200, 330, { size: 92, color: P.red, spacing: 6 })).set({ alpha: 0 }, 0).from({ alpha: 0, scale: 1.3 }, { at: 1.6, dur: 0.4 });
  sh.push(1.05, { fy: 600 });
});

// ================= 主歌1：出城、到应天 =================
F.shot('me', pre(1), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 700, 521));
  sh.el({ box: [-20, 560, 1960, 360], depth: 0.5 }, (o) => longWall(o, 620, 900, { n: 4, doorW: 110 }));
  sh.el({ box: [780, 120, 360, 520], depth: 0.9 }, (o) => BH.profile(o, 960, 622, 1.15));
  sh.el({ box: [1260, 200, 520, 300], depth: 1 }, (o) => { BH.text(o.ink, '张子明', 1500, 330, { size: 110 }); BH.text(o.red, '领兵千户', 1500, 430, { size: 60, color: P.red }); })
    .set({ alpha: 0 }, 0).from({ alpha: 0, x: 40 }, { at: at(sh, charT(1, '张')), dur: 0.4 });
  sh.push(1.06, { fy: 480 });
}, { transition: 'paper' });

F.shot('surrounded', pre(2), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 520, 531));
  sh.el({ box: [480, 260, 960, 380], depth: 0.5 }, (o) => BH.city(o, 960, 600, 900, 0.9));
  sh.el({ box: [-40, 560, 2000, 360], depth: 0.75 }, (o) => { BH.ground(o, 640, 1080, 532); BH.tents(o, 20, 1900, 760, 1.0, 533); BH.crowd(o, -20, 1940, 880, 1.15, 534, { flags: 6, flagChar: '汉' }); });
  sh.el({ box: [80, 170, 600, 160], depth: 1 }, (o) => BH.text(o.red, '一三六三', 360, 290, { size: 100, color: P.red, spacing: 12 })).set({ alpha: 0 }, 0).from({ alpha: 0 }, { at: at(sh, L(2).start), dur: 0.4 });
  sh.push(1.05, { fy: 560 });
});

F.shot('order', pre(3), (sh) => {
  sh.el({ depth: 0.2 }, (o) => { o.blueT.fillStyle = BH.tone(0.5); o.blueT.fillRect(0, 0, 1920, 880); o.knockRect(0, 0, 1920, 880); BH.windowFrame(o, [180, 200, 340, 420], 4, 5, 10); BH.windowFrame(o, [1400, 200, 340, 420], 4, 5, 10); o.ink.lineWidth = 6; o.ink.beginPath(); o.ink.moveTo(0, 880); o.ink.lineTo(1920, 880); o.ink.stroke(); });
  sh.el({ box: [1000, 300, 340, 600], depth: 0.9 }, (o) => BH.robed(o, 1160, 880, 1.2, { robe: 'red' }));
  sh.el({ box: [560, 340, 320, 560], depth: 0.9 }, (o) => BH.profile(o, 720, 880, 1.05));
  sh.el({ box: [1020, 230, 480, 140], depth: 1 }, (o) => BH.text(o.ink, '大都督 朱文正', 1260, 320, { size: 62 }));
  sh.kick(at(sh, charT(3, '名')), 8);
  sh.push(1.06, { fx: 940, fy: 600 });
});

F.shot('boat', pre(4), (sh) => {
  sh.el({ box: [-20, 0, 1960, 760], depth: 0.4 }, (o) => { BH.nightSky(o, 760, 541, [1650, 200, 50]); waterGate(o, 900, 740, 520, { top: 300 }); });
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => { o.blueT.fillStyle = BH.tone(0.45); o.blueT.fillRect(0, 740, 1920, 340); BH.waves(o, 740, 1080, 34, 23, 0.38, 1.2, ph); }));
  sh.cycle(w, { period: B / 2 });
  sh.el({ box: [600, 560, 600, 330], depth: 1 }, (o) => BH.boat(o, 900, 860, 1.4)).bob({ amp: 4 }).to({ x: -640, y: 20, scale: 1.15 }, { at: 0.2, dur: 'shot', ease: 'none' });
});

F.shot('walk', pre(5), (sh) => {
  const night = sh.el({ depth: 0.15 }, (o) => BH.nightSky(o, 760, 551, [1500, 230, 60]));
  const day = sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 760, 552); BH.sun(o, 1500, 260, 90); });
  const tDay = at(sh, charT(5, '天'));
  day.set({ alpha: 0 }, 0).set({ alpha: 1 }, tDay); night.set({ alpha: 1 }, 0).set({ alpha: 0 }, tDay);
  sh.el({ depth: 0.4, box: [-60, 420, 2040, 360] }, (o) => BH.mount(o, -60, 2000, 760, 260, 553, 0.6));
  sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 554));
  const man = sh.el({ box: [200, 380, 300, 520], depth: 0.9 }, (o) => BH.profile(o, 340, 870, 0.95));
  man.bob({ amp: 6, period: B / 2 }).to({ x: 520 }, { at: 0, dur: tDay, ease: 'none' }).to({ alpha: 0 }, { at: tDay, dur: 0.1 });
  const lying = sh.el({ box: [700, 700, 700, 200], depth: 0.95 }, (o) => { const p = new Path2D(); p.ellipse(1040, 850, 200, 34, 0, 0, 7); p.moveTo(1270, 840); p.arc(1250, 838, 26, 0, 7); o.knock(p); o.ink.fill(p); BH.reeds(o, 720, 1380, 880, 555); });
  lying.set({ alpha: 0 }, 0).set({ alpha: 1 }, tDay);
});

F.shot('arrive', pre(6), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 600, 561));
  sh.el({ depth: 0.5, box: [700, 300, 1100, 460] }, (o) => { BH.city(o, 1250, 740, 1000, 0.95); BH.text(o.ink, '应天', 1250, 400, { size: 80 }); });
  sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => BH.ground(o, 740, 1080, 562));
  sh.el({ box: [180, 560, 200, 340], depth: 0.9 }, (o) => BH.profile(o, 280, 880, 0.6)).bob({ amp: 5, period: B / 2 }).to({ x: 600, scale: 0.85 }, { at: 0, dur: 'shot', ease: 'none' });
  sh.el({ box: [140, 180, 420, 160], depth: 1 }, (o) => BH.text(o.red, '半个月', 350, 290, { size: 96, color: P.red })).set({ alpha: 0 }, 0).from({ alpha: 0 }, { at: at(sh, charT(6, '半')), dur: 0.3 });
  sh.push(1.06, { fx: 1100, fy: 560 });
});

F.shot('audience', pre(7), (sh) => {
  sh.el({ depth: 0.2 }, (o) => { o.blueT.fillStyle = BH.tone(0.5); o.blueT.fillRect(0, 0, 1920, 760); o.knockRect(0, 0, 1920, 760); const k = o.ink; k.lineWidth = 3; for (let i = -12; i <= 12; i++) { k.beginPath(); k.moveTo(960 + i * 40, 760); k.lineTo(960 + i * 190, 1080); k.stroke(); } k.lineWidth = 6; k.beginPath(); k.moveTo(0, 760); k.lineTo(1920, 760); k.stroke(); });
  sh.el({ box: [1060, 260, 700, 640], depth: 0.8 }, (o) => { BH.shadow(o, 1400, 866, 300, 30, 0.6); BH.throne(o, 1400, 860, 1.4, { sitter: 0.4 }); });
  sh.el({ box: [360, 400, 300, 500], depth: 0.95 }, (o) => BH.profile(o, 500, 880, 1.0));
  sh.push(1.05, { fx: 1000, fy: 620 });
});

F.shot('lowwater', pre(8), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 600, 571));
  sh.el({ depth: 0.6, box: [0, 560, 1920, 520] }, (o) => { BH.ground(o, 600, 1080, 572); for (let i = 0; i < 6; i++) { o.ink.lineWidth = 2; o.ink.beginPath(); o.ink.moveTo(0, 640 + i * 22); o.ink.lineTo(1920, 640 + i * 22); o.ink.stroke(); } o.blueT.fillStyle = BH.tone(0.5); o.blueT.fillRect(0, 800, 1920, 280); });
  const w = [0, 1].map((ph) => sh.el({ depth: 0.8, box: [0, 790, 1920, 120] }, (o) => BH.waves(o, 800, 900, 22, 573, 0.4, 1.1, ph)));
  sh.cycle(w, { period: B / 2 });
  sh.el({ box: [400, 300, 1120, 560], depth: 0.9 }, (o) => BH.tower(o, 960, 820, 1.0));
  sh.el({ box: [1000, 270, 460, 140], depth: 1 }, (o) => BH.text(o.ink, '江水日涸', 1230, 380, { size: 88 })).set({ alpha: 0 }, 0).from({ alpha: 0 }, { at: at(sh, charT(8, '江')), dur: 0.4 });
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.12, fy: 700 }, { dur: 'shot' });
}, { res: 1.14 });

// ================= 导歌1：朱元璋的话（刻本书页）=================
F.shot('book9', pre(9), (sh) => {
  sh.el({ box: [300, 130, 1320, 760] }, (o) => BH.bookPage(o, {
    center: '明史卷一百三十三', seal: '应天',
    cols: [{ text: '太祖谓子明' }, { text: '归语而帅' }, { text: '坚守一月', size: 124, color: 'red' }, { text: '吾自取之', size: 124 }],
    pic: (p, r) => { BH.sky(p, r[1], 620, 581); BH.throne(p, r[0] + r[2] / 2, r[1] + r[3] - 30, 0.75, { sitter: 0.36 }); },
  }));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.1, fy: 500 }, { at: 0.5, dur: 3.0 });
  sh.kick(at(sh, charT(10, '坚')), 9);
}, { res: 1.14, transition: 'paper' });

// ================= 副歌1 =================
F.shot('C1a', pre(11, 0.25), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 560, 591); longWall(p, 520, 840, { x0: 1040, x1: 1820, n: 2, doorW: 120 }); for (const x of [1120, 1240, 1360, 1480, 1600, 1720]) BH.sentry(p, x, 490, 0.36); }));
  sh.type(11, { box: TYPE, color: (r) => (r === 1 ? 'red' : 'ink') });
  sh.push(1.04);
}, { transition: 'split' });
F.shot('C1b', pre(12, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 600, 601); BH.sun(p, 1650, 560, 60); BH.waves(p, 600, 840, 30, 602, 0.4, 1.2); BH.boat(p, 1380, 720, 0.9); }));
  sh.type(12, { box: TYPE, rows: ['救兵', '就要到', '救兵', '就要到'], color: (r) => (r >= 2 ? 'red' : 'ink'), scale: [0.9, 1, 0.9, 1] });
});
F.shot('C1c', pre(13, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.nightSky(p, 840, 611, [1680, 290, 46]); bigGate(p, [1040, 330, 780, 510], 1430, 320, 'closed', { archY: 540 }); }));
  sh.type(13, { box: TYPE, rows: ['守住啊', '救兵', '就要到'], color: (r) => (r >= 1 ? 'red' : 'ink') });
  sh.push(1.04);
});

// ================= 主歌2：回程、湖口、劝降 =================
F.shot('back', pre(14), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 640, 621));
  sh.el({ depth: 0.4, box: [-60, 420, 2040, 340] }, (o) => BH.mount(o, -60, 2000, 740, 220, 622, 0.6));
  sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => BH.ground(o, 740, 1080, 623));
  sh.el({ box: [1400, 380, 300, 520], depth: 0.9 }, (o) => BH.profile(o, 1540, 880, 0.95, { flip: true })).bob({ amp: 6, period: B / 2 }).to({ x: -900 }, { at: 0, dur: 'shot', ease: 'none' });
}, { transition: 'paper' });

F.shot('seized', pre(15), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 620, 631));
  sh.el({ depth: 0.45, box: [900, 280, 1040, 460] }, (o) => BH.tower(o, 1500, 690, 0.62));
  sh.el({ depth: 0.7, box: [0, 660, 1920, 140] }, (o) => BH.waves(o, 680, 760, 24, 632, 0.4, 1.1));
  sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => { BH.ground(o, 760, 1080, 633); BH.reeds(o, 1200, 1900, 880, 634); });
  sh.el({ box: [1180, 250, 260, 140], depth: 1 }, (o) => BH.text(o.ink, '湖口', 1310, 360, { size: 84 }));
  sh.el({ box: [340, 360, 760, 540], depth: 1 }, (o) => { BH.sentry(o, 520, 880, 1.0); BH.robed(o, 720, 880, 0.95); BH.sentry(o, 920, 880, 1.0, { flip: true }); });
  sh.push(1.08, { fx: 720, fy: 620 });
  sh.kick(at(sh, charT(15, '拿')), 9);
});

F.shot('offer', pre(16), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 640, 641));
  sh.el({ depth: 0.5, box: [-40, 380, 2000, 420] }, (o) => { BH.ground(o, 760, 1080, 642); BH.tents(o, 0, 1920, 760, 1.3, 643); BH.flag(o, 300, 760, 300, '汉', 0); BH.flag(o, 1650, 760, 300, '汉', 1); });
  sh.el({ box: [760, 380, 320, 520], depth: 0.95 }, (o) => BH.robed(o, 920, 880, 1.0));
  sh.el({ box: [1060, 380, 360, 520], depth: 0.95 }, (o) => BH.profile(o, 1220, 880, 1.0, { flip: true, robe: 'red' }));
  sh.el({ box: [180, 180, 520, 170], depth: 1 }, (o) => BH.text(o.red, '富贵', 440, 310, { size: 120, color: P.red, spacing: 20 })).set({ alpha: 0 }, 0).from({ alpha: 0, scale: 1.3 }, { at: at(sh, charT(17, '富')), dur: 0.3 });
  sh.push(1.06, { fx: 1060, fy: 620 });
});

F.shot('nod', pre(18), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 900, 651));
  const head = sh.el({ box: [660, 140, 600, 760], depth: 0.95 }, (o) => BH.profile(o, 960, 1240, 2.4));
  const tn = at(sh, charT(18, '点'));
  head.to({ y: 26, rot: 3 }, { at: tn, dur: 0.25 }).to({ y: 0, rot: 0 }, { at: tn + 0.3, dur: 0.3 });
});

F.shot('march', pre(19), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 460, 661));
  sh.el({ box: [-20, 200, 1960, 600], depth: 0.4 }, (o) => longWall(o, 280, 760, { n: 3, doorW: 180 }));
  sh.el({ depth: 0.8, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 662));
  const grp = sh.el({ box: [-60, 420, 760, 480], depth: 0.95 }, (o) => { BH.sentry(o, 80, 880, 0.9); BH.robed(o, 270, 880, 0.9); BH.sentry(o, 460, 880, 0.9); });
  grp.bob({ amp: 5, period: B }).to({ x: 600 }, { at: 0, dur: 'shot', ease: 'none' });
});

// ================= 导歌2：站到城下，抬头 =================
F.shot('lookup', pre(20), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 220, 671));
  sh.el({ box: [-20, 120, 1960, 800], depth: 0.5 }, (o) => { longWall(o, 200, 900, { n: 2, doorW: 220 }); for (let x = 60; x < 1900; x += 90) BH.sentry(o, x, 200, 0.32); });
  sh.el({ box: [860, 520, 200, 380], depth: 0.95 }, (o) => BH.profile(o, 960, 885, 0.75));
  sh.camSet({ zoom: 1.2, fy: 760 }).camTo({ zoom: 1.0, fy: 540 }, { at: 0.3, dur: L(20).end - L(20).start });
}, { res: 1.22 });

// ================= 副歌2：同一句话，这回是喊出来 =================
F.shot('C2a', pre(21, 0.25), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 420, 681); longWall(p, 420, 840, { x0: 1040, x1: 1820, n: 1, doorW: 1 }); for (const x of [1120, 1260, 1400, 1540, 1680]) BH.sentry(p, x, 400, 0.3); BH.profile(p, 1430, 840, 0.62); }));
  sh.type(21, { box: TYPE, color: 'red' });
}, { transition: 'split' });
F.shot('C2b', pre(22, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 840, 691); ['救', '且', '至'].forEach((ch, i) => BH.text(p.red, ch, 1430, 380 + i * 190, { size: 170, color: P.red })); BH.text(p.ink, '《明史》', 1720, 810, { size: 32, weight: '600' }); }));
  sh.type(22, { box: TYPE, rows: ['救兵', '就要到', '救兵', '就要到'], color: 'red', scale: [0.9, 1, 0.9, 1] });
});
F.shot('C2c', pre(23, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 500, 701); longWall(p, 480, 840, { x0: 1040, x1: 1820, n: 2, doorW: 120 }); for (let x = 1080; x < 1800; x += 60) BH.sentry(p, x, 460, 0.32); BH.flag(p, 1200, 460, 140, '', 0); BH.flag(p, 1660, 460, 140, '', 1); }));
  sh.type(23, { box: TYPE, rows: ['守住啊', '救兵', '就要到'], color: 'red' });
  sh.push(1.04);
});

// ================= 间奏：城里的八十五天（快切四场）=================
const I0 = L(23).end + 0.5, I1 = pre(24), ID = (I1 - I0) / 4;
const caption = (sh, a, b) => sh.el({ box: [940, 210, 680, 200], depth: 1 }, (o) => { const r = [960, 230, 640, 160]; o.knockRect(...r); BH.erase(o.blueT, (c) => c.fillRect(...r)); o.ink.fillStyle = P.paper; o.ink.fillRect(...r); o.ink.fillStyle = P.ink; o.ink.lineWidth = 4; o.ink.strokeRect(...r); BH.text(o.red, a, 1280, 310, { size: 72, color: P.red }); BH.text(o.ink, b, 1280, 366, { size: 34, weight: '600' }); }).set({ alpha: 0 }, 0).from({ alpha: 0, x: 30 }, { at: 0.15, dur: 0.3 });
F.shot('i-fuzhou', I0, (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 520, 711));
  sh.el({ box: [-20, 260, 1960, 640], depth: 0.6 }, (o) => {
    longWall(o, 320, 880, { n: 3, doorW: 1 });
    const gap = (c) => { c.beginPath(); c.moveTo(620, 280); c.lineTo(700, 520); c.lineTo(820, 470); c.lineTo(900, 880); c.lineTo(1260, 880); c.lineTo(1300, 560); c.lineTo(1380, 600); c.lineTo(1420, 280); c.fill(); };
    BH.erase(o.ink, gap); BH.erase(o.blueT, gap); BH.erase(o.mask, gap);
    for (let i = 0; i < 12; i++) { const x = 900 + i * 30; o.knockRect(x - 7, 600, 14, 280); o.ink.fillRect(x - 7, 600, 14, 280); } o.ink.fillRect(890, 640, 370, 10); o.ink.fillRect(890, 800, 370, 10);
  });
  const sm = [0, 1].map((ph) => sh.el({ box: [800, 300, 520, 400], depth: 0.8 }, (o) => { BH.smoke(o, 1060, 600, 1.0, 712, ph); }));
  sh.cycle(sm, { period: B / 2 });
  caption(sh, '抚州门', '城坏二十余丈 且战且筑');
  sh.push(1.06, { fy: 600 });
}, { transition: 'paper' });
F.shot('i-xincheng', I0 + ID, (sh) => {
  sh.el({ depth: 0.2 }, (o) => BH.sky(o, 120, 900, 721));
  sh.el({ box: [-20, 140, 1960, 780], depth: 0.6 }, (o) => { BH.archWall(o, [-20, 140, 1960, 760], [960, 470, 460]); BH.doors(o, 960, 400, 900, 460); });
  sh.el({ box: [0, 880, 1920, 200], depth: 0.9 }, (o) => BH.ground(o, 900, 1080, 722));
  [[960, 0.9], [860, 0.8], [1060, 0.8]].forEach(([x, s], i) => sh.el({ box: [x - 140, 420, 280, 480], depth: 1 }, (o) => BH.sentry(o, x, 890, s)).from({ scale: 0.55, y: -80, alpha: 0 }, { at: 0.1 + i * 0.2, dur: 1.0 }).bob({ amp: 6, period: B / 2, phase: i }));
  caption(sh, '新城门', '薛显开门突击');
});
F.shot('i-shuiguan', I0 + ID * 2, (sh) => {
  sh.el({ box: [-20, 150, 1960, 640], depth: 0.5 }, (o) => waterGate(o, 1180, 760, 560));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => BH.waves(o, 760, 1080, 40, 22, 0.4, 1.2, ph)));
  sh.cycle(w, { period: B / 2 });
  const sp = [0, 1, 2].map((ph) => sh.el({ box: [520, 260, 1000, 580], depth: 0.85 }, (o) => { for (let i = 0; i < 3; i++) spear(o, 1060 + i * 90, 560 + i * 30, 780 - i * 40, 640 + i * 40, true); BH.fire(o, 760, 660, 70, 90 + ph * 10, ph, 31); }));
  sh.cycle(sp, { period: B / 3 });
  caption(sh, '水关', '铁戟铁钩 烧红了再刺');
});
F.shot('i-gongbu', I0 + ID * 3, (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 640, 731));
  sh.el({ box: [720, 300, 1200, 600], depth: 0.6 }, (o) => BH.city(o, 1320, 880, 1000, 1.25));
  sh.el({ box: [1000, 340, 200, 300], depth: 0.6 }, (o) => BH.sentry(o, 1080, 600, 0.55, { flip: true }));
  const ar = sh.el({ box: [80, 420, 420, 80], depth: 0.8 }, (o) => { const k = o.ink; k.lineWidth = 5; k.beginPath(); k.moveTo(100, 470); k.lineTo(470, 450); k.stroke(); o.red.beginPath(); o.red.moveTo(490, 449); o.red.lineTo(460, 438); o.red.lineTo(462, 462); o.red.fill(); });
  ar.to({ x: 560, y: 90 }, { at: 0.2, dur: 1.0, ease: 'power1.in' });
  sh.kick(1.2, 10);
  sh.el({ box: [80, 170, 700, 170], depth: 1 }, (o) => { BH.text(o.red, '宫步门', 420, 260, { size: 72, color: P.red }); BH.text(o.ink, '赵德胜中弩 箭深入六寸', 420, 316, { size: 34, weight: '600' }); }).set({ alpha: 0 }, 0).from({ alpha: 0 }, { at: 0.15, dur: 0.3 });
});

// ================= 主歌3：城下喊话 =================
F.shot('shout', pre(24), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 520, 741));
  sh.el({ box: [-20, 140, 1960, 600], depth: 0.4 }, (o) => longWall(o, 200, 700, { n: 2, doorW: 200 }));
  sh.el({ depth: 0.8, box: [0, 700, 1920, 380] }, (o) => BH.ground(o, 720, 1080, 742));
  sh.el({ box: [460, 300, 320, 600], depth: 0.95 }, (o) => BH.profile(o, 620, 885, 1.3, { flip: true }));
  ['我', '张', '大', '舍'].forEach((ch, i) => {
    const t = at(sh, charT(24, ['我', '张', '大', '社'][i] === '社' ? '舍' : ['我', '张', '大', '舍'][i], i === 0 ? 1 : 0));
    const e = sh.el({ box: [870, 160 + i * 170, 260, 200], depth: 1 }, (o) => { BH.erase(o.blueT, (c) => c.fillRect(890, 180 + i * 170, 220, 170)); BH.text(o.red, ch, 1000, 330 + i * 170, { size: 160, color: P.red }); });
    e.set({ alpha: 0 }, 0).set({ alpha: 1 }, t).from({ scale: 1.4 }, { at: t, dur: 0.22, ease: 'back.out(2.2)' });
    sh.kick(t, 8);
  });
  sh.el({ box: [1460, 760, 420, 80], depth: 1 }, (o) => BH.text(o.ink, '《明史》', 1680, 820, { size: 40, weight: '600' })).set({ alpha: 0 }, 0).from({ alpha: 0 }, { at: 0.6, dur: 0.4 });
}, { transition: 'wipe' });

F.shot('hold', pre(25), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 600, 751));
  sh.el({ box: [-20, 380, 1960, 520], depth: 0.5 }, (o) => longWall(o, 520, 900, { n: 3, doorW: 140 }));
  const row = sh.el({ box: [-20, 200, 1960, 340], depth: 0.7 }, (o) => { for (let x = 40; x < 1900; x += 70) BH.sentry(o, x, 515, 0.5); BH.flag(o, 400, 515, 260, '', 0); BH.flag(o, 1500, 515, 260, '', 1); });
  row.from({ y: 30 }, { at: at(sh, charT(25, '守')), dur: 0.5 });
  sh.kick(at(sh, charT(25, '牢')), 8);
  sh.push(1.06, { fy: 500 });
});

F.shot('spears', pre(26), (sh) => {
  sh.el({ depth: 0.1 }, (o) => BH.sky(o, 0, 640, 761));
  sh.el({ box: [-20, 140, 1960, 640], depth: 0.4 }, (o) => longWall(o, 230, 760, { n: 3, doorW: 180 }));
  sh.el({ depth: 0.8, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 762));
  const fall = sh.el({ box: [200, 160, 1520, 740], depth: 0.95 }, (o) => { for (let i = 0; i < 9; i++) spear(o, 260 + i * 170, 180, 900 + (i - 4) * 18, 800 - Math.abs(i - 4) * 14); });
  const tDrop = at(sh, charT(26, '落'));
  fall.set({ alpha: 0 }, 0).from({ y: -420, alpha: 0 }, { at: tDrop - 0.5, dur: 0.5, ease: 'power3.in' });
  F.shake(sh.t0 + tDrop, 16, 0.6); sh.kick(tDrop, 14);
});

F.shot('delivered', pre(27), (sh) => {
  sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 700, 771); BH.sun(o, 1500, 560, 120); });
  sh.el({ box: [-20, 280, 1960, 520], depth: 0.5 }, (o) => longWall(o, 360, 760, { n: 3, doorW: 160 }));
  sh.el({ depth: 0.8, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 772));
  sh.el({ box: [800, 820, 320, 70], depth: 0.9 }, (o) => BH.shadow(o, 960, 860, 140, 18, 0.55));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.12, fy: 600 }, { dur: 'shot' });
}, { res: 1.14 });

// ================= 桥段：后来 =================
F.shot('temple', pre(28), (sh) => {
  sh.el({ depth: 0.15 }, (o) => BH.sky(o, 0, 760, 781));
  sh.el({ box: [420, 220, 1080, 680], depth: 0.7 }, (o) => temple(o, 960, 880, 820, '忠臣庙'));
  sh.el({ box: [0, 860, 1920, 220], depth: 0.9 }, (o) => BH.ground(o, 880, 1080, 782));
  sh.el({ box: [1500, 170, 380, 150], depth: 1 }, (o) => BH.text(o.ink, '南昌', 1690, 280, { size: 80 }));
  sh.push(1.06, { fy: 560 });
}, { transition: 'paper' });
F.shot('statues', pre(29), (sh) => {
  sh.el({ depth: 0.2 }, (o) => { o.blueT.fillStyle = BH.tone(0.55); o.blueT.fillRect(0, 0, 1920, 900); o.knockRect(0, 0, 1920, 900); });
  sh.el({ box: [60, 420, 1800, 480], depth: 0.8 }, (o) => statues(o, 100, 1820, 860, 14, 8));
  const hl = sh.el({ box: [890, 230, 260, 200], depth: 1 }, (o) => { BH.text(o.red, '第八', 1021, 370, { size: 100, color: P.red }); });
  hl.set({ alpha: 0 }, 0).from({ alpha: 0, scale: 1.4 }, { at: at(sh, charT(29, '第')), dur: 0.3 });
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.25, fx: 1021, fy: 640 }, { at: at(sh, charT(29, '我')), dur: 1.6 });
}, { res: 1.26 });
F.shot('book30', pre(30), (sh) => {
  sh.el({ box: [300, 130, 1320, 760] }, (o) => BH.bookPage(o, {
    center: '明史卷一百三十三', seal: '忠节',
    cols: [{ text: '张子明者' }, { text: '至城下大呼' }, { text: '救且至', size: 140, color: 'red' }, { text: '追封忠节侯', size: 104 }],
    pic: (p, r) => { BH.sky(p, r[1], 620, 791); temple(p, r[0] + r[2] / 2, r[1] + r[3] - 30, 300, '忠臣庙'); },
  }));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.1, fy: 500 }, { at: 0.4, dur: 3.0 });
  sh.kick(at(sh, charT(30, '忠')), 9);
}, { res: 1.14 });

// ================= 最后的副歌：朱色大字 =================
F.shot('F1', pre(31, 0.25), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => tally(p, [1080, 240, 700, 560])));
  sh.type(31, { box: TYPE, rows: ['守住了', '守了', '八十五天'], color: 'red', scale: [0.8, 0.8, 1] });
}, { transition: 'split' });
F.shot('F2', pre(32, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 560, 801); for (let i = 0; i < 4; i++) BH.tower(p, 1100 + i * 190, 600 + i * 50, 0.18 + i * 0.05, { phase: i % 2 }); BH.waves(p, 600, 840, 26, 802, 0.4, 1.2); }));
  sh.type(32, { box: TYPE, rows: ['七月', '救兵到了', '我没有', '看到'], color: (r) => (r >= 2 ? 'red' : 'ink') });
});
F.shot('F3', pre(33, 0.2), (sh) => {
  sh.el({ box: FBOX, depth: 0.5 }, (o) => BH.frame(o, FRAME, (p) => { BH.sky(p, 200, 700, 811); BH.archWall(p, [1040, 200, 780, 640], [1430, 470, 420]); BH.ground(p, 700, 840, 812); }));
  sh.type(33, { box: TYPE, rows: ['我喊过的', '那一句', '救兵', '就要到'], color: 'red', scale: [0.8, 0.8, 1, 1] });
  sh.push(1.05);
});

// ================= 尾奏 =================
F.shot('dawn', L(33).end + 0.4, (sh) => {
  sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 620, 821); BH.sun(o, 1500, 520, 130); });
  sh.el({ box: [-20, 300, 1960, 440], depth: 0.5 }, (o) => longWall(o, 400, 700, { names: ['抚州', '宫步', '士步', '桥步', '章江', '新城', '琉璃', '澹台'], nameSize: 26, doorW: 96, open: [0, 1, 2, 3, 4, 5, 6, 7] }));
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.85, box: [0, 680, 1920, 400] }, (o) => BH.waves(o, 700, 1080, 30, 822, 0.3, 1.2, ph)));
  sh.cycle(w, { period: B });
  sh.push(1.05, { fy: 560 });
}, { transition: 'paper' });

F.shot('card', S.snap(153.0), (sh) => {
  sh.el({ box: [240, 170, 1440, 700] }, (o) => BH.card(o, {
    ep: F.vars.epNo, series: F.vars.series, title: '洪都守了八十五天', kind: 'timeline', src: '据《明史》《明史纪事本末》',
    items: [{ a: '四月', b: '号称六十万' }, { a: '五月', b: '薛显开门突击' }, { a: '六月', b: '水关烧红铁钩' }, { a: '七月', b: '援军到 围解' }],
  }));
  sh.push(1.03);
}, { transition: 'paper' });

F.shot('quiet', S.snap(163.0), (sh) => {
  sh.el({ box: [-20, 0, 1960, 760], depth: 0.4 }, (o) => { BH.nightSky(o, 760, 831, [480, 210, 56]); waterGate(o, 1250, 740, 520, { top: 320 }); });
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.9, box: [0, 720, 1920, 360] }, (o) => { o.blueT.fillStyle = BH.tone(0.45); o.blueT.fillRect(0, 740, 1920, 340); BH.waves(o, 740, 1080, 34, 832, 0.3, 1.2, ph); }));
  sh.cycle(w, { period: B });
  sh.el({ box: [180, 640, 440, 240], depth: 1 }, (o) => { BH.boat(o, 400, 860, 0.9); BH.lantern(o, 330, 770, 0.4, true); }).bob({ amp: 3, period: B * 2 }).drift({ x: 320 });
  sh.push(1.06, { fy: 600 });
}, { transition: 'paper' });

// ================= 片尾卡 =================
F.shot('end', S.duration - 3.2, (sh) => {
  sh.el({ box: [240, 180, 1440, 680] }, (o) => BH.endCard(o, { question: '洪都守住了，头功给谁？', options: ['朱文正', '邓愈', '张子明'], next: `下一集 · ${F.vars.nextTitle || '康郎山下 两支船队'}` }));
}, { transition: 'cut', subs: false });

F.finish();
