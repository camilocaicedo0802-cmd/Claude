import { staticFile } from "remotion";

// Paleta de marca (manual de marca de Beleza)
export const COLORS = {
  durazno: "#FAEDCD", // cercanía, piel, calidez y acentos emocionales
  marfil: "#F5F0EC", // fondo principal, limpieza y descanso visual
  salvia: "#6D8B74", // bienestar, naturalidad y contenido educativo
  petroleo: "#45595A", // confianza, títulos, logo, CTA y piezas de autoridad
} as const;

// Tipografías: máximo dos familias por pieza.
// TAN Pearl no está disponible aún: se sustituye por Cormorant Garamond (sustitución segura del manual).
export const FONTS = {
  display: "'TAN Pearl', 'Cormorant Garamond', serif",
  body: "'Glacial Indifference', 'Montserrat', Arial, sans-serif",
} as const;

export const FONT_FACES = `
@font-face { font-family: 'Glacial Indifference'; font-weight: 400; src: url(${staticFile("fonts/glacial-indifference-400.woff2")}) format('woff2'); }
@font-face { font-family: 'Glacial Indifference'; font-weight: 700; src: url(${staticFile("fonts/glacial-indifference-700.woff2")}) format('woff2'); }
@font-face { font-family: 'Cormorant Garamond'; font-weight: 600; src: url(${staticFile("fonts/cormorant-garamond-latin-600-normal.woff2")}) format('woff2'); }
@font-face { font-family: 'Cormorant Garamond'; font-weight: 700; src: url(${staticFile("fonts/cormorant-garamond-latin-700-normal.woff2")}) format('woff2'); }
`;

export const VIDEO = { width: 1080, height: 1920, fps: 30 } as const;
