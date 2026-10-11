import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { F } from "./theme";

// Coloca los .ttf/.woff2 en public/fonts (font_match.py --download "Familia:peso" --dest public/fonts).
// loadFont bloquea el render hasta que la fuente está lista (evita frames con la fuente de sistema).
// AJUSTA esta lista a las fuentes elegidas en estilo.md.
export const FONT_FILES: { family: string; file: string; weight: string }[] = [
  { family: F.primary, file: "fonts/Archivo-800.ttf", weight: "800" },
  { family: F.secondary, file: "fonts/Parisienne-400.ttf", weight: "400" },
];

export const fontsReady = Promise.all(FONT_FILES.map((f) => loadFont({ family: f.family, url: staticFile(f.file), weight: f.weight })));
