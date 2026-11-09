"""The edit: every shot of the Road to Nowhere video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx3 as G3
import gfx4 as G4
import gfx5 as G5
import gfx7 as G7
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1112.45
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


# ------------------------------------------------------------------ map paths (lon, lat)
NC288_OLD = ["bryson", (-83.470, 35.433), (-83.500, 35.435), (-83.530, 35.437), (-83.560, 35.443), (-83.600, 35.447),
         (-83.640, 35.452), (-83.680, 35.457), (-83.700, 35.461), "proctor"]
PLAN = ["tunnel", (-83.565, 35.468), (-83.600, 35.472), (-83.635, 35.468), (-83.670, 35.470), (-83.700, 35.472),
        (-83.730, 35.470), (-83.760, 35.466), (-83.785, 35.462), "lv_west", "fontana_dam"]
TRAIL = ["tunnel", (-83.565, 35.465), (-83.600, 35.469), (-83.635, 35.465), (-83.670, 35.467), (-83.700, 35.469),
         "proctor", (-83.730, 35.467), (-83.760, 35.463), (-83.785, 35.459), "fontana_dam"]
SHORE = [(-83.545, 35.457), (-83.560, 35.470), (-83.600, 35.479), (-83.650, 35.476), (-83.700, 35.481), (-83.750, 35.477),
         (-83.795, 35.468), (-83.800, 35.457), (-83.760, 35.460), (-83.720, 35.463), (-83.680, 35.459), (-83.640, 35.456),
         (-83.600, 35.459), (-83.565, 35.455)]
STATE_RD = ["bryson", (-83.455, 35.437), (-83.465, 35.444), "lv_start"]


CEM_PTS = [(-83.565, 35.4705), (-83.590, 35.4775), (-83.615, 35.4765), (-83.640, 35.4760), (-83.665, 35.4790), (-83.690, 35.4800),
           (-83.730, 35.4790), (-83.750, 35.4770), (-83.770, 35.4740), (-83.790, 35.4690)]


def CEMS(t0, step=0.08):
    return [dict(type="pin", at=p, t0=t0 + i * step, color=WHITE, r=7, pulse=False) for i, p in enumerate(CEM_PTS)]


def LV(t0, draw=2.0, color=YELLOW, width=7):
    return dict(type="route", ll=M.rn_lakeview(), t0=t0, draw=draw, color=color, width=width)


def LAKE(t0, fadein=2.5, alpha=1.0):
    return dict(type="polys", polys=M.rn_lake_lonlat(), t0=t0, fadein=fadein, fill=(14, 22, 32), color=(60, 100, 140),
                width=2, alpha=alpha)


def PARK(t0, alpha=0.35):
    return dict(type="polys", polys=M.rn_park_lonlat(), t0=t0, fadein=1.0, fill=(60, 130, 70), color=(110, 200, 120),
                width=3, alpha=alpha)


# ------------------------------------------------------------------ the edit
def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="f_50894285987.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Por qué Estados Unidos pagó 52 millones de dólares por no acabar una carretera que ya tenía su túnel?",
                     ("52", "millones"), size=64), tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_fhFUNQk3h6M.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Y cómo llegan hoy las familias a esas tumbas?", ("tumbas?", "tumbas"), size=76), tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 71.2)
    add(0.0, V("28342", "u_yj4Jjl2sCL0.jpg", 2.0, "cold"), [Badge("CAROLINA DEL NORTE", 0.6, None)], tex=CLEAN)
    add(2.20, V("100233", "u_38gjpr9UxiA.jpg", 1.0, "doc"), [rich("UNA CARRETERA DE MONTAÑA", ("montaña",), 0.2, y=0.84, size=58)],
        tr="fade", td=0.4, tex=CLEAN)
    add(4.00, fr("f_36562380744.jpg", "Foto: Robert Lz (CC BY 2.0)", g="doc", box=(0.74, 0.70)),
        [rich("«BIENVENIDO A LA CARRETERA A NINGUNA PARTE»", ("ninguna", "parte»"), 1.4, step=0.1, y=0.065, size=50, maxw=0.9)],
        tr="whip_l", td=0.25, tex=CLEAN)
    add(8.00, kb("f_36562380744.jpg", "punch", "doc", cam0=(0.42, 0.42, 1.12), cam1=(0.42, 0.40, 1.3)), tex=CLEAN)
    add(10.10, cus(G7.year_q, q_t=7.2), [rich("EL AÑO EN QUE EMPEZÓ TODO", ("empezó",), 1.6, y=0.18, size=52)], tr="flash", td=0.2, tex=DARK)
    add(18.40, mp("rn_lake", [(0, -83.505, 35.452, 1.25), (3.2, -83.515, 35.454, 1.55)],
                  [dict(type="pin", at="lv_start", t0=0.1, label="EL CARTEL", side="r", size=40),
                   LV(0.4, 1.9),
                   dict(type="label", at=(-83.505, 35.4645), text="6 MILLAS · ≈ 10 KM", t0=1.2, size=48, color=YELLOW),
                   dict(type="pin", at="tunnel", t0=2.3, label="EL TÚNEL", side="l", box=True, size=44)]),
        tr="zoom", td=0.3, tex=GFX)
    add(21.60, kb("f_50894279002.jpg", "in", "doc"), [big("UN TÚNEL TERMINADO", 0.1, 0.12, 64, WHITE),
                                                     Counter(0, 1200, "{:,.0f} PIES", "≈ 365 METROS", 1.6, 1.4, (0.5, 0.62), 150)],
        tr="whip_l", td=0.25, tex=CLEAN)
    add(26.90, kb("f_50894285987.jpg", "in", "none"), [torch(((0.45, 0.55), (0.55, 0.5)), r=420, amb=0.08),
                                                      big("SIN UNA SOLA LUZ", 0.3, 0.86, 72, YELLOW)], tex=DARK)
    add(28.40, kb("f_50894285567.jpg", "punch", "doc"), [rich("AL SALIR, EL ASFALTO SE ACABA…", ("acaba…",), 0.2, y=0.86, size=56)],
        tex=CLEAN)
    add(31.10, V("51581", "u_D2NvTDuPME4.jpg", 0.5, "doc"), [big("…Y EMPIEZA EL BOSQUE", 0.1, 0.84, 72, WHITE)], tr="fade", td=0.3, tex=CLEAN)
    add(32.40, kb("f_5910363969.jpg", "in", "doc"), [rich("DEBAJO DEL LAGO…", ("lago…",), 0.3, y=0.84, size=62)], tr="fade", td=0.4, tex=CLEAN)
    add(35.00, cus(G7.valley, mode="under", show_labels=False),
        [rich("PUEBLOS ENTEROS · Y OTRA CARRETERA, LA VIEJA", ("pueblos", "enteros", "vieja"), 0.2, step=0.13, y=0.12, size=54, maxw=0.9)],
        tr="fade", td=0.3, tex=GFX)
    add(38.90, mp("rn_lake", [(0, -83.62, 35.462, 0.72), (5.0, -83.66, 35.466, 0.82)],
                  [LAKE(0.0, 0.1),
                   dict(type="pin", at="tunnel", t0=0.1, label="TÚNEL", side="r", size=40),
                   *CEMS(1.0),
                   dict(type="label", at=(-83.67, 35.493), text="28 CEMENTERIOS FAMILIARES", t0=w("cementerios", 43.0) - 38.9, size=56, box=True),
                   dict(type="label", at=(-83.67, 35.443), text="LAGO FONTANA", t0=0.4, size=44, color=BLUE)]),
        tr="zoom", td=0.3, tex=GFX)
    add(44.40, kb("u_fhFUNQk3h6M.jpg", "in", "doc"), [big("HOY, SOLO EN LANCHA…", 0.1, 0.84, 70, WHITE)], tr="whip_l", td=0.25, tex=CLEAN)
    add(46.40, kb("u_nKWp8eqtnn4.jpg", "in", "doc"), [big("…O TRAS HORAS DE CAMINATA", 0.1, 0.84, 66, WHITE)], tex=CLEAN)
    add(47.90, mp("rn_lake", [(0, -83.64, 35.455, 0.66), (6.0, -83.66, 35.455, 0.70)],
                  [LAKE(0.0, 0.1), LV(0.0, 0.1),
                   dict(type="pin", at="bryson", t0=0.2, label="BRYSON CITY", side="t", size=40),
                   dict(type="route", path=PLAN, t0=0.6, draw=2.6, color=WHITE, width=5, dash=16),
                   dict(type="pin", at="fontana_dam", t0=2.8, label="PRESA", side="l", size=40),
                   dict(type="label", at=(-83.66, 35.492), text="≈ 30 MILLAS · CASI 50 KM", t0=2.2, size=54, color=YELLOW),
                   dict(type="label", at=(-83.50, 35.476), text="SE QUEDÓ EN 6", t0=w("seis", 54.9) - 47.9, size=60, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(55.20, V("44269", "u_VazdXrGvLnQ.jpg", 1.0, "cold"),
        [rich("HAY PROMESAS QUE SE ROMPEN… Y PROMESAS QUE SE CUMPLEN", ("rompen…", "cumplen"), 0.2, step=0.11, y=0.84, size=52, maxw=0.85)],
        tr="fade", td=0.4, tex=CLEAN)
    add(58.70, kb("f_36562370534.jpg", "punch", "dark"), [Darken(0.6), Stamp("LE PUSIERON PRECIO", 0.9, YELLOW, (0.5, 0.5), -8, 110)],
        tex=DARK)
    q1(60.80)
    q2(67.90)
    # title sting
    add(71.20, kb("f_37016472650.jpg", "in", "dark"),
        [Darken(0.45, 0.0, 0.3),
         BigText("ROAD TO NOWHERE", "bebas", 180, YELLOW, (0.5, 0.40), 0.1, None, "pop", tracking=10),
         BigText("La carretera a ninguna parte", "serif_it", 70, WHITE, (0.5, 0.58), 0.45, None, "up"),
         Badge("CAPÍTULO 1 · EL VALLE ANTES DEL AGUA", 1.0, None)], tr="flash", td=0.25, tex=DARK)

    # ============================== CAP 1: EL VALLE ANTES DEL AGUA (71.2 - 182.3)
    add(75.80, mp("rn_valley", [(0, -83.60, 35.445, 0.64), (7.0, -83.58, 35.44, 0.78)],
                  [dict(type="label", at=(-83.66, 35.432), text="RÍO LITTLE TENNESSEE", t0=w("little", 80.2) - 75.8, size=46, color=BLUE),
                   dict(type="label", at=(-83.62, 35.40), text="CONDADO DE SWAIN", t0=w("swain", 82.0) - 75.8, size=50),
                   dict(type="pin", at="bryson", t0=1.2, label="BRYSON CITY", side="r", size=38)],
                  "ANTES DEL AGUA"), tr="zoom", td=0.35, tex=GFX)
    add(82.50, kb("l_8c10612.jpg", "in", "archival"), [Caption("Smoky Mountains, Carolina del Norte · 1939", "Library of Congress", 0.3),
                                                     rich("POBRE Y EMPINADA… PERO CON GENTE", ("gente",), 0.4, y=0.1, size=56)], tex=ARCH)
    add(86.50, kb("l_8c10613.jpg", "in", "archival"), [big("GRANJAS", 0.1, 0.84, 84, YELLOW, "pop")], tex=ARCH)
    add(87.40, kb("l_8b34005.jpg", "in", "archival"), [big("ASERRADEROS", 0.1, 0.84, 84, YELLOW, "pop")], tex=ARCH)
    add(88.20, kb("u_w6TUIcuzSwg.jpg", "up", "bw"), [big("IGLESIAS", 0.1, 0.84, 84, YELLOW, "pop")], tex=ARCH)
    add(89.10, kb("u__CyyAj0QboY.jpg", "in", "sepia"), [big("ESCUELAS", 0.1, 0.84, 84, YELLOW, "pop")], tex=ARCH)
    add(90.10, kb("l_8c10603.jpg", "in", "archival"), [rich("PUEBLOS CON NOMBRES QUE HOY CASI NADIE DICE", ("nadie",), 0.2, y=0.84, size=52, maxw=0.8)],
        tr="fade", td=0.3, tex=ARCH)
    add(93.30, Solid("black"), [BigText("JUDSON", "bebas", 150, WHITE, (0.5, 0.3), 0.0, None, "type", tracking=10),
                                BigText("BUSHNELL", "bebas", 150, WHITE, (0.5, 0.5), 0.95, None, "type", tracking=10),
                                BigText("FORNEY", "bebas", 150, WHITE, (0.5, 0.7), 1.95, None, "type", tracking=10)], tex=DARK)
    add(95.80, mp("rn_valley", [(0, -83.66, 35.455, 0.85), (5.6, -83.71, 35.462, 1.35)],
                  [dict(type="route", ll=M.rn_flow(("Hazel Creek",), (-83.723, 35.461))[:150], t0=w("hazel", 99.8) - 95.8 - 0.6,
                        draw=1.4, color=BLUE, width=5),
                   dict(type="label", at=(-83.683, 35.497), text="HAZEL CREEK", t0=w("hazel", 99.8) - 95.8, size=46, color=BLUE),
                   dict(type="pin", at="proctor", t0=w("hazel", 99.8) - 95.8 + 0.6),
                   dict(type="label", at=(-83.735, 35.474), text="PROCTOR", t0=w("proctor", 101.5) - 95.8 - 0.3, size=54, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(102.00, kb("l_8c13758.jpg", "in", "archival"), [Counter(0, 1000, "≈ {:,.0f}", "VECINOS", 0.3, 1.2, (0.5, 0.45), 170),
                                                      Caption("Aserradero en Carolina del Norte · 1940", "Library of Congress", 2.0)], tex=ARCH)
    add(104.20, kb("l_8c10582.jpg", "l", "archival"), [rich("UNA VÍA DE TREN PARA SACAR LA MADERA", ("madera",), 0.2, y=0.84, size=54)],
        tex=ARCH)
    add(106.50, kb("u_jrRe6er0pY0.jpg", "in", "sepia"), [rich("UNA ESCUELA… A LA QUE SE IBA CAMINANDO", ("caminando",), 0.2, y=0.84, size=54)],
        tex=ARCH)
    add(110.00, cus(G7.valley, mode="life", cem_t=7.4), [rich("TU MUNDO CABÍA EN ESE VALLE", ("valle",), 0.3, y=0.1, size=56)],
        tr="fade", td=0.3, tex=GFX)
    add(120.50, mp("rn_valley", [(0, -83.58, 35.445, 0.70), (9.0, -83.60, 35.447, 0.80)],
                   [dict(type="pin", at="bryson", t0=0.1, label="BRYSON CITY", side="r", size=38),
                    dict(type="pin", at="proctor", t0=0.3, label="PROCTOR", side="l", size=38),
                    dict(type="route", ll=M.rn_old_road(), t0=w("nc", 123.5) - 120.5 - 0.3, draw=2.4, color=YELLOW, width=7),
                    dict(type="label", at=(-83.58, 35.465), text="NC 288", t0=w("288", 123.9) - 120.5, size=64, box=True),
                    dict(type="label", at=(-83.58, 35.42), text="1924 – 1930 · POR LA ORILLA NORTE", t0=w("1924", 126.4) - 120.5, size=44),
                    dict(type="label", at=(-83.70, 35.42), text="TRAZADO APROXIMADO", t0=3.0, size=30, color=(170, 170, 170))]),
        tr="zoom", td=0.3, tex=GFX)
    add(131.40, kb("l_8c10828.jpg", "l", "archival"), [rich("CAMIONES DE MADERA · VISITAS DE LOS DOMINGOS", ("madera", "domingos"), 0.3, y=0.84, size=50, maxw=0.85),
                                                     Caption("Carretera en las Smoky Mountains · 1939", None, 2.4)], tex=ARCH)
    add(135.40, kb("l_8c10830.jpg", "in", "archival"), [rich("DE PROCTOR A BRYSON CITY, SIN ATAJO", ("atajo",), 0.2, y=0.1, size=54)], tex=ARCH)
    add(138.30, kb("l_8c10830.jpg", "punch", "archival", cam0=(0.5, 0.55, 1.2), cam1=(0.5, 0.55, 1.45)),
        [big("MODESTA. Y LA ÚNICA.", 0.3, 0.84, 78, YELLOW, "pop")], tex=ARCH)
    add(140.90, kb("l_8a01333.jpg", "in", "archival"), [Badge("1940", 0.2, None), rich("PONTE EN UNA DE ESAS GRANJAS", ("granjas",), 0.6, y=0.84, size=56)],
        tr="fade", td=0.3, tex=ARCH)
    add(144.30, kb("u_UgyLA7XBLyQ.jpg", "in", "doc"), [rich("TUS ABUELOS, A DIEZ MINUTOS DE TU PUERTA", ("abuelos",), 0.3, y=0.84, size=54, maxw=0.8)],
        tex=CLEAN)
    add(147.60, kb("u__CyyAj0QboY.jpg", "l", "sepia"), [rich("TUS HIJOS, EN LA ESCUELA DE PROCTOR", ("proctor",), 0.2, y=0.84, size=54)], tex=ARCH)
    add(149.70, kb("l_8c10618.jpg", "in", "archival"), [big("¿«LAGO»?", 0.5, 0.5, 150, YELLOW, "pop")], tex=ARCH)
    add(153.90, V("4374", "u_cwQQXPpH4pY.jpg", 1.0, "doc"), [rich("UN RÍO ENTRE MONTAÑAS", ("río",), 0.2, y=0.84, size=58)], tr="fade", td=0.3, tex=CLEAN)
    add(156.00, kb("l_8c10611.jpg", "in", "archival"), [rich("UN VALLE QUE SE CULTIVA DESDE HACE GENERACIONES", ("generaciones",), 0.2, y=0.84, size=50, maxw=0.85)],
        tex=ARCH)
    add(158.70, mp("rn_lake", [(0, -83.60, 35.50, 0.60), (8.0, -83.58, 35.51, 0.68)],
                   [PARK(w("parque", 164.8) - 158.7),
                    dict(type="label", at=(-83.55, 35.565), text="PARQUE NACIONAL GREAT SMOKY MOUNTAINS", t0=w("great", 166.8) - 158.7, size=52, box=True),
                    dict(type="label", at=(-83.55, 35.545), text="AÑOS 30", t0=w("30", 163.1) - 158.7, size=46, color=YELLOW),
                    dict(type="pin", at="bryson", t0=0.3, label="BRYSON CITY", side="r", size=38)], "AL NORTE"),
        tr="zoom", td=0.3, tex=GFX)
    add(168.40, kb("l_3c03257.jpg", "in", "archival"), [rich("MUCHOS YA HABÍAN TENIDO QUE VENDER", ("vender",), 0.3, y=0.84, size=56),
                                                      Caption("Cabaña al pie de las Great Smokies · hacia 1900", None, 2.2)], tex=ARCH)
    add(172.10, kb("l_8a01317.jpg", "in", "archival"), [rich("ESTE VALLE YA SABÍA LO QUE ERA PERDER TIERRA", ("perder",), 0.3, y=0.84, size=52, maxw=0.8)],
        tex=ARCH)
    add(175.10, kb("l_8a01335.jpg", "punch", "archival"), [big("ESTA VEZ, CASI TODO", 2.4, 0.84, 82, YELLOW, "pop")], tex=ARCH)
    add(178.80, Solid("black"), [big("UNA GUERRA", 0.6, 0.45, 150, WHITE, "pop"), big("Y LA PRISA QUE TRAJO", 1.9, 0.62, 70, YELLOW)],
        tr="black", td=0.2, tex=DARK)

    # ============================== CAP 2: LA PRESA (182.3 - 323.7)
    bg, ov = chapter(2, "La presa", None, year="1941 – 1944", base=kb("l_3c04778.jpg", "in", "archival"))
    add(182.30, bg, ov + [Badge("7 DE DICIEMBRE DE 1941", 0.3, None)], tr="flash", td=0.25, tex=ARCH)
    add(186.30, kb("l_3a18762.jpg", "punch", "archival"), [big("PEARL HARBOR", 0.2, 0.84, 96, WHITE, "pop"),
                                                         Flash(0.0, 0.25, (255, 255, 255), 0.7)], tex=ARCH, post=postshake(6))
    add(187.80, kb("l_8b05339.jpg", "in", "archival"), [rich("ESTADOS UNIDOS NECESITA AVIONES", ("aviones",), 0.2, y=0.1, size=56),
                                                      big("MUCHOS AVIONES", w("muchos", 191.4) - 187.8, 0.86, 80, YELLOW, "pop")], tex=ARCH)
    add(192.70, kb("l_8b03796.jpg", "in", "archival"), [big("ALUMINIO", w("aluminio", 194.6) - 192.7, 0.84, 110, YELLOW, "pop")], tex=ARCH)
    add(195.30, kb("l_8b02206.jpg", "in", "archival"), [rich("SE FABRICA A BASE DE ELECTRICIDAD", ("electricidad",), 0.2, y=0.84, size=56),
                                                      Caption("Fundición de aluminio · 1942", "Library of Congress", 1.8)], tex=ARCH)
    add(198.10, mp("rn_reg", [(0, -83.95, 35.75, 0.74), (6.0, -84.0, 35.80, 0.86), (12.5, -84.05, 35.85, 0.86)],
                   [dict(type="state", name="Tennessee", t0=0.2, color=(160, 160, 160), width=3, alpha=0.8),
                    dict(type="label", at=(-84.35, 35.55), text="TENNESSEE", t0=w("tennessee", 200.4) - 198.1, size=56),
                    dict(type="label", at=(-83.25, 35.30), text="CAROLINA DEL NORTE", t0=0.4, size=46),
                    dict(type="pin", at="fontana_dam", t0=0.5, label="EL RÍO", side="b", size=36),
                    dict(type="pin", at="alcoa", t0=w("alcoa", 201.9) - 198.1, label="ALCOA", side="r", box=True, size=48),
                    dict(type="route", path=["fontana_dam", (-83.90, 35.62), "alcoa"], t0=w("corriente", 203.1) - 198.1, draw=1.0, color=YELLOW,
                         width=5, dash=14),
                    dict(type="pin", at="oak_ridge", t0=w("oak", 206.5) - 198.1, label="OAK RIDGE", side="r", box=True, size=48),
                    dict(type="label", at=(-84.27, 36.07), text="EN SECRETO", t0=w("secreto", 208.8) - 198.1, size=50, color=RED),
                    dict(type="route", path=["fontana_dam", (-84.05, 35.75), "oak_ridge"], t0=w("necesitar", 210.9) - 198.1, draw=1.0,
                         color=YELLOW, width=5, dash=14)]),
        tr="zoom", td=0.3, tex=GFX)
    add(212.40, V("51585", "u_cwQQXPpH4pY.jpg", 1.0, "doc", m="l"), [big("LA RESPUESTA ESTABA EN EL RÍO", 0.2, 0.84, 70)], tr="fade", td=0.3, tex=CLEAN)
    add(214.70, kb("l_8d04903.jpg", "in", "archival"), [Badge("TVA · AUTORIDAD DEL VALLE DEL TENNESSEE", 0.3, None),
                                                      rich("CERRAR EL RÍO CON UNA PRESA", ("presa",), w("cerrarlo", 218.9) - 214.7, y=0.84, size=58),
                                                      Caption("Obras de la TVA · 1942", "Library of Congress", 1.2)], tex=ARCH)
    add(220.20, kb("f_9258164552.jpg", "in", "doc"), [big("FONTANA", w("fontana", 222.2) - 220.2, 0.5, 190, YELLOW, "pop"),
                                                    Caption("Presa Fontana · foto: Tennessee Valley Authority (CC BY 2.0)", None, 2.0)], tex=CLEAN)
    add(223.00, kb("l_8d05017.jpg", "in", "archival"), [Badge("1 DE ENERO DE 1942", 0.4, None),
                                                      big("TRES SEMANAS DESPUÉS DEL ATAQUE", w("tres", 226.8) - 223.0, 0.84, 64, YELLOW)], tex=ARCH)
    add(228.70, kb("l_8d04904.jpg", "in", "archival"), [Counter(0, 5000, "{:,.0f}", "HOMBRES", 0.6, 1.2, (0.5, 0.45), 190)], tex=ARCH)
    add(231.10, kb("l_8d05014.jpg", "in", "archival"), [big("3 TURNOS", 0.2, 0.84, 96, YELLOW, "pop")], tex=ARCH)
    add(232.50, kb("l_8d04929.jpg", "in", "archival"), [big("7 DÍAS A LA SEMANA", 0.2, 0.84, 84, YELLOW, "pop")], tex=ARCH)
    add(234.00, kb("l_8d05010.jpg", "in", "archival"), [rich("GENTE DE LAS MONTAÑAS DE CAROLINA DEL NORTE", ("montañas",), 0.6, y=0.86, size=48, maxw=0.85),
                                                      Caption("Obreros de la TVA · 1942", "Library of Congress", 0.2, y=0.1)], tex=ARCH)
    add(238.40, cus(G7.dam_height), tr="fade", td=0.3, tex=GFX)
    add(247.20, kb("l_8c10629.jpg", "in", "archival"), [rich("PARA EL VALLE, LA GUERRA NO LLEGÓ CON BOMBAS", ("bombas",), 0.2, y=0.84, size=52, maxw=0.85)],
        tr="fade", td=0.3, tex=ARCH)
    add(250.50, cus(G3.document, lines=[("AVISO", 80), ("", 20), ("LA TVA COMPRA ESTA TIERRA.", 46), ("", 10), ("SE LE OFRECE UN PRECIO", 40),
                                        ("Y UN PLAZO PARA DESALOJAR.", 40)], sign_t=4.0), tr="whip_l", td=0.25, tex=GFX)
    add(256.70, cus(G7.icon_grid, kind="house", n=131, per=10, total=1311, title="FAMILIAS", sub="SALIERON DEL VALLE", t0=0.6, fill=2.0),
        tr="fade", td=0.25, tex=GFX)
    add(260.20, cus(G7.icon_grid, kind="grave", n=105, per=10, total=1047, title="TUMBAS", sub="SE DESENTERRARON Y SE TRASLADARON",
                    t0=w("trasladaron", 263.4) - 260.2 - 1.0, fill=2.0), tr="fade", td=0.25, tex=GFX)
    add(265.50, kb("l_8a01334.jpg", "in", "archival"), [rich("UN CAMIÓN CON LOS MUEBLES…", ("muebles…",), 0.3, y=0.84, size=58)], tex=ARCH)
    add(268.80, kb("u_Kddnmo9pZ50.jpg", "out", "bw"), [big("…Y UNA ÚLTIMA MIRADA A LA CASA", 0.2, 0.84, 66, YELLOW)], tex=ARCH)
    add(270.50, kb("u_v6oeEzbgCoY.jpg", "in", "doc"), [rich("LA PRÓXIMA VEZ, DESDE UNA LANCHA", ("lancha",), 0.3, y=0.84, size=58)],
        tr="fade", td=0.3, tex=CLEAN)
    add(275.60, cus(G7.valley, mode="flood", t_flood=2.6, flood_dur=6.0), tr="flash", td=0.25, tex=GFX)
    add(284.70, mp("rn_valley", [(0, -83.60, 35.445, 0.66), (5.0, -83.62, 35.447, 0.72)],
                   [dict(type="route", ll=M.rn_old_road(), t0=0.0, draw=0.1, color=YELLOW, width=7),
                    dict(type="label", at=(-83.58, 35.465), text="NC 288", t0=0.0, size=56, box=True, t1=2.0),
                    dict(type="label", at=(-83.57, 35.425), text="JUDSON · BUSHNELL", t0=0.0, size=44, t1=1.6),
                    LAKE(0.4, 2.4),
                    dict(type="label", at=(-83.62, 35.475), text="CASI TODA LA NC 288, BAJO EL AGUA", t0=2.4, size=50, color=YELLOW)],
                   "NOVIEMBRE DE 1944"), tr="fade", td=0.3, tex=GFX)
    add(289.50, kb("f_5911006100.jpg", "in", "cold"), [rich("LA GUERRA TENÍA PRISA", ("prisa",), 0.2, y=0.12, size=60),
                                                     big("EL VALLE NO TUVO TIEMPO NI DE DESPEDIRSE", 1.8, 0.86, 58, YELLOW)], tr="fade", td=0.4, tex=CLEAN)
    add(293.80, mp("rn_lake", [(0, -83.70, 35.465, 1.0), (6.0, -83.715, 35.467, 1.25)],
                   [dict(type="pin", at="proctor", t0=0.2, label="PROCTOR", side="l", box=True, size=50),
                    dict(type="label", at=(-83.716, 35.486), text="POR ENCIMA DEL AGUA", t0=1.2, size=46, color=GREEN),
                    dict(type="route", ll=M.rn_old_road()[::-1][:40], t0=w("carretera", 300.3) - 293.8, draw=1.4, color=(150, 150, 150), width=6, dash=14),
                    dict(type="label", at=(-83.66, 35.437), text="LA NC 288, EN EL FONDO", t0=w("fondo", 302.7) - 293.8, size=44),
                    PARK(w("parque", 304.4) - 293.8, 0.28)]),
        tr="zoom", td=0.3, tex=GFX)
    add(305.10, fr("l_577096p.jpg", "Casa Calhoun, cerca de Hazel Creek · HABS, Library of Congress"),
        [rich("SUS VECINOS TAMBIÉN TUVIERON QUE IRSE", ("irse",), 0.2, y=0.065, size=50, maxw=0.85)], tex=ARCH)
    add(307.70, V("2632", "u_lehbaCvP-ow.jpg", 0.5, "dark"), [rich("UN PUEBLO QUE EL AGUA NO TOCÓ…", ("tocó…",), 0.2, y=0.84, size=58),
                                                      big("SE MURIÓ IGUAL", w("murió", 310.0) - 307.7, 0.5, 120, YELLOW, "pop")], tex=DARK)
    add(310.70, fr("l_578023p.jpg", "Cementerio de Proctor · HABS, Library of Congress"),
        [rich("LOS MUERTOS DE LA LADERA NORTE", ("norte",), 0.4, y=0.065, size=54)], tex=ARCH)
    add(315.30, cus(G7.icon_grid, kind="cross", n=28, per=1, total=28, title="CEMENTERIOS FAMILIARES", sub="POR ENCIMA DEL AGUA",
                    t0=0.4, fill=1.4, color=(230, 226, 214)), tr="fade", td=0.25, tex=GFX)
    add(318.10, cus(G7.valley, mode="cut"), tr="fade", td=0.3, tex=GFX)

    # ============================== CAP 3: LA PROMESA (323.7 - 436.9)
    bg, ov = chapter(3, "La promesa", None, year="1943", base=fr("f_40934321803.jpg", g="archival"))
    add(323.70, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(327.20, kb("l_8d05019.jpg", "in", "archival"), [rich("MIENTRAS LA PRESA CRECÍA, SE FIRMÓ UN ACUERDO", ("acuerdo",), 0.2, y=0.84, size=52, maxw=0.85)],
        tex=ARCH)
    add(330.40, cus(G7.agreement, mode="parties", times=[5.0, 6.1, 7.4, 9.1]), tr="fade", td=0.3, tex=GFX)
    add(341.00, kb("l_192145p.jpg", "in", "archival"), [rich("INTERIOR: EL DUEÑO DE LOS PARQUES NACIONALES", ("parques",), 0.4, y=0.84, size=50, maxw=0.85)],
        tex=ARCH)
    add(345.40, cus(G7.agreement, mode="terms", term_t=[2.0, 7.6, 99]), tr="fade", td=0.3, tex=GFX)
    add(358.30, mp("rn_lake", [(0, -83.64, 35.50, 0.62), (4.0, -83.64, 35.50, 0.66)],
                   [PARK(0.1), LAKE(0.0, 0.1),
                    dict(type="label", at=(-83.66, 35.493), text="LA ORILLA NORTE, AL PARQUE", t0=0.6, size=50, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(360.40, kb("l_8a01320.jpg", "in", "archival"), [rich("LA GENTE QUE QUEDABA TENÍA QUE IRSE", ("irse",), 0.2, y=0.84, size=54)], tex=ARCH)
    add(362.70, V("2796", "u_OqZ0j8PKe8Q.jpg", 1.0, "doc"), [Counter(0, 37, "${:,.0f}", "EL ACRE", 0.9, 1.2, (0.5, 0.42), 190),
                                                          big("MENOS DE 100 DÓLARES LA HECTÁREA", w("menos", 367.3) - 362.7, 0.8, 58, YELLOW)], tex=CLEAN)
    add(369.40, cus(G7.agreement, mode="terms", term_t=[-1, -1, 4.5]), tr="fade", td=0.3, tex=GFX)
    add(375.70, mp("rn_lake", [(0, -83.60, 35.455, 0.64), (7.0, -83.62, 35.457, 0.68)],
                   [LAKE(0.0, 0.1),
                    dict(type="pin", at="bryson", t0=w("bryson", 379.7) - 375.7, label="BRYSON CITY", side="t", box=True, size=44),
                    dict(type="route", path=["bryson", "lv_start"], t0=w("bryson", 379.7) - 375.7 + 0.3, draw=0.6, color=WHITE, width=5, dash=16),
                    dict(type="route", ll=M.rn_lakeview(), t0=w("bryson", 379.7) - 375.7 + 0.8, draw=0.8, color=WHITE, width=5, dash=16),
                    dict(type="route", path=PLAN, t0=w("bryson", 379.7) - 375.7 + 1.5, draw=2.0, color=WHITE, width=5, dash=16),
                    dict(type="pin", at="fontana_dam", t0=w("presa", 382.6) - 375.7, label="PRESA", side="t", box=True, size=44),
                    dict(type="label", at=(-83.66, 35.493), text="≈ 30 MILLAS POR LA ORILLA NORTE", t0=2.6, size=50, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(383.20, kb("f_37414724515.jpg", "in", "doc"), [rich("UNA CARRETERA JUNTO AL AGUA, CON VISTAS AL LAGO", ("agua", "lago"), 0.4, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(388.60, kb("u_CE9u5g_AJk0.jpg", "in", "doc"), [Darken(0.6), big("NORTH SHORE ROAD", w("north", 390.7) - 388.6, 0.45, 130, YELLOW, "pop"),
                                                      big("LA CARRETERA DE LA ORILLA NORTE", 0.4, 0.62, 52, WHITE)], tex=CLEAN)
    add(391.60, kb("u_OYd-CB6usX8.jpg", "in", "doc"), [rich("VOLVER A TENER A MANO A SUS MUERTOS", ("muertos",), 0.6, y=0.84, size=56)], tex=CLEAN)
    add(397.70, kb("u_MjH55Ef3w_0.jpg", "in", "warm"), [rich("TURISTAS · GASOLINERAS · NEGOCIOS", ("turistas", "gasolineras", "negocios"), w("turistas", 400.6) - 397.7, step=0.5, y=0.84, size=58)],
        tex=CLEAN)
    add(402.90, fr("f_21954793770.jpg", "Juzgado del condado de Swain, Bryson City · State Archives of North Carolina"),
        [rich("SWAIN SE HABÍA QUEDADO SIN SU MEJOR TIERRA", ("tierra",), 0.3, y=0.065, size=50, maxw=0.85)], tex=ARCH)
    add(407.60, kb("f_45923250064.jpg", "in", "doc"), [Darken(0.55), big("TU INDEMNIZACIÓN DE VERDAD", w("indemnización", 410.3) - 407.6, 0.5, 96, YELLOW, "pop")],
        tex=CLEAN)
    add(411.50, cus(G7.agreement, mode="clause", hl_t=6.4, red_t=10.0), tr="fade", td=0.3, tex=GFX)
    add(425.50, kb("u_6xafY_AEILM.jpg", "in", "doc"), [rich("A NADIE LE PREOCUPÓ DEMASIADO", ("nadie",), 0.2, y=0.12, size=58),
                                                      rich("CUANDO ACABARA LA GUERRA, HABRÍA DINERO", ("dinero",), 2.0, y=0.84, size=52, maxw=0.85)], tex=CLEAN)
    add(431.10, kb("f_37016472650.jpg", "in", "doc"), [rich("LES HABÍAN PROMETIDO UN CAMINO", ("camino",), 0.2, y=0.12, size=58),
                                                     big("Y EMPEZARON A ESPERARLO", w("esperarlo", 435.7) - 431.1 - 0.4, 0.84, 78, YELLOW, "pop")],
        tr="fade", td=0.3, tex=CLEAN)

    # ============================== CAP 4: LA ROCA (436.9 - 573.2)
    bg, ov = chapter(4, "La roca", "f_36640507290.jpg", year="1945 – 1962")
    add(436.90, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(439.50, kb("f_9258163692.jpg", "in", "doc"), [rich("FONTANA YA DABA LUZ", ("luz",), 0.2, y=0.84, size=60),
                                                    Caption("Presa Fontana · foto: Tennessee Valley Authority (CC BY 2.0)", None, 1.2, y=0.1)], tex=CLEAN)
    add(443.70, V("18305", "u_8lnbXtxFGZw.jpg", 0.5, "dark"), [big("EL MOMENTO DE CUMPLIR", 0.1, 0.4, 84, WHITE),
                                                            big("PERO EL DINERO LLEGABA A CUENTAGOTAS", 1.8, 0.6, 58, YELLOW)], tex=DARK)
    add(447.40, cus(G7.road_progress, stage=1948, t0=1.2, nothing_t=8.0), tr="fade", td=0.3, tex=GFX)
    add(456.70, fr("l_1a11171.jpg", "«Carretera junto al lago Cheoah, hacia la presa Fontana» · postal de 1948", g="doc"),
        [Badge("AÑOS 50", 0.3, None)], tex=ARCH)
    add(463.90, V("12292", "u_73OJLcahQHg.jpg", 0.5, "warm"), [rich("SE FUERON HACIENDO MAYORES", ("mayores",), 0.3, y=0.84, size=58)], tr="fade", td=0.3, tex=CLEAN)
    add(468.50, kb("u_egeIhNGnI5M.jpg", "in", "dark"), [rich("ENTERRADOS LEJOS DE SUS PADRES", ("lejos",), 0.8, y=0.84, size=58)], tex=DARK)
    add(473.40, mp("rn_loc", [(0, -83.47, 35.44, 0.85), (6.0, -83.48, 35.445, 1.0)],
                   [dict(type="pin", at="bryson", t0=0.2, label="BRYSON CITY", side="b", size=40),
                    dict(type="route", path=STATE_RD, t0=w("carretera", 477.4) - 473.4, draw=1.4, color=WHITE, width=8),
                    dict(type="pin", at="lv_start", t0=w("límite", 479.5) - 473.4, label="LÍMITE DEL PARQUE", side="l", size=40),
                    dict(type="label", at=(-83.47, 35.465), text="1958 · LA PARTE DEL ESTADO", t0=0.6, size=50, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(480.40, V("7163", "u_tWptj-b6IqM.jpg", 1.0, "doc"), [Badge("1960", 0.2, None), rich("LAS MÁQUINAS ENTRAN EN EL PARQUE", ("parque",), 0.6, y=0.84, size=56)],
        tex=CLEAN)
    add(485.50, mp("rn_loc", [(0, -83.50, 35.452, 1.0), (2.0, -83.51, 35.454, 1.1)],
                   [dict(type="route", path=STATE_RD, t0=0.0, draw=0.1, color=WHITE, width=8),
                    dict(type="route", ll=M.rn_lakeview()[:300], t0=0.2, draw=1.6, color=YELLOW, width=8),
                    dict(type="label", at=(-83.50, 35.468), text="LA LADERA NORTE", t0=0.6, size=46)]),
        tr="fade", td=0.3, tex=GFX)
    add(487.80, kb("f_36890263971.jpg", "in", "doc"), [rich("LA MONTAÑA DIO EL PRIMER AVISO", ("aviso",), 0.4, y=0.84, size=58)], tex=CLEAN)
    add(490.30, kb("f_37030843805.jpg", "l", "doc"), [rich("AL DERRETIRSE LA NIEVE SOBRE LOS CORTES…", ("cortes…",), 0.2, y=0.12, size=52),
                                                    big("OLÍA A AZUFRE", w("olía", 493.8) - 490.3, 0.84, 96, YELLOW, "pop")], tex=CLEAN)
    add(495.10, kb("l_8d04921.jpg", "in", "archival"), [rich("PARA LOS OBREROS, UNA MOLESTIA MÁS", ("molestia",), 0.2, y=0.84, size=56)], tex=ARCH)
    add(497.50, V("44616", "u_5B9P725PnuQ.jpg", 1.0, "cold"), [rich("PARA EL PARQUE, UN PROBLEMA MUY SERIO", ("serio",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(501.30, kb("f_36223363743.jpg", "in", "doc"), [big("EL CULPABLE TIENE NOMBRE", 0.1, 0.12, 64),
                                                     big("ANAKEESTA", w("anarquista", 506.0) - 501.3, 0.5, 170, YELLOW, "pop"),
                                                     Caption("Anakeesta, Great Smoky Mountains · foto: James St. John (CC BY 2.0)", None, 2.0)], tex=CLEAN)
    add(507.20, kb("u_j7WBHTOIyBA.jpg", "in", "dark"), [rich("UNA PIZARRA MUY VIEJA CARGADA DE PIRITA", ("pirita",), 0.2, y=0.12, size=54),
                                                      big("PARECE ORO… Y NO LO ES", w("parece", 510.5) - 507.2, 0.84, 76, YELLOW)], tex=DARK)
    add(512.10, cus(G7.rock, mode="buried"), tr="fade", td=0.3, tex=GFX)
    add(517.10, cus(G7.apple), tr="fade", td=0.3, tex=GFX)
    add(523.10, warp(G7.rock, 0.0, 0.62, mode="cut"), tr="fade", td=0.3, tex=GFX)
    add(531.60, kb("u_L581hl6Gbok.jpg", "in", "doc"), [big("ÁCIDA Y CARGADA DE METALES", 0.1, 0.84, 72, YELLOW)], tex=CLEAN)
    add(533.70, V("529", "u_cwQQXPpH4pY.jpg", 1.0, "bw"), [rich("LLEGA A LOS ARROYOS Y MATA LO QUE VIVE EN ELLOS", ("mata",), 0.2, y=0.12, size=52, maxw=0.85),
                                                        big("LOS PECES · LAS PLANTAS · TODO", w("peces", 536.7) - 533.7, 0.84, 70, YELLOW)], tex=CLEAN)
    add(538.70, kb("f_36890263971.jpg", "punch", "doc"), [Darken(0.5), big("UNA MONTAÑA ABIERTA", 0.6, 0.42, 110, WHITE),
                                                        big("NO SE PUEDE VOLVER A CERRAR", 2.4, 0.6, 76, YELLOW)], tex=CLEAN)
    add(543.40, cus(G3.document, lines=[("1962", 70), ("OFICINA FEDERAL DE CARRETERAS", 40), ("", 8), ("AL DIRECTOR DEL SERVICIO", 40),
                                        ("DE PARQUES NACIONALES:", 40), ("", 8), ("REPLANTEAR LA OBRA EN SERIO.", 44)], sign_t=5.4),
        tr="whip_l", td=0.25, tex=GFX)
    add(553.20, V("10395", "u_wB9iWZKwljw.jpg", 0.5, "dark"), [Stamp("INDEFENDIBLE", w("indefendible", 555.6) - 553.2, RED, (0.5, 0.5), -10, 130)],
        tex=DARK)
    add(557.70, kb("f_36640507290.jpg", "in", "dark"), [rich("EL AVISO PERFECTO PARA PARAR", ("parar",), 0.2, y=0.4, size=64)], tex=DARK)
    add(559.60, Solid("black"), [big("NO SE PARÓ", 0.2, 0.5, 170, RED, "pop")], tr="flash", td=0.15, tex=DARK)
    # subscribe CTA
    add(561.20, kb("f_50894285567.jpg", "in", "dark"), [Darken(0.35), rich("ANTES DE LA ÚLTIMA OBRA… UNA COSA", ("cosa",), 0.3, y=0.4, size=60),
                                                      rich("HISTORIAS DE CAMINOS QUE ALGUIEN DEJÓ A MEDIAS", ("medias",), w("historias", 566.7) - 561.2, step=0.1, y=0.55, size=50, maxw=0.85)],
        tr="fade", td=0.3, tex=DARK)
    add(568.70, kb("f_50894285567.jpg", "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe),
                                                              big("AQUÍ SÍ TERMINAMOS LO QUE EMPEZAMOS", w("aquí", 570.4) - 568.7, 0.3, 58, YELLOW)], tex=DARK)

    # ============================== CAP 5: EL TÚNEL Y EL PARÓN (573.2 - 731.0)
    bg, ov = chapter(5, "El túnel", "f_50894279002.jpg", year="1960 – 1978")
    add(573.20, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(576.80, mp("rn_loc", [(0, -83.49, 35.452, 0.9), (8.0, -83.52, 35.456, 1.15)],
                   [dict(type="route", path=STATE_RD, t0=0.0, draw=0.1, color=WHITE, width=8),
                    dict(type="route", ll=M.rn_lakeview()[:300], t0=0.0, draw=0.1, color=YELLOW, width=8),
                    dict(type="route", ll=M.rn_lakeview()[299:], t0=0.6, draw=w("1970", 582.4) - 576.8 + 1.0, color=YELLOW, width=8),
                    dict(type="label", at=(-83.50, 35.470), text="CURVA A CURVA, HACIA EL OESTE", t0=0.6, size=46),
                    dict(type="pin", at="noland", t0=w("puente", 585.9) - 576.8, label="PUENTE DE NOLAND CREEK", side="b", size=40),
                    dict(type="pin", at="tunnel", t0=w("túnel", 591.1) - 576.8 - 0.4, label="EL TÚNEL · 1970", side="l", box=True, size=46)]),
        tr="zoom", td=0.3, tex=GFX)
    add(591.70, kb("f_50894285987.jpg", "in", "none"), [torch(((0.4, 0.55), (0.6, 0.5)), r=480, amb=0.1),
                                                      rich("EXCAVADO · REVESTIDO · LISTO PARA LOS AUTOS", ("excavado", "revestido", "listo"), w("excavado", 593.3) - 591.7, step=0.3, y=0.86, size=52, maxw=0.9)],
        tex=DARK)
    add(596.10, kb("f_50894279002.jpg", "in", "doc"), [rich("DESDE FUERA, PARECE LA ENTRADA A ALGO IMPORTANTE", ("importante",), 0.2, step=0.1, y=0.86, size=52, maxw=0.85)],
        tex=CLEAN)
    add(599.30, V("45703", "u_XG88BYDSDZA.jpg", 0.5, "doc"), [Darken(0.35), Counter(0, 4, "${:,.0f} MILLONES", "GASTADOS PARA ENTONCES", 1.4, 1.2, (0.5, 0.45), 160)],
        tex=CLEAN)
    add(603.20, mp("rn_loc", [(0, -83.527, 35.457, 1.4), (7.0, -83.531, 35.458, 1.75)],
                   [dict(type="route", ll=M.rn_lakeview(), t0=0.0, draw=0.1, color=YELLOW, width=8),
                    dict(type="pin", at="noland", t0=0.3, label="PUENTE DE NOLAND CREEK · SIGUE AHÍ", side="b", box=True, size=44),
                    dict(type="label", at=(-83.519, 35.4725), text="NOLAND CREEK", t0=0.8, size=40, color=BLUE),
                    dict(type="pin", at="tunnel", t0=w("cargando", 607.5) - 603.2, label="HASTA EL TÚNEL", side="t", size=42),
                    dict(type="route", ll=M.rn_lakeview(), t0=w("cargando", 607.5) - 603.2, draw=0.1, color=YELLOW, width=8, traffic=5, speed=160)]),
        tr="zoom", td=0.3, tex=GFX)
    add(610.20, cus(G7.road_progress, stage=1972, t0=1.8), tr="fade", td=0.3, tex=GFX)
    add(615.30, kb("u_QxZG4Q750rQ.jpg", "in", "dark"), [big("¿POR QUÉ JUSTO ENTONCES?", 0.2, 0.45, 90, WHITE),
                                                      big("POR LA SUMA DE TODO", 1.9, 0.6, 70, YELLOW)], tex=DARK)
    add(618.30, kb("f_36640507290.jpg", "in", "doc"), [big("LA ROCA ÁCIDA SEGUÍA AHÍ", 0.2, 0.84, 72, YELLOW)], tex=CLEAN)
    add(620.50, kb("u_WFvvQj48KeA.jpg", "in", "doc"), [big("CADA MILLA, MÁS CARA QUE LA ANTERIOR", 0.2, 0.84, 64, YELLOW)], tex=CLEAN)
    add(622.80, V("100190", "u_ihxgrRm4UGc.jpg", 1.0, "doc"), [rich("EL PARQUE YA NO QUERÍA SEGUIR PARTIENDO LA MONTAÑA", ("montaña",), 0.2, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(626.40, kb("u_tWptj-b6IqM.jpg", "out", "bw"), [big("LAS MÁQUINAS SE FUERON", 0.2, 0.42, 84, WHITE), big("Y NO VOLVIERON", 1.5, 0.58, 84, YELLOW)],
        tex=ARCH)
    add(628.60, mp("rn_lake", [(0, -83.55, 35.455, 0.95), (6.5, -83.60, 35.46, 0.85)],
                   [LAKE(0.0, 0.1), dict(type="route", path=STATE_RD, t0=0.0, draw=0.1, color=WHITE, width=6), LV(0.0, 0.1),
                    dict(type="label", at=(-83.50, 35.472), text="≈ 6 MILLAS DE ASFALTO", t0=w("seis", 631.2) - 628.6, size=48, box=True),
                    dict(type="pin", at="tunnel", t0=w("túnel", 632.9) - 628.6, label="UN TÚNEL PERFECTO", side="b", size=42),
                    dict(type="label", at=(-83.62, 35.478), text="DETRÁS, EL BOSQUE", t0=w("bosque", 635.1) - 628.6, size=50, color=GREEN)]),
        tr="zoom", td=0.3, tex=GFX)
    add(635.70, mp("rn_lake", [(0, -83.66, 35.46, 0.66), (5.5, -83.68, 35.462, 0.70)],
                   [LAKE(0.0, 0.1), LV(0.0, 0.1),
                    dict(type="route", path=PLAN, t0=0.2, draw=1.6, color=RED, width=6, dash=14),
                    dict(type="label", at=(-83.67, 35.503), text="FALTABAN MÁS DE 20 MILLAS", t0=0.6, size=54, color=RED),
                    *CEMS(w("cementerios", 640.4) - 635.7),
                    dict(type="label", at=(-83.67, 35.443), text="AHÍ ESTABAN LOS CEMENTERIOS", t0=w("cementerios", 640.4) - 635.7 + 0.3, size=48, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(641.90, V("2026", "u_UynJGy6a3t4.jpg", 2.0, "doc"), [rich("YA SE PODÍA MANEJAR HASTA EL TÚNEL Y CRUZARLO", ("túnel",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(645.90, kb("f_37414724515.jpg", "in", "doc"), [rich("…Y MIRAR EL LAGO", ("lago",), 0.2, y=0.84, size=60)], tex=CLEAN)
    add(647.40, kb("u_SNcdJjKTzdE.jpg", "punch", "dark"), [big("A LOS ABUELOS NO SE LLEGABA", 0.2, 0.84, 76, YELLOW, "pop")], tex=DARK)
    add(649.90, Solid("dark_grid"), [
                                                      BigText("HELEN Y MILDRED CABLE", "bebas", 120, YELLOW, (0.5, 0.45), w("helen", 651.7) - 649.9, None, "pop", tracking=6),
                                                      BigText("DOS HERMANAS QUE CRECIERON EN LA ORILLA NORTE", "bebas", 52, WHITE, (0.5, 0.6), w("crecido", 654.0) - 649.9, None, "up", tracking=3)],
        tr="fade", td=0.3, tex=DARK)
    add(655.60, V("23411", "u_dPw2s3_QWtw.jpg", 1.0, "warm"), [Badge("1976 · UNA REUNIÓN FAMILIAR", 0.3, None),
                                                            rich("RECUPERAR UNA COSTUMBRE DE LAS MONTAÑAS", ("costumbre",), 2.2, y=0.84, size=54)], tex=CLEAN)
    add(662.10, fr("f_40343994254.jpg", "Día de Decoración en el parque · foto: NPS / Warren Bielenberg (dominio público)", g="doc"),
        [big("EL DÍA DE DECORACIÓN", 0.2, 0.065, 72, YELLOW)], tex=CLEAN)
    add(664.70, kb("f_39243840250.jpg", "in", "doc"), [rich("LA FAMILIA LIMPIA SUS TUMBAS Y LAS ADORNA CON FLORES", ("limpia", "flores"), 0.3, step=0.1, y=0.86, size=50, maxw=0.85)],
        tex=CLEAN)
    add(668.40, cus(G4.calendar, cards=[("4.º", "MAYO DE 1978", "EL CUARTO DOMINGO", 0.3, (60, 62, 66))], title="LA PRIMERA VEZ"),
        tr="fade", td=0.3, tex=GFX)
    add(672.50, kb("u_OYd-CB6usX8.jpg", "in", "doc"), [rich("EN EL CEMENTERIO DE SU FAMILIA", ("familia",), 0.2, y=0.84, size=58)], tex=CLEAN)
    add(674.50, V("24918", "u_fhFUNQk3h6M.jpg", 1.0, "doc"), [rich("CRUZARON EL LAGO EN LANCHAS DE PESCA", ("lanchas",), 0.2, y=0.12, size=56),
                                                           Counter(0, 100, "+{:,.0f}", "PARIENTES", w("100", 678.4) - 674.5 - 0.6, 1.0, (0.5, 0.6), 170)], tex=CLEAN)
    add(679.20, kb("u_fRitufEoeTs.jpg", "in", "dark"), [rich("LO QUE ENCONTRARON LES DOLIÓ", ("dolió",), 0.2, y=0.84, size=60)], tex=DARK)
    add(682.00, kb("u_Kbrlt7dkimk.jpg", "in", "bw"), [big("1/3", 0.8, 0.42, 200, YELLOW, "pop"),
                                                     big("DE LAS LÁPIDAS, CAÍDAS O GIRADAS", 1.6, 0.62, 64, WHITE)], tex=ARCH)
    add(686.30, kb("u_SNcdJjKTzdE.jpg", "l", "doc"), [big("EL BOSQUE SE HABÍA COMIDO LAS LOMAS", 0.2, 0.84, 66, YELLOW)], tex=CLEAN)
    add(688.50, cus(G7.headstone), [rich("SU HERMANITO, SHUFFORD", ("shufford",), w("chaufford", 691.6) - 688.5 - 2.0, y=0.92, size=46)], tr="fade", td=0.4, tex=GFX)
    add(696.70, kb("u_XUEYM2Htt8Y.jpg", "in", "doc"), [rich("EN LA PIEDRA, SU NOMBRE ESTÁ MAL ESCRITO", ("mal",), 0.2, y=0.84, size=56),
                                                     big("NADIE HABÍA VUELTO PARA CORREGIRLO", w("nadie", 700.0) - 696.7, 0.12, 58, YELLOW)], tex=CLEAN)
    add(702.40, kb("u_dWSbI693jZU.jpg", "in", "warm"), [rich("LIMPIARON · ENDEREZARON · PUSIERON FLORES", ("flores",), 0.4, step=0.35, y=0.84, size=56)], tex=CLEAN)
    add(706.80, fr("l_578023p.jpg", "Cementerio de Proctor · HABS, Library of Congress"), [Badge("AL AÑO SIGUIENTE · PROCTOR", 0.3, None)], tex=ARCH)
    add(711.50, kb("u_uPzrMFwC-mA.jpg", "in", "doc"), [rich("EL PARQUE EMPEZÓ A CRUZAR A LAS FAMILIAS EN SUS LANCHAS", ("lanchas",), 0.3, step=0.09, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(716.50, kb("u_73OJLcahQHg.jpg", "in", "warm"), [rich("UNA ASOCIACIÓN PARA LOS CEMENTERIOS DE LA ORILLA NORTE", ("asociación",), 0.4, step=0.09, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(723.30, kb("u_nSpj-Z12lX0.jpg", "in", "dark"), [rich("SI EL GOBIERNO NO CUMPLÍA POR LAS BUENAS…", ("buenas…",), w("si", 726.2) - 723.3, y=0.35, size=58),
                                                      big("¿PODÍA OBLIGARLO UN JUEZ?", w("podía", 728.7) - 723.3, 0.6, 96, YELLOW, "pop")], tex=DARK)

    # ============================== CAP 6: EL JUEZ Y EL CHEQUE (731.0 - 873.4)
    bg, ov = chapter(6, "El juez y el cheque", "u_YL5dq3CXNlI.jpg", year="1983 – 2018")
    add(730.80, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(734.30, V("47687", "u_SlyYm_CJW8E.jpg", 1.0, "doc"), [rich("VECINOS DE SWAIN CONTRA EL GOBIERNO", ("gobierno",), 0.2, y=0.12, size=56),
                                                           big("QUE SE CUMPLIERA LO FIRMADO EN 1943", w("cumpliera", 737.5) - 734.3, 0.84, 62, YELLOW)], tex=CLEAN)
    add(740.00, kb("u_6sI88x150Xs.jpg", "in", "doc"), [Darken(0.45), Badge("TRIBUNAL FEDERAL DE APELACIONES", 0.3, None),
                                                     big("1983", w("1983", 743.9) - 740.0, 0.5, 200, YELLOW, "pop"),
                                                     big("HUBO SENTENCIA", w("sentencia", 745.8) - 740.0, 0.72, 66, WHITE)], tex=CLEAN)
    add(746.40, kb("u_TdNLjGXVH3s.jpg", "punch", "dark"), [Stamp("NO LES DIO LA RAZÓN", 0.6, RED, (0.5, 0.5), -10, 110)], tex=DARK, post=postshake(3))
    add(749.40, cus(G7.agreement, mode="clause", hl_t=0.6, red_t=4.0), tr="fade", td=0.3, tex=GFX)
    add(757.40, kb("u_a6h5e59r15o.jpg", "in", "doc"), [rich("INTERIOR NI SIQUIERA ESTABA OBLIGADO A PEDIRLO", ("obligado",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(761.40, V("28901", "u_egeIhNGnI5M.jpg", 1.0, "dark"), [big("UN GOLPE SECO", 0.2, 0.15, 70, WHITE),
                                                            Counter(0, 40, "{:,.0f} AÑOS", "ESPERANDO ALGO QUE, SEGÚN EL JUEZ, NADIE LES DEBÍA", 2.4, 1.0, (0.5, 0.5), 170)],
        tex=DARK)
    add(769.00, Split([kb("f_37016472650.jpg", "in", "doc"), kb("f_36640507290.jpg", "in", "doc")], labels=["LA CARRETERA ENTERA", "NI UN CORTE MÁS"]),
        [big("EL CONDADO SE PARTIÓ EN DOS", 0.2, 0.1, 64, YELLOW)], tex=CLEAN)
    add(772.00, kb("f_37016472650.jpg", "l", "doc"), [rich("UNOS: LAS 30 MILLAS, LO PACTADO, LOS VISITANTES", ("30", "pactado", "visitantes"), 0.3, step=0.12, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(777.50, kb("f_36640507290.jpg", "in", "doc"), [rich("OTROS: NI UN CORTE MÁS EN UN PARQUE NACIONAL", ("corte",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(781.60, V("22959", "u_W5QT1mUUCkk.jpg", 1.0, "warm"), [rich("LA LÍNEA PASABA POR DENTRO DE LA MISMA FAMILIA", ("familia",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(785.50, kb("u_XU93D-JThyE.jpg", "in", "doc"), [Badge("OCTUBRE DE 2000", 0.3, None),
                                                     Counter(0, 16, "${:,.0f} MILLONES", "PARA RETOMAR LA CARRETERA", w("16", 790.8) - 785.5, 1.0, (0.5, 0.5), 150)],
        tex=CLEAN)
    add(793.90, kb("u_ZXfQvRfLTcI.jpg", "in", "doc"), [rich("ANTES, ESTUDIAR EL IMPACTO EN EL PARQUE", ("impacto",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(798.60, V("18288", "u_y02jEX_BOO0.jpg", 0.5, "doc"), [rich("INGENIEROS · GEÓLOGOS · AUDIENCIAS PÚBLICAS · MILES DE PÁGINAS",
                                                                ("ingenieros", "geólogos", "audiencias", "páginas"), 0.4, step=0.45, y=0.84, size=48, maxw=0.9)], tex=CLEAN)
    add(804.20, kb("u_AFB6S2kibuk.jpg", "in", "doc"), [Darken(0.55), rich("DE LA CARRETERA COMPLETA A ARREGLOS MÁS PEQUEÑOS", ("completa", "pequeños"), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=CLEAN)
    add(809.40, kb("f_36223363743.jpg", "in", "doc"), [big("TODAS CHOCABAN CON LO MISMO", 0.1, 0.4, 70, WHITE),
                                                     big("LA ROCA Y LA FACTURA", w("roca", 811.5) - 809.4, 0.58, 96, YELLOW, "pop")], tex=CLEAN)
    add(812.90, V("18305", "u_BRl69uNXr7g.jpg", 4.0, "dark"), [Darken(0.35), Counter(0, 600, "≈ ${:,.0f} MILLONES", "PARA TERMINARLA", 2.2, 1.4, (0.5, 0.48), 150)],
        tex=DARK)
    add(817.60, cus(G3.document, lines=[("DECISIÓN FINAL", 70), ("28 DE DICIEMBRE DE 2007", 40), ("", 12), ("NO SE CONSTRUYE LA CARRETERA.", 42),
                                        ("EN SU LUGAR, SE PAGARÁ AL CONDADO.", 42)], sign_t=5.2), tr="whip_l", td=0.25, tex=GFX)
    add(825.00, kb("f_7263397008.jpg", "in", "doc"), [Badge("6 DE FEBRERO DE 2010", 0.3, None),
                                                    LowerThird("KEN SALAZAR", "Secretario del Interior · foto de archivo (USFWS, dominio público)", w("salazar", 831.2) - 825.0 - 1.0)],
        tex=CLEAN)
    add(832.40, cus(G7.check, mode="check"), tr="fade", td=0.3, tex=GFX)
    add(837.40, cus(G7.agreement, mode="void"), tr="whip_l", td=0.25, tex=GFX)
    add(841.30, V("45703", "u_XG88BYDSDZA.jpg", 3.0, "doc"), [rich("EL DINERO LLEGÓ POR PARTES", ("partes",), 0.2, y=0.12, size=58),
                                                           Badge("JULIO DE 2018 · ÚLTIMO PAGO", w("julio", 844.6) - 841.3, None)], tex=CLEAN)
    add(845.90, kb("f_6261748687.jpg" if os.path.exists(os.path.join(IMG, "f_6261748687.jpg")) else "f_45923250064.jpg", "in", "doc"),
        [Darken(0.45), rich("«DE VERDAD NOS LLEGÓ EL DINERO»", ("verdad",), 0.2, y=0.45, size=72, maxw=0.85),
         big("— EL ADMINISTRADOR DEL CONDADO DE SWAIN", 1.8, 0.62, 44, (200, 200, 200))], tex=CLEAN)
    add(850.40, cus(G7.check, mode="vault"), [rich("NI SIQUIERA PUEDE GASTARLO A SU GUSTO", ("gusto",), 0.2, y=0.1, size=52)], tr="fade", td=0.3, tex=GFX)
    add(862.60, kb("f_50894285567.jpg", "in", "doc"), [rich("EN EL BANCO, EL PRECIO DE SU CARRETERA", ("precio",), 0.2, y=0.12, size=56),
                                                     big("LO QUE NO TIENE ES LA CARRETERA", w("lo", 865.7) - 862.6, 0.84, 70, YELLOW, "pop")], tex=CLEAN)
    add(867.70, V("100233", "u_38gjpr9UxiA.jpg", 8.0, "doc"), [rich("Y LA CARRETERA QUE NUNCA SE TERMINÓ…", ("nunca",), 0.2, y=0.12, size=56),
                                                            big("SIGUE COSTANDO", w("sigue", 871.7) - 867.7, 0.84, 90, YELLOW, "pop")], tex=CLEAN)

    # ============================== CAP 7: HOY (873.3 - 999.1)
    bg, ov = chapter(7, "Hoy", "f_37016472650.jpg", year="2023 – 2026")
    add(873.30, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(876.80, mp("rn_loc", [(0, -83.51, 35.452, 0.9), (4.0, -83.515, 35.454, 1.0)],
                   [LV(0.2, 1.6, YELLOW, 8),
                    dict(type="label", at=(-83.51, 35.472), text="LAKEVIEW DRIVE", t0=w("lakeview", 877.7) - 876.8, size=64, box=True),
                    dict(type="label", at=(-83.51, 35.437), text="6,5 MILLAS · ≈ 10,5 KM", t0=w("seis", 879.2) - 876.8, size=52, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(880.70, kb("u_fPWTPqLqAIk.jpg", "in", "doc"), [Badge("VERANO DE 2023", 0.2, None),
                                                           rich("CERRADA PARA REHACERLA DE PUNTA A PUNTA", ("punta",), 0.8, y=0.84, size=56)], tex=CLEAN)
    add(885.50, kb("u_6mxkt0IlgQQ.jpg", "in", "doc"), [big("ASFALTO NUEVO", 0.1, 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(886.80, kb("u_JMGkA06zHZ4.jpg", "in", "doc"), [big("BARANDAS NUEVAS", 0.1, 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(888.10, kb("u_-uyajkK3ON4.jpg", "in", "doc"), [big("DRENAJES Y ESTACIONAMIENTOS", 0.1, 0.84, 76, YELLOW, "pop")], tex=CLEAN)
    add(890.20, V("41537", "u_l_0mNTbf6F8.jpg", 2.0, "doc"), [rich("REABRIÓ A FINALES DE 2023", ("2023",), 0.2, y=0.12, size=56),
                                                            big("ÚLTIMA CAPA: PRIMAVERA DE 2024", w("última", 892.5) - 890.2, 0.84, 64, YELLOW)], tex=CLEAN)
    add(896.30, cus(G7.bars, items=[("2000 · EL CONGRESO, PARA TERMINARLA", 16, "$16 MILLONES", (200, 200, 200)),
                                    ("2023 · LA OBRA, PARA REHACERLA", 15.9, "≈ $16 MILLONES", YELLOW)],
                    title="CASI LO MISMO", unit="MILLONES DE DÓLARES", t0=0.6, step=3.0), tr="fade", td=0.3, tex=GFX)
    add(903.20, kb("f_50894279002.jpg", "in", "doc"), [rich("PARA ACABARLA, NUNCA APARECIÓ", ("nunca",), 0.2, y=0.12, size=58),
                                                     big("PARA DEJARLA COMO NUEVA, SÍ", w("dinero", 906.7) - 903.2, 0.84, 78, YELLOW, "pop")], tex=CLEAN)
    add(908.70, kb("u_fhFUNQk3h6M.jpg", "in", "dark"), [Darken(0.5), Badge("EL OTRO MISTERIO", 0.2, None)] +
        question("¿Y cómo llegan hoy las familias a esas tumbas?", ("tumbas?", "tumbas"), size=76), tr="glitch", td=0.3, tex=DARK)
    add(914.70, kb("u_YYPH07g_ku0.jpg", "in", "doc"), [big("POR AGUA", 0.1, 0.45, 160, YELLOW, "pop"),
                                                          big("COMO HACE MÁS DE 40 AÑOS", 0.8, 0.64, 60, WHITE)], tex=CLEAN)
    add(917.10, cus(G7.valley, mode="boat"), [Badge("DE ABRIL A MEDIADOS DE OCTUBRE", 0.3, None),
                                             rich("EN LANCHA · Y EN ALGUNOS TRAMOS, EN TODOTERRENO", ("lancha", "todoterreno"), 2.6, step=0.12, y=0.93, size=44, maxw=0.9)],
        tr="fade", td=0.3, tex=GFX)
    add(923.70, kb("u_scVKJTfUsKg.jpg", "in", "doc"), [rich("UNA DE ESAS LANCHAS SE LLAMA «MISS HAZEL»", ("hazel»",), 0.3, step=0.1, y=0.12, size=54, maxw=0.85),
                                                     big("COMO EL ARROYO DE PROCTOR", w("como", 926.4) - 923.7, 0.86, 60, YELLOW)], tex=CLEAN)
    add(927.80, V("24993", "u_XPZu8CfuZLY.jpg", 1.0, "doc"), [rich("BAJAS EN LA ORILLA · CUESTA ARRIBA · LA LOMA", ("loma",), 0.3, step=0.3, y=0.84, size=54, maxw=0.85)],
        tex=CLEAN)
    add(932.00, kb("f_40343994254.jpg", "in", "doc"), [rich("LIMPIAS LA TUMBA Y LA ADORNAS CON FLORES", ("flores",), 0.3, y=0.86, size=54, maxw=0.85)], tex=CLEAN)
    add(935.00, kb("u_hvAUtO1OEP4.jpg", "in", "warm"), [big("HECHAS A MANO, CON PAPEL CREPÉ", 0.3, 0.86, 64, YELLOW)], tex=CLEAN)
    add(937.40, V("23133", "u_EUr3ywS260Y.jpg", 1.0, "warm"), [rich("DESPUÉS SE CANTA · Y SE COME TODOS JUNTOS", ("canta", "juntos"), 0.2, step=0.15, y=0.84, size=54, maxw=0.85)],
        tex=CLEAN)
    add(941.10, kb("u_406eekQWH7w.jpg", "in", "warm"), [big("CARNE DE CERDO DESMENUZADA", 0.1, 0.84, 66, YELLOW, "pop")], tex=CLEAN)
    add(942.90, kb("u_Gc-Gf7egfRg.jpg", "in", "warm"), [big("HOJAS DE COL · MAÍZ CON CREMA", 0.1, 0.84, 66, YELLOW, "pop")], tex=CLEAN)
    add(945.10, kb("f_48095288746.jpg", "in", "doc"), [Darken(0.5), Counter(0, 1000, "+{:,.0f}", "TUMBAS QUE NUNCA SE MOVIERON", 0.8, 1.2, (0.5, 0.45), 170),
                                                     big("28 CEMENTERIOS", 0.3, 0.15, 64, WHITE)], tex=CLEAN)
    add(950.10, kb("f_48095286526.jpg", "in", "doc"), [Badge("DESDE 1980", 0.2, None),
                                                     rich("CUADRILLAS DEL PARQUE LOS MANTIENEN LIMPIOS", ("limpios",), 0.6, y=0.84, size=54, maxw=0.85)], tex=CLEAN)
    add(955.30, kb("f_10172654564.jpg", "in", "doc"), [Darken(0.6), rich("LAS LOMAS, IMPECABLES", ("impecables",), 0.4, y=0.45, size=80),
                                                     big("SEGÚN MILDRED CABLE", 1.6, 0.6, 50, (230, 230, 230))], tex=CLEAN)
    add(960.10, V("21449", "u_hah1pStl7L0.jpg", 0.5, "warm"), [big("3 Y 4 GENERACIONES", w("3", 962.1) - 960.1, 0.45, 110, YELLOW, "pop"),
                                                            rich("HACIENDO EL MISMO VIAJE", ("viaje",), 2.6, y=0.62, size=58)], tex=CLEAN)
    add(965.10, kb("u_FnaiTxmOHhA.jpg", "in", "doc"), [big("OTRA FORMA DE LLEGAR: A PIE", 0.4, 0.84, 72, YELLOW)], tex=CLEAN)
    add(968.30, mp("rn_lake", [(0, -83.64, 35.462, 0.64), (7.5, -83.67, 35.462, 0.70)],
                   [LAKE(0.0, 0.1), LV(0.0, 0.1),
                    dict(type="pin", at="tunnel", t0=0.2, label="TÚNEL", side="r", size=40),
                    dict(type="route", path=TRAIL, t0=w("sendero", 972.0) - 968.3 - 0.4, draw=2.6, color=GREEN, width=6, dash=12),
                    dict(type="label", at=(-83.66, 35.492), text="LAKESHORE TRAIL · ≈ 35 MILLAS", t0=w("lake", 973.0) - 968.3, size=54, box=True),
                    dict(type="pin", at="fontana_dam", t0=w("presa", 975.9) - 968.3, label="PRESA", side="l", size=40)]),
        tr="zoom", td=0.3, tex=GFX)
    add(976.40, kb("u_1wFbQIFO4SY.jpg", "in", "doc"), [rich("A VECES, POR ENCIMA DE LA VIEJA NC 288", ("nc", "288"), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(982.50, kb("f_53336824851.jpg", "in", "doc"), [rich("AUTOS DE LOS AÑOS 20 Y 30", ("20", "30"), 0.3, y=0.12, size=60),
                                                     Caption("Auto abandonado en el parque · foto: Gary Millar (CC BY 2.0)", None, 1.6)], tex=CLEAN)
    add(986.40, V("21549", "u_lPrewM0P7_A.jpg", 1.0, "doc"), [rich("OXIDADOS ENTRE LOS ÁRBOLES", ("oxidados",), 0.2, y=0.12, size=60)], tex=CLEAN)
    add(988.50, kb("u_s-5AFvzQ_z8.jpg", "in", "doc"), [big("CON HELECHOS SALIENDO POR LAS VENTANAS", 0.2, 0.84, 60, YELLOW)], tex=CLEAN)
    add(990.40, fr("l_577096p.jpg", "Casa Calhoun, Proctor · HABS, Library of Congress"), [rich("PROCTOR: ALGUNA CASA QUE EL AGUA NO TOCÓ", ("tocó",), 0.4, step=0.1, y=0.065, size=50, maxw=0.85)],
        tex=ARCH)
    add(996.20, V("17805", "u_fhFUNQk3h6M.jpg", 1.0, "warm"), [rich("CADA VEZ QUE UNA LANCHA CRUZA CON FLORES…", ("flores…",), 0.3, y=0.84, size=56)],
        tr="fade", td=0.4, tex=CLEAN)

    # ============================== CONCLUSIÓN (999.1 - 1098.0)
    q1(999.10, badge="DE VUELTA A LA PREGUNTA 1")
    add(1008.10, kb("f_36640507290.jpg", "in", "dark"), [big("1 · LA ROCA", 0.2, 0.5, 150, YELLOW, "pop")], tr="flash", td=0.2, tex=DARK)
    add(1010.80, warp(G7.rock, 2.0, 0.6, mode="cut"), [rich("CADA MILLA NUEVA, OTRO CORTE · OTRO ARROYO EN PELIGRO", ("corte", "arroyo"), 0.3, step=0.1, y=0.93, size=44, maxw=0.9)],
        tr="fade", td=0.3, tex=GFX)
    add(1017.00, V("529", "u_cwQQXPpH4pY.jpg", 6.0, "doc"), [rich("EN UN LUGAR QUE EXISTE JUSTO PARA PROTEGERLOS", ("protegerlos",), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(1022.00, cus(G7.valley, mode="cut", show_labels=False), [rich("LAS TUMBAS, DETRÁS DE ESA ROCA", ("tumbas",), 0.3, y=0.1, size=56)], tr="fade", td=0.3, tex=GFX)
    add(1025.10, kb("u_fRitufEoeTs.jpg", "punch", "dark"), [rich("ENVENENAR EL PARQUE PARA LLEGAR A LOS MUERTOS", ("envenenar", "muertos"), 0.3, step=0.1, y=0.84, size=54, maxw=0.85)],
        tex=DARK)
    add(1028.10, Solid("black"), [big("2 · EL DINERO", 0.1, 0.5, 150, YELLOW, "pop")], tr="flash", td=0.2, tex=DARK)
    add(1030.30, cus(G7.bars, items=[("TERMINARLA", 600, "≈ $600 MILLONES", RED), ("NO TERMINARLA", 0.0, "$0 PARA EL GOBIERNO", YELLOW)],
                     title="¿CUÁNTO COSTABA CADA CAMINO?", unit="MILLONES DE DÓLARES", t0=0.4, step=w("terminarla", 1034.3) - 1030.3 - 0.4),
        tr="fade", td=0.3, tex=GFX)
    add(1037.00, cus(G7.agreement, mode="clause", hl_t=0.3, red_t=3.4), tr="fade", td=0.3, tex=GFX)
    add(1042.00, V("28901", "u_egeIhNGnI5M.jpg", 4.0, "dark"), [big("Y ASÍ ESPERÓ DÉCADAS", 0.2, 0.84, 76, WHITE)], tex=DARK)
    add(1044.00, kb("u_UgyLA7XBLyQ.jpg", "in", "dark"), [rich("CADA AÑO SIN CARRETERA, UN AÑO MÁS LEJOS DE LOS SUYOS", ("lejos",), 0.3, step=0.1, y=0.84, size=50, maxw=0.85)],
        tex=DARK)
    add(1048.80, fr("f_47848477042.jpg", "Expediente del Departamento de Conservación y Desarrollo · State Archives of North Carolina"),
        [rich("UNA PROMESA FIRMADA NO DESAPARECE SOLA", ("firmada",), 0.2, y=0.065, size=50, maxw=0.85)], tex=ARCH)
    add(1051.80, cus(G7.agreement, mode="parties", times=[-4, -4, -4, -4]), tr="fade", td=0.3, tex=GFX)
    add(1054.30, kb("u_L_U4jhwZ6hY.jpg", "in", "doc"), [rich("EL CONDADO VOLVÍA A EXIGIRLA, UNA Y OTRA VEZ", ("exigirla",), 0.3, step=0.1, y=0.12, size=52, maxw=0.85),
                                                      Badge("2000 · EL CONGRESO PONE DINERO", w("congreso", 1057.6) - 1054.3, None)], tex=CLEAN)
    add(1060.20, kb("f_7263397008.jpg", "in", "doc"), [big("HACÍA FALTA OTRA FIRMA", 0.2, 0.84, 76, YELLOW)], tex=CLEAN)
    add(1063.40, cus(G7.bars, items=[("TERMINARLA", 600, "≈ $600 MILLONES", RED), ("LA FIRMA DE 2010", 52, "$52 MILLONES", YELLOW)],
                     title="MENOS DE LA DÉCIMA PARTE", unit="MILLONES DE DÓLARES", t0=0.2, step=0.6), tr="fade", td=0.3, tex=GFX)
    add(1068.40, kb("u_6kA9FjqUxhM.jpg", "in", "doc"), [big("PARA WASHINGTON, LA SALIDA MÁS BARATA", 0.4, 0.84, 64, YELLOW)], tex=CLEAN)
    add(1071.00, cus(G7.check, mode="check"), [big("PARA EL CONDADO: 52 MILLONES EN LA MANO", 2.6, 0.08, 52, YELLOW)], tr="fade", td=0.3, tex=GFX)
    add(1076.60, cus(G7.year_q, q_t=3.4), [rich("LE PUSIERON PRECIO… PERO NO FECHA", ("precio…", "fecha"), 0.3, y=0.18, size=60)], tr="flash", td=0.2, tex=DARK)
    add(1081.40, fr("f_36562380744.jpg", "El cartel a la entrada de Lakeview Drive · foto: Robert Lz (CC BY 2.0)", g="doc", box=(0.74, 0.70)),
        [rich("EL CARTEL SIGUE IGUAL", ("igual",), 0.3, y=0.065, size=60)], tr="fade", td=0.3, tex=CLEAN)
    add(1086.70, kb("u_fhFUNQk3h6M.jpg", "out", "warm"), [rich("CADA TEMPORADA, A UNA LANCHA CON FLORES DE PAPEL", ("flores", "papel"), 0.3, step=0.1, y=0.84, size=52, maxw=0.85)],
        tex=CLEAN)
    add(1092.20, kb("f_50894285567.jpg", "in", "doc"), [rich("LA CARRETERA SE QUEDÓ A MEDIO CAMINO", ("medio",), 0.2, y=0.12, size=58)], tex=CLEAN)
    add(1094.70, kb("f_26181802147.jpg", "in", "doc"), [Darken(0.6), big("LA PROMESA LA SIGUEN CUMPLIENDO ELLOS", 0.2, 0.42, 72, WHITE),
                                                       big("A MANO", 1.9, 0.6, 130, YELLOW, "pop")], tex=CLEAN)
    add(1097.90, kb("f_37414724515.jpg", "out", "dark"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿HAY EN TU FAMILIA UN PUEBLO, UNA CASA O UNA TUMBA",
                                 line2="A LA QUE YA NO SE PUEDE LLEGAR?", cta="CUÉNTANOS DÓNDE ESTÁ Y QUIÉN LA CUIDA HOY"),
         rich("Por un lago, por una frontera o por la distancia", ("lago", "frontera", "distancia"), w("puede", 1104.6) - 1097.9, step=0.08, y=0.2, size=46, maxw=0.85)],
        tex=DARK)
    return S
