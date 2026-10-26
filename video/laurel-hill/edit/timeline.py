"""The edit: every shot of the Laurel Hill video, synced to the voice-over."""
import bisect
import os

import numpy as np

import gfx2 as G2
import maps as M
from engine import RED, WHITE, YELLOW, ROOT
from gfx import (Badge, BigText, Callout, Caption, CCTV, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Seq, Solid, Split, Stamp, Still, TimelineBar, Video, Counter, background)
from render import Shot
from words import at as w

TOTAL = 1093.25
ARCH = dict(grain=11, dust=0.5, flicker=0.035, vignette=1.0)
FILM = dict(grain=12, dust=0.6, flicker=0.04, vignette=1.0)
CLEAN = dict(grain=4, vignette=0.75)
GFX = dict(grain=3, vignette=0.45)
DARK = dict(grain=6, vignette=1.0)

# ------------------------------------------------------------------ helpers
_SC = {}


def _scenes(film):
    if film not in _SC:
        p = os.path.join(ROOT, "work", "scenes", f"pd_{film}.txt")
        _SC[film] = [0.0] + [float(x) for x in open(p).read().split()] + [1e9]
    return _SC[film]


def clip(film, approx, dur, g="faded", speed=1.0, **kw):
    """Prelinger clip starting near `approx`, kept inside one scene when possible."""
    sc = _scenes(film)
    i = bisect.bisect_right(sc, approx) - 1
    a, b = sc[i], sc[i + 1]
    need = dur * speed + 0.25
    s = approx
    if b - s < need:
        s = max(a + 0.08, b - need)
    return Video(f"pd_{film}.mp4", start=s, speed=speed, grade=g, **kw)


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
    """Chapter title card overlays on a Still background."""
    ovs = [Darken(0.45, 0.0, 0.3),
           BigText(f"CAPÍTULO {num}" + (f"  ·  {year}" if year else ""), "bebas", 46, YELLOW, (0.5, 0.40), 0.1, None, "up", tracking=6),
           BigText(title, "serif", 104, WHITE, (0.5, 0.52), 0.25, None, "up"),
           FnOverlay(_underline, y=0.62, t0=0.5)]
    return kb(bg, "in", g), ovs


def _underline(img, t, dur, y=0.62, t0=0.5, wmax=560):
    import cv2
    from engine import ease_out, prog
    k = ease_out(prog(t, t0, 0.6)) * (1 - prog(t, dur - 0.3, 0.3))
    if k > 0:
        x0 = int(960 - wmax * k)
        cv2.rectangle(img, (x0, int(1080 * y)), (int(960 + wmax * k), int(1080 * y) + 8), YELLOW, -1)


def question(lines, hl, shake=False):
    """Dark concrete card with a typed question; `hl` words highlighted."""
    words = []
    t = 0.15
    for wd in lines.split():
        st = "h" if wd.strip("¿?,.").lower() in hl else "n"
        words.append((wd, t, st))
        t += 0.11
    return [Rich(words, 0.5, 0.5, 0.7, 76)]


def postshake(amt):
    def f(img, t, dur):
        return G2.shake_frame(img, t, amt)
    return f


def map_pa(cams, layers, title=None):
    return M.MapScene("pa", cams, layers, title)


def map_ne(cams, layers, title=None):
    return M.MapScene("ne", cams, layers, title)


LH = M.COORDS["t_laurel"]
TUNNELS = ["t_laurel", "t_allegheny", "t_rays", "t_sideling", "t_tuscarora", "t_kittatinny", "t_blue"]


# ------------------------------------------------------------------ the edit
def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    snow = G2.SnowOverlay(240)
    snow2 = G2.SnowOverlay(200, seed=5, speed=1.4)

    # ============================== INTRO (0 - 65.9)
    add(0.0, kb("u_forest2.jpg", "in", "cold"), [snow, Badge("LAUREL HILL · PENSILVANIA", 0.6, 4.2)], tex=CLEAN)
    add(2.55, kb("u_forest3.jpg", "r", "cold"), [snow], tex=CLEAN)
    add(w("todo", 5.0), kb("u_forest6.jpg", "in", "cold", z=1.05), [snow], tr="fade", td=0.5, tex=CLEAN)
    t_sonar = w("sonar", 9.0)
    add(w("veces", 6.6), kb("u_fog1.jpg", "in", "cold"), [Flash(t_sonar - w("veces", 6.6), 0.25, (255, 255, 255), 0.35)],
        tex=CLEAN, post=lambda im, t, d, ts=t_sonar - w("veces", 6.6): G2.shake_frame(im, t, 6 * min(1, max(0, (t - ts) * 2))))
    add(w("rugido", 10.4), kb("u_fog3.jpg", "in", "dark", z=1.1),
        [FnOverlay(G2.waveform_overlay, y=0.55, amp=1.2), BigText("UN RUGIDO SORDO", "bebas", 64, WHITE, (0.5, 0.22), 0.2, None, "up", tracking=4)],
        tex=DARK, post=postshake(5))
    add(w("vibracion", 13.3), kb("u_forest1.jpg", "down", "cold", z=1.2), [snow2], tex=CLEAN, post=postshake(10))
    t0 = w("viene", 16.2)
    add(t0, kb("c006.jpg", g="archival", cam0=(0.5, 0.5, 1.0), cam1=(0.6, 0.62, 1.55)),
        [Badge("TÚNEL DE LAUREL HILL", 0.4, 2.6)], tr="zoom", td=0.5, tex=ARCH)
    t1964 = w("1964", 19.6)
    add(t1964 - 0.15, kb("u_tun3.jpg", "in", "bw"), [BigText("1964", "bebas", 300, RED, (0.5, 0.5), 0.0, None, "pop", stroke=0),
                                                  Caption("ABANDONADO", None, 0.5)], tr="flash", td=0.25, tex=DARK)
    add(w("autopista", 22.3), kb("u_aband2.jpg", "in", "dark"), tex=DARK)
    add(w("entrada", 24.0), kb("u_door3.jpg", g="bw", cam0=(0.35, 0.5, 1.2), cam1=(0.6, 0.5, 1.2)), [Callout(0.5, 0.45, 0.72, 0.25, "TUBO DE METAL", 0.6)], tex=DARK)
    add(w("porton", 26.6) - 0.1, kb("u_door1.jpg", "punch", "dark"), [Callout(0.47, 0.6, 0.72, 0.3, "PORTÓN DE GARAJE", 0.2)], tex=DARK)
    add(w("curiosear", 29.3) - 0.5, kb("u_lock2.jpg", "punch", "bw"), tr="whip_l", td=0.3, tex=DARK)
    add(w("cerrado", 31.0) - 0.6, kb("u_cam2.jpg", "in", "dark"), tex=DARK)
    add(w("todas", 33.0), kb("c006.jpg", g="bw", cam0=(0.58, 0.6, 1.5), cam1=(0.58, 0.6, 1.62)),
        [CCTV("CAM 03", "LAUREL HILL · PORTAL OESTE")], tr="glitch", td=0.25, tex=dict(grain=2, vignette=0.4))
    add(w("acerca", 35.0) - 0.4, kb("c051.jpg", "punch", "dark"), tex=DARK)
    add(w("normal", 36.8) - 0.2, kb("c027.jpg", "in", "doc"), [Badge("TÚNEL ABANDONADO (SIDELING HILL)", 0.3, 3.6)], tex=CLEAN)
    add(w("tapian", 41.0) - 0.2, kb("c032.jpg", "up", "doc"), tex=CLEAN)
    t_rev = w("reves", 44.0)
    add(w("este", 43.5) - 0.05, Solid("black"), [BigText("ESTE VA AL REVÉS", "bebas", 150, WHITE, (0.5, 0.5), 0.0, None, "pop")],
        tr="flash", td=0.2, tex=GFX)
    add(w("detras", 45.3), cus(G2.mountain, mode="tunnel"), tex=GFX)
    t2003 = w("2003", 50.0)
    add(t2003 - 0.6, kb("u_cam1.jpg", "in", "dark"), [BigText("DESDE 2003", "bebas", 140, YELLOW, (0.5, 0.75), 0.4, None, "pop")], tex=DARK)
    add(w("curioso", 52.4), kb("u_door3.jpg", "l", "dark"), tex=DARK)
    add(w("lugares", 55.2) - 0.2, kb("c087.jpg", "in", "dark"), tr="fade", td=0.5, tex=DARK)
    add(w("otros", 57.6), kb("u_door3.jpg", g="bw", cam0=(0.5, 0.5, 1.05), cam1=(0.5, 0.5, 1.4)), [Darken(0.5, 1.0, 1.0)], tex=DARK)
    add(w("vigilan", 61.0) - 0.45, Solid("concrete"), question("¿Por qué vigilan así un túnel abandonado?", {"vigilan"}),
        tr="black", td=0.4, tex=DARK)
    add(w("ruje", 63.6) - 0.75, Solid("concrete"), question("¿Y qué es lo que ruge ahí dentro?", {"ruge"}),
        tex=DARK, post=lambda im, t, d: G2.shake_frame(im, t, 4 if t > 0.7 else 0))
    # title sting
    add(w("para", 65.9) - 0.9, kb("c006.jpg", "in", "archival"),
        [Darken(0.4, 0, 0.2), BigText("LAUREL HILL", "serif_black", 190, WHITE, (0.5, 0.46), 0.1, None, "zoom"),
         BigText("EL TÚNEL QUE NADIE PUEDE VER", "bebas", 56, YELLOW, (0.5, 0.62), 0.5, None, "up", tracking=8)],
        tr="glitch", td=0.3, tex=ARCH)

    # ============================== CAPÍTULO 1 · 1940 (65.9 - 234.3)
    b, o = chapter(1, "La autopista del futuro", "c001.jpg", "archival", "1940")
    add(w("abandonaron", 68.6) - 0.2, b, o, tr="fade", td=0.5, tex=ARCH)
    add(w("historia", 70.8), kb("c000.jpg", "in", "archival"), [TimelineBar(1930, 2030, 0.1, (0.3, 1.8), start_year=2026, y=0.84)], tex=ARCH)
    t_pitt = w("pittsburgh", 74.5)
    add(t_pitt - 0.9, map_pa([(0, -78.4, 40.3, 0.42), (5, -78.4, 40.3, 0.5)], [
        {"type": "pin", "at": "pittsburgh", "label": "PITTSBURGH", "t0": 0.7, "side": "l"},
        {"type": "pin", "at": "harrisburg", "label": "HARRISBURG", "t0": 1.6},
        {"type": "route", "path": ["pittsburgh", (-79.5, 40.55), (-79.0, 40.3), (-78.7, 40.55), (-78.3, 40.25), (-77.9, 40.5),
                                    (-77.5, 40.25), (-77.2, 40.45), "harrisburg"], "t0": 1.9, "draw": 2.6, "color": (200, 200, 200), "width": 4}],
        "ANTES DE 1940"), tr="whip_l", td=0.35, tex=GFX)
    add(w("curvas", 78.3) - 0.3, Seq([(2.0, clip("ToNewHor1940", 256, 2.0, "archival")), (1.8, clip("Conqueri1937", 88, 1.8, "archival"))]), tex=FILM)
    add(w("allegheny", 81.2) - 0.5, kb("u_fog2.jpg", "l", "doc"), [Caption("ALLEGHENY MOUNTAINS", None, 0.3)], tex=CLEAN)
    add(w("motor", 82.6) - 0.1, clip("Conqueri1937", 120, 1.8, "archival"), tex=FILM)
    t_oct = w("octubre", 84.6)
    add(t_oct - 0.5, kb("c040.jpg", "in", "faded"), [Darken(0.35, 0, 0.1),
        BigText("1 DE OCTUBRE DE 1940", "bebas", 150, WHITE, (0.5, 0.5), 0.1, None, "pop")], tr="flash", td=0.25, tex=ARCH)
    add(w("estreno", 87.0), fr("c040.jpg", None, "faded", slide="r", zoom=(1.0, 1.08)), tex=ARCH)
    add(w("turnpike", 90.2) - 0.4, fr("c039.jpg", "PENNSYLVANIA TURNPIKE", "faded", slide="l", zoom=(1.0, 1.06)), tex=ARCH)
    t160 = w("160", 92.5)
    add(t160 - 0.5, map_pa([(0, -78.45, 40.15, 0.55), (11, -78.45, 40.15, 0.62)], [
        {"type": "state", "name": "Pennsylvania", "t0": 0.0, "width": 3, "color": (150, 150, 150)},
        {"type": "route", "path": M.TURNPIKE, "t0": 0.2, "draw": 3.0, "width": 7},
        {"type": "pin", "at": "irwin", "label": "IRWIN", "t0": w("irwin", 100.5) - t160 + 0.5, "side": "l"},
        {"type": "label", "at": "pittsburgh", "text": "cerca de Pittsburgh", "t0": w("pittsburgh", 101.5) - t160 + 0.5, "dy": -40, "size": 32},
        {"type": "pin", "at": "carlisle", "label": "CARLISLE", "t0": w("carlisle", 103.0) - t160 + 0.5}]),
        [Counter(0, 160, "{:,.0f}", "MILLAS", 0.3, 1.6, (0.5, 0.2), 150, t1=w("kilometros", 96.5) - t160 + 0.3),
         Counter(0, 260, "≈ {:,.0f}", "KILÓMETROS", w("kilometros", 96.5) - t160 + 0.35, 1.0, (0.5, 0.2), 150,
                 t1=w("irwin", 100.5) - t160 - 0.5),
         Rich([("SIN", w("cruces", 97.6) - t160, "n"), ("CRUCES", w("cruces", 97.6) - t160, "h"), ("·", w("semaforos", 98.5) - t160, "n"),
               ("SIN", w("semaforos", 98.5) - t160, "n"), ("SEMÁFOROS", w("semaforos", 98.5) - t160, "h")], 0.5, 0.86, 0.8, 52,
              t1=w("irwin", 100.5) - t160 + 1.5)], tr="whip_l", td=0.35, tex=GFX)
    t_sup = w("superautopista", 105.0)
    add(w("llamaron", 103.8) - 0.1, clip("ToNewHor1940", 744, 3.6, "faded"),
        [Rich([("la", t_sup - w("llamaron", 103.8) - 0.6, "n"), ("primera", t_sup - w("llamaron", 103.8) - 0.4, "n"),
               ("superautopista", t_sup - w("llamaron", 103.8), "h"), ("de", t_sup - w("llamaron", 103.8) + 0.5, "n"),
               ("Estados Unidos", t_sup - w("llamaron", 103.8) + 0.6, "n")], 0.5, 0.8, 0.8, 60, panel=True)], tex=FILM)
    add(w("prisa", 107.8) - 0.3, clip("Conqueri1937", 200, 2.2, "archival"), tex=FILM)
    t1938 = w("1938", 112.0)
    add(w("obras", 110.0) - 0.1, clip("Conqueri1937", 216, 3.0, "archival"), [Badge("OCTUBRE DE 1938", 0.2)], tex=FILM)
    add(w("federal", 113.4) - 0.3, fr("l_unemployed.jpg", "LA GRAN DEPRESIÓN", "archival", zoom=(1.0, 1.07)), tex=ARCH)
    add(w("miles", 116.0) - 0.1, kb("l_drill.jpg", g="archival", cam0=(0.36, 0.6, 1.35), cam1=(0.36, 0.4, 1.35)), [Rich([("menos", w("menos", 118.6) - w("miles", 116.0) + 0.1, "n"),
        ("de", w("menos", 118.6) - w("miles", 116.0) + 0.2, "n"), ("dos años", w("menos", 118.6) - w("miles", 116.0) + 0.3, "h")], 0.5, 0.82, 0.6, 64)], tex=ARCH)
    add(w("sueldo", 122.9) - 1.2, clip("Conqueri1937", 256, 3.0, "archival"), tex=FILM)
    add(w("noche", 124.2) - 0.1, kb("c003.jpg", "l", "archival"), [Badge("LA NOCHE DEL ESTRENO", 0.2)], tex=ARCH)
    add(w("fila", 128.5) - 0.6, clip("Conqueri1937", 80, 3.0, "archival"), [Rich([("autos", 0.4, "n"), ("haciendo", 0.55, "n"), ("fila", 0.7, "h"),
        ("en las casetas de peaje", 0.9, "n")], 0.5, 0.82, 0.8, 56, panel=True)], tex=FILM)
    t19 = w("19", 133.2)
    add(w("pagaron", 131.8) - 0.2, kb("l_drill.jpg", g="archival", cam0=(0.36, 0.5, 1.35), cam1=(0.36, 0.5, 1.55)), [Darken(0.55, 0, 0.5),
        Counter(0, 19, "{:,.0f}", "TRABAJADORES MURIERON EN LAS OBRAS", t19 - w("pagaron", 131.8) + 0.1, 0.8, (0.5, 0.45), 260, color=WHITE)],
        tr="black", td=0.5, tex=ARCH)
    add(w("encontraron", 138.0) - 0.4, clip("ToNewHor1940", 868, 4.2, "faded"), tex=FILM)
    t_lim = w("limite", 143.2)
    add(w("principio", 142.4) - 0.2, clip("Conqueri1937", 272, 2.6, "archival"),
        [Rich([("SIN", t_lim - w("principio", 142.4), "n"), ("LÍMITE DE VELOCIDAD", t_lim - w("principio", 142.4) + 0.1, "h")], 0.5, 0.5, 0.8, 70)], tex=FILM)
    add(w("tuneles", 145.4) - 0.2, kb("c007.jpg", "in", "archival"), tex=ARCH)
    t50 = w("50", 147.6)
    add(t50 - 0.6, kb("u_speed2.jpg", "in", "bw"), [Counter(0, 50, "{:,.0f}", "MILLAS POR HORA", 0.3, 0.9, (0.2, 0.42), 220, color=WHITE),
        Counter(0, 80, "≈ {:,.0f}", "KM/H", w("kilometros", 149.3) - t50 + 0.6, 0.8, (0.2, 0.8), 90, color=YELLOW)], tex=DARK)
    add(w("respetaba", 151.0) - 0.9, clip("GiveYour1954", 137, 1.8, "faded", speed=1.3), tr="whip_l", td=0.3, tex=FILM)
    t_dolar = w("dolar", 154.0)
    add(w("cruzarla", 152.9) - 0.1, kb("c008.jpg", "in", "faded"), [Darken(0.45, 0, 0.2),
        Counter(0, 1.5, "{:,.2f}", "POR CRUZARLA DE PUNTA A PUNTA", t_dolar - w("cruzarla", 152.9), 0.8, (0.5, 0.45), 230, prefix="$", color=YELLOW)], tex=ARCH)
    t150 = w("150", 158.2)
    add(w("primeros", 156.6) - 0.3, clip("Conqueri1937", 81, 4.0, "archival"), [Darken(0.5, 0, 0.3),
        Counter(0, 150000, "{:,.0f}", "VEHÍCULOS EN 15 DÍAS", t150 - w("primeros", 156.6) + 0.1, 1.4, (0.5, 0.45), 200, prefix="+")], tex=FILM)
    add(w("subir", 160.8) - 0.4, cus(G2.mountain, mode="tunnel", seed=7), [], tr="whip_l", td=0.3, tex=GFX)
    t7 = w("siete", 163.6)
    tl = w("laurel", 166.4)
    layers = [{"type": "state", "name": "Pennsylvania", "t0": 0.0, "width": 3, "color": (150, 150, 150)},
              {"type": "route", "path": M.TURNPIKE, "t0": 0.0, "draw": 0.01, "width": 6}]
    for i, tn in enumerate(TUNNELS[::-1]):
        layers.append({"type": "marker", "at": tn, "t0": 0.3 + i * 0.22, "num": 7 - i})
    layers.append({"type": "pin", "at": "t_laurel", "label": "LAUREL HILL", "t0": tl - t7 + 0.1, "box": True, "size": 44})
    add(t7 - 0.3, map_pa([(0, -78.45, 40.08, 0.78), (tl - t7, -78.45, 40.08, 0.8), (tl - t7 + 1.6, -79.2, 40.1, 1.6), (6, -79.22, 40.1, 1.75)], layers,
                         "7 TÚNELES"), tex=GFX)
    t4541 = w("4541", 169.0)
    add(t4541 - 0.5, kb("c006.jpg", g="archival", cam0=(0.5, 0.55, 1.0), cam1=(0.57, 0.62, 1.3)),
        [Darken(0.6, 0, 0.3), Counter(0, 4541, "{:,.0f}", "PIES DE ROCA PERFORADA", 0.3, 1.2, (0.5, 0.42), 200),
         BigText("≈ 1,4 KM", "bebas", 80, YELLOW, (0.5, 0.78), w("kilometro", 171.0) - t4541 + 0.5, None, "pop")], tex=ARCH)
    add(w("magia", 173.6) - 0.9, kb("c008.jpg", "punch", "faded"), [Rich([("aquello", 0.6, "n"), ("era", 0.75, "n"), ("magia", 0.9, "h")], 0.5, 0.84, 0.6, 70)], tex=ARCH)
    add(w("metias", 176.2) - 0.2, kb("u_tent1.jpg", g="faded", cam0=(0.5, 0.55, 1.0), cam1=(0.5, 0.52, 1.7), ease="in"), tex=FILM)
    add(w("salias", 178.4) - 0.2, kb("c007.jpg", g="archival", cam0=(0.5, 0.5, 1.6), cam1=(0.5, 0.5, 1.0), ease="out"), tr="zoom", td=0.5, tex=ARCH)
    # summer 1940 drive
    add(w("imaginate", 181.6) - 0.1, kb("u_car1.jpg", "l", "faded"), [Badge("VERANO DE 1940", 0.3)], tr="flash", td=0.3, tex=FILM)
    add(w("ventanilla", 184.0) - 0.3, clip("Conqueri1937", 104, 2.4, "archival"), tex=FILM)
    add(w("acondicionado", 187.0) - 0.6, kb("u_car2.jpg", "punch", "faded"), tex=FILM)
    add(w("recta", 189.2) - 0.6, kb("c022.jpg", "in", "archival"), tex=ARCH)
    t_sol = w("desaparece", 191.0)
    add(t_sol - 0.1, kb("u_tun3.jpg", "in", "bw"), tr="black", td=0.4, tex=DARK)
    add(w("lamparas", 192.6) - 0.8, kb("c021.jpg", g="warm", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.6), ease="lin"), tex=FILM)
    add(w("eco", 194.0) - 0.1, kb("u_tun1.jpg", g="warm", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.5), ease="lin"), tex=FILM, post=postshake(2))
    add(w("faros", 198.2) - 1.2, kb("u_tun4.jpg", g="warm", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.35), ease="lin"),
        [FnOverlay(G2.flare, t0=0.6, d=1.0)], tex=FILM)
    add(w("milla", 200.2) - 0.6, kb("c004.jpg", "in", "archival"), [Badge("CASI UNA MILLA", 0.2)], tex=ARCH)
    add(w("salir", 202.5) - 0.2, kb("u_fog1.jpg", "l", "doc"), tr="flash", td=0.4, tex=CLEAN)
    add(w("montana", 204.6) - 0.6, kb("c001.jpg", "r", "archival"), tex=ARCH)
    t_ap = w("apodaran", 207.6)
    add(w("raro", 206.2) - 0.3, kb("c008.jpg", "l", "faded"), [Darken(0.6, 0.8, 0.4),
        BigText("«LA AUTOPISTA DE LOS TÚNELES»", "serif_it", 84, WHITE, (0.5, 0.5), w("tuneles", 210.0) - w("raro", 206.2) - 0.2, None, "up")], tex=ARCH)
    t_esc = w("esconder", 213.8)
    add(w("sirve", 211.0) - 0.4, Split([kb("c007.jpg", "in", "archival"), kb("u_lock2.jpg", "in", "bw")], labels=["DEJAR PASAR", "ESCONDER"]), tex=ARCH)
    add(w("1940", 215.6) - 0.5, kb("c006.jpg", "in", "archival"), [Badge("1940: SOLO DEJAR PASAR", 0.2)], tex=ARCH)
    t_lp = w("letra", 219.6)
    add(w("futuro", 218.6) - 0.6, Solid("concrete"), [Rich([("Pero", 0.1, "n"), ("el", 0.2, "n"), ("futuro", 0.3, "n"), ("venía", 0.6, "n"), ("con", 0.8, "n"),
        ("letra", t_lp - w("futuro", 218.6) + 0.6, "h"), ("pequeña", t_lp - w("futuro", 218.6) + 0.75, "h")], 0.5, 0.5, 0.7, 84)], tr="black", td=0.3, tex=DARK)
    add(w("afuera", 222.0) - 0.2, cus(G2.lanes, jam=False), tex=GFX)
    add(w("detalle", 228.0) - 0.3, kb("c006.jpg", g="archival", cam0=(0.5, 0.5, 1.0), cam1=(0.6, 0.62, 1.45)), [Darken(0.75, 0, 1.0)], tex=ARCH)

    # ============================== CAPÍTULO 2 · CUATRO CARRILES, UNA PUERTA (234.3 - 393.8)
    b, o = chapter(2, "Cuatro carriles, una puerta", "u_traf2.jpg", "dark", "1964")
    add(w("exito", 234.5) - 0.2, b, o, tr="glitch", td=0.3, tex=DARK)
    add(w("modelo", 237.6) - 0.3, Seq([(2.4, clip("GiveYour1954", 30, 2.4, "faded")), (2.4, clip("Conqueri1937", 352, 2.4, "archival"))]),
        [Caption("EL MODELO DE LAS INTERESTATALES", None, 0.3)], tex=FILM)
    add(w("cada", 242.4) - 0.1, Seq([(2.6, clip("GiveYour1954", 90, 2.6, "faded")), (2.6, kb("u_truck1.jpg", "l", "faded"))]), tex=FILM)
    add(w("llegaban", 247.7) - 0.1, cus(G2.lanes, jam=True), tr="whip_l", td=0.3, tex=GFX)
    t_puerta = w("puerta", 254.0)
    add(w("filas", 251.5) - 0.3, cus(G2.lanes, jam=True, title="4 FILAS · 1 PUERTA"), tex=GFX)
    add(w("bastaba", 255.8) - 0.1, kb("u_truck2.jpg", "in", "doc"), tex=CLEAN)
    add(w("fila", 259.5) - 0.5, clip("GiveYour1954", 560, 3.4, "faded"), [Rich([("millas", 0.4, "h"), ("hacia", 0.6, "n"), ("atrás", 0.75, "n")], 0.5, 0.82, 0.6, 64)], tex=FILM)
    add(w("domingos", 261.6) - 0.3, clip("GiveYour1954", 1256, 2.4, "faded"), [Badge("LOS DOMINGOS DE AGOSTO", 0.2)], tex=FILM)
    add(w("familias", 263.6) - 0.1, Seq([(2.4, clip("GiveYour1954", 645, 2.4, "faded")), (2.6, clip("GiveYour1954", 625, 2.6, "faded"))]), tex=FILM)
    t_par = w("separaba", 271.6)
    add(w("milla", 270.0) - 0.3, map_pa([(0, -79.1, 40.08, 1.2), (4, -79.18, 40.09, 1.5)], [
        {"type": "route", "path": M.TURNPIKE, "t0": 0.0, "draw": 0.01, "width": 6},
        {"type": "pin", "at": "t_laurel", "label": "LAUREL HILL", "t0": 0.0, "box": True},
        {"type": "route", "path": ["t_laurel", "donegal", "new_stanton"], "t0": 0.8, "draw": 3.0, "color": RED, "width": 11}], "TODO SE PARABA"),
        tex=GFX)
    add(w("hilera", 273.2) - 0.3, kb("u_traf2.jpg", "in", "doc"), tex=CLEAN)
    add(w("curva", 277.3) - 0.6, kb("u_traf1.jpg", "l", "doc"), tex=CLEAN)
    add(w("peaton", 279.4) - 0.6, clip("GiveYour1954", 600, 2.6, "faded"), tex=FILM)
    add(w("media", 281.6) - 0.1, kb("c004.jpg", "in", "archival"), tex=ARCH)
    add(w("tragandose", 284.0) - 0.1, clip("Conqueri1937", 497.5, 2.6, "archival"), tex=FILM)
    add(w("encima", 286.6) - 0.2, kb("c021.jpg", "in", "warm"), [Callout(0.5, 0.62, 0.72, 0.32, "SIN SEPARACIÓN", 0.6)], tex=FILM)
    add(w("carril", 290.0) - 0.3, cus(G2.tunnel_section), tr="whip_l", td=0.3, tex=GFX)
    add(w("trailer", 294.9) - 0.6, kb("u_tun4.jpg", g="dark", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.4), ease="lin"),
        [FnOverlay(G2.flare, t0=0.8, d=1.0)], tex=FILM)
    add(w("maravilla", 299.6) - 0.6, kb("c008.jpg", "in", "faded"), [Badge("1940: UNA MARAVILLA", 0.2)], tex=ARCH)
    add(w("miedo", 302.6) - 0.9, kb("u_tun3.jpg", "punch", "bw"), [Badge("1960: DABA MIEDO", 0.1, None, color=RED)], tr="glitch", td=0.25, tex=DARK)

    # ---- simpler pace from here
    add(w("comision", 304.0) - 0.4, kb("c007.jpg", "in", "archival"), [Rich([("duplicar", 0.8, "h"), ("los", 1.0, "n"), ("túneles", 1.1, "n")], 0.5, 0.84, 0.6, 66)], tex=ARCH)
    t_cu = w("cuatro", 307.0)
    lay = [{"type": "route", "path": M.TURNPIKE, "t0": 0.0, "draw": 0.01, "width": 6}]
    for i, tn in enumerate(TUNNELS):
        lay.append({"type": "marker", "at": tn, "t0": 0.0})
    for i, tn in enumerate(["t_allegheny", "t_tuscarora", "t_kittatinny", "t_blue"]):
        lay.append({"type": "label", "at": tn, "text": "×2", "t0": 0.8 + i * 0.5, "dy": -46, "size": 44, "color": YELLOW})
    add(t_cu - 0.4, map_pa([(0, -78.3, 40.08, 0.75), (6, -78.3, 40.08, 0.8)], lay, "SEGUNDO TUBO EN 4 TÚNELES"), tex=GFX)
    add(w("cuentas", 312.5) - 0.8, kb("c006.jpg", "l", "archival"), [Rich([("En", 0.2, "n"), ("Laurel Hill", 0.3, "h"), ("las", 0.6, "n"), ("cuentas", 0.7, "n"),
        ("salieron", 0.9, "n"), ("otras", 1.1, "n")], 0.5, 0.82, 0.7, 60, panel=True)], tex=ARCH)
    add(w("barato", 315.0) - 0.3, cus(G2.mountain, mode="bypass"), tex=GFX)
    add(w("septiembre", 319.6) - 0.3, kb("u_exc1.jpg", "l", "faded"), [Badge("SEPTIEMBRE DE 1962", 0.2)], tex=FILM)
    add(w("maquinas", 327.0) - 0.4, Seq([(3.0, clip("GiveYour1954", 768, 3.0, "faded")), (2.8, kb("u_exc2.jpg", "r", "faded"))]), tex=FILM)
    add(w("desvio", 330.0) - 0.3, cus(G2.mountain, mode="elev"), tex=GFX)
    add(w("turnpike", 338.5) - 0.3, clip("GiveYour1954", 1024, 4.0, "faded"), [Caption("LA TRINCHERA DE LAUREL HILL", "el desvío de 1964", 0.3)], tex=FILM)
    # CTA subscribe
    add(w("aqui", 339.6) - 0.1, kb("u_tun2.jpg", "in", "doc"), [Rich([("una", 1.6, "n"), ("cosa", 1.75, "h")], 0.5, 0.5, 0.6, 90)], tr="black", td=0.4, tex=DARK)
    add(w("canal", 344.6) - 0.6, kb("u_door1.jpg", "in", "dark"), [Rich([("abrir", 0.5, "n"), ("caminos", 0.65, "h"), ("y", 0.9, "n"), ("puertas", 1.0, "h"),
        ("que", 1.3, "n"), ("alguien", 1.4, "n"), ("cerró", 1.55, "n")], 0.5, 0.78, 0.7, 64, panel=True)], tex=DARK)
    add(w("contarte", 348.8) - 0.2, kb("c027.jpg", "punch", "doc"), [Rich([("qué", 0.4, "n"), ("había", 0.55, "n"), ("detrás", 0.75, "h")], 0.5, 0.84, 0.6, 70)], tex=CLEAN)
    add(w("suscribete", 352.0) - 1.4, kb("c021.jpg", "in", "warm"), [Darken(0.45, 0, 0.3), FnOverlay(G2.subscribe)], tex=CLEAN)
    add(w("cerrarse", 355.4) - 1.2, cus(G2.garage_close, bg_fn=lambda t: __import__("engine").kb_frame(
        __import__("engine").load_image("c021.jpg", "warm"), 0.5, 0.5, 1.15 + t * 0.02)), tex=CLEAN)
    t30 = w("30", 357.0)
    add(t30 - 0.2, Solid("black"), [BigText("30 DE OCTUBRE DE 1964", "bebas", 150, WHITE, (0.5, 0.45), 0.0, None, "pop"),
        BigText("la víspera de Halloween", "serif_it", 64, YELLOW, (0.5, 0.62), w("halloween", 360.0) - t30 - 0.3, None, "up")], tex=GFX)
    t_traf = w("trafico", 361.0)
    add(t_traf - 0.2, map_pa([(0, -79.24, 40.09, 2.2), (4.0, -79.24, 40.09, 2.4)], [
        {"type": "route", "path": ["donegal", "t_laurel", "somerset"], "t0": 0.0, "draw": 0.01, "width": 8, "color": (110, 110, 110)},
        {"type": "route", "path": ["donegal", (-79.27, 40.115), (-79.22, 40.125), (-79.17, 40.09), "somerset"], "t0": 0.3, "draw": 1.6, "width": 9},
        {"type": "label", "at": (-79.21, 40.135), "text": "LA TRINCHERA (1964)", "t0": 1.2, "dy": -30, "size": 42, "color": YELLOW},
        {"type": "label", "at": "t_laurel", "text": "TÚNEL CERRADO", "t0": 1.8, "dy": 50, "size": 40, "color": (190, 190, 190)}]), tex=GFX)
    add(w("oscuras", 364.6) - 0.6, kb("c021.jpg", "in", "warm"), [FnOverlay(G2.lights_off, start=0.3, span=1.6)], tex=FILM)
    add(w("24", 366.0) - 0.3, kb("c006.jpg", "in", "archival"), [Darken(0.5, 0, 0.3), Counter(0, 24, "{:,.0f}", "AÑOS DE SERVICIO", 0.1, 0.8, (0.5, 0.45), 260)], tex=ARCH)
    add(w("derrumbado", 369.0) - 0.6, kb("c004.jpg", "l", "archival"), [Rich([("No", 0.3, "n"), ("se", 0.35, "n"), ("derrumbó.", 0.45, "h"), ("No", 1.8, "n"),
        ("falló.", 1.95, "h")], 0.5, 0.82, 0.7, 70)], tex=ARCH)
    add(w("simplemente", 371.4) - 0.2, kb("u_aband1.jpg", "in", "dark"), [Rich([("le", 1.4, "n"), ("salía", 1.5, "n"), ("más", 1.65, "n"), ("a cuenta", 1.8, "h"),
        ("rodearlo", 2.2, "n")], 0.5, 0.82, 0.7, 60, panel=True)], tex=CLEAN)
    add(w("1968", 375.0) - 0.4, kb("c027.jpg", "in", "doc"), [Badge("1968", 0.2), Caption("SIDELING HILL", "abandonado con 13 millas de autopista", 1.0)], tex=CLEAN)
    add(w("race", 383.6) - 0.6, kb("c032.jpg", "up", "doc"), [Caption("RAYS HILL", None, 0.3)], tex=CLEAN)
    add(w("visto", 384.6) - 0.1, kb("c008.jpg", "in", "faded"), [Darken(0.6, 1.0, 1.5)], tex=ARCH)
    add(w("detalle", 390.4) - 0.6, kb("c006.jpg", g="archival", cam0=(0.55, 0.6, 1.0), cam1=(0.58, 0.64, 1.6), ease="in"), [Darken(0.6, 0, 1.0)], tex=ARCH)
    t_viejo = w("viejo", 392.6)
    add(w("tunel", 392.0) - 0.15, Solid("black"), [Rich([("MÁS", 0.2, "n"), ("VIEJO", 0.35, "h"), ("QUE", 0.6, "n"), ("LA", 0.7, "n"), ("AUTOPISTA", 0.85, "n")], 0.5, 0.5, 0.8, 100)],
        tr="glitch", td=0.3, tex=GFX)

    # ============================== CAPÍTULO 3 · MÁS VIEJO QUE LA AUTOPISTA (393.8 - 636)
    b, o = chapter(3, "Más viejo que la autopista", "u_steam2.jpg", "bw", "1881–1940")
    add(w("encontrar", 394.6) - 0.6, b, o, tr="fade", td=0.4, tex=ARCH)
    add(w("autos", 398.1) - 0.1, clip("passenger_train", 377, 2.2, "archival"), tex=FILM)
    add(w("imperios", 401.6) - 0.8, fr("l_keppler2.jpg", "«EL COLOSO DE LOS FERROCARRILES» · 1879", "archival", zoom=(1.0, 1.1)), tex=ARCH)
    add(w("1880", 404.5) - 0.4, fr("c079.jpg", None, "archival", box=(0.84, 0.6)), [Badge("DÉCADA DE 1880", 0.2)], tex=ARCH)
    add(w("negocio", 406.4) - 0.3, clip("passenger_train", 300, 3.0, "archival"), tex=FILM)
    add(w("vanderbilt", 409.6) - 0.4, fr("c061.jpg", None, "archival", box=(0.5, 0.86), cy=0.5),
        [LowerThird("WILLIAM H. VANDERBILT", "Dueño del New York Central", 0.3)], tex=ARCH)
    add(w("epoca", 414.0) - 0.4, kb("l_vand_team.jpg", "l", "archival"), [Rich([("el", 1.4, "n"), ("hombre", 1.5, "n"), ("más", 1.65, "n"), ("rico", 1.8, "h"),
        ("del", 2.0, "n"), ("mundo", 2.1, "h")], 0.5, 0.84, 0.7, 64, panel=True)], tex=ARCH)
    add(w("otro", 418.0) - 0.3, fr("c062.jpg", None, "archival", box=(0.5, 0.86), cy=0.5),
        [LowerThird("GEORGE B. ROBERTS", "Presidente del Pennsylvania Railroad", w("roberts", 423.0) - w("otro", 418.0) - 0.4)], tex=ARCH)
    t_dom = w("dominaba", 424.0)
    add(t_dom - 0.4, map_ne([(0, -76.8, 41.3, 0.62), (9.5, -76.4, 41.6, 0.58)], [
        {"type": "state", "name": "Pennsylvania", "t0": 0.0, "width": 4, "color": (215, 38, 61), "fill": (60, 20, 26), "alpha": 0.7},
        {"type": "rail", "path": M.PRR, "t0": 0.3, "draw": 2.0, "color": (230, 80, 90), "width": 5},
        {"type": "label", "at": (-78.5, 40.2), "text": "PENNSYLVANIA RAILROAD", "t0": 1.6, "size": 40, "color": (255, 140, 140)},
        {"type": "state", "name": "New York", "t0": w("territorio", 431.0) - t_dom - 0.8, "width": 4, "color": (120, 170, 230), "fill": (20, 34, 60), "alpha": 0.7},
        {"type": "rail", "path": M.NYC_RR, "t0": w("territorio", 431.0) - t_dom - 0.6, "draw": 2.0, "color": (120, 170, 230), "width": 5},
        {"type": "label", "at": (-76.0, 43.5), "text": "NEW YORK CENTRAL", "t0": w("territorio", 431.0) - t_dom + 0.6, "size": 40, "color": (160, 200, 255)}],
        "DOS IMPERIOS"), tex=GFX)
    t_ws = w("shore", 438.7)
    add(w("hasta", 433.0) - 0.3, map_ne([(0, -75.2, 41.9, 0.85), (11, -74.6, 42.0, 0.95)], [
        {"type": "state", "name": "Pennsylvania", "t0": 0.0, "width": 3, "color": (215, 38, 61), "fill": (60, 20, 26), "alpha": 0.6},
        {"type": "state", "name": "New York", "t0": 0.0, "width": 3, "color": (120, 170, 230), "fill": (20, 34, 60), "alpha": 0.6},
        {"type": "rail", "path": M.NYC_RR, "t0": 0.0, "draw": 0.01, "color": (120, 170, 230), "width": 5},
        {"type": "rail", "path": M.WEST_SHORE, "t0": t_ws - w("hasta", 433.0), "draw": 3.0, "color": (230, 80, 90), "width": 5},
        {"type": "label", "at": "newburgh", "text": "WEST SHORE", "t0": t_ws - w("hasta", 433.0) + 0.6, "dx": -150, "size": 46, "color": (255, 140, 140)},
        {"type": "label", "at": "poughkeepsie", "text": "RÍO HUDSON", "t0": t_ws - w("hasta", 433.0) + 2.5, "dx": 160, "size": 34, "color": (160, 200, 255)}]), tex=GFX)
    add(w("quitarle", 443.1) - 0.3, fr("c075.jpg", "GRAND CENTRAL DEPOT · NEW YORK CENTRAL", "archival", box=(0.84, 0.66)), tex=ARCH)
    add(w("respondio", 445.6) - 0.4, Split([fr("c061.jpg", None, "archival", box=(0.7, 0.8)), fr("c062.jpg", None, "archival", box=(0.7, 0.8))],
        labels=["VANDERBILT", "ROBERTS"], vs=True), tex=ARCH)
    add(w("entraria", 449.0) - 0.5, map_pa([(0, -78.3, 40.4, 0.48), (5, -78.3, 40.3, 0.55)], [
        {"type": "rail", "path": M.SOUTH_PENN, "t0": 0.2, "draw": 2.2, "color": YELLOW, "width": 6},
        {"type": "label", "at": (-78.3, 40.75), "text": "VANDERBILT ENTRA EN PENSILVANIA", "t0": 0.8, "size": 48, "color": WHITE}]), tex=GFX)
    add(w("aliados", 451.0) - 0.6, clip("SteelASy1936", 258, 2.6, "archival"), tex=FILM)
    add(w("carnegie", 455.0) - 0.4, fr("c065.jpg", None, "archival", box=(0.5, 0.86), cy=0.5), [LowerThird("ANDREW CARNEGIE", "Magnate del acero · Pittsburgh", 0.2)], tex=ARCH)
    add(w("henry", 457.0) - 0.3, fr("l_frick2.jpg", None, "archival", box=(0.5, 0.86), cy=0.5), [LowerThird("HENRY CLAY FRICK", "El coque para los hornos", 0.2)], tex=ARCH)
    add(w("hornos", 459.0) - 0.4, clip("SteelASy1936", 280, 2.4, "archival"), tex=FILM)
    add(w("hartos", 461.0) - 0.4, Seq([(2.6, clip("SteelASy1936", 168, 2.6, "archival")), (2.4, kb("c084.jpg", "l", "archival"))]), tex=FILM)
    add(w("nacio", 467.0) - 0.4, clip("passenger_train", 296, 3.6, "archival"), [Darken(0.55, 0, 0.3),
        BigText("SOUTH PENNSYLVANIA RAILROAD", "serif", 92, WHITE, (0.5, 0.48), 0.4, None, "up"), FnOverlay(_underline, y=0.57, t0=0.7, wmax=520)], tex=FILM)
    t_rec = w("recta", 469.6)
    add(t_rec - 0.3, map_pa([(0, -78.3, 40.25, 0.55), (8, -78.75, 40.15, 0.75)], [
        {"type": "rail", "path": M.SOUTH_PENN, "t0": 0.2, "draw": 3.0, "color": YELLOW, "width": 6},
        {"type": "label", "at": (-78.3, 40.55), "text": "9 TÚNELES", "t0": w("nueve", 475.6) - t_rec, "size": 56, "color": YELLOW},
        {"type": "pin", "at": "t_laurel", "label": "LAUREL HILL", "t0": w("laurel", 477.6) - t_rec, "box": True}]), tex=GFX)
    add(w("plan", 479.6) - 0.2, kb("u_steam3.jpg", "l", "archival"), [Rich([("El", 0.1, "n"), ("plan", 0.2, "n"), ("era", 0.35, "n"), ("enorme", 0.5, "h")], 0.5, 0.84, 0.6, 70)], tex=ARCH)
    t200 = w("200", 481.7) - 0.6
    add(t200, map_pa([(0, -78.3, 40.25, 0.5), (7, -78.3, 40.25, 0.56)], [
        {"type": "rail", "path": M.SOUTH_PENN, "t0": 0.0, "draw": 0.01, "color": YELLOW, "width": 6},
        {"type": "pin", "at": "marysville", "label": "MARYSVILLE", "t0": w("marysville", 483.2) - t200},
        {"type": "label", "at": "marysville", "text": "río Susquehanna", "t0": w("susquehanna", 485.0) - t200, "dy": 46, "size": 32, "color": (150, 190, 220)},
        {"type": "pin", "at": "west_newton", "label": "WEST NEWTON", "t0": w("newton", 486.2) - t200, "side": "l"}]),
        [Counter(0, 200, "≈ {:,.0f}", "MILLAS DE VÍA", 0.5, 1.0, (0.5, 0.83), 120)], tex=GFX)
    add(w("1881", 487.8) - 0.5, kb("c023.jpg", "up", "archival"), [TimelineBar(1870, 1890, 0.1, (0.2, 1.0), start_year=1870, y=0.84)], tex=ARCH)
    add(w("cuadrillas", 491.6) - 0.6, kb("l_drill.jpg", g="archival", cam0=(0.36, 0.6, 1.35), cam1=(0.36, 0.4, 1.35)), [Rich([("terraplenes", 0.9, "n"), ("·", 1.2, "n"), ("puentes", 1.4, "n"), ("·", 1.7, "n"),
        ("túneles", 1.8, "h")], 0.5, 0.86, 0.8, 56, panel=True)], tex=ARCH)
    add(w("piensa", 498.2) - 0.2, kb("c081.jpg", "l", "archival"), [Badge("1883", 0.2)], tex=ARCH)
    add(w("polvora", 501.4) - 0.6, kb("l_drill.jpg", g="archival", cam0=(0.36, 0.45, 1.45), cam1=(0.36, 0.45, 1.7)),
        [Flash(1.4, 0.25, (255, 230, 180), 0.8)], tex=ARCH, post=lambda im, t, d: G2.shake_frame(im, t, 9 if 1.35 < t < 2.3 else 0))
    add(w("magnates", 506.4) - 0.6, Split([fr("c061.jpg", None, "archival", box=(0.7, 0.8)), fr("c062.jpg", None, "archival", box=(0.7, 0.8))],
        labels=["VANDERBILT", "ROBERTS"], vs=True), [Stamp("GUERRA", 1.4, RED, (0.5, 0.2), -8, 110)], tex=ARCH)
    add(w("final", 510.2) - 0.2, fr("x02.jpg", None, "archival", zoom=(1.0, 1.08)), tex=ARCH)
    add(w("morgan", 513.6) - 0.6, fr("l_morgan2.jpg", None, "archival", box=(0.5, 0.86), cy=0.5), [LowerThird("J. P. MORGAN", "El banquero más poderoso del país", 0.3)], tex=ARCH)
    add(w("ruina", 520.4) - 1.6, fr("x02.jpg", None, "archival", zoom=(1.15, 1.3)), [Rich([("una", 1.2, "n"), ("ruina", 1.35, "h"), ("para", 1.6, "n"), ("todos", 1.75, "n")], 0.5, 0.86, 0.6, 66, panel=True)], tex=ARCH)
    add(w("verano", 523.6) - 0.4, fr("l_corsair2.jpg", "EL CORSAIR", "archival"), [Badge("VERANO DE 1885", 0.2)], tex=ARCH)
    add(w("trato", 529.0) - 0.5, fr("l_corsair1.jpg", None, "archival", zoom=(1.0, 1.1)), tex=ARCH)
    add(w("quedaba", 530.6) - 0.6, Split([fr("c061.jpg", None, "archival", box=(0.7, 0.8)), fr("c062.jpg", None, "archival", box=(0.7, 0.8))],
        labels=["SE QUEDA EL WEST SHORE", "ENTIERRA EL SOUTH PENN"]), tex=ARCH)
    t_par2 = w("parar", 536.0)
    add(w("otono", 535.0) - 0.4, map_pa([(0, -78.3, 40.25, 0.55), (4, -78.3, 40.25, 0.58)], [
        {"type": "rail", "path": M.SOUTH_PENN, "t0": 0.0, "draw": 0.01, "color": YELLOW, "width": 6, "t1": t_par2 - w("otono", 535.0) + 0.6},
        {"type": "rail", "path": M.SOUTH_PENN, "t0": t_par2 - w("otono", 535.0) + 0.6, "draw": 0.01, "color": (110, 110, 110), "width": 6}]),
        [Stamp("ORDEN DE PARAR · 1885", t_par2 - w("otono", 535.0) + 0.1, RED, (0.5, 0.45), -6, 110)], tex=GFX)
    add(w("hombres", 538.0) - 0.4, kb("l_drill.jpg", g="archival", cam0=(0.36, 0.5, 1.35), cam1=(0.36, 0.5, 1.55)), [Darken(0.6, 0.5, 1.5)], tex=ARCH)
    add(w("capataz", 543.0) - 0.4, Seq([(2.4, clip("SteelASy1936", 646, 2.4, "archival")), (2.0, clip("SteelASy1936", 404, 2.0, "archival"))]),
        [Darken(0.4, 3.4, 1.0)], tex=FILM)
    add(w("cientos", 547.6) - 0.6, clip("SteelASy1936", 480, 3.6, "archival"), tex=FILM)
    add(w("perforado", 552.4) - 0.6, cus(G2.mountain, mode="bore"), tex=GFX)
    add(w("herida", 557.2) - 0.6, kb("c023.jpg", "in", "archival"), tex=ARCH)
    add(w("locura", 562.4) - 1.2, kb("l_keppler2.jpg", "in", "archival"), [Darken(0.4, 0, 0.3),
        BigText("«LA LOCURA DE VANDERBILT»", "serif_it", 92, WHITE, (0.5, 0.5), 1.0, None, "up")], tex=ARCH)
    add(w("terraplenes", 565.6) - 0.6, kb("l_coke.jpg", "l", "archival"), [Caption("TERRAPLENES QUE NO LLEVABAN A NINGUNA PARTE", None, 0.3)], tex=ARCH)
    add(w("bocas", 568.6) - 0.3, kb("c087.jpg", "in", "doc"), tex=CLEAN)
    add(w("siglo", 572.6) - 0.6, kb("u_aband1.jpg", "in", "doc"), [TimelineBar(1880, 1940, 0.2, (0.4, 2.4), start_year=1885, y=0.84)], tex=CLEAN)
    add(w("pasaron", 576.4) - 0.4, fr("l_migrant.jpg", "LA GRAN DEPRESIÓN · 1936", "archival", box=(0.5, 0.8)), tex=ARCH)
    t_ing = w("ingenieros", 582.0)
    add(w("busco", 580.6) - 0.4, map_pa([(0, -78.3, 40.2, 0.6), (9, -78.4, 40.15, 0.66)], [
        {"type": "rail", "path": M.SOUTH_PENN, "t0": 0.0, "draw": 0.01, "color": (130, 130, 130), "width": 5},
        {"type": "route", "path": M.TURNPIKE, "t0": t_ing - w("busco", 580.6) + 1.0, "draw": 3.0, "width": 7},
        {"type": "label", "at": (-78.3, 40.55), "text": "LA VIEJA OBRA DEL FERROCARRIL", "t0": 0.6, "size": 42, "color": (200, 200, 200)}]), tex=GFX)
    add(w("regalado", 590.0) - 1.0, Solid("concrete"), [Rich([("Era", 0.1, "n"), ("trabajo", 0.3, "n"), ("regalado", 0.5, "h")], 0.5, 0.5, 0.7, 110)], tex=DARK)
    t_seis = w("seis", 594.6)
    lay = [{"type": "route", "path": M.TURNPIKE, "t0": 0.0, "draw": 0.01, "width": 6}]
    for i, tn in enumerate(TUNNELS):
        lay.append({"type": "marker", "at": tn, "t0": 0.2 + i * 0.12, "color": (200, 200, 200)})
    for i, tn in enumerate(["t_laurel", "t_rays", "t_sideling", "t_tuscarora", "t_kittatinny", "t_blue"]):
        lay.append({"type": "marker", "at": tn, "t0": t_seis - w("siete", 592.0) + 0.3 + i * 0.15, "color": YELLOW})
    add(w("siete", 592.0) - 0.3, map_pa([(0, -78.3, 40.08, 0.75), (6, -78.3, 40.08, 0.8)], lay),
        [BigText("6 DE 7", "bebas", 160, YELLOW, (0.5, 0.18), t_seis - w("siete", 592.0) + 0.2, None, "pop")], tex=GFX)
    add(w("obreros", 597.0) - 0.4, clip("Conqueri1937", 256, 4.0, "archival"), [Caption("UN CONTRATISTA Y UN PEÓN", None, 0.6)], tex=FILM)
    add(w("trabajado", 602.1) - 0.3, fr("c080.jpg", "EL FERROCARRIL DE VANDERBILT", "archival", box=(0.84, 0.66)), tex=ARCH)
    add(w("54", 605.6) - 0.6, kb("c081.jpg", "in", "archival"), [TimelineBar(1880, 1945, 0.0, (0.2, 1.4), start_year=1885, y=0.84, label_fmt="{}"),
        BigText("54 AÑOS DESPUÉS", "bebas", 130, WHITE, (0.5, 0.42), 0.4, None, "pop")], tex=ARCH)
    add(w("simbolo", 609.6) - 0.6, clip("ToNewHor1940", 756, 4.6, "faded"), [Rich([("sobre", 2.6, "n"), ("la", 2.7, "n"), ("obra", 2.8, "n"), ("abandonada", 3.0, "h"),
        ("de una", 3.4, "n"), ("guerra de millonarios", 3.6, "h")], 0.5, 0.8, 0.8, 58, panel=True)], tex=FILM)
    add(w("cerraron", 616.2) - 0.4, kb("c006.jpg", "in", "archival"), [Badge("1885 · 1964", 0.3)], tex=ARCH)
    add(w("dos", 622.0) - 0.2, kb("c023.jpg", "in", "archival"), [Rich([("Dos", 0.1, "h"), ("veces", 0.3, "h"), ("lo", 0.6, "n"), ("perforaron", 0.7, "n")], 0.5, 0.84, 0.6, 66)], tex=ARCH)
    add(w("tren", 623.4) - 0.6, clip("passenger_train", 376, 3.0, "archival"), [Caption("UN TREN QUE NUNCA LLEGÓ", None, 0.3)], tex=FILM)
    add(w("autos", 627.0) - 0.4, clip("GiveYour1954", 1024, 3.6, "faded"), [Caption("AUTOS QUE SE FUERON POR LA TRINCHERA", None, 0.3)], tex=FILM)
    add(w("solo", 632.6) - 0.6, kb("c032.jpg", "in", "doc"), tex=CLEAN)
    add(w("faltaba", 635.2) - 0.4, kb("c006.jpg", g="archival", cam0=(0.55, 0.6, 1.0), cam1=(0.58, 0.63, 1.4)), [Darken(0.35, 2.0, 2.0)], tex=ARCH)

    # ============================== CAPÍTULO 4 · EL TÚNEL QUE NADIE MIRABA (641 - 691)
    b, o = chapter(4, "El túnel que nadie miraba", "u_tun2.jpg", "dark", "1964–2003")
    add(w("durante", 639.0) - 0.3, b, o, tr="black", td=0.5, tex=DARK)
    add(w("guardar", 644.2) - 0.6, kb("u_salt1.jpg", "in", "dark"), [Caption("ALMACÉN DE MATERIALES", None, 0.3)], tex=DARK)
    add(w("tiro", 647.0) - 1.0, kb("u_tun3.jpg", "in", "bw"), [Rich([("¿campo", 0.2, "n"), ("de", 0.35, "n"), ("tiro?", 0.45, "h")], 0.5, 0.8, 0.6, 70), Flash(1.0, 0.12, (255, 240, 200), 0.6)], tex=DARK)
    add(w("oscuridad", 649.0) - 0.3, kb("u_tun2.jpg", "in", "doc"), tex=DARK)
    add(w("arriba", 652.4) - 0.2, kb("u_traf3.jpg", "l", "doc"), [Badge("LA TRINCHERA DE 1964", 0.3)], tex=CLEAN)
    add(w("pasaban", 655.1) - 0.3, clip("GiveYour1954", 1024, 3.4, "faded"), tex=FILM)
    add(w("ninguno", 659.0) - 0.4, cus(G2.mountain, mode="hidden"), tex=GFX)
    add(w("vieja", 665.4) - 0.2, kb("u_aband2.jpg", "in", "doc"), [Caption("LA VIEJA CALZADA", "cortada, sin llevar a ninguna parte", 0.3)], tex=CLEAN)
    add(w("igual", 670.0) - 0.4, kb("l_coke.jpg", "r", "archival"), tex=ARCH)
    t70 = w("70", 675.6)
    add(t70 - 0.6, kb("u_tun3.jpg", "in", "bw"), [Counter(1964, 1970, "{:.0f}", "", 0.0, 0.4, (0.5, 0.45), 260, t1=w("80", 676.8) - t70 + 0.6),
        Counter(1970, 1980, "{:.0f}", "", w("80", 676.8) - t70 + 0.6, 0.4, (0.5, 0.45), 260, t1=w("90", 677.8) - t70 + 0.6),
        Counter(1980, 1990, "{:.0f}", "", w("90", 677.8) - t70 + 0.6, 0.4, (0.5, 0.45), 260)], tex=DARK)
    add(w("decadas", 679.0) - 0.4, kb("u_tun2.jpg", "in", "doc"), [Rich([("el", 1.0, "n"), ("único", 1.1, "n"), ("ruido", 1.3, "h")], 0.5, 0.82, 0.6, 64)], tex=DARK)
    add(w("camion", 682.5) - 0.5, kb("u_truck2.jpg", "in", "dark"), tex=DARK)
    add(w("disparo", 686.6) - 1.0, kb("u_tun2.jpg", "punch", "doc"), [Flash(1.05, 0.12, (255, 240, 200), 0.7)], tex=DARK,
        post=lambda im, t, d: G2.shake_frame(im, t, 8 if 1.0 < t < 1.4 else 0))
    add(w("miraba", 690.0) - 0.8, kb("c006.jpg", g="archival", cam0=(0.55, 0.6, 1.2), cam1=(0.58, 0.63, 2.0), ease="in"),
        [Rich([("hasta", 1.2, "n"), ("que", 1.3, "n"), ("alguien", 1.45, "n"), ("lo", 1.6, "n"), ("miró", 1.7, "h"), ("con", 2.0, "n"), ("otros ojos", 2.1, "h")], 0.5, 0.82, 0.8, 60, panel=True)],
        tex=ARCH)

    # ============================== CAPÍTULO 5 · LOS NUEVOS INQUILINOS (693 - 937.6)
    t_nec = w("necesitas", 693.4)
    b, o = chapter(5, "Los nuevos inquilinos", "u_race3.jpg", "dark", "2003")
    add(t_nec - 0.4, b, o, tr="zoom", td=0.5, tex=DARK)
    add(t_nec + 2.6, fr("c107.jpg", None, "doc", box=(0.62, 0.82)), [LowerThird("CHIP GANASSI", "Dueño de Chip Ganassi Racing", 0.3)], tex=CLEAN)
    t_cor = w("corrio", 699.6)
    add(t_cor - 0.6, map_pa([(0, -79.6, 40.3, 1.0), (3, -79.75, 40.25, 1.3)], [
        {"type": "pin", "at": "pittsburgh", "label": "PITTSBURGH", "t0": 0.2, "side": "r"},
        {"type": "pin", "at": "monessen", "label": "MONESSEN · AQUÍ NACIÓ", "t0": 0.6, "box": True}]), tex=GFX)
    add(t_cor + 2.0, kb("u_race1.jpg", "l", "faded"), [Darken(0.45, 0, 0.3), Counter(0, 5, "{:,.0f}", "VECES EN LAS 500 MILLAS DE INDIANÁPOLIS", 0.0, 0.6, (0.5, 0.4), 220),
        TimelineBar(1980, 1990, 0.6, (0.8, 1.2), start_year=1982, y=0.84)], tex=FILM)
    add(w("octavo", 708.4) - 0.6, kb("u_race2.jpg", "in", "faded"), [BigText("8º", "bebas", 320, YELLOW, (0.5, 0.45), 0.3, None, "pop"),
        Caption("SU MEJOR RESULTADO", None, 0.6)], tex=FILM)
    add(w("1984", 710.6) - 0.6, kb("c123.jpg", "l", "faded"), [Badge("MICHIGAN · 1984", 0.2)], tex=FILM)
    t_gir = w("girando", 714.4)
    add(t_gir - 0.4, kb("u_blur1.jpg", g="doc", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.3, 25), ease="in"),
        [Flash(w("choco", 716.2) - t_gir + 0.4, 0.2, (255, 255, 255), 0.9)], tex=FILM,
        post=lambda im, t, d: G2.shake_frame(im, t, 4 + 10 * (t > 1.8)))
    add(w("pedazos", 718.4) - 0.2, Solid("black"), [Rich([("Se", 0.5, "n"), ("lo", 0.6, "n"), ("llevaron", 0.7, "n"), ("en", 0.9, "n"), ("helicóptero", 1.0, "h"),
        ("con", 1.7, "n"), ("heridas", 1.85, "r"), ("graves", 2.0, "r"), ("en", 2.15, "n"), ("la", 2.25, "n"), ("cabeza", 2.35, "r")], 0.5, 0.5, 0.72, 70)],
        tr="glitch", td=0.25, tex=GFX)
    add(w("nunca", 723.4) - 0.3, fr("c108.jpg", None, "bw"), tex=CLEAN)
    add(w("cuesta", 726.5) - 1.0, kb("u_speed1.jpg", "punch", "doc"), [Rich([("cada", 0.8, "n"), ("milla", 0.95, "h"), ("por", 1.15, "n"), ("hora", 1.25, "n")], 0.5, 0.84, 0.6, 64)], tex=CLEAN)
    add(w("2003", 729.0) - 0.2, kb("u_tun1.jpg", g="doc", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.35)), [Badge("2003", 0.2)], tex=DARK)
    t_pis = w("pista", 734.6)
    add(w("vieron", 731.6) - 0.3, kb("u_tun2.jpg", "in", "doc"), [Rich([("no", 0.6, "n"), ("era", 0.7, "n"), ("un", 0.8, "n"), ("almacén", 0.9, "n"), ("olvidado", 1.1, "n")], 0.5, 0.82, 0.7, 60)], tex=DARK)
    add(t_pis - 0.5, kb("c021.jpg", g="warm", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.4), ease="lin"),
        [BigText("ERA UNA PISTA", "bebas", 170, WHITE, (0.5, 0.5), 0.3, None, "pop")], tr="flash", td=0.3, tex=FILM)
    add(w("entender", 736.0) - 0.4, kb("u_race1.jpg", "r", "doc"), tex=CLEAN)
    add(w("aire", 742.2) - 0.8, clip("Streamli1936", 180, 3.0, "archival"), tex=FILM)
    add(w("fuerza", 745.4) - 0.8, cus(G2.aero, mode="downforce"), tex=GFX)
    add(w("tuneles", 749.0) - 0.6, kb("x03.jpg", "in", "archival"), [Caption("TÚNEL DE VIENTO", "ventiladores gigantes", 0.3)], tex=ARCH)
    add(w("quieto", 752.8) - 1.6, clip("Streamli1936", 272, 3.0, "archival"), [Caption("UN AUTO QUIETO", None, 0.3)], tex=FILM)
    add(w("trampa", 755.8) - 0.6, cus(G2.aero, mode="windtunnel"), tex=GFX)
    add(w("pista", 757.6) - 0.2, cus(G2.aero, mode="track"), tr="whip_l", td=0.3, tex=GFX)
    add(w("ofrecia", 761.6) - 0.4, kb("c006.jpg", "in", "archival"), [Rich([("y", 1.6, "n"), ("con", 1.7, "n"), ("la", 1.8, "n"), ("montaña", 1.9, "n"), ("ya", 2.2, "n"), ("pagada", 2.35, "h")], 0.5, 0.84, 0.7, 60, panel=True)], tex=ARCH)
    add(w("milla", 765.4) - 0.6, cus(G2.tunnel_topview, mode="facts"), tex=GFX)
    t100 = w("100", 777.2)
    add(w("meter", 772.7) - 0.4, kb("u_race3.jpg", "punch", "dark"), [Rich([("un", 0.5, "n"), ("auto", 0.6, "n"), ("de", 0.8, "n"), ("verdad", 0.9, "h"), ("con", 1.2, "n"), ("piloto", 1.4, "h")], 0.5, 0.84, 0.6, 64)], tex=DARK)
    ta = w("acelerarlo", 774.8) - 0.2
    add(ta, kb("u_blur2.jpg", g="doc", cam0=(0.45, 0.5, 1.0), cam1=(0.55, 0.5, 1.15), ease="lin"),
        [Counter(0, 100, "{:,.0f}+", "MILLAS POR HORA", t100 - ta + 0.1, 1.0, (0.5, 0.42), 220),
         BigText("≈ 160 KM/H", "bebas", 90, YELLOW, (0.5, 0.78), w("kilometros", 779.6) - ta, None, "pop")], tex=FILM)
    add(w("condiciones", 782.0) - 0.4, Split([kb("u_forest4.jpg", "in", "cold"), kb("u_fog1.jpg", "in", "doc")], labels=["ENERO", "AGOSTO"]), tex=CLEAN)
    add(w("rival", 786.8) - 0.4, kb("u_lock1.jpg", "punch", "dark"), [Rich([("sin", 0.5, "n"), ("que", 0.6, "n"), ("nadie", 0.7, "h"), ("vea", 0.9, "n"), ("nada", 1.0, "h")], 0.5, 0.84, 0.6, 64)], tex=DARK)
    add(w("ponte", 788.3) - 0.2, kb("u_race3.jpg", "punch", "dark"), tex=DARK)
    add(w("nevando", 791.8) - 0.6, kb("u_forest4.jpg", "in", "cold"), [snow], tex=CLEAN)
    add(w("hoja", 795.6) - 0.6, kb("u_tun1.jpg", "in", "doc"), tex=DARK)
    add(w("paredes", 796.8) - 0.2, cus(G2.speed_tunnel), tex=FILM)
    add(w("ingenieros", 799.6) - 0.5, kb("u_data3.jpg", "l", "doc"), tex=CLEAN)
    add(w("menos", 801.2) - 0.1, cus(G2.tunnel_topview, mode="run"), tex=GFX)
    add(w("pasada", 806.8) - 0.4, kb("u_data2.jpg", "in", "dark"), [FnOverlay(G2.telemetry)], tex=DARK)
    t_rep = w("repavimento", 814.6)
    add(t_rep - 0.8, kb("c021.jpg", "in", "warm"), [Darken(0.7, 0, 0.3),
        Callout(0.5, 0.86, 0.22, 0.78, "PAVIMENTO NUEVO", 0.4), Callout(0.5, 0.18, 0.75, 0.2, "CONTROL DEL CLIMA", w("clima", 816.6) - t_rep + 0.6),
        Callout(0.3, 0.4, 0.12, 0.25, "SEGURIDAD", w("seguridad", 817.6) - t_rep + 0.6), Callout(0.7, 0.45, 0.85, 0.55, "MEDICIÓN", w("medicion", 818.4) - t_rep + 0.6)], tex=FILM)
    add(w("boca", 819.6) - 0.3, kb("u_door1.jpg", "in", "dark"), [CCTV("CAM 01", "PORTAL · TUBO DE METAL")], tex=dict(grain=2, vignette=0.4))
    add(w("2004", 825.6) - 0.4, kb("u_race2.jpg", "l", "doc"), [Badge("2004 · PRIMER INDYCAR EN EL TÚNEL", 0.2)], tex=CLEAN)
    add(w("2006", 828.4) - 0.4, cus(G2.patents), tex=GFX)
    add(w("gente", 837.0) - 0.3, kb("u_salt1.jpg", "in", "doc"), [Stamp("NO ERA PARA GUARDAR SAL", 1.6, RED, (0.5, 0.5), -8, 90)], tex=CLEAN)
    add(w("respuesta", 842.4) - 0.6, Solid("concrete"), question("¿Qué es lo que ruge dentro de Laurel Hill?", {"ruge"}) +
        [Badge("LA RESPUESTA", 0.2)], tr="black", td=0.4, tex=DARK)
    add(w("rugido", 848.0) - 0.4, kb("u_fog3.jpg", "in", "dark", z=1.1), [FnOverlay(G2.waveform_overlay, y=0.55, amp=1.0)], tex=DARK, post=postshake(3))
    add(w("probable", 851.6) - 0.6, kb("u_blur3.jpg", g="doc", cam0=(0.4, 0.5, 1.0), cam1=(0.6, 0.5, 1.15), ease="lin"), tex=FILM)
    add(w("tubo", 856.0) - 0.4, cus(G2.speed_tunnel), tex=FILM)
    add(w("sonido", 858.4) - 0.4, kb("c006.jpg", "in", "archival"), [FnOverlay(G2.sound_rings, cx=0.6, cy=0.62)], tex=ARCH)
    add(w("tuberia", 866.0) - 1.4, kb("u_tun3.jpg", "in", "bw"), [FnOverlay(G2.sound_rings, cx=0.5, cy=0.55)], tex=DARK)
    add(w("vibracion", 869.0) - 0.3, cus(G2.mountain, mode="pulse"), [BigText("EN EL CORAZÓN DE LA MONTAÑA", "bebas", 64, WHITE, (0.5, 0.2), 1.6, None, "up")], tex=GFX)
    add(w("oficial", 875.6) - 1.0, kb("u_lock2.jpg", "in", "bw"), tex=DARK)
    add(w("excursionistas", 877.0) - 0.3, kb("u_door3.jpg", "l", "doc"), [FnOverlay(G2.shutter_flash, times=(0.8, 1.6, 2.1))], tex=CLEAN)
    add(w("foros", 880.4) - 0.6, Solid("concrete"), [Rich([("«un", 0.3, "n"), ("lugar", 0.45, "n"), ("secreto", 0.6, "h"), ("en", 0.9, "n"), ("Pensilvania»", 1.0, "n")], 0.5, 0.5, 0.7, 84)], tex=DARK)
    add(w("2012", 885.4) - 0.6, fr("c109.jpg", None, "doc", box=(0.62, 0.82)), [Badge("≈ 2012 · SE RECONOCE EN PÚBLICO", 0.2)], tex=CLEAN)
    t51 = w("51", 893.6)
    add(w("apodo", 891.0) - 0.4, kb("c006.jpg", g="bw", cam0=(0.58, 0.6, 1.4), cam1=(0.58, 0.6, 1.55)),
        [CCTV("CAM 07", "LAUREL HILL"), Stamp("ÁREA 51 DE GANASSI", t51 - w("apodo", 891.0) - 0.3, RED, (0.5, 0.5), -10, 120)], tex=dict(grain=2, vignette=0.4))
    add(w("sirvio", 895.6) - 0.3, kb("c110.jpg", "l", "doc"), tex=CLEAN)
    add(w("cuatro", 901.6) - 0.6, cus(G2.championships), tex=GFX)
    add(w("2010", 907.6) - 0.3, kb("c110.jpg", "in", "doc"), [Badge("2010", 0.2), Rich([("algo", 1.4, "n"), ("que", 1.5, "n"), ("ningún", 1.65, "n"), ("otro", 1.8, "n"), ("dueño", 1.95, "h"),
        ("ha", 2.2, "n"), ("conseguido", 2.3, "h")], 0.5, 0.84, 0.7, 60, panel=True)], tex=CLEAN)
    t10 = w("temporada", 912.3) - 0.3
    add(t10, cus(G2.triple_2010, imgs=(None, "c118.jpg", "c125.jpg"),
                 times=(w("indianapolis", 914.8) - t10 - 0.3, w("daytona", 917.0) - t10, w("brickyard", 918.2) - t10)), tex=GFX)
    add(w("ironia", 921.6) - 0.6, clip("passenger_train", 376, 4.6, "archival"), [Caption("PARA QUE UNOS TRENES FUERAN MÁS RÁPIDOS", None, 0.4)], tex=FILM)
    add(w("terminó", 926.4) - 0.4, kb("u_blur3.jpg", g="doc", cam0=(0.42, 0.5, 1.0), cam1=(0.58, 0.5, 1.12), ease="lin"),
        [Caption("PARA QUE UNOS AUTOS FUERAN MÁS RÁPIDOS", None, 0.3)], tex=FILM)
    add(w("cambio", 931.0) - 0.3, Split([fr("c079.jpg", None, "archival", box=(0.85, 0.6)), kb("u_race2.jpg", "in", "doc")], labels=["1881", "2003"], vs=True), tex=ARCH)
    add(w("guerra", 935.4) - 0.6, fr("c107.jpg", None, "doc", box=(0.62, 0.82)), [Darken(0.5, 1.0, 1.0)], tex=CLEAN)

    # ============================== CAPÍTULO 6 · HOY (937.6 - 1029)
    b, o = chapter(6, "Cómo está hoy", "u_door1.jpg", "dark", "2026")
    add(w("hoy", 938.0) - 0.3, b, o, tr="black", td=0.5, tex=DARK)
    add(w("comision", 941.6) - 0.6, kb("u_aband1.jpg", "in", "doc"), [Caption("PROPIEDAD DE LA COMISIÓN DE LA AUTOPISTA", "alquilado al equipo de Ganassi", 0.3)], tex=CLEAN)
    add(w("noticias", 946.6) - 0.6, kb("u_door3.jpg", g="bw", cam0=(0.5, 0.5, 1.05), cam1=(0.5, 0.5, 1.4)), [BigText("?", "bebas", 300, YELLOW, (0.5, 0.48), 1.2, None, "pop")], tex=DARK)
    add(w("porton", 952.4) - 0.4, kb("u_lock2.jpg", "in", "bw"), tex=DARK)
    add(w("visitas", 955.4) - 0.6, kb("u_door1.jpg", g="dark", cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.55, 1.2)), [CCTV("CAM 01", "LAUREL HILL · 2026", "2026-10-26 23:14:")], tex=dict(grain=2, vignette=0.4))
    add(w("ganar", 960.6) - 1.4, kb("u_race1.jpg", "l", "doc"), tex=CLEAN)
    add(w("piloto", 964.6) - 0.6, fr("c119.jpg", None, "doc", box=(0.62, 0.82)), [LowerThird("ÁLEX PALOU", "Piloto español · Barcelona", w("palau", 968.0) - w("piloto", 964.6) + 0.2)], tex=CLEAN)
    add(w("2025", 967.2) - 0.4, fr("c120.jpg", None, "doc", box=(0.62, 0.82)), [Badge("2025 · GANA LAS 500 MILLAS DE INDIANÁPOLIS", 0.2)], tex=CLEAN)
    add(w("agosto", 973.6) - 1.2, cus(G2.palou_titles), tex=GFX)
    add(w("paso", 978.6) - 0.6, kb("u_tun1.jpg", "in", "doc"), [Rich([("¿Pasó", 0.3, "n"), ("alguna", 0.45, "n"), ("vez", 0.6, "n"), ("por", 0.75, "n"), ("debajo", 0.85, "n"),
        ("de", 1.0, "n"), ("Laurel Hill?", 1.1, "h")], 0.5, 0.5, 0.7, 72)], tex=DARK)
    add(w("tratandose", 985.0) - 0.6, kb("c006.jpg", g="bw", cam0=(0.58, 0.6, 1.4), cam1=(0.58, 0.6, 1.5)), [CCTV("CAM 07", "LAUREL HILL"),
        Stamp("CLASIFICADO", 1.2, RED, (0.5, 0.5), -8, 140)], tex=dict(grain=2, vignette=0.4))
    add(w("ojos", 992.6) - 1.2, Solid("concrete"), [BigText("DOS MANERAS DE VERLO", "bebas", 120, WHITE, (0.5, 0.5), 0.2, None, "pop")], tex=DARK)
    add(w("principio", 996.6) - 0.6, kb("x11.jpg", "l", "cold"), [Darken(0.6, 0, 0.2), snow, Caption("1 · DESDE EL SENDERO, EN INVIERNO", "cuando el bosque no tapa nada", 0.3)], tex=CLEAN)
    add(w("tapa", 1002.0) - 0.8, kb("u_forest2.jpg", "up", "cold"), [snow], tex=CLEAN)
    add(w("otra", 1003.6) - 0.3, kb("u_truck1.jpg", "l", "doc"), [Caption("2 · DESDE LA PROPIA TURNPIKE", None, 0.3)], tex=CLEAN)
    t_este = w("este", 1008.0)
    add(t_este - 0.6, map_pa([(0, -79.3, 40.1, 1.6), (9, -79.23, 40.1, 2.6)], [
        {"type": "route", "path": ["donegal", (-79.27, 40.115), (-79.22, 40.125), (-79.17, 40.09), "somerset"], "t0": 0.4, "draw": 3.0, "width": 9},
        {"type": "route", "path": [(-79.3, 40.105), "t_laurel"], "t0": w("separa", 1011.0) - t_este + 0.2, "draw": 1.6, "width": 8, "color": (150, 150, 150)},
        {"type": "label", "at": (-79.33, 40.12), "text": "HACIA EL ESTE  →", "t0": 0.4, "size": 40, "color": WHITE},
        {"type": "pin", "at": "t_laurel", "label": "BOCA DEL TÚNEL", "t0": w("boca", 1013.0) - t_este + 0.4, "box": True, "side": "b"},
        {"type": "label", "at": (-79.21, 40.135), "text": "TRINCHERA DE 1964", "t0": w("trinchera", 1016.0) - t_este + 0.2, "dy": -30, "size": 40, "color": YELLOW}]),
        tex=GFX)
    add(w("miles", 1018.6) - 0.4, kb("u_traf3.jpg", "in", "doc"), tex=CLEAN)
    add(w("metros", 1022.6) - 0.6, cus(G2.mountain, mode="hidden"), tex=GFX)
    add(w("devuelve", 1026.4) - 0.4, kb("u_forest2.jpg", "in", "cold"), [snow, TimelineBar(1880, 2030, 0.1, (0.2, 1.6), start_year=2026, y=0.84)], tr="glitch", td=0.3, tex=CLEAN)

    # ============================== CAPÍTULO 7 · CONCLUSIÓN (1029 - 1093.25)
    add(w("vigilan", 1030.6) - 0.9, Solid("concrete"), question("¿Por qué vigilan así un túnel abandonado?", {"vigilan"}), tr="black", td=0.4, tex=DARK)
    add(w("guarda", 1033.8) - 0.6, kb("c006.jpg", g="archival", cam0=(0.55, 0.6, 1.0), cam1=(0.58, 0.63, 1.3)), [Darken(0.6, 0, 0.5),
        Rich([("Es", w("secreto", 1037.0) - w("guarda", 1033.8) + 0.3, "n"), ("un", w("secreto", 1037.0) - w("guarda", 1033.8) + 0.4, "n"),
              ("secreto", w("secreto", 1037.0) - w("guarda", 1033.8) + 0.6, "h")], 0.5, 0.8, 0.6, 90)], tex=ARCH)
    add(w("como", 1038.4) - 0.2, kb("u_blur1.jpg", g="doc", cam0=(0.45, 0.5, 1.0), cam1=(0.55, 0.5, 1.12), ease="lin"), tex=FILM)
    add(w("vale", 1043.4) - 0.4, kb("u_lock1.jpg", "punch", "dark"), tex=DARK)
    add(w("circulo", 1045.4) - 0.6, cus(G2.circle_story), tex=GFX)
    add(w("tren", 1050.6) - 0.6, fr("c023.jpg", None, "archival", box=(0.5, 0.86), cy=0.5), [Caption("1881 · UN TREN QUE JAMÁS PASÓ", None, 0.3)], tex=ARCH)
    add(w("terminaron", 1054.0) - 0.2, kb("c006.jpg", "in", "archival"), [Caption("1940 · AUTOS DURANTE SOLO 24 AÑOS", None, 0.3)], tex=ARCH)
    add(w("cerraron", 1057.0) - 0.2, clip("GiveYour1954", 560, 2.8, "faded"), [Caption("1964 · SE QUEDÓ CHICO", None, 0.3)], tex=FILM)
    add(w("servia", 1060.0) - 0.4, Split([kb("c007.jpg", "in", "archival"), kb("u_lock2.jpg", "in", "bw")], labels=["DEJAR PASAR", "ESCONDER"]), tex=ARCH)
    t_esc2 = w("esconder", 1066.0)
    add(t_esc2 - 0.15, Solid("black"), [BigText("ESCONDER.", "serif_black", 180, WHITE, (0.5, 0.5), 0.0, None, "zoom")], tr="flash", td=0.2, tex=GFX)
    add(w("atajo", 1068.6) - 0.6, kb("c006.jpg", g="archival", cam0=(0.5, 0.5, 1.0), cam1=(0.6, 0.62, 1.4)), [Darken(0.55, 0, 0.3),
        Rich([("De", 0.3, "n"), ("atajo", 0.5, "h"), ("a", 1.0, "n"), ("escondite", 1.2, "h")], 0.5, 0.5, 0.7, 110)], tex=ARCH)
    add(w("protegido", 1073.4) - 1.6, kb("c008.jpg", "in", "faded"), tex=ARCH)
    add(w("cruzaban", 1075.4) - 0.6, kb("u_cam2.jpg", "in", "dark"), tex=DARK)
    add(w("familia", 1077.4) - 0.5, fr("c040.jpg", None, "faded", zoom=(1.0, 1.08)), [Badge("ANTES DEL 30 DE OCTUBRE DE 1964", 0.3)], tex=ARCH)
    add(w("cruzo", 1081.6) - 0.4, kb("c021.jpg", "in", "warm"), tex=FILM)
    add(w("preguntale", 1084.0) - 0.2, kb("c001.jpg", "in", "archival"), [Darken(0.45, 0, 0.3), FnOverlay(G2.comments_cta)], tex=ARCH)
    add(w("archivo", 1091.6) - 2.2, kb("c006.jpg", g="archival", cam0=(0.5, 0.5, 1.0), cam1=(0.55, 0.58, 1.15)),
        [Darken(0.5, 0.0, 0.3), BigText("LAUREL HILL", "serif_black", 150, WHITE, (0.5, 0.48), 0.6, None, "zoom"),
         Darken(0.0, 2.6, 1.2)], tr="fade", td=0.6, tex=ARCH)
    return S
