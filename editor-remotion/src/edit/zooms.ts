// Zoom por frase. 1,00 = recorte vertical a toda la altura del plano (el encuadre del gancho).
// Menos de 1 abre el plano (la base se funde a negro por abajo) y deja sitio al texto detrás del sujeto.
// Reglas de estilo.md §6: apertura cerrada que se aleja, salto de ~250 ms en palabra clave, nunca más de 2 s quieto.
import { T, seg } from "../timeline";

const S = (id: string) => seg(id);
const P = 0.25; // salto de zoom
export const WIDE = 0.66; // plano abierto para el texto detrás del sujeto

export const ZOOMS: Record<string, [number, number][]> = {
  s01_hook: [
    [0, 1.2],
    [0.85, WIDE], // se aleja mientras entra «Años» detrás de la cabeza
    [T("s01", 6) - 0.05, 0.7],
    [T("s01", 6) + 0.16, 1.04], // «el mismo Personaje»: plano cerrado
    [T("s01", 9) - 0.08, 1.1],
    [T("s01", 9) + 0.1, 0.94], // desenfoque + obturador
    [S("s01").end, 1.0],
  ],
  s02_casting: [
    [S("s02").start, 0.96],
    [T("s02", 8) - 0.02, 0.98],
    [T("s02", 8) + P, 1.08],
    [T("s02", 12) - 0.05, 1.11],
    [T("s02", 12) + 0.3, 0.92], // abre para las fichas
    [S("s02").end, 0.97],
  ],
  s03_propuesta: [
    [S("s03").start, 1.04],
    [S("s03").cuts[0] - 0.01, 1.09],
    [S("s03").cuts[0], 0.93],
    [S("s03").end, 0.98],
  ],
  s04_escucho: [
    [S("s04").start, 0.94],
    [T("s04", 6) - 0.02, 0.97],
    [T("s04", 6) + P, 1.07],
    [T("s04", 7) - 0.05, 1.09],
    [T("s04", 7) + 0.3, 0.93], // abre para las tarjetas
    [S("s04").end, 0.99],
  ],
  s05_decisiones: [
    [S("s05").start, 1.0],
    [S("s05").start + 0.5, WIDE], // «El problema» detrás de la cabeza
    [T("s05", 7) - 0.05, 0.7],
    [T("s05", 7) + 0.16, 1.05], // «Decisiones»: plano cerrado
    [S("s05").end, 1.13],
  ],
  s06_bits: [
    [S("s06").start, 0.95],
    [S("s06").cuts[0] - 0.01, 1.0],
    [S("s06").cuts[0], 1.06],
    [S("s06").cuts[0] + 0.5, WIDE], // «la estructura de BITS» detrás de la cabeza
    [T("s06", 17) - 0.05, 0.7],
    [T("s06", 17) + 0.2, 0.95],
    [S("s06").end, 1.0],
  ],
  s08_melodia: [
    [S("s08").start, 0.93],
    [T("s08", 12) - 0.02, 0.97],
    [T("s08", 12) + P, 1.06],
    [S("s08").end, 1.09],
  ],
  s09_accion: [
    [S("s09").start, 0.92],
    [S("s09").end, 0.98],
  ],
  s10_conflicto: [
    [S("s10").start, 0.97],
    [T("s10", 2) + P, 1.05],
    [T("s10", 7) - 0.12, 1.07],
    [T("s10", 7) + 0.3, WIDE], // «Avance» detrás de la cabeza
    [S("s10").end, 0.7],
  ],
  s11_streaming: [
    [S("s11").start, 0.96],
    [S("s11").cuts[0] - 0.01, 1.02],
    [S("s11").cuts[0], 1.08],
    [S("s11").end, 1.12],
  ],
  s13_repitas: [
    [S("s13").start, 1.15],
    [S("s13").start + 0.5, WIDE], // «No te repitas» detrás de la cabeza
    [T("s13", 8) - 0.05, 0.7],
    [T("s13", 8) + 0.16, 1.04],
    [S("s13").end, 1.1],
  ],
  s14_comenta: [
    [S("s14").start, 0.94],
    [S("s14").cuts[0] - 0.01, 0.97],
    [S("s14").cuts[0], 1.04],
    [T("s14", 7) - 0.05, 1.06],
    [T("s14", 7) + 0.3, 0.92], // abre para la tarjeta de la masterclass
    [S("s14").cuts[1] - 0.01, 0.95],
    [S("s14").cuts[1], 1.04],
    [S("s14").end, 1.1],
  ],
};
