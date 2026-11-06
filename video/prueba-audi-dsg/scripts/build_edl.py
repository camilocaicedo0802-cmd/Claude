"""Edit decision list for the Audi DSG test video.

All times tied to the speech are written in SOURCE seconds of the Lienzo and
mapped to the output timeline with o(). Output: rm/src/edl.json
"""
import json, re, sys, os

S = os.path.dirname(os.path.abspath(__file__))
FPS = 30

# Voice segments kept from the Lienzo (snapped to silences).
SEGS = [(0.000, 3.165), (4.905, 14.585), (17.380, 23.860), (24.045, 35.095),
        (37.035, 45.660), (47.000, 55.415), (72.690, 76.250)]
OUT_STARTS = []
acc = 0.0
for a, b in SEGS:
    OUT_STARTS.append(acc)
    acc += b - a
VOICE_END = acc
END_CARD = 2.65
TOTAL = VOICE_END + END_CARD


def o(src):
    for (a, b), st in zip(SEGS, OUT_STARTS):
        if a - 1e-6 <= src <= b + 1e-6:
            return round(st + (src - a), 4)
    raise ValueError(f"src {src} not in a kept segment")


def oe(src):  # end of a span: allow segment end
    return o(src)


# ---------------------------------------------------------------- words
words_raw = json.load(open(os.path.join(S, "lienzo_words.json")))
FIX = {"todo": "tu", "audio": "Audi"}
RED = {"FALLANDO?", "AUDI", "PROBLEMAS", "DSG,", "DIAGNÓSTICO,", "FALLA,", "SENSOR", "DAÑO",
       "ACEITE.", "ACEITE,", "DESMONTAR", "CLONAR", "PROGRAMADA", "ACOMPÁÑAME.", "MENSAJE.",
       "HIDRÁULICA", "ELECTRÓNICA,", "TRANSMISIÓN,", "MECATRÓNICA,", "MECATRÓNICA."}
words = []
for seg in words_raw:
    for w in seg["words"]:
        t = w["w"].strip()
        t = FIX.get(t, t)
        try:
            s, e = o(w["s"]), o(min(w["e"], w["s"] + 1.2))
        except ValueError:
            continue
        words.append({"t": t.upper(), "src": w["s"], "s": s, "e": e})

# Spans (src) where a title replaces the subtitles.
NO_SUBS = [(0.0, 1.80), (5.0, 5.66), (10.80, 14.60), (20.25, 23.90), (25.85, 27.43),
           (30.15, 32.0), (40.95, 45.70), (50.20, 55.45), (75.25, 76.30)]


def hidden(src):
    return any(a <= src < b for a, b in NO_SUBS)


# Hard breaks (src) where a subtitle group must end: visual cuts.
BREAKS = [1.95, 7.0, 8.95, 17.38, 24.045, 27.44, 31.95, 33.46, 37.035, 39.93, 47.0, 50.27, 72.69]


def groups_from(ws):
    gs, cur = [], []
    def flush():
        if cur:
            gs.append(list(cur)); cur.clear()
    for i, w in enumerate(ws):
        if cur:
            prev = cur[-1]
            txt = " ".join(x["t"] for x in cur + [w])
            brk = any(prev["src"] < b <= w["src"] for b in BREAKS)
            if len(txt) > 24 or len(cur) >= 4 or w["s"] - prev["e"] > 0.45 or brk or prev["t"][-1] in ",.?":
                flush()
        cur.append(w)
    flush()
    return gs


vis = [w for w in words if not hidden(w["src"])]
subs = []
for g in groups_from(vis):
    txt = [w["t"] for w in g]
    # split into two lines when long
    lines = [txt]
    if (len(" ".join(txt)) > 16 and len(txt) >= 3) or (len(" ".join(txt)) > 19 and len(txt) == 2):
        best, bi = 1e9, 1
        for k in range(1, len(txt)):
            d = abs(len(" ".join(txt[:k])) - len(" ".join(txt[k:])))
            if d < best:
                best, bi = d, k
        lines = [txt[:bi], txt[bi:]]
    start = g[0]["s"]
    end = g[-1]["e"] + 0.12
    subs.append({"from": start, "to": end,
                 "lines": [[{"t": w, "red": w in RED} for w in ln] for ln in lines],
                 "at": [w["s"] for w in g]})
# avoid overlaps / tiny gaps between consecutive groups
for a, b in zip(subs, subs[1:]):
    if b["from"] - a["to"] < 0.25:
        a["to"] = b["from"]

# ---------------------------------------------------------------- visuals
V = []  # each: dict(kind, from, to, ...)


def vis_(kind, f, t, **kw):
    V.append(dict(kind=kind, **{"from": round(f, 4), "to": round(t, 4)}, **kw))


L = "LienzoAudi.mp4"
FACE = [50, 30]
# 1 HOOK
vis_("speaker", o(0.0), o(1.96), src=L, srcStart=0.0, zoom=[1.16, 1.24], origin=FACE, enter="zoomblur")
vis_("speaker", o(1.96), o(3.165), src=L, srcStart=1.96, zoom=[1.42, 1.48], origin=FACE, enter="zoomblur")
# 2
vis_("speaker", o(4.905), o(7.0), src=L, srcStart=4.905, zoom=[1.04, 1.10], origin=FACE, enter="zoomblur")
vis_("broll", o(7.0), o(8.95), src=L, srcStart=70.45, rate=0.7, zoom=[1.18, 1.05], origin=[50, 55], enter="zoomblur")
vis_("speaker", o(8.95), o(10.84), src=L, srcStart=8.95, zoom=[1.26, 1.30], origin=FACE, enter="cut")
vis_("darkcards", o(10.84), o(14.585), cards=[
    {"src": "IMG_6311.mp4", "srcStart": 0.4, "at": 0.0, "x": 300, "y": 640, "w": 470, "h": 700, "from": "zoom"},
    {"src": "IMG_6302.mp4", "srcStart": 1.2, "at": round(o(12.10) - o(10.84), 3), "x": 780, "y": 700, "w": 470, "h": 700, "from": "right"},
], enter="zoomblur")
# 3
vis_("speaker", o(17.38), o(20.30), src=L, srcStart=17.38, zoom=[1.02, 1.08], origin=[50, 25], enter="zoomblur")
vis_("collage", o(20.30), o(23.86), tiles=[
    ["IMG_6302.mp4", 0.5], ["IMG_6311.mp4", 1.5], ["IMG_6306.mp4", 1.0], ["IMG_6313.mp4", 2.0],
    ["IMG_6304.mp4", 0.2], ["IMG_6307.mp4", 0.5], ["IMG_6310.mp4", 0.0], ["IMG_6305.mp4", 0.5],
    ["IMG_6315.mp4", 1.0], ["IMG_6318.mp4", 0.2]], enter="zoomblur")
# 4
vis_("speaker", o(24.045), o(25.90), src=L, srcStart=24.045, zoom=[1.22, 1.26], origin=[50, 25], enter="zoomblur")
vis_("broll", o(25.90), o(27.44), src="IMG_6318.mp4", srcStart=0.2, zoom=[1.35, 1.15], origin=[50, 55], enter="zoomblur", grade="dark")
vis_("speaker", o(27.44), o(30.22), src=L, srcStart=27.44, zoom=[1.02, 1.07], origin=[50, 25], enter="zoomblur")
vis_("float3d", o(30.22), o(31.95), cards=[
    {"src": "IMG_6311.mp4", "srcStart": 2.0, "at": 0.0, "label": "HIDRÁULICA"},
    {"src": "IMG_6307.mp4", "srcStart": 1.0, "at": round(o(31.08) - o(30.22), 3), "label": "TARJETA ELECTRÓNICA"},
], enter="zoomblur")
vis_("speaker", o(31.95), o(33.46), src=L, srcStart=31.95, zoom=[1.12, 1.16], origin=[50, 25], enter="zoomblur")
vis_("speaker", o(33.46), o(35.095), src=L, srcStart=33.46, zoom=[1.38, 1.42], origin=[50, 22], enter="cut", shake=0.35)
# 5
vis_("lightcard", o(37.035), o(39.93), src="IMG_6309.mp4", srcStart=7.2, step="PASO 01", title="DESMONTAJE", enter="zoomblur")
vis_("speaker", o(39.93), o(40.99), src=L, srcStart=39.93, zoom=[1.18, 1.22], origin=[50, 25], enter="zoomblur")
vis_("clone", o(40.99), o(45.66), left={"src": "IMG_6311.mp4", "srcStart": 3.0}, right={"src": "IMG_6302.mp4", "srcStart": 3.0},
     tVieja=round(o(42.61) - o(40.99), 3), tNueva=round(o(43.63) - o(40.99), 3), tValores=round(o(44.97) - o(40.99), 3), enter="zoomblur")
# 6
vis_("speaker", o(47.0), o(50.27), src=L, srcStart=47.0, zoom=[1.04, 1.12], origin=[50, 30], enter="zoomblur")
vis_("broll", o(50.27), o(51.81), src="IMG_6303.mp4", srcStart=12.0, zoom=[1.25, 1.12], origin=[50, 50], enter="zoomblur")
vis_("darkwide", o(51.81), o(54.11), src="IMG_6312.mp4", srcStart=44.6, enter="zoomblur")
vis_("broll", o(54.11), o(55.415), src="IMG_6316.mp4", srcStart=6.3, zoom=[1.15, 1.28], origin=[50, 50], enter="zoomblur")
# 7 CTA
vis_("speaker", o(72.69), o(75.31), src=L, srcStart=72.69, zoom=[1.06, 1.12], origin=[50, 25], enter="zoomblur")
vis_("speaker", o(75.31), o(76.25), src=L, srcStart=75.31, zoom=[1.32, 1.36], origin=[50, 25], enter="cut")
# END CARD
vis_("endcard", VOICE_END, TOTAL, src=L, srcStart=70.45, rate=0.5, enter="zoomblur")

# ---------------------------------------------------------------- overlays
OV = []


def ov(kind, f, t, **kw):
    OV.append(dict(kind=kind, **{"from": round(f, 4), "to": round(t, 4)}, **kw))


ov("hook", o(0.0), o(1.92), line1="¿LA TRANSMISIÓN DE TU AUDI", line2="ESTÁ FALLANDO?", tLine2=round(o(0.98), 3))
ov("bigword", o(5.08), o(6.95), small="ESTE", big="AUDI A3", pill="DSG", y=1180)
ov("location", o(7.08), o(8.95), a="HIDALGO", b="TIZAYUCA", tB=round(o(8.28) - o(7.08), 3))
ov("label", o(10.84) + 0.08, o(14.585), line1="TRANSMISIÓN DSG", line2="MECATRÓNICA", tLine2=round(o(13.74) - o(10.84) - 0.08, 3), y=1420)
ov("codes", o(20.30), o(23.86), title="CÓDIGOS DE FALLA", codes=[["P17BF", round(o(21.40) - o(20.30), 3)], ["P189C", round(o(22.58) - o(20.30), 3)]])
ov("impact", o(25.90), o(27.44), small="BAJA", big="PRESIÓN", under="DE ACEITE", y=960)
ov("stepchip", o(37.035), o(39.93), text="PASO 01", sub="DESMONTAJE")
ov("stepchip", o(40.99), o(45.66), text="PASO 02", sub="CLONACIÓN")
ov("stepword", o(50.27), o(51.81), step="PASO 03", small="LLENADO DE", big="ACEITE")
ov("stepword", o(51.81), o(54.11), step="PASO 04", small="", big="INSTALACIÓN", y=1430)
ov("stepword", o(54.11), o(55.415), step="PASO 05", small="Y LOS", big="AJUSTES")
ov("cta", o(75.31), TOTAL, small="MÁNDANOS", big="UN MENSAJE", endAt=round(VOICE_END, 4))

# ---------------------------------------------------------------- sfx (output seconds)
SFX = []


def sfx(kind, t, gain=1.0):
    SFX.append({"kind": kind, "t": round(t, 3), "gain": gain})


sfx("boom", 0.0, 0.9)
# typing ticks for hook line 1 (letter reveal over first 0.9s)
for i in range(22):
    sfx("tick", 0.03 + i * 0.04, 0.55)
sfx("glitch", o(0.98), 0.8)
sfx("impact", o(0.98), 0.9)
for v in V[1:]:
    if v["enter"] == "zoomblur":
        sfx("whoosh", v["from"], 0.85)
    elif v["enter"] == "cut":
        sfx("swish", v["from"], 0.6)
sfx("pop", o(5.08) + 0.03, 0.8)
sfx("pop", o(5.08) + 0.30, 0.6)
sfx("pop", o(7.08), 0.7)
sfx("pop", o(8.28), 0.6)
sfx("pop", o(10.84) + 0.10, 0.8)
sfx("whoosh_short", o(12.10), 0.7)
sfx("impact", o(13.74), 0.6)
sfx("pop", o(20.30) + 0.1, 0.7)
sfx("error", o(21.40), 0.7)
sfx("error", o(22.58), 0.7)
sfx("riser", o(25.90) - 1.0, 0.6)
sfx("boom", o(25.90), 1.0)
sfx("pop", o(30.22) + 0.05, 0.6)
sfx("pop", o(31.08), 0.6)
sfx("impact", o(33.46), 0.7)
sfx("pop", o(37.035) + 0.15, 0.6)
sfx("pop", o(40.99) + 0.1, 0.7)
for i in range(14):
    sfx("data", o(41.4) + i * 0.24, 0.35)
sfx("pop", o(42.61), 0.6)
sfx("pop", o(43.63), 0.6)
sfx("ding", o(44.97), 0.7)
sfx("pop", o(50.27) + 0.08, 0.7)
sfx("pop", o(51.81) + 0.1, 0.7)
sfx("pop", o(54.11) + 0.08, 0.7)
sfx("impact", o(75.31), 0.85)
sfx("pop", o(75.31) + 0.25, 0.6)
sfx("riser", VOICE_END - 1.2, 0.5)
sfx("boom", VOICE_END, 0.9)
sfx("stamp", VOICE_END + 0.55, 0.9)
sfx("ding", VOICE_END + 1.0, 0.5)

MUSIC = {"bpm": 140, "drop": round(o(4.905), 3), "dropout": [round(o(25.90) - 0.55, 3), round(o(25.90), 3)],
         "cta": round(o(72.69), 3), "end": round(VOICE_END, 3), "total": round(TOTAL, 3)}

edl = {"fps": FPS, "width": 1080, "height": 1920, "total": round(TOTAL, 4), "durationInFrames": int(round(TOTAL * FPS)),
       "voice": [{"src": [a, b], "out": round(st, 4)} for (a, b), st in zip(SEGS, OUT_STARTS)],
       "visuals": V, "overlays": OV, "subs": subs, "sfx": sorted(SFX, key=lambda x: x["t"]), "music": MUSIC}
json.dump(edl, open(os.path.join(S, "..", "remotion", "src", "edl.json"), "w"), ensure_ascii=False, indent=1)
print("total", TOTAL, "frames", edl["durationInFrames"], "visuals", len(V), "subs", len(subs), "sfx", len(SFX))
for s in subs:
    print(f"{s['from']:6.2f}-{s['to']:6.2f}  " + " / ".join(" ".join(w['t'] for w in ln) for ln in s['lines']))
# visual coverage check
cov = sorted((v["from"], v["to"]) for v in V)
for (a1, b1), (a2, b2) in zip(cov, cov[1:]):
    if abs(b1 - a2) > 0.02:
        print("GAP/OVERLAP", b1, a2)
