"""Convierte tiempos absolutos del timeline (según un EDL antiguo) a anclas de tiempo original: at(src).
Así, si el montaje cambia (nuevos cortes), los gráficos, b-rolls y SFX siguen pegados a su frase.
Uso: python3 retime_to_src.py <edl_antiguo.json> <archivo.ts[x]>...
"""
import json, re, sys
segs = json.load(open(sys.argv[1]))["segments"]

def to_src(t):
    for s in segs:
        d = s["srcOut"] - s["srcIn"]
        if s["outIn"] - 1e-6 <= t < s["outIn"] + d - 1e-6:
            return s["srcIn"] + (t - s["outIn"])
    last = segs[-1]
    return last["srcOut"] + (t - last["outIn"] - (last["srcOut"] - last["srcIn"]))

num = r"(\d+(?:\.\d+)?)"
conv = lambda m: m.group(0).replace(m.group("n"), f"at({to_src(float(m.group('n'))):.2f})", 1)
patterns = [
    rf"end: (?P<n>{num[1:-1]})",
    rf"t0: (?P<n>{num[1:-1]})",
    rf"t1: (?P<n>{num[1:-1]})",
    rf"\bs\((?P<n>{num[1:-1]}),",
    rf"typing\((?P<n>{num[1:-1]}),",
    rf"t0=\{{(?P<n>{num[1:-1]})\}}",
    rf"t1=\{{(?P<n>{num[1:-1]})\}}",
    rf"clickAt=\{{(?P<n>{num[1:-1]})\}}",
    rf"\bt: (?P<n>{num[1:-1]}) \}}",
]
for path in sys.argv[2:]:
    src = open(path).read()
    n0 = src.count("at(")
    for p in patterns:
        src = re.sub(p, lambda m: m.group(0) if float(m.group("n")) == 0 else conv(m), src)
    # listas de tiempos: BLUR_INS, FLASHES, FLICKERS, STREAKS
    def lst(m):
        items = [x.strip() for x in m.group(2).split(",")]
        out = [f"at({to_src(float(x)):.2f})" if re.fullmatch(r"\d+(?:\.\d+)?", x) else x for x in items]
        return f"{m.group(1)}[{', '.join(out)}]"
    src = re.sub(r"(export const (?:BLUR_INS|FLASHES|FLICKERS|STREAKS) = )\[([^\]]*)\]", lst, src)
    open(path, "w").write(src)
    print(path, "anclas at():", src.count("at(") - n0)
