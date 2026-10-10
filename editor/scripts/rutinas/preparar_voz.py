"""Días 4 a 7 (rutinas con voz en off): limpia la voz en off y genera su línea de tiempo.

Uso: python3 scripts/rutinas/preparar_voz.py <dia4|dia5|dia6|dia7> <voz.m4a>
Salidas: public/<dia>/voz.wav (voz ORIGINAL sin normalizar, solo cortada) y src/<dia>/data/edit.json (palabras en
la línea de tiempo editada, con su volumen relativo "db").

- TOMAS: solo las frases buenas de la grabación (fuera repeticiones y frases que se reinician).
- Silencios: se cortan los de más de 0,3 s (estilo.md §2) dejando 0,15 s a cada lado: la voz en off respira un poco
  más que un corte a cámara, porque encima va la toma de apoyo.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preparar as base  # noqa: E402  (silencios() y volumen_por_palabra() del día 1)

RAIZ = Path(__file__).resolve().parent.parent.parent
MARGEN = 0.15
SR = 48000

TOMAS = {
    # Fuera: "Cambiamos al otro muslo" (72–77,6 s, se repite completa después) y "Durante tres minutos y recuerda,
    # debe deslizarse fácilmente" (97,9–106,5 s, repetida enseguida); el silencio de 14 s antes del cierre se corta solo.
    "dia4": [(1.90, 72.00), (77.60, 97.90), (106.50, 137.90), (151.30, 172.10)],
    # Fuera: "Ahora vamos otros tres minutos hacia el lateral izquierdo. Vas a repetir." (69,6–76,9 s, repetida) y el
    # bloque 110,2–134,7 s que repite el cierre con un error ("para realizar").
    "dia5": [(0.85, 69.60), (76.90, 110.20), (134.70, 148.90)],
    # Fuera: el primer "Ahora vamos a repetir la misma secuencia en el muslo izquierdo. Tres minutos de barridos y
    # tres." (57,3–67,2 s), que se corta a mitad y se repite completo enseguida.
    "dia6": [(1.50, 56.30), (69.30, 125.20)],
    # Sin repeticiones; fuera solo el ruido final que Whisper lee como "Gracias" (77,9 s).
    "dia7": [(1.50, 77.45)],
}


def main() -> None:
    dia, src = sys.argv[1], sys.argv[2]
    tomas = TOMAS[dia]
    datos = json.load(open(RAIZ / f"scripts/rutinas/voz_{dia}.json"))
    palabras = [w for w in datos["words"] if any(w["end"] > a and w["start"] < b for a, b in tomas)]

    tramos = []
    sil = base.silencios(src)
    for ta, tb in tomas:
        cursor = ta
        for s, e in sil:
            a, b = s + MARGEN, e - MARGEN
            if b <= cursor or a >= tb:
                continue
            if a > cursor:
                tramos.append((cursor, min(a, tb)))
            cursor = max(cursor, b)
        if cursor < tb:
            tramos.append((cursor, tb))
    tramos = [(a, b) for a, b in tramos if b - a > 0.05]

    salida, t = [], 0.0
    for a, b in tramos:
        salida.append({"srcStart": round(a, 4), "srcEnd": round(b, 4), "outStart": round(t, 4)})
        t += b - a
    duracion = t

    def mapear(x: float) -> float:
        for tr in salida:
            if x < tr["srcStart"]:
                return tr["outStart"]
            if x <= tr["srcEnd"]:
                return tr["outStart"] + x - tr["srcStart"]
        return duracion

    db = base.volumen_por_palabra(src, palabras)
    words = [{"text": w["text"], "start": round(mapear(w["start"]), 3), "end": round(mapear(w["end"]), 3), "db": d} for w, d in zip(palabras, db)]
    (RAIZ / f"src/{dia}/data").mkdir(parents=True, exist_ok=True)
    json.dump({"duration": duracion, "segments": salida, "words": words}, open(RAIZ / f"src/{dia}/data/edit.json", "w"), ensure_ascii=False, indent=1)

    # Corte a muestra exacta con atrim + concat (sin aselect: no hay vídeo con el que alinear y así no hay bloques)
    filtro = "".join(f"[0:a]atrim=start={a:.5f}:end={b:.5f},asetpts=N/SR/TB[t{i}];" for i, (a, b) in enumerate(tramos))
    filtro += "".join(f"[t{i}]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=0:a=1[a]"
    dst = RAIZ / f"public/{dia}/voz.wav"
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", filtro, "-map", "[a]", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)
    print(f"{dia}: {len(tramos)} tramos · {datos['duration']:.1f}s → {duracion:.2f}s")


if __name__ == "__main__":
    main()
