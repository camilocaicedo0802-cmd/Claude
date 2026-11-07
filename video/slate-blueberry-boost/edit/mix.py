"""Audio: voice (best takes) + music bed + SFX extracted from the reference -> mix.wav (48 kHz stereo)."""
import sys, os, json, subprocess, re, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DRIVE", "")
import timeline as TL
E = os.path.dirname(os.path.abspath(__file__)); SR = 48000
SFXDIR, MUSIC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

def lufs(path):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])

def load(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

# 1) voice: per-piece level matching, then EQ / de-ess / compression in ffmpeg
v, sr = sf.read(f"{E}/voice_raw.wav", dtype="float32")
vmap = json.load(open(f"{E}/voice_raw_map.json"))
lev = []
for p in vmap:
    seg = v[int(p["t0"] * SR):int(p["t1"] * SR)]
    fr = seg[: len(seg) // 480 * 480].reshape(-1, 480); e = np.sqrt((fr ** 2).mean(1) + 1e-12)
    act = e[e > np.percentile(e, 40)]
    lev.append(20 * np.log10(np.sqrt((act ** 2).mean()) + 1e-9))
ref = np.median(lev)
g = np.ones_like(v)
for p, l in zip(vmap, lev):
    gain = 10 ** (np.clip(ref - l, -6, 6) / 20)
    g[int(p["t0"] * SR):int(p["t1"] * SR)] = gain
v = v * g
sf.write(f"{E}/voice_lev.wav", v, SR, subtype="FLOAT")
chain = ("highpass=f=85,equalizer=f=250:t=o:w=1.2:g=-2.5,equalizer=f=3800:t=o:w=1.4:g=2.5,"
         "equalizer=f=10000:t=h:w=0.7:g=1.5,deesser=i=0.35,"
         "acompressor=threshold=-24dB:ratio=3:attack=6:release=140:makeup=3")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/voice_lev.wav", "-af", chain, "-ac", "2", "-ar", str(SR), f"{E}/voice_proc.wav"], check=True)
vl = lufs(f"{E}/voice_proc.wav")
voice = load(f"{E}/voice_proc.wav") * 10 ** ((-15.0 - vl) / 20)

N = int(TL.END * SR)
mix = np.zeros((N, 2), np.float32)
mix[: min(N, len(voice))] += voice[:N]

# 2) music bed: reference sits ~12 LU under the voice
m = load(MUSIC)
ml = lufs(MUSIC)
m = m * 10 ** ((-27.5 - ml) / 20)
m = m[:N]
fo = int(0.35 * SR); m[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix[: len(m)] += m

# 3) SFX (levels relative to the reference mix, +1.5 dB to make up for the tonal-only extraction)
for name, t, gdb in TL.SFX:
    x = load(f"{SFXDIR}/{name}.wav") * 10 ** ((gdb + 1.5) / 20)
    i = int(t * SR); j = min(N, i + len(x)); mix[i:j] += x[: j - i]

sf.write(OUT, mix, SR, subtype="FLOAT")
print("voice LUFS", vl, "-> -15 ; music LUFS", ml, "-> -27.5 ; pieces level spread", np.round(np.array(lev) - ref, 1))
