import { Easing, interpolate } from "remotion";
import wordsJson from "./data/words.json";
import edlJson from "./data/edl.json";

export type Word = { i: number; text: string; start: number; end: number; src: number };
export const WORDS = wordsJson as Word[];
const byIndex = new Map(WORDS.map((w) => [w.i, w]));
export const word = (i: number): Word => {
  const w = byIndex.get(i);
  if (!w) throw new Error(`Palabra ${i} no existe en words.json`);
  return w;
};

export type Segment = {
  srcIn: number;
  srcOut: number;
  outIn: number;
  faceX: number;
  faceY: number;
  faceS: number;
};
export const EDL = edlJson as { fps: number; duration: number; segments: Segment[] };

/**
 * Convierte un tiempo del VIDEO BASE original (segundos) al timeline final según el EDL.
 * Si ese instante se eliminó en el montaje, devuelve el inicio del siguiente segmento conservado.
 * Anclar los tiempos al original evita que gráficos, b-rolls y SFX se descuadren al cambiar cortes.
 */
export const at = (src: number): number => {
  for (const s of EDL.segments) {
    if (src < s.srcIn) return s.outIn;
    if (src <= s.srcOut) return s.outIn + (src - s.srcIn);
  }
  return EDL.duration;
};

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/** Progreso 0..1 entre t0 y t0+dur (segundos) con easing. */
export const prog = (t: number, t0: number, dur: number, easing = easeOut) =>
  interpolate(t, [t0, t0 + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

/** Entrada/salida estándar: 1 dentro, 0 fuera, con rampas en segundos. */
export const inOut = (t: number, t0: number, t1: number, rin = 0.17, rout = 0.14) =>
  Math.min(prog(t, t0, rin), 1 - prog(t, t1 - rout, rout, Easing.in(Easing.quad)));

// Medición de texto sin caché (las fuentes se cargan de forma asíncrona y la caché guardaría medidas falsas).
let ctx: CanvasRenderingContext2D | null = null;
export const measure = (text: string, font: string, letterSpacingEm = 0): number => {
  if (!ctx) {
    const c = document.createElement("canvas");
    ctx = c.getContext("2d");
  }
  if (!ctx) return text.length * 30;
  ctx.font = font;
  const px = parseFloat(font.match(/(\d+(?:\.\d+)?)px/)?.[1] ?? "100");
  return ctx.measureText(text).width + letterSpacingEm * px * Math.max(0, text.length - 1);
};
