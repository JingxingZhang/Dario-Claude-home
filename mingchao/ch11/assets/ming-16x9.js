// 大明开局 · 16:9 横屏（默认；接在 ming.js、ming-recipes.js 之后加载，chapter.js 之前。竖屏工程不加载本文件）
// 画布 1920×1080。主题栏 x 60–910、y 40–136；内容安全区 x 100–1820、y 170–870（M.SAFE）；字幕带 y 890–1060。
// 只改尺寸和排版：F.kw / F.dossier 的默认位置、格子间距，以及所有带固定坐标的配方；调用方式与 9:16 版完全相同。
(function () {
  const M = window.Ming;
  M.W = 1920; M.H = 1080;
  M.SAFE = { x: 100, y: 170, w: 1720, h: 700, cx: 960, bottom: 870 };

  // 格子：每格一屏 1920×1080，格间留 160px
  M.stage = function (world) {
    const st = { panels: {} };
    st.panel = (id, gx, gy) => {
      const p = M.el('div', 'panel', world);
      p.id = 'p-' + id; p.setAttribute('data-id', 'shot-' + id);
      p.style.left = gx * 2080 + 'px'; p.style.top = gy * 1240 + 'px';
      st.panels[id] = { el: p, x: gx * 2080, y: gy * 1240 };
      return p;
    };
    st.show = (tl, id, t0, t1) => {
      const el = st.panels[id].el;
      tl.set(el, { visibility: 'visible' }, Math.max(0, t0));
      if (t1 != null) tl.set(el, { visibility: 'hidden' }, t1);
    };
    st.at = (id, x, y) => [st.panels[id].x + x, st.panels[id].y + y];
    return st;
  };

  const film0 = M.film;
  M.film = function (opts) {
    const F = film0(opts);
    const { C, tl, fx } = F;
    // 花字：默认在画面中上部、居中 1200 宽（x 360–1560），y 380
    const kwLayer = document.getElementById('kw');
    F.kw = (text, t, o) => {
      o = Object.assign({ until: t + 1.6, x: 360, w: 1200, y: 380, size: 180, color: C.red, back: true, rot: -3, sfx: 'impact', gain: 0.5 }, o || {});
      const n = [...String(text).replace(/<[^>]+>/g, '')].length, size = Math.min(o.size, Math.floor((o.w - 80) / Math.max(1, n)));
      const e = M.box(kwLayer, 'kw', o.x, o.y, `<span style="font-size:${size}px;color:${o.color};${o.back ? 'background:rgba(239,230,210,.95);box-shadow:0 12px 30px rgba(60,40,20,.2);' : 'text-shadow:0 6px 0 rgba(239,230,210,.95);'}">${text}</span>`, { w: o.w, rotate: o.rot + 'deg' });
      fx.in(e, t - 0.14, { opacity: 0, scale: 1.7 }, { opacity: 1, scale: 1 }, 0.2, 'power4.in');
      if (o.sfx) MR.sfx(o.sfx, t + 0.04, { gain: o.gain });
      if (o.until != null) fx.to(e, o.until, { opacity: 1, scale: 1 }, { opacity: 0, scale: 0.94 }, 0.22, 'power2.in');
      return e;
    };
    // 档案卡：卡片在画面中央（#dossier：x 540、y 180，最高 690），栏目多时行距自动收紧
    F.dossier = (d) => {
      d = Object.assign({ title: '户 口 本', sub: '', seal: '', rows: [] }, d || {});
      const dos = document.getElementById('dossier'), veil = document.getElementById('veil');
      const step = d.rows.length > 3 ? Math.floor(460 / d.rows.length) : 124;
      const CH = Math.min(690, Math.max(480, 250 + d.rows.length * step));
      const card = M.box(dos, 'card', 0, 0, '', { w: 840, h: CH });
      M.box(card, 'kai', 0, 40, d.title, { w: 840, textAlign: 'center', fontSize: '64px', letterSpacing: '6px' });
      if (d.sub) M.box(card, 'note', 0, 128, d.sub, { w: 840, textAlign: 'center' });
      const seal = d.seal ? M.seal(card, d.seal, { x: 690, y: 40, size: 92, rot: 6 }) : null;
      const rows = {};
      d.rows.forEach(([k, label], i) => {
        const r = M.box(card, 'row', 48, 190 + i * step, `<div class="k">${label}</div><div class="v" style="color:var(--wash-2)">？</div>`, { h: step - 16 });
        rows[k] = { row: r, ph: M.q(r, '.v'), v: M.box(r, 'v', 150, Math.max(6, (step - 16 - 64) / 2), ''), i };
      });
      gsap.set(dos, { opacity: 0, y: 40 });
      const api = { card, rows, seal };
      api.in = (t, unroll) => {
        fx.to(veil, t, { opacity: 0 }, { opacity: 0.86 }, 0.4, 'power2.out');
        fx.to(dos, t, { opacity: 0, y: 40, scale: 0.96 }, { opacity: 1, y: 0, scale: 1 }, 0.55, 'expo.out');
        if (unroll) fx.in(card, t, { scaleY: 0.05, transformOrigin: '50% 0%' }, { scaleY: 1 }, 0.7, 'expo.out');
        MR.sfx('paper', t + 0.1, { gain: 0.5 });
      };
      api.out = (t) => {
        fx.to(dos, t, { opacity: 1, y: 0, scale: 1 }, { opacity: 0, y: -30, scale: 0.97 }, 0.35, 'power2.in');
        fx.to(veil, t, { opacity: 0.86 }, { opacity: 0 }, 0.45, 'power2.inOut');
      };
      api.fill = (k, t, html, small) => {
        const R = rows[k];
        R.v.innerHTML = `<span class="w">${html}</span>${small ? `<small>${small}</small>` : ''}`;
        fx.to(R.ph, t, { opacity: 1 }, { opacity: 0 }, 0.15, 'none');
        M.write(tl, M.chars(M.q(R.v, '.w'), html), t, { dir: 'right', dur: 0.3, stagger: 0.12 });
        if (small) fx.fade(M.q(R.v, 'small'), t + 0.3, 0.4);
        MR.sfx('draw', t + 0.05, { dur: 0.4, gain: 0.45 });
      };
      api.mark = (k, t) => {
        const hi = M.box(card, '', 30, 190 + rows[k].i * step - 6, '', { w: 780, h: step - 4, border: `5px solid ${C.red}`, borderRadius: '10px', boxSizing: 'border-box' });
        fx.in(hi, t, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1 }, 0.4, 'expo.out');
      };
      api.stamp = (text, t, o) => { const s = M.seal(card, text, Object.assign({ x: 640, y: CH - 170, size: 120, rot: -8 }, o || {})); fx.stamp(s, t); return s; };
      api.stampSeal = (t) => seal && fx.stamp(seal, t);
      return api;
    };
    return F;
  };

  // ===================== 配方（横屏重排；参数与 9:16 版相同）=====================
  const rec0 = M.recipes;
  M.recipes = function (F) {
    const R = rec0(F);
    const { C, tl, fx } = F;
    const box = M.box, svg = M.svg, fig = F.fig;
    const A = M.SAFE, X = A.cx, L0 = A.x, LW = A.w;
    const line = (p, cls, y, html, st) => box(p, cls, L0, y, html, Object.assign({ w: LW, textAlign: 'center', whiteSpace: 'nowrap' }, st || {}));

    R.title = (p, o) => {
      const y = o.y == null ? 170 : o.y, sz = o.size || 88;
      const e = line(p, 'kai', y, '', { fontSize: sz + 'px', color: o.color || C.ink });
      M.write(tl, M.chars(e, o.text), o.at, { dir: 'right', dur: 0.3, stagger: Math.min(0.12, 0.9 / [...o.text].length) });
      let s = null;
      if (o.sub) { s = line(p, 'note src', y + sz * 1.3, o.sub); fx.fade(s, o.subAt == null ? o.at + 0.4 : o.subAt); }
      return { el: e, sub: s };
    };
    R.source = (p, o) => { const e = line(p, 'note src', o.y == null ? 826 : o.y, o.text, { fontSize: '32px' }); fx.fade(e, o.at); return e; };

    // 古地图：默认框居中 x 590–1330、y 196–846（比例与竖版相同，经纬不变形更多）
    const map0 = R.map;
    R.map = (p, o) => map0(p, Object.assign({}, o, { box: Object.assign({ x: X - 370, y: 196, w: 740, h: 650 }, o.box || {}) }));
    R.route = (p, map, o) => {
      const P = o.pts.map((k) => map.pt(k));
      const d = M.smooth(P);
      const col = o.color || C.red;
      const s = svg(p, 0, 0, M.W, M.H, `<path class="rt" pathLength="1" d="${d}" stroke="${col}" stroke-width="9" fill="none" stroke-linecap="round" ${o.dashed ? 'stroke-dasharray=".015 .012"' : ''}/>`);
      const path = M.q(s, '.rt');
      const dot = box(p, '', 0, 0, '', { w: 32, h: 32, borderRadius: '50%', background: col, boxShadow: '0 0 0 7px rgba(194,58,44,.25)' });
      const dur = o.dur || 2.0;
      if (!o.dashed) fx.draw(path, o.at, dur, 'power1.inOut'); else fx.fade(s, o.at, 0.4);
      const prog = { v: 0 };
      const place = () => { const Lt = path.getTotalLength(), q = path.getPointAtLength(Lt * prog.v); dot.style.transform = `translate(${q.x - 16}px, ${q.y - 16}px)`; };
      gsap.set(dot, { opacity: 0 }); place();
      tl.fromTo(dot, { opacity: 0 }, { opacity: 1, duration: 0.2, immediateRender: false }, o.at);
      tl.fromTo(prog, { v: 0 }, { v: 1, duration: dur, ease: 'power1.inOut', immediateRender: false, onUpdate: place }, o.at);
      MR.sfx('whoosh', o.at + dur * 0.5, { gain: 0.35, dur });
      if (o.label) { const [x, y] = P[P.length - 1]; const l = box(p, 'chip', Math.min(x + 20, A.x + A.w - 280), y + 14, o.label, { fontSize: '40px', background: col }); fx.pop(l, o.labelAt == null ? o.at + dur : o.labelAt, 0.4); }
      return { path, dot };
    };
    R.fires = (p, map, o) => {
      o.pts.forEach((k, i) => {
        const [x, y] = map.pt(k);
        const glow = box(p, '', x - 70, y - 80, `<img src="${M.ink({ size: 300, seed: 9, color: '194,58,44', alpha: 0.35, n: 30, spread: 0.2 })}" style="width:140px;height:140px">`);
        const f = svg(p, x - 34, y - 76, 68, 86, M.flame(), '0 0 52 68');
        const t = o.at + i * (o.gap || 0.22);
        fx.fade(glow, t, 0.3);
        fx.in(f, t, { scale: 0, opacity: 0, transformOrigin: '50% 100%' }, { scale: 1, opacity: 1 }, 0.35, MR.spring(0.3));
        tl.fromTo(f, { scaleY: 1 }, { scaleY: 1.15, duration: 0.18, yoyo: true, repeat: 9, ease: 'sine.inOut', immediateRender: false }, t + 0.35);
        if (o.years && o.years[i]) { const yb = box(p, 'chip', x - 46, y - 130, o.years[i], { fontSize: '32px', background: C.red, padding: '6px 12px 8px' }); fx.pop(yb, t + 0.15, 0.4); }
        MR.sfx('hit', t, { gain: 0.4, pan: ((i % 3) - 1) * 0.4 });
      });
      if (o.label) { const B = map.box; const l = box(p, 'chip', B.x + B.w + 40, B.y + B.h - 70, o.label, { fontSize: '42px', background: C.red }); fx.pop(l, o.labelAt == null ? o.at + 0.3 : o.labelAt, 0.4); }
    };

    // 皇位接力：龙椅居中，人名在右侧，时间轴横贯下方
    R.relay = (p, o) => {
      const TH = { x: X - 180, y: 250 };
      const glow = box(p, '', X - 350, TH.y - 60, '', { w: 700, h: 700, borderRadius: '50%', background: 'radial-gradient(circle, rgba(214,180,98,.45), rgba(214,180,98,0) 65%)' });
      const th = fig(p, TH.x, TH.y, 360, 400, M.goldDefs + M.throne(), 1.0);
      const t0 = o.items[0].at - 1.0, sa = o.seatAt == null ? t0 : o.seatAt;
      fx.in(th, sa, { opacity: 0, y: 40 }, { opacity: 1, y: 0 }, 0.6, 'expo.out'); fx.fade(glow, sa + 0.2, 0.8);
      MR.sfx('impact', sa + 0.3, { gain: 0.45 });
      if (o.title) R.title(p, { text: o.title, at: o.titleAt == null ? t0 : o.titleAt, y: 166, size: 76 });
      const [y0, y1] = o.years, AX = { x: 260, y: 790, w: 1400 };
      const yr = (y) => AX.x + ((y - y0) / (y1 - y0 + 0.5)) * AX.w;
      const ticks = []; for (let y = Math.ceil(y0); y <= y1; y++) ticks.push(y);
      const step = Math.max(1, Math.ceil(ticks.length / 10));
      const axis = svg(p, 0, AX.y - 40, M.W, 120, `<path pathLength="1" d="M${AX.x},40 L${AX.x + AX.w},40" stroke="${C.ink}" stroke-width="5" fill="none"/>` + ticks.filter((_, i) => i % step === 0).map((y) => `<path d="M${yr(y)},28 L${yr(y)},52" stroke="${C.ink}" stroke-width="5"/><text x="${yr(y)}" y="100" text-anchor="middle" font-family="LXGW WenKai" font-size="38" fill="${C.ink2}">${y}</text>`).join(''));
      fx.draw(M.q(axis, 'path'), t0 + 0.3, 0.8); fx.fade(axis, t0 + 0.3, 0.4);
      const punch = (t) => { const [wx, wy] = F.S.at(p.id.replace('p-', ''), M.W / 2, M.H / 2); F.camTo(t, { focus: [wx, wy], zoom: 1.07, duration: 0.12, ease: 'power3.out', noDrift: true }); F.camTo(t + 0.15, { focus: [wx, wy], zoom: 1.0, duration: 0.6, ease: 'power2.out' }); MR.sfx('hit', t, { gain: 0.55 }); };
      const seatBottom = TH.y + 340;
      const NX = X + 290, NW = A.x + A.w - NX;
      const els = o.items.map((it, idx) => {
        const nextAt = o.items[idx + 1] ? o.items[idx + 1].at : Infinity;
        const sc = it.child ? 1.15 : 1.6;
        const e = fig(p, X - 60 * sc, seatBottom - 200 * sc, 120, 200, M.emperor(), sc, false, it.color || C.ink);
        gsap.set(e, { opacity: 0 });
        tl.fromTo(e, { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.25, immediateRender: false }, it.at - 0.15);
        punch(it.at - 0.15);
        const n = box(p, 'kai', NX, 360, it.name, { w: NW, fontSize: '88px', whiteSpace: 'nowrap' });
        const s2 = box(p, 'note', NX + 4, 474, it.sub || '', { w: NW, fontSize: '40px' });
        gsap.set([n, s2], { opacity: 0 });
        const until = Math.min(it.until == null ? it.at + 2.5 : it.until, nextAt - 0.34);
        tl.fromTo([n, s2], { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: 0.25, ease: 'expo.out', immediateRender: false }, it.at - 0.15);
        tl.fromTo([n, s2], { opacity: 1 }, { opacity: 0, duration: 0.15, immediateRender: false }, until);
        if (it.from != null) {
          const seg = box(p, '', yr(it.from), AX.y - 16, '', { w: Math.max(12, yr(it.to) - yr(it.from)), h: 32, background: it.segColor || C.ink2, transformOrigin: '0 50%', borderRadius: '4px' });
          fx.in(seg, it.segAt == null ? it.at : it.segAt, { scaleX: 0 }, { scaleX: 1 }, 0.4, 'power3.out');
          if (it.segLabel) { const l = box(p, 'note', yr(it.from) - 10, AX.y - 74, it.segLabel, { fontSize: '34px', color: it.segColor === C.red ? C.red : C.ink2 }); fx.fade(l, (it.segAt == null ? it.at : it.segAt) + 0.1, 0.3); }
        }
        const oa = it.outAt == null ? until : it.outAt;
        if (it.out === 'kick') { tl.fromTo(e, { x: 0, opacity: 1 }, { x: -700, opacity: 0, rotation: -25, duration: 0.35, ease: 'power3.in', immediateRender: false }, oa); MR.sfx('whip', oa + 0.1, { gain: 0.5 }); }
        else if (it.out === 'fall') { tl.fromTo(e, { color: C.ink }, { color: C.red, duration: 0.12, immediateRender: false }, oa); tl.fromTo(e, { opacity: 1, y: 0 }, { opacity: 0, y: 60, duration: 0.6, ease: 'power2.in', immediateRender: false }, oa + 0.4); MR.sfx('thud', oa + 0.05, { gain: 0.7 }); }
        else if (it.out !== 'stay') tl.fromTo(e, { opacity: 1 }, { opacity: 0, y: 30, duration: 0.5, immediateRender: false }, oa);
        return e;
      });
      return { throne: th, emperors: els, yr };
    };

    // 族谱：只有一列（一条血脉）时横排、从左到右；多列时竖排，每列最多 5 代
    R.tree = (p, o) => {
      const drawNode = (x, yc, w, h, nd, ni, ci, n) => {
        const hiFrom = nd.hi == null ? 1 : nd.hi;
        const nm = nd.self ? nd.name : nd.name.slice(0, hiFrom) + '<span class="num">' + nd.name.slice(hiFrom) + '</span>';
        const b = box(p, '', x - w / 2, yc - h / 2, `<div class="note" style="text-align:center;font-size:${h > 130 ? 34 : 30}px;line-height:1.2">${nd.role || ''}</div><div class="kai" style="text-align:center;font-size:${h > 130 ? 68 : 58}px;line-height:1.1;white-space:nowrap">${nm}</div>`, { w, h, border: `4px solid ${nd.self ? C.red : C.ink}`, borderRadius: '12px', background: '#f4ecda', boxSizing: 'border-box', paddingTop: h > 130 ? '18px' : '6px' });
        fx.drop(b, nd.at - 0.1, 40, 0.5);
        MR.sfx('pop', nd.at + 0.05, { note: ni + 1 + ci, gain: 0.4, pan: n > 1 ? (ci / (n - 1) - 0.5) : 0 });
        if (o.hiAt != null || nd.hiAt != null) M.qa(b, '.num').forEach((e) => fx.to(e, (nd.hiAt == null ? o.hiAt + ni * 0.12 : nd.hiAt), { color: C.ink }, { color: C.red }, 0.3));
        return b;
      };
      if (o.cols.length === 1 && o.dir !== 'col') {
        const c = o.cols[0], nodes = c.nodes, n = nodes.length;
        const gap = LW / n, w = Math.min(300, gap - 40), h = 170, yc = 560;
        const xs = nodes.map((_, i) => L0 + gap * (i + 0.5));
        const hd = line(p, 'kai', 300, c.head, { fontSize: '64px', color: C.red });
        fx.rise(hd, c.headAt == null ? nodes.find(Boolean).at - 0.4 : c.headAt, 16);
        nodes.forEach((nd, ni) => {
          if (!nd) return;
          drawNode(xs[ni], yc, w, h, nd, ni, 0, 1);
          if (ni > 0 && nodes[ni - 1]) {
            const x0 = xs[ni - 1] + w / 2, len = xs[ni] - xs[ni - 1] - w;
            const ln = svg(p, x0, yc - 10, len, 20, `<path pathLength="1" d="M0,10 L${len - 4},10" stroke="${C.ink2}" stroke-width="5" fill="none"/><path d="M${len - 14},2 L${len},10 L${len - 14},18" fill="none" stroke="${C.ink2}" stroke-width="5"/>`);
            fx.draw(M.q(ln, 'path'), nd.at - 0.25, 0.25); fx.fade(ln, nd.at - 0.25, 0.2);
          }
        });
        return { xs, Y: [yc] };
      }
      const n = o.cols.length, xs = o.cols.map((_, i) => L0 + (LW / (n + 1)) * (i + 1));
      const Y = [298, 430, 562, 694, 826], BH = 112;
      o.cols.forEach((c, ci) => {
        const x = xs[ci];
        const hd = box(p, 'kai', x - 160, 170, c.head, { w: 320, textAlign: 'center', fontSize: '56px', color: C.red, whiteSpace: 'nowrap' });
        fx.rise(hd, c.headAt == null ? c.nodes.find(Boolean).at - 0.4 : c.headAt, 16);
        c.nodes.forEach((nd, ni) => {
          if (!nd) return;
          drawNode(x, Y[ni], 280, BH, nd, ni, ci, n);
          if (ni > 0 && c.nodes[ni - 1]) { const gap = Y[ni] - Y[ni - 1] - BH; const ln = svg(p, x - 3, Y[ni - 1] + BH / 2, 6, gap, `<path pathLength="1" d="M3,0 L3,${gap}" stroke="${C.ink2}" stroke-width="5" fill="none"/>`); fx.draw(M.q(ln, 'path'), nd.at - 0.25, 0.25); }
        });
      });
      return { xs, Y };
    };

    // 证伪：卷轴居中（宽 1100）→ 一排史书 + 放大镜 → 朱印 → 解释
    R.refute = (p, o) => {
      if (o.question) { const q = line(p, 'kai', 170, o.question, { fontSize: '80px' }); fx.rise(q, o.qAt, 24); }
      const SW = 1100, SX = X - SW / 2, SY = 300, SH = 320;
      const scroll = box(p, '', SX, SY, '', { w: SW, h: SH });
      const paperS = box(scroll, '', 30, 0, '', { w: SW - 60, h: SH, background: '#f6eedc', border: `2px solid ${C.wash}`, boxShadow: '0 12px 30px rgba(60,40,20,.15)' });
      const rodL = box(scroll, '', 0, -20, '', { w: 34, h: SH + 40, background: C.ink2, borderRadius: '10px' });
      const rodR = box(scroll, '', SW - 34, -20, '', { w: 34, h: SH + 40, background: C.ink2, borderRadius: '10px' });
      const k = box(paperS, 'kai', 0, 40, o.kicker || '传说', { w: SW - 60, textAlign: 'center', fontSize: '46px', color: C.ink2 });
      const c = box(paperS, 'kai', 30, 110, o.claim, { w: SW - 120, textAlign: 'center', fontSize: '68px', lineHeight: 1.25 });
      const t = o.claimAt;
      fx.fade(scroll, t - 0.4, 0.2);
      fx.in(paperS, t - 0.4, { clipPath: 'inset(0 50% 0 50%)' }, { clipPath: 'inset(0 0% 0 0%)' }, 0.9, 'power3.out');
      fx.in(rodL, t - 0.4, { x: SW / 2 - 17 }, { x: 0 }, 0.9, 'power3.out'); fx.in(rodR, t - 0.4, { x: -(SW / 2 - 17) }, { x: 0 }, 0.9, 'power3.out');
      MR.sfx('paper', t - 0.3, { gain: 0.5 });
      fx.fade(k, t + 0.2); fx.rise(c, t + 0.3, 14);
      if (o.extra) { const e = box(paperS, 'note', 0, 240, o.extra, { w: SW - 60, textAlign: 'center' }); fx.rise(e, o.extraAt, 14); }
      const books = [0, 1, 2].map((i) => fig(p, X - 311 + i * 250, 660, 122, 150, M.iconBook(), 1.0));
      books.forEach((b, i) => { fx.drop(b, o.checkAt - 0.2 + i * 0.12, 40); tl.fromTo(b, { rotationY: 0 }, { rotationY: 180, duration: 0.4, ease: 'power2.inOut', yoyo: true, repeat: 3, immediateRender: false }, o.checkAt + 0.3 + i * 0.15); });
      MR.sfx('paper', o.checkAt + 0.2, { gain: 0.4 }); MR.sfx('paper', o.checkAt + 0.6, { gain: 0.35, pan: 0.4 });
      const lens = svg(p, X - 420, 650, 140, 140, `<circle cx="56" cy="56" r="42" fill="rgba(255,255,255,.25)" stroke="${C.ink}" stroke-width="10"/><path d="M88,88 L130,130" stroke="${C.ink}" stroke-width="16" stroke-linecap="round"/>`);
      fx.fade(lens, o.checkAt + 0.1, 0.3);
      tl.fromTo(lens, { x: 0 }, { x: 640, duration: 1.6, ease: 'sine.inOut', immediateRender: false }, o.checkAt + 0.2);
      const st = M.seal(p, o.stamp || '查无此条', { x: X - 230, y: 400, size: 150, zhu: true, rot: -10, row: true });
      fx.stamp(st, o.stampAt, 0.9);
      const alts = o.alts || [];
      if (alts.length) fx.to([...books, lens], alts[0].at - 0.3, { opacity: 1 }, { opacity: 0 }, 0.3);
      const W0 = LW / (alts.length + 1);
      alts.forEach((a, i) => { const e = box(p, 'tag', L0 + W0 * (i + 1) - 150, 664, a.text, { w: 300, textAlign: 'center', boxSizing: 'border-box' }); fx.pop(e, a.at - 0.05, 0.5); MR.sfx('pop', a.at, { note: i + 3, gain: 0.45 }); });
      if (o.conclusion) { const e = line(p, 'kai', 750, o.conclusion, { fontSize: '66px', color: C.red }); fx.rise(e, o.conclusionAt, 16); }
      if (o.source) R.source(p, { text: o.source, at: o.stampAt + 0.5, y: 830 });
      return { scroll, stamp: st };
    };

    // 对照：左右两半（top → 左，bottom → 右），中间一条竖线
    R.compare = (p, o) => {
      box(p, '', X - 2, 200, '', { w: 4, h: 620, background: C.wash2 });
      const half = (h, x0) => {
        const f = fig(p, x0 + 30, 320, 400, 232, h.figure || M.buffalo(), h.scale || 1.05);
        const l = box(p, 'kai', x0 + 40, 196, h.label, { fontSize: '58px', whiteSpace: 'nowrap' });
        fx.rise(f, h.at - 0.3, 20); fx.fade(l, h.at);
        if (h.tag) { const t = box(p, 'tag', x0 + 40, 600, h.tag); fx.pop(t, h.tagAt == null ? h.at + 0.5 : h.tagAt, 0.5); }
        return f;
      };
      const xL = L0, xR = X + 40;
      half(o.top, xL); half(o.bottom, xR);
      const marks = (x0, y, vals, times) => vals.map((ok, i) => {
        const e = box(p, '', x0 + i * 124, y, `<div class="note" style="text-align:center;font-size:40px;color:${C.ink}">${o.keys[i]}</div><div style="text-align:center;font:900 76px/1 var(--hei);color:${ok ? C.ink : C.red}">${ok ? '✓' : '✕'}</div>`, { w: 112 });
        fx.pop(e, times[i], 0.45); MR.sfx(ok ? 'ding' : 'thud', times[i] + 0.05, { note: 3 + i, gain: 0.4 });
        return e;
      });
      if (o.topMarks) marks(xL + 480, 360, o.topMarks, o.topAt);
      if (o.bottomMarks) marks(xR + 480, 360, o.bottomMarks, o.bottomAt);
      if (o.link) { const lk = svg(p, X - 260, 640, 520, 100, `<path pathLength="1" d="M500,20 Q260,110 20,20" stroke="${C.red}" stroke-width="6" fill="none"/>`); fx.draw(M.q(lk, 'path'), o.link.at, 0.6); if (o.link.label) { const c = box(p, 'chip', X - 90, 740, o.link.label, { fontSize: '38px', background: C.red }); fx.pop(c, o.link.at + 0.4, 0.45); } }
    };

    // 循环图：有标题时标题在左、圆环在右；没有标题时圆环居中
    R.cycle = (p, o) => {
      const cx = o.title ? X + 260 : X, cy = 510, RR = 225;
      if (o.title) { const t = box(p, 'kai', L0 + 20, 440, o.title, { w: 700, textAlign: 'center', fontSize: '110px', whiteSpace: 'nowrap' }); fx.rise(t, o.titleAt, 16); }
      const ring = box(p, '', cx - RR, cy - RR, '', { w: RR * 2, h: RR * 2 });
      const n = o.nodes.length;
      o.nodes.forEach((nd, i) => {
        const a = -Math.PI / 2 + (i / n) * Math.PI * 2, x = RR + Math.cos(a) * RR, y = RR + Math.sin(a) * RR;
        let e, bw = 180, bh = 120;
        if (nd.figure) { bw = nd.figure.w * nd.figure.sc; bh = nd.figure.h * nd.figure.sc; e = fig(ring, x - bw / 2, y - bh / 2 - 24, nd.figure.w, nd.figure.h, nd.figure.svg, nd.figure.sc); }
        else e = box(ring, 'kai', x - 120, y - 70, nd.html || '', { w: 240, textAlign: 'center', fontSize: '52px', lineHeight: 1.15 });
        const lb = box(ring, 'chip', x - 90, y + bh / 2 - 10, nd.label, { w: 180, textAlign: 'center', fontSize: '40px', padding: '8px 0 10px' });
        fx.pop(e, nd.at - 0.1, 0.5); fx.pop(lb, nd.at + 0.1, 0.4); MR.sfx('pop', nd.at, { note: i + 2, gain: 0.45 });
      });
      const arrows = svg(ring, 0, 0, RR * 2, RR * 2, o.nodes.map((_, i) => {
        const a0 = -Math.PI / 2 + (i / n) * Math.PI * 2 + 0.42, a1 = a0 + (Math.PI * 2) / n - 0.84;
        return `<path class="ar" pathLength="1" d="M${RR + RR * Math.cos(a0)},${RR + RR * Math.sin(a0)} A${RR},${RR} 0 0 1 ${RR + RR * Math.cos(a1)},${RR + RR * Math.sin(a1)}" stroke="${C.red}" stroke-width="7" fill="none" marker-end="url(#ah-${p.id})"/>`;
      }).join('') + `<defs><marker id="ah-${p.id}" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="${C.red}"/></marker></defs>`);
      M.qa(arrows, '.ar').forEach((e, i) => fx.draw(e, (o.arrowsAt || [])[i] == null ? o.nodes[(i + 1) % n].at - 0.3 : o.arrowsAt[i], 0.5));
      if (o.spinAt != null) tl.fromTo(arrows, { rotation: 0 }, { rotation: 360, transformOrigin: '50% 50%', duration: 6, ease: 'power1.inOut', immediateRender: false }, o.spinAt);
      if (o.fadeAt != null) fx.to(ring, o.fadeAt, { opacity: 1 }, { opacity: 0.35 }, 2.0, 'power1.inOut');
      return ring;
    };

    // 数据计数卡：居中，最宽 1200
    R.counters = (p, o) => {
      const y = o.y == null ? 340 : o.y, CW = Math.min(LW, Math.max(760, 420 * o.items.length + 72)), cx0 = X - CW / 2;
      const card = box(p, '', cx0, y, '', { w: CW, h: 300, background: '#f4ecda', border: `4px solid ${C.ink}`, borderRadius: '12px', boxShadow: '0 14px 34px rgba(60,40,20,.15)' });
      box(card, 'kai', 36, 26, o.title || '', { fontSize: '50px', whiteSpace: 'nowrap' });
      const w = (CW - 72) / o.items.length;
      o.items.forEach((it, i) => {
        const c = box(card, '', 36 + i * w, 110, `<span class="kai" style="font-size:52px">${it.label} </span><span class="num" style="font:900 120px/1 var(--hei);color:${C.red}">0</span><span class="note" style="font-size:40px;color:${C.ink}"> ${it.unit || ''}</span>`, { whiteSpace: 'nowrap' });
        const d = it.decimals || 0;
        fx.count(M.q(c, '.num'), it.at, 0, it.value, 1.3, (v) => v.toFixed(d));
      });
      fx.rise(card, o.at - 0.2, 20);
      MR.sfx('count', o.items[0].at, { dur: 1.4, gain: 0.4 });
      if (o.source) R.source(p, { text: o.source, at: o.at + 0.5, y: y + 330 });
      return card;
    };

    // 名目票据：一行 4 张；超过 4 张排两行（票据变矮）
    R.slips = (p, o) => {
      if (o.title) R.title(p, { text: o.title, at: o.titleAt, y: 170, size: 80, sub: o.source });
      const N = o.items.length, cw = 380, chh = N > 4 ? 230 : 270, gx = (LW - 4 * cw) / 5;
      const els = o.items.map((it, i) => {
        const col = i % 4, row = Math.floor(i / 4), perRow = Math.min(4, N - row * 4);
        const x = X - (perRow * cw + (perRow - 1) * gx) / 2 + col * (cw + gx), y = 350 + row * (chh + 22);
        const e = box(p, '', x, y, `<div class="kai" style="font-size:80px;color:${C.red};text-align:center;margin-top:${N > 4 ? 30 : 44}px;white-space:nowrap">${it.name}</div><div class="note" style="text-align:center;margin-top:14px;font-size:38px;color:${C.ink}">${it.why || ''}</div>`, { w: cw, h: chh, background: '#f6eedc', border: `5px solid ${C.red}`, borderRadius: '10px', boxShadow: '0 10px 24px rgba(60,40,20,.15)', rotate: (i % 2 ? 3 : -3) + 'deg' });
        fx.in(e, it.at - 0.2, { opacity: 0, scale: 1.4, y: -30 }, { opacity: 1, scale: 1, y: 0 }, 0.3, 'power4.in');
        MR.sfx('paper', it.at + 0.08, { gain: 0.55, pan: col / 3 - 0.5 });
        return e;
      });
      if (o.finale) {
        const f = o.finale;
        fx.to(els, f.at - 0.6, { opacity: 1 }, { opacity: 0.3 }, 0.4);
        const big = box(p, '', X - 360, 300, `<div class="kai" style="font-size:160px;color:${C.paper};text-align:center;margin-top:60px;white-space:nowrap">${f.name}</div><div class="kai" style="text-align:center;font-size:52px;color:${C.paper};margin-top:16px">${f.sub || ''}</div>`, { w: 720, h: 440, background: C.red, borderRadius: '12px', boxShadow: '0 20px 50px rgba(120,30,20,.35)' });
        fx.in(big, f.at - 0.25, { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1 }, 0.25, 'power4.in');
        MR.sfx('impact', f.at, { gain: 0.6 });
        if (f.coins !== false) {
          const r = MR.random(5);
          for (let i = 0; i < 16; i++) {
            const a = (i / 16) * Math.PI * 2, d = 420 + r() * 220;
            const c = fig(p, X - 40, 480, 100, 100, M.coin(), 0.8);
            gsap.set(c, { opacity: 0 });
            tl.fromTo(c, { opacity: 1, x: 0, y: 0, rotation: 0 }, { x: Math.cos(a) * d, y: Math.sin(a) * d * 0.45 + 120, rotation: r() * 720, duration: 1.3, ease: 'power2.out', immediateRender: false }, f.at + 0.02);
          }
          MR.sfx('count', f.at + 0.1, { dur: 0.9, gain: 0.4 });
        }
        return { slips: els, big };
      }
      return { slips: els };
    };

    // 大字砸下 + 一排印章：大字上移缩小后，印章横排在下方
    R.slam = (p, o) => {
      const sz = Math.min(o.size || 320, Math.floor(LW / Math.max(1, [...o.text].length) * 1.15));
      const big = line(p, 'kai', 250, o.text, { fontSize: sz + 'px', color: o.color || C.red, lineHeight: 1 });
      fx.in(big, o.at - 0.2, { opacity: 0, scale: 2.4 }, { opacity: 1, scale: 1 }, 0.22, 'power4.in');
      MR.sfx('impact', o.at + 0.02, { gain: 0.85 }); MR.sfx('subdrop', o.at + 0.02, { gain: 0.8, dur: 1.6 });
      tl.fromTo(p, { x: 0 }, { x: 10, duration: 0.04, yoyo: true, repeat: 7, ease: 'none', immediateRender: false }, o.at + 0.02);
      let sub = null;
      if (o.sub) { sub = line(p, 'kai', 250 + sz + 30, o.sub, { fontSize: '72px' }); fx.rise(sub, o.subAt == null ? o.at - 1 : o.subAt, 16); }
      const seals = o.seals || [];
      if (seals.length) {
        const la = o.liftAt == null ? seals[0].at - 0.6 : o.liftAt;
        fx.to(big, la, { y: 0, scale: 1 }, { y: -150, scale: 0.55 }, 0.5, 'power3.inOut');
        if (sub) fx.to(sub, la, { y: 0, opacity: 1 }, { y: -300, opacity: 0 }, 0.4, 'power3.inOut');
        const gap = Math.min(260, (LW - 40) / seals.length), x0 = X - (gap * (seals.length - 1) + 180) / 2;
        seals.forEach((s, i) => {
          const x = x0 + i * gap, y = 520;
          const e = M.seal(p, s.char, { x, y, size: 180, rot: [-6, 4, -3, 6][i % 4] });
          fx.stamp(e, s.at + 0.05, 0.8);
          if (s.art) { const a2 = svg(p, x + 15, y + 200, 150, 130, s.art); fx.fade(a2, s.at + 0.15, 0.3); }
        });
      }
      return big;
    };

    // 金句：逐行书写，居中
    R.quote = (p, o) => {
      if (o.by) { const w = M.seal(p, o.by, { x: X - 60, y: 170, size: 120, rot: -4, zhu: true }); fx.stamp(w, o.byAt, 0.6); }
      let y = o.by ? 330 : 250;
      o.lines.forEach((l, i) => {
        const n = [...l.text].length, sz = Math.min(l.size || (i === 1 ? 130 : 96), Math.floor(LW / Math.max(1, n)));
        const e = line(p, 'kai', y, '', { fontSize: sz + 'px', color: l.color || (i === 1 ? C.red : C.ink) });
        M.write(tl, M.chars(e, l.text), l.at - 0.1, { dur: 0.3, stagger: 0.13, dir: 'right' });
        MR.sfx('draw', l.at, { dur: 0.8, gain: 0.4 });
        y += sz * 1.4;
      });
      const a = line(p, 'kai', y + 20, o.attribution || '——《明朝那些事儿》', { fontSize: '46px', color: C.gold });
      fx.rise(a, o.attrAt, 14);
    };

    // 片尾预告
    R.endCard = (p, o) => {
      const V = F.V;
      const nx = line(p, 'note', 170, '下 一 集', { fontSize: '44px', letterSpacing: '8px', color: C.ink2 });
      const no = box(p, 'chip', X - 130, 236, V.nextNo, { w: 260, textAlign: 'center', background: C.red, fontFamily: 'var(--kai)', fontWeight: 500, fontSize: '56px', padding: '14px 0 16px', letterSpacing: '6px' });
      const n = [...V.nextTitle].length, tsz = Math.min(220, Math.floor((LW - 20) / Math.max(1, n) - 12));
      const tt = line(p, 'kai', 350, '', { fontSize: tsz + 'px', lineHeight: 1, letterSpacing: '12px' });
      fx.fade(nx, o.at - 0.3); fx.drop(no, o.at - 0.1, 40, 0.5);
      M.write(tl, M.chars(tt, V.nextTitle), o.titleAt == null ? o.at + 0.3 : o.titleAt, { dur: 0.5, stagger: Math.min(0.3, 1.2 / n) });
      MR.sfx('draw', o.titleAt == null ? o.at + 0.3 : o.titleAt, { dur: 0.8, gain: 0.5 });
      const hy = 350 + tsz + 40;
      if (V.nextHint) { const h = line(p, 'kai', hy, V.nextHint, { fontSize: '56px', color: C.red }); fx.pop(h, o.hintAt == null ? o.at + 1.2 : o.hintAt, 0.5); }
      if (o.question) { const q = line(p, 'kai', hy + (V.nextHint ? 84 : 0), o.question, { fontSize: '60px', color: C.ink }); fx.rise(q, o.questionAt, 14); }
      const ser = line(p, 'kai', 800, V.series, { fontSize: '44px', letterSpacing: '8px', color: C.ink2 });
      fx.fade(ser, (o.questionAt == null ? o.at + 1.5 : o.questionAt) + 0.6, 0.6);
      if (V.seal) { const sl = M.seal(p, V.seal, { x: 1600, y: 660, size: 100, rot: -6 }); fx.stamp(sl, F.T.last() + 0.2, 0.6); }
      MR.sfx('chime', F.T.last() + 0.4, { gain: 0.5 });
      svg(p, 0, 860, M.W, 220, M.mountains(M.W, 220, 131, { layers: 2, top: 0.2 }));
    };

    R.verdict = (p, o) => { const s = M.seal(p, o.text, { x: o.x == null ? X - 190 : o.x, y: o.y == null ? 420 : o.y, size: o.size || 150, rot: o.rot == null ? -8 : o.rot, row: true, zhu: !!o.zhu }); fx.stamp(s, o.at, 0.9); return s; };
    // 远山地平线：地平线默认 y 868，紧贴字幕带上沿
    R.land = (p, o) => { o = o || {}; svg(p, 0, o.y == null ? 520 : o.y, M.W, 560, M.mountains(M.W, 560, o.seed || 12, { layers: 3, top: 0.14, amp: 0.2 })); if (o.ground !== false) box(p, '', 0, 868, '', { w: M.W, h: 5, background: C.ink, opacity: 0.85 }); };

    return R;
  };
})();
