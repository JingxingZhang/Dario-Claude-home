---
name: "dangnian-mingyue"
description: "当年明月：把上传的历史书（如《明朝那些事儿》）某一章，先写成一首歌（迪伦式歌词、陶喆式R&B，Suno只生成一次，用户下载mp3发回），再按逐字时间做成抖音横屏MV（16:9、系列“大明开局”）：明代版画套色画面、副歌大字排版、歌词字幕、右上角署名、封面与发布文案，史实按正史核对。用户说“做第N章”“把这章做成歌/MV”时使用。"
---

# 当年明月 · 歌与 MV

用户说“做第 N 章”，分两段做完：

- **A 段：做歌**。读书 → 核对史实 → 写歌词和歌曲说明 → 用 Suno 生成**一次** → 把 suno.com 的链接发给用户 → **停下**，等用户下载 mp3 发回来。
- **B 段：做 MV**。收到 mp3 → 拉逐字时间和节拍 → 对齐 → 分镜 → 版画动画 → 检查 → 渲染 → 封面、知识卡 → 歌词分镜稿、发布文案、交付说明 → 交付。

两段里只有 A 段末尾这一处必须停下。其他地方一口气做完，除非遇到真正要用户拍板的事（书里找不到这一章、Suno 额度不够、mp3 和 Suno 记录的对不上）。用户另说“先只写歌词”“先出 15 秒小样”，就做到那一步为止。

## 默认设置（用户已确认，除非用户另说，一律照此）

| 项 | 默认 |
|---|---|
| 平台 | 抖音 |
| 产物 | 一首歌（Suno 生成）+ 这首歌的 MV。没有旁白，没有动效音：**音轨就是整首歌** |
| 画幅 | 16:9 横屏 1920×1080，30 fps。主题栏 x 60–910、y 40–136；右上角署名 x 1600 以右、y 170 以上；字幕带 y 905–1080；画面内容放 y 170–890 |
| 时长 | **跟着歌走**，不卡秒数。歌词写到约 3–4 分钟的量（30–40 行），超过 4 分 30 秒完播率会掉 |
| 系列名 | **大明开局**（变量 `series`）；不用原书名或作者名做系列名 |
| 歌词 | 对标获诺贝尔文学奖的那位民谣诗人：新闻式叙事、画面清单、悬而不决的副歌、最后一次副歌改一个字、第二人称“你”、**允许古今并置**（现代画面要具体，全曲最多一段）。规范见 `references/lyrics-style.md` |
| 曲风 | 陶喆式 R&B 的强化版：neo-soul 律动、Rhodes 电钢琴、律动贝斯、带摇摆感的现场鼓、带转音的男声、假声、福音式和声、五声音阶旋律和二胡古筝点缀。提示词里**不写任何歌手名**。模板见 `references/suno.md` |
| 生成 | **每章只调用一次** `audio-create`（用户是免费版，每月 50 credits）；不调用 `audio-download`；歌由用户在网页上下载 |
| 画风 | **主歌、前奏、间奏：明代版画 × 套色印刷**（墨、朱、靛三版，半调网点、刻线、轻微错版、纸纹）；**副歌：大字排版**（一字一印，唱到哪字砸到哪字）+ 右侧版画画框。规范见 `references/banhua-style.md` |
| 画面 | **跟着歌词走**：每句歌词写到的人、物、动作，画面上都要出现。不用任何生成图片，不模仿现成作品；人物是墨色剪影 + 白刻线（不用骨骼角色） |
| 字幕 | 歌词逐字变色（唱过的字墨色，副歌唱过的字朱色，没唱到的字浅灰） |
| 主题栏 | 每段一句，≤ 10 字，用歌词的笔法：一个具体画面，带一点不安或反讽，不解释、少用问号；副歌段的主题栏重复，最后一次改一个字（例：“江水在涨”→“江水还在涨”） |
| 署名 | 右上角常驻“@张景行”+ 小印“景行”（变量 `signature`、`sealText`）；3:4 封面同样 |
| 成品体积 | ≤ 100 MB（变量 `maxMB` 或 `render.js --max-mb`） |
| AI 标识 | 视频和简介里**都不写** Suno、AI 生成之类的字样；发布时用户会在抖音勾选 AI 生成内容声明（发布清单里提醒） |

## 目录

- `scripts/setup.sh`：环境检查与安装（Node、ffmpeg、Chromium/Playwright、fonttools、pillow、字体）。**每个新会话先跑**（首次约 4 分钟，后台跑）。
- `scripts/epub_chapter.py`：列目录、取章节正文和元数据。`scripts/wikisource.py`：查正史原文。
- `scripts/new_chapter.sh`：新建一集工程（引擎、场景库、字体、封面模板、示例歌和示例分镜）。
- `scripts/song_sync.py`：mp3 + Suno 逐字时间 + 节拍 → 歌曲数据（写进 index.html 的 `#song`）、`assets/song.wav`（−14 LUFS）、`out/subtitles.srt`；核对 mp3 是不是那一首。
- `scripts/check.js`：合成检查（报错、字体、镜头覆盖、第 0 帧、副歌大字、撞署名/主题栏/字幕带、印制耗时），并写 `out/shots.json`。
- `scripts/still.js`：导静帧；`scripts/sheet.py`：拼图；`scripts/render.js`：渲染成片（`--from/--to` 只渲染一段、`--draft` 快速小样）；`scripts/qa.py`：成片质检；`scripts/compress.sh`：压缩别处来的视频。
- `scripts/lyrics_md.py`：生成歌词分镜稿.md；`scripts/check_glyphs.py`：查缺字；`scripts/fonts.py`：下载并裁剪字体（setup.sh 调用）。
- `assets/runtime/banhua.js`：版画套色 MV 引擎（`BH.film`、镜头、元素、错版、副歌大字、主题栏、字幕、给检查脚本的报告接口）；`assets/runtime/mr.js`：变量、字体就绪；`assets/vendor/gsap.min.js`（GSAP 3.14，标准免费许可）。
- `assets/template/`：`index.html`（章节骨架与变量）、`bh-lib.js`（版画场景库）、`shapes.js`（形体）、`cover.html`（3:4 封面）、`fonts.css`、`example/`（示例分镜 `chapter.example.js`、示例歌数据、示例歌词）。
- `references/lyrics-style.md` **歌词规范（写歌词前必读）**；`references/suno.md` **Suno 流程与曲风模板（生成前必读）**；`references/banhua-style.md` **画风、引擎接口、场景库、分镜规则（写分镜前必读）**；`references/fact-check.md` 史实核对；`references/publish-copy.md` 发布文案；`references/delivery-notes.md` 交付说明模板；`references/pitfalls.md` 避坑清单与耗时。

## A 段：做歌

记 `SK` 为本 skill 目录。工作目录放在 `/home/user/<书名拼音>/chNN`（或会话的主工作目录下）。

**0. 环境**（后台跑，同时做第 1–3 步）：`bash $SK/scripts/setup.sh`，每一项打 ✓ 才算好。

**1. 找书和章**：`python3 -I $SK/scripts/epub_chapter.py` 列目录（自动在上传目录里找 epub）；`python3 -I $SK/scripts/epub_chapter.py <序号或标题> --out <工作目录>/chNN-source.txt` 取正文。看会话里有没有用户发来的往期数据（见「抖音互动设计」第 6 条），有就先读。

**2. 读章并核对史实**（`references/fact-check.md`）：列人物、时间、地点、事件、因果链，逐项查正史；**同时挑出“能入歌的细节”**（一句原话、一个物件、一个数目、一个动作），记进核对表。歌词只从这张表里取细节，不编。

**3. 写歌词和歌曲说明**（`references/lyrics-style.md`）：一句话说清这首歌讲什么 → 定歌名（≤ 6 字，一个画面）→ 定结构（Verse / Refrain / Bridge / Final Refrain，带 Suno 段落标签）→ 逐行写（7–14 字，中间一个空格分成两个短语）→ 副歌最后一次改一个字 → 放一句可转述的冷知识 → 过自检表。写三份文件：
- `tools/lyrics.txt`：唱的版本（多音字换成同音字，交给 Suno）；
- `tools/lyrics-display.txt`：显示版（和唱的版本逐行、每行字数相同）；
- `tools/song-brief.md`：歌曲说明（歌名、一句话、曲风模板与提示词、避开项、段落、古今并置位置、冷知识句、多音字替换）。

**4. 建工程**：`bash $SK/scripts/new_chapter.sh <工作目录>/chNN`，改 index.html 顶部变量：`series`、`epNo`、`songTitle`、`chapNo`、`chapTitle`、`partLine`、`nextNo`、`nextTitle`（`signature`、`sealText`、`maxMB` 不用动）。把第 3 步的三份文件放进 `tools/`，跑 `python3 -I $SK/scripts/check_glyphs.py <章节>`。

**5. 生成歌**（`references/suno.md`）：
- 先 `account-usage` 看额度，不够就告诉用户、停下。
- 调用**一次** `audio-create`：`title` 写“歌名（大明开局·第N集）”，`lyrics` 用 `tools/lyrics.txt` 全文，`style` 用模板加微调，`negative_style`，`vocal_gender: "male"`；`model`、`duration` 不填。
- `audio-wait` 等到能播，再 `until: "complete"` 等到能下载；写 `tools/suno.json`。
- 把 `song_url` 发给用户：“打开链接 → ⋯ → Download → MP3，下载后发回来”。如果返回了两首，把两个链接都给，标出推荐哪首、为什么。
- **A 段到此停下。**

## B 段：做 MV（用户发来 mp3 之后）

**B1. 收歌、拉数据**：mp3 在 `/root/.claude/uploads/` 下（取最新的），拷成 `tools/song.mp3`。用 `tools/suno.json` 的 id（没有就用 `library-search` 按歌名找），调用 `audio-lyrics-alignment` 和 `audio-analysis`，等到不再是 processing，**把返回的 JSON 原样**写进 `tools/suno-alignment.json`、`tools/suno-analysis.json`。

**B2. 对齐**：`python3 -I $SK/scripts/song_sync.py <章节> --mp3 <章节>/tools/song.mp3`。它会核对时长、写 `#song`、出 `assets/song.wav` 和字幕，最后打印段落表。有 ✗ 先解决（最常见：用户下的是另一首）。

**B3. 分镜**：写简短的 `treatment.md`，包括：
- 段落表（每段的时间、主题栏）；
- 逐镜表：镜号、第几句、画面（这句歌词里能画的人、物、动作）、动作（推、颠、漂、交替）、转场；
- 副歌大字表：每句怎么折行、哪几个字印朱色、画框里画什么；
- 互动落点：冷知识、知识卡、片尾卡各在第几秒。

**B4. 搭镜头**：在 `assets/chapter.js` 里照示例的结构写（`references/banhua-style.md`；示例换成本集内容）。先做第 0 帧（标题卡）、第一句副歌、知识卡和最难的那一镜。场景库没有的东西就在本章里照库的写法画。

**B5. 检查**：`node $SK/scripts/check.js <章节>` 做到 0 个 ✗。⚠ 要导出那一刻的画面看一眼再判断。然后导关键帧拼图：第 0 帧、每个镜头的中段、每句副歌唱完的那一刻、知识卡、片尾卡。命令是 `node $SK/scripts/still.js <章节> --at 0,… --out <目录>`，再 `python3 -I $SK/scripts/sheet.py <目录> <拼图.png> 4 480`，**用 Read 看拼图**。重点查：画面是否跟着歌词、字是否被裁、是否撞署名或字幕带、副歌大字是否够大、有没有空镜。修完再导一遍。拿不准节奏时，先用 `render.js --from A --to B --draft` 出一段小样看。

**B6. 渲染**（后台）：`node $SK/scripts/render.js <章节>` → `out/<章节>-vN.mp4`，约为片长 × 6（4 分钟的歌约 20–25 分钟；开工就放后台，告诉用户大概多久）。完成后跑 `python3 -I $SK/scripts/qa.py <mp4>`：体积 ✓、响度约 −14 LUFS ✓、无黑场。再从 MP4 抽看第 0 帧、副歌、知识卡、结尾几帧（`ffmpeg -ss <t> -i <mp4> -frames:v 1 x.png`）。

**B7. 封面与知识卡图**（渲染期间做）：
- 3:4 封面：改 `cover/cover.html` 的 `COVER`（红签、两行钩子大字、歌名、章节和年份）和 `hero()`（一个最有分量的意象），再 `node $SK/scripts/still.js <章节>/cover/cover.html --at 0.5 --out <章节>/cover/cover.png`。
- 横版封面：`still.js <章节> --at 0 --out <章节>/cover/cover-16x9.png`。
- 知识卡单独导一张：`--at <知识卡完整显示的秒数> --out <章节>/cover/知识卡.png`。

**B8. 文稿与交付**：
- `python3 -I $SK/scripts/lyrics_md.py <章节>` 生成歌词分镜稿.md；
- 按 `references/publish-copy.md` 写 `发布文案.md`；
- 按 `references/delivery-notes.md` 写 `交付说明.md`（含史实核对表、Suno 实际唱的与歌词的出入、互动落点、数据回填表）。

用 SendUserFile 发：成片 MP4、`out/subtitles.srt`、歌词（显示版）、歌词分镜稿.md、treatment.md、封面 PNG（3:4 和 16:9）、知识卡.png、发布文案.md、交付说明.md。再把整个章节目录（不含 `out/*.mp4`、`tools/song.mp3`、`assets/song.wav`）打成 zip 一起发。提醒用户：云端容器会回收，文件以发出的为准。

## 抖音互动设计（MV 版）

依据：抖音公开的推荐原理是预估用户对内容的点赞、关注、分享、评论等行为，并重视收藏、复访、追更这类长期目标。所以每集都要给观众**存下来、说两句、转给别人、追下一集**的具体理由。第三方流传的“权重排序”没有官方出处，不当依据。

1. **留人（前 3 秒）**：第 0 帧是标题卡（横版封面）；风格里写 short intro，让第一句歌词尽早开口；第一句就是钩子（一个具体的人 + 一个问题）。前奏超过 12 秒，标题镜头要有持续运动，必要时在前奏里切第二镜。
2. **收藏：知识卡**。放在间奏或尾奏，统一版式（`BH.card`），完整停留 ≥ 2.5 秒；卡上的数字都在核对表里。
3. **评论：片尾卡站队题**。最后 3–4 秒（`BH.endCard`），选项都印在屏上；置顶评论用同一句原话，作者先答。剧透邀请写在简介或置顶评论里，必须有明确的史实答案。不做故意留错、“扣 1”、要求点赞关注。
4. **转发：一句冷知识**。写进歌词，同一镜里把它印出来（大字或刻本小字）；数字进核对表，不夸大。
5. **追更**：片尾卡写“下一集 · ……”（具体画面）；合集“大明开局”。
6. **数据回填**：交付说明末尾附空表（见模板），发布 7 天后用户填回来。会话里有往期数据时，写歌词前先做对比（哪集哪项最好、最差，对应的是什么），把据此做的调整写进交付说明。没有数据就按默认做，不编造。

## 只做一部分时

- **只写歌词**：做到 A 段第 3 步，交出三份文件和核对表，不生成。
- **只生成歌**：用户给了歌词，就先按自检表检查，提出修改建议，用户同意后再调用一次 `audio-create`。
- **重新生成**：只在用户明确要求时做（会再花额度）；问清这次改什么（歌词、曲风模板、BPM），旧的 `tools/suno.json` 改名留底。
- **只做 MV**：用户带来 mp3 和 suno.com 链接（或 id），从 B1 开始。mp3 不是 Suno 生成的就拿不到逐字时间，告诉用户这一点，问他要 Suno 上的那首。
- **小样**：`render.js <章节> --from 30 --to 50 --draft`（只渲染一段、快速编码）。
- **改某一处**：按“时间点 + 改什么”做最小修改（改 chapter.js），重导相关关键帧，再渲染。歌词唱错了不能改字幕了事，要告诉用户，由用户决定要不要重新生成。
- **改署名或体积上限**：改 index.html 变量 `signature`（留空不显示）、`maxMB`，以及 cover.html 里的变量；或渲染时加 `--max-mb 60`。

## 底线

- 歌词用自己的话写，原书金句最多一句，并在简介里注明“讲法参考《明朝那些事儿》”；系列名、标题、封面不用原书名或作者名，不写成或暗示是原作者的作品。
- 歌词学那位诗人的眼光和笔法，不直译、不套用他的句子，作品里不出现他的名字；曲风学陶喆式 R&B 的特征，不写任何歌手名，不模仿任何真实歌手的声音。
- 史实以正史为准，不确定的写“号称”“有人说”；歌词、主题栏、知识卡、冷知识里的细节不为了押韵或画面编造。
- 每章只生成一次歌；不替用户花下载额度；不在视频和简介里写 Suno 或 AI 字样（平台的 AI 声明由用户发布时勾选）。
- 不用任何 AI 生成图片；画面全部用代码绘制，不模仿已有影视、动漫、版画作品的具体画面。
- 互动只给观众真实的理由，不硬要点赞关注、不故意留错、不编造往期数据。
- 长任务一律后台运行，并告诉用户大约要多久；不要让用户在没有消息的情况下干等。
