#!/usr/bin/env bash
# 给无声成片配上歌：bash mux.sh 歌曲.mp3 [无声版.mp4] [输出.mp4]
# 先核对时长（应约 234.7 秒，对不上说明下的不是这一版），再把响度归一到 -14 LUFS 配进去；画面直接复制，不重编码。
set -euo pipefail
SONG="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"
VID="${2:-$HERE/out/ep12-dengfenglai-pixel-silent.mp4}"
OUT="${3:-$HERE/out/ep12-dengfenglai-pixel.mp4}"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SONG")
python3 -c "import sys; d=float('$D'); print(f'歌曲时长 {d:.2f}s（这一版 Suno 记录 234.68s）'); sys.exit(0 if abs(d-234.68)<1.0 else 1)" \
  || { echo '✗ 时长对不上：可能下载的是另外三版中的一版（这支 MV 按 id 252e6605 那一版对齐）'; exit 1; }
ffmpeg -v error -y -i "$VID" -i "$SONG" -map 0:v:0 -map 1:a:0 -c:v copy \
  -af loudnorm=I=-14:TP=-1.0:LRA=11 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$OUT"
ls -l "$OUT"
