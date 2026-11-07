#!/usr/bin/env python3
"""用上传后的资源地址填好下载页模板。
用法：python build_page.py <输出.html> <page.json>
page.json：
{
  "title": "晴天", "h1_accent": "综艺花字版", "meta": "周杰伦《晴天》动态排版歌词 MV · 1080p 原画",
  "cover_url": "/_blob/…", "cover_alt": "封面：…",
  "versions": [
    {"id": "v1", "name": "综艺花字版 · 专辑原版音频", "badge": "推荐",
     "spec": "1920×1080 · 30fps · 4:32 · AAC 320 kbps · 147 MB",
     "filename": "晴天_综艺花字版_1080p.mp4", "total": 147004363,
     "parts": ["/_blob/…", "/_blob/…"]}
  ]
}
新版本放在 versions 最前面；旧版本保留在后面，同一个页面链接不变。"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
out, cfg = sys.argv[1], json.load(open(sys.argv[2]))
s = open(os.path.join(HERE, '..', 'assets', 'download_page.html'), encoding='utf-8').read()
for k in ('title', 'h1_accent', 'meta', 'cover_url', 'cover_alt'):
    s = s.replace('{{' + k.upper() + '}}', cfg.get(k, ''))
s = s.replace('{{VERSIONS_JSON}}', json.dumps(cfg['versions'], ensure_ascii=False, indent=2))
open(out, 'w', encoding='utf-8').write(s)
print('✓', out)
