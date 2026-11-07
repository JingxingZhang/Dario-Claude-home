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

## 综艺花字版（`render_huazi.py` + `huazi.py`）

背景、天气和小黄花的故事线不变，只把歌词换成综艺花字：

- **字形**：主歌用站酷快乐体（可爱、偏童年感），副歌用 Noto Sans SC Black（冲击力强）
- **分层**：硬投影 → 深色外描边 → 白色内描边 → 竖向渐变填充 → 上半部高光；暗场景下外描边带光晕
- **动效**：逐字回弹弹出（带过冲和旋转）、待机轻微浮动、副歌按节拍放大
- **配色**：每段一套（回忆暖黄 / 雨雾蓝 / 暴雨冰蓝 / 午后橙 / 夜雨紫 / 晴天白黄蓝边），关键词单独配色（小黄花、雨、风、放晴、爱、拜拜）
- **贴纸**：星星闪光、问号、爱心、雨滴、速度线、笑脸太阳，以及「童年回忆杀」「灵魂拷问」「意难平」这类综艺小标签

字体：ZCOOL KuaiLe、Noto Sans SC（Google Fonts，OFL 授权）。

## 专辑原版音频版（`render_huazi_album.py`）

音源换成《叶惠美》专辑原版 FLAC（4:29.75，44.1 kHz/16-bit）。用 chroma 特征逐句比对，把歌词时间轴从旧音源迁移过来：

- 前半段（前奏、主歌、副歌）整体比旧音源晚 0.8 秒
- 旧音源（抖音 4:45 版）是把前奏、主歌、副歌重复拼接出来的；原版结构是 13 秒间奏 → 第二段主歌（从「为你翘课的那一天」开始）→ 副歌 → 30 秒吉他 solo
- 间奏里小黄花回来，少一片花瓣重新开花；吉他 solo 段加入「吉他 Solo」花字、跟着节拍飘的音符，以及一朵新开的花，片尾跟着原曲自然结束
- 音轨：FLAC → AAC 320 kbps
