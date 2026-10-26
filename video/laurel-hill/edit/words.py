"""Word-level timing lookup from the voice-over transcript."""
import bisect
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def _load():
    segs = json.load(open(os.path.join(ROOT, "work", "words.json")))
    words = [(w["s"], w["e"], w["w"]) for s in segs for w in s["words"]]
    p = os.path.join(ROOT, "work", "retx.json")
    if os.path.exists(p):
        fix = json.load(open(p))
        for key, ws in fix.items():
            a, b = map(float, key.split("-"))
            ws = [w for w in ws if a + 0.5 <= w["s"] < b - 0.5]
            if not ws:
                continue
            a2, b2 = min(w["s"] for w in ws), max(w["e"] for w in ws)
            words = [w for w in words if not (a2 - 0.2 <= w[0] < b2 + 0.2)]
            words += [(w["s"], w["e"], w["w"]) for w in ws]
        words.sort()
    return words


WORDS = _load()
STARTS = [w[0] for w in WORDS]
NORMS = [norm(w[2]) for w in WORDS]


def at(word, near, window=8.0):
    """Start time of `word` (may be several words) closest after near-2s."""
    parts = [norm(p) for p in word.split()]
    i0 = bisect.bisect_left(STARTS, near - 2.0)
    best = None
    for i in range(i0, len(WORDS)):
        if STARTS[i] > near + window:
            break
        if all(i + k < len(NORMS) and NORMS[i + k].startswith(parts[k]) for k in range(len(parts))):
            d = abs(STARTS[i] - near)
            if best is None or d < best[0]:
                best = (d, STARTS[i])
    if best is None:
        raise KeyError(f"word {word!r} not found near {near}")
    return best[1]


def end_of(word, near, window=8.0):
    t = at(word, near, window)
    i = STARTS.index(t)
    n = len(word.split())
    return WORDS[i + n - 1][1]
