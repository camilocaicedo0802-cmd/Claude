import numpy as np, soundfile as sf, os, sys
base = sys.argv[1]; out = sys.argv[2]
os.makedirs(out+"/sfx", exist_ok=True)
st = {s: sf.read(f"{base}/{s}.wav")[0] for s in ["drums","bass","other","vocals"]}
sr = 44100
def T(t): return int(round(t*sr))
XF = T(0.03)
def patch(y, a, b, off):
    """replace y[a:b] with y[a+off:b+off] using equal-power crossfades"""
    y = y.copy(); src = st_orig[cur][T(a+off)-XF:T(b+off)+XF].copy()
    seg_len = T(b)-T(a)+2*XF
    src = src[:seg_len]
    dst = y[T(a)-XF:T(a)-XF+len(src)]
    n=len(src); w=np.ones(n)
    ramp=np.sin(np.linspace(0,np.pi/2,XF))**2
    w[:XF]=ramp; w[-XF:]=ramp[::-1]
    w=w[:,None]
    y[T(a)-XF:T(a)-XF+n] = dst*(1-w) + src*w
    return y
st_orig = {k:v.copy() for k,v in st.items()}
patches = {
 "drums": [(0.00+0.03,1.42,4.0),(2.80,3.22,2.0),(6.32,7.15,-2.0),(7.15,7.82,2.0)],
 "other": [(1.60,2.85,2.0),(2.80,3.22,2.0),(6.32,7.15,-2.0),(7.15,7.82,2.0),(11.52,12.88,2.0),(17.28,17.98,-2.0),(20.12,21.32,-4.0),(25.32,27.08,-4.0)],
}
clean = {}
for s in ["drums","bass","other"]:
    y = st[s]
    global cur
    cur = s
    for (a,b,off) in patches.get(s,[]):
        y = patch(y,a,b,off)
    clean[s]=y
bed = clean["drums"]+clean["bass"]+clean["other"]
sf.write(out+"/musica_timeless_limpia.wav", bed, sr)
raw = st["drums"]+st["bass"]+st["other"]
sf.write(out+"/musica_timeless_con_sfx.wav", raw, sr)
def cut(name, srcs, a, b, fi=0.005, fo=0.04, gain_to=-3.0):
    y = sum(st[s] for s in srcs)[T(a):T(b)].copy()
    n=len(y); fi_n=T(fi); fo_n=T(fo)
    y[:fi_n]*=np.linspace(0,1,fi_n)[:,None]; y[-fo_n:]*=np.linspace(1,0,fo_n)[:,None]
    pk=np.max(np.abs(y)); y*=10**(gain_to/20)/max(pk,1e-9)
    sf.write(f"{out}/sfx/{name}.wav", y, sr)
    print(f"{name}: {a:.2f}-{b:.2f}s from {srcs}, {b-a:.2f}s")
cut("flash_click_1", ["drums"], 0.03, 0.26)
cut("flash_click_2", ["drums"], 0.50, 0.70)
cut("flash_click_3", ["drums"], 0.81, 1.00)
cut("boom_ring",     ["other"], 1.62, 2.90, fo=0.3)
cut("boom_ring_2",   ["other"], 20.14, 21.40, fo=0.3)
cut("glass_crack",   ["drums","other"], 2.82, 3.30, fo=0.1)
cut("riser",         ["drums","other"], 6.30, 7.80, fi=0.3, fo=0.08)
cut("ui_beep",       ["other"], 11.54, 12.90, fo=0.1)
cut("photo_paper",   ["other"], 17.30, 17.98, fo=0.08)
cut("pops",          ["other"], 25.34, 27.08, fo=0.1)
