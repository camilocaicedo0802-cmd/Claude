import numpy as np, cv2, sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
a=np.array(Image.open(src).convert('RGB')); H,W,_=a.shape
cx,cy=545,473  # centro del reloj en la imagen original
yy,xx=np.mgrid[0:H,0:W]; r=np.hypot(xx-cx,yy-cy)
ai=a.astype(int); light=ai.mean(2); blueish=(ai[...,2]-ai[...,0])>35
mask=((r<86)&(light<212)&~blueish)|((r<30)&(blueish|(light<212)))
mask=cv2.dilate(mask.astype(np.uint8)*255,np.ones((5,5),np.uint8),iterations=2)
sin=cv2.inpaint(a[...,::-1].copy(),mask,7,cv2.INPAINT_TELEA)[...,::-1]
white=((a>=236).all(2)).astype(np.uint8); ff=np.zeros((H+2,W+2),np.uint8); filled=white.copy()
for p in [(0,0),(W-1,0),(0,H-1),(W-1,H-1)]: cv2.floodFill(filled,ff,p,2)
bg=(filled==2).astype(np.uint8)
# huecos dentro de las anillas (zona superior)
w2=((a>=232).all(2)).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(w2,8)
for i in range(1,n):
    x,y,w,h,area=st[i]
    if y<170 and y+h<170 and area>300: bg[lab==i]=1
alpha=np.clip((1-cv2.GaussianBlur(bg.astype(np.float32),(5,5),0))*1.15,0,1)
out=np.dstack([sin,(alpha*255).astype(np.uint8)])
ys,xs=np.nonzero(alpha>0.02); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
Image.fromarray(out[y0:y1,x0:x1]).save(dst)
print('tam',x1-x0,y1-y0,'centro reloj rel',round((cx-x0)/(x1-x0),4),round((cy-y0)/(y1-y0),4))
