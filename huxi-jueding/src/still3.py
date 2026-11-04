"""关键帧拼图：python3 still3.py 输出.png 秒,秒,… [列数]"""
import sys
from PIL import Image, ImageDraw
import mv3
ts=[float(x) for x in sys.argv[2].split(',')]
cols=int(sys.argv[3]) if len(sys.argv)>3 else 3
tw,th=640,360
rows=(len(ts)+cols-1)//cols
sheet=Image.new('RGB',(cols*(tw+4),rows*(th+4)),'white')
for i,t in enumerate(ts):
    im=mv3.frame(t).resize((tw,th),Image.BILINEAR)
    ImageDraw.Draw(im).text((4,4),f'{t:.1f}',fill=(255,0,255))
    sheet.paste(im,((i%cols)*(tw+4),(i//cols)*(th+4)))
sheet.save(sys.argv[1])
