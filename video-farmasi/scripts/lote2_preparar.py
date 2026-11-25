"""Lote 2 · monta el A-roll multi-clip de un vídeo a partir de datos/lote2/<vid>_guion.py

Uso: python3 scripts/lote2_preparar.py v1 [--sin-video] [--sin-audio]

Salidas (no versionadas):
  public/lote2/edit/<vid>_aroll.mp4   1080x1920 · 29,97 fps · cada toma recortada del 4K con su encuadre
  public/lote2/edit/<vid>_voz.wav     voz cortada (microfundidos de 12 ms), igualada por toma y procesada
  src/lote2/datos/<vid>.json          segmentos, anclas y bloques de subtítulos (con anchos de palabra medidos)

Los tiempos por palabra salen de Whisper large-v3 sobre la ventana exacta de cada toma (en caché) y se alinean
con el texto corregido del guion (nombres propios, ortografía, palabras clave).
"""
import difflib, importlib.util, json, os, re, subprocess, sys, unicodedata
from concurrent.futures import ThreadPoolExecutor
import numpy as np

VID = sys.argv[1]
spec = importlib.util.spec_from_file_location("guion", f"datos/lote2/{VID}_guion.py")
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
FPS_SRC = 30000 / 1001
SRC_W, SRC_H = 2160, 3840
os.makedirs("public/lote2/edit/tmp", exist_ok=True)
os.makedirs("src/lote2/datos", exist_ok=True)
os.makedirs("datos/lote2/cache", exist_ok=True)

# ---------- segmentos en tiempo de edición (cortes a fotograma exacto de la fuente) ----------
segs = []; t = 0.0
for i, s in enumerate(G.SEGMENTOS):
    fa = round(s["a"] * FPS_SRC); n = round((s["b"] - s["a"]) * FPS_SRC)
    a = fa / FPS_SRC; d = n / FPS_SRC
    segs.append({**s, "i": i, "a": a, "b": a + d, "n": n, "dur": d, "editStart": t})
    t += d
TOTAL = t

# ---------- vídeo ----------
def recorte(enc):
    z, ax, ay = G.ENCUADRES[enc]
    cw = int(round(SRC_W / z / 2) * 2); ch = int(round(SRC_H / z / 2) * 2)
    x = int(round(ax * (SRC_W - cw) / 2) * 2); y = int(round(ay * (SRC_H - ch) / 2) * 2)
    return f"crop={cw}:{ch}:{x}:{y}"

def enc_video(s):
    out = f"public/lote2/edit/tmp/{VID}_{s['i']:02d}.mp4"
    vf = f"{recorte(s['enc'])},scale=1080:1920:flags=lanczos,setsar=1"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.4f}", "-i", G.FUENTE.format(clip=s["clip"]),
                    "-frames:v", str(s["n"]), "-vf", vf, "-r", "30000/1001", "-an", "-c:v", "libx264", "-crf", "14",
                    "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "30", out], check=True)
    return out

if "--sin-video" not in sys.argv:
    with ThreadPoolExecutor(3) as ex:
        partes = list(ex.map(enc_video, segs))
    lista = f"public/lote2/edit/tmp/{VID}_lista.txt"
    open(lista, "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in partes))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy",
                    f"public/lote2/edit/{VID}_aroll.mp4"], check=True)

# ---------- audio: voz por toma, igualada, con microfundidos ----------
def wav16(clip):
    p = f"datos/lote2/cache/{clip}_16k.wav"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", G.FUENTE.format(clip=clip), "-vn", "-ac", "1", "-ar", "16000", p], check=True)
    return p

import soundfile as sf
audio = {c: sf.read(wav16(c))[0].astype(np.float32) for c in sorted({s["clip"] for s in segs})}

def nivel_voz(s):
    x = audio[s["clip"]][int(s["a"] * 16000):int(s["b"] * 16000)]
    hop = 320; n = len(x) // hop
    r = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)]) + 1e-9
    return 20 * np.log10(np.percentile(r, 85))

if "--sin-audio" not in sys.argv:
    niveles = [nivel_voz(s) for s in segs]
    ref = float(np.median([n for s, n in zip(segs, niveles) if not s.get("mudo")]))
    f = 0.012
    entradas = []; filtros = []
    for k, s in enumerate(segs):
        entradas += ["-i", G.FUENTE.format(clip=s["clip"])]
        g = -60 if s.get("mudo") else max(-6, min(6, ref - niveles[k]))  # "mudo": solo imagen (plano de cierre)
        filtros.append(f"[{k}:a]atrim=start={s['a']:.5f}:duration={s['dur']:.5f},asetpts=PTS-STARTPTS,aresample=48000,"
                       f"pan=mono|c0=0.5*c0+0.5*c1,volume={g:.2f}dB,afade=t=in:d={f},afade=t=out:st={s['dur'] - f:.4f}:d={f}[a{k}]")
    cadena = ";".join(filtros) + ";" + "".join(f"[a{k}]" for k in range(len(segs))) + \
        f"concat=n={len(segs)}:v=0:a=1,highpass=f=90,afftdn=nf=-30,equalizer=f=250:t=q:w=1.2:g=-2," \
        "equalizer=f=3200:t=q:w=1.5:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=4:release=90:makeup=2," \
        "loudnorm=I=-16:TP=-1.5:LRA=7[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", cadena, "-map", "[out]", "-ar", "48000", "-ac", "2",
                    f"public/lote2/edit/{VID}_voz.wav"], check=True)

# ---------- tiempos por palabra (Whisper sobre la ventana de cada toma) ----------
_modelo = None
def whisper(s):
    p = f"datos/lote2/cache/w_{s['clip']}_{s['a']:.3f}_{s['b']:.3f}.json"
    if os.path.exists(p): return json.load(open(p))
    global _modelo
    if _modelo is None:
        from faster_whisper import WhisperModel
        _modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
    a0 = max(0, s["a"] - 0.15)
    x = audio[s["clip"]][int(a0 * 16000):int((s["b"] + 0.15) * 16000)]
    sg, _ = _modelo.transcribe(x, language="es", word_timestamps=True, beam_size=5, vad_filter=False)
    ws = [[w.word.strip(), round(a0 + w.start, 3), round(a0 + w.end, 3)] for z in sg for w in z.words]
    json.dump(ws, open(p, "w"), ensure_ascii=False)
    return ws

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

# ---------- tokens del guion ----------
def tokens(s):
    out = []
    for quien, texto in s.get("txt", []):
        abierta = False
        for raw in texto.split():
            if raw == "/":
                if out: out[-1]["corte"] = True
                continue
            ancla = None
            if "@" in raw: raw, ancla = raw.split("@", 1)
            pre = re.match(r"^[¿¡]*", raw).group(0)
            empieza = raw[len(pre):].startswith("*")
            cuerpo = raw.replace("*", "")
            termina = raw.rstrip("?!.,").endswith("*")
            clave = abierta or empieza
            if empieza: abierta = True
            if termina: abierta = False
            vis = re.sub(r"[.,;:]", "", cuerpo)
            out.append({"vis": vis, "n": norm(cuerpo), "quien": quien, "clave": clave, "finClave": clave and not abierta,
                        "ancla": ancla, "fin": bool(re.search(r"[.?!]$", cuerpo))})
    return out

def alinear(toks, ws, s):
    """Asigna (inicio, fin) de fuente a cada token alineando con las palabras de Whisper."""
    A = [t["n"] for t in toks]; B = [norm(w[0]) for w in ws]
    tiempos = [None] * len(toks)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1): tiempos[i1 + k] = (ws[j1 + k][1], ws[j1 + k][2])
        elif op == "replace":
            ta, tb = ws[j1][1], ws[j2 - 1][2]; paso = (tb - ta) / (i2 - i1)
            for k in range(i2 - i1): tiempos[i1 + k] = (ta + k * paso, ta + (k + 1) * paso)
    # huecos (tokens sin palabra): interpolar entre vecinos
    for k in range(len(toks)):
        if tiempos[k] is None:
            prev = next((tiempos[j][1] for j in range(k - 1, -1, -1) if tiempos[j]), s["a"])
            nxt = next((tiempos[j][0] for j in range(k + 1, len(toks)) if tiempos[j]), s["b"])
            tiempos[k] = (prev, max(prev + 0.08, (prev + nxt) / 2))
    # Whisper a veces alarga el inicio de una palabra tras un silencio: limitarlo a 0,65 s antes de su fin
    for k, (a, b) in enumerate(tiempos):
        tiempos[k] = (max(a, b - 0.65), b)
    return tiempos

# ---------- medidas reales de las fuentes ----------
from PIL import ImageFont
FUENTES = {"ctx": ImageFont.truetype("public/fuentes/cliente/HelveticaNeue-Medium.otf", 200),
           "clave": ImageFont.truetype("public/fuentes/cliente/HelveticaNeue-Heavy.otf", 200)}
TRACK = {"ctx": -0.035, "clave": -0.03}
TAM = {"ctx": 64, "clave": 96}
ESPACIO = 0.25
MAX_CTX = 700  # px
MAX_CLAVE = 880

def ancho_em(txt, tipo):
    return FUENTES[tipo].getlength(txt) / 200 + len(txt) * TRACK[tipo]

def ancho_linea(ps, tipo):
    return sum(p["w"] for p in ps) * TAM[tipo] + ESPACIO * TAM[tipo] * (len(ps) - 1)

# ---------- palabras en tiempo de edición y bloques ----------
palabras = []; anclas = {}
for s in segs:
    toks = tokens(s)
    if not toks: continue
    tm = alinear(toks, whisper(s), s)
    for tk, (a, b) in zip(toks, tm):
        ea = s["editStart"] + max(0.0, a - s["a"]); eb = s["editStart"] + min(b, s["b"]) - s["a"]
        tk.update({"s": round(ea, 3), "e": round(max(eb, ea + 0.08), 3), "seg": s["i"], "enc": s["enc"]})
        palabras.append(tk)
        if tk["ancla"]: anclas[tk["ancla"]] = {"s": tk["s"], "e": tk["e"], "seg": s["i"]}

bloques = []
actual = None
def cerrar():
    global actual
    if actual and actual["lineas"]: bloques.append(actual)
    actual = None

for k, p in enumerate(palabras):
    pos_key = (p["enc"], p["quien"])
    nuevo = actual is None or actual["_key"] != pos_key
    if not nuevo and k > 0 and p["s"] - palabras[k - 1]["e"] > 0.55: nuevo = True
    if nuevo:
        cerrar()
        x, y, lado = G.POS.get(pos_key, (540, 1270, None))
        actual = {"_key": pos_key, "quien": p["quien"], "x": x, "y": y, "lado": lado, "lineas": []}
    tipo = "clave" if p["clave"] else "ctx"
    item = {"t": p["vis"], "s": p["s"], "e": p["e"], "w": round(ancho_em(p["vis"], tipo), 4)}
    L = actual["lineas"]
    if tipo == "ctx":
        if L and L[-1]["tipo"] == "ctx" and ancho_linea(L[-1]["p"] + [item], "ctx") <= MAX_CTX:
            L[-1]["p"].append(item)
        elif L and L[-1]["tipo"] == "ctx" and len(L) == 1:
            L.append({"tipo": "ctx", "p": [item]})  # no cabe: segunda línea de contexto en el mismo bloque
        elif L and L[-1]["tipo"] == "ctx":
            # tampoco cabe en la segunda línea: el bloque termina aquí y la palabra abre uno nuevo en el mismo sitio
            cerrar(); x, y, lado = G.POS.get(pos_key, (540, 1270, None))
            actual = {"_key": pos_key, "quien": p["quien"], "x": x, "y": y, "lado": lado, "lineas": [{"tipo": "ctx", "p": [item]}]}
        else:
            L.append({"tipo": "ctx", "p": [item]})
    else:
        if L and L[-1]["tipo"] == "clave": L[-1]["p"].append(item)
        else: L.append({"tipo": "clave", "p": [item]})
    if p["finClave"] or p.get("corte") or (p["fin"] and tipo == "ctx" and len(actual["lineas"][-1]["p"]) >= 2):
        cerrar()
cerrar()

# Reparto equilibrado de las dos líneas de contexto (evita una palabra suelta en la segunda línea)
for b in bloques:
    L = b["lineas"]
    if len(L) >= 2 and L[0]["tipo"] == "ctx" and L[1]["tipo"] == "ctx":
        ps = L[0]["p"] + L[1]["p"]
        mejor = None
        for k in range(1, len(ps)):
            w1, w2 = ancho_linea(ps[:k], "ctx"), ancho_linea(ps[k:], "ctx")
            if w1 <= MAX_CTX and w2 <= MAX_CTX:
                coste = abs(w1 - w2) + (0 if w1 >= w2 else 40)  # mejor la primera un poco más larga
                if mejor is None or coste < mejor[0]: mejor = (coste, k)
        if mejor:
            L[0]["p"], L[1]["p"] = ps[:mejor[1]], ps[mejor[1]:]

for i, b in enumerate(bloques):
    todas = [q for l in b["lineas"] for q in l["p"]]
    b["desde"] = round(todas[0]["s"] - 0.06, 3)
    fin = todas[-1]["e"]
    if i + 1 < len(bloques):
        sig = bloques[i + 1]["lineas"][0]["p"][0]["s"] - 0.06
        b["hasta"] = round(min(sig - 0.02, fin + 0.7) if sig - fin < 1.2 else fin + 0.6, 3)
    else:
        b["hasta"] = round(fin + 0.8, 3)
    for l in b["lineas"]:
        if l["tipo"] == "clave":
            w = ancho_linea(l["p"], "clave")
            if w > MAX_CLAVE: l["escala"] = round(MAX_CLAVE / w, 3)
    del b["_key"]

# Nada pisa la cara (corrección de la clienta): si el bloque choca con una cara detectada (scripts/caras.py), baja por debajo de la barbilla
ALTO = {"ctx": 0.95, "clave": 0.86}
p_caras = f"src/lote2/datos/{VID}_caras.json"
if os.path.exists(p_caras):
    caras = json.load(open(p_caras))["caras"]
    movidos = 0
    for b in bloques:
        w = max(ancho_linea(l["p"], l["tipo"]) * l.get("escala", 1) for l in b["lineas"]) + (80 if b.get("lado") else 0)
        h = sum(TAM[l["tipo"]] * l.get("escala", 1) * ALTO[l["tipo"]] for l in b["lineas"])
        x0, x1 = b["x"] - w / 2 - 20, b["x"] + w / 2 + 20
        def choca(y):
            y0, y1 = y - h / 2 - 14, y + h / 2 + 14
            return [c for t, cc in caras if b["desde"] - 0.1 <= t <= b["hasta"] + 0.1 for c in cc
                    if c[0] - 20 < x1 and c[0] + c[2] + 20 > x0 and c[1] - 20 < y1 and c[1] + c[3] + 24 > y0]
        cs = choca(b["y"])
        if cs:
            nuevo = max(c[1] + c[3] for c in cs) + 40 + h / 2
            b["y"] = round(min(nuevo, 1590 - h / 2)); movidos += 1
            if choca(b["y"]): print(f"  AVISO: el bloque de {b['desde']:.2f}s sigue tocando una cara")
    print(f"  caras: {movidos} bloques bajados para no tapar caras")

json.dump({"duracionS": round(TOTAL, 4),
           "segmentos": [{"i": s["i"], "clip": s["clip"], "enc": s["enc"], "editStart": round(s["editStart"], 4), "dur": round(s["dur"], 4),
                          "a": round(s["a"], 4)} for s in segs],
           "anclas": anclas, "bloques": bloques},
          open(f"src/lote2/datos/{VID}.json", "w"), ensure_ascii=False, indent=1)
print(f"{VID}: {TOTAL:.2f}s · {len(segs)} tomas · {len(palabras)} palabras · {len(bloques)} bloques")
for b in bloques:
    print(f"  {b['desde']:6.2f}-{b['hasta']:6.2f} {b['quien']} " + " | ".join(("**" if l["tipo"] == "clave" else "") + " ".join(q["t"] for q in l["p"]) for l in b["lineas"]))
