"""Guion de Napoleón compartido por todos los motores de voz.

Cada frase: (texto hablado, sección, énfasis, etiqueta de emoción para ElevenLabs v3).
El texto se escribe como se pronuncia ("mil ochocientos dos"); VISIBLE dice cómo se ve en pantalla.
"""

GUION = [
    ("¡Napoleón era más alto que el francés promedio!", "gancho", False, "excited"),
    ("Y lo recordamos enano... por culpa de un dibujante inglés.", "gancho", False, "mischievously"),
    ("En mil ochocientos dos, Napoleón es el hombre más poderoso de Francia.", "desarrollo", False, "storytelling"),
    ("Pero en Londres... un caricaturista lo odia.", "conflicto", False, "whispers"),
    ("Lo dibuja diminuto, con berrinches de niño, y le pone un apodo:", "desarrollo", False, "chuckles"),
    ("¡Little Boney!", "conflicto", True, "sarcastic"),
    ("Los periódicos lo copian por toda Europa.", "desarrollo", False, "excited"),
    ("Cuando muere, en mil ochocientos veintiuno, la autopsia dice: cinco pies y dos pulgadas.", "desarrollo", False, "thoughtful"),
    ("En Inglaterra eso es...", "conflicto", False, "curious"),
    ("¡uno cincuenta y siete!", "conflicto", True, "surprised"),
    ("Pero eran pulgadas francesas, más largas.", "desarrollo", False, "mischievously"),
    ("¿Cuánto medía de verdad?", "conflicto", False, "curious"),
    ("¡Casi uno sesenta y nueve!", "conflicto", True, "amazed"),
    ("¿Y el francés promedio?", "conflicto", False, "curious"),
    ("Unos uno sesenta y cinco.", "desarrollo", False, "sarcastic"),
    ("Para colmo, siempre aparecía rodeado de su guardia: soldados elegidos por altos.", "desarrollo", False, "chuckles"),
    ("Y el pequeño cabo era un apodo cariñoso, no una medida.", "desarrollo", False, "warmly"),
    ("Veredicto: ¡mito!", "veredicto", True, "dramatic"),
    ("¿Emperador bajito... o víctima del primer meme de la historia?", "pregunta", False, "excited"),
]

# secuencias habladas -> cómo se ven en los subtítulos
VISIBLE = {
    ("mil", "ochocientos", "dos"): "1802",
    ("mil", "ochocientos", "veintiuno"): "1821",
    ("uno", "cincuenta", "y", "siete"): "¡1,57",
    ("uno", "sesenta", "y", "nueve"): "1,69",
    ("uno", "sesenta", "y", "cinco"): "1,65",
}
ENFASIS_PALABRAS = {"mito", "meme", "165", "1802", "1821"}

# Indicaciones de voz del usuario (se usan tal cual con Gemini)
INDICACIONES = (
    "Genera una voz completamente natural y humana, con una narración fluida, expresiva y envolvente. "
    "Utiliza entonaciones naturales, pausas y cambios de ritmo. Haz énfasis en las preguntas, transmite suspenso, "
    "sorpresa, emoción o intriga según el contexto de cada momento. La voz debe sentirse cercana, auténtica y dinámica, "
    "como una persona que cuenta una historia y logra mantener al espectador conectado de principio a fin. "
    "Evita sonar robótica, monótona o artificial."
)
