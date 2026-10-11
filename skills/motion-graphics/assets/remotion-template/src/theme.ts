// ─────────────────────────────────────────────────────────────────────────────
// TOKENS DE ESTILO: rellénalos con los valores medidos en estilo.md.
// Los de abajo son el ejemplo "editorial monocromo" (referencia de ejemplo);
// SUSTITÚYELOS por los de cada referencia nueva. Nada de aquí es obligatorio.
// ─────────────────────────────────────────────────────────────────────────────
export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION_S = 30; // duración total (locución + cierre)

export const C = {
  bgLight: "#E4E4E4", // fondo claro dominante (paleta §7)
  bgDark: "#131314", // fondo oscuro dominante
  ink: "#141414", // texto/objetos sobre claro
  inkOnDark: "#F0F0F0", // texto sobre oscuro
  accent: "#FFD400", // color de palabra destacada (si la referencia usa uno)
  keyFrom: "#B4B4B4", // color inicial del revelado gris→tinta
  endCard: "#B6B6B6",
} as const;

export const F = {
  primary: "Archivo", // palo seco principal
  secondary: "Parisienne", // segunda familia (caligráfica, serif…)
} as const;

/** Estilos de subtítulo reutilizables. Ajusta tamaños/pesos/animación a la referencia. */
export const CAPTION_LOOKS = {
  // dos niveles: guía pequeña + palabra clave grande (editorial)
  editorialLight: {
    guide: { font: F.secondary, weight: 400, size: 58, color: C.ink, tracking: "0em", uppercase: false },
    key: { font: F.primary, weight: 800, size: 126, color: C.ink, tracking: "-0.035em", uppercase: false },
    keyFrom: C.keyFrom,
    reveal: "rise" as const,
    aberration: 0.22,
  },
  editorialDark: {
    guide: { font: F.primary, weight: 800, size: 52, color: C.inkOnDark, tracking: "-0.02em", uppercase: false },
    key: { font: F.secondary, weight: 400, size: 150, color: C.inkOnDark, tracking: "0em", uppercase: false },
    keyFrom: C.inkOnDark,
    reveal: "wipe" as const,
    aberration: 0.35,
  },
} as const;
