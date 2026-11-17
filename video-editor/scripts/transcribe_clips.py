"""Re-transcribe tramos concretos del bruto con Whisper large-v3 para obtener
tiempos por palabra precisos (en segundos del archivo original).
Uso: python3 -I transcribe_clips.py <audio> <salida.json> a1:b1 a2:b2 ..."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
audio, out = sys.argv[1], sys.argv[2]
spans = [tuple(map(float, s.split(":"))) for s in sys.argv[3:]]
model = WhisperModel("large-v3", device="cpu", compute_type="int8", download_root="/home/user/Claude/video-editor/.models")
prompt = "305 Media Club. Un filmmaker, un editor, un community manager y alguien que te maneje los anuncios en Meta. ¿Son cuatro sueldos o solo uno?"
res = {}
for a, b in spans:
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    wav = np.frombuffer(pcm, np.float32)
    segs, _ = model.transcribe(wav, language="es", word_timestamps=True, beam_size=5, initial_prompt=prompt, condition_on_previous_text=False, vad_filter=False)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"text": w.word.strip(), "start": round(a + w.start, 3), "end": round(a + w.end, 3), "p": round(w.probability, 2)})
    res[f"{a}:{b}"] = words
    print(f"[{a}-{b}] " + " ".join(f"{w['text']}({w['start']:.2f}-{w['end']:.2f})" for w in words), flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
