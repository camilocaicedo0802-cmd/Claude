"""Día 10 · "Día 21 y continuidad" (a cámara): elige las tomas buenas, corta silencios y genera el vídeo editado.

Uso: python3 scripts/dia10/preparar.py <crudo.mp4 original> <crudo30.mov> <transcripcion_completa.json> [--sin-video]

Mismo método que el día 8 (scripts/dia8/preparar.py): el vídeo se monta por tramos de fotogramas exactos y el audio
con atrim + concat a muestra exacta. Salidas: src/dia10/data/edit.json y public/dia10/editado.mp4 (audio ORIGINAL,
sin normalizar). Los tiempos por palabra se afinan después con scripts/dia10/retiempos.py.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preparar as base  # noqa: E402  (silencios() y volumen_por_palabra() del día 1)

FPS = 30
HOLD = 0.7
SR = 48000
RAIZ = Path(__file__).resolve().parent.parent.parent

# Tomas que se conservan (segundos del crudo), en el orden en que van en el vídeo.
# Fuera: el primer "Felicitaciones, llegaste al día 21" (1,5–3,7 s, lo repite enseguida y la segunda enlaza con
# "y más allá…") · 42–69 s (espera en silencio y voces de fondo: "Antonia") · el primer "y lo más importante,
# revisando cómo se va a…" (85,5–88,5 s, se corta y lo repite completo; Whisper lo funde en un "comportando" de
# 4,5 s) · 93–116 s (silencio, un "y ya está" casi inaudible y "¡María Antonia!" de fondo) · el primer "ahora
# cuéntanos" (114,2–115,1 s), que se corta y se repite completo · silencio final.
TOMAS = [
    (4.45, 42.45),  # Felicitaciones, llegaste al día 21… o qué más te importaba.
    (69.30, 84.75),  # Compara tus registros con los anteriores… respetando las instrucciones del producto.
    (89.45, 93.25),  # Y lo más importante, revisando cómo se va comportando tu piel y tu cuerpo.
    (116.60, 127.80),  # Ahora cuéntanos vía WhatsApp… hacer de su cuidado corporal una rutina.
]


def main() -> None:
    crudo, crudo30, trans = sys.argv[1], sys.argv[2], sys.argv[3]
    datos = json.load(open(trans))
    sil = base.silencios(crudo)

    # Tramos (con su toma) dentro de cada toma, sin los silencios de más de 0,3 s (margen del día 1)
    tramos = []
    for k, (ta, tb) in enumerate(TOMAS):
        cursor = ta
        for s, e in sil:
            a, b = s + base.MARGEN, e - base.MARGEN
            if b <= cursor or a >= tb:
                continue
            if a > cursor:
                tramos.append((k, cursor, min(a, tb)))
            cursor = max(cursor, b)
        if cursor < tb:
            tramos.append((k, cursor, tb))
    # A fotograma exacto
    tramos = [(k, round(a * FPS), round(b * FPS)) for k, a, b in tramos]
    tramos = [(k, a, b) for k, a, b in tramos if b - a >= 2]

    salida, f_out = [], 0
    for k, a, b in tramos:
        salida.append({"toma": k, "srcStart": a / FPS, "srcEnd": b / FPS, "outStart": f_out / FPS})
        f_out += b - a
    duracion = f_out / FPS

    def mapear(k: int, t: float) -> float:
        propios = [tr for tr in salida if tr["toma"] == k]
        for tr in propios:
            if t < tr["srcStart"]:
                return tr["outStart"]
            if t <= tr["srcEnd"]:
                return tr["outStart"] + t - tr["srcStart"]
        ult = propios[-1]
        return ult["outStart"] + ult["srcEnd"] - ult["srcStart"]

    palabras = []
    for k, (ta, tb) in enumerate(TOMAS):
        for w in datos["words"]:
            if w["end"] > ta and w["start"] < tb:
                palabras.append((k, w))
    db = base.volumen_por_palabra(crudo, [w for _, w in palabras])
    words = [
        {"text": w["text"], "start": round(mapear(k, w["start"]), 3), "end": round(mapear(k, w["end"]), 3), "db": d}
        for (k, w), d in zip(palabras, db)
    ]
    words.sort(key=lambda w: w["start"])
    (RAIZ / "src/dia10/data").mkdir(parents=True, exist_ok=True)
    json.dump({"duration": duracion, "segments": salida, "words": words},
              open(RAIZ / "src/dia10/data/edit.json", "w"), ensure_ascii=False, indent=1)

    if "--sin-video" not in sys.argv:
        dst = RAIZ / "public/dia10/editado.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            lista = Path(tmp) / "lista.txt"
            with open(lista, "w") as fl:
                for i, (k, a, b) in enumerate(tramos):
                    parte = Path(tmp) / f"v{i:03d}.mp4"
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a / FPS:.4f}", "-i", crudo30, "-frames:v", str(b - a),
                                    "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p",
                                    "-r", str(FPS), str(parte)], check=True)
                    fl.write(f"file '{parte}'\n")
            video = Path(tmp) / "video.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(video)], check=True)
            # Audio a muestra exacta (mismos límites que los fotogramas) + silencio final de HOLD
            filtro = "".join(f"[0:a]atrim=start={a / FPS:.6f}:end={b / FPS:.6f},asetpts=N/SR/TB[t{i}];" for i, (_, a, b) in enumerate(tramos))
            filtro += "".join(f"[t{i}]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=0:a=1,apad=pad_dur={HOLD}[a]"
            audio = Path(tmp) / "audio.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", crudo, "-filter_complex", filtro, "-map", "[a]", "-ar", str(SR),
                            "-c:a", "pcm_s16le", str(audio)], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(audio), "-filter_complex",
                            f"[0:v]tpad=stop_mode=clone:stop_duration={HOLD}[v]", "-map", "[v]", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(dst)], check=True)
    print(f"{len(salida)} tramos · {datos['duration']:.2f}s → {duracion:.2f}s (+{HOLD}s final)")


if __name__ == "__main__":
    main()
