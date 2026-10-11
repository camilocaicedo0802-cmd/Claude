"""Día 10: apoyos sacados de otros crudos.

Uso: python3 scripts/dia10/apoyos.py <crudo_30 del día 9> <toma de apoyo del día 2>

1. Fotos de control ("vas a tomarte una foto de frente, de costado, de espalda y luego del otro costado"): las MISMAS
   escenas de la toma de apoyo del día 2 que el día 8 (frente 3,30 s · costado 16,45 s · espalda 13,40 s · el otro
   costado 8,60 s; corrección del usuario: nada de fotogramas de otros crudos). 1,2 s de cada una, en movimiento
   dentro del visor del móvil: secuencias de JPEG en public/dia10/fotos_dia2/<pose>/00.jpg… (668×1188, el visor).
2. B-roll de la rutina para "debes seguir repitiendo esta misma rutina de aquí en adelante": cuatro fragmentos cortos
   (≈0,9 s) del crudo del día 9 —piernas, abdomen y glúteos con el equipo, brazos con las manos—, reencuadrados como
   en el día 9 (el borde derecho del crudo deja ver el cuarto de al lado), uno detrás de otro: public/dia10/rutina.mp4
   (sin audio), su secuencia de JPEG en public/dia10/rutina_fotogramas/0000.jpg… y src/dia10/data/rutina.json (zona y
   fotograma de inicio de cada fragmento).
Remotion solo lee los JPEG: el Chromium del entorno no decodifica H.264.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
PUB = RAIZ / "public/dia10"
FPS = 30
# (zona, segundo del crudo del día 9, fotogramas): trabaja la zona, cómoda, y no mira a cámara ni a quien graba
FRAGMENTOS = [("piernas", 116.4, 26), ("abdomen", 196.6, 26), ("glúteos", 240.6, 26), ("brazos", 537.2, 28)]
ENCUADRE = "crop=960:1707:0:160,scale=1080:1920:flags=lanczos,setsar=1"  # el mismo del día 9 (scripts/dia9/montar.py)
# pose: segundo de la toma de apoyo del día 2 (los mismos que scripts/dia8/apoyos.py)
FOTOS = {"frente": 3.30, "costado": 16.45, "espalda": 13.40, "otro": 8.60}
FOTO_SEG = 1.2


def jpeg(src: str, carpeta: Path, patron: str, filtros: list[str]) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    for f in carpeta.glob("*.jpg"):
        f.unlink()
    subprocess.run(["ffmpeg", "-v", "error", "-y", *filtros[:-1], "-i", src, "-an", "-vf", filtros[-1], "-q:v", "2",
                    "-start_number", "0", str(carpeta / patron)], check=True)


def main() -> None:
    crudo9, apoyo2 = sys.argv[1], sys.argv[2]
    for pose, s in FOTOS.items():
        jpeg(apoyo2, PUB / "fotos_dia2" / pose, "%02d.jpg",
             ["-ss", f"{s:.2f}", "-t", f"{FOTO_SEG}", f"fps={FPS},scale=668:1188:flags=lanczos"])
    print(f"fotos del día 2: {', '.join(FOTOS)} ({round(FOTO_SEG * FPS)} fotogramas cada una)")

    dst = PUB / "rutina.mp4"
    info, f0 = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        with open(lista, "w") as fl:
            for i, (zona, s, n) in enumerate(FRAGMENTOS):
                parte = Path(tmp) / f"r{i}.mp4"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.4f}", "-i", crudo9, "-frames:v", str(n), "-an",
                                "-vf", ENCUADRE, "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15",
                                "-pix_fmt", "yuv420p", "-r", str(FPS), str(parte)], check=True)
                fl.write(f"file '{parte}'\n")
                info.append({"zona": zona, "desde": f0, "frames": n})
                f0 += n
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
                        "-movflags", "+faststart", str(dst)], check=True)
    jpeg(str(dst), PUB / "rutina_fotogramas", "%04d.jpg", ["null"])
    json.dump(info, open(RAIZ / "src/dia10/data/rutina.json", "w"), ensure_ascii=False, indent=1)
    print(f"rutina: {len(info)} fragmentos · {f0} fotogramas")


if __name__ == "__main__":
    main()
