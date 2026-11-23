// Línea de tiempo del montaje. Todos los tiempos en segundos; se pasan a fotogramas en los componentes.
import edlJson from "./data/edl.json";
import carasJson from "./data/caras.json";

type EdlItem = {
  id: string;
  src: string;
  section: string;
  duration: number;
  cuts: number[];
  words: { text: string; start: number; end: number }[];
};
const edl = edlJson as unknown as EdlItem[];
const caras = carasJson as unknown as Record<string, { cx: number; cy: number; w: number; W: number; H: number; track?: [number, number, number][] }>;

// Inicio de cada frase. Están sobre la rejilla de 0,25 s de la música (120 BPM) para que los cortes caigan a tempo.
export const STARTS: Record<string, number> = {
  s01_hook: 0.0,
  s02_casting: 5.5,
  s03_propuesta: 14.0,
  s04_escucho: 17.75,
  s05_decisiones: 23.75,
  s06_bits: 28.5,
  s08_melodia: 39.75,
  s09_accion: 43.25,
  s10_conflicto: 47.5,
  s11_streaming: 51.0,
  s12_testimonio: 58.5,
  s13_repitas: 80.75,
  s14_comenta: 84.0,
};
export const BEAT_PARTITURA = { start: 37.25, end: 39.75 }; // frase del guion que no está grabada: va escrita
export const TOTAL_SECONDS = 92.0; // termina cuando Armando acaba de hablar (sin tarjeta final)
export const TAIL = 0.4; // cola de imagen exportada tras la última palabra

export type Segment = {
  id: string;
  file: string;
  start: number;
  duration: number; // duración de la voz
  end: number; // hasta dónde se ve la imagen (inicio de lo siguiente)
  cuts: number[]; // cortes internos (absolutos)
  words: { text: string; t: number; end: number }[];
  face: { x: number; y: number };
  track?: [number, number, number][]; // [t local, x, y] de la cara, suavizado
  srcW: number;
  srcH: number;
};

const order = edl.map((e) => e.id);
export const SEGMENTS: Segment[] = edl.map((e, i) => {
  const start = STARTS[e.id];
  const nextId = order[i + 1];
  let next = nextId ? STARTS[nextId] : TOTAL_SECONDS;
  if (e.id === "s06_bits") next = BEAT_PARTITURA.start;
  const face = caras[e.id] ?? { cx: 0.5, cy: 0.5, w: 0.3, W: 1080, H: 1920 };
  const testi = e.id === "s12_testimonio";
  return {
    id: e.id,
    file: `media/aroll/${e.id}.mp4`,
    start,
    duration: e.duration,
    end: Math.min(next, start + e.duration + TAIL),
    cuts: e.cuts.map((c) => start + c),
    words: e.words.map((w) => ({ text: w.text, t: start + w.start, end: start + w.end })),
    face: { x: face.cx, y: face.cy },
    track: face.track,
    srcW: testi ? 1080 : 3840,
    srcH: testi ? 1920 : 2160,
  };
});

export const seg = (id: string): Segment => {
  const s = SEGMENTS.find((x) => x.id.startsWith(id));
  if (!s) throw new Error(`Segmento no encontrado: ${id}`);
  return s;
};
/** Tiempo absoluto en que se pronuncia la palabra `i` del segmento. */
export const T = (id: string, i: number): number => {
  const s = seg(id);
  const w = s.words[i];
  if (!w) throw new Error(`Palabra ${i} no existe en ${id}`);
  return w.t;
};
/** Fin de la voz de un segmento. */
export const END = (id: string): number => seg(id).start + seg(id).duration;

// Cambios de bloque del guion (transiciones con efecto).
export const CUTS = {
  problema: 5.5, // barras + destello tras el gancho
  solucion: 28.5, // barras + destello
  testimonio: 58.5, // glitch + corte
  cta: 80.75, // barras + destello
};
