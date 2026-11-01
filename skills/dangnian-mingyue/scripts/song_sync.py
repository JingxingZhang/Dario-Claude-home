#!/usr/bin/env python3
"""歌曲对齐：用户下载的 mp3 + Suno 的逐字歌词时间 + 节拍分析 → 歌曲数据（写进 index.html 的 #song）、响度归一的音轨、字幕。
  python3 -I song_sync.py <章节目录> --mp3 <歌曲.mp3>
      [--alignment tools/suno-alignment.json] [--analysis tools/suno-analysis.json]
      [--lyrics tools/lyrics.txt] [--display tools/lyrics-display.txt] [--force] [--no-audio]

输入（第 B1 步由 Claude 用 Suno MCP 拉下来存好）：
  tools/suno-alignment.json   audio-lyrics-alignment 的原样返回（status 必须是 complete）
  tools/suno-analysis.json    audio-analysis 的原样返回（beats、bpm、sections；没有也能跑，只是没有节拍）
  tools/lyrics.txt            交给 Suno 的歌词（带 [Verse] [Refrain] 这类段落标签；唱的版本）
  tools/lyrics-display.txt    字幕显示版（可选；和 lyrics.txt 逐行对应、每行字数相同，只换多音字的写法）
输出：
  tools/song.json、index.html 里的 <script id="song">、assets/song.wav（−14 LUFS、真峰值 −1.5 dBTP）、out/subtitles.srt
检查：mp3 时长和 Suno 记录的时长差 > 0.5 秒就报错（多半下错了歌或被剪过；确认无误用 --force）。"""
import json, os, re, subprocess, sys

args = sys.argv[1:]
if not args or args[0].startswith('-'): sys.exit(__doc__)
ROOT = os.path.abspath(args[0])
def opt(k, d=None):
    return args[args.index(k) + 1] if k in args else d
P = lambda *a: os.path.join(ROOT, *a)
mp3 = opt('--mp3'); force = '--force' in args; no_audio = '--no-audio' in args
f_align = opt('--alignment', P('tools', 'suno-alignment.json')); f_ana = opt('--analysis', P('tools', 'suno-analysis.json'))
f_lyr = opt('--lyrics', P('tools', 'lyrics.txt')); f_disp = opt('--display', P('tools', 'lyrics-display.txt'))
if not os.path.exists(P('index.html')): sys.exit(f'✗ 不是章节目录：{ROOT}')
if not os.path.exists(f_align): sys.exit(f'✗ 没有逐字时间：{f_align}（先用 Suno MCP 的 audio-lyrics-alignment 拉下来存成这个文件）')
bad = 0
def ok(msg): print('✓ ' + msg)
def warn(msg): print('⚠ ' + msg)
def err(msg):
    global bad; bad += 1; print('✗ ' + msg)

align = json.load(open(f_align, encoding='utf-8'))
if align.get('status') not in (None, 'complete'): sys.exit(f"✗ 逐字时间还没好（status={align.get('status')}）：等一会儿再拉一次")
ana = json.load(open(f_ana, encoding='utf-8')) if os.path.exists(f_ana) else {}
suno = json.load(open(P('tools', 'suno.json'), encoding='utf-8')) if os.path.exists(P('tools', 'suno.json')) else {}

# ---------- 时长核对 ----------
def probe(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True)
    return float(r.stdout.strip())
dur_mp3 = probe(mp3) if mp3 else None
dur_ref = ana.get('duration_s') or (suno.get('duration') if suno else None)
if mp3 and not os.path.exists(mp3): sys.exit(f'✗ 找不到 mp3：{mp3}')
if dur_mp3 and dur_ref:
    d = abs(dur_mp3 - float(dur_ref))
    if d > 0.5 and not force: sys.exit(f'✗ mp3 时长 {dur_mp3:.2f}s 和 Suno 记录的 {float(dur_ref):.2f}s 差 {d:.2f}s：多半不是同一首或被剪过（确认无误加 --force）')
    ok(f'时长核对：mp3 {dur_mp3:.2f}s ≈ Suno {float(dur_ref):.2f}s')
duration = dur_mp3 or float(dur_ref or 0)

# ---------- 段落标签 ----------
TAGS = [(r'^intro', '前奏', False), (r'^pre-?chorus', '导歌', False), (r'^final (refrain|chorus|hook)', '最后的副歌', True), (r'^(refrain|chorus|hook)', '副歌', True),
        (r'^verse\s*(\d+)?', '主歌', False), (r'^bridge', '桥段', False), (r'^(instrumental|break|interlude|solo)', '间奏', False), (r'^outro|^end', '尾奏', False)]
def tag_info(tag):
    t = tag.strip().lower()
    for pat, label, ch in TAGS:
        m = re.match(pat, t)
        if m:
            if label == '主歌' and m.group(1): label += m.group(1)
            return label, ch
    return tag.strip(), False

# ---------- 解析逐字时间 → 行 ----------
is_lyric = lambda c: not c.isspace() and c not in '[]'
lines, cur, tag, tag_events = [], None, None, []
prev_end = 0.0
def new_line():
    global cur
    cur = {'tag': tag, 'chars': []}; lines.append(cur)
def put(c, s, e):
    if cur is None or (cur['chars'] and cur.get('closed')): new_line()
    cur['chars'].append({'c': c, 's': s, 'e': e})
for w in align.get('words', []):
    text, s, e = w.get('word', ''), float(w.get('start_s', 0)), float(w.get('end_s', 0))
    segs = text.split('\n')
    for si, seg in enumerate(segs):
        if si > 0:  # 换行：结束当前行
            if cur is not None and cur['chars']: cur['closed'] = True
        m = re.fullmatch(r'\s*\[([^\]]*)\]\s*', seg)
        if m:
            tag = m.group(1); tag_events.append({'tag': tag, 'after': prev_end, 'line_index': len([l for l in lines if l['chars']])}); cur = None; continue
        chars = list(seg)
        lyr = [c for c in chars if is_lyric(c)]
        if not lyr:
            if chars and cur is not None and cur['chars'] and not cur.get('closed'): cur['chars'].append({'c': ' ', 's': None, 'e': None})
            continue
        # 时间：没有换行的整词就在 [s, e]；带换行时，第一个换行前的字是上一行的尾巴，放在上一个字之后
        if len(segs) > 1 and si == 0:
            a, b = prev_end, max(prev_end + 0.05, min(prev_end + 0.35, s))
        else:
            a, b = s, max(e, s + 0.05)
        n = len(lyr); k = 0
        for c in chars:
            if c.isspace():
                if cur is not None and cur['chars'] and not cur.get('closed') and cur['chars'][-1]['c'] != ' ': cur['chars'].append({'c': ' ', 's': None, 'e': None})
                continue
            if c in '[]': continue
            cs, ce = a + (b - a) * k / n, a + (b - a) * (k + 1) / n
            if cur is None or cur.get('closed'): new_line()
            cur['chars'].append({'c': c, 's': round(cs, 3), 'e': round(ce, 3)}); k += 1
        prev_end = b
lines = [l for l in lines if any(c['s'] is not None for c in l['chars'])]
for l in lines:
    while l['chars'] and l['chars'][-1]['c'] == ' ': l['chars'].pop()
    while l['chars'] and l['chars'][0]['c'] == ' ': l['chars'].pop(0)
    l.pop('closed', None)
if not lines: sys.exit('✗ 逐字时间里没有歌词（是纯音乐吗？）')

# ---------- 显示版 ----------
def lyric_lines(f):
    if not os.path.exists(f): return None
    out = []
    for raw in open(f, encoding='utf-8'):
        t = raw.strip()
        if not t or re.fullmatch(r'\[[^\]]*\]', t): continue
        out.append(t)
    return out
strip = lambda s: re.sub(r'[\s　，。、！？,.!?；;：:“”"‘’（）()·…—-]', '', s)
sung = lyric_lines(f_lyr); disp = lyric_lines(f_disp)
if sung is not None and len(sung) != len(lines): warn(f'lyrics.txt 有 {len(sung)} 行，逐字时间里有 {len(lines)} 行：按逐字时间为准（检查 Suno 拿到的是不是这份歌词）')
out_lines = []
for i, l in enumerate(lines):
    text = ''.join(c['c'] for c in l['chars'])
    display = text.replace(' ', '　')
    chars = [{'c': ('　' if c['c'] == ' ' else c['c']), 's': c['s'], 'e': c['e']} for c in l['chars']]
    if disp and i < len(disp):
        d = disp[i].replace(' ', '　')
        if len(strip(d)) == len(strip(text)):
            src = [c for c in chars if c['s'] is not None]; j = 0; nc = []
            for ch in d:
                if strip(ch): nc.append({'c': ch, 's': src[j]['s'], 'e': src[j]['e']}); j += 1
                else: nc.append({'c': ch, 's': None, 'e': None})
            display, chars = d, nc
        else: warn(f'第 {i + 1} 句显示版字数不同，用唱的版本：「{text}」 vs 「{d}」')
    ts = [c['s'] for c in chars if c['s'] is not None]; te = [c['e'] for c in chars if c['e'] is not None]
    label, chorus = tag_info(l['tag'] or '')
    out_lines.append({'i': i + 1, 'tag': l['tag'] or '', 'label': label, 'chorus': chorus, 'text': text, 'display': display, 'start': round(min(ts), 3), 'end': round(max(te), 3), 'chars': chars})

# ---------- 段落 ----------
secs = []
first = out_lines[0]['start']
if first > 1.0: secs.append({'tag': 'Intro', 'label': '前奏', 'chorus': False, 'start': 0.0})
for ev in tag_events:
    li = ev['line_index']
    start = out_lines[li]['start'] if li < len(out_lines) and out_lines[li]['tag'] == ev['tag'] else ev['after'] + 0.4
    label, ch = tag_info(ev['tag'])
    if secs and abs(secs[-1]['start'] - start) < 0.05 and secs[-1]['tag'] != 'Intro': secs[-1] = {'tag': ev['tag'], 'label': label, 'chorus': ch, 'start': start}
    else: secs.append({'tag': ev['tag'], 'label': label, 'chorus': ch, 'start': round(start, 3)})
if not tag_events: secs.append({'tag': '', 'label': '主歌', 'chorus': False, 'start': first})
last = out_lines[-1]['end']
if duration - last > 2.0 and not any(s['start'] > last - 0.05 for s in secs): secs.append({'tag': 'Outro', 'label': '尾奏', 'chorus': False, 'start': round(last + 0.5, 3)})
secs.sort(key=lambda s: s['start'])
# 没有歌词的长空档（> 6 秒）标成间奏
for a, b in zip(out_lines, out_lines[1:]):
    if b['start'] - a['end'] > 6 and not any(a['end'] - 0.1 <= s['start'] <= b['start'] + 0.1 and s['label'] == '间奏' for s in secs):
        secs.append({'tag': 'Instrumental', 'label': '间奏', 'chorus': False, 'start': round(a['end'] + 0.5, 3)})
secs.sort(key=lambda s: s['start'])
for i, s in enumerate(secs):
    s['i'] = i + 1; s['end'] = round(secs[i + 1]['start'] if i + 1 < len(secs) else duration, 3)
    s['lines'] = [l['i'] for l in out_lines if s['start'] - 0.05 <= l['start'] < s['end']]
for l in out_lines:
    l['sec'] = next((s['i'] for s in secs if s['start'] - 0.05 <= l['start'] < s['end']), None)

beats = [round(float(b['time_s']), 3) for b in ana.get('beats', []) if 'time_s' in b]
song = {
    'title': suno.get('title', ''), 'clip': suno.get('id', ''), 'song_url': suno.get('song_url', ''),
    'duration': round(duration, 3), 'bpm': ana.get('bpm'), 'key': ana.get('key'), 'time_signature': ana.get('time_signature'),
    'beats': beats, 'sections': secs, 'lines': out_lines,
    'musicSections': [{'start': s['start_s'], 'end': s['end_s'], 'label': s['label']} for s in ana.get('sections', [])],
    'terms': ana.get('terms', []),
}
if not beats: warn('没有节拍数据（tools/suno-analysis.json 缺失或还在 processing）：画面照样能做，只是不能卡拍')
os.makedirs(P('tools'), exist_ok=True); os.makedirs(P('out'), exist_ok=True)
json.dump(song, open(P('tools', 'song.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 写进 index.html ----------
h = open(P('index.html'), encoding='utf-8').read()
blob = json.dumps(song, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
h2, n = re.subn(r'<script type="application/json" id="song">.*?</script>', lambda m: f'<script type="application/json" id="song">{blob}</script>', h, flags=re.S)
if not n: err('index.html 里找不到 <script type="application/json" id="song">')
else: open(P('index.html'), 'w', encoding='utf-8').write(h2); ok(f'歌曲数据写进 index.html（{len(out_lines)} 句、{len(secs)} 段、{len(beats)} 拍）')

# ---------- 字幕 ----------
def ts(t):
    t = max(0, t); return f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t - int(t)) * 1000)) % 1000:03d}'
srt = []
for i, l in enumerate(out_lines):
    end = min(l['end'] + 0.5, out_lines[i + 1]['start'] - 0.05) if i + 1 < len(out_lines) else l['end'] + 1.0
    srt += [str(i + 1), f"{ts(l['start'] - 0.1)} --> {ts(end)}", l['display'].replace('　', ' '), '']
open(P('out', 'subtitles.srt'), 'w', encoding='utf-8').write('\n'.join(srt)); ok(f'字幕 out/subtitles.srt（{len(out_lines)} 条）')

# ---------- 音轨：响度归一 ----------
if mp3 and not no_audio:
    os.makedirs(P('assets'), exist_ok=True)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', mp3, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr, re.S)
    if not m: err('loudnorm 第一遍失败：' + r.stderr[-300:])
    else:
        j = json.loads(m.group(0))
        af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
              f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
        r2 = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', af, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', P('assets', 'song.wav')], capture_output=True, text=True)
        if r2.returncode: err('写 assets/song.wav 失败：' + r2.stderr[-300:])
        else: ok(f"音轨 assets/song.wav（原响度 {float(j['input_i']):.1f} LUFS → −14 LUFS）")

# ---------- 摘要 ----------
fmt = lambda t: f'{int(t // 60)}:{t % 60:04.1f}'
print(f"\n歌曲 {song['title'] or '(无标题)'}  {fmt(duration)}  {song['bpm'] or '?'} BPM  {song['key'] or ''}")
for s in secs:
    ls = s['lines']; print(f"  {fmt(s['start'])}–{fmt(s['end'])}  {s['label']}{'（副歌）' if s['chorus'] and '副歌' not in s['label'] else ''}  " + (f"第 {ls[0]}–{ls[-1]} 句" if ls else '无歌词'))
long = [l for l in out_lines if len(strip(l['display'])) > 15]
if long: warn('这些句子超过 15 字，字幕会缩小字号：' + '、'.join(f"第{l['i']}句" for l in long))
sys.exit(1 if bad else 0)
