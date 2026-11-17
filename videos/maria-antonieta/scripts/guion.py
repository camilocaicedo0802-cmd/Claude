"""Guion de «¿María Antonieta dijo "que coman pasteles"?» compartido por el motor de voz y la alineación.

Cada frase: (texto hablado, sección, énfasis, etiqueta libre).
El texto se escribe como se pronuncia ("mil setecientos setenta"); VISIBLE dice cómo se ve en pantalla.
"""

GUION = [
    ("María Antonieta nunca dijo «que coman pasteles»...", "gancho", False, ""),
    ("y la frase se escribió cuando era una niña.", "gancho", False, ""),
    ("En mil setecientos setenta, una princesa austríaca de catorce años llega a Versalles para casarse con el futuro rey.", "origen", False, ""),
    ("Pero ahí no la quieren.", "origen", False, ""),
    ("La llaman «la Austríaca»...", "escalon", False, ""),
    ("y en francés esa palabra esconde otra: «perra».", "escalon", False, ""),
    ("Cuando el país se arruina, le ponen otro mote: «Madame Déficit».", "escalon", False, ""),
    ("Llega la Revolución, el pueblo no tiene pan, y hay una frase que la persigue hasta hoy:", "escalon2", False, ""),
    ("«¡Que coman pasteles!».", "escalon2", True, ""),
    ("La prueba de que no le importaba nadie.", "escalon2", False, ""),
    ("Pero, ¿quién la oyó decirla?", "climax", False, ""),
    ("¡Nadie!", "climax", True, ""),
    ("La frase está en el libro de un filósofo, y la dice «una gran princesa»... sin nombre.", "climax", False, ""),
    ("Y ni siquiera dice pasteles: dice brioche.", "climax", False, ""),
    ("¿Y dónde estaba María Antonieta cuando se escribió?", "climax", False, ""),
    ("¡En Viena... siendo una niña!", "climax", True, ""),
    ("Lo más irónico: en mil setecientos setenta y cinco, tras unas revueltas por el pan, le escribe a su madre que deben trabajar por la felicidad del pueblo.", "golpe", False, ""),
    ("Dieciocho años después... la guillotinan.", "golpe", False, ""),
    ("Veredicto: falso.", "veredicto", True, ""),
    ("¿Reina sin corazón... o víctima de la fake news más exitosa de la historia?", "pregunta", False, ""),
]

# Dirección actoral por frase (para Gemini TTS): momentos clave, suspenso y entonación
DIRECCION = [
    "arranque intrigante y contundente, como quien desmiente un mito famoso; pausa tras 'pasteles'",
    "remate sorprendente, bajando la voz con complicidad",
    "narrador de cuento, cálido, como un 'érase una vez'",
    "giro sombrío, lento",
    "tono de chisme de la corte, imitando el desdén",
    "revelación picante: pausa antes de 'perra' y dila con fuerza",
    "ironía; pronuncia 'Madame Déficit' a la francesa",
    "tensión que crece, el ritmo se acelera",
    "MOMENTO CLAVE: la frase famosa, exclamada con desprecio aristocrático",
    "indignado, como lo diría el pueblo",
    "giro: pregunta lenta y desafiante",
    "MOMENTO CLAVE: golpe seco y fuerte",
    "como un detective que revela una pista; pausa misteriosa antes de 'sin nombre'",
    "divertido y sorprendido; pronuncia 'brioche' a la francesa",
    "suspenso, la pregunta sube al final",
    "MOMENTO CLAVE: revelación triunfal",
    "más íntimo y serio, casi emotivo",
    "MOMENTO CLAVE: grave y pausado, silencio dramático antes de 'la guillotinan'",
    "MOMENTO CLAVE: pausa tras 'Veredicto' y golpe fuerte en 'falso'",
    "pregunta final con la mayor energía y volumen de todo el audio, dejándola abierta",
]
assert len(DIRECCION) == len(GUION)

PRONUNCIACION = "Pronuncia 'Madame Déficit' y 'brioche' a la francesa, y 'fake news' en inglés."

# secuencias habladas -> cómo se ven en los subtítulos (las más largas primero)
VISIBLE = {
    ("mil", "setecientos", "setenta", "y", "cinco"): "1775",
    ("mil", "setecientos", "setenta"): "1770",
    ("catorce",): "14",
    ("dieciocho",): "18",
}
ENFASIS_PALABRAS = {"pasteles", "perra", "deficit", "nadie", "brioche", "viena", "nina", "falso", "guillotinan", "1770", "1775"}

# pausa (s) que queda DESPUÉS de cada frase: las de suspenso, más largas
PAUSAS = {0: 0.4, 1: 0.6, 2: 0.36, 3: 0.55, 4: 0.3, 5: 0.5, 6: 0.55, 7: 0.4, 8: 0.45, 9: 0.6, 10: 0.45,
          11: 0.5, 12: 0.4, 13: 0.5, 14: 0.45, 15: 0.6, 16: 0.5, 17: 0.7, 18: 0.55}

# Indicaciones de voz del usuario (se usan tal cual con Gemini)
INDICACIONES = (
    "Genera una voz completamente natural y humana, con una narración fluida, expresiva y envolvente. "
    "Utiliza entonaciones naturales, pausas y cambios de ritmo. Haz énfasis en las preguntas, transmite suspenso, "
    "sorpresa, emoción o intriga según el contexto de cada momento. La voz debe sentirse cercana, auténtica y dinámica, "
    "como una persona que cuenta una historia y logra mantener al espectador conectado de principio a fin. "
    "Evita sonar robótica, monótona o artificial."
)
