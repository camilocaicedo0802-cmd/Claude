"""Día 10: b-roll de la rutina para "debes seguir repitiendo esta misma rutina de aquí en adelante".

Uso: python3 scripts/dia10/apoyos.py <crudo_30 del día 9>
Cuatro fragmentos cortos (≈0,9 s) del crudo del día 9 —piernas, abdomen, glúteos y brazos con el equipo—, sin
escalar, uno detrás de otro: public/dia10/rutina.mp4 (sin audio) y src/dia10/data/rutina.json (zona y fotograma
de inicio de cada fragmento dentro del archivo).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
FPS = 30
# (zona, segundo del crudo del día 9, fotogramas): el equipo se ve trabajando y ella no mira a cámara
FRAGMENTOS = [("piernas", 116.4, 26), ("abdomen", 196.6, 26), ("glúteos", 240.6, 26), ("brazos", 487.4, 28)]


def main() -> None:
    crudo = sys.argv[1]
    dst = RAIZ / "public/dia10/rutina.mp4"
    info, f0 = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        with open(lista, "w") as fl:
            for i, (zona, s, n) in enumerate(FRAGMENTOS):
                parte = Path(tmp) / f"r{i}.mp4"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.4f}", "-i", crudo, "-frames:v", str(n), "-an",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p",
                                "-r", str(FPS), str(parte)], check=True)
                fl.write(f"file '{parte}'\n")
                info.append({"zona": zona, "desde": f0, "frames": n})
                f0 += n
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
                        "-movflags", "+faststart", str(dst)], check=True)
    json.dump(info, open(RAIZ / "src/dia10/data/rutina.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(info)} fragmentos · {f0} fotogramas")


if __name__ == "__main__":
    main()
