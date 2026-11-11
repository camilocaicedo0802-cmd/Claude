import wave, numpy as np, sys, json
W=sys.argv[1]
segs=[("Q1","IMG_7103",1.74,2.92),("A1","IMG_7103",3.32,4.42),("Q2","IMG_7103",5.78,7.06),("A2","IMG_7103",7.38,9.64),
("Q3","IMG_7103",11.44,13.20),("A3","IMG_7103",18.12,20.96),("Q4","IMG_7103",34.34,35.66),("A4","IMG_7103",36.14,37.06),
("Q5","IMG_7103",40.92,42.90),("A5","IMG_7103",57.22,60.60),("Q6","IMG_7106",2.26,3.68),("A6","IMG_7106",4.88,7.82),
("Q7","IMG_7106",10.42,12.20),("A7a","IMG_7106",13.70,17.06),("A7b","IMG_7106",35.38,37.40),("Q8","IMG_7108",4.34,6.98),
("A8","IMG_7108",7.84,10.88),("C1","IMG_7110",7.00,10.60),("C2","IMG_7110",13.90,15.60),("C3a","IMG_7110",19.28,21.06),("C3b","IMG_7110",22.96,25.94)]
X={}
def load(f):
    if f not in X:
        w=wave.open(f"{W}/audio/{f}.wav"); X[f]=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    return X[f]
def env(x):  # 10ms rms frames
    n=len(x)//160; return 20*np.log10(np.sqrt((x[:n*160].reshape(n,160)**2).mean(1))+1e-9)
out={}
for name,f,a,b in segs:
    e=env(load(f)); fr=lambda t:int(t*100)
    floor=np.percentile(e,10)
    # in: search back from a up to 0.30s for first frame where energy < floor+8 sustained
    i=fr(a)
    lo=max(0,fr(a-0.30))
    win=e[lo:fr(a)+3]
    k=np.argmin(win); ins=(lo+k)/100
    # out: search forward from b up to 0.45s for minimum
    hi=min(len(e)-1,fr(b+0.45)); win2=e[fr(b)-3:hi]; k2=np.argmin(win2); outs=(fr(b)-3+k2)/100
    peak=e[fr(a):fr(b)].max()
    print(f"{name:4s} {f} {a:6.2f}->{ins:6.2f}  {b:6.2f}->{outs:6.2f}  dur={outs-ins:5.2f} min_in={win.min():6.1f} min_out={win2.min():6.1f} peak={peak:6.1f} floor={floor:6.1f}")
    out[name]=(f,round(ins,2),round(outs,2))
json.dump(out,open(W+'/voice_segs.json','w'),indent=1)
