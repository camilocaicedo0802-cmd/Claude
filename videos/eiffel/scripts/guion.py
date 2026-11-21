"""Guion del short «El hombre que vendió la Torre Eiffel» (Victor Lustig, vertical).

Cada frase: (texto hablado, sección, énfasis, voz). Voz "" = narrador (Charon); "lustig", "lustig2" y "esposa" = citas.
Pronunciación escrita como se dice: «Torre Éifel», «Víctor Lústig» (en los subtítulos se ve bien escrito).
Pausas: solo las marcadas (0,5 s antes de «Y eso lo convence», 0,4 s después de «¿Y cómo terminó?» y micro pausas
de 0,25–0,3 s); ninguna otra de más de 0,3 s. «vendedor aprendiz», un 15 % más lento y sin nada después.
"""

M = "muletilla"

GUION = [
    # 0 · escena imposible
    ("Un estafador vendió la Torre Éifel...", 0, False, ""),
    ("y quiso repetirlo.", 0, False, ""),
    # 1 · mira
    ("Mira, en 1925 la torre está oxidada, cuesta una fortuna... y había nacido para ser desmontada.", 0, False, ""),
    ("Y un estafador, Víctor Lústig, lo lee y piensa:", 0, False, ""),
    ("Si la van a desmontar... alguien la puede vender.", 0, False, "lustig"),
    # 2 · escalada en tres
    ("Primero, falsifica papeles del gobierno.", 0, False, ""),
    ("Después, cita en secreto a seis chatarreros en un hotel de lujo.", 0, False, ""),
    ("Y les suelta:", 0, False, ""),
    ("Vendemos la torre como chatarra. Pero ni una palabra.", 0, False, "lustig2"),
    # 3 · la duda
    ("Uno quiere comprarla, pero su esposa sospecha:", 0, False, ""),
    ("¿Y si es una estafa?", 0, False, "esposa"),
    # 4 · el giro
    ("Así que Lústig le confiesa que es un funcionario corrupto... y le pide un soborno.", 0, False, ""),
    ("Y eso lo convence.", 0, True, ""),
    # 5 · el mecanismo
    ("Mira, un estafador nunca pediría un soborno... pero un funcionario de verdad, sí.", 0, False, ""),
    ("Le paga la torre...", 0, False, ""),
    ("y encima el soborno.", 0, False, ""),
    # 6 · el remate
    ("¿Y la denuncia?", 0, False, ""),
    ("Nunca llegó: al comprador le dio demasiada vergüenza.", 0, False, ""),
    ("Así que Lústig volvió a intentarlo... y esta vez tuvo que huir.", 0, False, ""),
    ("¿Y cómo terminó?", 0, False, ""),
    ("Murió preso, y en su certificado de defunción, en profesión, pusieron:", 0, False, ""),
    ("«vendedor aprendiz».", 0, True, ""),
]


def buscar(inicio, desde=0):
    for i in range(desde, len(GUION)):
        if GUION[i][0].startswith(inicio):
            return i
    raise ValueError(inicio)


CAPITULOS = ["Torre Eiffel"]
SERIAS = set()
OBJETIVO_PPM = 202.0
TEMPO_FRASE = {buscar("«vendedor aprendiz»"): 0.85, buscar("Así que Lústig le confiesa"): 0.88}
HABLADAS = {"1925": 3}

# Voz natural (como Napoleón): la toma del narrador queda continua (scripts/montar_natural.py). Pausas en silencio
# real y en tiempo final: las marcadas quedan exactas; las demás solo se acortan hasta estos topes.
PAUSA_NORMAL = 0.17
PAUSA_INTERNA_MAX = 0.22
SIN_RESPIRACIONES = True
REFUERZO_FINAL = 1.15
PAUSAS = {
    buscar("Un estafador vendió"): 0.30,      # micro pausa después de «Torre Eiffel...»
    buscar("Así que Lústig le confiesa"): 0.50,  # medio segundo antes de «Y eso lo convence»
    buscar("Le paga la torre"): 0.30,          # antes de «y encima el soborno»
    buscar("¿Y cómo terminó?"): 0.40,          # después de la pregunta misteriosa
    buscar("Murió preso"): 0.30,               # «en profesión, pusieron:» → «vendedor aprendiz»
}
SILENCIO_INTERNO = (0.18, 0.10)
# en el susurro de Lustig se respeta la micro pausa de «Si la van a desmontar...» (hasta 0,28 s)
SILENCIO_FRASE = {buscar("Si la van a desmontar"): (0.40, 0.28)}

VOCES_EXTRA = {
    "lustig": ("Enceladus", "Un caballero elegante piensa en voz alta, en un susurro suave, lento y seguro, saboreando una idea brillante, con una sonrisa que se nota al final. Sin acento extranjero."),
    "lustig2": ("Enceladus", "Un caballero elegante propone un negocio confidencial: voz baja, segura y persuasiva; 'Pero ni una palabra' casi en susurro y más grave. Sin acento extranjero."),
    "esposa": ("Kore", "Una esposa seca y escéptica, de brazos cruzados, que desconfía; la pregunta sube al final. Articula bien clara la f de estafa: es-ta-FA."),
}
AJUSTE_CITAS = {"lustig": (0, 1.0), "lustig2": (0, 1.0), "esposa": (0, 1.12)}
ESTILO_MULETILLA = ""

VISIBLE = {
    ("eifel",): "Eiffel",
    ("lustig",): "Lustig",
}
ENFASIS_PALABRAS = set()

INDICACIONES = (
    "Narra como un amigo que cuenta un chisme buenísimo y admira un poco la jugada del estafador: cómplice, pícaro, muy "
    "expresivo, con mucha variación entre graves y agudos, nunca de documental. Sin respiraciones audibles. Dirección frase a frase: "
    "1) Empieza arriba, con energía y picardía; acentúa 'vendió', micro pausa después de 'Torre Éifel...' y di 'y quiso repetirlo' "
    "con una sonrisa cómplice, casi riéndote. 2) 'Mira...' baja a un tono relajado y conversacional; 'oxidada' y 'cuesta una fortuna' "
    "rápido, de pasada; en 'había nacido para ser desmontada' sube con sorpresa, como si acabaras de enterarte. "
    "3) 'Primero' claro y marcado; 'Después' con más velocidad; cada paso más rápido que el anterior. "
    "4) 'Uno quiere comprarla' con ilusión. 5) En el giro baja la voz, como quien cuenta la parte buena: 'funcionario corrupto' "
    "saboreándolo y acentúa 'soborno'; 'Y eso lo convence.' corto, seguro y con un punto de admiración. "
    "6) 'Mira' explicativo y rápido; acentúa 'nunca'; 'pero un funcionario de verdad, sí' con tono de '¿lo ves?'; "
    "'y encima el soborno' con incredulidad divertida. 7) '¿Y la denuncia?' pregunta rápida; 'Nunca llegó' seco; 'vergüenza' con "
    "gracia, compadeciendo al comprador; 'volvió a intentarlo...' pícaro; 'y esta vez tuvo que huir' rápido, como una huida; "
    "'¿Y cómo terminó?' frena, más misterioso; 'Murió preso' neutral, sin burla; 'vendedor aprendiz' más lento, seco e irónico, "
    "con media sonrisa, y ahí termina sin respiración ni ningún sonido después."
)
NARRADOR = (
    "Eres un narrador masculino latinoamericano (español neutro, con seseo) de videos cortos: ritmo muy ágil, unas 200 palabras "
    "por minuto, frases encadenadas sin pausas salvo las indicadas."
)
PRONUNCIACION = "Pronuncia 'Torre Éifel' y 'Víctor Lústig' tal como están escritos, y '1925' como 'mil novecientos veinticinco'."
