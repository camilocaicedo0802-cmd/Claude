import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
src=sys.argv[1]; a,b=map(float,sys.argv[2].split(':'))
raw=subprocess.run(["ffmpeg","-v","error","-ss",str(a),"-t",str(b-a),"-i",src,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
x=np.frombuffer(raw,dtype=np.float32); sr=16000; hop=160
e=np.sqrt(np.convolve(x**2,np.ones(400)/400,'same'))[::hop]; db=20*np.log10(e+1e-9)
floor=np.percentile(db,10); thr=floor+12
on=db>thr
# close gaps < 0.12 s, drop islands < 0.08 s
isl=[]; i=0; n=len(on)
while i<n:
    if on[i]:
        j=i
        while j<n and on[j]: j+=1
        isl.append([i,j]); i=j
    else: i+=1
merged=[]
for s,t in isl:
    if merged and s-merged[-1][1] < 12: merged[-1][1]=t
    else: merged.append([s,t])
merged=[m for m in merged if m[1]-m[0]>=8]
m=WhisperModel("medium",device="cpu",compute_type="int8")
print(f"floor {floor:.0f} dB")
for s,t in merged:
    s0=max(0,s*hop-1600); t0=min(len(x),t*hop+1600)
    segs,_=m.transcribe(x[s0:t0],language="en",condition_on_previous_text=False,initial_prompt="Gua sha, hyaluronic serum, plumper, dewy, depuff, sculpt, Radiant Blueberry Boost, Slate, Tulsa.")
    txt=" ".join(sg.text.strip() for sg in segs)
    print(f"{a+s*hop/sr:7.2f}-{a+t*hop/sr:7.2f} ({(t-s)*hop/sr:4.2f}s) pk{db[s:t].max():.0f}  {txt}")
