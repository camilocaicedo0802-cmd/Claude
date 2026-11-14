"""Convierte cualquier narración (ElevenLabs, Gemini, grabación propia) en voz.wav + voz-palabras.json.

1. Transcribe public/voz-cruda.wav con faster-whisper (tiempos por palabra).
2. Alinea esa transcripción con el guion exacto (scripts/guion.py) para conservar ortografía y puntuación.
3. Acorta las pausas largas entre frases (las de suspenso se dejan más largas).
4. Procesa el audio (EQ suave, compresión, -16 LUFS, la pregunta final más fuerte) y escribe los tiempos.

Uso:  python3 scripts/alinear.py [--tempo 1.0] [--voz "nombre"]
"""

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
import unicodedata
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from guion import ENFASIS_PALABRAS, GUION, VISIBLE  # noqa: E402

SR = 24000

# pausa (s) que queda DESPUÉS de cada frase; las de suspenso más largas
PAUSA_NORMAL = 0.26
PAUSA_DESPUES = {1: 0.42, 8: 0.36, 9: 0.34, 11: 0.30, 13: 0.30, 14: 0.38, 16: 0.42, 17: 0.40}
PAUSA_INTERNA_MAX = 0.30  # pausas dentro de una frase


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalnum() and not unicodedata.combining(c))


def leer(ruta):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768


def transcribir(x):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    x16 = np.interp(np.arange(0, len(x), SR / 16000), np.arange(len(x)), x).astype(np.float32)
    segs, _ = m.transcribe(x16, language="es", beam_size=5, word_timestamps=True)
    return [{"w": w.word.strip(), "ini": w.start, "fin": w.end} for s in segs for w in s.words]


def alinear(fichas, oidas):
    """fichas: [{'texto', 'frase'}] del guion; oidas: [{'w','ini','fin'}] de whisper. Rellena ini/fin en fichas."""
    a = [norm(f["texto"]) for f in fichas]
    b = [norm(o["w"]) for o in oidas]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                fichas[i1 + k]["ini"], fichas[i1 + k]["fin"] = oidas[j1 + k]["ini"], oidas[j1 + k]["fin"]
        elif op == "replace":
            t0, t1 = oidas[j1]["ini"], oidas[j2 - 1]["fin"]
            pesos = np.array([max(1, len(a[k])) for k in range(i1, i2)], float)
            bordes = t0 + (t1 - t0) * np.concatenate([[0], np.cumsum(pesos) / pesos.sum()])
            for k in range(i2 - i1):
                fichas[i1 + k]["ini"], fichas[i1 + k]["fin"] = float(bordes[k]), float(bordes[k + 1])
    # las que whisper no oyó: interpolar entre vecinas
    for i, f in enumerate(fichas):
        if "ini" not in f:
            prev = next((fichas[k]["fin"] for k in range(i - 1, -1, -1) if "fin" in fichas[k]), 0.0)
            sig = next((fichas[k]["ini"] for k in range(i + 1, len(fichas)) if "ini" in fichas[k]), prev + 0.3)
            f["ini"], f["fin"] = prev, max(prev + 0.08, min(sig, prev + 0.35))
    return fichas


def plan_de_cortes(x, fichas):
    """Tramos a conservar [(desde, hasta)] del audio original.

    Las pausas son los huecos entre palabras que da whisper (incluyen respiraciones, que no son silencio).
    Cada hueco más largo que su objetivo se acorta cortando en los puntos de menor energía."""
    total = len(x) / SR
    win = int(SR * 0.005)
    n = len(x) // win
    rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1))
    rms = np.convolve(rms, np.ones(5) / 5, mode="same")

    def energia(t):
        return rms[min(n - 1, max(0, int(t * SR / win)))]

    conservar, cursor = [], max(0.0, fichas[0]["ini"] - 0.06)
    for k in range(len(fichas) - 1):
        a, b = fichas[k]["fin"], fichas[k + 1]["ini"]
        borde = fichas[k]["frase"] != fichas[k + 1]["frase"]
        objetivo = PAUSA_DESPUES.get(fichas[k]["frase"], PAUSA_NORMAL) if borde else PAUSA_INTERNA_MAX
        exceso = (b - a) - objetivo
        if exceso <= 0.04:
            continue
        candidatos = np.arange(a + 0.05, b - 0.05 - exceso + 1e-6, 0.005)
        if len(candidatos) == 0:
            continue
        c0 = min(candidatos, key=lambda c: energia(c) + energia(c + exceso))
        conservar.append((cursor, float(c0)))
        cursor = float(c0 + exceso)
    conservar.append((cursor, min(total, fichas[-1]["fin"] + 0.35)))
    return conservar


def mapear(t, conservar):
    acumulado = 0.0
    for a, b in conservar:
        if t < a:
            return acumulado
        if t <= b:
            return acumulado + (t - a)
        acumulado += b - a
    return acumulado


def aplicar_visibles(palabras):
    salida, i = [], 0
    while i < len(palabras):
        for clave, texto in VISIBLE.items():
            n = len(clave)
            trozo = palabras[i:i + n]
            if len(trozo) == n and tuple(norm(p["texto"]) for p in trozo) == tuple(norm(c) for c in clave):
                fin = trozo[-1]["inicio"] + trozo[-1]["duracion"]
                cola = "".join(c for c in trozo[-1]["visible"] if not c.isalnum())[-1:]
                salida.append({**trozo[0], "visible": texto + cola, "enfasis": True, "duracion": round(fin - trozo[0]["inicio"], 3)})
                i += n
                break
        else:
            salida.append(palabras[i])
            i += 1
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default="public/voz-cruda.wav")
    ap.add_argument("--tempo", type=float, default=1.0)
    ap.add_argument("--voz", default="ElevenLabs v3 · Laura")
    args = ap.parse_args()

    x = leer(args.entrada)
    fichas = [{"texto": tok, "frase": i} for i, (t, *_) in enumerate(GUION) for tok in t.split()]
    alinear(fichas, transcribir(x))
    conservar = plan_de_cortes(x, fichas)

    editado = np.concatenate([x[int(a * SR):int(b * SR)] for a, b in conservar])
    # micro fundidos en cada empalme para que no chasquee
    pos = 0
    for a, b in conservar[:-1]:
        pos += int((b - a) * SR)
        k = int(0.012 * SR)
        editado[max(0, pos - k):pos] *= np.linspace(1, 0, min(k, pos))
        editado[pos:pos + k] *= np.linspace(0, 1, len(editado[pos:pos + k]))

    T = args.tempo
    palabras, frases = [], []
    for f in fichas:
        i = f["frase"]
        texto, seccion, enfasis, _ = GUION[i]
        ini = mapear(f["ini"], conservar) / T
        fin = mapear(f["fin"], conservar) / T
        visible = f["texto"].upper() if enfasis else f["texto"]
        palabras.append({"texto": norm(f["texto"]), "inicio": round(ini, 3), "duracion": round(max(0.06, fin - ini), 3),
                         "visible": visible, "enfasis": enfasis or norm(f["texto"]) in ENFASIS_PALABRAS,
                         "frase": i, "seccion": seccion})
    for i, (texto, seccion, *_rest) in enumerate(GUION):
        ps = [p for p in palabras if p["frase"] == i]
        frases.append({"i": i, "texto": texto, "seccion": seccion, "inicio": ps[0]["inicio"],
                       "fin": round(ps[-1]["inicio"] + ps[-1]["duracion"], 3)})
    palabras = aplicar_visibles(palabras)
    duracion = len(editado) / SR / T

    with tempfile.TemporaryDirectory() as tmp:
        crudo = os.path.join(tmp, "e.wav")
        with wave.open(crudo, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(editado, -1, 1) * 32767).astype(np.int16).tobytes())
        ult = frases[-1]
        cadena = (
            (f"atempo={T}," if abs(T - 1) > 1e-3 else "")
            + "highpass=f=80,equalizer=f=3200:t=q:w=1.4:g=1.2,deesser=i=0.25,"
            "acompressor=threshold=-20dB:ratio=2:attack=10:release=160:makeup=1.5,"
            "loudnorm=I=-16:TP=-1.5:LRA=11,"
            f"volume=1.45:enable='between(t,{ult['inicio'] - 0.05:.2f},{ult['fin'] + 0.15:.2f})',"
            "alimiter=limit=0.95:level=false"
        )
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", crudo, "-af", cadena, "-ar", "48000", "-ac", "1", "public/voz.wav"], check=True)

    with open("public/voz-palabras.json", "w", encoding="utf-8") as f:
        json.dump({"voz": args.voz, "duracion": round(duracion, 3), "frases": frases, "palabras": palabras}, f, ensure_ascii=False, indent=1)
    n = sum(len(t.split()) for t, *_ in GUION)
    for fr in frases:
        print(f"[{fr['i']:02d}] {fr['inicio']:6.2f}–{fr['fin']:6.2f}  {fr['texto']}")
    print(f"Duración {duracion:.2f} s · {n / duracion:.2f} palabras/s")


if __name__ == "__main__":
    main()
