"""The edit: every shot of the Kiowa Creek (lost locomotive) video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx9 as G9
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1061.59
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
BLUE = (110, 170, 220)
GREY_ = (160, 160, 160)
IMG = os.path.join(ROOT, "assets", "img")
VIDDIR = os.path.join(ROOT, "assets", "vid")

GARDNER = "Alexander Gardner, 1867 · Boston Public Library (CC BY 2.0)"
LOC_ = "Library of Congress"


def w(word, near, window=8.0):
    try:
        return words.at(word, near, window)
    except KeyError:
        print(f"[anchor] {word!r} not found near {near}; using {near}", file=sys.stderr)
        return near


# ------------------------------------------------------------------ helpers
def _key(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("l", "i").replace("1", "i").replace("o", "0"))


_FILES = {}


def res(path):
    """Unsplash ids read off contact sheets can confuse I/l/1 and O/0: map to the file on disk."""
    if os.path.exists(os.path.join(IMG, path)) or not path.startswith("u_"):
        return path
    if not _FILES:
        for f in os.listdir(IMG):
            if f.startswith("u_"):
                _FILES[_key(f)] = f
    return _FILES.get(_key(path), path)


def pick(primary, fallback):
    return primary if os.path.exists(os.path.join(IMG, res(primary))) else fallback


def kb(path, m="in", g="doc", z=1.0, **kw):
    cams = {
        "in": ((0.5, 0.5, z), (0.5, 0.5, z * 1.16)),
        "out": ((0.5, 0.5, z * 1.16), (0.5, 0.5, z)),
        "l": ((0.38, 0.5, z * 1.15), (0.62, 0.5, z * 1.15)),
        "r": ((0.62, 0.5, z * 1.15), (0.38, 0.5, z * 1.15)),
        "up": ((0.5, 0.62, z * 1.15), (0.5, 0.38, z * 1.15)),
        "down": ((0.5, 0.38, z * 1.15), (0.5, 0.62, z * 1.15)),
        "punch": ((0.5, 0.5, z * 1.05), (0.5, 0.5, z * 1.35)),
    }
    c0, c1 = kw.pop("cam0", None), kw.pop("cam1", None)
    if c0 is None:
        c0, c1 = cams[m]
    return Still(res(path), c0, c1, grade=g, **kw)


def fr(path, cap=None, g="archival", **kw):
    return Framed(res(path), cap, grade=g, **kw)


def L(lid, fallback, cap=None, g="archival"):
    """Library of Congress picture (framed) if downloaded, else the fallback base."""
    f = f"l_{lid}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, g)
    return fallback


def has(f):
    return os.path.exists(os.path.join(IMG, f))


USED_VID = set()


def V(vid, fallback, start=0.0, g="doc", z0=1.0, z1=1.08, speed=1.0, m="in"):
    """Mixkit clip if its licence allowed the download, else a Ken Burns still."""
    f = f"mk_{vid}.mp4"
    if os.path.exists(os.path.join(VIDDIR, f)):
        USED_VID.add(vid)
        return Video(f, start, speed, g, z0, z1)
    return kb(fallback, m, g)


def cus(fn, **kw):
    return Custom(fn, **kw)


def warp(fn, a, b, **kw):
    return Custom(lambda t, d: fn(a + b * t, d, **kw))


def chapter(num, title, bg, g="dark", year=None, base=None):
    ovs = [Darken(0.5, 0.0, 0.3),
           BigText(f"CAPÍTULO {num}" + (f"  ·  {year}" if year else ""), "bebas", 46, YELLOW, (0.5, 0.40), 0.1, None, "up", tracking=6),
           BigText(title, "serif", 92, WHITE, (0.5, 0.52), 0.25, None, "up"),
           FnOverlay(_underline, y=0.62, t0=0.5)]
    return (base or kb(bg, "in", g)), ovs


def _underline(img, t, dur, y=0.62, t0=0.5, wmax=560):
    k = ease_out(prog(t, t0, 0.6)) * (1 - prog(t, dur - 0.3, 0.3))
    if k > 0:
        x0 = int(960 - wmax * k)
        cv2.rectangle(img, (x0, int(1080 * y)), (int(960 + wmax * k), int(1080 * y) + 8), YELLOW, -1)


def question(lines, hl, y=0.5, size=72):
    out, t = [], 0.15
    for wd in lines.split():
        st_ = "h" if wd.strip("¿?,.").lower() in hl else "n"
        out.append((wd, t, st_))
        t += 0.11
    return [Rich(out, 0.5, y, 0.72, size)]


def rich(text, hl=(), t0=0.15, step=0.12, y=0.5, size=62, maxw=0.7, red=()):
    out, t = [], t0
    for wd in text.split():
        k = wd.strip("¿?,.:«»…").lower()
        out.append((wd, t, "h" if k in hl else ("r" if k in red else "n")))
        t += step
    return Rich(out, 0.5, y, maxw, size)


def big(text, t0=0.2, y=0.82, size=66, col=WHITE, anim="up", t1=None):
    return BigText(text, "bebas", size, col, (0.5, y), t0, t1, anim, tracking=4)


def torch(path=((0.3, 0.55), (0.7, 0.45)), r=440, t0=0.0, amb=0.13):
    return FnOverlay(G5.flashlight, path=path, r=r, t0=t0, amb=amb)


def postshake(amt):
    def f(img, t, dur):
        return G2.shake_frame(img, t, amt)
    return f


def mp(name, cams, layers, title=None):
    return M.MapScene(name, cams, layers, title)


def card(lines, base="dark_grid"):
    """Typographic card on a dark background: lines = [(text, size, color, y, t0)]."""
    return Solid(base), [BigText(tx, "bebas", sz, col, (0.5, y), t0, None, "up", tracking=4) for tx, sz, col, y, t0 in lines]


# ------------------------------------------------------------------ Kiowa Creek specifics
KP = ["kansas_city", "lawrence", "topeka", "manhattan_ks", "junction_city", "abilene", "salina", "ellsworth", "hays", "ellis",
      "wakeeney", "oakley", "sharon_springs", "cheyenne_wells", "kit_carson", "hugo", "limon", "agate", "deer_trail", "byers",
      "strasburg", "bennett", "denver"]
KP_EAST = KP[:KP.index("strasburg") + 1]          # built from Kansas City westward
KP_WEST = ["denver", "bennett", "strasburg"]       # the second crew, from Denver eastward
COAST = ["nyc", "chicago", "kansas_city", "denver", "cheyenne", "ogden", "reno", "sacramento", "sf"]
CREEK = M.kc_creek_ll()
TOW = ["kc_cross"] + KP[::-1][2:]                  # Kiowa Creek back to Kansas City (west to east)


def kp_layers(t0=0.0, draw=6.0, col=YELLOW):
    return [dict(type="state", name="Kansas", t0=t0, color=GREY_, width=3, alpha=0.6),
            dict(type="state", name="Colorado", t0=t0, color=GREY_, width=3, alpha=0.6),
            dict(type="rail", path=KP, t0=t0 + 0.2, draw=draw, color=col, width=6)]


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="u_F8Iyt407ApM.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Por qué tanta gente persiguió durante más de un siglo una locomotora que nadie lograba encontrar?",
                     ("siglo", "nadie"), size=64), tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_57muzgYYtFQ.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Y dónde estaba de verdad?", ("verdad?",), size=90), tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 63.3)
    add(0.0, kb("u_bhGuqye5Uwc.jpg", "in", "dark"), [rich("IMAGINA PERDER UNA LOCOMOTORA", ("locomotora",), 0.2, y=0.84, size=64)], tex=DARK)
    add(w("no", 2.1), kb("u_zMS-RWqHhek.jpg", "punch", "bw"), [big("NI UN TORNILLO", 0.0, 0.84, 84, WHITE, "pop")], tex=DARK)
    add(w("ni", 2.8), kb("u_26ldqVyJ9Kw.jpg", "punch", "dark"), [big("NI UNA RUEDA", 0.0, 0.84, 84, WHITE, "pop")], tex=DARK)
    add(w("una máquina", 3.86), fr("f_54522621773.jpg", "Una locomotora americana de la época · imagen de referencia", "bw"),
        [big("HIERRO · TAN GRANDE COMO UN CAMIÓN", 0.5, 0.1, 58, YELLOW)], tex=ARCH)
    add(6.40, mp("kc_us", [(0, -98.0, 38.5, 0.75), (3.0, -104.4, 39.75, 1.25)],
                 [dict(type="state", name="Colorado", t0=0.3, color=YELLOW, width=4, alpha=0.9),
                  dict(type="pin", at="kc_cross", t0=1.2, label="LLANURAS DE COLORADO", side="r", box=True, size=50)]),
        [Badge("MAYO DE 1878", 0.3, None)], tr="zoom", td=0.3, tex=GFX)
    add(w("un ferrocarril", 9.6), kb("u_2tfQcOodk60.jpg", "in", "doc"), [big("UN FERROCARRIL PERDIÓ UNA", 0.2, 0.84, 70)], tex=CLEAN)
    add(11.90, kb("u_FNZwttoLRSU.jpg", "punch", "doc"), [big("CAYÓ A UN ARROYO EN PLENA CRECIDA", 0.2, 0.84, 66, YELLOW)], tex=CLEAN)
    add(w("y cuando", 14.5), kb("w_kiowa_creek.jpg", "out", "doc"),
        [Stamp("YA NO ESTABA", w("ya", 16.0) - w("y cuando", 14.5), RED, (0.5, 0.5), -8, 120)], tex=CLEAN)
    add(17.20, cus(G9.crossing, mode="recover", t0=0.4, tender_t=w("tender", 20.6) - 17.2, temp_t=99,
                   no_t=w("locomotora", 24.0) - 17.2), tr="fade", td=0.25, tex=GFX)
    add(25.20, cus(G9.crossing, mode="search", t0=0.0, pit_t=0.1, dig_d=2.4),
        [Stamp("NI UN TROZO", w("ni", 29.6) - 25.2, RED, (0.3, 0.32), -8, 100)], tr="fade", td=0.25, tex=GFX)
    add(30.90, kb("u_aG8iIT9_iqM.jpg", "in", "bw"), [Counter(0, 111, "{:.0f}", "AÑOS BUSCÁNDOLA", 0.2, 1.4, (0.5, 0.45), 220)], tex=DARK)
    add(w("ferroviarios", 33.6), L("1s00072", kb("u_YZbKblJ1_I0.jpg", "in", "bw")), [big("FERROVIARIOS", 0.0, 0.84, 84, YELLOW, "pop")], tex=ARCH)
    add(w("curiosos", 34.5), kb("u_F8Iyt407ApM.jpg", "in", "cold"), [big("CURIOSOS", 0.0, 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(w("hasta", 35.0), kb("u_kJTo5r1NuSE.jpg", "punch", "warm"), [big("Y HASTA UN NOVELISTA FAMOSO", 0.0, 0.84, 70, YELLOW, "pop")], tex=CLEAN)
    add(36.60, kb("u_zjrL-buRjD0.jpg", "in", "cold"), [Badge("1989", 0.2, None), Counter(0, 300, "+{:.0f}", "PERSONAS", 0.4, 1.6, (0.5, 0.45), 200)],
        tr="flash", td=0.2, tex=CLEAN)
    add(w("con detectores", 40.4), kb("u_brsP25BuajE.jpg", "in", "warm"), [big("DETECTORES · RADARES", 0.2, 0.84, 84, WHITE, "pop")], tex=CLEAN)
    add(w("y la ayuda", 42.2), kb("u_HsqBGASgXJA.jpg", "in", "doc"), [big("Y UN SATÉLITE DEL GOBIERNO", 0.1, 0.84, 70, YELLOW)], tex=CLEAN)
    add(44.10, Solid("black"), [big("NUNCA DIERON CON ELLA", 0.1, 0.5, 110, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(45.60, kb("w_kiowa_creek.jpg", "in", "dark"),
        [Darken(0.45), BigText("LA LOCOMOTORA PERDIDA", "serif", 104, WHITE, (0.5, 0.44), 0.3, None, "up"),
         BigText("DE KIOWA CREEK", "bebas", 92, YELLOW, (0.5, 0.58), 0.9, None, "up", tracking=10)], tr="fade", td=0.4, tex=DARK)
    add(49.40, kb("u_aT88kga0g_M.jpg", "in", "dark"), [rich("LA RESPUESTA ESTUVO AL ALCANCE DE CUALQUIERA", ("cualquiera",), 0.2, step=0.1, y=0.84, size=56,
                                                          maxw=0.85)], tex=DARK)
    add(w("solo", 52.6), kb("u_2jPwtG5cZOA.jpg", "in", "doc"), [big("NADIE LA BUSCÓ DONDE ESTABA", 0.1, 0.84, 72, YELLOW)], tex=CLEAN)
    q1(55.30)
    q2(61.10)

    # ============================== CAP 1: EL FERROCARRIL QUE LLEGÓ A DENVER (63.3 - 203.7)
    bg, ov = chapter(1, "EL FERROCARRIL QUE LLEGÓ A DENVER", "u_2tfQcOodk60.jpg", year="1869–1876")
    add(63.30, bg, ov, tr="black", td=0.2, tex=DARK)
    add(68.00, mp("kc_us", [(0, -98.0, 39.0, 0.8), (3.5, -104.99, 39.74, 1.5)],
                  [dict(type="state", name="Colorado", t0=0.2, color=GREY_, width=3, alpha=0.7),
                   dict(type="pin", at="denver", t0=0.8, label="DENVER", side="r", box=True, size=56)]),
        [Badge("AÑOS 1860", 0.3, None)], tr="zoom", td=0.3, tex=GFX)
    add(w("de mineros", 71.6), fr("f_5199798142.jpg", "Diligencia hacia Denver desde Hays City, Kansas · " + GARDNER),
        [big("MINEROS Y COMERCIANTES", 0.2, 0.08, 60, YELLOW)], tex=ARCH)
    add(w("en mitad", 73.6), fr("f_5199203669.jpg", "Las grandes llanuras de Kansas · " + GARDNER), [big("EN MITAD DE NINGUNA PARTE", 0.2, 0.08, 60)], tex=ARCH)
    add(75.20, kb("u_YZbKblJ1_I0.jpg", "in", "bw"), [big("LE FALTABA…", 0.2, 0.84, 70), big("EL TREN", w("tren", 78.9) - 75.2, 0.5, 160, YELLOW, "pop")],
        tex=ARCH)
    add(79.70, fr("f_5199203755.jpg", "Tendido de vía a 300 millas del Misuri, 19 de octubre de 1867 · " + GARDNER),
        [BigText("KANSAS PACIFIC", "serif", 96, WHITE, (0.5, 0.1), w("kansas", 82.0) - 79.7, None, "up")], tex=ARCH)
    add(82.70, L("1s00006", fr("f_5199796564.jpg", "Kansas City, en la frontera de Kansas y Misuri · " + GARDNER),
                 "Oficina de la Union Pacific Railway, División Este · Wyandotte, Kansas, 1867 · " + LOC_),
        [big("AL PRINCIPIO NI SIQUIERA SE LLAMABA ASÍ", 0.2, 0.08, 56)], tex=ARCH)
    bg, ov = card([("NACIÓ COMO UNA RAMA DE LA", 50, GREY_, 0.28, 0.1), ("UNION PACIFIC", 120, WHITE, 0.43, 0.3),
                   ("1869: KANSAS PACIFIC", 120, YELLOW, 0.65, w("1869", 89.0) - 85.5)])
    add(85.50, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(90.80, fr("f_5199201941.jpg", "El Misuri en Kansas City · " + GARDNER), [Badge("KANSAS CITY", 0.2, None)], tex=ARCH)
    add(w("y avanzaba", 93.6), mp("kc_reg", [(0, -95.5, 39.0, 0.9), (5.0, -100.5, 39.0, 0.78)],
                                   [dict(type="state", name="Kansas", t0=0.0, color=GREY_, width=3, alpha=0.6),
                                    dict(type="rail", path=KP_EAST, t0=0.2, draw=6.5, color=YELLOW, width=6),
                                    dict(type="pin", at="kansas_city", t0=0.1, label="KANSAS CITY", side="r", box=True, size=40),
                                    dict(type="label", at="salina", text="PRADERAS DE KANSAS", t0=1.6, dy=-90, size=48)]),
        tr="zoom", td=0.3, tex=GFX)
    add(97.40, L("1s00072", fr("f_5199203919.jpg", "Campamento de ingenieros en Kansas · " + GARDNER), "Tren de obras al oeste de Fort Hays · 1867 · " + LOC_),
        [big("CUADRILLAS QUE VIVÍAN AL LADO DE LA VÍA", 0.3, 0.08, 54)], tex=ARCH)
    add(101.20, fr("f_5199203755.jpg", "Tendido de vía, octubre de 1867 · " + GARDNER, zoom=(1.08, 1.22)),
        [big("KILÓMETRO A KILÓMETRO", 0.2, 0.08, 64, YELLOW)], tex=ARCH)
    add(w("sobre", 104.0), V("49780", "u_149vt6evNQQ.jpg", 0.0, "doc"), [big("UNA LLANURA QUE NO SE ACABA", 0.2, 0.84, 66)], tex=CLEAN)
    add(106.30, kb("u_kkopeY-zE28.jpg", "in", "doc"), [big("CAZADORES DE BISONTES", w("cazadores", 109.0) - 106.3, 0.84, 72, YELLOW)], tex=CLEAN)
    add(110.90, kb("u_hYpesag8gBg.jpg", "in", "warm"), [Darken(0.35), BigText("«BUFFALO BILL»", "serif", 120, WHITE, (0.5, 0.5), w("búfalo", 114.8) - 110.9, None, "pop"),
                                                        big("EL APODO LE QUEDÓ PARA SIEMPRE", 0.3, 0.84, 54, GREY_)], tex=CLEAN)
    add(116.60, mp("kc_reg", [(0, -100.0, 39.0, 0.8), (4.0, -103.4, 39.4, 1.3), (8.5, -104.0, 39.6, 1.8)],
                   [dict(type="state", name="Colorado", t0=0.0, color=GREY_, width=3, alpha=0.6),
                    dict(type="rail", path=KP_EAST[:KP_EAST.index("hugo") + 1], t0=0.0, draw=0.1, color=YELLOW, width=6),
                    dict(type="rail", path=["hugo", "limon", "agate", "deer_trail", "byers", "strasburg"], t0=w("las dos", 123.2) - 116.6,
                         draw=3.0, color=YELLOW, width=6),
                    dict(type="rail", path=KP_WEST, t0=w("desde", 120.6) - 116.6, draw=4.5, color=RED, width=6),
                    dict(type="pin", at="denver", t0=1.0, label="DENVER", side="l", box=True, size=40),
                    dict(type="label", at="limon", text="1870", t0=0.5, dy=-80, size=60)]),
        [Badge("1870", 0.2, None)], tex=GFX)
    add(125.60, cus(G4.calendar, cards=[("15", "AGOSTO DE 1870", "LAS DOS CUADRILLAS SE JUNTAN", 0.2, (60, 62, 66))], title="EN MITAD DE LA PRADERA"),
        tr="fade", td=0.3, tex=GFX)
    add(w("a unas", 129.4), mp("kc_mid", [(0, -104.65, 39.74, 0.85), (4.5, -104.65, 39.74, 0.95)],
                                [dict(type="rail", path=["denver", "bennett", "strasburg"], t0=0.0, draw=2.5, color=YELLOW, width=6),
                                 dict(type="pin", at="denver", t0=0.1, label="DENVER", side="l", box=True, size=44),
                                 dict(type="pin", at="strasburg", t0=1.8, label="STRASBURG", side="r", box=True, size=44),
                                 dict(type="label", at=(-104.65, 39.74), text="38 MILLAS · ~60 KM", t0=2.4, dy=-110, size=56, box=True)]),
        tex=GFX)
    add(134.40, fr("f_28826764000.jpg", "Strasburg, Colorado · foto: Lyn Lomasi (CC BY 2.0)", "doc"), [big("HOY: STRASBURG", 0.1, 0.1, 72, YELLOW)], tex=CLEAN)
    add(136.00, kb("u_p2B-PQTFuwA.jpg", "in", "warm"), [big("SEGÚN EL CARTEL DEL LUGAR…", 0.2, 0.84, 64)], tex=CLEAN)
    add(139.20, fr("f_5199203755.jpg", "Tendido de vía en Kansas, 1867 · " + GARDNER, zoom=(1.0, 1.12)),
        [Counter(0, 10, "{:.0f} MILLAS", "≈ 16 KM EN UNA SOLA JORNADA", 0.4, 1.4, (0.5, 0.42), 170)], tex=ARCH)
    add(144.90, mp("kc_us", [(0, -96.0, 39.0, 0.62), (5.0, -98.0, 39.5, 0.66)],
                   [dict(type="rail", path=COAST, t0=0.3, draw=4.0, color=YELLOW, width=6)]),
        [big("UNA CADENA DE RIELES DE COSTA A COSTA", w("costa", 148.6) - 144.9, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(150.10, mp("kc_us", [(0, -98.0, 39.5, 0.66), (4.9, -100.0, 39.5, 0.7)],
                   [dict(type="rail", path=COAST, t0=-5, draw=0.1, color=YELLOW, width=6),
                    dict(type="pin", at="denver", t0=w("denver", 154.0) - 150.1, label="PASANDO POR DENVER", side="r", box=True, size=46),
                    dict(type="label", at="nyc", text="ATLÁNTICO", t0=w("atlántico", 152.2) - 150.1, dx=60, dy=60, size=48, box=True),
                    dict(type="label", at="sf", text="PACÍFICO", t0=w("pacífico", 153.3) - 150.1, dx=-40, dy=60, size=48, box=True)]),
        [big("POR FIN, EN TREN", 0.2, 0.1, 64, YELLOW)], tex=GFX)
    add(155.00, L("09576", kb("u_Q9X_p5dDq_8.jpg", "in", "warm"), "Calle 16, Denver · años 1870 · " + LOC_),
        [big("PARA DENVER, UNA FIESTA", 0.2, 0.08, 64, YELLOW)], tex=ARCH)
    add(157.20, L("18853", kb("u_YfTxKqI9vDU.jpg", "in", "dark"), "Baldwin Locomotive Works, Filadelfia · " + LOC_),
        [Badge("FILADELFIA · 1870", 0.2, None), big("BALDWIN LOCOMOTIVE WORKS", w("baldwin", 160.0) - 157.2, 0.86, 62, YELLOW)], tex=ARCH)
    bg, ov = card([("LLEVABA EL NÚMERO", 56, GREY_, 0.27, 0.1), ("51", 380, YELLOW, 0.57, 0.3)], base="black")
    add(163.60, bg, ov, tr="black", td=0.1, tex=DARK)
    add(165.10, cus(G9.anatomy, t_chim=w("chimenea", 168.6) - 165.1, t_boil=w("caldera", 169.6) - 165.1, t_tend=w("tender", 171.1) - 165.1),
        tr="fade", td=0.3, tex=GFX)
    add(173.50, mp("kc_reg", [(0, -99.5, 39.0, 0.78), (4.0, -100.5, 39.0, 0.8)],
                   kp_layers(0.0, 0.1) + [dict(type="route", path=KP, t0=0.0, draw=0.1, color=YELLOW, width=1, traffic=3, speed=260)]),
        [big("YENDO Y VINIENDO POR LAS LLANURAS", 0.2, 0.1, 58)], tex=GFX)
    add(177.80, L("1s00053", fr("f_5199203001.jpg", "Embarque de ganado en Abilene, Kansas · " + GARDNER),
                  "Carga de ganado en Abilene, Kansas · 1867 · " + LOC_), [big("TRENES DE CARGA", 0.2, 0.08, 64, YELLOW)], tex=ARCH)
    add(181.50, kb("u_rvVhr2LngP4.jpg", "in", "dark"), [rich("UN PROBLEMA QUE NO SE VEÍA EN EL MAPA", ("problema",), 0.2, step=0.1, y=0.84, size=58, maxw=0.85)],
        tex=DARK)
    add(185.90, V("18305", "u_jaHmB2Z996I.jpg", 0.0, "dark"), [big("DEBÍA MÁS DE LO QUE GANABA", 0.1, 0.84, 70, YELLOW)], tex=DARK)
    add(187.70, kb("u_BgDf7_FFVhE.jpg", "in", "warm"), [Stamp("QUIEBRA · 1876", w("quiebra", 189.3) - 187.7, RED, (0.5, 0.45), -10, 120)], tex=CLEAN)
    add(w("en manos", 190.3), V("241", "u_CDQ9CKvYreg.jpg", 0.5, "warm"), [big("ADMINISTRADORES NOMBRADOS POR UN JUEZ", 0.2, 0.84, 58)], tex=CLEAN)
    add(193.50, V("3459", "u_InMS8UZ5Ki8.jpg", 0.0, "warm"), [big("EL TREN SEGUÍA FUNCIONANDO…", 0.2, 0.84, 62),
                                                               big("…AHORRANDO EN TODO", w("ahorrando", 196.8) - 193.5, 0.84, 70, YELLOW, t1=None)], tex=DARK)
    add(199.10, V("21581", "u_ofJ7pPG9KcI.jpg", 0.0, "dark"), [rich("Y DONDE MÁS SE NOTABA ERA EN LUGARES COMO ESTE", ("este",), 0.2, step=0.1, y=0.84, size=56,
                                                            maxw=0.85)], tex=DARK)

    # ============================== CAP 2: UN ARROYO CASI SIEMPRE SECO (203.7 - 322.2)
    bg, ov = chapter(2, "UN ARROYO CASI SIEMPRE SECO", "w_kiowa_creek.jpg", year="1877")
    add(203.70, bg, ov, tr="black", td=0.2, tex=DARK)
    add(207.60, mp("kc_mid", [(0, -104.75, 39.74, 0.85), (4.0, -104.65, 39.75, 1.0)],
                   [dict(type="rail", path=["denver", "watkins", "bennett", "kc_cross", "strasburg"], t0=0.0, draw=0.1, color=(120, 120, 140), width=4),
                    dict(type="route", ll=CREEK, t0=0.3, draw=2.0, color=BLUE, width=6),
                    dict(type="pin", at="denver", t0=0.0, label="DENVER", side="l", box=True, size=44),
                    dict(type="pin", at="kc_cross", t0=1.4, label="KIOWA CREEK", side="r", box=True, size=48),
                    dict(type="label", at=(-104.70, 39.74), text="25 MILLAS · ~40 KM", t0=2.0, dy=-100, size=52, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(211.90, kb("w_kiowa_creek.jpg", "in", "doc"), [Badge("1877", 0.2, None), Caption("Kiowa Creek, Colorado · 2023", "foto: Jeffrey Beall (CC BY 4.0)", 0.6)], tex=CLEAN)
    add(216.20, kb("f_45193826691.jpg", "in", "doc"), [big("UNA FRANJA ANCHA DE ARENA CLARA", 0.2, 0.84, 64),
                                                     Caption("Bijou Creek, vecino del Kiowa · foto: James St. John (CC BY 2.0)", None, 1.0, y=0.08)], tex=CLEAN)
    add(w("con algo", 218.6), kb("u_ofJ7pPG9KcI.jpg", "in", "warm"), [big("Y CASI NUNCA AGUA", 0.4, 0.84, 72, YELLOW)], tex=CLEAN)
    add(221.60, kb("u_eYWNaMffWHI.jpg", "in", "warm"), [big("A PIE, SIN MOJARTE LAS BOTAS", 0.2, 0.84, 66)], tex=CLEAN)
    add(224.60, mp("kc_mid", [(0, -104.62, 39.06, 0.95), (2.0, -104.56, 39.30, 0.95), (6.4, -104.25, 40.10, 0.9)],
                   [dict(type="route", ll=CREEK, t0=0.6, draw=6.0, color=BLUE, width=6),
                    dict(type="pin", at="black_forest", t0=0.2, label="BLACK FOREST", side="l", box=True, size=46),
                    dict(type="pin", at="kc_cross", t0=4.0, label="EL CRUCE", side="r", box=True, size=40),
                    dict(type="pin", at="platte_mouth", t0=w("south", 230.4) - 224.6, label="SOUTH PLATTE", side="r", box=True, size=46)]),
        [big("NACE AL SUR…", 0.2, 0.1, 58, t1=w("desemboca", 228.6) - 224.6 - 0.3), big("…Y MUERE AL NORTE", w("desemboca", 228.6) - 224.6, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(232.20, V("41370", "f_30254783477.jpg", 2.0, "doc"), [big("CASI TODO EL AÑO: NADA", 0.2, 0.84, 70)], tex=CLEAN)
    add(235.30, fr("f_5199203043.jpg", "Un pueblo junto a la vía: Salina, Kansas, 1867 · " + GARDNER), [big("UN PUÑADO DE CASAS", 0.2, 0.08, 64)], tex=ARCH)
    add(238.60, mp("kc_loc", [(0, -104.43, 39.755, 0.6), (3.6, -104.41, 39.753, 0.8)],
                   [dict(type="pin", at="kc_cross", t0=0.3, label="KIOWA CROSSING", side="r", box=True, size=54),
                    dict(type="label", at="kc_cross", text="«EL CRUCE DEL KIOWA»", t0=w("el cruce", 240.6) - 238.6, dy=110, size=46)]),
        tr="zoom", td=0.3, tex=GFX)
    add(242.20, kb("u_qMUTRo3jdnk.jpg", "in", "warm"), [Badge("MARZO DE 1877", 0.2, None),
                                                       Stamp("OFICINA DE CORREOS: BENNET", w("bennet", 246.0) - 242.2, YELLOW, (0.5, 0.5), -6, 90)], tex=CLEAN)
    bg, ov = card([("POR UN POLÍTICO DE COLORADO", 50, GREY_, 0.33, 0.1), ("HIRAM P. BENNET", 130, WHITE, 0.52, 0.5)])
    add(247.60, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(249.90, Solid("dark_grid"), [BigText("BENNET", "bebas", 220, WHITE, (0.5, 0.45), 0.1, w("dos", 253.2) - 249.9, "up", tracking=20),
                                     BigText("BENNETT", "bebas", 220, YELLOW, (0.5, 0.45), w("dos", 253.2) - 249.9, None, "pop", tracking=20),
                                     big("CON DOS T", w("dos", 253.2) - 249.9 + 0.3, 0.7, 70, WHITE)], tex=GFX)
    add(254.90, cus(G9.crossing, mode="build", t0=0.8, bt=99), tr="fade", td=0.3, tex=GFX)
    add(258.30, kb("u_FZEvFjHqxfk.jpg", "in", "doc"), [big("UN MURO DE TIERRA QUE SUBE LA VÍA", 0.2, 0.84, 64)], tex=CLEAN)
    add(261.40, cus(G9.crossing, mode="build", t0=-5.0, bt=w("puente", 263.4) - 261.4 - 0.4), tr="fade", td=0.25, tex=GFX)
    add(264.60, kb("u_1Y5W0TOI3I0.jpg", "in", "doc"), [big("PARA UN ARROYO SECO: MÁS QUE SUFICIENTE", 0.2, 0.84, 60)], tex=CLEAN)
    add(267.40, V("2088", "u_xYsP8ZRDq8E.jpg", 2.0, "doc"), [big("NI TE HABRÍAS FIJADO EN EL PUENTE", 0.3, 0.84, 62)], tex=CLEAN)
    add(271.30, kb("u_Obpget_fY8U.jpg", "punch", "dark"), [big("NO SIEMPRE ESTÁ SECO", 0.3, 0.84, 84, YELLOW, "pop")], tr="flash", td=0.2, tex=DARK)
    add(274.20, V("21576", "u_QMT9sUm6yPE.jpg", 0.0, "dark"), [big("TORMENTAS DE PRIMAVERA", 0.2, 0.84, 70)], tex=DARK)
    add(w("pueden", 276.6), kb("u_m-5pFjuxSBk.jpg", "in", "dark"), [big("VIOLENTAS", 0.2, 0.84, 96, RED, "pop")], tex=DARK)
    add(278.30, V("26077", "u_F1dMNfyhd1k.jpg", 0.0, "dark"), [big("MUCHA AGUA EN POCO TIEMPO", 0.2, 0.84, 68), big("A VECES, LEJOS", w("a veces", 280.9) - 278.3, 0.1, 60, YELLOW)],
        tex=DARK)
    add(282.70, mp("kc_mid", [(0, -104.50, 39.50, 0.9), (5.5, -104.47, 39.58, 0.95)],
                   [dict(type="route", ll=CREEK, t0=0.0, draw=0.1, color=BLUE, width=5),
                    dict(type="cloud", at=(-104.55, 39.30), t0=0.3, label="LLUVIA A CÁNTAROS", size=44, bolt=True),
                    dict(type="sun", at="kc_cross", t0=w("mientras", 285.6) - 282.7, label="SOL EN EL CRUCE", size=44),
                    dict(type="label", at=(-104.47, 39.52), text="20 MILLAS RÍO ARRIBA", t0=1.4, dx=260, size=46, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(288.20, kb("u_xFgmpNb-4Rg.jpg", "in", "warm"), [big("NO TIENE DÓNDE QUEDARSE", 0.2, 0.84, 70)], tex=CLEAN)
    add(291.40, kb("f_51314490745.jpg", "punch", "doc"), [big("DE GOLPE, COMO UNA OLA", 0.2, 0.84, 76, YELLOW),
                                                        Caption("Crecida repentina en un cauce seco · Arizona", "Grand Canyon NPS (CC BY 2.0)", 0.8, y=0.08)], tex=CLEAN)
    add(294.60, kb("u_xbqLvtw_nd0.jpg", "in", "doc"), [big("UNA MANGUERA DE JARDÍN VACÍA", 0.2, 0.84, 66)], tex=CLEAN)
    add(296.90, cus(G9.hose, open_t=w("abres", 301.0) - 296.9, travel=1.3), tr="fade", td=0.25, tex=GFX)
    add(305.30, kb("f_31319968238.jpg", "in", "doc"), [big("KIOWA CREEK: IGUAL, PERO A LO GRANDE", 0.2, 0.84, 62, YELLOW)], tex=CLEAN)
    add(308.70, cus(G9.crossing, mode="dry", labels=False), [big("PENSADO PARA EL KIOWA DE TODOS LOS DÍAS", 0.2, 0.12, 60)], tr="fade", td=0.25, tex=GFX)
    add(311.70, kb("u_a3pKxtQ0OdM.jpg", "in", "warm"), [big("ARENA SECA · BOTAS LIMPIAS", 0.2, 0.84, 70)], tex=CLEAN)
    add(314.40, V("4422", "u_pSmG9_yxKbA.jpg", 0.0, "night"), [big("NO PARA UNA NOCHE DE TORMENTA", 0.1, 0.84, 66, YELLOW)], tex=DARK)
    add(316.50, V("28901", "u_FQODry-m9Kc.jpg", 0.0, "dark"), [big("UNOS AÑOS, NADA", 0.2, 0.84, 70)], tex=DARK)
    add(318.90, Solid("black"), [big("HASTA LA PRIMAVERA DE 1878", 0.1, 0.5, 110, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)

    # ============================== CAP 3: LA NOCHE DEL 21 DE MAYO DE 1878 (322.2 - 442.3)
    bg, ov = chapter(3, "LA NOCHE DEL 21 DE MAYO", "u_qyUBpdfN1N8.jpg", year="1878")
    add(322.20, bg, ov, tr="black", td=0.2, tex=DARK)
    add(w("sobre", 325.0), mp("kc_mid", [(0, -104.55, 39.30, 0.95), (6.0, -104.45, 39.55, 0.9)],
                               [dict(type="route", ll=CREEK, t0=w("durante", 327.8) - 325.0, draw=4.5, color=(90, 150, 210), width=10),
                                dict(type="cloud", at=(-104.62, 39.18), t0=0.0, scale=1.1, bolt=True),
                                dict(type="cloud", at=(-104.45, 39.30), t0=0.3, scale=0.9, bolt=True),
                                dict(type="label", at=(-104.62, 39.12), text="TIERRAS ALTAS AL SUR DE BENNETT", t0=0.6, dy=200, size=44, box=True),
                                dict(type="pin", at="bennett", t0=0.4, label="BENNETT", side="l", box=True, size=40)]),
        [big("BARRANCOS Y CAUCES SECOS SE LLENAN", w("durante", 327.8) - 325.0 + 0.4, 0.1, 56, BLUE)], tr="zoom", td=0.3, tex=GFX)
    add(331.40, V("4423", "u_SY-kiXImJR4.jpg", 0.0, "night"), [big("AL CAER LA NOCHE…", 0.2, 0.84, 70)], tex=DARK)
    add(335.60, V("100183", "u_FNZwttoLRSU.jpg", 0.0, "doc"), [big("UN RÍO ANCHO, MARRÓN Y RÁPIDO", 0.2, 0.84, 70, YELLOW)], tex=CLEAN)
    add(w("que arrastraba", 338.0), kb("u_jyn_JGU4HtQ.jpg", "punch", "doc"), [big("RAMAS · PIEDRAS · TODO", 0.2, 0.84, 76)], tex=CLEAN)
    add(342.50, cus(G9.washout_plan, t0=0.1, front_d=3.4, solo_t=w("toda", 346.3) - 342.5, erode_t=99, cede_t=99), tr="fade", td=0.3, tex=GFX)
    add(349.00, cus(G9.crossing, mode="flood", t0=-1.0), tr="fade", td=0.25, tex=GFX)
    add(354.50, cus(G9.washout_plan, t0=-10.0, front_d=0.1, solo_t=-10.0, erode_t=-0.8, erode_d=3.2, cede_t=w("cedió", 356.4) - 354.5),
        tr="fade", td=0.25, tex=GFX)
    add(358.80, cus(G9.crossing, mode="gap", t0=0.4), tr="fade", td=0.3, tex=DARK)
    add(363.90, mp("kc_mid", [(0, -104.80, 39.74, 1.0), (5.0, -104.55, 39.75, 1.1)],
                   [dict(type="route", path=["denver", "watkins", "bennett", "kc_cross"], t0=0.4, draw=4.5, color=YELLOW, width=5),
                    dict(type="route", ll=CREEK, t0=0.0, draw=0.1, color=(90, 150, 210), width=8),
                    dict(type="pin", at="denver", t0=0.1, label="DENVER", side="l", box=True, size=44),
                    dict(type="xmark", at="kc_cross", t0=0.2)]),
        [Badge("21 DE MAYO · NOCHE", 0.2, None), big("UN TREN DE CARGA SALE HACIA EL ESTE", 0.4, 0.1, 58)], tr="zoom", td=0.3, tex=GFX)
    add(369.00, kb("u_57muzgYYtFQ.jpg", "in", "night"), [big("DELANTE: LA LOCOMOTORA 51", 0.1, 0.84, 70, YELLOW)], tex=DARK)
    add(371.30, kb("u_InMS8UZ5Ki8.jpg", "in", "dark"), [big("EN LA CABINA, LOS HOMBRES QUE LA MANEJABAN", 0.2, 0.84, 58)], tex=DARK)
    add(374.30, kb("u_Dz_WKOrSnwE.jpg", "in", "bw"), [big("LOS PERIÓDICOS DIERON SUS NOMBRES", 0.2, 0.84, 62)], tex=ARCH)
    add(376.90, cus(G9.names3, t0=0.1, step=w("george", 378.4) - 376.9, end_t=w("ni siquiera", 382.8) - 376.9,
                    bottom="NI SIQUIERA EN ESO SE PUSIERON DE ACUERDO"), tr="fade", td=0.3, tex=DARK)
    add(385.30, cus(G9.cab, end_t=99), [big("PONTE EN ESA CABINA", 0.1, 0.18, 70), big("DE NOCHE · LLUEVE", w("es de", 386.6) - 385.3, 0.3, 60, BLUE)],
        tr="black", td=0.15, tex=DARK)
    add(387.80, kb("u_57muzgYYtFQ.jpg", "punch", "night"), [big("LA ÚNICA LUZ: EL FAROL", 0.2, 0.84, 72, YELLOW)], tex=DARK)
    add(w("que alumbra", 390.3), warp(G9.cab, 3.0, 1.0, end_t=99), [big("UNOS METROS DE VÍA MOJADA", 0.2, 0.18, 64)], tex=DARK)
    add(393.30, kb("u_ZxZQk7777R4.jpg", "in", "night"), [big("NADIE HA PODIDO AVISAR", w("nadie", 395.8) - 393.3, 0.84, 72, RED)], tex=DARK)
    add(397.60, cus(G9.cab, end_t=w("la locomotora", 407.0) - 397.6), [big("ESPERANDO VER EL PUENTE DE SIEMPRE", 0.3, 0.18, 60),
                                                                   big("¿CUÁNTO TIEMPO PARA REACCIONAR?", w("es imposible", 402.2) - 397.6, 0.3, 64, YELLOW)],
        tex=DARK)
    add(407.00, cus(G9.crossing, mode="fall", fall_t=w("cayó", 409.4) - 407.0), [Flash(w("cayó", 409.4) - 407.0 + 0.25, 0.25)],
        tr="black", td=0.1, tex=DARK, post=postshake(0.0))
    add(412.70, V("3458", "u_lXISATe1WBQ.jpg", 0.0, "dark"), [big("TRES HOMBRES PERDIERON LA VIDA", 0.2, 0.5, 86, WHITE),
                                                            rich("NUNCA SE ACLARÓ DEL TODO QUIÉN IBA A BORDO", ("quién",), w("aunque", 415.2) - 412.7, step=0.1, y=0.66,
                                                                 size=50, maxw=0.85)], tr="black", td=0.3, tex=DARK)
    add(418.20, kb("f_9790154476.jpg", "in", "doc"), [big("AL BAJAR EL AGUA…", 0.2, 0.84, 70),
                                                    Caption("Vía socavada por una crecida", "foto: Andrew Magill (CC BY 2.0)", 0.8, y=0.08)], tex=CLEAN)
    add(422.20, cus(G9.crossing, mode="recover", t0=0.6, tender_t=w("también", 428.1) - 422.2, temp_t=99, no_t=99), tr="fade", td=0.3, tex=GFX)
    add(429.50, fr("f_5199202033.jpg"),
        [Caption("Puente del ferrocarril sobre el Kaw, Kansas · 1867", GARDNER, 0.3, y=0.08),
         LowerThird("CORONEL FISHER", "Superintendente de la zona", 0.4, w("levantó", 431.8) - 429.5 + 0.6),
         big("UN PUENTE PROVISIONAL, A TODA PRISA", w("levantó", 431.8) - 429.5 + 0.9, 0.88, 56, YELLOW)], tex=ARCH)
    add(434.90, cus(G9.crossing, mode="recover", t0=-9, cars=False, temp_t=-5, no_t=99, labels=False),
        [big("LOS TRENES VOLVIERON A PASAR", 0.2, 0.12, 64)], tr="fade", td=0.3, tex=GFX)
    add(438.10, V("2871", "u_2tfQcOodk60.jpg", 1.0, "doc"), [big("TODO VOLVIÓ A LA NORMALIDAD", 0.1, 0.84, 70)], tex=CLEAN)
    add(439.80, Solid("black"), [big("TODO, MENOS LA LOCOMOTORA", 0.1, 0.5, 110, RED, "pop")], tr="black", td=0.1, tex=DARK)

    # ============================== CAP 4: LA PRIMERA BÚSQUEDA (442.3 - 565.5)
    bg, ov = chapter(4, "LA PRIMERA BÚSQUEDA", "u_2jPwtG5cZOA.jpg", year="1878")
    add(442.30, bg, ov, tr="black", td=0.2, tex=DARK)
    add(445.30, kb("f_45193826691.jpg", "out", "doc"), [big("NI JUNTO AL PUENTE", 0.4, 0.84, 70),
                                                      big("NI RÍO ABAJO", w("ni río", 447.4) - 445.3, 0.72, 70, YELLOW),
                                                      big("NI A LA VISTA", w("ni enterrada", 448.6) - 445.3, 0.6, 70, RED)], tex=CLEAN)
    add(450.60, fr("f_54521488997.jpg", "Una locomotora de la época · imagen de referencia", "bw"), [big("LO MÁS CARO DE UN FERROCARRIL", 0.2, 0.1, 60, YELLOW)],
        tex=ARCH)
    add(452.80, V("18304", "u_jaHmB2Z996I.jpg", 0.0, "warm"), [Stamp("EN QUIEBRA", 0.4, RED, (0.5, 0.45), -10, 130),
                                                             big("NO PODÍA DEJARLA ATRÁS", 1.4, 0.84, 66)], tex=CLEAN)
    add(456.20, kb("u_8iNmC7ZJFnY.jpg", "in", "doc"), [big("A BUSCARLA", 0.2, 0.84, 90, YELLOW, "pop")], tex=CLEAN)
    bg, ov = card([("AL FRENTE: EL JEFE DE TALLERES", 50, GREY_, 0.32, 0.1), ("NESMITH", 180, WHITE, 0.53, w("nesmith", 461.9) - 458.9)])
    add(458.90, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(463.40, V("18305", "u_jaHmB2Z996I.jpg", 2.0, "dark"), [Counter(0, 6000, "${:,.0f}", "GASTADOS EN LA BÚSQUEDA", w("seis", 466.0) - 463.4, 1.2, (0.5, 0.42), 180),
                                                             big("UNA FORTUNA", w("fortuna", 468.3) - 463.4, 0.8, 70, YELLOW)], tex=DARK)
    add(469.50, cus(G9.crossing, mode="search", pit_t=99), [big("UNA Y OTRA VEZ", w("una y otra", 473.0) - 469.5, 0.24, 56, YELLOW)], tr="fade", td=0.3, tex=GFX)
    add(474.70, kb("u_JADCXzrkyuA.jpg", "punch", "bw"), [big("EL GOLPE SECO DEL METAL", 0.1, 0.84, 70)], tex=DARK)
    add(476.80, cus(G9.crossing, mode="search", pit_t=0.6, dig_d=3.4), [Badge("Y CAVARON", 0.1, None)], tr="fade", td=0.25, tex=GFX)
    add(482.60, kb("u_2jPwtG5cZOA.jpg", "punch", "dark"), [big("AHORA MIRA ESE POZO", 0.1, 0.84, 72, YELLOW)], tex=DARK)
    add(484.30, kb("u_7FgmeXzVlh0.jpg", "down", "dark"), [big("ARENA MOJADA QUE SE ESCURRE", 0.1, 0.84, 66)], tex=DARK)
    add(486.70, kb("u_B-JJxUzeX3M.jpg", "in", "doc"), [big("PALAS AL FONDO", 0.1, 0.84, 76)], tex=CLEAN)
    add(488.30, kb("f_31319968238.jpg", "out", "doc"), [rich("Y ARRIBA, EL ARROYO QUE SE TRAGÓ UN TREN", ("tren",), 0.2, step=0.1, y=0.84, size=58, maxw=0.85)],
        tex=CLEAN)
    add(492.10, V("2066", "u_k8dhUvoSbOs.jpg", 0.0, "dark"), [big("PODÍA VOLVER A PASAR", 0.3, 0.84, 80, RED)], tex=DARK)
    add(495.20, kb("u_an61L7VeTeY.jpg", "in", "doc"), [big("SOLO SALIERON JUEGOS DE RUEDAS", 0.2, 0.84, 66)], tex=CLEAN)
    add(498.30, Solid("black"), [Stamp("NI RASTRO", 0.2, RED, (0.5, 0.5), -8, 160)], tr="black", td=0.1, tex=DARK)
    add(501.20, fr("f_54567792007.jpg", None, "bw"), [Darken(0.45), rich("¿CÓMO PUEDE DESAPARECER ALGO TAN GRANDE?", ("grande?",), 0.1, step=0.1, y=0.5, size=72,
                                                                       maxw=0.8)], tex=ARCH)
    add(503.70, kb("u_qzLNoovv09M.jpg", "punch", "warm"), [big("LA RESPUESTA ESTÁ EN LA ARENA", 0.1, 0.84, 72, YELLOW)], tex=CLEAN)
    GR = dict(t_water=w("pero", 508.1) - 505.6 + 0.4, t_sink=w("y lo que", 516.5) - 505.6 - 0.3, t_dry=w("luego", 518.5) - 505.6)
    add(505.60, cus(G9.grains, **GR), tr="fade", td=0.25, tex=GFX)
    add(513.30, V("41369", "u_vvXmOOL2dRE.jpg", 0.0, "doc"), [big("CASI COMO UN LÍQUIDO", 0.1, 0.84, 80, BLUE)], tex=CLEAN)
    add(516.50, warp(G9.grains, 516.5 - 505.6, 1.0, **GR), [big("FIRME OTRA VEZ", w("firme", 523.5) - 516.5, 0.9, 64, YELLOW)], tex=GFX)
    add(524.80, V("1931", "u_L13LuGgpJz0.jpg", 2.0, "doc"), [big("LO HAS VISTO EN LA PLAYA", 0.1, 0.84, 70)], tex=CLEAN)
    add(526.20, kb("u_4H7jhY0euKQ.jpg", "down", "doc"), [big("QUIETO EN LA ORILLA…", 0.2, 0.84, 66)], tex=CLEAN)
    add(w("llega", 527.8), V("1013", "u_fu55ZVUsMG4.jpg", 3.0, "doc"), [big("…LOS PIES SE HUNDEN SOLOS", 0.6, 0.84, 66, YELLOW)], tex=CLEAN)
    add(530.90, V("51481", "u_edFec7dDfss.jpg", 0.0, "doc"), [big("LA ARENA QUEDA LISA", 0.4, 0.84, 72),
                                                            big("COMO SI NUNCA HUBIERAS ESTADO", w("como", 533.7) - 530.9, 0.12, 56, YELLOW)], tex=CLEAN)
    add(536.00, V("41368", "u_FNZwttoLRSU.jpg", 0.0, "dark"), [big("EN 1878, LO MISMO…", 0.2, 0.84, 72)], tex=DARK)
    add(540.10, warp(G9.grains, -0.0, 1.0, t_water=-3.0, t_sink=0.2, t_dry=3.0, labels=False),
        [big("…SOLO QUE LO QUE SE HUNDE ES UN TREN", 0.2, 0.12, 60, YELLOW)], tr="fade", td=0.25, tex=GFX)
    add(543.90, cus(G9.crossing, mode="shuffle", labels=False, t0=0.2), [big("SEGUÍA AHÍ ABAJO… EN ALGÚN LUGAR", 0.2, 0.12, 64)], tr="fade", td=0.25, tex=GFX)
    add(549.00, kb("u_DvQ3xYWObr8.jpg", "in", "bw"), [big("LAS VARILLAS NO TOCARON NADA", 0.2, 0.84, 64),
                                                    Stamp("BÚSQUEDA ABANDONADA", w("dejó", 552.0) - 549.0, RED, (0.5, 0.42), -8, 100)], tex=ARCH)
    add(553.60, kb("u_aG8iIT9_iqM.jpg", "in", "dark"), [big("ANTES DE QUE ESTO SE CONVIERTA EN LEYENDA…", 0.2, 0.84, 58)], tex=DARK)
    add(558.00, kb("u_57muzgYYtFQ.jpg", "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe),
                                                                big("TE PROMETO QUE ESTE TIENE FINAL", w("te prometo", 562.8) - 558.0, 0.3, 58, YELLOW)], tex=DARK)

    # ============================== CAP 5: NACE LA LEYENDA (565.5 - 706.9)
    bg, ov = chapter(5, "NACE LA LEYENDA", "u_aG8iIT9_iqM.jpg", year="1914–1982")
    add(565.50, bg, ov, tr="black", td=0.2, tex=DARK)
    add(570.60, kb("u_szLT9wytlJ8.jpg", "in", "dark"), [torch(((0.4, 0.55), (0.6, 0.5)), r=460, amb=0.2),
                                                       big("EN EL FONDO DORMÍA UNA LOCOMOTORA ENTERA", 0.2, 0.84, 58)], tex=DARK)
    add(574.10, kb("u_MNxynPJOFiM.jpg", "punch", "warm"), [big("BASTABA CON CAVAR EN EL LUGAR JUSTO", 0.1, 0.84, 62)], tex=CLEAN)
    add(576.50, kb("u_IzLWSbMoCPo.jpg", "in", "dark"), [Darken(0.35), BigText("LA LOCOMOTORA PERDIDA", "serif", 96, WHITE, (0.5, 0.45), 0.3, None, "up"),
                                                       BigText("DE KIOWA CREEK", "bebas", 84, YELLOW, (0.5, 0.58), 0.8, None, "up", tracking=10)], tex=DARK)
    add(579.30, kb("u_5d8S0VTGvDo.jpg", "in", "warm"), [Badge("JULIO DE 1914", 0.2, None), big("36 AÑOS DESPUÉS", w("36", 581.0) - 579.3, 0.84, 76, YELLOW)],
        tr="fade", td=0.3, tex=ARCH)
    add(w("un periódico", 584.0), cus(G9.newspaper, hl1=99, hl2=99), tr="fade", td=0.25, tex=GFX)
    bg, ov = card([("SE LO CONTÓ UN SUPERINTENDENTE DE LA", 48, GREY_, 0.32, 0.1), ("UNION PACIFIC", 150, YELLOW, 0.5, 0.4),
                   ("QUE YA CONTROLABA AQUELLA VÍA", 52, WHITE, 0.68, w("la compañía", 590.7) - 587.5)])
    add(587.50, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(593.70, kb("u_XVYleJiw_As.jpg", "in", "dark"), [big("LOS DETALLES YA HABÍAN CAMBIADO", 0.2, 0.84, 64)], tex=DARK)
    add(597.00, cus(G9.newspaper, hl1=0.4, hl2=w("y llamaba", 600.9) - 597.0 + 0.4), tr="fade", td=0.25, tex=GFX)
    add(604.00, cus(G9.legend, t0=-0.3, step=0.9, last_t=99), tr="fade", td=0.25, tex=GFX)
    add(607.30, kb("u_Dz_WKOrSnwE.jpg", "in", "bw"), [big("ASÍ FUNCIONAN LAS LEYENDAS", 0.1, 0.84, 70, YELLOW),
                                                    big("CADA VEZ QUE SE CUENTAN, CAMBIAN", w("cada", 609.6) - 607.3, 0.12, 56)], tex=ARCH)
    add(612.50, cus(G9.legend, t0=-5.0, step=0.9, last_t=w("la locomotora", 614.7) - 612.5), tex=GFX)
    add(616.90, kb("u_jyn_JGU4HtQ.jpg", "in", "doc"), [Badge("1935", 0.2, None), big("OTRA CRECIDA ENORME", 0.3, 0.84, 76, YELLOW)], tr="flash", td=0.2, tex=CLEAN)
    add(621.50, fr("f_460205263.jpg", "Vía arrastrada por una crecida · foto: born1945 (CC BY 2.0)", "bw"),
        [big("SE LLEVÓ OTRA VEZ LOS PUENTES", 0.2, 0.08, 62)], tex=ARCH)
    add(625.70, V("100184", "u_BYJHQG_KdHc.jpg", 0.0, "doc"), [big("EL ARROYO RECORDÓ DE QUÉ ERA CAPAZ", 0.2, 0.84, 62)], tex=CLEAN)
    add(628.40, cus(G9.crossing, mode="shuffle", t0=0.2), [big("COMO QUIEN BARAJA UN MAZO DE CARTAS", w("como", 631.2) - 628.4, 0.24, 52, YELLOW)],
        tr="fade", td=0.25, tex=GFX)
    add(633.00, kb("u_1gn8Q_zecco.jpg", "in", "bw"), [big("CADA AÑO, MÁS DIFÍCIL SABER DÓNDE", 0.3, 0.84, 62)], tex=DARK)
    add(638.20, kb("u_5d8S0VTGvDo.jpg", "in", "warm"), [Badge("1978", 0.2, None), big("100 AÑOS DEL ACCIDENTE", 0.4, 0.84, 70, YELLOW)], tex=CLEAN)
    add(642.40, kb("u_XVYleJiw_As.jpg", "in", "dark"), [big("UN ARTÍCULO SOBRE LA LOCOMOTORA DESAPARECIDA", 0.1, 0.84, 56)], tex=DARK)
    add(w("y uno", 646.0), V("10395", "u_HwL5Yn048FY.jpg", 0.0, "warm"), [big("UNO DE SUS LECTORES…", 0.1, 0.84, 66)], tex=CLEAN)
    bg, ov = card([("UN ESCRITOR LLAMADO", 52, GREY_, 0.33, 0.1), ("CLIVE CUSSLER", 160, WHITE, 0.52, 0.2), ("NOVELISTA DE AVENTURAS", 54, YELLOW, 0.7, 2.0)])
    add(w("clive", 648.6) - 0.6, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(651.40, kb("u_99CW5GoxcbY.jpg", "in", "warm"), [big("MUY CONOCIDO EN ESTADOS UNIDOS", 0.1, 0.84, 64)], tex=CLEAN)
    add(654.00, V("21612", "u_rvVhr2LngP4.jpg", 0.0, "dark"), [big("UNA AFICIÓN POCO COMÚN…", 0.2, 0.84, 64),
                                                             big("BUSCAR NAUFRAGIOS DE VERDAD", w("buscar", 656.7) - 654.0, 0.12, 64, YELLOW)], tex=DARK)
    bg, ov = card([("NUMA", 240, YELLOW, 0.45, 0.2), ("AGENCIA NACIONAL SUBMARINA Y MARINA", 56, WHITE, 0.66, w("la agencia", 660.0) - 658.7)])
    add(658.70, bg, ov, tr="fade", td=0.2, tex=GFX)
    hun = pick("w_hunley.jpg", "")
    if hun:
        add(664.50, fr(hun, "El submarino H. L. Hunley · Marina de EE. UU. (dominio público)", "bw"), [big("EL SUBMARINO HUNLEY", 0.2, 0.08, 64, YELLOW)], tex=ARCH)
    else:
        bg, ov = card([("AÑOS MÁS TARDE ENCONTRARÍA", 50, GREY_, 0.33, 0.1), ("EL SUBMARINO HUNLEY", 120, WHITE, 0.5, 0.4),
                       ("DE LA GUERRA CIVIL", 60, YELLOW, 0.66, 1.2)])
        add(664.50, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(668.60, kb("f_30254783477.jpg", "out", "doc"), [rich("UNA LOCOMOTORA ENTERRADA: JUSTO SU TIPO DE MISTERIO", ("misterio",), 0.2, step=0.1, y=0.84, size=56,
                                                                maxw=0.85)], tex=CLEAN)
    add(673.20, kb("u_qMUTRo3jdnk.jpg", "in", "dark"), [Darken(0.35), BigText("«NIGHT PROBE»", "serif", 120, WHITE, (0.5, 0.46), w("night", 675.6) - 673.2, None, "pop"),
                                                       big("UNA NOVELA · 1981", w("publicada", 676.6) - 673.2, 0.62, 60, YELLOW)], tex=DARK)
    add(w("sobre un", 678.5), kb("u_KMTuxhsuJpo.jpg", "in", "dark"), [rich("UN TREN QUE DESAPARECE EN UN RÍO CON UN SECRETO A BORDO", ("secreto",), 0.1, step=0.09,
                                                                           y=0.84, size=54, maxw=0.88)], tex=DARK)
    add(681.90, kb("u_iQSpfpK4K_U.jpg", "in", "cold"), [big("Y QUISO BUSCARLA EN PERSONA", 0.2, 0.84, 66, YELLOW)], tex=CLEAN)
    add(684.40, kb("u_z9-01lfO2g8.jpg", "in", "cold"), [Badge("1981 · 1982", 0.2, None), big("EN 1981… Y OTRA VEZ EN 1982", 0.3, 0.84, 66)], tex=CLEAN)
    add(688.40, kb("u_brsP25BuajE.jpg", "out", "warm"), [big("CUSSLER Y SU HIJO DIRK", 0.1, 0.84, 66),
                                                       big("CON UN MAGNETÓMETRO", w("magnetómetro", 691.0) - 688.4, 0.12, 64, YELLOW)], tex=CLEAN)
    add(692.60, cus(G9.crossing, mode="magnet", t0=0.0), [big("UN DETECTOR DE METALES PARA COSAS ENORMES", w("algo", 696.9) - 692.6, 0.25, 54, YELLOW)],
        tr="fade", td=0.25, tex=GFX)
    add(699.80, kb("u_EF9irJtpquw.jpg", "in", "cold"), [Stamp("NADA CONCLUYENTE", 0.2, RED, (0.5, 0.5), -8, 110)], tex=CLEAN)
    add(701.80, kb("u_DkaYA17fu20.jpg", "in", "bw"), [big("LA ARENA NO SOLTABA SU SECRETO", 0.2, 0.84, 66)], tex=DARK)
    add(704.00, kb("u_k8dhUvoSbOs.jpg", "punch", "dark"), [big("VOLVER A LO GRANDE", 0.2, 0.84, 90, YELLOW, "pop")], tex=DARK)

    # ============================== CAP 6: LA GRAN BÚSQUEDA DE 1989 (706.9 - 819.4)
    bg, ov = chapter(6, "LA GRAN BÚSQUEDA", "u_Aqa6NwBxsgY.jpg", year="ENERO DE 1989")
    add(706.90, bg, ov, tr="black", td=0.2, tex=DARK)
    add(709.40, kb("u_Aqa6NwBxsgY.jpg", "in", "cold"), [big("NUMA ORGANIZA LA BÚSQUEDA MÁS GRANDE", 0.2, 0.84, 62, YELLOW)], tex=CLEAN)
    bg, ov = card([("DETRÁS ESTABA", 50, GREY_, 0.32, 0.1), ("CRAIG DIRGO", 150, WHITE, 0.5, 0.2),
                   ("RECIÉN LLEGADO COMO DIRECTOR DE NUMA", 50, YELLOW, 0.68, w("que acababa", 715.1) - 713.4)])
    add(713.40, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(717.10, V("10396", "u_kJTo5r1NuSE.jpg", 0.0, "warm"), [big("AÑOS DESPUÉS, COAUTOR DE CUSSLER", 0.2, 0.84, 64)], tex=CLEAN)
    add(720.90, kb("u_F8Iyt407ApM.jpg", "in", "cold"), [big("MEJOR DE LO QUE NADIE ESPERABA", 0.2, 0.84, 66)], tex=CLEAN)
    add(724.00, V("3406", "u_FQODry-m9Kc.jpg", 0.0, "cold"), [big("UN DÍA FRÍO DE INVIERNO", 0.1, 0.84, 70, BLUE)], tex=CLEAN)
    add(725.60, kb("u_zjrL-buRjD0.jpg", "out", "cold"), [Counter(0, 300, "+{:.0f}", "PERSONAS EN EL ARROYO", 0.2, 1.4, (0.5, 0.42), 200)], tex=CLEAN)
    add(728.20, kb("u_s59_0RyYuso.jpg", "in", "cold"), [big("EN CAMIONETAS", 0.1, 0.84, 80)], tex=CLEAN)
    add(729.70, kb("u_oz4vgWPI8Tc.jpg", "in", "warm"), [big("ABRIGOS · GORROS · TERMOS DE CAFÉ", 0.1, 0.84, 62)], tex=CLEAN)
    add(732.70, kb("u_-9Vhp1-osLo.jpg", "in", "cold"), [big("FAMILIAS · JUBILADOS · AFICIONADOS A LOS TRENES", 0.2, 0.84, 54)], tex=CLEAN)
    add(737.00, kb("u_5ucPWHPm_G4.jpg", "in", "cold"), [big("YA NO SENTÍAN LAS MANOS", 0.3, 0.84, 70, BLUE)], tex=CLEAN)
    add(741.10, cus(G9.numbers1989, times=[0.0, 0.2, 99, 99]), tr="fade", td=0.2, tex=GFX)
    add(744.70, V("5292", "u_qgJCTooDMns.jpg", 0.0, "dark"), [big("SEÑALES HACIA EL SUBSUELO", 0.1, 0.84, 66)], tex=DARK)
    add(748.80, cus(G9.numbers1989, times=[-1, -1, 0.2, 99]), [big("ESPERANDO UN AVISO", w("por si", 750.8) - 748.8, 0.85, 56, YELLOW)], tex=GFX)
    add(753.70, V("4462", "u_BeGRBsAISuw.jpg", 0.0, "doc"), [big("POR LA VÍA DE AL LADO, TRENES DE CARGA", 0.3, 0.84, 58)], tex=CLEAN)
    add(757.60, mp("kc_loc", [(0, -104.415, 39.754, 0.9), (3.9, -104.410, 39.753, 1.15)],
                   [dict(type="route", path=[(-104.60, 39.745), (-104.43, 39.757), (-104.41, 39.7527), (-104.30, 39.73)], t0=0.0, draw=0.1,
                         color=(150, 150, 170), width=2, traffic=2, speed=300),
                    dict(type="xmark", at="kc_cross", t0=0.3),
                    dict(type="label", at="kc_cross", text="AQUÍ CAYÓ LA 51", t0=0.6, dy=-120, size=54, box=True)]),
        [Badge("MÁS DE UN SIGLO DESPUÉS", 0.2, None)], tex=GFX)
    add(761.50, kb("u_mvgikzPvj14.jpg", "in", "cold"), [big("NADIE LEVANTABA LA VISTA", 0.1, 0.84, 66), big("TODOS MIRABAN LA ARENA", w("todos", 763.2) - 761.5,
                                                                                                             0.12, 64, YELLOW)], tex=CLEAN)
    add(764.80, kb("u_8Hjx3GNZYeA.jpg", "in", "doc"), [big("Y NO SOLO DESDE EL SUELO", 0.1, 0.84, 66), big("UN SATÉLITE DEL GOBIERNO", w("satélite", 769.0) - 764.8,
                                                                                                            0.12, 70, YELLOW)], tex=CLEAN)
    add(770.50, cus(G9.satellite, t0=0.0), tr="fade", td=0.25, tex=GFX)
    add(775.20, kb("u_vylRxokF76Y.jpg", "in", "warm"), [big("AL FINAL DEL DÍA: LO DE SIEMPRE", 0.2, 0.84, 66)], tex=CLEAN)
    add(778.80, kb("u_si1TVN_QCS0.jpg", "in", "warm"), [big("TROZOS SUELTOS DEL ACCIDENTE", 0.2, 0.84, 66)], tex=CLEAN)
    add(783.10, Solid("black"), [Stamp("LA LOCOMOTORA, NO", 0.1, RED, (0.5, 0.5), -8, 130)], tr="black", td=0.1, tex=DARK)
    add(785.00, kb("u_eLaCt0BRQvU.jpg", "punch", "bw"), [big("UN DETALLE QUE MUCHOS PASARON POR ALTO", 0.2, 0.84, 58)], tex=DARK)
    add(787.50, cus(G9.crossing, mode="magnet", t0=-1.0), [big("UN MAGNETÓMETRO LA HABRÍA NOTADO", w("y un", 790.0) - 787.5, 0.25, 56, YELLOW)],
        tr="fade", td=0.25, tex=GFX)
    add(794.70, cus(G9.reading, t0=0.1, ghost_t=1.0, years_t=[w("1981", 798.6) - 794.7, w("1982", 800.4) - 794.7, w("1989", 801.8) - 794.7]),
        tr="fade", td=0.25, tex=GFX)
    add(804.20, kb("u_IfHAeNOOGQ0.jpg", "in", "warm"), [rich("COMO SI NO HUBIERA NINGUNA LOCOMOTORA", ("ninguna",), 0.2, step=0.1, y=0.84, size=60, maxw=0.85)],
        tex=CLEAN)
    add(807.90, Solid("black"), [big("LA PREGUNTA CAMBIÓ", 0.1, 0.5, 120, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    bg, ov = card([("YA NO ERA: ¿DÓNDE ESTÁ ENTERRADA?", 66, GREY_, 0.38, 0.1),
                   ("SINO: ¿SE QUEDÓ ALGUNA VEZ ALLÍ?", 84, YELLOW, 0.58, w("era si", 811.9) - 809.9)])
    add(809.90, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(814.20, kb("u_DvQ3xYWObr8.jpg", "in", "bw"), [big("EN VEZ DE UNA PALA…", 0.2, 0.84, 70)], tex=DARK)
    add(816.90, kb("u_aT88kga0g_M.jpg", "in", "dark"), [big("…BUSCAR EN OTRO LUGAR", 0.1, 0.84, 72, YELLOW)], tex=DARK)

    # ============================== CAP 7: LOS PAPELES (819.4 - 944.9)
    bg, ov = chapter(7, "LOS PAPELES", "u_BgDf7_FFVhE.jpg", year="1997")
    add(819.40, bg, ov, tr="black", td=0.2, tex=DARK)
    bg, ov = card([("LLOYD GLASIER", 150, WHITE, 0.45, 0.1), ("HISTORIADOR DEL FERROCARRIL · DENVER", 54, YELLOW, 0.63, 0.5)])
    add(821.60, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(824.10, kb("u_ggeZ9oyI-PE.jpg", "in", "warm"), [big("LO QUE NADIE HABÍA HECHO EN UN SIGLO", 0.2, 0.84, 62)], tex=CLEAN)
    add(827.80, kb("w_kiowa_creek.jpg", "in", "bw"), [Stamp("NO FUE AL ARROYO", 0.1, RED, (0.5, 0.5), -8, 110)], tex=DARK)
    add(829.10, kb("u_aT88kga0g_M.jpg", "punch", "warm"), [big("FUE A LOS ARCHIVOS DEL FERROCARRIL", 0.1, 0.84, 64, YELLOW)], tex=DARK)
    add(830.60, kb("u_jv5gATbl2xo.jpg", "in", "warm"), [big("LOS LIBROS DE CADA LOCOMOTORA", 0.3, 0.84, 66)], tex=CLEAN)
    q2(835.10, badge="PREGUNTA 2 · LA RESPUESTA")
    add(841.10, cus(G9.ledger, mode="find", t0=0.0, notes_t=[w("se había desenterrado", 843.2) - 841.1, w("remolcado", 846.0) - 841.1, 99, 99]),
        tr="fade", td=0.3, tex=GFX)
    add(848.00, mp("kc_reg", [(0, -101.5, 39.0, 0.78), (3.0, -99.5, 39.0, 0.8)],
                   [dict(type="state", name="Kansas", t0=0.0, color=GREY_, width=3, alpha=0.6),
                    dict(type="rail", path=KP, t0=0.0, draw=0.1, color=(120, 120, 130), width=4),
                    dict(type="route", path=TOW, t0=0.1, draw=2.6, color=RED, width=7),
                    dict(type="pin", at="kc_cross", t0=0.0, label="KIOWA CREEK", side="l", box=True, size=38),
                    dict(type="pin", at="kansas_city", t0=2.4, label="KANSAS CITY", side="l", box=True, size=44)]),
        [big("CIENTOS DE MILLAS, A LA OTRA PUNTA DE KANSAS", 0.2, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(851.20, L("1s00005", kb("u_bhGuqye5Uwc.jpg", "in", "dark"), "Talleres del ferrocarril en Wyandotte (Kansas City), 1867 · " + LOC_),
        [big("EN LOS TALLERES: RECONSTRUIDA", w("la reconstruyeron", 853.4) - 851.2, 0.08, 58, YELLOW)], tex=ARCH)
    add(855.90, kb("u_RvcPDUMoqTE.jpg", "in", "warm"), [Badge("1997", 0.2, None), big("ANUARIO DEL MUSEO DEL FERROCARRIL DE COLORADO", w("en un", 858.6) - 855.9, 0.84,
                                                                                         52)], tex=CLEAN)
    bg, ov = card([("RECONSTRUCCIÓN TERMINADA EN", 50, GREY_, 0.28, 0.1), ("1880", 280, YELLOW, 0.5, 0.3),
                   ("MENOS DE DOS AÑOS DESPUÉS DE LA CRECIDA", 54, WHITE, 0.72, w("menos", 866.0) - 862.1)])
    add(862.10, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(868.50, cus(G9.rebuild, t0=-0.2, t1=0.6), tr="fade", td=0.25, tex=GFX)
    add(872.10, cus(G9.rebuild, t0=-5.0, t1=-4.0, num_t=w("1026", 876.6) - 872.1 - 0.4), [big("CUANDO LA UNION PACIFIC RENUMERÓ SUS MÁQUINAS", 0.2, 0.32, 52)],
        tex=GFX)
    add(878.90, fr("f_54567792007.jpg", "Locomotora de la época con más ruedas motrices · imagen de referencia", "bw"),
        [big("SIGUIÓ TRABAJANDO HASTA FINALES DE SIGLO", 0.2, 0.08, 58, YELLOW)], tex=ARCH)
    add(881.30, Solid("black"), [big("FÍJATE EN LO QUE SIGNIFICA", 0.1, 0.5, 96, WHITE, "pop")], tr="black", td=0.1, tex=DARK)
    add(883.30, cus(G9.two_lanes, t0=0.0, step=0.25, hl_t=w("la 51", 887.6) - 883.3), tr="fade", td=0.25, tex=GFX)
    add(891.60, kb("u_F8Iyt407ApM.jpg", "out", "cold"), [big("LA DE CUSSLER · LA DE LAS 300 PERSONAS", w("la de", 893.7) - 891.6, 0.84, 58)], tex=CLEAN)
    add(896.90, mp("kc_reg", [(0, -103.5, 39.3, 1.0), (3.2, -101.0, 39.0, 0.85)],
                   [dict(type="rail", path=KP, t0=0.0, draw=0.1, color=(120, 120, 130), width=4),
                    dict(type="route", path=TOW, t0=0.2, draw=3.0, color=YELLOW, width=6)]),
        [big("…SE HABÍA IDO DE ALLÍ EN TREN", 0.2, 0.1, 66, YELLOW)], tex=GFX)
    add(900.10, kb("u_dkt3FhN3utQ.jpg", "in", "warm"), [big("ARREGLAR UNA MÁQUINA: LO NORMAL", 0.2, 0.84, 64)], tex=CLEAN)
    add(903.60, kb("u_lXISATe1WBQ.jpg", "in", "dark"), [big("LO EXTRAÑO ERA LA FORMA", 0.1, 0.84, 66),
                                                       big("¿POR QUÉ DE NOCHE?", w("por qué", 905.1) - 903.6, 0.42, 84, YELLOW, "pop"),
                                                       big("¿POR QUÉ SIN QUE NADIE SE ENTERARA?", w("sin", 906.6) - 903.6, 0.58, 60, WHITE)], tex=DARK)
    add(908.10, kb("u_CDQ9CKvYreg.jpg", "in", "bw"), [Stamp("NINGÚN DOCUMENTO LO EXPLICA", 0.1, RED, (0.5, 0.5), -6, 90)], tex=DARK)
    add(909.80, V("18304", "u_jaHmB2Z996I.jpg", 2.0, "dark"), [big("CUSSLER TENÍA SU TEORÍA", 0.1, 0.84, 66),
                                                             big("¿UN FRAUDE AL SEGURO?", w("fraude", 913.0) - 909.8, 0.45, 96, YELLOW, "pop")], tex=DARK)
    add(914.50, cus(G9.theory, t0=0.0, step=1.5, deny_t=w("la compañía", 919.8) - 914.5), [big("Y HOY YA NO HAY A QUIÉN RECLAMAR", w("y hoy", 921.4) - 914.5, 0.92,
                                                                                               50, GREY_)], tr="fade", td=0.25, tex=GFX)
    add(923.60, Solid("black"), [big("HAY UN DATO MÁS", 0.1, 0.5, 110, WHITE, "pop")], tr="black", td=0.1, tex=DARK)
    add(925.00, cus(G9.merger, t0=0.0, join_t=w("se fusionó", 930.0) - 925.0, note_t=99), tr="fade", td=0.25, tex=GFX)
    add(933.80, kb("u_jv5gATbl2xo.jpg", "in", "warm"), [rich("UNA LOCOMOTORA DE MÁS O DE MENOS EN UNA LISTA…", ("lista",), 0.2, step=0.09, y=0.4, size=60,
                                                                maxw=0.85),
                                                       rich("…PODÍA PASAR SIN QUE NADIE PREGUNTARA", ("nadie",), w("podía", 938.2) - 933.8, step=0.09, y=0.6, size=60,
                                                            maxw=0.85)], tex=CLEAN)
    add(940.60, cus(G9.merger, t0=-9.0, join_t=-8.0, note_t=0.1), tex=GFX)

    # ============================== CAP 8: HOY (944.9 - 983.0)
    bg, ov = chapter(8, "HOY", "w_kiowa_creek.jpg", year="2026")
    add(944.90, bg, ov, tr="black", td=0.2, tex=DARK)
    add(948.70, kb("f_45193826691.jpg", "in", "doc"), [Badge("2026", 0.2, None), big("SIGUE AHÍ, SECO CASI TODO EL AÑO", w("seco", 952.3) - 948.7, 0.84, 62)],
        tex=CLEAN)
    add(953.90, V("4059", "u_Obpget_fY8U.jpg", 0.0, "dark"), [big("Y CAPAZ DE LO MISMO QUE EN 1878", 0.2, 0.84, 64, YELLOW)], tex=DARK)
    add(956.80, V("100351", "u_TByVnyEo-ao.jpg", 0.0, "doc"), [big("CADA PRIMAVERA, VUELVE A CORRER UNAS HORAS", 0.3, 0.84, 58)], tex=CLEAN)
    add(961.70, kb("u_zBHU08hdzhY.jpg", "in", "doc"), [big("YA NO ES UN PUÑADO DE CASAS", 0.2, 0.84, 66)], tex=CLEAN)
    add(964.20, cus(G9.count_up, value=2900, t0=0.4), tr="fade", td=0.2, tex=GFX)
    add(968.10, kb("u_9ks9RfEQZHk.jpg", "in", "doc"), [big("Y NO DEJA DE CRECER", 0.2, 0.84, 70)], tex=CLEAN)
    add(970.50, mp("kc_loc", [(0, -104.43, 39.755, 0.7), (4.8, -104.41, 39.753, 0.9)],
                   [dict(type="route", path=[(-104.60, 39.745), (-104.43, 39.757), (-104.41, 39.7527), (-104.30, 39.73)], t0=0.0, draw=0.1,
                         color=(170, 170, 190), width=2, traffic=3, speed=280),
                    dict(type="pin", at="kc_cross", t0=0.4, label="EL MISMO LUGAR DE ENTONCES", side="r", box=True, size=48)]),
        [big("LOS TRENES DE LA UNION PACIFIC SIGUEN CRUZANDO", 0.2, 0.1, 54)], tex=GFX)
    add(975.30, V("52025", "u_mR2UetL_tzU.jpg", 0.0, "doc"), [big("LA AUTOPISTA I-70", 0.2, 0.84, 80, YELLOW)], tex=CLEAN)
    add(978.10, kb("u_z-JZMtEabzY.jpg", "in", "doc"), [big("MILES DE AUTOS AL DÍA", 0.1, 0.84, 66, t1=w("sin", 980.7) - 978.1 - 0.3),
                                                     big("SIN SABER LO QUE SE BUSCÓ DEBAJO", w("sin", 980.7) - 978.1, 0.84, 62, YELLOW)], tex=CLEAN)

    # ============================== CONCLUSIÓN (983.0 - end)
    q1(983.00, badge="DE VUELTA A LA PREGUNTA 1")
    add(991.40, kb("u_2jPwtG5cZOA.jpg", "punch", "dark"), [big("BUSCABAN EN EL LUGAR EQUIVOCADO", 0.1, 0.5, 92, YELLOW, "pop")], tr="flash", td=0.2, tex=DARK)
    add(993.70, cus(G9.two_places, t0=0.1, t1=w("estuvo", 996.6) - 993.7), [big("GUARDADO EN UN ARCHIVO, ESPERANDO A QUE ALGUIEN LO ABRIERA",
                                                                               w("guardado", 999.3) - 993.7, 0.88, 50, WHITE)], tr="fade", td=0.25, tex=GFX)
    add(1002.80, kb("u_IzLWSbMoCPo.jpg", "in", "dark"), [big("UNA LOCOMOTORA TRAGADA POR LA ARENA…", 0.1, 0.84, 62)], tex=DARK)
    add(1005.40, kb("u_jv5gATbl2xo.jpg", "punch", "warm"), [big("…ES MÁS BONITA QUE UNA LÍNEA EN UN REGISTRO", 0.1, 0.84, 58, YELLOW)], tex=CLEAN)
    add(1008.60, kb("u_XVYleJiw_As.jpg", "in", "dark"), [big("LOS PERIÓDICOS LA REPITIERON", 0.1, 0.84, 66)], tex=ARCH)
    add(1010.30, V("10396", "u_d34DtRp1bqo.jpg", 0.0, "warm"), [big("UN NOVELISTA LA HIZO LIBRO", 0.1, 0.84, 66)], tex=CLEAN)
    add(1011.90, kb("u_FNZwttoLRSU.jpg", "in", "dark"), [big("CADA CRECIDA, MÁS MISTERIO", 0.1, 0.84, 70)], tex=DARK)
    add(1014.90, Solid("black"), [big("NADIE QUERÍA UNA RESPUESTA ABURRIDA", 0.1, 0.5, 90, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(1017.00, kb("u_ggeZ9oyI-PE.jpg", "in", "dark"), [big("NADIE FUE AL ÚNICO LUGAR DONDE ESTABA", 0.2, 0.84, 60)], tex=DARK)
    add(1020.40, kb("u_B-JJxUzeX3M.jpg", "in", "dark"), [rich("MÁS DE UN SIGLO CAVANDO CON PALAS LO QUE ESTABA ESCRITO EN UN PAPEL", ("papel",), 0.1, step=0.08,
                                                              y=0.5, size=64, maxw=0.85)], tex=DARK)
    add(1024.50, V("1594", "u_ZRJurausAc0.jpg", 0.0, "warm"), [big("PERO ALGO SIGUE PERDIDO", 0.1, 0.84, 72),
                                                        big("Y NO ES LA LOCOMOTORA", w("y no", 1027.7) - 1024.5, 0.12, 70, YELLOW)], tex=CLEAN)
    add(1029.50, cus(G9.names3, t0=0.2, step=0.7, end_t=w("nadie", 1036.4) - 1029.5), tr="fade", td=0.3, tex=DARK)
    add(1038.90, V("3458", "u_lXISATe1WBQ.jpg", 3.0, "dark"), [big("NI SI SUS FAMILIAS PUDIERON DESPEDIRSE", 0.1, 0.84, 60)], tex=DARK)
    add(1041.70, fr("f_54522621773.jpg", None, "bw"), [big("LA MÁQUINA VOLVIÓ AL TRABAJO", 0.1, 0.1, 66)], tex=ARCH)
    add(1043.50, Solid("black"), [big("LOS HOMBRES NO VOLVIERON A CASA", 0.1, 0.5, 96, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(1045.60, kb("u_rNxfMnfnenE.jpg", "out", "bw"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿HAY EN TU FAMILIA UNA HISTORIA QUE TODOS",
                                 line2="DAN POR CIERTA Y NADIE HA COMPROBADO?", cta="CUÉNTALA EN LOS COMENTARIOS"),
         rich("A veces la respuesta está en un cajón, no en la arena", ("cajón",), w("a veces", 1058.2) - 1045.6 - 0.3, step=0.08, y=0.2, size=50, maxw=0.85)],
        tex=DARK)
    return S
