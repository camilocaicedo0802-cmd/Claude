import os, numpy as np, librosa, warnings, json
from scipy.signal import fftconvolve, butter, sosfiltfilt
warnings.filterwarnings("ignore")
SR=22050
sos=butter(4, 300, btype="highpass", fs=SR, output="sos")
ref,_=librosa.load("material/referencia/audio.wav", sr=SR, mono=True); ref=sosfiltfilt(sos, ref)
c2=np.concatenate([[0],np.cumsum(ref**2)])
files=[]
for root,_,fs in os.walk("material/drive/SFX"):
    if "SFX2" in root: continue
    for f in fs:
        if f.lower().endswith((".wav",".mp3",".m4a",".mpeg")) and not f.startswith("Copia de") and "25 sonidos" not in f: files.append(os.path.join(root,f))
events={"0.0 inicio/zoom-out":(0.0,0.6),"0.27 Prospects":(0.15,0.45),"1.8 Understand":(1.65,2.0),"2.2 avion":(2.05,2.6),"3.15 trans blur":(3.0,3.4),"3.5 tachado":(3.4,4.0),"4.45 trans lineas":(4.3,4.9),"5.2 content grande":(5.0,5.5),"6.2 corte b-roll+aro":(6.0,6.5),"7.0 tooltip tecleado":(6.8,7.9),"8.2 glitch":(8.05,8.5),"8.9 You record/REC":(8.7,9.3),"10.3 tarjeta 1":(10.1,11.3),"11.9 tarjeta 2":(11.7,13.3),"13.7 sub drop":(13.5,14.1),"14.6-15.9 Your plate":(14.5,16.1),"16.9 PLAN":(16.4,17.3),"17.6 SHOOT":(17.4,17.95),"18.3 SCRIPT":(18.1,18.6),"18.9 EDIT":(18.6,19.15),"19.3 POST":(19.15,19.7),"20.5 trans lineas 2":(20.3,20.8),"20.8 value tecleado":(20.7,21.6),"22.8 together":(22.4,23.2)}
best={k:[] for k in events}
seen=set()
for p in sorted(files):
    name=os.path.basename(p)
    if name in seen: continue
    seen.add(name)
    try: y,_=librosa.load(p, sr=SR, mono=True, duration=6)
    except Exception: continue
    if len(y)<SR*0.06: continue
    y=sosfiltfilt(sos,y); env=np.abs(y); idx=np.where(env>env.max()*0.05)[0]
    if len(idx)==0: continue
    y=y[idx[0]:]
    s=y[:int(SR*0.5)]
    if len(s)<SR*0.05: continue
    n=np.linalg.norm(s)
    cc=fftconvolve(ref, s[::-1], mode="valid"); e=np.sqrt(np.maximum(c2[len(s):]-c2[:-len(s)],1e-9)); ncc=np.abs(cc/(n*e))
    mu,sd=ncc.mean(),ncc.std()
    for k,(a,b) in events.items():
        i0,i1=int(max(0,a-0.05)*SR),min(len(ncc),int(b*SR))
        if i1<=i0: continue
        j=i0+int(np.argmax(ncc[i0:i1])); best[k].append(((ncc[j]-mu)/sd, float(ncc[j]), j/SR, name))
out={}
for k,v in best.items():
    v.sort(reverse=True); out[k]=v[:4]
    print(f"[{k}] "+" | ".join(f"{n} (ncc {c:.2f}, z {z:.0f}, t {t:.2f})" for z,c,t,n in v[:4]))
json.dump(out, open("material/referencia/sfx_match_eventos.json","w"), indent=1, ensure_ascii=False)
