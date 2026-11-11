"""Edit decision list -> timeline.json for the Slate "Spray tan problems" reel.

All times in the output are seconds on the final timeline (30 fps, 1080x1920).
"""
import json, sys, os

W = sys.argv[1]
OUT = os.path.join(W, "timeline.json")
FPS = 30
MUSIC_OFFSET = 13.40          # start the track on a strong kick
voice = json.load(open(os.path.join(W, "voice_segs.json")))
tr = json.load(open(os.path.join(W, "transcript_med.json")))
voice["A7a"] = ["IMG_7106", 14.14, 17.04]      # "book your appointment ... before your wedding" (no trailing "and")
beats_all = json.load(open(os.path.join(W, "beats.json")))["beats"]
BEATS = [b - MUSIC_OFFSET for b in beats_all if b >= MUSIC_OFFSET]


def words(src, a, b):
    """Transcribed words (abs source time) inside [a, b]."""
    out = []
    for s in tr[src + ".wav"]:
        for ws, we, w in s["words"]:
            if ws >= a - 0.02 and ws < b:
                out.append([ws, we, w.strip()])
    return out


def snap_beat(t, mode="next", min_t=None):
    cands = [b for b in BEATS if (min_t is None or b >= min_t)]
    if mode == "next":
        c = [b for b in cands if b >= t - 0.04]
        return c[0] if c else t
    return min(cands, key=lambda b: abs(b - t))


# ---------------------------------------------------------------- copy
# problem text words are mapped 1:1 onto the transcribed words of the question take
PAIRS = [
    dict(q="Q1", a=["A1"], problem=["Pale", "or", "dull", "skin?"],
         sol=[["A", None], ["custom", None], ["spray tan", "accent"]], sol_sync=["A", "custom", "spray"],
         P="p1_pale", S="s1_after"),
    dict(q="Q2", a=["A2"], problem=["Need", "color", "ASAP?"],
         sol=[["Rapid", "accent"], ["tan formula", None]], sol_sync=["rapid", "formula"],
         P="p2_asap", S="s2_spray"),
    dict(q="Q3", a=["A3"], problem=["Dry", "or", "patchy", "skin?"],
         sol=[["Exfoliate", "accent"], ["24 hours before", None]], sol_sync=["Exfoliate", "24"],
         P="p3_dry", S="s3_exfoliate", S2="s3_exfoliate2", S2_key="24"),
    dict(q="Q4", a=["A4"], problem=["Tan", "fading", "unevenly?"],
         sol=[["Moisturize", "accent"], ["daily", None]], sol_sync=["Moisturize", "daily."],
         P="p4_fading", S="s4_moisturize"),
    dict(q="Q5", a=["A5"], problem=["Tan", "sticking|", "to", "hands", "&", "feet?"],
         sol=[["Barrier cream", "accent"], ["in the room", None]], sol_sync=["barrier", "in"],
         P="p5_hands", S="s5_barrier"),
    dict(q="Q6", a=["A6"], problem=["Going", "on", "vacation?"],
         sol=[["Book", None], ["1–2 days", "accent"], ["before your trip", None]], sol_sync=["Book", "one", "before"],
         P="p6_vacation", S="s6_glow"),
    dict(q="Q7", a=["A7a", "A7b"], problem=["Wedding", "or|", "special", "event?"],
         sol=[["Proper prep", None], ["+", None], ["custom shade", "accent"]], sol_sync=["book", "custom", "custom"],
         P="p7_event", S="s7_event", S2="s7_spray", S2_voice="A7b"),
    dict(q="Q8", a=["A8"], problem=["Not", "sure", "which", "shade", "or", "solution", "is", "right", "for", "you?"],
         sol=[["Personalized", "accent"], ["consultation", None]], sol_sync=["personalized", "consultation."],
         P="p8_unsure", S="s8_consult"),
]
# manual word-time fixes (whisper merged "Tan fading")
FIX = {("Q4", 1): 34.58}

HOOK_END = 2.60          # beat 4
QA_GAP = 0.10
PAIR_TAIL = 0.22


def tighten(seg):
    src, a, b = seg
    ww = [w for s_ in tr[src + ".wav"] for w in s_["words"] if w[0] >= a - 0.02 and w[0] < b]
    if not ww:
        return seg
    return [src, round(max(a, ww[0][0] - 0.12), 2), round(min(b, ww[-1][1] + 0.24), 2)]


for k in list(voice):
    if k not in ("A7a", "A7b", "C3a"):
        voice[k] = tighten(voice[k])

timeline = {"fps": FPS, "w": 1080, "h": 1920, "music_offset": MUSIC_OFFSET,
            "beats": BEATS[:120], "voice": [], "pairs": [], "sfx": []}

t = HOOK_END
for i, p in enumerate(PAIRS):
    qsrc, qin, qout = voice[p["q"]]
    pair = {"n": i + 1, "start": t, "P": p["P"], "S": p["S"], "problem": [], "sol": p["sol"]}
    qstart = t + 0.10
    timeline["voice"].append({"id": p["q"], "src": qsrc, "in": qin, "out": qout, "at": qstart, "kind": "q"})
    qw = words(qsrc, qin, qout)
    # skip filler words before the question ("Okay", "I'm")
    qw = [w for w in qw if w[2].lower().strip(",.") not in ("okay", "i'm")]
    for k, txt in enumerate(p["problem"]):
        ws = qw[min(k, len(qw) - 1)][0] if k < len(qw) else qw[-1][0] + 0.12 * (k - len(qw) + 1)
        ws = FIX.get((p["q"], k), ws)
        pair["problem"].append([txt, round(qstart + ws - qin, 3)])
    q_first = qstart + qw[0][0] - qin
    t_after_q = qstart + (qout - qin)
    # answer voice (one or two takes, butted together)
    at = t_after_q + QA_GAP
    q_last_end0 = qstart + qw[-1][1] - qin
    a0src, a0in, a0out = voice[p["a"][0]]
    a0w = words(a0src, a0in, a0out)
    off = a0w[0][0] - a0in
    at = max(at, q_last_end0 + 0.50 - off)
    a_words = []
    a_first = None
    for aid in p["a"]:
        asrc, ain, aout = voice[aid]
        timeline["voice"].append({"id": aid, "src": asrc, "in": ain, "out": aout, "at": at, "kind": "a"})
        for ws, we, w in words(asrc, ain, aout):
            a_words.append([round(at + ws - ain, 3), round(at + we - ain, 3), w])
        if a_first is None:
            a_first = a_words[0][0]
        at += (aout - ain)
    a_end = at
    # solution sync points: first transcribed word that starts with the sync key
    sync = []
    used = 0
    for key in p["sol_sync"]:
        k = key.lower().strip(".,")
        hit = None
        for j in range(used, len(a_words)):
            if a_words[j][2].lower().strip(".,").startswith(k):
                hit = j
                break
        if hit is None:
            sync.append(sync[-1] + 0.25 if sync else a_first)
        else:
            sync.append(a_words[hit][0])
            used = hit
    q_last_end = qstart + qw[-1][1] - qin
    split = max(q_last_end + 0.03, a_first - 0.45)
    split = min(split, a_first - 0.12)
    pair.update(q_first=round(q_first, 3), split=round(split, 3), a_first=round(a_first, 3),
                sol_times=[round(s, 3) for s in sync], a_end=round(a_end, 3))
    if p.get("S2"):
        if p.get("S2_voice"):
            s2 = [v["at"] for v in timeline["voice"] if v["id"] == p["S2_voice"]][0] - 0.05
        else:
            s2 = [w[0] for w in a_words if w[2].lower().startswith(p["S2_key"])][0] - 0.12
        pair["S2"] = p["S2"]
        pair["s2_at"] = round(s2, 3)
    end = snap_beat(a_end + PAIR_TAIL)
    if end - (a_end + PAIR_TAIL) > 0.30:            # don't wait too long for the beat
        end = a_end + PAIR_TAIL
    pair["end"] = round(end, 3)
    timeline["pairs"].append(pair)
    t = end

# ---------------------------------------------------------------- outro (talking head, lip-synced)
OUT0 = t
ot = OUT0 + 0.10
outro = {"start": OUT0, "clips": [], "captions": []}
CAP = {
    "C1": [["Every skin tone,", "Every"], ["undertone", "undertone"], ["& glow goal", "and"], ["is *different*", "is"]],
    "C2": [["Your spray tan", "Your"], ["should be *too*", "should"]],
    "C3a": [["If you relate", "If"], ["to any of this,", "to"]],
    "C3b": [["come see us", "Come"], ["at *Slate*", "at"], ["& we'll find", "and"], ["the *perfect tan*", "the"], ["for you ✦", "for"]],
}
GAPS = {"C1": 0.10, "C2": 0.06, "C3a": 0.04, "C3b": 0.0}
seg_times = {}
for cid in ["C1", "C2", "C3a", "C3b"]:
    ot += GAPS[cid]
    src, a, b = voice[cid]
    timeline["voice"].append({"id": cid, "src": src, "in": a, "out": b, "at": ot, "kind": "c"})
    ww = words(src, a, b)
    # in C3b the first "Come" belongs to this take
    used = 0
    for text, key in CAP[cid]:
        hit = None
        for j in range(used, len(ww)):
            if ww[j][2].lower().strip(".,").startswith(key.lower()):
                hit = j
                break
        if hit is None:
            continue
        outro["captions"].append([text, round(ot + ww[hit][0] - a, 3)])
        used = hit + 1
    seg_times[cid] = (ot, ot + (b - a), src, a)
    ot += (b - a)
# caption end times = next caption start (or segment end)
caps = outro["captions"]
for k in range(len(caps)):
    nxt = caps[k + 1][1] if k + 1 < len(caps) else ot + 0.6
    caps[k].append(round(nxt, 3))

# visual clips in the outro: talking head (lip-synced) + inserts
c1s, c1e, src1, a1 = seg_times["C1"]
def at_word(cid, key, nth=0):
    s, e, src, a = seg_times[cid]
    b = voice[cid][2]
    hits = [w for w in words(src, a, b) if w[2].lower().strip(".,").startswith(key.lower())]
    return s + hits[nth][0] - a
w_skin = at_word("C1", "skin")
w_under = at_word("C1", "undertone")
w_glow = at_word("C1", "glow")
w_is = at_word("C1", "is")
c2s, c2e, _, _ = seg_times["C2"]
c3as, c3ae, _, _ = seg_times["C3a"]
c3bs, c3be, _, _ = seg_times["C3b"]
w_and = at_word("C3b", "and")
END = c3be + 1.10
w_for = at_word("C3b", "for")
outro["clips"] = [
    {"kind": "talk", "start": OUT0, "end": w_skin - 0.04, "zoom": [1.0, 1.03]},
    {"kind": "photo", "asset": "o_res1", "start": w_skin - 0.04, "end": w_under - 0.04, "flash": True},
    {"kind": "photo", "asset": "o_res2", "start": w_under - 0.04, "end": w_glow - 0.04, "flash": True},
    {"kind": "photo", "asset": "o_res3", "start": w_glow - 0.04, "end": w_is - 0.02, "flash": True},
    {"kind": "talk", "start": w_is - 0.02, "end": c2s - 0.03, "zoom": [1.03, 1.05]},
    {"kind": "talk", "start": c2s - 0.03, "end": c3as - 0.02, "zoom": [1.10, 1.12]},
    {"kind": "talk", "start": c3as - 0.02, "end": c3bs - 0.02, "zoom": [1.0, 1.03]},
    {"kind": "video", "asset": "o_slate", "start": c3bs - 0.02, "end": w_and - 0.04, "punch": True},
    {"kind": "video", "asset": "o_desk", "start": w_and - 0.04, "end": w_for - 0.06, "punch": True},
    {"kind": "video", "asset": "o_final", "start": w_for - 0.06, "end": END, "punch": True},
]
# talking head time mapping: timeline -> source time (only valid inside voice segments; between
# segments we hold the nearest segment edge so lips never drift)
outro["talk_map"] = [[s, e, src, a] for (s, e, src, a) in seg_times.values()]
outro["end"] = END
timeline["outro"] = outro
timeline["hook"] = {"start": 0.0, "end": HOOK_END}
timeline["duration"] = round(END, 3)
json.dump(timeline, open(OUT, "w"), indent=1, ensure_ascii=False)

# report
print(f"hook 0.00-{HOOK_END:.2f}")
for p in timeline["pairs"]:
    print(f"P{p['n']} {p['start']:6.2f}-{p['end']:6.2f}  q_first={p['q_first']:6.2f} split={p['split']:6.2f} a_end={p['a_end']:6.2f}  prob={[w[1] for w in p['problem']]} sol={p['sol_times']}")
print(f"outro {OUT0:.2f}-{END:.2f}")
for c in outro["captions"]:
    print("   cap", c)
for c in outro["clips"]:
    print("   clip", c["kind"], c.get("asset", ""), round(c["start"], 2), round(c["end"], 2))
print("duration", END)
