# Línea de tiempo del reel "Spray tan problems? We've got solutions!" (Slate).
# Tiempos de salida en segundos. El A-roll sale de edl_src.BLOCKS; los textos se anclan a las palabras de
# la transcripción (work/words.json) convertidas a tiempo de salida.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from engine import *
from edl_src import BLOCKS

SCR = os.path.dirname(PROJ)
DL = os.path.join(SCR, "dl")
BANK = os.path.join(DL, "bank")
SALON = os.path.join(DL, "broll2")
STOCK = os.path.join(SCR, "stock")

HOOK = 2.25           # duración del gancho inicial
TAIL = 0.7            # cierre después de la última palabra
CW, CH = 520, 325     # tamaño de las tarjetas
TW, TH = 448, 280     # tarjeta problema: más compacta para no tocar la cabeza
TOP = (540, 215)      # centro tarjeta problema (de y=75 a y=355)
BOT = (540, 1528)     # centro tarjeta solución
MID_Y = 1236          # centro del texto central (debajo del logo de la camiseta)

# ------------------------------------------------------------------ A-roll
ANCHOR = {"IMG_7103": (575, 400), "IMG_7106": (560, 380), "IMG_7108": (560, 400), "IMG_7110": (560, 390)}
spans = []      # dict(src, a, b, t0, t1)
phases = {}     # fase -> (t_inicio, t_fin, src)
t = HOOK
for bid, sp in BLOCKS:
    for (src, a, b, ph) in sp:
        d = dict(src=src, a=a, b=b, t0=t, t1=t + (b - a), block=bid, ph=[])
        for i, (ts, pid) in enumerate(ph):
            te = ph[i + 1][0] if i + 1 < len(ph) else b
            phases[pid] = (t + ts - a, t + te - a, src)
            d["ph"].append((t + ts - a, pid))
        spans.append(d)
        t += b - a
SPEECH_END = t
TOTAL = t + TAIL

def block_range(bid):
    ss = [s for s in spans if s["block"] == bid]
    return ss[0]["t0"], ss[-1]["t1"]

# palabras → tiempo de salida
_words = json.load(open(os.path.join(PROJ, "work", "words.json")))
def wt(src, word, near):
    """Tiempo de salida de la palabra `word` dicha cerca de `near` (segundos de la toma)."""
    best = None
    for s in _words[src + ".wav"]:
        for w in s["words"]:
            if w["w"].strip(" ,.?!").lower().startswith(word.lower()) and abs(w["s"] - near) < 1.2:
                if best is None or abs(w["s"] - near) < abs(best - near): best = w["s"]
    if best is None:
        raise KeyError(f"palabra no encontrada: {word} @ {near} en {src}")
    for s in spans:
        if s["src"] == src and s["a"] - 0.05 <= best <= s["b"]:
            return s["t0"] + max(best, s["a"]) - s["a"]
    raise KeyError(f"{word} @ {best} fuera de los tramos de {src}")

# Borde superior de la cabeza (mínimo medido por tramo, y en px a zoom 1). Si queda por encima de
# HEAD_MIN, el A-roll se baja lo justo para que la tarjeta de arriba nunca toque la cabeza ni la cara.
HEAD_TOP = {("IMG_7103", 1.62): 440, ("IMG_7103", 5.66): 452, ("IMG_7103", 11.36): 444, ("IMG_7103", 18.00): 420,
            ("IMG_7103", 34.02): 380, ("IMG_7103", 40.66): 342, ("IMG_7103", 57.04): 358, ("IMG_7106", 2.34): 354,
            ("IMG_7106", 4.76): 364, ("IMG_7106", 10.46): 370, ("IMG_7106", 29.25): 442, ("IMG_7108", 3.74): 442,
            ("IMG_7108", 7.74): 454, ("IMG_7110", 7.18): 388, ("IMG_7110", 13.84): 388, ("IMG_7110", 19.24): 378,
            ("IMG_7110", 22.93): 400}
HEAD_MIN = TOP[1] + TH / 2 + 32   # margen libre bajo la tarjeta

def shift_of(s):
    return max(0.0, HEAD_MIN - HEAD_TOP.get((s["src"], s["a"]), 999))

def zoom_at(tt):
    """Sin acercamientos que suban la cara: solo un 'pop' corto al entrar cada bloque, anclado arriba de la
    cabeza para que esta no se desplace hacia la tarjeta."""
    for s in spans:
        if s["t0"] <= tt < s["t1"] + 1e-6:
            b0, _ = block_range(s["block"])
            z = 1 + 0.06 * (1 - ease_out(prog(tt, b0, 0.32)))
            return s, z
    return spans[-1], 1.0

# ------------------------------------------------------------------ fuentes de las tarjetas
def V(path, start, fy=0.5, zoom=1.0, cx=0.5, speed=1.0):
    return ("video", path, start, fy, zoom, cx, speed)

def F(path, cx=0.5, cy=0.5, zoom=1.0):
    return ("photo", path, cx, cy, zoom)

def bank(n): return os.path.join(BANK, n)
def stock(n): return os.path.join(STOCK, n)
def salon(n): return os.path.join(SALON, n)

# ------------------------------------------------------------------ objetos animados
class Card:
    """Tarjeta B-roll. srcs: [(t_desde, fuente)], role 'top'|'bot'. Entra deslizando con rebote,
    sale encogiendo hacia fuera. Si lleva etiqueta, se oscurece la parte baja del contenido."""
    def __init__(self, role, t_in, t_out, srcs, label=None, pill_txt=None, pos=None, size=None, scrim=False):
        self.role, self.t_in, self.t_out, self.srcs = role, t_in, t_out, srcs
        self.pos = pos or (TOP if role == "top" else BOT)
        self.w, self.h = size or ((TW, TH) if role == "top" else (CW, CH))
        self.frame = CardFrame(self.w, self.h)
        self.label = label
        self.scrim = scrim or (label is not None)
        self.pill = None
        if pill_txt == "problem":
            self.pill = pill("PROBLEM", bg=(255, 252, 248), fg=(120, 74, 58), size=25, icon="x")
        elif pill_txt == "solution":
            self.pill = pill("SOLUTION", fg=(255, 255, 255), size=25, icon="check", grad=((196, 132, 86), (233, 182, 138)))
        self.readers = {}
        self.photos = {}

    def _content(self, t):
        cur = None
        for ts, src in self.srcs:
            if t >= ts - 1e-6: cur = (ts, src)
        if cur is None: cur = self.srcs[0]
        ts, src = cur
        k = (ts, src[1])
        # Ken Burns suave
        life = max(0.0, t - self.t_in) / max(0.5, self.t_out - self.t_in)
        kb = 1.0 + 0.06 * life
        cw, ch = int(self.w * 1.2), int(self.h * 1.2)
        if src[0] == "video":
            if k not in self.readers:
                _, path, st, fy, zoom, cx, speed = src
                start = st + max(0.0, max(t, ts) - max(self.t_in, ts)) * speed
                vf = (f"crop=iw/{zoom}:iw/{zoom}*{self.h}/{self.w}:(iw-iw/{zoom})*{cx}:(ih-iw/{zoom}*{self.h}/{self.w})*{fy},"
                      f"scale={cw}:{ch}:flags=lanczos" + (f",setpts=PTS/{speed}" if speed != 1.0 else ""))
                self.readers[k] = Reader(path, start, max(0.5, (self.t_out - t + 0.5) * speed), cw, ch, vf_extra=vf)
            img = self.readers[k].next()
        else:
            if k not in self.photos:
                _, path, pcx, pcy, zoom = src
                self.photos[k] = load_photo(path, cw, ch, pcx, pcy, zoom)
            img = self.photos[k]
        # recorte Ken Burns y escala al tamaño de la tarjeta
        z = 1.2 / kb
        sw, sh = int(self.w * z), int(self.h * z)
        x0, y0 = (cw - sw) // 2, (ch - sh) // 2
        c = cv2.resize(img[y0:y0 + sh, x0:x0 + sw], (self.w, self.h), interpolation=cv2.INTER_AREA)
        c = grade(c, LUT_BROLL, 1.04)
        if self.scrim:
            g = self._scrim()
            c = (c.astype(np.float32) * g).astype(np.uint8)
        return c

    _sc = None
    def _scrim(self):
        if self._sc is None:
            yy = np.linspace(0, 1, self.h)[:, None, None]
            self._sc = (1 - 0.62 * np.clip((yy - 0.3) / 0.7, 0, 1) ** 1.3).astype(np.float32)
        return self._sc

    def transform(self, t):
        """(dx, dy, escala, alfa, giro) de la tarjeta en t."""
        pin = prog(t, self.t_in, 0.42)
        side = 1 if self.role == "top" else -1
        dx = side * 640 * (1 - ease_back(pin, 1.25))
        rot = side * -7 * (1 - ease_out(pin))
        sc = 0.9 + 0.1 * ease_out(pin)
        al = ease_out(prog(t, self.t_in, 0.15))
        dy = 0
        if t > self.t_out:
            po = prog(t, self.t_out, 0.26)
            sc *= 1 - 0.25 * ease_in(po)
            al *= 1 - ease_in(po)
            dy = (-1 if self.role == "top" else 1) * 90 * ease_in(po)
        return dx, dy, sc, al, rot

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.27

    def draw(self, dst, t):
        if not self.active(t):
            if t >= self.t_out + 0.27 and self.readers:
                for r in self.readers.values(): r.close()
                self.readers = {}
            return
        dx, dy, sc, al, rot = self.transform(t)
        cx, cy = self.pos[0] + dx, self.pos[1] + dy
        draw_card(dst, self.frame, self._content(t), cx, cy, sc, al, rot)
        if self.pill is not None:
            pp = prog(t, self.t_in + 0.22, 0.3)
            if pp > 0:
                px = cx - self.w / 2 * sc + self.pill.w / 2 - 6
                py = cy - self.h / 2 * sc - 2
                draw_sprite(dst, self.pill, px, py, (0.4 + 0.6 * ease_back(pp, 2.0)) * sc, al * ease_out(pp))
        if self.label is not None:
            for lb in self.label:
                lb.cx_off = 0
                lb.draw(dst, t, dx, dy, al)

class Label:
    """TextBlock pegado a una tarjeta (se mueve con ella al salir)."""
    def __init__(self, lines, cx, cy, t_out, line_gap=-0.06):
        self.tb = TextBlock(lines, cx, cy, t_out, line_gap=line_gap, anchor="bottom")
        self.t_out = t_out

    def draw(self, dst, t, dx=0, dy=0, al=1.0):
        if dx == 0 and dy == 0:
            self.tb.draw(dst, t); return
        # desplazar: dibujar en coordenadas desplazadas
        for w, sp, x, y in self.tb.items:
            if t < w.t: continue
            p = prog(t, w.t, 0.26)
            sc = 0.55 + 0.45 * ease_back(p, 2.2)
            a = ease_out(prog(t, w.t, 0.12)) * al
            if t > self.t_out: a *= 1 - ease_in(prog(t, self.t_out, 0.22))
            draw_sprite(dst, sp, x + dx, y + dy + 18 * (1 - ease_out(p)), sc, a)

class Mid:
    """Texto central (preguntas y cierre)."""
    def __init__(self, lines, t_out, cy=MID_Y, line_gap=-0.14):
        self.tb = TextBlock(lines, 540, cy, t_out, line_gap=line_gap)

    def draw(self, dst, t):
        self.tb.draw(dst, t)

class Stars:
    def __init__(self, pts, t0, spread=0.12, dur=0.95):
        self.tw = [Twinkle(STAR, x, y, t0 + i * spread, dur, s, rot) for i, (x, y, s, rot) in enumerate(pts)]

    def draw(self, dst, t):
        for tw in self.tw: tw.draw(dst, t)

STAR = star_sprite(56)

# ------------------------------------------------------------------ construcción
layers = []
sfx = []      # (t, nombre, ganancia dB)

def label_lines(*rows):
    return [[Word(txt, sty, tt) for (txt, sty, tt) in row] for row in rows]

def problem_solution(bid, qsrc, q_words, top_srcs, a_srcs, a_labels, star_pts=None, q_gap=-0.14):
    """q_words: líneas de (texto, estilo, palabra_ancla, segundo_aprox) para el texto central.
    a_labels: lista de (t_out_rel|None, líneas) para la etiqueta de la tarjeta de solución."""
    b0, b1 = block_range(bid)
    qid = "Q" + bid[1]; aid = "A" + bid[1]
    tq0, tq1, _ = phases[qid]
    ta0, ta1, asrc = phases[aid]
    out = b1 - 0.24
    # texto central (pregunta)
    lines = [[Word(txt, sty, wt(qsrc, anc, near)) for (txt, sty, anc, near) in row] for row in q_words]
    layers.append(Mid(lines, out, line_gap=q_gap))
    # tarjeta problema
    tsr = [(b0 + 0.02 if i == 0 else wt(qsrc, *ts), s) for i, (ts, s) in enumerate(top_srcs)]
    layers.append(Card("top", b0 + 0.02, out, tsr, pill_txt="problem"))
    sfx.append((b0 + 0.04, "pop", -15))
    # tarjeta solución + etiqueta
    t_bot = ta0 + 0.05
    asr = [(t_bot if i == 0 else wt(asrc, *ts), s) for i, (ts, s) in enumerate(a_srcs)]
    labs = []
    for j, (lab_until, rows) in enumerate(a_labels):
        rows_t = [[(txt, sty, wt(asrc, anc, near)) for (txt, sty, anc, near) in row] for row in rows]
        until = out if lab_until is None else wt(asrc, *lab_until) - 0.12
        labs.append(Label(label_lines(*rows_t), BOT[0], BOT[1] + CH / 2 - 24, until, line_gap=-0.02))
    layers.append(Card("bot", t_bot, out, asr, label=labs, pill_txt="solution"))
    sfx.append((t_bot + 0.02, "swish", -17))
    # brillo en la palabra grande de la primera etiqueta
    first_big = min(w.t for lb in labs[:1] for w, *_ in lb.tb.items if w.style == "a_big")
    sfx.append((first_big, "chime", -21))
    pts = star_pts or [(BOT[0] + 238, BOT[1] - 150, 0.75, 20), (BOT[0] - 250, BOT[1] + 132, 0.5, -15), (BOT[0] + 215, BOT[1] + 120, 0.42, 30)]
    layers.append(Stars(pts, first_big - 0.05))
    # salida del bloque
    sfx.append((out - 0.04, "whoosh", -19))

S, B = "q_small", "q_big"
AS, AB = "a_small", "a_big"

# --- Gancho ---------------------------------------------------------------------------------------
class Hook:
    def __init__(self):
        self.r = None
        self.t1 = HOOK
        self.lines1 = TextBlock([[Word("SPRAY TAN", "hook_caps", 0.0)], [Word("Problems?", "hook_big", 0.18)]], 540, 1060, HOOK - 0.18, line_gap=-0.1)
        self.lines2 = TextBlock([[Word("WE'VE GOT", "hook_caps", 0.85)], [Word("Solutions!", "hook_tan", 1.05)]], 540, 1420, HOOK - 0.18, line_gap=-0.1)
        self.stars = Stars([(880, 1330, 0.9, 25), (205, 1520, 0.6, -20), (850, 1570, 0.5, 35), (230, 980, 0.55, 15)], 1.05, 0.1, 1.0)
        vig = np.ones((H, W, 1), np.float32)
        yy = np.linspace(0, 1, H)[:, None, None]
        vig = (0.6 + 0.4 * np.clip(np.abs(yy - 0.64) * 2.4, 0, 1) ** 1.5) * vig  # oscurece el centro para el texto
        self.vig = vig

    def draw_base(self, t):
        if self.r is None:
            self.r = Reader(bank("st3_204_Videos_Proceso.mp4"), 0.4, HOOK + 0.6, W, H,
                            vf_extra=f"scale={W}:-2:flags=lanczos,crop={W}:{H}:0:(ih-{H})/2")
        img = grade(self.r.next(), LUT_BROLL, 1.05)
        z = 1.0 + 0.05 * (t / HOOK)
        M = cv2.getRotationMatrix2D((540, 900), 0, z)
        img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        return (img.astype(np.float32) * self.vig).astype(np.uint8)

    def draw(self, dst, t):
        if t >= HOOK + 0.3: return
        self.lines1.draw(dst, t); self.lines2.draw(dst, t); self.stars.draw(dst, t)

HOOK_L = Hook()
layers.append(HOOK_L)
sfx += [(0.0, "pop", -13), (0.18, "pop_hi", -15), (0.84, "swish", -18), (1.05, "sparkle", -17), (HOOK - 0.22, "whoosh", -16)]

# --- P1 Pale or dull skin → A custom spray tan ----------------------------------------------------
problem_solution("P1", "IMG_7103",
    [[("Pale", S, "Pale", 1.74), ("or", S, "or", 1.98)], [("dull", B, "dull", 2.28), ("skin", B, "skin", 2.56)]],
    [(None, F(bank("st3_271_Fotos_Antes_Cámara.jpg"), 0.5, 0.40, 1.15))],
    [(None, V(bank("st1_002_spraytan1-Brol.mov"), 1.0, 0.52, 1.1))],
    [(None, [[("A custom", AS, "custom", 3.40)], [("spray tan", AB, "spray", 3.68)]])])

# --- P2 Need color ASAP → Rapid tan ---------------------------------------------------------------
problem_solution("P2", "IMG_7103",
    [[("Need", S, "Need", 5.78), ("color", S, "color", 6.08)], [("ASAP?", B, "ASAP", 6.60)]],
    [(None, F(stock("ASAP_3_dhZtNlvNE8M.jpg"), 0.5, 0.52, 2.0))],
    [(None, V(bank("st3_200_Videos_Proceso.mp4"), 1.5, 0.42, 1.0))],
    [(None, [[("Rapid tan", AB, "rapid", 7.98)], [("formula, just for that", AS, "formula", 8.28)]])])

# --- P3 Dry or patchy skin → Exfoliate 24 h before ------------------------------------------------
problem_solution("P3", "IMG_7103",
    [[("Dry", S, "Dry", 11.44), ("or", S, "or", 12.00)], [("patchy", B, "patch", 12.32), ("skin", B, "skin", 12.70)]],
    [(None, F(stock("dry_1_tWTFjznQlBA.jpg"), 0.5, 0.5, 1.1))],
    [(None, F(stock("exfoliate_1_LB_OWger9XE.jpg"), 0.5, 0.42, 1.0))],
    [(None, [[("Exfoliate", AB, "Exfoliate", 18.14)], [("24 hrs before your appointment", AS, "24", 18.86)]])])

# --- P4 Tan fading unevenly → Moisturize daily -----------------------------------------------------
problem_solution("P4", "IMG_7103",
    [[("Tan", S, "Tan", 34.16), ("fading", S, "fading", 34.34)], [("unevenly", B, "unevenly", 34.82)]],
    [(None, F(stock("fading_1_ggYiBc5QLbM.jpg"), 0.38, 0.60, 1.5))],
    [(None, F(stock("moisturize_1_EM9VdLxwqPs.jpg"), 0.5, 0.5, 1.0))],
    [(None, [[("Moisturize", AB, "Moisturize", 36.14)], [("daily", AS, "daily", 36.62)]])])

# --- P5 Tan sticking to hands & feet → barrier cream in the room ----------------------------------
problem_solution("P5", "IMG_7103",
    [[("Tan", S, "Tan", 40.96), ("sticking to", S, "sticking", 41.04)], [("hands", B, "hands", 42.08), ("&", B, "and", 42.34), ("feet", B, "feet", 42.66)]],
    [(None, F(stock("hands_feet_1_KZKpDrJ3_lk.jpg"), 0.5, 0.5, 1.0)),
     (("feet", 42.66), F(stock("hands_feet_2_oy8LFbcB8hQ.jpg"), 0.5, 0.5, 1.0))],
    [(None, V(bank("st2_110_Videos_Consultaantesd.mov"), 19.0, 0.42, 1.55, 0.12))],
    [(None, [[("Barrier cream", AB, "barrier", 57.82)], [("in the room, before", AS, "in", 58.58)], [("your appointment", AS, "appointment", 60.26)]])])

# --- P6 Going on vacation → Book 1–2 days before ---------------------------------------------------
problem_solution("P6", "IMG_7106",
    [[("Going on", S, "Going", 2.42)], [("vacation", B, "vacation", 3.18)]],
    [(None, F(stock("vacation_1_Nl-SXO4FAHw.jpg"), 0.5, 0.5, 1.0))],
    [(None, F(stock("calendar_1_cdDDWLezAJ0.jpg"), 0.5, 0.5, 1.0))],
    [(None, [[("Book your tan", AB, "Book", 4.88)], [("1–2 days before your trip", AS, "one", 5.82)]])])

# --- P7 Wedding or special event → book ahead + proper prep + custom shade -------------------------
problem_solution("P7", "IMG_7106",
    [[("Wedding", B, "Wedding", 10.58)], [("or special event", S, "or", 11.14)]],
    [(None, F(stock("wedding_1_-BPwR5_GSe0.jpg"), 0.5, 0.45, 1.0))],
    [(None, V(bank("st2_112_Videos_Llegadaalsalón.mov"), 0.8, 0.40, 1.0)),
     (("follow", 33.02), F(stock("exfoliate_3_3i9wHKQ-63M.jpg"), 0.5, 0.5, 1.0)),
     (("custom", 36.34), V(bank("st2_097_Videos_Proceso.mov"), 1.0, 0.36, 1.0))],
    [(("follow", 33.02), [[("Book", AS, "book", 30.12)], [("1–2 days before", AB, "one", 30.86)]]),
     (None, [[("Proper prep", AB, "prep", 33.58)], [("+ custom shade", AS, "custom", 36.34)]])],
    )

# --- P8 Not sure which shade → personalized consultation ------------------------------------------
problem_solution("P8", "IMG_7108",
    [[("Not sure which", S, "Not", 3.80)], [("shade", B, "shade", 5.16), ("or", S, "or", 5.50), ("solution?", B, "solution", 5.70)]],
    [(None, F(stock("unsure_1_-wjk_SSqCE4.jpg"), 0.5, 0.4, 1.0))],
    [(None, V(bank("st2_109_Videos_Consultaantesd.mov"), 24.0, 0.43, 1.0))],
    [(None, [[("Personalized", AB, "personalized", 8.98)], [("spray tan consultation", AS, "spray", 9.56)]])])

# --- Cierre ---------------------------------------------------------------------------------------
c0, c1 = block_range("CL")
CS, CB, CT = "c_small", "c_big", "c_tan"
def cap(rows, t_out, cy=MID_Y):
    layers.append(Mid([[Word(txt, sty, wt("IMG_7110", anc, near)) for (txt, sty, anc, near) in row] for row in rows], t_out, cy))
# Every skin tone, undertone, and glow goal is different.
t_u = wt("IMG_7110", "undertone", 8.28); t_g = wt("IMG_7110", "and", 9.22); t_d = wt("IMG_7110", "is", 9.88)
t_c1end = phases["C1"][1]
cap([[("Every", CS, "Every", 7.24)], [("skin tone", CB, "skin", 7.52)]], t_u - 0.24)
cap([[("undertone", CB, "undertone", 8.28)]], t_g - 0.24)
cap([[("& glow goal", CT, "glow", 9.26)]], t_d - 0.22)
cap([[("is", CS, "is", 9.88)], [("different", CB, "different", 10.12)]], t_c1end - 0.22)
layers.append(Card("top", c0 + 0.02, t_c1end - 0.05,
    [(c0 + 0.02, F(stock("glow_3_VrW_EgqwOUo.jpg"), 0.5, 0.45, 1.0)),
     (t_u, V(bank("st3_207_Videos_Después.mov"), 0.6, 0.33, 1.0)),
     (t_g, V(bank("st1_007_spraytan1-Brol.mov"), 1.0, 0.36, 1.0))]))
sfx += [(c0 + 0.04, "pop", -15), (t_g + 0.05, "sparkle", -20)]
layers.append(Stars([(TOP[0] + TW / 2 + 2, TOP[1] - TH / 2 + 22, 0.7, 20), (TOP[0] - TW / 2 - 2, TOP[1] + 30, 0.5, -10)], t_g))
# Your spray tan should be too.
t_c2 = phases["C2"]
cap([[("Your spray tan", CS, "Your", 13.88)], [("should be too", CT, "should", 14.54)]], t_c2[1] - 0.2)
layers.append(Card("top", t_c2[0] + 0.02, t_c2[1] - 0.1, [(t_c2[0], V(bank("st3_206_Videos_Después.mov"), 1.6, 0.30, 1.0))]))
sfx += [(t_c2[0] + 0.03, "swish", -18), (wt("IMG_7110", "should", 14.54), "chime", -22)]
# If you relate to any of this,
t_c3 = phases["C3"]
cap([[("If you", CS, "If", 19.32)], [("relate", CB, "relate", 19.98)], [("to any of this", CS, "to", 20.32)]], t_c3[1] - 0.26)
sfx += [(wt("IMG_7110", "relate", 19.98), "pop_hi", -20)]
# come see us at Slate and we'll find the perfect tan for you.
t_c4 = phases["C4"]
t_and = wt("IMG_7110", "and", 24.04)
cap([[("come see us at", CS, "Come", 22.98)], [("Slate", CB, "Slate", 23.92)]], t_and - 0.24)
cap([[("& we'll find the", CS, "and", 24.04)], [("perfect tan", CT, "perfect", 24.84)], [("for you", CS, "for", 25.44)]], TOTAL - 0.05)
layers.append(Card("top", t_c4[0] + 0.02, TOTAL + 1,
    [(t_c4[0], V(salon("IMG_0822.MOV"), 0.5, 0.15, 1.0)),
     (t_and, V(salon("IMG_0816.MOV"), 0.0, 0.40, 1.0, speed=0.62))]))
sfx += [(t_c4[0] + 0.03, "pop", -15), (wt("IMG_7110", "Slate", 23.92), "sparkle", -18), (wt("IMG_7110", "perfect", 24.84), "chime", -21), (SPEECH_END + 0.15, "ding", -19)]
layers.append(Stars([(TOP[0] + TW / 2 + 2, TOP[1] - TH / 2 + 22, 0.75, 20), (TOP[0] - TW / 2 - 2, TOP[1] + 30, 0.55, -15), (790, MID_Y + 120, 0.5, 25)], wt("IMG_7110", "Slate", 23.92)))
layers.append(Stars([(270, MID_Y - 40, 0.6, -20), (820, MID_Y + 60, 0.7, 25), (540, MID_Y - 150, 0.45, 10)], SPEECH_END + 0.1, 0.1, 1.1))

if __name__ == "__main__":
    print("TOTAL", round(TOTAL, 2), "speech_end", round(SPEECH_END, 2))
    for k, v in sorted(phases.items(), key=lambda kv: kv[1][0]):
        print(k, round(v[0], 2), round(v[1], 2), v[2])
    print(len(layers), "capas", len(sfx), "efectos")
