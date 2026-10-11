"""Recorta silencios de la locución y la acelera sin cambiar el tono.
Uso: python3 tools/editar_voz.py assets/voz.mp3 public/audio/voz_edit.wav
"""
import subprocess, sys, re, json

SRC, DST = sys.argv[1], sys.argv[2]
GAP = 0.14      # silencio máximo conservado entre frases (s, antes de acelerar)
TEMPO = 1.19    # aceleración final

log = subprocess.run(["ffmpeg", "-i", SRC, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                           capture_output=True, text=True).stdout)
# segmentos de voz = complemento de los silencios
segs, cur = [], 0.0
for s, e in zip(starts, ends):
    if s > cur:
        segs.append([cur, s])
    cur = e
if cur < dur:
    segs.append([cur, dur])
segs = [[max(0, a - GAP / 2), min(dur, b + GAP / 2)] for a, b in segs if b - a > 0.05]
# fusiona solapes
merged = []
for a, b in segs:
    if merged and a <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
parts = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b-a-0.015:.3f}:d=0.015[s{i}];"
                for i, (a, b) in enumerate(merged))
flt = parts + "".join(f"[s{i}]" for i in range(len(merged))) + f"concat=n={len(merged)}:v=0:a=1,atempo={TEMPO}," \
      "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=7[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", flt, "-map", "[out]", "-ar", "48000", "-ac", "1", DST], check=True)
# mapa tiempo original -> tiempo editado (para re-alinear palabras)
mapping, acc = [], 0.0
for a, b in merged:
    mapping.append(dict(src_a=a, src_b=b, dst_a=acc / TEMPO))
    acc += b - a
json.dump(dict(tempo=TEMPO, segments=mapping, out_duration=acc / TEMPO), open(DST + ".map.json", "w"), indent=1)
print("segmentos", len(merged), "duración final", round(acc / TEMPO, 2))
