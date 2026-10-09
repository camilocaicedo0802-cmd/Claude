"""Día 3: música (con la duración del vídeo editado del día 3) y efectos en public/dia3/audio/.

Reutiliza el sintetizador del día 1 (scripts/audio_marca.py) sin tocarlo y añade el efecto
"obturador" (clic de cámara) para las tres fotos de perfil, frente y espalda.
Uso: python -I scripts/dia3/audio_dia3.py
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import audio_marca as am  # noqa: E402

am.OUT = RAIZ / "public/dia3/audio"


def obturador():
    """Clic de cámara: espejo que sube (ruido filtrado corto) + cortinilla que cae 70 ms después."""
    np = am.np
    x = np.zeros(int(0.5 * am.SR))
    for t0, f, g in [(0.0, [2500, 9000], 1.0), (0.07, [1200, 6000], 0.8)]:
        tt = am.t_(0.035)
        s = am.filtro(am.ruido(0.035), "bandpass", f) * np.exp(-tt / 0.008) * g
        i = int(t0 * am.SR)
        x[i:i + len(s)] += s
    cuerpo = np.sin(2 * np.pi * 180 * am.t_(0.06)) * np.exp(-am.t_(0.06) / 0.015) * 0.4
    x[:len(cuerpo)] += cuerpo
    return am.reverb(am.estereo(x, 0.1), dur=0.4, decay=0.08, wet=0.12)


if __name__ == "__main__":
    duracion = json.load(open(RAIZ / "src/dia3/data/edit.json"))["duration"] + 0.7
    sys.argv = [sys.argv[0], str(duracion)]
    am.main()
    am.guardar("obturador", obturador())
