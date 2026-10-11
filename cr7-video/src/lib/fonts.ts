import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Réplicas de las fuentes de la referencia (estilo.md §3.1).
export const SANS = "CR7Sans"; // FreeSans (clon de Helvetica)
export const SERIF = "CR7Serif"; // Tinos Bold Italic condensada al 70 %
export const SERIF_ANCHA = "CR7SerifAncha"; // Tinos Bold Italic sin condensar
export const MANO = "CR7Mano"; // Permanent Marker (rótulos a mano)

loadFont({
  family: SANS,
  url: staticFile("fonts/FreeSansBold.ttf"),
  weight: "700",
});
loadFont({
  family: SANS,
  url: staticFile("fonts/FreeSans.ttf"),
  weight: "400",
});
loadFont({
  family: SERIF,
  url: staticFile("fonts/TinosCondensed-BoldItalic.ttf"),
  weight: "700",
  style: "italic",
});
loadFont({
  family: SERIF_ANCHA,
  url: staticFile("fonts/Tinos-BoldItalic.ttf"),
  weight: "700",
  style: "italic",
});
loadFont({ family: MANO, url: staticFile("fonts/PermanentMarker.ttf") });
