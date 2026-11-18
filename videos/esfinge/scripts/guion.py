"""Guion de «La nariz de la Esfinge de Giza» compartido por el motor de voz y la alineación.

Cada frase: (texto hablado, sección, énfasis, etiqueta libre).
El texto se escribe como se pronuncia ("mil setecientos noventa y ocho"); VISIBLE dice cómo se ve en pantalla.
"""

GUION = [
    ("¡Napoleón no le voló la nariz a la Esfinge!...", "gancho", False, ""),
    ("La pobre ya estaba chata... antes de que él naciera.", "gancho", False, ""),
    ("En mil setecientos noventa y ocho, Napoleón llega con sus cañones a las pirámides.", "origen", False, ""),
    ("Y claro: francés, con cañones y frente a una Esfinge sin nariz...", "origen", False, ""),
    ("¿quién más iba a ser?", "origen", False, ""),
    ("Y nace la leyenda: soldados aburridos usaron la nariz como tiro al blanco.", "escalon", False, ""),
    ("Una nariz de un metro... ¡imposible fallar!", "escalon", False, ""),
    ("Y la historia pasa de guía en guía.", "escalon", False, ""),
    ("El caso parece clarísimo: llega Napoleón... y la nariz desaparece.", "escalon2", False, ""),
    ("Total, ya era «el bajito»...", "escalon2", False, ""),
    ("¿qué le cuesta ser vándalo también?", "escalon2", False, ""),
    ("Pero en mil setecientos treinta y siete, un explorador danés dibuja la Esfinge...", "climax", False, ""),
    ("¡y ya está chata!", "climax", True, ""),
    ("¿Cuántos años tenía Napoleón?", "climax", False, ""),
    ("¡Ni había nacido!", "climax", True, ""),
    ("¿Y el verdadero culpable?", "climax", False, ""),
    ("Un fanático, en mil trescientos setenta y ocho, harto de que le llevaran ofrendas.", "climax", False, ""),
    ("Para colmo, al vándalo lo ahorcaron.", "golpe", False, ""),
    ("Y la expedición de Napoleón hasta encontró la piedra de Rosetta...", "golpe", False, ""),
    ("que hoy está en Londres.", "golpe", False, ""),
    ("Los ingleses, otra vez.", "golpe", False, ""),
    ("Veredicto: ¡mito!", "veredicto", True, ""),
    ("Primero bajito, ahora vándalo...", "pregunta", False, ""),
    ("¿qué más le van a inventar al pobre Napoleón?", "pregunta", False, ""),
]

# Dirección con energía de chisme histórico (como el short de Napoleón): sorpresa, picardía, pausas y golpes
DIRECCION = [
    "arranque con mucha energía y sorpresa, desmintiendo un mito famoso; tono alto en '¡no le voló la nariz!'",
    "con ternura burlona en 'la pobre'; pausa tras 'chata...' y remate pícaro",
    "épico, como narrador de película de aventuras",
    "ironía cómplice, enumerando las 'pruebas' con picardía",
    "pregunta irónica que sube al final, como quien guiña el ojo",
    "tono de leyenda contada alrededor de una fogata, misterioso",
    "MOMENTO CLAVE: pausa tras 'un metro...' y '¡imposible fallar!' con humor y fuerza",
    "rápido, como un rumor que se riega",
    "tono de detective seguro de sí mismo; pausa antes de 'y la nariz desaparece'",
    "burla cariñosa, recordando el apodo",
    "pregunta irónica y divertida",
    "giro de suspenso: 'Pero...' lento, como quien saca una prueba secreta",
    "MOMENTO CLAVE: sorpresa fuerte en '¡y ya está chata!'",
    "pregunta desafiante, la entonación sube al final",
    "MOMENTO CLAVE: respuesta triunfal y fuerte, casi riéndose",
    "pregunta con intriga, bajando la voz",
    "revelación dramática, pausada, como quien desenmascara al culpable",
    "tono de 'para colmo', sorprendido y serio",
    "orgulloso y animado; pausa tras 'Rosetta...'",
    "remate pícaro",
    "MOMENTO CLAVE: resignación irónica, con un suspiro de burla",
    "MOMENTO CLAVE: pausa tras 'Veredicto' y golpe fuerte en '¡mito!'",
    "enumerando con burla cariñosa",
    "pregunta final con la mayor energía y volumen de todo el audio, divertida y dejándola abierta",
]
assert len(DIRECCION) == len(GUION)

ESTILO_EXTRA = (
    "Energía alta de principio a fin: tono vivo y muy variado, que suba y baje mucho, como un creador de contenido "
    "que cuenta un chisme histórico divertido. Exclama en los momentos clave, usa ironía y complicidad, y nunca suenes plano."
)

PRONUNCIACION = "Pronuncia 'Rosetta' como en español; 'Napoleón' y 'Esfinge' con claridad."

# secuencias habladas -> cómo se ven en los subtítulos (las más largas primero)
VISIBLE = {
    ("mil", "setecientos", "noventa", "y", "ocho"): "1798",
    ("mil", "setecientos", "treinta", "y", "siete"): "1737",
    ("mil", "trescientos", "setenta", "y", "ocho"): "1378",
}
ENFASIS_PALABRAS = {"esfinge", "chata", "napoleon", "leyenda", "metro", "vandalo", "1798", "1737", "1378", "rosetta", "londres", "mito"}

# pausa (s) que queda DESPUÉS de cada frase: las de suspenso, más largas
PAUSAS = {0: 0.4, 1: 0.6, 2: 0.4, 3: 0.3, 4: 0.6, 5: 0.4, 6: 0.45, 7: 0.55, 8: 0.4, 9: 0.3, 10: 0.6,
          11: 0.35, 12: 0.5, 13: 0.4, 14: 0.55, 15: 0.4, 16: 0.6, 17: 0.5, 18: 0.3, 19: 0.4, 20: 0.6, 21: 0.55, 22: 0.3}

INDICACIONES = (
    "Genera una voz completamente natural y humana, con una narración fluida, expresiva y envolvente. "
    "Utiliza entonaciones naturales, pausas y cambios de ritmo. Haz énfasis en las preguntas, transmite suspenso, "
    "sorpresa, emoción o intriga según el contexto de cada momento. La voz debe sentirse cercana, auténtica y dinámica, "
    "como una persona que cuenta una historia y logra mantener al espectador conectado de principio a fin. "
    "Evita sonar robótica, monótona o artificial."
)
