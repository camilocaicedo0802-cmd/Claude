"""Día 9 "Rutina integrada": tiempos por palabra desde la voz en off YA LIMPIA (public/dia9/voz.wav).

Uso: python3 scripts/dia9/retiempos.py <transcripcion_de_voz_limpia.json>
     (la transcripción sale de: <venv>/bin/python -I scripts/transcribir.py public/dia9/voz.wav <salida.json>)

Por qué: en la grabación original Whisper fundió los primeros 33 s en un solo segmento (con la toma repetida de
"Aplica el aceite…") y sus tiempos por palabra salían hasta 1 s adelantados; además la palabra que tocaba el borde
de una toma descartada se colaba duplicada. Sobre la voz limpia la transcripción sale frase a frase. Si el inicio de
una palabra cae dentro de un silencio o justo antes (≤ 0,15 s; Whisper suele absorber la pausa anterior), se lleva
al final del silencio.
Reescribe solo "words" de src/dia9/data/edit.json (duración y tramos siguen siendo los de preparar_voz.py).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preparar as base  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    voz = str(RAIZ / "public/dia9/voz.wav")
    datos = json.load(open(sys.argv[1]))
    sil = base.silencios(voz)
    palabras = []
    for w in datos["words"]:
        s, e = w["start"], w["end"]
        for a, b in sil:
            if a - 0.15 <= s < b < e:  # también si la pausa empieza justo después (≤ 0,15 s)
                s = b
        palabras.append({"text": w["text"], "start": round(s, 3), "end": round(e, 3)})
    db = base.volumen_por_palabra(voz, palabras)
    ruta = RAIZ / "src/dia9/data/edit.json"
    edit = json.load(open(ruta))
    edit["words"] = [{**w, "db": d} for w, d in zip(palabras, db)]
    json.dump(edit, open(ruta, "w"), ensure_ascii=False, indent=1)
    print(f"{len(palabras)} palabras · {edit['duration']:.2f}s")


if __name__ == "__main__":
    main()
