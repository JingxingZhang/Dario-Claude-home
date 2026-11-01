// 当年明月 · 运行时（MR）：变量、弹簧缓动、种子随机数、字体就绪。
// 画面引擎在 banhua.js；渲染脚本（scripts/lib/film.js 等）只认：
//   window.__timelines.film = { duration(), time(t, suppress) }   （banhua.js 的 F.finish() 注册）
//   window.__mr.ready() → Promise                                 字体、图片都就绪后才开始截帧
(function () {
  const MR = (window.MR = window.MR || {});
  // GSAP 默认把 px 值取整：慢速平移会一顿一顿。关掉。
  if (window.gsap) gsap.defaults({ autoRound: false });

  // 变量：读 <html data-composition-variables> 的默认值，按声明的类型转换
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

  // 弹簧缓动：bounce 是过冲量（0 不过冲，0.1 轻微，0.3 活泼）
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

  // 有种子的随机数（mulberry32）
  MR.random = function (seed) {
    let a = (Number(seed) || 1) >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  window.__mr = {
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
