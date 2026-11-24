import { CAMARA, Mov } from "./plan";
import { eOut } from "./util";

export const BASE = { s: 1.3, y: -288 };

// Valor de cámara en un instante (s): encadena movimientos; cada uno parte del valor real en su inicio.
const valorHasta = (t: number, n: number): { s: number; y: number } => {
  let cur = { s: 1, y: 0 };
  for (let i = 0; i < n; i++) {
    const m: Mov = CAMARA[i];
    if (t < m.t) break;
    const inicio = valorHasta(m.t, i);
    const p = m.d <= 0 ? 1 : Math.min(1, (t - m.t) / m.d);
    const e = m.lineal ? p : eOut(p);
    cur = { s: inicio.s + (m.s - inicio.s) * e, y: inicio.y + (m.y - inicio.y) * e };
  }
  return cur;
};
export const camara = (t: number) => valorHasta(t, CAMARA.length);

// v2 (UGC): cortes secos, sin desenfoque de corte. Se mantiene la función para poder reactivarlo.
export const desenfoqueTH = (_frame: number) => ({ blur: 0, extra: 0 });
