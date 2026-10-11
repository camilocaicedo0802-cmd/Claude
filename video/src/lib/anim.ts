import { Easing, interpolate, interpolateColors } from "remotion";

// Curvas suaves, sin rebotes (estilo.md §6).
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const easeIn = Easing.bezier(0.55, 0, 1, 0.45);

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Interpola `t` (segundos) entre [t0, t1] -> [a, b] con easing; fuera del rango se mantiene. */
export const kf = (t: number, [t0, t1]: [number, number], [a, b]: [number, number], easing = easeOut) =>
  interpolate(t, [t0, t1], [a, b], { ...clampOpts, easing });

/** Varias claves: times y values del mismo largo. */
export const kfs = (t: number, times: number[], values: number[], easing = easeInOut) =>
  interpolate(t, times, values, { ...clampOpts, easing });

export const kcolor = (t: number, [t0, t1]: [number, number], [a, b]: [string, string]) =>
  interpolateColors(Math.min(Math.max(t, t0), t1), [t0, t1], [a, b]);

/** Muelle amortiguado simple en segundos (0 -> 1), con ligero sobrepaso. */
export const springy = (t: number, start: number, dur = 0.45, overshoot = 0.08) => {
  if (t <= start) return 0;
  const x = Math.min((t - start) / dur, 1);
  const base = 1 - Math.pow(1 - x, 3);
  return base + Math.sin(x * Math.PI) * overshoot * (1 - x);
};
