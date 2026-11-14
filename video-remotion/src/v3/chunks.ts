import {Word} from '../engine/types';
import {WORDS} from './timeline';

export type Chunk = {idx: number[]; s: number; e: number};

// Bloques de hasta 5 palabras / 24 letras; se cortan en puntuación y pausas > 0,35 s.
const makeChunks = (words: Word[]): Chunk[] => {
  const out: number[][] = [];
  let cur: number[] = [];
  const len = (c: number[]) => c.reduce((n, i) => n + words[i].text.length + 1, 0);
  words.forEach((w, i) => {
    const prev = cur.length ? words[cur[cur.length - 1]] : null;
    if (prev && (w.s - prev.e > 0.35 || cur.length >= 5 || len(cur) + w.text.length > 24)) {
      out.push(cur);
      cur = [];
    }
    cur.push(i);
    if (/[,.?]$/.test(w.text)) {
      out.push(cur);
      cur = [];
    }
  });
  if (cur.length) out.push(cur);
  return out.map((idx, k) => {
    const s = words[idx[0]].s - 0.08;
    const natural = words[idx[idx.length - 1]].e + 0.35;
    const next = out[k + 1] ? words[out[k + 1][0]].s - 0.08 : natural;
    return {idx, s, e: Math.min(natural, next)};
  });
};

export const CHUNKS = makeChunks(WORDS);
