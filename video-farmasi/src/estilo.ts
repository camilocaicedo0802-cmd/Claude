// Tokens de estilo medidos en la referencia (ver estilo.md §4.1). Lienzo 1080x1920 @ 60 fps.
export const C = {
  // Acento lila (corrección de la clienta: sustituye al cian de la referencia)
  acento: "#B794F6", // destacados sobre vídeo
  acentoClaro: "#D2B8FF",
  gigArriba: "#E4D4FF", // degradado de la palabra gigante detrás de la cabeza
  gigAbajo: "#9D6FEA",
  mgArriba: "#B892F5", // titulares sobre fondo claro
  mgAbajo: "#7E4FDC",
  pildora: "#9B6BF2",
  rojo: "#EC011A",
  rojo2: "#EB2C35",
  blanco: "#F7F5FB",
  navy1: "#2E1C52", // tarjetas oscuras: morado profundo
  navy2: "#150B2A",
  verde: "#22C55E",
  fondoSupDer: "#DCCBFF", // fondo de los motion graphics: lavanda
  fondoInfIzq: "#CFBDF7",
  fondoBlanco: "#FBF8FF",
  grisMG: "#2B2B2B",
} as const;

export const F = {
  sans: "Jost",
  cond: "Sofia Sans Extra Condensed",
} as const;

// Tamaños (§3.2)
export const T = {
  subtitulo: 80,
  destacado: 84,
  contexto: 60,
  mgPequeno: 52,
  mgCursiva: 112,
} as const;

// Posiciones verticales de los bloques sobre la toma UGC (ajustadas a la cara de la toma)
export const Y = {
  subtitulo: 1290, // línea pequeña (altura del pecho, justo bajo la barbilla tras el reencuadre)
  contextoArriba: 330, // palabras de contexto cuando la gigante va detrás
  giganteDetras: 640, // centro de la palabra gigante detrás de la cabeza (tapa pelo y frente)
  giganteDelante: 1440, // centro de la palabra gigante tecleada delante (pecho)
} as const;

export const FPS = 60;
