"""Guion del short «Lo contrataron» (vertical): el resumen de «Los genios que contrataron a Hitler».

Cada frase: (texto hablado, sección, énfasis, voz). Voz "" = narrador (Charon); "hindenburg" y "papen" = citas.
Pronunciación escrita como se dice: «Pápen», «Híndenburg» (en los subtítulos se ven bien escritas).
Ritmo de chisme: 195–205 palabras por minuto, en presente. Solo dos pausas: 0,4 s antes de «Votan a favor»
y otra antes de la última frase, que va un 12 % más lenta.
"""

M = "muletilla"

GUION = [
    # 0 · escena imposible
    ("Le regaló el poder a Hitler... y prometió que en dos meses lo tendría chillando en un rincón.", 0, False, ""),
    # 1 · mira
    ("Mira, Hitler nunca había ganado una mayoría.", 0, False, ""),
    ("Pero un aristócrata, Franz von Pápen, quería vengarse de un rival... y necesitaba sus votos.", 0, False, ""),
    # 2 · la burla
    ("El presidente se burlaba de Hitler:", 0, False, ""),
    ("Como mucho, lo hago cartero.", 0, False, "hindenburg"),
    ("Y Pápen lo tranquiliza:", 0, False, ""),
    ("Solo tres ministros nazis de once. Lo tenemos rodeado.", 0, False, "papen"),
    # 3 · arranca el reloj
    ("Enero de 1933: Hitler es canciller.", 0, False, ""),
    ("Sin mayoría. Sin ganar.", 0, True, ""),
    # 4 · escalada en tres
    ("A las cuatro semanas, se incendia el Parlamento.", 0, False, ""),
    ("A las cinco, elecciones con miedo en las calles... y ni así saca mayoría.", 0, False, ""),
    ("A los 52 días... el Parlamento vota su propia desaparición.", 0, False, ""),
    # 5 · el giro
    ("¿Y los hombres de Pápen, los que lo iban a controlar?", 0, False, ""),
    ("Votan a favor.", 0, True, ""),
    ("En el rincón no terminó Hitler... terminó el Parlamento entero.", 0, False, ""),
    # 6 · el mecanismo
    ("Mira, creían que lo tenían rodeado.", 0, False, ""),
    ("Pero uno de esos tres ministros controlaba la policía del estado más grande de Alemania.", 0, False, ""),
    # 7 · el remate
    ("Cómo llegó a esa silla es todavía más absurdo: está en el video de aquí abajo.", 0, False, ""),
    ("Pero el final ya lo sabes: lo habían contratado... y el contratado se quedó con la empresa.", 0, False, ""),
]


def buscar(inicio, desde=0):
    for i in range(desde, len(GUION)):
        if GUION[i][0].startswith(inicio):
            return i
    raise ValueError(inicio)


CAPITULOS = ["Lo contrataron"]
SERIAS = set()
OBJETIVO_PPM = 208.0
# frase final un 12 % más lenta
TEMPO_FRASE = {buscar("¿Y los hombres de Pápen"): 0.74, buscar("Pero el final ya lo sabes"): 0.74}
# la última frase conserva sus micro-pausas naturales (en «sabes:» y «contratado...»), sin pasar de 0,22 s
SILENCIO_FRASE = {buscar("Pero el final ya lo sabes"): (0.35, 0.22)}
# palabras que se dicen como varias (para medir el ritmo real)
HABLADAS = {"1933": 5, "52": 3}

# pausas (s) DESPUÉS de cada frase: casi nada (sin respiraciones), salvo las dos que pide el guion
PAUSA_NORMAL = 0.10
PAUSAS = {buscar("¿Y los hombres de Pápen"): 0.4, buscar("Cómo llegó a esa silla"): 0.5}
# dentro de cada frase, los silencios largos se acortan a esto
SILENCIO_INTERNO = (0.18, 0.10)

VOCES_EXTRA = {
    "hindenburg": ("Algenib", "Habla un anciano mariscal de ochenta y cuatro años, con voz grave, lenta y despectiva, burlándose de alguien."),
    "papen": ("Algieba", "Habla un aristócrata satisfecho y seguro de sí mismo que tranquiliza a otro con una sonrisa."),
}
ESTILO_MULETILLA = ""
# ajuste de cada cita (semitonos, tempo): las tomas ya salieron graves; Hindenburg apenas más lento
AJUSTE_CITAS = {"hindenburg": (-1, 0.95), "papen": (-1, 1.0)}

VISIBLE = {
    ("papen",): "Papen",
    ("hindenburg",): "Hindenburg",
}
ENFASIS_PALABRAS = set()

INDICACIONES = (
    "Narra como un amigo que te cuenta un chisme histórico buenísimo: rápido, cómplice, irónico, en tuteo y en presente, "
    "con mucha variación de tono y remates con picardía. Nunca suenes a documental solemne. Sin respiraciones audibles."
)
NARRADOR = (
    "Eres un narrador masculino latinoamericano (español neutro, con seseo) de videos cortos: ritmo muy ágil, unas 200 palabras "
    "por minuto, frases encadenadas sin pausas. La invitación al video ('está en el video de aquí abajo') dila rápido y casual, "
    "como un comentario de paso, nunca como vendedor. La última frase ('Pero el final ya lo sabes...') dila un poco más despacio."
)
PRONUNCIACION = "Pronuncia 'Pápen' y 'Híndenburg' tal como están escritos."
