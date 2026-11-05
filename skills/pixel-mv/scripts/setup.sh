#!/usr/bin/env bash
# 像素 MV 环境准备：ffmpeg、Python 依赖、三套字体。已装好的会跳过。用法：bash setup.sh
set -euo pipefail
CA=/root/.ccr/ca-bundle.crt; [ -f "$CA" ] && export SSL_CERT_FILE=$CA REQUESTS_CA_BUNDLE=$CA
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && echo "✓ $(ffmpeg -version | head -1 | cut -d' ' -f1-3)" || { echo "✗ 缺 ffmpeg"; exit 1; }
python3 -c "import PIL, numpy, fontTools, brotli" 2>/dev/null || pip install -q pillow numpy fonttools brotli 2>/dev/null || pip install -q --break-system-packages pillow numpy fonttools brotli
python3 -c "import PIL, numpy, fontTools, brotli; print('✓ Pillow', PIL.__version__, '· numpy', numpy.__version__)"
python3 "$HERE/fonts.py"
echo "✓ 完成  SKILL=$(dirname "$HERE")"
