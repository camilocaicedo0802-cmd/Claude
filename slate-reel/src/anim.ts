import { Easing, interpolate } from "remotion";

export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/**
 * Valor por fotogramas clave: [[frame, valor], ...]. Si dos claves están en
 * fotogramas consecutivos el cambio es un salto (corte seco), como los
 * punch-ins del referente.
 */
export const keyframes = (
  frame: number,
  keys: ReadonlyArray<readonly [number, number]>,
  easing = easeInOut,
): number => {
  if (keys.length === 0) return 1;
  if (frame <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [f0, v0] = keys[i];
    const [f1, v1] = keys[i + 1];
    if (frame >= f0 && frame <= f1) {
      if (f1 - f0 <= 1) return frame < f1 ? v0 : v1;
      return interpolate(frame, [f0, f1], [v0, v1], { ...clamp, easing });
    }
  }
  return keys[keys.length - 1][1];
};

/** Entrada del referente: opacidad + desenfoque (+ desplazamiento opcional). */
export const blurIn = (frame: number, start: number, dur = 4, blurPx = 12) => ({
  opacity: interpolate(frame, [start, start + dur], [0, 1], clamp),
  filter: `blur(${interpolate(frame, [start, start + dur], [blurPx, 0], { ...clamp, easing: easeOut })}px)`,
});

/** Salida del referente: el grupo se funde y se desenfoca en 6 fotogramas. */
export const blurOut = (frame: number, end: number, dur = 6, blurPx = 8) => ({
  opacity: interpolate(frame, [end - dur, end], [1, 0], clamp),
  blur: interpolate(frame, [end - dur, end], [0, blurPx], clamp),
});
