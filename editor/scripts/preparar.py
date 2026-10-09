"""Prepara el borrador: corta silencios > 0,3 s y reasigna los tiempos por palabra.

Uso: python3 scripts/preparar.py <audio_o_video_crudo> <transcripcion.json>

Salidas:
  src/data/edit.json         tramos que se conservan + palabras en la línea de tiempo editada
  public/crudo/voz.m4a       voz normalizada a -14 LUFS / -1 dBTP (misma línea de tiempo que el crudo)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SILENCIO_MIN = 0.30  # s: todo silencio más largo se corta (estilo.md §2)
UMBRAL_DB = -35  # dB: suelo ≈ -58 dB, voz ≈ -23 dB; a -35 también caen las respiraciones
MARGEN = 0.08  # s de aire que se deja a cada lado del corte para no comerse sílabas
COLA = 1.0  # s que se conservan tras la última palabra (deja respirar el «Día 1» final)

RAIZ = Path(__file__).resolve().parent.parent


def silencios(src: str) -> list[tuple[float, float]]:
    out = subprocess.run(
        ["ffmpeg", "-i", src, "-af", f"silencedetect=noise={UMBRAL_DB}dB:d={SILENCIO_MIN}", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    return list(zip(starts, ends))


def normalizar(src: str, dst: Path) -> None:
    medir = subprocess.run(
        ["ffmpeg", "-i", src, "-vn", "-af", "loudnorm=I=-14:TP=-1:LRA=7:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    m = json.loads(medir[medir.rindex("{"):])
    filtro = (
        "loudnorm=I=-14:TP=-1:LRA=7:linear=true:"
        f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
        f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-af", filtro, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(dst)],
        check=True,
    )


def main() -> None:
    src, trans = sys.argv[1], sys.argv[2]
    datos = json.load(open(trans))
    palabras = datos["words"]
    inicio = max(0.0, palabras[0]["start"] - 0.10)
    fin = min(datos["duration"], palabras[-1]["end"] + COLA)

    # Tramos que se conservan = [inicio, fin] menos cada silencio (dejando MARGEN a cada lado)
    tramos, cursor = [], inicio
    for s, e in silencios(src):
        a, b = s + MARGEN, e - MARGEN
        if b <= cursor or a >= fin:
            continue
        if a > cursor:
            tramos.append([cursor, a])
        cursor = max(cursor, b)
    tramos.append([cursor, fin])
    tramos = [[round(a, 3), round(b, 3)] for a, b in tramos if b - a > 0.05]

    # Reasignar cada palabra a la línea de tiempo editada
    salida, t_out = [], 0.0
    for a, b in tramos:
        salida.append({"srcStart": a, "srcEnd": b, "outStart": round(t_out, 3)})
        t_out += b - a

    def mapear(t: float) -> float:
        for tr in salida:
            if t < tr["srcStart"]:
                return tr["outStart"]  # cae en un silencio cortado: se pega al siguiente tramo
            if t <= tr["srcEnd"]:
                return tr["outStart"] + t - tr["srcStart"]
        last = salida[-1]
        return last["outStart"] + last["srcEnd"] - last["srcStart"]

    words = [
        {"text": w["text"], "start": round(mapear(w["start"]), 3), "end": round(mapear(w["end"]), 3)}
        for w in palabras
    ]
    edit = {"duration": round(t_out, 3), "segments": salida, "words": words}
    (RAIZ / "src/data").mkdir(parents=True, exist_ok=True)
    json.dump(edit, open(RAIZ / "src/data/edit.json", "w"), ensure_ascii=False, indent=1)
    normalizar(src, RAIZ / "public/crudo/voz.m4a")
    cortado = datos["duration"] - t_out
    print(f"{len(salida)} tramos · {len(salida) - 1} cortes · {datos['duration']:.2f}s → {t_out:.2f}s (−{cortado:.2f}s)")


if __name__ == "__main__":
    main()
