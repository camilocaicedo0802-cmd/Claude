"""Día 3 · "Preparación y uso seguro": elige las tomas buenas, corta silencios y genera el vídeo ya editado.

Uso: python3 scripts/dia3/preparar.py <crudo30.mov> <transcripcion.json> [--sin-video]
     <crudo30.mov>: el crudo convertido a 30 fps CFR (ver scripts/dia2/convertir.sh); el original es HEVC 10 bits a 59,94 fps.

Diferencias con scripts/preparar.py (día 1, que no se toca):
  - El crudo es 1080×1920: NO se recorta (un recorte obligaría a escalar y perder nitidez).
  - TOMAS: solo se conservan las tomas buenas; fuera los intentos fallidos y el "Listo, chao".
  - CORRECCIONES: palabras que Whisper fusionó al repetir la frase (se reescriben a mano).
Salidas: src/dia3/data/edit.json y public/dia3/editado.mp4 (audio ORIGINAL, sin normalizar).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preparar as base  # noqa: E402  (reutiliza silencios() y volumen_por_palabra() del día 1)

FPS = 30
HOLD = 0.7
RAIZ = Path(__file__).resolve().parent.parent.parent

# Tomas que se conservan (segundos del crudo). La transcripción (transcripcion.json) se hizo toma a toma.
# Fuera: 0–57 s charla fuera de guion · 82 s "antes de empezar… cosas no" (repetida) · los intentos de
# "tercero / tres…" de 156–178 s · "o no veo me ganado" · "quinto, siempre siempre vas a tener" y dos "quinto"
# incompletos (258 y 272 s) · "listo" / "gracias" del final.
TOMAS = [(91.40, 107.20), (126.80, 146.20), (183.90, 199.00), (226.20, 238.45), (279.85, 295.90), (304.40, 308.95)]
CORRECCIONES: list[dict] = []


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
    # Una palabra entra si se solapa con una toma (la primera de cada toma puede empezar unos ms antes)
    palabras = [w for w in datos["words"] if any(w["end"] > a and w["start"] < b for a, b in TOMAS)]
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
    (RAIZ / "src/dia3/data").mkdir(parents=True, exist_ok=True)
    json.dump(edit, open(RAIZ / "src/dia3/data/edit.json", "w"), ensure_ascii=False, indent=1)
    if "--sin-video" not in sys.argv:
        render_editado(src, tramos, RAIZ / "public/dia3/editado.mp4")
    print(f"{len(salida)} tramos · {len(salida) - 1} cortes · {datos['duration']:.2f}s → {duracion:.2f}s (+{HOLD}s final)")


if __name__ == "__main__":
    main()
