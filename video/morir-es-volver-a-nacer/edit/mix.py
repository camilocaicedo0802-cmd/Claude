"""Mezcla final: voz + música original (ducking) + efectos sintetizados sincronizados con el montaje.
uso: python mix.py VOZ.wav OUT.wav TOTAL"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A  # noqa: E402
from audio import SR, boom, db, duck, fade, hit, load, place, riser, rumble, static, stereo, ticks, whoosh  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lufs(path):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for line in out.splitlines()[::-1]:
        if line.strip().startswith("I:"):
            return float(line.split()[1])
    return -20.0


def tone(f, d, amp=0.25):
    t = np.arange(int(d * SR)) / SR
    x = np.sin(2 * np.pi * f * t) * amp
    x[: int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))
    x[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return stereo(x)


def heartbeat_sfx(d=2.0, bpm=72):
    return A.heartbeat(d, bpm)


def build_sfx(N, total):
    import timeline
    shots = timeline.build()
    shots.sort(key=lambda s: s.start)
    buf = np.zeros((N, 2), np.float32)
    WH, WH2, BOOM, HIT, RIS = whoosh(), whoosh(0.4, 500, 7000), boom(), hit(), riser()
    for i, s in enumerate(shots):
        end = shots[i + 1].start if i + 1 < len(shots) else total
        names = [type(o).__name__ for o in s.ov]
        if s.tr in ("whip_l", "whip_r", "zoom"):
            place(buf, WH, s.start - 0.3, db(-9))
        elif s.tr == "glitch":
            place(buf, static(0.3), s.start - 0.12, db(-6))
            place(buf, WH2, s.start - 0.2, db(-10))
        elif s.tr == "flash":
            place(buf, HIT, s.start - 0.02, db(-8))
            place(buf, boom(1.2, 90, 40), s.start, db(-12))
        for o in s.ov:
            n = type(o).__name__
            if n == "NeonBox":
                place(buf, HIT, s.start + o.t0, db(-7))
                place(buf, static(0.18), s.start + o.t0, db(-14))
            elif n == "TypeLine":
                d = min(len(o.text) / o.cps, end - s.start - o.t0)
                place(buf, ticks(max(0.2, d), o.cps), s.start + o.t0, db(-13))
            elif n == "BigNumber" and o.count:
                place(buf, ticks(min(o.count[2], 2.0), 20), s.start + o.t0, db(-15))
                place(buf, HIT, s.start + o.t0 + o.count[2], db(-10))
            elif n == "Polaroid":
                place(buf, whoosh(0.35, 800, 6000), s.start + o.t0 - 0.1, db(-16))
            elif n == "Rings":
                place(buf, RIS, s.start - 1.4, db(-14))
                place(buf, BOOM, s.start + 0.1, db(-8))
            elif n == "ECG":
                for k in range(2):
                    place(buf, tone(1000, 0.12, 0.2), s.start + o.t0 + 0.35 + k * 60 / o.bpm, 1.0)
                place(buf, tone(1000, max(0.5, end - s.start - o.flat_at), 0.18), s.start + o.flat_at + 0.3, 1.0)
            elif n == "Cycle":
                place(buf, whoosh(1.2, 150, 1500), s.start + o.t0, db(-16))
        if type(s.base).__name__ == "LightTunnel":
            place(buf, rumble(min(6.0, end - s.start + 0.5)), s.start, db(-14))
        if s.post is not None and getattr(s.post, "__name__", "") == "post" and "heartbeat" in str(s.post.__qualname__):
            place(buf, heartbeat_sfx(end - s.start, 80), s.start, db(-6))
    return buf


SLOTS = [(0.0, 79.2), (77.7, 129.0), (127.5, 210.0), (208.5, 276.0), (274.3, 363.0), (361.6, None)]


def build_music(N, total):
    buf = np.zeros((N, 2), np.float32)
    for k, (s, e) in enumerate(SLOTS):
        e = total if e is None else min(e, total)
        if s >= total:
            break
        p = os.path.join(ROOT, "assets", "score", f"cue_{k + 1}.wav")
        if not os.path.exists(p):
            p = p[:-4] + ".flac"
        g = -27.5 - lufs(p)
        clip = load(p, 0, e - s + 0.2)
        clip = clip[: int((e - s) * SR)]
        fade(clip, 2.0 if s > 0 else 0.3, 3.0 if e < total else 4.0)
        place(buf, clip, s, db(g))
    return buf


def main():
    voz, out, total = sys.argv[1], sys.argv[2], float(sys.argv[3])
    N = int(total * SR)
    v = load(voz)[:N]
    v = np.pad(v, ((0, N - len(v)), (0, 0)))
    # voz a ~ -16 LUFS antes de mezclar
    vg = -16.0 - lufs(voz)
    v *= db(vg)
    music = build_music(N, total)
    music = duck(music, v, -9.0, 0.08, 0.6) * db(1.5)
    sfx = build_sfx(N, total) * db(-11)
    mix = v + music + sfx
    tmp = out + ".raw.wav"
    for arr, name in ((mix, tmp), (music, out + ".music.wav"), (sfx, out + ".sfx.wav")):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_f32le", name],
                       input=arr.astype("<f4").tobytes(), check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:print_format=none",
                    "-ar", str(SR), "-c:a", "pcm_s16le", out], check=True)
    os.remove(tmp)
    print("mezcla:", out, "LUFS final", lufs(out), "| música", round(lufs(out + ".music.wav"), 1), "| sfx", round(lufs(out + ".sfx.wav"), 1))


if __name__ == "__main__":
    main()
