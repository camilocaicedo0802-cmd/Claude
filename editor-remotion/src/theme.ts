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
  lime: "#DFFF4F",
  limeGlow: "rgba(223,255,79,0.55)",
  white: "#FFFFFF",
  grey: "#C4C3B8",
  red: "#C6001B",
  redDot: "#D4002A",
  wine: "#8A0015",
  wineDark: "#0A0204",
  green: "#5F8F1E",
  cream: "#F4E6C8",
  bg: "#060606",
};

export const FPS = 60;
export const W = 1080;
export const H = 1920;

// Zonas del lienzo en el formato «ventana horizontal» (propuesta del reel de Instagram).
export const WINDOW = { x: 28, y: 446, w: 1024, h: 640, r: 32 };
export const FULL = { x: 0, y: 0, w: W, h: H, r: 0 };
export const LOWER_CY = 1312; // centro de la zona de subtítulos/gráficos bajo la ventana
export const FULL_CY = 1150; // centro del bloque de subtítulos a pantalla completa (55–57 %)
