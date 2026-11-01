// 当年明月 · 浏览器端公用：启动 Chromium（Playwright），打开一支片（index.html 或 cover.html），按时间 seek。
// 约定见 assets/runtime/mr.js：window.__timelines.<名字> 是暂停的 GSAP 时间线；window.__mr.ready() 等字体图片就绪。
'use strict';
const fs = require('fs'), path = require('path'), os = require('os');

function playwright() {
  const tries = ['playwright', 'playwright-core', path.join(os.homedir(), 'ming-node/node_modules/playwright'), path.join(os.homedir(), 'ming-node/node_modules/playwright-core')];
  for (const m of tries) { try { return require(m); } catch (e) { /* 下一个 */ } }
  throw new Error('找不到 Playwright：先跑 bash scripts/setup.sh');
}

async function launch() {
  const { chromium } = playwright();
  const args = ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text', '--allow-file-access-from-files', '--hide-scrollbars', '--mute-audio'];
  const exe = process.env.MING_CHROME || undefined;
  try { return await chromium.launch({ executablePath: exe, args }); }
  catch (e) {
    for (const p of ['/opt/pw-browsers/chromium']) if (fs.existsSync(p)) return chromium.launch({ executablePath: p, args });
    throw e;
  }
}

// 目标可以是章节目录（读 index.html）或某个 .html
function resolveHtml(target) {
  const t = path.resolve(target);
  if (fs.existsSync(t) && fs.statSync(t).isDirectory()) return path.join(t, 'index.html');
  return t;
}

function sizeOf(html) {
  const s = fs.readFileSync(html, 'utf8');
  const w = Number((s.match(/data-width="(\d+)"/) || [])[1] || 1920), h = Number((s.match(/data-height="(\d+)"/) || [])[1] || 1080);
  const fps = Number((s.match(/data-fps="(\d+)"/) || [])[1] || 30);
  return { width: w, height: h, fps };
}

async function open(browser, target) {
  const html = resolveHtml(target);
  if (!fs.existsSync(html)) throw new Error('找不到 ' + html);
  const { width, height, fps } = sizeOf(html);
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e && e.message || e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + html, { waitUntil: 'load' });
  await page.addStyleTag({ content: 'html,body{margin:0!important;overflow:hidden!important;background:#000}' });
  try { await page.waitForFunction(() => window.__timelines && Object.keys(window.__timelines).length > 0, null, { timeout: 30000 }); }
  catch (e) { throw new Error('页面没有注册时间线（window.__timelines）：' + (errors.join(' | ') || '检查 chapter.js 是否以 F.finish() 结尾')); }
  await page.evaluate(() => (window.__mr ? window.__mr.ready() : document.fonts.ready));
  const info = await page.evaluate(() => {
    const name = window.__timelines.film ? 'film' : Object.keys(window.__timelines)[0];
    window.__tlName = name;
    return { name, duration: window.__timelines[name].duration() };
  });
  const seek = (t) => page.evaluate((x) => { window.__timelines[window.__tlName].time(x, false); }, t);
  return { page, html, root: path.dirname(html), width, height, fps, duration: info.duration, errors, seek };
}

// --at 解析：逗号分隔的秒数
const parseTimes = (s) => String(s).split(',').map((x) => x.trim()).filter(Boolean).map(Number).filter((x) => isFinite(x));

// 简单参数解析：--key value / --flag
function args(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) { const k = a.slice(2); const v = argv[i + 1]; if (v === undefined || v.startsWith('--')) out[k] = true; else { out[k] = v; i++; } }
    else out._.push(a);
  }
  return out;
}

module.exports = { launch, open, resolveHtml, sizeOf, parseTimes, args };
