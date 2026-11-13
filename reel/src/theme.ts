// Tokens visuales sacados de estilo.md (colores y tipografías del vídeo de referencia).
import { cancelRender, continueRender, delayRender, staticFile } from "remotion";

// Fuentes locales (public/fonts): Chrome headless no puede descargar Google Fonts a través del proxy.
// Outfit y Oswald son variables (un archivo cubre todos los pesos).
const loadLocalFont = (family: string, file: string, weight: string) => {
  if (typeof document === "undefined") return family;
  const handle = delayRender(`Cargando fuente ${family}`);
  const face = new FontFace(family, `url(${staticFile(file)}) format('woff2')`, { weight, style: "normal" });
  face
    .load()
    .then(() => {
      document.fonts.add(face);
      continueRender(handle);
    })
    .catch((err) => cancelRender(err));
  return family;
};

export const OUTFIT = loadLocalFont("Outfit", "fonts/Outfit-400.woff2", "100 900");
export const BEBAS = loadLocalFont("Bebas Neue", "fonts/BebasNeue-400.woff2", "400");
export const OSWALD = loadLocalFont("Oswald", "fonts/Oswald-500.woff2", "200 700");
// Lema del logotipo de Macizo ("Madera en el Diseño"): DIN condensada -> Barlow Condensed.
export const BARLOW = loadLocalFont("Barlow Condensed", "fonts/BarlowCondensed-400.woff2", "400");

export const W = 1080;
export const H = 1920;
export const FPS = 30;

export const C = {
  yellowTop: "#FFF34F",
  yellowMid: "#FCEB3F",
  yellowBottom: "#F6CD22",
  yellow: "#FCE500",
  orangeA: "#FF9500",
  orangeB: "#FFAB00",
  orangeC: "#FFB700",
  lime: "#C6EF17",
  limeTop: "#E4FF5A",
  red: "#FE4348",
  white: "#FFFFFF",
  ink: "#111111",
  graphBg: "#0F0F0A",
  graphBg2: "#1A180D",
  glass: "rgba(20,16,14,0.78)",
  glassBorder: "rgba(255,255,255,0.12)",
};

export const GRADIENT = {
  yellow: `linear-gradient(180deg, ${C.yellowTop} 0%, ${C.yellowMid} 45%, ${C.yellowBottom} 100%)`,
  lime: `linear-gradient(180deg, ${C.limeTop} 0%, ${C.lime} 100%)`,
  white: "linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 60%, #E9E4DA 100%)",
  orange: `linear-gradient(90deg, ${C.orangeA} 0%, ${C.orangeB} 55%, ${C.orangeC} 100%)`,
};

export const GLOW = {
  yellow: "drop-shadow(0 0 28px rgba(252,229,0,0.45))",
  lime: "drop-shadow(0 0 28px rgba(198,239,23,0.5))",
  white: "drop-shadow(0 0 22px rgba(255,255,255,0.28))",
};
