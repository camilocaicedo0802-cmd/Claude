import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// SF Pro Display (archivos del cliente). Los estilos que faltaban en el paquete
// (Black y Light rectas, Italic regular) se derivaron con scripts/shear_font.py.
export const SF = "SF Pro Display Edit";

const faces: { file: string; weight: string; style: "normal" | "italic" }[] = [
  { file: "SFProDisplay-Regular.otf", weight: "400", style: "normal" },
  { file: "SFProDisplay-ItalicDerived.otf", weight: "400", style: "italic" },
  { file: "SFProDisplay-LightUpright.otf", weight: "300", style: "normal" },
  { file: "SFProDisplay-LightItalic.otf", weight: "300", style: "italic" },
  { file: "SFProDisplay-Medium.otf", weight: "500", style: "normal" },
  { file: "SFProDisplay-Bold.otf", weight: "700", style: "normal" },
  { file: "SFProDisplay-BlackUpright.otf", weight: "900", style: "normal" },
  { file: "SFProDisplay-BlackItalic.otf", weight: "900", style: "italic" },
];

for (const f of faces) {
  loadFont({ family: SF, url: staticFile(`fonts/${f.file}`), weight: f.weight, style: f.style });
}

// Relación altura de mayúscula / em de SF Pro Display (1443 / 2048)
export const CAP = 1443 / 2048;
