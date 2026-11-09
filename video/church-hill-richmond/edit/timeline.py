"""The edit: every shot of the Church Hill Tunnel (Richmond) video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx3 as G3
import gfx4 as G4
import gfx5 as G5
import gfx7 as G7
import gfx8 as G8
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1118.90
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
GREEN = (60, 170, 90)
BLUE = (110, 170, 220)
IMG = os.path.join(ROOT, "assets", "img")
VIDDIR = os.path.join(ROOT, "assets", "vid")


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


# ------------------------------------------------------------------ Richmond specifics
TUNNEL = ["west_portal", "east_portal"]
COAL = ["charleston_wv", (-81.20, 38.10), (-80.88, 37.67), "white_sulphur", "cliftonforge", (-79.07, 38.15), (-78.48, 38.03),
        (-77.95, 37.85), "rich"]
TO_SEA = ["rich", (-77.10, 37.36), (-76.75, 37.17), "newport_news"]
AROUND = [(-77.4285, 37.5310), (-77.4233, 37.5272), (-77.4146, 37.5240), (-77.4100, 37.5250)]
GREY_ = (160, 160, 160)


def pick(primary, fallback):
    return primary if os.path.exists(os.path.join(IMG, primary)) else fallback


def card(lines, base="dark_grid"):
    """Typographic card on a dark background: lines = [(text, size, color, y, t0)]."""
    return Solid(base), [BigText(tx, "bebas", sz, col, (0.5, y), t0, None, "up", tracking=4) for tx, sz, col, y, t0 in lines]


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="f_6991547391.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.45), Badge(badge, 0.2, None)] +
            question("¿Por qué Richmond decidió sellar ese túnel con la locomotora y dos hombres dentro?", ("sellar",), size=68),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_nv_CLuGKJ-Q.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Y por qué, en cien años, nadie ha conseguido sacar ese tren?", ("nadie",), size=70), tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 63.9)
    add(0.0, fr("f_16217681043.jpg", "El túnel de Church Hill · postal antigua (VCU Libraries)"), [Badge("OCTUBRE DE 1925", 0.4, None)], tex=ARCH)
    add(2.40, mp("rc_reg", [(0, -78.6, 37.7, 0.55), (1.7, -77.6, 37.55, 0.75)],
                 [dict(type="state", name="Virginia", t0=0.0, color=GREY_, width=3, alpha=0.7),
                  dict(type="pin", at="rich", t0=0.3, label="RICHMOND, VIRGINIA", side="r", box=True, size=50)]), tr="zoom", td=0.3, tex=GFX)
    add(4.10, kb("u_Scij5JjDstA.jpg", "in", "dark"), [rich("ENTERRARON A UN MAQUINISTA DE TREN", ("maquinista",), 0.3, y=0.84, size=56)], tex=DARK)
    add(6.40, cus(G8.coffin, n_t=1.9, a_t=3.7, b_t=6.2), tr="fade", td=0.3, tex=DARK)
    add(14.70, kb("u_IQ5zJ-jYkJI.jpg", "in", "bw"), [rich("Y ESA LOCOMOTORA SIGUE HOY DONDE ÉL LA DEJÓ", ("hoy",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tr="fade", td=0.3, tex=ARCH)
    add(17.50, kb("u_nv_CLuGKJ-Q.jpg", "in", "none"), [torch(((0.45, 0.55), (0.55, 0.5)), r=420, amb=0.12), big("BAJO TIERRA · A OSCURAS", 0.2, 0.84, 72, YELLOW)],
        tex=DARK)
    add(19.60, kb("u_9O770ZdQQjs.jpg", "in", "dark"), [Counter(0, 10, "{:.0f}", "VAGONES ENGANCHADOS DETRÁS", 0.2, 0.9, (0.5, 0.45), 200)], tex=DARK)
    add(22.00, kb("f_52139781848.jpg", "in", "doc"), [rich("ENCIMA HAY UN PARQUE", ("parque",), 0.2, y=0.12, size=60),
                                                     LowerThird("JEFFERSON PARK", "Church Hill, Richmond · foto: schizoform (CC BY 2.0)", w("jefferson", 24.3) - 22.0)],
        tr="fade", td=0.3, tex=CLEAN)
    add(25.50, V("40657", "u_GvL__XG0to4.jpg", 1.0, "doc"), [big("CÉSPED", 0.1, 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(26.40, kb("u_rpl9UrPcRTI.jpg", "in", "doc"), [big("BANCAS", 0.0, 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(27.10, kb("u_zFDoHnPATY8.jpg", "in", "warm"), [rich("UNA DE LAS MEJORES VISTAS DEL CENTRO", ("vistas",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(29.90, V("4831", "u_U2H4HNrApd0.jpg", 0.5, "warm"), [rich("LOS NIÑOS CORREN POR LA HIERBA", ("niños",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(32.00, kb("u_AOMrugxXivY.jpg", "in", "warm"), [rich("LOS VECINOS VEN CAER LA TARDE SOBRE LOS EDIFICIOS", ("tarde",), 0.2, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(35.50, V("40656", "u_KFUMV4LY0lk.jpg", 0.5, "doc"), [rich("CASI NADIE PIENSA EN LO QUE TIENE DEBAJO DE LOS PIES", ("debajo",), 0.2, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(38.40, cus(G8.hill, mode="teaser", t0=0.1), tr="fade", td=0.3, tex=GFX)
    add(41.00, kb("u_nuqhqqpCeAQ.jpg", "in", "dark"), [big("AL MENOS DOS HOMBRES", 0.1, 0.42, 96, WHITE, "pop"),
                                                     big("QUE NUNCA SALIERON", 0.9, 0.58, 76, YELLOW)], tex=DARK)
    bg, ov = card([("DE UNO SE SABE EL NOMBRE COMPLETO", 46, (190, 190, 190), 0.25, 0.1), ("RICHARD LEWIS", 130, WHITE, 0.38, 0.6),
                   ("DEL OTRO, UNA INICIAL Y UN APELLIDO", 46, (190, 190, 190), 0.62, w("del", 45.4) - 43.4), ("H. SMITH", 130, YELLOW, 0.75, w("apenas", 46.3) - 43.4)])
    add(43.40, bg, ov, tr="black", td=0.2, tex=DARK)
    add(48.50, kb("u_74VbII_Eexo.jpg", "in", "dark"), [rich("Y PUEDE QUE NO SEAN LOS ÚNICOS", ("únicos",), 0.2, y=0.5, size=72)], tex=DARK)
    add(50.50, kb("u_bxoBooJleSM.jpg", "in", "bw"), [big("LA MÁQUINA TIENE NÚMERO", 0.1, 0.84, 72, YELLOW)], tex=ARCH)
    add(52.10, kb("u_9_8K9PMGa8Q.jpg", "in", "bw"), [Darken(0.5), big("ALGUNOS HOMBRES", 0.1, 0.42, 96, WHITE), big("NI SIQUIERA TIENEN NOMBRE", 0.6, 0.58, 76, YELLOW)],
        tex=ARCH)
    q1(54.60)
    q2(60.00)
    add(63.90, kb("f_6991547591.jpg", "in", "dark"),
        [Darken(0.45, 0.0, 0.3),
         BigText("CHURCH HILL", "bebas", 190, YELLOW, (0.5, 0.40), 0.1, None, "pop", tracking=10),
         BigText("El tren enterrado de Richmond", "serif_it", 70, WHITE, (0.5, 0.58), 0.45, None, "up"),
         Badge("CAPÍTULO 1 · LA COLINA DE LA LIBERTAD", 1.0, None)], tr="flash", td=0.25, tex=DARK)

    # ============================== CAP 1: LA COLINA DE LA LIBERTAD (63.9 - 198.2)
    add(68.60, kb("f_2899335954.jpg", "in", "archival"), [LowerThird("CHURCH HILL", "«La colina de la iglesia» · foto aérea, Library of Virginia", 0.3)], tr="fade", td=0.3, tex=ARCH)
    add(71.80, kb("l_4a16704.jpg", "in", "archival"), [Badge("SAINT JOHN'S CHURCH", 0.3, None)], tex=ARCH)
    add(74.90, kb("l_18146.jpg", "in", "archival"), [Badge("1775", 0.3, None), Caption("St. John's desde el banco de Patrick Henry · 1901", "Library of Congress", 1.0)], tex=ARCH)
    add(77.70, fr("l_3a10310.jpg"), [LowerThird("PATRICK HENRY", "Abogado · retrato de archivo", 0.6)], tex=ARCH)
    add(80.00, fr("l_08961.jpg", "«Give me liberty, or give me death!» · litografía de 1876 (Library of Congress)"), [rich("UNO DE LOS DISCURSOS MÁS FAMOSOS", ("famosos",), 0.2, y=0.065, size=50, maxw=0.95)],
        tex=ARCH)
    add(83.40, kb("l_08961.jpg", "in", "archival", cam0=(0.5, 0.45, 1.35), cam1=(0.5, 0.42, 1.55)), [Darken(0.6), rich("«DENME LA LIBERTAD O DENME LA MUERTE»", ("libertad", "muerte»"), w("denme", 84.8) - 83.4, step=0.15, y=0.5, size=72, maxw=0.8)],
        tex=ARCH)
    add(87.60, kb("f_51807193652.jpg", "in", "doc"), [Badge("DONDE NACIÓ EL PAÍS", 0.3, None)], tex=CLEAN)
    add(91.50, cus(G8.hill, mode="intro", t0=0.2), tr="fade", td=0.3, tex=GFX)
    add(95.40, kb("l_04082.jpg", "in", "archival"), [Badge("UN SIGLO DESPUÉS", 0.2, None), Caption("Richmond desde Gamble's Hill, con ruinas · 1865", "Library of Congress", 1.4)],
        tr="fade", td=0.3, tex=ARCH)
    add(98.60, kb("l_34850.jpg", "in", "archival"), [rich("LA CAPITAL DE LA CONFEDERACIÓN", ("confederación",), 0.2, y=0.86, size=56)], tex=ARCH)
    add(101.60, kb("l_34938.jpg", "in", "archival"), [big("1865 · TERMINA LA GUERRA CIVIL", 0.2, 0.86, 64, YELLOW)], tex=ARCH)
    add(105.80, kb("l_08232.jpg", "punch", "archival"), [big("EL CENTRO ARDIÓ EL ÚLTIMO DÍA", 0.2, 0.86, 64, YELLOW)], tex=ARCH)
    add(109.80, kb("l_80237.jpg", "in", "archival"), [rich("TERRENOS QUEMADOS · GENTE SIN TRABAJO", ("quemados", "trabajo"), 0.3, y=0.86, size=54)], tex=ARCH)
    add(113.80, kb("l_08225.jpg", "in", "archival"), [rich("LA CIUDAD NECESITABA DINERO Y UN FUTURO", ("futuro",), 0.2, y=0.86, size=54)], tex=ARCH)
    add(117.40, kb("u_t_-X3OIQVkA.jpg", "in", "doc"), [big("Y EL FUTURO LLEGABA EN TREN", 0.4, 0.84, 72, YELLOW)], tr="fade", td=0.3, tex=CLEAN)
    add(120.30, fr("l_28027.jpg", "Locomotora de vapor · 1909 (Library of Congress)"),
        [LowerThird("CHESAPEAKE AND OHIO", "La C&O", w("chesapeake", 123.0) - 120.3)], tex=ARCH)
    add(125.80, mp("rc_reg", [(0, -80.4, 37.9, 0.6), (4.0, -80.2, 37.9, 0.66)],
                   [dict(type="state", name="West Virginia", t0=0.2, color=YELLOW, width=4, fill=(80, 70, 40), alpha=0.6),
                    dict(type="label", at=(-81.0, 38.55), text="VIRGINIA OCCIDENTAL", t0=w("virginia", 128.8) - 125.8 - 0.4, size=54, box=True),
                    dict(type="label", at=(-80.9, 37.95), text="CARBÓN", t0=w("carbón", 127.3) - 125.8, size=60, color=YELLOW)]), tr="zoom", td=0.3, tex=GFX)
    add(129.80, kb("l_8a39584.jpg", "in", "archival"), [rich("EL CARBÓN BAJABA EN TREN", ("tren",), 0.2, y=0.86, size=58),
                                                      Caption("Tren de carbón en Virginia Occidental · 1938", "Library of Congress", 1.0, y=0.1)], tex=ARCH)
    add(132.50, mp("rc_reg", [(0, -79.6, 37.9, 0.6), (5.6, -78.2, 37.7, 0.66)],
                   [dict(type="route", path=COAL, t0=0.1, draw=2.4, color=YELLOW, width=6),
                    dict(type="pin", at="rich", t0=2.4, label="RICHMOND", side="r", size=44),
                    dict(type="label", at=(-77.3, 37.38), text="MUELLES DEL JAMES · BARCOS", t0=w("muelles", 135.2) - 132.5, size=44, box=True),
                    dict(type="label", at=(-79.4, 38.45), text="TRAZADO APROXIMADO", t0=1.0, size=30, color=GREY_)]), tr="fade", td=0.3, tex=GFX)
    add(138.10, V("3435", "u_RIERU5CXjpk.jpg", 0.5, "doc"), [rich("CADA TONELADA SOLO VALÍA DINERO SI LLEGABA A UN BARCO", ("barco",), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=DARK)
    add(142.70, mp("rc_loc", [(0, -77.4215, 37.5300, 0.72), (10.0, -77.4205, 37.5305, 0.85)],
                   [dict(type="pin", at="west_portal", t0=0.2, label="LAS VÍAS", side="l", size=46),
                    dict(type="label", at="docks", text="EL AGUA", t0=w("agua", 144.1) - 142.7, size=50, color=BLUE),
                    dict(type="label", at=(-77.4170, 37.5330), text="LA COLINA", t0=w("colina", 144.9) - 142.7, size=60, box=True),
                    dict(type="route", ll=M.rc_viaduct()[:40], t0=w("rodearla", 145.7) - 142.7, draw=1.2, color=GREY_, width=5, dash=14),
                    dict(type="label", at=(-77.4255, 37.5270), text="RODEARLA: LARGO", t0=w("rodearla", 145.7) - 142.7 + 0.4, size=40, color=GREY_),
                    dict(type="label", at=(-77.4170, 37.5372), text="SUBIRLA: IMPOSIBLE", t0=w("subirla", 147.2) - 142.7, size=40, color=RED),
                    dict(type="route", path=TUNNEL, t0=w("debajo", 152.1) - 142.7 - 0.4, draw=1.4, color=YELLOW, width=8, smooth=False),
                    dict(type="label", at=(-77.4150, 37.5308), text="POR DEBAJO", t0=w("debajo", 152.1) - 142.7 + 0.6, size=50, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(152.70, kb("l_34837.jpg", "in", "archival"), [rich("LA CIUDAD QUERÍA ESE TREN TANTO COMO LA COMPAÑÍA", ("ciudad",), 0.2, step=0.1, y=0.86, size=50, maxw=0.85),
                                                     Caption("Main Street desde Libby Hill · 1865", "Library of Congress", 1.6, y=0.1)], tr="fade", td=0.3, tex=ARCH)
    add(156.60, kb("u_agFtk6trGHA.jpg", "l", "bw"), [rich("SIN TÚNEL, EL CARBÓN PODÍA SALIR POR OTRO LADO", ("otro", "lado"), 0.2, step=0.1, y=0.84, size=52, maxw=0.85)], tex=ARCH)
    add(160.30, kb("l_08225.jpg", "l", "archival", z=1.1), [rich("DE CIUDAD DE PASO… A PUERTO", ("puerto",), 0.6, y=0.86, size=62),
                                                          Caption("Rocketts y el río James · 1864", "Library of Congress", 0.2, y=0.1)], tex=ARCH)
    add(166.50, kb("u_rvVhr2LngP4.jpg", "in", "doc"), [rich("EL CONCEJO HIZO ALGO QUE HOY SUENA RARO", ("raro",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(170.70, V("18305", "u_sUHD8WFjkB0.jpg", 0.5, "dark"), [big("CIENTOS DE MILES DE DÓLARES", 0.2, 0.42, 88, YELLOW, "pop"),
                                                            big("DE DINERO PÚBLICO", 0.8, 0.58, 66, WHITE)], tex=DARK)
    add(174.00, fr("f_16600696720.jpg", "Plano de los barrios Jackson y Jefferson, Richmond · VCU Libraries"),
        [rich("PARA QUE UNA EMPRESA PRIVADA CAVARA BAJO EL BARRIO", ("privada",), 0.2, step=0.1, y=0.065, size=44, maxw=0.95)], tex=ARCH)
    add(178.60, kb("f_14678311770.jpg", "in", "doc"), [Badge("CHURCH HILL · 1872", 0.2, None), rich("PONTE EN EL LUGAR DE UN VECINO", ("vecino",), 0.6, y=0.86, size=56)],
        tr="fade", td=0.3, tex=CLEAN)
    add(183.10, kb("u_IKDooOt3fAs.jpg", "in", "doc"), [rich("UNA CASA DE LADRILLO CON VISTAS AL RÍO", ("río",), 0.2, y=0.86, size=56)], tex=CLEAN)
    add(186.00, kb("f_14884875413.jpg", "up", "doc"), [big("UNA CALLE EMPINADA", 0.1, 0.86, 70)], tex=CLEAN)
    add(187.60, kb("f_9438589255.jpg", "in", "doc"), [rich("CERCA DE LA IGLESIA MÁS FAMOSA DE LA CIUDAD", ("famosa",), 0.2, step=0.1, y=0.86, size=52, maxw=0.85)], tex=CLEAN)
    add(190.20, kb("u_2PKKbKEkmQE.jpg", "in", "doc"), [big("TRENES POR DEBAJO DE TU SALA", 0.4, 0.84, 76, YELLOW, "pop")], tex=CLEAN)
    add(193.90, kb("u_0NZybxVDI24.jpg", "in", "doc"), [rich("¿DE QUÉ ESTÁ HECHA LA TIERRA QUE PISAS?", ("tierra",), 0.4, y=0.5, size=72)], tex=CLEAN)

    # ============================== CAP 2: LA OBRA (198.2 - 329.6)
    bg, ov = chapter(2, "La obra", None, year="1872 – 1874", base=fr("l_05404.jpg", g="archival"))
    add(198.20, bg, ov + [Caption("Túnel de la C&O en Virginia Occidental · 1872", "Library of Congress", 0.8)], tr="flash", td=0.25, tex=ARCH)
    add(201.60, kb("u_jhjixIHT5cg.jpg", "in", "doc"), [Darken(0.55), rich("LA COLINA CONTESTÓ ENSEGUIDA", ("enseguida",), 0.1, y=0.12, size=56),
                                                     big("NO ERA ROCA", w("roca", 203.9) - 201.6 - 0.4, 0.84, 96, YELLOW, "pop")], tex=CLEAN)
    add(204.60, kb("u_RoAhv3M5DUI.jpg", "in", "cold"), [rich("ARCILLA AZULADA · BLANDA · HÚMEDA", ("azulada", "blanda", "húmeda"), 0.2, step=0.4, y=0.84, size=62)], tex=CLEAN)
    add(207.40, kb("u_u4ijcCaprRc.jpg", "in", "cold"), [rich("SE MUEVE EN CUANTO LE QUITAS ALGO DE DEBAJO", ("mueve",), 0.3, step=0.1, y=0.84, size=54, maxw=0.85)], tex=CLEAN)
    add(211.80, cus(G8.plasticine, close_t=w("pero", 216.7) - 211.8), tr="fade", td=0.3, tex=GFX)
    add(218.80, fr("l_06921.jpg", "Método para cavar túneles en tierra · grabado de 1837 (Library of Congress)"),
        [rich("DE POCO EN POCO, APUNTALANDO CON MADERA", ("madera",), 0.4, step=0.1, y=0.065, size=48, maxw=0.95)], tex=ARCH)
    add(224.00, cus(G8.hill, mode="dig", t0=0.0), tr="fade", td=0.3, tex=GFX)
    add(228.30, fr("l_09198.jpg", "Entibado de madera en un túnel · 1904 (Library of Congress)"),
        [rich("TU VIDA DEPENDÍA DEL ÚLTIMO PUNTAL", ("puntal",), 0.3, step=0.1, y=0.065, size=50, maxw=0.95)], tex=ARCH)
    add(233.50, kb("u_PDhSqtLG4cw.jpg", "in", "doc"), [big("LENTO Y PELIGROSO", 0.4, 0.84, 84, YELLOW, "pop")], tex=DARK)
    add(235.70, kb("u_TgtKBX2-_do.jpg", "in", "dark"), [rich("LA COLINA SE COBRÓ LA PRIMERA VIDA", ("vida",), 0.4, y=0.84, size=58)], tex=DARK)
    bg, ov = card([("A LOS CUATRO MESES", 50, (190, 190, 190), 0.3, 0.2), ("JAMES BOLTON", 150, WHITE, 0.46, 1.0),
                   ("INGENIERO AYUDANTE", 54, YELLOW, 0.6, 1.6), ("LE CAYÓ ENCIMA TIERRA DEL TECHO", 50, (190, 190, 190), 0.74, w("cayó", 242.2) - 238.3)])
    add(238.30, bg, ov, tr="black", td=0.2, tex=DARK, post=postshake(0))
    add(244.30, kb("u_S9yS7UTB1h0.jpg", "in", "dark"), [Darken(0.55), big("LO PEOR LLEGÓ EN ENERO DE 1873", 0.3, 0.5, 84, YELLOW, "pop")], tex=DARK)
    add(247.30, kb("u_YeZHDQJDEX8.jpg", "punch", "bw"), [rich("UNA NOCHE, GRIETAS EN LAS CALLES SOBRE EL TÚNEL", ("grietas",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=ARCH, post=postshake(2))
    add(251.10, kb("u_rNBaaxyeWWM.jpg", "in", "dark"), [rich("LA CIUDAD SACÓ A LOS VECINOS DE SUS CASAS", ("vecinos",), 0.3, y=0.84, size=56)], tex=DARK)
    add(254.20, cus(G8.hill, mode="sink", t0=w("hundió", 258.4) - 254.2 - 2.0, tumble_t=w("voltereta", 266.5) - 254.2 - 0.6),
        [rich("UN TROZO DEL TAMAÑO DE UNA CUADRA PEQUEÑA", ("cuadra",), 1.4, step=0.1, y=0.93, size=44, maxw=0.9)], tr="fade", td=0.3, tex=GFX,
        post=None)
    add(267.60, kb("l_02516.jpg", "in", "archival"), [rich("TAMBIÉN, PARTE DE LA CASA DEL PÁRROCO DE SAINT JOHN", ("párroco",), 0.3, step=0.1, y=0.88, size=48, maxw=0.85),
                                                    Caption("St. John's desde el cementerio · 1865", "Library of Congress", 0.2, y=0.1)], tex=ARCH)
    add(273.70, kb("u_4dPHQviRbWo.jpg", "in", "bw"), [Darken(0.55), big("TERCERA IGLESIA PRESBITERIANA", 0.3, 0.42, 72, WHITE),
                                                    Stamp("DESTRUIDA", w("destruido", 278.3) - 273.7, RED, (0.5, 0.62), -6, 100)], tex=ARCH)
    add(280.40, kb("u_ESqdY3R98-Y.jpg", "in", "dark"), [Darken(0.55), big("LA COLINA ESTABA AVISANDO", 0.2, 0.42, 84, WHITE),
                                                      big("NADIE QUISO ESCUCHARLA", w("nadie", 283.2) - 280.4, 0.6, 76, RED, "pop")], tex=DARK)
    add(284.70, fr("l_3a30161.jpg", "Pala de vapor en una obra de ferrocarril · 1906"), [big("LAS OBRAS SIGUIERON", 0.1, 0.065, 66, YELLOW)], tex=ARCH)
    add(286.40, fr("f_16217681043.jpg", "El túnel de Church Hill · postal antigua (VCU Libraries)"), [Badge("FINALES DE 1873", 0.2, None),
                                                                                                    big("TERMINADO", 1.4, 0.065, 70, YELLOW)], tex=ARCH)
    add(291.20, cus(G8.hill, mode="done", t0=0.2), tr="fade", td=0.3, tex=GFX)
    add(300.00, mp("rc_loc", [(0, -77.4200, 37.5300, 0.72), (3.0, -77.4190, 37.5290, 0.78)],
                   [dict(type="route", path=TUNNEL, t0=0.0, draw=0.8, color=YELLOW, width=8, smooth=False),
                    dict(type="pin", at="docks", t0=0.8, label="LOS MUELLES", side="r", box=True, size=46)]), tr="zoom", td=0.3, tex=GFX)
    add(303.00, kb("u_IQ5zJ-jYkJI.jpg", "out", "bw"), [rich("EL PRIMER TREN CRUZÓ ANTES DE QUE ACABARA EL AÑO", ("primer",), 0.2, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=ARCH)
    add(305.50, kb("u_B-JJxUzeX3M.jpg", "in", "doc"), [rich("PERO EL PRECIO YA ESTABA PAGADO", ("precio",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(308.60, kb("u_PHQkRcLYXBs.jpg", "in", "sepia"), [Darken(0.6), Badge("1874 · UNA REVISTA CIENTÍFICA", 0.2, None), big("6 O 7 MUERTOS", w("seis", 312.7) - 308.6, 0.5, 130, YELLOW, "pop")],
        tex=ARCH)
    add(314.30, kb("u_OwDG_-_T2Co.jpg", "in", "doc"), [big("NUNCA FUE UN BUEN TÚNEL", 0.4, 0.84, 76, WHITE)], tex=CLEAN)
    add(316.80, kb("u_NWZRr1mrn1g.jpg", "in", "cold"), [Darken(0.55), big("LA ARCILLA SEGUÍA MOVIÉNDOSE", 0.1, 0.84, 70, YELLOW)], tex=CLEAN)
    add(318.80, V("2716", "u_Nw_D8v79PM4.jpg", 0.5, "cold"), [big("EL AGUA SE FILTRABA POR TODAS PARTES", 0.1, 0.84, 64)], tex=CLEAN)
    add(321.20, kb("u__Ppf7roueMA.jpg", "in", "bw"), [big("LOS LADRILLOS SUFRÍAN", 0.1, 0.84, 70)], tex=ARCH)
    add(322.60, V("2846", "u_ZxZQk7777R4.jpg", 0.5, "doc"), [rich("COMO UNA CASA CON GOTERAS QUE NUNCA SE ARREGLAN DEL TODO", ("goteras",), 0.2, step=0.09, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(326.50, kb("u_S-eIM6dq7Jw.jpg", "in", "dark"), [rich("FUNCIONABA… PERO HABÍA QUE VIGILARLA SIEMPRE", ("vigilarla",), 0.2, y=0.84, size=54)], tex=DARK)

    # ============================== CAP 3: EL ABANDONO Y LA VUELTA (329.6 - 466.5)
    bg, ov = chapter(3, "El abandono y la vuelta", None, year="1881 – 1925", base=fr("l_160659p.jpg", g="archival"))
    add(329.60, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(333.10, kb("l_8a39062.jpg", "in", "archival"), [big("TRENES DE CARBÓN · CASI 30 AÑOS", 0.1, 0.86, 62, YELLOW)], tex=ARCH)
    add(334.80, mp("rc_reg", [(0, -77.5, 37.4, 0.85), (6.0, -77.1, 37.25, 0.95)],
                   [dict(type="pin", at="rich", t0=0.1, label="RICHMOND", side="l", size=44),
                    dict(type="route", path=TO_SEA, t0=0.6, draw=2.0, color=YELLOW, width=6),
                    dict(type="pin", at="newport_news", t0=w("newport", 339.0) - 334.8, label="NEWPORT NEWS · 1881", side="r", box=True, size=46),
                    dict(type="label", at=(-76.25, 37.55), text="BAHÍA DE CHESAPEAKE", t0=w("bahía", 340.4) - 334.8, size=40, color=BLUE)]),
        tr="zoom", td=0.3, tex=GFX)
    add(341.80, kb("l_8a38669.jpg", "in", "archival"), [rich("EL CARBÓN PASABA BAJO CHURCH HILL RUMBO AL MAR", ("mar",), 0.4, step=0.1, y=0.86, size=50, maxw=0.85)], tex=ARCH)
    add(347.30, fr("f_16217681043.jpg"), [rich("LA COLINA LO AGUANTABA COMO PODÍA", ("podía",), w("colina", 349.7) - 347.3, y=0.065, size=50, maxw=0.95)], tex=ARCH)
    add(351.50, kb("l_4a24185.jpg", "in", "archival"), [rich("OTRA FORMA DE LLEGAR AL RÍO", ("río",), 0.4, y=0.86, size=60)], tex=ARCH)
    add(355.80, mp("rc_loc", [(0, -77.4190, 37.5285, 0.72), (6.5, -77.4170, 37.5270, 0.80)],
                   [dict(type="route", path=TUNNEL, t0=0.0, draw=0.1, color=GREY_, width=8, smooth=False),
                    dict(type="route", ll=M.rc_viaduct(), t0=0.6, draw=2.2, color=YELLOW, width=8),
                    dict(type="label", at=(-77.4175, 37.5228), text="VIADUCTO DE ACERO · 1901", t0=1.6, size=50, box=True),
                    dict(type="label", at=(-77.4150, 37.5320), text="EL TÚNEL", t0=0.4, size=40, color=GREY_),
                    dict(type="label", at=(-77.4290, 37.5235), text="RÍO JAMES", t0=w("james", 359.8) - 355.8, size=44, color=BLUE)]),
        tr="zoom", td=0.3, tex=GFX)
    add(362.30, fr("l_162206p.jpg", "El viaducto de la C&O junto al James · HAER, Library of Congress"),
        [rich("MÁS SEGURO · MÁS SECO · MÁS FÁCIL", ("seguro", "seco", "fácil"), 0.3, step=0.25, y=0.065, size=50, maxw=0.95)], tex=ARCH)
    add(366.10, fr("f_16217681043.jpg"), [Stamp("1902 · FUERA DE USO", w("dejó", 368.6) - 366.1, RED, (0.5, 0.5), -10, 96)], tex=ARCH)
    add(370.00, kb("u_SuOFXGBGmkM.jpg", "in", "dark"), [rich("NO LO RELLENARON NI LO TAPIARON", ("rellenaron", "tapiaron"), 0.1, y=0.84, size=58)], tex=DARK)
    add(372.20, kb("u_nv_CLuGKJ-Q.jpg", "in", "none"), [torch(((0.4, 0.5), (0.6, 0.5)), r=460, amb=0.15),
                                                       rich("CASI 4.000 PIES DE OSCURIDAD BAJO EL BARRIO", ("oscuridad",), 0.3, step=0.1, y=0.84, size=54, maxw=0.85)], tex=DARK)
    add(378.20, cus(G8.hill, mode="leak", t0=0.1, props_t=99), tr="fade", td=0.3, tex=GFX)
    add(381.20, kb("u_9O770ZdQQjs.jpg", "in", "dark"), [rich("PAGADO CON DINERO DE LA CIUDAD Y CON VIDAS DE OBREROS", ("vidas",), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=DARK)
    add(386.00, kb("f_3595198231.jpg", "in", "archival"), [rich("DORMIDO BAJO UN BARRIO ENTERO", ("dormido",), 0.2, y=0.86, size=58),
                                                         Caption("Church Hill y Tobacco Row · 1958", "Library of Virginia", 0.6, y=0.1)], tex=ARCH)
    add(388.40, kb("l_4a12494.jpg", "in", "archival"), [rich("LA CIUDAD SIGUIÓ CRECIENDO ENCIMA", ("encima",), 0.2, y=0.86, size=58)], tex=ARCH)
    add(390.50, mp("rc_loc", [(0, -77.4150, 37.5285, 1.1), (4.6, -77.4148, 37.5282, 1.2)],
                   [dict(type="route", path=TUNNEL, t0=0.0, draw=0.1, color=GREY_, width=10, smooth=False),
                    dict(type="pin", at="east_portal", t0=0.3, label="1913 · ALARGAN LA BOCA ESTE", side="r", box=True, size=46),
                    dict(type="label", at=(-77.4150, 37.5262), text="PARA ABRIR UNA CALLE NUEVA", t0=w("calle", 394.4) - 390.5, size=42)]),
        tr="zoom", td=0.3, tex=GFX)
    add(395.10, kb("u_rvVhr2LngP4.jpg", "in", "doc"), [Badge("1915 · UN INFORME", 0.2, None), rich("LO QUE TODOS SOSPECHABAN", ("sospechaban",), 1.2, y=0.84, size=58)],
        tex=CLEAN)
    add(399.20, fr("l_09197.jpg", "Túnel reforzado con madera · 1904 (Library of Congress)"), [big("NECESITABA REFUERZOS", 0.3, 0.065, 70, YELLOW)], tex=ARCH)
    add(401.50, cus(G8.hill, mode="leak", t0=-1.6, props_t=0.2), tr="fade", td=0.3, tex=GFX)
    add(405.40, kb("l_8a39551.jpg", "in", "archival"), [rich("PERO EL TRÁFICO DE CARBÓN NO DEJABA DE CRECER", ("crecer",), 0.2, step=0.1, y=0.86, size=52, maxw=0.85)], tex=ARCH)
    add(408.80, kb("u_TJjnHzn31gw.jpg", "in", "doc"), [rich("EL VIADUCTO SE QUEDABA CORTO", ("corto",), 0.2, y=0.84, size=58)], tex=CLEAN)
    add(411.10, kb("u_8QZz0b3wsvE.jpg", "in", "doc"), [big("MÁS VÍAS", 0.2, 0.84, 96, YELLOW, "pop")], tex=CLEAN)
    add(413.40, kb("f_16217681043.jpg", "in", "archival"), [Darken(0.55), rich("YA ERA SUYO · YA ESTABA CAVADO · YA HABÍA COSTADO DINERO Y VIDAS", ("suyo", "cavado", "vidas"),
                                                                       w("ya", 415.9) - 413.4, step=0.12, y=0.5, size=56, maxw=0.8)], tex=ARCH)
    add(420.60, V("10395", "u_0gkw_9fy0eQ.jpg", 0.5, "dark"), [Badge("1925", 0.2, None), big("LA C&O TOMÓ UNA DECISIÓN", 0.8, 0.84, 70, YELLOW)], tex=DARK)
    add(425.00, fr("l_3b36023.jpg", "Revestimiento de concreto en un túnel · 1934 (Library of Congress)"),
        [rich("VOLVER A ENTRAR · ARCOS DE CONCRETO", ("concreto",), 0.3, step=0.15, y=0.065, size=50, maxw=0.95)], tex=ARCH)
    add(429.90, kb("u_d8OykIsYfDo.jpg", "in", "doc"), [rich("EN EL PAPEL TENÍA LÓGICA", ("lógica",), 0.2, y=0.4, size=70),
                                                     rich("EL CONCRETO, MÁS FUERTE QUE EL LADRILLO", ("concreto",), 2.2, y=0.58, size=54)], tex=CLEAN)
    add(434.30, kb("u__Ppf7roueMA.jpg", "in", "bw"), [rich("PARA PONER UN ARCO NUEVO HABÍA QUE QUITAR PARTE DEL VIEJO", ("quitar",), 0.2, step=0.09, y=0.84, size=50, maxw=0.85)],
        tex=ARCH)
    add(438.60, kb("u_jhjixIHT5cg.jpg", "punch", "doc"), [rich("EN UNA COLINA QUE LLEVABA MEDIO SIGLO MOVIÉNDOSE", ("moviéndose",), 0.2, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(442.80, fr("l_3c07164.jpg", "Cuadrilla cargando traviesas · hacia 1920 (Library of Congress)"), [Badge("SEPTIEMBRE DE 1925", 0.3, None),
                                                                                                    big("VOLVIERON LAS CUADRILLAS", 1.2, 0.07, 60, YELLOW)], tex=ARCH)
    add(446.80, kb("u_9_8K9PMGa8Q.jpg", "in", "bw"), [rich("CIENTOS DE HOMBRES, MUCHOS DE ELLOS JORNALEROS NEGROS", ("jornaleros", "negros"), 0.2, step=0.1, y=0.86, size=50, maxw=0.85)],
        tex=ARCH)
    add(451.00, kb("u_qefCF3r4Eoc.jpg", "punch", "dark"), [big("PICOS Y PALAS", 0.1, 0.84, 84, YELLOW, "pop")], tex=DARK)
    add(452.40, kb("u_W-wCP4zdscI.jpg", "in", "doc"), [big("UN TÚNEL CERRADO DESDE HACÍA MÁS DE 20 AÑOS", 0.2, 0.86, 58)], tex=CLEAN)
    # subscribe CTA
    add(455.20, kb("f_6991547391.jpg", "in", "dark"), [Darken(0.4), rich("ANTES DE ENTRAR CON ELLOS… UNA COSA", ("cosa",), 0.2, y=0.4, size=62),
                                                     rich("HISTORIAS DE LO QUE QUEDÓ ENTERRADO BAJO LAS CIUDADES", ("enterrado",), w("historias", 459.3) - 455.2, step=0.1, y=0.56, size=50, maxw=0.85)],
        tr="fade", td=0.3, tex=DARK)
    add(461.80, kb("f_6991547391.jpg", "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe),
                                                             big("ESOS HOMBRES MERECEN QUE ALGUIEN SE ACUERDE DE ELLOS", w("esos", 463.5) - 461.8, 0.3, 54, YELLOW)], tex=DARK)

    # ============================== CAP 4: EL 2 DE OCTUBRE DE 1925 (466.5 - 597.0)
    bg, ov = chapter(4, "El 2 de octubre", None, year="1925", base=V("4422", "u_rNBaaxyeWWM.jpg", 1.0, "dark"))
    add(466.50, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(469.80, V("2716", "u_Nw_D8v79PM4.jpg", 2.0, "cold"), [rich("LA ARCILLA ESTABA EMPAPADA", ("empapada",), 0.3, y=0.84, size=62)], tex=CLEAN)
    add(472.10, cus(G4.calendar, cards=[("2", "OCTUBRE DE 1925", "VIERNES", 0.2, (60, 62, 66))], title="EL DÍA"), tr="fade", td=0.3, tex=GFX)
    add(475.00, cus(G8.hill, mode="work", t0=0.2), tr="fade", td=0.3, tex=GFX)
    add(481.80, kb("u_IQ5zJ-jYkJI.jpg", "in", "bw"), [LowerThird("LOCOMOTORA 231", "Cerca de la boca oeste", w("locomotora", 483.9) - 481.8)], tex=ARCH)
    add(486.00, kb("u_IHdI6Sdo4U4.jpg", "in", "dark"), [LowerThird("THOMAS MASON", "Maquinista", 0.6)], tex=DARK)
    add(488.30, fr("l_3a41429.jpg", "Tren de vagones plataforma · 1904 (Library of Congress)"),
        [Counter(0, 10, "{:.0f}", "VAGONES PLATAFORMA", 0.4, 0.9, (0.5, 0.42), 170)], tex=ARCH)
    add(491.50, kb("u_2PKKbKEkmQE.jpg", "in", "doc"), [rich("DESPACIO, COMO DENTRO DE UN TÚNEL EN OBRAS", ("despacio",), 0.3, step=0.1, y=0.84, size=54, maxw=0.85)], tex=CLEAN)
    add(495.20, kb("u_WYh-Ux5LmHI.jpg", "in", "dark"), [LowerThird("BENJAMIN MOSBY", "Fogonero", w("benjamin", 497.9) - 495.2)], tex=DARK)
    add(499.00, V("3443", "u_RIERU5CXjpk.jpg", 0.5, "doc"), [rich("MANTENER VIVO EL FUEGO DE LA CALDERA", ("fuego",), 0.3, y=0.84, size=58)], tex=DARK)
    add(502.20, kb("u_B-JJxUzeX3M.jpg", "in", "doc"), [rich("UN DÍA DE TRABAJO NORMAL", ("normal",), 0.1, y=0.4, size=70),
                                                     rich("NADIE ESPERABA NADA DISTINTO", ("nadie",), w("nadie", 504.2) - 502.2, y=0.58, size=56)], tex=CLEAN)
    add(507.90, kb("u_nv_CLuGKJ-Q.jpg", "in", "none"), [torch(((0.45, 0.5), (0.55, 0.5)), r=440, amb=0.12), Badge("POCO DESPUÉS DE LAS 3 DE LA TARDE", 0.2, None),
                                                       big("LA COLINA AVISÓ POR ÚLTIMA VEZ", w("colina", 510.3) - 507.9, 0.84, 66, YELLOW)], tex=DARK)
    add(512.30, kb("u_OwDG_-_T2Co.jpg", "in", "doc"), [rich("CAEN LADRILLOS DEL TECHO AL AGUA DE LAS VÍAS", ("ladrillos",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN, post=postshake(3))
    add(516.60, V("3676", "u_ybDP4a_VdMk.jpg", 0.5, "doc"), [big("LAS LUCES PARPADEAN DOS VECES", 0.3, 0.84, 66, YELLOW)], tex=DARK)
    add(518.60, cus(G8.hill, mode="collapse", t0=w("vino", 520.7) - 518.6 - 2.0), tr="fade", td=0.2, tex=GFX, post=postshake(6))
    add(526.50, Solid("black"), [big("LAS LUCES SE APAGARON", 0.0, 0.5, 120, WHITE, "pop")], tr="black", td=0.1, tex=DARK)
    add(528.40, kb("u_bXT0rIrfMzs.jpg", "in", "dark"), [rich("LA BOCA OESTE, A SOLO 100 PIES · 30 M", ("100",), 0.2, y=0.4, size=60),
                                                      big("EL DERRUMBE LA HABÍA TAPADO", w("derrumbe", 532.9) - 528.4, 0.58, 76, RED, "pop")], tex=DARK)
    add(534.50, cus(G8.tunnel_run, t0=0.2), [big("SOLO QUEDABA UNA DIRECCIÓN", 0.2, 0.2, 64, YELLOW)], tr="fade", td=0.2, tex=DARK)
    add(537.00, kb("u_TdOHDpcyzZU.jpg", "in", "dark"), [rich("IMAGINA ESTAR AHÍ", ("ahí",), 0.1, y=0.3, size=72),
                                                      rich("OYES EL TECHO CAER DETRÁS · NO VES NADA", ("nada",), 1.4, step=0.1, y=0.5, size=56, maxw=0.85)], tex=DARK)
    add(541.60, cus(G8.tunnel_run, t0=-2.0), tr="fade", td=0.2, tex=DARK)
    add(547.40, kb("u_VpkNCd5d_4Y.jpg", "in", "sepia"), [rich("LOS PERIÓDICOS DEL DÍA SIGUIENTE", ("periódicos",), 0.2, y=0.84, size=58)], tex=ARCH)
    add(550.00, kb("u_kqgC_6j6AaA.jpg", "in", "dark"), [rich("CORRIENDO A CIEGAS · GRITANDO · TROPEZANDO CONTRA LAS PAREDES", ("ciegas", "gritando", "tropezando"), 0.2, step=0.3,
                                                             y=0.84, size=50, maxw=0.9)], tex=DARK, post=postshake(2))
    add(554.10, kb("u_iDF0FXUxGhE.jpg", "in", "dark"), [big("BUSCANDO LA LUZ CON LAS MANOS", 0.1, 0.84, 66, YELLOW)], tex=DARK)
    add(556.30, kb("u_CfSE-yO-0bQ.jpg", "in", "dark"), [rich("ALGUNOS SE ARRASTRARON BAJO LOS VAGONES", ("arrastraron",), 0.2, y=0.84, size=56)], tex=DARK)
    add(559.20, kb("u_nv_CLuGKJ-Q.jpg", "out", "doc"), [big("CASI TODOS SALIERON", 0.1, 0.42, 96, WHITE), big("UN PEQUEÑO MILAGRO", w("pequeño", 561.8) - 559.2, 0.58, 70, YELLOW)],
        tex=DARK)
    add(563.10, cus(G8.tunnel_run, t0=-4.0), [rich("MÁS DE UN KILÓMETRO A OSCURAS, CON LA COLINA CAYENDO DETRÁS", ("oscuras",), 0.3, step=0.1, y=0.2, size=50, maxw=0.88)],
        tr="fade", td=0.2, tex=DARK)
    add(568.20, Solid("black"), [big("PERO NO TODOS LO LOGRARON", 0.1, 0.5, 100, RED, "pop")], tr="black", td=0.1, tex=DARK)
    add(570.10, kb("u_IzLWSbMoCPo.jpg", "punch", "dark"), [rich("LA TIERRA APLASTÓ LA CABINA DE LA LOCOMOTORA", ("cabina",), 0.2, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=DARK, post=postshake(4))
    add(574.50, kb("u_IHdI6Sdo4U4.jpg", "punch", "dark"), [big("MASON QUEDÓ ATRAPADO DENTRO", 0.2, 0.84, 72, YELLOW, "pop")], tex=DARK)
    add(576.90, V("1964", "u_QxhBhL-4oL0.jpg", 0.5, "dark"), [rich("SE ROMPIÓ LA CALDERA · EL VAPOR SALIÓ DE GOLPE", ("vapor",), 0.2, step=0.1, y=0.84, size=54, maxw=0.85)], tex=DARK,
        post=postshake(3))
    add(579.80, kb("u_JKAKwrATVq8.jpg", "in", "warm"), [big("QUEMA LA PIEL EN SEGUNDOS", 0.2, 0.84, 76, YELLOW, "pop")], tex=DARK)
    bg, ov = card([("A SU LADO", 50, (190, 190, 190), 0.32, 0.1), ("BENJAMIN MOSBY", 140, WHITE, 0.47, 0.4),
                   ("SE LLEVÓ LA PEOR PARTE", 60, RED, 0.63, w("peor", 584.7) - 582.6)])
    add(582.60, bg, ov, tr="black", td=0.2, tex=DARK)
    add(586.10, kb("u_rzCi3mD-6ho.jpg", "in", "dark"), [rich("AUN ASÍ, SALIÓ CAMINANDO", ("caminando",), 0.2, y=0.3, size=66),
                                                      rich("¾ DE MILLA A OSCURAS, CON EL CUERPO ESCALDADO", ("escaldado",), w("recorrió", 588.8) - 586.1, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=DARK)
    add(592.60, kb("u_7WHr0xmGiBA.jpg", "in", "dark"), [LowerThird("HOSPITAL GRACE", "Richmond", 0.4)], tex=ARCH)
    add(595.20, kb("u_L_QJabM3f-U.jpg", "in", "dark"), [big("MURIÓ UNAS 7 HORAS DESPUÉS", 0.1, 0.84, 70, YELLOW)], tex=DARK)

    # ============================== CAP 5: LOS QUE NO SALIERON (597.0 - 717.6)
    bg, ov = chapter(5, "Los que no salieron", "f_52139781848.jpg", year="OCTUBRE DE 1925")
    add(597.00, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(599.80, kb("u_S9yS7UTB1h0.jpg", "punch", "doc"), [Darken(0.55), big("ARRIBA, LA TIERRA TAMBIÉN SE MOVIÓ", 0.1, 0.84, 66, YELLOW)], tex=CLEAN, post=postshake(4))
    add(601.80, kb("u_iRBti2TQePA.jpg", "in", "doc"), [rich("UNA GRIETA DE 100 PIES DE LARGO Y 20 DE HONDO", ("100", "20"), 0.3, step=0.1, y=0.84, size=54, maxw=0.85)], tex=CLEAN)
    add(606.00, kb("u_JRn81Q4P9m4.jpg", "in", "doc"), [rich("SE TRAGÓ UNA ACERA Y UNA ESCALERA", ("acera", "escalera"), 0.2, y=0.84, size=58)], tex=CLEAN)
    add(608.60, V("4831", "u_U2H4HNrApd0.jpg", 3.0, "doc"), [rich("POCO ANTES HABÍAN CRUZADO POR AHÍ UNOS NIÑOS", ("niños",), 0.2, step=0.1, y=0.84, size=54, maxw=0.85)], tex=CLEAN)
    add(611.60, kb("f_14862529594.jpg", "in", "doc"), [rich("NO CAYÓ NINGUNA CASA", ("ninguna",), 0.1, y=0.12, size=58),
                                                     rich("SOLO SE LLEVÓ A LOS QUE ESTABAN DEBAJO", ("debajo",), w("colina", 614.1) - 611.6, step=0.1, y=0.86, size=54, maxw=0.85)], tex=CLEAN)
    add(616.90, kb(pick("w_00.jpg", "u_bXT0rIrfMzs.jpg"), "in", "archival" if os.path.exists(os.path.join(IMG, "w_00.jpg")) else "dark"),
        [rich("NO PODÍAN ENTRAR POR LAS BOCAS: EL TECHO SEGUÍA CAYENDO", ("cayendo",), 0.3, step=0.1, y=0.86, size=48, maxw=0.88)], tex=ARCH)
    add(621.90, kb("l_3a30161.jpg", "in", "archival", cam0=(0.62, 0.45, 1.3), cam1=(0.62, 0.42, 1.5)), [big("EXCAVARON DESDE ARRIBA", 0.3, 0.84, 72, YELLOW)], tex=ARCH)
    add(624.50, cus(G8.hill, mode="rescue", t0=0.3), tr="fade", td=0.3, tex=GFX)
    add(630.80, kb(pick("w_00.jpg", "l_3a38263.jpg"), "in", "archival"), [big("MEDIA CIUDAD SE ACERCÓ A MIRAR", 0.4, 0.86, 64, YELLOW)], tex=ARCH)
    add(633.30, kb("u_0NZybxVDI24.jpg", "punch", "doc"), [rich("CADA VEZ QUE AVANZABAN, LA ARCILLA SE DERRUMBABA", ("derrumbaba",), 0.2, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN, post=postshake(3))
    add(637.10, V("28901", "u_S-eIM6dq7Jw.jpg", 1.0, "dark"), [big("MÁS DE UNA SEMANA", 0.3, 0.84, 80, YELLOW, "pop")], tex=DARK)
    bg, ov = card([("ALLÍ ESTABA", 54, (190, 190, 190), 0.38, 0.0), ("THOMAS MASON", 150, WHITE, 0.53, 0.3)])
    add(640.10, bg, ov, tr="black", td=0.2, tex=DARK)
    add(641.80, kb("u_nuqhqqpCeAQ.jpg", "in", "dark"), [big("EL ÚNICO CUERPO QUE SE SACÓ DE LA COLINA", 0.2, 0.5, 70, YELLOW)], tex=DARK)
    add(644.60, kb("u_gYC68k9trV8.jpg", "in", "cold"), [rich("LO ENTERRARON POCO DESPUÉS", ("enterraron",), 0.2, y=0.84, size=58)], tex=DARK)
    add(646.30, cus(G8.coffin, n_t=w("231", 648.9) - 646.3 - 0.3, a_t=None, b_t=w("máquina", 651.0) - 646.3, bottom="EL DE LA MÁQUINA EN LA QUE MURIÓ"),
        tr="fade", td=0.3, tex=DARK)
    add(652.50, kb("u_74VbII_Eexo.jpg", "in", "dark"), [big("FALTABAN DOS HOMBRES", 0.3, 0.42, 96, WHITE),
                                                      big("DOS JORNALEROS", w("jornaleros", 654.5) - 652.5, 0.58, 70, YELLOW)], tex=DARK)
    add(657.00, cus(G8.company_list, mode="list", row_t=0.1, hl_t=w("smith", 660.8) - 657.0 + 0.2), tr="fade", td=0.3, tex=GFX)
    add(661.70, kb("u_TdOHDpcyzZU.jpg", "in", "dark"), [rich("A LEWIS SE LO BUSCÓ AL MENOS DOS SEMANAS", ("dos", "semanas"), 0.3, step=0.1, y=0.84, size=54, maxw=0.85)], tex=DARK)
    bg, ov = card([("DE SMITH NI SIQUIERA QUEDÓ SU NOMBRE DE PILA", 50, (190, 190, 190), 0.3, 0.1), ("H.", 300, YELLOW, 0.55, 1.4),
                   ("SOLO UNA LETRA", 64, WHITE, 0.78, 2.8)])
    add(665.20, bg, ov, tr="black", td=0.2, tex=DARK)
    add(669.00, kb("u_9_8K9PMGa8Q.jpg", "out", "bw"), [rich("PROBABLEMENTE ERAN NEGROS", ("negros",), 0.3, y=0.86, size=60)], tex=ARCH)
    add(672.40, kb("u_5d8S0VTGvDo.jpg", "in", "sepia"), [Badge("VIRGINIA · 1925", 0.2, None),
                                                       rich("UN MAQUINISTA BLANCO: NOMBRE, EDAD Y DETALLES", ("blanco",), w("maquinista", 676.7) - 672.4, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=ARCH)
    add(680.90, kb("u_Q77Ocr7p8cM.jpg", "in", "sepia"), [rich("UN JORNALERO NEGRO: A VECES NI SALÍA", ("ni", "salía"), 0.2, y=0.84, size=58)], tex=ARCH)
    add(684.30, kb("u_rvVhr2LngP4.jpg", "in", "doc"), [rich("NO QUEDÓ MÁS QUE UNA LÍNEA EN UN PAPEL", ("línea",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(687.50, cus(G8.company_list, mode="count", c1=w("faltaban", 691.6) - 687.5, c2=w("entre", 696.7) - 687.5), tr="fade", td=0.3, tex=GFX)
    add(696.70, fr("l_11733.jpg", "Trabajadores afroamericanos en las vías · Library of Congress"), [big("ENTRE 10 Y 15, SEGÚN LOS OBREROS", 0.1, 0.065, 62, YELLOW)], tex=ARCH)
    add(698.70, kb("u_jpkvklXwt98.jpg", "in", "doc"), [rich("TRABAJADORES NUEVOS QUE NO ESTABAN EN NINGUNA LISTA", ("ninguna",), w("trabajadores", 700.6) - 698.7, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(704.80, kb("u_PHQkRcLYXBs.jpg", "in", "sepia"), [big("OTRAS CRÓNICAS: 6 DESAPARECIDOS", 0.2, 0.5, 80, YELLOW)], tex=ARCH)
    add(707.10, kb("u_Dz_WKOrSnwE.jpg", "in", "dark"), [Stamp("CIFRA OFICIAL: 2", 0.4, YELLOW, (0.5, 0.42), -8, 110),
                                                      big("AUNQUE PUDIERON SER MÁS", w("aunque", 709.2) - 707.1, 0.7, 66, WHITE)], tex=DARK)
    add(711.00, cus(G8.names_wall, t0=0.2, step=0.45), [big("HOY SE HABLA DE AL MENOS CUATRO MUERTOS", 0.1, 0.07, 54, (190, 190, 190))], tr="fade", td=0.3, tex=DARK)

    # ============================== CAP 6: EL VEREDICTO Y LA ARENA (717.6 - 842.2)
    bg, ov = chapter(6, "El veredicto y la arena", "u_xf5Qn2-GaJQ.jpg", year="1925 – 1926")
    add(717.60, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(722.00, kb("u_jhjixIHT5cg.jpg", "in", "doc"), [Badge("UN INSPECTOR DE LA CIUDAD", 0.2, None), rich("LA TIERRA HÚMEDA SACADA DE LAS PAREDES", ("húmeda",), 0.8, y=0.84, size=54)],
        tex=CLEAN)
    add(726.60, kb("u_CfSE-yO-0bQ.jpg", "in", "doc"), [rich("Y LA VIBRACIÓN DE LA LOCOMOTORA", ("vibración",), 0.1, y=0.84, size=58)], tex=CLEAN)
    add(728.50, fr("l_09198.jpg"), [Badge("OTRO INFORME", 0.2, None), rich("REFUERZOS MAL COLOCADOS", ("mal",), 1.4, y=0.065, size=54, maxw=0.95)], tex=ARCH)
    add(733.00, kb("u_HpmDAS1Dozs.jpg", "in", "doc"), [rich("EL JURADO QUE INVESTIGÓ LA MUERTE DE MASON", ("jurado",), 0.2, step=0.1, y=0.84, size=54, maxw=0.85)], tex=CLEAN)
    add(737.10, cus(G8.verdict), tr="fade", td=0.3, tex=GFX)
    add(742.60, cus(G8.warnings2, t1=w("1873", 745.7) - 742.6, t2=w("1925", 749.2) - 742.6, t3=w("siguió", 755.4) - 742.6 - 0.4), tr="fade", td=0.3, tex=GFX)
    add(756.30, kb("u_rLlZ_8LUKtY.jpg", "in", "doc"), [rich("UN JURADO FORENSE: VECINOS QUE ESCUCHABAN A LOS TESTIGOS", ("vecinos",), 0.3, step=0.1, y=0.84, size=50, maxw=0.88)],
        tex=CLEAN)
    add(764.40, kb("u__JEiyOfC2y8.jpg", "up", "doc"), [big("NO PODÍA METER A NADIE EN LA CÁRCEL", 0.1, 0.84, 64, WHITE)], tex=CLEAN)
    add(767.00, warp(G8.verdict, 2.8, 1.0), [big("PERO DEJABA ESCRITO: NO FUE UN ACCIDENTE SIN MÁS", w("accidente", 771.3) - 767.0 - 1.2, 0.08, 50, YELLOW)],
        tr="fade", td=0.3, tex=GFX)
    add(772.50, kb("u_Bh6u25Qv9qA.jpg", "in", "dark"), [big("¿Y QUÉ HIZO LA EMPRESA?", 0.4, 0.5, 96, YELLOW)], tex=DARK)
    add(776.10, kb("f_6991547591.jpg", "in", "doc"), [Darken(0.6), rich("NO VOLVIÓ A ENTRAR · NO SIGUIÓ BUSCANDO", ("no",), 0.2, step=0.15, y=0.14, size=54, maxw=0.9),
                                                    big("HIZO LO CONTRARIO", w("hizo", 779.1) - 776.1, 0.84, 84, RED, "pop")], tex=CLEAN)
    add(781.10, cus(G3.document, lines=[("PRIMAVERA DE 1926", 64), ("COMISIÓN DEL ESTADO", 40), ("QUE VIGILA LOS FERROCARRILES", 40), ("", 10),
                                        ("SE ORDENA SELLAR", 46), ("EL TÚNEL DE CHURCH HILL.", 46)], sign_t=w("ordenó", 786.7) - 781.1), tr="whip_l", td=0.25, tex=GFX)
    bg, ov = card([("PARA ENTONCES, EL ÚNICO CUERPO RECUPERADO", 52, (190, 190, 190), 0.38, 0.1), ("THOMAS MASON", 140, WHITE, 0.53, 0.8)])
    add(788.30, bg, ov, tr="black", td=0.2, tex=DARK)
    add(793.10, cus(G8.hill, mode="seal", t0=w("tapones", 796.2) - 793.1 - 2.8), tr="fade", td=0.3, tex=GFX)
    add(803.20, kb("u_HkxPrTZGEl8.jpg", "in", "doc"), [rich("COMO LLENAR DE TIERRA UNA TUMBA QUE NADIE VA A VOLVER A ABRIR", ("tumba",), w("como", 806.3) - 803.2, step=0.09,
                                                             y=0.84, size=50, maxw=0.88)], tex=CLEAN)
    add(809.80, kb("u_nv_CLuGKJ-Q.jpg", "in", "none"), [torch(((0.45, 0.5), (0.55, 0.5)), r=420, amb=0.15),
                                                       rich("SACAR EL TREN HABRÍA COSTADO MÁS VIDAS", ("vidas",), 0.4, step=0.1, y=0.84, size=56)], tex=DARK)
    add(815.20, kb("u_ESqdY3R98-Y.jpg", "in", "dark"), [Darken(0.55), big("LA COLINA NO ESTABA PARA MÁS POZOS", 0.1, 0.84, 64)], tex=DARK)
    add(817.50, V("18305", "u_sUHD8WFjkB0.jpg", 3.0, "dark"), [big("LO MÁS BARATO", 0.2, 0.42, 110, YELLOW, "pop"), big("Y LO MÁS RÁPIDO", 1.4, 0.6, 76, WHITE)], tex=DARK)
    add(820.40, kb("u_vdMPZzH2h3I.jpg", "in", "warm"), [rich("NADA QUE BUSCAR · NADA QUE REVISAR · NADA QUE PREGUNTAR", ("nada",), 0.4, step=0.35, y=0.84, size=52, maxw=0.9)],
        tex=CLEAN)
    bg, ov = card([("SI HUBIERAS SIDO DE LA FAMILIA DE", 52, (190, 190, 190), 0.38, 0.1), ("RICHARD LEWIS", 140, WHITE, 0.53, 0.6)])
    add(827.00, bg, ov, tr="black", td=0.2, tex=DARK)
    add(832.60, kb("u_du8xCg9IznM.jpg", "in", "cold"), [rich("NUNCA IBAS A TENER UNA TUMBA DONDE LLEVARLE FLORES", ("flores",), 0.2, step=0.1, y=0.84, size=50, maxw=0.88)],
        tex=CLEAN)
    add(835.90, kb("f_52139781848.jpg", "out", "doc"), [Darken(0.6), big("SU TUMBA: UNA COLINA", 0.2, 0.42, 96, WHITE), big("CON UN PARQUE ENCIMA", 1.0, 0.58, 76, YELLOW)],
        tex=CLEAN)
    add(839.00, kb("f_6845420510.jpg", "in", "doc"), [rich("CON UN TAPÓN DE CONCRETO, EL PROBLEMA DEJÓ DE ESTAR A LA VISTA", ("vista",), 0.2, step=0.08, y=0.86, size=48, maxw=0.9)],
        tex=CLEAN)

    # ============================== CAP 7: HOY (842.2 - 1005.6)
    bg, ov = chapter(7, "Hoy", "f_6991547391.jpg", year="1998 – 2026")
    add(842.20, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(846.50, mp("rc_loc", [(0, -77.4195, 37.5315, 0.78), (4.7, -77.4195, 37.5315, 0.84)],
                   [dict(type="route", path=TUNNEL, t0=0.1, draw=1.0, color=(150, 150, 150), width=8, smooth=False, dash=16),
                    dict(type="pin", at="west_portal", t0=w("dos", 850.0) - 846.5, label="BOCA OESTE", side="l", box=True, size=44),
                    dict(type="pin", at="east_portal", t0=w("bocas", 850.2) - 846.5, label="BOCA ESTE", side="r", box=True, size=44),
                    dict(type="label", at="jefferson_park", text="JEFFERSON PARK", t0=0.6, size=40, color=GREEN)]), tr="zoom", td=0.3, tex=GFX)
    add(851.20, kb("f_6991547803.jpg", "in", "doc"), [rich("DETRÁS DE UNA REJA, EN UN TERRENO PRIVADO", ("reja",), 0.2, step=0.1, y=0.12, size=50, maxw=0.9),
                                                    Caption("Boca oeste · foto: Eli Christman (CC BY 2.0)", None, 1.4)], tex=CLEAN)
    add(856.00, kb("f_6845420808.jpg", "in", "doc"), [big("CONCRETO MANCHADO DE HUMEDAD", 0.2, 0.86, 64, YELLOW)], tex=CLEAN)
    add(858.40, kb("f_6991547391.jpg", "l", "doc"), [Badge("DESDE 2012", 0.2, None),
                                                   rich("UNA PLACA HISTÓRICA DEL ESTADO DE VIRGINIA", ("placa",), 0.8, step=0.1, y=0.86, size=54, maxw=0.85)], tex=CLEAN)
    add(865.00, cus(G8.hill, mode="today", t0=0.2), tr="fade", td=0.3, tex=GFX)
    add(870.30, kb("u_nv_CLuGKJ-Q.jpg", "in", "dark"), [Darken(0.5), Badge("EL OTRO MISTERIO", 0.2, None)] +
        question("¿Por qué, en cien años, nadie ha conseguido sacar la locomotora?", ("nadie",), size=70), tr="glitch", td=0.3, tex=DARK)
    add(878.10, kb("u_9O770ZdQQjs.jpg", "in", "dark"), [Badge("1998", 0.2, None),
                                                      rich("UN PERIODISTA SE METIÓ POR LA BOCA ESTE", ("periodista",), 0.8, step=0.1, y=0.84, size=54, maxw=0.85)], tex=DARK)
    add(884.80, kb("u_nuqhqqpCeAQ.jpg", "in", "dark"), [rich("AGUA · BARRO · OSCURIDAD", ("agua", "barro", "oscuridad"), 0.2, step=0.5, y=0.5, size=80)], tex=DARK)
    bg, ov = card([("RUMORES", 60, (190, 190, 190), 0.25, 0.1), ("¿ORO?", 150, YELLOW, 0.42, w("oro", 890.9) - 888.3),
                   ("¿25 CUERPOS?", 130, YELLOW, 0.6, w("25", 891.8) - 888.3)])
    ov.append(Stamp("NADA PROBADO", w("nada", 893.2) - 888.3, RED, (0.5, 0.8), -6, 90))
    add(888.30, bg, ov, tr="black", td=0.2, tex=DARK)
    add(894.80, kb("u_-fXpv0MTHRo.jpg", "in", "doc"), [Badge("2006", 0.2, None),
                                                     rich("UNA SOCIEDAD HISTÓRICA Y UNA EMPRESA DE TRENES: «VAMOS A SACARLA»", ("sacarla»",), 0.8, step=0.1, y=0.84, size=48, maxw=0.88)],
        tex=CLEAN)
    add(901.70, kb("u_rzCi3mD-6ho.jpg", "in", "dark"), [rich("UNA CÁMARA POR UN AGUJERO HASTA EL TÚNEL", ("cámara",), 0.2, step=0.1, y=0.84, size=54)], tex=DARK)
    add(905.80, kb("u_74VbII_Eexo.jpg", "in", "dark"), [rich("LIMO Y AGUA", ("limo", "agua"), 0.2, y=0.4, size=84),
                                                      big("NI RASTRO DE UN TREN", w("rastro", 908.3) - 905.8, 0.6, 76, YELLOW)], tex=DARK)
    add(910.40, kb("u_9O770ZdQQjs.jpg", "out", "dark"), [big("BOMBEAR MILLONES DE GALONES", 0.3, 0.84, 72, YELLOW)], tex=DARK)
    add(913.80, kb("u_S9yS7UTB1h0.jpg", "in", "dark"), [Darken(0.55), rich("SIN ESA AGUA, LA COLINA PODÍA VOLVER A CEDER", ("ceder",), 0.2, step=0.1, y=0.84, size=54, maxw=0.85)], tex=DARK)
    add(918.20, kb("u_rvVhr2LngP4.jpg", "in", "doc"), [Stamp("SIN PERMISOS", w("permisos", 921.2) - 918.2 - 0.4, RED, (0.5, 0.5), -10, 120)], tex=CLEAN)
    add(922.20, kb("f_6991547591.jpg", "out", "doc"), [big("EL PROYECTO SE PARÓ", 0.1, 0.42, 96, WHITE), big("NADIE LO HA VUELTO A INTENTAR", 1.4, 0.6, 66, YELLOW)], tex=CLEAN)
    add(925.70, kb("u_IzLWSbMoCPo.jpg", "in", "doc"), [rich("QUIZÁ NO HABRÍA MUCHO QUE SACAR", ("mucho",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(929.10, kb("u_4oW8p6no-Zc.jpg", "in", "dark"), [rich("LOS VAGONES DE MADERA: NADA", ("nada",), w("vagones", 931.5) - 929.1, y=0.4, size=66),
                                                      rich("LA LOCOMOTORA: DÉCADAS BAJO EL AGUA", ("agua",), w("locomotora", 934.5) - 929.1, y=0.58, size=60)], tex=DARK)
    add(937.80, kb("u_HA0RgI-ISko.jpg", "in", "sepia"), [Badge("UN PROFESOR DE RICHMOND", 0.2, None),
                                                       rich("«SI SACAN EL TREN, LA HISTORIA PERDERÍA SU MISTERIO»", ("misterio»",), w("dijo", 942.4) - 937.8, step=0.1, y=0.84, size=52, maxw=0.88)],
        tex=ARCH)
    add(946.70, kb("u_gYC68k9trV8.jpg", "in", "cold"), [rich("AHÍ ABAJO HAY DOS HOMBRES", ("dos", "hombres"), w("ahí", 949.1) - 946.7, y=0.4, size=68),
                                                      rich("A LOS MUERTOS NO SE LES MOLESTA POR UN TREN", ("muertos",), w("los", 951.2) - 946.7, step=0.1, y=0.6, size=54, maxw=0.85)], tex=DARK)
    add(953.70, kb("u_YeZHDQJDEX8.jpg", "in", "bw"), [Darken(0.55), big("LA COLINA SIGUE CEDIENDO", 0.2, 0.84, 76, YELLOW)], tex=ARCH)
    bg, ov = card([("SEGÚN UNA HISTORIA DEL TÚNEL", 46, (190, 190, 190), 0.25, 0.2), ("1962", 200, YELLOW, 0.45, w("1962", 961.6) - 957.2),
                   ("SE HUNDIÓ UNA CASA SOBRE EL TRAZADO", 60, WHITE, 0.66, w("hundió", 963.6) - 957.2),
                   ("MURIÓ UN OBRERO", 64, RED, 0.78, w("murió", 965.8) - 957.2)])
    add(957.20, bg, ov, tr="black", td=0.2, tex=DARK)
    add(966.90, kb("u_TgtKBX2-_do.jpg", "in", "dark"), [big("LA MADERA SE PUDRE", 0.1, 0.84, 76)], tex=DARK)
    add(968.70, kb("u_nuqhqqpCeAQ.jpg", "out", "dark"), [big("EL AGUA LO LLENA CASI TODO", 0.1, 0.84, 70)], tex=DARK)
    add(970.40, kb("f_14862529594.jpg", "in", "doc"), [rich("EL SUELO DEL BARRIO SE ASIENTA DE VEZ EN CUANDO", ("asienta",), 0.2, step=0.1, y=0.86, size=52, maxw=0.85)], tex=CLEAN)
    add(973.40, kb("f_52139781848.jpg", "in", "warm"), [Badge("2 DE OCTUBRE DE 2025", 0.2, None), rich("JUSTO CIEN AÑOS DESPUÉS", ("cien",), 1.0, y=0.84, size=60)],
        tr="fade", td=0.4, tex=CLEAN)
    add(980.50, V("3461", "u_fvl4b1gjpbk.jpg", 0.5, "warm"), [Darken(0.7), rich("VELAS Y MÚSICA EN JEFFERSON PARK", ("velas",), 0.3, y=0.84, size=58)], tex=DARK)
    add(983.20, V("18288", "u_qFH7-yKoxik.jpg", 0.5, "doc"), [rich("EL ALCALDE FIRMÓ UNA DECLARACIÓN OFICIAL", ("declaración",), 0.2, y=0.84, size=54)], tex=CLEAN)
    add(986.10, cus(G3.document, lines=[("DECLARACIÓN", 70), ("CIUDAD DE RICHMOND · 2025", 40), ("", 12), ("…EL TREN ENTERRADO", 44),
                                        ("Y UN NÚMERO DESCONOCIDO", 44), ("DE OBREROS…", 44)], sign_t=99), tr="whip_l", td=0.25, tex=GFX)
    add(991.20, V("41744", "u_UrAKbpKnak8.jpg", 0.5, "warm"), [Darken(0.55), big("CIEN AÑOS DESPUÉS", 0.2, 0.42, 90, WHITE), big("NADIE SABE CUÁNTOS SON", 1.2, 0.58, 76, YELLOW)], tex=DARK)
    add(994.60, V("21612", "u_5FOfresB1G4.jpg", 0.5, "warm"), [rich("UN DOCUMENTAL SOBRE LA HISTORIA ESCONDIDA DE VIRGINIA", ("escondida",), 0.2, step=0.1, y=0.84, size=50, maxw=0.88)],
        tex=DARK)
    add(999.40, kb("u_5FOfresB1G4.jpg", "in", "warm"), [Darken(0.55), rich("«ES TARDE PARA DESHACER EL DAÑO…", ("tarde",), 0.2, step=0.1, y=0.38, size=60, maxw=0.85),
                                                      rich("…PERO NO PARA CONOCER LA HISTORIA Y RECORDAR A LOS QUE MURIERON»", ("recordar",), w("pero", 1001.5) - 999.4, step=0.08,
                                                           y=0.58, size=50, maxw=0.88)], tex=DARK)

    # ============================== CONCLUSIÓN (1005.6 - end)
    q1(1005.60, badge="DE VUELTA A LA PREGUNTA 1")
    add(1012.20, kb("u_ESqdY3R98-Y.jpg", "punch", "dark"), [Darken(0.55), big("LA COLINA YA NO DEJABA ENTRAR", 0.1, 0.5, 90, YELLOW, "pop")], tr="flash", td=0.2, tex=DARK)
    add(1014.70, cus(G8.warnings2, t1=0.2, t2=0.9, t3=3.0), [big("MEDIO SIGLO AVISANDO", 0.1, 0.07, 56, (190, 190, 190))], tr="fade", td=0.3, tex=GFX)
    add(1019.90, cus(G8.hill, mode="rescue", t0=-2.5), tr="fade", td=0.3, tex=GFX)
    add(1025.80, cus(G8.company_list, mode="list", row_t=-3.0, hl_t=-1.0), [big("SEGUIR CAVANDO PODÍA AÑADIR NOMBRES A LA LISTA", 0.2, 0.08, 50, YELLOW)],
        tr="fade", td=0.3, tex=GFX)
    add(1029.40, kb("u_nv_CLuGKJ-Q.jpg", "out", "dark"), [big("EN ESO, LA DECISIÓN TENÍA SENTIDO", 0.1, 0.5, 80, WHITE)], tex=DARK)
    add(1031.60, Solid("black"), [big("PERO NO ES TODA LA RESPUESTA", 0.1, 0.5, 100, YELLOW, "pop")], tr="black", td=0.1, tex=DARK)
    add(1034.40, cus(G8.why_sealed, times=[0.0, w("barato", 1036.2) - 1034.4, w("jurado", 1038.3) - 1034.4, w("faltaban", 1041.9) - 1034.4]),
        tr="fade", td=0.3, tex=GFX)
    add(1046.10, kb("f_6845420510.jpg", "punch", "doc"), [rich("SE DECIDIÓ EN 1926 Y NADIE LO HA CAMBIADO", ("1926",), 0.2, step=0.1, y=0.86, size=54, maxw=0.85)], tex=CLEAN)
    add(1051.50, cus(G8.coffin, n_t=0.4, a_t=None, b_t=w("locomotora", 1054.4) - 1051.5, bottom="LA LOCOMOTORA TIENE NÚMERO… Y LO LLEVÓ UN ATAÚD"),
        tr="fade", td=0.3, tex=DARK)
    add(1058.20, kb("f_6991547391.jpg", "in", "doc"), [big("EL TÚNEL TIENE UNA PLACA DEL ESTADO", 0.1, 0.86, 64)], tex=CLEAN)
    add(1060.30, kb("u_zFDoHnPATY8.jpg", "in", "warm"), [big("LA CIUDAD, UN PARQUE CON BUENAS VISTAS", 0.1, 0.86, 62)], tex=CLEAN)
    add(1062.70, V("3458", "u_wkn_KHBExcE.jpg", 0.5, "warm"), [big("Y UNA CEREMONIA CADA CIEN AÑOS", 0.1, 0.86, 64)], tex=DARK)
    bg, ov = card([("Y UNO DE LOS HOMBRES QUE SIGUEN AHÍ ABAJO TIENE", 46, (190, 190, 190), 0.25, 0.2), ("H.", 300, YELLOW, 0.52, 1.6),
                   ("UNA SOLA LETRA EN LUGAR DE NOMBRE", 60, WHITE, 0.8, w("letra", 1068.8) - 1064.9)])
    add(1064.90, bg, ov, tr="black", td=0.2, tex=DARK)
    add(1071.00, kb("l_4a12835.jpg", "in", "archival"), [Darken(0.55), big("ARRIBA: LA IGLESIA DE «LIBERTAD O MUERTE»", 0.2, 0.86, 60, YELLOW)], tr="fade", td=0.3, tex=ARCH)
    add(1075.00, kb("u_nv_CLuGKJ-Q.jpg", "in", "none"), [torch(((0.45, 0.5), (0.55, 0.5)), r=420, amb=0.12),
                                                        big("DEBAJO: HOMBRES QUE NADIE SE MOLESTÓ EN CONTAR", 0.1, 0.86, 58, WHITE)], tex=DARK)
    add(1078.30, cus(G8.names_wall, t0=0.0, step=0.65), tr="fade", td=0.3, tex=DARK)
    add(1086.00, kb("f_52139781848.jpg", "out", "warm"), [Darken(0.55), big("PARA LA COLINA, TODOS PESAN LO MISMO", 0.2, 0.42, 72, WHITE),
                                                        big("PARA LA HISTORIA, NO", w("historia", 1089.5) - 1086.0, 0.6, 96, YELLOW, "pop")], tex=CLEAN)
    add(1090.50, kb("f_6991547803.jpg", "in", "doc"), [rich("NO SOLO POR EL AGUA O POR LOS PERMISOS", ("agua", "permisos"), w("no", 1093.9) - 1090.5, step=0.1, y=0.86, size=54, maxw=0.85),
                                                     big("EL TÚNEL SIGUE CERRADO", 0.2, 0.12, 70, YELLOW)], tex=CLEAN)
    add(1096.40, V("41744", "u_UrAKbpKnak8.jpg", 4.0, "warm"), [Darken(0.55), rich("CONTAR, POR FIN, A TODOS LOS QUE HAY DENTRO", ("todos",), w("contar", 1101.0) - 1096.4, step=0.12,
                                                                   y=0.5, size=66, maxw=0.85)], tex=DARK)
    add(1105.00, kb("u_9_8K9PMGa8Q.jpg", "out", "bw"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿ALGUIEN DE TU FAMILIA TRABAJÓ EN EL TREN, UNA MINA",
                                 line2="O UNA OBRA, Y CASI NO QUEDÓ NADA ESCRITO DE ÉL?", cta="CUÉNTANOS SU NOMBRE EN LOS COMENTARIOS"),
         rich("A veces, un nombre es lo único que se puede rescatar", ("nombre",), w("veces", 1116.3) - 1105.0 - 0.4, step=0.08, y=0.2, size=48, maxw=0.85)],
        tex=DARK)
    return S
