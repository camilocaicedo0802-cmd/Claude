"""Audio: cleaned dialogue + ducked music + SFX -> mix.wav (48k stereo), then loudness-normalised.

usage: python3 mix.py <work> <out_dir> [--no-music]
"""
import json, math, os, subprocess, sys
import numpy as np

W, OD = sys.argv[1], sys.argv[2]
NO_MUSIC = "--no-music" in sys.argv
T = json.load(open(os.path.join(W, "timeline.json")))
SR = 48000
DUR = T["duration"] + 0.2
N = int(DUR * SR)
SFX = os.path.join(W, "res", "sfx")
MUSIC = os.path.join(W, "res", "music", "Tommy Richman - Million Dollar Baby [Instrumental].mp3")
os.makedirs(OD, exist_ok=True)
db = lambda x: 10 ** (x / 20)


def load(path, ss=None, to=None, af=None, ch=2):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None: cmd += ["-ss", str(ss)]
    if to is not None: cmd += ["-to", str(to)]
    cmd += ["-i", path, "-vn"]
    if af: cmd += ["-af", af]
    cmd += ["-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def place(bus, x, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]; i = 0
    n = min(len(x), len(bus) - i)
    if n > 0:
        bus[i:i + n] += x[:n] * gain


def active_rms_db(x):
    m = x.mean(1) if x.ndim == 2 else x
    fr = 480
    n = len(m) // fr
    r = np.sqrt((m[:n * fr].reshape(n, fr) ** 2).mean(1) + 1e-12)
    act = r[r > r.max() * 0.12]
    return 20 * np.log10(np.sqrt((act ** 2).mean()) + 1e-12)


# ------------------------------------------------------------------ dialogue
VOICE_AF = ("highpass=f=85,lowpass=f=15000,afftdn=nr=10:nf=-48:tn=1,"
            "equalizer=f=220:t=q:w=1.0:g=-2.0,equalizer=f=3600:t=q:w=1.2:g=2.5,equalizer=f=9500:t=h:w=0.7:g=1.5,"
            "acompressor=threshold=-24dB:ratio=3:attack=5:release=90:makeup=3,"
            "deesser=i=0.35:m=0.5:f=0.5")
voice = np.zeros((N, 2), np.float32)
vact = np.zeros(N, np.float32)
TARGET = {"q": -17.5, "a": -16.5, "c": -16.5}
for v in T["voice"]:
    src = os.path.join(W, "raw", v["src"] + ".MOV")
    x = load(src, v["in"], v["out"], VOICE_AF, ch=1)[:, 0]
    # short fades so cuts never click
    f = int(0.02 * SR)
    x[:f] *= np.linspace(0, 1, f); x[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    g = db(TARGET[v["kind"]] - active_rms_db(x))
    x = x * g
    st = np.stack([x, x], 1)
    place(voice, st, v["at"])
    i = int(v["at"] * SR)
    vact[i:i + len(x)] = np.maximum(vact[i:i + len(x)], 1.0)
print("dialogue placed:", len(T["voice"]))

# ------------------------------------------------------------------ music with ducking
music = np.zeros((N, 2), np.float32)
if not NO_MUSIC:
    m = load(MUSIC, T["music_offset"], T["music_offset"] + DUR + 0.5,
             "equalizer=f=2800:t=q:w=1.4:g=-3,equalizer=f=60:t=q:w=1.0:g=-1.5")
    m = m[:N]
    m *= db(-19.0 - active_rms_db(m))       # music bed reference level when no one speaks
    # ducking envelope from voice activity (attack 80 ms, release 350 ms), computed at 100 Hz
    hop = SR // 100
    a = vact[: (N // hop) * hop].reshape(-1, hop).max(1)
    env = np.zeros_like(a)
    for k in range(len(a)):
        prev = env[k - 1] if k else 0
        coef = 0.30 if a[k] > prev else 0.03
        env[k] = prev + (a[k] - prev) * coef
    gain_db = -10.5 * env                       # -9 dB under dialogue
    gain = np.repeat(db(gain_db), hop)
    gain = np.pad(gain, (0, N - len(gain)), constant_values=gain[-1])
    m[: len(gain)] *= gain[:, None]
    # fade in 15 ms, fade out over the last 1.6 s
    fi = int(0.015 * SR); m[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(1.6 * SR); end = int(T["duration"] * SR)
    m[end - fo:end] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    m[end:] = 0
    music = m

# ------------------------------------------------------------------ sound design
sfx = np.zeros((N, 2), np.float32)
cache = {}
def S(name, ss=None, to=None):
    k = (name, ss, to)
    if k not in cache:
        cache[k] = load(os.path.join(SFX, name), ss, to)
    return cache[k]
events = []
def ev(t, name, gdb, peak=0.0, ss=None, to=None):
    events.append((t - peak, name, gdb, ss, to))

# hook
ev(0.00, "Swoosh 01 - 04.wav", -8, peak=0.09)
ev(0.16, "Pop up SFX.mp3", -5, peak=0.19)
ev(0.95, "Swoosh 01 - 05.wav", -12, peak=0.07)
ev(1.16, "disappear.wav", -12, peak=0.45)
# boundaries
ends = [T["hook"]["end"]] + [p["end"] for p in T["pairs"]]
whoosh = ["VS_Short Whoosh 1.mp3", "VS_Short Whoosh 3.mp3", "VS_Short Whoosh 6.mp3", "VS_Short Whoosh 2.mp3"]
for k, B in enumerate(ends):
    if k == 0:
        ev(B, "Woosh Effect 5.wav", -9, peak=0.45)
    elif k == len(ends) - 1:
        ev(B, "Woosh Effect 2.wav", -10, peak=1.11)
    else:
        ev(B - 0.06, whoosh[k % len(whoosh)], -11, peak=0.55)
# pairs
for p in T["pairs"]:
    lab = max(p["q_first"] - 0.16, p["start"] + 0.12)
    ev(lab + 0.06, "Pop up SFX.mp3", -11, peak=0.19)
    ev(p["split"] + 0.04, "Swoosh 01 - 03.wav", -10, peak=0.08)
    ct = min(p["split"] + 0.20, p["a_first"] - 0.34)
    if ct > p["split"] + 0.02:
        ev(ct, "Acierto y error.mp3", -16, peak=0.08, ss=2.78, to=3.16)
    if p.get("S2"):
        ev(p["s2_at"] + 0.10, "Swoosh 01 - 07.wav", -13, peak=0.07)
# outro
for c in T["outro"]["clips"]:
    if c.get("flash"):
        ev(c["start"], "Camera Shutter Click 01.wav", -8, peak=0.07)
        ev(c["start"], "Camera Flash.wav", -16, peak=0.12)
    if c.get("punch"):
        ev(c["start"], "Swoosh 01 - 06.wav", -12, peak=0.07)
last_cap = T["outro"]["captions"][-1]
ev(last_cap[1] + 0.05, "disappear.wav", -12, peak=0.45)

for t, name, gdb, ss, to in events:
    x = S(name, ss, to)
    if ss is not None:
        f = int(0.01 * SR); x = x.copy(); x[:f] *= np.linspace(0, 1, f)[:, None]; x[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
    # normalise each sfx by its own peak so the gain table is meaningful
    pk = np.abs(x).max() + 1e-9
    place(sfx, x / pk * db(-6), t, db(gdb))
print("sfx events:", len(events))

if True:
    hop = SR // 100
    a_ = vact[: (N // hop) * hop].reshape(-1, hop).max(1)
    env_ = np.zeros_like(a_)
    for k in range(len(a_)):
        prev = env_[k - 1] if k else 0
        env_[k] = prev + (a_[k] - prev) * (0.5 if a_[k] > prev else 0.05)
    g_ = np.repeat(db(-7.0 * env_), hop)
    g_ = np.pad(g_, (0, N - len(g_)), constant_values=1.0)
    sfx *= g_[:, None]
mix = voice + music + sfx * 0.9
end = int((T["duration"]) * SR)
mix = mix[:end + int(0.05 * SR)]
tmp = os.path.join(OD, "mix_raw.wav")
import wave
pcm = np.clip(mix, -1, 1)
with wave.open(tmp, "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes((pcm * 32767).astype(np.int16).tobytes())
# two-pass loudness normalisation to -14 LUFS / -1 dBTP
meas = subprocess.run(["ffmpeg", "-v", "info", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
js = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
      f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
outp = os.path.join(OD, "mix_nomusic.wav" if NO_MUSIC else "mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", outp], check=True)
print("written", outp, "input LUFS", js["input_i"])
