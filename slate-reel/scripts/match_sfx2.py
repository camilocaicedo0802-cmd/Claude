import numpy as np, librosa, glob, os, sys, json, subprocess, tempfile, warnings
warnings.filterwarnings('ignore')
from scipy.signal import fftconvolve
SR = 22050
ref, _ = librosa.load('/home/user/Claude/slate-reel/analysis/audio_full.wav', sr=SR, mono=True)
e = np.cumsum(np.concatenate([[0], ref**2]))
def load_any(p):
    tmp = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg','-v','error','-y','-i',p,'-ac','1','-ar',str(SR),tmp])
    try:
        y, _ = librosa.load(tmp, sr=SR, mono=True)
    except Exception:
        y = np.zeros(10)
    if os.path.exists(tmp): os.remove(tmp)
    return y
def ncc(s):
    num = fftconvolve(ref, s[::-1], mode='valid')
    win = e[len(s):] - e[:-len(s)]
    return num / (np.sqrt(np.maximum(win, 1e-9)) * np.linalg.norm(s))
root = sys.argv[1]
files = [f for f in sorted(glob.glob(root + '/**/*', recursive=True)) if os.path.isfile(f) and f.lower().rsplit('.',1)[-1] in ('wav','mp3','m4a','mpeg','aif','aiff','ogg','flac')]
seen = set(); out = []
for f in files:
    base = os.path.basename(f).replace('Copia de ','')
    if base in seen: continue
    seen.add(base)
    y = load_any(f)
    if len(y) < SR*0.05 or np.abs(y).max() < 1e-4: continue
    segs = librosa.effects.split(y, top_db=38, frame_length=1024, hop_length=256)
    segs = [s for s in segs if (s[1]-s[0]) > SR*0.04][:40]
    for k,(a,b) in enumerate(segs):
        tpl = y[a:min(b, a+int(SR*0.5))]
        if len(tpl) < SR*0.04 or np.linalg.norm(tpl) < 1e-4: continue
        c = ncc(tpl)
        med = np.median(np.abs(c)); mad = np.median(np.abs(np.abs(c)-med))*1.4826 + 1e-9
        idx = np.argsort(c)[::-1]; picked=[]
        for i in idx:
            if c[i] < 0.28 or len(picked) >= 10: break
            if all(abs(i-j) > SR*0.25 for j in picked): picked.append(i)
        hits = [(round(i/SR,3), round(float(c[i]),3), round(float((c[i]-med)/mad),1)) for i in picked]
        hits = [h for h in hits if h[2] > 9]
        if hits:
            rel = os.path.relpath(f, root)
            out.append({'file': rel, 'seg': k, 'seg_start': round(a/SR,3), 'seg_dur': round((b-a)/SR,3), 'hits': sorted(hits)})
            print(f"{rel[:55]:55s} seg{k:02d}@{a/SR:6.2f}s ({(b-a)/SR:4.2f}s): " + ' '.join(f"{t}s r={v} z={z}" for t,v,z in sorted(hits)), flush=True)
json.dump(out, open(sys.argv[2],'w'), indent=1, ensure_ascii=False)
print('done', len(files))
