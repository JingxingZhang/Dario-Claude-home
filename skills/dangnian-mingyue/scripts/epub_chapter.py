#!/usr/bin/env python3
"""读上传的 epub：列目录、取某一章正文（含“参考消息”等侧栏、图片位置），并给出书名、作者、部名和下一章标题。
  python3 -I epub_chapter.py <book.epub>                 列出全部章节（序号、标题、字数）
  python3 -I epub_chapter.py <book.epub> <序号|标题关键词> [--out 文件]   取一章正文，末尾附元数据 JSON
不带 epub 路径时，自动在 /root/.claude/uploads 和当前目录下找 .epub。"""
import sys, os, re, html, json, zipfile, glob, posixpath

def find_epub():
    c = glob.glob('/root/.claude/uploads/**/*.epub', recursive=True) + glob.glob('**/*.epub', recursive=True)
    return sorted(c, key=os.path.getmtime)[-1] if c else None

args = [x for x in sys.argv[1:] if not x.startswith('--')]
out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
if out in args: args.remove(out)
path = args[0] if args and args[0].endswith('.epub') else find_epub()
if not path: sys.exit('没找到 epub')
want = args[1] if len(args) > 1 and args[0].endswith('.epub') else (args[0] if args and not args[0].endswith('.epub') else None)
z = zipfile.ZipFile(path)
opf_path = re.search(r'full-path="([^"]+)"', z.read('META-INF/container.xml').decode()).group(1)
opf = z.read(opf_path).decode('utf-8'); base = posixpath.dirname(opf_path)
meta = {k: (re.search(fr'<dc:{k}[^>]*>(.*?)</dc:{k}>', opf, re.S) or [None, ''])[1].strip() for k in ('title', 'creator', 'publisher')}
manifest = {m.group(1): m.group(2) for m in re.finditer(r'<item[^>]*id="([^"]+)"[^>]*href="([^"]+)"', opf)}
manifest.update({m.group(2): m.group(1) for m in re.finditer(r'<item[^>]*href="([^"]+)"[^>]*id="([^"]+)"', opf)})
spine = [manifest[i] for i in re.findall(r'<itemref[^>]*idref="([^"]+)"', opf) if i in manifest]

def text_of(href):
    s = z.read(posixpath.join(base, href)).decode('utf-8', 'ignore')
    s = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', r'[图 \1]', s)
    s = re.sub(r'</p>|<br[^>]*>|</h\d>|</div>', '\n', s); s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\n\s*\n+', '\n', html.unescape(s)).strip()

chapters = []
for href in spine:
    t = text_of(href)
    m = re.match(r'\s*(第[一二三四五六七八九十百零〇\d]+章|附录[一二三四五六七八九十]*)\s*([^\n]*)', t)
    if m:
        parts = t.split('\n')
        title = m.group(2).strip() or (parts[1].strip() if len(parts) > 1 else '')
        chapters.append({'no': m.group(1), 'title': title, 'href': href, 'chars': len(re.sub(r'\s', '', t))})
if want is None:
    print(f"《{meta['title']}》 {meta['creator']} · {meta['publisher']}  （{path}）")
    for i, c in enumerate(chapters, 1): print(f"{i:>3}  {c['no']}  {c['title']}  {c['chars']} 字")
    sys.exit()
idx = None
if want.isdigit(): idx = int(want) - 1
else:
    for i, c in enumerate(chapters):
        if want in c['no'] + c['title']: idx = i; break
if idx is None or not (0 <= idx < len(chapters)): sys.exit(f'没找到章节：{want}')
c = chapters[idx]; nxt = chapters[idx + 1] if idx + 1 < len(chapters) else None
body = text_of(c['href'])
part = re.search(r'第[壹贰叁肆伍陆柒捌玖拾]+部', meta['title'])
info = {'book': meta['title'], 'author': meta['creator'], 'part': part.group(0) if part else '', 'chapter_no': c['no'], 'chapter_title': c['title'],
        'next_no': nxt['no'] if nxt else '', 'next_title': nxt['title'] if nxt else '', 'chars': c['chars'], 'index': idx + 1}
res = body + '\n\n---\n' + json.dumps(info, ensure_ascii=False, indent=1)
if out: open(out, 'w', encoding='utf-8').write(res); print(json.dumps(info, ensure_ascii=False))
else: print(res)
