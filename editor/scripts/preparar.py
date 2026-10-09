"""Prepara el borrador: corta silencios > 0,3 s y genera el vídeo ya editado con su audio original.

Uso: python3 scripts/preparar.py <video_crudo> <transcripcion.json> [--sin-video]
     --sin-video: solo regenera src/data/edit.json (no vuelve a renderizar editado.mp4)

Salidas:
  src/data/edit.json           tramos conservados (a fotograma exacto) + palabras en la línea de tiempo editada,
                               cada una con "db": su pico de volumen respecto a la mediana de la voz (para los zooms)
  public/crudo/editado.mp4     vídeo recortado del 4K (1620×2880) con los silencios ya quitados y el audio
                               ORIGINAL del vídeo (sin normalizar); congela el último fotograma HOLD segundos
"""
import array
import json
import math
import re
import subprocess
import sys
from pathlib import Path

FPS = 30
SILENCIO_MIN = 0.30  # s: todo silencio más largo se corta (estilo.md §2)
UMBRAL_DB = -35  # dB: suelo ≈ -58 dB, voz ≈ -23 dB; a -35 también caen las respiraciones
MARGEN = 0.08  # s de aire que se deja a cada lado del corte para no comerse sílabas
COLA = 1.0  # s que se conservan tras la última palabra
HOLD = 0.7  # s de último fotograma congelado al final (debe coincidir con HOLD en src/lib/timing.ts)
RECORTE = "crop=1620:2880:270:268"  # plano medio sacado del 4K sin escalar (estilo.md §11)

RAIZ = Path(__file__).resolve().parent.parent


def silencios(src: str) -> list[tuple[float, float]]:
    out = subprocess.run(
        ["ffmpeg", "-i", src, "-vn", "-af", f"silencedetect=noise={UMBRAL_DB}dB:d={SILENCIO_MIN}", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    return list(zip(starts, ends))


def volumen_por_palabra(src: str, palabras: list[dict]) -> list[float]:
    """Pico de RMS (ventanas de 50 ms) de cada palabra, en dB respecto a la mediana de todas las palabras."""
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    a = array.array("h")
    a.frombytes(pcm)
    picos = []
    for w in palabras:
        i0, i1 = int(w["start"] * 16000), int(w["end"] * 16000)
        mejor = 1e-9
        for j in range(i0, max(i0 + 1, i1 - 800), 400):
            v = a[j:j + 800]
            if v:
                mejor = max(mejor, math.sqrt(sum(x * x for x in v) / len(v)) / 32768)
        picos.append(20 * math.log10(mejor))
    mediana = sorted(picos)[len(picos) // 2]
    return [round(p - mediana, 1) for p in picos]


def render_editado(src: str, tramos: list[tuple[int, int]], dst: Path) -> None:
    """Corta vídeo y audio con los mismos límites (en fotogramas) en una sola pasada."""
    sel_v = "+".join(f"between(n,{a},{b - 1})" for a, b in tramos)
    sel_a = "+".join(f"between(t,{a / FPS:.6f},{b / FPS - 1e-6:.6f})" for a, b in tramos)
    filtro = (
        f"[0:v]{RECORTE},select='{sel_v}',setpts=N/FRAME_RATE/TB,tpad=stop_mode=clone:stop_duration={HOLD}[v];"
        f"[0:a]aselect='{sel_a}',asetpts=N/SR/TB,apad=pad_dur={HOLD}[a]"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-g", "15", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(dst)],
        check=True,
    )


def main() -> None:
    src, trans = sys.argv[1], sys.argv[2]
    datos = json.load(open(trans))
    palabras = datos["words"]
    inicio = max(0.0, palabras[0]["start"] - 0.10)
    fin = min(datos["duration"], palabras[-1]["end"] + COLA)

    # Tramos que se conservan = [inicio, fin] menos cada silencio (dejando MARGEN a cada lado)
    tramos_s, cursor = [], inicio
    for s, e in silencios(src):
        a, b = s + MARGEN, e - MARGEN
        if b <= cursor or a >= fin:
            continue
        if a > cursor:
            tramos_s.append((cursor, a))
        cursor = max(cursor, b)
    tramos_s.append((cursor, fin))
    # A fotograma exacto: vídeo y audio cortan en el mismo instante
    tramos = [(round(a * FPS), round(b * FPS)) for a, b in tramos_s]
    tramos = [(a, b) for a, b in tramos if b - a >= 2]

    salida, f_out = [], 0
    for a, b in tramos:
        salida.append({"srcStart": a / FPS, "srcEnd": b / FPS, "outStart": f_out / FPS})
        f_out += b - a
    duracion = f_out / FPS

    def mapear(t: float) -> float:
        for tr in salida:
            if t < tr["srcStart"]:
                return tr["outStart"]  # cae en un silencio cortado: se pega al siguiente tramo
            if t <= tr["srcEnd"]:
                return tr["outStart"] + t - tr["srcStart"]
        return duracion

    db = volumen_por_palabra(src, palabras)
    words = [
        {"text": w["text"], "start": round(mapear(w["start"]), 3), "end": round(mapear(w["end"]), 3), "db": d}
        for w, d in zip(palabras, db)
    ]
    edit = {"duration": duracion, "segments": salida, "words": words}
    (RAIZ / "src/data").mkdir(parents=True, exist_ok=True)
    json.dump(edit, open(RAIZ / "src/data/edit.json", "w"), ensure_ascii=False, indent=1)
    if "--sin-video" not in sys.argv:
        render_editado(src, tramos, RAIZ / "public/crudo/editado.mp4")
    print(f"{len(salida)} tramos · {len(salida) - 1} cortes · {datos['duration']:.2f}s → {duracion:.2f}s (+{HOLD}s final)")


if __name__ == "__main__":
    main()
