"""Música original sintetizada nota a nota (sin samples ni pistas de terceros: no puede recibir reclamos).

python3 music.py n1|n2 plan.json out.wav
"""
import json
import sys

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, '/home/user/notas/edit')
from score import (SR, bass, bell, drone, hat, kick, lay_pad, pad, piano, place, pluck, reverb, rng,  # noqa: E402
                   timp, tremolo, lp, hp)


def boom(amp=0.6):
    """Golpe grave de impacto para titulares y cifras."""
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 32 + 70 * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    s += lp(rng.normal(0, 1, n), 900) * np.exp(-t * 14) * 0.35
    return np.stack([s, s], 1) * amp


def riser(dur=1.2, amp=0.08):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = hp(rng.normal(0, 1, n), 1500) * (t / dur) ** 2.5
    return np.stack([s, s * 0.9], 1) * amp


def env_section(buf, a, b, gain, fade=1.5):
    """Multiplica buf entre a y b por gain con rampas suaves."""
    n = len(buf)
    g = np.ones(n)
    ia, ib = int(a * SR), int(b * SR)
    f = int(fade * SR)
    g[ia:ib] = gain
    ramp = np.linspace(1, gain, f)
    g[max(0, ia - f // 2):max(0, ia - f // 2) + len(ramp)] = ramp[:len(g[max(0, ia - f // 2):max(0, ia - f // 2) + len(ramp)])]
    return buf * g[:, None]


def eerie(m, dur, amp=0.03, vib=0.18):
    """Tono agudo y frío (seno con vibrato lento): suspenso sin melodía."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 440.0 * 2 ** ((m - 69) / 12) * (1 + 0.004 * np.sin(2 * np.pi * vib * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    e = np.minimum(1, t / 3.0) * np.clip((dur - t) / 3.0, 0, 1)
    return np.stack([s * e, s * e * 0.85], 1) * amp


def cue_n1(plan):
    """Suspenso sobrio en re menor: drone grave, latido suave, cuerdas oscuras en trémolo y golpes graves
    en las cifras. Sin arpegios, sin platillos ni nada que suene ligero."""
    total = plan['end_body'] + 0.6
    hits = plan['hits']
    sec = dict(plan['sections'])
    B0, Q = sec['body'], sec['question']
    beat = 60 / 76
    bar = beat * 4
    N = int((total + 4) * SR)
    music = np.zeros((N, 2))
    place(music, drone(26, total + 2, 0.15), 0)
    place(music, drone(33, total + 2, 0.06), 0)
    # acordes oscuros con segunda menor (Dm(add b2) - Bb - Gm - A sus)
    prog = [[50, 51, 57], [46, 50, 53], [43, 46, 50], [45, 50, 52]]
    lay = np.zeros_like(music)
    lay_pad(lay, total, prog, bar * 2, bright=520, amp=0.09)
    music += lay
    # latido: dos golpes graves por compás, filtrados
    perc = np.zeros_like(music)
    t = B0
    while t < Q - 0.2:
        place(perc, kick(0.20), t)
        place(perc, kick(0.11), t + 0.21)
        t += bar / 2
    music += lp(perc, 180)
    # tono agudo frío en dos tramos
    place(music, eerie(81, 30.0, 0.018), B0 + 18)
    place(music, eerie(80, 34.0, 0.016), B0 + 58)
    # cuerdas graves en trémolo desde los gráficos
    tre = np.zeros_like(music)
    tt, n = B0 + 18, 0
    while tt < Q - 1:
        ch = prog[n % 4]
        place(tre, tremolo([m for m in ch], bar * 2 + 1.5, 5.5, 0.045), tt)
        tt += bar * 2
        n += 1
    music += lp(tre, 1400)
    # notas graves de piano, muy espaciadas
    pn = np.zeros_like(music)
    tt = B0 + 2
    for k in range(200):
        if tt > Q - 1:
            break
        place(pn, piano([38, 41, 37, 38][k % 4], 4.5, 0.05, -0.15), tt)
        tt += bar * 2
    music += pn
    # golpes graves en titulares y cifras (sin timbal brillante)
    fx = np.zeros_like(music)
    for h in hits:
        if h > 0.5:
            place(fx, riser(1.2, 0.025), h - 1.2)
        place(fx, boom(0.30), h)
    music += fx
    # pregunta final: solo drone, pad y tres notas de piano
    pq = np.zeros_like(music)
    for j, m in enumerate([62, 61, 57]):
        place(pq, piano(m, 4.0, 0.045, -0.2 + 0.1 * j), Q + 0.4 + j * 1.8)
    music += pq
    music = reverb(music, 2.6, 0.25)
    g = np.ones(len(music))

    def ramp(a, b, g0, g1):
        ia, ib = int(a * SR), int(b * SR)
        g[ia:ib] = np.linspace(g0, g1, ib - ia)
    ramp(Q - 0.8, Q + 0.4, 1.0, 0.8)
    g[int((Q + 0.4) * SR):] = 0.8
    ramp(total - 1.2, total, 0.8, 0.0)
    g[int(total * SR):] = 0
    music *= g[:, None]
    return music[:int(total * SR)]


def cue_n2(plan):
    """Fondo informativo sobrio (si menor / re mayor, 84 BPM): pads cálidos, pulso grave suave y piano espaciado.
    Sin arpegios ni platillos para no restarle seriedad."""
    total = plan['end_body'] + 0.6
    hits = plan.get('hits', [])
    beat = 60 / 84
    bar = beat * 4
    N = int((total + 4) * SR)
    music = np.zeros((N, 2))
    prog = [[47, 50, 54, 57], [43, 47, 50, 54], [50, 54, 57, 61], [45, 49, 52, 57]]  # Bm7 Gmaj7 Dmaj7 A
    lay = np.zeros_like(music)
    lay_pad(lay, total, prog, bar * 2, bright=1000, amp=0.08)
    music += lay
    place(music, drone(35, total + 2, 0.07), 0)
    perc = np.zeros_like(music)
    t, i = 0.0, 0
    while t < total - 1:
        ch = prog[int(t // (bar * 2)) % 4]
        place(perc, kick(0.14), t)
        place(perc, bass(ch[0] - 12, beat * 1.8, 0.16), t)
        if i % 2 == 1:
            place(perc, kick(0.08), t + beat * 2)
        t += bar
        i += 1
    music += lp(perc, 220)
    pn = np.zeros_like(music)
    t, k = 1.0, 0
    while t < total - 2:
        ch = prog[int(t // (bar * 2)) % 4]
        place(pn, piano(ch[1 + k % 3] + 12, 3.5, 0.04, -0.2 + 0.15 * (k % 3)), t)
        t += bar
        k += 1
    music += pn
    for h in hits:
        place(music, boom(0.18), h)
    music = reverb(music, 2.2, 0.22)
    g = np.ones(len(music))
    ia, ib = int((total - 1.5) * SR), int(total * SR)
    g[ia:ib] = np.linspace(1, 0, ib - ia)
    g[ib:] = 0
    music *= g[:, None]
    return music[:int(total * SR)]


if __name__ == '__main__':
    which, plan_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    plan = json.load(open(plan_path))
    m = {'n1': cue_n1, 'n2': cue_n2}[which](plan)
    m = m / max(1e-6, np.abs(m).max()) * 0.89
    wavfile.write(out, SR, (m * 32767).astype(np.int16))
    print(out, len(m) / SR)
