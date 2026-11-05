# 用来转成 32-bit 像素风的照片：要求与 Prompt

## 什么样的照片转出来好看
- **光线有方向**：黄金时段（日出后、日落前）、逆光、路灯和窗光这类明确的光源。转成像素后，明暗分得清，轮廓光会很漂亮。
- **构图简单**：一个主体，前景、中景、远景分得开。草地、人群、树叶这类密集细节，缩小后会变成一团噪点。
- **颜色收敛**：整张图以 2–3 个主色为主（比如紫加橙，或蓝加暖黄）。转像素时要压到 32–64 色，颜色越统一越好看。
- **画面干净**：对焦清晰，没有运动模糊，没有文字和水印，不要相框、不要拼图。
- **规格**：横版 16:9，至少 1920×1080。
- **人物**：MV 里的角色要几十个镜头长得一样，照片里的人做不到这一点。所以人物最好用背影、剪影或远景，或者干脆不拍人。

## 通用后缀（每条 Prompt 后面都加上）
> cinematic photo, golden hour lighting, clear subject, simple composition, strong silhouettes, limited color palette, sharp focus, no text, no watermark, 16:9

## 按《关键词》的故事准备的 6 张
1. **秋天的银杏大道（主歌一、副歌一）**
   > A quiet city avenue lined with golden ginkgo trees in late autumn afternoon, fallen ginkgo leaves covering the stone sidewalk, warm sunlight streaming through the leaves from the left, soft blue sky, no people, eye-level view
2. **深夜书桌（前奏、写词）**
   > A cozy desk by a window at night, an open blank notebook and a pencil under a warm desk lamp, a ginkgo branch visible outside the window with a few golden leaves, deep blue night sky, warm and cool contrast, no people
3. **一片银杏叶落在本子上（小杏的特写）**
   > Macro photo of a single golden ginkgo leaf resting on an open notebook page with faint ruled lines, warm lamp light from the side, shallow depth of field, soft shadows
4. **冬天的小站台（寒假暂别）**
   > A small train platform on a snowy winter afternoon, a commuter train with lit windows waiting at the platform, light snowfall, overcast pale blue sky, yellow safety line on the platform edge, two distant figures seen from behind, calm and quiet mood
5. **雪夜路灯（当面告白）**
   > A snowy street at night with a single warm street lamp, bare tree branches covered in snow, falling snowflakes glowing in the lamplight, deep navy sky, empty sidewalk with a few footprints
6. **湖边城市的晚霞（可做片尾或封面）**
   > A lakeside promenade at sunset, a city skyline in silhouette across the water with lit windows, layered pink and orange clouds, the setting sun reflecting as a golden path on calm water, a railing in the foreground, purple and orange color palette

## 拿到照片之后我怎么处理
缩到 320×180 或 480×270，提取 32–64 色调色板，用有规律的点阵表现渐变，把明暗分成几级色阶，主要轮廓加深色描边，最后按整数倍放大。生成好的照片直接发给我就行。
