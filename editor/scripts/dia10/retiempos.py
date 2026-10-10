"""Día 10 "Día 21 y continuidad": tiempos por palabra desde el vídeo YA EDITADO (public/dia10/editado.mp4).

Uso: python3 scripts/dia10/retiempos.py <transcripcion_del_editado.json>
     (la transcripción sale de: audio de public/dia10/editado.mp4 → scripts/transcribir.py)

Por qué: en el crudo Whisper fundió dos repeticiones (el doble "Felicitaciones, llegaste al día 21" y el "y lo más
importante, revisando cómo se va…" que se corta) en palabras de varios segundos; sobre el vídeo ya editado la
transcripción sale frase a frase y sin ellas. Si el inicio de una palabra cae dentro de un silencio o justo antes
(≤ 0,15 s; Whisper suele absorber la pausa anterior), se lleva al final del silencio.
Reescribe solo "words" de src/dia10/data/edit.json (duración y tramos siguen siendo los de preparar.py).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preparar as base  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    voz = str(RAIZ / "public/dia10/editado.mp4")
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
    ruta = RAIZ / "src/dia10/data/edit.json"
    edit = json.load(open(ruta))
    edit["words"] = [{**w, "db": d} for w, d in zip(palabras, db)]
    json.dump(edit, open(ruta, "w"), ensure_ascii=False, indent=1)
    print(f"{len(palabras)} palabras · {edit['duration']:.2f}s")


if __name__ == "__main__":
    main()
