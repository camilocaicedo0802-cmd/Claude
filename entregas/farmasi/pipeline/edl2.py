"""v3 timing: natural speed, natural breaths kept, one inserted beat after the question."""
FPS = 30
W, H = 1080, 1920
SPEED = 1.0

# (name, src_in, src_out) or (name, None, pause_seconds)
SEGS = [
    ("A", 31.92, 34.30),    # cuando come cualquier cosa que coma
    ("B", 35.02, 36.60),    # la glucosa sube
    ("C1", 37.15, 41.26),   # y demora mucho tiempo estando ahí, ¿qué es lo que le ayuda la sidra de manzana?
    ("P1", None, 0.40),     # beat after the question (room tone)
    ("C2", 41.28, 42.50),   # a que esa glucosa
    ("F", 43.00, 47.85),    # no quede por tanto tiempo arriba, sino que baje mucho más rápido
]
ROOMTONE = (42.42, 42.95)

OFFS = {}
_t = 0.0
for name, a, b in SEGS:
    dur = b if a is None else (b - a) / SPEED
    OFFS[name] = (_t, a, b)
    _t += dur
TOTAL = _t
NFRAMES = int(round(TOTAL * FPS))
AUDIO_SEGS = [(n, a, b) for n, a, b in SEGS if a is not None]


def src_to_out(src):
    for name, a, b in SEGS:
        if a is not None and a - 0.03 <= src <= b + 0.03:
            return OFFS[name][0] + (src - a) / SPEED
    raise ValueError(src)


def out_to_src(name, t):
    o, a, _ = OFFS[name]
    return a + (t - o) * SPEED


def start(name):
    return OFFS[name][0]


def fr(t):
    return int(round(t * FPS))


# Visual plan (output seconds). Text cue times are phrase-level, held for the whole shot.
CUT = dict(S1=0.0, S2=src_to_out(32.82), S3=start("B"), S4=start("C1"), S5=src_to_out(39.46),
           S6=src_to_out(40.38), S7a=start("C2"), S7b=start("F"), S7c=src_to_out(44.64), END=TOTAL)
