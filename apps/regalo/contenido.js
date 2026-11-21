/*
  ════════════════════════════════════════════════════════════════════
  TODO lo que se personaliza del regalo está en este archivo.
  Cambia los textos entre comillas, guarda y recarga la página.
  Las fotos van en la carpeta "fotos/" y los audios en "audio/".

  Para resaltar una palabra o frase en itálica, ponla entre asteriscos:
  "Momentos que *no se borran*". Funciona en títulos, carta, preguntas y vale.
  ════════════════════════════════════════════════════════════════════
*/
window.REGALO = {
  // ── Quién regala y quién recibe ───────────────────────────────────
  para: "Leidy",
  de: "Juan Caicedo",
  pareja: "Leidy y Juan",
  fechaInicio: "2026-03-21",       // el día que se hicieron novios: de aquí sale el contador de días

  // ── Pantalla de bienvenida ────────────────────────────────────────
  bienvenidaPara: "Mi yiya",       // nombre en la tarjeta del corazón (vacío = usa "para")
  bienvenidaDe: "Camilo",          // firma en la tarjeta del corazón (vacío = usa "de")
  dedicatoria: "Hice esto pensando en ti, detalle por detalle. Ojalá te guste tanto como *me gustas tú.*",
  toquesCorazon: 4,                // cuántos toques llenan el corazón

  // ── Portada ───────────────────────────────────────────────────────
  portada: { foto: "fotos/portada.jpg" },

  // ── Nuestra canción ───────────────────────────────────────────────
  cancion: {
    titulo: "",                            // opcional: nombre de la canción (el reproductor de Spotify ya lo muestra)
    artista: "",
    foto: "fotos/disco.jpg",               // la foto que gira en el disco
    archivo: "",                           // un audio propio en "audio/" (si se deja vacío, suena desde Spotify)
    spotify: "https://open.spotify.com/track/5Vn2XpqzUOozKNmBmAgysw",
    sonarAlAbrir: true                     // solo aplica al audio propio
  },

  // ── Galería ───────────────────────────────────────────────────────
  galeria: {
    titulo: "Momentos que *no se borran*",
    fotos: [
      { src: "fotos/galeria-1.jpg", alt: "Selfie de Leidy y Juan sonriendo" },
      { src: "fotos/galeria-2.jpg", alt: "Leidy y Juan frente al espejo" },
      { src: "fotos/galeria-3.jpg", alt: "Leidy y Juan de cerca, ella lanzando un beso" },
      { src: "fotos/galeria-4.jpg", alt: "Leidy y Juan en un cumpleaños" },
      { src: "fotos/galeria-5.jpg", alt: "Leidy y Juan en el grado de Juan" },
      { src: "fotos/galeria-6.jpg", alt: "Leidy y Juan en la celebración del grado" }
    ]
  },

  // ── Carta ─────────────────────────────────────────────────────────
  carta: {
    saludo: "Hola, mi amor.",
    parrafos: [
      "Quise regalarte algo que no se pudiera envolver. Algo que puedas abrir cuando quieras, donde estés, y que siempre te diga lo mismo: *que te elijo.*",
      "Cuando te conocí no sabía que ese día iba a dividir mi vida en un antes y un después. Hoy lo tengo clarísimo: lo mejor empezó contigo.",
      "Me gusta cómo te ríes cuando algo de verdad te da risa. Me gusta que me entiendas con solo mirarme. Me gusta el plan más simple del mundo si es a tu lado.",
      "También hemos pasado días difíciles, y de cada uno salimos más unidos. Gracias por quedarte, por tenerme paciencia y por creer en mí cuando a mí se me olvida hacerlo.",
      "No sé todo lo que viene, pero sí sé *con quién quiero vivirlo.*"
    ],
    despedida: "Con todo mi amor,"
  },

  // ── Línea del tiempo ──────────────────────────────────────────────
  recuerdos: {
    titulo: "Nuestra *línea del tiempo*",
    lugarInicio: "",                 // opcional, por ejemplo "Todo empezó en Medellín"
    momentos: [
      {
        fecha: "2023-08-17",
        titulo: "El día que nos *conocimos*",
        texto: "Ese día no sabía que estaba conociendo a una de las personas más importantes de mi vida. Hoy lo cuento como el principio de todo."
        // foto: "fotos/…jpg"   (opcional: una foto redonda junto al recuerdo)
      },
      {
        fecha: "2025-06-21",
        titulo: "Empezamos a *salir*",
        texto: "Casi dos años después de conocernos, por fin nos dimos la oportunidad. Desde esa primera salida supe que quería muchas más."
      },
      {
        fecha: "2026-03-21",
        titulo: "Nos hicimos *novios*",
        texto: "Desde ese día llevo la cuenta, y cada uno de esos días ha valido la pena."
      }
    ]
  },

  // ── Mensaje de voz ────────────────────────────────────────────────
  voz: { archivo: "" },            // graba un audio, ponlo en "audio/" y escribe aquí la ruta, por ejemplo "audio/mensaje.m4a"

  // ── Mapa de lugares ───────────────────────────────────────────────
  // Sin puntos, la sección no aparece. Cada punto lleva lat y lng
  // (en Google Maps: clic derecho sobre el lugar → el primer dato son las coordenadas).
  lugares: {
    titulo: "El mapa de *nuestra historia*",
    texto: "Cada punto es un lugar que nos hizo ser quienes somos. Tócalos y revívelos.",
    puntos: []
  },

  // ── Cierre ────────────────────────────────────────────────────────
  final: {
    foto: "fotos/final.jpg",
    frase: "Hecho con amor, solo para ti"
  },

  // ── Última sorpresa: preguntas y vale ─────────────────────────────
  // "correcta" es la posición de la respuesta buena empezando en 0.
  // Con correcta: "todas" cualquier respuesta vale.
  sorpresa: {
    intro: "Para descubrir mi última sorpresa tendrás que responder unas preguntas sobre nosotros.",
    preguntas: [
      {
        pregunta: "¿Cuántos *viajes* hemos hecho?",
        pista: "No puedes contarlos.",
        opciones: ["8 viajes", "6 viajes", "5 viajes"],
        correcta: 1
      },
      {
        pregunta: "¿Quién dijo *“te quiero”* primero?",
        opciones: ["Tú", "Yo", "Los dos al mismo tiempo"],
        correcta: "todas"            // pendiente: Juan confirma la respuesta
      },
      {
        pregunta: "¿Quién se *enamoró* primero?",
        opciones: ["Tú", "Yo", "Los dos desde el primer día"],
        correcta: "todas"            // pendiente: Juan confirma la respuesta
      }
    ],
    vale: "Vale por una escapada a una *cabaña en diciembre*, solo tú y yo."
  }
};
