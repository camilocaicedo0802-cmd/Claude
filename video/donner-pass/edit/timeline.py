"""The edit: every shot of the Donner Pass video, synced to the voice-over."""
import bisect
import os
import sys

import cv2

import gfx2 as G2
import gfx3 as G3
import gfx4 as G4
import gfx5 as G5
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Seq, Solid, Split, Stamp, Still, TimelineBar, Video)
from render import Shot
import words

TOTAL = 1130.06
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
FILM = dict(grain=12, dust=0.6, flicker=0.04, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)
GREYC = (110, 112, 116)
GREEN = (40, 130, 70)
SNOWC = (90, 130, 170)


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
    sc = _scenes(name)
    i = bisect.bisect_right(sc, approx) - 1
    a, b = sc[i], sc[i + 1]
    need = dur * speed + 0.25
    s = approx
    if b - s < need:
        s = max(a + 0.1, b - need)
    return Video(f"ia_{name}.mp4", start=s, speed=speed, grade=g, **kw)


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
    return Still(path, c0, c1, grade=g, **kw)


def st(sid, m="in", z=1.0, **kw):
    """Alfred A. Hart stereograph (left half), Central Pacific Railroad, 1865-69."""
    return kb(f"l_{sid}_L.jpg", m, "archival", z, **kw)


def fr(path, cap=None, g="archival", **kw):
    return Framed(path, cap, grade=g, **kw)


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


CP_ROUTE = ["sacramento", "colfax", "emigrant_gap", "tunnel6", "truckee", "reno", "winnemucca", "elko", "promontory"]
UP_ROUTE = ["council_bluffs", "north_platte", "cheyenne", (-107.2, 41.8), (-110.0, 41.3), "ogden", "promontory"]
SIERRA_ROUTE = ["sacramento", (-121.2, 38.8), "colfax", "dutch_flat", "emigrant_gap", "yuba_gap", "cisco", "norden", "tunnel6", "truckee"]
SEA_ROUTE = [(113.0, 22.0), (122.0, 24.5), (140.0, 31.0), (165.0, 36.0), (-170.0, 38.0), (-145.0, 38.5), (-122.42, 37.77)]
OLD_LINE = ["norden", "tunnel6", "china_wall", (-120.300, 39.3115), (-120.282, 39.3060), (-120.262, 39.3010)]
NEW_TUNNEL = [(-120.3530, 39.3170), (-120.330, 39.3110), (-120.305, 39.3050), (-120.290, 39.3040)]


# ------------------------------------------------------------------ the edit
def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="u_V5QEkJL3O3c.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.55), Badge(badge, 0.2, None)] +
            question("¿Por qué Estados Unidos abandonó un túnel que costó tanto abrir a mano?", ("abandonó",), size=68),
            tr="glitch", td=0.3, tex=DARK)

    # ============================== INTRO (0 - 67.3)
    add(0.0, kb("f_6970089625.jpg", "in", "none"), [torch(((0.2, 0.6), (0.55, 0.5)), r=440, amb=0.12), Badge("DONNER PASS · CALIFORNIA", 0.6, 3.0)], tex=DARK)
    add(3.32, kb("f_6970092315.jpg", "in", "cold"), [Badge("UN TÚNEL DE TREN", 0.2, None)], tr="fade", td=0.4, tex=CLEAN)
    t_sn = w("sierra", 6.2)
    add(t_sn - 0.6, mp("dp_sierra", [(0, -120.6, 39.1, 1.05), (2.6, -120.35, 39.3, 1.45)],
                       [dict(type="label", at=(-120.9, 38.75), text="SIERRA NEVADA", t0=0.3, size=58),
                        dict(type="pin", at="tunnel6", t0=0.9, label="DONNER PASS", side="r", box=True, size=48)]),
        tr="zoom", td=0.35, tex=GFX)
    add(8.38, kb("u_ATvkjM2a5Xk.jpg", "in", "cold"), [Counter(0, 7000, "+{:,.0f}", "PIES DE ALTURA", 0.2, 1.2, (0.5, 0.42), 190, sub="≈ 2.100 METROS")],
        tr="whip_l", td=0.25, tex=CLEAN)
    add(12.44, kb("f_6823963454.jpg", "in", "none"), [torch(((0.25, 0.45), (0.75, 0.55))), rich("NI RIELES NI TRENES", ("rieles", "trenes"), 1.4, y=0.84, size=58)],
        tr="fade", td=0.4, tex=DARK)
    add(16.72, kb("u_t0l8jUAYC88.jpg", "in", "cold"), [big("LOS TRENES NO SE HAN IDO", 0.4)], tex=CLEAN)
    add(19.70, kb("f_32253221834.jpg", "in", "faded"), [rich("SIGUEN CRUZANDO CADA DÍA", ("cada", "día"), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(w("otro", 23.0) - 1.2, warp(G5.tunnel6, 3.2, 1.0, mode="two"), tr="zoom", td=0.3, tex=GFX)
    add(24.68, kb("u_ynYlqQV4Qtk.jpg", "in", "dark"), [rich("NI DERRUMBE NI ACCIDENTE", ("derrumbe", "accidente"), 0.4, y=0.84, size=56)], tr="fade", td=0.3, tex=DARK)
    add(27.04, kb("u_RkjuiI6N8fg.jpg", "in", "none"), [torch(((0.15, 0.5), (0.7, 0.55)), r=360)], tex=DARK)
    t_bar = w("barrenos", 32.6)
    add(t_bar - 1.4, kb("u_u6zVikMNTmQ.jpg", "punch", "warm"), [torch(((0.45, 0.5), (0.55, 0.48)), r=520, amb=0.12),
                                                              Callout(960, 560, 1300, 300, "MARCAS DE BARRENOS", 0.6)], tex=CLEAN)
    add(33.84, fr("l_1s00546_L.jpg", "Túnel de la cumbre, antes de terminarse · Alfred A. Hart, 1866-67"), [Badge("HECHAS A MANO · +150 AÑOS", 0.3, None)], tex=ARCH)
    add(37.08, kb("u_XZuqMUiSdgc.jpg", "punch", "warm"), [big("A GOLPES DE MAZO", 0.4, 0.84, 76, YELLOW, "pop")], tex=CLEAN, post=postshake(3))
    add(40.02, kb("u_cRDUjKh6Xj0.jpg", "in", "dark"), [rich("UN DÍA, SIN CEREMONIA, LA DEJARON VACÍA", ("vacía",), 0.4, y=0.84, size=52)], tr="fade", td=0.5, tex=DARK)
    add(43.44, kb("u_QgdRRlD6iXo.jpg", "in", "doc"), [big("MILES DE NOMBRES", 0.3, 0.84, 70)], tex=CLEAN)
    add(w("grupos", 46.2) - 0.3, kb("f_6970080205.jpg", "l", "doc"), tr="whip_l", td=0.2, tex=CLEAN)
    add(48.16, kb("f_8306423263.jpg", "in", "doc"), [rich("Y DE GENTE QUE SUBIÓ EL FIN DE SEMANA PASADO", ("pasado",), 0.2, y=0.84, size=48, maxw=0.8)], tex=CLEAN)
    t_ni = w("pero", 51.3)
    add(t_ni - 0.1, st("1s00510", "in"), [Darken(0.1), rich("NI UNO DE LOS HOMBRES QUE LA ABRIERON", ("ni", "uno"), 0.4, y=0.86, size=52, maxw=0.8),
                                          Caption("Trabajadores junto a la boca del túnel de la cumbre · A. A. Hart", None, 1.8, None, 0.96)], tr="fade", td=0.4, tex=ARCH)
    add(53.64, kb("u_7Gk3VDkqw0w.jpg", "in", "none"), [torch(((0.3, 0.4), (0.6, 0.6))), rich("LA PIEDRA RECUERDA LO QUE LA HISTORIA OLVIDÓ", ("piedra", "olvidó"), 0.8, y=0.84, size=50, maxw=0.8)],
        tex=DARK)
    q1(58.42)
    add(62.80, kb("u_NryPG6WPPho.jpg", "in", "dark"), [Darken(0.5), Badge("PREGUNTA 2", 0.2, None)] +
        question("¿Y por qué entre tantos nombres no está el de ninguno de los que lo cavaron?", ("ninguno",), size=68), tr="glitch", td=0.3, tex=DARK)
    # title sting
    add(67.3, st("1s00547", "in"),
        [Darken(0.5, 0.0, 0.3), BigText("DONNER PASS", "bebas", 190, YELLOW, (0.5, 0.40), 0.1, None, "pop", tracking=10),
         BigText("El túnel que nadie firmó", "serif_it", 70, WHITE, (0.5, 0.58), 0.45, None, "up"),
         Badge("CAPÍTULO 1 · LA MONTAÑA QUE NO DEJABA PASAR", 1.0, None)], tr="flash", td=0.25, tex=ARCH)

    # ============================== CAP 1: LA MONTAÑA (70.6 - 184.3)
    add(70.6, kb("u_Gt8UhEvzIxc.jpg", "in", "cold"), [Badge("DONNER LAKE · SIERRA NEVADA", 0.2, None)], tr="fade", td=0.3, tex=CLEAN)
    add(72.14, kb("u_IuSemNxGS88.jpg", "in", "cold"), [rich("UNO DE LOS LUGARES DONDE MÁS NIEVA DE EE. UU.", ("nieva",), 0.3, y=0.84, size=50, maxw=0.8)], tex=CLEAN)
    add(75.76, cus(G5.snow_depth, peak_t=w("800", 81.6) - 75.76 - 0.2), tr="fade", td=0.3, tex=GFX)
    add(84.52, kb("l_3a28397.jpg", "in", "archival"), [Caption("Tocones cortados por la expedición Donner en Summit Valley (foto de 1866)", None, 0.4)], tex=ARCH)
    add(88.36, kb("u_QFhIVlX9wTs.jpg", "in", "warm"), [Badge("INVIERNO DE 1846", 0.2, None), rich("81 COLONOS CAMINO DE CALIFORNIA", ("81",), 1.2, y=0.84, size=56)], tex=CLEAN)
    add(95.02, kb("u_HwoBnQNUqCQ.jpg", "in", "cold"), [big("LA EXPEDICIÓN DONNER", 0.2, 0.84, 72, YELLOW)], tex=CLEAN, post=postshake(1))
    add(100.26, kb("u_2x8ofryv4JU.jpg", "in", "cold"), [rich("MESES SIN AVANZAR NI RETROCEDER", ("meses",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(103.58, cus(G5.party, t_die=1.2), tr="fade", td=0.3, tex=GFX)
    add(106.98, kb("u_gL84ogFsV6s.jpg", "in", "dark"), [Darken(0.35), rich("TUVIERON QUE HACER LO IMPENSABLE", ("impensable",), 0.6, y=0.84, size=56)], tex=DARK)
    add(111.40, kb("l_23486.jpg", "up", "doc"), [LowerThird("MONUMENTO A LOS PIONEROS", "Donner Memorial State Park, Truckee", 0.3)], tex=CLEAN)
    add(114.30, kb("u_09mUBr7p1i4.jpg", "in", "cold"), [big("LA MONTAÑA QUE NO DEJA PASAR", 0.4, 0.5, 80, WHITE, "pop")], tex=CLEAN)
    add(118.08, st("1s00549", "in"), [Badge("15 AÑOS DESPUÉS", 0.2, None)], tr="fade", td=0.3, tex=ARCH)
    add(120.80, kb("u_Gfd1kprvOac.jpg", "in", "warm"), [big("POR AHÍ IBA A PASAR UN TREN", 0.3, 0.84, 66, YELLOW)], tex=CLEAN)
    add(123.74, fr("l_05516.jpg"), [LowerThird("ABRAHAM LINCOLN", "Presidente de EE. UU. · firma la ley en 1862", 0.4), Badge("1862", 0.2, None)], tex=ARCH)
    t_tc = 128.6
    add(t_tc, mp("dp_us", [(0, -105.0, 40.0, 0.95), (10.2, -110.0, 40.3, 1.0)],
                 [                  dict(type="route", path=UP_ROUTE, t0=w("este", 134.4) - t_tc, draw=2.6, color=WHITE, width=6),
                  dict(type="label", at=(-96.5, 42.6), text="UNION PACIFIC", t0=w("este", 134.4) - t_tc + 0.3, size=44),
                  dict(type="route", path=CP_ROUTE, t0=w("sacramento", 135.6) - t_tc, draw=2.6, color=YELLOW, width=7),
                  dict(type="pin", at="sacramento", t0=w("sacramento", 135.6) - t_tc, label="SACRAMENTO", side="l"),
                  dict(type="label", at=(-119.0, 37.6), text="CENTRAL PACIFIC", t0=w("central", 137.2) - t_tc, size=48, box=True)]),
        [BigText("EL PRIMER FERROCARRIL TRANSCONTINENTAL", "bebas", 58, WHITE, (0.5, 0.1), 0.3, None, "up", tracking=4)], tr="zoom", td=0.35, tex=GFX)
    t_sv = 138.82
    add(t_sv, mp("dp_sierra", [(0, -121.1, 38.9, 1.0), (7.0, -120.6, 39.15, 1.12)],
                 [dict(type="pin", at="sacramento", t0=0.0, label="SACRAMENTO", side="b", pulse=False),
                  dict(type="band", path=[(-121.6, 38.0), (-121.0, 38.6), (-120.5, 39.1), (-120.2, 39.5), (-120.0, 39.9)], t0=w("sierra", 144.3) - t_sv,
                       draw=1.0, width=170, alpha=0.3, color=(220, 230, 240)),
                  dict(type="label", at=(-120.55, 38.95), text="SIERRA NEVADA", t0=w("sierra", 144.3) - t_sv + 0.4, size=64, box=True)]),
        [BigText("EL PEOR OBSTÁCULO DE TODO EL CAMINO", "bebas", 56, WHITE, (0.5, 0.1), w("peor", 141.5) - t_sv, None, "up", tracking=4)], tr="fade", td=0.3, tex=GFX)
    add(146.04, kb("u_rvVhr2LngP4.jpg", "in", "sepia"), [LowerThird("THEODORE JUDAH", "Ingeniero que trazó la ruta", 0.3)], tex=ARCH)
    add(148.78, mp("dp_sierra", [(0, -120.9, 39.05, 1.05), (5.3, -120.6, 39.2, 1.2)],
                   [dict(type="route", path=SIERRA_ROUTE, t0=0.1, draw=2.4, color=YELLOW, width=6),
                    dict(type="pin", at="tunnel6", t0=2.0, label="DONNER PASS", side="r", box=True, size=46)]), tr="fade", td=0.3, tex=GFX)
    add(151.28 + 0.8, st("1s00589", "in"), [Counter(0, 15, "{:.0f}", "TÚNELES", 0.0, 0.8, (0.5, 0.45), 230)], tex=ARCH)
    add(154.10, warp(G5.tunnel6, 0.0, 0.55, mode="plan"), tr="zoom", td=0.3, tex=GFX)
    add(163.82, kb("u_B6yDtYs2IgY.jpg", "in", "sepia"), [Darken(0.3), Badge("NOVIEMBRE DE 1863", 0.2, None),
                                                       rich("JUDAH MUERE DE FIEBRE AMARILLA", ("judah",), 1.6, y=0.84, size=56)], tr="fade", td=0.4, tex=ARCH)
    add(169.24, st("1s00454", "in"), [rich("SU RUTA SE CONSTRUYÓ SIN ÉL", ("sin", "él"), 0.4, y=0.88, size=56)], tex=ARCH)
    add(172.58, kb("u_ozevp_eAklI.jpg", "in", "cold"), [Badge("DÉCADA DE 1860", 0.2, None), big("NO HABÍA MÁQUINAS", 1.6, 0.84, 76, YELLOW, "pop")], tex=CLEAN)
    add(178.44, kb("l_3a36055.jpg", "in", "archival"), [rich("HACÍAN FALTA MILES DE BRAZOS", ("miles",), 0.3, y=0.86, size=56),
                                                       Caption("Campamento de construcción de la Central Pacific, 1869", None, 2.4, None, 0.95)], tex=ARCH)

    # ============================== CAP 2: LOS HOMBRES DE CROCKER (184.3 - 302.8)
    bg, ov = chapter(2, "Los hombres de Crocker", None, year="1865", base=st("1s00615", "in"))
    add(184.3, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(187.58, kb("u_N_nunvZZG88.jpg", "in", "sepia"), [LowerThird("CHARLES CROCKER", "Socio de la Central Pacific, a cargo de la obra", 0.2)], tex=ARCH)
    add(190.62, kb("u_5nCqLHKK468.jpg", "in", "dark"), [rich("AGUANTABAN POCO", ("poco",), 0.2, y=0.84, size=64)], tex=DARK)
    add(192.68, kb("u_uG3sjycquog.jpg", "in", "warm"), [rich("TRABAJABAN UNOS DÍAS Y COBRABAN…", ("cobraban…",), 0.2, y=0.84, size=56)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("minas", 196.4) - 0.6, kb("u_FYHn7Kobdw8.jpg", "in", "warm"), [Badge("A LAS MINAS DE PLATA DE NEVADA", 0.2, None)], tr="whip_l", td=0.2, tex=CLEAN)
    add(198.34, kb("u_SJvva-31YIk.jpg", "in", "cold"), [rich("ASÍ NO SE ABRE UNA MONTAÑA", ("montaña",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(201.26, kb("u_rNxfMnfnenE.jpg", "in", "sepia"), [Badge("PRINCIPIOS DE 1865", 0.2, None), rich("ALGO QUE PARECÍA UNA LOCURA", ("locura",), w("locura", 207.6) - 201.26 - 0.8, y=0.84, size=58)],
        tex=ARCH)
    add(209.10, st("1s00615", "punch"), [Stamp("TRABAJADORES CHINOS", 0.25, YELLOW, (0.5, 0.5), -6, 90),
                                          Caption("Campamento chino en Brown's Station · Alfred A. Hart", None, 1.2, None, 0.96)], tex=ARCH, post=postshake(2))
    add(211.26, st("1s00510", "l"), [rich("HUBO QUIEN DUDÓ DE QUE AGUANTARAN", ("dudó",), 0.3, y=0.88, size=54)], tex=ARCH)
    add(213.80, kb("u_DgugiZUfH9k.jpg", "in", "sepia"), [rich("CROCKER RESPONDIÓ CON UNA PREGUNTA", ("pregunta",), 0.3, y=0.84, size=54)], tex=ARCH)
    add(218.12, kb("u_vhKZvNFmpPU.jpg", "in", "warm"), [Darken(0.25), rich("«¿ACASO NO LEVANTARON ELLOS LA GRAN MURALLA?»", ("muralla?»",), 0.2, y=0.5, size=64, maxw=0.8)],
        tr="whip_r", td=0.25, tex=CLEAN)
    add(221.16, st("1s00566", "in"), [rich("LA PRUEBA SALIÓ BIEN", ("bien",), 0.3, y=0.88, size=58),
                                      Caption("Cantera de granito de Rocklin, Central Pacific · A. A. Hart", None, 1.4, None, 0.96)], tex=ARCH)
    t_pac = 225.34
    add(t_pac, mp("dp_pacific", [(0, 150.0, 30.0, 1.05), (11.3, 175.0, 31.0, 1.12)],
                  [dict(type="pin", at="taishan", t0=0.4, label="SUR DE CHINA", side="b", box=True, size=46),
                   dict(type="route", path=SEA_ROUTE, t0=w("pacifico", 230.4) - t_pac, draw=3.4, color=YELLOW, width=6, dash=26),
                   dict(type="pin", at=(-122.42, 37.77), t0=w("pacifico", 230.4) - t_pac + 3.0, label="SAN FRANCISCO", side="b"),
                   dict(type="label", at=(180.0, 28.0), text="OCÉANO PACÍFICO", t0=w("pacifico", 230.4) - t_pac + 0.6, size=56, color=(140, 180, 220))]),
        [Counter(0, 12000, "{:,.0f}", "HOMBRES", 0.3, 1.2, (0.5, 0.18), 140)], tr="zoom", td=0.35, tex=GFX)
    add(w("trabajo", 233.4) - 0.1, kb("u_x7Od4oNheYQ.jpg", "in", "warm"), [rich("TRABAJO Y UNA VIDA MEJOR", ("vida", "mejor"), 0.3, y=0.84, size=58)], tex=CLEAN)
    t_cq = 236.68
    add(t_cq, cus(G3.stats_panel, items=[("30–40", "HOMBRES POR CUADRILLA", 0.3), ("1", "CAPATAZ BLANCO", w("capataz", 239.4) - t_cq),
                                         ("8 H", "TURNOS DE DÍA Y DE NOCHE", w("turnos", 241.4) - t_cq)], title="ASÍ TRABAJABAN"), tr="fade", td=0.3, tex=GFX)
    add(245.30, kb("u_ZkcWw0wiTo0.jpg", "in", "dark"), [rich("PONTE EN SU LUGAR", ("su", "lugar"), 0.4, y=0.84, size=64)], tr="fade", td=0.4, tex=DARK)
    add(247.60, kb("u_x7Od4oNheYQ.jpg", "out", "cold"), [rich("HAS CRUZADO UN OCÉANO ENTERO", ("océano",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(w("idioma", 252.2) - 1.6, kb("u_U5fVbJbZPLc.jpg", "in", "warm"), [rich("CASI NADIE HABLA TU IDIOMA", ("idioma",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(253.50, kb("u_KyUTpclm8aw.jpg", "in", "cold"), [rich("UNA MONTAÑA HELADA", ("helada",), 0.2, y=0.84, size=60)], tex=CLEAN)
    add(w("agujeros", 255.4) - 0.2, kb("u_bkKSMn73KeQ.jpg", "punch", "bw"), tex=ARCH, post=postshake(2))
    add(257.62, kb("u_TRys9NU8GiQ.jpg", "in", "warm"), [rich("SOLO CONOCES A TU CUADRILLA", ("cuadrilla",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(260.54, kb("u_3JFVNo4ukKQ.jpg", "in", "warm"), [rich("LA PAGA, PARA TU FAMILIA AL OTRO LADO DEL MAR", ("familia",), 0.3, y=0.84, size=50, maxw=0.8)], tex=CLEAN)
    add(264.74, kb("u_l_s0dZ9NaxI.jpg", "in", "cold"), [rich("INVIERNO TRAS INVIERNO", ("invierno",), 0.3, y=0.84, size=62)], tex=CLEAN)
    add(269.40, cus(G5.wages, t2=w("mientras", 278.7) - 269.40), tr="fade", td=0.3, tex=GFX)
    add(282.66, kb("u_DgugiZUfH9k.jpg", "out", "sepia"), [Darken(0.4), Badge("GUARDA ESTE DETALLE", 0.2, None)], tex=ARCH)
    add(285.96, st("1s00615", "out"), [Darken(0.35), rich("NO SE CONSERVA NI EL NOMBRE", ("nombre",), 0.4, y=0.5, size=72)], tex=ARCH)
    add(290.14, kb("f_14222377592.jpg", "in", "archival"), [rich("LA HISTORIA NO APUNTÓ QUIÉNES ERAN", ("quiénes",), 1.2, y=0.88, size=52),
                                                           Caption("Comida de trabajadores chinos · SMU Libraries", None, 2.4, None, 0.96)], tex=ARCH)
    add(295.16, st("1s00509", "in"), [Badge("AGOSTO DE 1866", 0.2, None)], tex=ARCH)
    add(299.38, kb("u_YF6xCFF6JhU.jpg", "punch", "cold"), [big("EL GRANITO DE LA CUMBRE", 0.3, 0.84, 70)], tex=CLEAN)

    # ============================== CAP 3: A GOLPES CONTRA EL GRANITO (302.8 - 461.7)
    bg, ov = chapter(3, "A golpes contra el granito", None, year="1866–1867", base=st("1s00546", "in"))
    add(302.8, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(305.82, warp(G5.hand_drill, 0.0, 0.35), tr="fade", td=0.3, tex=GFX)
    add(317.78, warp(G5.hand_drill, 4.25, 0.28), tex=GFX)
    t_ex = w("explosion", 323.3)
    add(t_ex - 0.2, kb("u_NMRvHU8lSHI.jpg", "punch", "warm"), [Flash(0.0, 0.2, (255, 240, 220), 0.9)], tex=CLEAN, post=postshake(6))
    add(t_ex + 1.4, st("1s00510", "in"), [rich("SACAR LOS ESCOMBROS A MANO… Y OTRA VEZ", ("mano…",), 0.3, y=0.88, size=52, maxw=0.8)], tex=ARCH)
    add(327.54, warp(G5.tunnel6, 0.0, 0.8, mode="fronts"), tr="zoom", td=0.3, tex=GFX)
    add(334.94, warp(G5.tunnel6, 0.0, 0.62, mode="shaft"), tex=GFX)
    add(344.86, st("1s00545", "in"), [Caption("Casa del pozo sobre el túnel de la cumbre · Alfred A. Hart", None, 0.5)], tex=ARCH)
    add(348.02, kb("u_CgXwuXIdQic.jpg", "in", "warm"), [big("UNA LOCOMOTORA ENTERA · 12 TONELADAS", 0.3, 0.84, 58, YELLOW), Caption("Ilustración", None, 0.3, None, 0.96)], tex=CLEAN)
    add(353.02, kb("l_3a28342.jpg", "in", "archival"), [Counter(0, 10, "{:.0f}", "YUNTAS DE BUEYES", 0.2, 0.6, (0.5, 0.4), 170, sub="DURANTE 6 SEMANAS"),
                                                       Caption("Yuntas bajando de la cumbre por el camino de Donner Lake, 1866", None, 1.6, None, 0.96)], tex=ARCH)
    add(357.02, cus(G5.progress_bars, items=(("PÓLVORA NEGRA", 14, 0.3), ("NITROGLICERINA", 22, None))), tr="fade", td=0.3, tex=GFX)
    add(364.34, kb("u_4kuAvNfHEzI.jpg", "in", "dark"), [rich("UN DÍA ENTERO DE GOLPES…", ("golpes…",), 0.3, y=0.84, size=58),
                                                      rich("POCO MÁS QUE UNA REGLA", ("regla",), w("regla", 370.0) - 364.34 - 1.0, y=0.94, size=48)], tex=DARK)
    add(371.48, kb("u_k1Bhq14XVFQ.jpg", "in", "warm"), [Badge("FEBRERO DE 1867", 0.2, None), big("ALGO MUCHO MÁS POTENTE", 2.0, 0.84, 66, YELLOW, "pop")], tex=CLEAN)
    add(377.84, st("1s00517", "in"), [LowerThird("JAMES HOWDEN", "Químico británico · Donner Lake", 0.4)], tex=ARCH)
    add(w("nitroglacerina", 383.6) - 0.5, kb("u_wtPwGXUvgXU.jpg", "punch", "dark"), [big("NITROGLICERINA", 0.1, 0.17, 110, YELLOW, "pop")], tex=DARK, post=postshake(2))
    add(385.56, kb("u_DnBL5m9aQe8.jpg", "in", "doc"), [Counter(0, 100, "{:.0f}", "LIBRAS AL DÍA", w("100", 389.6) - 385.56, 0.8, (0.5, 0.42), 200, sub="≈ 45 KILOS"),
                                                     rich("UN TECHO DE TABLAS Y UNA OLLA VIEJA", ("olla",), 0.2, y=0.86, size=48)], tex=CLEAN)
    add(392.46, cus(G5.progress_bars, items=(("PÓLVORA NEGRA", 14, -2.0), ("NITROGLICERINA", 22, 0.3))), tr="fade", td=0.3, tex=GFX)
    add(398.36, kb("u_N_nunvZZG88.jpg", "in", "sepia"), [Badge("MAYO DE 1867", 0.2, None),
                                                       Counter(0, 681, "{:.0f}", "PIES POR ABRIR", w("681", 405.8) - 398.36, 0.9, (0.5, 0.42), 200)], tex=ARCH)
    add(408.20, kb("u_W-wCP4zdscI.jpg", "in", "warm"), [rich("EL FINAL SE VEÍA CERCA", ("cerca",), 0.3, y=0.84, size=60)], tex=CLEAN)
    add(w("claro", 410.4) - 0.1, kb("u_XySaPZljJ54.jpg", "punch", "warm"), [Flash(0.2, 0.2, (255, 240, 220), 0.8), big("MUCHÍSIMO MÁS PELIGROSA", 0.4, 0.84, 66, RED, "pop")],
        tex=CLEAN, post=postshake(5))
    add(415.20, kb("u_TFy7jIdLX7M.jpg", "in", "bw"), [Badge("SAN FRANCISCO · 1866", 0.2, None), rich("ESTALLA UN ENVÍO", ("estalla",), 0.8, y=0.84, size=62)], tex=ARCH)
    add(w("explosion", 419.4) - 0.3, kb("u_woPmQeB-xfY.jpg", "punch", "bw"), [Counter(0, 6, "{:.0f}", "TRABAJADORES MUERTOS", 0.6, 0.6, (0.5, 0.42), 220, color=RED)],
        tex=ARCH, post=postshake(4))
    add(424.04, kb("u_YRuTVMIKHdE.jpg", "in", "dark"), [Badge("NOVIEMBRE DE 1867", 0.2, None), rich("DEJA DE USARLA", ("deja",), 1.0, y=0.84, size=62)], tex=DARK)
    add(430.14, kb("u_rNxfMnfnenE.jpg", "in", "sepia"), [LowerThird("ALFRED NOBEL", "La patente de la nitroglicerina", 0.3)], tex=ARCH)
    add(434.56, kb("u_qefCF3r4Eoc.jpg", "in", "dark"), [Stamp("«QUE LA ENTIERREN»", w("enterraran", 439.4) - 434.56, RED, (0.5, 0.45), -8, 100)], tex=DARK)
    add(440.86, kb("u_l0WUe7VsIpI.jpg", "in", "dark"), [rich("ANTES DE CONTARTE LO QUE PASÓ EN LA CUMBRE…", ("cumbre…",), 0.3, y=0.84, size=52, maxw=0.8)], tex=DARK)
    add(446.62, kb("u_ynYlqQV4Qtk.jpg", "in", "dark"), [big("BAJAMOS A LOS TÚNELES", 0.1, 0.84, 70)], tex=DARK)
    add(w("subimos", 448.4) - 0.2, kb("u_F8qo72p7UOE.jpg", "in", "cold"), [big("SUBIMOS A LOS PUERTOS", 0.1, 0.84, 70)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("seguimos", 449.9) - 0.2, kb("u_Dezs_ZXuGEk.jpg", "in", "cold"), [big("SEGUIMOS LAS VÍAS QUE EL PAÍS DEJÓ ATRÁS", 0.1, 0.84, 58)], tr="whip_l", td=0.2, tex=CLEAN)
    add(452.16, st("1s00510", "out"), [rich("PARA QUE NO SE PIERDA QUIÉN LAS HIZO", ("quién",), 0.2, y=0.88, size=54)], tex=ARCH)
    add(w("suscribete", 456.4) - 1.8, kb("u_rO6bcXIMrPg.jpg", "in", "cold"), [Darken(0.35), FnOverlay(G2.subscribe)], tex=CLEAN)
    add(457.52 + 0.6, kb("u_oRepfU2n5tc.jpg", "in", "cold"), [rich("PEOR QUE EL GRANITO", ("peor",), 1.4, y=0.5, size=80)], tex=CLEAN, post=postshake(1))

    # ============================== CAP 4: EL ENEMIGO ERA LA NIEVE (461.7 - 663.1)
    bg, ov = chapter(4, "El enemigo era la nieve", "u_wRuZ-Nbl6mo.jpg", "cold", "1866–1867")
    add(461.7, bg, ov, tr="flash", td=0.25, tex=CLEAN)
    add(w("enemigo", 464.4) - 0.2, kb("u_8hxD_7dKHeo.jpg", "down", "cold"), [big("ESTABA ENCIMA", 0.6, 0.84, 76, YELLOW, "pop")], tex=CLEAN)
    add(w("cayeron", 471.6) - 0.3, cus(G5.storms, every=0.07), tr="fade", td=0.3, tex=GFX)
    add(475.38, kb("u_7EyTL50ZXfQ.jpg", "in", "cold"), [Counter(0, 18, "{:.0f}", "PIES DE NIEVE DE MEDIA", w("18", 478.0) - 475.38, 0.8, (0.5, 0.42), 220, sub="MÁS DE 5 METROS")],
        tex=CLEAN)
    t_cal = 480.94
    add(t_cal, cus(G4.calendar, cards=[("18", "FEB 1867", "EMPIEZA", w("18", 485.0) - t_cal, SNOWC), ("2", "MAR 1867", "TERMINA", w("2", 487.4) - t_cal, SNOWC)],
                   title="LA PEOR TORMENTA: CASI DOS SEMANAS"), tr="fade", td=0.3, tex=GFX)
    add(489.62, cus(G5.snow_corridor), tr="fade", td=0.3, tex=GFX)
    add(496.76, kb("u_YdT7VwTn5TM.jpg", "in", "cold"), [rich("DOS VECES BAJO TIERRA", ("dos", "veces"), 0.3, y=0.84, size=62)], tex=CLEAN)
    add(w("dentro", 500.6) - 0.2, Split([kb("u_Rm9tpyYDHHY.jpg", "in", "cold"), st("1s00546", "in")], labels=["PARA DORMIR: NIEVE", "PARA TRABAJAR: ROCA"]), tex=CLEAN)
    add(504.80, kb("u_jHJdVMHLuug.jpg", "in", "bw"), [rich("LOS BRAZOS DESTROZADOS", ("destrozados",), 0.8, y=0.84, size=60)], tr="fade", td=0.3, tex=ARCH)
    add(509.66, kb("u_l0WUe7VsIpI.jpg", "in", "cold"), [torch(((0.5, 0.7), (0.5, 0.4)), r=460, amb=0.15), rich("UN TÚNEL BLANCO HASTA UN CATRE HELADO", ("helado",), 1.2, y=0.84, size=52)],
        tex=DARK)
    add(514.96, kb("u_0Si1n-fgw8w.jpg", "punch", "warm"), [big("VUELTA A EMPEZAR", 0.2, 0.84, 70)], tex=CLEAN, post=postshake(2))
    add(517.98, kb("u_wbPCr5CZADg.jpg", "in", "cold"), [big("LAS AVALANCHAS", 0.3, 0.84, 84, RED, "pop")], tex=CLEAN, post=postshake(3))
    add(520.32, st("1s00582", "in"), [Caption("Túnel n.º 12, Strong's Canyon · Alfred A. Hart", None, 0.3)], tex=ARCH)
    add(522.96, kb("u_6Oovj0oGjRQ.jpg", "punch", "cold"), [Flash(0.4, 0.4, (255, 255, 255), 0.9), rich("CUADRILLAS ENTERAS", ("enteras",), 1.0, y=0.84, size=64)],
        tex=CLEAN, post=postshake(8))
    add(529.36, kb("u_wHccjtern38.jpg", "in", "cold"), [rich("HASTA LA PRIMAVERA", ("primavera",), 0.6, y=0.84, size=62)], tr="fade", td=0.6, tex=CLEAN)
    add(532.74, kb("u_R8_y8pSf-bg.jpg", "in", "dark"), [Darken(0.5)] + question("¿Cuántos murieron ese invierno en la Sierra?", ("cuántos",), size=76), tex=DARK)
    add(535.04, kb("u_aVNcT0obqtQ.jpg", "in", "cold"), [rich("NADIE LO SABE CON EXACTITUD", ("nadie",), 0.2, y=0.42, size=60),
                                                      rich("HOMBRES QUE NADIE CONTÓ", ("contó",), 1.6, y=0.58, size=72)], tex=CLEAN)
    add(540.54, kb("u_0BxnugVcdhM.jpg", "up", "doc"), [rich("UN MURO DE PIEDRA SECA, A MANO", ("mano",), 0.3, y=0.2, size=56),
                                                     Counter(0, 75, "{:.0f} PIES", "DE ALTO", w("75", 545.0) - 540.54, 0.8, (0.5, 0.55), 180, sub="MÁS DE 20 METROS")],
        tr="fade", td=0.3, tex=CLEAN)
    add(548.18, kb("f_6970075417.jpg", "in", "cold"), [rich("PARA SOSTENER LA VÍA EN LA LADERA", ("ladera",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(551.72, kb("u__Ppf7roueMA.jpg", "in", "doc"), [big("SIN CEMENTO · PIEDRA SOBRE PIEDRA", 0.2, 0.84, 62)], tex=CLEAN)
    t_cw = w("china", 556.6)
    add(554.34, kb("f_6823951250.jpg", "in", "cold"),
        [BigText("CHINA WALL", "bebas", 150, WHITE, (0.5, 0.42), t_cw - 554.34, None, "pop", tracking=10),
         BigText("«el muro de los chinos»", "serif_it", 60, YELLOW, (0.5, 0.56), t_cw - 554.34 + 0.8, None, "up")], tex=CLEAN)
    add(559.68, st("1s00550", "in"), [rich("SE RETIRA LA NIEVE… Y LLEGA OTRA PELEA", ("pelea",), 0.3, y=0.88, size=52, maxw=0.8)], tex=ARCH)
    add(564.60, cus(G4.calendar, cards=[("24", "JUN 1867", "HUELGA", 0.2, RED)], title="ESTA VEZ, CON LA COMPAÑÍA"), tr="fade", td=0.3, tex=GFX)
    t_hm = 567.92
    add(t_hm, mp("dp_sierra", [(0, -120.4, 39.32, 1.5), (9.1, -120.37, 39.32, 1.6)],
                 [dict(type="route", path=["cisco", "norden", "tunnel6", "donner_lake", "truckee"], t0=0.3, draw=2.0, color=RED, width=10),
                  dict(type="pin", at="cisco", t0=w("cisco", 575.4) - t_hm, label="CISCO", side="b"),
                  dict(type="pin", at="truckee", t0=w("truckee", 576.2) - t_hm, label="TRUCKEE", side="b"),
                  dict(type="label", at=(-120.38, 39.42), text="30 MILLAS · 48 KM", t0=w("30", 571.6) - t_hm, size=54, box=True)]),
        [Counter(0, 3000, "{:,.0f}", "TRABAJADORES CHINOS EN HUELGA", 0.4, 1.2, (0.5, 0.16), 130)], tr="zoom", td=0.3, tex=GFX)
    t_dm = 577.02
    add(t_dm, cus(G3.stats_panel, items=[("$40", "AL MES", 0.2), ("10 H", "Y NO 11", w("10", 579.6) - t_dm), ("−", "HORAS EN LOS TÚNELES", w("turnos", 582.0) - t_dm)],
                  title="LO QUE PEDÍAN"), tr="fade", td=0.3, tex=GFX)
    add(584.42, kb("u_rNxfMnfnenE.jpg", "in", "sepia"), [Stamp("NO CEDIÓ EN NADA", 0.3, RED, (0.5, 0.48), -8, 100)], tex=ARCH, post=postshake(2))
    add(586.66, kb("u_EBxCFAdfEac.jpg", "in", "dark"), [rich("SIN SUMINISTROS", ("sin",), 0.3, y=0.84, size=64)], tex=DARK)
    add(588.76, kb("u_Mx3tCAyN0vI.jpg", "in", "warm"), [Stamp("−1 MES DE PAGA", 1.6, RED, (0.5, 0.5), -8, 100)], tex=CLEAN)
    add(593.20, st("1s00566", "out"), [rich("UNA SEMANA DESPUÉS, DE VUELTA AL TRABAJO", ("vuelta",), 0.3, y=0.88, size=52, maxw=0.8)], tex=ARCH)
    add(595.78, kb("u_uG3sjycquog.jpg", "in", "warm"), [rich("Y LUEGO, SIN ANUNCIARLO, SUBIERON EL SUELDO", ("sueldo",), 0.3, y=0.84, size=50, maxw=0.8)], tex=CLEAN)
    add(599.82, st("1s00615", "out"), [Darken(0.35), rich("UNA DE LAS MAYORES HUELGAS DE SU ÉPOCA", ("mayores",), 0.2, y=0.42, size=58, maxw=0.8),
                                       rich("Y HOY CASI NADIE LA RECUERDA", ("nadie",), 2.7, y=0.58, size=62)], tex=ARCH)
    add(604.90, kb("u_u6zVikMNTmQ.jpg", "in", "warm"), [rich("GOLPE A GOLPE", ("golpe",), 0.4, y=0.84, size=70)], tex=CLEAN)
    add(609.28, warp(G5.tunnel6, 0.0, 0.62, mode="meet"), tr="zoom", td=0.3, tex=GFX)
    add(625.44, warp(G5.tunnel6, 0.0, 0.7, mode="depth"), tex=GFX)
    add(633.52, st("1s00521", "in"), [Badge("PRIMAVERA DE 1868", 0.4, None), rich("LA VÍA, CASI LISTA", ("lista",), 2.4, y=0.88, size=56)], tr="fade", td=0.3, tex=ARCH)
    add(639.56, kb("f_6823968520.jpg", "in", "cold"), [rich("EL HIELO HABÍA TAPADO LOS TÚNELES", ("hielo",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(643.50, kb("l_3a27839.jpg", "in", "archival"), [rich("EXPLOSIVOS Y PALA, OTRA VEZ", ("pala",), 0.3, y=0.86, size=56)], tex=ARCH)
    add(646.16, kb("u_ATvkjM2a5Xk.jpg", "out", "cold"), [TimelineBar(1865, 1868, 0.2, (0.3, 2.4), 1865), big("CASI TRES AÑOS", 0.6, 0.4, 96, YELLOW, "pop")], tex=CLEAN)
    add(650.22, st("1s53975", "in"), [Badge("18 DE JUNIO DE 1868", 0.2, None), rich("PASA EL PRIMER TREN DE PASAJEROS", ("primer",), 1.6, y=0.88, size=54)], tex=ARCH)
    add(655.76, st("1s00547", "out"), [big("HABÍAN VENCIDO AL GRANITO", 0.1, 0.84, 70, YELLOW)], tex=ARCH)
    add(657.60, kb("u_HwoBnQNUqCQ.jpg", "in", "cold"), [rich("PERO LA NIEVE NO SE HABÍA IDO", ("nieve",), 0.2, y=0.84, size=60)], tex=CLEAN)
    add(660.38, vid("ThisIsMy1940_2", 346.0, 2.9, "cold"), [rich("CADA INVIERNO, OTRA VEZ", ("invierno",), 0.3, y=0.84, size=60)], tex=FILM)

    # ============================== CAP 5: UNA VÍA BAJO TECHO (663.1 - 784.2)
    bg, ov = chapter(5, "Una vía bajo techo", None, year="1868–1952", base=st("1s00577", "in"))
    add(663.1, bg, ov, tr="flash", td=0.25, tex=ARCH)
    add(667.0, kb("l_56317.jpg", "in", "archival"), [big("TECHÓ LA VÍA", 0.2, 0.84, 80, YELLOW, "pop"),
                                                    Caption("La cumbre con los cobertizos y Donner Lake al fondo, 1868", None, 0.9, None, 0.96)], tex=ARCH)
    add(w("cobertizos", 669.4) - 0.6, cus(G5.snowshed), tr="zoom", td=0.3, tex=GFX)
    add(676.66, st("1s00575", "in"), [rich("UN GRANERO INTERMINABLE CON UN TREN DENTRO", ("granero",), 0.3, y=0.88, size=52, maxw=0.8)], tr="fade", td=0.3, tex=ARCH)
    add(680.98, mp("dp_sierra", [(0, -120.5, 39.3, 1.3), (4.7, -120.45, 39.3, 1.4)],
                   [dict(type="route", path=["emigrant_gap", "yuba_gap", "cisco", "norden", "tunnel6", "donner_lake", "truckee"], t0=0.2, draw=2.0,
                         color=(186, 140, 90), width=14)]),
        [Counter(0, 37, "{:.0f} MILLAS", "DE VÍA BAJO TECHO", 0.4, 1.2, (0.5, 0.16), 140, sub="≈ 60 KM EN UNOS 3 AÑOS")], tr="fade", td=0.3, tex=GFX)
    add(685.72, st("1s00574", "in"), [rich("MADERA LABRADA A MANO", ("mano",), 0.3, y=0.88, size=58)], tex=ARCH)
    add(690.82, kb("u_uG3sjycquog.jpg", "punch", "warm"), [Counter(0, 2000000, "+${:,.0f}", "DÓLARES DE LA ÉPOCA", 0.2, 1.2, (0.5, 0.45), 150)], tex=CLEAN)
    add(693.88, cus(G3.document, lines=[("SACRAMENTO, 1868", 50), ("", 20), ("LOS COBERTIZOS", 50), ("SE PAGARÁN SOLOS", 50), ("EN UN SOLO INVIERNO.", 50), ("", 20),
                                        ("E. B. CROCKER", 40)], sign_t=4.6), [Caption("Recreación", None, 0.4, None, 0.95)], tr="fade", td=0.3, tex=GFX)
    add(700.46, st("1s00579", "in"), [Badge("INVIERNO DE 1869", 0.2, None),
                                      Counter(0, 4, "{:.0f}", "DÍAS CORTADA", w("cuatro", 703.8) - 700.46, 0.6, (0.5, 0.45), 220)], tex=ARCH)
    t_ut = 705.78
    add(t_ut, mp("dp_us", [(0, -112.0, 40.6, 1.4), (3.2, -112.5, 41.2, 1.7)],
                 [dict(type="route", path=CP_ROUTE, t0=-5, draw=0.01, color=YELLOW, width=7),
                  dict(type="route", path=UP_ROUTE, t0=-5, draw=0.01, color=WHITE, width=6),
                  dict(type="pin", at="promontory", t0=0.4, label="PROMONTORY · UTAH", side="r", box=True, size=46)]), tr="zoom", td=0.3, tex=GFX)
    add(708.92, fr("l_3c16354.jpg", "Celebración del ferrocarril transcontinental, 1869"), [big("DE COSTA A COSTA", 0.4, 0.1, 62, YELLOW)], tex=ARCH)
    add(712.40, vid("ThisIsMy1940", 429.0, 3.8, "faded"), [Badge("DÉCADA TRAS DÉCADA", 0.2, None)], tex=FILM)
    add(716.18, vid("ThisIsMy1940", 294.0, 3.0, "faded"), [rich("SE QUEDÓ CORTO", ("corto",), 0.3, y=0.84, size=62)], tex=FILM)
    add(719.24, kb("l_315581p.jpg", "in", "archival"), [Badge("1925 · SOUTHERN PACIFIC", 0.2, None),
                                                      Caption("Túnel n.º 41, el túnel largo de 1925 · HAER, Library of Congress", None, 1.6, None, 0.95)], tex=ARCH)
    add(726.86, warp(G5.tunnel6, 0.0, 0.5, mode="two"), tr="zoom", td=0.3, tex=GFX)
    add(739.94, vid("ThisIsMy1940_2", 428.0, 2.2, "cold"), [rich("LA NIEVE SEGUÍA MANDANDO", ("mandando",), 0.2, y=0.84, size=58)], tex=FILM)
    add(742.14, kb("u_liBqA_qgbA4.jpg", "in", "cold"), [Badge("13 DE ENERO DE 1952", 0.2, None), big("EN PLENA VENTISCA", 1.8, 0.84, 70)], tex=CLEAN, post=postshake(2))
    add(746.84, kb("l_3c32393.jpg", "in", "archival"), [LowerThird("CITY OF SAN FRANCISCO", "Uno de los trenes más famosos del país", 0.3)], tex=ARCH)
    t_yg = 749.56
    add(t_yg, mp("dp_sierra", [(0, -120.48, 39.31, 1.6), (4.8, -120.48, 39.31, 1.7)],
                 [dict(type="route", path=SIERRA_ROUTE[3:], t0=-5, draw=0.01, color=(160, 160, 160), width=5),
                  dict(type="pin", at="tunnel6", t0=0.0, label="DONNER PASS", side="r", pulse=False),
                  dict(type="pin", at="yuba_gap", t0=0.5, label="YUBA GAP", side="l", color=RED, box=True),
                  dict(type="route", path=["yuba_gap", "cisco", "norden", "tunnel6"], t0=1.0, draw=1.4, color=RED, width=5, dash=18),
                  dict(type="label", at=(-120.47, 39.36), text="17 MILLAS AL OESTE", t0=1.8, size=50, box=True)]), tr="fade", td=0.3, tex=GFX)
    add(754.38, vid("ThisIsMy1940_2", 364.2, 5.3, "cold"), [Counter(0, 222, "{:.0f}", "PERSONAS A BORDO", w("222", 757.0) - 754.38, 0.8, (0.5, 0.42), 220)], tex=CLEAN)
    add(759.60, kb("u_FWunh_ntoGI.jpg", "in", "cold"), [Counter(0, 3, "{:.0f}", "DÍAS ATRAPADOS", 0.2, 0.5, (0.5, 0.42), 220)], tex=CLEAN)
    add(761.52, kb("u_u7hKg-Lgzm0.jpg", "in", "cold"), [rich("ABRIR LA CARRETERA Y SACARLOS EN AUTO", ("auto",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(765.14, cus(G5.snow_depth, inches=800, peak=None, title="INVIERNO DE 1951-1952"), tr="fade", td=0.3, tex=GFX)
    add(769.46, kb("u_e8wlIgQyiv8.jpg", "in", "cold"), [big("NUNCA SE RINDIÓ DEL TODO", 0.6, 0.84, 70)], tex=CLEAN)
    add(773.38, vid("ThisIsMy1940_2", 439.0, 3.1, "cold"), [rich("CADA INVIERNO COSTABA UN POCO MÁS", ("más",), 0.3, y=0.84, size=56)], tex=FILM)
    add(776.50, vid("ThisIsMy1940_2", 583.0, 3.8, "cold"), tex=FILM)
    add(780.36, kb("u_N_nunvZZG88.jpg", "in", "sepia"), [rich("ALGUIEN IBA A SENTARSE A HACER NÚMEROS", ("números",), 0.3, y=0.84, size=54, maxw=0.8)], tex=ARCH)

    # ============================== CAP 6: EL ABANDONO (784.2 - 954.9)
    bg, ov = chapter(6, "El abandono", "f_6823963454.jpg", "dark", "1993")
    add(784.2, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(787.42, kb("f_6970078769.jpg", "in", "cold"), [Badge("1993 · SOUTHERN PACIFIC", 0.2, None), rich("DEJA DE USAR LA VÍA VIEJA", ("vieja",), 1.6, y=0.84, size=58)], tex=CLEAN)
    t_ab = 792.96
    add(t_ab, mp("dp_loc", [(0, -120.31, 39.312, 1.2), (11.8, -120.31, 39.31, 1.3)],
                 [dict(type="route", path=OLD_LINE, t0=0.2, draw=2.0, color=RED, width=9),
                  dict(type="pin", at="norden", t0=0.1, label="NORDEN", side="t"),
                  dict(type="pin", at=OLD_LINE[-1], t0=1.8, label="COBERTIZO 47", side="b"),
                  dict(type="pin", at="tunnel6", t0=0.8, label="TÚNEL 6", side="t", color=WHITE, pulse=False),
                  dict(type="label", at=(-120.31, 39.335), text="≈ 7 MILLAS · 11 KM", t0=2.4, size=54, box=True),
                  dict(type="route", path=NEW_TUNNEL, t0=w("trafico", 799.0) - t_ab, draw=1.6, color=YELLOW, width=9, dash=20, smooth=False),
                  dict(type="label", at=(-120.32, 39.298), text="TÚNEL DE 1925", t0=w("trafico", 799.0) - t_ab + 1.0, size=46, color=YELLOW)]),
        tr="zoom", td=0.3, tex=GFX)
    add(804.72, st("1s00142", "in"), [rich("DEMASIADO CARO, INVIERNO TRAS INVIERNO", ("caro",), 0.3, y=0.88, size=52, maxw=0.8)],
        tex=ARCH)
    add(812.60, kb("u_V5QEkJL3O3c.jpg", "in", "dark"), [rich("SIN CEREMONIA NI DISCURSOS", ("ceremonia",), 0.3, y=0.84, size=58)], tr="fade", td=0.4, tex=DARK)
    add(815.82, kb("f_6823954790.jpg", "in", "cold"), [Counter(0, 125, "{:.0f} AÑOS", "DE TRENES", 0.4, 1.0, (0.5, 0.42), 200)], tex=CLEAN)
    add(820.98, kb("u_yEvnB6YDd88.jpg", "out", "bw"), [rich("LOS RIELES DESAPARECIERON", ("desaparecieron",), 0.3, y=0.84, size=58)], tex=ARCH)
    add(824.00, kb("f_6970091341.jpg", "in", "none"), [torch(((0.2, 0.5), (0.8, 0.5)), r=440), rich("UN PASILLO DE GRANITO", ("granito",), 1.2, y=0.84, size=58)], tex=DARK)
    add(829.14, kb("u_DEdnviFTeZE.jpg", "punch", "warm"), [torch(((0.4, 0.5), (0.6, 0.5)), r=520, amb=0.12), big("LAS MARCAS DE LOS BARRENOS", 0.6, 0.84, 62, YELLOW)], tex=CLEAN)
    add(832.14, kb("f_6970092315.jpg", "in", "cold"), [Badge("CASI UN TERCIO DE MILLA", w("tercio", 837.4) - 832.14, None)], tex=CLEAN)
    add(838.52, kb("u_nv_CLuGKJ-Q.jpg", "out", "dark"), [rich("LA LUZ DE AFUERA DESAPARECE", ("desaparece",), 0.3, y=0.84, size=58)], tex=DARK)
    add(842.10, kb("u_rHBKXaEAJfI.jpg", "in", "cold"), [FnOverlay(G4.drips, n=40), rich("GOTEA · HACE FRÍO", ("frío",), 0.3, y=0.84, size=62)], tex=CLEAN)
    add(845.86, kb("f_6823968520.jpg", "in", "cold"), [rich("EL HIELO SE CUELA POR LAS BOCAS", ("hielo",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(848.74, kb("u_KMAqr5CE-X8.jpg", "in", "cold"), [rich("COMO SI LA MONTAÑA QUISIERA CERRARLO", ("cerrarlo",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(851.78, kb("u_6i3O_w7wOyE.jpg", "in", "dark"), [rich("SOLO TU LINTERNA", ("linterna",), 0.3, y=0.84, size=64)], tex=DARK)
    add(855.06, kb("f_6970089625.jpg", "in", "cold"), [rich("VACÍO NO SE QUEDÓ MUCHO TIEMPO", ("vacío",), 0.3, y=0.84, size=56)], tex=CLEAN)
    add(858.04, kb("u_78gHd4C9aR8.jpg", "in", "doc"), [big("EXCURSIONISTAS", 0.1, 0.84, 76)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("ciclistas", 859.9) - 0.2, kb("u_b31n8E5C6HE.jpg", "in", "doc"), [big("CICLISTAS", 0.1, 0.84, 76)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("curiosos", 861.2) - 0.3, kb("f_6823957298.jpg", "in", "doc"), [big("CURIOSOS", 0.1, 0.84, 76)], tr="whip_l", td=0.2, tex=CLEAN)
    add(862.22, kb("u_tUXzeXh_JU8.jpg", "punch", "doc"), [big("Y LOS AEROSOLES", 0.2, 0.84, 80, RED, "pop")], tr="glitch", td=0.25, tex=CLEAN)
    add(864.26, kb("f_8306417343.jpg", "in", "doc"), [Badge("2021 · ALERTA DE PATRIMONIO HISTÓRICO", 0.2, None),
                                                    rich("EL VANDALISMO Y EL GRAFITI DAÑAN LOS TÚNELES", ("grafiti",), w("vandalismo", 869.8) - 864.26, y=0.84, size=52, maxw=0.8)],
        tex=CLEAN)
    add(873.86, kb("u_NryPG6WPPho.jpg", "in", "dark"), [Darken(0.55), Badge("PREGUNTA 2", 0.2, None)] +
        question("¿Por qué, entre tantos nombres pintados, no está el de ninguno de los que lo cavaron?", ("ninguno",), size=66), tr="glitch", td=0.3, tex=DARK)
    add(883.74, Solid("black"), [BigText("NO ES CASUALIDAD", "serif", 110, WHITE, (0.5, 0.5), 0.1, None, "pop")], tex=DARK)
    t_pay = 885.28
    add(t_pay, cus(G5.payroll, hl_t=w("john", 900.5) - t_pay), tr="fade", td=0.3, tex=GFX)
    add(904.34, kb("u_B6yDtYs2IgY.jpg", "in", "sepia"), [Darken(0.3), rich("NI UNA CARTA · NI UN DIARIO", ("carta", "diario"), 0.3, y=0.5, size=72)], tex=ARCH)
    add(908.52, kb("u_DgugiZUfH9k.jpg", "out", "sepia"), [rich("NADIE MÁS LO IBA A HACER", ("nadie",), 0.6, y=0.84, size=62)], tex=ARCH)
    add(913.34, kb("l_3b07534.jpg", "in", "bw"), [big("EL OLVIDO LLEGÓ HASTA LA FOTO", 0.2, 0.1, 62, YELLOW)], tr="fade", td=0.4, tex=ARCH)
    add(915.86, kb("l_3a10360.jpg", "in", "archival"), [Badge("10 DE MAYO DE 1869 · PROMONTORY, UTAH", 0.2, None)], tex=ARCH)
    add(921.80, kb("l_3b07534.jpg", "punch", "bw"), [rich("LA IMAGEN MÁS FAMOSA DE TODA LA OBRA", ("famosa",), 0.3, y=0.1, size=52, maxw=0.8),
                                                   FnOverlay(G5.missing, t0=w("esa", 929.0) - 921.80)], tex=ARCH)
    add(932.98, kb("l_28462.jpg", "in", "archival"), [Badge("1882 · LEY DE EXCLUSIÓN CHINA", 0.2, None),
                                                     Caption("«The anti-Chinese wall», caricatura de 1882", None, 1.4, None, 0.96)], tex=ARCH)
    add(939.24, fr("l_11861.jpg", "«The only one barred out», caricatura de 1882"), [rich("LES CERRABA LA PUERTA", ("puerta",), 0.4, y=0.1, size=56)], tex=ARCH)
    t_ex = 942.28
    add(t_ex, cus(G4.timeline, events=[(1869, "PROMONTORY", 0.2), (1882, "LEY DE EXCLUSIÓN", 0.4), (1943, "DEROGADA", 0.8)], hi=1882, red=(1882,),
                  title="EN VIGOR", y0=1860, y1=1960),
        [FnOverlay(G4.span_bar, ya=1882, yb=1943, text="61 AÑOS", t0=0.5, y1940=1860, y2000=1960)], tr="fade", td=0.3, tex=GFX)
    add(944.68, kb("f_6970088001.jpg", "in", "none"), [torch(((0.3, 0.5), (0.7, 0.5)), r=420), rich("NI UNA LÍNEA PARA ELLOS", ("línea",), 1.6, y=0.84, size=62)], tex=DARK)
    add(949.92, st("1s00510", "in", 1.1), [rich("HASTA QUE ALGUIEN DECIDIÓ ACORDARSE", ("acordarse",), 0.6, y=0.88, size=54)], tr="fade", td=0.4, tex=ARCH)

    # ============================== CAP 7: HOY (954.9 - 1058.6)
    bg, ov = chapter(7, "Hoy", "l_13375.jpg", "warm", "2019–2026")
    add(954.9, bg, ov, tr="flash", td=0.25, tex=CLEAN)
    add(957.18, kb("u_zA0YZfEZplA.jpg", "in", "warm"), [Badge("MAYO DE 2019 · 150 AÑOS", 0.2, None),
                                                      rich("SUS DESCENDIENTES VUELVEN A PROMONTORY", ("descendientes",), 1.4, y=0.84, size=52, maxw=0.8)], tex=CLEAN)
    add(963.18, kb("l_13376.jpg", "in", "warm") if os.path.exists(os.path.join(ROOT, "assets", "img", "l_13376.jpg")) else kb("l_13375.jpg", "out", "warm"),
        [rich("PARA REPETIR AQUELLA FOTO", ("foto",), 0.2, y=0.42, size=60), rich("ESTA VEZ, CON ELLOS DENTRO", ("ellos", "dentro"), w("esta", 966.6) - 963.18, y=0.58, size=72)],
        tex=CLEAN)
    add(968.76, kb("f_51825887422.jpg", "in", "archival"), [rich("Y UNO DE LOS RECONOCIMIENTOS, EN ESTA MONTAÑA", ("montaña",), 0.3, y=0.86, size=50, maxw=0.8)], tex=ARCH)
    t_rc = 974.40
    add(t_rc, cus(G4.calendar, cards=[("2024", "ASCE", "HITO DE LA INGENIERÍA CIVIL", 0.2, GREEN)], title="TÚNEL N.º 6"), tr="fade", td=0.3, tex=GFX)
    add(982.52, st("1s00508", "in"), [Badge("DIC. 2024 · MONUMENTO HISTÓRICO NACIONAL", 0.2, None),
                                      BigText("SUMMIT CAMP", "bebas", 120, WHITE, (0.5, 0.45), w("summit", 992.3) - 982.52, None, "pop", tracking=8),
                                      Caption("Campamento junto al túnel de la cumbre · Alfred A. Hart", None, 1.0, None, 0.96)], tex=ARCH)
    t_pl = 993.56
    add(t_pl, cus(G4.calendar, cards=[("2024", "ASCE", "TÚNEL 6", 0.0, GREEN), ("DIC", "2024", "SUMMIT CAMP", 0.0, GREEN), ("10", "AGO 2025", "UNA PLACA", 0.3, YELLOW)]),
        tr="fade", td=0.3, tex=GFX)
    add(w("descubrio", 1002.4) - 0.3, kb("u_UeoVTVxXSho.jpg", "in", "warm"), [rich("SUS NOMBRES, POR FIN, EN LA PIEDRA", ("nombres",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(1003.64, kb("f_6970075417.jpg", "out", "cold"), [Badge("RECORRIDOS GUIADOS", 0.2, None),
                                                        BigText("CHINA WALL", "bebas", 140, WHITE, (0.5, 0.45), w("china", 1010.8) - 1003.64, None, "pop", tracking=10)], tex=CLEAN)
    add(1012.58, kb("f_6823954790.jpg", "out", "cold"), [Badge("2026", 0.2, None), rich("SIN RIELES Y SIN TRENES", ("sin",), 3.0, y=0.84, size=60)], tex=CLEAN)
    add(1019.90, kb("f_32304744153.jpg", "in", "faded"), [rich("ABAJO, LOS TRENES DE CARGA SIGUEN PASANDO", ("carga",), 0.3, y=0.86, size=52, maxw=0.8)], tex=CLEAN)
    t_i80 = 1025.24
    add(t_i80, mp("dp_loc", [(0, -120.31, 39.32, 1.25), (6.3, -120.3, 39.32, 1.35)],
                  [dict(type="road", name="80", level="Interstate", bbox=(-120.45, 39.26, -120.15, 39.37), t0=0.3, draw=1.2, color=YELLOW, width=8, traffic=18, speed=180),
                   dict(type="label", at=(-120.25, 39.345), text="INTERESTATAL 80", t0=0.9, size=50, box=True),
                   dict(type="pin", at="tunnel6", t0=2.0, label="TÚNEL 6", side="b", color=WHITE)]), tr="zoom", td=0.3, tex=GFX)
    add(1031.60, kb("u_NII3TsVdwZA.jpg", "in", "night"), [rich("LA MAYORÍA NO LO SABE", ("no",), 0.3, y=0.84, size=62)], tex=DARK)
    add(1035.74, kb("u_XZuqMUiSdgc.jpg", "in", "warm"), [rich("UN TÚNEL ABIERTO A GOLPES DE MAZO", ("mazo",), 0.3, y=0.84, size=58)], tex=CLEAN)
    add(1039.28, kb("u_fp8Cxb88AMQ.jpg", "in", "none"), [torch(((0.3, 0.5), (0.7, 0.5)), r=430), rich("OSCURIDAD · FRÍO · PINTURA", ("pintura",), 2.0, y=0.84, size=62)], tex=DARK)
    add(1047.58, kb("u_DEdnviFTeZE.jpg", "in", "warm"), [torch(((0.35, 0.5), (0.65, 0.5)), r=520, amb=0.12),
                                                       rich("LA FIRMA DE VERDAD DEL TÚNEL", ("firma",), 1.8, y=0.84, size=60)], tex=CLEAN)
    add(1054.32, kb("u_cRDUjKh6Xj0.jpg", "in", "dark"), [rich("YA PODEMOS RESPONDER", ("responder",), 0.4, y=0.5, size=80)], tr="fade", td=0.4, tex=DARK)

    # ============================== CONCLUSIÓN (1058.6 - end)
    q1(1058.5)
    add(1062.70, vid("ThisIsMy1940", 1052.0, 4.2, "faded"), [big("NO PORQUE FALLARA", 0.1, 0.2, 76, WHITE, "pop"),
                                                             Counter(0, 125, "{:.0f} AÑOS", "DE TRENES", 1.0, 0.9, (0.5, 0.62), 170)], tex=FILM)
    add(1067.02, vid("ThisIsMy1940_2", 501.0, 3.2, "cold"), [rich("LA MONTAÑA NUNCA DEJÓ DE COBRAR", ("cobrar",), 0.3, y=0.84, size=58)], tex=FILM)
    add(1070.22, warp(G5.tunnel6, 3.0, 1.0, mode="two"), [Badge("MÁS BARATO PASAR POR DEBAJO", 0.3, None)], tr="fade", td=0.3, tex=GFX)
    add(1076.30, st("1s00510", "punch"), [big("EL GRANITO LO VENCIERON UNOS HOMBRES A MANO", 0.2, 0.86, 54, YELLOW)], tex=ARCH)
    add(1079.04, kb("u_IuSemNxGS88.jpg", "in", "cold"), [big("LA NIEVE NO LA VENCIÓ NADIE", 0.1, 0.5, 86, WHITE, "pop")], tex=CLEAN, post=postshake(2))
    add(1081.08, st("1s00547", "in"), [rich("NO FUE SOLO UNA VÍA VIEJA", ("vieja",), 2.0, y=0.88, size=58)], tr="fade", td=0.4, tex=ARCH)
    add(1086.18, fr("l_3c16354.jpg"), [rich("UNA DE LAS OBRAS MÁS DIFÍCILES DEL TRANSCONTINENTAL", ("difíciles",), 0.3, y=0.1, size=48, maxw=0.85)], tex=ARCH)
    add(1093.64, kb("u_RkjuiI6N8fg.jpg", "in", "doc"), [rich("UN TÚNEL LLENO DE NOMBRES…", ("nombres…",), 0.3, y=0.42, size=64),
                                                      rich("MENOS LOS DE QUIENES LO CAVARON", ("cavaron",), w("menos", 1097.4) - 1093.64, y=0.58, size=64)], tex=CLEAN)
    add(1099.50, kb("f_6823964782.jpg", "in", "none"), [torch(((0.3, 0.55), (0.6, 0.45)), r=420), rich("NO ES LA PINTURA", ("pintura",), 2.6, y=0.84, size=64)], tex=DARK)
    add(1105.68, fr("l_1s00546_L.jpg", "Túnel de la cumbre · Alfred A. Hart, 1866-67"), [rich("MILES DE GOLPES DE GENTE SIN NOMBRE", ("golpes",), 0.3, y=0.1, size=52, maxw=0.85)],
        tex=ARCH)
    add(1111.76, kb("u_p0hjCbjI4dw.jpg", "in", "sepia"), [big("AHORA TE PREGUNTO A TI", 0.2, 0.84, 66, YELLOW)], tr="fade", td=0.4, tex=ARCH)
    add(1113.38, kb("u_m30lrm0utLo.jpg", "in", "cold"), [rich("¿ALGUIEN DE TU FAMILIA LLEGÓ A ESTE PAÍS…", ("familia",), 0.2, y=0.84, size=52, maxw=0.8)], tex=CLEAN)
    add(w("via", 1117.6) - 0.2, kb("u_80N41Pt698Q.jpg", "in", "doc"), [big("UNA VÍA", 0.0, 0.84, 76)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("carretera", 1119.0) - 0.1, kb("u_2U4NUJjG58g.jpg", "in", "doc"), [big("UNA CARRETERA", 0.0, 0.84, 76)], tr="whip_l", td=0.2, tex=CLEAN)
    add(w("campo", 1120.3) - 0.1, kb("u_M02WlFtuPbw.jpg", "in", "warm"), [big("UN CAMPO · UNA OBRA", 0.0, 0.84, 76)], tr="whip_l", td=0.2, tex=CLEAN)
    add(1122.24, kb("u_rO6bcXIMrPg.jpg", "out", "dark"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿CÓMO SE LLAMABA?", line2="¿QUÉ LEVANTÓ?", cta="CUÉNTANOS EN LOS COMENTARIOS"),
         rich("Aquí, por lo menos, su nombre sí va a quedar escrito", ("nombre",), w("aqui", 1126.0) - 1122.24, step=0.09, y=0.2, size=48, maxw=0.85)], tex=DARK)
    return S
