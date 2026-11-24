import { Easing, interpolate } from "remotion";
import { FPS } from "./estilo";
import edicion from "./datos/edicion.json";

export const f = (s: number) => Math.round(s * FPS); // segundos de edición → fotograma
export const eOut = Easing.bezier(0.16, 1, 0.3, 1);
export const eInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export type Palabra = { text: string; startMs: number; endMs: number };
export const PALABRAS: Palabra[] = edicion.palabras;
export const DURACION_VOZ_S: number = edicion.duracionS;
export const inicio = (i: number) => PALABRAS[i].startMs / 1000; // s
export const fin = (i: number) => PALABRAS[i].endMs / 1000;

// Animación de entrada genérica (opacidad, desenfoque, desplazamiento, escala)
export const entrada = (frame: number, desde: number, dur = 8, dy = -12, escala0 = 1.06, blur0 = 8) => {
  const p = interpolate(frame, [desde, desde + dur], [0, 1], { ...clamp, easing: eOut });
  return {
    opacity: p,
    filter: blur0 ? `blur(${(1 - p) * blur0}px)` : undefined,
    translate: `0px ${(1 - p) * dy}px`,
    scale: String(escala0 + (1 - escala0) * p),
  } as const;
};

// Limpia puntuación para subtítulos (la referencia no usa comas ni puntos)
export const limpio = (t: string) => t.replace(/[.,;:¿?]/g, "");
