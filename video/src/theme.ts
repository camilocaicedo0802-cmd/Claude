// Valores de estilo.md (convertidos a 1080×1920).
export const C = {
  paper: "#E4E4E4", // fondo papel
  ink: "#141414", // texto y objetos negros
  night: "#131314", // escenas oscuras
  snow: "#F0F0F0", // texto sobre oscuro
  endCard: "#B6B6B6", // tarjeta de cierre
  keyFrom: "#B4B4B4", // gris inicial de la palabra destacada
} as const;

export const F = {
  script: "Parisienne", // línea guía (sustituto de la caligráfica de la referencia)
  sans: "Archivo", // palabra destacada (sustituto de Helvetica Neue Heavy)
} as const;

export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION_S = 43.2;

// Geometría compartida entre escenas (para que las transiciones sean continuas, sin cortes visibles)
export const BAND = { y: 1120, h: 220 }; // franja negra E1 -> E2 (en pantalla)
export const PHONE_E2 = { cx: 540, cy: 1060, w: 500 }; // móvil al final de E2 = inicio de E3
