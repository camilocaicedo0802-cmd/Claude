// Zooms por frase (multiplicador sobre el zoom base). Reglas de estilo.md §6:
// apertura cerrada que se aleja, salto de 250 ms en palabra clave, empuje lento y nunca un plano quieto más de 2 s.
import { SEGMENTS, T, seg } from "../timeline";

const S = (id: string) => seg(id);
const PUNCH = 0.25;

export const ZOOMS: Record<string, [number, number][]> = {
  // Gancho: abre cerrado (1,18) y se aleja en 900 ms; salto en «Personaje»; vuelve a abrir en el desenfoque.
  s01_hook: [
    [0, 1.18],
    [0.9, 1.0],
    [T("s01", 8) - 0.02, 1.02],
    [T("s01", 8) + PUNCH, 1.13],
    [T("s01", 9) - 0.04, 1.16],
    [T("s01", 9) + 0.12, 1.0],
    [S("s01").end, 1.08],
  ],
  s02_casting: [
    [S("s02").start, 1.0],
    [T("s02", 7), 1.04],
    [T("s02", 9) + PUNCH, 1.14],
    [T("s02", 12) - 0.05, 1.17],
    [T("s02", 12) + 0.3, 1.0],
    [S("s02").end, 1.06],
  ],
  s03_propuesta: [
    [S("s03").start, 1.12],
    [S("s03").cuts[0] - 0.01, 1.17],
    [S("s03").cuts[0], 1.0],
    [S("s03").end, 1.06],
  ],
  s04_escucho: [
    [S("s04").start, 1.0],
    [T("s04", 6), 1.05],
    [T("s04", 6) + PUNCH, 1.14],
    [T("s04", 7) - 0.03, 1.16],
    [T("s04", 7) + 0.3, 1.04],
    [S("s04").end, 1.1],
  ],
  s05_decisiones: [
    [S("s05").start, 1.0],
    [T("s05", 9) - 0.02, 1.05],
    [T("s05", 9) + PUNCH, 1.16],
    [S("s05").end, 1.24],
  ],
  s06_bits: [
    [S("s06").start, 1.14],
    [S("s06").cuts[0] - 0.01, 1.2],
    [S("s06").cuts[0], 1.0],
    [T("s06", 13) - 0.02, 1.03],
    [T("s06", 13) + PUNCH, 1.15],
    [S("s06").end, 1.2],
  ],
  s08_melodia: [
    [S("s08").start, 1.0],
    [T("s08", 12), 1.06],
    [T("s08", 12) + PUNCH, 1.15],
    [S("s08").end, 1.18],
  ],
  s09_accion: [
    [S("s09").start, 1.1],
    [T("s09", 6) - 0.02, 1.13],
    [T("s09", 6) + PUNCH, 1.0],
    [S("s09").end, 1.07],
  ],
  s10_conflicto: [
    [S("s10").start, 1.0],
    [T("s10", 10) - 0.02, 1.05],
    [T("s10", 10) + PUNCH, 1.17],
    [S("s10").end, 1.2],
  ],
  s11_streaming: [
    [S("s11").start, 1.08],
    [S("s11").cuts[0] - 0.01, 1.15],
    [S("s11").cuts[0], 1.0],
    [S("s11").end, 1.08],
  ],
  // CTA mirando a cámara: pantalla completa, abre cerrado como el gancho.
  s13_repitas: [
    [S("s13").start, 1.16],
    [S("s13").start + 0.8, 1.0],
    [T("s13", 11) - 0.02, 1.03],
    [T("s13", 11) + PUNCH, 1.12],
    [S("s13").end, 1.14],
  ],
  s14_comenta: [
    [S("s14").start, 1.0],
    [S("s14").cuts[0] - 0.01, 1.04],
    [S("s14").cuts[0], 1.12],
    [S("s14").cuts[1] - 0.01, 1.18],
    [S("s14").cuts[1], 1.0],
    [S("s14").start + S("s14").duration, 1.05],
    [S("s14").end, 1.14],
  ],
};
void SEGMENTS;
