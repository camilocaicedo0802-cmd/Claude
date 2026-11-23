"""B-roll en horizontal (16:10, como la ventana de la opción B) → public/media/broll/brh_*.mp4

Son los mismos clips y los mismos tramos que el b-roll vertical de la opción A, con otro recorte.
"""
import os
import re
import subprocess
import unicodedata

SRC = "material/drive/RECURSOS"
files = {unicodedata.normalize("NFC", re.sub(r"^(Copia de )+", "", f)[:-4]): os.path.join(SRC, f) for f in os.listdir(SRC)}

PLAN = [  # salida, fuente, inicio (s), duración (s), recorte
    ("brh_casting", files["c63"], 3.1, 2.1, "crop=1080:676:0:520"),
    ("brh_ojo", files["Vídeo (7)"], 0.2, 2.6, "crop=1080:676:0:622"),
    ("brh_partitura", "material/stock/mk_41678_4k.mp4", 2.6, 3.6, "crop=3456:2160:192:0"),
    ("brh_actriz", "material/stock/mk_43403_4k.mp4", 8.9, 2.6, "crop=3456:2160:230:0"),
]
for out, path, ss, dur, crop in PLAN:
    dst = f"public/media/broll/{out}.mp4"
    vf = crop + ",scale=1600:1000:flags=lanczos,fps=30,format=yuv420p"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(dur), "-i", path, "-vf", vf, "-an", "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-g", "15", dst], check=True, stdin=subprocess.DEVNULL)
    print(out, os.path.getsize(dst) // 1000, "KB")
