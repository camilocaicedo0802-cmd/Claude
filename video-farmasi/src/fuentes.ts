import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { F } from "./estilo";

// Sustitutas de las fuentes de la referencia (ver estilo.md §3.1):
// Helvetica Neue → Inter Tight · Druk/Tusker condensada → League Gothic al 75 % de ancho.
const pesos = ["400", "500", "600", "700", "800"] as const;
for (const w of pesos) {
  loadFont({ family: F.sans, url: staticFile(`fuentes/InterTight-${w}.ttf`), weight: w });
}
loadFont({ family: F.sans, url: staticFile("fuentes/InterTight-800i.ttf"), weight: "800", style: "italic" });
loadFont({ family: F.cond, url: staticFile("fuentes/LeagueGothic-Cond.ttf"), weight: "400" });
