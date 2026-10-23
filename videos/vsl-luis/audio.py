#!/usr/bin/env python3
"""Build the VSL soundtrack: cleaned voice + ducked epic music + synthesized SFX.

Usage:
    python3 audio.py --work <dir> --music <track.mp3> --music-start 9.0 --out mix.wav

<work> holds voice_raw.wav (the edited voice). SFX are synthesized here so no third-party
samples are needed; the music must be a track you are allowed to use (CC0 by default).
"""
import argparse
import os
import subprocess
import wave

import numpy as np

SR = 48000
TOTAL = 34.37  # edit length (32.77 s) + 1.6 s outro, same as render.py
rng = np.random.default_rng(3)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def lowpass(x, cutoff):
    """One-pole lowpass; cutoff may be an array (time-varying)."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 380
    return 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.025)


def whoosh(dur=0.45, peak=0.55):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    shape = np.sin(np.pi * u ** 0.8) ** 2
    noise = rng.standard_normal(n)
    y = lowpass(noise, 300 + 5200 * shape)
    y -= lowpass(y, 180)
    return peak * y / (np.abs(y).max() + 1e-9) * shape


def riser(dur=1.2):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    noise = lowpass(rng.standard_normal(n), 200 + 9000 * u ** 2)
    tone = np.sin(2 * np.pi * np.cumsum(180 + 900 * u ** 2) / SR)
    y = (0.6 * noise / np.abs(noise).max() + 0.25 * tone) * u ** 2.2
    return 0.7 * y


def boom(dur=1.6, f0=85, f1=38, level=0.95):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.45)
    click = lowpass(rng.standard_normal(n), 1800) * env_exp(n, 0.03)
    y = np.tanh(1.6 * (body + 0.5 * click))
    return level * y / np.abs(y).max()


def hit():
    return boom(0.5, 140, 60, 0.6)


def buzz(dur=0.36):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * 98 * t)) + np.sign(np.sin(2 * np.pi * 103 * t))
    y = lowpass(sq, 1400) * np.minimum(1, (dur - t) / 0.05) * np.minimum(1, t / 0.01)
    return 0.22 * y / np.abs(y).max()


def shimmer(dur=1.1):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * env_exp(n, 0.35 + 0.1 * k)
            for k, f in enumerate([1568, 2093, 2637, 3136, 4186]))
    y *= 1 + 0.3 * np.sin(2 * np.pi * 9 * t)
    return 0.12 * y / np.abs(y).max()


def tick():
    n = int(0.012 * SR)
    return 0.07 * np.sin(2 * np.pi * 2400 * np.arange(n) / SR) * env_exp(n, 0.003)


EVENTS = [
    # time (edit timeline), sound, gain
    (2.62, pop, 1.0), (3.84, pop, 1.0), (8.78, pop, 1.0), (11.76, pop, 1.0), (14.50, pop, 1.0),
    (24.55, pop, 1.0), (26.47, pop, 1.0), (29.21, pop, 1.0),
    (5.34, whoosh, 0.8), (7.64, lambda: whoosh(0.35), 0.45), (17.22, whoosh, 1.0),
    (17.98, lambda: whoosh(0.35), 0.5), (20.88, lambda: whoosh(0.4), 0.8), (24.44, lambda: whoosh(0.4), 0.8),
    (32.74, whoosh, 0.7),
    (6.98, buzz, 1.0), (18.73, buzz, 1.0),
    (19.97, riser, 1.0), (21.17, boom, 1.0), (21.25, shimmer, 1.0), (23.09, shimmer, 0.9),
    (24.55, hit, 0.7), (25.25, hit, 1.0), (11.76, hit, 0.45), (32.07, boom, 0.9),
]


def sfx_track():
    n = int(TOTAL * SR) + SR
    out = np.zeros(n)
    events = list(EVENTS)
    t = 21.32
    while t < 23.05:  # counter ticks, slowing down with the count
        events.append((t, tick, 1.0))
        t += 0.045 + 0.09 * ((t - 21.32) / 1.73) ** 2
    for t0, fn, g in events:
        y = fn() * g
        i = int(t0 * SR)
        out[i:i + len(y)] += y[: n - i]
    return out[: int(TOTAL * SR)]


def write_wav(path, mono):
    st = np.repeat(np.clip(mono, -1, 1)[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--music-start", type=float, default=9.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sfx = os.path.join(args.work, "sfx.wav")
    write_wav(sfx, sfx_track())
    voice = os.path.join(args.work, "voice_raw.wav")
    fade_out = TOTAL - 1.4
    graph = (
        # voice: rumble cut, gentle denoise, presence, leveling
        "[0:a]highpass=f=85,afftdn=nr=10:nf=-32,equalizer=f=3200:t=q:w=1.2:g=2.5,"
        "equalizer=f=250:t=q:w=1:g=-2,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=3,"
        f"apad=whole_dur={TOTAL},asplit=2[v][key];"
        # music: from the build-up, ducked under the voice, softer while the proof cards build tension
        f"[1:a]atrim=start={args.music_start}:duration={TOTAL},asetpts=PTS-STARTPTS,"
        "volume=0.30,volume='if(between(t,17.2,21.15),0.75,1)':eval=frame,"
        f"afade=t=in:st=0:d=0.4,afade=t=out:st={fade_out:.2f}:d=1.4[m];"
        "[m][key]sidechaincompress=threshold=0.035:ratio=5:attack=15:release=320:makeup=1[md];"
        "[2:a]volume=0.9[s];"
        "[v][md][s]amix=inputs=3:normalize=0:duration=first,"
        "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[out]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-i", args.music, "-i", sfx,
                    "-filter_complex", graph, "-map", "[out]", "-ac", "2", "-ar", "48000", args.out], check=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
