# 高分辨率字幕切分（原脚本 320 宽对细字幕检测失败）
import subprocess, json, sys, numpy as np
from PIL import Image, ImageDraw
V=sys.argv[1]; out='tools/ocr'
W,H=960,540; y0,y1=448,490  # 字幕带 905-970 / 1080 → 452-485 / 540
fps=10
raw=subprocess.run(['ffmpeg','-v','error','-i',V,'-vf',f'fps={fps},scale={W}:{H},crop={W}:{y1-y0}:0:{y0},format=rgb24','-f','rawvideo','-'],capture_output=True,check=True).stdout
fr=np.frombuffer(raw,np.uint8).reshape(-1,y1-y0,W,3)
m=fr.astype(int).min(-1)>170
cnt=m.reshape(len(m),-1).sum(1)
thr=60
segs=[];cur=None
for i,c in enumerate(cnt):
    on=c>thr
    if on and cur is None: cur=[i,i]
    elif on:
        d=(m[i]^m[i-1]).sum()
        if d>0.5*max(m[i].sum(),m[i-1].sum()): segs.append(cur);cur=[i,i]
        else: cur[1]=i
    elif cur is not None: segs.append(cur);cur=None
if cur: segs.append(cur)
segs=[s for s in segs if s[1]-s[0]>=4]
times=[[round(s[0]/fps,2),round((s[1]+1)/fps,2)] for s in segs]
json.dump(times,open(f'{out}/segs.json','w'))
tiles=[]
for s,(a,b) in zip(segs,times):
    k=(s[0]+s[1])//2
    im=Image.fromarray(fr[k][:,180:780]).resize((1200,(y1-y0)*2))
    d=ImageDraw.Draw(im); d.text((4,2),f'{a:.1f}-{b:.1f}',fill=(255,0,255))
    tiles.append(im)
per=20
for k in range(0,len(tiles),per):
    sub=tiles[k:k+per]; tw,th=sub[0].size
    sh=Image.new('RGB',(tw,th*len(sub)))
    for i,im in enumerate(sub): sh.paste(im,(0,i*th))
    sh.save(f'{out}/lines_{k//per+1}.png')
print(len(times),'lines'); print(times)
