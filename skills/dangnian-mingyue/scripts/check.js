#!/usr/bin/env node
// MV 合成检查：页面报错、字体、歌曲数据、镜头覆盖、第 0 帧、副歌大字、版面冲突（撞署名/主题栏/字幕带）、元素印制耗时。
//   node check.js <章节目录> [--step 0.5]
// 输出 ✗（必须修）和 ⚠（导出那一刻看一眼再判断）；顺带写 out/shots.json（lyrics_md.py 用）。
'use strict';
const fs = require('fs'), path = require('path');
const { launch, open, args } = require('./lib/film');
const A = args(process.argv.slice(2));
const ROOT = path.resolve(A._[0] || '.');
const STEP = Number(A.step || 0.5);
(async () => {
  const browser = await launch();
  let bad = 0, warn = 0;
  const X = (m) => { bad++; console.log('✗ ' + m); }, Wn = (m) => { warn++; console.log('⚠ ' + m); }, OK = (m) => console.log('✓ ' + m);
  try {
    const f = await open(browser, ROOT);
    const p = f.page;
    if (f.errors.length) X('页面报错：' + f.errors.slice(0, 5).join(' | '));
    const fonts = await p.evaluate(() => [...document.fonts].map((x) => `${x.family} ${x.weight} ${x.status}`));
    const miss = fonts.filter((x) => !x.endsWith('loaded')); miss.length ? X('字体没加载：' + miss.join('、')) : OK(`字体 ${fonts.length} 个已加载`);
    const song = await p.evaluate(() => window.__bh.song());
    const shots = await p.evaluate(() => window.__bh.shots());
    OK(`歌曲 ${song.duration.toFixed(1)}s、${song.lines.length} 句、${song.sections.length} 段；镜头 ${shots.length} 个`);
    if (fs.existsSync(path.join(ROOT, 'assets', 'song.wav'))) {
      const d = Number(require('child_process').spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path.join(ROOT, 'assets', 'song.wav')]).stdout);
      Math.abs(d - song.duration) > 0.3 ? X(`音轨 ${d.toFixed(2)}s 和歌曲数据 ${song.duration.toFixed(2)}s 对不上：重跑 song_sync.py`) : OK('音轨时长与歌曲数据一致');
    } else Wn('还没有 assets/song.wav（示例歌或还没跑 song_sync.py）');
    if (!song.topics.length) Wn('没有主题栏（F.topic）'); else if (song.topics[0].t > 0.01) Wn('第 0 秒没有主题栏');
    // 镜头太短 / 太长
    for (const s of shots) { const d = s.t1 - s.t0; if (d < 0.6) Wn(`镜头 ${s.name} 只有 ${d.toFixed(2)}s`); if (d > 14) Wn(`镜头 ${s.name} 长 ${d.toFixed(1)}s（MV 里一镜别超过两句歌词，或者给它加镜头运动）`); }
    // 副歌要有大字
    for (const l of song.lines.filter((x) => x.chorus)) {
      const sh = shots.filter((s) => s.t0 < l.end && s.t1 > l.start);
      if (!sh.some((s) => s.type)) Wn(`副歌「${l.text}」（${l.start.toFixed(1)}s）没有大字排版（sh.type）`);
    }
    // 逐时刻采样
    const times = []; for (let t = 0; t < song.duration; t += STEP) times.push(+t.toFixed(3));
    const seen = new Map(); let slow = [];
    const hit = (b, r) => b[0] < r[0] + r[2] && b[2] > r[0] && b[1] < r[1] + r[3] && b[3] > r[1];
    for (const t of times) {
      const r = await p.evaluate((x) => window.__bh.report(x), t);
      if (!r.shots.length) { X(`${t.toFixed(1)}s 没有镜头（空画面）`); continue; }
      if (!r.els.length) Wn(`${t.toFixed(1)}s 镜头 ${r.shots.join('+')} 里没有可见元素`);
      if (t === 0 && r.els.some((e) => e.alpha < 0.99)) Wn('第 0 帧有半透明元素：第 0 帧就是横版封面，首帧元素别做淡入');
      for (const e of r.els) {
        if (e.ms > 1500) slow.push(`${e.name} ${Math.round(e.ms)}ms`);
        if (e.bg || e.alpha < 0.5) continue;
        const keys = [];
        if (hit(e.bbox, [1600, 0, 320, 170])) keys.push('右上角署名');
        if (r.topic && hit(e.bbox, [60, 40, 850, 140]) && e.kind === 'type') keys.push('主题栏');
        if (r.sub && e.bbox[3] > 900 && (e.kind === 'type' || e.bbox[1] > 700)) keys.push('字幕带');
        for (const k of keys) { const id = e.name + k; if (!seen.has(id)) { seen.set(id, t); Wn(`${t.toFixed(1)}s ${e.name}${e.text ? '「' + e.text + '」' : ''} 撞到${k}`); } }
      }
    }
    slow = [...new Set(slow)]; if (slow.length) Wn('印制很慢的元素（box 太大或 res 太高）：' + slow.slice(0, 6).join('、'));
    fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
    fs.writeFileSync(path.join(ROOT, 'out', 'shots.json'), JSON.stringify({ shots, song }, null, 1));
    console.log(`\n检查完：${bad} 个 ✗，${warn} 个 ⚠（镜头表写在 out/shots.json）`);
  } finally { await browser.close(); }
  process.exit(bad ? 1 : 0);
})().catch((e) => { console.error('✗ ' + e.message); process.exit(1); });
