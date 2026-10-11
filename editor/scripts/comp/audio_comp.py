"""Vídeos complementarios: música propia y efectos en public/comp_<vídeo>/audio/, más el obturador del día 2.

Uso: python -I scripts/comp/audio_comp.py <abdomen|piernas|producto>
Reutiliza el sintetizador del día 1 (scripts/audio_marca.py) y el obturador de scripts/dia2/audio_dia2.py sin tocarlos.
Mismos timbres y la misma limpieza para la voz que los 10 vídeos del reto (sin graves < 70 Hz, hueco en 1–3 kHz),
con una música distinta para cada uno:
- abdomen: La mayor a 76 BPM, calma de masaje (Amaj9 · F#m9 · Dmaj9 · E6sus), arpegio lento de piano eléctrico en
  negras y un pad que respira cada dos compases.
- piernas: Mi mayor a 82 BPM (Emaj7 · C#m7 · Amaj7 · B6), arpegio que sube en corcheas (como las pasadas
  ascendentes) y percusión muy ligera.
- producto: Do mayor a 100 BPM (Cmaj7 · Am7 · Fmaj7 · G6), pulsos cortos tipo "interfaz" y bajo con más presencia.
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

ESTILOS = {
    "abdomen": {"bpm": 76, "acordes": [[57, 61, 64, 68, 71], [54, 57, 61, 64, 68], [50, 54, 57, 61, 64], [52, 56, 59, 61, 66]],
                "bajos": [45, 42, 50, 40], "arpegio": "negras", "percusion": False},
    "piernas": {"bpm": 82, "acordes": [[52, 56, 59, 63], [49, 52, 56, 59], [45, 49, 52, 56], [47, 51, 54, 56]],
                "bajos": [40, 37, 45, 35], "arpegio": "corcheas", "percusion": True},
    "producto": {"bpm": 100, "acordes": [[48, 52, 55, 59], [45, 48, 52, 55], [41, 45, 48, 52], [43, 47, 50, 52]],
                 "bajos": [36, 33, 41, 31], "arpegio": "pulsos", "percusion": True},
}


def musica(duracion: float, e: dict):
    beat = 60 / e["bpm"]
    compas = 4 * beat
    n = int((duracion + 2.5) * am.SR)
    mix = np.zeros((n, 2))
    total = int(np.ceil(duracion / compas)) + 1
    fin_ritmo = duracion - 1.5

    def poner(senal, inicio):
        i = int(inicio * am.SR)
        if i >= n:
            return
        j = min(n, i + len(senal))
        mix[i:j] += senal[: j - i]

    for b in range(total):
        t0 = b * compas
        ac = e["acordes"][b % 4]
        # Pad: dos voces desafinadas, entra y sale suave (en abdomen "respira" cada dos compases)
        dur = compas * (2 if e["arpegio"] == "negras" else 1) + 1.0
        if e["arpegio"] != "negras" or b % 2 == 0:
            tt = am.t_(dur)
            env = np.minimum(1, tt / (1.2 if e["arpegio"] == "negras" else 0.6)) * np.clip((dur - tt) / 1.2, 0, 1)
            for nota in ac[:4]:
                for det, pan in ((-7, -0.6), (7, 0.6)):
                    f = am.hz(nota) * 2 ** (det / 1200)
                    s = sum(np.sin(2 * np.pi * f * h * tt + am.rng.uniform(0, 6.28)) / h ** 1.7 for h in range(1, 7))
                    poner(am.estereo(s * env * 0.038, pan), t0)
        # Arpegio de piano eléctrico
        if e["arpegio"] == "negras":
            pasos = [(k * beat, ac[k % len(ac)] + 12) for k in range(4)]
            decay, vol = 0.7, 0.085
        elif e["arpegio"] == "corcheas":
            orden = [0, 1, 2, 3, 1, 2, 3, 0]
            pasos = [(k * beat / 2, ac[orden[k]] + (24 if k == 7 else 12)) for k in range(8)]
            decay, vol = 0.36, 0.085
        else:  # pulsos cortos tipo interfaz: corcheas en la quinta y la octava
            pasos = [(k * beat / 2, ac[0] + 24 if k % 2 == 0 else ac[2] + 12) for k in range(8)]
            decay, vol = 0.16, 0.07
        for k, (dt, nota) in enumerate(pasos):
            f = am.hz(nota)
            tt = am.t_(1.2)
            v = am.rng.uniform(0.55, 0.85)
            env = np.minimum(1, tt / 0.004) * np.exp(-tt / decay)
            s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.12)) * env * v
            poner(am.estereo(s * vol, 0.35 if k % 2 else -0.35), t0 + dt)
        # Bajo suave
        if b >= 1:
            for tb in ((0, 2) if e["arpegio"] == "negras" else (0, 2, 3.5)):
                largo = 1.6 if tb < 3 else 0.5
                tt = am.t_(beat * largo)
                env = np.minimum(1, tt / 0.01) * np.exp(-tt / 0.8) * np.clip((beat * largo - tt) / 0.08, 0, 1)
                f = am.hz(e["bajos"][b % 4])
                s = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * env
                poner(am.estereo(s * (0.11 if e["arpegio"] == "pulsos" else 0.09)), t0 + tb * beat)
        # Percusión muy ligera (bombo suave y aro), nunca en abdomen
        if e["percusion"] and b >= 2 and t0 < fin_ritmo:
            for tb in range(4):
                tg = t0 + tb * beat
                if tg > fin_ritmo:
                    break
                if tb in (0, 2):
                    tt = am.t_(0.35)
                    fase = 2 * np.pi * np.cumsum(46 + 72 * np.exp(-tt / 0.04)) / am.SR
                    poner(am.estereo(np.sin(fase) * np.exp(-tt / 0.12) * 0.1), tg)
                else:
                    c = am.filtro(am.ruido(0.18), "bandpass", [1200, 3500]) * np.exp(-am.t_(0.18) / 0.04)
                    poner(am.estereo(c * 0.07, 0.1), tg)
                p = am.filtro(am.ruido(0.12), "highpass", 7000) * np.exp(-am.t_(0.12) / 0.03)
                poner(am.estereo(p * 0.035, 0.45), tg + beat / 2)

    mix = am.reverb(mix, dur=2.8, decay=0.72, wet=0.34)
    mix = am.filtro(mix, "highpass", 70)
    mix = mix - 0.37 * am.filtro(mix, "bandpass", [1000, 3000])
    mix = mix[: int(duracion * am.SR)]
    tt = am.t_(duracion)
    mix *= (np.minimum(1, tt / 0.4) * np.clip((duracion - tt) / 1.5, 0, 1))[:, None]
    return np.tanh(mix * 1.4)


if __name__ == "__main__":
    video = sys.argv[1]
    am.OUT = RAIZ / f"public/comp_{video}/audio"
    duracion = json.load(open(RAIZ / f"src/comp_{video}/data/edit.json"))["duration"] + 0.7
    sys.argv = [sys.argv[0], str(duracion)]
    am.main()  # efectos de marca (y la música del día 1, que se sustituye a continuación)
    am.guardar("musica", musica(duracion, ESTILOS[video]), pico_db=-1.0)
    am.guardar("obturador", audio_dia2.obturador())
