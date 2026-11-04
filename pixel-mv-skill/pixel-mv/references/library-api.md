# 素材库速查（lib/）

坐标一律是原生画布 320×180；`scale=2` 的人物约 82 px 高。底部 y≥120 留给歌词花字和署名，画面里的字和道具尽量放在 y<120。
人物、猫、狗的 `x, y` 是**脚底中点**；`face` / `face_dir` 为 1 朝右、-1 朝左。表情和动作名见各函数说明。

## 常用组合
- 两人对戏：`street(img, t, v is True, scroll=…, rain_k=…)` → `person(…ME…)` + `person(…YOU…)` → 配角 → 像素花字（`sfx` / `say` / `OS` / `stamp`）。
- 综艺强调：`burst()` 或 `dots_bg()` 背景 + `concentration()` 集中线 + `sfx(…, slam=True)`。
- 系统/手机梗：`phone_face()`、`chat_bubble()`、`popup()` + `cursor()`、`sys_msg()`、`meter()`、`toggle()`。
- 任何东西会演戏：先画形状，再 `face(img, cx, cy, expr)`；表情有 happy shock sad side sleep blush smirk scream laugh heart dead。
- 时间：`seg(lt, a, b)` 0→1 进度，`ease()` 缓动，`hsh()` 确定性随机（不要用 random，否则每帧不同、渲染会抖）。
- 音乐：`pump(t)` 鼓点脉冲 0–1，`rms(t)` 音量 0–1，`beat_phase(t)` 距上一拍的秒数。


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

## chars — 人物与小道具

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
- `person(img, x, y, who='girl', face=1, expr='smile', arm='down', t=0.0, scale=2, walk=False, umbrella=None, glasses=False, kneel=False, horns=False, mask=False, breathe=0.0)` — x,y：脚底中点（原生坐标）。face=1 朝右，-1 朝左。
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

## props2 — 综艺元素、配角、会演戏的物件、场景道具

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

## scenes_common — 通用背景

- `rain(img, t, k, ground=180)`
- `room(img, t, v2=False, fog=0.0, rain_k=1.0)` — 室内窗边（向原视频的雨夜窗景致意）
- `street(img, t, v2=False, scroll=0.0, ground=128, rain_k=0.8, neon=None)`

## huazi — 高清花字

- `draw_sticker(base, kind, x, y, size, t, born, seed=0)`
- `font(ch, size, fam='zcool-qingke-huangyou')`
- `grad(w, h, c1, c2, y0, y1)`
- `pill(base, cx, cy, text, size=60, fg=(255, 255, 255), bg=(40, 20, 60), edge=(255, 110, 170), fam='zcool-kuaile', alpha=1.0)`
- class `Line(self, t0, t1, text, pal='white', kw=None, kwpal='pink', size=120, cx=960, cy=830, angle=0.0, deco=(), kwscale=1.3, stagger=0.05)`

## engine — 引擎

- `build_lyrics(song, cfg)` — cfg：列表（按句序）或 dict（键为句序号，或直接用歌词原文——重复的句子自动共用一套样式），每项是 Z.Line 的参数；kw 可配 kwpal 为列表实现多组重点词各自换色。
- class `MV(self, song, shots, cfg, danmu=None, title_style=None, replay_label='回放 REPLAY', tag='像素 MV')`
- class `Song(self, root)`

## sticker — 表情包

- `cursor_to(img, lt, x0, y0, x1, y1, t0=0.1, t1=0.75)`
- `gift_box(img, cx, cy, t, label='礼物', open_k=0.0, col=(240, 80, 120), ribbon=(255, 214, 90))`
- `ticket(img, x, y, label='优先券', col=(255, 214, 80))`
- `ui_button(img, cx, cy, label, done_label, done, press=False, col=(250, 60, 90), done_col=(150, 150, 165), icon=None, w=62, fg_done=(250, 248, 240))` — 一枚像素按钮（关注 / 推荐 / 收藏…），icon(d, x, y) 可画左侧小图标
- class `Sticker(self, pixel, text, kw=None, pal='yel', kwpal='pink', pill=None, pill_bg=(60, 20, 70), size=138, deco=('heart', 'star', 'bang'))`

## 取值表
- `person(expr=…)`：smile wink happy closed heart surprised side angry pout sad smirk blush shy
- `person(arm=…)`：down wave point phone heart(比心) shrug cover(捂脸) hold(双手递东西) ear(侧耳) fist umbrella chest(捂胸口)
- `person(…)` 开关：walk umbrella=颜色 glasses kneel horns mask breathe=起伏像素
- `make_look(name, base, hair_style=long|short|bob|ponytail|bun|bald, body=dress|hoodie|shirt|suit|uniform, beard=True, clip=颜色或None, blush=True, hair=…, cloth=…, legs=…, shoe=…, tie=…)`
- `cat/dog(pose=…)`：cat：sit walk sleep hiss roll up；dog：sit walk up jump。`expr`：normal side shock happy heart angry cover(猫)/sad(狗)。`sign='文字'` 举牌，`hat=police|goggle`（猫），`glasses=True`
- `sfx(pal=…)`：yel red pink cyan green purp white；`scale=1` 小字（只描深色边，清晰），`scale=2` 大字；`slam=True` 盖章式砸下
- 花字配色 `pal/kwpal`：pink yel cyan red purp green white whiteb；贴纸 `deco`：heart heart2 star bang q sweat x note crack drop horn wave
