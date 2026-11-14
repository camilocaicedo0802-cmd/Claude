"""Narración de Napoleón con Edge TTS, calibrada por medición.

Indicaciones del guion:
  - Velocidad: ~3 palabras por segundo (≈183 por minuto).
  - Tono: gancho muy alto (≈283 Hz), desarrollo en tono de narradora (≈186 Hz),
    conflicto y preguntas arriba otra vez (≈248 Hz).
  - La pregunta final es la frase con más volumen del video.
  - Voz muy animada, de "chisme histórico", con ironía.

Cómo se cumple: cada frase se sintetiza, se mide su tono (mediana de F0) y su duración,
y se corrigen el desplazamiento de tono por frase y la velocidad global hasta llegar al objetivo.
Los parámetros finales quedan en scripts/calibracion.json.

Uso:  python3 scripts/tts.py [--voz es-US-PalomaNeural]
En la nube de Claude Code: SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
"""

import argparse
import asyncio
import json
import os
import subprocess
import tempfile
import wave

import numpy as np
import edge_tts

SR = 24000
GANCHO, NARRADORA, CONFLICTO = 283, 186, 248

# (texto, tono objetivo Hz, volumen, pausa después ms, sección, énfasis)
GUION = [
    ("¡Napoleón era más alto que el francés promedio!", GANCHO, "+15%", 160, "gancho", False),
    ("Y lo recordamos enano por culpa de un dibujante inglés.", GANCHO, "+10%", 320, "gancho", False),
    ("En 1802, Napoleón es el hombre más poderoso de Francia.", NARRADORA, "+0%", 180, "desarrollo", False),
    ("Pero en Londres, un caricaturista lo odia.", CONFLICTO, "+8%", 260, "conflicto", False),
    ("Lo dibuja diminuto, con berrinches de niño, y le pone un apodo:", NARRADORA, "+0%", 120, "desarrollo", False),
    ("¡Lítel Bóni!", CONFLICTO, "+12%", 240, "conflicto", True),
    ("Los periódicos lo copian por toda Europa.", NARRADORA, "+0%", 300, "desarrollo", False),
    ("Cuando muere, en 1821, la autopsia dice: cinco pies y dos pulgadas.", NARRADORA, "+0%", 200, "desarrollo", False),
    ("En Inglaterra eso es…", CONFLICTO, "+5%", 160, "conflicto", False),
    ("¡uno cincuenta y siete!", CONFLICTO, "+14%", 280, "conflicto", True),
    ("Pero eran pulgadas francesas, más largas.", NARRADORA, "+0%", 160, "desarrollo", False),
    ("¿Cuánto medía de verdad?", CONFLICTO, "+8%", 160, "conflicto", False),
    ("¡Casi uno sesenta y nueve!", CONFLICTO, "+14%", 220, "conflicto", True),
    ("¿Y el francés promedio?", CONFLICTO, "+8%", 140, "conflicto", False),
    ("Unos uno sesenta y cinco.", NARRADORA, "+3%", 320, "desarrollo", False),
    ("Para colmo, siempre aparecía rodeado de su guardia, soldados elegidos por altos.", NARRADORA, "+0%", 160, "desarrollo", False),
    ("Y el pequeño cabo era un apodo cariñoso, no una medida.", NARRADORA, "+0%", 320, "desarrollo", False),
    ("Veredicto: ¡mito!", CONFLICTO, "+18%", 300, "veredicto", True),
    ("¿Emperador bajito… o víctima del primer meme de la historia?", CONFLICTO, "+40%", 700, "pregunta", False),
]

PALABRAS_POR_SEG = 3.05

VISIBLE = {
    ("lítel", "bóni"): "¡Little Boney",
    ("uno", "cincuenta", "y", "siete"): "¡1,57",
    ("uno", "sesenta", "y", "nueve"): "1,69",
    ("uno", "sesenta", "y", "cinco"): "1,65",
}
ENFASIS_PALABRAS = {"mito", "meme", "165"}


def limpio(s):
    return "".join(c for c in s.lower() if c.isalnum())


async def sintetizar(texto, voz, rate, pitch, volume, mp3_path):
    com = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch, volume=volume, boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY"))
    palabras = []
    with open(mp3_path, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                palabras.append({"texto": chunk["text"], "inicio": chunk["offset"] / 1e7, "duracion": chunk["duration"] / 1e7})
    return palabras


def mp3_a_pcm(mp3_path):
    return subprocess.run(["ffmpeg", "-v", "error", "-i", mp3_path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], check=True, capture_output=True).stdout


def recortar_silencios(pcm, umbral_db=-42.0, margen_ini=0.03, margen_fin=0.07):
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    win = int(SR * 0.01)
    n = len(x) // win
    rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    activos = np.where(20 * np.log10(rms) > umbral_db)[0]
    if len(activos) == 0:
        return pcm, 0.0
    ini = max(0, activos[0] * win - int(SR * margen_ini))
    fin = min(len(x), (activos[-1] + 1) * win + int(SR * margen_fin))
    return pcm[ini * 2: fin * 2], ini / SR


def tono_mediano(pcm):
    """Mediana de F0 (Hz) en los tramos con voz (autocorrelación, rango de voz femenina)."""
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    x = x[::2]  # 12 kHz basta para medir el tono
    sr = SR // 2
    win, hop = int(0.04 * sr), int(0.01 * sr)
    f0 = []
    for i in range(0, len(x) - win, hop):
        fr = x[i:i + win] * np.hanning(win)
        if np.sqrt(np.mean(fr ** 2)) < 0.02:
            continue
        ac = np.correlate(fr, fr, "full")[win - 1:]
        lo, hi = int(sr / 520), int(sr / 110)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] / ac[0] > 0.45:
            f0.append(sr / k)
    return float(np.median(f0)) if f0 else 0.0


def con_puntuacion(texto, palabras):
    fichas = texto.split()
    salida, j = [], 0
    for p in palabras:
        objetivo = limpio(p["texto"])
        k = j
        while k < len(fichas) and limpio(fichas[k]) != objetivo:
            k += 1
        if k < len(fichas):
            salida.append(fichas[k])
            j = k + 1
        else:
            salida.append(p["texto"])
    return salida


def aplicar_visibles(palabras):
    salida, i = [], 0
    while i < len(palabras):
        hecho = False
        for clave, texto in VISIBLE.items():
            n = len(clave)
            trozo = palabras[i:i + n]
            if len(trozo) == n and tuple(limpio(p["texto"]) for p in trozo) == clave:
                fin = trozo[-1]["inicio"] + trozo[-1]["duracion"]
                cola = "".join(c for c in trozo[-1]["visible"] if not c.isalnum())[-1:]
                visible = texto + cola
                if trozo[0].get("enfasis"):
                    visible = visible.upper()
                salida.append({**trozo[0], "visible": visible, "enfasis": True, "duracion": round(fin - trozo[0]["inicio"], 3)})
                i += n
                hecho = True
                break
        if not hecho:
            salida.append(palabras[i])
            i += 1
    return salida


async def pasada(voz, params, tmp):
    """Sintetiza todas las frases con los parámetros dados. Devuelve audio, mediciones y palabras."""
    resultados = []
    for i, (texto, objetivo, vol, pausa, seccion, enfasis) in enumerate(GUION):
        mp3 = os.path.join(tmp, f"{i:02d}.mp3")
        rate = f"{params['rate'] + params['ajuste_rate'][i]:+d}%"
        pitch = f"{params['pitch'][i]:+d}Hz"
        palabras = await sintetizar(texto, voz, rate, pitch, vol, mp3)
        pcm, quitado = recortar_silencios(mp3_a_pcm(mp3))
        resultados.append({"pcm": pcm, "quitado": quitado, "palabras": palabras, "tono": tono_mediano(pcm), "dur": len(pcm) / 2 / SR})
    return resultados


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", default="es-US-PalomaNeural")
    ap.add_argument("--salida", default="public")
    ap.add_argument("--iteraciones", type=int, default=5)
    args = ap.parse_args()
    os.makedirs(args.salida, exist_ok=True)
    base_tono = 193
    params = {
        "rate": 26,
        # las preguntas y la frase final, un pelín más pausadas para que se entiendan
        "ajuste_rate": [(-6 if "?" in g[0] else 0) for g in GUION],
        "pitch_base": None,
        "pitch": [int(g[1] - base_tono) for g in GUION],
    }
    # frases que se pegaban a esta velocidad: un poco más despacio
    for i, g in enumerate(GUION):
        if g[0].startswith("Y lo recordamos") or g[0].startswith("Lo dibuja"):
            params["ajuste_rate"][i] = -6
    params.pop("pitch_base")
    total_palabras = sum(len(g[0].split()) for g in GUION)
    total_pausas = sum(g[3] for g in GUION[:-1]) / 1000

    with tempfile.TemporaryDirectory() as tmp:
        for it in range(args.iteraciones):
            res = await pasada(args.voz, params, tmp)
            dur = sum(r["dur"] for r in res) + total_pausas
            wps = total_palabras / dur
            errores = [(r["tono"] - g[1]) / g[1] for r, g in zip(res, GUION)]
            peor = max(abs(e) for e in errores)
            print(f"iteración {it + 1}: {wps:.2f} palabras/s · peor desvío de tono {peor * 100:.1f}%")
            if peor <= 0.05 and 2.95 <= wps <= 3.15:
                break
            for i, (r, g) in enumerate(zip(res, GUION)):
                params["pitch"][i] = int(np.clip(params["pitch"][i] + 0.9 * (g[1] - r["tono"]), -60, 140))
            params["rate"] = int(np.clip(params["rate"] + 90 * (PALABRAS_POR_SEG / wps - 1), 0, 80))

        # --- ensamblar la versión final ---
        pcm_total = bytearray()
        todas, frases = [], []
        for i, (r, g) in enumerate(zip(res, GUION)):
            texto, objetivo, vol, pausa, seccion, enfasis = g
            t0 = len(pcm_total) / 2 / SR
            for p, visible in zip(r["palabras"], con_puntuacion(texto, r["palabras"])):
                if enfasis:
                    visible = visible.upper()
                todas.append({**p, "visible": visible, "enfasis": enfasis or limpio(visible) in ENFASIS_PALABRAS,
                              "inicio": round(max(t0, t0 + p["inicio"] - r["quitado"]), 3), "duracion": round(p["duracion"], 3),
                              "frase": i, "seccion": seccion})
            frases.append({"i": i, "texto": texto, "seccion": seccion, "inicio": round(t0, 3), "fin": round(t0 + r["dur"], 3),
                           "tono_objetivo": objetivo, "tono_medido": round(r["tono"])})
            pcm_total += r["pcm"]
            pcm_total += b"\x00\x00" * int(SR * pausa / 1000)
            print(f"[{i:02d}] {t0:6.2f}s  objetivo {objetivo} Hz → medido {r['tono']:.0f} Hz  {texto}")

        crudo = os.path.join(tmp, "crudo.wav")
        with wave.open(crudo, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(bytes(pcm_total))
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", crudo, "-af",
            "highpass=f=80,equalizer=f=220:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.4:g=2,deesser=i=0.35,"
            "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2,"
            "loudnorm=I=-16:TP=-1.5:LRA=11,"
            f"volume=1.6:enable='between(t,{frases[-1]['inicio'] - 0.05:.2f},{frases[-1]['fin'] + 0.1:.2f})',"
            "alimiter=limit=0.95:level=false",
            "-ar", "48000", "-ac", "1", os.path.join(args.salida, "voz.wav"),
        ], check=True)

    todas = aplicar_visibles(todas)
    duracion = len(pcm_total) / 2 / SR
    with open(os.path.join(args.salida, "voz-palabras.json"), "w", encoding="utf-8") as f:
        json.dump({"voz": args.voz, "duracion": round(duracion, 3), "frases": frases, "palabras": todas}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(os.path.dirname(__file__), "calibracion.json"), "w", encoding="utf-8") as f:
        json.dump({"voz": args.voz, **params}, f, indent=1)
    print(f"Duración total: {duracion:.2f} s · {total_palabras / duracion:.2f} palabras/s ({total_palabras / duracion * 60:.0f} por minuto)")


if __name__ == "__main__":
    asyncio.run(main())
