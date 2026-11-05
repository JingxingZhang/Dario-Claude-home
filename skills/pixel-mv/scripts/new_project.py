#!/usr/bin/env python3
"""新建一首歌的像素 MV 项目。
  python3 new_project.py 项目目录 --audio 歌曲文件 --title 歌名 --artist 原唱 [--signature @张景行]
生成：project.json、mv.py（镜头骨架）、tools/、out/、cover/、故事.md、歌词精读.md 和 分镜说明.md（模板）。
时长自动读取；片头标题卡默认 0–9.6 秒，片尾卡默认最后 10 秒（可在 project.json 改）。"""
import argparse, json, os, shutil, subprocess

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('dir'); ap.add_argument('--audio', required=True)
ap.add_argument('--title', required=True); ap.add_argument('--artist', default='')
ap.add_argument('--signature', default='@张景行'); ap.add_argument('--tag', default='像素 MV')
A = ap.parse_args()
d = os.path.abspath(A.dir)
for sub in ('tools', 'out', 'cover', 'stickers'):
    os.makedirs(os.path.join(d, sub), exist_ok=True)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', A.audio], capture_output=True, text=True, check=True).stdout.strip())
pj = dict(title=A.title, artist=A.artist, signature=A.signature, tag=A.tag, duration=round(dur, 3),
          title_end=9.6, end_start=round(dur - 10, 1), audio=os.path.abspath(A.audio))
json.dump(pj, open(os.path.join(d, 'project.json'), 'w'), ensure_ascii=False, indent=2)
for src, dst in (('mv_template.py', 'mv.py'), ('story_template.md', '故事.md'), ('storyboard_template.md', '分镜说明.md'), ('lyric_analysis_template.md', '歌词精读.md')):
    if not os.path.exists(os.path.join(d, dst)):
        shutil.copy(os.path.join(SKILL, 'templates', src), os.path.join(d, dst))
open(os.path.join(d, '.gitignore'), 'w').write('out/*.mp4\ntools/*.raw\n__pycache__/\n')
print(f'✓ 项目 {d}\n  时长 {dur:.2f}s  片头卡到 9.6s  片尾卡从 {dur - 10:.1f}s\n  下一步：查创作背景 → tools/lyrics.txt → 歌词精读.md → tools/audio.json → 故事.md → 分镜与角色 → mv.py → 封面')
