import json,sys,base64,subprocess,time,os
name,text=sys.argv[1],sys.argv[2]
prompt=("# AUDIO PROFILE: Sofía\n## Creadora de contenido colombiana, 27 años, de Bogotá.\n\n"
"### DIRECTOR'S NOTES\nEstilo: cercana, segura y con energía, como contándole un truco a una amiga en un video de TikTok. Sonríe al hablar.\n"
"Acento: español colombiano de Bogotá, natural.\nRitmo: ágil, sin pausas largas.\n\n#### TRANSCRIPT\n"+text)
body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Kore"}}}}}
json.dump(body,open(f"q_{name}.json","w"))
for attempt in range(5):
    for M in ["gemini-3.1-flash-tts-preview","gemini-3.8-flash-tts"]:
        r=subprocess.run(["curl","-sS","--max-time","120",f"https://generativelanguage.googleapis.com/v1beta/models/{M}:generateContent","-H","Content-Type: application/json","-d",f"@q_{name}.json"],capture_output=True,text=True)
        d={}
        try:
            d=json.loads(r.stdout); p=d["candidates"][0]["content"]["parts"][0]["inlineData"]
            raw=base64.b64decode(p["data"])
            if raw[:4]==b"RIFF": open(f"{name}.wav","wb").write(raw)
            else:
                open(f"{name}.pcm","wb").write(raw)
                subprocess.run(["ffmpeg","-v","error","-y","-f","s16le","-ar","24000","-ac","1","-i",f"{name}.pcm",f"{name}.wav"],check=True)
            dur=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{name}.wav"],capture_output=True,text=True).stdout.strip()
            print(name,"OK",M,dur); sys.exit(0)
        except SystemExit: raise
        except Exception as e:
            msg=(d.get("error") or {}).get("message","")[:70] if d else str(e)[:70]
            print(name,M,"fail:",msg or (d.get("candidates") or [{}])[0].get("finishReason"),file=sys.stderr)
    time.sleep(20)
sys.exit(1)
