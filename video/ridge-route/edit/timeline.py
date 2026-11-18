"""The edit: every shot of the Ridge Route video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx7 as G7
import gfx13 as G13
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1131.70
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










# ------------------------------------------------------------------ Ridge Route specifics
RIDGE = M.rr_ll("ridge")
RIDGE_FULL = M.rr_ll("ridge_full")
I5 = M.rr_ll("i5")
US99 = M.rr_ll("us99")
AQUEDUCT = [(-120.10, 36.60), (-119.75, 36.10), (-119.50, 35.75)] + [tuple(p) for p in M.rr_data()["aqueduct"]]
CAP_LOC = "Library of Congress"
F = lambda i: f"f_{i}.jpg"
RED_ = (230, 70, 60)
BLUE_ = (110, 170, 220)
GREEN_ = (90, 210, 120)
CONC = (60, 200, 255)


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

    def q1(t0, bg="u_l2RPhWg31ro.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Por qué California siguió pagando, año tras año, una carretera por la que ya no subía nadie?", ("pagando,", "nadie?"), size=66),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_IdaRwQkKptc.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Cómo acabó la carretera más importante de California convertida en un camino que nadie puede usar?", ("importante", "nadie"), size=66),
            tr="glitch", td=0.3, tex=DARK)

    W_ = lambda name, fb, cap: pick_w(name, fb, cap)
    POSTCARD = lambda fb: fb
    OLD1 = F(48342039636)

    # ============================== INTRO (0 - 74.2)
    add(0.0, V("52430", "u_A8FVPa-wxbQ.jpg", 0.0, "doc"), [rich("VAS MANEJANDO HACIA EL NORTE POR LA INTERSTATE 5", ("interstate", "5"), 0.3, step=0.1, y=0.84, size=58, maxw=0.8)],
        tex=CLEAN)
    add(4.68, kb(F(3869990358), "in", "doc"), [big("8 CARRILES", 0.0, 0.3, 92, WHITE, "pop"), big("TRÁILERES SUBIENDO SIN ESFUERZO", w("tráileres", 6.6) - 4.68, 0.86, 64)],
        tex=CLEAN)
    add(8.56, kb("u_LrbG00vGyuQ.jpg", "up", "doc"), [big("PERO SI MIRAS HACIA LO ALTO…", 0.1, 0.86, 70)], tex=CLEAN)
    add(10.6, kb(OLD1, "in", "doc"), [big("HAY OTRA CARRETERA", 0.0, 0.86, 92, YELLOW, "pop")], tex=CLEAN)
    add(12.32, kb("u_TGDATKr4CLg.jpg", "punch", "doc"), [big("CONCRETO ROTO Y LLENO DE GRIETAS", 0.2, 0.86, 70)], tex=CLEAN)
    add(14.8, mp("rr_loc", [(0, -118.69, 34.63, 0.42), (2.7, -118.69, 34.66, 0.5)], [dict(type="route", ll=RIDGE, t0=0.0, draw=2.4, color=CONC, width=6)]),
        [big("SERPENTEA POR LA CRESTA", 0.3, 0.1, 66, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(17.48, kb("u_IdaRwQkKptc.jpg", "in", "doc"), [big("NADIE LA USA", 0.0, 0.86, 96, WHITE, "pop")], tex=CLEAN)
    add(18.72, kb("u_l2RPhWg31ro.jpg", "in", "cold"), [big("Y NO LLEVA A NINGÚN SITIO", 0.1, 0.86, 76)], tex=DARK)
    add(w("hace", 20.6), POSTCARD(kb("u_gc9Uou0GQC0.jpg", "in", "archival")), [Badge("HACE 100 AÑOS", 0.1, None),
                                                                               big("EL MISMO VIAJE TE COSTABA EL DÍA ENTERO", 0.6, 0.08, 56, YELLOW)], tex=ARCH)
    add(24.68, mp("rr_mid", [(0, -118.72, 34.66, 0.62), (3.0, -118.72, 34.66, 0.66)], [dict(type="route", ll=RIDGE_FULL, t0=0.0, draw=2.6, color=CONC, width=6)]),
        [Counter(0, 697, "{:.0f}", "CURVAS", 0.0, 1.4, (0.24, 0.3), 140, color=YELLOW),
         big("LÍMITE: 15 MILLAS POR HORA", w("un límite", 26.1) - 24.68, 0.88, 62, WHITE)], tr="zoom", td=0.3, tex=GFX)
    add(27.66, cus(G13.timecard, t0=0.0, out_t=w("listo", 31.3) - 27.66), tr="fade", td=0.2, tex=GFX)
    add(34.44, kb("u_P0bVatS8Jdw.jpg", "in", "doc"), [big("SI UN CAMIÓN PERDÍA LOS FRENOS…", 0.1, 0.12, 64),
                                                     big("…ACABABA EN EL FONDO DEL BARRANCO", w("acababan", 36.6) - 34.44, 0.86, 64, RED_)], tex=DARK)
    add(38.56, mp("rr_reg", [(0, -118.65, 34.75, 0.95), (2.7, -118.65, 34.75, 1.0)],
                  [dict(type="pin", at="rr_la", t0=0.1, label="LOS ÁNGELES", side="r", box=True, size=40),
                   dict(type="pin", at="rr_bakersfield", t0=0.4, label="BAKERSFIELD", side="r", box=True, size=40),
                   dict(type="route", ll=RIDGE_FULL, t0=0.3, draw=1.6, color=CONC, width=7)]),
        [big("LA CARRETERA MÁS IMPORTANTE DE CALIFORNIA", 0.3, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(41.3, kb("u_2bIF4cEJT4M.jpg", "in", "doc"), [Stamp("HOY, CERRADA", 0.2, RED_, (0.5, 0.48), -8, 130)], tex=CLEAN)
    add(42.68, kb(pick("m_13361680.jpg", F(7506439740)), "in", "doc"), [big("BAJO ESE LAGO…", 0.1, 0.3, 76), big("…HAY OTRA CARRETERA, HUNDIDA", w("hay", 44.9) - 42.68, 0.86, 70, BLUE_)],
        tex=CLEAN)
    add(46.78, kb("u_RuTa3MKO5IU.jpg", "in", "warm"), [Darken(0.35), big("Y LO MÁS RARO: UNA FACTURA", 0.1, 0.5, 84, YELLOW, "pop")], tex=CLEAN)
    add(48.7, cus(_card, lines=[("EL ESTADO SIGUIÓ PAGANDO LA DE LA CRESTA", 56, WHITE, 0.32, 0.1), ("HASTA 1965", 170, YELLOW, 0.5, 0.6),
                                ("32 AÑOS DESPUÉS DEL ÚLTIMO AUTO", 60, RED_, 0.7, w("32", 53.5) - 48.7)]), tr="fade", td=0.2, tex=GFX)
    add(56.44, kb(OLD1, "in", "doc"), [Darken(0.35), BigText("THE RIDGE ROUTE", "serif", 120, WHITE, (0.5, 0.48), 0.3, None, "up"),
                                       big("«SE LLAMABA»", 0.1, 0.34, 50, GREY_)], tr="fade", td=0.3, tex=CLEAN)
    add(58.92, kb(F(55646484600), "in", "doc"), [big("SU HISTORIA NO TERMINÓ CUANDO LA CERRARON", 0.2, 0.86, 62)], tex=CLEAN)
    q1(62.2)
    q2(67.84)

    # ============================== CAP 1: EL MURO (74.2 - 202.8)
    bg, ov = chapter(1, "EL MURO ENTRE LOS ÁNGELES Y EL VALLE", "u_po2VODCFpio.jpg", g="doc", year="1850–1910")
    add(74.22, bg, ov, tr="black", td=0.2, tex=DARK)
    add(76.96, kb("u_hTcIbJCGCT8.jpg", "in", "doc"), [big("¿EN LO ALTO DE UNA MONTAÑA, POR GUSTO?", 0.1, 0.86, 64)], tex=CLEAN)
    t0 = 79.24
    add(t0, mp("rr_reg", [(0, -118.4, 34.4, 1.0), (14.2, -118.8, 34.9, 0.9)],
               [dict(type="pin", at="rr_la", t0=w("los ángeles", 82.0) - t0, label="LOS ÁNGELES", side="r", box=True, size=40),
                dict(type="label", at=(-118.2, 33.85), text="UNA CUENCA", t0=w("cuenca", 83.6) - t0, size=48, box=True),
                dict(type="band", path=[(-120.4, 34.75), (-119.2, 34.72), (-118.5, 34.55), (-117.6, 34.3)], t0=w("encerrada", 84.2) - t0, color=(230, 220, 200), width=90, alpha=0.22),
                dict(type="label", at=(-120.0, 35.15), text="MONTAÑAS DE ESTE A OESTE", t0=w("cruzan", 86.4) - t0, size=42, box=True),
                dict(type="label", at=(-119.35, 35.75), text="VALLE DE SAN JOAQUÍN", t0=w("valle", 89.6) - t0, size=50, box=True),
                dict(type="pin", at="rr_bakersfield", t0=w("granjas", 92.0) - t0, label="BAKERSFIELD", side="r", box=True, size=38)]),
        tr="zoom", td=0.3, tex=GFX)
    add(93.94, kb("u_LrbG00vGyuQ.jpg", "in", "doc"), [big("ENTRE LOS DOS: UNA PARED", 0.1, 0.3, 76, YELLOW), big("ROCA · CAÑONES · CUESTAS", 1.2, 0.86, 70)], tex=CLEAN)
    add(97.98, W_("tejon1868", L("3g01998", kb("u_8hUXojHvw9E.jpg", "in", "warm"), "Valle de Tejon · litografía de 1855 · " + CAP_LOC),
                  "El paso de Tejon en 1868 · Alexander Gardner · " + WM), [big("CRUZARLA ERA UNA AVENTURA", 0.2, 0.08, 64)], tex=ARCH)
    add(101.16, W_("uvas_gardner", kb("u_QVfkOMtLF00.jpg", "in", "warm"), "Cañada de las Uvas, o paso de Tejon, 1867 · Alexander Gardner · " + WM),
        [big("CARRETAS Y DILIGENCIAS POR EL FONDO DE LOS CAÑONES", 0.2, 0.86, 56)], tex=ARCH)
    add(106.82, L("011559p", W_("tejon_1914", kb("u_mGDyJz7lBQc.jpg", "in", "warm"), "Fort Tejon, 1914 · " + WM), "Fort Tejon · HABS · " + CAP_LOC),
        [Badge("MEDIADOS DEL SIGLO XIX", 0.1, None), BigText("FORT TEJON", "serif", 100, YELLOW, (0.5, 0.12), w("fort", 110.9) - 106.82, None, "up")], tex=ARCH)
    add(112.92, L("24162", kb("u_FI73bqDrxWU.jpg", "in", "warm"), "Fort Tejon hoy · Carol M. Highsmith · " + CAP_LOC),
        [Badge("1858", 0.1, None), big("UNOS VISITANTES QUE NADIE ESPERABA…", 0.6, 0.86, 62)], tex=ARCH)
    add(118.96, W_("camels_dh", kb("u_v0NIPDl0yZA.jpg", "punch", "warm"), "Camellos del Ejército de EE. UU. · " + WM),
        [big("CAMELLOS", 0.0, 0.86, 120, YELLOW, "pop")], tex=ARCH)
    add(120.0, kb("u_BkqUJQiucKY.jpg", "in", "warm"), [big("¿SERVIRÍAN PARA CRUZAR LOS DESIERTOS DEL OESTE?", 0.2, 0.86, 56)], tex=CLEAN)
    add(123.96, kb("u_i_Z1o10BPPk.jpg", "in", "warm"), [big("AGUANTABAN COMO NADIE…", 0.1, 0.3, 72), big("…PERO ASUSTABAN A LOS CABALLOS", w("pero", 126.4) - 123.96, 0.86, 70, YELLOW)],
        tex=CLEAN)
    add(128.6, kb("u_U_SG5fO-ivs.jpg", "in", "warm"), [Badge("1861 · GUERRA CIVIL", 0.1, None), big("FIN DEL EXPERIMENTO", 0.5, 0.3, 80),
                                                     big("VENDIDOS O SUELTOS POR EL DESIERTO", w("acabaron", 133.4) - 128.6, 0.86, 62)], tex=CLEAN)
    add(136.2, kb("u_SvQMKx3Fl4s.jpg", "punch", "doc"), [Badge("1857", 0.1, None), big("EL TERREMOTO DE FORT TEJON", w("terremoto", 143.2) - 136.2, 0.86, 76, RED_)],
        post=postshake(5), tex=CLEAN)
    add(145.5, kb("u_8hUXojHvw9E.jpg", "in", "doc"), [big("ESE ERA EL LUGAR", 0.0, 0.5, 96, WHITE, "pop")], tex=CLEAN)
    add(146.9, kb("u_FNZwttoLRSU.jpg", "in", "doc"), [big("MONTAÑAS QUE SE MOVÍAN", 0.0, 0.3, 64), big("RÍOS QUE CRECÍAN DE GOLPE", w("ríos", 148.5) - 146.9, 0.46, 64),
                                                     big("CAMINOS QUE HABÍA QUE REHACER CADA INVIERNO", w("caminos", 150.4) - 146.9, 0.86, 56, YELLOW)], tex=CLEAN)
    add(153.1, L("3a52101", kb("u_wdsqSEom9fg.jpg", "in", "archival"), "Los Ángeles, primeros automóviles · " + CAP_LOC),
        [Badge("PRINCIPIOS DEL SIGLO XX", 0.1, None), big("LLEGA EL AUTOMÓVIL", 0.6, 0.08, 72, YELLOW)], tex=ARCH)
    add(156.14, L("6a18117", kb("u_gbE9qCONBHM.jpg", "in", "archival"), "Mercado de Los Ángeles, calles 9 y San Pedro · 1910 · " + CAP_LOC),
        [big("LOS ÁNGELES CRECÍA COMO POCAS CIUDADES", 0.2, 0.08, 60)], tex=ARCH)
    add(160.98, L("1a00662", kb("u_zCmAA7vm6lY.jpg", "in", "archival"), "Spring Street, Los Ángeles · 1906 · " + CAP_LOC),
        [Darken(0.3), Badge("1900", 0.0, None), Counter(0, 100000, "{:,.0f}", "HABITANTES", 0.3, 1.0, (0.5, 0.42), 150, prefix="≈ ")], tex=ARCH)
    add(164.34, kb("u_blh38qzyCRQ.jpg", "in", "doc"), [Darken(0.3), Badge("1910", 0.0, None),
                                                     Counter(100000, 300000, "{:,.0f}", "HABITANTES · Y SEGUÍA SUBIENDO", 0.2, 1.2, (0.5, 0.42), 150, color=YELLOW, prefix="+ DE ")],
        tex=CLEAN)
    add(169.16, kb(F(1058422005), "in", "doc"), [big("LA GENTE QUERÍA MANEJAR HACIA EL NORTE", 0.1, 0.86, 62)], tex=CLEAN)
    add(170.88, kb("u_7bk8q4AyJm8.jpg", "in", "warm"), [big("LOS CAMIONES: FRUTAS Y VERDURAS DEL VALLE", 0.1, 0.86, 62)], tex=CLEAN)
    t0 = 174.44
    add(t0, mp("rr_reg", [(0, -118.65, 34.75, 0.95)],
               [dict(type="pin", at="rr_la", t0=0.0, label="LOS ÁNGELES", side="r", box=True, size=40),
                dict(type="pin", at="rr_bakersfield", t0=0.2, label="BAKERSFIELD", side="r", box=True, size=40),
                dict(type="route", path=["rr_la", (-118.62, 34.5), (-118.85, 34.85), "rr_bakersfield"], t0=1.2, draw=1.8, color=YELLOW, width=6, dash=24)]),
        [big("UNA CARRETERA DE VERDAD PARA UNIR SUS DOS MITADES", w("una carretera", 176.7) - t0, 0.1, 56, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(180.08, kb("u_RuTa3MKO5IU.jpg", "in", "warm"), [Darken(0.45), Badge("1910 · LOS VOTANTES APRUEBAN", 0.1, None),
                                                       Counter(0, 18, "${:.0f} MILLONES", "UN PRÉSTAMO ENORME PARA LA ÉPOCA", w("18", 184.5) - 180.08, 1.0, (0.5, 0.46), 150, color=YELLOW)],
        tex=CLEAN)
    add(186.56, kb("u_6V2vCZ2hYtY.jpg", "in", "warm"), [big("LA PRIMERA RED DE CARRETERAS ESTATALES", 0.2, 0.86, 62)], tex=CLEAN)
    add(189.72, kb("u_JNDQNIuHI1g.jpg", "in", "doc"), [big("LOS ÁNGELES – EL VALLE: UNA PIEZA CLAVE", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)
    add(193.76, cus(_card, lines=[("GUARDA ESTA PALABRA", 56, GREY_, 0.34, 0.1), ("PRÉSTAMO", 190, YELLOW, 0.52, 0.5),
                                  ("VA A PESAR MÁS QUE CUALQUIER CURVA", 56, WHITE, 0.7, w("porque", 196.5) - 193.76)]), tr="fade", td=0.2, tex=GFX)
    add(199.26, kb("u_V82wRm87E7s.jpg", "in", "doc"), [big("EL PROBLEMA: DÓNDE PONERLA", 0.2, 0.86, 76)], tex=CLEAN)

    # ============================== CAP 2: POR QUÉ POR LA CRESTA (202.8 - 325.8)
    bg, ov = chapter(2, "POR QUÉ POR LA CRESTA", F(48342186127), g="doc", year="1914–1921")
    add(202.78, bg, ov, tr="black", td=0.2, tex=DARK)
    add(205.68, kb("u_3XxhSnxaQWs.jpg", "in", "doc"), [big("LO LÓGICO: EL FONDO DE LOS CAÑONES", 0.1, 0.86, 64)], tex=CLEAN)
    add(206.68, mp("rr_mid", [(0, -118.85, 34.85, 1.0), (4.0, -118.9, 34.9, 1.3)],
                   [dict(type="pin", at="rr_grapevine", t0=0.2, label="CAÑÓN DEL GRAPEVINE", side="r", box=True, size=40)]),
        [big("«GRAPEVINE»: POR LAS PARRAS SILVESTRES DEL ARROYO", w("que debía", 209.6) - 206.68, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(213.3, cus(G13.section, mode="flood", t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(219.16, kb("u_42G7xwGncC4.jpg", "in", "doc"), [big("EN UNA NOCHE, EL TRABAJO DE MESES", 0.1, 0.86, 68, YELLOW)], tex=CLEAN)
    add(222.1, kb("u_ZimUN_fsmjM.jpg", "in", "doc"), [big("HABÍA QUE EMPEZAR DE NUEVO…", 0.0, 0.38, 72), big("…CON OTRA IDEA", w("y esta", 223.8) - 222.1, 0.54, 90, YELLOW, "pop")],
        tex=CLEAN)
    add(225.42, cus(G13.section, mode="ridge", t0=w("la carretera", 229.8) - 225.42), [big("LOS INGENIEROS MIRARON HACIA ARRIBA", 0.1, 0.1, 58, WHITE)],
        tr="fade", td=0.2, tex=GFX)
    add(237.82, W_("tamping1915", kb("u_6x6bV7QN3GQ.jpg", "in", "archival"), "Cuadrilla en la obra de la Ridge Route · 1915 · " + WM),
        [big("UNA DECISIÓN SENSATA CON LAS HERRAMIENTAS DE 1914", 0.2, 0.08, 56)], tex=ARCH)
    add(241.92, kb("u_WoZs8gGyQBY.jpg", "in", "doc"), [Stamp("NO HABÍA GRANDES MÁQUINAS", 0.2, RED_, (0.5, 0.5), -8, 92)], tex=CLEAN)
    add(245.32, W_("fresno_odot", kb("u_6x6bV7QN3GQ.jpg", "in", "doc"), "Traíllas Fresno tiradas por caballos · Oregon DOT (CC BY 2.0) · " + WM),
        [big("HOMBRES", 0.0, 0.3, 84, WHITE, "pop"), big("PALAS", w("palas", 246.6) - 245.32, 0.44, 84, WHITE, "pop"),
         big("TRAÍLLAS TIRADAS POR CABALLOS", w("traillas", 247.2) - 245.32, 0.86, 64, YELLOW)], tex=ARCH)
    add(249.04, cus(G13.wrap, t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(259.66, cus(G13.curves, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(270.08, mp("rr_loc", [(0, -118.70, 34.60, 0.62), (4.4, -118.70, 34.70, 0.6)], [dict(type="route", ll=RIDGE, t0=0.0, draw=4.0, color=CONC, width=5)]),
        [big("DESDE EL AIRE: UN HILO ENREDADO SOBRE LAS MONTAÑAS", 0.4, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(274.46, W_("original", kb(F(51784589554), "in", "archival"), "La Ridge Route original · " + WM),
        [big("UNA CINTA ESTRECHA", 0.0, 0.3, 76), big("SIN BARANDAS · SIN DÓNDE ORILLARSE", 1.4, 0.86, 64, YELLOW)], tex=ARCH)
    add(278.66, kb("u_6h8R-RIgtT0.jpg", "in", "doc"), [big("DOS CAMIONES EN UNA CURVA…", 0.1, 0.3, 70), big("UNO FRENABA Y SE PEGABA AL BORDE", 2.4, 0.86, 64, RED_)],
        tex=CLEAN)
    add(284.54, POSTCARD(W_("ca1920_1", kb("u_3h0sCtXULYw.jpg", "in", "archival"), "La Ridge Route hacia 1920 · " + WM)),
        [Badge("OCTUBRE DE 1915", 0.1, None), big("ABRE… TODAVÍA DE TIERRA", 0.6, 0.86, 70, YELLOW)], tex=ARCH)
    add(289.28, kb("u_po2VODCFpio.jpg", "in", "doc"), [Darken(0.35), Counter(0, 450000, "${:,.0f}", "COSTÓ", 0.2, 1.0, (0.5, 0.3), 130, color=YELLOW),
                                                 big("24 MILLAS MÁS CORTA QUE EL CAMINO ANTERIOR", w("acortaba", 291.8) - 289.28, 0.86, 56)], tex=CLEAN)
    add(295.92, W_("ca1920_2", kb(F(51784212538), "in", "archival"), "La Ridge Route hacia 1920 · " + WM),
        [big("EL PLAN: CUBRIRLA DE CONCRETO ENSEGUIDA", 0.1, 0.08, 58), Badge("1917 · EE. UU. ENTRA EN LA GUERRA", w("1917", 299.6) - 295.92, None),
         Stamp("OBRA FRENADA", w("frenó", 303.5) - 295.92, RED_, (0.5, 0.55), -8, 110)], tex=ARCH)
    add(304.62, W_("constr1919", kb("u_9qfH_EIzH6w.jpg", "in", "archival"), "Obras de la Ridge Route · 1919 · California Highways · " + WM),
        [Badge("1919 · LLEGA EL CONCRETO", 0.1, None), big("ÚLTIMO TRAMO DEL NORTE: 1921", w("y el último", 307.6) - 304.62, 0.86, 64, YELLOW)], tex=ARCH)
    add(311.64, cus(_card, lines=[("COSTO TOTAL", 60, GREY_, 0.36, 0.1), ("≈ $1,5 MILLONES", 150, YELLOW, 0.54, 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(315.66, mp("rr_reg", [(0, -118.65, 34.75, 0.95)],
                   [dict(type="pin", at="rr_la", t0=0.0, label="LOS ÁNGELES", side="r", box=True, size=40),
                    dict(type="pin", at="rr_bakersfield", t0=0.0, label="BAKERSFIELD", side="r", box=True, size=40),
                    dict(type="route", ll=RIDGE_FULL, t0=0.3, draw=1.8, color=CONC, width=7)]),
        [big("POR PRIMERA VEZ: DIRECTO Y PAVIMENTADO", 0.6, 0.1, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(321.62, kb("u_xo0NVB5fauM.jpg", "in", "archival"), [big("LO QUE NO DECÍAN LOS ANUNCIOS: LO QUE COSTABA HACERLO", 0.2, 0.86, 54)], tex=ARCH)

    # ============================== CAP 3: UN VIAJE EN LOS AÑOS VEINTE (325.8 - 455.8)
    bg, ov = chapter(3, "UN VIAJE POR LA RIDGE ROUTE", F(5744217358), g="doc", year="AÑOS VEINTE")
    add(325.82, bg, ov, tr="black", td=0.2, tex=DARK)
    add(328.76, L("1a00670", kb("u_wdsqSEom9fg.jpg", "in", "archival"), "Broadway, Los Ángeles · 1902 · " + CAP_LOC),
        [big("SALES TEMPRANO DE LOS ÁNGELES", 0.2, 0.08, 66)], tex=ARCH)
    add(332.22, kb("u_vlFco6P4j6I.jpg", "in", "warm"), [Counter(0, 12, "{:.0f} HORAS", "HASTA BAKERSFIELD", 0.3, 1.0, (0.5, 0.42), 170, color=YELLOW, prefix="≈ ")],
        tex=DARK)
    add(335.6, W_("ca1920_3", kb("u_hTcIbJCGCT8.jpg", "in", "archival"), "La Ridge Route hacia 1920 · " + WM),
        [big("EN LA MONTAÑA:", 0.1, 0.28, 64), big("15 MPH", 0.5, 0.48, 180, YELLOW, "pop"), big("≈ 24 KM/H", w("unos", 339.0) - 335.6, 0.66, 64)], tex=ARCH)
    add(341.64, kb("u_hJJM5qJMDbc.jpg", "in", "warm"), [big("LA VELOCIDAD DE UNA BICICLETA TRANQUILA", 0.1, 0.86, 62)], tex=CLEAN)
    add(346.24, cus(G13.timecard, t0=w("te sellan", 351.1) - 346.24, out_t=w("si llegaste", 357.4) - 346.24), [Badge("CASTAIC", w("castaic", 349.8) - 346.24, None)],
        tr="fade", td=0.2, tex=GFX)
    add(362.38, kb("u_hTcIbJCGCT8.jpg", "in", "doc"), [big("AUNQUE LA MONTAÑA YA SE ENCARGA DE FRENARTE", 0.2, 0.86, 60)], tex=CLEAN)
    add(365.78, cus(G13.climb, mode="up", t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(379.82, cus(G13.climb, mode="down", t0=0.2), [big("LA BAJADA ES PEOR", 0.0, 0.92, 70, RED_)], tr="fade", td=0.2, tex=GFX)
    add(389.68, kb("u_wzGAPwbUfao.jpg", "in", "doc"), [big("EL PRECIPICIO A UN LADO", 0.1, 0.3, 72), big("NINGUNA BARANDA QUE TE PARARA", 1.6, 0.86, 70, RED_)], tex=CLEAN)
    add(394.6, V("52434", "u_g_FizakXz50.jpg", 0.0, "doc"), [big("CAMIONES CARGADOS CON TONELADAS", 0.1, 0.12, 64), big("UNA APUESTA DIARIA", w("era", 398.4) - 394.6, 0.86, 80, YELLOW)],
        tex=CLEAN)
    add(399.82, kb("u_-kl1qAOCkXoI.jpg", "punch", "dark"), [big("SE IBAN POR EL BORDE", 0.3, 0.86, 92, RED_, "pop")], post=postshake(4), tex=DARK)
    add(402.8, kb(F(3869990146), "in", "doc"), [big("LA BAJADA FINAL HACIA EL VALLE", 0.0, 0.12, 62), big("OLOR A FRENOS QUEMADOS", w("el olor", 404.6) - 402.8, 0.86, 76, YELLOW)],
        tex=CLEAN)
    add(407.78, kb("u_OwBRQ0bykX8.jpg", "in", "warm"), [big("UN CAMIÓN EN LA CUNETA, ECHANDO HUMO", 0.1, 0.86, 64)], tex=DARK)
    add(414.6, W_("rockslide", kb("u_E7RzhOJLKNc.jpg", "in", "dark"), "La Ridge Route hoy · " + WM),
        [Darken(0.45), big("LA CURVA DEL HOMBRE MUERTO", 0.3, 0.38, 76), BigText("DEAD MAN'S CURVE", "serif", 110, RED_, (0.5, 0.56), w("dead", 419.0) - 414.6, None, "pop")],
        tex=DARK)
    add(420.58, kb("u_E7RzhOJLKNc.jpg", "in", "dark"), [big("NADIE TENÍA QUE EXPLICAR POR QUÉ", 0.1, 0.86, 70)], tex=DARK)
    add(422.82, kb("u_n51RN1R7ScI.jpg", "in", "cold"), [Badge("INVIERNO", 0.1, None), big("LA NIEVE TAPABA LOS PASOS ALTOS", 0.4, 0.86, 66)], tex=CLEAN)
    add(426.18, V("44269", "u_xJ2tjuUHD9M.jpg", 0.0, "cold"), [big("LA NIEBLA, ATRAPADA ENTRE LOS CERROS", 0.1, 0.86, 64)], tex=CLEAN)
    t0 = 429.32
    add(t0, mp("rr_reg", [(0, -118.9, 34.8, 1.0)],
               [dict(type="route", ll=RIDGE_FULL, t0=0.0, draw=0.2, color=CONC, width=7),
                dict(type="xmark", at=(-118.76, 34.70), t0=0.6, size=60),
                dict(type="label", at=(-119.3, 35.7), text="NORTE", t0=w("california", 433.0) - t0, size=60, box=True),
                dict(type="label", at=(-118.2, 33.9), text="SUR", t0=w("california", 433.0) - t0 + 0.3, size=60, box=True)]),
        [big("CALIFORNIA, PARTIDA EN DOS", w("california", 433.0) - t0, 0.1, 70, RED_)], tr="zoom", td=0.3, tex=GFX)
    add(434.88, kb("u_m3vPvRTNrMs.jpg", "in", "dark"), [big("LA NOCHE DENTRO DEL AUTO, ENVUELTOS EN MANTAS", 0.2, 0.86, 60)], tex=DARK)
    add(441.16, kb("u_GYnwI9IPTIU.jpg", "in", "dark"), [big("OTROS DABAN LA VUELTA…", 0.0, 0.38, 72), big("SIN HABER LLEGADO A NINGUNA PARTE", 1.8, 0.54, 64, YELLOW)], tex=DARK)
    add(447.12, W_("ca1920_4", kb(F(55646268819), "in", "archival"), "La Ridge Route hacia 1920 · " + WM),
        [big("AUN ASÍ, LA GENTE LA USABA", 0.0, 0.08, 66), big("NO HABÍA OTRA", w("porque", 449.2) - 447.12, 0.86, 92, YELLOW, "pop")], tex=ARCH)
    add(450.22, kb("u_1OKrxrhonw8.jpg", "in", "archival"), [big("MILES DE VIAJEROS CANSADOS…", 0.1, 0.3, 70), big("…ALGUIEN ABRE UN NEGOCIO", w("alguien", 453.2) - 450.22, 0.86, 76, YELLOW)],
        tex=ARCH)

    # ============================== CAP 4: LAS POSADAS (455.8 - 574.0)
    bg, ov = chapter(4, "LAS POSADAS DE LAS CUMBRES", "u_gB8kWnDfqEA.jpg", g="warm", year="1915–1930")
    add(455.8, bg, ov, tr="black", td=0.2, tex=DARK)
    add(458.82, kb("u_79M58-PH2W0.jpg", "in", "archival"), [big("POSADAS · RESTAURANTES · GASOLINERAS", 0.0, 0.86, 64)], tex=ARCH)
    add(460.66, cus(G13.inns, t0=w("las ponían", 464.3) - 460.66, step=0.45), [big("NO A LA ENTRADA DEL PUEBLO", 0.1, 0.94, 50, GREY_)], tr="fade", td=0.2, tex=GFX)
    add(469.12, kb("u_W7nMl3oWVt0.jpg", "punch", "warm"), [big("RELLENAR EL RADIADOR", 0.0, 0.86, 80, WHITE, "pop")], tex=CLEAN)
    add(w("comprar", 471.0), kb("u_xCDnn4bH6D0.jpg", "punch", "warm"), [big("GASOLINA", 0.0, 0.86, 90, WHITE, "pop")], tex=CLEAN)
    add(w("comer", 471.9), kb("u_Q0OitqGyVWA.jpg", "punch", "warm"), [big("ALGO CALIENTE", 0.0, 0.86, 90, WHITE, "pop")], tex=CLEAN)
    add(473.16, kb("u_ZCGyXRnr4Uw.jpg", "in", "warm"), [big("UN MECÁNICO PARA LOS FRENOS ANTES DE LA BAJADA", 0.4, 0.86, 56, YELLOW)], tex=CLEAN)
    add(479.52, W_("reservoir_summit", kb(F(55646069796), "in", "doc"), "Reservoir Summit hoy · " + WM),
        [BigText("RESERVOIR SUMMIT", "serif", 92, YELLOW, (0.5, 0.12), 0.1, None, "up"), big("UN RESTAURANTE ELEGANTE CON VISTAS AL PRECIPICIO", 1.0, 0.86, 56)], tex=CLEAN)
    add(484.72, kb("u_JQT6xXS16dg.jpg", "in", "warm"), [big("CENAR MIRANDO LAS LUCES DEL VALLE", 0.1, 0.86, 66)], tex=DARK)
    add(487.3, W_("halfway", cus(G13.inns, t0=-9, hi=2), "Sitio del Kelly's Half Way Inn · " + WM),
        [BigText("KELLY'S HALF WAY INN", "serif", 84, YELLOW, (0.5, 0.12), 0.1, None, "up"), big("LA POSADA DE LA MITAD DEL CAMINO", 1.2, 0.86, 60)], tex=ARCH)
    add(492.06, W_("tumble", cus(G13.inns, t0=-9, hi=3), "Sitio del Tumble Inn · " + WM), [BigText("TUMBLE INN", "serif", 100, YELLOW, (0.5, 0.12), 0.0, None, "up")],
        tex=ARCH)
    add(494.04, cus(G13.inns, t0=-9, hi=4), [big("SANDBERG'S SUMMIT HOTEL", w("estaba", 498.7) - 494.04, 0.08, 66, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(500.6, W_("sandberg", kb("u_gB8kWnDfqEA.jpg", "in", "warm"), "Sitio del Sandberg's Summit Hotel · " + WM),
        [big("UNA CABAÑA DE TRONCOS DE TRES PISOS", 0.1, 0.08, 62), big("CON UNA ENORME CHIMENEA", w("con una", 502.8) - 500.6, 0.86, 70, YELLOW)], tex=ARCH)
    add(504.5, kb("u_n51RN1R7ScI.jpg", "in", "cold"), [big("EL REFUGIO DE LOS ATRAPADOS POR LA NIEVE", 0.1, 0.86, 62)], tex=CLEAN)
    add(508.48, V("3459", "u_Q0OitqGyVWA.jpg", 0.0, "warm"), [big("AQUELLA CHIMENEA LOS SALVÓ DEL FRÍO", 0.3, 0.86, 66, YELLOW)], tex=DARK)
    add(511.92, kb("u_IYDM50Nwp-8.jpg", "in", "archival"), [BigText("NATIONAL FOREST INN", "serif", 90, YELLOW, (0.5, 0.14), 0.2, None, "up"),
                                                          big("LA MÁS ANIMADA", 0.8, 0.86, 70)], tex=ARCH)
    add(514.56, kb("u_9TrbRKa5Yf4.jpg", "in", "archival"), [Badge("LEY SECA · 1920–1933", 0.1, None), big("EL COMEDOR SE CONVERTÍA EN SALÓN DE BAILE", w("su comedor", 518.3) - 514.56, 0.86, 58)],
        tex=ARCH)
    add(521.92, kb("u_tSi3-w7ISXE.jpg", "in", "warm"), [big("NADIE PREGUNTABA DE DÓNDE SALÍAN LAS BEBIDAS", 0.1, 0.86, 58)], tex=DARK)
    add(525.92, kb("u_OKm954YY_Xo.jpg", "in", "archival"), [big("ALLÍ ARRIBA, LA LEY LLEGABA DESPACIO", 0.2, 0.86, 66, YELLOW)], tex=ARCH)
    add(529.8, W_("ca1920_5", kb(F(5590800823), "in", "archival"), "La Ridge Route hacia 1920 · " + WM), [big("PARA LOS VIAJEROS: LO MEJOR DEL VIAJE", 0.1, 0.86, 62)], tex=ARCH)
    add(533.4, cus(_card, lines=[("PARA LOS DUEÑOS, UN NEGOCIO QUE DEPENDÍA DE UNA SOLA COSA:", 46, GREY_, 0.36, 0.1),
                                 ("QUE LA CARRETERA SIGUIERA SIENDO", 74, WHITE, 0.52, w("que la", 536.9) - 533.4),
                                 ("EL ÚNICO CAMINO", 110, YELLOW, 0.66, w("único", 538.9) - 533.4)]), tr="fade", td=0.2, tex=GFX)
    add(540.1, kb("u_9qfH_EIzH6w.jpg", "in", "doc"), [big("EL ESTADO INTENTABA DOMAR LA MONTAÑA A GOLPES", 0.1, 0.86, 58)], tex=CLEAN)
    add(543.86, cus(G13.swedes, t0=0.2), tr="fade", td=0.2, tex=GFX)
    add(551.64, kb(pick(F(48342181577), "w_swede.jpg"), "up", "doc"), [BigText("SWEDE'S CUT", "serif", 110, YELLOW, (0.5, 0.14), 0.0, None, "up"),
                                                                       big("TODAVÍA HOY IMPRESIONA", w("y todavía", 553.6) - 551.64, 0.86, 70)], tex=CLEAN)
    add(556.78, kb(pick(F(48342181942), F(48342181577)), "in", "doc"), [Badge("1924", 0.1, None), big("ENSANCHAN LAS CURVAS CIEGAS MÁS PELIGROSAS", 0.5, 0.86, 58)], tex=CLEAN)
    add(561.38, kb("u_Q2qxFeqxnQk.jpg", "in", "doc"), [big("EL TRÁFICO CRECÍA CADA AÑO…", 0.1, 0.3, 70), big("…Y LA CARRETERA SEGUÍA SIENDO LA MISMA CINTA", 2.2, 0.86, 56, YELLOW)],
        tex=CLEAN)
    add(567.6, kb("u_GTFvjTPrdFE.jpg", "in", "warm"), [big("POSADAS ESPERANDO CLIENTES QUE NO IBAN A VOLVER", 0.4, 0.86, 58)], tex=DARK)

    # ============================== CAP 5: LA CARRETERA DEL CAÑÓN (574.0 - 708.3)
    bg, ov = chapter(5, "LA CARRETERA DEL CAÑÓN", "u_49TfEiFhWGI.jpg", g="doc", year="1930–1961")
    add(573.98, bg, ov, tr="black", td=0.2, tex=DARK)
    add(577.0, kb("u_Q2qxFeqxnQk.jpg", "in", "doc"), [big("LA RIDGE ROUTE SE HABÍA QUEDADO PEQUEÑA", 0.1, 0.86, 62)], tex=CLEAN)
    add(578.64, kb("u_TmnnwturBdQ.jpg", "in", "doc"), [Badge("DESDE 1914", 0.1, None), big("LAS MÁQUINAS", w("las máquinas", 581.6) - 578.64, 0.86, 110, YELLOW, "pop")], tex=CLEAN)
    add(582.76, kb("u_eIj8K5dHyIY.jpg", "in", "doc"), [big("MÁQUINAS DE ORUGA QUE MUEVEN MONTAÑAS DE ROCA", 0.1, 0.86, 58)], tex=CLEAN)
    add(586.32, kb("u_ZcozVqL5FKc.jpg", "punch", "doc"), [big("DINAMITA MÁS FIABLE", 0.0, 0.86, 84, WHITE, "pop")], post=postshake(5), tex=CLEAN)
    add(588.28, cus(_card, lines=[("LO QUE ANTES ERA IMPOSIBLE", 70, GREY_, 0.4, 0.1), ("AHORA SOLO ERA CARO", 110, YELLOW, 0.56, w("ahora", 590.0) - 588.28)]),
        tr="fade", td=0.2, tex=GFX)
    t0 = 591.86
    add(t0, mp("rr_loc", [(0, -118.73, 34.66, 0.55), (14.0, -118.76, 34.66, 0.62)],
               [dict(type="route", ll=RIDGE, t0=0.0, draw=0.2, color=(150, 150, 160), width=5),
                dict(type="route", ll=US99, t0=w("sino", 598.1) - t0, draw=3.0, color=GREEN_, width=7),
                dict(type="label", at=(-118.68, 34.73), text="1915 · LA CRESTA", t0=0.3, size=40, box=True),
                dict(type="label", at=(-118.86, 34.60), text="1933 · EL CAÑÓN DEL PIRU", t0=w("pirú", 600.0) - t0, size=40, box=True)]),
        [Badge("1930", 0.1, None), big("RIDGE ROUTE ALTERNATE → US 99", w("la llamaron", 600.8) - t0, 0.1, 62, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(606.48, L("8b32666", pick(F(4274994698), "u_A8FVPa-wxbQ.jpg"), "La US 99 en el valle de San Joaquín · Dorothea Lange, 1938 · " + CAP_LOC),
        [big("TRES CARRILES · EL DEL CENTRO PARA ADELANTAR", 0.1, 0.08, 56), big("CURVAS MUCHO MÁS ABIERTAS", w("y curvas", 609.8) - 606.48, 0.86, 64, YELLOW)], tex=ARCH)
    add(611.9, kb("u_79M58-PH2W0.jpg", "in", "archival"), [Darken(0.4), big("PAGADA CON EL IMPUESTO A LA GASOLINA", 0.1, 0.24, 58),
                                                          Counter(0, 3.5, "${:.1f} MILLONES", "", w("costó", 615.2) - 611.9, 1.0, (0.5, 0.55), 140, color=YELLOW)], tex=ARCH)
    t0 = 618.04
    add(t0, mp("rr_loc", [(0, -118.765, 34.645, 1.3), (13.0, -118.765, 34.645, 1.5)],
               [dict(type="route", ll=US99, t0=0.0, draw=0.2, color=GREEN_, width=7),
                dict(type="pin", at="rr_pyramid_rock", t0=w("dejaron", 621.7) - t0, label="UN PICACHO CON FORMA DE PIRÁMIDE", side="r", box=True, size=38)]),
        [BigText("PYRAMID ROCK", "serif", 110, YELLOW, (0.5, 0.14), w("pyramid", 627.2) - t0, None, "up"),
         big("ACUÉRDATE DE ESE NOMBRE", w("acuérdate", 628.6) - t0, 0.88, 64)], tr="zoom", td=0.3, tex=GFX)
    add(631.84, pick_f(4274994698, L("8b32666", kb("u_A8FVPa-wxbQ.jpg", "in", "doc"), None), "La US 99 en el condado de Kern, 1939 · marca de dominio público (Flickr)"),
        [Badge("29 DE OCTUBRE DE 1933", 0.1, None), big("SE ABRE LA CARRETERA NUEVA", 0.8, 0.86, 70, YELLOW)], tex=ARCH)
    add(636.56, mp("rr_mid", [(0, -118.75, 34.70, 0.72)],
                   [dict(type="route", ll=RIDGE_FULL, t0=0.0, draw=0.2, color=(150, 150, 160), width=5),
                    dict(type="route", ll=US99, t0=0.2, draw=1.6, color=GREEN_, width=7)]),
        [big("CASI 10 MILLAS MENOS", 0.3, 0.1, 76, GREEN_), big("MUCHO MÁS RÁPIDA", w("y permitía", 638.2) - 636.56, 0.88, 62)], tr="zoom", td=0.3, tex=GFX)
    add(640.4, kb("u_wdsqSEom9fg.jpg", "in", "archival"), [big("UNA MAÑANA DE CURVAS…", 0.1, 0.3, 70), big("…EN UNA FRACCIÓN DEL TIEMPO", w("ahora", 643.3) - 640.4, 0.86, 70, YELLOW)],
        tex=ARCH)
    add(645.46, L("8b32666", kb("u_9INE4qc6LLc.jpg", "in", "doc"), None), [big("LOS CAMIONES BAJABAN SIN JUGARSE LA VIDA", 0.1, 0.86, 60)], tex=ARCH)
    add(648.58, kb(pick(F(51784212538), "u_l2RPhWg31ro.jpg"), "in", "doc"), [big("LA RIDGE ROUTE SE VACIÓ DE UN DÍA PARA OTRO", 0.1, 0.86, 60, YELLOW)], tex=CLEAN)
    add(652.1, kb("u_3h0sCtXULYw.jpg", "in", "doc"), [big("NADIE PUSO UNA BARRERA", 0.0, 0.38, 76), big("SIMPLEMENTE, DEJÓ DE SUBIR GENTE", 1.8, 0.54, 66, YELLOW)], tex=CLEAN)
    add(656.4, kb("u_JNDQNIuHI1g.jpg", "in", "warm"), [big("SOLO ALGUNOS RANCHEROS Y VECINOS", 0.1, 0.86, 64)], tex=CLEAN)
    add(661.44, kb("u_l2RPhWg31ro.jpg", "out", "cold"), [big("PARA EL RESTO DE CALIFORNIA, DEJÓ DE EXISTIR", 0.2, 0.86, 58)], tex=DARK)
    add(665.96, W_("tumble_step", kb("u_SZwTEno2Eyo.jpg", "in", "warm"), "Escalones del Tumble Inn · " + WM), [big("LAS POSADAS, SIN CLIENTES", 0.0, 0.86, 72)], tex=ARCH)
    add(668.88, W_("tumble", kb("u_82LVi7g5_rU.jpg", "in", "warm"), "Sitio del Tumble Inn · " + WM), [Badge("1933", 0.0, None), big("CIERRA EL TUMBLE INN", 0.3, 0.86, 76)],
        tex=ARCH)
    add(671.62, V("3443", "u_ebrLOCu1chY.jpg", 0.0, "warm"), [Badge("OCTUBRE DE 1932", 0.1, None), big("ARDE EL NATIONAL FOREST INN", 0.5, 0.86, 72, (255, 170, 80)),
                                                              big("NADIE LO RECONSTRUYÓ", w("y nadie", 679.1) - 671.62, 0.14, 62)], tex=DARK)
    add(680.98, W_("sandberg", kb("u_gB8kWnDfqEA.jpg", "in", "warm"), None), [big("SANDBERG'S AGUANTÓ MÁS…", 0.1, 0.86, 70)], tex=ARCH)
    add(684.24, V("3459", "u_wPV4vRwSTfA.jpg", 0.0, "warm"), [Badge("29 DE ABRIL DE 1961", 0.1, None), big("SE QUEMÓ POR COMPLETO", 0.8, 0.86, 80, (255, 170, 80))], tex=DARK)
    add(688.86, kb("u_Q0OitqGyVWA.jpg", "in", "warm"), [big("BASURA QUEMADA EN LA GRAN CHIMENEA", 0.1, 0.86, 64)], tex=DARK)
    add(691.94, kb("u_3A_3x7Ijy8E.jpg", "in", "doc"), [big("SOLO QUEDARON LOS CIMIENTOS", 1.0, 0.86, 76, YELLOW)], tex=CLEAN)
    add(697.4, cus(_card, lines=[("COMO RUTA PRINCIPAL DURÓ", 60, GREY_, 0.38, 0.1), ("18 AÑOS", 180, YELLOW, 0.56, w("18", 700.0) - 697.4)]), tr="fade", td=0.2, tex=GFX)
    add(702.16, kb("u_RuTa3MKO5IU.jpg", "in", "warm"), [Darken(0.3), big("LO MÁS RARO NO ESTABA EN LA MONTAÑA…", 0.1, 0.3, 64),
                                                       big("…ESTABA EN LAS CUENTAS DEL ESTADO", w("estaba en", 705.3) - 702.16, 0.86, 70, YELLOW)], tex=CLEAN)

    # ============================== CAP 6: LA FACTURA (708.3 - 821.4)
    bg, ov = chapter(6, "LA FACTURA HASTA 1965", "u_Vm2LYbTdGNQ.jpg", g="warm", year="1933–1965")
    add(708.32, bg, ov, tr="black", td=0.2, tex=DARK)
    add(710.52, kb("u_-qq7JUjlhcs.jpg", "in", "warm"), [Darken(0.4), Counter(0, 1.5, "${:.1f} MILLONES", "LO QUE COSTÓ LA RIDGE ROUTE", 0.1, 1.0, (0.5, 0.46), 150, color=YELLOW, prefix="≈ ")],
        tex=CLEAN)
    add(712.76, kb("u_KPHhnz-3iI0.jpg", "in", "warm"), [big("DINERO PRESTADO CON BONOS", 0.3, 0.12, 72, YELLOW), big("SE DEVUELVE DURANTE DÉCADAS, CON INTERESES", w("un préstamo", 717.5) - 712.76, 0.86, 56)],
        tex=CLEAN)
    q1(722.1, bg="u_l2RPhWg31ro.jpg", badge="PREGUNTA 1 · LA RESPUESTA")
    add(731.48, cus(_card, lines=[("PORQUE LA DEUDA", 80, WHITE, 0.42, 0.0), ("NO ENTENDÍA DE TRÁFICO", 110, YELLOW, 0.58, 0.6)]), tr="flash", td=0.2, tex=GFX)
    add(733.48, Split([kb("u_xZ7V5m3HVfQ.jpg", "in", "doc"), kb("u_l2RPhWg31ro.jpg", "in", "doc")], labels=["MIL AUTOS", "NINGUNO"]),
        [big("A LOS PRESTAMISTAS LES DABA IGUAL", 0.2, 0.08, 58)], tex=CLEAN)
    add(739.3, kb("u_tT2DSShVDTI.jpg", "in", "warm"), [big("UN COMPROMISO FIRMADO", 0.1, 0.3, 72), big("CUOTA A CUOTA, AÑO TRAS AÑO", 1.6, 0.86, 72, YELLOW)], tex=CLEAN)
    add(744.88, cus(G13.bonds, t0=0.2, use_t=1.0, end_t=w("1965", 761.0) - 744.88), [big("1933: EL ÚLTIMO AUTO… Y AÑOS DE PAGOS POR DELANTE", 0.3, 0.12, 52)],
        tr="fade", td=0.2, tex=GFX)
    add(764.16, pick_f(4274994698, L("8b32666", kb("u_9INE4qc6LLc.jpg", "in", "doc"), None), None),
        [big("LOS CAMIONES RODABAN POR LA CARRETERA NUEVA…", 0.1, 0.12, 58), big("…Y EL ESTADO PAGABA LA VIEJA", w("el estado", 769.2) - 764.16, 0.86, 70, YELLOW)], tex=ARCH)
    add(771.44, L("50214", kb("u_A8FVPa-wxbQ.jpg", "in", "doc"), "La Interstate 5 · Carol M. Highsmith · " + CAP_LOC),
        [Counter(0, 32, "{:.0f} AÑOS", "SIN TRÁFICO", 0.2, 1.0, (0.5, 0.2), 120, color=YELLOW), big("Y EN EL CAÑÓN, UNA AUTOPISTA MÁS GRANDE", w("y en", 774.2) - 771.44, 0.86, 58)],
        tex=CLEAN)
    add(778.88, kb("u_PxiAc1aElFQ.jpg", "in", "warm"), [big("PIÉNSALO ASÍ", 0.0, 0.3, 80), big("LAS CUOTAS DE UN CARRO QUE YA VENDISTE", 1.2, 0.86, 62, YELLOW)], tex=CLEAN)
    add(783.22, kb(pick(F(51784212538), "u_3h0sCtXULYw.jpg"), "in", "doc"), [big("TIRADO EN UN CERRO", 0.0, 0.3, 76), big("Y QUE YA NO ARRANCA", w("y que", 784.9) - 783.22, 0.86, 76, RED_)],
        tex=CLEAN)
    add(786.7, cus(_card, lines=[("SE USÓ", 60, GREY_, 0.3, 0.0), ("18 AÑOS", 130, WHITE, 0.42, 0.3), ("SE PAGÓ DURANTE", 60, GREY_, 0.58, w("se pagó", 790.4) - 786.7),
                                 ("50", 190, YELLOW, 0.74, w("se pagó", 790.4) - 786.7 + 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(792.12, V("18305", "u_-qq7JUjlhcs.jpg", 0.0, "warm"), [big("GENERACIONES QUE NUNCA LA PISARON AYUDARON A PAGARLA", 0.2, 0.86, 54)], tex=DARK)
    add(798.1, kb(OLD1, "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe), big("SUSCRIBIRTE NO CUESTA NADA, NI DENTRO DE 50 AÑOS", w("suscribirte", 801.4) - 798.1, 0.14, 50, YELLOW)],
        tex=DARK)
    add(811.72, kb("u_49TfEiFhWGI.jpg", "in", "doc"), [big("¿Y QUÉ FUE DE LA NUEVA, LA DEL CAÑÓN?", 0.2, 0.86, 64)], tex=CLEAN)
    add(816.96, kb(pick("m_13361680.jpg", "u_IVajGOKvs7c.jpg"), "in", "cold"), [big("UN FINAL TODAVÍA MÁS EXTRAÑO", 0.0, 0.3, 66), big("ACABÓ BAJO EL AGUA", w("acabó", 819.5) - 816.96, 0.86, 90, BLUE_, "pop")],
        tex=CLEAN)

    # ============================== CAP 7: TRES CARRETERAS (821.4 - 965.4)
    bg, ov = chapter(7, "TRES CARRETERAS EN UN MISMO CORREDOR", "u_xZ7V5m3HVfQ.jpg", g="doc", year="1952–1973")
    add(821.42, bg, ov, tr="black", td=0.2, tex=DARK)
    add(824.26, L("8b32666", kb("u_9INE4qc6LLc.jpg", "in", "doc"), None), [Badge("1952", 0.1, None), big("AMPLIADA A CUATRO CARRILES", 0.4, 0.86, 70),
                                                                            big("EL TRÁFICO NO PARABA DE CRECER", w("pero", 828.0) - 824.26, 0.12, 60, YELLOW)], tex=ARCH)
    add(830.22, L("50215", kb("u_J-hYMYa2jY8.jpg", "in", "doc"), "La Interstate 5 · Carol M. Highsmith · " + CAP_LOC),
        [Badge("AÑOS SESENTA", 0.1, None), BigText("INTERSTATE 5", "serif", 110, YELLOW, (0.5, 0.42), w("la interstate", 834.4) - 830.22, None, "up"),
         big("«THE GOLDEN STATE FREEWAY»", w("la golden", 835.6) - 830.22, 0.58, 60, WHITE)], tex=CLEAN)
    add(838.02, V("507", "u_xZ7V5m3HVfQ.jpg", 0.0, "doc"), [Badge("24 DE AGOSTO DE 1970", 0.1, None), big("SE TERMINA EL TRAMO DE MONTAÑA", 0.8, 0.86, 66)], tex=CLEAN)
    add(842.72, V("611", F(3869990358), 0.0, "doc"), [big("8 CARRILES ANCHOS", 0.0, 0.3, 84, WHITE, "pop"), big("PENDIENTES SUAVES · EL MISMO CORREDOR", 1.6, 0.86, 62)], tex=CLEAN)
    add(847.64, cus(G13.wrap, t0=-9, cut_t=w("las atravesaron", 852.3) - 847.64), tr="fade", td=0.2, tex=GFX)
    add(853.72, cus(G13.section, mode="cut", t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(858.62, kb("u_A8FVPa-wxbQ.jpg", "in", "doc"), [Darken(0.35), Counter(0, 103, "${:.0f} MILLONES", "COSTÓ LA AUTOPISTA", 0.1, 1.0, (0.5, 0.42), 150, color=YELLOW)], tex=CLEAN)
    add(861.04, kb(pick(F(11158109183), "u_V7XJ_4PlWU4.jpg"), "in", "doc"), [Darken(0.3), Badge("1970", 0.1, None),
                                                                           Counter(0, 73000, "{:,.0f}", "AUTOS AL DÍA", 0.3, 1.2, (0.5, 0.42), 150, color=YELLOW)], tex=CLEAN)
    add(865.44, V("1151", "u_M3RVFbqKGu4.jpg", 0.0, "dark"), [big("HOY, MUCHÍSIMOS MÁS", 0.1, 0.38, 80), big("DÍA Y NOCHE, SIN PARAR", 1.2, 0.54, 70, YELLOW)], tex=DARK)
    add(869.48, pick_f(4274994698, kb("u_3h0sCtXULYw.jpg", "in", "doc"), None), [big("LA CARRETERA DE 1933 TAMBIÉN SE QUEDÓ SIN USO", 0.2, 0.86, 58)], tex=ARCH)
    add(875.12, V("43603", "u_49TfEiFhWGI.jpg", 0.0, "doc"), [big("Y ESTA VEZ, UN DESTINO TODAVÍA MÁS EXTRAÑO", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)
    add(878.5, cus(G13.drown, t0=0.8), tr="fade", td=0.2, tex=GFX)
    add(890.86, L("22649", kb(pick("m_13361680.jpg", F(7506439740)), "in", "doc"), "Pyramid Lake · Carol M. Highsmith · " + CAP_LOC),
        [BigText("PYRAMID LAKE", "serif", 120, WHITE, (0.5, 0.14), 0.3, None, "up")], tex=CLEAN)
    add(893.12, V("4996", "u_PUOQLdE0T6w.jpg", 0.0, "doc"), [big("HOY SE PESCA Y SE NAVEGA EN LANCHA", 0.1, 0.86, 66)], tex=CLEAN)
    add(897.06, kb(pick(F(7506439740), "m_13361680.jpg"), "in", "doc"), [Darken(0.25), big("BAJO SUS AGUAS: EL ASFALTO DE LOS AÑOS 40", 0.2, 0.12, 60, BLUE_),
                                                                        big("CASI NADIE SABE QUE ESTÁ AHÍ", w("y casi", 901.8) - 897.06, 0.86, 66)], tex=CLEAN)
    t0 = 903.98
    add(t0, mp("rr_loc", [(0, -118.775, 34.65, 1.4)],
               [dict(type="route", ll=US99, t0=0.0, draw=0.2, color=GREEN_, width=6, dash=16),
                dict(type="pin", at="rr_pyramid_rock", t0=0.4, label="PYRAMID ROCK", side="r", box=True, size=44),
                dict(type="label", at=(-118.80, 34.675), text="PYRAMID LAKE", t0=0.8, size=44, color=BLUE_)]),
        [big("EL ÚNICO TESTIGO DE LO QUE HAY DEBAJO", w("como el", 911.1) - t0, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(913.56, kb(pick(F(5119977535), "u_IVajGOKvs7c.jpg"), "in", "doc"), [big("EL LAGO GUARDA OTRA IRONÍA", 0.1, 0.86, 70)], tex=CLEAN)
    t0 = 915.54
    add(t0, mp("rr_reg", [(0, -119.3, 35.3, 0.9), (8.0, -118.9, 34.9, 0.95)],
               [dict(type="route", ll=AQUEDUCT, t0=w("forma", 917.8) - t0, draw=4.0, color=BLUE_, width=7, traffic=4, speed=120),
                dict(type="label", at=(-119.6, 35.95), text="DEL NORTE DE CALIFORNIA", t0=w("del norte", 919.2) - t0, size=40, box=True),
                dict(type="pin", at="rr_pyramid_lake", t0=1.0, label="PYRAMID LAKE", side="l", box=True, size=38),
                dict(type="pin", at="rr_la", t0=w("los ángeles", 923.0) - t0, label="LOS ÁNGELES", side="r", box=True, size=38)]),
        [big("EL GRAN ACUEDUCTO DE CALIFORNIA", 0.3, 0.1, 62, BLUE_)], tr="zoom", td=0.3, tex=GFX)
    add(923.94, L("24058", kb("u_YPcoGp--Gh0.jpg", "in", "doc"), "El Acueducto de California · Carol M. Highsmith · " + CAP_LOC),
        [big("SIGUE UNIENDO LAS DOS MITADES DEL ESTADO", 0.2, 0.86, 62, YELLOW)], tex=CLEAN)
    add(929.82, kb("u_R06WzhBJzog.jpg", "in", "doc"), [big("AHORA LO QUE CRUZA LAS MONTAÑAS ES AGUA", 0.1, 0.12, 60, BLUE_),
                                                      big("NO CAMIONES POR 697 CURVAS", w("y no", 932.6) - 929.82, 0.86, 66)], tex=CLEAN)
    add(936.8, kb("u_YPcoGp--Gh0.jpg", "in", "doc"), [big("UNA CARRETERA QUE NADIE VE SIGUE CUMPLIENDO SU MISIÓN", 0.2, 0.86, 54, YELLOW)], tex=CLEAN)
    add(940.42, cus(G13.layers, t0=w("arriba", 942.6) - 940.42, step=w("abajo", 948.5) - w("arriba", 942.6)), tr="fade", td=0.2, tex=GFX)
    add(956.12, cus(G13.layers, t0=-9), [big("TRES CARRETERAS PARA EL MISMO VIAJE", 0.1, 0.1, 62, YELLOW), big("EN CAPAS, COMO UN PASTEL", w("en capas", 958.3) - 956.12, 0.2, 54)],
        tex=GFX)
    add(960.58, kb(OLD1, "in", "doc"), [big("LA PRIMERA SIGUE A LA VISTA", 0.0, 0.3, 76), big("LA ÚNICA QUE TODAVÍA PUEDES PISAR", w("y es", 962.3) - 960.58, 0.86, 66, YELLOW)],
        tex=CLEAN)

    # ============================== CAP 8: HOY (965.4 - 1069.8)
    bg, ov = chapter(8, "LA CARRETERA OLVIDADA", F(55646069796), g="doc", year="1933–2025")
    add(965.42, bg, ov, tr="black", td=0.2, tex=DARK)
    add(967.54, kb(F(55646268819), "in", "doc"), [big("UN CAMINO OLVIDADO", 0.1, 0.86, 80)], tex=CLEAN)
    add(970.38, kb("u_UnYe2ixjDsE.jpg", "in", "doc"), [big("CAMINOS DE SERVICIO…", 0.1, 0.3, 70), big("…Y TRAMOS CERRADOS EN EL BOSQUE NACIONAL ANGELES", w("y otras", 972.9) - 970.38, 0.86, 54, YELLOW)],
        tex=CLEAN)
    add(976.02, kb("u_2bIF4cEJT4M.jpg", "in", "doc"), [Stamp("CERRADA A LOS AUTOS", 0.2, RED_, (0.5, 0.5), -8, 100)], tex=CLEAN)
    add(977.6, kb("u_l2RPhWg31ro.jpg", "in", "cold"), [big("CASI SEIS DÉCADAS EN SILENCIO", 0.2, 0.86, 70)], tex=DARK)
    add(981.24, cus(_card, lines=[("1991", 110, YELLOW, 0.3, 0.1), ("HARRISON SCOTT", 110, WHITE, 0.48, w("harrison", 985.0) - 981.24),
                                  ("INGENIERO JUBILADO · LA RECORRIÓ CON SU HIJO", 50, GREY_, 0.64, w("harrison", 985.0) - 981.24 + 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(988.18, kb(F(5590800823), "in", "doc"), [big("DECIDIÓ SALVARLA", 0.5, 0.86, 90, YELLOW, "pop")], tex=CLEAN)
    add(991.38, V("10395", "u_KPHhnz-3iI0.jpg", 0.0, "warm"), [big("6 AÑOS PELEANDO CON PAPELES Y OFICINAS", 0.1, 0.86, 62)], tex=DARK)
    add(994.34, kb(OLD1, "in", "doc"), [Darken(0.4), Badge("SEPTIEMBRE DE 1997", 0.1, None),
                                        Counter(0, 17.6, "{:.1f} MILLAS", "EN EL REGISTRO NACIONAL DE LUGARES HISTÓRICOS", w("17", 997.2) - 994.34, 1.0, (0.5, 0.44), 150, color=YELLOW)],
        tex=CLEAN)
    add(1002.56, cus(_card, lines=[("UN LIBRO SOBRE ELLA", 66, WHITE, 0.36, 0.1), ("2008", 110, YELLOW, 0.52, w("2008", 1005.2) - 1002.56),
                                   ("HITO HISTÓRICO DE CALIFORNIA (INGENIEROS CIVILES)", 50, GREY_, 0.66, w("2008", 1005.2) - 1002.56 + 0.4)]), tr="fade", td=0.2, tex=GFX)
    add(1009.28, kb(F(5591392068), "in", "doc"), [big("PERO DECLARARLA HISTÓRICA NO LA ABRIÓ", 0.1, 0.86, 64, RED_)], tex=CLEAN)
    add(1011.94, kb("u_1Ym4Hrk77L4.jpg", "in", "dark"), [Badge("2005", 0.1, None), big("LLUVIAS MUY FUERTES LA DAÑAN", 0.5, 0.86, 70)], tex=DARK)
    add(1015.18, kb("u_IdaRwQkKptc.jpg", "in", "doc"), [big("SE REPARÓ… Y SIGUIÓ CERRADA", 0.2, 0.86, 72, YELLOW)], tex=CLEAN)
    add(1020.2, kb("u_txUQ3hFbPlg.jpg", "in", "doc"), [big("JORNADAS DE VOLUNTARIOS", 0.2, 0.86, 76)], tex=CLEAN)
    add(1024.66, Split([kb("u_z3eqDS6P0Dk.jpg", "in", "doc"), W_("tamping1915", kb("u_DvQ3xYWObr8.jpg", "in", "archival"), None)], labels=["HOY", "1915"]),
        [big("PALAS Y RASTRILLOS, COMO LAS CUADRILLAS DE 1915", 0.2, 0.08, 54)], tex=CLEAN)
    add(1029.0, kb("u_B-JJxUzeX3M.jpg", "in", "doc"), [big("PIEDRAS · RAMAS · TIERRA", 0.2, 0.86, 76)], tex=CLEAN)
    add(1032.7, kb("u_eKY6_9W_iqY.jpg", "in", "doc"), [Badge("2025", 0.1, None), big("UNA COMPAÑÍA DE GAS SE OFRECE A TAPAR BACHES", 0.6, 0.12, 56),
                                                      big("UNAS 6 MILLAS", w("de unas", 1039.4) - 1032.7, 0.86, 80, YELLOW)], tex=CLEAN)
    add(1040.72, kb("u_sBYGD7Zgkbk.jpg", "in", "dark"), [Badge("NOVIEMBRE DE 2025", 0.1, None), big("OTRA GRAN TORMENTA", 0.6, 0.38, 80),
                                                        big("Y OTRA VEZ, A PEDIR MANOS", w("y la", 1044.2) - 1040.72, 0.54, 66, YELLOW)], tex=DARK)
    add(1047.3, kb(F(55646268819), "in", "doc"), [big("SI SUBES HASTA DONDE SE PUEDE…", 0.1, 0.86, 66)], tex=CLEAN)
    add(1049.16, W_("curb", kb("u_TGDATKr4CLg.jpg", "in", "doc"), "Bordillo de concreto de la Ridge Route · " + WM),
        [big("EL CONCRETO ORIGINAL DE HACE UN SIGLO", 0.1, 0.86, 64, YELLOW)], tex=CLEAN)
    add(1051.9, kb("u_yd5ZyiRRpa8.jpg", "in", "doc"), [big("GRIETAS Y HIERBAS", 0.0, 0.3, 76), big("PERO CON SU FORMA DE SIEMPRE", w("pero", 1053.7) - 1051.9, 0.86, 66)], tex=CLEAN)
    add(1055.92, W_("guardrail", kb("u_sZOyrl0HSX4.jpg", "in", "doc"), "Restos de la Ridge Route · " + WM), [big("MUROS DE CONTENCIÓN", 0.0, 0.86, 80)], tex=CLEAN)
    add(1057.76, kb("u_RR7KxUAuYPY.jpg", "in", "doc"), [big("CUNETAS POR DONDE CORRÍA EL AGUA", 0.0, 0.86, 70)], tex=CLEAN)
    add(1059.96, W_("turnout", kb(F(51784212538), "in", "doc"), "La Ridge Route hoy · " + WM), [big("BORDES DE CONCRETO QUE MARCABAN LAS CURVAS", 0.0, 0.86, 62)], tex=CLEAN)
    add(1062.84, W_("tumble_step", kb("u_SZwTEno2Eyo.jpg", "in", "doc"), None),
        [big("ESCALONES DE LAS VIEJAS POSADAS", 0.4, 0.12, 66), big("QUE HOY SUBEN HACIA LA NADA", w("que hoy", 1067.7) - 1062.84, 0.86, 70, YELLOW)], tex=CLEAN)

    # ============================== CONCLUSIÓN (1069.8 - 1131.7)
    q2(1069.76, badge="DE VUELTA A LA PREGUNTA 2")
    add(1077.92, cus(_card, lines=[("PORQUE SE HIZO CON LO ÚNICO QUE HABÍA EN 1914", 54, WHITE, 0.4, 0.1)]), tex=GFX)
    add(1082.18, kb("u_6x6bV7QN3GQ.jpg", "punch", "doc"), [big("PALAS", 0.0, 0.3, 100, WHITE, "pop"), big("CABALLOS", 0.54, 0.46, 100, WHITE, "pop")], tex=CLEAN)
    add(1083.26, kb(F(48342186127), "punch", "doc"), [big("LA CRESTA DE UNA MONTAÑA", 0.2, 0.86, 84, YELLOW, "pop")], tex=CLEAN)
    add(1085.48, mp("rr_reg", [(0, -118.65, 34.75, 0.95)],
                    [dict(type="pin", at="rr_la", t0=0.0, label="LOS ÁNGELES", side="r", box=True, size=38),
                     dict(type="pin", at="rr_bakersfield", t0=0.0, label="BAKERSFIELD", side="r", box=True, size=38),
                     dict(type="route", ll=RIDGE_FULL, t0=0.2, draw=1.2, color=CONC, width=7)]),
        [big("FUNCIONÓ: UNIÓ CALIFORNIA POR PRIMERA VEZ", 0.2, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(1088.56, kb("u_eIj8K5dHyIY.jpg", "in", "doc"), [big("LLEGARON LAS MÁQUINAS…", 0.0, 0.3, 72), big("…Y LA DEJARON ARRIBA, SOLA", w("el estado", 1090.3) - 1088.56, 0.86, 72, YELLOW)],
        tex=CLEAN)
    add(1094.12, kb(OLD1, "out", "doc"), [big("COLGADA DE LA MONTAÑA", 0.2, 0.86, 76)], tex=CLEAN)
    add(1097.54, cus(G13.bonds, t0=-9, use_t=-9, end_t=0.3), [big("Y DURANTE DÉCADAS, EL ESTADO LA SIGUIÓ PAGANDO", 0.1, 0.12, 52, YELLOW)], tex=GFX)
    add(1100.72, cus(G13.layers, t0=-9), [big("CADA CARRETERA SE TRAGÓ A LA ANTERIOR", 0.1, 0.1, 60, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(1104.6, kb(F(55646069796), "in", "doc"), [big("SOLO LA PRIMERA SIGUE A LA VISTA", 0.1, 0.86, 70, YELLOW)], tex=CLEAN)
    add(1106.76, cus(G13.climb, mode="down", t0=-3.0), [Darken(0.45), rich("¿TE HABRÍAS ATREVIDO A BAJAR LA RIDGE ROUTE EN UN AUTO DE 1920?", ("atrevido", "1920?"),
                                                                            w("tú", 1108.3) - 1106.76, step=0.08, y=0.42, size=64, maxw=0.82),
                                                        big("SIN BARANDAS · CON LOS FRENOS ECHANDO HUMO", w("sin", 1113.6) - 1106.76, 0.62, 56, RED_)], tex=GFX)
    add(1115.6, kb(OLD1, "out", "doc"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿TE HABRÍAS ATREVIDO A BAJAR LA RIDGE ROUTE", line2="EN UN AUTO DE 1920?", cta="TE LEO EN LOS COMENTARIOS")], tex=DARK)
    add(1117.64, kb(F(55646484600), "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe),
                                                           big("MENOS CURVAS QUE LA RIDGE ROUTE · NINGUNA MULTA", w("te prometo", 1122.6) - 1117.64, 0.14, 50, YELLOW)], tex=DARK)
    add(1127.4, kb(F(3869990146), "in", "doc"), [big("LA PRÓXIMA VEZ QUE SUBAS EL GRAPEVINE…", 0.1, 0.86, 64)], tex=CLEAN)
    add(w("mira", 1129.7), kb(OLD1, "out", "doc"), [big("MIRA HACIA LA CRESTA", 0.0, 0.42, 84), big("AHÍ SIGUE", w("ahí", 1130.9) - w("mira", 1129.7), 0.58, 110, YELLOW, "pop")],
        tex=CLEAN)
    return S


def pick_w(name, fallback, cap):
    f = f"w_{name}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, "archival")
    return fallback


def pick_f(fid, fallback, cap):
    f = f"f_{fid}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, "archival")
    return fallback


def pick_l(lid, fallback, cap):
    return L(lid, fallback, cap)
