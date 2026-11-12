"""Per-frame layout shared by the compositor and the text overlay.

The talking head is the base layer for the whole video (after the hook): every frame maps to a voice
segment and a source time, so lips are always in sync. Support visuals live in cards:
problem card on top, solution card at the bottom, polaroids/Slate card in the outro.

usage: python3 layout.py <work>   -> <work>/layout.json
"""
import json, math, os, sys

W = sys.argv[1]
T = json.load(open(os.path.join(W, "timeline.json")))
F = json.load(open(os.path.join(W, "talk_faces.json")))
FPS = 30
N = int(math.ceil(T["duration"] * FPS))

clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
lerp = lambda a, b, e: a + (b - a) * e
def e_out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def e_in_cubic(x): x = clamp(x); return x ** 3
def e_out_back(x, s=1.3):
    x = clamp(x); c3 = s + 1; return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2

TOP = dict(x=90, y=230, w=900, h=230)          # text-only band (no card) – kept for the overlay
BOT = dict(x=90, y=1206, w=900, h=300)
SQ, GAP = 300, 28
SQ_X = (540 - SQ - GAP // 2, 540 + GAP // 2)          # before (left) / after (right)
OFF_TOP, OFF_BOT = -500, 1960
ENTER, EXIT = 0.36, 0.20

ZOOM = {"q": 1.25, "a": 1.32, "h": 1.22}
ZOOM_C = {"C1": 1.24, "C2": 1.36, "C3a": 1.26, "C3b": 1.31}

# ------------------------------------------------------------------ talking head mapping
HOOK_SEG = {"id": "H", "src": "IMG_7108", "in": 0.20, "out": 2.80, "kind": "h", "at": 0.0}
segs = sorted(T["voice"] + [HOOK_SEG], key=lambda v: v["at"])
for v in segs:
    f = F[v["id"]]
    v["t0"], v["t1"] = f["t0"], f["t1"]               # source range covered by the mezz
    v["end"] = v["at"] + (v["out"] - v["in"])
    v["zoom"] = ZOOM_C.get(v["id"], ZOOM.get(v["kind"], 1.35))
    v["n"] = len(f["faces"])


def face_ok(v, src):
    i = int(round((src - v["t0"]) * FPS))
    if i < 0 or i >= v["n"]:
        return False
    return F[v["id"]]["faces"][i] is not None


# one cut per gap: at the pair boundary if the gap spans one, otherwise when the previous line ends
PAIR_B = [T["hook"]["end"]] + [p["end"] for p in T["pairs"]]
HOOK_END_ = T["hook"]["end"]
for k, v in enumerate(segs):
    if k == 0:
        v["vs"] = 0.0
        continue
    prev = segs[k - 1]
    lo, hi = prev["end"], v["at"]
    c = next((B for B in PAIR_B if lo - 0.05 <= B <= hi + 0.05), lo)
    c = min(max(c, v["at"] - (v["in"] - v["t0"]) + 0.02), hi)         # enough pre-roll in the mezz
    c = max(min(c, prev["end"] + (prev["t1"] - prev["out"]) - 0.04), lo)  # enough post-roll
    v["vs"] = c
for k, v in enumerate(segs):
    v["ve"] = segs[k + 1]["vs"] if k + 1 < len(segs) else 1e9


def talk_at(t):
    """-> (segment, source time)"""
    for v in segs:
        if v["vs"] <= t < v["ve"]:
            src = v["in"] + (t - v["at"])
            return v, min(max(src, v["t0"]), v["t1"] - 0.04)
    v = segs[0]
    return v, max(v["in"] + (t - v["at"]), v["t0"])


# ------------------------------------------------------------------ card schedule
cards = []
for p in T["pairs"]:
    end = p["end"]
    cards.append(dict(slot="bot", role="problem", pair=p["n"], asset=p["P"], t_in=p["start"] + 0.06,
                      t_out=end - EXIT, bx=SQ_X[0], bw=SQ, dim_at=p["split"]))
    c = dict(slot="bot", role="solution", pair=p["n"], asset=p["S"], t_in=p["split"], t_out=end - EXIT,
             bx=SQ_X[1], bw=SQ)
    if p.get("S2"):
        c.update(asset2=p["S2"], t2=p["s2_at"])
    cards.append(c)

cap_list = T["outro"]["captions"]
def cap_t(prefix):
    for c in cap_list:
        if c[0].startswith(prefix):
            return c[1]
    raise KeyError(prefix)
END = T["outro"]["end"]
# results of three clients: three square tiles in the bottom slot, one per "skin tone / undertone / glow goal"
r1, r2, r3 = cap_t("Every skin") + 0.25, cap_t("undertone") - 0.02, cap_t("& glow") + 0.06
tw = (BOT["w"] - 2 * 21) // 3
for k, (aid, tin) in enumerate([("o_res1", r1), ("o_res2", r2), ("o_res3", r3)]):
    cards.append(dict(slot="bot", role="outro", pair=0, asset=aid, t_in=tin, t_out=cap_t("Your spray") - 0.22,
                      bx=BOT["x"] + k * (tw + 21), bw=tw))
cards.append(dict(slot="bot", role="outro", pair=0, asset="o_slate", t_in=cap_t("come see") - 0.10,
                  t_out=END + 1.0, seq=[["o_desk", cap_t("& we'll") - 0.06]]))


def card_state(c, t):
    if t < c["t_in"] - 0.001 or t >= c["t_out"] + EXIT:
        return None
    st = {k: c[k] for k in ("slot", "role", "asset") if k in c}
    st["pair"] = c.get("pair", 0)
    st["lt"] = round(t - c["t_in"], 4)
    seq = c.get("seq") or ([[c["asset2"], c["t2"]]] if c.get("asset2") else [])
    prev_a, prev_t = c["asset"], c["t_in"]
    for a2, t2 in seq:
        if t >= t2:
            st["asset"], st["lt"] = prev_a, round(t - prev_t, 4)
            st["asset2"], st["lt2"], st["mix"] = a2, round(t - t2, 4), round(clamp((t - t2) / 0.24), 4)
            prev_a, prev_t = a2, t2
    pin = (t - c["t_in"]) / ENTER
    pout = (t - c["t_out"]) / EXIT
    if c["slot"] == "pol":
        e = e_out_back(pin, 2.0)
        sc = lerp(0.55, 1.0, e)
        dy = lerp(-40, 0, e_out_cubic(pin)) - 560 * e_in_cubic(pout)
        st.update(cx=c["cx"], cy=round(c["cy"] + dy, 2), rot=round(c["rot"] + (1 - e_out_cubic(pin)) * -10, 3),
                  scale=round(sc, 4), alpha=round(clamp(pin * 3) * (1 - clamp(pout * 1.5)), 4))
        return st
    rest = TOP if c["slot"] == "top" else BOT
    off = OFF_TOP if c["slot"] == "top" else OFF_BOT
    y = lerp(off, rest["y"], e_out_cubic(pin))
    if pout > 0:
        y = lerp(rest["y"], off, e_in_cubic(pout))
    st.update(x=c.get("bx", rest["x"]), y=round(y, 2), w=c.get("bw", rest["w"]), h=rest["h"],
              dim=round(0.10 * e_out_cubic((t - c["dim_at"]) / 0.3), 4) if c.get("dim_at") else 0.0)
    return st


# ------------------------------------------------------------------ frames
HOOK_END = T["hook"]["end"]
bounds = [p["end"] for p in T["pairs"][:-1]]          # pair -> pair cuts get a zoom punch
frames = []
for f in range(N):
    t = f / FPS
    fr = {"t": round(t, 4)}
    if True:
        v, src = talk_at(t)
        z = v["zoom"] * (1 + 0.025 * clamp((t - v["vs"]) / max(v["ve"] - v["vs"], 0.1) if v["ve"] < 1e8 else (t - v["vs"]) / 3))
        punch = 1.0
        for B in [HOOK_END] + bounds + [T["pairs"][-1]["end"]]:
            if B <= t < B + 0.26:
                punch = 1 + 0.06 * (1 - e_out_cubic((t - B) / 0.26))
        med = F[v["id"]]["median"]
        fr["base"] = {"kind": "talk", "seg": v["id"], "src": round(src - v["t0"], 4), "zoom": round(z, 4),
                      "punch": round(punch, 4), "face": med}
    cs = [s for s in (card_state(c, t) for c in cards) if s]
    fr["cards"] = cs
    frames.append(fr)

json.dump({"fps": FPS, "n": N, "top": TOP, "bot": BOT, "frames": frames}, open(os.path.join(W, "layout.json"), "w"))
# summary
cuts = []
prev = None
for fr in frames:
    b = fr["base"]
    key = b.get("seg", "hook")
    if key != prev:
        cuts.append((fr["t"], key, b.get("src")))
        prev = key
for c in cuts:
    print("cut", c)
miss = {}
for fr in frames:
    b = fr["base"]
    if b["kind"] == "talk":
        v = next(x for x in segs if x["id"] == b["seg"])
        if not face_ok(v, v["t0"] + b["src"]):
            miss.setdefault(b["seg"], []).append(fr["t"])
for v in segs:
    fx, fy, fw = F[v["id"]]["median"]
    z = v["zoom"]
    wh = 2880 / z
    y0 = min(max(fy * 2880 - 840 * (wh / 1920), 0), 2880 - wh)
    cy = (fy * 2880 - y0) * 1920 / wh
    fh = fw * 405 / 720 * 1920 * z
    print("seg", v["id"], "face_y", round(cy), "chin~", round(cy + 0.62 * fh), "hair~", round(cy - 0.95 * fh))
for k, ts in miss.items():
    print("no-face frames", k, len(ts), ts[0], ts[-1])
print("frames", N)
