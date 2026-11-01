// 版画场景库：天、山、水、地、人、马、船、城、旗、火……全部印在三块版上（o.ink / o.red / o.blue，网点版 o.inkT / o.redT / o.blueT）。
// 用法：在 sh.el({...}, o => BH.horse(o, 960, 860, 1.6)) 里调用。坐标是屏幕坐标（1920×1080）。
// 人物、马、船、器物的 (x, y) 一律是“水平中心、着地线”；s 是缩放。o.knock(path) 把轮廓写进遮挡层（挡住后面的元素）。
(function () {
  const PAL = BH.PAL, S = BH.S, INK = PAL.ink, RED = PAL.red, PAPER = PAL.paper;
  const tone = (a) => `rgba(0,0,0,${a})`;
  const fill = (c, path, x, y, s, flip, color) => BH.at(c, x, y, s, (k) => { if (color) k.fillStyle = color; k.fill(path); }, flip);
  const line = (c, path, x, y, s, flip, w) => BH.at(c, x, y, s, (k) => { k.lineWidth = w / s; k.lineJoin = 'round'; k.stroke(path); }, flip);
  const knock = (o, path, x, y, s, flip) => BH.at(o.mask, x, y, s, (k) => k.fill(path), flip);
  const carve = (c, x, y, s, flip, fn) => BH.at(c, x, y, s, (k) => { k.save(); k.globalCompositeOperation = 'destination-out'; k.strokeStyle = '#000'; k.fillStyle = '#000'; k.lineCap = 'round'; fn(k); k.restore(); }, flip);
  const erase = (c, fn) => { c.save(); c.globalCompositeOperation = 'destination-out'; c.fillStyle = c.strokeStyle = '#000'; fn(c); c.restore(); };
  const curve = (k, w, ...p) => { k.lineWidth = w; k.beginPath(); k.moveTo(p[0], p[1]); for (let i = 2; i < p.length; i += 4) k.quadraticCurveTo(p[i], p[i + 1], p[i + 2], p[i + 3]); k.stroke(); };
  BH.carve = carve; BH.erase = erase; BH.fillAt = fill; BH.lineAt = line; BH.knockAt = knock; BH.tone = tone;

  // ---------------- 天、日、月、星 ----------------
  // 木刻天空：横向刻线，越高越密越粗（默认印在靛版）
  BH.sky = (o, y0 = 0, y1 = 620, seed = 1, plate = 'blue') => {
    const r = BH.rng(seed), c = o[plate]; c.save(); c.lineCap = 'round';
    for (let y = y0; y < y1; y += 9) { const t = 1 - (y - y0) / (y1 - y0); c.lineWidth = 0.6 + 4.2 * t * t;
      let x = -40; while (x < 1960) { const len = 60 + r() * 380 * (0.4 + t), gap = 6 + r() * 40 * (1 - t); c.beginPath(); c.moveTo(x, y + (r() - 0.5) * 1.5); c.lineTo(x + len, y + (r() - 0.5) * 1.5); c.stroke(); x += len + gap; } }
    c.restore();
  };
  // 夜空：整片靛色，月亮和星星留白（月亮单独做元素时用 BH.moon）
  BH.nightSky = (o, y1 = 1080, seed = 5, moon = null) => {
    o.blue.fillRect(-20, -20, 1960, y1 + 20); const r = BH.rng(seed);
    erase(o.blue, (c) => { if (moon) { c.beginPath(); c.arc(moon[0], moon[1], moon[2], 0, 7); c.fill(); }
      for (let i = 0; i < 200; i++) { c.beginPath(); c.arc(r() * 1920, r() * Math.min(y1, 560), r() * 2 + 0.4, 0, 7); c.fill(); }
      c.lineCap = 'round'; for (let y = 20; y < Math.min(y1, 600); y += 14) { c.lineWidth = 1.3; let x = 0; while (x < 1920) { const len = 80 + r() * 300; if (r() < 0.45) { c.beginPath(); c.moveTo(x, y); c.lineTo(x + len, y); c.stroke(); } x += len + 30; } } });
  };
  BH.sun = (o, x, y, r) => { o.red.beginPath(); o.red.arc(x, y, r, 0, 7); o.red.fill(); o.knock(circle(x, y, r)); };
  BH.moon = (o, x, y, r) => { o.knock(circle(x, y, r)); o.ink.lineWidth = 1.5; o.ink.globalAlpha = 0.35; o.ink.beginPath(); o.ink.arc(x, y, r, 0, 7); o.ink.stroke(); o.ink.globalAlpha = 1; };
  const circle = (x, y, r) => { const p = new Path2D(); p.arc(x, y, r, 0, 7); return p; };
  BH.circle = circle;

  // ---------------- 山、水、地 ----------------
  BH.mount = (o, x0, x1, base, peak, seed, dens = 0.75) => {
    const pts = BH.ridge(x0, x1, base, peak, seed, 1.2), p = BH.ridgePath(pts, base);
    const g = o.blueT.createLinearGradient(0, base - peak, 0, base); g.addColorStop(0, tone(dens)); g.addColorStop(1, tone(dens * 0.15));
    o.blueT.fillStyle = g; o.blueT.fill(p); o.knock(p);
    const k = o.ink; k.save(); k.clip(p); k.lineWidth = 1.8; const r = BH.rng(seed);
    for (let i = 1; i < 9; i++) { k.setLineDash([20 + r() * 60, 8 + r() * 20]); BH.polyline(k, pts.map((q) => [q[0], q[1] + i * 16 + i * i * 2])); k.stroke(); }
    k.restore(); k.lineWidth = 4; BH.polyline(k, pts); k.stroke(); return pts;
  };
  // 青海波水纹（近大远小）；phase 0/1/2 做成几张交替，水就动起来
  BH.waves = (o, top, bottom, r0 = 34, seed = 2, dens = 0.32, persp = 1.2, phase = 0) => {
    o.blueT.fillStyle = tone(dens); o.blueT.fillRect(-20, top, 1960, bottom - top); o.knockRect(-20, top, 1960, bottom - top);
    const k = o.ink, rr = BH.rng(seed); let r = r0 * 0.5;
    for (let row = 0, y = top; y < bottom + r; row++, y += r * 0.55, r = r0 * (0.5 + persp * Math.min(1, (y - top) / Math.max(1, bottom - top)))) {
      const shift = phase * r * 0.66;
      for (let x = (row % 2) * r - r - rr() * r + shift - 2 * r; x < 1920 + r; x += r * 2) {
        const yy = y + (rr() - 0.5) * 2;
        k.save(); k.globalCompositeOperation = 'destination-out'; k.beginPath(); k.arc(x, yy, r, Math.PI, 0); k.lineTo(x + r, yy + r); k.lineTo(x - r, yy + r); k.fill(); k.restore();
        k.lineWidth = Math.max(1.6, r / 12); for (const f of [1, 0.72, 0.46]) { k.beginPath(); k.arc(x, yy, r * f - 2, Math.PI, 0); k.stroke(); }
      }
    }
  };
  BH.crests = (o, y, seed = 3, step = 210, size = 46, phase = 0) => {
    const k = o.ink, r = BH.rng(seed);
    for (let x = -40 + phase * 24; x < 1980; x += step * (0.8 + r() * 0.4)) {
      const s = size * (0.8 + r() * 0.5), yy = y + (r() - 0.5) * 30;
      k.save(); k.globalCompositeOperation = 'destination-out'; k.beginPath(); k.ellipse(x, yy + s * 0.2, s * 1.3, s * 0.9, 0, 0, 7); k.fill(); k.restore();
      k.lineWidth = 4; k.beginPath();
      for (let a = 0; a < Math.PI * 3.2; a += 0.12) { const rad = s * (1 - a / (Math.PI * 3.6)), px = x + Math.cos(a + Math.PI) * rad, py = yy + Math.sin(a + Math.PI) * rad * 0.8; a ? k.lineTo(px, py) : k.moveTo(px, py); }
      k.stroke(); for (let i = 0; i < 5; i++) { k.beginPath(); k.arc(x + s * 1.2 + i * 10, yy - s * 0.5 - i * 6, 3 + r() * 3, 0, 7); k.fill(); }
    }
  };
  BH.ground = (o, y0, y1 = 1080, seed = 4) => {
    const k = o.ink, r = BH.rng(seed); o.knockRect(-20, y0, 1960, y1 - y0); k.save(); k.lineCap = 'round';
    for (let y = y0 + 6; y < y1; y += 7) { const t = (y - y0) / (y1 - y0); k.lineWidth = 1 + 3 * t;
      let x = r() * 40 - 20; while (x < 1940) { const len = 10 + r() * 50 * (0.3 + t); if (r() < 0.25 + 0.6 * t) { k.beginPath(); k.moveTo(x, y); k.lineTo(x + len, y); k.stroke(); } x += len + 8 + r() * 30 * (1 - t); } }
    k.restore(); k.fillRect(-20, y0, 1960, 5);
  };
  BH.hill = (o, d, seed = 6) => { const p = new Path2D(d); o.knock(p); o.ink.lineWidth = 5; o.ink.stroke(p); const k = o.ink; k.save(); k.clip(p); const r = BH.rng(seed);
    k.lineCap = 'round'; for (let y = 0; y < 1080; y += 8) { k.lineWidth = 1.2 + y / 500; let x = r() * 40; while (x < 1920) { const len = 10 + r() * 40; if (r() < 0.35) { k.beginPath(); k.moveTo(x, y); k.lineTo(x + len, y); k.stroke(); } x += len + 14 + r() * 30; } } k.restore(); return p; };
  BH.shadow = (o, x, y, rx, ry = 24, a = 0.45) => { o.blueT.fillStyle = tone(a); o.blueT.beginPath(); o.blueT.ellipse(x, y, rx, ry, 0, 0, 7); o.blueT.fill(); };

  // ---------------- 人、马 ----------------
  // 马与骑者（朝右；flip 朝左）。phase 0/1：远侧两条腿前后交替，配合 el.bob 就是走。(x, y) = 中心、蹄子着地线
  BH.horse = (o, x, y, s = 1, opt = {}) => {
    const h = S.horse(), R = h.rider, flip = !!opt.flip, X = x - (flip ? -220 : 220) * s, Y = y - 300 * s, ph = opt.phase || 0;
    const far = new Path2D(); const m1 = new DOMMatrix().translate(272, 196).rotate(ph ? -12 : 10).translate(-272, -196), m2 = new DOMMatrix().translate(130, 198).rotate(ph ? 12 : -10).translate(-130, -198);
    far.addPath(new Path2D('M262 196 C270 230 284 255 290 292 L290 300 L310 300 L307 288 C300 262 293 230 286 194 Z'), m1);
    far.addPath(new Path2D('M122 196 C112 230 116 260 120 292 L118 300 L140 300 L137 290 C134 262 132 230 142 200 Z'), m2);
    const parts = [far, h.tail, h.body]; if (opt.rider !== false) parts.push(R.cape, R.skirt, R.torso, R.arm, R.leg, R.head, R.hat);
    for (const p of parts) knock(o, p, X, Y, s, flip);
    fill(o.blue, far, X, Y, s, flip); fill(o.ink, far, X, Y, s, flip); fill(o.ink, h.tail, X, Y, s, flip); fill(o.ink, h.body, X, Y, s, flip);
    if (opt.rider !== false) {
      fill(o.red, R.cape, X, Y, s, flip); line(o.ink, R.cape, X, Y, s, flip, 3);
      for (const k of ['skirt', 'torso', 'arm', 'leg', 'head', 'hat']) fill(o.ink, R[k], X, Y, s, flip);
      fill(o[opt.robe || 'red'], R.torso, X, Y, s, flip); fill(o[opt.robe || 'red'], R.skirt, X, Y, s, flip);
    }
    carve(o.ink, X, Y, s, flip, (k) => {
      curve(k, 3, 300, 64, 290, 110, 296, 150); curve(k, 3, 286, 76, 270, 120, 274, 170); curve(k, 3, 104, 118, 92, 150, 110, 186); curve(k, 3, 128, 124, 118, 160, 132, 192);
      curve(k, 2.5, 150, 112, 190, 108, 236, 112); curve(k, 2.5, 160, 182, 200, 192, 232, 186); curve(k, 2.5, 262, 214, 262, 250, 262, 288); curve(k, 2.5, 94, 206, 92, 250, 94, 288);
      curve(k, 2, 320, 46, 306, 60, 296, 72); curve(k, 2, 326, 52, 312, 68, 300, 82); curve(k, 2, 46, 150, 44, 190, 46, 230); curve(k, 2, 58, 140, 54, 180, 56, 214);
      k.beginPath(); k.arc(h.eye[0], h.eye[1], 4.5, 0, 7); k.fill();
      if (opt.rider !== false) { curve(k, 2.5, 214, 40, 222, 70, 216, 92); curve(k, 2, 200, 100, 212, 130, 222, 160); }
    });
    if (opt.rider !== false) BH.at(o.ink, X, Y, s, (k) => { k.lineWidth = 2 / s; k.beginPath(); k.moveTo(282, 72); k.lineTo(372, 92); k.stroke(); }, flip);
  };
  // 长衫人（正面）。(x, y) = 中心、脚底
  BH.robed = (o, x, y, s = 1, opt = {}) => {
    const f = S.robed(), X = x - 70 * s, Y = y - 420 * s;
    for (const p of [f.robe, f.hat, f.head]) { knock(o, p, X, Y, s); fill(o.ink, p, X, Y, s); }
    if (opt.robe) fill(o[opt.robe], f.robe, X, Y, s);
    carve(o.ink, X, Y, s, false, (k) => {
      for (const [a, b, c, d] of f.collar) { k.lineWidth = 4; k.beginPath(); k.moveTo(a, b); k.lineTo(c, d); k.stroke(); }
      k.lineWidth = 3; k.beginPath(); k.moveTo(30, f.belt); k.quadraticCurveTo(70, f.belt + 10, 112, f.belt); k.stroke();
      curve(k, 2.5, 30, 110, 22, 170, 18, 228); curve(k, 2.5, 110, 110, 118, 170, 122, 228); curve(k, 2.5, 52, 260, 46, 330, 38, 410); curve(k, 2.5, 88, 260, 94, 330, 102, 410); curve(k, 2, 70, 256, 70, 330, 70, 412);
      k.lineWidth = 2; k.stroke(f.hands);
    });
  };
  // 侧面长衫人（朝右；flip 朝左）
  BH.profile = (o, x, y, s = 1, opt = {}) => {
    const f = S.profile(), flip = !!opt.flip, X = x - (flip ? -78 : 78) * s, Y = y - 418 * s;
    for (const p of ['robe', 'sleeve', 'head', 'hat', 'beard']) { knock(o, f[p], X, Y, s, flip); fill(o.ink, f[p], X, Y, s, flip); }
    if (opt.robe) { fill(o[opt.robe], f.robe, X, Y, s, flip); fill(o[opt.robe], f.sleeve, X, Y, s, flip); }
    carve(o.ink, X, Y, s, flip, (k) => { curve(k, 2.5, 50, 140, 44, 260, 36, 410); curve(k, 2.5, 84, 150, 90, 270, 100, 410); curve(k, 2, 80, 130, 104, 150, 126, 176); k.beginPath(); k.arc(f.eye[0], f.eye[1], 3, 0, 7); k.fill(); });
  };
  // 蹲坐磨桨的人（朝右）
  BH.grinder = (o, x, y, s = 1, opt = {}) => {
    const g = S.grinder(), X = x - 100 * s, Y = y - 200 * s;
    for (const p of ['oar', 'body', 'head', 'hat']) { knock(o, g[p], X, Y, s); fill(o.ink, g[p], X, Y, s); }
    fill(o.red, g.stone, X, Y, s); line(o.ink, g.stone, X, Y, s, false, 3);
    carve(o.ink, X, Y, s, false, (c) => { curve(c, 2.5, 50, 90, 44, 130, 56, 180); curve(c, 2.5, 70, 80, 64, 130, 78, 176); c.lineWidth = 2; c.beginPath(); c.moveTo(-40, 180); c.lineTo(290, 102); c.stroke(); });
    if (opt.sparks !== false) { const r = BH.rng(opt.seed || 9); for (let i = 0; i < 9; i++) { o.red.beginPath(); o.red.arc(X + s * (170 + i * 9), Y + s * (92 - i * 7 - r() * 10), (3 + r() * 3) * s, 0, 7); o.red.fill(); } }
  };
  // 躺倒的老将 + 断旗（flagChar 旗上的字，留空不写）
  BH.fallen = (o, x, y, s = 1, flagChar = '') => {
    const f = S.fallen(), X = x - 190 * s, Y = y;
    BH.at(o.ink, X, Y, s, (c) => { c.lineWidth = 9 / s; c.beginPath(); c.moveTo(140, 4); c.lineTo(290, -140); c.stroke(); c.beginPath(); c.moveTo(300, -150); c.lineTo(430, -300); c.stroke(); });
    knock(o, f.flag, X, Y, s); fill(o.red, f.flag, X, Y, s); line(o.ink, f.flag, X, Y, s, false, 4);
    if (flagChar) BH.at(o.ink, X, Y, s, (c) => BH.text(c, flagChar, f.flagChar[0], f.flagChar[1] + 30, { size: 84 }));
    for (const p of ['legs', 'body', 'arm', 'helmet']) { knock(o, f[p], X, Y, s); fill(o.ink, f[p], X, Y, s); }
    carve(o.ink, X, Y, s, false, (c) => { c.lineWidth = 2.5; for (const px of f.plates) { c.beginPath(); c.moveTo(px, -54); c.quadraticCurveTo(px + 8, -30, px, -6); c.stroke(); } c.beginPath(); c.moveTo(60, -30); c.lineTo(250, -28); c.stroke(); });
  };
  // 持枪守城的人（朝右）
  BH.sentry = (o, x, y, s = 1, opt = {}) => {
    const st = S.sentry(), flip = !!opt.flip, X = x - (flip ? -50 : 50) * s;
    for (const p of ['spear', 'body', 'head', 'helmet']) { knock(o, st[p], X, y, s, flip); fill(o.ink, st[p], X, y, s, flip); }
    fill(o.red, st.tassel, X, y, s, flip);
  };
  // 一排人（远景剪影：头、肩、枪），用来表示军队、人群
  BH.crowd = (o, x0, x1, y, s = 1, seed = 3, opt = {}) => {
    const r = BH.rng(seed), k = o.ink, p = new Path2D();
    for (let x = x0; x < x1; x += (18 + r() * 14) * s) {
      const h = (60 + r() * 20) * s, hx = x + (r() - 0.5) * 6 * s;
      p.moveTo(hx + 9 * s, y - h); p.arc(hx, y - h, 9 * s, 0, 7);
      p.moveTo(hx - 14 * s, y); p.quadraticCurveTo(hx - 15 * s, y - h + 12 * s, hx, y - h + 10 * s); p.quadraticCurveTo(hx + 15 * s, y - h + 12 * s, hx + 14 * s, y); p.closePath();
      if (opt.spears !== false && r() < 0.6) { p.moveTo(hx + 8 * s, y - h * 0.5); p.lineTo(hx + 12 * s, y - h - 70 * s); p.lineTo(hx + 15 * s, y - h - 70 * s); p.lineTo(hx + 11 * s, y - h * 0.5); p.closePath(); }
    }
    o.knock(p); k.fill(p);
    if (opt.flags) for (let i = 0; i < opt.flags; i++) { const fx = x0 + (x1 - x0) * (i + 0.5) / opt.flags; BH.flag(o, fx, y - 70 * s, 160 * s, opt.flagChar || '', i % 2); }
  };

  // ---------------- 旗、营帐、鸟、箭、松、芦苇 ----------------
  // 旗：(x, y) 旗杆底，h 杆高；phase 0/1 两张交替就是飘
  BH.flag = (o, x, y, h, ch = '', phase = 0, opt = {}) => {
    const k = o.ink, w = opt.w || h * 0.42, top = y - h, wv = phase ? 1 : -1;
    k.fillRect(x - 3, top, 6, h); o.knockRect(x - 3, top, 6, h);
    const p = new Path2D(); p.moveTo(x + 3, top); p.quadraticCurveTo(x + w * 0.5, top + wv * 10, x + w, top + 4); p.quadraticCurveTo(x + w * 0.95, top + w * 0.5, x + w * 1.02, top + w * 0.86);
    p.quadraticCurveTo(x + w * 0.5, top + w * 0.86 - wv * 12, x + 3, top + w * 0.8); p.closePath();
    o.knock(p); o[opt.plate || 'red'].fill(p); k.lineWidth = 3; k.stroke(p);
    if (ch) BH.text(k, ch, x + w * 0.5, top + w * 0.62, { size: w * 0.5 });
  };
  BH.tents = (o, x0, x1, y, s = 1, seed = 5) => { const r = BH.rng(seed), k = o.ink;
    for (let x = x0; x < x1; x += (110 + r() * 60) * s) { const w = (80 + r() * 30) * s, h = w * 0.7, p = new Path2D(); p.moveTo(x - w / 2, y); p.lineTo(x, y - h); p.lineTo(x + w / 2, y); p.closePath();
      o.knock(p); k.lineWidth = 3; k.stroke(p); BH.hatch(k, p, { angle: 70, gap: 7, width: 1.5, rect: [x - w, y - h, w * 2, h] }); k.fillRect(x - 2, y - h - 30 * s, 4, 30 * s); o.red.beginPath(); o.red.moveTo(x + 2, y - h - 30 * s); o.red.lineTo(x + 26 * s, y - h - 24 * s); o.red.lineTo(x + 2, y - h - 16 * s); o.red.fill(); } };
  BH.birds = (o, rect, n = 7, seed = 8) => { const [x0, y0, w, h] = rect, r = BH.rng(seed), k = o.ink; k.lineWidth = 4; k.lineCap = 'round';
    for (let i = 0; i < n; i++) { const bx = x0 + r() * w, by = y0 + r() * h, s = 0.7 + r() * 0.6; k.beginPath(); k.moveTo(bx - 18 * s, by - 6 * s); k.quadraticCurveTo(bx - 6 * s, by - 10 * s, bx, by); k.quadraticCurveTo(bx + 6 * s, by - 10 * s, bx + 18 * s, by - 6 * s); k.stroke(); } };
  BH.arrows = (o, rect, n = 12, seed = 9) => { const [x0, y0, w, h] = rect, r = BH.rng(seed), k = o.ink;
    for (let i = 0; i < n; i++) { const ax = x0 + r() * w, ay = y0 + r() * h; k.lineWidth = 3; k.beginPath(); k.moveTo(ax, ay); k.lineTo(ax - 30 - r() * 20, ay - 70); k.stroke(); k.beginPath(); k.moveTo(ax - 36, ay - 70); k.lineTo(ax - 24, ay - 88); k.lineTo(ax - 20, ay - 64); k.fill(); } };
  BH.pine = (o, x, y, h, seed = 3) => { const r = BH.rng(seed), k = o.ink, trunk = new Path2D();
    trunk.moveTo(x - h * 0.03, y); trunk.bezierCurveTo(x, y - h * 0.5, x + h * 0.08, y - h * 0.7, x + h * 0.02, y - h); trunk.lineTo(x + h * 0.06, y - h); trunk.bezierCurveTo(x + h * 0.12, y - h * 0.7, x + h * 0.05, y - h * 0.5, x + h * 0.04, y); trunk.closePath();
    o.knock(trunk); k.fill(trunk);
    for (let i = 0; i < 5; i++) { const cy = y - h * (0.42 + i * 0.13), cx = x + (i % 2 ? 1 : -1) * h * 0.13, w = h * (0.32 - i * 0.04), p = new Path2D(); p.ellipse(cx, cy, w, h * 0.065, 0, 0, 7);
      o.knock(p); k.fill(p); carve(k, 0, 0, 1, false, (c) => { c.lineWidth = 2; for (let j = 0; j < 9; j++) { const px = cx - w * 0.8 + (j / 8) * w * 1.6; c.beginPath(); c.moveTo(px, cy + h * 0.03); c.lineTo(px + 8, cy - h * 0.03); c.stroke(); } }); } };
  BH.reeds = (o, x0, x1, y, seed = 4) => { const r = BH.rng(seed), k = o.ink, p = new Path2D();
    for (let i = 0; i < (x1 - x0) / 9; i++) { const x = x0 + r() * (x1 - x0), h = 80 + r() * 160, b = (r() - 0.3) * 40; p.moveTo(x, y); p.quadraticCurveTo(x + b * 0.3, y - h * 0.5, x + b, y - h); p.lineTo(x + b + 5, y - h); p.quadraticCurveTo(x + b * 0.3 + 5, y - h * 0.5, x + 5, y); p.closePath(); }
    o.knock(p); k.fill(p); };

  // ---------------- 火、烟、雨 ----------------
  // 火：朱版火舌 + 墨线勾边；phase 0/1/2 三张交替
  BH.fire = (o, x, y, w, h, phase = 0, seed = 11) => { const r = BH.rng(seed + phase * 101), p = new Path2D(); p.moveTo(x - w / 2, y);
    const n = 7; for (let i = 0; i <= n; i++) { const fx = x - w / 2 + (w * i) / n, fh = h * (0.45 + r() * 0.55) * Math.sin((i / n) * Math.PI) ** 0.5; p.quadraticCurveTo(fx - w / n * 0.5, y - fh * 0.6, fx + (r() - 0.5) * 20, y - fh); p.quadraticCurveTo(fx + w / n * 0.3, y - fh * 0.5, fx + w / n * 0.5, y - fh * 0.2); }
    p.lineTo(x + w / 2, y); p.closePath(); o.knock(p); o.red.fill(p); o.ink.lineWidth = 4; o.ink.stroke(p);
    o.redT.fillStyle = tone(0.6); o.redT.beginPath(); o.redT.ellipse(x, y - h * 0.4, w * 0.9, h * 0.8, 0, 0, 7); o.redT.fill(); };
  BH.smoke = (o, x, y, s = 1, seed = 12, phase = 0) => { const r = BH.rng(seed); for (let i = 0; i < 9; i++) { const px = x + (r() - 0.5) * 120 * s + phase * 10, py = y - i * 50 * s - phase * 14, rr = (40 + i * 10) * s; o.blueT.fillStyle = tone(0.35); o.blueT.beginPath(); o.blueT.arc(px, py, rr, 0, 7); o.blueT.fill(); o.ink.lineWidth = 2; o.ink.beginPath(); o.ink.arc(px, py, rr, Math.PI * 1.1, Math.PI * 1.8); o.ink.stroke(); } };
  BH.rain = (o, rect = [0, 0, 1920, 900], seed = 13, phase = 0) => { const [x0, y0, w, h] = rect, r = BH.rng(seed), k = o.ink; k.lineWidth = 2; k.lineCap = 'round';
    for (let i = 0; i < 260; i++) { const x = x0 + r() * w, y = y0 + ((r() * h + phase * 40) % h); k.beginPath(); k.moveTo(x, y); k.lineTo(x - 10, y + 34); k.stroke(); } };

  // ---------------- 建筑、器物 ----------------
  // 城墙 + 城楼（x 中心，y 墙脚，w 宽）
  BH.city = (o, x, y, w = 900, s = 1) => { const c = S.city(w), X = x - (w / 2) * s;
    for (const p of ['wall', 'teeth', 'tower', 'tower2', 'roof1', 'roof2', 'plat']) knock(o, c[p], X, y, s);
    BH.at(o.ink, X, y, s, (k) => { k.lineWidth = 4 / s; k.stroke(c.wall); BH.hatch(k, c.wall, { angle: 0, gap: 12, width: 1.4, rect: [X, y - 170 * s, w * s, 170 * s] }); k.fill(c.teeth); k.fill(c.arch); k.fill(c.plat); k.fill(c.roof1); k.fill(c.roof2); k.lineWidth = 3 / s; k.stroke(c.tower); k.stroke(c.tower2); for (const cx of c.cols) k.fillRect(cx - 4, -280, 8, 86); });
    fill(o.red, c.tower, X, y, s); fill(o.red, c.tower2, X, y, s);
    BH.at(o.blueT, X, y, s, (k) => { k.fillStyle = tone(0.3); k.fill(c.wall); });
  };
  BH.throne = (o, x, y, s = 1, opt = {}) => { const t = S.throne();
    for (const p of ['back', 'arms', 'base', 'seat']) { knock(o, t[p], x, y, s); fill(o.red, t[p], x, y, s); line(o.ink, t[p], x, y, s, false, 5); }
    knock(o, t.panel, x, y, s); fill(o.ink, t.panel, x, y, s);
    carve(o.ink, x, y, s, false, (c) => { c.lineWidth = 3; for (let i = 0; i < 6; i++) { c.beginPath(); c.arc(0, -225, 20 + i * 14, Math.PI * 1.1, Math.PI * 1.9); c.stroke(); } c.beginPath(); c.arc(0, -225, 12, 0, 7); c.fill(); });
    if (opt.sitter) BH.robed(o, x - 4 * s, y - 130 * s + 4, opt.sitter, { robe: opt.sitterRobe });
  };
  // 楼船（朝右）：x 中心，y 水线
  BH.tower = (o, x, y, s = 1, opt = {}) => { const t = S.tower(), X = x - 460 * s, k = o.ink;
    BH.at(k, X, y, s, (c) => { c.lineWidth = 4 / s; for (let i = 0; i < 22; i++) { const xx = 160 + i * 26; c.beginPath(); c.moveTo(xx, 0); c.lineTo(xx - 50, 80); c.stroke(); } });
    t.boxes.forEach((b, i) => { knock(o, b, X, y, s); fill(o.red, b, X, y, s); line(k, b, X, y, s, false, 4); const [a, bb, bot, top] = t.decks[i];
      BH.at(k, X, y, s, (c) => { for (let xx = a + 30; xx < bb - 20; xx += 46) c.fillRect(xx, top + 18, 24, (bot - top) * 0.45); c.lineWidth = 3 / s; c.beginPath(); c.moveTo(a, bot - 14); c.lineTo(bb, bot - 14); c.stroke(); for (let xx = a; xx < bb; xx += 16) { c.beginPath(); c.moveTo(xx, bot - 14); c.lineTo(xx, bot - 2); c.stroke(); } }); });
    t.roofs.forEach((r) => { knock(o, r, X, y, s); fill(k, r, X, y, s); });
    knock(o, t.hull, X, y, s); fill(k, t.hull, X, y, s);
    carve(k, X, y, s, false, (c) => { c.lineWidth = 2.6; for (let row = 0; row < 4; row++) for (let xx = 60 + (row % 2) * 18; xx < 880; xx += 36) { c.beginPath(); c.arc(xx, -50 + row * 18, 16, 0.1 * Math.PI, 0.9 * Math.PI); c.stroke(); } });
    t.masts.forEach(([mx, y0, y1]) => { BH.at(k, X, y, s, (c) => c.fillRect(mx - 4, y1, 8, y0 - y1)); BH.at(o.red, X, y, s, (c) => { const p = new Path2D(); const w = opt.phase ? -1 : 1; p.moveTo(mx + 4, y1); p.quadraticCurveTo(mx + 60, y1 + 10 * w, mx + 120, y1 - 4); p.lineTo(mx + 110, y1 + 40); p.quadraticCurveTo(mx + 60, y1 + 50 - 8 * w, mx + 4, y1 + 44); c.fill(p); BH.at(o.mask, X, y, s, (m) => m.fill(p)); }); });
  };
  // 小船（篷船）：x 中心，y 水线
  BH.boat = (o, x, y, s = 1, opt = {}) => { const b = S.boat(), X = x - 190 * s; for (const p of [b.hull, b.canopy]) { knock(o, p, X, y, s); fill(o.ink, p, X, y, s); }
    carve(o.ink, X, y, s, false, (c) => { c.lineWidth = 2; for (let i = 0; i < 6; i++) { c.beginPath(); c.moveTo(188 + i * 16, -40); c.quadraticCurveTo(230, -80 + i * 2, 276 - i * 2, -40); c.stroke(); } });
    if (opt.sail) BH.at(o.ink, X, y, s, (k) => { k.fillRect(148, -240, 6, 220); const p = new Path2D('M156 -228 L268 -206 L256 -54 L156 -44 Z'); k.lineWidth = 3 / s; k.stroke(p); BH.at(o.mask, X, y, s, (m) => m.fill(p)); for (let i = 1; i < 6; i++) { k.beginPath(); k.moveTo(156, -228 + i * 30); k.lineTo(266, -206 + i * 26); k.stroke(); } }); };
  // 拱门墙：墙面砖缝刻线，门里是另一个世界（门洞留给后面的元素露出来）
  BH.archWall = (o, rect, door, seed = 33) => { const [x0, y0, w, h] = rect, [dx, dy, dw] = door, k = o.ink, p = new Path2D(); p.rect(x0, y0, w, h);
    const d = new Path2D(); d.moveTo(dx - dw / 2, y0 + h); d.lineTo(dx - dw / 2, dy); d.arc(dx, dy, dw / 2, Math.PI, 0); d.lineTo(dx + dw / 2, y0 + h); d.closePath();
    k.fill(p); erase(k, (c) => c.fill(d)); carve(k, 0, 0, 1, false, (c) => { c.save(); c.clip(p); c.lineWidth = 3; for (let y = y0 + 30; y < y0 + h; y += 60) { c.beginPath(); c.moveTo(x0, y); c.lineTo(x0 + w, y); c.stroke(); for (let x = x0 + ((y / 60) % 2) * 60; x < x0 + w; x += 120) { c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 60); c.stroke(); } } c.restore(); });
    const hole = new Path2D(); hole.rect(x0, y0, w, h); o.mask.save(); o.mask.fill(hole); o.mask.globalCompositeOperation = 'destination-out'; o.mask.fill(d); o.mask.restore(); return d; };
  // 两扇朱门（开着）
  BH.doors = (o, dx, y0, y1, dw) => { const k = o.ink; for (const [x, sgn] of [[dx - dw / 2 - 200, 1], [dx + dw / 2, -1]]) { const p = new Path2D(); p.moveTo(x + (sgn > 0 ? 200 : 0), y0 + 40); p.lineTo(x + (sgn > 0 ? 40 : 160), y0); p.lineTo(x + (sgn > 0 ? 40 : 160), y1 + 40); p.lineTo(x + (sgn > 0 ? 200 : 0), y1); p.closePath();
    o.knock(p); o.red.fill(p); k.lineWidth = 6; k.stroke(p); for (let r = 0; r < 7; r++) for (let c = 0; c < 3; c++) { k.beginPath(); k.arc(x + 70 + c * 40 + (sgn < 0 ? -10 : 10), y0 + 80 + r * 75, 7, 0, 7); k.fill(); } } };
  BH.lantern = (o, x, y, s = 1, glow = true) => { const ln = S.lantern(); if (glow) { const g = o.redT.createRadialGradient(x, y, 10 * s, x, y, 230 * s); g.addColorStop(0, tone(0.85)); g.addColorStop(1, tone(0)); o.redT.fillStyle = g; o.redT.beginPath(); o.redT.arc(x, y, 230 * s, 0, 7); o.redT.fill(); }
    knock(o, ln.body, x, y, s); fill(o.red, ln.body, x, y, s); line(o.ink, ln.body, x, y, s, false, 3); fill(o.ink, ln.caps, x, y, s); };
  // 窗（格子）：rect 内留白，给后面的元素露出来
  BH.windowFrame = (o, rect, cols = 4, rows = 2, w = 14) => { const [x, y, ww, hh] = rect, k = o.ink; k.lineWidth = w; k.strokeRect(x, y, ww, hh); k.lineWidth = w * 0.6;
    for (let i = 1; i < cols; i++) { k.beginPath(); k.moveTo(x + (ww * i) / cols, y); k.lineTo(x + (ww * i) / cols, y + hh); k.stroke(); } for (let j = 1; j < rows; j++) { k.beginPath(); k.moveTo(x, y + (hh * j) / rows); k.lineTo(x + ww, y + (hh * j) / rows); k.stroke(); } };

  // ---------------- 文字类：刻本页、标题、框、知识卡、片尾卡 ----------------
  // 明刻本书页：版框、界行、版心鱼尾；cols 从右往左 [{text, size, color:'ink'|'red'}]；pic(o, rect) 左半页插图
  BH.bookPage = (o, spec) => { const { x0 = 330, x1 = 1590, y0 = 150, y1 = 862, center = '', cols = [], pic = null, seal = '' } = spec, k = o.ink, cx = (x0 + x1) / 2;
    const page = new Path2D(); page.rect(x0, y0, x1 - x0, y1 - y0); o.knock(page);
    k.lineWidth = 9; k.strokeRect(x0, y0, x1 - x0, y1 - y0); k.lineWidth = 2.5; k.strokeRect(x0 + 14, y0 + 14, x1 - x0 - 28, y1 - y0 - 28);
    k.beginPath(); k.moveTo(cx - 34, y0 + 14); k.lineTo(cx - 34, y1 - 14); k.moveTo(cx + 34, y0 + 14); k.lineTo(cx + 34, y1 - 14); k.stroke();
    for (const fy of [y0 + 100, y1 - 122]) { k.beginPath(); k.moveTo(cx - 34, fy); k.lineTo(cx, fy + 22); k.lineTo(cx + 34, fy); k.lineTo(cx + 34, fy - 16); k.lineTo(cx - 34, fy - 16); k.fill(); }
    if (center) BH.vtext(k, center, cx, y0 + 150, { weight: '600', size: 30, gap: 10 });
    let x = x1 - 70; for (const c of cols) { const sz = c.size || 50, cw = Math.max(80, sz * 1.25); BH.vtext(o[c.color || 'ink'], c.text, x - cw / 2 + 30, y0 + 46, { size: sz, weight: sz > 90 ? '900' : '600', gap: sz > 90 ? 18 : 24 });
      x -= cw; k.lineWidth = 1.6; k.beginPath(); k.moveTo(x + 20, y0 + 14); k.lineTo(x + 20, y1 - 14); k.stroke(); }
    if (pic) { const r = [x0 + 34, y0 + 34, cx - 34 - 20 - x0 - 34, y1 - y0 - 68], p = new Path2D(); p.rect(...r); for (const c of [o.ink, o.red, o.blue, o.blueT, o.redT]) { c.save(); c.clip(p); } pic(o, r); for (const c of [o.ink, o.red, o.blue, o.blueT, o.redT]) c.restore(); k.lineWidth = 3; k.stroke(p); }
    if (seal) BH.seal(o.red, x1 - 60, y1 - 62, 70, seal, { color: RED, seed: 3 });
  };
  // 标题卡：大字 + 年份；用在前奏第 0 帧（也是横版封面）
  BH.titleCard = (o, spec) => { const { title, sub = '', y = 430, rect = [420, 190, 1080, 330] } = spec, k = o.ink, [x, yy, w, h] = rect;
    const p = new Path2D(); p.rect(x, yy, w, h); o.knock(p); k.fillRect(x + 20, yy + 10, w - 40, 6); k.fillRect(x + 20, yy + h - 16, w - 40, 6);
    const size = Math.min(230, (w - 80) / [...title].length / 1.12); BH.text(k, title, x + w / 2, y, { size, spacing: size * 0.11 });
    if (sub) BH.text(o.red, sub, x + w / 2, y + 60, { size: 44, color: RED, spacing: 40 }); };
  // 版框：副歌右侧的画框（插图印在框里）
  BH.frame = (o, rect, pic) => { const [x, y, w, h] = rect, p = new Path2D(); p.rect(x, y, w, h); o.knock(p);
    if (pic) { for (const c of [o.ink, o.red, o.blue, o.blueT, o.redT, o.inkT]) { c.save(); c.clip(p); } pic(o, rect); for (const c of [o.ink, o.red, o.blue, o.blueT, o.redT, o.inkT]) c.restore(); }
    o.ink.lineWidth = 9; o.ink.strokeRect(x, y, w, h); o.ink.lineWidth = 2.5; o.ink.strokeRect(x - 14, y - 14, w + 28, h + 28); };
  // 知识卡（尾奏用，统一版式）：kind 'timeline' | 'steps' | 'people'；items [{a:'1363', b:'一句话'}]；src 出处
  BH.card = (o, spec) => { const { ep = '01', series = '大明开局', title = '', kind = 'steps', items = [], src = '', rect = [260, 190, 1400, 660] } = spec, [x, y, w, h] = rect, k = o.ink;
    const p = new Path2D(); p.rect(x, y, w, h); o.knock(p); k.lineWidth = 8; k.strokeRect(x, y, w, h); k.lineWidth = 2; k.strokeRect(x + 14, y + 14, w - 28, h - 28);
    o.red.fillRect(x + 40, y + 40, 320, 56); erase(o.red, (c) => BH.text(c, `${series} · 第${ep}集`, x + 200, y + 80, { size: 30, weight: '900', color: '#000' }));
    BH.text(k, title, x + w / 2, y + 170, { size: 72 });
    const n = items.length, cw = (w - 160) / Math.max(1, n), ty = y + 330;
    if (kind === 'timeline') { k.lineWidth = 6; k.beginPath(); k.moveTo(x + 80, ty); k.lineTo(x + w - 80, ty); k.stroke(); }
    items.forEach((it, i) => { const cx = x + 80 + cw * (i + 0.5);
      if (kind === 'timeline') { o.red.beginPath(); o.red.arc(cx, ty, 18, 0, 7); o.red.fill(); k.lineWidth = 4; k.beginPath(); k.arc(cx, ty, 18, 0, 7); k.stroke(); BH.text(o.red, it.a, cx, ty - 44, { size: 46, color: RED }); wrap(k, it.b, cx, ty + 80, cw - 30, 40); }
      else if (kind === 'steps') { const box = new Path2D(); box.rect(cx - cw / 2 + 20, ty - 80, cw - 40, 300); k.lineWidth = 4; k.stroke(box); BH.text(o.red, it.a || ['①', '②', '③', '④', '⑤'][i], cx, ty - 10, { size: 60, color: RED }); wrap(k, it.b, cx, ty + 70, cw - 80, 42);
        if (i < n - 1) { k.lineWidth = 6; k.beginPath(); k.moveTo(cx + cw / 2 - 16, ty + 70); k.lineTo(cx + cw / 2 + 16, ty + 70); k.stroke(); k.beginPath(); k.moveTo(cx + cw / 2 + 4, ty + 58); k.lineTo(cx + cw / 2 + 18, ty + 70); k.lineTo(cx + cw / 2 + 4, ty + 82); k.stroke(); } }
      else { k.beginPath(); k.arc(cx, ty, 54, 0, 7); k.lineWidth = 5; k.stroke(); BH.text(k, it.a, cx, ty + 16, { size: 44 }); wrap(k, it.b, cx, ty + 120, cw - 30, 38); if (i < n - 1) { k.setLineDash([10, 8]); k.lineWidth = 3; k.beginPath(); k.moveTo(cx + 60, ty); k.lineTo(cx + cw - 60, ty); k.stroke(); k.setLineDash([]); } }
    });
    if (src) BH.text(k, src, x + w - 50, y + h - 40, { size: 26, weight: '600', align: 'right' });
  };
  // 折行：标点不放行首（挤到上一行末尾）
  const wrap = (k, s, cx, y, w, size) => { const per = Math.max(1, Math.floor(w / (size * 1.02))), cs = [...s], rows = []; let cur = [];
    for (const c of cs) { if (cur.length >= per && !'，。、；：！？）》”'.includes(c)) { rows.push(cur); cur = []; } cur.push(c); } if (cur.length) rows.push(cur);
    rows.forEach((r, i) => BH.text(k, r.join(''), cx, y + i * size * 1.3, { size, weight: '600' })); };
  BH.wrap = wrap;
  // 片尾卡：站队题（选项都在屏上）+ 下一集
  BH.endCard = (o, spec) => { const { question = '', options = [], next = '', rect = [260, 200, 1400, 640] } = spec, [x, y, w, h] = rect, k = o.ink;
    const p = new Path2D(); p.rect(x, y, w, h); o.knock(p); k.lineWidth = 8; k.strokeRect(x, y, w, h);
    wrap(k, question, x + w / 2, y + 130, w - 160, 64);
    const n = options.length, cw = (w - 160) / Math.max(1, n); options.forEach((op, i) => { const cx = x + 80 + cw * (i + 0.5), b = new Path2D(); b.rect(cx - cw / 2 + 24, y + 300, cw - 48, 130); o.red.fill(b); erase(o.red, (c) => BH.text(c, op, cx, y + 385, { size: 54, color: '#000' })); k.lineWidth = 4; k.stroke(b); });
    if (next) BH.text(k, next, x + w / 2, y + h - 60, { size: 40, weight: '600' });
  };
})();
