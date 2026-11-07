#!/bin/bash
# 环境准备：Python 依赖、skia 需要的系统库、开源字体（OFL）→ ~/.cache/huazi-mv/fonts
set -e
python3 -c "import skia, librosa, cv2" 2>/dev/null || pip install -q skia-python librosa opencv-python-headless numpy
python3 -c "import skia" 2>/dev/null || { (apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1 || (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1)); }
python3 -c "import skia, librosa, cv2; print('✓ skia', skia.__version__, '· librosa', librosa.__version__)"
which ffmpeg >/dev/null && echo "✓ $(ffmpeg -version | head -1 | cut -c1-40)" || echo "✗ 需要 ffmpeg"
FD="${HZMV_FONTS:-$HOME/.cache/huazi-mv/fonts}"; mkdir -p "$FD"
B=https://raw.githubusercontent.com/google/fonts/main/ofl
for p in zcoolkuaile/ZCOOLKuaiLe-Regular.ttf "notosanssc/NotoSansSC%5Bwght%5D.ttf" "notoserifsc/NotoSerifSC%5Bwght%5D.ttf" \
         "cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf" "cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf"; do
  n=$(basename "$p" | sed 's/%5B/[/;s/%5D/]/')
  if [ ! -s "$FD/$n" ] || [ "$(stat -c %s "$FD/$n")" -lt 10000 ]; then curl -sSL -o "$FD/$n" "$B/$p"; fi
  sz=$(stat -c %s "$FD/$n"); [ "$sz" -gt 10000 ] && echo "✓ $n" || echo "✗ $n 下载失败（$sz 字节）"
done
echo "字体目录：$FD"
