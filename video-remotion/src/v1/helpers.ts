import {Easing, interpolate} from 'remotion';
import {WORDS} from './timeline';

/** Segundo (en la línea de tiempo) en que empieza la palabra i. */
export const ws = (i: number) => WORDS[i].s;
/** Segundo en que termina la palabra i. */
export const we = (i: number) => WORDS[i].e;

export const sec = (s: number, fps: number) => Math.round(s * fps);

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** 0→1 en `dur` fotogramas a partir de `start` con easeOut. */
export const inProgress = (frame: number, start: number, dur: number) =>
  interpolate(frame, [start, start + dur], [0, 1], {...clamp, easing: easeOut});

/** 1→0 en `dur` fotogramas terminando en `end`. */
export const outProgress = (frame: number, end: number, dur: number) =>
  interpolate(frame, [end - dur, end], [1, 0], {...clamp, easing: easeInOut});

/** Generador pseudoaleatorio determinista. */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 9301 + 49297) * 233280;
  return x - Math.floor(x);
};
