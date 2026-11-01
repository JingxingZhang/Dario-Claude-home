// 示例分镜：《江水在涨》前 75 秒（前奏 → 主歌1 → 副歌 → 主歌2 → 副歌 → 间奏）。
// 写法：镜头按歌词切（L(n).start 是第 n 句开口的时间），主歌是版画画面，副歌是大字排版 + 右侧画框。
// 每个 sh.el({...}, o => …) 是一块“印好的版”：只印一次，之后只做移动、缩放、显隐。
const F = BH.film();
const S = F.song, L = S.line, B = S.beatPeriod;
const pre = (n, d = 0.35) => L(n).start - d;              // 第 n 句开口前一点切镜头（落在拍上更好：S.snap(t)）

// ---------- 主题栏：每段一句（迪伦式：一个具体画面，不解释）----------
F.topic(0, '1363年，水先到了');
F.topic(S.sec(2).start, '城里坐着名义上的皇帝');
F.topic(S.sec(3).start, '江水在涨');
F.topic(S.sec(4).start, '长衫客只说了八个字');
F.topic(S.sec(5).start, '江水还在涨');
F.topic(S.sec(6).start, '一图看懂');
F.topic(S.duration - 3.2, '换了是你');

// ---------- 前奏：第 0 帧就是封面 ----------
F.shot('title', 0, (sh) => {
  sh.el({ depth: 0.2 }, (o) => { BH.sky(o, 0, 640, 11); BH.sun(o, 1560, 470, 150); });
  sh.el({ depth: 0.4 }, (o) => { BH.mount(o, 1100, 1980, 680, 200, 5, 0.6); BH.mount(o, -60, 760, 690, 150, 8, 0.5); });
  const w = [0, 1, 2].map((ph) => sh.el({ depth: 0.8, box: [0, 620, 1920, 460] }, (o) => { BH.waves(o, 640, 1080, 60, 3, 0.35, 1.3, ph); BH.crests(o, 650, 9, 240, 46, ph); }));
  sh.cycle(w, { period: B / 2 });                                          // 三张水纹交替：水在动
  sh.el({ depth: 0.8, box: [120, 440, 380, 300] }, (o) => BH.boat(o, 300, 700, 0.8)).bob({ amp: 6 }).sway({ deg: 2 });
  sh.el({ depth: 1, box: [400, 170, 1120, 380] }, (o) => BH.titleCard(o, { title: F.vars.songTitle || '江水在涨', sub: '一三六三' }));
  sh.push(1.08, { fy: 520 });
  F.kickBeats(4, S.sec(2).start, { every: 4, amt: 4 });
});

// ---------- 主歌1 ----------
F.shot('rider', pre(1), (sh) => {
  sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 600, 21); BH.sun(o, 1500, 420, 150); });
  sh.el({ depth: 0.35 }, (o) => { BH.mount(o, 700, 2000, 720, 380, 12, 0.75); BH.mount(o, -100, 1100, 740, 250, 14, 0.55); });
  sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => { BH.ground(o, 760, 1080, 5); BH.shadow(o, 900, 868, 420, 26, 0.35); });
  const legs = [0, 1].map((ph) => sh.el({ box: [440, 280, 920, 620] }, (o) => BH.horse(o, 900, 862, 1.75, { phase: ph })));
  sh.cycle(legs, { period: B / 2 });
  legs.forEach((e) => e.bob({ amp: 5, period: B / 2 }).drift({ x: 160 }));
  sh.push(1.06);
}, { transition: 'paper' });

F.shot('throne', pre(3), (sh) => {
  sh.el({ depth: 0.3 }, (o) => {
    o.blueT.fillStyle = BH.tone(0.55); o.blueT.fillRect(0, 0, 1920, 760); o.knockRect(0, 0, 1920, 760);
    for (const wx of [180, 1440]) {
      BH.erase(o.blueT, (c) => c.fillRect(wx, 200, 300, 400));
      o.blue.save(); o.blue.beginPath(); o.blue.rect(wx, 200, 300, 400); o.blue.clip(); BH.sky(o, 200, 600, wx); o.blue.restore();   // 窗外的天
      for (let i = 0; i < 4; i++) { const fx = wx + 40 + i * 70; o.red.beginPath(); o.red.moveTo(fx, 420); o.red.lineTo(fx + 44, 436); o.red.lineTo(fx, 452); o.red.fill(); o.ink.lineWidth = 3; o.ink.beginPath(); o.ink.moveTo(fx, 600); o.ink.lineTo(fx, 410); o.ink.stroke(); }
      BH.windowFrame(o, [wx, 200, 300, 400], 4, 5, 10);
    }
    const k = o.ink; k.lineWidth = 3; for (let i = -12; i <= 12; i++) { k.beginPath(); k.moveTo(960 + i * 40, 760); k.lineTo(960 + i * 190, 1080); k.stroke(); }
    for (const yy of [790, 830, 885, 960, 1060]) { k.beginPath(); k.moveTo(0, yy); k.lineTo(1920, yy); k.stroke(); }
    k.lineWidth = 6; k.beginPath(); k.moveTo(0, 760); k.lineTo(1920, 760); k.stroke();
  });
  sh.el({ box: [560, 280, 800, 620] }, (o) => { BH.shadow(o, 960, 866, 330, 30, 0.6); BH.throne(o, 960, 860, 1.55, { sitter: 0.36 }); });
  sh.camSet({ zoom: 1 }).camTo({ zoom: 1.25, fy: 680 }, { at: 0.5, ease: 'power1.inOut' });   // 推近：椅子很大，人很小
}, { transition: 'cut', res: 1.3 });

F.shot('home', pre(5), (sh) => {
  sh.el({ depth: 0.2 }, (o) => BH.sky(o, 120, 900, 33));
  sh.el({ box: [0, 0, 1920, 900] }, (o) => { BH.archWall(o, [0, 0, 1920, 900], [960, 340, 400]); BH.doors(o, 960, 300, 900, 400); });
  sh.el({ box: [0, 890, 1920, 190] }, (o) => BH.ground(o, 900, 1080, 9));
  sh.el({ box: [900, 420, 120, 180], depth: 1 }, (o) => BH.lantern(o, 960, 520, 1.0, false)).sway({ deg: 3 });   // 灯没有点
  sh.push(1.1, { fy: 520 });
});

// ---------- 副歌：大字（一字一印，唱到哪砸到哪）+ 右侧画框 ----------
F.shot('refrain-1', pre(7, 0.25), (sh) => {
  sh.el({ box: [1000, 160, 860, 740], depth: 0.5 }, (o) => BH.frame(o, [1040, 200, 780, 640], (p) => { BH.sky(p, 200, 560, 71); BH.waves(p, 520, 840, 40, 4, 0.4, 1.2, 0); BH.boat(p, 1430, 600, 0.9); }));
  sh.type(7, { box: [110, 210, 860, 660] });
  sh.push(1.04);
}, { transition: 'split' });
F.shot('refrain-2', pre(8, 0.2), (sh) => {
  sh.el({ box: [1000, 160, 860, 740], depth: 0.5 }, (o) => BH.frame(o, [1040, 200, 780, 640], (p) => { BH.nightSky(p, 840, 66, [1240, 330, 70]); BH.waves(p, 600, 840, 30, 6, 0.55); BH.boat(p, 1450, 760, 1.2); BH.grinder(p, 1380, 742, 0.75, { sparks: false }); }));
  sh.type(8, { box: [110, 210, 860, 660], scale: [0.62, 1] });
});

// ---------- 主歌2 ----------
F.shot('door', pre(9), (sh) => {
  sh.el({ depth: 0.2 }, (o) => BH.sky(o, 140, 900, 34));
  sh.el({ box: [0, 0, 1920, 910] }, (o) => { BH.archWall(o, [0, 0, 1920, 900], [960, 340, 400]); BH.doors(o, 960, 300, 900, 400); });
  sh.el({ box: [0, 890, 1920, 190] }, (o) => { BH.ground(o, 900, 1080, 9); o.blueT.fillStyle = BH.tone(0.8); o.blueT.beginPath(); o.blueT.moveTo(905, 905); o.blueT.lineTo(1015, 905); o.blueT.lineTo(1180, 1080); o.blueT.lineTo(860, 1080); o.blueT.fill(); });
  sh.el({ box: [860, 360, 200, 560] }, (o) => BH.robed(o, 960, 905, 1.25)).from({ alpha: 0 }, { at: 0, dur: 0.8 });
  sh.push(1.12, { fy: 600 });
}, { transition: 'paper' });

F.shot('eight', pre(10), (sh) => {
  sh.el({ box: [300, 130, 1320, 760] }, (o) => BH.bookPage(o, {
    center: '明史卷一百二十八', seal: '诚意伯',
    cols: [{ text: '太祖将救安丰' }, { text: '刘基谏曰' }, { text: '汉吴伺隙', size: 140, color: 'red' }, { text: '未可动也', size: 140 }, { text: '太祖不听' }],
    pic: (p, r) => { BH.sky(p, r[1], 600, 44); BH.mount(p, r[0] - 40, r[0] + r[2] + 40, 620, 250, 31, 0.7); BH.waves(p, 600, r[1] + r[3], 30, 4, 0.3, 1.2); BH.sun(p, 760, 330, 60); BH.profile(p, 470, 700, 0.7, { flip: true }); },
  }));
  sh.camSet({ zoom: 1.0 }).camTo({ zoom: 1.28, fx: 1220, fy: 470 }, { at: 0.6, dur: 2.2 });   // 推到那八个字
  sh.kick(L(10).chars.find((c) => c.c === '汉').s - sh.t0, 10);
});

F.shot('leave', pre(11), (sh) => {
  sh.el({ depth: 0.15 }, (o) => { BH.sky(o, 0, 640, 51); BH.sun(o, 380, 470, 120); });
  sh.el({ depth: 0.35 }, (o) => BH.mount(o, -100, 2000, 720, 300, 52, 0.7));
  sh.el({ depth: 0.9, box: [0, 740, 1920, 340] }, (o) => BH.ground(o, 760, 1080, 53));
  const legs = [0, 1].map((ph) => sh.el({ box: [1000, 380, 700, 520] }, (o) => BH.horse(o, 1350, 862, 1.3, { phase: ph, flip: true })));
  sh.cycle(legs, { period: B / 2 });
  legs.forEach((e) => e.bob({ amp: 4, period: B / 2 }).to({ x: -760, scale: 0.7 }, { at: L(12).start - sh.t0, dur: L(13).start - L(12).start }));   // 跨上马，越走越远
}, { transition: 'wipe' });

F.shot('lookback', pre(13), (sh) => {
  sh.el({ depth: 0.2 }, (o) => BH.sky(o, 0, 700, 61));
  sh.el({ depth: 0.5 }, (o) => { BH.mount(o, 900, 2000, 700, 220, 62, 0.6); BH.waves(o, 700, 900, 30, 63, 0.35); });
  sh.el({ box: [0, 860, 1920, 220] }, (o) => BH.ground(o, 880, 1080, 64));
  sh.el({ box: [380, 380, 260, 520] }, (o) => BH.profile(o, 500, 885, 1.15));
  sh.el({ box: [1180, 380, 260, 520] }, (o) => BH.profile(o, 1300, 885, 1.15, { flip: true })).from({ alpha: 0 }, { at: L(14).start - sh.t0, dur: 0.4 });
});

// ---------- 副歌（再来一遍，换画框里的画）----------
F.shot('refrain-3', pre(15, 0.25), (sh) => {
  sh.el({ box: [1000, 160, 860, 740], depth: 0.5 }, (o) => BH.frame(o, [1040, 200, 780, 640], (p) => { BH.sky(p, 200, 520, 81); BH.tower(p, 1430, 690, 0.62); BH.waves(p, 700, 840, 30, 7, 0.4); }));
  sh.type(15, { box: [110, 210, 860, 660], color: (r) => (r === 0 ? 'ink' : 'red') });
}, { transition: 'split' });
F.shot('refrain-4', pre(16, 0.15), (sh) => {
  sh.el({ box: [1000, 160, 860, 740], depth: 0.5 }, (o) => BH.frame(o, [1040, 200, 780, 640], (p) => { BH.nightSky(p, 840, 91); BH.tower(p, 1430, 700, 0.5); BH.waves(p, 700, 840, 26, 8, 0.5); }));
  sh.type(16, { box: [110, 210, 860, 660], color: 'red' });
});
F.shot('refrain-5', pre(17, 0.1), (sh) => {
  sh.el({ box: [1000, 160, 860, 740], depth: 0.5 }, (o) => BH.frame(o, [1040, 200, 780, 640], (p) => { BH.nightSky(p, 840, 66, [1240, 330, 70]); BH.waves(p, 600, 840, 30, 6, 0.55); BH.boat(p, 1450, 760, 1.2); BH.grinder(p, 1380, 742, 0.75); }));
  sh.type(17, { box: [110, 210, 860, 660], scale: [0.62, 1] });
});

// ---------- 间奏 / 尾奏：一图看懂（知识卡，统一版式，停留 ≥ 2.5 秒）----------
F.shot('card', S.sec(6).start, (sh) => {
  sh.el({ box: [240, 170, 1440, 700] }, (o) => BH.card(o, { ep: F.vars.epNo, series: F.vars.series, title: '一封劝谏，两条路', kind: 'steps', src: '据《明史·刘基传》',
    items: [{ b: '安丰被围，小明王求救' }, { b: '刘基：汉吴伺隙，未可动也' }, { b: '太祖不听，亲自去救' }] }));
  sh.push(1.03);
}, { transition: 'paper' });

// ---------- 片尾卡：站队题（选项都印在屏上）+ 下一集 ----------
F.shot('end', S.duration - 3.2, (sh) => {
  sh.el({ box: [240, 180, 1440, 680] }, (o) => BH.endCard(o, { question: '救，还是不救？换了是你，走哪一条？', options: ['救安丰', '守应天'], next: `下一集 · ${F.vars.nextTitle || '下游那个磨桨的人'}` }));
}, { transition: 'cut', subs: false });

F.finish();
