"""Guion de «Hackeó GTA 6 desde la tele de un hotel» compartido por la voz, el montaje y la alineación.

Cada frase: (texto hablado, sección, énfasis, voz). Voz "" = narrador; "c1" y "c2" = comentarios de internet;
"hacker" = el mensaje del chat. No se dice el nombre del chico (era menor de edad).
"""

GUION = [
    ("Un chico de diecisiete años hackeó Ge te a seis... desde la tele de un hotel.", "gancho", True, ""),
    ("Mira, la policía ya lo había atrapado por hackear otras empresas.", "mira", False, ""),
    ("Le quitaron la computadora y lo llevaron a un hotel, para protegerlo.", "mira", False, ""),
    ("Sin computadora... ¿qué podía hacer?", "mira", False, ""),
    ("Primero, se mete al chat interno de Rockstar.", "escalada", False, ""),
    ("Después, a sus archivos secretos.", "escalada", False, ""),
    ("Y un domingo... sube noventa videos de Ge te a seis a un foro.", "escalada", True, ""),
    ("Y en internet se ríen:", "burla", False, ""),
    ("¡Es falso!", "burla", False, "c1"),
    ("¡Eso parece de PlayStation dos!", "burla", False, "c2"),
    ("Hasta que él escribe en el chat de los empleados:", "amenaza", False, ""),
    ("Si no me contactan en veinticuatro horas... publico el código del juego.", "amenaza", False, "hacker"),
    ("Y Rockstar lo confirma:", "giro", False, ""),
    ("los videos son reales.", "giro", True, ""),
    ("¿Y cómo lo hizo sin computadora?", "giro", False, ""),
    ("Con un Fire Stick: el aparatito para ver series en la tele.", "mecanismo", False, ""),
    ("Lo enchufa, usa su celular... y entra.", "mecanismo", False, ""),
    ("La policía lo había escondido ahí para protegerlo...", "mecanismo", False, ""),
    ("y le dio el cuarto perfecto para hackear.", "mecanismo", True, ""),
    ("A Rockstar le costó cinco millones de dólares.", "remate", False, ""),
    ("A él, un hospital de seguridad, sin fecha de salida.", "remate", False, ""),
    ("Todo por un aparatito de cuarenta dólares... enchufado a la tele de un hotel.", "remate", True, ""),
]

# Dirección del narrador (una por frase; las de otras voces no se usan con el narrador)
DIRECCION = [
    "GANCHO: arriba, con picardía y asombro, como quien suelta el chisme más increíble",
    "tono cómplice de amigo que cuenta el contexto, rápido",
    "rápido y con ironía suave en 'para protegerlo'",
    "pregunta pícara y retadora",
    "ESCALADA 1: rápido",
    "ESCALADA 2: todavía más rápido",
    "ESCALADA 3: el más rápido y con más energía de los tres, golpe en 'noventa videos'",
    "burlón, preparando los comentarios",
    "(otra voz)",
    "(otra voz)",
    "suspenso, bajando la voz",
    "(otra voz)",
    "seco y serio",
    "golpe firme y contundente",
    "pregunta intrigante",
    "revelación divertida, explicando como a un amigo; 'Fire Stick' en inglés",
    "rápido, con ritmo, como quien describe algo facilísimo",
    "ironía clara",
    "remate irónico",
    "REMATE: voz más grave, seria y pausada que en el resto del audio",
    "REMATE: grave, sobrio y respetuoso, sin burla",
    "REMATE FINAL: la frase más lenta de todo el audio (un 15 % más lenta), grave y con peso, saboreando la ironía hasta 'la tele de un hotel'",
]
assert len(DIRECCION) == len(GUION)

ESTILO_EXTRA = (
    "Habla rápido, entre 195 y 205 palabras por minuto, en presente y tuteando, como un amigo que te cuenta un chisme "
    "tecnológico. Sin pausas entre frases y sin respiraciones audibles. Energía alta, picardía y mucha variación de tono."
)

PRONUNCIACION = (
    "'Ge te a seis' es la sigla del videojuego GTA 6: di 'ge, te, a' letra por letra EN ESPAÑOL (la ge suena 'je') y "
    "'seis' en español; nunca en inglés. 'Rockstar' y 'Fire Stick' en inglés. 'hackeó' y 'hackear' como 'jaqueó' y 'jaquear'."
)

# Voces extra (Gemini TTS): voz y forma de decirlo
VOCES_EXTRA = {
    "c1": ("Puck", "Eres un usuario de internet joven que se burla en voz alta, riéndose, incrédulo y sarcástico."),
    "c2": ("Leda", "Eres una usuaria de internet joven que se burla con risa y tono despectivo, exagerando."),
    "hacker": ("Enceladus", "Voz fría, lenta y casi susurrada, amenazante y calmada, muy cerca del micrófono. Sin emoción."),
}

# secuencias habladas -> cómo se ven en los subtítulos (las más largas primero)
VISIBLE = {
    ("ge", "te", "a", "seis"): "GTA 6",
    ("cinco", "millones"): "5 MILLONES",
    ("playstation", "dos"): "PLAYSTATION 2",
    ("diecisiete",): "17",
    ("noventa",): "90",
    ("veinticuatro",): "24",
    ("cuarenta",): "40",
}
ENFASIS_PALABRAS = {"hotel", "tele", "policia", "rockstar", "noventa", "90", "falso", "reales", "fire", "stick", "hackear",
                    "millones", "40", "17", "gta"}

# Solo dos pausas: 0,4 s antes de «los videos son reales» y 0,5 s antes de «Todo por un aparatito…»
PAUSA_NORMAL = 0.1
PAUSA_INTERNA_MAX = 0.08
REFUERZO_FINAL = 1.0
PAUSAS = {12: 0.54, 20: 0.70}  # medidas para que el silencio real final quede en 0,4 y 0,5 s
SIN_RESPIRACIONES = True

INDICACIONES = (
    "Genera una voz completamente natural y humana, con una narración fluida, expresiva y envolvente. "
    "Utiliza entonaciones naturales y cambios de ritmo. Haz énfasis en las preguntas, transmite suspenso, "
    "sorpresa, emoción o intriga según el contexto de cada momento. La voz debe sentirse cercana, auténtica y dinámica, "
    "como una persona que cuenta una historia y logra mantener al espectador conectado de principio a fin. "
    "Evita sonar robótica, monótona o artificial."
)

# Ajustes por frase en el montaje: (velocidad, semitonos). La escalada acelera en cada paso; el remate, más grave.
# La última frase además va 10–15 % más lenta que el resto (montar_voz.py lo mide y lo ajusta).
AJUSTE_FRASES = {4: (0.85, 0), 5: (1.04, 0), 6: (1.45, 0), 19: (1.0, 0), 20: (1.0, 0), 21: (1.0, 0)}

# silencio que se inserta ANTES de estas frases en el montaje (alinear.py luego lo deja en la medida de PAUSAS)
PAUSAS_INSERTAR = {13: 0.8, 21: 0.95}
