import subprocess, numpy as np, json, sys
SH=[("IMG_6016",1.0,2.667,1,1),("IMG_6017",0.6,3.233,1,1),("IMG_6019",4.4,2.1,0,1),("IMG_6024",5.2,2.667,1,0),
    ("IMG_6018",3.0,2.667,1,1),("IMG_6019",6.5,1.333,0,1),("IMG_6022_rev",0.0,1.75,1,1),("IMG_6023",4.0,3.333,1,0)]
T_RED=np.array([220,54,60])/255; T_WHITE=np.array([208,208,204])/255; CAP=226/255
FAB_T={'IMG_6023':17,'IMG_6024':12}  # el delantero necesita algo más de tela visible
N=33; W=np.array([0.2126,0.7152,0.0722])
def frames(n,s,d,k=4):
    out=[]
    for i in range(k):
        t=s+d*(i+0.5)/k
        raw=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',f'public/tomas/{n}.mp4','-frames:v','1','-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
        out.append(np.frombuffer(raw,np.uint8).reshape(480,270,3).astype(float)/255)
    return np.array(out)
def stats(f):
    a=f.reshape(-1,3); L=a@W; mx=a.max(1); mn=a.min(1); sat=(mx-mn)/np.maximum(mx,1e-3)
    fab=np.median(a[L<np.percentile(L,40)],0)
    m=(L>np.percentile(L,40))&(L<np.percentile(L,75))&(sat<0.55); neu=np.median(a[m],0)
    redm=(a[:,0]>1.6*a[:,1]+0.06)&(a[:,0]>0.15); red=np.percentile(a[redm],75,axis=0) if redm.sum()>50 else None
    wm=(L>np.percentile(L,99.5))&(np.abs(a[:,0]-a[:,2])<0.12); white=np.median(a[wm],0) if wm.sum()>20 else None
    return fab,neu,red,white
def pchip(xs,ys,x):
    xs=np.array(xs,float);ys=np.array(ys,float);h=np.diff(xs);d=np.diff(ys)/h;m=np.zeros_like(ys)
    for k in range(1,len(xs)-1):
        if d[k-1]*d[k]>0: w1=2*h[k]+h[k-1];w2=h[k]+2*h[k-1]; m[k]=(w1+w2)/(w1/d[k-1]+w2/d[k])
    m[0]=d[0];m[-1]=d[-1]
    i=np.clip(np.searchsorted(xs,x,side='right')-1,0,len(h)-1); t=(x-xs[i])/h[i]
    return (2*t**3-3*t**2+1)*ys[i]+(t**3-2*t**2+t)*h[i]*m[i]+(-2*t**3+3*t**2)*ys[i+1]+(t**3-t**2)*h[i]*m[i+1]
res=[];prev=[];rep=[]
fmt=lambda v:None if v is None else tuple(int(x) for x in (np.atleast_1d(v)*255).round())
for n,s,d,ur,uw in SH:
    f=frames(n,s,d); fab,neu,red,white=stats(f)
    tf=FAB_T.get(n,11)/255
    # gris objetivo de los pliegues: su luminancia escalada como el resto de la imagen (sin tinte)
    hiL=(white@W) if (uw and white is not None) else (red[0] if red is not None else (f.reshape(-1,3)@W).max())
    hiT=(T_WHITE@W) if (uw and white is not None) else T_RED[0]
    tn=max(tf+0.015,(neu@W)*hiT/hiL)
    luts=[]
    for c in range(3):
        pts=[(fab[c],tf),(neu[c],tn)]
        if ur and red is not None: pts.append((red[c],T_RED[c]))
        if uw and white is not None: pts.append((white[c],T_WHITE[c]))
        clean=[(0.0,0.0)]
        for x,y in sorted(pts):
            if x>clean[-1][0]+0.003 and y>clean[-1][1]+0.003: clean.append((x,y))
        clean.append((1.0,max(CAP,clean[-1][1]+0.01)))
        xs,ys=zip(*clean); luts.append(np.clip(pchip(xs,ys,np.linspace(0,1,N)),0,1))
    g=np.linspace(0,1,N); o=np.stack([np.interp(f[...,c],g,luts[c]) for c in range(3)],-1)
    fa,na,ra,wa=stats(o)
    line=f"{n} {s:5.2f} tela {fmt(fab)}->{fmt(fa)} pliegues {fmt(neu)}->{fmt(na)} rojo {fmt(red)}->{fmt(ra)} blanco {fmt(white)}->{fmt(wa)} luma {f.mean()*255:.1f}->{o.mean()*255:.1f}"
    print(line); rep.append(line)
    res.append([[round(float(v),4) for v in l] for l in luts]); prev.append(np.concatenate([f[1],o[1]],1))
json.dump(res,open(sys.argv[1],'w'))
img=(np.concatenate([np.concatenate(prev[:4],1),np.concatenate(prev[4:],1)],0)*255).astype(np.uint8)
subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{img.shape[1]}x{img.shape[0]}','-i','-',sys.argv[2]],input=img.tobytes())
