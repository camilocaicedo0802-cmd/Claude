import json, sys, wave, subprocess, difflib, re, unicodedata, numpy as np
from faster_whisper import WhisperModel
d = sys.argv[1]
bl = json.load(open(d + "/bloques.json"))
m = WhisperModel("small", device="cpu", compute_type="int8")
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()
for i, b in enumerate(bl):
    p = f"{d}/b{i:02d}.wav"
    try:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    except Exception:
        continue
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, language="es", condition_on_previous_text=False)
    t = " ".join(s.text for s in segs)
    A, B = norm(b), norm(t)
    sm = difflib.SequenceMatcher(None, A, B)
    diffs = [(" ".join(A[i1:i2]), " ".join(B[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    dur = len(a) / 16000
    print(f"b{i:02d}: {dur:.1f}s {len(A)} palabras {len(A)/dur*60:.0f} wpm, similitud {sm.ratio():.3f}")
    for x, y in diffs:
        print("    guion:", x, "| voz:", y)
