"""Reel #3 audio: original dark hip-hop bed (92 BPM, C minor) + client SFX library + party ambience + voice."""
import os, sys, math, subprocess
import numpy as np
import scipy.io.wavfile as wf
from synth3 import *
import edl
import reel3 as R

REPO_SFX = '/home/user/Claude/recursos/sfx'
def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
SFX = {k: load(f'{REPO_SFX}/cliente/{k}.mp3') for k in
       ['whoosh_corto', 'whoosh_largo', 'pop', 'click', 'cash_register', 'contador_ticks', 'impacto_bajo', 'riser', 'notificacion']}
AMB = {k: load(f'{REPO_SFX}/ambiente/{k}.mp3') for k in
       ['ambiente_fiesta_bar', 'ambiente_feria_risas', 'multitud_celebra', 'fuegos_artificiales_gente']}
HIT = dict(whoosh_corto=0.18, whoosh_largo=0.38, pop=0.20, click=0.11, cash_register=1.03, contador_ticks=0.08,
           impacto_bajo=0.16, riser=1.84, notificacion=0.23)
for k in SFX: SFX[k] = SFX[k] / (np.abs(SFX[k]).max() + 1e-9)

def put_st(buf, x, t, gain=1.0, length=None, fade=0.05):
    if length is not None:
        x = x[:, :T(length)].copy(); f = min(T(fade), x.shape[1])
        x[:, -f:] *= np.linspace(1, 0, f)
    i = T(t)
    if i >= buf.shape[1]: return
    j0 = max(0, -i); x = x[:, j0:]; i = max(i, 0)
    n = min(x.shape[1], buf.shape[1] - i)
    buf[:, i:i + n] += x[:, :n] * gain

def S(buf, name, t, gain=1.0, **kw):
    put_st(buf, SFX[name], t - HIT[name], gain, **kw)

T_ = R.T_

# ------------------------------------------------------------- music
CH = [(36, [60, 63, 67]), (32, [56, 60, 63]), (29, [53, 56, 60]), (31, [55, 59, 62])]   # Cm Ab Fm G
MEL = [(0, 79, .75), (1, 75, .5), (1.5, 72, .5), (2.5, 74, 1.0), (4, 79, .5), (4.5, 77, .5), (5, 75, .75), (6, 72, 1.5)]

def bell(freq, dur=1.2):
    n = T(dur); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * freq * tt) * env_exp(n, 0.5) + 0.45 * np.sin(2 * np.pi * freq * 2.76 * tt) * env_exp(n, 0.12)
         + 0.2 * np.sin(2 * np.pi * freq * 5.4 * tt) * env_exp(n, 0.04))
    x[:40] *= np.linspace(0, 1, 40); return x

def sub808(freq, dur):
    n = T(dur); tt = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-tt / 0.03))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.7)
    x *= np.minimum(1, (n - np.arange(n)) / 800)
    return np.tanh(x * 2.2) * 0.8

def snare():
    n = T(0.25)
    x = filt(noise(n), 'bp', (1500, 7000)) * env_exp(n, 0.05) * 0.8
    tt = np.arange(n) / SR
    x += np.sin(2 * np.pi * 190 * tt) * env_exp(n, 0.04) * 0.6
    return x

def music():
    drums = np.zeros((2, N)); bass = np.zeros((2, N)); keys = np.zeros((2, N)); pad = np.zeros((2, N))
    K = kick(0.35); SN = snare(); CL = clap()
    t_drop0, t_drop1 = T_(6) - 0.16, T_(6)
    end = R.DUR - 0.6
    side = np.ones(N)
    b = 0
    while b * BAR < end:
        t0 = b * BAR; root, ch = CH[b % 4]
        chart = R.CH0 <= t0 < R.BR1
        steps = [(0, 1.0), (1.5, 0.8), (2.75, 0.7)]
        for s, g in steps:
            tb = t0 + s * BEAT
            if tb >= end or t_drop0 <= tb < t_drop1: continue
            add(drums, K, tb, 0.9 * g)
            add(bass, sub808(mtof(root), (BEAT * (1.5 if s == 0 else 1.2))), tb, 0.55 * g)
            i = T(tb); n = min(T(0.25), N - i)
            if n > 0: side[i:i + n] = np.minimum(side[i:i + n], 1 - 0.6 * np.exp(-np.arange(n) / (0.08 * SR)))
        for s in (1, 3):
            tb = t0 + s * BEAT
            if tb < end and not (t_drop0 <= tb < t_drop1):
                add(drums, SN, tb, 0.45); add(drums, CL, tb + 0.01, 0.3)
        for k8 in range(8):
            tb = t0 + k8 * BEAT / 2
            if tb >= end or t_drop0 <= tb < t_drop1: continue
            add(drums, hat(open_=(k8 == 7 and chart)), tb, 0.16 if k8 % 2 == 0 else 0.11, 0.3)
        if b % 2 == 1:   # 16th roll at end of every second bar
            for r in range(4): add(drums, hat(), t0 + 3.5 * BEAT + r * BEAT / 8, 0.08 + 0.02 * r, 0.3)
        n = T(BAR + 0.1)
        pd = sum(saw(mtof(m - 12), n, (-0.004, 0.0, 0.005)) for m in ch)
        pd = filt(pd, 'lowpass', 1100 if chart else 750) * np.minimum(1, np.arange(n) / (0.15 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.15 * SR))
        add(pad, pd, t0, 0.04)
        if b % 2 == 0:
            for off, m, ln in MEL:
                tb = t0 + off * BEAT
                if tb < end: add(keys, bell(mtof(m), ln * BEAT + 0.6), tb, 0.07, 0.2)
        b += 1
    # final hit
    for m in (36, 48, 60, 63, 67):
        add(keys, bell(mtof(m + 12 if m > 40 else m + 24), 2.0), end, 0.06, rng.uniform(-0.4, 0.4))
    add(bass, sub808(mtof(36), 1.6), end, 0.6); add(drums, K, end, 0.9)
    for tr in (bass, pad, keys): tr *= side
    mix = drums * 0.85 + bass + keys + pad
    # dropout before the URL
    a, z = T(t_drop0), T(t_drop1)
    mix[:, a:z] *= np.linspace(1, 0, z - a) ** 3
    mix = filt_st(mix, 'highpass', 28)
    f0 = T(R.DUR - 0.5); mix[:, f0:] *= np.linspace(1, 0, N - f0)
    return mix

# ------------------------------------------------------------- SFX timeline (client library)
def sfx():
    B = np.zeros((2, N))
    S(B, 'whoosh_corto', T_(4), 0.5)
    for k in range(3): S(B, 'pop', T_(3) + 0.10 * k + 0.12, 0.45)
    S(B, 'impacto_bajo', T_(6), 0.7); S(B, 'whoosh_corto', T_(6) + 0.02, 0.45)
    for k in range(3): S(B, 'pop', T_(8) + 0.30 + 0.16 * k + 0.14, 0.5)
    S(B, 'impacto_bajo', T_(9), 0.6)
    S(B, 'whoosh_largo', R.PH0, 0.55); S(B, 'whoosh_corto', T_(12), 0.4)
    S(B, 'whoosh_largo', R.PH1, 0.45)
    S(B, 'notificacion', T_(15), 0.45)
    S(B, 'impacto_bajo', T_(17), 0.6)
    S(B, 'click', T_(19), 0.6); S(B, 'click', T_(21), 0.6); S(B, 'whoosh_corto', T_(20), 0.3)
    S(B, 'impacto_bajo', T_(24), 0.6); S(B, 'cash_register', T_(24) + 0.12, 0.55)
    S(B, 'click', T_(26), 0.6); S(B, 'click', T_(29), 0.6)
    S(B, 'notificacion', T_(33), 0.45)
    S(B, 'whoosh_corto', T_(42), 0.45); S(B, 'click', T_(42) + 0.02, 0.5)
    # chart
    S(B, 'riser', R.CH0, 0.45); S(B, 'impacto_bajo', R.CH0 + 0.02, 0.75); S(B, 'whoosh_largo', R.CH0, 0.5)
    for wi in (45, 50, 57):
        S(B, 'whoosh_corto', T_(wi) - 0.05, 0.45); S(B, 'pop', T_(wi) + 0.2, 0.4)
    put_st(B, AMB['ambiente_fiesta_bar'][:, T(5):], R.CH0, 0.10, length=R.BR1 - R.CH0, fade=0.4)
    put_st(B, AMB['fuegos_artificiales_gente'], T_(45) - 1.6, 0.22, length=3.6, fade=0.5)
    put_st(B, AMB['multitud_celebra'], T_(50) - 0.5, 0.25, length=2.4, fade=0.5)
    put_st(B, AMB['ambiente_feria_risas'][:, T(2):], T_(57) - 0.2, 0.25, length=R.BR1 - T_(57) + 0.2, fade=0.5)
    # b-roll
    S(B, 'whoosh_largo', R.BR0, 0.5); S(B, 'whoosh_corto', T_(63) - 0.05, 0.4); S(B, 'whoosh_corto', T_(64) - 0.05, 0.35)
    S(B, 'whoosh_largo', R.BR1, 0.45)
    # groups
    S(B, 'impacto_bajo', T_(68), 0.55); S(B, 'whoosh_corto', T_(68), 0.35)
    put_st(B, SFX['contador_ticks'], T_(72) - 0.12, 0.45, length=0.65, fade=0.08)
    S(B, 'whoosh_corto', T_(73), 0.4)
    S(B, 'whoosh_corto', T_(78), 0.4); S(B, 'pop', T_(78) + 0.1, 0.4)
    # CTA
    S(B, 'whoosh_corto', T_(85) + 0.1, 0.45)
    for k in range(7): put_st(B, SFX['click'][:, T(0.06):T(0.2)], T_(89) + k * (T_(90) + 0.35 - T_(89)) / 7, 0.3)
    S(B, 'riser', T_(90), 0.4); S(B, 'impacto_bajo', T_(90), 0.7)
    t_click = T_(92) + 0.05
    S(B, 'click', t_click, 0.7); S(B, 'notificacion', t_click + 0.15, 0.5)
    # light swish on every other jump cut that has nothing else around it
    busy = [T_(i) for i in (4, 6, 9, 17, 24, 42, 68, 73, 78, 90)] + [R.PH0, R.PH1, R.CH0, R.BR0, R.BR1]
    for tc in edl.CUTS[::2]:
        if min(abs(tc - b_) for b_ in busy) > 0.4 and not (R.CH0 <= tc < R.BR1):
            S(B, 'whoosh_corto', tc, 0.22)
    return B

# ------------------------------------------------------------- voice (edited)
def voice():
    sr, a = wf.read(f'{ROOT}/raw/voice_full.wav'); a = a.astype(np.float64) / 32768
    v = np.zeros(N); xf = T(0.012)
    for (s0, s1), o in zip(edl.SEGS, edl.OUT0):
        seg = a[T(s0):T(s1)].copy()
        seg[:xf] *= np.linspace(0, 1, xf); seg[-xf:] *= np.linspace(1, 0, xf)
        i = T(o); n = min(len(seg), N - i); v[i:i + n] += seg[:n]
    v = filt(v, 'highpass', 90)
    v = v + 0.2 * filt(v, 'bp', (2500, 6000))
    k = T(0.4); env = np.sqrt(np.convolve(v ** 2, np.ones(k) / k, 'same'))
    ref = np.percentile(env[env > env.max() * 0.05], 70)
    g = np.convolve(np.clip(ref / np.maximum(env, ref * 0.15), 0.7, 2.2), np.ones(T(0.3)) / T(0.3), 'same')
    v = np.tanh(v * g / (np.abs(v * g).max() * 0.8)) * 0.9
    return v

if __name__ == '__main__':
    m = music(); s = sfx(); v = voice()
    k = T(0.05); ev = np.sqrt(np.convolve(v ** 2, np.ones(k) / k, 'same')); ev /= ev.max() + 1e-9
    act = np.convolve(np.clip((ev - 0.04) / 0.1, 0, 1), np.ones(T(0.25)) / T(0.25), 'same')
    duck = 1 - 0.5 * np.clip(act, 0, 1)
    m /= np.abs(m).max() + 1e-9; s /= np.abs(s).max() + 1e-9
    mix = np.stack([v, v]) * 0.82 + m * 0.30 * duck + s * 0.50
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.95
    wf.write(f'{ROOT}/work/mix.wav', SR, (mix.T * 32767).astype(np.int16))
    wf.write(f'{ROOT}/work/music.wav', SR, (m.T * 0.9 * 32767).astype(np.int16))
    print('ok', R.DUR)
