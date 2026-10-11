#!/usr/bin/env python3
"""
Audio de la referencia: separar voz/música, construir la cama musical en bucle y extraer SFX.

Subcomandos:
  separate <video|audio> <outdir> [--model htdemucs|htdemucs_ft]
      -> <outdir>/<model>/<nombre>/{vocals,no_vocals}.wav
  music <no_vocals.wav> <salida.wav> --duration 45 [--start 0.3 --end 8.3] [--xfade 1.0] [--keep-percussive]
      -> bucle con fundidos de potencia constante; por defecto se queda con la parte ARMÓNICA
         (quita golpes/whooshes que la referencia mezcló encima de la música).
  sfx <no_vocals.wav> <outdir> [--times 0.0,3.4,...] [--pre 0.05 --post 0.6]
      -> recorta efectos alrededor de los instantes dados (o de los onsets percusivos fuertes si no se dan).

Si la descarga oficial de pesos de Demucs (dl.fbaipublicfiles.com) está bloqueada, se usa un espejo
en Hugging Face verificando el prefijo SHA-256 que va en el propio nombre del archivo (el mismo chequeo que hace Demucs).
"""
import argparse
import hashlib
import os
import subprocess
import sys
import urllib.request

import numpy as np

SR = 44100
MODELS = {
    "htdemucs": ["955717e8-8726e21a.th"],
    "htdemucs_ft": ["f7e0c4bc-ba3fe64a.th", "d12395a8-e57c48e6.th", "92cfc3b6-ef3bcb9c.th", "04573f0d-f3cf25b2.th"],
}
OFFICIAL = "https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/"
MIRROR = "https://huggingface.co/JosefKuchar/Demucs/resolve/main/"


def ensure_demucs_weights(model="htdemucs"):
    cache = os.path.join(os.path.expanduser("~"), ".cache", "torch", "hub", "checkpoints")
    os.makedirs(cache, exist_ok=True)
    for f in MODELS.get(model, []):
        dst = os.path.join(cache, f)
        if os.path.exists(dst):
            continue
        expected = f.split("-")[1].split(".")[0]
        for base in (OFFICIAL, MIRROR):
            try:
                print(f"  descargando {f} de {base.split('/')[2]}…", file=sys.stderr)
                urllib.request.urlretrieve(base + f, dst + ".part")
                h = hashlib.sha256(open(dst + ".part", "rb").read()).hexdigest()
                if h.startswith(expected):
                    os.replace(dst + ".part", dst)
                    break
                print(f"  hash no coincide ({h[:8]} != {expected}), se descarta", file=sys.stderr)
                os.remove(dst + ".part")
            except Exception as e:  # noqa: BLE001
                print(f"  fallo con {base}: {e}", file=sys.stderr)
        if not os.path.exists(dst):
            raise RuntimeError(f"No se pudieron obtener los pesos {f}")


def to_wav(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), dst], check=True)


def cmd_separate(a):
    ensure_demucs_weights(a.model)
    os.makedirs(a.outdir, exist_ok=True)
    src = a.input
    if not src.lower().endswith(".wav"):
        wav = os.path.join(a.outdir, os.path.splitext(os.path.basename(src))[0] + ".wav")
        to_wav(src, wav)
        src = wav
    subprocess.run([sys.executable, "-m", "demucs", "-n", a.model, "--two-stems", "vocals", "-o", a.outdir, src], check=True)
    out = os.path.join(a.outdir, a.model, os.path.splitext(os.path.basename(src))[0])
    print(out)


def norm_peak(x, peak_db):
    return x * (10 ** (peak_db / 20) / (np.max(np.abs(x)) + 1e-12))


def cmd_music(a):
    import librosa
    import soundfile as sf

    y, _ = librosa.load(a.input, sr=SR, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y])
    if not a.keep_percussive:
        y = np.stack([librosa.effects.hpss(ch, margin=2.0)[0] for ch in y])
    end = a.end if a.end else y.shape[1] / SR - 0.2
    seg = y[:, int(a.start * SR): int(end * SR)]
    xf = int(a.xfade * SR)
    if seg.shape[1] <= 2 * xf:
        raise SystemExit("Segmento demasiado corto para el fundido")
    target = int(a.duration * SR)
    out = np.zeros((2, target + seg.shape[1]))
    t = np.linspace(0, np.pi / 2, xf)
    fin, fout = np.sin(t), np.cos(t)
    pos, first = 0, True
    while pos < target:
        s = seg.copy()
        if not first:
            s[:, :xf] *= fin
        s[:, -xf:] *= fout
        out[:, pos: pos + s.shape[1]] += s
        pos += s.shape[1] - xf
        first = False
    out = norm_peak(out[:, :target], -3.0)
    sf.write(a.output, out.T, SR)
    rms = 20 * np.log10(np.sqrt((out ** 2).mean()) + 1e-12)
    reps = a.duration / max(0.1, (seg.shape[1] - xf) / SR)
    print(f"{a.output}: {a.duration:.1f}s, RMS {rms:.1f} dBFS, el segmento se repite ~{reps:.1f} veces")


def cmd_sfx(a):
    import librosa
    import soundfile as sf

    y, _ = librosa.load(a.input, sr=SR, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y])
    mono = y.mean(0)
    perc = librosa.effects.hpss(mono, margin=1.5)[1]
    if a.times:
        times = [float(x) for x in a.times.split(",")]
    else:
        on = librosa.onset.onset_detect(y=perc, sr=SR, units="time", delta=0.3)
        st = librosa.onset.onset_strength(y=perc, sr=SR, hop_length=512)
        times = [float(t) for t in on if st[min(len(st) - 1, int(t * SR / 512))] > np.percentile(st, 92)]
    os.makedirs(a.outdir, exist_ok=True)
    for k, t in enumerate(times):
        s0, s1 = max(0, int((t - a.pre) * SR)), min(y.shape[1], int((t + a.post) * SR))
        x = y[:, s0:s1].T.copy()
        n = len(x)
        fi, fo = int(0.003 * SR), int(min(0.08, a.post / 3) * SR)
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        f = os.path.join(a.outdir, f"ref_sfx_{k:02d}_{t:.2f}s.wav")
        sf.write(f, norm_peak(x, -1.0), SR)
        print(f, f"{n / SR:.2f}s")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("separate")
    p.add_argument("input")
    p.add_argument("outdir")
    p.add_argument("--model", default="htdemucs", choices=list(MODELS))
    p = sp.add_parser("music")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--start", type=float, default=0.3)
    p.add_argument("--end", type=float, default=None)
    p.add_argument("--xfade", type=float, default=1.0)
    p.add_argument("--keep-percussive", action="store_true")
    p = sp.add_parser("sfx")
    p.add_argument("input")
    p.add_argument("outdir")
    p.add_argument("--times", default=None)
    p.add_argument("--pre", type=float, default=0.05)
    p.add_argument("--post", type=float, default=0.6)
    a = ap.parse_args()
    {"separate": cmd_separate, "music": cmd_music, "sfx": cmd_sfx}[a.cmd](a)


if __name__ == "__main__":
    main()
