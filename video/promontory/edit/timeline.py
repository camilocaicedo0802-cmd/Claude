"""The edit: every shot of the Promontory Summit video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx7 as G7
import gfx14 as G14
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1095.92
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












# ------------------------------------------------------------------ Promontory specifics
OLD = M.pm_ll("old")
CUT = M.pm_ll("cutoff")
CP = M.pm_ll("cp")
UP = M.pm_ll("up")
STAGE = M.pm_ll("stage")
CAP_LOC = "Library of Congress"
F = lambda i: f"f_{i}.jpg"
N = lambda i: f"n_{i}.jpg"
RED_ = (230, 70, 60)
BLUE_ = (110, 170, 220)
GREEN_ = (90, 210, 120)
CYAN = (90, 220, 255)
CPC = (230, 110, 60)
UPC = (110, 170, 230)
GOLD = (236, 190, 70)
COAST = [(-74.006, 40.713), (-75.165, 39.953), (-80.0, 40.44), (-84.5, 41.0), (-87.63, 41.88), (-91.5, 41.6), (-95.93, 41.26)]
SHAKE = F(53755586094)     # «East and West shaking hands at laying last rail», A. J. Russell, 10 May 1869 (restored scan)


def _card(t, dur, lines=()):
    from gfx import background
    img = background("dark_grid", t)
    for tx, sz, col, y, t0 in lines:
        G2.label(img, tx, 960, 1080 * y, ease_out(prog(t, t0, 0.4)), sz, col)
    return img


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="u_93rTRYRAvi4.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Cómo pudo quedarse sin trenes la vía más famosa del país, sin que nadie la cerrara?", ("trenes", "nadie"), size=66),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_saS98jKhVjA.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Por qué Estados Unidos hizo una fiesta para desmontar el ferrocarril que lo había unido?", ("fiesta", "desmontar"), size=66),
            tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 62.2)
    add(0.0, kb(F(4048831870), "in", "doc"), [rich("IMAGINA ARRANCAR A PROPÓSITO…", ("arrancar",), 0.3, step=0.12, y=0.84, size=64, maxw=0.8)], tex=CLEAN)
    add(2.3, kb(F(1701193034), "punch", "archival"), [big("…EL FERROCARRIL MÁS FAMOSO DE TU PAÍS", 0.0, 0.86, 64, YELLOW)], tex=ARCH)
    add(4.02, mp("pm_us", [(0, -98.0, 40.0, 0.63), (4.4, -98.0, 40.0, 0.66)],
                 [dict(type="label", at=(-71.0, 36.5), text="ATLÁNTICO", t0=w("atlántico", 6.8) - 4.02, size=46, box=True, color=BLUE_),
                  dict(type="label", at=(-125.0, 36.0), text="PACÍFICO", t0=w("pacífico", 7.8) - 4.02, size=46, box=True, color=BLUE_),
                  dict(type="rail", ll=COAST + UP, t0=0.2, draw=1.6, color=UPC, width=6),
                  dict(type="rail", ll=[(-122.27, 37.80)] + CP, t0=0.6, draw=1.4, color=CPC, width=6)]),
        [big("LA PRIMERA VÍA DE COSTA A COSTA", 0.2, 0.1, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(8.48, V("52012", "u_RyCvLcn1FJc.jpg", 0.0, "warm"), [Badge("SEPTIEMBRE DE 1942", 0.1, None), big("EN EL DESIERTO DE UTAH", 0.5, 0.86, 72)], tex=CLEAN)
    add(w("lo hizo", 12.0), kb("u_xlW6BalTOHw.jpg", "in", "warm"), [big("ESTADOS UNIDOS LO HIZO…", 0.0, 0.3, 72),
                                                                big("…Y LO CELEBRÓ", w("celebró", 13.6) - w("lo hizo", 12.0), 0.86, 96, YELLOW, "pop")], tex=CLEAN)
    add(14.94, kb(F(22852991529), "in", "doc"), [big("DOS LOCOMOTORAS FRENTE A FRENTE", 0.2, 0.86, 68)], tex=CLEAN)
    add(17.48, cus(G14.spike, mode="pull", t0=0.0, inch=False), tr="fade", td=0.2, tex=GFX)
    add(20.8, cus(_card, lines=[("300", 200, YELLOW, 0.44, 0.0), ("PERSONAS APLAUDIERON", 70, WHITE, 0.62, 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(22.62, cus(_card, lines=[("EN PRIMERA FILA…", 60, GREY_, 0.36, 0.1), ("UNA ANCIANA DE 85 AÑOS", 96, WHITE, 0.52, 0.5)]), tex=GFX)
    add(25.94, kb(F(34594793542), "in", "archival"), [Badge("1869", 0.1, None), big("CON 12 AÑOS, HABÍA VISTO CLAVAR ESA VÍA", 0.3, 0.86, 60, YELLOW),
                                                        big("EN ESE MISMO SITIO", w("en ese", 27.9) - 25.94, 0.94, 46)], tex=ARCH)
    add(28.98, cus(G14.teardown, t0=0.0, title=False), [big("DESPUÉS LLEGARON LAS CUADRILLAS", 0.1, 0.11, 62, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(31.52, L("8c34159", kb("u_HGCqL-tRcac.jpg", "in", "archival"), "Recogida de chatarra en Fort Kent (Maine), 1942 · FSA/OWI · " + CAP_LOC),
        [Counter(0, 100, "{:.0f}", "MILLAS DE RIELES EN UN MES", 0.0, 1.2, (0.5, 0.42), 150, prefix="+"),
         big("…Y EL ACERO, A LA GUERRA", w("mandaron", 33.9) - 31.52, 0.9, 62, RED_)], tex=ARCH)
    add(35.9, kb(F(1588802176), "in", "doc"), [big("EL CLAVO DEL GOBERNADOR…", 0.0, 0.3, 64), Stamp("PERDIDO", w("perdió", 37.4) - 35.9, RED_, (0.5, 0.62), -8, 120)],
        tex=CLEAN)
    add(38.36, kb(F(49225875482), "in", "doc"), [big("NI SIQUIERA ERA EL FAMOSO CLAVO DE ORO", 0.2, 0.86, 62, GOLD)], tex=CLEAN)
    add(w("que había", 40.6), kb(F(2167001390), "punch", "dark"), [big("ESE HABÍA DESAPARECIDO DE LA VÍA MUCHO ANTES", 0.1, 0.86, 56)], tex=DARK)
    add(43.2, kb(F(54573177158), "in", "doc"), [Darken(0.35), big("«EL LUGAR SE LLAMABA»", 0.0, 0.34, 50, GREY_),
                                                BigText("PROMONTORY SUMMIT", "serif", 120, WHITE, (0.5, 0.5), 0.3, None, "up")], tr="fade", td=0.3, tex=CLEAN)
    add(45.84, kb(F(26234958554), "in", "doc"), [big("LO MÁS RARO:", 0.0, 0.3, 64, YELLOW), big("PARA ENTONCES, CASI NO PASABAN TRENES", 1.4, 0.86, 62)], tex=CLEAN)
    q1(50.66)
    q2(56.9)

    # ============================== CAP 1: LA CARRERA (62.2 - 186.2)
    bg, ov = chapter(1, "LA CARRERA DE LAS DOS COMPAÑÍAS", F(52466090825), g="doc", year="1862–1869")
    add(62.22, bg, ov, tr="black", td=0.2, tex=DARK)
    add(65.4, L("1s53977", kb("u_9evooDnb_mA.jpg", "in", "archival"), "Monument Point, al norte del Gran Lago Salado · " + CAP_LOC),
        [big("UNA CARRERA QUE EMPEZÓ ANTES DE QUE ELLA NACIERA", 0.1, 0.86, 56)], tex=ARCH)
    add(67.64, kb("u_K_8P5FEUYuQ.jpg", "in", "archival"), [Badge("1862", 0.0, None), big("EN PLENA GUERRA CIVIL", 0.4, 0.86, 76, RED_)], tex=ARCH)
    add(71.0, mp("pm_us", [(0, -98.0, 40.0, 0.63), (4.5, -98.0, 40.0, 0.66)],
                 [dict(type="route", ll=[(-121.49, 38.58), (-112.55, 41.62), (-95.93, 41.26)], t0=0.4, draw=1.6, color=YELLOW, width=6, dash=26),
                  dict(type="label", at=(-80.0, 44.5), text="ESTE", t0=w("este", 74.0) - 71.0, size=56, box=True),
                  dict(type="label", at=(-118.0, 46.0), text="OESTE", t0=w("oeste", 74.6) - 71.0, size=56, box=True)]),
        [big("LEY DEL FERROCARRIL DEL PACÍFICO", 0.2, 0.1, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(75.5, L("03412", cus(_card, lines=[("LA FIRMÓ", 60, GREY_, 0.36, 0.0), ("ABRAHAM LINCOLN", 110, WHITE, 0.52, 0.2)]),
                "Abraham Lincoln · " + CAP_LOC), [big("ABRAHAM LINCOLN LA FIRMÓ", 0.1, 0.08, 58, YELLOW)], tex=ARCH)
    add(77.26, kb("u_ci4fws74o-g.jpg", "in", "archival"), [big("UNA APUESTA ENORME…", 0.1, 0.3, 74, YELLOW),
                                                         big("…EN MITAD DE UNA GUERRA QUE PARTÍA AL PAÍS EN DOS", w("en mitad", 79.6) - 77.26, 0.86, 54)], tex=ARCH)
    add(81.78, mp("pm_us", [(0, -98.0, 40.0, 0.63), (3.1, -98.0, 40.0, 0.65)],
                  [dict(type="pin", at="pm_nyc", t0=0.2, label="NUEVA YORK", side="l", box=True, size=40),
                   dict(type="pin", at="pm_sf", t0=w("california", 83.6) - 81.78, label="CALIFORNIA", side="r", box=True, size=40)]),
        [big("MESES DE VIAJE", w("meses", 84.3) - 81.78, 0.88, 96, RED_, "pop")], tr="zoom", td=0.3, tex=GFX)
    add(84.88, kb("u_9evooDnb_mA.jpg", "in", "archival"), [big("EN BARCO O EN CARRETA", 0.1, 0.86, 76)], tex=ARCH)
    add(87.14, kb(F(12004010574), "in", "doc"), [big("LA IDEA: HACERLO EN UNA SEMANA", 0.1, 0.86, 70, YELLOW)], tex=CLEAN)
    add(89.34, Split([kb(F(23219987175), "in", "doc"), kb(F(23194846536), "in", "doc")], labels=["CENTRAL PACIFIC", "UNION PACIFIC"]),
        [big("DOS COMPAÑÍAS", 0.0, 0.1, 70, YELLOW)], tex=CLEAN)
    add(91.78, mp("pm_us", [(0, -113.0, 40.5, 1.0), (4.8, -110.0, 40.8, 0.95)],
                  [dict(type="pin", at="pm_sacramento", t0=w("sacramento", 93.6) - 91.78, label="SACRAMENTO", side="l", box=True, size=40, color=CPC),
                   dict(type="rail", ll=CP, t0=w("avanzaría", 94.9) - 91.78, draw=1.8, color=CPC, width=7)]),
        [big("CENTRAL PACIFIC: HACIA EL ESTE →", 0.3, 0.1, 62, CPC)], tr="zoom", td=0.3, tex=GFX)
    add(96.64, mp("pm_us", [(0, -100.0, 41.0, 0.95), (4.9, -104.0, 41.0, 0.92)],
                  [dict(type="rail", ll=CP, t0=0.0, draw=0.01, color=CPC, width=7),
                   dict(type="pin", at="pm_omaha", t0=w("omaha", 98.4) - 96.64, label="OMAHA", side="r", box=True, size=40, color=UPC),
                   dict(type="rail", ll=UP, t0=w("avanzaría", 99.9) - 96.64, draw=1.8, color=UPC, width=7)]),
        [big("← UNION PACIFIC: HACIA EL OESTE", 0.3, 0.1, 62, UPC)], tr="zoom", td=0.3, tex=GFX)
    add(101.62, cus(G14.paid, t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(106.02, kb("u_WAWMxOAy6SA.jpg", "in", "doc"), [big("NINGUNA TENÍA PRISA POR ENCONTRARSE CON LA OTRA", 0.1, 0.86, 54)], tex=CLEAN)
    add(109.0, kb("u_jrA2l3JjD5k.jpg", "punch", "warm"), [big("MÁS MILLAS = MÁS DINERO", 0.0, 0.86, 80, YELLOW, "pop")], tex=CLEAN)
    add(110.8, kb("u_HEj3tE9ME_I.jpg", "in", "cold"), [big("EL PEOR TROZO:", 0.0, 0.3, 64),
                                                      BigText("SIERRA NEVADA", "serif", 110, WHITE, (0.5, 0.5), w("la sierra", 113.4) - 110.8, None, "up")], tex=CLEAN)
    add(115.26, kb(F(52389954250), "in", "archival"), [Counter(0, 10000, "{:,.0f}", "TRABAJADORES CHINOS", w("10", 118.6) - 115.26, 1.0, (0.5, 0.78), 110,
                                                               prefix="≈ ", color=YELLOW), big("MILES DE TRABAJADORES CHINOS", 0.2, 0.12, 60)], tex=ARCH)
    add(120.46, kb(F(49992920567), "in", "archival"), [big("TÚNELES EN GRANITO, A MANO", 0.1, 0.86, 70)], tex=ARCH)
    add(w("colgados", 123.2), kb(F(6823951250), "up", "cold"), [big("COLGADOS DE CUERDAS · CON PÓLVORA", 0.0, 0.86, 62)], tex=CLEAN)
    add(w("en pleno", 124.9), kb(F(6970074417), "in", "cold"), [big("EN PLENO INVIERNO", 0.0, 0.86, 80, BLUE_)], tex=CLEAN)
    add(126.0, cus(G14.granite, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(129.1, kb(F(50818220428), "in", "archival"), [big("COBRABAN MENOS QUE LOS BLANCOS", 0.1, 0.86, 64)], tex=ARCH)
    add(w("dormían", 131.4), kb(F(52317603499), "in", "archival"), [big("DORMÍAN EN TIENDAS", 0.0, 0.3, 64),
                                                                  big("EL TRABAJO MÁS PELIGROSO", w("hacían", 132.6) - w("dormían", 131.4), 0.86, 70, RED_)], tex=ARCH)
    add(134.42, kb("u_yE9zGc-WicQ.jpg", "in", "dark"), [big("MUCHOS NO VOLVIERON A CASA", 0.1, 0.86, 76)], tex=DARK)
    add(136.24, L("1s00599", kb(F(25690069454), "in", "archival"), "Truckee Meadows · Alfred A. Hart · " + CAP_LOC),
        [Badge("1868", 0.1, None), big("POR FIN, FUERA DE LAS MONTAÑAS", 0.4, 0.86, 64)], tex=ARCH)
    add(140.0, V("4462", F(54497409990), 0.0, "warm"), [big("LA CARRERA SE VOLVIÓ UNA LOCURA", 0.0, 0.86, 72, RED_)], tex=CLEAN)
    t0 = 142.32
    add(t0, mp("pm_reg", [(0, -112.7, 41.45, 0.84), (4.2, -112.7, 41.5, 0.9)],
               [dict(type="rail", ll=CP[-6:], t0=0.3, draw=2.8, color=CPC, width=7),
                dict(type="rail", ll=UP[-5:], t0=0.3, draw=2.8, color=UPC, width=7),
                dict(type="label", at=(-112.55, 41.15), text="GRAN LAGO SALADO", t0=0.5, size=40, box=True, color=BLUE_)]),
        [big("CADA UNA POR SU LADO", 0.2, 0.1, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(146.54, cus(G14.parallel, t0=0.2, blast_t=w("explosiones", 154.2) - 146.54), tr="fade", td=0.2, tex=GFX)
    add(151.78, kb(F(26746733792), "in", "doc"), [big("SE OÍAN LAS EXPLOSIONES DE LA CUADRILLA RIVAL", 0.2, 0.86, 56)], post=postshake(4), tex=CLEAN)
    add(156.18, cus(G14.parallel, t0=-9, blast_t=-9), tex=GFX)
    add(158.48, kb(F(34594793542), "in", "archival"),
        [Badge("28 DE ABRIL DE 1869", 0.1, None), big("EL CENTRAL PACIFIC QUISO DEJAR CLARO QUIÉN MANDABA", 0.6, 0.86, 54)], tex=ARCH)
    add(164.7, cus(G14.tenmiles, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(168.08, kb("u_QYcg2R8cHa0.jpg", "in", "warm"), [Stamp("RÉCORD", 0.1, RED_, (0.5, 0.45), -8, 140), big("NADIE LO HABÍA HECHO ANTES", 0.4, 0.86, 64)], tex=CLEAN)
    add(170.1, kb(F(24315260230), "in", "warm"), [big("EL CAMPAMENTO SE LLAMÓ…", 0.1, 0.3, 60),
                                                   BigText("VICTORY", "serif", 130, YELLOW, (0.5, 0.52), w("victory", 172.9) - 170.1, None, "up"),
                                                   big("«VICTORIA»", w("victoria", 173.6) - 170.1, 0.7, 60)], tex=CLEAN)
    t0 = 174.54
    add(t0, mp("pm_reg", [(0, -112.7, 41.3, 0.85), (7.0, -112.55, 41.58, 1.5)],
               [dict(type="label", at=(-112.55, 41.12), text="GRAN LAGO SALADO", t0=w("lago", 180.6) - t0, size=44, box=True, color=BLUE_),
                dict(type="pin", at="pm_promontory", t0=0.6, label="PUNTO DE ENCUENTRO", side="r", box=True, size=44),
                dict(type="label", at=(-112.55, 41.70), text="UNA LOMA EN EL DESIERTO", t0=w("una loma", 179.0) - t0, size=40, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(181.58, kb(F(44738313224), "in", "doc"), [BigText("PROMONTORY SUMMIT", "serif", 104, WHITE, (0.5, 0.42), 0.0, None, "up"),
                                                  big("UN SITIO QUE CASI NADIE SABÍA SEÑALAR EN UN MAPA", 0.8, 0.86, 54)], tex=CLEAN)

    # ============================== CAP 2: 10 DE MAYO DE 1869 (186.2 - 314.6)
    bg, ov = chapter(2, "EL DÍA DEL CLAVO DE ORO", F(53267244235), g="doc", year="10 DE MAYO DE 1869")
    add(186.2, bg, ov, tr="black", td=0.2, tex=DARK)
    add(190.12, kb("u_WAWMxOAy6SA.jpg", "in", "warm"), [Badge("WYOMING", 0.1, None), big("OBREROS A LOS QUE NO LES HABÍAN PAGADO", 0.4, 0.86, 60)], tex=CLEAN)
    add(w("del vicepresidente", 194.0) - 0.8, L("1s53973", kb(F(8704887771), "in", "archival"), "Interior de un coche de pasajeros, Omaha · " + CAP_LOC),
        [big("RETUVIERON EL VAGÓN DEL VICEPRESIDENTE", 0.1, 0.12, 60), Stamp("HASTA COBRAR", w("hasta cobrar", 195.4) - w("del vicepresidente", 194.0) + 0.8, RED_,
                                                                             (0.5, 0.6), -8, 110)], tex=ARCH)
    add(196.42, kb("u_FvQ5YgLbiEg.jpg", "in", "cold"), [Badge("10 DE MAYO DE 1869", 0.1, None), big("AMANECIÓ FRÍO EN PROMONTORY", w("amaneció", 199.9) - 196.42, 0.86, 70)],
        tex=CLEAN)
    add(202.24, kb(F(8704887771), "in", "archival"),
        [big("LLEGAN LOS TRENES ESPECIALES", 0.1, 0.86, 64, YELLOW)], tex=ARCH)
    add(206.04, kb(F(23220025425), "in", "doc"), [BigText("JUPITER", "serif", 120, YELLOW, (0.5, 0.14), 0.1, None, "up"), big("LA LOCOMOTORA DEL CENTRAL PACIFIC", 0.5, 0.86, 60),
                                                  Badge("RÉPLICA DE 1979", 0.3, None)], tex=CLEAN)
    add(209.74, kb(F(23194846536), "in", "doc"), [BigText("Nº 119", "serif", 120, WHITE, (0.5, 0.14), 0.1, None, "up"), big("LA DEL UNION PACIFIC", 0.5, 0.86, 64),
                                                  Badge("RÉPLICA DE 1979", 0.3, None)], tex=CLEAN)
    add(213.36, kb(F(8706011188), "in", "archival"), [big("FRENTE A FRENTE", 0.1, 0.12, 80, YELLOW),
                                                       big("SEPARADAS POR UN HUECO DE VÍA SIN TERMINAR", w("separadas", 215.8) - 213.36, 0.86, 56)], tex=ARCH)
    add(218.32, kb(F(3641701190), "in", "archival"), [rich("OBREROS · SOLDADOS · PERIODISTAS · CURIOSOS", ("obreros", "soldados", "periodistas", "curiosos"), 0.4,
                                                           step=0.45, y=0.86, size=58, maxw=0.9)], tex=ARCH)
    add(222.86, L("3b07534", kb(F(3641701190), "punch", "archival"), "Promontory, 10 de mayo de 1869 · " + CAP_LOC),
        [big("UNOS CUANTOS CIENTOS DE PERSONAS", 0.1, 0.86, 62), big("SEGÚN QUIÉN LO CONTARA", 1.4, 0.94, 44, GREY_)], tex=ARCH)
    add(225.92, cus(_card, lines=[("ENTRE ELLOS, UNA NIÑA DE 12 AÑOS", 56, GREY_, 0.34, 0.0),
                                  ("MARY IPSEN", 140, WHITE, 0.52, w("mary", 228.1) - 225.92)]), tr="fade", td=0.2, tex=GFX)
    add(229.82, L("1s00098", kb("u_mrKyfB0Dxns.jpg", "in", "archival"), "Campamento de Reynolds & Dowling, Quaking Asp Hill · " + CAP_LOC),
        [big("AYUDANTE DE COCINA EN LOS CAMPAMENTOS", 0.1, 0.86, 62)], tex=ARCH)
    add(233.04, kb("u_ptjT7wUoiRM.jpg", "in", "archival"),
        [Darken(0.45), rich("«LO MEJOR DE AQUELLOS DÍAS: COMERSE LO QUE SOBRABA»", ("mejor", "sobraba»"), 0.6, step=0.14, y=0.5, size=64, maxw=0.8)], tex=ARCH)
    add(239.3, kb(F(53458590708), "in", "doc"), [big("CLAVOS ESPECIALES PARA EL ACTO", 0.1, 0.86, 66)], tex=CLEAN)
    add(242.58, kb(F(49225875482), "punch", "dark"), [big("EL MÁS FAMOSO…", 0.0, 0.3, 64), big("DE ORO", w("de oro", 243.9) - 242.58, 0.52, 150, GOLD, "pop")], tex=DARK)
    add(w("encargado", 245.0), cus(_card, lines=[("ENCARGADO POR", 54, GREY_, 0.34, 0.0), ("DAVID HEWES", 130, WHITE, 0.5, 0.3),
                                                 ("EMPRESARIO DE SAN FRANCISCO", 56, YELLOW, 0.66, 0.9)]), tr="fade", td=0.2, tex=GFX)
    t0 = 248.28
    add(t0, cus(G14.spike, mode="gold", t0=0.0, t_names=0.6, t_phrase=w("una frase", 250.3) - t0, t_tie=99), tr="fade", td=0.2, tex=GFX)
    add(253.22, cus(G14.spike, mode="gold", t0=-9, t_tie=0.3), tex=GFX)
    add(257.32, kb(F(2167001390), "in", "dark"), [Darken(0.3), big("ACUÉRDATE DE ESTE CLAVO", 0.1, 0.3, 78, GOLD),
                                                  big("MÁS ADELANTE NOS VA A DAR UNA SORPRESA", w("más adelante", 259.4) - 257.32, 0.86, 58)], tex=DARK)
    add(262.0, kb(F(6472846821), "in", "archival"), [big("GOLPES SIMBÓLICOS", 0.1, 0.86, 76), Badge("MURAL DEL CAPITOLIO DE EE. UU.", 0.3, None)],
        tex=ARCH)
    add(264.72, kb("u_XZuqMUiSdgc.jpg", "punch", "doc"), [big("UNO FALLÓ EL MARTILLAZO", 0.0, 0.86, 74, RED_)], post=postshake(5), tex=CLEAN)
    add(266.74, kb("u_k9rwcGU_NcY.jpg", "in", "warm"), [big("DABA IGUAL: EL TELÉGRAFO ESTABA CONECTADO", 0.1, 0.86, 56)], tex=CLEAN)
    add(269.6, cus(G14.morse, t0=0.2), tr="fade", td=0.2, tex=GFX)
    t0 = 273.08
    add(t0, mp("pm_us", [(0, -98.0, 40.0, 0.63), (3.0, -98.0, 40.0, 0.66)],
               [dict(type="route", ll=[(-112.55, 41.62), (-77.04, 38.91)], t0=0.0, draw=0.8, color=YELLOW, width=4, dash=20, smooth=False),
                dict(type="pin", at="pm_dc", t0=0.4, label="WASHINGTON", side="r", box=True, size=36),
                dict(type="route", ll=[(-112.55, 41.62), (-74.0, 40.71)], t0=w("nueva", 274.6) - t0, draw=0.8, color=YELLOW, width=4, dash=20, smooth=False),
                dict(type="pin", at="pm_nyc", t0=w("nueva", 274.6) - t0 + 0.4, label="NUEVA YORK", side="r", box=True, size=36),
                dict(type="route", ll=[(-112.55, 41.62), (-122.42, 37.77)], t0=w("san francisco", 275.4) - t0, draw=0.6, color=YELLOW, width=4, dash=20, smooth=False),
                dict(type="pin", at="pm_sf", t0=w("san francisco", 275.4) - t0 + 0.3, label="SAN FRANCISCO", side="r", box=True, size=36)]),
        tr="zoom", td=0.3, tex=GFX)
    add(276.12, V("100205", "u_pS-mtvufoJ4.jpg", 2.0, "warm"), [big("CAMPANAS…", 0.0, 0.86, 90, YELLOW, "pop")], tex=CLEAN)
    add(w("cañonazos", 277.2), kb("u_ci4fws74o-g.jpg", "punch", "warm"), [big("…Y CAÑONAZOS", 0.0, 0.86, 90, RED_, "pop")], post=postshake(6), tex=CLEAN)
    add(278.04, mp("pm_us", [(0, -98.0, 40.0, 0.63), (5.5, -98.0, 40.0, 0.68)],
                   [dict(type="rail", ll=COAST + UP + CP[::-1] + [(-122.27, 37.80)], t0=0.2, draw=3.0, color=YELLOW, width=7)]),
        [big("DE COSTA A COSTA", 0.2, 0.1, 76, YELLOW), big("POR UN CAMINO DE HIERRO", w("por un camino", 281.8) - 278.04, 0.9, 62)], tr="zoom", td=0.3, tex=GFX)
    add(283.82, kb(F(35750879260), "in", "doc"), [big("LAS DOS LOCOMOTORAS, HASTA TOCARSE", 0.1, 0.86, 64), Badge("RÉPLICAS · HOY", 0.3, None)], tex=CLEAN)
    add(287.34, V("51631", "u_xzKtOI1Cnxo.jpg", 3.0, "warm"), [big("ALGUIEN SACÓ CHAMPÁN", 0.0, 0.86, 76, YELLOW)], tex=CLEAN)
    add(288.82, kb(F(34594793542), "in", "archival"), [big("LAS FOTOS QUE HOY SALEN EN TODOS LOS LIBROS", 0.2, 0.86, 58)], tex=ARCH)
    add(292.5, fr(SHAKE, "«East and West shaking hands at laying last rail» · A. J. Russell, 10 de mayo de 1869"),
        [big("LA MÁS FAMOSA: BRINDANDO ENTRE LAS DOS MÁQUINAS", 0.4, 0.08, 54, YELLOW)], tex=ARCH)
    add(297.24, kb(SHAKE, "punch", "archival"), [big("LO CURIOSO ES LO QUE NO SALE", 0.1, 0.86, 70, YELLOW)], tex=ARCH)
    add(299.44, kb(F(52389954250), "in", "archival"), [big("CASI NINGUNO DE LOS TRABAJADORES CHINOS", 0.1, 0.86, 60)], tex=ARCH)
    add(302.0, kb(F(52317603499), "punch", "archival"), [big("QUE HABÍAN ABIERTO MEDIA VÍA", 0.0, 0.86, 68, YELLOW)], tex=ARCH)
    add(303.98, kb(SHAKE, "out", "archival"), [FnOverlay(G14.outframe, t0=0.2), big("SE QUEDARON FUERA DEL ENCUADRE", 0.6, 0.9, 64, YELLOW)], tex=ARCH)
    add(306.18, mp("pm_us", [(0, -112.55, 41.62, 1.6), (2.9, -100.0, 40.5, 0.64)],
                   [dict(type="pin", at="pm_promontory", t0=0.0, label="PROMONTORY", side="r", box=True, size=44, r=14)]),
        [big("EL CENTRO DEL MUNDO", 0.2, 0.86, 80, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(309.08, kb(F(26234958554), "in", "doc"), [big("LO QUE NADIE PENSÓ…", 0.0, 0.3, 64)], tex=CLEAN)
    add(w("si ese lugar", 310.9), kb("u_xlW6BalTOHw.jpg", "in", "warm"), [big("¿SERVÍA PARA ALGO MÁS QUE PARA UNA FIESTA?", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)

    # ============================== CAP 3: LA VIDA EN LA LÍNEA (314.6 - 443.6)
    bg, ov = chapter(3, "LA VIDA EN LA LÍNEA", F(8706010162), g="archival", year="1870–1900", base=L("56311", kb(F(8706010162), "in", "archival"), None))
    add(314.56, bg, ov, tr="black", td=0.2, tex=DARK)
    add(318.0, kb(F(53267123109), "in", "doc"), [big("EN LO ALTO DE UNA LOMA, EN MITAD DE LA NADA", 0.0, 0.86, 56)], tex=CLEAN)
    add(320.18, kb("u_FLU-CCrhNZg.jpg", "in", "warm"), [rich("NI AGUA · NI PUEBLO · NADA QUE HACER", ("agua", "pueblo", "nada"), 0.2, step=0.35, y=0.84, size=64, maxw=0.9)],
        tex=CLEAN)
    t0 = 324.08
    add(t0, mp("pm_reg", [(0, -112.3, 41.45, 1.05), (4.1, -112.2, 41.4, 1.15)],
               [dict(type="pin", at="pm_promontory", t0=0.0, label="PROMONTORY", side="l", box=True, size=38),
                dict(type="rail", ll=OLD[OLD.index(min(OLD, key=lambda p: abs(p[0] + 112.55) + abs(p[1] - 41.62))):], t0=0.6, draw=2.0, color=YELLOW, width=6),
                dict(type="pin", at="pm_ogden", t0=w("ogden", 327.4) - t0, label="OGDEN", side="r", box=True, size=48)]),
        [big("EL ENLACE SE MUDA A OGDEN", 0.2, 0.1, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(328.22, L("1s00402", kb(F(51668596324), "in", "archival"), "Ogden, Utah · " + CAP_LOC),
        [big("UNA CIUDAD DE VERDAD, JUNTO A LAS MONTAÑAS", 0.1, 0.86, 58)], tex=ARCH)
    add(331.06, kb(F(8704887771), "in", "archival"), [big("PROMONTORY: UNA ESTACIÓN DE APOYO", 0.1, 0.86, 62)], tex=ARCH)
    add(333.64, V("52009", "u_g1WoGCQ5v28.jpg", 2.0, "warm"), [big("UN PUÑADO DE EMPLEADOS", 0.0, 0.3, 60), big("EL CALOR DEL VERANO…", 0.6, 0.86, 70, (255, 160, 60))], tex=CLEAN)
    add(336.38, kb("u_WNyhCTgo2Ys.jpg", "in", "cold"), [big("…Y LAS VENTISCAS DEL INVIERNO", 0.0, 0.86, 68, BLUE_)], tex=CLEAN)
    add(338.04, mp("pm_us", [(0, -98.0, 40.0, 0.63), (3.4, -98.0, 40.0, 0.66)],
                   [dict(type="rail", ll=COAST + UP + CP[::-1] + [(-122.27, 37.80)], t0=0.0, draw=0.6, color=YELLOW, width=6, traffic=8, speed=260)]),
        [big("LA GRAN ARTERIA DEL PAÍS", 0.2, 0.1, 70, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(341.48, kb(F(26228664861), "in", "archival"), [big("TRENES DE PASAJEROS HACIA CALIFORNIA", 0.1, 0.86, 60)], tex=ARCH)
    add(344.5, kb("u_jrA2l3JjD5k.jpg", "in", "warm"), [big("ORO Y PLATA", 0.0, 0.86, 90, GOLD, "pop")], tex=CLEAN)
    add(w("el correo", 346.4), kb("u_mg2ACzid4fY.jpg", "in", "warm"), [big("EL CORREO Y EL GANADO", 0.0, 0.86, 72)], tex=CLEAN)
    t0 = 347.96
    add(t0, mp("pm_reg", [(0, -112.85, 41.45, 0.86), (3.9, -112.85, 41.5, 0.9)],
               [dict(type="rail", ll=OLD, t0=0.0, draw=1.2, color=YELLOW, width=6),
                dict(type="pin", at="pm_lucin", t0=0.8, label="LUCIN", side="l", box=True, size=34),
                dict(type="pin", at="pm_terrace", t0=1.1, label="TERRACE", side="l", box=True, size=34),
                dict(type="pin", at="pm_kelton", t0=1.4, label="KELTON", side="r", box=True, size=34),
                dict(type="pin", at="pm_promontory", t0=1.7, label="PROMONTORY", side="r", box=True, size=34),
                dict(type="pin", at="pm_corinne", t0=2.0, label="CORINNE", side="r", box=True, size=34),
                dict(type="pin", at="pm_ogden", t0=2.3, label="OGDEN", side="r", box=True, size=34)]),
        [big("PUEBLOS QUE SOLO EXISTÍAN POR EL TREN", 0.2, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(351.86, kb(F(26773123011), "in", "doc"), [Badge("EL MÁS GRANDE", 0.0, None), BigText("TERRACE", "serif", 130, YELLOW, (0.5, 0.45), 0.2, None, "up")], tex=CLEAN)
    add(353.68, L("3a28195", kb(F(54497409990), "in", "archival"), "Locomotora de carga del Central Pacific · " + CAP_LOC),
        [big("LOS TALLERES DEL CENTRAL PACIFIC EN UTAH", 0.1, 0.86, 60)], tex=ARCH)
    add(356.66, kb(F(27728076325), "in", "warm"), [Darken(0.3), Counter(0, 16, "{:.0f}", "LOCOMOTORAS EN LA ROTONDA", 0.1, 0.9, (0.5, 0.4), 160, color=YELLOW),
                                                    big("Y DEPÓSITOS DE CARBÓN", w("depósitos", 358.9) - 356.66, 0.86, 58)], tex=CLEAN)
    add(360.38, cus(_card, lines=[("UNA ESCUELA", 70, WHITE, 0.3, 0.0), ("HOTELES", 70, WHITE, 0.42, w("hoteles", 361.3) - 360.38),
                                  ("UN SALÓN", 70, WHITE, 0.54, w("un salón", 362.0) - 360.38), ("¡Y HASTA UNA BIBLIOTECA!", 84, YELLOW, 0.68, w("biblioteca", 363.4) - 360.38)]),
        tr="fade", td=0.2, tex=GFX)
    add(364.58, kb(F(23964257354), "in", "warm"), [Counter(0, 1000, "{:,.0f}", "VECINOS", 0.1, 1.0, (0.5, 0.36), 140, prefix="≈ "),
                                                   big("CASI LA MITAD, CHINOS", w("casi la mitad", 366.6) - 364.58, 0.86, 72, YELLOW)], tex=CLEAN)
    add(368.68, L("1s00510", kb(F(52317603499), "in", "archival"), "Obreros cerca de la boca del túnel de la cumbre · Alfred A. Hart · " + CAP_LOC),
        [big("LOS MISMOS HOMBRES QUE HABÍAN CONSTRUIDO LA VÍA", 0.1, 0.86, 56)], tex=ARCH)
    add(371.86, kb(F(26234963934), "in", "doc"), [big("PEONES DE MANTENIMIENTO", 0.0, 0.86, 72)], tex=CLEAN)
    add(374.08, kb(F(26746728502), "in", "doc"), [rich("COCINEROS · TIENDAS · LAVANDERÍAS", ("cocineros", "tiendas", "lavanderías"), 0.2, step=0.5, y=0.86, size=64,
                                                       maxw=0.9)], tex=CLEAN)
    t0 = 377.54
    add(t0, mp("pm_reg", [(0, -113.55, 41.55, 1.5), (4.2, -113.58, 41.57, 1.6)],
               [dict(type="pin", at="pm_terrace", t0=0.0, label="TERRACE", side="r", box=True, size=40),
                dict(type="route", ll=[(-113.533, 41.502), (-113.58, 41.56), (-113.64, 41.61), (-113.70, 41.65)], t0=w("canal", 379.6) - t0, draw=1.4, color=BLUE_,
                     width=5, dash=18),
                dict(type="label", at=(-113.55, 41.68), text="CANAL DE MADERA · 12 MILLAS", t0=w("canal", 379.6) - t0 + 0.6, size=40, box=True, color=BLUE_)]),
        [big("NO HABÍA AGUA", 0.1, 0.1, 70, YELLOW), Badge("ESQUEMA", 0.5, None)], tr="zoom", td=0.3, tex=GFX)
    add(381.8, kb(F(47094173541), "in", "doc"), [BigText("KELTON", "serif", 130, YELLOW, (0.5, 0.16), 0.1, None, "up")], tex=CLEAN)
    add(384.2, kb("u_AIrhQLML8mY.jpg", "in", "warm"), [big("CADA DÍA SALÍAN DILIGENCIAS", 0.1, 0.86, 66)], tex=CLEAN)
    t0 = 387.24
    add(t0, mp("pm_west", [(0, -115.5, 43.6, 1.12), (4.0, -115.8, 43.9, 1.15)],
               [dict(type="pin", at="pm_kelton", t0=0.0, label="KELTON", side="r", box=True, size=38),
                dict(type="route", ll=STAGE, t0=0.3, draw=3.2, color=(230, 180, 90), width=6, dash=22),
                dict(type="pin", at="pm_boise", t0=1.4, label="BOISE (IDAHO)", side="r", box=True, size=38),
                dict(type="label", at=(-119.5, 44.2), text="OREGÓN", t0=w("oregon", 388.0) - t0 + 0.6, size=44, box=True)]),
        [big("HACIA EL NOROESTE", 0.2, 0.1, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(391.2, kb("u_EBJ6kdKHqrs.jpg", "in", "warm"), [big("BAJABAS DEL TREN EN KELTON…", 0.0, 0.3, 62), big("…Y SEGUÍAS DÍAS ENTEROS EN CARRUAJE", 1.6, 0.86, 62, YELLOW)],
        tex=CLEAN)
    t0 = 395.48
    add(t0, mp("pm_west", [(0, -115.8, 43.9, 1.15), (4.8, -115.8, 43.9, 1.18)],
               [dict(type="route", ll=STAGE, t0=0.0, draw=0.01, color=(230, 180, 90), width=6, dash=22),
                dict(type="pin", at="pm_kelton", t0=0.0, label="KELTON", side="r", box=True, size=38),
                dict(type="pin", at="pm_boise", t0=0.2, label="BOISE · 2 DÍAS", side="r", box=True, size=42),
                dict(type="pin", at="pm_walla", t0=w("cuatro", 396.9) - t0, label="WALLA WALLA · 4 DÍAS", side="r", box=True, size=42)]),
        tr="zoom", td=0.3, tex=GFX)
    add(400.28, kb(F(26746744512), "in", "doc"), [big("UN PUEBLO DIMINUTO…", 0.0, 0.3, 62), big("…LA PUERTA DE MEDIO NOROESTE", 1.6, 0.86, 66, YELLOW)], tex=CLEAN)
    add(405.4, kb("u_fBUm6bhh6Ng.jpg", "in", "doc"), [Stamp("UN PROBLEMA", 0.1, RED_, (0.5, 0.48), -8, 120)], tex=CLEAN)
    t0 = 407.34
    add(t0, mp("pm_reg", [(0, -112.75, 41.25, 0.86), (6.3, -112.75, 41.35, 0.9)],
               [dict(type="label", at=(-112.55, 41.12), text="GRAN LAGO SALADO", t0=0.2, size=50, box=True, color=BLUE_),
                dict(type="rail", ll=OLD, t0=w("un rodeo", 411.8) - t0, draw=2.2, color=YELLOW, width=7),
                dict(type="pin", at="pm_lucin", t0=w("un rodeo", 411.8) - t0, label="LUCIN", side="l", box=True, size=36),
                dict(type="pin", at="pm_ogden", t0=w("un rodeo", 411.8) - t0 + 1.8, label="OGDEN", side="r", box=True, size=36)]),
        [big("UN RODEO ENORME POR EL NORTE", w("un rodeo", 411.8) - t0, 0.92, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(413.68, cus(G14.profile, mode="old", t0=0.2, step=1.6), tr="fade", td=0.2, tex=GFX)
    add(420.24, L("1s53975", kb(F(54497515525), "in", "archival"), "Tren de construcción en Ten Mile Canyon · " + CAP_LOC),
        [big("CADA TREN QUE SUBÍA PERDÍA TIEMPO", 0.1, 0.86, 62)], tex=ARCH)
    add(423.5, kb(F(27728076325), "punch", "warm"), [big("GASTABA CARBÓN Y DESGASTABA FRENOS", 0.0, 0.86, 62)], tex=CLEAN)
    add(426.06, kb(F(460228024), "in", "cold"), [big("EN INVIERNO, NIEVE Y HIELO EN LOS RIELES", 0.1, 0.86, 60, BLUE_), big("TODO, MÁS LENTO", w("todo era", 429.1) - 426.06, 0.94, 50)],
        tex=ARCH)
    add(431.44, kb(F(54497515525), "in", "archival"), [big("CON POCO TRÁFICO, EL RODEO SE AGUANTABA", 0.1, 0.86, 58)], tex=ARCH)
    add(434.88, kb("u_SAo07YHgJUw.jpg", "in", "doc"), [Badge("FINALES DEL SIGLO XIX", 0.1, None), big("TRENES CADA VEZ MÁS LARGOS Y PESADOS", 0.5, 0.86, 62)], tex=CLEAN)
    add(440.22, kb("u_wt6jb1rbh_8.jpg", "in", "doc"), [big("Y ALGUIEN EMPEZÓ A MIRAR EL LAGO CON OTROS OJOS", 0.2, 0.86, 56, YELLOW)], tex=CLEAN)

    # ============================== CAP 4: EL ATAJO DEL LAGO (443.6 - 585.5)
    bg, ov = chapter(4, "EL ATAJO DEL LAGO", "u_kN89XrQog0k.jpg", g="doc", year="1902–1910")
    add(443.58, bg, ov, tr="black", td=0.2, tex=DARK)
    add(445.84, cus(_card, lines=[("SOUTHERN PACIFIC", 120, YELLOW, 0.42, 0.0), ("YA CONTROLABA AL VIEJO CENTRAL PACIFIC", 56, WHITE, 0.6, 0.6)]), tr="fade", td=0.2,
        tex=GFX)
    add(448.54, kb("u_-J2pOmhv0M0.jpg", "in", "doc"), [big("UNA IDEA QUE PARECÍA UNA LOCURA", 0.1, 0.86, 64)], tex=CLEAN)
    t0 = 451.06
    add(t0, mp("pm_reg", [(0, -112.75, 41.25, 0.86), (3.2, -112.75, 41.25, 0.9)],
               [dict(type="rail", ll=OLD, t0=0.0, draw=0.01, color=(150, 140, 100), width=5),
                dict(type="rail", ll=CUT, t0=w("cruzarlo", 453.4) - t0 - 0.4, draw=1.4, color=CYAN, width=8)]),
        [big("SI EL LAGO ESTABA EN MEDIO… ¡A CRUZARLO!", 0.1, 0.1, 60, CYAN)], tr="zoom", td=0.3, tex=GFX)
    add(454.3, L("582561c", kb(F(5392295172), "in", "archival"), "Lucin Cutoff · " + CAP_LOC),
        [Badge("1902", 0.1, None), BigText("LUCIN CUTOFF", "serif", 110, WHITE, (0.5, 0.14), 0.4, None, "up"), big("EL ATAJO DE LUCIN", w("el atajo", 458.0) - 454.3, 0.88, 66, YELLOW)],
        tex=ARCH)
    add(459.66, L("3a30161", kb("u_-o0HZfyurbc.jpg", "in", "archival"), "Pala de vapor en obras de ferrocarril, c. 1906 · " + CAP_LOC),
        [Counter(0, 3000, "{:,.0f}", "OBREROS", 0.1, 1.0, (0.5, 0.36), 140, prefix="≈ "), big("SIETE DÍAS A LA SEMANA", w("siete", 461.6) - 459.66, 0.86, 72, YELLOW)], tex=ARCH)
    add(463.18, L("3b17993", kb("u_pvdN9qvtBLs.jpg", "in", "archival"), "Trabajando sobre la sal del Gran Lago Salado, 1908 · " + CAP_LOC),
        [big("CAMPAMENTOS SOBRE EL PROPIO LAGO", 0.1, 0.12, 62), big("EN BARCAZAS Y EN VAGONES", w("en barcas", 466.0) - 463.18, 0.86, 62)], tex=ARCH)
    add(467.82, L("4a09206", kb("u_IXZyQNcU2Jc.jpg", "in", "archival"), "Gran Lago Salado, c. 1900 · Detroit Publishing · " + CAP_LOC),
        [big("AGUA TAN SALADA QUE NO SERVÍA NI PARA LAVARSE", 0.2, 0.08, 54, YELLOW)], tex=ARCH)
    add(471.26, cus(G14.trestle, mode="build", t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(477.68, L("582561c", kb(F(5392295172), "in", "doc"), "Caballete del atajo Ogden-Lucin sobre el Gran Lago Salado · HAER · " + CAP_LOC),
        [big("≈ 19 KM SOBRE EL AGUA SALADA", 0.1, 0.9, 62, YELLOW)], tex=ARCH)
    add(480.92, cus(G14.trestle, mode="sink", t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(487.38, kb("u_IXZyQNcU2Jc.jpg", "in", "doc"), [big("CUENTAN QUE SE TRAGÓ VAGONES ENTEROS DE PIEDRA", 0.2, 0.86, 54)], tex=CLEAN)
    add(491.1, kb("u_d2kMu9-WYRg.jpg", "in", "doc"), [big("…Y EN LA SUPERFICIE, NADA", 0.1, 0.86, 70)], tex=CLEAN)
    t0 = 493.8
    add(t0, mp("pm_reg", [(0, -112.75, 41.25, 0.86), (4.1, -112.75, 41.25, 0.9)],
               [dict(type="rail", ll=OLD, t0=0.0, draw=0.01, color=(150, 140, 100), width=5),
                dict(type="rail", ll=CUT, t0=0.0, draw=0.01, color=CYAN, width=8, traffic=1, speed=300)]),
        [Badge("MARZO DE 1904", 0.1, None), big("EL PRIMER TREN DE CARGA CRUZA EL LAGO", 0.5, 0.9, 60, CYAN)], tr="zoom", td=0.3, tex=GFX)
    add(497.9, cus(G14.profile, mode="both", t0=-1.4, step=1.2), tr="fade", td=0.2, tex=GFX)
    add(505.1, kb("u_kN89XrQog0k.jpg", "in", "doc"), [big("PARA EL FERROCARRIL: UN SUEÑO", 0.0, 0.86, 68, GREEN_)], tex=CLEAN)
    add(506.82, kb(F(26234958554), "in", "cold"), [big("PARA LA VÍA VIEJA…", 0.0, 0.3, 64), Stamp("SENTENCIA", w("sentencia", 508.6) - 506.82, RED_, (0.5, 0.6), -8, 140)],
        tex=CLEAN)
    q1(509.94, bg="u_93rTRYRAvi4.jpg", badge="RESPUESTA A LA PREGUNTA 1")
    add(517.68, cus(_card, lines=[("NI UN DESASTRE", 90, WHITE, 0.36, 0.0), ("NI UNA QUIEBRA", 90, WHITE, 0.52, w("ni ninguna", 519.4) - 517.68)]), tr="fade", td=0.2,
        tex=GFX)
    add(520.52, L("582561c", kb(F(5392295172), "punch", "archival"), "Lucin Cutoff · " + CAP_LOC),
        [big("LA DEJÓ VACÍA UN PUENTE", 0.0, 0.5, 100, YELLOW, "pop")], tex=ARCH)
    add(522.14, V("4462", F(54497515525), 0.0, "warm"), [big("LOS TRENES GRANDES DEJARON DE SUBIR A PROMONTORY", 0.1, 0.86, 54)], tex=CLEAN)
    t0 = 526.5
    add(t0, mp("pm_reg", [(0, -112.75, 41.3, 0.86), (4.7, -112.75, 41.3, 0.9)],
               [dict(type="rail", ll=CUT, t0=0.0, draw=0.01, color=CYAN, width=8, traffic=3, speed=260),
                dict(type="route", ll=OLD, t0=0.0, draw=0.01, color=YELLOW, width=7, t1=1.2),
                dict(type="route", ll=OLD, t0=1.2, draw=0.01, color=(150, 140, 100), width=4, dash=16),
                dict(type="label", at=(-112.95, 41.86), text="RAMAL SECUNDARIO", t0=w("ramal", 529.6) - t0, size=48, box=True)]),
        [big("DE LÍNEA PRINCIPAL…", 0.2, 0.1, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(531.24, cus(_card, lines=[("AHÍ TIENES", 70, GREY_, 0.4, 0.0), ("EL CONTRASTE", 120, YELLOW, 0.56, 0.3)]), tr="fade", td=0.2, tex=GFX)
    add(532.88, cus(G14.traffic, t0=0.1, row2=99), tr="fade", td=0.2, tex=GFX)
    add(w("cruzaban", 535.5), V("4461", "u_cw8zyuWz8CU.jpg", 3.0, "doc"), [big("UNA DOCENA DE TRENES AL DÍA, EN CADA SENTIDO", 0.1, 0.86, 58, CYAN)], tex=CLEAN)
    add(539.14, cus(G14.traffic, t0=-9, row2=0.2), tr="fade", td=0.2, tex=GFX)
    add(543.36, kb(F(26235877813), "in", "doc"), [big("ALGO DE CARGA Y LOS POCOS VECINOS QUE QUEDABAN", 0.2, 0.86, 54)], tex=CLEAN)
    add(546.8, V("17792", F(12004010574), 0.0, "doc"), [Darken(0.5), FnOverlay(G2.subscribe), big("SI TE ESTÁ GUSTANDO, SUSCRÍBETE", 0.2, 0.14, 62, YELLOW),
                                                       big("ESTE CANAL NO SE QUEDA SIN TRENES", w("a diferencia", 549.9) - 546.8, 0.24, 52)], tex=DARK)
    add(553.64, kb(F(53266774791), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("CADA SEMANA SALE UNO NUEVO", 0.1, 0.14, 62, YELLOW)], tex=DARK)
    add(558.8, L("8b25790", kb(F(3702058107), "in", "archival"), "Corinne, Utah, 1940 · FSA/OWI · " + CAP_LOC),
        [big("LOS PUEBLOS LO NOTARON ENSEGUIDA", 0.1, 0.86, 62)], tex=ARCH)
    t0 = 560.62
    add(t0, mp("pm_reg", [(0, -113.3, 41.55, 1.2), (3.3, -113.3, 41.55, 1.25)],
               [dict(type="pin", at="pm_terrace", t0=0.0, label="TERRACE", side="r", box=True, size=44),
                dict(type="label", at=(-113.53, 41.40), text="TALLERES → NEVADA", t0=w("que se fueron", 562.2) - t0, size=44, box=True, color=RED_)]),
        tr="zoom", td=0.3, tex=GFX)
    add(563.9, kb(F(26773123011), "punch", "cold"), [Badge("1910", 0.1, None), Stamp("ABANDONADO", w("abandonado", 565.4) - 563.9, RED_, (0.5, 0.5), -8, 120)], tex=CLEAN)
    add(566.66, V("2785", "u_9tzn340P0xw.jpg", 1.0, "cold"), [big("APEADEROS QUE DESAPARECIERON DE LOS HORARIOS", 0.1, 0.86, 54)], tex=CLEAN)
    add(569.14, kb("u_9tzn340P0xw.jpg", "in", "cold"), [big("KELTON AGUANTÓ A DURAS PENAS", 0.1, 0.86, 66)], tex=CLEAN)
    add(572.88, kb(F(53267244235), "in", "doc"), [big("EL LUGAR DONDE SE UNIÓ EL PAÍS SEGUÍA AHÍ", 0.1, 0.86, 56)], tex=CLEAN)
    add(575.86, kb(F(54573177158), "out", "cold"), [big("PERO CASI NADIE PASABA PARA VERLO", 0.1, 0.86, 62)], tex=CLEAN)
    add(578.16, kb("u_saS98jKhVjA.jpg", "in", "dark"), [Darken(0.3), big("Y TODAVÍA FALTABA LO MÁS RARO", 0.1, 0.5, 80, YELLOW)], tex=DARK)
    add(580.16, cus(_card, lines=[("CASI 40 AÑOS DESPUÉS…", 70, GREY_, 0.36, 0.0), ("UNA FIESTA", 130, YELLOW, 0.52, w("alguien", 582.1) - 580.16),
                                  ("PARA ARRANCARLA", 90, WHITE, 0.68, w("para arrancarla", 584.2) - 580.16)]), tr="fade", td=0.2, tex=GFX)

    # ============================== CAP 5: LA GUERRA Y EL ABANDONO (585.5 - 696.4)
    bg, ov = chapter(5, "LA GUERRA Y EL ABANDONO", "u_krsmsfjjGgg.jpg", g="cold", year="1930–1942")
    add(585.46, bg, ov, tr="black", td=0.2, tex=DARK)
    add(588.6, kb(F(7012363883), "in", "doc"), [big("UNA VÍA QUE NADIE SABÍA PARA QUÉ MANTENER", 0.1, 0.86, 58)], tex=CLEAN)
    add(592.32, kb("u_kdEiqHKt_0o.jpg", "in", "warm"), [big("ALGÚN TREN DE GANADO EN TEMPORADA", 0.1, 0.86, 62), big("…Y POCO MÁS", w("y poco", 595.2) - 592.32, 0.3, 80, YELLOW)],
        tex=CLEAN)
    add(596.42, kb("u_E_dOFTggZtg.jpg", "in", "warm"), [big("RANCHEROS Y APEADEROS PERDIDOS", 0.1, 0.86, 64)], tex=CLEAN)
    add(600.26, kb(F(51403622085), "in", "warm"), [big("EL MAQUINISTA LOS CONOCÍA POR SU NOMBRE", 0.1, 0.86, 58)], tex=CLEAN)
    add(603.38, V("100634", "u_sBXVsMsfoEc.jpg", 0.0, "cold"), [Badge("AÑOS 30 · GRAN DEPRESIÓN", 0.1, None)], tex=CLEAN)
    add(606.46, kb(F(4048831870), "in", "cold"), [big("EL SOUTHERN PACIFIC PIDE CERRARLO", 0.1, 0.86, 62)], tex=CLEAN)
    add(609.1, kb(F(26234963934), "in", "cold"), [Badge("1933", 0.1, None), big("SE LEVANTA UN PRIMER TRAMO DE RIELES", 0.4, 0.86, 60)], tex=CLEAN)
    add(613.0, kb("u_4Tr4OrpQwNw.jpg", "in", "cold"), [Darken(0.3), Badge("1937", 0.1, None), big("KELTON, EL PUEBLO DE LAS DILIGENCIAS", 0.4, 0.12, 56),
                                                  Counter(0, 47, "{:.0f}", "VECINOS", w("quedaban", 617.3) - 613.0, 0.8, (0.5, 0.6), 160, color=YELLOW)], tex=CLEAN)
    add(619.62, kb("u_QYcg2R8cHa0.jpg", "in", "warm"), [big("LAS VÍAS SEGUÍAN BRILLANDO AL SOL…", 0.1, 0.86, 62)], tex=CLEAN)
    add(623.08, kb("u_93rTRYRAvi4.jpg", "in", "warm"), [big("…PERO CADA AÑO, MENOS RAZONES PARA PASAR", 0.0, 0.86, 58)], tex=CLEAN)
    add(626.0, V("51793", "u_sBXVsMsfoEc.jpg", 1.0, "warm"), [big("MÁS POLVO QUE CARGA", 0.2, 0.86, 76)], tex=CLEAN)
    add(629.18, cus(_card, lines=[("HASTA QUE LLEGÓ EL", 60, GREY_, 0.36, 0.0), ("7 DE DICIEMBRE DE 1941", 110, RED_, 0.52, 0.5)]), tr="glitch", td=0.3, tex=GFX)
    add(632.96, L("3c04778", kb("u_HlQGJyNwAnI.jpg", "in", "doc"), "Pearl Harbor, 7 de diciembre de 1941 · " + CAP_LOC),
        [BigText("PEARL HARBOR", "serif", 120, WHITE, (0.5, 0.12), 0.0, None, "up")], tex=ARCH)
    add(634.92, kb("u_gyv33zW7Op4.jpg", "in", "doc"), [big("ESTADOS UNIDOS ENTRA EN LA SEGUNDA GUERRA MUNDIAL", 0.1, 0.86, 54)], tex=CLEAN)
    add(637.92, V("2237", "u_ib7jwp7m0iA.jpg", 1.0, "warm"), [big("DE LA NOCHE A LA MAÑANA: ACERO", 0.0, 0.14, 66, YELLOW),
                                                       rich("BARCOS · TANQUES · CAÑONES", ("barcos", "tanques", "cañones"), w("barcos", 640.6) - 637.92, step=0.6, y=0.86, size=66)],
        tex=CLEAN)
    add(642.74, kb("u_P8jEvckndSE.jpg", "in", "warm"), [big("Y SOBRE TODO, PARA MOVER TODO ESO", 0.1, 0.86, 62)], tex=CLEAN)
    add(645.66, V("1947", "u_bhpyQFlKysQ.jpg", 4.0, "warm"),
        [big("LAS FÁBRICAS NO DABAN ABASTO", 0.1, 0.86, 66)], tex=ARCH)
    add(648.38, L("3f05676", kb("u_5_uEbMeeJrc.jpg", "in", "archival"), "«Save scrap for victory!», cartel de 1941 · " + CAP_LOC),
        [big("CAMPAÑAS PARA RECOGER CHATARRA", 0.1, 0.92, 58, YELLOW)], tex=ARCH)
    add(651.68, cus(G14.scrap, t0=0.1), tr="fade", td=0.2, tex=GFX)
    add(655.14, L("8c27782", kb("u_qz1DQ7sKxZE.jpg", "in", "archival"), "Niños recogiendo chatarra, Connecticut, 1942 · FSA/OWI · " + CAP_LOC),
        [big("LOS NIÑOS BUSCABAN METAL CON CARRETILLAS", 0.1, 0.86, 58)], tex=ARCH)
    add(658.52, L("8c34159", kb("u_HGCqL-tRcac.jpg", "in", "archival"), "Recogida de chatarra en Fort Kent (Maine), 1942 · FSA/OWI · " + CAP_LOC),
        [big("REJAS DE PARQUES · CAÑONES DE MONUMENTOS", 0.1, 0.86, 58)], tex=ARCH)
    add(661.78, L("8b04469", kb("u_T8vNEq4IRqM.jpg", "punch", "archival"), "Desguace de chatarra para la guerra, 1942 · FSA/OWI · " + CAP_LOC),
        [big("¡HASTA RIELES DE TRANVÍAS!", 0.1, 0.86, 70, YELLOW)], tex=ARCH)
    t0 = 664.86
    add(t0, mp("pm_reg", [(0, -112.85, 41.45, 0.86), (5.7, -112.85, 41.5, 0.92)],
               [dict(type="route", ll=OLD, t0=0.2, draw=1.8, color=(200, 200, 210), width=8)]),
        [big("EN MITAD DEL DESIERTO DE UTAH…", 0.1, 0.1, 62),
         Counter(0, 100, "{:.0f}", "MILLAS DE ACERO QUE CASI NADIE USABA", w("había más", 666.9) - t0, 1.2, (0.5, 0.82), 120, prefix="+", color=YELLOW)],
        tr="zoom", td=0.3, tex=GFX)
    add(670.64, cus(_card, lines=[("MARZO DE 1942", 110, YELLOW, 0.42, 0.0), ("3 MESES DESPUÉS DE PEARL HARBOR", 60, WHITE, 0.58, 0.6)]), tr="fade", td=0.2, tex=GFX)
    add(674.64, kb(F(52466090825), "in", "cold"), [big("EL SOUTHERN PACIFIC PIDE ABANDONAR LO QUE QUEDA", 0.1, 0.86, 56)], tex=CLEAN)
    add(679.5, kb("u_xlW6BalTOHw.jpg", "in", "warm"), [Stamp("NADIE SE OPUSO", 0.1, RED_, (0.5, 0.5), -6, 120)], tex=CLEAN)
    add(681.18, cus(_card, lines=[("NI LOS RANCHEROS", 72, WHITE, 0.34, 0.0), ("NI EL ESTADO", 72, WHITE, 0.48, w("ni el estado", 682.6) - 681.18),
                                  ("NI LOS POCOS VECINOS DE KELTON", 72, WHITE, 0.62, w("ni los pocos", 683.4) - 681.18)]), tr="fade", td=0.2, tex=GFX)
    add(685.38, V("42117", "u_ib7jwp7m0iA.jpg", 0.5, "warm"),
        [big("EL METAL QUE UNIÓ EL PAÍS…", 0.1, 0.1, 60, YELLOW), big("…IBA A SERVIR PARA DEFENDERLO", w("iba a servir", 687.4) - 685.38, 0.92, 60)], tex=ARCH)
    add(689.3, kb(F(53267244235), "in", "doc"), [Badge("SEPTIEMBRE DE 1942", 0.1, None), big("PERO LO QUE PASÓ EN PROMONTORY…", 0.4, 0.86, 62)], tex=CLEAN)
    add(692.46, kb("u_IG1VKwKUY7E.jpg", "in", "dark"), [big("…NO SE PARECE A NINGÚN OTRO CIERRE", 0.1, 0.86, 64, YELLOW)], tex=DARK)

    # ============================== CAP 6: LA CEREMONIA DE 1942 (696.4 - 838.9)
    bg, ov = chapter(6, "LA FIESTA PARA ARRANCAR LA VÍA", "u_IG1VKwKUY7E.jpg", g="warm", year="8 DE SEPTIEMBRE DE 1942")
    add(696.44, bg, ov, tr="black", td=0.2, tex=DARK)
    add(698.32, L("8b04469", kb("u_T8vNEq4IRqM.jpg", "in", "archival"), "Grúa magnética cargando chatarra, 1942 · FSA/OWI · " + CAP_LOC),
        [big("PODRÍAN HABERLO HECHO EN SILENCIO", 0.1, 0.12, 56), big("GRÚAS · RIELES · VAGONES", w("arrancar", 699.6) - 698.32, 0.86, 62)], tex=ARCH)
    add(701.92, kb("u_tD9-ycJprFs.jpg", "in", "doc"), [big("PERO EN UTAH DECIDIERON OTRA COSA", 0.1, 0.86, 62)], tex=CLEAN)
    add(705.2, kb(F(6472846821), "in", "archival"), [big("LO MISMO QUE SU PRINCIPIO:", 0.0, 0.3, 60), big("UNA CEREMONIA", w("una ceremonia", 707.5) - 705.2, 0.86, 96, YELLOW, "pop")],
        tex=ARCH)
    add(708.88, cus(_card, lines=[("LA MAÑANA DEL", 60, GREY_, 0.36, 0.0), ("8 DE SEPTIEMBRE DE 1942", 110, YELLOW, 0.52, 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(712.16, kb("u_s4vuMuapk4Y.jpg", "in", "doc"), [LowerThird("HERBERT MAW", "GOBERNADOR DE UTAH", 0.2, None), big("SALE DE SALT LAKE CITY", 0.6, 0.14, 62)],
        tex=CLEAN)
    t0 = 714.9
    add(t0, mp("pm_reg", [(0, -112.2, 41.2, 1.0), (3.3, -112.3, 41.35, 1.0)],
               [dict(type="pin", at="pm_slc", t0=0.0, label="SALT LAKE CITY", side="r", box=True, size=38),
                dict(type="route", ll=[(-111.891, 40.761), (-111.95, 41.0), (-111.974, 41.223), (-112.0155, 41.5102), (-112.20, 41.60), (-112.40, 41.64), (-112.548, 41.6185)],
                     t0=0.2, draw=2.8, color=WHITE, width=5, dash=18),
                dict(type="pin", at="pm_ogden", t0=1.2, label="OGDEN", side="r", box=True, size=38),
                dict(type="pin", at="pm_promontory", t0=2.6, label="PROMONTORY", side="r", box=True, size=38)]),
        [big("CARAVANA DE AUTOS CON ESCOLTA DE POLICÍA", 0.1, 0.1, 58)], tr="zoom", td=0.3, tex=GFX)
    add(718.16, kb(F(341604649), "in", "archival"), [Badge("OGDEN", 0.1, None), big("LA RADIO LOCAL TRANSMITE UN PROGRAMA ESPECIAL", 0.4, 0.86, 54)], tex=ARCH)
    add(721.9, kb(F(6332927417), "in", "doc"), [big("POR EL CAMINO:", 0.0, 0.3, 56, GREY_), big("OFICIALES DE LA MARINA", 0.3, 0.44, 70),
                                                big("Y DIRECTIVOS DEL FERROCARRIL", w("y a directivos", 724.0) - 721.9, 0.58, 64, YELLOW)], tex=CLEAN)
    t0 = 726.28
    add(t0, mp("pm_reg", [(0, -112.6, 41.6, 1.6), (4.2, -112.62, 41.6, 1.7)],
               [dict(type="pin", at="pm_rozel", t0=0.2, label="ROZEL", side="l", box=True, size=44),
                dict(type="label", at=(-112.6467, 41.53), text="EN 1869: «VICTORY»", t0=w("victory", 729.6) - t0, size=46, box=True, color=YELLOW),
                dict(type="pin", at="pm_promontory", t0=0.6, label="PROMONTORY", side="r", box=True, size=36)]),
        tr="zoom", td=0.3, tex=GFX)
    add(730.48, cus(_card, lines=[("POLLO PARA", 70, GREY_, 0.36, 0.0), ("88 INVITADOS", 130, YELLOW, 0.52, 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(733.8, kb(F(7012363883), "in", "warm"), [big("A LAS DOS DE LA TARDE EMPIEZA EL ACTO", 0.1, 0.86, 62)], tex=CLEAN)
    add(735.9, kb(F(53265883327), "in", "doc"), [rich("DISCURSOS · UN MAESTRO DE CEREMONIAS · FOTÓGRAFOS", ("discursos", "fotógrafos"), 0.2, step=0.45, y=0.86, size=56, maxw=0.9)],
        tex=CLEAN)
    add(739.8, kb(F(35750879070), "in", "doc"), [big("UNA ORACIÓN DE APERTURA", 0.1, 0.86, 66)], tex=CLEAN)
    add(744.44, cus(_card, lines=[("TODO DURÓ APENAS", 60, GREY_, 0.36, 0.0), ("MEDIA HORA", 140, YELLOW, 0.52, 0.3)]), tr="fade", td=0.2, tex=GFX)
    add(746.48, fr(SHAKE, "10 de mayo de 1869 · A. J. Russell"), [big("DOS LOCOMOTORAS FRENTE A FRENTE, COMO EN 1869", 0.3, 0.08, 54, YELLOW)], tex=ARCH)
    add(751.26, kb(F(3641701190), "in", "dark"), [Darken(0.45), big("BUSCARON A LOS ÚLTIMOS TESTIGOS VIVOS", 0.1, 0.5, 70, YELLOW)], tex=DARK)
    add(753.9, cus(G14.lifeline, t0=0.0, t73=99, t42=w("ahora con", 756.7) - 753.9), tr="fade", td=0.2, tex=GFX)
    t0 = w("desde bear", 758.4)
    add(t0, mp("pm_reg", [(0, -112.4, 41.62, 1.6), (4.0, -112.4, 41.62, 1.65)],
               [dict(type="pin", at="pm_bear_river_city", t0=0.0, label="BEAR RIVER CITY", side="r", box=True, size=40),
                dict(type="pin", at="pm_promontory", t0=0.8, label="PROMONTORY", side="l", box=True, size=40)]),
        [big("A POCAS MILLAS DE ALLÍ", w("a pocas", 761.0) - t0, 0.9, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(762.56, cus(_card, lines=[("Y TAMBIÉN", 60, GREY_, 0.34, 0.0), ("ISRAEL HUNSAKER", 120, WHITE, 0.5, 0.2), ("90 AÑOS", 80, YELLOW, 0.66, w("de 90", 764.2) - 762.56)]),
        tr="fade", td=0.2, tex=GFX)
    add(764.88, kb(F(34594793542), "in", "archival"),
        [big("HABÍA TENDIDO RIELES EN ESA MISMA LOMA", 0.1, 0.86, 62)], tex=ARCH)
    add(768.26, kb(SHAKE, "punch", "archival"), [big("DICEN QUE HASTA SALÍA EN LA FOTO DEL CHAMPÁN", 0.1, 0.9, 56, YELLOW)], tex=ARCH)
    add(771.24, kb(F(34594793542), "out", "dark"), [Darken(0.45), big("UNA MUJER CUYO TÍO ABUELO ESTUVO EN 1869…", 0.1, 0.5, 62)], tex=DARK)
    add(775.14, kb(F(1701193034), "in", "archival"), [big("…LE ENTREGÓ AL GOBERNADOR UNA BARRA DE HIERRO", 0.0, 0.86, 58, YELLOW)], tex=ARCH)
    add(777.82, cus(G14.spike, mode="pull", t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(781.66, kb(F(9432581500), "punch", "doc"), [big("LOS DIRECTIVOS LO FUERON AFLOJANDO", 0.1, 0.86, 62)], tex=CLEAN)
    add(784.04, cus(_card, lines=[("LO SACÓ DEL TODO", 60, GREY_, 0.34, 0.0), ("EVERETT MICHAELS", 120, WHITE, 0.5, 0.3),
                                  ("DE LA COMPAÑÍA DE CHATARRA", 64, YELLOW, 0.66, w("de la compañía", 787.2) - 784.04)]), tr="fade", td=0.2, tex=GFX)
    add(787.22, L("8c34149", kb("u_HGCqL-tRcac.jpg", "in", "archival"), "Recogida de chatarra en Fort Kent (Maine), 1942 · FSA/OWI · " + CAP_LOC),
        [big("QUE SE IBA A QUEDAR CON LOS RIELES", 0.1, 0.86, 62)], tex=ARCH)
    add(790.38, kb(F(53267057083), "in", "warm"), [big("EL PÚBLICO APLAUDIÓ…", 0.0, 0.3, 64), big("…Y MÁS DE UNO TENÍA LOS OJOS HÚMEDOS", w("aunque", 791.9) - 790.38, 0.86, 58, YELLOW)],
        tex=CLEAN)
    add(794.16, kb(F(2167001390), "in", "dark"), [Darken(0.3), big("YA TE LO ADELANTÉ AL PRINCIPIO", 0.1, 0.5, 66)], tex=DARK)
    add(796.0, kb(F(1588802176), "punch", "doc"), [Stamp("NO ERA DE ORO", 0.1, RED_, (0.5, 0.5), -8, 120)], tex=CLEAN)
    add(797.62, cus(_card, lines=[("Y LA RAZÓN ES…", 70, GREY_, 0.4, 0.0), ("CASI CÓMICA", 130, YELLOW, 0.56, 0.6)]), tr="fade", td=0.2, tex=GFX)
    add(799.44, cus(G14.spike, mode="gold", t0=-9, t_tie=99), [big("EL CLAVO DE ORO DE 1869…", 0.1, 0.84, 60), big("…SOLO ESTUVO EN LA VÍA UNOS MINUTOS", w("solo estuvo", 801.6) - 799.44, 0.92, 56, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(804.32, kb(F(6472846821), "in", "archival"), [big("AL TERMINAR LA CEREMONIA…", 0.0, 0.86, 64)], tex=ARCH)
    add(805.84, cus(G14.spike, mode="swap", t0=-9, swap_t=0.2), tr="fade", td=0.2, tex=GFX)
    add(808.76, kb(F(49225875482), "in", "dark"), [big("EL DE ORO VOLVIÓ A MANOS DE SU DUEÑO", 0.0, 0.86, 62, GOLD)], tex=DARK)
    add(810.5, kb("u_uDtK4fKM6mI.jpg", "in", "doc"), [Badge("DESDE 1892", 0.1, None), BigText("UNIVERSIDAD DE STANFORD", "serif", 96, WHITE, (0.5, 0.14), w("stanford", 813.6) - 810.5,
                                                                                               None, "up")], tex=CLEAN)
    add(w("en california", 815.4) - 0.3, kb(F(2167001390), "punch", "dark"), [big("EN UN MUSEO DE STANFORD, EN CALIFORNIA", 0.1, 0.86, 60, GOLD)], tex=DARK)
    add(816.56, cus(G14.spike, mode="pull", t0=-9, inch=False), [big("EL QUE ARRANCÓ EL GOBERNADOR EN 1942…", 0.1, 0.9, 58, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(820.06, kb(F(84216464), "in", "doc"), [big("…ERA UNO CUALQUIERA, PUESTO PARA LA OCASIÓN", 0.0, 0.86, 58)], tex=CLEAN)
    add(823.24, kb(F(53266774791), "in", "doc"), [big("COMO LA PRIMERA, EN PARTE UN ESPECTÁCULO", 0.2, 0.86, 60)], tex=CLEAN)
    add(828.42, kb("u_rVU56Znkt38.jpg", "in", "warm"), [big("PERO A NADIE LE IMPORTÓ", 0.0, 0.86, 74, YELLOW)], tex=CLEAN)
    add(830.1, kb(F(53267056468), "in", "warm"), [big("NO HABÍAN IDO POR EL CLAVO", 0.0, 0.3, 64),
                                                  big("SINO A DESPEDIRSE DE ALGO QUE ERA PARTE DE SU HISTORIA", w("había ido", 832.3) - 830.1, 0.86, 52, YELLOW)], tex=CLEAN)
    add(835.62, L("8c34160", kb("u_5_uEbMeeJrc.jpg", "in", "archival"), "Recogida de chatarra en Fort Kent (Maine), 1942 · FSA/OWI · " + CAP_LOC),
        [big("Y EMPEZÓ EL TRABAJO DE VERDAD", 0.1, 0.86, 66, YELLOW)], tex=ARCH)

    # ============================== CAP 7: ADÓNDE FUE EL ACERO (838.9 - 965.5)
    bg, ov = chapter(7, "ADÓNDE FUE EL ACERO", "u_ib7jwp7m0iA.jpg", g="warm", year="1942")
    add(838.94, bg, ov, tr="black", td=0.2, tex=DARK)
    add(842.0, cus(G14.teardown, t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(845.84, kb(F(1834382789), "in", "doc"), [big("QUITABAN LOS CLAVOS", 0.0, 0.3, 66), big("LEVANTABAN LOS RIELES CON GRÚAS", w("levantaban", 846.9) - 845.84, 0.86, 62)],
        tex=CLEAN)
    add(848.96, L("8c34729", kb("u_T8vNEq4IRqM.jpg", "in", "archival"), "Electroimán cargando chatarra en un vagón, Washington, 1942 · FSA/OWI · " + CAP_LOC),
        [big("A LOS VAGONES PLANOS", 0.0, 0.86, 70)], tex=ARCH)
    add(850.54, cus(G14.teardown, t0=-1.5, title=False), [big("Y EL TREN DE TRABAJO RETROCEDÍA UN POCO MÁS", 0.1, 0.11, 56, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(853.6, kb(F(24315260230), "in", "warm"), [big("DETRÁS SOLO QUEDABA EL TERRAPLÉN, DESNUDO", 0.1, 0.86, 58)], tex=CLEAN)
    t0 = 856.84
    add(t0, mp("pm_reg", [(0, -112.85, 41.45, 0.86), (4.9, -112.85, 41.45, 0.9)],
               [dict(type="route", ll=OLD, t0=0.0, draw=0.01, color=(200, 200, 210), width=8, t1=w("habían", 859.4) - t0),
                dict(type="route", ll=OLD, t0=0.0, draw=0.01, color=(130, 110, 80), width=4, dash=14)]),
        [Counter(0, 100, "{:.0f}", "MILLAS EN UN MES", 0.2, 1.2, (0.5, 0.82), 120, prefix="+", color=YELLOW),
         big("DESAPARECIERON DEL DESIERTO", w("habían", 859.4) - t0, 0.1, 62, RED_)], tr="zoom", td=0.3, tex=GFX)
    add(861.7, kb(F(26235873513), "in", "warm"), [big("EL RAMAL MÁS LARGO ABANDONADO EN TODO EL PAÍS ESE AÑO", 0.1, 0.86, 52)], tex=CLEAN)
    add(865.46, kb(F(53458590708), "punch", "dark"), [big("¿Y ADÓNDE FUE TODO ESE ACERO?", 0.0, 0.5, 84, YELLOW, "pop")], tex=DARK)
    t0 = 866.94
    add(t0, mp("pm_reg", [(0, -112.3, 41.35, 1.05), (7.0, -112.2, 41.3, 1.15)],
               [dict(type="pin", at="pm_promontory", t0=0.0, label="PROMONTORY", side="l", box=True, size=38),
                dict(type="route", ll=[(-112.548, 41.6185), (-112.2, 41.45), (-111.974, 41.223)], t0=0.6, draw=1.4, color=YELLOW, width=6),
                dict(type="pin", at="pm_ogden", t0=w("ogden", 872.4) - t0, label="OGDEN", side="r", box=True, size=40),
                dict(type="route", ll=[(-111.974, 41.223), (-112.026, 41.111)], t0=w("clearfield", 873.2) - t0, draw=0.6, color=YELLOW, width=6),
                dict(type="pin", at="pm_clearfield", t0=w("clearfield", 873.2) - t0 + 0.4, label="CLEARFIELD", side="r", box=True, size=40)]),
        [big("A LOS GRANDES DEPÓSITOS MILITARES", w("depósitos", 870.2) - t0, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(874.02, V("4462", "u_cw8zyuWz8CU.jpg", 0.0, "doc"), [big("PARA MOVER MUNICIONES Y SUMINISTROS", 0.0, 0.86, 62)], tex=CLEAN)
    t0 = 876.68
    add(t0, mp("pm_west", [(0, -115.6, 40.2, 1.1), (4.7, -116.4, 39.6, 1.15)],
               [dict(type="pin", at="pm_promontory", t0=0.0, label="PROMONTORY", side="r", box=True, size=38),
                dict(type="route", ll=[(-112.548, 41.6185), (-115.5, 40.6), (-118.6246, 38.5246)], t0=0.3, draw=1.6, color=YELLOW, width=6, dash=20),
                dict(type="pin", at="pm_hawthorne", t0=w("hawthorne", 879.7) - t0, label="HAWTHORNE (NEVADA)", side="r", box=True, size=40)]),
        [big("SEGÚN ALGUNOS: UN ARSENAL DE LA MARINA", 0.1, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(881.4, L("70421", kb("u_FvQ5YgLbiEg.jpg", "in", "doc"), "Polvorines militares cerca de Hawthorne, Nevada · Carol M. Highsmith · " + CAP_LOC),
        [Badge("HAWTHORNE, NEVADA", 0.1, None), big("BOMBAS Y MUNICIÓN PARA LA GUERRA EN EL PACÍFICO", 0.4, 0.92, 54)], tex=ARCH)
    add(885.1, kb("u_eLeXwRx4ALs.jpg", "in", "warm"), [big("LOS RIELES DEL ORO Y LA PLATA DEL OESTE…", 0.0, 0.86, 60, GOLD)], tex=CLEAN)
    add(887.5, kb("u_-o0HZfyurbc.jpg", "in", "warm"), [big("…ACABARON MOVIENDO PROYECTILES", 0.2, 0.86, 70, RED_)], tex=CLEAN)
    add(891.0, cus(_card, lines=[("UNA IRONÍA", 120, YELLOW, 0.44, 0.0), ("DIFÍCIL DE INVENTAR", 70, WHITE, 0.6, 0.5)]), tr="fade", td=0.2, tex=GFX)
    add(893.1, kb(F(51668596324), "in", "doc"), [Badge("1870", 0.1, None), big("OGDEN LE QUITÓ A PROMONTORY EL ENLACE", 0.4, 0.86, 60)], tex=CLEAN)
    add(898.4, cus(_card, lines=[("72 AÑOS DESPUÉS…", 70, GREY_, 0.38, 0.0), ("SE QUEDÓ TAMBIÉN CON SUS RIELES", 84, YELLOW, 0.54, 0.6)]), tr="fade", td=0.2, tex=GFX)
    add(901.88, kb("u_6T_1WqO8jlY.jpg", "in", "doc"), [big("DOS TROZOS DE RIEL COMO RECUERDO", 0.1, 0.86, 64)], tex=CLEAN)
    t0 = 905.02
    add(t0, mp("pm_reg", [(0, -112.1, 41.4, 1.4), (2.8, -112.1, 41.4, 1.45)],
               [dict(type="pin", at="pm_ogden", t0=0.0, label="OGDEN", side="r", box=True, size=44),
                dict(type="pin", at="pm_brigham", t0=w("brigham", 906.4) - t0, label="BRIGHAM CITY", side="r", box=True, size=44)]),
        tr="zoom", td=0.3, tex=GFX)
    add(907.78, kb(F(6562128955), "in", "doc"), [Badge("BRIGHAM CITY", 0.1, None), big("ACABÓ EN UN PEQUEÑO MONUMENTO QUE TODAVÍA EXISTE", 0.4, 0.86, 52)], tex=CLEAN)
    add(912.1, kb(F(6562129221), "in", "doc"), [big("SI PASAS POR ALLÍ, PUEDES TOCARLO", 0.1, 0.86, 64, YELLOW)], tex=CLEAN)
    add(914.66, kb("u_-mUBrTfsu0A.jpg", "in", "doc"), [big("HIERRO DE LA VÍA MÁS FAMOSA DEL PAÍS", 0.1, 0.86, 62)], tex=CLEAN)
    add(918.06, kb(F(341604649), "in", "archival"), [Badge("OGDEN", 0.0, None), Stamp("PERDIDO", 0.3, RED_, (0.5, 0.55), -8, 120)], tex=ARCH)
    add(919.54, cus(G14.spike, mode="pull", t0=-9, inch=False), [big("¿Y EL CLAVO DEL GOBERNADOR?", 0.1, 0.84, 60, YELLOW),
                                                                 big("A UNA ASOCIACIÓN DE PIONEROS", w("se entregó", 921.4) - 919.54, 0.92, 56)], tr="fade", td=0.2, tex=GFX)
    add(923.62, kb("u_Z0oDwCjEDz8.jpg", "in", "doc"), [big("EXPUESTO UN TIEMPO EN EL CAPITOLIO DE UTAH", 0.1, 0.86, 58)], tex=CLEAN)
    add(926.58, kb("u_rmUZEsTQr5Y.jpg", "in", "cold"), [Stamp("PARADERO DESCONOCIDO", 0.1, RED_, (0.5, 0.5), -6, 96)], tex=CLEAN)
    add(928.86, kb("u_LtS8IRxtdT4.jpg", "in", "doc"), [big("MIENTRAS, EL ATAJO SIGUIÓ CAMBIANDO EL PAISAJE", 0.2, 0.86, 56)], tex=CLEAN)
    add(933.94, L("582561c", kb(F(5392295172), "in", "doc"), "Caballete del atajo Ogden-Lucin · HAER · " + CAP_LOC),
        [Badge("AÑOS 50", 0.1, None), big("EL PUENTE DE MADERA…", 0.4, 0.86, 64)], tex=ARCH)
    add(936.48, kb(F(5392295172), "in", "doc"), [big("…SE CAMBIA POR UN TERRAPLÉN DE TIERRA Y ROCA", 0.0, 0.86, 58)], tex=CLEAN)
    add(939.3, cus(G14.split_lake, t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(942.16, kb("u_kN89XrQog0k.jpg", "punch", "doc"), [big("AL NORTE, MUCHO MÁS SALADO", 0.0, 0.3, 62), big("ROJIZO, CASI ROSA", w("y tomó", 944.8) - 942.16, 0.86, 80, (230, 130, 150))],
        tex=CLEAN)
    add(947.9, kb(N("iss015e05815"), "in", "doc"), [big("AL SUR, VERDE", 0.0, 0.86, 80, (90, 190, 170))], tex=CLEAN)
    add(949.0, kb(N("iss059e099093"), "punch", "doc"), [Badge("FOTO DESDE LA ESTACIÓN ESPACIAL · NASA", 0.1, None), big("TODAVÍA SE VE LA RAYA", 0.6, 0.86, 76, YELLOW)],
        tex=CLEAN)
    add(952.54, L("582561c", kb(F(17712449353), "in", "archival"), "Lucin Cutoff · " + CAP_LOC),
        [big("Y EL VIEJO PUENTE QUE MATÓ A PROMONTORY…", 0.1, 0.12, 56), big("…TAMPOCO SE SALVÓ", w("tampoco", 954.6) - 952.54, 0.86, 70, RED_)], tex=ARCH)
    add(956.12, kb("u_g4ZcRJUpFPQ.jpg", "in", "warm"), [Badge("DESDE 1993", 0.1, None), big("SE DESMONTÓ", 0.4, 0.86, 76)], tex=CLEAN)
    add(958.74, kb("u_R6tJUiEYZ6g.jpg", "in", "warm"), [big("MADERA CURTIDA CASI UN SIGLO EN AGUA SALADA", 0.1, 0.86, 56)], tex=CLEAN)
    add(962.56, kb("u_dsbPXrmGcOA.jpg", "in", "warm"), [big("VENDIDA PARA MUEBLES Y CASAS", 0.1, 0.86, 66, YELLOW)], tex=CLEAN)

    # ============================== CAP 8: HOY (965.5 - 1095.9)
    bg, ov = chapter(8, "LO QUE QUEDA DE PROMONTORY", F(53265883227), g="doc", year="HOY")
    add(965.46, bg, ov, tr="black", td=0.2, tex=DARK)
    add(968.5, L("158148p", kb(F(44738313224), "in", "doc"), "Monumento al clavo de oro, condado de Box Elder · HABS · " + CAP_LOC),
        [big("UN MONUMENTO DE PIEDRA… Y EL VIENTO", 0.1, 0.9, 58)], tex=ARCH)
    add(970.04, kb(F(36026286245), "in", "doc"), [Badge("1965", 0.1, None), big("SITIO HISTÓRICO NACIONAL", w("declarado", 973.3) - 970.04, 0.86, 72, YELLOW)], tex=CLEAN)
    add(975.4, kb(F(12004010574), "in", "doc"), [Badge("1969 · CENTENARIO", 0.1, None), big("VUELVE A TENDERSE UN TRAMO DE VÍA", w("volvieron", 978.2) - 975.4, 0.86, 60)],
        tex=CLEAN)
    add(978.22, kb(F(52466090825), "in", "doc"), [big("UN TRAMO CORTO, PARA LAS VISITAS", 0.4, 0.86, 64)], tex=CLEAN)
    add(982.34, kb(F(22825879887), "in", "doc"), [Badge("1979", 0.1, None), big("RÉPLICAS EXACTAS DEL JUPITER…", 0.4, 0.86, 64)], tex=CLEAN)
    add(986.28, kb(F(53267056468), "in", "doc"), [big("…Y DE LA 119, QUE FUNCIONAN DE VERDAD", 0.0, 0.86, 62, YELLOW)], tex=CLEAN)
    add(989.5, kb(F(53265883327), "in", "doc"), [Badge("2019", 0.1, None), big("PARQUE HISTÓRICO NACIONAL", 0.4, 0.86, 72, YELLOW)], tex=CLEAN)
    add(993.14, kb(F(35750879260), "in", "doc"), [big("CADA MAYO, LAS DOS RÉPLICAS FRENTE A FRENTE", 0.1, 0.86, 58)], tex=CLEAN)
    add(997.26, kb(F(22852991529), "punch", "doc"), [big("Y ALGUIEN REPITE LA ESCENA DE 1869", 0.0, 0.86, 64, YELLOW)], tex=CLEAN)
    t0 = 1001.14
    add(t0, mp("pm_reg", [(0, -112.6, 41.62, 1.6), (3.8, -112.9, 41.66, 1.45)],
               [dict(type="pin", at="pm_promontory", t0=0.0, label="PARQUE", side="r", box=True, size=40),
                dict(type="route", ll=[p for p in OLD if -113.2 < p[0] < -112.54][::-1], t0=0.6, draw=2.6, color=(220, 190, 140), width=6, dash=16)]),
        [big("CAMINOS DE TIERRA HACIA EL OESTE", 0.2, 0.1, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(1004.98, kb(F(26746736192), "in", "doc"), [big("LO QUE DE VERDAD QUEDÓ", 0.0, 0.86, 72, YELLOW)], tex=CLEAN)
    add(1006.38, kb(F(26234958554), "in", "doc"), [big("LOS TERRAPLENES, SIN RIELES", 0.1, 0.86, 72)], tex=CLEAN)
    add(1008.86, kb(F(26746733792), "in", "doc"), [big("LOS CORTES EN LA ROCA, A PICO Y PALA", 0.1, 0.86, 64)], tex=CLEAN)
    add(1011.74, kb(F(26234962934), "in", "doc"), [big("LOS RESTOS DE LOS CABALLETES", 0.1, 0.86, 68)], tex=CLEAN)
    add(1013.56, cus(G14.parallel, t0=-9, blast_t=999), [big("LOS DOS TERRAPLENES DE AQUELLA CARRERA ABSURDA", 0.3, 0.9, 54, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(1018.4, kb(F(23964257354), "in", "warm"), [big("UNO AL LADO DEL OTRO, IGUAL DE VACÍOS", 0.0, 0.86, 64)], tex=CLEAN)
    add(1021.38, kb(F(26773123011), "in", "doc"), [BigText("TERRACE", "serif", 110, YELLOW, (0.5, 0.14), 0.0, None, "up"), big("CIMIENTOS Y UN CEMENTERIO", 0.4, 0.86, 66)],
        tex=CLEAN)
    add(1024.66, kb("u_du8xCg9IznM.jpg", "in", "cold"), [big("CASTIGADO POR LOS SAQUEADORES", 0.0, 0.86, 66, RED_)], tex=CLEAN)
    add(1026.72, kb("u_GkhcoWrAzNA.jpg", "in", "cold"), [BigText("KELTON", "serif", 110, YELLOW, (0.5, 0.14), 0.0, None, "up"),
                                                       big("UNAS POCAS LÁPIDAS MEDIO ENTERRADAS", 0.4, 0.86, 60)], tex=CLEAN)
    add(1029.98, kb(F(26746741062), "in", "warm"), [big("UN DESIERTO TAN SECO…", 0.0, 0.3, 64),
                                                    big("…QUE EL TERRAPLÉN SIGUE CASI IGUAL QUE CUANDO LO DEJARON", w("que el terraplén", 1032.2) - 1029.98, 0.86, 52, YELLOW)], tex=CLEAN)
    q2(1035.24, bg="u_saS98jKhVjA.jpg", badge="LA GRAN PREGUNTA")
    add(1042.86, kb(F(53267056313), "in", "doc"), [Badge("1942", 0.1, None), big("NADIE LO VIO COMO UNA DERROTA", 0.4, 0.86, 72, YELLOW)], tex=CLEAN)
    add(1047.18, kb("u_kN89XrQog0k.jpg", "in", "doc"), [big("CASI 40 AÑOS CRUZANDO POR EL LAGO", 0.1, 0.86, 64)], tex=CLEAN)
    add(1050.46, kb(F(53267244235), "in", "cold"), [big("PROMONTORY: MÁS UN RECUERDO QUE UNA VÍA", 0.1, 0.86, 62)], tex=CLEAN)
    add(1053.96, kb("u_-o0HZfyurbc.jpg", "in", "warm"),
        [big("EN PLENA GUERRA, SU ACERO PARA EL PAÍS", 0.1, 0.92, 58, YELLOW)], tex=ARCH)
    add(1056.42, kb("u_auj_oFzaVOw.jpg", "in", "warm"), [big("LA FORMA MÁS DIGNA DE JUBILARLA", 0.1, 0.86, 70, YELLOW)], tex=CLEAN)
    add(1058.86, kb("u_5_uEbMeeJrc.jpg", "in", "doc"), [big("NO LA TIRARON A LA BASURA…", 0.0, 0.86, 70)], tex=CLEAN)
    add(1060.44, kb("u_P8jEvckndSE.jpg", "in", "warm"), [big("…LA MANDARON A SERVIR UNA ÚLTIMA VEZ", 0.0, 0.86, 66, YELLOW)], tex=CLEAN)
    add(1062.92, kb("u_IG1VKwKUY7E.jpg", "in", "warm"), [big("POR ESO LE HICIERON UNA FIESTA", 0.0, 0.3, 70, YELLOW),
                                                       big("NO PARA CELEBRAR QUE SE IBA…", w("no para", 1064.3) - 1062.92, 0.86, 62)], tex=CLEAN)
    add(1066.5, kb(F(53266774791), "in", "warm"), [big("…SINO PARA DESPEDIRLA COMO SE MERECÍA", 0.0, 0.86, 64, YELLOW)], tex=CLEAN)
    add(1068.86, kb(F(3641701190), "in", "dark"), [Darken(0.45), big("Y MARY IPSEN ESTUVO EN LAS DOS", 0.1, 0.5, 80, YELLOW)], tex=DARK)
    t0 = 1071.4
    add(t0, cus(G14.lifeline, t0=-0.3, t73=w("73", 1073.5) - t0, t42=w("vio cómo se desarmaba", 1076.0) - t0), tr="fade", td=0.2, tex=GFX)
    add(1078.08, kb(F(26234958554), "in", "dark"), [Darken(0.45), FnOverlay(G4.comments, line1="¿HICIERON BIEN EN MANDAR ESOS RIELES A LA GUERRA",
                                                                             line2="O TENDRÍAN QUE HABERLOS DEJADO COMO MONUMENTO?", cta="TE LEO EN LOS COMENTARIOS")],
        tex=DARK)
    add(1087.48, kb(F(53267244235), "in", "dark", z=1.1), [Darken(0.55), FnOverlay(G2.subscribe), big("SIGUE RECORRIENDO LAS VÍAS QUE ESTADOS UNIDOS DEJÓ ATRÁS", 0.2, 0.14, 50,
                                                                                                        YELLOW)], tex=DARK)
    add(1091.86, kb(F(2167001390), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("AQUÍ NO HACE FALTA NINGÚN CLAVO DE ORO", 0.1, 0.14, 56, GOLD),
                                                         big("CON UN CLIC BASTA", w("con un clic", 1094.6) - 1091.86, 0.26, 70, WHITE, "pop")], tex=DARK)
    return S


def pick_f(fid, fallback, cap):
    f = f"f_{fid}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, "archival")
    return fallback


def pick_l(lid, fallback, cap):
    return L(lid, fallback, cap)
