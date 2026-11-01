#!/usr/bin/env bash
# 当年明月 · 环境准备（每个新会话跑一次；已装好的步骤会自动跳过）
# 需要：Node ≥ 18、ffmpeg/ffprobe、Chromium（Playwright）；装：fonttools、pillow、字体（思源宋体、霞鹜文楷、思源黑体）
# 首次约 4 分钟（主要是下载、裁剪字体）。用法：bash scripts/setup.sh
set -euo pipefail
CA=/root/.ccr/ca-bundle.crt
if [ -f "$CA" ]; then export SSL_CERT_FILE=$CA REQUESTS_CA_BUNDLE=$CA NODE_EXTRA_CA_CERTS=$CA; fi   # 云端代理的证书（不要关闭校验）
SK="$(cd "$(dirname "$0")/.." && pwd)"
say() { printf '\n== %s\n' "$*"; }

say "Node / ffmpeg"
node -e 'const v=+process.versions.node.split(".")[0]; if (v<18) { console.error("Node 版本太低："+process.version); process.exit(1) } console.log("✓ Node "+process.version)'
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && echo "✓ $(ffmpeg -version | head -1 | cut -d' ' -f1-3)" || { echo "✗ 缺 ffmpeg/ffprobe（apt install ffmpeg 或 brew install ffmpeg）"; exit 1; }

say "Chromium（Playwright，用来逐帧截图）"
if ! node -e "require('playwright')" 2>/dev/null && ! node -e "require('playwright-core')" 2>/dev/null; then
  # 云端容器已预装 Playwright 和 Chromium，不会走到这里；本地电脑第一次用时装到 ~/ming-node
  mkdir -p "$HOME/ming-node" && npm i -s --prefix "$HOME/ming-node" playwright >/dev/null && (cd "$HOME/ming-node" && npx -y playwright install chromium)
fi
node -e "
const { launch } = require('$SK/scripts/lib/film.js');
launch().then(async (b) => { console.log('✓ Chromium ' + b.version()); await b.close(); }).catch((e) => { console.error('✗ Chromium 启动失败：' + e.message + '（可设 MING_CHROME=浏览器路径）'); process.exit(1); });"

say "系统 Python 的小工具（读 epub、查字形、拼关键帧、裁字体）"
python3 -c "import fontTools, PIL" 2>/dev/null || pip install -q fonttools pillow 2>/dev/null || pip install -q --break-system-packages fonttools pillow
echo "✓ fonttools、pillow"

say "字体（思源宋体、霞鹜文楷、思源黑体：官方源下载 + GB2312 子集，缓存在 ~/.cache/ming-fonts；首次约 3 分钟）"
python3 "$SK/scripts/fonts.py" "${MING_FONTS:-$HOME/.cache/ming-fonts}"

say "完成"
echo "SK=$SK"
