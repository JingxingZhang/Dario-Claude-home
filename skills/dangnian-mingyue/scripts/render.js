#!/usr/bin/env node
// 渲染成片：逐帧 seek 截图（多个页面并行）→ ffmpeg 编码 → 配上 assets/song.wav（song_sync.py 做的响度归一音轨）→ 按体积上限出最终 MP4。
//   node render.js <章节目录> [--workers 4] [--max-mb 100] [--crf 18] [--out 文件.mp4] [--draft] [--from 秒 --to 秒] [--silent] [--blur N]
//   --from/--to  只渲染其中一段（看效果用；音轨同步截取）
//   --silent     没有音轨也渲染（测试用；正式成片必须有 assets/song.wav）
//   --blur N     运动模糊：每帧拍 N 个子帧取平均；版画画面默认不用（1），镜头运动多时可用 2
//   --max-mb M   成品体积上限（MB，1 MB = 1,000,000 字节），默认读 index.html 变量 maxMB，没有就 100。
//                先按 CRF 画质编码并把码率封顶在上限以内；万一超了，自动改两遍编码压到上限的 92%
//   --draft      小样：不加模糊、快速编码（看节奏用）
//   --two-pass   直接用两遍编码压到上限的 92%（一般不需要，超限时会自动改用）
// 声音：整首歌就是音轨，不另配音、不加动效。
'use strict';
const fs = require('fs'), path = require('path'), os = require('os');
const { spawn, spawnSync } = require('child_process');
const { launch, open, args } = require('./lib/film');

const A = args(process.argv.slice(2));
const ROOT = path.resolve(A._[0] || '.');
const SK = path.resolve(__dirname, '..');
const draft = !!A.draft;
const BLUR = draft ? 1 : Math.max(1, Number(A.blur || 1));
const WORKERS = Math.max(1, Number(A.workers || Math.min(4, os.cpus().length)));
const CRF = Number(A.crf || (draft ? 23 : 18));
const run = (cmd, a, o) => { const r = spawnSync(cmd, a, Object.assign({ stdio: ['ignore', 'pipe', 'pipe'] }, o || {})); if (r.status !== 0) throw new Error(`${cmd} 失败：${String(r.stderr || '').slice(-800)}`); return String(r.stdout || ''); };
const probe = (f) => JSON.parse(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration,size', '-of', 'json', f])).format;
const mb = (b) => (b / 1e6).toFixed(1) + ' MB';
const t0 = Date.now(), el = () => ((Date.now() - t0) / 1000).toFixed(0) + 's';

function maxMB() {
  if (A['max-mb']) return Number(A['max-mb']);
  const s = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const m = s.match(/"id":"maxMB"[^}]*"default":\s*([\d.]+)/);
  return m ? Number(m[1]) : 100;
}

function nextOut() {
  if (A.out) return path.resolve(A.out);
  const base = path.basename(ROOT);
  fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
  let v = 1; while (fs.existsSync(path.join(ROOT, 'out', `${base}-v${v}.mp4`))) v++;
  return path.join(ROOT, 'out', `${base}-v${v}.mp4`);
}

function ensureSong() {
  const snd = path.join(ROOT, 'assets', 'song.wav');
  if (fs.existsSync(snd)) return snd;
  if (A.silent) { console.log('⚠ 没有 assets/song.wav：按 --silent 渲染无声版'); return null; }
  throw new Error('没有音轨 assets/song.wav：先跑 scripts/song_sync.py（测试可加 --silent）');
}

// 一个 worker：渲染帧 [a, b)，写一段中间视频
async function worker(browser, idx, a, b, fps, seg, size) {
  const f = await open(browser, ROOT);
  const cdp = await f.page.context().newCDPSession(f.page);
  const vf = BLUR > 1 ? ['-vf', `tmix=frames=${BLUR},select='eq(mod(n\\,${BLUR})\\,${BLUR - 1})',setpts=N/(${fps}*TB)`] : [];
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(fps * BLUR), '-i', '-', ...vf,
    '-r', String(fps), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10', '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'ignore', 'pipe'] });
  let ffErr = ''; ff.stderr.on('data', (d) => { ffErr += d; });
  const done = new Promise((res, rej) => ff.on('close', (c) => (c === 0 ? res() : rej(new Error('ffmpeg 段编码失败：' + ffErr.slice(-500))))));
  const write = (buf) => new Promise((res) => { if (ff.stdin.write(buf)) res(); else ff.stdin.once('drain', res); });
  for (let k = a; k < b; k++) {
    for (let j = 0; j < BLUR; j++) {
      const t = BLUR > 1 ? Math.max(0, (k - ((BLUR - 1 - j) / (BLUR - 1)) * 0.5) / fps) : k / fps;
      await f.seek(Math.min(t, f.duration));
      const shot = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 94, optimizeForSpeed: true });
      await write(Buffer.from(shot.data, 'base64'));
    }
    if (idx === 0 && (k - a) % Math.max(1, Math.floor((b - a) / 10)) === 0) process.stdout.write(`frames   ${Math.round(((k - a) / (b - a)) * 100)}%（${el()}）\n`);
  }
  ff.stdin.end();
  await done;
  if (f.errors.length) console.log(`⚠ worker ${idx} 页面报错：` + f.errors.slice(0, 3).join(' | '));
  await f.page.close();
}

(async () => {
  if (!fs.existsSync(path.join(ROOT, 'index.html'))) throw new Error('不是章节目录：' + ROOT);
  const snd = ensureSong();
  const browser = await launch();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ming-render-'));
  try {
    const probeF = await open(browser, ROOT);
    const { fps, width, height } = probeF; const D = probeF.duration;
    if (probeF.errors.length) console.log('⚠ 页面报错：' + probeF.errors.slice(0, 5).join(' | '));
    await probeF.page.close();
    const T0 = Math.max(0, Number(A.from || 0)), T1 = Math.min(D, Number(A.to || D)), DD = T1 - T0;
    const F0 = Math.round(T0 * fps), N = Math.ceil(T1 * fps) - F0;
    const cap = maxMB();
    console.log(`render   ${path.basename(ROOT)}  ${width}×${height} ${fps}fps  ${T0.toFixed(1)}–${T1.toFixed(1)}s = ${N} 帧  模糊×${BLUR}  并行 ${WORKERS}  上限 ${cap} MB`);
    const per = Math.ceil(N / WORKERS), segs = [], jobs = [];
    for (let i = 0; i < WORKERS; i++) {
      const a = F0 + i * per, b = Math.min(F0 + N, a + per);
      if (a >= b) break;
      const seg = path.join(tmp, `seg${i}.mp4`); segs.push(seg);
      jobs.push(worker(browser, i, a, b, fps, seg, { width, height }));
    }
    await Promise.all(jobs);
    console.log(`frames   完成（${el()}）`);
    const list = path.join(tmp, 'list.txt');
    fs.writeFileSync(list, segs.map((s) => `file '${s}'`).join('\n'));
    const video = path.join(tmp, 'video.mp4');
    run('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]);

    // 最终编码：H.264 High + AAC 192k，+faststart（抖音、微信都能直接播）
    const out = nextOut();
    const ABR = 192000, limit = cap * 1e6;
    const capKbps = Math.floor(((limit * 0.96 * 8) / DD - ABR) / 1000);
    if (capKbps < 300) throw new Error(`体积上限 ${cap} MB 对 ${DD.toFixed(0)} 秒的片子太小（视频码率只剩 ${capKbps} kbps）`);
    const audio = snd && fs.existsSync(snd) ? ['-ss', T0.toFixed(3), '-i', snd] : [];
    const amap = audio.length ? ['-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000'] : ['-map', '0:v:0'];
    const common = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(fps), '-movflags', '+faststart', '-t', DD.toFixed(3)];
    const preset = draft ? 'veryfast' : 'slow';
    const vCap = capKbps < 40000 ? ['-maxrate', `${capKbps}k`, '-bufsize', `${capKbps * 2}k`] : [];
    run('ffmpeg', ['-v', 'error', '-y', '-i', video, ...audio, ...amap, ...common, '-preset', preset, '-crf', String(CRF), ...vCap, out]);
    let info = probe(out);
    if (A['two-pass'] || Number(info.size) > limit * 0.99) {
      const br = Math.floor(capKbps * 0.92);
      console.log(`size     ${A['two-pass'] ? '按要求' : `CRF 编码 ${mb(info.size)} 超过上限，`}改用两遍编码（${br} kbps）…`);
      const pl = path.join(tmp, 'x264');
      run('ffmpeg', ['-v', 'error', '-y', '-i', video, '-map', '0:v:0', ...common, '-preset', preset, '-b:v', `${br}k`, '-pass', '1', '-passlogfile', pl, '-an', '-f', 'null', '/dev/null']);
      run('ffmpeg', ['-v', 'error', '-y', '-i', video, ...audio, ...amap, ...common, '-preset', preset, '-b:v', `${br}k`, '-maxrate', `${capKbps}k`, '-bufsize', `${capKbps * 2}k`, '-pass', '2', '-passlogfile', pl, out]);
      info = probe(out);
    }
    const ok = Number(info.size) <= limit;
    console.log(`done     ${out}`);
    console.log(`         ${Number(info.duration).toFixed(2)}s  ${mb(info.size)}（上限 ${cap} MB ${ok ? '✓' : '✗'}）  用时 ${el()}`);
    if (!ok) process.exitCode = 1;
  } finally {
    await browser.close();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
})().catch((e) => { console.error('✗ ' + e.message); process.exit(1); });
