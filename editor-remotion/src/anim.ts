import { Easing, interpolate } from "remotion";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Progreso 0→1 entre `from` y `from + dur` (segundos), con curva de salida suave. */
export const ramp = (t: number, from: number, dur: number, easing: (n: number) => number = Easing.out(Easing.cubic)) =>
  interpolate(t, [from, from + dur], [0, 1], { ...clamp, easing });

export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

/** Interpolación por tramos sobre claves [tiempo, valor] con salida suave en cada tramo. */
export const keys = (t: number, ks: [number, number][], easing: (n: number) => number = Easing.out(Easing.cubic)) => {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 0; i < ks.length - 1; i++) {
    const [t0, v0] = ks[i];
    const [t1, v1] = ks[i + 1];
    if (t <= t1) {
      if (t1 === t0) return v1;
      return lerp(v0, v1, easing((t - t0) / (t1 - t0)));
    }
  }
  return ks[ks.length - 1][1];
};

/** Pseudoaleatorio determinista (para variar SFX de teclas, etc.). */
export const rnd = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
