"""Construye el montaje de voz: recorta tomas, quita silencios, limpia audio y remapea palabras."""
import json, subprocess, os, numpy as np, librosa
T={t["id"]:t for t in json.load(open("material/tomas.json"))}
def words(ids, a=None, b=None):
    ws=[]
    for i in ids: ws+=T[i]["words"]
    return [w for w in ws if (a is None or w["s"]>=a-1e-6) and (b is None or w["e"]<=b+1e-6)]
# id, fuente, palabras, vertical(4K), sección
EDL=[
 ("s01_hook","crudo/C454.MOV",words(["C454_1"]),"hook"),
 ("s02_casting","crudo/C455.MOV",words(["C455_2"],13.7),"problema"),
 ("s03_propuesta","crudo/C455.MOV",[dict(w,s=max(w["s"],43.80)) for w in words(["C455_4"],43.39,47.7)],"problema"),
 ("s04_escucho","crudo/C455.MOV",words(["C455_10","C455_11","C455_12"]),"problema"),
 ("s05_decisiones","crudo/C455.MOV",words(["C455_17"]),"problema"),
 ("s06_bits","crudo/C456.MOV",words(["C456_2"]),"solucion"),
 ("s08_melodia","crudo/C458.MOV",words(["C458_3"]),"solucion"),
 ("s09_accion","crudo/C459.MOV",words(["C459_2"]),"solucion"),
 ("s10_conflicto","crudo/C459.MOV",words(["C459_7"]),"solucion"),
 ("s11_streaming","crudo/C460.MOV",words(["C460_1"]),"solucion"),
 ("s12_testimonio","testimonios/testimonio_2.mp4",words(["testimonio_2_3"]),"prueba"),
 ("s13_repitas","crudo/C461.MOV",words(["C461_4"]),"cta"),
 ("s14_comenta","crudo/C462.MOV",words(["C462_2"]),"cta"),
]
MAXGAP,KEEP=0.26,0.10
out=[]
for sid,src,ws,sec in EDL:
    name=os.path.splitext(os.path.basename(src))[0]
    y,sr=librosa.load(f"material/audio16k/{name}.wav",sr=16000)
    hop=160; rms=librosa.feature.rms(y=y,frame_length=400,hop_length=hop)[0]; db=20*np.log10(rms+1e-9)
    a0,b0=ws[0]["s"],ws[-1]["e"]
    sp=np.percentile(db[int(a0*100):int(b0*100)],85); thr=sp-24
    # extremos: ajustar al inicio/fin real de la voz (umbral estricto para no confundir ruido con voz)
    strict=sp-13
    if "testimonio" in src:
        start,end=a0-0.08,b0+0.05
    else:
        lo,hi=int(max(0,a0-0.3)*100),int((b0+0.5)*100)
        idx=[k for k in range(lo,min(hi,len(db))) if db[k]>strict]
        first=next(k for k in idx if k>=int((a0-0.3)*100)); 
        # primera voz fuerte tras el silencio previo a la toma
        k=int(a0*100)
        while k<len(db) and db[k]<=strict: k+=1
        j=k
        while j>int((a0-0.3)*100) and db[j-1]>thr: j-=1
        start=max(0,min(k,max(j,k-12))/100-0.07)
        last=max(k2 for k2 in idx if k2<=int((b0+0.35)*100))
        j=last
        while j<min(len(db)-1,last+35) and db[j]>thr: j+=1
        end=j/100+0.08
        if end>b0+0.24:  # hay voz de otra toma pegada: cortar en el valle de energía
            seg=db[int(b0*100):int((b0+0.30)*100)]; end=b0+int(np.argmin(seg))/100
    # silencios internos
    quiet=db[int(start*100):int(end*100)]<(sp-16); keep=[]; cur=start; k=0; n=len(quiet)
    while k<n:
        if quiet[k]:
            k2=k
            while k2<n and quiet[k2]: k2+=1
            if (k2-k)/100>MAXGAP and k>5 and k2<n-5:
                keep.append((cur,start+k/100+KEEP)); cur=start+k2/100-KEEP
            k=k2
        else: k+=1
    keep.append((cur,end))
    # remapeo de palabras
    def remap(t):
        acc=0
        for a,b in keep:
            if t<=b: return acc+max(0,t-a)
            acc+=b-a
        return acc
    def onset(w):
        a,b=int(w["s"]*100),int(w["e"]*100)
        for k in range(a,b):
            if db[k]>sp-20: return max(w["s"],k/100-0.02)
        return w["s"]
    W=[dict(text=w["w"],start=round(remap(max(onset(w),start)),3),end=round(remap(min(w["e"],end)),3)) for w in ws]
    dur=sum(b-a for a,b in keep); cuts=[round(sum(b2-a2 for a2,b2 in keep[:q+1]),3) for q in range(len(keep)-1)]
    out.append(dict(id=sid,src=src,section=sec,keep=[(round(a,3),round(b,3)) for a,b in keep],duration=round(dur,3),cuts=cuts,words=W,text=" ".join(w["w"] for w in ws)))
    print(f"{sid:16s} {src:28s} {start:6.2f}-{end:6.2f} → {dur:5.2f}s  piezas={len(keep)} cortes={cuts}")
json.dump(out,open("material/edl.json","w"),ensure_ascii=False,indent=1)
print("TOTAL voz: %.2f s"%sum(o["duration"] for o in out))
