"""Día 10 (último del reto): música propia y efectos en public/dia10/audio/, más el obturador del día 2.

Reutiliza el sintetizador del día 1 (scripts/audio_marca.py) y el obturador de scripts/dia2/audio_dia2.py sin tocarlos.
Música de celebración, distinta de la de los días anteriores con los mismos timbres y la misma limpieza para la voz:
Sol mayor a 96 BPM (Gmaj9 · Em7 · Cmaj7 · D6), arpegio de piano eléctrico en corcheas que sube, campanas suaves en
el primer tiempo de cada compás y pandereta muy baja a contratiempo.
Uso: python -I scripts/dia10/audio_dia10.py
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ / "scripts/dia2"))
import audio_dia2  # noqa: E402  (fija am.OUT en public/dia2: se cambia justo después)
import audio_marca as am  # noqa: E402

np = am.np
am.OUT = RAIZ / "public/dia10/audio"


def musica10(duracion):
    bpm = 96
    beat = 60 / bpm
    compas = 4 * beat
    n = int((duracion + 2.5) * am.SR)
    mix = np.zeros((n, 2))
    acordes = [[55, 59, 62, 66], [52, 55, 59, 62], [52, 55, 59, 60], [50, 54, 57, 59]]  # Gmaj7 Em7 Cmaj7 D6
    bajos = [43, 40, 48, 38]
    total_compases = int(np.ceil(duracion / compas)) + 1
    fin_ritmo = duracion - 1.5

    def poner(señal, inicio):
        i = int(inicio * am.SR)
        if i >= n:
            return
        j = min(n, i + len(señal))
        mix[i:j] += señal[: j - i]

    for b in range(total_compases):
        t0 = b * compas
        ac = acordes[b % 4]
        dur = compas + 1.0
        tt = am.t_(dur)
        env = np.minimum(1, tt / 0.6) * np.clip((dur - tt) / 1.0, 0, 1)
        for nota in ac:
            for det, pan in ((-7, -0.6), (7, 0.6)):
                f = am.hz(nota) * 2 ** (det / 1200)
                s = sum(np.sin(2 * np.pi * f * h * tt + am.rng.uniform(0, 6.28)) / h ** 1.7 for h in range(1, 7))
                poner(am.estereo(s * env * 0.04, pan), t0)
        # Arpegio en corcheas que sube por el acorde (y la novena arriba en el último)
        for k, idx in enumerate([0, 1, 2, 3, 1, 2, 3, 0]):
            f = am.hz(ac[idx] + (24 if k == 7 else 12))
            tt = am.t_(1.0)
            vel = am.rng.uniform(0.55, 0.85)
            env = np.minimum(1, tt / 0.004) * np.exp(-tt / 0.38)
            s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.12)) * env * vel
            poner(am.estereo(s * 0.09, 0.35 if k % 2 else -0.35), t0 + k * beat / 2)
        # Campana suave en el primer tiempo (fundamental + parcial inarmónico), a partir del compás 2
        if b >= 1:
            tt = am.t_(2.4)
            f = am.hz(ac[3] + 24)
            env = np.minimum(1, tt / 0.003) * np.exp(-tt / 0.9)
            s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / 0.25)) * env
            poner(am.estereo(s * 0.035, 0.2), t0)
        if b >= 1:
            for tb in (0, 2, 3.5):
                largo = 1.4 if tb < 3 else 0.5
                tt = am.t_(beat * largo)
                env = np.minimum(1, tt / 0.01) * np.exp(-tt / 0.75) * np.clip((beat * largo - tt) / 0.08, 0, 1)
                f = am.hz(bajos[b % 4])
                s = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * env
                poner(am.estereo(s * 0.095), t0 + tb * beat)
        if b >= 2 and t0 < fin_ritmo:
            for tb in range(4):
                tg = t0 + tb * beat
                if tg > fin_ritmo:
                    break
                if tb in (0, 2):
                    tt = am.t_(0.35)
                    fase = 2 * np.pi * np.cumsum(46 + 72 * np.exp(-tt / 0.04)) / am.SR
                    poner(am.estereo(np.sin(fase) * np.exp(-tt / 0.12) * 0.11), tg)
                else:
                    c = am.filtro(am.ruido(0.18), "bandpass", [1200, 3500]) * np.exp(-am.t_(0.18) / 0.04)
                    poner(am.estereo(c * 0.08, 0.1), tg)
                # Pandereta a contratiempo
                p = am.filtro(am.ruido(0.12), "highpass", 7000) * np.exp(-am.t_(0.12) / 0.03)
                poner(am.estereo(p * 0.04, 0.45), tg + beat / 2)

    mix = am.reverb(mix, dur=2.6, decay=0.7, wet=0.32)
    mix = am.filtro(mix, "highpass", 70)
    mix = mix - 0.37 * am.filtro(mix, "bandpass", [1000, 3000])
    mix = mix[: int(duracion * am.SR)]
    tt = am.t_(duracion)
    mix *= (np.minimum(1, tt / 0.4) * np.clip((duracion - tt) / 1.5, 0, 1))[:, None]
    return np.tanh(mix * 1.4)


if __name__ == "__main__":
    duracion = json.load(open(RAIZ / "src/dia10/data/edit.json"))["duration"] + 0.7
    sys.argv = [sys.argv[0], str(duracion)]
    am.main()  # efectos de marca (y la música del día 1, que se sustituye a continuación)
    am.guardar("musica", musica10(duracion), pico_db=-1.0)
    am.guardar("obturador", audio_dia2.obturador())
