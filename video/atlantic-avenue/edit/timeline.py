"""The edit: every shot of the Atlantic Avenue video, synced to the voice-over."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx6 as G6
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still)
from render import Shot
import words

TOTAL = 1145.23
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
GREEN = (60, 170, 90)
IMG = os.path.join(ROOT, "assets", "img")


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


def cus(fn, **kw):
    return Custom(fn, **kw)


def warp(fn, a, b, **kw):
    return Custom(lambda t, d: fn(a + b * t, d, **kw))


def chapter(num, title, bg, g="dark", year=None, base=None):
    ovs = [Darken(0.5, 0.0, 0.3),
           BigText(f"CAPÍTULO {num}" + (f"  ·  {year}" if year else ""), "bebas", 46, YELLOW, (0.5, 0.40), 0.1, None, "up", tracking=6),
           BigText(title, "serif", 100, WHITE, (0.5, 0.52), 0.25, None, "up"),
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
        k = wd.strip("¿?,.:«»").lower()
        out.append((wd, t, "h" if k in hl else ("r" if k in red else "n")))
        t += step
    return Rich(out, 0.5, y, maxw, size)


def big(text, t0=0.2, y=0.82, size=66, col=WHITE, anim="up"):
    return BigText(text, "bebas", size, col, (0.5, y), t0, None, anim, tracking=4)


def torch(path=((0.3, 0.55), (0.7, 0.45)), r=440, t0=0.0, amb=0.13):
    return FnOverlay(G5.flashlight, path=path, r=r, t0=t0, amb=amb)


def postshake(amt):
    def f(img, t, dur):
        return G2.shake_frame(img, t, amt)
    return f


def mp(name, cams, layers, title=None):
    return M.MapScene(name, cams, layers, title)


AVENUE = ["furman", "columbia", "hicks", "henry", "clinton", "court", "boerum", "smith", "bond", "flatbush"]
TUNNEL = ["columbia", "hicks", "henry", "clinton", "court", "boerum"]
LIRR_1844 = ["pier_bk", "court", "flatbush", "east_ny", "jamaica", "hicksville", "ronkonkoma", "riverhead", "greenport"]
SOUND = ["greenport", (-72.15, 41.20), "stonington"]
TO_BOSTON = ["stonington", "providence", "boston"]
SHORE_1848 = ["manhattan", (-73.62, 41.00), "bridgeport", "new_haven", "hartford", "springfield", "worcester", "boston"]
LIRR_TODAY = ["flatbush", (-73.946, 40.680), "east_ny", (-73.866, 40.690)]

RUMORS = [(0.0, "1916", "BOMBAS", 380, 330), (0.0, "AÑOS 20", "HONGOS · WHISKY", 960, 300), (0.0, "1936", "UN CADÁVER", 1540, 360),
          (0.0, "AÑOS 50", "DOS HISTORIADORES", 640, 760), (0.0, "1861", "¿UNA LOCOMOTORA?", 1300, 780)]


def rumors(times):
    return [(t,) + c[1:] for t, c in zip(times, RUMORS)]


# ------------------------------------------------------------------ the edit
def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="u_8rZ0VKNbfiY.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Cómo pierde Nueva York un túnel de tren entero bajo una de sus avenidas?", ("pierde",), size=68),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_at22jGn2ZHs.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Por qué hoy, después de que miles de personas bajaran por esa alcantarilla, ya no puede entrar nadie?",
                     ("nadie",), size=64), tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 67.2)
    add(0.0, kb("f_4323697878.jpg", "in", "none"), [torch(((0.25, 0.55), (0.55, 0.5)), r=420, amb=0.1),
                                                  Badge("BROOKLYN · NUEVA YORK", 0.8, 3.0)], tex=DARK)
    add(w("linterna", 3.4) - 0.3, kb("f_4322963019.jpg", "up", "none"), [torch(((0.2, 0.7), (0.8, 0.3)), r=460, amb=0.1)], tr="fade", td=0.4, tex=DARK)
    add(w("pierde", 7.6) - 0.4, kb("f_3864042152.jpg", "in", "none"), [torch(((0.35, 0.5), (0.65, 0.5)), r=480, amb=0.12)], tex=DARK)
    add(w("alta", 10.2) - 0.2, kb("f_4323703228.jpg", "in", "doc"), [big("ALTA COMO UNA CASA DE DOS PISOS", 0.3, 0.84, 62)], tex=CLEAN)
    add(w("retumba", 13.5) - 0.9, kb("f_4322959359.jpg", "punch", "dark"), [Flash(0.8, 0.2, (255, 255, 255), 0.6)], tex=DARK, post=postshake(7))
    add(w("encima", 14.8) - 0.1, kb("u_hxNW53TdOro.jpg", "in", "dark"), [rich("A POCAS PIES, ACABA DE FRENAR UN AUTOBÚS", ("autobús",), 0.3, y=0.84, size=54, maxw=0.8)],
        tex=DARK, post=postshake(2))
    add(17.10, mp("aa_nyc", [(0, -73.98, 40.70, 0.32), (3.0, -73.993, 40.690, 0.62)],
                  [dict(type="label", at=(-73.975, 40.645), text="BROOKLYN", t0=0.3, size=64),
                   dict(type="label", at=(-73.99, 40.765), text="MANHATTAN", t0=0.5, size=54),
                   dict(type="route", path=AVENUE, t0=1.2, draw=1.4, color=YELLOW, width=7, smooth=False),
                   dict(type="pin", at="court", t0=2.4, label="ATLANTIC AVENUE", side="r", box=True, size=46)]),
        tr="zoom", td=0.35, tex=GFX)
    add(w("avenidas", 22.6) - 0.4, kb("u_Rv9Dc_O-kqk.jpg", "in", "doc"), [rich("UNA DE LAS AVENIDAS CON MÁS TRÁFICO DE NUEVA YORK", ("tráfico",), 0.2, y=0.84, size=52, maxw=0.8)],
        tr="whip_l", td=0.25, tex=CLEAN)
    add(w("cavaron", 25.6) - 0.2, warp(G6.london, 0.0, 1.0), tr="fade", td=0.3, tex=GFX)
    add(w("oscuras", 31.6) - 0.6, kb("u_at22jGn2ZHs.jpg", "in", "dark"), [big("A OSCURAS DESDE 1861", 0.4, 0.5, 96, YELLOW, "pop")], tr="fade", td=0.4, tex=DARK)
    add(34.76, kb("f_4323701866.jpg", "in", "none"), [torch(((0.3, 0.5), (0.65, 0.5)), r=480, amb=0.12),
                                                     rich("UNA PARED QUE NADIE HA PODIDO ABRIR", ("nadie",), 1.0, y=0.84, size=56)], tex=DARK)
    add(w("unica", 38.0) - 0.2, kb("f_3863966838.jpg", "in", "doc"), [Callout(1000, 760, 1300, 360, "LA ÚNICA ENTRADA", 1.4)], tex=CLEAN)
    add(w("durante", 42.6) - 0.2, kb("u_a1Ih1k2H-AA.jpg", "punch", "doc"), [Counter(0, 120, "{:.0f} AÑOS", "SIN QUE NADIE SUPIERA CUÁL ERA", 0.2, 1.2, (0.5, 0.45), 170)],
        tex=CLEAN)
    add(w("hasta", 45.5) - 0.1, kb("f_4323692534.jpg", "in", "doc"), [rich("HASTA QUE UN JOVEN DE 20 AÑOS BAJÓ POR ELLA", ("20",), 0.2, y=0.86, size=52, maxw=0.8)],
        tr="whip_l", td=0.25, tex=CLEAN)
    add(48.58, kb("u_dnnBNxq51wg.jpg", "in", "warm"), [rich("UNA CIUDAD PUEDE OLVIDAR CASI CUALQUIER COSA", ("olvidar",), 0.3, y=0.84, size=54, maxw=0.8)],
        tr="fade", td=0.4, tex=CLEAN)
    add(w("raro", 51.9) - 0.2, kb("u_nXguHgL22ag.jpg", "down", "doc"), [rich("LO RARO ES OLVIDAR LO QUE TIENE DEBAJO DE LOS PIES", ("debajo",), 0.3, y=0.84, size=52, maxw=0.8)],
        tex=CLEAN)
    q1(55.28)
    q2(w("por", 60.0) - 0.2)
    # title sting
    add(66.4, kb("f_4267479707.jpg", "in", "none"),
        [Darken(0.45, 0.0, 0.3), torch(((0.4, 0.5), (0.6, 0.5)), r=620, amb=0.25),
         BigText("ATLANTIC AVENUE", "bebas", 180, YELLOW, (0.5, 0.40), 0.1, None, "pop", tracking=10),
         BigText("El túnel que Nueva York perdió", "serif_it", 70, WHITE, (0.5, 0.58), 0.45, None, "up"),
         Badge("CAPÍTULO 1 · UNA CALLE CON LOCOMOTORAS", 1.0, None)], tr="flash", td=0.25, tex=DARK)

    # ============================== CAP 1: UNA CALLE CON LOCOMOTORAS (67.2 - 207.7)
    add(71.10, fr("l_05840.jpg", "Brooklyn visto desde Trinity Church, Nueva York · 1853"), [Badge("DÉCADA DE 1840 · ATLANTIC STREET", 0.3, None)],
        tr="fade", td=0.4, tex=ARCH)
    add(w("manhattan", 76.3) - 0.5, mp("aa_nyc", [(0, -73.995, 40.70, 0.55), (4.0, -74.0, 40.695, 0.85)],
                                       [dict(type="label", at=(-73.985, 40.678), text="BROOKLYN", t0=0.2, size=58),
                                        dict(type="label", at=(-74.012, 40.716), text="MANHATTAN", t0=0.4, size=52),
                                        dict(type="label", at=(-73.996, 40.705), text="EAST RIVER", t0=0.8, size=40, color=(150, 190, 230)),
                                        dict(type="route", path=["pier_bk", (-74.006, 40.697), "whitehall"], t0=1.4, draw=1.4, color=WHITE, width=4, dash=14),
                                        dict(type="pin", at="pier_bk", t0=1.0, label="SOUTH FERRY", side="l", size=40)]),
        tr="zoom", td=0.3, tex=GFX)
    add(79.92, kb("u_QZilFMg8NEs.jpg", "in", "warm"), [rich("UN PROBLEMA QUE HOY SUENA A CHISTE", ("chiste",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(w("medio", 83.6) - 0.4, warp(G6.street_train, 0.5, 1.0, mode="street"), [big("POR EL MEDIO PASABA EL TREN", 0.2, 0.07, 54, YELLOW)], tr="whip_l", td=0.25, tex=GFX)
    add(w("desde", 85.6) - 0.2, fr("l_3a32457.jpg", "South Ferry, Brooklyn · 1840"), [Badge("DESDE 1836 · LONG ISLAND RAIL ROAD", 0.3, None)], tex=ARCH)
    add(w("barco", 92.6) - 0.8, fr("l_12785.jpg", "Brooklyn Ferry · grabado del siglo XIX"), [rich("EL BARCO HACIA MANHATTAN", ("manhattan",), 0.2, y=0.065, size=50)], tex=ARCH)
    add(95.22, kb("u_IubvO9kt9fk.jpg", "in", "warm"), [rich("NI ANDÉN NI BARRERA", ("andén", "barrera"), 0.2, y=0.84, size=62)], tex=CLEAN)
    add(w("via", 97.3) - 0.2, fr("l_3a12536.jpg", "«Governor's race in New Jersey» · caricatura de 1844"), [rich("ENTRE LAS CASAS, LOS CARRUAJES Y LOS VECINOS", ("vecinos",), 0.4, y=0.065, size=46, maxw=0.85)],
        tex=ARCH)
    add(w("reglas", 104.4) - 1.4, kb("u_Y373lwUrS7U.jpg", "in", "warm"), [big("SE PUSIERON REGLAS", 0.3, 0.84, 70, YELLOW)], tex=CLEAN)
    add(105.28, warp(G6.street_train, 0.0, 1.0, mode="street"), tr="fade", td=0.3, tex=GFX)
    add(114.28, fr("l_13155.jpg", "«Get off the track!» · partitura con locomotora, 1844"), [Stamp("PROHIBIDO EL SILBATO", 0.6, RED, (0.5, 0.5), -10, 96)], tex=ARCH)
    add(w("tapaban", 117.2) - 0.3, warp(G6.street_train, 0.0, 1.0, mode="box"), tr="whip_l", td=0.25, tex=GFX)
    add(122.48, kb("u_Rd-Nxg7Zd4I.jpg", "punch", "dark"), [big("AUN ASÍ, HUBO ATROPELLOS", 0.3, 0.84, 66, RED, "pop")], tex=DARK, post=postshake(3))
    add(w("cargado", 125.0) - 0.4, warp(G6.street_train, 0.0, 0.8, mode="brake"), [rich("Y EN UNA CALLE LLENA DE GENTE, ESO ES MUCHA CALLE", ("mucha",), w("calle", 128.6) - 124.6, y=0.92, size=46, maxw=0.85)],
        tr="fade", td=0.3, tex=GFX)
    add(133.14, kb("u_LRblyGXwxMY.jpg", "in", "warm"), [rich("LO QUE LLEVABAN ESOS VAGONES ERA ABONO", ("abono",), 0.4, y=0.84, size=56)], tex=CLEAN)
    add(w("basura", 136.7) - 0.2, kb("u_6tLMrDA1-Fs.jpg", "in", "bw"), [rich("BASURA DE LAS CALLES · POLVO DE LAS LETRINAS", ("letrinas",), 0.2, y=0.84, size=52, maxw=0.85)], tex=ARCH)
    add(143.26, kb("u_7KDqzUW3MI4.jpg", "in", "warm"), [rich("IMAGÍNATE ABRIR LA VENTANA DE TU CASA…", ("ventana",), 0.2, y=0.84, size=56)], tr="fade", td=0.3, tex=CLEAN)
    add(w("salida", 147.6) - 0.3, fr("l_51468.jpg", "City Hall de Brooklyn · 1863"), [big("LA SALIDA FUE UN TRATO", 0.2, 0.065, 64, YELLOW)], tex=ARCH)
    add(150.00, mp("aa_loc", [(0, -73.993, 40.6895, 0.42), (6.0, -73.996, 40.6905, 0.55)],
                   [dict(type="route", path=AVENUE[:7], t0=0.3, draw=1.4, color=(150, 150, 150), width=10, smooth=False),
                    dict(type="label", at=(-73.9935, 40.6878), text="ATLANTIC STREET", t0=0.5, size=46),
                    dict(type="route", path=TUNNEL, t0=1.6, draw=1.8, color=YELLOW, width=8, smooth=False, dash=18),
                    dict(type="label", at=(-73.994, 40.6915), text="EL TREN, POR DEBAJO", t0=2.2, size=44, color=YELLOW),
                    dict(type="route", path=["columbia", "furman", "pier_bk"], t0=4.2, draw=1.0, color=WHITE, width=6, smooth=False),
                    dict(type="pin", at="pier_bk", t0=5.0, label="HASTA EL AGUA", side="l", box=True, size=42)]),
        tr="zoom", td=0.3, tex=GFX)
    add(157.24, cus(G6.cut_cover, mode="dig"), tr="fade", td=0.3, tex=GFX)
    add(165.48, kb("u_B-JJxUzeX3M.jpg", "in", "warm"), [rich("SOBRE TODO OBREROS IRLANDESES", ("irlandeses",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(w("pico", 168.4) - 0.3, kb("u_KluCioF4FYc.jpg", "punch", "dark"), [big("A PICO Y PALA", 0.0, 0.84, 76, YELLOW, "pop")], tex=DARK, post=postshake(2))
    add(170.10, cus(G6.cut_cover, mode="build"), tr="fade", td=0.3, tex=GFX)
    add(177.12, cus(G6.avenue_profile, mode="open"), tr="fade", td=0.3, tex=GFX)
    add(w("media", 185.6) - 0.1, mp("aa_loc", [(0, -73.9952, 40.6904, 0.62), (6.0, -73.9952, 40.6904, 0.7)],
                                    [dict(type="route", path=TUNNEL, t0=0.2, draw=1.6, color=YELLOW, width=12, smooth=False),
                                     dict(type="label", at=(-73.9952, 40.6885), text="≈ 2.500 PIES · MÁS DE 750 M", t0=1.6, size=52, box=True),
                                     dict(type="label", at=(-73.9995, 40.6927), text="COLUMBIA ST", t0=0.6, size=34),
                                     dict(type="label", at=(-73.9905, 40.6900), text="BOERUM PL", t0=0.9, size=34)]),
        tr="zoom", td=0.3, tex=GFX)
    add(w("metro", 193.9) - 1.0, kb("f_3864042152.jpg", "in", "doc"), [rich("EL TÚNEL DE METRO MÁS VIEJO DEL MUNDO", ("viejo",), 0.4, y=0.84, size=58)], tr="fade", td=0.3, tex=CLEAN)
    add(w("cara", 197.1) - 0.6, kb("f_4322962651.jpg", "l", "doc"), [rich("CARA · MODERNA · PENSADA PARA DURAR", ("durar",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(201.02, mp("aa_ne", [(0, -73.6, 41.2, 0.55), (5.5, -72.5, 41.55, 0.62)],
                   [dict(type="pin", at="pier_bk", t0=0.3, label="BROOKLYN", side="l", size=40),
                    dict(type="route", path=["pier_bk", "boston"], t0=1.0, draw=1.8, color=WHITE, width=4, dash=16),
                    dict(type="pin", at="boston", t0=2.6, label="BOSTON", side="r", box=True, size=46),
                    dict(type="label", at=(-72.6, 41.95), text="≈ 200 MILLAS · +300 KM", t0=3.0, size=44, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)

    # ============================== CAP 2: EL VIAJE QUE NO DURÓ (207.7 - 404.2)
    bg, ov = chapter(2, "El viaje que no duró", None, year="1844–1861", base=fr("l_03789.jpg"))
    add(207.70, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(w("noche", 211.0) - 0.4, fr("l_13380.jpg", "Saliendo de Boston en el vapor Cambria · 1846"), [rich("UNA NOCHE DE BARCO O UN ROSARIO DE TRANSBORDOS", ("transbordos",), 0.3, y=0.065, size=46, maxw=0.85)],
        tex=ARCH)
    add(214.18, fr("l_02955.jpg", "Tren de vapor, grabado de 1831"), [big("EN UN SOLO DÍA", 0.6, 0.065, 70, YELLOW)], tex=ARCH)
    add(w("tren", 217.6) - 0.3, mp("aa_ne", [(0, -73.4, 40.95, 0.55), (8.5, -72.6, 41.15, 0.72), (13.5, -71.8, 41.6, 0.6)],
                                  [dict(type="route", path=LIRR_1844, t0=0.2, draw=3.4, color=YELLOW, width=6, smooth=True),
                                   dict(type="label", at=(-73.25, 41.07), text="95 MILLAS · +150 KM", t0=2.4, size=46, color=YELLOW),
                                   dict(type="pin", at="greenport", t0=3.6, label="GREENPORT", side="b", size=40),
                                   dict(type="route", path=SOUND, t0=w("barco", 226.9) - 217.3, draw=1.6, color=WHITE, width=5, dash=14),
                                   dict(type="pin", at="stonington", t0=w("stonington", 227.9) - 217.3, label="STONINGTON", side="r", size=40),
                                   dict(type="route", path=TO_BOSTON, t0=w("otro", 229.6) - 217.3, draw=1.6, color=YELLOW, width=6, smooth=True),
                                   dict(type="pin", at="boston", t0=w("boston", 230.5) - 217.3 + 0.6, label="BOSTON", side="r", box=True, size=44)]),
        tr="zoom", td=0.3, tex=GFX)
    add(232.10, fr("l_3b05374.jpg", "Locomotora, 1851"), [Badge("VERANO DE 1844", 0.3, None),
                                                          rich("EL TÚNEL ERA SU PUERTA DE SALIDA", ("puerta",), w("tunel", 235.8) - 232.1, y=0.065, size=52)], tex=ARCH)
    add(239.62, kb("u_RSO-EI5bHT4.jpg", "in", "warm"), [big("EL NEGOCIO DURÓ UN SUSPIRO", 0.2, 0.84, 66, YELLOW)], tex=CLEAN)
    add(w("otros", 241.6) - 0.2, kb("u_tokoLFH-3Wk.jpg", "in", "doc"), [rich("OTROS BARCOS Y OTRAS LÍNEAS", ("barcos", "líneas"), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(246.30, mp("aa_ne", [(0, -72.6, 41.55, 0.55), (8.0, -72.3, 41.6, 0.58)],
                   [dict(type="route", path=LIRR_1844 + SOUND[1:] + TO_BOSTON[1:], t0=0.0, draw=0.1, color=(120, 120, 120), width=5, smooth=True),
                    dict(type="route", path=SHORE_1848, t0=0.6, draw=3.0, color=WHITE, width=7, smooth=True),
                    dict(type="label", at=(-72.95, 41.95), text="DICIEMBRE DE 1848: TODO EN TREN", t0=2.4, size=46, box=True),
                    dict(type="xmark", at="greenport", t0=w("quiebra", 260.2) - 246.3 - 0.4, size=40),
                    dict(type="label", at=(-72.55, 40.85), text="EL ATAJO, SIN SENTIDO", t0=w("atajo", 255.2) - 246.3, size=44, color=RED)]),
        tr="fade", td=0.3, tex=GFX)
    add(w("quiebra", 260.2) - 0.7, kb("u_TdNLjGXVH3s.jpg", "in", "dark"), [Stamp("QUIEBRA", 0.3, RED, (0.5, 0.5), -10, 150)], tex=DARK)
    add(261.96, fr("l_58225.jpg", "Taller de carpintería de Walt Whitman, Cumberland Street, cerca de Atlantic · 1852"),
        [rich("ARRIBA, EN LA CALLE, EMPEZABA OTRA GUERRA", ("guerra",), 0.6, y=0.065, size=50, maxw=0.85)], tr="fade", td=0.3, tex=ARCH)
    add(266.40, Split([kb("l_3a34140.jpg", "in", "archival"), kb("u_YbZtSVIbWTM.jpg", "in", "warm")], labels=["LA COMPAÑÍA", "LOS VECINOS"]), tex=ARCH)
    add(271.06, kb("u_7KDqzUW3MI4.jpg", "l", "warm"), [rich("HARTOS DEL HUMO, LA CENIZA Y EL RUIDO", ("humo", "ceniza", "ruido"), 0.6, y=0.84, size=56)], tex=CLEAN)
    add(277.12, kb("u_6e_uBz9txLk.jpg", "in", "bw"), [rich("SUS CASAS NUNCA VALDRÍAN LO QUE PODÍAN VALER", ("valer",), 0.3, y=0.84, size=52, maxw=0.8)], tex=ARCH)
    add(282.40, fr("l_51469.jpg", "City Hall, Brooklyn · 1863"), [Badge("1850", 0.2, None), Stamp("PROHIBIDO EL VAPOR", 0.9, RED, (0.5, 0.5), -10, 100)], tex=ARCH)
    add(286.44, kb("u_veNb0DDegzE.jpg", "punch", "doc"), [big("LOS TRIBUNALES", 0.2, 0.84, 70)], tex=CLEAN)
    add(w("albany", 288.6) - 0.6, kb("l_1s14037_L.jpg", "in", "archival"), [LowerThird("ALBANY", "La capital del estado · el Senado hacia 1860", 0.3)], tex=ARCH)
    add(291.26, kb("u_0ezHc4mqnGk.jpg", "in", "warm"), [Badge("1853", 0.2, None), big("PARECIÓ RESUELTO", 0.4, 0.84, 70)], tr="fade", td=0.3, tex=CLEAN)
    add(295.20, mp("aa_loc", [(0, -73.990, 40.6885, 0.42), (4.6, -73.988, 40.6878, 0.48)],
                   [dict(type="route", path=AVENUE, t0=0.2, draw=1.6, color=YELLOW, width=16, smooth=False),
                    dict(type="label", at=(-73.986, 40.6858), text="LA ACTUAL ATLANTIC AVENUE", t0=1.0, size=50, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(299.94, fr("l_04738.jpg", "Frente de una locomotora de vapor"), [Badge("UNA LEY GARANTIZABA EL VAPOR", 0.3, None)], tex=ARCH)
    add(303.60, Solid("black"), [big("DURÓ POCO", 0.0, 0.5, 120, RED, "pop")], tr="flash", td=0.15, tex=DARK)
    add(304.60, fr("l_3a12920.jpg", "«The telegraphic candidates» · caricatura de 1848"), [rich("ESPECULADORES DE TERRENOS", ("especuladores",), w("especuladores", 307.4) - 304.6, y=0.065, size=56)],
        tex=ARCH)
    add(311.12, kb("u_dKSHk0Jvs4g.jpg", "in", "warm"), [Badge("1859", 0.2, None), rich("CERRAR EL TÚNEL · VAGONES CON CABALLOS", ("cerrar", "caballos"), 0.6, y=0.84, size=54, maxw=0.8)],
        tex=CLEAN)
    add(317.80, mp("aa_nyc", [(0, -73.985, 40.705, 0.6), (6.0, -73.975, 40.715, 0.66)],
                   [dict(type="pin", at="pier_bk", t0=0.2, label="ATLANTIC", side="l", size=40),
                    dict(type="route", path=["pier_bk", (-73.975, 40.705), (-73.96, 40.725), "hunters_point"], t0=1.0, draw=2.0, color=YELLOW, width=6),
                    dict(type="pin", at="hunters_point", t0=2.6, label="HUNTERS POINT · QUEENS", side="r", box=True, size=42),
                    dict(type="label", at=(-73.995, 40.735), text="MAYO DE 1861", t0=0.6, size=50)]),
        tr="zoom", td=0.3, tex=GFX)
    add(325.96, kb("u_rdJXICdRVaQ.jpg", "in", "warm"), [Badge("OTOÑO DE 1861", 0.2, None), rich("PONTE EN UNA DE ESAS CASAS", ("casas",), 0.6, y=0.84, size=56)], tr="fade", td=0.4, tex=CLEAN)
    add(331.34, kb("u_miwPN1DVs-0.jpg", "in", "dark"), [rich("HACE MESES QUE NO PASA UN TREN", ("tren",), 0.2, y=0.84, size=56)], tex=DARK)
    add(333.74, fr("f_3626355415.jpg", "Una carretilla dentro del túnel · foto: Justin Kerr Sheckler (CC BY 2.0)", g="doc"),
        [rich("CARRETILLAS DE TIERRA Y LADRILLO", ("tierra", "ladrillo"), 0.3, y=0.065, size=52)], tex=CLEAN)
    add(337.16, warp(G6.avenue_profile, 0.0, 0.32, mode="seal"), tr="fade", td=0.3, tex=GFX)
    add(340.82, kb("u_7KDqzUW3MI4.jpg", "in", "warm"), [rich("LA OBRA LA PAGAN LOS DUEÑOS… Y TÚ ERES UNO DE ELLOS", ("tú",), 0.2, y=0.84, size=50, maxw=0.85)], tex=CLEAN)
    add(344.40, kb("u_4yCXNMLP9g8.jpg", "in", "doc"), [rich("¿RELLENARLO ENTERO?", ("entero",), 0.4, y=0.84, size=64)], tex=CLEAN)
    add(350.04, Solid("black"), [big("NI HABLAR", 0.0, 0.5, 150, YELLOW, "pop")], tr="flash", td=0.15, tex=DARK)
    add(351.24, warp(G6.avenue_profile, 0.0, 0.42, mode="seal"), tr="fade", td=0.25, tex=GFX)
    add(362.10, kb("f_4323703228.jpg", "in", "doc"), [big("NADIE LO DESTRUYÓ", 0.1, 0.84, 72, YELLOW)], tex=CLEAN)
    add(363.74, kb("f_4267479707.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=560, amb=0.2),
                                                      rich("POR ESO EL TÚNEL EXISTE TODAVÍA", ("todavía",), 0.8, y=0.84, size=56)], tex=DARK)
    add(368.34, kb("u_Rd-Nxg7Zd4I.jpg", "in", "dark"), [rich("UNA LEYENDA: SE HABÍA QUEDADO DENTRO UNA LOCOMOTORA", ("locomotora",), 0.6, y=0.84, size=50, maxw=0.85)],
        tr="fade", td=0.4, tex=DARK)
    add(375.70, kb("u_CgXwuXIdQic.jpg", "punch", "dark"), [Stamp("GUARDA ESTA LEYENDA", 0.3, YELLOW, (0.5, 0.5), -8, 90)], tex=DARK)
    add(378.34, fr("l_17382.jpg", "Walt Whitman en 1854"), [Badge("BROOKLYN STANDARD", 0.3, None),
                                                            rich("UN PERIODISTA DE BROOKLYN", ("periodista",), 0.6, y=0.065, size=52)], tex=ARCH)
    add(383.74, kb("u_at22jGn2ZHs.jpg", "in", "dark"), [rich("«OSCURO COMO LA TUMBA, FRÍO, HÚMEDO Y SILENCIOSO»", ("tumba",), 0.2, step=0.14, y=0.5, size=64, maxw=0.8)],
        tr="fade", td=0.3, tex=DARK)
    add(388.08, fr("l_00752.jpg", None), [LowerThird("WALT WHITMAN", "Poeta · periodista en Brooklyn", w("walt", 391.9) - 388.08)], tex=ARCH)
    add(393.78, fr("l_4a23885.jpg", "Atlantic Avenue, Brooklyn · hacia 1910"), [rich("ARRIBA, LA AVENIDA SIGUIÓ CON SU VIDA", ("vida",), 0.3, y=0.065, size=52)],
        tr="fade", td=0.4, tex=ARCH)
    add(396.32, fr("l_4a25241.jpg", "Estación del Long Island Rail Road, Atlantic Avenue · hacia 1900"), [big("MÁS DE MEDIO SIGLO SIN QUE NADIE BAJARA", 0.3, 0.065, 54, YELLOW)],
        tex=ARCH)
    add(399.02, kb("f_4322966761.jpg", "punch", "doc"), [Badge("PRIMERA GUERRA MUNDIAL", 0.2, None), Flash(w("golpes", 402.9) - 399.02, 0.2, (255, 255, 255), 0.6)],
        tex=CLEAN, post=postshake(5))

    # ============================== CAP 3: UN TÚNEL CONVERTIDO EN RUMOR (404.2 - 503.3)
    bg, ov = chapter(3, "Un túnel convertido en rumor", "f_4323698642.jpg", "dark", "1916–1979")
    add(404.16, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(406.78, fr("l_22664.jpg", "Muelle de Jersey City tras la explosión de Black Tom · julio de 1916"), [rich("EE. UU. TODAVÍA NO HABÍA ENTRADO EN LA GUERRA", ("guerra",), 0.2, y=0.065, size=48, maxw=0.85)],
        tex=ARCH)
    add(410.02, fr("l_3c30625.jpg", "Ruinas de Black Tom: sabotaje alemán en el puerto de Nueva York, 1916"), [big("SABOTEADORES ALEMANES", 0.3, 0.065, 66, RED)], tex=ARCH)
    add(413.50, kb("u_Axli9F0n26A.jpg", "in", "dark"), [rich("LLEGÓ UN AVISO", ("aviso",), 0.2, y=0.5, size=80)], tex=DARK)
    add(416.20, kb("u_8rZ0VKNbfiY.jpg", "in", "dark"), [rich("¿ALGUIEN FABRICABA BOMBAS AHÍ ABAJO?", ("bombas",), 0.4, y=0.84, size=58, red=("bombas",))], tex=DARK, post=postshake(2))
    add(420.90, fr("l_43391.jpg"), [LowerThird("BUREAU OF INVESTIGATION", "Con los años se convertiría en el FBI", 0.4)], tex=ARCH)
    add(w("fbi", 425.3) - 0.3, kb("l_14201.jpg", "in", "doc"), [big("FBI", 0.1, 0.84, 110, YELLOW, "pop")], tr="whip_l", td=0.2, tex=CLEAN)
    add(426.70, kb("f_4322959359.jpg", "punch", "dark"), [rich("UN BOQUETE A MARTILLO NEUMÁTICO", ("boquete",), 0.3, y=0.84, size=58)], tex=DARK, post=postshake(6))
    add(431.70, Solid("black"), [big("NO HABÍA NADA", 0.0, 0.5, 120, WHITE, "pop")], tr="flash", td=0.15, tex=DARK)
    add(w("dejaron", 432.9) - 0.2, kb("u_kUPrYsViPiw.jpg", "in", "dark"), [rich("DEJARON UNA LUZ, LO SELLARON Y SE FUERON", ("luz",), 0.3, y=0.84, size=54, maxw=0.8)], tex=DARK)
    add(437.32, kb("u_rzCi3mD-6ho.jpg", "in", "dark"), [rich("LE DIO CUERDA A LA IMAGINACIÓN", ("imaginación",), 1.0, y=0.84, size=58)], tr="fade", td=0.4, tex=DARK)
    add(441.98, kb("u_P9nFGQRWEp0.jpg", "in", "dark"), [Badge("AÑOS 20", 0.2, None), rich("¿UN CULTIVO DE HONGOS?", ("hongos",), 0.4, y=0.84, size=62)], tex=DARK)
    add(446.54, fr("l_3b41624.jpg", "El alambique más grande decomisado · 1922"), [rich("¿WHISKY EN PLENA LEY SECA?", ("whisky",), 0.3, y=0.065, size=58)], tex=ARCH)
    add(450.48, kb("u_XA-Sr07Qqno.jpg", "in", "dark"), [Badge("1936", 0.2, None), rich("LA POLICÍA BUSCA UN CADÁVER", ("cadáver",), 0.5, y=0.84, size=58)], tex=DARK)
    add(455.72, kb("u_b8RvR4kAG1c.jpg", "in", "dark"), [rich("ENTERRADO DENTRO, SEGÚN SE CONTABA", ("enterrado",), 0.2, y=0.84, size=56)], tex=DARK)
    add(459.04, kb("u_jPtLJBqpQyA.jpg", "punch", "doc"), [rich("NI ENCONTRARON POR DÓNDE METERSE", ("dónde",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(461.70, kb("u_5utYi64hnJ0.jpg", "in", "warm"), [Badge("FINALES DE LOS 50", 0.2, None), rich("DOS HISTORIADORES DEL FERROCARRIL", ("historiadores",), 0.4, y=0.84, size=56)], tex=CLEAN)
    add(w("tampoco", 466.0) - 0.1, kb("u_GN2IqNRlPXs.jpg", "punch", "doc"), [Stamp("TAMPOCO PASARON", 0.2, YELLOW, (0.5, 0.5), -8, 110)], tex=CLEAN)
    add(469.80, warp(G6.avenue_profile, 1.4, 0.6, mode="seal"), [rich("LAS LEYES Y LOS LADRILLOS HABÍAN HECHO SU TRABAJO", ("leyes", "ladrillos"), 0.2, y=0.93, size=44, maxw=0.9)],
        tr="fade", td=0.3, tex=GFX)
    add(472.80, kb("u_ySNtJhDX-cw.jpg", "in", "doc"), [rich("EL TÚNEL HABÍA DESAPARECIDO DE LA VISTA", ("desaparecido",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(475.22, kb("u_-fpWAljGoGA.jpg", "in", "warm"), [rich("SOLO QUEDABAN LAS HISTORIAS, CADA UNA MÁS EXAGERADA", ("historias",), 0.3, y=0.84, size=52, maxw=0.8)], tex=CLEAN)
    tb = w("bombas", 481.4)
    add(tb - 0.4, cus(G6.rumor_board, cards=rumors([0.4, w("whisky", 482.2) - tb + 0.4, w("cadaver", 482.9) - tb + 0.4, 2.0, w("locomotora", 483.6) - tb + 0.4])),
        [Stamp("CASI NINGUNA COMPROBADA", w("casi", 484.7) - tb + 0.4, RED, (0.5, 0.55), -8, 84)], tr="fade", td=0.3, tex=GFX)
    add(487.20, kb("u_vRH__teNKBM.jpg", "in", "dark"), [rich("MIENTRAS ALGUIEN LAS CONTARA, EL TÚNEL NO MORÍA", ("contara",), 0.4, y=0.84, size=54, maxw=0.8)], tr="fade", td=0.4, tex=DARK)
    add(491.94, kb("u_CbSIiGiK9sM.jpg", "in", "warm"), [FnOverlay(G6.radio, lines=[("LA MÁS NOVELESCA…", 66), ("ACABÓ EN LA RADIO", 54)], x=0.3, y=0.42, t0=0.6, every=1.6)],
        tex=CLEAN)
    add(496.72, kb("u_idwpKeO-ZWk.jpg", "in", "dark"), [Badge("UNA NOCHE DE 1979", 0.2, None), rich("UN CHICO DE 19 AÑOS LA ESTABA ESCUCHANDO", ("19",), 1.4, y=0.84, size=54, maxw=0.8)],
        tex=DARK)

    # ============================== CAP 4: LO ENCONTRÓ UN CUENTO (503.3 - 640.5)
    bg, ov = chapter(4, "Lo encontró un cuento", None, year="1979–1980", base=kb("f_4323696052.jpg", "in", "dark"))
    add(503.32, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(506.06, fr("l_117040p.jpg"),
        [LowerThird("BOB DIAMOND", "De Brooklyn · dejó Ingeniería Eléctrica en el Pratt Institute", 0.3)], tex=ARCH)
    add(510.76, kb("u_0w-7su4kinI.jpg", "in", "warm"), [FnOverlay(G6.radio, lines=[("ESA NOCHE, EN LA RADIO…", 60), ("UNA HISTORIA DE NOVELA", 54)], x=0.32, y=0.45, t0=0.4, every=1.6)],
        tex=CLEAN)
    add(516.22, Split([fr("l_19233.jpg"), fr("l_3a24150.jpg")], labels=["JOHN WILKES BOOTH", "ABRAHAM LINCOLN"]),
        [rich("EL HOMBRE QUE MATÓ A LINCOLN", ("mató",), 1.0, y=0.07, size=50)], tex=ARCH)
    add(520.52, kb("l_04719.jpg", "in", "doc"), [Caption("Diario de bolsillo de John Wilkes Booth (1864) · colección del museo", None, 0.4),
                                                 rich("¿PÁGINAS DE SU DIARIO EN UN TÚNEL SECRETO BAJO BROOKLYN?", ("túnel", "secreto"), 0.8, y=0.14, size=48, maxw=0.85)], tex=CLEAN)
    add(525.06, kb("l_04718.jpg", "punch", "doc"), [Stamp("¿UN CUENTO?", 0.4, RED, (0.5, 0.5), -10, 130)], tex=CLEAN)
    add(527.68, kb("u_fteR0e2BzKo.jpg", "in", "doc"), [rich("LO DEL TÚNEL, NO", ("túnel",), 0.2, y=0.84, size=64),
                                                     big("PENSÓ COMO UN INGENIERO", w("penso", 529.5) - 527.68, 0.2, 60, YELLOW)], tex=CLEAN)
    add(531.22, kb("u_URnyBZCnlIs.jpg", "in", "doc"), [rich("SI PASARON TRENES POR DEBAJO… ALGUIEN TUVO QUE DIBUJAR POR DÓNDE", ("dibujar",), 0.2, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(536.42, kb("u_AFB6S2kibuk.jpg", "in", "doc"), [Darken(0.4), big("A BUSCAR EL DIBUJO", 0.2, 0.84, 70, YELLOW)], tex=CLEAN)
    add(538.40, kb("u_ArPcvUm96FM.jpg", "in", "bw"), [Badge("MÁS DE UN AÑO", 0.2, None), rich("HORAS EN BIBLIOTECAS", ("bibliotecas",), 0.5, y=0.84, size=60)], tex=ARCH)
    add(541.80, kb("u_mU_xG4wNkKw.jpg", "in", "warm"), [Darken(0.4), rich("MICROFILMS DE PERIÓDICOS VIEJOS Y MAPAS DEL SIGLO XIX", ("microfilms", "mapas"), 0.2, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(546.06, fr("l_07322.jpg", "Oficinas del Brooklyn Daily Eagle · 1916"), [Badge("BROOKLYN EAGLE · ARTÍCULO DE 1911", 0.4, None)], tex=ARCH)
    add(551.08, kb("u_nCykWCCb5aI.jpg", "in", "warm"), [rich("HABLABA DEL TÚNEL… Y DE UNOS PLANOS", ("planos",), 0.2, y=0.84, size=58)], tex=CLEAN)
    add(554.52, fr("l_3b38906.jpg", "Borough Hall de Brooklyn · 1908"), [rich("EN LA OFICINA DEL PRESIDENTE DEL CONDADO", ("presidente",), 0.4, y=0.065, size=50, maxw=0.85)],
        tex=ARCH)
    add(559.12, kb("u_fM-DIVSpadk.jpg", "in", "warm"), [rich("HIZO ALGO QUE NADIE HABÍA HECHO EN DÉCADAS", ("nadie",), 0.2, y=0.84, size=54, maxw=0.8),
                                                      big("LOS PIDIÓ", w("pidio", 564.6) - 559.12, 0.5, 120, YELLOW, "pop")], tex=CLEAN)
    add(565.52, kb("u_X_j3b4rqnIk.jpg", "in", "doc"), [Stamp("PERDIDOS HACE MUCHO", 1.2, RED, (0.5, 0.5), -8, 100)], tex=CLEAN)
    add(572.18, kb("f_4322960431.jpg", "punch", "doc"), [big("DIAMOND INSISTIÓ", 0.0, 0.84, 80, YELLOW, "pop")], tex=CLEAN)
    add(573.54, kb("u_5utYi64hnJ0.jpg", "in", "warm"), [LowerThird("HOWARD GOLDEN", "Presidente del condado de Brooklyn", 0.4)], tex=CLEAN)
    add(577.86, kb("u_50iCaDpf7a0.jpg", "punch", "dark"), [rich("UNA CAJA VIEJA CERRADA CON LLAVE", ("llave",), 0.4, y=0.84, size=58)], tex=DARK)
    add(582.12, cus(G6.blueprint, hi_t=w("circulo", 589.5) - 582.12), tr="fade", td=0.3, tex=GFX)
    add(592.28, kb("u_GN2IqNRlPXs.jpg", "in", "doc"), [rich("LAS LEYES · LOS LADRILLOS · EL OLVIDO", ("leyes", "ladrillos", "olvido"), 0.6, y=0.5, size=72)], tr="fade", td=0.3, tex=CLEAN)
    add(599.24, kb("u_kqgC_6j6AaA.jpg", "in", "dark"), [rich("PERO FÍJATE EN LO QUE ACABA DE PASAR", ("fíjate",), 0.2, y=0.5, size=64)], tex=DARK)
    add(601.46, Split([kb("l_43391.jpg", "in", "archival"), kb("u_XA-Sr07Qqno.jpg", "in", "dark"), kb("u_5utYi64hnJ0.jpg", "in", "warm")],
                      labels=["AGENTES", "POLICÍA", "HISTORIADORES"]), [Stamp("SE QUEDARON FUERA", w("quedaron", 606.4) - 601.46, RED, (0.5, 0.55), -8, 96)], tex=CLEAN)
    add(608.22, kb("f_4323696052.jpg", "in", "doc"), [rich("UN CHICO QUE HABÍA SALIDO DETRÁS DE UN CUENTO", ("cuento",), 0.4, y=0.86, size=52, maxw=0.8)], tex=CLEAN)
    add(612.50, kb("l_04719.jpg", "punch", "doc"), [Stamp("CASI SEGURO, INVENTADO", 0.4, RED, (0.5, 0.5), -8, 90)], tex=CLEAN)
    add(615.02, mp("aa_loc", [(0, -73.991, 40.6912, 0.85), (5.5, -73.991, 40.6912, 0.95)],
                   [dict(type="pin", at="borough_hall", t0=0.3, label="BOROUGH HALL", side="r", box=True, size=42),
                    dict(type="route", path=["borough_hall", (-73.9915, 40.6905), "court"], t0=1.4, draw=1.2, color=WHITE, width=5, dash=12),
                    dict(type="pin", at="court", t0=2.4, label="LA ALCANTARILLA", side="l", size=42),
                    dict(type="label", at=(-73.9885, 40.6900), text="A POCAS CUADRAS", t0=3.0, size=44, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(620.68, kb("u_URnyBZCnlIs.jpg", "out", "doc"), [rich("UNOS PLANOS QUE LLEVABAN DÉCADAS ESPERANDO", ("décadas",), 0.2, y=0.84, size=54, maxw=0.8)], tex=CLEAN)
    add(624.26, kb("f_3627170494.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=520, amb=0.2),
                                                      big("LO HABÍA ENTERRADO UNA LEY", 0.1, 0.40, 78, WHITE),
                                                      big("LO RESCATÓ UN CUENTO", w("rescatar", 627.6) - 624.26, 0.58, 90, YELLOW, "pop")], tex=DARK)
    add(629.88, fr("f_3835371247.jpg", "Bob Diamond · foto: evan p. cordes (CC BY 2.0)", g="doc"), [Badge("1980 · 20 AÑOS", 0.3, None)], tex=CLEAN)
    add(633.98, kb("u_nXguHgL22ag.jpg", "punch", "doc"), [big("YA SABÍA DÓNDE ESTABA LA PUERTA", 0.1, 0.84, 62, YELLOW)], tex=CLEAN)
    add(636.20, kb("u_Rv9Dc_O-kqk.jpg", "in", "doc"), [rich("FALTABA QUE LA CIUDAD LE DEJARA ABRIRLA", ("ciudad",), 0.3, y=0.84, size=56)], tex=CLEAN)

    # ============================== CAP 5: LA BAJADA (640.5 - 779.2)
    bg, ov = chapter(5, "La bajada", "u_yybIBW3lqGM.jpg", "dark", "1981")
    add(640.48, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(643.10, kb("u_FGjR4IGwP7U.jpg", "in", "night"), [rich("ABRIR UNA ALCANTARILLA EN MITAD DE UNA AVENIDA", ("alcantarilla",), 0.3, y=0.84, size=52, maxw=0.8)], tex=CLEAN)
    add(w("trafico", 649.6) - 0.6, kb("u_7ccqBRt94dA.jpg", "in", "doc"), [big("CON TRÁFICO A TODAS HORAS", 0.1, 0.84, 64)], tr="whip_l", td=0.2, tex=CLEAN)
    add(651.24, kb("u_KGDVTn9lYDE.jpg", "in", "warm"), [Badge("1981", 0.2, None), Stamp("PERMISO CONCEDIDO", 1.2, GREEN, (0.5, 0.5), -8, 96)], tex=CLEAN)
    add(655.68, kb("f_4322955587.jpg", "in", "doc"), [rich("LA COMPAÑÍA DEL GAS Y VARIOS FUNCIONARIOS CORTARON EL PASO", ("gas",), 0.3, step=0.1, y=0.86, size=48, maxw=0.85)],
        tex=CLEAN)
    add(663.08, kb("u_yybIBW3lqGM.jpg", "punch", "dark"), [rich("ANTES DE QUE SE LEVANTE ESA TAPA… UNA COSA", ("tapa…",), 0.2, y=0.84, size=54, maxw=0.8)], tex=DARK)
    add(667.16, kb("u_8rZ0VKNbfiY.jpg", "in", "dark"), [Darken(0.3), rich("MÁS DE UN AÑO PARA SABER POR DÓNDE SE ENTRABA", ("año",), 0.2, y=0.24, size=50, maxw=0.8),
                                                      FnOverlay(G2.subscribe)], tex=DARK)
    add(677.72, kb("f_4323692142.jpg", "punch", "doc"), [big("Y AHORA, LA TAPA", 0.0, 0.84, 80, YELLOW, "pop")], tr="flash", td=0.2, tex=CLEAN)
    add(679.80, warp(G6.descent, 0.0, 0.14), tr="fade", td=0.25, tex=GFX)
    add(686.68, warp(G6.descent, 0.95, 0.12), tex=GFX)
    add(694.38, kb("u_H30WWJyrvgs.jpg", "in", "dark"), [rich("PONTE EN SU LUGAR", ("lugar",), 0.1, y=0.84, size=64)], tex=DARK)
    add(695.60, kb("u_XCnqwORjlWg.jpg", "in", "dark"), [rich("BOCA ABAJO · UNA LINTERNA · UNA BOTELLA DE OXÍGENO", ("oxígeno",), 0.3, y=0.84, size=50, maxw=0.85)], tex=DARK)
    add(700.96, warp(G6.descent, 1.6, 0.12), tex=GFX)
    add(707.84, fr("f_3627171366.jpg", "El paso que lleva al túnel · foto: Justin Kerr Sheckler (CC BY 2.0)", g="doc"),
        [rich("SOBRE LOS CODOS, COMO DEBAJO DE UNA CAMA… DE 70 PIES", ("70",), 0.3, step=0.1, y=0.065, size=46, maxw=0.85)], tex=CLEAN)
    add(715.90, kb("u_hxNW53TdOro.jpg", "in", "dark"), [rich("ENCIMA DE TU ESPALDA, PASAN LOS AUTOBUSES", ("autobuses",), 0.3, y=0.84, size=54)], tex=DARK, post=postshake(4))
    add(720.64, kb("f_4322963019.jpg", "in", "none"), [torch(((0.5, 0.6), (0.5, 0.4)), r=420, amb=0.08), rich("TU MANO TOCA LADRILLO", ("ladrillo",), 0.4, y=0.84, size=62),
                                                      big("ES LO ALTO DE UNA BÓVEDA", w("alto", 724.0) - 720.64, 0.2, 62, YELLOW)], tex=DARK)
    add(725.62, warp(G6.descent, 2.35, 0.12), tex=GFX)
    add(732.22, kb("f_4322959359.jpg", "punch", "dark"), [big("SE ASOMÓ", 0.0, 0.84, 80)], tex=DARK)
    add(733.10, warp(G6.descent, 2.95, 0.24), tex=GFX)
    add(739.80, kb("f_4267479707.jpg", "in", "none"), [torch(((0.2, 0.5), (0.8, 0.5)), r=520, amb=0.1)], tr="fade", td=0.4, tex=DARK)
    add(w("oscuridad", 743.3) - 0.4, kb("f_3627169592.jpg", "in", "none"), [torch(((0.7, 0.5), (0.3, 0.5)), r=520, amb=0.12)], tex=DARK)
    add(746.36, kb("f_4322962651.jpg", "r", "doc"), [rich("EL PISO SECO · LAS PAREDES ENTERAS", ("seco", "enteras"), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(749.96, kb("u_kUPrYsViPiw.jpg", "in", "dark"), [Badge("DESDE 1861", 0.2, None), rich("SOLO LOS AGENTES DE 1916, UN RATO", ("1916",), w("salvo", 754.4) - 749.96, y=0.84, size=54)],
        tex=DARK)
    add(758.94, kb("f_4323700566.jpg", "in", "doc"), [rich("DIAMOND LO RESUMIRÍA CON UNA COMPARACIÓN", ("comparación",), 0.3, y=0.86, size=52, maxw=0.8)], tex=CLEAN)
    add(763.68, kb("u_Bt3LHQMgJlI.jpg", "in", "none"), [big("«COMO PISAR LA LUNA»", 0.4, 0.5, 110, YELLOW, "pop")], tr="fade", td=0.3, tex=DARK)
    add(767.36, kb("f_4323697878.jpg", "in", "doc"), [Badge("21 AÑOS", 0.2, None), rich("EL TÚNEL QUE UNA CIUDAD ENTERA HABÍA OLVIDADO", ("olvidado",), 0.6, y=0.84, size=54, maxw=0.8)],
        tex=CLEAN)
    add(772.78, kb("f_4322960431.jpg", "in", "doc"), [Counter(0, 30, "{:.0f} AÑOS", "PELEANDO PARA QUE NO LO VOLVIERAN A OLVIDAR", 0.3, 1.2, (0.5, 0.45), 170)], tex=CLEAN)

    # ============================== CAP 6: EL SEGUNDO CIERRE (779.2 - 982.5)
    bg, ov = chapter(6, "El segundo cierre", "f_4322960747.jpg", "dark", "1982–2015")
    add(779.20, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(781.38, fr("f_3835371247.jpg", g="doc"),
        [LowerThird("BROOKLYN HISTORIC RAILWAY ASSOCIATION", "Fundada por Bob Diamond en 1982", 0.4)], tex=CLEAN)
    add(789.10, warp(G6.permit, 0.0, 0.42, mode="signed"), tr="fade", td=0.3, tex=GFX)
    add(797.80, kb("f_4267480311.jpg", "in", "doc"), [Badge("1989", 0.3, None), rich("REGISTRO NACIONAL DE LUGARES HISTÓRICOS", ("históricos",), 0.6, y=0.86, size=52, maxw=0.85)], tex=CLEAN)
    add(804.30, kb("f_4322956255.jpg", "in", "doc"), [rich("UNA RAREZA MUY DE BROOKLYN", ("brooklyn",), 0.3, y=0.86, size=58)], tex=CLEAN)
    add(807.74, kb("f_4323691530.jpg", "in", "doc"), [rich("FILA EN LA ACERA · UNO A UNO POR LA ALCANTARILLA", ("alcantarilla",), 0.2, y=0.86, size=50, maxw=0.85)], tex=CLEAN)
    add(811.02, kb("f_4323702150.jpg", "down", "doc"), [rich("UN TÚNEL DE ANTES DE LA GUERRA CIVIL", ("guerra", "civil"), 0.3, y=0.86, size=54)], tex=CLEAN)
    add(814.98, kb("f_3370869032.jpg", "in", "doc"), [FnOverlay(G6.counter_people, n=400, t0=0.3)], tex=CLEAN)
    add(820.50, warp(G6.permit, 0.0, 0.5, mode="line"), [Badge("LA LÍNEA QUE CASI NADIE LEYÓ", 0.2, None)], tr="fade", td=0.3, tex=GFX)
    add(829.80, kb("u_oathFTcFigc.jpg", "in", "warm"), [big("ESA LÍNEA TAMBIÉN VA A VOLVER", 0.1, 0.84, 62, YELLOW)], tex=CLEAN)
    add(832.30, kb("u_fM-DIVSpadk.jpg", "out", "warm"), [rich("CON LA CIUDAD, SIEMPRE HUBO ROCES", ("roces",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(835.98, mp("aa_nyc", [(0, -74.0, 40.685, 0.85), (5.5, -74.005, 40.68, 0.95)],
                   [dict(type="pin", at="red_hook", t0=0.3, label="RED HOOK", side="l", box=True, size=44),
                    dict(type="label", at=(-74.006, 40.668), text="UN TRANVÍA CON VAGONES ANTIGUOS", t0=1.2, size=40),
                    dict(type="pin", at="court", t0=0.8, label="EL TÚNEL", side="r", size=38)]),
        tr="zoom", td=0.3, tex=GFX)
    add(841.98, kb("u_I8ZSorf5jUY.jpg", "in", "bw"), [Badge("2003", 0.2, None), rich("LE RETIRARON EL PERMISO Y QUITARON LAS VÍAS", ("vías",), 0.4, y=0.84, size=52, maxw=0.8)],
        tex=ARCH)
    add(847.54, kb("u_ffH_GkINfyY.jpg", "in", "dark"), [rich("ESPOSADO POR ENTRAR EN EL TÚNEL QUE ÉL MISMO ENCONTRÓ", ("esposado",), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=DARK)
    add(853.38, kb("f_4323696052.jpg", "punch", "dark"), [big("UNA OBSESIÓN", 0.2, 0.84, 80, YELLOW)], tex=DARK)
    add(858.94, kb("f_4323701866.jpg", "in", "none"), [torch(((0.3, 0.5), (0.7, 0.5)), r=480, amb=0.12),
                                                      rich("HACIA HICKS STREET ACABABA EN UNA PARED", ("pared",), 0.4, y=0.84, size=56)], tex=DARK)
    add(863.92, fr("l_03365.jpg", "Locomotora de vapor · grabado de 1831") if os.path.exists(os.path.join(IMG, "l_03365.jpg")) else fr("l_02955.jpg", "Locomotora de vapor · grabado de 1831"),
        [rich("DETRÁS: UNA LOCOMOTORA DE LA DÉCADA DE 1830", ("locomotora",), 0.4, y=0.065, size=52, maxw=0.85)], tex=ARCH)
    add(871.28, kb("u_PDhSqtLG4cw.jpg", "in", "warm"), [Badge("2010", 0.2, None), rich("UN DOCUMENTAL Y LA EXCAVACIÓN DE ESA PARED", ("excavación",), 0.6, y=0.84, size=54, maxw=0.8)],
        tex=CLEAN)
    add(879.00, kb("u_S54gOumfMJY.jpg", "in", "doc"), [rich("LOS BOMBEROS CANCELARON UNA PROYECCIÓN DE CINE AHÍ ABAJO", ("bomberos",), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(885.72, kb("u_KGDVTn9lYDE.jpg", "punch", "dark"), [Badge("17 DE DICIEMBRE DE 2010 · 4:45 P. M.", 0.2, None), rich("UNA CARTA", ("carta",), w("carta", 892.4) - 885.72, y=0.5, size=90)],
        tex=DARK)
    add(893.32, warp(G6.permit, 0.0, 0.5, mode="revoked"), tr="fade", td=0.2, tex=GFX)
    add(896.40, warp(G6.avenue_profile, 0.0, 0.18, mode="onedoor"), [rich("UNA SOLA ENTRADA · POCA VENTILACIÓN", ("sola",), 0.3, y=0.93, size=46)], tr="fade", td=0.3, tex=GFX)
    add(903.14, warp(G6.avenue_profile, 1.3, 0.25, mode="onedoor"), tex=GFX)
    add(911.36, kb("u_kqgC_6j6AaA.jpg", "in", "dark"), [rich("LA RESPUESTA AL OTRO MISTERIO", ("misterio",), 0.3, y=0.5, size=70)], tex=DARK)
    q2(914.80)
    add(921.06, kb("u_jPtLJBqpQyA.jpg", "punch", "doc"), [big("PORQUE EL TÚNEL TIENE UNA SOLA PUERTA", 0.0, 0.84, 62, YELLOW)], tex=CLEAN)
    add(923.12, kb("u_fM-DIVSpadk.jpg", "in", "warm"), [rich("Y LA ÚNICA QUE PODÍA AUTORIZAR OTRA ERA LA MISMA CIUDAD", ("ciudad",), 0.3, step=0.1, y=0.84, size=48, maxw=0.85)],
        tex=CLEAN)
    add(930.40, kb("u_CgXwuXIdQic.jpg", "in", "dark"), [rich("LA BÚSQUEDA DE LA LOCOMOTORA SIGUIÓ", ("locomotora",), 0.3, y=0.84, size=56)], tex=DARK)
    add(934.84, cus(G6.avenue_profile, mode="scan"), tr="fade", td=0.3, tex=GFX)
    add(949.60, kb("u_Rd-Nxg7Zd4I.jpg", "in", "dark"), [Stamp("¿UNA LOCOMOTORA? NADIE LO DIJO", 0.3, RED, (0.5, 0.5), -8, 76),
                                                      rich("ALGO GRANDE DE METAL · NO SABÍAN QUÉ ERA", ("metal",), w("solo", 951.2) - 949.6, y=0.84, size=52, maxw=0.8)], tex=DARK)
    add(956.64, kb("u_TdNLjGXVH3s.jpg", "in", "dark"), [Counter(0, 15, "{:.0f}", "CARGOS CONTRA LA CIUDAD", 0.2, 1.0, (0.5, 0.42), 200),
                                                      Stamp("PERDIÓ", w("perdio", 959.4) - 956.64, RED, (0.5, 0.5), -10, 170)], tex=DARK)
    add(960.40, kb("u_YFz39MOmxnQ.jpg", "in", "doc"), [Badge("18 DE MARZO DE 2015 · TRIBUNAL DE APELACIÓN", 0.2, None)], tex=CLEAN)
    add(967.42, warp(G6.permit, 0.0, 0.6, mode="signed"), [Badge("REVOCABLE A VOLUNTAD", 0.2, None)], tr="fade", td=0.3, tex=GFX)
    add(972.76, warp(G6.permit, 0.0, 0.5, mode="line"), [Badge("LA MISMA LÍNEA DE 1986", 0.2, None)], tex=GFX)
    add(977.00, kb("f_4323701866.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=420, amb=0.08),
                                                      rich("LA PARED SE QUEDÓ SIN ABRIR", ("pared",), 0.2, y=0.84, size=60),
                                                      big("Y DIAMOND NUNCA VOLVIÓ A BAJAR", w("diamond", 979.3) - 977.0, 0.94, 52, YELLOW)], tex=DARK)

    # ============================== CAP 7: HOY (982.5 - 1056.2)
    bg, ov = chapter(7, "Hoy", "u_7KDqzUW3MI4.jpg", "dark", "2021–2026")
    add(982.48, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(w("flatbush", 984.9) - 0.4, kb("f_4323696052.jpg", "in", "bw"), [Caption("Bob Diamond (1960–2021)", "Murió en Flatbush, Brooklyn, el 21 de agosto de 2021", 0.3)], tex=ARCH)
    add(988.54, kb("u_vRH__teNKBM.jpg", "in", "dark"), [rich("61 AÑOS · 11 SIN PISAR EL TÚNEL", ("11",), 0.3, y=0.84, size=60)], tex=DARK)
    add(992.08, kb("u_a1Ih1k2H-AA.jpg", "in", "doc"), [Badge("2026", 0.2, None), Stamp("CERRADO AL PÚBLICO", 0.8, RED, (0.5, 0.5), -8, 96)], tex=CLEAN)
    add(995.92, mp("aa_loc", [(0, -73.9935, 40.6900, 0.6), (6.8, -73.9924, 40.6897, 1.1)],
                   [dict(type="route", path=AVENUE[:8], t0=0.2, draw=1.2, color=(160, 160, 160), width=10, smooth=False),
                    dict(type="label", at=(-73.991, 40.6870), text="NI VISITAS NI EXCAVACIÓN", t0=0.8, size=44, color=RED),
                    dict(type="pin", at="court", t0=w("alcantarilla", 1000.4) - 995.92, label="ATLANTIC AVE Y COURT ST", side="r", box=True, size=42)]),
        tr="zoom", td=0.3, tex=GFX)
    add(1002.76, kb("f_3295488141.jpg", "in", "doc"), [rich("ARRIBA HA CAMBIADO CASI TODO", ("todo",), 0.3, y=0.86, size=58)], tex=CLEAN)
    add(1005.52, kb("u_KSf8G_VMh7w.jpg", "in", "doc"), [rich("DONDE EN 1981 HABÍA UN BANCO, HOY HAY UN SUPERMERCADO", ("supermercado",), 0.3, step=0.1, y=0.86, size=48, maxw=0.85)],
        tex=CLEAN)
    add(1012.10, kb("u_7ccqBRt94dA.jpg", "in", "doc"), [rich("PASAN LOS AUTOBUSES", ("autobuses",), 0.1, y=0.84, size=58)], tex=CLEAN)
    add(w("cruza", 1013.4) - 0.2, kb("u_arPQ-sQ4JQk.jpg", "in", "warm"), [rich("LA GENTE CRUZA CON EL CAFÉ EN LA MANO", ("café",), 0.1, y=0.84, size=56)], tr="whip_l", td=0.2, tex=CLEAN)
    add(1015.30, cus(G6.avenue_profile, mode="today"), tr="fade", td=0.3, tex=GFX)
    add(1020.30, mp("aa_loc", [(0, -73.985, 40.6870, 0.42), (2.9, -73.985, 40.6870, 0.45)],
                    [dict(type="pin", at="court", t0=0.2, label="LA TAPA", side="t", size=40),
                     dict(type="route", path=AVENUE[5:], t0=0.6, draw=1.6, color=YELLOW, width=8, smooth=False),
                     dict(type="pin", at="flatbush", t0=2.0, label="TERMINAL DE ATLANTIC", side="b", box=True, size=40),
                     dict(type="label", at=(-73.985, 40.6895), text="≈ 1 MILLA", t0=1.4, size=48, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(1023.20, kb("u_hWZuRADRj_8.jpg", "in", "doc"), [Badge("FLATBUSH AVENUE · LONG ISLAND RAIL ROAD", 0.2, None)], tex=CLEAN)
    add(1026.90, mp("aa_nyc", [(0, -73.93, 40.69, 0.42), (7.0, -73.90, 40.695, 0.5)],
                    [dict(type="pin", at="flatbush", t0=0.2, label="ATLANTIC TERMINAL", side="l", size=38),
                     dict(type="route", path=LIRR_TODAY, t0=0.6, draw=3.0, color=YELLOW, width=7, smooth=True, traffic=3, speed=160),
                     dict(type="label", at=(-73.92, 40.672), text="BAJO LA MISMA AVENIDA", t0=1.6, size=44),
                     dict(type="label", at=(-73.885, 40.705), text="HACIA QUEENS", t0=3.0, size=44, color=YELLOW)]),
        tr="fade", td=0.3, tex=GFX)
    add(1034.22, kb("u_6vtjadr0e2I.jpg", "in", "doc"), [rich("LA COMPAÑÍA QUE SE FUE EN 1861… VOLVIÓ BAJO TIERRA", ("volvió",), 0.3, step=0.1, y=0.86, size=48, maxw=0.85)], tex=CLEAN)
    add(1042.64, kb("f_4322963717.jpg", "in", "none"), [torch(((0.3, 0.5), (0.7, 0.5)), r=540, amb=0.15), rich("LA BÓVEDA SIGUE SECA Y ENTERA", ("seca", "entera"), 1.0, y=0.84, size=58)],
        tr="fade", td=0.4, tex=DARK)
    add(1047.74, kb("f_4323701866.jpg", "punch", "none"), [torch(((0.5, 0.5), (0.5, 0.5)), r=380, amb=0.06),
                                                          big("¿Y DETRÁS DE LA PARED?", 0.4, 0.84, 70, YELLOW)], tex=DARK)
    add(1052.74, kb("u_kqgC_6j6AaA.jpg", "in", "dark"), [rich("DE VUELTA A LA PRIMERA PREGUNTA", ("primera",), 0.3, y=0.5, size=70)], tr="fade", td=0.4, tex=DARK)

    # ============================== CONCLUSIÓN (1056.2 - end)
    q1(1056.20)
    add(1060.10, kb("f_3627170748.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=520, amb=0.15), big("LO PIERDE A MEDIAS", 0.0, 0.5, 110, YELLOW, "pop")], tex=DARK)
    add(1062.70, kb("l_1s14037_L.jpg", "in", "archival"), [Badge("1859 · UNA LEY MANDÓ CERRARLO", 0.2, None)], tex=ARCH)
    add(1066.02, warp(G6.avenue_profile, 1.0, 0.5, mode="seal"), [rich("LOS VECINOS PREFIRIERON TAPARLO A RELLENARLO", ("taparlo",), 0.2, y=0.93, size=44, maxw=0.9)],
        tr="fade", td=0.3, tex=GFX)
    add(1072.74, kb("u_50iCaDpf7a0.jpg", "in", "dark"), [rich("LOS PLANOS, EN UNA CAJA CON LLAVE", ("llave",), 0.2, y=0.84, size=58)], tex=DARK)
    add(1075.84, kb("u_X_j3b4rqnIk.jpg", "in", "doc"), [rich("MÁS DE UN SIGLO SIN QUE NADIE FUERA A BUSCARLOS", ("siglo",), 0.2, y=0.84, size=52, maxw=0.8)], tex=CLEAN)
    add(1079.60, cus(G6.avenue_profile, mode="today"), tr="fade", td=0.3, tex=GFX)
    add(1084.12, kb("u_nXguHgL22ag.jpg", "in", "doc"), [rich("LO QUE SE PERDIÓ FUE EL CAMINO PARA LLEGAR", ("camino",), 0.2, y=0.84, size=56, maxw=0.8)], tex=CLEAN)
    add(1087.54, kb("u_kqgC_6j6AaA.jpg", "in", "dark"), [rich("FÍJATE EN QUIÉN LO ENCONTRÓ", ("quién",), 0.1, y=0.5, size=72)], tex=DARK)
    add(1089.60, Split([kb("l_43391.jpg", "in", "archival"), kb("u_XA-Sr07Qqno.jpg", "in", "dark"), kb("u_5utYi64hnJ0.jpg", "in", "warm")],
                       labels=["NI LOS AGENTES", "NI LA POLICÍA", "NI LOS HISTORIADORES"]), tex=CLEAN)
    add(1094.60, kb("u_CbSIiGiK9sM.jpg", "in", "warm"), [FnOverlay(G6.radio, lines=[("UN CHICO Y UNA RADIO", 60), ("EL DIARIO DE UN ASESINO", 52)], x=0.3, y=0.42, t0=0.3, every=1.4)],
        tex=CLEAN)
    add(1100.08, kb("f_3627169592.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=520, amb=0.2),
                                                       big("LO ENTERRÓ UNA LEY", 0.1, 0.40, 84, WHITE),
                                                       big("LO SALVÓ UN CUENTO", w("salvo", 1102.6) - 1100.08, 0.58, 96, YELLOW, "pop")], tex=DARK)
    add(1103.94, cus(G6.rumor_board, cards=rumors([0.0, 0.0, 0.0, 0.0, 0.0])), [rich("LO ÚNICO QUE SIGUIÓ VIVO FUERON LAS HISTORIAS", ("historias",), w("unico", 1106.8) - 1103.94, y=0.5, size=56, maxw=0.8)],
        tr="fade", td=0.3, tex=GFX)
    add(1109.72, kb("u_7ccqBRt94dA.jpg", "in", "doc"), [rich("LA PRÓXIMA VEZ QUE ESPERES EL AUTOBÚS EN ATLANTIC CON COURT…", ("atlantic", "court…"), 0.2, step=0.09, y=0.84, size=48, maxw=0.85)],
        tex=CLEAN)
    add(1113.54, kb("u_yybIBW3lqGM.jpg", "punch", "doc"), [big("MIRA LA TAPA", 0.0, 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(1115.48, kb("f_4322963019.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=520, amb=0.15), big("UNA BÓVEDA DE 1844", 0.2, 0.84, 70)], tex=DARK)
    add(w("pared", 1118.3) - 0.3, kb("f_4323701866.jpg", "in", "none"), [torch(((0.45, 0.5), (0.55, 0.5)), r=420, amb=0.1), big("UNA PARED QUE NADIE HA ABIERTO", 0.0, 0.84, 64)],
        tr="whip_l", td=0.2, tex=DARK)
    add(w("locomotora", 1121.6) - 0.6, kb("u_Rd-Nxg7Zd4I.jpg", "in", "dark"), [big("Y, QUIZÁ, UNA LOCOMOTORA", 0.2, 0.84, 70, YELLOW)], tr="fade", td=0.3, tex=DARK)
    add(1123.74, kb("f_4267479707.jpg", "out", "none"), [torch(((0.45, 0.5), (0.55, 0.5)), r=640, amb=0.22),
                                                       rich("MIENTRAS ALGUIEN SIGA CONTÁNDOLO, NO ESTÁ PERDIDO DEL TODO", ("contándolo",), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tr="fade", td=0.4, tex=DARK)
    add(1128.16, fr("l_4a23885.jpg", "Atlantic Avenue, Brooklyn · hacia 1910"), [big("AHORA TE PREGUNTO A TI", 0.2, 0.065, 66, YELLOW)], tr="fade", td=0.4, tex=ARCH)
    add(1130.06, kb("u_7KDqzUW3MI4.jpg", "out", "dark"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿TU ABUELO O TU ABUELA", line2="HABLABA DEL TÚNEL DE ATLANTIC AVENUE?", cta="CUÉNTANOS EN LOS COMENTARIOS QUÉ TE CONTABA"),
         rich("Fueron historias como esa las que lo mantuvieron vivo durante 120 años", ("120",), w("fueron", 1139.6) - 1130.06, step=0.08, y=0.2, size=46, maxw=0.85)],
        tex=DARK)
    return S
