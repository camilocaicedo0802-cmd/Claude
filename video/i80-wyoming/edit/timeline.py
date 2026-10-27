"""The edit: every shot of the I-80 Wyoming video, synced to the voice-over."""
import bisect
import os
import sys

import cv2
import numpy as np

import gfx2 as G2
import gfx3 as G3
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Seq, Solid, Split, Stamp, Still, TimelineBar, Video)
from render import Shot
import words

TOTAL = 1126.37
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
FILM = dict(grain=12, dust=0.6, flicker=0.04, vignette=1.0)
VHS = dict(grain=8, dust=0.0, flicker=0.02, vignette=0.9)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)


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


def postshake(amt):
    def f(img, t, dur):
        return G2.shake_frame(img, t, amt)
    return f


def gate(**kw):
    return FnOverlay(G3.gate_overlay, **kw)


# map helpers ---------------------------------------------------------
LOC_C = (-106.22, 41.62)
LOC_BB = (-107.7, 40.9, -105.0, 42.3)
US30_BB = (-107.0, 41.2, -105.5, 42.1)
I80_LOC = dict(type="road", name="80", level="Interstate", bbox=LOC_BB, reverse=True)  # drawn east -> west
US30_LOC = dict(type="road", name="30", level="Federal", bbox=US30_BB)
WY_BB = (-111.6, 40.4, -103.6, 45.3)
US_BB = (-126, 23, -65, 51)


def mp(name, cams, layers, title=None):
    return M.MapScene(name, cams, layers, title)


def lay(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


TOWNS3 = [dict(type="pin", at="rock_river", label="ROCK RIVER", side="r", size=36),
          dict(type="pin", at="medicine_bow", label="MEDICINE BOW", side="t", size=36),
          dict(type="pin", at="hanna", label="HANNA", side="l", size=36)]
UP_RAIL = ["laramie", "bosler", "rock_river", "medicine_bow", (-106.35, 41.93), "hanna", (-106.70, 41.83), "walcott", "sinclair", "rawlins"]


def flow_over_elk(z, t0=0.3, cam=LOC_C):
    bm = M.basemap("loc")
    ex, ey = bm.px(*M.COORDS["elk_mtn"])
    cx, cy = bm.px(*cam)
    return G3.FlowOverlay(960 + (ex - cx) * z, 540 + (ey - cy) * z, 80 * z / 0.8, t0=t0)


# ------------------------------------------------------------------ the edit
def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    snow = G2.SnowOverlay(240, speed=1.3)
    snow2 = G2.SnowOverlay(200, seed=5, speed=2.2)

    # ============================== INTRO (0 - 84.9)
    add(0.0, kb("u_VoWBZW9xA7U.jpg", "in", "cold"), [snow2, Badge("I-80 · WYOMING", 0.5, 3.0)], tex=CLEAN, post=postshake(3))
    t_sf = w("san", 4.4)
    add(t_sf - 0.15, kb("u_71vAb1FXB6g.jpg", "in", "cold"), [BigText("SAN FRANCISCO", "bebas", 70, WHITE, (0.5, 0.82), 0.1, None, "up", tracking=4)],
        tr="whip_l", td=0.3, tex=CLEAN)
    t_ny = w("nueva", 6.0)
    add(t_ny - 0.1, kb("u_5omwAMDxmkU.jpg", "in", "warm"), [BigText("NUEVA YORK", "bebas", 70, WHITE, (0.5, 0.82), 0.1, None, "up", tracking=4)],
        tr="whip_l", td=0.3, tex=CLEAN)
    t_oc = w("otro", 8.3) - 1.1
    add(t_oc, mp("us", [(0, -98, 40.0, 0.62), (2.0, -98, 40.0, 0.66)],
                 [dict(type="road", name="80", level="Interstate", bbox=US_BB, t0=0.0, draw=1.5, width=6),
                  dict(type="pin", at="sf", t0=0.0, label="SF", side="l"), dict(type="pin", at="nyc", t0=1.3, label="NY", side="r")]),
        tr="zoom", td=0.4, tex=GFX)
    add(9.02, kb("f_49160451161.jpg", "in", "cold"), [Badge("MAYO", 0.3, 3.0)], tr="fade", td=0.3, tex=CLEAN)
    t_4 = w("cuatro", 13.5)
    add(12.3, kb("u_7CffibpcnuI.jpg", "punch", "cold"),
        [Counter(0, 4, "{:.0f}", "PIES DE NIEVE DURA", t_4 - 12.3, 0.8, (0.5, 0.42), 220, sub="MÁS DE UN METRO")], tex=CLEAN, post=postshake(2))
    add(17.6, vid("rpsnowroad", 440.0, 2.6, "faded"), tex=FILM)
    add(20.16, kb("u_y8ax9FcLtes.jpg", "in", "cold"), [rich("SOLO ENCIMA DEL ASFALTO", ("asfalto",), 0.6, y=0.8, size=60)], tex=CLEAN)
    add(24.14, kb("f_55252804633.jpg", "punch", "cold"), [Flash(0.0, 0.15, (255, 255, 255), 0.5)], tex=CLEAN)
    add(25.86, vid("rpsnowroad", 112.0, 3.0, "faded"), [BigText("LA NIEVE NO SE QUEDA DONDE CAE", "bebas", 58, WHITE, (0.5, 0.8), 0.4, None, "up", tracking=3)],
        tex=FILM)
    add(28.9, vid("gov.dot.fhwa.ttp.vh-286", 78.0, 3.6, "cold", zoom0=1.5, zoom1=1.58, cx=0.45, cy=0.38), tex=VHS)
    t_tro = w("tropieza", 32.5)
    add(t_tro, kb("u_tv53M6u2bAQ.jpg", "in", "cold"), tr="zoom", td=0.35, tex=CLEAN)
    t_tr = w("trazo", 35.2)
    add(t_tr - 0.4, kb("u_HA0Rgl-ISko.jpg", "in", "sepia"),
        [FnOverlay(lambda im, t, d: G2.aa_poly(im, G2.partial_line(np.array([[260, 610], [1660, 470]], float), ease_out(prog(t, 0.3, 1.0))), RED, 8)),
         Badge("WASHINGTON", 0.6, None)], tex=ARCH)
    add(38.2, kb("u_0gkw_9fy0eQ.jpg", "r", "warm"), [rich("ALGUIEN YA LO HABÍA ADVERTIDO", ("advertido",), 0.8, y=0.78, size=56)], tex=ARCH)
    t_fr = w("fracasar", 46.0)
    add(41.4, kb("u_luOHcHUkirA.jpg", "in", "doc"),
        [Badge("1956 · WYOMING → WASHINGTON", 0.3, None), Stamp("«VA A FRACASAR»", t_fr - 41.4, RED, (0.5, 0.55), -8, 110)], tex=ARCH)
    add(48.08, vid("Building1948", 140.0, 2.0, "bw"), [BigText("AUN ASÍ LA CONSTRUYERON", "bebas", 64, WHITE, (0.5, 0.8), 0.2, None, "up", tracking=3)],
        tex=FILM)
    add(w("algo", 50.0), kb("u_Qdbzh5KJWTo.jpg", "in", "night"), tr="glitch", td=0.3, tex=DARK)
    add(51.42, kb("u_phv0kzqMJyk.jpg", "in", "cold"), [gate(t0=0.5)], tex=CLEAN)
    t_otro = w("otro", 56.5)
    add(54.6, mp("loc", [(0, -106.25, 41.62, 0.62), (7.0, -106.25, 41.66, 0.66)],
                 [lay(I80_LOC, t0=0.0, draw=1.0, color=YELLOW, width=7),
                  lay(US30_LOC, t0=w("carretera", 58.3) - 54.6, draw=1.0, color=WHITE, width=6),
                  lay(I80_LOC, t0=w("dos", 59.8) - 54.6, draw=0.4, color=RED, width=9),
                  lay(US30_LOC, t0=w("dos", 59.8) - 54.6 + 0.2, draw=0.4, color=RED, width=9),
                  dict(type="xmark", at=(-106.2, 41.56), t0=w("dos", 59.8) - 54.6 + 0.5),
                  dict(type="xmark", at=(-106.2, 41.84), t0=w("dos", 59.8) - 54.6 + 0.7),
                  dict(type="label", at=(-106.2, 41.92), text="LAS DOS A LA VEZ", t0=w("vez", 60.5) - 54.6, size=56, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(61.6, mp("us", [(0, -98, 40.0, 0.66), (5.0, -104.5, 41.3, 1.3)],
                 [dict(type="road", name="80", level="Interstate", bbox=US_BB, t0=0.0, draw=0.01, width=6),
                  dict(type="road", name="80", level="Interstate", bbox=(-107.2, 40, -105.4, 43), t0=1.5, draw=0.5, color=RED, width=12),
                  dict(type="pin", at="arlington", t0=2.6, label="AQUÍ SE CORTA", side="t", color=RED, size=44)]),
        tr="fade", td=0.3, tex=GFX)
    add(66.58, Split([kb("u_6tiPnI_ijuI.jpg", "in", "cold"), kb("u_kZokA2VTKn4.jpg", "in", "cold")], labels=["SAN FRANCISCO", "NUEVA YORK"]),
        tr="whip_r", td=0.3, tex=CLEAN)
    add(w("entre", 69.6), kb("u_1RE_PkB9n4Y.jpg", "in", "cold", z=1.05),
        [BigText("NO PASA NADIE", "bebas", 84, WHITE, (0.5, 0.5), 0.5, None, "up", tracking=6)], tr="fade", td=0.4, tex=CLEAN)
    add(72.08, kb("u_OQMZwNd3ThU.jpg", "in", "warm"), [rich("EL PAPEL LO AGUANTA TODO", ("papel",), 0.2, y=0.8, size=58)], tex=CLEAN)
    add(w("esta", 74.4), kb("l_48974.jpg", "punch", "cold"), [BigText("ESTA MESETA, NO.", "serif", 96, WHITE, (0.5, 0.5), 0.15, None, "pop")],
        tr="flash", td=0.2, tex=CLEAN, post=postshake(3))
    add(76.12, kb("u_scbYOgVyb8Q.jpg", "in", "dark"), [Darken(0.5)] + question("¿Por qué levantar una carretera que ya sabían que iba a fallar?", ("fallar?",)),
        tr="fade", td=0.3, tex=DARK)
    add(79.92, kb("u_1RE_PkB9n4Y.jpg", "out", "dark"), [Darken(0.55)] + question("¿Y por qué dejar a todo el mundo sin camino, cerrando también la alternativa?", ("alternativa?", "camino,")),
        tr="glitch", td=0.3, tex=DARK)
    # title sting
    add(84.94, kb("u_A-NVHPka9Rk.jpg", "in", "cold"),
        [Darken(0.5, 0.0, 0.3), BigText("I-80", "bebas", 230, YELLOW, (0.5, 0.40), 0.1, None, "pop", tracking=12),
         BigText("La autopista que el viento cierra", "serif_it", 70, WHITE, (0.5, 0.60), 0.45, None, "up")],
        tr="flash", td=0.25, tex=CLEAN)

    # ============================== CAP 1: DOS MAPAS (87.98 - 235.86)
    add(87.98, fr("f_8706012176.jpg", "Ferrocarril transcontinental, década de 1860", g="archival"), [Badge("MAPA 1 · 1868", 0.2, None)], tr="fade", td=0.3, tex=ARCH)
    add(91.54, kb("u_ylNoOK6ylHg.jpg", "in", "sepia"), [Badge("MAPA 2 · 1956", 0.2, None)], tex=ARCH)
    add(95.94, mp("loc", [(0, -106.2, 41.7, 0.6), (5.4, -106.2, 41.72, 0.68)],
                  [lay(US30_LOC, t0=0.0, draw=1.2, color=WHITE, width=6), lay(I80_LOC, t0=0.5, draw=1.4, color=YELLOW, width=7),
                   dict(type="label", at=(-106.35, 41.77), text="20 MILLAS · 32 KM", t0=w("millas", 97.0) - 95.94, size=52, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(101.4, fr("f_18412591328.jpg", "Union Pacific, 1868", g="archival"), [Badge("1868 · UNION PACIFIC", 0.2, None)], tex=ARCH)
    add(w("cruzar", 105.0) - 0.6, kb("f_5105784756.jpg", "l", "archival"), tex=ARCH)
    add(109.32, mp("loc", [(0, -105.9, 41.45, 0.85), (6.5, -106.3, 41.6, 0.8)],
                   [dict(type="pin", at="laramie", t0=0.2, label="LARAMIE", side="r"),
                    dict(type="route", path=["laramie", "elk_mtn", "walcott"], t0=1.0, draw=2.0, color=YELLOW, width=5, dash=26),
                    dict(type="label", at=(-106.0, 41.38), text="LÍNEA RECTA", t0=2.5, size=50, color=YELLOW),
                    dict(type="pin", at="elk_mtn", t0=w("montana", 116.5) - 109.32, label="ELK MOUNTAIN", side="b", color=WHITE)]),
        tr="zoom", td=0.35, tex=GFX)
    add(w("llamada", 117.6) - 0.2, kb("f_54182264076.jpg", "in", "cold"), [LowerThird("ELK MOUNTAIN", "3.400 m · una montaña solitaria", 0.4)], tex=CLEAN)
    add(119.24, kb("l_33152.jpg", "l", "bw"), [rich("LOS TOPÓGRAFOS DEL TREN ESTUDIARON ESE TERRENO", ("topógrafos",), 0.3, y=0.84, size=50)], tex=ARCH)
    t_otro2 = w("lado", 122.5)
    add(t_otro2 - 0.3, mp("loc", [(0, -106.2, 41.7, 0.62), (7.0, -106.25, 41.78, 0.7)],
                          [dict(type="rail", path=UP_RAIL, t0=0.2, draw=3.0, color=(205, 170, 120), width=5),
                           dict(type="pin", at="elk_mtn", t0=0.0, label="ELK MOUNTAIN", side="b", color=WHITE, pulse=False),
                           dict(type="label", at=(-106.15, 41.98), text="20 MILLAS AL NORTE", t0=1.6, size=48, box=True),
                           dict(type="pin", at="medicine_bow", t0=w("medicine", 128.6) - t_otro2 + 0.3, label="MEDICINE BOW", side="t")]),
        tr="fade", td=0.3, tex=GFX)
    add(130.66, kb("u_u82pLER9M6w.jpg", "l", "bw"),
        [Counter(0, 20, "{:.0f}", "MILLAS DE RIELES DE MÁS", 0.2, 1.0, (0.5, 0.45), 200, sub="QUE PAGAR Y MANTENER PARA SIEMPRE")], tex=ARCH)
    add(137.6, kb("f_16623612593.jpg", "in", "bw"), [rich("NINGUNA COMPAÑÍA HACE ESO POR GUSTO", ("gusto",), 0.3, y=0.82, size=52)], tex=ARCH)
    add(140.46, kb("l_36454.jpg", "in", "cold"), [Darken(0.25), rich("ALGO VIERON EN ESA MESETA", ("meseta",), 0.4, y=0.5, size=66)], tex=CLEAN)
    add(144.72, kb("u_BeGRBsAISuw.jpg", "r", "bw"), tex=ARCH)
    add(147.32, vid("LincolnH1915", 42.0, 3.2, "bw"), [Badge("1913 · LINCOLN HIGHWAY", 0.2, None)], tex=FILM)
    add(w("siguio", 151.9) - 0.5, kb("f_4506726488.jpg", "in", "doc"), [Caption("«En la Lincoln Highway»", None, 0.3)], tex=ARCH)
    add(153.7, kb("l_33082.jpg", "l", "doc"), [Badge("1926 · US 30", 0.2, None)], tex=CLEAN)
    t_tres = w("tres", 157.3)
    add(t_tres, Seq([(1.3, kb("u_Z8OBYVwZhWU.jpg", "in", "warm")), (1.3, kb("f_14096904051.jpg", "in", "warm")),
                     (1.3, kb("l_48973.jpg", "in", "doc")), (1.0, kb("u_rTccfq6HOdM.jpg", "in", "warm"))]),
        [rich("VIVÍAN DE LO QUE PASABA FRENTE A SUS PUERTAS", ("puertas",), 0.3, y=0.84, size=48)], tex=CLEAN)
    t_rr = w("rock", 163.6)
    add(t_rr, kb("l_47658.jpg", "in", "doc"), [BigText("ROCK RIVER", "bebas", 96, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tr="whip_l", td=0.2, tex=CLEAN)
    t_mb = w("medicine", 164.6)
    add(t_mb, kb("f_7155743334.jpg", "in", "doc"), [BigText("MEDICINE BOW", "bebas", 96, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tr="whip_l", td=0.2, tex=CLEAN)
    t_ha = w("hannah", 165.8)
    add(t_ha, mp("loc", [(0, -106.56, 41.87, 1.0), (1.2, -106.56, 41.87, 1.08)], [dict(type="pin", at="hanna", t0=0.0, color=YELLOW)]),
        [BigText("HANNA", "bebas", 96, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tr="whip_l", td=0.2, tex=GFX)
    add(166.88, vid("HighwayH1956", 588.0, 4.0, "bw"), [Badge("1956 · EL SEGUNDO MAPA", 0.2, None)], tr="fade", td=0.3, tex=FILM)
    add(170.96, kb("u_XWW746i6WoM.jpg", "in", "doc"), [Badge("CONGRESO · LEY DE INTERESTATALES", 0.3, None)], tex=CLEAN)
    add(176.2, vid("HighwayH1956", 500.0, 4.0, "bw"), [rich("LO MÁS DIRECTAS POSIBLE", ("directas",), 0.3, y=0.8, size=64)], tex=FILM)
    add(180.26, vid("BuildersOfTh", 60.0, 3.0, "faded"), [LowerThird("OFICINA DE CARRETERAS PÚBLICAS", "Washington", 0.3)], tex=FILM)
    t_wy = w("traves", 184.3) - 1.0
    add(t_wy, mp("wy", [(0, -107.6, 42.9, 0.62), (3.5, -106.6, 41.7, 0.9)],
                 [dict(type="road", name="80", level="Interstate", bbox=WY_BB, t0=0.2, draw=2.2, color=YELLOW, width=7),
                  dict(type="state", name="Wyoming", t0=0.0, color=WHITE, width=3, alpha=0.6)]), tr="zoom", td=0.35, tex=GFX)
    add(186.88, mp("loc", [(0, -106.2, 41.55, 0.72), (9.5, -106.3, 41.6, 0.82)],
                   [dict(type="pin", at="laramie", t0=0.3, label="LARAMIE", side="r"),
                    dict(type="pin", at="walcott", t0=w("walcott", 189.0) - 186.88, label="WALCOTT JCT.", side="l"),
                    lay(US30_LOC, t0=0.0, draw=0.01, color=(120, 120, 120), width=4),
                    lay(I80_LOC, t0=2.4, draw=2.6, color=YELLOW, width=8),
                    dict(type="pin", at="elk_mtn", t0=w("elk", 192.6) - 186.88, label="ELK MOUNTAIN", side="b", color=WHITE),
                    dict(type="label", at=(-106.2, 41.33), text="−19 MILLAS", t0=w("19", 194.5) - 186.88, size=80, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(196.6, vid("1956-11-05_Eisenhower_Re-Elected", 22.0, 3.6, "bw"),
        [LowerThird("DWIGHT D. EISENHOWER", "Presidente de EE. UU. (1953–1961)", 0.4)], tex=FILM)
    add(200.26, vid("202248_Freeway_Driving", 35.0, 4.6, "faded"),
        [Counter(0, 41000, "{:,.0f}", "MILLAS DE AUTOPISTAS", 0.2, 1.4, (0.5, 0.42), 190, sub="SIN SEMÁFOROS NI CRUCES")], tex=FILM)
    add(204.96, kb("u_bqGdhrAftLc.jpg", "in", "doc"), [Badge("DE COSTA A COSTA", 0.2, None)], tex=CLEAN)
    add(207.34, vid("HighwayH1956", 766.0, 2.4, "bw"), tex=FILM)
    add(w("linea", 209.8) - 0.2, cus(G3.straight_vs_detour), tr="whip_r", td=0.3, tex=GFX)
    add(213.04, kb("u_6kA9FjqUxhM.jpg", "in", "doc"), [LowerThird("FRANK TURNER", "Al frente de las carreteras federales", 0.8)], tex=CLEAN)
    add(220.16, kb("u_ylNoOK6ylHg.jpg", "punch", "sepia"), [Callout(1180, 500, 1420, 300, "EL MAPA DEL TRAMO", 0.8)], tex=ARCH)
    add(223.68, mp("loc", [(0, -106.25, 41.5, 0.9), (6.4, -106.25, 41.5, 0.97)],
                   [lay(I80_LOC, t0=0.0, draw=0.8, color=YELLOW, width=8),
                    dict(type="label", at=(-106.25, 41.72), text="LIMPIA · RECTA · PERFECTA", t0=1.0, size=60)]),
        tr="fade", td=0.3, tex=GFX)
    t_map = 230.06
    add(t_map, mp("loc", [(0, -106.25, 41.6, 0.8), (5.8, -106.35, 41.62, 0.95)],
                  [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8), dict(type="pin", at="elk_mtn", t0=0.0, pulse=False, color=WHITE)]),
        [BigText("EN UN MAPA, EL VIENTO NO EXISTE.", "serif", 70, WHITE, (0.5, 0.2), 0.2, w("wyoming", 233.0) - t_map, "up"),
         flow_over_elk(0.8, w("wyoming", 233.0) - t_map + 0.2, (-106.25, 41.6))],
        tex=GFX)

    # ============================== CAP 2: LA PELEA (235.86 - 330.42)
    bg, ov = chapter(2, "La pelea", "l_32860.jpg", "dark", "1956–1966")
    add(235.86, bg, ov, tr="flash", td=0.25, tex=CLEAN)
    add(238.9, mp("loc", [(0, -106.2, 41.75, 0.62), (5.6, -106.2, 41.8, 0.7)],
                  [lay(US30_LOC, t0=0.0, draw=1.4, color=WHITE, width=8)] + TOWNS3 +
                  [dict(type="label", at=(-106.2, 42.05), text="LO LÓGICO: SEGUIR LA US 30", t0=1.0, size=52, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    t_no = w("no", 246.3)
    add(244.58, vid("HighwayH1956", 255.0, 3.0, "bw"), [Stamp("NO", t_no - 244.58, RED, (0.5, 0.5), -10, 200)], tex=FILM)
    add(247.64, kb("u_7jhmlQ468MU.jpg", "in", "cold"), [Badge("RANCHEROS DE ARLINGTON", 0.2, None), snow], tex=CLEAN)
    add(252.1, mp("loc", [(0, -106.2, 41.72, 0.7), (6.3, -106.2, 41.72, 0.74)],
                  [lay(US30_LOC, t0=0.0, draw=0.01, color=WHITE, width=6), lay(I80_LOC, t0=0.2, draw=1.0, color=YELLOW, width=7)] + TOWNS3 +
                  [dict(type="label", at=(-106.0, 41.72), text="20 MILLAS LEJOS", t0=1.8, size=52, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(258.38, kb("f_19805452428.jpg", "l", "doc"), [rich("EL TREN YA HABÍA DADO LA VUELTA", ("vuelta",), 1.2, y=0.82, size=52)], tex=CLEAN)
    add(264.1, vid("HighwayH1956", 322.0, 4.0, "bw"), [rich("NO ERA UNA DISCUSIÓN DE INGENIEROS", ("ingenieros",), 0.4, y=0.82, size=52)], tex=FILM)
    tg = w("gasolinera", 269.0)
    tc = w("cafe", 270.0)
    tm = w("motel", 270.8)
    tt = w("tienda", 271.6)
    add(tg - 0.1, kb("u_Z8OBYVwZhWU.jpg", "punch", "warm"), [BigText("GASOLINERA", "bebas", 90, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(tc - 0.1, kb("u_rTccfq6HOdM.jpg", "punch", "warm"), [BigText("CAFÉ", "bebas", 90, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(tm - 0.1, kb("u_Nunk5bl1JbI.jpg", "punch", "warm"), [BigText("MOTEL", "bebas", 90, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(tt - 0.1, kb("u_F5XRetowPgs.jpg", "punch", "warm"), [BigText("TIENDA", "bebas", 90, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(273.5, kb("u_PjeZGaKunAI.jpg", "in", "warm"), [BigText("THE VIRGINIAN", "serif", 110, WHITE, (0.5, 0.42), 0.4, None, "up"),
                                                       BigText("OWEN WISTER · 1902", "bebas", 46, YELLOW, (0.5, 0.56), 0.9, None, "up", tracking=6)], tex=CLEAN)
    add(277.12, kb("u_efI9Yih-RHc.jpg", "l", "doc"), [rich("UNA DE LAS NOVELAS DE VAQUEROS MÁS FAMOSAS", ("vaqueros",), 0.3, y=0.84, size=48)], tex=CLEAN)
    add(281.12, kb("f_28436010018.jpg", "in", "archival", cam0=(0.28, 0.66, 1.9), cam1=(0.28, 0.68, 2.2)),
        [Badge("HOTEL THE VIRGINIAN · MEDICINE BOW", 0.3, None)], tex=ARCH)
    add(284.04, mp("loc", [(0, -106.2, 41.75, 0.66), (3.0, -106.2, 41.7, 0.7)],
                   [lay(US30_LOC, t0=0.0, draw=0.01, color=WHITE, width=6), lay(I80_LOC, t0=0.0, draw=1.3, color=YELLOW, width=8)] + TOWNS3 +
                   [dict(type="label", at=(-106.2, 41.5), text="20 MILLAS AL SUR", t0=1.2, size=52, box=True)]), tr="fade", td=0.25, tex=GFX)
    add(287.04, kb("f_50789391883.jpg", "in", "faded"), [rich("FUERA DEL MAPA DE LA GENTE QUE PASA", ("pasa",), 1.2, y=0.82, size=52)], tex=CLEAN)
    add(292.04, kb("u_L_U4jhwZ6hY.jpg", "in", "doc"), [Badge("SENADO DE EE. UU.", 0.3, None)], tr="fade", td=0.3, tex=CLEAN)
    add(296.94, kb("u_XWW746i6WoM.jpg", "out", "dark"),
        [Darken(0.55), BigText("1959 · SENADORES DE WYOMING", "bebas", 50, YELLOW, (0.5, 0.3), 0.1, None, "up", tracking=6),
         BigText("JOSEPH C. O'MAHONEY", "serif", 84, WHITE, (0.5, 0.47), w("joseph", 299.5) - 296.94, None, "up"),
         BigText("GALE McGEE", "serif", 84, WHITE, (0.5, 0.62), w("gail", 301.5) - 296.94, None, "up")], tex=DARK)
    add(302.62, kb("u_SKcTKYNRvHY.jpg", "in", "warm"), [rich("QUE CADA ESTADO DECIDA POR DÓNDE PASAN SUS INTERESTATALES", ("estado", "decida"), 0.5, y=0.78, size=50)],
        tex=ARCH)
    t_mov = w("movio", 309.5)
    add(308.48, mp("loc", [(0, -106.25, 41.6, 0.82), (2.7, -106.25, 41.6, 0.86)],
                   [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=9)]), [Stamp("NO SE MOVIÓ", t_mov - 308.48, RED, (0.5, 0.45), -8, 120)], tex=GFX)
    add(311.18, vid("gov.dot.fhwa.ttp.vh-60h", 64.0, 3.3, "doc"), [Badge("LA RESPUESTA DE WASHINGTON", 0.2, None)], tex=VHS)
    add(314.5, vid("rpsnowroad", 454.0, 3.8, "faded"), [rich("EQUIPO MODERNO PARA QUITAR NIEVE", ("moderno",), 0.4, y=0.84, size=50)], tex=FILM)
    t_cad = w("caducidad", 320.0)
    add(318.3, kb("u_Qdbzh5KJWTo.jpg", "in", "night"),
        [Darken(0.4), BigText("FECHA DE CADUCIDAD", "bebas", 110, WHITE, (0.5, 0.45), t_cad - 318.3, None, "pop", tracking=6),
         Stamp("MUY CORTA", w("corta", 321.5) - 318.3, RED, (0.5, 0.65), -8, 100)], tex=DARK)
    add(322.46, vid("BuildersOfTh", 377.0, 3.8, "faded"), [Badge("VERANO DE 1966", 0.2, None)], tex=FILM)
    add(326.3, kb("u_IojdpIRgOQk.jpg", "in", "doc"), [TimelineBar(1966, 1970, 0.2, (0.4, 2.4), 1966, 0.84)], tex=CLEAN)

    # ============================== CAP 3: CUATRO DÍAS (330.42 - 511.8)
    bg, ov = chapter(3, "Cuatro días", "u_A-NVHPka9Rk.jpg", "dark", "1970")
    add(330.42, bg, ov + [Badge("SÁBADO 3 DE OCTUBRE DE 1970", 0.9, None, "tl")], tr="flash", td=0.25, tex=CLEAN)
    add(333.36, kb("f_53577131945.jpg", "in", "doc"), [Badge("UNA SALIDA EN MITAD DE LA PRADERA", 0.3, None)], tex=CLEAN)
    add(337.9, kb("u_DcH00XKgCuQ.jpg", "r", "doc"), [rich("NI PUEBLO NI ÁRBOLES", ("pueblo", "árboles"), 0.1, y=0.5, size=72)], tex=CLEAN)
    add(339.64, vid("HighwayH1956", 189.0, 2.9, "bw"), tex=FILM)
    add(342.5, vid("HighwayH1956", 233.0, 3.0, "bw"), [Counter(0, 400, "+{:.0f}", "PERSONAS APLAUDIENDO", 0.0, 1.0, (0.5, 0.45), 180)], tex=FILM)
    add(345.48, mp("loc", [(0, -106.2, 41.55, 0.72), (4.5, -106.2, 41.55, 0.76)],
                   [lay(I80_LOC, t0=0.0, draw=1.5, color=YELLOW, width=9)]),
        [Counter(0, 77, "{:.0f} MILLAS", "≈ 124 KM DE INTERESTATAL NUEVA", 0.0, 1.2, (0.5, 0.2), 120)], tr="fade", td=0.25, tex=GFX)
    add(350.04, vid("HighwayH1956", 211.0, 2.5, "bw"), [Badge("EL GOBERNADOR CORTA LA CINTA", 0.2, None)], tex=FILM)
    add(w("camiones", 352.7) - 0.2, vid("Transpor1946", 366.6, 2.9, "bw"), tex=FILM)
    add(355.48, kb("u_A-NVHPka9Rk.jpg", "punch", "cold"), [BigText("DISFRÚTALO.", "serif_it", 110, WHITE, (0.5, 0.5), 0.1, None, "pop")], tex=CLEAN)
    add(356.64, kb("u_1RE_PkB9n4Y.jpg", "in", "dark"),
        [Darken(0.4), BigText("NO DURARÁ ABIERTA MÁS DE", "bebas", 58, WHITE, (0.5, 0.36), 0.3, None, "up", tracking=4),
         Counter(0, 4, "{:.0f} DÍAS", "", 0.9, 0.8, (0.5, 0.55), 230, color=YELLOW)], tr="glitch", td=0.3, tex=DARK)
    add(360.68, kb("u_pPkzZYG0veM.jpg", "in", "sepia"), [Badge("UN RÉCORD", 0.2, None)], tex=ARCH)
    add(363.4, kb("u_bqGdhrAftLc.jpg", "in", "doc"), [Counter(0, 77, "{:.0f} MILLAS DE GOLPE", "LA MAYOR APERTURA DE INTERESTATAL DEL PAÍS", 0.3, 1.2, (0.5, 0.45), 120)], tex=CLEAN)
    add(369.24, vid("HighwayH1956", 56.0, 1.6, "bw"), [BigText("ORGULLO", "bebas", 110, WHITE, (0.5, 0.5), 0.0, None, "pop", tracking=8)], tex=FILM)
    add(370.84, kb("u_1RE_PkB9n4Y.jpg", "punch", "cold"), [Stamp("UN SÍNTOMA", 0.3, RED, (0.5, 0.5), -8, 120)], tr="glitch", td=0.25, tex=CLEAN)
    add(372.26, mp("wy", [(0, -107.6, 41.6, 0.85), (8.4, -107.3, 41.6, 0.9)],
                   [dict(type="road", name="80", level="Interstate", bbox=(-111.2, 40.4, -110.0, 42), t0=0.2, draw=0.5, color=YELLOW, width=7),
                    dict(type="road", name="80", level="Interstate", bbox=(-109.4, 40.4, -108.2, 42), t0=0.8, draw=0.5, color=YELLOW, width=7),
                    dict(type="road", name="80", level="Interstate", bbox=(-107.6, 40.4, -106.9, 42), t0=1.4, draw=0.5, color=YELLOW, width=7),
                    dict(type="road", name="80", level="Interstate", bbox=(-105.3, 40.4, -104.0, 42), t0=2.0, draw=0.5, color=YELLOW, width=7),
                    dict(type="label", at=(-107.6, 42.15), text="A PEDAZOS", t0=1.0, size=60, box=True),
                    dict(type="road", name="30", level="Federal", bbox=(-111.2, 40.4, -104.0, 43.0), t0=w("pedazo", 376.8) - 372.26, draw=1.8, color=(170, 170, 170), width=4, dash=18)]),
        tr="fade", td=0.3, tex=GFX)
    add(380.8, mp("loc", [(0, -106.2, 41.7, 0.66), (4.0, -106.2, 41.7, 0.7)],
                  [lay(US30_LOC, t0=0.0, draw=0.01, color=(170, 170, 170), width=5), lay(I80_LOC, t0=0.0, draw=0.8, color=YELLOW, width=8),
                   dict(type="label", at=(-106.2, 41.98), text="LA VIEJA: 20 MILLAS AL NORTE", t0=0.8, size=50, box=True)]), tr="fade", td=0.25, tex=GFX)
    add(384.72, kb("u_VoWBZW9xA7U.jpg", "punch", "cold"), [BigText("TODO O NADA", "bebas", 150, WHITE, (0.5, 0.5), 0.05, None, "pop", tracking=10)],
        tr="flash", td=0.2, tex=CLEAN, post=postshake(4))
    T_SAT, T_SUN, T_MON = w("sabado", 389.2), w("domingo", 392.0), w("lunes", 398.1)
    T_TUE, T_WED = w("martes", 399.0), w("miercoles", 412.6)
    add(386.5, cus(G3.countdown, times=[T_SAT - 386.5 + 0.1, 99, 99, 99, 99], final_t=99), tr="fade", td=0.3, tex=GFX)
    add(T_SUN, vid("202248_Freeway_Driving", 150.0, 3.2, "faded"), [Badge("DOMINGO · FAMILIAS DE PASEO", 0.2, None)], tex=FILM)
    add(w("gusto", 395.5) - 0.5, vid("202248_Freeway_Driving", 311.0, 2.6, "faded"), [rich("SIN CURVAS", ("curvas",), 0.2, y=0.8, size=60)], tex=FILM)
    add(T_MON - 0.1, cus(G3.countdown, times=[-1, -1, 0.2, T_TUE - T_MON + 0.1, 99], final_t=99, hi=3), tr="fade", td=0.2, tex=GFX)
    add(400.58, vid("Transpor1946", 405.2, 3.2, "bw"), [Counter(0, 19, "−{:.0f} MILLAS", "", 0.2, 0.8, (0.5, 0.82), 110, color=YELLOW)], tex=FILM)
    add(403.82, kb("u_PNb6Zn-f5R4.jpg", "in", "doc"), [rich("NADIE MIRA EL CIELO DEL OESTE", ("oeste",), 0.4, y=0.82, size=56)], tex=CLEAN)
    add(407.76, vid("rpsnowroad", 52.5, 4.6, "faded"), [Badge("DETRÁS DE ELK MOUNTAIN", 0.4, None)], tex=FILM)
    add(T_WED - 0.1, cus(G3.countdown, times=[-1, -1, -1, -1, 0.15], final_t=w("rola", 418.4) - T_WED, hi=4), tr="fade", td=0.2, tex=GFX)
    add(w("tormenta", 416.5) - 0.1, vid("rpsnowroad", 125.0, 2.2, "faded"), tex=FILM, post=postshake(3))
    add(w("rola", 418.4) - 0.2, kb("u_phv0kzqMJyk.jpg", "in", "cold"), [gate(t0=0.0), Stamp("CERRADA", 0.9, RED, (0.62, 0.38), -8, 110)], tex=CLEAN)
    # in the truck cab
    add(420.72, kb("u_PNb6Zn-f5R4.jpg", "punch", "doc"), [Badge("MIÉRCOLES POR LA TARDE", 0.3, None)], tr="fade", td=0.3, tex=CLEAN)
    add(424.7, kb("u_A-NVHPka9Rk.jpg", "in", "doc"), [rich("NUEVA · ANCHA · SIN CURVAS", ("nueva", "ancha"), 0.6, y=0.82, size=60)], tex=CLEAN)
    add(429.06, kb("u_1RE_PkB9n4Y.jpg", "punch", "cold"), [Flash(0.0, 0.3, (255, 255, 255), 0.95), snow2], tex=CLEAN)
    add(w("linea", 431.4) - 0.1, vid("gov.dot.fhwa.ttp.vh-157", 440.0, 2.6, "cold_bw"), tex=VHS)
    add(433.98, kb("u_-hazlBRUM1U.jpg", "in", "warm"),
        [FnOverlay(G2.waveform_overlay, y=0.8, amp=0.8), Caption("«...más adelante ya no se pasa»", None, 0.8, None, 0.66)], tex=ARCH)
    add(438.82, vid("gov.dot.fhwa.ttp.vh-157", 705.0, 4.3, "cold_bw"), [rich("TE ORILLAS CON EL MOTOR ENCENDIDO", ("motor",), 0.3, y=0.82, size=52)], tex=VHS)
    add(443.14, kb("u_5DXpcrNBG48.jpg", "in", "cold"), [rich("NADIE SABE CUÁNTO VA A DURAR", ("cuánto",), 0.2, y=0.82, size=56)], tex=CLEAN)
    add(445.4, kb("u_R7-X7O0Wjcs.jpg", "in", "cold"), [Darken(0.3), BigText("ACABAS DE ESTRENAR UNA COSTUMBRE", "bebas", 64, WHITE, (0.5, 0.82), 1.2, None, "up", tracking=3)], tex=CLEAN)
    add(449.14, kb("u_scbYOgVyb8Q.jpg", "in", "dark"),
        [Darken(0.45), BigText("NO EN ENERO", "bebas", 80, (170, 170, 170), (0.5, 0.33), 0.1, None, "up", tracking=6),
         BigText("NI EN SU PRIMER INVIERNO", "bebas", 80, (170, 170, 170), (0.5, 0.47), w("siquiera", 450.0) - 449.14, None, "up", tracking=6),
         BigText("EN SU PRIMERA SEMANA", "bebas", 104, YELLOW, (0.5, 0.64), w("primera", 452.3) - 449.14, None, "pop", tracking=6)], tex=DARK)
    add(455.04, vid("gov.dot.fhwa.ttp.vh-60h", 408.0, 2.7, "doc"), [Badge("LAS MÁQUINAS PROMETIDAS", 0.2, None)], tex=VHS)
    add(457.7, vid("rpsnowroad", 409.5, 3.6, "faded"), [Stamp("NO ALCANZARON", 0.4, RED, (0.5, 0.5), -8, 120)], tex=FILM)
    add(461.3, kb("u_Obpget_fY8U.jpg", "in", "dark"), [rich("LO QUE VINO DESPUÉS FUE PEOR", ("peor",), 0.2, y=0.82, size=60)], tex=DARK)
    add(463.28, Seq([(1.3, kb("u_jbA2kQI0lx4.jpg", "punch", "cold")), (1.3, kb("u_zvNNtHa7-Zk.jpg", "punch", "cold")),
                     (1.1, kb("u_rYzjlG45K1A.jpg", "punch", "cold"))]), [Badge("LOS CIERRES, UNA COSTUMBRE", 0.2, None)], tex=CLEAN)
    add(467.02, vid("gov.dot.fhwa.ttp.vh-157", 333.0, 2.6, "cold_bw"), [Badge("AL ESTE DE ARLINGTON", 0.2, None)], tex=VHS)
    add(w("bulldozers", 471.6) - 0.3, kb("u_yjKIbvTOn1Q.jpg", "punch", "cold"), [BigText("BULLDOZERS", "bebas", 110, WHITE, (0.5, 0.78), 0.1, None, "pop", tracking=8)], tex=CLEAN)
    add(473.66, vid("1967-02-28_Viet_Sweep", 8.5, 2.8, "bw"), [Badge("ÉPOCA DE VIETNAM", 0.2, None)], tex=FILM)
    add(w("radio", 476.6) - 0.2, kb("u_CbSIiGiK9sM.jpg", "in", "warm"), [FnOverlay(G2.waveform_overlay, y=0.82, amp=0.7),
                                                                        Caption("«...la ruta Ho Chi Minh...»", None, 0.5, None, 0.66)], tex=ARCH)
    add(479.46, vid("1967-02-28_Viet_Sweep", 26.0, 2.5, "bw"), tex=FILM)
    add(481.98, kb("u_NKr0qBAkU4s.jpg", "in", "bw"), [rich("LE PUSIERON NOMBRE ANTES QUE NADIE", ("nombre",), 0.2, y=0.82, size=52)], tex=ARCH)
    add(483.88, kb("u_VoWBZW9xA7U.jpg", "in", "cold"),
        [Darken(0.35), BigText("SNOW CHI MINH TRAIL", "type", 104, WHITE, (0.5, 0.45), 0.3, None, "type"),
         BigText("LA RUTA HO CHI MINH DE LA NIEVE", "bebas", 50, YELLOW, (0.5, 0.6), 2.2, None, "up", tracking=6), snow2], tex=CLEAN)
    add(488.9, kb("u_Oaqk7qqNh_c.jpg", "in", "warm"),
        [LowerThird("JOHN WAGGENER", "Historiador · autor de «Snow Chi Minh Trail»", w("historiador", 493.2) - 488.9)], tex=ARCH)
    add(495.7, kb("u_HA0Rgl-ISko.jpg", "in", "dark"), [Darken(0.4), rich("FALTA LA PIEZA QUE NO ENCAJA", ("pieza",), 0.2, y=0.5, size=72)], tex=DARK)
    add(497.92, Split([kb("l_36455.jpg", "in", "cold"), kb("u_luOHcHUkirA.jpg", "in", "doc")], labels=["WYOMING: «VA A FRACASAR»", "WASHINGTON: «ADELANTE»"]),
        tr="whip_l", td=0.3, tex=CLEAN)
    add(503.24, kb("u_scbYOgVyb8Q.jpg", "out", "dark"), [Darken(0.5)] + question("¿Cómo se pasa de un aviso tan claro a un cierre en cuatro días?", ("cuatro", "días?")),
        tr="glitch", td=0.3, tex=DARK)
    add(506.98, kb("l_48974.jpg", "in", "cold"), [rich("LA RESPUESTA ESTÁ ALLÁ ARRIBA", ("arriba",), 0.4, y=0.82, size=58)], tex=CLEAN)

    # ============================== CAP 4: LA NIEVE QUE VIAJA (511.8 - 659.62)
    bg, ov = chapter(4, "La nieve que viaja", "u_Ls2fcCP0IB4.jpg", "night")
    add(511.8, bg, ov, tr="flash", td=0.25, tex=DARK)
    add(514.6, vid("gov.dot.fhwa.ttp.vh-157", 466.0, 1.9, "cold_bw"), [Badge("ENERO · AÑOS 70", 0.2, None)], tex=VHS)
    add(516.5, kb("u_dXG4-cyRe8M.jpg", "in", "night"), [rich("NUEVA Y ANCHA", ("ancha",), 0.2, y=0.82, size=60)], tex=DARK)
    add(518.62, kb("u_Qdbzh5KJWTo.jpg", "punch", "night"), [snow2, BigText("DESAPARECE", "bebas", 120, WHITE, (0.5, 0.5), w("desaparece", 520.6) - 518.62, None, "pop", tracking=10)],
        tex=DARK, post=postshake(2))
    add(522.02, kb("f_49160014428.jpg", "in", "cold"), [rich("NO ES LA NIEVE DEL PISO", ("piso",), 0.2, y=0.82, size=58)], tex=CLEAN)
    add(524.34, vid("rpsnowroad", 127.0, 2.9, "faded"), [rich("ES EL AIRE, LLENO DE NIEVE QUE CORRE DE LADO", ("aire",), 0.2, y=0.84, size=48)], tex=FILM)
    add(527.22, vid("gov.dot.fhwa.ttp.vh-157", 918.0, 3.3, "cold_bw"), [Badge("POR EL ESPEJO", 0.6, None)], tex=VHS)
    add(w("llenar", 532.0) - 1.5, vid("gov.dot.fhwa.ttp.vh-286", 171.0, 1.8, "cold", zoom0=1.5, zoom1=1.55, cx=0.45, cy=0.38), tex=VHS)
    add(533.44, kb("u_auKUoQcwQfs.jpg", "in", "cold"), [rich("NO ES COMO LA DE UNA CIUDAD", ("ciudad",), 0.2, y=0.82, size=58)], tex=CLEAN)
    add(535.4, kb("l_33152.jpg", "in", "doc"), [Counter(0, 7000, "+{:,.0f} PIES", "≈ 2.100 METROS DE ALTURA", 0.3, 1.3, (0.5, 0.42), 150)], tex=CLEAN)
    add(540.32, cus(G3.snow_section, mode="travel"), tr="fade", td=0.3, tex=GFX)
    t_trop = w("tropieza", 552.0)
    add(550.56, cus(G3.snow_section, mode="trap"), tr="fade", td=0.2, tex=GFX)
    t_roca = w("roca", 555.0)
    add(t_roca - 0.15, kb("u_aVNcT0obqtQ.jpg", "punch", "cold"), [BigText("UNA ROCA", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(w("desnivel", 556.0) - 0.15, kb("u_y8ax9FcLtes.jpg", "punch", "cold"), [BigText("UN DESNIVEL", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(w("barandal", 557.0) - 0.15, kb("f_5456619127.jpg", "punch", "cold"), [BigText("UN BARANDAL", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(w("camion", 558.3) - 0.15, kb("u_L6Ln7ViU6Bs.jpg", "punch", "cold"), [BigText("UN CAMIÓN", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(559.42, kb("u_DvSdq5JcMfE.jpg", "r", "doc"), [rich("EL VIENTO TIENE DÓNDE AGARRAR FUERZA", ("fuerza",), 0.2, y=0.82, size=54)], tex=CLEAN)
    add(561.98, kb("l_33146.jpg", "l", "doc"), [rich("MILLAS Y MILLAS SIN UN SOLO ÁRBOL", ("árbol",), 0.6, y=0.82, size=54)], tex=CLEAN)
    add(567.26, kb("f_54182264076.jpg", "punch", "cold"), [Counter(0, 11000, "+{:,.0f} PIES", "ELK MOUNTAIN · SE ALZA SOLA", 0.3, 1.2, (0.5, 0.42), 150)], tex=CLEAN)
    add(570.62, mp("loc", [(0, -106.5, 41.64, 1.0), (5.0, -106.5, 41.64, 1.04)],
                   [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=7), dict(type="pin", at="elk_mtn", t0=0.0, pulse=False, color=WHITE)]),
        [flow_over_elk(1.0, 0.2, (-106.5, 41.64)), Caption("Como tapar con el dedo la punta de una manguera", None, 1.0, None, 0.88)], tex=GFX)
    add(575.56, kb("u_scbYOgVyb8Q.jpg", "in", "dark"), [Darken(0.45), FnOverlay(G3.gauge, value=60, unit="MPH", sub="≈ 100 KM/H · RACHAS EN INVIERNO")], tex=DARK)
    t_des = w("desniveles", 588.3)
    add(581.68, cus(G3.snow_section, mode="road", tag_t0=t_des - 581.68), tr="fade", td=0.3, tex=GFX)
    add(593.32, cus(G3.snow_section, mode="trap"), [BigText("CADA UNA ES UNA TRAMPA", "bebas", 60, RED, (0.5, 0.92), 0.1, None, "up", tracking=4)], tex=GFX)
    add(595.22, Split([kb("f_49160451161.jpg", "in", "cold"), kb("u_7CffibpcnuI.jpg", "in", "cold")], labels=["EL CAMPO: CASI PELADO", "LA CARRETERA: 4 PIES"]),
        tr="whip_l", td=0.3, tex=CLEAN)
    add(602.36, mp("loc", [(0, -106.3, 41.6, 0.8), (5.8, -106.4, 41.62, 0.9)],
                   [lay(US30_LOC, t0=0.0, draw=0.01, color=(150, 150, 150), width=5), lay(I80_LOC, t0=0.0, draw=0.01, color=RED, width=10),
                    dict(type="label", at=(-106.3, 41.38), text="EL TERRENO MÁS EXPUESTO", t0=0.8, size=54, box=True)]),
        [flow_over_elk(0.8, 0.0, (-106.3, 41.6))], tex=GFX)
    add(608.14, mp("loc", [(0, -106.2, 41.78, 0.72), (5.4, -106.2, 41.8, 0.76)],
                   [lay(I80_LOC, t0=0.0, draw=0.01, color=(150, 150, 150), width=5), lay(US30_LOC, t0=0.0, draw=1.0, color=WHITE, width=9)] + TOWNS3 +
                   [dict(type="label", at=(-106.2, 42.06), text="NUNCA TUVO ESE PROBLEMA", t0=1.6, size=52, box=True)]), tr="fade", td=0.3, tex=GFX)
    add(613.52, kb("u_rxLGSOM0e3U.jpg", "in", "cold"), [Badge("VALLAS CONTRA LA NIEVE · DESDE LOS AÑOS 20", 0.3, None)], tex=CLEAN)
    add(w("listones", 617.0) - 0.3, kb("u_lAcrtTbS4xo.jpg", "l", "cold"), [rich("LISTONES DE MADERA DE POCOS PIES", ("pocos",), 0.3, y=0.84, size=52)], tex=CLEAN)
    add(621.34, cus(G3.snow_section, mode="fence"), tr="fade", td=0.3, tex=GFX)
    t_cuatro = w("cuatro", 639.0)
    add(632.5, cus(G3.fence_math, t2=w("doble", 635.9) - 632.5, final_t=t_cuatro - 632.5), tr="fade", td=0.3, tex=GFX)
    add(640.36, kb("l_47857.jpg", "in", "doc"), [rich("SE LLENABAN EN UN DÍA", ("día",), 0.4, y=0.78, size=58), Stamp("DE ADORNO", w("adorno", 645.2) - 640.36, RED, (0.5, 0.55), -8, 100)],
        tex=CLEAN)
    add(646.16, kb("u_R7-X7O0Wjcs.jpg", "in", "cold"), [rich("CADA VALLA LLENA TENÍA UN PRECIO", ("precio",), 0.3, y=0.82, size=56)], tex=CLEAN)
    add(649.66, vid("gov.dot.fhwa.ttp.vh-157", 652.0, 2.4, "cold_bw"), [Badge("CAMIONEROS VARADOS", 0.1, None)], tex=VHS)
    add(w("quita", 652.2) - 0.1, kb("u_Ls2fcCP0IB4.jpg", "in", "night"), [Badge("QUITANIEVES TODA LA NOCHE", 0.1, None)], tex=DARK)
    add(w("pueblos", 654.4) - 0.1, kb("u_azcw0YOnYVc.jpg", "in", "cold"), [Badge("PUEBLOS ESPERANDO MERCANCÍA", 0.1, None)], tex=CLEAN)
    add(656.96, kb("u_1RE_PkB9n4Y.jpg", "in", "cold"), [BigText("TODO PARA AHORRAR 19 MILLAS", "bebas", 84, WHITE, (0.5, 0.5), 0.2, None, "up", tracking=6)], tex=CLEAN)

    # ============================== CAP 5: LA FIRMA (659.62 - 788.9)
    bg, ov = chapter(5, "La firma", "u_OQMZwNd3ThU.jpg", "dark", "1959")
    add(659.62, bg, ov, tr="flash", td=0.25, tex=CLEAN)
    add(662.6, kb("u_XWW746i6WoM.jpg", "in", "doc"), [rich("WASHINGTON LE PASÓ POR ENCIMA", ("encima",), 0.2, y=0.82, size=56)], tex=CLEAN)
    add(665.06, kb("u_y02jEX_B0O0.jpg", "in", "warm"), [rich("PERO HAY UN PAPEL QUE LA COMPLICA", ("papel",), 0.2, y=0.84, size=54)], tex=ARCH)
    add(667.46, kb("u_Qdbzh5KJWTo.jpg", "in", "night"), [Darken(0.3), BigText("ANTES, UNA COSA", "bebas", 90, WHITE, (0.5, 0.5), 0.2, None, "up", tracking=6)], tex=DARK)
    add(670.38, vid("rpsnowroad", 230.0, 3.0, "faded"), [Badge("1970 · NADIE AVISABA", 0.2, None)], tex=FILM)
    add(w("enteraban", 676.6) - 0.3, kb("u_zvNNtHa7-Zk.jpg", "punch", "cold"), tex=CLEAN)
    add(678.72, kb("u_scbYOgVyb8Q.jpg", "in", "dark"), [Darken(0.5), FnOverlay(G2.subscribe), BigText("AQUÍ SÍ TE AVISAMOS", "bebas", 80, YELLOW, (0.5, 0.33), 0.1, None, "up", tracking=6)],
        tr="fade", td=0.3, tex=DARK)
    add(685.38, kb("u_y02jEX_B0O0.jpg", "punch", "warm"), [BigText("Y AHORA, EL PAPEL", "bebas", 84, WHITE, (0.5, 0.8), 0.1, None, "up", tracking=6)], tex=ARCH)
    t_apr = w("aprobo", 693.6)
    add(687.36, cus(G3.document, lines=[("WYOMING STATE HIGHWAY COMMISSION", 40), ("VERANO DE 1959", 34), ("TRAZADO INTERSTATE 80:", 34),
                                       ("LARAMIE – WALCOTT, VÍA ARLINGTON", 34), ("RESOLUCIÓN: APROBADO", 34)], sign_t=t_apr - 687.36 - 0.6),
        [Stamp("APROBADO", t_apr - 687.36 + 0.7, RED, (0.62, 0.62), -10, 120)], tr="fade", td=0.3, tex=ARCH)
    add(695.84, vid("HighwayH1956", 255.0, 2.5, "bw"), [BigText("LA MISMA QUE HABÍA DICHO QUE NO", "bebas", 60, WHITE, (0.5, 0.84), 0.1, None, "up", tracking=4)], tex=FILM)
    add(698.42, vid("HighwayH1956", 122.0, 1.7, "bw"), [Badge("IMAGÍNATE ESA MESA", 0.1, None)], tex=FILM)
    add(700.12, kb("u_y02jEX_B0O0.jpg", "punch", "warm"), [rich("TRES AÑOS PELEANDO CONTRA ESA LÍNEA", ("tres", "años"), 0.3, y=0.84, size=52)], tex=ARCH)
    add(703.94, kb("u_OQMZwNd3ThU.jpg", "punch", "warm"), [rich("FIRMANDO LO QUE JURARON QUE FRACASARÍA", ("fracasaría",), 0.6, y=0.84, size=52)], tex=ARCH)
    add(708.62, vid("HighwayH1956", 810.0, 4.0, "bw"), [rich("UNA PREGUNTA DEL PROPIO ESTADO", ("pregunta",), 0.3, y=0.86, size=50)], tex=FILM)
    add(712.64, kb("l_33082.jpg", "r", "doc"), [Badge("WYOMING SALE A LA CARRETERA", 0.3, None)], tex=CLEAN)
    t_9 = w("nueve", 719.2)
    add(716.08, cus(G3.survey, big_t=t_9 - 716.08 + 0.3, sub_t=w("pensaban", 723.7) - 716.08), tr="fade", td=0.3, tex=GFX)
    add(728.6, kb("u_HA0Rgl-ISko.jpg", "in", "sepia"), [rich("BUSCÓ UNA PRUEBA Y ENCONTRÓ LA DE WASHINGTON", ("washington",), 0.3, y=0.82, size=50)], tex=ARCH)
    add(733.16, kb("u_ylNoOK6ylHg.jpg", "in", "sepia"), [rich("NO FUE SOLO UN MAPA EN LA PARED", ("mapa",), 0.4, y=0.84, size=54)], tex=ARCH)
    add(738.4, mp("loc", [(0, -106.25, 41.6, 0.82), (3.7, -106.25, 41.6, 0.86)], [lay(I80_LOC, t0=0.0, draw=1.4, color=YELLOW, width=9)]),
        [rich("UNA LÍNEA RECTA QUE CASI TODOS ACEPTARON", ("aceptaron",), 0.3, y=0.15, size=52)], tr="fade", td=0.3, tex=GFX)
    add(w("dibujaron", 743.4) - 0.2, kb("u_AFB6S2kibuk.jpg", "punch", "sepia"), [BigText("LA DIBUJARON", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=ARCH)
    add(w("firmaron", 744.6) - 0.2, kb("u_y02jEX_B0O0.jpg", "punch", "warm"), [BigText("LA FIRMARON", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=ARCH)
    add(w("automovilistas", 745.9) - 0.2, vid("202248_Freeway_Driving", 58.0, 1.9, "faded"), [BigText("LA PEDÍAN", "bebas", 80, WHITE, (0.5, 0.8), 0.0, None, "pop", tracking=6)], tex=FILM)
    add(747.74, kb("u_VoWBZW9xA7U.jpg", "in", "cold"), [snow2, BigText("EL ÚNICO EN DESACUERDO: EL VIENTO", "bebas", 70, WHITE, (0.5, 0.5), 0.8, None, "up", tracking=4)],
        tex=CLEAN, post=postshake(2))
    add(750.52, kb("u_pPkzZYG0veM.jpg", "in", "sepia"), [Badge("OTRA VERSIÓN, MÁS CÓMODA", 0.3, None)], tex=ARCH)
    add(755.9, vid("1965-01-25_Inauguration_Highlights", 20.0, 5.0, "bw"), [LowerThird("LADY BIRD JOHNSON", "Esposa del presidente Lyndon B. Johnson", 0.6)], tex=FILM)
    add(761.26, kb("u_cejIF5AIAys.jpg", "in", "doc"), [rich("¿SOBREVOLÓ LA ZONA Y PIDIÓ LA RUTA CON MEJORES VISTAS?", ("vistas?",), 0.3, y=0.82, size=48)], tex=CLEAN)
    add(766.14, kb("u_Oaqk7qqNh_c.jpg", "in", "warm"), [Stamp("MITO", w("sostiene", 769.3) - 766.14, RED, (0.5, 0.5), -10, 170)], tex=ARCH)
    add(770.48, cus(G3.lady_bird_timeline), tr="fade", td=0.3, tex=GFX)
    add(777.16, fr("f_5369979271.jpg", "Lady Bird Johnson", g="bw"), [Stamp("NUNCA VOLÓ SOBRE ESE TRAMO", 1.4, RED, (0.5, 0.82), -6, 70)], tex=ARCH)
    add(781.52, kb("l_36455.jpg", "in", "cold"), [rich("EL VIENTO SEGUÍA AHÍ, CADA INVIERNO", ("invierno",), 0.3, y=0.82, size=56)], tex=CLEAN)
    add(785.78, kb("l_32860.jpg", "in", "doc"), [rich("IBA A OBLIGAR A WYOMING A INVENTAR ALGO", ("inventar",), 0.2, y=0.82, size=52)], tex=CLEAN)

    # ============================== CAP 6: VALLAS Y BARRERAS (788.9 - 882.4)
    bg, ov = chapter(6, "Vallas y barreras", "l_48974.jpg", "dark", "1971")
    add(788.9, bg, ov, tr="flash", td=0.25, tex=CLEAN)
    add(791.56, vid("gov.dot.fhwa.ttp.vh-286", 358.0, 5.5, "doc"), [LowerThird("RONALD TABLER", "Investigador del Servicio Forestal de EE. UU.", w("ronald", 795.6) - 791.56)], tex=VHS)
    add(797.2, vid("gov.dot.fhwa.ttp.vh-286", 233.0, 5.3, "cold", zoom0=1.5, zoom1=1.6, cx=0.45, cy=0.38), [rich("EL MEJOR LABORATORIO QUE PODÍA PEDIR", ("laboratorio",), 1.0, y=0.84, size=52)], tex=VHS)
    add(802.6, vid("gov.dot.fhwa.ttp.vh-286", 389.0, 3.8, "doc"), tex=VHS)
    add(806.4, vid("gov.dot.fhwa.ttp.vh-286", 545.0, 3.7, "doc"), [Badge("CON ESOS DATOS DISEÑÓ OTRA VALLA", 0.1, None)], tex=VHS)
    add(810.16, vid("gov.dot.fhwa.ttp.vh-286", 856.5, 3.6, "doc"), [Counter(0, 12, "+{:.0f} PIES", "≈ 4 METROS DE ALTO", 0.2, 0.9, (0.5, 0.42), 170)], tex=VHS)
    add(813.78, kb("f_5925425024.jpg", "in", "doc"), [rich("VIGAS EN DIAGONAL CONTRA EL VIENTO", ("diagonal",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("enterrada", 817.6) - 0.3, vid("gov.dot.fhwa.ttp.vh-286", 888.0, 1.9, "doc"), tex=VHS)
    add(819.32, vid("gov.dot.fhwa.ttp.vh-286", 950.0, 4.8, "doc"), [rich("A UNA DISTANCIA CALCULADA, NO ADIVINADA", ("calculada",), 0.6, y=0.88, size=48)], tex=VHS)
    add(824.1, kb("f_52942752461.jpg", "in", "doc"), [Counter(0, 11, "{:.0f} MILLAS", "LAS PRIMERAS · 1971", 0.3, 0.9, (0.5, 0.42), 160)], tex=CLEAN)
    add(w("decenas", 828.6) - 0.3, vid("gov.dot.fhwa.ttp.vh-287", 175.0, 3.2, "doc"), [rich("DESPUÉS, DECENAS DE MILLAS MÁS", ("decenas",), 0.2, y=0.84, size=54)], tex=CLEAN)
    add(831.58, cus(G3.stats_panel, items=[("−50%", "GASTO EN QUITAR NIEVE", 0.3), ("−70%", "ACCIDENTES", w("accidentes", 836.8) - 831.58),
                                         ("< 10", "AÑOS PARA PAGARSE", w("pagaron", 840.6) - 831.58)], title="DONDE SE PUSIERON LAS VALLAS"),
        tr="fade", td=0.3, tex=GFX)
    add(844.42, kb("f_5457226056.jpg", "in", "doc"), [Badge("WYOMING · COLORADO · UTAH", 0.3, None)], tex=CLEAN)
    add(848.28, kb("f_52890415114.jpg", "l", "doc"), [rich("FILAS DE VALLAS ALTAS Y OSCURAS", ("oscuras",), 0.3, y=0.84, size=54)], tex=CLEAN)
    add(w("vaca", 851.9) - 0.3, kb("f_54194292409.jpg", "in", "doc"), [BigText("YA SABES DE DÓNDE SALIERON", "bebas", 66, WHITE, (0.5, 0.84), 1.0, None, "up", tracking=4)], tex=CLEAN)
    add(855.1, kb("u_IdaRwQkKptc.jpg", "in", "dark"), [rich("LA OTRA SOLUCIÓN FUE MÁS DURA", ("dura",), 0.1, y=0.82, size=56)], tex=DARK)
    add(856.72, kb("f_54558448783.jpg", "in", "doc"), [gate(t0=w("barreras", 861.0) - 856.72 - 0.4),
                                                      BigText("BARRERAS", "bebas", 110, WHITE, (0.5, 0.3), w("barreras", 861.0) - 856.72, None, "pop", tracking=8)], tex=CLEAN)
    add(862.72, mp("loc", [(0, -106.2, 41.55, 0.72), (3.7, -106.2, 41.55, 0.75)],
                   [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8),
                    dict(type="gate", at="laramie", t0=0.4, label="LARAMIE", side="l"),
                    dict(type="gate", at="walcott", t0=w("walcott", 864.8) - 862.72, label="WALCOTT JCT.", side="r")]), tr="fade", td=0.3, tex=GFX)
    add(866.38, kb("u_zvNNtHa7-Zk.jpg", "in", "cold"), [rich("NO UN LETRERO QUE CUALQUIERA PODÍA IGNORAR", ("ignorar",), 0.4, y=0.84, size=50)], tex=CLEAN)
    add(871.08, kb("u_IdaRwQkKptc.jpg", "in", "cold"), [rich("HOY SON NORMALES EN EL NORTE DEL PAÍS", ("normales",), 0.3, y=0.84, size=52)], tex=CLEAN)
    add(875.36, kb("u_scbYOgVyb8Q.jpg", "in", "dark"), [Darken(0.5)] + question("Si Wyoming aprendió tanto, ¿por qué esta autopista sigue cerrando?", ("cerrando?",)),
        tr="glitch", td=0.3, tex=DARK)

    # ============================== CAP 7: HOY (882.4 - 1046.56)
    bg, ov = chapter(7, "Hoy", "u_bd8cp1NAago.jpg", "cold", "2026")
    add(882.4, bg, ov, tr="flash", td=0.25, tex=CLEAN)
    add(884.84, kb("u_JMGBUi2WWEs.jpg", "in", "night"),
        [BigText("LUNES 18 DE MAYO DE 2026", "bebas", 70, WHITE, (0.5, 0.2), 0.3, None, "up", tracking=6),
         BigText("02:00", "mono", 150, YELLOW, (0.5, 0.78), w("dos", 891.6) - 884.84 - 0.2, None, "pop")], tex=DARK)
    add(w("linea", 892.3) - 0.2, kb("u_u13zBF4r56A.jpg", "in", "night"), [FnOverlay(lambda im, t, d: G2.lights_off(im, t, d, 1.6, 1.4)),
                                                                     Badge("APAGÓN: RAWLINS · SINCLAIR · WAMSUTTER", 0.3, None)], tex=DARK)
    add(897.34, mp("wy", [(0, -107.0, 41.5, 0.8), (6.0, -107.0, 41.5, 0.84)],
                   [dict(type="road", name="80", level="Interstate", bbox=(-109.3, 40.4, -104.75, 42), t0=0.6, draw=2.2, color=RED, width=10),
                    dict(type="pin", at="rock_springs", t0=0.3, label="ROCK SPRINGS", side="b", color=RED),
                    dict(type="pin", at="cheyenne", t0=1.6, label="CHEYENNE", side="b", color=RED),
                    dict(type="label", at=(-107.0, 42.25), text="CERRADA EN LOS DOS SENTIDOS", t0=1.4, size=54, box=True)]),
        [Counter(0, 200, "+{:.0f} MILLAS", "DE GOLPE", w("son", 903.7) - 897.34, 1.0, (0.5, 0.83), 120)], tr="fade", td=0.3, tex=GFX)
    add(906.38, kb("u_R7-X7O0Wjcs.jpg", "in", "cold"), [rich("CIENTOS DE CAMIONEROS VARADOS", ("varados",), 0.2, y=0.84, size=56)], tex=CLEAN)
    add(908.82, kb("u_vjeGHRAf-YQ.jpg", "in", "night"), [Badge("RAWLINS · 05:30", 0.2, None)], tex=DARK)
    add(912.5, kb("u_wCWqEBMjkMA.jpg", "in", "cold"),
        [Rich([("6 HORAS PARADA", 0.2, "h"), ("·", 1.4, "n"), ("NO VEÍA NADA", 1.6, "n"), ("·", 3.0, "n"), ("¼ DE TANQUE", 3.4, "r")], 0.5, 0.82, 0.86, 58)], tex=CLEAN)
    add(918.92, kb("u_5DXpcrNBG48.jpg", "in", "cold"), [Counter(0, 11, "{:.0f} HORAS", "DETENIDO ENTRE WAMSUTTER Y RAWLINS", 0.3, 1.0, (0.5, 0.42), 170)], tex=CLEAN)
    add(925.86, kb("u_ljU7DhGiF10.jpg", "in", "doc"), [Badge("ÁREA DE DESCANSO DE WAGONHOUND", 0.2, None)], tex=CLEAN)
    add(w("golpeado", 929.6) - 0.6, kb("u_M3ZAMByBMrQ.jpg", "punch", "cold"), [Stamp("QUITANIEVES GOLPEADO", 0.6, RED, (0.5, 0.5), -8, 90)], tex=CLEAN, post=postshake(3))
    add(932.86, kb("u_7CffibpcnuI.jpg", "in", "cold"), [Badge("MEDIODÍA · EN PLENO MAYO", 0.2, None), rich("MONTONES DE NIEVE DE 4 PIES", ("4", "pies"), 1.4, y=0.84, size=54)], tex=CLEAN)
    add(939.6, kb("u_jbA2kQI0lx4.jpg", "in", "cold"), [Badge("HOY: CIERRE POR ETAPAS", 0.2, None)], tex=CLEAN)
    add(941.6, kb("f_52886340247.jpg", "in", "night"), [Badge("ETAPA 1 · VEHÍCULOS ALTOS Y LIGEROS", 0.2, None)], tex=DARK)
    add(947.94, kb("u_cJKUzAgHwpA.jpg", "punch", "cold"), [rich("EL VIENTO LOS VOLTEA COMO SI FUERAN DE CARTÓN", ("cartón",), 0.2, y=0.84, size=50)], tex=CLEAN, post=postshake(6))
    add(951.02, kb("u_phv0kzqMJyk.jpg", "in", "cold"), [gate(t0=0.3), Badge("ETAPA 2 · TODOS", 0.2, None)], tex=CLEAN)
    add(954.16, kb("u_scbYOgVyb8Q.jpg", "in", "dark"), [Darken(0.5)] + question("¿Por qué cerrar también la carretera alternativa?", ("alternativa?",), y=0.5),
        tr="glitch", td=0.3, tex=DARK)
    t_tam = w("tambien", 964.3)
    add(959.98, mp("loc", [(0, -106.2, 41.7, 0.66), (6.0, -106.2, 41.7, 0.7)],
                   [lay(I80_LOC, t0=0.0, draw=0.6, color=RED, width=9), dict(type="gate", at="laramie", t0=0.5), dict(type="gate", at="walcott", t0=0.7),
                    lay(US30_LOC, t0=t_tam - 959.98, draw=0.6, color=RED, width=9),
                    dict(type="label", at=(-106.2, 41.98), text="POR NORMA", t0=w("norma", 966.4) - 959.98, size=60, box=True)] + TOWNS3), tr="fade", td=0.3, tex=GFX)
    add(967.88, cus(G3.truck_queue), tr="fade", td=0.3, tex=GFX)
    add(977.74, kb("u_azcw0YOnYVc.jpg", "in", "cold"), [rich("UNA CALLE PRINCIPAL · DOS CARRILES · NIEVE", ("dos", "carriles"), 0.6, y=0.84, size=52)], tex=CLEAN)
    add(w("cientos", 979.6), kb("l_47658.jpg", "in", "doc"), [Badge("PUEBLOS DE UNOS CIENTOS DE VECINOS", 0.2, None)], tex=CLEAN)
    add(984.84, mp("loc", [(0, -106.2, 41.75, 0.66), (5.8, -106.2, 41.78, 0.7)],
                   [lay(I80_LOC, t0=0.0, draw=0.01, color=RED, width=8), dict(type="gate", at="laramie", t0=0.0, pulse=False),
                    lay(US30_LOC, t0=0.6, draw=1.0, color=YELLOW, width=8, traffic=26, speed=160)] + TOWNS3 +
                   [dict(type="label", at=(-106.2, 42.0), text="TODOS POR AQUÍ", t0=1.6, size=56, box=True)]), tr="fade", td=0.3, tex=GFX)
    add(990.66, kb("u_IdaRwQkKptc.jpg", "in", "cold"), [gate(t0=0.4), Stamp("CERRADA CON CANDADO", w("candado", 993.9) - 990.66, RED, (0.5, 0.42), -6, 90)], tex=CLEAN)
    add(996.68, kb("u_H2UzCyX32p4.jpg", "in", "doc"), [rich("MUCHOS HABLAN ESPAÑOL", ("español",), 0.3, y=0.84, size=62)], tex=CLEAN)
    add(1001.0, kb("u_PNb6Zn-f5R4.jpg", "in", "dark"),
        [FnOverlay(G3.chat_overlay, msgs=[("Rigo", "¿Cómo va la I-80 en Arlington?"), ("Toño", "Cerrada desde Laramie"),
                                          ("Luis", "Cielo blanco sobre Elk Mountain"), ("Don Beto", "Mejor espérense en Laramie")],
                   x=0.6, t0=0.4, every=1.6), Caption("Ilustración", None, 0.4, None, 0.95)], tex=DARK)
    add(1008.9, kb("f_54182264076.jpg", "in", "cold"), [Badge("SI VES EL CIELO BLANCO SOBRE ELK MOUNTAIN…", 0.2, None)], tex=CLEAN)
    add(w("espera", 1011.6) - 0.2, kb("u_nhvGR3-6vJY.jpg", "in", "cold"), [rich("MEJOR ESPERA EN LARAMIE", ("laramie",), 0.2, y=0.84, size=62)], tex=CLEAN)
    add(1015.54, kb("u_HA0Rgl-ISko.jpg", "in", "sepia"), [rich("LA DISCUSIÓN DE 1956 SIGUE ABIERTA", ("1956",), 0.3, y=0.82, size=56)], tex=ARCH)
    add(1020.28, mp("loc", [(0, -106.2, 41.7, 0.66), (8.5, -106.2, 41.78, 0.72)],
                    [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=7),
                     dict(type="route", path=["laramie", "bosler", "rock_river", "medicine_bow", (-106.35, 41.93), "hanna", (-106.70, 41.83), "walcott"],
                          t0=w("segunda", 1024.3) - 1020.28, draw=2.4, color=WHITE, width=6, dash=22)] + TOWNS3 +
                    [dict(type="label", at=(-106.2, 42.0), text="UNA SEGUNDA RUTA", t0=w("segunda", 1024.3) - 1020.28 + 0.6, size=56, box=True)]),
        tr="fade", td=0.3, tex=GFX)
    add(1035.78, kb("u_luOHcHUkirA.jpg", "in", "doc"), [Counter(0, 6000, "{:,.0f} MILLONES", "DE DÓLARES", 0.2, 1.2, (0.5, 0.45), 170, color=YELLOW)], tex=CLEAN)
    add(1038.84, cus(G3.cost_compare), tr="fade", td=0.3, tex=GFX)

    # ============================== CONCLUSIÓN (1046.56 - end)
    add(1046.56, kb("u_ylNoOK6ylHg.jpg", "in", "sepia"), [Badge("WASHINGTON · EL MAPA EN LA PARED", 0.3, None)], tr="fade", td=0.6, tex=ARCH)
    add(1051.42, mp("loc", [(0, -106.25, 41.55, 0.86), (7.0, -106.25, 41.55, 0.92)], [lay(I80_LOC, t0=0.0, draw=1.2, color=YELLOW, width=9)]),
        [Rich([("UNA", 2.5, "n"), ("LÍNEA", 2.62, "n"), ("RECTA", 2.74, "h"), ("·", 3.4, "n"), ("19", 3.6, "h"), ("MILLAS", 3.72, "n"),
               ("MENOS", 3.84, "n"), ("·", 4.4, "n"), ("CASI", 4.6, "n"), ("TODOS", 4.72, "n"), ("DE", 4.84, "n"), ("ACUERDO", 4.96, "h")], 0.5, 0.15, 0.9, 52)],
        tr="fade", td=0.3, tex=GFX)
    add(1058.54, kb("u_AFB6S2kibuk.jpg", "in", "sepia"), [BigText("EN EL PAPEL, LO ERA.", "serif", 84, WHITE, (0.5, 0.5), 0.2, None, "up")], tex=ARCH)
    add(1060.68, kb("u_scbYOgVyb8Q.jpg", "in", "dark"), [Darken(0.5)] + question("¿Por qué levantar una carretera que ya sabían que iba a fallar?", ("fallar?",)),
        tr="glitch", td=0.3, tex=DARK)
    add(1066.82, vid("202248_Freeway_Driving", 35.0, 2.1, "faded"), [BigText("UNA LEY PEDÍA RUTAS DIRECTAS", "bebas", 64, WHITE, (0.5, 0.84), 0.1, None, "up", tracking=4)], tex=FILM)
    add(1068.98, vid("202248_Freeway_Driving", 104.0, 3.4, "faded"), [BigText("LOS AUTOMOVILISTAS QUERÍAN LLEGAR ANTES", "bebas", 60, WHITE, (0.5, 0.84), 0.1, None, "up", tracking=4)], tex=FILM)
    add(w("mapa", 1072.4) - 0.3, mp("loc", [(0, -106.25, 41.6, 0.85), (4.6, -106.25, 41.6, 0.9)],
                                    [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8),
                                     dict(type="label", at="arlington", text="UN ESPACIO EN BLANCO", t0=0.8, size=60, box=True, dy=-90)]), tex=GFX)
    add(1076.8, cus(G3.countdown, times=[0.05, 0.1, 0.15, 0.2, 0.25], final_t=0.7), tr="fade", td=0.25, tex=GFX)
    add(1079.4, mp("loc", [(0, -106.4, 41.62, 0.95), (5.5, -106.4, 41.62, 1.0)], [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8)]),
        [flow_over_elk(0.95, 0.2, (-106.4, 41.62))], tex=GFX)
    add(1084.9, kb("u_VoWBZW9xA7U.jpg", "in", "cold"), [snow2, rich("UNA LÍNEA DE OFICINA NO LE IBA A PEDIR PERMISO", ("permiso",), 0.4, y=0.84, size=50)], tex=CLEAN,
        post=postshake(2))
    add(1089.32, mp("loc", [(0, -106.25, 41.6, 0.85), (3.1, -106.25, 41.6, 0.88)], [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8)]),
        [BigText("EN UN MAPA, EL VIENTO NO EXISTE.", "serif", 72, WHITE, (0.5, 0.5), 0.1, None, "up")], tex=GFX)
    add(1092.44, vid("rpsnowroad", 113.0, 2.7, "faded"), [Darken(0.45), BigText("EN ARLINGTON, A VECES ES LO ÚNICO QUE EXISTE.", "serif", 56, WHITE, (0.5, 0.5), 0.1, None, "up")],
        tex=FILM, post=postshake(2))
    add(1095.12, mp("loc", [(0, -106.25, 41.6, 0.85), (5.8, -106.25, 41.6, 0.9)], [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8)]),
        [FnOverlay(G3.phone_overlay), BigText("LA LÍNEA SIGUE AHÍ", "bebas", 64, WHITE, (0.5, 0.06), 1.0, None, "up", tracking=4)], tex=GFX)
    add(w("vallas", 1102.3) - 0.2, kb("f_52942752461.jpg", "in", "doc"), [BigText("LAS VALLAS", "bebas", 84, WHITE, (0.5, 0.82), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(w("barreras", 1103.6) - 0.2, kb("u_IdaRwQkKptc.jpg", "in", "cold"), [BigText("LAS BARRERAS", "bebas", 84, WHITE, (0.5, 0.82), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(w("camiones", 1105.3) - 0.2, kb("u_R7-X7O0Wjcs.jpg", "in", "cold"), [BigText("LOS CAMIONES ESPERANDO", "bebas", 84, WHITE, (0.5, 0.82), 0.0, None, "pop", tracking=6)], tex=CLEAN)
    add(1107.64, mp("loc", [(0, -106.3, 41.6, 0.82), (3.2, -106.3, 41.6, 0.85)],
                    [lay(I80_LOC, t0=0.0, draw=0.01, color=YELLOW, width=8), dict(type="gate", at="laramie", t0=0.2), dict(type="gate", at="walcott", t0=0.3)]),
        [flow_over_elk(0.82, 0.0, (-106.3, 41.6)), BigText("EL VIENTO, DIBUJADO POR FIN", "serif", 70, WHITE, (0.5, 0.14), 0.4, None, "up")], tex=GFX)
    add(1110.82, kb("u_nhvGR3-6vJY.jpg", "in", "cold"), [Darken(0.35), rich("¿TE TOCÓ ESPERAR FRENTE A LA BARRERA DE LARAMIE?", ("barrera",), 1.6, y=0.42, size=56),
                                                         rich("¿TIENES TU PROPIA CARRETERA MALDITA?", ("maldita?",), w("trailer", 1116.5) - 1110.82, y=0.6, size=56)],
        tr="fade", td=0.4, tex=CLEAN)
    add(1119.36, kb("u_VoWBZW9xA7U.jpg", "out", "dark"),
        [Darken(0.45), BigText("CUÉNTAMELO EN LOS COMENTARIOS", "bebas", 76, YELLOW, (0.5, 0.36), 0.1, None, "pop", tracking=6),
         rich("¿Cuál es la carretera que más miedo te ha dado en invierno?", ("miedo",), 1.9, step=0.09, y=0.56, size=48, maxw=0.8),
         rich("¿Y cuántas horas te tuvo esperando?", ("horas",), 4.5, step=0.09, y=0.7, size=48, maxw=0.8)], tex=DARK)
    return S
