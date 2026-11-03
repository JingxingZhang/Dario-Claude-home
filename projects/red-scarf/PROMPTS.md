# The Long Red Scarf — 提示词手册

> 提示词用英文（模型对英文更稳）。每个镜头先用 **Nano Banana 2.1** 出首帧，再用 **Veo 3.1** 做图生视频。
> 镜头编号与 `edl.json` 一致，文件按 `S01.png` / `S01.mp4` 命名。

---

## 0. 固定模块（每条提示词都要拼进去）

### STYLE（风格块）
```
2D hand-drawn animation still, European storybook illustration style, clean dark-brown ink outlines with varying line weight, flat cel-shaded characters with soft painted shadows, watercolor and gouache textured backgrounds on visible paper grain, soft atmospheric haze, muted overcast palette of pale grey-teal, sage green and ochre, the long red scarf is the only strongly saturated color, gentle storybook lighting, 16:9 widescreen, no text, no letters, no watermark
```

### HER（主角块）
```
a very tall, lanky young woman with a deadpan, sleepy half-lidded expression, short copper-orange bob haircut with blunt bangs, light freckles, long charcoal-grey wool overcoat to her shins, black tights, chunky brown lace-up boots, an extremely long hand-knitted bright red scarf (several meters long) wrapped once around her neck with both ends trailing far behind her in the wind, a paper grocery bag with a baguette tucked under her left arm
```

### TOWN（场景块）
```
a windy seaside hill town in late autumn: steep cobbled streets, narrow pastel terraced houses with white window frames, iron lampposts, seagulls, a grey harbor glimpsed in the distance, orange and ochre leaves blowing through the air
```

### NEG（反向提示词，Veo 填 negative prompt）
```
3D render, CGI, photorealistic, anime, glossy, morphing, warping face, extra limbs, extra fingers, duplicated scarf, scarf changing color, style change, camera shake, text, subtitles, watermark, logo
```

---

## 1. 先做两张"定妆图"（之后每张都当参考图喂进去）

**REF-A 角色三视图**（Nano Banana 2.1，2K，16:9）
```
Character turnaround model sheet on a plain warm-white paper background: front view, three-quarter view, side view and back view of [HER], plus three small expression heads (deadpan, tiny surprise, small content smile). [STYLE]. Consistent proportions across all views, full body, evenly spaced.
```

**REF-B 风格样板**（Nano Banana 2.1，2K，16:9）
```
Wide establishing background painting of [TOWN], empty street, no characters. [STYLE].
```

> 挑满意的各存一张：`stills/REF_A.png`、`stills/REF_B.png`。后面每个镜头都把 REF-A + REF-B 一起作为参考图，再加一句：
> `Use the attached character sheet for her exact design and the attached background for the exact painting style.`

---

## 2. 逐镜头提示词

规则：
- **首帧 = 动作发生前的那一瞬间**，给 Veo 留出表演空间。
- Veo 时长选 **4s**（最短，最省钱）；剪辑只用其中约 2.2 秒，所以视频提示词里写明"动作在前 3 秒内完成"。
- 每条 Veo 提示词末尾都加 **MOTION_TAIL**：
```
Keep the exact hand-drawn 2D style, line work, colors and character design of the input image. Fluid traditional 2D character animation with snappy comedic timing, smear frames on fast moves. Static camera unless stated. Audio: soft wind ambience and one light foley sound for the action, no music, no dialogue.
```

| # | 时长 | Nano Banana 首帧 | Veo 3.1 动作 |
|---|---|---|---|
| S01 | 2.5s | `Wide side-on shot of [HER] walking from left to right along a steep cobbled street of [TOWN], her red scarf streaming horizontally behind her for meters in the strong wind, leaves blowing. [STYLE]` | `She strolls left to right with long, lazy strides, deadpan; the enormous red scarf ripples and snakes behind her in the wind; leaves swirl past. Slow camera pan following her.` |
| S02 | 2.2s | `Medium side shot on a windy street: a small boy in a yellow raincoat has just let go of a red balloon, the balloon string floating up just out of his reach; [HER] walks past behind him, scarf end trailing near the string. [STYLE]` | `Without looking, she gives a tiny flick of her neck; the scarf end whips up, curls around the balloon string like a hand and drops it back into the boy's open palm. The boy blinks. She keeps walking out of frame. Action completes within the first 3 seconds.` |
| S03 | 2.2s | `Medium shot: an old man with a white mustache on a bench, his newspaper pages bursting apart and flying in the wind; [HER] entering from the left. [STYLE]` | `The loose newspaper pages fly toward her; her trailing scarf sweeps through the air in one smooth arc, gathers all pages into a neat stack and slaps it back onto the old man's lap. He stares. She never breaks stride. Action completes within the first 3 seconds.` |
| S04 | 2.2s | `Side shot: a window cleaner on a tall wooden ladder leaning against a pastel house, the ladder starting to tip away from the wall, bucket swinging; [HER] walking past an iron lamppost at the foot of the ladder. [STYLE]` | `As the ladder tips, her scarf whips out, loops around the ladder and the lamppost and ties itself into a neat bow, the ladder snaps back upright. The window cleaner, still clinging on, gives a shaky thumbs up. Action completes within the first 3 seconds.` |
| S05 | 2.2s | `Low angle under an autumn tree: a small bird's nest with three blue eggs tumbling off a branch in the wind, a mother bird flapping in alarm; [HER] walking underneath. [STYLE]` | `The nest falls; her scarf swings beneath it like a hammock and catches it softly, the eggs bounce once and settle; the scarf lifts the nest gently back onto the branch. The bird lands on it, relieved. Action completes within the first 3 seconds.` |
| S06 | 2.2s | `Side shot outside a small café with striped awning: a waiter in a white apron mid-stumble on the cobbles, his tray of teacups tilting and cups beginning to slide off; [HER] passing by. [STYLE]` | `The cups slide off the tray; her scarf slides flat underneath them like a second tray, catches every cup without spilling, and tips them neatly back onto his tray. The waiter freezes in a bow. Action completes within the first 3 seconds.` |
| S07 | 2.2s | `Small park on the hill, a red-and-yellow diamond kite tangled high in a bare tree; a girl in a green coat pointing up at it, close to tears; [HER] standing below, looking up deadpan, unwinding her red scarf from her neck. [STYLE]` | `She swings the long red scarf over her head like a lasso, then throws it high; the end hooks the tangled kite and frees it. Action completes within the first 3 seconds.` |
| S08 | 2.2s | `Same park, wider: the freed kite catching a huge gust and soaring up into the grey sky, the red scarf still knotted to it, trailing like a long kite tail and pulled out of her hands; [HER] below with an empty bare neck, arms slightly raised. [STYLE]` | `The gust yanks the kite up; the red scarf slips out of her fingers and flies away with it as a kite tail, shrinking into the sky. She watches it go, blinking slowly, bare-necked. The girl cheers.` |
| S09 | 2.2s | `Side-on street shot, [HER] walking left to right WITHOUT her scarf (bare neck, coat collar up), the wind has stopped, the last leaves drifting down vertically, the light a little colder and bluer. [STYLE]` | `She walks on calmly; the wind dies completely; the last leaves float straight down and settle on the cobbles. Everything goes very still and quiet.` |
| S10 | 2.2s | `Extreme close-up of [HER]'s freckled nose and half-lidded eyes in profile against a pale cold sky, a single tiny snowflake drifting down just above her nose. No scarf. [STYLE]` | `The single snowflake drifts down and lands on the tip of her nose. Her eyes slowly cross to look at it. Very slow, gentle motion. Static camera.` |
| S11 | 2.2s | `Close-up of [HER]'s face, frontal, deadpan, bare neck, coat collar up, a few snowflakes falling around her, cold blue-grey light. [STYLE]` | `She gives one tiny full-body shiver, deadpan, and exhales a small puff of white breath. A few snowflakes fall. Subtle and comedic.` |
| S12 | 3.3s | **首帧**：`Medium wide shot in light snowfall: [HER] standing still on the street without her scarf, looking up; high above, the long red scarf drifting down out of the sky like a ribbon; in the background on the hill the girl in the green coat holds the kite and waves. [STYLE]` **尾帧**：`Same composition: the red scarf has landed and is wrapped perfectly around [HER]'s neck once, both ends hanging; she has a tiny content smile; the girl waves in the background. [STYLE]` | **首尾帧模式**：`The red scarf flutters down out of the snowy sky in slow loops and wraps itself neatly around her neck. She gives a tiny, satisfied smile. The girl waves in the distance.` |
| S13 | 2.4s | `Back view, wide shot: [HER] walking away up the snowy cobbled street, the red scarf trailing behind her, snow falling, warm lit windows in the pastel houses. [STYLE]` | `She walks slowly away from the camera up the street; the red scarf sways gently; snow falls. Slow, calm. Static camera.` |

---

## 3. Veo 3.1 参数

| 项 | 设置 |
|---|---|
| 模式 | Image-to-Video（首帧）；S12 用 First + Last frame |
| 比例 / 分辨率 | 16:9 / 1080p（Lite 试稿可用 720p） |
| 时长 | 4s（S12 可选 6s） |
| 音频 | 保留原生音效（剪辑时压低到 −16dB 垫在音乐下，不要可关） |
| 抽卡 | 每镜先跑 2 条；有物理动作的 S02–S08、S12 预计要 3–6 条 |

## 4. 交付命名

- 首帧图：`stills/S01.png` … `stills/S13.png`
- 视频：`clips/S01.mp4` …；多条候选用 `S05_t1.mp4`、`S05_t2.mp4`，我来挑。
- 配乐：从 Suno 下载你选的那版 mp3，命名 `music/score.mp3`。

---

## 5. 精简版首帧提示词（定妆图已定，配合 REF_A + REF_B 两张参考图使用）

> 定妆图用 ChatGPT Images 2.5 生成，保存在 `stills/REF_A.png`、`stills/REF_B.png`。13 张首帧建议**用同一个工具**出，每次都附上这两张图。
> 调整：气球改蓝色、风筝改黄蓝色，避免和红围巾抢颜色；背景要求比 REF_B 更简洁、更雾、更灰，让人物跳出来。

每条末尾都拼上 **TAIL**：
```
Use the first attached image as the exact character design (face, copper bob with bangs, freckles, charcoal-grey coat, very long chunky red knitted scarf with fringe, black tights, brown lace-up boots, paper bag with baguette under her right arm) and the second attached image for the watercolor painting style and town. Keep the background simpler, hazier and more muted than the reference so she stands out; the red scarf is the boldest color in the frame. 2D hand-drawn storybook animation frame, 16:9, no text.
```

| # | 首帧提示词（+ TAIL） |
|---|---|
| S01 | Wide side-view shot: she walks from left to right along a steep cobbled street of the seaside town, her very long red scarf streaming horizontally behind her in strong wind, a few leaves blowing. |
| S02 | Medium side shot on the windy street: a small boy in a yellow raincoat has just let go of a sky-blue balloon, its string floating just above his reaching hand; she walks past right behind him, the end of her scarf trailing near the string. |
| S03 | Medium side shot: an old man with a white mustache sitting on a bench, newspaper pages bursting out of his hands and flying in the wind; she enters from the left, deadpan. |
| S04 | Side shot: a window cleaner on a tall wooden ladder leaning against a pastel house, the ladder starting to tip away from the wall, his bucket swinging; she walks past an iron lamppost at the foot of the ladder. |
| S05 | Low angle under an autumn tree: a small bird's nest with three blue eggs tumbling off a branch, a mother bird flapping in alarm; she walks underneath, looking straight ahead. |
| S06 | Side shot outside a small café with a striped awning: a waiter in a white apron mid-stumble on the cobbles, teacups starting to slide off his tilted tray; she is passing by. |
| S07 | Small hilltop park: a yellow-and-blue diamond kite tangled high in a bare tree, a little girl in a green coat pointing up at it, about to cry; she stands below looking up deadpan, unwinding the red scarf from her neck. |
| S08 | Same park, wider: the freed kite soaring up into the grey sky with her red scarf tied to it like a long kite tail, the scarf end just slipping out of her fingers; she stands below with a bare neck; the girl cheers. |
| S09 | Side-view shot: she walks from left to right with NO scarf, bare neck, coat collar turned up; the wind has stopped, the last leaves falling straight down; colder, bluer light. |
| S10 | Extreme close-up of her face in profile, nose and half-lidded eye, against a pale cold sky, no scarf, a single tiny snowflake drifting just above the tip of her nose. |
| S11 | Close-up of her face, front view, deadpan, bare neck, coat collar up, a few snowflakes falling around her, cold blue-grey light. |
| S12 首帧 | Medium-wide shot in light snowfall: she stands still on the cobbled street with no scarf, looking up; high above, the long red scarf drifts down out of the sky like a ribbon; far in the background the girl in the green coat holds the kite and waves. |
| S12 尾帧 | **在 S12 首帧上做图片编辑**：Edit this image: the red scarf is now wrapped once around her neck with both ends hanging down, she has a tiny content smile; keep everything else identical. |
| S13 | Back view, wide shot: she walks away up the snowy cobbled street, the red scarf trailing behind her, snow falling, warm light glowing in the windows. |
