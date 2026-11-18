import { loadFont } from "@remotion/fonts";
import { useEffect, useState } from "react";
import { staticFile, useDelayRender } from "remotion";
import { FUENTE } from "./estilo";

// Tipografías (estilo.md §12). La referencia usa Helvetica Neue, que es de pago.
// Para usar la original, sustituye estos tres archivos por los de Helvetica Neue
// (Light, Bold, Bold Italic) manteniendo los nombres de familia.
const cargar = () =>
  Promise.all([
    loadFont({
      family: FUENTE.normal,
      url: staticFile("fonts/InterDisplay-Light.otf"),
      weight: "300",
    }),
    loadFont({
      family: FUENTE.fuerte,
      url: staticFile("fonts/texgyreheros-bold.otf"),
      weight: "700",
      style: "normal",
    }),
    loadFont({
      family: FUENTE.fuerte,
      url: staticFile("fonts/texgyreheros-bolditalic.otf"),
      weight: "700",
      style: "italic",
    }),
  ]);

let promesa: Promise<unknown> | null = null;

/** Retiene el render hasta que las fuentes están cargadas. */
export const useFuentes = (): boolean => {
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [listas, setListas] = useState(false);
  const [handle] = useState(() => delayRender("Cargando tipografías"));

  useEffect(() => {
    promesa = promesa ?? cargar();
    promesa
      .then(() => {
        setListas(true);
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  }, [handle, continueRender, cancelRender]);

  return listas;
};
