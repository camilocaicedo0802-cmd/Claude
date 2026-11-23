import sys, os, json, base64, urllib.request, wave
model, voice, out = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(sys.argv[4]).read().strip()
style = ("Narra como un locutor hombre, en español latinoamericano neutro, con energía, confianza y calidez natural, como un guía amigable que explica "
         "un tutorial en redes sociales. Ritmo ágil y dinámico, pausas cortas entre pasos, sonrisa en la voz, nada robótico. "
         "Pronuncia 'Cabany' como 'Kabáni', 'RUC' como 'ruc' y 'ATP' como 'a te pe'. Texto:\n\n")
body = {"contents": [{"parts": [{"text": style + text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
try:
    r = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read().decode()[:800]); sys.exit(1)
part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
pcm = base64.b64decode(part["data"]); print(part.get("mimeType"), len(pcm))
rate = 24000
mt = part.get("mimeType", "")
if "rate=" in mt: rate = int(mt.split("rate=")[1].split(";")[0])
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
print("ok", out, len(pcm) / 2 / rate, "s")
