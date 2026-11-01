# 画风与分镜：明代版画 × 套色印刷（主歌）＋ 大字排版（副歌）

画面像一张会动的套色版画：米色纸，墨、朱、靛三块版各印一遍，半调网点、刻线、轻微错版，纸纹和颗粒每秒抖 6 次（像逐张印出来的）。副歌改成大字排版：一字一印，唱到哪个字，哪个字就砸下来，右侧画框里印一张小画。**画面跟着歌词走**：每句歌词写到的人、物、动作，画面上都要真的出现。

全部用代码画，不用任何生成图片。只借鉴明代版画和套色印刷的形式语言，不模仿任何现成作品的画面。

## 一、视觉规范

| 项 | 规范 |
|---|---|
| 纸 | `#ece2ca`，带纤维、斑驳；全片一张纸（`paperSeed` 变量） |
| 墨版 | `#1f1b1c`：轮廓、剪影、刻线、文字 |
| 朱版 | `#c63b2b`：太阳、旗、门、袍、重点字；一个画面里朱色只给 1–2 样东西 |
| 靛版 | `#2c5b82`：天空刻线、山、水、夜色、阴影（多用网点版 `blueT`） |
| 网点 | 浓淡一律用网点版（`inkT` / `redT` / `blueT` 里画 alpha），不用渐变色 |
| 白线 | 黑色剪影上用“刻”出来的白线表现结构（`BH.carve`），这是木刻的味道 |
| 人物 | 墨色剪影 + 白刻线，脸不画五官；近景人物高度 ≥ 300px |
| 字体 | 思源宋体 900（大字、主题栏、字幕）、600（小字、出处） |
| 帧率 | 30 fps；运动以平移、推拉、上下颠、两三张交替（limited animation）为主 |

**画面跟着歌词**：先把每句歌词拆成“能画的东西”（人、物、地点、动作），再决定这一句给哪一镜。抽象句（“有人说聪明人 从来不回头”）找一个具体画面去接（两个人：一个往前走，一个回头）。古今并置的歌词，就让写字楼也印成版画（`BH.office`），窗外是 1363 年的江。

## 二、版面（16:9 1920×1080）

| 区域 | 位置 |
|---|---|
| 主题栏（引擎画） | 朱色块 x 60–910、y 40–136，纸色字；下方小字“大明开局 · 第N集《歌名》” |
| 署名（引擎画） | 右上角“@张景行”+ 小印，x 1600 以右、y 170 以上不要放东西 |
| 字幕带（引擎画） | y 905–1080，纸色底；歌词逐字变色（唱过的字墨色，副歌唱过的字朱色，没唱到的字浅灰） |
| 画面内容 | y 170–890；人物着地线在 860–880 左右；副歌大字框默认 `[110, 210, 860, 660]`，右侧画框 `[1040, 200, 780, 640]` |

## 三、引擎接口（`vendor/banhua.js`）

```js
const F = BH.film();                 // 读 #song（歌曲数据）和 index.html 的变量
const S = F.song, L = S.line;        // L(n)：第 n 句 {start, end, text, display, chars:[{c,s,e}], chorus, label}
S.sec(n) / S.sec('副歌')             // 第 n 段 {start, end, label, chorus, lines}
S.beats / S.beatPeriod / S.snap(t) / S.beatAfter(t) / S.beatsIn(a, b)

F.topic(t, '一句主题栏')              // 每段一句；第 0 秒必须有
F.shot('名字', 开始秒, (sh) => { … }, { transition: 'cut' | 'paper' | 'wipe' | 'split', res: 1.12, subs: true });
                                      // 镜头从“开始秒”到下一个镜头开始；第一个镜头必须从 0 开始
F.kick(t, 8) / F.kickBeats(a, b, { every: 2, amt: 5 })   // 错版震一下（墨、朱、靛三版散开再合上）
F.shake(t, 10, 0.4)                   // 震屏
F.finish();                           // 最后一行
```

镜头里：
```js
const e = sh.el({ box: [x, y, w, h], depth: 1, res: 1.12, name: '马' }, (o) => BH.horse(o, 960, 862, 1.6));
//  box：这块版的范围（屏幕坐标），只印 box 里的东西；越小越快。不给就是全屏
//  depth：视差，0 = 不跟镜头动（天），1 = 完全跟镜头（前景）
e.from({ x: -300, alpha: 0 }, { at: 0, dur: 1.2, ease: 'power2.out' })   // at、dur 相对镜头开始，单位秒；dur: 'shot' = 到镜头结束
e.to({ x: 200, scale: 0.8 }, { at: 2, dur: 3 })
e.set({ alpha: 0 }, 0)
e.bob({ amp: 5, period: S.beatPeriod })     // 上下颠（按节拍）
e.sway({ deg: 2 }) / e.drift({ x: 160 }) / e.pulse({ amt: 0.03 })        // 摇、整镜匀速漂移、每拍一跳
sh.cycle([e0, e1, e2], { period: S.beatPeriod / 2 })                    // 几张版轮流显示：走路、水纹、火、旗
sh.push(1.1, { fx, fy })              // 整镜慢推
sh.camSet({ zoom, fx, fy }) / sh.camTo({ zoom: 1.3, fx: 1200, fy: 470 }, { at: 0.5, dur: 2 })
sh.type(第几句 | '文字', { box, rows, scale: [0.6, 1], color: (row, col, i) => 'ink'|'red'|'tone', mode: 'slam'|'all', maxPerRow: 4 })
sh.kick(相对秒, 量)
```

画版用的 `o`：`o.ink / o.red / o.blue`（实版）、`o.inkT / o.redT / o.blueT`（网点版，画 `BH.tone(0.5)` 这种透明度）、`o.knock(path)` / `o.knockRect(...)`（遮挡：这块挡住后面的版）。元素的 (x, y) 一律是屏幕坐标。

## 四、场景库（`assets/bh-lib.js`，人和物的 (x, y) = 水平中心、着地线）

| 类 | 函数 |
|---|---|
| 天 | `BH.sky(o, y0, y1, seed)` 刻线天、`BH.nightSky(o, y1, seed, [mx,my,mr])` 夜空（月亮留白）、`BH.sun(o, x, y, r)`、`BH.moon(o, x, y, r)` |
| 山水地 | `BH.mount(o, x0, x1, base, peak, seed, dens)`、`BH.waves(o, top, bottom, r, seed, dens, persp, phase)`、`BH.crests(o, y, seed, step, size, phase)`、`BH.ground(o, y0, y1, seed)`、`BH.hill(o, 'SVG路径')`、`BH.shadow(o, x, y, rx)` |
| 人 | `BH.horse(o, x, y, s, { phase, flip, rider, robe })`、`BH.robed(o, x, y, s, { robe })`（正面长衫）、`BH.profile(o, x, y, s, { flip, robe })`（侧面）、`BH.grinder`（蹲着磨桨）、`BH.sentry`（持枪）、`BH.fallen(o, x, y, s, '旗上字')`、`BH.crowd(o, x0, x1, y, s, seed, { flags })`（远景军队、人群） |
| 物 | `BH.flag(o, x, y, h, '字', phase)`、`BH.tents`、`BH.birds`、`BH.arrows`、`BH.pine`、`BH.reeds`、`BH.fire(o, x, y, w, h, phase)`、`BH.smoke`、`BH.rain`、`BH.lantern` |
| 建筑 | `BH.city(o, x, y, w, s)` 城墙城楼、`BH.throne(o, x, y, s, { sitter: 0.36 })` 龙椅（可坐一个很小的人）、`BH.archWall(o, rect, [门心x, 拱顶y, 门宽])`、`BH.doors`、`BH.windowFrame(o, rect, 列, 行)`、`BH.tower(o, x, y, s)` 三层楼船、`BH.boat(o, x, y, s, { sail })`、`BH.office(o, x, y, s, '屏幕上的字')` 写字楼一角 |
| 文字 | `BH.titleCard(o, { title, sub })` 片头标题、`BH.bookPage(o, { center, cols, pic, seal })` 明刻本书页（原话、史料）、`BH.frame(o, rect, pic)` 副歌画框、`BH.card(o, {...})` 知识卡、`BH.endCard(o, { question, options, next })` 片尾卡、`BH.text / BH.vtext / BH.seal / BH.wrap` |
| 工具 | `BH.carve(c, x, y, s, flip, fn)` 刻白线、`BH.erase(c, fn)` 挖掉、`BH.hatch(c, path, {...})` 排线、`BH.rng(seed)`、`BH.ridge`、`BH.torn`、`BH.roof`；形体 `BH.S.horse()` 等（`assets/shapes.js`） |

库里没有的东西（比如寺庙、钟、信、算卦的签筒），就在本章 `chapter.js` 里照库里的写法画：Path2D 剪影 → `o.knock` → 墨版填色 → `BH.carve` 刻白线 → 朱版点一样东西 → 网点版打阴影。画得好的可以挪进 `bh-lib.js`，在交付说明里写一句。

## 五、分镜规则

1. **第 0 帧就是横版封面**：第一个镜头从 0 秒开始，用 `BH.titleCard` 写歌名，配一个最有分量的意象。首帧元素不做淡入。
2. **按歌词切**：一句或两句歌词一镜，在开口前 0.2–0.4 秒切（`L(n).start - 0.3`，能落在拍上更好：`S.snap()`）。一镜不超过 14 秒；长的前奏、间奏要有持续运动（推、漂、水纹交替）。
3. **副歌 = 大字**：每句副歌一个镜头，`sh.type(n)` 出大字，右侧 `BH.frame` 里印一张和这句有关的小画。第一句副歌用 `transition: 'split'`（错版炸开）。最后一次副歌用朱色大字（`color: 'red'`）。
4. **转场**：段落之间用 `paper`（纸闪）或 `wipe`（毛边擦过去），同一段里用 `cut`。全片 `wipe` 不超过 3 次。
5. **动**：每一镜至少有一样在动——推镜（`sh.push`）、颠（`bob`）、漂（`drift`）、交替（`cycle`：走路两张、水纹三张、火三张、旗两张）。节拍明显的段落用 `F.kickBeats` 让错版跟着拍子跳。
6. **镜头推近时算好裁切**：推到 1.3 倍，原来在边上的东西会出画，人物会撞进字幕带。推近的目标点放在画面中部。
7. **原话、史料**：用 `BH.bookPage` 印成明刻本书页（版框、界行、鱼尾、出处卷次），原话印大字、朱色。
8. **知识卡（收藏）**：间奏或尾奏放一张 `BH.card`（统一版式：左上角“大明开局 · 第N集”、平实的标题、3–5 项、底部小字出处），完整停留 ≥ 2.5 秒，卡上的数字都在核对表里。
9. **片尾卡（评论、追更）**：最后 3–4 秒用 `BH.endCard`：站队题 + 选项（都印在屏上）+“下一集：……”。

## 六、渲染与速度（4 核实测）

- 每块版只印一次（半调、刻痕都在这一步），之后每帧只做合成：10 秒片段逐帧约 33 秒，编码约 30 秒。一首 4 分钟的歌，整片约 20 分钟。
- 印一块全屏的版约 0.3–0.6 秒，`check.js` 会列出超过 1.5 秒的元素。慢的话缩小 `box`，或者把 `res` 调回 1。
- 只缓存当前镜头和下一个镜头的版。`still.js` 跳着导帧时会现印，所以第一张会慢一点。
- 推镜放大超过 1.15 倍的镜头，把 `res` 设成和最大放大倍数差不多（例如 1.35），不然会糊。
