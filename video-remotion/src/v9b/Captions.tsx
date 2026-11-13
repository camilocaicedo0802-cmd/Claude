import {useMemo} from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeOut} from '../engine/helpers';
import {Word} from '../engine/types';
import {C, OUTFIT} from '../v1/theme';
import {WORDS} from '../v9/timeline';
import {DISPLAY, KEY, NO_CAPS, capY} from './data';

type Chunk = {idx: number[]; s: number; e: number};

// Bloques de 1-3 palabras (máx. ~16 letras): se cortan en puntuación, pausas y cambios de toma.
const makeChunks = (words: Word[]): Chunk[] => {
  const out: number[][] = [];
  let cur: number[] = [];
  const len = (c: number[]) => c.reduce((n, i) => n + words[i].text.length + 1, 0);
  words.forEach((w, i) => {
    const prev = cur.length ? words[cur[cur.length - 1]] : null;
    if (prev && (w.s - prev.e > 0.3 || cur.length >= 3 || w.seg !== prev.seg || len(cur) + w.text.length > 17)) {
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
    const s = words[idx[0]].s;
    const natural = words[idx[idx.length - 1]].e + 0.25;
    const next = out[k + 1] ? words[out[k + 1][0]].s : natural;
    return {idx, s, e: Math.min(natural, next)};
  });
};

const clean = (i: number) => (DISPLAY[i] ?? WORDS[i].text.replace(/[,.]/g, '')).toUpperCase();

/** Subtítulo cinético: palabra a palabra, la palabra clave dentro de un recuadro morado. */
export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const chunks = useMemo(() => makeChunks(WORDS), []);
  const t = frame / 30;
  if (NO_CAPS.some(([a, b]) => t >= a && t < b)) return null;
  const c = chunks.find((x) => t >= x.s && t < x.e);
  if (!c) return null;
  const k = chunks.indexOf(c);
  const tilt = k % 2 ? 1.5 : -1.5;
  const out = interpolate(frame, [c.e * 30 - 2, c.e * 30], [1, 0], clamp);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 50,
          right: 50,
          top: capY(t),
          translate: '0 -50%',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '0 22px',
          rotate: `${tilt}deg`,
          opacity: out,
          fontFamily: OUTFIT,
          fontWeight: 900,
          letterSpacing: '-0.03em',
          lineHeight: 1.05,
        }}
      >
        {c.idx.map((i) => {
          const at = WORDS[i].s * 30;
          const p = interpolate(frame - at, [0, 5], [0, 1], {...clamp, easing: easeOut});
          const pop = interpolate(frame - at, [0, 3, 6], [0.5, 1.14, 1], clamp);
          const key = KEY.has(i);
          if (frame < at - 1) return <span key={i} style={{opacity: 0, fontSize: key ? 96 : 84}}>{clean(i)}</span>;
          return (
            <span
              key={i}
              style={{
                position: 'relative',
                fontSize: key ? 96 : 84,
                color: '#FFFFFF',
                padding: key ? '0 18px 6px' : 0,
                scale: String(pop),
                translate: `0 ${(1 - p) * 26}px`,
                opacity: interpolate(frame - at, [0, 2], [0, 1], clamp),
                textShadow: key ? `0 4px 0 ${C.purpleShadow}` : '0 5px 0 rgba(0,0,0,0.55), 0 0 22px rgba(0,0,0,0.55)',
                WebkitTextStroke: key ? undefined : '2px rgba(0,0,0,0.35)',
              }}
            >
              {key ? (
                <span
                  style={{
                    position: 'absolute',
                    inset: '4px 0 0',
                    borderRadius: 16,
                    background: C.purpleGrad,
                    boxShadow: `0 6px 0 ${C.purpleShadow}, 0 0 30px ${C.purpleGlow}`,
                    scale: `${interpolate(frame - at, [0, 4], [0, 1], {...clamp, easing: easeOut})} 1`,
                    transformOrigin: '0 50%',
                    rotate: '-2deg',
                    zIndex: -1,
                  }}
                />
              ) : null}
              <span style={{position: 'relative'}}>{clean(i)}</span>
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
