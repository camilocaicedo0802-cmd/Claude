// Tokens de estilo medidos en la referencia (ver estilo.md §4.1). Lienzo 1080x1920 @ 60 fps.
export const C = {
  cian: "#1FADD9",
  cianClaro: "#28BCEE",
  cianGigArriba: "#68D8F8",
  cianGigAbajo: "#3D7BA6",
  cianMGArriba: "#65CEF8",
  cianMGAbajo: "#3AA0CD",
  pildora: "#0FB2EF",
  personas: "#1EB4EA",
  rojo: "#EC011A",
  rojo2: "#EB2C35",
  blanco: "#F3F4F9",
  navy1: "#0B3350",
  navy2: "#021725",
  navyCab: "#1D3E8A",
  verde: "#22C55E",
  fondoSupDer: "#8BCEFA",
  fondoInfIzq: "#83C3EB",
  fondoBlanco: "#F8F9FE",
  grisMG: "#2B2B2B",
} as const;

export const F = {
  sans: "Inter Tight",
  cond: "League Gothic Cond",
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
