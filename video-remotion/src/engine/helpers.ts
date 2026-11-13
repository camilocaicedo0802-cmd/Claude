import {Easing, interpolate} from 'remotion';
import {Word} from './types';

export const sec = (s: number, fps: number) => Math.round(s * fps);
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const rand = (seed: number) => {
  const x = Math.sin(seed * 9301 + 49297) * 233280;
  return x - Math.floor(x);
};
export const inOut = (frame: number, s: number, e: number, fin = 6, fout = 5) =>
  interpolate(frame, [s, s + fin, e - fout, e], [0, 1, 1, 0], clamp);

/** Atajos para anclar todo a palabras: ws(i) = inicio, we(i) = fin (segundos). */
export const wordTimes = (words: Word[]) => ({
  ws: (i: number) => words[i].s,
  we: (i: number) => words[i].e,
  /** índice de la n-ésima aparición de un texto (sin tildes ni signos) */
  find: (text: string, nth = 0) => {
    const norm = (t: string) => t.toLowerCase().normalize('NFKD').replace(/[^a-zñ0-9]/g, '');
    const hits = words.map((w, i) => [norm(w.text), i] as const).filter(([t]) => t === norm(text));
    if (!hits[nth]) throw new Error(`Palabra no encontrada: ${text} #${nth}`);
    return hits[nth][1];
  },
});
