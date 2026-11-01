#!/usr/bin/env node
// 导出静帧（关键帧、封面、知识卡）。
//   node still.js <章节目录|某个.html> --at 0,12.5,30 --out <目录>        → <目录>/<页面名>-<秒>s.png
//   node still.js <章节目录|某个.html> --at 158.5 --out <文件.png>         → 单张，直接写这个文件
'use strict';
const fs = require('fs'), path = require('path');
const { launch, open, parseTimes, args } = require('./lib/film');
(async () => {
  const A = args(process.argv.slice(2));
  if (!A._[0] || A.at === undefined) { console.error('用法：node still.js <章节目录|.html> --at 0,1.5 --out <目录或.png>'); process.exit(2); }
  const times = parseTimes(A.at);
  const browser = await launch();
  try {
    const f = await open(browser, A._[0]);
    const out = path.resolve(A.out || path.join(f.root, 'out', 'stills'));
    const single = /\.png$/i.test(out);
    if (single && times.length !== 1) throw new Error('--out 写成 .png 时只能导一个时间点');
    if (!single) fs.mkdirSync(out, { recursive: true }); else fs.mkdirSync(path.dirname(out), { recursive: true });
    const base = path.basename(f.html, '.html');
    for (const t of times) {
      await f.seek(Math.min(t, f.duration));
      const file = single ? out : path.join(out, `${base}-${t.toFixed(2)}s.png`);
      await f.page.screenshot({ path: file, type: 'png' });
      console.log('still   ', file);
    }
    console.log(`         ${f.width}×${f.height}，共 ${times.length} 张——发出去前先打开看一眼`);
    if (f.errors.length) console.log('⚠ 页面报错：\n  ' + f.errors.join('\n  '));
  } finally { await browser.close(); }
})().catch((e) => { console.error('✗ ' + e.message); process.exit(1); });
