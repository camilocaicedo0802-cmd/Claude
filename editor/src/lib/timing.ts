import { spring } from "remotion";
import edit from "../data/edit.json";

export type Word = { text: string; start: number; end: number; db?: number };
export type Segment = { srcStart: number; srcEnd: number; outStart: number };

// Línea de tiempo YA editada (silencios cortados) generada por scripts/preparar.py
export const WORDS: Word[] = edit.words;
export const SEGMENTS: Segment[] = edit.segments;
export const DURATION: number = edit.duration;
// Aire final tras la última palabra, sobre el último plano (el audio crudo acaba a los 0,3 s)
export const HOLD = 0.7;

const norm = (s: string) =>
  s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9 |]/g, "")
    .trim();

/** Busca una frase en la transcripción y devuelve sus tiempos en el vídeo editado.
 *  Un token puede llevar alternativas con «|» (p. ej. "3|tres semanas"), porque Whisper alterna cifras y letras. */
export const at = (phrase: string, afterSec = 0) => {
  const tokens = norm(phrase).split(/\s+/);
  for (let i = 0; i <= WORDS.length - tokens.length; i++) {
    if (WORDS[i].start < afterSec) continue;
    if (tokens.every((t, k) => t.split("|").includes(norm(WORDS[i + k].text)))) {
      return { start: WORDS[i].start, end: WORDS[i + tokens.length - 1].end };
    }
  }
  throw new Error(`Frase no encontrada en la transcripción: "${phrase}"`);
};

/** Progreso 0→1 con muelle a partir de un segundo concreto del vídeo editado. */
export const pop = (frame: number, fps: number, atSec: number, damping = 14) => {
  const local = frame - Math.round(atSec * fps);
  if (local < 0) return 0;
  return spring({ frame: local, fps, config: { damping, stiffness: 170, mass: 0.6 } });
};
