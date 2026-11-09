"""Timeline: SLATE 'Spray tan problems? We've got solutions!' (Problem vs Solution). No emojis on screen.
Voice: off-camera colleague reads each PROBLEM, the presenter answers with the SOLUTION (both kept).
Every cut and text time is derived from the assembled voice (voice_raw_map.json + words.json), so re-cutting
the voice keeps everything in sync."""
import json, os, re
from ps_engine import *
from voice_edl import EDL, ROLE

HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.environ["STDIR"]; PS = os.environ["PSDIR"]
B = lambda p: f"{ST}/b/{p}"
SAL = lambda n: f"{ST}/broll2/{n}.MOV"
TH = {k: f"{PS}/raw/{k}.MOV" for k in ["IMG_7103", "IMG_7106", "IMG_7108", "IMG_7110"]}
OFF = 1.40                      # hook plays alone, voice starts here

GRADE_T = "eq=contrast=1.05:saturation=1.04:gamma=1.03,colorbalance=rm=0.01:bm=-0.01"          # presenter: lift shadows a touch
GRADE_B = "eq=contrast=1.05:brightness=0.005:saturation=1.07:gamma=1.02,colorbalance=rm=0.015:bm=-0.015"
GRADE_A = GRADE_B                                                                              # solutions: warm, glowy
GRADE_Q = "eq=contrast=1.03:saturation=0.88:gamma=1.02,colorbalance=rs=-0.01:bs=0.015:bm=0.01"  # problems: slightly cooler / flatter

# ---------------------------------------------------------------- derive times from the voice
_VMAP = json.load(open(os.path.join(HERE, "voice_raw_map.json")))
SEG = {}
for p in _VMAP:
    a, e = SEG.get(p["seg"], (p["t0"] + OFF, p["t1"] + OFF))
    SEG[p["seg"]] = (min(a, p["t0"] + OFF), max(e, p["t1"] + OFF))
NSEG = len(SEG)
def cut(k):       # cut before segment k (middle of the gap)
    return OFF if k == 0 else round((SEG[k - 1][1] + SEG[k][0]) / 2, 3)
VOICE_END = SEG[NSEG - 1][1]
CARD = round(VOICE_END + 0.06, 3)
END = round(CARD + 2.65, 3)

def _norm(s): return re.sub(r"[^a-z0-9']", "", s.lower())

def _align():
    """Align script tokens (EDL text) to whisper words segment by segment; unmatched tokens are interpolated."""
    ws = [dict(w=x["w"], s=x["s"] + OFF, e=x["e"] + OFF) for x in json.load(open(os.path.join(HERE, "words.json")))]
    out = {}
    for k in range(NSEG):
        a, e = SEG[k]
        toks = EDL[k][3].replace(" one to two ", " 1-2 ").split()
        mine = [w for w in ws if a - 0.08 <= w["s"] < e - 0.02]
        res = [None] * len(toks); j = 0
        for i, tk in enumerate(toks):
            n = _norm(tk)
            for jj in range(j, min(j + 4, len(mine))):
                if _norm(mine[jj]["w"]) == n or (n == "12" and _norm(mine[jj]["w"]) in ("one", "1")):
                    res[i] = (mine[jj]["s"], mine[jj]["e"]); j = jj + 1; break
        # interpolate gaps
        known = [(i, r) for i, r in enumerate(res) if r]
        for i in range(len(toks)):
            if res[i]: continue
            prv = max([kk for kk, _ in known if kk < i], default=None); nxt = min([kk for kk, _ in known if kk > i], default=None)
            t0 = res[prv][1] if prv is not None else a; t1 = res[nxt][0] if nxt is not None else e
            span = [kk for kk in range((prv if prv is not None else -1) + 1, nxt if nxt is not None else len(toks))]
            q = span.index(i); d = (t1 - t0) / max(1, len(span))
            res[i] = (t0 + q * d, t0 + (q + 1) * d)
        out[k] = [dict(w=tk, s=r[0], e=r[1]) for tk, r in zip(toks, res)]
    return out
WORDS_BY_SEG = _align()

def word(k, tok, after=0.0):
    """Start time of the first word in segment k matching tok (script spelling); ~0.12 s earlier than whisper."""
    for w in WORDS_BY_SEG[k]:
        if _norm(w["w"]) == _norm(tok) and w["s"] >= after: return round(w["s"] - 0.12, 3)
    raise KeyError((k, tok))

def b(t0, t1, path, src, z0=1.0, z1=1.06, cx=0.5, cy=0.5, grade=GRADE_A):
    return dict(t0=t0, t1=t1, kind="b", path=path, src=src, z0=z0, z1=z1, cx=cx, cy=cy, grade=grade)
def th(t0, t1, clip, z0=1.0, z1=1.04, cx=0.5, cy=0.40, grade=GRADE_T):
    return dict(t0=t0, t1=t1, kind="t", clip=clip, z0=z0, z1=z1, cx=cx, cy=cy, grade=grade)

C = [cut(k) for k in range(NSEG)] + [CARD]
mid = lambda k: round((C[k] + C[k + 1]) / 2, 3)
s5 = word(5, "before"); s9 = word(9, "room"); s13a = word(13, "1-2"); s13b = word(13, "follow") - 0.10
s13c = word(13, "send"); s13d = word(13, "custom") - 0.15; s15 = word(15, "spray"); s19 = word(19, "and")
c1 = [C[16] + (C[17] - C[16]) * i / 4 for i in range(5)]
cal0 = word(11, "tan")

SHOTS = [
 b(0.000, C[0], B("st1_proc/IMG_4096.mov"), 0.30, 1.05, 1.12, 0.5, 0.45),                 # HOOK: golden spray mist
 b(C[0], C[1], B("st1_antes/IMG_4082.MOV"), 1.50, 1.04, 1.10, 0.5, 0.42, GRADE_Q),        # Q1 pale or dull skin (before)
 b(C[1], C[2], B("st3_proc/MVI_4552.MP4"), 1.00, 1.00, 1.06, 0.5, 0.45),                  # A1 custom spray tan
 b(C[2], C[3], B("st2_trans/IMG_1937.MOV"), 0.20, 1.02, 1.08, 0.5, 0.42, GRADE_Q),        # Q2 need color ASAP (before)
 th(C[3], C[3] + 1.37, "IMG_7103", 1.10, 1.14, 0.5, 0.36),                                 # A2 "we have a rapid formula"
 b(C[3] + 1.37, C[4], B("st2_proc/IMG_1965.MOV"), 0.80, 1.00, 1.06),                      #    fast application
 b(C[4], C[5], B("st1_trans/r2_antes.mov"), 0.20, 1.04, 1.10, 0.5, 0.42, GRADE_Q),        # Q3 dry or patchy skin (before)
 th(C[5], s5, "IMG_7103", 1.10, 1.14, 0.5, 0.36),                                          # A3 "exfoliate 24 hours"
 b(s5, C[6], B("st2_lleg/IMG_1941.MOV"), 1.50, 1.00, 1.06),                               #    "...before your appointment" (arriving)
 th(C[6], C[7], "IMG_7103", 1.00, 1.03, 0.5, 0.40, GRADE_Q),                               # Q4 tan fading unevenly (she listens)
 b(C[7], C[8], SAL("IMG_0801"), 0.10, 1.00, 1.06),                                         # A4 moisturize daily (lotions)
 b(C[8], mid(8), B("st3_proc/MVI_4541.MP4"), 20.50, 1.04, 1.10, 0.5, 0.45, GRADE_Q),      # Q5 hands being sprayed
 b(mid(8), C[9], B("st2_proc/IMG_1959.MOV"), 2.60, 1.00, 1.06, 0.5, 0.5, GRADE_Q),        #    arm / hand
 th(C[9], s9, "IMG_7103", 1.10, 1.14, 0.5, 0.36),                                          # A5 "we have barrier cream in the"
 b(s9, C[10], B("st2_proc/IMG_1955.MOV"), 1.50, 1.00, 1.06),                              #    "room ... before your appointment"
 b(C[10], C[11], B("st3_desp/IMG_2209.MOV"), 2.40, 1.00, 1.06, 0.5, 0.40),                # Q6 going on vacation (bikini glow)
 th(C[11], C[12], "IMG_7106", 1.04, 1.08, 0.5, 0.38),                                      # A6 book 1-2 days before your trip + calendar
 b(C[12], C[13], B("st2_trans/IMG_1987.MOV"), 4.20, 1.00, 1.06, 0.5, 0.38),               # Q7 wedding or special event (glam)
 th(C[13], s13a, "IMG_7106", 1.10, 1.14, 0.5, 0.36),                                       # A7 "make sure you book your appointment"
 b(s13a, s13b, B("st2_lleg/IMG_1944.MOV"), 1.00, 1.00, 1.06),                             #    "1-2 days before your wedding"
 b(s13b, s13c, B("st2_cons/IMG_1948.MOV"), 12.50, 1.10, 1.16, 0.5, 0.40),                 #    "follow the prep instructions"
 b(s13c, s13d, B("st3_proc/MVI_4545.MP4"), 3.50, 1.00, 1.06),                             #    application
 th(s13d, C[14], "IMG_7106", 1.12, 1.16, 0.5, 0.36),                                       #    "...a custom shade for you"
 b(C[14], mid(14), B("st2_cons/IMG_1949.MOV"), 9.00, 1.12, 1.18, 0.40, 0.42),             # Q8 which shade or solution (bottle + brush)
 b(mid(14), C[15], B("st2_cons/IMG_1949.MOV"), 20.50, 1.06, 1.12, 0.40, 0.42),            #    tech explaining
 b(C[15], s15, B("st2_cons/IMG_1948.MOV"), 31.00, 1.06, 1.12, 0.5, 0.40),                 # A8 personalized consultation
 th(s15, C[16], "IMG_7108", 1.08, 1.12, 0.5, 0.36),                                        #    presenter
 b(c1[0], c1[1], B("st1_desp/IMG_4122.mov"), 5.20, 1.00, 1.06, 0.5, 0.42),                # C1 every skin tone: different clients
 b(c1[1], c1[2], B("st2_trans/IMG_1988.MOV"), 4.60, 1.00, 1.06, 0.5, 0.40),
 b(c1[2], c1[3], B("st3_desp/IMG_2210.MOV"), 6.40, 1.00, 1.06, 0.5, 0.40),
 b(c1[3], c1[4], B("st4_vid/IMG_3826.MOV"), 1.20, 1.00, 1.06, 0.5, 0.45),
 th(C[17], C[18], "IMG_7110", 1.06, 1.10, 0.5, 0.38),                                      # C2 your spray tan should be too
 th(C[18], C[19], "IMG_7110", 1.12, 1.16, 0.5, 0.36),                                      # C3 if you relate to any of this
 b(C[19], s19, SAL("IMG_0822"), 0.30, 1.00, 1.06, 0.5, 0.40),                             # C4 come see us at Slate (storefront)
 th(s19, CARD, "IMG_7110", 1.06, 1.10, 0.5, 0.38),                                         #    perfect tan for you
 dict(t0=CARD, t1=END, kind="white"),
]

def load_words(path=None, vmap=None):
    """Caption words: solutions and closing only (problem lines are on the problem card)."""
    out = []
    for k in range(NSEG):
        if ROLE[k] != "Q": out += WORDS_BY_SEG[k]
    return out

def build_overlays(words):
    sz_cond = fit_size(COND, "DEALING WITH", 472 / 0.94)
    sz_serif = fit_size(SERIF, "sinus pressure?", 690)
    T1 = sz_cond * 1.12
    sub_y = lambda cy: cy + T1 * 1.25
    ov = []
    # HOOK
    ov.append(SparkleTitle(["SPRAY TAN", "PROBLEMS?"], 0.03, C[0], cy=0.215 * H, size=sz_cond * 1.55, dur=0.38, seed=21))
    ov.append(TypeLine("we've got solutions!", 0.48, C[0], cx=W / 2, cy=0.215 * H + sz_cond * 1.55 * 1.80, size=sz_serif * 1.12, cps=40))
    ov.append(Twinkles(0.30, C[0], W / 2, 0.215 * H + 110, 780, 480, n=7, seed=3, maxsize=40))
    # PROBLEMS (glass card, serif italic typed)
    P = lambda lines, k, size=74: ov.append(ProblemCard(lines, C[k], C[k + 1], cy=0.140 * H, size=size))
    P(["Pale or dull skin"], 0)
    P(["Need color ASAP"], 2)
    P(["Dry or patchy skin"], 4)
    P(["Tan fading unevenly"], 6)
    P(["Tan sticking to", "hands and feet"], 8)
    P(["Going on vacation"], 10)
    P(["Wedding or", "special event"], 12)
    P(["Not sure which shade", "or solution is right for you?"], 14, size=62)
    # SOLUTIONS (pill with star, warm sparkle title, twinkles)
    S_ = lambda lines, t0, t1, seed, **k: ov.append(SolutionTitle(lines, t0, t1, cy=0.150 * H, size=T1, sub_size=sz_serif * 0.92, seed=seed, **k))
    S_(["CUSTOM SPRAY TAN"], C[1], C[2], 1)
    S_(["RAPID TAN"], C[3], C[4], 2)
    S_(["EXFOLIATE"], C[5], C[6], 3, sub="24 hours before", sub_t=word(5, "24"))
    S_(["MOISTURIZE DAILY"], C[7], C[8], 4)
    S_(["BARRIER CREAM"], C[9], C[10], 5, sub="before your appointment", sub_t=word(9, "before"))
    S_(["BOOK 1-2 DAYS"], C[11], C[12], 6, sub="before your trip", sub_t=word(11, "before"))
    ov.append(LabeledCalendar(cal0, C[12], W / 2, 0.575 * H, w=820, h=470, month="DECEMBER", start_day=15, event_idx=5, book_idx=3,
                              ev_label="TRIP", bk_label="BOOK", arrow_label="1-2 DAYS"))
    S_(["PROPER PREP"], C[13], s13d, 7, sub="follow the prep instructions", sub_t=word(13, "follow"))
    S_(["CUSTOM SHADE"], s13d, C[14], 8, sub="made for you", sub_t=word(13, "shade") + 0.25)
    S_(["PERSONALIZED", "CONSULTATION"], C[15], C[16], 9)
    # CLOSING
    ov.append(SparkleTitle(["EVERY SKIN TONE,"], C[16] + 0.03, C[17], cy=0.110 * H, size=T1, seed=31))
    ov.append(TypeLine("undertone and glow goal", word(16, "undertone"), C[17], cx=W / 2, cy=sub_y(0.110 * H), size=sz_serif * 0.86))
    ov.append(FadeUp("is different.", word(16, "is"), C[17], W / 2, sub_y(0.110 * H) + sz_serif * 0.86 * 1.18, sz_serif * 0.86, SERIF))
    ov.append(SparkleTitle(["YOUR SPRAY TAN"], C[17] + 0.03, C[18], cy=0.110 * H, size=T1, seed=33))
    ov.append(TypeLine("should be too.", word(17, "should"), C[18], cx=W / 2, cy=sub_y(0.110 * H), size=sz_serif * 1.02))
    ov.append(SparkleTitle(["COME SEE US"], word(19, "come"), CARD, cy=0.110 * H, size=T1, seed=35))
    ov.append(TypeLine("at Slate", word(19, "Slate"), CARD, cx=W / 2, cy=sub_y(0.110 * H), size=sz_serif * 1.05))
    ov.append(Twinkles(word(19, "come") + 0.2, CARD, W / 2, 0.110 * H + 50, 640, 250, n=6, seed=9))
    # captions: solutions + closing only; below the shirt logo on presenter punch-ins
    def ypos(t):
        for s in SHOTS:
            if s["t0"] <= t < s["t1"]:
                if s["kind"] == "t": return (0.725 if s["z0"] >= 1.08 else 0.66) * H
                return 0.62 * H
        return 0.62 * H
    def hide(t):
        return t < C[0] or (cal0 <= t < C[12]) or (C[16] <= t < C[18]) or t >= CARD
    ov.append(Captions(words, 61.0, ypos, hide))
    ov.append(EndCard(CARD, END + 1, "Let's find your perfect tan", "SLATE TULSA"))
    return ov

QA = [C[k] for k in (1, 3, 5, 7, 9, 11, 13, 15)]                     # problem -> solution cuts
AQ = [C[k] for k in (0, 2, 4, 6, 8, 10, 12, 14, 16)]                  # hook -> problem, solution -> next problem, -> closing
POSTS = [WhipTransition(t, 0.12, 0.45) for t in QA] + [ZoomTransition(t, 0.14, 0.20) for t in AQ] + [Flash(CARD, 0.12, 0.6)]

SFX = [("sparkle", 0.03, -21.0)]
for t in AQ[:-1]:
    SFX += [("whoosh", t - 0.22, -27.0), ("pop", t + 0.02, -26.0)]
for t in QA:   # short chime, so it never masks the first word of the answer
    SFX += [("whoosh", t - 0.22, -26.0), ("ting", t - 0.06, -29.0)]
SFX += [("pop", cal0 + 0.95, -27.0), ("pop", cal0 + 1.20, -28.0),
        ("whoosh", C[16] - 0.22, -27.0), ("sparkle", C[16] + 0.03, -24.0), ("ting", C[17] + 0.03, -28.0),
        ("sparkle", word(19, "come"), -24.0), ("whoosh", CARD - 0.23, -27.0), ("ding", CARD, -20.0)]
