"""Voz natural (como el short de Napoleón): la toma del narrador queda CONTINUA, sin cortarla por frases ni estirarla.

Solo se insertan las citas (Lustig, la esposa) en las pausas naturales que el narrador dejó después de los dos puntos.
Luego alinear.py recorta las pausas largas (con fundidos) y acelera apenas con atempo:
    python3 scripts/montar_natural.py --narrador DIR/cap0_1.wav --citas DIR --tomas lustig=1,lustig2=1,esposa=2
    python3 scripts/alinear.py --sin-cortes --tempo 1.10   (el mismo --tempo en los dos)
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import guion as g  # noqa: E402
from alinear import SR, alinear, leer, transcribir  # noqa: E402
from montar_largo import a_wav, comprimir_silencios, env_db, nivel_ref, punto_quieto, recortar, rms_voz  # noqa: E402

AIRE = 0.18  # silencio a cada lado de una cita insertada (alinear.py lo ajusta después a la pausa del guion)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--narrador", required=True)
    ap.add_argument("--citas", required=True, help="carpeta con las tomas de las citas")
    ap.add_argument("--tomas", default="", help="voz=toma, separados por coma (por defecto 1)")
    ap.add_argument("--salida", default="public/voz-cruda.wav")
    ap.add_argument("--tempo", type=float, default=1.10, help="el mismo que se usará en alinear.py")
    args = ap.parse_args()
    tomas = dict(p.split("=") for p in args.tomas.split(",") if p)

    x = leer(args.narrador)
    nivel = rms_voz(x)
    narr = [i for i, fr in enumerate(g.GUION) if not fr[3]]
    fichas = [{"texto": tok, "frase": i} for i in narr for tok in g.GUION[i][0].split()]
    alinear(fichas, transcribir(x))
    fin = {i: max(f["fin"] for f in fichas if f["frase"] == i) for i in narr}

    # dónde va cada cita: justo después de la frase del narrador que la anuncia
    inserciones = []
    for i, (_t, _c, _e, voz) in enumerate(g.GUION):
        if voz:
            previa = max(j for j in narr if j < i)
            if inserciones and inserciones[-1][0] == previa:
                inserciones[-1][1].append(voz)
            else:
                inserciones.append((previa, [voz]))

    piezas, cursor = [], 0
    for previa, voces in inserciones:
        corte = punto_quieto(x, fin[previa] + 0.01, 0.25)
        piezas.append(x[cursor:corte])
        for voz in voces:
            y = leer(os.path.join(args.citas, f"{voz}_{tomas.get(voz, '1')}.wav"))
            y = comprimir_silencios(recortar(y, nivel_ref(y)), nivel_ref(y), 0.40, 0.28)
            y = y * (nivel / rms_voz(y)) * 0.92
            f = int(0.008 * SR)
            y[:f] *= np.linspace(0, 1, f)
            y[-f:] *= np.linspace(1, 0, f)
            piezas += [np.zeros(int(AIRE * SR), np.float32), y, np.zeros(int(AIRE * SR), np.float32)]
        cursor = corte
        print(f"cita {'+'.join(voces)} después de la frase {previa} ({corte / SR:.2f} s)", flush=True)
    piezas.append(x[cursor:])
    salida = ajustar_pausas(np.concatenate(piezas), args.tempo)
    a_wav(salida, args.salida)
    print(f"{args.salida}: {len(salida) / SR:.1f} s (narrador continuo, sin estirar)")


def silencios(x, minimo=0.06):
    """tramos de silencio real [(s0, s1)] en segundos"""
    win = int(SR * 0.005)
    db = np.convolve(env_db(x, win), np.ones(5) / 5, mode="same")
    quieto = db < np.percentile(db, 95) - 40
    out, j, n = [], 0, len(quieto)
    while j < n:
        if quieto[j]:
            k = j
            while k < n and quieto[k]:
                k += 1
            if (k - j) * win / SR >= minimo:
                out.append((j * win / SR, k * win / SR))
            j = k
        else:
            j += 1
    return out


def ajustar_pausas(x, tempo):
    """Pausas medidas como silencio real y en tiempo FINAL (después de acelerar con `tempo`): las marcadas en PAUSAS
    quedan exactas (se corta o se agrega silencio en su centro); las demás entre frases solo se acortan hasta
    PAUSA_NORMAL y las de dentro de una frase hasta PAUSA_INTERNA_MAX. Así se conserva la variación natural."""
    fichas = [{"texto": tok, "frase": i} for i, (t, *_r) in enumerate(g.GUION) for tok in t.split()]
    alinear(fichas, transcribir(x))
    fin = {i: max(f["fin"] for f in fichas if f["frase"] == i) for i in range(len(g.GUION))}
    ini = {i: min(f["ini"] for f in fichas if f["frase"] == i) for i in range(len(g.GUION))}
    sil = silencios(x)
    cambios = {}  # índice del silencio -> largo final
    for k in range(len(g.GUION) - 1):
        a, b = fin[k] - 0.2, ini[k + 1] + 0.2
        cand = [(min(s1, b) - max(s0, a), n) for n, (s0, s1) in enumerate(sil) if min(s1, b) - max(s0, a) > 0]
        objetivo = g.PAUSAS.get(k, g.PAUSA_NORMAL) * tempo
        if not cand:
            print(f"  frase {k}: sin silencio en el borde", flush=True)
            continue
        n = max(cand)[1]
        cambios[n] = (objetivo, k in g.PAUSAS)
    tope = getattr(g, "PAUSA_INTERNA_MAX", 0.30) * tempo
    for n, (s0, s1) in enumerate(sil):
        if n not in cambios and s0 > 0.05 and s1 - s0 > tope:
            cambios[n] = (tope, False)
    piezas, cursor = [], 0
    for n, (s0, s1) in enumerate(sil):
        if n not in cambios or s0 < 0.05 or s1 > len(x) / SR - 0.05:
            continue
        largo, (objetivo, exacta) = s1 - s0, cambios[n]
        medio = int((s0 + s1) / 2 * SR)
        if largo > objetivo + 0.02:
            quita = int((largo - objetivo) * SR)
            piezas.append(x[cursor:medio - quita // 2])
            cursor = medio + (quita - quita // 2)
        elif exacta and largo < objetivo - 0.02:
            piezas += [x[cursor:medio], np.zeros(int((objetivo - largo) * SR), np.float32)]
            cursor = medio
    piezas.append(x[cursor:])
    return np.concatenate(piezas)


if __name__ == "__main__":
    main()
