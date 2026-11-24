"""Edit decision list for the 12s glucose draft (Farmasi Nutriplus ACV gummies).

All times in seconds. Source times refer to raw/toma_ugc.mov unless noted.
Talking-head audio/video is sped up by SPEED (pitch preserved for audio).
"""
FPS = 30
W, H = 1080, 1920
SPEED = 1.1

# Voice segments kept from the main take (source in/out). Order = output order.
AUDIO_SEGS = [
    ("A", 31.92, 34.16),   # cuando come cualquier cosa que coma
    ("B", 35.02, 36.40),   # la glucosa sube
    ("C", 37.27, 42.32),   # y demora mucho tiempo estando ahí... a que esa glucosa
    ("F", 43.12, 47.60),   # no quede por tanto tiempo arriba, sino que baje mucho más rápido
]


def seg_offsets():
    out, t = {}, 0.0
    for name, a, b in AUDIO_SEGS:
        out[name] = (t, a, b)
        t += (b - a) / SPEED
    return out, t


OFFS, TOTAL = seg_offsets()
NFRAMES = int(round(TOTAL * FPS))


def src_to_out(src):
    """Map a source time in the main take to output time."""
    for name, a, b in AUDIO_SEGS:
        if a - 0.05 <= src <= b + 0.05:
            o, _, _ = OFFS[name]
            return o + (src - a) / SPEED
    raise ValueError(src)


def out_to_src(name, t):
    o, a, _ = OFFS[name]
    return a + (t - o) * SPEED


def fr(t):
    return int(round(t * FPS))


# Visual shots: (id, kind, frame_start, frame_end, params)
SHOTS = [
    dict(id="S1", kind="th", seg="A", f0=0, f1=fr(src_to_out(32.82)),
         zoom=(1.00, 1.07), center=(0.47, 0.52)),
    dict(id="S2", kind="broll", src="raw/apoyo2.mov", start=5.95, speed=0.70,
         f0=fr(src_to_out(32.82)), f1=fr(OFFS["B"][0]), zoom=1.22, center=(0.5, 0.56)),
    dict(id="S3", kind="image", src="stock/glucometro_lectura.jpg",
         f0=fr(OFFS["B"][0]), f1=fr(OFFS["C"][0]), zoom=(1.05, 1.22), center=(0.47, 0.43)),
    dict(id="S4", kind="th", seg="C", f0=fr(OFFS["C"][0]), f1=fr(src_to_out(39.46)),
         zoom=(1.10, 1.13), center=(0.47, 0.55)),
    dict(id="S5", kind="broll", src="raw/apoyo3.mov", start=0.0, speed=0.75,
         f0=fr(src_to_out(39.46)), f1=fr(src_to_out(40.38)), zoom=1.12, center=(0.5, 0.45)),
    dict(id="S6", kind="broll", src="raw/apoyo1.mov", start=12.0, speed=0.90,
         f0=fr(src_to_out(40.38)), f1=fr(src_to_out(41.28)), zoom=1.35, center=(0.44, 0.60)),
    dict(id="S7a", kind="th", seg="C", f0=fr(src_to_out(41.28)), f1=fr(OFFS["F"][0]),
         zoom=(1.00, 1.02), center=(0.47, 0.55)),
    dict(id="S7b", kind="th", seg="F", f0=fr(OFFS["F"][0]), f1=fr(src_to_out(44.64)),
         zoom=(1.12, 1.14), center=(0.47, 0.55)),
    dict(id="S7c", kind="th", seg="F", f0=fr(src_to_out(44.64)), f1=NFRAMES,
         zoom=(1.22, 1.27), center=(0.47, 0.53)),
]

# Caption groups: list of words (text, src_start, style). style: None | 'red' | 'green' | 'big'
# Source times from whisper word timestamps (main take), corrected by ear/energy.
CAPTIONS = [
    [("CUANDO", 31.98), ("COME", 32.38)],
    [("CUALQUIER", 32.82), ("COSA", 33.40)],
    [("QUE", 33.64), ("COMA", 33.90)],
    [("LA", 35.06), ("GLUCOSA", 35.40, "red")],
    [("SUBE", 35.98, "red", "📈")],
    [("Y", 37.29), ("DEMORA", 37.60)],
    [("MUCHO", 38.28), ("TIEMPO", 38.64)],
    [("ESTANDO", 38.98), ("AHÍ", 39.30)],
    [("¿QUÉ ES", 39.46), ("LO QUE", 39.62), ("LE AYUDA", 39.92)],
    [("LA SIDRA", 40.30, "green"), ("DE MANZANA?", 40.80, "green", "🍎")],
    [("A QUE", 41.28), ("ESA", 41.68), ("GLUCOSA", 41.84, "red")],
    [("NO QUEDE", 43.12), ("POR", 43.58)],
    [("TANTO", 43.82), ("TIEMPO", 44.08)],
    [("ARRIBA", 44.36, "red")],
    [("SINO", 44.64), ("QUE", 45.02), ("BAJE", 45.62, "green")],
    [("MUCHO", 46.24), ("MÁS", 46.92), ("RÁPIDO", 47.16, "green", "⚡")],
]
