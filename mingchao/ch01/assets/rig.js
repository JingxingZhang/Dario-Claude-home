// 2.5D 骨骼角色：分件 + 正向运动学 + 二分光影（暗面 / 受光边，按光源方向逐帧计算）+ 墨线描边 + 二次运动。
// 一切由时间 t 决定（pose(t) 返回关节角度），逐帧渲染完全确定。
//   const r = Rig.human(parent, { look: Rig.LOOK.soldier, scale: 1, facing: 1 });
//   r.set({ x, y, angles: {...} }, light)   每帧调用
(function () {
  const Rig = (window.Rig = {});
  const NS = 'http://www.w3.org/2000/svg';
  let UID = 0;
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const D2R = Math.PI / 180;

  // ---------- 颜色 ----------
  const hex = (h) => { h = h.replace('#', ''); return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16)); };
  const toHex = (c) => '#' + c.map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('');
  Rig.mix = (a, b, k) => { const A = hex(a), B = hex(b); return toHex(A.map((v, i) => v + (B[i] - v) * k)); };
  Rig.shade = (c, k, tint) => Rig.mix(c, tint || '#0a1020', k);

  // ---------- 形状 ----------
  // 肢段：沿 +y，长 len，起点宽 w0、终点宽 w1，bulge 控制肌肉鼓起
  Rig.limb = (len, w0, w1, bulge) => {
    const b = bulge == null ? 0.6 : bulge, a = w0 / 2, c = w1 / 2;
    return `M${-a},0 C${-a - b * a * 0.5},${len * 0.3} ${-c - b * c * 0.3},${len * 0.7} ${-c},${len} A${c},${c} 0 0 0 ${c},${len} C${c + b * c * 0.3},${len * 0.7} ${a + b * a * 0.4},${len * 0.3} ${a},0 A${a},${a * 0.8} 0 0 0 ${-a},0 Z`;
  };
  // 躯干（向上，-y）：骨盆 → 腰 → 胸 → 肩，胸口略向前
  Rig.torsoShape = () => 'M-25,6 C-27,-20 -24,-40 -22,-52 C-30,-80 -34,-105 -30,-122 C-14,-132 18,-132 34,-120 C40,-100 36,-78 26,-54 C26,-38 28,-18 25,6 C10,12 -10,12 -25,6 Z';
  // 头（侧面朝右）：后脑圆、额、鼻、唇、下巴、颈
  Rig.headShape = () => 'M-6,4 C-16,0 -22,-14 -22,-30 C-22,-48 -10,-58 4,-58 C18,-58 26,-48 27,-36 L33,-24 L28,-21 L29,-15 C29,-10 25,-6 19,-5 C14,-2 8,4 4,6 Z';
  Rig.helmetShape = () => 'M-24,-30 C-25,-52 -10,-66 6,-66 C22,-66 31,-54 30,-38 L34,-35 L-4,-36 C-8,-30 -14,-22 -18,-12 L-27,-14 C-27,-20 -26,-26 -24,-30 Z';
  Rig.footShape = (len) => `M-9,-6 C-9,4 -6,10 0,10 L${len},10 C${len + 4},10 ${len + 4},2 ${len - 4},-2 C${len * 0.6},-6 ${len * 0.3},-12 0,-12 C-6,-12 -9,-10 -9,-6 Z`;
  Rig.handShape = () => 'M-9,-4 C-10,6 -6,14 2,14 C10,14 12,6 10,-2 C8,-8 -6,-10 -9,-4 Z';
  Rig.skirtShape = (len, w) => `M${-w / 2},0 L${w / 2},0 C${w / 2 + 6},${len * 0.5} ${w / 2 + 10},${len * 0.8} ${w / 2 + 8},${len} L${-w / 2 - 6},${len} C${-w / 2 - 8},${len * 0.7} ${-w / 2 - 6},${len * 0.4} ${-w / 2},0 Z`;
  Rig.plumeShape = (len, w) => `M${-w / 2},0 C${-w / 2 - 3},${len * 0.5} ${-w * 0.2},${len} 0,${len + 4} C${w * 0.2},${len} ${w / 2 + 3},${len * 0.5} ${w / 2},0 Z`;

  // ---------- 骨架 ----------
  // spec.bones: [{ name, parent, pivot:[x,y] }]（pivot 在父骨局部坐标）；spec.parts: [{ bone, d, pal, w, detail, z, outline }]
  // 渲染：每个部件一组 <g transform=matrix>，内有 底色 / 暗面(遮罩) / 细节(裁剪) / 受光边(遮罩) / 墨线
  Rig.build = (parent, spec, opt) => {
    const id = ++UID, root = el('g', {}, parent);
    if (opt.cls) root.setAttribute('class', opt.cls);
    const defs = el('defs', {}, root);
    const bones = {}; spec.bones.forEach((b) => (bones[b.name] = b));
    // 光影用 clipPath 嵌套（比 mask 快得多）：在部件形状里依次画
    //   受光边色（整块）→ 暗面色（形状向背光方向挪 r，只留下受光侧一条边）→ 底色（形状向光源挪 s，再裁到“背光挪 r”的形状里）
    const parts = spec.parts.slice().sort((a, b) => a.z - b.z).map((pt, i) => {
      const sid = `rs${id}_${i}`;
      el('path', { id: sid, d: pt.d }, defs);
      const cp = el('clipPath', { id: sid + 'c' }, defs); el('use', { href: '#' + sid }, cp);
      const cpR = el('clipPath', { id: sid + 'k' }, defs); const rimCut = el('use', { href: '#' + sid }, cpR);
      const g = el('g', {}, root);
      const inner = el('g', { 'clip-path': `url(#${sid}c)` }, g);
      const rim = el('use', { href: '#' + sid, fill: '#fff' }, inner);
      const sh = el('use', { href: '#' + sid, fill: pt.pal.shadow }, inner);
      const litG = el('g', { 'clip-path': `url(#${sid}k)` }, inner);
      const lit = el('use', { href: '#' + sid, fill: pt.pal.base }, litG);
      if (pt.detail) { const dg = el('g', {}, inner); dg.innerHTML = pt.detail; }
      if (pt.outline !== false) el('use', { href: '#' + sid, fill: 'none', stroke: '#07090d', 'stroke-width': pt.ow || 4.5, 'stroke-linejoin': 'round' }, g);
      if (pt.over) { const og = el('g', {}, g); og.innerHTML = pt.over; }
      return { pt, g, sh, lit, rimCut, rim };
    });
    const shadowEl = opt.ground ? el('ellipse', { rx: opt.ground, ry: opt.ground * 0.16, fill: 'rgba(0,0,0,.55)' }, root) : null;
    if (shadowEl) root.insertBefore(shadowEl, root.children[1]);
    const world = {};
    const api = {
      root, parts, world,
      // pose: { x, y, s, facing, angles:{bone:deg}, worldAngles:{bone:deg} }；light: { dx, dy, color, s, r, rimA }
      set(pose, light) {
        const s = pose.s || 1, fx = pose.facing || 1;
        const R0 = { a: s * fx, b: 0, c: 0, d: s, e: pose.x, f: pose.y, ang: 0 };
        const A = pose.angles || {}, WA = pose.worldAngles || {};
        for (const b of spec.bones) {
          const P = b.parent ? world[b.parent] : R0;
          const px = b.pivot ? b.pivot[0] : 0, py = b.pivot ? b.pivot[1] : 0;
          const e = P.a * px + P.c * py + P.e, f = P.b * px + P.d * py + P.f;
          let ang = (A[b.name] || 0) + (b.rest || 0);
          if (WA[b.name] != null) ang = WA[b.name] - P.ang;
          const totAng = P.ang + ang, r = ang * D2R, cs = Math.cos(r), sn = Math.sin(r);
          world[b.name] = { a: P.a * cs + P.c * sn, b: P.b * cs + P.d * sn, c: -P.a * sn + P.c * cs, d: -P.b * sn + P.d * cs, e, f, ang: totAng };
        }
        if (shadowEl) { shadowEl.setAttribute('cx', pose.x); shadowEl.setAttribute('cy', pose.groundY == null ? pose.y + 170 * s : pose.groundY); shadowEl.setAttribute('rx', opt.ground * s); shadowEl.setAttribute('ry', opt.ground * s * 0.16); }
        const L = light || { dx: 0.6, dy: -0.8, color: '#ffffff', s: 0.35, r: 3.5, rimA: 0.9 };
        const ln = Math.hypot(L.dx, L.dy) || 1, lx = L.dx / ln, ly = L.dy / ln;
        for (const P of parts) {
          const m = world[P.pt.bone];
          P.g.setAttribute('transform', `matrix(${m.a},${m.b},${m.c},${m.d},${m.e},${m.f})`);
          // 世界方向 → 部件局部方向（逆线性变换后归一化）
          const det = m.a * m.d - m.b * m.c, ix = (m.d * lx - m.c * ly) / det, iy = (-m.b * lx + m.a * ly) / det, il = Math.hypot(ix, iy) || 1;
          const ux = ix / il, uy = iy / il, sh = (P.pt.w || 30) * (L.s == null ? 0.35 : L.s), rr = L.r == null ? 3.5 : L.r;
          P.sh.setAttribute('transform', `translate(${-ux * rr},${-uy * rr})`);
          P.rimCut.setAttribute('transform', `translate(${-ux * rr},${-uy * rr})`);
          P.lit.setAttribute('transform', `translate(${ux * sh},${uy * sh})`);
          P.rim.setAttribute('fill', L.color);
        }
      },
    };
    return api;
  };

  // ---------- 造型（配色与装备）----------
  const P = (base, k, tint) => ({ base, shadow: Rig.shade(base, k == null ? 0.55 : k, tint) });
  const scales = (w, h, step, color) => { let s = ''; for (let y = -h; y < h; y += step) { s += `<path d="M${-w},${y} ` + Array.from({ length: Math.ceil((2 * w) / 9) }, (_, i) => `q4.5,6 9,0`).join(' ') + `" fill="none" stroke="${color}" stroke-width="1.6" transform="translate(${(y / step) % 2 ? 4.5 : 0},0)"/>`; } return s; };
  Rig.LOOK = {
    soldier: { skin: P('#b88660', 0.6), armor: P('#4a5560', 0.6), armorDark: P('#2f3840', 0.6), cloth: P('#8e2a1f', 0.55), leather: P('#4b3426', 0.6), metal: P('#8d98a0', 0.55), plume: P('#c8321e', 0.5), boot: P('#2a2420', 0.5), trim: '#c49a4a', scale: 'rgba(10,14,18,.55)', weapon: 'spear', helmet: true, cape: false, beard: false },
    general: { skin: P('#8a5e44', 0.6), armor: P('#262a30', 0.55), armorDark: P('#16191d', 0.5), cloth: P('#a5261a', 0.5), leather: P('#3a2a20', 0.6), metal: P('#b9c2c8', 0.5), plume: P('#d9381f', 0.45), boot: P('#1c1816', 0.5), trim: '#d9a64a', scale: 'rgba(200,160,80,.35)', weapon: 'sword', helmet: true, cape: true, beard: true },
    // 主帅：金褐甲、红披风、长髯（朱元璋、郭子兴这类；具体人物在章节里改配色区分）
    commander: { skin: P('#a77a58', 0.6), armor: P('#6b5232', 0.55), armorDark: P('#3e2f1e', 0.55), cloth: P('#9c2318', 0.5), leather: P('#3a2a20', 0.6), metal: P('#c9b27a', 0.5), plume: P('#d9381f', 0.45), boot: P('#1c1816', 0.5), trim: '#e6b85a', scale: 'rgba(40,24,10,.45)', weapon: null, helmet: true, cape: true, beard: true, longBeard: true },
    // 元军：青灰甲、无红缨
    yuan: { skin: P('#b0845e', 0.6), armor: P('#3d4a52', 0.6), armorDark: P('#27323a', 0.6), cloth: P('#2e4a5a', 0.55), leather: P('#4b3426', 0.6), metal: P('#7f8a90', 0.55), plume: null, boot: P('#2a2420', 0.5), trim: '#9a8a6a', scale: 'rgba(10,14,18,.55)', weapon: 'spear', helmet: true, cape: false, beard: true },
    // 文官 / 谋士：长袍、幞头、长须（李善长这类）
    scholar: { robe: true, skin: P('#c09070', 0.6), cloth: P('#2f4f5a', 0.55), clothDark: P('#22383f', 0.55), sash: P('#7a2a1a', 0.5), boot: P('#1c1816', 0.5), trim: '#c9a85a', hat: 'futou', beard: true, longBeard: true },
    // 百姓：粗布短褐、发髻
    civilian: { robe: true, short: true, skin: P('#b88660', 0.6), cloth: P('#6b5a44', 0.55), clothDark: P('#4c3f30', 0.55), sash: P('#3a2e22', 0.5), boot: P('#2a2420', 0.5), trim: '#8a7a5a', hat: 'bun', beard: false },
  };

  // ---------- 人 ----------
  Rig.human = (parent, opt) => {
    const L = opt.look, tr = L.trim;
    const b = [
      { name: 'root' },
      { name: 'torso', parent: 'root', pivot: [0, 0] },
      { name: 'head', parent: 'torso', pivot: [6, -128] },
      { name: 'plume0', parent: 'head', pivot: [4, -66] }, { name: 'plume1', parent: 'plume0', pivot: [0, 15] }, { name: 'plume2', parent: 'plume1', pivot: [0, 14] },
      { name: 'cape0', parent: 'torso', pivot: [-16, -116] }, { name: 'cape1', parent: 'cape0', pivot: [0, 40] }, { name: 'cape2', parent: 'cape1', pivot: [0, 38] }, { name: 'cape3', parent: 'cape2', pivot: [0, 36] },
      { name: 'uaB', parent: 'torso', pivot: [-4, -112] }, { name: 'faB', parent: 'uaB', pivot: [0, 58] }, { name: 'hdB', parent: 'faB', pivot: [0, 52] },
      { name: 'uaF', parent: 'torso', pivot: [8, -112] }, { name: 'faF', parent: 'uaF', pivot: [0, 58] }, { name: 'hdF', parent: 'faF', pivot: [0, 52] }, { name: 'weapon', parent: 'hdF', pivot: [0, 4] },
      { name: 'thB', parent: 'root', pivot: [-6, 4] }, { name: 'shB', parent: 'thB', pivot: [0, 80] }, { name: 'ftB', parent: 'shB', pivot: [0, 78] },
      { name: 'thF', parent: 'root', pivot: [8, 4] }, { name: 'shF', parent: 'thF', pivot: [0, 80] }, { name: 'ftF', parent: 'shF', pivot: [0, 78] },
      { name: 'skB', parent: 'root', pivot: [-12, -6] }, { name: 'skF', parent: 'root', pivot: [12, -6] },
    ];
    const back = (p) => ({ base: Rig.shade(p.base, 0.28), shadow: Rig.shade(p.shadow, 0.3) });
    if (L.robe) return Rig.robed(parent, opt, b, back);
    const armorDetail = `${scales(40, 140, 9, L.scale)}`;
    const torsoDetail = `${armorDetail}<rect x="-40" y="-48" width="80" height="13" fill="${L.leather.base}"/><rect x="-6" y="-49" width="13" height="15" rx="2" fill="${tr}"/><circle cx="12" cy="-92" r="13" fill="${L.metal.base}" stroke="${tr}" stroke-width="3"/><path d="M-30,-118 C-10,-108 14,-108 34,-118" stroke="${tr}" stroke-width="4" fill="none"/>`;
    const parts = [];
    const add = (bone, d, pal, w, z, extra) => parts.push(Object.assign({ bone, d, pal, w, z }, extra || {}));
    // 远侧（压暗）
    if (L.cape) { const cp = (len, a, b2) => `M${-a / 2},0 L${a / 2},0 L${b2 / 2},${len + 6} L${-b2 / 2},${len + 6} Z`; add('cape0', cp(42, 26, 34), back(L.cloth), 30, 0, { ow: 3.5 }); add('cape1', cp(40, 34, 40), back(L.cloth), 36, 0.1, { ow: 3.5 }); add('cape2', cp(38, 40, 44), back(L.cloth), 40, 0.2, { ow: 3.5 }); add('cape3', 'M-22,0 L22,0 L14,30 L4,22 L-6,36 L-14,24 L-24,34 Z', back(L.cloth), 40, 0.3, { ow: 3.5 }); }
    add('thB', Rig.limb(82, 34, 26), back(L.cloth), 30, 1);
    add('shB', Rig.limb(80, 25, 20), back(L.boot), 24, 1.1, { detail: `<rect x="-20" y="0" width="40" height="30" fill="${back(L.cloth).base}"/>` });
    add('ftB', Rig.footShape(30), back(L.boot), 18, 1.2);
    add('skB', Rig.skirtShape(66, 40), back(L.armorDark), 40, 1.3, { detail: scales(40, 80, 9, L.scale) });
    add('uaB', Rig.limb(60, 24, 20), back(L.armor), 22, 1.4, { detail: scales(20, 70, 9, L.scale) });
    add('faB', Rig.limb(54, 20, 16), back(L.leather), 18, 1.5);
    add('hdB', Rig.handShape(), back(L.skin), 18, 1.6);
    // 躯干、头
    add('torso', Rig.torsoShape(), L.armor, 60, 2, { detail: torsoDetail });
    add('head', Rig.headShape(), L.skin, 46, 3, { detail: `<path d="M22,-34 q5,-2 8,1" stroke="#07090d" stroke-width="3.2" fill="none"/>` + Rig.beard(L), over: `<path d="M17,-31 l6,-1" stroke="#ffe7b0" stroke-width="2.4" stroke-linecap="round"/>` });
    if (L.helmet) add('head', Rig.helmetShape(), L.metal, 48, 3.1, { detail: `<path d="M-28,-40 C-6,-44 14,-44 34,-38" stroke="${tr}" stroke-width="4" fill="none"/><path d="M6,-66 L6,-40" stroke="${Rig.shade(L.metal.base, 0.5)}" stroke-width="3"/>` });
    if (L.plume) { add('plume0', Rig.limb(20, 9, 15, 0.3), L.plume, 13, 3.22, { ow: 3 }); add('plume1', Rig.limb(19, 15, 16, 0.2), L.plume, 15, 3.21, { ow: 3 }); add('plume2', Rig.plumeShape(24, 16), L.plume, 14, 3.2, { ow: 3 }); }
    add('skF', Rig.skirtShape(68, 44), L.armorDark, 44, 3.5, { detail: scales(44, 80, 9, L.scale) + `<path d="M-24,0 L24,0" stroke="${tr}" stroke-width="5"/>` });
    // 近侧
    add('thF', Rig.limb(82, 36, 28), L.cloth, 32, 4);
    add('shF', Rig.limb(80, 26, 21), L.boot, 26, 4.1, { detail: `<rect x="-20" y="0" width="40" height="30" fill="${L.cloth.base}"/><path d="M-14,34 L14,34" stroke="${tr}" stroke-width="3"/>` });
    add('ftF', Rig.footShape(32), L.boot, 20, 4.2);
    // 兵器（在近侧手之下）
    if (L.weapon === 'spear') add('weapon', 'M-150,-3 L170,-3 L170,3 L-150,3 Z M170,-7 L206,0 L170,7 Z', { base: '#5a4030', shadow: '#2a1d16' }, 6, 4.5, { ow: 3, over: '<path d="M164,-9 C158,-2 158,2 164,9" stroke="#c8321e" stroke-width="5" fill="none"/>' });
    if (L.weapon === 'sword') add('weapon', 'M-26,-4 L4,-4 L4,4 L-26,4 Z M4,-12 L10,-12 L10,12 L4,12 Z M10,-5 L118,-3 L132,0 L118,3 L10,5 Z', L.metal, 10, 4.5, { ow: 3, over: '<path d="M14,-1 L118,-1" stroke="#ffffff" stroke-width="1.6" opacity=".7"/>' });
    add('uaF', Rig.limb(60, 27, 22), L.armor, 24, 5, { detail: scales(22, 70, 9, L.scale), over: `<path d="M-17,-6 C-16,14 16,14 17,-6 C10,-14 -10,-14 -17,-6 Z" fill="${L.armorDark.base}" stroke="#07090d" stroke-width="3.5"/><path d="M-14,4 C-4,10 4,10 14,4" stroke="${tr}" stroke-width="3" fill="none"/>` });
    add('faF', Rig.limb(54, 22, 18), L.leather, 20, 5.1, { detail: `<rect x="-14" y="20" width="28" height="28" fill="${L.metal.base}"/>` });
    add('hdF', Rig.handShape(), L.skin, 18, 5.2);
    return Rig.build(parent, { bones: b, parts }, opt);
  };

  // 胡须：短须 / 长髯
  Rig.beard = (L) => !L.beard ? '' : L.longBeard ? '<path d="M0,0 C8,8 18,4 24,-8 C22,8 16,26 8,40 C6,24 2,14 -4,6 Z" fill="#14100e"/>' : '<path d="M2,2 C10,6 20,0 24,-8 C20,-2 14,0 8,-2 Z" fill="#14100e"/>';
  // 长袍人物（文官、百姓）：宽袖、交领、腰带、长袍下摆；幞头或发髻
  Rig.robed = (parent, opt, b, back) => {
    const L = opt.look, tr = L.trim, parts = [];
    const add = (bone, d, pal, w, z, extra) => parts.push(Object.assign({ bone, d, pal, w, z }, extra || {}));
    const hem = L.short ? 70 : 128;
    const folds = (n, len) => Array.from({ length: n }, (_, i) => `<path d="M${-14 + i * 10},6 C${-12 + i * 10},${len * 0.4} ${-16 + i * 11},${len * 0.7} ${-14 + i * 11},${len}" stroke="${Rig.shade(L.cloth.base, 0.55)}" stroke-width="2.2" fill="none" opacity=".7"/>`).join('');
    add('thB', Rig.limb(82, 30, 24), back(L.cloth), 28, 1);
    add('shB', Rig.limb(80, 22, 18), back(L.clothDark), 22, 1.1);
    add('ftB', Rig.footShape(28), back(L.boot), 18, 1.2);
    add('skB', Rig.skirtShape(hem, 46), back(L.clothDark), 46, 1.3, { detail: folds(4, hem) });
    add('uaB', Rig.limb(60, 28, 36, 0.2), back(L.cloth), 30, 1.4);
    add('faB', Rig.limb(52, 38, 30, 0.1), back(L.cloth), 32, 1.5);
    add('hdB', Rig.handShape(), back(L.skin), 18, 1.6);
    add('torso', Rig.torsoShape(), L.cloth, 60, 2, { detail: `<path d="M-22,-124 C-6,-100 10,-80 24,-56" stroke="${Rig.shade(L.cloth.base, 0.6)}" stroke-width="10" fill="none"/><path d="M-22,-124 C-6,-100 10,-80 24,-56" stroke="${tr}" stroke-width="3" fill="none"/><rect x="-40" y="-52" width="80" height="14" fill="${L.sash.base}"/>${folds(3, -40).replace(/M(-?\d+),6/g, 'M$1,-40')}` });
    add('head', Rig.headShape(), L.skin, 46, 3, { detail: `<path d="M22,-34 q5,-2 8,1" stroke="#07090d" stroke-width="3.2" fill="none"/>` + Rig.beard(L), over: `<path d="M17,-31 l6,-1" stroke="#ffe7b0" stroke-width="2.4" stroke-linecap="round"/>` });
    if (L.hat === 'futou') add('head', 'M-22,-30 C-24,-52 -10,-64 6,-64 C20,-64 28,-54 27,-38 L-4,-38 C-8,-34 -14,-30 -20,-26 Z M-22,-40 L-46,-46 L-46,-38 L-22,-34 Z', { base: '#15171c', shadow: '#07080b' }, 44, 3.1);
    if (L.hat === 'bun') add('head', 'M-20,-36 C-22,-52 -8,-62 6,-60 C18,-58 24,-50 24,-40 L-4,-40 Z M-14,-60 C-18,-74 0,-78 4,-66 Z', { base: '#191410', shadow: '#0a0806' }, 40, 3.1);
    add('skF', Rig.skirtShape(hem, 50), L.clothDark, 50, 3.5, { detail: folds(4, hem) + `<path d="M-26,0 L26,0" stroke="${tr}" stroke-width="4"/>` });
    add('thF', Rig.limb(82, 32, 26), L.cloth, 30, 4);
    add('shF', Rig.limb(80, 23, 19), L.clothDark, 24, 4.1);
    add('ftF', Rig.footShape(30), L.boot, 20, 4.2);
    add('uaF', Rig.limb(60, 30, 38, 0.2), L.cloth, 32, 5);
    add('faF', Rig.limb(52, 40, 32, 0.1), L.cloth, 34, 5.1, { detail: `<path d="M-20,44 L20,44" stroke="${tr}" stroke-width="3"/>` });
    add('hdF', Rig.handShape(), L.skin, 18, 5.2);
    return Rig.build(parent, { bones: b, parts }, opt);
  };

  // ---------- 马（侧面朝右）----------
  Rig.horse = (parent, opt) => {
    const coat = P(opt.coat || '#4a2c1e', 0.6), dark = { base: Rig.shade(coat.base, 0.3), shadow: Rig.shade(coat.shadow, 0.3) }, mane = P(opt.mane || '#0c0a0a', 0.4), hoof = P('#2a2420', 0.5), tack = P('#7a2a1a', 0.5), gold = '#d9a64a';
    const b = [
      { name: 'body' },
      { name: 'neck', parent: 'body', pivot: [88, -34] }, { name: 'head', parent: 'neck', pivot: [8, -104] },
      { name: 'tail0', parent: 'body', pivot: [-120, -30] }, { name: 'tail1', parent: 'tail0', pivot: [0, 40] }, { name: 'tail2', parent: 'tail1', pivot: [0, 36] },
      { name: 'flB', parent: 'body', pivot: [70, 30] }, { name: 'flB2', parent: 'flB', pivot: [0, 70] }, { name: 'flB3', parent: 'flB2', pivot: [0, 62] },
      { name: 'hlB', parent: 'body', pivot: [-92, 18] }, { name: 'hlB2', parent: 'hlB', pivot: [0, 78] }, { name: 'hlB3', parent: 'hlB2', pivot: [0, 66] },
      { name: 'flF', parent: 'body', pivot: [84, 34] }, { name: 'flF2', parent: 'flF', pivot: [0, 70] }, { name: 'flF3', parent: 'flF2', pivot: [0, 62] },
      { name: 'hlF', parent: 'body', pivot: [-80, 22] }, { name: 'hlF2', parent: 'hlF', pivot: [0, 78] }, { name: 'hlF3', parent: 'hlF2', pivot: [0, 66] },
      { name: 'saddle', parent: 'body', pivot: [6, -52] },
    ];
    const hoofD = 'M-12,0 L12,0 L15,18 L-13,18 Z';
    const parts = [];
    const add = (bone, d, pal, w, z, extra) => parts.push(Object.assign({ bone, d, pal, w, z }, extra || {}));
    add('tail0', Rig.limb(42, 22, 26, 0.2), mane, 22, 0); add('tail1', Rig.limb(38, 26, 24, 0.2), mane, 24, 0.1); add('tail2', Rig.plumeShape(40, 24), mane, 22, 0.2);
    add('flB', Rig.limb(70, 34, 22), dark, 30, 1); add('flB2', Rig.limb(62, 18, 15, 0.2), dark, 16, 1.1); add('flB3', hoofD, hoof, 20, 1.2);
    add('hlB', Rig.limb(78, 46, 24), dark, 40, 1); add('hlB2', Rig.limb(66, 20, 15, 0.2), dark, 16, 1.1); add('hlB3', hoofD, hoof, 20, 1.2);
    add('body', 'M-130,-30 C-140,10 -112,52 -70,52 C-20,58 40,58 80,52 C116,46 128,10 116,-26 C100,-60 50,-62 0,-60 C-50,-58 -118,-66 -130,-30 Z', coat, 110, 2, { detail: `<path d="M-60,40 C-20,48 30,48 70,40" stroke="${Rig.shade(coat.base, 0.5)}" stroke-width="4" fill="none" opacity=".6"/>` });
    add('neck', 'M-42,16 C-46,-30 -36,-76 -16,-110 L30,-102 C40,-62 42,-20 44,20 Z', coat, 70, 2.1, { over: `<path d="M-18,-112 C-36,-86 -44,-54 -48,-20 C-38,-42 -34,-62 -26,-78 C-36,-52 -42,-30 -44,-4 C-30,-30 -24,-62 -16,-84 Z" fill="${mane.base}" stroke="#07090d" stroke-width="3"/>` });
    add('head', 'M-24,-8 C-30,-32 -10,-46 14,-40 L94,-12 C108,-6 110,14 96,22 L62,30 C40,32 8,24 -14,16 Z M-8,-38 L2,-66 L14,-38 Z', coat, 54, 2.2, { detail: `<path d="M-8,-26 L82,8" stroke="${tack.base}" stroke-width="6"/><circle cx="28" cy="-8" r="6" fill="${gold}"/><path d="M88,10 l10,0" stroke="#07090d" stroke-width="3"/>`, over: '<path d="M18,-22 l9,2" stroke="#ffe7b0" stroke-width="3" stroke-linecap="round"/>' });
    add('saddle', 'M-50,4 C-40,-12 40,-12 52,2 L46,28 L-44,28 Z', tack, 60, 2.3, { detail: `<path d="M-48,8 L50,8" stroke="${gold}" stroke-width="4"/>` });
    add('flF', Rig.limb(70, 36, 22), coat, 32, 3); add('flF2', Rig.limb(62, 18, 15, 0.2), coat, 16, 3.1); add('flF3', hoofD, hoof, 20, 3.2);
    add('hlF', Rig.limb(78, 48, 24), coat, 42, 3); add('hlF2', Rig.limb(66, 20, 15, 0.2), coat, 16, 3.1); add('hlF3', hoofD, hoof, 20, 3.2);
    return Rig.build(parent, { bones: b, parts }, opt);
  };

  // ---------- 动作（关节角度 = 时间的函数）----------
  const sin = Math.sin, cos = Math.cos, TAU = Math.PI * 2;
  const pos = (x) => Math.max(0, x);
  // 二次运动：链条每节比上一节晚一点、幅度衰减
  const chain = (A, names, t, base, amp, w, lag) => names.forEach((n, i) => { A[n] = (i === 0 ? base : 0) + amp * (1 + i * 0.4) * sin(w * t - i * lag); });
  // 持枪冲锋跑
  Rig.runSpear = (t, o) => {
    o = o || {}; const per = o.period || 0.52, f = (TAU * (t + (o.phase || 0))) / per;
    const A = {};
    A.torso = 16 + 3 * sin(f * 2);
    A.head = -14;
    A.thF = -34 * sin(f) - 6; A.shF = 14 + 58 * Math.pow(pos(sin(f - 1.1)), 1.3); A.ftF = -8 + 18 * sin(f - 0.4);
    A.thB = -34 * sin(f + Math.PI) - 6; A.shB = 14 + 58 * Math.pow(pos(sin(f + Math.PI - 1.1)), 1.3); A.ftB = -8 + 18 * sin(f + Math.PI - 0.4);
    A.uaF = -62 + 6 * sin(f); A.faF = -28;
    A.uaB = -18 + 10 * sin(f + Math.PI); A.faB = -86;
    A.skF = -A.torso * 0.6 - 10 + 10 * sin(f - 0.8); A.skB = -A.torso * 0.6 + 8 + 10 * sin(f + Math.PI - 0.8);
    chain(A, ['plume0', 'plume1', 'plume2'], t, 78, 10, 9, 0.9);
    return { angles: A, worldAngles: { weapon: 6 + 3 * sin(f) }, bob: -Math.abs(cos(f)) * 12 };
  };
  // 不跑动时红缨、披风的轻微飘动
  const idle = (A, t) => { chain(A, ['plume0', 'plume1', 'plume2'], t, 155, 5, 3, 0.9); chain(A, ['cape0', 'cape1', 'cape2', 'cape3'], t, 6, 3, 2.5, 0.8); };
  // 站立（呼吸起伏）
  Rig.stand = (t) => { const br = Math.sin(t * 2.2), A = { torso: 2 + br, head: -2 - br * 0.5, thF: -4, shF: 4, ftF: 0, thB: 4, shB: 4, ftB: 0, uaF: 8 + br, faF: -40, uaB: -4, faB: -14, skF: -2, skB: 2 }; idle(A, t); return { angles: A, worldAngles: { weapon: -86 }, bob: br * 1.5 }; };
  // 走路
  Rig.walk = (t, o) => {
    o = o || {}; const per = o.period || 1.0, f = (TAU * (t + (o.phase || 0))) / per, A = {};
    A.torso = 4; A.head = -3;
    A.thF = -22 * sin(f); A.shF = 6 + 34 * pos(sin(f - 1.3)); A.ftF = -4 + 10 * sin(f - 0.5);
    A.thB = -22 * sin(f + Math.PI); A.shB = 6 + 34 * pos(sin(f + Math.PI - 1.3)); A.ftB = -4 + 10 * sin(f + Math.PI - 0.5);
    A.uaF = 16 * sin(f); A.faF = -18; A.uaB = 16 * sin(f + Math.PI); A.faB = -18;
    A.skF = -6 + 5 * sin(f - 0.8); A.skB = 6 + 5 * sin(f + Math.PI - 0.8);
    chain(A, ['plume0', 'plume1', 'plume2'], t, 150, 6, 5, 0.9); chain(A, ['cape0', 'cape1', 'cape2', 'cape3'], t, 8, 4, 4, 0.8);
    A.faF = -40;
    return { angles: A, worldAngles: { weapon: -86 }, bob: -Math.abs(cos(f)) * 5 };
  };
  // 作揖：上身前倾，双手合于胸前
  Rig.bow = (t, k) => { k = k == null ? 1 : k; const A = { torso: 26 * k, head: 8 * k, thF: -6 * k, shF: 8 * k, thB: 2, shB: 6, uaF: -66 * k, faF: -64 * k, uaB: -58 * k, faB: -72 * k, skF: -14 * k, skB: -8 * k }; idle(A, t); return { angles: A, worldAngles: { weapon: -86 }, bob: 0 }; };
  // 训话 / 指向：上身略后仰，近侧手臂前伸指出
  Rig.address = (t) => { const s = Math.sin(t * 3), A = { torso: -4 + s, head: -10, thF: -10, shF: 6, thB: 8, shB: 6, uaF: -118 + 4 * s, faF: -8, uaB: -8, faB: -32, skF: 4, skB: 6 }; idle(A, t); return { angles: A, bob: 0 }; };
  // 骑乘（配合马的颠簸）；提剑前指
  Rig.rideSword = (t, o) => {
    o = o || {}; const per = o.period || 0.5, f = (TAU * t) / per;
    const A = {};
    A.torso = 10 + 5 * sin(f + 0.6); A.head = -10 - 3 * sin(f + 0.6);
    A.thF = -78; A.shF = 92; A.ftF = -20; A.thB = -74; A.shB = 90; A.ftB = -20;
    A.uaF = -112 + 6 * sin(f + 1.2); A.faF = -12;
    A.uaB = -40 + 4 * sin(f); A.faB = -70;
    A.skF = -55; A.skB = -40 + 6 * sin(f);
    chain(A, ['plume0', 'plume1', 'plume2'], t, 80, 10, 8, 0.9);
    chain(A, ['cape0', 'cape1', 'cape2', 'cape3'], t, 56, 9, 7, 0.8);
    return { angles: A, worldAngles: { weapon: -14 + 4 * sin(f + 1.2) }, bob: 0 };
  };
  // 马：跑步（四拍，前后腿相位错开）
  Rig.gallop = (t, o) => {
    o = o || {}; const per = o.period || 0.5, f = (TAU * t) / per;
    const leg = (ph, up, k) => [up * sin(f + ph) - 4, 10 + k * pos(sin(f + ph - 1.3)), -10 + 20 * pos(sin(f + ph - 1.8))];
    const A = {};
    A.body = -4 * sin(f + 0.5);
    A.neck = 48 + 6 * sin(f + 1.2); A.head = -16 + 7 * sin(f + 1.6);
    [['flF', 0], ['flB', 0.5], ['hlF', 2.6], ['hlB', 3.1]].forEach(([n, ph]) => {
      const hind = n[0] === 'h', [u, l, h3] = leg(ph, hind ? 30 : 36, hind ? -38 : 52);
      A[n] = hind ? -u : -u; A[n + '2'] = l; A[n + '3'] = h3;
    });
    chain(A, ['tail0', 'tail1', 'tail2'], t, 78, 8, 9, 0.8);
    return { angles: A, bob: -Math.abs(sin(f)) * 16, pitch: A.body };
  };
})();
