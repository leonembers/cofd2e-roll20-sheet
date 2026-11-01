"""Measure per-splat frame art border width (fraction of image width) from the mid tiles actually referenced in dist/sheet.css."""
import re,os,subprocess,json
from PIL import Image
import numpy as np
css=open('dist/sheet.css').read()
urls=sorted(set(re.findall(r'url\("(https://cdn[^"]*-?mid[^"]*\.(?:jpg|png))"\)',css)))
out={}
for u in urls:
    f='/tmp/art/'+re.sub(r'[^a-z0-9.]','_',u.split('cofd-sheet-art@')[1])
    if not os.path.exists(f): subprocess.run(['curl','-s','-o',f,u])
    try: im=np.asarray(Image.open(f).convert('L'),dtype=float)
    except Exception as e: print('ERR',u,e); continue
    H,W=im.shape; band=im[H//4:3*H//4]
    sd=band.std(axis=0)+np.abs(np.diff(band,axis=1,prepend=band[:,:1])).mean(axis=0)
    mid=np.median(sd[int(W*.3):int(W*.7)]); thr=mid*2.2+4
    l=0
    while l<W*.2 and sd[l:l+3].max()>thr: l+=1
    # extend: last index in left 15% exceeding thr
    L=max([i for i in range(int(W*.15)) if sd[i]>thr] or [0])
    R=max([i for i in range(int(W*.15)) if sd[W-1-i]>thr] or [0])
    out[u.split('@')[1]]=(round(L/W,4),round(R/W,4),W)
    print(u.split('@')[1],out[u.split('@')[1]],flush=True)
json.dump(out,open('/tmp/framew.json','w'),indent=1)
