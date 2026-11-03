"""导关键帧并拼图：python3 still.py 输出.png 秒,秒,… [列数]"""
import sys
from PIL import Image
import mv
ts=[float(x) for x in sys.argv[2].split(',')]
cols=int(sys.argv[3]) if len(sys.argv)>3 else 4
s=2
tiles=[]
for t in ts:
    im=mv.frame(t).resize((mv.W*s,mv.H*s),Image.NEAREST)
    tiles.append((t,im))
rows=(len(tiles)+cols-1)//cols
sheet=Image.new('RGB',(cols*mv.W*s+(cols-1)*4,rows*(mv.H*s+4)),(255,255,255))
from pixlib import draw_text
for i,(t,im) in enumerate(tiles):
    draw_text(im,2,2,f'{t:.1f}',(255,0,255))
    sheet.paste(im,((i%cols)*(mv.W*s+4),(i//cols)*(mv.H*s+4)))
sheet.save(sys.argv[1])
