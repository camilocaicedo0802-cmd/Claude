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

TOP = dict(x=44, y=168, w=992, h=440)
BOT = dict(x=44, y=1252, w=992, h=448)
OFF_TOP, OFF_BOT = -500, 1980
ENTER, EXIT = 0.42, 0.22

ZOOM = {"q": 1.28, "a": 1.42}
ZOOM_C = {"C1": 1.30, "C2": 1.47, "C3a": 1.34, "C3b": 1.40}

# ------------------------------------------------------------------ talking head mapping
segs = sorted(T["voice"], key=lambda v: v["at"])
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
PAIR_B = [p["end"] for p in T["pairs"]]
HOOK_END_ = T["hook"]["end"]
for k, v in enumerate(segs):
    if k == 0:
        v["vs"] = HOOK_END_
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
    cards.append(dict(slot="top", role="problem", pair=p["n"], asset=p["P"], t_in=p["start"] + 0.04,
                      t_out=end - EXIT, dim_at=p["split"]))
    c = dict(slot="bot", role="solution", pair=p["n"], asset=p["S"], t_in=p["split"], t_out=end - EXIT)
    if p.get("S2"):
        c.update(asset2=p["S2"], t2=p["s2_at"])
    cards.append(c)

caps = {c[0]: c for c in T["outro"]["captions"]}
cap_list = T["outro"]["captions"]
def cap_t(prefix):
    for c in cap_list:
        if c[0].startswith(prefix):
            return c[1]
    raise KeyError(prefix)
POL = [dict(cx=226, cy=392, rot=-7), dict(cx=546, cy=372, rot=3), dict(cx=862, cy=398, rot=8)]
pol_in = [cap_t("Every skin") + 0.30, cap_t("undertone") - 0.02, cap_t("& glow") + 0.08]
pol_out = cap_t("Your spray") - 0.25
for k, aid in enumerate(["o_res1", "o_res2", "o_res3"]):
    cards.append(dict(slot="pol", role="outro", asset=aid, t_in=pol_in[k], t_out=pol_out + 0.05 * k, **POL[k]))
END = T["outro"]["end"]
cards.append(dict(slot="top", role="outro", pair=0, asset="o_slate", t_in=cap_t("come see") - 0.10,
                  t_out=END + 1.0, asset2="o_desk", t2=cap_t("& we'll") - 0.06))


def card_state(c, t):
    if t < c["t_in"] - 0.001 or t >= c["t_out"] + EXIT:
        return None
    st = {k: c[k] for k in ("slot", "role", "asset") if k in c}
    st["pair"] = c.get("pair", 0)
    st["lt"] = round(t - c["t_in"], 4)
    if c.get("asset2") and t >= c["t2"]:
        st["asset2"] = c["asset2"]
        st["lt2"] = round(t - c["t2"], 4)
        st["mix"] = round(clamp((t - c["t2"]) / 0.24), 4)
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
    y = lerp(off, rest["y"], e_out_back(pin, 1.25))
    if pout > 0:
        y = lerp(rest["y"], off, e_in_cubic(pout))
    st.update(x=rest["x"], y=round(y, 2), w=rest["w"], h=rest["h"],
              dim=round(0.12 * e_out_cubic((t - c["dim_at"]) / 0.3), 4) if c.get("dim_at") else 0.0)
    return st


# ------------------------------------------------------------------ frames
HOOK_END = T["hook"]["end"]
bounds = [p["end"] for p in T["pairs"][:-1]]          # pair -> pair cuts get a zoom punch
frames = []
for f in range(N):
    t = f / FPS
    fr = {"t": round(t, 4)}
    if t < HOOK_END:
        fr["base"] = {"kind": "hook"}
    else:
        v, src = talk_at(t)
        z = v["zoom"] * (1 + 0.025 * clamp((t - v["vs"]) / max(v["ve"] - v["vs"], 0.1) if v["ve"] < 1e8 else (t - v["vs"]) / 3))
        punch = 1.0
        for B in bounds + [T["pairs"][-1]["end"]]:
            if B <= t < B + 0.26:
                punch = 1 + 0.10 * (1 - e_out_cubic((t - B) / 0.26))
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
for k, ts in miss.items():
    print("no-face frames", k, len(ts), ts[0], ts[-1])
print("frames", N)
