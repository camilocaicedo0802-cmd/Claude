"""word timings of the assembled voice (output seconds) with Whisper word timestamps."""
import json, numpy as np, scipy.io.wavfile as wf
from faster_whisper import WhisperModel
N = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel5/'
sr, a = wf.read(N + 'voice_test.wav'); a = a.astype(np.float32) / 32768
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language='es', word_timestamps=True, beam_size=5,
                       initial_prompt='Félix, countertop, granito, cuarzo, appointment, sample, Samantha.')
out = []
for s in segs:
    for w in s.words:
        out.append({'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 2)})
json.dump(out, open(N + 'edit/words_out.json', 'w'), indent=0, ensure_ascii=False)
print(' '.join(f"{w['w']}@{w['s']:.2f}" for w in out))
