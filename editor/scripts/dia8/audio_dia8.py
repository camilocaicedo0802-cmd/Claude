"""Día 8: música (con la duración del vídeo editado) y efectos en public/dia8/audio/, más el obturador del día 2.

Reutiliza el sintetizador del día 1 (scripts/audio_marca.py) y el obturador de scripts/dia2/audio_dia2.py sin tocarlos.
Uso: python -I scripts/dia8/audio_dia8.py
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ / "scripts/dia2"))
import audio_dia2  # noqa: E402  (fija am.OUT en public/dia2: se cambia justo después)
import audio_marca as am  # noqa: E402

am.OUT = RAIZ / "public/dia8/audio"

if __name__ == "__main__":
    duracion = json.load(open(RAIZ / "src/dia8/data/edit.json"))["duration"] + 0.7
    sys.argv = [sys.argv[0], str(duracion)]
    am.main()
    am.guardar("obturador", audio_dia2.obturador())
