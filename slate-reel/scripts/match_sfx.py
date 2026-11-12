# Find which SFX files appear in the reference audio, and where, via normalized cross-correlation.
import numpy as np, librosa, glob, os, sys, json, subprocess, tempfile
from scipy.signal import fftconvolve, butter, sosfiltfilt
SR = 22050
ref, _ = librosa.load('/home/user/Claude/slate-reel/analysis/audio_full.wav', sr=SR, mono=True)
def hp(x, fc):
    sos = butter(4, fc, 'hp', fs=SR, output='sos'); return sosfiltfilt(sos, x)
def load_any(p):
    try:
        y, _ = librosa.load(p, sr=SR, mono=True); return y
    except Exception:
        tmp = tempfile.mktemp(suffix='.wav')
        subprocess.run(['ffmpeg','-v','error','-y','-i',p,'-ac','1','-ar',str(SR),tmp])
        y, _ = librosa.load(tmp, sr=SR, mono=True); os.remove(tmp); return y
def ncc(x, s):
    # normalized cross-correlation of template s over signal x
    num = fftconvolve(x, s[::-1], mode='valid')
    e = np.cumsum(np.concatenate([[0], x**2]))
    win = e[len(s):] - e[:-len(s)]
    den = np.sqrt(np.maximum(win, 1e-12)) * np.linalg.norm(s)
    return num / den
results = {}
files = sorted(glob.glob(sys.argv[1] + '/**/*', recursive=True))
files = [f for f in files if os.path.isfile(f) and f.lower().rsplit('.',1)[-1] in ('wav','mp3','m4a','mpeg','aif','aiff','ogg','flac')]
for f in files:
    s = load_any(f)
    if len(s) < SR*0.05: continue
    # trim leading silence, use the first 0.6 s (or full if shorter) as template
    nz = np.where(np.abs(s) > 0.02*np.abs(s).max())[0]
    s = s[nz[0]:] if len(nz) else s
    dur = len(s)/SR
    tpl = s[:int(SR*min(0.6, dur))]
    if len(tpl) > len(ref): continue
    best = []
    for band, fc in (('full', None), ('hp2k', 2000)):
        x = ref if fc is None else hp(ref, fc)
        t = tpl if fc is None else hp(tpl, fc)
        if np.linalg.norm(t) < 1e-6: continue
        c = ncc(x, t)
        # peaks
        idx = np.argsort(c)[::-1]
        picked = []
        for i in idx:
            if c[i] < 0.30 or len(picked) >= 12: break
            if all(abs(i - j) > SR*0.3 for j in picked): picked.append(i)
        best += [(band, round(i/SR, 3), round(float(c[i]), 3)) for i in picked]
    results[os.path.relpath(f, sys.argv[1])] = {'dur': round(dur,2), 'hits': sorted(best, key=lambda h: h[1])}
    if best:
        print(f"{os.path.relpath(f, sys.argv[1])[:60]:60s} dur={dur:5.2f}  " + ' '.join(f"{b}@{t}s:{v}" for b,t,v in sorted(best, key=lambda h:h[1])))
json.dump(results, open('/home/user/media-in/work/sfx_matches.json','w'), indent=1, ensure_ascii=False)
print('done', len(files), 'files')
