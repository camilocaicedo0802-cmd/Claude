"""¿Y si morir es volver a nacer? — línea de tiempo. Cada plano se ancla a una frase de la locución,
buscada en orden (cursor) dentro de work/words.json."""
import glob
import os
import re
import unicodedata

from engine import FPS
from gfx import Solid, Split, Still, Video
from mist import (BLK, RED, WHT, YEL, BigNumber, Blur, Corridor, Cycle, Dim, ECG, Embers, Flicker, Kinetic,
                  LightTunnel, LowerName, NeonBox, Polaroid, Quote, Rings, TimeArrow, Tint, TypeLine, chain, chroma,
                  heartbeat, shake)
from render import Shot
from words import WORDS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK = os.environ.get("STOCK_DIR", os.path.join(ROOT, "stock"))
_FILES = [p for p in glob.glob(os.path.join(STOCK, "*", "*")) if p.lower().endswith((".mp4", ".jpg", ".jpeg", ".png", ".webp"))]


def S(key):
    m = [p for p in _FILES if key in os.path.basename(p)]
    if not m:
        raise KeyError(f"stock {key!r} no encontrado")
    return m[0]


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


NW = [norm(w[2]) for w in WORDS]


class Anchor:
    def __init__(self):
        self.i = 0

    def __call__(self, phrase, lead=0.12):
        parts = [norm(p) for p in phrase.split()]
        for i in range(self.i, len(WORDS)):
            if all(i + k < len(NW) and NW[i + k].startswith(parts[k]) for k in range(len(parts))):
                self.i = i + 1
                return max(0.0, WORDS[i][0] - lead)
        raise LookupError(phrase)


# ------------------------------------------------------------------ helpers de bases
MOV = {"in": ((0.5, 0.5, 1.0), (0.5, 0.5, 1.14)), "out": ((0.5, 0.5, 1.16), (0.5, 0.5, 1.0)),
       "l": ((0.58, 0.5, 1.15), (0.42, 0.5, 1.15)), "r": ((0.42, 0.5, 1.15), (0.58, 0.5, 1.15)),
       "up": ((0.5, 0.6, 1.15), (0.5, 0.4, 1.15)), "down": ((0.5, 0.4, 1.15), (0.5, 0.6, 1.15)),
       "punch": ((0.5, 0.5, 1.05), (0.5, 0.5, 1.35))}


def kb(key, mv="in", g="mist", cam=None):
    c0, c1 = cam if cam else MOV[mv]
    return Still(S(key), c0, c1, grade=g)


def vid(key, start=0.0, speed=1.0, g="mist", z0=1.04, z1=1.12, rev=False):
    return Video(S(key), start, speed, grade=g, zoom0=z0, zoom1=z1, reverse=rev)


def embers(color=(150, 20, 26)):
    return Embers(color=color)


def black():
    return Embers(color=(40, 10, 12), n=60)


def pol(key, **kw):
    return Polaroid(S(key), **kw)


def K(*lines, **kw):
    """Kinetic con sintaxis corta: 'TEXTO|w TEXTO2|r' por línea."""
    out = []
    for ln in lines:
        items = []
        for chunk in ln.split(" / "):
            txt, _, sty = chunk.rpartition("|") if "|" in chunk else (chunk, "", "w")
            items.append((txt, sty or "w"))
        out.append(items)
    return Kinetic(out, **kw)


# ------------------------------------------------------------------ montaje
def build():
    a = Anchor()
    shots = []

    def add(t, base, ov=(), tr=None, td=0.4, tex=None, post=None):
        shots.append(Shot(t, base, list(ov), tr, td if tr else 0.0, tex, post))

    try:
        _build(a, add)
    except LookupError as e:  # tramo de la locución aún no disponible (parte 7)
        print("[timeline] ancla no encontrada, se corta aquí:", e)
    return shots


def _build(a, add):
    # ============ GANCHO =================================================================
    add(0.0, black(), [TypeLine("Imagina que acabas de morir.", t0=0.15, y=0.5, size=72, cps=17)])
    add(a("Tu cuerpo"), Solid("black"), [ECG(t0=0.0, flat_at=1.6)], tr="glitch", td=0.25)
    add(a("inmóvil") - 0.1, vid("mk_32789", 2, 0.8, "mist_cold"), [Dim(0.2)], tr="fade", td=0.3)
    add(a("Las personas"), vid("mk_43851", 3, 1.0, "mist_cold"))
    add(a("Puedes imaginar"), vid("mk_4701", 2, 1.0, "mist_cold"),
        [K("SUS ROSTROS|w", t0=0.6, size=110, y=0.42), K("SUS VOCES|w", t0=1.5, size=110, y=0.56),
         K("SUS LÁGRIMAS|r", t0=2.3, size=110, y=0.70)])
    add(a("Pero poco"), vid("mk_8743", 4, 0.9, "mist_cold"), [Blur(0, 14, 1.0), Dim(0.35, 1.5)])
    add(a("Ya no sientes"), kb("us_fmWFJ6pjrTg", "in", "mist_cold"), [Blur(10, 0, 0, 0.8)], tr="fade", td=0.5)
    add(a("Los sonidos"), vid("mk_4747", 3, 1.0, "mist_cold"), [Blur(0, 10, 0.8), Dim(0.3, 0.8)])
    add(a("Los recuerdos"), kb("us_7sPg5OLfExc", "in", "mist"), [Blur(0, 16, 1.5), Dim(0.4, 1.8)])
    add(a("como si alguien"), vid("mk_52299", 3, 1.0, "mist_red"),
        [K("CADA FRAGMENTO|w", "de tu existencia|s", t0=2.0, size=120, step=0.14)])
    add(a("Y entonces la"), black(), [K("Y ENTONCES|w", "la ves|s", t0=0.1, size=130)], tr="black", td=0.6)
    add(a("Una luz al"), LightTunnel((0.25, 0.7)), [K("UNA LUZ|w", "al final del túnel|sy", t0=0.3, size=120, y=0.78)],
        tr="flash", td=0.3)
    add(a("Cada vez es"), vid("mk_2026", 1, 1.0, "mist"), [K("MÁS INTENSA|w", t0=0.3, y=0.2, size=96),
                                                         K("MÁS CERCANA|y", t0=1.4, y=0.32, size=96)])
    add(a("Sientes que"), LightTunnel((0.6, 1.1), speed=1.6), [Rings(0.3, r0=0.12, r1=0.5)])
    add(a("tienes la sensación"), kb("wm_hieronymus", "up", "mist"),
        [LowerName("EL BOSCO · ASCENSO AL EMPÍREO (c. 1500)", t0=0.6)], tr="fade", td=0.4)
    add(a("que ningún ser"), kb("wm_hieronymus", cam=((0.62, 0.32, 1.6), (0.66, 0.3, 2.1)), g="mist"),
        [NeonBox("NADIE HA PODIDO EXPLICARLO", t0=0.9, pos=(0.5, 0.82), size=54)])
    add(a("Quizá piensas"), kb("us_6GXi5qAk", "in", "mist_cold"), [K("TUS SERES QUERIDOS|w", t0=1.8, y=0.8, size=96)],
        tr="fade", td=0.4)
    add(a("Quizá crees"), vid("mk_39707", 2, 1.0, "mist"), [K("EL CIELO|y", t0=0.9, size=150)])
    add(a("que vas a otro"), vid("mk_10410", 1, 1.0, "mist"), [K("OTRO PLANO|w", "de existencia|s", t0=0.4, size=110)])
    add(a("o que finalmente"), vid("mk_4113", 2, 1.0, "mist"),
        [K("¿QUÉ HAY|w", "DESPUÉS DE LA MUERTE?|r", t0=0.9, size=110)])
    add(a("pero y si no"), black(), [NeonBox("¿Y SI NO ES ASÍ?", t0=0.05, size=78)], tr="glitch", td=0.3, post=chroma(3))
    add(a("esa luz no"), LightTunnel((0.9, 0.6)), [K("¿Y SI ESA LUZ|w", "NO ES EL / CIELO?|r", t0=0.1, size=130, dim=0.25)])
    add(a("no hay ningún"), vid("mk_118", 2, 1.0, "mist_cold"), [K("NINGÚN|w / PARAÍSO|r", "esperándote|s", t0=0.4, size=130)])
    add(a("esa luz es"), kb("us_HqhKXIrfz8I", "in", "mist"),
        [K("LA MISMA LUZ|w", "que viste al nacer|sy", t0=1.6, size=120, y=0.78)], tr="flash", td=0.35)
    # título
    add(a("Detente"), embers(), [Rings(0.0, r0=0.2, r1=0.5, n=3),
                                K("¿Y SI MORIR|w", "ES VOLVER A / NACER?|r", t0=0.25, size=165, step=0.12)],
        tr="flash", td=0.5, post=chroma(2))
    # ============ EL PRIMER TÚNEL: EL VIENTRE ===========================================
    add(a("Antes de conocer"), kb("us_Bc7E9R84P2Q", "in", "mist"), [TypeLine("ANTES DE CONOCER ESTE MUNDO", t0=0.1, y=0.12, size=58)],
        tr="black", td=0.5)
    add(a("pasaste meses"), vid("mk_99925", 2, 1.0, "mist_red"), [BigNumber(" MESES", "dentro del vientre de tu madre", t0=0.3,
                                                                           count=(1, 9, 1.2), fmt="{:.0f}")])
    add(a("Un lugar oscuro"), vid("mk_3839", 1, 1.0, "mist_red"), [K("OSCURO|w", t0=0.1, y=0.4, size=120),
                                                                  K("CÁLIDO|r", t0=0.7, y=0.56, size=120)])
    add(a("donde no conocías"), kb("wm_leonardo", "in", "sepia"), [LowerName("LEONARDO DA VINCI · ESTUDIOS DEL FETO (c. 1511)", t0=0.5)])
    add(a("No sabías"), vid("mk_4148", 1, 1.0, "mist"), [K("LAS ESTRELLAS|w", t0=0.9, size=110)])
    add(a("los océanos"), vid("mk_44372", 2, 1.0, "mist_cold"), [K("LOS OCÉANOS|w", t0=0.0, size=110)], tr="whip_l", td=0.25)
    add(a("las ciudades"), vid("mk_42342", 2, 1.0, "mist"), [K("LAS CIUDADES|w", t0=0.0, size=110)], tr="whip_l", td=0.25)
    add(a("ni las personas"), vid("mk_4180", 1, 1.0, "mist"), [K("LAS PERSONAS|w", "que algún día amarías|s", t0=0.0, size=110)],
        tr="whip_l", td=0.25)
    add(a("Tu universo"), kb("nasa_carina", "out", "mist"), [K("TU UNIVERSO ENTERO|w", "dentro de otro cuerpo|sy", t0=0.2, size=120)],
        tr="zoom", td=0.5)
    add(a("Hasta que"), vid("mk_48186", 2, 1.0, "mist_red"), [], post=heartbeat(80, 0.05))
    add(a("Comenzaron"), vid("mk_41999", 1, 1.3, "mist_red"), [K("CONTRACCIONES|r", t0=0.3, size=130)], post=shake(0.6))
    add(a("Algo empezó"), LightTunnel((0.15, 0.4), speed=2.2), [Tint((1.3, 0.45, 0.4), 0.9, 0), K("ALGO EMPEZÓ|w", "A EMPUJARTE|r", t0=0.2, size=110)],
        post=shake(0.8))
    add(a("Atravesaste"), LightTunnel((0.3, 0.8), speed=2.6), [Tint((1.3, 0.5, 0.45), 0.8, 0),
                                                             K("UN ESPACIO ESTRECHO|w", t0=0.3, y=0.2, size=96),
                                                             K("una especie de túnel|sy", t0=1.6, y=0.8, size=110)])
    add(a("que te llevaba"), LightTunnel((0.8, 1.2), speed=3.0), [Tint((1.25, 0.6, 0.5), 0.6, 0)])
    add(a("Y entonces apareció"), LightTunnel((0.5, 1.0), speed=1.0), [K("Y ENTONCES|w", "apareció la luz|sy", t0=0.2, size=120, y=0.78, dim=0.2)])
    add(a("Saliste"), kb("us_JoeYzwliXto", "in", "mist"), [], tr="flash", td=0.4)
    add(a("Respiraste"), kb("us_dFy-FgVxAVs", "punch", "mist"), [K("PRIMERA VEZ|w", t0=0.5, y=0.8, size=110)])
    add(a("Escuchaste"), kb("us_WbC9XIlQb4k", "in", "mist"))
    add(a("y comenzaste"), vid("mk_49971", 3, 1.0, "mist"), [Dim(0.25)])
    add(a("absolutamente"), vid("mk_49970", 1, 1.0, "mist"), [K("ABSOLUTAMENTE|w", "NADA|r", t0=0.1, size=140, dim=0.3)])
    # ============ DOS TÚNELES ============================================================
    add(a("Ahora vuelv"), black(), [TypeLine("Ahora vuelve a imaginar tu muerte.", t0=0.1, y=0.5, size=66, cps=20)],
        tr="black", td=0.6)
    add(a("pasaría si"), vid("mk_4747", 1, 1.0, "mist_cold"), [K("EXPERIENCIAS|w", "cercanas a la muerte|s", t0=0.8, size=110, y=0.75)],
        tr="fade", td=0.3)
    add(a("una puerta"), Corridor(0.4), [K("¿UNA PUERTA|w", "HACIA OTRO PLANO?|r", t0=0.1, size=110, y=0.2)])
    add(a("Y si fuera"), Split([LightTunnel((0.6, 1.0)), Still(S("us_HqhKXIrfz8I"), (0.5, 0.5, 1.0), (0.5, 0.5, 1.1), "mist")],
                               gap=8, labels=["MORIR", "NACER"]))
    add(a("Y si la luz"), vid("mk_39708", 1, 1.0, "mist"), [K("EL MÁS ALLÁ|y", t0=1.6, size=130)])
    add(a("fuera la luz"), kb("us_vTknj2OxDVg", "in", "mist"), [K("LA LUZ DEL EXTERIOR|w", t0=0.4, size=110, y=0.2)])
    add(a("recibe a un"), kb("us_I8Ik4L3lPrs", "in", "mist"))
    add(a("morir y"), embers(), [K("MORIR|w / Y|s / NACER|r", t0=0.0, size=170, step=0.22)], tr="glitch", td=0.3)
    add(a("acontecimientos"), embers(), [K("NO SON DOS ACONTECIMIENTOS|w", t0=0.0, size=96, y=0.5)])
    add(a("Quizás sean"), embers((90, 14, 18)), [Cycle(0.1, "MORIR", "NACER", 0.25)])
    add(a("Cierras los"), vid("mk_4257", 0, 0.7, "mist"), [Quote(["Cierras los ojos en una vida", "y los abres en otra."], t0=0.2,
                                                                   pos=(0.5, 0.82))], tr="black", td=0.4)
    add(a("y los abres"), kb("us_WbC9XIlQb4k", cam=((0.45, 0.42, 1.5), (0.45, 0.42, 1.8)), g="mist"),
        [Quote(["Cierras los ojos en una vida", "y los abres en otra."], t0=0.0, pos=(0.5, 0.82), cps=999)], tr="flash", td=0.3)
    add(a("Abandonas"), vid("mk_434", 2, 1.0, "mist_red"), [K("ABANDONAS UN CUERPO|w", "y llegas a otro|s", t0=0.4, size=110)])
    add(a("Una familia te"), Split([Still(S("us_Cxpqnzd3Psg"), (0.5, 0.5, 1.0), (0.5, 0.5, 1.1), "mist_cold"),
                                    Video(S("mk_49970"), 2, 1.0, "mist", 1.0, 1.08)], gap=8, labels=["TE DESPIDEN", "TE ESPERAN"]))
    add(a("Y lo más extraño"), black(), [NeonBox("NINGUNO DE LOS DOS MUNDOS LO SABE", t0=1.6, size=56)], tr="glitch", td=0.3)
    add(a("porque tal vez"), vid("mk_43853", 2, 1.0, "mist_cold"), [K("TUS VIDAS ANTERIORES|w", t0=0.8, size=110, y=0.8)])
    add(a("Cada vez que naces"), vid("mk_50951", 1, 1.0, "mist"), [K("TODO LO QUE FUISTE|w", "desaparece|s", t0=0.6, size=120)])
    add(a("Tu nombre"), black(), [TypeLine("NOMBRE: ________", t0=0.05, y=0.38, size=80, cps=40, color=WHT),
                                  K("CAMBIA|r", t0=0.6, y=0.6, size=130)])
    add(a("tu rostro"), vid("mk_34522", 1, 1.0, "mist"), [K("TU ROSTRO|w", "CAMBIA|r", t0=0.0, size=120)], tr="glitch", td=0.25)
    add(a("tus padres"), embers((60, 30, 20)), [pol("wm_portretfotografie", t0=0.0, w=0.3, angle=-5, pos=(0.36, 0.5)),
                                               pol("wm_lindholm", t0=0.4, w=0.34, angle=6, pos=(0.66, 0.5))])
    add(a("tus recuerdos"), embers(), [BigNumber("", "TUS RECUERDOS COMIENZAN DESDE CERO", t0=0.0, count=(9999, 0, 1.8), size=280)])
    add(a("Pero y si algo"), black(), [NeonBox("¿Y SI ALGO PERMANECE?", t0=0.3, size=70)], tr="black", td=0.4)
    add(a("Y si es esa"), vid("mk_39668", 2, 1.0, "mist"), [K("LA SENSACIÓN|w", "de estar vivo|s", t0=0.8, size=110)])
    add(a("a través de"), vid("mk_4257", 2, 1.0, "mist"), [K("A TRAVÉS DE TUS PROPIOS OJOS|w", t0=0.3, size=96, y=0.82)])
    add(a("de sentir"), vid("mk_4401", 2, 1.0, "mist"), [K("ERES TÚ|r", t0=0.9, size=150)])
    add(a("continúa de"), vid("mk_1704", 1, 1.0, "mist"), [K("DE UNA VIDA|w", "a otra|sy", t0=0.2, size=120)])
    add(a("Tal vez no estás"), embers(), [K("TU PRIMERA|w / EXISTENCIA|r", t0=0.1, size=140)], tr="fade", td=0.3)
    add(a("vez simplemente"), embers((50, 30, 20)), [pol("wm_vera-andersen", t0=0.0, w=0.24, angle=-8, pos=(0.25, 0.5)),
                                                     pol("wm_baby-kruipend", t0=0.35, w=0.3, angle=4, pos=(0.52, 0.47)),
                                                     pol("wm_mother-and-child", t0=0.7, w=0.24, angle=-3, pos=(0.78, 0.53)),
                                                     K("LAS ANTERIORES|w", t0=1.4, size=110, y=0.88)])
    # ============ LOS PATRONES ==========================================================
    add(a("Y aquí es"), black(), [K("Y AQUÍ TODO SE VUELVE|w", "MÁS PERTURBADOR|r", t0=0.2, size=120)], tr="glitch", td=0.35,
        post=chroma(3))
    add(a("porque si cada"), vid("mk_100558", 1, 1.0, "mist"), [Cycle(0.4, "MUERTE", "NACIMIENTO", 0.3, r=0.26)])
    add(a("no resolviste"), vid("mk_100558", 6, 1.0, "mist"), [K("TODO LO QUE|w", "NO RESOLVISTE|r", t0=0.0, size=120)])
    add(a("y si no estás"), black(), [NeonBox("¿NO ESTÁS AQUÍ POR CASUALIDAD?", t0=0.1, size=62)], tr="glitch", td=0.3)
    add(a("y si estás repitiendo"), vid("mk_28894", 1, 1.0, "mist"), [K("REPITIENDO|r", "una historia sin terminar|s", t0=0.4, size=120)])
    add(a("los patrones"), vid("mk_2846", 2, 1.0, "mist_cold"), [K("LOS PATRONES|w", t0=0.6, size=130)])
    add(a("los mismos errores"), vid("mk_25594", 3, 1.0, "mist"), [K("LOS MISMOS ERRORES|w", t0=0.1, size=110, y=0.82)], tr="whip_r", td=0.25)
    add(a("las mismas relaciones"), vid("mk_4504", 2, 1.0, "mist"), [K("LAS MISMAS RELACIONES|w", t0=0.1, size=110, y=0.82)],
        tr="whip_r", td=0.25)
    add(a("miedos"), vid("mk_4511", 0, 0.8, "mist_cold"), [K("LOS MISMOS MIEDOS|w", t0=0.0, size=110, y=0.82)], tr="whip_r", td=0.25)
    add(a("las mismas decisiones"), vid("mk_8750", 2, 1.0, "mist"), [K("LAS MISMAS DECISIONES|r", t0=0.1, size=110, y=0.82)],
        tr="whip_r", td=0.25)
    add(a("y si no fuera"), black(), [K("¿Y SI NO FUERA|w", "LA PRIMERA VEZ?|r", t0=0.1, size=130)], tr="glitch", td=0.3,
        post=chroma(4))
    add(a("Quizá en otra"), vid("mk_18308", 3, 1.0, "mist_cold"), [K("TE ENAMORASTE|w", t0=1.0, size=110, y=0.2)])
    add(a("Quizá también perdiste"), vid("mk_4701", 4, 1.0, "mist"), [K("OPORTUNIDADES PERDIDAS|w", t0=0.6, size=110, y=0.82)])
    add(a("Quizá también tuviste"), vid("mk_28890", 1, 1.0, "mist"), [K("ELEGISTE|w", "EXACTAMENTE LO MISMO|r", t0=1.8, size=110)])
    add(a("Y ahora estás"), vid("mk_39668", 6, 1.0, "mist"), [K("OTRA VERSIÓN|w", "de esa historia|s", t0=1.2, size=120)])
    add(a("Y si cada nueva"), vid("mk_39705", 2, 1.0, "mist"), [K("OTRA OPORTUNIDAD|y", t0=1.0, size=120)], tr="fade", td=0.4)
    add(a("Y si el"), embers((90, 14, 18)), [Cycle(0.0, "MUERTE", "NACIMIENTO", 0.6),
                                            K("ROMPER|r", "EL CICLO|w", t0=1.6, size=100, y=0.5)])
    add(a("O peor"), black(), [K("O PEOR AÚN|r", t0=0.05, size=150)], tr="glitch", td=0.25, post=chroma(5))
    add(a("y si estuvieras"), vid("mk_2561", 2, 1.0, "mist"), [K("UNA|w", t0=0.9, y=0.3, size=140), K("Y OTRA|w", t0=1.3, y=0.45, size=140),
                                                               K("VEZ|r", t0=1.7, y=0.6, size=140)])
    add(a("sin saber"), vid("mk_28894", 6, 1.0, "mist"), [K("SIN SABERLO|w", t0=0.5, size=120, y=0.82)])
    # ============ EL TIEMPO ==============================================================
    add(a("Pero espera"), black(), [NeonBox("PERO ESPERA", t0=0.05, size=90)], tr="glitch", td=0.3, post=chroma(4))
    add(a("hay algo"), embers(), [K("ALGO TODAVÍA|w", "MÁS EXTRAÑO|r", t0=0.2, size=130)])
    add(a("Siempre hemos"), vid("mk_1704", 4, 1.0, "mist"), [Dim(0.35), TimeArrow(1.5, step=1.4)])
    add(a("pero y si el tiempo"), vid("mk_2561", 8, 1.0, "mist", rev=True), [K("¿Y SI EL TIEMPO|w", "NO FUNCIONA ASÍ?|r", t0=0.3, size=110)])
    add(a("Tal vez no renaces"), embers(), [K("NO RENACES|w", "en el futuro|s", t0=0.2, size=130)])
    add(a("tal vez podrías"), kb("wm_pieter-bruegel-the-elder-hunters", "r", "mist"), [K("EL PASADO|y", t0=1.1, size=130, y=0.8)])
    add(a("en el presente"), vid("mk_42342", 6, 1.0, "mist"), [K("EL PRESENTE|w", t0=0.0, size=130, y=0.8)], tr="whip_l", td=0.25)
    add(a("futuro que todavía"), kb("nasa_iss", "in", "mist_cold"), [K("UN FUTURO|r", "que todavía no existe|s", t0=0.2, size=120, y=0.78)],
        tr="whip_l", td=0.25)
    add(a("Imagina que todas"), kb("wm_pieter-bruegel-the-elder-the-tower", "in", "mist"),
        [K("TODAS LAS VIDAS|w", "son habitaciones|s", t0=0.7, size=110, y=0.82)], tr="black", td=0.5)
    add(a("de un edificio"), Corridor(0.5), [K("UN EDIFICIO|w", "INFINITO|r", t0=0.2, size=130, y=0.2)])
    add(a("En una habitación"), kb("wm_pieter-bruegel-the-elder-peasant", "l", "mist"),
        [K("NACISTE HACE|s", t0=0.3, size=100, y=0.3), BigNumber(" AÑOS", "", t0=0.8, count=(0, 500, 1.2), fmt="{:.0f}", pos=(0.5, 0.55))])
    add(a("en otra estás"), vid("mk_4401", 8, 1.0, "mist"), [K("AHORA MISMO|w", t0=0.2, size=130)], tr="whip_l", td=0.25)
    add(a("en otra todavía"), vid("mk_10408", 1, 1.0, "mist"), [K("TODAVÍA NO|w", "HAS NACIDO|r", t0=0.2, size=130)], tr="whip_l", td=0.25)
    add(a("Cada habitación"), embers((60, 30, 20)), [pol("wm_hans-holbein", t0=0.0, w=0.22, angle=-6, pos=(0.2, 0.46)),
                                                     pol("wm_kinematograph", t0=0.4, w=0.3, angle=3, pos=(0.47, 0.42)),
                                                     pol("wm_karl-friedrich", t0=0.8, w=0.28, angle=-4, pos=(0.76, 0.5)),
                                                     pol("wm_portraits-of-an", t0=1.4, w=0.22, angle=7, pos=(0.36, 0.7)),
                                                     pol("wm_opening-prayer", t0=1.9, w=0.28, angle=-2, pos=(0.64, 0.72))])
    add(a("una época"), kb("wm_karl-friedrich", "r", "mist"), [K("OTRA ÉPOCA|w", "otro mundo|s", t0=0.4, size=120, y=0.8)])
    add(a("pero todas"), black(), [K("ALGO EN COMÚN|w", t0=0.1, size=120)], tr="fade", td=0.3)
    add(a("alguien llega"), embers(), [K("LLEGA|w", t0=0.0, size=150, y=0.3, step=0.1), K("VIVE|w", t0=0.45, size=150, y=0.45),
                                       K("MUERE|r", t0=0.9, size=150, y=0.6)])
    add(a("y vuelve a"), Corridor(0.9), [K("Y VUELVE A ATRAVESAR|w", "UNA PUERTA|r", t0=0.2, size=110, y=0.18)])
    add(a("quizá el tiempo"), vid("mk_1704", 7, 1.0, "mist"), [TimeArrow(0.0, step=0.5), K("¿UNA LÍNEA?|w", t0=1.4, size=110, y=0.25)])
    add(a("quizá sea un"), vid("mk_2075", 4, 1.0, "mist"), [K("UN LABERINTO|r", t0=0.5, size=150)], tr="zoom", td=0.5)
    add(a("en el que la"), kb("us_hPRXeiQQ4-s", "punch", "mist"), [K("LA CONCIENCIA SALTA|w", t0=0.6, size=110, y=0.82)])
    add(a("sin recordar"), kb("us_z3v__zzp22U", cam=((0.5, 0.5, 1.0), (0.5, 0.5, 1.4, 25)), g="mist"),
        [K("SIN RECORDAR|w", "dónde estuvo antes|s", t0=0.5, size=110)])
    add(a("Y si esto fuera"), vid("mk_4180", 4, 1.0, "mist"), [K("TODAS LAS VIDAS|w", "que podrías estar viviendo|s", t0=1.0, size=110)],
        tr="fade", td=0.3)
    add(a("Quizá en algún"), Split([Still(S("us_dFy-FgVxAVs"), (0.5, 0.5, 1.0), (0.5, 0.5, 1.1), "mist"),
                                    Still(S("us_CjgwW0VR3d0"), (0.5, 0.5, 1.0), (0.5, 0.5, 1.1), "mist_cold")],
                                   gap=8, labels=["NACIENDO", "MURIENDO"]))
    add(a("Quizá otra está"), kb("wm_kinematograph", "r", "sepia"), [LowerName("VIENA, HACIA 1900", t0=0.6)])
    add(a("Quizá alguien"), kb("wm_the-triumph-of-death", "l", "mist"), [K("MURIÓ HACE SIGLOS|w", t0=0.6, size=110, y=0.82)])
    add(a("está comenzando"), kb("us_OUYg0Q3ec-Y", "in", "mist"), [K("COMIENZA AHORA|y", t0=0.4, size=120, y=0.8)])
    add(a("todavía no debería"), embers(), [K("TODAVÍA NO|w", "DEBERÍA EXISTIR|r", t0=0.0, size=130)])
    # ============ LA PREGUNTA ============================================================
    add(a("Y entonces aparece"), black(), [TypeLine("La pregunta más inquietante de todas...", t0=0.6, y=0.5, size=62, cps=24)],
        tr="black", td=0.6)
    add(a("Y si nunca"), embers(), [Rings(0.0, n=3), K("¿Y SI NUNCA HAS TENIDO|w", "UN VERDADERO|w / COMIENZO?|r", t0=0.1, size=120)],
        tr="flash", td=0.3)
    add(a("Y si tu existencia"), kb("nasa_gsfc", "in", "mist"), [Cycle(0.3, "NACIMIENTO", "MUERTE", 0.8, r=0.3)])
    add(a("Una historia"), vid("mk_50956", 1, 1.0, "mist"), [K("QUE NUNCA|w", "TERMINA|r", t0=1.2, size=140)])
    add(a("Tal vez llevas"), kb("wm_pieter-bruegel-the-elder-hunters", cam=((0.3, 0.4, 1.5), (0.5, 0.5, 1.0)), g="mist"),
        [K("MILES DE AÑOS|w", "aquí|s", t0=0.4, size=130)])
    add(a("tal vez ha sido"), embers((50, 30, 20)), [pol("wm_rembrandt", t0=0.0, w=0.2, angle=-6, pos=(0.17, 0.4)),
                                                     pol("wm_lindholm", t0=0.25, w=0.22, angle=4, pos=(0.38, 0.6)),
                                                     pol("wm_vera-andersen", t0=0.5, w=0.18, angle=-3, pos=(0.58, 0.38)),
                                                     pol("wm_hans-holbein", t0=0.75, w=0.18, angle=6, pos=(0.8, 0.58)),
                                                     K("CIENTOS|y / de personas|s", t0=1.1, size=130, y=0.88, dim=0.25)])
    add(a("tal vez has amado"), vid("mk_18308", 10, 1.0, "mist"), [K("AMADO|w", t0=0.0, size=150)])
    add(a("sufrido"), vid("mk_43851", 10, 1.0, "mist_cold"), [K("SUFRIDO|w", t0=0.0, size=150)])
    add(a("olvidado"), vid("mk_1961", 2, 1.0, "mist"), [K("OLVIDADO|w", t0=0.0, size=150)])
    add(a("y vuelto"), kb("us_OUYg0Q3ec-Y", "in", "mist"), [K("VUELTO A COMENZAR|r", t0=0.0, size=130)])
    add(a("tantas veces"), kb("nasa_carina", cam=((0.42, 0.55, 2.6), (0.5, 0.5, 1.0)), g="mist"),
        [K("UN PEQUEÑO FRAGMENTO|w", "de algo muchísimo más grande|sy", t0=1.6, size=110)])
    add(a("peor es que"), black(), [NeonBox("NUNCA PODRÍAS SABERLO", t0=0.1, size=80)], tr="glitch", td=0.3, post=chroma(4))
    add(a("porque si cada"), vid("mk_50951", 8, 1.0, "mist"), [K("CADA NACIMIENTO|w", "BORRA LO ANTERIOR|r", t0=0.5, size=110)])
    add(a("manera de distinguir"), embers(), [BigNumber("", "TU PRIMERA VIDA... O LA NÚMERO MIL", t0=0.2, count=(1, 1000, 2.0), size=300)])
    add(a("solo conocerías"), vid("mk_34522", 4, 1.0, "mist"), [K("LA VERSIÓN ACTUAL|w", "de ti mismo|s", t0=0.8, size=110)])
    add(a("Así que"), kb("us_73OJLcahQHg", "in", "mist"), [K("UNA FOTOGRAFÍA TUYA|w", "de bebé|sy", t0=1.5, size=110, y=0.72)],
        tr="black", td=0.5)
    add(a("detente unos"), kb("us_cqgnUEOaW00", "in", "mist"), [])
    # ============ FINAL (parte 7 de la voz) =============================================
    add(a("Mira ese"), embers((50, 30, 20)), [pol("wm_vera-andersen", t0=0.0, w=0.32, angle=-2, pos=(0.5, 0.5))], tr="fade", td=0.5)
    add(a("Esos ojos"), kb("wm_vera-andersen", cam=((0.5, 0.3, 2.0), (0.5, 0.3, 2.4)), g="sepia"))
    add(a("Esa persona"), vid("mk_4225", 0, 0.8, "mist"), [Dim(0.15)])
    add(a("qué perderá"), vid("mk_4225", 3, 0.8, "mist"), [K("¿CUÁNTO TIEMPO|w", "tendrá que vivir?|s", t0=0.9, size=110, y=0.8)])
    add(a("Y pregúntate"), black(), [TypeLine("Y pregúntate:", t0=0.1, y=0.5, size=76, cps=18)], tr="black", td=0.5)
    add(a("Estás viendo"), kb("wm_baby-kruipend", "in", "sepia"), [K("¿EL COMIENZO|w", "de tu vida...|s", t0=0.4, size=120, dim=0.3)])
    add(a("o el momento"), kb("wm_portraits-of-an", "in", "sepia"), [K("¿O EL MOMENTO EN QUE|w", "OLVIDASTE TODAS|r", "LAS ANTERIORES?|r",
                                                                   t0=0.4, size=110)], tr="flash", td=0.3)
    add(a("Porque quizá"), kb("us_gYC68k9trV8", "in", "mist_cold"), [K("LA MUERTE|w", "no sea el final|s", t0=0.8, size=120)],
        tr="black", td=0.5)
    add(a("Quizá sea simplemente"), kb("us_OUYg0Q3ec-Y", "in", "mist"), [K("SINO EL COMIENZO|y", "de la siguiente|s", t0=1.2, size=120)])
    add(a("Y tal vez"), LightTunnel((0.3, 1.6), speed=1.3), [K("CUANDO VUELVAS A VER|w", "ESA LUZ...|y", t0=0.6, size=120, y=0.8)],
        tr="fade", td=0.6)
    add(a("todo esto"), LightTunnel((1.6, 2.2), speed=0.6), [K("TODO ESTO|w", "YA TE HAYA OCURRIDO|r", "ANTES|r", t0=0.3, size=120, dim=0.35),
                                                           Flicker(2.6, 1.2, peak=1.0)])
    end = a("antes", lead=-0.6)
    add(end, embers(), [K("¿Y SI MORIR|w", "ES VOLVER A / NACER?|r", t0=0.6, size=150, step=0.14)], tr="flash", td=0.8)
