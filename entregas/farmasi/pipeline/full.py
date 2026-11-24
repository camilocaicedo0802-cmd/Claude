"""Full Farmasi UGC video (~45 s) in the reference style.
Timeline = audio segments (source in/out or room-tone pauses) -> shots -> text cues."""
import sys, os, math, subprocess
import numpy as np

SP = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else None
ONLY = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
os.chdir(SP)
sys.path.insert(0, "scripts")
from mglib import *  # noqa: F401,F403,E402
from mglib import Image, ImageDraw, ImageFilter  # noqa: E402
from stabilize import stabilize  # noqa: E402

# ------------------------------------------------------------------ audio segments
SEGS = [
    ("I1", 0.15, 1.10),     # Holis.
    ("I2", 1.28, 5.22),     # Llegué. Hoy le tocó a mi esposo hacerme almorzaíto.
    ("I3", 12.45, 14.30),   # Bueno, llegué corriendo
    ("I4", 14.85, 17.82),   # a comer estas papitas, rosita con mi ensalada,
    ("I5a", 17.92, 20.88),  # pero primero me voy a tomar
    ("I5b", 21.32, 23.75),  # mis gomitas de sidra de manzana.
    ("PP", None, 0.55),     # beat for the product scene
    ("I6", 24.25, 27.00),   # Mi esposo me explicaba, a él le encanta investigar todo,
    ("I6b", 28.00, 29.55),  # él me explicaba que
    ("A", 30.95, 34.30),    # por lo general uno cuando come cualquier cosa que coma
    ("B", 35.02, 36.60),    # la glucosa sube
    ("C1", 37.15, 41.26),   # y demora mucho tiempo estando ahí. ¿Qué es lo que le ayuda la sidra de manzana?
    ("P1", None, 0.40),     # beat after the question
    ("C2", 41.28, 42.50),   # a que esa glucosa
    ("F", 43.00, 47.85),    # no quede por tanto tiempo arriba, sino que baje mucho más rápido.
    ("O1", 48.97, 51.20),   # Nosotros nos comemos dos gomitas al día,
    ("O2", 53.82, 55.75),   # una antes de la comida.
    ("O3", 56.25, 58.05),   # Me voy a comer las dos porque no me comí esta mañana.
    ("END", None, 1.90),    # end card
]
ROOMTONE = {"PP": 42.42, "P1": 42.42, "END": 58.05}

OFFS, _t = {}, 0.0
for name, a, b in SEGS:
    OFFS[name] = (_t, a, b)
    _t += b if a is None else (b - a)
TOTAL = _t
NF = int(round(TOTAL * FPS))


def S(name):
    return OFFS[name][0]


def T(src):
    for name, a, b in SEGS:
        if a is not None and a - 0.03 <= src <= b + 0.03:
            return OFFS[name][0] + (src - a)
    raise ValueError(src)


def src_of(t):
    """output time -> (segment name, source time) for talking-head frames"""
    for name, a, b in SEGS:
        o = OFFS[name][0]
        d = b if a is None else b - a
        if o - 1e-6 <= t < o + d + 1e-6:
            return name, (None if a is None else a + (t - o))
    return SEGS[-1][0], None


# ------------------------------------------------------------------ cues
def small(text, t, until=None, layer="front", ink=False, y=None, size=50):
    return dict(kind="small", text=text, t=t, until=until, layer=layer, ink=ink, y=y, size=size)


def big(text, t, until=None, layer="behind", grad="lilac", y=None, size=360, maxw=1000):
    return dict(kind="big", text=text, t=t, until=until, layer=layer, grad=grad, y=y, size=size, maxw=maxw)


# shot boundaries (output seconds)
B_V1b = S("I2")
B_V2 = T(3.62)
B_V6 = S("I5b")
B_V7 = T(22.68)
B_S2 = T(32.82)
B_S5 = T(39.46)
B_S6 = T(40.38)
B_S7c = T(44.64)

SHOTS = [
    # ---------------- intro
    dict(id="V1a", kind="th", t0=0.0, t1=B_V1b, zoom=(1.06, 1.10), center=(0.48, 0.50), cues=[
        big("HOLIS", 0.0, until=T(1.95)),
    ]),
    dict(id="V1b", kind="th", t0=B_V1b, t1=B_V2, zoom=(1.16, 1.20), center=(0.48, 0.52), cues=[
        big("HOLIS", -1, until=T(1.95)),
        small("llegué", T(1.30), until=T(1.95)),
        small("hoy le tocó a mi", T(1.95)),
        big("ESPOSO", T(3.10)),
    ]),
    dict(id="V2", kind="broll", src="raw/apoyo2.mov", start=5.85, speed=0.58, zoom=1.08, center=(0.5, 0.62),
         t0=B_V2, t1=S("I3"), cues=[
        small("hacerme", B_V2 + 0.03, ink=True, y=250),
        big("ALMORZAÍTO", B_V2 + 0.16, layer="front", grad="lilacd", y=420, size=250),
    ]),
    dict(id="V3", kind="th", t0=S("I3"), t1=S("I4"), zoom=(1.08, 1.12), center=(0.48, 0.50), cues=[
        small("bueno, llegué", S("I3") + 0.03),
        big("CORRIENDO", T(13.05)),
    ]),
    dict(id="V4", kind="th", t0=S("I4"), t1=S("I5a"), zoom=(1.16, 1.20), center=(0.48, 0.52), cues=[
        small("a comer estas papitas", S("I4") + 0.04, until=T(16.45)),
        small("rosita con mi", T(16.45)),
        big("ENSALADA", T(16.75)),
    ]),
    dict(id="V5", kind="th", t0=S("I5a"), t1=B_V6, zoom=(1.06, 1.10), center=(0.48, 0.52), cues=[
        small("pero", S("I5a") + 0.03, until=T(20.10)),
        big("PRIMERO", T(18.60)),
        small("me voy a tomar", T(20.10)),
    ]),
    dict(id="V6", kind="th", t0=B_V6, t1=B_V7, zoom=(1.14, 1.18), center=(0.48, 0.52), cues=[
        small("me voy a tomar mis", -1),
        big("GOMITAS", T(21.95)),
    ]),
    dict(id="V7", kind="scene", scene="product", t0=B_V7, t1=S("I6"), cues=[
        small("gomitas de", B_V7 + 0.04, ink=True, y=250),
        big("SIDRA DE", B_V7 + 0.12, layer="front", grad="lilacd", y=400, size=240),
        big("MANZANA", B_V7 + 0.26, layer="front", grad="lilacd", y=600, size=240),
    ]),
    dict(id="V8", kind="th", t0=S("I6"), t1=S("I6b"), zoom=(1.08, 1.12), center=(0.48, 0.56), cues=[
        small("mi esposo me explicaba", S("I6") + 0.04, until=T(25.28)),
        small("a él le encanta", T(25.28)),
        big("INVESTIGAR", T(25.85), size=330),
    ]),
    dict(id="V9", kind="th", t0=S("I6b"), t1=S("A"), zoom=(1.18, 1.22), center=(0.48, 0.56), cues=[
        big("INVESTIGAR", -1, size=330),
        small("él me explicaba que", S("I6b") + 0.04),
    ]),
    # ---------------- glucose section (as v4)
    dict(id="S1", kind="th", t0=S("A"), t1=B_S2, zoom=(1.04, 1.10), center=(0.47, 0.55), cues=[
        small("por lo general", S("A") + 0.04, until=T(31.96), y=430),
        small("cuando", T(31.96), y=430),
        big("COME", T(31.55), y=640, size=380),
    ]),
    dict(id="S2", kind="broll", src="raw/apoyo1.mov", start=4.55, speed=1.0, zoom=2.4, center=(1.0, 0.67),
         t0=B_S2, t1=S("B"), cues=[
        big("CUALQUIER", B_S2 + 0.04, layer="front", grad="lilacd", y=290, size=240),
        big("COSA", B_S2 + 0.18, layer="front", grad="lilacd", y=545, size=240),
        small("que coma", B_S2 + 0.34, ink=True, y=725, size=52),
    ]),
    dict(id="S3", kind="scene", scene="glucose", t0=S("B"), t1=S("C1"), cues=[]),
    dict(id="S4", kind="th", t0=S("C1"), t1=B_S5, zoom=(1.10, 1.15), center=(0.47, 0.56), card="red", cues=[
        small("y demora mucho", S("C1") + 0.06, y=400),
        big("TIEMPO", S("C1") + 0.35, y=610),
    ]),
    dict(id="S5", kind="broll", src="raw/apoyo3.mov", start=0.0, speed=0.75, zoom=1.06, center=(0.5, 0.55),
         matte="birefnet", leak=True, t0=B_S5, t1=B_S6, cues=[
        small("¿qué es lo que", B_S5 + 0.03, ink=True, y=330),
        big("LE AYUDA", B_S5 + 0.14, grad="lilacd", y=520, size=300),
    ]),
    dict(id="S6", kind="broll", src="raw/apoyo1.mov", start=11.95, speed=0.85, zoom=1.30, center=(0.44, 0.62),
         t0=B_S6, t1=S("C2"), cues=[
        small("la", B_S6 + 0.03, ink=True, y=300, size=52),
        big("SIDRA DE", B_S6 + 0.10, layer="front", grad="lilacd", y=440, size=230),
        big("MANZANA?", B_S6 + 0.24, layer="front", grad="lilacd", y=650, size=230),
    ]),
    dict(id="S7a", kind="th", t0=S("C2"), t1=S("F"), zoom=(1.02, 1.05), center=(0.47, 0.56), cues=[
        small("a que esa", S("C2") + 0.03, y=450),
        big("GLUCOSA", S("C2") + 0.18, y=660, size=330),
    ]),
    dict(id="S7b", kind="th", t0=S("F"), t1=B_S7c, zoom=(1.12, 1.15), center=(0.47, 0.56), card="lilac", cues=[
        small("no quede por tanto tiempo", S("F") + 0.05, y=300, size=48),
        big("ARRIBA", T(43.92), grad="red", y=520),
    ]),
    dict(id="S7c", kind="th", t0=B_S7c, t1=S("O1"), zoom=(1.16, 1.24), center=(0.47, 0.63), card="lilac", cues=[
        small("sino que", B_S7c + 0.03, until=T(46.15) + 0.2, y=260, size=48),
        big("BAJE", B_S7c + 0.2, until=T(46.15) + 0.2, y=470, size=400),
        small("mucho", T(46.15) + 0.04, y=1180, size=54),
        big("MÁS RÁPIDO", T(46.15) + 0.16, layer="front", grad="white", y=1390, size=260, maxw=960),
    ]),
    # ---------------- outro
    dict(id="V10", kind="broll", src="raw/apoyo2.mov", start=2.05, speed=1.0, zoom=1.10, center=(0.5, 0.62),
         t0=S("O1"), t1=S("O2"), cues=[
        small("nosotros nos comemos", S("O1") + 0.04, ink=True, y=250),
        big("DOS GOMITAS", T(50.0), layer="front", grad="lilacd", y=420, size=240),
        small("al día", T(50.55), ink=True, y=590, size=54),
    ]),
    dict(id="V11", kind="th", t0=S("O2"), t1=S("O3"), zoom=(1.08, 1.12), center=(0.47, 0.58), cues=[
        small("una antes de la comida", S("O2") + 0.04),
        big("ANTES", S("O2") + 0.18),
    ]),
    dict(id="V12", kind="th", t0=S("O3"), t1=S("END"), zoom=(1.14, 1.18), center=(0.47, 0.60), cues=[
        small("me voy a comer", S("O3") + 0.04, until=T(56.92)),
        big("LAS DOS", T(56.70)),
        small("porque no me comí esta mañana", T(56.92), size=46),
    ]),
    dict(id="V13", kind="scene", scene="end", t0=S("END"), t1=TOTAL, cues=[
        small("gomitas de sidra de manzana", S("END") + 0.05, ink=True, y=250),
        big("NUTRIPLUS", S("END") + 0.15, layer="front", grad="lilacd", y=420, size=250),
        small("Farmasi", S("END") + 0.45, ink=True, y=1650, size=56),
    ]),
]
for s in SHOTS:
    s["f0"], s["f1"] = fr(s["t0"]), fr(s["t1"])
SHOTS[-1]["f1"] = NF
SH = {s["id"]: s for s in SHOTS}

# ------------------------------------------------------------------ sources
_RV = []


def rvm():
    if not _RV:
        _RV.extend(np.load(f"work/rvmfull/{k}.npy", mmap_mode="r") for k in ("frames", "pha", "fgr"))
    return _RV


def load_th(s):
    frames, pha, fgr = rvm()
    idx = []
    for f in range(s["f0"], s["f1"]):
        _, src = src_of(f / FPS)
        if src is None:  # frame rounding put us inside a pause: use the start of the next spoken segment
            _, src = src_of(f / FPS + 1.0 / FPS)
        idx.append(min(len(pha) - 1, int(round(src * FPS))))
    lo, hi = max(0, min(idx) - 2), min(len(pha), max(idx) + 3)
    st = stabilize(np.asarray(pha[lo:hi]), radius=2, sigma=40)
    st = np.clip((st.astype(np.float32) - 6) * (255 / 243), 0, 255).astype(np.uint8)
    return [(np.asarray(frames[j]), st[j - lo], np.asarray(fgr[j])) for j in idx]


def load_broll(s):
    n = s["f1"] - s["f0"]
    z, (cx, cy) = s["zoom"], s["center"]
    args = ["-ss", f"{s['start']:.4f}", "-i", s["src"], "-an", "-vf",
            f"setpts=(PTS-STARTPTS)/{s['speed']},fps={FPS},"
            f"crop=w=iw/{z}:h=ih/{z}:x=(iw-iw/{z})*{cx}:y=(ih-ih/{z})*{cy},{TM},"
            f"scale={W}:{H}:flags=lanczos", "-frames:v", str(n)]
    return ffmpeg_frames(args, W, H, n)


def th_zoom(s, i, n):
    k = i / max(1, n - 1)
    z0, z1 = s["zoom"]
    punch = 1 + 0.06 * (1 - ease_out(i / 6)) if s["f0"] > 0 else 1.0
    return (z0 + (z1 - z0) * ease_in_out(k)) * punch


def head_top(s, src):
    """median topmost person row (output coords) in the central band, from the stabilized RVM alpha"""
    n = len(src)
    tops = []
    for i in np.linspace(0, n - 1, 6).astype(int):
        a = np.asarray(zoom_frame(src[i][1], th_zoom(s, i, n), s["center"]), np.float32) / 255
        band = a[:, int(W * 0.32):int(W * 0.68)].mean(1)
        rows = np.where(band > 0.45)[0]
        if len(rows):
            tops.append(rows[0])
    return float(np.median(tops)) if tops else 800.0


# ------------------------------------------------------------------ cue rendering
def draw_cue(base, c, t, shot_t0, auto_y):
    if t < c["t"] or (c["until"] is not None and t >= c["until"]):
        return
    t_in = c["t"] if c["t"] >= shot_t0 - 0.02 else t - 10  # carried over from previous shot: no re-reveal
    fade = 1.0
    if c["until"] is not None:
        fade = clamp((c["until"] - t) / 0.16)
    layer = base if fade >= 0.999 else Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if c["kind"] == "big":
        y = c["y"] if c["y"] is not None else auto_y["big"]
        big_reveal(layer, c["text"], c["size"], c["grad"], W / 2, y, t, t_in, c["maxw"])
    else:
        y = c["y"] if c["y"] is not None else auto_y["small"]
        words = c["text"].split(" ")
        kinetic_line(layer, [(w, t_in + i * 0.08) for i, w in enumerate(words)], W / 2, y, t,
                     size=c["size"], color=INK if c["ink"] else WHITE, shadow=not c["ink"])
    if layer is not base:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * fade)))
        base.alpha_composite(layer)


# ------------------------------------------------------------------ glucose chart cards
def draw_cards(base, s, t):
    if s.get("card") == "red":
        rp = ease_in_out((t - (s["t0"] + 0.12)) / 1.9)
        draw_card(base, t, 1440, s["t0"] + 0.02, rp, 0, False)
    elif s.get("card") == "lilac":
        t_in = SH["S7b"]["t0"]
        g1 = 0.44 * ease_out((t - t_in) / (SH["S7c"]["t0"] - t_in))
        g2 = 0.56 * ease_in_out((t - (SH["S7c"]["t0"] + 0.08)) / 1.35)
        ex = ease_out((t - T(46.15)) / 0.22)
        if ex < 1:
            draw_card(base, t, 1480, t_in + 0.02, 1.0, g1 + g2, True, ex, 170)


# ------------------------------------------------------------------ full-screen scenes
def scene_glucose(t, t0):
    lt = t - t0
    base = scene_bg().copy()
    k = ease_out_back(lt / 0.42, 1.4)
    ke = ease_out(lt / 0.42)
    for path, title, chip, side, cy_ in (("stock/cgm.jpg", "Monitor de glucosa", "↑ sube", -1, 0.15),
                                         ("stock/glucometro_prueba.jpg", "Prueba en casa", "↑ sube", 1, 0.35)):
        im = photo_card(path, title, chip, RED, cy_).rotate(-side * 9 * ke, resample=Image.BICUBIC, expand=True)
        put(base, im, W / 2 + side * 290 * k, 1010 + 20 * (1 - ke), alpha=ke, scale=0.92, blur=1.2)
    front = photo_card("stock/glucometro_lectura.jpg", "Medición de glucosa", "↑ 8.4 mmol/L", RED, 0.38)
    put(base, front, W / 2, 990 + 50 * (1 - ke), alpha=min(1, lt / 0.12), scale=1.0 + 0.1 * k)
    kinetic_line(base, [("la", t0 + 0.04)], W / 2, 300, t, size=46, color=INK, shadow=False)
    big_reveal(base, "GLUCOSA", 250, "lilacd", W / 2, 430, t, t0 + 0.12)
    if t >= T(35.85):
        big_reveal(base, "SUBE", 300, "red", W / 2 + 80, 1640, t, T(35.85))
        ka = ease_out((t - T(35.85)) / 0.35)
        put(base, arrow_img(), W / 2 - 250, 1640 + 60 * (1 - ka) - 10, alpha=ka)
    return push_in(base, lt, 1.6)


def scene_product(t, t0, end=False):
    lt = t - t0
    base = scene_bg().copy()
    ke = ease_out(lt / 0.45)
    k = ease_out_back(lt / 0.45, 1.3)
    card = photo_card("stock/bottle_card.png", "Gomitas Nutriplus", "Farmasi", (150, 70, 200), 0.5,
                      sub="vinagre de manzana")
    ang = (-4 if not end else 3) * ke
    put(base, card.rotate(ang, resample=Image.BICUBIC, expand=True), W / 2, 1110 + 60 * (1 - ke),
        alpha=min(1, lt / 0.12), scale=1.25 * (0.9 + 0.1 * k))
    return push_in(base, lt, 2.0)


def push_in(base, lt, dur):
    z = 1.0 + 0.045 * ease_in_out(lt / dur)
    im = base.convert("RGB")
    if z > 1.001:
        cw, ch = W / z, H / z
        im = im.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
    return im.convert("RGBA")


# ------------------------------------------------------------------ main
def main():
    need = set(ONLY) if ONLY else None
    enc = None
    if not ONLY:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "work/mix_full.wav",
                                "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                                "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                                "-shortest", OUT], stdin=subprocess.PIPE)
    zoom_blur_cuts = {SH[i]["f0"] for i in ("V2", "V7", "V8", "S3", "S4", "S7a", "V10", "V13")}
    leak_cuts = {SH[i]["f0"] for i in ("S5", "V7")}
    for s in SHOTS:
        rng = range(s["f0"], s["f1"])
        if need is not None and not any(f in need for f in rng):
            continue
        n = s["f1"] - s["f0"]
        src = obj = None
        auto_y = None
        if s["kind"] == "th":
            src = load_th(s)
            top = head_top(s, src)
            yb = clamp(top - 120, 330, 860)
            bh = big_word("HOLIS", 360, "lilac").height
            auto_y = {"big": yb, "small": yb - bh / 2 - 28}
        elif s["kind"] == "broll":
            src = load_broll(s)
            if s.get("matte"):
                raw = [np.asarray(get_matte(f"full_{s['id']}", j, Image.fromarray(src[j]), s["matte"]))
                       for j in range(n)]
                obj = [Image.fromarray(m) for m in stabilize(raw, radius=2, sigma=40)]
        for i, f in enumerate(rng):
            if need is not None and f not in need:
                continue
            t = f / FPS
            behind = [c for c in s["cues"] if c["layer"] == "behind"]
            front = [c for c in s["cues"] if c["layer"] == "front"]
            if s["kind"] == "scene":
                if s["scene"] == "glucose":
                    base = scene_glucose(t, s["t0"])
                else:
                    base = scene_product(t, s["t0"], end=s["scene"] == "end")
                for c in s["cues"]:
                    draw_cue(base, c, t, s["t0"], {"big": 600, "small": 300})
            else:
                person = None
                if s["kind"] == "th":
                    z = th_zoom(s, i, n)
                    frm, pa, fg = src[i]
                    im = zoom_frame(frm, z, s["center"])
                    person = zoom_frame(fg, z, s["center"]).convert("RGBA")
                    person.putalpha(zoom_frame(pa, z, s["center"]))
                else:
                    punch = 1 + 0.06 * (1 - ease_out(i / 6))
                    im = zoom_frame(src[i], punch, (0.5, 0.5)) if punch > 1.0005 else Image.fromarray(src[i])
                    if obj is not None:
                        person = im.convert("RGBA")
                        person.putalpha(obj[i] if punch <= 1.0005 else zoom_frame(np.asarray(obj[i]), punch, (0.5, 0.5)))
                base = im.convert("RGBA")
                for c in behind:
                    draw_cue(base, c, t, s["t0"], auto_y)
                if person is not None:
                    base.alpha_composite(person)
                draw_cards(base, s, t)
                for c in front:
                    draw_cue(base, c, t, s["t0"], auto_y)
            for cf in zoom_blur_cuts:
                if -3 <= f - cf <= 3:
                    base = zoom_blur(base, 1 - abs(f - cf) / 4)
            for lk0 in leak_cuts:
                if lk0 - 4 <= f <= lk0 + 7:
                    ph = (f - (lk0 - 4)) / 11
                    base = light_leak(base, math.sin(math.pi * ph) * 1.2, ph)
            if f >= NF - 8:  # soft fade-out of the very end
                fo = (NF - f) / 8
                base = Image.blend(Image.new("RGBA", (W, H), (255, 255, 255, 255)), base, 0.4 + 0.6 * fo)
            rgb = base.convert("RGB")
            if ONLY:
                rgb.save(f"{OUT}_{f:04d}.png")
            else:
                enc.stdin.write(rgb.tobytes())
        print(s["id"], s["f0"], s["f1"], flush=True)
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__" and OUT:
    main()
