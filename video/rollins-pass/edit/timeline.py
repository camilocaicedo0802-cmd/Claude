"""The edit: every shot of the Rollins Pass video, synced to the voice-over (times in seconds)."""
import os
import re
import sys

import cv2

import gfx2 as G2
import gfx4 as G4
import gfx5 as G5
import gfx8 as G8
import gfx7 as G7
import gfx12 as G12
import maps as M
from engine import RED, ROOT, WHITE, YELLOW, ease_out, prog
from gfx import (Badge, BigText, Callout, Caption, Counter, Custom, Darken, Flash, FnOverlay, Framed, LowerThird, Rich,
                 Solid, Split, Stamp, Still, Video)
from render import Shot
import words

TOTAL = 1171.49
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








# ------------------------------------------------------------------ Rollins Pass specifics
GRADE = M.rp_ll("full")
GRADE_W, GRADE_E = M.rp_ll("west"), M.rp_ll("east")


def _tunnel_only():
    pts = M.rp_ll("tunnel")
    wp = M.COORDS["rp_wportal"]
    i = min(range(len(pts)), key=lambda k: (pts[k][0] - wp[0]) ** 2 + (pts[k][1] - wp[1]) ** 2)
    return pts[:i + 1]


TUNNEL = _tunnel_only()
FRONT = M.rp_ll("front")
TRANSCON = ["rp_omaha", (-100.77, 41.12), "rp_cheyenne", "rp_laramie", (-107.24, 41.79), (-109.47, 41.53), "rp_ogden"]
CZ = ["rp_chicago", (-91.5, 41.2), "rp_omaha", (-100.0, 40.6), "rp_denver", (-105.7, 39.9), (-106.9, 39.6), "rp_gj",
      (-110.8, 39.6), "rp_slc", (-116.0, 40.8), "rp_reno", (-121.0, 38.9), "rp_sf"]
CAP_LOC = "Library of Congress"
F = lambda i: f"f_{i}.jpg"
GOLD = (240, 200, 90)
RED_ = (230, 70, 60)


def _mcard(t, dur, sub=""):
    from gfx import background
    img = background("dark_grid", t)
    G2.label(img, "DAVID H. MOFFAT", 960, 470, ease_out(prog(t, 0.1, 0.4)), 130, YELLOW)
    if sub:
        G2.label(img, sub, 960, 600, ease_out(prog(t, 0.4, 0.4)), 56, WHITE)
    return img


def build():
    S = []

    def add(t, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        S.append(Shot(t, base, ov, tr, td, tex or {}, post, name))

    def q1(t0, bg="f_259182829.jpg", badge="PREGUNTA 1"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Por qué un ferrocarril pensado para unos pocos años acabó funcionando 24?", ("24?", "años"), size=70),
            tr="glitch", td=0.3, tex=DARK)

    def q2(t0, bg="u_vDQ-e3RtaoE.jpg", badge="PREGUNTA 2"):
        add(t0, kb(bg, "in", "dark"), [Darken(0.5), Badge(badge, 0.2, None)] +
            question("¿Y qué esconde esta montaña que llega cada día a los grifos de Denver?", ("grifos", "esconde"), size=70),
            tr="glitch", td=0.3, tex=DARK)

    MOFFAT = lambda fb: pick_w("wm_moffat1898", fb, "David H. Moffat, hacia 1898 · Rose & Hopkins · " + WM)
    MOFFAT2 = lambda fb: pick_w("wm_moffat_bio", MOFFAT(fb), "David H. Moffat, hacia 1898 · " + WM)
    CORONA = lambda fb, f="l_pc_corona_line.jpg", m="l": kb(f, m, "archival") if has(f) else fb
    HAS_M = has("w_wm_moffat1898.jpg")
    DK = lambda k=0.35: [Darken(k)] if HAS_M else []
    MCARD = lambda sub="": cus(_mcard, sub=sub)

    # ============================== INTRO (0 - 66.6)
    add(0.0, kb(F(259180593), "in", "doc"), [rich("VAS SUBIENDO POR UN CAMINO DE TIERRA EN LAS ROCOSAS DE COLORADO", ("colorado",), 0.3, step=0.09,
                                                  y=0.84, size=56, maxw=0.8)], tex=CLEAN)
    add(4.1, kb(F(259181835), "in", "doc"), [big("TAN ALTO QUE YA NO QUEDAN ÁRBOLES", 0.1, 0.86, 68)], tex=CLEAN)
    add(6.6, kb("u_tmijtl52k2Y.jpg", "punch", "doc"), [big("TABLONES GRISES", 0.2, 0.86, 80)], tex=CLEAN)
    add(9.42, kb("u_EQC6OYebxbE.jpg", "punch", "doc"), [big("CLAVOS DEL TAMAÑO DE UN DEDO", 0.1, 0.86, 72)], tex=CLEAN)
    add(w("durmientes", 11.6) - 0.1, kb("u_GyXD9pVq-sw.jpg", "in", "doc"), [big("DURMIENTES MEDIO ENTERRADOS", 0.1, 0.86, 72)], tex=CLEAN)
    add(13.48, kb(F(259182829), "l", "doc"), [big("PERO AQUÍ ARRIBA NO HAY VÍAS", 0.2, 0.86, 72, YELLOW)], tex=CLEAN)
    add(15.6, kb(F(259181154), "punch", "doc"), [big("UNA BARRERA", w("barrera", 16.6) - 15.6, 0.86, 92, WHITE, "pop")], tex=CLEAN)
    add(17.7, pick_w("wm_needle", kb("u_YugQUJClgkM.jpg", "in", "dark"), None), [Darken(0.25), big("UN TÚNEL CERRADO", 0.2, 0.86, 92, RED_, "pop")], tex=DARK)
    add(20.72, pick_w("wm_snowcuts", CORONA(kb(F(9271450537), "in", "archival")), "Los cortes de nieve de Rollins Pass, años 1910 · " + WM),
        [Badge("HACE UN SIGLO", 0.1, None), Caption("CORONA, 1909", "Library of Congress", 0.3, y=0.88)], tr="flash", td=0.2, tex=ARCH)
    add(21.88, cus(G12.profile, mode="over", t0=0.3), [big("TRENES HASTA CASI 11.700 PIES", 0.4, 0.93, 56, WHITE)], tr="fade", td=0.2, tex=GFX)
    add(26.28, V("3384", "u_nLqha2mP4ig.jpg", 0.0, "doc"), [big("POR ENCIMA DE LAS NUBES", 0.1, 0.86, 76)], tex=CLEAN)
    add(27.82, kb("u_8ugL4UBc8qM.jpg", "in", "archival"), [big("ATRAPADOS EN LA NIEVE", 0.1, 0.12, 70), big("MÁS DE UN MES", w("más de", 29.6) - 27.82, 0.86, 92, YELLOW, "pop")],
        tex=ARCH)
    add(31.14, kb("u_pO8_Js7FzMg.jpg", "in", "cold"), [big("CON LA TRIPULACIÓN DENTRO", 0.1, 0.86, 72)], tex=DARK)
    bg, ov = card([("CONSTRUIDO PARA DURAR", 64, GREY_, 0.36, 0.2), ("3 O 4 AÑOS", 190, WHITE, 0.54, w("tres", 34.9) - 32.84)])
    add(32.84, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(36.36, Solid("dark_grid"), [Counter(0, 24, "{:.0f}", "AÑOS", 0.2, 0.8, (0.5, 0.45), 260, color=YELLOW), big("DURÓ", 0.0, 0.2, 80)], tex=GFX)
    add(38.16, MOFFAT(kb("u_rvVhr2LngP4.jpg", "in", "warm")), [big("SE GASTÓ AQUÍ SU FORTUNA", 0.3, 0.08, 64, YELLOW)], tex=ARCH)
    add(41.28, kb("u_JxDpG9z2V2g.jpg", "in", "dark"), [big("Y MURIÓ SIN VER LO QUE DE VERDAD QUERÍA", 0.1, 0.86, 60)], tex=DARK)
    add(43.68, V("4396", "u_mNRznimQKPo.jpg", 0.0, "cold"), [big("PERO LA MONTAÑA QUE LO VENCIÓ…", 0.1, 0.86, 70)], tex=CLEAN)
    add(45.6, kb("u_3ZpDWziy4Jk.jpg", "in", "doc"), [Darken(0.35), big("ESCONDE ALGO QUE USAN", 0.0, 0.26, 64),
                                                    Counter(0, 1000000, "{:,.0f}", "PERSONAS", w("millón", 47.4) - 45.6, 1.0, (0.5, 0.5), 170, prefix="+ DE ")],
        tex=CLEAN)
    add(48.48, V("3891", "u_vDQ-e3RtaoE.jpg", 0.0, "doc"), [big("CADA MAÑANA, SIN SABERLO", 0.1, 0.86, 76, YELLOW)], tex=CLEAN)
    add(50.96, kb("u_cghEZI_lORc.jpg", "in", "cold"), [big("HAY MONTAÑAS QUE SE CRUZAN UNA VEZ", 0.1, 0.86, 66)], tex=CLEAN)
    add(53.34, kb(F(259182267), "in", "doc"), [big("ESTA LLEVA SIGLO Y MEDIO", 0.1, 0.42, 72), big("COBRANDO PEAJE", 0.9, 0.56, 104, YELLOW, "pop")],
        tex=CLEAN)
    q1(56.08)
    q2(62.02)

    # ============================== CAP 1: DENVER, MOFFAT Y EL PEAJE (66.6 - 207.9)
    bg, ov = chapter(1, "DENVER, MOFFAT Y EL PEAJE", "l_1s11052_L.jpg", g="archival", year="1860–1880")
    add(66.64, bg, ov, tr="black", td=0.2, tex=DARK)
    add(68.76, L("1s11061_L", kb("u_NflJmUuaYVI.jpg", "in", "doc"), "Calle 17, Denver · hacia 1900 · " + CAP_LOC),
        [big("UN PROBLEMA QUE SE VEÍA DESDE CUALQUIER CALLE", 0.2, 0.08, 56)], tex=ARCH)
    add(72.48, kb("u_3ZpDWziy4Jk.jpg", "punch", "doc"), [big("LAS MONTAÑAS", 0.0, 0.86, 110, WHITE, "pop")], tex=CLEAN)
    add(73.82, kb("u_ZsW_Qcfj8eU.jpg", "in", "warm"), [big("A UNA MILLA DE ALTURA", 0.1, 0.4, 84), big("1.609 METROS", 0.6, 0.54, 60, YELLOW)], tex=CLEAN)
    add(76.0, mp("rp_mid", [(0, -105.1, 39.8, 0.75), (3.6, -105.35, 39.85, 0.68)],
                 [dict(type="pin", at="rp_denver", t0=0.2, label="DENVER", side="r", box=True, size=42),
                  dict(type="band", path=[(-105.35, 39.62), (-105.33, 39.85), (-105.30, 40.12)], t0=0.6, color=(230, 230, 230), width=90, alpha=0.18),
                  dict(type="label", at=(-105.55, 40.02), text="LAS ROCOSAS", t0=0.9, size=58, box=True)]), tr="zoom", td=0.3, tex=GFX)
    t0 = 77.82
    add(t0, mp("rp_reg", [(0, -106.0, 39.6, 1.0), (8.7, -106.6, 39.7, 1.05)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=40),
                dict(type="label", at=(-107.6, 40.5), text="CARBÓN", t0=w("carbón", 81.6) - t0, size=56, box=True),
                dict(type="label", at=(-106.6, 39.2), text="MADERA", t0=w("madera", 82.4) - t0, size=56, box=True),
                dict(type="label", at=(-108.3, 39.4), text="GANADO", t0=w("ganado", 83.2) - t0, size=56, box=True),
                dict(type="label", at=(-107.3, 38.4), text="PUEBLOS MINEROS", t0=w("pueblos", 84.3) - t0, size=56, box=True)]),
        [big("AL OTRO LADO DE ESA PARED", 0.2, 0.08, 62)], tr="zoom", td=0.3, tex=GFX)
    t0 = 86.52
    add(t0, mp("rp_reg", [(0, -106.6, 39.9, 0.95), (6.3, -106.8, 39.8, 0.95)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=40),
                dict(type="route", ll=M.rp_ll("overland"), t0=0.4, draw=2.6, color=(200, 200, 205), width=6),
                dict(type="label", at=(-107.5, 41.95), text="POR WYOMING", t0=w("wyoming", 89.6) - t0, size=50, box=True),
                dict(type="route", ll=M.rp_ll("drg_south"), t0=w("rodeo", 91.2) - t0, draw=2.4, color=(200, 200, 205), width=6),
                dict(type="label", at=(-107.0, 37.3), text="UN ENORME RODEO POR EL SUR", t0=w("rodeo", 91.2) - t0 + 0.6, size=50, box=True)]),
        tr="fade", td=0.2, tex=GFX)
    add(92.86, V("21612", "u_DgugiZUfH9k.jpg", 0.0, "warm"), [big("UN MAPA DE FERROCARRILES DE LA ÉPOCA", 0.1, 0.86, 64)], tex=DARK)
    add(95.8, mp("rp_us", [(0, -101.0, 40.0, 1.15), (2.4, -104.0, 40.0, 1.35)],
                 [dict(type="route", path=TRANSCON, t0=0.0, draw=0.2, color=(200, 200, 205), width=6),
                  dict(type="route", ll=M.rp_ll("drg_south"), t0=0.0, draw=0.2, color=(200, 200, 205), width=6),
                  dict(type="pin", at="rp_denver", t0=0.2, label="DENVER", side="r", box=True, size=40)]),
        [big("UN CALLEJÓN SIN SALIDA", 0.3, 0.1, 80, RED_, "pop")], tex=GFX)
    add(98.18, V("18305", "u_8F3jhpfWlPY.jpg", 0.0, "warm"), [big("LA RIQUEZA DEL ESTADO PASABA DE LARGO", 0.1, 0.86, 60)], tex=DARK)
    add(100.68, MOFFAT(MCARD("BANQUERO DE DENVER")), DK(0.2) + [big("DAVID H. MOFFAT" if HAS_M else "", w("david", 102.6) - 100.68, 0.86, 96, YELLOW, "up")], tex=ARCH)
    add(104.16, L("1s11054_L", kb("u_ud0Y1ItHhr0.jpg", "in", "doc"), "Denver · 1897 · " + CAP_LOC),
        [Badge("DENVER · 1860", 0.1, None), big("LLEGÓ CON 20 AÑOS", w("veinte", 107.6) - 104.16, 0.08, 64, YELLOW)], tex=ARCH)
    add(108.28, kb("u_5twimJ0bLFE.jpg", "in", "warm"), [big("LO PRIMERO QUE ABRIÓ: UNA LIBRERÍA", 0.2, 0.86, 64)], tex=CLEAN)
    add(110.4, L("020918p", kb("u_WshrPg8tjQI.jpg", "in", "doc"), "Esquina de Larimer y la calle 15 · HABS · " + CAP_LOC),
        [big("CALLE 15 Y LARIMER", 0.4, 0.08, 72, YELLOW)], tex=ARCH)
    add(113.18, kb("u_oIM7Izl5ERk.jpg", "in", "warm"), [big("NO LE FUE BIEN", 0.1, 0.86, 84)], tex=CLEAN)
    add(114.42, kb("u_rvVhr2LngP4.jpg", "in", "warm"), [big("VOLVIÓ A LO QUE SABÍA HACER DESDE NIÑO", 0.1, 0.86, 60)], tex=CLEAN)
    add(117.1, kb("u_1AucbckEJWk.jpg", "punch", "doc"), [big("LA BANCA", 0.0, 0.86, 110, WHITE, "pop")], tex=CLEAN)
    add(w("1880", 118.6) - 0.1, kb("u_6hOlSAQ-L98.jpg", "in", "warm"), [Badge("1880", 0.1, None), big("PRESIDENTE DEL", 0.3, 0.38, 60, GREY_),
                                                                     big("FIRST NATIONAL BANK OF DENVER", 0.6, 0.52, 80, YELLOW)], tex=CLEAN)
    add(122.78, kb("u_CZFq3AjZObM.jpg", "in", "dark"), [Counter(0, 100, "{:.0f}", "MINAS", 0.3, 1.2, (0.5, 0.45), 200, prefix="+ DE ")], tex=DARK)
    add(125.6, kb("u_CIw2BjPHgq4.jpg", "in", "doc"), [big("MEDIA DOCENA DE FERROCARRILES", 0.2, 0.86, 70)], tex=CLEAN)
    t0 = 128.92
    add(t0, mp("rp_us", [(0, -103.0, 40.6, 1.6), (9.9, -104.6, 40.5, 1.9)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="l", box=True, size=40),
                dict(type="pin", at="rp_cheyenne", t0=0.3, label="CHEYENNE", side="r", box=True, size=40),
                dict(type="rail", ll=M.rp_ll("den_chey"), t0=w("cheyenne", 131.0) - t0, draw=1.4, color=YELLOW, width=6),
                dict(type="label", at=(-104.2, 40.45), text="HACIA 1870", t0=w("1870", 133.0) - t0, dx=170, size=44, box=True),
                dict(type="route", path=TRANSCON, t0=w("transcontinental", 136.4) - t0, draw=2.0, color=(220, 220, 225), width=5),
                dict(type="label", at=(-109.0, 42.2), text="LA TRANSCONTINENTAL", t0=w("transcontinental", 136.4) - t0 + 0.6, size=44, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    add(138.9, pick_w("wm_drg_soldier", L("1s53092_L", kb(F(9274236880), "in", "doc"), "Vista al oeste desde Marshall Pass · 1883 · " + CAP_LOC),
                      "Tren de la Denver and Rio Grande en Soldier Summit · 1915 · " + WM),
        [big("PRESIDENTE DE LA DENVER AND RIO GRANDE", w("denver", 142.9) - 138.9, 0.08, 58, YELLOW)], tex=ARCH)
    t0 = 144.24
    add(t0, mp("rp_reg", [(0, -106.8, 40.1, 0.95)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=40),
                dict(type="pin", at="rp_slc", t0=0.2, label="SALT LAKE", side="r", box=True, size=40),
                dict(type="route", path=["rp_denver", "rp_slc"], smooth=False, t0=w("estudiar", 146.2) - t0, draw=2.0, color=YELLOW, width=6, dash=26),
                dict(type="xmark", at=(-108.4, 40.25), t0=w("dejaron", 149.6) - t0, size=50)]),
        [Counter(0, 200000, "${:,.0f}", "EN ESTUDIAR LA RUTA", 0.2, 1.2, (0.5, 0.16), 120, color=YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(151.16, kb("u_8X4t6I203uo.jpg", "in", "doc"), [big("SI ALGUIEN PODÍA ABRIR UN CAMINO HACIA EL OESTE…", 0.1, 0.42, 58),
                                                     big("…ERA ÉL", w("era", 154.5) - 151.16, 0.58, 110, YELLOW, "pop")], tex=CLEAN)
    add(155.64, V("51689", "u_uhHnR7-QHrA.jpg", 0.0, "cold"), [big("NO ERA EL PRIMERO QUE LO INTENTABA", 0.1, 0.86, 66)], tex=CLEAN)
    bg, ov = card([("1873", 150, YELLOW, 0.34, 0.1), ("JOHN Q. A. ROLLINS", 96, WHITE, 0.54, w("john", 162.4) - 159.32), ("PIONERO", 54, GREY_, 0.68, w("john", 162.4) - 159.32 + 0.3)])
    add(159.32, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(163.6, kb("u_ohLUHSuDMwM.jpg", "in", "warm"), [Badge("AGOSTO DE 1873", 0.1, None), big("UN CAMINO DE CARRETAS", w("camino", 167.0) - 163.6, 0.86, 80)],
        tex=CLEAN)
    add(167.94, mp("rp_mid", [(0, -105.45, 39.88, 0.8), (2.7, -105.6, 39.91, 0.95)],
                   [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=40),
                    dict(type="route", ll=GRADE, t0=0.2, draw=2.2, color=(220, 180, 110), width=5, dash=14),
                    dict(type="pin", at="rp_pass", t0=1.2, label="UN PASO ALTÍSIMO", side="t", box=True, size=40)]), tr="zoom", td=0.3, tex=GFX)
    add(170.66, kb("u_Nu2QIe1P3HQ.jpg", "in", "warm"), [big("LO CONVIRTIÓ EN NEGOCIO", 0.1, 0.86, 76)], tex=CLEAN)
    add(172.72, kb("u_2bIF4cEJT4M.jpg", "punch", "doc"), [big("QUIEN QUISIERA CRUZAR, PAGABA", 0.1, 0.12, 62),
                                                         Stamp("PEAJE", w("peaje", 175.3) - 172.72, YELLOW, (0.5, 0.5), -8, 170)], tex=CLEAN)
    bg, ov = card([("1874", 120, YELLOW, 0.3, 0.1), ("MARGARET CRAWFORD", 96, WHITE, 0.48, w("margaret", 178.0) - 176.16),
                   ("LA PRIMERA EN CRUZARLO EN CARRETA", 56, GREY_, 0.64, w("primera", 180.6) - 176.16)])
    add(176.16, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(182.28, kb("u_LiGTtFoyI2M.jpg", "in", "cold"), [Badge("EN JUNIO", 0.1, None), big("Y AUN ASÍ, UNA VENTISCA", w("aún", 183.6) - 182.28, 0.86, 80, YELLOW)],
        post=postshake(3), tex=DARK)
    add(186.12, kb(F(259183277), "in", "doc"), [big("EL CAMINO DE ROLLINS DURÓ POCOS AÑOS", 0.1, 0.86, 64)], tex=CLEAN)
    add(189.22, kb("u_Ktz6cKpMVJs.jpg", "in", "doc"), [Badge("HACIA 1880", 0.1, None), big("YA CASI NADIE LO USABA", 0.6, 0.86, 72)], tex=CLEAN)
    add(192.74, kb("u_mNRznimQKPo.jpg", "punch", "cold"), [big("DEMASIADO ALTO", 0.0, 0.3, 84, WHITE, "pop"),
                                                          big("DEMASIADO DURO", w("duro", 195.0) - 192.74, 0.46, 84, WHITE, "pop"),
                                                          big("DEMASIADO EXPUESTO", w("expuesto", 196.2) - 192.74, 0.62, 84, YELLOW, "pop")], tex=CLEAN)
    add(197.6, kb(F(259182192), "in", "doc"), [big("PERO EL PASO CONSERVÓ SU NOMBRE", 0.1, 0.3, 58),
                                              BigText("ROLLINS PASS", "serif", 130, YELLOW, (0.5, 0.5), w("rollins", 199.9) - 197.6, None, "up")], tex=CLEAN)
    add(201.3, kb(F(259182638), "in", "doc"), [Badge("20 AÑOS DESPUÉS", 0.1, None), big("MOFFAT IBA A VOLVER", 0.8, 0.86, 76)], tex=CLEAN)
    add(205.68, kb("u_fE-UheAsalU.jpg", "punch", "archival"), [big("ESTA VEZ, CON UN TREN", 0.2, 0.86, 92, YELLOW, "pop")], tex=ARCH)

    # ============================== CAP 2: EL ATAJO POR ENCIMA (207.9 - 343.7)
    bg, ov = chapter(2, "EL ATAJO POR ENCIMA", "l_pc_corona_peaks.jpg", g="archival", year="1902–1904")
    add(207.92, bg, ov, tr="black", td=0.2, tex=DARK)
    add(211.62, pick_w("wm_dnp1907", L("1a01433", kb("u_wBwNmU_wwhY.jpg", "in", "doc"), "«Moffat Road», Boulder Park · 1909 · " + CAP_LOC),
                       "Folleto de la Denver, Northwestern and Pacific · 1907 · " + WM),
        [Badge("1902 · CON 63 AÑOS", 0.0, None), big("DENVER, NORTHWESTERN & PACIFIC", w("denver", 215.0) - 211.62, 0.08, 66, YELLOW)], tex=ARCH)
    add(217.34, kb("u_wBwNmU_wwhY.jpg", "in", "doc"), [big("UNA IDEA CLARA Y AMBICIOSA", 0.1, 0.86, 72)], tex=CLEAN)
    add(219.86, kb("u_mSS0srvsfJk.jpg", "in", "doc"), [big("VÍA ANCHA, COMO LAS GRANDES DEL PAÍS", 0.1, 0.86, 66)], tex=CLEAN)
    t0 = 223.54
    add(t0, mp("rp_reg", [(0, -106.8, 40.1, 0.95)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=40),
                dict(type="route", path=["rp_denver", "rp_slc"], smooth=False, t0=w("recta", 225.6) - t0, draw=2.6, color=YELLOW, width=7),
                dict(type="pin", at="rp_slc", t0=w("salt", 227.0) - t0, label="SALT LAKE CITY", side="r", box=True, size=40)]),
        [big("EN LÍNEA RECTA · SIN RODEOS", w("sin", 230.2) - t0, 0.1, 70, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(231.68, kb("u_DgugiZUfH9k.jpg", "in", "warm"), [big("MOFFAT SABÍA CUÁL ERA LA FORMA CORRECTA", 0.1, 0.86, 60)], tex=CLEAN)
    add(234.6, cus(G12.profile, mode="tunnel", tunnel_t=0.3), [big("UN TÚNEL LARGO, CERCA DE JAMES PEAK", w("james", 238.5) - 234.6, 0.93, 54, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(242.1, kb("u_ljhHqO9iCRU.jpg", "punch", "doc"), [Darken(0.45), big("EL PROBLEMA: EL PRECIO", 0.0, 0.86, 92, RED_, "pop")], tex=CLEAN)
    add(243.84, kb("u_hVOdstdHLaY.jpg", "in", "dark"), [big("NO COBRA UN SOLO FLETE", 0.1, 0.3, 72), big("HASTA QUE CAE LA ÚLTIMA PARED", w("hasta", 245.8) - 243.84, 0.86, 64, YELLOW)],
        tex=DARK)
    add(247.86, V("28894", "u_lFUwpyV8Igg.jpg", 0.0, "dark"), [big("AÑOS DE GASTOS", 0.4, 0.86, 92)], tex=DARK)
    add(250.56, kb("u_6AQY7pOllS0.jpg", "in", "dark"), [Darken(0.45), big("NINGÚN BANCO DE NUEVA YORK", 0.1, 0.36, 70),
                                                       big("QUERÍA PRESTARLE ESE DINERO", 1.4, 0.5, 70, RED_),
                                                       big("A UN HOMBRE DE DENVER CON UNA IDEA", w("hombre", 253.6) - 250.56, 0.86, 56)], tex=DARK)
    add(256.38, kb("u_eLqWJqJzJDg.jpg", "in", "warm"), [big("UNA DECISIÓN QUE TODAVÍA HOY SE DISCUTE", 0.2, 0.86, 62, YELLOW)], tex=CLEAN)
    add(259.72, cus(G12.profile, mode="over", t0=0.2), [big("MIENTRAS JUNTABA DINERO: EL TREN POR ENCIMA", 0.2, 0.93, 52, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(264.24, mp("rp_loc", [(0, -105.69, 39.912, 0.8), (3.9, -105.69, 39.915, 0.86)],
                   [dict(type="rail", ll=GRADE, t0=0.0, draw=3.4, color=YELLOW, width=6),
                    dict(type="pin", at="rp_corona", t0=1.0, label="ROLLINS PASS", side="t", box=True, size=40)]),
        [Stamp("PROVISIONAL", w("serían", 266.6) - 264.24, YELLOW, (0.5, 0.55), -8, 120)], tr="zoom", td=0.3, tex=GFX)
    add(268.16, kb(F(9271450537), "in", "archival"), [big("COBRAR FLETES…", 0.1, 0.38, 72), big("…Y PAGAR LA OBRA DE VERDAD", w("pagar", 270.4) - 268.16, 0.54, 72, YELLOW)],
        tex=ARCH)
    add(272.8, pick_w("wm_rifle1903", kb("u_tazmNqUEdes.jpg", "in", "archival"), "Obras en Riflesight Notch · 1903 · " + WM),
        [Badge("ENERO DE 1903", 0.2, None), big("EMPIEZAN LAS CUADRILLAS", 0.6, 0.08, 64)], tex=ARCH)
    add(276.28, kb(F(259181107), "in", "doc"), [big("LO QUE CONSTRUYERON PARECÍA IMPOSIBLE", 0.1, 0.86, 62, YELLOW)], tex=CLEAN)
    add(278.92, mp("rp_loc", [(0, -105.66, 39.912, 0.78), (3.4, -105.70, 39.912, 0.82)],
                   [dict(type="rail", ll=GRADE[::-1], t0=0.0, draw=3.2, color=YELLOW, width=6)]),
        [Counter(0, 23, "{:.0f}", "MILLAS DE SUBIDA", 0.2, 1.4, (0.5, 0.15), 120, color=YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(282.34, kb("u_cS6mz9BmOhM.jpg", "in", "doc"), [big("TÚNELES CORTOS", 0.0, 0.86, 92, WHITE, "pop")], tex=CLEAN)
    add(w("caballetes", 284.0) - 0.1, pick_w("wm_rifle_trestle", kb("u_-XLoAB32uOI.jpg", "in", "doc"), "Restos del caballete de Riflesight Notch · " + WM),
        [big("CABALLETES DE MADERA SOBRE LOS BARRANCOS", 0.0, 0.08, 58, YELLOW)], tex=CLEAN)
    add(286.24, pick_w("wm_rifle1905", kb(F(259181132), "in", "doc"), "Riflesight Notch hacia 1905 · " + WM),
        [BigText("RIFLESIGHT NOTCH", "serif", 96, YELLOW, (0.5, 0.12), 0.3, None, "up")], tex=ARCH)
    add(288.8, cus(G12.loop, t0=0.2, cross_t=w("encima", 291.6) - 288.8), [big("COMO UNA RAMPA DE ESTACIONAMIENTO", w("como", 294.6) - 288.8, 0.93, 56)],
        tr="fade", td=0.2, tex=GFX)
    add(296.78, cus(G12.grade, t0=w("2", 302.6) - 296.78, t2=0.3, helpers_t=99), tr="fade", td=0.2, tex=GFX)
    add(303.3, kb("u_t_-X3OIQVkA.jpg", "in", "doc"), [big("COMO EMPUJAR EL CARRITO DEL SUPER LLENO", 0.1, 0.12, 60),
                                                    big("POR UNA CUESTA INTERMINABLE", 1.6, 0.86, 70, YELLOW)], tex=CLEAN)
    add(307.58, kb("u_LRblyGXwxMY.jpg", "in", "doc"), [big("CADA VAGÓN DE MÁS SE NOTA", 0.1, 0.86, 76)], tex=CLEAN)
    add(309.76, cus(G12.grade, t0=-9, t2=-9, helpers_t=w("dos", 316.3) - 309.76), [big("SOLO UNOS POCOS VAGONES A LA VEZ", 0.2, 0.08, 56, WHITE)],
        tr="fade", td=0.2, tex=GFX)
    add(318.42, CORONA(kb(F(259182829), "in", "doc")), [Badge("1904 · LA CUMBRE", 0.1, None),
                                                       Counter(0, 11700, "{:,.0f}", "PIES · 3.560 METROS", w("11", 322.1) - 318.42, 1.2, (0.5, 0.16), 120,
                                                               color=YELLOW, prefix="CASI ")], tex=ARCH)
    add(326.88, pick_w("wm_dsl_shed", CORONA(kb(F(258903093), "in", "archival"), "l_pc_corona_lake.jpg", "r"),
                       "Tren de la Denver and Salt Lake saliendo de un cobertizo en la cumbre · Richard Fogg · " + WM),
        [big("COMEDOR DE LADRILLO", 0.4, 0.08, 64), big("ALOJAMIENTO", w("alojamiento", 330.6) - 326.88, 0.18, 56, WHITE),
         big("Y HASTA UNA ESTACIÓN METEOROLÓGICA", w("meteorológica", 332.2) - 326.88, 0.86, 56, YELLOW)], tex=ARCH)
    add(333.56, CORONA(kb(F(259182829), "in", "doc"), "l_pc_corona_peaks.jpg", "in"), [Darken(0.25), BigText("CORONA", "serif", 150, YELLOW, (0.5, 0.45), 0.2, None, "up"),
                                               big("LA CORONA DE LAS ROCOSAS", w("como", 335.3) - 333.56, 0.6, 60, WHITE)], tex=CLEAN)
    add(337.02, kb("u_fr42hVGA5ok.jpg", "in", "warm"), [big("EN VERANO, UN ESPECTÁCULO", 0.2, 0.86, 76)], tex=CLEAN)
    add(340.2, V("21585", "u_LGGOV_8UtCc.jpg", 0.0, "cold"), [big("PERO EL VERANO DURA MUY POCO", 0.3, 0.86, 76, YELLOW)], tex=DARK)

    # ============================== CAP 3: LA COLINA EN INVIERNO (343.7 - 473.6)
    bg, ov = chapter(3, "LA COLINA EN INVIERNO", "u_GXffe1Hdezk.jpg", g="cold", year="1904–1922")
    add(343.74, bg, ov, tr="black", td=0.2, tex=DARK)
    add(346.4, V("3352", "u_CxUpw0O2-ig.jpg", 0.0, "cold"), [big("DE OCTUBRE…", 0.0, 0.4, 92), big("…A BIEN ENTRADO JUNIO", w("junio", 347.4) - 346.4, 0.56, 92, YELLOW)],
        tex=DARK)
    add(348.22, V("2197", "u_SH4GNXNj1RA.jpg", 0.0, "cold"), [big("EN UNA SOLA NOCHE…", 0.2, 0.38, 80),
                                                              big("…MÁS NIEVE DE LA QUE SE QUITA EN UNA SEMANA", w("de la", 351.8) - 348.22, 0.54, 56, YELLOW)],
        tex=DARK)
    add(354.16, pick_w("wm_snowcuts_nypl", kb("u_U79jSiu5V6k.jpg", "in", "cold"), "Cortes de nieve en Rollins Pass · Detroit Publishing Co. (NYPL) · " + WM),
        [big("EL VIENTO LA EMPUJA HACIA LA VÍA", 0.2, 0.08, 62), big("ZANJAS Y CORTES DE LA ROCA", w("zanjas", 357.8) - 354.16, 0.86, 70, YELLOW)], tex=ARCH)
    add(359.44, cus(G12.shed, mode="cover", t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(365.06, fr(F(51375390925), "Una estación bajo los cobertizos: Norden, Sierra Nevada, hacia 1930 · Donner Summit Historical Society"),
        [big("ARRIBA, EN CORONA, LA ESTACIÓN QUEDÓ METIDA DEBAJO DEL TECHO", 0.5, 0.08, 52)], tex=ARCH)
    add(370.58, cus(G12.shed, mode="leak", t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(373.1, cus(G12.shed, mode="crush", t0=-1.2), post=postshake(4), tex=GFX)
    add(376.6, cus(G12.shed, mode="fire", t0=0.0), tr="flash", td=0.2, tex=GFX)
    add(379.6, V("3459", "u_sStoal3vris.jpg", 0.0, "warm"), [big("COBERTIZOS Y VÍAS INCLUIDOS", 0.1, 0.86, 72, (255, 170, 80))], tex=DARK)
    add(383.5, pick_w("wm_snowplow1910", L("53298", kb("u_Jc-7YJB3Xho.jpg", "in", "cold"), "Quitanieves en el Colorado Midland, Hagerman Pass · 1899 · " + CAP_LOC),
                      "Quitanieves rotativa en la línea de Moffat, años 1910 · " + WM),
        [big("QUITANIEVES ROTATIVAS", 0.4, 0.08, 80, YELLOW)], tex=ARCH)
    add(387.04, cus(G12.rotary, t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(392.16, pick_w("wm_rot_harmon6", kb(F(22188993984), "in", "doc"),
                       "Quitanieves rotativa · Byron Harmon · " + WM),
        [Badge("1918", 0.1, None), Counter(0, 3, "{:.0f}", "QUITANIEVES", w("tres", 395.0) - 392.16, 0.6, (0.5, 0.18), 140, color=YELLOW)], tex=ARCH)
    add(395.68, kb("u_CIw2BjPHgq4.jpg", "in", "doc"), [Counter(0, 45, "{:.0f}", "LOCOMOTORAS", 0.3, 1.0, (0.5, 0.2), 140, prefix="≈ ")], tex=CLEAN)
    add(399.0, kb("u_GXffe1Hdezk.jpg", "punch", "cold"), [Darken(0.3), big("NO ERAN SUFICIENTES", 0.0, 0.86, 92, WHITE, "pop")], tex=DARK)
    add(400.5, kb(F(25710335643), "in", "archival"), [big("TRENES ATRAPADOS DURANTE DÍAS", 0.1, 0.86, 72)], tex=ARCH)
    add(403.18, kb(F(9669151849), "in", "archival"), [big("ALGUNOS INVIERNOS…", 0.1, 0.08, 62),
                                                     big("UNO O DOS MESES", w("uno", 406.0) - 403.18, 0.86, 96, YELLOW, "pop")], tex=ARCH)
    add(408.1, kb("u_8XNIqU-jecM.jpg", "in", "cold"), [big("COMO BARCOS ATRAPADOS EN EL HIELO", 0.1, 0.86, 66)], tex=DARK)
    add(410.1, V("4283", "u_JhQT5jPjt_4.jpg", 0.0, "cold"), [big("ESPERANDO A QUE ALGUIEN LLEGARA A SACARLOS", 0.2, 0.86, 58)], tex=DARK)
    add(413.6, kb("u_pO8_Js7FzMg.jpg", "punch", "cold"), [big("PONTE EN SU LUGAR", 0.1, 0.5, 104, WHITE, "pop")], tex=DARK)
    add(415.62, kb("u_awLk-2VTrYA.jpg", "in", "cold"), [big("DÍAS MIRANDO UN MURO BLANCO", 0.2, 0.86, 72)], tex=DARK)
    add(419.78, cus(G12.trapped, t0=0.0, days=(4, 18), temp_t=w("20", 422.4) - 419.78), [big("A MÁS DE 3.000 METROS", 0.2, 0.93, 56)],
        tr="fade", td=0.2, tex=GFX)
    add(426.72, kb("u_tektbjMy82s.jpg", "in", "warm"), [big("LA ÚNICA CALEFACCIÓN: LA CALDERA", 0.1, 0.86, 70)], tex=DARK)
    add(429.8, cus(G12.trapped, t0=-6.0, days=(18, 31), coal_t=0.0), [big("Y EL CARBÓN SE ACABA", 0.2, 0.93, 66, RED_)], tex=GFX)
    add(431.46, kb("u_xgaMkZmowLc.jpg", "in", "cold"), [big("CUALQUIER RESCATE: POR LA MISMA VÍA ENTERRADA", 0.1, 0.86, 58)], tex=DARK)
    add(435.36, kb("u_N_nunvZZG88.jpg", "in", "warm"), [Badge("MIENTRAS, EN DENVER", 0.1, None), big("CADA DÍA QUE ESE TREN NO COBRA", 0.8, 0.86, 70, YELLOW)],
        tex=CLEAN)
    add(440.22, kb("u_oRepfU2n5tc.jpg", "in", "cold"), [Darken(0.35), big("Y NO TODOS BAJARON", 0.2, 0.5, 100, RED_, "pop")], tex=DARK)
    add(442.08, kb("u_uRGebYpwpn8.jpg", "in", "archival"), [Badge("1910", 0.1, None), big("FALLAN LOS FRENOS EN PLENA PENDIENTE", 0.4, 0.08, 60),
                                                           big("4 MUERTOS", w("cuatro", 447.6) - 442.08, 0.86, 100, RED_, "pop")], tex=ARCH)
    add(449.0, kb("u_6Oovj0oGjRQ.jpg", "in", "cold"), [Badge("DICIEMBRE DE 1917", 0.1, None), big("UN ALUD", w("lúd", 452.6) - 449.0, 0.86, 110, WHITE, "pop")],
        post=postshake(3), tex=CLEAN)
    add(455.36, mp("rp_loc", [(0, -105.66, 39.93, 1.1)], [dict(type="rail", ll=GRADE, t0=0.0, draw=0.1, color=(200, 200, 210), width=4),
                                                           dict(type="pin", at="rp_ydl", t0=0.1, label="YANKEE DOODLE LAKE", side="r", box=True, size=44)]),
        [big("3 TRABAJADORES MUERTOS", w("mató", 456.9) - 455.36, 0.12, 70, RED_)], tr="zoom", td=0.3, tex=GFX)
    add(458.68, kb("u_wbPCr5CZADg.jpg", "in", "cold"), [Badge("FEBRERO DE 1922", 0.1, None), big("OTRO ALUD EN EL BUCLE", w("otro", 461.4) - 458.68, 0.08, 66),
                                                       big("4 MÁS", w("cuatro", 463.4) - 458.68, 0.86, 110, RED_, "pop")], tex=CLEAN)
    add(464.68, kb("u_6tLMrDA1-Fs.jpg", "in", "archival"), [big("LOS FERROVIARIOS LE PUSIERON NOMBRE", 0.1, 0.86, 66)], tex=ARCH)
    bg, ov = card([("LA LLAMABAN SIMPLEMENTE", 56, GREY_, 0.34, 0.1), ("«THE HILL»", 170, YELLOW, 0.52, w("colina", 469.4) - 467.76 - 0.3),
                   ("LA COLINA", 70, WHITE, 0.7, w("colina", 469.4) - 467.76 + 0.2)])
    add(467.76, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(470.48, kb("u_LGGOV_8UtCc.jpg", "in", "cold"), [big("Y LA COLINA SE COMÍA TODO", 0.2, 0.86, 84, YELLOW)], tex=DARK)

    # ============================== CAP 4: LA TRAMPA (473.6 - 590.0)
    bg, ov = chapter(4, "LA TRAMPA", "u_tUkqup_I7Ps.jpg", g="dark", year="1904–1913")
    add(473.58, bg, ov, tr="black", td=0.2, tex=DARK)
    add(475.16, V("3435", "u_sUHD8WFjkB0.jpg", 0.0, "warm"), [big("SE COMÍA EL CARBÓN", 0.0, 0.3, 84, WHITE),
                                                             big("LOS REFUERZOS QUEMABAN PARTE DE LA CARGA", 1.0, 0.86, 58, YELLOW)], tex=DARK)
    add(479.84, kb("u_DvQ3xYWObr8.jpg", "in", "archival"), [big("SE COMÍA LOS SUELDOS", 0.1, 0.4, 84), big("DE LAS CUADRILLAS DE LA NIEVE", 0.6, 0.54, 60, YELLOW)],
        tex=ARCH)
    add(483.16, kb("u_tFvLJMHczCY.jpg", "in", "warm"), [big("SE COMÍA LA MADERA DE LOS COBERTIZOS", 0.1, 0.86, 66)], tex=CLEAN)
    add(485.66, kb("u_dqCzbaunrFY.jpg", "in", "cold"), [big("CADA PRIMAVERA, AL DERRETIRSE LA NIEVE…", 0.1, 0.86, 62)], tex=CLEAN)
    add(488.54, kb("u_m3gMsMXYKC4.jpg", "punch", "doc"), [big("LOS DAÑOS DEL INVIERNO", 0.0, 0.86, 80, YELLOW)], tex=CLEAN)
    add(490.54, kb("u_DDnW-v862T8.jpg", "punch", "cold"), [big("VIGAS PARTIDAS", 0.0, 0.86, 96, WHITE, "pop")], tex=CLEAN)
    add(w("rieles", 491.9) - 0.1, kb("u_szsMvHD45qU.jpg", "punch", "doc"), [big("RIELES TORCIDOS", 0.0, 0.86, 96, WHITE, "pop")], tex=CLEAN)
    add(w("tramos", 493.4) - 0.1, kb(F(259181190), "punch", "doc"), [big("COBERTIZOS APLASTADOS", 0.0, 0.86, 96, WHITE, "pop")], tex=CLEAN)
    add(495.36, V("18305", "u_8F3jhpfWlPY.jpg", 0.0, "warm"), [big("Y SOBRE TODO…", 0.0, 0.3, 70), big("EL DINERO DEL TÚNEL", w("dinero", 497.6) - 495.36, 0.5, 110, YELLOW, "pop")],
        tex=DARK)
    add(499.84, MOFFAT2(MCARD()), DK(0.25) + [big("ATRAPADO", 0.3, 0.86, 110, RED_, "pop")], tex=ARCH)
    add(501.86, kb("u_BgDf7_FFVhE.jpg", "in", "warm"), [rich("UN PRÉSTAMO NUEVO PARA PAGAR LOS INTERESES DEL ANTERIOR", ("intereses", "anterior"), 0.1, step=0.12,
                                                            y=0.5, size=70, maxw=0.8)], tex=CLEAN)
    add(505.12, cus(G12.seasons, t0=0.3, step=0.85, tunnel_t=w("túnel", 511.5) - 505.12), tr="fade", td=0.2, tex=GFX)
    add(515.94, V("18304", "u_Nu2QIe1P3HQ.jpg", 0.0, "warm"), [big("SIGUIÓ PONIENDO SU PROPIO DINERO", 0.1, 0.86, 66)], tex=DARK)
    add(518.46, kb("u_N_nunvZZG88.jpg", "in", "warm"), [big("VENDIÓ ACCIONES", 0.0, 0.4, 80, WHITE, "pop"), big("PIDIÓ PRÉSTAMOS", w("pidió", 519.6) - 518.46, 0.54, 80, YELLOW, "pop")],
        tex=CLEAN)
    add(520.94, mp("rp_us", [(0, -92.0, 40.5, 0.75)], [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="l", box=True, size=40),
                                                         dict(type="route", path=["rp_denver", (-90.0, 41.6), "rp_nyc"], t0=0.2, draw=1.6, color=YELLOW, width=6),
                                                         dict(type="route", path=["rp_nyc", (-90.0, 40.4), "rp_denver"], t0=1.8, draw=1.4, color=(200, 200, 205), width=4, dash=18),
                                                         dict(type="pin", at="rp_nyc", t0=1.2, label="NUEVA YORK", side="l", box=True, size=40)]),
        [big("UNA Y OTRA VEZ", 0.6, 0.12, 74, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(524.68, kb("u_JxDpG9z2V2g.jpg", "in", "dark"), [Badge("NUEVA YORK · MARZO DE 1911", 0.1, None), big("UNA VEZ MÁS, BUSCANDO FINANCIACIÓN", 1.0, 0.86, 62)],
        tex=DARK)
    add(531.76, MOFFAT(MCARD("1839–1911")), DK() + [big("MURIÓ EL 18 DE MARZO DE 1911", 0.2, 0.08, 66, WHITE), big("A LOS 73 AÑOS", w("73", 534.0) - 531.76, 0.86, 80, YELLOW)],
        tex=ARCH)
    add(535.2, kb("u_6hOlSAQ-L98.jpg", "in", "warm"), [big("SU FORTUNA, CASI AGOTADA", 0.0, 0.38, 76), big("EL TÚNEL, TODAVÍA EN LOS PLANOS", w("túnel", 537.4) - 535.2, 0.54, 72, YELLOW)],
        tex=CLEAN)
    add(539.4, kb("u_ljhHqO9iCRU.jpg", "in", "dark"), [Badge("1913", 0.1, None), Stamp("QUIEBRA", w("quebró", 541.2) - 539.4, RED_, (0.5, 0.5), -10, 170)],
        post=postshake(3), tex=DARK)
    add(542.18, pick_w("wm_dsl1922", kb("l_6a18548.jpg", "l", "archival"),
                       "Denver and Salt Lake Railroad, hacia 1922 · L. C. McClure · " + WM),
        [big("UN NOMBRE NUEVO", 0.1, 0.08, 62), big("DENVER AND SALT LAKE RAILROAD", w("denver", 544.7) - 542.18, 0.86, 78, YELLOW)], tex=ARCH)
    add(546.84, kb(F(55551015766), "in", "doc"), [big("UN NOMBRE QUE PROMETÍA ALGO QUE NUNCA IBA A CUMPLIR", 0.1, 0.86, 56)], tex=CLEAN)
    t0 = 549.84
    add(t0, mp("rp_reg", [(0, -106.4, 40.1, 1.05), (5.7, -106.7, 40.2, 1.1)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=40),
                dict(type="rail", ll=M.rp_ll("moffat_craig"), t0=0.2, draw=2.6, color=YELLOW, width=6),
                dict(type="pin", at="rp_craig", t0=w("craig", 553.4) - t0, label="CRAIG", side="t", box=True, size=44)]),
        [big("Y AHÍ SE QUEDÓ", w("ahí", 554.6) - t0, 0.1, 76, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    t0 = 555.58
    add(t0, mp("rp_reg", [(0, -108.6, 40.3, 0.95)],
               [dict(type="rail", ll=M.rp_ll("moffat_craig"), t0=0.0, draw=0.1, color=YELLOW, width=6),
                dict(type="pin", at="rp_craig", t0=0.0, label="CRAIG", side="t", box=True, size=40),
                dict(type="route", path=["rp_craig", (-109.8, 40.6), "rp_slc"], t0=0.3, draw=2.2, color=(200, 200, 205), width=5, dash=22),
                dict(type="label", at=(-109.7, 40.3), text="CIENTOS DE MILLAS DE MONTAÑAS Y DESIERTO", t0=1.0, size=40, box=True),
                dict(type="pin", at="rp_slc", t0=1.6, label="SALT LAKE CITY", side="r", box=True, size=40),
                dict(type="xmark", at="rp_slc", t0=w("nunca", 559.9) - t0, size=46)]), tex=GFX)
    bg, ov = card([("LA LÍNEA DE 3 O 4 AÑOS…", 66, GREY_, 0.36, 0.1), ("…YA LLEVABA CASI UNA DÉCADA", 86, WHITE, 0.52, w("ya", 564.4) - 561.0),
                   ("SUBIENDO LA COLINA", 70, YELLOW, 0.66, w("subiendo", 566.0) - 561.0)])
    add(561.0, bg, ov, tr="fade", td=0.2, tex=GFX)
    add(567.48, kb(F(259181400), "in", "doc"), [Darken(0.35), big("NADIE PAGABA PARA BAJARLA", 0.1, 0.86, 80, RED_)], tex=CLEAN)
    add(570.84, V("3296", "u_mNRznimQKPo.jpg", 0.0, "cold"), [big("ANTES DE VER QUIÉN ACABÓ PAGANDO ESE TÚNEL…", 0.2, 0.86, 58)], tex=CLEAN)
    add(w("si te", 575.6), kb(F(259182829), "in", "dark", z=1.12), [Darken(0.55), FnOverlay(G2.subscribe)], tex=DARK)
    add(582.4, kb("l_1a01464.jpg", "in", "archival"), [big("LA SOLUCIÓN LLEGÓ DE DONDE MOFFAT NUNCA LA HABÍA BUSCADO", 0.2, 0.08, 52),
                                                       big("Y LE COSTÓ A COLORADO MUCHO MÁS", w("y le", 586.2) - 582.4, 0.86, 70, YELLOW)], tex=ARCH)

    # ============================== CAP 5: EL ESTADO PAGA EL TÚNEL (590.0 - 735.7)
    bg, ov = chapter(5, "EL ESTADO PAGA EL TÚNEL", "u_kiYKo_mhbuE.jpg", g="cold", year="1922–1928")
    add(590.06, bg, ov, tr="black", td=0.2, tex=DARK)
    add(592.82, L("1a01464", kb("u_XmB1WOLzlZ8.jpg", "in", "doc"), "Capitolio de Colorado, Denver · hacia 1900 · " + CAP_LOC),
        [big("AL FINAL, LO PUSO EL PÚBLICO", 0.2, 0.08, 72, YELLOW)], tex=ARCH)
    add(594.78, V("41192", "u_N_nunvZZG88.jpg", 0.0, "warm"), [big("AÑOS DE DISCUSIONES", 0.1, 0.3, 72),
                                                               big("BONOS RECHAZADOS · VOTACIONES", w("bonos", 597.0) - 594.78, 0.86, 66, YELLOW)], tex=DARK)
    add(600.0, kb("u_p3QgWIZtNJE.jpg", "in", "warm"), [Badge("1922", 0.1, None), big("EL LEGISLATIVO DE COLORADO APRUEBA LA LEY", w("aprobó", 603.2) - 600.0, 0.86, 62, YELLOW)],
        tex=CLEAN)
    add(605.46, kb("u_kiYKo_mhbuE.jpg", "in", "cold"), [rich("LA SALIDA DE DENVER HACIA EL OESTE YA NO PODÍA QUEDAR EN MANOS DE UN SOLO HOMBRE", ("oeste", "solo", "hombre"),
                                                            0.2, step=0.11, y=0.5, size=64, maxw=0.82)], tex=CLEAN)
    add(613.02, kb("u_bt-ZiOql8Hc.jpg", "in", "dark"), [Badge("1923", 0.1, None), big("EMPIEZAN LAS OBRAS", 0.4, 0.38, 80),
                                                       big("DURARÍAN 5 AÑOS", w("durarían", 616.0) - 613.02, 0.54, 80, YELLOW)], tex=DARK)
    add(617.42, cus(G12.pioneer, mode="probe", t0=0.3), tr="fade", td=0.2, tex=GFX)
    add(623.22, kb("u_WYxszmANp9g.jpg", "in", "dark"), [big("UNOS 8 PIES DE ANCHO", 0.0, 0.3, 80, YELLOW), big("PARA CONOCER LA ROCA ANTES DE ARRIESGARSE", 1.9, 0.86, 58)],
        tex=DARK)
    add(628.02, kb("u_Yns2AVqJgp4.jpg", "punch", "doc"), [big("HICIERON BIEN", 0.0, 0.86, 96, WHITE, "pop")], tex=CLEAN)
    add(629.16, kb("u_4admqbSrJIQ.jpg", "in", "archival"), [Badge("LADO OESTE", 0.1, None), big("ROCA BLANDA Y TRAICIONERA", w("blanda", 631.0) - 629.16, 0.86, 80, YELLOW)],
        tex=ARCH)
    add(632.92, V("28901", "u_lFUwpyV8Igg.jpg", 0.0, "dark"), [big("SE RETRASÓ", 0.0, 0.38, 84, WHITE, "pop"), big("SE ENCARECIÓ", w("encareció", 634.4) - 632.92, 0.52, 84, YELLOW, "pop"),
                                                              big("UNA Y OTRA VEZ", w("una", 635.2) - 632.92, 0.66, 66, WHITE)], tex=DARK)
    add(636.44, cus(G12.pioneer, mode="rate", t0=w("21", 639.3) - 636.44), [Badge("48 MESES", 0.2, None)], tr="fade", td=0.2, tex=GFX)
    add(643.36, kb("u_bQ0FtTrcwwI.jpg", "punch", "doc"), [big("A GOLPE DE TALADRO Y DINAMITA", 0.0, 0.86, 76, YELLOW)], post=postshake(3), tex=CLEAN)
    add(645.54, pick_w("wm_mt_done", kb("u_WzXvVof2PvI.jpg", "in", "dark"), "Cae la última pared del túnel piloto · 1927 · International News · " + WM),
        [Badge("18 DE FEBRERO DE 1927", 0.1, None), big("CAE LA ÚLTIMA PARED DEL TÚNEL PEQUEÑO", 1.2, 0.08, 58, YELLOW)], tex=ARCH)
    add(651.3, kb("u_35uadY2c0DE.jpg", "in", "doc"), [big("LA CARGA FINAL NO LA DETONÓ UN MINERO", 0.1, 0.86, 62)], tex=CLEAN)
    add(654.04, L("3a53302", kb("u_p3QgWIZtNJE.jpg", "in", "warm"), "Calvin Coolidge · 1923 · " + CAP_LOC), [big("LA DETONÓ EL PRESIDENTE", 0.1, 0.08, 62),
                                                                              LowerThird("CALVIN COOLIDGE", "Presidente de Estados Unidos", w("calvin", 656.6) - 654.04)],
        tex=ARCH)
    t0 = 657.68
    add(t0, mp("rp_us", [(0, -91.0, 39.4, 0.72)],
               [dict(type="pin", at="rp_washington", t0=0.0, label="WASHINGTON", side="r", box=True, size=40),
                dict(type="route", path=["rp_washington", (-90.0, 41.4), "rp_eportal"], t0=0.4, draw=1.6, color=YELLOW, width=6, dash=20),
                dict(type="pin", at="rp_eportal", t0=1.8, label="TÚNEL MOFFAT", side="l", box=True, size=40)]),
        [Counter(0, 1500, "{:,.0f}", "MILLAS", 0.5, 1.4, (0.5, 0.15), 120, color=YELLOW, prefix="+ DE "), big("UN BOTÓN EN WASHINGTON", 0.1, 0.9, 62)],
        tr="zoom", td=0.3, tex=GFX)
    add(661.94, kb("u_6AQY7pOllS0.jpg", "in", "dark"), [big("MOFFAT HABÍA IDO A NUEVA YORK A PEDIR PRÉSTAMOS PARA ESE AGUJERO", 0.1, 0.86, 52)], tex=DARK)
    add(666.18, L("3b39477", kb("l_1a01464.jpg", "in", "archival"), "Coolidge en su despacho · 1926 · " + CAP_LOC),
        [big("AHORA LO ABRÍA LA CASA BLANCA", 0.1, 0.08, 70, YELLOW)], tex=ARCH)
    add(668.36, pick_w("wm_dsl_mt", kb(F(10807100), "in", "doc"), "Tren de la Denver and Salt Lake entrando en el túnel Moffat · " + WM),
        [Badge("FEBRERO DE 1928", 0.1, None), big("EL PRIMER TREN ATRAVIESA EL TÚNEL MOFFAT", 1.2, 0.08, 60, YELLOW)], tex=ARCH)
    add(673.1, mp("rp_loc", [(0, -105.70, 39.895, 0.8)],
                  [dict(type="route", ll=TUNNEL, t0=0.1, draw=2.0, color=WHITE, width=6, dash=20),
                   dict(type="pin", at="rp_eportal", t0=0.0, label="BOCA ESTE", side="r", box=True, size=38),
                   dict(type="pin", at="rp_wportal", t0=1.8, label="BOCA OESTE", side="l", box=True, size=38)]),
        [Counter(0, 6.2, "{:.1f}", "MILLAS · UNOS 10 KM", 0.2, 1.2, (0.5, 0.15), 130, color=YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(676.78, cus(G12.profile, mode="both", tunnel_t=0.0, diff_t=w("2", 683.8) - 676.78), tr="fade", td=0.2, tex=GFX)
    add(686.7, kb(F(4876683853), "in", "doc"), [big("CASI EN PLANO", 0.0, 0.38, 84), big("MENOS DEL 1 %", w("menos", 688.6) - 686.7, 0.54, 110, YELLOW, "pop")], tex=CLEAN)
    add(690.64, kb("u_mzTbd_qPQNA.jpg", "in", "warm"), [big("LO QUE COSTÓ, NADIE LO HABÍA PREVISTO", 0.1, 0.86, 64)], tex=CLEAN)
    add(694.5, cus(G7.bars, items=[("PRESUPUESTO", 6.6, "$6,6 MILLONES", (200, 200, 205)), ("FACTURA FINAL", 24.0, "≈ $24 MILLONES", RED_)],
                   title="EL TÚNEL MOFFAT · CON INTERESES", t0=0.3, step=w("factura", 700.4) - 694.5 - 0.3), tr="fade", td=0.2, tex=GFX)
    add(702.48, kb("u_1vZCYQm6CB8.jpg", "in", "dark"), [big("Y NO SOLO SE PAGÓ EN DINERO", 0.1, 0.86, 72)], tex=DARK)
    add(704.98, cus(G7.icon_grid, kind="person", n=28, per=1, total=28, title="TRABAJADORES MUERTOS", sub="CIFRA OFICIAL", t0=0.2, fill=1.6, cols=14),
        tr="fade", td=0.2, tex=GFX)
    add(709.48, cus(G7.icon_grid, kind="person", n=55, per=1, total=55, title="HASTA 55", sub="PRESERVE ROLLINS PASS · IDENTIFICACIÓN PROVISIONAL", t0=0.2,
                    fill=2.0, cols=14, color=YELLOW), tex=GFX)
    add(717.76, kb(F(4877300842), "in", "doc"), [Badge("BOCA ESTE · HOY", 0.1, None), big("LAS CABAÑAS DE LOS TRABAJADORES", w("cabañas", 721.6) - 717.76, 0.86, 70)],
        tex=CLEAN)
    add(724.38, kb("u_Cr0TRGldLSs.jpg", "in", "doc"), [Badge("2020", 0.1, None), big("ENTRE LOS LUGARES MÁS AMENAZADOS DEL PATRIMONIO DE COLORADO", 0.6, 0.86, 52, YELLOW)],
        tex=CLEAN)
    add(729.16, kb(F(3536251157), "in", "doc"), [big("SE LLAMÓ COMO EL HOMBRE QUE LO SOÑÓ", 0.1, 0.86, 66)], tex=CLEAN)
    add(732.32, MOFFAT(MCARD()), DK() + [big("LLEVABA 17 AÑOS MUERTO", 0.2, 0.86, 84, YELLOW)], tex=ARCH)

    # ============================== CAP 6: EL FIN DE LA COLINA (735.7 - 851.7)
    bg, ov = chapter(6, "EL FIN DE LA COLINA", F(3536263023), g="doc", year="1928–1936")
    add(735.66, bg, ov, tr="black", td=0.2, tex=DARK)
    add(739.76, cus(G12.profile, mode="both", tunnel_t=w("abajo", 744.4) - 739.76), [big("ARRIBA: HORAS DE LUCHA", 0.2, 0.93, 56),
                                                                                  big("ABAJO: UNOS MINUTOS", w("abajo", 744.4) - 739.76, 0.86, 56, YELLOW)],
        tr="fade", td=0.2, tex=GFX)
    add(748.42, kb(F(259182192), "in", "doc"), [Badge("1935", 0.1, None), big("SE APRUEBA EL ABANDONO DE LA VÍA DE LA CUMBRE", 0.5, 0.86, 58)], tex=CLEAN)
    add(753.2, kb(F(259181775), "in", "doc"), [Badge("1936", 0.1, None), big("RIELES ARRANCADOS Y VENDIDOS", w("arrancados", 756.8) - 753.2, 0.86, 76, YELLOW)], tex=CLEAN)
    add(758.9, Solid("dark_grid"), [big("PENSADA PARA 3 O 4 AÑOS", 0.1, 0.24, 66, GREY_),
                                    Counter(0, 24, "{:.0f}", "AÑOS FUNCIONANDO", w("24", 762.4) - 758.9, 0.8, (0.5, 0.52), 230, color=YELLOW)], tex=GFX)
    add(763.84, kb(F(3536263023), "in", "doc"), [big("EL TÚNEL CUMPLIÓ LA PROMESA DE MOFFAT", 0.3, 0.86, 64, YELLOW)], tex=CLEAN)
    t0 = 767.88
    add(t0, mp("rp_reg", [(0, -106.4, 39.9, 1.25), (11.0, -106.7, 39.8, 1.35)],
               [dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=38),
                dict(type="rail", ll=M.rp_ll("moffat_craig"), t0=0.0, draw=1.0, color=(200, 200, 205), width=5),
                dict(type="route", ll=M.rp_ll("dotsero"), t0=w("enlace", 771.2) - t0, draw=1.6, color=YELLOW, width=8),
                dict(type="label", at=(-106.9, 39.95), text="1934 · UNAS 40 MILLAS", t0=w("millas", 772.4) - t0, dx=-60, size=40, box=True),
                dict(type="route", ll=M.rp_ll("dotsero_slc")[:400], t0=w("conectaba", 775.0) - t0, draw=2.0, color=(120, 200, 255), width=6),
                dict(type="label", at=(-107.6, 39.25), text="DENVER AND RIO GRANDE WESTERN", t0=w("denver", 777.5) - t0, size=40, box=True)]),
        tr="zoom", td=0.3, tex=GFX)
    t0 = 779.06
    add(t0, mp("rp_reg", [(0, -106.8, 39.8, 0.95)],
               [dict(type="route", ll=M.rp_ll("drg_south"), t0=0.0, draw=0.1, color=(150, 150, 155), width=5, dash=18),
                dict(type="route", ll=M.rp_ll("moffat_craig")[:500] + M.rp_ll("dotsero") + M.rp_ll("dotsero_slc"), t0=0.2, draw=2.4, color=YELLOW, width=7),
                dict(type="pin", at="rp_denver", t0=0.0, label="DENVER", side="r", box=True, size=38),
                dict(type="pin", at="rp_slc", t0=2.2, label="HACIA EL PACÍFICO", side="r", box=True, size=38)]),
        [Counter(0, 176, "{:.0f}", "MILLAS MENOS", w("176", 783.4) - t0, 1.0, (0.5, 0.14), 130, color=YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(784.66, kb("u_OVE2SA0TVJE.jpg", "in", "warm"), [big("POR PRIMERA VEZ, DENVER TENÍA SU SALIDA DIRECTA AL OESTE", 0.2, 0.86, 56, YELLOW)], tex=CLEAN)
    add(789.08, kb(F(4477067504), "in", "doc"), [Badge("HOY", 0.1, None), big("LOS TRENES DE CARGA DE UNION PACIFIC", w("trenes", 791.0) - 789.08, 0.86, 66)], tex=CLEAN)
    add(793.26, kb(F(5252265974), "in", "doc"), [big("Y EL CALIFORNIA ZEPHYR DE AMTRAK", 0.3, 0.86, 70, YELLOW)], tex=CLEAN)
    t0 = 797.08
    add(t0, mp("rp_us", [(0, -100.0, 39.8, 0.7)],
               [dict(type="route", path=CZ, t0=0.2, draw=4.0, color=YELLOW, width=6, traffic=3, speed=160),
                dict(type="pin", at="rp_chicago", t0=0.2, label="CHICAGO", side="r", box=True, size=38),
                dict(type="pin", at="rp_sf", t0=w("san", 799.8) - t0, label="SAN FRANCISCO", side="r", box=True, size=38),
                dict(type="pin", at="rp_denver", t0=w("denver", 802.6) - t0, label="DENVER", side="t", box=True, size=38),
                dict(type="pin", at="rp_slc", t0=w("salt", 803.0) - t0, label="SALT LAKE CITY", side="t", box=True, size=38)]), tr="zoom", td=0.3, tex=GFX)
    add(804.04, pick_w("wm_cz_mt", kb(F(5198110237), "in", "doc"), "California Zephyr en el túnel Moffat · folleto Burlington–Rio Grande · " + WM),
        [big("LO QUE MOFFAT NUNCA CONSIGUIÓ…", 0.1, 0.08, 62), big("…LO HACE ESE TREN TODOS LOS DÍAS", w("lo hace", 806.2) - 804.04, 0.86, 66, YELLOW)], tex=CLEAN)
    add(810.34, kb("u_xM2LYGASrsE.jpg", "in", "dark"), [big("9.239 PIES", 0.2, 0.4, 110, YELLOW), big("EL PUNTO MÁS ALTO DE TODA LA RED DE AMTRAK", w("pasa", 813.6) - 810.34, 0.56, 56)],
        tex=DARK)
    add(817.12, V("2026", "u_ZqBAKm5gKEU.jpg", 0.0, "dark"), [big("LA MAYORÍA NI SE ENTERA", 0.1, 0.86, 76)], tex=DARK)
    add(821.94, kb("u_SuOFXGBGmkM.jpg", "punch", "dark"), [big("…Y SALE AL OTRO LADO", 0.0, 0.86, 76, YELLOW)], tex=DARK)
    add(823.9, kb(F(20153995572), "in", "doc"), [Badge("EN INVIERNO", 0.1, None), big("UN TREN CARGADO DE ESQUIADORES", w("cargado", 827.2) - 823.9, 0.86, 70)],
        tex=CLEAN)
    add(828.52, V("4016", F(4692640009), 0.0, "cold"), [big("WINTER PARK", 0.2, 0.4, 110, WHITE), big("JUSTO A LA SALIDA DEL TÚNEL", w("justo", 831.8) - 828.52, 0.56, 64, YELLOW)],
        tex=CLEAN)
    add(833.34, kb("u_xhHebwH-AiA.jpg", "in", "cold"), [big("SI ALGUNA VEZ HACES ESE VIAJE…", 0.1, 0.86, 70)], tex=CLEAN)
    add(w("negro", 837.3) - 0.3, Solid("black"), [big("TODO SE VUELVE NEGRO", 0.3, 0.5, 90, WHITE)], tex=DARK)
    add(838.44, mp("rp_loc", [(0, -105.70, 39.905, 0.85)],
                   [dict(type="route", ll=GRADE, t0=0.0, draw=0.1, color=(150, 150, 160), width=4, dash=14),
                    dict(type="route", ll=TUNNEL, t0=0.2, draw=2.6, color=YELLOW, width=7, traffic=1, speed=120),
                    dict(type="label", at="rp_corona", text="CORONA", t0=0.4, dy=-40, size=40, box=True)]),
        [big("POR DEBAJO DE LA COLINA, CASI EN LÍNEA RECTA", 0.2, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(842.34, kb(F(259183072), "in", "cold"), [big("ARRIBA, EL VIENTO SOBRE LOS RESTOS DE CORONA", 0.2, 0.86, 60)], tex=CLEAN)
    add(845.94, kb(F(172753176), "in", "doc"), [big("EL TÚNEL SALVÓ A DENVER", 0.0, 0.36, 76), big("PERO NO ES EL ÚNICO TÚNEL", w("pero", 847.3) - 845.94, 0.52, 90, YELLOW, "pop")],
        tex=CLEAN)

    # ============================== CAP 7: EL AGUA DE DENVER (851.7 - 975.0)
    bg, ov = chapter(7, "EL AGUA DE DENVER", F(3536184337), g="doc", year="1936–2025")
    add(851.7, bg, ov, tr="black", td=0.2, tex=DARK)
    add(853.42, cus(G12.pioneer, mode="probe", t0=-3.0), [big("¿RECUERDAS EL TÚNEL PEQUEÑO?", 0.0, 0.93, 60, YELLOW)], tr="fade", td=0.2, tex=GFX)
    add(855.88, kb(F(3536184337), "in", "doc"), [big("NADIE QUERÍA DEJARLO VACÍO", 0.2, 0.86, 76)], tex=CLEAN)
    add(859.38, kb("u_PqEEJbNrvn8.jpg", "in", "doc"), [big("AL OTRO LADO DE LA DIVISORIA", 0.1, 0.38, 72), big("LA VERTIENTE OESTE", 1.2, 0.52, 80, BLUE)], tex=CLEAN)
    add(863.98, V("1612", "u_dqCzbaunrFY.jpg", 0.0, "cold"), [big("LOS RÍOS QUE LLEVAN LA NIEVE HACIA EL PACÍFICO", 0.1, 0.86, 58)], tex=CLEAN)
    add(869.04, kb("u_9ks9RfEQZHk.jpg", "in", "warm"), [big("Y DENVER, EN EL LADO SECO", 0.1, 0.38, 76), big("NECESITABA AGUA", w("necesitaba", 871.0) - 869.04, 0.52, 96, YELLOW, "pop")],
        tex=CLEAN)
    add(872.46, cus(G12.pioneer, mode="water", t0=0.0), tr="fade", td=0.2, tex=GFX)
    add(876.04, cus(G12.water, t0=0.3), [big("LA CUENCA DEL RÍO FRASER", w("fraser", 883.6) - 876.04, 0.93, 54, BLUE)], tr="fade", td=0.2, tex=GFX)
    add(887.02, kb("u_UaITS7CCnDE.jpg", "in", "doc"), [Counter(0, 90, "{:.0f}", "AÑOS BAJANDO HACIA DENVER", 0.4, 1.0, (0.5, 0.2), 140, color=YELLOW, prefix="CASI ")],
        tex=CLEAN)
    add(w("casas", 891.8) - 0.1, kb("u_gVYc6LgLCm8.jpg", "in", "warm"), [big("CASAS", 0.0, 0.86, 100, WHITE, "pop")], tex=CLEAN)
    add(w("jardines", 893.3) - 0.1, kb("u_owu6poZfEEE.jpg", "in", "warm"), [big("JARDINES", 0.0, 0.86, 100, WHITE, "pop")], tex=CLEAN)
    add(w("fábricas", 894.3) - 0.1, kb("u_m49y6IOk784.jpg", "in", "doc"), [big("FÁBRICAS", 0.0, 0.86, 100, WHITE, "pop")], tex=ARCH)
    add(895.68, V("10334", "u_7RFBmmk7jHc.jpg", 0.0, "warm"), [big("CUANDO ALGUIEN EN DENVER LLENA UN VASO…", 0.3, 0.86, 64)], tex=CLEAN)
    add(900.12, kb("u_igx6ZdyTxLo.jpg", "in", "dark"), [big("…PUDO HABER CRUZADO LA DIVISORIA CONTINENTAL", 0.1, 0.3, 60),
                                                       big("POR DENTRO Y SIN PAGAR PEAJE", w("solo", 906.6) - 900.12, 0.86, 72, YELLOW)], tex=DARK)
    q2(909.9, bg="u_eKHy3YRiLb8.jpg", badge="PREGUNTA 2 · LA RESPUESTA")
    add(917.18, kb("u_vDQ-e3RtaoE.jpg", "punch", "dark"), [BigText("AGUA", "serif", 220, BLUE, (0.5, 0.5), 0.0, None, "pop")], tex=DARK)
    add(918.12, kb("u_eKHy3YRiLb8.jpg", "in", "doc"), [big("POR DEBAJO DE LA COLINA QUE ARRUINÓ A MOFFAT", 0.1, 0.12, 58),
                                                      big("CORRE PARTE DEL AGUA DE LOS GRIFOS DE SU CIUDAD", w("corre", 920.8) - 918.12, 0.86, 58, YELLOW)], tex=CLEAN)
    add(924.32, L("1a01524", kb(F(7417283404), "in", "archival"), "Cañón del Fraser en la «Moffat Road» · 1909 · " + CAP_LOC),
        [big("MOFFAT QUERÍA TRAER A DENVER LA RIQUEZA DEL OESTE", 0.2, 0.08, 56)], tex=ARCH)
    add(928.54, kb(F(5382985945), "in", "doc"), [big("LA MONTAÑA LE DIO LAS DOS COSAS", 0.1, 0.12, 64, WHITE),
                                                big("UN CAMINO HACIA EL OTRO LADO", w("un camino", 932.3) - 928.54, 0.86, 70, YELLOW)], tex=CLEAN)
    add(w("y el agua", 933.9) - 0.1, kb("u_BNgdTPv8sSQ.jpg", "in", "cold"), [big("Y EL AGUA QUE VENÍA DE ALLÍ", 0.0, 0.86, 76, BLUE)], tex=CLEAN)
    add(936.2, kb(F(172752793), "in", "doc"), [big("EL PEAJE TIENE UN ÚLTIMO CAPÍTULO", 0.1, 0.86, 70, YELLOW)], tex=CLEAN)
    add(938.86, kb("u__EvGgF37AD4.jpg", "in", "doc"), [big("LA COMPAÑÍA QUE USABA EL TÚNEL PAGABA", 0.1, 0.1, 56),
                                                      Counter(0, 12000, "${:,.0f}", "AL AÑO", w("12", 943.9) - 938.86, 1.0, (0.5, 0.5), 170, color=YELLOW)], tex=CLEAN)
    add(945.68, kb(F(4877284322), "in", "doc"), [big("UNA CIFRA CASI SIMBÓLICA", 0.0, 0.38, 80), big("PARA EL PASO MÁS VALIOSO DE LAS ROCOSAS", 1.4, 0.54, 60, YELLOW)],
        tex=CLEAN)
    add(950.04, V("241", "u_BgDf7_FFVhE.jpg", 0.0, "warm"), [Badge("ENERO DE 2025", 0.1, None), big("CONTRATO NUEVO: 25 AÑOS", w("nuevo", 953.4) - 950.04, 0.38, 76),
                                                             big("SIN RENTA", w("ya", 956.2) - 950.04, 0.54, 110, YELLOW, "pop")], tex=DARK)
    add(957.5, kb(F(4450795367), "in", "doc"), [big("A CAMBIO, ALGO QUE NO SE MIDE EN DÓLARES", 0.1, 0.1, 60),
                                               big("EL DERECHO A SUS PROPIOS TRENES DE PASAJEROS", w("el derecho", 961.2) - 957.5, 0.86, 60, YELLOW)], tex=CLEAN)
    bg, ov = card([("1873", 110, GREY_, 0.24, 0.1), ("ROLLINS COBRABA POR CRUZAR EN CARRETA", 64, WHITE, 0.36, 0.5),
                   ("2025", 110, YELLOW, 0.58, w("2025", 970.6) - 965.6), ("EL ESTADO DEJÓ DE COBRAR POR CRUZAR EN TREN", 64, YELLOW, 0.7, w("el estado", 972.1) - 965.6)])
    add(965.6, bg, ov, tr="fade", td=0.2, tex=GFX)

    # ============================== CAP 8: LA COLINA HOY (975.0 - 1109.9)
    bg, ov = chapter(8, "LA COLINA HOY", F(259180569), g="doc", year="1956–2026")
    add(975.02, bg, ov, tr="black", td=0.2, tex=DARK)
    add(978.4, kb(F(259184899), "in", "doc"), [Badge("1956", 0.0, None), big("LA REABRIERON… PERO NO PARA LOS TRENES", 0.3, 0.86, 62)], tex=CLEAN)
    add(982.12, kb("u_DxP0Gy7_7Pg.jpg", "in", "doc"), [big("UN CAMINO DE TIERRA PARA AUTOS", 0.2, 0.86, 72)], tex=CLEAN)
    add(986.7, kb(F(259180569), "in", "doc"), [big("VISTAS QUE CORTAN LA RESPIRACIÓN", 0.2, 0.86, 72)], tex=CLEAN)
    add(989.52, kb("u_6B67Jz9xK3k.jpg", "in", "doc"), [big("UNA VÍA DE TREN DEJA UN BUEN CAMINO DE MONTAÑA", 0.1, 0.1, 56),
                                                      big("SIN CURVAS CERRADAS NI REPECHOS", w("nada", 994.1) - 989.52, 0.86, 70, YELLOW)], tex=CLEAN)
    add(997.34, mp("rp_loc", [(0, -105.69, 39.912, 0.78)],
                   [dict(type="route", ll=GRADE, t0=0.1, draw=3.6, color=(235, 200, 140), width=6, traffic=2, speed=160)]),
        [big("EN CARRO POR DONDE SUBÍAN LAS LOCOMOTORAS", 0.3, 0.1, 58)], tr="zoom", td=0.3, tex=GFX)
    add(1002.98, kb("u_2bIF4cEJT4M.jpg", "in", "doc"), [big("HASTA QUE LA MONTAÑA VOLVIÓ A CERRAR LA PUERTA", 0.1, 0.86, 60, RED_)], tex=CLEAN)
    add(1006.16, kb("u_4XPzVsrAbxs.jpg", "punch", "doc"), [Badge("1979", 0.1, None), big("UN DESPRENDIMIENTO DE ROCAS", 0.6, 0.86, 76)], post=postshake(4), tex=CLEAN)
    add(1013.14, pick_w("wm_needle", kb("u_hyNbatg81Po.jpg", "in", "doc"), "Needle's Eye Tunnel · " + WM),
        [BigText("NEEDLE'S EYE", "serif", 110, YELLOW, (0.5, 0.42), 0.0, None, "up"), big("EL OJO DE LA AGUJA", w("ojo", 1014.9) - 1013.14, 0.58, 64)], tex=CLEAN)
    add(1015.98, mp("rp_loc", [(0, -105.665, 39.935, 1.25)],
                    [dict(type="rail", ll=GRADE, t0=0.0, draw=0.1, color=(200, 200, 210), width=4),
                     dict(type="pin", at="rp_needle", t0=0.1, label="NEEDLE'S EYE", side="r", box=True, size=42)]),
        [Badge("SE REABRE EN 1989", w("1989", 1018.6) - 1015.98, None)], tr="zoom", td=0.3, tex=GFX)
    add(1020.58, kb("u_nwqDgNZZ99k.jpg", "in", "doc"), [Badge("1990", 0.1, None), big("OTRO DESPRENDIMIENTO HIERE A UN VISITANTE", 0.6, 0.1, 58),
                                                       big("CERRADO PARA SIEMPRE", w("cerró", 1025.4) - 1020.58, 0.86, 92, RED_, "pop")], tex=CLEAN)
    add(1027.36, kb(F(259181775), "in", "doc"), [big("HOY SE SUBE DESDE LOS DOS LADOS", 0.1, 0.86, 70)], tex=CLEAN)
    add(1031.92, cus(G12.speed_sign, t0=0.1), tex=CLEAN)
    add(1034.44, kb("u_U79jSiu5V6k.jpg", "in", "cold"), [big("EN TEORÍA, ABRE A MEDIADOS DE JUNIO", 0.1, 0.38, 64),
                                                        big("MUCHOS AÑOS, HASTA JULIO", w("muchos", 1037.6) - 1034.44, 0.54, 80, YELLOW)], tex=CLEAN)
    t0 = 1041.14
    add(t0, mp("rp_loc", [(0, -105.672, 39.928, 1.05)],
               [dict(type="route", ll=GRADE_W, t0=0.0, draw=0.6, color=(235, 200, 140), width=6),
                dict(type="route", ll=GRADE_E, t0=0.0, draw=0.6, color=(235, 200, 140), width=6),
                dict(type="xmark", at=(-105.672, 39.938), t0=w("no puedes", 1042.4) - t0, size=46)]),
        [big("NO SE PUEDE LLEGAR AL OTRO LADO", 0.3, 0.1, 64, RED_)], tr="zoom", td=0.3, tex=GFX)
    add(1043.7, kb("u_8F47XWiUPrQ.jpg", "in", "doc"), [big("A PIE O EN BICICLETA", 0.6, 0.86, 84)], tex=CLEAN)
    add(1047.64, kb("u_cuRbcnvgvOA.jpg", "in", "cold"), [big("NO CONVIENE TOMÁRSELO A LA LIGERA", 0.1, 0.12, 62),
                                                        Badge("2021", w("2021", 1050.2) - 1047.64, None),
                                                        Counter(0, 15, "{:.0f}", "AGENCIAS EN LA BÚSQUEDA", w("15", 1055.0) - 1047.64, 0.8, (0.5, 0.62), 150, color=YELLOW)],
        tex=CLEAN)
    add(1056.8, V("3370", "u_1vn19QxbwUE.jpg", 0.0, "doc"), [big("ALLÁ ARRIBA, CASI TODO SIGUE DONDE QUEDÓ", 0.2, 0.86, 64)], tex=CLEAN)
    add(1061.96, kb(F(258903093), "in", "doc"), [big("LOS CABALLETES DE MADERA", 0.0, 0.86, 80)], tex=CLEAN)
    add(1064.74, kb(F(259181190), "in", "doc"), [big("LOS TABLONES DE LOS COBERTIZOS", 0.0, 0.86, 76)], tex=CLEAN)
    add(1066.76, kb("u_oqjMtZHZ66k.jpg", "in", "doc"), [big("LOS DURMIENTES", 0.0, 0.86, 84)], tex=CLEAN)
    add(1068.44, kb(F(259181888), "in", "doc"), [big("LOS CIMIENTOS DE CORONA, BARRIDOS POR EL VIENTO", 0.0, 0.86, 60)], tex=CLEAN)
    add(1072.24, pick_w("wm_ydl_nypl", kb("u_Bi0FKH-J-Ek.jpg", "in", "doc"), "Yankee Doodle Lake y James Peak · Detroit Publishing Co. (NYPL) · " + WM),
        [big("YANKEE DOODLE LAKE", 0.2, 0.08, 80, YELLOW), big("HOY, UNA PARADA PARA HACER FOTOS", w("es hoy", 1077.4) - 1072.24, 0.86, 62)], tex=CLEAN)
    add(1080.08, kb(F(259181154), "in", "doc"), [big("HAY QUIEN PIDE REABRIR EL OJO DE LA AGUJA", 0.2, 0.86, 64, YELLOW)], tex=CLEAN)
    t0 = 1084.22
    add(t0, mp("rp_mid", [(0, -105.58, 39.92, 0.72)],
               [dict(type="route", ll=GRADE, t0=0.0, draw=0.1, color=(235, 200, 140), width=5),
                dict(type="pin", at="rp_winterpark", t0=0.4, label="WINTER PARK", side="l", box=True, size=40, color=(90, 200, 120)),
                dict(type="pin", at="rp_fraser", t0=0.9, label="FRASER", side="l", box=True, size=40, color=(90, 200, 120)),
                dict(type="label", at=(-105.86, 40.06), text="A FAVOR", t0=1.6, size=58, color=(110, 220, 140)),
                dict(type="pin", at=(-105.51, 39.96), t0=w("boulder", 1093.0) - t0, label="BOULDER", side="r", box=True, size=40, color=RED_),
                dict(type="pin", at=(-105.514, 39.80), t0=w("gilpin", 1093.6) - t0, label="GILPIN", side="r", box=True, size=40, color=RED_),
                dict(type="label", at=(-105.33, 39.70), text="EN CONTRA", t0=w("oponen", 1095.0) - t0, size=58, color=RED_)]),
        [big("UNA SEGUNDA RUTA SOBRE LA DIVISORIA", w("segunda", 1088.4) - t0, 0.1, 58, YELLOW)], tr="zoom", td=0.3, tex=GFX)
    add(1096.96, kb(F(259181400), "in", "doc"), [Badge("2013 · SERVICIO FORESTAL", 0.1, None),
                                                Counter(0, 10, "${:.0f} MILLONES", "SOLO EL CAMINO Y LOS CABALLETES", w("10", 1100.8) - 1096.96, 1.0, (0.5, 0.45), 150,
                                                        color=YELLOW, prefix="≈ "), big("SIN CONTAR EL TÚNEL", w("sin", 1105.0) - 1096.96, 0.86, 70, RED_)], tex=CLEAN)
    add(1106.52, kb("u_IdaRwQkKptc.jpg", "in", "doc"), [big("Y MIENTRAS DISCUTEN…", 0.1, 0.38, 72), big("LA BARRERA SIGUE CERRADA", w("la barrera", 1108.0) - 1106.52, 0.54, 86, RED_)],
        tex=CLEAN)

    # ============================== CONCLUSIÓN (1109.9 - 1171.5)
    q1(1109.92, badge="DE VUELTA A LA PREGUNTA 1")
    add(1117.4, V("18305", "u_8F3jhpfWlPY.jpg", 0.0, "warm"), [rich("PORQUE LA COLINA SE COMÍA EL DINERO QUE DEBÍA LIBRARSE DE ELLA", ("dinero",), 0.1, step=0.1,
                                                                  y=0.5, size=66, maxw=0.8)], tex=DARK)
    add(1121.34, cus(G12.seasons, t0=-20, step=0.85, tunnel_t=0.3), [big("CADA INVIERNO SE LLEVABA LO QUE EL TÚNEL NECESITABA", 0.2, 0.93, 52, YELLOW)], tex=GFX)
    add(1124.68, kb("u_6AQY7pOllS0.jpg", "in", "dark"), [big("NINGÚN BANCO QUERÍA ESPERAR TANTOS AÑOS", 0.1, 0.86, 64)], tex=DARK)
    add(1128.22, kb("u_tazmNqUEdes.jpg", "in", "doc"), [big("NO DURÓ POR BUENA", 0.0, 0.38, 84), big("DURÓ PORQUE NADIE TENÍA CON QUÉ SUSTITUIRLA", w("duró", 1130.4) - 1128.22, 0.54, 60, YELLOW)],
        tex=CLEAN)
    add(1133.82, L("1a01464", kb("u_XmB1WOLzlZ8.jpg", "in", "doc"), None), [big("HASTA QUE UN ESTADO ENTERO DECIDIÓ PAGAR", 0.1, 0.86, 62, YELLOW)], tex=ARCH)
    add(1136.46, V("4115", "u_cghEZI_lORc.jpg", 0.0, "cold"), [big("CRUZAR ESTA MONTAÑA SIEMPRE TUVO UN PRECIO", 0.1, 0.86, 66)], tex=CLEAN)
    add(1139.28, kb("u_2bIF4cEJT4M.jpg", "punch", "doc"), [big("LO COBRÓ ROLLINS CON SU CASETA", 0.0, 0.86, 72)], tex=CLEAN)
    add(1141.24, kb("u_8ugL4UBc8qM.jpg", "in", "archival"), [big("LO COBRÓ LA NIEVE", 0.0, 0.3, 80), big("CARBÓN · MESES PERDIDOS · VIDAS", w("carbón", 1142.4) - 1141.24, 0.86, 70, YELLOW)],
        tex=ARCH)
    add(1145.48, L("1a01464", kb("u_kiYKo_mhbuE.jpg", "in", "cold"), None), [big("LO PAGÓ COLORADO", 0.0, 0.38, 80), big("24 MILLONES", w("24", 1147.0) - 1145.48, 0.54, 110, YELLOW, "pop")],
        tex=ARCH)
    add(1148.44, MOFFAT(MCARD()), DK() + [big("MOFFAT PUSO SU FORTUNA… Y NO LLEGÓ A VERLO", 0.2, 0.86, 62, WHITE)], tex=ARCH)
    add(1151.68, kb(F(259182267), "out", "doc"), [Darken(0.4), big("LA MONTAÑA SIEMPRE COBRÓ", 0.1, 0.42, 92, WHITE),
                                                  big("SOLO CAMBIÓ QUIÉN PAGABA", w("solo", 1153.9) - 1151.68, 0.58, 92, YELLOW)], tex=CLEAN)
    add(1156.08, kb("u_U79jSiu5V6k.jpg", "in", "cold"), [Darken(0.4), rich("¿ALGUNA VEZ TE QUEDASTE ATRAPADO POR LA NIEVE O POR UNA CARRETERA CORTADA?", ("nieve", "cortada?"),
                                                                       w("alguna", 1157.9) - 1156.08, step=0.07, y=0.5, size=66, maxw=0.82)], tex=CLEAN)
    add(1162.26, kb("u_XJfLW1Fhhqo.jpg", "in", "cold"), [big("¿DÓNDE FUE?", 0.0, 0.3, 80, WHITE, "pop"), big("¿CUÁNTO TIEMPO?", w("cuánto", 1163.3) - 1162.26, 0.46, 80, WHITE, "pop"),
                                                        big("¿CÓMO SALISTE?", w("cómo", 1164.3) - 1162.26, 0.62, 80, YELLOW, "pop")], tex=CLEAN)
    add(1166.0, kb(F(259180593), "out", "doc"),
        [Darken(0.45), FnOverlay(G4.comments, line1="¿ALGUNA VEZ TE QUEDASTE ATRAPADO", line2="POR LA NIEVE O UNA CARRETERA CORTADA?", cta="CUÉNTALO EN LOS COMENTARIOS"),
         rich("A veces el camino más corto es el que más caro te sale", ("caro",), w("a veces", 1167.7) - 1166.0 - 0.3, step=0.07, y=0.2, size=50, maxw=0.85)],
        tex=DARK)
    return S


def pick_w(name, fallback, cap):
    f = f"w_{name}.jpg"
    if os.path.exists(os.path.join(IMG, f)):
        return fr(f, cap, "archival")
    return fallback


def pick_l(lid, fallback, cap):
    return L(lid, fallback, cap)
