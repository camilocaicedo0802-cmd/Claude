"""Guion de «¿Michael Jackson se quiso volver blanco?» compartido por el motor de voz y la alineación.

Cada frase: (texto hablado, sección, énfasis, etiqueta libre).
El texto se escribe como se pronuncia ("mil novecientos ochenta y dos"); VISIBLE dice cómo se ve en pantalla.
"""

GUION = [
    ("¡Michael Jackson no se volvió blanco por gusto!...", "gancho", False, ""),
    ("Y lo creímos... por culpa de un secreto que él mismo guardó.", "gancho", False, ""),
    ("En mil novecientos ochenta y dos, con Thriller, ¡Michael es el artista más grande del planeta!", "origen", False, ""),
    ("Pero pronto... le aparecen manchas blancas en la piel.", "origen", False, ""),
    ("Él las tapa con maquillaje... y calla.", "escalon", False, ""),
    ("Los tabloides lo apodan «Wacko Jacko» y publican que se blanquea a propósito.", "escalon", False, ""),
    ("¡Las revistas lo copian por todo el mundo!", "escalon", False, ""),
    ("Y las fotos parecen darles la razón:", "escalon2", False, ""),
    ("a los veinte, piel morena...", "escalon2", False, ""),
    ("a los treinta y tres, ¡casi blanca!", "escalon2", True, ""),
    ("Y encima... ¡se opera la nariz!", "escalon2", False, ""),
    ("Pero tenía... ¡vitiligo! Una enfermedad que borra el color de la piel.", "climax", False, ""),
    ("¿Quién lo confirmó?", "climax", False, ""),
    ("¡Su autopsia, en dos mil nueve!", "climax", True, ""),
    ("¿Y las cremas que usaba?", "climax", False, ""),
    ("¡Eran para igualar las manchas, no para blanquearse!", "climax", False, ""),
    ("Para colmo, cuando por fin lo contó en televisión... ¡muchos ya no le creyeron!", "golpe", False, ""),
    ("Y eso que ya había cantado: «No importa si eres negro o blanco».", "golpe", False, ""),
    ("Veredicto: ¡mito!", "veredicto", True, ""),
    ("¿Quiso ser blanco... o fue víctima del chisme más cruel del pop?", "pregunta", False, ""),
]

# Dirección con la energía del short de Napoleón: chisme histórico, sorpresa, pausas y golpes en los momentos clave
DIRECCION = [
    "arranque con mucha energía y sorpresa, como quien revela un secreto increíble; tono alto en 'no se volvió blanco'",
    "baja la voz con picardía y complicidad; pausa después de 'creímos...'",
    "épico y emocionado, subiendo el tono como quien presenta a una superestrella; 'Thriller' en inglés",
    "giro de suspenso: 'Pero pronto...' lento y misterioso",
    "casi en susurro, íntimo; pausa dramática antes de 'y calla'",
    "tono de chisme sensacionalista, con burla e ironía; 'Wacko Jacko' en inglés y con énfasis",
    "rápido y animado, como un rumor que se riega",
    "suspenso, como un detective que muestra la prueba",
    "lento y descriptivo",
    "MOMENTO CLAVE: sorpresa fuerte, sube mucho el tono en '¡casi blanca!'",
    "remate irónico: pausa en 'Y encima...' y golpe en '¡se opera la nariz!'",
    "MOMENTO CLAVE: el gran giro; pausa antes de '¡vitiligo!' y dilo con fuerza; luego explica con calidez",
    "pregunta desafiante, la entonación sube al final",
    "MOMENTO CLAVE: respuesta triunfal y fuerte",
    "pregunta curiosa, con picardía",
    "firme y enérgico, desmintiendo el rumor",
    "indignación que crece: '¡muchos ya no le creyeron!' con fuerza",
    "emotivo; cita la frase con calidez y admiración",
    "MOMENTO CLAVE: pausa tras 'Veredicto' y golpe fuerte en '¡mito!'",
    "pregunta final con la mayor energía y volumen de todo el audio, dejándola abierta",
]
assert len(DIRECCION) == len(GUION)

# energía general (se suma a las indicaciones)
ESTILO_EXTRA = (
    "Energía alta de principio a fin: tono vivo y muy variado, que suba y baje mucho, como un creador de contenido "
    "que cuenta un chisme histórico apasionante. Exclama en los momentos clave, susurra en los secretos y nunca suenes plano."
)

PRONUNCIACION = "Pronuncia 'Michael Jackson', 'Thriller' y 'Wacko Jacko' en inglés; 'pop' como en español."

# secuencias habladas -> cómo se ven en los subtítulos (las más largas primero)
VISIBLE = {
    ("mil", "novecientos", "ochenta", "y", "dos"): "1982",
    ("dos", "mil", "nueve"): "2009",
    ("treinta", "y", "tres"): "33",
    ("veinte",): "20",
}
ENFASIS_PALABRAS = {"thriller", "manchas", "wacko", "jacko", "vitiligo", "autopsia", "cremas", "mito", "blanca", "1982", "2009"}

# pausa (s) que queda DESPUÉS de cada frase: las de suspenso, más largas
PAUSAS = {0: 0.4, 1: 0.6, 2: 0.4, 3: 0.55, 4: 0.5, 5: 0.4, 6: 0.55, 7: 0.4, 8: 0.35, 9: 0.45, 10: 0.6,
          11: 0.55, 12: 0.4, 13: 0.55, 14: 0.4, 15: 0.6, 16: 0.45, 17: 0.65, 18: 0.55}

INDICACIONES = (
    "Genera una voz completamente natural y humana, con una narración fluida, expresiva y envolvente. "
    "Utiliza entonaciones naturales, pausas y cambios de ritmo. Haz énfasis en las preguntas, transmite suspenso, "
    "sorpresa, emoción o intriga según el contexto de cada momento. La voz debe sentirse cercana, auténtica y dinámica, "
    "como una persona que cuenta una historia y logra mantener al espectador conectado de principio a fin. "
    "Evita sonar robótica, monótona o artificial."
)
