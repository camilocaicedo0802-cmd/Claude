/*
  ════════════════════════════════════════════════════════════════════
  TODO lo que se personaliza del regalo está en este archivo.
  Cambia los textos entre comillas, guarda y recarga la página.
  Las fotos van en la carpeta "fotos/" y los audios en "audio/".
  ════════════════════════════════════════════════════════════════════
*/
window.REGALO = {
  // ── Quién regala y quién recibe ───────────────────────────────────
  para: "Mi amor",                 // nombre de tu pareja
  de: "Camilo",                    // tu nombre
  pareja: "Tú y yo",               // línea bajo el nombre en la portada, por ejemplo "Sofía y Camilo"
  fechaInicio: "2023-03-03",       // el día que empezaron: AAAA-MM-DD (de aquí sale el contador de días)

  // ── Pantalla de bienvenida ────────────────────────────────────────
  dedicatoria: "Hice esto pensando en ti, detalle por detalle. Ojalá te guste tanto como me gustas tú.",
  toquesCorazon: 4,                // cuántos toques llenan el corazón

  // ── Portada ───────────────────────────────────────────────────────
  portada: { foto: "fotos/portada.jpg" },

  // ── Nuestra canción ───────────────────────────────────────────────
  cancion: {
    titulo: "Melodía de ejemplo",
    artista: "Cámbiala por la canción de ustedes",
    foto: "fotos/galeria-1.jpg",           // la foto que gira en el disco
    archivo: "audio/cancion-demo.mp3",     // un audio propio (o déjalo en "" si solo usas Spotify)
    spotify: "",                           // enlace de la canción en Spotify: https://open.spotify.com/track/…
    sonarAlAbrir: true                     // empieza a sonar cuando se abre el corazón
  },

  // ── Galería ───────────────────────────────────────────────────────
  galeria: {
    titulo: "Momentos que no se borran",
    fotos: [
      { src: "fotos/galeria-1.jpg", alt: "Nosotros, foto 1" },
      { src: "fotos/galeria-2.jpg", alt: "Nosotros, foto 2" },
      { src: "fotos/galeria-3.jpg", alt: "Nosotros, foto 3" },
      { src: "fotos/galeria-4.jpg", alt: "Nosotros, foto 4" },
      { src: "fotos/galeria-5.jpg", alt: "Nosotros, foto 5" },
      { src: "fotos/galeria-6.jpg", alt: "Nosotros, foto 6" }
    ]
  },

  // ── Carta ─────────────────────────────────────────────────────────
  carta: {
    saludo: "Hola, mi amor.",
    parrafos: [
      "Quise regalarte algo que no se pudiera envolver. Algo que puedas abrir cuando quieras, donde estés, y que siempre te diga lo mismo: que te elijo.",
      "Cuando te conocí no sabía que ese día iba a dividir mi vida en un antes y un después. Hoy lo tengo clarísimo: lo mejor empezó contigo.",
      "Me gusta cómo te ríes cuando algo de verdad te da risa. Me gusta que me entiendas con solo mirarme. Me gusta el plan más simple del mundo si es a tu lado.",
      "También hemos pasado días difíciles, y de cada uno salimos más unidos. Gracias por quedarte, por tenerme paciencia y por creer en mí cuando a mí se me olvida hacerlo.",
      "No sé todo lo que viene, pero sí sé con quién quiero vivirlo."
    ],
    despedida: "Con todo mi amor,"
  },

  // ── Línea del tiempo ──────────────────────────────────────────────
  recuerdos: {
    titulo: "Nuestra línea del tiempo",
    lugarInicio: "Todo empezó en Bogotá",
    momentos: [
      {
        fecha: "2023-02-24",
        titulo: "Nuestra primera cita",
        texto: "Me temblaban las manos antes de verte. Pedimos un café que se enfrió porque no paramos de hablar. Esa tarde supe que quería una segunda cita.",
        foto: "fotos/galeria-2.jpg"
      },
      {
        fecha: "2023-12-12",
        titulo: "Nuestro primer viaje",
        texto: "Maleta mal hecha, lista de canciones eterna y cero plan. Nos perdimos dos veces y aun así fue perfecto. Contigo hasta perderse es buen plan.",
        foto: "fotos/galeria-4.jpg"
      },
      {
        fecha: "2025-01-12",
        titulo: "Un lugar que es nuestro",
        texto: "Puede ser una casa, una banca del parque o tu lado del sofá. Donde estés tú, ahí es mi hogar.",
        foto: "fotos/galeria-6.jpg"
      }
    ]
  },

  // ── Mensaje de voz ────────────────────────────────────────────────
  voz: { archivo: "audio/mensaje-demo.mp3" },   // graba un audio con tu celular y ponlo aquí

  // ── Mapa de lugares ───────────────────────────────────────────────
  // lat y lng: en Google Maps, clic derecho sobre el lugar → el primer dato que aparece son las coordenadas.
  lugares: {
    titulo: "El mapa de nuestra historia",
    texto: "Cada punto es un lugar que nos hizo ser quienes somos. Tócalos y revívelos.",
    puntos: [
      {
        nombre: "Donde nos conocimos",
        cuando: "Febrero de 2023",
        texto: "Llegué tarde, pedí disculpas y tú te reíste. Ahí empezó todo.",
        direccion: "Parque de la 93, Bogotá",
        lat: 4.6767, lng: -74.0483
      },
      {
        nombre: "El café de la primera cita",
        cuando: "Febrero de 2023",
        texto: "Dos cafés fríos y una conversación que no quería terminar.",
        direccion: "Usaquén, Bogotá",
        lat: 4.6946, lng: -74.0308
      },
      {
        nombre: "Villa de Leyva",
        cuando: "Diciembre de 2023",
        texto: "Nuestro primer viaje. La plaza de noche, el frío y tu mano en el bolsillo de mi chaqueta.",
        direccion: "Plaza Mayor, Villa de Leyva, Boyacá",
        lat: 5.6333, lng: -73.5255
      },
      {
        nombre: "Cartagena",
        cuando: "2024",
        texto: "El atardecer en la muralla y la promesa de volver cada año.",
        direccion: "Centro Histórico, Cartagena de Indias",
        lat: 10.4236, lng: -75.5510
      },
      {
        nombre: "París",
        cuando: "Pronto",
        texto: "El viaje que tenemos pendiente. Ya empecé a ahorrar.",
        direccion: "Torre Eiffel, París, Francia",
        lat: 48.8584, lng: 2.2945
      }
    ]
  },

  // ── Cierre ────────────────────────────────────────────────────────
  final: {
    foto: "fotos/final.jpg",
    frase: "Hecho con amor, solo para ti"
  },

  // ── Última sorpresa: preguntas y vale ─────────────────────────────
  // "correcta" es la posición de la respuesta buena empezando en 0.
  // Usa correcta: "todas" si cualquier respuesta vale.
  sorpresa: {
    intro: "Para descubrir mi última sorpresa tendrás que responder unas preguntas sobre nosotros.",
    preguntas: [
      {
        pregunta: "¿Dónde fue nuestra primera cita?",
        opciones: ["En un café", "En el cine", "En un parque"],
        correcta: 0
      },
      {
        pregunta: "¿Quién dijo “te amo” primero?",
        opciones: ["Tú", "Yo", "Los dos al tiempo"],
        correcta: 1
      },
      {
        pregunta: "¿Qué es lo que más me gusta de ti?",
        opciones: ["Tu risa", "Tu forma de mirarme", "Todo, obvio"],
        correcta: 2
      }
    ],
    vale: "Vale por una cena en el lugar que tú elijas. Tú decides, yo invito."
  }
};
