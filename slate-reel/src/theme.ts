import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Tipografías del referente (ver estilo.md §3–4).
// Grotesca: Inter Display (equivalente abierto de la del referente).
// Palabra destacada: Instrument Serif Italic.
export const SANS = "Inter Display";
export const SERIF = "Instrument Serif";

loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-Medium.otf"), weight: "500" });
loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-SemiBold.otf"), weight: "600" });
loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-Bold.otf"), weight: "700" });
loadFont({ family: SANS, url: staticFile("fonts/InterDisplay-Black.otf"), weight: "900" });
loadFont({
  family: SERIF,
  url: staticFile("fonts/InstrumentSerif-Italic.ttf"),
  style: "italic",
  weight: "400",
});

// Colores medidos en el referente.
export const C = {
  white: "#FFFFFF",
  yellow: "#FCF210",
  // Escala de la barra de valoración 1 → 10.
  scale: [
    "#54A949",
    "#54A949",
    "#BAD54F",
    "#BAD54F",
    "#F2E041",
    "#F2E041",
    "#F79A2D",
    "#F79A2D",
    "#ED7417",
    "#F73734",
  ],
  glowRed: "247, 55, 52",
  glowYellow: "242, 224, 65",
  glowGold: "252, 214, 120",
} as const;

// Posiciones en el lienzo 1080×1920.
export const LAYOUT = {
  subtitleCenterY: 1095, // 57 % de la altura
  blockTop: 960, // 50 %
  barCenterY: 1230, // 64 %
} as const;

export const TEXT_SHADOW = "0 2px 10px rgba(0,0,0,0.28)";
