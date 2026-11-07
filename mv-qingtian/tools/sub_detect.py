import cv2, numpy as np, json, sys
cap=cv2.VideoCapture('src/in.mp4'); fps=cap.get(5); n=int(cap.get(7)); print(fps,n)
# find subtitle band from one frame
rows=[]; i=0; sigs=[]
while True:
    ok,f=cap.read()
    if not ok: break
    if i%3==0:
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        band=g[700:800]
        b=(band>128).astype(np.uint8)
        sigs.append((i/fps,b))
    i+=1
# rows with any text over whole video
acc=np.zeros(100)
for t,b in sigs: acc+=b.sum(1)
print('rows active', np.nonzero(acc)[0][[0,-1]] if acc.any() else None)
segs=[];cur=None
for t,b in sigs:
    s=b.sum()
    if s<20:
        if cur: segs.append(cur); cur=None
        continue
    if cur is None or np.abs(b.astype(int)-cur['b'].astype(int)).sum()>0.15*max(s,cur['b'].sum()):
        if cur: segs.append(cur)
        cur={'t0':t,'t1':t,'b':b}
    else: cur['t1']=t
if cur: segs.append(cur)
print(len(segs))
out=[]
for k,s in enumerate(segs):
    out.append({'i':k,'t0':round(s['t0'],2),'t1':round(s['t1']+0.1,2)})
    cv2.imwrite(f'subs/{k:03d}.png',255*s['b'])
json.dump(out,open('subs.json','w'),indent=0)
