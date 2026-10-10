"""Días 4, 5 y 6: música (con la duración de la voz en off editada) y efectos en public/<dia>/audio/.

Reutiliza el sintetizador del día 1 (scripts/audio_marca.py) sin tocarlo.
Uso: python -I scripts/rutinas/audio.py <dia4|dia5|dia6>
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import audio_marca as am  # noqa: E402

if __name__ == "__main__":
    dia = sys.argv[1]
    am.OUT = RAIZ / f"public/{dia}/audio"
    duracion = json.load(open(RAIZ / f"src/{dia}/data/edit.json"))["duration"] + 0.7
    sys.argv = [sys.argv[0], str(duracion)]
    am.main()
