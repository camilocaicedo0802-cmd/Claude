import { CAMARA, ESCENAS, Mov } from "./plan";
import { eOut, f } from "./util";

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

// Desenfoque del plano hablando alrededor de las escenas a pantalla completa (§6 corte con desenfoque)
export const desenfoqueTH = (frame: number) => {
  let blur = 0;
  let extra = 0;
  for (const e of ESCENAS) {
    const a = f(e.desde);
    const b = f(e.hasta);
    if (frame >= a - 6 && frame < a) {
      const p = (frame - (a - 6)) / 6;
      blur = Math.max(blur, p * 20);
      extra = Math.max(extra, p * 0.08);
    }
    if (frame >= b && frame < b + 14) {
      const p = 1 - eOut((frame - b) / 14);
      blur = Math.max(blur, p * 20);
    }
  }
  return { blur, extra };
};
