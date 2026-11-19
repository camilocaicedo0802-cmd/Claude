"""The edit: every shot of the Saluda Grade video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx7 as G7
import gfx15 as G15
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1112.42
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
BLUE = (110, 170, 220)
GREY_ = (160, 160, 160)
IMG = os.path.join(ROOT, "assets", "img")
VIDDIR = os.path.join(ROOT, "assets", "vid")

WM = "Wikimedia Commons"
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












# ------------------------------------------------------------------ Saluda Grade specifics
LINE = M.sg_ll("line")
GRADE = M.sg_ll("grade")
PACOLET = [[tuple(p) for p in l] for l in M.sg_data()["pacolet"]]
CAP_LOC = "Library of Congress"
F = lambda i: f"f_{i}.jpg"
U = lambda i: f"u_{i}.jpg"
RED_ = (230, 70, 60)
BLUE_ = (110, 170, 220)
GREEN_ = (90, 210, 120)
GOLD = (236, 190, 70)
RAIL = (230, 200, 120)
NIGHT = dict(grain=8, vignette=1.1)


def _card(t, dur, lines=()):
    from gfx import background
    img = background("dark_grid", t)
    for tx, sz, col, y, t0 in lines:
        G2.label(img, tx, 960, 1080 * y, ease_out(prog(t, t0, 0.4)), sz, col)
    return img


def _sub(line):
    """the part of the line between two latitudes (north first)"""
    return line


def _seg(a, b):
    """piece of the line between the points closest to a and b (lon, lat)."""
    import math
    ia = min(range(len(LINE)), key=lambda i: math.hypot(LINE[i][0] - a[0], LINE[i][1] - a[1]))
    ib = min(range(len(LINE)), key=lambda i: math.hypot(LINE[i][0] - b[0], LINE[i][1] - b[1]))
    return LINE[min(ia, ib):max(ia, ib) + 1] if ia <= ib else LINE[ib:ia + 1][::-1]


SALUDA, MELROSE, TRYON, ASHEVILLE, SPARTANBURG = (-82.3493, 35.2362), (-82.3226, 35.2196), (-82.2385, 35.2082), (-82.554, 35.5951), (-81.9321, 34.9496)
INMAN, ZIRCONIA = (-82.0901, 35.0471), (-82.4162, 35.2418)
TRAIL = _seg(ZIRCONIA, INMAN)
SAL_TRY = _seg(SALUDA, TRYON)
ASH_SAL = _seg(ASHEVILLE, SALUDA)
SOUTH = [(-82.554, 35.595), (-82.30, 35.25), (-81.932, 34.950), (-81.03, 34.00), (-79.93, 32.78)]
CSPECIAL = [(-79.93, 32.78), (-81.03, 34.00), (-81.932, 34.950), (-82.349, 35.236), (-82.554, 35.595), (-83.92, 35.96), (-84.51, 39.10)]


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg=U("GCGykwFKSYI"), badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Cómo pudo el mejor maquinista de la compañía, que conocía esa montaña como nadie, acabar bajándola sin frenos?", ("mejor", "frenos?"), size=62),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg=U("o4xumntlvYs"), badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Por qué un ferrocarril mandaba a propósito cada tren hacia una vía sin salida?", ("propósito", "salida?"), size=68),
            tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 63.9)
    add(0.0, kb(U("HIPH-vbN8Kg"), "in", "doc"), [rich("IMAGINA UN FERROCARRIL QUE MANDA A PROPÓSITO CADA TREN…", ("propósito",), 0.3, step=0.11, y=0.84, size=58, maxw=0.85)],
        tex=CLEAN)
    add(w("contra", 3.6), kb(U("rWryJFQIF6o"), "punch", "doc"), [big("…CONTRA UN MONTÓN DE TIERRA", 0.0, 0.86, 80, YELLOW, "pop")], post=postshake(5), tex=CLEAN)
    add(5.72, kb(U("5ZZn4Br2scs"), "in", "doc"), [big("NO SOLO A LOS QUE PIERDEN LOS FRENOS", 0.0, 0.3, 62)], tex=CLEAN)
    add(w("a todos", 7.6), cus(_card, lines=[("A TODOS", 220, YELLOW, 0.5, 0.0)]), tr="fade", td=0.15, tex=GFX)
    t0 = 8.64
    add(t0, mp("sg_reg", [(0, -82.0, 35.3, 1.0), (3.7, -82.3, 35.3, 1.08)],
               [dict(type="label", at=(-80.2, 35.75), text="CAROLINA DEL NORTE", t0=w("carolina", 12.0) - t0, size=46, box=True),
                dict(type="pin", at="sg_saluda", t0=w("carolina", 12.0) - t0 + 0.4, label="LAS MONTAÑAS", side="l", box=True, size=40)]),
        [Badge("DÉCADA DE 1890", 0.1, None)], tr="zoom", td=0.3, tex=GFX)
    add(12.4, kb(F(3738207265), "in", "archival"), [big("UN FERROCARRIL EMPEZÓ A HACER EXACTAMENTE ESO", 0.2, 0.86, 58)], tex=ARCH)
    add(16.16, kb(U("HwmUiC1vPUE"), "in", "doc"), [big("UN HOMBRE VIGILABA EL CAMBIO DE AGUJAS", 0.1, 0.12, 60), big("DÍA Y NOCHE", w("día", 18.5) - 16.16, 0.86, 80, YELLOW)],
        tex=CLEAN)
    add(w("y lo dejaba", 19.2), cus(G15.safety, mode="idle", t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(21.9, kb(U("BHs95lcSsbk"), "in", "doc"), [big("PARA SEGUIR: PITAR…", 0.1, 0.3, 70), big("…Y DEMOSTRAR QUE SABÍA FRENAR", w("y demostrar", 24.6) - 21.9, 0.86, 64, YELLOW)],
        tex=CLEAN)
    add(26.96, cus(G15.safety, mode="runaway", t0=0.0), tr="fade", td=0.15, tex=GFX)
    add(29.4, V("44269", U("Y0a6EeC1a6M"), 0.0, "doc"), [big("TENÍA SUS MOTIVOS", 0.1, 0.3, 70)], tex=CLEAN)
    add(w("era la cuesta", 30.9), kb(U("PV_4h9i73BU"), "in", "doc"), [big("LA CUESTA MÁS EMPINADA DE UNA LÍNEA PRINCIPAL", 0.0, 0.12, 58, YELLOW),
                                                                   big("EN TODO ESTADOS UNIDOS", 1.4, 0.86, 70)], tex=CLEAN)
    add(35.36, L("3c27557", kb(U("ydhN7dJBVRw"), "in", "dark"), "Cuadrilla de presos, Thomasville (Georgia) · " + CAP_LOC),
        [rich("PRESOS · GUARDIAS · MAQUINISTAS", ("presos", "guardias", "maquinistas"), 0.2, step=0.5, y=0.9, size=64, maxw=0.9)], tex=ARCH)
    add(38.64, kb(U("GCGykwFKSYI"), "in", "dark"), [big("UNO DE LOS MEJORES DE LA COMPAÑÍA", 0.1, 0.86, 62)], tex=NIGHT)
    add(w("bajó", 41.1), cus(G15.runaway, t0=0.0, span=3.6), [big("UNA NOCHE, SIN FRENOS", 0.2, 0.92, 60, RED_)], tr="fade", td=0.2, tex=GFX)
    add(45.2, kb(F(53892218747), "in", "archival"), [Darken(0.3), big("«LA LLAMABAN»", 0.0, 0.3, 50, GREY_),
                                                     BigText("LA PENDIENTE DE SALUDA", "serif", 104, WHITE, (0.5, 0.48), 0.3, None, "up"),
                                                     big("SALUDA GRADE", 0.8, 0.62, 56, YELLOW)], tr="fade", td=0.3, tex=ARCH)
    add(w("hoy", 48.1), kb(U("0Kw44ElHN3A"), "in", "doc"), [big("HOY NO PASA NI UN TREN", 0.0, 0.86, 76)], tex=CLEAN)
    add(49.28, kb(F(6469069457), "in", "doc"), [big("Y LO QUE LA CERRÓ…", 0.1, 0.3, 66), big("…NO FUE NINGÚN CHOQUE", w("no fue", 51.0) - 49.28, 0.86, 76, YELLOW)], tex=CLEAN)
    q1(52.64)
    q2(58.5)

    # ============================== CAP 1: UNA PARED (63.9 - 198.6)
    bg, ov = chapter(1, "UNA PARED ENTRE ASHEVILLE Y EL SUR", U("JkoYQPW6DBc"), g="doc", year="1870–1877")
    add(63.92, bg, ov, tr="black", td=0.2, tex=DARK)
    add(68.36, L("09291", kb(U("kzZ8mpDTSRs"), "in", "doc"), "Asheville, 1894 · " + CAP_LOC),
        [Badge("DÉCADA DE 1870", 0.1, None), BigText("ASHEVILLE", "serif", 110, WHITE, (0.5, 0.14), 0.4, None, "up")], tex=ARCH)
    t0 = w("en el oeste", 71.2)
    add(t0, mp("sg_reg", [(0, -82.4, 35.4, 0.92), (4.9, -82.55, 35.55, 1.05)],
               [dict(type="pin", at="sg_asheville", t0=0.0, label="ASHEVILLE", side="r", box=True, size=44),
                dict(type="label", at=(-83.6, 35.95), text="LOS APALACHES", t0=w("apalaches", 74.6) - t0, size=50, box=True)]),
        [big("UN PUEBLO DE MONTAÑA", 0.2, 0.9, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(76.3, kb(U("hwKOKClLnHQ"), "in", "doc"), [rich("MADERA · AIRE FRESCO · GANAS DE CRECER", ("madera", "fresco", "crecer"), 0.2, step=0.5, y=0.86, size=62, maxw=0.9)],
        tex=CLEAN)
    t0 = 80.26
    add(t0, mp("sg_us", [(0, -81.5, 34.6, 2.6), (4.2, -81.5, 34.4, 2.4)],
               [dict(type="pin", at="sg_asheville", t0=0.0, label="ASHEVILLE", side="l", box=True, size=36),
                dict(type="route", ll=SOUTH, t0=0.4, draw=2.4, color=YELLOW, width=6, dash=22),
                dict(type="label", at=(-80.6, 33.2), text="LAS LLANURAS DEL SUR", t0=w("llanuras", 82.6) - t0, size=40, box=True)]),
        [big("¿CÓMO BAJAR HASTA LAS LLANURAS?", 0.2, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(84.46, L("6a09713", kb(U("A56yu_pmNKQ"), "in", "doc"), "Fábrica de algodón, Spartanburg, 1909 · " + CAP_LOC),
        [rich("PUERTOS · FÁBRICAS DE ALGODÓN · DINERO", ("puertos", "algodón", "dinero"), 0.2, step=0.6, y=0.9, size=58, maxw=0.9)], tex=ARCH)
    add(88.5, kb(U("xeTAoNgmVEE"), "in", "doc"), [big("DURANTE DÉCADAS, LA ÚNICA SALIDA:", 0.1, 0.12, 56), big("UN CAMINO DE TIERRA", 0.9, 0.86, 80, YELLOW)], tex=CLEAN)
    add(92.78, kb(U("w_cSBsncdzg"), "in", "doc"), [big("LOS ARRIEROS BAJABAN REBAÑOS ENTEROS", 0.1, 0.12, 56), big("CERDOS…", w("cerdos", 95.6) - 92.78, 0.86, 90, YELLOW, "pop")],
        tex=CLEAN)
    add(w("vacas", 96.5), kb(U("3D1wBLPqqck"), "in", "doc"), [big("…VACAS…", 0.0, 0.86, 90, YELLOW, "pop")], tex=CLEAN)
    add(97.1, kb(U("gnuUSiaB1cw"), "in", "doc"), [big("…Y PAVOS", 0.0, 0.86, 90, YELLOW, "pop"), big("HACIA CAROLINA DEL SUR", 0.6, 0.12, 54)], tex=CLEAN)
    add(99.84, cus(_card, lines=[("TARDABAN", 70, GREY_, 0.4, 0.0), ("DÍAS", 180, YELLOW, 0.56, 0.2)]), tr="fade", td=0.15, tex=GFX)
    add(w("cuando llovía", 101.0), L("8a35181", kb(U("2jPwtG5cZOA"), "in", "doc"), "Auto atascado en el barro, Carolina del Sur, 1941 · FSA/OWI · " + CAP_LOC),
        [big("EL BARRO SE TRAGABA LAS CARRETAS HASTA LOS EJES", 0.1, 0.08, 54, YELLOW)], tex=ARCH)
    add(104.66, kb(U("mgv_6Y22p00"), "in", "cold"), [big("PARA UN PUEBLO QUE QUERÍA CRECER…", 0.1, 0.3, 60), big("…COMO VIVIR ENCERRADO", 1.6, 0.86, 76, YELLOW)], tex=CLEAN)
    t0 = 108.5
    add(t0, mp("sg_mid", [(0, -82.25, 35.27, 0.47), (4.2, -82.25, 35.27, 0.5)],
               [dict(type="pin", at="sg_asheville", t0=0.2, label="ASHEVILLE", side="r", box=True, size=40),
                dict(type="pin", at="sg_spartanburg", t0=w("spartanburg", 110.0) - t0, label="SPARTANBURG", side="l", box=True, size=40),
                dict(type="label", at=(-82.05, 35.45), text="UNA PARED", t0=w("pared", 112.0) - t0, size=60, box=True, color=RED_)]),
        tr="zoom", td=0.3, tex=GFX)
    add(112.72, kb(F(5086951252), "in", "doc"), [BigText("EL ESCARPE DE LA BLUE RIDGE", "serif", 92, WHITE, (0.5, 0.14), 0.0, None, "up")], tex=CLEAN)
    add(114.42, cus(G15.wall, t0=0.0, step=1.6, hi_t=w("como el borde", 117.9) - 114.42), [big("COMO EL BORDE DE UNA MESA", w("como el borde", 117.9) - 114.42, 0.94, 50, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(120.94, cus(_card, lines=[("LA COMPAÑÍA ENCARGADA DE CRUZARLA", 50, GREY_, 0.34, 0.0), ("ASHEVILLE AND SPARTANBURG", 96, WHITE, 0.5, 0.3),
                                  ("RAILROAD", 96, YELLOW, 0.62, 0.5)]), tr="fade", td=0.2, tex=GFX)
    add(125.4, kb(U("Jv4uhQpL9vM"), "in", "archival"), [big("UN INGENIERO A BUSCAR EL MEJOR CAMINO", 0.1, 0.86, 60)], tex=ARCH)
    add(127.92, cus(_card, lines=[("SE LLAMABA", 56, GREY_, 0.36, 0.0), ("CHARLES PEARSON", 120, WHITE, 0.52, 0.2), ("CAPITÁN", 70, YELLOW, 0.67, w("era capitán", 129.6) - 127.92)]),
        tr="fade", td=0.2, tex=GFX)
    add(131.08, kb(U("VKJPVFyJnNo"), "in", "doc"), [big("BUSCABA UNA PENDIENTE RAZONABLE", 0.1, 0.86, 64)], tex=CLEAN)
    add(134.7, kb(F(3739002362), "in", "archival"), [big("…QUE LOS TRENES DE LA ÉPOCA PUDIERAN SUBIR", 0.1, 0.86, 58)], tex=ARCH)
    add(137.98, kb(U("Ag6m0LZNwnE"), "in", "doc"), [Stamp("NO LO ENCONTRÓ", 0.0, RED_, (0.5, 0.4), -6, 110),
                                                     big("DEMASIADO ALTA · DEMASIADO CERCA", w("demasiado alta", 140.9) - 137.98, 0.86, 64, YELLOW)], tex=CLEAN)
    add(143.12, cus(G15.ramp, t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(149.16, cus(G15.options, t0=w("una era", 150.5) - 149.16, straight_t=99), [big("DOS OPCIONES", 0.0, 0.5, 120, WHITE, "pop", t1=1.2)], tr="fade", td=0.2, tex=GFX)
    add(155.18, kb(U("Rwv2WSg49e8"), "in", "doc"), [big("ALGO QUE LA COMPAÑÍA NO PODÍA PAGAR", 0.1, 0.86, 60, RED_)], tex=CLEAN)
    add(157.42, cus(G15.options, t0=-9, straight_t=0.3), tr="fade", td=0.2, tex=GFX)
    t0 = w("cañón del río", 160.0)
    add(t0, mp("sg_loc", [(0, -82.33, 35.215, 0.62), (3.0, -82.34, 35.225, 0.7)],
               [*[dict(type="route", ll=l, t0=0.2, draw=1.4, color=BLUE_, width=6) for l in PACOLET],
                dict(type="label", at=(-82.295, 35.19), text="RÍO PACOLET", t0=0.6, size=46, box=True, color=BLUE_),
                dict(type="pin", at="sg_saluda", t0=w("saluda", 163.7) - t0, label="SALUDA", side="l", box=True, size=50)]),
        [big("POR EL CAÑÓN DEL PACOLET, HASTA LA CUMBRE", 0.1, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(164.88, kb(U("-dKftqr_wVE"), "in", "doc"), [big("UN CAÑÓN ESTRECHO, CON PAREDES DE ROCA", 0.1, 0.86, 60)], tex=CLEAN)
    add(w("arroyos", 167.2), V("100209", U("kJdlf_PABnA"), 1.0, "doc"), [big("ARROYOS EN CASCADA", 0.0, 0.86, 76)], tex=CLEAN)
    add(169.48, kb(U("nShLC-WruxQ"), "in", "doc"), [big("Y APENAS SITIO PARA UNA VÍA", 0.0, 0.86, 70)], tex=CLEAN)
    add(171.56, cus(_card, lines=[("PERO ERA CORTO", 80, WHITE, 0.38, 0.0), ("CORTO = BARATO", 130, YELLOW, 0.56, w("corto significa", 174.3) - 171.56)]),
        tr="fade", td=0.2, tex=GFX)
    add(175.98, cus(G15.options, t0=-9, straight_t=-9), [big("ELIGIERON LA SEGUNDA", 0.0, 0.5, 96, YELLOW, "pop")], tr="fade", td=0.2, tex=GFX)
    add(177.4, cus(G15.grade_cmp, t0=99, show_saluda=w("cinco", 180.0) - 177.4), tr="fade", td=0.2, tex=GFX)
    add(182.9, cus(G15.grade_cmp, t0=0.3, show_saluda=-9), tex=GFX)
    add(188.54, kb(U("4ZO31xeiFxw"), "in", "cold"), [big("MÁS DEL DOBLE DE EMPINADA", 0.1, 0.3, 80, YELLOW), big("QUE CASI CUALQUIER LÍNEA PRINCIPAL DEL PAÍS", 1.2, 0.86, 56)],
        tex=CLEAN)
    add(193.36, kb(U("rkFIIE9PxH0"), "in", "archival"), [big("SOBRE EL PAPEL, SOLO UN NÚMERO", 0.1, 0.86, 66)], tex=ARCH)
    add(195.82, kb(U("qefCF3r4Eoc"), "punch", "dark"), [big("PERO ALGUIEN TENÍA QUE CONSTRUIRLA", 0.1, 0.86, 66, YELLOW)], tex=DARK)

    # ============================== CAP 2: LOS PRESOS (198.6 - 302.4)
    bg, ov = chapter(2, "LOS PRESOS QUE LA CONSTRUYERON", U("ydhN7dJBVRw"), g="dark", year="1877–1878")
    add(198.56, bg, ov, tr="black", td=0.2, tex=DARK)
    add(200.56, L("4a10700", kb(U("PDxYfXVlK2M"), "in", "dark"), "«A Southern chain gang», c. 1900 · Detroit Publishing · " + CAP_LOC),
        [Badge("1877", 0.1, None), big("CAROLINA DEL NORTE EMPIEZA A USAR PRESOS DEL ESTADO", 0.4, 0.08, 52, YELLOW), big("PARA CONSTRUIR FERROCARRILES", 1.6, 0.92, 56)],
        tex=ARCH)
    add(208.54, cus(_card, lines=[("MANO DE OBRA", 80, WHITE, 0.4, 0.0), ("CASI GRATIS", 140, YELLOW, 0.56, 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(210.6, L("3a30758", kb(U("a9X7rBh-A5Y"), "in", "dark"), "Presos y guardias, Thomasville (Georgia), c. 1890 · " + CAP_LOC),
        [big("EL ESTADO ALQUILABA SUS PRISIONEROS A LAS COMPAÑÍAS", 0.1, 0.08, 52), big("SOLO TENÍAN QUE DARLES DE COMER Y VIGILARLOS", w("que solo", 213.5) - 210.6, 0.92, 52, YELLOW)],
        tex=ARCH)
    add(216.72, kb(F(55316805664), "in", "doc"), [big("MUCHOS, HOMBRES NEGROS CONDENADOS POR DELITOS PEQUEÑOS", 0.1, 0.08, 50, YELLOW)], tex=CLEAN)
    add(220.1, L("3a38069", kb(U("-T6vP7ZGz0Q"), "in", "dark"), "Cuadrilla de presos, Newport News (Virginia), 1901 · " + CAP_LOC),
        [big("LOS AÑOS DUROS DESPUÉS DE LA GUERRA CIVIL", 0.1, 0.9, 56)], tex=ARCH)
    t0 = 222.64
    add(t0, mp("sg_loc", [(0, -82.336, 35.228, 0.62), (3.8, -82.336, 35.228, 0.68)],
               [dict(type="rail", ll=GRADE, t0=0.2, draw=2.0, color=RAIL, width=6),
                dict(type="pin", at="sg_saluda", t0=0.1, label="SALUDA", side="l", box=True, size=40),
                dict(type="pin", at="sg_melrose", t0=1.6, label="MELROSE", side="r", box=True, size=40)]),
        [big("UNO DE LOS PRIMEROS LUGARES DONDE LOS MANDARON", 0.2, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(226.48, kb(U("eYUsQA9YX0Q"), "punch", "doc"), [big("EL TRABAJO ERA BRUTAL", 0.0, 0.5, 100, RED_, "pop")], tex=CLEAN)
    add(227.74, kb(U("9kziftYx92c"), "in", "doc"), [big("UNA EXPLANACIÓN EN ROCA, COLGADA SOBRE UN BARRANCO", 0.1, 0.86, 54)], tex=CLEAN)
    add(w("apico", 231.4), kb(U("5nCqLHKK468"), "in", "warm"), [rich("PICO · PALA · PÓLVORA", ("pico", "pala", "pólvora"), 0.0, step=0.5, y=0.86, size=80)], tex=CLEAN)
    add(233.66, kb(U("9g7z3e2trRk"), "in", "doc"), [big("CARGAR PIEDRA A MANO", 0.0, 0.86, 76)], tex=CLEAN)
    add(235.2, L("3a38070", kb(U("ydhN7dJBVRw"), "in", "dark"), "Campamento de presos, Florida, c. 1898 · " + CAP_LOC),
        [big("CAMPAMENTOS AL AIRE LIBRE", 0.1, 0.08, 60)], tex=ARCH)
    add(w("con cadenas", 237.6), kb(U("-T6vP7ZGz0Q"), "in", "dark"), [big("CADENAS EN LOS PIES · GUARDIAS ARMADOS", 0.0, 0.86, 62, YELLOW)], tex=DARK)
    add(240.36, L("3a30757", kb(U("U5Rdrv5ZOt8"), "in", "cold"), "«On the chain gang», c. 1890 · " + CAP_LOC), [big("EN INVIERNO, CON NIEVE", 0.0, 0.9, 66, BLUE_)], tex=ARCH)
    add(242.3, kb(U("9H3WouBtk0U"), "in", "warm"), [big("EN VERANO, UN CALOR HÚMEDO QUE NO DEJABA RESPIRAR", 0.0, 0.86, 54, (255, 160, 60))], tex=CLEAN)
    add(245.48, kb(U("9kziftYx92c"), "up", "doc"), [big("LA LADERA CAÍA CASI EN VERTICAL", 0.1, 0.86, 66)], tex=CLEAN)
    add(249.7, L("3a46297", kb(U("-dKftqr_wVE"), "in", "doc"), "Presos de una cuadrilla, c. 1898 · " + CAP_LOC),
        [big("ATADOS CON CUERDAS", 0.1, 0.08, 66, YELLOW), big("PICANDO LA ROCA CON EL VACÍO A LA ESPALDA", w("picando", 252.4) - 249.7, 0.92, 54)], tex=ARCH)
    add(254.7, kb(U("fsj6Ly_lqOs"), "in", "doc"), [rich("ENFERMOS · HERIDOS POR LAS EXPLOSIONES · APLASTADOS POR LAS ROCAS", ("enfermos", "heridos", "aplastados"), 0.2, step=0.35,
                                                       y=0.86, size=50, maxw=0.9)], post=postshake(4), tex=CLEAN)
    add(260.32, cus(_card, lines=[("TANTAS MUERTES QUE EL PARLAMENTO DEL ESTADO…", 50, GREY_, 0.36, 0.0),
                                  ("…ABRIÓ UNA INVESTIGACIÓN ESPECIAL", 84, YELLOW, 0.54, w("abrió", 263.0) - 260.32)]), tr="fade", td=0.2, tex=GFX)
    add(265.32, kb(U("qefCF3r4Eoc"), "in", "dark"), [big("PERO LA OBRA NO SE DETUVO", 0.0, 0.86, 70)], tex=DARK)
    add(267.04, L("3c10533", kb(U("5nCqLHKK468"), "in", "warm"), "Cuadrilla de presos, grabado de 1877 · " + CAP_LOC),
        [big("CUANDO UN HOMBRE CAÍA, LLEGABA OTRO", 0.1, 0.9, 60, YELLOW)], tex=ARCH)
    add(269.42, kb(U("ZLHBjxbCCEc"), "in", "cold"), [big("NADIE LLEVÓ BIEN LA CUENTA", 0.1, 0.3, 70), big("DE CUÁNTOS SE QUEDARON EN ESA LADERA", 1.4, 0.86, 58)], tex=DARK)
    add(273.0, cus(_card, lines=[("4 DE JULIO DE 1878", 120, YELLOW, 0.44, 0.0), ("DÍA DE LA INDEPENDENCIA", 60, WHITE, 0.6, w("el día", 275.8) - 273.0)]), tr="fade", td=0.2,
        tex=GFX)
    add(277.72, kb(U("fRP83Yr4BZw"), "in", "doc"), [big("EL PRIMER TREN LLEGA A LO ALTO DE LA CUESTA", 0.1, 0.12, 56), BigText("SALUDA", "serif", 110, YELLOW, (0.5, 0.82), 1.6, None, "up")],
        tex=CLEAN)
    add(281.1, L("1a34296", kb(U("MjH55Ef3w_0"), "in", "doc"), "Fiesta del 4 de julio en el campo, 1939 · FSA/OWI · " + CAP_LOC),
        [rich("BANDA DE MÚSICA · DISCURSOS · VECINOS", ("música", "discursos", "vecinos"), 0.2, step=0.5, y=0.9, size=58, maxw=0.9)], tex=ARCH)
    add(285.46, kb(U("BHs95lcSsbk"), "punch", "doc"), [big("PARA VER LLEGAR AQUELLA MÁQUINA HUMEANTE", 0.1, 0.86, 58)], tex=CLEAN)
    add(288.52, kb(F(3738201863), "in", "archival"), [big("PARA MUCHOS, LA PRIMERA LOCOMOTORA QUE VEÍAN", 0.1, 0.86, 56)], tex=ARCH)
    t0 = 291.88
    add(t0, mp("sg_reg", [(0, -82.0, 35.0, 1.05), (3.2, -82.0, 35.0, 1.1)],
               [dict(type="rail", ll=LINE, t0=0.1, draw=1.8, color=RAIL, width=6),
                dict(type="pin", at="sg_asheville", t0=0.0, label="LAS MONTAÑAS", side="l", box=True, size=38),
                dict(type="pin", at="sg_spartanburg", t0=1.4, label="EL SUR", side="r", box=True, size=38)]),
        [big("POR FIN, CONECTADAS", 0.4, 0.9, 66, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(295.1, kb(U("Tpn1Z4mQ7Uc"), "in", "cold"), [big("Y ENTONCES EMPEZÓ EL VERDADERO PROBLEMA", 0.1, 0.86, 58)], tex=DARK)
    add(297.9, kb(U("zKDoIU8Svv4"), "in", "doc"), [big("SUBIR: DIFÍCIL", 0.0, 0.86, 90, WHITE, "pop")], tex=CLEAN)
    add(299.86, kb(U("al54F4mvCU8"), "punch", "dark"), [big("BAJAR: MUCHO PEOR", 0.0, 0.86, 90, RED_, "pop")], tex=DARK)

    # ============================== CAP 3: BAJAR ERA PEOR (302.4 - 415.1)
    bg, ov = chapter(3, "BAJAR ERA PEOR", U("M502gf9Qc5k"), g="dark", year="1878–1890")
    add(302.4, bg, ov, tr="black", td=0.2, tex=DARK)
    add(304.52, kb(F(3738195861), "in", "archival"), [big("PIENSA EN UN TREN DE CARGA DE AQUELLOS AÑOS", 0.1, 0.86, 56)], tex=ARCH)
    add(306.94, kb(F(3738200963), "in", "archival"), [big("VAGONES DE MADERA LLENOS DE CARBÓN", 0.1, 0.12, 58), big("DECENAS DE TONELADAS CADA UNO", w("decenas", 309.6) - 306.94, 0.86, 70, YELLOW)], tex=ARCH)
    add(312.24, kb("m_11036792.jpg", "in", "doc"), [big("Y LOS FRENOS NO ERAN COMO LOS DE HOY", 0.1, 0.86, 62)], tex=CLEAN)
    add(314.46, cus(G15.brakes, t0=0.2, rain=False), tr="fade", td=0.2, tex=GFX)
    add(322.04, L("8d15935", cus(G15.brakes, t0=-9, rain=True), "Guardafrenos sobre un tren de carga, 1943 · FSA/OWI · " + CAP_LOC),
        [big("SI LLOVÍA O HELABA, EL TECHO RESBALABA COMO EL HIELO", 0.1, 0.9, 52, BLUE_)], tex=ARCH)
    add(325.24, L("8d15933", kb(U("TqojTmKMXLo"), "in", "doc"), "Guardafrenos sobre un tren de carga, 1943 · FSA/OWI · " + CAP_LOC),
        [big("UNO DE LOS OFICIOS MÁS PELIGROSOS DEL PAÍS", 0.1, 0.9, 56, YELLOW)], tex=ARCH)
    add(328.06, L("8d27514", kb(U("TqojTmKMXLo"), "punch", "doc"), "Guardafrenos subiendo a un vagón, 1943 · FSA/OWI · " + CAP_LOC),
        [big("UN MAL PASO ENTRE DOS VAGONES…", 0.1, 0.12, 60), big("…Y CAÍA A LA VÍA", w("y el guardafrenos", 330.0) - 328.06, 0.9, 70, RED_)], post=postshake(3), tex=ARCH)
    add(332.0, L("99412", kb(U("S9NBbGoZQIA"), "in", "archival"), "Tren de vapor en una pendiente, c. 1920 · " + CAP_LOC),
        [big("EN UNA BAJADA NORMAL, ESO FUNCIONABA", 0.1, 0.9, 58)], tex=ARCH)
    add(334.12, cus(G15.runaway, t0=0.0, span=8.0, top=45, title="EN SALUDA, LA GRAVEDAD EMPUJA"), tr="fade", td=0.2, tex=GFX)
    add(337.24, kb(U("hz42BMifzl0"), "in", "dark"), [big("SI EL TREN AGARRABA VELOCIDAD…", 0.1, 0.3, 62), big("…YA NO HABÍA FORMA DE PARARLO", w("ya no", 339.4) - 337.24, 0.86, 66, RED_)],
        tex=DARK)
    add(341.7, kb(U("_g3ZYDLOuOs"), "in", "dark"), [big("LAS RUEDAS PATINABAN SOBRE EL RIEL MOJADO", 0.1, 0.86, 56)], tex=DARK)
    add(344.1, kb(U("60EerzK0OYM"), "punch", "warm"), [big("LOS FRENOS SE RECALENTABAN", 0.0, 0.3, 66, (255, 140, 40)), big("Y EL TREN SEGUÍA ACELERANDO", 1.4, 0.86, 66)],
        post=postshake(3), tex=CLEAN)
    add(347.38, L("3a15319", kb(U("AJaRUJirtko"), "in", "archival"), "Locomotora tras un accidente, 1885 · " + CAP_LOC),
        [big("UN TREN DESBOCADO EN ESA CUESTA…", 0.1, 0.08, 60), big("…NO TENÍA SALIDA", w("no tenía", 349.0) - 347.38, 0.92, 76, RED_)], tex=ARCH)
    add(350.7, kb(U("zKDoIU8Svv4"), "in", "doc"), [big("PARA SUBIR, EL FERROCARRIL BUSCÓ TRUCOS", 0.1, 0.86, 60)], tex=CLEAN)
    add(353.54, cus(G15.pieces, t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(360.22, kb(F(53584292061), "in", "doc"), [Badge("SALUDA", 0.1, None), big("ARRIBA, LOS VOLVÍA A JUNTAR", 0.3, 0.86, 66)], tex=CLEAN)
    add(362.96, L("99520", kb(F(3738207265), "in", "archival"), "Locomotoras de vapor en una pendiente, 1918 · " + CAP_LOC),
        [big("LOCOMOTORAS DE AYUDA, SIEMPRE ESPERANDO", 0.1, 0.9, 58, YELLOW)], tex=ARCH)
    add(366.46, kb(F(18787809691), "in", "archival"), [big("TRIPULACIONES LISTAS PARA BAJAR A BUSCAR EL SIGUIENTE TROZO", 0.1, 0.9, 50)], tex=ARCH)
    add(370.28, kb(U("P9SW5TUveiw"), "in", "archival"), [rich("LENTO · CARO · SIN FIN", ("lento", "caro", "fin"), 0.0, step=0.5, y=0.86, size=80)], tex=ARCH)
    add(373.14, kb(U("4IsLiMQgbY0"), "in", "doc"), [big("A VECES SUBÍAN MÁS RÁPIDO…", 0.1, 0.86, 64)], tex=CLEAN)
    add(376.08, kb(U("5ZZn4Br2scs"), "punch", "dark"), [big("…DE LO QUE BAJABAN", 0.0, 0.3, 70, YELLOW), big("NADIE SE ATREVÍA A SOLTAR LOS FRENOS", 1.0, 0.86, 58)], tex=DARK)
    add(379.48, kb(U("fbnyneIStG0"), "in", "cold"), [big("AUN ASÍ, LA MONTAÑA COBRÓ SU PRECIO", 0.1, 0.86, 62, YELLOW)], tex=DARK)
    add(382.26, L("3a26339", kb(U("PKeMRO9Gf4Y"), "in", "archival"), "Accidente ferroviario, 1887 · " + CAP_LOC),
        [Badge("1880", 0.1, None), Counter(0, 14, "{:.0f}", "MUERTOS EN LA PENDIENTE", 0.3, 0.8, (0.5, 0.78), 140, color=RED_)], tex=ARCH)
    add(385.98, L("06777", kb(U("AJaRUJirtko"), "in", "archival"), "Accidente ferroviario, 1922 · National Photo Company · " + CAP_LOC),
        [Badge("1886 · UN TREN DESBOCADO", 0.1, None),
         rich("6 PRESOS · 2 GUARDIAS · 1 CAPATAZ", ("6", "2", "1"), w("mató", 387.9) - 385.98, step=0.5, y=0.88, size=70, red=("presos", "guardias", "capataz"))], tex=ARCH)
    add(392.08, cus(_card, lines=[("SE INVESTIGABA", 80, WHITE, 0.34, 0.0), ("SE APUNTABA", 80, WHITE, 0.48, w("se apuntaba", 393.6) - 392.08),
                                  ("SE OLVIDABA", 100, RED_, 0.64, w("se olvidaba", 394.7) - 392.08)]), tr="fade", td=0.2, tex=GFX)
    add(396.56, kb(U("MvF3pDeWdIQ"), "in", "doc"), [rich("MÁS CUIDADO · MÁS PACIENCIA · MENOS VELOCIDAD", ("cuidado", "paciencia", "velocidad"), 0.0, step=0.4, y=0.86, size=58,
                                                         maxw=0.9)], tex=CLEAN)
    add(400.4, kb(U("aroQQ_iz0Jg"), "in", "archival"), [Darken(0.45), big("LOS DIRECTIVOS INSISTÍAN:", 0.1, 0.36, 56, GREY_),
                                                         big("«CON CUIDADO, ERA CASI IMPOSIBLE»", 0.8, 0.52, 76, YELLOW)], tex=ARCH)
    add(406.08, kb(U("rNBaaxyeWWM"), "in", "dark"), [Badge("JUNIO DE 1890", 0.1, None), big("PASÓ LO QUE TODOS DECÍAN QUE ERA IMPOSIBLE", w("pasó", 409.0) - 406.08, 0.86, 56)],
        tex=NIGHT)
    add(411.66, kb(U("JgDUVGAXsso"), "in", "dark"), [big("Y CAMBIÓ PARA SIEMPRE LA FORMA DE BAJAR ESA MONTAÑA", 0.1, 0.86, 52, YELLOW)], tex=NIGHT)

    # ============================== CAP 4: LA NOCHE DEL 17 DE JUNIO (415.1 - 578.0)
    bg, ov = chapter(4, "LA NOCHE DEL 17 DE JUNIO", U("tT_SrSMhhgE"), g="dark", year="1890")
    add(415.06, bg, ov, tr="black", td=0.2, tex=DARK)
    t0 = 419.54
    add(t0, mp("sg_mid", [(0, -82.4, 35.4, 0.6), (5.6, -82.38, 35.3, 0.72)],
               [dict(type="pin", at="sg_asheville", t0=0.0, label="ASHEVILLE", side="r", box=True, size=40),
                dict(type="rail", ll=ASH_SAL, t0=0.4, draw=4.4, color=RAIL, width=6, traffic=1, speed=50),
                dict(type="pin", at="sg_spartanburg", t0=w("spartanburg", 421.9) - t0, label="SPARTANBURG", side="l", box=True, size=40)]),
        [Badge("TREN DE CARGA Nº 11", 0.1, None), big("10 VAGONES DE CARBÓN", w("con 10", 423.4) - t0, 0.9, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(425.22, kb(U("xXlgOWLA2c4"), "in", "archival"), [big("UN VIAJE HECHO DECENAS DE VECES", 0.1, 0.86, 62)], tex=ARCH)
    add(428.92, V("22729", U("AuTZAjMj6Lg"), 0.0, "dark"), [big("NADIE ESPERABA NADA ESPECIAL", 0.0, 0.86, 64)], tex=NIGHT)
    add(430.96, L("99449", kb(U("fE-UheAsalU"), "in", "archival"), "Locomotora de vapor, 1914 · " + CAP_LOC),
        [big("EN LO ALTO, UNA LOCOMOTORA DE AYUDA", 0.1, 0.08, 60), big("PARA SUJETARLO EN LA BAJADA", w("para sujetarlo", 434.5) - 430.96, 0.92, 60, YELLOW)], tex=ARCH)
    add(436.26, cus(_card, lines=[("LA MANEJABA", 56, GREY_, 0.34, 0.0), ("LEWIS TUNSTALL", 130, WHITE, 0.5, 0.3),
                                  ("UNO DE LOS MAQUINISTAS DE MÁS CONFIANZA", 54, YELLOW, 0.66, w("uno de", 438.1) - 436.26)]), tr="fade", td=0.2, tex=GFX)
    add(441.32, kb(U("pgF3KNKPpo4"), "in", "cold"), [big("AÑOS EN ESA MONTAÑA", 0.0, 0.86, 70)], tex=CLEAN)
    add(443.2, kb(U("WhbZOII5xS0"), "in", "dark"), [big("SABÍA CUÁNDO FRENAR… Y CUÁNTO", 0.0, 0.86, 66, YELLOW)], tex=DARK)
    add(446.18, cus(_card, lines=[("JEFE DEL TREN", 56, GREY_, 0.38, 0.0), ("GEORGE RICKETTS", 120, WHITE, 0.54, 0.3)]), tr="fade", td=0.2, tex=GFX)
    add(449.22, cus(G15.brakes, t0=0.0, rain=True), tr="fade", td=0.2, tex=GFX)
    t0 = 455.12
    add(t0, mp("sg_loc", [(0, -82.346, 35.234, 0.75), (2.7, -82.34, 35.232, 0.8)],
               [dict(type="pin", at="sg_saluda", t0=0.0, label="SALUDA", side="l", box=True, size=44),
                dict(type="rail", ll=GRADE, t0=w("empezaron", 456.4) - t0, draw=6.0, color=RED_, width=7)]),
        [big("EMPIEZAN A BAJAR", 0.6, 0.9, 70, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(457.82, kb(U("R9wiKs0USP8"), "in", "dark"), [big("AL PRINCIPIO, TODO IBA BIEN", 0.0, 0.86, 66)], tex=NIGHT)
    add(459.7, kb(U("T2kZBPyLoeM"), "in", "cold"), [big("PERO LOS RIELES ESTABAN MOJADOS", 0.0, 0.86, 64, BLUE_)], tex=NIGHT)
    add(461.74, kb(U("TqojTmKMXLo"), "punch", "dark"), [big("LAS RUEDAS DEJARON DE AGARRAR", 0.1, 0.86, 66, RED_)], post=postshake(4), tex=DARK)
    add(464.9, kb(U("M502gf9Qc5k"), "in", "dark"), [big("LOS FRENOS YA NO HACÍAN NADA", 0.0, 0.86, 70, RED_)], tex=DARK)
    add(467.22, cus(G15.runaway, t0=0.0, span=16.0), [big("EL TREN EMPEZÓ A CORRER", 0.2, 0.92, 60, RED_)], tr="fade", td=0.2, tex=GFX)
    add(469.14, cus(_card, lines=[("LOS PERIÓDICOS LO LLAMARON", 56, GREY_, 0.38, 0.0), ("«UNA CARRERA LOCA»", 120, YELLOW, 0.54, 0.6)]), tr="fade", td=0.15, tex=GFX)
    add(472.34, cus(G15.runaway, t0=-(472.34 - 467.22), span=16.0), [big("SEGÚN ALGUNAS ESTIMACIONES", 0.0, 0.92, 54)], tex=GFX)
    add(478.16, cus(_card, lines=[("UN TREN NORMAL BAJABA…", 64, WHITE, 0.4, 0.0), ("…CASI AL PASO", 110, YELLOW, 0.56, 0.6)]), tr="fade", td=0.15, tex=GFX)
    add(482.42, cus(G15.runaway, t0=-(482.42 - 467.22), span=16.0), [big("3 MILLAS SIN QUE NADIE PUDIERA HACER NADA", 0.0, 0.92, 54, YELLOW)], tex=GFX)
    t0 = 485.52
    add(t0, mp("sg_loc", [(0, -82.33, 35.225, 0.8), (2.5, -82.325, 35.222, 0.86)],
               [dict(type="rail", ll=GRADE, t0=0.0, draw=0.01, color=RED_, width=7),
                dict(type="pin", at="sg_melrose", t0=0.0, label="MELROSE", side="r", box=True, size=46)]),
        [big("AL PIE DE LA MONTAÑA", 0.3, 0.9, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(488.0, L("06778", kb(U("HOIJDtXNu6Y"), "in", "archival"), "Locomotora descarrilada, 1922 · National Photo Company · " + CAP_LOC),
        [big("EN UNA CURVA, SE SALIÓ DE LA VÍA…", 0.0, 0.08, 60), big("…Y SE ESTRELLÓ CONTRA UN ROBLE", w("y se estrelló", 490.0) - 488.0, 0.92, 66, RED_)],
        post=postshake(6), tex=ARCH)
    add(492.26, L("06780", kb(U("y1nV8ldIlDw"), "in", "dark"), "Locomotora volcada, 1922 · National Photo Company · " + CAP_LOC),
        [Darken(0.35), big("TUNSTALL MURIÓ APLASTADO BAJO SU MÁQUINA", 0.2, 0.5, 64, WHITE)], tex=ARCH)
    add(494.98, cus(_card, lines=[("J. J. SMYER · MAQUINISTA", 74, WHITE, 0.36, 0.0), ("WILLIAM TAYLOR · FOGONERO", 74, WHITE, 0.5, w("y el fogonero", 497.5) - 494.98),
                                  ("MURIERON EN EL ACTO", 90, RED_, 0.66, w("murieron", 499.5) - 494.98)]), tr="fade", td=0.2, tex=GFX)
    add(500.76, L("06774", kb(U("PKeMRO9Gf4Y"), "in", "archival"), "Accidente ferroviario, 1922 · National Photo Company · " + CAP_LOC),
        [big("UN GUARDAFRENOS: LAS DOS PIERNAS ROTAS", 0.1, 0.9, 58)], tex=ARCH)
    add(503.52, L("06782", kb(U("HOIJDtXNu6Y"), "in", "archival"), "Accidente ferroviario, 1922 · National Photo Company · " + CAP_LOC),
        [big("OTRO, SEGÚN LOS PERIÓDICOS, PERDIÓ LA VISTA", 0.1, 0.9, 58)], tex=ARCH)
    add(506.0, L("3a26333", kb(U("AJaRUJirtko"), "in", "archival"), "Accidente ferroviario, 1909 · " + CAP_LOC),
        [big("UN TREN DE AUXILIO CON MÉDICOS… Y ENTERRADORES", 0.1, 0.9, 56, YELLOW)], tex=ARCH)
    add(509.82, cus(_card, lines=[("DAÑOS", 60, GREY_, 0.34, 0.0), ("$75.000", 170, YELLOW, 0.5, 0.2), ("UNA FORTUNA PARA LA ÉPOCA", 60, WHITE, 0.66, w("una fortuna", 512.7) - 509.82)]),
        tr="fade", td=0.2, tex=GFX)
    add(514.4, kb(U("tT_SrSMhhgE"), "in", "dark"), [big("PERO LO QUE PESABA NO ERA EL DINERO", 0.1, 0.86, 62)], tex=NIGHT)
    add(516.7, cus(_card, lines=[("HABÍA MUERTO", 80, WHITE, 0.4, 0.0), ("EL MEJOR DE TODOS", 120, YELLOW, 0.56, 0.5)]), tr="fade", td=0.2, tex=GFX)
    q1(518.96, badge="RESPUESTA A LA PREGUNTA 1")
    add(522.16, cus(_card, lines=[("TUNSTALL", 90, WHITE, 0.36, 0.0), ("NO SE EQUIVOCÓ", 120, GREEN_, 0.52, 0.3),
                                  ("HIZO LO DE SIEMPRE, CON LA EXPERIENCIA DE SIEMPRE", 50, GREY_, 0.68, 1.6)]), tr="fade", td=0.2, tex=GFX)
    add(526.52, kb(U("4ZO31xeiFxw"), "in", "cold"), [rich("LA MONTAÑA · LA LLUVIA · UNOS FRENOS QUE NO ESTABAN HECHOS PARA ESO", ("montaña", "lluvia", "frenos"), 0.0, step=0.3,
                                                          y=0.86, size=52, maxw=0.9)], tex=CLEAN)
    add(531.0, kb(U("MvF3pDeWdIQ"), "in", "dark"), [big("SI AL MEJOR LE PODÍA PASAR…", 0.0, 0.3, 64), big("…LE PODÍA PASAR A CUALQUIERA", w("le podía pasar a", 532.8) - 531.0, 0.86, 70, YELLOW)],
        tex=DARK)
    add(534.62, kb(U("HIPH-vbN8Kg"), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("¿TE TIENE AGARRADO AL ASIENTO? SUSCRÍBETE", 0.2, 0.14, 56, YELLOW)],
        tex=DARK)
    add(538.72, kb(U("2PKKbKEkmQE"), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("AQUÍ NO HACE FALTA FRENAR", 0.1, 0.14, 62, YELLOW),
                                                             big("TAMBIÉN EN LA TELE", w("también", 542.4) - 538.72, 0.24, 50)], tex=DARK)
    add(543.76, kb(F(54008316302), "in", "archival"), [Badge("HENDERSONVILLE", 0.1, None), big("ALLÍ ENTERRARON A TUNSTALL", 0.4, 0.86, 64)], tex=ARCH)
    add(546.46, cus(G15.stump, t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(551.9, kb(U("lgbbUZ7VHJI"), "in", "doc"), [big("UN SÍMBOLO ANTIGUO", 0.0, 0.3, 64), big("UNA VIDA CORTADA ANTES DE TIEMPO", w("una vida", 553.3) - 551.9, 0.86, 64, YELLOW)],
        tex=CLEAN)
    add(555.6, cus(G15.stump, t0=-9), [big("TRES LETRAS GRABADAS EN LA PIEDRA", 0.0, 0.08, 56, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(559.68, cus(_card, lines=[("BROTHERHOOD OF LOCOMOTIVE ENGINEERS", 60, WHITE, 0.4, 0.0), ("HERMANDAD DE MAQUINISTAS DE LOCOMOTORA", 70, YELLOW, 0.56, 0.6)]),
        tr="fade", td=0.2, tex=GFX)
    add(561.86, kb(F(3739002362), "in", "archival"), [big("SUS COMPAÑEROS QUISIERON QUE QUEDARA CLARO QUIÉN ERA", 0.1, 0.9, 50)], tex=ARCH)
    add(565.18, kb(U("8ugL4UBc8qM"), "in", "cold"), [big("UN MAQUINISTA QUE MURIÓ EN SU PUESTO", 0.0, 0.86, 64, YELLOW)], tex=CLEAN)
    add(567.52, kb(U("hz42BMifzl0"), "in", "dark"), [big("DESPUÉS DE AQUELLA NOCHE…", 0.0, 0.3, 60), big("…NADIE SE FIÓ DE LOS FRENOS", w("la compañía", 569.0) - 567.52, 0.86, 66, RED_)],
        tex=DARK)
    add(571.5, kb(U("U5Rdrv5ZOt8"), "in", "cold"), [Darken(0.4), rich("¿CÓMO SE PROTEGE UNO DE UNA MONTAÑA QUE NO PERDONA NI AL MEJOR?", ("protege", "mejor?"), 0.1,
                                                                        step=0.1, y=0.5, size=64, maxw=0.8)], tex=DARK)
    add(574.8, kb(U("0ldAi89gjx4"), "punch", "doc"), [big("LO QUE HICIERON TODAVÍA PARECE UNA LOCURA", 0.1, 0.86, 58, YELLOW)], tex=CLEAN)

    # ============================== CAP 5: LA VÍA DE ESCAPE (578.0 - 725.3)
    bg, ov = chapter(5, "LA VÍA DE ESCAPE", U("o4xumntlvYs"), g="doc", year="DESDE 1890")
    add(578.0, bg, ov, tr="black", td=0.2, tex=DARK)
    add(580.7, kb(U("T2kZBPyLoeM"), "in", "doc"), [big("SI NO SE PODÍA PARAR EN LA VÍA PRINCIPAL…", 0.1, 0.12, 56), big("…HABÍA QUE DARLE OTRO SITIO DONDE IR", w("había que", 584.1) - 580.7,
                                                                                                                0.86, 62, YELLOW)], tex=CLEAN)
    t0 = 586.3
    add(t0, mp("sg_loc", [(0, -82.336, 35.228, 0.66), (2.4, -82.336, 35.228, 0.7)],
               [dict(type="rail", ll=GRADE, t0=0.0, draw=0.8, color=RAIL, width=6),
                dict(type="pin", at="sg_saluda", t0=0.0, label="SALUDA", side="l", box=True, size=38),
                dict(type="pin", at="sg_melrose", t0=0.2, label="MELROSE", side="r", box=True, size=38)]),
        [big("VÍAS DE ESCAPE", 0.6, 0.9, 80, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(588.74, cus(G15.safety, mode="idle", t0=0.0), [big("RAMALES CORTOS, CUESTA ARRIBA, HASTA UN MONTÓN DE TIERRA", 0.3, 0.06, 46, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(597.24, cus(G15.safety, mode="runaway", t0=w("se clavaría", 601.8) - 597.24 - 1.8), [big("PERDERÍA VELOCIDAD SUBIENDO", 0.2, 0.06, 50, YELLOW)], tex=GFX)
    add(603.7, L("06776", kb(U("AJaRUJirtko"), "in", "archival"), "Accidente ferroviario, 1922 · National Photo Company · " + CAP_LOC),
        [big("MEJOR UN TREN ROTO EN UNA LADERA…", 0.0, 0.08, 60, YELLOW), big("…QUE UN TREN LLENO DE MUERTOS", w("que un tren", 605.3) - 603.7, 0.92, 64)], tex=ARCH)
    add(608.2, kb(U("f6j5Dol1H_I"), "in", "doc"), [big("PERO LO IMPORTANTE NO ERA LA VÍA…", 0.1, 0.3, 62), big("…ERA CÓMO SE USABA", w("era cómo", 610.4) - 608.2, 0.86, 76, YELLOW)],
        tex=CLEAN)
    add(611.94, kb(U("2IkxeDKaZdY"), "in", "doc"), [big("EL CAMBIO NO APUNTABA A LA VÍA PRINCIPAL", 0.1, 0.86, 60)], tex=CLEAN)
    add(616.86, cus(G15.safety, mode="idle", t0=-9), [big("SIEMPRE HACIA LA VÍA DE ESCAPE", 0.0, 0.06, 64, RED_, "pop")], tr="fade", td=0.15, tex=GFX)
    add(620.34, L("63327", kb(U("zDpgqjqb3cE"), "in", "doc"), "Caseta de guardagujas · Carol M. Highsmith · " + CAP_LOC),
        [big("UN GUARDAGUJAS, EN UNA CASETA AL LADO DE LA VÍA", 0.1, 0.9, 56)], tex=ARCH)
    add(624.48, L("8d11363", kb(U("LBPU8K7loz8"), "in", "dark"), "Guardagujas de noche, 1942 · FSA/OWI · " + CAP_LOC),
        [rich("DE DÍA Y DE NOCHE · LLUVIA · NIEBLA · NIEVE", ("día", "noche", "lluvia", "niebla", "nieve"), 0.0, step=0.4, y=0.9, size=56, maxw=0.9)], tex=ARCH)
    add(628.3, kb(U("2PKKbKEkmQE"), "in", "doc"), [big("EL MAQUINISTA HACÍA SONAR EL SILBATO", 0.1, 0.12, 58), big("«VOY CONTROLADO»", w("para avisar", 631.4) - 628.3, 0.86, 80, GREEN_)],
        tex=CLEAN)
    add(633.76, cus(G15.safety, mode="ok", t0=0.0, whistle_t=0.0, switch_t=w("movía", 637.7) - 633.76), tr="fade", td=0.2, tex=GFX)
    add(640.18, kb(U("MvF3pDeWdIQ"), "in", "doc"), [big("PONTE EN LA CABINA DE UNO DE ESOS TRENES", 0.1, 0.86, 58, YELLOW)], tex=CLEAN)
    add(642.48, kb(U("O5QHHI6xpwc"), "in", "doc"), [big("FRENOS APRETADOS · SILBATO LISTO", 0.0, 0.86, 62)], tex=CLEAN)
    add(646.02, kb(U("PBDD42RMAR4"), "punch", "doc"), [big("LOS OJOS CLAVADOS EN EL CAMBIO", 0.1, 0.86, 64)], tex=CLEAN)
    add(649.24, cus(G15.safety, mode="ok", t0=-9, switch_t=-1), [big("SI LA AGUJA SE MUEVE, RESPIRAS", 0.0, 0.06, 64, GREEN_)], tr="fade", td=0.15, tex=GFX)
    add(651.9, cus(G15.safety, mode="runaway", t0=0.8), [big("SI NO SE MUEVE…", 0.0, 0.94, 56, RED_)], tr="fade", td=0.15, tex=GFX)
    add(657.6, cus(_card, lines=[("COMO UNA PUERTA SIEMPRE CERRADA", 76, WHITE, 0.4, 0.0), ("QUE SOLO SE ABRE SI DEMUESTRAS QUE SABES FRENAR", 54, YELLOW, 0.56,
                                                                                         w("y que solo", 659.7) - 657.6)]), tr="fade", td=0.2, tex=GFX)
    add(663.06, kb(U("AZB6Gg3mhRY"), "in", "dark"), [big("SI EL SILBATO NO SONABA…", 0.0, 0.3, 64), big("…O SI VENÍA DEMASIADO RÁPIDO", w("o si", 664.6) - 663.06, 0.86, 64, RED_)],
        tex=NIGHT)
    add(666.74, cus(G15.safety, mode="runaway", t0=0.2), [big("EL GUARDAGUJAS NO TOCABA NADA", 0.0, 0.94, 52, WHITE)], tr="fade", td=0.15, tex=GFX)
    add(671.06, L("1a34696", kb(U("zDpgqjqb3cE"), "in", "doc"), "Guardagujas junto a una señal, 1939 · " + CAP_LOC),
        [big("LA REGLA ERA SENCILLA", 0.1, 0.9, 64)], tex=ARCH)
    add(673.36, cus(_card, lines=[("EN CASO DE DUDA", 90, WHITE, 0.4, 0.0), ("NO HAGAS NADA", 140, YELLOW, 0.56, 0.6)]), tr="fade", td=0.2, tex=GFX)
    add(676.08, cus(_card, lines=[("SI SE EQUIVOCABA CON UN TREN CONTROLADO:", 50, GREY_, 0.3, 0.0), ("UNAS HORAS PERDIDAS", 80, WHITE, 0.42, w("el ferrocarril", 679.4) - 676.08),
                                  ("SI SE EQUIVOCABA AL REVÉS:", 50, GREY_, 0.6, w("si se equivocaba al", 681.4) - 676.08),
                                  ("VIDAS", 120, RED_, 0.73, w("vidas", 682.9) - 676.08)]), tr="fade", td=0.2, tex=GFX)
    add(684.68, L("06782", kb(U("HOIJDtXNu6Y"), "in", "archival"), "Accidente ferroviario, 1922 · National Photo Company · " + CAP_LOC),
        [big("NO ACABÓ CON TODOS LOS ACCIDENTES", 0.1, 0.9, 60)], tex=ARCH)
    add(687.02, kb(U("gUebCivJHjc"), "in", "doc"), [Badge("1893", 0.1, None), big("UN VAGÓN LLENO DE GANADO", 0.6, 0.86, 70)], tex=CLEAN)
    add(692.68, cus(_card, lines=[("AQUELLA CURVA AÚN SE LLAMA", 56, GREY_, 0.36, 0.0), ("LA CURVA DEL MATADERO", 110, RED_, 0.52, w("la curva", 695.8) - 692.68),
                                  ("SLAUGHTERHOUSE CURVE", 54, WHITE, 0.66, w("la curva", 695.8) - 692.68 + 0.5)]), tr="fade", td=0.2, tex=GFX)
    add(697.48, L("3a30134", kb(U("PKeMRO9Gf4Y"), "in", "archival"), "Accidente ferroviario, 1910 · " + CAP_LOC),
        [Badge("VERANO DE 1903", 0.1, None), big("TRES CHOQUES", 0.6, 0.86, 90, RED_, "pop")], tex=ARCH)
    add(700.36, cus(G15.safety, mode="runaway", t0=-9), [big("PERO LAS VÍAS DE ESCAPE CUMPLIERON", 0.1, 0.94, 56, GREEN_)], tr="fade", td=0.2, tex=GFX)
    add(703.88, L("99392", kb(U("AJaRUJirtko"), "in", "archival"), "Tren descarrilado, 1914 · " + CAP_LOC),
        [big("EMPOTRADOS EN LA TIERRA", 0.1, 0.08, 66), big("VAGONES AMONTONADOS COMO FICHAS DE DOMINÓ", w("con los vagones", 707.6) - 703.88, 0.92, 56, YELLOW)], tex=ARCH)
    add(710.22, L("99385", kb(U("y1nV8ldIlDw"), "in", "archival"), "Tren descarrilado, 1918 · " + CAP_LOC),
        [big("Y LA TRIPULACIÓN SALIÓ POR SU PROPIO PIE", 0.1, 0.9, 58, GREEN_)], tex=ARCH)
    add(712.64, cus(_card, lines=[("LOS TRENES SE ROMPÍAN", 90, WHITE, 0.4, 0.0), ("LOS HOMBRES, CADA VEZ MENOS", 90, GREEN_, 0.56, w("los hombres", 714.4) - 712.64)]),
        tr="fade", td=0.2, tex=GFX)
    add(716.32, V("44268", U("pgF3KNKPpo4"), 0.0, "doc"), [big("DURANTE DÉCADAS, ESA REGLA EXTRAÑA MANTUVO VIVA LA CUESTA", 0.1, 0.86, 50)], tex=CLEAN)
    add(720.24, kb(F(53578613032), "in", "doc"), [Badge("SALUDA", 0.1, None), big("ARRIBA PASABA ALGO QUE NADIE HABRÍA IMAGINADO", 0.4, 0.86, 54, YELLOW)], tex=CLEAN)

    # ============================== CAP 6: EL PUEBLO DE VERANEO (725.3 - 840.2)
    bg, ov = chapter(6, "EL PUEBLO DE VERANEO", F(21950883940), g="archival", year="1890–1964")
    add(725.34, bg, ov, tr="black", td=0.2, tex=DARK)
    add(727.0, kb(U("A56yu_pmNKQ"), "in", "doc"),
        [Badge("FINALES DEL SIGLO XIX", 0.1, None), big("FAMILIAS RICAS DE CHARLESTON Y COLUMBIA", 0.4, 0.9, 58)], tex=ARCH)
    t0 = 731.04
    add(t0, mp("sg_us", [(0, -81.3, 34.2, 2.7), (2.6, -81.4, 34.3, 2.8)],
               [dict(type="pin", at="sg_charleston", t0=0.0, label="CHARLESTON", side="r", box=True, size=36),
                dict(type="pin", at="sg_columbia", t0=0.2, label="COLUMBIA", side="r", box=True, size=36),
                dict(type="route", ll=[(-79.93, 32.78), (-81.03, 34.00), (-82.349, 35.236)], t0=0.6, draw=1.6, color=YELLOW, width=5, dash=18),
                dict(type="pin", at="sg_saluda", t0=1.8, label="SALUDA", side="l", box=True, size=40)]),
        [big("BUSCABAN UN LUGAR FRESCO PARA EL VERANO", 0.1, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(733.66, kb(U("48f_w14IiJg"), "in", "warm"), [big("ESCAPAR DEL CALOR PEGAJOSO DE LA COSTA", 0.1, 0.86, 60, (255, 160, 60))], tex=CLEAN)
    add(737.24, kb(U("c2xLHa-3L8c"), "in", "doc"), [big("Y LO ENCONTRARON EN LO ALTO DE AQUELLA CUESTA", 0.1, 0.86, 56)], tex=CLEAN)
    add(740.52, kb(U("oWvZwcRloC8"), "in", "doc"), [big("LLEGABAN EN TREN, CLARO", 0.0, 0.86, 70)], tex=CLEAN)
    add(742.06, kb(F(4135579919), "in", "archival"), [BigText("CAROLINA SPECIAL", "serif", 104, YELLOW, (0.5, 0.14), w("el carolina", 744.6) - 742.06, None, "up"),
                                                      big("UN TREN DE PASAJEROS ELEGANTE", 0.2, 0.9, 58)], tex=ARCH)
    t0 = w("que unía", 746.6)
    add(t0, mp("sg_us", [(0, -82.2, 35.9, 2.0), (2.6, -82.2, 36.0, 1.9)],
               [dict(type="rail", ll=CSPECIAL, t0=0.0, draw=1.8, color=YELLOW, width=6),
                dict(type="pin", at="sg_charleston", t0=0.0, label="CHARLESTON", side="r", box=True, size=34),
                dict(type="pin", at="sg_cincinnati", t0=1.4, label="CINCINNATI", side="r", box=True, size=34)]),
        tr="zoom", td=0.3, tex=GFX)
    add(748.0, L("33585", kb(U("j8W2oKHjzeo"), "in", "archival"), "Coche de pasajeros del Southern Railway, 1918 · " + CAP_LOC),
        [rich("FAMILIAS · BAÚLES · NIÑOS ASOMADOS A LA VENTANA", ("familias", "baúles", "niños"), 0.6, step=0.5, y=0.9, size=56, maxw=0.9)], tex=ARCH)
    add(752.34, kb(F(23110010971), "in", "archival"), [rich("HOTELES · PENSIONES · CASAS DE VERANO", ("hoteles", "pensiones", "verano"), 0.3, step=0.6, y=0.9, size=58, maxw=0.9)],
        tex=ARCH)
    add(757.14, kb(F(53892218747), "in", "archival"), [big("LA ESTACIÓN SE LLENABA DE GENTE", 0.1, 0.9, 62)], tex=ARCH)
    add(760.48, L("99520", kb(U("fRP83Yr4BZw"), "in", "archival"), "Locomotoras de vapor en una pendiente, 1918 · " + CAP_LOC),
        [big("LLEGABAN JADEANDO A LA CUMBRE, ENVUELTAS EN HUMO", 0.1, 0.9, 54, YELLOW)], tex=ARCH)
    add(763.72, kb(U("7KKQG0eB_TI"), "in", "doc"), [Counter(0, 60, "{:.0f}", "VAGONES", 0.6, 3.0, (0.5, 0.4), 150, color=YELLOW),
                                                    big("LOS NIÑOS CONTABAN VAGONES…", 0.1, 0.12, 60), big("…Y SALUDABAN A LOS MAQUINISTAS", w("y saludando", 767.3) - 763.72, 0.86, 60)],
        tex=CLEAN)
    add(769.46, kb(F(22680367688), "in", "archival"), [big("LA CUESTA PELIGROSA, LA MEJOR ATRACCIÓN DEL PUEBLO", 0.1, 0.9, 52, YELLOW)], tex=ARCH)
    add(774.1, kb(F(26577895004), "in", "doc"), [big("MIENTRAS TANTO, LA VÍA CAMBIÓ DE DUEÑO", 0.1, 0.86, 60)], tex=CLEAN)
    add(776.66, L("4a10878", kb(F(4138985073), "in", "archival"), "Estación del Southern Railway, c. 1900 · Detroit Publishing · " + CAP_LOC),
        [Badge("1895", 0.1, None), BigText("SOUTHERN RAILWAY", "serif", 100, WHITE, (0.5, 0.14), 0.4, None, "up"),
         big("UNA DE LAS GRANDES COMPAÑÍAS DEL SUR", w("una de", 780.6) - 776.66, 0.9, 56, YELLOW)], tex=ARCH)
    add(783.18, kb(U("Msl2GqWaPCo"), "in", "doc"), [rich("FRENOS DE AIRE · LOCOMOTORAS DIÉSEL · CONTROLES MÁS PRECISOS", ("aire", "diésel", "controles"), 0.0, step=0.5, y=0.86,
                                                         size=52, maxw=0.9)], tex=CLEAN)
    add(789.48, cus(G15.safety, mode="idle", t0=-9), [big("LAS VÍAS DE ESCAPE SE QUEDARON", 0.0, 0.06, 64, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(791.5, kb(U("q2QWsSe26mA"), "in", "doc"), [big("BAJANDO A PASO DE TORTUGA", 0.1, 0.12, 66), big("CON LOS FRENOS APRETADOS DURANTE MILLAS", w("con los frenos", 794.6) - 791.5,
                                                                                                          0.86, 56)], tex=CLEAN)
    add(796.86, kb(U("Bt-h01XOQu4"), "in", "warm"), [big("LAS LOCOMOTORAS DE AYUDA SEGUÍAN VIVIENDO EN SALUDA", 0.1, 0.86, 52)], tex=CLEAN)
    add(799.9, kb(F(4138985073), "in", "archival"), [big("AFICIONADOS DE TODO EL PAÍS, CON SUS CÁMARAS", 0.1, 0.12, 56),
                                                     big("PARA VER A LAS MÁQUINAS PELEAR CON LA CUESTA", w("solo para", 803.1) - 799.9, 0.88, 54, YELLOW)], tex=ARCH)
    t0 = 806.28
    add(t0, mp("sg_loc", [(0, -82.33, 35.222, 0.8), (5.4, -82.324, 35.22, 0.95)],
               [dict(type="rail", ll=GRADE, t0=0.0, draw=0.01, color=RAIL, width=6),
                dict(type="pin", at="sg_melrose", t0=w("en melrose", 810.0) - t0, label="MELROSE", side="r", box=True, size=44)]),
        [big("QUEDÓ UNA SOLA VÍA DE ESCAPE", 0.2, 0.1, 62, YELLOW), big("AL PIE DE LA CUESTA", w("al pie", 808.8) - t0, 0.9, 60)], tr="zoom", td=0.3, tex=GFX)
    add(811.68, cus(G15.timer, t0=0.3, fast_t=w("si iba", 822.3) - 811.68), tr="fade", td=0.2, tex=GFX)
    add(825.56, cus(_card, lines=[("EL ÚLTIMO ACCIDENTE GRAVE", 70, WHITE, 0.4, 0.0), ("1964", 170, YELLOW, 0.56, 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(829.32, kb(F(3419124433), "in", "archival"), [big("CASI UNA LEYENDA ENTRE LOS FERROVIARIOS DEL PAÍS", 0.1, 0.9, 54, YELLOW)], tex=ARCH)
    add(834.46, kb(U("kzZ8mpDTSRs"), "in", "doc"), [big("PERO LAS LEYENDAS NO PAGAN LAS FACTURAS", 0.1, 0.12, 60), big("Y EL MUNDO DE ABAJO ESTABA CAMBIANDO", w("y el mundo", 836.8) - 834.46,
                                                                                                                          0.86, 58, YELLOW)], tex=CLEAN)

    # ============================== CAP 7: LAS CUENTAS Y EL AGUA (840.2 - 970.0)
    bg, ov = chapter(7, "LAS CUENTAS Y EL AGUA", U("0Kw44ElHN3A"), g="doc", year="1968–2024")
    add(840.18, bg, ov, tr="black", td=0.2, tex=DARK)
    add(842.04, L("1a11197", kb(U("QrgRXH81DXk"), "in", "archival"), "Main Street, Hendersonville, postal de 1946 · " + CAP_LOC),
        [big("PRIMERO SE FUERON LOS PASAJEROS", 0.0, 0.08, 60, YELLOW), big("AHORA SUBÍAN EN AUTO", 1.6, 0.92, 64)], tex=ARCH)
    add(846.7, kb(F(4144600508), "in", "archival"), [Badge("FINALES DE 1968", 0.1, None), big("EL ÚLTIMO VIAJE DEL CAROLINA SPECIAL", 0.6, 0.9, 58, YELLOW)], tex=ARCH)
    add(851.58, kb(U("zLJgfG2tSwA"), "in", "doc"), [big("DESPUÉS EMPEZÓ A FALLAR LA CARGA", 0.1, 0.86, 62)], tex=CLEAN)
    add(853.72, cus(_card, lines=[("CADA TREN QUE SUBÍA SALUDA NECESITABA:", 50, GREY_, 0.28, 0.0), ("+ LOCOMOTORAS DE AYUDA", 70, WHITE, 0.42, w("necesitaba", 855.8) - 853.72),
                                  ("+ COMBUSTIBLE", 70, WHITE, 0.54, w("más combustible", 857.4) - 853.72), ("+ TIEMPO · + GENTE", 70, YELLOW, 0.66, w("más tiempo", 858.6) - 853.72)]),
        tr="fade", td=0.2, tex=GFX)
    add(860.54, kb(U("7QqASHGpdjE"), "in", "doc"), [big("LOS CAMIONES, POR LAS AUTOPISTAS NUEVAS", 0.1, 0.12, 58), big("SIN TANTAS COMPLICACIONES", 1.4, 0.86, 64, YELLOW)], tex=CLEAN)
    t0 = 864.82
    add(t0, mp("sg_mid", [(0, -82.3, 35.25, 0.5), (6.7, -82.3, 35.25, 0.55)],
               [dict(type="rail", ll=LINE, t0=0.0, draw=0.01, color=RAIL, width=6),
                dict(type="label", at=(-82.95, 35.0), text="OTRAS RUTAS: MÁS LARGAS, MUCHO MÁS FÁCILES", t0=0.8, size=40, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(871.5, cus(_card, lines=[("9 DE DICIEMBRE DE 2001", 110, YELLOW, 0.4, 0.0), ("NORFOLK SOUTHERN, HEREDERA DEL SOUTHERN RAILWAY", 50, WHITE, 0.56,
                                                                                    w("norfolk", 873.7) - 871.5)]), tr="fade", td=0.2, tex=GFX)
    add(876.64, kb(U("JfrgGe-uQOA"), "in", "doc"), [Stamp("SERVICIO SUSPENDIDO", 0.0, RED_, (0.5, 0.5), -6, 100)], tex=CLEAN)
    add(878.32, kb(U("Rwv2WSg49e8"), "in", "cold"), [Counter(0, 123, "{:.0f}", "AÑOS DESPUÉS DEL PRIMER TREN", 0.0, 1.4, (0.5, 0.4), 150, color=YELLOW),
                                                     big("LA CUESTA SE QUEDÓ EN SILENCIO", w("la cuesta", 881.9) - 878.32, 0.86, 64)], tex=CLEAN)
    add(883.72, kb(U("O5QHHI6xpwc"), "in", "doc"), [big("NI CEREMONIA NI DESPEDIDA", 0.0, 0.86, 70)], tex=CLEAN)
    add(885.98, kb(U("arxL6nIJ7_A"), "in", "cold"), [big("UN DÍA, SIMPLEMENTE, DEJARON DE PASAR TRENES", 0.1, 0.86, 56)], tex=CLEAN)
    add(889.5, kb(F(53584292061), "out", "doc"), [big("LOS VECINOS TARDARON SEMANAS EN DARSE CUENTA", 0.1, 0.86, 56)], tex=CLEAN)
    add(893.16, kb(U("g9gc8b_JqnU"), "in", "cold"), [Darken(0.4), rich("¿QUÉ CONSIGUIÓ, POR FIN, SACAR A LOS TRENES DE ESA MONTAÑA?", ("sacar", "montaña?"), 0.1, step=0.1,
                                                                         y=0.5, size=64, maxw=0.8)], tex=DARK)
    add(897.18, cus(_card, lines=[("NI UN CHOQUE · NI UN DESASTRE", 70, WHITE, 0.4, 0.0), ("LAS CUENTAS", 150, YELLOW, 0.57, w("fueron", 899.3) - 897.18)]), tr="fade", td=0.2,
        tex=GFX)
    add(900.64, kb(U("e0bPLaMOv0k"), "in", "doc"), [big("Y FÍJATE EN CÓMO LO HICIERON", 0.0, 0.86, 66, YELLOW)], tex=CLEAN)
    add(902.56, cus(G15.safety, mode="closed", t0=w("echando", 906.2) - 902.56), [Badge("ABRIL DE 2003", 0.1, None)], tr="fade", td=0.2, tex=GFX)
    add(909.16, kb(U("o4xumntlvYs"), "in", "doc"), [big("IGUAL QUE HABÍA SALVADO A SUS TRENES DURANTE UN SIGLO", 0.1, 0.12, 52), big("CON UN MONTÓN DE TIERRA", w("con un montón", 912.1) - 909.16,
                                                                                                                                0.86, 80, YELLOW, "pop")], tex=CLEAN)
    add(913.8, kb(U("sb0Nt_Sk0bo"), "in", "doc"), [big("LOS RIELES SE OXIDARON BAJO LOS ÁRBOLES", 0.1, 0.86, 60)], tex=CLEAN)
    add(917.62, kb(F(8025543263), "in", "doc"), [Badge("MÁS DE 20 AÑOS", 0.1, None), big("UN MANTENIMIENTO MÍNIMO, POR SI ACASO", w("y le hacía", 921.2) - 917.62, 0.86, 58)],
        tex=CLEAN)
    add(924.62, kb(F(22260954498), "in", "doc"), [big("PERO NINGÚN TREN VOLVIÓ A SUBIR", 0.0, 0.86, 64)], tex=CLEAN)
    add(926.5, kb(F(52435458217), "in", "doc"), [big("LOS ARBUSTOS CRECIERON ENTRE LOS DURMIENTES", 0.1, 0.12, 54), big("Y LA VÍA SE VOLVIÓ UN SENDERO", w("y los vecinos", 928.4) - 926.5,
                                                                                                                      0.86, 62, YELLOW)], tex=CLEAN)
    add(932.56, kb(U("ESL1rIs9j48"), "in", "dark"), [Badge("SEPTIEMBRE DE 2024", 0.1, None), BigText("HURACÁN HELENE", "serif", 110, WHITE, (0.5, 0.5),
                                                                                                 w("llegó", 934.8) - 932.56, None, "up")], post=postshake(3), tex=DARK)
    add(936.88, V("4423", U("HhV8vUbxJdM"), 1.0, "dark"), [big("UNA DE LAS PEORES TORMENTAS QUE HAN CAÍDO SOBRE ESAS MONTAÑAS", 0.1, 0.86, 50)], tex=DARK)
    add(941.0, kb(F(54702800979), "in", "doc"), [Badge("ASHEVILLE", 0.1, None), big("LOS RÍOS SE DESBORDARON", 0.3, 0.86, 66)], tex=CLEAN)
    add(943.08, kb(F(54095615728), "in", "doc"), [big("Y ARRASARON BARRIOS ENTEROS", 0.0, 0.86, 66, YELLOW)], tex=CLEAN)
    t0 = 945.4
    add(t0, mp("sg_mid", [(0, -82.29, 35.22, 1.2), (3.8, -82.29, 35.22, 1.32)],
               [dict(type="rail", ll=SAL_TRY, t0=0.2, draw=1.6, color=RED_, width=8),
                dict(type="pin", at="sg_saluda", t0=0.0, label="SALUDA", side="l", box=True, size=40),
                dict(type="pin", at="sg_tryon", t0=0.6, label="TRYON", side="r", box=True, size=40)]),
        [big("LA LLUVIA SE LLEVÓ LA TIERRA DE DEBAJO DE LA VÍA", 0.2, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(949.2, cus(G15.washout, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(953.72, kb(F(54068742981), "in", "doc"), [big("LA MONTAÑA QUE QUISO TIRAR LOS TRENES POR LA LADERA…", 0.1, 0.12, 52)], tex=CLEAN)
    add(957.46, kb(U("13dudPW47eQ"), "in", "doc"), [big("…ACABÓ ECHANDO ABAJO EL PROPIO FERROCARRIL", 0.0, 0.86, 60, RED_)], post=postshake(3), tex=CLEAN)
    add(960.52, cus(_card, lines=[("UN MES DESPUÉS", 70, GREY_, 0.38, 0.0), ("PERMISO PARA ABANDONARLA", 100, RED_, 0.54, w("pidió", 962.0) - 960.52)]), tr="fade", td=0.2, tex=GFX)
    add(964.82, kb(U("MTssq81dPUU"), "in", "cold"), [Counter(0, 146, "{:.0f}", "AÑOS", 0.0, 1.2, (0.5, 0.4), 160, color=YELLOW),
                                                     big("LA MONTAÑA SE HABÍA QUEDADO CON LA VÍA", w("la montaña", 967.1) - 964.82, 0.86, 60)], tex=CLEAN)

    # ============================== CAP 8: HOY (970.0 - 1112.4)
    bg, ov = chapter(8, "LO QUE QUEDA DE LA PENDIENTE", U("EWzWAuS1WYs"), g="doc", year="2025–HOY")
    add(970.0, bg, ov, tr="black", td=0.2, tex=DARK)
    add(972.14, cus(_card, lines=[("JUNIO DE 2025", 90, YELLOW, 0.32, 0.0), ("ORGANIZACIONES DE LAS DOS CAROLINAS COMPRAN LA LÍNEA", 46, WHITE, 0.44, 0.6),
                                  ("$28,5 MILLONES", 150, YELLOW, 0.62, w("28", 977.6) - 972.14)]), tr="fade", td=0.2, tex=GFX)
    add(980.12, kb(F(54702800944), "in", "doc"), [big("EL PRECIO BAJÓ POR LOS DESTROZOS DEL HURACÁN", 0.1, 0.86, 56)], tex=CLEAN)
    add(982.76, kb(U("XUoLEvMjRTQ"), "in", "doc"), [big("EL DINERO: SOBRE TODO, DE LOS GOBIERNOS DE LOS DOS ESTADOS", 0.1, 0.86, 50)], tex=CLEAN)
    add(986.82, kb(U("lZ5UPQzDuSg"), "in", "doc"), [big("LA LEY DEJA LA PUERTA ABIERTA A QUE VUELVAN LOS TRENES", 0.1, 0.12, 50),
                                                    big("AUNQUE NADIE LO ESPERA", w("aunque", 991.3) - 986.82, 0.86, 64, YELLOW)], tex=CLEAN)
    t0 = 993.56
    add(t0, mp("sg_mid", [(0, -82.25, 35.15, 0.75), (8.4, -82.25, 35.15, 0.8)],
               [dict(type="route", ll=TRAIL, t0=0.4, draw=3.0, color=GREEN_, width=8),
                dict(type="pin", at="sg_inman", t0=w("inman", 997.6) - t0, label="INMAN (CAROLINA DEL SUR)", side="r", box=True, size=36),
                dict(type="pin", at="sg_zirconia", t0=w("circonia", 999.6) - t0, label="ZIRCONIA (CAROLINA DEL NORTE)", side="l", box=True, size=36)]),
        [big("UN SENDERO DE UNAS 31 MILLAS · ≈ 50 KM", 0.3, 0.1, 58, GREEN_)], tr="zoom", td=0.3, tex=GFX)
    add(1001.96, kb(F(51634859611), "in", "doc"), [big("PARA CAMINAR…", 0.0, 0.86, 70)], tex=CLEAN)
    add(1002.82, V("44327", U("S57YtJOhTA8"), 0.0, "doc"), [big("…Y PARA IR EN BICI", 0.0, 0.86, 70, GREEN_)], tex=CLEAN)
    add(1004.22, kb(U("MwnGvYexG4I"), "in", "doc"), [big("SI SALE BIEN, BAJARÁS EN BICI…", 0.1, 0.12, 60), big("…FRENANDO CON DOS DEDOS", w("frenando", 1007.7) - 1004.22, 0.86, 70, YELLOW)],
        tex=CLEAN)
    add(1009.24, kb(U("fE-UheAsalU"), "in", "archival"), [big("DONDE TUNSTALL NO PUDO FRENAR CON TODA UNA LOCOMOTORA", 0.1, 0.86, 52)], tex=ARCH)
    add(1013.94, kb(F(53578613032), "in", "doc"), [Badge("SALUDA, HOY", 0.1, None), big("LA VÍA SIGUE CRUZANDO EL CENTRO DEL PUEBLO", 0.4, 0.86, 56)], tex=CLEAN)
    add(1018.24, kb(U("yZW_ZlzCFiQ"), "in", "doc"), [big("LA VIEJA ESTACIÓN ES UN PEQUEÑO MUSEO", 0.1, 0.86, 60)], tex=CLEAN)
    add(1021.08, kb(U("LqOzpnP_ZOw"), "in", "doc"), [Badge("MELROSE", 0.1, None), big("ENTRE LA MALEZA, EL TERRAPLÉN DE LA ÚLTIMA VÍA DE ESCAPE", 0.4, 0.86, 50)], tex=CLEAN)
    add(1027.56, cus(G15.stump, t0=-9), [big("Y EN HENDERSONVILLE, LA LÁPIDA SIGUE AHÍ", 0.0, 0.08, 56, YELLOW)], tr="fade", td=0.2, tex=GFX)
    q2(1031.26, badge="LA GRAN PREGUNTA")
    add(1038.66, kb(U("AuTZAjMj6Lg"), "in", "dark"), [big("PORQUE EN SALUDA NO SE PODÍA CONFIAR EN NADA", 0.1, 0.86, 58, YELLOW)], tex=NIGHT)
    add(1041.54, cus(_card, lines=[("NI EN LOS FRENOS", 76, WHITE, 0.34, 0.0), ("NI EN LOS RIELES MOJADOS", 76, WHITE, 0.48, w("ni en los rieles", 1042.7) - 1041.54),
                                  ("NI EN EL MEJOR MAQUINISTA", 86, YELLOW, 0.64, w("ni siquiera", 1044.4) - 1041.54)]), tr="fade", td=0.2, tex=GFX)
    add(1047.14, kb(U("ZW6RUvsaFTc"), "in", "cold"), [big("LA MONTAÑA PODÍA GANAR A CUALQUIERA", 0.1, 0.86, 64)], tex=CLEAN)
    add(1050.42, kb(U("HwmUiC1vPUE"), "punch", "doc"), [big("ASÍ QUE LE DIERON LA VUELTA A LA REGLA", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)
    add(1053.82, cus(_card, lines=[("NO ESPERAR A QUE ALGO FALLARA:", 64, WHITE, 0.4, 0.0), ("DAR POR HECHO QUE IBA A FALLAR", 90, RED_, 0.56, w("dio por", 1056.3) - 1053.82)]),
        tr="fade", td=0.2, tex=GFX)
    add(1057.92, cus(G15.safety, mode="ok", t0=-9, switch_t=-1), [big("CADA TREN TENÍA QUE GANARSE EL DERECHO A SEGUIR", 0.1, 0.06, 54, GREEN_)], tr="fade", td=0.2, tex=GFX)
    add(1061.52, cus(G15.rule, t0=w("en casi", 1064.4) - 1061.52, flip_t=w("en saluda", 1069.0) - 1061.52), [big("UNA FORMA DE PENSAR AL REVÉS", 0.1, 0.14, 64, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(1073.16, kb(U("JkoYQPW6DBc"), "in", "doc"), [big("FUNCIONÓ DURANTE MÁS DE UN SIGLO", 0.0, 0.86, 66)], tex=CLEAN)
    add(1075.18, kb(U("ZSPRtPwsHwk"), "in", "dark"), [big("PERO LA MONTAÑA TUVO LA ÚLTIMA PALABRA", 0.0, 0.3, 62, YELLOW),
                                                      rich("PRIMERO, LAS CUENTAS · LUEGO, EL AGUA", ("cuentas", "agua"), w("primero", 1078.5) - 1075.18, step=0.5, y=0.86, size=62)],
        tex=DARK)
    add(1081.52, cus(G15.safety, mode="runaway", t0=-9), [big("CON UN MONTÓN DE TIERRA SE SALVABAN LOS TRENES…", 0.1, 0.06, 50, GREEN_)], tr="fade", td=0.2, tex=GFX)
    add(1084.68, cus(G15.safety, mode="closed", t0=0.0), [big("…Y CON UN MONTÓN DE TIERRA SE CERRÓ LA VÍA", 0.1, 0.94, 50, RED_)], tex=GFX)
    add(1089.16, kb(U("zDpgqjqb3cE"), "in", "dark"), [big("AHORA PONTE TÚ EN LA CASETA", 0.1, 0.12, 64, YELLOW), big("ES DE NOCHE, LLUEVE Y UN TREN BAJA PITANDO", w("es de noche", 1091.0) - 1089.16,
                                                                                                                    0.86, 56)], tex=NIGHT)
    add(1094.32, kb(U("AZB6Gg3mhRY"), "in", "dark"), [Darken(0.45), FnOverlay(G4.comments, line1="TE PARECE QUE VIENE UN POCO RÁPIDO…",
                                                                               line2="¿MUEVES LA PALANCA O LO MANDAS CONTRA LA TIERRA?", cta="TE LEO EN LOS COMENTARIOS")], tex=DARK)
    add(1101.84, kb(U("HIPH-vbN8Kg"), "in", "dark", z=1.1), [Darken(0.55), FnOverlay(G2.subscribe), big("SIGUE RECORRIENDO LAS VÍAS QUE ESTADOS UNIDOS DEJÓ ATRÁS", 0.2, 0.14, 50,
                                                                                                          YELLOW)], tex=DARK)
    add(1106.4, kb(U("rWryJFQIF6o"), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("AQUÍ NINGÚN TREN ACABA CONTRA UN MONTÓN DE TIERRA", 0.1, 0.14, 52, YELLOW),
                                                           big("BUENO… CASI NINGUNO", w("bueno", 1110.7) - 1106.4, 0.26, 70, WHITE, "pop")], tex=DARK)
    return S


def pick_f(fid, fallback, cap):
    f = f"f_{fid}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, "archival")
    return fallback


def pick_l(lid, fallback, cap):
    return L(lid, fallback, cap)
