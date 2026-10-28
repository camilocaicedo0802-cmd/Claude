"""The edit: every shot of the Cumberland Gap video, synced to the voice-over."""
import bisect
import math
import os
import sys

import cv2
import numpy as np

import gfx2 as G2
import gfx3 as G3
import gfx4 as G4
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Seq, Solid, Split, Stamp, Still, TimelineBar, Video)
from render import Shot
import words

TOTAL = 1130.37
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
FILM = dict(grain=12, dust=0.6, flicker=0.04, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
GREEN = (60, 150, 80)
GREYC = (110, 112, 116)
DIRT = (176, 132, 84)


def w(word, near, window=8.0):
    try:
        return words.at(word, near, window)
    except KeyError:
        print(f"[anchor] {word!r} not found near {near}; using {near}", file=sys.stderr)
        return near


# ------------------------------------------------------------------ helpers
_SC = {}


def _scenes(name):
    if name not in _SC:
        p = os.path.join(ROOT, "work", "scenes", f"{name}.txt")
        cuts = [float(x) for x in open(p).read().split()] if os.path.exists(p) else []
        _SC[name] = [0.0] + cuts + [1e9]
    return _SC[name]


def vid(name, approx, dur, g="faded", speed=1.0, **kw):
    """Archive film clip starting near `approx`, kept inside one scene when possible."""
    sc = _scenes(name)
    i = bisect.bisect_right(sc, approx) - 1
    a, b = sc[i], sc[i + 1]
    need = dur * speed + 0.25
    s = approx
    if b - s < need:
        s = max(a + 0.1, b - need)
    return Video(f"ia_{name}.mp4", start=s, speed=speed, grade=g, **kw)


# stand-ins used while a Flickr original is not on disk (Flickr throttled the downloads)
FALLBACK = {
    "f_8735585048.jpg": "l_8a16679.jpg", "f_6350137195.jpg": "u_qQxWAnfhUA8.jpg", "f_50217966033.jpg": "u_nDi1FnvsiRk.jpg",
    "f_6350100983.jpg": "u_QxOn3aBTu0A.jpg", "f_6350857048.jpg": "u_IHUSxUm-xRQ.jpg", "f_29304863863.jpg": "u_dXPwkmcrG9A.jpg",
    "f_54659201921.jpg": "u_3-6S9dWxB1Y.jpg", "f_3907232380.jpg": "l_8a16688.jpg", "f_3907232108.jpg": "l_8a16679.jpg",
    "f_4987674424.jpg": "l_31467.jpg", "f_8735585216.jpg": "u_rkCx9LgOK0k.jpg", "f_22936253412.jpg": "u_CoD2Q92UaEg.jpg",
    "f_6350142987.jpg": "u_J3__44tDpAU.jpg", "f_6350079043.jpg": "u_VJQt1JFNXsM.jpg", "f_6350098587.jpg": "u_T0jn-8ZuL5o.jpg",
    "f_6350116055.jpg": "u_eohdpP_XFJw.jpg", "f_51529351091.jpg": "l_63992.jpg", "f_53615094042.jpg": "u_RxVtDbR00cg.jpg",
    "f_52071242701.jpg": "u_WzXvVof2PvI.jpg", "f_51721940911.jpg": "u_KaLTI2GaOWQ.jpg", "f_51721131837.jpg": "u_F2iCP_knaj8.jpg",
    "f_51721940961.jpg": "u_bt-ZiOql8Hc.jpg", "f_51722190863.jpg": "u_g7kDjtik3TE.jpg", "f_51820642354.jpg": "u_PBDu2DN_87U.jpg",
    "f_51614553206.jpg": "u_-uqA4gOLqqg.jpg", "f_6804440059.jpg": "u_M6c3Pkpf1bg.jpg", "f_14019231093.jpg": "u_rNXxhKcFWGo.jpg",
}


def _img(path):
    if not os.path.exists(os.path.join(ROOT, "assets", "img", path)) and path in FALLBACK:
        return FALLBACK[path]
    return path


def have(path):
    return os.path.exists(os.path.join(ROOT, "assets", "img", path))


def kb(path, m="in", g="doc", z=1.0, **kw):
    path = _img(path)
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
    return Still(path, c0, c1, grade=g, **kw)


def fr(path, cap=None, g="archival", **kw):
    return Framed(path, cap, grade=g, **kw)


def cus(fn, **kw):
    return Custom(fn, **kw)


def chapter(num, title, bg, g="dark", year=None):
    ovs = [Darken(0.45, 0.0, 0.3),
           BigText(f"CAPÍTULO {num}" + (f"  ·  {year}" if year else ""), "bebas", 46, YELLOW, (0.5, 0.40), 0.1, None, "up", tracking=6),
           BigText(title, "serif", 104, WHITE, (0.5, 0.52), 0.25, None, "up"),
           FnOverlay(_underline, y=0.62, t0=0.5)]
    return kb(bg, "in", g), ovs


def _underline(img, t, dur, y=0.62, t0=0.5, wmax=560):
    k = ease_out(prog(t, t0, 0.6)) * (1 - prog(t, dur - 0.3, 0.3))
    if k > 0:
        x0 = int(960 - wmax * k)
        cv2.rectangle(img, (x0, int(1080 * y)), (int(960 + wmax * k), int(1080 * y) + 8), YELLOW, -1)


def question(lines, hl, y=0.5, size=72):
    out, t = [], 0.15
    for wd in lines.split():
        st = "h" if wd.strip("¿?,.").lower() in hl else "n"
        out.append((wd, t, st))
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


def postshake(amt):
    def f(img, t, dur):
        return G2.shake_frame(img, t, amt)
    return f


def mp(name, cams, layers, title=None):
    return M.MapScene(name, cams, layers, title)


# local geometry around the pass (metres east/north of the saddle) -------------------------------------
GAP = M.COORDS["gap"]
U = (math.sin(math.radians(52)), math.cos(math.radians(52)))      # along the ridge (to the NE)
D = (-U[1], U[0])                                                   # down the north slope (to the NW)
S_ = (-D[0], -D[1])                                                 # down the south slope (to the SE)


def enm(e, n):
    return (GAP[0] + e / (111320 * math.cos(math.radians(GAP[1]))), GAP[1] + n / 110950)


def at(a, b):  # a metres along U, b metres along D
    return enm(a * U[0] + b * D[0], a * U[1] + b * D[1])


def at_s(a, b):  # b metres along S_ (south slope)
    return enm(a * U[0] + b * S_[0], a * U[1] + b * S_[1])


OLD_25E = [at(60, 1700), at(260, 1250), at(-220, 1020), at(240, 800), at(-220, 600), at(200, 400), at(-140, 190), GAP,
           at_s(160, 220), at_s(-160, 470), at_s(120, 720), M.COORDS["cg_town"]]
TUNNEL = [at(-380, 760), at_s(-380, 760)]
TRAIL = [at(-60, 1650), at(120, 1200), at(-80, 820), at(80, 420), GAP, at_s(120, 250), M.COORDS["gap_cave"]]
TRI = at(-420, 0)
BORDERS = [dict(type="route", path=[TRI, at(1400, 0), at(2600, 0)], smooth=False, t0=0.0, draw=0.8, color=(200, 200, 200), width=3, dash=14),
           dict(type="route", path=[enm(-4000, 0), TRI], smooth=False, t0=0.0, draw=0.8, color=(200, 200, 200), width=3, dash=14),
           dict(type="route", path=[TRI, enm(4000, 0)], smooth=False, t0=0.0, draw=0.8, color=(200, 200, 200), width=3, dash=14)]
# fix the TN line to a parallel through the tri-state point
BORDERS[1]["path"] = [(TRI[0] - 0.05, TRI[1]), TRI]
BORDERS[2]["path"] = [TRI, (TRI[0] + 0.05, TRI[1])]
STATES3 = [dict(type="label", at=enm(-2300, 1500), text="KENTUCKY", size=64),
           dict(type="label", at=enm(2300, 250), text="VIRGINIA", size=64),
           dict(type="label", at=enm(-600, -2000), text="TENNESSEE", size=64)]
APPAL = [(-86.6, 33.6), (-85.2, 34.6), (-83.6, 35.6), (-82.0, 36.4), (-80.4, 37.4), (-79.2, 38.6), (-78.2, 39.6), (-76.8, 40.6),
         (-75.2, 41.6), (-74.0, 42.6)]
NS_ROUTE = ["detroit", "cincinnati", "lexington", "gap", "knoxville", "atlanta", "daytona"]
DIXIE = ["detroit", "cincinnati", "lexington", "gap", "knoxville", "chattanooga", "atlanta", "jacksonville", "miami"]
OHIO_FL = ["columbus", "cincinnati", "lexington", "gap", "knoxville", "atlanta", "daytona"]
WROAD = ["gap", "pineville", "flat_lick", "hazel_patch", "rockcastle", "boonesborough"]
PARK = [(-83.735, 36.566), (-83.66, 36.588), (-83.55, 36.618), (-83.43, 36.651), (-83.40, 36.668), (-83.43, 36.683), (-83.55, 36.650),
        (-83.665, 36.620), (-83.745, 36.585)]


def loc_cam(t, e=0.0, n=0.0, z=0.7):
    lon, lat = enm(e, n)
    return (t, lon, lat, z)


# ------------------------------------------------------------------ the edit
def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bgimg, badge="PREGUNTA 1"):
        add(t0, kb(bgimg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Por qué un país que vive de sus carreteras borró del mapa una por la que pasaban miles de autos cada día?",
                     ("borró",), size=64), tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 58.88)
    add(0.0, kb("u_4pdM_wHnYzw.jpg", "in", "cold"), [Badge("CUMBERLAND GAP", 0.4, 2.4)], tex=CLEAN)
    t_ky = w("kentucky", 3.6)
    add(t_ky - 0.9, mp("cg_loc", [loc_cam(0, 0, 300, 0.9), loc_cam(4.6, 0, 0, 1.15)],
                       BORDERS + [dict(STATES3[0], t0=0.9), dict(STATES3[1], t0=w("virginia", 4.4) - t_ky + 0.9),
                                  dict(STATES3[2], t0=w("tennessee", 5.0) - t_ky + 0.9),
                                  dict(type="pin", at="gap", t0=w("cumberland", 6.0) - t_ky + 0.9, label="CUMBERLAND GAP", side="r", box=True, size=46)]),
        tr="zoom", td=0.35, tex=GFX)
    add(7.32, kb("u_CoD2Q92UaEg.jpg", "in", "warm"), tr="fade", td=0.3, tex=CLEAN)
    add(w("pajaros", 9.6) - 0.3, kb("u_c-_yEpa4lpc.jpg", "in", "warm"), tex=CLEAN)
    add(11.04, kb("u_rgZMErtznRc.jpg", "down", "doc"), tex=CLEAN)
    t_dentro = w("dentro", 12.6)
    add(t_dentro - 0.2, kb("f_34833834135.jpg", "in", "doc"),
        [Counter(0, 30000, "+{:,.0f}", "VEHÍCULOS CADA DÍA", w("30", 14.4) - t_dentro, 1.2, (0.5, 0.42), 170)], tr="zoom", td=0.3, tex=CLEAN)
    add(16.7, kb("u_2JLN11-aHmM.jpg", "in", "warm"), tr="fade", td=0.4, tex=CLEAN)
    add(18.98, kb("f_4987674424.jpg", "punch", "faded"), [Badge("HACE NO TANTO", 0.2, None)], tr="glitch", td=0.3, tex=ARCH, post=postshake(2))
    add(21.74, mp("cg_loc", [loc_cam(0, -130, 200, 1.45), loc_cam(4.5, -130, 200, 1.6)],
                  BORDERS + [dict(type="route", path=OLD_25E, t0=0.3, draw=3.0, color=YELLOW, width=7),
                             dict(type="label", at=at(700, 1300), text="US-25E", t0=1.0, size=60, box=True),
                             dict(type="label", at=at(-900, 300), text="CURVAS CERRADAS", t0=w("curvas", 25.2) - 21.74, size=50)]),
        tr="fade", td=0.3, tex=GFX)
    add(26.22, mp("cg_east", [(0, -83.5, 36.0, 0.8), (4.2, -83.5, 36.0, 0.85)],
                  [dict(type="route", path=NS_ROUTE, t0=0.2, draw=2.0, color=YELLOW, width=6, traffic=14, speed=120),
                   dict(type="label", at=(-84.6, 41.3), text="MEDIO OESTE", t0=0.6, size=52),
                   dict(type="label", at=(-83.4, 31.6), text="EL SUR", t0=w("sur", 29.2) - 26.22, size=52),
                   dict(type="pin", at="gap", t0=1.2, color=RED)]), tr="zoom", td=0.35, tex=GFX)
    t_mm = w("massacre", 32.0)
    add(30.42, kb("u_q_Hl2VNxERE.jpg", "punch", "night"),
        [Darken(0.35), BigText("MASSACRE MOUNTAIN", "serif", 110, WHITE, (0.5, 0.45), t_mm - 30.42, None, "pop"),
         BigText("«LA MONTAÑA DE LA MASACRE»", "bebas", 50, RED, (0.5, 0.58), t_mm - 30.42 + 1.2, None, "up", tracking=6)],
        tr="flash", td=0.25, tex=DARK, post=postshake(3))
    add(35.28, kb("l_63991.jpg", "in", "doc"), [big("HOY NO QUEDA NI RASTRO", 0.4)], tr="fade", td=0.4, tex=CLEAN)
    add(37.64, kb("u_h1lF_j0fZdo.jpg", "in", "cold"), [rich("LAS CARRETERAS SUELEN MORIR DE OLVIDO", ("olvido",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(41.02, kb("u_V72VFoZ4LIk.jpg", "punch", "doc"), [Stamp("A PROPÓSITO", w("proposito", 41.9) - 41.02, RED, (0.5, 0.5), -8, 120)],
        tr="whip_l", td=0.25, tex=CLEAN, post=postshake(3))
    add(43.02, kb("u_jYA6yTcqI0k.jpg", "in", "dark"), [Darken(0.5), big("DOS COSAS NO CUADRAN", 0.2, 0.5, 96, YELLOW, "pop")], tr="fade", td=0.3, tex=DARK)
    q1(45.48, "u_IYAvTCJ4-AY.jpg")
    add(51.52, kb("u_di4pFRL4SkI.jpg", "in", "dark"), [Darken(0.55), Badge("PREGUNTA 2", 0.2, None)] +
        question("¿Y por qué, si aquella carretera se cobraba vidas cada año, tardaron décadas en quitarla?", ("décadas",), size=64),
        tr="glitch", td=0.3, tex=DARK)

    # ============================== CAP 1: LA PUERTA DEL OESTE (58.88 - 251)
    add(58.88, kb("l_63989.jpg", "in", "doc"),
        [Darken(0.45, 0.0, 0.3), BigText("CUMBERLAND GAP", "bebas", 190, YELLOW, (0.5, 0.40), 0.1, None, "pop", tracking=10),
         BigText("La carretera que borraron a propósito", "serif_it", 64, WHITE, (0.5, 0.58), 0.45, None, "up"),
         Badge("CAPÍTULO 1 · LA PUERTA DEL OESTE", 1.2, None)], tr="flash", td=0.25, tex=CLEAN)
    add(w("clave", 62.6) - 0.4, kb("f_8735585048.jpg", "in", "faded"),
        [Caption("Postal de la US-25E, Middlesboro (Kentucky)" if have("f_8735585048.jpg") else "Middlesboro, Kentucky (1935)", None, 0.3)], tex=ARCH)
    add(65.66, kb("l_3b00607.jpg", "in", "archival"), [rich("NO ERA UNA MONTAÑA CUALQUIERA", ("cualquiera",), 0.3, y=0.86, size=52)], tex=ARCH)
    add(68.08, kb("f_6350137195.jpg", "l", "warm"), [big("DEBAJO HABÍA OTRO CAMINO", 0.6)], tex=CLEAN)
    t_mapa = 71.14
    add(t_mapa, mp("cg_east", [(0, -82.0, 36.0, 0.76), (12.0, -82.5, 36.3, 0.95)],
                   [dict(type="label", at=(-72.5, 33.5), text="ATLÁNTICO", t0=w("costa", 75.8) - t_mapa, size=56, color=(140, 180, 220)),
                    dict(type="label", at=(-91.8, 33.4), text="MISSISSIPPI", t0=w("mississippi", 77.0) - t_mapa, size=56, color=(140, 180, 220)),
                    dict(type="band", path=APPAL, t0=w("muralla", 77.6) - t_mapa, draw=1.4, width=60, alpha=0.38),
                    dict(type="label", at=(-79.0, 37.2), text="LOS APALACHES", t0=w("apalaches", 79.3) - t_mapa, size=66, box=True)]),
        tr="fade", td=0.4, tex=GFX)
    add(83.2, cus(G4.ridge_front, mode="notch", title="UNA MUESCA", sub=None), tr="zoom", td=0.35, tex=GFX)
    t_1631 = w("1631", 89.6)
    add(87.14, kb("l_63990.jpg", "r", "doc"), [LowerThird("CUMBERLAND MOUNTAINS", "Un paso natural en la muralla", 0.3),
                                              Counter(0, 1631, "{:,.0f} PIES", "≈ 500 METROS", t_1631 - 87.14, 1.0, (0.5, 0.4), 150)], tex=CLEAN)
    add(93.78, mp("cg_loc", [loc_cam(0, 0, 0, 0.9), loc_cam(3.0, 0, 0, 1.4)],
                  [dict(type="pin", at="gap", t0=0.3, label="CUMBERLAND GAP", side="r", box=True, size=50)]), tr="zoom", td=0.3, tex=GFX)
    t_mucho = w("mucho", 96.2)
    add(t_mucho, kb("u_FaqgDW9n9FA.jpg", "in", "warm"), [Badge("MUCHO ANTES DE LOS EUROPEOS", 0.2, None)], tr="fade", td=0.3, tex=CLEAN)
    add(w("gente", 101.0) - 0.3, kb("u_AjyF1e_AGmc.jpg", "in", "doc"), tex=CLEAN)
    add(102.7, Split([kb("l_07521.jpg", "in", "archival", cam0=(0.5, 0.4, 1.0), cam1=(0.5, 0.38, 1.08)), kb("l_07579.jpg", "in", "archival", cam0=(0.5, 0.3, 1.0), cam1=(0.5, 0.28, 1.08))], labels=["SHAWNEE", "CHEROKEE"]),
        [Badge("RETRATOS DE MCKENNEY & HALL · 1830s", 0.3, None)], tr="whip_r", td=0.3, tex=ARCH)
    add(107.62, cus(G4.ridge_front, mode="warpath"), tr="fade", td=0.3, tex=GFX)
    add(113.1, kb("u_nCHP8xRf5Xw.jpg", "in", "warm"), [Badge("13 DE ABRIL DE 1750", 0.4, None)], tex=CLEAN)
    add(119.26, kb("u_xzY5RQDrlw4.jpg", "in", "doc"), [LowerThird("THOMAS WALKER", "Médico y explorador de Virginia", 0.3)], tex=CLEAN)
    add(123.56, kb("f_50217966033.jpg", "in", "doc"), [Badge("UNA CUEVA CON UN MANANTIAL", 0.3, None)], tex=CLEAN)
    t_cave = w("cave", 128.6)
    add(t_cave - 0.4, kb("u_-fKYil98I8E.jpg", "in", "cold"),
        [Darken(0.3), BigText("CAVE GAP", "bebas", 150, WHITE, (0.5, 0.45), 0.3, None, "pop", tracking=10),
         BigText("«EL PASO DE LA CUEVA»", "serif_it", 56, YELLOW, (0.5, 0.6), 1.0, None, "up")], tex=CLEAN)
    add(131.16, kb("u_k-Pz80yzt7c.jpg", "in", "doc"), [rich("NO ERA UN HALLAZGO NUEVO", ("nuevo",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(133.36, kb("u_sNosbWsH9wE.jpg", "in", "cold"),
        [Counter(0, 15000, "{:,.0f}", "AÑOS CRUZANDO POR AQUÍ", w("15", 135.4) - 133.36, 1.2, (0.5, 0.45), 200)], tex=CLEAN)
    t_ath = w("hathiamiowie", 140.8)
    add(137.48, kb("u_bmRp98_vsrQ.jpg", "in", "doc"),
        [BigText("ATHIAMIOWEE", "serif", 110, WHITE, (0.5, 0.48), t_ath - 137.48, None, "pop"),
         BigText("NOMBRE SHAWNEE DEL SENDERO", "bebas", 46, YELLOW, (0.5, 0.6), t_ath - 137.48 + 0.6, None, "up", tracking=6)], tex=CLEAN)
    add(142.9, kb("u_HA0Rgl-ISko.jpg", "in", "sepia"), [rich("EN LOS PAPELES DE LOS COLONOS", ("papeles",), 0.3, y=0.84, size=54)], tex=ARCH)
    add(w("cambio", 146.9) - 0.6, fr("l_3b08248.jpg"), tex=ARCH)
    add(148.94, kb("l_3a51182.jpg", "in", "archival", z=1.05), [Caption("George Caleb Bingham, «Daniel Boone escolta a los colonos a través del Cumberland Gap» (1851-52)", None, 0.4)],
        tr="fade", td=0.4, tex=ARCH)
    add(152.06, kb("l_3c12549.jpg", "in", "archival"), [LowerThird("DANIEL BOONE", "1734 – 1820", 0.3), Badge("1775", 0.2, None)], tex=ARCH)
    add(w("hacha", 157.0) - 0.6, kb("u_Yz6dxnW6-gw.jpg", "punch", "doc"), [big("A GOLPE DE HACHA", 0.3)], tex=CLEAN, post=postshake(3))
    t_200 = w("200", 160.0)
    add(159.38, mp("cg_reg", [(0, -84.0, 37.25, 1.0), (6.0, -84.0, 37.25, 1.08)],
                   [dict(type="pin", at="gap", t0=0.0, label="CUMBERLAND GAP", side="r"),
                    dict(type="route", path=WROAD, t0=0.2, draw=3.4, color=DIRT, width=7, dash=22),
                    dict(type="label", at=(-83.62, 37.35), text="≈ 200 MILLAS · 320 KM", t0=t_200 - 159.38 + 0.4, size=52, box=True),
                    dict(type="pin", at="boonesborough", t0=3.6, label="CORAZÓN DE KENTUCKY", side="r")]), tr="zoom", td=0.35, tex=GFX)
    add(165.68, kb("l_4a13858.jpg", "in", "archival"),
        [BigText("WILDERNESS ROAD", "bebas", 130, WHITE, (0.5, 0.44), 0.3, None, "pop", tracking=8),
         BigText("«el camino de la tierra salvaje»", "serif_it", 56, YELLOW, (0.5, 0.58), 1.0, None, "up")], tex=ARCH)
    add(170.78, kb("f_22936253412.jpg", "in", "warm"), [rich("AL PRINCIPIO, POCO MÁS QUE UNA VEREDA", ("vereda",), 0.2, y=0.84, size=52)], tex=CLEAN)
    add(w("carretas", 175.2) - 1.2, vid("american_pioneer", 330.0, 3.5, "bw"), [Badge("1796 · CARRETAS", 0.2, None)], tex=FILM)
    add(176.9, vid("american_pioneer", 380.0, 6.8, "bw"),
        [BigText("200.000 – 300.000", "bebas", 150, YELLOW, (0.5, 0.42), w("200", 179.8) - 176.9, None, "pop", tracking=4),
         BigText("PERSONAS ANTES DE 1810", "bebas", 56, WHITE, (0.5, 0.56), w("200", 179.8) - 176.9 + 0.6, None, "up", tracking=6)], tex=FILM)
    add(183.66, kb("f_6350100983.jpg", "in", "warm"), [rich("FAMILIAS ENTERAS", ("familias",), 0.2, y=0.84, size=60)], tex=CLEAN)
    add(w("buscando", 186.4) - 0.2, kb("f_6350857048.jpg", "l", "warm"), [rich("TIERRA PROPIA AL OTRO LADO", ("propia",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(189.7, vid("american_pioneer", 432.0, 2.2, "bw"), tex=FILM)
    add(191.9, kb("l_02659.jpg", "in", "archival"), [rich("ERA SU TIERRA", ("su",), 0.6, y=0.86, size=60)], tex=ARCH)
    add(w("emboscadas", 196.3) - 0.5, kb("l_3b08533.jpg", "punch", "archival"), [big("EMBOSCADAS Y VENGANZAS", 0.4, 0.86, 60, RED)], tex=ARCH, post=postshake(2))
    t_1784 = 199.5
    add(t_1784, kb("u_9evooDnb_mA.jpg", "in", "bw"),
        [Darken(0.35), Badge("1784 · FUENTE: FHWA", 0.2, None),
         Counter(0, 100, "+{:.0f}", "VIAJEROS MUERTOS EN EL LADO DE KENTUCKY", w("100", 203.6) - t_1784, 1.0, (0.5, 0.45), 230)], tex=ARCH)
    add(206.3, fr("l_3a37699.jpg"), [rich("BOONE LO SABÍA MEJOR QUE NADIE", ("boone",), 0.1, y=0.88, size=50)], tex=ARCH)
    add(208.0, vid("kentucky_pioneers", 59.3, 5.2, "bw"), [Badge("1773", 0.3, None)], tex=FILM)
    add(213.34, kb("f_6350142987.jpg", "in", "warm"), [rich("SU FAMILIA Y VARIAS MÁS", ("familia",), 0.2, y=0.84, size=54)], tex=CLEAN)
    add(218.36, mp("cg_reg", [(0, -83.3, 36.72, 1.2), (4.5, -83.3, 36.7, 1.4)],
                   [dict(type="pin", at="gap", t0=0.0, label="CUMBERLAND GAP", side="b"),
                    dict(type="pin", at="powell_valley", t0=0.3, label="POWELL VALLEY", side="t", color=RED, box=True)]), tr="zoom", td=0.3, tex=GFX)
    add(w("emboscada", 226.8) - 0.6, kb("l_07745.jpg", "punch", "archival"), [Flash(0.0, 0.15)], tr="flash", td=0.2, tex=ARCH, post=postshake(4))
    add(229.46, kb("u_-YiJvbfNDqk.jpg", "in", "dark"),
        [Darken(0.45), BigText("JAMES BOONE", "serif", 110, WHITE, (0.5, 0.45), w("james", 231.0) - 229.46, None, "up"),
         BigText("16 AÑOS", "bebas", 64, YELLOW, (0.5, 0.58), w("16", 232.0) - 229.46, None, "up", tracking=8)], tr="fade", td=0.5, tex=DARK)
    add(w("media", 234.0) - 0.4, kb("u_9evooDnb_mA.jpg", "out", "bw"), tex=ARCH)
    add(w("despues", 235.6) - 0.3, kb("l_11174.jpg", "in", "archival"), [rich("VOLVIÓ CON EL HACHA EN LA MANO", ("hacha",), 0.8, y=0.88, size=52)], tex=ARCH)
    add(w("tampoco", 240.4) - 0.2, vid("american_pioneer", 358.0, 2.0, "bw"), tex=FILM)
    add(w("carretas", 243.3) - 0.3, Split([kb("u_I2iUaroWHbc.jpg", "in", "bw"), kb("l_31467.jpg", "in", "archival")], labels=["CARRETAS", "PRIMEROS AUTOS"]),
        [big("MÁS DE UN SIGLO", 1.6, 0.1, 64, YELLOW)], tr="whip_l", td=0.3, tex=ARCH)
    add(w("cumberland", 248.0) - 0.4, kb("l_07660.jpg", "in", "archival"), [rich("DE TODO MENOS CALMA", ("calma",), 0.6, y=0.88, size=60)], tex=ARCH)

    # ============================== CAP 2: DE VEREDA A CARRETERA (251 - 379.6)
    t_c2 = w("primero", 251.4) - 0.1
    bg, ov = chapter(2, "De vereda a carretera", "l_3b07606.jpg", "archival", "1863–1926")
    add(t_c2, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(w("durante", 253.4) - 0.1, kb("l_03976.jpg", "in", "archival"), [Badge("GUERRA CIVIL · 1861–1865", 0.2, None)], tex=ARCH)
    t_tres = w("tres", 258.6)
    add(256.7, kb("l_3a50539.jpg", "r", "archival"),
        [Counter(0, 3, "{:.0f}", "VECES CAMBIÓ DE MANOS", t_tres - 256.7, 0.6, (0.5, 0.42), 240, sub="EN UNOS 16 MESES")], tex=ARCH)
    add(261.42, kb("u_vkAPZtoMdrI.jpg", "in", "bw"), [Badge("SEPTIEMBRE DE 1863", 0.2, None),
                                                     Counter(0, 2300, "{:,.0f}", "CONFEDERADOS SE RINDEN", w("rendirse", 265.9) - 261.42, 1.0, (0.5, 0.45), 190)], tex=ARCH)
    add(w("paso", 269.6) - 0.3, kb("f_29304863863.jpg", "in", "bw"), [rich("YA NO VOLVIÓ A CAMBIAR DE DUEÑO", ("dueño",), 0.3, y=0.86, size=52)], tex=ARCH)
    add(w("soldado", 272.0) - 0.2, kb("l_23672.jpg", "in", "archival"),
        [Caption("«Los árboles que cubrían las montañas han caído todos»", "Un soldado de Ohio, 1863", 0.6)], tex=ARCH)
    add(w("caido", 279.0) - 1.6, kb("l_23673.jpg", "l", "archival"), tex=ARCH)
    add(w("cueva", 281.0) - 0.3, kb("f_54659201921.jpg", "in", "bw"), [Badge("LA CUEVA: HOSPITAL IMPROVISADO", 0.3, None)], tex=ARCH)
    add(w("todavia", 284.0) - 0.2, kb("u_IafBotza6JA.jpg", "in", "warm"), [rich("NOMBRES ESCRITOS CON HOLLÍN DE ANTORCHAS", ("hollín",), 1.0, y=0.84, size=50)], tex=CLEAN)
    t_prog = w("progreso", 291.0) - 0.9
    add(t_prog, vid("33-169", 66.0, 2.6, "bw"), [big("EL PROGRESO", 0.3, 0.84, 76, YELLOW, "pop")], tr="flash", td=0.2, tex=FILM)
    add(w("middlesboro", 293.6) - 0.6, mp("cg_loc", [loc_cam(0, -2000, 300, 0.9), loc_cam(3.4, -2000, 300, 1.0)],
                                          [dict(type="pin", at="middlesboro", t0=0.4, label="MIDDLESBORO", side="r", box=True, size=50),
                                           dict(type="pin", at="gap", t0=1.0, label="EL PASO", side="r", color=WHITE, pulse=False)]), tex=GFX)
    add(w("pueblo", 296.8) - 0.4, kb("l_3c21535.jpg", "in", "archival"), [Badge("MIDDLESBORO · 1890", 0.2, None)], tex=ARCH)
    add(w("carbon", 298.6) - 0.4, kb("u_KksaprMndok.jpg", "in", "bw"), [big("MINAS DE CARBÓN", 0.2)], tex=ARCH)
    add(w("rincon", 300.4) - 0.3, vid("33-169", 325.0, 4.6, "bw"), [Badge("1908 · UN ESCAPARATE FEDERAL", 0.3, None)], tex=FILM)
    add(w("muestra", 305.6) - 0.6, vid("33-169", 428.0, 4.0, "bw"), [rich("PIEDRA TRITURADA Y COMPACTADA", ("triturada",), 0.4, y=0.86, size=54)], tex=FILM)
    t_dos = w("dos", 309.6)
    add(t_dos - 0.3, mp("cg_loc", [loc_cam(0, -1550, -280, 0.95), loc_cam(5.8, -1550, -280, 1.05)],
                        BORDERS + [dict(type="pin", at="middlesboro", t0=0.0, label="MIDDLESBORO", side="l", pulse=False),
                                   dict(type="route", path=["middlesboro", at(-200, 1700)] + OLD_25E[1:], t0=0.3, draw=3.0, color=YELLOW, width=7),
                                   dict(type="pin", at="cg_town", t0=3.0, label="CUMBERLAND GAP (TN)", side="r", pulse=False),
                                   dict(type="label", at=enm(-1700, 900), text="≈ 2,5 MILLAS", t0=1.6, size=56, box=True)]), tr="fade", td=0.3, tex=GFX)
    add(315.4, vid("33-266", 180.0, 4.2, "bw"), [rich("ASÍ DEBÍA SER UN CAMINO MODERNO", ("moderno",), 0.3, y=0.86, size=52)], tex=FILM)
    t_1916 = 319.6
    add(t_1916, mp("cg_east", [(0, -84.0, 35.5, 0.78), (8.0, -84.0, 35.6, 0.82)],
                   [dict(type="route", path=DIXIE, t0=w("dixie", 325.2) - t_1916, draw=2.0, color=YELLOW, width=6),
                    dict(type="pin", at="gap", t0=0.2, color=RED, label="CUMBERLAND GAP", side="r"),
                    dict(type="label", at=(-87.2, 33.0), text="DIXIE HIGHWAY", t0=w("dixie", 325.2) - t_1916 + 0.6, size=60, box=True)]),
        [Badge("1916", 0.2, None)], tr="zoom", td=0.3, tex=GFX)
    t_1926 = w("1926", 328.4)
    add(t_1926 - 0.4, kb("f_8735585216.jpg", "in", "faded"), [Badge("1926 · NUMERACIÓN FEDERAL", 0.2, None),
                                                             BigText("US-25E", "bebas", 150, YELLOW, (0.5, 0.45), w("25e", 334.6) - t_1926 + 0.4, None, "pop", tracking=10)],
        tex=ARCH)
    add(w("problema", 335.6) - 0.2, kb("u_aNglGVT07Ms.jpg", "in", "bw"), [rich("PARA METER LA CARRETERA POR EL PASO…", ("paso…",), 0.3, y=0.86, size=52)], tex=ARCH)
    add(w("quitaron", 340.8) - 0.6, cus(G4.ridge_front, mode="cut"), tr="zoom", td=0.3, tex=GFX)
    add(w("muesca", 347.6) - 0.6, kb("l_3b00607.jpg", "out", "archival"), [rich("YA NO ERA LA MISMA", ("misma",), 0.6, y=0.88, size=60)], tex=ARCH)
    add(w("asfalto", 350.6) - 0.3, kb("u_culd5miA7UA.jpg", "in", "doc"), [big("CURVAS CERRADAS", 0.4)], tex=CLEAN)
    add(w("viejo", 353.4) - 0.3, cus(G4.pass_section, mode="layers"), tr="fade", td=0.3, tex=GFX)
    add(w("abajo", 361.8) - 0.2, vid("american_pioneer", 300.0, 3.2, "bw"), [Badge("ABAJO: LOS PIONEROS", 0.2, None)], tex=FILM)
    add(w("arriba", 365.2) - 0.2, vid("33-266", 150.0, 2.4, "bw"), [Badge("ARRIBA: LOS AUTOS", 0.2, None)], tex=FILM)
    add(w("tarde", 367.5) - 0.2, Split([kb("f_6350079043.jpg", "in", "warm"), kb("u_U4rFbH_XUlY.jpg", "in", "faded")], vs=True),
        [big("UNO DE LOS DOS IBA A SOBRAR", 0.6, 0.86, 60, YELLOW)], tex=CLEAN)
    add(w("durante", 370.4) - 0.2, vid("fc-fc-3139", 108.0, 4.6, "bw"), [Badge("TRÁFICO DE PRINCIPIOS DE SIGLO", 0.3, None)], tex=FILM)
    add(w("vino", 376.6) - 1.0, kb("u_1jtExSGqIOE.jpg", "in", "doc"), tr="whip_l", td=0.25, tex=CLEAN)

    # ============================== CAP 3: MASSACRE MOUNTAIN (379.6 - 502.6)
    t_c3 = w("con", 379.6) - 0.1
    bg, ov = chapter(3, "Massacre Mountain", "u_IYAvTCJ4-AY.jpg", "dark")
    add(t_c3, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(w("llegaron", 381.4) - 0.2, kb("u_PN-m8hQi4fI.jpg", "in", "night"),
        [Counter(0, 18000, "{:,.0f}", "VEHÍCULOS AL DÍA", w("18", 383.4) - w("llegaron", 381.4) + 0.2, 1.2, (0.5, 0.42), 190)], tex=DARK)
    add(w("autos", 387.3) - 0.1, kb("u_U4rFbH_XUlY.jpg", "in", "warm"), [Badge("FAMILIAS DE VACACIONES", 0.2, None)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("camionetas", 389.6) - 0.1, kb("u_7E0MMarta-U.jpg", "in", "doc"), [Badge("CAMIONETAS DE TRABAJO", 0.2, None)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("traileres", 391.4) - 0.2, kb("u_P0bVatS8Jdw.jpg", "in", "cold"), [Badge("Y SOBRE TODO, TRÁILERES", 0.2, None)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("todos", 394.2) - 0.2, mp("cg_loc", [loc_cam(0, -130, 200, 1.5), loc_cam(5.6, -130, 200, 1.6)],
                                    BORDERS + [dict(type="route", path=OLD_25E, t0=0.0, draw=0.8, color=YELLOW, width=7, traffic=14, speed=90),
                                               dict(type="label", at=at(-1100, 900), text="2 CARRILES", t0=w("carriles", 396.0) - w("todos", 394.2) + 0.2, size=52, box=True),
                                               dict(type="label", at=at(900, 350), text="≈ 10 CURVAS CERRADAS", t0=w("decena", 397.8) - w("todos", 394.2) + 0.2, size=52, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(w("ahora", 399.9) - 0.1, kb("u_lz0guF9OVxU.jpg", "in", "night"), [rich("PONTE EN LA CABINA", ("cabina",), 0.3, y=0.84, size=58)], tex=DARK)
    add(w("cada", 405.3) - 0.1, kb("u_al01Ad0f_KI.jpg", "punch", "night"), [FnOverlay(G4.brake_heat, t0=0.4, steps=7, every=0.8)], tex=DARK)
    add(w("delante", 411.6) - 0.2, kb("u_fGkuoKmahDo.jpg", "in", "cold"), [rich("UN AUTO LENTO ENTRE LA NIEBLA", ("niebla",), 0.4, y=0.84, size=54)], tex=CLEAN)
    add(w("detras", 415.5) - 0.2, kb("u_FW8HAgggcJ8.jpg", "in", "night"), [rich("DETRÁS, UNA FILA QUE CRECE", ("crece",), 0.2, y=0.84, size=54)], tex=DARK)
    add(w("carril", 418.4) - 0.3, kb("u_vAKOBXeA6_8.jpg", "punch", "night"), [Flash(w("adelanta", 421.6) - w("carril", 418.4) + 0.3, 0.2)],
        tex=DARK, post=postshake(4))
    add(w("ahi", 423.6) - 0.1, kb("u_Wa7n0RT3I_8.jpg", "in", "dark"), [rich("AHÍ ARRIBA SE JUNTABA TODO LO MALO", ("malo",), 0.2, y=0.84, size=52)], tex=DARK)
    add(w("niebla", 426.2) - 0.1, kb("u_fV5RjTaKH4o.jpg", "in", "cold"), [big("NIEBLA", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("hielo", 428.8) - 0.1, kb("u_RamrxiQPxJE.jpg", "in", "cold"), [big("HIELO", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("filas", 430.6) - 0.1, kb("u_BqQDTFTveOQ.jpg", "in", "doc"), [big("FILAS", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("prisa", 433.8) - 0.6, kb("u_s4hSyBXDAgI.jpg", "in", "night"), [big("PRISA", 0.1, 0.84, 80, RED)], tr="whip_l", td=0.2, tex=DARK)
    add(w("eso", 435.2) - 0.1, kb("u_WM5WRBl-EZ8.jpg", "in", "dark"), [Darken(0.4), big("ESO TENÍA UN PRECIO", 0.2, 0.5, 90, WHITE, "pop")], tr="black", td=0.3, tex=DARK)
    t_5 = w("cinco", 440.6)
    add(w("segun", 437.0) - 0.1, kb("u_YH1KID3mTpY.jpg", "in", "dark"),
        [Darken(0.45), Badge("FUENTE: ADMINISTRACIÓN FEDERAL DE CARRETERAS", 0.2, None),
         Counter(0, 5, "≈ {:.0f}", "MUERTES AL AÑO", t_5 - w("segun", 437.0) + 0.1, 0.8, (0.5, 0.45), 240)], tex=DARK)
    add(w("otras", 442.6) - 0.1, kb("u_q_Hl2VNxERE.jpg", "in", "dark"), [rich("OTRAS CRÓNICAS: MÁS DE MEDIA DOCENA", ("docena",), 0.3, y=0.84, size=54)], tex=DARK)
    add(w("por", 445.6) - 0.2, mp("cg_loc", [loc_cam(0, -130, 200, 1.5), loc_cam(3.6, -130, 200, 1.6)],
                                  BORDERS + [dict(type="route", path=OLD_25E, t0=0.0, draw=0.6, color=RED, width=9)]),
        [BigText("MASSACRE MOUNTAIN", "serif", 96, WHITE, (0.5, 0.16), w("massacre", 447.4) - w("por", 445.6) + 0.2, None, "pop")], tex=GFX)
    add(449.06, kb("u_owSUPshiaAc.jpg", "in", "night"), [rich("UN AUTO QUE NO LLEGÓ A CASA", ("casa",), 0.8, y=0.84, size=56)], tr="fade", td=0.4, tex=DARK)
    t_ej = w("ejemplo", 454.0) - 0.2
    add(t_ej, mp("cg_east", [(0, -83.0, 35.0, 0.8), (5.0, -83.0, 35.0, 0.84)],
                 [dict(type="route", path=OHIO_FL, t0=0.3, draw=3.0, color=YELLOW, width=6),
                  dict(type="pin", at="columbus", t0=0.2, label="OHIO", side="r"),
                  dict(type="pin", at="daytona", t0=w("florida", 456.6) - t_ej, label="PLAYAS DE FLORIDA", side="r")]),
        [Badge("UN EJEMPLO", 0.2, None)], tr="zoom", td=0.3, tex=GFX)
    add(w("ninos", 459.4) - 0.2, kb("u_INvrDywsRmo.jpg", "in", "warm"), tex=CLEAN)
    add(w("carro", 461.4) - 0.2, kb("u_bjELEEMf8pU.jpg", "in", "warm"), tex=CLEAN)
    add(w("media", 463.4) - 0.1, kb("u_F3edSiwSJkw.jpg", "punch", "doc"), [rich("LA CURVA SE CIERRA MÁS DE LO ESPERADO", ("cierra",), 0.4, y=0.86, size=52)], tex=CLEAN)
    add(w("frente", 467.0) - 0.2, kb("u_lz0guF9OVxU.jpg", "punch", "night"), [Flash(1.2, 0.25, (255, 255, 255), 0.9)], tex=DARK, post=postshake(6))
    add(w("son", 470.6) - 0.1, Solid("black"), [BigText("DOS SEGUNDOS", "serif", 120, WHITE, (0.5, 0.5), 0.15, None, "pop")], tex=DARK)
    add(w("pueblos", 473.4) - 0.5, kb("l_8a16680.jpg", "in", "bw"), [Caption("Middlesboro, Kentucky (1935)", None, 0.3)], tex=ARCH)
    add(w("familia", 476.0) - 0.4, kb("f_3907232380.jpg", "in", "faded"), tex=ARCH)
    add(w("cruzar", 480.8) - 1.0, kb("u_jYA6yTcqI0k.jpg", "in", "cold"), [rich("YA NO VOLVÍA A CRUZAR SIN ACORDARSE", ("acordarse",), 0.4, y=0.84, size=52)], tex=CLEAN)
    add(w("anos", 484.6) - 0.6, vid("safety_through_seat_belts", 200.0, 4.0, "faded"), [Badge("AÑOS 60 · MEJORAS DE SEGURIDAD", 0.2, None),
                                                                                     Stamp("NO BASTARON", w("bastaron", 487.4) - w("anos", 484.6) + 0.6, RED, (0.5, 0.5), -8, 100)],
        tex=FILM)
    add(w("solucion", 489.2) - 0.2, kb("u_EPHB1FqN_ns.jpg", "in", "doc"), [big("¿CUATRO CARRILES?", w("cuatro", 491.0) - w("solucion", 489.2), 0.84, 84, YELLOW, "pop")], tex=CLEAN)
    add(w("aqui", 492.6) - 0.2, mp("cg_loc", [loc_cam(0, -130, 200, 1.4), loc_cam(3.0, -130, 200, 1.45)],
                                   BORDERS + [dict(type="route", path=OLD_25E, t0=0.0, draw=0.4, color=YELLOW, width=7)]),
        [Stamp("NO", 0.3, RED, (0.5, 0.5), -10, 200)], tex=GFX)
    add(w("porque", 496.4) - 0.1, kb("l_63992.jpg", "in", "doc"), [rich("YA NO ERA SOLO UNA MONTAÑA", ("montaña",), 0.4, y=0.84, size=54)], tex=CLEAN)
    add(w("parque", 501.6) - 0.6, kb("l_404582c.jpg", "in", "doc"), [big("ERA UN PARQUE NACIONAL", 0.3, 0.84, 70, YELLOW, "pop")], tex=CLEAN)

    # ============================== CAP 4: CONDENADA DESDE 1940 (502.6 - 654.9)
    t_c4 = w("no", 503.2) - 0.4
    bg, ov = chapter(4, "Condenada desde 1940", "l_63990.jpg", "dark")
    add(t_c4, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(w("1940", 505.6) - 0.2, kb("u_E94nZORR5qc.jpg", "in", "doc"), [Badge("1940 · EL CONGRESO", 0.2, None)], tex=CLEAN)
    t_park = w("cumberland", 509.6) - 0.3
    add(t_park, mp("cg_mid", [(0, -83.57, 36.63, 1.0), (12.6, -83.57, 36.63, 1.1)],
                   [dict(type="poly", pts=PARK, t0=0.3, alpha=0.45),
                    dict(type="label", at=(-83.58, 36.71), text="CUMBERLAND GAP NATIONAL HISTORICAL PARK", t0=0.6, size=46, box=True),
                    dict(type="pin", at="gap", t0=0.0, pulse=False, color=WHITE),
                    dict(type="label", at=(-83.78, 36.66), text="KENTUCKY", t0=w("tres", 516.4) - t_park, size=48),
                    dict(type="label", at=(-83.40, 36.60), text="VIRGINIA", t0=w("tres", 516.4) - t_park + 0.2, size=48),
                    dict(type="label", at=(-83.64, 36.52), text="TENNESSEE", t0=w("tres", 516.4) - t_park + 0.4, size=48)]),
        [Counter(0, 20000, "{:,.0f} ACRES", "≈ 8.000 HECTÁREAS", w("20", 513.4) - t_park, 1.2, (0.5, 0.8), 110)], tr="zoom", td=0.3, tex=GFX)
    add(w("encargo", 521.0) - 1.6, kb("u_ds7E21WhTQ4.jpg", "in", "warm"), [rich("LO IMPORTANTE ERA EL ENCARGO", ("encargo",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("devolver", 526.6) - 0.6, cus(G3.document, lines=[("LEY DEL PARQUE · 1940", 54), ("", 20), ("ENCARGO:", 46), ("DEVOLVER EL PASO Y EL", 46),
                                                             ("WILDERNESS ROAD A SU", 46), ("ASPECTO DE 1780-1810", 46)], sign_t=5.0),
        tr="fade", td=0.3, tex=GFX)
    add(w("abrirlo", 535.0) - 0.1, kb("u_ITBuy3A4-bA.jpg", "in", "cold"), [TimelineBar(1940, 1959, 0.2, (0.3, 1.8), 1940)], tex=CLEAN)
    add(w("julio", 539.0) - 0.8, kb("u_xcTOlVY-4Xw.jpg", "in", "warm"), [Badge("4 DE JULIO DE 1959", 0.2, None)], tex=CLEAN)
    add(w("dedico", 543.0) - 0.4, kb("u_I306rDlvTYY.jpg", "in", "warm"), [rich("AUTORIDADES LLEGADAS DE WASHINGTON", ("washington",), 0.3, y=0.84, size=52)], tex=CLEAN)
    add(w("nixon", 548.6) - 1.4, kb("f_26975446814.jpg", "in", "faded"), [LowerThird("RICHARD NIXON", "Vicepresidente de EE. UU. (1953–1961)", 0.4)], tex=ARCH)
    add(w("escena", 549.4) - 0.3, kb("u_rAoQn6kwv64.jpg", "in", "warm"), [rich("LA ESCENA TENÍA SU IRONÍA", ("ironía",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("estrado", 552.6) - 0.6, kb("u_IkEpl3JkVqU.jpg", "in", "warm"), [Badge("EN EL ESTRADO: LOS PIONEROS", 0.2, None)], tex=CLEAN)
    add(w("seguian", 556.2) - 0.4, kb("u_7RnL30gvk34.jpg", "in", "cold"), [Badge("EN LA MONTAÑA: LOS CAMIONES DE LA US-25E", 0.2, None)], tex=CLEAN)
    t_mid = w("parque", 561.6) - 0.2
    add(t_mid, mp("cg_mid", [(0, -83.65, 36.63, 1.0), (5.6, -83.67, 36.63, 1.1)],
                  [dict(type="poly", pts=PARK, t0=0.0, alpha=0.45),
                   dict(type="road", name="25E", level="Federal", bbox=(-84.4, 36.25, -82.9, 37.05), t0=w("carretera", 565.4) - t_mid - 0.4, draw=1.0, color=RED, width=9),
                   dict(type="label", at=(-83.80, 36.70), text="US-25E", t0=w("carretera", 565.4) - t_mid + 0.4, size=56, box=True)]),
        [BigText("ATRAVESÁNDOLO POR LA MITAD", "bebas", 60, WHITE, (0.5, 0.88), w("mitad", 566.0) - t_mid, None, "up", tracking=4)], tr="fade", td=0.3, tex=GFX)
    add(w("piensalo", 567.4) - 0.1, kb("u_Wka1lmO_H38.jpg", "in", "dark"), [Darken(0.55), big("PIÉNSALO UN MOMENTO", 0.1, 0.5, 90, WHITE, "pop")], tex=DARK)
    add(w("1940", 569.6) - 0.3, vid("Knightso1938", 381.0, 5.5, "bw"), [Badge("1940", 0.2, None), rich("MILES DE AUTOS CADA DÍA", ("miles",), 0.8, y=0.86, size=54)], tex=FILM)
    add(w("gobierno", 575.6) - 0.3, cus(G3.document, lines=[("1940", 70), ("", 20), ("ESTA CARRETERA", 56), ("NO DEBE ESTAR AQUÍ", 56)], sign_t=3.4),
        [Caption("Recreación", None, 0.4, None, 0.95)], tr="fade", td=0.3, tex=GFX)
    add(w("parecia", 583.2) - 0.4, kb("u_WM5WRBl-EZ8.jpg", "in", "dark"), [Darken(0.3), rich("¿LA QUITARON POR PELIGROSA?", ("peligrosa?",), 0.3, y=0.5, size=72)], tex=DARK)
    add(w("realidad", 588.2) - 0.4, cus(G4.timeline, events=[(1940, "LA SENTENCIA", 0.4), (1959, "PARQUE ABIERTO", 1.6), (1965, "MÁS TRÁILERES", 2.4), (1975, "MÁS MUERTES", 3.0)],
                                       hi=1940, red=(1940,), title="LA SENTENCIA LLEGÓ PRIMERO"), tr="fade", td=0.3, tex=GFX)
    add(w("estorbaba", 594.6) - 0.6, kb("f_6350098587.jpg", "in", "warm"), [rich("SIMPLEMENTE ESTORBABA A LA HISTORIA", ("historia",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("ahora", 596.4) - 0.1, kb("u_ZUBQPscbYis.jpg", "in", "cold"), [rich("CUMPLIR LA SENTENCIA NO ERA NADA FÁCIL", ("fácil",), 0.6, y=0.84, size=52)], tex=CLEAN)
    t_rodeo = w("la", 600.3) - 0.1
    add(t_rodeo, mp("cg_reg", [(0, -84.0, 36.95, 0.9), (10.6, -83.9, 36.8, 1.0)],
                    [dict(type="road", name="25E", level="Federal", bbox=(-86.4, 35.4, -81.6, 38.6), t0=0.2, draw=1.6, color=YELLOW, width=8, traffic=20, speed=110),
                     dict(type="label", at=(-84.6, 37.75), text="NORTE", t0=w("norte", 603.4) - t_rodeo, size=52),
                     dict(type="label", at=(-83.4, 35.9), text="SUR", t0=w("sur", 604.4) - t_rodeo, size=52),
                     dict(type="pin", at="gap", t0=w("cerrar", 605.6) - t_rodeo, color=RED, label="¿CERRAR?", side="r", box=True),
                     dict(type="route", path=["pineville", (-84.4, 36.85), (-84.5, 36.3), "knoxville"], t0=w("rodeo", 609.4) - t_rodeo, draw=1.6,
                          color=RED, width=6, dash=20),
                     dict(type="label", at=(-84.95, 36.6), text="UN RODEO", t0=w("rodeo", 609.4) - t_rodeo + 0.8, size=52, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(w("1956", 612.6) - 0.6, kb("u_rvVhr2LngP4.jpg", "in", "warm"), [Badge("1956 · SERVICIO DE PARQUES NACIONALES", 0.2, None),
                                                                       rich("UNA IDEA QUE SONABA A LOCURA", ("locura",), 1.6, y=0.84, size=54)], tex=CLEAN)
    add(w("si", 618.8) - 0.2, cus(G4.pass_section, mode="idea"), tr="zoom", td=0.3, tex=GFX)
    add(w("durante", 624.6) - 0.1, kb("u_4JdvOwrVzfY.jpg", "in", "warm"), [Badge("ESTUDIOS · DÉCADA DE 1960", 0.2, None)], tex=CLEAN)
    add(w("ensanchar", 628.6) - 0.3, kb("l_63991.jpg", "out", "doc"), [rich("ENSANCHAR HABRÍA DESTROZADO LO QUE HABÍA QUE PROTEGER", ("destrozado",), 0.4, y=0.84, size=48, maxw=0.8)], tex=CLEAN)
    add(w("asi", 634.0) - 0.1, cus(G3.document, lines=[("LEY FEDERAL · 1973", 58), ("", 20), ("CONSTRUIR LOS TÚNELES", 52), ("BAJO CUMBERLAND GAP", 52)], sign_t=3.6),
        [Caption("Recreación", None, 0.4, None, 0.95)], tr="fade", td=0.3, tex=GFX)
    t_obj = w("uno", 640.6) - 0.2
    add(t_obj, cus(G3.stats_panel, items=[("1", "SEGURIDAD AL VOLANTE", 0.3), ("2", "EL ASPECTO HISTÓRICO", w("otro", 643.6) - t_obj)], title="LOS DOS OBJETIVOS"),
        [Stamp("EL PRIMERO DE LA LISTA", w("primero", 644.8) - t_obj, YELLOW, (0.66, 0.78), -6, 56)], tr="fade", td=0.3, tex=GFX)
    add(w("solo", 647.6) - 0.3, kb("u_8lnbXtxFGZw.jpg", "in", "doc"), [big("FALTABA EL DINERO", 0.4, 0.84, 76, YELLOW)], tex=CLEAN)
    add(w("washington", 652.2) - 0.4, kb("u_L_U4jhwZ6hY.jpg", "in", "night"), [rich("EL DINERO IBA A TARDAR", ("tardar",), 0.6, y=0.84, size=58)], tex=DARK)

    # ============================== CAP 5: EL TÚNEL (654.9 - 879.9)
    t_c5 = w("espera", 654.6) - 0.6
    bg, ov = chapter(5, "El túnel", "u_gmy25xvSkq8.jpg", "dark", "1979–1996")
    add(t_c5, bg, ov, tr="flash", td=0.25, tex=DARK)
    t_79 = w("1979", 657.6) - 0.6
    add(t_79, kb("u_DyYbAk1LFEs.jpg", "in", "doc"), [Badge("1979", 0.2, None), Counter(0, 1, "{:.0f}", "MILLÓN DE DÓLARES", w("millon", 659.4) - t_79, 0.4, (0.5, 0.45), 230)], tex=CLEAN)
    add(w("geologos", 662.6) - 0.6, kb("f_51721940911.jpg", "in", "doc"), [Badge("LOS GEÓLOGOS ESTUDIAN LA ROCA", 0.2, None)], tex=CLEAN)
    add(w("cinco", 665.9) - 0.1, cus(G4.calendar, cards=[("20", "NOV 1984", "CONTRATO ADJUDICADO", 0.4, GREYC)]), tr="fade", td=0.3, tex=GFX)
    add(w("despues", 672.1) - 0.1, kb("u_OQMZwNd3ThU.jpg", "in", "warm"), [rich("CASI 30 AÑOS DE ESTUDIOS", ("30",), 0.3, y=0.84, size=56), big("POR FIN HABÍA FECHA", 2.3, 0.7, 64, YELLOW)], tex=CLEAN)
    add(w("justo", 677.0) - 0.4, kb("u_sT50jo9LCH0.jpg", "in", "night"), [Darken(0.45), big("ANTES DE LA DECISIÓN QUE LO CAMBIA TODO…", 0.3, 0.5, 64, WHITE)], tex=DARK)
    add(w("canal", 680.6) - 0.6, kb("u_D7avZZXM0S0.jpg", "in", "warm"), [rich("SEGUIMOS A LOS CAMINOS HASTA EL FINAL", ("final",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("abren", 684.6) - 0.4, kb("u_rXtU385sj_w.jpg", "in", "doc"), [big("LOS QUE SE ABREN", 0.1, 0.84, 70)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("cierran", 686.6) - 0.4, kb("u_h1lF_j0fZdo.jpg", "in", "cold"), [big("LOS QUE SE CIERRAN", 0.1, 0.84, 70)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("borrar", 689.4) - 1.0, kb("u_V72VFoZ4LIk.jpg", "in", "doc"), [big("Y LOS QUE ALGUIEN DECIDE BORRAR", 0.1, 0.84, 64, YELLOW)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("suscribete", 692.2) - 1.2, kb("u_k-Pz80yzt7c.jpg", "in", "warm"), [Darken(0.35), FnOverlay(G2.subscribe)], tex=CLEAN)
    add(w("washington", 695.0) - 0.8, kb("u_XU93D-JThyE.jpg", "punch", "cold"), [rich("COSAS QUE SOLO PASAN EN WASHINGTON", ("washington",), 0.2, y=0.84, size=54)], tex=CLEAN)
    t_cal = w("tres", 696.4) - 0.1
    add(t_cal, cus(G4.calendar, cards=[("20", "NOV 1984", "CONTRATO", 0.0, GREYC), ("14", "DIC 1984", "STOP", w("14", 699.6) - t_cal, RED)],
                   title="TRES SEMANAS Y MEDIA DESPUÉS"), tr="fade", td=0.2, tex=GFX)
    t_rr = w("reagan", 702.0) - 0.9
    add(t_rr, kb("l_3a53308.jpg", "in", "archival"), [LowerThird("RONALD REAGAN", "Presidente de EE. UU. (1981–1989)", 0.3),
                                                   Stamp("PARAR EL PROYECTO", w("parar", 703.0) - t_rr, RED, (0.5, 0.42), -8, 96)], tex=CLEAN, post=postshake(2))
    add(w("segun", 705.6) - 0.2, kb("u_6cRJM4UmSHk.jpg", "in", "cold"), [rich("«PARA RECORTAR EL DÉFICIT»", ("déficit»",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(w("gente", 709.6) - 0.6, kb("f_3907232108.jpg", "in", "faded"), [rich("MÁS AÑOS DE MASSACRE MOUNTAIN", ("massacre", "mountain"), 1.4, y=0.86, size=56)], tex=ARCH)
    add(w("politicos", 714.6) - 0.3, kb("f_16315836669.jpg", "in", "doc", cam0=(0.78, 0.42, 1.6), cam1=(0.76, 0.42, 1.75))
        if have("f_16315836669.jpg") else kb("u_E94nZORR5qc.jpg", "out", "doc"),
        [LowerThird("HAL ROGERS", "Congresista por Kentucky desde 1981", 0.6)], tex=CLEAN)
    t_cal2 = w("15", 720.0) - 0.4
    add(t_cal2, cus(G4.calendar, cards=[("20", "NOV 1984", "CONTRATO", 0.0, GREYC), ("14", "DIC 1984", "STOP", 0.0, RED),
                                        ("15", "MAY 1985", "SIGUE ADELANTE", 0.3, (40, 130, 70))]),
        [LowerThird("DONALD HODEL", "Secretario del Interior", w("hodel", 724.0) - t_cal2)], tr="fade", td=0.3, tex=GFX)
    add(w("con", 727.4) - 0.1, kb("f_52071242701.jpg", "in", "doc"), [Badge("PRIMERO: UN TÚNEL PILOTO", 0.3, None)], tr="fade", td=0.3, tex=CLEAN)
    add(w("tardaron", 733.0) - 0.2, cus(G4.pass_section, mode="pilot"), [FnOverlay(G4.drips, n=26)], tr="zoom", td=0.3, tex=GFX)
    add(w("sorpresa", 745.0) - 0.8, kb("u_j6NxATgIeuU.jpg", "in", "dark"), [rich("UNA SORPRESA TRAS OTRA", ("sorpresa",), 0.2, y=0.84, size=58)], tex=DARK)
    add(w("arsilla", 747.6) - 0.2, kb("u_RoAhv3M5DUI.jpg", "punch", "doc"), [big("ARCILLA", 0.0, 0.84, 84, YELLOW, "pop")], tr="whip_l", td=0.15, tex=CLEAN)
    add(w("cuevas", 749.0) - 0.15, kb("u_bqVjvut1Oq0.jpg", "in", "cold"), [big("CUEVAS", 0.0, 0.84, 84, YELLOW, "pop")], tr="whip_l", td=0.15, tex=CLEAN)
    add(w("manantiales", 749.9) - 0.15, kb("u_-fKYil98I8E.jpg", "in", "cold"), [big("MANANTIALES", 0.0, 0.84, 84, YELLOW, "pop")], tr="whip_l", td=0.15, tex=CLEAN)
    add(w("arroyos", 751.2) - 0.15, kb("u_8QGC3MZgsnU.jpg", "in", "cold"), [big("ARROYOS BAJO TIERRA", 0.0, 0.84, 76, YELLOW, "pop")], tr="whip_l", td=0.15, tex=CLEAN)
    t_cav = w("cavernas", 753.2) - 0.15
    add(t_cav, kb("u_JJRYm9hqM58.jpg", "up", "cold"), [Counter(0, 85, "{:.0f} PIES", "DE ALTO · ≈ 26 M", 0.3, 0.9, (0.5, 0.45), 180)], tr="whip_l", td=0.15, tex=CLEAN)
    t_lago = w("lago", 757.6) - 0.6
    add(t_lago, kb("u_xyVkXjRvcME.jpg", "in", "cold"), [Counter(0, 30, "{:.0f} PIES", "DE PROFUNDIDAD", 0.5, 0.8, (0.5, 0.45), 180), big("UN LAGO", 0.0, 0.2, 70)], tex=CLEAN)
    t_agua = w("agua", 760.6) - 0.2
    add(t_agua, kb("f_6804440059.jpg", "in", "cold"), [FnOverlay(G4.drips, n=60),
                                                      Counter(0, 450, "{:.0f}", "GALONES POR MINUTO", w("450", 762.0) - t_agua, 1.0, (0.5, 0.42), 210, sub="≈ 1.700 LITROS")],
        tex=CLEAN)
    add(w("forrar", 765.6) - 0.6, kb("f_14019231093.jpg", "in", "cold"), [rich("UNA GRUESA CAPA DE PLÁSTICO", ("plástico",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(w("imagina", 769.6) - 0.1, kb("f_51722190863.jpg", "in", "dark"), [rich("IMAGINA SER UNO DE ESOS OBREROS", ("obreros",), 0.3, y=0.84, size=54)], tr="fade", td=0.4, tex=DARK)
    add(w("llevas", 774.8) - 0.1, kb("u_WzXvVof2PvI.jpg", "in", "dark"), [FnOverlay(G4.drips, n=40)], tex=DARK)
    add(w("sabiendo", 778.4) - 0.2, Split([kb("f_51820642354.jpg", "in", "doc"), kb("f_51614553206.jpg", "in", "doc")], labels=["TÚ", "LA OTRA CUADRILLA"]),
        tex=CLEAN)
    add(w("calculos", 786.2) - 0.6, kb("f_51721131837.jpg", "punch", "doc"), [rich("SI LOS CÁLCULOS FALLAN POR POCO…", ("fallan",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("dia", 788.6) - 0.6, kb("u_Uf8DWj-KIEg.jpg", "in", "dark"), [FnOverlay(G2.sound_rings, cx=0.5, cy=0.5)], tex=DARK, post=postshake(3))
    add(w("despues", 791.6) - 0.1, kb("f_51721940961.jpg", "in", "doc"), [Badge("21 DE JUNIO DE 1991", 0.2, None), rich("DESDE LOS DOS LADOS A LA VEZ", ("dos",), 2.0, y=0.84, size=54)], tex=CLEAN)
    add(w("9", 798.4) - 0.4, cus(G4.pass_section, mode="meet"), tr="zoom", td=0.3, tex=GFX)
    add(w("fin", 805.4) - 0.3, cus(G4.pass_section, mode="open"), tr="flash", td=0.25, tex=GFX)
    add(w("casi", 813.6) - 0.2, kb("u_Gr4i6eeBvu8.jpg", "in", "doc"), [Badge("DOS TUBOS · DOS CARRILES POR SENTIDO", 0.2, None)], tex=CLEAN)
    t_cost = w("principio", 817.8) - 0.4
    add(t_cost, cus(G4.cost_bars, items=[("PREVISTO", 160, 0.3, GREYC), ("COSTE FINAL", 280, w("280", 825.2) - t_cost, YELLOW)], title="EL TÚNEL"),
        tr="fade", td=0.3, tex=GFX)
    add(w("aqui", 826.6) - 0.2, kb("u_di4pFRL4SkI.jpg", "in", "dark"), [Darken(0.5), Badge("PREGUNTA 2", 0.2, None),
                                                                      rich("¿POR QUÉ TARDARON TANTO EN QUITARLA?", ("tanto",), w("massacre", 829.6) - w("aqui", 826.6), y=0.5, size=72)],
        tr="glitch", td=0.3, tex=DARK)
    add(w("porque", 834.0) - 0.2, kb("u_ZUBQPscbYis.jpg", "in", "cold"),
        [Darken(0.35), BigText("QUITARLA", "bebas", 130, WHITE, (0.32, 0.5), 0.3, None, "pop", tracking=6),
         BigText("≠", "bebas", 150, YELLOW, (0.5, 0.5), 1.0, None, "pop"),
         BigText("CERRARLA", "bebas", 130, WHITE, (0.68, 0.5), 1.4, None, "pop", tracking=6)], tex=CLEAN)
    add(w("era", 837.9) - 0.1, kb("u_cds5wXQUJsM.jpg", "in", "doc"), [rich("UNA DE LAS RUTAS PRINCIPALES ENTRE EL NORTE Y EL SUR", ("norte", "sur"), 0.3, y=0.84, size=48, maxw=0.8)], tex=CLEAN)
    add(w("mandar", 842.6) - 0.6, mp("cg_east", [(0, -84.0, 36.0, 0.8), (5.0, -84.0, 36.0, 0.83)],
                                     [dict(type="route", path=NS_ROUTE, t0=0.0, draw=0.4, color=YELLOW, width=6, traffic=24, speed=150),
                                      dict(type="pin", at="gap", t0=0.3, color=RED, label="NINGUNA ALTERNATIVA", side="r", box=True)]), tex=GFX)
    add(w("unica", 848.2) - 0.4, kb("u_ZjXR5BDwyTo.jpg", "in", "night"), [rich("LA ÚNICA SALIDA: DENTRO DE LA MONTAÑA", ("dentro",), 0.3, y=0.84, size=52)], tex=DARK)
    add(w("fortuna", 850.4) - 0.6, kb("u_v9rZ3Yz6fSg.jpg", "in", "cold"), [big("A CUENTAGOTAS", 0.8, 0.84, 76, YELLOW)], tex=CLEAN)
    t_40 = w("entre", 852.8) - 0.1
    add(t_40, cus(G4.timeline, events=[(1956, "LA PROPUESTA", 0.4), (1973, "LA LEY", 1.0), (1979, "1.ER MILLÓN", 1.6), (1984, "REAGAN: STOP", w("presidente", 857.8) - t_40),
                                       (1996, "PRIMER AUTO", w("cruzo", 854.6) - t_40)], hi=1984, red=(1984,), title="LA ESPERA"),
        [FnOverlay(G4.span_bar, ya=1956, yb=1996, text="40 AÑOS", t0=w("40", 856.4) - t_40)], tr="fade", td=0.3, tex=GFX)
    add(w("desde", 859.4) - 0.2, kb("f_34833834135.jpg", "in", "doc"), [Badge("DESDE EL 18 DE OCTUBRE DE 1996", 0.2, None)], tex=CLEAN)
    add(w("pasaban", 867.4) - 0.2, kb("u_H03VleIfuvE.jpg", "in", "warm"),
        [FnOverlay(G3.gauge, value=45, unit="MPH", sub="≈ 70 KM/H", t0=0.6), big("EN LÍNEA RECTA, POR DEBAJO", 0.2, 0.12, 60)], tex=CLEAN)
    add(w("arriba", 873.0) - 0.2, kb("u_fT-y9mceAVU.jpg", "in", "cold"), [rich("ARRIBA, LA VIEJA CARRETERA SE QUEDÓ VACÍA", ("vacía",), 0.3, y=0.84, size=52)], tex=CLEAN)
    add(w("entonces", 875.9) - 0.1, kb("u_VjQ1tj1_jMU.jpg", "in", "dark"), [Darken(0.4), big("LA PARTE MÁS RARA DE ESTA HISTORIA", 0.8, 0.5, 76, YELLOW, "pop")], tex=DARK)

    # ============================== CAP 6: BORRAR LA CARRETERA (879.9 - 1008.4)
    t_c6 = w("cuando", 880.0) - 0.2
    bg, ov = chapter(6, "Borrar la carretera", "u_h1lF_j0fZdo.jpg", "dark")
    add(t_c6, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(w("normal", 883.2) - 0.4, kb("u_l2RPhWg31ro.jpg", "in", "cold"), [rich("LO NORMAL ES DEJARLA AHÍ", ("dejarla",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(w("grietas", 886.0) - 0.4, kb("u_nv6W9GCdHQQ.jpg", "punch", "doc"), [big("GRIETAS", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("hierba", 887.4) - 0.3, kb("u_ErBlfW7rfBI.jpg", "in", "doc"), [big("HIERBA", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("paseo", 891.6) - 1.2, kb("u_VjQ1tj1_jMU.jpg", "in", "doc"), [big("UN PASEO", 0.4, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("aqui", 892.4) - 0.2, kb("u_V72VFoZ4LIk.jpg", "punch", "doc"), [Stamp("LA DESMONTARON", w("desmontaron", 893.4) - w("aqui", 892.4) + 0.2, RED, (0.5, 0.5), -8, 110)],
        tex=CLEAN, post=postshake(4))
    add(w("primero", 894.0) - 0.1, kb("u_EpzhIINqUfc.jpg", "in", "doc"), [Badge("1 · LEVANTAR EL ASFALTO", 0.2, None)], tex=CLEAN)
    add(w("rompieron", 897.2) - 0.3, kb("u_HFWcm4a3eOM.jpg", "in", "doc"), [Badge("2 · ROMPER LAS CURVAS UNA A UNA", 0.2, None)], tex=CLEAN, post=postshake(2))
    add(w("despues", 899.8) - 0.1, kb("u_3U7jsNq1ZSk.jpg", "in", "doc"), [Badge("3 · LLEVARSE LOS ESCOMBROS", 0.2, None)], tex=CLEAN)
    add(w("toneladas", 902.0) - 0.4, kb("u_eIj8K5dHylY.jpg", "in", "doc"), [rich("HASTA EL RELLENO DE DÉCADAS ATRÁS", ("relleno",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("querian", 906.4) - 0.6, cus(G4.pass_section, mode="erase"),
        [BigText("COMO SI NUNCA HUBIERA EXISTIDO", "bebas", 64, YELLOW, (0.5, 0.92), w("nunca", 910.0) - w("querian", 906.4) + 0.6, None, "up", tracking=4)], tr="fade", td=0.3, tex=GFX)
    add(w("saber", 913.6) - 0.6, kb("u_mPmips2hYd0.jpg", "in", "warm"), [Badge("DIARIOS ANTIGUOS", 0.2, None)], tex=CLEAN)
    add(w("mapas", 918.4) - 0.3, kb("u_DD0fKMPg8ZA.jpg", "in", "sepia"), [Badge("MAPAS ANTIGUOS", 0.2, None)], tex=ARCH)
    add(w("forma", 921.6) - 0.4, fr("l_3a52112.jpg"), [rich("LA FORMA QUE VIO DANIEL BOONE", ("boone",), 0.3, y=0.88, size=54)], tex=ARCH)
    add(w("replantaron", 923.8) - 0.1, kb("u_EkEdHarUPTs.jpg", "in", "warm"), [rich("ESPECIES NATIVAS DONDE HABÍA GUARDARRAÍLES", ("nativas",), 0.4, y=0.84, size=50)], tex=CLEAN)
    t_5m = w("borrar", 927.4) - 0.2
    add(t_5m, cus(G4.cost_bars, items=[("EL TÚNEL", 280, 0.2, GREYC), ("BORRAR LA CARRETERA", 5, w("5", 929.6) - t_5m, (90, 190, 110))], title="CASI NADA AL LADO DEL TÚNEL"),
        tr="fade", td=0.3, tex=GFX)
    add(w("final", 932.4) - 0.1, kb("u_oTLHqheXS7Q.jpg", "in", "warm"), [big("6 PIES DE ANCHO · MENOS DE 2 M", 0.8, 0.84, 62)], tex=CLEAN)
    add(w("vuelve", 937.6) - 0.2, kb("f_6350116055.jpg", "in", "warm"), [rich("COMO EN TIEMPOS DE LOS PIONEROS", ("pioneros",), 0.3, y=0.84, size=54)], tex=CLEAN)
    t_3mi = w("tres", 942.0) - 0.2
    add(t_3mi, mp("cg_loc", [loc_cam(0, -450, 600, 1.35), loc_cam(6.2, -450, 550, 1.5)],
                  BORDERS + [dict(type="route", path=TRAIL, t0=0.2, draw=2.6, color=DIRT, width=7, dash=16),
                             dict(type="label", at=at(-1000, 1200), text="≈ 3 MILLAS · SOLO A PIE", t0=1.6, size=54, box=True),
                             dict(type="pin", at="gap", t0=0.0, color=WHITE, pulse=False)]), tr="zoom", td=0.3, tex=GFX)
    add(w("subes", 948.6) - 0.3, kb("u_OcAB4rvMhj8.jpg", "in", "warm"), [big("TIERRA BAJO LOS PIES", 0.3)], tex=CLEAN)
    add(w("arboles", 950.6) - 0.3, kb("u_0DbZQRqCglU.jpg", "in", "warm"), [big("ÁRBOLES A LOS LADOS", 0.2)], tex=CLEAN)
    add(w("ningun", 952.0) - 0.2, kb("u_-YiJvbfNDqk.jpg", "in", "cold"), [big("NINGÚN MOTOR", 0.3)], tex=CLEAN)
    add(w("alto", 954.6) - 0.6, kb("f_51529351091.jpg", "in", "doc"), [Badge("LÍNEA KENTUCKY · VIRGINIA", 0.3, None)], tex=CLEAN)
    add(w("mirar", 961.0) - 1.4, kb("l_63990.jpg", "l", "doc"), [rich("LO QUE VENÍAN A BUSCAR", ("buscar",), 0.6, y=0.84, size=56)], tex=CLEAN)
    add(w("nada", 964.8) - 0.1, kb("l_63991.jpg", "in", "doc"), [rich("NADA TE DICE QUE AQUÍ HUBO UNA CARRETERA", ("carretera",), 0.3, y=0.84, size=50)], tex=CLEAN)
    add(w("70", 966.2) - 0.2, kb("u_F3edSiwSJkw.jpg", "in", "bw"), [Counter(0, 70, "{:.0f} AÑOS", "DE CURVAS TEMIDAS", 0.2, 0.8, (0.5, 0.45), 170)], tex=ARCH)
    add(w("raya", 969.4) - 0.6, kb("u_6NJ5WxAvMnE.jpg", "in", "cold"), [Stamp("NI UNA RAYA", 0.2, RED, (0.5, 0.42), -6, 90)], tr="glitch", td=0.2, tex=CLEAN)
    add(w("trozo", 970.4) - 0.3, kb("u_MZgmNH6174Q.jpg", "in", "cold"), [Stamp("NI UN TROZO DE ASFALTO", 0.1, RED, (0.5, 0.42), -6, 80)], tr="glitch", td=0.2, tex=CLEAN)
    add(w("exactamente", 972.4) - 0.6, kb("u_R9tPheZuGnA.jpg", "in", "warm"), [rich("EXACTAMENTE LO QUE BUSCABAN", ("exactamente",), 0.3, y=0.84, size=56)], tr="fade", td=0.4, tex=CLEAN)
    add(w("hubo", 974.8) - 0.1, kb("u_rNxfMnfnenE.jpg", "in", "warm"), [rich("UN HOMBRE ESPERABA ESE CAMINO MÁS QUE NADIE", ("nadie",), 0.3, y=0.84, size=50)], tex=CLEAN)
    add(w("thomas", 977.8) - 0.1, kb("u_2ILU-oeOuE4.jpg", "in", "warm"), [LowerThird("THOMAS D. CLARK", "Historiador oficial de Kentucky", 0.3)], tex=CLEAN)
    add(w("lugares", 982.6) - 0.6, fr("l_3b08248.jpg"), [Caption("«Un lugar que todo kentuckiano tiene que visitar»", None, 0.4)], tex=ARCH)
    add(w("antes", 986.4) - 0.1, kb("u_0DbZQRqCglU.jpg", "out", "warm"), [Badge("SU SUEÑO", 0.3, None),
                                                                        rich("CAMINAR POR CUMBERLAND GAP SIN UN SOLO AUTO ALREDEDOR", ("sin", "auto"), w("caminar", 990.0) - w("antes", 986.4), y=0.8, size=52, maxw=0.8)],
        tex=CLEAN)
    add(w("anos", 993.0) - 0.1, kb("f_6350137195.jpg", "r", "warm"), [big("EL SUEÑO SE CUMPLIÓ", 1.8, 0.84, 72, YELLOW)], tex=CLEAN)
    add(w("asi", 997.6) - 0.6, kb("u_IYAvTCJ4-AY.jpg", "in", "dark"), [rich("LA CARRETERA QUE MATABA GENTE DESAPARECIÓ DE VERDAD", ("desapareció",), 0.3, y=0.84, size=50, maxw=0.8)], tex=DARK)
    add(w("tunel", 1001.4) - 0.6, kb("u_cgMDbarQHpA.jpg", "in", "doc"), [rich("PERO EL TÚNEL SIGUE AHÍ ABAJO", ("túnel",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(w("vive", 1005.0) - 0.4, kb("f_34833834135.jpg", "punch", "doc"), [rich("Y VIVE DE UNA MANERA QUE POCOS IMAGINAN", ("imaginan",), 0.3, y=0.84, size=52)], tex=CLEAN)

    # ============================== CAP 7: HOY (1008.4 - 1078.4)
    t_c7 = w("hoy", 1008.4) - 0.1
    bg, ov = chapter(7, "Hoy", "u_Jyfdf2_Gl78.jpg", "dark", "2026")
    add(t_c7, bg, ov, tr="flash", td=0.25, tex=DARK)
    t_30 = w("tunel", 1010.8) - 0.2
    add(t_30, kb("u_xa14tewS1-w.jpg", "in", "doc"), [Counter(0, 30, "{:.0f} AÑOS", "1996 → 2026", w("30", 1012.8) - t_30, 0.8, (0.5, 0.45), 200)], tex=CLEAN)
    t_oct = w("del", 1014.2) - 0.1
    add(t_oct, cus(G4.calendar, cards=[("16", "OCT 2026", "", 0.2, (40, 130, 70)), ("17", "OCT 2026", "", 0.4, (40, 130, 70)),
                                       ("18", "OCT 2026", "", 0.6, (40, 130, 70))], title="ALGO QUE CASI NUNCA PASA"), tr="fade", td=0.3, tex=GFX)
    add(w("visitas", 1019.8) - 0.3, kb("u_YHMOk7iLUEc.jpg", "in", "doc"), [Badge("VISITAS GUIADAS DENTRO DEL TÚNEL", 0.2, None)], tex=CLEAN)
    add(w("caminatas", 1023.4) - 0.3, kb("u_rjWqOnJAUyk.jpg", "in", "warm"), [Badge("CAMINATAS HASTA EL VIEJO PASO", 0.2, None)], tex=CLEAN)
    t_tr = w("mientras", 1026.4) - 0.2
    add(t_tr, kb("u_iNlNrMjdI_Q.jpg", "in", "warm"),
        [Counter(0, 30000, "+{:,.0f}", "VEHÍCULOS AL DÍA", w("30", 1030.2) - t_tr, 1.0, (0.5, 0.42), 190)], tex=CLEAN)
    add(w("desde", 1032.2) - 0.1, kb("u_TtMKq3lJm-U.jpg", "in", "dark"), [Badge("2 SALAS DE CONTROL · 24 HORAS", 0.2, None)], tex=DARK)
    add(w("vigilando", 1035.6) - 0.6, kb("u_p7Bfwn_VKRQ.jpg", "in", "cold"), tex=CLEAN)
    add(w("camiones", 1038.6) - 0.2, kb("f_53615094042.jpg", "in", "doc"), [Badge("CARGA PELIGROSA", 0.2, None)], tex=CLEAN)
    add(w("cruzan", 1041.6) - 0.6, cus(G4.hazmat), tr="fade", td=0.3, tex=GFX)
    add(w("bomberos", 1045.6) - 0.6, kb("u_7g3pHGykPXU.jpg", "in", "doc"), [big("BOMBEROS", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("emergencias", 1047.6) - 0.3, kb("u_owSUPshiaAc.jpg", "in", "night"), [big("EMERGENCIAS", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=DARK)
    add(w("gruas", 1050.0) - 0.4, kb("u_HZ_6ktzQWZ0.jpg", "in", "doc"), [big("GRÚAS", 0.1, 0.84, 80)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("contrario", 1051.0) - 0.8, Split([kb("u_YH1KID3mTpY.jpg", "in", "dark"), kb("u_TtMKq3lJm-U.jpg", "in", "dark")], labels=["MASSACRE MOUNTAIN", "HOY"]),
        [big("TODO MEDIDO · TODO CONTROLADO", w("medido", 1052.6) - w("contrario", 1051.0) + 0.8, 0.1, 60, YELLOW)], tex=DARK)
    add(w("justo", 1058.2) - 0.2, kb("u_CoD2Q92UaEg.jpg", "in", "warm"), [rich("JUSTO ENCIMA: SILENCIO", ("silencio",), 0.4, y=0.84, size=58)], tr="fade", td=0.5, tex=CLEAN)
    add(w("rugian", 1061.6) - 0.8, cus(G4.pass_section, mode="today"), tr="fade", td=0.3, tex=GFX)
    add(w("muchos", 1069.6) - 0.1, kb("u_e7r0wTz3ZHU.jpg", "in", "dark"), [rich("A UNOS METROS SOBRE SU CABEZA…", ("cabeza…",), 1.4, y=0.84, size=56)], tex=DARK)
    add(w("camino", 1075.4) - 0.6, kb("l_3a51182.jpg", "out", "archival", z=1.05), [rich("EL CAMINO QUE ABRIÓ DANIEL BOONE", ("boone",), 0.4, y=0.88, size=54)], tex=ARCH)

    # ============================== CONCLUSIÓN (1078.4 - end)
    add(w("asi", 1078.4) - 0.1, kb("u_jYA6yTcqI0k.jpg", "in", "dark"), [Darken(0.45), big("LA PRIMERA PREGUNTA", 0.3, 0.5, 90, YELLOW, "pop")], tr="fade", td=0.4, tex=DARK)
    q1(w("por", 1081.7) - 0.2, "u_IYAvTCJ4-AY.jpg")
    add(w("estados", 1087.8) - 0.2, kb("u_WM5WRBl-EZ8.jpg", "in", "dark"), [Darken(0.3), rich("NO SOLO PORQUE MATARA GENTE", ("solo",), 0.5, y=0.5, size=72)], tex=DARK)
    add(w("borro", 1093.0) - 0.4, cus(G4.pass_section, mode="layers"), [Badge("ESTABA ENCIMA DE ALGO QUE VALÍA MÁS", 0.2, None)], tr="fade", td=0.3, tex=GFX)
    add(w("camino", 1097.6) - 0.6, kb("l_3a51182.jpg", "in", "archival", z=1.1), [rich("EL CAMINO DE CIENTOS DE MILES DE FAMILIAS", ("familias",), 0.3, y=0.88, size=50)], tex=ARCH)
    add(w("unica", 1101.0) - 0.8, cus(G4.pass_section, mode="erase"), tr="fade", td=0.3, tex=GFX)
    t_three = w("salvar", 1104.6) - 0.6
    add(t_three, kb("u_0DbZQRqCglU.jpg", "in", "warm"),
        [Darken(0.55), Rich([("SALVAR", 0.3, "h"), ("UN", 0.42, "n"), ("CAMINO", 0.54, "n"), ("·", 1.4, "n"), ("BORRAR", 1.6, "r"), ("OTRO", 1.72, "n"),
               ("·", w("tercero", 1112.0) - t_three - 0.4, "n"), ("ABRIR", w("tercero", 1112.0) - t_three - 0.2, "h"), ("UN", w("tercero", 1112.0) - t_three - 0.08, "n"),
               ("TERCERO", w("tercero", 1112.0) - t_three + 0.04, "h")], 0.5, 0.5, 0.9, 64)], tex=CLEAN)
    add(w("si", 1114.8) - 0.2, kb("u_H03VleIfuvE.jpg", "in", "warm"), [Badge("CAMINO DE KNOXVILLE O DE LEXINGTON", 0.4, None)], tex=CLEAN)
    add(w("cuentanos", 1116.0) - 0.4, kb("u_e7r0wTz3ZHU.jpg", "out", "dark"),
        [Darken(0.4), FnOverlay(G4.comments, line1="¿SABÍAS QUE PASABAS POR DEBAJO", line2="DEL WILDERNESS ROAD?")], tex=DARK)
    add(w("llegaste", 1121.2) - 0.4, kb("u_F3edSiwSJkw.jpg", "out", "bw"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿SUBISTE POR MASSACRE MOUNTAIN?", line2="¿QUÉ CURVA NO SE TE HA OLVIDADO?")], tr="fade", td=0.4, tex=DARK)
    return S
