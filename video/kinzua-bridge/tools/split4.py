"""Corta el máster en 4 partes mp4 reproducibles de tamaño parecido (cortes en fotogramas clave, sin recodificar).

usage: python split4.py MAESTRO.mp4 CARPETA_SALIDA NOMBRE  ->  NOMBRE_parte_N_de_4.mp4 (≈350 MiB cada una para ~19 min)"""
import subprocess, sys, os
src, outdir, stem = sys.argv[1], sys.argv[2], sys.argv[3]
p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "packet=stream_index,pts_time,size,flags", "-of", "csv=p=0", src],
                   capture_output=True, text=True, check=True).stdout.split("\n")
pk = []
for l in p:
    f = l.split(",")
    if len(f) < 4 or f[1] in ("", "N/A"):
        continue
    pk.append((int(f[0]), float(f[1]), int(f[2]), "K" in f[3]))
pk.sort(key=lambda x: x[1])
total = sum(x[2] for x in pk)
keys, acc = [], 0
for s, t, sz, k in pk:
    if s == 0 and k:
        keys.append((t, acc))
    acc += sz
cuts = []
for q in (1, 2, 3):
    tgt = total * q / 4
    cuts.append(min(keys, key=lambda x: abs(x[1] - tgt))[0])
print("cuts", cuts, "total MiB", total / 2**20)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0", "-c", "copy", "-f", "segment",
                "-segment_times", ",".join(f"{c:.6f}" for c in cuts), "-reset_timestamps", "1", "-segment_start_number", "1",
                "-segment_format_options", "movflags=+faststart", os.path.join(outdir, stem + "_parte_%d_de_4.mp4")], check=True)
for f in sorted(os.listdir(outdir)):
    fp = os.path.join(outdir, f)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fp], capture_output=True, text=True).stdout.strip()
    print(f, round(os.path.getsize(fp) / 2**20, 1), "MiB", d, "s")
