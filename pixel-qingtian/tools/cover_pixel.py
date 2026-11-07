import os, sys
SK, P = sys.argv[1], os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.join(SK, 'scripts'))
from _load import load
mv = load(P)
import huazi as Z
from PIL import Image
pj, t = mv.song.p, mv.COVER_T
cv = Image.new('RGB', (180, 240)); mv.COVER_3X4(cv, t)
big = cv.resize((1080, 1440), Image.NEAREST)
ts = dict(pal='pink', size=250, angle=-3, deco=('star', 'note')); ts.update(getattr(mv, 'TITLE_STYLE', None) or {})
ts['size'] = min(ts.get('size', 250), int(900 / max(1, len(pj['title'])) / 1.05))
Z.Line(-2, 99, pj['title'], cx=540, cy=200, stagger=0.0, pop=1.08,
       **{k: v for k, v in ts.items() if k in ('pal', 'size', 'angle', 'deco', 'kw', 'kwpal')}).draw(big, 3.0, 0.5)
if pj.get('artist'):
    Z.pill(big, 540, 1240, '原唱 · ' + pj['artist'], 56)
Z.pill(big, 540, 1336, pj.get('tag') or '像素 MV', 40, bg=(255, 110, 170), edge=(255, 255, 255))
if pj.get('signature'):
    sg = Z.signature(pj['signature']); big.paste(sg, (540 - sg.width // 2, 1440 - sg.height - 8), sg)
os.makedirs(os.path.join(P, 'cover'), exist_ok=True)
big.save(os.path.join(P, 'cover', '封面.png'))
if '--also-16x9' in sys.argv:
    mv.frame(t).save(os.path.join(P, 'cover', '封面_16x9.png'))
print('ok')
