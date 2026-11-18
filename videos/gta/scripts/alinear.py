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
import guion as _guion  # noqa: E402
from guion import ENFASIS_PALABRAS, GUION, VISIBLE  # noqa: E402

SR = 24000

# pausa (s) que queda DESPUÉS de cada frase; las de suspenso más largas
# narración pausada: las pausas de los momentos clave se respetan (suspenso antes de cada revelación)
PAUSA_NORMAL = 0.32
PAUSA_DESPUES = getattr(_guion, 'PAUSAS', {})
PAUSA_INTERNA_MAX = 0.42  # pausas dentro de una frase (puntos suspensivos)


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


def _sim(x, y):
    if not x or not y:
        return 0.0
    return difflib.SequenceMatcher(None, x, y, autojunk=False).ratio()


def alinear(fichas, oidas):
    """fichas: [{'texto', 'frase'}] del guion; oidas: [{'w','ini','fin'}] de whisper. Rellena ini/fin en fichas.

    Alineación difusa (programación dinámica): acepta palabras parecidas ("esfinje" = "esfinge") y dos palabras
    del guion que whisper oyó juntas ("pobrella" = "pobre ya"). Lo que no casa se reparte entre las vecinas.
    """
    a = [norm(f["texto"]) for f in fichas]
    b = [norm(o["w"]) for o in oidas]
    n, m = len(a), len(b)
    HUECO = -0.45
    puntos = np.full((n + 1, m + 1), -1e9)
    paso = {}
    puntos[0, :] = np.arange(m + 1) * HUECO
    puntos[:, 0] = np.arange(n + 1) * HUECO
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            mejor, de = puntos[i, j], paso.get((i, j))
            if i and j:
                v = puntos[i - 1, j - 1] + 2 * _sim(a[i - 1], b[j - 1]) - 1
                if v > mejor:
                    mejor, de = v, ("par", 1)
            if i >= 2 and j:
                v = puntos[i - 2, j - 1] + 2 * _sim(a[i - 2] + a[i - 1], b[j - 1]) - 1 + 0.3
                if v > mejor:
                    mejor, de = v, ("junta", 2)
            if i:
                v = puntos[i - 1, j] + HUECO
                if v > mejor:
                    mejor, de = v, ("sobraA", 1)
            if j:
                v = puntos[i, j - 1] + HUECO
                if v > mejor:
                    mejor, de = v, ("sobraB", 1)
            puntos[i, j], paso[(i, j)] = mejor, de
    # recorrer hacia atrás
    i, j, anclas = n, m, []
    while i > 0 or j > 0:
        tipo, _ = paso[(i, j)]
        if tipo == "par":
            if _sim(a[i - 1], b[j - 1]) >= 0.6:
                anclas.append(([i - 1], j - 1))
            i, j = i - 1, j - 1
        elif tipo == "junta":
            if _sim(a[i - 2] + a[i - 1], b[j - 1]) >= 0.6:
                anclas.append(([i - 2, i - 1], j - 1))
            i, j = i - 2, j - 1
        elif tipo == "sobraA":
            i -= 1
        else:
            j -= 1
    anclas.reverse()
    usadas = set()
    for idx, jj in anclas:
        o = oidas[jj]
        usadas.add(jj)
        pesos = np.array([max(1, len(a[k])) for k in idx], float)
        bordes = o["ini"] + (o["fin"] - o["ini"]) * np.concatenate([[0], np.cumsum(pesos) / pesos.sum()])
        for q, k in enumerate(idx):
            fichas[k]["ini"], fichas[k]["fin"] = float(bordes[q]), float(bordes[q + 1])
    # tramos sin ancla: repartir el tiempo de las palabras oídas que quedaron sueltas (p. ej. "1798" = 5 palabras)
    i = 0
    while i < n:
        if "ini" in fichas[i]:
            i += 1
            continue
        k = i
        while k < n and "ini" not in fichas[k]:
            k += 1
        t_prev = fichas[i - 1]["fin"] if i > 0 else 0.0
        t_sig = fichas[k]["ini"] if k < n else (oidas[-1]["fin"] if oidas else t_prev + 0.3)
        sueltas = [o for jj, o in enumerate(oidas) if jj not in usadas and o["ini"] >= t_prev - 0.01 and o["fin"] <= t_sig + 0.01]
        if sueltas:
            t0, t1 = sueltas[0]["ini"], sueltas[-1]["fin"]
            pesos = np.array([max(1, len(a[q])) for q in range(i, k)], float)
            bordes = t0 + (t1 - t0) * np.concatenate([[0], np.cumsum(pesos) / pesos.sum()])
            for q in range(i, k):
                fichas[q]["ini"], fichas[q]["fin"] = float(bordes[q - i]), float(bordes[q - i + 1])
        else:
            for q in range(i, k):
                prev = fichas[q - 1]["fin"] if q > 0 else 0.0
                f = fichas[q]
                f["ini"], f["fin"] = prev, max(prev + 0.08, min(t_sig, prev + 0.35))
        i = k
    return fichas


def plan_de_cortes(x, fichas):
    """Tramos a conservar [(desde, hasta)] del audio original.

    Los huecos candidatos salen de whisper (entre palabras), pero SOLO se corta dentro de un tramo
    que el audio confirma como silencio: whisper a veces da el final de una palabra antes de tiempo
    y cortar ahí se comería sílabas."""
    total = len(x) / SR
    win = int(SR * 0.005)
    n = len(x) // win
    rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1))
    rms = np.convolve(rms, np.ones(5) / 5, mode="same")
    db = 20 * np.log10(rms + 1e-9)
    umbral = np.percentile(db, 95) - 34
    silencio = db < umbral

    conservar, cursor = [], max(0.0, fichas[0]["ini"] - 0.06)
    for k in range(len(fichas) - 1):
        a, b = fichas[k]["fin"], fichas[k + 1]["ini"]
        borde = fichas[k]["frase"] != fichas[k + 1]["frase"]
        objetivo = PAUSA_DESPUES.get(fichas[k]["frase"], PAUSA_NORMAL) if borde else PAUSA_INTERNA_MAX
        # buscar el silencio real más largo alrededor del hueco (se amplía un poco: whisper se equivoca)
        i0, i1 = int(max(0, a - 0.25) * SR / win), int(min(total, b + 0.25) * SR / win)
        mejor, j = (0, 0), i0
        while j < i1:
            if silencio[j]:
                q = j
                while q < i1 and silencio[q]:
                    q += 1
                if q - j > mejor[1] - mejor[0]:
                    mejor = (j, q)
                j = q
            else:
                j += 1
        s0, s1 = mejor[0] * win / SR, mejor[1] * win / SR
        largo_silencio = s1 - s0
        exceso = largo_silencio - objetivo
        if exceso <= 0.04:
            continue
        # cortar en el centro del silencio, dejando aire a los dos lados
        c0 = s0 + (largo_silencio - exceso) / 2
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
    ap.add_argument("--voz", default="Gemini 2.5 Flash TTS · Charon")
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
