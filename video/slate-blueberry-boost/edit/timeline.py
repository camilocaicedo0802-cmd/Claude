"""Edit timeline for 'Radiant Blueberry Boost' (style of the Sinus Facial reference reel)."""
import json, os
from engine import *

D = os.environ["DRIVE"]          # downloaded Drive folder
P = lambda n: f"{D}/proceso/{n}.MP4"
TH = {"IMG_7029": f"{D}/broll/IMG_7029.MOV", "IMG_7032": f"{D}/broll/IMG_7032.MOV"}
DESPUES = f"{D}/despues/IMG_7040_2.mov"
VARIANT = os.environ.get("VARIANT", "cta")     # "cta" (ends with the Tulsa line + end card) or "nocta"
CTA = VARIANT == "cta"
END = 43.40 if CTA else 38.80                  # video length (s)
VOICE_END = None if CTA else 37.80             # no-CTA: voice stops after "...refresh the skin."
MUSIC_FADE = 0.35 if CTA else 1.6              # music fade-out at the end (s)

GRADE_B = "eq=contrast=1.05:saturation=1.04:gamma=0.98"
GRADE_T = "eq=contrast=1.04:saturation=1.02,colorbalance=rm=0.02:bm=-0.02"

# kind 'b' = b-roll (path, src start); kind 't' = talking head synced to the voice map
# z0->z1 = zoom (push-in), cx/cy = focus point (fraction of source frame)
SHOTS = [
 dict(t0=0.00,  t1=2.55,  kind="t", clip="IMG_7029", z0=1.00, z1=1.04, cx=0.45, cy=0.42),
 dict(t0=2.55,  t1=5.38,  kind="t", clip="IMG_7029", z0=1.36, z1=1.38, cx=0.42, cy=0.40),
 dict(t0=5.38,  t1=7.72,  kind="b", path=P("MVI_5226"), src=0.20, z0=1.00, z1=1.09, cx=0.40, cy=0.50),
 dict(t0=7.72,  t1=9.02,  kind="b", path=P("MVI_5222"), src=0.40, z0=1.05, z1=1.12, cx=0.50, cy=0.45),
 dict(t0=9.02,  t1=10.22, kind="b", path=P("MVI_5216"), src=8.40, z0=1.00, z1=1.07, cx=0.45, cy=0.50),
 dict(t0=10.22, t1=12.22, kind="b", path=P("MVI_5220"), src=0.60, z0=1.00, z1=1.06, cx=0.50, cy=0.50),
 dict(t0=12.22, t1=13.28, kind="t", clip="IMG_7029", z0=1.16, z1=1.18, cx=0.43, cy=0.42),
 dict(t0=13.28, t1=14.85, kind="b", path=P("MVI_5226"), src=5.00, z0=1.05, z1=1.12, cx=0.42, cy=0.45),
 dict(t0=14.85, t1=16.68, kind="b", path=P("MVI_5227"), src=8.20, z0=1.00, z1=1.06, cx=0.50, cy=0.50),
 dict(t0=16.68, t1=18.80, kind="b", path=P("MVI_5212"), src=1.60, z0=1.00, z1=1.07, cx=0.50, cy=0.48),
 dict(t0=18.80, t1=20.30, kind="b", path=P("MVI_5211"), src=30.0, z0=1.04, z1=1.10, cx=0.50, cy=0.48),
 dict(t0=20.30, t1=21.26, kind="b", path=P("MVI_5221"), src=5.50, z0=1.10, z1=1.16, cx=0.50, cy=0.50),
 dict(t0=21.26, t1=21.96, kind="b", path=P("MVI_5212"), src=14.6, z0=1.12, z1=1.18, cx=0.50, cy=0.50),
 dict(t0=21.96, t1=22.66, kind="b", path=DESPUES,       src=2.30, z0=1.05, z1=1.11, cx=0.50, cy=0.50),
 dict(t0=22.66, t1=24.20, kind="b", path=P("MVI_5248"), src=0.80, z0=1.00, z1=1.06, cx=0.50, cy=0.50),
 dict(t0=24.20, t1=25.40, kind="b", path=P("MVI_5246"), src=2.80, z0=1.00, z1=1.06, cx=0.50, cy=0.50),
 dict(t0=25.40, t1=26.55, kind="b", path=P("MVI_5249"), src=1.60, z0=1.02, z1=1.08, cx=0.50, cy=0.50),
 dict(t0=26.55, t1=28.72, kind="b", path=P("MVI_5253"), src=0.40, z0=1.00, z1=1.07, cx=0.50, cy=0.50),
 dict(t0=28.72, t1=30.84, kind="t", clip="IMG_7032", z0=1.00, z1=1.04, cx=0.45, cy=0.42),
 dict(t0=30.84, t1=31.95, kind="b", path=P("MVI_5238"), src=5.00, z0=1.00, z1=1.06, cx=0.50, cy=0.55),
 dict(t0=31.95, t1=32.60, kind="b", path=P("MVI_5234"), src=1.80, z0=1.04, z1=1.08, cx=0.50, cy=0.55),
 dict(t0=32.60, t1=33.92, kind="b", path=P("MVI_5255"), src=4.00, z0=1.00, z1=1.06, cx=0.50, cy=0.50),
 dict(t0=33.92, t1=35.90, kind="b", path=P("MVI_5215"), src=3.50, z0=1.04, z1=1.12, cx=0.50, cy=0.50),
 dict(t0=35.90, t1=37.84 if CTA else END, kind="b", path=P("MVI_5256"), src=0.10, z0=1.00, z1=1.06 if CTA else 1.10, cx=0.50, cy=0.50),
]
if CTA:
    SHOTS += [
 dict(t0=37.84, t1=40.13, kind="t", clip="IMG_7032", z0=1.10, z1=1.14, cx=0.45, cy=0.42),
 dict(t0=40.13, t1=END,   kind="white"),
    ]

def load_words(path):
    ws = json.load(open(path))
    out = []
    for w in ws:
        t = w["w"].replace("de -puff", "depuff")
        out.append(dict(w=t, s=w["s"], e=w["e"]))
    # merge whisper's split "de" + "-puff"
    merged = []
    for w in out:
        if merged and w["w"].startswith("-"):
            merged[-1]["w"] += w["w"][1:]; merged[-1]["e"] = w["e"]
        else:
            merged.append(w)
    for i, w in enumerate(merged):
        if w["w"] in ("sleep.", "Sleep."): w["w"] = "Slate."
        if w["w"] == "globe": w["w"] = "globes"
        if w["w"] == "chill": w["w"] = "chilled"
    # "...with a chilled" -> "...with the chilled"
    for i in range(len(merged) - 1):
        if merged[i]["w"] == "a" and merged[i + 1]["w"] == "chilled": merged[i]["w"] = "the"
    # "that you've holding" (whisper dropped 'been'): add it into the same word slot
    for i in range(len(merged) - 1):
        if merged[i]["w"] == "you've" and merged[i + 1]["w"] == "holding": merged[i]["w"] = "you've been"
    return merged

def build_overlays(words):
    sz_cap = 61.0                                   # Poppins Bold, tight tracking: same width as the reference
    sz_cond = fit_size(COND, "DEALING WITH", 472 / 0.94)
    sz_serif = fit_size(SERIF, "sinus pressure?", 690)
    sz_big = fit_size(SERIF, "techniques,", 480)
    ov = []
    # 1) intro title (sparkle reveal + serif typewriter)
    ov.append(SparkleTitle(["A FACIAL MADE OF"], 0.07, 2.55, cy=0.115 * H, size=sz_cond, seed=3))
    ov.append(TypeLine("blueberries?", 0.50, 2.55, cx=W / 2, cy=0.115 * H + sz_cond * 0.98, size=sz_serif))
    # 2) product title over the jar shot
    ov.append(SparkleTitle(["THE RADIANT", "BLUEBERRY BOOST"], 5.45, 7.72, cy=0.135 * H, size=sz_cond * 0.98, seed=7))
    # 3) results: serif words zooming in (one per quick cut)
    ov.append(TrackIn("firmer,", 20.33, 21.26, W / 2, 0.165 * H, sz_big))
    ov.append(TrackIn("plumper,", 21.29, 21.96, W / 2, 0.165 * H, sz_big))
    ov.append(TrackIn("super dewy.", 21.99, 22.66, W / 2, 0.165 * H, sz_big))
    # 4) gua sha: bold word + serif accent (like 'THE hydration'), sparkle-flash on the bold word (no "&")
    ov.append(SparkleTitle(["SCULPT"], 24.26, 25.40, cy=0.115 * H, size=sz_cond * 1.05, dur=0.30, seed=11))
    ov.append(TypeLine("depuff", 24.50, 25.40, cx=W / 2, cy=0.115 * H + sz_cond * 1.12, size=sz_serif * 1.08, instant=True))
    # 5) calm & refreshed (fade-up pair)
    t_calm = 37.84 if CTA else END + 1
    ov.append(FadeUp("calm", 36.40, t_calm, W / 2, 0.145 * H, fit_size(SANSB, "refreshed", 342) * 1.0, SANSB))
    ov.append(FadeUp("and refreshed.", 36.95, t_calm, W / 2, 0.145 * H + 92, sz_serif * 1.02, SERIF))
    # captions
    def ypos(t):
        for lo, hi, y in CAP_Y:
            if lo <= t < hi: return y * H
        return 0.53 * H
    def hide(t):
        return (20.30 <= t < 22.66) or (24.26 <= t < 25.40) or (36.40 <= t < 37.84) or t >= (40.13 if CTA else 36.40)
    ov.append(Captions(words, sz_cap, ypos, hide))
    if CTA:
        ov.append(EndCard(40.13, END + 1, "Book your Radiant Blueberry Boost at Slate", "Tulsa, OK"))
    return ov

# caption vertical position per time range (fraction of height)
CAP_Y = [
 (0.00, 5.38, 0.635),    # talking head: below the shirt logo
 (5.38, 7.72, 0.235),    # under the product title
 (12.22, 13.28, 0.655),
 (28.72, 30.84, 0.635),
 (37.84, 40.13, 0.65),
]

SFX = [  # (file, time, gain_dB)  — sounds extracted from the reference
 ("sparkle", 0.00, -19.7),
 ("ting",    2.05, -31.0),
 ("ding",    2.61, -18.0),
 ("sparkle", 5.38, -19.7),
 ("ding",   24.26, -18.0),
]
