"""The edit: every shot of the Kinzua Bridge video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx10 as G10
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1112.53
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
BLUE = (110, 170, 220)
GREY_ = (160, 160, 160)
IMG = os.path.join(ROOT, "assets", "img")
VIDDIR = os.path.join(ROOT, "assets", "vid")

HAER = "HAER, Library of Congress · vía Wikimedia Commons (dominio público)"
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




# ------------------------------------------------------------------ Kinzua specifics
import json as _json
import math as _math

from engine import ease_io as _eio

BRIDGE = [(-78.5884, 41.7595), (-78.5950, 41.7623)]          # south end -> north end
WM = "Wikimedia Commons"


def _creek_path():
    d = _json.load(open(os.path.join(ROOT, "assets", "map", "kz", "creeks.geojson")))
    pts = []
    for f in d["features"]:
        if f["properties"]["GNIS_NAME"] != "Kinzua Creek":
            continue
        g = f["geometry"]
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            pts += [tuple(p[:2]) for p in ln]
    c = (-78.5917, 41.7609)
    sel = [p for p in pts if p[0] <= c[0] and _math.hypot((p[0] - c[0]) * 83000, (p[1] - c[1]) * 111320) < 1750]
    sel.sort(key=lambda p: p[0])
    return sel[::4] + [c, (-78.5890, 41.7620)]


TORNADO = _creek_path()


def steel_sweep(t, d, t0=0.3, sd=4.0, **kw):
    return G10.viaduct(t, d, "steel", steel=_eio(prog(t, t0, sd)), **kw)


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="u_PySq7yX6hlw.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("Si alguien sabía cómo iba a caer este puente, ¿por qué cayó igual?", ("sabía", "igual?"), size=70),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_Im2gYLhfwmU.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Cómo puede derrumbarse un puente de acero de 1900 por culpa de una pieza de 1882?", ("1900", "1882?"),
                     size=66), tr="glitch", td=0.3, tex=DARK)

    BR = lambda m="full", **kw: cus(G10.viaduct, mode=m, **kw)

    # ============================== INTRO (0 - 65.5)
    add(0.0, kb("f_10930540835.jpg", "in", "doc"), [rich("CAMINAS SOBRE UN VIEJO PUENTE DE TREN", ("tren",), 0.3, y=0.86, size=60)], tex=CLEAN)
    add(3.0, kb("f_15080828510.jpg", "down", "doc"), [big("A CASI 300 PIES SOBRE UN VALLE", 0.2, 0.86, 70, YELLOW)], tex=CLEAN)
    add(6.0, kb("f_6158266022.jpg", "in", "doc"), [big("LOS RIELES DE SIEMPRE", 0.1, 0.86, 72)], tex=CLEAN)
    add(7.8, kb("f_14508848369.jpg", "punch", "doc"), [big("DE PRONTO, LA VÍA SE ACABA", 0.2, 0.86, 76, YELLOW, "pop")], tex=CLEAN)
    add(10.1, V("28343", "u_GFJ6vPY6PpE.jpg", 0.0, "doc"), [big("NI CURVA NI ESTACIÓN", 0.1, 0.86, 72)], tex=CLEAN)
    add(11.9, kb("f_10930675384.jpg", "in", "doc"), [big("SOLO UN PISO DE VIDRIO…", 0.1, 0.84, 72),
                                                  big("…Y DEBAJO, EL VACÍO", w("debajo", 13.4) - 11.9, 0.14, 72, YELLOW)], tex=CLEAN)
    add(15.5, kb("f_15267529465.jpg", "down", "doc"), [big("AHÍ ESTÁ LA OTRA MITAD DEL PUENTE", 0.4, 0.86, 64)], tex=CLEAN)
    add(19.0, kb("f_48814289628.jpg", "in", "doc"), [Darken(0.35), Counter(0, 11, "{:.0f}", "TORRES DE ACERO RETORCIDAS", 0.2, 1.0, (0.5, 0.42), 200)],
        tex=CLEAN)
    add(21.4, kb("f_3925810057.jpg", "l", "doc"), [big("TIRADAS ENTRE LOS ÁRBOLES DESDE 2003", 0.3, 0.86, 62)], tex=CLEAN)
    add(24.6, BR("collapse", fall_t=0.6), [big("MENOS DE 30 SEGUNDOS", 0.2, 0.1, 66, YELLOW)], tr="flash", td=0.2, tex=GFX)
    add(w("un tornado", 26.6), kb("u_onClfj_UleQ.jpg", "punch", "dark"), [big("UN TORNADO DE LOS MÁS DÉBILES", 0.1, 0.86, 70, WHITE)],
        tex=DARK)
    add(28.9, kb("f_3926595982.jpg", "in", "doc"), [big("Y NADIE SE LAS LLEVÓ", 0.1, 0.86, 76, YELLOW)], tex=CLEAN)
    add(30.5, kb("u_nCHP8xRf5Xw.jpg", "in", "dark"), [big("LO INQUIETANTE: ALGUIEN LO VIO VENIR", 0.2, 0.86, 64)], tex=DARK)
    add(33.0, cus(G10.report, kind="2002", times=[0.3, 0.6, 0.9], hl_t=1.6), [big("UN AÑO ANTES, POR ESCRITO", 0.2, 0.06, 56, YELLOW)],
        tr="fade", td=0.25, tex=GFX)
    add(37.9, kb("f_48829570077.jpg", "in", "doc"), [Stamp("CERRADO", 0.2, RED, (0.5, 0.45), -8, 140)], tex=CLEAN)
    add(w("mandaron", 38.9), kb("u_o2l4HsudmlY.jpg", "in", "doc"), [big("UNA CUADRILLA A REPARARLO", 0.1, 0.86, 70),
                                                                  big("Y LA OBRA IBA ADELANTADA", w("y la obra", 40.7) - 38.9, 0.12, 64, YELLOW)],
        tex=CLEAN)
    add(42.4, kb("f_46285579202.jpg", "in", "doc"), [big("AUN ASÍ, CAYÓ CASI COMO LO HABÍAN DESCRITO", 0.2, 0.86, 58)], tex=CLEAN)
    add(45.6, BR("after", checks=[0, 1, 2, 3, 4, 5, 19, 18, 17], check_t=-5),
        [big("LO QUE SIGUE EN PIE TERMINA DONDE LLEGARON LOS REPARADORES", 0.3, 0.1, 52, YELLOW)], tr="fade", td=0.3, tex=GFX)
    add(49.8, kb("u_PySq7yX6hlw.jpg", "in", "dark"), [big("HAY ADVERTENCIAS QUE LLEGAN TARDE", 0.1, 0.42, 72),
                                                    big("ESTA LLEGÓ A TIEMPO… Y NO BASTÓ", w("esta", 51.8) - 49.8, 0.58, 76, YELLOW)], tex=DARK)
    q1(54.1)
    q2(58.3)

    # ============================== CAP 1: EL GENERAL QUE NO QUERÍA DAR RODEOS (65.5 - 187.5)
    bg, ov = chapter(1, "EL GENERAL QUE NO QUERÍA DAR RODEOS", "u_wiGXcdylkEw.jpg", year="1882")
    add(65.5, bg, ov, tr="black", td=0.2, tex=DARK)
    add(68.7, L("86053", kb("u_T1hm6aOPEzk.jpg", "in", "doc"), "Thomas L. Kane · " + LOC_),
        [LowerThird("THOMAS L. KANE", "1822–1883", 0.4)], tex=ARCH)
    add(w("y en 1882", 70.4), kb("u_B6yDtYs2IgY.jpg", "in", "warm"), [big("UNA VIDA PARA VARIAS BIOGRAFÍAS", 0.4, 0.86, 64)], tex=CLEAN)
    add(75.3, kb("u_nCHP8xRf5Xw.jpg", "in", "warm"), [Darken(0.5), big("ABOGADO", 0.1, 0.42, 96, WHITE, "pop"),
                                                    big("CONTRA LA ESCLAVITUD", w("luchó", 76.6) - 75.3, 0.58, 80, YELLOW, "pop")], tex=CLEAN)
    add(78.3, L("20633", kb("u_YEZVoBxezW4.jpg", "in", "bw"), "Bocetos de los Bucktails, 1863 · " + LOC_),
        [big("GUERRA CIVIL: UN REGIMIENTO DE TIRADORES", 0.2, 0.08, 56)], tex=ARCH)
    add(81.1, kb("u_zGpAzM5T5KM.jpg", "in", "warm"), [big("UNA COLA DE VENADO EN EL SOMBRERO", 0.1, 0.86, 64),
                                                    BigText("«BUCKTAILS»", "serif", 110, YELLOW, (0.5, 0.42), w("bucktails", 83.6) - 81.1, None, "pop")],
        tex=CLEAN)
    add(85.1, kb("u_YEZVoBxezW4.jpg", "in", "bw"), [big("HERIDO · CAPTURADO", 0.1, 0.42, 90, WHITE, "pop"),
                                                  big("Y AUN ASÍ, GENERAL", w("y aún", 86.9) - 85.1, 0.58, 90, YELLOW, "pop")], tex=ARCH)
    add(89.4, mp("kz_us", [(0, -95.0, 40.0, 0.62), (7.4, -95.0, 40.0, 0.66)],
                 [dict(type="pin", at="dc", t0=0.3, label="WASHINGTON", side="r", box=True, size=40),
                  dict(type="pin", at="salt_lake_city", t0=w("mormones", 94.8) - 89.4, label="UTAH", side="r", box=True, size=40),
                  dict(type="route", path=["dc", (-87.0, 40.6), (-100.0, 41.5), "salt_lake_city"], t0=w("mormones", 94.8) - 89.4,
                       draw=2.0, color=YELLOW, width=5, dash=18)]),
        [big("MEDIADOR ENTRE LOS MORMONES Y WASHINGTON", w("hizo", 93.7) - 89.4, 0.1, 56, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(96.8, kb("u_PxuLE7N57Ac.jpg", "in", "warm"), [big("A PUNTO DE ENFRENTARSE EN UTAH", 0.2, 0.86, 66)], tex=CLEAN)
    add(100.1, mp("kz_reg", [(0, -77.6, 41.0, 0.75), (5.4, -78.5, 41.6, 1.2)],
                  [dict(type="state", name="Pennsylvania", t0=0.1, color=YELLOW, width=4, alpha=0.8),
                   dict(type="label", at=(-78.0, 41.5), text="NORTE DE PENNSYLVANIA", t0=0.6, dy=-60, size=46, box=True),
                   dict(type="pin", at="kane", t0=w("su apellido", 107.6) - 100.1, label="KANE", side="l", box=True, size=48)]),
        tr="zoom", td=0.3, tex=GFX)
    add(103.1, V("1764", "u_cUs32adw_Ww.jpg", 0.0, "doc"), [big("BOSQUES ESPESOS Y COLINAS", 0.2, 0.86, 70)], tex=CLEAN)
    add(105.6, kb(pick("w_kane_statue.jpg", "u_T1hm6aOPEzk.jpg"), "in", "doc"), [LowerThird("KANE, PENNSYLVANIA", "El pueblo lleva su apellido", 0.3)],
        tex=CLEAN)
    add(109.6, V("41418", "u_DGDLqRFjCoQ.jpg", 0.0, "doc"), [Darken(0.4), Counter(0, 100000, "+{:,.0f}", "ACRES DE BOSQUE · 40.000 HECTÁREAS", 0.2, 1.4,
                                                                   (0.5, 0.42), 170)], tex=CLEAN)
    add(w("la región", 113.4), kb("u_sUHD8WFjkB0.jpg", "in", "dark"), [big("LA REGIÓN ESCONDÍA CARBÓN", 0.1, 0.86, 72, YELLOW)], tex=DARK)
    add(115.1, kb("u_7_MlMgVMuqU.jpg", "punch", "dark"), [big("EL PROBLEMA: SACARLO DE AHÍ", 0.2, 0.86, 72)], tex=DARK)
    bg, ov = card([("KANE PRESIDÍA UNA COMPAÑÍA DE CARBÓN Y FERROCARRIL", 48, GREY_, 0.33, 0.1),
                   ("NEW YORK, LAKE ERIE", 110, WHITE, 0.5, w("la new", 121.3) - 118.3), ("AND WESTERN", 110, WHITE, 0.64, w("la new", 121.3) - 118.3 + 0.4)])
    add(118.3, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(124.0, mp("kz_reg", [(0, -78.6, 41.6, 1.25), (4.0, -78.6, 41.7, 1.45)],
                  [dict(type="pin", at="bradford", t0=0.2, label="BRADFORD", side="r", box=True, size=38),
                   dict(type="pin", at="kane", t0=0.4, label="KANE", side="l", box=True, size=38),
                   dict(type="pin", at="st_marys", t0=0.8, label="MINAS DEL CONDADO DE ELK", side="r", box=True, size=40),
                   dict(type="route", path=["bradford", "kinzua", "mt_jewett", "st_marys"], t0=1.0, draw=2.4, color=YELLOW, width=5)]),
        [big("POR EL CAMINO MÁS DIRECTO", 0.4, 0.1, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(128.1, mp("kz_mid", [(0, -78.62, 41.74, 0.9), (5.1, -78.595, 41.76, 1.3)],
                  [dict(type="pin", at="kinzua", t0=w("valle", 131.4) - 128.1, label="EL VALLE DEL KINZUA", side="r", box=True, size=50),
                   dict(type="pin", at="mt_jewett", t0=0.3, label="MOUNT JEWETT", side="l", box=True, size=38)]),
        [big("EN MEDIO: ALGO QUE NO SE PODÍA MOVER", 0.2, 0.1, 58)], tr="zoom", td=0.3, tex=GFX)
    add(133.2, cus(G10.detour, t0=0.2, t1=w("así que", 141.2) - 133.2 + 1.2), [big("CURVAS Y CUESTAS DURANTE AÑOS", w("eran", 137.5) - 133.2, 0.9, 54)],
        tr="fade", td=0.25, tex=GFX)
    add(147.1, BR("full", dims=0.4), [big("CASI MEDIA MILLA DE LARGO", w("y casi", 151.6) - 147.1, 0.9, 56, YELLOW)], tr="fade", td=0.25, tex=GFX)
    bg, ov = card([("EN 1882 NO EXISTÍA EN EL MUNDO", 60, GREY_, 0.36, 0.1), ("UN PUENTE DE TREN TAN ALTO", 110, YELLOW, 0.55, 0.9)])
    add(154.0, bg, ov, tr="black", td=0.15, tex=GFX)
    add(160.2, L("3c06858", fr("f_4728002306.jpg", "Octave Chanute · SDASM Archives (sin restricciones conocidas)", "bw"),
                 "Octave Chanute · " + LOC_), [LowerThird("OCTAVE CHANUTE", "Ingeniero nacido en París", w("octave", 163.3) - 160.2)],
        tex=ARCH)
    add(164.8, mp("kz_us", [(0, -92.0, 39.5, 0.75), (4.9, -94.6, 39.1, 1.4)],
                  [dict(type="state", name="Missouri", t0=0.2, color=GREY_, width=3, alpha=0.7),
                   dict(type="pin", at="kc_hannibal", t0=w("kansas", 169.1) - 164.8, label="KANSAS CITY", side="r", box=True, size=44)]),
        [big("EL PRIMER PUENTE SOBRE EL RÍO MISSOURI", 0.4, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(169.9, L("00465", fr("f_54798015151.jpg", "Planeador de Chanute, 1896 · " + LOC_, "bw"), "Planeador de Chanute, 1896 · " + LOC_),
        [big("CONSEJOS POR CARTA A LOS HERMANOS WRIGHT", 0.4, 0.08, 56, YELLOW)], tex=ARCH)
    add(176.8, L("3b36053", kb("u_Yn8D5B8C-eY.jpg", "in", "dark"), "Modelo de planeador de Chanute · " + LOC_),
        [big("ANTES DE AYUDAR A NADIE A DESPEGAR…", 0.2, 0.08, 56)], tex=ARCH)
    add(179.7, BR("build", t0=-0.2, build_d=7.4, labels=False), [big("…20 TORRES DE HIERRO SOBRE UN VALLE", 0.2, 0.1, 58, YELLOW),
                                                                big("Y RÁPIDO", w("y hacerlo", 185.2) - 179.7, 0.88, 84, YELLOW, "pop")],
        tr="fade", td=0.25, tex=GFX)

    # ============================== CAP 2: 94 DÍAS Y LA OCTAVA MARAVILLA (187.5 - 324.4)
    bg, ov = chapter(2, "94 DÍAS Y LA OCTAVA MARAVILLA", "w_haer_aerial.jpg", year="1882–1884")
    add(187.5, bg, ov, tr="black", td=0.2, tex=DARK)
    add(189.0, cus(G4.calendar, cards=[("10", "MAYO DE 1882", "EMPIEZA LA OBRA", 0.1, (60, 62, 66))]), tr="fade", td=0.2, tex=GFX)
    add(191.1, mp("kz_reg", [(0, -76.8, 41.0, 0.72), (4.0, -77.6, 41.2, 0.72)],
                  [dict(type="state", name="Pennsylvania", t0=0.0, color=GREY_, width=3, alpha=0.7),
                   dict(type="pin", at="phoenixville", t0=0.2, label="PHOENIX IRON WORKS", side="l", box=True, size=40),
                   dict(type="pin", at="kinzua", t0=0.2, label="KINZUA", side="r", box=True, size=40),
                   dict(type="route", path=["phoenixville", "harrisburg", (-77.6, 41.3), "kinzua"], t0=0.6, draw=2.8, color=YELLOW, width=5)]),
        [big("PIEZAS YA FABRICADAS, CERCA DE FILADELFIA", 0.3, 0.1, 56)], tr="zoom", td=0.3, tex=GFX)
    add(196.7, cus(G10.phoenix, t0=0.3, stave_t=w("como las", 202.5) - 196.7), tr="fade", td=0.25, tex=GFX)
    add(204.4, kb("w_haer_3.jpg", "in", "bw"), [Counter(0, 110, "{:.0f}", "PEDESTALES DE ARENISCA", 0.3, 1.2, (0.5, 0.22), 150),
                                              Caption("Pedestal de arenisca bajo una torre · c. 1900", HAER, 1.6)], tex=ARCH)
    add(208.7, V("50871", "u_PJF04VoMBaE.jpg", 0.0, "doc"), [big("DE LA MISMA LADERA DEL VALLE", 0.1, 0.86, 66)], tex=CLEAN)
    add(211.0, BR("build", t0=0.0, build_d=12.0, labels=False), [big("TORRE TRAS TORRE · SIN ANDAMIOS", 0.3, 0.1, 58, YELLOW)], tr="fade", td=0.25,
        tex=GFX)
    add(215.5, L("4a24872", warp(G10.viaduct, 4.5, 1.0, mode="build", t0=0.0, build_d=12.0), "Grúa de montaje avanzando sobre un viaducto · Lethbridge, c. 1910 · " + LOC_),
        [big("UNA GRÚA SOBRE EL PROPIO PUENTE", 0.3, 0.08, 60, YELLOW)], tex=ARCH)
    add(218.7, warp(G10.viaduct, 7.7, 1.0, mode="build", t0=0.0, build_d=12.0),
        [big("AVANZA SOBRE LO TERMINADO", 0.1, 0.1, 58)], tex=GFX)
    add(222.8, kb("u_LWLlAfKpXew.jpg", "in", "dark"), [big("REMACHANDO HIERRO A LA ALTURA DE 30 PISOS", 0.2, 0.86, 58)], tex=DARK)
    add(227.7, kb("f_48829031043.jpg", "up", "doc"), [big("SIN ARNÉS · CON EL VIENTO EN LA CARA", 0.1, 0.86, 64, YELLOW)], tex=CLEAN)
    add(231.1, cus(G4.calendar, cards=[("29", "AGOSTO DE 1882", "EL PUENTE, LISTO", 0.2, (60, 62, 66))]),
        [Counter(0, 94, "{:.0f} DÍAS", "DE TRABAJO", w("94", 234.3) - 231.1, 1.0, (0.5, 0.88), 80)], tr="fade", td=0.25, tex=GFX)
    add(237.1, BR("full", dims=0.2, steel=0.0), tr="fade", td=0.25, tex=GFX)
    add(245.6, cus(G10.heights, times=[0.2, 1.0, 99]), [big("6 DE SUS 20 TORRES, MÁS ALTAS QUE LAS DEL PUENTE DE BROOKLYN", 0.4, 0.08, 46)],
        tr="fade", td=0.25, tex=GFX)
    add(249.5, L("00756", kb("u_-sQ4FsomXEs.jpg", "in", "doc"), "El puente de Brooklyn, 1883 · " + LOC_), [Badge("NUEVA YORK · 1883", 0.2, None)],
        tex=ARCH)
    add(252.3, kb("w_haer_aerial.jpg", "out", "bw"), [big("EL PUENTE DE TREN MÁS ALTO Y MÁS LARGO DEL MUNDO", 0.2, 0.86, 56, YELLOW),
                                                    Caption("El viaducto desde el aire", HAER, 1.2, y=0.08)], tex=ARCH)
    add(255.5, L("1s08287", kb("w_haer_1.jpg", "in", "bw"), "«The Great Kinzua Bridge», años 1880 · " + LOC_),
        [big("MUCHA GENTE NO SE LO CREÍA", 0.3, 0.08, 62)], tex=ARCH)
    add(259.8, kb("w_haer_6.jpg", "up", "bw"), [big("COLUMNAS TAN DELGADAS QUE PARECÍAN POSTES", 0.2, 0.86, 58)], tex=ARCH)
    add(263.0, kb("u_UuX-Le3bfzc.jpg", "punch", "warm"), [big("¿HECHO DE MADERA?", 0.2, 0.5, 120, YELLOW, "pop")], tex=CLEAN)
    add(266.6, kb("w_haer_5.jpg", "in", "bw"), [big("LOS TRENES TAMPOCO SE FIABAN", 0.2, 0.86, 64), Caption("Un tren sobre el viaducto · c. 1900", HAER, 0.8, y=0.08)],
        tex=ARCH)
    add(269.0, kb("w_haer_2.jpg", "in", "bw"), [Counter(0, 5, "{:.0f} MPH", "≈ 8 KM/H", 0.2, 0.8, (0.5, 0.42), 200)], tex=ARCH)
    add(272.8, kb("w_haer_4.jpg", "in", "bw"), [big("LA ESTRUCTURA VIBRABA", 0.0, 0.86, 76, YELLOW)], tex=ARCH, post=postshake(3.0))
    add(274.6, Solid("dark_grid"), [big("MÁS DESPACIO QUE ALGUIEN TROTANDO", 0.1, 0.45, 84, WHITE, "pop"),
                                    big("Y AUN ASÍ, NO ESPANTÓ A NADIE", w("eso", 276.9) - 274.6, 0.6, 64, YELLOW)], tex=GFX)
    add(278.8, kb("u_haW7JojeC-A.jpg", "in", "warm"), [Darken(0.45), BigText("«LA OCTAVA MARAVILLA", "serif", 104, WHITE, (0.5, 0.44), 0.4, None, "up"),
                                                     BigText("DEL MUNDO»", "serif", 104, YELLOW, (0.5, 0.58), 0.8, None, "up")], tex=CLEAN)
    add(281.7, mp("kz_reg", [(0, -79.0, 42.0, 0.85), (5.5, -78.8, 41.9, 0.95)],
                  [dict(type="pin", at="buffalo", t0=0.2, label="BUFFALO", side="r", box=True, size=40),
                   dict(type="pin", at="pittsburgh_pa", t0=0.5, label="PITTSBURGH", side="r", box=True, size=40),
                   dict(type="pin", at="kinzua", t0=0.1, label="KINZUA", side="r", box=True, size=40),
                   dict(type="route", path=["buffalo", (-78.7, 42.4), "bradford", "kinzua"], t0=0.6, draw=2.2, color=YELLOW, width=5),
                   dict(type="route", path=["pittsburgh_pa", (-79.2, 41.2), "kane", "kinzua"], t0=1.0, draw=2.2, color=YELLOW, width=5)]),
        [big("TRENES DE EXCURSIÓN SOLO PARA CRUZARLO", 0.4, 0.1, 58)], tr="zoom", td=0.3, tex=GFX)
    add(287.2, fr("f_51335779989.jpg", "Tren de excursión sobre el viaducto · David Schnell (dominio público)", "doc"),
        [big("UN PASEO DE DOMINGO", w("en un paseo", 291.2) - 287.2, 0.08, 66, YELLOW)], tex=CLEAN)
    add(292.9, Solid("black"), [big("EL RÉCORD LE DURÓ POCO", 0.1, 0.5, 110, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(294.9, mp("kz_atl", [(0, -40.0, 44.0, 0.75), (3.2, -10.0, 44.0, 0.85)],
                  [dict(type="pin", at="kinzua", t0=0.1, label="KINZUA", side="r", box=True, size=40),
                   dict(type="pin", at="garabit", t0=0.8, label="SUR DE FRANCIA · 1884", side="l", box=True, size=40)]),
        tr="zoom", td=0.3, tex=GFX)
    add(298.0, kb("f_30718169908.jpg", "in", "doc"), [Counter(0, 401, "{:.0f} PIES", "VIADUCTO DE GARABIT", 0.3, 1.2, (0.5, 0.2), 150),
                                                    Caption("Viaducto de Garabit, Francia", "foto: Mike McBey (CC BY 2.0)", 1.0)], tex=CLEAN)
    add(302.1, L("32749", kb("u_OcgYNWmJVQQ.jpg", "in", "bw"), "Gustave Eiffel · " + LOC_), [LowerThird("GUSTAVE EIFFEL", "Su empresa levantó Garabit", 0.6)],
        tex=ARCH)
    add(305.5, kb("u_OcgYNWmJVQQ.jpg", "up", "bw"), [big("UNA TORRE EN PARÍS", 0.1, 0.86, 76, YELLOW)], tex=ARCH)
    add(308.6, L("86053", kb("u_T1hm6aOPEzk.jpg", "in", "doc"), "Thomas L. Kane · " + LOC_),
        [Darken(0.4), big("KANE MURIÓ EN DICIEMBRE DE 1883", w("murió", 311.2) - 308.6, 0.86, 62, YELLOW)], tex=ARCH)
    add(314.8, kb("w_haer_aerial.jpg", "in", "bw"), [big("POCO MÁS DE UN AÑO DESPUÉS", 0.1, 0.86, 64)], tex=ARCH)
    add(317.6, kb("w_haer_aerial.jpg", "out", "bw"), [big("EL PUENTE SOBREVIVIÓ A SU DUEÑO", 0.1, 0.86, 66, YELLOW)], tex=ARCH)
    add(319.6, kb("u_Rd-Nxg7Zd4I.jpg", "in", "dark"), [rich("LO QUE NO IBA A AGUANTAR: EL PESO DE LOS TRENES QUE VENÍAN", ("peso",), 0.2, step=0.09,
                                                            y=0.86, size=54, maxw=0.88)], tex=DARK)

    # ============================== CAP 3: PUENTE NUEVO, PERNOS VIEJOS (324.4 - 464.3)
    bg, ov = chapter(3, "PUENTE NUEVO, PERNOS VIEJOS", "w_haer_4.jpg", g="bw", year="1900")
    add(324.4, bg, ov, tr="black", td=0.2, tex=DARK)
    bg, ov = card([("LA COMPAÑÍA DE KANE QUEBRÓ", 70, GREY_, 0.38, 0.1), ("EL PUENTE PASA AL ERIE RAILROAD", 96, YELLOW, 0.56, 1.6)])
    add(326.6, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(330.3, cus(G10.weights, t0=0.3), tr="fade", td=0.25, tex=GFX)
    add(338.6, Solid("black"), [big("1900: UNA DECISIÓN RADICAL", 0.1, 0.45, 96, WHITE, "pop"),
                                big("NO REFORZARLO: CAMBIARLO ENTERO", w("no lo", 342.0) - 338.6, 0.6, 84, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(345.3, cus(G4.calendar, cards=[("14", "MAYO DE 1900", "ÚLTIMO TREN", 0.2, (60, 62, 66)),
                                       ("24", "MAYO DE 1900", "DESMONTAN EL HIERRO", w("y 10", 348.2) - 345.3, (60, 62, 66)),
                                       ("26", "MAYO DE 1900", "EMPIEZA EL DE ACERO", w("el 26", 351.6) - 345.3, (60, 62, 66))]),
        tr="fade", td=0.25, tex=GFX)
    add(353.6, cus(steel_sweep, t0=0.2, sd=4.4), [big("EN EL MISMO LUGAR Y CON LA MISMA FORMA", w("en el mismo", 355.9) - 353.6, 0.1, 56, YELLOW)],
        tr="fade", td=0.25, tex=GFX)
    bg, ov = card([("DISEÑO: C. R. GRIMM", 100, WHITE, 0.42, 0.1), ("CONSTRUCCIÓN: ELMIRA BRIDGE COMPANY", 64, YELLOW, 0.58, w("y lo", 360.8) - 358.6)])
    add(358.6, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(363.5, kb("u_x19nNMWeo5A.jpg", "in", "doc"), [Counter(0, 3358, "{:,.0f}", "TONELADAS DE ACERO", 0.2, 1.4, (0.5, 0.42), 190),
                                                    big("MÁS DEL DOBLE QUE EL HIERRO DE 1882", w("más del", 367.1) - 363.5, 0.86, 58, YELLOW)], tex=CLEAN)
    add(371.0, kb("w_haer_6.jpg", "in", "bw"), [big("100 A 150 HOMBRES · JORNADAS DE 10 HORAS", 0.2, 0.86, 58),
                                              big("CASI 4 MESES", w("durante", 375.8) - 371.0, 0.12, 64, YELLOW)], tex=ARCH)
    add(377.7, cus(G4.calendar, cards=[("25", "SEPTIEMBRE DE 1900", "VUELVEN LOS TRENES", 0.2, (60, 62, 66))]),
        [Counter(0, 275000, "${:,.0f}", "COSTE DE LA OBRA", w("la obra", 382.8) - 377.7, 1.2, (0.5, 0.88), 80)], tr="fade", td=0.25, tex=GFX)
    add(386.9, kb("f_6157730279.jpg", "in", "doc"), [big("MÁS FUERTE · LISTO PARA LAS GRANDES LOCOMOTORAS", 0.2, 0.86, 56)], tex=CLEAN)
    add(391.8, kb("w_haer_aerial.jpg", "in", "bw"), [big("NUEVO DE ARRIBA ABAJO…", 0.3, 0.86, 70)], tex=ARCH)
    add(395.8, Solid("black"), [big("PERO NO TODO LO ERA", 0.1, 0.5, 110, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(398.1, BR("full", steel=1.0, hl_base=w("empezando", 401.1) - 398.1), [big("LO QUE ESTABA A RAS DE SUELO SE QUEDÓ COMO ESTABA", 0.2, 0.1, 54)],
        tr="fade", td=0.25, tex=GFX)
    add(404.3, cus(G10.bolt, mode="1882", t0=0.2), [big("UNOS 3 CENTÍMETROS", w("unos tres", 412.0) - 404.3, 0.08, 60, YELLOW)], tr="fade", td=0.25, tex=GFX)
    add(413.8, cus(G10.bolt, mode="short", t0=0.4, k_t=w("empalmaron", 421.5) - 413.8), tr="fade", td=0.25, tex=GFX)
    add(425.0, cus(G10.bolt, mode="sleeve", t0=-1.0, labels=False), [big("COMO AÑADIR UN TRAMO A UNA MANGUERA", 0.1, 0.08, 62, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(427.7, kb("u_F2maVHNkbtk.jpg", "in", "warm"), [big("BARATO Y RÁPIDO", 0.1, 0.42, 90, YELLOW, "pop"),
                                                     big("Y EN AQUEL MOMENTO, PARECÍA SUFICIENTE", w("y en", 429.5) - 427.7, 0.58, 60, WHITE)], tex=CLEAN)
    bg, ov = card([("UNOS AÑOS DESPUÉS, EL PROPIO GRIMM RECONOCIÓ", 52, GREY_, 0.36, 0.1),
                   ("ESOS PERNOS TENDRÍAN QUE HABERSE CAMBIADO", 80, YELLOW, 0.55, w("tendrían", 435.7) - 432.0)])
    add(432.0, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(437.4, kb("w_haer_5.jpg", "in", "bw"), [big("PERO YA ESTABA EN SERVICIO", 0.1, 0.86, 66),
                                              big("NADIE IBA A DESMONTAR NADA", w("los trenes", 439.8) - 437.4, 0.12, 64, YELLOW)], tex=ARCH)
    add(443.8, kb("u_Rd-Nxg7Zd4I.jpg", "in", "dark"), [big("MEDIO SIGLO DE TRABAJO", 0.1, 0.86, 70)], tex=DARK)
    add(w("con carbón", 447.5), kb("u_sUHD8WFjkB0.jpg", "punch", "dark"), [big("CARBÓN", 0.0, 0.86, 96, WHITE, "pop")], tex=DARK)
    add(w("madera", 448.3), kb("u_LkFNUzrpDVw.jpg", "punch", "warm"), [big("MADERA", 0.0, 0.86, 96, WHITE, "pop")], tex=CLEAN)
    add(w("madera", 448.3) + 0.7, kb("u_X-o-Pd_FRU4.jpg", "punch", "dark"), [big("PETRÓLEO", 0.0, 0.86, 96, WHITE, "pop")], tex=DARK)
    add(451.4, kb("u_xXIgOWLA2c4.jpg", "in", "bw"), [Badge("OCTUBRE DE 1950", 0.2, None), big("LA ÚLTIMA LOCOMOTORA DE VAPOR", 0.4, 0.86, 64)], tex=ARCH)
    add(457.4, kb("f_6157730279.jpg", "out", "doc"), [big("POR FUERA, RECIÉN HECHO", 0.1, 0.86, 70)], tex=CLEAN)
    add(460.2, cus(G10.bolt, mode="sleeve", t0=-1.0, labels=False), [big("POR DEBAJO, SUS PIES TENÍAN 18 AÑOS MÁS", 0.1, 0.1, 62, YELLOW)],
        tr="fade", td=0.25, tex=GFX)

    # ============================== CAP 4: DEL CHATARRERO AL PARQUE (464.3 - 598.5)
    bg, ov = chapter(4, "DEL CHATARRERO AL PARQUE", "f_6160758020.jpg", year="1959–2002")
    add(464.3, bg, ov, tr="black", td=0.2, tex=DARK)
    add(467.5, kb("u_7_MlMgVMuqU.jpg", "in", "dark"), [big("EL CARBÓN DEJÓ DE PAGAR LA VÍA", 0.1, 0.86, 66)], tex=DARK)
    add(469.6, V("2196", "f_10930568756.jpg", 0.0, "doc"), [big("EL TRÁFICO FUE BAJANDO", 0.1, 0.86, 66)], tex=CLEAN)
    add(471.1, cus(G4.calendar, cards=[("21", "JUNIO DE 1959", "FIN DEL SERVICIO COMERCIAL", 0.2, (60, 62, 66))]), tr="fade", td=0.25, tex=GFX)
    add(477.5, kb("u_y7rls96Zeok.jpg", "in", "dark"), [big("SIN TRENES, SOLO UNA COSA:", 0.1, 0.4, 70),
                                                     big("MILES DE TONELADAS DE ACERO EN VENTA", w("miles", 481.6) - 477.5, 0.56, 64, YELLOW)], tex=DARK)
    add(485.1, kb("u_0x6wy2keS20.jpg", "in", "dark"), [Counter(0, 76000, "${:,.0f}", "A UNA CHATARRERÍA DE INDIANA, PENNSYLVANIA", 0.2, 1.2,
                                                                 (0.5, 0.42), 180)], tex=DARK)
    bg, ov = card([("EL DUEÑO", 52, GREY_, 0.33, 0.1), ("NICK KOVALCHICK", 130, WHITE, 0.5, 0.3),
                   ("SU TRABAJO: CORTAR PUENTES, NO SALVARLOS", 58, YELLOW, 0.67, w("y su", 492.5) - 490.5)])
    add(490.5, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(495.7, kb("f_6157730279.jpg", "in", "doc"), [big("CUANDO VIO LO QUE HABÍA COMPRADO…", 0.1, 0.86, 64)], tex=CLEAN)
    add(499.0, kb("f_10930616054.jpg", "in", "warm"), [Darken(0.5), BigText("«NUNCA HABRÁ OTRO PUENTE COMO ESTE»", "serif", 76, WHITE, (0.5, 0.48), 0.3, None, "up"),
                                                     big("CUENTAN QUE DIJO", 0.1, 0.34, 48, GREY_)], tex=CLEAN)
    add(502.2, cus(G4.calendar, cards=[("—", "OCTUBRE DE 1959", "UN ÚLTIMO DÍA DE TRABAJO", 0.2, (60, 62, 66))]), tr="fade", td=0.25, tex=GFX)
    add(509.5, fr("f_51334324392.jpg", "Un tren sobre el viaducto · David Schnell (dominio público)", "doc"),
        [big("TRENES DESVIADOS, COMO EN LOS VIEJOS TIEMPOS", 0.3, 0.08, 56)], tex=CLEAN)
    add(517.0, kb("f_14508848369.jpg", "in", "doc"), [Stamp("NO LO CORTÓ", 0.1, RED, (0.5, 0.45), -8, 120)], tex=CLEAN)
    add(518.8, mp("kz_reg", [(0, -77.6, 41.0, 0.7), (3.8, -77.6, 41.0, 0.74)],
                  [dict(type="state", name="Pennsylvania", t0=0.1, color=YELLOW, width=4, fill=(80, 70, 30), alpha=0.6)]),
        [big("CONVENCIÓ AL ESTADO DE PENNSYLVANIA PARA QUE LO COMPRARA", 0.2, 0.1, 50, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(522.6, cus(G4.calendar, cards=[("12", "AGOSTO DE 1963", "EL ESTADO LO COMPRA", 0.2, (60, 62, 66))]),
        [big("GOBERNADOR WILLIAM SCRANTON", w("el gobernador", 525.6) - 522.6, 0.08, 56),
         Counter(0, 50000, "${:,.0f}", "", w("firmó", 527.4) - 522.6, 1.0, (0.5, 0.9), 80)], tr="fade", td=0.25, tex=GFX)
    add(530.1, V("2647", "f_15080959508.jpg", 0.0, "doc"), [big("UN PARQUE ESTATAL", 0.2, 0.86, 76), Badge("1970", w("que abrió", 532.7) - 530.1, None)], tex=CLEAN)
    add(535.0, cus(G8.history_line, marks=[("1882", "EL PUENTE DE HIERRO"), ("1900", "EL DE ACERO"), ("1963", "LO COMPRA EL ESTADO"),
                                           ("1977", "REGISTRO HISTÓRICO"), ("1982", "HITO DE LA INGENIERÍA"), ("1987", "VUELVEN LOS TRENES")],
                    title="UNA SEGUNDA VIDA", t0=0.2, step=0.0),
        tr="fade", td=0.25, tex=GFX)
    add(552.0, fr("f_51335779989.jpg", "Knox & Kane Railroad sobre el viaducto · David Schnell (dominio público)", "doc"),
        [big("1987: TRENES LLENOS DE TURISTAS", 0.2, 0.08, 62, YELLOW), LowerThird("KNOX & KANE RAILROAD", "Cruzaban el valle despacio", w("los del", 557.0) - 552.0)],
        tex=CLEAN)
    add(560.4, kb("f_6158266022.jpg", "in", "doc"), [Darken(0.4), Counter(0, 100000, "+{:,.0f}", "PASAJEROS AL AÑO", 0.2, 1.2, (0.5, 0.36), 150),
                                                   Counter(0, 215000, "{:,.0f}", "VISITAS AL PARQUE", w("y el parque", 562.8) - 560.4, 1.2, (0.5, 0.64), 130)],
        tex=CLEAN)
    add(566.2, kb("f_15080828510.jpg", "down", "doc"), [big("POR LA VENTANA NO SE VEÍA EL BORDE…", 0.2, 0.86, 62)], tex=CLEAN)
    add(572.1, kb("f_48829031043.jpg", "up", "doc"), [big("…SINO EL FONDO DEL VALLE, 300 PIES MÁS ABAJO", 0.1, 0.86, 58, YELLOW)], tex=CLEAN)
    add(575.8, V("51448", "u_o4hCKsG3hVw.jpg", 0.0, "doc"), [big("EL ARROYO, COMO UN HILO ENTRE LOS ÁRBOLES", 0.1, 0.86, 58)], tex=CLEAN)
    add(578.4, L("1s08287", kb("w_haer_1.jpg", "in", "bw"), "«The Great Kinzua Bridge», años 1880 · " + LOC_),
        [big("EL MISMO PASEO QUE EN 1882", 0.2, 0.08, 64, YELLOW)], tex=ARCH)
    add(583.1, kb("f_10930616054.jpg", "in", "dark", z=1.1), [Darken(0.55), FnOverlay(G2.subscribe),
                                                           big("LO QUE ENCONTRARON CAMBIÓ EL DESTINO DEL PUENTE", w("porque", 594.1) - 583.1, 0.3, 56, YELLOW)],
        tex=DARK)

    # ============================== CAP 5: LA ADVERTENCIA (598.5 - 719.1)
    bg, ov = chapter(5, "LA ADVERTENCIA", "u_Im2gYLhfwmU.jpg", year="2002–2003")
    add(598.5, bg, ov, tr="black", td=0.2, tex=DARK)
    add(602.0, cus(G10.report, kind="2002", times=[w("acero", 604.6) - 602.0, w("cimientos", 605.9) - 602.0, w("pernos", 609.0) - 602.0],
                   hl_t=w("pernos", 609.0) - 602.0 + 0.6), tr="fade", td=0.25, tex=GFX)
    add(611.1, kb("u_d3KjJHhblTI.jpg", "in", "warm"), [big("EL RESPONSABLE DE LOS PARQUES DEL ESTADO:", 0.1, 0.32, 54, GREY_),
                                                     BigText("«PEOR DE LO QUE SE HABÍA CALCULADO»", "serif", 74, WHITE, (0.5, 0.5),
                                                             w("el deterioro", 615.0) - 611.1, None, "up")], tex=CLEAN)
    add(618.7, kb("u_Wbo15q-W7aI.jpg", "in", "doc"), [big("PIENSA EN UNA SILLA DE CUATRO PATAS", 0.3, 0.86, 64)], tex=CLEAN)
    add(623.5, cus(G10.chair, gust_t=w("pero si", 629.7) - 623.5, bolt_t=w("si esas", 636.8) - 623.5, rot_t=w("si los", 640.8) - 623.5),
        [big("MIENTRAS EL AIRE ESTÁ QUIETO, LA SOSTIENE SU PESO", 0.3, 0.92, 48, (40, 40, 40), t1=w("pero si", 629.7) - 623.5)],
        tr="fade", td=0.25, tex=GFX)
    add(644.0, cus(G10.tower_end, mode="weight", t0=w("contra el", 651.8) - 644.0),
        [big("CADA TORRE ERA ESA SILLA… DE CIENTOS DE PIES", 0.2, 0.16, 54, YELLOW)], tr="fade", td=0.25, tex=GFX)
    add(654.4, cus(G10.tower_end, mode="wind", wind_t=0.1), tr="fade", td=0.2, tex=GFX)
    add(659.7, cus(G10.report, kind="2002", times=[-3, -3, -3], hl_t=-2), [big("Y ESO QUEDÓ POR ESCRITO", 0.1, 0.06, 56, YELLOW)], tr="fade", td=0.25, tex=GFX)
    bg, ov = card([("NO ERA UNA CORAZONADA", 90, GREY_, 0.38, 0.1), ("ERA UN DIAGNÓSTICO", 120, YELLOW, 0.56, w("era un", 668.7) - 667.0),
                   ("MECANISMO CONCRETO · ADVERTENCIA CLARA", 54, WHITE, 0.72, w("con un", 670.0) - 667.0)])
    add(667.0, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(673.4, kb("f_10930616054.jpg", "in", "doc"), [big("EL ESTADO NO LO IGNORÓ", 0.1, 0.86, 70, YELLOW),
                                                    Stamp("2002: CERRADO A LOS TRENES", w("ese mismo", 675.1) - 673.4, RED, (0.5, 0.36), -6, 84),
                                                    Stamp("SEPT. 2002: Y A LOS PEATONES", w("y en septiembre", 677.5) - 673.4, RED, (0.5, 0.56), 5, 74)], tex=CLEAN)
    add(680.8, fr("f_51334324392.jpg", None, "doc"), [big("LOS VAGONES FRENABAN ANTES DE LA PRIMERA TORRE", 0.3, 0.08, 54)], tex=CLEAN)
    add(686.1, cus(G4.calendar, cards=[("—", "FEBRERO DE 2003", "LLEGA LA REPARACIÓN", 0.2, (60, 62, 66))]),
        [big("W. M. BRODE COMPANY · OHIO", w("llegó", 687.4) - 686.1, 0.08, 60, YELLOW)], tr="fade", td=0.25, tex=GFX)
    add(690.6, kb("u_Yn8D5B8C-eY.jpg", "in", "doc"), [Darken(0.5), Counter(0, 10, "+${:.0f} MILLONES", "DE CONTRATO", 0.2, 1.0, (0.5, 0.42), 150)], tex=CLEAN)
    add(693.4, BR("repair", check_t=0.4), [big("TORRE POR TORRE", 0.2, 0.1, 72, YELLOW),
                                          big("REFORZANDO LAS PARTES MÁS BAJAS", w("reforzando", 695.7) - 693.4, 0.9, 56)], tr="fade", td=0.25, tex=GFX)
    add(700.0, cus(G10.bolt, mode="new2011", t0=0.2, labels=False), [big("EL INFORME SEÑALÓ LA BASE…", 0.1, 0.1, 62),
                                                                     big("…Y LA OBRA EMPEZÓ POR LA BASE", w("y la obra", 701.7) - 700.0, 0.2, 62, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(704.4, kb("u_jNxYj6sFEoE.jpg", "in", "doc"), [big("LA OBRA AVANZÓ BIEN", 0.1, 0.86, 70)], tex=CLEAN)
    add(706.0, cus(G4.calendar, cards=[("—", "JULIO DE 2003", "ADELANTADOS AL CALENDARIO", 0.2, (60, 62, 66))]),
        [big("MÁS DE LA MITAD DEL PUENTE", w("y habían", 708.3) - 706.0, 0.9, 60, YELLOW)], tr="fade", td=0.25, tex=GFX)
    add(711.0, BR("repair", check_t=-5), [big("UNA TORRE TRAS OTRA, CON APOYOS NUEVOS", 0.2, 0.1, 58)], tr="fade", td=0.25, tex=GFX)
    add(714.8, kb("u_o2l4HsudmlY.jpg", "out", "doc"), [big("POR PRIMERA VEZ EN MUCHO TIEMPO…", 0.1, 0.42, 64),
                                                     big("EL PUENTE IBA GANANDO LA CARRERA", w("el puente", 716.7) - 714.8, 0.58, 76, YELLOW)], tex=CLEAN)

    # ============================== CAP 6: EL 21 DE JULIO DE 2003 (719.1 - 847.4)
    bg, ov = chapter(6, "EL 21 DE JULIO", "u_wdtAUnoRnlw.jpg", year="2003")
    add(719.1, bg, ov, tr="black", td=0.2, tex=DARK)
    add(721.9, cus(G4.calendar, cards=[("21", "JULIO DE 2003", "LUNES", 0.1, (60, 62, 66))]), tr="fade", td=0.2, tex=GFX)
    add(722.9, V("2221", "u_8IQyd8wEAzI.jpg", 0.0, "dark"), [big("EMPIEZA A LLOVER SOBRE EL VALLE", 0.1, 0.86, 66)], tex=DARK)
    add(724.6, Solid("dark_grid"), [big("POCO ANTES DE LAS 3 DE LA TARDE", 0.1, 0.36, 66, GREY_), big("FLOYD QUILLIN", w("el capataz", 726.0) - 724.6, 0.52, 130, WHITE),
                                    big("CAPATAZ DE LA OBRA", w("el capataz", 726.0) - 724.6 + 0.4, 0.68, 56, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(728.6, kb("u_o2l4HsudmlY.jpg", "in", "dark"), [big("UNA DECISIÓN SENSATA", 0.1, 0.42, 70),
                                                     big("TODOS ABAJO: FIN DE LA JORNADA", w("mandó", 730.3) - 728.6, 0.58, 66, YELLOW)], tex=DARK)
    add(734.2, kb("u_fteR0e2BzKo.jpg", "in", "warm"), [big("ÉL SE QUEDÓ, HACIENDO INVENTARIO", 0.1, 0.86, 64)], tex=CLEAN)
    add(739.2, V("22729", "u_AuTZAjMj6Lg.jpg", 0.0, "dark"), [big("AL SALIR: LLUVIA FUERTE", 0.1, 0.86, 70)], tex=DARK)
    add(741.2, V("4423", "u_L4-16dmZ-1c.jpg", 0.0, "night"), [big("ESTRUENDOS, UNO DETRÁS DE OTRO", 0.2, 0.86, 66, YELLOW),
                                                            Flash(0.3, 0.2), Flash(w("uno detrás", 743.7) - 741.2, 0.2), Flash(w("como", 745.2) - 741.2, 0.2)],
        tex=DARK)
    add(746.7, V("2197", "u_9Nq1lUhhayg.jpg", 0.0, "dark"), [big("HOJAS Y RAMAS VOLANDO", 0.1, 0.86, 72)], tex=DARK, post=postshake(4.0))
    add(749.4, kb("u_laxcXxlLQiA.jpg", "punch", "dark"), [big("A LA CAMIONETA", 0.0, 0.86, 80, WHITE, "pop")], tex=DARK)
    add(750.9, kb("u_BtQj8wWWbpw.jpg", "in", "dark"), [big("LOS ÁRBOLES CASI SE TOCABAN POR ARRIBA", 0.3, 0.86, 60)], tex=DARK, post=postshake(5.0))
    add(757.3, kb("u_EVhuJCqYLxM.jpg", "in", "dark"), [big("LA CASETA DEL GUARDIA", 0.1, 0.36, 70), big("10 × 16 PIES", w("de unos", 758.7) - 757.3, 0.5, 64, GREY_),
                                                     big("SE LEVANTÓ DEL SUELO", w("se levantó", 760.5) - 757.3, 0.64, 80, YELLOW, "pop")], tex=DARK,
        post=postshake(4.0))
    add(762.1, kb("u_v23RO_cLbwA.jpg", "in", "dark"), [big("MARCHA ATRÁS HASTA UNA ALCANTARILLA", 0.1, 0.86, 62)], tex=DARK, post=postshake(3.0))
    add(766.4, Solid("black"), [big("Y DE PRONTO… CALMA", 0.4, 0.5, 110, WHITE, "pop")], tr="black", td=0.1, tex=DARK)
    add(768.6, V("28342", "u_pl4DSTLXD0E.jpg", 0.0, "dark"), [big("DESDE EL CAMINO NO SE VEÍA EL PUENTE", 0.1, 0.86, 62),
                                                     big("SOLO ÁRBOLES DOBLADOS · LLUVIA · RUIDO", w("solo", 772.4) - 768.6, 0.14, 58, YELLOW)], tex=DARK)
    add(775.9, kb("u_onClfj_UleQ.jpg", "in", "dark"), [big("UN TORNADO", 0.2, 0.86, 110, YELLOW, "pop")], tex=DARK)
    add(778.6, mp("kz_loc", [(0, -78.600, 41.756, 0.62), (5.5, -78.594, 41.759, 0.75)],
                  [dict(type="funnel", path=TORNADO, t0=0.3, draw=4.6, swath=46, label="TORNADO F1"),
                   dict(type="route", ll=BRIDGE, t0=0.0, draw=0.1, color=YELLOW, width=7),
                   dict(type="label", at=TORNADO[0], text="TOCA TIERRA A 1 MILLA", t0=0.4, dy=90, size=40, box=True),
                   dict(type="label", at=(-78.5917, 41.7600), text="SUBE POR EL CAUCE DEL ARROYO", t0=w("y subió", 782.2) - 778.6, dy=110, size=40, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(784.2, cus(G10.fscale, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(789.9, cus(G10.gauge, crit_t=99, torn_t=0.2), [big("AL MENOS", 0.1, 0.06, 54, GREY_)], tr="fade", td=0.2, tex=GFX)
    add(795.7, cus(G10.tower_end, mode="wind", wind_t=0.1, labels=True), [big("ENTRÓ EN EL VALLE DE LADO", 0.1, 0.06, 56, YELLOW),
                                                                          big("JUSTO POR DONDE ERA MÁS DÉBIL", w("justo", 797.4) - 795.7, 0.94, 56, RED)],
        tr="fade", td=0.2, tex=GFX)
    add(800.1, Solid("black"), [big("ALGUIEN GRITÓ: «¡EL PUENTE SE HA CAÍDO!»", 0.1, 0.5, 78, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(802.9, kb("f_48814289628.jpg", "in", "doc"), [big("FALTABA TODO EL CENTRO", w("faltaba", 807.3) - 802.9, 0.86, 76, YELLOW)], tex=CLEAN)
    add(808.9, BR("after"), [Counter(0, 11, "{:.0f}", "DE 20 TORRES EN EL SUELO", 0.2, 0.9, (0.5, 0.86), 120)], tr="fade", td=0.2, tex=GFX)
    add(812.0, V("4060", "u_PySq7yX6hlw.jpg", 0.0, "dark"), [big("AQUELLOS ESTRUENDOS…", 0.1, 0.42, 70),
                                                           big("NO ERAN TRUENOS", w("no eran", 815.8) - 812.0, 0.58, 96, YELLOW, "pop")], tex=DARK)
    add(817.2, BR("collapse", fall_t=0.2), [big("ERAN LAS TORRES, UNA DETRÁS DE OTRA", 0.1, 0.1, 58, YELLOW)], tr="flash", td=0.2, tex=GFX,
        post=postshake(2.0))
    add(821.5, kb("f_3925810839.jpg", "in", "doc"), [big("POR CÓMO QUEDARON LOS RESTOS…", 0.1, 0.86, 64)], tex=CLEAN)
    add(823.2, BR("collapse", fall_t=w("tres torres", 825.4) - 823.2 + 2.6), [big("EL CENTRO CEDIÓ PRIMERO", 0.1, 0.1, 64, YELLOW),
                                                                            big("TRES TORRES SE DESPEGARON DE SUS BASES", w("tres torres", 825.4) - 823.2, 0.9, 54),
                                                                            big("COLGADAS DE LOS RIELES", w("colgadas", 829.8) - 823.2, 0.96, 46, GREY_)],
        tr="fade", td=0.2, tex=GFX)
    add(832.6, kb("f_48829570657.jpg", "in", "doc"), [Darken(0.35), big("TODO PASÓ EN MENOS DE", 0.1, 0.34, 60, WHITE),
                                                    big("30 SEGUNDOS", 0.4, 0.5, 150, YELLOW, "pop")], tex=CLEAN)
    bg, ov = card([("NADIE MURIÓ", 130, WHITE, 0.42, 0.1), ("NI RESULTÓ HERIDO", 96, YELLOW, 0.58, 0.6)])
    add(835.1, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(837.0, mp("kz_reg", [(0, -78.4, 41.8, 1.15), (5.6, -78.2, 41.75, 1.2)],
                  [dict(type="pin", at="kinzua", t0=0.1, label="KINZUA · F1", side="l", box=True, size=40),
                   dict(type="cloud", at="potter", t0=0.4, label="CONDADO DE POTTER: OTRO, MUCHO MÁS FUERTE", size=36, bolt=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(842.6, kb("u_H47zWON7sDI.jpg", "in", "dark"), [rich("¿CÓMO PUDO UNO TAN DÉBIL TUMBAR EL PUENTE?", ("débil",), 0.2, step=0.1, y=0.5, size=72, maxw=0.8)],
        tex=DARK)

    # ============================== CAP 7: LOS PERNOS Y LAS ARANDELAS (847.4 - 975.4)
    bg, ov = chapter(7, "LOS PERNOS Y LAS ARANDELAS", "u_F2maVHNkbtk.jpg", year="DICIEMBRE DE 2003")
    add(847.4, bg, ov, tr="black", td=0.2, tex=DARK)
    add(849.9, cus(G10.report, kind="2003", times=[0.6, 1.1, 1.6, 2.1], hl_t=w("en los", 854.4) - 849.9), tr="fade", td=0.25, tex=GFX)
    add(855.3, kb("f_3926595982.jpg", "in", "doc"), [big("EL LADO QUE RECIBIÓ EL VIENTO", w("el que", 858.0) - 855.3, 0.86, 66, YELLOW)], tex=CLEAN)
    add(859.4, cus(G10.four_bases, t0=0.2, t1=w("el perno", 862.7) - 859.4), tr="fade", td=0.2, tex=GFX)
    add(865.0, cus(G10.bolt, mode="snap", t0=0.0, k_t=w("estirado", 867.2) - 865.0), tr="fade", td=0.2, tex=GFX)
    add(868.7, cus(G10.bolt, mode="sleevefail", t0=0.0, k_t=w("aquellos", 871.8) - 868.7), tr="fade", td=0.2, tex=GFX)
    add(877.1, Solid("black"), [big("EL DETALLE MÁS INQUIETANTE", 0.1, 0.5, 100, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(879.4, cus(G10.bolt, mode="sleevefail", t0=-3.0, k_t=0.2, labels=False),
        [big("MUCHOS MANGUITOS YA ESTABAN AGRIETADOS ANTES DEL TORNADO", 0.2, 0.08, 52, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(882.9, cus(G10.clip, t0=0.2, snap_t=w("se parte", 889.6) - 882.9), [big("GRIETAS DE FATIGA", 0.1, 0.06, 62, WHITE)], tr="fade", td=0.2, tex=GFX)
    add(890.4, cus(G10.bolt, mode="washer", t0=0.0, k_t=w("así que", 892.7) - 890.4), tr="fade", td=0.2, tex=GFX)
    add(895.6, kb("u_CsvHNEY7cs8.jpg", "in", "doc"), [big("PODÍAS PASAR CADA DÍA…", 0.1, 0.86, 70),
                                                    big("…Y NO VER NADA", w("y no", 897.8) - 895.6, 0.14, 76, YELLOW)], tex=CLEAN)
    add(899.0, cus(G10.tower_end, mode="lift", lift_t=w("le salió", 904.6) - 899.0),
        [Counter(0, 30, "≈{:.0f} T", "DE TIRÓN HACIA ARRIBA POR TORRE", w("le salió", 904.6) - 899.0, 1.0, (0.5, 0.2), 110)], tr="fade", td=0.2, tex=GFX)
    add(908.0, cus(G10.gauge, crit_t=0.3, torn_t=w("casi", 911.2) - 908.0), tr="fade", td=0.2, tex=GFX)
    add(914.3, V("4059", "u_wdtAUnoRnlw.jpg", 0.0, "dark"), [big("NO HIZO FALTA UNA TORMENTA EXTRAORDINARIA", 0.1, 0.42, 62),
                                                           big("BASTÓ UNA FUERTE, EN EL DÍA EQUIVOCADO", w("bastó", 917.0) - 914.3, 0.58, 66, YELLOW)], tex=DARK)
    add(919.9, cus(G10.tower_end, mode="sway", sway_t=0.3), [big("SE BALANCEARON VARIAS VECES ANTES DE SOLTARSE", 0.2, 0.94, 52, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    q2(924.6, badge="PREGUNTA 2 · LA RESPUESTA")
    add(934.0, cus(steel_sweep, t0=-6.0, sd=1.0, hl_base=w("dejaron", 936.1) - 934.0),
        [big("CAMBIARON EL PUENTE ENTERO…", 0.1, 0.08, 62), big("…Y DEJARON LOS PERNOS", w("dejaron", 936.1) - 934.0, 0.16, 62, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(937.3, cus(G10.visible_vs_hidden, t0=0.2, t1=w("lo que lo", 939.2) - 937.3), [big("CON EMPALMES DE HACÍA UN SIGLO", w("con empalmes", 942.7) - 937.3,
                                                                                         0.8, 56, YELLOW)], tr="fade", td=0.2, tex=GFX)
    bg, ov = card([("EL PROPIO INGENIERO DE 1900 LO HABÍA ADMITIDO", 54, GREY_, 0.38, 0.1),
                   ("ESOS PERNOS DEBÍAN HABERSE CAMBIADO", 84, YELLOW, 0.56, w("esos", 948.1) - 944.8)])
    add(944.8, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(950.6, BR("after", checks=[0, 1, 2, 3, 4, 5, 19, 18, 17], check_t=w("las torres", 953.6) - 950.6),
        [big("LAS TORRES YA REPARADAS NO SE MOVIERON", w("las torres", 953.6) - 950.6, 0.1, 58, GREEN_)], tr="fade", td=0.2, tex=GFX)
    bg, ov = card([("STEPHEN BRODE, DUEÑO DE LA EMPRESA:", 54, GREY_, 0.36, 0.1),
                   ("LAS TORRES QUE HABÍAMOS REPARADO POR COMPLETO", 64, WHITE, 0.52, w("las torres", 959.9) - 956.2),
                   ("AGUANTARON TODO", 110, YELLOW, 0.68, w("aguantaron", 961.9) - 956.2)])
    add(956.2, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(963.7, BR("after", checks=[0, 1, 2, 3, 4, 5, 19, 18, 17], check_t=-5),
        [big("LA LÍNEA ENTRE LO QUE SIGUE EN PIE Y LO QUE ESTÁ EN EL SUELO", 0.1, 0.1, 50),
         big("NO LA TRAZÓ EL VIENTO", w("no la", 967.0) - 963.7, 0.86, 64, WHITE),
         big("LA TRAZÓ EL CALENDARIO DE OBRA", w("la trazó", 968.3) - 963.7, 0.94, 64, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(971.0, kb("f_3925810057.jpg", "in", "doc"), [big("EL ACERO AGUANTÓ EL TORNADO", 0.1, 0.86, 72)], tex=CLEAN)
    add(972.8, cus(G10.bolt, mode="snap", t0=-2.0, k_t=-1.0, labels=False), [big("LOS PERNOS DE HIERRO, NO", 0.1, 0.1, 84, RED, "pop")], tr="flash", td=0.2,
        tex=GFX)

    # ============================== CAP 8: HOY (975.4 - 1065.4)
    bg, ov = chapter(8, "HOY", "f_48814289628.jpg", year="2003–2026")
    add(975.4, bg, ov, tr="black", td=0.2, tex=DARK)
    add(976.7, kb("f_46285579202.jpg", "in", "doc"), [Counter(0, 2000, "{:,.0f}", "PERSONAS AL DÍA FUERON A VERLO", 0.2, 1.0, (0.5, 0.42), 170),
                                                    big("¿DÓNDE PODEMOS DONAR PARA RECONSTRUIRLO?", w("muchas", 979.7) - 976.7, 0.86, 54, YELLOW)], tex=CLEAN)
    add(983.2, kb("f_15080789199.jpg", "in", "doc"), [Counter(0, 45, "${:.0f} MILLONES", "PARA RECONSTRUIRLO", 0.2, 1.0, (0.5, 0.4), 160),
                                                    big("PARA UN PUENTE DE TREN SIN TRENES", w("para un", 986.6) - 983.2, 0.86, 60, YELLOW)], tex=CLEAN)
    add(989.6, kb("f_48829570367.jpg", "in", "doc"), [big("AL FINAL, LO MÁS EXTRAÑO", 0.1, 0.86, 70)], tex=CLEAN)
    add(992.2, Solid("black"), [big("NI LO RECONSTRUYERON", 0.1, 0.42, 96, WHITE, "pop"),
                                big("NI RECOGIERON LOS RESTOS", w("y tampoco", 993.9) - 992.2, 0.58, 96, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(996.7, kb("f_3925809715.jpg", "in", "doc"), [big("LAS TORRES SIGUEN DONDE EL TORNADO LAS DEJÓ", 0.2, 0.86, 58)], tex=CLEAN)
    add(1000.8, fr("f_51335779989.jpg", None, "doc"), [Stamp("2006: FIN DEL KNOX & KANE", 0.3, RED, (0.5, 0.45), -8, 90),
                                                       big("PERDIÓ 3 DE CADA 4 PASAJEROS", w("tras", 1004.6) - 1000.8, 0.9, 58, YELLOW)], tex=CLEAN)
    add(1007.4, kb("f_48829570657.jpg", "up", "doc"), [big("ARREGLARON LAS TORRES QUE SEGUÍAN EN PIE", 0.1, 0.86, 60)], tex=CLEAN)
    add(1011.0, cus(G10.bolt, mode="new2011", t0=w("cada", 1013.8) - 1011.0), [big("ESTA VEZ, NADA DE UN PERNO POR PATA", 0.1, 0.94, 54)],
        tr="fade", td=0.2, tex=GFX)
    add(1020.6, kb("w_phoenix_plate.jpg", "in", "bw"), [Darken(0.5), big("LOS PLANOS ORIGINALES DE 1899", 0.2, 0.86, 64, YELLOW),
                                                      big("GUARDADOS EN EL SMITHSONIAN", w("que estaban", 1025.6) - 1020.6, 0.12, 60)], tex=ARCH)
    add(1028.5, cus(G4.calendar, cards=[("15", "SEPTIEMBRE DE 2011", "ABRE EL KINZUA SKY WALK", 0.2, (60, 62, 66))]), tr="fade", td=0.2, tex=GFX)
    add(1032.8, BR("skywalk", t0=0.2), [big("UNOS 600 PIES SOBRE LAS TORRES QUE QUEDAN", 0.1, 0.1, 56)], tr="fade", td=0.2, tex=GFX)
    add(1036.5, kb("f_10930675384.jpg", "in", "doc"), [big("UN MIRADOR CON PISO DE VIDRIO", 0.1, 0.86, 70, YELLOW)], tex=CLEAN)
    add(1039.2, kb("f_10930540835.jpg", "in", "doc"), [Counter(0, 4.3, "${:.1f} MILLONES", "COSTE DEL SKY WALK", 0.2, 1.0, (0.5, 0.4), 150),
                                                     big("2016: CENTRO DE VISITANTES", w("y en 2016", 1041.3) - 1039.2, 0.86, 60)], tex=CLEAN)
    add(1045.5, kb("f_6158270308.jpg", "in", "doc"), [Badge("2026", 0.2, None), big("NI SIQUIERA ESA MITAD DESCANSA", 0.4, 0.86, 66)], tex=CLEAN)
    add(1049.4, V("4125", "u_8KfCR12oeUM.jpg", 0.0, "warm"), [big("DESDE FINALES DE 2024: EN OBRAS", 0.1, 0.86, 64),
                                                            big("ACERO, PINTURA Y VIDRIO NUEVOS", w("con acero", 1052.6) - 1049.4, 0.14, 60, YELLOW)], tex=CLEAN)
    add(1055.1, cus(G4.calendar, cards=[("4", "SEPTIEMBRE DE 2026", "ABRE", 0.2, (60, 62, 66)), ("31", "OCTUBRE DE 2026", "CIERRA", w("al 31", 1058.5) - 1055.1,
                                                                                                (60, 62, 66))], title="SOLO ESTE TRAMO DEL AÑO"),
        tr="fade", td=0.2, tex=GFX)
    add(1059.9, kb("u_haW7JojeC-A.jpg", "in", "warm"), [Darken(0.35), big("PARA VER LOS COLORES DEL BOSQUE", 0.1, 0.86, 66),
                                                      big("FIN DE LAS OBRAS: OTOÑO DE 2027", w("las obras", 1062.0) - 1059.9, 0.14, 62, YELLOW)], tex=CLEAN)

    # ============================== CONCLUSIÓN (1065.4 - end)
    q1(1065.4, badge="DE VUELTA A LA PREGUNTA 1")
    bg, ov = card([("SABERLO", 130, WHITE, 0.36, 0.1), ("NO ERA LO MISMO QUE", 60, GREY_, 0.5, 0.5), ("TENER TIEMPO", 130, YELLOW, 0.64, 0.9)])
    add(1072.0, bg, ov, tr="flash", td=0.2, tex=GFX)
    add(1074.6, Solid("dark_grid"), [big("LOS INGENIEROS ACERTARON EN EL CÓMO", 0.1, 0.42, 72, WHITE),
                                     big("NADIE PODÍA SABER EL CUÁNDO", w("pero nadie", 1076.8) - 1074.6, 0.58, 80, YELLOW)], tex=GFX)
    add(1078.9, BR("repair", check_t=0.1), [big("LA REPARACIÓN IBA TORRE POR TORRE", 0.1, 0.1, 58)], tr="fade", td=0.2, tex=GFX)
    add(1081.0, BR("collapse", fall_t=0.4, checks=[0, 1, 2, 3, 4, 5, 19, 18, 17], check_t=-5),
        [big("Y EL TORNADO LLEGÓ A MITAD DE CAMINO", 0.1, 0.1, 58, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(1084.0, cus(G10.bolt, mode="washer", t0=-1.0, k_t=0.2, labels=False), [big("EL PUNTO DÉBIL, EL MÁS DIFÍCIL DE VER", 0.1, 0.08, 58),
                                                                              big("ESCONDIDO BAJO LAS ARANDELAS", w("escondido", 1087.0) - 1084.0, 0.16, 58, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    bg, ov = card([("UN AHORRO DE 1900", 120, WHITE, 0.42, 0.1), ("SIN CORREGIR DURANTE MÁS DE 100 AÑOS", 64, YELLOW, 0.58, w("que nadie", 1090.1) - 1088.8)])
    add(1088.8, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(1093.3, kb("f_46285579202.jpg", "out", "doc"), [Darken(0.45), big("LOS INGENIEROS ACERTARON EN TODO…", 0.1, 0.42, 76, WHITE),
                                                      big("…MENOS EN LA FECHA", w("menos", 1095.4) - 1093.3, 0.58, 110, YELLOW, "pop")], tex=CLEAN)
    add(1096.8, kb("u_LCS7oXArC-A.jpg", "out", "bw"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿HAS VIVIDO ALGO ASÍ? UNA GOTERA, UNA PARED,",
                                 line2="UN CARRO CON UN RUIDO RARO… ¿A TIEMPO O UN DÍA TARDE?", cta="CUÉNTALO EN LOS COMENTARIOS"),
         rich("A veces lo que más importa es lo que no se ve", ("no", "se", "ve"), w("a veces", 1109.7) - 1096.8 - 0.3, step=0.08, y=0.2, size=50, maxw=0.85)],
        tex=DARK)
    return S


GREEN_ = (80, 190, 110)
