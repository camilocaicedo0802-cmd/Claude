# Mide el desplazamiento global (dx, dy) de la imagen entre fotogramas con correlación de fase.
# dx > 0: el contenido se mueve hacia la DERECHA en pantalla; dx < 0: hacia la IZQUIERDA.
import subprocess, numpy as np, sys
W,H=180,320
def load(p,ss=None,t=None,fps=15,reverse=False):
    cmd=['ffmpeg','-v','error']+(['-ss',str(ss)] if ss is not None else [])+(['-t',str(t)] if t else [])+['-i',p,'-vf',f'fps={fps},scale={W}:{H},format=gray','-f','rawvideo','-']
    f=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.uint8).reshape(-1,H,W).astype(float)
    return f[::-1] if reverse else f
win=np.outer(np.hanning(H),np.hanning(W))
def shift(a,b):
    A=np.fft.fft2((a-a.mean())*win); B=np.fft.fft2((b-b.mean())*win)
    R=A*np.conj(B); R/=np.abs(R)+1e-9; r=np.fft.ifft2(R).real
    y,x=np.unravel_index(np.argmax(r),r.shape)
    if y>H//2: y-=H
    if x>W//2: x-=W
    return x,y
def motion(f,fps=15):
    s=np.array([shift(f[i+1],f[i]) for i in range(len(f)-1)],float)
    return s.sum(0)*(1080/W), s  # total en px de 1080
if __name__=='__main__':
    p=sys.argv[1]; fps=15
    f=load(p,fps=fps)
    cuts=[int(c) for c in sys.argv[2].split(',')]
    for a,b in zip(cuts,cuts[1:]):
        seg=f[int(a/30*fps)+1:int(b/30*fps)-1]
        tot,s=motion(seg)
        d='→ DERECHA' if tot[0]>60 else ('← IZQUIERDA' if tot[0]<-60 else '· casi fijo')
        v='↓' if tot[1]>60 else ('↑' if tot[1]<-60 else '')
        print(f"{a/30:5.2f}-{b/30:5.2f}s  dx={tot[0]:+6.0f}px dy={tot[1]:+6.0f}px  {d} {v}")
