#!/usr/bin/env bash
# 把一个已有的 MP4 压到体积上限以内（默认 100 MB；1 MB = 1,000,000 字节）。render.js 出的成片已经在上限内，这个脚本用于别处来的视频。
#   bash compress.sh <输入.mp4> [上限MB=100] [输出.mp4=<输入>-<上限>MB.mp4]
set -euo pipefail
IN="$1"; CAP="${2:-100}"; OUT="${3:-${IN%.*}-${CAP}MB.mp4}"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
SIZE=$(stat -c %s "$IN")
if python3 -c "import sys; sys.exit(0 if $SIZE <= $CAP*1e6 else 1)"; then echo "已经在上限内：$(python3 -c "print(round($SIZE/1e6,1))") MB"; exit 0; fi
VK=$(python3 -c "print(int(($CAP*1e6*0.94*8/$D - 192000)/1000))")
[ "$VK" -gt 300 ] || { echo "上限太小：视频码率只剩 ${VK} kbps"; exit 1; }
LOG=$(mktemp -d)/x264
ffmpeg -v error -y -i "$IN" -c:v libx264 -preset slow -b:v ${VK}k -pass 1 -passlogfile "$LOG" -an -f null /dev/null
ffmpeg -v error -y -i "$IN" -c:v libx264 -preset slow -b:v ${VK}k -maxrate $((VK*3/2))k -bufsize $((VK*3))k -pass 2 -passlogfile "$LOG" \
  -pix_fmt yuv420p -profile:v high -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "压缩完成：$OUT  $(python3 -c "import os; print(round(os.path.getsize('$OUT')/1e6,1))") MB（上限 $CAP MB，视频 ${VK} kbps）"
