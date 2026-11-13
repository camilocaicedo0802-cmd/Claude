import {useMemo} from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {clamp, easeOut} from './helpers';
import {useSpec} from './spec';
import {Spec, Word} from './types';
import {C, OUTFIT} from '../v1/theme';

type Block = {text: string; s: number; e: number};

const makeHidden = (spec: Spec) => (s: number) =>
  spec.noSubs.some(([a, b]) => s >= a && s < b) || spec.titles.some((t) => s >= t.start - 0.02 && s < t.end);

// Bloques de 1-4 palabras, se cortan en puntuación, pausas y títulos (estilo.md §2)
const makeBlocks = (spec: Spec): Block[] => {
  const covered = new Set(spec.titles.flatMap((t) => t.covers));
  const hidden = makeHidden(spec);
  const out: {words: Word[]}[] = [];
  let cur: Word[] = [];
  spec.words.forEach((w, i) => {
    if (covered.has(i) || hidden(w.s)) {
      if (cur.length) out.push({words: cur});
      cur = [];
      return;
    }
    const prev = cur[cur.length - 1];
    if (prev && (w.s - prev.e > 0.35 || cur.length >= 4 || w.seg !== prev.seg)) {
      out.push({words: cur});
      cur = [];
    }
    cur.push(w);
    if (/[,.?]$/.test(w.text)) {
      out.push({words: cur});
      cur = [];
    }
  });
  if (cur.length) out.push({words: cur});
  return out.map((b, i, arr) => {
    const s = b.words[0].s;
    const natural = b.words[b.words.length - 1].e + 0.3;
    const next = arr[i + 1]?.words[0].s ?? natural;
    return {text: b.words.map((w) => w.text).join(' '), s, e: Math.min(natural, next)};
  });
};

/** Subtítulos pequeños sincronizados palabra a palabra (aparece el bloque al empezar su primera palabra). */
export const Subtitles: React.FC = () => {
  const spec = useSpec();
  const BLOCKS = useMemo(() => makeBlocks(spec), [spec]);
  const hidden = useMemo(() => makeHidden(spec), [spec]);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const b = BLOCKS.find((x) => t >= x.s && t < x.e && !hidden(t));
  if (!b) return null;
  const p = interpolate(frame - b.s * fps, [0, 4], [0, 1], {...clamp, easing: easeOut});
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 1490, // corrección §10.2: debajo de la barbilla, nunca sobre la cara
          translate: '0 -50%',
          textAlign: 'center',
          fontFamily: OUTFIT,
          fontWeight: 600,
          fontSize: 38,
          letterSpacing: '-0.02em',
          color: C.subWhite,
          textShadow: '0 2px 8px rgba(0,0,0,0.45)',
          opacity: p,
          scale: String(interpolate(p, [0, 1], [0.92, 1])),
        }}
      >
        {b.text}
      </div>
    </AbsoluteFill>
  );
};
