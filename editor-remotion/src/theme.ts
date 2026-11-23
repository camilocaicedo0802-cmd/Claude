// Colores, tipografías y medidas sacados de estilo.md (vídeo de referencia).
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Fuentes en local (public/fonts) para que el render no dependa de la red.
const face = (family: string, file: string, weight: string, style: "normal" | "italic" = "normal") =>
  loadFont({ family, url: staticFile(`fonts/${file}`), weight, style, format: "truetype" });
face("Inter Tight", "InterTight-500.ttf", "500");
face("Inter Tight", "InterTight-600.ttf", "600");
face("Inter Tight", "InterTight-700.ttf", "700");
face("Sora", "Sora-300.ttf", "300");
face("Sora", "Sora-400.ttf", "400");
face("Instrument Serif", "InstrumentSerif-Italic.ttf", "400", "italic");

export const FONT = {
  grotesk: "Inter Tight", // subtítulos (sustituto libre de Helvetica Now Display)
  wide: "Sora", // tarjetas y fichas (sustituto libre de Clash Display Light)
  serif: "Instrument Serif", // píldora verde (sustituto libre de PP Editorial New Italic)
};

export const C = {
  accent: "#FFDE21", // amarillo del cliente (sustituye al lima de la referencia)
  accentGlow: "rgba(255,222,33,0.55)",
  white: "#FFFFFF",
  grey: "#C4C3B8",
  red: "#C6001B",
  redDot: "#D4002A",
  wine: "#8A0015",
  wineDark: "#0A0204",
  gold: "#B88A00", // vidrio ámbar para solución/CTA (antes verde)
  cream: "#F4E6C8",
  bg: "#060606",
};

export const FPS = 60;
export const W = 1080;
export const H = 1920;

// Todo el vídeo va en recorte vertical a pantalla completa (corrección del cliente).
export const CHEST_CY = 1185; // centro del bloque de subtítulos sobre el pecho
export const LOW_CY = 1390; // subtítulos cuando el plano tiene la cara en el centro (b-roll)
export const GFX_CY = 1300; // centro de tarjetas, fichas y gráficos
