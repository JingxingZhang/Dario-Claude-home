"""《晚安》3:4 竖版封面（1080×1440）：python3 cover_34.py [输出.png]
原生像素画 270×360，最近邻放大 4 倍；歌名、原唱、钩子用高清花字叠加。复用 mv.py 里的角色和道具。"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.environ.get('PIXMV_SKILL') or os.path.expanduser(
    '~/.claude/skills/synced/1974bc8c-88fb-49fb-9b5a-c4cbb9578337_ce470cf2-cfe7-4b32-a524-0f5c17582033/pixel-mv')
os.environ['PIXMV_PROJECT'] = HERE
os.environ['PIXMV_SKILL'] = SKILL
sys.path.insert(0, os.path.join(SKILL, 'lib')); sys.path.insert(0, HERE)
import mv
from mv import *
import huazi as Z

CW, CH, K4 = 270, 360, 4
img = Image.new('RGB', (CW, CH))
d = ImageDraw.Draw(img)
p = P(False)
t = 0.6

# 夜空 + 星星
fill_grad(img, p['sky0'], p['sky1'], 0, CH, 0, CW)
stars(img, t, 70, w=CW, h=250, seed=4)
# 月亮（戴睡帽，脸红）
moonc(img, 212, 58, 'blush', 4, False)
# 远处楼群 + 屋顶
skyline(img, False, 304, seed=61, w=CW, hmin=20, hmax=90, lit=0.3)
R(d, 0, 300, CW, CH - 300, lerpc(p['ink'], p['wall'], 0.6))
R(d, 0, 300, CW, 2, lerpc(p['wall2'], (255, 255, 255), 0.2))
# 关系进度条：朋友 ——●—— 恋人，卡在暧昧区
rel_bar(img, CW // 2, 170, 0.5, False, 120)
# 我和她拉着系着心的绳子
lx, yx = 64, 206
lead(img, lx, 300, 'wave', 'happy', 1, 3)
you(img, yx, 300, 'phone', 'smile', -1, 3)
hy = 251
d.line([(lx + 22, hy), (135, hy + 3), (yx - 22, hy)], fill=(240, 220, 180), width=2)
heart(img, 135, hy + 1, 3, (255, 100, 150))
for sx, sy in ((112, 228), (160, 236), (135, 214)):
    sparkle(img, sx, sy, 2)

big = img.resize((CW * K4, CH * K4), Image.NEAREST)
# 歌名、原唱、标签
title = Z.Line(-1, 99, '晚安', pal='yel', size=300, cx=400, cy=270, angle=-4, deco=('star', 'heart'), stagger=0.0, pop=1.0)
title.draw(big, 5.0)
Z.pill(big, 400, 470, '原唱 · 颜人中', 60)
Z.pill(big, 400, 560, '像素 MV', 44, bg=(255, 110, 170), edge=(255, 255, 255))
# 钩子
hook = Z.Line(-1, 99, '朋友以上 恋人未满', pal='pink', kw=['恋人未满'], kwpal='yel', size=96, cx=540, cy=1282, angle=-2, stagger=0.0, pop=1.0)
hook.draw(big, 5.0)
sig = Z.signature('@张景行')
big.paste(sig, (540 - sig.width // 2, CH * K4 - sig.height - 10), sig)

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'cover', '封面-3x4.png')
big.save(out)
print('✓', out, big.size)
