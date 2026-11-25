import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Fuentes del lote 2 (enviadas por la clienta; los archivos viven en public/fuentes/cliente/ y no se versionan).
// Helvetica Neue Medium para el texto de contexto y Helvetica Neue Heavy (lila) para la palabra clave (corrección de la clienta).
export const HN = "Helvetica Neue L2";
export const GP = "Georgia Pro L2";

loadFont({ family: HN, url: staticFile("fuentes/cliente/HelveticaNeue-Medium.otf"), weight: "500" });
loadFont({ family: HN, url: staticFile("fuentes/cliente/HelveticaNeue-Bold.otf"), weight: "700" });
loadFont({ family: HN, url: staticFile("fuentes/cliente/HelveticaNeue-Heavy.otf"), weight: "800" });
loadFont({ family: GP, url: staticFile("fuentes/cliente/GeorgiaPro-SemiBold.ttf"), weight: "600" });
loadFont({ family: GP, url: staticFile("fuentes/cliente/GeorgiaPro-Bold.ttf"), weight: "700" });
