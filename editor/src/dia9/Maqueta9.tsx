import React from "react";
import { useCaras, zonasEn } from "../rutinas/Caras";
import { useT } from "../rutinas/util";
import { Elem, Lado } from "../dia6/Maqueta";

// Maqueta del día 9: columnas a los lados de la cabeza, como la del día 6 (src/dia6/Maqueta.tsx, que no se toca),
// pero con otro orden de búsqueda para no tapar la acción: 1) su lado junto a la cabeza, 2) el otro lado junto a la
// cabeza, 3) debajo de la cabeza en su lado, 4) debajo en el otro lado. La zona de la cabeza ya incluye 100 px de
// margen (estilo.md §10.13). Las columnas bajan hasta y = 1480 (mesa y banco; la interfaz de Reels empieza más abajo).

type Caja = { x0: number; y0: number; x1: number; y1: number };
type Pos = { left: number; top: number; s: number };
export const LIM9 = { arriba: 150, abajo: 1480 };
const HUECO = 18;
const BORDE = 24;

const maqueta = (zona: Caja, elems: Elem[]): (Pos | null)[] => {
  const libre = { izq: zona.x0 - BORDE, der: 1080 - BORDE - zona.x1 };
  const ocupado = { izq: LIM9.arriba, der: LIM9.arriba };
  const debajo = Math.max(LIM9.arriba, zona.y1 + 12);
  const mitad = 540 - BORDE;
  return elems.map((e) => {
    const b = e.escala ?? 1;
    const pref = e.lado ?? "izq";
    const otro: Lado = pref === "izq" ? "der" : "izq";
    const intentos: [Lado, boolean][] = [
      [pref, false],
      [otro, false],
      [pref, true],
      [otro, true],
    ];
    for (const [lado, abajo] of intentos) {
      const top = abajo ? Math.max(ocupado[lado], debajo) : ocupado[lado];
      // Junto a la cabeza solo mientras la columna está a su altura; por debajo de ella hay media pantalla
      const ancho = top >= debajo ? mitad : libre[lado];
      const s = Math.min(b, ancho / e.w);
      if (s < b * 0.8) continue;
      if (top + e.h * s > LIM9.abajo) continue;
      ocupado[lado] = top + e.h * s + HUECO;
      return { left: lado === "izq" ? BORDE : 1080 - BORDE - e.w * s, top, s };
    }
    return null;
  });
};

/** Coloca los elementos (en orden de prioridad) y los desliza a su nuevo sitio en cada corte de la toma. */
export const Columnas9: React.FC<{ desde: number; hasta: number; elementos: Elem[] }> = ({ desde, hasta, elementos }) => {
  const caras = useCaras();
  const { t } = useT();
  const { actual, previa, k } = zonasEn(caras, t, desde, hasta);
  const ahora = maqueta(actual, elementos);
  const antes = maqueta(previa, elementos);
  return (
    <>
      {elementos.map((e, i) => {
        const a = ahora[i];
        if (!a) return null;
        // Si cambia de lado, salta en el corte: deslizarse de una columna a otra cruzaría por delante de la cara
        const previo = antes[i];
        const b = previo && previo.left < 540 === a.left < 540 ? previo : a;
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
export const ajustar9 = (zona: Caja, fijos: Elem[], extras: Elem[]): Elem[] => {
  for (let quitar = 0; quitar <= extras.length; quitar++) {
    const lista = [...fijos, ...extras.slice(quitar)];
    const pos = maqueta(zona, lista);
    if (pos.slice(fijos.length).every(Boolean)) return lista;
  }
  return fijos;
};
