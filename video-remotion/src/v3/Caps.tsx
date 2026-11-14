import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeOut} from '../engine/helpers';
import {Word} from '../engine/types';
import {OUTFIT} from '../v1/theme';
import {KEY, T} from './data';
import {WORDS} from './timeline';

// ------------------------------------------------------------------
// Subtítulo karaoke (propuesta C): la frase entera aparece en una píldora oscura;
// cada palabra pasa de gris a BLANCO LISO al pronunciarla y las palabras clave
// se encienden en MORADO LISO (sin texturas, estilo.md §10.7).
// ------------------------------------------------------------------

type Chunk = {idx: number[]; s: number; e: number};

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

const CHUNKS = makeChunks(WORDS);
const clean = (i: number) => WORDS[i].text.replace(/[,.]/g, '').toUpperCase();

export const Caps: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  if (t >= T.end) return null;
  const c = CHUNKS.find((x) => t >= x.s && t < x.e);
  if (!c) return null;
  const l = frame - c.s * 30;
  const p = interpolate(l, [0, 4], [0, 1], {...clamp, easing: easeOut});
  const gap = CHUNKS[CHUNKS.indexOf(c) + 1]?.s ?? 999;
  const out = gap - c.e > 0.05 ? interpolate(frame, [c.e * 30 - 3, c.e * 30], [1, 0], clamp) : 1;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1640, display: 'flex', justifyContent: 'center', translate: '0 -50%'}}>
        <div
          style={{
            maxWidth: 980,
            padding: '16px 32px 20px',
            borderRadius: 30,
            background: 'rgba(12,10,16,0.74)',
            border: '1.5px solid rgba(255,255,255,0.12)',
            boxShadow: '0 16px 40px rgba(0,0,0,0.45)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '0 16px',
            fontFamily: OUTFIT,
            fontWeight: 800,
            fontSize: 54,
            letterSpacing: '-0.01em',
            lineHeight: 1.12,
            opacity: p * out,
            scale: String(interpolate(p, [0, 1], [0.92, 1])),
            translate: `0 ${(1 - p) * 18}px`,
          }}
        >
          {c.idx.map((i) => {
            const on = interpolate(frame - WORDS[i].s * 30, [0, 3], [0, 1], clamp);
            const lift = interpolate(frame - WORDS[i].s * 30, [0, 2, 5], [0, -5, 0], clamp);
            const key = KEY.has(i);
            return (
              <span
                key={i}
                style={{
                  color: on > 0.5 ? (key ? '#C46BFF' : '#FFFFFF') : 'rgba(255,255,255,0.32)',
                  translate: `0 ${lift}px`,
                  display: 'inline-block',
                }}
              >
                {clean(i)}
              </span>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
