import metricas from "./datos/metricas.json";
type Clave = keyof typeof metricas;
// Ancho de un texto en px (avances de glifo de la fuente real; sin kerning)
export const ancho = (texto: string, fuente: Clave, size: number, tracking = 0) => {
  const m = metricas[fuente];
  let w = 0;
  for (const c of texto) w += ((m.adv as Record<string, number>)[c] ?? 0.5) + tracking;
  return w * size;
};
export const cap = (fuente: Clave) => metricas[fuente].cap;
// Tamaño de fuente para que el texto ocupe `anchoObjetivo` (con tope)
export const ajustar = (texto: string, fuente: Clave, anchoObjetivo: number, maximo: number, tracking = 0) =>
  Math.min(maximo, anchoObjetivo / ancho(texto, fuente, 1, tracking));
