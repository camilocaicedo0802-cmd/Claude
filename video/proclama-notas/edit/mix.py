"""Mezcla final: música + sonido ambiente de los planos + efectos de Proclama, normalizada a -14 LUFS.

python3 mix.py plan.json music.wav out.wav [--music-lufs -17]
plan.json: {'total', 'shots': [[t, src, t_in, dur, vol_db|None, speed]], 'sfx': [[name|path, t, gain_db]],
            'voices': [[t, src, t_in, dur, gain_db]]  (opcional: entrevistas, a nivel de diálogo)}
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

SR = 48000
SFX = '/home/user/notas/work/assets/sfx/'


def decode(src, t_in=0.0, dur=None, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{t_in:.3f}']
    if dur:
        cmd += ['-t', f'{dur:.3f}']
    cmd += ['-i', src, '-vn']
    if af:
        cmd += ['-af', af]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    r = subprocess.run(cmd, capture_output=True)
    a = np.frombuffer(r.stdout, np.float32)
    return a.reshape(-1, 2).astype(np.float64) if len(a) else np.zeros((0, 2))


def lufs(x, tmp='/tmp/_lufs.wav'):
    wavfile.write(tmp, SR, np.clip(x, -1, 1).astype(np.float32))
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', tmp, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True)
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    return float(m[-1]) if m else -70.0


def fade(a, fi=0.08, fo=0.12):
    n = len(a)
    i, o = min(n, int(fi * SR)), min(n, int(fo * SR))
    if i:
        a[:i] *= np.linspace(0, 1, i)[:, None]
    if o:
        a[-o:] *= np.linspace(1, 0, o)[:, None]
    return a


def place(buf, a, t, gain_db=0.0):
    i = int(round(t * SR))
    if i < 0:
        a, i = a[-i:], 0
    j = min(len(buf), i + len(a))
    if j > i:
        buf[i:j] += a[:j - i] * 10 ** (gain_db / 20)


def main():
    plan_path, music_path, out = sys.argv[1:4]
    music_lufs = float(sys.argv[sys.argv.index('--music-lufs') + 1]) if '--music-lufs' in sys.argv else -17.0
    target = float(sys.argv[sys.argv.index('--target') + 1]) if '--target' in sys.argv else -14.0
    plan = json.load(open(plan_path))
    total = plan['total']
    N = int(total * SR) + SR
    bus_music, bus_nat, bus_fx, bus_voice = (np.zeros((N, 2)) for _ in range(4))
    sr, m = wavfile.read(music_path)
    m = m.astype(np.float64) / 32768.0
    m *= 10 ** ((music_lufs - lufs(m)) / 20)
    place(bus_music, m, plan.get('music_t0', 0.0))
    for t, src, t_in, dur, vol, speed in plan['shots']:
        if vol is None or speed != 1.0:
            continue
        a = decode(src, t_in, dur)
        if len(a) == 0:
            continue
        L = lufs(a) if len(a) > SR else -20.0
        g = -14.0 - L if L > -60 else 0.0  # cada fuente a -14 LUFS antes de aplicar su nivel relativo
        place(bus_nat, fade(a, 0.1, 0.15), t, vol + g + plan.get('nat_boost', 0.0))
    for v in plan.get('voices', []):
        t, src, t_in, dur, gain = v[:5]
        af = 'highpass=f=85,lowpass=f=12000,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2'
        a = decode(src, t_in, dur, af=af)
        L = lufs(a)
        g = (-16.0 - L) if L > -60 else 0.0  # cada respuesta a -16 LUFS: todas las voces al mismo nivel
        place(bus_voice, fade(a, 0.06, 0.12), t, gain + g)
    for name, t, gain in plan.get('sfx', []):
        p = name if os.path.exists(name) else SFX + name + '.wav'
        place(bus_fx, decode(p), t, gain)
    # ducking: la música baja bajo las voces de entrevistas
    if np.abs(bus_voice).max() > 0:
        def movavg(x, k):
            c = np.concatenate([[0.0], np.cumsum(x)])
            half = k // 2
            idx = np.arange(len(x))
            a, b = np.clip(idx - half, 0, len(x)), np.clip(idx + half, 0, len(x))
            return (c[b] - c[a]) / np.maximum(1, b - a)
        env = movavg(np.abs(bus_voice).max(1), int(0.05 * SR))
        gate = movavg((env > 0.01).astype(np.float64), int(0.5 * SR))
        duck = 1 - plan.get('duck', 0.55) * np.clip(gate * 1.6, 0, 1)
        bus_music *= duck[:, None]
    mix = bus_music + bus_nat + bus_fx + bus_voice
    mix = mix[:int(total * SR)]
    tmp = out + '.pre.wav'
    wavfile.write(tmp, SR, np.clip(mix, -1, 1).astype(np.float32))
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', tmp, '-af', f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-ar', str(SR), '-c:a', 'pcm_s16le', out],
                   check=True)
    os.remove(tmp)
    for nm, b in (('música', bus_music), ('ambiente', bus_nat), ('efectos', bus_fx), ('voces', bus_voice)):
        if np.abs(b).max() > 0:
            print(f'  {nm}: {lufs(b[:int(total * SR)]):.1f} LUFS (antes de normalizar)')
    print(out, 'final', lufs(wavfile.read(out)[1].astype(np.float64) / 32768.0), 'LUFS')


if __name__ == '__main__':
    main()
