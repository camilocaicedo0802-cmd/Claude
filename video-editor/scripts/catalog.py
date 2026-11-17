"""Cataloga clips: miniatura del fotograma central + metadatos.
Uso: python3 -I catalog.py <carpeta> <salida_dir>"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
src, out = sys.argv[1], sys.argv[2]
os.makedirs(f"{out}/thumbs", exist_ok=True)
files = sorted([f for f in os.listdir(src) if f.lower().endswith((".mp4", ".mov"))],
               key=lambda s: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)])
def one(f):
    p = os.path.join(src, f)
    name = re.sub(r"(Copia de )+", "", f).rsplit(".", 1)[0].replace("(", "").replace(")", "")
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                                    "-of", "json", p], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout or "{}")
    v = next((s for s in pr.get("streams", []) if s.get("codec_type") == "video"), {})
    has_a = any(s.get("codec_type") == "audio" for s in pr.get("streams", []))
    d = float(pr.get("format", {}).get("duration", 0) or 0)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(d / 2), "-i", p, "-frames:v", "1", "-vf",
                    "scale=180:320:force_original_aspect_ratio=decrease,pad=180:320:(ow-iw)/2:(oh-ih)/2,"
                    f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{name}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.8",
                    f"{out}/thumbs/{name}.jpg"], stdin=subprocess.DEVNULL)
    return {"name": name, "file": f, "dur": round(d, 2), "w": v.get("width"), "h": v.get("height"), "fps": v.get("r_frame_rate"), "audio": has_a}
with ThreadPoolExecutor(4) as ex:
    rows = list(ex.map(one, files))
json.dump(rows, open(f"{out}/meta.json", "w"), indent=1)
from collections import Counter
print(len(rows), "clips; resoluciones:", Counter(f"{r['w']}x{r['h']}" for r in rows).most_common(6))
print("duración total:", round(sum(r["dur"] for r in rows), 1), "s; con audio:", sum(r["audio"] for r in rows))
