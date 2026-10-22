"""Mix voice + ducked music + SFX cues, then loudness-normalise to -14 LUFS.

Usage: python3 mix_audio.py <work_dir> <assets_dir> <source.mov> <music.mp3> <out.wav>
"""
import json, os, subprocess, sys
import numpy as np
import scipy.io.wavfile as wf
import scipy.signal as sg

WORK, ASSETS, SRC, MUSIC, OUT = sys.argv[1:6]
SR = 48000
DUR = 43.4
VOICE_END = 41.6
N = int(DUR * SR)

def load(path, start=0.0, dur=None, filters=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path]
    if dur: cmd += ["-t", str(dur)]
    if filters: cmd += ["-af", filters]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def fit(x, n):
    out = np.zeros((n, 2))
    out[:min(n, len(x))] = x[:n]
    return out

db = lambda d: 10 ** (d / 20)

# voice: clean low rumble, gentle compression, presence lift
voice = fit(load(SRC, 0, VOICE_END, "highpass=f=85,lowpass=f=15000,"
                 "equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1:g=-1.5,"
                 "acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=2.5"), N)
fade = int(0.25 * SR); e = int(VOICE_END * SR)
voice[e - fade:e] *= np.linspace(1, 0, fade)[:, None]
voice /= np.sqrt(np.mean(voice[:e] ** 2)) + 1e-9
voice *= db(-18)

# music: start on a downbeat so the hook slam lands on the beat
import librosa
y, sr = librosa.load(MUSIC, sr=22050, duration=12)
_, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
offset = float(beats[0]) if len(beats) else 0.0
music = fit(load(MUSIC, offset, DUR + 1), N)
music /= np.sqrt(np.mean(music ** 2)) + 1e-9
music *= db(-18)

# ducking curve from the voice envelope
env = np.sqrt(sg.lfilter([1], [1, -0.995], (voice ** 2).mean(1)) * 0.005)
active = (env > db(-38)).astype(np.float64)
target = np.where(active > 0, db(-13.0), db(-8.0))          # music level relative to its normalised RMS
t = np.arange(N) / SR
target = np.where(t >= VOICE_END - 0.1, db(-2.5), target)   # end card: music up
gain = np.empty(N); g = target[0]
att, rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.30 * SR))
for i in range(N):                                         # one-pole smoothing (fast down, slow up)
    a = att if target[i] < g else rel
    g = a * g + (1 - a) * target[i]
    gain[i] = g
gain *= np.clip(t / 0.05, 0, 1)
gain *= np.clip((DUR - t) / 0.9, 0, 1)
music *= gain[:, None]

# SFX cues
sfx = np.zeros((N, 2))
cache = {}
for tc, name, gdb in json.load(open(os.path.join(WORK, "sfx_cues.json"))):
    if name not in cache:
        r, x = wf.read(os.path.join(ASSETS, "sfx", name + ".wav"))
        x = x.astype(np.float64) / 32768.0
        cache[name] = x if x.ndim == 2 else np.stack([x, x], 1)
    x = cache[name] * db(gdb) * db(-6)
    s = int(tc * SR)
    if s >= N: continue
    n = min(len(x), N - s)
    sfx[s:s + n] += x[:n]

mix = voice + music + sfx
mix /= max(1.0, np.abs(mix).max() / 0.98)
tmp = OUT + ".pre.wav"
wf.write(tmp, SR, mix.astype(np.float32))

# two-pass loudnorm to -14 LUFS / -1 dBTP
p1 = subprocess.run(["ffmpeg", "-v", "info", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.0:LRA=9:print_format=json",
                     "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(p1[p1.rfind("{"):p1.rfind("}") + 1])
af = (f"loudnorm=I=-14:TP=-1.0:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", str(SR), OUT], check=True)
os.remove(tmp)
print("music offset", round(offset, 3), "measured", m["input_i"], "LUFS")
