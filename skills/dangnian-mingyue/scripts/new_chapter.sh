#!/usr/bin/env bash
# 新建一集 MV 工程：版画套色引擎、场景库、字体、封面模板，外加一首示例歌和示例分镜（可以直接导静帧看效果）。
#   bash new_chapter.sh <工作目录>/<章节目录名>
# 示例歌是《江水在涨》前 75 秒的结构（逐字时间、节拍）。跑完 song_sync.py 后，index.html 里的歌曲数据换成本集的歌；
# assets/chapter.js 照示例的结构重写成本集分镜。
set -euo pipefail
SK="$(cd "$(dirname "$0")/.." && pwd)"; D="${1:?用法：bash new_chapter.sh <章节目录>}"
[ -e "$D/index.html" ] && { echo "已存在：$D"; exit 1; }
FONTS="${MING_FONTS:-$HOME/.cache/ming-fonts}"
[ -f "$FONTS/NotoSerifSC-900.woff" ] || { echo "字体还没准备好：先跑 bash $SK/scripts/setup.sh"; exit 1; }
T="$SK/assets/template"
mkdir -p "$D/assets/fonts" "$D/vendor" "$D/tools" "$D/cover" "$D/out"
cp "$T/index.html" "$D/index.html"
cp "$T/fonts.css" "$T/shapes.js" "$T/bh-lib.js" "$D/assets/"
cp "$T/example/chapter.example.js" "$D/assets/chapter.js"
cp "$T/example/lyrics.example.txt" "$D/tools/lyrics.example.txt"
cp "$T/cover.html" "$D/cover/cover.html"
cp "$FONTS"/*.woff "$FONTS/OFL.txt" "$D/assets/fonts/"
cp "$SK/assets/runtime/mr.js" "$SK/assets/runtime/banhua.js" "$SK/assets/vendor/gsap.min.js" "$SK/assets/vendor/GSAP-LICENSE.txt" "$D/vendor/"
python3 -I - "$D/index.html" "$T/example/song.example.json" <<'EOF'
import sys, re, json
p, ex = sys.argv[1], sys.argv[2]
h = open(p, encoding='utf-8').read()
blob = json.dumps(json.load(open(ex, encoding='utf-8')), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
h, n = re.subn(r'<script type="application/json" id="song">.*?</script>', lambda m: f'<script type="application/json" id="song">{blob}</script>', h, flags=re.S)
assert n == 1
open(p, 'w', encoding='utf-8').write(h)
EOF
echo "新工程（版画套色 · 16:9 · 30fps，内含示例歌与示例分镜）：$D"
echo "下一步：A 段写歌词、生成歌；B 段拿到 mp3 后跑 song_sync.py，再重写 assets/chapter.js"
