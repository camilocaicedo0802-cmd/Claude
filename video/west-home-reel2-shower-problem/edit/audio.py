"""Reel 2 mix: Félix's voice + music (tape stop, bar splices, ducking) + SFX taken only from the client's library."""
import sys, os, subprocess, json, math
import numpy as np
import scipy.signal as sg
import scipy.io.wavfile as wf
import pyloudnorm as pyln
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T
import overlays as O
from core import ROOT

SR = 48000
N = int(T.DUR * SR) + 1
OUT = ROOT + 'out/'; STEM = OUT + 'stems/'
os.makedirs(STEM, exist_ok=True)
meter = pyln.Meter(SR)
LIB = ROOT + 'sfxlib/'
CAT = {e['file']: e for e in json.load(open(LIB + 'library.json'))}


def load(path, a=None, b=None, ch=1, filt=None):
    cmd = ['ffmpeg', '-v', 'error']
    if a is not None:
        cmd += ['-ss', f'{a:.3f}']
    cmd += ['-i', path]
    if b is not None:
        cmd += ['-t', f'{b - a:.3f}']
    if filt:
        cmd += ['-af', filt]
    cmd += ['-vn', '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return x.reshape(-1, ch) if ch > 1 else x


def db(x):
    return 10 ** (x / 20)


def fade(x, fi=0.01, fo=0.02):
    x = x.copy(); n1, n2 = int(fi * SR), int(fo * SR)
    x[:n1] *= np.linspace(0, 1, n1)[:, None] if x.ndim == 2 else np.linspace(0, 1, n1)
    x[-n2:] *= np.linspace(1, 0, n2)[:, None] if x.ndim == 2 else np.linspace(1, 0, n2)
    return x


# ---------------------------------------------------------------- voice
VFILT = ('highpass=f=90,lowpass=f=15000,afftdn=nr=12:nf=-40,'
         'equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=9000:t=q:w=1.0:g=1.5,'
         'acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,deesser=i=0.35')
voice = np.zeros(N, np.float32); vact = np.zeros(N, np.float32)
for path, a, b, tp in T.VOICE:
    pre = 0.4
    x = load(path, max(0, a - pre), b, 1, VFILT)[int((a - max(0, a - pre)) * SR):].astype(np.float64)
    x *= db(-17.0 - meter.integrated_loudness(x))
    x = fade(x, 0.012, 0.03)
    i = int(tp * SR); n = min(len(x), N - i)
    voice[i:i + n] += x[:n]; vact[i:i + n] = 1
wf.write(STEM + 'voice.wav', SR, voice)

# ---------------------------------------------------------------- music
mus = load(ROOT + 'music/track.mp3', ch=2)
music = np.zeros((N, 2), np.float32)
XF = int(0.012 * SR)


def place(dst_t0, dst_t1, src_t0, fin=True, fout=True):
    a, b = int(dst_t0 * SR), min(N, int(dst_t1 * SR))
    s = int(src_t0 * SR)
    seg = mus[s:s + (b - a)].copy()
    if fin: seg[:XF] *= np.linspace(0, 1, XF)[:, None]
    if fout: seg[-XF:] *= np.linspace(1, 0, XF)[:, None]
    music[a:a + len(seg)] += seg


TAPE0 = T.FREEZE0
place(0.0, TAPE0, 0.0, fin=False, fout=False)
# tape stop: playback rate falls 1 -> 0 over 0.45 s
dur = 0.45; n = int(dur * SR)
rate = np.linspace(1, 0, n) ** 1.3
pos = TAPE0 * SR + np.cumsum(rate)
ts = np.stack([np.interp(pos, np.arange(len(mus)), mus[:, c]) for c in range(2)], 1).astype(np.float32)
ts *= np.linspace(1, 0, n)[:, None] ** 0.6
music[int(TAPE0 * SR):int(TAPE0 * SR) + n] = ts
# segment B (intro section, then the drop on the reveal) and the outro splice
B0 = T.SEGB; OUTRO_V = T.OUTRO; OUTRO_T = T.B0 + T.P * 64
place(B0, OUTRO_V + 0.012, B0 - T.DB)
place(OUTRO_V - 0.012, T.DUR, OUTRO_T)
# segment B fades in over 1 s, low-passed until the reveal
i0 = int(B0 * SR); i1 = int((T.REVEAL - 0.02) * SR)
music[i0:i0 + SR] *= np.linspace(0, 1, SR)[:, None] ** 1.5
sos = sg.butter(2, 900, 'lp', fs=SR, output='sos')
lp = sg.sosfiltfilt(sos, music[i0:i1], axis=0)
mix_k = np.linspace(0, 1, i1 - i0)[:, None] ** 3              # filter opens towards the drop
music[i0:i1] = (lp * (1 - mix_k) + music[i0:i1] * mix_k).astype(np.float32)
fo = int(0.5 * SR); music[-fo:] *= np.linspace(1, 0, fo)[:, None]

a8 = int(T.ba(16) * SR)
music[:a8] *= db(4.0)                                      # thin intro section: lift it
ml = meter.integrated_loudness(music.astype(np.float64))
music *= db(-22.0 - ml)
# ducking under the voice (look-ahead 40 ms, attack 60 ms, release 300 ms)
v_rms = np.sqrt(sg.lfilter([1], [1, -0.999], voice.astype(np.float64) ** 2) * 0.001)
gate = (v_rms > db(-45)).astype(np.float32) * vact
la = int(0.04 * SR); gate = np.concatenate([gate[la:], np.zeros(la, np.float32)])
env = np.zeros(N, np.float32); e = 1.0
att, rel = math.exp(-48 / (0.06 * SR)), math.exp(-48 / (0.30 * SR))
for i in range(0, N, 48):
    g = gate[i:i + 48].max(); e = g + (e - g) * (att if g > e else rel); env[i:i + 48] = e
music *= db(-8.5 * env)[:, None]
wf.write(STEM + 'music.wav', SR, music)

# ---------------------------------------------------------------- SFX (client library only)
KEYS = [f'audio/typing/mechanical_keyboard_click_{k:02d}.wav' for k in (4, 5, 7, 8, 10, 11, 12, 13, 17, 18, 19)]
MAP = {   # kind -> (file, gain dB, align: 'peak' puts the sound's peak on the event time)
    'pop': ('audio/pop/pop_up_sfx.wav', -15, 'peak'),
    'bass': ('audio/impact/sub_bass_hit.wav', -18, 'peak'),
    'impact': ('audio/impact/sub_bass_drop_2.wav', -13, 'peak'),
    'stamp': ('audio/impact/deep_bass_hit_1.wav', -14, 'peak'),
    'shutter': ('audio/camera/camera_shutter.wav', -12, 'peak'),
    'flash': ('audio/camera/camera_flash.wav', -15, 'peak'),
    'glass': ('audio/glass/vidrio.wav', -16, 'peak'),
    'shine': ('audio/pop/chasquido_epico.wav', -16, 'peak'),
    'click': ('audio/click/mouse_click_04.wav', -12, 'peak'),
    'swoosh': ('audio/whoosh/swoosh_01_04.wav', -13, 'peak'),
}
_cache = {}


def snd(f):
    if f not in _cache:
        sr, x = wf.read(LIB + f)
        x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
        if x.ndim == 1: x = np.stack([x, x], 1)
        _cache[f] = x
    return _cache[f]


sfx = np.zeros((N, 2), np.float64)
log = []


def put(t, f, gain, align='peak', maxlen=None, pan=0.0):
    x = snd(f)
    if maxlen:
        x = fade(x[:int(maxlen * SR)], 0.002, 0.08)
    off = int(CAT[f]['peak_t'] * SR) if align == 'peak' else 0
    i = int(t * SR) - off; j0 = max(0, i); k0 = j0 - i; n = min(len(x) - k0, N - j0)
    if n <= 0: return
    y = x[k0:k0 + n] * db(gain)
    if pan:
        y = y * np.array([math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)]) * math.sqrt(2)
    sfx[j0:j0 + n] += y
    log.append((round(t, 3), f.split('/')[-1], gain))


O.build()
rng = np.random.default_rng(11)
for t, kind, g in sorted(O.SFX):
    if kind == 'key':
        f = KEYS[rng.integers(len(KEYS))]
        put(t, f, -21 + g + rng.uniform(-1.5, 1.5), 'peak', pan=rng.uniform(-0.25, 0.25))
    elif kind == 'film':
        x = snd('audio/retro/film_burns_sfx.wav')[int(7.6 * SR):int(8.8 * SR)]
        x = fade(x, 0.01, 0.25); i = int(t * SR)
        sfx[i:i + len(x)] += x * db(-17 + g); log.append((t, 'film_burns_sfx.wav[7.6-8.8]', -17 + g))
    else:
        f, base, al = MAP[kind]
        put(t, f, base + g, al, maxlen=1.4 if kind in ('bass', 'impact', 'stamp') else None)
# transitions
WH = ['audio/whoosh/vs_short_whoosh_1.wav', 'audio/whoosh/vs_short_whoosh_3.wav', 'audio/whoosh/vs_short_whoosh_4.wav',
      'audio/whoosh/vs_short_whoosh_6.wav', 'audio/whoosh/vs_short_whoosh_2.wav']
k = 0
for s in T.SHOTS:
    tin = s.get('tin', ('cut',))
    if tin[0] == 'whip':
        put(s['t0'], WH[k % len(WH)], -14, pan={'left': -0.4, 'right': 0.4}.get(tin[1], 0)); k += 1
    elif tin[0] == 'zoom':
        put(s['t0'], 'audio/whoosh/woosh_effect_8.wav', -15)
    elif tin[0] == 'flash':
        put(s['t0'], 'audio/camera/camera_flash.wav', -17)
# riser into the before/after reveal
put(T.REVEAL, 'audio/riser/sharp_riser.wav', -15)
wf.write(STEM + 'sfx.wav', SR, sfx.astype(np.float32))
json.dump(log, open(STEM + 'sfx_log.json', 'w'), indent=0)

# ---------------------------------------------------------------- mix + master
mix = np.stack([voice, voice], 1).astype(np.float64) + music.astype(np.float64) + sfx
mix *= db(-14.3 - meter.integrated_loudness(mix))
wf.write(OUT + 'mix_pre.wav', SR, mix.astype(np.float32))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + 'mix_pre.wav', '-af',
                'alimiter=limit=0.84:attack=3:release=60:level=disabled', '-c:a', 'pcm_s24le', OUT + 'mix.wav'], check=True)
sr_, fin = wf.read(OUT + 'mix.wav'); fin = fin.astype(np.float64) / 2 ** 31
print('final LUFS', round(meter.integrated_loudness(fin), 2), 'peak dBFS', round(20 * np.log10(np.abs(fin).max()), 2))
for name, x in [('voice', np.stack([voice, voice], 1)), ('music', music), ('sfx', sfx)]:
    print(name, 'LUFS', round(meter.integrated_loudness(x.astype(np.float64)), 1))
print('sfx events', len(log))
