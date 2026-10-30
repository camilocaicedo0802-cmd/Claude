"""Audio mix: voice-over + ducked music + SFX, rendered in numpy, then loudness-normalised with ffmpeg."""
import sys, os, subprocess, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import S, A
import edl

SR = 48000
VO_SRC = os.environ.get("VO_FILE", S + "/assets/narracion.mp3")


def decode(path, ss=0.0, dur=None, af=None, mono=False):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path]
    if dur:
        cmd += ["-t", str(dur)]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "1" if mono else "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, 1) if mono else a.reshape(-1, 2)


def db(x):
    return 10 ** (x / 20)


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i < 0:
        clip = clip[-i:]
        i = 0
    n = min(len(clip), len(buf) - i)
    if n > 0:
        buf[i:i + n] += clip[:n] * gain


def fade(clip, fin=0.0, fout=0.0):
    c = clip.copy()
    n = len(c)
    if fin:
        k = min(n, int(fin * SR))
        c[:k] *= np.linspace(0, 1, k)[:, None]
    if fout:
        k = min(n, int(fout * SR))
        c[n - k:] *= np.linspace(1, 0, k)[:, None]
    return c


def env_follow(x, attack=0.03, release=0.35, win=0.02):
    hop = int(win * SR)
    m = x.shape[0] // hop
    rms = np.sqrt((x[:m * hop, 0] ** 2).reshape(m, hop).mean(1) + 1e-12)
    out = np.zeros_like(rms)
    a_up = np.exp(-win / attack)
    a_dn = np.exp(-win / release)
    v = 0.0
    for i, r in enumerate(rms):
        v = a_up * v + (1 - a_up) * r if r > v else a_dn * v + (1 - a_dn) * r
        out[i] = v
    return np.repeat(out, hop)[: x.shape[0]], hop


def main(out_wav):
    shots, ovs, sfx = edl.build()
    total = edl.END
    N = int(total * SR) + SR
    mix = np.zeros((N, 2), np.float32)

    # --- voice-over (cleaned, compressed)
    vo = decode(VO_SRC, 0, edl.VO_END + 0.6,
                af="highpass=f=75,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,"
                   "equalizer=f=3500:t=q:w=1.2:g=2", mono=False)
    vo = fade(vo, 0, 0.4)
    vo_buf = np.zeros_like(mix)
    place(vo_buf, vo, edl.OFF)
    # normalise VO peak-ish to -3 dBFS rms-ish target
    vrms = np.sqrt(np.mean(vo_buf[vo_buf[:, 0] != 0] ** 2))
    vo_buf *= db(-17) / max(vrms, 1e-6)

    # --- music
    music = np.zeros_like(mix)
    title = 106.64 + edl.OFF
    m1 = decode(A + "/music/Hitman.mp3", 52.0, title + 0.4)
    m1 = fade(m1, 0.6, 0.9)
    place(music, m1, 0.0)
    m2 = decode(A + "/music/Malicious.mp3", 0.0, total - (111.2 + edl.OFF) + 0.5)
    m2 = fade(m2, 1.2, 3.5)
    place(music, m2, 111.2 + edl.OFF)
    mrms = np.sqrt(np.mean(music[music[:, 0] != 0] ** 2))
    music *= db(-27) / max(mrms, 1e-6)
    # ducking from VO envelope
    env, _ = env_follow(vo_buf)
    thr = db(-35)
    active = np.clip((env - thr) / (thr * 3), 0, 1)
    gain = 1.0 - 0.45 * active          # about -5 dB under speech
    music *= gain[:, None]

    # --- sfx
    sfx_buf = np.zeros_like(mix)
    cache = {}
    times = []
    for t, name, vol, dur in sfx:
        if name not in cache:
            cache[name] = decode(A + f"/sfx/{name}.mp3")
        c = cache[name]
        if dur:
            c = fade(c[: int(dur * SR)], 0, min(0.4, dur / 3))
        place(sfx_buf, c, t, vol)
        times.append(t)
    # automatic transition sounds where none is placed
    auto = {"whip": ("1490", 0.45, -0.12), "zoom": ("1492", 0.5, -0.15), "glitch": ("2946", 0.45, -0.05)}
    for s in shots:
        if s.get("tin") and s["tin"][0] in auto:
            name, vol, dt = auto[s["tin"][0]]
            t = s["t"] + dt
            if any(abs(t - x) < 0.35 for x in times):
                continue
            if name not in cache:
                cache[name] = decode(A + f"/sfx/{name}.mp3")
            place(sfx_buf, cache[name], t, vol)
    sfx_buf *= db(-9)

    mix = vo_buf + music + sfx_buf
    mix = mix[: int(total * SR)]
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    tmp = S + "/work/mix_raw.wav"
    import wave
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(tmp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    # two-pass loudnorm to YouTube-friendly -14 LUFS
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", str(SR), out_wav], check=True)
    print("mix done", out_wav, js["input_i"])


if __name__ == "__main__":
    main(sys.argv[1])
