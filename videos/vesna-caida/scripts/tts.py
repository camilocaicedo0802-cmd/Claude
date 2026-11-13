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

# (texto, rate, pitch, volume, pausa_despues_ms, seccion, enfasis)
# Más entonación: contrastes fuertes entre frases (las sorpresas suben de tono y volumen,
# el suspenso baja y se ralentiza) y pausas dramáticas antes de cada remate.
# "enfasis" = el subtítulo sale en MAYÚSCULAS y amarillo.
GUION = [
    # GANCHO
    ("Esta mujer cayó desde más de diez mil metros de altura…", "+6%", "+8Hz", "+0%", 220, "gancho", False),
    ("¡sin paracaídas!", "-8%", "+28Hz", "+30%", 520, "gancho", True),
    ("Y sobrevivió.", "-18%", "-10Hz", "+10%", 620, "gancho", True),
    ("Básicamente, tuvo el peor vuelo de su vida,", "+10%", "+3Hz", "+0%", 120, "gancho", False),
    ("pero también el mejor aterrizaje de la historia.", "+4%", "+16Hz", "+10%", 520, "gancho", False),
    # CONTEXTO
    ("Se llamaba Vesna.", "-6%", "+4Hz", "+0%", 200, "contexto", False),
    ("Tenía 23 años, y era azafata.", "+8%", "+10Hz", "+0%", 420, "contexto", False),
    ("Terminó en ese avión por una confusión con otra compañera.", "+10%", "-2Hz", "+0%", 260, "contexto", False),
    ("Sí, un error de oficina.", "-8%", "+18Hz", "+5%", 520, "contexto", False),
    # GIRO
    ("Pero 46 minutos después…", "-16%", "-10Hz", "+0%", 420, "giro", False),
    ("¡Bum!", "-8%", "+30Hz", "+35%", 420, "giro", True),
    ("Una explosión destrozó el avión en pleno cielo.", "+12%", "+10Hz", "+10%", 280, "giro", False),
    ("La aeronave se partió en tres.", "+4%", "+2Hz", "+0%", 180, "giro", False),
    ("Y Vesna cayó junto a los restos.", "-10%", "-9Hz", "+0%", 520, "giro", False),
    # EL SECRETO
    ("¿Su secreto para sobrevivir?", "-8%", "+24Hz", "+5%", 500, "secreto", False),
    ("Quedó atrapada en la parte trasera del fuselaje,", "+8%", "+2Hz", "+0%", 120, "secreto", False),
    ("junto a un carrito de comida.", "-6%", "+14Hz", "+5%", 420, "secreto", False),
    ("Sí, el carrito de los refrigerios terminó siendo parte de su equipo de supervivencia.", "+12%", "+8Hz", "+0%", 240, "secreto", False),
    ("¡Empleado del mes!", "-6%", "+28Hz", "+30%", 560, "secreto", True),
    # RESCATE Y RECUPERACIÓN
    ("Los restos cayeron sobre un bosque nevado.", "+4%", "-6Hz", "+0%", 220, "rescate", False),
    ("Un médico la encontró, y consiguió auxiliarla.", "+8%", "+6Hz", "+0%", 460, "rescate", False),
    ("Vesna estuvo 27 días en coma.", "-10%", "-10Hz", "+0%", 260, "recuperacion", False),
    ("Sufrió heridas gravísimas…", "-8%", "-6Hz", "+0%", 320, "recuperacion", False),
    ("¡pero volvió a caminar!", "+4%", "+22Hz", "+18%", 440, "recuperacion", False),
    ("Y hasta consiguió un récord Guinness.", "+6%", "+16Hz", "+12%", 520, "recuperacion", False),
    # VEREDICTO Y CIERRE
    ("Veredicto: ¡verdad!", "-12%", "+14Hz", "+22%", 480, "veredicto", True),
    ("Después de eso, hasta las turbulencias debían parecerle un masaje.", "+4%", "+8Hz", "+0%", 700, "cierre", False),
]

# Cómo se escriben en pantalla algunas palabras que la voz necesita leer distinto
VISIBLE = {
    ("diez", "mil"): "10.000",
    ("bum",): "¡BOOM!",
}


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


def aplicar_visibles(palabras):
    """Une/renombra palabras según VISIBLE (p. ej. "diez mil" -> "10.000")."""
    limpio = lambda s: "".join(c for c in s.lower() if c.isalnum())  # noqa: E731
    salida, i = [], 0
    while i < len(palabras):
        hecho = False
        for clave, texto in VISIBLE.items():
            n = len(clave)
            trozo = palabras[i:i + n]
            if len(trozo) == n and tuple(limpio(p["texto"]) for p in trozo) == clave:
                fin = trozo[-1]["inicio"] + trozo[-1]["duracion"]
                cola = "".join(c for c in trozo[-1]["visible"] if not c.isalnum())[-1:] if texto[-1].isalnum() else ""
                salida.append({**trozo[0], "visible": texto + cola, "duracion": round(fin - trozo[0]["inicio"], 3)})
                i += n
                hecho = True
                break
        if not hecho:
            salida.append(palabras[i])
            i += 1
    return salida


def mp3_a_pcm(mp3_path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", mp3_path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        check=True, capture_output=True,
    ).stdout
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", default="es-US-AlonsoNeural")
    ap.add_argument("--salida", default="public")
    ap.add_argument("--hasta", type=int, default=len(GUION), help="número de frases a generar")
    args = ap.parse_args()

    os.makedirs(args.salida, exist_ok=True)
    pcm_total = bytearray()
    todas = []
    frases = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (texto, rate, pitch, vol, pausa, seccion, enfasis) in enumerate(GUION[: args.hasta]):
            mp3 = os.path.join(tmp, f"{i:02d}.mp3")
            palabras = await sintetizar(texto, args.voz, rate, pitch, vol, mp3)
            pcm, quitado = recortar_silencios(mp3_a_pcm(mp3))
            t0 = len(pcm_total) / 2 / SR
            for p, visible in zip(palabras, con_puntuacion(texto, palabras)):
                if enfasis:
                    visible = visible.upper()
                todas.append({**p, "visible": visible, "enfasis": enfasis,
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

    todas = aplicar_visibles(todas)
    with open(os.path.join(args.salida, "voz-palabras.json"), "w", encoding="utf-8") as f:
        json.dump({"voz": args.voz, "duracion": round(len(pcm_total) / 2 / SR, 3),
                   "frases": frases, "palabras": todas}, f, ensure_ascii=False, indent=1)
    print("Duración total:", round(len(pcm_total) / 2 / SR, 2), "s")


if __name__ == "__main__":
    asyncio.run(main())
