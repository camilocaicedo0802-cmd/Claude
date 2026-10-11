#!/usr/bin/env python3
"""
Jump-cuts: elimina los silencios de un metraje (persona a cámara, podcast, pantalla) y deja un archivo
nuevo listo para usar como A-roll. Transcribe DESPUÉS este archivo para que subtítulos y cortes cuadren.

  python3 jumpcut.py bruto.mp4 public/aroll.mp4 --min-silence 0.35 --pad 0.08 [--thr-db -32]
  --keep 0.15   deja este silencio residual entre frases (ritmo menos "picado" si la referencia es pausada)
  --list        solo imprime los segmentos (sin renderizar), para revisar o para usar como lista de cortes

Imprime los instantes de corte en la línea de tiempo NUEVA (útiles para alternar zoom punches en cada corte).
"""
import argparse
import json
import subprocess
import tempfile

import numpy as np


def as_wav(path):
    """librosa/soundfile no leen mp4/mov: extrae el audio a un wav temporal con ffmpeg."""
    import os
    import subprocess
    import tempfile

    if path.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
        return path
    tmp = os.path.join(tempfile.gettempdir(), "mg_" + os.path.basename(path) + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
    return tmp


def segments(path, min_sil, pad, thr_db, keep):
    import librosa

    y, sr = librosa.load(as_wav(path), sr=16000)
    hop = 160
    db = 20 * np.log10(librosa.feature.rms(y=y, frame_length=480, hop_length=hop)[0] + 1e-9)
    thr = thr_db if thr_db is not None else np.percentile(db, 95) - 28
    t = np.arange(len(db)) * hop / sr
    speech = db >= thr
    segs, s = [], None
    for i, v in enumerate(speech):
        if v and s is None:
            s = t[i]
        if not v and s is not None:
            segs.append([s, t[i]])
            s = None
    if s is not None:
        segs.append([s, t[-1]])
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < min_sil:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    dur = len(y) / sr
    out = [[max(0.0, a - pad), min(dur, b + pad + keep)] for a, b in merged if b - a > 0.08]
    return out, dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--min-silence", type=float, default=0.35)
    ap.add_argument("--pad", type=float, default=0.08)
    ap.add_argument("--keep", type=float, default=0.0)
    ap.add_argument("--thr-db", type=float, default=None)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    segs, dur = segments(a.src, a.min_silence, a.pad, a.thr_db, a.keep)
    total = sum(b - a_ for a_, b in segs)
    cuts, acc = [], 0.0
    for a_, b in segs[:-1]:
        acc += b - a_
        cuts.append(round(acc, 3))
    print(json.dumps({"segmentos": [[round(x, 3), round(y, 3)] for x, y in segs], "cortes_en_nueva_linea": cuts}, ensure_ascii=False))
    print(f"{len(segs)} segmentos · {dur:.1f}s -> {total:.1f}s (−{dur - total:.1f}s de silencio)")
    if a.list:
        return
    parts = []
    for i, (s, e) in enumerate(segs):
        parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, e - s - 0.012):.3f}:d=0.012[a{i}]")
    concat = "".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(";".join(parts) + ";" + concat)
        script = f.name
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-filter_complex_script", script, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", a.dst], check=True)
    print(a.dst)


if __name__ == "__main__":
    main()
