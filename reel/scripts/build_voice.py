"""Monta la pista de voz final siguiendo src/data/edl.json.

Procesado: paso alto 80 Hz, reducción de ruido suave, EQ de presencia, compresión y normalización.
Cada segmento lleva fundidos de 6 ms para que los cortes no hagan clic.
Uso: python3 build_voice.py <video_base> <edl.json> <salida.wav>
"""
import json
import subprocess
import sys

src, edl_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
edl = json.load(open(edl_path))["segments"]
F = 0.006
parts, labels = [], []
for k, s in enumerate(edl):
    d = s["srcOut"] - s["srcIn"]
    parts.append(
        f"[a]atrim=start={s['srcIn']:.4f}:end={s['srcOut']:.4f},asetpts=PTS-STARTPTS,"
        f"afade=t=in:d={F},afade=t=out:st={max(0, d - F):.4f}:d={F}[s{k}]"
    )
    labels.append(f"[s{k}]")
pre = ("[0:a]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,highpass=f=80,afftdn=nf=-28,"
       "equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=2.5,"
       "acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4,asplit=1[a]")
graph = ";".join([pre] + parts + ["".join(labels) + f"concat=n={len(edl)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=7[out]"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", graph, "-map", "[out]",
                "-ar", "48000", "-ac", "1", out], check=True)
dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                     capture_output=True, text=True).stdout.strip()
print("voz:", out, dur, "s")
