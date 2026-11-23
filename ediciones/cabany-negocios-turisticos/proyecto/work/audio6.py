"""Business reel audio: Gemini TTS male voice + original upbeat bed (112 BPM, G major) + client SFX library."""
import os, sys, math, subprocess
import numpy as np
import scipy.io.wavfile as wf
from scipy import signal
import reel6 as R

ROOT = R.ROOT
SR = 44100
DUR = R.DUR
N = int(SR * DUR)
rng = np.random.default_rng(5)
def T(t): return int(round(t * SR))
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def noise(n): return rng.standard_normal(n)
def filt(x, kind, f, order=2):
    if kind == 'bp': s = signal.butter(order, [f[0] / (SR / 2), f[1] / (SR / 2)], 'bandpass', output='sos')
    else: s = signal.butter(order, f / (SR / 2), kind, output='sos')
    return signal.sosfilt(s, x)
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(buf, x, t, gain=1.0, pan=0.0):
    i = T(t)
    if i >= buf.shape[1] or i + len(x) <= 0: return
    j0 = max(0, -i); x = x[j0:]; i = max(i, 0)
    n = min(len(x), buf.shape[1] - i)
    l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
    buf[0, i:i + n] += x[:n] * gain * l * 1.414; buf[1, i:i + n] += x[:n] * gain * r * 1.414

# ------------------------------------------------------------- client SFX
REPO_SFX = '/home/user/Claude/recursos/sfx'
def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
    return a / (np.abs(a).max() + 1e-9)
SFX = {k: load(f'{REPO_SFX}/cliente/{k}.mp3') for k in
       ['whoosh_corto', 'whoosh_largo', 'pop', 'click', 'cash_register', 'contador_ticks', 'impacto_bajo', 'riser', 'notificacion']}
AMB = {'multitud': load(f'{REPO_SFX}/ambiente/multitud_celebra.mp3')}
HIT = dict(whoosh_corto=0.18, whoosh_largo=0.38, pop=0.20, click=0.11, cash_register=1.03, contador_ticks=0.08,
           impacto_bajo=0.16, riser=1.84, notificacion=0.23)
def put_st(buf, x, t, gain=1.0, length=None, fade=0.05):
    if length is not None:
        x = x[:, :T(length)].copy(); f = min(T(fade), x.shape[1]); x[:, -f:] *= np.linspace(1, 0, f)
    i = T(t)
    if i >= buf.shape[1]: return
    j0 = max(0, -i); x = x[:, j0:]; i = max(i, 0)
    n = min(x.shape[1], buf.shape[1] - i); buf[:, i:i + n] += x[:, :n] * gain
def S(buf, name, t, gain=1.0, **kw): put_st(buf, SFX[name], t - HIT[name], gain, **kw)
def key_click(buf, t, g=0.22): put_st(buf, SFX['click'][:, T(0.07):T(0.17)], t, g * rng.uniform(0.8, 1.1))

T_ = R.T_

def sfx():
    B = np.zeros((2, N))
    # hook: one punchy cut per business type
    for k, tc in enumerate([0.0, T_(5), T_(8), T_(10)]):
        if tc > 0: S(B, 'whoosh_corto', tc, 0.5)
        S(B, 'pop', tc + 0.06, 0.38)
    S(B, 'impacto_bajo', T_(2), 0.4); S(B, 'impacto_bajo', T_(6), 0.35); S(B, 'impacto_bajo', T_(13), 0.4)
    # intro
    S(B, 'whoosh_largo', 5.80, 0.45); S(B, 'riser', T_(22) - 0.02, 0.3); S(B, 'impacto_bajo', T_(22), 0.55)
    S(B, 'whoosh_corto', T_(24), 0.4)
    for k in range(3): S(B, 'notificacion', T_(28) + k * 0.5, 0.3)
    S(B, 'pop', T_(32), 0.4)
    # how it works
    S(B, 'whoosh_largo', 12.42, 0.4)
    for k in range(6): S(B, 'pop', T_(42) - 0.1 + 0.08 * k + 0.05, 0.34)
    # step headers
    for t0 in (14.72, 20.80, 28.90, 34.84, 39.70, 45.16):
        S(B, 'whoosh_largo', t0, 0.42); S(B, 'impacto_bajo', t0 + 0.08, 0.36); S(B, 'pop', t0 + 0.12, 0.33)
    # step 1
    S(B, 'pop', T_(47), 0.4); S(B, 'cash_register', T_(47) + 0.1, 0.25)
    for k in range(16): key_click(B, T_(50) - 0.1 + k * (T_(51) + 0.6 - T_(50)) / 16)
    S(B, 'whoosh_corto', 18.4, 0.4); S(B, 'click', T_(53), 0.75)
    S(B, 'whoosh_corto', 19.3, 0.38)
    for a_, b_, n in [(19.30, 19.55, 9), (19.55, 19.85, 12), (19.85, 20.05, 7), (20.05, 20.30, 8)]:
        for k in range(n): key_click(B, a_ + k * (b_ - a_) / n, 0.16)
    S(B, 'click', 20.42, 0.7); S(B, 'notificacion', 20.55, 0.32)
    # step 2
    for k, tk in [(1, T_(70)), (2, T_(71)), (3, T_(73))]: S(B, 'click', tk + 0.05, 0.55); S(B, 'pop', tk + 0.07, 0.25)
    S(B, 'pop', T_(75), 0.4); S(B, 'click', 28.45, 0.6)
    # step 3: typing
    from reel6 import DW
    for a_, d, n in DW:
        for k in range(min(n, 14)): key_click(B, a_ + k * d / min(n, 14), 0.16)
    for ts in (T_(86), T_(91), T_(93), T_(96)): S(B, 'whoosh_corto', ts - 0.05, 0.22); S(B, 'pop', ts - 0.02, 0.25)
    # step 4: uploads
    from reel6 import UP
    for a_, d in UP:
        S(B, 'whoosh_corto', a_, 0.3); put_st(B, SFX['contador_ticks'], a_ + 0.02, 0.22, length=d, fade=0.06)
        S(B, 'notificacion', a_ + d, 0.32); S(B, 'pop', a_ + 0.02, 0.3)
    # step 5
    for x in (39.95, 40.15, 40.35, 40.55): S(B, 'pop', x, 0.3)
    S(B, 'click', T_(119) + 0.2, 0.75); S(B, 'whoosh_largo', T_(119) + 0.35, 0.4)
    S(B, 'whoosh_corto', T_(120), 0.35); S(B, 'pop', T_(122), 0.35)
    S(B, 'riser', T_(129), 0.35); S(B, 'impacto_bajo', T_(129), 0.5); S(B, 'notificacion', T_(129) + 0.05, 0.45)
    put_st(B, AMB['multitud'], T_(129) - 0.5, 0.18, length=2.2, fade=0.5)
    # step 6
    S(B, 'impacto_bajo', T_(134) + 0.12, 0.5); S(B, 'whoosh_corto', T_(134), 0.4)
    S(B, 'whoosh_largo', T_(137), 0.38)
    put_st(B, SFX['contador_ticks'], T_(137) + 0.1, 0.28, length=1.6, fade=0.2)
    S(B, 'cash_register', T_(139) + 0.9, 0.3)
    S(B, 'whoosh_corto', T_(149) - 0.1, 0.35); S(B, 'pop', T_(149), 0.35)
    for ts, *_ in [(T_(155),), (T_(157),), (T_(160),)]: S(B, 'pop', ts, 0.36)
    S(B, 'notificacion', T_(161), 0.3)
    # CTA + end
    S(B, 'whoosh_largo', 55.20, 0.42); S(B, 'impacto_bajo', T_(167), 0.45)
    for k in range(16): key_click(B, T_(170) - 0.1 + k * 0.9 / 16, 0.2)
    S(B, 'click', 57.45, 0.6)
    S(B, 'riser', T_(172), 0.35); S(B, 'impacto_bajo', T_(172) + 0.02, 0.6)
    S(B, 'pop', T_(177) + 0.2, 0.4); S(B, 'notificacion', T_(177) + 0.22, 0.3)
    return B

# ------------------------------------------------------------- music bed
BEAT = 60 / 112; BAR = 4 * BEAT
CH = [(43, [55, 59, 62, 66]), (40, [52, 55, 59, 62]), (36, [48, 52, 55, 59]), (38, [50, 54, 57, 60])]   # Gmaj7 Em7 Cmaj7 D7
def kick():
    n = T(0.4); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * np.cumsum(50 + 100 * np.exp(-tt / 0.03)) / SR) * env_exp(n, 0.15)
    return np.tanh(x * 1.5)
def snap():
    n = T(0.18); return filt(noise(n), 'bp', (1800, 6000)) * env_exp(n, 0.035)
def hat(op=False):
    n = T(0.2 if op else 0.05); return filt(noise(n), 'highpass', 8000) * env_exp(n, 0.05 if op else 0.01)
def pluck(f, d=0.5):
    n = T(d); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * 2 * f * tt) * env_exp(n, 0.08) + 0.2 * np.sin(2 * np.pi * 3 * f * tt) * env_exp(n, 0.04)) * env_exp(n, 0.22)
    x[:40] *= np.linspace(0, 1, 40); return x
def rhodes(f, d):
    n = T(d); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt) * env_exp(n, 0.4)) * env_exp(n, 1.2)
    x *= np.minimum(1, np.arange(n) / 300) * np.minimum(1, (n - np.arange(n)) / 1500); return x
def bassn(f, d):
    n = T(d); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt)
    return np.tanh(x * np.minimum(1, np.arange(n) / 150) * np.minimum(1, (n - np.arange(n)) / 800) * 1.3)

def music():
    dr = np.zeros((2, N)); bs = np.zeros((2, N)); ky = np.zeros((2, N)); pl = np.zeros((2, N))
    K = kick(); SN = snap(); side = np.ones(N)
    end = DUR - 1.0
    b = 0
    while b * BAR < end:
        t0 = b * BAR; root, ch = CH[b % 4]
        intro = t0 < 3.5
        soft = False
        for k in range(4):
            tb = t0 + k * BEAT
            if tb >= end: break
            if not intro and not soft:
                add(dr, K, tb, 0.85)
                i = T(tb); n = min(T(0.22), N - i); side[i:i + n] = np.minimum(side[i:i + n], 1 - 0.55 * np.exp(-np.arange(n) / (0.07 * SR)))
                if k in (1, 3): add(dr, SN, tb, 0.42, 0.1)
            for h in range(2):
                add(dr, hat(op=(h == 1 and k == 3)), tb + h * BEAT / 2, 0.14 if not intro else 0.08, 0.3)
        for k8 in (0, 1.5, 2, 3, 3.5):
            tb = t0 + k8 * BEAT
            if tb < end and not intro: add(bs, bassn(mtof(root - 12 + (7 if k8 == 3.5 else 0)), BEAT * 0.45), tb, 0.45)
        for m in ch: add(ky, rhodes(mtof(m), BAR + 0.2), t0, 0.05, rng.uniform(-0.3, 0.3))
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[3] + 12, ch[2] + 24]
        for k8, m in enumerate(arp):
            tb = t0 + k8 * BEAT / 2
            if tb < end and not soft: add(pl, pluck(mtof(m), 0.4), tb, 0.06, 0.35 if k8 % 2 else -0.35)
        b += 1
    for m in (43, 55, 59, 62, 66, 71):
        add(ky, rhodes(mtof(m), 2.2), end, 0.07)
    add(dr, K, end, 0.8)
    for tr in (bs, ky, pl): tr *= side
    mix = dr + bs + ky + pl
    ir = noise(T(1.0)) * env_exp(T(1.0), 0.25); ir = filt(ir, 'lowpass', 6000); ir /= np.abs(ir).sum() ** 0.5 * 8
    mix += np.stack([signal.fftconvolve((ky + pl)[c], ir)[:N] for c in range(2)]) * 0.5
    mix = np.stack([filt(mix[c], 'highpass', 30) for c in range(2)])
    f0 = T(DUR - 0.8); mix[:, f0:] *= np.linspace(1, 0, N - f0)
    return mix

def voice():
    sr, a = wf.read(f'{ROOT}/voice/voice.wav')
    a = a.astype(np.float64) / 32768
    if a.ndim == 2: a = a.mean(1)
    v = np.zeros(N); n = min(len(a), N); v[:n] = a[:n]
    return v

if __name__ == '__main__':
    m = music(); s = sfx(); v = voice()
    k = T(0.05); ev = np.sqrt(np.convolve(v ** 2, np.ones(k) / k, 'same')); ev /= ev.max() + 1e-9
    act = np.convolve(np.clip((ev - 0.04) / 0.1, 0, 1), np.ones(T(0.3)) / T(0.3), 'same')
    duck = 1 - 0.45 * np.clip(act, 0, 1)
    m /= np.abs(m).max() + 1e-9; s /= np.abs(s).max() + 1e-9; v /= np.abs(v).max() + 1e-9
    mix = np.stack([v, v]) * 0.85 + m * 0.50 * duck + s * 0.42
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.95
    wf.write(f'{ROOT}/work/mix.wav', SR, (mix.T * 32767).astype(np.int16))
    wf.write(f'{ROOT}/work/music.wav', SR, (m.T * 0.9 * 32767).astype(np.int16))
    print('ok', DUR)
