# 工具速查（lib/）

这些是画画用的工具，不是模板：人物、场景、配色都按这首歌设计（见 visual-design.md）。
坐标一律是原生画布 320×180；底部 y≥120 留给歌词花字和署名，画面里的字和道具尽量放在 y<120。
角色、宠物的 `x, y` 是**脚底中点**；`face` / `face_dir` 为 1 朝右、-1 朝左。

## 常用手法
- 设计角色：`charkit.pixmap(字符画, 调色表)` → `put(img, spr, x, y, scale, face)`；多帧动作按 `lt` 选帧；表情用 `eyes()` 和 `mouth()` 叠加，或者每种表情各画一个头。
- 任何东西会演戏：先画形状，再 `face(img, cx, cy, expr)`；expr 可选 happy shock sad side sleep blush smirk scream laugh heart dead。
- 综艺强调：`burst()` / `dots_bg()` 背景 + `concentration()` 集中线 + `sfx(…, slam=True)` / `stamp()`。
- 系统梗：`popup()` + `cursor()`、`sys_msg()`、`meter()`、`toggle()`、`danmaku()`。
- 背景：`dither_grad()` 抖动渐变、`draw_sky()` 带太阳的天空、`draw_water()` 水面；`props2` 里有山、海、T 台、审讯室、摩天轮等道具。
- 时间：`seg(lt, a, b)` 0→1 进度，`ease()` 缓动，`hsh()` 确定性随机（不要用 random）。
- 音乐：`pump(t)` 鼓点脉冲，`rms(t)` 音量，`beat_phase(t)` 距上一拍的秒数。


## charkit — 角色设计

- `eyes(img, x, y, kind='dot', gap=4, col=(34, 24, 44), scale=1)` — 在 (x,y) 起画一双眼睛（左眼左上角），gap 为两眼间距（原生像素，未放大前）。
- `light(col, k=0.3)`
- `mouth(img, x, y, kind='smile', col=(34, 24, 44), scale=1)` — 嘴：smile 微笑 / grin 大笑（带红） / o 惊讶 / flat 一字 / sad 撇嘴 / smirk 坏笑 / wave 波浪（委屈）
- `palette_strip(img, x, y, cols, size=8)` — 设定图上的配色条
- `pixmap(art, pal, outline=(34, 24, 44), shade=None)` — 字符画 → RGBA 精灵。'.' 和空格是透明；outline=None 不描边；shade=(字符, 比例) 可自动生成暗面色
- `put(img, spr, x, y, scale=1, face=1, anchor='feet')` — 把精灵贴到画布：anchor='feet' 时 x,y 为脚底中点；'center' 为中心；'topleft' 为左上角
- `recolor(art_pal, **over)` — 复制一份调色表并替换部分颜色（同一角色换季、换装，随故事时间线换色时用）
- `shade(col, k=0.3)`

## pixlib — 底层

- `blit_mask(arr, m, x, y, col, scale=1)`
- `clamp(x, a=0.0, b=1.0)`
- `disc(d, cx, cy, r, col)`
- `dither_grad(h, w, c_top, c_bot, levels=7)` — 竖向渐变 + 4×4 Bayer 抖动，量化成 levels 档
- `draw_sky(img, tod, hz=104, sun=True, stars=0.0, t=0.0)`
- `draw_text(img, x, y, s, col, scale=1, shadow=None, gap=0, colors=None, outline=None)` — 在 PIL 图上画像素字；colors 可逐字给颜色；返回宽度
- `draw_vtext(img, x, y, s, col, shadow=None)`
- `draw_water(img, t, tod, hz=104, red=0.0, choppy=0.3, y1=180)`
- `ease(x)`
- `glyph(ch)` — 返回 (mask ndarray bool, advance)
- `hsh(*v)` — 确定性伪随机 0..1
- `lerp(a, b, k)`
- `lerpc(c1, c2, k)`
- `seg(t, a, b)` — t 在 [a,b] 内的进度 0..1
- `sepia(img, k=1.0)`
- `sky_colors(tod)`
- `sun_pos(tod, hz)` — 太阳沿弧线从东（右）升到西（左）落
- `text_w(s, scale=1, gap=0)`
- `tint(img, col, k)`

## props2 — 综艺元素、会演戏的物件、宠物、场景道具

- `OS(img, x, y, s, t, born)`
- `big_heart_building(img, ground, t, k=1.0)` — 楼群窗户亮成一颗心
- `bubble_box(img, x, y, w, h, bg=(250, 248, 240), edge=(34, 24, 44), tail='l')`
- `building_face(img, x, ground, w, h, expr='shock', col=(46, 38, 90), win=(255, 210, 120))` — 一栋会做表情的楼：窗户亮灯拼出眼睛和嘴
- `calendar_face(img, x, y, label, expr='happy', flip=0.0)`
- `cat(img, x, y, t=0.0, pose='sit', expr='normal', face_dir=1, scale=2, sign=None, glasses=False, hat=None, hearts=False)` — 橘猫：x,y 为脚底中点。pose: sit / walk / sleep / hiss / roll / up(举牌)
- `clapper(img, x, y, t, snap)`
- `clock_face(img, cx, cy, r, t, expr='scream', shake=True)`
- `cloud_face(img, cx, cy, expr='happy', col=(250, 250, 255), k=1.0)` — 会演戏的云朵（下雨天的配角、天气类歌曲的贯穿物件）
- `cup_face(img, cx, cy, expr='happy', col=(250, 246, 236), drink=(150, 90, 60), steam=0.0)` — 一杯会演戏的饮料（咖啡/奶茶），t 传给 steam 让热气飘
- `cursor(img, x, y)`
- `danmaku(img, t, items, t0=0.0, y0=18, rows=3, speed=70)` — 弹幕：items = [(出现时刻, 文字, 颜色)]
- `dog(img, x, y, t=0.0, pose='sit', expr='normal', face_dir=1, scale=2, sign=None, hearts=False, col=(236, 236, 236), ear=(150, 110, 80))` — 小狗（垂耳、摇尾巴）。pose: sit / walk / up(举牌) / jump。参数和 cat() 一致，方便互换。
- `face(img, cx, cy, expr='happy', k=1, col=(34, 24, 44))` — 在物件上画一张小脸（eyes 间距 6k）
- `ferris(img, cx, cy, r, t, col=(255, 140, 200))`
- `firework(img, cx, cy, t, born, col)`
- `heart_face(img, cx, cy, k=2, expr='happy', broken=False, col=(240, 60, 100))`
- `interrogation(img, t, swing=True)`
- `lamp(img, x, ground, expr='happy', on=True, h=70)`
- `megaphone(img, x, y, t, face_dir=1)`
- `meter(img, x, y, label, v, col=(255, 70, 110), w=70, show_pct=True, blink=False)`
- `moon(img, cx, cy, r=12, expr='happy', col=(250, 240, 200), blush=False)`
- `mountains(img, scroll=0.0, ground=128)`
- `phone_face(img, x, y, w=60, h=104, expr=None)`
- `pop(img, x, y, s, t, born, dur=9.0, scale=2, c1=(250, 248, 240), c2=None, ring=(250, 248, 240), out=(34, 24, 44), jitter=0, slam=False)` — 动态像素花字：弹出（slam=True 为盖章式从大砸下），dur 后消失
- `popup(img, x, y, title, msg, btns=('是', '否'), sel=0, pressed=False, w=150)` — 复古系统弹窗
- `ptext(img, x, y, s, scale=2, c1=(250, 248, 240), c2=None, ring=(250, 248, 240), out=(34, 24, 44), anchor='c', shadow=True)`
- `rainbow(img, cx, cy, r, k=1.0)`
- `runway(img, t, v2=False)`
- `safe_box(img, x, y, closed, locked)`
- `say(img, x, y, s, t=None, born=None, tail='l', bg=(250, 248, 240), fg=(34, 24, 44), cps=16, os_=False)` — 说话 / 内心 OS 气泡（打字机效果）。x,y 为气泡左上角
- `score_card(img, x, y, s)`
- `scroll_list(img, x, y, items, k, t)`
- `sfx(img, x, y, s, t, born, dur=1.2, pal='yel', scale=2, jitter=1, slam=False)`
- `slot_machine(img, x, y, t, stops, results, lever=0.0)` — 老虎机：stops=每格停的时刻，results=停下的表情
- `stamp(img, cx, cy, s, t, born, col=(230, 40, 60), dur=99, scale=2)` — 印章：方框 + 字，从大砸下
- `star_face(img, cx, cy, r=9, expr='happy', col=(255, 226, 90))`
- `sun(img, cx, cy, r=12, expr='happy', t=0.0)`
- `sys_msg(img, cx, y, s, col=(120, 120, 140))`
- `toggle(img, x, y, label, on)`
- `trash_face(img, x, y, expr='happy', lid=0.0)`
- `wave_sea(img, t, y0=110, col=(60, 150, 220))`

## chars — 小道具、背景特效、Q 版小人脚手架

- `R(d, x, y, w, h, c)`
- `bang(img, x, y, n=2, col=(255, 70, 90))`
- `big_button(img, cx, cy, pressed, label='离开')`
- `burst(img, t, c1, c2, cx=160, cy=90, n=16)` — 放射背景（综艺感）
- `calendar(img, x, y, label, col=(240, 70, 80), flip=0.0)`
- `chat_bubble(img, x, y, w, h, col, right=False)`
- `clock(img, cx, cy, r, t)`
- `concentration(img, cx, cy, t, col=(255, 255, 255), n=40, r0=60)` — 集中线
- `curtains(img, k, t)` — 舞台幕布：k=0 全开，1 全关
- `dial(img, cx, cy, r, ang)` — 情绪表盘：ang 0..1（0 难过 → 1 心动）
- `dots_bg(img, t, c1, c2, step=14)`
- `ellipse_fill(d, cx, cy, rx, ry, col)`
- `envelope(img, x, y, open_k=0.0)`
- `heart(img, cx, cy, k=1, col=(240, 60, 100), broken=False)`
- `magnifier(img, x, y, r=8)`
- `make_look(name, base='boy', **kw)` — 新建角色外观并注册，例如 make_look('grandpa', 'boy', hair_style='bald', hair=(220,220,220), beard=True, body='shirt')。
- `outline_rgba(im, col=(34, 24, 44))`
- `paste(img, spr, x, y)`
- `person(img, x, y, who='girl', face=1, expr='smile', arm='down', t=0.0, scale=2, walk=False, umbrella=None, glasses=False, kneel=False, horns=False, mask=False, breathe=0.0)` — 通用 Q 版小人（脚手架）：只用于快速试画、路人群演。主角和重要角色请按歌用 charkit 从零设计。
- `phone_big(img, x, y, w=70, h=120, lit=True)`
- `qmark(img, x, y, col=(255, 230, 90))`
- `rose(img, x, y)`
- `scaled(spr, k)`
- `scooter(img, x, y, t)`
- `sign_board(img, x, y, w, h, t)`
- `sparkle(img, x, y, r=3, col=(255, 250, 200))`
- `spotlight(img, cx, top, bot, r, col=(255, 250, 200), k=0.35)`
- `sweat(img, x, y, k=1)`
- `trash(img, x, y)`
- `vein(img, x, y)`
- `wave_line(img, y0, t, amp, col, x0=0, x1=320, speed=1.0, beat=0.0)`

## scenes_common — 霓虹街、雨、窗边（歌词需要时才用）

- `rain(img, t, k, ground=180)`
- `room(img, t, v2=False, fog=0.0, rain_k=1.0)` — 室内窗边（向原视频的雨夜窗景致意）
- `street(img, t, v2=False, scroll=0.0, ground=128, rain_k=0.8, neon=None)`

## refine — 角色精修（迭代二画风）
- `render_char(img, art, pal, x, y, face_dir, eye=(列, 行, 间距), mth=(列, 行), expr='smile', bob=0)` — 精修角色：Scale2x + 体积光影 + 彩色描边 + 高清五官；x,y 脚底中点；大小等于原来 scale=2
- `refined_sprite(art, pal)` — 没有五官的物件、宠物的精修精灵
- `EXPR` — 表情表：normal smile happy blush shock stuck think sad heart zip；`face_hd(...)` 底层五官绘制

## style — 迭代二画风的背景工具与高清光影层
- `grad3(h, w, c0, c1, c2)` 三段渐变；`glow_np(img, cx, cy, r, col, k)` 柔和光晕
- `sky(img, t, season, tod, hz)`（自动登记调色键）、`sky_key(season, tod)`、`cloud(...)`、`city(img, hz, season, key)`
- `tree(img, x, ground, season, k)`、`crown / trunk / branches`、`ground_fill(img, ground, season, scroll, tod)`、`snowfall(img, t, n)`、`falling_leaves(img, t, n, scroll, ground, season)`
- season 预设：autumn year2 summer spring winter（来自《关键词》，换歌就改 `LEAF_TONES`、`SKY`）
- `mark(img)` — 背景画完时调用，登记背景快照（景深、轮廓光用）；`set_grade(key)` — 手动指定调色：day gold dawn winter night wnight None

## glassui — 液态玻璃组件（详见 liquid-glass.md）
在镜头函数里登记，引擎放大画面后统一画。坐标默认原生（320×180）；born=出现时刻（全片秒），None=常驻。
- `gchip(t, born, cx, cy, text, col=TXT, size=50, tint=白, tint_a=0.12, dur=99, minw=0, hd=False)` — 玻璃胶囊标签，字色按底色自动深浅
- `gtag(t, born, cx, cy, text, pal='yel', size=54)` — 按配色名着色的标签（yel pink cyan red purp green white）
- `gcard(t, born, cx, cy, hw, hh, r=30, tint, tint_a, refr, mag, content=fn(big,X,Y,HW,HH,lum), sdf=fn(HW,HH)->(px,py)->d)` — 任意玻璃卡片 / 形状
- `gheart(t, born, cx, cy, size)` — 心形玻璃窗；`glens(t, cx, cy, r, refr, mag)` — 圆形透镜；`gdrop(t, born, cx, cy, r)` — 溅起的玻璃水珠
- `bubbles(t, n, seed, x0, x1, y0, y1, r0, r1, speed)` — 上浮的玻璃水滴（氛围）
- `gmove(t, born, a=(x,y,hw), b=(x,y,hw), hh=15)` — 液态选择框从 a 流到 b
- `gsearch(t, born, cx, cy, hw, query, result)` — 玻璃搜索框（打字 + 结果淡入）
- `gsign(cx, cy, text, scale=2)` — 配角头顶的玻璃小牌
- `say / OS / popup / meter` — 同名覆盖 props2 的版本（参数兼容），变成玻璃气泡、深色玻璃 OS、玻璃提示卡、玻璃液体进度条；popup 多一个 born 参数

## glass — 液态玻璃材质（底层）
- `glass(big, cx, cy, hw, hh, sdf=None, t, tint, tint_a, bezel, refr, mag, blur, shadow, alpha, spec, lift, light)` — 在 1080p 帧上画一块玻璃，返回玻璃内的平均亮度（用于选字色）
- `sdf_rrect(px, py, hw, hh, r)`、`sdf_circle(px, py, r)`、`sdf_heart(px, py, s)`、`sdf_union(*ds, k)` — 形状距离场，可平滑合并
- `spring(dt)` — 带过冲的弹簧 0→1；`htext(big, x, y, s, size, col, anchor='c')` — 高清文字；`tw(s, size)` — 文字宽度；`ink(col, lum)` — 按底色选字色
- `post(big, bloom=0.22, vig=0.14)` — 整帧柔光 + 暗角（任意尺寸）

## cover — 3:4 封面
- `portrait_from(scene320x180, x0=70, top=60)` — 把横版场景裁成 180×240 竖版并补天空
- `build_3x4(draw_native, t, title, artist, tag, signature, title_style)` — 竖版封面合成（scripts/cover.py 调用）

## huazi — 高清花字

- `draw_sticker(base, kind, x, y, size, t, born, seed=0)`
- `font(ch, size, fam='zcool-qingke-huangyou')`
- `grad(w, h, c1, c2, y0, y1)`
- `pill(base, cx, cy, text, size=60, fg=(255, 255, 255), bg=(40, 20, 60), edge=(255, 110, 170), fam='zcool-kuaile', alpha=1.0)`
- class `Line(self, t0, t1, text, pal='white', kw=None, kwpal='pink', size=120, cx=960, cy=830, angle=0.0, deco=(), kwscale=1.3, stagger=0.05, pop=1.28, float_amp=5, shake=0, beat_kick=0.08)` — 动效随曲风调：pop 入场回弹（抒情 1.08、默认 1.28、燃 1.45），stagger 逐字间隔（快歌 0.03、慢歌 0.09），

## engine — 引擎

- `build_lyrics(song, cfg, base=None)` — cfg：列表（按句序）或 dict（键为句序号，或直接用歌词原文——重复的句子自动共用一套样式），每项是 Z.Line 的参数；kw 可配 kwpal 为列表实现多组重点词各自换色。
- class `MV(self, song, shots, cfg, danmu=None, title_style=None, replay_label='回放 REPLAY', tag='像素 MV', lyric_base=None, glass=True, lyric_dock=True, sections=None, post_fx=True, hd_light=True)` — hd_light：迭代二高清光影层（景深、轮廓光、光束、调色）； lyric_base：全曲歌词花字的基调（按曲风定），如 dict(pop=1.08, stagger=0.09, float_amp=3) 抒情、dict(pop=1.45, stagger=0.03, shake=5) 燃。glass：液态玻璃层开关；lyric_dock：歌词玻璃托盘；sections：段落切换时刻（玻璃透镜横扫）；post_fx：柔光 + 暗角。danmu / replay_label 只为兼容旧项目，新流程不用回放。
- class `Song(self, root)` — Initialize self.  See help(type(self)) for accurate signature.

## sticker — 表情包

- `cursor_to(img, lt, x0, y0, x1, y1, t0=0.1, t1=0.75)`
- `gift_box(img, cx, cy, t, label='礼物', open_k=0.0, col=(240, 80, 120), ribbon=(255, 214, 90))`
- `ticket(img, x, y, label='优先券', col=(255, 214, 80))`
- `ui_button(img, cx, cy, label, done_label, done, press=False, col=(250, 60, 90), done_col=(150, 150, 165), icon=None, w=62, fg_done=(250, 248, 240))` — 一枚像素按钮（关注 / 推荐 / 收藏…），icon(d, x, y) 可画左侧小图标
- class `Sticker(self, pixel, text, kw=None, pal='yel', kwpal='pink', pill=None, pill_bg=(60, 20, 70), size=138, deco=('heart', 'star', 'bang'))` — pixel(t) -> 180×180 RGB 像素层；text 用 / 分两行；pill 为底部标签（表情包默认不加署名）

## 取值表
- Q 版小人 `person(expr=…)`（仅试画、路人）：smile wink happy closed heart surprised side angry pout sad smirk blush shy
- `person(arm=…)`：down wave point phone heart(比心) shrug cover(捂脸) hold(双手递东西) ear(侧耳) fist umbrella chest(捂胸口)
- `person(…)` 开关：walk umbrella=颜色 glasses kneel horns mask breathe=起伏像素
- `make_look(name, base, hair_style=long|short|bob|ponytail|bun|bald, body=dress|hoodie|shirt|suit|uniform, beard=True, clip=颜色或None, blush=True, hair=…, cloth=…, legs=…, shoe=…, tie=…)`
- `cat/dog(pose=…)`：cat：sit walk sleep hiss roll up；dog：sit walk up jump。`expr`：normal side shock happy heart angry cover(猫)/sad(狗)。`sign='文字'` 举牌，`hat=police|goggle`（猫），`glasses=True`
- `sfx(pal=…)`：yel red pink cyan green purp white；`scale=1` 小字（只描深色边，清晰），`scale=2` 大字；`slam=True` 盖章式砸下
- 花字配色 `pal/kwpal`：pink yel cyan red purp green white whiteb；贴纸 `deco`：heart heart2 star bang q sweat x note crack drop horn wave
