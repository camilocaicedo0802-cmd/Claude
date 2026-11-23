// Subtítulos de la opción B: son los mismos bloques (mismas palabras y tiempos) que el montaje vertical,
// recolocados en la zona INFERIOR, bajo la ventana. El testimonio conserva su posición (va a pantalla completa).
import { CapBlock } from "../components/Captions";
import { CAPTIONS, TESTI_CY, WIDE_CY } from "../edit/captions";
import { CHEST_CY, GFX_CY, LOW_CY } from "../theme";
import { KEY_CY, LABEL_CY, LOWER_CY } from "./layout";

export const BITS_WORD_CY = 1482; // «Transitarlos», bajo la línea de BITS
export const MELODIA_CY = 1422; // bajo el pentagrama
export const COMENTA_CY = 1196; // «Comenta», sobre la píldora
export const CLASE_ROWS_CY = 1162; // dos filas sobre la tarjeta de la masterclass

const MAP: [number, Partial<CapBlock>][] = [
  [CHEST_CY, { cy: LOWER_CY }],
  [LOW_CY, { cy: LOWER_CY }],
  [WIDE_CY, { cy: KEY_CY }], // fila de continuación tras la palabra gigante (la ventana está bajada)
  [GFX_CY - 205, { cy: LABEL_CY }],
  [GFX_CY - 200, { cy: LABEL_CY - 6 }],
  [GFX_CY + 168, { cy: BITS_WORD_CY, maxW: 800 }],
  [GFX_CY + 110, { cy: MELODIA_CY }],
  [GFX_CY - 128, { cy: COMENTA_CY }],
  [GFX_CY - 150, { cy: CLASE_ROWS_CY }],
  [TESTI_CY, {}],
];

export const CAPTIONS_H: CapBlock[] = CAPTIONS.map((b) => {
  const m = MAP.find(([cy]) => cy === b.cy);
  if (!m) throw new Error(`Bloque de subtítulos sin posición en el formato horizontal (cy=${b.cy})`);
  return { ...b, ...m[1] };
});
