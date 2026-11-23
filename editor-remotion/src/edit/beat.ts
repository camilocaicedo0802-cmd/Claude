// Frase del guion que NO está en el material grabado («Piénsalo como una partitura musical: conocer las notas
// no es suficiente»). Se resuelve escrita en pantalla, tecleada palabra a palabra sobre un b-roll de teclado.
import { BEAT_PARTITURA } from "../timeline";

const line = (start: number, step: number, text: string) => text.split(" ").map((w, i) => ({ t: start + i * step, text: w }));
export const BEAT_LINES = [
  line(BEAT_PARTITURA.start + 0.2, 0.19, "Piénsalo como una partitura:"),
  line(BEAT_PARTITURA.start + 1.2, 0.18, "conocer las notas no basta."),
];
