"""Guion del short «La llave del Titanic» (vertical).

Cada frase: (texto hablado, sección, énfasis, voz). Todo lo dice el narrador (Charon) en UNA sola toma, como en el short
de Napoleón: él mismo actúa las citas (la pregunta de la audiencia, la respuesta del vigía, la carta del oficial).
Los números van escritos como se dicen; en los subtítulos se ven en cifras (VISIBLE).
Pausas marcadas: después de «Titanic…», «prisa…», «Quedan unos…», antes de «No.» y antes de «era el único…».
"""

M = "muletilla"

GUION = [
    # gancho
    ("Una llave pudo salvar el Titanic...", 0, False, ""),
    ("y se fue en el bolsillo de un oficial.", 0, False, ""),
    # origen
    ("Justo antes de zarpar, a uno de los oficiales del Titanic lo dejan en tierra.", 0, False, ""),
    # primer escalón
    ("Se va con prisa...", 0, False, ""),
    ("y se lleva la llave del armario de los prismáticos.", 0, False, ""),
    ("Los vigías tendrán que mirar el mar a ojo.", 0, False, ""),
    # segundo escalón
    ("Catorce de abril, once y cuarenta de la noche: el vigía ve el iceberg.", 0, False, ""),
    ("Quedan unos...", 0, False, ""),
    ("¡treinta y siete segundos!", 0, False, ""),
    ("Después le preguntan:", 0, False, ""),
    ("«¿Con prismáticos, cuánto antes lo habría visto?»", 0, False, ""),
    ("«Lo suficiente para esquivarlo».", 0, False, ""),
    # clímax
    ("Pero los oficiales del puente sí tenían prismáticos.", 0, False, ""),
    ("¿Y por qué no lo vieron?", 0, False, ""),
    ("Noche sin luna.", 0, False, ""),
    ("Mar como un espejo.", 0, False, ""),
    ("Ni una gota de espuma alrededor del hielo.", 0, False, ""),
    ("¿Y avisos de hielo?", 0, False, ""),
    ("¡Seis ese mismo día!", 0, False, ""),
    ("¿Y frenaron?", 0, False, ""),
    ("No.", 0, True, ""),
    # golpe extra
    ("Para colmo, el oficial de la llave había escrito:", 0, False, ""),
    ("«Qué pena no hacer su primer viaje».", 0, False, ""),
    ("Esa pena le salvó la vida.", 0, False, ""),
    # cierre
    ("El único que tenía la llave...", 0, False, ""),
    ("era el único que no iba en el barco.", 0, False, ""),
    ("Veredicto: medio mito.", 0, True, ""),
]


def buscar(inicio, desde=0):
    for i in range(desde, len(GUION)):
        if GUION[i][0].startswith(inicio):
            return i
    raise ValueError(inicio)


CAPITULOS = ["Titanic"]
SERIAS = set()
OBJETIVO_PPM = 175.0
TEMPO_FRASE = {}
HABLADAS = {}

# Voz natural (como Napoleón): la toma queda continua (scripts/montar_natural.py). Pausas en silencio real y en tiempo
# final: las marcadas quedan exactas; las demás solo se acortan hasta estos topes (se conserva la variación natural).
PAUSA_NORMAL = 0.28
PAUSA_INTERNA_MAX = 0.26
SIN_RESPIRACIONES = True
REFUERZO_FINAL = 1.1
PAUSAS = {
    buscar("Una llave pudo"): 0.32,       # «...el Titanic…» → «y se fue»
    buscar("Se va con prisa"): 0.28,      # «prisa…» → «y se lleva la llave»
    buscar("Quedan unos"): 0.38,          # suspenso antes de «¡treinta y siete segundos!»
    buscar("¿Y frenaron?"): 0.75,         # [pausa] → «No.»
    buscar("El único que tenía"): 0.70,   # [pausa] → «era el único que no iba en el barco»
    buscar("era el único"): 0.40,         # → «Veredicto: medio mito.»
}
SILENCIO_INTERNO = (0.30, 0.22)
SILENCIO_FRASE = {}

VOCES_EXTRA = {}
AJUSTE_CITAS = {}
ESTILO_MULETILLA = ""

VISIBLE = {
    ("catorce",): "14",
    ("once", "y", "cuarenta"): "11:40",
    ("treinta", "y", "siete"): "¡37",
}
ENFASIS_PALABRAS = set()

# Dirección de la toma única (scripts/voz_una_toma.py)
ESTILO_TOMA = (
    "Cuenta esto como un amigo que te revela un dato increíble de historia: intrigante, cercano y muy expresivo, con "
    "muchas subidas y bajadas de entonación y énfasis claro en los momentos clave; nunca de documental. Es una tragedia "
    "real: nada de burla cuando hablas del choque. Eres un narrador masculino latinoamericano (español neutro, con seseo) "
    "que cuenta historias en redes sociales: voz narrativa, cálida y envolvente. Ritmo ágil de video corto (unas 185 palabras por minuto), frases "
    "encadenadas y sin respiraciones audibles, pero natural, sin atropellarte. Cuando hay una cita, tú mismo cambias la "
    "voz para actuarla. Pronuncia 'Titanic' a la española (Titánic)."
)
DIRECCION = [
    "arranca con intriga, como quien revela un secreto; micro pausa después de 'Titanic'",
    "remata con ironía, casi sonriendo",
    "narrativo y ágil; 'lo dejan en tierra' con un poco de sorpresa",
    "rápido, con prisa",
    "pícaro, acentúa 'la llave' y 'prismáticos'",
    "con un dejo de gravedad: 'a ojo'",
    "baja la voz, tenso y concreto, como un parte de guardia",
    "suspenso, alarga 'unos...'",
    "MOMENTO CLAVE: sorpresa fuerte, casi exclamado",
    "neutral, preparando la cita",
    "ACTÚA a un senador de 1912: formal y serio",
    "ACTÚA al vigía: sencillo, firme y un poco amargo",
    "giro: 'Pero' marcado; acentúa 'sí tenían'",
    "pregunta intrigada, sube al final",
    "corto y grave",
    "corto, con asombro",
    "pausado, como describiendo una foto",
    "pregunta rápida",
    "MOMENTO CLAVE: incredulidad, acentúa 'Seis'",
    "pregunta lenta, con suspenso; después, un silencio",
    "MOMENTO CLAVE: seco y rotundo, una sola palabra",
    "'Para colmo' con picardía; preparando la cita",
    "ACTÚA al oficial escribiendo una carta: decepcionado, con nostalgia",
    "revelación con ironía suave; acentúa 'salvó'",
    "lento y misterioso; deja la frase en el aire",
    "remate con media sonrisa, acentúa 'el único'",
    "veredicto claro y firme: 'medio mito' con énfasis",
]
assert len(DIRECCION) == len(GUION)

INDICACIONES = ESTILO_TOMA
NARRADOR = ""
PRONUNCIACION = "Pronuncia 'Titanic' a la española (Titánic)."
