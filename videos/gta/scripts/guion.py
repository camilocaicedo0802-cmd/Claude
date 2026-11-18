"""Guion de «GTA existe por un bug» compartido por el motor de voz y la alineación.

Cada frase: (texto hablado, sección, énfasis, etiqueta libre).
"""

GUION = [
    ("¡GTA existe por un bug!", "gancho", True, ""),
    ("Un error que volvía loca a la policía...", "gancho", False, ""),
    ("y eso ni siquiera es lo más loco de su historia.", "gancho", False, ""),
    ("Al principio no era un juego de criminales: era de carreras, policías contra ladrones.", "origen", False, ""),
    ("Y era... ¡aburridísimo!", "origen", True, ""),
    ("Tan aburrido que estuvo a punto de cancelarse.", "escalon", False, ""),
    ("Hasta que un error en el código vuelve locos a los policías:", "escalon2", False, ""),
    ("ya no te persiguen...", "escalon2", False, ""),
    ("¡te embisten, te encierran, te sacan de la calle!", "escalon2", True, ""),
    ("Y los que lo prueban no quieren soltarlo.", "climax", False, ""),
    ("¿Lo más divertido?", "climax", False, ""),
    ("¡Escaparse de esos policías locos!", "climax", True, ""),
    ("¿Y arreglaron el bug?", "climax", False, ""),
    ("¡Al contrario!", "climax", True, ""),
    ("Lo convirtieron en el juego...", "climax", False, ""),
    ("y le pusieron Grand Theft Auto: robo de autos.", "climax", True, ""),
    ("Pero lo más loco vino después.", "golpe", False, ""),
    ("Cuando en Inglaterra pidieron prohibirlo por violento...", "golpe", False, ""),
    ("esa polémica la había inventado su propia distribuidora.", "golpe", True, ""),
    ("Contrataron a un experto en escándalos para que todo el mundo hablara del juego.", "golpe", False, ""),
    ("Y vaya que hablaron.", "golpe", False, ""),
    ("Veredicto: ¡real!", "veredicto", True, ""),
    ("¿Genios del marketing... o pura suerte?", "pregunta", False, ""),
]

# Dirección con energía de chisme gamer: sorpresa, complicidad, pausas y golpes en los momentos clave
DIRECCION = [
    "arranque con mucha energía y sorpresa, como quien revela un dato increíble; golpe fuerte en '¡bug!'",
    "tono divertido y misterioso, con picardía en 'loca'",
    "baja la voz con complicidad, como adelantando un chisme todavía mejor",
    "narrador que cuenta el origen con ritmo, enumerando con curiosidad",
    "MOMENTO CLAVE: pausa tras 'Y era...' y remata '¡aburridísimo!' con burla exagerada, alargando la 'í'",
    "dramático, con suspenso, como una tragedia a punto de ocurrir",
    "giro: 'Hasta que...' lento y emocionado, como el inicio de algo épico",
    "suave, casi normal, preparando el contraste",
    "MOMENTO CLAVE: acelera y sube con cada verbo, cada vez más fuerte, como una persecución",
    "contento y cómplice, como quien confiesa que el juego es adictivo",
    "pregunta curiosa y juguetona, la entonación sube al final",
    "respuesta eufórica y divertida",
    "pregunta con picardía, bajando la voz",
    "MOMENTO CLAVE: golpe fuerte y sorprendido",
    "orgulloso, con pausa al final",
    "épico, como el anuncio de un título legendario; 'Grand Theft Auto' en inglés y con fuerza; 'robo de autos' con complicidad",
    "cambio de tono: suspenso y misterio, bajando la voz",
    "tono de escándalo, como un noticiero sensacionalista",
    "MOMENTO CLAVE: revelación sorprendida e irónica, casi riéndose",
    "rápido y pícaro, como quien cuenta una travesura",
    "remate con picardía y satisfacción",
    "MOMENTO CLAVE: pausa tras 'Veredicto' y golpe fuerte en '¡real!'",
    "pregunta final con la mayor energía y volumen de todo el audio, dejándola abierta",
]
assert len(DIRECCION) == len(GUION)

ESTILO_EXTRA = (
    "Energía alta de principio a fin: tono vivo y muy variado, que suba y baje mucho, como un creador de contenido "
    "gamer que cuenta un chisme histórico apasionante. Exclama en los momentos clave, susurra en los secretos y nunca suenes plano."
)

PRONUNCIACION = (
    "Pronuncia 'GTA' letra por letra en español: 'ge-te-a'. Pronuncia 'bug' en inglés ('bag'). "
    "Pronuncia 'Grand Theft Auto' en inglés."
)

VISIBLE = {
    ("ge", "te", "a"): "GTA",
}
ENFASIS_PALABRAS = {"gta", "bug", "policia", "aburridisimo", "cancelarse", "error", "embisten", "encierran", "calle",
                    "divertido", "contrario", "grand", "theft", "auto", "inglaterra", "prohibirlo", "polemica",
                    "distribuidora", "escandalos", "real", "marketing", "suerte", "locos"}

# pausa (s) que queda DESPUÉS de cada frase
PAUSAS = {0: 0.45, 1: 0.35, 2: 0.6, 3: 0.4, 4: 0.55, 5: 0.6, 6: 0.3, 7: 0.25, 8: 0.6, 9: 0.45, 10: 0.3, 11: 0.5,
          12: 0.3, 13: 0.35, 14: 0.25, 15: 0.65, 16: 0.45, 17: 0.25, 18: 0.55, 19: 0.4, 20: 0.6, 21: 0.55}

INDICACIONES = (
    "Genera una voz completamente natural y humana, con una narración fluida, expresiva y envolvente. "
    "Utiliza entonaciones naturales, pausas y cambios de ritmo. Haz énfasis en las preguntas, transmite suspenso, "
    "sorpresa, emoción o intriga según el contexto de cada momento. La voz debe sentirse cercana, auténtica y dinámica, "
    "como una persona que cuenta una historia y logra mantener al espectador conectado de principio a fin. "
    "Evita sonar robótica, monótona o artificial."
)
