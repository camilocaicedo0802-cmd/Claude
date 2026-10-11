// Curvas de velocidad personalizadas (estilo.md §5: ease-out fuerte, sin lineales, rebote ≤3 %).
export const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
export const prog = (f: number, start: number, dur: number) => clamp01((f - start) / dur);

export type Ease = (t: number) => number;
export const E = {
  expoOut: ((t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t))) as Ease,
  expoIn: ((t) => (t <= 0 ? 0 : Math.pow(2, 10 * t - 10))) as Ease,
  expoInOut: ((t) =>
    t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2) as Ease,
  quintOut: ((t) => 1 - Math.pow(1 - t, 5)) as Ease,
  quartIn: ((t) => t * t * t * t) as Ease,
  cubicInOut: ((t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)) as Ease,
  // overshoot suave (~3 %)
  softBack: ((t) => {
    const s = 0.9;
    return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2);
  }) as Ease,
};

/** Interpolación de `from` a `to` entre `start` y `start+dur` con la curva dada. */
export const tw = (f: number, start: number, dur: number, from: number, to: number, ease: Ease = E.expoOut) =>
  from + (to - from) * ease(prog(f, start, dur));

/** Velocidad (unidades/frame) de una función animada; sirve para calcular el motion blur. */
export const vel = (fn: (f: number) => number, f: number) => fn(f + 0.5) - fn(f - 0.5);

/** Entrada/salida en un solo valor: 0 antes, 1 mientras está, 0 tras salir. */
export const life = (f: number, inStart: number, inDur: number, outStart: number, outDur: number, easeIn: Ease = E.expoOut, easeOut: Ease = E.expoIn) =>
  f < outStart ? easeIn(prog(f, inStart, inDur)) : 1 - easeOut(prog(f, outStart, outDur));

export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

/** Pseudo-aleatorio determinista. */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
