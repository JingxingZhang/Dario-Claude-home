# 《关键词》64-bit 像素 MV · AI 生成画面提示词

## 分工：哪些交给 AI，哪些留给代码
| 交给 AI 生成（代码画不好的） | 留给代码（代码画得好，而且要动） |
|---|---|
| 人物半身、特写、有表情和手部动作的情绪镜头（13 张） | 天空、云、水面、雪、落叶、城市、银杏大道、房间、车站等 64-bit 背景 |
| 两张角色设定图（给 AI 保持角色一致用） | 走路、递东西、挥手这类要连续动的小人镜头 |
| | 液态玻璃标签、气泡、选择框，花字歌词，转场，所有动态效果 |

AI 生成的图片我会用 `pixelate.py` 转成 64-bit 像素画（原生 960×540，最多 160 色），全片共用一套调色板。然后在代码里给它加上镜头缓推、飘落的叶子和雪、灯光闪烁、玻璃元素和歌词，让定格的插画也有动感。

## 生成规则（每张都要遵守）
1. **生成干净的动漫插画，不要直接生成“像素风”。** AI 画的像素图格子大小不统一，转换效果反而差；干净插画转出来的像素格子才规整。
2. **横版 16:9，至少 1920×1080。**
3. **画面下方三分之一尽量简单**（地面、桌面、水面），主体和人脸放在上方三分之二。下面要放歌词。
4. **角色要一致**：先生成两张角色设定图（R1、R2），之后每张都把设定图当参考图上传（用生成工具的“参考图 / 角色一致性”功能）。把下面的“角色描述块”原样贴进每条提示词。
5. 不要文字、水印、Logo；人物是原创角色，不要像任何真人或明星。
6. 文件名用镜头编号（R1.png、A01.png……），生成好直接发给我。

## 风格后缀（每条都加在最后）
> soft anime illustration, clean lineart, gentle cel shading with soft gradients, warm cinematic lighting, cozy and tender mood, original characters, 16:9, high detail

## 反向提示词（工具支持就填）
> text, watermark, logo, signature, pixel art, 3d render, photorealistic, extra fingers, deformed hands, blurry, low quality, celebrity likeness

## 角色描述块（原样贴进每条提示词）
- **BOY**（“我”）：`a young man in his early 20s with short slightly messy black hair and soft bangs, gentle round face, warm brown eyes, slim build`
  - 秋：`wearing a navy blue knit sweater and dark grey trousers, a yellow pencil tucked behind his right ear`
  - 冬：`wearing a grey-blue wool coat and a cream knit beanie`
  - 第二年秋：`wearing a ginkgo-yellow knit sweater, a red pen tucked behind his right ear`
- **GIRL**（“你”）：`a young woman in her early 20s with a chin-length brown bob haircut, bright warm eyes, soft smile`
  - 秋：`wearing a long cream coat and a red knit scarf`
  - 冬：`wearing a camel wool coat and the same red knit scarf`
  - 第二年秋：`wearing a long cream coat and a red knit scarf`
- 注：原来的分镜没有刻意强调“你”的性别。这里为了生成一致的人物写成了年轻女性；想改成别的样子，把这一块换掉就行，其他提示词不用动。

---

## 角色设定图（先生成这两张）
**R1 · BOY 设定图**
> character reference sheet of [BOY], front view, side view and back view standing on a plain light background, autumn outfit [BOY 秋], plus three small head studies: smiling, surprised, blushing + 风格后缀

**R2 · GIRL 设定图**
> character reference sheet of [GIRL], front view, side view and back view standing on a plain light background, autumn outfit [GIRL 秋], plus three small head studies: smiling, laughing, blushing + 风格后缀

---

## 13 张情绪镜头

**A01 · 初遇（0:21 · 幸福的样子）**
> late autumn afternoon on a quiet avenue lined with golden ginkgo trees, [GIRL 秋] bending slightly and holding out a single sheet of notebook paper she just caught from the wind, smiling kindly; [BOY 秋] in front of her, surprised and shy, reaching to take it; golden leaves drifting in the air, warm sunlight from the left, medium shot + 风格后缀

**A02 · 回头喊名字（0:35 · 当你口中喊我名字）**
> golden ginkgo avenue, [GIRL 秋] a few steps ahead, turning back over her shoulder and waving, calling out with a bright smile, her red scarf fluttering; [BOY 秋] in the foreground seen from behind, slightly out of focus; sunset backlight, falling ginkgo leaves + 风格后缀

**A03 · 第一张合照（0:54 · 这是第一次）**
> close-up selfie of [BOY 秋] and [GIRL 秋] under a golden ginkgo tree, heads tilted together, both smiling, she makes a peace sign, he holds the camera with an outstretched arm, golden leaves around them, warm afternoon light + 风格后缀

**A04 · 忘词（1:31 · 却又忘词）**
> snowy street corner in winter, [BOY 冬] holding a small blank card in both hands, frozen with an awkward nervous expression, blushing; [GIRL 冬] standing in front of him with a gentle amused smile; light snowfall, soft overcast light + 风格后缀

**A05 · 站台暂别（1:38 · 我不怕潜台词）**
> small train platform on a snowy winter afternoon, [GIRL 冬] standing at the open door of a commuter train, waving goodbye with a warm smile, a small suitcase beside her; [BOY 冬] on the platform seen from behind, waving back; light snow, yellow safety line, lit train windows + 风格后缀

**A06 · 车窗雾上画心（1:42 · 是你心中有我名字）**（最难，优先生成）
> view from outside a train window in winter, the glass covered in soft fog, [GIRL 冬] inside the train drawing a heart shape on the fogged window with her fingertip, looking out with a tender smile, the heart area clear so her face shows through it; snowflakes on the glass, warm light inside, cool blue light outside + 风格后缀

**A07 · 视频通话（1:55 · 我们的故事开始）**
> winter night, cozy desk by a window with snow falling outside, [BOY 冬] (beanie on) smiling at a smartphone propped on the desk, the phone screen shows [GIRL 冬] waving in a video call; warm desk lamp light, an open notebook beside him + 风格后缀

**A08 · 雪夜告白（2:12 · 你是我的关键词）**
> snowy night under a single warm street lamp, [BOY 冬] holding open a notebook toward [GIRL 冬]; the page has one large handwritten character on it; she covers her mouth, blushing and surprised; snowflakes glowing in the lamplight, bare snowy branches + 风格后缀

**A09 · 发现藏头（2:18 · 你藏在歌词）**
> night, [GIRL 冬] sitting at a desk under a warm lamp, holding a handwritten notebook close, eyes widening in happy surprise as she reads, one finger tracing down the first column of the page, warm and intimate mood + 风格后缀

**A10 · 一周年（2:44 · 这是第一次）**
> warm late autumn afternoon by a window with golden ginkgo leaves outside, [BOY 第二年秋] and [GIRL 第二年秋] leaning together over a small strawberry cake with a single number-one candle, about to blow it out, both smiling + 风格后缀

**A11 · 送出笔记本（2:47 · 爱一个人爱得如此慷慨又自私）**
> under a large golden ginkgo tree, [BOY 第二年秋] handing a well-worn navy blue notebook to [GIRL 第二年秋] with both hands, a little shy; she receives it with a moved smile; ginkgo leaves falling, golden hour light + 风格后缀

**A12 · 最后一页（2:54 · 你是我的关键词）**
> close-up from above of an open notebook on a wooden desk, the last page, a woman's hand holding a red pen writing on it, the red scarf end visible at the edge of the frame, a pressed ginkgo leaf lying on the page, warm afternoon light + 风格后缀

**A13 · 尾奏背影（2:59 · 尾奏）**
> wide shot of a long golden ginkgo avenue at sunset, [BOY 第二年秋] and [GIRL 第二年秋] seen from behind walking hand in hand into the distance, her red scarf the brightest spot of color, golden leaves falling, long soft shadows + 风格后缀

---

## 拿到图之后
1. 我用 `pixelate.py` 把它们转成 64-bit 像素画，全片共用一套调色板；
2. 把它们排进对应镜头。特写镜头加缓推、飘落物、灯光和玻璃元素，小人镜头照常用代码画；
3. 代码画的小人会按设定图的发型和衣服颜色调整，和 AI 特写对得上。

## 发布时注意
片中有 AI 生成的画面。按《人工智能生成合成内容标识办法》（2025 年 9 月 1 日起施行），发布时要勾选平台的“AI 生成”标识，简介里也写明“部分画面由 AI 生成后像素化处理”。
