"""Día 2 · "Punto de partida": elige las tomas buenas, corta silencios y genera el vídeo ya editado.

Uso: python3 scripts/dia2/preparar.py <crudo30.mov> <transcripcion.json> [--sin-video]
     <crudo30.mov>: el crudo convertido a 30 fps CFR (ver convertir.sh); el original es HEVC 10 bits a 59,94 fps.

Diferencias con scripts/preparar.py (día 1, que no se toca):
  - El crudo es 1080×1920: NO se recorta (un recorte obligaría a escalar y perder nitidez).
  - TOMAS: solo se conservan las tomas buenas; fuera los intentos fallidos y el "Listo, chao".
  - CORRECCIONES: palabras que Whisper fusionó al repetir la frase (se reescriben a mano).
Salidas: src/dia2/data/edit.json y public/dia2/editado.mp4 (audio ORIGINAL, sin normalizar).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preparar as base  # noqa: E402  (reutiliza silencios() y volumen_por_palabra() del día 1)

FPS = 30
HOLD = 0.7
RAIZ = Path(__file__).resolve().parent.parent.parent

# Tomas que se conservan (segundos del crudo). Lo que queda fuera:
#   0–9 s preparación · 27,8–48,9 s dos intentos fallidos de "usa un fondo neutro…" (el 2.º dice "medidas"
#   en vez de "foto") · 107,5–109,8 s "algo muy importante que también…" que vuelve a empezar ·
#   140,5 s "Listo. Chao".
TOMAS = [(9.10, 14.85), (54.35, 64.80), (74.40, 86.10), (109.84, 125.30), (132.00, 138.95)]

# Whisper fundió la frase repetida en una sola palabra "debes" (109,42–111,38): tiempos reales de la 2.ª toma
CORRECCIONES = [
    {"text": "algo", "start": 109.86, "end": 110.12},
    {"text": "muy", "start": 110.12, "end": 110.26},
    {"text": "importante", "start": 110.26, "end": 110.66},
    {"text": "que", "start": 110.66, "end": 110.84},
    {"text": "también", "start": 110.84, "end": 111.08},
    {"text": "debes", "start": 111.08, "end": 111.38},
]


def render_editado(src: str, tramos: list[tuple[int, int]], dst: Path) -> None:
    sel_v = "+".join(f"between(n,{a},{b - 1})" for a, b in tramos)
    sel_a = "+".join(f"between(t,{a / FPS:.6f},{b / FPS - 1e-6:.6f})" for a, b in tramos)
    filtro = (
        f"[0:v]select='{sel_v}',setpts=N/FRAME_RATE/TB,tpad=stop_mode=clone:stop_duration={HOLD}[v];"
        f"[0:a]asetnsamples=n=16:p=0,aselect='{sel_a}',asetpts=N/SR/TB,apad=pad_dur={HOLD}[a]"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    import subprocess
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(dst)],
        check=True,
    )


def main() -> None:
    src, trans = sys.argv[1], sys.argv[2]
    datos = json.load(open(trans))
    dentro = lambda t: any(a <= t <= b for a, b in TOMAS)  # noqa: E731
    palabras = [w for w in datos["words"] if dentro(w["start"]) and not (109.4 <= w["start"] < 111.38)]
    palabras = sorted(palabras + CORRECCIONES, key=lambda w: w["start"])

    sil = base.silencios(src)
    tramos_s = []
    for ta, tb in TOMAS:
        cursor = ta
        for s, e in sil:
            a, b = s + base.MARGEN, e - base.MARGEN
            if b <= cursor or a >= tb:
                continue
            if a > cursor:
                tramos_s.append((cursor, min(a, tb)))
            cursor = max(cursor, b)
        if cursor < tb:
            tramos_s.append((cursor, tb))
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
                return tr["outStart"]
            if t <= tr["srcEnd"]:
                return tr["outStart"] + t - tr["srcStart"]
        return duracion

    db = base.volumen_por_palabra(src, palabras)
    words = [
        {"text": w["text"], "start": round(mapear(w["start"]), 3), "end": round(mapear(w["end"]), 3), "db": d}
        for w, d in zip(palabras, db)
    ]
    edit = {"duration": duracion, "segments": salida, "words": words}
    (RAIZ / "src/dia2/data").mkdir(parents=True, exist_ok=True)
    json.dump(edit, open(RAIZ / "src/dia2/data/edit.json", "w"), ensure_ascii=False, indent=1)
    if "--sin-video" not in sys.argv:
        render_editado(src, tramos, RAIZ / "public/dia2/editado.mp4")
    print(f"{len(salida)} tramos · {len(salida) - 1} cortes · {datos['duration']:.2f}s → {duracion:.2f}s (+{HOLD}s final)")


if __name__ == "__main__":
    main()
