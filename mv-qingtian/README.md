# 晴天 · 动态排版歌词 MV 渲染器

纯代码渲染的歌词 MV（1920×1080 / 30fps）：每一帧都由 [skia-python](https://github.com/kyamagu/skia-python) 绘制，没有使用任何视频生成模型或素材。

## 视觉方案

**一句话故事：** 一场雨，从回忆一直下到现在；等到放晴那天，你已经不在。

| 段落 | 时间 | 色调 | 视觉 |
|---|---|---|---|
| 序 Prelude | 0:00–0:28 | 米白纸面 | 标题、小黄花花苞、花茎生长 |
| I 回忆 | 0:28–1:21 | 暖棕旧纸 | 花开、飘走；秋千、五线谱、竖排书页、教室窗格；雨开始落 |
| II 雨 | 1:24–2:21 | 深青暴雨 | 闪电、斜风、玻璃水珠、字被雨打散 / 被风吹远 |
| III 雨后 | 2:21–2:52 | 雾灰 | 花苞回来，涟漪随鼓点扩散 |
| IV 午后 | 2:52–3:45 | 黄昏金 | 小黄花再开，却少了一片花瓣 |
| V 暴雨 | 3:47–4:08 | 夜色 | 雨最大的时候 |
| VI 晴天 | 4:08–4:45 | 天蓝 + 太阳 | “等到放晴的那天”云开、花田盛开；最后一句花瓣被风吹散 |

- **字体**：霞鹜文楷（主歌，手写旧书感）/ Noto Serif SC 可变字重（副歌）/ Cormorant Garamond Italic（英文译文、唱名）
- **节拍**：librosa 测得 68 BPM，主拍驱动副歌缩放脉冲、涟漪、音符弹出
- **每句歌词都有专属动效**：bloom / float / swing / staff / fall / vert / window / question / wind / rainheavy / blurout / distance / storybook / spread / drift / clear

## 使用

```bash
pip install skia-python librosa opencv-python-headless numpy
python tools/analyze_audio.py song.wav audio.json      # 节拍与频段能量
python tools/sub_detect.py                               # 从歌词视频提取字幕时间轴（可选）
# 自行准备 lyrics.py（LINES / CHAPTERS），字体放到 fonts/
python render.py preview prev 30 90 250                  # 预览指定秒数的静帧
python render.py chunk 0 2175 part0.mp4 19               # 分段渲染，可多进程并行
```

`lyrics.py`、音频、字体和成片因版权与体积原因不入库。
