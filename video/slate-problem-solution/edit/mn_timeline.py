"""Reel 3 v4 — new minimal SLATE line (client brief + 3 new references). Rebuilt from scratch.
Structure: hook on the presenter -> for each of the 8 items: numbered PROBLEM over a problem b-roll (off-camera
voice), SOLUTION on the presenter with one-word captions, then a b-roll with the solution keyword (kinetic,
underlined) -> closing montage with a stacked sentence, sticker cut-out moment, storefront, fade to black.
Both original voices kept. No emojis. Text inside the client's safe zone."""
import os, json
import numpy as np, cv2
from mn_engine import *
import ps_timeline as P                      # voice-derived segment times + word alignment (both voices)

OFF, C, SEG, NSEG, TH = P.OFF, P.C, P.SEG, P.NSEG, P.TH
ST, B, SAL = P.ST, P.B, P.SAL
WB = P.WORDS_BY_SEG
LIB = os.environ.get("LIBDIR", os.path.join(os.path.dirname(ST), "lib"))
LUT = f"{LIB}/lut/calor_desvanecido.cube"           # client's LUT pack: soft warm look, natural skin
GRADE = (f"split[ga][gb];[gb]lut3d={LUT}[gl];[ga][gl]blend=all_expr='A*0.45+B*0.55',"
         "eq=contrast=1.01:brightness=0.005:saturation=1.0")
GRADE_T = GRADE_B = GRADE
VOICE_END = P.VOICE_END
END = round(VOICE_END + 0.95, 3)

def ws(k, tok, after=0.0):
    for w in WB[k]:
        if w["w"].lower().strip(".,?!") == tok.lower() and w["s"] >= after: return w["s"]
    raise KeyError((k, tok))

MED, CLOSE = (1.00, 0.42), (1.20, 0.40)
def th(t0, t1, clip, fr=MED, push=0.03):
    return dict(t0=t0, t1=t1, kind="t", clip=clip, z0=fr[0], z1=fr[0] + push, cx=0.5, cy=fr[1], grade=GRADE)
def b(t0, t1, path, src, z0=1.02, z1=1.08, cx=0.5, cy=0.5):
    return dict(t0=t0, t1=t1, kind="b", path=path, src=src, z0=z0, z1=z1, cx=cx, cy=cy, grade=GRADE)

DRESS = f"{ST}/dress/d/IMG_1992.jpg"
def load_still(s):
    """Graded still at the decoder size (same LUT as the video)."""
    raw = __import__("subprocess").run(["ffmpeg", "-v", "error", "-i", s["path"], "-vf",
        f"scale={SRC_W}:{SRC_H}:flags=lanczos,{GRADE},format=rgb24", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(SRC_H, SRC_W, 3)

# cut points inside answers (on the spoken word)
a2 = ws(3, "formula") - 0.05; a3 = ws(5, "before") - 0.06; a5 = ws(9, "room") - 0.16; a6 = ws(11, "1-2") - 0.06
a7a = ws(13, "1-2") - 0.06; a7b = ws(13, "follow") - 0.10; a7c = ws(13, "and", ws(13, "send")) - 0.06
a8 = ws(15, "personalized") - 0.08; c4 = ws(19, "slate") - 0.08
m1 = [C[16] + (C[17] - C[16]) * i / 4 for i in range(5)]

SHOTS = [
 dict(t0=0.0, t1=C[0], kind="b", path=TH["IMG_7103"], src=0.10, z0=1.00, z1=1.05, cx=0.5, cy=0.42, grade=GRADE),  # hook on her
 b(C[0], C[1], B("st1_antes/IMG_4082.MOV"), 1.5, 1.04, 1.09, 0.5, 0.42),          # 1 pale / dull (before)
 b(C[1], C[2], B("st3_proc/MVI_4552.MP4"), 1.0, 1.00, 1.06, 0.5, 0.45),            #   custom spray tan
 b(C[2], C[3], B("st2_trans/IMG_1937.MOV"), 0.2, 1.02, 1.08, 0.5, 0.42),           # 2 need color ASAP
 th(C[3], a2, "IMG_7103", CLOSE),                                                   #   "we have a rapid"
 b(a2, C[4], B("st2_proc/IMG_1965.MOV"), 0.8, 1.00, 1.06),                         #   formula (fast application)
 b(C[4], C[5], B("st1_antes/IMG_4083.MOV"), 0.8, 1.04, 1.09, 0.5, 0.42),           # 3 dry / patchy
 th(C[5], a3, "IMG_7103", MED),                                                     #   "exfoliate 24 hours"
 b(a3, C[6], SAL("IMG_0802"), 0.2, 1.00, 1.06, 0.5, 0.55),                         #   before your appointment
 b(C[6], C[7], B("st1_desp/IMG_4123.mov"), 0.35, 1.02, 1.08, 0.5, 0.48),           # 4 fading unevenly (tan line)
 b(C[7], C[8], SAL("IMG_0801"), 0.1, 1.00, 1.06, 0.5, 0.55),                       #   moisturize daily (lotions)
 b(C[8], C[9], B("st3_proc/MVI_4541.MP4"), 26.8, 1.25, 1.30, 0.42, 0.62),          # 5 hands & feet (hand sprayed)
 th(C[9], a5, "IMG_7103", CLOSE),                                                   #   "we have barrier cream in the"
 b(a5, C[10], B("st2_cons/IMG_1949.MOV"), 20.5, 1.02, 1.08, 0.40, 0.45),           #   room ... (tech with the bottle)
 b(C[10], C[11], B("st3_desp/IMG_2209.MOV"), 2.4, 1.00, 1.06, 0.5, 0.40),          # 6 vacation (glow)
 th(C[11], a6, "IMG_7106", MED),                                                    #   "book your spray tan"
 b(a6, C[12], B("st2_lleg/IMG_1942.MOV"), 0.6, 1.00, 1.05, 0.5, 0.63),                        #   1-2 days before your trip
 dict(t0=C[12], t1=C[13], kind="img", path=DRESS, src=0, z0=1.30, z1=1.42, cx=0.5, cy=0.40, cy1=0.52),  # 7 wedding/event
 th(C[13], a7a, "IMG_7106", CLOSE),                                                 #   "make sure you book your appointment"
 b(a7a, a7b, B("st2_lleg/IMG_1943.MOV"), 1.6, 1.00, 1.05, 0.5, 0.63),                         #   1-2 days before your wedding
 b(a7b, a7c, B("st2_cons/IMG_1948.MOV"), 12.5, 1.06, 1.12, 0.5, 0.40),             #   follow the prep instructions
 th(a7c, C[14], "IMG_7106", MED),                                                   #   "and we'll do a custom shade for you"
 b(C[14], C[15], B("st2_cons/IMG_1949.MOV"), 9.0, 1.08, 1.14, 0.40, 0.42),         # 8 which shade / solution
 th(C[15], a8, "IMG_7108", MED),                                                    #   "every client gets a"
 b(a8, C[16], B("st2_cons/IMG_1948.MOV"), 31.0, 1.04, 1.10, 0.5, 0.40),            #   personalized consultation
 b(m1[0], m1[1], B("st1_desp/IMG_4122.mov"), 5.2, 1.00, 1.05, 0.5, 0.42),          # closing montage: every skin tone
 b(m1[1], m1[2], B("st2_trans/IMG_1988.MOV"), 4.6, 1.00, 1.05, 0.5, 0.40),
 b(m1[2], m1[3], B("st3_desp/IMG_2210.MOV"), 6.4, 1.00, 1.05, 0.5, 0.40),
 b(m1[3], m1[4], B("st4_vid/IMG_3826.MOV"), 1.2, 1.00, 1.05, 0.5, 0.45),
 th(C[17], C[18], "IMG_7110", CLOSE),                                               # your spray tan should be too
 th(C[18], C[19], "IMG_7110", MED, push=0.0),                                       # if you relate... (sticker)
 th(C[19], c4, "IMG_7110", CLOSE),                                                  # come see us at
 b(c4, END, SAL("IMG_0822"), 0.05, 1.00, 1.05, 0.5, 0.42),                          # Slate storefront -> fade out
]
for s in SHOTS: s.setdefault("src", 0)

def _shot(t):
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]: return s
    return SHOTS[-1]

def load_words(path=None, vmap=None):
    return [w for k in range(NSEG) if P.ROLE[k] != "Q" for w in WB[k]]

def build_overlays(words):
    ov = []
    # HOOK (on the presenter, lower-left over her black top)
    ov.append(Block([[("Spray tan", "b")], [("problems?", "P")], [("we've got solutions.", "m")]],
                    [0.08, 0.34, 0.80], C[0] - 0.14, x=90, y_bottom=1470))
    # PROBLEMS: numbered, word by word with the off-camera voice, progress row
    PROB = [
        (0, [[("Pale or", "m")], [("dull skin", "p")]], ["pale", "dull"]),
        (2, [[("Need color", "m")], [("ASAP", "p")]], ["need", "asap"]),
        (4, [[("Dry or", "m")], [("patchy skin", "p")]], ["dry", "patchy"]),
        (6, [[("Tan fading", "m")], [("unevenly", "p")]], ["tan", "unevenly"]),
        (8, [[("Tan sticking to", "m")], [("hands & feet", "p")]], ["tan", "hands"]),
        (10, [[("Going on", "m")], [("vacation", "p")]], ["going", "vacation"]),
        (12, [[("Wedding or", "m")], [("special event", "p")]], ["wedding", "special"]),
        (14, [[("Not sure which", "m")], [("shade or solution", "p")], [("is right for you?", "m")]], ["not", "shade", "is"]),
    ]
    for n, (q, rows, keys) in enumerate(PROB, 1):
        tt = [ws(q, k) - 0.06 for k in keys]
        ov.append(NumberTitle(n, 8, rows, tt, C[q] + 0.02, C[q + 1] - 0.16))
    # SOLUTIONS on b-roll: keyword blocks (kinetic + underline)
    SOL = [
        ([[("A custom", "m")], [("spray tan", "P")]], [C[1] + 0.06, ws(1, "spray") - 0.04], C[2] - 0.14, 1),
        ([[("rapid", "P")], [("formula", "b")]], [a2 + 0.04, a2 + 0.20], C[4] - 0.14, 0),
        ([[("24h", "B")], [("before your appointment", "m")]], [a3 + 0.04, ws(5, "your") - 0.06], C[6] - 0.14, None),
        ([[("moisturize", "P")], [("daily", "b")]], [C[7] + 0.06, ws(7, "daily") - 0.04], C[8] - 0.14, 0),
        ([[("barrier cream", "p")], [("in the room,", "m")], [("before your appointment", "m")]],
         [a5 + 0.04, a5 + 0.16, ws(9, "before") - 0.06], C[10] - 0.14, 0),
        ([[("1-2", "B")], [("days before your trip", "m")]], [a6 + 0.04, ws(11, "days") - 0.06], C[12] - 0.14, None),
        ([[("1-2 days", "b")], [("before your wedding", "m")]], [a7a + 0.04, ws(13, "before") - 0.06], a7b - 0.12, None),
        ([[("follow the", "m")], [("prep", "P")], [("instructions", "b")]], [a7b + 0.04, ws(13, "prep") - 0.06, ws(13, "instructions") - 0.06], a7c - 0.12, 1),
        ([[("personalized", "P")], [("consultation", "b")]], [a8 + 0.04, ws(15, "consultation") - 0.06], C[16] - 0.14, 0),
    ]
    global UNDERLINES, BIGNUM
    UNDERLINES, BIGNUM = [], []
    for rows, tt, t_out, ul in SOL:
        u = None
        if ul is not None:
            u = (ul, tt[ul] + 0.22); UNDERLINES.append(tt[ul] + 0.22)
        if rows[0][0][1] == "B": BIGNUM.append(tt[0])
        ov.append(Block(rows, tt, t_out, x=90, y_bottom=1470, underline=u))
    # CLOSING montage: one sentence building up over four clients
    ov.append(Block([[("Every skin tone,", "m")], [("undertone,", "P")], [("& glow goal", "m")], [("is different.", "P")]],
                    [ws(16, "every") - 0.04, ws(16, "undertone") - 0.06, ws(16, "and") - 0.06, ws(16, "is") - 0.06],
                    C[17] - 0.14, x=90, y_bottom=1470))
    # storefront: Slate
    ov.append(Block([[("Slate", "P")], [("we'll find the", "m")], [("perfect tan for you.", "m")]],
                    [c4 + 0.06, ws(19, "we'll") - 0.06, ws(19, "perfect") - 0.06], END + 1, x=90, y_bottom=1470,
                    underline=(0, c4 + 0.40)))
    UNDERLINES.append(c4 + 0.40)
    # one-word captions, only while the presenter is on screen
    def shot_at(t):
        for s in SHOTS:
            if s["t0"] <= t < s["t1"]: return s
        return SHOTS[-1]
    def ypos(t):
        s = shot_at(t)
        return 1290 if s["z0"] < 1.10 else 1515
    def hide(t):
        s = shot_at(t)
        return s["kind"] != "t"
    ov.append(WordCaptions(words, ypos, hide,
                           emph=["rapid", "exfoliate", "barrier", "book", "appointment", "custom", "shade", "client", "too.", "relate"]))
    return ov

PRE = [BottomShade(lambda t: _shot(t)["kind"] in ("b", "img")), Cutout(C[18], C[19], os.environ.get("U2NET_HOME", os.path.join(os.path.dirname(ST), "models", "rembg")))]
POSTS = [SoftZoom(C[0], 0.10, 0.07), SoftZoom(C[16], 0.10, 0.07), FadeOut(END - 0.70, END)]

def _sfx():
    out = [("bass", 0.0, -31.0), ("tick", 0.08, -31.0), ("tick", 0.34, -32.0), ("tick", 0.80, -33.0)]
    for q in (0, 2, 4, 6, 8, 10, 12, 14):
        out.append(("tick", C[q] + 0.02, -29.0))
    for t in (C[1], a2, a3, C[7], a5, a6, a7a, a7b, a8, c4):          # cuts into a solution b-roll
        out.append(("swoosh_a", t - 0.07, -30.0))
    for t in UNDERLINES: out.append(("underline", t, -33.0))
    for t in BIGNUM: out.append(("pop", t, -29.0))
    out += [("swoosh_b", C[16] - 0.06, -32.0), ("shutter", C[18], -28.0)]
    return out
build_overlays([])                       # fills UNDERLINES / BIGNUM for the mix
SFX = _sfx()
MUSIC_LEVEL = -28.5
