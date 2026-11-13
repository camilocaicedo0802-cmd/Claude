"""The edit: every shot of the Natchez Trace video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx11 as G11
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1193.90
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






# ------------------------------------------------------------------ Natchez Trace specifics
import json as _json

_R = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nt_route.json")))
_SC = 444.0 / _R["mi"][-1]          # official mileposts vs measured centreline


def route(m0=0.0, m1=444.0):
    """Lon/lat polyline of the parkway between two official mileposts (NPS boundary centreline)."""
    out = [p for p, mi in zip(_R["ll"], _R["mi"]) if m0 <= mi * _SC <= m1]
    return [tuple(p) for p in out]


def mp_at(m):
    import numpy as _np
    mi = _np.array(_R["mi"]) * _SC
    i = int(_np.searchsorted(mi, m))
    i = min(max(i, 0), len(mi) - 1)
    return tuple(_R["ll"][i])


PARK = route()
OHIO_DOWN = ["pittsburgh_nt", (-80.6, 40.6), (-81.6, 39.4), (-82.6, 38.6), "cincinnati_oh", (-85.0, 38.7), "louisville_ky",
             (-86.6, 37.9), (-88.0, 37.8), "cairo_il", (-89.6, 36.5), "memphis", (-90.6, 34.6), (-91.1, 33.2), "vicksburg", "natchez",
             (-91.4, 31.0), (-91.1, 30.5), "new_orleans"]
KY_UP = ["natchez", "lexington_ky"]
MIL_ROAD = ["nashville_tn", (-87.03, 35.61), "florence_al", (-88.15, 34.0), "columbus_ms", (-89.0, 32.4), (-89.7, 31.2),
            "madisonville_la", "new_orleans"]


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="u_GkpFUHXM0xo.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Por qué hicieron falta 67 años para una carretera de dos carriles?", ("67",), size=72),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_UIWMt5r1jeQ.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Y por qué en 444 millas no se vende ni un galón de gasolina?", ("444", "gasolina?"), size=72),
            tr="glitch", td=0.3, tex=DARK)

    NT = lambda m, **kw: cus(G11.__dict__[m], **kw)
    HS = "Carol M. Highsmith · Library of Congress"

    # ============================== INTRO (0 - 73.0)
    add(0.0, kb("w_highsmith.jpg", "in", "doc"), [rich("VAS MANEJANDO POR UN BOSQUE DE MISSISSIPPI", ("mississippi",), 0.3, y=0.86, size=58)],
        tex=CLEAN)
    add(w("y llevas", 3.2), kb("l_42697.jpg", "in", "doc"), [big("HORAS SIN VER UN CAMIÓN", 0.2, 0.86, 72, YELLOW)], tex=CLEAN)
    add(5.8, cus(G11.rules, times=[-1, w("cartel", 9.3) - 5.8, w("gasolinera", 6.8) - 5.8, w("semáforo", 8.2) - 5.8, 99], speed_t=99),
        tr="fade", td=0.2, tex=GFX)
    add(10.1, V("100333", "l_42698.jpg", 0.0, "doc"), [big("DOS CARRILES VACÍOS", 0.1, 0.86, 72)], tex=CLEAN)
    add(w("y un", 12.4), V("100233", "l_04384.jpg", 0.0, "doc"), [big("LÍMITE: 50 MILLAS POR HORA", 0.1, 0.86, 72, YELLOW),
                                                                big("QUE AQUÍ NADIE SE SALTA", w("que aquí", 15.1) - w("y un", 12.4), 0.14, 60)], tex=CLEAN)
    add(17.1, cus(G11.fuel, t0=0.2), [big("¿DÓNDE CARGAR?", 1.6, 0.14, 72, YELLOW)], tr="fade", td=0.2, tex=DARK)
    add(21.3, kb("f_2324968747.jpg", "in", "doc"), [big("TE ORILLAS", 0.0, 0.86, 80)], tex=CLEAN)
    add(22.6, V("2728", "u_FnaiTxmOHhA.jpg", 0.0, "doc"), [big("UNOS PASOS ENTRE LOS ÁRBOLES…", 0.1, 0.86, 66)], tex=CLEAN)
    add(w("y el suelo", 24.6), kb("w_grindstone.jpg", "punch", "doc"), [big("…Y EL SUELO SE ABRE", 0.0, 0.86, 80, YELLOW, "pop")], tex=CLEAN)
    add(26.3, kb("f_44238521561.jpg", "in", "doc"), [big("UNA ZANJA MÁS ALTA QUE TÚ", 0.1, 0.86, 72)], tex=CLEAN)
    add(28.3, kb("f_37063709992.jpg", "up", "doc"), [big("RAÍCES COLGANDO DE LAS PAREDES", 0.1, 0.86, 66)], tex=CLEAN)
    add(31.3, kb("f_43332777955.jpg", "in", "doc"), [big("NO LA HIZO NINGUNA MÁQUINA", 0.1, 0.86, 70)], tex=CLEAN)
    add(33.0, kb("u_J34M8K1uqs4.jpg", "in", "doc"), [big("PISADA A PISADA", w("pisada", 34.2) - 33.0, 0.86, 84, YELLOW, "pop")], tex=CLEAN)
    add(35.7, cus(G11.sunken, t0=0.0, deep_d=3.8, yrs=(1790, 1830), person=False), [big("MILES DE HOMBRES QUE VOLVÍAN A CASA", 0.1, 0.1, 60)],
        tr="fade", td=0.2, tex=GFX)
    add(39.7, kb("f_36421185033.jpg", "in", "doc"), [Darken(0.35), BigText("THE NATCHEZ TRACE", "serif", 112, WHITE, (0.5, 0.48), 0.3, None, "up"),
                                                    big("«LO LLAMABAN»", 0.1, 0.36, 50, GREY_)], tr="fade", td=0.3, tex=CLEAN)
    add(42.5, mp("nt_us", [(0, -89.5, 33.8, 0.85), (5.8, -89.0, 33.8, 1.0)],
                 [dict(type="route", ll=PARK, t0=0.3, draw=3.0, color=YELLOW, width=6),
                  dict(type="pin", at="natchez", t0=0.2, label="NATCHEZ", side="l", box=True, size=40),
                  dict(type="pin", at="nashville_tn", t0=2.6, label="NASHVILLE", side="r", box=True, size=40)]),
        [Counter(0, 67, "{:.0f} AÑOS", "PARA CONSTRUIR LA CARRETERA", w("67", 45.8) - 42.5, 1.2, (0.5, 0.2), 120)], tr="zoom", td=0.3, tex=GFX)
    add(48.8, pick_l("09868", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Jeff Busby · " + LOC_),
        [big("EL HOMBRE QUE LA PROPUSO MURIÓ ESPERÁNDOLA", 0.2, 0.08, 56, YELLOW)], tex=ARCH)
    add(w("y hoy", 51.7), kb("u_Rj7sPIb4LY0.jpg", "punch", "dark"), [Badge("2026", 0.2, None),
                                                                   big("OTRA VEZ NO SE PUEDE RECORRER ENTERA", 0.4, 0.86, 62, RED)], tex=DARK)
    add(56.0, kb("u_gCz68Y5kEuM.jpg", "in", "warm"), [big("HAY CAMINOS QUE SE HACEN PARA LLEGAR…", 0.2, 0.42, 66),
                                                     big("ESTE SE HIZO PARA NO TENER PRISA", w("este", 58.7) - 56.0, 0.58, 76, YELLOW)], tex=CLEAN)
    q1(61.8)
    q2(67.0)

    # ============================== CAP 1: LA SENDA Y LOS KAINTUCKS (73.0 - 213.1)
    bg, ov = chapter(1, "LA SENDA Y LOS KAINTUCKS", "f_44238514641.jpg", year="ANTES DE 1810")
    add(73.0, bg, ov, tr="black", td=0.2, tex=DARK)
    add(76.9, kb("u_F0DkWW9sfK0.jpg", "l", "doc"), [big("LA ABRIERON LOS BISONTES…", 0.1, 0.86, 70)], tex=CLEAN)
    add(w("y los", 77.9), kb("u_gj4PFH15pjw.jpg", "in", "doc"), [big("…Y LOS CIERVOS", 0.0, 0.86, 76)], tex=CLEAN)
    add(80.1, mp("nt_reg", [(0, -89.0, 33.8, 0.62), (7.1, -88.0, 34.6, 0.72)],
                 [dict(type="route", ll=PARK[::-1], t0=0.3, draw=4.0, color=(200, 170, 110), width=5, dash=16),
                  dict(type="pin", at="nashville_tn", t0=0.6, label="SALINAS (HOY NASHVILLE)", side="r", box=True, size=38),
                  dict(type="pin", at="natchez", t0=0.2, label="MISSISSIPPI", side="l", box=True, size=38),
                  dict(type="label", at=(-88.3, 34.2), text="POR LAS CRESTAS", t0=w("iban", 83.1) - 80.1, dx=180, size=46, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(87.2, kb("u_RU3DtnbuHaA.jpg", "in", "dark"), [big("DETRÁS, LOS PUEBLOS NATIVOS", 0.1, 0.86, 70)], tex=DARK)
    add(90.6, kb(pick("w_pharr.jpg", "f_37045369346.jpg"), "in", "doc"), [Badge("CERCA DE TUPELO", 0.2, None),
                                                                         Counter(0, 2000, "{:,.0f} AÑOS", "MONTÍCULOS FUNERARIOS", w("hay", 92.7) - 90.6, 1.2,
                                                                                 (0.5, 0.42), 150)], tex=CLEAN)
    add(95.8, kb("u_x_XUgMfGISk.jpg", "in", "warm"), [big("UN JEFE CHICKASAW LO USABA TANTO…", 0.2, 0.86, 62)], tex=CLEAN)
    add(w("el camino", 102.4) - 0.2, Solid("dark_grid"), [BigText("«EL CAMINO DE PIOMINGO»", "serif", 100, YELLOW, (0.5, 0.5), 0.2, None, "pop")], tex=GFX)
    add(104.4, pick_w("survey_1809", kb("u_DD0fKMPg8ZA.jpg", "in", "warm"), "Levantamiento del Natchez Trace, c. 1800 · " + WM),
        [big("LOS EUROPEOS TARDARON EN CONOCERLA", 0.2, 0.08, 58)], tex=ARCH)
    add(110.1, kb("u_hjwKMkehBco.jpg", "in", "warm"), [Badge("1742", 0.1, None), big("UN FRANCÉS LA RECORRE ENTERA", 0.3, 0.86, 64)], tex=CLEAN)
    add(113.4, kb("u_QdRnZlzYJPA.jpg", "in", "dark"), [big("NO DIJO SU NOMBRE…", 0.1, 0.42, 70),
                                                     BigText("«CONDICIONES MISERABLES»", "serif", 88, YELLOW, (0.5, 0.58), w("habló", 116.6) - 113.4, None, "up")],
        tex=DARK)
    add(119.0, kb("u_9-jsuoR1drI.jpg", "in", "warm"), [big("MEDIO SIGLO DESPUÉS…", 0.1, 0.86, 70)], tex=CLEAN)
    add(124.0, mp("nt_us", [(0, -84.0, 39.0, 0.9), (6.3, -84.0, 39.0, 0.95)],
                  [dict(type="state", name="Kentucky", t0=0.0, color=YELLOW, width=3, alpha=0.7),
                   dict(type="state", name="Ohio", t0=0.3, color=YELLOW, width=3, alpha=0.7),
                   dict(type="state", name="Pennsylvania", t0=0.6, color=YELLOW, width=3, alpha=0.7)]),
        [big("GRANJEROS SIN CÓMO VENDER SU COSECHA POR TIERRA", w("que no", 127.1) - 124.0, 0.1, 54)], tr="zoom", td=0.3, tex=GFX)
    add(130.3, pick_w("flatboat_waud", L("14306", kb("u_-4r9zYqtrug.jpg", "in", "doc"), "Hombres en una balsa plana con barriles · 1830 · " + LOC_),
                     "Viaje en balsa plana · grabado de Alfred R. Waud · " + WM),
        [big("UNA BALSA PLANA: UNA CAJA DE MADERA GIGANTE", w("poco", 132.3) - 130.3, 0.08, 54, YELLOW)], tex=ARCH)
    add(135.6, kb("u_NqsjraL0GLc.jpg", "punch", "warm"), [big("TABACO", 0.0, 0.86, 92, WHITE, "pop")], tex=CLEAN)
    add(w("harina", 136.7), kb("u_6v5wsYTxtBQ.jpg", "punch", "warm"), [big("HARINA", 0.0, 0.86, 92, WHITE, "pop")], tex=CLEAN)
    add(w("carne", 137.4), kb("u_j7lJlpwowOs.jpg", "punch", "warm"), [big("CARNE SALADA", 0.0, 0.86, 92, WHITE, "pop")], tex=CLEAN)
    add(w("barriles", 138.3), kb("u_VQRmSYDTDjs.jpg", "punch", "warm"), [big("WHISKY", 0.0, 0.86, 92, WHITE, "pop")], tex=CLEAN)
    add(139.6, mp("nt_us", [(0, -82.0, 38.5, 0.82), (6.7, -88.5, 33.5, 0.82)],
                  [dict(type="route", path=OHIO_DOWN, t0=0.3, draw=6.0, color=(110, 170, 220), width=7),
                   dict(type="pin", at="pittsburgh_nt", t0=0.1, label="EL OHIO", side="r", box=True, size=36),
                   dict(type="label", at="memphis", text="EL MISSISSIPPI", t0=w("luego", 144.7) - 139.6, dx=-200, size=42, box=True)]),
        [big("RÍO ABAJO, DURANTE SEMANAS", 0.2, 0.1, 62)], tr="zoom", td=0.3, tex=GFX)
    add(146.3, mp("nt_us", [(0, -90.8, 31.0, 1.4), (4.9, -90.6, 30.7, 1.6)],
                  [dict(type="pin", at="natchez", t0=0.2, label="NATCHEZ", side="r", box=True, size=40),
                   dict(type="pin", at="new_orleans", t0=w("nueva", 148.6) - 146.3, label="NUEVA ORLEANS", side="r", box=True, size=40)]),
        [big("AL FINAL DEL VIAJE: VENDÍAN TODO", w("vendían", 149.8) - 146.3, 0.1, 60, YELLOW)], tex=GFX)
    add(151.2, pick_w("jolly", L("01064", kb("u_-4r9zYqtrug.jpg", "in", "doc"), "«The jolly flat boat men», según George Caleb Bingham · 1847 · " + LOC_),
                     "«The Jolly Flatboatmen», George Caleb Bingham, 1846 · " + WM),
        [big("LA CARGA… Y TAMBIÉN LA BALSA", 0.2, 0.08, 62), big("SE DESARMABA PARA APROVECHAR LA MADERA", w("que se", 153.5) - 151.2, 0.92, 52, YELLOW)],
        tex=ARCH)
    add(156.3, kb("u_hZhWQipJ-Lg.jpg", "in", "warm"), [big("PIENSA EN LO QUE VENÍA DESPUÉS", 0.1, 0.86, 66)], tex=CLEAN)
    add(158.4, L("4a24301", kb("f_44261142351.jpg", "in", "doc"), "Natchez, «bajo la colina», y el Mississippi · c. 1910 · " + LOC_),
        [big("UN PUEBLO SOBRE UN ACANTILADO", 0.2, 0.08, 62)], tex=ARCH)
    add(160.8, kb("u_iLpyO-jq4lM.jpg", "in", "dark"), [big("EL DINERO DE TODO UN AÑO", 0.1, 0.36, 72, YELLOW),
                                                     big("COSIDO EN EL FORRO DEL ABRIGO", 0.8, 0.52, 64, WHITE)], tex=DARK)
    add(164.3, pick_w("under_hill_bahin", L("4a32715", kb("f_43355888575.jpg", "in", "doc"), "Natchez Under-the-Hill · " + LOC_),
                      "Natchez Under-the-Hill · Louis Joseph Bahin · " + WM),
        [BigText("NATCHEZ UNDER-THE-HILL", "bebas", 84, YELLOW, (0.5, 0.1), w("natchez", 167.6) - 164.3, None, "up", tracking=6)], tex=ARCH)
    add(169.8, kb("u_D4baoYDCajw.jpg", "in", "dark"), [big("TABERNAS", 0.0, 0.42, 84, WHITE, "pop"),
                                                     big("APUESTAS · PELEAS", w("sus apuestas", 171.3) - 169.8, 0.58, 72, YELLOW, "pop")], tex=DARK)
    add(173.9, kb("u_K0l4GwGX-Ec.jpg", "in", "dark"), [big("MEJOR NO QUEDARSE MUCHO", 0.1, 0.86, 70)], tex=DARK)
    add(175.8, cus(G11.flatboat, mode="up", back_t=0.3), [big("Y NO HAY BARCO QUE VAYA EN ESA DIRECCIÓN", w("y no", 181.6) - 175.8, 0.92, 52, RED)],
        tr="fade", td=0.2, tex=GFX)
    add(184.1, cus(G11.treadmill, t0=0.2), tr="fade", td=0.2, tex=GFX)
    bg, ov = card([("EN EL SUR LES PUSIERON A TODOS EL MISMO APODO", 50, GREY_, 0.34, 0.1), ("«KAINTUCKS»", 170, YELLOW, 0.52, w("keintux", 196.1) - 191.4 - 0.2),
                   ("FUERAN DE DONDE FUERAN", 56, WHITE, 0.7, w("fueran", 194.6) - 191.4)])
    add(191.4, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(197.4, kb("u_LpSDKz6dUyY.jpg", "in", "cold"), [Badge("HACIA 1810", 0.1, None),
                                                     Counter(0, 10000, "{:,.0f}", "AL AÑO VOLVÍAN AL NORTE", 0.3, 1.2, (0.5, 0.4), 170)], tex=CLEAN)
    add(203.0, kb("u_9sYijleVWq0.jpg", "in", "warm"), [big("A PIE O A CABALLO · 2 A 3 SEMANAS", 0.1, 0.86, 64)], tex=CLEAN)
    add(206.6, kb("f_42430605240.jpg", "in", "doc"), [big("UN CAMINO DE VUELTA A CASA…", 0.1, 0.86, 70),
                                                    big("…Y PRONTO, DEL GOBIERNO", w("y muy", 208.6) - 206.6, 0.14, 66, YELLOW)], tex=CLEAN)

    # ============================== CAP 2: EL CAMINO DEL GOBIERNO (213.1 - 350.2)
    bg, ov = chapter(2, "EL CAMINO DEL GOBIERNO", "w_survey_1809.jpg", g="archival", year="1801–1810")
    add(213.1, bg, ov, tr="black", td=0.2, tex=DARK)
    add(w("los chickasaw", 218.0) - 0.2, mp("nt_reg", [(0, -89.2, 33.5, 0.62), (5.0, -89.0, 33.6, 0.66)],
                                              [dict(type="route", ll=PARK, t0=0.0, draw=0.1, color=(200, 170, 110), width=5, dash=16),
                                               dict(type="label", at=(-88.7, 34.3), text="CHICKASAW", t0=0.2, size=58, box=True),
                                               dict(type="label", at=(-89.6, 32.6), text="CHOCTAW", t0=0.6, size=58, box=True)]),
        [big("PERMISO PARA ABRIR UN CAMINO POR SUS TIERRAS", w("el permiso", 220.3) - 218.0 + 0.2, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(222.9, pick_w("jefferson", L("31800", kb("u_hjwKMkehBco.jpg", "in", "warm"), "Thomas Jefferson · 1805 · " + LOC_), "Thomas Jefferson · Rembrandt Peale, 1800 · " + WM),
        [LowerThird("THOMAS JEFFERSON", "Presidente, 1801–1809", 0.4), big("UNA GRAN RUTA POSTAL HACIA EL MISSISSIPPI", 0.6, 0.08, 54)], tex=ARCH)
    add(227.3, kb("w_survey_1809.jpg", "in", "archival"), [Darken(0.3), BigText("«COLUMBIAN HIGHWAY»", "serif", 100, YELLOW, (0.5, 0.5), 0.6, None, "pop"),
                                                           big("EL NOMBRE QUE JEFFERSON TENÍA PENSADO", 0.2, 0.34, 50, WHITE)], tex=ARCH)
    add(231.9, kb("u_o2-rI5me4QQ.jpg", "in", "cold"), [big("EL EJÉRCITO A ENSANCHARLA", 0.1, 0.86, 68)], tex=CLEAN)
    add(234.4, V("22731", "u_mI-QcAP95Ok.jpg", 0.0, "warm"), [big("TALARON ÁRBOLES", 0.1, 0.86, 72),
                                                            big("TRONCOS SOBRE LOS ARROYOS", w("pusieron", 235.9) - 234.4, 0.14, 66, YELLOW)], tex=CLEAN)
    add(239.9, kb("u_Zu9U98JjuWQ.jpg", "in", "warm"), [Badge("1809", 0.1, None), big("YA PODÍAN PASAR CARRETAS", 0.3, 0.86, 70)], tex=CLEAN)
    add(243.4, kb("u_oathFTcFigc.jpg", "in", "warm"), [big("EL CORREO SALÍA DE NASHVILLE", 0.1, 0.86, 66),
                                                     big("LOS SÁBADOS POR LA NOCHE", w("los sábados", 245.3) - 243.4, 0.14, 60, YELLOW)], tex=CLEAN)
    add(247.2, cus(G11.bars, rows=[("1809, A CABALLO", 240, "10 DÍAS", (200, 200, 206)), ("HOY, EN CARRO", 9, "9 HORAS", (90, 190, 110))],
                   title="NASHVILLE → NATCHEZ", times=[0.2, w("hoy", 250.2) - 247.2]), tr="fade", td=0.2, tex=GFX)
    add(w("te llevaría", 253.7), kb("l_42698.jpg", "in", "doc"), [big("HOY: UNAS 9 HORAS", 0.0, 0.86, 76, YELLOW),
                                                                big("SIN PISAR EL ACELERADOR", 0.9, 0.14, 62)], tex=CLEAN)
    add(258.0, kb("u_5Lkw26URfiQ.jpg", "in", "warm"), [big("10 DÍAS DE CAMINO NECESITAN DÓNDE DORMIR", 0.1, 0.86, 60)], tex=CLEAN)
    add(261.4, L("42683", kb("u_dm6grquJR7M.jpg", "in", "doc"), "Mount Locust, la única posada que sobrevive · " + HS),
        [BigText("«STANDS»", "serif", 110, YELLOW, (0.5, 0.12), w("stands", 264.2) - 261.4, None, "pop"),
         big("UNAS 40 A LO LARGO DE LA SENDA", w("llegaron", 266.3) - 261.4, 0.2, 56)], tex=CLEAN)
    add(268.0, kb("u_azZm4fh8uzc.jpg", "in", "dark"), [big("NO TE IMAGINES UN HOTEL", 0.1, 0.86, 72)], tex=DARK)
    add(269.9, cus(G11.stand_menu, times=[w("cémola", 271.8) - 269.9 - 0.2, w("tocino", 274.1) - 269.9, w("galletas", 274.8) - 269.9,
                                          w("café", 275.6) - 269.9, w("un trago", 276.2) - 269.9], sleep_t=99),
        tr="fade", td=0.2, tex=GFX)
    add(277.9, kb("u_1vcib_vJNdo.jpg", "in", "dark"), [big("DORMÍAS EN EL SUELO, JUNTO A DESCONOCIDOS", 0.1, 0.86, 60)], tex=DARK)
    add(281.1, L("42684", kb("f_48754075063.jpg", "in", "doc"), "Interior de Mount Locust · " + HS),
        [big("O EN EL PORCHE, SI YA NO CABÍA NADIE", 0.1, 0.08, 56)], tex=CLEAN)
    add(283.6, kb("u_mNC_avQmeq8.jpg", "in", "dark"), [big("DORMÍAS CON UNA MANO SOBRE EL DINERO", 0.1, 0.86, 62, YELLOW)], tex=DARK)
    add(286.1, kb("u_xjmHGUO_xTw.jpg", "in", "dark"), [big("OTRA CLASE DE GENTE", 0.4, 0.86, 76, RED)], tex=DARK)
    bg, ov = card([("BANDAS DE SALTEADORES", 52, GREY_, 0.34, 0.1), ("LOS HERMANOS HARPE", 110, WHITE, 0.5, 0.4),
                   ("SAMUEL MASON", 110, WHITE, 0.66, w("o la", 292.0) - 289.4)])
    add(289.4, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(294.0, kb("u_dCKZuqyXzuQ.jpg", "in", "dark"), [torch(((0.4, 0.55), (0.6, 0.5)), r=440, amb=0.2),
                                                     big("ESPERANDO EN LOS TRAMOS MÁS SOLITARIOS", 0.2, 0.86, 58)], tex=DARK)
    add(297.3, kb("u_ZZW4eHYSEgA.jpg", "in", "dark"), [big("CON LA COSECHA ENTERA ENCIMA…", 0.1, 0.42, 66),
                                                     big("CADA CURVA, UNA APUESTA", w("cada", 301.1) - 297.3, 0.58, 80, YELLOW)], tex=DARK)
    add(303.6, pick_w("burr", L("04519", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Aaron Burr · 1836 · " + LOC_), "Aaron Burr · John Vanderlyn · " + WM),
        [big("NI A LOS VIAJEROS IMPORTANTES LES GUSTABA", 0.1, 0.08, 54), LowerThird("AARON BURR", "Exvicepresidente del país", w("aaron", 306.5) - 303.6)],
        tex=ARCH)
    add(w("pasó", 310.7), kb("u_LpSDKz6dUyY.jpg", "in", "bw"), [big("LE ESCRIBIÓ A SU HIJA…", 0.1, 0.36, 60),
                                                              BigText("«UNA TIERRA VIL»", "serif", 110, YELLOW, (0.5, 0.52), w("que era", 312.6) - w("pasó", 310.7), None, "pop")],
        tex=DARK)
    add(314.9, kb("u_Tyy_kyZZl_k.jpg", "in", "bw"), [big("NO TODOS IBAN POR VOLUNTAD PROPIA", 0.2, 0.86, 64)], tex=DARK)
    bg, ov = card([("POR EL MISMO CAMINO, LOS TRAFICANTES DE ESCLAVOS", 50, GREY_, 0.34, 0.1),
                   ("HOMBRES, MUJERES Y NIÑOS ENCADENADOS", 72, WHITE, 0.5, w("llevaban", 322.1) - 319.1),
                   ("DE UN MERCADO A OTRO", 64, RED, 0.66, w("de un", 326.0) - 319.1)])
    add(319.1, bg, ov, tr="black", td=0.2, tex=DARK)
    add(327.8, kb("u_3mFKHgRC54Q.jpg", "in", "bw"), [big("LA MISMA TIERRA, EL MISMO BARRO", 0.1, 0.42, 70),
                                                   big("UN VIAJE QUE NADIE HABÍA ELEGIDO", w("para un", 330.3) - 327.8, 0.58, 66, YELLOW)], tex=DARK)
    add(332.6, mp("nt_reg", [(0, -89.0, 33.8, 0.6), (6.6, -89.0, 33.8, 0.64)],
                  [dict(type="route", ll=PARK, t0=0.0, draw=0.1, color=YELLOW, width=6, traffic=5, speed=160),
                   dict(type="pin", at="natchez", t0=0.0, label="NATCHEZ", side="l", box=True, size=36),
                   dict(type="pin", at="nashville_tn", t0=0.0, label="NASHVILLE", side="r", box=True, size=36)]),
        [big("1810: LA CARRETERA MÁS IMPORTANTE DE LA REGIÓN", 0.2, 0.1, 54, YELLOW)], tex=GFX)
    add(339.1, kb("u_x_XUgMfGISk.jpg", "in", "warm"), [big("EL CORREO", 0.0, 0.3, 64, WHITE, "pop"),
                                                     big("LOS SOLDADOS", w("pasaban los soldados", 340.5) - 339.1, 0.42, 64, WHITE, "pop"),
                                                     big("LOS PREDICADORES", w("pasaban los predicadores", 342.2) - 339.1, 0.54, 64, WHITE, "pop"),
                                                     big("LOS LADRONES", w("pasaban los ladrones", 343.6) - 339.1, 0.66, 70, RED, "pop")], tex=CLEAN)
    add(345.2, kb("u_mI-QcAP95Ok.jpg", "in", "warm"), [Badge("1813", 0.1, None), big("UN HOMBRE QUE SALIÓ DE ÉL CON UN APODO NUEVO", 0.3, 0.86, 56)], tex=CLEAN)

    # ============================== CAP 3: OLD HICKORY VUELVE A PIE (350.2 - 489.1)
    bg, ov = chapter(3, "OLD HICKORY VUELVE A PIE", "u_LpSDKz6dUyY.jpg", year="1813–1815")
    add(350.2, bg, ov, tr="black", td=0.2, tex=DARK)
    add(352.9, pick_l("3b06829", pick_w("jackson_earl", fr("f_15790285613.jpg", "Andrew Jackson, estatua en Nashville · Gary Todd (CC0)", "doc"),
                                        "Andrew Jackson · Ralph E. W. Earl · " + WM), "General Jackson · " + LOC_),
        [LowerThird("ANDREW JACKSON", "Voluntarios de Tennessee", 0.3), big("EN GUERRA CONTRA GRAN BRETAÑA", w("con estados", 355.4) - 352.9, 0.08, 54)],
        tex=ARCH)
    add(358.0, mp("nt_us", [(0, -88.0, 33.5, 0.9), (5.5, -89.0, 32.5, 1.0)],
                  [dict(type="route", path=["nashville_tn", (-86.9, 35.0), (-88.0, 34.4), (-89.0, 33.0), "natchez"], t0=0.3, draw=3.5, color=RED, width=6),
                   dict(type="pin", at="nashville_tn", t0=0.1, label="TENNESSEE", side="r", box=True, size=36),
                   dict(type="pin", at="natchez", t0=2.0, label="NATCHEZ", side="l", box=True, size=36),
                   ]),
        [Counter(0, 2070, "{:,.0f}", "VOLUNTARIOS", 0.3, 1.2, (0.5, 0.16), 110)], tr="zoom", td=0.3, tex=GFX)
    add(363.5, L("08176", kb("u_K0l4GwGX-Ec.jpg", "in", "doc"), "Escena en el bajo Mississippi · " + LOC_),
        [big("A DEFENDER NUEVA ORLEANS DE LOS BRITÁNICOS", 0.1, 0.08, 56, YELLOW)], tex=ARCH)
    add(367.4, kb("u_Q26QBC_zQ4k.jpg", "in", "cold"), [big("CIENTOS DE MILLAS, POR RÍO Y POR TIERRA", 0.1, 0.86, 62),
                                                     big("EN PLENO INVIERNO", w("en pleno", 371.2) - 367.4, 0.14, 70, BLUE)], tex=CLEAN)
    add(373.0, kb("u_g3lutX_kiys.jpg", "in", "dark"), [big("LA GUERRA HABÍA CAMBIADO DE PLANES", 0.1, 0.86, 64)], tex=DARK)
    bg, ov = card([("ACAMPADOS CERCA DE NATCHEZ", 52, GREY_, 0.34, 0.1), ("2 REGIMIENTOS DE INFANTERÍA", 84, WHITE, 0.5, 0.3),
                   ("1 CUERPO DE CABALLERÍA", 84, WHITE, 0.64, w("y un", 379.6) - 376.6)])
    add(376.6, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(383.8, kb("u_-ltjzTfhpCI.jpg", "in", "warm"), [big("UNA ORDEN DESDE WASHINGTON", 0.1, 0.86, 66), Badge("6 DE FEBRERO", w("firmada", 386.2) - 383.8, None),
                                                     Stamp("DADOS DE BAJA", w("la tropa", 388.4) - 383.8, RED, (0.5, 0.45), -8, 120)], tex=CLEAN)
    add(390.7, Solid("black"), [big("ASÍ, SIN MÁS", 0.1, 0.5, 120, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(392.4, kb("u_kwamtSMfXP0.jpg", "in", "bw"), [big("+2.000 HOMBRES · MUCHOS ENFERMOS", 0.1, 0.3, 66),
                                                   big("A CIENTOS DE MILLAS DE CASA", w("a cientos", 396.1) - 392.4, 0.44, 60),
                                                   ], tex=DARK)
    add(398.1, kb("u_3mFKHgRC54Q.jpg", "in", "bw"), [big("SIN PAGA", 0.0, 0.34, 84, RED, "pop"), big("SIN COMIDA", 0.8, 0.5, 84, RED, "pop"),
                                                   big("SIN TRANSPORTE", 1.6, 0.66, 84, RED, "pop")], tex=DARK)
    add(401.7, kb("u_6s8IZT0d-sk.jpg", "in", "cold"), [big("PONTE EN SU LUGAR", 0.1, 0.86, 76)], tex=CLEAN)
    add(404.5, V("2717", "u_LpSDKz6dUyY.jpg", 0.0, "cold"), [big("INVIERNO · PURO BARRO", 0.1, 0.86, 76, BLUE)], tex=CLEAN)
    add(407.8, kb("u_d279-ljvY3U.jpg", "in", "dark"), [big("SEMANAS LEJOS DE TU FAMILIA", 0.1, 0.42, 66),
                                                     big("TIENES FIEBRE", w("tienes", 410.2) - 407.8, 0.56, 76, RED)], tex=DARK)
    add(w("que ya", 412.3), Solid("black"), [big("«YA NO ERES ASUNTO DE NADIE»", 0.0, 0.5, 96, WHITE, "pop")], tr="black", td=0.1, tex=DARK)
    add(414.0, pick_l("12774", pick_w("jackson_bep", fr("f_104101418.jpg", "Andrew Jackson · estatua en Nashville · Brent Moore (CC BY 2.0)", "doc"),
                                      "Andrew Jackson · grabado · " + WM), "General Andrew Jackson · " + LOC_),
        [big("JACKSON SE NEGÓ A DEJARLOS AHÍ", 0.1, 0.08, 62, YELLOW)], tex=ARCH)
    add(417.2, kb("u_mNC_avQmeq8.jpg", "in", "warm"), [Counter(0, 1000, "${:,.0f}", "PRESTADOS A SU NOMBRE", 0.1, 1.0, (0.5, 0.36), 170),
                                                     big("CARRETAS PARA LOS ENFERMOS · COMIDA", w("para pagar", 419.4) - 417.2, 0.72, 56, YELLOW)], tex=CLEAN)
    add(424.1, kb("u_ZPuRUlmV8Dg.jpg", "in", "warm"), [big("DE VUELTA POR EL NATCHEZ TRACE", 0.1, 0.86, 64),
                                                     ], tex=CLEAN)
    add(427.3, kb("u_uNssca4IsiE.jpg", "in", "warm"), [big("A PIE, A SU LADO", 0.1, 0.86, 70), big("CEDIENDO SUS CABALLOS", w("y cediendo", 428.6) - 427.3, 0.14, 66, YELLOW)],
        tex=CLEAN)
    add(432.0, kb("u_diAupqmZXPQ.jpg", "in", "warm"), [big("EL BARRO Y EL CANSANCIO, COMO UNO MÁS", 0.1, 0.86, 62)], tex=CLEAN)
    add(436.2, kb("u_xnQaH8qF0Rc.jpg", "in", "doc"), [big("DURO COMO EL NOGAL AMERICANO", 0.1, 0.42, 70),
                                                    BigText("HICKORY", "serif_black", 140, YELLOW, (0.5, 0.6), w("el hickory", 439.4) - 436.2, None, "pop")], tex=CLEAN)
    add(440.6, pick_w("jackson_earl", fr("f_15790285613.jpg", "Andrew Jackson, estatua en Nashville · Gary Todd (CC0)", "doc"), "Andrew Jackson · " + WM),
        [Darken(0.3), BigText("«OLD HICKORY»", "serif", 130, YELLOW, (0.5, 0.5), 0.3, None, "pop")], tex=ARCH)
    add(443.3, pick_w("benton", L("06376", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Thomas H. Benton · 1837 · " + LOC_), "Thomas Hart Benton · " + WM),
        [big("MESES DESPUÉS…", 0.1, 0.08, 56), LowerThird("THOMAS HART BENTON", "Oficial de Jackson", w("thomas", 446.7) - 443.3)], tex=ARCH)
    add(449.3, kb("u_-ltjzTfhpCI.jpg", "in", "warm"), [big("A WASHINGTON, A RECLAMAR LOS 1.000 DÓLARES", 0.1, 0.86, 58)], tex=CLEAN)
    add(451.8, fr("f_104101418.jpg", "Andrew Jackson, Nashville · Brent Moore (CC BY 2.0)", "doc"),
        [big("EL APODO YA NO SE LO QUITÓ NADIE", 0.1, 0.08, 60, YELLOW), big("CON ÉL LLEGÓ A LA PRESIDENCIA", w("con él", 454.7) - 451.8, 0.92, 58)], tex=CLEAN)
    add(457.9, kb("u_J34M8K1uqs4.jpg", "in", "warm"), [big("LO HABÍA GANADO CAMINANDO HACIA CASA", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)
    add(460.3, kb("u_o2-rI5me4QQ.jpg", "l", "cold"), [Badge("1815", 0.1, None), big("EL CAMINO VOLVIÓ A LLENARSE", 0.4, 0.86, 66)], tex=CLEAN)
    add(465.2, L("3b24268", kb("u_o2-rI5me4QQ.jpg", "in", "bw"), "Grabado de 1835 · " + LOC_),
        [big("LA MILICIA QUE VENCIÓ EN NUEVA ORLEANS VUELVE A TENNESSEE", 0.1, 0.08, 52, YELLOW)], tex=ARCH)
    add(467.9, L("42683", kb("u_c4US2NpZ7Bk.jpg", "in", "doc"), "Mount Locust · " + HS), [big("LAS MISMAS CABAÑAS", w("durmiendo", 471.2) - 467.9, 0.08, 66)],
        tex=CLEAN)
    add(473.0, kb("f_44238514641.jpg", "in", "doc"), [big("UNA PROCESIÓN DE HOMBRES CANSADOS", 0.2, 0.86, 64)], tex=CLEAN)
    add(479.5, kb("u_fOokRWUpMg8.jpg", "in", "dark"), [big("NADA PODÍA QUITARLE ESE PAPEL…", 0.1, 0.42, 66),
                                                     ], tex=DARK)
    add(482.3, V("4422", "u_NKIB-TB3rvE.jpg", 0.0, "night"), [big("…PERO EN EL RÍO SE MOVÍA ALGO", 0.1, 0.42, 66, YELLOW),
                                                            big("QUE IBA A DEJAR ESE CAMINO SIN NADIE", w("que iba", 486.3) - 482.3, 0.58, 60)], tex=DARK)

    # ============================== CAP 4: EL VAPOR Y LA ZANJA (489.1 - 625.1)
    bg, ov = chapter(4, "EL VAPOR Y LA ZANJA", "u_NKIB-TB3rvE.jpg", year="1811–1900")
    add(489.1, bg, ov, tr="black", td=0.2, tex=DARK)
    add(491.7, pick_w("steamboat_1812", L("08177", kb("u_RrmXUxMqFcM.jpg", "in", "doc"), "Vapor en el Mississippi · " + LOC_),
                      "El New Orleans, primer vapor de los ríos del oeste · " + WM),
        [BigText("«NEW ORLEANS»", "serif", 100, YELLOW, (0.5, 0.1), w("se llamaba", 494.9) - 491.7, None, "up")], tex=ARCH)
    add(496.5, mp("nt_us", [(0, -84.0, 37.5, 0.75), (5.7, -88.5, 33.5, 0.82)],
                  [dict(type="route", path=OHIO_DOWN, t0=0.2, draw=4.6, color=(230, 230, 236), width=6),
                   dict(type="pin", at="pittsburgh_nt", t0=0.0, label="PITTSBURGH · 1811", side="r", box=True, size=36),
                   dict(type="pin", at="new_orleans", t0=4.5, label="1812", side="r", box=True, size=40)]),
        [big("EL PRIMER BARCO DE VAPOR HASTA NUEVA ORLEANS", 0.2, 0.1, 54)], tr="zoom", td=0.3, tex=GFX)
    add(502.2, L("3b22234", kb("u_U6HqJ5A7yzY.jpg", "in", "doc"), "«Hailing a steamboat» · 1871 · " + LOC_), [big("EN POCOS AÑOS, DOCENAS", w("y en", 505.7) - 502.2, 0.08, 64)],
        tex=ARCH)
    add(508.4, mp("nt_us", [(0, -88.5, 34.0, 0.82), (5.9, -86.5, 36.5, 0.86)],
                  [dict(type="route", path=OHIO_DOWN[::-1], t0=w("podían", 511.7) - 508.4 - 0.4, draw=3.0, color=YELLOW, width=7)]),
        [big("UNA VENTAJA QUE NINGUNA BALSA TUVO JAMÁS", 0.1, 0.1, 56), big("PODÍAN SUBIR RÍO ARRIBA", w("podían", 511.7) - 508.4, 0.9, 72, YELLOW, "pop")],
        tex=GFX)
    add(514.3, kb("u_RrmXUxMqFcM.jpg", "in", "doc"), [big("ESO LO CAMBIÓ TODO PARA LOS KAINTUCKS", 0.1, 0.86, 60)], tex=CLEAN)
    add(516.8, kb("u_ClzDGtdq68g.jpg", "in", "warm"), [big("NI VENDER LA BALSA NI CAMINAR SEMANAS", 0.1, 0.86, 62)], tex=CLEAN)
    add(521.0, L("08176", kb("u_xDuNqiySozo.jpg", "in", "warm"), "Escena en el bajo Mississippi · " + LOC_),
        [big("UN PASAJE · VOLVER SENTADO", 0.1, 0.08, 64, YELLOW), big("LA PLATA A SALVO EN EL CAMAROTE", w("y volver", 522.7) - 521.0 + 0.8, 0.92, 56)], tex=ARCH)
    add(526.4, cus(G11.bars, rows=[("A PIE", 21, "3 SEMANAS DE BARRO", (200, 200, 206)), ("EN BARCO", 4, "POCOS DÍAS", YELLOW)], title="DE VUELTA AL NORTE",
                   times=[0.1, w("en barco", 528.9) - 526.4]), tr="fade", td=0.2, tex=GFX)
    add(531.5, mp("nt_reg", [(0, -88.6, 33.5, 0.58), (5.7, -88.6, 33.2, 0.6)],
                  [dict(type="route", ll=PARK, t0=0.0, draw=0.1, color=(160, 150, 120), width=5, dash=16),
                   dict(type="route", path=MIL_ROAD, t0=0.4, draw=3.5, color=RED, width=6),
                   dict(type="label", at="columbus_ms", text="CAMINO MILITAR DE JACKSON · 1817–1820", t0=w("se construyó", 537.5) - 531.5, dx=140, size=40, box=True)]),
        [big("UNA RUTA MÁS RECTA", 0.2, 0.1, 62)], tr="zoom", td=0.3, tex=GFX)
    add(541.2, kb("u_Zu9U98JjuWQ.jpg", "in", "warm"), [big("«EL CAMINO MILITAR DE JACKSON»", 0.0, 0.86, 70, YELLOW)], tex=CLEAN)
    add(544.7, kb("u_Axli9F0n26A.jpg", "in", "warm"), [Badge("HACIA 1825", 0.1, None), big("EL CORREO TAMBIÉN SE VA", 0.3, 0.86, 70)], tex=CLEAN)
    add(549.4, kb("u_86gRgd2Kdpw.jpg", "in", "bw"), [Badge("AÑOS 1830", 0.1, None), big("CASI NADIE · LAS POSADAS CIERRAN", 0.3, 0.86, 64)], tex=DARK)
    add(556.2, L("093883p", kb("u_86gRgd2Kdpw.jpg", "in", "bw"), "Butler Dogtrot, en el viejo Natchez Trace · HABS · " + LOC_),
        [Badge("1840", 0.1, None), big("CABAÑAS VACÍAS", w("habrías", 559.2) - 556.2, 0.08, 66)], tex=ARCH)
    add(561.8, V("28342", "u_Q2yhonBKuck.jpg", 0.0, "dark"), [big("PUENTES DE TRONCOS PODRIDOS", 0.0, 0.42, 66),
                                                     big("LA SENDA, TAPADA POR LA MALEZA", w("y la", 563.2) - 561.8, 0.58, 64, YELLOW)], tex=DARK)
    add(565.9, kb("f_44238521561.jpg", "in", "doc"), [big("EL CAMINO NO DESAPARECIÓ DEL TODO", 0.1, 0.86, 64)], tex=CLEAN)
    add(568.5, kb("u_mBV6JIBq1l0.jpg", "in", "warm"), [big("EN EL SUR DE MISSISSIPPI, EL SUELO ES UN POLVO MUY FINO", 0.1, 0.86, 54),
                                                     big("QUE TRAJO EL VIENTO DURANTE MILES DE AÑOS", w("que el viento", 571.6) - 568.5, 0.14, 56, YELLOW)], tex=CLEAN)
    add(575.1, cus(G11.sunken, t0=0.2, deep_d=11.0, yrs=(1800, 1900), roots_t=99), tr="fade", td=0.2, tex=GFX)
    add(587.1, kb("f_42430605240.jpg", "up", "doc"), [big("MÁS ALTO QUE DOS PERSONAS, UNA ENCIMA DE OTRA", 0.0, 0.86, 54, YELLOW)], tex=CLEAN)
    add(590.1, kb("f_37063709992.jpg", "in", "doc"), [big("UN PASILLO ENTRE PAREDES DE TIERRA", 0.0, 0.86, 62), big("CON RAÍCES COLGANDO", 1.8, 0.14, 62, YELLOW)],
        tex=CLEAN)
    add(593.6, kb("w_grindstone.jpg", "in", "doc"), [big("ESA MARCA SIGUIÓ AHÍ", 0.1, 0.86, 70)], tex=CLEAN)
    add(596.8, kb("f_36421185033.jpg", "out", "doc"), [big("CASI UN SIGLO: UNA ZANJA EN EL BOSQUE", 0.1, 0.86, 62),
                                                     big("QUE SOLO CONOCÍAN LOS GRANJEROS", w("que solo", 601.5) - 596.8, 0.14, 58, YELLOW)], tex=CLEAN)
    add(604.5, V("2221", "u_FnaiTxmOHhA.jpg", 0.0, "dark"), [big("ANTES DE VER CÓMO ESE CAMINO VOLVIÓ A LA VIDA…", 0.3, 0.86, 56)], tex=DARK)
    add(w("si te", 609.5), kb("w_highsmith.jpg", "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe)], tex=DARK)
    add(w("porque lo", 615.8), kb("l_04384.jpg", "in", "doc"), [big("LO QUE PASÓ DESPUÉS NO LO ESPERABA NADIE", 0.1, 0.86, 58),
                                                              big("PARA QUE NADIE TUVIERA PRISA", w("para que", 622.5) - w("porque lo", 615.8), 0.14, 66, YELLOW)], tex=CLEAN)

    # ============================== CAP 5: BUSBY Y EL PARQUE CON FORMA DE CARRETERA (625.1 - 763.8)
    bg, ov = chapter(5, "UN PARQUE CON FORMA DE CARRETERA", "l_42698.jpg", year="1909–1938")
    add(625.1, bg, ov, tr="black", td=0.2, tex=DARK)
    add(627.4, kb("u_ysuzvcVdEzo.jpg", "in", "doc"), [Badge("1909", 0.1, None), big("UNA ASOCIACIÓN DE MUJERES", 0.3, 0.86, 66)], tex=CLEAN)
    add(632.8, kb("f_36398370694.jpg", "in", "doc"), [big("MARCADORES A LO LARGO DEL VIEJO TRACE", 0.1, 0.86, 60)], tex=CLEAN)
    bg, ov = card([("SE LLAMABAN", 52, GREY_, 0.36, 0.1), ("DAUGHTERS OF THE", 96, WHITE, 0.5, 0.3), ("AMERICAN REVOLUTION", 96, YELLOW, 0.63, 0.6)])
    add(637.3, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(640.8, kb("f_43332777955.jpg", "in", "doc"), [big("CONDADO POR CONDADO, LA ZANJA VOLVÍA A TENER NOMBRE", 0.1, 0.86, 54)], tex=CLEAN)
    add(645.1, L("3c29408", kb("u_3mFKHgRC54Q.jpg", "in", "bw"), "Natchez, embarcadero del ferry · 1927 · " + LOC_), [Badge("AÑOS 1930", 0.1, None), big("LA GRAN DEPRESIÓN", w("llegó", 646.6) - 645.1, 0.86, 84, YELLOW, "pop")],
        tex=ARCH)
    add(648.9, kb("u_x0_yX5VXDjc.jpg", "in", "bw"), [big("MISSISSIPPI: UNO DE LOS ESTADOS MÁS POBRES", 0.1, 0.86, 58)], tex=DARK)
    add(652.4, pick_w("busby", L("09868", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Jeff Busby · " + LOC_), "Jeff Busby · " + WM),
        [LowerThird("JEFF BUSBY", "Congresista por Mississippi", 0.3), big("MÁS DE 10 AÑOS EN WASHINGTON", w("que llevaba", 654.8) - 652.4, 0.08, 56)], tex=ARCH)
    add(658.8, kb("u_4DmYfVEpOXo.jpg", "in", "warm"), [big("TUVO UNA IDEA", 0.0, 0.3, 80, YELLOW, "pop"),
                                                     rich("¿POR QUÉ NO PONERLOS A CONSTRUIR UNA CARRETERA SOBRE EL CAMINO DE LOS KAINTUCKS?", ("carretera",),
                                                          w("si había", 660.0) - 658.8, step=0.08, y=0.6, size=56, maxw=0.85)], tex=CLEAN)
    add(666.4, kb("u_o2-rI5me4QQ.jpg", "in", "bw"), [big("FRANKLIN D. ROOSEVELT LO RESPALDÓ", 0.1, 0.86, 62)], tex=DARK)
    add(668.6, kb("u_DYWHwLZyJ64.jpg", "in", "warm"), [Badge("1934", 0.1, None), Counter(0, 50000, "${:,.0f}", "PARA ESTUDIAR EL TRAZADO", 0.4, 1.2, (0.5, 0.42), 170)],
        tex=CLEAN)
    add(674.1, pick_w("busby", L("09868", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Jeff Busby · " + LOC_), "Jeff Busby · " + WM),
        [Stamp("1935: DEJA SU ESCAÑO", 0.6, RED, (0.5, 0.45), -8, 100), big("ANTES DE LA PRIMERA PALADA", w("antes", 679.0) - 674.1, 0.88, 60)], tex=ARCH)
    add(681.9, kb("u_GkpFUHXM0xo.jpg", "in", "doc"), [big("LA IDEA SIGUIÓ ADELANTE SIN ÉL", 0.1, 0.86, 64)], tex=CLEAN)
    add(684.8, cus(G4.calendar, cards=[("18", "MAYO DE 1938", "NACE EL PARQUE NACIONAL", 0.2, (60, 62, 66))]), tr="fade", td=0.2, tex=GFX)
    add(691.2, V("41379", "u_L--Tbbbe2V4.jpg", 0.0, "doc"), [big("Y ESO MARCÓ SU DESTINO", 0.1, 0.86, 66)], tex=CLEAN)
    add(692.9, cus(G11.park_road, t0=0.3, buy_t=w("con una", 698.5) - 692.9), [big("NO UNA AUTOPISTA: UN PARQUE ALARGADO", 0.2, 0.06, 56, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(700.8, cus(G11.park_road, t0=-9, buy_t=-9), [big("EL GOBIERNO COMPRA LA TIERRA A AMBOS LADOS", 0.1, 0.06, 54, YELLOW),
                                                     big("NADIE ABRIRÁ UNA TIENDA JUNTO AL ASFALTO", w("para que", 705.1) - 700.8, 0.94, 52)], tex=GFX)
    add(708.5, cus(G11.rules, times=[99, 0.1, w("nada de gasolineras", 710.1) - 708.5, w("nada de semáforos", 711.6) - 708.5, 99], speed_t=99),
        tr="fade", td=0.2, tex=GFX)
    add(713.2, V("41559", "l_04384.jpg", 0.0, "doc"), [big("NADA TE OBLIGA A FRENAR", 0.1, 0.86, 72)], tex=CLEAN)
    add(717.7, cus(G11.rules, times=[99, -1, -1, -1, 99], speed_t=0.1), [big("Y EN ALGUNOS TRAMOS, MENOS", w("y en algunos", 722.4) - 717.7, 0.08, 56)],
        tr="fade", td=0.2, tex=GFX)
    add(724.6, V("41555", "l_08888.jpg", 0.0, "doc"), [big("LO JUSTO PARA MIRAR EL PAISAJE", 0.1, 0.86, 66)], tex=CLEAN)
    add(726.9, cus(G11.rules, times=[0.1, -1, -1, -1, 99], speed_t=99), [big("VEHÍCULOS COMERCIALES: PROHIBIDOS EN TODO EL RECORRIDO", 0.3, 0.88, 50, RED)],
        tr="fade", td=0.2, tex=GFX)
    q2(730.7, badge="PREGUNTA 2 · LA RESPUESTA")
    bg, ov = card([("NO ES UNA CARRETERA CON UN PARQUE ALREDEDOR", 60, GREY_, 0.38, 0.1),
                   ("ES UN PARQUE NACIONAL CON FORMA DE CARRETERA", 80, YELLOW, 0.56, w("es un", 742.6) - 739.9)])
    add(739.9, bg, ov, tr="flash", td=0.2, tex=GFX)
    add(745.4, kb("u_5XG-Soq1iTQ.jpg", "in", "warm"), [big("ALLÍ NO SE PERMITE VENDER NADA", 0.1, 0.86, 66),
                                                     big("COMO UN SUPERMERCADO EN MEDIO DE YELLOWSTONE", w("igual", 747.6) - 745.4, 0.14, 54, YELLOW)], tex=CLEAN)
    add(751.2, kb("u_P0bVatS8Jdw.jpg", "in", "doc"), [big("POR ESO TAMPOCO ENTRAN CAMIONES", 0.1, 0.86, 66),
                                                    big("SERÍA UNA RUTA DE CARGA MÁS", w("convertirían", 754.0) - 751.2, 0.14, 60, YELLOW)], tex=CLEAN)
    add(759.0, kb("u_4DmYfVEpOXo.jpg", "out", "doc"), [big("EL PLAN ERA BONITO…", 0.0, 0.42, 70),
                                                                                        big("FALTABA CONSTRUIRLO", w("faltaba", 760.0) - 759.0, 0.58, 84, YELLOW, "pop")],
        tex=CLEAN)

    # ============================== CAP 6: LOS 67 AÑOS DE OBRA (763.8 - 907.3)
    bg, ov = chapter(6, "LOS 67 AÑOS DE OBRA", "u_WRbr71MxE-c.jpg", year="1939–2005")
    add(763.8, bg, ov, tr="black", td=0.2, tex=DARK)
    add(766.9, kb("u_6s8IZT0d-sk.jpg", "in", "bw"), [big("CUADRILLAS DE LA DEPRESIÓN", 0.1, 0.86, 66),
                                                    big("CUALQUIER JORNAL", w("hombres", 770.1) - 766.9, 0.14, 64, YELLOW)], tex=ARCH)
    add(772.4, kb("u_o2-rI5me4QQ.jpg", "r", "bw"), [Badge("1941", 0.1, None), big("LA SEGUNDA GUERRA MUNDIAL", 0.3, 0.86, 70, RED),
                                                  big("EL DINERO Y LOS HOMBRES, A OTRA PARTE", w("y el dinero", 776.4) - 772.4, 0.14, 56)], tex=DARK)
    add(779.7, kb("u_GJs_Zit-eOQ.jpg", "in", "dark"), [big("A MEDIO EMPEZAR", 0.1, 0.86, 80, YELLOW)], tex=DARK)
    add(782.3, kb("u_7xfqSh_KdKU.jpg", "in", "doc"), [big("UNA AUTOPISTA NORMAL: DE UN EXTREMO AL OTRO", 0.2, 0.86, 56),
                                                    big("CON PRISA POR CONECTAR CIUDADES", w("con prisa", 787.8) - 782.3, 0.14, 58)], tex=CLEAN)
    add(789.7, cus(G11.pieces, t0=-30, y0=1955, y1=1955.1), [big("ESTA SE HACÍA A TROZOS", 0.1, 0.86, 76, YELLOW, "pop")], tr="fade", td=0.2, tex=GFX)
    add(792.3, kb("u_DD0fKMPg8ZA.jpg", "in", "warm"), [big("DONDE SE HABÍA COMPRADO LA TIERRA", 0.0, 0.42, 62),
                                                     big("Y CUANDO HABÍA PRESUPUESTO", w("y cuando", 793.9) - 792.3, 0.58, 66, YELLOW)], tex=CLEAN)
    add(796.8, kb("u_P0bVatS8Jdw.jpg", "in", "dark"), [big("NO MUEVE CARGA NI TRAE NEGOCIOS…", 0.1, 0.42, 64),
                                                     big("NUNCA ES LA PRIMERA DE LA LISTA", w("nunca", 799.7) - 796.8, 0.58, 66, YELLOW)], tex=DARK)
    add(802.4, cus(G11.pieces, t0=0.0, y0=1939, y1=1964), [big("SIEMPRE AL RITMO DEL PRESUPUESTO", w("siempre", 807.2) - 802.4, 0.88, 54, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(809.5, pick_w("busby", L("09868", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Jeff Busby · " + LOC_), "Jeff Busby · " + WM),
        [Darken(0.35), big("18 DE OCTUBRE DE 1964: MUERE JEFF BUSBY", 0.2, 0.86, 58, YELLOW), big("TENÍA 80 AÑOS", w("tenía", 816.1) - 809.5, 0.14, 64)], tex=ARCH)
    add(817.5, cus(G11.pieces, t0=-30, y0=1964, y1=1964.1), [big("TRAMOS SUELTOS · NO SE PODÍA RECORRER ENTERA", 0.2, 0.88, 52)], tr="fade", td=0.2, tex=GFX)
    add(825.4, pick_w("arch_nps", fr("f_5841323526.jpg", "El puente de los dos arcos · foto: daveoratox (CC BY 2.0)", "doc"),
                      "Puente de doble arco, milla 438 · NPS (dominio público)"),
        [Badge("1994", 0.1, None), big("LA OBRA MÁS LLAMATIVA DEL PROYECTO", 0.4, 0.08, 58, YELLOW)], tex=CLEAN)
    add(833.6, cus(G11.arch_bridge, t0=-20, build_d=0.1, dims_t=w("a 145", 836.7) - 833.6), [big("UN PUENTE DE CONCRETO CON DOS ARCOS", 0.1, 0.06, 54, WHITE)],
        tr="fade", td=0.2, tex=GFX)
    add(841.8, kb("u_zfPksMTcWAA.jpg", "in", "doc"), [big("ARCO PRINCIPAL: 582 PIES", 0.1, 0.86, 76, YELLOW), big("CASI 180 METROS DE UN LADO A OTRO", 1.6, 0.14, 58)],
        tex=CLEAN)
    add(849.0, cus(G11.arch_bridge, t0=0.3, build_d=4.6, dims_t=99), tr="fade", td=0.2, tex=GFX)
    add(853.9, mp("nt_reg", [(0, -86.95, 35.88, 3.2), (3.1, -86.95, 35.88, 3.4)],
                  [dict(type="pin", at="franklin_tn", t0=0.2, label="FRANKLIN", side="r", box=True, size=40),
                   dict(type="pin", at="double_arch", t0=0.6, label="EL PUENTE", side="l", box=True, size=40),
                   dict(type="route", path=["franklin_tn", "double_arch"], t0=0.8, draw=1.4, color=YELLOW, width=5, dash=14)]),
        [big("PIEZAS FABRICADAS EN FRANKLIN", 0.1, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(857.0, cus(G11.arch_bridge, t0=-0.2, build_d=4.6, dims_t=99), [big("HASTA QUE LOS ARCOS SE CERRARON", w("hasta", 861.5) - 857.0, 0.94, 54, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(863.6, kb("f_1520326718.jpg", "in", "doc"), [Counter(0, 11.3, "${:.1f} MILLONES", "", 0.1, 1.0, (0.5, 0.36), 150),
                                                   big("PREMIO PRESIDENCIAL DE DISEÑO", w("y al año", 865.8) - 863.6, 0.86, 62, YELLOW),
                                                   Caption("Natchez Trace Parkway Bridge", "foto: The_Gut (CC BY 2.0)", 0.5, y=0.08)], tex=CLEAN)
    add(870.0, mp("nt_reg", [(0, -90.2, 32.4, 1.5), (5.5, -90.15, 32.35, 1.8)],
                  [dict(type="route", ll=route(0, 444), t0=0.0, draw=0.1, color=(200, 200, 206), width=6),
                   dict(type="route", ll=route(87, 105), t0=0.4, draw=1.0, color=RED, width=9),
                   dict(type="pin", at="jackson_ms", t0=0.2, label="JACKSON, CAPITAL DEL ESTADO", side="r", box=True, size=38)]),
        [big("EL ÚLTIMO HUECO", 0.2, 0.1, 64, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(875.5, kb("u_7xfqSh_KdKU.jpg", "out", "doc"), [big("LA CIUDAD HABÍA CRECIDO MIENTRAS ESPERABA", 0.1, 0.86, 58),
                                                     big("ABRIRSE PASO ENTRE BARRIOS ENTEROS", w("que hubo", 878.8) - 875.5, 0.14, 58, YELLOW)], tex=CLEAN)
    add(881.8, cus(G11.pieces, t0=-6.0, y0=1990, y1=2005.2), tr="fade", td=0.2, tex=GFX)
    bg, ov = card([("67 AÑOS", 200, YELLOW, 0.45, 0.1), ("DESPUÉS DE QUE NACIERA EL PARQUE", 60, WHITE, 0.64, 0.6)])
    add(888.5, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(891.4, mp("nt_us", [(0, -89.0, 33.8, 0.88), (5.0, -89.0, 33.8, 0.92)],
                  [dict(type="route", ll=PARK, t0=0.3, draw=3.0, color=YELLOW, width=7),
                   dict(type="pin", at="natchez", t0=0.1, label="NATCHEZ", side="l", box=True, size=38),
                   dict(type="pin", at="nashville_tn", t0=2.5, label="NASHVILLE", side="r", box=True, size=38)]),
        [big("444 MILLAS · 715 KM SIN SALIRTE DEL PARQUE", 0.4, 0.1, 54, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(899.7, kb("l_42697.jpg", "in", "doc"), [big("A 50 MILLAS POR HORA, CLARO", 0.0, 0.86, 72, YELLOW)], tex=CLEAN)
    add(901.3, pick_w("busby", L("09868", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), "Jeff Busby · " + LOC_), "Jeff Busby · " + WM),
        [Darken(0.35), big("BUSBY PROPUSO UNA CARRETERA PARA DAR TRABAJO RÁPIDO", 0.1, 0.84, 52),
         big("NO VIVIÓ PARA MANEJARLA", w("no vivió", 905.1) - 901.3, 0.14, 72, YELLOW)], tex=ARCH)

    # ============================== CAP 7: LA CARRETERA PARTIDA OTRA VEZ (907.3 - 1038.9)
    bg, ov = chapter(7, "LA CARRETERA PARTIDA OTRA VEZ", "u_Rj7sPIb4LY0.jpg", year="2026")
    add(907.3, bg, ov, tr="black", td=0.2, tex=DARK)
    add(910.4, kb("f_6623867793.jpg", "in", "doc"), [big("LO QUE SE HABÍA PROMETIDO", 0.1, 0.86, 66)], tex=CLEAN)
    add(913.3, V("100231", "f_45528674134.jpg", 0.0, "doc"), [big("UNAS 9 HORAS DE CURVAS SUAVES", 0.1, 0.86, 66),
                                                            big("SIN UN SOLO CAMIÓN", w("sin un", 916.9) - 913.3, 0.14, 70, YELLOW)], tex=CLEAN)
    add(918.3, kb("u_G6VNKqR8NvM.jpg", "in", "doc"), [big("AL OTRO LADO DE LOS ÁRBOLES: LA AUTOPISTA", 0.1, 0.86, 58)], tex=CLEAN)
    add(925.5, Split([kb("u_RXhYafME6r0.jpg", "in", "doc"), kb("l_42697.jpg", "in", "doc")], labels=["ELLOS VAN MÁS RÁPIDO", "TÚ VAS MÁS TRANQUILO"]),
        tex=CLEAN)
    add(928.4, V("39912", "u_cYzYovIzICM.jpg", 0.0, "warm"), [big("RUTA FAVORITA DE MOTOCICLISTAS…", 0.1, 0.86, 62)], tex=CLEAN)
    add(w("ciclistas", 930.7) + 0.3, L("42699", kb("u_5ycLBsDqfBk.jpg", "in", "doc"), "En bicicleta por la Natchez Trace · " + HS),
        [big("…Y CICLISTAS, POR TRAMOS, DURANTE DÍAS", 0.1, 0.08, 58)], tex=CLEAN)
    add(936.0, kb("u_OpvM6zsgSPI.jpg", "in", "doc"), [big("UNA CARRETERA, AUNQUE SEA UN PARQUE, TAMBIÉN SE GASTA", 0.1, 0.86, 54)], tex=CLEAN)
    add(940.0, cus(G11.clay, t0=0.2, cycles=2.0), tr="fade", td=0.2, tex=GFX)
    add(948.8, Solid("black"), [big("LO MÁS IRÓNICO LLEGA AHORA", 0.1, 0.5, 100, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(951.7, cus(G11.two_decades, t0=-3.0, t1=-1.0, t2=w("la carretera vuelve", 955.8) - 951.7), [big("SOLO 21 AÑOS DESPUÉS DE TERMINARLA", 0.1, 0.1, 56)],
        tr="fade", td=0.2, tex=GFX)
    add(957.6, kb("u_WRbr71MxE-c.jpg", "in", "doc"), [Counter(0, 150, "${:.0f} MILLONES", "PARA RECONSTRUIR 83 MILLAS", w("de 150", 960.6) - 957.6, 1.2,
                                                            (0.5, 0.4), 160)], tex=CLEAN)
    add(966.0, mp("nt_reg", [(0, -89.6, 33.0, 0.95), (7.0, -89.4, 33.2, 1.05)],
                  [dict(type="route", ll=PARK, t0=0.0, draw=0.1, color=(200, 200, 206), width=6),
                   dict(type="route", ll=route(135, 159.5), t0=w("pero otro", 969.2) - 966.0, draw=1.2, color=RED, width=10),
                   dict(type="label", at=mp_at(147), text="24 MILLAS EN OBRAS", t0=w("pero otro", 969.2) - 966.0 + 0.8, dx=220, size=44, box=True),
                   dict(type="pin", at="jackson_ms", t0=0.2, label="JACKSON", side="l", box=True, size=34)]),
        [big("CENTRO DE MISSISSIPPI", 0.2, 0.1, 60, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(973.1, kb("u_rYzjlG45K1A.jpg", "in", "doc"), [big("CERRADO AL TRÁFICO", 0.0, 0.1, 80, RED, "pop")], tex=CLEAN)
    add(976.7, kb("u_4DmYfVEpOXo.jpg", "in", "doc"), [big("LEVANTANDO LA CARRETERA HASTA ABAJO", 0.1, 0.86, 62),
                                                    big("DRENAJES · PUENTES", w("rehaciendo", 979.7) - 976.7, 0.14, 66, YELLOW)], tex=CLEAN)
    add(982.9, kb("u_L9IHDMIZkKM.jpg", "in", "doc"), [big("EL DESVÍO TE SACA POR CARRETERAS ESTATALES", 0.2, 0.86, 58)], tex=CLEAN)
    add(989.8, kb("u_G6VNKqR8NvM.jpg", "out", "doc"), [big("PARA LOS VECINOS: UN RODEO", 0.1, 0.86, 66),
                                                     big("AL TRABAJO · AL MÉDICO · A LA ESCUELA", w("para ir", 992.2) + 0.3 - 989.8, 0.14, 60, YELLOW)], tex=CLEAN)
    add(997.0, Solid("black"), [big("Y NO ES EL ÚNICO CORTE", 0.1, 0.5, 100, WHITE, "pop")], tr="black", td=0.1, tex=DARK)
    add(999.0, pick_w("arch_nps", fr("f_5841323526.jpg", "El puente de los dos arcos · foto: daveoratox (CC BY 2.0)", "doc"),
                      "Puente de doble arco, milla 438 · NPS (dominio público)"),
        [big("EL ORGULLO DE TODO EL PROYECTO", 0.1, 0.08, 60), Stamp("CERRADO DESDE EL 15/4/2026", w("lleva", 1003.1) - 999.0, RED, (0.5, 0.5), -8, 84)], tex=CLEAN)
    add(1007.9, kb("u_P0bVatS8Jdw.jpg", "in", "doc"), [big("UN RODEO POR CARRETERAS NORMALES", 0.1, 0.86, 62),
                                                     big("CON GASOLINERAS Y CAMIONES", w("de esas", 1010.3) - 1007.9 + 0.4, 0.14, 62, YELLOW)], tex=CLEAN)
    add(1016.7, cus(G11.two_decades, t0=-0.4, t1=w("estuvo", 1024.2) - 1016.7 - 0.6, t2=99), [big("LA VUELTA QUE HA DADO TODO", 0.1, 0.1, 58)],
        tr="fade", td=0.2, tex=GFX)
    add(1026.9, kb("u_dq3ujEmzV0s.jpg", "in", "doc"), [big("PARA CRUZARLA HOY, HAY QUE SALIRSE DE ELLA", 0.1, 0.86, 58),
                                                     big("COMO LOS KAINTUCKS SE SALÍAN DEL RÍO", w("igual", 1030.9) - 1026.9, 0.14, 58, YELLOW)], tex=CLEAN)
    add(1034.2, kb("u_WRbr71MxE-c.jpg", "out", "doc"), [Darken(0.4), big("88 AÑOS DESPUÉS DE EMPEZARLA…", 0.1, 0.42, 72),
                                                                                        big("TODAVÍA SE ESTÁ CONSTRUYENDO", w("todavía", 1036.7) - 1034.2, 0.58, 80, YELLOW, "pop")],
        tex=CLEAN)

    # ============================== CAP 8: HOY (1038.9 - 1117.8)
    bg, ov = chapter(8, "HOY", "w_grindstone.jpg", year="2026")
    add(1038.9, bg, ov, tr="black", td=0.2, tex=DARK)
    add(1043.6, mp("nt_loc", [(0, -91.25, 31.75, 0.55), (4.4, -91.2, 31.7, 0.7)],
                   [dict(type="pin", at="emerald_mound", t0=w("cerca de la milla 10", 1048.0) - 1043.6, label="MILLA 10", side="l", box=True, size=36),
                    dict(type="pin", at="mount_locust", t0=w("cerca de la milla 15", 1057.0) - 1043.6, label="MILLA 15", side="r", box=True, size=36),
                    dict(type="pin", at="sunken_trace", t0=w("en la milla 41", 1070.7) - 1043.6, label="MILLA 41", side="r", box=True, size=36)]),
        [big("DONDE TODAVÍA PUEDES TOCAR EL CAMINO ORIGINAL", 0.2, 0.1, 54)], tr="zoom", td=0.3, tex=GFX)
    add(1048.0, kb(pick("w_emerald.jpg", "f_399314509.jpg"), "in", "doc"), [LowerThird("EMERALD MOUND", "Milla 10", 0.3)], tex=CLEAN)
    add(1051.1, kb("f_37045369346.jpg", "up", "doc"), [big("LO LEVANTARON LOS PUEBLOS NATIVOS", 0.1, 0.86, 62),
                                                     big("SIGLOS ANTES QUE CUALQUIER EUROPEO", w("siglos", 1054.0) - 1051.1, 0.14, 58, YELLOW)], tex=CLEAN)
    add(1057.0, kb("f_3251630999.jpg", "in", "doc"), [LowerThird("MOUNT LOCUST", "Milla 15 · hacia 1780", 0.3)], tex=CLEAN)
    add(1064.2, L("42682", kb("u_c4US2NpZ7Bk.jpg", "in", "doc"), "Mount Locust · " + HS),
        [big("LA ÚNICA POSADA QUE HA LLEGADO HASTA HOY", w("es la única", 1066.7) - 1064.2, 0.08, 56, YELLOW)], tex=CLEAN)
    add(1070.7, kb("f_44238514641.jpg", "in", "doc"), [LowerThird("SUNKEN TRACE", "Milla 41", 0.3)], tex=CLEAN)
    add(1075.2, kb("w_grindstone.jpg", "down", "doc"), [big("UN PASILLO HUNDIDO", 0.2, 0.86, 70), big("RAÍCES COLGANDO", w("con raíces", 1079.2) - 1075.2, 0.14, 64)],
        tex=CLEAN)
    add(1081.7, V("2187", "f_42430605240.jpg", 0.0, "doc"), [big("MÁS FRESCO · EL RUIDO DESAPARECE", 0.1, 0.86, 64)], tex=CLEAN)
    add(1086.4, kb(pick("w_pharr.jpg", "u_4vJprMy4nsQ.jpg"), "in", "doc"), [LowerThird("PHARR MOUNDS", "Milla 286 · cerca de Tupelo", 0.3),
                                                                          big("LOS MONTÍCULOS DE 2.000 AÑOS DEL PRINCIPIO", w("siguen", 1089.9) - 1086.4, 0.08, 54)],
        tex=CLEAN)
    add(1092.7, kb("u_9aTq1QcnJek.jpg", "l", "doc"), [big("SOBRE LA MISMA LÍNEA QUE SIGUIERON LOS BISONTES", 0.3, 0.86, 54)], tex=CLEAN)
    add(1096.4, kb("f_6109637455.jpg", "in", "doc"), [big("TENNESSEE: DONDE ESTUVO LA POSADA DE GRINDER", 0.1, 0.08, 54),
                                                    Caption("Cabaña junto al sitio de Grinder's Stand", "foto: Ron Cogswell (CC BY 2.0)", 1.0)], tex=CLEAN)
    add(1104.4, fr("f_5409091539.jpg", "Monumento a Meriwether Lewis · foto: Stuart Seeger (CC BY 2.0)", "doc"),
        [LowerThird("MERIWETHER LEWIS", "Murió aquí en 1809", 0.3), big("LA EXPEDICIÓN DE LEWIS Y CLARK", w("el explorador", 1108.3) - 1104.4, 0.08, 54)], tex=CLEAN)
    add(1111.6, fr("f_104101418.jpg", "Estatua de Andrew Jackson, Nashville · Brent Moore (CC BY 2.0)", "doc"),
        [big("NASHVILLE, EL FINAL DEL VIAJE", 0.1, 0.08, 58), big("UNA ESTATUA DE OLD HICKORY", w("hay", 1115.7) - 1111.6, 0.92, 60, YELLOW)], tex=CLEAN)

    # ============================== CONCLUSIÓN (1117.8 - end)
    q1(1117.8, badge="DE VUELTA A LA PREGUNTA 1")
    add(1125.1, kb("u_GJs_Zit-eOQ.jpg", "punch", "dark"), [big("PORQUE NADIE LA NECESITABA CON URGENCIA", 0.1, 0.5, 72, YELLOW, "pop")], tr="flash", td=0.2,
        tex=DARK)
    add(1127.9, cus(G11.pieces, t0=0.0, y0=1938, y1=2005.2), [big("DEPRESIÓN · GUERRA · SOLO CUANDO SOBRABA DINERO", 0.1, 0.06, 50)], tr="fade", td=0.2, tex=GFX)
    add(1134.5, kb("u_P0bVatS8Jdw.jpg", "in", "dark"), [big("SIN CARGA NI NEGOCIOS: SIEMPRE HABÍA OTRA OBRA", 0.1, 0.86, 56)], tex=DARK)
    add(1140.0, cus(G11.park_road, t0=-9, buy_t=-9), [big("A TROZOS · COMPRANDO LA TIERRA MILLA A MILLA", 0.1, 0.06, 52, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(1144.4, kb("w_highsmith.jpg", "in", "warm"), [big("HECHA PARA IR DESPACIO…", 0.1, 0.42, 72),
                                                    big("…Y CONSTRUIDA DESPACIO", w("también", 1147.5) - 1144.4, 0.58, 84, YELLOW, "pop")], tex=CLEAN)
    add(1149.4, V("2647", "u_XPfnxJP4GDs.jpg", 0.0, "warm"), [big("EN ESTE CAMINO, NADIE LLEGÓ NUNCA RÁPIDO", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)
    add(w("ni los", 1152.7), kb("u_iLpyO-jq4lM.jpg", "in", "warm"), [big("NI LOS KAINTUCKS", 0.0, 0.42, 84, WHITE, "pop"),
                                                                   big("CON LA PLATA COSIDA AL ABRIGO", 0.8, 0.58, 56, GREY_)], tex=CLEAN)
    add(w("ni el correo", 1156.6), kb("u_oathFTcFigc.jpg", "in", "warm"), [big("NI EL CORREO", 0.0, 0.42, 84, WHITE, "pop"), big("10 DÍAS DE VIAJE", 0.6, 0.58, 56, GREY_)],
        tex=CLEAN)
    add(w("ni jackson", 1159.8), fr("f_15790285613.jpg", None, "doc"), [Darken(0.3), big("NI JACKSON", 0.0, 0.42, 84, WHITE, "pop"),
                                                                       big("A PIE JUNTO A SUS ENFERMOS", 0.6, 0.58, 56, GREY_)], tex=CLEAN)
    add(w("ni busby", 1163.1), pick_w("busby", L("09868", kb("u_QdRnZlzYJPA.jpg", "in", "dark"), None), None),
        [Darken(0.45), big("NI BUSBY", 0.0, 0.42, 84, WHITE, "pop"), big("MURIÓ ESPERANDO", 0.5, 0.58, 56, GREY_)], tex=ARCH)
    add(w("ni tú", 1165.7), cus(G11.nobody_fast, times=[-5, -5, -5, -5, 0.2]), tr="fade", td=0.2, tex=GFX)
    add(1169.1, kb("f_44238521561.jpg", "out", "doc"), [Darken(0.45), big("LO QUE MATÓ AL PRIMER CAMINO FUE LA LENTITUD", 0.1, 0.42, 62, WHITE),
                                                      big("LO QUE SALVÓ AL SEGUNDO, TAMBIÉN", w("lo que salvó", 1172.0) - 1169.1, 0.58, 76, YELLOW)], tex=CLEAN)
    add(1174.5, kb("l_42698.jpg", "in", "doc"), [Darken(0.45), rich("¿CUÁL ES EL VIAJE DE VUELTA A CASA QUE MÁS LARGO SE TE HA HECHO?", ("casa",),
                                                                   w("cuál", 1176.4) - 1174.5, step=0.07, y=0.5, size=66, maxw=0.82)], tex=CLEAN)
    add(1180.0, V("1764", "u_Q29XMoSRNKo.jpg", 0.0, "doc"), [big("UNA MUDANZA", 0.0, 0.3, 72, WHITE, "pop"), big("UN REGRESO DE OTRO PAÍS", w("un regreso", 1181.6) - 1180.0, 0.46, 68, WHITE, "pop"),
                                                     big("LA CARRETERA INTERMINABLE CON LOS NIÑOS ATRÁS", w("una carretera", 1183.6) - 1180.0, 0.62, 54, YELLOW)], tex=CLEAN)
    add(1186.4, kb("l_42698.jpg", "out", "doc"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿CUÁL ES EL VIAJE DE VUELTA A CASA QUE MÁS",
                                 line2="LARGO SE TE HA HECHO EN LA VIDA?", cta="CUÉNTALO EN LOS COMENTARIOS"),
         rich("A veces lo que más recordamos de un viaje es lo que tardamos en llegar", ("tardamos",), w("a veces", 1188.0) - 1186.4 - 0.3, step=0.07,
              y=0.2, size=48, maxw=0.85)], tex=DARK)
    return S


def pick_w(name, fallback, cap):
    f = f"w_{name}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, "archival")
    return fallback


def pick_l(lid, fallback, cap):
    return L(lid, fallback, cap)
