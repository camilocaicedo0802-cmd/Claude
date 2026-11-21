"""Guion del short «Roswell: el ovni que era un globo espía» (vertical).

Cada frase: (texto hablado, sección, énfasis, voz). Voz "" = narrador (Charon); "general" y "militar" = citas.
«Róswel» va escrito como se pronuncia (en los subtítulos se ve «Roswell»).
Ritmo de chisme, 195–205 palabras por minuto, con un punto misterioso en el gancho.
Una sola pausa: 0,5 s antes de «Pero no era un ovni». La última frase, un poco más lenta.
"""

M = "muletilla"

GUION = [
    # 0 · escena imposible
    ("El ejército de Estados Unidos anunció que había capturado un ovni... y horas después lo negó.", 0, False, ""),
    # 1 · mira
    ("En 1947, un granjero de Róswel encuentra en su rancho unos restos rarísimos: goma, papel de aluminio, palitos.", 0, False, ""),
    ("Y la base militar del pueblo anuncia: «Capturamos un platillo volador».", 0, False, ""),
    # 2 · la burla
    ("Pero esa misma tarde, un general muestra los restos a la prensa:", 0, False, ""),
    ("Es un globo meteorológico.", 0, False, "general"),
    ("Y el mundo se ríe del pueblo.", 0, False, ""),
    # 3 · escalada en tres
    ("Durante 30 años, nadie se acuerda.", 0, False, ""),
    ("Hasta que un militar que tocó los restos dice:", 0, False, ""),
    ("Lo del globo era mentira.", 0, False, "militar"),
    ("Después aparecen testigos que hablan de cuerpos.", 0, False, ""),
    ("Y luego, un video de una «autopsia alienígena» que ven millones.", 0, False, ""),
    # 4 · el giro
    ("Y en 1994, la Fuerza Aérea lo admite: sí había un secreto.", 0, False, ""),
    ("Pero no era un ovni.", 0, True, ""),
    # 5 · el mecanismo
    ("Era un proyecto ultrasecreto: cadenas de globos con micrófonos, flotando altísimo para detectar las futuras bombas atómicas soviéticas.", 0, False, ""),
    ("Por eso no podían decir la verdad... y prefirieron que el mundo se riera.", 0, False, ""),
    # 6 · el remate
    ("¿Y los cuerpos?", 0, False, ""),
    ("Según la Fuerza Aérea, muñecos de prueba lanzados desde globos... años después.", 0, False, ""),
    ("O sea: el ejército capturó un ovni... que era su propio globo espía.", 0, False, ""),
]


def buscar(inicio, desde=0):
    for i in range(desde, len(GUION)):
        if GUION[i][0].startswith(inicio):
            return i
    raise ValueError(inicio)


CAPITULOS = ["Roswell"]
SERIAS = set()
OBJETIVO_PPM = 200.0
# frases que el TTS dijo atropelladas, un poco más lentas; la última, ~10 % más lenta que el resto
TEMPO_FRASE = {buscar("Y el mundo se ríe"): 0.72, buscar("Por eso no podían"): 0.86, buscar("¿Y los cuerpos?"): 0.85, buscar("O sea: el ejército"): 0.95}
SILENCIO_FRASE = {buscar("O sea: el ejército"): (0.35, 0.2)}
HABLADAS = {"1947": 5, "1994": 5, "30": 1}

PAUSA_NORMAL = 0.10
PAUSAS = {buscar("Y en 1994"): 0.5}
SILENCIO_INTERNO = (0.18, 0.10)

VOCES_EXTRA = {
    "general": ("Orus", "Habla un general del ejército de 1947 ante la prensa: voz seca, firme y cortante, como quien da una orden."),
    "militar": ("Enceladus", "Habla un militar retirado y anciano que susurra un secreto en voz muy baja, casi al oído, con tono de confesión."),
}
AJUSTE_CITAS = {"general": (-3, 1.0), "militar": (0, 0.96)}
ESTILO_MULETILLA = ""

VISIBLE = {
    ("roswel",): "Roswell",
}
ENFASIS_PALABRAS = set()

INDICACIONES = (
    "Narra como un amigo que te cuenta un chisme buenísimo: rápido, cómplice, irónico, en tuteo, con mucha variación de tono. "
    "La primera frase dila con un punto de misterio, como quien empieza una historia de ovnis. Nunca suenes a documental. "
    "Sin respiraciones audibles."
)
NARRADOR = (
    "Eres un narrador masculino latinoamericano (español neutro, con seseo) de videos cortos: ritmo muy ágil, unas 200 palabras "
    "por minuto, frases encadenadas sin pausas, salvo un silencio breve antes de 'Pero no era un ovni'. "
    "La última frase ('O sea: el ejército capturó un ovni...') dila un poco más despacio, saboreando el remate."
)
PRONUNCIACION = "Pronuncia 'Róswel' tal como está escrito."
