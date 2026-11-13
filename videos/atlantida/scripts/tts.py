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
# Dirección "natural y humana": frases completas (sin trocear), contrastes suaves de tono,
# ritmo de narrador que cuenta un recuerdo y pausas variadas según la emoción.
GUION = [
    # GANCHO
    ("Nací en una ciudad donde el oro decoraba los templos, los canales atravesaban las calles, y el océano parecía obedecernos.", "-4%", "+0Hz", "+0%", 600, "gancho", False),
    ("Créeme…", "-12%", "-2Hz", "-5%", 420, "gancho", False),
    ("vivíamos en el paraíso.", "-8%", "+2Hz", "+0%", 750, "gancho", False),
    # MARAVILLA
    ("Nuestros palacios eran gigantescos, nuestras riquezas parecían infinitas, y nuestra ciudad estaba construida en enormes círculos de tierra y agua.", "-2%", "+2Hz", "+0%", 500, "maravilla", False),
    ("Éramos tan poderosos que empezamos a creer que nada podía detenernos.", "-2%", "+3Hz", "+3%", 650, "maravilla", False),
    ("Y ese fue nuestro primer error.", "-12%", "-4Hz", "+0%", 900, "maravilla", False),
    # EFECTO DOMINÓ
    ("Los dioses dejaron de mirarnos con admiración…", "-6%", "+0Hz", "+0%", 420, "domino", False),
    ("y comenzaron a castigarnos.", "-8%", "-3Hz", "+3%", 650, "domino", False),
    ("Primero tembló la tierra.", "+0%", "+0Hz", "+3%", 420, "domino", False),
    ("Después llegaron las olas.", "+0%", "+2Hz", "+5%", 550, "domino", False),
    ("Intenté correr, pero las calles ya estaban desapareciendo bajo el agua.", "+6%", "+3Hz", "+5%", 600, "domino", False),
    ("En una sola noche, nuestro mundo dejó de existir.", "-12%", "-4Hz", "+0%", 1000, "domino", False),
    # REVELACIÓN
    ("Quizás nunca hayas escuchado mi nombre,", "-6%", "+0Hz", "-3%", 300, "revelacion", False),
    ("pero nuestra ciudad se llamaba Atlántida.", "-8%", "+2Hz", "+5%", 800, "revelacion", False),
    ("Y lo más extraño es que toda esta historia viene de unos escritos de Platón, hace más de dos mil años.", "-2%", "+2Hz", "+0%", 700, "revelacion", False),
    # CIERRE
    ("Nunca encontraron pruebas concluyentes de que existiéramos.", "-4%", "+0Hz", "+0%", 550, "cierre", False),
    ("Así que tal vez no fui testigo de una civilización perdida…", "-8%", "-2Hz", "-3%", 500, "cierre", False),
    ("Tal vez fui parte de una leyenda.", "-12%", "-3Hz", "-3%", 1000, "cierre", False),
    ("Veredicto:", "-6%", "+2Hz", "+5%", 260, "veredicto", True),
    ("¡Mito!", "-10%", "+4Hz", "+10%", 700, "veredicto", True),
]

# Cómo se escriben en pantalla algunas palabras que la voz necesita leer distinto
VISIBLE = {
    ("dos", "mil"): "2.000",
}

# Palabras que salen en amarillo aunque la frase no sea de énfasis
ENFASIS_PALABRAS = {"atlántida", "platón"}


def respiracion(sr, dur=0.34, nivel_db=-34.0, seed=0):
    """Inhalación muy suave (ruido coloreado con envolvente) para que la voz suene humana."""
    rng = np.random.default_rng(seed)
    n = int(sr * dur)
    ruido = rng.standard_normal(n)
    espectro = np.fft.rfft(ruido)
    frec = np.fft.rfftfreq(n, 1 / sr)
    forma = np.exp(-((frec - 1400) / 1100) ** 2) + 0.5 * np.exp(-((frec - 2600) / 700) ** 2)
    x = np.fft.irfft(espectro * forma, n)
    tt = np.linspace(0, 1, n)
    x *= np.sin(np.pi * np.clip(tt * 1.25, 0, 1)) ** 1.5 * np.clip((1 - tt) * 6, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (nivel_db / 20)
    return (x * 32767).astype(np.int16).tobytes()


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
    ap.add_argument("--voz", default="es-MX-JorgeNeural")
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
                limpia = "".join(c for c in visible.lower() if c.isalnum())
                if enfasis:
                    visible = visible.upper()
                todas.append({**p, "visible": visible, "enfasis": enfasis or limpia in ENFASIS_PALABRAS,
                              "inicio": round(max(t0, t0 + p["inicio"] - quitado), 3),
                              "duracion": round(p["duracion"], 3), "frase": i, "seccion": seccion})
            dur = len(pcm) / 2 / SR
            frases.append({"i": i, "texto": texto, "seccion": seccion,
                           "inicio": round(t0, 3), "fin": round(t0 + dur, 3)})
            pcm_total += pcm
            silencio = bytearray(b"\x00\x00" * int(SR * pausa / 1000))
            if pausa >= 500 and i + 1 < min(args.hasta, len(GUION)):
                aire = respiracion(SR, seed=i)
                pos = max(0, len(silencio) - len(aire) - int(SR * 0.06) * 2)
                silencio[pos:pos + len(aire)] = aire
            pcm_total += silencio
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
            "highpass=f=70,equalizer=f=170:t=q:w=1:g=2.5,equalizer=f=3000:t=q:w=1.4:g=1.5,"
            "deesser=i=0.35,"
            "acompressor=threshold=-21dB:ratio=2.2:attack=10:release=160:makeup=2,"
            "aecho=0.9:0.6:28|47:0.10|0.06,"
            "loudnorm=I=-16:TP=-1.5:LRA=10",
            "-ar", "48000", "-ac", "1", os.path.join(args.salida, "voz.wav"),
        ], check=True)

    todas = aplicar_visibles(todas)
    with open(os.path.join(args.salida, "voz-palabras.json"), "w", encoding="utf-8") as f:
        json.dump({"voz": args.voz, "duracion": round(len(pcm_total) / 2 / SR, 3),
                   "frases": frases, "palabras": todas}, f, ensure_ascii=False, indent=1)
    print("Duración total:", round(len(pcm_total) / 2 / SR, 2), "s")


if __name__ == "__main__":
    asyncio.run(main())
