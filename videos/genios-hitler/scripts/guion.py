"""Guion de «Los genios que contrataron a Hitler» (video largo, horizontal).

Cada frase: (texto hablado, capítulo, énfasis, voz). Voz "" = narrador (Charon); "muletilla" = «Ese ya no llega a nada»
(un único audio que se repite igual las cuatro veces); el resto son citas con voces secundarias.
Pronunciación escrita como se dice: «Pápen», «Híndenburg», «Dájau» (en los subtítulos se ven bien escritas).
"""

M = "muletilla"

GUION = [
    # ---------------- 0 · Apertura
    ("Relájate. Lo hemos contratado. En dos meses lo tenemos tan arrinconado que va a chillar.", 0, False, "papen"),
    ("Eso lo dijo un aristócrata alemán en enero de 1933, para tranquilizar a un amigo preocupado.", 0, False, ""),
    ("¿Y sabes a quién habían contratado?", 0, False, ""),
    ("A Adolf Hitler.", 0, True, ""),
    ("Y sí: dos meses después había alguien chillando en un rincón.", 0, False, ""),
    ("Pero no era Hitler.", 0, True, ""),
    ("Porque Hitler nunca ganó unas elecciones por mayoría.", 0, False, ""),
    ("Nunca.", 0, True, ""),
    ("Al poder lo subieron unos señores que se reían de él...", 0, False, ""),
    ("y que se creían muchísimo más listos que él.", 0, False, ""),
    ("Y cómo llegamos ahí es absurdo:", 0, False, ""),
    ("un espía que se afilia al partido que espiaba,", 0, False, ""),
    ("un golpe de Estado en una cervecería,", 0, False, ""),
    ("un juez que no lo deporta porque «se siente alemán»...", 0, False, ""),
    ("y un presidente que lo quería poner a lamer sellos.", 0, False, ""),
    ("Empecemos por el espía.", 0, False, ""),
    # ---------------- 1 · El espía
    ("Hitler tiene 30 años, no tiene casa, ni novia, ni plan...", 1, False, ""),
    ("y trabaja de espía para el ejército alemán.", 1, False, ""),
    ("Su misión: vigilar partidos políticos.", 1, False, ""),
    ("Un día lo mandan a uno chiquitito: el Partido Obrero Alemán.", 1, False, ""),
    ("¿Cuántos eran?", 1, False, ""),
    ("Unos cuarenta tipos en una cervecería de Múnich.", 1, False, ""),
    ("Y Hitler está ahí, sentado, aburrido...", 1, False, ""),
    ("hasta que alguien dice algo que no le gusta.", 1, False, ""),
    ("Y se para. Y empieza a gritar. Y no para.", 1, False, ""),
    ("Y el fundador del partido, en vez de echarlo, se queda fascinado.", 1, False, ""),
    ("Dicen que soltó algo así como:", 1, False, ""),
    ("Este tiene una bocota. Nos sirve.", 1, False, "fundador"),
    ("O sea: lo mandan a espiar al partido...", 1, False, ""),
    ("y termina afiliándose.", 1, True, ""),
    ("Le dan el carnet número 555.", 1, False, ""),
    ("Suena a partido grande, ¿no?", 1, False, ""),
    ("Pues no. Empezaron a contar desde el 501 para parecer más.", 1, False, ""),
    ("Desde el primer día, todo inflado.", 1, False, ""),
    ("Y el espía resulta ser un show: grita, suda, golpea la mesa, y la gente hace fila para verlo.", 1, False, ""),
    ("En dos años, el partido ya se llama Partido Nacionalsocialista...", 1, False, ""),
    ("y lo manda él.", 1, True, ""),
    ("Pero seamos serios: un partido de cervecería no le quita el sueño a nadie.", 1, False, ""),
    ("Y Hitler tiene prisa. Muchísima prisa.", 1, False, ""),
    # ---------------- 2 · El golpe de la cervecería
    ("Imagínate un país donde una barra de pan cuesta miles de millones.", 2, False, ""),
    ("Esa es Alemania en 1923.", 2, False, ""),
    ("La gente lleva el sueldo en carretillas.", 2, False, ""),
    ("Y Hitler piensa: es ahora o nunca.", 2, False, ""),
    ("¿Su plan? Y esto es real:", 2, False, ""),
    ("hay un mitin de políticos importantes en otra cervecería; sí, otra.", 2, False, ""),
    ("Hitler entra con sus hombres, se sube a una silla, dispara al techo y grita:", 2, False, ""),
    ("¡La revolución nacional ha comenzado!", 2, False, ""),
    ("Y durante una noche, se siente el dueño de Baviera.", 2, False, ""),
    ("Al día siguiente marchan por el centro de Múnich.", 2, False, ""),
    ("Y la policía los está esperando.", 2, False, ""),
    ("Disparos.", 2, False, ""),
    ("Mueren dieciséis de los suyos y cuatro policías.", 2, False, ""),
    ("¿Y Hitler?", 2, False, ""),
    ("Se disloca el hombro, se sube a un auto...", 2, False, ""),
    ("y se va.", 2, True, ""),
    ("Lo encuentran dos días después, escondido en la casa de un amigo.", 2, False, ""),
    ("Y dicen que, cuando llegó la policía, quiso pegarse un tiro, y la esposa del amigo le quitó la pistola.", 2, False, ""),
    ("Fin. Todo el mundo lo da por terminado.", 2, False, ""),
    ("Un golpe de Estado armado en una cervecería, que no duró ni un día.", 2, False, ""),
    ("Ese ya no llega a nada.", 2, False, M),
    ("Pero espérate, que viene el juicio.", 2, False, ""),
    ("Y el juez es...", 2, False, ""),
    ("digamos, comprensivo.", 2, False, ""),
    ("Lo deja hablar todo lo que quiere.", 2, False, ""),
    ("Hitler convierte el juicio en un show...", 2, False, ""),
    ("y sale famoso.", 2, False, ""),
    ("¿La condena por traición? Cinco años.", 2, False, ""),
    ("¿Cuántos cumple?", 2, False, ""),
    ("Nueve meses.", 2, True, ""),
    ("Y no en un calabozo, ¿eh?", 2, False, ""),
    ("Una celda cómoda, con visitas, flores, cartas de admiradoras, regalos, comida...", 2, False, ""),
    ("Dicen que hasta engordó.", 2, False, ""),
    ("Y como se aburre, se pone a dictar un libro.", 2, False, ""),
    ("¿Sabes cuál era el título original?", 2, False, ""),
    ("«Cuatro años y medio de lucha contra las mentiras, la estupidez y la cobardía».", 2, False, ""),
    ("El editor lo leyó y le dijo: mejor algo más corto.", 2, False, ""),
    ("Y quedó en «Mi lucha».", 2, False, ""),
    ("Y falta lo mejor.", 2, False, ""),
    ("Hitler ni siquiera era alemán: era austríaco.", 2, False, ""),
    ("Y la ley lo decía clarito: si un extranjero es condenado por traición, se le deporta.", 2, False, ""),
    ("¿Lo deportaron?", 2, False, ""),
    ("No.", 2, True, ""),
    ("¿Sabes por qué?", 2, False, ""),
    ("Porque el juez dijo que Hitler pensaba y sentía de una forma muy alemana.", 2, False, ""),
    ("O sea: da un golpe de Estado, sale antes, sale famoso, sale con libro...", 2, False, ""),
    ("y se queda.", 2, True, ""),
    # ---------------- 3 · La fiera domada
    ("Lo primero que hace Hitler al salir de la cárcel es ir a ver al primer ministro de Baviera, el que había prohibido su partido.", 3, False, ""),
    ("Y le pone cara de niño bueno:", 3, False, ""),
    ("«Ya cambié. Voy a respetar las reglas».", 3, False, ""),
    ("Y el ministro se lo cree.", 3, False, ""),
    ("Levanta la prohibición y, después de la reunión, suelta una frase que debería estar en un museo:", 3, False, ""),
    ("La fiera está domada. Podemos aflojarle la cadena.", 3, False, "ministro"),
    ("¿Cuánto le duró lo domado?", 3, False, ""),
    ("Semanas.", 3, True, ""),
    ("En su primer gran discurso, Hitler está tan agresivo que le prohíben hablar en público.", 3, False, ""),
    ("Dos años sin poder dar un discurso en Baviera.", 3, False, ""),
    ("Y para colmo, en las elecciones de 1928, el partido de Hitler saca...", 3, False, ""),
    ("el 2,6 %.", 3, True, ""),
    ("Doce diputados de casi quinientos.", 3, False, ""),
    ("Si esto fuera una startup, los inversionistas ya se habrían ido corriendo.", 3, False, ""),
    ("Ese ya no llega a nada.", 3, False, M),
    ("Y probablemente ahí se habría quedado...", 3, False, ""),
    ("si no fuera por lo que pasó un año después, en Nueva York.", 3, False, ""),
    # ---------------- 4 · La crisis
    ("En 1929, Nueva York estornuda...", 4, False, ""),
    ("y Alemania se enferma.", 4, False, ""),
    ("Se cae la Bolsa, los bancos estadounidenses piden su plata de vuelta, y Alemania termina con seis millones de desempleados.", 4, False, ""),
    ("Y cuando la gente está desesperada, ¿quién aparece vendiendo soluciones fáciles para problemas difíciles?", 4, False, ""),
    ("Exacto. El de la cervecería.", 4, False, ""),
    ("En 1930, el partido del 2,6 % salta al 18 %.", 4, True, ""),
    ("De doce diputados a ciento siete.", 4, False, ""),
    ("Ni las criptomonedas suben así.", 4, False, ""),
    ("Y en julio de 1932: 37 %.", 4, True, ""),
    ("El partido de Hitler es el más votado de Alemania.", 4, False, ""),
    ("Y aquí es donde todo el mundo dice: «Ah, entonces ganó».", 4, False, ""),
    ("Pues no.", 4, True, ""),
    ("Fue el más votado, sí. Pero 37 % no es mayoría: seis de cada diez alemanes votaron por otro.", 4, False, ""),
    ("Ojo: casi catorce millones lo votaron sabiendo lo que decía.", 4, False, ""),
    ("Eso pesa.", 4, False, ""),
    ("Pero el que nombraba al jefe de gobierno era el presidente.", 4, False, ""),
    ("Hitler necesitaba convencer a un solo hombre...", 4, False, ""),
    ("y ese hombre no lo soportaba.", 4, False, ""),
    # ---------------- 5 · El cartero
    ("Paul von Híndenburg.", 5, True, ""),
    ("Ochenta y cuatro años, héroe de guerra, presidente de Alemania y dueño del bigote más serio de Europa.", 5, False, ""),
    ("Híndenburg mira a Hitler como quien mira a un mesero maleducado.", 5, False, ""),
    ("Ni siquiera lo llamaba por su nombre: le decía «el cabo bohemio»...", 5, False, ""),
    ("y Hitler ni siquiera era de Bohemia. Ni eso se sabía.", 5, False, ""),
    ("Ese mismo año, Hitler decide presentarse a presidente contra él.", 5, False, ""),
    ("Pero había un detallito...", 5, False, ""),
    ("Hitler seguía sin ser alemán.", 5, False, ""),
    ("Había renunciado a ser austríaco y llevaba siete años sin nacionalidad.", 5, False, ""),
    ("El señor de «Alemania para los alemanes»...", 5, False, ""),
    ("no tenía pasaporte alemán.", 5, True, ""),
    ("¿La solución? Un estado donde los nazis estaban en el gobierno lo nombra funcionario público, y con el puesto le dan la ciudadanía.", 5, False, ""),
    ("Imagínate a Hitler de burócrata, con sello y escritorio.", 5, False, ""),
    ("Y Híndenburg lo aplasta.", 5, False, ""),
    ("Unos meses después, Hitler va a verlo y le exige que lo nombre jefe de gobierno.", 5, False, ""),
    ("Híndenburg lo escucha un rato...", 5, False, ""),
    ("y le dice que no.", 5, True, ""),
    ("Y cuentan que después, con los suyos, soltó:", 5, False, ""),
    ("¿Ese tipo, canciller? Como mucho lo hago director de Correos. Para que lama los sellos con mi cara.", 5, False, "hindenburg"),
    ("Ese ya no llega a nada.", 5, False, M),
    ("Acuérdate de los sellos. Van a volver.", 5, False, ""),
    # ---------------- 6 · Acabado
    ("Y entonces pasa algo que casi nadie cuenta: Hitler empieza a caer.", 6, False, ""),
    ("En noviembre de 1932, su partido pierde dos millones de votos.", 6, False, ""),
    ("Y por dentro está peor: el partido está quebrado.", 6, False, ""),
    ("Deudas por todos lados y gente que se va.", 6, False, ""),
    ("¿Y Hitler?", 6, False, ""),
    ("Otra vez con lo del tiro.", 6, False, ""),
    ("Según el diario de su jefe de propaganda, dijo:", 6, False, ""),
    ("Si el partido se rompe, me pego un tiro en tres minutos.", 6, False, "diario"),
    ("Afuera ya lo están despidiendo.", 6, False, ""),
    ("Un profesor británico escribe que", 6, False, ""),
    ("Hitler seguramente va a terminar como un viejito en una cervecería de Baviera, contándoles a sus amigos lo cerca que estuvo de tomar Alemania.", 6, False, "profesor"),
    ("Ese ya no llega a nada.", 6, False, M),
    ("Y justo ahí, cuando ya estaba en el suelo...", 6, False, ""),
    ("aparece un hombre con una idea brillante.", 6, False, ""),
    # ---------------- 7 · Los genios
    ("Franz von Pápen.", 7, True, ""),
    ("Aristócrata, elegantísimo, exoficial de caballería...", 7, False, ""),
    ("y uno de los políticos menos tomados en serio de Alemania.", 7, False, ""),
    ("Para que te hagas una idea: había sido jefe de gobierno unos meses, y en una votación del Parlamento perdió quinientos doce a cuarenta y dos.", 7, False, ""),
    ("Quinientos doce a cuarenta y dos.", 7, True, ""),
    ("¿Y quién lo había puesto en el cargo?", 7, False, ""),
    ("Un general muy astuto, su amigo...", 7, False, ""),
    ("que cuando alguien le dijo que Pápen no era ninguna cabeza, contestó:", 7, False, ""),
    ("No tiene que ser una cabeza. Es un sombrero.", 7, False, "general"),
    ("Pero el general del sombrero se cansa, y en diciembre le quita el puesto y se queda él.", 7, False, ""),
    ("Y Pápen no lo perdona.", 7, False, ""),
    ("Y para vengarse, se le ocurre la idea del siglo:", 7, False, ""),
    ("usar a Hitler.", 7, True, ""),
    ("Se reúne a escondidas con él en la casa de un banquero, convence al hijo del presidente...", 7, False, ""),
    ("y entre todos van a ver al viejo Híndenburg:", 7, False, ""),
    ("Tranquilo. Lo nombramos, pero lo rodeamos de los nuestros.", 7, False, "papen2"),
    ("¿Cuántos nazis habría en el gobierno?", 7, False, ""),
    ("Solo tres de once ministros.", 7, False, ""),
    ("El plan era perfecto: Hitler pone los votos...", 7, False, ""),
    ("y ellos llevan las riendas.", 7, False, ""),
    ("Y Híndenburg, el del «como mucho, cartero»...", 7, False, ""),
    ("firma.", 7, True, ""),
    ("30 de enero de 1933.", 7, True, ""),
    ("Hitler es nombrado canciller de Alemania.", 7, False, ""),
    ("Sin mayoría. Sin ganar. Por un acuerdo entre unos pocos señores en un despacho.", 7, False, ""),
    ("Y Pápen, feliz de la vida, le dice a su amigo preocupado:", 7, False, ""),
    ("Relájate. Lo hemos contratado. En dos meses lo tenemos tan arrinconado que va a chillar.", 7, False, "papen"),
    ("Y cuentan que al día siguiente, otro de los socios del acuerdo murmuró:", 7, False, ""),
    ("Ayer cometí la mayor estupidez de mi vida.", 7, False, "socio"),
    # ---------------- 8 · Los dos meses
    ("Dos meses. Ese era el plazo de Pápen. Vamos a ver cómo le fue.", 8, False, ""),
    ("A las cuatro semanas, se incendia el Parlamento.", 8, False, ""),
    ("Adentro arrestan a un joven comunista holandés.", 8, False, ""),
    ("Al día siguiente, Hitler consigue un decreto que suspende la libertad de prensa, de reunión y de expresión.", 8, False, ""),
    ("Miles de opositores terminan presos.", 8, False, ""),
    ("A las cinco semanas, nuevas elecciones, con la oposición perseguida y las calles llenas de matones.", 8, False, ""),
    ("Y ahora sí, ¿sacó la mayoría?", 8, False, ""),
    ("Tampoco. 43,9 %.", 8, True, ""),
    ("Ni con miedo le alcanzó.", 8, False, ""),
    ("22 de marzo. Y aquí ya no hay nada de chiste: abre Dájau, el primer campo de concentración.", 8, False, ""),
    ("Los primeros presos son opositores políticos.", 8, False, ""),
    ("Al día siguiente, el Parlamento vota una ley que le permite a Hitler hacer leyes...", 8, False, ""),
    ("sin el Parlamento.", 8, True, ""),
    ("O sea, el Parlamento vota su propia desaparición.", 8, False, ""),
    ("Solo los socialdemócratas votan en contra, y su líder dice una frase que todavía pone la piel de gallina:", 8, False, ""),
    ("Pueden quitarnos la libertad y la vida. Pero no el honor.", 8, False, "wels"),
    ("¿Y los conservadores de Pápen, los que lo iban a controlar?", 8, False, ""),
    ("Votan a favor.", 8, True, ""),
    ("Ahora haz la cuenta. Del 30 de enero al 23 de marzo.", 8, False, ""),
    ("Cincuenta y dos días.", 8, True, ""),
    ("Pápen dijo que en dos meses alguien iba a terminar chillando en un rincón.", 8, False, ""),
    ("Y tenía razón.", 8, False, ""),
    ("Solo se equivocó de persona: en el rincón terminó el Parlamento entero.", 8, False, ""),
    ("Y en julio, todos los partidos menos uno quedan prohibidos.", 8, False, ""),
    ("El partido que nunca ganó una mayoría...", 8, False, ""),
    ("ahora era el único.", 8, False, ""),
    ("Pero los genios todavía no habían pagado la cuenta.", 8, False, ""),
    ("Y uno de ellos la pagó con su vida.", 8, False, ""),
    # ---------------- 9 · La cuenta
    ("Un año después, Hitler manda a matar a sus rivales en una sola noche: la Noche de los Cuchillos Largos.", 9, False, ""),
    ("Al general del sombrero lo matan en su casa, junto a su esposa.", 9, False, ""),
    ("Al secretario y al escritor de discursos de Pápen, también.", 9, False, ""),
    ("¿Y Pápen?", 9, False, ""),
    ("Lo encierran en su casa. Se salva de milagro.", 9, False, ""),
    ("En agosto muere Híndenburg, y Hitler se queda con todo:", 9, False, ""),
    ("el gobierno, el país...", 9, False, ""),
    ("y un ejército que le jura lealtad a él, personalmente.", 9, False, ""),
    ("¿Y te acuerdas de los sellos?", 9, False, ""),
    ("En 1941, Alemania deja de usar los sellos con la cara de Híndenburg...", 9, False, ""),
    ("y los cambia por sellos con la cara de Hitler.", 9, True, ""),
    ("El que iba a ser cartero terminó en todas las cartas de Alemania.", 9, False, ""),
    ("Y Pápen, el genio del plan...", 9, False, ""),
    ("sobrevive a todo.", 9, False, ""),
    ("A la guerra, a Hitler...", 9, False, ""),
    ("y en los juicios de Núremberg lo absuelven.", 9, False, ""),
    ("Después escribe unas memorias explicando que, en realidad, él no tuvo la culpa de nada.", 9, False, ""),
    ("El hombre que «no llegaba a nada» terminó desatando la guerra más sangrienta de la historia.", 9, False, ""),
    ("Decenas de millones de muertos.", 9, False, ""),
    ("Entonces, ¿Hitler llegó al poder ganando las elecciones?", 9, False, ""),
    ("Veredicto: medio mito.", 9, True, ""),
    ("Lo votaron millones, y eso pesa. Pero nunca la mayoría.", 9, False, ""),
    ("El poder no se lo dieron las urnas: se lo regalaron unos señores muy elegantes que se creían más listos que él.", 9, False, ""),
    ("Lo habían contratado.", 9, False, ""),
    ("Y el contratado...", 9, False, ""),
    ("se quedó con la empresa.", 9, True, ""),
]

CAPITULOS = ["Apertura", "El espía", "El golpe de la cervecería", "La fiera domada", "La crisis", "El cartero", "Acabado", "Los genios", "Los dos meses", "La cuenta"]


def buscar(texto, desde=0):
    for i in range(desde, len(GUION)):
        if GUION[i][0].startswith(texto):
            return i
    raise KeyError(texto)


# momentos serios: unas 150 palabras por minuto y la voz sin sonrisa
SERIAS = {buscar("Disparos."), buscar("Mueren dieciséis"), buscar("Ojo: casi catorce"), buscar("Eso pesa."),
          buscar("Según el diario"), buscar("Si el partido se rompe"), buscar("22 de marzo"), buscar("Los primeros presos"),
          buscar("Pueden quitarnos"), buscar("Un año después, Hitler manda"), buscar("Al general del sombrero lo matan"),
          buscar("Al secretario y al escritor"), buscar("El hombre que «no llegaba"), buscar("Decenas de millones")}

# pausas (s) DESPUÉS de cada frase. Por defecto, una transición natural corta; 0,3 antes de cada remate;
# las cuatro largas que pide el guion; y ninguna otra de más de medio segundo.
PAUSA_NORMAL = 0.18
PAUSA_REMATE = 0.3
PAUSA_CAPITULO = 0.45
REMATES = [
    "¿Y sabes a quién", "Al poder lo subieron", "Hitler tiene 30 años", "¿Cuántos eran?", "O sea: lo mandan", "Suena a partido",
    "En dos años, el partido", "¿Y Hitler?", "Se disloca", "Y el juez es", "Hitler convierte el juicio", "¿Cuántos cumple?",
    "El editor lo leyó", "¿Lo deportaron?", "O sea: da un golpe", "¿Cuánto le duró", "Y para colmo, en las elecciones",
    "Y probablemente", "En 1929, Nueva York", "Y cuando la gente", "Y aquí es donde", "Hitler necesitaba convencer",
    "Ni siquiera lo llamaba", "Pero había un detallito", "El señor de «Alemania", "Híndenburg lo escucha", "Y justo ahí",
    "Aristócrata, elegantísimo", "Y para vengarse", "¿Cuántos nazis", "El plan era perfecto", "Y Híndenburg, el del",
    "Y ahora sí, ¿sacó", "Al día siguiente, el Parlamento vota", "¿Y los conservadores", "El partido que nunca",
    "En 1941", "Y Pápen, el genio", "Y el contratado",
]
PAUSAS = {}
_v = 0
for _t in REMATES:
    _i = buscar(_t, 0)
    if _t == "¿Y Hitler?":
        PAUSAS[_i] = PAUSA_REMATE
        _i = buscar(_t, _i + 1)
    PAUSAS[_i] = PAUSA_REMATE
PAUSAS[buscar("Y sí: dos meses después")] = 0.5      # medio segundo antes de «Pero no era Hitler»
PAUSAS[buscar("Disparos.")] = 0.5                     # medio segundo después de «Disparos»
PAUSAS[buscar("Ni con miedo le alcanzó")] = 1.0       # un segundo antes de la frase de Dachau
PAUSAS[buscar("Los primeros presos")] = 1.0           # y un segundo después
PAUSAS[buscar("El poder no se lo dieron")] = 0.7      # 0,7 s antes de la última frase
for _i in range(len(GUION) - 1):
    if GUION[_i][1] != GUION[_i + 1][1]:
        PAUSAS.setdefault(_i, PAUSA_CAPITULO)

# las citas: cuatro voces secundarias (Gemini), con un estilo distinto para cada personaje
VOCES_EXTRA = {
    "papen": ("Algieba", "Eres un aristócrata alemán de clase alta, satisfecho y relajado, que tranquiliza a un amigo con aire de superioridad, casi sonriendo."),
    "papen2": ("Algieba", "Eres un aristócrata alemán de clase alta, seguro de sí mismo y tranquilizador, convenciendo a un anciano presidente en voz baja."),
    "ministro": ("Algieba", "Eres un político conservador orgulloso de sí mismo, que anuncia algo con satisfacción y solemnidad."),
    "socio": ("Algieba", "Eres un político conservador que murmura con arrepentimiento, en voz baja, casi para sí mismo."),
    "hindenburg": ("Algenib", "Eres un anciano mariscal de ochenta y cuatro años: voz grave, lenta y profunda, con desprecio contenido."),
    "fundador": ("Fenrir", "Eres un hombre sencillo entusiasmado que acaba de descubrir a un orador, con acento coloquial y mucha emoción."),
    "general": ("Fenrir", "Eres un general astuto y socarrón que suelta un chiste seco con media sonrisa."),
    "profesor": ("Sadaltager", "Eres un profesor universitario británico que escribe con tono académico y un punto de sorna."),
    "diario": ("Sadaltager", "Lees una entrada de diario: voz plana, seca, sin emoción ni ironía, como un acta."),
    "wels": ("Sadaltager", "Eres un político socialdemócrata valiente ante un parlamento hostil: voz digna, pausada y firme, sin ninguna ironía."),
}
ESTILO_MULETILLA = (
    "Di esta frase como si imitaras a un señor aristócrata que desprecia a alguien: un poco más grave que tu voz normal, "
    "lenta, con desdén elegante y aburrido, arrastrando apenas 'nada'."
)

# cómo se ven algunas palabras en los subtítulos (claves normalizadas: minúsculas y sin tildes)
VISIBLE = {
    ("papen",): "Papen",
    ("hindenburg",): "Hindenburg",
    ("dajau",): "Dachau",
}
ENFASIS_PALABRAS = set()

INDICACIONES = (
    "Narra como un amigo que te cuenta un chisme histórico: irónico, cómplice, en tuteo y en presente, con mucha variación "
    "de tono y remates con picardía. Nunca suenes a documental solemne, salvo en las frases serias que se indican: ahí "
    "baja el ritmo y pierde la sonrisa. Voz natural y humana, fluida y expresiva; sin respiraciones audibles."
)
PRONUNCIACION = "Pronuncia 'Pápen', 'Híndenburg', 'Múnich', 'Baviera', 'Dájau' y 'Núremberg' tal como están escritos."
