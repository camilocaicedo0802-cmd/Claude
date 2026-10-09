import React, { createContext, useContext } from "react";

// Posición de la cara en la toma de apoyo (scripts/rutinas/montar.py, YuNet cada 3 fotogramas, coordenadas 1080×1920).
// Todos los gráficos se colocan con colocar(): nunca a menos de 100 px de la cara (estilo.md §10.13).
export type DatosCaras = { cada: number; caras: (number | null)[][] };
type Caja = { x0: number; y0: number; x1: number; y1: number };

const Ctx = createContext<DatosCaras>({ cada: 3, caras: [] });
export const CarasProvider: React.FC<{ datos: DatosCaras; children: React.ReactNode }> = ({ datos, children }) => <Ctx.Provider value={datos}>{children}</Ctx.Provider>;
export const useCaras = () => useContext(Ctx);

const MARGEN = 100;
const PELO = 0.45; // la caja de YuNet empieza en la frente: se amplía hacia arriba para cubrir el pelo
const POR_DEFECTO: Caja = { x0: 330, y0: 260, x1: 750, y1: 820 }; // si no hay ninguna detección cerca

/** Zona prohibida (cara + pelo + 100 px) entre dos instantes. Las muestras sin cara heredan la detección más cercana (±2 s). */
export const zonaCara = (datos: DatosCaras, t0: number, t1: number, fps = 30): Caja => {
  const { cada, caras } = datos;
  const i0 = Math.max(0, Math.floor((t0 * fps) / cada));
  const i1 = Math.min(caras.length - 1, Math.ceil((t1 * fps) / cada));
  const radio = Math.round((2 * fps) / cada);
  let z: Caja | null = null;
  for (let i = i0; i <= i1; i++) {
    let c = caras[i];
    for (let d = 1; (!c || c[1] === null) && d <= radio; d++) {
      const a = caras[i - d];
      const b = caras[i + d];
      c = a && a[1] !== null ? a : b && b[1] !== null ? b : c;
    }
    const caja =
      c && c[1] !== null
        ? { x0: (c[1] as number) - MARGEN, y0: (c[2] as number) - (c[4] as number) * PELO - MARGEN, x1: (c[1] as number) + (c[3] as number) + MARGEN, y1: (c[2] as number) + (c[4] as number) + MARGEN }
        : POR_DEFECTO;
    z = z ? { x0: Math.min(z.x0, caja.x0), y0: Math.min(z.y0, caja.y0), x1: Math.max(z.x1, caja.x1), y1: Math.max(z.y1, caja.y1) } : caja;
  }
  return z ?? POR_DEFECTO;
};

export type Lugar = "arriba" | "izq" | "der" | "abajo";
/** Coloca una caja de w×h donde no toque la cara, probando los lugares en el orden dado. */
export const colocar = (zona: Caja, w: number, h: number, orden: Lugar[] = ["izq", "der", "arriba", "abajo"]) => {
  for (const l of orden) {
    if (l === "arriba" && zona.y0 - 70 >= h) return { lugar: l, left: 540 - w / 2, top: zona.y0 - h };
    if (l === "izq" && zona.x0 - 20 >= w) return { lugar: l, left: Math.max(20, (zona.x0 - w) / 2), top: Math.min(Math.max(230, (zona.y0 + zona.y1) / 2 - h / 2), 1180 - h) };
    if (l === "der" && 1060 - zona.x1 >= w) return { lugar: l, left: Math.min(1060 - w, zona.x1 + (1060 - zona.x1 - w) / 2), top: Math.min(Math.max(230, (zona.y0 + zona.y1) / 2 - h / 2), 1180 - h) };
    if (l === "abajo" && 1600 - Math.max(zona.y1, 1150) >= h) return { lugar: l, left: 540 - w / 2, top: Math.max(zona.y1, 1150) };
  }
  return null;
};
