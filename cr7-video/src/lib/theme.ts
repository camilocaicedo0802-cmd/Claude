// Valores tomados de estilo.md (§3, §5, §8). Todo en píxeles de 1080x1920.
export const W = 1080;
export const H = 1920;
export const FPS = 30;

export const C = {
  blanco: "#FFFFFF",
  fondo: "#FCFCFC",
  negro: "#000000",
  grisEntrando: "#BDBDBD",
  gris: "#858585",
  boton: "#2E2E2E",
  dialogo: "#262626",
  tarjeta: "#C0C0C0",
  teal: "#3C9398",
  rojo: "#B5121B",
  rojoAcento: "#C8102E",
  reticula: "#C8C8C8",
  bokeh: "#DEDEDE",
  glow: "rgba(190,215,255,0.85)",
  glow2: "rgba(160,190,255,0.45)",
};

// Sombra larga abajo a la derecha (luz arriba-izquierda).
export const SOMBRA = "drop-shadow(40px 60px 50px rgba(0,0,0,0.38))";
export const SOMBRA_SUAVE = "drop-shadow(24px 36px 34px rgba(0,0,0,0.30))";

// Curva de entrada principal (ease-out fuerte).
export const EASE_OUT = [0.16, 1, 0.3, 1] as const;
