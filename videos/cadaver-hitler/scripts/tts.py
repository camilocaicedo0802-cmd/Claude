"""Genera la narración con Edge TTS frase por frase.

Edge TTS gratuito no acepta SSML con estilos emotivos, así que la expresividad se
consigue dando a cada frase su propia velocidad, tono y volumen, y metiendo
pausas medidas entre ellas. Salidas (en public/):
  voz.wav          narración completa, normalizada
  voz-palabras.json  tiempos de cada palabra (para subtítulos y sincronía)

Uso:  python3 scripts/tts.py [--voz es-MX-JorgeNeural]
En la nube de Claude Code hace falta: SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
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

# (texto, rate, pitch, volume, pausa_despues_ms, seccion)
GUION = [
    # GANCHO
    ("¿Cómo engañas a Hitler durante una guerra?", "+2%", "+4Hz", "+0%", 320, "gancho"),
    ("Pues los británicos tuvieron una idea bastante peculiar:", "+10%", "+0Hz", "+0%", 140, "gancho"),
    ("¡enviarle un espía muerto!", "-6%", "+6Hz", "+15%", 480, "gancho"),
    # CONTEXTO
    ("Era 1943, y los aliados querían invadir Sicilia.", "+6%", "+0Hz", "+0%", 120, "contexto"),
    ("El problema era que los alemanes ya sospechaban del plan.", "+6%", "-2Hz", "+0%", 260, "contexto"),
    ("Así que necesitaban distraerlos.", "+4%", "+0Hz", "+0%", 160, "contexto"),
    ("Y mucho.", "-10%", "-3Hz", "+5%", 420, "contexto"),
    # DESARROLLO
    ("Su solución fue conseguir un cadáver, ponerle uniforme militar, inventarle una identidad y entregarle documentos secretos falsos.", "+10%", "+0Hz", "+0%", 300, "desarrollo"),
    ("Básicamente, crearon un espía que no podía hablar, no podía traicionar a nadie…", "+6%", "+0Hz", "+0%", 260, "desarrollo"),
    ("y tenía una misión muy importante.", "-4%", "-2Hz", "+5%", 460, "desarrollo"),
    # GIRO
    ("Lo llamaron William Martin, y dejaron su cuerpo cerca de las costas de España, con un maletín lleno de información falsa.", "+6%", "+0Hz", "+0%", 320, "giro"),
    ("Los alemanes encontraron los documentos…", "+0%", "-2Hz", "+0%", 420, "giro"),
    ("¡y se tragaron el cuento!", "+2%", "+5Hz", "+12%", 480, "giro"),
    # DESENLACE Y VEREDICTO
    ("Hitler reforzó Grecia y Cerdeña, mientras los aliados desembarcaban en Sicilia.", "+6%", "+0Hz", "+0%", 320, "desenlace"),
    ("Sí. Un hombre muerto ayudó a engañar a uno de los ejércitos más poderosos del mundo.", "+2%", "+0Hz", "+0%", 520, "desenlace"),
    ("Veredicto: ¡verdad!", "-8%", "+3Hz", "+15%", 420, "veredicto"),
    ("Y probablemente fue el único espía que cumplió su misión sin decir una sola palabra.", "+0%", "-2Hz", "+0%", 600, "cierre"),
]


async def sintetizar(texto, voz, rate, pitch, volume, mp3_path):
    com = edge_tts.Communicate(
        texto, voz, rate=rate, pitch=pitch, volume=volume,
        boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY"),
    )
    palabras = []
    with open(mp3_path, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                palabras.append({
                    "texto": chunk["text"],
                    "inicio": chunk["offset"] / 1e7,
                    "duracion": chunk["duration"] / 1e7,
                })
    return palabras


def recortar_silencios(pcm, umbral_db=-42.0, margen_ini=0.03, margen_fin=0.07):
    """Quita el silencio que Edge TTS deja antes y después de cada frase.
    Devuelve (pcm_recortado, segundos_quitados_al_inicio)."""
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


def con_puntuacion(texto, palabras):
    """Edge TTS devuelve las palabras sin signos. Las empareja con las del guion
    para que el subtítulo muestre '¿Cómo', 'guerra?', '¡enviarle', '1943,'..."""
    fichas = texto.split()
    limpio = lambda s: "".join(c for c in s.lower() if c.isalnum())  # noqa: E731
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


def mp3_a_pcm(mp3_path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", mp3_path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        check=True, capture_output=True,
    ).stdout
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", default="es-MX-JorgeNeural")
    ap.add_argument("--salida", default="public")
    ap.add_argument("--hasta", type=int, default=len(GUION), help="número de frases a generar")
    args = ap.parse_args()

    os.makedirs(args.salida, exist_ok=True)
    pcm_total = bytearray()
    todas = []
    frases = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (texto, rate, pitch, vol, pausa, seccion) in enumerate(GUION[: args.hasta]):
            mp3 = os.path.join(tmp, f"{i:02d}.mp3")
            palabras = await sintetizar(texto, args.voz, rate, pitch, vol, mp3)
            pcm, quitado = recortar_silencios(mp3_a_pcm(mp3))
            t0 = len(pcm_total) / 2 / SR
            for p, visible in zip(palabras, con_puntuacion(texto, palabras)):
                todas.append({**p, "visible": visible,
                              "inicio": round(max(t0, t0 + p["inicio"] - quitado), 3),
                              "duracion": round(p["duracion"], 3), "frase": i, "seccion": seccion})
            dur = len(pcm) / 2 / SR
            frases.append({"i": i, "texto": texto, "seccion": seccion,
                           "inicio": round(t0, 3), "fin": round(t0 + dur, 3)})
            pcm_total += pcm
            pcm_total += b"\x00\x00" * int(SR * pausa / 1000)
            print(f"[{i:02d}] {t0:6.2f}s  {dur:5.2f}s  {texto}")

        crudo = os.path.join(tmp, "crudo.wav")
        with wave.open(crudo, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(bytes(pcm_total))

        # Cuerpo de voz: quita graves sobrantes, da presencia, compresión suave y normaliza a -16 LUFS.
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", crudo, "-af",
            "highpass=f=70,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=180:t=q:w=1:g=1.5,"
            "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,"
            "loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar", "48000", "-ac", "1", os.path.join(args.salida, "voz.wav"),
        ], check=True)

    with open(os.path.join(args.salida, "voz-palabras.json"), "w", encoding="utf-8") as f:
        json.dump({"voz": args.voz, "duracion": round(len(pcm_total) / 2 / SR, 3),
                   "frases": frases, "palabras": todas}, f, ensure_ascii=False, indent=1)
    print("Duración total:", round(len(pcm_total) / 2 / SR, 2), "s")


if __name__ == "__main__":
    asyncio.run(main())
