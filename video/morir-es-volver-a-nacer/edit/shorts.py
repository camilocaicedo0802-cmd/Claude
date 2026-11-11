"""Shorts 1080x1920 sacados del video: video 16:9 al centro sobre fondo difuminado, gancho arriba y subtítulos
palabra por palabra (ASS). uso: python shorts.py VIDEO.mp4 MEZCLA.wav OUT_DIR"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")

# (nombre, inicio_frase, fin_frase, gancho en 2 líneas) — tiempos por palabras de la locución
SHORTS = [
    ("short_1_la_luz", ("Y", "entonces", "la"), ("naciste",), ("¿Y SI ESA LUZ", "NO ES EL CIELO?")),
    ("short_2_vidas_anteriores", ("morir", "y"), ("recuerdas", "las", "anteriores"), ("¿POR QUÉ NO RECUERDAS", "TUS VIDAS ANTERIORES?")),
    ("short_3_patrones", ("y", "si", "estas", "repitiendo"), ("pasado", "por", "ellos"), ("¿Y SI NO ES LA", "PRIMERA VEZ QUE LO VIVES?")),
]


def norm(s):
    import re
    import unicodedata
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def words():
    segs = json.load(open(os.path.join(ROOT, "work", "words.json")))
    return [(w["s"], w["e"], w["w"]) for s in segs for w in s["words"]]


def find(W, seq, after=0.0):
    n = [norm(x[2]) for x in W]
    for i in range(len(W)):
        if W[i][0] >= after and all(i + k < len(W) and n[i + k].startswith(seq[k]) for k in range(len(seq))):
            return i
    raise LookupError(seq)


def ts(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def ass(W, i0, i1, t0, hook, path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Bebas Neue,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,7,4,2,60,60,430,1
Style: Hook,Bebas Neue,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,7,4,8,50,50,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    dur = W[i1][1] - t0 + 1.2
    ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Hook,,0,0,0,,{{\\fad(250,300)}}{hook[0]}\\N{{\\c&H2216EB&}}{hook[1]}")
    # grupos de hasta 3 palabras; la palabra activa en amarillo
    i = i0
    while i <= i1:
        grp = list(range(i, min(i + 3, i1 + 1)))
        # cortar el grupo tras puntuación
        for k, j in enumerate(grp):
            if W[j][2].rstrip()[-1:] in ".?!,:" and k < len(grp) - 1:
                grp = grp[:k + 1]
                break
        for k, j in enumerate(grp):
            s = W[j][0] - t0
            nxt = W[grp[-1] + 1][0] if grp[-1] + 1 < len(W) else 1e9
            e = (W[grp[k + 1]][0] if k + 1 < len(grp) else min(W[j][1] + 0.15, nxt)) - t0
            if e <= s:
                continue
            txt = []
            for jj in grp:
                w = W[jj][2].upper().strip()
                txt.append(("{\\c&H00D6FF&}" + w + "{\\c&HFFFFFF&}") if jj == j else w)
            pop = "{\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
            ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{pop}{' '.join(txt)}")
        i = grp[-1] + 1
    open(path, "w").write(head + "\n".join(ev) + "\n")
    return dur


def main():
    video, mix, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    W = words()
    for name, a, b, hook in SHORTS:
        i0 = find(W, [norm(x) for x in a])
        i1 = find(W, [norm(x) for x in b], W[i0][0]) + len(b) - 1
        t0 = W[i0][0] - 0.25
        sub = os.path.join(out, name + ".ass")
        dur = ass(W, i0, i1, t0, hook, sub)
        fc = ("[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=28:2,eq=brightness=-0.22:saturation=0.8[bg];"
              "[b]scale=1242:-2,crop=1080:ih[fg];[bg][fg]overlay=0:(H-h)/2-40,"
              f"subtitles={name}.ass:fontsdir={os.path.relpath(FONTS, out).replace(os.sep, '/')},fade=t=out:st={dur - 0.6:.2f}:d=0.6[v];"
              f"[1:a]afade=t=in:d=0.15,afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]")
        dst = os.path.join(out, name + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", os.path.abspath(video),
                        "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", os.path.abspath(mix), "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.abspath(dst)], check=True, cwd=out)
        print(dst, round(dur, 1), "s, desde", round(t0, 1))


if __name__ == "__main__":
    main()
