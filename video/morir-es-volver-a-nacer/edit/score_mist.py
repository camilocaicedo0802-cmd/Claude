"""Banda sonora original del episodio (sintetizada nota a nota con score.py; sin muestras ni música de terceros).
uso: python score_mist.py OUT_DIR L1 L2 L3 L4 L5 L6  -> cue_1.wav .. cue_6.wav"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S  # noqa: E402
from score import SR, bell, chords_over, drone, hat, kick, lay_pad, piano, place, tremolo  # noqa: E402

rng = np.random.default_rng(11)


def cue_hook(dur):  # muerte y túnel: dron grave, pulso lento, campanas lejanas, swell hacia la luz
    buf = S.cue_dark(dur)
    for t in np.arange(10, dur - 4, 9.0):
        place(buf, piano(rng.choice([57, 60, 64, 65]), 5.0, 0.04, rng.uniform(-0.5, 0.5)), t)
    return buf


def cue_womb(dur):  # el vientre: colchón cálido, latido de 72 bpm, campanas suaves
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    place(buf, drone(38, dur + 3, 0.10), 0)
    lay_pad(buf, dur, [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 61]], 7.0, bright=900, amp=0.09)
    for t in np.arange(0.5, dur - 1, 60 / 72):
        place(buf, kick(0.26), t)
        place(buf, kick(0.15), t + 0.22)
    for t in np.arange(5, dur - 3, 6.5):
        place(buf, bell(rng.choice([74, 77, 81, 79]), 5, 0.035, rng.uniform(-0.7, 0.7)), t + rng.uniform(0, 1.5))
    return buf


def cue_mystery(dur):  # dos túneles: dron, pad muy oscuro, notas graves de piano, campanas raras
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    place(buf, drone(26, dur + 3, 0.15), 0)
    prog = [[50, 57, 62, 65], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 57, 61]]
    lay_pad(buf, dur, prog, 9.0, bright=600, amp=0.10)
    for i, (t, ch) in enumerate(chords_over(dur, prog, 9.0)):
        place(buf, piano(ch[0] - 12, 7.0, 0.07), t)
        if i % 2 == 1:
            place(buf, piano(ch[2], 5.0, 0.035, 0.2), t + 4.5)
    for t in np.arange(12, dur - 4, 17.0):
        place(buf, bell(rng.choice([69, 74, 77]), 6, 0.03, rng.uniform(-0.7, 0.7)), t)
    return buf


def cue_clock(dur):  # el tiempo: tic-tac suave, trémolo menor y pulso grave, creciendo
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    place(buf, drone(33, dur + 3, 0.14), 0)
    prog = [[45, 52, 57, 60], [44, 51, 56, 60], [41, 48, 53, 57], [40, 47, 52, 56]]
    lay_pad(buf, dur, prog, 7.0, bright=700, amp=0.07)
    for t, ch in chords_over(dur, prog, 7.0):
        grow = min(1.0, 0.35 + t / dur)
        place(buf, tremolo([m + 12 for m in ch[:3]], 7.5, 5.5, 0.05 * grow), t)
    beat = 60 / 90
    for k, t in enumerate(np.arange(0.5, dur - 1, beat)):
        place(buf, hat(0.022, 0.025, 0.35 if k % 2 else -0.35), t)
        if k % 4 == 0:
            place(buf, kick(0.22), t)
    return buf


def cue_final(dur):  # clímax y final: acordes menores lentos, piano grave y melodía escasa
    buf = S.cue_sad(dur)
    place(buf, drone(33, dur + 3, 0.08), 0)
    return buf


CUES = [cue_hook, cue_womb, cue_mystery, S.cue_tension, cue_clock, cue_final]


def main():
    out = sys.argv[1]
    lens = [float(x) for x in sys.argv[2:]]
    os.makedirs(out, exist_ok=True)
    for i, (fn, L) in enumerate(zip(CUES, lens)):
        x = fn(L + 4.0)
        x = S.reverb(x, 2.6, 0.32)
        x = S.lp(S.hp(x, 30), 5500)[: int((L + 4.0) * SR)]
        x /= np.abs(x).max() + 1e-9
        x *= 0.7
        p = os.path.join(out, f"cue_{i + 1}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", p],
                       input=x.astype("<f4").tobytes(), check=True)
        print(p, round(L + 4, 1))


if __name__ == "__main__":
    main()
