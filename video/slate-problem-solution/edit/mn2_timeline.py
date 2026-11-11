"""Reel 3 v5 — minimal line rebuilt with the client's text presets, SFX and visual assets (see mn2_engine.py).
Same cut (shots, voice, cut points) as v4 (mn_timeline.py)."""
import os
import mn_timeline as M
from mn_engine import Cutout, FadeOut, SoftZoom
from mn2_engine import *

P, C, OFF, TH, END = M.P, M.C, M.OFF, M.TH, M.END
SHOTS, GRADE_T, GRADE_B, load_still, ws = M.SHOTS, M.GRADE_T, M.GRADE_B, M.load_still, M.ws
a2, a3, a5, a6, a7a, a7b, a7c, a8, c4 = M.a2, M.a3, M.a5, M.a6, M.a7a, M.a7b, M.a7c, M.a8, M.c4
LIB2 = os.environ.get("LIBDIR", os.path.join(os.path.dirname(M.ST), "libscan", "dl2"))   # client library (not in repo)
_shot = M._shot
load_words = M.load_words

def build_overlays(words):
    ov = []
    # HOOK — Texto Elegancia Real
    ov.append(EleganciaReal(["spray", "tan", "problems?"], ["we've got", "solutions!"], 0.04, C[0] - 0.18, y_script=1400, ss=175))
    # PROBLEMS — numbered, CapCut bounce_up / slide_up, light vs semibold (Three Aesthetic contrast)
    PROB = [(0, [("Pale or", "L", 62), ("dull skin", "S", 104)], ["pale", "dull"]),
            (2, [("Need color", "L", 62), ("ASAP", "S", 104)], ["need", "asap"]),
            (4, [("Dry or", "L", 62), ("patchy skin", "S", 104)], ["dry", "patchy"]),
            (6, [("Tan fading", "L", 62), ("unevenly", "S", 104)], ["tan", "unevenly"]),
            (8, [("Tan sticking to", "L", 62), ("hands & feet", "S", 104)], ["tan", "hands"]),
            (10, [("Going on", "L", 62), ("vacation", "S", 104)], ["going", "vacation"]),
            (12, [("Wedding or", "L", 62), ("special event", "S", 104)], ["wedding", "special"]),
            (14, [("Not sure which", "L", 58), ("shade or solution", "S", 92), ("is right for you?", "L", 58)], ["not", "shade", "is"])]
    global PROB_T
    PROB_T = []
    for n, (q, rows, keys) in enumerate(PROB, 1):
        ov.append(NumberedProblem(n, 8, rows, [ws(q, k) - 0.06 for k in keys], C[q] + 0.02, C[q + 1] - 0.18))
        PROB_T.append(C[q] + 0.02)
    # SOLUTIONS on b-roll — Dúo Cinemático + Texto Elegante marker
    SOL = [("Custom", "S", 124, "spray tan", 200, C[1] + 0.06, ws(1, "spray") - 0.04, C[2] - 0.14, False),
           ("Rapid", "S", 124, "formula", 200, a2 + 0.04, a2 + 0.26, C[4] - 0.14, False),
           ("24h", "B", 210, "before your appointment", 120, a3 + 0.04, ws(5, "your") - 0.08, C[6] - 0.14, True),
           ("Moisturize", "S", 118, "daily", 200, C[7] + 0.06, ws(7, "daily") - 0.04, C[8] - 0.14, False),
           ("Barrier cream", "S", 112, "in the room", 170, a5 + 0.04, a5 + 0.26, C[10] - 0.14, False),
           ("1-2 days", "B", 170, "before your trip", 150, a6 + 0.04, ws(11, "before") - 0.06, C[12] - 0.14, True),
           ("1-2 days", "B", 170, "before your wedding", 150, a7a + 0.04, ws(13, "before") - 0.06, a7b - 0.12, True),
           ("Prep", "S", 124, "instructions", 190, a7b + 0.04, ws(13, "instructions") - 0.06, a7c - 0.12, False),
           ("Personalized", "S", 112, "consultation", 190, a8 + 0.04, ws(15, "consultation") - 0.06, C[16] - 0.14, False)]
    global SOL_T
    SOL_T = []
    for i, (l1, fk, s1, l2, s2, t1, t2, to, mk) in enumerate(SOL):
        ov.append(SolutionDuo(l1, fk, s1, l2, s2, t1, t2, to, x=90, y_base=1360, marker=mk, seed=i))
        SOL_T.append((t1, mk, fk == "B"))
    # CLOSING — Three Aesthetic Words stack over the montage
    rows = [("Every skin tone,", "L", 76, WHITE), ("undertone,", "B", 128, WHITE), ("& glow goal", "L", 76, WHITE),
            ("is different.", "O", 175, BLUSH)]
    global CLOSE_T
    CLOSE_T = [ws(16, "every") - 0.04, ws(16, "undertone") - 0.06, ws(16, "and") - 0.06, ws(16, "is") - 0.06]
    ov.append(AestheticStack(rows, CLOSE_T, C[17] - 0.15, x=90, y_bottom=1440))
    # STOREFRONT — SB Fade blanco elegante
    global STORE_T
    STORE_T = (c4 + 0.02, c4 + 0.14, ws(19, "we'll") - 0.05)
    ov.append(FadeBlancoElegante("COME SEE US AT", "Slate", "we'll find the perfect tan for you.", *STORE_T, END + 1, y_script=1250))
    # CAPTIONS — Apple Texto Deslizante 2 (+ Dúo script for key words), presenter only
    def ypos(t):
        s = _shot(t)
        return 1300 if s["z0"] < 1.10 else 1515
    ov.append(GlideCaptions(words, ypos, lambda t: _shot(t)["kind"] != "t",
                            emph=["rapid", "exfoliate", "barrier", "book", "custom", "shade", "client", "too.", "relate"]))
    return ov

PRE = [GradientPNG(f"{LIB2}/DEGRADADOS_NEGROS/Degradado a negro subtítulos.png", lambda t: _shot(t)["kind"] in ("b", "img"), 0.62),
       Cutout(C[18], C[19], os.environ.get("U2NET_HOME", os.path.join(os.path.dirname(M.ST), "models", "rembg")))]
POSTS = [SoftZoom(C[0], 0.10, 0.06), FilmBurn(f"{LIB2}/FILM_BURNS/film burns(2).mp4", C[16], 0.5, 0.42), FadeOut(END - 0.70, END)]

build_overlays([])
SFX = [("snap", 0.0, -12.5), ("click", 0.05, -10.5)]
SFX += [("drip", t, -19.5) for t in PROB_T]
for i, (t1, mk, big) in enumerate(SOL_T):
    SFX.append(("swoosh_cut" if i % 2 == 0 else "swoosh_cut2", t1 - 0.10, -11.0))
    if mk: SFX.append(("marker", t1 + 0.30, -7.0))
    if big: SFX.append(("popup", t1, -19.0))
SFX += [("title_whoosh", C[16] - 0.55, -10.0)] + [("swoosh_word", t, -15.0) for t in CLOSE_T]
SFX += [("shutter", C[18], -6.5), ("swoosh_cut2", c4 - 0.10, -11.0)]
SFX += [("key", STORE_T[1] + i * (14 / 30) / 5, -17.0) for i in range(5)]
SFX += [("shimmer", END - 2.5, -23.0)]
MUSIC_LEVEL = -28.5
