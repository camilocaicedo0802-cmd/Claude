"""Día 8 · "Evaluación del Día 10" (a cámara): elige las tomas buenas, corta silencios y genera el vídeo editado.

Uso: python3 scripts/dia8/preparar.py <crudo.mp4 original> <crudo30.mp4> <transcripcion_completa.json> [--sin-video]

Como el día 3, pero las tomas pueden ir EN OTRO ORDEN que en el crudo (aquí el final de la primera toma de
"revisa si aparecieron moretones…" va detrás de la segunda), así que no sirve select (conserva el orden del
crudo): el vídeo se monta por tramos de fotogramas exactos y el audio con atrim + concat a muestra exacta.
Salidas: src/dia8/data/edit.json y public/dia8/editado.mp4 (audio ORIGINAL, sin normalizar).
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
# Fuera: los dos primeros intentos de "vuelve a calificar…" (20–42 s) y "vuelve a calificar la sensación de la piel"
# (45–48 s, se corrige enseguida) · "Toña" (63 s, fuera de guion) · el arranque "vas a tomarte las mismas" (71 s) ·
# la primera toma de "revisa si aparecieron moretones…" hasta "cambiarlo por otro" (92–102 s, repetida mejor a
# los 130 s) · "Además, revisa…" y el intento a medias de 125–129 s · silencio final.
TOMAS = [
    (5.20, 13.50),  # Felicitaciones, llegaste al día 10…
    (48.60, 56.30),  # vuelve a calificar la sensación de pesadez, la suavidad de la piel o cómo sigues percibiendo…
    (73.70, 82.20),  # vas a tomarte las mismas fotografías que el día número uno, de frente, de costado…
    (129.00, 138.70),  # revisa si aparecieron moretones, irritación y determina si es necesario suspender…
    (102.30, 106.30),  # de lo contrario puedes seguir con la rutina el resto de estos 10 días.
    (138.90, 148.20),  # Además recuerda: no estamos buscando perfección…
    (169.20, 178.70),  # Y recuerda calificar tus objetivos según la constancia…
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
    (RAIZ / "src/dia8/data").mkdir(parents=True, exist_ok=True)
    json.dump({"duration": duracion, "segments": salida, "words": words},
              open(RAIZ / "src/dia8/data/edit.json", "w"), ensure_ascii=False, indent=1)

    if "--sin-video" not in sys.argv:
        dst = RAIZ / "public/dia8/editado.mp4"
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
