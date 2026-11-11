# Mezcla de audio: voz (preguntas fuera de cámara + respuestas) igualada por fase, limpiada y normalizada
# a -14 LUFS, más efectos de sonido sintetizados en los tiempos de timeline.sfx.
#   python3 audio.py salida.wav
import sys, os, subprocess, json, re, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL
from engine import PROJ

SR = 48000
DL = TL.DL
WORK = os.path.join(PROJ, "work")
TARGET_PHASE = -33.0   # LUFS por fase antes de normalizar
TRIM = {"A1": 3.0, "A2": 1.8, "Q3": 1.8, "C2": 0.8, "C4": 0.7, "A8": 0.4}   # ajuste fino medido tras la mezcla (dB)

def wav48(src):
    out = os.path.join(WORK, f"{src}_48k.wav")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(DL, "raw", src + ".MOV"), "-map", "0:a:0",
                        "-ar", str(SR), "-ac", "2", out], check=True)
    return out

def read_wav(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, w.getnchannels())

def write_wav(p, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

def lufs(path, a, b):
    r = subprocess.run(["ffmpeg", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", path, "-af", "ebur128=framelog=quiet",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(m.group(1)) if m else TARGET_PHASE

def build_voice():
    n = int((TL.TOTAL + 0.5) * SR)
    v = np.zeros((n, 2), np.float32)
    cache = {}
    for s in TL.spans:
        src = s["src"]
        if src not in cache: cache[src] = read_wav(wav48(src))
        x = cache[src]
        a, b = int(s["a"] * SR), int(s["b"] * SR)
        seg = x[a:b].copy()
        # ganancia por fase (rampa de 60 ms en los cambios)
        g = np.ones(len(seg), np.float32)
        for i, (ts, pid) in enumerate(s["ph"]):
            te = s["ph"][i + 1][0] if i + 1 < len(s["ph"]) else s["t1"]
            pa, pb = s["a"] + ts - s["t0"], s["a"] + te - s["t0"]
            gain = 10 ** ((TARGET_PHASE - lufs(wav48(src), pa, pb) + TRIM.get(pid, 0.0)) / 20)
            i0, i1 = int((pa - s["a"]) * SR), int((pb - s["a"]) * SR)
            g[i0:i1] = gain
        k = int(0.06 * SR)
        g = np.convolve(g, np.ones(k) / k, mode="same").astype(np.float32)
        seg *= g[:, None]
        f = int(0.012 * SR)
        seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR)
        v[o:o + len(seg)] += seg[:n - o]
    return v

def loudnorm(inp, out, I=-14.0, TP=-1.5, pre=""):
    chain = (pre + "," if pre else "")
    r = subprocess.run(["ffmpeg", "-i", inp, "-af", chain + f"loudnorm=I={I}:TP={TP}:LRA=7:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    ln = (f"loudnorm=I={I}:TP={TP}:LRA=7:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", inp, "-af", chain + ln, "-ar", str(SR), out], check=True)

def main(out):
    v = build_voice()
    raw = os.path.join(WORK, "voice_raw.wav"); write_wav(raw, v)
    clean = os.path.join(WORK, "voice_clean.wav")
    pre = ("highpass=f=80,lowpass=f=16000,afftdn=nr=8:nf=-52,"
           "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.5:g=2,"
           "acompressor=threshold=-24dB:ratio=3:attack=6:release=120:makeup=3,"
           "deesser=i=0.35")
    loudnorm(raw, clean, -14.5, -1.5, pre)
    voice = read_wav(clean)
    # efectos
    sfx = np.zeros_like(voice)
    sdir = os.path.join(PROJ, "sfx")
    for t, name, gdb in TL.sfx:
        x = read_wav(os.path.join(sdir, name + ".wav")) * 10 ** (gdb / 20)
        o = int(max(0, t) * SR)
        e = min(len(sfx), o + len(x))
        sfx[o:e] += x[:e - o]
    write_wav(os.path.join(WORK, "sfx_stem.wav"), sfx)
    mix = voice + sfx
    m = os.path.join(WORK, "mix_pre.wav"); write_wav(m, mix)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", m, "-af", "alimiter=limit=0.89:attack=3:release=60:level=false",
                    "-t", f"{TL.TOTAL:.3f}", out], check=True)
    print("ok", out)

if __name__ == "__main__":
    main(sys.argv[1])
