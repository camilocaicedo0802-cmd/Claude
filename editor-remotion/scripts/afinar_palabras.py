#!/usr/bin/env python3
"""Afina los tiempos por palabra de Whisper y corrige nombres propios.

Fuentes: Whisper sin VAD (material/transcripciones/<clip>.json), Whisper con VAD
(material/transcripciones/_vad.json) y la energía real de la voz (silencios >= 0,12 s).
Regla: se parte del tiempo con VAD; la primera palabra tras cada silencio real se ancla
al final de ese silencio y la palabra anterior termina donde empieza el silencio.
Salida: src/datos/palabras.json (tiempos relativos al archivo de origen de cada clip)."""
import subprocess, json, numpy as np, scipy.signal as sg

CLIPS = ["toma1_agro", "wa_105147_0", "wa_105147_1", "wa_105147_2", "wa_105147_3", "wa_105147_4", "wa_105147_5"]
# Texto final (corrige marcas y quita claquetas). Debe tener las mismas palabras de discurso que Whisper.
TEXTO = {
    "toma1_agro": "Hola mis Kracks, ¿ustedes saben qué ventajas hay de sembrar semilla certificada?",
    "wa_105147_0": "Estoy acá en un día de campo de Fedearroz, el gremio de arroceros en Colombia, y nos van a contar cuáles son las principales ventajas de sembrar semilla certificada.",
    "wa_105147_1": "Buenas tardes, mi nombre es Luis Bernal Gutiérrez, ingeniero agrónomo de Fedearroz y hago parte del proyecto de asistencia AMTEC.",
    "wa_105147_2": "Beneficio número uno, semilla libre de malezas.",
    "wa_105147_3": "Beneficio número dos, garantía de que lo que usted compra es lo que se lleva.",
    "wa_105147_4": "Beneficio número tres, excelente sanidad y mayor potencial de rendimiento.",
    "wa_105147_5": "AMTEC, adopción masiva de tecnología.",
}
SALTAR_VAD = {"wa_105147_1": 2, "wa_105147_5": 1}     # palabras de claqueta al inicio (transcripción con VAD)
# Inicio real del discurso (s) cuando la claqueta confunde a Whisper.
INICIO_MIN = {"wa_105147_4": 1.50, "wa_105147_5": 1.95, "wa_105147_1": 2.30}

def silencios(clip):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", f"material/crudo/{clip}.mp4", "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], check=True, capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    y = sg.sosfilt(sg.butter(4, [180, 7600], btype="band", fs=16000, output="sos"), x)
    w = 160
    db = 20 * np.log10(np.array([np.sqrt((y[i:i + w] ** 2).mean()) for i in range(0, len(y) - w, w)]) + 1e-7)
    db = np.convolve(db, np.ones(3) / 3, "same")
    ruido, pico = np.percentile(db, 12), np.percentile(db, 95)
    act = db > ruido + 0.30 * (pico - ruido)
    gaps, i, n = [], 0, len(act)
    while i < n:
        if not act[i]:
            j = i
            while j < n and not act[j]: j += 1
            if j - i >= 12: gaps.append((i / 100, j / 100))
            i = j
        else: i += 1
    return gaps, act

vad = json.load(open("material/transcripciones/_vad.json"))
salida = {}
for clip in CLIPS:
    palabras = TEXTO[clip].split()
    ws = vad[clip][SALTAR_VAD.get(clip, 0):]
    assert len(ws) == len(palabras), (clip, len(ws), len(palabras), [w["text"] for w in ws])
    s = [max(w["s"], INICIO_MIN.get(clip, 0)) if k == 0 else w["s"] for k, w in enumerate(ws)]
    e = [w["e"] for w in ws]
    gaps, act = silencios(clip)
    notas = {}
    for g0, g1 in gaps:
        if g1 < s[0] - 0.3 or g0 > e[-1]: continue
        # palabra cuyo inicio queda más cerca del final del silencio
        k = min(range(len(s)), key=lambda i: abs(s[i] - g1))
        if abs(s[k] - g1) <= 0.45:
            if abs(s[k] - g1) > 0.03: notas[k] = s[k]
            s[k] = g1
            if k > 0: e[k - 1] = min(e[k - 1], g0 + 0.03) if e[k - 1] > g0 else e[k - 1]
    # la primera palabra empieza donde empieza de verdad la voz
    i0 = int(s[0] * 100)
    if not act[min(i0, len(act) - 1)]:
        nxt = np.where(act[i0:i0 + 80])[0]
        if len(nxt): notas[0] = s[0]; s[0] = (i0 + nxt[0]) / 100
    # última palabra: hasta el final real de la voz
    j = int(e[-1] * 100); fin = j
    while fin < len(act) - 1 and fin < j + 40 and act[fin]: fin += 1
    e[-1] = fin / 100
    res = []
    for k, t in enumerate(palabras):
        if k > 0 and s[k] < s[k - 1] + 0.04: s[k] = s[k - 1] + 0.04
        if k + 1 < len(s): e[k] = min(max(e[k], s[k] + 0.05), max(s[k] + 0.05, s[k + 1]))
        res.append({"text": t, "startMs": round(s[k] * 1000), "endMs": round(max(e[k], s[k] + 0.05) * 1000)})
    salida[clip] = res
    print(f"\n{clip}  silencios: " + " ".join(f"[{a:.2f}-{b:.2f}]" for a, b in gaps))
    print("  " + " ".join(f"{i}:{w['text']}[{w['startMs'] / 1000:.2f}" + (f"←{notas[i]:.2f}" if i in notas else "") + f"-{w['endMs'] / 1000:.2f}]" for i, w in enumerate(res)))
json.dump(salida, open("src/datos/palabras.json", "w"), ensure_ascii=False, indent=1)
