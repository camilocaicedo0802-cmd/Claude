"""Genera src/data/edl.json: la línea de tiempo completa en fotogramas (30 fps).

Regla de corte (corrección del cliente): cada toma ENTRA cuando la persona empieza a hablar
y SALE en cuanto termina; no se espera a que nadie camine ni llegue. Por eso cada segmento se
define por sus palabras: empieza LEAD s antes de la primera palabra y acaba TAIL s después de
la última. Si dentro de una toma hay un silencio largo (alguien caminando), se parte en dos.

Fuentes: analysis/segments_aligned.json (palabras alineadas con MMS_FA, tiempos del bruto).
Tiempo de una palabra en la línea de tiempo: f = seg.from + (t_bruto - seg.src_in) * FPS.
"""
import json
import math
import os

ROOT = "/home/user/Claude/video-editor"
FPS = 30
LEAD = 0.10  # s antes de la primera palabra
TAIL = 0.13  # s después de la última palabra
END_HOLD = 0.40  # al final del vídeo, para leer "YA MISMO"
aligned = {it["id"]: it["words"] for it in json.load(open(f"{ROOT}/analysis/segments_aligned.json"))}

# Clips preparados (scripts/prepare_clips.py): segundo del bruto en el que empieza cada uno y su longitud
CLIPS = {
    "s1_hook": (1.70, 160), "s2_editor": (9.95, 30), "s3_cm": (16.85, 43), "s4_meta": (22.95, 73),
    "s5_sueldos": (90.20, 117), "s6_marca": (122.55, 117), "s8_cta": (196.35, 102),
}

# ---------------------------------------------------------------- segmentos (en orden)
# id, clip, clave de palabras alineadas, ventana del bruto para elegir palabras (s), cola final
PLAN = [
    ("s1a_hook", "s1_hook", "hook", (0, 99), TAIL),  # ella: pregunta
    ("s1b_filmmaker", "s1_hook", "filmmaker", (0, 99), TAIL),  # él: "un filmmaker" (sin esperar el paneo)
    ("s2_editor", "s2_editor", "editor", (0, 99), TAIL),
    ("s3_cm", "s3_cm", "cm", (0, 99), TAIL),
    ("s4_meta", "s4_meta", "meta", (0, 99), TAIL),
    ("s5a_sueldos", "s5_sueldos", "sueldosB", (0, 92.6), TAIL),  # él: "¿serían cuatro sueldos..."
    ("s5b_uno", "s5_sueldos", "sueldosB", (92.6, 99), TAIL),  # ella: "...o solo uno?" (sin esperar que llegue)
    ("s6_marca", "s6_marca", "marca", (0, 999), TAIL),
    ("MONTAGE", None, None, None, None),
    ("s8_cta", "s8_cta", "cta", (0, 999), END_HOLD),
]

SEGS = []
cursor = 0
montage_from = None
for sid, clip, key, window, tail in PLAN:
    if sid == "MONTAGE":
        montage_from = cursor
        SEGS.append(None)  # se coloca después, cuando se conoce la rejilla de golpes de la música
        continue
    w0, w1 = window
    csrc, cframes = CLIPS[clip]
    ws = [w for w in aligned[key] if w0 <= w["start"] < w1]
    clip_start = max(0, round((ws[0]["start"] - LEAD - csrc) * FPS))
    src_in = csrc + clip_start / FPS
    dur = round((ws[-1]["end"] + tail - src_in) * FPS)
    dur = min(dur, cframes - clip_start)
    SEGS.append(dict(id=sid, clip=clip, clipStart=clip_start, src_in=src_in, from_=cursor, dur=dur, words=ws))
    cursor += dur


def seg(sid):
    return next(s for s in SEGS if s and s["id"] == sid)


def start(sid):
    return seg(sid)["from_"]


def end(sid):
    s = seg(sid)
    return s["from_"] + s["dur"]


def tl(s, t):
    return s["from_"] + (t - s["src_in"]) * FPS


# ---------------------------------------------------------------- música y montaje al golpe
# La música (DivKid - Parisian Funk) se coloca para que su drop (91,93 s del tema) caiga en
# el "o" de "o solo uno". Golpes del bombo tras el drop: 92,46 s + 0,48 s * k (125 BPM).
SONG = "assets_in/musica/PACK MÚSICA V2/DivKid - Parisian Funk.mp3"
SONG_DROP = 91.93
BEAT = 0.48
s5b = seg("s5b_uno")
f_o = tl(s5b, s5b["words"][0]["start"])
music_start = SONG_DROP - f_o / FPS  # segundo del tema en el fotograma 0
beat_tl = lambda k: (92.46 - music_start + BEAT * k) * FPS  # fotograma del golpe k

SHOTS = [
    ("full_camara", "FILMMAKER"),
    ("full_edicion", "EDITOR"),
    ("full_movil", "COMMUNITY MANAGER"),
    ("full_analiticas", "META ADS"),
    ("full_vlogger", "CONTENIDO"),
    ("full_redes", "RESULTADOS"),
]
# primer corte: el primer golpe que deja al menos 0,8 s de primer plano; luego cada 2 golpes
k = 0
while beat_tl(k) < montage_from + 0.8 * FPS:
    k += 1
cuts = [montage_from] + [round(beat_tl(k + 2 * i)) for i in range(len(SHOTS))]
montage = [dict(file=f"broll/{f}.mp4", from_=cuts[i], dur=cuts[i + 1] - cuts[i], label=lab) for i, (f, lab) in enumerate(SHOTS)]
MONTAGE = dict(from_=cuts[0], to=cuts[-1])
# los segmentos posteriores al montaje se desplazan
shift = MONTAGE["to"] - montage_from
after = False
for s in SEGS:
    if s is None:
        after = True
    elif after:
        s["from_"] += shift
SEGS = [s for s in SEGS if s]
TOTAL = end("s8_cta")

# Voz en off "trabajando para tu negocio" bajo el montaje (otra toma, src 178.05)
VO = dict(file="clips/s7_vo.wav", from_=MONTAGE["from_"], src=178.05)

# ---------------------------------------------------------------- palabras en la línea de tiempo
words = []
for s in SEGS:
    for w in s["words"]:
        words.append(dict(text=w["text"], f0=tl(s, w["start"]), f1=tl(s, w["end"]), seg=s["id"]))
for w in aligned["marcaAlt"]:
    if w["text"].strip(".").lower() in ("trabajando", "para", "tu", "negocio"):
        words.append(dict(text=w["text"], f0=VO["from_"] + (w["start"] - VO["src"]) * FPS,
                          f1=VO["from_"] + (w["end"] - VO["src"]) * FPS, seg="montage"))
words.sort(key=lambda w: w["f0"])
for i, w in enumerate(words):
    w["i"] = i


def find(text, after=0):
    """Primera palabra que empieza por `text` a partir del fotograma `after`."""
    t = text.lower().strip("¿?¡!.,")
    for w in words:
        if w["f0"] >= after and w["text"].lower().strip("¿?¡!.,").startswith(t):
            return w
    raise KeyError(text)


def F(text, after=0):
    return math.floor(find(text, after)["f0"])


# ---------------------------------------------------------------- palabras destacadas
# kicker: texto pequeño (se teclea); big: palabra gigante; until: fin; covers: fotogramas cuyas
# palabras no llevan subtítulo (las dice la palabra grande). behind: detrás de la persona.
H = []


def hl(kicker, big, k_word, b_word, until, style, behind, layout, covers_to=None, k_after=0, b_offset=0,
       kicker_italic=True):
    kw = find(k_word, k_after) if k_word else None
    bw = find(b_word, kw["f0"] if kw else k_after)
    k_from = math.floor(kw["f0"]) if kw else None
    b_from = math.floor(bw["f0"]) + b_offset
    c0 = k_from if k_from is not None else b_from
    c1 = until if covers_to is None else covers_to
    H.append(dict(kicker=kicker, big=big, kFrom=k_from, bFrom=b_from, to=until, style=style, behind=behind,
                  layout=layout, kickerItalic=kicker_italic,
                  covers=[w["i"] for w in words if c0 <= w["f0"] < c1]))


# Gancho
hl("DUEÑO DE", "NEGOCIOS", "dueño", "negocios", F("¿cuántas"), "red", False,
   dict(align="left", x=100, kickerY=975, bigY=1015, size=220), kicker_italic=False)
hl("¿CUÁNTAS", "PERSONAS?", "¿cuántas", "personas", F("para"), "white", False,
   dict(align="right", x=1000, kickerY=975, bigY=1015, size=200), covers_to=F("necesitas"))
# Roles (cada uno con su tarjeta de b-roll y etiqueta "SUELDO #n")
hl("UN", "FILMMAKER", "un", "filmmaker", end("s1b_filmmaker"), "red", True,
   dict(align="center", x=540, kickerY=500, bigY=545, size=200), k_after=start("s1b_filmmaker"))
hl("UN", "EDITOR", "un", "editor", end("s2_editor"), "white", False,
   dict(align="center", x=540, kickerY=290, bigY=335, size=280), k_after=start("s2_editor"))
hl("UN", "COMMUNITY\nMANAGER", "un", "community", end("s3_cm"), "red", True,
   dict(align="center", x=540, kickerY=430, bigY=475, size=185), k_after=start("s3_cm"))
hl("LOS ANUNCIOS EN", "META", "los", "meta", end("s4_meta"), "white", False,
   dict(align="center", x=540, kickerY=290, bigY=335, size=330), k_after=start("s4_meta"), b_offset=-3)
# Sueldos: 4 -> 1
hl("¿SERÍAN", "4 SUELDOS", "¿serían", "cuatro", end("s5a_sueldos"), "white", False,
   dict(align="center", x=540, kickerY=960, bigY=1005, size=200), k_after=start("s5a_sueldos"))
hl("¿O SOLO", "1", "o", "uno", end("s5b_uno"), "red", False,
   dict(align="center", x=540, kickerY=560, bigY=600, size=600), k_after=start("s5b_uno"), b_offset=-4)
# Marca
hl("EN", "305 MEDIA CLUB", "en", "305", F("por", start("s6_marca")), "red", False,
   dict(align="center", x=540, kickerY=230, bigY=275, size=150), k_after=start("s6_marca"))
# Logo del cliente (última variante del .ai, horizontal) en lugar del texto, solo al nombrar la empresa
H[-1]["logo"] = dict(file="logo/305_media_club_h.png", width=860, top=262, aspect=4101 / 1008)
hl("TODO TU", "EQUIPO", "todo", "equipo", end("s6_marca"), "white", False,
   dict(align="center", x=540, kickerY=905, bigY=950, size=250),
   covers_to=F("de", F("equipo", start("s6_marca"))), k_after=start("s6_marca"))
# Cierre
hl("¿QUÉ ESTÁS", "ESPERANDO?", "¿qué", "esperando", F("con", start("s8_cta")), "red", True,
   dict(align="center", x=540, kickerY=470, bigY=515, size=170),
   covers_to=F("comunícate", start("s8_cta")), k_after=start("s8_cta"))
hl(None, "YA MISMO", None, "ya", TOTAL, "white", False,
   dict(align="center", x=540, kickerY=0, bigY=960, size=215), k_after=F("nosotros", start("s8_cta")))

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
seg_end_of = {s["id"]: s["from_"] + s["dur"] for s in SEGS}
seg_end_of["montage"] = MONTAGE["to"]
for i, b in enumerate(blocks):
    last_word = next(w for w in words if math.floor(w["f0"]) == b["words"][-1]["f"])
    e = math.ceil(last_word["f1"]) + 12
    e = min(e, seg_end_of[last_word["seg"]])  # nunca pasa a la toma siguiente
    if i + 1 < len(blocks):
        e = min(e, blocks[i + 1]["start"])
    for h in H:
        if h["layout"]["bigY"] > 850 and b["start"] < h["bFrom"] < e:
            e = h["bFrom"]
    b["end"] = e

# ---------------------------------------------------------------- tarjetas de b-roll (detrás de la persona)
s6 = seg("s6_marca")
CARDS = [
    dict(file="broll/card_filmmaker.mp4", from_=start("s1b_filmmaker"), to=end("s1b_filmmaker"), x=650, y=640, w=360, h=450, rot=3, label="SUELDO #1"),
    dict(file="broll/card_editor.mp4", from_=start("s2_editor"), to=end("s2_editor"), x=690, y=660, w=340, h=425, rot=3, label="SUELDO #2"),
    dict(file="broll/card_cm.mp4", from_=start("s3_cm") + 1, to=end("s3_cm"), x=600, y=830, w=400, h=500, rot=3, label="SUELDO #3"),
    dict(file="broll/card_meta.mp4", from_=start("s4_meta") + 5, to=end("s4_meta"), x=50, y=680, w=340, h=425, rot=-3, label="SUELDO #4"),
    # mismos segundos del bruto que en la versión aprobada (123,62 s -> 125,12 s)
    dict(file="broll/card_dinero.mp4", from_=round(tl(s6, 123.62)), to=round(tl(s6, 125.12)), x=650, y=150, w=300, h=375, rot=3, label="1 SUELDO"),
]

# ---------------------------------------------------------------- monedas de neón (4 sueldos -> 1)
fw_cuatro = F("cuatro", start("s5a_sueldos"))
f_o_frame = F("o", start("s5b_uno"))
NEON = dict(pops=[fw_cuatro + 2 + 4 * k for k in range(4)], collapse=f_o_frame, end=end("s5b_uno"), y=290)

# ---------------------------------------------------------------- transiciones (en cada corte)
TRANS = [
    dict(at=start("s1b_filmmaker"), kind="blur", out=3, inn=4),
    dict(at=start("s2_editor"), kind="blur", out=3, inn=4),
    dict(at=start("s3_cm"), kind="blur", out=3, inn=4),
    dict(at=start("s4_meta"), kind="blur", out=3, inn=4),
    dict(at=start("s5a_sueldos"), kind="blur", out=4, inn=6),
    dict(at=start("s5b_uno"), kind="blur", out=2, inn=3),  # corte en la misma toma + reencuadre
    dict(at=start("s6_marca"), kind="blur", out=4, inn=6),
    dict(at=MONTAGE["from_"], kind="leak", out=6, inn=10),
    dict(at=start("s8_cta"), kind="blur", out=4, inn=6),
]

# ---------------------------------------------------------------- zoom/reencuadre por segmento (fotogramas locales)
def ramp(sid, s0, s1, ox, oy):
    return [dict(f=0, s=s0, ox=ox, oy=oy), dict(f=seg(sid)["dur"], s=s1, ox=ox, oy=oy)]


punch = F("comunícate", start("s8_cta")) - start("s8_cta")
ZOOM = {
    "s1a_hook": ramp("s1a_hook", 1.42, 1.51, 50, 48),
    "s1b_filmmaker": ramp("s1b_filmmaker", 1.30, 1.35, 45, 40),
    "s2_editor": ramp("s2_editor", 1.30, 1.36, 50, 40),
    "s3_cm": ramp("s3_cm", 1.32, 1.38, 50, 38),
    "s4_meta": ramp("s4_meta", 1.30, 1.38, 50, 40),
    "s5a_sueldos": ramp("s5a_sueldos", 1.18, 1.22, 50, 38),
    "s5b_uno": ramp("s5b_uno", 1.26, 1.29, 50, 37),
    "s6_marca": ramp("s6_marca", 1.14, 1.22, 50, 36),
    "s8_cta": [dict(f=0, s=1.14, ox=50, oy=36), dict(f=punch - 1, s=1.18, ox=50, oy=36),
               dict(f=punch, s=1.34, ox=50, oy=34), dict(f=seg("s8_cta")["dur"], s=1.40, ox=50, oy=34)],
}

# ---------------------------------------------------------------- SFX (solo de la carpeta del cliente)
SFX_PEAK = {"whoosh_swhoosh": 12, "whoosh_2": 33, "whoosh_4": 21, "whoosh_5": 14, "whoosh_short3": 17,
            "whoosh_short4": 16, "bass_drop10": 1, "bass_deep1": 8, "bass_sub": 1, "pop": 5, "swoosh_03": 2,
            "swoosh_05": 2, "tecla": 2, "key_click1": 1, "key_click2": 1, "riser_sharp": 52, "boom2": 3,
            "shutter": 7, "type_letras": 0}
sfx = []


def S(name, at, db, peak=True):
    """Coloca un SFX para que su pico caiga en el fotograma `at`."""
    st = at - (SFX_PEAK.get(name, 0) if peak else 0)
    sfx.append(dict(file=f"sfx/{name}.wav", from_=max(0, st), db=db))


def typing(text, st, every=2, db=-17):
    """Una pulsación por carácter visible (los espacios no suenan)."""
    keys = ["tecla", "key_click1", "key_click2"]
    n = 0
    for i, ch in enumerate(text):
        if ch.strip():
            S(keys[n % 3], st + i * every, db + (6 if keys[n % 3] != "tecla" else 0))
            n += 1


S("bass_sub", 0, -12, peak=False)  # la voz entra encima a los 0,1 s
for h in H:
    if h["kicker"]:
        typing(h["kicker"], h["kFrom"], every=1)
    S("whoosh_swhoosh" if h["style"] == "red" else "whoosh_5", h["bFrom"], -13)
# graves en las palabras clave
for word, aft, db in (("cuatro", start("s5a_sueldos"), -11), ("305", start("s6_marca"), -14), ("esperando", start("s8_cta"), -11)):
    S("bass_deep1", F(word, aft), db)  # "305" más bajo: ahora se solapa con la cola del drop
S("bass_sub", F("ya", start("s8_cta")), -13)
# corte de ella a él (antes era el paneo de cámara)
S("whoosh_4", start("s1b_filmmaker"), -12)
# obturador de cámara en "filmmaker"
S("shutter", F("filmmaker", start("s1b_filmmaker")) + 4, -13)
# tarjetas
for c in CARDS:
    S("pop", c["from_"] + 2, -17)
    typing(c["label"], c["from_"] + 6, every=1, db=-19)
# monedas
for p in NEON["pops"]:
    S("swoosh_03", p, -18)
S("riser_sharp", NEON["collapse"], -12)
S("bass_drop10", NEON["collapse"], -6)
S("swoosh_05", NEON["collapse"] + 1, -14)
# entrada al montaje con destello
S("whoosh_2", MONTAGE["from_"], -12)
S("boom2", MONTAGE["from_"], -15)
for m in montage:
    typing(m["label"], m["from_"] + 4, every=1, db=-19)
# punch-in del cierre
S("swoosh_03", start("s8_cta") + punch, -16)

# ---------------------------------------------------------------- música (dB por tramos)
music_file = f"music/parisian_funk_{round(music_start * 100)}.wav"
MUSIC = dict(file=music_file, songStart=round(music_start, 3), keys=[
    dict(f=0, db=-17), dict(f=f_o_frame - 6, db=-17), dict(f=f_o_frame, db=-9), dict(f=f_o_frame + 20, db=-10),
    dict(f=start("s6_marca") + 3, db=-17), dict(f=MONTAGE["from_"] - 3, db=-17), dict(f=MONTAGE["from_"], db=-12),
    dict(f=MONTAGE["from_"] + 39, db=-12), dict(f=MONTAGE["from_"] + 51, db=-2), dict(f=MONTAGE["to"] - 11, db=-2),
    dict(f=MONTAGE["to"] + 3, db=-17), dict(f=TOTAL - 17, db=-17), dict(f=TOTAL, db=-40)])
music_path = f"{ROOT}/public/{music_file}"
if not os.path.exists(music_path):
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{music_start:.3f}", "-t", f"{TOTAL / FPS + 1:.2f}",
                    "-i", f"{ROOT}/{SONG}", "-ac", "2", "-ar", "48000", music_path], check=True)

edl = dict(fps=FPS, total=TOTAL,
           segments=[dict(id=s["id"], clip=s["clip"], file=f"clips/{s['clip']}.mp4", fg=f"clips/{s['clip']}_fg.webm",
                          wav=f"clips/{s['clip']}.wav", clipStart=s["clipStart"], from_=s["from_"], dur=s["dur"],
                          zoom=ZOOM[s["id"]]) for s in SEGS],
           montage=montage, vo=VO, highlights=H, subtitles=blocks, cards=CARDS, neon=NEON, transitions=TRANS,
           sfx=sorted(sfx, key=lambda x: x["from_"]), music=MUSIC)
os.makedirs(f"{ROOT}/src/data", exist_ok=True)
json.dump(edl, open(f"{ROOT}/src/data/edl.json", "w"), ensure_ascii=False, indent=1)
print(f"total {TOTAL} fotogramas ({TOTAL / FPS:.2f} s) | música desde {music_start:.2f} s del tema | cortes del montaje {cuts}")
for s in SEGS:
    first, last = s["words"][0], s["words"][-1]
    print(f"  {s['id']:14s} {s['from_'] / FPS:5.2f}-{(s['from_'] + s['dur']) / FPS:5.2f}s  clip {s['clip']}+{s['clipStart']}"
          f"  margen antes {tl(s, first['start']) / FPS - s['from_'] / FPS:.2f}s · después {(s['from_'] + s['dur'] - tl(s, last['end'])) / FPS:.2f}s"
          f"  «{first['text']} … {last['text']}»")
for h in H:
    print(f"  HL {h['kFrom']}/{h['bFrom']}-{h['to']} {h['kicker']} | {h['big']!r}")
