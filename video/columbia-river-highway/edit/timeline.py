"""The edit: every shot of the Columbia River Highway video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx7 as G7
import gfx16 as G16
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1076.82
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












# ------------------------------------------------------------------ Columbia River Highway specifics
LINE = M.cr_ll("line")
CRD = M.cr_data()
ROAD = [[tuple(p) for p in r] for r in CRD["road"]]
UNDER = [[tuple(p) for p in r] for r in CRD["under"]]
I84 = [[tuple(p) for p in r] for r in CRD["i84"]]
WEST = [tuple(p) for p in CRD["west"]]
GAP = [tuple(p) for p in CRD["gap"]]
CAP_LOC = "Library of Congress"
F = lambda i: f"f_{i}.jpg"
U = lambda i: f"u_{i}.jpg"
WK = lambda n: f"w_{n}.jpg"
RED_ = (230, 70, 60)
BLUE_ = (110, 170, 220)
GREEN_ = (90, 210, 120)
GOLD = (236, 190, 70)
NIGHT = dict(grain=8, vignette=1.1)
SNOWY = G2.SnowOverlay(300, 4, 1.0)
SNOWY2 = G2.SnowOverlay(420, 9, 1.6)
US30 = [(-123.83, 46.19), (-122.68, 45.52), (-121.18, 45.60), (-117.0, 44.0), (-116.2, 43.6), (-112.45, 42.87), (-110.0, 41.6),
        (-104.82, 41.14), (-98.4, 40.9), (-96.0, 41.26), (-91.5, 41.9), (-87.65, 41.88), (-84.5, 41.0), (-80.0, 40.44), (-75.16, 39.95), (-74.4, 39.36)]
COAST = [(-122.33, 47.6), (-116.2, 43.6), (-104.99, 39.74), (-95.99, 41.25), (-87.63, 41.88), (-80.0, 40.44), (-74.0, 40.71)]
WIRE = [(-77.03, 38.90), (-84.5, 39.1), (-95.0, 40.0), (-105.0, 42.0), (-116.0, 44.5), (-122.24, 45.54)]


def _card(t, dur, lines=()):
    from gfx import background
    img = background("dark_grid", t)
    for tx, sz, col, y, t0 in lines:
        G2.label(img, tx, 960, 1080 * y, ease_out(prog(t, t0, 0.4)), sz, col)
    return img


def WP(name, fallback, cap, g="archival"):
    """Wikimedia Commons picture (framed) if it was downloaded, else the fallback base."""
    f = WK(name)
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, g)
    return fallback


def _declutter(S):
    """Framed photos with a caption: shrink the photo a little and push bottom text below the caption."""
    from gfx import BigText, Framed, Rich
    for sh in S:
        b = sh.base
        if not (isinstance(b, Framed) and b.caption):
            continue
        low = [o for o in sh.ov if (isinstance(o, BigText) and o.pos[1] > 0.75) or (isinstance(o, Rich) and o.y > 0.75)]
        if not low:
            continue
        b.box, b.cyf = (0.66, 0.6), 0.45
        for o in low:
            if isinstance(o, BigText):
                o.pos = (o.pos[0], 0.925)
            else:
                o.y = 0.925
    return S


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg=F(10488711553), badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Por qué dos hombres se quedaron nueve días viviendo en un túnel, cuando todos los demás se fueron?", ("nueve", "túnel,", "fueron?"), size=64),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg=F(33194005485), badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Y por qué Oregón enterró los túneles de su carretera más admirada, para acabar construyéndolos otra vez?", ("enterró", "otra", "vez?"), size=62),
            tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 60.5)
    add(0.0, kb(F(10488711553), "in", "doc"), [rich("IMAGINA VIVIR NUEVE DÍAS DENTRO DE UN TÚNEL DE CARRETERA", ("nueve", "días", "túnel"), 0.3, step=0.1, y=0.84,
                                                    size=58, maxw=0.86)], tex=CLEAN)
    add(3.46, kb(U("hyNbatg81Po"), "in", "dark"), [big("NO EN UNA CUEVA…", 0.0, 0.3, 70), big("…NI EN UN REFUGIO DE MONTAÑA", w("refugio", 5.0) - 3.46, 0.86, 64)],
        tex=CLEAN)
    add(5.84, kb(F(10488538355), "down", "doc"), [big("EN UN TÚNEL", 0.0, 0.14, 90, YELLOW), big("CON EL RÍO RUGIENDO CIENTOS DE PIES MÁS ABAJO", 1.0, 0.86, 54)],
        tex=CLEAN)
    t0 = 9.54
    add(t0, mp("cr_us", [(0, -119.5, 44.0, 1.6), (2.8, -121.2, 45.0, 2.3)],
               [dict(type="label", at=(-120.5, 44.0), text="OREGÓN", t0=w("oregón", 11.6) - t0, size=56, box=True),
                dict(type="pin", at="cr_twin", t0=w("oregón", 11.6) - t0 + 0.3, label="LA GARGANTA DEL COLUMBIA", side="r", box=True, size=34)]),
        [Badge("NOVIEMBRE DE 1921", 0.1, None)], tr="zoom", td=0.3, tex=GFX)
    add(12.4, cus(_card, lines=[("DOS HOMBRES", 170, YELLOW, 0.48, 0.0), ("LO HICIERON", 70, WHITE, 0.64, 0.4)]), tr="fade", td=0.15, tex=GFX)
    add(14.28, kb(U("yxbjmHnAFDI"), "in", "doc"), [big("COCINARON GANSOS…", 0.1, 0.86, 76, YELLOW)], tex=CLEAN)
    add(w("hornillo", 15.6), kb(U("N561DZ3NfVM"), "in", "doc"), [big("…EN UN HORNILLO DE CAMPING", 0.0, 0.86, 70)], tex=CLEAN)
    add(16.6, kb(U("pImp9uVuMrc"), "punch", "doc"), [big("ASARON MANZANAS", 0.0, 0.86, 80, YELLOW)], tex=CLEAN)
    add(w("miraron", 18.0), kb(F(33037103702), "in", "archival"), [big("Y MIRARON EL PAISAJE POR VENTANAS ABIERTAS EN LA ROCA", 0.2, 0.9, 52)], tex=ARCH)
    add(21.14, cus(G16.carving, t0=0.2, names_t=1.6), [big("ANTES DE IRSE, GRABARON SUS NOMBRES EN LA PARED", 0.2, 0.08, 54, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(24.04, kb(F(32348982144), "in", "archival"), [Badge("30 AÑOS DESPUÉS", 0.1, None), big("EL ESTADO LLENÓ ESE TÚNEL DE ROCAS…", 0.3, 0.86, 62)], tex=ARCH)
    add(25.7, cus(G16.fill, t0=-1.4, title="…HASTA EL TECHO"), tr="fade", td=0.15, tex=GFX)
    add(27.64, kb(F(31741900193), "in", "archival"), [big("A OTRO, EL MÁS BONITO DE TODOS…", 0.1, 0.86, 64)], tex=ARCH)
    add(w("volar", 30.3), V("51821", U("ZcozVqL5FKc"), 0.0, "doc"), [Flash(0.0, 0.2), big("…LO HIZO VOLAR EN PEDAZOS", 0.1, 0.86, 76, RED_, "pop")],
        post=postshake(6), tex=CLEAN)
    add(32.12, kb(F(11354002363), "in", "archival"), [big("LA CARRETERA MÁS ADMIRADA QUE OREGÓN HABÍA CONSTRUIDO NUNCA", 0.2, 0.9, 50)], tex=ARCH)
    add(36.42, kb(U("Iz_Yuy1gFCY"), "in", "doc"), [Darken(0.35), big("«LA LLAMABAN»", 0.0, 0.3, 50, GREY_),
                                                  BigText("COLUMBIA RIVER HIGHWAY", "serif", 104, WHITE, (0.5, 0.48), 0.3, None, "up"),
                                                  big("LA CARRETERA DEL RÍO COLUMBIA", 0.8, 0.62, 52, YELLOW)], tr="fade", td=0.3, tex=CLEAN)
    add(38.98, kb(F(51721940961), "in", "doc"), [Badge("HOY", 0.1, None), big("EL MISMO ESTADO GASTA MILLONES EN VOLVER A ABRIRLOS", 0.3, 0.86, 54)], tex=CLEAN)
    add(w("uno por uno", 42.2), kb(F(52411893685), "punch", "doc"), [big("UNO POR UNO", 0.0, 0.86, 90, YELLOW, "pop")], tex=CLEAN)
    add(43.96, kb(F(10488714063), "in", "dark"), [big("Y LO QUE PASÓ CON AQUELLAS DOS FIRMAS…", 0.1, 0.3, 60),
                                                 big("…ES LO ÚLTIMO QUE NADIE ESPERABA", w("lo último", 46.6) - 43.96, 0.86, 64, YELLOW)], tex=DARK)
    q1(48.52)
    q2(53.64)

    # ============================== CAP 1: EL SUEÑO DE SAM HILL (60.5 - 177.9)
    bg, ov = chapter(1, "EL SUEÑO DE SAM HILL", U("hgLk4h8AkJY"), g="doc", year="1900–1913")
    add(60.52, bg, ov, tr="black", td=0.2, tex=DARK)
    add(63.4, L("22254", cus(_card, lines=[("SAM HILL", 160, WHITE, 0.5, 0.0)]), "Samuel Hill, 1915 · " + CAP_LOC),
        [LowerThird("SAM HILL", "UN HOMBRE MUY RICO", 0.3), big("SU DINERO: LOS TRENES", w("trenes", 65.8) - 63.4, 0.1, 54, YELLOW)], tex=ARCH)
    add(66.66, kb(U("OOdaVUis_3E"), "in", "doc"), [big("LO QUE LE QUITABA EL SUEÑO:", 0.1, 0.12, 54), big("LAS CARRETERAS", w("carreteras", 68.8) - 66.66, 0.86, 90, YELLOW, "pop")],
        tex=CLEAN)
    add(69.54, L("3a38821", kb(U("Yoqi404MJ8M"), "in", "doc"), "Autos camino de las cuevas de Oregón, 1913 · " + CAP_LOC),
        [Badge("PRINCIPIOS DEL SIGLO XX", 0.1, None), big("CAMINOS DE TIERRA Y BARRO", w("tierra", 72.6) - 69.54, 0.92, 62, YELLOW)], tex=ARCH)
    t0 = 74.28
    add(t0, mp("cr_us", [(0, -98.0, 39.5, 0.62), (3.8, -98.0, 39.5, 0.66)],
               [dict(type="route", ll=COAST, t0=0.4, draw=2.6, color=YELLOW, width=7, dash=26),
                dict(type="label", at=(-98.0, 46.5), text="AUTOPISTAS PAVIMENTADAS DE COSTA A COSTA", t0=0.6, size=44, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(78.16, cus(_card, lines=[("ERA UN HOMBRE", 70, GREY_, 0.4, 0.0), ("EXCÉNTRICO", 170, YELLOW, 0.56, 0.2)]), tr="fade", td=0.15, tex=GFX)
    t0 = 79.7
    add(t0, mp("cr_reg", [(0, -121.4, 45.6, 0.8), (3.3, -120.95, 45.65, 1.05)],
               [dict(type="label", at=(-121.6, 45.95), text="WASHINGTON", t0=w("washington", 82.0) - t0, size=46, box=True),
                dict(type="label", at=(-121.6, 45.25), text="OREGÓN", t0=0.3, size=46, box=True),
                dict(type="pin", at="cr_maryhill", t0=w("washington", 82.0) - t0 + 0.4, label="SU MANSIÓN", side="l", box=True, size=38)]),
        tr="zoom", td=0.3, tex=GFX)
    add(83.0, kb(F(10488734584), "in", "doc"), [big("UNA MANSIÓN ENORME EN MITAD DE LA NADA", 0.1, 0.86, 58)], tex=CLEAN)
    add(85.36, kb(F(28113709259), "in", "doc"), [big("Y AL LADO…", 0.1, 0.12, 60), BigText("STONEHENGE", "serif", 120, WHITE, (0.5, 0.5), w("stonehenge", 89.3) - 85.36, None, "up"),
                                                big("A TAMAÑO REAL", w("tamaño", 88.0) - 85.36, 0.86, 70, YELLOW)], tex=CLEAN)
    add(90.74, L("50402", kb(F(39861851202), "in", "doc"), "Maryhill Stonehenge · Carol M. Highsmith · " + CAP_LOC),
        [big("POR LOS MUERTOS DE LA PRIMERA GUERRA MUNDIAL", 0.3, 0.92, 52, YELLOW)], tex=ARCH)
    add(93.86, kb(U("xpw5IOgLjuw"), "in", "doc"), [Badge("VIAJE A EUROPA", 0.1, None), big("CON SU AMIGO EL INGENIERO…", w("su amigo", 95.6) - 93.86, 0.86, 60)], tex=CLEAN)
    add(w("samuel", 97.1), WP("lancaster", cus(_card, lines=[("INGENIERO", 60, GREY_, 0.36, 0.0), ("SAMUEL LANCASTER", 120, WHITE, 0.52, 0.2)]),
                                "Samuel C. Lancaster, 1916 · The World's Work · Wikimedia Commons"),
        tr="fade", td=0.15, tex=ARCH)
    add(98.6, kb(U("cE4BazvvAqI"), "in", "doc"), [big("UNA CARRETERA PODÍA SER UNA OBRA DE ARTE", 0.2, 0.86, 62, YELLOW)], tex=CLEAN)
    add(102.6, L("354581p", kb(U("GFDJQra8yYo"), "in", "doc"), "Puente de Multnomah Creek · HAER · " + CAP_LOC),
        [big("IGUAL QUE UN PUENTE… O UNA CATEDRAL", 0.1, 0.92, 58)], tex=ARCH)
    t0 = 104.62
    add(t0, mp("cr_ch", [(0, 8.2, 46.85, 0.75), (3.2, 8.45, 46.97, 1.7)],
               [dict(type="label", at=(7.4, 46.55), text="SUIZA", t0=0.2, size=60, box=True),
                dict(type="pin", at="cr_lucerne", t0=w("lucerna", 108.6) - t0 if w("lucerna", 108.6) - t0 < 3.0 else 2.6, label="LAGO DE LUCERNA", side="l", box=True, size=36)]),
        tr="zoom", td=0.3, tex=GFX)
    add(107.8, L("07229", kb(U("KBE0J47YBRc"), "in", "doc"), "La Axenstrasse, lago de Lucerna, hacia 1890 · Photochrom · " + CAP_LOC),
        [big("LA CARRETERA SE METÍA DENTRO DEL ACANTILADO", 0.3, 0.92, 54)], tex=ARCH)
    add(111.4, L("1b13213", kb(U("-d5LnEKrlYc"), "in", "doc"), "La Axenstrasse, 1924 · " + CAP_LOC),
        [big("UN TÚNEL CON VENTANAS HACIA EL AGUA", 0.2, 0.92, 60, YELLOW)], tex=ARCH)
    add(113.88, V("2026", U("tmfbPd2hCmM"), 0.0, "dark"), [big("MANEJABAS POR DENTRO DE LA ROCA…", 0.2, 0.86, 64)], tex=DARK)
    add(117.88, kb(U("-d5LnEKrlYc"), "punch", "doc"), [Flash(0.0, 0.25), big("…Y EL PAISAJE APARECÍA DE GOLPE", 0.1, 0.86, 70, YELLOW, "pop")], tex=CLEAN)
    add(120.06, kb(F(7655739614), "in", "archival"), [big("AL VOLVER, HILL TENÍA CLARO LO QUE QUERÍA", 0.2, 0.86, 58)], tex=ARCH)
    add(124.72, kb(U("rvVhr2LngP4"), "in", "doc"), [Badge("1913", 0.1, None), big("INVITÓ A LOS LEGISLADORES DE OREGÓN A SU FINCA", 0.3, 0.86, 56)], tex=CLEAN)
    add(128.28, kb(F(2848624621), "in", "doc"), [big("UNA CARRETERA PAVIMENTADA DE PRUEBA", 0.1, 0.12, 60, YELLOW),
                                                big("LA HABÍA MANDADO CONSTRUIR ÉL MISMO", w("él mismo", 131.4) - 128.28, 0.86, 56)], tex=CLEAN)
    add(133.82, kb(F(3717503753), "in", "doc"), [big("LOS POLÍTICOS VOLVIERON CONVENCIDOS", 0.1, 0.86, 62)], tex=CLEAN)
    t0 = w("la garganta", 138.0)
    add(t0, mp("cr_reg", [(0, -121.75, 45.62, 0.62), (3.4, -121.75, 45.62, 0.7)],
               [dict(type="label", at=(-121.4, 45.95), text="WASHINGTON", t0=0.2, size=40, box=True),
                dict(type="label", at=(-121.4, 45.27), text="OREGÓN", t0=0.2, size=40, box=True),
                dict(type="label", at=(-121.95, 45.68), text="LA GARGANTA DEL COLUMBIA", t0=0.6, size=44, box=True, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(141.42, kb(U("Djh97TvIfpk"), "in", "doc"), [big("UN CAÑÓN ENORME", 0.1, 0.12, 70), big("PAREDES DE BASALTO OSCURO", w("basalto", 143.6) - 141.42, 0.86, 64, YELLOW)],
        tex=CLEAN)
    add(144.9, kb(U("jgRRDfYV7l0"), "in", "doc"), [big("DECENAS DE CASCADAS", 0.1, 0.86, 70)], tex=CLEAN)
    add(w("un río", 146.4), kb(U("8ZytzmKizII"), "in", "doc"), [big("UN RÍO TAN ANCHO QUE PARECE UN LAGO", 0.0, 0.86, 62, YELLOW)], tex=CLEAN)
    add(148.48, kb(U("Do6sxp_IyJA"), "up", "doc"), [big("LA MÁS ALTA DE ESAS CASCADAS", 0.1, 0.86, 54), BigText("MULTNOMAH FALLS", "serif", 100, WHITE, (0.5, 0.16), 0.4, None, "up")],
        tex=CLEAN)
    add(151.42, kb(F(48931923128), "up", "doc"), [Darken(0.3), Counter(0, 600, "{:,.0f}", "PIES", 0.1, 1.2, (0.5, 0.5), 190, sub="MÁS DE 600 PIES · CASI 190 METROS", prefix="+")],
        tex=CLEAN)
    add(155.26, kb(U("Z_uAD9G7lnA"), "in", "dark"), [big("EL PROBLEMA: LA GARGANTA ERA CASI IMPOSIBLE", 0.1, 0.86, 58, YELLOW)], tex=DARK)
    add(158.64, cus(G16.hang, t0=0.0), [big("POR LA ORILLA YA PASABA EL FERROCARRIL", 0.1, 0.94, 50),
                                        big("POR ARRIBA, LOS ACANTILADOS CAÍAN A PICO", w("por arriba", 161.9) - 158.64, 0.2, 50, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(164.56, cus(G16.hang, t0=-9, road_t=w("colgaras", 167.0) - 164.56), [big("NO HABÍA SITIO… A NO SER QUE LA COLGARAS DE LA ROCA", 0.1, 0.94, 48)], tex=GFX)
    add(168.38, cus(_card, lines=[("Y ESO ES EXACTAMENTE", 70, WHITE, 0.4, 0.0), ("LO QUE HICIERON", 130, YELLOW, 0.56, 0.3)]), tr="fade", td=0.15, tex=GFX)
    add(170.74, kb(F(10488545415), "in", "doc"), [big("UNA CARRETERA COLGADA DEL ACANTILADO", 0.1, 0.12, 60, YELLOW),
                                                 big("A CIENTOS DE PIES SOBRE EL AGUA", w("cientos", 172.6) - 170.74, 0.86, 60)], tex=CLEAN)
    add(175.08, kb(U("UkNRoy162l8"), "in", "doc"), [big("ENTRE CASCADAS Y PAREDES DE ROCA", 0.1, 0.86, 62)], tex=CLEAN)

    # ============================== CAP 2: LAS VENTANAS DE MITCHELL POINT (177.9 - 346.7)
    bg, ov = chapter(2, "LAS VENTANAS DE MITCHELL POINT", F(31741899653), g="archival", year="1913–1918")
    add(177.86, bg, ov, tr="black", td=0.2, tex=DARK)
    add(180.5, kb(F(31184842405), "in", "archival"), [Badge("1913 · EMPIEZAN LAS OBRAS", 0.1, None), big("CUADRILLAS COLGADAS DE CUERDAS", 0.4, 0.88, 60)],
        tex=ARCH)
    add(183.18, kb(U("ZcozVqL5FKc"), "punch", "doc"), [Flash(0.05, 0.2), big("ROCA ABIERTA CON DINAMITA", 0.1, 0.86, 70, YELLOW, "pop")], post=postshake(5), tex=CLEAN)
    add(184.62, kb(F(51546650926), "in", "archival"), [big("ESCOMBROS FUERA, EN CARROS TIRADOS POR CABALLOS", 0.3, 0.88, 54)], tex=ARCH)
    add(188.0, L("354578p", kb(F(10488546096), "in", "doc"), "Muro de piedra junto al viaducto oeste de Multnomah Falls · HAER · " + CAP_LOC),
        [big("MUROS DE PIEDRA LEVANTADOS A MANO SOBRE EL VACÍO", 0.4, 0.92, 52, YELLOW)], tex=ARCH)
    add(193.76, kb(U("ojswDCtlE44"), "in", "doc"), [big("NO LUCHABA CONTRA EL PAISAJE…", 0.1, 0.12, 62), big("…LO ENSEÑABA", w("enseñaba", 197.0) - 193.76, 0.86, 90, YELLOW, "pop")],
        tex=CLEAN)
    add(198.28, kb(F(22501966425), "in", "archival"), [rich("CURVAS AMPLIAS · PUENTES DE CONCRETO · BARANDAS DECORADAS", ("amplias", "concreto", "decoradas"), 0.1, step=0.35,
                                                             y=0.9, size=50, maxw=0.92)], tex=ARCH)
    add(201.72, kb(F(174311636), "in", "doc"), [big("MIRADORES PARA QUE PARARAS EL AUTO", 0.1, 0.86, 62)], tex=CLEAN)
    add(204.74, kb(F(48594823382), "in", "doc"), [big("NO SE TRATABA DE LLEGAR RÁPIDO", 0.1, 0.12, 62), big("SINO DE DISFRUTAR EL CAMINO", w("disfrutar", 207.2) - 204.74, 0.86, 70, YELLOW)],
        tex=CLEAN)
    add(208.5, cus(G16.rule5, t0=0.4, curve_t=w("curva", 213.0) - 208.5), [big("LA REGLA DE LANCASTER", 0.0, 0.94, 46, GREY_)], tr="fade", td=0.2, tex=GFX)
    add(214.84, L("21322", kb(U("OOdaVUis_3E"), "in", "doc"), "Turistas de Nueva York en la Columbia River Highway, 1916 · " + CAP_LOC),
        [big("QUE HASTA LOS AUTOS MÁS MODESTOS SUBIERAN SIN SUFRIR", 0.3, 0.92, 50, YELLOW)], tex=ARCH)
    add(219.52, cus(_card, lines=[("OTROS MILLONARIOS", 120, WHITE, 0.46, 0.0), ("SE SUMARON", 80, YELLOW, 0.6, 0.3)]), tr="fade", td=0.15, tex=GFX)
    add(221.12, WP("benson", cus(_card, lines=[("UN MADERERO", 60, GREY_, 0.36, 0.0), ("SIMON BENSON", 130, WHITE, 0.52, 0.2)]), "Simon Benson · Wikimedia Commons"),
        tr="fade", td=0.15, tex=ARCH)
    add(223.34, kb(F(14459425543), "in", "doc"), [big("PAGÓ DE SU BOLSILLO EL PUENTECITO DE PIEDRA", 0.1, 0.12, 56, YELLOW), big("QUE CRUZA MULTNOMAH FALLS POR LA MITAD",
                                                                                                                         w("todavía", 225.2) - 223.34, 0.86, 56)], tex=CLEAN)
    add(227.46, kb(U("QaqskcbpvCE"), "in", "doc"), [big("COMPRÓ LOS TERRENOS DE VARIAS CASCADAS", 0.1, 0.86, 60)], tex=CLEAN)
    add(232.04, kb(F(19414222526), "in", "doc"), [big("Y SE LOS REGALÓ AL ESTADO", 0.0, 0.86, 76, YELLOW), big("PARA QUE NADIE PUDIERA ESTROPEARLOS", 1.4, 0.12, 52)], tex=CLEAN)
    add(235.54, WP("vh_ded", kb(F(52104719742), "in", "archival"), "Inauguración de Vista House, 5 de mayo de 1918 · Wikimedia Commons"),
        [Badge("1918", 0.1, None), BigText("VISTA HOUSE", "serif", 110, WHITE, (0.5, 0.14), 0.3, None, "up")], tex=ARCH)
    add(238.64, kb(F(2253447605), "in", "doc"), [big("UN MIRADOR DE PIEDRA EN LO ALTO DE UN ACANTILADO", 0.1, 0.86, 56)], tex=CLEAN)
    add(241.3, kb(U("MQNWj9UeqKo"), "in", "doc"), [big("TODAVÍA HOY, UNA DE LAS POSTALES DE OREGÓN", 0.1, 0.86, 58, YELLOW)], tex=CLEAN)
    add(244.02, L("354569p", kb(F(192333031), "in", "doc"), "Viaducto de Crown Point · HAER · " + CAP_LOC),
        [big("PERO EL PRIMER TRAMO SE HABÍA ABIERTO ANTES", 0.2, 0.08, 54), big("1915", w("1915", 247.4) - 244.02, 0.88, 110, YELLOW, "pop")], tex=ARCH)
    t0 = 249.1
    add(t0, mp("cr_us", [(0, -118.0, 46.0, 1.5), (3.8, -121.5, 45.6, 2.4)],
               [dict(type="pin", at="cr_crown", t0=0.3, label="LA PRIMERA CARRETERA PAVIMENTADA DEL NOROESTE", side="r", box=True, size=34)]),
        tr="zoom", td=0.3, tex=GFX)
    add(253.1, kb(F(11794815443), "in", "archival"), [Badge("1916", 0.1, None), big("LA DEDICARON CON UN GRAN ACTO EN LO ALTO DE LOS ACANTILADOS", 0.3, 0.9, 50)],
        tex=ARCH)
    add(256.54, L("7a10264", cus(_card, lines=[("WOODROW WILSON", 120, WHITE, 0.5, 0.0)]), "Woodrow Wilson, 1916 · " + CAP_LOC),
        [big("SEGÚN LAS CRÓNICAS, DESDE WASHINGTON…", 0.1, 0.08, 52), LowerThird("WOODROW WILSON", "PRESIDENTE DE ESTADOS UNIDOS", w("presidente", 259.4) - 256.54)], tex=ARCH)
    t0 = w("pulsó", 260.4)
    add(t0, mp("cr_us", [(0, -98.0, 41.0, 0.62), (4.1, -100.0, 42.0, 0.66)],
               [dict(type="pin", at=(-77.03, 38.90), t0=0.0, label="UN BOTÓN EN WASHINGTON", side="l", box=True, size=34),
                dict(type="route", ll=WIRE, t0=0.5, draw=2.0, color=YELLOW, width=6, dash=18),
                dict(type="pin", at="cr_crown", t0=2.5, label="UNA BANDERA EN OREGÓN", side="r", box=True, size=34)]),
        tr="zoom", td=0.3, tex=GFX)
    t0 = 264.12
    add(t0, mp("cr_gorge", [(0, -122.0, 45.6, 0.5), (5.6, -121.65, 45.68, 0.8)],
               [dict(type="route", ll=LINE, t0=0.0, draw=2.5, color=GOLD, width=6),
                dict(type="pin", at="cr_mitchell", t0=w("mitchell", 267.6) - t0, label="MITCHELL POINT", side="r", box=True, size=40)]),
        [big("LA JOYA DE LA CARRETERA", 0.2, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(269.88, kb(U("LrxPIk8_qQk"), "in", "dark"), [big("CUENTA UNA LEYENDA…", 0.1, 0.12, 60), big("UN TAL CAPITÁN MITCHELL", w("capitán", 271.8) - 269.88, 0.86, 70, YELLOW)],
        tex=DARK)
    add(273.28, kb(F(7155137155), "down", "dark"), [Darken(0.25), big("EN GUERRA CON LOS NATIVOS, SE HABRÍA LANZADO AL VACÍO", 0.1, 0.86, 52),
                                                   big("PARA QUE NO LO CAPTURARAN", 2.4, 0.12, 54, YELLOW)], tex=DARK)
    add(278.4, kb(U("ihiEd-_4TNY"), "in", "dark"), [big("LOS PERIÓDICOS DE LA ÉPOCA YA DUDABAN DE QUE FUERA VERDAD", 0.1, 0.86, 50)], tex=DARK)
    add(281.18, cus(_card, lines=[("PERO EL NOMBRE SE QUEDÓ", 70, WHITE, 0.4, 0.0), ("MITCHELL POINT", 140, YELLOW, 0.56, 0.3)]), tr="fade", td=0.15, tex=GFX)
    add(282.84, kb(F(31741899853), "up", "archival"), [big("HASTA ENTONCES, PARA PASARLA…", 0.1, 0.12, 58), big("UNA CUESTA TAN EMPINADA QUE SOLO CABÍA UN AUTO", 1.6, 0.9, 52, YELLOW)],
        tex=ARCH)
    add(286.34, cus(G16.flagmen, t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(292.68, L("3a47468", kb(U("Yoqi404MJ8M"), "in", "doc"), "Auto en una carretera de Oregón, 1921 · " + CAP_LOC),
        [big("UN VECINO SOLO VIO A UN AUTO INTENTARLO POR SU CUENTA", 0.3, 0.92, 50)], tex=ARCH)
    add(297.68, cus(G16.flagmen, t0=-9, horses_t=0.1), tr="fade", td=0.15, tex=GFX)
    add(300.14, cus(_card, lines=[("LANCASTER Y EL INGENIERO", 60, GREY_, 0.34, 0.0), ("JOHN ELLIOTT", 120, WHITE, 0.5, 0.2),
                                  ("DECIDIERON ATRAVESAR LA ROCA", 70, YELLOW, 0.66, w("atravesar", 302.4) - 300.14)]), tr="fade", td=0.15, tex=GFX)
    add(303.72, L("1b13125", kb(F(7655741578), "in", "archival"), "La Axenstrasse, Suiza, hacia 1900 · " + CAP_LOC), [big("COMO EN SUIZA", 0.1, 0.9, 80, YELLOW)],
        tex=ARCH)
    add(305.52, cus(G16.windows, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(312.32, kb(F(31741900193), "in", "archival"), [big("CADA VENTANA: UNOS 20 PIES DE ALTO (6 M)", 0.1, 0.9, 56, YELLOW)], tex=ARCH)
    add(314.98, kb(F(31741899653), "in", "archival"), [big("EL COLUMBIA, ENMARCADO COMO EN UN CUADRO", 0.2, 0.9, 58)], tex=ARCH)
    add(318.78, cus(G16.windows, t0=-9, car_t=0.6, title="12 DE AGOSTO DE 1915"), [big("EL PRIMER AUTO CRUZA EL TÚNEL", 0.3, 0.94, 50, YELLOW)], tr="fade", td=0.2,
        tex=GFX)
    add(323.28, cus(_card, lines=[("LO MANEJABA", 56, GREY_, 0.32, 0.0), ("H. W. MITCHELL", 120, WHITE, 0.46, 0.2),
                                  ("PRESIDENTE DE LOS AUTOS MITCHELL", 64, YELLOW, 0.62, w("presidente", 326.0) - 323.28),
                                  ]), tr="fade", td=0.15, tex=GFX)
    add(328.28, kb(F(51840815448), "in", "archival"), [big("LA MARCA, CASUALMENTE, TAMBIÉN SE LLAMABA MITCHELL", 0.1, 0.9, 52, YELLOW)], tex=ARCH)
    add(330.9, fr(F(32431368091), None),
        [rich("«SIEMPRE CREÍ QUE LA CARRETERA SUIZA NO SE PODÍA SUPERAR»", ("suiza",), 0.2, step=0.12, y=0.86, size=52, maxw=0.86)], tex=ARCH)
    add(336.66, kb(F(52105794591), "punch", "archival"), [big("HASTA QUE VIO AQUELLO", 0.0, 0.88, 84, YELLOW, "pop")], tex=ARCH)
    add(338.16, Split([kb(F(23057702844), "in", "archival"), kb(F(51841052374), "in", "archival"), kb(F(23659775706), "in", "archival")]),
        [big("LA FOTO QUE TODO EL MUNDO QUERÍA TENER", 0.3, 0.9, 58, YELLOW)], tex=ARCH)
    t0 = 342.52
    add(t0, mp("cr_east", [(0, -121.6, 45.70, 0.5), (4.2, -121.45, 45.69, 0.62)],
               [dict(type="route", ll=LINE, t0=0.0, draw=0.1, color=GOLD, width=6),
                dict(type="pin", at="cr_mitchell", t0=0.0, label="MITCHELL POINT", side="l", box=True, size=34),
                dict(type="pin", at="cr_twin", t0=1.4, label="EL TÚNEL DE NUESTRA HISTORIA", side="r", box=True, size=36, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)

    # ============================== CAP 3: ATRAPADOS EN LOS TÚNELES GEMELOS (346.7 - 523.1)
    bg, ov = chapter(3, "ATRAPADOS EN LOS TÚNELES GEMELOS", F(33194005485), g="archival", year="1921")
    add(346.74, bg, ov, tr="black", td=0.2, tex=DARK)
    t0 = 349.3
    add(t0, mp("cr_east", [(0, -121.43, 45.69, 0.62), (2.0, -121.42, 45.688, 0.78)],
               [dict(type="route", ll=LINE, t0=0.0, draw=0.1, color=GOLD, width=6),
                dict(type="pin", at="cr_mosier", t0=0.0, label="MOSIER", side="r", box=True, size=38),
                dict(type="label", at=(-121.43, 45.705), text="OTRO SALIENTE DE ROCA", t0=0.5, size=38, box=True)]), tr="zoom", td=0.3, tex=GFX)
    add(351.3, kb(F(33037107592), "in", "archival"), [Badge("HACIA 1921", 0.1, None), big("DOS TÚNELES SEGUIDOS, DINAMITADOS EN EL BASALTO", 0.3, 0.9, 54)], tex=ARCH)
    add(357.1, kb(F(32348982144), "in", "archival"), [Darken(0.3), BigText("LOS TÚNELES GEMELOS", "serif", 100, WHITE, (0.5, 0.44), 0.1, None, "up"),
                                                     big("MOSIER TWIN TUNNELS", 0.6, 0.58, 54, YELLOW)], tex=ARCH)
    add(359.16, kb(F(33037103702), "in", "archival"), [big("TAMBIÉN TENÍAN VENTANAS HACIA EL RÍO", 0.1, 0.9, 58)], tex=ARCH)
    add(w("como agujeros", 362.8), kb(F(10488714063), "in", "doc"), [big("COMO AGUJEROS EN LA PARED DE UN CASTILLO", 0.0, 0.86, 60, YELLOW)], tex=CLEAN)
    add(365.24, kb(U("w-0Gb3AfxKw"), "in", "dark"), [SNOWY, Badge("19 DE NOVIEMBRE DE 1921", 0.1, None)], tex=NIGHT)
    add(367.66, kb(F(27949835269), "in", "cold"), [SNOWY2, big("UNA TORMENTA DE NIEVE CAYÓ SOBRE LA GARGANTA", 0.1, 0.86, 56)], tex=CLEAN)
    add(370.8, L("3b16110", kb(U("bMOCBS1psL8"), "in", "cold"), "Auto atascado en la nieve, 1908 · Bain News Service · " + CAP_LOC),
        [SNOWY, big("VARIOS AUTOS QUEDARON ATRAPADOS", 0.2, 0.92, 58, YELLOW)], tex=ARCH)
    add(374.68, L("84459", kb(U("CRe2E9eNQr4"), "in", "cold"), "Paso abierto en la nieve, Snoqualmie (Washington), 1920 · " + CAP_LOC),
        [big("NI SEGUIR NI VOLVER", 0.4, 0.92, 70, YELLOW)], tex=ARCH)
    add(378.8, cus(G16.funnel, t0=0.2), [big("EN ESA GARGANTA, EL VIENTO DEL ESTE BAJA HELADO", 0.1, 0.1, 50)], tr="fade", td=0.2, tex=GFX)
    add(385.08, kb(U("mig3zZLvtUQ"), "in", "dark"), [SNOWY2, big("LA CARRETERA MÁS BONITA DEL PAÍS…", 0.1, 0.12, 60),
                                                    big("…SE CONVIRTIÓ EN UNA TRAMPA", w("trampa", 388.6) - 385.08 - 0.4, 0.86, 76, RED_, "pop")], tex=NIGHT)
    add(389.76, cus(_card, lines=[("PONTE EN SU LUGAR", 120, YELLOW, 0.5, 0.0)]), tr="fade", td=0.15, tex=GFX)
    add(391.14, kb(U("AoBNEMvYrk4"), "in", "cold"), [SNOWY2, big("FUERA: LA NIEVE TAPANDO LA CARRETERA", 0.1, 0.86, 60)], tex=CLEAN)
    add(393.78, kb(F(10488710113), "in", "dark"), [big("DENTRO: LA OSCURIDAD DEL BASALTO", 0.1, 0.86, 62)], tex=DARK)
    add(395.72, kb(F(10488717753), "in", "dark"), [big("EL RUIDO DEL VIENTO ENTRANDO POR LAS VENTANAS", 0.1, 0.86, 54)], tex=DARK)
    add(398.02, kb(U("uEvHiiIDGWQ"), "down", "cold"), [big("Y, MUY ABAJO, EL RÍO", 0.1, 0.86, 70, YELLOW)], tex=CLEAN)
    add(401.0, cus(_card, lines=[("UNO DE LOS ATRAPADOS", 60, GREY_, 0.36, 0.0), ("CHARLES SADILEK", 130, WHITE, 0.52, 0.2)]), tr="fade", td=0.15, tex=GFX)
    add(403.66, kb(U("yxbjmHnAFDI"), "in", "doc"), [big("VENÍA DE CAZAR", 0.0, 0.12, 64), big("CON EL AUTO LLENO DE GANSOS", w("lleno", 405.0) - 403.66, 0.86, 70, YELLOW)],
        tex=CLEAN)
    add(406.16, kb(U("Ff4BbI31Czg"), "in", "doc"), [big("Y GANAS DE LLEGAR A CASA, EN PORTLAND", 0.1, 0.86, 62)], tex=CLEAN)
    add(408.54, cus(_card, lines=[("CON ÉL, OTRO VIAJERO", 60, GREY_, 0.36, 0.0), ("E. B. MARVIN", 140, WHITE, 0.52, w("marvin", 410.4) - 408.54)]), tr="fade", td=0.15,
        tex=GFX)
    add(411.34, L("3c13360", kb(U("3vpP08JSRVU"), "in", "cold"), "Autos atrapados por la nieve, Nueva York, 1917 · Bain News Service · " + CAP_LOC),
        [big("LOS DEMÁS DEJARON SUS AUTOS", 0.2, 0.92, 60)], tex=ARCH)
    t0 = w("y bajaron", 413.2)
    add(t0, mp("cr_east", [(0, -121.41, 45.69, 0.8), (3.8, -121.41, 45.688, 0.9)],
               [dict(type="pin", at="cr_twin", t0=0.0, label="LOS TÚNELES", side="l", box=True, size=36),
                dict(type="route", ll=[CRD["wp"]["twin"], CRD["wp"]["mosier"]], t0=0.3, draw=1.6, color=WHITE, width=5, dash=14),
                dict(type="pin", at="cr_mosier", t0=1.6, label="MOSIER: UNA CAMA CALIENTE", side="r", box=True, size=36)]),
        [big("BAJARON CAMINANDO HASTA MOSIER", 0.2, 0.1, 58)], tr="zoom", td=0.3, tex=GFX)
    add(417.2, cus(_card, lines=[("SADILEK Y MARVIN…", 90, WHITE, 0.42, 0.0), ("NO", 220, YELLOW, 0.6, 0.6)]), tr="fade", td=0.15, tex=GFX)
    add(419.08, kb(F(32811368040), "in", "archival"), [big("SE METIERON EN EL TÚNEL…", 0.1, 0.12, 64), big("…Y SE QUEDARON", 1.2, 0.86, 80, YELLOW, "pop")], tex=ARCH)
    add(421.48, kb(F(33037103702), "punch", "archival"), [big("DESDE DENTRO, POR LAS VENTANAS ABIERTAS EN LA ROCA…", 0.1, 0.88, 54)], tex=ARCH)
    add(424.34, kb(F(53473592977), "in", "cold"), [SNOWY2, big("…VEÍAN LA TORMENTA CAER SOBRE EL RÍO", 0.1, 0.12, 56),
                                                  big("SIN QUE LES TOCARA UN COPO", w("sin que", 426.7) - 424.34, 0.86, 66, YELLOW)], tex=CLEAN)
    add(428.46, L("09541", kb(U("IcPnSFJ2lbg"), "in", "doc"), "Auto de acampada, 1910 · Bain News Service · " + CAP_LOC),
        [big("SACARON EL EQUIPO DE ACAMPADA", 0.2, 0.92, 60)], tex=ARCH)
    add(430.78, kb(U("wBcjVM4zAZc"), "in", "doc"), [big("ENCENDIERON LOS HORNILLOS…", 0.0, 0.86, 64)], tex=CLEAN)
    add(431.76, V("2771", U("jMbpZh6QrK4"), 0.0, "doc"), [big("…Y A COCINAR LOS GANSOS", 0.2, 0.86, 70, YELLOW)], tex=CLEAN)
    add(434.26, kb(U("uO418iKele8"), "punch", "doc"), [big("MANZANAS ASADAS", 0.0, 0.86, 80, YELLOW, "pop")], tex=CLEAN)
    add(435.92, kb(U("BiDH-0Cdgfc"), "in", "doc"), [big("LOS QUE SE FUERON LES DEJARON MANTAS Y ALGO DE COMIDA", 0.1, 0.86, 50)], tex=CLEAN)
    add(438.9, kb(U("LBPU8K7loz8"), "in", "dark"), [big("ALGUNOS VECINOS SUBÍAN A VISITARLOS", 0.1, 0.86, 58)], tex=DARK)
    add(440.56, kb(U("FJS2CCXzIdc"), "in", "dark"), [big("UNA NOCHE, UNA BOTELLA DE WHISKY PARA COMPARTIR", 0.2, 0.86, 54, YELLOW)], tex=DARK)
    add(443.76, cus(_card, lines=[("LOS DOS HOMBRES", 70, WHITE, 0.4, 0.0), ("SE LA GUARDARON", 130, YELLOW, 0.56, 0.3)]), tr="fade", td=0.15, tex=GFX)
    add(445.3, kb(U("B5PGhF55FgU"), "in", "dark"), [big("LAS NOCHES ERAN LO PEOR", 0.0, 0.86, 72, YELLOW)], tex=NIGHT)
    add(446.74, kb(U("9lEGCbgAQSQ"), "in", "cold"), [SNOWY2, big("EL VIENTO HELADO ENTRABA POR LAS VENTANAS DE PIEDRA", 0.1, 0.86, 52)], tex=NIGHT)
    add(448.96, V("22730", U("3HFuk5INTW4"), 0.0, "doc"), [big("EL ÚNICO CALOR: EL DE LOS HORNILLOS", 0.2, 0.86, 62)], tex=NIGHT)
    add(451.54, kb(U("sSe-MwPfiJE"), "in", "doc"), [big("DORMÍAN ENVUELTOS EN MANTAS", 0.1, 0.86, 64)], tex=CLEAN)
    add(453.22, kb(U("VxgyYFdQsu0"), "in", "cold"), [SNOWY, big("OYENDO CRUJIR LA NIEVE… Y EL RÍO, MUY ABAJO", 0.1, 0.86, 56)], tex=NIGHT)
    add(456.96, kb(U("mtmx7Ze0JU4"), "in", "cold"), [big("CUALQUIERA HABRÍA BAJADO AL PUEBLO A LA PRIMERA", 0.1, 0.86, 54)], tex=CLEAN)
    add(460.06, cus(_card, lines=[("ELLOS SE QUEDARON", 120, YELLOW, 0.5, 0.0)]), tr="fade", td=0.15, tex=GFX)
    add(461.44, kb(F(10488711553), "in", "dark"), [Darken(0.55), Badge("RESPUESTA 1", 0.1, None)] +
                                                 question("¿Por qué se quedaron nueve días viviendo en un túnel?", ("nueve", "túnel?"), size=70), tr="glitch", td=0.25, tex=DARK)
    add(467.86, cus(_card, lines=[("PORQUE NO PODÍAN", 80, WHITE, 0.4, 0.0), ("PAGAR EL MOTEL", 150, YELLOW, 0.56, 0.3)]), tr="fade", td=0.15, tex=GFX)
    add(469.78, cus(G16.prices, t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(474.12, kb(U("7mvyz93pdms"), "in", "cold"), [SNOWY, big("EN CUANTO VIERON A TANTA GENTE ATRAPADA", 0.1, 0.86, 56)], tex=NIGHT)
    add(477.44, kb(U("N561DZ3NfVM"), "in", "doc"), [rich("EL TÚNEL · EL FRÍO · SU PROPIA COMIDA", ("túnel", "frío", "comida"), 0.1, step=0.45, y=0.14, size=60),
                                                   big("ANTES QUE DEJARSE SACAR EL DINERO", w("a dejarse", 480.8) - 477.44, 0.86, 64, YELLOW)], tex=CLEAN)
    add(482.36, L("8a12901", kb(F(47052031782), "in", "cold"), "Autos entre la nieve, Ohio, 1940 · FSA/OWI · " + CAP_LOC),
        [Badge("NUEVE DÍAS DESPUÉS", 0.1, None), big("EL ESTADO ABRIÓ UN PASO DESDE MOSIER", 0.4, 0.86, 60)], tex=ARCH)
    add(486.48, L("14017", kb(F(47052031782), "in", "cold"), "El río Columbia y la carretera cerca de Eagle Creek, 1923 · " + CAP_LOC),
        [big("LA CARRETERA, CERRADA HASTA LA PRIMAVERA", 0.2, 0.92, 56)], tex=ARCH)
    add(488.6, kb(U("1zQCeFIjmZs"), "in", "cold"), [big("SADILEK MANDÓ SU AUTO A PORTLAND…", 0.1, 0.12, 60), big("…EN BARCAZA", w("barcaza", 490.6) - 488.6, 0.86, 90, YELLOW, "pop")],
        tex=CLEAN)
    add(491.84, kb(F(10488540114), "in", "doc"), [big("PERO ANTES DE IRSE, HICIERON ALGO MÁS", 0.1, 0.86, 62)], tex=CLEAN)
    add(494.86, kb(U("Ru_tWerljsY"), "in", "dark"), [big("CON UNA HERRAMIENTA, GRABARON EN LA ROCA", 0.1, 0.86, 60)], tex=DARK)
    add(497.9, cus(G16.carving, t0=0.2, names_t=w("debajo", 502.2) - 497.9), tr="fade", td=0.2, tex=GFX)
    add(505.28, kb(F(10488711553), "in", "dark", z=1.1), [Darken(0.55), FnOverlay(G2.subscribe), big("¿TE TIENE ATRAPADO COMO A ELLOS?", 0.2, 0.12, 60, YELLOW),
                                                         big("AQUÍ NO TE VAMOS A COBRAR DE MÁS: ES GRATIS", w("aquí no", 508.8) - 505.28, 0.24, 50, WHITE)], tex=DARK)
    add(511.18, kb(F(33037103702), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("EN LA TELE, EL BOTÓN ESTÁ JUSTO DEBAJO DEL VÍDEO", 0.1, 0.12, 54, YELLOW)],
        tex=DARK)
    add(514.5, kb(F(33194005485), "in", "archival"), [big("LO QUE NO PODÍAN IMAGINAR…", 0.1, 0.12, 60),
                                                     big("30 AÑOS DESPUÉS", w("30 años", 517.6) - 514.5, 0.86, 80, YELLOW)], tex=ARCH)
    add(519.02, cus(G16.fill, t0=0.2, title="SU FIRMA, BAJO TONELADAS DE ROCA"), tr="fade", td=0.2, tex=GFX)

    # ============================== CAP 4: DEMASIADOS AUTOS (523.1 - 628.4)
    bg, ov = chapter(4, "DEMASIADOS AUTOS", U("V7XJ_4P1WU4"), g="doc", year="1926–1953")
    add(523.08, bg, ov, tr="black", td=0.2, tex=DARK)
    add(525.6, L("24525", kb(U("5d2QJl88QbI"), "in", "doc"), "Campamento de turistas en auto, 1923 · National Photo Company · " + CAP_LOC),
        [big("LOS AUTOS", w("los autos", 526.7) - 525.6, 0.12, 90, YELLOW, "pop"), big("MUCHÍSIMOS AUTOS", w("muchísimos", 527.9) - 525.6, 0.88, 80, WHITE, "pop")], tex=ARCH)
    add(529.16, L("354591p", kb(F(48609040451), "in", "doc"), "Puente de Horsetail Falls · HAER · " + CAP_LOC),
        [big("HECHA PARA IR SIN PRISA", 0.2, 0.92, 70)], tex=ARCH)
    add(532.44, L("3b13596", kb(U("JbUOPQlKZ-Y"), "in", "doc"), "Campamento público de autos, 1923 · " + CAP_LOC),
        [Badge("AÑOS 20", 0.1, None), big("EL PAÍS ENTERO SE SUBIÓ A CUATRO RUEDAS", 0.4, 0.92, 56, YELLOW)], tex=ARCH)
    add(536.24, cus(_card, lines=[("AUTOS EN OREGÓN", 54, GREY_, 0.3, 0.0), ("1915", 120, WHITE, 0.46, 0.2), ("UNAS DECENAS DE MILES", 90, WHITE, 0.62, 1.4)]),
        tr="fade", td=0.15, tex=GFX)
    add(541.1, cus(_card, lines=[("DIEZ AÑOS DESPUÉS", 60, GREY_, 0.3, 0.0)]),
        [Counter(0, 200000, "{:,.0f}", "AUTOS", 0.2, 1.2, (0.5, 0.56), 190, prefix="≈ ")], tr="fade", td=0.15, tex=GFX)
    add(543.84, kb(U("pDVWlGJzM8Y"), "in", "dark"), [big("Y CASI TODOS QUERÍAN PASAR POR EL MISMO SITIO", 0.1, 0.86, 54)], tex=DARK)
    t0 = 546.62
    add(t0, mp("cr_us", [(0, -98.0, 41.5, 0.62), (4.6, -98.0, 41.5, 0.66)],
               [dict(type="route", ll=US30, t0=0.6, draw=3.0, color=YELLOW, width=7),
                dict(type="label", at=(-98.0, 44.4), text="US 30 · DE COSTA A COSTA", t0=w("us-30", 550.0) - t0, size=48, box=True)]),
        [Badge("1926", 0.1, None)], tr="zoom", td=0.3, tex=GFX)
    add(552.24, kb(F(36433779033), "in", "doc"), [big("UNA DE LAS NUEVAS CARRETERAS NUMERADAS QUE CRUZABAN EL PAÍS", 0.1, 0.86, 50)], tex=CLEAN)
    add(555.48, V("52430", U("P0bVatS8Jdw"), 0.0, "doc"), [big("POR AQUEL CAMINO DE MIRADORES…", 0.1, 0.12, 58), big("CAMIONES DE CARGA", w("camiones", 557.7) - 555.48, 0.86, 80, YELLOW)],
        tex=CLEAN)
    add(559.5, V("44284", U("h-kD4142VIQ"), 0.0, "doc"), [big("AUTOBUSES Y FAMILIAS CON PRISA POR LLEGAR A LA COSTA", 0.1, 0.86, 52)], tex=CLEAN)
    add(563.02, cus(G16.squeeze, t0=0.2, truck_t=w("más grande", 564.6) - 563.02), tr="fade", td=0.2, tex=GFX)
    add(567.86, kb(F(33037104002), "in", "archival"), [big("LOS TÚNELES SE QUEDARON ESTRECHOS", 0.0, 0.88, 66, YELLOW)], tex=ARCH)
    add(569.52, cus(_card, lines=[("1915: UNA MARAVILLA", 100, GREEN_, 0.4, 0.0), ("1930: UN CUELLO DE BOTELLA", 100, RED_, 0.58, w("en 1930", 572.8) - 569.52)]),
        tr="fade", td=0.15, tex=GFX)
    add(576.02, cus(G16.squeeze, t0=-9, truck_t=-1), [big("PARARSE · ESPERAR · PASAR UNO A UNO", 0.1, 0.94, 50)], tr="fade", td=0.2, tex=GFX)
    add(582.46, kb(F(22476093746), "up", "archival"), [big("EN MITCHELL POINT, LOS CAMIONES GRANDES APENAS PASABAN", 0.1, 0.9, 50)], tex=ARCH)
    add(585.88, L("191913p", kb(F(33037107592), "in", "archival"), "Túneles gemelos de Mosier · HAER · " + CAP_LOC),
        [big("EN LOS GEMELOS HUBO QUE AGRANDAR LA ROCA", 0.2, 0.08, 54),
         big("LAS ENTRADAS DE PIEDRA LABRADA DESAPARECIERON", w("las entradas", 588.6) - 585.88, 0.92, 52, YELLOW)], tex=ARCH)
    add(592.44, kb(F(10488519675), "in", "doc"), [big("CURVAS DIBUJADAS PARA DISFRUTAR…", 0.1, 0.12, 60), big("…CURVAS PARA FRENAR", w("para frenar", 595.6) - 592.44, 0.86, 80, RED_, "pop")],
        tex=CLEAN)
    add(597.72, kb(U("5d8S0VTGvDo"), "in", "doc"), [big("LOS INGENIEROS YA PENSABAN EN OTRA COSA", 0.1, 0.86, 60)], tex=CLEAN)
    add(601.52, cus(G16.hang, t0=-9, road_t=-9, i84_t=w("carretera nueva", 603.8) - 601.52, title="ABAJO, A LA ORILLA DEL RÍO"), tr="fade", td=0.2, tex=GFX)
    add(605.8, kb(U("2WwIzHPOwOA"), "in", "doc"), [rich("MÁS ANCHA · MÁS RECTA · AL NIVEL DEL AGUA", ("ancha", "recta", "agua"), 0.0, step=0.45, y=0.86, size=60)], tex=CLEAN)
    add(609.02, cus(_card, lines=[("SIN MIRADORES", 90, WHITE, 0.34, 0.0), ("SIN VENTANAS", 90, WHITE, 0.48, 0.5), ("SIN POESÍA", 110, YELLOW, 0.64, 1.1)]),
        tr="fade", td=0.15, tex=GFX)
    add(612.54, V("611", U("Vu652ykZ0Xw"), 0.0, "doc"), [big("SOLO VELOCIDAD", 0.0, 0.86, 90, YELLOW, "pop")], tex=CLEAN)
    t0 = 613.8
    add(t0, mp("cr_gorge", [(0, -121.9, 45.62, 0.5), (8.2, -121.55, 45.62, 0.56)],
               [dict(type="route", ll=LINE, t0=0.0, draw=0.1, color=(150, 130, 90), width=4),
                *[dict(type="route", ll=ln, t0=0.4, draw=2.5, color=WHITE, width=5) for ln in I84],
                dict(type="pin", at="cr_dalles", t0=w("the dalles", 619.0) - t0, label="THE DALLES", side="l", box=True, size=38)]),
        [Badge("AÑOS 30 → 1953", 0.1, None), big("LA CARRETERA DE LA ORILLA", 0.3, 0.1, 54)], tr="zoom", td=0.3, tex=GFX)
    add(620.52, kb(F(36849923940), "in", "doc"), [big("AL FINAL DE LA GARGANTA", 0.0, 0.86, 64)], tex=CLEAN)
    add(622.0, kb(F(2817449671), "in", "doc"), [big("ERA FEA…", 0.0, 0.12, 80), big("…PERO FUNCIONABA", 0.9, 0.86, 80, YELLOW, "pop")], tex=CLEAN)
    add(624.06, kb(F(10488538355), "down", "doc"), [big("Y LA DE ARRIBA EMPEZÓ A SOBRAR", w("la de arriba", 626.2) - 624.06, 0.88, 66, YELLOW)], tex=CLEAN)

    # ============================== CAP 5: EL ENTIERRO DE LOS TÚNELES (628.4 - 740.9)
    bg, ov = chapter(5, "EL ENTIERRO DE LOS TÚNELES", U("CgUQnwOnJBI"), g="dark", year="1948–1966")
    add(628.44, bg, ov, tr="black", td=0.2, tex=DARK)
    add(631.36, L("354590p", kb(F(3429860882), "in", "doc"), "Túnel de Oneonta · HAER · " + CAP_LOC),
        [Badge("1948 · ONEONTA", 0.1, None), big("UN DESVÍO POR FUERA DE LA ROCA", w("abrieron", 635.8) - 631.36, 0.92, 58)], tex=ARCH)
    add(637.44, kb(F(52104717652), "in", "archival"), [Stamp("TAPADO CON ESCOMBROS", 0.3, RED_, (0.5, 0.5), -10, 90)], tex=ARCH)
    add(639.86, kb(F(51841052374), "in", "archival"), [Badge("1953", 0.1, None), Stamp("CERRADO", 0.6, RED_, (0.5, 0.5), -10, 130)], tex=ARCH)
    add(643.22, kb(U("P0bVatS8Jdw"), "in", "doc"), [big("YA NO PODÍA CON EL TRÁFICO NI CON EL TAMAÑO DE LOS VEHÍCULOS", 0.1, 0.86, 48)], tex=CLEAN)
    add(647.88, kb(F(14204853748), "in", "doc"), [Badge("1954", 0.1, None), Flash(w("derrumbe", 649.6) - 647.88, 0.2),
                                                 big("UN DERRUMBE TAPÓ LA BOCA OESTE DE LOS GEMELOS", 1.4, 0.86, 54, YELLOW)], post=postshake(4), tex=CLEAN)
    add(652.5, kb(U("4admqbSrJlQ"), "in", "dark"), [big("LAS ROCAS LLEVABAN AÑOS CAYENDO SOBRE LOS AUTOS", 0.1, 0.86, 54)], tex=DARK)
    add(654.9, kb(F(14354210924), "punch", "doc"), [big("QUE PASABAN BAJO EL ACANTILADO", 0.0, 0.86, 64)], tex=CLEAN)
    add(656.68, cus(_card, lines=[("EL ESTADO DESVIÓ EL TRÁFICO…", 70, WHITE, 0.4, 0.0), ("…Y DECIDIÓ PARA SIEMPRE", 110, YELLOW, 0.56, w("y tomó", 658.7) - 656.68)]),
        tr="fade", td=0.15, tex=GFX)
    add(660.92, cus(G16.fill, t0=0.1, title="LLENÓ LOS DOS TÚNELES DE ROCA, DE PUNTA A PUNTA"), tr="fade", td=0.2, tex=GFX)
    add(664.24, cus(_card, lines=[("UN INGENIERO LO RESUMIRÍA AÑOS DESPUÉS:", 50, GREY_, 0.32, 0.0), ("«SE CERRARON CON LA IDEA", 84, WHITE, 0.48, 1.6),
                                  ("DE QUE NUNCA SE IBAN A VOLVER A ABRIR»", 84, YELLOW, 0.62, 2.3)]), tr="fade", td=0.15, tex=GFX)
    add(670.0, cus(G16.carving, t0=-9), [Darken(0.75, 0.2, 1.4), big("DENTRO, A OSCURAS, QUEDARON LAS FIRMAS", 0.3, 0.86, 58, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(674.08, kb(F(52689188670), "in", "doc"), [Badge("1966", 0.1, None), big("EL GOLPE FINAL", 0.3, 0.86, 90, RED_, "pop")], tex=CLEAN)
    add(677.82, V("41361", U("Vu652ykZ0Xw"), 0.0, "doc"), [big("LA AUTOPISTA DE LA ORILLA SE HABÍA QUEDADO PEQUEÑA", 0.1, 0.12, 54),
                                                          big("UNA INTERESTATAL DE 4 CARRILES", w("interestatal", 682.6) - 677.82, 0.86, 70, YELLOW)], tex=CLEAN)
    add(684.52, cus(G16.hang, t0=-9, road_t=-9, i84_t=-9, cut_t=w("recortar", 685.9) - 684.52, title="PARA HACERLE SITIO"), tr="fade", td=0.2, tex=GFX)
    add(688.08, kb(F(31741900193), "punch", "archival"), [big("EL ESTADO VOLÓ EN PEDAZOS EL TÚNEL DE MITCHELL POINT", 0.1, 0.9, 50, YELLOW)], tex=ARCH)
    add(w("mitchell point", 689.9), V("51821", U("87DGZ7r2CTM"), 0.0, "doc"), [Flash(0.0, 0.25), Stamp("1966", 0.2, RED_, (0.5, 0.5), -10, 150)], post=postshake(7),
        tex=CLEAN)
    t0 = 691.48
    add(t0, mp("cr_gorge", [(0, -121.75, 45.65, 0.62), (3.9, -121.65, 45.68, 0.7)],
               [*[dict(type="route", ll=ln, t0=0.0, draw=1.6, color=WHITE, width=6) for ln in I84],
                dict(type="label", at=(-121.75, 45.62), text="INTERSTATE 84", t0=w("interstate", 693.4) - t0, size=50, box=True)]), tr="zoom", td=0.3, tex=GFX)
    add(695.4, cus(G16.windows, t0=-9), [big("LAS CINCO VENTANAS QUE ENAMORARON A MEDIO PAÍS…", 0.1, 0.06, 50, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(w("nube de polvo", 699.6) - 0.4, kb(U("87DGZ7r2CTM"), "punch", "doc"), [big("…EN UNA NUBE DE POLVO", 0.1, 0.86, 76, RED_, "pop")], post=postshake(4), tex=CLEAN)
    add(701.1, kb(F(52689188670), "r", "doc"), [big("DEL TÚNEL MÁS FOTOGRAFIADO DE OREGÓN NO QUEDÓ NI EL HUECO", 0.1, 0.86, 50)], tex=CLEAN)
    add(704.56, kb(F(7155137155), "in", "doc"), [big("SOLO UN TAJO EN EL ACANTILADO, JUNTO A LOS CARRILES", 0.1, 0.86, 56, YELLOW)], tex=CLEAN)
    add(707.92, V("52447", U("G6VNKqR8NvM"), 0.0, "doc"), [big("MUCHOS PASABAN POR DEBAJO CADA DÍA…", 0.1, 0.12, 58)], tex=CLEAN)
    add(709.98, kb(F(31741899653), "in", "archival"), [big("…SIN SABER QUE ALLÍ ARRIBA HUBO VENTANAS", 0.1, 0.86, 60, YELLOW)], tex=ARCH)
    add(714.6, cus(_card, lines=[("FÍJATE EN LA IRONÍA", 110, YELLOW, 0.5, 0.0)]), tr="fade", td=0.15, tex=GFX)
    add(716.06, Split([kb(F(11794815443), "in", "archival"), V("611", U("Vu652ykZ0Xw"), 2.0, "doc")], labels=("PARA ENSEÑAR EL PAISAJE", "PARA PASAR SIN MIRARLO")),
        [big("LA CARRETERA DE SAM HILL…", 0.2, 0.08, 52, YELLOW)], tex=CLEAN)
    add(719.36, kb(U("Vu652ykZ0Xw"), "in", "doc"), [big("…ACABÓ ENTERRADA PARA PASAR POR DELANTE DEL PAISAJE SIN MIRARLO", 0.1, 0.86, 48, YELLOW)], tex=CLEAN)
    add(724.22, L("51236", kb(U("Yoqi404MJ8M"), "in", "doc"), "La vieja carretera cerca de Troutdale · Carol M. Highsmith · " + CAP_LOC),
        [Badge("DURANTE 20 AÑOS", 0.1, None), big("NADIE PARECIÓ ECHARLA DE MENOS", 0.4, 0.92, 60)], tex=ARCH)
    add(727.62, L("51323", kb(F(49029278663), "in", "doc"), "La vieja carretera cerca de Corbett · Carol M. Highsmith · " + CAP_LOC),
        [big("ALGUNOS TRAMOS, CARRETERAS LOCALES", 0.2, 0.92, 60)], tex=ARCH)
    add(730.56, kb(U("AdTY2eti9m4"), "in", "doc"), [big("OTROS SE LOS COMIÓ EL BOSQUE", 0.0, 0.86, 70, YELLOW)], tex=CLEAN)
    add(732.44, L("51321", kb(U("xSm1ivIkV5k"), "in", "doc"), "Baranda de piedra cubierta de musgo · Carol M. Highsmith · " + CAP_LOC),
        [big("Y EN ALGUNOS SITIOS, UN SIMPLE CAMINO DE SERVICIO", 0.3, 0.92, 54)], tex=ARCH)
    add(737.62, kb(U("zROafZ6GOy4"), "in", "dark"), [big("HASTA QUE ALGUIEN SE DIO CUENTA DE LO QUE HABÍA PERDIDO", 0.1, 0.86, 52, YELLOW)], tex=DARK)

    # ============================== CAP 6: EL ARREPENTIMIENTO Y LAS FIRMAS (740.9 - 857.7)
    bg, ov = chapter(6, "EL ARREPENTIMIENTO Y LAS FIRMAS", U("kIuXeVYrNM4"), g="cold", year="1982–1994")
    add(740.88, bg, ov, tr="black", td=0.2, tex=DARK)
    add(742.58, kb(U("GFDJQra8yYo"), "in", "doc"), [Badge("1982 · CERCA DE HOOD RIVER", 0.1, None), big("EL ESTADO DERRIBÓ UN VIEJO PUENTE DE LA CARRETERA", 0.4, 0.86, 54)],
        tex=CLEAN)
    add(747.86, L("130537p", kb(F(48609040451), "in", "doc"), "Puente de Latourell Creek · HAER · " + CAP_LOC),
        [big("A MUCHOS LES DOLIÓ VER DESAPARECER OTRO PEDAZO DE HISTORIA", 0.2, 0.92, 50, YELLOW)], tex=ARCH)
    add(752.14, kb(U("rvVhr2LngP4"), "in", "doc"), [rich("ESTUDIOS · ASOCIACIONES · PAPELES", ("estudios", "asociaciones", "papeles"), 0.0, step=0.5, y=0.86, size=66)], tex=CLEAN)
    add(755.78, L("00001", kb(U("l68Z6eF2peA"), "in", "doc"), "Puentes de la Columbia River Highway · HAER · " + CAP_LOC),
        [rich("HISTORIADORES · VECINOS · INGENIEROS DEL ESTADO", ("historiadores", "vecinos", "ingenieros"), 0.1, step=0.4, y=0.92, size=46, maxw=0.95)], tex=ARCH)
    add(761.2, kb(U("xSm1ivIkV5k"), "in", "doc"), [big("MIDIENDO MUROS…", 0.0, 0.86, 70)], tex=CLEAN)
    add(762.02, L("130543p", kb(U("AdTY2eti9m4"), "in", "doc"), "Puente de Shepperd's Dell · HAER · " + CAP_LOC),
        [big("…FOTOGRAFIANDO PUENTES CUBIERTOS DE MUSGO", 0.1, 0.92, 56, YELLOW)], tex=ARCH)
    add(764.64, kb(F(12962218645), "in", "doc"), [Badge("1983", 0.1, None), big("REGISTRO NACIONAL DE LUGARES HISTÓRICOS", 0.4, 0.86, 60, YELLOW)], tex=CLEAN)
    t0 = 769.92
    add(t0, mp("cr_gorge", [(0, -121.75, 45.62, 0.48), (7.3, -121.75, 45.62, 0.52)],
               [dict(type="label", at=(-121.75, 45.76), text="ÁREA ESCÉNICA NACIONAL", t0=w("área", 773.9) - t0, size=52, box=True, color=GREEN_),
                dict(type="label", at=(-121.75, 45.50), text="TODA LA GARGANTA, PROTEGIDA", t0=w("toda la", 772.4) - t0, size=42, box=True)]),
        [Badge("1986 · EL CONGRESO", 0.1, None)], tr="zoom", td=0.3, tex=GFX)
    add(777.24, kb(U("Dz_WKOrSnwE"), "in", "doc"), [Badge("1987 · PARLAMENTO DE OREGÓN", 0.1, None), big("UN PLAN QUE MUCHOS TOMARON POR UNA LOCURA", 0.6, 0.86, 56, YELLOW)],
        tex=CLEAN)
    t0 = 782.88
    add(t0, mp("cr_gorge", [(0, -121.75, 45.62, 0.5), (5.3, -121.75, 45.62, 0.53)],
               [dict(type="route", ll=LINE, t0=0.2, draw=3.0, color=GOLD, width=6),
                dict(type="label", at=(-121.75, 45.50), text="RESTAURARLA ENTERA · MÁS DE 70 MILLAS", t0=w("70", 785.0) - t0, size=44, box=True)]),
        [big("TAL COMO ERA EN LOS AÑOS 20", w("tal como", 786.3) - t0, 0.92, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    t0 = 788.12
    add(t0, mp("cr_gorge", [(0, -121.75, 45.62, 0.53), (3.9, -121.75, 45.62, 0.55)],
               [dict(type="route", ll=LINE, t0=0.0, draw=0.1, color=(120, 110, 90), width=4),
                *[dict(type="route", ll=r, t0=0.3, draw=0.8, color=GOLD, width=10) for r in ROAD],
                dict(type="label", at=(-122.15, 45.66), text="LO QUE EXISTÍA: PARA LOS AUTOS", t0=0.4, size=40, box=True, color=GOLD)]), tex=GFX)
    t0 = 791.94
    add(t0, mp("cr_gorge", [(0, -121.75, 45.62, 0.55), (3.9, -121.75, 45.62, 0.57)],
               [dict(type="route", ll=LINE, t0=0.0, draw=0.1, color=(120, 110, 90), width=4),
                *[dict(type="route", ll=r, t0=0.0, draw=0.1, color=GOLD, width=10) for r in ROAD],
                *[dict(type="route", ll=r, t0=0.3, draw=1.0, color=GREEN_, width=10, dash=16) for r in UNDER],
                dict(type="label", at=(-121.45, 45.76), text="LO PERDIDO O ENTERRADO: SENDERO", t0=0.4, size=40, box=True, color=GREEN_)]), tex=GFX)
    add(795.8, kb(U("nGt71kRwUOw"), "in", "doc"), [big("PARA CAMINAR Y PARA IR EN BICI", 0.0, 0.86, 70, YELLOW)], tex=CLEAN)
    add(798.22, kb(F(33194005485), "in", "archival"), [big("EL PRIMER GRAN RETO: LOS TÚNELES GEMELOS", 0.1, 0.88, 58, YELLOW)], tex=ARCH)
    add(800.76, L("191913p", kb(F(33037104002), "in", "archival"), "Túneles gemelos de Mosier · HAER · " + CAP_LOC),
        [Badge("1994", 0.1, None), big("LOS CONTRATISTAS EMPIEZAN A SACAR LA ROCA", 0.4, 0.92, 56, YELLOW)], tex=ARCH)
    add(803.8, cus(G16.fill, t0=0.3, mode="dig"), tr="fade", td=0.2, tex=GFX)
    add(809.26, kb(U("Yns2AVqJgp4"), "in", "dark"), [big("40 AÑOS DE OSCURIDAD Y HUMEDAD", 0.1, 0.12, 62), big("LA ROCA DE ARRIBA, AGRIETADA", w("agrietada", 812.4) - 809.26, 0.86, 64, YELLOW)],
        tex=DARK)
    add(813.84, cus(_card, lines=[("CADA METRO", 120, WHITE, 0.42, 0.0), ("UN RIESGO", 140, RED_, 0.58, 0.4)]), tr="fade", td=0.15, tex=GFX)
    add(815.58, kb(U("wp81DxKUd1E"), "in", "doc"), [big("PIENSA EN ESOS HOMBRES, CON CASCOS Y LINTERNAS", 0.1, 0.86, 54)], tex=CLEAN)
    add(818.56, kb(F(51614553206), "in", "dark"), [big("SACANDO PIEDRA A PIEDRA LO QUE OTROS METIERON DÉCADAS ANTES", 0.1, 0.86, 48)], tex=DARK)
    add(822.16, kb(U("pRQk1Llu2so"), "in", "dark"), [big("SIN SABER QUÉ IBAN A ENCONTRAR DETRÁS", 0.1, 0.86, 60, YELLOW)], tex=NIGHT)
    add(825.02, cus(G16.fill, t0=-12, mode="dig", reveal_t=w("apareció", 827.4) - 825.02, title="Y ENTONCES, EN UNA DE LAS PAREDES…"), tr="fade", td=0.2, tex=GFX)
    add(828.72, cus(G16.carving, t0=0.1, names_t=w("dos nombres", 831.6) - 828.72),
        [rich("LETRAS TALLADAS A MANO · UNA FECHA · DOS NOMBRES", ("letras", "fecha", "nombres"), 0.1, step=0.45, y=0.08, size=44)], tr="fade", td=0.2, tex=GFX)
    add(832.8, cus(G16.carving, t0=-9), [Darken(0.35), big("LAS FIRMAS DE SADILEK Y MARVIN", 0.0, 0.14, 62), big("SEGUÍAN AHÍ", 0.8, 0.86, 110, YELLOW, "pop")], tex=GFX)
    add(835.84, cus(G16.fill, t0=-9, title="LA ROCA QUE LO ENTERRÓ…"), [big("…TAMBIÉN LAS HABÍA PROTEGIDO", w("también", 838.6) - 835.84, 0.94, 60, YELLOW)], tr="fade", td=0.2,
        tex=GFX)
    add(840.6, cus(_card, lines=[("DURANTE 40 AÑOS, NADIE LAS TOCÓ", 70, WHITE, 0.3, 0.0), ("NI LA LLUVIA", 90, BLUE_, 0.46, w("ni la lluvia", 843.5) - 840.6),
                                 ("NI EL VIENTO", 90, GREY_, 0.6, w("ni el viento", 844.3) - 840.6), ("NI LOS AUTOS", 90, YELLOW, 0.74, w("ni los autos", 845.1) - 840.6)]),
        tr="fade", td=0.15, tex=GFX)
    add(846.38, cus(_card, lines=[("LO RARO ES ESTO", 120, YELLOW, 0.5, 0.0)]), tr="fade", td=0.15, tex=GFX)
    add(847.66, kb(U("rkFIIE9PxH0"), "in", "doc"), [big("EL ESTADO QUISO BORRAR AQUEL TÚNEL DEL MAPA…", 0.1, 0.86, 56)], tex=CLEAN)
    add(w("y al hacerlo", 849.7), cus(G16.carving, t0=-9), [Darken(0.3), big("…Y GUARDÓ LO ÚNICO QUE NADIE HABÍA PLANEADO", 0.1, 0.1, 54, YELLOW)], tr="fade", td=0.15, tex=GFX)
    add(853.9, cus(_card, lines=[("LA FIRMA DE DOS TIPOS", 90, WHITE, 0.4, 0.0), ("QUE NO QUISIERON PAGAR UN MOTEL", 84, YELLOW, 0.56, 1.1)]), tr="fade", td=0.15, tex=GFX)

    # ============================== CAP 7: VOLVER A ABRIR (857.7 - 964.8)
    bg, ov = chapter(7, "VOLVER A ABRIR", F(10488540114), g="doc", year="2000–2025")
    add(857.68, bg, ov, tr="black", td=0.2, tex=DARK)
    add(859.76, cus(G16.fill, t0=0.3, mode="rebuilt", title="NO TOCARON LAS LETRAS"), tr="fade", td=0.2, tex=GFX)
    add(864.94, kb(F(10488533594), "in", "doc"), [Badge("JULIO DE 2000", 0.1, None), big("LOS TÚNELES GEMELOS VUELVEN A ABRIRSE", 0.4, 0.86, 60, YELLOW)], tex=CLEAN)
    add(868.52, kb(U("vE_qxEQggj0"), "in", "doc"), [big("ESTA VEZ, SOLO A PIE Y EN BICI", 0.1, 0.86, 70)], tex=CLEAN)
    add(871.1, cus(_card, lines=[("LA OBRA COSTÓ UNOS", 60, GREY_, 0.3, 0.0)]),
        [Counter(0, 11, "{:,.0f}", "MILLONES DE DÓLARES", 0.3, 1.2, (0.5, 0.56), 220, prefix="$")], tr="fade", td=0.15, tex=GFX)
    add(874.02, kb(F(10488544756), "in", "doc"), [big("PARA QUE NO SE REPITIERA LO DE 1954…", 0.1, 0.86, 60)], tex=CLEAN)
    add(877.32, kb(F(26340261222), "in", "doc"), [big("…UN TEJADO DE CONCRETO PEGADO AL ACANTILADO", 0.1, 0.86, 58, YELLOW)], tex=CLEAN)
    add(882.02, cus(G16.shelter, t0=0.2, drop_t=w("roca", 883.0) - 882.02), tr="fade", td=0.2, tex=GFX)
    add(888.3, kb(F(10488711553), "in", "doc"), [big("Y PARA QUE TODO PARECIERA DE 1921…", 0.1, 0.12, 60)], tex=CLEAN)
    add(891.78, kb(F(10488542456), "in", "doc"), [big("…MADERA DE CEDRO DE OTRO TÚNEL VIEJO DE OREGÓN", 0.1, 0.86, 56, YELLOW)], tex=CLEAN)
    add(896.36, cus(_card, lines=[("EN LA REAPERTURA", 60, GREY_, 0.38, 0.0), ("LA NIETA DE SADILEK", 120, WHITE, 0.54, 0.3)]), tr="fade", td=0.15, tex=GFX)
    add(899.32, cus(_card, lines=[("QUEDARSE EN EL TÚNEL", 70, WHITE, 0.38, 0.0), ("«DECÍA MUCHO DE LO INDEPENDIENTES QUE ERAN»", 66, YELLOW, 0.54, 0.6)]),
        tr="fade", td=0.15, tex=GFX)
    add(904.08, kb(F(10488714063), "in", "doc"), [big("LA GENTE SE PARABA DELANTE DE LA PARED", 0.1, 0.86, 60)], tex=CLEAN)
    add(906.24, cus(G16.carving, t0=-9), [Darken(0.3), big("DOS DESCONOCIDOS QUE, SIN QUERERLO…", 0.1, 0.1, 56),
                                          big("…SE HICIERON PARTE DE LA HISTORIA DE LA CARRETERA", w("parte de", 910.1) - 906.24, 0.9, 52, YELLOW)], tr="fade", td=0.15, tex=GFX)
    add(912.6, kb(F(3429860882), "in", "doc"), [Badge("DESPUÉS: ONEONTA", 0.1, None), big("2006–2009: FUERA LOS ESCOMBROS", w("le sacaron", 914.8) - 912.6, 0.86, 64, YELLOW)],
        tex=CLEAN)
    add(918.8, kb(F(38088823072), "in", "dark"), [Badge("SEPTIEMBRE DE 2017", 0.1, None), big("UN INCENDIO FORESTAL", 0.5, 0.86, 70, RED_)], tex=NIGHT)
    add(w("arrasó", 921.8) - 0.3, kb(F(38836548751), "in", "dark"), [big("ARRASÓ LA GARGANTA", 0.1, 0.86, 70)], tex=NIGHT)
    add(922.76, kb(F(36332415774), "in", "doc"), [big("Y QUEMÓ LA MADERA DEL TÚNEL", 0.0, 0.86, 66, YELLOW)], tex=CLEAN)
    add(924.42, kb(F(36979283196), "in", "doc"), [big("LO VOLVIERON A REPARAR", 0.0, 0.86, 66)], tex=CLEAN)
    add(925.68, kb(F(34402135150), "in", "doc"), [Badge("2021", 0.1, None), big("REABRIÓ POR SEGUNDA VEZ EN SU VIDA", 0.3, 0.86, 62, YELLOW)], tex=CLEAN)
    add(928.96, kb(F(27693265417), "in", "doc"), [big("QUEDABA EL MÁS DIFÍCIL", 0.0, 0.12, 70, YELLOW),
                                                 big("EN LOS OTROS BASTABA CON SACAR LO QUE HABÍA DENTRO", w("bastaba", 931.9) - 928.96, 0.86, 50)], tex=CLEAN)
    add(934.02, cus(_card, lines=[("CON MITCHELL POINT, NO", 90, WHITE, 0.34, 0.0), ("YA NO EXISTÍA", 120, RED_, 0.5, w("ya no existía", 936.2) - 934.02),
                                  ("NADA QUE DESENTERRAR", 80, YELLOW, 0.66, w("no había", 937.8) - 934.02)]), tr="fade", td=0.15, tex=GFX)
    add(939.5, kb(U("izRQ870yJO8"), "in", "doc"), [Badge("2018 · UN COMITÉ", 0.1, None), big("LO MEJOR ERA HACERLO OTRA VEZ", 0.6, 0.86, 70, YELLOW)], tex=CLEAN)
    add(944.1, kb(F(51554363793), "in", "doc"), [Badge("2021", 0.1, None), big("LAS OBRAS EMPIEZAN EN EL MISMO SALIENTE DE ROCA", 0.3, 0.86, 54)], tex=CLEAN)
    add(946.4, kb(F(52071469104), "in", "doc"), [big("UN TÚNEL NUEVO, CON SUS VENTANAS", 0.1, 0.86, 60)], tex=CLEAN)
    add(948.24, kb(F(54149324634), "in", "doc"), [Badge("NOVIEMBRE DE 2024", 0.1, None), big("LA GENTE ENTRA POR PRIMERA VEZ", 0.4, 0.86, 62, YELLOW)], tex=CLEAN)
    add(952.14, cus(G16.windows, t0=0.2, length="655 PIES · ≈ 200 M", sub="5 VENTANAS SOBRE EL RÍO", title="21 DE MARZO DE 2025 · ABRE AL PÚBLICO", new=True,
                    car_t=None), tr="fade", td=0.2, tex=GFX)
    add(958.76, kb(F(52411893685), "in", "doc"), [big("CINCO VENTANAS SOBRE EL RÍO", 0.1, 0.86, 66)], tex=CLEAN)
    add(962.34, kb(F(31741899653), "in", "archival"), [big("COMO EL DE 1915", 0.0, 0.86, 90, YELLOW, "pop")], tex=ARCH)

    # ============================== CAP 8: HOY (964.8 - 1076.8)
    bg, ov = chapter(8, "LO QUE QUEDA HOY", F(23269873053), g="doc", year="HOY")
    add(964.8, bg, ov, tr="black", td=0.2, tex=DARK)
    t0 = 968.58
    add(t0, mp("cr_gorge", [(0, -121.75, 45.62, 0.5), (5.3, -121.75, 45.62, 0.54)],
               [*[dict(type="route", ll=r, t0=0.0, draw=0.8, color=GREEN_, width=9, dash=16) for r in UNDER],
                *[dict(type="route", ll=r, t0=w("y el resto", 971.4) - t0, draw=0.8, color=GOLD, width=9) for r in ROAD],
                dict(type="label", at=(-121.45, 45.76), text="UNAS 20 MILLAS: A PIE Y EN BICI", t0=0.3, size=40, box=True, color=GREEN_),
                dict(type="label", at=(-122.15, 45.66), text="EL RESTO: CON LOS AUTOS", t0=w("y el resto", 971.4) - t0, size=40, box=True, color=GOLD)]),
        [big("HOY SE PUEDE RECORRER CASI ENTERA", 0.1, 0.92, 54)], tr="zoom", td=0.3, tex=GFX)
    t0 = 973.84
    add(t0, mp("cr_east", [(0, -121.58, 45.70, 0.62), (4.4, -121.57, 45.70, 0.7)],
               [dict(type="route", ll=GAP, t0=0.3, draw=1.4, color=RED_, width=10, dash=14),
                dict(type="pin", at="cr_hoodriver", t0=0.2, label="HOOD RIVER", side="r", box=True, size=36),
                dict(type="label", at=(-121.58, 45.725), text="EL ÚLTIMO TRAMO: SIN DINERO", t0=1.2, size=42, box=True, color=RED_)]), tr="zoom", td=0.3, tex=GFX)
    add(978.26, cus(_card, lines=[("LO CALCULAN EN UNOS", 60, GREY_, 0.3, 0.0)]),
        [Counter(0, 50, "{:,.0f}", "MILLONES DE DÓLARES", 0.2, 1.0, (0.5, 0.56), 220, prefix="$")], tr="fade", td=0.15, tex=GFX)
    add(980.52, kb(F(2817449887), "in", "doc"), [big("Y HABRÁ QUE PASAR POR DEBAJO DE LA AUTOPISTA…", 0.1, 0.12, 54),
                                                big("…QUE UN DÍA SE COMIÓ LA CARRETERA VIEJA", w("que un día", 984.0) - 980.52, 0.86, 58, YELLOW)], tex=CLEAN)
    add(986.56, kb(F(23528784599), "in", "doc"), [big("SI CAMINAS POR LOS TÚNELES GEMELOS…", 0.1, 0.86, 60)], tex=CLEAN)
    add(988.88, cus(G16.carving, t0=-9), [big("…TODAVÍA PUEDES LEER LAS LETRAS", 0.0, 0.1, 60, YELLOW)], tr="fade", td=0.15, tex=GFX)
    add(990.98, kb(F(10488717753), "in", "doc"), [big("PROTEGIDAS, JUSTO DONDE LAS DEJARON", 0.1, 0.86, 62)], tex=CLEAN)
    add(994.7, kb(U("dsIyg_6406g"), "in", "doc"), [big("MUCHA GENTE PASA DE LARGO SIN VERLAS", 0.1, 0.86, 60)], tex=CLEAN)
    add(996.86, kb(U("sKEXhW0tghI"), "in", "doc"), [big("LOS QUE SE PARAN SE QUEDAN UN RATO, HACIENDO CUENTAS", 0.1, 0.86, 52, YELLOW)], tex=CLEAN)
    add(1000.28, cus(_card, lines=[("NUEVE DÍAS", 170, YELLOW, 0.5, 0.0)]), tr="fade", td=0.1, tex=GFX)
    add(1001.58, kb(U("CAiHfuGhRSU"), "punch", "doc"), [big("GANSOS", 0.0, 0.86, 100, YELLOW, "pop")], tex=CLEAN)
    add(1002.32, kb(U("BSWthxJFJqs"), "punch", "doc"), [big("MANZANAS", 0.0, 0.86, 100, YELLOW, "pop")], tex=CLEAN)
    add(1003.32, kb(U("FJS2CCXzIdc"), "punch", "dark"), [big("UNA BOTELLA DE WHISKY", 0.0, 0.86, 90, YELLOW, "pop")], tex=DARK)
    add(1004.32, kb(F(52411962413), "in", "doc"), [big("EN MITCHELL POINT PUEDES ASOMARTE A LAS VENTANAS NUEVAS", 0.2, 0.86, 52)], tex=CLEAN)
    add(1007.74, kb(F(52018570953), "in", "doc"), [big("Y VER EL RÍO COMO LO VIO AQUEL PRIMER AUTO EN 1915", 0.1, 0.86, 54, YELLOW)], tex=CLEAN)
    add(1012.26, kb(F(52689188670), "down", "doc"), [big("ABAJO, LA INTERSTATE 84 SIGUE A LO SUYO", 0.1, 0.12, 58)], tex=CLEAN)
    add(1015.5, kb(U("G6VNKqR8NvM"), "in", "doc"), [big("CAMIONES QUE NO LEVANTAN LA VISTA", 0.0, 0.86, 66)], tex=CLEAN)
    add(1017.9, kb(F(54149462465), "in", "doc"), [big("ARRIBA, LA GENTE VUELVE A CAMINAR DESPACIO", 0.2, 0.86, 58, YELLOW)], tex=CLEAN)
    add(1020.64, kb(F(54149003181), "in", "doc"), [big("PARANDO EN CADA VENTANA", 0.1, 0.86, 70)], tex=CLEAN)
    q2(1023.56, badge="LA GRAN PREGUNTA")
    add(1031.44, cus(_card, lines=[("PORQUE AQUELLA CARRETERA", 70, WHITE, 0.4, 0.0), ("LLEGÓ DEMASIADO PRONTO", 120, YELLOW, 0.56, 0.6)]), tr="fade", td=0.15, tex=GFX)
    add(1033.78, Split([kb(F(11794815443), "in", "archival"), V("611", U("Vu652ykZ0Xw"), 6.0, "doc")], labels=("SE HIZO PARA MIRAR", "TODOS QUERÍAN CORRER")),
        tex=CLEAN)
    add(1038.5, cus(G16.squeeze, t0=-9, truck_t=-1), [big("CUANDO LOS AUTOS CRECIERON, LA BELLEZA SE VOLVIÓ UN ESTORBO", 0.1, 0.94, 46, YELLOW)], tr="fade", td=0.15, tex=GFX)
    add(w("y el estado", 1041.6), cus(G16.fill, t0=-9, title="Y LA ENTERRARON SIN PENSARLO DOS VECES"), tr="fade", td=0.15, tex=GFX)
    add(1044.76, kb(F(52105794591), "in", "archival"), [big("SOLO CUANDO LA PERDIÓ…", 0.1, 0.12, 66), big("…SUPO LO QUE VALÍA", w("de lo que", 1047.0) - 1044.76, 0.86, 80, YELLOW, "pop")],
        tex=ARCH)
    add(1048.6, cus(G16.era, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(1054.32, cus(G16.carving, t0=-9), [Darken(0.2), big("LO ÚNICO QUE NO SE MOVIÓ EN TODO ESE TIEMPO", 0.1, 0.1, 54),
                                           big("DOS NOMBRES EN UNA PARED", w("dos nombres", 1056.6) - 1054.32, 0.9, 80, YELLOW, "pop")], tr="fade", td=0.15, tex=GFX)
    add(1058.86, kb(F(10488710113), "in", "dark"), [Darken(0.45), FnOverlay(G4.comments, line1="¿TE HABRÍAS QUEDADO EN EL TÚNEL CON ELLOS…",
                                                                            line2="…O HABRÍAS BAJADO AL PUEBLO CON LOS DEMÁS?", cta="TE LEO EN LOS COMENTARIOS")], tex=DARK)
    add(1067.92, kb(U("Iz_Yuy1gFCY"), "in", "dark", z=1.1), [Darken(0.55), FnOverlay(G2.subscribe), big("SIGUE RECORRIENDO LOS CAMINOS QUE ESTADOS UNIDOS DEJÓ ATRÁS", 0.2, 0.14,
                                                                                                              50, YELLOW)], tex=DARK)
    add(1072.36, kb(F(10488714063), "in", "dark", z=1.1), [Darken(0.5), FnOverlay(G2.subscribe), big("AQUÍ NO HACE FALTA GRABAR TU NOMBRE EN LA PARED", 0.1, 0.12, 52, YELLOW),
                                           big("CON UN CLIC, YA ERES DE LA CASA", w("con un clic", 1074.6) - 1072.36, 0.24, 62, WHITE, "pop")], tex=DARK)
    return _declutter(S)
