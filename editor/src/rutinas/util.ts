import { spring, useCurrentFrame, useVideoConfig } from "remotion";

export type Word = { text: string; start: number; end: number; db?: number };
export const HOLD = 0.7;
export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const norm = (s: string) =>
  s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9 |]/g, "")
    .trim();

/** Crea at() para una transcripción: busca una frase y devuelve sus tiempos (falla si no existe). */
export const crearAt = (words: Word[]) => (phrase: string, afterSec = 0) => {
  const tokens = norm(phrase).split(/\s+/);
  for (let i = 0; i <= words.length - tokens.length; i++) {
    if (words[i].start < afterSec) continue;
    if (tokens.every((t, k) => t.split("|").includes(norm(words[i + k].text)))) {
      return { start: words[i].start, end: words[i + tokens.length - 1].end };
    }
  }
  throw new Error(`Frase no encontrada en la voz en off: "${phrase}"`);
};

export const pop = (frame: number, fps: number, atSec: number, damping = 14) => {
  const local = frame - Math.round(atSec * fps);
  if (local < 0) return 0;
  return spring({ frame: local, fps, config: { damping, stiffness: 170, mass: 0.6 } });
};

export const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { frame, fps, t: frame / fps };
};
