// 当年明月 · 镜头配方库（抖音 9:16 版）
// Ming.film() 把每章都一样的部分收在一起：镜头队列（按时间排序）、墨迹转场、档案卡、主题栏、花字、字幕、动效音量、
// 停留段镜头呼吸、试看窗口、注册时间线。配方（F.R.*）把验证过的镜头做成“填数据”的函数。
// 没有片头：旁白从第 0 秒开口，第一个镜头就是钩子。所有配方都排在安全区里（M.SAFE：x 60–920、y 360–1240）。
// 约定：所有时间都是秒，通常写成 T(行号)、T(行号, '词')、T.end(行号)（见 SKILL.md）。
(function () {
  const M = window.Ming;

  M.film = function (opts) {
    opts = opts || {};
    const V = MR.vars();
    const C = M.C;
    const W = window.__testWindow || null;
    // 动效音量（V.sfxGain，默认 1.2）+ 试看窗口的时间平移；返回原始时间，方便写在补间位置上
    const sfx0 = MR.sfx;
    MR.sfx = (name, at, o) => {
      if (!(at >= 0)) return at;
      if (W && (at < W[0] || at > W[1])) return at;
      sfx0(name, W ? at - W[0] : at, Object.assign({}, o, { gain: ((o && o.gain) ?? 1) * (V.sfxGain ?? 1.2) }));
      return at;
    };
    const DATA = JSON.parse(document.getElementById('script-lines').textContent);
    const T = M.voice(DATA.lines);
    const tl = gsap.timeline({ paused: true });
    const fx = M.bind(tl);
    const world = document.getElementById('world');
    const S = M.stage(world);
    const cam = MR.camera('#world', { width: M.W, height: M.H });
    M.paper(document.querySelector('#paper canvas'), opts.paperSeed || 7);
    const hudEp = document.getElementById('hudEp'), topics = document.getElementById('topics');
    if (hudEp) hudEp.textContent = V.series + (V.epNo ? ' · ' + V.epNo : '');
    // 署名：右上角常驻（变量 signature，默认“@张景行”；留空则不显示）
    const sign = document.getElementById('sign');
    if (sign) { if (V.signature) sign.textContent = V.signature; else sign.style.display = 'none'; }
    const topicSize = (text) => Math.max(34, Math.min(50, Math.floor(470 / Math.max(1, [...text].length)) - 3)) + 'px';
    let curTopic = topics ? M.el('div', 'topic', topics, V.topic || V.chapTitle, { fontSize: topicSize(V.topic || V.chapTitle) }) : null;

    const F = { V, C, T, tl, fx, S, cam, DATA, M };
    F.box = M.box; F.svg = M.svg;
    F.fig = (p, x, y, w, h, inner, sc, flip, color) => {
      const s = M.svg(p, x, y, w * (sc || 1), h * (sc || 1), flip ? `<g transform="translate(${w},0) scale(-1,1)">${inner}</g>` : inner, `0 0 ${w} ${h}`);
      s.style.color = color || C.ink; s.style.overflow = 'visible';
      return s;
    };
    // ---------- 镜头：先排队，finish() 时按时间排序再交给 MR.camera ----------
    const camQ = [];
    F.camTo = (t, o) => camQ.push({ t: Math.max(0, t), o, i: camQ.length });
    F.go = (id, t, dur, ease, extra) => F.camTo(t, Object.assign({ fit: '#p-' + id, pad: 0, duration: dur == null ? 1.0 : dur, ease: ease || 'power3.inOut' }, extra || {}));
    F.look = (id, x, y, zoom, t, dur, ease) => { const [wx, wy] = S.at(id, x, y); F.camTo(t, { focus: [wx, wy], zoom, duration: dur == null ? 1 : dur, ease: ease || 'power3.inOut' }); };
    F.cut = (id, t) => F.go(id, t, 0.02, 'none');
    F.scene = (name, t) => tl.addLabel('scene:' + name, Math.max(0, t));
    F.show = (id, t0, t1) => S.show(tl, id, t0, t1);
    // 墨迹转场：t 开始涌，t+0.5 盖满（在此切镜头），随后散开
    const wipeImg = document.querySelector('#wipe img');
    wipeImg.src = M.inkFlood(21);
    gsap.set(wipeImg, { opacity: 0, scale: 0.05 });
    F.wipe = (t, cutFn) => {
      tl.fromTo(wipeImg, { opacity: 1, scale: 0.05, rotation: 0 }, { scale: 1.7, rotation: 25, duration: 0.5, ease: 'power2.in', immediateRender: false }, t);
      if (cutFn) cutFn(t + 0.5);
      tl.fromTo(wipeImg, { opacity: 1, scale: 1.7, rotation: 25 }, { opacity: 0, scale: 2.6, rotation: 40, duration: 0.55, ease: 'power2.out', immediateRender: false }, t + 0.5);
      MR.sfx('whoosh', t + 0.45, { gain: 0.55 });
    };
    // 一个镜头 = 一个格子：F.shot(id, gx, gy, t0, t1, { enter: 'pan'|'wipe'|'cut'|'none', dur })
    // pan：t0 起平移 dur 秒；wipe：t0-0.5 起墨迹，t0 切入；cut：t0 硬切（配合 drop/重音）
    let firstShot = true;
    F.shot = (id, gx, gy, t0, t1, o) => {
      o = Object.assign({ enter: 'pan', dur: 0.9 }, o || {});
      const p = S.panel(id, gx, gy);
      if (firstShot) { firstShot = false; cam.set({ fit: '#p-' + id, pad: 0 }); F.cut(id, 0); p.style.visibility = 'visible'; if (t1 != null) tl.set(p, { visibility: 'hidden' }, t1); return p; } // 第一个镜头 = 第 0 帧（也是信息流里的首帧）
      if (o.enter === 'pan') { F.go(id, t0, o.dur); F.show(id, t0 - 0.1, t1); }
      else if (o.enter === 'wipe') { F.wipe(t0 - 0.5, (tc) => F.cut(id, tc)); F.show(id, t0 - 0.05, t1); }
      else if (o.enter === 'cut') { F.cut(id, t0); F.show(id, t0 - 0.05, t1); }
      else F.show(id, t0, t1);
      return p;
    };
    // 主题栏从第 0 帧起常驻（深底，夜景上也看得清）；换段时换一句“这一段在讲什么”
    F.topic = (t, text) => {
      const e = M.el('div', 'topic', topics, text, { fontSize: topicSize(text) });
      fx.in(e, t, { opacity: 0, y: 24 }, { opacity: 1, y: 0 }, 0.35, 'expo.out');
      if (curTopic) fx.to(curTopic, t, { opacity: 1, y: 0 }, { opacity: 0, y: -24 }, 0.25, 'power2.in');
      curTopic = e;
    };
    F.hudOff = (t) => fx.to(document.getElementById('hud'), t, { opacity: 1 }, { opacity: 0 }, 0.5);
    // 花字：关键词随旁白弹出 F.kw(text, t, { until, x, w, y, size, color, back, rot, sfx, gain })
    //   y 是花字顶边（默认 760，安全区中部）；x、w 是所占横向范围（默认整个安全区 60/860）；back 给一块宣纸底，压在画面上也不打架；同一时刻只放一个
    const kwLayer = document.getElementById('kw');
    F.kw = (text, t, o) => {
      o = Object.assign({ until: t + 1.6, x: 60, w: 860, y: 760, size: 180, color: C.red, back: true, rot: -3, sfx: 'impact', gain: 0.5 }, o || {});
      const n = [...String(text).replace(/<[^>]+>/g, '')].length, size = Math.min(o.size, Math.floor((o.w - 80) / Math.max(1, n)));
      const e = M.box(kwLayer, 'kw', o.x, o.y, `<span style="font-size:${size}px;color:${o.color};${o.back ? 'background:rgba(239,230,210,.95);box-shadow:0 12px 30px rgba(60,40,20,.2);' : 'text-shadow:0 6px 0 rgba(239,230,210,.95);'}">${text}</span>`, { w: o.w, rotate: o.rot + 'deg' });
      fx.in(e, t - 0.14, { opacity: 0, scale: 1.7 }, { opacity: 1, scale: 1 }, 0.2, 'power4.in');
      if (o.sfx) MR.sfx(o.sfx, t + 0.04, { gain: o.gain });
      if (o.until != null) fx.to(e, o.until, { opacity: 1, scale: 1 }, { opacity: 0, scale: 0.94 }, 0.22, 'power2.in');
      return e;
    };

    // ---------- 档案卡（悬浮在镜头世界之上，章节的“线索物”）----------
    F.dossier = (d) => {
      d = Object.assign({ title: '户 口 本', sub: '', seal: '', rows: [] }, d || {});
      const dos = document.getElementById('dossier'), veil = document.getElementById('veil');
      const CH = Math.min(860, Math.max(520, 250 + d.rows.length * 124));   // 卡片高度随栏目数
      const card = M.box(dos, 'card', 0, 0, '', { w: 840, h: CH });
      M.box(card, 'kai', 0, 40, d.title, { w: 840, textAlign: 'center', fontSize: '64px', letterSpacing: '6px' });
      if (d.sub) M.box(card, 'note', 0, 128, d.sub, { w: 840, textAlign: 'center' });
      const seal = d.seal ? M.seal(card, d.seal, { x: 690, y: 40, size: 92, rot: 6 }) : null;
      const rows = {};
      d.rows.forEach(([k, label], i) => {
        const r = M.box(card, 'row', 48, 190 + i * 124, `<div class="k">${label}</div><div class="v" style="color:var(--wash-2)">？</div>`, { h: 108 });
        rows[k] = { row: r, ph: M.q(r, '.v'), v: M.box(r, 'v', 150, 22, ''), i };
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
      api.mark = (k, t) => { // 红框圈住某一栏
        const hi = M.box(card, '', 30, 190 + rows[k].i * 124 - 6, '', { w: 780, h: 120, border: `5px solid ${C.red}`, borderRadius: '10px', boxSizing: 'border-box' });
        fx.in(hi, t, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1 }, 0.4, 'expo.out');
      };
      api.stamp = (text, t, o) => { const s = M.seal(card, text, Object.assign({ x: 640, y: CH - 170, size: 120, rot: -8 }, o || {})); fx.stamp(s, t); return s; };
      api.stampSeal = (t) => seal && fx.stamp(seal, t);
      return api;
    };

    // ---------- 收尾：字幕、声音、镜头呼吸、结尾停留、注册（试看窗口时只播一段）----------
    F.finish = () => {
      M.subtitles(tl, T, DATA.chunks, document.getElementById('subs'));
      camQ.sort((a, b) => a.t - b.t || a.i - b.i);
      const poseOf = (o) => {
        if (o.fit) { const P = S.panels[String(o.fit).replace('#p-', '')]; return { focus: [P.x + M.W / 2, P.y + M.H / 2], zoom: o.zoom || 1 }; }
        return { focus: o.focus, zoom: o.zoom };
      };
      const drifts = [];
      camQ.forEach((m, k) => {
        if (m.o.noDrift) return;
        const end = m.t + (m.o.duration == null ? 0.8 : m.o.duration);
        const next = camQ[k + 1] ? camQ[k + 1].t : T.last() + 1.0 + V.endHold;
        const gap = next - end;
        if (gap < 2.2) return;
        const p0 = poseOf(m.o), dy = [0, -14, 12][k % 3];
        drifts.push({ t: end + 0.05, o: { focus: [p0.focus[0], p0.focus[1] + dy], zoom: p0.zoom * 1.045, duration: gap - 0.15, ease: 'sine.inOut' }, i: m.i + 0.5 });
      });
      camQ.push(...drifts);
      camQ.sort((a, b) => a.t - b.t || a.i - b.i).forEach((m) => cam.to(tl, m.t, m.o));
      tl.to({}, { duration: V.endHold }, T.last() + 1.0);
      if (W) { const film = gsap.timeline({ paused: true }); film.add(tl.tweenFromTo(W[0], W[1], { ease: 'none' })); (window.__timelines = window.__timelines || {}).film = film; }
      else (window.__timelines = window.__timelines || {}).film = tl;
    };

    F.R = M.recipes(F);
    return F;
  };

  // =====================================================================
  // 配方：每个都在一个 panel（1080×1920）里搭好画面并挂上动画，全部排在安全区 x 60–920、y 360–1240 内
  //   水平中心 X = 490（避开右侧按钮列）；字号下限：标注 34px、地名 42px、正文 46px
  // =====================================================================
  M.recipes = function (F) {
    const { C, tl, fx, T } = F;
    const box = M.box, svg = M.svg, fig = F.fig;
    const A = M.SAFE, X = A.cx, L0 = A.x, LW = A.w;       // 安全区左边、宽度、水平中心
    const R = {};
    // 横向居中的一行字（在安全区里居中）
    const line = (p, cls, y, html, st) => box(p, cls, L0, y, html, Object.assign({ w: LW, textAlign: 'center', whiteSpace: 'nowrap' }, st || {}));

    // 大标题书写：R.title(p, { text, at, y, size, color, sub, subAt })
    R.title = (p, o) => {
      const y = o.y == null ? 380 : o.y, sz = o.size || 88;
      const e = line(p, 'kai', y, '', { fontSize: sz + 'px', color: o.color || C.ink });
      M.write(tl, M.chars(e, o.text), o.at, { dir: 'right', dur: 0.3, stagger: Math.min(0.12, 0.9 / [...o.text].length) });
      let s = null;
      if (o.sub) { s = line(p, 'note src', y + sz * 1.3, o.sub); fx.fade(s, o.subAt == null ? o.at + 0.4 : o.subAt); }
      return { el: e, sub: s };
    };
    // 出处小注：R.source(p, { text, at, y })
    R.source = (p, o) => { const e = line(p, 'note src', o.y == null ? 1186 : o.y, o.text, { fontSize: '32px' }); fx.fade(e, o.at); return e; };

    // 古地图：R.map(p, { region:{lon0,lon1,lat0,lat1}, box:{x,y,w,h}, layers:['coastEast','huangheLower','huaihe','changjiang'|'coast','huanghe','yangtze'],
    //   lakes:['poyang'], labels:[{text,lon,lat,size}], cities:[{key, at, label?, dx, dy}], marker:{key, at, label, sub, subAt}, drawAt })
    // 默认地图框 x 80–900、y 440–1180；河流裁在框内。返回 { pt(key|[lon,lat]) → panel 坐标, prj, frame }
    R.map = (p, o) => {
      const G = M.geo, B = Object.assign({ x: 80, y: 440, w: 820, h: 740 }, o.box || {});
      const prj = M.proj(Object.assign({ w: B.w, h: B.h }, o.region));
      const pt = (k) => { const ll = typeof k === 'string' ? G.city[k] : k; const [x, y] = prj(ll[0], ll[1]); return [B.x + x, B.y + y]; };
      const frame = box(p, '', B.x - 18, B.y - 18, '', { w: B.w + 36, h: B.h + 36, border: `4px solid ${C.ink}`, borderRadius: '8px', background: 'rgba(228,214,184,.55)' });
      const style = { coastEast: [C.ink2, 5], coast: [C.ink2, 5], huangheLower: [C.ink, 12], huanghe: [C.ink, 9], huaihe: [C.ink2, 8], changjiang: [C.ink, 13], yangtze: [C.ink, 9] };
      let inner = '';
      (o.layers || ['coastEast', 'huangheLower', 'huaihe', 'changjiang']).forEach((k) => {
        const [col, w] = style[k] || [C.ink2, 6];
        inner += `<path class="ly ly-${k}" pathLength="1" d="${prj.path(G[k])}" stroke="${col}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`;
      });
      (o.lakes || []).forEach((k) => { inner += `<path class="lake" d="${prj.path(G.lake[k], true)}" fill="${C.wash2}" stroke="${C.ink2}" stroke-width="3" opacity=".9"/>`; });
      const s = svg(p, B.x, B.y, B.w, B.h, inner); s.style.overflow = 'hidden';
      const t0 = o.drawAt;
      fx.in(frame, t0 - 0.3, { opacity: 0 }, { opacity: 1 }, 0.5);
      M.qa(s, '.ly').forEach((e, i) => fx.draw(e, t0 + i * 0.25, 1.5));
      M.qa(s, '.lake').forEach((e) => fx.fade(e, t0 + 0.6, 0.6));
      MR.sfx('draw', t0, { dur: 1.6, gain: 0.35 });
      (o.labels || []).forEach((l) => { const [x, y] = pt([l.lon, l.lat]); const e = box(p, 'kai', x, y, l.text, { fontSize: (l.size || 42) + 'px', color: C.ink2, whiteSpace: 'nowrap', letterSpacing: '4px' }); fx.fade(e, t0 + 0.8); });
      (o.cities || []).forEach((c, i) => {
        const [x, y] = pt(c.key);
        const d = box(p, '', x - 9, y - 9, '', { w: 18, h: 18, borderRadius: '50%', background: C.ink });
        const l = box(p, 'kai', x + (c.dx == null ? 14 : c.dx), y + (c.dy == null ? -58 : c.dy), c.label || G.name[c.key] || c.key, { fontSize: '46px', color: C.ink, whiteSpace: 'nowrap' });
        const t = c.at == null ? t0 + 0.8 + i * 0.12 : c.at;
        fx.pop(d, t, 0.4); fx.fade(l, t + 0.1);
      });
      let mk = null;
      if (o.marker) {
        const m = o.marker, [x, y] = pt(m.key);
        const ring = box(p, '', x - 46, y - 46, '', { w: 92, h: 92, borderRadius: '50%', border: `5px solid ${C.red}` });
        const dot = box(p, '', x - 16, y - 16, '', { w: 32, h: 32, borderRadius: '50%', background: C.red });
        const l = box(p, 'kai', x + 30, y - 80, m.label || G.name[m.key], { fontSize: '64px', color: C.red, whiteSpace: 'nowrap' });
        fx.pop(dot, m.at, 0.5, 0.3); MR.sfx('pop', m.at + 0.1, { note: 3 });
        fx.in(ring, m.at + 0.1, { scale: 0.2, opacity: 1 }, { scale: 1.6, opacity: 0 }, 1.2, 'expo.out');
        fx.rise(l, m.at + 0.05, 16);
        if (m.sub) { const s2 = box(p, 'note', x + 34, y - 2, m.sub, { fontSize: '36px' }); fx.fade(s2, m.subAt == null ? m.at + 0.5 : m.subAt); }
        mk = { x, y };
      }
      return { pt, prj, frame, svg: s, marker: mk, box: B };
    };
    // 行军路线：R.route(p, map, { pts:[key|[lon,lat]...], at, dur, color, label, labelAt, dashed })
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
      if (o.label) { const [x, y] = P[P.length - 1]; const l = box(p, 'chip', Math.min(x + 20, 760), y + 14, o.label, { fontSize: '40px', background: col }); fx.pop(l, o.labelAt == null ? o.at + dur : o.labelAt, 0.4); }
      return { path, dot };
    };
    // 火点（起义、战火）：R.fires(p, map, { pts:[...], years:['1351',…], at, gap, label, labelAt })
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
      if (o.label) { const l = box(p, 'chip', 520, 1110, o.label, { fontSize: '42px', background: C.red }); fx.pop(l, o.labelAt == null ? o.at + 0.3 : o.labelAt, 0.4); }
    };
    // 洪水 / 战火蔓延的墨晕（在地图框内）：R.spread(p, map, { key, at, dur, color, size })
    R.spread = (p, map, o) => {
      const B = map.box, [x, y] = map.pt(o.key), S = o.size || 660;
      const clip = box(p, '', B.x, B.y, '', { w: B.w, h: B.h, overflow: 'hidden' });
      p.insertBefore(clip, map.svg.nextSibling);
      const blob = box(clip, '', x - B.x - S / 2, y - B.y - S / 2, `<img src="${M.ink({ size: 700, seed: o.seed || 91, alpha: 0.42, n: 120, spread: 0.55, color: o.color || '30,45,60', rim: 0.5 })}" style="width:${S}px;height:${S}px">`);
      gsap.set(blob, { opacity: 0 });
      tl.fromTo(blob, { opacity: 0.9, scale: 0.05 }, { opacity: 0.9, scale: 1, duration: o.dur || 4, ease: 'power2.out', immediateRender: false }, o.at);
      MR.sfx('whoosh', o.at + 0.2, { gain: 0.5, dur: 1.5 });
      return blob;
    };

    // 时间轴接力（皇位、掌权者轮换）：R.relay(p, { title, titleAt, years:[y0,y1], seatAt,
    //   items:[{ name, sub, at, until, from, to, child, out:'fade'|'kick'|'fall'|'stay', outAt, color, segColor, segLabel, segAt }] })
    R.relay = (p, o) => {
      const TH = { x: X - 180, y: 470 };                  // 龙椅 360×400
      const glow = box(p, '', X - 350, TH.y - 60, '', { w: 700, h: 700, borderRadius: '50%', background: 'radial-gradient(circle, rgba(214,180,98,.45), rgba(214,180,98,0) 65%)' });
      const th = fig(p, TH.x, TH.y, 360, 400, M.goldDefs + M.throne(), 1.0);
      const t0 = o.items[0].at - 1.0, sa = o.seatAt == null ? t0 : o.seatAt;
      fx.in(th, sa, { opacity: 0, y: 40 }, { opacity: 1, y: 0 }, 0.6, 'expo.out'); fx.fade(glow, sa + 0.2, 0.8);
      MR.sfx('impact', sa + 0.3, { gain: 0.45 });
      if (o.title) R.title(p, { text: o.title, at: o.titleAt == null ? t0 : o.titleAt, y: 366, size: 76 });
      const [y0, y1] = o.years, AX = { x: 100, y: 1130, w: 780 };
      const yr = (y) => AX.x + ((y - y0) / (y1 - y0 + 0.5)) * AX.w;
      const ticks = []; for (let y = Math.ceil(y0); y <= y1; y++) ticks.push(y);
      const step = Math.max(1, Math.ceil(ticks.length / 7));
      const axis = svg(p, 0, AX.y - 40, M.W, 120, `<path pathLength="1" d="M${AX.x},40 L${AX.x + AX.w},40" stroke="${C.ink}" stroke-width="5" fill="none"/>` + ticks.filter((_, i) => i % step === 0).map((y) => `<path d="M${yr(y)},28 L${yr(y)},52" stroke="${C.ink}" stroke-width="5"/><text x="${yr(y)}" y="100" text-anchor="middle" font-family="LXGW WenKai" font-size="38" fill="${C.ink2}">${y}</text>`).join(''));
      fx.draw(M.q(axis, 'path'), t0 + 0.3, 0.8); fx.fade(axis, t0 + 0.3, 0.4);
      const punch = (t) => { const [wx, wy] = F.S.at(p.id.replace('p-', ''), M.W / 2, M.H / 2); F.camTo(t, { focus: [wx, wy], zoom: 1.07, duration: 0.12, ease: 'power3.out', noDrift: true }); F.camTo(t + 0.15, { focus: [wx, wy], zoom: 1.0, duration: 0.6, ease: 'power2.out' }); MR.sfx('hit', t, { gain: 0.55 }); };
      const seatBottom = TH.y + 340;
      const els = o.items.map((it, idx) => {
        const nextAt = o.items[idx + 1] ? o.items[idx + 1].at : Infinity;
        const sc = it.child ? 1.15 : 1.6;
        const e = fig(p, X - 60 * sc, seatBottom - 200 * sc, 120, 200, M.emperor(), sc, false, it.color || C.ink);
        gsap.set(e, { opacity: 0 });
        tl.fromTo(e, { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.25, immediateRender: false }, it.at - 0.15);
        punch(it.at - 0.15);
        const n = line(p, 'kai', 890, it.name, { fontSize: '88px' });
        const s2 = line(p, 'note', 1000, it.sub || '', { fontSize: '40px' });
        gsap.set([n, s2], { opacity: 0 });
        const until = Math.min(it.until == null ? it.at + 2.5 : it.until, nextAt - 0.34); // 名字先退场，下一位再登场，不重影
        tl.fromTo([n, s2], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.25, ease: 'expo.out', immediateRender: false }, it.at - 0.15);
        tl.fromTo([n, s2], { opacity: 1 }, { opacity: 0, duration: 0.15, immediateRender: false }, until);
        if (it.from != null) {
          const seg = box(p, '', yr(it.from), AX.y - 16, '', { w: Math.max(12, yr(it.to) - yr(it.from)), h: 32, background: it.segColor || C.ink2, transformOrigin: '0 50%', borderRadius: '4px' });
          fx.in(seg, it.segAt == null ? it.at : it.segAt, { scaleX: 0 }, { scaleX: 1 }, 0.4, 'power3.out');
          if (it.segLabel) { const l = box(p, 'note', yr(it.from) - 10, AX.y - 74, it.segLabel, { fontSize: '34px', color: it.segColor === C.red ? C.red : C.ink2 }); fx.fade(l, (it.segAt == null ? it.at : it.segAt) + 0.1, 0.3); }
        }
        const oa = it.outAt == null ? until : it.outAt;
        if (it.out === 'kick') { tl.fromTo(e, { x: 0, opacity: 1 }, { x: 700, opacity: 0, rotation: 25, duration: 0.35, ease: 'power3.in', immediateRender: false }, oa); MR.sfx('whip', oa + 0.1, { gain: 0.5 }); }
        else if (it.out === 'fall') { tl.fromTo(e, { color: C.ink }, { color: C.red, duration: 0.12, immediateRender: false }, oa); tl.fromTo(e, { opacity: 1, y: 0 }, { opacity: 0, y: 60, duration: 0.6, ease: 'power2.in', immediateRender: false }, oa + 0.4); MR.sfx('thud', oa + 0.05, { gain: 0.7 }); }
        else if (it.out !== 'stay') tl.fromTo(e, { opacity: 1 }, { opacity: 0, y: 30, duration: 0.5, immediateRender: false }, oa);
        return e;
      });
      return { throne: th, emperors: els, yr };
    };

    // 族谱 / 人物关系（竖排多列，每列最多 5 代）：R.tree(p, { cols:[{ head, headAt, nodes:[{ role, name, at, self, hi:'从第几个字起标红' }] }], hiAt })
    R.tree = (p, o) => {
      const n = o.cols.length, xs = o.cols.map((_, i) => L0 + (LW / (n + 1)) * (i + 1));
      const Y = [520, 685, 850, 1015, 1180], BH = 124;
      o.cols.forEach((c, ci) => {
        const x = xs[ci];
        const hd = box(p, 'kai', x - 160, 372, c.head, { w: 320, textAlign: 'center', fontSize: '60px', color: C.red, whiteSpace: 'nowrap' });
        fx.rise(hd, c.headAt == null ? c.nodes.find(Boolean).at - 0.4 : c.headAt, 16);
        c.nodes.forEach((nd, ni) => {
          if (!nd) return;
          const hiFrom = nd.hi == null ? 1 : nd.hi;
          const nm = nd.self ? nd.name : nd.name.slice(0, hiFrom) + '<span class="num">' + nd.name.slice(hiFrom) + '</span>';
          const b = box(p, '', x - 140, Y[ni] - BH / 2, `<div class="note" style="text-align:center;font-size:30px;line-height:1.2">${nd.role || ''}</div><div class="kai" style="text-align:center;font-size:62px;line-height:1.1;white-space:nowrap">${nm}</div>`, { w: 280, h: BH, border: `4px solid ${nd.self ? C.red : C.ink}`, borderRadius: '12px', background: '#f4ecda', boxSizing: 'border-box', paddingTop: '8px' });
          fx.drop(b, nd.at - 0.1, 40, 0.5);
          MR.sfx('pop', nd.at + 0.05, { note: ni + 1 + ci, gain: 0.4, pan: n > 1 ? (ci / (n - 1) - 0.5) : 0 });
          if (ni > 0 && c.nodes[ni - 1]) { const gap = Y[ni] - Y[ni - 1] - BH; const ln = svg(p, x - 3, Y[ni - 1] + BH / 2, 6, gap, `<path pathLength="1" d="M3,0 L3,${gap}" stroke="${C.ink2}" stroke-width="5" fill="none"/>`); fx.draw(M.q(ln, 'path'), nd.at - 0.25, 0.25); }
          if (o.hiAt != null || nd.hiAt != null) M.qa(b, '.num').forEach((e) => fx.to(e, (nd.hiAt == null ? o.hiAt + ni * 0.12 : nd.hiAt), { color: C.ink }, { color: C.red }, 0.3));
        });
      });
      return { xs, Y };
    };

    // 证伪：传说卷轴 + 史书翻查 + 朱印“查无此条” + 更可能的解释
    // R.refute(p, { question, qAt, kicker, claim, claimAt, extra, extraAt, checkAt, stamp:'查无此条', stampAt, source, alts:[{text,at}], conclusion, conclusionAt })
    R.refute = (p, o) => {
      if (o.question) { const q = line(p, 'kai', 366, o.question, { fontSize: '80px' }); fx.rise(q, o.qAt, 24); }
      const scroll = box(p, '', L0, 500, '', { w: LW, h: 380 });
      const paperS = box(scroll, '', 30, 0, '', { w: LW - 60, h: 380, background: '#f6eedc', border: `2px solid ${C.wash}`, boxShadow: '0 12px 30px rgba(60,40,20,.15)' });
      const rodL = box(scroll, '', 0, -20, '', { w: 34, h: 420, background: C.ink2, borderRadius: '10px' });
      const rodR = box(scroll, '', LW - 34, -20, '', { w: 34, h: 420, background: C.ink2, borderRadius: '10px' });
      const k = box(paperS, 'kai', 0, 44, o.kicker || '传说', { w: LW - 60, textAlign: 'center', fontSize: '46px', color: C.ink2 });
      const c = box(paperS, 'kai', 30, 116, o.claim, { w: LW - 120, textAlign: 'center', fontSize: '64px', lineHeight: 1.25 });
      const t = o.claimAt;
      fx.fade(scroll, t - 0.4, 0.2);
      fx.in(paperS, t - 0.4, { clipPath: 'inset(0 50% 0 50%)' }, { clipPath: 'inset(0 0% 0 0%)' }, 0.9, 'power3.out');
      fx.in(rodL, t - 0.4, { x: LW / 2 - 17 }, { x: 0 }, 0.9, 'power3.out'); fx.in(rodR, t - 0.4, { x: -(LW / 2 - 17) }, { x: 0 }, 0.9, 'power3.out');
      MR.sfx('paper', t - 0.3, { gain: 0.5 });
      fx.fade(k, t + 0.2); fx.rise(c, t + 0.3, 14);
      if (o.extra) { const e = box(paperS, 'note', 0, 290, o.extra, { w: LW - 60, textAlign: 'center' }); fx.rise(e, o.extraAt, 14); }
      const books = [0, 1, 2].map((i) => fig(p, 130 + i * 250, 940, 122, 150, M.iconBook(), 1.0));
      books.forEach((b, i) => { fx.drop(b, o.checkAt - 0.2 + i * 0.12, 40); tl.fromTo(b, { rotationY: 0 }, { rotationY: 180, duration: 0.4, ease: 'power2.inOut', yoyo: true, repeat: 3, immediateRender: false }, o.checkAt + 0.3 + i * 0.15); });
      MR.sfx('paper', o.checkAt + 0.2, { gain: 0.4 }); MR.sfx('paper', o.checkAt + 0.6, { gain: 0.35, pan: 0.4 });
      const lens = svg(p, 70, 930, 140, 140, `<circle cx="56" cy="56" r="42" fill="rgba(255,255,255,.25)" stroke="${C.ink}" stroke-width="10"/><path d="M88,88 L130,130" stroke="${C.ink}" stroke-width="16" stroke-linecap="round"/>`);
      fx.fade(lens, o.checkAt + 0.1, 0.3);
      tl.fromTo(lens, { x: 0 }, { x: 560, duration: 1.6, ease: 'sine.inOut', immediateRender: false }, o.checkAt + 0.2);
      const st = M.seal(p, o.stamp || '查无此条', { x: X - 230, y: 640, size: 150, zhu: true, rot: -10, row: true });
      fx.stamp(st, o.stampAt, 0.9);
      const alts = o.alts || [];
      if (alts.length) fx.to([...books, lens], alts[0].at - 0.3, { opacity: 1 }, { opacity: 0 }, 0.3);
      const W0 = LW / (alts.length + 1);
      alts.forEach((a, i) => { const e = box(p, 'tag', L0 + W0 * (i + 1) - 130, 940, a.text, { w: 260, textAlign: 'center', boxSizing: 'border-box' }); fx.pop(e, a.at - 0.05, 0.5); MR.sfx('pop', a.at, { note: i + 3, gain: 0.45 }); });
      if (o.conclusion) { const e = line(p, 'kai', 1050, o.conclusion, { fontSize: '66px', color: C.red }); fx.rise(e, o.conclusionAt, 16); }
      if (o.source) R.source(p, { text: o.source, at: o.stampAt + 0.5, y: 1186 });
      return { scroll, stamp: st };
    };

    // 上下对照：R.compare(p, { top:{ label, figure, scale, at, tag, tagAt }, bottom:{...}, keys:['牛','书','大官'],
    //   topMarks:[bool…], topAt:[t…], bottomMarks:[bool…], bottomAt:[t…], link:{ at, label } })
    R.compare = (p, o) => {
      box(p, '', L0, 800, '', { w: LW, h: 4, background: C.wash2 });
      const half = (h, y0) => {
        const f = fig(p, 70, y0 + 120, 400, 232, h.figure || M.buffalo(), h.scale || 1.05);
        const l = box(p, 'kai', 80, y0, h.label, { fontSize: '58px', whiteSpace: 'nowrap' });
        fx.rise(f, h.at - 0.3, 20); fx.fade(l, h.at);
        if (h.tag) { const t = box(p, 'tag', 520, y0 + 10, h.tag); fx.pop(t, h.tagAt == null ? h.at + 0.5 : h.tagAt, 0.5); }
        return f;
      };
      half(o.top, 400); half(o.bottom, 840);
      const marks = (x0, y, vals, times) => vals.map((ok, i) => {
        const e = box(p, '', x0 + i * 130, y, `<div class="note" style="text-align:center;font-size:40px;color:${C.ink}">${o.keys[i]}</div><div style="text-align:center;font:900 76px/1 var(--hei);color:${ok ? C.ink : C.red}">${ok ? '✓' : '✕'}</div>`, { w: 120 });
        fx.pop(e, times[i], 0.45); MR.sfx(ok ? 'ding' : 'thud', times[i] + 0.05, { note: 3 + i, gain: 0.4 });
        return e;
      });
      if (o.topMarks) marks(530, 580, o.topMarks, o.topAt);
      if (o.bottomMarks) marks(530, 1020, o.bottomMarks, o.bottomAt);
      if (o.link) { const lk = svg(p, 430, 470, 340, 80, `<path pathLength="1" d="M330,40 Q170,-10 10,40" stroke="${C.red}" stroke-width="6" fill="none"/>`); fx.draw(M.q(lk, 'path'), o.link.at, 0.6); if (o.link.label) { const c = box(p, 'chip', 520, 410, o.link.label, { fontSize: '38px', background: C.red }); fx.pop(c, o.link.at + 0.4, 0.45); } }
    };

    // 循环图（“一辈子就这样”）：R.cycle(p, { title, titleAt, nodes:[{ label, figure?:{svg,w,h,sc}, html?, at }], arrowsAt:[t…], spinAt, fadeAt })
    R.cycle = (p, o) => {
      if (o.title) { const t = line(p, 'kai', 370, o.title, { fontSize: '76px', color: C.ink }); fx.rise(t, o.titleAt, 16); }
      const RR = 260, ring = box(p, '', X - RR, 560, '', { w: RR * 2, h: RR * 2 });
      const n = o.nodes.length;
      o.nodes.forEach((nd, i) => {
        const a = -Math.PI / 2 + (i / n) * Math.PI * 2, cx = RR + Math.cos(a) * RR, cy = RR + Math.sin(a) * RR;
        let e, bw = 180, bh = 120;
        if (nd.figure) { bw = nd.figure.w * nd.figure.sc; bh = nd.figure.h * nd.figure.sc; e = fig(ring, cx - bw / 2, cy - bh / 2 - 24, nd.figure.w, nd.figure.h, nd.figure.svg, nd.figure.sc); }
        else e = box(ring, 'kai', cx - 120, cy - 70, nd.html || '', { w: 240, textAlign: 'center', fontSize: '52px', lineHeight: 1.15 });
        const lb = box(ring, 'chip', cx - 90, cy + bh / 2 - 10, nd.label, { w: 180, textAlign: 'center', fontSize: '40px', padding: '8px 0 10px' });
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

    // 数据计数卡：R.counters(p, { title, at, y, items:[{ label, value, unit, at, decimals }], source })
    R.counters = (p, o) => {
      const y = o.y == null ? 640 : o.y;
      const card = box(p, '', L0, y, '', { w: LW, h: 300, background: '#f4ecda', border: `4px solid ${C.ink}`, borderRadius: '12px', boxShadow: '0 14px 34px rgba(60,40,20,.15)' });
      box(card, 'kai', 36, 26, o.title || '', { fontSize: '50px', whiteSpace: 'nowrap' });
      const w = (LW - 72) / o.items.length;
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

    // 名目票据（一张张拍下，最后一张大票砸下）：R.slips(p, { title, titleAt, source, items:[{ name, why, at }], finale:{ name, sub, at, coins:true } })
    R.slips = (p, o) => {
      if (o.title) R.title(p, { text: o.title, at: o.titleAt, y: 366, size: 80, sub: o.source });
      const els = o.items.map((it, i) => {
        const x = i % 2 ? 500 : 80, y = 560 + Math.floor(i / 2) * 320;
        const e = box(p, '', x, y, `<div class="kai" style="font-size:80px;color:${C.red};text-align:center;margin-top:44px;white-space:nowrap">${it.name}</div><div class="note" style="text-align:center;margin-top:14px;font-size:38px;color:${C.ink}">${it.why || ''}</div>`, { w: 380, h: 270, background: '#f6eedc', border: `5px solid ${C.red}`, borderRadius: '10px', boxShadow: '0 10px 24px rgba(60,40,20,.15)', rotate: (i % 2 ? 3 : -3) + 'deg' });
        fx.in(e, it.at - 0.2, { opacity: 0, scale: 1.4, y: -30 }, { opacity: 1, scale: 1, y: 0 }, 0.3, 'power4.in');
        MR.sfx('paper', it.at + 0.08, { gain: 0.55, pan: i % 2 ? 0.3 : -0.3 });
        return e;
      });
      if (o.finale) {
        const f = o.finale;
        fx.to(els, f.at - 0.6, { opacity: 1 }, { opacity: 0.3 }, 0.4);
        const big = box(p, '', X - 360, 600, `<div class="kai" style="font-size:160px;color:${C.paper};text-align:center;margin-top:60px;white-space:nowrap">${f.name}</div><div class="kai" style="text-align:center;font-size:52px;color:${C.paper};margin-top:16px">${f.sub || ''}</div>`, { w: 720, h: 440, background: C.red, borderRadius: '12px', boxShadow: '0 20px 50px rgba(120,30,20,.35)' });
        fx.in(big, f.at - 0.25, { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1 }, 0.25, 'power4.in');
        MR.sfx('impact', f.at, { gain: 0.6 });
        if (f.coins !== false) {
          const r = MR.random(5);
          for (let i = 0; i < 16; i++) {
            const a = (i / 16) * Math.PI * 2, d = 340 + r() * 160;
            const c = fig(p, X - 40, 780, 100, 100, M.coin(), 0.8);
            gsap.set(c, { opacity: 0 });
            tl.fromTo(c, { opacity: 1, x: 0, y: 0, rotation: 0 }, { x: Math.cos(a) * d, y: Math.sin(a) * d * 0.7 + 180, rotation: r() * 720, duration: 1.3, ease: 'power2.out', immediateRender: false }, f.at + 0.02);
          }
          MR.sfx('count', f.at + 0.1, { dur: 0.9, gain: 0.4 });
        }
        return { slips: els, big };
      }
      return { slips: els };
    };

    // 大字砸下 + 一排印章（年份、天灾、罪名…）：R.slam(p, { text, sub, at, subAt, size, color, seals:[{ char, art?, at }], liftAt })
    R.slam = (p, o) => {
      const sz = Math.min(o.size || 320, Math.floor(LW / Math.max(1, [...o.text].length) * 1.15));
      const big = line(p, 'kai', 500, o.text, { fontSize: sz + 'px', color: o.color || C.red, lineHeight: 1 });
      fx.in(big, o.at - 0.2, { opacity: 0, scale: 2.4 }, { opacity: 1, scale: 1 }, 0.22, 'power4.in');
      MR.sfx('impact', o.at + 0.02, { gain: 0.85 }); MR.sfx('subdrop', o.at + 0.02, { gain: 0.8, dur: 1.6 });
      tl.fromTo(p, { x: 0 }, { x: 10, duration: 0.04, yoyo: true, repeat: 7, ease: 'none', immediateRender: false }, o.at + 0.02);
      let sub = null;
      if (o.sub) { sub = line(p, 'kai', 500 + sz + 30, o.sub, { fontSize: '72px' }); fx.rise(sub, o.subAt == null ? o.at - 1 : o.subAt, 16); }
      const seals = o.seals || [];
      if (seals.length) {
        const la = o.liftAt == null ? seals[0].at - 0.6 : o.liftAt;
        fx.to(big, la, { y: 0, scale: 1 }, { y: -150, scale: 0.55 }, 0.5, 'power3.inOut');
        if (sub) fx.to(sub, la, { y: 0, opacity: 1 }, { y: -300, opacity: 0 }, 0.4, 'power3.inOut');
        seals.forEach((s, i) => {
          const x = i % 2 ? 500 : 110, y = 640 + Math.floor(i / 2) * 300;
          const e = M.seal(p, s.char, { x, y, size: 180, rot: [-6, 4, -3, 6][i % 4] });
          fx.stamp(e, s.at + 0.05, 0.8);
          if (s.art) { const a2 = svg(p, x + 200, y + 24, 150, 130, s.art); fx.fade(a2, s.at + 0.15, 0.3); }
        });
      }
      return big;
    };

    // 金句（逐字书写 + 出处）：R.quote(p, { by, byAt, lines:[{ text, at, size, color }], attribution, attrAt })
    R.quote = (p, o) => {
      if (o.by) { const w = M.seal(p, o.by, { x: X - 60, y: 370, size: 120, rot: -4, zhu: true }); fx.stamp(w, o.byAt, 0.6); }
      let y = o.by ? 540 : 460;
      o.lines.forEach((l, i) => {
        const n = [...l.text].length, sz = Math.min(l.size || (i === 1 ? 130 : 96), Math.floor(LW / Math.max(1, n)));
        const e = line(p, 'kai', y, '', { fontSize: sz + 'px', color: l.color || (i === 1 ? C.red : C.ink) });
        M.write(tl, M.chars(e, l.text), l.at - 0.1, { dur: 0.3, stagger: 0.13, dir: 'right' });
        MR.sfx('draw', l.at, { dur: 0.8, gain: 0.4 });
        y += sz * 1.5;
      });
      const a = line(p, 'kai', y + 20, o.attribution || '——《明朝那些事儿》', { fontSize: '46px', color: C.gold });
      fx.rise(a, o.attrAt, 14);
    };

    // 片尾预告：R.endCard(p, { at, titleAt, hint, hintAt, question, questionAt })
    R.endCard = (p, o) => {
      const V = F.V;
      const nx = line(p, 'note', 380, '下 一 集', { fontSize: '44px', letterSpacing: '8px', color: C.ink2 });
      const no = box(p, 'chip', X - 130, 460, V.nextNo, { w: 260, textAlign: 'center', background: C.red, fontFamily: 'var(--kai)', fontWeight: 500, fontSize: '56px', padding: '14px 0 16px', letterSpacing: '6px' });
      const n = [...V.nextTitle].length, tsz = Math.min(280, Math.floor((LW - 20) / Math.max(1, n) - 12));
      const tt = line(p, 'kai', 580, '', { fontSize: tsz + 'px', lineHeight: 1, letterSpacing: '12px' });
      fx.fade(nx, o.at - 0.3); fx.drop(no, o.at - 0.1, 40, 0.5);
      M.write(tl, M.chars(tt, V.nextTitle), o.titleAt == null ? o.at + 0.3 : o.titleAt, { dur: 0.5, stagger: Math.min(0.3, 1.2 / n) });
      MR.sfx('draw', o.titleAt == null ? o.at + 0.3 : o.titleAt, { dur: 0.8, gain: 0.5 });
      const hy = 580 + tsz + 50;
      if (V.nextHint) { const h = line(p, 'kai', hy, V.nextHint, { fontSize: '56px', color: C.red }); fx.pop(h, o.hintAt == null ? o.at + 1.2 : o.hintAt, 0.5); }
      if (o.question) { const q = line(p, 'kai', hy + (V.nextHint ? 90 : 0), o.question, { fontSize: '60px', color: C.ink }); fx.rise(q, o.questionAt, 14); }
      const ser = line(p, 'kai', 1150, V.series, { fontSize: '44px', letterSpacing: '8px', color: C.ink2 });
      fx.fade(ser, (o.questionAt == null ? o.at + 1.5 : o.questionAt) + 0.6, 0.6);
      if (V.seal) { const sl = M.seal(p, V.seal, { x: 760, y: 1110, size: 100, rot: -6 }); fx.stamp(sl, F.T.last() + 0.2, 0.6); }
      MR.sfx('chime', F.T.last() + 0.4, { gain: 0.5 });
      svg(p, 0, 1250, M.W, 670, M.mountains(M.W, 670, 131, { layers: 2, top: 0.2 }));
    };

    // 横排朱印（一句判词）：R.verdict(p, { text, at, x, y, size, rot, zhu })
    R.verdict = (p, o) => { const s = M.seal(p, o.text, { x: o.x == null ? X - 190 : o.x, y: o.y == null ? 820 : o.y, size: o.size || 150, rot: o.rot == null ? -8 : o.rot, row: true, zhu: !!o.zhu }); fx.stamp(s, o.at, 0.9); return s; };

    // 剪影入场：R.figure(p, { svg, w, h, x, y, sc, flip, color, at, from:'rise'|'left'|'right'|'pop'|'none', walk:{ dx, dur } })
    //   首帧（第 0 秒）里的元素用 from:'none'：一开始就在，信息流首帧才是完整画面
    //   人物剪影建议 sc ≥ 1.6（高 320px 以上），手机上才看得清姿态
    R.figure = (p, o) => {
      const e = fig(p, o.x, o.y, o.w, o.h, o.svg, o.sc || 1, o.flip, o.color);
      if (o.from === 'left') fx.in(e, o.at, { x: -260, opacity: 0 }, { x: 0, opacity: 1 }, 1.0, 'power2.out');
      else if (o.from === 'right') fx.in(e, o.at, { x: 260, opacity: 0 }, { x: 0, opacity: 1 }, 1.0, 'power2.out');
      else if (o.from === 'pop') fx.pop(e, o.at, 0.5);
      else if (o.from !== 'none') fx.rise(e, o.at, 24);
      if (o.walk) { tl.fromTo(e, { x: 0 }, { x: o.walk.dx, duration: o.walk.dur, ease: 'none', immediateRender: false }, o.at + 0.6); tl.fromTo(e, { y: 0 }, { y: -6, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: Math.max(1, Math.floor(o.walk.dur / 0.45)), immediateRender: false }, o.at + 0.6); }
      return e;
    };
    // 远山地平线：R.land(p, { seed, y, ground })（地平线默认 y 1236，紧贴字幕带上沿）
    R.land = (p, o) => { o = o || {}; svg(p, 0, o.y == null ? 880 : o.y, M.W, 700, M.mountains(M.W, 700, o.seed || 12, { layers: 3, top: 0.14, amp: 0.2 })); if (o.ground !== false) box(p, '', 0, 1236, '', { w: M.W, h: 5, background: C.ink, opacity: 0.85 }); };

    return R;
  };
})();
