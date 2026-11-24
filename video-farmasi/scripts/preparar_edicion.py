"""Monta el A-roll editado a partir de datos/guion_fuente.py:
 - public/edit/aroll.mp4            vídeo cortado (sin audio)
 - public/edit/aroll_persona.webm   capa de la persona con alfa, mismos cortes
 - public/edit/voz.wav              voz cortada con microfundidos de 12 ms y procesada
 - src/datos/edicion.json           segmentos y palabras en tiempos de la edición
"""
import json, os, subprocess, sys
sys.path.insert(0, "datos")
from guion_fuente import SEGMENTOS, P
FPS_SRC = 30
os.makedirs("public/edit", exist_ok=True)
segs = []; t = 0.0
for a, b in SEGMENTOS:
    fa, fb = round(a * FPS_SRC), round(b * FPS_SRC)
    segs.append({"in": fa / FPS_SRC, "out": fb / FPS_SRC, "inFrame": fa, "outFrame": fb, "editStart": t})
    t += (fb - fa) / FPS_SRC
total = t

def concat_video(src, dst, extra_in, enc):
    parts = "".join(f"[0:v]trim=start_frame={s['inFrame']}:end_frame={s['outFrame']},setpts=PTS-STARTPTS[v{i}];" for i, s in enumerate(segs))
    chain = parts + "".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *extra_in, "-i", src, "-filter_complex", chain, "-map", "[out]", "-an", *enc, dst], check=True)

if "--sin-video" not in sys.argv:
    concat_video("public/proxy/ugc.mp4", "public/edit/aroll.mp4", [], ["-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30"])
    if os.path.exists("public/matte/ugc_persona.webm"):
        concat_video("public/matte/ugc_persona.webm", "public/edit/aroll_persona.webm", ["-c:v", "libvpx-vp9"],
                     ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M", "-deadline", "good", "-cpu-used", "4", "-row-mt", "1", "-auto-alt-ref", "0", "-r", "30"])

# Voz: cortes con microfundidos + limpieza + compresión + loudness
f = 0.012
parts = "".join(f"[0:a]atrim=start={s['in']}:end={s['out']},asetpts=PTS-STARTPTS,afade=t=in:d={f},afade=t=out:st={s['out']-s['in']-f:.4f}:d={f}[a{i}];" for i, s in enumerate(segs))
chain = parts + "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,highpass=f=85,afftdn=nf=-28,equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.5:g=2.5,acompressor=threshold=-21dB:ratio=3:attack=4:release=90:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "public/crudo/toma_ugc.mov", "-filter_complex", chain, "-map", "[out]", "-ar", "48000", "-ac", "2", "public/edit/voz.wav"], check=True)

# Palabras en tiempos de edición
palabras = []
for txt, a, b in P:
    seg = next((s for s in segs if s["in"] - 0.06 <= a < s["out"]), None)
    if seg is None:
        print("AVISO: palabra fuera de los segmentos:", txt, a); continue
    ea = seg["editStart"] + max(0, a - seg["in"])
    eb = seg["editStart"] + min(b, seg["out"]) - seg["in"]
    palabras.append({"text": txt, "startMs": round(ea * 1000), "endMs": round(max(eb, ea + 0.08) * 1000)})
json.dump({"duracionS": round(total, 4), "segmentos": [{"editStart": round(s["editStart"], 4), "in": s["in"], "out": s["out"]} for s in segs],
           "palabras": palabras}, open("src/datos/edicion.json", "w"), ensure_ascii=False, indent=1)
print(f"duración editada {total:.2f}s · {len(segs)} segmentos · {len(palabras)} palabras")
for s in segs: print(f"  edit {s['editStart']:6.2f}s  ← fuente {s['in']:.2f}-{s['out']:.2f}")
