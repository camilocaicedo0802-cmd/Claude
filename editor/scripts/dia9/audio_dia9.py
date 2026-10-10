"""Día 9: música propia (variación de la del día 1) y efectos en public/dia9/audio/, más el obturador del día 2.

Reutiliza el sintetizador del día 1 (scripts/audio_marca.py) y el obturador de scripts/dia2/audio_dia2.py sin tocarlos.
Para que no suene igual que los días anteriores, la música cambia de tonalidad, tempo y figura (mismos timbres y la
misma limpieza para la voz): Re mayor a 92 BPM (Dmaj7 · Bm7 · Gmaj7 · A7sus4), arpegio sincopado en semicorcheas
tipo marimba y palmada suave en el 4.
Uso: python -I scripts/dia9/audio_dia9.py
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
am.OUT = RAIZ / "public/dia9/audio"


def musica9(duracion):
    bpm = 92
    beat = 60 / bpm
    compas = 4 * beat
    n = int((duracion + 2.5) * am.SR)
    mix = np.zeros((n, 2))
    acordes = [[50, 54, 57, 61], [47, 50, 54, 57], [50, 54, 55, 59], [52, 55, 57, 62]]  # Dmaj7 Bm7 Gmaj7 A7sus4
    bajos = [38, 35, 43, 45]
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
        # PAD (igual que el día 1, algo más bajo para dejar sitio al arpegio)
        dur = compas + 1.0
        tt = am.t_(dur)
        env = np.minimum(1, tt / 0.7) * np.clip((dur - tt) / 1.0, 0, 1)
        for nota in ac:
            for det, pan in ((-6, -0.6), (6, 0.6)):
                f = am.hz(nota) * 2 ** (det / 1200)
                s = sum(np.sin(2 * np.pi * f * h * tt + am.rng.uniform(0, 6.28)) / h ** 1.6 for h in range(1, 7))
                poner(am.estereo(s * env * 0.042, pan), t0)
        # ARPEGIO tipo marimba: semicorcheas sincopadas (posición, nota del acorde, octava)
        patron = [(0, 0, 12), (3, 2, 12), (6, 1, 24), (8, 3, 12), (10, 2, 12), (11, 0, 24), (14, 3, 12)]
        for k, (pos, idx, octava) in enumerate(patron):
            f = am.hz(ac[idx] + octava)
            tt = am.t_(0.7)
            vel = am.rng.uniform(0.6, 0.95)
            env = np.minimum(1, tt / 0.002) * np.exp(-tt / 0.22)
            s = (np.sin(2 * np.pi * f * tt) + 0.18 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt / 0.03)) * env * vel
            poner(am.estereo(s * (0.085 if octava == 12 else 0.05), 0.4 if k % 2 else -0.4), t0 + pos * beat / 4)
        # BAJO: negra con puntillo + corchea a partir del compás 2
        if b >= 1:
            for tb, largo in ((0, 1.5), (1.5, 0.5), (2, 1.6)):
                tt = am.t_(beat * largo)
                env = np.minimum(1, tt / 0.01) * np.exp(-tt / 0.7) * np.clip((beat * largo - tt) / 0.08, 0, 1)
                f = am.hz(bajos[b % 4] + (7 if tb == 1.5 else 0))
                s = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * env
                poner(am.estereo(s * 0.09), t0 + tb * beat)
        # PERCUSIÓN a partir del compás 3: bombo suave 1 y 3 (+ "y" del 2), palmada suave en el 4, shaker a contratiempo
        if b >= 2 and t0 < fin_ritmo:
            for tb in (0, 1.5, 2):
                tg = t0 + tb * beat
                if tg > fin_ritmo:
                    break
                tt = am.t_(0.35)
                fase = 2 * np.pi * np.cumsum(48 + 70 * np.exp(-tt / 0.035)) / am.SR
                poner(am.estereo(np.sin(fase) * np.exp(-tt / 0.11) * (0.08 if tb == 1.5 else 0.115)), tg)
            tg = t0 + 3 * beat
            if tg <= fin_ritmo:
                c = sum(am.filtro(am.ruido(0.16), "bandpass", [900, 2600]) * np.exp(-am.t_(0.16) / 0.03) * g
                        for g in (1.0, 0.5))
                poner(am.estereo(c * 0.07, -0.15), tg)
            for k in range(4):
                tg = t0 + (k + 0.5) * beat
                if tg > fin_ritmo:
                    break
                sh = am.filtro(am.ruido(0.07), "highpass", 6500) * np.exp(-am.t_(0.07) / 0.018)
                poner(am.estereo(sh * 0.045, 0.45), tg)

    mix = am.reverb(mix, dur=2.4, decay=0.65, wet=0.3)
    mix = am.filtro(mix, "highpass", 70)
    mix = mix - 0.37 * am.filtro(mix, "bandpass", [1000, 3000])
    mix = mix[: int(duracion * am.SR)]
    tt = am.t_(duracion)
    mix *= (np.minimum(1, tt / 0.4) * np.clip((duracion - tt) / 1.5, 0, 1))[:, None]
    return np.tanh(mix * 1.4)


if __name__ == "__main__":
    duracion = json.load(open(RAIZ / "src/dia9/data/edit.json"))["duration"] + 0.7
    sys.argv = [sys.argv[0], str(duracion)]
    am.main()  # efectos de marca (y la música del día 1, que se sustituye a continuación)
    am.guardar("musica", musica9(duracion), pico_db=-1.0)
    am.guardar("obturador", audio_dia2.obturador())
