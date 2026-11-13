import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Tipografía base del referente (subtítulos, etiquetas, números): Inter Display.
export const SANS = "Inter Display";
// Palabras importantes: tipografías del manual de marca SLATE.
export const BRAND_SERIF = "Black Mango"; // titulares / palabra destacada
export const BRAND_SCRIPT = "Jimmy Script"; // acento caligráfico ("glow", como "Feel Your glow up")
export const BRAND_SANS = "Tenor Sans"; // ubicación / cierre

loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-Medium.otf"), weight: "500" });
loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-SemiBold.otf"), weight: "600" });
loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-Bold.otf"), weight: "700" });
loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-Black.otf"), weight: "900" });
// Black Mango y Jimmy Script: extraídas del PDF del manual (subconjunto A–W, a–y, 0–9).
loadFont({ family: BRAND_SERIF, url: staticFile("brand/fonts/BlackMango-Regular.ttf"), weight: "400" });
loadFont({ family: BRAND_SCRIPT, url: staticFile("brand/fonts/JimmyScript-Light.ttf"), weight: "400" });
loadFont({ family: BRAND_SANS, url: staticFile("fonts/TenorSans-Regular.ttf"), weight: "400" });

// Paleta del manual de marca (muestreada del PDF).
export const BRAND = {
  sage: "#809368",
  sageLight: "#A3B988",
  brown: "#683A22",
  beige: "#E4C6A8",
  navy: "#132B39",
  white: "#FFFFFF",
} as const;

export const C = {
  white: BRAND.white,
  // Color de las palabras destacadas.
  highlight: BRAND.sageLight,
  accentWarm: BRAND.beige,
  // Escala de la barra 1 → 10: del beige al marrón de la marca (tonos de bronceado).
  scale: ["#E4C6A8", "#DBB898", "#D1A988", "#C49674", "#B68361", "#A6704F", "#966141", "#855235", "#76452B", "#683A22"],
  scaleText: ["#132B39", "#132B39", "#132B39", "#132B39", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
  glowSage: "163, 185, 136",
  glowBeige: "228, 198, 168",
  glowBrown: "104, 58, 34",
} as const;

// Posiciones en el lienzo 1080×1920.
export const LAYOUT = {
  subtitleCenterY: 1095, // 57 % de la altura
  blockTop: 960, // 50 %
  barCenterY: 1230, // 64 %
} as const;

export const TEXT_SHADOW = "0 2px 10px rgba(0,0,0,0.28)";
