import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeOut} from '../engine/helpers';
import {OUTFIT} from '../v1/theme';
import {T, TITLES} from './data';
import {Live} from './Live';
import {WORDS} from './timeline';

const F = 30;

// ------------------------------------------------------------------
// Subtítulo pequeño de la referencia (§2) para los tramos sin bloque grande:
// blanco liso, bloques cortos, cada palabra entra fantasma al decirla.
// ------------------------------------------------------------------
const covered = new Set(TITLES.flatMap((t) => t.covers));
type Block = {idx: number[]; s: number; e: number};
const BLOCKS: Block[] = (() => {
  const out: number[][] = [];
  let cur: number[] = [];
  WORDS.forEach((w, i) => {
    if (covered.has(i)) {
      if (cur.length) out.push(cur);
      cur = [];
      return;
    }
    const prev = cur.length ? WORDS[cur[cur.length - 1]] : null;
    if (prev && (w.s - prev.e > 0.3 || cur.length >= 4)) {
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
    const s = WORDS[idx[0]].s - 0.04;
    const natural = WORDS[idx[idx.length - 1]].e + 0.3;
    const next = out[k + 1] ? WORDS[out[k + 1][0]].s - 0.04 : natural;
    const nextTitle = Math.min(...TITLES.map((t) => t.start).filter((x) => x > s), 999);
    return {idx, s, e: Math.min(natural, next, nextTitle)};
  });
})();

export const SmallSubs: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t >= T.end) return null;
  const b = BLOCKS.find((x) => t >= x.s && t < x.e);
  if (!b) return null;
  const out = interpolate(frame, [b.e * F - 3, b.e * F], [1, 0], clamp);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 1650,
          translate: '0 -50%',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '0 12px',
          fontFamily: OUTFIT,
          fontWeight: 700,
          fontSize: 50,
          letterSpacing: '-0.02em',
          color: '#FFFFFF',
          textShadow: '0 4px 16px rgba(0,0,0,0.55)',
          opacity: out,
        }}
      >
        {b.idx.map((i, j) => {
          const l = frame - WORDS[i].s * F;
          const p = interpolate(l, [0, 4], [0, 1], {...clamp, easing: easeOut});
          const dir = j % 2 ? 1 : -1;
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                opacity: l < 0 ? 0 : p,
                scale: String(interpolate(p, [0, 1], [1.08, 1])),
                translate: `${dir * (1 - p) * 18}px ${(1 - p) * 10}px`,
                filter: p < 1 ? `blur(${10 * (1 - p)}px)` : undefined,
              }}
            >
              {WORDS[i].text.replace(/[.]/g, '')}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Persona recortada encima de los bloques que van «detrás de él» (solo a pantalla completa). */
export const PersonCut: React.FC = () => (
  <>
    {TITLES.filter((t) => t.scene).map((t) => (
      <Live key={t.id} from={t.start} to={t.end + 0.05} mask="c" />
    ))}
  </>
);
