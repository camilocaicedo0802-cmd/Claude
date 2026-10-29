"""Montaje del piloto E001 (bloques 1 a 3): movimiento, rótulos, mapa, sellos y sonido, todo por código.

Entradas:
- video/E001/planos_piloto.json                  guion de planos (scripts/e001_planos.py)
- video/E001/img/<id>.png                        imágenes; si falta una, sale un marcador "imagen pendiente"
- video/E001/audio/E001_01.mp3 y _tiempos.json   narración con tiempos por carácter (scripts/e001_voz.py)
- video/E001/audio/musica.mp3                    opcional: música de la Biblioteca de Audio de YouTube

Sin narración, los tiempos se estiman a partir del texto y sale una animática con subtítulos quemados.
Con narración, los subtítulos van aparte en piloto.srt (regla de la fase 6: no se queman en los largos).

Salidas en trabajo/E001/ (carpeta local, no se versiona): piloto.mp4 (1920×1080, 30 fps) y piloto.srt.

Uso:
    python3 scripts/e001_montaje.py               # piloto completo
    python3 scripts/e001_montaje.py --borrador    # 960×540 y codificación rápida
    python3 scripts/e001_montaje.py --muestras    # además, un fotograma de cada plano en trabajo/E001/muestras/

Los textos en pantalla, su posición y los efectos de cada plano están en EDICION (más abajo).
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
import wave
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_voz import MP3, TIEMPOS, texto_parte  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
VIDEO = RAIZ / "video/E001"
TRABAJO = RAIZ / "trabajo/E001"
FUENTES = RAIZ / "trabajo/fuentes"
MAPAS = RAIZ / "trabajo/mapas"
MUSICA = VIDEO / "audio/musica.mp3"

FPS = 30
PREVIO = 0.5   # segundos antes de que empiece la voz
COLA = 1.6     # segundos después de la última palabra
ADELANTO = 0.07  # el corte entra un poco antes de la palabra
SR = 48000

# Paleta de la fase 6
NOCHE = (20, 22, 31)
TINTA = (30, 26, 22)
PAPEL = (234, 219, 192)
PAPEL_CLARO = (246, 236, 214)
HUESO = (246, 240, 228)
COCHINILLA = (179, 39, 45)
AZUL = (61, 141, 181)
ORO = (217, 166, 55)
VERDE = (46, 91, 69)

DESCARGAS = {
    "Anton-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf",
    "Fraunces.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf",
    "Fraunces-Italic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces-Italic%5BSOFT,WONK,opsz,wght%5D.ttf",
    "Inter.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "paises_110m.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson",
    "estados_110m.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_1_states_provinces.geojson",
}


# ---------------------------------------------------------------- edición de cada plano

def grito(texto, acento=None, pos=(0.5, 0.18), en=None, tam=150, ancho=0.86):
    """Frase grande en Anton, hueso con contorno tinta y una palabra en cochinilla."""
    return dict(tipo="grito", texto=texto, acento=acento, pos=pos, en=en, tam=tam, ancho=ancho)


def fecha(texto, pos=(0.5, 0.16), en=None, tam=78):
    """Rótulo de fecha y lugar en Fraunces; la primera parte en oro."""
    return dict(tipo="fecha", texto=texto, pos=pos, en=en, tam=tam)


def etiqueta(texto, pos=(0.2, 0.14), en=None):
    return dict(tipo="etiqueta", texto=texto, pos=pos, en=en)


def nombre(texto, pos=(0.05, 0.78), en=None):
    """Rótulo inferior con el nombre de una persona (pos es la esquina izquierda)."""
    return dict(tipo="nombre", texto=texto, pos=pos, en=en)


def tarjeta(texto, acento=None, pos=(0.5, 0.2), en=None):
    """Tarjeta de fuente en papel claro (periódicos, biografías, museo)."""
    return dict(tipo="tarjeta", texto=texto, acento=acento, pos=pos, en=en)


def sello(texto, color=COCHINILLA, pos=(0.5, 0.5), en=None, giro=-8, tam=120, retraso=0.0):
    return dict(tipo="sello", texto=texto, color=color, pos=pos, en=en, giro=giro, tam=tam, retraso=retraso)


def capitulo(numero, titulo, extra=None, pos=(0.5, 0.17), en=None):
    return dict(tipo="capitulo", numero=numero, titulo=titulo, extra=extra, pos=pos, en=en)


def expediente(arriba, principal, pos=(0.5, 0.2), en=None):
    return dict(tipo="expediente", arriba=arriba, principal=principal, pos=pos, en=en)


# desc: lo que muestra el marcador mientras falta la imagen; foco: punto hacia el que va la cámara
# sfx: (sonido, palabra o segundos desde el inicio del plano, ganancia)
EDICION = {
    "S01": dict(desc="Silueta de la Ciudad de México al amanecer", foco=(0.5, 0.62),
                textos=[fecha("1842 · MÉXICO", pos=(0.5, 0.3), tam=104)], sfx=[("campana", 0.25, 0.5)]),
    "S02": dict(desc="Desfile militar de perfil, con banderas tricolor", sfx=[("tambor", 0.0, 0.55)]),
    "S03": dict(desc="Dos cañones disparan salvas de honor", textos=[etiqueta("SALVAS DE CAÑÓN", en="cañonazos")],
                sfx=[("canon", 0.02, 0.8), ("canon", 0.5, 0.6)]),
    "S04": dict(desc="Orador en un podio frente a la multitud", foco=(0.5, 0.4)),
    "S05": dict(desc="Ataúd pequeño con una sola pierna dentro", foco=(0.5, 0.58),
                textos=[grito("¿UNA PIERNA?", "PIERNA", en="pierna")]),
    "S06": dict(desc="Santa Anna de cuerpo entero bajo un foco (con REF)",
                textos=[grito("NO ES UNA METÁFORA", "METÁFORA", pos=(0.5, 0.15), tam=120),
                        nombre("ANTONIO LÓPEZ DE SANTA ANNA", en="antonio")]),
    "S07": dict(desc="Fila de soldados en posición de firmes"),
    "S08": dict(desc="Poeta con pluma y un pergamino larguísimo", foco=(0.45, 0.48), sfx=[("pluma", 0.1, 0.5)]),
    "S09": dict(desc="Columna con una urna en un cementerio antiguo"),
    "S10": dict(desc="Santa Anna congelado a mitad del saludo (con REF)",
                textos=[grito("NI SIQUIERA ES LO MÁS RARO", "RARO", pos=(0.32, 0.5), tam=140, ancho=0.5)],
                sfx=[("impacto", 0.0, 0.7)]),
    "S11": dict(desc="Pierna de corcho en una vitrina de museo",
                textos=[fecha("HOY · EN UNA VITRINA", pos=(0.5, 0.14), en="hoy")]),
    "S12": dict(desc="Mapa: de México a Illinois", mapa=True, sfx=[("whoosh", 0.1, 0.6)]),
    "S13": dict(desc="Las dos piernas como piezas de museo",
                textos=[grito("¿CUÁL TUVO EL DESTINO MÁS ABSURDO?", "ABSURDO", pos=(0.5, 0.17), tam=118, ancho=0.9)]),
    "S14": dict(desc="Santa Anna en un pedestal: aplausos y abucheos (con REF)",
                textos=[grito("¿HÉROE?", pos=(0.2, 0.2), tam=130),
                        grito("¿VILLANO?", "¿VILLANO?", pos=(0.8, 0.2), en="discutidos", tam=130)]),
    "S15": dict(desc="Libro de historia con una página arrancada", foco=(0.5, 0.5),
                textos=[grito("LA PARTE QUE FALTA", "FALTA", en="nadie")], sfx=[("papel", 0.05, 0.5)]),
    "S16": dict(desc="Alguien mira el celular con desconfianza",
                textos=[grito("¿CHISME DE INTERNET?", pos=(0.5, 0.17), tam=125),
                        sello("NO", pos=(0.5, 0.52), en="internet", tam=230, giro=-10, retraso=0.2)]),
    "S17": dict(desc="Periódico, biografía y ficha de museo",
                textos=[tarjeta("PERIÓDICOS 1842", "1842", pos=(0.22, 0.14), en="periódicos"),
                        tarjeta("BIOGRAFÍAS", pos=(0.5, 0.14), en="biografías"),
                        tarjeta("MUSEO", pos=(0.8, 0.14), en="museo")], sfx=[("papel", 0.0, 0.4)]),
    "S18": dict(desc="Lupa sobre un documento antiguo",
                textos=[sello("CON FUENTES.\nSIN CUENTOS.", pos=(0.7, 0.68), en="también", tam=96, giro=-6)]),
    "S19": dict(desc="Ataúd con cinta tricolor y una medalla",
                textos=[capitulo("1", "EL FUNERAL", en="cómo")]),
    "S20": dict(desc="La columna de noche, con la urna volcada",
                textos=[capitulo("2", "LA TUMBA VACÍA", "1844", en="después")]),
    "S21": dict(desc="Dos amigos en la sobremesa; uno cuenta la historia",
                textos=[capitulo("3", "UNA HISTORIA PARA CONTAR", en="historia")]),
    "S22": dict(desc="Tres sellos de madera con tinta verde, oro y carmesí",
                textos=[sello("VERDAD", VERDE, pos=(0.22, 0.24), en="verdad", giro=-7),
                        sello("A MEDIAS", ORO, pos=(0.5, 0.2), en="medias", giro=4),
                        sello("MITO", COCHINILLA, pos=(0.78, 0.24), en="mito", giro=-5)]),
    "S23": dict(desc="Sobre lacrado con sello rojo bajo un foco",
                textos=[expediente("PRÓXIMO", "EXPEDIENTE", pos=(0.5, 0.2), en="continuación")]),
    "S24": dict(desc="Santa Anna entra y se quita el bicornio (con REF)",
                textos=[expediente("EXPEDIENTE N.º 001", "SANTA ANNA", pos=(0.72, 0.42), en="dueño")]),
}

# Movimiento de cámara según el texto de "movimiento" del guion de planos:
# (zoom inicial, zoom final, desplazamiento en x de inicio a fin, en y, sacudida inicial en px)
CAMARAS = [
    ("sacudida + acercamiento", (1.0, 1.12, None, None, 0)),
    ("corte seco", (1.07, 1.1, None, None, 14)),
    ("acercamiento + sello", (1.0, 1.08, None, None, 0)),
    ("leve acercamiento", (1.0, 1.05, None, None, 0)),
    ("acercamiento a", (1.0, 1.2, None, None, 0)),
    ("acercamiento", (1.0, 1.1, None, None, 0)),
    ("paneo izquierda", (1.18, 1.18, (0.36, 0.64), None, 0)),
    ("paneo de abajo", (1.22, 1.22, None, (0.64, 0.36), 0)),
    ("paneo siguiendo", (1.15, 1.18, (0.4, 0.6), None, 0)),
    ("paneo cenital", (1.14, 1.16, (0.42, 0.58), (0.52, 0.48), 0)),
    ("paneo lateral", (1.14, 1.14, (0.43, 0.57), None, 0)),
    ("golpes de sello", (1.0, 1.04, None, None, 0)),
    ("dibujo de la flecha", (1.0, 1.06, None, None, 0)),
]


# ---------------------------------------------------------------- utilidades

def asegurar_recursos():
    for nombre_archivo, url in DESCARGAS.items():
        destino = (MAPAS if nombre_archivo.endswith(".geojson") else FUENTES) / nombre_archivo
        if not destino.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            print("Descargando", nombre_archivo)
            urllib.request.urlretrieve(url, destino)


@lru_cache(maxsize=None)
def fuente(familia, tam, peso=400):
    archivo = {"anton": "Anton-Regular.ttf", "fraunces": "Fraunces.ttf",
               "fraunces-it": "Fraunces-Italic.ttf", "inter": "Inter.ttf"}[familia]
    f = ImageFont.truetype(str(FUENTES / archivo), max(8, round(tam)))
    if familia != "anton":
        ejes = []
        for eje in f.get_variation_axes():
            n = eje["name"]
            n = n.decode() if isinstance(n, bytes) else n
            valor = {"Weight": peso, "Optical Size": min(eje["maximum"], max(eje["minimum"], tam)),
                     "Softness": 0, "Wonky": 0}.get(n, eje["default"])
            ejes.append(valor)
        f.set_variation_by_axes(ejes)
    return f


def sin_tildes(c):
    return unicodedata.normalize("NFD", c)[0].lower()


def suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def salida(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def rebote(x):
    x = min(1.0, max(0.0, x))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def con_alfa(img, alfa):
    if alfa >= 0.999:
        return img
    img = img.copy()
    img.putalpha(img.getchannel("A").point([round(v * alfa) for v in range(256)]))
    return img


def pegar(fondo, capa, cx, cy, alfa=1.0, escala=1.0):
    if alfa <= 0.003:
        return
    if abs(escala - 1) > 0.002:
        capa = capa.resize((max(1, round(capa.width * escala)), max(1, round(capa.height * escala))), Image.BICUBIC)
    capa = con_alfa(capa, alfa)
    fondo.paste(capa, (round(cx - capa.width / 2), round(cy - capa.height / 2)), capa)


def sombra(capa, radio, desplazamiento, opacidad=0.55, color=TINTA):
    """Devuelve la capa con una sombra suave debajo (mismo centro)."""
    m = radio * 2 + abs(desplazamiento) * 2
    lienzo = Image.new("RGBA", (capa.width + m * 2, capa.height + m * 2), (0, 0, 0, 0))
    s = Image.new("RGBA", lienzo.size, color + (0,))
    a = Image.new("L", lienzo.size, 0)
    a.paste(capa.getchannel("A").point([round(v * opacidad) for v in range(256)]), (m, m + desplazamiento))
    s.putalpha(a.filter(ImageFilter.GaussianBlur(radio)))
    s.alpha_composite(capa, (m, m))
    return s


# ---------------------------------------------------------------- tiempos

class Narracion:
    """Texto de la narración (espacios colapsados) con el inicio y el fin de cada carácter."""

    def __init__(self, datos):
        self.texto, self.ini, self.fin = "", [], []
        for c, a, b in zip(datos["caracteres"], datos["inicios"], datos["finales"]):
            if c.isspace():
                if not self.texto or self.texto[-1] == " ":
                    continue
                c = " "
            self.texto += c
            self.ini.append(a + PREVIO)
            self.fin.append(b + PREVIO)
        self.clave = "".join(sin_tildes(c) for c in self.texto)

    def buscar(self, frase, desde=0):
        k = "".join(sin_tildes(c) for c in " ".join(frase.split()))
        i = self.clave.find(k, desde)
        if i < 0:
            raise ValueError(f"No encuentro en la narración: {frase!r}")
        return i

    def palabra(self, palabra, desde, hasta):
        k = "".join(sin_tildes(c) for c in palabra)
        for m in re.finditer(rf"(?<!\w){re.escape(k)}(?!\w)", self.clave[desde:hasta]):
            return desde + m.start()
        raise ValueError(f"No encuentro la palabra {palabra!r} en el plano")

    @property
    def final(self):
        return self.fin[-1]


def estimar_tiempos(texto):
    """Sin narración: unos 15 caracteres por segundo y pausas en la puntuación."""
    caracteres, inicios, finales, t = [], [], [], 0.0
    for i, c in enumerate(texto):
        caracteres.append(c)
        inicios.append(t)
        t += 1 / 15
        finales.append(t)
        siguiente = texto[i + 1] if i + 1 < len(texto) else ""
        if c == "." and siguiente == ".":
            t += 0.22
        elif c in ".?!":
            t += 0.38
        elif c in ",:":
            t += 0.14
        elif c == "\n":
            t += 0.3
    return {"caracteres": caracteres, "inicios": inicios, "finales": finales, "fuente": "estimado"}


def subtitulos(narr, maximo=42):
    """Bloques de subtítulos: una frase por bloque, como mucho dos líneas de `maximo` caracteres."""
    bloques, inicio = [], 0
    for m in re.finditer(r"[.?!:](?=\s|$)(?!\.)", narr.texto):
        bloques.append((inicio, m.end()))
        inicio = m.end() + 1
    resultado = []
    for a, b in bloques:
        frase = narr.texto[a:b].strip()
        trozos = [frase]
        if len(frase) > maximo * 2:  # se parte en la coma más cercana al centro
            comas = [m.end() for m in re.finditer(r",\s", frase)]
            if comas:
                corte = min(comas, key=lambda c: abs(c - len(frase) / 2))
                trozos = [frase[:corte].strip(), frase[corte:].strip()]
        pos = a
        for trozo in trozos:
            i = narr.texto.index(trozo, pos)
            j = i + len(trozo) - 1
            pos = j + 1
            lineas = [trozo]
            if len(trozo) > maximo:  # dos líneas parejas, partidas en el espacio más cercano al centro
                corte = min((m.start() for m in re.finditer(" ", trozo)), key=lambda c: abs(c - len(trozo) / 2))
                lineas = [trozo[:corte], trozo[corte + 1:]]
            resultado.append((narr.ini[i], narr.fin[j], "\n".join(lineas)))
    # cada bloque dura hasta el siguiente como mucho, y al menos 1 s
    finales = []
    for k, (a, b, t) in enumerate(resultado):
        siguiente = resultado[k + 1][0] if k + 1 < len(resultado) else b + 1.5
        finales.append((a, min(max(b + 0.25, a + 1.0), siguiente - 0.04), t))
    return finales


def srt(bloques, ruta):
    def tc(s):
        ms = round(s * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    ruta.write_text("\n".join(f"{n}\n{tc(a)} --> {tc(b)}\n{t}\n" for n, (a, b, t) in enumerate(bloques, 1)))


# ---------------------------------------------------------------- fondos

def textura(estilo, tam, semilla):
    ancho, alto = tam
    rng = np.random.default_rng(semilla)
    base = np.array(PAPEL if estilo == "papel" else NOCHE, dtype=np.float32)
    bajo = Image.fromarray((rng.random((alto // 120 + 2, ancho // 120 + 2)) * 255).astype(np.uint8))
    bajo = np.asarray(bajo.resize((ancho, alto), Image.BICUBIC), dtype=np.float32) / 255 - 0.5
    grano = rng.normal(0, 1, (alto, ancho)).astype(np.float32)
    yy, xx = np.mgrid[0:alto, 0:ancho].astype(np.float32)
    r = np.hypot((xx - ancho / 2) / (ancho / 2), (yy - alto / 2) / (alto / 2))
    if estilo == "papel":
        luz = 1 - 0.22 * np.clip(r - 0.35, 0, None) ** 1.6
        img = base[None, None] * (1 + 0.07 * bajo[..., None]) * luz[..., None] + 3.5 * grano[..., None]
    else:
        luz = 1 + 0.55 * np.clip(1 - r, 0, None) ** 2
        img = base[None, None] * (1 + 0.1 * bajo[..., None]) * luz[..., None] + 2.0 * grano[..., None]
    img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if estilo == "papel":  # fibras del papel
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(ancho * alto // 9000):
            x, y = rng.random() * ancho, rng.random() * alto
            ang, largo = rng.random() * math.pi, 6 + rng.random() * 30
            d.line([(x, y), (x + math.cos(ang) * largo, y + math.sin(ang) * largo)],
                   fill=(120, 95, 60, int(10 + rng.random() * 22)), width=1)
    return img


def marcador(plano, desc, tam):
    """Fondo provisional mientras falta la imagen del plano."""
    estilo = plano["estilo"] if plano["estilo"] in ("papel", "noche") else "papel"
    img = textura(estilo, tam, sum(map(ord, plano["id"])))
    ancho, alto = tam
    d = ImageDraw.Draw(img, "RGBA")
    tinta = TINTA if estilo == "papel" else HUESO
    m = round(alto * 0.07)
    for x in range(m, ancho - m, 40):  # marco discontinuo
        d.line([(x, m), (min(x + 22, ancho - m), m)], fill=tinta + (70,), width=3)
        d.line([(x, alto - m), (min(x + 22, ancho - m), alto - m)], fill=tinta + (70,), width=3)
    for y in range(m, alto - m, 40):
        d.line([(m, y), (m, min(y + 22, alto - m))], fill=tinta + (70,), width=3)
        d.line([(ancho - m, y), (ancho - m, min(y + 22, alto - m))], fill=tinta + (70,), width=3)
    e = alto / 1080
    textos = Image.new("RGBA", tam, (0, 0, 0, 0))  # el texto con alfa se dibuja en una capa aparte
    d = ImageDraw.Draw(textos)
    d.text((ancho / 2, alto * 0.5), plano["id"], font=fuente("anton", 420 * e), fill=tinta + (18,), anchor="mm")
    d.text((ancho / 2, alto * 0.47), desc, font=fuente("fraunces-it", 58 * e, 500), fill=tinta + (215,), anchor="mm")
    d.text((ancho / 2, alto * 0.555), f"IMAGEN PENDIENTE · {plano['id']}", font=fuente("inter", 26 * e, 600),
           fill=tinta + (160,), anchor="mm")
    return Image.alpha_composite(img.convert("RGBA"), textos).convert("RGB")


class Mapa:
    """Mapa de México a Illinois (Natural Earth, dominio público) con la flecha que se dibuja."""
    LON = (-128.0, -60.0)
    LAT_C = 30.0
    ORIGEN = (-96.68, 19.45)    # Cerro Gordo, Veracruz
    DESTINO = (-89.65, 39.80)   # Springfield, Illinois

    def __init__(self, tam):
        self.tam = tam
        ancho, alto = tam
        self.k = ancho / ((self.LON[1] - self.LON[0]) * math.cos(math.radians(self.LAT_C)))
        paises = json.loads((MAPAS / "paises_110m.geojson").read_text())["features"]
        estados = json.loads((MAPAS / "estados_110m.geojson").read_text())["features"]
        s = 2  # se dibuja al doble y se reduce, para suavizar los bordes
        grande = (ancho * s, alto * s)
        base = textura("papel", grande, 7).filter(ImageFilter.GaussianBlur(1))
        mar = Image.new("RGBA", grande, AZUL + (34,))
        base = Image.alpha_composite(base.convert("RGBA"), mar)
        d = ImageDraw.Draw(base, "RGBA")
        for f in paises:
            for anillo in self._anillos(f, s):
                d.polygon(anillo, fill=PAPEL_CLARO + (255,))
        for f in paises:
            if f["properties"]["NAME"] == "Mexico":
                for anillo in self._anillos(f, s):
                    d.polygon(anillo, fill=VERDE + (70,))
        for f in estados:
            for anillo in self._anillos(f, s):
                d.line(anillo + anillo[:1], fill=TINTA + (60,), width=2 * s)
        for f in paises:
            for anillo in self._anillos(f, s):
                d.line(anillo + anillo[:1], fill=TINTA + (230,), width=3 * s, joint="curve")
        self.base = base.resize(tam, Image.LANCZOS).convert("RGB")
        illinois = Image.new("RGBA", grande, (0, 0, 0, 0))
        di = ImageDraw.Draw(illinois)
        for f in estados:
            if f["properties"]["name"] == "Illinois":
                for anillo in self._anillos(f, s):
                    di.polygon(anillo, fill=COCHINILLA + (215,))
                    di.line(anillo + anillo[:1], fill=TINTA + (255,), width=3 * s)
        self.illinois = illinois.resize(tam, Image.LANCZOS)
        e = alto / 1080
        self.rotulo_mx = self._rotulo("MÉXICO", None, 54 * e)
        self.rotulo_il = self._rotulo("ILLINOIS", "EE. UU.", 46 * e)

    def xy(self, lon, lat, s=1):
        ancho, alto = self.tam
        lon_c = sum(self.LON) / 2
        x = ancho / 2 + (lon - lon_c) * math.cos(math.radians(self.LAT_C)) * self.k
        y = alto / 2 - (lat - self.LAT_C) * self.k
        return x * s, y * s

    def _anillos(self, f, s):
        g = f["geometry"]
        polis = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poli in polis:
            for anillo in poli:
                yield [self.xy(lon, lat, s) for lon, lat in anillo]

    def _rotulo(self, texto, sub, tam):
        f = fuente("fraunces", tam, 700)
        fs = fuente("inter", tam * 0.5, 700)
        w = max(f.getlength(texto), fs.getlength(sub) if sub else 0) + tam
        capa = Image.new("RGBA", (round(w), round(tam * (2.1 if sub else 1.5))), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        d.text((capa.width / 2, tam * 0.72), texto, font=f, fill=TINTA, anchor="mm",
               stroke_width=max(2, round(tam / 12)), stroke_fill=PAPEL_CLARO)
        if sub:
            d.text((capa.width / 2, tam * 1.6), sub, font=fs, fill=COCHINILLA, anchor="mm")
        return capa

    def fotograma(self, t):
        img = self.base.copy()
        p = salida((t - 0.08) / 0.85)
        llegada = suave((t - 0.75) / 0.3)
        if llegada > 0:
            img.paste(self.illinois, (0, 0), con_alfa(self.illinois, llegada))
        e = self.tam[1] / 1080
        x0, y0 = self.xy(*self.ORIGEN)
        x1, y1 = self.xy(*self.DESTINO)
        cx, cy = (x0 + x1) / 2 + 260 * e, (y0 + y1) / 2 + 40 * e  # curva hacia el golfo
        u = np.linspace(0, 1, 400)
        px = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1
        py = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1
        largo = np.concatenate([[0], np.cumsum(np.hypot(np.diff(px), np.diff(py)))])
        en = lambda s: (float(np.interp(s, largo, px)), float(np.interp(s, largo, py)))  # noqa: E731
        d = ImageDraw.Draw(img)
        r = 13 * e
        d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=COCHINILLA, outline=TINTA, width=max(2, round(3 * e)))
        hasta = largo[-1] * p
        trazo, hueco = 30 * e, 18 * e
        for a in np.arange(0, hasta, trazo + hueco):  # trazo discontinuo medido sobre la curva
            b = min(a + trazo, hasta)
            d.line([en(v) for v in np.linspace(a, b, 8)], fill=COCHINILLA, width=round(9 * e), joint="curve")
        if p > 0.05:
            (ax, ay), (bx, by) = en(max(0.0, hasta - 10 * e)), en(hasta)
            ang = math.atan2(by - ay, bx - ax)
            punta = 34 * e
            d.polygon([(bx + math.cos(ang) * punta * 0.6, by + math.sin(ang) * punta * 0.6),
                       (bx + math.cos(ang + 2.5) * punta, by + math.sin(ang + 2.5) * punta),
                       (bx + math.cos(ang - 2.5) * punta, by + math.sin(ang - 2.5) * punta)], fill=COCHINILLA)
        mx, my = self.xy(-102.5, 24.0)
        pegar(img, self.rotulo_mx, mx, my, suave(t / 0.25))
        ix, iy = self.xy(-89.2, 40.0)
        pegar(img, self.rotulo_il, ix + self.rotulo_il.width / 2 + 60 * e, iy, llegada)
        return img


# ---------------------------------------------------------------- rótulos

def capa_grito(el, e):
    f = fuente("anton", el["tam"] * e)
    trazo = max(3, round(el["tam"] * e / 18))
    ancho_max = el["ancho"] * 1920 * e
    palabras, lineas = el["texto"].split(), [[]]
    for p in palabras:
        prueba = " ".join(lineas[-1] + [p])
        if lineas[-1] and f.getlength(prueba) > ancho_max:
            lineas.append([p])
        else:
            lineas[-1].append(p)
    alto_linea = el["tam"] * e * 1.08
    w = max(f.getlength(" ".join(l)) for l in lineas) + trazo * 4
    capa = Image.new("RGBA", (round(w), round(alto_linea * len(lineas) + trazo * 4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    acento = (el.get("acento") or "").split()
    for n, linea in enumerate(lineas):
        x = (capa.width - f.getlength(" ".join(linea))) / 2
        y = trazo * 2 + n * alto_linea
        for p in linea:
            color = COCHINILLA if p in acento else HUESO
            d.text((x, y), p, font=f, fill=color, stroke_width=trazo, stroke_fill=TINTA)
            x += f.getlength(p + " ")
    return sombra(capa, round(10 * e), round(8 * e))


def capa_fecha(el, e):
    tam = el["tam"] * e
    partes = el["texto"].split(" · ")
    f = fuente("fraunces", tam, 650)
    sep = "  ·  "
    w = f.getlength(sep.join(partes))
    pad = tam * 0.55
    capa = Image.new("RGBA", (round(w + pad * 2), round(tam * 1.75)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle([0, 0, capa.width - 1, capa.height - 1], radius=round(tam * 0.18), fill=NOCHE + (225,))
    d.line([(pad, capa.height - tam * 0.32), (capa.width - pad, capa.height - tam * 0.32)], fill=ORO + (200,),
           width=max(2, round(tam / 26)))
    x, y = pad, capa.height * 0.44
    for n, parte in enumerate(partes):
        if n:
            d.text((x, y), sep, font=f, fill=HUESO, anchor="lm")
            x += f.getlength(sep)
        d.text((x, y), parte, font=f, fill=ORO if n == 0 else HUESO, anchor="lm")
        x += f.getlength(parte)
    return sombra(capa, round(12 * e), round(6 * e), 0.45)


def capa_etiqueta(el, e):
    tam = 72 * e
    f = fuente("anton", tam)
    w = f.getlength(el["texto"])
    barra = tam * 0.22
    capa = Image.new("RGBA", (round(w + tam * 1.2 + barra), round(tam * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rectangle([0, 0, capa.width, capa.height], fill=TINTA + (240,))
    d.rectangle([0, 0, barra, capa.height], fill=COCHINILLA)
    d.text((barra + tam * 0.6, capa.height / 2), el["texto"], font=f, fill=HUESO, anchor="lm")
    return sombra(capa, round(10 * e), round(6 * e), 0.4)


def capa_nombre(el, e):
    tam = 60 * e
    f = fuente("fraunces", tam, 750)
    w = f.getlength(el["texto"])
    barra = tam * 0.2
    capa = Image.new("RGBA", (round(w + tam * 1.3 + barra), round(tam * 1.7)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rectangle([0, 0, capa.width, capa.height], fill=PAPEL_CLARO + (250,))
    d.rectangle([0, 0, barra, capa.height], fill=COCHINILLA)
    d.text((barra + tam * 0.6, capa.height / 2), el["texto"], font=f, fill=TINTA, anchor="lm")
    return sombra(capa, round(12 * e), round(6 * e), 0.5)


def capa_tarjeta(el, e):
    tam = 54 * e
    f = fuente("fraunces", tam, 650)
    texto, acento = el["texto"], el.get("acento")
    w = f.getlength(texto)
    capa = Image.new("RGBA", (round(w + tam * 1.2), round(tam * 1.75)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rectangle([0, 0, capa.width - 1, capa.height - 1], fill=PAPEL_CLARO + (252,), outline=TINTA,
                width=max(2, round(3 * e)))
    x = tam * 0.6
    for p in texto.split(" "):
        d.text((x, capa.height / 2), p, font=f, fill=COCHINILLA if p == acento else TINTA, anchor="lm")
        x += f.getlength(p + " ")
    return sombra(capa, round(10 * e), round(7 * e), 0.5)


def capa_sello(el, e):
    tam = el["tam"] * e
    f = fuente("anton", tam)
    lineas = el["texto"].split("\n")
    w = max(f.getlength(l) for l in lineas)
    borde = max(4, round(tam / 14))
    pad = tam * 0.38
    alto = tam * 1.12 * len(lineas) + pad * 1.2
    capa = Image.new("RGBA", (round(w + pad * 2), round(alto)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    color = el["color"]
    d.rounded_rectangle([borde, borde, capa.width - borde, capa.height - borde], radius=round(tam * 0.12),
                        outline=color, width=borde)
    d.rounded_rectangle([borde * 3, borde * 3, capa.width - borde * 3, capa.height - borde * 3],
                        radius=round(tam * 0.08), outline=color, width=max(2, borde // 2))
    for n, l in enumerate(lineas):
        d.text((capa.width / 2, pad * 0.6 + tam * 1.12 * (n + 0.5) + borde), l, font=f, fill=color, anchor="mm")
    # tinta irregular, como un sello de goma
    rng = np.random.default_rng(len(el["texto"]) * 31)
    ruido = Image.fromarray((rng.random((capa.height // 6 + 1, capa.width // 6 + 1)) * 255).astype(np.uint8))
    ruido = np.asarray(ruido.resize(capa.size, Image.BICUBIC), dtype=np.float32) / 255
    fino = rng.random((capa.height, capa.width))
    mascara = np.clip((ruido * 0.6 + fino * 0.4 - 0.18) * 3.0, 0.35, 1.0)
    a = np.asarray(capa.getchannel("A"), dtype=np.float32) * mascara * 0.92
    capa.putalpha(Image.fromarray(a.astype(np.uint8)))
    return capa.rotate(el["giro"], resample=Image.BICUBIC, expand=True)


def capa_capitulo(el, e):
    tam_n, tam_t = 190 * e, 104 * e
    fn, ft = fuente("anton", tam_n), fuente("anton", tam_t)
    trazo = max(3, round(tam_t / 17))
    num = el["numero"]
    wn, wt = fn.getlength(num), ft.getlength(el["titulo"])
    extra_w = 0
    if el.get("extra"):
        fe = fuente("fraunces", 70 * e, 700)
        extra_w = fe.getlength(el["extra"]) + 70 * e * 1.3
    hueco = tam_t * 0.35
    capa = Image.new("RGBA", (round(wn + hueco + max(wt, extra_w) + trazo * 4), round(tam_n * 1.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.text((trazo * 2, capa.height / 2), num, font=fn, fill=COCHINILLA, anchor="lm", stroke_width=trazo,
           stroke_fill=TINTA)
    x = trazo * 2 + wn + hueco
    alto_t = capa.height / 2 - (tam_t * 0.42 if el.get("extra") else 0)
    d.text((x, alto_t), el["titulo"], font=ft, fill=HUESO, anchor="lm", stroke_width=trazo, stroke_fill=TINTA)
    numero = sombra(capa, round(10 * e), round(8 * e))
    margen = round(10 * e) * 2 + round(8 * e) * 2  # el que añade sombra()
    extra = None
    if el.get("extra"):
        extra = capa_fecha(dict(texto=el["extra"], tam=62), e)
    return numero, extra, (x + margen, alto_t + margen)


def capa_expediente(el, e):
    tam = 92 * e
    f = fuente("fraunces", tam, 850)
    fa = fuente("inter", 26 * e, 700)
    arriba = " ".join(el["arriba"])  # espaciado de letras
    w = max(f.getlength(el["principal"]), fa.getlength(arriba)) + tam * 1.1
    pestana_w, pestana_h = w * 0.36, tam * 0.42
    capa = Image.new("RGBA", (round(w), round(tam * 2.15 + pestana_h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    carpeta = (222, 196, 140)
    d.rounded_rectangle([0, 0, pestana_w, pestana_h * 2], radius=round(tam * 0.12), fill=carpeta)
    d.rounded_rectangle([0, pestana_h, capa.width - 1, capa.height - 1], radius=round(tam * 0.1), fill=carpeta,
                        outline=(176, 146, 88), width=max(2, round(3 * e)))
    d.text((tam * 0.55, pestana_h + tam * 0.5), arriba, font=fa, fill=COCHINILLA, anchor="lm")
    d.text((tam * 0.55, pestana_h + tam * 1.35), el["principal"], font=f, fill=TINTA, anchor="lm")
    return sombra(capa, round(14 * e), round(9 * e), 0.5)


class Rotulo:
    """Un texto en pantalla ya dibujado, con su animación de entrada."""

    def __init__(self, el, e, ancho, alto):
        self.el, self.t = el, el["t"]
        self.ancho, self.alto, self.e = ancho, alto, e
        tipo = el["tipo"]
        self.extra = None
        if tipo == "capitulo":
            self.capa, self.extra, self.pos_titulo = capa_capitulo(el, e)
        else:
            self.capa = {"grito": capa_grito, "fecha": capa_fecha, "etiqueta": capa_etiqueta, "nombre": capa_nombre,
                         "tarjeta": capa_tarjeta, "sello": capa_sello, "expediente": capa_expediente}[tipo](el, e)
        x, y = el["pos"]
        if tipo == "nombre":  # pos es la esquina izquierda
            self.cx, self.cy = x * ancho + self.capa.width / 2, y * alto
        else:
            self.cx, self.cy = x * ancho, y * alto

    def componer(self, img, t):
        u = t - self.t
        if u < 0:
            return
        tipo, e = self.el["tipo"], self.e
        if tipo == "grito":
            pegar(img, self.capa, self.cx, self.cy, salida(u / 0.12), 1.18 - 0.18 * rebote(u / 0.22))
        elif tipo in ("fecha", "tarjeta"):
            pegar(img, self.capa, self.cx, self.cy + 26 * e * (1 - salida(u / 0.35)), salida(u / 0.3))
        elif tipo in ("etiqueta", "nombre"):
            p = salida(u / 0.35)
            recorte = self.capa.crop((0, 0, max(1, round(self.capa.width * p)), self.capa.height))
            img.paste(recorte, (round(self.cx - self.capa.width / 2), round(self.cy - self.capa.height / 2)), recorte)
        elif tipo == "sello":
            p = u / 0.11
            pegar(img, self.capa, self.cx, self.cy, min(1.0, p * 1.4), 1.0 + 1.1 * (1 - salida(p)) if p < 1 else 1.0)
        elif tipo == "capitulo":
            pegar(img, self.capa, self.cx, self.cy, salida(u / 0.15), 1.12 - 0.12 * rebote(u / 0.25))
            if self.extra is not None:
                v = u - 0.45
                if v > 0:
                    x = self.cx - self.capa.width / 2 + self.pos_titulo[0] + self.extra.width / 2 - 10 * e
                    y = self.cy + 62 * e
                    pegar(img, self.extra, x, y + 20 * e * (1 - salida(v / 0.3)), salida(v / 0.25))
        elif tipo == "expediente":
            pegar(img, self.capa, self.cx, self.cy - 40 * e * (1 - salida(u / 0.4)), salida(u / 0.3))


# ---------------------------------------------------------------- render de cada plano

def camara(movimiento, foco):
    for clave, valores in CAMARAS:
        if clave in movimiento:
            z0, z1, px, py, sac = valores
            break
    else:
        z0, z1, px, py, sac = 1.0, 1.08, None, None, 0
    return dict(z0=z0, z1=z1, px=px or (foco[0], foco[0]), py=py or (foco[1], foco[1]), sacudida=sac)


def sacudir(t, golpes, e):
    dx = dy = 0.0
    for t0, amp in golpes:
        u = t - t0
        if 0 <= u < 0.6:
            a = amp * e * math.exp(-u / 0.12)
            dx += a * math.sin(2 * math.pi * 17 * u)
            dy += a * math.cos(2 * math.pi * 13 * u + 0.7)
    return dx, dy


def encuadre(fuente_img, cam, u, desplaz, ancho, alto):
    sw, sh = fuente_img.size
    z = cam["z0"] + (cam["z1"] - cam["z0"]) * (0.5 * u + 0.5 * suave(u))
    cx = cam["px"][0] + (cam["px"][1] - cam["px"][0]) * suave(u)
    cy = cam["py"][0] + (cam["py"][1] - cam["py"][0]) * suave(u)
    # el recorte mantiene 16:9 aunque la imagen no lo sea del todo
    base_w = min(sw, sh * ancho / alto)
    w = base_w / z
    h = w * alto / ancho
    x0 = min(max(cx * sw - w / 2, 0), sw - w) + desplaz[0] * w / ancho
    y0 = min(max(cy * sh - h / 2, 0), sh - h) + desplaz[1] * h / alto
    x0 = min(max(x0, 0), sw - w)
    y0 = min(max(y0, 0), sh - h)
    return fuente_img.resize((ancho, alto), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def render_plano(tarea):
    ancho, alto = tarea["ancho"], tarea["alto"]
    e = alto / 1080
    tam_fuente = (round(ancho * 1.25), round(alto * 1.25))
    mapa = None
    if tarea.get("mapa"):
        mapa = Mapa(tam_fuente)
        fondo = None
    elif tarea["imagen"]:
        fondo = Image.open(tarea["imagen"]).convert("RGB")
    else:
        fondo = marcador(tarea["plano"], tarea["desc"], tam_fuente)
    rotulos = [Rotulo(el, e, ancho, alto) for el in tarea["textos"]]
    subt = [(a, b, capa_subtitulo(t, e)) for a, b, t in tarea["subtitulos"]]
    aviso = capa_aviso(tarea["aviso"], e) if tarea["aviso"] else None
    golpes = tarea["golpes"]
    if tarea["cam"]["sacudida"]:
        golpes = golpes + [(tarea["t0"], tarea["cam"]["sacudida"])]
    n = tarea["fotogramas"]
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ancho}x{alto}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", tarea["preset"], "-crf", "18", "-threads", "2",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(tarea["salida"])],
        stdin=subprocess.PIPE)
    muestra = None
    for k in range(n):
        t = tarea["t0"] + k / FPS
        u = k / max(1, n - 1)
        origen = mapa.fotograma(t - tarea["t0"]) if mapa else fondo
        img = encuadre(origen, tarea["cam"], u, sacudir(t, golpes, e), ancho, alto)
        for r in rotulos:
            r.componer(img, t)
        for a, b, capa in subt:
            if a <= t < b:
                pegar(img, capa, ancho / 2, alto - capa.height / 2 - 36 * e)
        if aviso is not None:
            img.paste(aviso, (round(ancho - aviso.width - 28 * e), round(28 * e)), aviso)
        fundido = min(1.0, (t + 0.0001) / 0.4, (tarea["total"] - t) / 0.6)
        if fundido < 1:
            img = Image.blend(Image.new("RGB", img.size, (0, 0, 0)), img, max(0.0, fundido))
        if k == round(n * 0.8):
            muestra = img
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg falló en {tarea['plano']['id']}")
    if tarea["muestras"] and muestra is not None:
        muestra.save(TRABAJO / "muestras" / f"{tarea['plano']['id']}.jpg", quality=88)
    return tarea["plano"]["id"]


def capa_subtitulo(texto, e):
    f = fuente("inter", 40 * e, 600)
    lineas = texto.split("\n")
    w = max(f.getlength(l) for l in lineas) + 48 * e
    h = len(lineas) * 52 * e + 28 * e
    capa = Image.new("RGBA", (round(w), round(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle([0, 0, capa.width - 1, capa.height - 1], radius=round(10 * e), fill=(10, 10, 14, 185))
    for n, l in enumerate(lineas):
        d.text((capa.width / 2, 14 * e + 52 * e * (n + 0.5)), l, font=f, fill=(255, 255, 255), anchor="mm")
    return capa


def capa_aviso(texto, e):
    f = fuente("inter", 22 * e, 700)
    capa = Image.new("RGBA", (round(f.getlength(texto) + 36 * e), round(44 * e)), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle([0, 0, capa.width - 1, capa.height - 1], radius=round(8 * e), fill=COCHINILLA + (230,))
    d.text((capa.width / 2, capa.height / 2), texto, font=f, fill=HUESO, anchor="mm")
    return capa


# ---------------------------------------------------------------- sonido

def filtrar(x, bajo=None, alto=None):
    """Filtro pasa banda suave por FFT (bajo y alto en Hz)."""
    espectro = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if bajo:
        g *= 1 / np.sqrt(1 + (bajo / np.maximum(f, 1)) ** 4)
    if alto:
        g *= 1 / np.sqrt(1 + (f / alto) ** 4)
    return np.fft.irfft(espectro * g, len(x))


def normalizar(x, pico=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * pico


def sonido(nombre, rng):
    t = lambda d: np.arange(int(d * SR)) / SR  # noqa: E731
    if nombre == "canon":
        s = t(2.2)
        ruido = filtrar(rng.normal(0, 1, len(s)), alto=500) * np.exp(-s / 0.35)
        grave = np.sin(2 * np.pi * (58 * s - 9 * s ** 2)) * np.exp(-s / 0.5)
        chasquido = filtrar(rng.normal(0, 1, len(s)), bajo=800) * np.exp(-s / 0.012)
        cola = filtrar(rng.normal(0, 1, len(s)), alto=180) * np.exp(-s / 0.9) * 0.5
        return normalizar(ruido * 1.2 + grave * 0.9 + chasquido * 0.35 + cola)
    if nombre == "golpe":
        s = t(0.5)
        golpe = np.sin(2 * np.pi * (95 * s - 40 * s ** 2)) * np.exp(-s / 0.07)
        madera = filtrar(rng.normal(0, 1, len(s)), bajo=300, alto=2500) * np.exp(-s / 0.025)
        return normalizar(golpe + madera * 0.7)
    if nombre == "impacto":
        s = t(1.6)
        grave = np.sin(2 * np.pi * 46 * s) * np.exp(-s / 0.45)
        cuerpo = filtrar(rng.normal(0, 1, len(s)), alto=260) * np.exp(-s / 0.25)
        return normalizar(grave + cuerpo * 0.8)
    if nombre == "whoosh":
        s = t(0.9)
        env = np.sin(np.pi * np.clip(s / 0.9, 0, 1)) ** 2
        ruido = rng.normal(0, 1, len(s))
        grave, agudo = filtrar(ruido, bajo=200, alto=900), filtrar(ruido, bajo=1500, alto=5000)
        m = np.sin(np.pi * s / 0.9)  # el brillo sube y baja
        return normalizar((grave * (1 - m) + agudo * m * 1.6) * env)
    if nombre == "tambor":
        s = t(2.6)
        y = np.zeros(len(s))
        for golpe_t, fuerza in [(0, 1), (0.36, 0.7), (0.54, 0.6), (0.72, 1), (1.08, 0.7), (1.26, 0.6), (1.44, 1),
                                (1.8, 0.7), (1.98, 0.6), (2.16, 1)]:
            i = int(golpe_t * SR)
            d = len(s) - i
            u = np.arange(d) / SR
            parche = filtrar(rng.normal(0, 1, d), bajo=1200) * np.exp(-u / 0.06)
            cuerpo = np.sin(2 * np.pi * 190 * u) * np.exp(-u / 0.04)
            y[i:] += fuerza * (parche * 0.8 + cuerpo * 0.6)
        return normalizar(y) * np.clip((2.6 - s) / 0.5, 0, 1)
    if nombre == "campana":
        s = t(5.0)
        f0 = 196.0
        y = sum(a * np.sin(2 * np.pi * f0 * r * s) * np.exp(-s / d)
                for r, a, d in [(0.5, 0.6, 3.5), (1.0, 1.0, 2.6), (1.19, 0.5, 2.0), (1.5, 0.35, 1.6),
                                (2.0, 0.45, 1.3), (2.51, 0.25, 0.9), (3.0, 0.2, 0.7)])
        ataque = filtrar(rng.normal(0, 1, len(s)), bajo=1500) * np.exp(-s / 0.01) * 0.3
        return normalizar(y + ataque)
    if nombre == "pluma":
        s = t(1.8)
        y = np.zeros(len(s))
        for _ in range(7):
            i = int(rng.random() * 1.4 * SR)
            d = int((0.08 + rng.random() * 0.18) * SR)
            u = np.arange(d) / d
            y[i:i + d] += filtrar(rng.normal(0, 1, d), bajo=2500, alto=8000) * np.sin(np.pi * u) * (0.5 + rng.random())
        return normalizar(y)
    if nombre == "papel":
        s = t(0.8)
        chispas = (rng.random(len(s)) > 0.996) * rng.normal(0, 1, len(s))
        y = filtrar(chispas * 6 + rng.normal(0, 0.25, len(s)), bajo=1800, alto=7000)
        return normalizar(y * np.exp(-s / 0.35))
    raise ValueError(nombre)


def leer_audio(ruta, canales=1):
    datos = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(ruta), "-f", "f32le", "-ac", str(canales),
                            "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(datos, dtype=np.float32)
    return x.reshape(-1, canales) if canales > 1 else x


def mezclar(total, eventos, con_voz, ruta):
    n = int(total * SR) + SR
    mezcla = np.zeros((n, 2), dtype=np.float32)
    rng = np.random.default_rng(1842)
    # ambiente de época muy bajo: rumor grave
    ambiente = filtrar(rng.normal(0, 1, n), bajo=40, alto=320)
    mezcla += (normalizar(ambiente) * 0.035)[:, None]
    voz_env = np.zeros(n)
    if con_voz:
        voz = leer_audio(MP3)
        i = int(PREVIO * SR)
        voz = voz[: n - i]
        mezcla[i:i + len(voz)] += voz[:, None] * 0.95
        env = np.abs(voz)
        k = int(0.3 * SR)
        env = np.convolve(env, np.ones(k) / k, mode="same")
        voz_env[i:i + len(env)] = env
    cache = {}
    for nombre_sfx, t0, ganancia in eventos:
        if nombre_sfx not in cache:
            cache[nombre_sfx] = sonido(nombre_sfx, rng).astype(np.float32)
        s = cache[nombre_sfx]
        i = int(t0 * SR)
        s = s[: max(0, n - i)]
        mezcla[i:i + len(s)] += s[:, None] * ganancia * (0.55 if con_voz else 0.8)
    if MUSICA.exists():
        musica = leer_audio(MUSICA, 2)[:n]
        g = 0.32 - 0.22 * np.clip(voz_env[: len(musica)] / 0.04, 0, 1)
        mezcla[: len(musica)] += musica * g[:, None]
    fin = np.clip((total - np.arange(n) / SR) / 0.6, 0, 1)
    mezcla *= fin[:, None]
    mezcla = np.tanh(mezcla * 1.1) / math.tanh(1.1)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mezcla, -1, 1) * 32767).astype(np.int16).tobytes())


def sonoridad(entrada, salida_mp4, video):
    """Normaliza a -14 LUFS (referencia de YouTube) en dos pasadas y une audio y video."""
    medida = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(entrada), "-af",
                             "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
    m = json.loads(medida[medida.rindex("{"):])
    filtro = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(video),
                    "-i", str(entrada), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", filtro, "-ar", str(SR),
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(salida_mp4)], check=True)


# ---------------------------------------------------------------- principal

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--borrador", action="store_true", help="960×540 y codificación rápida")
    parser.add_argument("--muestras", action="store_true", help="guardar un fotograma de cada plano")
    args = parser.parse_args()

    asegurar_recursos()
    ancho, alto = (960, 540) if args.borrador else (1920, 1080)
    TRABAJO.mkdir(parents=True, exist_ok=True)
    (TRABAJO / "segmentos").mkdir(exist_ok=True)
    if args.muestras:
        (TRABAJO / "muestras").mkdir(exist_ok=True)

    con_voz = MP3.exists() and TIEMPOS.exists()
    datos = json.loads(TIEMPOS.read_text()) if con_voz else estimar_tiempos(texto_parte(1))
    narr = Narracion(datos)
    planos = [p for p in json.loads((VIDEO / "planos_piloto.json").read_text()) if p["id"] != "REF"]

    inicios, desde = [], 0
    for p in planos:
        i = narr.buscar(p["frase"], desde)
        inicios.append(i)
        desde = i + 1
    total = narr.final + COLA
    cortes = [0.0] + [max(0.0, narr.ini[i] - ADELANTO) for i in inicios[1:]] + [total]
    marcos = [round(c * FPS) for c in cortes]

    faltan = [p["id"] for p in planos if p["archivo"] and not (RAIZ / p["archivo"]).exists()]
    aviso = None
    if not con_voz or faltan:
        partes = (["SIN VOZ"] if not con_voz else []) + (["IMÁGENES PENDIENTES"] if faltan else [])
        aviso = "ANIMÁTICA · " + " · ".join(partes)
    bloques = subtitulos(narr)
    srt(bloques, TRABAJO / "piloto.srt")

    tareas, eventos = [], []
    for n, p in enumerate(planos):
        ed = EDICION.get(p["id"], {})
        t0 = marcos[n] / FPS
        i_ini, i_fin = inicios[n], inicios[n + 1] if n + 1 < len(inicios) else len(narr.texto)

        def momento(ancla, base=t0):
            if ancla is None:
                return base + 0.25
            if isinstance(ancla, (int, float)):
                return t0 + ancla
            return narr.ini[narr.palabra(ancla, i_ini, i_fin)]

        textos, golpes = [], []
        for el in ed.get("textos", []):
            el = dict(el, t=momento(el["en"]) + el.get("retraso", 0.0))
            if el["tipo"] == "sello":
                aterriza = el["t"] + 0.11
                golpes.append((aterriza, 16))
                eventos.append(("golpe", aterriza - 0.02, 0.9))
            textos.append(el)
        for nombre_sfx, ancla, ganancia in ed.get("sfx", []):
            t_sfx = momento(ancla) if isinstance(ancla, str) else t0 + ancla
            eventos.append((nombre_sfx, t_sfx, ganancia))
            if nombre_sfx == "canon":
                golpes.append((t_sfx + 0.02, 12))
        imagen = RAIZ / p["archivo"] if p["archivo"] and (RAIZ / p["archivo"]).exists() else None
        tareas.append(dict(
            plano=p, desc=ed.get("desc", p["frase"]), imagen=imagen, mapa=ed.get("mapa", False),
            cam=camara(p["movimiento"], ed.get("foco", (0.5, 0.5))), textos=textos, golpes=golpes,
            t0=t0, fotogramas=marcos[n + 1] - marcos[n], total=total, ancho=ancho, alto=alto,
            subtitulos=[b for b in bloques if b[1] > t0 and b[0] < marcos[n + 1] / FPS] if not con_voz else [],
            aviso=aviso, preset="veryfast" if args.borrador else "medium", muestras=args.muestras,
            salida=TRABAJO / "segmentos" / f"{n:02d}_{p['id']}.mp4"))

    print(f"{len(planos)} planos · {total:.1f} s · {'voz real' if con_voz else 'tiempos estimados'} · "
          f"{len(planos) - len(faltan)} imágenes y {len(faltan)} marcadores · {ancho}×{alto}")
    with Pool(4) as pool:
        for hecho in pool.imap_unordered(render_plano, tareas):
            print("  plano", hecho, flush=True)

    lista = TRABAJO / "segmentos" / "lista.txt"
    lista.write_text("".join(f"file '{t['salida'].name}'\n" for t in tareas))
    mezcla = TRABAJO / "mezcla.wav"
    mezclar(total, eventos, con_voz, mezcla)
    destino = TRABAJO / ("piloto_borrador.mp4" if args.borrador else "piloto.mp4")
    if con_voz:
        sonoridad(mezcla, destino, lista)
    else:  # sin voz no tiene sentido llevar el ambiente a -14 LUFS
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
                        "-i", str(mezcla), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", str(destino)], check=True)
    shutil.rmtree(TRABAJO / "segmentos")
    print("Listo:", destino.relative_to(RAIZ), "y", (TRABAJO / "piloto.srt").relative_to(RAIZ))


if __name__ == "__main__":
    main()
