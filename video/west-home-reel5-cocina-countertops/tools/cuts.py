"""refine piece in/out points to energy dips, assemble a test voice track and re-transcribe it."""
import sys, json, numpy as np, scipy.io.wavfile as wf, scipy.signal as sg
N = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel5/'
# (take, in, out, gap_after) — whisper times; refined below
P = [
    ('IMG_5382', 0.46, 5.05, 0.08),   # Félix, ¿qué pasa si quiero remodelar mi cocina y no sé qué countertop elegir?
    ('IMG_5384', 4.97, 6.13, 0.0),    # tenemos dos opciones
    ('IMG_5384', 7.39, 9.03, 0.08),   # el granito o el cuarzo.
    ('IMG_5391', 6.86, 9.11, 0.08),   # ¿cuál es la diferencia entre los dos materiales?
    ('IMG_5393', 3.24, 6.91, 0.08),   # el granito puede ser un poco más económico pero requiere mayor mantenimiento
    ('IMG_5393', 11.74, 14.18, 0.04), # el cuarzo es un material fabricado
    ('IMG_5393', 14.57, 16.56, 0.06), # hay más variación en los patrones
    ('IMG_5393', 17.10, 19.60, 0.08), # lo mejor de todo es que ya viene completamente sellado
    ('IMG_5396', 8.21, 17.90, 0.08),  # el cuarzo resiste calor, pero no tanto como el granito, entonces tienes que ser cuidadoso ... no dejarlas encima de tu countertop porque se puede dañar.
    ('IMG_5399', 4.69, 6.30, 0.08),   # ¿qué opción me recomendarías tú?
    ('IMG_5400', 13.28, 15.11, 0.0),  # hacemos un appointment y vamos a
    ('IMG_5400', 15.71, 17.71, 0.06), # un distribuidor de materiales
    ('IMG_5400', 23.23, 26.50, 0.10), # porque no es lo mismo mirarla completo a mirar un sample pequeño.
    ('IMG_5402', 1.20, 2.85, 0.0),    # Y si quieres que mi equipo y yo te ayudemos,
    ('IMG_5402', 4.84, 7.65, 0.0),    # comenta la palabra cocina y nos podremos en contacto contigo.
]
SR = 16000
cache = {}
def load(k):
    if k not in cache:
        sr, a = wf.read(N + f'audio/{k}.wav'); cache[k] = a.astype(np.float32) / 32768
    return cache[k]
def env(a):
    y = sg.sosfilt(sg.butter(4, [100, 4000], 'bp', fs=SR, output='sos'), a)
    h = int(0.01 * SR)
    return np.array([20 * np.log10(np.sqrt((y[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(y) - h, h)])
def refine(k, t, lo, hi):
    e = env(load(k)); i0, i1 = max(0, int((t + lo) * 100)), min(len(e) - 1, int((t + hi) * 100))
    seg = e[i0:i1 + 1]
    # prefer the quietest 10 ms frame, ties broken toward t
    j = int(np.argmin(seg + 0.02 * np.abs(np.arange(i0, i1 + 1) - t * 100)))
    return round((i0 + j) / 100, 2), round(float(seg[j]), 1)
out = []
for k, a, b, g in P:
    a2, ea = refine(k, a, -0.03, 0.03)
    b2, eb = refine(k, b, -0.03, 0.03)
    out.append((k, a2, b2, g))
    print(f'{k} {a:6.2f}->{a2:6.2f} ({ea:5.1f} dB)  {b:6.2f}->{b2:6.2f} ({eb:5.1f} dB)  len {b2 - a2:4.2f}')
json.dump(out, open(N + 'edit_pieces.json', 'w'), indent=0)
# assemble
xs = []
for k, a, b, g in out:
    x = load(k)[int(a * SR):int(b * SR)].copy()
    f = int(0.008 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    xs += [x, np.zeros(int(g * SR), np.float32)]
v = np.concatenate(xs); wf.write(N + 'voice_test.wav', SR, (v * 32767).astype(np.int16))
print('TOTAL', round(len(v) / SR, 2))
if '--tr' in sys.argv:
    from faster_whisper import WhisperModel
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    segs, _ = m.transcribe(v, language='es', word_timestamps=True)
    for s in segs: print(f'[{s.start:6.2f}-{s.end:6.2f}] {s.text}')
