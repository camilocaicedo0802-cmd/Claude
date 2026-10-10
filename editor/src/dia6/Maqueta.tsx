import React from "react";
import { useCaras, zonasEn } from "../rutinas/Caras";
import { useT } from "../rutinas/util";

// Maqueta del día 6. En este crudo ella está en el centro y la cabeza se mueve mucho dentro de cada toma, así que
// los recursos van en columnas pegadas a los bordes (lo más lejos posible del cuerpo), empiezan debajo del título
// (que se apoya encima de la cabeza) y llegan hasta y = 1480 (la cortina; la mesa y el banco empiezan más abajo).
// Si una columna es algo estrecha, el elemento se reduce (hasta un 80 %); si no cabe, prueba en el otro lado.
// Nunca se acercan a menos de 100 px de la cabeza (zonaCara ya incluye ese margen).

type Caja = { x0: number; y0: number; x1: number; y1: number };
export type Lado = "izq" | "der";
export type Elem = {
  w: number;
  h: number;
  escala?: number;
  lado?: Lado;
  render: (style: React.CSSProperties) => React.ReactNode;
};
type Pos = { left: number; top: number; s: number };

const ARRIBA = 240;
const ABAJO = 1480;
const HUECO = 18;
const BORDE = 24;

const maqueta = (zona: Caja, elems: Elem[]): (Pos | null)[] => {
  const y0 = Math.max(ARRIBA, zona.y0 + 12);
  const libre = { izq: zona.x0 - BORDE, der: 1080 - BORDE - zona.x1 };
  const ocupado = { izq: y0, der: y0 };
  return elems.map((e) => {
    const pref = e.lado ?? "izq";
    for (const lado of [pref, pref === "izq" ? "der" : "izq"] as Lado[]) {
      const b = e.escala ?? 1;
      const s = Math.min(b, libre[lado] / e.w);
      if (s < b * 0.8) continue;
      if (ocupado[lado] + e.h * s > ABAJO) continue;
      const top = ocupado[lado];
      ocupado[lado] = top + e.h * s + HUECO;
      return {
        left: lado === "izq" ? BORDE : 1080 - BORDE - e.w * s,
        top,
        s,
      };
    }
    return null;
  });
};

/** Coloca los elementos (en orden de prioridad) y los desliza a su nuevo sitio en cada corte de la toma. */
export const Columnas: React.FC<{
  desde: number;
  hasta: number;
  elementos: Elem[];
  /** Índices que se dibujan (el resto solo ocupa su sitio). Por defecto, todos. */
  dibujar?: (i: number) => boolean;
}> = ({ desde, hasta, elementos, dibujar = () => true }) => {
  const caras = useCaras();
  const { t } = useT();
  const { actual, previa, k } = zonasEn(caras, t, desde, hasta);
  const ahora = maqueta(actual, elementos);
  const antes = maqueta(previa, elementos);
  return (
    <>
      {elementos.map((e, i) => {
        const a = ahora[i];
        if (!a || !dibujar(i)) return null;
        const b = antes[i] ?? a;
        const s = b.s + (a.s - b.s) * k;
        return (
          <React.Fragment key={i}>
            {e.render({
              left: b.left + (a.left - b.left) * k,
              top: b.top + (a.top - b.top) * k,
              transform: s !== 1 ? `scale(${s})` : undefined,
              transformOrigin: "0 0",
            })}
          </React.Fragment>
        );
      })}
    </>
  );
};

/** Quita los extras más antiguos hasta que el más reciente cabe (nunca desaparece lo último que se ha dicho). */
export const ajustar = (zona: Caja, fijos: Elem[], extras: Elem[]): Elem[] => {
  for (let quitar = 0; quitar <= extras.length; quitar++) {
    const lista = [...fijos, ...extras.slice(quitar)];
    const pos = maqueta(zona, lista);
    if (pos.slice(fijos.length).every(Boolean)) return lista;
  }
  return fijos;
};
export { maqueta };
