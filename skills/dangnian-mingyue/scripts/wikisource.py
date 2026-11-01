#!/usr/bin/env python3
"""查正史原文（维基文库）。自带限速与重试；卷名在维基文库上不统一时先用搜索。
  python3 -I wikisource.py search '"五姓漢人" 元史'      全文搜索：用繁体、原文短语加引号、带上书名
  python3 -I wikisource.py page "明史/卷1" [关键词 …]     取一页原文；给了关键词就只打印命中上下文"""
import sys, time, json, re, ssl, urllib.parse, urllib.request
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt') if __import__('os').path.exists('/root/.ccr/ca-bundle.crt') else None
def get(params):
    url = 'https://zh.wikisource.org/w/api.php?' + urllib.parse.urlencode({**params, 'format': 'json'})
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'dangnian-mingyue-factcheck/1.0'})
            return json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())
        except Exception as e:
            if '429' in str(e) or 'timed out' in str(e): time.sleep(4 * (i + 1)); continue
            raise
    raise SystemExit('维基文库请求失败（多次 429）')
cmd = sys.argv[1]
if cmd == 'search':
    r = get({'action': 'query', 'list': 'search', 'srsearch': sys.argv[2], 'srlimit': 8})
    for h in r['query']['search']: print(h['title'], '|', re.sub(r'<[^>]+>', '', h['snippet'])[:150])
elif cmd == 'page':
    r = get({'action': 'parse', 'page': sys.argv[2], 'prop': 'wikitext', 'redirects': 1})
    if 'error' in r: raise SystemExit(r['error'].get('info'))
    t = r['parse']['wikitext']['*']
    for _ in range(3):  # {{YL|至正四年}} 这类模板保留最后一个参数（正文），其余模板去掉
        t = re.sub(r'\{\{[^{}|]*\|([^{}]*)\}\}', lambda m: m.group(1).split('|')[-1], t)
    t = re.sub(r'\{\{[^{}]*\}\}|<ref[^>]*>.*?</ref>|<ref[^>]*/>|\[\[[^\]|]*\||\]\]|\[\[', '', t)
    keys = sys.argv[3:]
    if not keys: print(t[:6000])
    for k in keys:
        for m in re.finditer(re.escape(k), t): print(f'…{t[max(0, m.start() - 120):m.end() + 160]}…\n')
