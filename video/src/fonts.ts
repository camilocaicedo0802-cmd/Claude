import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { F } from "./theme";

// Se cargan desde public/fonts para que el render espere a que estén listas.
export const fontsReady = Promise.all([
  loadFont({ family: F.sans, url: staticFile("fonts/archivo-latin-600-normal.woff2"), weight: "600" }),
  loadFont({ family: F.sans, url: staticFile("fonts/archivo-latin-800-normal.woff2"), weight: "800" }),
  loadFont({ family: F.sans, url: staticFile("fonts/archivo-latin-900-normal.woff2"), weight: "900" }),
  loadFont({ family: F.script, url: staticFile("fonts/parisienne-latin-400-normal.woff2"), weight: "400" }),
]);
