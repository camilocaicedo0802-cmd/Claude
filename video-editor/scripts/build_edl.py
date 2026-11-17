"""Genera src/data/edl.json: la línea de tiempo completa en fotogramas (30 fps).

Fuentes: analysis/segments_aligned.json (palabras alineadas con MMS_FA) y las
decisiones de montaje de abajo. Todos los tiempos de palabra se convierten a
fotogramas de la línea de tiempo: f = seg.from + (t_src - seg.src) * FPS.
"""
import json
import math
import os

ROOT = "/home/user/Claude/video-editor"
FPS = 30
aligned = {it["id"]: it["words"] for it in json.load(open(f"{ROOT}/analysis/segments_aligned.json"))}

# ---------------------------------------------------------------- segmentos
# id, archivo, from (fotograma), duración (fotogramas), inicio en el bruto (s), palabras
SEGS = [
    dict(id="s1_hook", from_=0, dur=160, src=1.70, words=["hook", "filmmaker"]),
    dict(id="s2_editor", from_=160, dur=30, src=9.95, words=["editor"]),
    dict(id="s3_cm", from_=190, dur=43, src=16.85, words=["cm"]),
    dict(id="s4_meta", from_=233, dur=73, src=22.95, words=["meta"]),
    dict(id="s5_sueldos", from_=306, dur=117, src=90.20, words=["sueldosB"]),
    dict(id="s6_marca", from_=423, dur=116, src=122.55, words=["marca"]),
    dict(id="s8_cta", from_=711, dur=102, src=196.35, words=["cta"]),
]
TOTAL = 813
MONTAGE = dict(from_=539, to=711)
# cortes del montaje cada 2 golpes (125 BPM, golpe = 0,48 s) a partir del drop en 13,15 s
DROP_S = 13.15
BEAT = 0.48
cuts = [round((DROP_S + (10 + 2 * k) * BEAT) * FPS) for k in range(7)]  # 10 golpes tras el drop = 17,95 s
cuts[0] = MONTAGE["from_"]
cuts[-1] = MONTAGE["to"]
SHOTS = [
    ("full_camara", "FILMMAKER"),
    ("full_edicion", "EDITOR"),
    ("full_movil", "COMMUNITY MANAGER"),
    ("full_analiticas", "META ADS"),
    ("full_vlogger", "CONTENIDO"),
    ("full_redes", "RESULTADOS"),
]
montage = [dict(file=f"broll/{f}.mp4", from_=cuts[i], dur=cuts[i + 1] - cuts[i], label=lab) for i, (f, lab) in enumerate(SHOTS)]

# Voz en off "trabajando para tu negocio" bajo el montaje (otra toma, src 178.05)
VO = dict(file="clips/s7_vo.wav", from_=539, src=178.05)


def seg_by_id(i):
    return next(s for s in SEGS if s["id"] == i)


def tl(seg, t):
    return seg["from_"] + (t - seg["src"]) * FPS


# ---------------------------------------------------------------- palabras en la línea de tiempo
words = []  # cada palabra: text, from, to (fotogramas, float), seg
for seg in SEGS:
    for key in seg["words"]:
        for w in aligned[key]:
            words.append(dict(text=w["text"], f0=tl(seg, w["start"]), f1=tl(seg, w["end"]), seg=seg["id"]))
for w in aligned["marcaAlt"]:
    if w["text"].strip(".").lower() in ("trabajando", "para", "tu", "negocio"):
        words.append(dict(text=w["text"], f0=VO["from_"] + (w["start"] - VO["src"]) * FPS,
                          f1=VO["from_"] + (w["end"] - VO["src"]) * FPS, seg="montage"))
words.sort(key=lambda w: w["f0"])
for i, w in enumerate(words):
    w["i"] = i


def find(text, after=0):
    """Índice de la primera palabra que empieza por `text` a partir del fotograma `after`."""
    t = text.lower().strip("¿?¡!.,")
    for w in words:
        if w["f0"] >= after and w["text"].lower().strip("¿?¡!.,").startswith(t):
            return w
    raise KeyError(text)


# ---------------------------------------------------------------- palabras destacadas
# kicker: texto pequeño (se teclea); big: palabra gigante; covers: palabras habladas que
# sustituye en los subtítulos. style: red | white. behind: detrás de la persona.
H = []


def hl(kicker, big, k_word, b_word, until, style, behind, layout, covers, k_after=0, b_offset=0, kicker_italic=True):
    kw = find(k_word, k_after) if k_word else None
    bw = find(b_word, kw["f0"] if kw else k_after)
    k_from = math.floor(kw["f0"]) if kw else None
    b_from = math.floor(bw["f0"]) + b_offset
    H.append(dict(kicker=kicker, big=big, kFrom=k_from, bFrom=b_from, to=until, style=style, behind=behind,
                  layout=layout, kickerItalic=kicker_italic,
                  covers=[w["i"] for w in words if covers[0] <= w["f0"] < covers[1]]))


s1 = seg_by_id("s1_hook")
# Gancho
hl("DUEÑO DE", "NEGOCIOS", "dueño", "negocios", 39, "red", False,
   dict(align="left", x=100, kickerY=975, bigY=1015, size=220), (14, 39), kicker_italic=False)
hl("¿CUÁNTAS", "PERSONAS?", "¿cuántas", "personas", 76, "white", False,
   dict(align="right", x=1000, kickerY=975, bigY=1015, size=200), (39, 60))
# Roles (cada uno con su tarjeta de b-roll y etiqueta "SUELDO #n")
hl("UN", "FILMMAKER", "un", "filmmaker", 160, "red", True,
   dict(align="center", x=540, kickerY=500, bigY=545, size=200), (130, 160), k_after=130)
hl("UN", "EDITOR", "un", "editor", 190, "white", False,
   dict(align="center", x=540, kickerY=290, bigY=335, size=280), (160, 190), k_after=160)
hl("UN", "COMMUNITY\nMANAGER", "un", "community", 233, "red", True,
   dict(align="center", x=540, kickerY=430, bigY=475, size=185), (190, 233), k_after=190)
hl("LOS ANUNCIOS EN", "META", "los", "meta", 306, "white", False,
   dict(align="center", x=540, kickerY=290, bigY=335, size=330), (270, 306), k_after=268, b_offset=-3)
# Sueldos: 4 -> 1
hl("¿SERÍAN", "4 SUELDOS", "¿serían", "cuatro", 393, "white", False,
   dict(align="center", x=540, kickerY=960, bigY=1005, size=200), (306, 393), k_after=306)
hl("¿O SOLO", "1", "o", "uno", 423, "red", False,
   dict(align="center", x=540, kickerY=560, bigY=600, size=600), (393, 423), k_after=390, b_offset=-4)
# Marca
hl("EN", "305 MEDIA CLUB", "en", "305", 460, "red", False,
   dict(align="center", x=540, kickerY=230, bigY=275, size=150), (424, 460), k_after=424)
hl("TODO TU", "EQUIPO", "todo", "equipo", 539, "white", False,
   dict(align="center", x=540, kickerY=905, bigY=950, size=250), (504, 521), k_after=500)
# Cierre
hl("¿QUÉ ESTÁS", "ESPERANDO?", "¿qué", "esperando", 768, "red", True,
   dict(align="center", x=540, kickerY=470, bigY=515, size=170), (728, 754), k_after=711)
hl(None, "YA MISMO", None, "ya", 813, "white", False,
   dict(align="center", x=540, kickerY=0, bigY=960, size=215), (786, 813), k_after=780)

covered = set(i for h in H for i in h["covers"])

# ---------------------------------------------------------------- subtítulos (bloques de 1 a 3 palabras)
blocks = []
cur = []


FUNC = {"para", "tu", "de", "con", "que", "el", "la", "los", "y", "un", "en", "por", "a", "te"}


def flush(carry_func=False):
    """Cierra el bloque; con carry_func, las palabras de enlace finales pasan al siguiente."""
    global cur
    carry = []
    if carry_func:
        while len(cur) > 1 and cur[-1]["text"].lower().strip("¿?¡!.,") in FUNC:
            carry.insert(0, cur.pop())
    if cur:
        blocks.append(dict(words=[dict(text=w["text"].strip("¿?¡!.,").lower() if not w["text"].isupper() else w["text"],
                                       f=math.floor(w["f0"])) for w in cur],
                           start=math.floor(cur[0]["f0"]), end=None))
    cur = carry


prev = None
for w in words:
    if w["i"] in covered:
        flush()
        prev = w
        continue
    gap = (w["f0"] - prev["f1"]) if prev else 99
    if cur and (gap > 9 or prev["text"].endswith((",", ".", "?")) or prev["seg"] != w["seg"]):
        flush()
    elif cur and (len(cur) >= 3 or sum(len(x["text"]) for x in cur) + len(w["text"]) > 18):
        flush(carry_func=True)
    cur.append(w)
    prev = w
flush()
# cada bloque dura hasta que empieza el siguiente o 0,5 s después de su última palabra
for i, b in enumerate(blocks):
    last_word = next(w for w in words if math.floor(w["f0"]) == b["words"][-1]["f"])
    end = math.ceil(last_word["f1"]) + 12
    if i + 1 < len(blocks):
        end = min(end, blocks[i + 1]["start"])
    for h in H:
        if h["layout"]["bigY"] > 850 and b["start"] < h["bFrom"] < end:
            end = h["bFrom"]
    b["end"] = end

# ---------------------------------------------------------------- tarjetas de b-roll (detrás de la persona)
CARDS = [
    dict(file="broll/card_filmmaker.mp4", from_=126, to=160, x=650, y=640, w=360, h=450, rot=3, label="SUELDO #1"),
    dict(file="broll/card_editor.mp4", from_=160, to=190, x=690, y=660, w=340, h=425, rot=3, label="SUELDO #2"),
    dict(file="broll/card_cm.mp4", from_=191, to=233, x=600, y=830, w=400, h=500, rot=3, label="SUELDO #3"),
    dict(file="broll/card_meta.mp4", from_=240, to=306, x=50, y=680, w=340, h=425, rot=-3, label="SUELDO #4"),
    dict(file="broll/card_dinero.mp4", from_=455, to=500, x=650, y=150, w=300, h=375, rot=3, label="1 SUELDO"),
]

# ---------------------------------------------------------------- monedas de neón (4 sueldos -> 1)
fw_cuatro = math.floor(find("cuatro", 306)["f0"])
f_o = math.floor(find("o", 390)["f0"])
NEON = dict(pops=[fw_cuatro + 2 + 4 * k for k in range(4)], collapse=f_o, end=423, y=290)

# ---------------------------------------------------------------- transiciones
TRANS = [
    dict(at=160, kind="blur", out=3, inn=4),
    dict(at=190, kind="blur", out=3, inn=4),
    dict(at=233, kind="blur", out=3, inn=4),
    dict(at=306, kind="blur", out=4, inn=6),
    dict(at=423, kind="blur", out=4, inn=6),
    dict(at=539, kind="leak", out=6, inn=10),
    dict(at=711, kind="blur", out=4, inn=6),
]

# ---------------------------------------------------------------- zoom/reencuadre por segmento
# scale y origen (x%, y%) en keyframes de fotograma local
ZOOM = {
    "s1_hook": [dict(f=0, s=1.42, ox=50, oy=48), dict(f=105, s=1.52, ox=50, oy=48), dict(f=118, s=1.30, ox=45, oy=40), dict(f=160, s=1.36, ox=45, oy=40)],
    "s2_editor": [dict(f=0, s=1.30, ox=50, oy=40), dict(f=30, s=1.36, ox=50, oy=40)],
    "s3_cm": [dict(f=0, s=1.32, ox=50, oy=38), dict(f=43, s=1.38, ox=50, oy=38)],
    "s4_meta": [dict(f=0, s=1.30, ox=50, oy=40), dict(f=73, s=1.38, ox=50, oy=40)],
    "s5_sueldos": [dict(f=0, s=1.18, ox=50, oy=38), dict(f=117, s=1.24, ox=50, oy=38)],
    "s6_marca": [dict(f=0, s=1.14, ox=50, oy=36), dict(f=116, s=1.22, ox=50, oy=36)],
    "s8_cta": [dict(f=0, s=1.14, ox=50, oy=36), dict(f=43, s=1.18, ox=50, oy=36), dict(f=44, s=1.34, ox=50, oy=34), dict(f=102, s=1.40, ox=50, oy=34)],
}

# ---------------------------------------------------------------- SFX (solo de la carpeta del cliente)
SFX_PEAK = {"whoosh_swhoosh": 12, "whoosh_2": 33, "whoosh_4": 21, "whoosh_5": 14, "whoosh_short3": 17,
            "whoosh_short4": 16, "bass_drop10": 1, "bass_deep1": 8, "bass_sub": 1, "pop": 5, "swoosh_03": 2,
            "swoosh_05": 2, "tecla": 2, "key_click1": 1, "key_click2": 1, "riser_sharp": 52, "boom2": 3,
            "shutter": 7, "type_letras": 0}
sfx = []


def S(name, at, db, peak=True):
    """Coloca un SFX para que su pico caiga en el fotograma `at`."""
    start = at - (SFX_PEAK.get(name, 0) if peak else 0)
    sfx.append(dict(file=f"sfx/{name}.wav", from_=max(0, start), db=db))


def typing(text, start, every=2, db=-17):
    """Una pulsación por carácter visible (los espacios no suenan)."""
    keys = ["tecla", "key_click1", "key_click2"]
    n = 0
    for i, ch in enumerate(text):
        if ch.strip():
            S(keys[n % 3], start + i * every, db + (6 if keys[n % 3] != "tecla" else 0))
            n += 1


S("bass_sub", 0, -9, peak=False)
for h in H:
    if h["kicker"]:
        typing(h["kicker"], h["kFrom"], every=1)
    big_sfx = "whoosh_swhoosh" if h["style"] == "red" else "whoosh_5"
    S(big_sfx, h["bFrom"], -13)
# graves en las palabras clave
for word, after in (("cuatro", 306), ("305", 424), ("esperando", 711)):
    S("bass_deep1", math.floor(find(word, after)["f0"]), -11)
S("bass_sub", math.floor(find("ya", 780)["f0"]), -13)
# paneo rápido hacia él (fotograma ~114 de s1)
S("whoosh_4", 114, -12)
# obturador de cámara en "filmmaker"
S("shutter", math.floor(find("filmmaker", 130)["f0"]) + 4, -13)
# tarjetas
for c in CARDS:
    S("pop", c["from_"] + 2, -17)
    typing(c["label"], c["from_"] + 6, every=1, db=-19)
# monedas
for p in NEON["pops"]:
    S("swoosh_03", p, -18)
S("riser_sharp", NEON["collapse"], -12)
S("bass_drop10", NEON["collapse"], -4)
S("swoosh_05", NEON["collapse"] + 1, -14)
# entrada al montaje con destello
S("whoosh_2", MONTAGE["from_"], -12)
S("boom2", MONTAGE["from_"], -15)
# etiquetas tecleadas del montaje
for m in montage:
    typing(m["label"], m["from_"] + 4, every=1, db=-19)
# punch-in del cierre
S("swoosh_03", 711 + 44, -16)

# ---------------------------------------------------------------- música (dB por tramos)
MUSIC = dict(file="music/parisian_funk_7883.wav", keys=[
    dict(f=0, db=-17), dict(f=388, db=-17), dict(f=394, db=-9), dict(f=414, db=-10), dict(f=426, db=-17),
    dict(f=536, db=-17), dict(f=539, db=-12), dict(f=578, db=-12), dict(f=590, db=-2), dict(f=700, db=-2),
    dict(f=714, db=-17), dict(f=796, db=-17), dict(f=813, db=-40)])

edl = dict(fps=FPS, total=TOTAL,
           segments=[dict(id=s["id"], file=f"clips/{s['id']}.mp4", fg=f"clips/{s['id']}_fg.webm", from_=s["from_"],
                          dur=s["dur"], zoom=ZOOM[s["id"]]) for s in SEGS],
           montage=montage, vo=VO, highlights=H, subtitles=blocks, cards=CARDS, neon=NEON, transitions=TRANS,
           sfx=sorted(sfx, key=lambda x: x["from_"]), music=MUSIC)
os.makedirs(f"{ROOT}/src/data", exist_ok=True)
json.dump(edl, open(f"{ROOT}/src/data/edl.json", "w"), ensure_ascii=False, indent=1)
print("segmentos:", len(SEGS), "| destacados:", len(H), "| bloques de subtítulos:", len(blocks), "| sfx:", len(sfx))
print("cortes del montaje:", cuts)
for b in blocks:
    print(f"  sub {b['start']:4d}-{b['end']:4d}: " + " ".join(f"{w['text']}@{w['f']}" for w in b["words"]))
for h in H:
    print(f"  HL {h['kFrom']}/{h['bFrom']}-{h['to']} {h['kicker']} | {h['big']!r} ({h['style']}{', detrás' if h['behind'] else ''})")
