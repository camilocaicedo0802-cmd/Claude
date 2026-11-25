import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { F } from "./estilo";

// Tipografía delicada (corrección de la clienta): Jost para textos y Sofia Sans Extra Condensed ligera
// para las palabras gigantes y titulares. Inter Tight queda solo como respaldo de símbolos (→).
for (const w of ["300", "400", "500", "600"] as const) {
  loadFont({ family: F.sans, url: staticFile(`fuentes/Jost-${w}.ttf`), weight: w });
}
for (const w of ["300", "400"] as const) {
  loadFont({ family: F.cond, url: staticFile(`fuentes/SofiaSansExtraCond-${w}.ttf`), weight: w });
}
loadFont({ family: "Inter Tight", url: staticFile("fuentes/InterTight-600.ttf"), weight: "600" });
