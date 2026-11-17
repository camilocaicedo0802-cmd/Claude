"""Recorta, iguala en color y convierte a 30 fps el b-roll de Mixkit.
card_*.mp4: 720x900 (4:5) para tarjetas; full_*.mp4: 1080x1920 para el montaje."""
import subprocess, os
ROOT = "/home/user/Claude/video-editor"
SRC = f"{ROOT}/assets_in/broll_web/src"
OUT = f"{ROOT}/public/broll"
os.makedirs(OUT, exist_ok=True)
MATCH = "eq=saturation=1.08:contrast=1.04,colorbalance=rs=0.02:bs=-0.03:rh=0.015:bh=-0.015"
# nombre, id, inicio, fin, tipo, x0 (px en la fuente)
JOBS = [
    ("card_filmmaker", "48778", 3.0, 7.0, "card", 500),
    ("card_editor", "50610", 0.5, 5.5, "card", 380),
    ("card_cm", "4908", 1.0, 6.0, "card", 1700),
    ("card_meta", "41278", 0.5, 5.5, "card", 1050),
    ("full_camara", "44076", 2.0, 4.2, "full", 1250),
    ("full_edicion", "50605", 3.0, 5.2, "full", 1300),
    ("full_movil", "1711", 3.0, 5.2, "full", 1300),
    ("full_analiticas", "41277", 1.0, 3.2, "full", 950),
    ("full_vlogger", "41269", 16.8, 19.0, "full", 1400),
    ("full_redes", "4908", 6.0, 8.2, "full", 1900),
]
for name, vid, a, b, kind, x0 in JOBS:
    src = f"{SRC}/{vid}.mp4"
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(","))
    if kind == "card":
        cw = int(h * 4 / 5); ow, oh = 720, 900
    else:
        cw = int(h * 9 / 16); ow, oh = 1080, 1920
    scale = w / 3840 if w < 3840 else 1
    x = min(max(0, int(x0 * scale)), w - cw)
    vf = f"crop={cw}:{h}:{x}:0,scale={ow}:{oh}:flags=lanczos,fps=30,{MATCH}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-i", src, "-t", str(b - a), "-an", "-vf", vf,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "15",
                    "-movflags", "+faststart", f"{OUT}/{name}.mp4"], check=True)
    print("ok", name, f"{w}x{h}", "crop x", x)
