"""Locución con Gemini TTS (Google AI Studio, endpoint nativo). La clave la inyecta el proxy (x-goog-api-key).

uso: python tts.py guion.txt salida_dir [--voice Charon] [--model gemini-2.5-flash-preview-tts] [--only N]
Divide el guion en bloques de ~170 palabras por párrafos, genera cada bloque (PCM 24 kHz) y los une con
pausas naturales en salida_dir/voz.wav."""
import argparse
import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import wave

STYLE = (
    "Eres el narrador de un documental de misterio en YouTube, en español latino neutro (sin acento marcado). "
    "Voz masculina grave, cercana e hipnótica, como si le hablaras a una sola persona en la oscuridad. "
    "Ritmo natural y fluido (unas 150 palabras por minuto), con pausas dramáticas antes de cada pregunta y después de las frases cortas; "
    "baja casi a un susurro en los momentos inquietantes y sube la intensidad en las revelaciones. "
    "Las preguntas suenan genuinamente intrigantes, no teatrales. No añadas ni cambies ninguna palabra. "
    "Lee el siguiente texto:\n\n"
)


def blocks(text, maxw=190):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out, cur = [], []
    for p in paras:
        if cur and sum(len(x.split()) for x in cur) + len(p.split()) > maxw:
            out.append(cur)
            cur = []
        cur.append(p)
    if cur:
        out.append(cur)
    return ["\n\n".join(b) for b in out]


def call(model, voice, text, tries=6):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    prompt = ("# AUDIO PROFILE: Narrador de documental de misterio\n"
              "## ESCENA: estudio oscuro, de noche; le habla en voz baja a una sola persona.\n"
              "### NOTAS DEL DIRECTOR\n"
              "Estilo: narrador masculino de documental de misterio en YouTube, voz grave, cálida y resonante, "
              "que cuenta una historia intrigante con energía y dramatismo (no solemne ni monótono). "
              "Varía la entonación y la intensidad: sube la energía en las revelaciones, baja casi a un susurro en lo inquietante, "
              "y evita la cadencia descendente repetida al final de cada frase.\n"
              "Acento: español latino neutro.\n"
              "Ritmo: ágil y fluido, unas 160 palabras por minuto; pausas breves y estratégicas (más marcadas solo antes "
              "de las preguntas clave).\n"
              "#### TRANSCRIPCIÓN\n" + text)
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "temperature": 1.0,
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for k in range(tries):
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": "proxy-injected"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
            part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
            return base64.b64decode(part["data"]), part.get("mimeType", "")
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:400]
            print("HTTP", e.code, msg.replace(chr(10), " "), flush=True)
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(20 * (k + 1))
                continue
            raise
        except (KeyError, IndexError) as e:
            print("respuesta sin audio:", json.dumps(r)[:400], flush=True)
            time.sleep(10)
    raise RuntimeError("TTS falló")


def write_wav(path, pcm, rate=24000):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("out")
    ap.add_argument("--voice", default="Charon")
    ap.add_argument("--model", default="gemini-2.5-flash-preview-tts")
    ap.add_argument("--only", type=int, default=None)
    ap.add_argument("--maxw", type=int, default=190)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bl = blocks(open(a.guion).read(), a.maxw)
    json.dump(bl, open(os.path.join(a.out, "bloques.json"), "w"), ensure_ascii=False, indent=1)
    for i, b in enumerate(bl):
        if a.only is not None and i != a.only:
            continue
        p = os.path.join(a.out, f"b{i:02d}.wav")
        if os.path.exists(p) and a.only is None:
            continue
        print(f"bloque {i + 1}/{len(bl)} ({len(b.split())} palabras)", flush=True)
        pcm, mime = call(a.model, a.voice, b)
        if "wav" in mime:
            open(p, "wb").write(pcm)
        else:
            write_wav(p, pcm)
        print("  ok", mime, round(len(pcm) / 48000, 1), "s", flush=True)
    if a.only is None:
        lst = os.path.join(a.out, "list.txt")
        sil = os.path.join(a.out, "sil.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.6", sil], check=True)
        with open(lst, "w") as f:
            for i in range(len(bl)):
                f.write(f"file 'b{i:02d}.wav'\nfile 'sil.wav'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s16le",
                        os.path.join(a.out, "voz_raw.wav")], check=True)
        print("unido:", os.path.join(a.out, "voz_raw.wav"))


if __name__ == "__main__":
    main()
