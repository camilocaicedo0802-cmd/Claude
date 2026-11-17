import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// SF Pro Display (archivos del cliente). Solo se usan los archivos originales, salvo la
// cursiva regular de los subtítulos (la Regular inclinada 12°, como las cursivas de Apple).
// No se usan versiones "enderezadas" de las cursivas: deformaban las curvas (O, S, C, R).
// El peso Black recto se obtiene engrosando la Bold original (ver EMBOLDEN).
export const SF = "SF Pro Display Edit";

const faces: { file: string; weight: string; style: "normal" | "italic" }[] = [
  { file: "SFProDisplay-Regular.otf", weight: "400", style: "normal" },
  { file: "SFProDisplay-ItalicDerived.otf", weight: "400", style: "italic" },
  { file: "SFProDisplay-LightItalic.otf", weight: "300", style: "italic" },
  { file: "SFProDisplay-Medium.otf", weight: "500", style: "normal" },
  { file: "SFProDisplay-Bold.otf", weight: "700", style: "normal" },
  { file: "SFProDisplay-BlackItalic.otf", weight: "900", style: "italic" },
];

for (const f of faces) {
  loadFont({ family: SF, url: staticFile(`fonts/${f.file}`), weight: f.weight, style: f.style });
}

// Relación altura de mayúscula / em de SF Pro Display (1443 / 2048)
export const CAP = 1443 / 2048;
// Black recta = Bold original + contorno uniforme de 0,0552 em (diferencia medida entre el
// grosor del palo de la Black y el de la Bold: 415 - 302 unidades de 2048).
export const EMBOLDEN = 113 / 2048;
// Interletraje de la palabra grande, calibrado sobre "CLIENTES" de la referencia
// (920 px de ancho con altura de mayúscula de 145 px).
export const BIG_TRACK = 0.0217;
