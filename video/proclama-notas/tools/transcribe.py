#!/usr/bin/env python3
# transcribe.py model out_dir wav1 [wav2...]  -> out_dir/<name>.json with segments+words
import sys, json, os, time
from faster_whisper import WhisperModel
model_name, outd, wavs = sys.argv[1], sys.argv[2], sys.argv[3:]
m = WhisperModel(model_name, device='cpu', compute_type='int8', cpu_threads=4)
prompt = ("Entrevista en Santander de Quilichao, Cauca. Gobernador del Cauca Octavio Guzmán, alcalde Luis Eduardo Grijalba, "
          "Delio Hernán Trujillo, alcalde de Inzá, Óscar Hernán Cifuentes, alcalde de Caloto, Leonel Barrera, EmQuilichao, "
          "Jorge Macías, Emcaservicios, Edgar Gómez, Carolina Camargo, secretaria de Salud, Hospital Francisco de Paula Santander, "
          "compactadores, Calle 5, Popayán, Proclama del Pacífico.")
for w in wavs:
    name = os.path.splitext(os.path.basename(w))[0]; out = os.path.join(outd, name + '.json')
    if os.path.exists(out): continue
    t = time.time()
    from scipy.io import wavfile
    import numpy as np
    sr, a = wavfile.read(w); a = a.astype(np.float32) / 32768.0
    segs, info = m.transcribe(a, language='es', beam_size=5, word_timestamps=True, initial_prompt=prompt, vad_filter=True)
    res = []
    for s in segs:
        res.append({'start': s.start, 'end': s.end, 'text': s.text.strip(), 'words': [{'w': x.word, 's': x.start, 'e': x.end, 'p': x.probability} for x in (s.words or [])]})
    json.dump({'file': w, 'duration': info.duration, 'segments': res}, open(out, 'w'), ensure_ascii=False, indent=1)
    with open(os.path.join(outd, name + '.txt'), 'w') as f:
        for s in res: f.write(f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text']}\n")
    print(name, f'{time.time()-t:.0f}s', flush=True)
