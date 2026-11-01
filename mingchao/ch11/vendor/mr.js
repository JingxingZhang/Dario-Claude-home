// 当年明月 · 运行时（MR）
// 页面里的“时间从哪来、镜头怎么走、声音落在哪”都在这里；渲染脚本（scripts/render.js 等）只认下面这个约定：
//   window.__timelines = { film: <暂停的 GSAP 时间线> }   画面完全由时间线时间决定（逐帧 seek，不靠真实时钟）
//   window.__mr.sound() → { hits: [{ name, at, gain, pan, note, dur }] }   动效音的落点，scripts/sound.py 据此合成
//   window.__mr.ready()  → Promise   字体、图片都就绪后才开始截帧
// 一切确定性：随机数有种子，弹簧是闭式解，镜头补间写成 fromTo。
(function () {
  const MR = (window.MR = window.MR || {});

  // GSAP 默认把 px 值取整（autoRound）：描边动画 stroke-dashoffset 1→0 会变成跳变、慢速平移会一顿一顿。全部关掉。
  if (window.gsap) gsap.defaults({ autoRound: false });

  // ---------- 变量：读 <html data-composition-variables> 的默认值，按声明的类型转换 ----------
  MR.vars = () => {
    let decl = [];
    try { decl = JSON.parse(document.documentElement.getAttribute('data-composition-variables') || '[]'); } catch (e) { decl = []; }
    const v = {};
    for (const d of decl) {
      if (!d || !d.id) continue;
      let x = d.default;
      if (d.type === 'number') x = Number(x);
      if (d.type === 'boolean') x = x === true || x === 'true';
      v[d.id] = x;
    }
    return v;
  };

  // ---------- 旁白逐词时间：narrate.py 写进 <script type="application/json" id="cues"> ----------
  let words = null;
  MR.words = () => {
    if (!words) {
      const node = document.getElementById('cues');
      words = node ? JSON.parse(node.textContent).words || [] : [];
    }
    return words.slice();
  };

  // ---------- 动效音：只记录落点，返回时间（动作和声音可以写在同一行）----------
  const hits = [];
  MR.sfx = function (name, at, opts) {
    const t = Number(at);
    if (!(t >= 0)) throw new Error(`MR.sfx('${name}') 需要 ≥ 0 的时间，收到 ${at}`);
    hits.push(Object.assign({}, opts || {}, { name: String(name), at: t }));
    return t;
  };

  // ---------- 弹簧缓动：bounce 是过冲量（0 不过冲，0.1 轻微，0.3 活泼），补间时长即稳定时间 ----------
  MR.spring = function (bounce) {
    const b = Math.min(0.9, Math.max(0, Number(bounce) || 0));
    const z = b <= 0 ? 1 : -Math.log(b) / Math.sqrt(Math.PI * Math.PI + Math.log(b) ** 2);
    const w = 6.9 / z;
    const f = (t) => {
      if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
      const wd = w * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
    };
    return (p) => (p <= 0 ? 0 : p >= 1 ? 1 : f(p));
  };

  // ---------- 有种子的随机数（mulberry32）：同一个种子，每次渲染都一样 ----------
  MR.random = function (seed) {
    let a = (Number(seed) || 1) >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  // ---------- 镜头：一个“世界”容器，镜头记焦点 (fx, fy) 和缩放（对数空间插值）----------
  //   const cam = MR.camera('#world', { width, height });
  //   cam.set({ fit: '#p-hook', pad: 0 });                         第一帧
  //   cam.to(tl, t, { fit: '#p-map', pad: 0, duration, ease })     移到某个格子（缩放使它铺满画面）
  //   cam.to(tl, t, { focus: [x, y], zoom: 1.2, duration, ease })  推近到世界坐标某点
  // 每一步都从“上一步声明的位置”出发（fromTo），所以 cam.to 必须按时间顺序调用（Ming.film 已排好序）。
  MR.camera = function (world, opts) {
    const o = opts || {};
    const el = typeof world === 'string' ? document.querySelector(world) : world;
    if (!el) throw new Error(`MR.camera：找不到 ${world}`);
    const root = document.querySelector('[data-composition-id]');
    const W = o.width || Number(root && root.getAttribute('data-width')) || 1920;
    const H = o.height || Number(root && root.getAttribute('data-height')) || 1080;
    el.style.transformOrigin = '0 0';
    const live = { fx: W / 2, fy: H / 2, lz: 0 };
    const apply = () => {
      const s = Math.exp(live.lz);
      el.style.transform = `translate(${W / 2 - s * live.fx}px, ${H / 2 - s * live.fy}px) scale(${s})`;
    };
    // 元素在世界里的坐标：只累加 offsetLeft/Top，不受当前镜头变换影响
    const box = (target) => {
      const t = typeof target === 'string' ? el.querySelector(target) || document.querySelector(target) : target;
      if (!t) throw new Error(`MR.camera：找不到 ${target}`);
      let x = 0, y = 0, n = t;
      while (n && n !== el) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
      return { x, y, w: t.offsetWidth, h: t.offsetHeight };
    };
    let plan = Object.assign({}, live);
    const pose = (p) => {
      const out = Object.assign({}, plan);
      if (p.fit) {
        const b = box(p.fit), pad = p.pad == null ? 80 : p.pad;
        out.fx = b.x + b.w / 2; out.fy = b.y + b.h / 2;
        out.lz = Math.log(p.zoom || Math.min(W / (b.w + 2 * pad), H / (b.h + 2 * pad)));
      } else {
        if (p.focus) { out.fx = p.focus[0]; out.fy = p.focus[1]; }
        if (p.zoom) out.lz = Math.log(p.zoom);
      }
      return out;
    };
    const cam = {
      set(p) { Object.assign(live, pose(p || {})); plan = Object.assign({}, live); apply(); return cam; },
      to(tl, at, p) {
        p = p || {};
        const target = pose(p);
        // 代理对象：补间写进来就立刻作用到世界上（逐帧 seek 时也生效，不依赖回调）
        const proxy = {};
        for (const k of Object.keys(target)) Object.defineProperty(proxy, k, { get: () => live[k], set: (v) => { live[k] = v; apply(); }, enumerable: true });
        tl.fromTo(proxy, Object.assign({}, plan), Object.assign({}, target, { duration: p.duration == null ? 0.8 : p.duration, ease: p.ease || 'power3.inOut', immediateRender: false }), Math.max(0, at));
        plan = target;
        return cam;
      },
      zoom: () => Math.exp(live.lz),
    };
    apply();
    return cam;
  };

  // ---------- 给渲染脚本的接口 ----------
  window.__mr = {
    sound: () => ({ hits: hits.slice() }),
    ready: async () => {
      if (document.fonts) {
        await Promise.all([...document.fonts].map((f) => f.load().catch(() => null)));
        await document.fonts.ready;
      }
      await Promise.all([...document.images].map((im) => (im.complete ? null : new Promise((r) => { im.onload = im.onerror = r; }))));
      return true;
    },
  };
})();
