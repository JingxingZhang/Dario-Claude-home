# Suno：生成歌、拉对齐数据（用 Suno MCP）

用户的 Suno 是免费版（2026-11 实测：每月 50 credits、只有 `v6-mini` 模型、下载额度为 0、有高级控制）。所以规则是：

- **每章只调用一次 `audio-create`**。不重试、不“多出几版挑一挑”。用户明确说“重做一首”“换个曲风再来一次”，才再调用一次。
- **不调用 `audio-download`**：下载额度是 0，调了也会被要求花额度。歌由用户在 suno.com 上下载 mp3，再发回来。
- 生成前先用 `account-usage` 看一下额度。`credits_remaining` 不够一次生成，就告诉用户并停下。
- 工具没加载时，先用 ToolSearch 搜 `suno` 加载（`select:mcp__Suno__audio-create,...`）。

## A 段：生成歌

### 1. 风格提示词（style）：陶喆式 R&B 的强化版

Suno 会拦截或忽略提示词里的真实歌手名，所以**不写任何歌手名**，把特征拆开来写。三个模板，按章节情绪选一个，再按本章内容微调（加减乐器、改 BPM）。长度 ≤ 1000 字符。

**A 律动叙事（默认）**
```
Mandopop R&B, neo-soul groove, warm Rhodes electric piano, funky fingerstyle bass, tight live drums with swing and ghost notes, clean electric guitar licks, smooth male tenor lead with agile melismatic runs, airy falsetto lifts in the refrain, stacked gospel-style backing harmonies, subtle erhu and guzheng accents on pentatonic hooks, storytelling verses, catchy soaring refrain, short intro, 84 bpm
```

**B 抒情慢板**（结局悲凉、人物落幕的章节）
```
Mandopop soul ballad, intimate piano and Rhodes, string quartet swells, brushed drums, round warm bass, expressive male tenor with tender falsetto and gospel runs, layered harmony choir in the final refrain, restrained verses building to a heartfelt climax, faint dizi melody, short intro, 70 bpm
```

**C 中国风 R&B**（打仗、权谋、节奏感强的章节）
```
Chinese-style R&B, hip-hop swing drums, slap and synth bass, pipa and guzheng riffs, erhu counter-melody, muted funk guitar, confident male tenor with rhythmic phrasing and falsetto ad-libs, call-and-response backing vocals, punchy catchy refrain, short intro, 92 bpm
```

**避开（negative_style）**：`EDM drops, trap hi-hats, heavy metal, screamo, auto-tune effect, children's choir, opera`
（这项要高级控制权限，返回 403 就去掉它重发。重发不算重试，因为第一次没有生成。）

### 2. 调用

```
audio-create {
  title:  "江水在涨（大明开局·第10集）",
  lyrics: <tools/lyrics.txt 的全文：唱的版本，带 [Verse] [Refrain] 标签>,
  style:  <模板 + 微调>,
  negative_style: "...",
  vocal_gender: "male"
}
```
- `model` 不填（用账号默认的模型）；`duration` 不填（歌多长由歌词决定，MV 跟着歌走）。
- 不用 `description` 模式：歌词必须是我们写好、核对过的那一份。
- 返回的 `clip_ids` 可能有一个或两个（看 Suno 怎么出）。**只调用这一次**；有两个的话，用 `audio-analysis` 的 `terms`/`labels` 比一下哪首更接近要求（男声、R&B、乐器对不对），把推荐的那首告诉用户，另一首也列出来，由用户决定。

### 3. 等歌出来，告诉用户

- `audio-wait`（`ids` 填全部 clip id）等到 `streaming`：这时已经能在网页上听。再调用一次 `audio-wait`，`until: "complete"`，等到能下载。
- 把 `song_url`（suno.com/song/…）发给用户，附一句：打开链接 → 右上角 ⋯ → Download → MP3，下载后直接发回来。
- 写 `tools/suno.json`：`{ "id", "title", "song_url", "style", "negative_style", "duration", "created_at" }`。`duration` 从 `audio-retrieve` 的 `metadata.duration` 读。
- **A 段到此停下**，等用户发 mp3。这是整个流程里唯一必须停下的地方。

## B 段：拉对齐数据

用户发来 mp3 后：

1. **找文件**：用户上传的文件在 `/root/.claude/uploads/` 下（`find /root/.claude/uploads -name '*.mp3'`，取最新的），拷进 `<章节>/tools/song.mp3`。
2. **确认是哪一首**：优先读 `tools/suno.json` 的 id。没有的话（比如换了会话），用 `library-search` 或 `library-list` 按歌名、时长找。实在对不上就问用户要 suno.com 的链接（`/song/<id>` 里就是 id）。
3. **逐字时间**：`audio-lyrics-alignment {id}`。返回 `processing` 就隔几秒再调用（第一次调用会启动对齐，不花额度）。等到 `complete`，**把返回的 JSON 原样**写进 `tools/suno-alignment.json`。
4. **节拍和段落**：`audio-analysis {id}`，同样等它离开 `processing`，原样写进 `tools/suno-analysis.json`。
5. 跑 `python3 -I scripts/song_sync.py <章节> --mp3 <章节>/tools/song.mp3`：核对时长（mp3 和 Suno 记录的时长差 > 0.5 秒就报错，多半是下错了歌）、解析逐字时间、算段落、写 `#song`、出 `assets/song.wav`（−14 LUFS）和字幕。

## 数据的样子（`song_sync.py` 已处理，了解即可）

- **逐字时间**：`words[]` 是 `{word, start_s, end_s}`。一个 `word` 可能是一个字、两个字，也可能带着换行和段落标签（`"桨\n\n[Verse 2]\n一"`）。换行前的字是上一行的尾巴，脚本会把它放在上一个字之后。
- **节拍**：`beats[].time_s` 可靠；`bar_position`（拍在小节里的位置）**不可靠**（实测常在 1、2 之间来回跳）。所以别按“小节第一拍”切镜头，按节拍时间点和段落切。
- **段落**：以歌词里的标签为准（[Verse 1] 等）；分析给的 `sections`（A/B/C 字母）只作参考，存在 `musicSections` 里。
- **歌词被改**：Suno 偶尔会多唱一遍副歌或改字。对齐结果是“交上去的歌词”的时间；听到有出入，以对齐结果为准，在交付说明里记一句。

## 版权与发布（用户已确认的做法）

- 用户的抖音没开收益，按非商业使用发布，用免费版的歌。
- **简介里不写“音乐由 Suno 生成”**，视频里也不出现任何 AI 字样。发布时，用户会在抖音勾选“作品含 AI 生成内容”的声明（发布清单里提醒一句）。
- 用户以后开通收益，要提醒：免费版生成的歌不能商用，升级后也不会给旧歌补授权。
