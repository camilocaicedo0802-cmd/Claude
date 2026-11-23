import whisper, json, sys, os, time, subprocess
m = whisper.load_model("turbo", download_root="material/whisper-models")
prompt = "Armando, actores, casting, mánager, encasillado, streaming, estructura de BITS de un guion, cada BIT, transitar, partitura musical, melodía, personajes multidimensionales, masterclass."
for src in sys.argv[1:]:
    name = os.path.splitext(os.path.basename(src))[0]
    out = f"material/transcripciones/{name}.json"
    if os.path.exists(out): continue
    wav = f"material/audio16k/{name}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-vn","-ac","1","-ar","16000",wav], check=True)
    t = time.time()
    r = m.transcribe(wav, language="es", word_timestamps=True, fp16=False, condition_on_previous_text=False, initial_prompt=prompt, temperature=0)
    json.dump(r, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"== {name} ({time.time()-t:.0f}s): {r['text'].strip()}", flush=True)
