#!/usr/bin/env python3
"""渲染指定秒数的静帧并拼成对照图（每行 3 张，左下角标秒数）。
用法：python contact_sheet.py <项目目录> <输出.jpg> 秒,秒,秒,…"""
import os, subprocess, sys, glob, shutil
import cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
P, out, ts = os.path.abspath(sys.argv[1]), sys.argv[2], [x for x in sys.argv[3].split(',') if x.strip()]
tmp = os.path.join(P, 'render', 'prev_tmp'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
subprocess.run([sys.executable, os.path.join(HERE, 'engine.py'), P, 'preview', tmp, *ts], check=True,
               stderr=subprocess.DEVNULL)
ims = []
for f in sorted(glob.glob(tmp + '/f_*.png')):
    im = cv2.resize(cv2.imread(f), (640, 360), interpolation=cv2.INTER_AREA)
    cv2.putText(im, os.path.basename(f)[2:-4], (8, 352), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1); ims.append(im)
while len(ims) % 3: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(out, np.vstack([np.hstack(ims[i:i + 3]) for i in range(0, len(ims), 3)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
print('✓', out, f'（单帧原图在 {tmp}）')
