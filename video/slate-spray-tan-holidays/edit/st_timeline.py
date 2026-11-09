"""Timeline: SLATE spray tan holiday reel (4 scenes of the script), SLATE graphic line + reference dynamics.
No emojis on screen (client request)."""
import json, os
from st_engine import *

D = os.environ["STDIR"]                         # scratchpad/st
R = lambda n: f"{D}/raw/{n}.MOV"
B = lambda p: f"{D}/b/{p}"
TH = {k: R(k) for k in ["IMG_7055", "IMG_7058", "IMG_7059", "IMG_7061", "IMG_7062", "IMG_7063"]}
VOICE_LEN = 19.78
END = 22.60
VOICE_MUTE = [(4.62, 5.09)]                    # soft mumbled "and" before "then we're heading" -> clean pause

GRADE_B = "eq=contrast=1.04:saturation=1.05:gamma=0.99"
GRADE_T = "eq=contrast=1.04:saturation=1.03,colorbalance=rm=0.015:bm=-0.015"

def b(t0, t1, path, src, z0=1.0, z1=1.06, cx=0.5, cy=0.5):
    return dict(t0=t0, t1=t1, kind="b", path=B(path), src=src, z0=z0, z1=z1, cx=cx, cy=cy)
def th(t0, t1, clip, z0=1.0, z1=1.04, cx=0.5, cy=0.42):
    return dict(t0=t0, t1=t1, kind="t", clip=clip, z0=z0, z1=z1, cx=cx, cy=cy)

SHOTS = [
 # ESCENA 1 — HOOK: result + application first, then her in front of SLATE
 b(0.00, 0.80, "st1_desp/IMG_4123.mov", 0.35, 1.08, 1.14, 0.5, 0.45),          # tan line reveal
 b(0.80, 1.55, "st3_proc/MVI_4549.mov", 1.40, 1.05, 1.12, 0.5, 0.48),          # spray on abdomen
 th(1.55, 3.20, "IMG_7055", 1.06, 1.12, 0.5, 0.40),                            # storefront
 # ESCENA 2 — HOLIDAYS
 th(3.20, 4.05, "IMG_7058", 1.10, 1.14, 0.5, 0.36),                            # "Thanksgiving's only..."
 b(4.05, 4.68, "st2_proc/IMG_1961.MOV", 0.60, 1.02, 1.08),                     # application (arm)
 th(4.68, 5.52, "IMG_7059", 1.10, 1.14, 0.5, 0.36),                            # "and then we're heading"
 b(5.52, 6.52, "st3_proc/MVI_4548.MP4", 2.00, 1.04, 1.10, 0.5, 0.42),          # arms-up application
 b(6.52, 7.50, "st3_desp/IMG_2211.MOV", 3.60, 1.02, 1.08, 0.5, 0.40),          # CHRISTMAS: glowing result
 b(7.50, 8.05, "st1_desp/IMG_4149.MOV", 1.20, 1.04, 1.10, 0.5, 0.42),          # NEW YEAR'S: posing result
 # ESCENA 3 — SPRAY TAN TIP
 th(8.05, 9.48, "IMG_7061", 1.04, 1.08, 0.5, 0.40),                            # "And remember to make sure"
 b(9.48, 10.22, "st1_proc/IMG_4100.MOV", 0.80, 1.02, 1.08),                    # "book your spray tan"
 th(10.22, 12.30, "IMG_7061", 1.00, 1.03, 0.5, 0.42),                          # "two days in advance..." + calendar
 b(12.30, 13.30, "st4_vid/IMG_3833.MOV", 1.60, 1.04, 1.10, 0.5, 0.48),         # result develops
 b(13.30, 14.55, "st3_desp/Video_despues.MOV", 0.40, 1.00, 1.05, 0.5, 0.45),   # result
 # ESCENA 4 — BOOKINGS / CLOSE
 th(14.55, 16.45, "IMG_7063", 1.06, 1.10, 0.5, 0.38),                          # "Holiday appointments are booking up fast"
 b(16.45, 17.35, "st2_trans/IMG_1987.MOV", 4.60, 1.00, 1.06, 0.5, 0.36),       # best result, glam
 b(17.35, 18.30, "st3_desp/IMG_2210.MOV", 3.70, 1.02, 1.08, 0.5, 0.45),        # tan line / glow
 th(18.30, 19.88, "IMG_7063", 1.12, 1.16, 0.5, 0.36),                          # "to get your holiday glow"
 dict(t0=19.88, t1=END, kind="white"),
]

def load_words(path):
    ws = json.load(open(path)); out = []
    for w in ws:
        if w["w"] == "so" and 12.0 < w["s"] < 12.5:   # whisper filled in a "so" that is not in the cut
            continue
        if any(a <= w["s"] < b for a, b in VOICE_MUTE):   # muted words do not get a caption
            continue
        out.append(dict(w=w["w"], s=w["s"], e=w["e"]))
    return out

def build_overlays(words):
    sz_cond = fit_size(COND, "DEALING WITH", 472 / 0.94)
    sz_serif = fit_size(SERIF, "sinus pressure?", 690)
    ov = []
    # ESCENA 1
    ov.append(GlassPill("TULSA, OK", 0.05, 3.20, W / 2, 0.075 * H, size=44, tracking=0.22))
    ov.append(SparkleTitle(["SPRAY TAN LOVERS,"], 1.55, 3.20, cy=0.150 * H, size=sz_cond * 0.98, seed=5))
    ov.append(TypeLine("this is for you!", 2.18, 3.20, cx=W / 2, cy=0.150 * H + sz_cond * 1.08, size=sz_serif * 0.98))
    # ESCENA 2 (one holiday at a time, synced to the word)
    ov.append(Particles("leaves", 3.24, 5.52, n=16, seed=4, opacity=0.9))
    ov.append(SparkleTitle(["THANKSGIVING"], 3.26, 5.52, cy=0.115 * H, size=sz_cond * 1.12, seed=8))
    ov.append(Particles("snow", 6.52, 7.50, n=46, seed=6, opacity=0.9))
    ov.append(SparkleTitle(["CHRISTMAS"], 6.55, 7.50, cy=0.105 * H, size=sz_cond * 1.12, dur=0.34, seed=9))
    ov.append(TypeLine("parties", 6.80, 7.50, cx=W / 2, cy=0.105 * H + sz_cond * 1.22, size=sz_serif * 1.05, instant=True))
    ov.append(Particles("confetti", 7.50, 8.05, n=60, seed=2, opacity=0.95))
    ov.append(SparkleTitle(["NEW YEAR'S"], 7.52, 8.05, cy=0.115 * H, size=sz_cond * 1.18, dur=0.28, seed=12))
    # ESCENA 3
    ov.append(GlassPill("SPRAY TAN TIP", 8.10, 12.30, W / 2, 0.075 * H, size=40, tracking=0.20))
    ov.append(FadeUp("BOOK", 9.50, 12.30, W / 2, 0.124 * H, 50, COND, dy=14))
    ov.append(SparkleTitle(["2 DAYS BEFORE"], 10.26, 12.30, cy=0.180 * H, size=sz_cond * 1.30, dur=0.40, seed=14))
    ov.append(TypeLine("your event", 11.80, 12.30, cx=W / 2, cy=0.180 * H + sz_cond * 1.52, size=sz_serif * 0.95, instant=True))
    ov.append(CalendarCard(10.55, 12.30, W / 2, 0.555 * H, w=820, h=470, month="DECEMBER", start_day=15, event_idx=5, book_idx=3))
    ov.append(FadeUp("fully", 13.30, 14.55, W / 2, 0.135 * H, fit_size(SANSB, "refreshed", 342), SANSB))
    ov.append(FadeUp("developed.", 13.62, 14.55, W / 2, 0.135 * H + 108, sz_serif * 1.02, SERIF))
    # ESCENA 4
    ov.append(Particles("snow", 14.55, 16.45, n=30, seed=11, opacity=0.6))
    ov.append(SparkleTitle(["HOLIDAY SPOTS"], 14.78, 16.45, cy=0.110 * H, size=sz_cond * 1.12, seed=15))
    ov.append(TypeLine("are filling up!", 15.50, 16.45, cx=W / 2, cy=0.110 * H + sz_cond * 1.22, size=sz_serif * 1.0))
    ov.append(SparkleTitle(["BOOK YOUR"], 17.74, 19.88, cy=0.110 * H, size=sz_cond * 1.12, dur=0.32, seed=17))
    ov.append(TypeLine("holiday glow", 18.92, 19.88, cx=W / 2, cy=0.110 * H + sz_cond * 1.22, size=sz_serif * 1.05))
    # captions (Poppins Bold + glow), hidden where a big graphic takes the centre
    def ypos(t):
        for lo, hi, y in CAP_Y:
            if lo <= t < hi: return y * H
        return 0.60 * H
    def hide(t):
        return (10.22 <= t < 12.30) or (13.30 <= t < 14.55) or t >= 19.88
    ov.append(Captions(words, 61.0, ypos, hide))
    ov.append(EndCard(19.88, END + 1, "Book your holiday glow", "SLATE TULSA"))
    return ov

CAP_Y = [
 (1.55, 3.20, 0.66),
 (3.20, 4.05, 0.64), (4.68, 5.52, 0.64),
 (8.05, 9.48, 0.66),
 (14.55, 16.45, 0.66), (18.30, 19.88, 0.66),
]

POSTS = [ZoomTransition(0.80, 0.12, 0.16), ZoomTransition(3.20, 0.16, 0.22), ZoomTransition(8.05, 0.16, 0.22),
         ZoomTransition(14.55, 0.16, 0.22), Flash(19.88, 0.12, 0.6)]

SFX = [  # (file, time, gain_dB) — sparkle/ding/ting extracted from the first reference; whoosh/riser/pop synthesized
 ("pop",     0.08, -24.0),
 ("whoosh",  0.62, -27.0),
 ("sparkle", 1.55, -21.0),
 ("whoosh",  2.98, -24.0),
 ("sparkle", 3.26, -21.0),
 ("sparkle", 6.55, -22.0),
 ("ting",    7.50, -28.0),
 ("sparkle", 7.52, -23.0),
 ("whoosh",  7.83, -24.0),
 ("pop",     8.12, -24.0),
 ("ding",   10.26, -19.0),
 ("pop",    11.10, -27.0),
 ("pop",    11.50, -26.0),
 ("whoosh", 14.33, -24.0),
 ("sparkle",14.78, -21.0),
 ("sparkle",17.74, -21.5),
 ("whoosh", 19.64, -27.0),
 ("ding",   19.88, -20.0),
]
