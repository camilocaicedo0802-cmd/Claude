"""Música (electronic hip-hop / funky, 104 BPM), efectos de sonido sintetizados y mezcla final.

Todo es síntesis propia (sin samples de terceros), así que no hay problemas de licencia.
Lee src/sfx.json (cues por frame) y public/audio/voz_edit.wav; escribe:
  public/audio/musica.wav, public/audio/sfx.wav, public/audio/mezcla.wav (la que usa Remotion)
Uso: python3 -I tools/audio.py
"""
import json
import subprocess

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
FPS = 30
DUR_FRAMES = 900
N = int(SR * DUR_FRAMES / FPS)
VOICE_OFFSET = 5  # frames (igual que src/cues.ts)
rng = np.random.default_rng(7)

cfg = json.load(open('src/sfx.json'))


def fr2s(fr):
    return int(round(fr / FPS * SR))


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)


def noise(n):
    return rng.standard_normal(n)


def reverb_ir(seconds=1.2, damp=3000):
    n = int(seconds * SR)
    ir = noise(n) * env_exp(n, seconds / 5)
    ir = lp(ir, damp)
    ir[0] = 1.0
    return ir / np.abs(ir).sum() * 6


IR_SHORT = reverb_ir(0.6, 4000)
IR_LONG = reverb_ir(1.6, 2500)


def place(buf, sig, at, gain=1.0):
    i = max(0, at)
    j = min(len(buf), at + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# --------------------------------------------------------------------------------------------- instrumentos
def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env_exp(n, 0.16)
    click = hp(noise(n), 2500) * env_exp(n, 0.002) * 0.5
    return np.tanh((body + click) * 1.6) * 0.9


def snare():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 185 * t) * env_exp(n, 0.05) * 0.6
    nz = bp(noise(n), 1200, 7500) * env_exp(n, 0.09)
    clap = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]):
        i = int(d * SR)
        clap[i:] += bp(noise(n - i), 900, 3200) * env_exp(n - i, 0.012 if k < 2 else 0.07)
    s = tone + nz * 0.7 + clap * 0.8
    s = s + fftconvolve(s, IR_SHORT)[:n] * 0.35
    return s * 0.55


def hat(open_=False):
    n = int((0.32 if open_ else 0.06) * SR)
    s = hp(noise(n), 7000, 4) * env_exp(n, 0.09 if open_ else 0.014)
    return s * (0.28 if open_ else 0.22)


def shaker():
    n = int(0.08 * SR)
    a = np.minimum(1, np.arange(n) / (0.02 * SR))
    return hp(noise(n), 5000) * a * env_exp(n, 0.02) * 0.12


def bass_note(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    saw = 2 * ((freq * t) % 1) - 1
    sub = np.sin(2 * np.pi * freq * t)
    cutoff_env = 180 + 1200 * np.exp(-t / 0.06)
    # filtro dinámico por bloques
    out = np.zeros(n)
    blk = 256
    zi_state = None
    from scipy.signal import sosfilt_zi
    for b in range(0, n, blk):
        c = float(cutoff_env[min(b, n - 1)])
        sos = butter(2, c, btype='low', fs=SR, output='sos')
        if zi_state is None:
            zi_state = sosfilt_zi(sos) * 0
        seg, zi_state = sosfilt(sos, saw[b : b + blk], zi=zi_state)
        out[b : b + blk] = seg
    a = np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.02).clip(0, 1)
    return np.tanh((out * 0.7 + sub * 0.8) * a * 1.4) * 0.5


def keys_chord(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for fq in freqs:
        s += np.sin(2 * np.pi * fq * t) * env_exp(n, 0.35)
        s += 0.35 * np.sin(2 * np.pi * fq * 2 * t) * env_exp(n, 0.12)
        s += 0.12 * np.sin(2 * np.pi * fq * 3.98 * t) * env_exp(n, 0.04)  # campana tipo Rhodes
    s *= 1 + 0.12 * np.sin(2 * np.pi * 5.2 * t)  # trémolo
    a = np.minimum(1, t / 0.003) * np.minimum(1, (dur - t) / 0.03).clip(0, 1)
    return s * a * 0.11


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for fq in freqs:
        for det in (-0.12, 0.0, 0.11):
            f2 = fq * 2 ** (det / 12)
            s += 2 * ((f2 * t + rng.random()) % 1) - 1
    s = lp(s, 1400)
    a = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.3).clip(0, 1)
    return s * a * 0.035


# A menor: Am9 | Fmaj9 | Cmaj7 | Em7
CHORDS = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 67], [48, 55, 59, 64], [52, 55, 59, 62]]
BASS_ROOT = [33, 29, 36, 28]
# patrón de bajo (paso 16avo, semitonos sobre la raíz, duración en pasos)
BASS_PAT = [(0, 0, 3), (3, 12, 1), (6, 0, 2), (8, 7, 2), (10, 0, 1), (11, 12, 1), (14, 10, 2)]
KICKS = [[0, 7, 10], [0, 10, 13]]


def music():
    bpm = cfg['music']['bpm']
    step = 60 / bpm / 4  # segundos por 16avo
    L = np.zeros(N)
    R = np.zeros(N)
    side = np.zeros(N)  # envolvente de sidechain
    drums = np.zeros(N)
    melodic = np.zeros(N)
    K, S, HC, HO = kick(), snare(), hat(), hat(True)
    for sec in cfg['music']['sections']:
        t0 = sec['from'] / FPS
        t1 = sec['to'] / FPS
        kind = sec['kind']
        nsteps = int(np.ceil((t1 - t0) / step))
        for s in range(nsteps):
            ts = t0 + s * step
            if ts >= t1:
                break
            bar = s // 16
            st = s % 16
            swing = step * 0.12 if st % 2 == 1 else 0
            at = int((ts + swing) * SR)
            ch = bar % 4
            if kind in ('groove',):
                if st in KICKS[bar % 2]:
                    place(drums, K, at)
                    place(side, env_exp(int(0.25 * SR), 0.08), at)
                if st in (4, 12):
                    place(drums, S, at)
                if st % 2 == 0:
                    place(drums, HC, at, 0.9 if st % 4 == 0 else 0.6)
                elif sec.get('perc'):
                    place(drums, HC, at, 0.35)
                if st == 14 and bar % 2 == 1:
                    place(drums, HO, at)
                if sec.get('perc') and st % 4 == 2:
                    place(drums, shaker(), at)
                for (ps, semi, ln) in BASS_PAT:
                    if st == ps:
                        place(melodic, bass_note(midi(BASS_ROOT[ch] + semi), ln * step * 0.92), at, 1.0)
                if st in (2, 7, 10) or (st == 14 and bar % 2 == 0):
                    place(melodic, keys_chord([midi(m) for m in CHORDS[ch]], step * (1.6 if st != 10 else 3)), at)
            elif kind == 'break':
                if st == 0:
                    place(melodic, pad([midi(m) for m in CHORDS[ch]], min(16 * step, t1 - ts) + 0.2), at)
                    place(melodic, keys_chord([midi(m) for m in CHORDS[ch]], 1.2), at, 0.7)
                if st % 4 == 0:
                    place(drums, HC, at, 0.25)
            elif kind == 'outro':
                if s == 0:
                    place(drums, K, at, 1.1)
                    place(drums, S, at, 0.8)
                    place(melodic, bass_note(midi(33), 1.4), at)
                    place(melodic, keys_chord([midi(m) for m in CHORDS[0]], 1.9), at, 1.3)
                    place(melodic, pad([midi(m) for m in CHORDS[0]], 1.9), at, 1.5)
                if s in (8, 12) and ts < t1 - 0.3:
                    place(drums, HC, at, 0.4)
    # filtro inicial (abre en "editor")
    open_at = fr2s(cfg['music']['sections'][0].get('filterOpenAt', 0))
    if open_at > 0:
        pre = lp(melodic[:open_at] + drums[:open_at], 900)
        fade = np.linspace(0, 1, open_at)
        melodic[:open_at] = melodic[:open_at] * fade + pre * (1 - fade) * 0.8
        drums[:open_at] *= fade * 0.7 + 0.3
    # sidechain (bombeo) sobre la parte melódica
    duck = 1 - 0.45 * np.clip(side, 0, 1)
    melodic *= duck
    # reverb en melódicos
    melodic = melodic + fftconvolve(melodic, IR_LONG)[:N] * 0.25
    mix = drums + melodic
    # stops: silencio total para dejar respirar la voz y las gráficas
    for a, b in cfg['music']['stops']:
        i, j = fr2s(a), fr2s(b)
        g = np.ones(N)
        g[i:j] = 0
        ramp = int(0.01 * SR)
        g[i - ramp : i] = np.linspace(1, 0, ramp)
        mix *= g
    # estéreo: pequeño Haas en melódicos
    d = int(0.012 * SR)
    L = mix
    R = drums + np.concatenate([np.zeros(d), melodic[:-d]])
    for a, b in cfg['music']['stops']:
        R[fr2s(a) : fr2s(b)] = 0
    # bajos controlados: corte bajo 32 Hz
    L, R = hp(L, 32), hp(R, 32)
    st = np.stack([L, R], 1)
    # cola final
    st[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))[:, None]
    return np.tanh(st * 1.2) / 1.2


# ---------------------------------------------------------------------------------------------- efectos
def sweep_noise(dur, f0, f1, peak=0.6, q=0.35):
    """Ruido filtrado por un pasa-banda cuya frecuencia central barre de f0 a f1 (estado del filtro continuo)."""
    from scipy.signal import sosfilt_zi
    n = int(dur * SR)
    out = np.zeros(n)
    nz = noise(n)
    blk = 256
    zi = None
    for b in range(0, n, blk):
        t = b / n
        fc = f0 * (f1 / f0) ** t
        lo, hi = max(40, fc * (1 - q)), min(SR / 2 - 100, fc * (1 + q))
        sos = butter(2, [lo, hi], btype='band', fs=SR, output='sos')
        if zi is None:
            zi = sosfilt_zi(sos) * 0
        seg, zi = sosfilt(sos, nz[b : b + blk], zi=zi)
        out[b : b + blk] = seg
    x = np.linspace(0, 1, n)
    env = np.where(x < peak, (x / peak) ** 2, ((1 - x) / (1 - peak)) ** 1.5)
    return lp(out, 9000) * env


def sfx(kind):
    if kind in ('whoosh', 'whoosh_big', 'whoosh_soft'):
        dur = {'whoosh': 0.4, 'whoosh_big': 0.55, 'whoosh_soft': 0.32}[kind]
        s = sweep_noise(dur, 400, 3800, peak=0.62) + sweep_noise(dur, 200, 1200, peak=0.6) * 0.6
        if kind == 'whoosh_big':
            n = len(s)
            t = np.arange(n) / SR
            s += np.sin(2 * np.pi * (60 + 80 * t / t[-1]) * t) * np.linspace(0, 1, n) ** 3 * 0.5
        s = s + fftconvolve(s, IR_SHORT)[: len(s)] * 0.3
        return s / (np.abs(s).max() + 1e-9) * 0.8, -0.62 * dur  # adelanto: el pico cae en el frame del cue
    if kind == 'swoosh':
        s = sweep_noise(0.22, 1500, 6000, peak=0.5)
        return s / (np.abs(s).max() + 1e-9) * 0.6, -0.1
    if kind == 'click':
        n = int(0.05 * SR)
        t = np.arange(n) / SR
        s = hp(noise(n), 3000) * env_exp(n, 0.0015) + np.sin(2 * np.pi * 2900 * t) * env_exp(n, 0.006) * 0.5
        return s * 0.8, 0
    if kind == 'tick':
        n = int(0.03 * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 4200 * t) * env_exp(n, 0.004) + hp(noise(n), 6000) * env_exp(n, 0.001) * 0.4) * 0.6, 0
    if kind == 'pop':
        n = int(0.14 * SR)
        t = np.arange(n) / SR
        f = 320 + 700 * (1 - np.exp(-t / 0.02))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.035)
        s += hp(noise(n), 2000) * env_exp(n, 0.002) * 0.3
        return s * 0.75, 0
    if kind in ('impact', 'impact_big', 'impact_soft'):
        dur = {'impact': 1.1, 'impact_big': 1.6, 'impact_soft': 0.8}[kind]
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = 34 + 60 * np.exp(-t / 0.08)
        sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, dur / 3.5)
        thump = lp(noise(n), 300) * env_exp(n, 0.05) * 1.5
        crack = bp(noise(n), 1500, 6000) * env_exp(n, 0.012) * (0.5 if kind == 'impact_big' else 0.25)
        s = sub + thump + crack
        s = s + fftconvolve(s, IR_LONG)[:n] * (0.5 if kind == 'impact_big' else 0.3)
        return np.tanh(s * 1.3) * 0.9, -0.005
    if kind in ('riser', 'riser_long'):
        dur = 0.5 if kind == 'riser' else 1.0
        n = int(dur * SR)
        t = np.arange(n) / SR
        x = t / dur
        nz = sweep_noise(dur, 500, 9000, peak=0.97, q=0.5)
        tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (x * 2)) / SR) * x ** 2 * 0.25
        s = nz + tone
        s = s / (np.abs(s).max() + 1e-9) * 0.6
        return s, 0
    if kind == 'keys':
        n = int(0.6 * SR)
        s = np.zeros(n)
        tt = 0.0
        while tt < 0.55:
            k = int(tt * SR)
            m = int(0.03 * SR)
            hit = bp(noise(m), 1800, 6500) * env_exp(m, 0.004) * (0.6 + 0.4 * rng.random())
            hit += lp(noise(m), 400) * env_exp(m, 0.006) * 0.4
            s[k : k + m] += hit[: n - k]
            tt += 0.055 + rng.random() * 0.06
        return s * 0.7, 0
    if kind == 'mouse':
        n = int(0.12 * SR)
        s = np.zeros(n)
        for d, g in ((0, 1.0), (0.07, 0.6)):
            k = int(d * SR)
            m = int(0.02 * SR)
            s[k : k + m] += (bp(noise(m), 2000, 8000) * env_exp(m, 0.0012) + lp(noise(m), 600) * env_exp(m, 0.003) * 0.6) * g
        return s * 0.9, 0
    if kind == 'scroll':
        n = int(0.9 * SR)
        s = np.zeros(n)
        tt, gap, fq = 0.0, 0.07, 2500
        while tt < 0.85:
            k = int(tt * SR)
            m = int(0.012 * SR)
            tk = np.sin(2 * np.pi * fq * np.arange(m) / SR) * env_exp(m, 0.002)
            s[k : k + m] += tk[: n - k]
            tt += gap
            gap = max(0.03, gap * 0.94)
            fq *= 1.02
        return s * 0.5, 0
    if kind == 'counter':
        n = int(1.1 * SR)
        s = np.zeros(n)
        for i in range(18):
            tt = 1.0 * (1 - (1 - i / 18) ** 2)
            k = int(tt * SR)
            m = int(0.01 * SR)
            s[k : k + m] += np.sin(2 * np.pi * 3500 * np.arange(m) / SR) * env_exp(m, 0.002)
        return s * 0.5, 0
    if kind == 'shutter':
        n = int(0.18 * SR)
        s = np.zeros(n)
        for d, g in ((0, 1.0), (0.075, 0.8)):
            k = int(d * SR)
            m = int(0.035 * SR)
            s[k : k + m] += bp(noise(m), 1500, 7000) * env_exp(m, 0.006) * g + lp(noise(m), 500) * env_exp(m, 0.008) * 0.5 * g
        return s * 0.9, -0.0
    if kind == 'scribble':
        n = int(0.28 * SR)
        x = np.linspace(0, 1, n)
        s = bp(noise(n), 2500, 7000) * (np.abs(np.sin(x * np.pi * 7)) ** 2) * np.sin(x * np.pi)
        return s * 0.35, 0
    raise ValueError(kind)


def sfx_track():
    L = np.zeros(N)
    R = np.zeros(N)
    for fr, kind, db in cfg['cues']:
        s, lead = sfx(kind)
        at = fr2s(fr) + int(lead * SR)
        g = 10 ** (db / 20)
        pan = 0.5 + 0.25 * np.sin(fr * 1.7)  # ligera variación estéreo
        place(L, s, at, g * np.sqrt(1 - pan) * 1.41)
        place(R, s, at, g * np.sqrt(pan) * 1.41)
    return np.stack([L, R], 1)


def load_voice():
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'public/audio/voz_edit.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).astype(np.float64)
    out = np.zeros(N)
    place(out, v, fr2s(VOICE_OFFSET))
    return out


def write(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=pcm, check=True)


def lufs(path):
    log = subprocess.run(['ffmpeg', '-i', path, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True).stderr
    for line in log.splitlines()[::-1]:
        if line.strip().startswith('I:'):
            return line.strip()
    return '?'


def lufs_val(x):
    write('out/_tmp.wav', x)
    txt = lufs('out/_tmp.wav')
    return float(txt.split()[1])


if __name__ == '__main__':
    mus = music()
    fx = sfx_track()
    voz = load_voice()
    # sidechain voz → música (la voz manda): −4 dB extra mientras se habla
    venv = np.abs(voz)
    k = int(0.08 * SR)
    venv = np.convolve(venv, np.ones(k) / k, mode='same')
    venv = np.clip(venv / (np.percentile(venv[venv > 1e-4], 75) + 1e-9), 0, 1)
    duck = 1 - 0.37 * venv
    v_l = lufs_val(np.stack([voz, voz], 1))
    m_l = lufs_val(mus)
    mus = mus * 10 ** ((v_l - 11 - m_l) / 20)  # música ≈ 11 LU bajo la voz (antes del ducking)
    fx = fx * 10 ** (-7 / 20) / (np.abs(fx).max() + 1e-9)  # picos de efectos a −7 dBFS antes de normalizar
    write('public/audio/musica.wav', mus)
    write('public/audio/sfx.wav', fx)
    mixed = mus * duck[:, None] + fx + voz[:, None]
    mixed = np.tanh(mixed * 1.05) / 1.05
    write('out/mezcla_pre.wav', mixed)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/mezcla_pre.wav', '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9', '-ar', str(SR), '-ac', '2', 'public/audio/mezcla.wav'], check=True)
    print('voz', v_l, 'música(orig)', m_l)
    print('mezcla', lufs('public/audio/mezcla.wav'))
